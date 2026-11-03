import { EventEmitter } from 'node:events';
import { parseFeed, decodeBody } from './feedparser.js';
import { readJson, JsonWriter } from './jsonfile.js';

const HOUR = 3_600_000;
const MAX_BYTES = 5 * 1024 * 1024;
const REQUESTED_TTL = 7 * 24 * HOUR;

export function isFeedUrl(u) {
  try {
    const url = new URL(u);
    return (url.protocol === 'http:' || url.protocol === 'https:') && u.length <= 2048;
  } catch { return false; }
}

/**
 * Crawls RSS/Atom/JSON feeds on a fixed interval (hourly by default) and caches the
 * parsed items on disk. Uses conditional GET (ETag / Last-Modified) and records a
 * per-feed status that the dashboard shows as "data freshness".
 */
export class Crawler extends EventEmitter {
  constructor({
    cacheFile,
    getFeeds = () => [],
    intervalMs = HOUR,
    timeoutMs = 20_000,
    concurrency = 4,
    maxItemsPerFeed = 60,
    fetch = globalThis.fetch,
    userAgent = 'Wallboard/1.0 (self-hosted dashboard; RSS reader)',
    now = () => Date.now(),
  }) {
    super();
    Object.assign(this, { cacheFile, getFeeds, intervalMs, timeoutMs, concurrency, maxItemsPerFeed, fetchImpl: fetch, userAgent, now });
    this.writer = new JsonWriter(cacheFile);
    this.feeds = new Map(); // url -> state
    this.requested = new Map(); // url -> last time a client asked for it
    this.lastRun = null;
    this.running = null;
    this.inflight = new Map();
    this.timer = null;
    this.nextRunAt = null;
  }

  async load() {
    const d = await readJson(this.cacheFile, null);
    if (d && typeof d === 'object') {
      for (const f of d.feeds || []) if (f?.url) this.feeds.set(f.url, f);
      for (const [u, t] of Object.entries(d.requested || {})) this.requested.set(u, t);
      this.lastRun = d.lastRun || null;
    }
    return this;
  }

  save() {
    return this.writer.write(() => ({
      lastRun: this.lastRun,
      requested: Object.fromEntries(this.requested),
      feeds: [...this.feeds.values()],
    }));
  }

  /** All feeds that should be crawled: referenced by layouts or recently requested. */
  wantedFeeds() {
    const set = new Set(this.getFeeds().filter(isFeedUrl));
    const cutoff = this.now() - REQUESTED_TTL;
    for (const [u, t] of this.requested) {
      if (t >= cutoff) set.add(u); else this.requested.delete(u);
    }
    return [...set];
  }

  /** Mark feeds as wanted by a client; unknown ones are crawled right away. */
  touch(urls) {
    const fresh = [];
    for (const u of urls) {
      if (!isFeedUrl(u)) continue;
      this.requested.set(u, this.now());
      if (!this.feeds.has(u) && !this.inflight.has(u)) fresh.push(u);
    }
    if (fresh.length) {
      Promise.all(fresh.map((u) => this.crawlOne(u))).then(() => {
        this.save();
        this.emit('crawled', { urls: fresh, finishedAt: new Date(this.now()).toISOString() });
      });
    }
    return fresh;
  }

  start() {
    this.stop();
    const last = this.lastRun?.finishedAt ? Date.parse(this.lastRun.finishedAt) : 0;
    const due = last + this.intervalMs - this.now();
    // After a restart, honour the hourly schedule instead of hammering every feed.
    this.#schedule(Math.max(due, 1500));
  }

  stop() {
    clearTimeout(this.timer);
    this.timer = null;
    this.nextRunAt = null;
  }

