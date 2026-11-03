// Small DOM and formatting helpers available to the app and to widgets (ctx.util).

/**
 * el('div.card#main', {onclick, title, style:{...}, dataset:{...}}, child, 'text', [more])
 * Creates an element. Strings become text nodes (never parsed as HTML).
 */
export function el(spec, props, ...children) {
  if (props == null || typeof props !== 'object' || props instanceof Node || Array.isArray(props)) {
    if (props != null) children.unshift(props);
    props = {};
  }
  const m = /^([a-z0-9-]+)?((?:[.#][\w-]+)*)$/i.exec(spec) || [];
  const node = document.createElement(m[1] || 'div');
  for (const part of (m[2] || '').match(/[.#][\w-]+/g) || []) {
    if (part[0] === '.') node.classList.add(part.slice(1)); else node.id = part.slice(1);
  }
  for (const [k, v] of Object.entries(props)) {
    if (v == null || v === false) continue;
    if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
    else if (k === 'style' && typeof v === 'object') Object.assign(node.style, v);
    else if (k === 'dataset') Object.assign(node.dataset, v);
    else if (k === 'class') node.className += ' ' + v;
    else if (k in node && typeof node[k] !== 'function' && !k.includes('-')) node[k] = v;
    else node.setAttribute(k, v === true ? '' : v);
  }
  append(node, children);
  return node;
}

function append(node, children) {
  for (const c of children.flat(Infinity)) {
    if (c == null || c === false) continue;
    node.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
}

export function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
}

export function uid(prefix = '') {
  const r = (globalThis.crypto?.randomUUID?.() || Math.random().toString(36).slice(2) + Date.now().toString(36)).replace(/-/g, '').slice(0, 10);
  return prefix ? `${prefix}-${r}` : r;
}

export function debounce(fn, ms) {
  let t;
  const d = (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
  d.cancel = () => clearTimeout(t);
  d.flush = (...a) => { clearTimeout(t); fn(...a); };
  return d;
}

/** "just now", "5 min ago", "3 h ago", "2 d ago", or a date. */
export function relTime(input, now = Date.now()) {
  if (!input) return 'never';
  const t = typeof input === 'number' ? input : Date.parse(input);
  if (!Number.isFinite(t)) return '';
  const s = Math.round((now - t) / 1000);
  if (s < -60) return 'in ' + relTime(now - (t - now), now).replace(' ago', '');
  if (s < 45) return 'just now';
  const m = Math.round(s / 60);
  if (m < 60) return `${m} min ago`;
  const h = Math.round(m / 60);
  if (h < 36) return `${h} h ago`;
  const d = Math.round(h / 24);
  if (d < 14) return `${d} d ago`;
  return new Date(t).toLocaleDateString();
}

export function hostOf(u) {
  try { return new URL(u).hostname.replace(/^www\./, ''); } catch { return String(u || ''); }
}

export function clone(v) { return v == null ? v : JSON.parse(JSON.stringify(v)); }

export function sameJson(a, b) { return JSON.stringify(a) === JSON.stringify(b); }

/** localStorage that never throws (private mode, quota, disabled storage). */
export const storage = {
  get(key, fallback = null) {
    try { const v = localStorage.getItem(key); return v == null ? fallback : JSON.parse(v); } catch { return fallback; }
  },
  set(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
  },
  remove(key) { try { localStorage.removeItem(key); } catch { /* ignore */ } },
};

/** "HH:MM" -> minutes after midnight. */
export function hm(s) {
  const m = /^(\d{1,2}):(\d{2})$/.exec(String(s || ''));
  return m ? (+m[1] % 24) * 60 + (+m[2] % 60) : null;
}

/** Is minute-of-day `now` inside [start, end) where the range may wrap midnight. */
export function inWindow(now, start, end) {
  if (start == null || end == null || start === end) return false;
  return start < end ? now >= start && now < end : now >= start || now < end;
}

export function toast(msg, ms = 3500) {
  let host = document.getElementById('toasts');
  if (!host) { host = el('div#toasts', { role: 'status', 'aria-live': 'polite' }); document.body.append(host); }
  const t = el('div.toast', msg);
  host.append(t);
  setTimeout(() => { t.classList.add('out'); setTimeout(() => t.remove(), 400); }, ms);
}
