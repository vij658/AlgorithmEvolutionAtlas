// Widget registry and loader. A widget is a folder under /widgets/<id>/ containing
// manifest.json and an ES module exporting `mount(root, ctx)`. See WIDGETS.md.
import * as api from './api.js';
import { collection } from './collections.js';
import * as util from './lib/util.js';
import { formatDuration, parseDuration } from './lib/duration.js';
import { tvActive } from './prefs.js';

let registry = new Map();
const modules = new Map();
const styles = new Set();

export async function loadRegistry() {
  let list = [];
  try {
    list = (await api.getCached('/api/widgets')).data;
  } catch {
    list = [];
  }
  registry = new Map(list.map((m) => [m.id, m]));
  return registry;
}

export const getManifest = (type) => registry.get(type);
export const allManifests = () => [...registry.values()];

/** Settings with manifest defaults filled in. */
export function withDefaults(manifest, settings = {}) {
  const out = {};
  for (const f of manifest?.settings || []) {
    if (f.default !== undefined) out[f.key] = util.clone(f.default);
  }
  return { ...out, ...settings };
}

async function loadModule(m) {
  const url = `/widgets/${m.id}/${m.module || 'widget.js'}`;
  if (!modules.has(url)) modules.set(url, import(url));
  for (const css of m.styles || []) {
    const href = `/widgets/${m.id}/${css}`;
    if (!styles.has(href)) {
      styles.add(href);
      document.head.append(util.el('link', { rel: 'stylesheet', href }));
    }
  }
  return modules.get(url);
}

/**
 * Mount a widget into `root`. Returns a handle with unmount(). Widget errors are
 * contained: the card shows the message instead of breaking the board.
 */
export async function mountWidget(root, widget, { saveSettings, isVisible, onVisible }) {
  const manifest = registry.get(widget.type);
  const cleanups = [];
  const handle = { unmount() { for (const c of cleanups.splice(0)) { try { c(); } catch (e) { console.error(e); } } } };
  root.className = `widget-body w-${widget.type}`;
  root.replaceChildren();
  if (!manifest) {
    root.append(util.el('div.widget-error', `Unknown widget “${widget.type}”. Its folder may have been removed.`));
    return handle;
  }
  const ctx = {
    id: widget.id,
    type: widget.type,
    manifest,
    settings: withDefaults(manifest, widget.settings),
    get tv() { return tvActive(); },
    api: { get: api.get, post: api.post, put: api.put, patch: api.patch, del: api.del, getCached: api.getCached },
    collection,
    now: api.now,
    util: { ...util, formatDuration, parseDuration },
    every(ms, fn, { immediate = true } = {}) {
      const t = setInterval(fn, ms);
      cleanups.push(() => clearInterval(t));
      if (immediate) fn();
      return () => clearInterval(t);
    },
    on(event, fn) { const off = api.on(event, fn); cleanups.push(off); return off; },
    onCleanup(fn) { cleanups.push(fn); },
    saveSettings(patch) { ctx.settings = { ...ctx.settings, ...patch }; saveSettings(patch); },
    isVisible,
    onVisible(fn) { const off = onVisible(fn); cleanups.push(off); return off; },
  };
  try {
    const mod = await loadModule(manifest);
    const mount = mod.mount || mod.default?.mount || mod.default;
    if (typeof mount !== 'function') throw new Error('module does not export mount()');
    const r = await mount(root, ctx);
    if (typeof r === 'function') cleanups.push(r);
    else if (r && typeof r.unmount === 'function') cleanups.push(() => r.unmount());
  } catch (err) {
    console.error(`[wallboard] widget ${widget.type} failed`, err);
    root.replaceChildren(util.el('div.widget-error', `${manifest.name || widget.type}: ${err.message}`));
  }
  return handle;
}
