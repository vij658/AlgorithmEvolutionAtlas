// Dependency-free, tolerant parser for RSS 2.0, RSS 1.0 (RDF), Atom and JSON Feed.
// It is not a general XML parser: it extracts the handful of fields a dashboard needs
// and survives the malformed markup that real-world feeds tend to contain.

const NAMED = {
  amp: '&', lt: '<', gt: '>', quot: '"', apos: "'", nbsp: ' ', ndash: '–', mdash: '—',
  lsquo: '‘', rsquo: '’', ldquo: '“', rdquo: '”', hellip: '…', bull: '•', middot: '·',
  copy: '©', reg: '®', trade: '™', euro: '€', pound: '£', yen: '¥', cent: '¢', deg: '°',
  times: '×', divide: '÷', laquo: '«', raquo: '»', eacute: 'é', egrave: 'è', aacute: 'á',
  agrave: 'à', ouml: 'ö', uuml: 'ü', auml: 'ä', szlig: 'ß', ntilde: 'ñ', ccedil: 'ç', iacute: 'í',
  oacute: 'ó', uacute: 'ú', Eacute: 'É', Ouml: 'Ö', Uuml: 'Ü', Auml: 'Ä', shy: '',
};

export function decodeEntities(s) {
  if (!s || s.indexOf('&') === -1) return s || '';
  return s.replace(/&(#x[0-9a-f]+|#\d+|[a-z][a-z0-9]*);/gi, (m, e) => {
    if (e[0] === '#') {
      const cp = e[1] === 'x' || e[1] === 'X' ? parseInt(e.slice(2), 16) : parseInt(e.slice(1), 10);
      if (!Number.isFinite(cp) || cp <= 0 || cp > 0x10ffff) return m;
      try { return String.fromCodePoint(cp); } catch { return m; }
    }
    return NAMED[e] ?? NAMED[e.toLowerCase()] ?? m;
  });
}

export function stripHtml(html) {
  if (!html) return '';
  return decodeEntities(
    html
      .replace(/<(script|style|iframe|noscript)[\s\S]*?<\/\1\s*>/gi, ' ')
      .replace(/<br\s*\/?>|<\/p>|<\/div>|<\/li>/gi, ' ')
      .replace(/<[^>]*>/g, ' '),
  ).replace(/\s+/g, ' ').trim();
}

function truncate(s, n) {
  if (s.length <= n) return s;
  const cut = s.slice(0, n);
  const sp = cut.lastIndexOf(' ');
  return (sp > n * 0.6 ? cut.slice(0, sp) : cut).replace(/[\s,.;:–-]+$/, '') + '…';
}

function escapeRe(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

/** Parse XML attributes from the inside of a start tag. */
export function parseAttrs(src) {
  const out = {};
  if (!src) return out;
  const re = /([\w:.-]+)\s*=\s*("([^"]*)"|'([^']*)')/g;
  let m;
  while ((m = re.exec(src))) out[m[1].toLowerCase()] = decodeEntities(m[3] ?? m[4] ?? '');
  return out;
}

