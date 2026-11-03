// Renders public/icons/icon.svg to the PNG sizes that iOS / Android / Fire TV want.
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const svg = readFileSync(new URL('../public/icons/icon.svg', import.meta.url), 'utf8');
const out = (n) => new URL(`../public/icons/${n}`, import.meta.url).pathname;
const browser = await chromium.launch();
const page = await browser.newPage();
for (const [name, size, pad, bg] of [
  ['icon-192.png', 192, 0, 'transparent'], ['icon-512.png', 512, 0, 'transparent'],
  ['apple-touch-icon.png', 180, 0, '#05080d'], ['maskable-512.png', 512, 0.12, '#05080d'],
]) {
  await page.setViewportSize({ width: size, height: size });
  const inner = Math.round(size * (1 - pad * 2));
  await page.setContent(`<body style="margin:0;background:${bg};display:grid;place-items:center;width:${size}px;height:${size}px">
    <div style="width:${inner}px;height:${inner}px">${svg.replace('<svg ', `<svg width="${inner}" height="${inner}" `)}</div></body>`);
  await page.screenshot({ path: out(name), omitBackground: bg === 'transparent' });
}
await browser.close();
console.log('icons written');
