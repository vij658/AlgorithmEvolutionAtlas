// Local stand-in for the internet: serves fixture feeds, a fake Open-Meteo, and a few
// misbehaving endpoints. Used by the test-suite and by the screenshot script so that
// nothing depends on outbound network access.
import http from 'node:http';
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const FIX = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../test/fixtures');

const HEADLINES = {
  ai: ['Open model matches frontier systems on reasoning benchmarks', 'Hospitals pilot AI scribes to cut paperwork', 'New chip promises 5x cheaper inference', 'EU publishes guidance for general-purpose AI models', 'Robotics startup shows household robot folding laundry', 'Researchers find simple trick to reduce hallucinations', 'Weather model built on transformers beats physics baseline', 'Universities add AI literacy to first-year curriculum', 'Speech model now handles 100 languages offline', 'Study: code assistants speed up maintenance work', 'Protein design tool goes open source', 'AI system helps astronomers spot 40 new exoplanets'],
  tech: ['Browser engine ships major speed upgrade', 'Smartphone makers agree on universal repair parts', 'Fusion startup reports record plasma run', 'Satellite internet comes to rural libraries', 'Linux kernel 7.2 released with new scheduler', 'E-ink tablets get color refresh rates fit for video', 'Battery breakthrough doubles e-bike range', 'Open-source office suite passes 100M users', 'City deploys sensor network to predict floods', 'Quantum computer keeps qubits stable for a full minute'],
  stocks: ['Stocks edge higher as rate decision looms', 'Tech shares lead Nasdaq to record close', 'Oil slips on rising inventories', 'Retail earnings beat expectations', 'Treasury yields fall for third straight day', 'Chipmaker guides above estimates, shares jump 8%', 'Gold steadies near all-time high', 'Small caps rally on soft inflation print', 'Dollar weakens against yen', 'Bank stocks climb after stress test results'],
  sports: ['Late goal sends underdogs into the final', 'Marathon record falls in windy conditions', 'Rookie quarterback throws four touchdowns', 'Tennis star advances after five-set thriller', 'Cycling team unveils new aero bike', 'Basketball season tips off with overtime win', 'Swimmer breaks 20-year-old world record', 'Cricket: chase of 350 completed with two balls left', 'Formula 1 title fight goes down to the last race', 'Hockey goalie posts third straight shutout'],
};

function genFeed(topic, n, origin) {
  const list = HEADLINES[topic] || HEADLINES.tech;
  const now = Date.now();
  const items = Array.from({ length: n }, (_, i) => {
    const t = list[i % list.length] + (i >= list.length ? ` (${Math.floor(i / list.length) + 1})` : '');
    const date = new Date(now - (i * 47 + 5) * 60_000).toUTCString();
    return `<item><title>${t}</title><link>${origin}/article/${topic}/${i}</link><guid>${topic}-${i}</guid><pubDate>${date}</pubDate>` +
      `<description>${t}. Fixture summary text describing the story in a sentence or two, as most feeds do.</description></item>`;
  }).join('');
  const label = { ai: 'AI Wire', tech: 'Tech Desk', stocks: 'Market Watcher', sports: 'Sports Center' }[topic] || 'Fixture';
  return `<?xml version="1.0"?><rss version="2.0"><channel><title>${label}</title><link>${origin}/</link>${items}</channel></rss>`;
}

export async function startFixtureServer({ port = 0 } = {}) {
  const hits = new Map();
  const state = { flakyFail: false, weatherFail: false, slowMs: 2000 };
  const server = http.createServer((req, res) => {
    const url = new URL(req.url, 'http://x');
    const p = url.pathname;
    hits.set(p, (hits.get(p) || 0) + 1);
    const origin = `http://${req.headers.host}`;
    const xml = (body, type = 'application/rss+xml; charset=utf-8', extra = {}) => { res.writeHead(200, { 'content-type': type, ...extra }); res.end(body); };
    try {
      if (p.startsWith('/feeds/')) {
        const name = path.basename(p);
        const type = name.endsWith('.json') ? 'application/feed+json' : name.endsWith('.html') ? 'text/html' : name === 'latin1.xml' ? 'application/xml' : 'application/rss+xml; charset=utf-8';
        return xml(readFileSync(path.join(FIX, name)), type);
      }
      if (p.startsWith('/gen/')) {
        const topic = path.basename(p, '.xml');
        return xml(genFeed(topic, Number(url.searchParams.get('n')) || 15, origin));
      }
      if (p === '/etag.xml') {
        if (req.headers['if-none-match'] === '"v1"') { res.writeHead(304, { etag: '"v1"' }); return res.end(); }
        return xml(readFileSync(path.join(FIX, 'rss2.xml')), undefined, { etag: '"v1"' });
      }
      if (p === '/redirect') { res.writeHead(302, { location: '/feeds/atom.xml' }); return res.end(); }
      if (p === '/status/500') { res.writeHead(500); return res.end('boom'); }
      if (p === '/status/404') { res.writeHead(404); return res.end('nope'); }
      if (p === '/slow') { setTimeout(() => xml(readFileSync(path.join(FIX, 'rss2.xml'))), state.slowMs); return; }
      if (p === '/flaky.xml') {
        if (state.flakyFail) { res.writeHead(503); return res.end(); }
        return xml(readFileSync(path.join(FIX, 'rdf.xml')));
      }
      if (p === '/v1/forecast') {
        if (state.weatherFail) { res.writeHead(500); return res.end(); }
        return xml(readFileSync(path.join(FIX, 'weather.json')), 'application/json');
      }
      if (p === '/v1/search') return xml(readFileSync(path.join(FIX, 'geocode.json')), 'application/json');
      res.writeHead(404); res.end();
    } catch (e) {
      res.writeHead(500); res.end(String(e));
    }
  });
  await new Promise((r) => server.listen(port, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}`;
  return {
    base, hits, state, server,
    close: () => new Promise((r) => { server.closeAllConnections?.(); server.close(r); }),
  };
}

// `node scripts/fixture-server.js 9300` runs it standalone for manual testing.
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const f = await startFixtureServer({ port: Number(process.argv[2]) || 9300 });
  console.log(`fixture server on ${f.base}  (try ${f.base}/gen/ai.xml)`);
}
