// News: merged headlines from the server's feed cache (/api/news).
export function mount(root, ctx) {
  const { el, relTime, hostOf } = ctx.util;
  const s = ctx.settings;
  const field = (k) => ctx.manifest.settings.find((f) => f.key === k);
  let feeds = (s.feeds || []).filter(Boolean);
  if (!feeds.length) {
    const label = field('topic').options.find((o) => o.value === s.topic)?.label;
    feeds = field('feeds').presets[label] || [];
  }
  const qs = feeds.map((f) => `feed=${encodeURIComponent(f)}`).join('&') + `&limit=${Number(s.maxItems) || 40}&maxAgeHours=${Number(s.maxAgeHours) || 0}`;
  const url = `/api/news?${qs}`;

  const meta = el('span.w-meta');
  const list = el('ol.nw-list.w-scroll');
  const status = el('div.nw-status');
  root.append(el('div.w-head', el('span.w-title', s.title || 'News'), meta), list, status);
  root.classList.toggle('no-summary', !s.showSummary);

  let lastLoad = 0;
  let retry = null;
  async function load() {
    clearTimeout(retry);
    if (!feeds.length) { list.replaceChildren(el('li.w-empty', 'No feeds configured. Add some in edit mode.')); return; }
    try {
      const { data, stale } = await ctx.api.getCached(url, `wb:news:${ctx.id}`);
      lastLoad = Date.now();
      render(data, stale);
      if (data.pending) retry = setTimeout(load, 4000); // new feeds are being fetched right now
    } catch (e) {
      list.replaceChildren(el('li.w-empty', `Could not load news: ${e.message}`));
    }
  }

  function render(d, stale) {
    const failing = d.feeds.filter((f) => f.ok === false);
    const pending = d.feeds.filter((f) => f.pending);
    const newest = d.feeds.map((f) => f.lastCrawled).filter(Boolean).sort().pop();
    meta.textContent = `${d.feeds.length} feed${d.feeds.length === 1 ? '' : 's'}`;
    status.replaceChildren(...[
      el('span.status-dot', { class: stale ? 'warn' : failing.length === d.feeds.length && d.feeds.length ? 'bad' : failing.length ? 'warn' : 'ok' }),
      el('span', stale ? `Offline — saved headlines` : pending.length ? `Fetching ${pending.length} new feed(s)…` : `Updated ${relTime(newest, ctx.now())}`),
      failing.length ? el('span.nw-fail', { title: failing.map((f) => `${f.title || hostOf(f.url)}: ${f.error}`).join('\n') }, ` · ${failing.length} failing`) : null,
    ].filter(Boolean));
    if (!d.items.length) {
      list.replaceChildren(el('li.w-empty', pending.length ? 'Fetching headlines…' : failing.length ? 'No headlines — the feeds could not be fetched. See Data freshness.' : 'No recent headlines.'));
      return;
    }
    list.replaceChildren(...d.items.map((it, i) => {
      const img = s.showImages && it.image && i < 30 ? el('img.nw-img', { src: it.image, alt: '', loading: 'lazy', decoding: 'async', referrerPolicy: 'no-referrer', onerror: (e) => e.target.remove() }) : null;
      const inner = [
        img,
        el('div.nw-text',
          el('div.nw-title', it.title),
          el('div.nw-meta', el('span.nw-src', it.source || hostOf(it.link)), it.published ? ` · ${relTime(it.published, ctx.now())}` : ''),
          s.showSummary && it.summary && it.summary !== it.title ? el('div.nw-sum', it.summary) : null),
      ];
      const open = s.openLinks && it.link && !ctx.tv;
      return el('li.nw-item', { class: img ? 'has-img' : '' }, open
        ? el('a.nw-link', { href: it.link, target: '_blank', rel: 'noopener noreferrer', draggable: 'false' }, inner)
        : el('div.nw-link', { tabindex: ctx.tv ? '0' : null }, inner)); // focusable so a TV remote can browse headlines
    }));
  }

  // Auto-scroll: move to the next headline every N seconds, wrap at the end.
  const scrollEvery = s.scrollSeconds == null || s.scrollSeconds === '' ? (ctx.tv ? 10 : 0) : Number(s.scrollSeconds);
  if (scrollEvery > 0) {
    let pausedUntil = 0;
    const pause = () => { pausedUntil = Date.now() + 60_000; };
    list.addEventListener('pointerdown', pause, { passive: true });
    list.addEventListener('wheel', pause, { passive: true });
    list.addEventListener('focusin', pause);
    ctx.every(scrollEvery * 1000, () => {
      if (!ctx.isVisible() || Date.now() < pausedUntil || list.scrollHeight <= list.clientHeight + 4) return;
      const items = [...list.children];
      const next = items.find((li) => li.offsetTop > list.scrollTop + 4);
      const atEnd = list.scrollTop + list.clientHeight >= list.scrollHeight - 4;
      list.scrollTo({ top: atEnd || !next ? 0 : next.offsetTop - list.offsetTop, behavior: 'smooth' });
    }, { immediate: false });
  }

  ctx.every(5 * 60_000, load);
  ctx.on('crawl', () => load());
  ctx.onVisible(() => { if (Date.now() - lastLoad > 2 * 60_000) load(); });
}
