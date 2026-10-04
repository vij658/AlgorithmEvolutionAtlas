#!/usr/bin/env python3
"""Build one self-contained HTML page from a Markdown part plus its Java verification programs.

Usage: build_html.py PART.md OUT.html
The Markdown starts with a meta block (Title, Part, Part-Title, Subtitle, Checks, JDK, Java, Description).
"""
import html
import pathlib
import re
import sys
import urllib.parse

import markdown
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JavaLexer

SERIES = [
    ("1", "Distance, similarity, number theory"),
    ("2", "Algorithm paradigms and classics"),
    ("3", "Performance laws and distributed systems"),
    ("4", "Security and identity"),
    ("5", "Design laws and engineering principles"),
]

CSS = r"""
:root{
  color-scheme: light dark;
  --bg:#faf9f6; --surface:#ffffff; --ink:#1c2230; --muted:#5a6376; --line:#e4e1d9;
  --accent:#2457b8; --accent-soft:#e9effb;
  --good:#17603a; --good-soft:#e7f4ec; --warn:#8a4b08; --warn-soft:#fdf1e1; --note:#3c4a6b; --note-soft:#eef1f7;
  --code-bg:#f3f1ea; --code-line:#e4e1d9;
  --t-kw:#8f2f78; --t-ty:#1f56b0; --t-str:#0e7446; --t-com:#6b7183; --t-num:#a9501a; --t-fn:#6b43b8; --t-an:#a9501a;
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#13161b; --surface:#1a1e25; --ink:#e7e9ee; --muted:#9ba4b3; --line:#2a303b;
    --accent:#86adff; --accent-soft:#1d2840;
    --good:#7fd6a2; --good-soft:#15291f; --warn:#f0b36b; --warn-soft:#2d2314; --note:#aab6d3; --note-soft:#1c2230;
    --code-bg:#171b22; --code-line:#2a303b;
    --t-kw:#d68ad0; --t-ty:#8fb4ff; --t-str:#7fd6a2; --t-com:#8a92a5; --t-num:#f0a46a; --t-fn:#b79cf0; --t-an:#f0a46a;
  }
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 var(--sans)}
.wrap{max-width:800px;margin:0 auto;padding:0 20px 90px}
header.hero{padding:56px 0 26px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
h1{font-size:clamp(28px,5vw,40px);line-height:1.15;margin:10px 0 8px;letter-spacing:-.01em}
.subtitle{font-size:18px;color:var(--muted);margin:0;max-width:60ch}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.badge{font-size:13px;padding:4px 10px;border:1px solid var(--line);border-radius:999px;background:var(--surface);color:var(--muted)}
.series{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 0;padding:0;list-style:none}
.chip{font-size:13px;padding:5px 11px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--muted)}
.chip b{color:var(--ink);font-weight:600}
.chip.current{border-color:var(--accent);background:var(--accent-soft);color:var(--ink)}
nav.toc{margin:28px 0 0;padding:16px 20px 12px;background:var(--surface);border:1px solid var(--line);border-radius:12px}
.toc-title{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 4px}
nav.toc .group{font-weight:600;margin:12px 0 4px}
nav.toc ol{list-style:none;margin:0;padding:0;columns:2 270px;column-gap:28px}
nav.toc li{break-inside:avoid;margin:2px 0;font-size:15px}
nav.toc a{color:var(--ink);text-decoration:none}
nav.toc a:hover{color:var(--accent);text-decoration:underline}
main{margin-top:8px}
h2{font-size:25px;line-height:1.25;margin:56px 0 6px;padding-top:26px;border-top:1px solid var(--line);scroll-margin-top:16px}
h2:first-child{border-top:0;padding-top:0}
h3{font-size:20px;line-height:1.3;margin:40px 0 8px;scroll-margin-top:16px}
p,li,blockquote,td,th{overflow-wrap:anywhere}
p{margin:.7em 0}
ul,ol{padding-left:1.4em}
li{margin:.3em 0}
a{color:var(--accent)}
code{font-family:var(--mono);font-size:.88em;background:var(--code-bg);padding:.1em .35em;border-radius:5px;border:1px solid var(--code-line);overflow-wrap:anywhere}
.highlight{position:relative;margin:16px 0;background:var(--code-bg);border:1px solid var(--code-line);border-radius:10px}
.highlight pre{margin:0;padding:14px 16px;overflow-x:auto;font:13.5px/1.55 var(--mono);tab-size:4;color:var(--ink)}
.highlight code{background:none;border:0;padding:0;font-size:inherit}
.highlight .k,.highlight .kd,.highlight .kn,.highlight .kr,.highlight .kp,.highlight .kc{color:var(--t-kw)}
.highlight .kt,.highlight .nc{color:var(--t-ty)}
.highlight .s,.highlight .s1,.highlight .s2,.highlight .sc,.highlight .sb{color:var(--t-str)}
.highlight .c,.highlight .c1,.highlight .cm,.highlight .cs,.highlight .cp,.highlight .ch{color:var(--t-com);font-style:italic}
.highlight .m,.highlight .mi,.highlight .mf,.highlight .mh,.highlight .mo,.highlight .mb,.highlight .il{color:var(--t-num)}
.highlight .nf,.highlight .fm{color:var(--t-fn)}
.highlight .nd{color:var(--t-an)}
.copy{position:absolute;top:8px;right:8px;font:12px var(--sans);padding:3px 9px;border-radius:6px;border:1px solid var(--line);background:var(--surface);color:var(--muted);cursor:pointer;opacity:0;transition:opacity .15s}
.highlight:hover .copy,.copy:focus-visible{opacity:1}
@media (hover:none){.copy{opacity:1}}
blockquote{margin:16px 0;padding:10px 16px;border-left:4px solid var(--note);background:var(--note-soft);border-radius:0 10px 10px 0;font-size:15px}
blockquote p{margin:.45em 0}
blockquote.verified{border-color:var(--good);background:var(--good-soft)}
blockquote.pitfall{border-color:var(--warn);background:var(--warn-soft)}
.table-wrap{overflow-x:auto;margin:18px 0;border:1px solid var(--line);border-radius:10px;background:var(--surface)}
table{border-collapse:collapse;width:100%;font-size:14.5px}
th,td{padding:9px 12px;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}
th{background:var(--note-soft);font-weight:600}
tr:last-child td{border-bottom:0}
details.program{margin:14px 0;border:1px solid var(--line);border-radius:10px;background:var(--surface);padding:0 14px}
details.program summary{cursor:pointer;padding:12px 0;font-weight:600}
details.program .muted{font-weight:400;color:var(--muted);font-size:14px;margin-left:6px}
details.program .highlight{margin-top:6px}
.dl{font-size:14px}
footer{margin-top:60px;padding-top:18px;border-top:1px solid var(--line);font-size:13px;color:var(--muted)}
@media print{
  body{background:#fff;color:#000}
  .copy{display:none}
  .highlight pre{white-space:pre-wrap;word-break:break-word}
  h2,h3{break-after:avoid}
  .highlight,blockquote,.table-wrap{break-inside:avoid}
}
"""

