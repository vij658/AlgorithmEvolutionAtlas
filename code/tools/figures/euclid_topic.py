#!/usr/bin/env python3
"""Build the visual pages for Era 1, topic 7 (Euclid's algorithm) from the program's own output.

Reads   code/era-01-the-first-algorithms/07-euclids-algorithm/expected-output.txt  (what EuclidsAlgorithm.java prints)
Writes  book/era-01-the-first-algorithms/07-euclids-algorithm/
          README.md                    GitHub edition: Mermaid diagrams, SVG figures, tables, fold-out answers
          assets/*-light.svg, *-dark.svg
          euclids-algorithm.html       interactive edition (from the template next to this script)

Every number in the figures and tables is parsed from the program output, so re-running the program and this
script keeps the book in step with the code. Run from anywhere:  python3 code/tools/figures/euclid_topic.py
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[3]
CODE = ROOT / "code" / "era-01-the-first-algorithms" / "07-euclids-algorithm"
BOOK = ROOT / "book" / "era-01-the-first-algorithms" / "07-euclids-algorithm"
ASSETS = BOOK / "assets"
TEMPLATE = pathlib.Path(__file__).resolve().parent / "euclid-page.html"

# Byrne's 1847 Euclid printed its figures in red, yellow and blue; the book's diagrams borrow that idea.
THEMES = {
    "light": dict(ink="#17171a", ink2="#55545a", muted="#7d7c84", grid="#e4e3dd", axis="#c4c3bb", red="#d5352a",
                  yellow="#e8a317", blue="#1f5ba8", on_red="#ffffff", on_yellow="#17171a", on_blue="#ffffff",
                  wash="#f1f0ea", ring="#ffffff"),
    "dark": dict(ink="#ecebe6", ink2="#b9b8b2", muted="#8f8e96", grid="#2b2e34", axis="#41444b", red="#f0584d",
                 yellow="#d9a227", blue="#5b8fe0", on_red="#14161a", on_yellow="#14161a", on_blue="#14161a",
                 wash="#1d2026", ring="#0d1117"),
}
FONT = "system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif"


# ----------------------------------------------------------------------------------------------------------------------
# 1. read the program output
# ----------------------------------------------------------------------------------------------------------------------
def parse(text: str) -> dict:
    d = {"trace": {}, "extended": [], "compare": [], "worst": [], "average": [], "exhaustive": []}
    for ln in text.splitlines():
        if m := re.match(r"trace (\d+) (\d+): (\d+) = (\d+) x (\d+) \+ (\d+)$", ln):
            key = f"{m.group(1)},{m.group(2)}"
            d["trace"].setdefault(key, []).append([int(m.group(i)) for i in range(3, 7)])
        elif m := re.match(r"quotients (\d+)/(\d+) = \[(.+)\]", ln):
            d["quotients"] = [int(x) for x in re.split(r"[;,]\s*", m.group(3))]
        elif m := re.match(r"extended \d+ \d+: q=(-?\d+) r=(-?\d+) s=(-?\d+) t=(-?\d+)$", ln):
            d["extended"].append([int(m.group(i)) for i in range(1, 5)])
        elif m := re.match(r"bezout (\d+) (\d+): (\d+) = (-?\d+) x \d+ \+ (-?\d+) x \d+$", ln):
            d["bezout"] = dict(a=int(m.group(1)), b=int(m.group(2)), g=int(m.group(3)), x=int(m.group(4)), y=int(m.group(5)))
        elif m := re.match(r"compare (\d+) (\d+): gcd=(\d+) trying=(\d+) subtracting=(\d+) dividing=(\d+) binary=(\d+)$", ln):
            d["compare"].append(dict(zip(["a", "b", "gcd", "trying", "subtracting", "dividing", "binary"], map(int, m.groups()))))
        elif m := re.match(r"exhaustive below (\d+): most steps (\d+) at \((\d+), (\d+)\)$", ln):
            d["exhaustive"].append(dict(limit=int(m.group(1)), steps=int(m.group(2)), a=int(m.group(3)), b=int(m.group(4))))
        elif m := re.match(r"worst digits=(\d+): \((\d+), (\d+)\) steps=(\d+) lame=(\d+)$", ln):
            d["worst"].append(dict(digits=int(m.group(1)), a=int(m.group(2)), b=int(m.group(3)), steps=int(m.group(4)), lame=int(m.group(5))))
        elif m := re.match(r"average digits=(\d+): ([\d.]+) steps over (\d+) random pairs$", ln):
            d["average"].append(dict(digits=int(m.group(1)), mean=float(m.group(2))))
            d["samples"] = int(m.group(3))
        elif m := re.match(r"slope: ([\d.]+) more steps per extra digit .*= ([\d.]+)$", ln):
            d["slope"], d["slope_predicted"] = float(m.group(1)), float(m.group(2))
        elif m := re.match(r"histogram 18 digits \((\d+) random pairs\): (.+)$", ln):
            d["hist_samples"] = int(m.group(1))
            d["histogram"] = [[int(a), int(b)] for a, b in (p.split(":") for p in m.group(2).split())]
        elif m := re.match(r"rsa: e=(\d+), phi=(\d+), d=(\d+)", ln):
            d["rsa"] = dict(e=int(m.group(1)), phi=int(m.group(2)), d=int(m.group(3)))
        elif m := re.match(r"EuclidsAlgorithm: (\d+) checks passed$", ln):
            d["checks"] = int(m.group(1))
    for k in ("quotients", "bezout", "slope", "histogram", "rsa", "checks"):
        if k not in d:
            raise SystemExit(f"program output has no {k!r} line")
    return d


# ----------------------------------------------------------------------------------------------------------------------
# 2. SVG figures (one light and one dark file each; transparent background so they sit on GitHub's page colour)
# ----------------------------------------------------------------------------------------------------------------------
def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" '
            f'aria-label="{html.escape(title)}" font-family="{FONT}"><title>{html.escape(title)}</title>{body}</svg>\n')


def text(x, y, s, fill, size=13, anchor="start", weight=400):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" text-anchor="{anchor}" '
            f'font-weight="{weight}">{html.escape(str(s))}</text>')


def squares(a, b):
    """The squares cut from an a-by-b rectangle, stage by stage: list of stages, each a list of (x, y, side)."""
    x0, y0, w, h = 0, 0, a, b
    stages = []
    while w and h:
        s = min(w, h)
        n = max(w, h) // s
        stage = []
        for i in range(n):
            if w >= h:
                stage.append((x0 + i * s, y0, s))
            else:
                stage.append((x0, y0 + i * s, s))
        stages.append(stage)
        if w >= h:
            x0, w = x0 + n * s, w - n * s
        else:
            y0, h = y0 + n * s, h - n * s
    return stages


def strip_figure(a, b, trace, t):
    """Euclid's algorithm as a picture: cut the biggest squares off a rectangle, stage by stage."""
    stages = squares(a, b)
    colors = [(t["red"], t["on_red"]), (t["yellow"], t["on_yellow"]), (t["blue"], t["on_blue"])]
    pw, gap, top = 228, 24, 28
    n_panels = len(stages) + 1
    W = n_panels * pw + (n_panels - 1) * gap
    scale = (pw - 8) / a
    rh = b * scale
    H = top + rh + 96
    out = []
    caps = [(f"A {a} × {b} rectangle", "Find the largest square tile that", "fits both sides exactly.")]
    for (big, q, small, r) in trace:
        caps.append((f"{big} = {q} × {small} + {r}",
                     f"Cut {q} square{'s' if q > 1 else ''} of side {small}." if r else f"{q} squares of side {small} fill it.",
                     f"A {small} × {r} piece is left." if r else "Nothing is left: done."))
    # zoom for the last panel if the final piece is small
    last = stages[-1]
    lx = min(s[0] for s in last); ly = min(s[1] for s in last)
    lw = max(s[0] + s[2] for s in last) - lx; lh = max(s[1] + s[2] for s in last) - ly
    zoom = min((pw - 8) / lw, rh / lh) / scale
    for p in range(n_panels):
        ox = p * (pw + gap) + 4
        is_zoom = p == n_panels - 1 and zoom > 1.5
        if not is_zoom:
            out.append(f'<rect x="{ox}" y="{top}" width="{a*scale:.1f}" height="{rh:.1f}" fill="{t["wash"]}" stroke="{t["ink"]}" stroke-width="1.5"/>')
            for k in range(min(p, len(stages))):
                fill, on = colors[k % 3]
                for (x, y, s) in stages[k]:
                    out.append(f'<rect x="{ox + x*scale:.1f}" y="{top + y*scale:.1f}" width="{s*scale:.1f}" height="{s*scale:.1f}" '
                               f'fill="{fill}" stroke="{t["ring"]}" stroke-width="1.5"/>')
                    if s * scale >= 26:
                        out.append(text(ox + (x + s/2)*scale, top + (y + s/2)*scale + 5, s, on, 12 if s * scale < 34 else 13, "middle", 600))
            if p == n_panels - 2 and zoom > 1.5:
                out.append(f'<rect x="{ox + lx*scale - 3:.1f}" y="{top + ly*scale - 3:.1f}" width="{lw*scale + 6:.1f}" height="{lh*scale + 6:.1f}" '
                           f'fill="none" stroke="{t["ink"]}" stroke-width="1.5"/>')
        else:
            zs = scale * zoom
            zx, zy = ox, top + (rh - lh * zs) / 2
            fill, on = colors[(len(stages) - 1) % 3]
            for (x, y, s) in last:
                out.append(f'<rect x="{zx + (x-lx)*zs:.1f}" y="{zy + (y-ly)*zs:.1f}" width="{s*zs:.1f}" height="{s*zs:.1f}" '
                           f'fill="{fill}" stroke="{t["ring"]}" stroke-width="1.5"/>')
                if s * zs >= 26:
                    out.append(text(zx + (x - lx + s/2)*zs, zy + (y - ly + s/2)*zs + 5, s, on, 12, "middle", 600))
            out.append(text(ox, top - 10, f"step {p} · zoomed in ×{zoom:.1f}", t["muted"], 12))
        c1, c2, c3 = caps[p]
        out.append(text(ox, top + rh + 26, c1, t["ink"], 14, "start", 650))
        out.append(text(ox, top + rh + 46, c2, t["ink2"], 13))
        out.append(text(ox, top + rh + 64, c3, t["ink2"], 13))
        if p == 0:
            out.append(text(ox, top - 10, "the problem", t["muted"], 12))
        elif not (p == n_panels - 1 and zoom > 1.5):
            out.append(text(ox, top - 10, f"step {p}", t["muted"], 12))
    return svg(W, H, "".join(out), f"Euclid's algorithm on {a} and {b} drawn as squares cut from a rectangle")


