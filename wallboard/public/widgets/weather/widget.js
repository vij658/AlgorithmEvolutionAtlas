// Weather widget backed by the server's Open-Meteo proxy (/api/weather).
const DEFAULT_LOC = { name: 'New York', lat: 40.71, lon: -74.01 };

// WMO weather interpretation codes -> [label, day icon, night icon]
const WMO = {
  0: ['Clear', '☀️', '🌙'], 1: ['Mainly clear', '🌤️', '🌙'], 2: ['Partly cloudy', '⛅', '☁️'], 3: ['Overcast', '☁️', '☁️'],
  45: ['Fog', '🌫️', '🌫️'], 48: ['Freezing fog', '🌫️', '🌫️'],
  51: ['Light drizzle', '🌦️', '🌧️'], 53: ['Drizzle', '🌦️', '🌧️'], 55: ['Heavy drizzle', '🌧️', '🌧️'],
  56: ['Freezing drizzle', '🌧️', '🌧️'], 57: ['Freezing drizzle', '🌧️', '🌧️'],
  61: ['Light rain', '🌦️', '🌧️'], 63: ['Rain', '🌧️', '🌧️'], 65: ['Heavy rain', '🌧️', '🌧️'],
  66: ['Freezing rain', '🌧️', '🌧️'], 67: ['Freezing rain', '🌧️', '🌧️'],
  71: ['Light snow', '🌨️', '🌨️'], 73: ['Snow', '🌨️', '🌨️'], 75: ['Heavy snow', '❄️', '❄️'], 77: ['Snow grains', '🌨️', '🌨️'],
  80: ['Showers', '🌦️', '🌧️'], 81: ['Showers', '🌧️', '🌧️'], 82: ['Violent showers', '⛈️', '⛈️'],
  85: ['Snow showers', '🌨️', '🌨️'], 86: ['Snow showers', '🌨️', '🌨️'],
  95: ['Thunderstorm', '⛈️', '⛈️'], 96: ['Thunderstorm, hail', '⛈️', '⛈️'], 99: ['Thunderstorm, hail', '⛈️', '⛈️'],
};
const wmo = (code, day = true) => { const w = WMO[code] || ['—', '🌡️', '🌡️']; return { label: w[0], icon: day ? w[1] : w[2] }; };

function pickUnits(u) {
  if (u === 'celsius' || u === 'fahrenheit') return u;
  return /-(US|LR|MM)\b/i.test(navigator.language || '') ? 'fahrenheit' : 'celsius';
}

export function mount(root, ctx) {
  const { el, relTime } = ctx.util;
  const s = ctx.settings;
  const loc = s.location && Number.isFinite(s.location.lat) ? s.location : DEFAULT_LOC;
  const units = pickUnits(s.units);
  const days = Math.min(7, Math.max(1, Number(s.days) || 5));
  const q = `/api/weather?lat=${loc.lat}&lon=${loc.lon}&units=${units}&days=${days}&name=${encodeURIComponent(loc.name || '')}`;
  const body = el('div.wx', el('div.w-empty', 'Loading weather…'));
  root.append(body);
  let lastOk = 0;

  async function load() {
    try {
      const { data, stale } = await ctx.api.getCached(q, `wb:wx:${q}`);
      lastOk = Date.now();
      render(data, stale || data.stale);
    } catch (e) {
      body.replaceChildren(el('div.w-empty', `Weather unavailable. ${e.message || ''}`));
    }
  }

  function render(d, stale) {
    const c = d.current || {};
    const deg = '°';
    const now = wmo(c.weather_code, c.is_day !== 0);
    const windUnit = units === 'fahrenheit' ? 'mph' : 'km/h';
    // Next hours, starting at the current hour.
    const h = d.hourly || { time: [] };
    const curHour = (c.time || '').slice(0, 13);
    let start = Math.max(0, h.time.findIndex((t) => t.slice(0, 13) === curHour));
    const hours = h.time.slice(start, start + 12).map((t, i) => ({
      t, temp: h.temperature_2m[start + i], p: h.precipitation_probability?.[start + i], ...wmo(h.weather_code[start + i], h.is_day?.[start + i] !== 0),
    }));
    const dd = d.daily || { time: [] };
    const lo = Math.min(...dd.temperature_2m_min), hi = Math.max(...dd.temperature_2m_max);
    const dayFmt = new Intl.DateTimeFormat(undefined, { weekday: 'short' });
    const hourFmt = new Intl.DateTimeFormat(undefined, { hour: 'numeric' });
    const daily = dd.time.map((t, i) => ({
      name: i === 0 ? 'Today' : dayFmt.format(new Date(t + 'T12:00')),
      min: dd.temperature_2m_min[i], max: dd.temperature_2m_max[i], p: dd.precipitation_probability_max?.[i], ...wmo(dd.weather_code[i]),
    }));
    const r = Math.round;
    body.replaceChildren(...[
      el('div.wx-now',
        el('div.wx-place', el('span.w-title', loc.name || 'Weather'), el('span.w-meta', stale ? `offline · ${relTime(d.fetchedAt, ctx.now())}` : '')),
        el('div.wx-main',
          el('span.wx-icon', { 'aria-hidden': 'true' }, now.icon),
          el('span.wx-temp.tabular', `${r(c.temperature_2m)}${deg}`)),
        el('div.wx-desc', now.label),
        el('div.wx-details', `Feels ${r(c.apparent_temperature)}${deg} · ${r(c.wind_speed_10m)} ${windUnit} · ${r(c.relative_humidity_2m)}%`),
        daily[0] ? el('div.wx-hilo', `H ${r(daily[0].max)}${deg}  L ${r(daily[0].min)}${deg}`) : null),
      s.showHourly && hours.length ? el('div.wx-hours', hours.map((x) => el('div.wx-hour',
        el('span.wx-h-t', hourFmt.format(new Date(x.t))),
        el('span.wx-h-i', x.icon),
        el('span.wx-h-v.tabular', `${r(x.temp)}${deg}`),
        el('span.wx-h-p', x.p ? `${x.p}%` : '')))) : null,
      el('div.wx-days', daily.map((x) => el('div.wx-day',
        el('span.wx-d-n', x.name),
        el('span.wx-d-i', { title: x.label }, x.icon),
        el('span.wx-d-p', x.p ? `${x.p}%` : ''),
        el('span.wx-d-lo.tabular', `${r(x.min)}${deg}`),
        el('span.wx-d-bar', el('i', { style: { left: `${((x.min - lo) / (hi - lo || 1)) * 100}%`, right: `${100 - ((x.max - lo) / (hi - lo || 1)) * 100}%` } })),
        el('span.wx-d-hi.tabular', `${r(x.max)}${deg}`)))),
    ].filter(Boolean));
  }

  ctx.every(15 * 60_000, load);
  ctx.onVisible(() => { if (Date.now() - lastOk > 15 * 60_000) load(); });
}
