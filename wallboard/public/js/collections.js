// Live, offline-first collections (timers, tasks, or anything a widget wants).
// Changes apply locally at once, are cached in localStorage, written to the server
// (queued while offline) and pushed to other screens via server-sent events.
import * as api from './api.js';
import { storage, uid } from './lib/util.js';

const cache = new Map();

class LiveCollection {
  constructor(name) {
    this.name = name;
    this.key = `wb:c:${name}`;
    const saved = storage.get(this.key, { version: 0, items: [] });
    this.items = saved.items || [];
    this.version = saved.version || 0;
    this.subs = new Set();
    this.loaded = false;
    this.refresh = this.refresh.bind(this);
    api.on('change', (e) => {
      if (e.kind === 'collection' && e.name === this.name && e.version !== this.version) this.refresh();
    });
    api.on('sse', (e) => { if (e.connected) this.refresh(); });
    this.refresh();
  }

  async refresh() {
    // Don't overwrite local edits that haven't reached the server yet.
    if (api.pendingWrites()) await api.flushQueue();
    if (api.pendingWrites()) return;
    try {
      const d = await api.get(`/api/c/${this.name}`);
      this.items = d.items;
      this.version = d.version;
      this.loaded = true;
      this.#persist();
      this.#notify();
    } catch { /* offline: keep local copy */ }
  }

  #persist() { storage.set(this.key, { version: this.version, items: this.items }); }
  #notify() { for (const fn of this.subs) { try { fn(this.items); } catch (e) { console.error(e); } } }

  subscribe(fn) {
    this.subs.add(fn);
    fn(this.items);
    return () => this.subs.delete(fn);
  }

  get(id) { return this.items.find((i) => i.id === id); }

  add(item) {
    const full = { ...item, id: item.id || uid(), createdAt: item.createdAt || new Date(api.now()).toISOString() };
    this.items = [...this.items, full];
    this.#local();
    api.enqueue({ method: 'POST', path: `/api/c/${this.name}`, body: full });
    return full;
  }

  update(id, patch) {
    const cur = this.get(id);
    if (!cur) return null;
    const next = { ...cur, ...patch };
    this.items = this.items.map((i) => (i.id === id ? next : i));
    this.#local();
    api.enqueue({ method: 'PATCH', path: `/api/c/${this.name}/${encodeURIComponent(id)}`, body: patch });
    return next;
  }

  remove(id) {
    this.items = this.items.filter((i) => i.id !== id);
    this.#local();
    api.enqueue({ method: 'DELETE', path: `/api/c/${this.name}/${encodeURIComponent(id)}` });
  }

  #local() { this.#persist(); this.#notify(); }
}

export function collection(name) {
  if (!/^[a-z0-9][a-z0-9_-]{0,39}$/.test(name)) throw new Error(`invalid collection name "${name}"`);
  if (!cache.has(name)) cache.set(name, new LiveCollection(name));
  return cache.get(name);
}