def nice_ticks(vmax, n=5):
    raw = vmax / n
    mag = 10 ** len(str(int(raw))) / 10 if raw >= 1 else 1
    step = min((s * mag for s in (1, 2, 2.5, 5, 10) if s * mag >= raw), default=raw)
    ticks, v = [], 0
    while v <= vmax + 1e-9:
        ticks.append(v)
        v += step
    if ticks[-1] < vmax:
        ticks.append(ticks[-1] + step)
    return ticks


def line_chart(series, xs_ticks, y_ticks, t, title, xlabel, ylabel, notes=()):
    """series: list of dict(name, points=[(x, y)], color, markers(bool), label)."""
    W, H = 720, 360
    L, R, T, B = 56, 210, 40, 52
    xmin = min(x for s in series for x, _ in s["points"]); xmax = max(x for s in series for x, _ in s["points"])
    ymax = y_ticks[-1]
    X = lambda x: L + (x - xmin) / (xmax - xmin) * (W - L - R)
    Y = lambda y: H - B - y / ymax * (H - T - B)
    out = []
    for v in y_ticks:
        out.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="{t["grid"] if v else t["axis"]}" stroke-width="1"/>')
        out.append(text(L - 8, Y(v) + 4, f"{v:,.0f}", t["muted"], 12, "end"))
    for v in xs_ticks:
        out.append(text(X(v), H - B + 20, v, t["muted"], 12, "middle"))
    out.append(text((L + W - R) / 2, H - 12, xlabel, t["ink2"], 13, "middle"))
    out.append(text(L - 8, T - 18, ylabel, t["ink2"], 13, "start"))
    for s in series:
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in s["points"])
        out.append(f'<polyline points="{pts}" fill="none" stroke="{s["color"]}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>')
        if s.get("markers"):
            for x, y in s["points"]:
                out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="4" fill="{s["color"]}" stroke="{t["ring"]}" stroke-width="2"/>')
        lx, ly = s["points"][-1]
        out.append(f'<line x1="{X(lx)+10:.1f}" y1="{Y(ly)+s.get("dy",0):.1f}" x2="{X(lx)+22:.1f}" y2="{Y(ly)+s.get("dy",0):.1f}" stroke="{s["color"]}" stroke-width="2"/>')
        for i, part in enumerate(s["label"]):
            out.append(text(X(lx) + 28, Y(ly) + s.get("dy", 0) + 4 + i * 16, part, t["ink"] if i == 0 else t["ink2"], 13, "start", 600 if i == 0 else 400))
    for (x, y, s) in notes:
        out.append(text(X(x), Y(y), s, t["ink2"], 13))
    return svg(W, H, "".join(out), title)


