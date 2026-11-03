// Pure grid helpers shared by the browser and the server (validation, tests).
// The canonical layout is a 12 x 8 grid per page; x/y are 0-based cells.

export const COLS = 12;
export const ROWS = 8;

export function clamp(n, lo, hi) {
  n = Math.round(Number(n));
  if (!Number.isFinite(n)) n = lo;
  return Math.min(hi, Math.max(lo, n));
}

export function overlaps(a, b) {
  return a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h;
}

export function inBounds(r, cols = COLS, rows = ROWS) {
  return r.x >= 0 && r.y >= 0 && r.w >= 1 && r.h >= 1 && r.x + r.w <= cols && r.y + r.h <= rows;
}

/** True if `rect` fits in the grid without overlapping any widget other than `ignoreId`. */
export function fits(rect, widgets, ignoreId = null, cols = COLS, rows = ROWS) {
  if (!inBounds(rect, cols, rows)) return false;
  return !widgets.some((w) => w.id !== ignoreId && overlaps(rect, w));
}

/** First free top-left position for a w x h rectangle (row-major), or null. */
export function findFreeSpot(widgets, w, h, cols = COLS, rows = ROWS) {
  for (let y = 0; y + h <= rows; y++) {
    for (let x = 0; x + w <= cols; x++) {
      if (fits({ x, y, w, h }, widgets, null, cols, rows)) return { x, y, w, h };
    }
  }
  return null;
}

/**
 * Find a spot for a new widget: try the preferred size, then progressively smaller
 * sizes down to the minimum. Returns {x,y,w,h} or null when the page is full.
 */
export function placeWidget(widgets, size = {}) {
  const w0 = clamp(size.w ?? 3, 1, COLS), h0 = clamp(size.h ?? 2, 1, ROWS);
  const minW = clamp(size.minW ?? 1, 1, w0), minH = clamp(size.minH ?? 1, 1, h0);
  const sizes = [];
  for (let w = minW; w <= w0; w++) for (let h = minH; h <= h0; h++) sizes.push([w, h]);
  // Largest area first; among equals prefer the preferred aspect ratio.
  const aspect = w0 / h0;
  sizes.sort((a, b) => b[0] * b[1] - a[0] * a[1] || Math.abs(a[0] / a[1] - aspect) - Math.abs(b[0] / b[1] - aspect));
  for (const [w, h] of sizes) {
    const spot = findFreeSpot(widgets, w, h);
    if (spot) return spot;
  }
  return null;
}

/** Sort widgets in reading order (used for the flowing phone / portrait layouts). */
export function readingOrder(widgets) {
  return [...widgets].sort((a, b) => a.y - b.y || a.x - b.x);
}

/** Column span of a widget when the page is reflowed into `cols` columns. */
export function flowSpan(w, cols) {
  if (cols >= COLS) return w;
  if (cols === 1) return 1;
  // Reflow into halves (or thirds for tiny widgets) so cards pair up neatly.
  if (w > COLS / 2) return cols;
  if (w <= 2) return Math.max(1, Math.round(cols / 3));
  return Math.max(1, Math.round(cols / 2));
}

/** Normalise a widget rectangle from untrusted input. */
export function normalizeRect(r, sizeLimits = {}) {
  const minW = sizeLimits.minW ?? 1, minH = sizeLimits.minH ?? 1;
  const maxW = Math.min(sizeLimits.maxW ?? COLS, COLS), maxH = Math.min(sizeLimits.maxH ?? ROWS, ROWS);
  const w = clamp(r.w, minW, maxW), h = clamp(r.h, minH, maxH);
  return { x: clamp(r.x, 0, COLS - w), y: clamp(r.y, 0, ROWS - h), w, h };
}
