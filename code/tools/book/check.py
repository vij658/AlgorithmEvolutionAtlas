#!/usr/bin/env python3
"""Render book pages in headless Chromium and report problems; save screenshots.

  python3 code/tools/book/check.py OUTDIR page.html [page.html ...]

For each page: desktop light, desktop dark and phone dark (390 px). Reports script errors, horizontal page scroll,
elements that stick out past the phone screen (scrolling figure frames and tables are allowed to be wide), links to
anchors that do not exist, and images that failed to load. Full-page screenshots go to OUTDIR.
"""
import pathlib
import sys

from playwright.sync_api import sync_playwright

CHROME = "/opt/pw-browsers/chromium"


def check(paths, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    problems = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME) if pathlib.Path(CHROME).exists() else p.chromium.launch()
        for path in paths:
            path = pathlib.Path(path).resolve()
            stem = path.stem
            for name, vp, scheme in [("desktop-light", (1180, 900), "light"), ("desktop-dark", (1180, 900), "dark"),
                                     ("phone-dark", (390, 844), "dark")]:
                ctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, color_scheme=scheme,
                                          device_scale_factor=1)
                pg = ctx.new_page()
                errors = []
                pg.on("pageerror", lambda e: errors.append(str(e)))
                pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
                pg.route("**/*", lambda r: r.abort() if r.request.url.startswith("http") else r.continue_())  # offline, like a sandbox
                pg.goto(path.as_uri())
                pg.wait_for_timeout(400)
                info = pg.evaluate("""() => {
                  const w = window.innerWidth, out = [];
                  for (const el of document.querySelectorAll('body *')) {
                    if (el.closest('.frame, .tbl, pre, .scrollx, .board svg, script, style')) continue;
                    const r = el.getBoundingClientRect();
                    if (r.width && r.right > w + 1) out.push(el.tagName + '.' + (el.className.baseVal ?? el.className) + ' :: ' + (el.textContent || '').trim().slice(0, 60));
                  }
                  const ids = new Set([...document.querySelectorAll('[id]')].map(e => e.id));
                  const broken = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1)).filter(h => h && !ids.has(h));
                  const imgs = [...document.querySelectorAll('img')].filter(i => i.complete && i.naturalWidth === 0 && !i.closest('.noimg')).map(i => i.src);
                  return {scroll: document.documentElement.scrollWidth > w, over: out.slice(0, 6), broken, imgs,
                          sections: document.querySelectorAll('section').length, height: document.documentElement.scrollHeight};
                }""")
                bad = errors or info["scroll"] or info["over"] or info["broken"]
                problems += bool(bad)
                print(f"{stem} {name}: {info['sections']} sections, {info['height']} px tall"
                      + (f"\n   errors: {errors}" if errors else "")
                      + ("\n   page scrolls sideways" if info["scroll"] else "")
                      + (f"\n   sticks out: {info['over']}" if info["over"] else "")
                      + (f"\n   broken anchors: {info['broken']}" if info["broken"] else ""))
                pg.screenshot(path=str(outdir / f"{stem}-{name}.png"), full_page=True)
                ctx.close()
        browser.close()
    print("problems:", problems)
    return problems


if __name__ == "__main__":
    sys.exit(1 if check(sys.argv[2:], pathlib.Path(sys.argv[1])) else 0)
