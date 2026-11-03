// Caching proxy for Open-Meteo (no API key needed). Proxying keeps the number of
// upstream calls low when several screens show the same location, lets TVs with odd
// browsers avoid CORS issues, and serves the last good forecast if upstream is down.

const TTL = 15 * 60_000;
const GEO_TTL = 24 * 3_600_000;

export class Weather {
  constructor({ base = 'https://api.open-meteo.com', geoBase = 'https://geocoding-api.open-meteo.com', fetch = globalThis.fetch, now = () => Date.now(), timeoutMs = 12_000 } = {}) {
    Object.assign(this, { base, geoBase, fetchImpl: fetch, now, timeoutMs });
    this.cache = new Map();
    this.geoCache = new Map();
    this.sources = new Map(); // key -> freshness info
  }

  static params(q) {
    const lat = Number(q.get('lat')), lon = Number(q.get('lon'));
    if (!Number.isFinite(lat) || !Number.isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) {
      const e = new Error('lat and lon are required'); e.status = 400; throw e;
    }
    const units = q.get('units') === 'fahrenheit' ? 'fahrenheit' : 'celsius';
    const days = Math.min(10, Math.max(1, Number(q.get('days')) || 5));
    return { lat: +lat.toFixed(2), lon: +lon.toFixed(2), units, days, name: (q.get('name') || '').slice(0, 80) };
  }

  async forecast({ lat, lon, units, days, name }) {
    const key = `${lat},${lon},${units},${days}`;
    const hit = this.cache.get(key);
    if (hit && this.now() - hit.at < TTL) return { ...hit.data, cached: true };
    const url = new URL('/v1/forecast', this.base);
    Object.entries({
      latitude: lat, longitude: lon, timezone: 'auto', forecast_days: days,
      temperature_unit: units, wind_speed_unit: units === 'fahrenheit' ? 'mph' : 'kmh',
      current: 'temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,wind_speed_10m,is_day,precipitation',
      hourly: 'temperature_2m,precipitation_probability,weather_code,is_day',
      daily: 'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset',
    }).forEach(([k, v]) => url.searchParams.set(k, String(v)));
    const label = name || `${lat}, ${lon}`;
    try {
      const res = await this.fetchImpl(url, { signal: AbortSignal.timeout(this.timeoutMs) });
      if (!res.ok) throw new Error(`Open-Meteo HTTP ${res.status}`);
      const raw = await res.json();
      const data = { ...raw, fetchedAt: new Date(this.now()).toISOString(), units };
      this.cache.set(key, { at: this.now(), data });
      this.sources.set(key, { key, label, ok: true, error: null, fetchedAt: data.fetchedAt, lastAttempt: data.fetchedAt });
      return data;
    } catch (err) {
      const msg = err?.name === 'TimeoutError' ? 'Timed out' : String(err?.cause?.code || err?.message || err);
      const prev = this.sources.get(key);
      this.sources.set(key, { key, label, ok: false, error: msg, fetchedAt: prev?.fetchedAt || null, lastAttempt: new Date(this.now()).toISOString() });
      if (hit) return { ...hit.data, stale: true, error: msg };
      const e = new Error(`Weather unavailable: ${msg}`); e.status = 502; throw e;
    }
  }

  async geocode(q) {
    q = String(q || '').trim().slice(0, 100);
    if (q.length < 2) return { results: [] };
    const key = q.toLowerCase();
    const hit = this.geoCache.get(key);
    if (hit && this.now() - hit.at < GEO_TTL) return hit.data;
    const url = new URL('/v1/search', this.geoBase);
    url.searchParams.set('name', q);
    url.searchParams.set('count', '8');
    url.searchParams.set('format', 'json');
    const res = await this.fetchImpl(url, { signal: AbortSignal.timeout(this.timeoutMs) });
    if (!res.ok) { const e = new Error(`Geocoding HTTP ${res.status}`); e.status = 502; throw e; }
    const raw = await res.json();
    const data = {
      results: (raw.results || []).map((r) => ({
        name: r.name, admin1: r.admin1 || '', country: r.country || '', latitude: r.latitude, longitude: r.longitude, timezone: r.timezone || '',
      })),
    };
    this.geoCache.set(key, { at: this.now(), data });
    return data;
  }

  status() { return [...this.sources.values()]; }
}
