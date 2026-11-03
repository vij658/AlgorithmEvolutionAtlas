// Renders pages and widget grids, keeps widgets mounted across layout changes, and
// handles paging (swipe, keys, dots).
import { el, sameJson } from './lib/util.js';
import { COLS, ROWS, flowSpan, readingOrder } from './lib/grid.js';
import { mountWidget, getManifest } from './widgets.js';
import { mutate } from './layout.js';

const pages = new Map(); // pageId -> { el, grid }
const mounted = new Map(); // widgetId -> { card, body, handle, type, settingsKey, pageId }
const pageSubs = new Set();
let track, viewport, dots, pageLabel;
let order = []; // page ids in order
let index = 0;
let editing = false;
let editHooks = null;
let mode = { kind: 'wide', cols: COLS };

export const currentIndex = () => index;
export const pageCount = () => order.length;
export const currentPageId = () => order[index];
export const getMode = () => mode;
export const isEditing = () => editing;
export function onPageChange(fn) { pageSubs.add(fn); return () => pageSubs.delete(fn); }
export const gridOf = (pageId) => pages.get(pageId)?.grid;
export const cardOf = (widgetId) => mounted.get(widgetId)?.card;

export function initBoard(root) {
  viewport = el('div#viewport');
  track = el('div#track');
  viewport.append(el('div#drift', track));
  dots = el('nav#dots', { 'aria-label': 'Pages' });
  pageLabel = el('div#page-label', { 'aria-hidden': 'true' });
  root.append(viewport, dots, pageLabel);
  setupSwipe();
  computeMode();
  addEventListener('resize', () => { if (computeMode()) relayout(); });
  return { viewport, track };
}

function computeMode() {
  const W = innerWidth, H = innerHeight;
  let next;
  if (W >= 760 && H >= 500 && W >= H * 1.05) next = { kind: 'wide', cols: COLS };
  else if (W >= 600) next = { kind: 'flow', cols: 6 };
  else next = { kind: 'flow', cols: 1 };
  const changed = next.kind !== mode.kind || next.cols !== mode.cols;
  mode = next;
  document.documentElement.dataset.mode = mode.kind;
  document.documentElement.dataset.cols = String(mode.cols);
  return changed;
}

let lastLayout = null;
function relayout() { if (lastLayout) render(lastLayout); }

/** Render `layout` (from layout.js), reusing mounted widgets whose type/settings match. */
export function render(layout) {
  lastLayout = layout;
  const seenPages = new Set();
  const seenWidgets = new Set();
  order = layout.pages.map((p) => p.id);
  layout.pages.forEach((page, pi) => {
    seenPages.add(page.id);
    let pg = pages.get(page.id);
    if (!pg) {
      const grid = el('div.grid');
      pg = { el: el('section.page', { dataset: { id: page.id } }, grid), grid };
      pages.set(page.id, pg);
    }
    pg.el.setAttribute('aria-label', page.name);
    pg.el.dataset.name = page.name;
    if (track.children[pi] !== pg.el) track.insertBefore(pg.el, track.children[pi] || null);
    pg.grid.classList.toggle('empty', page.widgets.length === 0);
    const flowOrder = new Map(readingOrder(page.widgets).map((w, i) => [w.id, i]));
    for (const w of page.widgets) {
      seenWidgets.add(w.id);
      const settingsKey = JSON.stringify(w.settings || {});
      let m = mounted.get(w.id);
      if (m && (m.type !== w.type || m.settingsKey !== settingsKey)) {
        m.handle?.unmount();
        m.card.remove();
        mounted.delete(w.id);
        m = null;
      }
      if (!m) m = createCard(w, page.id, settingsKey);
      if (m.card.parentNode !== pg.grid) pg.grid.append(m.card);
      m.pageId = page.id;
      m.widget = w;
      place(m.card, w, flowOrder.get(w.id));
      decorate(m, w, page);
    }
    if (!page.widgets.length && editing && !pg.grid.querySelector('.empty-hint')) {
      pg.grid.append(el('div.empty-hint', 'Empty page — tap “＋ Widget” to add something.'));
    }
    if (page.widgets.length || !editing) pg.grid.querySelector('.empty-hint')?.remove();
  });
  for (const [id, m] of mounted) {
    if (!seenWidgets.has(id)) { m.handle?.unmount(); m.card.remove(); mounted.delete(id); }
  }
  for (const [id, pg] of pages) if (!seenPages.has(id)) { pg.el.remove(); pages.delete(id); }
  if (index >= order.length) index = order.length - 1;
  renderDots(layout);
  applyTransform(true);
}

