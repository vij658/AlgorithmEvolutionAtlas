// Date widget: weekday, big day number, month (and year / ISO week).
function isoWeek(y, m, d) {
  const t = new Date(Date.UTC(y, m, d));
  const day = t.getUTCDay() || 7;
  t.setUTCDate(t.getUTCDate() + 4 - day);
  const y0 = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  return Math.ceil(((t - y0) / 86400000 + 1) / 7);
}

export function mount(root, ctx) {
  const { el } = ctx.util;
  const s = ctx.settings;
  let tz = s.timeZone?.trim() || undefined;
  try { new Intl.DateTimeFormat(undefined, { timeZone: tz }); } catch { tz = undefined; }
  const parts = (d, o) => Object.fromEntries(new Intl.DateTimeFormat(undefined, { ...o, timeZone: tz }).formatToParts(d).map((p) => [p.type, p.value]));
  const wd = el('div.dt-weekday'), day = el('div.dt-day.tabular'), month = el('div.dt-month'), extra = el('div.dt-extra');
  root.append(el('div.dt', wd, day, month, extra));
  let last = '';
  ctx.every(15_000, () => {
    const d = new Date(ctx.now());
    const p = parts(d, { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' });
    const n = parts(d, { year: 'numeric', month: 'numeric', day: 'numeric' });
    const key = `${p.weekday}${p.day}${p.month}${p.year}`;
    if (key === last) return;
    last = key;
    wd.textContent = p.weekday;
    day.textContent = p.day;
    month.textContent = s.showYear ? `${p.month} ${p.year}` : p.month;
    extra.textContent = s.showWeek ? `Week ${isoWeek(+n.year, +n.month - 1, +n.day)}` : '';
  });
}
