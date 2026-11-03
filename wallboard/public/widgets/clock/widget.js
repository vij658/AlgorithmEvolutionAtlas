// Clock widget: big tabular digits sized to fit the card.
export function mount(root, ctx) {
  const { el } = ctx.util;
  const s = ctx.settings;
  let tz = s.timeZone?.trim() || undefined;
  let tzError = '';
  try { new Intl.DateTimeFormat(undefined, { timeZone: tz }); } catch { tzError = `Unknown time zone “${tz}”`; tz = undefined; }
  const hour12 = s.hour12 === 'auto' ? undefined : s.hour12 === '12';
  const timeFmt = new Intl.DateTimeFormat(undefined, { hour: 'numeric', minute: '2-digit', second: s.showSeconds ? '2-digit' : undefined, hour12, timeZone: tz });
  const dateFmt = new Intl.DateTimeFormat(undefined, { weekday: 'long', month: 'long', day: 'numeric', timeZone: tz });
  const shortFmt = new Intl.DateTimeFormat(undefined, { weekday: 'short', month: 'short', day: 'numeric', timeZone: tz });

  const time = el('div.clk-time.tabular');
  const date = el('div.clk-date');
  const label = s.label || (tz ? tz.split('/').pop().replace(/_/g, ' ') : '');
  root.append(el('div.clk', label ? el('div.w-title.clk-label', label) : null, time, s.showDate ? date : null, tzError ? el('div.widget-error', tzError) : null));
  root.classList.toggle('with-date', !!s.showDate);
  root.classList.toggle('with-label', !!label);

  let lastText = '';
  function render() {
    const d = new Date(ctx.now());
    const parts = timeFmt.formatToParts(d);
    const text = parts.map((p) => p.value).join('');
    if (text === lastText) return;
    lastText = text;
    // Size the digits to the card: roughly 0.62em per character in tabular numerals.
    const chars = parts.filter((p) => p.type !== 'dayPeriod' && p.type !== 'literal').map((p) => p.value).join('').length + parts.filter((p) => p.type === 'literal' && p.value.trim()).length * 0.45 + (parts.some((p) => p.type === 'dayPeriod') ? 1.3 : 0);
    time.style.setProperty('--fit', (100 / (chars * 0.62)).toFixed(2));
    time.replaceChildren(...parts.map((p) => {
      if (p.type === 'dayPeriod') return el('span.clk-ampm', p.value.trim());
      if (p.type === 'second') return el('span.clk-sec', p.value);
      if (p.type === 'literal' && p.value.trim() === '') return '';
      if (p.type === 'literal') return el('span.clk-colon', p.value);
      return p.value;
    }));
    date.replaceChildren(el('span.clk-long', dateFmt.format(d)), el('span.clk-short', shortFmt.format(d)));
  }

  // Tick on the second boundary so seconds never skip or lag.
  let timer;
  const tick = () => { render(); timer = setTimeout(tick, 1000 - (ctx.now() % 1000) + 5); };
  tick();
  return () => clearTimeout(timer);
}
