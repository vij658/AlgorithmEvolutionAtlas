// TV mode: large type, D-pad / arrow-key spatial navigation, automatic page rotation.
import * as board from './board.js';
import { getPrefs, onPrefs, tvActive, rotateSeconds } from './prefs.js';
import { modalOpen } from './form.js';

const FOCUSABLE = 'button:not([disabled]), a[href], input:not([type=hidden]), select, textarea, [tabindex]:not([tabindex="-1"])';
let lastInput = 0;
let rotateTimer = null;

export function applyDisplayPrefs() {
  const p = getPrefs();
  const root = document.documentElement;
  root.classList.toggle('tv', tvActive());
  root.style.setProperty('--user-scale', String(Number(p.scale) || 1));
  root.style.setProperty('--safe-extra', `${Number(p.safeArea) || 0}px`);
}

function visible(elm) {
  if (elm.closest('[inert]') || elm.closest('[hidden]')) return false;
  const r = elm.getBoundingClientRect();
  return r.width > 0 && r.height > 0 && r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth;
}

function candidates() {
  const scope = document.querySelector('.modal-back:last-of-type .modal') || document;
  return [...scope.querySelectorAll(FOCUSABLE)].filter(visible);
}

/** Pick the nearest focusable element in a direction (simple spatial navigation). */
function nextInDirection(from, dir) {
  const a = from.getBoundingClientRect();
  const ax = a.left + a.width / 2, ay = a.top + a.height / 2;
  let best = null, bestScore = Infinity;
  for (const c of candidates()) {
    if (c === from || from.contains(c) && c !== from) continue;
    const b = c.getBoundingClientRect();
    const bx = b.left + b.width / 2, by = b.top + b.height / 2;
    let main, cross;
    if (dir === 'left') { main = a.left - b.right; cross = Math.abs(by - ay); if (bx >= ax - 1) continue; }
    else if (dir === 'right') { main = b.left - a.right; cross = Math.abs(by - ay); if (bx <= ax + 1) continue; }
    else if (dir === 'up') { main = a.top - b.bottom; cross = Math.abs(bx - ax); if (by >= ay - 1) continue; }
    else { main = b.top - a.bottom; cross = Math.abs(bx - ax); if (by <= ay + 1) continue; }
    const score = Math.max(0, main) + cross * 2 + (main < 0 ? 400 : 0);
    if (score < bestScore) { bestScore = score; best = c; }
  }
  return best;
}

function onKey(e) {
  lastInput = Date.now();
  const t = e.target;
  if (t.matches?.('input, textarea, select') && !['Escape'].includes(e.key)) {
    if (!(t.type === 'checkbox' || t.type === 'range') || !['ArrowUp', 'ArrowDown'].includes(e.key)) return;
  }
  const dir = { ArrowLeft: 'left', ArrowRight: 'right', ArrowUp: 'up', ArrowDown: 'down' }[e.key];
  if (!dir) return;
  if (e.defaultPrevented) return;
  const active = document.activeElement;
  const hasFocus = active && active !== document.body && visible(active);
  if (!hasFocus) {
    if (modalOpen()) { candidates()[0]?.focus(); e.preventDefault(); return; }
    // Nothing focused: left/right flips pages, up/down starts navigating the page.
    if (dir === 'left' && !board.isEditing()) { board.prev({ user: true }); e.preventDefault(); return; }
    if (dir === 'right' && !board.isEditing()) { board.next({ user: true }); e.preventDefault(); return; }
    const all = candidates();
    const first = all.find((c) => c.closest('.page, #edit-bar')) || all[0];
    first?.focus();
    e.preventDefault();
    return;
  }
  const target = nextInDirection(active, dir);
  e.preventDefault();
  if (target) { target.focus(); target.scrollIntoView?.({ block: 'nearest', inline: 'nearest' }); return; }
  if (!modalOpen() && !board.isEditing() && (dir === 'left' || dir === 'right')) {
    active.blur();
    if (dir === 'left') board.prev({ user: true }); else board.next({ user: true });
  }
}

function scheduleRotate() {
  clearInterval(rotateTimer);
  const s = rotateSeconds();
  if (!s) return;
  rotateTimer = setInterval(() => {
    // Pause while someone is using the screen, editing, or a dialog is open.
    if (board.isEditing() || modalOpen() || Date.now() - lastInput < 120_000) return;
    if (document.activeElement && document.activeElement !== document.body && document.activeElement.closest('.page')) return;
    board.next();
  }, s * 1000);
}

export function initTv() {
  applyDisplayPrefs();
  document.addEventListener('keydown', onKey);
  for (const ev of ['pointerdown', 'wheel', 'touchstart']) document.addEventListener(ev, () => { lastInput = Date.now(); }, { passive: true, capture: true });
  scheduleRotate();
  onPrefs(() => { applyDisplayPrefs(); scheduleRotate(); });
}
