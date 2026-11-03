// Screenshot / smoke-test harness. Runs the real server against local fixture feeds and
// a fake Open-Meteo, seeds timers and tasks, then drives Chromium at TV, iPad and phone
// sizes. Fails (exit 1) on console errors, failed requests or horizontal overflow.
//
//   node scripts/screenshots.mjs [outDir] [--dsf=2] [--only=tv,phone]
import { createRequire } from 'node:module';
import { mkdtemp, mkdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { createApp } from '../server/app.js';
import { startFixtureServer } from './fixture-server.js';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const outDir = path.resolve(args.find((a) => !a.startsWith('--')) || 'screenshots');
const dsf = Number(args.find((a) => a.startsWith('--dsf='))?.split('=')[1] || 1);
const only = args.find((a) => a.startsWith('--only='))?.split('=')[1]?.split(',');
await mkdir(outDir, { recursive: true });

const fx = await startFixtureServer();
const dataDir = await mkdtemp(path.join(tmpdir(), 'wb-shots-'));
const app = await createApp({ dataDir, weatherBase: fx.base, geocodeBase: fx.base, log: () => {} });
const { port } = await app.listen(0, '127.0.0.1');
const base = `http://127.0.0.1:${port}`;
const api = async (method, p, body) => {
  const r = await fetch(base + p, { method, headers: { 'content-type': 'application/json' }, body: body && JSON.stringify(body) });
  if (!r.ok) throw new Error(`${method} ${p}: ${r.status} ${await r.text()}`);
  return r.json();
};

// ---- seed ---------------------------------------------------------------------------
const layout = await api('GET', '/api/layout/default');
for (const page of layout.pages) {
  for (const w of page.widgets) {
    if (w.type === 'news') {
      const t = w.settings.topic;
      w.settings.feeds = [`${fx.base}/gen/${t}.xml?n=30`, `${fx.base}/feeds/${t === 'ai' ? 'rss2.xml' : t === 'tech' ? 'atom.xml' : 'rdf.xml'}`];
      if (t === 'tech') w.settings.feeds.push(`${fx.base}/status/500`); // one failing feed, as in real life
    }
    if (w.type === 'weather') w.settings.location = { name: 'New York', lat: 40.71, lon: -74.01 };
    if (w.type === 'weather') w.settings.units = 'fahrenheit';
  }
}
await api('PUT', '/api/layout/default', { pages: layout.pages, force: true });
await api('POST', '/api/refresh', {});
const now = Date.now();
for (const t of [
  { id: 't1', label: 'Pasta', durationMs: 10 * 60_000, state: 'running', endsAt: now + 6 * 60_000 + 12_000, group: 'default' },
  { id: 't2', label: '25m focus', durationMs: 25 * 60_000, state: 'running', endsAt: now + 17 * 60_000 + 40_000, group: 'default' },
  { id: 't3', label: 'Laundry', durationMs: 60 * 60_000, state: 'paused', remainingMs: 41 * 60_000, group: 'default' },
]) await api('PUT', `/api/c/timers/${t.id}`, t);
for (const [i, t] of [['Call the plumber', 1], ['Renew passport', 1], ['Buy milk & eggs', 2], ['Water the plants', 2], ['Back up the NAS', 3], ['Pick up dry cleaning', 3, true]].entries()) {
  await api('PUT', `/api/c/tasks/k${i}`, { text: t[0], priority: t[1], done: !!t[2], list: 'default', createdAt: new Date(now - (10 - i) * 60_000).toISOString(), doneAt: t[2] ? new Date().toISOString() : null });
}

// ---- drive the browser --------------------------------------------------------------
const DEVICES = {
  tv: { viewport: { width: 1920, height: 1080 }, query: '?tv=1', deviceScaleFactor: 1, userAgent: 'Mozilla/5.0 (Linux; Android 9; AFTMM Build/PS7633) AppleWebKit/537.36 (KHTML, like Gecko) Silk/120.4.1 like Chrome/120.0.6099.230 Safari/537.36' },
  'ipad-landscape': { viewport: { width: 1180, height: 820 }, hasTouch: true, isMobile: true, deviceScaleFactor: dsf },
  'ipad-portrait': { viewport: { width: 820, height: 1180 }, hasTouch: true, isMobile: true, deviceScaleFactor: dsf },
  phone: { viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, deviceScaleFactor: dsf },
};

const problems = [];
const browser = await chromium.launch();
for (const [name, dev] of Object.entries(DEVICES)) {
  if (only && !only.includes(name)) continue;
  const { query = '', ...opts } = dev;
  const context = await browser.newContext({ ...opts, timezoneId: 'America/New_York', locale: 'en-US', serviceWorkers: 'block' });
  // The sandbox has no internet: serve thumbnails that fixture feeds point at externally.
  await context.route((u) => !u.hostname.startsWith('127.0.0.1'), (route) =>
    route.request().resourceType() === 'image' ? route.fulfill({ path: new URL('../public/icons/icon-192.png', import.meta.url).pathname }) : route.abort());
  const page = await context.newPage();
  page.on('console', (m) => { if (m.type() === 'error') problems.push(`[${name}] console: ${m.text()}`); });
  page.on('pageerror', (e) => problems.push(`[${name}] pageerror: ${e.message}`));
  page.on('requestfailed', (r) => {
    const u = r.url();
    if (u.includes('/api/events')) return; // SSE is torn down on navigation
    problems.push(`[${name}] request failed: ${u} ${r.failure()?.errorText}`);
  });
  await page.goto(base + '/' + query);
  await page.waitForSelector('.w-news .nw-item', { state: 'attached', timeout: 15000 });
  await page.waitForSelector('.w-weather .wx-temp', { timeout: 15000 });
  await page.waitForTimeout(800);
  const shot = async (label) => {
    // Overflow check: nothing may stick out of the viewport horizontally.
    const overflow = await page.evaluate(() => {
      const bad = [];
      const vw = document.documentElement.clientWidth;
      if (document.documentElement.scrollWidth > vw + 1) bad.push(`document scrollWidth ${document.documentElement.scrollWidth} > ${vw}`);
      const current = document.querySelector('.page:not([inert])');
      for (const c of current?.querySelectorAll('.card') || []) {
        const r = c.getBoundingClientRect();
        if (r.right > vw + 1 || r.left < -1) bad.push(`card ${c.dataset.type} spans ${Math.round(r.left)}..${Math.round(r.right)}`);
        // Text overflowing its own card horizontally means a layout bug in the widget.
        if (c.scrollWidth > c.clientWidth + 2) bad.push(`card ${c.dataset.type} content overflows (${c.scrollWidth} > ${c.clientWidth})`);
      }
      return bad;
    });
    for (const o of overflow) problems.push(`[${name}/${label}] ${o}`);
    await page.screenshot({ path: path.join(outDir, `${name}-${label}.png`) });
  };
  await shot('1-home');
  await page.evaluate(() => window.wallboard.board.goTo(1, { instant: true }));
  await page.waitForTimeout(400);
  await shot('2-ai-news');
  await page.evaluate(() => window.wallboard.board.goTo(2, { instant: true }));
  await page.waitForTimeout(400);
  await shot('3-tech-news');
  await page.evaluate(() => window.wallboard.board.goTo(0, { instant: true }));
  await page.keyboard.press('e');
  await page.waitForSelector('#edit-bar');
  await page.waitForTimeout(300);
  await shot('4-edit');
  if (name === 'tv' || name === 'phone') {
    await page.click('.card[data-type="weather"] .eo-settings');
    await page.waitForSelector('.modal');
    await page.waitForTimeout(200);
    await page.screenshot({ path: path.join(outDir, `${name}-5-settings.png`) });
    await page.keyboard.press('Escape');
    await page.click('#edit-bar .btn.primary');
    await page.waitForSelector('.palette');
    await page.screenshot({ path: path.join(outDir, `${name}-6-palette.png`) });
    await page.keyboard.press('Escape');
  }
  await page.keyboard.press('Escape');
  await context.close();
}
await browser.close();
await app.close();
await fx.close();

if (problems.length) {
  console.log(`\n${problems.length} problem(s):\n` + problems.map((p) => '  - ' + p).join('\n'));
  process.exitCode = 1;
} else {
  console.log(`screenshots written to ${outDir}; no console errors, failed requests or overflow`);
}
