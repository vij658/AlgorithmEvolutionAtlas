import http from 'node:http';
import https from 'node:https';
import { promises as fs, createReadStream, readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Store, NAME_RE } from './store.js';
import { Crawler, isFeedUrl } from './crawler.js';
import { Weather } from './weather.js';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const PKG = JSON.parse(readFileSync(path.join(ROOT, 'package.json'), 'utf8'));
const MAX_BODY = 1024 * 1024;

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.webmanifest': 'application/manifest+json',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.ico': 'image/x-icon', '.txt': 'text/plain; charset=utf-8', '.mp4': 'video/mp4', '.webm': 'video/webm',
  '.woff2': 'font/woff2', '.md': 'text/markdown; charset=utf-8',
};

class HttpError extends Error {
  constructor(status, msg) { super(msg); this.status = status; }
}

function send(res, status, body, headers = {}) {
  const isBuf = Buffer.isBuffer(body) || typeof body === 'string';
  const data = isBuf ? body : JSON.stringify(body);
  res.writeHead(status, {
    'content-type': isBuf ? 'text/plain; charset=utf-8' : 'application/json; charset=utf-8',
    'cache-control': 'no-store',
    'x-server-time': String(Date.now()),
    ...headers,
  });
  res.end(data);
}

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const c of req) {
    size += c.length;
    if (size > MAX_BODY) throw new HttpError(413, 'Request body too large');
    chunks.push(c);
  }
  if (!size) return {};
  try { return JSON.parse(Buffer.concat(chunks).toString('utf8')); } catch { throw new HttpError(400, 'Invalid JSON'); }
}

/**
 * Build the Wallboard server. Nothing listens until `listen()` is called, which keeps
 * tests simple (port 0, temp data dir, fake fetch).
 */
