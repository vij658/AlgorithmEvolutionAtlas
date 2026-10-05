"""Build an era's front page in both editions: book/<era>/README.md (GitHub) and book/<era>/index.html (interactive).

The page carries the era's time line, a map of how its ideas combined, and one card per topic. A topic whose page has
not been built yet still gets a card, marked as planned, pointing at its entry in the reference catalog.
"""
import re

import diagrams
import page
from diagrams import Diagram


def chain_rows(catalog_md):
    """The 'chain at a glance' table of the reference catalog: {topic number: (when, the pain it answered)}."""
    rows = {}
    for ln in catalog_md.split("\n"):
        m = re.match(r"\| (\d+) \| \[.+?\]\((#[^)]+)\) \| (.+?) \| (.+?) \|$", ln)
        if m:
            rows[int(m.group(1))] = dict(anchor=m.group(2), when=m.group(3), pain=m.group(4))
    return rows


def built(era, t, BOOK, CODE):
    folder = f"{t[0]:02d}-{t[1]}"
    return (BOOK / era.ERA["folder"] / folder / f"{t[1]}.html").exists() and \
           (CODE / era.ERA["folder"] / folder / "expected-output.txt").exists()


def era_map(era):
    """Boxes are the era's topics; an arrow means 'this development reuses that idea' (not a proven line of descent)."""
    spec = era.MAP
    D = Diagram(spec["w"], spec["h"], f"How the ideas of Era {era.ERA['num']} combined: {era.ERA['title']}")
    by_num = {t[0]: t for t in era.TOPICS}
    for num, (x, y) in spec["at"].items():
        t = by_num[num]
        D.node(num, x, y, spec["bw"], spec["bh"], [(f"{num}. {t[2]}", "title"), (t[3], "note")],
               color=spec.get("color", {}).get(num, "ink"))
    for e in spec["edges"]:
        a, b, label = e[:3]
        opts = e[3] if len(e) > 3 else {}
        D.edge(a, b, label=label, **opts)
    return D


def build(era, BOOK, CODE):
    E = era.ERA
    out_dir = BOOK / E["folder"]
    catalog = (out_dir / "reference-catalog.md").read_text()
    chain = chain_rows(catalog)
    D = era_map(era)
    events = era.timeline_events()
    tl_label = f"Era {E['num']}: {E['title']}, from {E['span']}"

    # ---------------- GitHub edition ----------------
    assets = out_dir / "assets"
    assets.mkdir(exist_ok=True)
    for name, draw in [("era-timeline", lambda th, sa: page.timeline_svg(events, -1, th, sa, tl_label)),
                       ("era-map", lambda th, sa: D.render(th, standalone=sa))]:
        for t, theme in diagrams.GITHUB_THEMES.items():
            (assets / f"{name}-{t}.svg").write_text(draw(theme, True))
    L = [f"# Era {E['num']} — {E['title']}", "",
         f"*{E['span']}* · [Book contents](../README.md) · [Interactive edition](index.html) · "
         f"[Reference catalog](reference-catalog.md) · [Programs](../../code/{E['folder']}/README.md)", "",
         f"> **Field note from the visiting historian.** {E['lede']}", "",
         "## When", "", page.picture("assets/era-timeline", tl_label), "",
         "## How the ideas combined", "", page.picture("assets/era-map", D.label), "",
         f"*{era.MAP['caption']}*", "",
         "## The topics", "",
         "| # | Topic | When | What hurt | Read |", "|---|---|---|---|---|"]
    for t in era.TOPICS:
        num, slug, title = t[0], t[1], t[2]
        c = chain.get(num, {})
        folder = f"{num:02d}-{slug}"
        if built(era, t, BOOK, CODE):
            read = (f"[page]({folder}/README.md) · [interactive]({folder}/{slug}.html) · "
                    f"[program](../../code/{E['folder']}/{folder}/README.md)")
        else:
            read = f"planned · [references](reference-catalog.md{c.get('anchor', '')})"
        L.append(f"| {num} | **{title}** | {c.get('when', t[3])} | {c.get('pain', '')} | {read} |")
    L += ["", "The interactive edition is a single HTML file per topic: download it and open it in a browser, "
              "or use the published copy linked from the [book contents](../README.md).", ""]
    (out_dir / "README.md").write_text("\n".join(L))

    # ---------------- HTML edition ----------------
    html = render_index_html(era, BOOK, CODE, chain, D, events, tl_label)
    (out_dir / "index.html").write_text(html)
    print(f"built era {E['num']} index ({sum(built(era, t, BOOK, CODE) for t in era.TOPICS)} of {len(era.TOPICS)} topics built)")
    return html