def histogram(hist, t, title, highlight):
    W, H = 720, 320
    L, R, T, B = 64, 20, 40, 52
    xs = [s for s, _ in hist]
    ymax = nice_ticks(max(c for _, c in hist))[-1]
    yt = nice_ticks(max(c for _, c in hist))
    slot = (W - L - R) / len(hist)
    bw = min(24, slot - 2)
    Y = lambda y: H - B - y / ymax * (H - T - B)
    out = []
    for v in yt:
        out.append(f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W-R}" y2="{Y(v):.1f}" stroke="{t["grid"] if v else t["axis"]}" stroke-width="1"/>')
        out.append(text(L - 8, Y(v) + 4, f"{v:,.0f}", t["muted"], 12, "end"))
    for i, (s, c) in enumerate(hist):
        x = L + i * slot + (slot - bw) / 2
        y = Y(c)
        h = Y(0) - y
        r = min(4, h / 2, bw / 2)
        color = t["blue"]
        if h > 0:
            out.append(f'<path d="M{x:.1f},{Y(0):.1f} V{y + r:.1f} Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f} H{x + bw - r:.1f} '
                       f'Q{x + bw:.1f},{y:.1f} {x + bw:.1f},{y + r:.1f} V{Y(0):.1f} Z" fill="{color}"/>')
        if s % 5 == 0:
            out.append(text(x + bw / 2, H - B + 20, s, t["muted"], 12, "middle"))
        if s == highlight:
            out.append(text(x + bw / 2, y - 10, f"{c:,} pairs took {s} steps", t["ink"], 13, "middle", 600))
    out.append(text((L + W - R) / 2, H - 12, "division steps", t["ink2"], 13, "middle"))
    out.append(text(L - 8, T - 18, "random pairs", t["ink2"], 13, "start"))
    return svg(W, H, "".join(out), title)


