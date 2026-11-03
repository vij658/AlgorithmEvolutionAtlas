// Builds settings forms from a widget manifest's `settings` array, and a simple
// modal dialog used across the app.
import { el, clone } from './lib/util.js';
import * as api from './api.js';

let openModals = 0;
export const modalOpen = () => openModals > 0;

/** Show a modal. `build(close)` returns the content. Resolves with close(value). */
export function modal(title, build, { wide = false } = {}) {
  return new Promise((resolve) => {
    const prevFocus = document.activeElement;
    let done = false;
    const close = (value) => {
      if (done) return;
      done = true;
      openModals--;
      back.remove();
      document.removeEventListener('keydown', onKey, true);
      prevFocus?.focus?.();
      resolve(value);
    };
    const onKey = (e) => { if (e.key === 'Escape' || e.key === 'GoBack' || e.key === 'BrowserBack') { e.preventDefault(); e.stopPropagation(); close(undefined); } };
    const box = el('div.modal', { role: 'dialog', 'aria-modal': 'true', 'aria-label': title, class: wide ? 'wide' : '' },
      el('header.modal-head', el('h2', title), el('button.icon-btn', { type: 'button', 'aria-label': 'Close', onclick: () => close(undefined) }, '✕')),
      el('div.modal-body', build(close)),
    );
    const back = el('div.modal-back', { onclick: (e) => { if (e.target === back) close(undefined); } }, box);
    document.body.append(back);
    openModals++;
    document.addEventListener('keydown', onKey, true);
    requestAnimationFrame(() => (box.querySelector('[autofocus], input, select, textarea, button:not(.icon-btn)') || box).focus?.());
  });
}

export function confirmDialog(message, { ok = 'OK', danger = false } = {}) {
  return modal('Please confirm', (close) => el('div.confirm',
    el('p', message),
    el('div.form-actions',
      el('button.btn', { type: 'button', onclick: () => close(false) }, 'Cancel'),
      el('button.btn.primary', { type: 'button', class: danger ? 'danger' : '', autofocus: true, onclick: () => close(true) }, ok)),
  )).then((v) => v === true);
}

const isUrl = (s) => { try { const u = new URL(s); return u.protocol === 'http:' || u.protocol === 'https:'; } catch { return false; } };

