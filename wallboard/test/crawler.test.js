import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, readFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { Crawler } from '../server/crawler.js';
import { startFixtureServer } from '../scripts/fixture-server.js';

let fx, dir;
before(async () => { fx = await startFixtureServer(); dir = await mkdtemp(path.join(tmpdir(), 'wb-crawl-')); });
after(() => fx.close());

const mk = (feeds, opts = {}) => new Crawler({ cacheFile: path.join(dir, `cache-${Math.random()}.json`), getFeeds: () => feeds, timeoutMs: 500, ...opts });

test('crawls all formats, records per-feed status, merges items newest-first', async () => {
  const feeds = ['rss2.xml', 'atom.xml', 'rdf.xml', 'jsonfeed.json', 'latin1.xml'].map((f) => `${fx.base}/feeds/${f}`);
  const c = mk(feeds);
  const run = await c.crawlAll();
  assert.equal(run.feeds, 5);
  assert.equal(run.ok, 5);
  assert.equal(run.failed, 0);
  const st = c.getStatus();
  for (const f of st.feeds) {
    assert.equal(f.ok, true, f.url);
    assert.ok(f.lastCrawled && f.lastSuccess, 'timestamps set');
    assert.ok(f.itemCount > 0);
    assert.equal(f.httpStatus, 200);
    assert.equal(f.items, undefined, 'status does not leak items');
  }
  assert.equal(st.feeds.find((f) => f.url.endsWith('atom.xml')).title, 'Fixture Tech Wire');
  const items = c.getItems(feeds, { limit: 100 });
  assert.equal(items[0].title, 'Stocks rally as rates hold', 'newest first');
  assert.ok(items.every((i) => i.source && i.feedUrl));
  const dated = items.filter((i) => i.published).map((i) => i.published);
  assert.deepEqual(dated, [...dated].sort().reverse());
});

test('failures are recorded but cached items survive', async () => {
  const url = `${fx.base}/flaky.xml`;
  const c = mk([url]);
  await c.crawlAll();
  assert.equal(c.feedStatus(url).ok, true);
  fx.state.flakyFail = true;
  await c.crawlAll();
  const s = c.feedStatus(url);
  assert.equal(s.ok, false);
  assert.match(s.error, /^HTTP 503/);
  assert.equal(s.consecutiveFailures, 1);
  assert.ok(s.lastSuccess < s.lastCrawled || s.lastSuccess <= s.lastCrawled);
  assert.equal(c.getItems([url]).length, 1, 'stale items still served');
  fx.state.flakyFail = false;
});

test('HTTP errors, HTML pages, timeouts and redirects', async () => {
  const urls = { e500: `${fx.base}/status/500`, html: `${fx.base}/feeds/not-a-feed.html`, slow: `${fx.base}/slow`, redir: `${fx.base}/redirect`, dns: 'http://does-not-exist.invalid/feed' };
  const c = mk(Object.values(urls), { timeoutMs: 300 });
  const run = await c.crawlAll();
  assert.equal(run.ok, 1);
  assert.equal(run.failed, 4);
  assert.match(c.feedStatus(urls.e500).error, /HTTP 500/);
  assert.match(c.feedStatus(urls.html).error, /HTML page/);
  assert.match(c.feedStatus(urls.slow).error, /Timed out/);
  assert.ok(c.feedStatus(urls.dns).error, 'dns failure reported');
  assert.equal(c.feedStatus(urls.redir).title, 'Fixture Tech Wire');
  assert.equal(c.getItems([urls.redir])[0].link, 'https://tech.example.com/posts/1nm');
});

test('conditional GET: 304 keeps items and counts as success', async () => {
  const url = `${fx.base}/etag.xml`;
  const c = mk([url]);
  await c.crawlAll();
  await c.crawlAll();
  const s = c.feedStatus(url);
  assert.equal(s.httpStatus, 304);
  assert.equal(s.notModified, true);
  assert.equal(s.ok, true);
  assert.equal(c.getItems([url]).length, 3);
});

test('cache persists across restarts; schedule honours the interval', async () => {
  const file = path.join(dir, 'persist.json');
  const url = `${fx.base}/feeds/rss2.xml`;
  const a = new Crawler({ cacheFile: file, getFeeds: () => [url] });
  await a.crawlAll();
  const saved = JSON.parse(await readFile(file, 'utf8'));
  assert.equal(saved.feeds[0].items.length, 3);
  const b = await new Crawler({ cacheFile: file, getFeeds: () => [url], intervalMs: 3_600_000 }).load();
  assert.equal(b.getItems([url]).length, 3);
  b.start();
  const due = Date.parse(b.nextRunAt) - Date.now();
  assert.ok(due > 3_500_000, `next run ~1h after the last one, got ${due}`);
  b.stop();
});

test('scheduled crawling repeats on the interval', async () => {
  const url = `${fx.base}/feeds/rdf.xml?sched`;
  const c = mk([url], { intervalMs: 150 });
  const runs = [];
  c.on('crawled', (e) => runs.push(e));
  c.start(); // first run after 1.5 s (startup grace), then every 150 ms
  await new Promise((r) => setTimeout(r, 2000));
  c.stop();
  assert.ok(runs.length >= 2, `expected repeated runs, got ${runs.length}`);
  assert.ok(runs.every((r) => r.reason === 'schedule'));
});

test('concurrent crawlAll calls share one run; touch() crawls new feeds at once', async () => {
  const url = `${fx.base}/feeds/atom.xml?share`;
  const c = mk([url]);
  const before = fx.hits.get('/feeds/atom.xml') || 0;
  const [r1, r2] = await Promise.all([c.crawlAll(), c.crawlAll()]);
  assert.equal(r1, r2);
  assert.equal(fx.hits.get('/feeds/atom.xml') - before, 1);
  const extra = `${fx.base}/feeds/jsonfeed.json?touch`;
  const done = new Promise((r) => c.once('crawled', r));
  assert.deepEqual(c.touch([extra, 'javascript:alert(1)']), [extra]);
  await done;
  assert.equal(c.feedStatus(extra).ok, true);
  assert.ok(c.wantedFeeds().includes(extra), 'requested feeds join the schedule');
});
