import { test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import http from 'node:http';
import { createApp } from '../server/app.js';
import { startFixtureServer } from '../scripts/fixture-server.js';

let fx, app, base, dataDir;
const log = () => {};

async function boot() {
  app = await createApp({ dataDir, weatherBase: fx.base, geocodeBase: fx.base, log });
  const addr = await app.listen(0, '127.0.0.1');
  base = `http://127.0.0.1:${addr.port}`;
}

before(async () => {
  fx = await startFixtureServer();
  dataDir = await mkdtemp(path.join(tmpdir(), 'wb-api-'));
  await boot();
});
after(async () => { await app.close(); await fx.close(); });

const j = async (method, p, body, headers = {}) => {
  const res = await fetch(base + p, { method, headers: { 'content-type': 'application/json', ...headers }, body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body) });
  const text = await res.text();
  let data; try { data = JSON.parse(text); } catch { data = text; }
  return { status: res.status, data, headers: res.headers };
};

test('health and status', async () => {
  const h = await j('GET', '/api/health');
  assert.equal(h.status, 200);
  assert.equal(h.data.ok, true);
  assert.ok(Number(h.headers.get('x-server-time')) > 0);
  const s = await j('GET', '/api/status');
  assert.ok(s.data.crawler.feeds.length > 0, 'starter feeds from the default layout are scheduled');
});

test('default layout, save with versioning and conflict detection', async () => {
  const d = await j('GET', '/api/layout/default');
  assert.equal(d.data.isDefault, true);
  assert.equal(d.data.pages.length, 5);
  assert.deepEqual(d.data.pages.map((p) => p.name), ['Home', 'AI', 'Tech', 'Stocks', 'Sports']);
  const pages = [{ id: 'p1', name: 'Kitchen', widgets: [{ id: 'c1', type: 'clock', x: 0, y: 0, w: 4, h: 2, settings: { showSeconds: true } }] }];
  const put = await j('PUT', '/api/layout/kitchen', { pages, baseVersion: 0 });
  assert.equal(put.status, 200);
  assert.equal(put.data.version, 1);
  const stale = await j('PUT', '/api/layout/kitchen', { pages, baseVersion: 0 });
  assert.equal(stale.status, 409);
  assert.equal(stale.data.current.version, 1);
  const forced = await j('PUT', '/api/layout/kitchen', { pages, baseVersion: 0, force: true });
  assert.equal(forced.data.version, 2);
  const got = await j('GET', '/api/layout/kitchen');
  assert.equal(got.data.pages[0].widgets[0].settings.showSeconds, true);
  const profiles = await j('GET', '/api/profiles');
  assert.ok(profiles.data.some((p) => p.profile === 'kitchen'));
});

test('layout validation', async () => {
  const bad = async (pages, re) => {
    const r = await j('PUT', '/api/layout/v', { pages });
    assert.equal(r.status, 400, JSON.stringify(r.data));
    assert.match(r.data.error, re);
  };
  await bad('x', /array/);
  await bad([], /at least one page/);
  await bad([{ name: 'a', widgets: [{ type: '../evil', x: 0, y: 0, w: 1, h: 1 }] }], /invalid widget type/);
  await bad([{ name: 'a', widgets: [{ id: 'a', type: 'clock', x: 0, y: 0, w: 4, h: 4 }, { id: 'b', type: 'clock', x: 2, y: 2, w: 4, h: 4 }] }], /overlap/);
  assert.equal((await j('PUT', '/api/layout/BAD NAME', { pages: [] })).status, 400);
  // Out-of-range geometry is clamped, not rejected.
  const ok = await j('PUT', '/api/layout/v', { pages: [{ name: 'a', widgets: [{ type: 'clock', x: 50, y: -2, w: 30, h: 3 }] }] });
  assert.deepEqual(ok.data.pages[0].widgets[0], { ...ok.data.pages[0].widgets[0], x: 0, y: 0, w: 12, h: 3 });
});

