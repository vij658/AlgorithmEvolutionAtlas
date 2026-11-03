import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fits, findFreeSpot, placeWidget, normalizeRect, flowSpan, readingOrder } from '../public/js/lib/grid.js';
import { parseDuration, formatDuration } from '../public/js/lib/duration.js';

test('grid placement', () => {
  const ws = [{ id: 'a', x: 0, y: 0, w: 6, h: 4 }];
  assert.equal(fits({ x: 6, y: 0, w: 6, h: 4 }, ws), true);
  assert.equal(fits({ x: 5, y: 0, w: 2, h: 1 }, ws), false);
  assert.equal(fits({ x: 0, y: 0, w: 6, h: 4 }, ws, 'a'), true, 'ignores itself');
  assert.equal(fits({ x: 10, y: 0, w: 3, h: 1 }, ws), false, 'out of bounds');
  assert.deepEqual(findFreeSpot(ws, 3, 2), { x: 6, y: 0, w: 3, h: 2 });
  const full = [{ id: 'f', x: 0, y: 0, w: 12, h: 7 }];
  assert.deepEqual(placeWidget(full, { w: 4, h: 3, minW: 2, minH: 1 }), { x: 0, y: 7, w: 4, h: 1 });
  assert.equal(placeWidget([{ id: 'x', x: 0, y: 0, w: 12, h: 8 }], { w: 2, h: 2 }), null);
  assert.deepEqual(normalizeRect({ x: 11, y: -3, w: 4, h: 99 }), { x: 8, y: 0, w: 4, h: 8 });
  assert.equal(flowSpan(9, 6), 6);
  assert.equal(flowSpan(3, 1), 1);
  assert.equal(flowSpan(4, 6), 3);
  assert.equal(flowSpan(6, 6), 3);
  assert.equal(flowSpan(2, 6), 2);
  assert.deepEqual(readingOrder([{ x: 5, y: 1 }, { x: 0, y: 1 }, { x: 9, y: 0 }]).map((w) => w.x), [9, 0, 5]);
});

test('durations', () => {
  assert.equal(parseDuration('25m'), 25 * 60_000);
  assert.equal(parseDuration('1h'), 3_600_000);
  assert.equal(parseDuration('1h30m'), 5_400_000);
  assert.equal(parseDuration('1:30'), 90_000);
  assert.equal(parseDuration('1:00:00'), 3_600_000);
  assert.equal(parseDuration('90s'), 90_000);
  assert.equal(parseDuration('10'), 600_000, 'bare number = minutes');
  assert.equal(parseDuration('1.5h'), 5_400_000);
  assert.equal(parseDuration('abc'), null);
  assert.equal(parseDuration('0'), null);
  assert.equal(formatDuration(3_661_000), '1:01:01');
  assert.equal(formatDuration(65_000), '1:05');
  assert.equal(formatDuration(400), '0:01', 'rounds up so 0:00 means done');
});
