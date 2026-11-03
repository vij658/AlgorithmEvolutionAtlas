// The layout (pages + widgets) for this screen's profile: loading, saving, live sync
// with other screens, offline fallback.
import * as api from './api.js';
import { storage, clone, uid, debounce } from './lib/util.js';
import { getPrefs } from './prefs.js';

const FALLBACK = {
  version: 0,
  pages: [{ id: 'page-home', name: 'Home', widgets: [
    { id: 'clock-fallback', type: 'clock', x: 0, y: 0, w: 12, h: 5, settings: { showDate: true, showSeconds: true } },
    { id: 'fresh-fallback', type: 'freshness', x: 0, y: 5, w: 12, h: 3, settings: {} },
  ] }],
};

const subs = new Set();
let state = null; // { profile, version, pages, dirty }
let holdRemote = false; // while editing, remote changes wait
let remotePending = false;

const key = () => `wb:layout:${getPrefs().profile}`;

function publish(reason) {
  for (const fn of subs) fn(state, reason);
}

export const getLayout = () => state;
export function onLayout(fn) { subs.add(fn); return () => subs.delete(fn); }

export async function loadLayout() {
  const profile = getPrefs().profile;
  const local = storage.get(key());
  try {
    const remote = await api.get(`/api/layout/${profile}`);
    if (local?.dirty && local.profile === profile) {
      // Edited while offline. Push our copy unless someone else saved in between.
      state = { ...local };
      if ((local.baseVersion ?? local.version) === remote.version) { await save(true); publish('load'); return state; }
      console.warn('[wallboard] offline edits conflict with a newer layout; keeping the server copy');
    }
    state = { profile, version: remote.version, pages: remote.pages, dirty: false };
  } catch {
    state = local && local.profile === profile ? local : { profile, ...clone(FALLBACK), dirty: false };
  }
  storage.set(key(), state);
  publish('load');
  return state;
}

const saveSoon = debounce(() => save(), 700);

/** Apply a mutation to a copy of the pages and save. `fn(pages)` may return new pages. */
export function mutate(fn, { immediate = false } = {}) {
  const pages = clone(state.pages);
  const out = fn(pages);
  state = { ...state, pages: out || pages, dirty: true, baseVersion: state.baseVersion ?? state.version };
  storage.set(key(), state);
  publish('local');
  if (immediate) saveSoon.flush(); else saveSoon();
}

export function replacePages(pages) { mutate(() => clone(pages), { immediate: true }); }

async function save(force = false) {
  if (!state?.dirty) return;
  const sent = state.pages;
  const body = { pages: sent, baseVersion: state.baseVersion ?? state.version, force };
  try {
    const saved = await api.put(`/api/layout/${state.profile}`, body);
    if (state.pages !== sent) {
      // Edited again while the save was in flight: keep the newer local pages.
      state = { ...state, version: saved.version, baseVersion: saved.version };
      storage.set(key(), state);
      saveSoon();
      return;
    }
    state = { profile: state.profile, version: saved.version, pages: saved.pages, dirty: false };
    storage.set(key(), state);
    api.emit('layout-saved', { version: saved.version });
  } catch (err) {
    if (err instanceof api.ApiError && err.status === 409) {
      // Someone else saved meanwhile. The person editing here wins: they are looking at it.
      return save(true);
    }
    if (err instanceof api.ApiError) {
      api.emit('layout-error', { message: err.message });
      return;
    }
    setTimeout(() => save(), 20000); // offline; retry
  }
}

export function holdRemoteChanges(hold) {
  holdRemote = hold;
  if (!hold && remotePending) { remotePending = false; refreshFromServer(); }
}

async function refreshFromServer() {
  if (state?.dirty) return;
  try {
    const remote = await api.get(`/api/layout/${state.profile}`);
    if (remote.version === state.version) return;
    state = { profile: state.profile, version: remote.version, pages: remote.pages, dirty: false };
    storage.set(key(), state);
    publish('remote');
  } catch { /* offline */ }
}

api.on('change', (e) => {
  if (e.kind !== 'layout' || !state || e.profile !== state.profile || e.version === state.version) return;
  if (holdRemote) { remotePending = true; return; }
  refreshFromServer();
});
api.on('sse', (e) => { if (e.connected && state && !holdRemote) { if (state.dirty) save(); else refreshFromServer(); } });

// ---- helpers used by edit mode ------------------------------------------------
export function newPage(name = 'New page') { return { id: uid('page'), name, widgets: [] }; }

export function exportLayout() {
  return { format: 'wallboard-layout', version: 1, exportedAt: new Date().toISOString(), profile: state.profile, pages: clone(state.pages) };
}

export function parseImport(json) {
  const d = typeof json === 'string' ? JSON.parse(json) : json;
  const pages = Array.isArray(d) ? d : d?.pages;
  if (!Array.isArray(pages) || !pages.length) throw new Error('This file does not contain a Wallboard layout.');
  for (const p of pages) {
    if (!p || !Array.isArray(p.widgets)) throw new Error('A page in this file has no widget list.');
    for (const w of p.widgets) if (!w || typeof w.type !== 'string') throw new Error('A widget in this file has no type.');
  }
  return pages;
}

export async function resetToDefault() {
  await api.del(`/api/layout/${state.profile}`);
  storage.remove(key());
  return loadLayout();
}
