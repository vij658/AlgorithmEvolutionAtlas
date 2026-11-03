// Keep the screen on: Screen Wake Lock API where available (needs HTTPS), otherwise a
// tiny muted looping video, which most mobile browsers treat as "media playing".
import { el } from './lib/util.js';
import { getPrefs, onPrefs, tvActive } from './prefs.js';
import * as api from './api.js';

let lock = null;
let video = null;
let method = 'off';
let lastError = '';

async function requestLock() {
  if (!getPrefs().keepAwake) return release();
  if ('wakeLock' in navigator && window.isSecureContext) {
    try {
      lock = await navigator.wakeLock.request('screen');
      method = 'wake-lock';
      lock.addEventListener('release', () => { lock = null; if (document.visibilityState === 'visible') setTimeout(requestLock, 1000); });
      stopVideo();
      return;
    } catch (e) {
      lastError = e.message;
    }
  }
  startVideo();
}

function startVideo() {
  if (!video) {
    video = el('video', { muted: true, loop: true, playsInline: true, 'aria-hidden': 'true', tabindex: '-1' });
    video.setAttribute('playsinline', '');
    video.setAttribute('muted', '');
    video.src = '/media/keep-awake.mp4';
    Object.assign(video.style, { position: 'fixed', width: '1px', height: '1px', opacity: '0.01', pointerEvents: 'none', left: '0', bottom: '0' });
    document.body.append(video);
  }
  video.play().then(() => { method = 'video'; }).catch((e) => { method = 'waiting-for-tap'; lastError = e.message; });
}

function stopVideo() { if (video) { video.pause(); video.remove(); video = null; } }

async function release() {
  method = 'off';
  stopVideo();
  try { await lock?.release(); } catch { /* ignore */ }
  lock = null;
}

export function initAwake() {
  requestLock();
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') requestLock(); });
  // Autoplay / wake lock may need a user gesture; retry on the first interaction.
  const retry = () => { if (method !== 'wake-lock' && method !== 'video') requestLock(); };
  document.addEventListener('pointerdown', retry, { passive: true });
  document.addEventListener('keydown', retry);
  onPrefs(() => requestLock());
}

export function screenInfo() {
  const p = getPrefs();
  return [
    `Keep awake: ${method === 'wake-lock' ? 'on (Wake Lock API)' : method === 'video' ? 'on (video fallback)' : method === 'waiting-for-tap' ? 'waiting for a tap' : 'off'}${lastError && method !== 'wake-lock' ? ` — ${lastError}` : ''}`,
    `Secure context (HTTPS): ${window.isSecureContext ? 'yes' : 'no — offline cache and Wake Lock need HTTPS'}`,
    `Offline cache (service worker): ${navigator.serviceWorker?.controller ? 'active' : 'not active'}`,
    `TV mode: ${tvActive() ? 'on' : 'off'} (setting: ${p.tvMode})`,
    `Server: ${api.isOnline() ? 'reachable' : 'offline'}, live updates: ${api.sseState()}`,
    `Screen: ${innerWidth}×${innerHeight} @${devicePixelRatio}x, layout: ${document.documentElement.dataset.mode}`,
  ];
}