test('collections CRUD (timers / tasks / custom)', async () => {
  const add = await j('POST', '/api/c/tasks', { text: 'Buy milk', priority: 1, done: false });
  assert.equal(add.status, 201);
  const id = add.data.id;
  const again = await j('POST', '/api/c/tasks', { id, text: 'Buy milk', priority: 1, done: false });
  assert.equal(again.data.id, id, 'POST with id is idempotent');
  const patch = await j('PATCH', `/api/c/tasks/${id}`, { done: true });
  assert.equal(patch.data.done, true);
  assert.equal(patch.data.text, 'Buy milk');
  const list = await j('GET', '/api/c/tasks');
  assert.equal(list.data.items.length, 1);
  assert.ok(list.data.version >= 3);
  assert.equal((await j('PATCH', '/api/c/tasks/nope', { done: true })).status, 404);
  assert.equal((await j('DELETE', `/api/c/tasks/${id}`)).data.deleted, true);
  assert.equal((await j('DELETE', `/api/c/tasks/${id}`)).data.deleted, false, 'repeat delete is harmless');
  const t = await j('PUT', '/api/c/timers/t1', { label: '25m', durationMs: 1500000, state: 'running', endsAt: Date.now() + 1500000 });
  assert.equal(t.data.id, 't1');
  assert.equal((await j('POST', '/api/c/Bad!Name', {})).status, 400);
  assert.equal((await j('POST', '/api/c/tasks', '{oops')).status, 400);
  assert.equal((await j('POST', '/api/c/tasks', JSON.stringify({ text: 'x'.repeat(1024 * 1024 + 10) }))).status, 413);
});

test('news: on-demand crawl of new feeds, merged items, per-feed status', async () => {
  const feeds = [`${fx.base}/feeds/rss2.xml`, `${fx.base}/feeds/atom.xml`, `${fx.base}/status/404`];
  const qs = feeds.map((f) => 'feed=' + encodeURIComponent(f)).join('&');
  const first = await j('GET', `/api/news?${qs}&limit=10`);
  assert.equal(first.data.pending, 3);
  await new Promise((r) => app.crawler.once('crawled', r));
  const second = await j('GET', `/api/news?${qs}&limit=10`);
  assert.equal(second.data.pending, 0);
  assert.equal(second.data.items.length, 5);
  assert.equal(second.data.items[0].title, 'Model “Orion” tops benchmark & leaderboard');
  const bad = second.data.feeds.find((f) => f.url.endsWith('/404'));
  assert.equal(bad.ok, false);
  assert.match(bad.error, /HTTP 404/);
  const limited = await j('GET', `/api/news?${qs}&limit=2`);
  assert.equal(limited.data.items.length, 2);
});

test('manual refresh (one feed and all feeds) updates last-crawled', async () => {
  const url = `${fx.base}/feeds/rdf.xml`;
  const one = await j('POST', '/api/refresh', { url });
  assert.equal(one.data.feed.ok, true);
  const t1 = one.data.feed.lastCrawled;
  await new Promise((r) => setTimeout(r, 5));
  const all = await j('POST', '/api/refresh', {});
  assert.ok(all.data.run.feeds >= 1);
  assert.equal(all.data.run.reason, 'manual');
  const st = await j('GET', '/api/feeds/status');
  const f = st.data.feeds.find((x) => x.url === url);
  assert.ok(f.lastCrawled > t1, 'last crawled moved forward');
  assert.equal((await j('POST', '/api/refresh', { url: 'file:///etc/passwd' })).status, 400);
});

test('weather + geocode proxy with cache and stale fallback', async () => {
  const q = '/api/weather?lat=40.7128&lon=-74.006&units=fahrenheit&name=NYC';
  const a = await j('GET', q);
  assert.equal(a.status, 200);
  assert.equal(a.data.current.temperature_2m, 54.3);
  assert.ok(a.data.fetchedAt);
  const hits = fx.hits.get('/v1/forecast');
  const b = await j('GET', q);
  assert.equal(b.data.cached, true);
  assert.equal(fx.hits.get('/v1/forecast'), hits, 'served from cache');
  assert.equal((await j('GET', '/api/weather?lat=999&lon=0')).status, 400);
  fx.state.weatherFail = true;
  const fail = await j('GET', '/api/weather?lat=1&lon=1');
  assert.equal(fail.status, 502);
  fx.state.weatherFail = false;
  const st = await j('GET', '/api/status');
  assert.ok(st.data.weather.some((w) => w.label === 'NYC' && w.ok));
  assert.ok(st.data.weather.some((w) => !w.ok && w.error));
  const g = await j('GET', '/api/geocode?q=springfield');
  assert.equal(g.data.results.length, 2);
  assert.equal(g.data.results[0].admin1, 'Illinois');
});