export async function createApp({
  dataDir = process.env.DATA_DIR || path.join(ROOT, 'data'),
  publicDir = path.join(ROOT, 'public'),
  extraWidgetsDir = path.join(dataDir, 'widgets'),
  crawlIntervalMs = Number(process.env.CRAWL_INTERVAL_MINUTES || 60) * 60_000,
  fetch = globalThis.fetch,
  weatherBase = process.env.OPEN_METEO_BASE || undefined,
  geocodeBase = process.env.OPEN_METEO_GEO_BASE || undefined,
  tls = null,
  log = (...a) => console.log('[wallboard]', ...a),
} = {}) {
  await fs.mkdir(dataDir, { recursive: true });
  publicDir = path.resolve(publicDir);
  extraWidgetsDir = path.resolve(extraWidgetsDir);
  const store = await new Store(path.join(dataDir, 'state.json')).load();
  const crawler = await new Crawler({
    cacheFile: path.join(dataDir, 'feed-cache.json'),
    getFeeds: () => store.allFeedUrls(),
    intervalMs: crawlIntervalMs,
    fetch,
  }).load();
  const weather = new Weather({ base: weatherBase, geoBase: geocodeBase, fetch });
  const startedAt = new Date().toISOString();

  // ---- server-sent events ---------------------------------------------------
  const clients = new Set();
  function broadcast(event, data) {
    const msg = `event: ${event}\ndata: ${JSON.stringify({ ...data, serverTime: Date.now() })}\n\n`;
    for (const c of clients) c.write(msg);
  }
  store.on('change', (e) => broadcast('change', e));
  crawler.on('crawled', (e) => broadcast('crawl', e));
  const keepAlive = setInterval(() => { for (const c of clients) c.write(': ping\n\n'); }, 25_000);
  keepAlive.unref();

  // ---- widgets registry -----------------------------------------------------
  async function listWidgets() {
    const out = new Map();
    for (const [dir, origin] of [[path.join(publicDir, 'widgets'), 'builtin'], [extraWidgetsDir, 'custom']]) {
      let entries = [];
      try { entries = await fs.readdir(dir, { withFileTypes: true }); } catch { continue; }
      for (const e of entries) {
        if (!e.isDirectory() || e.name.startsWith('_') || e.name.startsWith('.') || !NAME_RE.test(e.name)) continue;
        try {
          const m = JSON.parse(await fs.readFile(path.join(dir, e.name, 'manifest.json'), 'utf8'));
          out.set(e.name, { ...m, id: e.name, module: m.module || 'widget.js', origin });
        } catch (err) {
          log(`widget "${e.name}" has an unreadable manifest: ${err.message}`);
        }
      }
    }
    return [...out.values()].sort((a, b) => (a.order ?? 100) - (b.order ?? 100) || a.id.localeCompare(b.id));
  }

  // ---- static files ---------------------------------------------------------
  async function serveStatic(req, res, pathname) {
    let rel;
    try { rel = decodeURIComponent(pathname); } catch { throw new HttpError(400, 'Bad path'); }
    if (rel.includes('\0')) throw new HttpError(400, 'Bad path');
    if (rel.endsWith('/')) rel += 'index.html';
    const candidates = [];
    // Custom widgets dropped into DATA_DIR/widgets override / extend the built-in ones.
    if (rel.startsWith('/widgets/')) candidates.push([extraWidgetsDir, rel.slice('/widgets'.length)]);
    candidates.push([publicDir, rel]);
    for (const [base, r] of candidates) {
      const file = path.resolve(base, '.' + path.posix.normalize(r));
      if (file !== base && !file.startsWith(base + path.sep)) throw new HttpError(403, 'Forbidden');
      let st;
      try { st = await fs.stat(file); } catch { continue; }
      if (st.isDirectory()) continue;
      const etag = `W/"${st.size.toString(36)}-${Math.floor(st.mtimeMs).toString(36)}"`;
      const headers = {
        'content-type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream',
        // Always revalidate: deployments are rare, but a stale app shell on a wall
        // screen nobody touches is worse than a cheap 304.
        'cache-control': 'no-cache',
        etag,
        'x-content-type-options': 'nosniff',
      };
      if (path.basename(file) === 'sw.js') headers['service-worker-allowed'] = '/';
      if (req.headers['if-none-match'] === etag) { res.writeHead(304, headers); res.end(); return; }
      headers['content-length'] = st.size;
      res.writeHead(200, headers);
      if (req.method === 'HEAD') { res.end(); return; }
      createReadStream(file).pipe(res);
      return;
    }
    throw new HttpError(404, 'Not found');
  }

  // ---- API ------------------------------------------------------------------
  const routes = [];
  const route = (method, pattern, fn) => routes.push({ method, pattern, fn });

  route('GET', /^\/api\/health$/, () => ({ ok: true, version: PKG.version, startedAt, now: Date.now() }));

  route('GET', /^\/api\/status$/, () => ({
    server: { version: PKG.version, startedAt, now: Date.now(), sseClients: clients.size },
    crawler: crawler.getStatus(),
    weather: weather.status(),
  }));

  route('GET', /^\/api\/widgets$/, () => listWidgets());

  route('GET', /^\/api\/profiles$/, () => store.listProfiles());
  route('GET', /^\/api\/layout\/([^/]+)$/, (req, m) => store.getLayout(m[1]));
  route('PUT', /^\/api\/layout\/([^/]+)$/, (req, m, body) => store.putLayout(m[1], body));
  route('DELETE', /^\/api\/layout\/([^/]+)$/, (req, m) => ({ deleted: store.deleteLayout(m[1]) }));

  route('GET', /^\/api\/c\/([^/]+)$/, (req, m) => store.getCollection(m[1]));
  route('PUT', /^\/api\/c\/([^/]+)$/, (req, m, body) => store.replaceCollection(m[1], body.items));
  route('POST', /^\/api\/c\/([^/]+)$/, (req, m, body) => [201, store.addItem(m[1], body)]);
  route('PUT', /^\/api\/c\/([^/]+)\/([^/]+)$/, (req, m, body) => store.putItem(m[1], decodeURIComponent(m[2]), body));
  route('PATCH', /^\/api\/c\/([^/]+)\/([^/]+)$/, (req, m, body) => {
    const r = store.patchItem(m[1], decodeURIComponent(m[2]), body);
    if (!r) throw new HttpError(404, 'No such item');
    return r;
  });
  route('DELETE', /^\/api\/c\/([^/]+)\/([^/]+)$/, (req, m) => {
    // Deleting something already gone is fine: offline clients replay deletes.
    return { deleted: store.deleteItem(m[1], decodeURIComponent(m[2])) };
  });

  route('GET', /^\/api\/news$/, (req, m, body, url) => {
    const feeds = [...new Set(url.searchParams.getAll('feed').map((s) => s.trim()).filter(isFeedUrl))].slice(0, 40);
    const limit = Math.min(200, Math.max(1, Number(url.searchParams.get('limit')) || 40));
    const maxAgeHours = Math.max(0, Number(url.searchParams.get('maxAgeHours')) || 0);
    const pending = crawler.touch(feeds);
    return {
      items: crawler.getItems(feeds, { limit, maxAgeHours }),
      feeds: feeds.map((u) => crawler.feedStatus(u)),
      pending: pending.length,
      lastRun: crawler.lastRun,
    };
  });

  route('GET', /^\/api\/feeds\/status$/, () => crawler.getStatus());

  route('POST', /^\/api\/refresh$/, async (req, m, body) => {
    if (body?.url) {
      if (!isFeedUrl(body.url)) throw new HttpError(400, 'Invalid feed URL');
      crawler.requested.set(body.url, Date.now());
      const st = await crawler.crawlOne(body.url);
      await crawler.save();
      crawler.emit('crawled', { urls: [body.url], finishedAt: new Date().toISOString() });
      return { feed: crawler.feedStatus(st.url) };
    }
    const run = await crawler.crawlAll({ reason: 'manual' });
    return { run, status: crawler.getStatus() };
  });

  route('GET', /^\/api\/weather$/, (req, m, body, url) => weather.forecast(Weather.params(url.searchParams)));
  route('GET', /^\/api\/geocode$/, (req, m, body, url) => weather.geocode(url.searchParams.get('q')));

  async function handle(req, res) {
    const url = new URL(req.url, 'http://local');
    const { pathname } = url;
    try {
      if (pathname === '/api/events') {
        res.writeHead(200, {
          'content-type': 'text/event-stream; charset=utf-8',
          'cache-control': 'no-cache, no-transform',
          connection: 'keep-alive',
          'x-accel-buffering': 'no', // nginx (Synology reverse proxy) must not buffer
        });
        res.write(`retry: 5000\nevent: hello\ndata: ${JSON.stringify({ serverTime: Date.now(), version: PKG.version })}\n\n`);
        clients.add(res);
        req.on('close', () => clients.delete(res));
        return;
      }
      if (pathname.startsWith('/api/')) {
        const matches = routes.filter((r) => r.pattern.test(pathname));
        if (!matches.length) throw new HttpError(404, 'Unknown API endpoint');
        const r = matches.find((x) => x.method === req.method);
        if (!r) throw new HttpError(405, 'Method not allowed');
        const body = ['POST', 'PUT', 'PATCH'].includes(req.method) ? await readBody(req) : null;
        let out = await r.fn(req, pathname.match(r.pattern), body, url);
        let status = 200;
        if (Array.isArray(out) && out.length === 2 && typeof out[0] === 'number') [status, out] = out;
        return send(res, status, out);
      }
      if (req.method !== 'GET' && req.method !== 'HEAD') throw new HttpError(405, 'Method not allowed');
      await serveStatic(req, res, pathname);
    } catch (err) {
      const status = err.status || 500;
      if (status >= 500) log(`${req.method} ${pathname} failed:`, err);
      if (res.headersSent) { res.end(); return; }
      send(res, status, { error: err.message || 'Error', ...(err.current ? { current: err.current } : {}) });
    }
  }

  const server = tls ? https.createServer(tls, handle) : http.createServer(handle);
  server.keepAliveTimeout = 65_000;

  return {
    server, store, crawler, weather,
    listen(port = 8080, host = '0.0.0.0') {
      return new Promise((resolve) => server.listen(port, host, () => resolve(server.address())));
    },
    async close() {
      crawler.stop();
      clearInterval(keepAlive);
      for (const c of clients) c.end();
      clients.clear();
      const closed = new Promise((r) => server.close(r));
      server.closeAllConnections?.();
      await closed;
      await store.flush();
      await crawler.writer.flush();
    },
  };
}
