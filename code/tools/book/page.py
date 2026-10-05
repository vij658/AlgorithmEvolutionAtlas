"""Render a topic of the book into its two editions from one spec.

  GitHub edition  : README.md with SVG pictures (light and dark files) and Markdown tables
  HTML edition    : one self-contained page (diagrams inline, widgets in plain JavaScript)

A spec is a dict:
  era, num, slug, title, date, lede, fieldnote, card (list of (label, markdown)),
  sections: list of dict(id, eyebrow, title, blocks: [block, ...])

Block types (each a dict with "type"):
  p        text (Markdown)                       callout   kind (wrong|key|circle|note), label, text
  diagram  diagram (diagrams.Diagram), caption   svg       name, draw(theme)->svg string, caption, alt
  table    head, rows, num (column indexes), hl  tries     items: [(question, answer)], all Markdown
  timeline events: [(when, what)], current       objects   items: [dict(title, text, link, link_text, licence, photo?, draw?)]
  links    items: [(level, title, source, url, why)]       code      code (Java), caption
  widget   html, js, css, fallback (an svg block for the GitHub edition), note
  details  summary, block (a table block)
Text is written in Markdown; the HTML edition converts it with the markdown package.
"""
import html
import json
import pathlib
import re

import markdown

import diagrams

HERE = pathlib.Path(__file__).resolve().parent
BASE_CSS = (HERE / "base.css").read_text()
REPO_URL = "https://github.com/vij658/AlgorithmEvolutionAtlas/blob/main/"


# ----------------------------------------------------------------------------------------------------------------------
# helpers
# ----------------------------------------------------------------------------------------------------------------------
def md_inline(s: str) -> str:
    """Markdown to HTML without the surrounding paragraph."""
    out = markdown.markdown(s)
    return re.sub(r"^<p>(.*)</p>$", r"\1", out.strip(), flags=re.S)


def md_block(s: str) -> str:
    return markdown.markdown(s)


def esc(s) -> str:
    return html.escape(str(s))


JAVA_KW = r"\b(static|long|int|double|boolean|while|for|if|else|return|new|final|void|char|byte|List|var|true|false|null|class|public|private)\b"


def java_html(code: str) -> str:
    out = []
    for line in code.split("\n"):
        m = re.search(r"//|/\*\*|^\s*\*", line)
        body, comment = (line[:m.start()], line[m.start():]) if m else (line, "")
        b = esc(body)
        b = re.sub(JAVA_KW, r'<span class="k-kw">\1</span>', b)
        b = re.sub(r"(?<![\w#&])(\d[\d_]*L?)\b", r'<span class="k-n">\1</span>', b)
        out.append(b + (f'<span class="k-c">{esc(comment)}</span>' if comment else ""))
    return "\n".join(out)


def picture(path_prefix: str, alt: str, width=None) -> str:
    w = f' width="{width}"' if width else ""
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="{path_prefix}-dark.svg">\n'
            f'  <img src="{path_prefix}-light.svg" alt="{esc(alt)}"{w}>\n</picture>')


def timeline_svg(events, current, theme, standalone, label):
    """A horizontal time line with one dot per development; the current topic is filled in red (current=-1: none)."""
    n = len(events)
    W, pad = max(760, n * 122), 64
    step = (W - 2 * pad) / max(1, n - 1)
    colw = min(step - 10, 132)
    c = lambda r: theme[r]
    out = [f'<line x1="{pad - 30}" y1="34" x2="{W - pad + 30}" y2="34" style="stroke:{c("ink")};stroke-width:2"/>']
    bottom = 0
    for i, (when, what) in enumerate(events):
        x = pad + i * step
        here = i == current
        out.append(f'<circle cx="{x:.1f}" cy="34" r="{9 if here else 7}" style="fill:{c("red") if here else c("surface")};stroke:{c("red") if here else c("ink")};stroke-width:2"/>')
        y = 50
        for part in diagrams.wrap(when, 11.5, 400, colw):
            y += 14
            out.append(f'<text x="{x:.1f}" y="{y}" text-anchor="middle" style="fill:{c("muted")};font-size:11.5px">{esc(part)}</text>')
        y += 4
        for part in diagrams.wrap(what, 12.5, 700 if here else 400, colw):
            y += 16
            out.append(f'<text x="{x:.1f}" y="{y}" text-anchor="middle" style="fill:{c("red") if here else c("ink")};'
                       f'font-size:12.5px;font-weight:{700 if here else 400}">{esc(part)}</text>')
        bottom = max(bottom, y)
    H = bottom + 16
    body = "".join(out)
    if standalone:
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(label)}" '
                f'style="font-family:{theme["font"]}"><title>{esc(label)}</title>{body}</svg>\n')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(label)}" style="font-family:{theme["font"]};'
            f'min-width:{int(W * 0.72)}px;max-width:{W * 1.05:.0f}px;margin:0 auto">{body}</svg>')