function createCard(w, pageId, settingsKey) {
  const body = el('div.widget-body');
  const card = el('article.card', { dataset: { id: w.id, type: w.type } }, body);
  const m = { card, body, handle: null, type: w.type, settingsKey, pageId, widget: w };
  mounted.set(w.id, m);
  mountWidget(body, w, {
    saveSettings(patch) {
      // Widget-initiated settings changes (e.g. remembered state) must not remount it.
      mutate((ps) => {
        for (const p of ps) for (const x of p.widgets) if (x.id === w.id) {
          x.settings = { ...x.settings, ...patch };
          m.settingsKey = JSON.stringify(x.settings);
        }
      });
    },
    isVisible: () => order[index] === m.pageId && document.visibilityState === 'visible',
    onVisible(fn) {
      return onPageChange(() => { if (order[index] === m.pageId) fn(); });
    },
  }).then((h) => {
    if (mounted.get(w.id) === m) m.handle = h; else h.unmount();
  });
  return m;
}

function place(card, w, flowIdx) {
  if (mode.kind === 'wide') {
    card.style.gridColumn = `${w.x + 1} / span ${w.w}`;
    card.style.gridRow = `${w.y + 1} / span ${w.h}`;
    card.style.order = '';
  } else {
    card.style.gridColumn = `span ${flowSpan(w.w, mode.cols)}`;
    const manifest = getManifest(w.type);
    const h = mode.cols === 1 ? Math.max(w.h, manifest?.size?.phoneH ?? 0) : w.h;
    card.style.gridRow = `span ${h}`;
    card.style.order = String(flowIdx ?? 0);
  }
}

function decorate(m, w, page) {
  const existing = m.card.querySelector(':scope > .edit-overlay');
  if (!editing) { existing?.remove(); m.card.classList.remove('editable'); m.card.removeAttribute('tabindex'); return; }
  m.card.classList.add('editable');
  const manifest = getManifest(w.type);
  if (existing) { existing.querySelector('.eo-name').textContent = manifest?.name || w.type; return; }
  const overlay = el('div.edit-overlay', { tabindex: '0', 'aria-label': `${manifest?.name || w.type} widget. Enter to move or resize.` },
    el('div.eo-bar',
      el('span.eo-name', manifest?.name || w.type),
      el('span.eo-mode'),
      el('button.eo-btn.eo-settings', { type: 'button', title: 'Settings', 'aria-label': 'Widget settings', onclick: (e) => { e.stopPropagation(); editHooks?.settings(m.widget); } }, '⚙'),
      el('button.eo-btn.eo-delete', { type: 'button', title: 'Remove', 'aria-label': 'Remove widget', onclick: (e) => { e.stopPropagation(); editHooks?.remove(m.widget); } }, '✕'),
    ),
    el('div.eo-resize', { title: 'Drag to resize', 'aria-hidden': 'true' }),
  );
  overlay.addEventListener('pointerdown', (e) => editHooks?.pointerdown(e, m.widget, m.card));
  overlay.addEventListener('keydown', (e) => editHooks?.keydown(e, m.widget, m.card));
  m.card.append(overlay);
}

export function setEditing(on, hooks) {
  editing = on;
  editHooks = hooks || editHooks;
  document.documentElement.classList.toggle('editing', on);
  relayout();
}

function renderDots(layout) {
  dots.replaceChildren(...layout.pages.map((p, i) => el('button.dot', {
    type: 'button',
    'aria-label': `Page ${i + 1}: ${p.name}`,
    'aria-current': i === index ? 'page' : null,
    title: p.name,
    onclick: () => goTo(i, { user: true }),
  })));
  dots.hidden = layout.pages.length < 2;
}

