"""Era 1, topic 8: Archimedes squeezes pi. Every number is parsed from ArchimedesPi.java's output."""
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"poly": [], "rounded": []}
    for ln in text.splitlines():
        if m := re.match(r"polygon (\d+): inside ([\d.]+) outside ([\d.]+) gap ([\d.]+)(?: \(gap shrank ([\d.]+) times\))?$", ln):
            d["poly"].append(dict(n=int(m.group(1)), inside=m.group(2), outside=m.group(3), gap=m.group(4), shrink=m.group(5)))
        elif m := re.match(r"archimedes: 223/71 = ([\d.]+) < inside 96-gon ([\d.]+) ; outside 96-gon ([\d.]+) < 22/7 = ([\d.]+) ; pi = ([\d.]+)$", ln):
            d["arch"] = dict(lo=m.group(1), in96=m.group(2), out96=m.group(3), hi=m.group(4), pi=m.group(5))
        elif m := re.match(r"sqrt3: 265/153 = ([\d.]+) < sqrt\(3\) = ([\d.]+) < 1351/780 = ([\d.]+) ; convergents (\d+) and (\d+) of .*: (.+)$", ln):
            d["sqrt3"] = dict(lo=m.group(1), v=m.group(2), hi=m.group(3), il=int(m.group(4)), iu=int(m.group(5)), conv=m.group(6))
        elif m := re.match(r"archimedes-margin: his lower bound gives up ([\d.]+), his upper bound ([\d.]+)", ln):
            d["margin"] = (m.group(1), m.group(2))
        elif m := re.match(r"rounded (\d+) digits: every value rounded outward: ([\d.]+) < pi < ([\d.]+) at 96 sides, still valid; (.+?) Archimedes", ln):
            d["rounded"].append(dict(digits=int(m.group(1)), lo=m.group(2), hi=m.group(3), verdict=m.group(4)))
        elif m := re.match(r"doublings: gap below 10\^-d needs (.+)$", ln):
            d["doublings"] = [dict(places=int(a), n=int(b)) for a, b in re.findall(r"(\d+) places: (\d+) doublings", m.group(1))]
        elif m := re.match(r"extrapolate: inside 96-gon (\d+) correct places; \(2 x inside \+ outside\)/3 = ([\d.]+), (\d+) places; \(4 x inside96 - inside48\)/3 = ([\d.]+), (\d+) places$", ln):
            d["extra"] = dict(base=int(m.group(1)), combo=m.group(2), combo_p=int(m.group(3)), rich=m.group(4), rich_p=int(m.group(5)))
    d["checks"] = C.checks(text)
    return d


def polygons_figure(t, standalone):
    """Hexagon, 12-gon and 24-gon inside and outside a circle, side by side."""
    out = []
    R = 80
    for i, n in enumerate([6, 12, 24]):
        cx, cy = 110 + i * 240, 120
        out.append(C.circle(cx, cy, R, "none", t["ink"], 1.5))
        for kind, r, col in [("in", R, t["blue"]), ("out", R / math.cos(math.pi / n), t["red"])]:
            pts = " ".join(f"{cx + r * math.cos(2 * math.pi * k / n + math.pi / n * (kind == 'out')):.1f},{cy + r * math.sin(2 * math.pi * k / n + math.pi / n * (kind == 'out')):.1f}" for k in range(n))
            out.append(f'<polygon points="{pts}" style="fill:none;stroke:{col};stroke-width:2"/>')
        out.append(C.text(cx, 236, f"{n} sides", t["ink"], 14, "middle", 700))
    out.append(C.text(20, 20, "Blue: inside, too short. Red: outside, too long. The circle is trapped between them.", t["ink2"], 13))
    return C.svg_doc(720, 250, "".join(out), "Hexagons, 12-gons and 24-gons inside and outside a circle", t, standalone, 0.55)


PI_HTML = """
<div class="board pi-board">
  <div style="min-width:0">
    <div class="controls">
      <button id="pi-dbl" class="primary" type="button">Double the sides</button>
      <button id="pi-reset" type="button">Back to hexagons</button>
    </div>
    <div class="pi-views">
      <svg id="pi-svg" viewBox="0 0 320 320" role="img" aria-label="A circle trapped between two polygons"></svg>
      <svg id="pi-zoom" viewBox="0 0 200 320" role="img" aria-label="A magnified slice where the polygons meet the circle"></svg>
    </div>
    <p class="zoomnote" id="pi-note"></p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The trap</div>
    <ol class="steps" id="pi-steps"></ol>
    <div class="result" id="pi-result" aria-live="polite"></div>
  </div>
</div>
"""

