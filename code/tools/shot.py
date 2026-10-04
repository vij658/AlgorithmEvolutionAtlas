#!/usr/bin/env python3
"""Render a built page in headless Chromium: structural checks plus screenshots (light, dark, mobile)."""
import pathlib
import sys

from playwright.sync_api import sync_playwright

page_path = pathlib.Path(sys.argv[1]).resolve()
outdir = pathlib.Path(sys.argv[2])
focus = sys.argv[3] if len(sys.argv) > 3 else "Mahalanobis"
outdir.mkdir(parents=True, exist_ok=True)
errors = []

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path="/opt/pw-browsers/chromium") if pathlib.Path("/opt/pw-browsers/chromium").exists() else p.chromium.launch()
    for name, vp, scheme in [("desktop-light", (1100, 1000), "light"), ("desktop-dark", (1100, 1000), "dark"), ("mobile-light", (390, 844), "light")]:
        ctx = browser.new_context(viewport={"width": vp[0], "height": vp[1]}, color_scheme=scheme)
        pg = ctx.new_page()
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(page_path.as_uri())
        if name == "desktop-light":
            info = pg.evaluate("""() => {
              const ids = new Set([...document.querySelectorAll('[id]')].map(e => e.id));
              const links = [...document.querySelectorAll('a[href^="#"]')].map(a => a.getAttribute('href').slice(1));
              return {
                h2: document.querySelectorAll('main h2').length,
                h3: document.querySelectorAll('main h3').length,
                highlights: document.querySelectorAll('.highlight').length,
                copyButtons: document.querySelectorAll('.copy').length,
                tables: document.querySelectorAll('table').length,
                verified: document.querySelectorAll('blockquote.verified').length,
                pitfall: document.querySelectorAll('blockquote.pitfall').length,
                brokenAnchors: links.filter(l => !ids.has(l)),
                horizontalScroll: document.documentElement.scrollWidth > window.innerWidth,
              };
            }""")
            print(info)
        pg.screenshot(path=str(outdir / f"{name}-top.png"))
        target = pg.locator("main h3", has_text=focus).first
        target.scroll_into_view_if_needed()
        pg.evaluate("window.scrollBy(0, -12)")
        pg.screenshot(path=str(outdir / f"{name}-entry.png"))
        if name == "mobile-light":
            print("mobile horizontal scroll:", pg.evaluate("document.documentElement.scrollWidth > window.innerWidth"))
            offenders = pg.evaluate("""() => {
              const w = window.innerWidth, out = [];
              for (const el of document.querySelectorAll('main *, header *, nav *')) {
                if (el.closest('pre, .table-wrap')) continue;
                const r = el.getBoundingClientRect();
                if (r.right > w + 1) out.push(el.tagName + ' ' + (el.className || '') + ' :: ' + el.textContent.trim().slice(0, 70));
              }
              return out.slice(0, 8);
            }""")
            print("overflowing elements:", offenders if offenders else "none")
        ctx.close()
    browser.close()

print("page errors:", errors if errors else "none")