  #schedule(ms) {
    clearTimeout(this.timer);
    this.nextRunAt = new Date(this.now() + ms).toISOString();
    this.timer = setTimeout(async () => {
      try { await this.crawlAll({ reason: 'schedule' }); } catch (e) { console.error('[crawler]', e); }
    }, ms);
    this.timer.unref?.();
  }

  /** Crawl every wanted feed. Concurrent calls share the same run. */
  crawlAll({ reason = 'manual' } = {}) {
    if (this.running) return this.running;
    this.running = (async () => {
      const startedAt = new Date(this.now()).toISOString();
      const urls = this.wantedFeeds();
      // Forget feeds that are no longer used anywhere.
      for (const u of this.feeds.keys()) if (!urls.includes(u)) this.feeds.delete(u);
      const queue = [...urls];
      const worker = async () => { while (queue.length) await this.crawlOne(queue.shift()); };
      await Promise.all(Array.from({ length: Math.min(this.concurrency, queue.length) }, worker));
      const states = urls.map((u) => this.feeds.get(u));
      this.lastRun = {
        reason, startedAt, finishedAt: new Date(this.now()).toISOString(),
        feeds: urls.length, ok: states.filter((s) => s?.ok).length, failed: states.filter((s) => s && !s.ok).length,
      };
      await this.save();
      this.emit('crawled', { ...this.lastRun });
      return this.lastRun;
    })().finally(() => {
      this.running = null;
      if (this.timer !== null || this.nextRunAt !== null) this.#schedule(this.intervalMs);
    });
    return this.running;
  }

  /** Crawl one feed (deduplicated while in flight). Never throws. */
  crawlOne(url) {
    if (this.inflight.has(url)) return this.inflight.get(url);
    const p = this.#fetchFeed(url).finally(() => this.inflight.delete(url));
    this.inflight.set(url, p);
    return p;
  }

  async #fetchFeed(url) {
    const prev = this.feeds.get(url) || { url, items: [] };
    const t0 = this.now();
    const headers = {
      'user-agent': this.userAgent,
      accept: 'application/rss+xml, application/atom+xml, application/feed+json, application/xml;q=0.9, text/xml;q=0.9, */*;q=0.5',
    };
    if (prev.etag) headers['if-none-match'] = prev.etag;
    if (prev.lastModified) headers['if-modified-since'] = prev.lastModified;
    const next = { ...prev, url, lastCrawled: null };
    try {
      const res = await this.fetchImpl(url, { headers, redirect: 'follow', signal: AbortSignal.timeout(this.timeoutMs) });
      next.httpStatus = res.status;
      if (res.status === 304) {
        next.ok = true;
        next.error = null;
        next.notModified = true;
        next.lastSuccess = new Date(this.now()).toISOString();
      } else if (!res.ok) {
        throw new Error(`HTTP ${res.status}${res.statusText ? ' ' + res.statusText : ''}`);
      } else {
        const len = Number(res.headers.get('content-length') || 0);
        if (len > MAX_BYTES) throw new Error('Feed is larger than 5 MB');
        const buf = new Uint8Array(await res.arrayBuffer());
        if (buf.byteLength > MAX_BYTES) throw new Error('Feed is larger than 5 MB');
        const parsed = parseFeed(decodeBody(buf, res.headers.get('content-type')), res.url || url);
        const items = parsed.items
          .sort((a, b) => (b.published || '').localeCompare(a.published || ''))
          .slice(0, this.maxItemsPerFeed);
        const prevIds = new Set((prev.items || []).map((i) => i.id));
        next.newItems = items.filter((i) => !prevIds.has(i.id)).length;
        if (next.newItems || !prev.lastChanged) next.lastChanged = new Date(this.now()).toISOString();
        Object.assign(next, {
          ok: true, error: null, notModified: false,
          title: parsed.title || prev.title || new URL(url).hostname,
          siteLink: parsed.siteLink || prev.siteLink || '',
          items,
          etag: res.headers.get('etag') || null,
          lastModified: res.headers.get('last-modified') || null,
          lastSuccess: new Date(this.now()).toISOString(),
        });
      }
      next.consecutiveFailures = 0;
    } catch (err) {
      next.ok = false;
      next.error = err?.name === 'TimeoutError' || err?.name === 'AbortError'
        ? `Timed out after ${Math.round(this.timeoutMs / 1000)} s`
        : String(err?.cause?.code || err?.message || err).slice(0, 200);
      next.consecutiveFailures = (prev.consecutiveFailures || 0) + 1;
      // Keep previously cached items so the dashboard still has something to show.
    }
    next.lastCrawled = new Date(this.now()).toISOString();
    next.durationMs = this.now() - t0;
    next.itemCount = next.items?.length || 0;
    if (!next.title) next.title = safeHost(url);
    this.feeds.set(url, next);
    return next;
  }

  feedStatus(url) {
    const f = this.feeds.get(url);
    if (!f) return { url, title: safeHost(url), pending: true, ok: null, lastCrawled: null, itemCount: 0 };
    const { items, etag, lastModified, ...rest } = f;
    return rest;
  }

  getStatus() {
    return {
      intervalMs: this.intervalMs,
      running: !!this.running,
      lastRun: this.lastRun,
      nextRunAt: this.nextRunAt,
      feeds: this.wantedFeeds().map((u) => this.feedStatus(u)),
    };
  }

  /** Merged, de-duplicated, newest-first items for the given feeds. */
  getItems(urls, { limit = 50, maxAgeHours = 0 } = {}) {
    const seen = new Set();
    const out = [];
    const cutoff = maxAgeHours > 0 ? new Date(this.now() - maxAgeHours * HOUR).toISOString() : null;
    for (const u of urls) {
      const f = this.feeds.get(u);
      if (!f?.items) continue;
      for (const it of f.items) {
        if (cutoff && it.published && it.published < cutoff) continue;
        const key = (it.link || '').replace(/[?#].*$/, '') || it.title.toLowerCase();
        if (seen.has(key)) continue;
        seen.add(key);
        out.push({ ...it, source: f.title || safeHost(u), feedUrl: u });
      }
    }
    out.sort((a, b) => (b.published || '').localeCompare(a.published || ''));
    return out.slice(0, limit);
  }
}

function safeHost(u) {
  try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return u; }
}
