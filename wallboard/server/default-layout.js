import { readFileSync } from 'node:fs';

// The news widget's manifest is the single source of truth for the starter feeds.
const newsManifest = JSON.parse(readFileSync(new URL('../public/widgets/news/manifest.json', import.meta.url), 'utf8'));
const topics = newsManifest.settings.find((f) => f.key === 'topic').options;
const presets = newsManifest.settings.find((f) => f.key === 'feeds').presets;
const starter = Object.fromEntries(topics.map((o) => [o.value, { label: o.label, feeds: presets[o.label] || [] }]));

let n = 0;
const id = (p) => `${p}-${(++n).toString(36)}`;

function newsPage(topic) {
  const { label, feeds } = starter[topic];
  return {
    id: `page-${topic}`,
    name: label,
    widgets: [
      { id: id('news'), type: 'news', x: 0, y: 0, w: 9, h: 8, settings: { title: `${label} news`, topic, feeds: [...feeds] } },
      { id: id('clock'), type: 'clock', x: 9, y: 0, w: 3, h: 3, settings: { showDate: true, showSeconds: false } },
      { id: id('weather'), type: 'weather', x: 9, y: 3, w: 3, h: 5, settings: {} },
    ],
  };
}

/** Layout used for a profile that has never been saved. */
export function defaultLayout() {
  n = 0;
  return {
    version: 0,
    pages: [
      {
        id: 'page-home',
        name: 'Home',
        widgets: [
          { id: id('clock'), type: 'clock', x: 0, y: 0, w: 6, h: 3, settings: { showDate: true, showSeconds: true } },
          { id: id('weather'), type: 'weather', x: 6, y: 0, w: 6, h: 3, settings: {} },
          { id: id('timers'), type: 'timers', x: 0, y: 3, w: 4, h: 5, settings: {} },
          { id: id('tasks'), type: 'tasks', x: 4, y: 3, w: 5, h: 5, settings: {} },
          { id: id('fresh'), type: 'freshness', x: 9, y: 3, w: 3, h: 5, settings: {} },
        ],
      },
      newsPage('ai'),
      newsPage('tech'),
      newsPage('stocks'),
      newsPage('sports'),
    ],
  };
}

export const starterFeeds = starter;
