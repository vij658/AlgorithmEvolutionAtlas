// Talks to the Wallboard server: JSON helpers, server clock offset, an offline write
// queue, a last-good-response cache, and the server-sent event stream.
import { storage } from './lib/util.js';

const listeners = new Map(); // event -> Set<fn>
let clockOffset = storage.get('wb:clockOffset', 0);
let online = true;
let es = null;

export function on(event, fn) {
  if (!listeners.has(event)) listeners.set(event, new Set());
  listeners.get(event).add(fn);
  return () => listeners.get(event)?.delete(fn);
}

export function emit(event, data) {
  for (const fn of listeners.get(event) || []) {
    try { fn(data); } catch (e) { console.error(`[wallboard] ${event} listener`, e); }
  }
}

/** Date.now() corrected to the server clock, so timers agree across devices. */
export const now = () => Date.now() + clockOffset;
export const isOnline = () => online;

function setOnline(v) {
  if (v === online) return;
  online = v;
  emit('connection', { online: v });
  if (v) flushQueue();
}

function noteServerTime(t, sentAt, recvAt) {
  const st = Number(t);
  if (!st) return;
  // Assume the server stamped the response half-way through the round trip.
  const offset = st - (sentAt + recvAt) / 2;
  // Ignore jitter; only move when the change is real.
  if (Math.abs(offset - clockOffset) > 750) {
    clockOffset = Math.round(offset);
    storage.set('wb:clockOffset', clockOffset);
  }
}

export class ApiError extends Error {
  constructor(status, msg, data) { super(msg); this.status = status; this.data = data; }
}

/** fetch JSON. Throws ApiError for HTTP errors, TypeError for network failures. */
export async function request(method, path, body, { timeout = 15000 } = {}) {
  const sentAt = Date.now();
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: body !== undefined ? { 'content-type': 'application/json' } : {},
      body: body !== undefined ? JSON.stringify(body) : undefined,
      cache: 'no-store',
      signal: AbortSignal.timeout ? AbortSignal.timeout(timeout) : undefined,
    });
  } catch (err) {
    setOnline(false);
    throw err;
  }
  noteServerTime(res.headers.get('x-server-time'), sentAt, Date.now());
  // A response served by the service worker from cache means we're offline.
  setOnline(res.headers.get('x-wallboard-offline') !== '1');
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) throw new ApiError(res.status, data?.error || `HTTP ${res.status}`, data);
  return data;
}

export const get = (p, o) => request('GET', p, undefined, o);
export const post = (p, b, o) => request('POST', p, b ?? {}, o);
export const put = (p, b, o) => request('PUT', p, b, o);
export const patch = (p, b, o) => request('PATCH', p, b, o);
export const del = (p, o) => request('DELETE', p, undefined, o);

/** GET with a localStorage fallback: returns the last good response when offline. */
export async function getCached(path, key = 'wb:get:' + path) {
  try {
    const data = await get(path);
    storage.set(key, { at: Date.now(), data });
    return { data, stale: false };
  } catch (err) {
    const hit = storage.get(key);
    if (hit) return { data: hit.data, stale: true, at: hit.at, error: err };
    throw err;
  }
}

// ---- offline write queue ------------------------------------------------------
// Writes that fail because the server is unreachable are kept and replayed in order.
let queue = storage.get('wb:queue', []);
let flushing = null;

export function enqueue(op) {
  queue.push({ ...op, at: Date.now() });
  storage.set('wb:queue', queue);
  return flushQueue();
}

export const pendingWrites = () => queue.length;

export function flushQueue() {
  if (flushing) return flushing;
  flushing = (async () => {
    while (queue.length) {
      const op = queue[0];
      try {
        await request(op.method, op.path, op.body);
      } catch (err) {
        if (err instanceof ApiError && err.status < 500) {
          console.warn('[wallboard] dropping rejected write', op, err.message);
        } else {
          setTimeout(flushQueue, 15000);
          break; // still offline; try again later
        }
      }
      queue.shift();
      storage.set('wb:queue', queue);
    }
    emit('queue', { pending: queue.length });
  })().finally(() => { flushing = null; });
  return flushing;
}

// ---- server-sent events ---------------------------------------------------------
export function connectEvents() {
  if (es || typeof EventSource === 'undefined') return;
  es = new EventSource('/api/events');
  const handle = (type) => (ev) => {
    let data = {};
    try { data = JSON.parse(ev.data); } catch { /* ignore */ }
    if (data.serverTime) noteServerTime(data.serverTime, Date.now(), Date.now());
    emit(type, data);
  };
  es.addEventListener('hello', (ev) => { setOnline(true); emit('sse', { connected: true }); handle('hello')(ev); });
  es.addEventListener('change', handle('change'));
  es.addEventListener('crawl', handle('crawl'));
  es.onerror = () => { emit('sse', { connected: false }); };
  // Browsers reconnect EventSource by themselves; when the tab comes back after a long
  // sleep, force a fresh connection so we don't miss changes.
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible' && es && es.readyState === EventSource.CLOSED) {
      es = null; connectEvents();
    }
  });
}

export const sseState = () => (es ? ['connecting', 'open', 'closed'][es.readyState] : 'off');

window.addEventListener('online', () => flushQueue());