class Doc {
  constructor(xml) {
    this.cdata = [];
    // Protect CDATA sections (they may contain anything, even "</item>"), drop comments,
    // processing instructions and doctype.
    this.xml = xml
      .replace(/<!\[CDATA\[([\s\S]*?)\]\]>/g, (_, c) => `\u0000${this.cdata.push(c) - 1}\u0000`)
      .replace(/<!--[\s\S]*?-->/g, '')
      .replace(/<\?[\s\S]*?\?>/g, '')
      .replace(/<!DOCTYPE[^>[]*(\[[\s\S]*?\])?\s*>/gi, '');
  }

  /** All elements named `name` (with or without namespace prefix) in `src`. */
  all(src, name) {
    const n = escapeRe(name);
    const re = new RegExp(`<(${n})((?:\\s[^>]*?)?)(?:/>|>([\\s\\S]*?)</\\1\\s*>)`, 'gi');
    const res = [];
    let m;
    while ((m = re.exec(src))) {
      // Guard against prefix matches like <link> matching <linkfoo>: the regex requires
      // whitespace, '/' or '>' after the name, which is ensured by the group pattern.
      res.push({ attrs: parseAttrs(m[2]), inner: m[3] ?? '', raw: m[0] });
    }
    return res;
  }

  first(src, ...names) {
    for (const name of names) {
      const r = this.all(src, name);
      if (r.length) return r[0];
    }
    return null;
  }

  /** Text content: CDATA verbatim, everything else entity-decoded. */
  text(inner) {
    if (!inner) return '';
    let out = '';
    const parts = inner.split(/\u0000(\d+)\u0000/);
    for (let i = 0; i < parts.length; i++) {
      out += i % 2 ? this.cdata[+parts[i]] : decodeEntities(parts[i]);
    }
    return out.trim();
  }

  textOf(src, ...names) {
    const el = this.first(src, ...names);
    return el ? this.text(el.inner) : '';
  }
}

function parseDate(s) {
  if (!s) return null;
  let t = Date.parse(s.trim());
  if (Number.isNaN(t)) {
    // Common broken forms: missing comma, two-digit years, "UT" zone.
    const fixed = s.trim().replace(/\bUT\b/, 'UTC').replace(/^(\w{3})\s+(\d)/, '$1, $2');
    t = Date.parse(fixed);
  }
  return Number.isNaN(t) ? null : new Date(t).toISOString();
}

function absUrl(u, base) {
  if (!u) return '';
  try { return new URL(u.trim(), base || undefined).href; } catch { return /^https?:\/\//i.test(u) ? u.trim() : ''; }
}

function firstImg(html) {
  const m = /<img\b[^>]*?\bsrc\s*=\s*("([^"]+)"|'([^']+)')/i.exec(html || '');
  return m ? decodeEntities(m[2] || m[3]) : '';
}

function hash(s) {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return (h >>> 0).toString(36);
}

function finalizeItem(it, base) {
  const title = truncate(stripHtml(it.title) || '(untitled)', 300);
  const link = absUrl(it.link, base);
  const summary = truncate(stripHtml(it.summary), 400);
  const image = absUrl(it.image, link || base);
  return {
    id: it.id || link || hash(title + (it.published || '')),
    title,
    link,
    published: it.published,
    summary,
    image: /^https?:/i.test(image) ? image : '',
    author: truncate(stripHtml(it.author), 80),
  };
}

function imageFrom(doc, src, htmlFallback) {
  for (const t of doc.all(src, 'media:thumbnail')) if (t.attrs.url) return t.attrs.url;
  for (const c of doc.all(src, 'media:content')) {
    if (c.attrs.url && (c.attrs.medium === 'image' || /^image\//.test(c.attrs.type || '') || /\.(jpe?g|png|webp|gif)(\?|$)/i.test(c.attrs.url))) return c.attrs.url;
    const nested = doc.first(c.inner, 'media:thumbnail');
    if (nested?.attrs.url) return nested.attrs.url;
  }
  for (const e of doc.all(src, 'enclosure')) if (e.attrs.url && /^image\//.test(e.attrs.type || '')) return e.attrs.url;
  const itunes = doc.first(src, 'itunes:image');
  if (itunes?.attrs.href) return itunes.attrs.href;
  return firstImg(htmlFallback);
}

function parseRss(doc, baseUrl) {
  const xml = doc.xml;
  const channel = doc.first(xml, 'channel');
  const chanSrc = channel ? channel.inner.replace(/<item[\s>][\s\S]*$/i, '') : '';
  const title = stripHtml(doc.textOf(chanSrc, 'title'));
  const siteLink = absUrl(doc.textOf(chanSrc, 'link'), baseUrl);
  const items = doc.all(xml, 'item').map(({ inner }) => {
    const content = doc.textOf(inner, 'content:encoded');
    const description = doc.textOf(inner, 'description');
    const guidEl = doc.first(inner, 'guid');
    const guid = guidEl ? doc.text(guidEl.inner) : '';
    let link = doc.textOf(inner, 'link');
    if (!link) {
      const atomLink = doc.first(inner, 'atom:link');
      link = atomLink?.attrs.href || '';
    }
    if (!link && /^https?:\/\//i.test(guid) && guidEl?.attrs.ispermalink !== 'false') link = guid;
    return finalizeItem({
      id: guid || '',
      title: doc.textOf(inner, 'title'),
      link,
      published: parseDate(doc.textOf(inner, 'pubDate', 'dc:date', 'published', 'updated')),
      summary: description || content,
      image: imageFrom(doc, inner, content || description),
      author: doc.textOf(inner, 'dc:creator', 'author'),
    }, siteLink || baseUrl);
  });
  return { title, siteLink, items };
}

function atomLink(doc, src) {
  const links = doc.all(src, 'link');
  const alt = links.find((l) => (!l.attrs.rel || l.attrs.rel === 'alternate') && l.attrs.href);
  return (alt || links.find((l) => l.attrs.href))?.attrs.href || '';
}

function parseAtom(doc, baseUrl) {
  const xml = doc.xml;
  const head = xml.replace(/<entry[\s>][\s\S]*$/i, '');
  const title = stripHtml(doc.textOf(head, 'title'));
  const siteLink = absUrl(atomLink(doc, head), baseUrl);
  const items = doc.all(xml, 'entry').map(({ inner }) => {
    const content = doc.textOf(inner, 'content');
    const summary = doc.textOf(inner, 'summary') || content || doc.textOf(inner, 'media:description');
    const authorEl = doc.first(inner, 'author');
    return finalizeItem({
      id: doc.textOf(inner, 'id'),
      title: doc.textOf(inner, 'title'),
      link: atomLink(doc, inner),
      published: parseDate(doc.textOf(inner, 'published', 'updated', 'dc:date')),
      summary,
      image: imageFrom(doc, inner, content || summary),
      author: authorEl ? doc.textOf(authorEl.inner, 'name') : '',
    }, siteLink || baseUrl);
  });
  return { title, siteLink, items };
}

function parseJsonFeed(text, baseUrl) {
  const j = JSON.parse(text);
  if (!j || !Array.isArray(j.items) || !String(j.version || '').includes('jsonfeed')) {
    throw new Error('Not a JSON Feed');
  }
  const siteLink = absUrl(j.home_page_url, baseUrl);
  return {
    title: stripHtml(j.title || ''),
    siteLink,
    items: j.items.map((it) => finalizeItem({
      id: String(it.id ?? ''),
      title: it.title || it.content_text?.slice(0, 120) || '',
      link: it.url || it.external_url,
      published: parseDate(it.date_published || it.date_modified),
      summary: it.summary || it.content_text || it.content_html || '',
      image: it.image || it.banner_image || firstImg(it.content_html),
      author: it.authors?.[0]?.name || it.author?.name || '',
    }, siteLink || baseUrl)),
  };
}

/**
 * Parse feed text. Returns { title, siteLink, items[] }. Throws on input that is
 * clearly not a feed (HTML pages, error documents, empty bodies).
 */
export function parseFeed(text, baseUrl = '') {
  if (typeof text !== 'string' || !text.trim()) throw new Error('Empty response');
  const head = text.trimStart().slice(0, 2048);
  if (head[0] === '{') return parseJsonFeed(text, baseUrl);
  const doc = new Doc(text);
  const root = doc.xml.trimStart().slice(0, 4096);
  if (/<feed[\s>]/i.test(root)) return parseAtom(doc, baseUrl);
  if (/<(rss|rdf:RDF)[\s>]/i.test(root) || /<channel[\s>]/i.test(root)) return parseRss(doc, baseUrl);
  if (/<html[\s>]/i.test(root)) throw new Error('Got an HTML page, not a feed');
  throw new Error('Not an RSS/Atom feed');
}

/** Pick a charset from Content-Type or the XML declaration. */
export function detectCharset(contentType, bytes) {
  const m = /charset\s*=\s*"?([\w.:-]+)/i.exec(contentType || '');
  if (m) return m[1].toLowerCase();
  const head = Buffer.from(bytes.subarray(0, 200)).toString('latin1');
  const x = /<\?xml[^>]*encoding\s*=\s*["']([\w.:-]+)["']/i.exec(head);
  return x ? x[1].toLowerCase() : 'utf-8';
}

export function decodeBody(bytes, contentType) {
  const cs = detectCharset(contentType, bytes);
  try { return new TextDecoder(cs).decode(bytes); } catch { return new TextDecoder('utf-8').decode(bytes); }
}
