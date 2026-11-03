// Boot: wire up board, layout sync, screen care (dim / awake / drift), TV mode and
// edit mode.
import { el, storage, toast } from './lib/util.js';
import * as api from './api.js';
import * as board from './board.js';
import { loadLayout, onLayout, getLayout } from './layout.js';
import { loadRegistry } from './widgets.js';
import { initDim, toggleDim, onDimChange } from './dim.js';
import { initAwake } from './awake.js';
import { initDrift } from './drift.js';
import { initTv } from './tv.js';
import { toggleEdit, exitEdit, enterEdit, isEditing, openDeviceSettings } from './edit.js';
import { modalOpen } from './form.js';
import { getPrefs } from './prefs.js';

const app = document.getElementById('app');

function registerServiceWorker() {
  if (!('serviceWorker' in navigator) || !window.isSecureContext) return;
  navigator.serviceWorker.register('/sw.js').then((reg) => {
    // Check for a new version every few hours; screens run for weeks.
    setInterval(() => reg.update().catch(() => {}), 3 * 3_600_000);
  }).catch((e) => console.warn('[wallboard] service worker failed', e));
  let reloading = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (reloading || !navigator.serviceWorker.controller) return;
    reloading = true;
    const reload = () => (isEditing() || modalOpen() ? setTimeout(reload, 30_000) : location.reload());
    setTimeout(reload, 1000);
  });
}

function buildChrome() {
  const fs = document.fullscreenEnabled || document.webkitFullscreenEnabled;
  const toggleFs = () => {
    if (document.fullscreenElement || document.webkitFullscreenElement) (document.exitFullscreen || document.webkitExitFullscreen).call(document);
    else (document.documentElement.requestFullscreen || document.documentElement.webkitRequestFullscreen)?.call(document.documentElement).catch?.(() => {});
  };
  const dimBtn = el('button.chrome-btn', { type: 'button', title: 'Dim screen (D)', 'aria-label': 'Toggle dimming', onclick: toggleDim }, '☾');
  onDimChange((d) => { dimBtn.textContent = d ? '☀' : '☾'; });
  const chrome = el('div#chrome', { role: 'toolbar', 'aria-label': 'Screen controls' },
    el('span#net', { title: '' }),
    el('button.chrome-btn', { type: 'button', title: 'Edit layout (E)', 'aria-label': 'Edit layout', onclick: toggleEdit }, '✎'),
    dimBtn,
    el('button.chrome-btn', { type: 'button', title: 'This screen’s settings', 'aria-label': 'Screen settings', onclick: openDeviceSettings }, '⚙'),
    fs ? el('button.chrome-btn', { type: 'button', title: 'Full screen (F)', 'aria-label': 'Full screen', onclick: toggleFs }, '⛶') : null,
  );
  app.append(chrome);

  // Auto-hide controls; any interaction shows them again.
  let hideTimer;
  const show = () => {
    document.documentElement.classList.remove('chrome-hidden');
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => { if (!chrome.contains(document.activeElement)) document.documentElement.classList.add('chrome-hidden'); }, 5000);
  };
  for (const ev of ['pointermove', 'pointerdown', 'keydown', 'focusin']) document.addEventListener(ev, show, { passive: true });
  show();

  const net = chrome.querySelector('#net');
  const updateNet = () => {
    const off = !api.isOnline();
    const pending = api.pendingWrites();
    net.textContent = off ? (pending ? `Offline · ${pending} unsaved` : 'Offline') : pending ? 'Saving…' : '';
    net.title = off ? 'Server unreachable. Showing saved data; changes are kept and sent when it is back.' : '';
    net.hidden = !net.textContent;
    document.documentElement.classList.toggle('offline', off);
  };
  api.on('connection', updateNet);
  api.on('queue', updateNet);
  setInterval(updateNet, 5000);
  updateNet();
  return { toggleFs };
}

function setupKeys({ toggleFs }) {
  document.addEventListener('keydown', (e) => {
    if (e.target.matches?.('input, textarea, select') || e.ctrlKey || e.metaKey || e.altKey) return;
    if (modalOpen()) return;
    const k = e.key;
    if (k === 'e' || k === 'E') { toggleEdit(); e.preventDefault(); }
    else if (k === 'Escape' && isEditing()) { exitEdit(); e.preventDefault(); }
    else if (k === 'd' || k === 'D') toggleDim();
    else if (k === 'f' || k === 'F') toggleFs();
    else if (k === 'PageDown' || k === 'MediaTrackNext' || k === 'MediaFastForward') { board.next({ user: true }); e.preventDefault(); }
    else if (k === 'PageUp' || k === 'MediaTrackPrevious' || k === 'MediaRewind') { board.prev({ user: true }); e.preventDefault(); }
    else if (k === 'ContextMenu' || k === 'Menu') { toggleEdit(); e.preventDefault(); }
  });
}

function setupLongPress(viewport) {
  // Long-press anywhere on the board (not on a control) enters edit mode.
  let t = null, sx = 0, sy = 0;
  viewport.addEventListener('pointerdown', (e) => {
    if (isEditing() || e.target.closest('button, a, input, textarea, select, .no-longpress')) return;
    sx = e.clientX; sy = e.clientY;
    clearTimeout(t);
    t = setTimeout(() => { t = null; enterEdit(); navigator.vibrate?.(20); }, 900);
  });
  const cancel = () => { clearTimeout(t); t = null; };
  viewport.addEventListener('pointermove', (e) => { if (t && Math.hypot(e.clientX - sx, e.clientY - sy) > 10) cancel(); });
  viewport.addEventListener('pointerup', cancel);
  viewport.addEventListener('pointercancel', cancel);
  viewport.addEventListener('contextmenu', (e) => { if (!e.target.closest('a, input, textarea')) e.preventDefault(); });
}

function nightlyReload() {
  // Pages that run for weeks accumulate cruft; reload once a night when nobody's looking.
  const target = new Date();
  target.setHours(3, 40 + Math.floor(Math.random() * 15), 0, 0);
  if (target <= new Date()) target.setDate(target.getDate() + 1);
  setTimeout(function tryReload() {
    if (isEditing() || modalOpen() || !api.isOnline()) { setTimeout(tryReload, 10 * 60_000); return; }
    location.reload();
  }, target - new Date());
}

async function boot() {
  registerServiceWorker();
  initTv();
  const { viewport } = board.initBoard(app);
  initDrift(document.getElementById('drift'));
  initDim();
  initAwake();
  const chrome = buildChrome();
  setupKeys(chrome);
  setupLongPress(viewport);

  const pageKey = () => `wb:page:${getPrefs().profile}`;
  board.onPageChange(({ index }) => storage.set(pageKey(), index));

  await loadRegistry();
  onLayout((layout, reason) => {
    board.render(layout);
    if (reason === 'load') board.goTo(Math.min(storage.get(pageKey(), 0) || 0, layout.pages.length - 1), { instant: true });
  });
  await loadLayout();
  api.connectEvents();
  api.on('layout-error', (e) => toast(`Layout not saved: ${e.message}`, 6000));
  api.on('sse', (e) => { if (e.connected) api.flushQueue(); });
  api.flushQueue();
  nightlyReload();
  document.documentElement.classList.add('ready');
  window.wallboard = { board, getLayout, api }; // handy for debugging from the console
}

boot().catch((err) => {
  console.error(err);
  app.replaceChildren(el('div.fatal', el('h1', 'Wallboard could not start'), el('pre', String(err?.stack || err))));
});
