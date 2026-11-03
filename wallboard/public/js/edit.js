// Edit mode: widget palette, drag / resize, manifest-driven settings, page management,
// layout export / import and the per-screen settings dialog.
import { el, toast } from './lib/util.js';
import { COLS, ROWS, fits, placeWidget, clamp } from './lib/grid.js';
import * as board from './board.js';
import { getLayout, mutate, newPage, exportLayout, parseImport, replacePages, holdRemoteChanges, resetToDefault, loadLayout } from './layout.js';
import { allManifests, getManifest } from './widgets.js';
import { modal, settingsDialog, confirmDialog } from './form.js';
import { getPrefs, setPrefs, PREF_FIELDS } from './prefs.js';
import { uid } from './lib/util.js';
import { screenInfo } from './awake.js';

let bar = null;
let offPage = null;
let barObserver = null;
const kbMode = new Map(); // widgetId -> 'move' | 'resize'

const currentPage = () => getLayout().pages.find((p) => p.id === board.currentPageId());

export function isEditing() { return board.isEditing(); }

export function enterEdit() {
  if (board.isEditing()) return;
  holdRemoteChanges(true);
  board.setEditing(true, hooks);
  bar = buildBar();
  document.body.append(bar);
  // Push the board down so the toolbar never covers widgets.
  barObserver = new ResizeObserver(() => document.documentElement.style.setProperty('--bar-h', `${bar ? bar.offsetHeight + 8 : 0}px`));
  barObserver.observe(bar);
  updateBar();
  offPage = board.onPageChange(updateBar);
  if (board.getMode().kind !== 'wide') toast('Tip: drag & resize work in the landscape layout. Here you can add, configure and remove widgets.', 6000);
  bar.querySelector('button')?.focus();
}

export function exitEdit() {
  if (!board.isEditing()) return;
  kbMode.clear();
  board.setEditing(false);
  bar?.remove();
  bar = null;
  offPage?.();
  barObserver?.disconnect();
  document.documentElement.style.setProperty('--bar-h', '0px');
  holdRemoteChanges(false);
}

export function toggleEdit() { if (board.isEditing()) exitEdit(); else enterEdit(); }

function buildBar() {
  const nameInput = el('input.page-name', { type: 'text', maxlength: 60, 'aria-label': 'Page name', onchange: () => {
    const id = board.currentPageId();
    const v = nameInput.value.trim() || 'Page';
    mutate((ps) => { ps.find((p) => p.id === id).name = v; });
  } });
  const b = (label, title, onclick, cls = '') => el('button.btn', { type: 'button', title, 'aria-label': title, onclick, class: cls }, label);
  return el('div#edit-bar', { role: 'toolbar', 'aria-label': 'Edit layout' },
    b('＋ Widget', 'Add a widget to this page', openPalette, 'primary'),
    el('span.bar-group', el('span.bar-label', 'Page'), nameInput,
      b('◀', 'Move page left', () => movePage(-1)),
      b('▶', 'Move page right', () => movePage(1)),
      b('＋ Page', 'Add a page', addPage),
      b('🗑', 'Delete this page', deletePage, 'danger')),
    el('span.bar-group',
      b('Export', 'Download this layout as a file', doExport),
      b('Import', 'Load a layout from a file', doImport),
      b('This screen', 'Settings for this screen only', openDeviceSettings)),
    b('✓ Done', 'Leave edit mode', exitEdit, 'primary done'),
  );
}

function updateBar() {
  if (!bar) return;
  const p = currentPage();
  const input = bar.querySelector('.page-name');
  if (p && document.activeElement !== input) input.value = p.name;
}

// ---- pages ------------------------------------------------------------------------
function addPage() {
  const page = newPage(`Page ${getLayout().pages.length + 1}`);
  const at = board.currentIndex() + 1;
  mutate((ps) => { ps.splice(at, 0, page); }, { immediate: true });
  board.goTo(at, { user: true });
  updateBar();
  bar.querySelector('.page-name').select();
}

async function deletePage() {
  const ps = getLayout().pages;
  if (ps.length < 2) { toast('A layout needs at least one page.'); return; }
  const p = currentPage();
  if (p.widgets.length && !(await confirmDialog(`Delete page “${p.name}” and its ${p.widgets.length} widget(s)?`, { ok: 'Delete page', danger: true }))) return;
  const i = board.currentIndex();
  mutate((pages) => pages.filter((x) => x.id !== p.id), { immediate: true });
  board.goTo(Math.max(0, i - 1));
  updateBar();
}

function movePage(dir) {
  const i = board.currentIndex();
  const j = i + dir;
  if (j < 0 || j >= getLayout().pages.length) return;
  mutate((ps) => { const [p] = ps.splice(i, 1); ps.splice(j, 0, p); }, { immediate: true });
  board.goTo(j, { instant: true });
}