# ----------------------------------------------------------------------------------------------------------------------
# GitHub edition
# ----------------------------------------------------------------------------------------------------------------------
def render_md(spec, outdir: pathlib.Path, nav) -> str:
    assets = outdir / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    used = set()

    def svg_pair(name, draw):
        used.add(name)
        for t, theme in diagrams.GITHUB_THEMES.items():
            (assets / f"{name}-{t}.svg").write_text(draw(theme, True))
        return f"assets/{name}"

    L = [f"# {spec['title']}", "",
         f"*Era {spec['era']} · topic {spec['num']} · {spec['date']}* · {nav['md']} · "
         f"[Interactive edition]({spec['slug']}.html) · [Program]({nav['code_rel']})", "",
         f"> **Field note from the visiting historian.** {spec['fieldnote']}", "",
         "| | |", "|---|---|"]
    L += [f"| **{a}** | {b} |" for a, b in spec["card"]]
    L.append("")
    for sec in spec["sections"]:
        L += [f"## {sec['title']}", ""]
        for b in sec["blocks"]:
            L += md_block_render(b, svg_pair, sec, spec) + [""]
    for f in assets.glob("*.svg"):
        if f.name.rsplit("-", 1)[0] not in used:
            f.unlink()
    return "\n".join(L)


def md_block_render(b, svg_pair, sec, spec):
    t = b["type"]
    if t == "p":
        return [b["text"]]
    if t == "diagram":
        D = b["diagram"]
        p = svg_pair(b["name"], lambda th, sa: D.render(th, standalone=sa))
        return [picture(p, D.label)] + ([f"*{b['caption']}*"] if b.get("caption") else [])
    if t == "svg":
        p = svg_pair(b["name"], b["draw"])
        return [picture(p, b["alt"], b.get("width"))] + ([f"*{b['caption']}*"] if b.get("caption") else [])
    if t == "timeline":
        p = svg_pair(b.get("name", "timeline"), lambda th, sa: timeline_svg(b["events"], b["current"], th, sa, b.get("label", "Timeline")))
        return [picture(p, b.get("label", "Timeline"))]
    if t == "table":
        out = ["| " + " | ".join(b["head"]) + " |", "|" + "|".join("---" for _ in b["head"]) + "|"]
        for i, r in enumerate(b["rows"]):
            cells = [f"**{c}**" if b.get("hl") == i and str(c).strip() else str(c) for c in r]
            out.append("| " + " | ".join(cells) + " |")
        return out
    if t == "details":
        return ["<details>", f"<summary>{b['summary']}</summary>", ""] + md_block_render(b["block"], svg_pair, sec, spec) + ["", "</details>"]
    if t == "callout":
        return [f"> **{b['label']}.** {b['text']}"]
    if t == "tries":
        out = []
        for i, (q, a) in enumerate(b["items"], 1):
            out += ["<details>", f"<summary><b>{i}.</b> {md_inline(q)}</summary>", "", a, "</details>", ""]
        return out
    if t == "objects":
        out = ["| | Object | Where to see it | Licence |", "|---|---|---|---|"]
        for o in b["items"]:
            img = f'<img src="{o["photo"]}" alt="{esc(o["title"])}" width="140">' if o.get("photo") else "—"
            out.append(f"| {img} | **{o['title']}**. {o['text']} | [{o['link_text']}]({o['link']}) | {o['licence']} |")
        return out
    if t == "links":
        out = ["| Level | Link | Why |", "|---|---|---|"]
        for lvl, title, source, url, why in b["items"]:
            out.append(f"| {lvl.capitalize()} | [{title}]({url}) — {source} | {why} |")
        return out
    if t == "code":
        return ([b["caption"], ""] if b.get("caption") else []) + ["```java", b["code"], "```"]
    if t == "widget":
        fb = b.get("fallback")
        out = md_block_render(fb, svg_pair, sec, spec) if fb else []
        return out + [f"*{b.get('note', 'This part is interactive in the HTML edition.')}*"]
    raise ValueError(f"unknown block type {t}")