INDEX_CSS = """
.topics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:22px}
@media (max-width:900px){.topics{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:600px){.topics{grid-template-columns:1fr}}
.topic{display:flex;flex-direction:column;gap:6px;padding:14px 16px 16px;background:var(--surface);border:1px solid var(--rule);border-top:4px solid var(--ink);min-width:0}
.topic.ready{border-top-color:var(--red)}
.topic .n{font-family:var(--mono);font-size:12px;color:var(--muted)}
.topic h3{margin:0;font-size:23px;line-height:1.15}
.topic h3 a{color:var(--ink);text-decoration:none}
.topic h3 a:hover{text-decoration:underline}
.topic .when{font-size:13px;color:var(--ink-2)}
.topic .pain{font-size:14.5px;margin:4px 0 6px}
.topic .pain b{font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);display:block}
.topic .go{margin-top:auto;display:flex;flex-wrap:wrap;gap:6px 12px;font-size:13.5px}
.topic .status{font-size:12px;font-weight:600;color:var(--muted)}
"""


def render_index_html(era, BOOK, CODE, chain, D, events, tl_label, standalone_doc=True):
    E = era.ERA
    T = diagrams.HTML_THEME
    repo = page.REPO_URL
    cards = []
    for t in era.TOPICS:
        num, slug, title = t[0], t[1], t[2]
        c = chain.get(num, {})
        folder = f"{num:02d}-{slug}"
        ready = built(era, t, BOOK, CODE)
        cat = f"{repo}book/{E['folder']}/reference-catalog.md{c.get('anchor', '')}"
        if ready:
            head = f'<a href="{folder}/{slug}.html">{page.esc(title)}</a>'
            go = (f'<a href="{folder}/{slug}.html">Open the page</a>'
                  f'<a href="{repo}code/{E["folder"]}/{folder}/README.md">Program</a>'
                  f'<a href="{repo}book/{E["folder"]}/{folder}/README.md">GitHub edition</a>')
            status = ""
        else:
            head = page.esc(title)
            go = f'<a href="{cat}">References in the catalog</a>'
            status = '<span class="status">Page coming next</span>'
        cards.append(f'<article class="topic{" ready" if ready else ""}"><span class="n">Topic {num}</span><h3>{head}</h3>'
                     f'<span class="when">{page.md_inline(c.get("when", t[3]))}</span>'
                     f'<p class="pain"><b>What hurt</b>{page.md_inline(c.get("pain", ""))}</p>{status}<div class="go">{go}</div></article>')
    nav = (f'<a href="{repo}book/README.md">Book contents</a>'
           f'<a href="{repo}book/{E["folder"]}/reference-catalog.md">Era {E["num"]} reference catalog</a>'
           f'<a href="{repo}code/{E["folder"]}/README.md">Era {E["num"]} programs</a>')
    body = f'''<div class="wrap">
<nav class="era-nav" aria-label="Book navigation">{nav}</nav>
<header class="hero">
  <div class="hero-top"><div class="titles">
    <div class="eyebrow">The Algorithm Evolution Atlas · Era {E["num"]} · {page.esc(E["span"])}</div>
    <h1>{page.esc(E["title"])}</h1></div>
    <div class="byrne-mark" aria-hidden="true"><i></i><i></i><i></i></div></div>
  <p class="lede">{page.md_inline(era.ERA.get("intro", E["lede"]))}</p>
  <p class="fieldnote">Field note from the visiting historian. {page.md_inline(E["lede"])}</p>
</header>
<section id="when" aria-labelledby="when-h">
  <div class="sec-label"><span class="n">01</span><span class="eyebrow">When</span></div>
  <h2 id="when-h">{len(era.TOPICS)} developments in order of time</h2>
  <figure class="dgm"><div class="frame">{page.timeline_svg(events, -1, T, False, tl_label)}</div></figure>
</section>
<section id="map" aria-labelledby="map-h">
  <div class="sec-label"><span class="n">02</span><span class="eyebrow">How the ideas combined</span></div>
  <h2 id="map-h">Each development reuses an older idea</h2>
  <figure class="dgm"><div class="frame">{D.render(T, standalone=False)}</div><figcaption>{page.md_inline(era.MAP["caption"])}</figcaption></figure>
</section>
<section id="topics" aria-labelledby="topics-h">
  <div class="sec-label"><span class="n">03</span><span class="eyebrow">The topics</span></div>
  <h2 id="topics-h">Open a topic</h2>
  <div class="topics">{"".join(cards)}</div>
</section>
<footer>Every link in this book was opened before it was listed, and every number comes from a program that was run.
<a href="{repo}">The Algorithm Evolution Atlas on GitHub</a>.</footer>
</div>'''
    doc = (f"<title>{page.esc(E['title'])}</title>\n"
           f'<meta name="description" content="{page.esc(E["lede"])}">\n'
           '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
           '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">\n'
           f"<style>\n{page.BASE_CSS}{page.NAV_CSS}{INDEX_CSS}\n</style>\n{body}\n")
    if standalone_doc:
        doc = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
               "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n" +
               doc.replace("</style>\n", "</style>\n</head>\n<body>\n", 1) + "</body>\n</html>\n")
    return doc
