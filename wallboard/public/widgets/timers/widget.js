// Timers: presets + custom durations, many at once, synced via the "timers" collection.
// A timer is { id, label, durationMs, state: 'running'|'paused', endsAt, remainingMs, group }.

let audio = null;
function unlockAudio() {
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    if (audio.state === 'suspended') audio.resume();
  } catch { /* no audio */ }
}
// Browsers only allow sound after a user gesture; unlock on the first one.
document.addEventListener('pointerdown', unlockAudio, { once: true, capture: true });
document.addEventListener('keydown', unlockAudio, { once: true, capture: true });

function beep() {
  if (!audio || audio.state !== 'running') return;
  const t0 = audio.currentTime;
  for (let i = 0; i < 3; i++) {
    const o = audio.createOscillator(), g = audio.createGain();
    o.type = 'sine';
    o.frequency.value = 880;
    g.gain.setValueAtTime(0.0001, t0 + i * 0.35);
    g.gain.exponentialRampToValueAtTime(0.35, t0 + i * 0.35 + 0.02);
    g.gain.exponentialRampToValueAtTime(0.0001, t0 + i * 0.35 + 0.25);
    o.connect(g).connect(audio.destination);
    o.start(t0 + i * 0.35);
    o.stop(t0 + i * 0.35 + 0.3);
  }
}

// Shared across widget instances so two timer widgets don't double-alert.
const alerted = new Map(); // timer id -> last alert time
const RING_FOR_MS = 2 * 60_000;

export function mount(root, ctx) {
  const { el, formatDuration, parseDuration } = ctx.util;
  const s = ctx.settings;
  const group = s.group || 'default';
  const col = ctx.collection('timers');
  const presets = (s.presets || []).map((p) => ({ label: p.trim(), ms: parseDuration(p) })).filter((p) => p.ms);

  const remaining = (t) => (t.state === 'running' ? t.endsAt - ctx.now() : t.remainingMs ?? t.durationMs);
  const ringing = (t) => t.state === 'running' && t.endsAt <= ctx.now();

  const input = el('input.tm-input', { type: 'text', placeholder: 'e.g. 7m Pasta · 1:30 · 2h', enterkeyhint: 'go', autocomplete: 'off', 'aria-label': 'New timer: duration and optional label' });
  const err = el('div.tm-err');
  const startCustom = () => {
    const [first, ...rest] = input.value.trim().split(/\s+/);
    const ms = parseDuration(first);
    if (!ms) { err.textContent = 'Try 10m, 1h30m, 90s or 1:30'; return; }
    err.textContent = '';
    start(ms, rest.join(' ') || first);
    input.value = '';
    input.blur();
  };
  input.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); startCustom(); } });

  const count = el('span.w-meta');
  const list = el('div.tm-list.w-scroll');
  root.append(
    el('div.w-head', el('span.w-title', s.title || 'Timers'), count),
    el('div.tm-presets', presets.map((p) => el('button.btn.tm-preset', { type: 'button', onclick: () => start(p.ms, p.label), 'aria-label': `Start a ${p.label} timer` }, p.label))),
    el('div.tm-new', input, el('button.btn.primary', { type: 'button', onclick: startCustom }, 'Start')),
    err,
    list,
  );

  function start(ms, label) {
    unlockAudio();
    col.add({ label, durationMs: ms, state: 'running', endsAt: ctx.now() + ms, remainingMs: ms, group });
  }

  const rows = new Map(); // id -> { row, time, bar, state }
  let timers = [];

  function actions(t) {
    const btn = (label, title, fn, cls = '') => el('button.icon-btn.tm-act', { type: 'button', title, 'aria-label': `${title} ${t.label}`, class: cls, onclick: fn }, label);
    if (ringing(t)) {
      return [
        btn('↺', 'Restart', () => col.update(t.id, { state: 'running', endsAt: ctx.now() + t.durationMs, remainingMs: t.durationMs })),
        el('button.btn.primary.tm-dismiss', { type: 'button', onclick: () => col.remove(t.id) }, 'Dismiss'),
      ];
    }
    return [
      t.state === 'running'
        ? btn('❚❚', 'Pause', () => col.update(t.id, { state: 'paused', remainingMs: Math.max(0, t.endsAt - ctx.now()) }))
        : btn('▶', 'Resume', () => col.update(t.id, { state: 'running', endsAt: ctx.now() + remaining(t) })),
      btn('+1', 'Add a minute', () => (t.state === 'running'
        ? col.update(t.id, { endsAt: t.endsAt + 60_000, durationMs: t.durationMs + 60_000 })
        : col.update(t.id, { remainingMs: remaining(t) + 60_000, durationMs: t.durationMs + 60_000 }))),
      btn('↺', 'Reset', () => col.update(t.id, { state: 'paused', remainingMs: t.durationMs })),
      btn('✕', 'Delete', () => col.remove(t.id), 'tm-del'),
    ];
  }

  function rebuild() {
    const sorted = timers.filter((t) => (t.group || 'default') === group).sort((a, b) =>
      (ringing(b) - ringing(a)) || ((a.state === 'running' ? 0 : 1) - (b.state === 'running' ? 0 : 1)) || (remaining(a) - remaining(b)));
    count.textContent = sorted.length ? `${sorted.filter((t) => t.state === 'running' && !ringing(t)).length} running` : '';
    rows.clear();
    if (!sorted.length) { list.replaceChildren(el('div.w-empty', 'Tap a preset to start a timer.')); return; }
    list.replaceChildren(...sorted.map((t) => {
      const time = el('span.tm-time.tabular');
      const bar = el('i');
      const row = el('div.tm-row', { dataset: { state: t.state } },
        el('div.tm-info', time, el('span.tm-label', t.label || formatDuration(t.durationMs))),
        el('div.tm-actions', actions(t)),
        el('div.tm-bar', bar));
      rows.set(t.id, { row, time, bar, t, wasRinging: ringing(t) });
      return row;
    }));
    tick();
  }

  function tick() {
    for (const r of rows.values()) {
      const t = r.t;
      const rem = remaining(t);
      const ring = ringing(t);
      if (ring !== r.wasRinging) { rebuild(); return; }
      r.time.textContent = ring ? `+${formatDuration(-rem)}` : formatDuration(rem);
      r.bar.style.width = `${Math.max(0, Math.min(100, (1 - rem / t.durationMs) * 100))}%`;
      r.row.classList.toggle('ringing', ring);
      if (ring && -rem < RING_FOR_MS) {
        const last = alerted.get(t.id) || 0;
        if (Date.now() - last > 8000) {
          if (!last && s.jump) ctx.util.toast(`⏰ ${t.label || 'Timer'} is done`, 12000);
          alerted.set(t.id, Date.now());
          if (s.sound) beep();
        }
      }
    }
  }

  const off = col.subscribe((items) => { timers = items; rebuild(); });
  ctx.every(250, tick, { immediate: false });
  return off;
}