# ----------------------------------------------------------------------------------------------------------------------
# HTML edition
# ----------------------------------------------------------------------------------------------------------------------
def render_html(spec, nav, standalone_doc=True) -> str:
    T = diagrams.HTML_THEME
    css, js = [BASE_CSS, NAV_CSS], [COMMON_JS]
    toc = "".join(f'<a href="#{s["id"]}">{esc(s.get("toc", s["title"]))}</a>' for s in spec["sections"])
    card = "".join(f'<div><dt>{esc(a)}</dt><dd>{md_inline(b)}</dd></div>' for a, b in spec["card"])
    body = [f'''<div class="wrap">
<nav class="era-nav" aria-label="Book navigation">{nav["html"]}</nav>
<header class="hero">
  <div class="hero-top"><div class="titles">
    <div class="eyebrow">The Algorithm Evolution Atlas · Era {spec["era"]} · Topic {spec["num"]} · {esc(spec["date"])}</div>
    <h1>{esc(spec["title"])}</h1></div>
    <div class="byrne-mark" aria-hidden="true"><i></i><i></i><i></i></div></div>
  <p class="lede">{md_inline(spec["lede"])}</p>
  <p class="fieldnote">Field note from the visiting historian. {md_inline(spec["fieldnote"])}</p>
  <nav class="toc" aria-label="On this page">{toc}</nav>
  <dl class="card-grid">{card}</dl>
</header>''']
    for n, sec in enumerate(spec["sections"], 1):
        body.append(f'<section id="{sec["id"]}" aria-labelledby="{sec["id"]}-h">\n'
                    f'  <div class="sec-label"><span class="n">{n:02d}</span><span class="eyebrow">{esc(sec["eyebrow"])}</span></div>\n'
                    f'  <h2 id="{sec["id"]}-h">{esc(sec["title"])}</h2>')
        for b in sec["blocks"]:
            h, c, j = html_block(b, T)
            body.append(h)
            if c:
                css.append(c)
            if j:
                js.append(j)
        body.append("</section>")
    body.append(f'<footer>{md_inline(spec.get("footer", ""))}<br><span class="navfoot">{nav["html"]}</span></footer>\n</div>')
    page = (f"<title>{esc(spec['title'])}</title>\n"
            f'<meta name="description" content="{esc(spec["description"])}">\n'
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Public+Sans:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@400;600&display=swap">\n'
            f"<style>\n{''.join(css)}\n</style>\n" + "\n".join(body) + "\n<script>\n" + "\n".join(js) + "\n</script>\n")
    if standalone_doc:
        page = "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n" + \
               page.replace("<style>", "<style>\nbody{margin:0}\n", 1).replace("</style>\n", "</style>\n</head>\n<body>\n", 1) + "</body>\n</html>\n"
    return page


