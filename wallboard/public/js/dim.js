// Night dimming: a black overlay whose opacity follows a schedule. Tapping a dimmed
// screen brightens it for a while; the moon button toggles dimming manually.
import { el, hm, inWindow } from './lib/util.js';
import { getPrefs, onPrefs } from './prefs.js';

let overlay;
let manual = null; // null = follow schedule, true/false = forced until the next schedule edge
let lastScheduled = null;
let wakeUntil = 0;
const subs = new Set();

export function onDimChange(fn) { subs.add(fn); return () => subs.delete(fn); }

function scheduled() {
  const p = getPrefs();
  if (!p.dimEnabled) return false;
  const d = new Date();
  return inWindow(d.getHours() * 60 + d.getMinutes(), hm(p.dimStart), hm(p.dimEnd));
}

export function isDimmed() {
  const s = scheduled();
  if (lastScheduled !== null && s !== lastScheduled) manual = null; // schedule edge resets overrides
  lastScheduled = s;
  return (manual ?? s) && Date.now() >= wakeUntil;
}

function apply() {
  const dim = isDimmed();
  const level = Math.min(0.97, Math.max(0, Number(getPrefs().dimLevel) || 0.8));
  overlay.style.opacity = dim ? String(level) : '0';
  overlay.classList.toggle('active', dim);
  document.documentElement.classList.toggle('dimmed', dim);
  for (const fn of subs) fn(dim);
}

export function toggleDim() {
  manual = !(manual ?? scheduled());
  wakeUntil = 0;
  apply();
}

export function initDim() {
  overlay = el('div#dim', { 'aria-hidden': 'true' });
  document.body.append(overlay);
  // First tap on a dimmed screen only wakes it, it doesn't press what's underneath.
  overlay.addEventListener('pointerdown', (e) => {
    if (!overlay.classList.contains('active')) return;
    e.preventDefault();
    e.stopPropagation();
    wakeUntil = Date.now() + (Number(getPrefs().wakeSeconds) || 45) * 1000;
    apply();
    setTimeout(apply, wakeUntil - Date.now() + 50);
  });
  document.addEventListener('keydown', () => {
    if (overlay.classList.contains('active')) { wakeUntil = Date.now() + (Number(getPrefs().wakeSeconds) || 45) * 1000; apply(); setTimeout(apply, wakeUntil - Date.now() + 50); }
  }, true);
  setInterval(apply, 20_000);
  onPrefs(apply);
  apply();
}
