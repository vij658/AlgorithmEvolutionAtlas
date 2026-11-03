// End-to-end checks in Chromium against the real server + local fixtures.
//   node scripts/e2e.mjs
import { createRequire } from 'node:module';
import { mkdtemp } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { createApp } from '../server/app.js';
import { startFixtureServer } from './fixture-server.js';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const fx = await startFixtureServer();
const dataDir = await mkdtemp(path.join(tmpdir(), 'wb-e2e-'));
const app = await createApp({ dataDir, weatherBase: fx.base, geocodeBase: fx.base, log: () => {} });
const { port } = await app.listen(0, '127.0.0.1');
const base = `http://localhost:${port}`; // localhost counts as a secure context (service worker, wake lock)
const api = async (method, p, body) => {
  const r = await fetch(base + p, { method, headers: { 'content-type': 'application/json' }, body: body && JSON.stringify(body) });
  return r.json();
};

// Point the news widgets at fixture feeds.
const layout = await api('GET', '/api/layout/default');
for (const p of layout.pages) for (const w of p.widgets) {
  if (w.type === 'news') w.settings.feeds = [`${fx.base}/gen/${w.settings.topic}.xml`];
}
await api('PUT', '/api/layout/default', { pages: layout.pages, force: true });
await api('POST', '/api/refresh', {});

const browser = await chromium.launch();
const errors = [];
async function open(opts = {}, prefs = {}) {
  const { query = '', sw = false, ...ctxOpts } = opts;
  const context = await browser.newContext({ viewport: { width: 1280, height: 800 }, timezoneId: 'America/New_York', locale: 'en-US', serviceWorkers: sw ? 'allow' : 'block', ...ctxOpts });
  await context.route((u) => !['localhost', '127.0.0.1'].includes(u.hostname), (r) => r.abort());
  await context.addInitScript((p) => { try { if (!localStorage.getItem('wb:prefs')) localStorage.setItem('wb:prefs', JSON.stringify(p)); } catch { /* error pages */ } }, { drift: false, ...prefs });
  const page = await context.newPage();
  page.setDefaultTimeout(6000);
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(base + '/' + query);
  await page.waitForSelector('.w-timers .tm-preset');
  return { context, page };
}
const pageIndex = (page) => page.evaluate(() => window.wallboard.board.currentIndex());
const results = [];
let A, B;
const failDir = process.env.E2E_FAIL_DIR;
let current = null;
async function step(name, fn) {
  for (const p of [A, B]) if (p && !p.isClosed()) await p.evaluate(() => window.wallboard?.board.goTo(0, { instant: true })).catch(() => {});
  try { await fn(); results.push(`  ✓ ${name}`); } catch (e) {
    results.push(`  ✗ ${name}\n      ${e.message.split('\n').slice(0, 3).join(' ')}`);
    process.exitCode = 1;
    if (failDir && current && !current.isClosed()) {
      await current.screenshot({ path: path.join(failDir, `fail-${results.length}.png`) }).catch(() => {});
      results.push('      state: ' + JSON.stringify(await current.evaluate(() => ({ cls: document.documentElement.className, idx: window.wallboard?.board.currentIndex(), modal: !!document.querySelector('.modal') })).catch((x) => x.message)));
    }
  }
}

