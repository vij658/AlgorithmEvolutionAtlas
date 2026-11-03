// Per-device preferences (kept in this browser only): which layout profile to show,
// TV mode, night dimming, burn-in drift, page rotation and so on.
import { storage } from './lib/util.js';

const KEY = 'wb:prefs';

// Doubles as the manifest for the "This screen" settings form.
export const PREF_FIELDS = [
  { key: 'profile', type: 'text', label: 'Layout profile', default: 'default', pattern: '^[a-z0-9][a-z0-9_-]{0,39}$',
    help: 'Screens with the same profile share one layout. Use e.g. "tv" for a different TV layout.' },
  { key: 'tvMode', type: 'select', label: 'TV mode', default: 'auto', options: [
    { value: 'auto', label: 'Auto-detect' }, { value: 'on', label: 'On' }, { value: 'off', label: 'Off' }],
    help: 'Large type, arrow-key navigation, page rotation. Auto turns on for Fire TV / smart-TV browsers or ?tv=1.' },
  { key: 'rotateSeconds', type: 'number', label: 'Auto-rotate pages every (seconds, 0 = off, blank = TV default 45)', min: 0, max: 3600, default: null },
  { key: 'scale', type: 'range', label: 'Text size', min: 0.7, max: 1.8, step: 0.05, default: 1 },
  { key: 'dimEnabled', type: 'boolean', label: 'Dim at night', default: true },
  { key: 'dimStart', type: 'time', label: 'Night starts', default: '22:30' },
  { key: 'dimEnd', type: 'time', label: 'Night ends', default: '06:30' },
  { key: 'dimLevel', type: 'range', label: 'Night dimming strength', min: 0.3, max: 0.97, step: 0.01, default: 0.82 },
  { key: 'wakeSeconds', type: 'number', label: 'Tap wakes the screen for (seconds)', min: 5, max: 600, default: 45 },
  { key: 'keepAwake', type: 'boolean', label: 'Keep the screen awake', default: true },
  { key: 'drift', type: 'boolean', label: 'Burn-in protection (slow layout drift)', default: true },
  { key: 'driftPx', type: 'number', label: 'Drift distance (px)', min: 2, max: 40, default: 10 },
  { key: 'safeArea', type: 'number', label: 'Extra edge margin (px, for TV overscan)', min: 0, max: 120, default: 0 },
];

const DEFAULTS = Object.fromEntries(PREF_FIELDS.map((f) => [f.key, f.default]));
let prefs = { ...DEFAULTS, ...storage.get(KEY, {}) };
const subs = new Set();

// URL overrides, handy for bookmarks on TVs: ?profile=tv&tv=1
const q = new URLSearchParams(location.search);
if (q.get('profile') && /^[a-z0-9][a-z0-9_-]{0,39}$/.test(q.get('profile'))) prefs.profile = q.get('profile');
if (q.has('tv')) prefs.tvMode = q.get('tv') === '0' ? 'off' : 'on';

export const getPrefs = () => prefs;

export function setPrefs(patch) {
  prefs = { ...prefs, ...patch };
  storage.set(KEY, prefs);
  for (const fn of subs) fn(prefs);
}

export function onPrefs(fn) { subs.add(fn); return () => subs.delete(fn); }

export function isTvDevice() {
  return /\bAFT|Silk|SmartTV|SMART-TV|Tizen|Web0S|WebOS|BRAVIA|Android TV|GoogleTV|CrKey|HbbTV|NetCast|Roku|PlayStation|Xbox/i.test(navigator.userAgent);
}

export function tvActive() {
  return prefs.tvMode === 'on' || (prefs.tvMode === 'auto' && isTvDevice());
}

export function rotateSeconds() {
  const r = prefs.rotateSeconds;
  if (r === null || r === undefined || r === '') return tvActive() ? 45 : 0;
  return Number(r) || 0;
}