def segments_figure(t):
    """A drawn figure in the style of Elements Book VII, where numbers are line segments (not a copy of any manuscript)."""
    W, H = 520, 200
    u = 0.38                     # pixels per unit; AB = 1071, CD = 462 as in the worked example
    out = []
    def seg(y, length, color, l1, l2, label):
        out.append(f'<line x1="40" y1="{y}" x2="{40 + length*u:.1f}" y2="{y}" stroke="{color}" stroke-width="6" stroke-linecap="butt"/>')
        out.append(text(32, y + 5, l1, t["ink"], 15, "end", 600))
        out.append(text(48 + length*u, y + 5, l2, t["ink"], 15, "start", 600))
        out.append(text(40 + length*u/2, y - 12, label, t["ink2"], 12, "middle"))
    seg(50, 1071, t["red"], "A", "B", "AB = 1071")
    seg(110, 462, t["blue"], "C", "D", "CD = 462")
    # ΓΔ measured off along AB twice, leaving a remainder
    for i in range(2):
        out.append(f'<line x1="{40 + i*462*u:.1f}" y1="150" x2="{40 + (i+1)*462*u - 2:.1f}" y2="150" stroke="{t["blue"]}" stroke-width="6"/>')
    out.append(f'<line x1="{40 + 924*u:.1f}" y1="150" x2="{40 + 1071*u:.1f}" y2="150" stroke="{t["yellow"]}" stroke-width="6"/>')
    out.append(text(40, 178, "CD measured off along AB twice leaves a remainder of 147", t["ink2"], 12))
    return svg(W, H, "".join(out), "Numbers as line segments, in the style of Euclid's Book VII figures")


def write_pair(name, fn):
    for theme, t in THEMES.items():
        (ASSETS / f"{name}-{theme}.svg").write_text(fn(t))


def picture(name, alt, width=None):
    w = f' width="{width}"' if width else ""
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="assets/{name}-dark.svg">\n'
            f'  <img src="assets/{name}-light.svg" alt="{html.escape(alt)}"{w}>\n</picture>')


# ----------------------------------------------------------------------------------------------------------------------
# 3. the Java shown in "Prove it", copied verbatim from the program
# ----------------------------------------------------------------------------------------------------------------------
def java_member(src: str, signature: str) -> str:
    """A method copied verbatim from the program, with the comment directly above it, de-indented by one level."""
    lines = src.split("\n")
    i = next(k for k, l in enumerate(lines) if signature in l)
    start = i
    while start > 0 and lines[start - 1].strip().startswith(("/**", "*", "//")):
        start -= 1
    depth, end = 0, i
    for k in range(i, len(lines)):
        depth += lines[k].count("{") - lines[k].count("}")
        if depth == 0 and "{" in "".join(lines[i:k + 1]):
            end = k
            break
    return "\n".join(l[4:] if l.startswith("    ") else l for l in lines[start:end + 1])


