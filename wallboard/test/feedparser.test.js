import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { parseFeed, decodeEntities, stripHtml, decodeBody } from '../server/feedparser.js';

const fx = (n) => readFileSync(new URL(`./fixtures/${n}`, import.meta.url), 'utf8');

test('RSS 2.0: entities, CDATA (even containing </item>), dates, images, guid links', () => {
  const f = parseFeed(fx('rss2.xml'), 'https://ai.example.com/feed');
  assert.equal(f.title, 'Fixture AI Daily');
  assert.equal(f.siteLink, 'https://ai.example.com/');
  assert.equal(f.items.length, 3);
  const [a, b, c] = f.items;
  assert.equal(a.title, 'Model “Orion” tops benchmark & leaderboard');
  assert.equal(a.link, 'https://ai.example.com/orion?utm_source=rss');
  assert.equal(a.id, 'ai-1');
  assert.equal(a.published, '2026-11-03T09:30:00.000Z');
  assert.equal(a.author, 'Ada Lovelace');
  assert.equal(a.summary, "The new model was released today. It contains in text.", "CDATA with </item> did not split the item");
  assert.equal(a.image, 'https://cdn.example.com/orion-thumb.jpg');
  assert.equal(b.title, 'Robots learn to fold laundry');
  assert.equal(b.summary, 'Researchers finally solved it.');
  assert.equal(b.published, '2026-11-02T23:00:00.000Z');
  assert.equal(b.image, 'https://cdn.example.com/laundry.png');
  assert.equal(c.link, 'https://ai.example.com/undated', 'permalink guid used as link');
  assert.equal(c.published, null);
});

test('Atom: html titles, relative links, author, image from content', () => {
  const f = parseFeed(fx('atom.xml'), 'https://tech.example.com/feed.atom');
  assert.equal(f.title, 'Fixture Tech Wire');
  assert.equal(f.siteLink, 'https://tech.example.com/');
  assert.equal(f.items[0].title, 'Chipmaker unveils 1nm process');
  assert.equal(f.items[0].link, 'https://tech.example.com/posts/1nm');
  assert.equal(f.items[0].summary, 'Smaller & faster.');
  assert.equal(f.items[0].author, 'Grace Hopper');
  assert.equal(f.items[0].published, '2026-11-03T08:15:00.000Z');
  assert.equal(f.items[1].published, '2026-11-02T11:00:00.000Z', 'falls back to <updated>');
  assert.equal(f.items[1].image, 'https://tech.example.com/b.webp');
});

test('RSS 1.0 / RDF and JSON Feed', () => {
  const r = parseFeed(fx('rdf.xml'));
  assert.equal(r.title, 'Fixture Markets');
  assert.equal(r.items[0].title, 'Stocks rally as rates hold');
  assert.equal(r.items[0].published, '2026-11-03T14:05:00.000Z');
  const j = parseFeed(fx('jsonfeed.json'));
  assert.equal(j.title, 'Fixture JSON');
  assert.equal(j.items[0].summary, 'Hello world');
});

test('rejects HTML pages and garbage', () => {
  assert.throws(() => parseFeed(fx('not-a-feed.html')), /HTML page/);
  assert.throws(() => parseFeed(''), /Empty/);
  assert.throws(() => parseFeed('hello world'), /Not an RSS/);
});

test('charset detection from the XML declaration', () => {
  const bytes = readFileSync(new URL('./fixtures/latin1.xml', import.meta.url));
  const f = parseFeed(decodeBody(bytes, 'application/xml'));
  assert.equal(f.items[0].title, 'München gewinnt Pokal');
});

test('entity and html helpers', () => {
  assert.equal(decodeEntities('&lt;a&gt; &amp;amp; &#x1F600; &#39; &bogus;'), '<a> &amp; 😀 \' &bogus;');
  assert.equal(stripHtml('<p>a<script>x()</script> <b>b</b>&nbsp;c</p>'), 'a b c');
});