/** Build field controls. Returns { node, read() -> {values} | throws Error }. */
export function buildFields(fields, values) {
  const readers = [];
  const node = el('div.fields');
  for (const f of fields || []) {
    if (f.type === 'heading') { node.append(el('h3.field-heading', f.label)); continue; }
    const id = `f-${f.key}-${Math.random().toString(36).slice(2, 7)}`;
    const cur = values[f.key] !== undefined ? values[f.key] : clone(f.default);
    const err = el('div.field-error');
    const help = f.help ? el('div.field-help', f.help) : null;
    let control, read;
    switch (f.type) {
      case 'boolean': {
        control = el('input', { type: 'checkbox', id, checked: !!cur });
        read = () => control.checked;
        node.append(el('div.field.field-check', control, el('label', { for: id }, f.label), help, err));
        readers.push([f, () => read(), err]);
        continue;
      }
      case 'select': {
        const opts = (f.options || []).map((o) => (typeof o === 'object' ? o : { value: o, label: String(o) }));
        control = el('select', { id }, opts.map((o) => el('option', { value: String(o.value), selected: String(o.value) === String(cur) }, o.label)));
        read = () => { const o = opts.find((x) => String(x.value) === control.value); return o ? o.value : control.value; };
        break;
      }
      case 'number': {
        control = el('input', { type: 'number', id, value: cur ?? '', min: f.min, max: f.max, step: f.step || 'any', inputmode: 'decimal' });
        read = () => {
          if (control.value === '') { if (f.required) throw new Error('Required'); return f.default === null ? null : f.default ?? null; }
          let n = Number(control.value);
          if (!Number.isFinite(n)) throw new Error('Enter a number');
          if (f.min != null && n < f.min) throw new Error(`Minimum is ${f.min}`);
          if (f.max != null && n > f.max) throw new Error(`Maximum is ${f.max}`);
          return n;
        };
        break;
      }
      case 'range': {
        const out = el('output', String(cur));
        control = el('input', { type: 'range', id, value: cur, min: f.min ?? 0, max: f.max ?? 1, step: f.step ?? 0.01, oninput: () => { out.textContent = control.value; } });
        read = () => Number(control.value);
        node.append(el('div.field', el('label', { for: id }, f.label, ' ', out), control, help, err));
        readers.push([f, () => read(), err]);
        continue;
      }
      case 'color':
        control = el('input', { type: 'color', id, value: cur || '#4f9dff' });
        read = () => control.value;
        break;
      case 'time':
        control = el('input', { type: 'time', id, value: cur || '' });
        read = () => control.value;
        break;
      case 'textarea':
        control = el('textarea', { id, rows: f.rows || 4, placeholder: f.placeholder || '' });
        control.value = cur ?? '';
        read = () => control.value;
        break;
      case 'list': {
        const wrap = el('div.list-field');
        const rows = el('div.list-rows');
        const addRow = (v = '') => {
          const input = el('input', { type: f.itemType === 'url' ? 'url' : 'text', value: v, placeholder: f.placeholder || '', inputmode: f.itemType === 'url' ? 'url' : null, autocapitalize: 'off', spellcheck: false });
          const row = el('div.list-row', input, el('button.icon-btn', { type: 'button', 'aria-label': 'Remove', onclick: () => row.remove() }, '✕'));
          rows.append(row);
          return input;
        };
        (Array.isArray(cur) ? cur : []).forEach((v) => addRow(v));
        const presetBtns = Object.entries(f.presets || {}).map(([label, list]) => el('button.btn.small', { type: 'button', onclick: () => { rows.replaceChildren(); list.forEach((v) => addRow(v)); } }, `Use ${label}`));
        wrap.append(rows, el('div.list-actions',
          el('button.btn.small', { type: 'button', onclick: () => addRow().focus() }, `＋ ${f.itemLabel || 'Add'}`),
          presetBtns));
        control = wrap;
        read = () => {
          const vals = [...rows.querySelectorAll('input')].map((i) => i.value.trim()).filter(Boolean);
          if (f.itemType === 'url') {
            const bad = vals.find((v) => !isUrl(v));
            if (bad) throw new Error(`Not a valid http(s) URL: ${bad}`);
          }
          if (f.max && vals.length > f.max) throw new Error(`At most ${f.max} entries`);
          return vals;
        };
        break;
      }
      case 'location': {
        const v = cur || {};
        const name = el('input', { type: 'text', value: v.name || '', placeholder: 'City, e.g. Berlin' });
        const lat = el('input', { type: 'number', step: 'any', value: v.lat ?? '', placeholder: 'Latitude', inputmode: 'decimal' });
        const lon = el('input', { type: 'number', step: 'any', value: v.lon ?? '', placeholder: 'Longitude', inputmode: 'decimal' });
        const results = el('div.geo-results');
        const search = async () => {
          results.replaceChildren(el('div.field-help', 'Searching…'));
          try {
            const r = await api.get(`/api/geocode?q=${encodeURIComponent(name.value)}`);
            if (!r.results.length) { results.replaceChildren(el('div.field-help', 'No places found.')); return; }
            results.replaceChildren(...r.results.map((g) => el('button.btn.small', { type: 'button', onclick: () => {
              name.value = [g.name, g.admin1, g.country].filter(Boolean).join(', ');
              lat.value = g.latitude; lon.value = g.longitude; results.replaceChildren();
            } }, [g.name, g.admin1, g.country].filter(Boolean).join(', '))));
          } catch (e) { results.replaceChildren(el('div.field-error', `Search failed: ${e.message}. Enter latitude/longitude instead.`)); }
        };
        const geo = navigator.geolocation && window.isSecureContext ? el('button.btn.small', { type: 'button', onclick: () => {
          navigator.geolocation.getCurrentPosition((p) => { lat.value = p.coords.latitude.toFixed(3); lon.value = p.coords.longitude.toFixed(3); if (!name.value) name.value = 'Here'; },
            (e) => results.replaceChildren(el('div.field-error', e.message)));
        } }, 'Use this device’s location') : null;
        control = el('div.location-field',
          el('div.row', name, el('button.btn.small', { type: 'button', onclick: search }, 'Search')),
          results, el('div.row', lat, lon), geo);
        name.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); search(); } });
        read = () => {
          if (lat.value === '' && lon.value === '') return null;
          const la = Number(lat.value), lo = Number(lon.value);
          if (!Number.isFinite(la) || Math.abs(la) > 90 || !Number.isFinite(lo) || Math.abs(lo) > 180) throw new Error('Latitude must be -90…90 and longitude -180…180');
          return { name: name.value.trim() || `${la.toFixed(2)}, ${lo.toFixed(2)}`, lat: la, lon: lo };
        };
        break;
      }
      default: // text
        control = el('input', { type: 'text', id, value: cur ?? '', placeholder: f.placeholder || '', maxlength: f.maxLength || 200 });
        read = () => {
          const v = control.value.trim();
          if (f.required && !v) throw new Error('Required');
          if (f.pattern && v && !new RegExp(f.pattern).test(v)) throw new Error(f.patternHelp || 'Invalid format');
          return v;
        };
    }
    node.append(el('div.field', el('label', { for: id }, f.label), control, help, err));
    readers.push([f, read, err]);
  }
  return {
    node,
    read() {
      const out = {};
      let ok = true;
      for (const [f, read, err] of readers) {
        err.textContent = '';
        try { out[f.key] = read(); } catch (e) { ok = false; err.textContent = e.message; }
      }
      if (!ok) throw new Error('Please fix the highlighted fields.');
      return out;
    },
  };
}

/** Modal settings form. Resolves with the new values, or undefined if cancelled. */
export function settingsDialog(title, fields, values, { extra } = {}) {
  return modal(title, (close) => {
    const f = buildFields(fields, values);
    const status = el('div.field-error');
    const form = el('form.settings-form', {
      onsubmit: (e) => {
        e.preventDefault();
        try { close(f.read()); } catch (err) { status.textContent = err.message; }
      },
    },
    fields?.length ? f.node : el('p.field-help', 'This widget has no settings.'),
    extra || null,
    status,
    el('div.form-actions',
      el('button.btn', { type: 'button', onclick: () => close(undefined) }, 'Cancel'),
      el('button.btn.primary', { type: 'submit' }, 'Save')));
    return form;
  }, { wide: true });
}
