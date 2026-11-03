// Burn-in protection: the whole board drifts a few pixels along a slow Lissajous path,
// so static elements (clock digits, card edges) never sit on exactly the same pixels.
import { getPrefs, onPrefs } from './prefs.js';

const STEP_MS = 90_000;

export function initDrift(target) {
  const tick = () => {
    const p = getPrefs();
    if (!p.drift) { target.style.transform = ''; document.documentElement.style.setProperty('--drift-pad', '0px'); return; }
    const a = Number(p.driftPx) || 10;
    document.documentElement.style.setProperty('--drift-pad', `${a}px`);
    const t = Date.now() / 3_600_000; // hours
    const x = Math.round(Math.sin(t * 2 * Math.PI * 1.3) * a);
    const y = Math.round(Math.sin(t * 2 * Math.PI * 0.9 + 1) * a * 0.7);
    target.style.setProperty('--drift-x', `${x}px`);
    target.style.setProperty('--drift-y', `${y}px`);
    target.style.transform = 'translate(var(--drift-x), var(--drift-y))';
  };
  target.style.transition = 'none';
  tick();
  void target.offsetWidth;
  target.style.transition = '';
  setInterval(tick, STEP_MS);
  onPrefs(tick);
}
