// Service worker: makes the app open without the server (app shell cached) and keeps
// the last good API responses for offline display. Bump VERSION on every release.
const VERSION = 'wallboard-v1.0.0';
const SHELL = [
  '/', '/index.html', '/manifest.webmanifest', '/css/app.css',
  '/js/main.js', '/js/api.js', '/js/board.js', '/js/collections.js', '/js/dim.js', '/js/drift.js',
  '/js/edit.js', '/js/form.js', '/js/layout.js', '/js/prefs.js', '/js/tv.js', '/js/widgets.js', '/js/awake.js',
  '/js/lib/util.js', '/js/lib/grid.js', '/js/lib/duration.js',
  '/icons/icon.svg', '/icons/icon-192.png', '/media/keep-awake.mp4',
];
const API_CACHE = `${VERSION}-api`;
// API responses worth showing while offline.
const CACHEABLE_API = /^\/api\/(widgets|layout\/|c\/|news|status|feeds\/status|weather)/;

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const cache = await caches.open(VERSION);
    await cache.addAll(SHELL);
    // Pre-cache the built-in widgets listed by the server.
    try {
      const list = await (await fetch('/api/widgets', { cache: 'no-store' })).json();
      const urls = list.filter((w) => w.origin === 'builtin').flatMap((w) => [
        `/widgets/${w.id}/manifest.json`, `/widgets/${w.id}/${w.module || 'widget.js'}`, ...(w.styles || []).map((s) => `/widgets/${w.id}/${s}`),
      ]);
      await cache.addAll(urls);
    } catch { /* widgets will be cached on first use */ }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    for (const key of await caches.keys()) if (!key.startsWith(VERSION)) await caches.delete(key);
    await self.clients.claim();
  })());
});

function offline(res) {
  // Mark responses served from cache so the app can show an "offline" badge.
  const h = new Headers(res.headers);
  h.set('x-wallboard-offline', '1');
  return new Response(res.body, { status: res.status, statusText: res.statusText, headers: h });
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin) return;
  if (url.pathname === '/api/events') return; // never touch the event stream

  if (url.pathname.startsWith('/api/')) {
    if (!CACHEABLE_API.test(url.pathname)) return;
    // Network first, cache as fallback.
    e.respondWith((async () => {
      try {
        const res = await fetch(req);
        if (res.ok) (await caches.open(API_CACHE)).put(req, res.clone());
        return res;
      } catch (err) {
        const hit = await caches.match(req, { cacheName: API_CACHE });
        if (hit) return offline(hit);
        throw err;
      }
    })());
    return;
  }

  // App shell & widgets: stale-while-revalidate, so screens start instantly and pick
  // up new versions on the next load.
  e.respondWith((async () => {
    const cache = await caches.open(VERSION);
    const hit = await cache.match(req, { ignoreSearch: url.pathname === '/' });
    const net = fetch(req).then((res) => {
      if (res.ok && res.type === 'basic') cache.put(req, res.clone());
      return res;
    }).catch(() => null);
    if (hit) { e.waitUntil(net); return hit; }
    const res = await net;
    if (res) return res;
    if (req.mode === 'navigate') return (await cache.match('/index.html')) || Response.error();
    return Response.error();
  })());
});
