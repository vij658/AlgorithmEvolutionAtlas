# Wallboard

An always-on dashboard for an iPad on the wall, a TV with a Fire TV Stick, or a spare phone. It shows a clock, the date, weather, several timers at once, a prioritised task list, news pages (AI, tech, stocks, sports) and a data-freshness tile.

- A **small Node 22 server** with **no npm dependencies**. It crawls your RSS / Atom / JSON feeds every hour, caches them, proxies the weather, and stores pages, widgets, timers and tasks as JSON.
- An **installable PWA** built from vanilla ES modules, with no build step. It has swipeable pages, a 12 × 8 widget grid and an edit mode. Night dimming, keep-awake, burn-in drift, offline cache and a TV mode keep it usable as a permanent display.

| TV (1920 × 1080, `?tv=1`) | iPad landscape | iPad portrait | Phone |
|---|---|---|---|
| ![](docs/screenshots/tv-1-home.png) | ![](docs/screenshots/ipad-landscape-1-home.png) | ![](docs/screenshots/ipad-portrait-1-home.png) | ![](docs/screenshots/phone-1-home.png) |

More screenshots are in [`docs/screenshots`](docs/screenshots): news pages, edit mode, the settings form and the widget palette. They were rendered from local fixture feeds, so the headlines are made up.

---

## Contents