JS = r"""
(function () {
  function copyText(text, done) {
    function fallback() {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      try { document.execCommand('copy'); done(true); } catch (e) { done(false); }
      document.body.removeChild(ta);
    }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, fallback);
    } else { fallback(); }
  }
  document.querySelectorAll('.highlight').forEach(function (box) {
    var pre = box.querySelector('pre');
    if (!pre) return;
    var btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'copy'; btn.textContent = 'Copy';
    btn.addEventListener('click', function () {
      copyText(pre.textContent.replace(/\n$/, ''), function (ok) {
        btn.textContent = ok ? 'Copied' : 'Press Ctrl+C';
        setTimeout(function () { btn.textContent = 'Copy'; }, 1600);
      });
    });
    box.appendChild(btn);
  });
})();
"""

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>@@TITLE@@ · Part @@PART@@</title>
<meta name="description" content="@@DESC@@">
<style>@@CSS@@</style>
</head>
<body>
<div class="wrap">
<header class="hero">
  <div class="eyebrow">@@TITLE@@ · Part @@PART@@ of 5</div>
  <h1>@@PART_TITLE@@</h1>
  <p class="subtitle">@@SUBTITLE@@</p>
  <div class="badges">@@BADGES@@</div>
  <ul class="series">@@SERIES@@</ul>