// ---- widgets ------------------------------------------------------------------------
function openPalette() {
  const page = currentPage();
  modal('Add a widget', (close) => el('div.palette', allManifests().map((m) => el('button.palette-item', {
    type: 'button',
    onclick: () => close(m),
  }, el('span.pi-icon', m.icon || '▦'), el('span.pi-text', el('strong', m.name || m.id), el('span', m.description || ''))))), { wide: true })
    .then((m) => {
      if (!m) return;
      const spot = placeWidget(page.widgets, m.size || {});
      if (!spot) { toast('No room on this page. Shrink or remove a widget, or add a page.'); return; }
      const w = { id: uid(m.id), type: m.id, ...spot, settings: {} };
      mutate((ps) => { ps.find((p) => p.id === page.id).widgets.push(w); }, { immediate: true });
      if (m.configureOnAdd) setTimeout(() => openSettings(w), 50);
    });
}

async function openSettings(widget) {
  const m = getManifest(widget.type);
  const values = await settingsDialog(`${m?.name || widget.type} settings`, m?.settings || [], widget.settings || {});
  if (!values) return;
  mutate((ps) => {
    for (const p of ps) for (const w of p.widgets) if (w.id === widget.id) w.settings = { ...w.settings, ...values };
  }, { immediate: true });
}

async function removeWidget(widget) {
  const m = getManifest(widget.type);
  if (!(await confirmDialog(`Remove the ${m?.name || widget.type} widget?`, { ok: 'Remove', danger: true }))) return;
  mutate((ps) => { for (const p of ps) p.widgets = p.widgets.filter((w) => w.id !== widget.id); }, { immediate: true });
}

function limits(type) {
  const s = getManifest(type)?.size || {};
  return { minW: s.minW ?? 1, minH: s.minH ?? 1, maxW: s.maxW ?? COLS, maxH: s.maxH ?? ROWS };
}

function pageOfWidget(id) { return getLayout().pages.find((p) => p.widgets.some((w) => w.id === id)); }

function commitRect(widget, rect) {
  const page = pageOfWidget(widget.id);
  if (!page || !fits(rect, page.widgets, widget.id)) return false;
  mutate((ps) => {
    const w = ps.find((p) => p.id === page.id).widgets.find((x) => x.id === widget.id);
    Object.assign(w, rect);
  });
  return true;
}

function onPointerDown(e, widget, card) {
  if (e.target.closest('button') || e.button > 0) return;
  if (board.getMode().kind !== 'wide') return;
  e.preventDefault();
  const kind = e.target.closest('.eo-resize') ? 'resize' : 'move';
  const page = pageOfWidget(widget.id);
  const grid = board.gridOf(page.id);
  const g = grid.getBoundingClientRect();
  const cw = g.width / COLS, ch = g.height / ROWS;
  const lim = limits(widget.type);
  const start = { x: e.clientX, y: e.clientY };
  const orig = { x: widget.x, y: widget.y, w: widget.w, h: widget.h };
  let rect = { ...orig };
  const ghost = el('div.ghost');
  ghost.style.gridColumn = `${orig.x + 1} / span ${orig.w}`;
  ghost.style.gridRow = `${orig.y + 1} / span ${orig.h}`;
  grid.append(ghost);
  card.classList.add('dragging', kind);
  const cardBox = card.getBoundingClientRect();
  try { e.target.setPointerCapture(e.pointerId); } catch { /* ignore */ }
  const move = (ev) => {
    const dx = ev.clientX - start.x, dy = ev.clientY - start.y;
    if (kind === 'move') {
      card.style.transform = `translate(${dx}px, ${dy}px)`;
      rect = { ...orig, x: clamp(orig.x + Math.round(dx / cw), 0, COLS - orig.w), y: clamp(orig.y + Math.round(dy / ch), 0, ROWS - orig.h) };
    } else {
      card.style.width = `${Math.max(cw * lim.minW, cardBox.width + dx)}px`;
      card.style.height = `${Math.max(ch * lim.minH, cardBox.height + dy)}px`;
      rect = { ...orig, w: clamp(orig.w + Math.round(dx / cw), lim.minW, Math.min(lim.maxW, COLS - orig.x)), h: clamp(orig.h + Math.round(dy / ch), lim.minH, Math.min(lim.maxH, ROWS - orig.y)) };
    }
    ghost.style.gridColumn = `${rect.x + 1} / span ${rect.w}`;
    ghost.style.gridRow = `${rect.y + 1} / span ${rect.h}`;
    ghost.classList.toggle('invalid', !fits(rect, page.widgets, widget.id));
  };
  const up = () => {
    window.removeEventListener('pointermove', move);
    window.removeEventListener('pointerup', up);
    window.removeEventListener('pointercancel', up);
    ghost.remove();
    card.classList.remove('dragging', kind);
    card.style.transform = card.style.width = card.style.height = '';
    const changed = rect.x !== orig.x || rect.y !== orig.y || rect.w !== orig.w || rect.h !== orig.h;
    if (changed && !commitRect(widget, rect)) toast('That spot is taken.');
  };
  window.addEventListener('pointermove', move);
  window.addEventListener('pointerup', up);
  window.addEventListener('pointercancel', up);
}