PI_CSS = """
.pi-board .pi-views{display:grid;grid-template-columns:3fr 2fr;gap:12px}
.pi-board svg{background:var(--wash);width:100%;height:auto}
.pi-board .steps li{font-size:12.5px}
"""

PI_JS = r"""
(() => {
  const svg = document.getElementById("pi-svg"), zoom = document.getElementById("pi-zoom");
  if (!svg) return;
  const ROWS = ROWS_JSON;
  let k = 0;
  const cx = 160, cy = 160, R = 130;
  function poly(parent, n, r, rot, color, scaleFn) {
    const pts = [];
    for (let i = 0; i < n; i++) { const a = 2 * Math.PI * i / n + rot; pts.push(scaleFn(r * Math.cos(a), r * Math.sin(a))); }
    sv("polygon", {points: pts.map(p => p.join(",")).join(" "), fill: "none", stroke: color, "stroke-width": 2}, parent);
  }
  function draw() {
    const n = ROWS[k].n;
    svg.innerHTML = ""; zoom.innerHTML = "";
    sv("circle", {cx, cy, r: R, fill: "none", stroke: "var(--ink)", "stroke-width": 1.5}, svg);
    poly(svg, n, R, 0, "var(--blue)", (x, y) => [cx + x, cy + y]);
    poly(svg, n, R / Math.cos(Math.PI / n), Math.PI / n, "var(--red)", (x, y) => [cx + x, cy + y]);
    const bx = cx + R * Math.cos(Math.PI / n), by = cy + R * Math.sin(Math.PI / n);
    sv("rect", {x: bx - 12, y: by - 12, width: 24, height: 24, fill: "none", stroke: "var(--muted)", "stroke-dasharray": "3 3"}, svg);
    // zoom: turn the picture so the corner of the outside polygon at angle pi/n lies on the x-axis, then magnify
    // around the circle there. The inside polygon's side is the vertical line x = R cos(pi/n).
    const t = Math.PI / n, xin = R * Math.cos(t), xout = R / Math.cos(t);
    const mag = 150 / (xout - xin), zx = 100, zy = 160;
    const map = (x, y) => [zx + (x - R) * mag, zy - y * mag];
    const half = 170 / mag, th = Math.asin(Math.min(1, half / R));
    const arc = [];
    for (let i = 0; i <= 60; i++) { const a = -th + 2 * th * i / 60; arc.push(map(R * Math.cos(a), R * Math.sin(a))); }
    sv("polyline", {points: arc.map(q => q.join(",")).join(" "), fill: "none", stroke: "var(--ink)", "stroke-width": 1.5}, zoom);
    const i1 = map(xin, R * Math.sin(t)), i2 = map(xin, -R * Math.sin(t));
    sv("line", {x1: i1[0], y1: i1[1], x2: i2[0], y2: i2[1], stroke: "var(--blue)", "stroke-width": 2}, zoom);
    const ov = map(xout, 0), o1 = map(xout * Math.cos(2 * t), xout * Math.sin(2 * t)), o2 = map(xout * Math.cos(2 * t), -xout * Math.sin(2 * t));
    sv("polyline", {points: [o1, ov, o2].map(q => q.join(",")).join(" "), fill: "none", stroke: "var(--red)", "stroke-width": 2}, zoom);
    sv("rect", {x: 4, y: 4, width: 128, height: 20, fill: "var(--wash)"}, zoom);
    sv("text", {x: i2[0] + 4, y: 312, fill: "var(--blue)", "font-size": 11, "font-weight": 700}, zoom, "inside");
    sv("text", {x: ov[0] - 4, y: 312, "text-anchor": "end", fill: "var(--red)", "font-size": 11, "font-weight": 700}, zoom, "outside");
    sv("text", {x: 8, y: 18, fill: "var(--muted)", "font-size": 11}, zoom, `magnified ${fmt(Math.round(mag))} times`);
    const steps = document.getElementById("pi-steps");
    steps.innerHTML = "";
    ROWS.slice(0, k + 1).forEach((r, i) => el("li", {class: i === k ? "current" : ""}, steps, `${r.n} sides: ${r.inside} < π < ${r.outside}`));
    const row = ROWS[k];
    document.getElementById("pi-result").innerHTML = `Gap: <b>${row.gap}</b>${row.shrink ? ` (${row.shrink} times smaller than before)` : ""}.` +
      (n === 96 ? ` Archimedes rounded these outward to <b>223/71 < π < 22/7</b>.` : "");
    document.getElementById("pi-note").textContent = n === 96 ? "Four doublings from the hexagon: Archimedes stopped here." : "The right-hand view magnifies the boxed slice so the gap stays visible.";
    document.getElementById("pi-dbl").disabled = k === ROWS.length - 1;
  }
  document.getElementById("pi-dbl").addEventListener("click", () => { if (k < ROWS.length - 1) { k++; draw(); } });
  document.getElementById("pi-reset").addEventListener("click", () => { k = 0; draw(); });
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Archimedes' squeeze combined with other ideas, from exhaustion to interval arithmetic")
    W, H = 210, 86
    nodes = {
        "exh": (180, 20, "Exhaustion", "", "Euclid's Elements, Book XII", "ink"),
        "rt": (610, 20, "Safe bounds for roots", "265/153 < √3 < 1351/780", "topic 4's square roots", "ink"),
        "sq": (395, 150, "Squeezing π", "⊕ two polygons that close in", "Measurement of a Circle, c. 250 BCE", "red"),
        "zu": (20, 300, "355/113", "", "Zu Chongzhi (430–501)", "ink"),
        "vc": (270, 300, "35 places", "⊕ polygons of 2^62 sides", "van Ceulen, by 1610", "ink"),
        "hy": (520, 300, "Combine the bounds", "⊕ cancel the main error", "Huygens, 1654", "ink"),
        "se": (770, 300, "Series for π", "⊕ infinite sums", "era 3", "ink"),
        "ia": (395, 460, "Interval arithmetic", "⊕ computers round outward", "Moore, 1966", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("exh", "sq", ports=("bottom", "top"))
    D.edge("rt", "sq", ports=("bottom", "top"))
    D.edge("sq", "zu", ports=("bottom", "top"), dashed=True)
    for k in ("vc", "hy", "se"):
        D.edge("sq", k, ports=("bottom", "top"))
    D.edge("vc", "ia", ports=("bottom", "top:0.3"), dashed=True)
    D.edge("sq", "ia", ports=("bottom:0.5", "top:0.5"))
    D.text(20, 600, "Dashed: the same goal or the same habit of mind, not a documented line of descent.", "caption")
    return D


def chain(d):
    p = d["poly"]
    dbl = {x["places"]: x["n"] for x in d["doublings"]}
    steps = [
        ("π cannot be written as a fraction", "Trap it: a polygon inside is too short, one outside too long", "Measurement of a Circle"),
        (f"Hexagons only say {p[0]['inside']} < π < {p[0]['outside'][:6]}", f"Double the sides: each doubling cuts the gap about {p[-1]['shrink'][:1]} times", "6, 12, 24, 48, 96 sides"),
        ("Each doubling needs a square root that cannot be exact", "Round every bound the safe way: lower bounds down, upper bounds up", "265/153 < √3 < 1351/780"),
        (f"35 places would need {dbl[35]} doublings", "Combine the bounds to cancel the main error; later, infinite series", "Huygens, 1654; era 3"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from an inexpressible number to guaranteed bounds")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx = (L, R) if i % 2 == 0 else (R, L)
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx, y, bw, rowh, [("THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="fixed by", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


def ladder(d):
    D = Diagram(1000, 230, "Doubling the sides from 6 to 96: the bounds close in")
    for i, p in enumerate(d["poly"]):
        D.node(i, 20 + i * 196, 50, 166, 110, [(f"{p['n']} sides", "title"), (f"> {p['inside'][:8]}", "combo"), (f"< {p['outside'][:8]}", "combo"), (f"gap {p['gap']}", "note")],
               color="red" if p["n"] == 96 else "ink")
        if i:
            D.edge(i - 1, i, ports=("right", "left"))
    D.text(20, 30, "EACH ARROW DOUBLES THE SIDES: HARMONIC MEAN FOR THE OUTSIDE, GEOMETRIC MEAN FOR THE INSIDE", "tag")
    D.text(20, 200, f"π = {d['arch']['pi']}… lies inside every box. The gap shrinks about four times per doubling.", "caption")
    return D


def safe_rounding(d):
    a = d["arch"]
    m = d["margin"]
    D = Diagram(1000, 260, "Archimedes rounded his 96-gon bounds outward, never inward")
    D.node("in", 20, 40, 280, 76, [("Inside 96-gon (exact)", "title"), (a["in96"], "combo")], color="blue")
    D.node("lo", 20, 160, 280, 76, [("Rounded down: 223/71", "title"), (f"{a['lo']}, gives up {m[0]}", "combo")], color="blue")
    D.node("pi", 360, 100, 280, 76, [("π", "big"), (a["pi"] + "…", "combo")], color="red")
    D.node("out", 700, 40, 280, 76, [("Outside 96-gon (exact)", "title"), (a["out96"], "combo")], color="blue")
    D.node("hi", 700, 160, 280, 76, [("Rounded up: 22/7", "title"), (f"{a['hi']}, gives up {m[1]}", "combo")], color="blue")
    D.edge("in", "lo", ports=("bottom", "top"))
    D.edge("out", "hi", ports=("bottom", "top"))
    D.text(500, 30, "SMALLER ←   → BIGGER", "tag", "middle")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def ordinal(n):
    return f"{n}{'th' if 10 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"


def build(ctx):
    import json
    d = parse(ctx["out"])
    rows = [dict(n=p["n"], inside=p["inside"][:9], outside=p["outside"][:9], gap=p["gap"], shrink=(p["shrink"] or "")[:5]) for p in d["poly"]]
    js = PI_JS.replace("ROWS_JSON", json.dumps(rows))
    a, s3, ex = d["arch"], d["sqrt3"], d["extra"]
    dbl = {x["places"]: x["n"] for x in d["doublings"]}
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Archimedes combined the method of exhaustion (squeeze a curved figure between straight ones) with safe numerical bounds for square roots, and turned a proof technique into a computation. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Archimedes' squeeze. Blue: the same guarantee built into computers."),
        ]),
        dict(id="trap", eyebrow="Try it", title="Trap the circle", toc="Try it", blocks=[
            dict(type="p", text="A polygon inside a circle is shorter than the circle; a polygon outside is longer. Double the number of sides and both get closer. Archimedes started from hexagons and doubled four times."),
            dict(type="widget", html=PI_HTML, js=js, css=PI_CSS,
                 fallback=dict(type="svg", name="polygons", draw=polygons_figure, alt="Hexagons, 12-gons and 24-gons inside and outside a circle"),
                 note="In the interactive edition you can double the sides yourself, with a magnified view of the gap."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="steps", eyebrow="Step by step", title="From hexagons to 96 sides", toc="Step by step", blocks=[
            dict(type="diagram", name="ladder", diagram=ladder(d)),
            dict(type="table", head=["Sides", "Inside (too short)", "Outside (too long)", "Gap", "Gap shrank"], num=[0, 3, 4], hl=len(d["poly"]) - 1,
                 rows=[[p["n"], p["inside"], p["outside"], p["gap"], (p["shrink"] + "×") if p["shrink"] else "—"] for p in d["poly"]]),
            dict(type="p", text="Proposition 3 in Heath's translation: \"The ratio of the circumference of any circle to its diameter is less than 3 1/7 but greater than 3 10/71.\""),
            dict(type="diagram", name="rounding", diagram=safe_rounding(d)),
            dict(type="callout", kind="key", label="Key idea",
                 text=f"Every square root on the way had to be replaced by a fraction, and the fraction had to err on the safe side. For √3 Archimedes used 265/153 < √3 < 1351/780 ({s3['lo']} < {s3['v']} < {s3['hi']}). "
                      f"Both are continued-fraction convergents of √3: the best fractions for √3 for their size, which Euclid's algorithm (topic 7) produces. They are the {ordinal(s3['il'] + 1)} and {ordinal(s3['iu'] + 1)} in the list {s3['conv']}. He does not say how he found them; reconstructions differ (**disputed**)."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How good is a guaranteed answer?", toc="Measured", blocks=[
            dict(type="p", text="The program redid the whole computation the way a hand computer must: every intermediate value rounded outward to a fixed number of digits. The bounds always stay valid; they just get looser."),
            dict(type="table", head=["Digits kept at every step", "Bounds at 96 sides", "Compared with 223/71 and 22/7"], num=[0],
                 rows=[[r["digits"], f"{r['lo']} < π < {r['hi']}", r["verdict"] + " Archimedes' bounds"] for r in d["rounded"]]),
            dict(type="p", text=f"Rounding blindly needs six digits at every step to be at least as tight as Archimedes' 223/71 and 22/7; at five digits it is looser. To shrink the gap further takes many more doublings. To bring it below "
                                + "; ".join(f"10⁻{x['places']}: {x['n']} doublings" for x in d["doublings"]) + ". "
                                f"Ludolph van Ceulen worked out π to 35 places with polygons of 2^62 sides; he died in 1610 and the full result was published in 1621. By this program's count, a gap below 10⁻³⁵ needs {dbl[35]} doublings from the hexagon, 6 × 2^{dbl[35]} sides."),
            dict(type="p", text=f"Combining the bounds helps more than doubling. The 96-gon's inside value is right to {ex['base']} places (its error is below 10⁻{ex['base']}); (2 × inside + outside) / 3 gives **{ex['combo_p']}**, and (4 × inside of the 96-gon − inside of the 48-gon) / 3 gives **{ex['rich_p']}**. "
                                "Huygens found improvements of this kind in 1654; Richardson later made the trick general."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Computers that round outward", toc="Full circle", blocks=[
            dict(type="p", text="Archimedes did not give *an* answer; he gave an answer with a guaranteed error bound. In 1966 Ramon Moore's book *Interval Analysis* made the same habit into a branch of computing: carry a lower and an upper bound through every step, rounding each the safe way, and the true answer is guaranteed to lie between them."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program's interval run is exactly that: with 6 digits kept it proves {d['rounded'][2]['lo']} < π < {d['rounded'][2]['hi']}, no matter how the rounding falls. Calling Archimedes' method the first algorithm with a guaranteed error bound is this book's framing (**conjecture**); MacTutor calls it \"the first theoretical calculation\" of π."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why is the hexagon inside a circle of diameter 1 exactly 3 long?", "Its six sides each equal the radius, 1/2, because the hexagon is made of six equilateral triangles: 6 × 1/2 = 3."),
            ("Is 22/7 bigger or smaller than π? And 223/71?", f"22/7 = {a['hi']} is bigger; 223/71 = {a['lo']} is smaller. π = {a['pi']}… lies between."),
            ("Why must a lower bound be rounded down?", "If it were rounded up it might pass π, and then it would no longer be a lower bound. Rounding the safe way keeps the guarantee."),
            ("Each doubling shrinks the gap about 4 times. Why 4?", "The error of an n-sided polygon shrinks like 1/n². Doubling n divides it by 2² = 4."),
            ("How many doublings from the hexagon bring the gap below 10⁻¹⁰?", f"**{dbl[10]}** doublings, a polygon of 6 × 2^{dbl[10]} sides."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Works of Archimedes", text="T. L. Heath's English translation (1897), including *Measurement of a Circle*. The surviving treatise is probably a fragment of a longer work (**disputed**).",
                 draw=C.draw_book, link="https://archive.org/details/worksofarchimede00arch", link_text="Internet Archive scan",
                 licence="Drawn placeholder; the 1897 book is scanned at the link."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Ludolph van Ceulen", "MacTutor History of Mathematics", "https://mathshistory.st-andrews.ac.uk/Biographies/Van_Ceulen/", "35 places of π from polygons of 2^62 sides, published in 1621"),
            ("deeper", "Interval Analysis (review)", "Science 158 (1967), review of R. E. Moore, Prentice-Hall 1966", "https://www.science.org/doi/10.1126/science.158.3799.365", "The 1966 book that made guaranteed bounds a branch of computing"),
        ]),
        C.prove_it_section(ctx, "ArchimedesPi", d["checks"],
                           "π between the polygons at every step, Archimedes' fractions outside the exact 96-gon values, his √3 bounds as convergents, and interval runs rounded outward at 4 to 7 digits.",
                           ["static BigDecimal[] doubleSides(BigDecimal a, BigDecimal b, MathContext mc)"]),
    ]
    return dict(
        title="Archimedes Squeezes Pi", date="c. 250 BCE",
        description="Era 1, topic 8 of The Algorithm Evolution Atlas: Archimedes traps π between polygons of 6 to 96 sides, with a doubling widget, diagrams and verified links.",
        lede="π cannot be written down exactly. Archimedes traps it instead: a polygon inside the circle is too short, one outside too long, and each doubling of the sides narrows the gap.",
        fieldnote="He does not give an answer; he gives an answer with a guaranteed error bound. After 6, 12, 24, 48 and 96 sides: 223/71 < π < 22/7.",
        card=[("When", "Measurement of a Circle, probably c. 250 BCE"),
              ("Where", "Syracuse, Sicily (**documented**)"),
              ("What hurt", "A needed quantity that no exact number expresses"),
              ("The fix", "Two bounds that close in, each step the same formula applied to the last"),
              ("Cost", "Each doubling cuts the gap about 4 times"),
              ("Atlas", "Ch. 6.4–6.5 Archimedes and numerical approximation; exhaustion")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ArchimedesPi.java`.",
    )
