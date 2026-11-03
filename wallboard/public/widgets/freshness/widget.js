// Data freshness: crawler + per-feed + weather status from /api/status.
export function mount(root, ctx) {
  const { el, relTime, hostOf } = ctx.util;
  const s = ctx.settings;
  const dot = el('span.status-dot');
  const btn = el('button.btn.small.fr-refresh', { type: 'button', onclick: refresh }, 'Refresh now');
  const summary = el('div.fr-summary');
  const list = el('ul.fr-list.w-scroll');
  root.append(el('div.w-head', el('span.w-title', dot, ' Data freshness'), btn), summary, list);
  let data = null, stale = false;

  function level(f, interval) {
    if (f.pending) return 'warn';
    const age = Date.now() - Date.parse(f.lastSuccess || 0);
    if (!f.ok) return age < 6 * 3_600_000 ? 'warn' : 'bad';
    return age < interval * 1.6 ? 'ok' : age < 6 * 3_600_000 ? 'warn' : 'bad';
  }

  function render() {
    if (!data) return;
    const c = data.crawler;
    const now = ctx.now();
    const feeds = c.feeds.map((f) => ({ ...f, lvl: level(f, c.intervalMs) }));
    const counts = { ok: 0, warn: 0, bad: 0 };
    feeds.forEach((f) => counts[f.lvl]++);
    const wx = data.weather || [];
    const wxBad = wx.filter((w) => !w.ok).length;
    const overall = stale ? 'warn' : counts.bad || wxBad ? 'bad' : counts.warn ? 'warn' : 'ok';
    dot.className = `status-dot ${overall}`;
    const failing = feeds.filter((f) => f.ok === false).length;
    summary.replaceChildren(
      el('div', stale ? el('strong.fr-warn', 'Server unreachable — showing saved status') : el('span', 'Server ', el('strong.fr-ok', 'online'))),
      el('div', `Feeds: ${feeds.length - failing} ok`, failing ? el('strong.fr-bad', ` · ${failing} failing`) : ''),
      el('div', c.running ? 'Crawling now…' : `Last crawl ${relTime(c.lastRun?.finishedAt, now)}${c.nextRunAt ? ` · next ${relTime(c.nextRunAt, now)}` : ''}`),
    );
    const rows = [];
    const shown = s.problemsOnly ? feeds.filter((f) => f.lvl !== 'ok') : feeds;
    if (s.showFeeds) {
      shown.sort((a, b) => ({ bad: 0, warn: 1, ok: 2 })[a.lvl] - ({ bad: 0, warn: 1, ok: 2 })[b.lvl] || (a.title || '').localeCompare(b.title || ''));
      for (const f of shown) {
        rows.push(el('li.fr-row', { title: `${f.url}${f.error ? `\n${f.error}` : ''}` },
          el('span.status-dot', { class: f.lvl }),
          el('span.fr-name', f.title || hostOf(f.url)),
          el('span.fr-age', f.pending ? 'queued' : relTime(f.lastCrawled, now)),
          f.error ? el('span.fr-err', f.error) : null));
      }
    }
    for (const w of wx) {
      rows.push(el('li.fr-row', { title: w.error || '' },
        el('span.status-dot', { class: w.ok ? 'ok' : 'bad' }),
        el('span.fr-name', `Weather · ${w.label}`),
        el('span.fr-age', relTime(w.fetchedAt, now)),
        w.error ? el('span.fr-err', w.error) : null));
    }
    if (!rows.length) rows.push(el('li.w-empty', s.problemsOnly ? 'All sources are fresh.' : 'No data sources yet.'));
    list.replaceChildren(...rows);
  }

  async function load() {
    try {
      const r = await ctx.api.getCached('/api/status', 'wb:status');
      data = r.data; stale = r.stale;
    } catch { stale = true; }
    render();
  }

  async function refresh() {
    btn.disabled = true;
    btn.textContent = 'Refreshing…';
    try {
      const r = await ctx.api.post('/api/refresh', {}, { timeout: 120_000 });
      ctx.util.toast(`Refreshed ${r.run.feeds} feeds: ${r.run.ok} ok${r.run.failed ? `, ${r.run.failed} failed` : ''}.`);
    } catch (e) {
      ctx.util.toast(`Refresh failed: ${e.message}`);
    }
    btn.disabled = false;
    btn.textContent = 'Refresh now';
    load();
  }

  ctx.every(60_000, load);
  ctx.every(20_000, render, { immediate: false }); // keep "x min ago" current
  ctx.on('crawl', load);
  ctx.on('connection', load);
}
