import { EventEmitter } from 'node:events';
import { randomUUID } from 'node:crypto';
import { readJson, JsonWriter } from './jsonfile.js';
import { normalizeRect, overlaps } from '../public/js/lib/grid.js';
import { defaultLayout } from './default-layout.js';

export const NAME_RE = /^[a-z0-9][a-z0-9_-]{0,39}$/;
const ID_RE = /^[A-Za-z0-9_.:-]{1,64}$/;
const LIMITS = { pages: 30, widgetsPerPage: 60, itemsPerCollection: 2000, itemBytes: 16_384, settingsBytes: 65_536 };

export class ValidationError extends Error {
  constructor(msg) { super(msg); this.status = 400; }
}
export class ConflictError extends Error {
  constructor(msg, current) { super(msg); this.status = 409; this.current = current; }
}

const clone = (v) => structuredClone(v);
const isObj = (v) => v && typeof v === 'object' && !Array.isArray(v);

/** Validate and normalise a layout coming from a client. Throws ValidationError. */
export function sanitizePages(pages) {
  if (!Array.isArray(pages)) throw new ValidationError('pages must be an array');
  if (pages.length < 1) throw new ValidationError('a layout needs at least one page');
  if (pages.length > LIMITS.pages) throw new ValidationError(`at most ${LIMITS.pages} pages`);
  const pageIds = new Set();
  return pages.map((p, i) => {
    if (!isObj(p)) throw new ValidationError(`page ${i} is not an object`);
    let id = typeof p.id === 'string' && ID_RE.test(p.id) ? p.id : `page-${randomUUID().slice(0, 8)}`;
    if (pageIds.has(id)) id = `page-${randomUUID().slice(0, 8)}`;
    pageIds.add(id);
    const name = String(p.name ?? `Page ${i + 1}`).slice(0, 60).trim() || `Page ${i + 1}`;
    const src = Array.isArray(p.widgets) ? p.widgets : [];
    if (src.length > LIMITS.widgetsPerPage) throw new ValidationError(`page "${name}" has too many widgets`);
    const widgets = [];
    const ids = new Set();
    for (const w of src) {
      if (!isObj(w)) throw new ValidationError(`page "${name}" contains a non-object widget`);
      if (typeof w.type !== 'string' || !NAME_RE.test(w.type)) throw new ValidationError(`invalid widget type "${w.type}"`);
      let wid = typeof w.id === 'string' && ID_RE.test(w.id) ? w.id : `${w.type}-${randomUUID().slice(0, 8)}`;
      if (ids.has(wid)) wid = `${w.type}-${randomUUID().slice(0, 8)}`;
      ids.add(wid);
      const settings = isObj(w.settings) ? w.settings : {};
      if (JSON.stringify(settings).length > LIMITS.settingsBytes) throw new ValidationError(`settings for ${wid} are too large`);
      const rect = normalizeRect(w);
      // Overlaps can't be fixed automatically in a meaningful way; reject so the
      // client finds out instead of the layout silently changing.
      const clash = widgets.find((o) => overlaps(o, rect));
      if (clash) throw new ValidationError(`widgets ${clash.id} and ${wid} overlap on page "${name}"`);
      widgets.push({ id: wid, type: w.type, ...rect, settings });
    }
    return { id, name, widgets };
  });
}

function sanitizeItem(item) {
  if (!isObj(item)) throw new ValidationError('item must be an object');
  if (JSON.stringify(item).length > LIMITS.itemBytes) throw new ValidationError('item too large');
  return item;
}

/**
 * Persistent state: one layout per profile (a profile is a named screen setup such as
 * "kitchen" or "tv") plus generic named collections (timers, tasks, anything a
 * custom widget wants). Emits 'change' events for live sync.
 */
export class Store extends EventEmitter {
  constructor(file) {
    super();
    this.file = file;
    this.writer = new JsonWriter(file);
    this.data = { layouts: {}, collections: {} };
  }

  async load() {
    const d = await readJson(this.file, null);
    if (isObj(d)) {
      this.data.layouts = isObj(d.layouts) ? d.layouts : {};
      this.data.collections = isObj(d.collections) ? d.collections : {};
    }
    return this;
  }

  save() { return this.writer.write(() => this.data); }
  flush() { return this.writer.flush(); }

  // ---- layouts --------------------------------------------------------------
  checkProfile(profile) {
    if (!NAME_RE.test(profile)) throw new ValidationError('profile names use a-z, 0-9, "-" and "_" (max 40)');
  }

  getLayout(profile) {
    this.checkProfile(profile);
    const l = this.data.layouts[profile];
    if (l) return clone({ profile, ...l });
    return { profile, ...defaultLayout(), isDefault: true };
  }