function applyTransform(instant = false) {
  if (!track) return;
  if (instant) track.style.transition = 'none';
  track.style.transform = `translate3d(${-index * 100}%,0,0)`;
  if (instant) { void track.offsetWidth; track.style.transition = ''; }
  [...dots.children].forEach((d, i) => d.setAttribute('aria-current', i === index ? 'page' : 'false'));
  [...track.children].forEach((p, i) => { p.inert = i !== index; p.setAttribute('aria-hidden', i !== index ? 'true' : 'false'); });
}

let labelTimer;
export function goTo(i, { user = false, instant = false } = {}) {
  if (!order.length) return;
  const n = order.length;
  const next = ((i % n) + n) % n;
  const changed = next !== index;
  index = next;
  applyTransform(instant);
  if (changed) {
    const name = pages.get(order[index])?.el.dataset.name || '';
    pageLabel.textContent = name;
    pageLabel.classList.add('show');
    clearTimeout(labelTimer);
    labelTimer = setTimeout(() => pageLabel.classList.remove('show'), 1600);
    for (const fn of pageSubs) fn({ index, pageId: order[index], user });
  }
}
export const next = (o) => goTo(index + 1, o);
export const prev = (o) => goTo(index - 1, o);

// ---- swipe ----------------------------------------------------------------------
function setupSwipe() {
  let start = null;
  let swiped = false;
  const NOSWIPE = 'input, textarea, select, [contenteditable], .no-swipe, .edit-overlay, .modal';
  viewport.addEventListener('pointerdown', (e) => {
    if (editing || order.length < 2 || e.button > 0 || e.target.closest(NOSWIPE)) return;
    start = { x: e.clientX, y: e.clientY, t: performance.now(), id: e.pointerId, active: false };
    swiped = false;
  });
  viewport.addEventListener('pointermove', (e) => {
    if (!start || e.pointerId !== start.id) return;
    const dx = e.clientX - start.x, dy = e.clientY - start.y;
    if (!start.active) {
      if (Math.abs(dx) > 12 && Math.abs(dx) > Math.abs(dy) * 1.2) {
        start.active = true;
        track.style.transition = 'none';
        try { viewport.setPointerCapture(e.pointerId); } catch { /* ignore */ }
      } else if (Math.abs(dy) > 16) { start = null; return; }
      else return;
    }
    const w = viewport.clientWidth;
    let off = dx;
    if ((index === 0 && dx > 0) || (index === order.length - 1 && dx < 0)) off = dx / 3; // rubber band at the ends
    track.style.transform = `translate3d(calc(${-index * 100}% + ${off}px),0,0)`;
    if (Math.abs(dx) > w) start.x = e.clientX - Math.sign(dx) * w;
  });
  const end = (e) => {
    if (!start || e.pointerId !== start.id) return;
    const s = start;
    start = null;
    track.style.transition = '';
    if (!s.active) return;
    swiped = true;
    const dx = e.clientX - s.x;
    const v = dx / Math.max(1, performance.now() - s.t);
    const w = viewport.clientWidth;
    if ((dx < -w * 0.18 || v < -0.45) && index < order.length - 1) goTo(index + 1, { user: true });
    else if ((dx > w * 0.18 || v > 0.45) && index > 0) goTo(index - 1, { user: true });
    else applyTransform();
  };
  viewport.addEventListener('pointerup', end);
  viewport.addEventListener('pointercancel', (e) => { if (start && e.pointerId === start.id) { start = null; track.style.transition = ''; applyTransform(); } });
  // A swipe must not also click whatever was under the finger.
  viewport.addEventListener('click', (e) => { if (swiped) { e.stopPropagation(); e.preventDefault(); swiped = false; } }, true);
  let wheelLock = 0;
  viewport.addEventListener('wheel', (e) => {
    if (editing || Math.abs(e.deltaX) < 30 || Math.abs(e.deltaX) < Math.abs(e.deltaY) * 1.5) return;
    const t = performance.now();
    if (t < wheelLock) return;
    wheelLock = t + 700;
    if (e.deltaX > 0) next({ user: true }); else prev({ user: true });
  }, { passive: true });
}