const { context: ctxA, page: pA } = await open();
A = pA;
current = A;
const { context: ctxB, page: pB } = await open({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
B = pB;

await step('swipe left/right changes pages', async () => {
  await A.mouse.move(700, 600); await A.mouse.down(); await A.mouse.move(500, 605, { steps: 5 }); await A.mouse.move(250, 610, { steps: 5 }); await A.mouse.up();
  await A.waitForTimeout(500);
  assert.equal(await pageIndex(A), 1);
  await A.mouse.move(300, 600); await A.mouse.down(); await A.mouse.move(800, 600, { steps: 8 }); await A.mouse.up();
  await A.waitForTimeout(500);
  assert.equal(await pageIndex(A), 0);
});

await step('arrow keys flip pages when nothing is focused; dots work', async () => {
  await A.keyboard.press('ArrowRight');
  assert.equal(await pageIndex(A), 1);
  await A.keyboard.press('ArrowLeft');
  assert.equal(await pageIndex(A), 0);
  await A.click('#dots .dot:nth-child(3)');
  assert.equal(await pageIndex(A), 2);
  await A.click('#dots .dot:nth-child(1)');
});

await step('timer presets and custom timers start and sync to another screen', async () => {
  await A.click('.w-timers .tm-preset:text-is("5m")');
  await A.fill('.w-timers .tm-input', '90s Tea');
  await A.press('.w-timers .tm-input', 'Enter');
  await A.waitForTimeout(400);
  const t = (await api('GET', '/api/c/timers')).items;
  assert.equal(t.length, 2);
  assert.ok(t.some((x) => x.label === 'Tea' && x.durationMs === 90_000));
  await B.waitForFunction(() => document.querySelectorAll('.w-timers .tm-row').length === 2, null, { timeout: 5000 });
  await A.click('.w-timers .tm-row:has-text("Tea") button[title="Pause"]');
  await A.waitForTimeout(300);
  assert.equal((await api('GET', '/api/c/timers')).items.find((x) => x.label === 'Tea').state, 'paused');
});

await step('a finished timer rings (flash + banner)', async () => {
  await api('POST', '/api/c/timers', { id: 'soon', label: 'Eggs', durationMs: 1000, state: 'running', endsAt: Date.now() + 800, group: 'default' });
  await A.waitForSelector('.w-timers .tm-row.ringing', { timeout: 5000 });
  await A.waitForSelector('.toast:has-text("Eggs is done")', { timeout: 3000 });
  await A.click('.tm-row.ringing .tm-dismiss');
  await A.waitForTimeout(300);
  assert.ok(!(await api('GET', '/api/c/timers')).items.some((x) => x.id === 'soon'));
});

await step('tasks: add with priority, complete, cycle priority, live on other screen', async () => {
  await A.click('.w-tasks .tk-pri-pick'); // normal -> low
  await A.click('.w-tasks .tk-pri-pick'); // low -> high
  await A.fill('.w-tasks .tk-input', 'Feed the cat');
  await A.press('.w-tasks .tk-input', 'Enter');
  await A.waitForTimeout(300);
  let task = (await api('GET', '/api/c/tasks')).items.find((x) => x.text === 'Feed the cat');
  assert.equal(task.priority, 1);
  await B.waitForSelector('.w-tasks .tk-row:has-text("Feed the cat")', { timeout: 5000 });
  await B.click('.w-tasks .tk-row:has-text("Feed the cat") .tk-check');
  await A.waitForSelector('.w-tasks .tk-row[data-done="1"]:has-text("Feed the cat")', { timeout: 5000 });
  await A.click('.w-tasks .tk-row:has-text("Feed the cat") .tk-pri');
  await A.waitForTimeout(300);
  task = (await api('GET', '/api/c/tasks')).items.find((x) => x.text === 'Feed the cat');
  assert.equal(task.done, true);
  assert.equal(task.priority, 2);
});

await step('tasks are kept locally while offline and sent when back', async () => {
  await ctxB.setOffline(true);
  await B.fill('.w-tasks .tk-input', 'Offline idea');
  await B.press('.w-tasks .tk-input', 'Enter');
  await B.waitForSelector('#net:has-text("Offline")', { timeout: 5000 });
  assert.ok(await B.isVisible('.w-tasks .tk-row:has-text("Offline idea")'));
  assert.ok(await B.evaluate(() => JSON.parse(localStorage.getItem('wb:c:tasks')).items.some((t) => t.text === 'Offline idea')), 'kept in localStorage');
  await ctxB.setOffline(false);
  await B.evaluate(() => window.wallboard.api.flushQueue());
  await new Promise((r) => setTimeout(r, 800));
  assert.ok((await api('GET', '/api/c/tasks')).items.some((x) => x.text === 'Offline idea'));
});

await step('edit mode: add widget from palette, drag, resize, settings form, delete', async () => {
  await A.keyboard.press('e');
  await A.waitForSelector('#edit-bar');
  // Make room: delete the freshness widget.
  await A.click('.card[data-type="freshness"] .eo-delete');
  await A.click('.modal .btn.primary');
  await A.waitForTimeout(900);
  let home = (await api('GET', '/api/layout/default')).pages[0];
  assert.ok(!home.widgets.some((w) => w.type === 'freshness'), 'freshness removed');
  await A.click('#edit-bar .btn.primary:has-text("Widget")');
  await A.click('.palette-item:has(strong:text-is("Date"))');
  await A.waitForTimeout(900);
  home = (await api('GET', '/api/layout/default')).pages[0];
  const date = home.widgets.find((w) => w.type === 'date');
  assert.ok(date, 'date widget added');
  assert.deepEqual([date.x, date.y], [9, 3]);
  // Drag it one cell to the right is impossible (edge) — drag the tasks widget? Move date down 2 rows.
  const card = await A.$('.card[data-type="date"] .edit-overlay');
  const box = await card.boundingBox();
  const grid = await A.$eval('.page:not([inert]) .grid', (g) => { const r = g.getBoundingClientRect(); return { w: r.width / 12, h: r.height / 8 }; });
  await A.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await A.mouse.down();
  await A.mouse.move(box.x + box.width / 2, box.y + box.height / 2 + grid.h * 2, { steps: 10 });
  await A.mouse.up();
  // Resize: make it 1 column narrower is below min (2)? date min 2: shrink width 3 -> 2.
  const box2 = await (await A.$('.card[data-type="date"] .eo-resize')).boundingBox();
  await A.mouse.move(box2.x + 10, box2.y + 10);
  await A.mouse.down();
  await A.mouse.move(box2.x + 10 - grid.w, box2.y + 10, { steps: 10 });
  await A.mouse.up();
  await A.waitForTimeout(1000);
  const d2 = (await api('GET', '/api/layout/default')).pages[0].widgets.find((w) => w.type === 'date');
  assert.deepEqual([d2.x, d2.y, d2.w, d2.h], [9, 5, 2, 3]);
  // Settings form generated from the manifest.
  await A.click('.card[data-type="clock"] .eo-settings');
  await A.uncheck('.modal .field-check:has-text("Show seconds") input');
  await A.fill('.modal .field:has-text("Time zone") input', 'Not/AZone');
  await A.click('.modal button[type="submit"]');
  await A.waitForTimeout(900);
  const clock = (await api('GET', '/api/layout/default')).pages[0].widgets.find((w) => w.type === 'clock');
  assert.equal(clock.settings.showSeconds, false);
  assert.ok(await A.isVisible('.w-clock .widget-error:has-text("Unknown time zone")'));
});

await step('keyboard move/resize in edit mode (TV remote)', async () => {
  await A.focus('.card[data-type="date"] .edit-overlay');
  await A.keyboard.press('Enter'); // move mode
  await A.keyboard.press('ArrowLeft');
  await A.keyboard.press('Enter'); // resize mode
  await A.keyboard.press('ArrowDown'); // refused: already touches the bottom edge
  await A.keyboard.press('ArrowRight'); // allowed: the freshness widget's old spot is free
  await A.keyboard.press('Enter'); // done
  await A.waitForTimeout(1000);
  const d = (await api('GET', '/api/layout/default')).pages[0].widgets.find((w) => w.type === 'date');
  assert.deepEqual([d.x, d.y, d.w, d.h], [9, 5, 3, 3], 'move left refused (tasks widget), grow down refused (edge), grow right accepted');
});

await step('pages: add, rename, reorder, delete', async () => {
  await A.click('#edit-bar button[title="Add a page"]');
  await A.fill('#edit-bar .page-name', 'Kitchen');
  await A.press('#edit-bar .page-name', 'Enter');
  await A.waitForTimeout(900);
  let pages = (await api('GET', '/api/layout/default')).pages;
  assert.equal(pages[1].name, 'Kitchen');
  await A.click('#edit-bar button[title="Move page right"]');
  await A.waitForTimeout(900);
  pages = (await api('GET', '/api/layout/default')).pages;
  assert.equal(pages[2].name, 'Kitchen');
  await A.click('#edit-bar button[title="Delete this page"]');
  await A.waitForTimeout(900);
  pages = (await api('GET', '/api/layout/default')).pages;
  assert.ok(!pages.some((p) => p.name === 'Kitchen'), 'empty page deleted without confirmation');
});

await step('export and import a layout', async () => {
  const dl = A.waitForEvent('download');
  await A.click('#edit-bar button[title="Download this layout as a file"]');
  const file = await dl;
  const json = JSON.parse(await (await file.createReadStream()).toArray().then((c) => Buffer.concat(c).toString()));
  assert.equal(json.format, 'wallboard-layout');
  json.pages = [json.pages[0]];
  json.pages[0].name = 'Imported';
  await A.click('#edit-bar button[title="Load a layout from a file"]');
  await A.fill('.modal textarea', JSON.stringify(json));
  await A.click('.modal .btn.primary');
  await A.waitForTimeout(900);
  const pages = (await api('GET', '/api/layout/default')).pages;
  assert.deepEqual(pages.map((p) => p.name), ['Imported']);
  await A.click('#edit-bar button[title="Load a layout from a file"]');
  await A.fill('.modal textarea', '{"nope": 1}');
  await A.click('.modal .btn.primary');
  assert.ok(await A.isVisible('.modal .field-error:has-text("does not contain")'));
  await A.keyboard.press('Escape');
  await A.click('#edit-bar .done');
});

await step('the other screen picks up the layout change live', async () => {
  await B.waitForFunction(() => window.wallboard.getLayout().pages.length === 1 && window.wallboard.getLayout().pages[0].name === 'Imported', null, { timeout: 5000 });
});

await ctxA.close();
await ctxB.close();

await step('TV mode: large type, D-pad focus navigation, auto-rotate', async () => {
  // Restore a multi-page layout for this test.
  await api('PUT', '/api/layout/tv', { pages: layout.pages.slice(0, 3), force: true });
  const { context, page } = await open({ viewport: { width: 1920, height: 1080 }, userAgent: 'Mozilla/5.0 (Linux; Android 9; AFTMM) AppleWebKit/537.36 (KHTML, like Gecko) Silk/120 Safari/537.36' }, { profile: 'tv', rotateSeconds: 2 });
  assert.ok(await page.evaluate(() => document.documentElement.classList.contains('tv')), 'TV mode auto-detected from the Fire TV user agent');
  const fs = await page.evaluate(() => parseFloat(getComputedStyle(document.documentElement).fontSize));
  assert.ok(fs >= 21, `large base font on TV (${fs}px)`);
  await page.waitForFunction(() => window.wallboard.board.currentIndex() === 1, null, { timeout: 6000 });
  // D-pad: Down focuses something on the page, Right moves focus, Enter presses.
  await page.keyboard.press('ArrowDown');
  const f1 = await page.evaluate(() => document.activeElement.outerHTML.slice(0, 60));
  await page.keyboard.press('ArrowRight');
  const f2 = await page.evaluate(() => document.activeElement.outerHTML.slice(0, 60));
  assert.notEqual(f1, f2);
  const where = await page.evaluate(() => [document.activeElement.className, !!document.activeElement.closest('.page:not([inert]), #chrome, #dots')]);
  assert.ok(where[1], `focus stays on the visible page or controls (${where[0]})`);
  // While someone is navigating, rotation pauses.
  const before = await pageIndex(page);
  await page.waitForTimeout(2600);
  assert.equal(await pageIndex(page), before);
  await context.close();
});

await step('night dimming follows the schedule; a tap wakes the screen', async () => {
  const { context, page } = await open({}, { dimEnabled: true, dimStart: '00:00', dimEnd: '23:59', dimLevel: 0.8, wakeSeconds: 2 });
  await page.waitForTimeout(500);
  assert.equal(await page.$eval('#dim', (e) => getComputedStyle(e).pointerEvents), 'auto');
  assert.ok(await page.$eval('#dim', (e) => e.classList.contains('active')));
  await page.mouse.click(400, 400);
  assert.ok(!(await page.$eval('#dim', (e) => e.classList.contains('active'))), 'tap wakes');
  await page.waitForTimeout(2500);
  assert.ok(await page.$eval('#dim', (e) => e.classList.contains('active')), 'dims again');
  await page.keyboard.press('d'); // manual toggle off
  assert.ok(!(await page.$eval('#dim', (e) => e.classList.contains('active'))));
  await context.close();
});

await step('service worker: app opens and shows saved data with the server unreachable', async () => {
  const { context, page } = await open({ sw: true });
  await page.waitForFunction(() => navigator.serviceWorker.controller || new Promise((r) => navigator.serviceWorker.addEventListener('controllerchange', () => r(true))), null, { timeout: 10000 });
  await page.reload();
  await page.waitForSelector('.w-tasks .tk-row');
  await context.setOffline(true);
  await page.reload();
  await page.waitForSelector('.w-tasks .tk-row', { timeout: 10000 });
  await page.waitForSelector('.w-clock .clk-time');
  await page.waitForSelector('#net:has-text("Offline")', { state: 'attached', timeout: 10000 });
  const info = await page.evaluate(async () => (await import('/js/awake.js')).screenInfo().join(' | '));
  assert.match(info, /Wake Lock|video|waiting/);
  await context.close();
});

await browser.close();
await app.close();
await fx.close();
console.log(results.join('\n'));
if (errors.length) { console.log('page errors:\n  ' + errors.join('\n  ')); process.exitCode = 1; }