</header>
<nav class="toc" aria-label="Contents"><p class="toc-title">Contents</p>@@TOC@@</nav>
<main>
@@BODY@@
@@PROGRAMS@@
</main>
<footer>@@FOOTER@@</footer>
</div>
<script>@@JS@@</script>
</body>
</html>
"""


def program_block(path: pathlib.Path) -> str:
    code = path.read_text()
    lines = code.count("\n") + (0 if code.endswith("\n") else 1)
    body = highlight(code, JavaLexer(), HtmlFormatter(cssclass="highlight"))
    uri = "data:text/plain;charset=utf-8," + urllib.parse.quote(code)
    name = html.escape(path.name)
    return (
        f'<details class="program"><summary><code>{name}</code>'
        f'<span class="muted">{lines} lines · run with <code>java {name}</code></span></summary>'
        f'<p><a class="dl" download="{name}" href="{uri}">Download {name}</a></p>{body}</details>'
    )


def build_toc(tokens) -> str:
    out = []
    for group in tokens:
        out.append(f'<div class="group"><a href="#{group["id"]}">{html.escape(group["name"])}</a></div><ol>')
        for item in group.get("children", []):
            out.append(f'<li><a href="#{item["id"]}">{html.escape(item["name"])}</a></li>')
        out.append("</ol>")
    return "".join(out)


def main() -> None:
    src = pathlib.Path(sys.argv[1])
    dest = pathlib.Path(sys.argv[2])
    md = markdown.Markdown(
        extensions=["meta", "fenced_code", "codehilite", "tables", "toc", "sane_lists"],
        extension_configs={
            "codehilite": {"guess_lang": False, "css_class": "highlight", "use_pygments": True},
            "toc": {"toc_depth": "2-3", "permalink": False},
        },
    )
    body = md.convert(src.read_text())
    meta = {k: " ".join(v).strip() for k, v in md.Meta.items()}

    body = re.sub(
        r"<blockquote>\s*<p><strong>(Verified|Pitfall|Rule of thumb|Note)\b",
        lambda m: f'<blockquote class="{m.group(1).lower().replace(" ", "-")}">\n<p><strong>{m.group(1)}',
        body,
    )
    body = body.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")

    part = meta["part"]
    java_files = [f.strip() for f in meta.get("java", "").split(",") if f.strip()]
    programs = ""
    if java_files:
        paths = []
        for f in java_files:                          # a name may be a glob, e.g. ../../code/principles/part-1-*/*/*.java
            paths += sorted(src.parent.glob(f)) if any(ch in f for ch in "*?[") else [src.parent / f]
        blocks = "".join(program_block(p) for p in paths)
        programs = (
            '<h2 id="verification-programs">Full verification programs</h2>'
            "<p>Each file below compiles as it is on JDK 17 or newer and prints a pass count at the end. "
            "They contain every snippet from this page plus the randomized checks behind each <strong>Verified</strong> note. "
            "Open one, then use <em>Download</em> or <em>Copy</em>.</p>" + blocks
        )

    chips = "".join(
        f'<li class="chip{" current" if n == part else ""}"><b>Part {n}</b> {html.escape(t)}</li>' for n, t in SERIES
    )
    badge_texts = ["Java 21 · every snippet compiled and run"]
    if meta.get("checks"):
        badge_texts.append(f'{meta["checks"]} checks passed')
    badge_texts.append(f"Part {part} of 5")
    badges = "".join(f'<span class="badge">{html.escape(t)}</span>' for t in badge_texts)
    footer = f'Verified on OpenJDK {html.escape(meta.get("jdk", ""))}. Randomized checks use fixed seeds, so the numbers reproduce.'

    page = TEMPLATE
    for key, val in {
        "@@TITLE@@": html.escape(meta["title"]),
        "@@PART@@": html.escape(part),
        "@@PART_TITLE@@": html.escape(meta["part-title"]),
        "@@SUBTITLE@@": html.escape(meta["subtitle"]),
        "@@DESC@@": html.escape(meta.get("description", meta["subtitle"]), quote=True),
        "@@BADGES@@": badges,
        "@@SERIES@@": chips,
        "@@TOC@@": build_toc(md.toc_tokens) + ('<div class="group"><a href="#verification-programs">Full verification programs</a></div>' if programs else ""),
        "@@BODY@@": body,
        "@@PROGRAMS@@": programs,
        "@@FOOTER@@": footer,
        "@@CSS@@": CSS,
        "@@JS@@": JS,
    }.items():
        page = page.replace(key, val)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page)
    print(f"wrote {dest} ({dest.stat().st_size:,} bytes), toc groups: {len(md.toc_tokens)}")


if __name__ == "__main__":
    main()
