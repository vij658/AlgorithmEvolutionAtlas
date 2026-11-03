import { readFileSync } from 'node:fs';
import { createApp } from './app.js';

const port = Number(process.env.PORT || 8080);
const host = process.env.HOST || '0.0.0.0';
let tls = null;
if (process.env.TLS_CERT && process.env.TLS_KEY) {
  tls = { cert: readFileSync(process.env.TLS_CERT), key: readFileSync(process.env.TLS_KEY) };
}

const app = await createApp({ tls });
const addr = await app.listen(port, host);
app.crawler.start();
console.log(`[wallboard] listening on ${tls ? 'https' : 'http'}://${host}:${addr.port} (data: ${process.env.DATA_DIR || 'data/'})`);
console.log(`[wallboard] crawling ${app.crawler.wantedFeeds().length} feeds every ${app.crawler.intervalMs / 60000} min; next run ${app.crawler.nextRunAt}`);

let stopping = false;
for (const sig of ['SIGINT', 'SIGTERM']) {
  process.on(sig, async () => {
    if (stopping) return;
    stopping = true;
    console.log(`[wallboard] ${sig}, shutting down`);
    const t = setTimeout(() => process.exit(1), 5000);
    t.unref();
    await app.close().catch(() => {});
    process.exit(0);
  });
}