function onKeyDown(e, widget, card) {
  const label = card.querySelector('.eo-mode');
  const setMode = (m) => {
    if (m) kbMode.set(widget.id, m); else kbMode.delete(widget.id);
    label.textContent = m === 'move' ? 'Moving — arrows, Enter for resize' : m === 'resize' ? 'Resizing — arrows, Enter when done' : '';
    card.classList.toggle('kb-active', !!m);
  };
  const mode = kbMode.get(widget.id);
  if (e.key === 'Enter' || e.key === ' ') {
    if (e.target !== e.currentTarget) return; // a button inside the overlay
    e.preventDefault();
    if (board.getMode().kind !== 'wide') { openSettings(widget); return; }
    setMode(mode === undefined ? 'move' : mode === 'move' ? 'resize' : null);
    return;
  }
  if (e.key === 'Escape' && mode) { e.preventDefault(); e.stopPropagation(); setMode(null); return; }
  const d = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] }[e.key];
  if (!d || !mode) return;
  e.preventDefault();
  e.stopPropagation();
  const cur = pageOfWidget(widget.id).widgets.find((w) => w.id === widget.id);
  const lim = limits(widget.type);
  const r = mode === 'move'
    ? { x: cur.x + d[0], y: cur.y + d[1], w: cur.w, h: cur.h }
    : { x: cur.x, y: cur.y, w: clamp(cur.w + d[0], lim.minW, lim.maxW), h: clamp(cur.h + d[1], lim.minH, lim.maxH) };
  if (!commitRect(widget, r)) card.animate?.([{ transform: `translate(${d[0] * 6}px, ${d[1] * 6}px)` }, { transform: 'none' }], 160);
}

const hooks = { settings: openSettings, remove: removeWidget, pointerdown: onPointerDown, keydown: onKeyDown };

// ---- export / import --------------------------------------------------------------
function doExport() {
  const data = exportLayout();
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const a = el('a', { href: URL.createObjectURL(blob), download: `wallboard-${data.profile}-${data.exportedAt.slice(0, 10)}.json` });
  document.body.append(a);
  a.click();
  setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
  toast('Layout exported.');
}

function doImport() {
  modal('Import layout', (close) => {
    const area = el('textarea', { rows: 8, placeholder: 'Paste exported layout JSON here, or choose a file.', spellcheck: false });
    const file = el('input', { type: 'file', accept: 'application/json,.json', onchange: async () => { if (file.files[0]) area.value = await file.files[0].text(); } });
    const err = el('div.field-error');
    return el('div.import',
      el('p.field-help', 'Importing replaces every page of this profile (“' + getPrefs().profile + '”). Export first if you want a backup.'),
      file, area, err,
      el('div.form-actions',
        el('button.btn', { type: 'button', onclick: () => close() }, 'Cancel'),
        el('button.btn.primary', { type: 'button', onclick: () => {
          try { close(parseImport(area.value)); } catch (e) { err.textContent = e instanceof SyntaxError ? 'That is not valid JSON.' : e.message; }
        } }, 'Replace layout')));
  }, { wide: true }).then((pages) => {
    if (!pages) return;
    replacePages(pages);
    board.goTo(0, { instant: true });
    updateBar();
    toast(`Imported ${pages.length} page(s).`);
  });
}

export async function openDeviceSettings() {
  const before = getPrefs();
  const info = screenInfo();
  const extra = el('div.device-info',
    el('h3.field-heading', 'About this screen'),
    el('ul', info.map((line) => el('li', line))),
    el('button.btn.small.danger', { type: 'button', onclick: async (e) => {
      const cancel = e.currentTarget.closest('.modal').querySelector('.form-actions .btn');
      if (!(await confirmDialog(`Reset profile “${before.profile}” to the starter layout? This affects every screen using it.`, { ok: 'Reset', danger: true }))) return;
      cancel.click();
      await resetToDefault();
      board.goTo(0, { instant: true });
      toast('Layout reset.');
    } }, 'Reset layout to starter pages'));
  const values = await settingsDialog('This screen', PREF_FIELDS, before, { extra });
  if (!values) return;
  setPrefs(values);
  if (values.profile !== before.profile) {
    await loadLayout();
    board.goTo(0, { instant: true });
    toast(`Showing profile “${values.profile}”.`);
  }
}