1. [Run it](#run-it)
2. [Synology NAS (Docker)](#synology-nas-docker)
3. [HTTPS: why it matters](#https-why-it-matters)
4. [iPad: Add to Home Screen + Guided Access](#ipad-add-to-home-screen--guided-access)
5. [Fire TV Stick](#fire-tv-stick)
6. [Phones](#phones)
7. [Using it](#using-it)
8. [Configuration](#configuration)
9. [API](#api)
10. [Development and tests](#development-and-tests)
11. [Writing widgets](#writing-widgets) (see [WIDGETS.md](WIDGETS.md))

---

## Run it

```bash
node server/index.js
```

Open `http://<this-machine>:8080`. Node 22 or newer is required, and there is nothing to install.

With Docker:

```bash
docker build -t wallboard .
```

```bash
docker run -d --name wallboard --restart unless-stopped -p 8080:8080 -v "$PWD/data:/data" wallboard
```

## Synology NAS (Docker)

These steps are for DSM 7.2 with **Container Manager**. On DSM 7.0/7.1 the package is called "Docker", but the steps are the same.

1. **Copy the project to the NAS.** Unzip `wallboard.zip` and upload the `wallboard` folder with File Station to, for example, `/volume1/docker/wallboard-src`.
2. **Create a data folder**, for example `/volume1/docker/wallboard`. Your layouts, timers, tasks and the feed cache live there, so back it up with Hyper Backup if you care about them.
3. **Create the project.** In Container Manager, open **Project → Create**:
   - Name: `wallboard`
   - Path: `/volume1/docker/wallboard-src`
   - Source: *use the existing docker-compose.yml*

   Check the `volumes:` line (`/volume1/docker/wallboard:/data`) and the `TZ` value, then click **Next → Done**. Container Manager builds the image (it only downloads `node:22-alpine`) and starts it.
4. Open `http://<nas-ip>:8080`.

**Permissions.** The container runs as the unprivileged `node` user (uid 1000). If the log says it cannot write `/data/state.json`, do one of these:
- Give *Everyone* read/write on the data folder (File Station → Properties → Permission).
- Or uncomment `user: "1026:100"` in `docker-compose.yml`, using your DSM user's IDs (SSH in and run `id`).

**Updating.** Replace the files in `wallboard-src`, then in Container Manager choose **Project → wallboard → Action → Build**, and restart. Data in `/volume1/docker/wallboard` is kept. Screens pick up the new version on their next reload, which happens at the latest during the nightly 03:40–03:55 self-reload.

**Without Container Manager's build** (for example on an ARM NAS with no compiler, though none is needed here), you can build on a PC and load the image on the NAS:

```bash
docker buildx build --platform linux/amd64 -t wallboard . && docker save wallboard | gzip > wallboard.tar.gz
```

Then import it under **Container Manager → Image → Add → Add from file**. Use `--platform linux/arm64` for ARM models.

**Health.** `GET /api/health` is used as the container health check. The **Data freshness** widget shows the crawler and every feed.

## HTTPS: why it matters

Browsers enable **service workers** (offline start-up) and the **Screen Wake Lock API** only on HTTPS pages (and on `localhost`). Over plain `http://nas-ip:8080`, everything else works, with two differences:
- The app cannot open while the NAS is down. A screen that is already running keeps showing its last data, and timers and tasks keep working locally.
- Keep-awake falls back to playing a tiny silent looping video. That works on most devices but is less reliable, so also turn off auto-lock on the device (see below).

The easiest fix on a Synology is the built-in reverse proxy:

1. **Certificate.** Under **Control Panel → Security → Certificate**, get a Let's Encrypt certificate for a name that points at your NAS (for example a free `yourname.synology.me` DDNS name). Or use a certificate you already have.
2. **Reverse proxy.** Under **Control Panel → Login Portal → Advanced → Reverse Proxy → Create**:
   - Source: HTTPS, hostname `wallboard.yourname.synology.me` (or the DDNS name with a port such as 8443), port 443 / 8443
   - Destination: HTTP, `localhost`, port `8080`
3. Under **Certificate → Settings**, assign the certificate to that reverse-proxy entry.
4. Open `https://wallboard.yourname.synology.me` on your screens.

Live updates use server-sent events. The server sends `X-Accel-Buffering: no` and a keep-alive every 25 s, which works with DSM's nginx defaults.

You can also let Node serve HTTPS directly: set `TLS_CERT=/data/cert.pem` and `TLS_KEY=/data/key.pem`.

> Keep Wallboard on your home network. It has no login: anyone who can reach it can edit the layout and tasks. Don't port-forward it to the internet. If you need remote access, use the Synology VPN Server or Tailscale.

## iPad: Add to Home Screen + Guided Access

1. Open the Wallboard URL in **Safari** (preferably the `https://` one).
2. Tap **Share → Add to Home Screen → Add**. Launching from the icon opens Wallboard full-screen, without Safari's toolbars.
3. Keep the screen on:
   - **Settings → Display & Brightness → Auto-Lock → Never.**
   - Wallboard also requests a wake lock. It shows its status under **⚙ (This screen) → About this screen**.
4. Lock the iPad to Wallboard with **Guided Access**:
   - **Settings → Accessibility → Guided Access →** turn it on. Set a passcode under **Passcode Settings**, and set **Display Auto-Lock → Never**.
   - Open Wallboard from the Home Screen and **triple-click** the top button (or the Home button).
   - Under *Options*, leave **Touch** on (you need it for timers and tasks) and turn **Sleep/Wake Button** off. Tap **Start**.
   - To leave Guided Access, triple-click and enter the passcode.
5. Tap the screen once after launching. iPadOS only allows the timer beep after a user gesture.
6. For a wall mount, keep the iPad charging. Settings → Battery → *Optimized Charging* (or the 80 % limit on newer iPads) helps the battery survive being plugged in permanently.

Both portrait and landscape work. In portrait the page reflows into two columns and scrolls vertically. Drag-to-move and resize need the landscape grid (you can always add, configure and remove widgets).

## Fire TV Stick

1. Install **Silk Browser** from the Amazon Appstore (it's preinstalled on most Fire TV devices).
2. Open `https://<your-wallboard>/?tv=1`.
   - `?tv=1` forces **TV mode**: large type, D-pad navigation, and pages that rotate every 45 s.
   - TV mode turns on automatically for Fire TV / Silk user agents. Add `&profile=tv` to give the TV its own layout (see [profiles](#profiles)).
3. Bookmark the page (Silk menu → **Add bookmark**) and use Silk's **full-screen** option from its menu.
4. Stop the Fire TV screensaver from covering the dashboard: **Settings → Display & Sounds → Screensaver → Start Time → Never**.
   - Some Fire OS versions also put the stick to sleep after a period of inactivity; the sleep timer is under the same Display settings where available.
   - If your model doesn't offer "Never", a kiosk browser such as *Fully Kiosk Browser* (sideloaded) can keep the screen on and auto-start the URL after a reboot.
5. Remote controls:
   - **◀ ▶** flip pages when nothing is selected.
   - **▼** starts moving the focus through the page (timer buttons, headlines, …), **OK** presses, and **Back** leaves.
   - Rotation pauses for 2 minutes after you touch the remote.
   - The **☰ (menu)** key toggles edit mode if Silk passes it to the page. If it doesn't, move the focus down to the **✎** button at the bottom right.

Editing on a TV with a remote works:
- Select a widget's frame and press **OK** to enter *move* mode; the arrows move it.
- Press **OK** again for *resize* mode, and **OK** once more to finish.

It's still more comfortable to edit the TV's layout from a phone or iPad set to the same profile.

## Phones

Open the URL. Then use *Add to Home Screen* (iOS Safari), or *Install app* / *Add to Home screen* in Chrome on Android. Phones show a single column that scrolls vertically.

## Using it

- **Swipe** left or right, use the arrow keys, or tap the dots at the bottom to change pages.
- **Controls** at the bottom right fade out after 5 s; tap anywhere to bring them back:
  - **✎** edit layout
  - **☾** dim now
  - **⚙** settings for this screen
  - **⛶** full screen
- **Edit mode**: tap ✎, press `E`, or **long-press** an empty spot on the board.
  - **＋ Widget** opens the palette. A new widget goes into the first free space and shrinks if needed.
  - **Drag** a widget to move it; drag the **corner** to resize it. A red outline means the spot is taken.
  - **⚙** on a widget opens its settings. The form is generated from the widget's manifest.
  - **✕** removes a widget.
  - **Page** controls: rename, move left/right, add, delete.
  - **Export / Import** downloads the layout as JSON, or replaces it from a file or pasted JSON. You can use it for backups, or to copy a layout between profiles.
- **Night dimming**: a black overlay between *Night starts* and *Night ends* (default 22:30–06:30, 82 %). Tapping a dimmed screen wakes it for 45 s without pressing anything underneath. **☾** toggles dimming manually until the next scheduled change.
- **Burn-in protection**: the whole board drifts up to ±10 px along a slow path. The bottom controls fade out, and the nightly reload clears any long-running state.
- **Offline**:
  - Timers, tasks and the layout are written to the browser first and then sent to the server. Changes made while the server is unreachable are queued and replayed when it's back.
  - Headlines and weather show their last good copy, with an "offline" badge.

### Widgets (v1)

| Widget | What it does |
|---|---|
| **Clock** | Large time, optional seconds, date and IANA time zone (add several for world clocks). |
| **Date** | Weekday, big day number, month and year, ISO week. |
| **Weather** | Current conditions, next hours and a daily forecast from [Open-Meteo](https://open-meteo.com) (no API key). Search for your city in its settings; the default is New York. |
| **Timers** | Preset buttons (default 1h / 25m / 10m / 5m / 1m) and a free-form entry: `7m Pasta`, `1:30`, `1h30m`, `90s`. Several timers run at once, with pause, +1 min, reset and delete. When one finishes, its row flashes, it beeps, and a banner appears on every page. Timers are **shared live across screens**: start one on your phone, watch it on the TV. |
| **Tasks** | To-dos with **high / normal / low** priority (tap the `!!` pill to cycle it). Completed tasks are struck through and can be cleared. Use the *List name* setting for separate lists (e.g. "shopping"). Tasks are kept in the browser's local storage and synced to the NAS, never to a cloud service. |
| **News** | Merged, de-duplicated, newest-first headlines from a list of feeds you edit. Starter lists are included for **AI, Tech, Stocks and Sports**, and each has a page in the default layout. Optional thumbnails, summaries and auto-scroll. Tap a headline to open it (not in TV mode). |
| **Data freshness** | When each feed was last crawled, failures with their error, weather age, server reachability, and a **Refresh now** button. |

Starter feeds (editable under each News widget's settings):
- **AI**: MIT News AI, MIT Technology Review AI, TechCrunch AI, VentureBeat AI, Hacker News (AI/LLM, 100+ points)
- **Tech**: Ars Technica, The Verge, Hacker News front page, TechCrunch, Wired
- **Stocks**: MarketWatch top stories, CNBC top news, CNBC finance, Yahoo Finance
- **Sports**: ESPN, BBC Sport, CBS Sports, Yahoo Sports

> Publishers move feeds now and then. If one stops working, the Data freshness tile shows it in red with the HTTP error. Replace it in the News widget's settings.

### Profiles

Every screen has a **layout profile** (⚙ → *Layout profile*, default `default`). Screens with the same profile share one layout and update live when it's edited anywhere. Give the TV `tv` and the kitchen iPad `kitchen` to have different pages on each.

You can also set it in the URL, which is handy for bookmarks: `/?profile=tv&tv=1`.

Timers and tasks are shared by all profiles. Use the widgets' *Timer group* / *List name* settings to separate them.

## Configuration

**Server (environment variables)**

| Variable | Default | Meaning |
|---|---|---|
| `PORT` | `8080` | HTTP(S) port |
| `HOST` | `0.0.0.0` | Bind address |
| `DATA_DIR` | `./data` (`/data` in Docker) | State, feed cache, custom widgets |
| `CRAWL_INTERVAL_MINUTES` | `60` | Feed crawl interval |
| `TLS_CERT`, `TLS_KEY` | – | Serve HTTPS directly with these PEM files |
| `OPEN_METEO_BASE`, `OPEN_METEO_GEO_BASE` | Open-Meteo | Alternative / self-hosted Open-Meteo endpoints |

**Crawler behaviour**

- The first crawl happens about 2 s after start (only if the last run is more than an hour old); after that it runs hourly.
- It uses conditional GET (ETag / Last-Modified), a 20 s timeout, 4 feeds in parallel and up to 60 items per feed.
- A feed that's added in a widget is fetched immediately.
- When a feed fails, its last good items stay on screen.

**Per screen** (⚙ → *This screen*, stored in the browser): profile, TV mode, page rotation, text size, night dimming schedule and strength, tap-to-wake duration, keep-awake, drift, extra edge margin for TV overscan.

**Files in `DATA_DIR`**

- `state.json`: layouts (per profile), timers, tasks, custom collections.
- `feed-cache.json`: crawled items and per-feed status.
- `widgets/`: drop-in custom widgets.

Writes are atomic (temp file plus rename). A corrupt file is moved aside instead of crashing the server.

## API

All endpoints return JSON. Every response carries `X-Server-Time`, which screens use to agree on timer end times.

| Method & path | Purpose |
|---|---|
| `GET /api/health` | Liveness |
| `GET /api/status` | Crawler, per-feed and weather freshness |
| `GET /api/layout/:profile` · `PUT` · `DELETE` | Pages and widgets. `PUT {pages, baseVersion}` returns 409 if another screen saved first. `DELETE` resets to the starter layout. |
| `GET /api/profiles` | Saved profiles |
| `GET /api/c/:name` · `POST` · `PUT /api/c/:name/:id` · `PATCH` · `DELETE` | Generic collections (`timers`, `tasks`, …) |
| `GET /api/news?feed=…&feed=…&limit=40&maxAgeHours=72` | Merged items plus per-feed status. Unknown feeds are fetched immediately. |
| `GET /api/feeds/status` | Crawler status |
| `POST /api/refresh` (`{}` or `{url}`) | Crawl everything, or one feed, now |
| `GET /api/weather?lat=&lon=&units=&days=&name=` | Open-Meteo forecast, cached 15 min. Serves stale data if upstream fails. |
| `GET /api/geocode?q=` | City search |
| `GET /api/widgets` | Installed widget manifests (built-in and custom) |
| `GET /api/events` | Server-sent events: `change` (layout or collection) and `crawl` |

## Development and tests

```bash
npm start            # server on :8080
npm run dev          # restart on file changes
npm test             # 27 unit and integration tests (node:test)
npm run e2e          # 14 browser checks in Chromium (needs Playwright)
npm run screenshots  # TV / iPad / phone screenshots into ./screenshots
npm run zip          # wallboard.zip for distribution
```

No test touches the internet:
- `scripts/fixture-server.js` serves fixture RSS 2.0, RSS 1.0/RDF, Atom, JSON Feed and Latin-1 feeds, along with broken ones (HTTP 500, an HTML page, a slow feed, a redirect, an ETag / 304 feed) and a fake Open-Meteo.
- The test suites, `e2e.mjs` and `screenshots.mjs` all run the real server against it.
- `screenshots.mjs` also fails if there are console errors, failed requests, or cards that overflow horizontally.

Project layout:

```
server/        index.js (entry) · app.js (HTTP, routes, SSE) · store.js · crawler.js · feedparser.js · weather.js
public/        index.html · sw.js · manifest.webmanifest · css/ · js/ (app modules) · widgets/<type>/ · icons/
test/          node:test suites + fixtures/
scripts/       fixture-server.js · e2e.mjs · screenshots.mjs · make-icons.mjs · make-zip.sh
```

## Writing widgets

A widget is a folder with a `manifest.json` and one JS module. Copy `public/widgets/_template` (or drop a folder into `/data/widgets` on the NAS). The full guide is in **[WIDGETS.md](WIDGETS.md)**.