test('server-sent events announce changes and crawls', async () => {
  const events = [];
  const req = http.get(base + '/api/events');
  const res = await new Promise((r) => req.on('response', r));
  assert.equal(res.headers['content-type'], 'text/event-stream; charset=utf-8');
  res.setEncoding('utf8');
  let buf = '';
  res.on('data', (d) => {
    buf += d;
    let i;
    while ((i = buf.indexOf('\n\n')) >= 0) {
      const chunk = buf.slice(0, i); buf = buf.slice(i + 2);
      const ev = /event: (\w+)/.exec(chunk)?.[1];
      const data = /data: (.*)/.exec(chunk)?.[1];
      if (ev) events.push({ ev, data: JSON.parse(data) });
    }
  });
  await new Promise((r) => setTimeout(r, 50));
  await j('POST', '/api/c/timers', { label: 'x' });
  await j('POST', '/api/refresh', { url: `${fx.base}/feeds/atom.xml` });
  await new Promise((r) => setTimeout(r, 100));
  req.destroy();
  assert.equal(events[0].ev, 'hello');
  assert.ok(events.some((e) => e.ev === 'change' && e.data.kind === 'collection' && e.data.name === 'timers'));
  assert.ok(events.some((e) => e.ev === 'crawl'));
});

test('static files: MIME, etag/304, traversal blocked, custom widget overlay', async () => {
  const r = await fetch(base + '/');
  assert.equal(r.status, 200);
  assert.match(r.headers.get('content-type'), /text\/html/);
  const etag = r.headers.get('etag');
  const r2 = await fetch(base + '/', { headers: { 'if-none-match': etag } });
  assert.equal(r2.status, 304);
  const js = await fetch(base + '/js/lib/grid.js');
  assert.match(js.headers.get('content-type'), /text\/javascript/);
  for (const p of ['/../package.json', '/%2e%2e/package.json', '/..%2fserver/app.js', '/widgets/..%2f..%2fpackage.json']) {
    const t = await fetch(base + p);
    assert.ok([403, 404, 400].includes(t.status), `${p} -> ${t.status}`);
  }
  assert.equal((await fetch(base + '/nope.js')).status, 404);
  assert.equal((await fetch(base + '/api/nope')).status, 404);
  assert.equal((await fetch(base + '/api/health', { method: 'DELETE' })).status, 405);
  // A custom widget dropped into DATA_DIR/widgets is listed and served.
  await mkdir(path.join(dataDir, 'widgets', 'hello'), { recursive: true });
  await writeFile(path.join(dataDir, 'widgets', 'hello', 'manifest.json'), JSON.stringify({ name: 'Hello', size: { w: 2, h: 2 } }));
  await writeFile(path.join(dataDir, 'widgets', 'hello', 'widget.js'), 'export function mount(){}');
  const reg = await j('GET', '/api/widgets');
  const hello = reg.data.find((w) => w.id === 'hello');
  assert.equal(hello.origin, 'custom');
  assert.equal((await fetch(base + '/widgets/hello/widget.js')).status, 200);
});

test('state survives a restart', async () => {
  await j('PUT', '/api/c/tasks/keep', { text: 'persist me', priority: 2 });
  await app.close();
  await boot();
  const t = await j('GET', '/api/c/tasks');
  assert.ok(t.data.items.some((i) => i.id === 'keep'));
  const k = await j('GET', '/api/layout/kitchen');
  assert.equal(k.data.pages[0].name, 'Kitchen');
  const st = await j('GET', '/api/feeds/status');
  assert.ok(st.data.feeds.some((f) => f.url.endsWith('rdf.xml') && f.ok), 'feed cache reloaded');
});