def big_as_strings(x):
    """JavaScript numbers are doubles: send integers of 2^53 and above as strings so no digits are lost."""
    if isinstance(x, bool):
        return x
    if isinstance(x, int) and abs(x) >= 2 ** 53:
        return str(x)
    if isinstance(x, list):
        return [big_as_strings(v) for v in x]
    if isinstance(x, dict):
        return {k: big_as_strings(v) for k, v in x.items()}
    return x


def main():
    out = (CODE / "expected-output.txt").read_text()
    d = parse(out)
    src = (CODE / "EuclidsAlgorithm.java").read_text()
    ASSETS.mkdir(parents=True, exist_ok=True)
    a, b = 1071, 462
    trace = d["trace"][f"{a},{b}"]
    g = trace[-1][2]

    write_pair("euclid-squares", lambda t: strip_figure(a, b, trace, t))
    worst = d["worst"]
    write_pair("worst-case", lambda t: line_chart(
        [dict(name="Lamé", points=[(w["digits"], w["lame"]) for w in worst], color=t["red"], markers=False,
              label=["Lamé's bound", "5 × digits"], dy=-10),
         dict(name="worst", points=[(w["digits"], w["steps"]) for w in worst], color=t["blue"], markers=True,
              label=["Worst case:", "consecutive Fibonacci", "numbers"], dy=12)],
        [1, 3, 6, 9, 12, 15, 18], nice_ticks(max(w["lame"] for w in worst)), t,
        "Division steps in the worst case, against Lamé's bound", "digits in the smaller number", "division steps"))
    avg = d["average"]
    write_pair("average-case", lambda t: line_chart(
        [dict(name="avg", points=[(v["digits"], v["mean"]) for v in avg], color=t["blue"], markers=True,
              label=[f"{avg[-1]['mean']:.1f} steps", "at 18 digits"])],
        [1, 3, 6, 9, 12, 15, 18], nice_ticks(max(v["mean"] for v in avg)), t,
        "Average division steps for random pairs", "digits in each number", "average division steps",
        notes=[(1.3, 37.5, f"+{d['slope']:.2f} steps per extra digit (measured, 6 to 18 digits)"),
               (1.3, 34.8, f"Heilbronn's formula 0.843 ln n predicts +{d['slope_predicted']:.2f}")]))
    mode = max(d["histogram"], key=lambda p: p[1])
    write_pair("steps-histogram", lambda t: histogram(d["histogram"], t, "How many division steps random 18-digit pairs take", mode[0]))
    write_pair("segments", segments_figure)

    data = dict(d)
    data["snippet"] = "\n\n".join(java_member(src, s) for s in ("static long gcd(long a, long b)", "static List<long[]> extendedRows(long a, long b)"))
    (BOOK / "data.json").write_text(json.dumps(data, indent=1))
    write_readme(d, trace, g, data["snippet"])
    if TEMPLATE.exists():
        page = TEMPLATE.read_text().replace("/*DATA*/null", json.dumps(big_as_strings(data)))
        (BOOK / "euclids-algorithm.html").write_text(page)
    print("figures, README and page written for Euclid's algorithm")


