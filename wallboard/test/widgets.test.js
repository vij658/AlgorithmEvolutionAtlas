import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readdirSync, readFileSync, existsSync } from 'node:fs';

const DIR = new URL('../public/widgets/', import.meta.url);
const TYPES = new Set(['text', 'textarea', 'number', 'range', 'boolean', 'select', 'color', 'time', 'list', 'location', 'heading']);

test('every widget folder has a valid manifest, module and styles', () => {
  const dirs = readdirSync(DIR, { withFileTypes: true }).filter((d) => d.isDirectory());
  assert.ok(dirs.length >= 8);
  for (const d of dirs) {
    const m = JSON.parse(readFileSync(new URL(`${d.name}/manifest.json`, DIR), 'utf8'));
    assert.ok(m.name, `${d.name}: name`);
    assert.ok(existsSync(new URL(`${d.name}/${m.module || 'widget.js'}`, DIR)), `${d.name}: module exists`);
    for (const s of m.styles || []) assert.ok(existsSync(new URL(`${d.name}/${s}`, DIR)), `${d.name}: ${s}`);
    const { w, h, minW = 1, minH = 1 } = m.size || {};
    assert.ok(w >= minW && h >= minH && w <= 12 && h <= 8, `${d.name}: size`);
    const keys = new Set();
    for (const f of m.settings || []) {
      assert.ok(TYPES.has(f.type), `${d.name}.${f.key}: unknown type ${f.type}`);
      if (f.type === 'heading') continue;
      assert.ok(f.key && !keys.has(f.key), `${d.name}: duplicate/missing key ${f.key}`);
      keys.add(f.key);
      assert.ok(f.label, `${d.name}.${f.key}: label`);
      if (f.type === 'select') assert.ok(f.options?.some((o) => (o.value ?? o) === f.default), `${d.name}.${f.key}: default is an option`);
    }
    const src = readFileSync(new URL(`${d.name}/${m.module || 'widget.js'}`, DIR), 'utf8');
    assert.match(src, /export (async )?function mount\(/, `${d.name}: exports mount()`);
  }
});

test('news starter feeds exist for every topic and are valid URLs', () => {
  const m = JSON.parse(readFileSync(new URL('news/manifest.json', DIR), 'utf8'));
  const topics = m.settings.find((f) => f.key === 'topic').options;
  const presets = m.settings.find((f) => f.key === 'feeds').presets;
  assert.deepEqual(topics.map((t) => t.label), ['AI', 'Tech', 'Stocks', 'Sports']);
  for (const t of topics) {
    assert.ok(presets[t.label].length >= 3, t.label);
    for (const u of presets[t.label]) assert.match(new URL(u).protocol, /^https:$/);
  }
});
