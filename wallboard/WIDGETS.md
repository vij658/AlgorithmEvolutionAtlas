# Writing your own widget

A widget is **a folder with two files**: `manifest.json` (what it is, how big, which settings) and an ES module (what it draws). No build step and no npm.

```
public/widgets/hello/
├── manifest.json
├── widget.js
└── style.css        (optional)
```

The quickest start is to copy the template:

```bash
cp -r public/widgets/_template public/widgets/hello
```

Reload the screen, enter edit mode, tap **＋ Widget**, and "My widget" is in the palette. Folders whose names start with `_` are ignored, which is why the template itself doesn't show up.

**On the NAS** you don't need to rebuild the image: put the folder in the data volume as `/data/widgets/hello/` (for example `/volume1/docker/wallboard/widgets/hello/`). The server lists and serves widgets from there too. A custom folder with the same name as a built-in widget replaces the built-in one.

The folder name is the widget's **type**. Use lowercase `a-z`, `0-9`, `-` and `_`.

## manifest.json

```json
{
  "name": "Hello",
  "description": "Shown in the palette.",
  "icon": "✨",
  "order": 50,
  "module": "widget.js",
  "styles": ["style.css"],
  "configureOnAdd": false,
  "size": { "w": 3, "h": 2, "minW": 2, "minH": 1, "maxW": 12, "maxH": 8, "phoneH": 3 },
  "settings": [
    { "key": "message", "type": "text", "label": "Message", "default": "Hello, wall!" }
  ]
}
```

| Field | Meaning |
|---|---|
| `name`, `description`, `icon` | Shown in the palette. |
| `order` | Position in the palette (lower comes first). |
| `module` | The JS file. Defaults to `widget.js`. |
| `styles` | CSS files to load once. |
| `configureOnAdd` | Open the settings form right after the widget is added. |
| `size` | Default `w`×`h` in grid cells (a page is 12 × 8), limits for resizing, and `phoneH`, the minimum height in rows on phones. |
| `settings` | The settings form. Edit mode builds it automatically. |

### Setting types

Every setting has `key`, `type`, `label`, an optional `default` and an optional `help`.

| `type` | Value | Extra fields |
|---|---|---|
| `text` | string | `placeholder`, `maxLength`, `required`, `pattern` + `patternHelp` |
| `textarea` | string | `rows`, `placeholder` |
| `number` | number (or the default when blank) | `min`, `max`, `step`, `required` |
| `range` | number (slider) | `min`, `max`, `step` |
| `boolean` | true / false | |
| `select` | one of the option values | `options`: `["a","b"]` or `[{ "value": 1, "label": "One" }]` |
| `color` | `#rrggbb` | |
| `time` | `"HH:MM"` | |
| `list` | array of strings | `itemType: "url"` (validates http/https), `itemLabel`, `placeholder`, `max`, `presets: { "Label": [values] }` (adds "Use Label" buttons) |
| `location` | `{ name, lat, lon }` or null | Includes city search (Open-Meteo geocoding) and "use this device's location" |
| `heading` | none | A section title in the form. Needs only `label`. |

Any widget whose settings include a `feeds` list of URLs gets those feeds crawled hourly by the server, so you can build a different kind of news display without touching the server.

## widget.js

```js
export function mount(root, ctx) {
  const { el } = ctx.util;
  root.append(el('div.w-title', ctx.settings.message));
  const stop = ctx.every(1000, () => { /* tick */ });
  return () => { /* optional cleanup; ctx.every / ctx.on are cleaned up for you */ };
}
```

`mount` can be `async`. It is called once per widget instance. When the user saves new settings, the widget is unmounted and mounted again. Errors thrown from `mount` appear inside the card instead of breaking the board.

`root` fills the card and has the class `w-<type>`. The card is a CSS **size container**, so you can use `cqw` / `cqh` / `cqmin` units and `@container` queries to fit any card size (see the clock and weather styles).

### ctx

| Member | What it does |
|---|---|
| `ctx.settings` | Manifest defaults merged with this instance's saved settings. |
| `ctx.id`, `ctx.type`, `ctx.manifest` | Identity and the parsed manifest. |
| `ctx.tv` | `true` in TV mode: bigger type, D-pad navigation. Make things focusable (`tabindex="0"` or buttons) so a remote can reach them. |
| `ctx.every(ms, fn, { immediate = true })` | `setInterval` that is cleared on unmount. |
| `ctx.on(event, fn)` | Server events: `'crawl'` (feeds were fetched), `'change'` (a layout or collection changed), `'connection'` (`{ online }`). Unsubscribed on unmount. |
| `ctx.onVisible(fn)`, `ctx.isVisible()` | Runs when this widget's page becomes the current page, and reports whether it is. Use them to refresh lazily. |
| `ctx.collection(name)` | A **live synced list**: `.items`, `.get(id)`, `.add(obj)`, `.update(id, patch)`, `.remove(id)`, `.subscribe(fn)` (returns an unsubscribe function). It works offline (localStorage plus a write queue), is stored on the server, and pushes to all screens. Prefix the name with your widget type. |
| `ctx.api.get / post / put / patch / del(path, body)` | JSON calls to the Wallboard server. |
| `ctx.api.getCached(path)` | GET that falls back to the last good response while offline. Returns `{ data, stale }`. |
| `ctx.saveSettings(patch)` | Persist small bits of per-instance state into the layout. This does not remount the widget. Don't call it often: every call saves the layout. |
| `ctx.now()` | `Date.now()` corrected to the server clock, so timers agree across screens. |
| `ctx.onCleanup(fn)` | Registers extra cleanup. |
| `ctx.util` | `el()`, `esc()`, `relTime()`, `hostOf()`, `uid()`, `debounce()`, `toast(msg)`, `formatDuration()`, `parseDuration()`, `storage` (a localStorage wrapper that never throws). |

`ctx.util.el('div.cls#id', { onclick, title, style: {...} }, ...children)` creates elements. Strings are added as text and never parsed as HTML, so feed or user content can't inject markup.

### Shared CSS building blocks

These classes are defined in `/css/app.css`: `.w-head`, `.w-title`, `.w-meta` (card header), `.w-scroll` (a scrolling area that fills the remaining height), `.w-empty`, `.btn` (`.primary`, `.small`, `.danger`), `.icon-btn`, `.status-dot` (`.ok`, `.warn`, `.bad`), `.tabular` and `.muted`. Colours are CSS variables such as `--text`, `--muted`, `--accent`, `--card-2`, `--ok`, `--warn` and `--bad`.

Scope your own rules to `.w-<type>`, or to a class you add yourself, so widgets never affect each other.

### Checklist

- It works from 2×1 up to full page; test it with `@container` rules.
- It looks right on black. It's a wall display, so avoid big white areas (burn-in, glare at night).
- It survives the server being offline (`getCached`, collections).
- On TV, controls are reachable with arrow keys.
- `npm test` validates every manifest in `public/widgets` (field types, defaults, the module exporting `mount`).
