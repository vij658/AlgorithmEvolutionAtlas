// Duration helpers for timers. Pure functions, shared with tests.

const UNIT = { h: 3_600_000, m: 60_000, s: 1000 };

/**
 * Parse "25m", "1h30m", "1.5h", "90s", "1:30" (m:ss), "1:00:00" (h:mm:ss) or a bare
 * number (minutes). Returns milliseconds, or null if invalid / zero.
 */
export function parseDuration(input) {
  const s = String(input ?? '').trim().toLowerCase().replace(/\s+/g, '');
  if (!s) return null;
  let ms = null;
  if (/^\d+(\.\d+)?$/.test(s)) ms = parseFloat(s) * UNIT.m;
  else if (/^\d+(:\d{1,2}){1,2}$/.test(s)) {
    const parts = s.split(':').map(Number);
    if (parts.slice(1).some((p) => p > 59)) return null;
    ms = parts.length === 3 ? parts[0] * UNIT.h + parts[1] * UNIT.m + parts[2] * UNIT.s : parts[0] * UNIT.m + parts[1] * UNIT.s;
  } else if (/^(\d+(\.\d+)?(h|m|s|min|hr|sec))+$/.test(s)) {
    ms = 0;
    for (const [, n, u] of s.matchAll(/(\d+(?:\.\d+)?)(h|hr|min|m|sec|s)/g)) ms += parseFloat(n) * UNIT[u[0]];
  }
  if (ms == null || !Number.isFinite(ms) || ms <= 0 || ms > 7 * 24 * UNIT.h) return null;
  return Math.round(ms);
}

/** 3661000 -> "1:01:01", 65000 -> "1:05". Rounds up so a running timer never shows 0:00 early. */
export function formatDuration(ms) {
  const neg = ms < 0;
  let t = Math.ceil(Math.abs(ms) / 1000);
  const h = Math.floor(t / 3600); t -= h * 3600;
  const m = Math.floor(t / 60); const s = t - m * 60;
  const ss = String(s).padStart(2, '0');
  return (neg ? '-' : '') + (h ? `${h}:${String(m).padStart(2, '0')}:${ss}` : `${m}:${ss}`);
}

/** Short label for a preset: 3600000 -> "1h", 1500000 -> "25m", 90000 -> "1m30s". */
export function shortLabel(ms) {
  let t = Math.round(ms / 1000);
  const h = Math.floor(t / 3600); t -= h * 3600;
  const m = Math.floor(t / 60); const s = t - m * 60;
  return [h && `${h}h`, m && `${m}m`, s && `${s}s`].filter(Boolean).join('') || '0s';
}