  listProfiles() {
    return Object.entries(this.data.layouts).map(([profile, l]) => ({
      profile, version: l.version, updatedAt: l.updatedAt, pages: l.pages.length,
    }));
  }

  /** Replace a profile's pages. With baseVersion, refuses to overwrite newer data. */
  putLayout(profile, body) {
    this.checkProfile(profile);
    if (!isObj(body)) throw new ValidationError('body must be an object');
    const pages = sanitizePages(body.pages);
    const current = this.data.layouts[profile];
    const curVersion = current?.version ?? 0;
    if (body.baseVersion != null && !body.force && Number(body.baseVersion) !== curVersion) {
      throw new ConflictError('layout was changed on another device', this.getLayout(profile));
    }
    const next = { version: curVersion + 1, updatedAt: new Date().toISOString(), pages };
    this.data.layouts[profile] = next;
    this.save();
    this.emit('change', { kind: 'layout', profile, version: next.version });
    return clone({ profile, ...next });
  }

  deleteLayout(profile) {
    this.checkProfile(profile);
    const existed = !!this.data.layouts[profile];
    delete this.data.layouts[profile];
    this.save();
    this.emit('change', { kind: 'layout', profile, version: 0 });
    return existed;
  }

  /** Every feed URL referenced by any widget's `feeds` setting, across all profiles. */
  allFeedUrls() {
    const urls = new Set();
    const layouts = Object.keys(this.data.layouts).length ? Object.values(this.data.layouts) : [defaultLayout()];
    for (const l of layouts) {
      for (const p of l.pages) {
        for (const w of p.widgets) {
          const f = w.settings?.feeds;
          if (Array.isArray(f)) for (const u of f) if (typeof u === 'string' && /^https?:\/\//i.test(u)) urls.add(u.trim());
        }
      }
    }
    return [...urls];
  }

  // ---- collections ----------------------------------------------------------
  #col(name, create = false) {
    if (!NAME_RE.test(name)) throw new ValidationError('collection names use a-z, 0-9, "-" and "_" (max 40)');
    let c = this.data.collections[name];
    if (!c && create) c = this.data.collections[name] = { version: 0, items: [] };
    return c;
  }

  #changed(name, c) {
    c.version++;
    c.updatedAt = new Date().toISOString();
    this.save();
    this.emit('change', { kind: 'collection', name, version: c.version });
  }

  getCollection(name) {
    const c = this.#col(name);
    return c ? clone({ name, version: c.version, updatedAt: c.updatedAt, items: c.items }) : { name, version: 0, items: [] };
  }

  addItem(name, item) {
    const c = this.#col(name, true);
    item = sanitizeItem(item);
    if (c.items.length >= LIMITS.itemsPerCollection) throw new ValidationError('collection is full');
    const id = typeof item.id === 'string' && ID_RE.test(item.id) ? item.id : randomUUID();
    const existing = c.items.findIndex((i) => i.id === id);
    const now = new Date().toISOString();
    const stored = { ...item, id, createdAt: item.createdAt || now, updatedAt: now };
    // POST with a known id is idempotent (offline clients may retry).
    if (existing >= 0) c.items[existing] = stored; else c.items.push(stored);
    this.#changed(name, c);
    return clone(stored);
  }

  putItem(name, id, item) {
    const c = this.#col(name, true);
    item = sanitizeItem(item);
    const idx = c.items.findIndex((i) => i.id === id);
    const now = new Date().toISOString();
    const stored = { ...item, id, createdAt: idx >= 0 ? c.items[idx].createdAt : now, updatedAt: now };
    if (idx >= 0) c.items[idx] = stored; else c.items.push(stored);
    this.#changed(name, c);
    return clone(stored);
  }

  patchItem(name, id, patch) {
    const c = this.#col(name);
    const idx = c ? c.items.findIndex((i) => i.id === id) : -1;
    if (idx < 0) return null;
    patch = sanitizeItem(patch);
    const merged = sanitizeItem({ ...c.items[idx], ...patch, id, updatedAt: new Date().toISOString() });
    c.items[idx] = merged;
    this.#changed(name, c);
    return clone(merged);
  }

  deleteItem(name, id) {
    const c = this.#col(name);
    const idx = c ? c.items.findIndex((i) => i.id === id) : -1;
    if (idx < 0) return false;
    c.items.splice(idx, 1);
    this.#changed(name, c);
    return true;
  }

  replaceCollection(name, items) {
    if (!Array.isArray(items)) throw new ValidationError('items must be an array');
    if (items.length > LIMITS.itemsPerCollection) throw new ValidationError('too many items');
    const c = this.#col(name, true);
    c.items = items.map((it) => {
      sanitizeItem(it);
      return { ...it, id: typeof it.id === 'string' && ID_RE.test(it.id) ? it.id : randomUUID() };
    });
    this.#changed(name, c);
    return this.getCollection(name);
  }
}