def html_block(b, T):
    t = b["type"]
    if t == "p":
        return f'<p class="col">{md_inline(b["text"])}</p>', None, None
    if t == "diagram":
        cap = f'<figcaption>{md_inline(b["caption"])}</figcaption>' if b.get("caption") else ""
        return f'<figure class="dgm"><div class="frame">{b["diagram"].render(T, standalone=False)}</div>{cap}</figure>', None, None
    if t == "svg":
        cap = f'<figcaption>{md_inline(b["caption"])}</figcaption>' if b.get("caption") else ""
        return f'<figure class="dgm"><div class="frame">{b["draw"](T, False)}</div>{cap}</figure>', None, None
    if t == "timeline":
        return (f'<figure class="dgm"><div class="frame">{timeline_svg(b["events"], b["current"], T, False, b.get("label", "Timeline"))}</div></figure>', None, None)
    if t == "table":
        num = set(b.get("num", []))
        head = "".join(f'<th class="{"n" if i in num else ""}">{esc(h)}</th>' for i, h in enumerate(b["head"]))
        trs = []
        for ri, r in enumerate(b["rows"]):
            cells = "".join(f'<td class="{"n" if i in num else ""}">{md_inline(str(c))}</td>' for i, c in enumerate(r))
            trs.append(f'<tr class="{"hl" if b.get("hl") == ri else ""}">{cells}</tr>')
        return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>', None, None
    if t == "details":
        inner, c, j = html_block(b["block"], T)
        return f'<details class="data"><summary>{esc(b["summary"])}</summary>{inner}</details>', c, j
    if t == "callout":
        return f'<div class="callout {b["kind"]} col"><div class="k">{esc(b["label"])}</div>{md_block(b["text"])}</div>', None, None
    if t == "tries":
        items = "".join(f'<details class="try"><summary><span class="q">{i}</span><span>{md_inline(q)}</span></summary>'
                        f'<div class="ans">{md_block(a)}</div></details>' for i, (q, a) in enumerate(b["items"], 1))
        return f'<div>{items}</div>', None, None
    if t == "objects":
        cards = []
        for o in b["items"]:
            draw = o["draw"](T, False) if o.get("draw") else ""
            if o.get("photo"):
                pic = (f'<div class="pic"><img src="{o["photo"]}" alt="{esc(o["title"])}" onerror="this.closest(\'.obj\').classList.add(\'noimg\')">'
                       f'<div class="fallback">{draw}<span>Photograph not shown here: open it from the link below.</span></div></div>')
            else:
                pic = f'<div class="pic">{draw}</div>'
            cards.append(f'<figure class="obj" style="margin:0">{pic}<figcaption class="txt"><b>{esc(o["title"])}</b><span>{md_inline(o["text"])}</span>'
                         f'<a href="{o["link"]}">{esc(o["link_text"])}</a><span class="lic">{md_inline(o["licence"])}</span></figcaption></figure>')
        return f'<div class="objects">{"".join(cards)}</div>', None, None
    if t == "links":
        cards = "".join(f'<a href="{url}" target="_blank" rel="noopener"><span class="lvl {lvl}">{lvl.capitalize()}</span>'
                        f'<span class="t">{esc(title)} · {esc(source)}</span><span class="w">{esc(why)}</span></a>'
                        for lvl, title, source, url, why in b["items"])
        return f'<div class="links">{cards}</div>', None, None
    if t == "code":
        cap = f'<p class="col">{md_inline(b["caption"])}</p>' if b.get("caption") else ""
        return f'{cap}<pre class="code">{java_html(b["code"])}</pre>', None, None
    if t == "widget":
        return b["html"], b.get("css"), b.get("js")
    raise ValueError(f"unknown block type {t}")


NAV_CSS = """
nav.era-nav{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13.5px;padding-top:18px;color:var(--muted)}
nav.era-nav a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--axis)}
nav.era-nav a:hover{color:var(--ink);border-color:var(--ink)}
nav.era-nav .here{color:var(--ink);font-weight:600}
footer .navfoot{display:inline-flex;flex-wrap:wrap;gap:6px 14px;margin-top:8px}
footer .navfoot a{color:var(--ink-2)}
"""

COMMON_JS = r"""
const NS = "http://www.w3.org/2000/svg";
const fmt = n => (typeof n === "number" ? n.toLocaleString("en-US") : String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","));
function el(tag, attrs = {}, parent, text) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) if (v !== null && v !== undefined) e.setAttribute(k, v);
  if (text !== undefined) e.textContent = text;
  if (parent) parent.appendChild(e);
  return e;
}
function sv(tag, attrs = {}, parent, text) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined) continue;
    if (typeof v === "string" && v.includes("var(")) e.style.setProperty(k, v); else e.setAttribute(k, v);
  }
  if (text !== undefined) e.textContent = text;
  if (parent) parent.appendChild(e);
  return e;
}
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const COLORS = ["var(--red)", "var(--yellow)", "var(--blue)"];
const ON = ["var(--on-red)", "var(--on-yellow)", "var(--on-blue)"];
"""


# ----------------------------------------------------------------------------------------------------------------------
# the reference catalog: reuse its checked links for each topic
# ----------------------------------------------------------------------------------------------------------------------
def catalog_links(catalog_md: str, topic_num: int, limit_per_level=4):
    """Link rows (level, title, source, url, why) from a topic's section of an era's reference catalog."""
    m = re.search(rf"^## {topic_num}\. .*?(?=^## |\Z)", catalog_md, re.S | re.M)
    if not m:
        return []
    rows = []
    for ln in m.group(0).split("\n"):
        mm = re.match(r"\| (Start|Deeper|Scholar) \| \[(.+?)\]\((https?://[^)]+)\)(.*?)\| (.+?) \| (.+?) \|$", ln)
        if mm:
            lvl, title, url, extra, source, why = mm.groups()
            why = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", why)          # a card is one link: keep nested links as text
            rows.append((lvl.lower(), title, source.strip(), url, why.strip()))
    order = {"start": 0, "deeper": 1, "scholar": 2}
    rows.sort(key=lambda r: order[r[0]])
    out, count = [], {}
    for r in rows:
        count[r[0]] = count.get(r[0], 0) + 1
        if count[r[0]] <= limit_per_level:
            out.append(r)
    return out