# ----------------------------------------------------------------------------------------------------------------------
# 4. the GitHub edition
# ----------------------------------------------------------------------------------------------------------------------
def write_readme(d, trace, g, snippet):
    A, B = 1071, 462
    bz = d["bezout"]
    cmp_rows = []
    labels = {(1071, 462): "the worked example", (89, 55): "consecutive Fibonacci numbers", (1000000, 1): "a huge and a tiny number"}
    for c in d["compare"]:
        lab = labels.get((c["a"], c["b"]))
        if lab is None:
            lab = "10-digit consecutive Fibonacci numbers" if c["gcd"] == 1 and c["subtracting"] - c["dividing"] <= 2 else "a random 18-digit pair"
        cmp_rows.append(f"| {c['a']:,} and {c['b']:,} ({lab}) | {c['gcd']} | {c['trying']:,} | {c['subtracting']:,} | **{c['dividing']}** | {c['binary']} |")
    ext_rows = "\n".join(
        f"| {i} | {'—' if i < 2 else q} | {r:,} | {s} | {t} | {s} × {A} {'−' if t < 0 else '+'} {abs(t)} × {B} = {s*A + t*B:,} |"
        for i, (q, r, s, t) in enumerate(d["extended"]))
    trace_rows = "\n".join(f"| {i+1} | {big:,} = {q} × {small:,} + {r:,} | {q} | {r:,} |" for i, (big, q, small, r) in enumerate(trace))
    small = d["trace"]["48,18"]
    ex100 = next(e for e in d["exhaustive"] if e["limit"] == 100)
    worst18 = d["worst"][-1]
    mode = max(d["histogram"], key=lambda p: p[1])
    big = next(c for c in d["compare"] if (c["a"], c["b"]) == (1000000, 1))
    md = f"""# Euclid's algorithm

*Era 1 · topic 7 · c. 300 BCE* · [Era 1 reference catalog](../reference-catalog.md#7-euclids-algorithm) · [Interactive edition](euclids-algorithm.html) · [Program](../../../code/era-01-the-first-algorithms/07-euclids-algorithm/)

> **Field note from the visiting historian.** Earlier procedures computed a value. This one stops on its own and is *proved* to work for every pair of numbers. Take the smaller from the larger, again and again; what is left at the end measures both. Twenty-three centuries later it still runs, in spirit unchanged, inside every encryption library.

| | |
|---|---|
| **When** | c. 300 BCE (the method probably predates Euclid) |
| **Where** | Alexandria; Euclid's *Elements*, Book VII, Propositions 1–2 |
| **What hurt** | Finding the greatest common measure of two numbers meant trying every candidate |
| **The fix** | Replace the pair (a, b) by (b, a mod b) until the remainder is 0 |
| **Cost** | At most 5 × the digits of the smaller number in division steps (Lamé, 1844) |
| **Atlas** | Ch. 4, *The Euclidean Algorithm*; Ch. 92, *Number Theory* |
| **Certainty** | **documented** (the text survives); **conjecture** for earlier origins |

## Where it sits in time

```mermaid
timeline
    title Era 1: the first algorithms
    c. 44,000 years ago : Notched bones (Border Cave)
    c. 3000 BCE : Written numerals and the first carry
    c. 1800 BCE : Babylonian place value and tables
                : The square root of 2 on YBC 7289
    c. 1550 BCE : Egyptian multiplication by doubling
    c. 300 BCE : Counting boards (Salamis tablet)
               : Euclid's algorithm (this topic)
    c. 250 BCE : Archimedes squeezes π
    c. 240 BCE : The sieve of Eratosthenes
```

## What hurt, and what fixed it

```mermaid
flowchart LR
  P0["Try every candidate<br/>until one divides both"]:::pain --> F1["Take the smaller from the larger<br/>Elements VII, c. 300 BCE"]:::fix
  F1 --> P1["1,000,000 and 1 need<br/>1,000,000 subtractions"]:::pain
  P1 --> F2["One division does a whole run<br/>(a mod b)"]:::fix
  F2 --> P2["The gcd alone is not enough:<br/>find x, y with ax + by = gcd"]:::pain
  P2 --> F3["Carry the steps back<br/>Aryabhata's pulverizer, 499 CE"]:::fix
  F3 --> P3["How slow can it get?"]:::pain
  P3 --> F4["Never more than 5 × digits<br/>Lamé, 1844"]:::fix
  classDef pain stroke:#d5352a,stroke-width:2px
  classDef fix stroke:#1f5ba8,stroke-width:2px
```

Red outlines are the pains; blue outlines are the fixes.

## The idea, as a picture

Two numbers are the two sides of a rectangle. Cut off the biggest square you can, as many times as it fits; then do the same to the piece that is left. When a piece is filled exactly by squares, the side of those squares measures both of the original sides. It is the greatest common divisor.

{picture("euclid-squares", f"Euclid's algorithm on {A} and {B} as squares cut from a rectangle: 2 squares of 462, 3 of 147, 7 of 21")}

The number of squares cut at each stage, **{", ".join(str(q) for q in d["quotients"])}**, is also the continued fraction {A}/{B} = [{d["quotients"][0]}; {", ".join(str(q) for q in d["quotients"][1:])}]. Every Euclid computation hides one.

Euclid himself drew numbers as line segments and measured one off along the other:

{picture("segments", "Numbers as line segments: AB = 1071 and CD = 462; CD measured off along AB twice leaves 147", 520)}

*Drawn for this book in the style of the* Elements*; not a copy of any manuscript.*

## Step by step

| Step | Division | Quotient (squares cut) | Remainder |
|---|---|---|---|
{trace_rows}

The last non-zero remainder, **{g}**, is gcd({A}, {B}).

> **Wrong turn.** Euclid subtracted, one copy at a time. That is fine for {A} and {B} ({next(c for c in d["compare"] if (c["a"], c["b"]) == (A, B))["subtracting"]} subtractions), but {big["a"]:,} and {big["b"]} need **{big["subtracting"]:,} subtractions** where a single division is enough. Division is subtraction done in bulk.

### Going backwards: the pulverizer

Run the steps in reverse and the remainders become combinations of the two starting numbers. Each row keeps the promise *remainder = s × {A} + t × {B}*:

| Row | Quotient | Remainder | s | t | Check |
|---|---|---|---|---|---|
{ext_rows}

So **{bz["g"]} = {bz["x"]} × {A} + {bz["y"]} × {B}** (Bézout's identity). Aryabhata called the method *kuttaka*, "pulverizing", because the numbers get smaller and smaller with each step. When the gcd is 1, *s* is the inverse of the first number modulo the second, and that inverse is how RSA key generation finds its matching exponent: {d["rsa"]["e"]} × {d["rsa"]["d"]:,} = 1 (mod {d["rsa"]["phi"]:,}).

## Four ways to find a gcd

Counts of the basic operations each method makes, from the program:

| Pair | gcd | Trying every candidate | Repeated subtraction (Euclid) | Division | Binary GCD (Stein) |
|---|---|---|---|---|---|
{chr(10).join(cmp_rows)}

Trying candidates grows with the size of the numbers. Subtraction can explode. Division grows only with the number of *digits*. Stein's binary method (published 1967) uses halving and subtraction, which suit hardware without fast division.

## How fast is it? Measured

The worst case is consecutive Fibonacci numbers: every quotient is 1, so each step takes away as little as possible. Lamé proved in 1844 that the steps never exceed five times the number of digits of the smaller number.

{picture("worst-case", "Worst-case division steps by digits of the smaller number, always at or below Lamé's bound of 5 times the digits")}

For random numbers it is much better. The average grows by about two steps per extra digit, as Heilbronn's formula 0.843 ln n predicts:

{picture("average-case", f"Average division steps for random pairs rise steadily to {d['average'][-1]['mean']:.1f} at 18 digits")}

And for random 18-digit pairs the counts bunch tightly around the middle; even the slowest pair needed {d["histogram"][-1][0]} steps, well under Lamé's {worst18["lame"]}:

{picture("steps-histogram", f"Distribution of division steps for {d['hist_samples']:,} random 18-digit pairs, peaking at {mode[0]} steps")}

## How ideas combined

```mermaid
flowchart TB
  A["Repeated subtraction<br/>(anthyphairesis)"] -->|"⊕ division"| B["Euclid's algorithm"]
  B -->|"⊕ carry the steps back"| C["Extended Euclid<br/>Aryabhata, 499 CE"]
  C -->|"⊕ arithmetic mod n"| D["Modular inverse"]
  E["Egyptian doubling<br/>(topic 5)"] -->|"⊕ squaring"| F["Square-and-multiply"]
  D --> G["RSA, 1977"]
  F --> G
  B -->|"⊕ Fibonacci numbers"| H["Lamé's bound, 1844<br/>an early running-time analysis"]
  B -->|"⊕ halving"| I["Binary GCD<br/>Stein, 1967"]
  B -->|"⊕ millions of public keys"| J["Weak-key hunt, 2012"]
  B -.->|"same quotients"| K["Continued fractions"]
```

*A ⊕ B = C: a new algorithm is an older idea combined with a new one.*

## Full circle

In 2012 a team from UC San Diego and the University of Michigan collected the public keys of millions of internet hosts and computed the greatest common divisors between them. Keys made with poor randomness share a prime factor, and a shared factor gives the private key away: they recovered RSA private keys for **0.50% of TLS hosts and 0.03% of SSH hosts** (*Mining Your Ps and Qs*, USENIX Security 2012; [factorable.net](https://factorable.net/)). An algorithm from 300 BCE found the weak locks.

## Pause and try

<details>
<summary><b>1.</b> Find gcd(48, 18). How many divisions does it take?</summary>

{"<br/>".join(f"{big:,} = {q} × {sm:,} + {r:,}" for big, q, sm, r in small)}<br/>
So gcd(48, 18) = **{small[-1][2]}**, in **{len(small)}** divisions.
</details>

<details>
<summary><b>2.</b> Why must the algorithm stop?</summary>

Each remainder is smaller than the number it was divided by, so the second number of the pair gets strictly smaller at every step. A list of whole numbers that keeps getting smaller cannot go on forever, so it reaches 0.
</details>

<details>
<summary><b>3.</b> Which pair of numbers below 100 makes the algorithm work hardest?</summary>

**({ex100["a"]}, {ex100["b"]})**, two consecutive Fibonacci numbers, with **{ex100["steps"]}** divisions. The program checked every pair below 100.
</details>

<details>
<summary><b>4.</b> Write {g} as a combination of {A} and {B}.</summary>

{bz["g"]} = **{bz["x"]}** × {A} + **{bz["y"]}** × {B}. Check: {bz["x"]*A:,} + {bz["y"]*B:,} = {bz["g"]}.
</details>

<details>
<summary><b>5.</b> Is it faster to find gcd(1,000,000, 1) by subtraction or by division?</summary>

Division: **{big["dividing"]}** step against **{big["subtracting"]:,}** subtractions.
</details>

## The objects

| | Object | What it shows | Licence |
|---|---|---|---|
| <img src="https://library.si.edu/sites/default/files/books/covers/preclarissimusl00eucl_cover.jpg" alt="Image of the 1482 printed edition of Euclid's Elements, from Smithsonian Libraries" width="140"> | **The first printed edition** of the *Elements*, printed by Erhard Ratdolt, Venice, 25 May 1482 | [Smithsonian Libraries' digitised copy](https://library.si.edu/digital-library/book/preclarissimusl00eucl) | CC0 (public domain), photo shown |
| — | **MS. D'Orville 301**, Bodleian Library: a Byzantine manuscript of the *Elements*, dated 888, written by Stephanos the clerk | [Catalogue entry](https://medieval.bodleian.ox.ac.uk/catalog/manuscript_4146) with links to the digital facsimile | Most Digital Bodleian images are CC BY-NC 4.0; linked, not copied |
| — | **P. Oxy. 29**, Penn Museum E2748: a papyrus fragment of Book II, Proposition 5, with its diagram. The museum dates it 200–400 CE; the papyrologist Eric Turner argued for 75–125 CE (**disputed**) | [Penn Museum record](https://collections.penn.museum/collections/object/63505) · [Bill Casselman's photographs and notes](https://personal.math.ubc.ca/~cass/Euclid/papyrus/papyrus.html) | No licence stated; linked, not copied |

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Euclid's Algorithm — Numberphile](https://www.youtube.com/watch?v=6Y3jHHE_hbA) | The algorithm and its Fibonacci connection |
| Start | [The Euclidean Algorithm (Finding the GCD/GCF) — Houston Math Prep](https://www.youtube.com/watch?v=SR-jmdjzw-Y) | Worked examples, step by step |
| Start | [Here's looking at Euclid — Gresham College, Robin Wilson](https://www.youtube.com/watch?v=9O97Xad-iTQ) | Greek mathematics and the *Elements* |
| Deeper | [MIT 6.042J Lecture 4 — MIT OpenCourseWare](https://www.youtube.com/watch?v=NuY7szYSXSw) | GCD, Euclid's algorithm and the Pulverizer |
| Deeper | [Euclid's Algorithm — Cut the Knot](https://www.cut-the-knot.org/blue/Euclid.shtml) | Why gcd(a, b) = gcd(b, r), and Bézout's identity |
| Deeper | [Euclidean Algorithm — Wolfram MathWorld](https://mathworld.wolfram.com/EuclideanAlgorithm.html) | Lamé's bound, the Fibonacci worst case, average steps |
| Scholar | [Elements VII.1](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII1.html) and [VII.2](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII2.html) — D. E. Joyce | The propositions themselves |
| Scholar | [Origins of the analysis of the Euclidean algorithm — J. Shallit, Historia Mathematica (1994)](https://www.sciencedirect.com/science/article/pii/S0315086084710317) | Who first bounded the running time |
| Scholar | [Aryabhata I — MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Aryabhata_I/) | The *kuttaka* ("pulverizer") and its link to Euclid's algorithm |
| Scholar | [Rivest, Shamir and Adleman (1977)](https://people.csail.mit.edu/rivest/Rsapaper.pdf) | "Use the following variation of Euclid's algorithm" to compute the RSA exponents |

## Prove it

The program behind every number on this page: [EuclidsAlgorithm.java](../../../code/era-01-the-first-algorithms/07-euclids-algorithm/EuclidsAlgorithm.java). It makes **{d["checks"]:,} checks**: every method against Java's `BigInteger.gcd`, Bézout's identity on 200,000 random pairs, Lamé's bound exhaustively below 1,000, and the continued fractions rebuilt exactly. The heart of it:

```java
{snippet}
```

Run it with `java EuclidsAlgorithm.java` (JDK 17 or newer). These figures and tables are regenerated from its output by [`code/tools/figures/euclid_topic.py`](../../../code/tools/figures/euclid_topic.py).
"""
    (BOOK / "README.md").write_text(md)


if __name__ == "__main__":
    main()
