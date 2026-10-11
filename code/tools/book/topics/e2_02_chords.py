"""Era 2, topic 2: Ptolemy's table of chords. Every number is parsed from PtolemyChords.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def from_sexa(s):
    """'1;2,50' -> 1 + 2/60 + 50/3600, exactly."""
    from fractions import Fraction
    whole, _, rest = s.partition(";")
    v = Fraction(int(whole))
    for i, dgt in enumerate(rest.split(",") if rest else []):
        v += Fraction(int(dgt), 60 ** (i + 1))
    return v


def to_sexa(v, places=2):
    n = round(v * 60 ** places)
    digits = []
    for _ in range(places):
        digits.insert(0, n % 60)
        n //= 60
    return f"{n};" + ",".join(map(str, digits))


def arc_value(s):
    """'1 1/2' -> 1.5, '3/4' -> 0.75, '36' -> 36."""
    total = 0.0
    for part in s.split():
        if "/" in part:
            n, d = part.split("/")
            total += int(n) / int(d)
        else:
            total += int(part)
    return total


def parse(text: str) -> dict:
    d = {"seeds": [], "route": [], "rows": []}
    for ln in text.splitlines():
        if m := re.match(r"theorem: (\d+) random quadrilaterals in a circle, largest relative gap (\S+)$", ln):
            d["theorem"] = dict(n=int(m.group(1)), gap=m.group(2))
        elif m := re.match(r"seed (\d+): (\S+) ; true (\S+)$", ln):
            d["seeds"].append(dict(arc=int(m.group(1)), value=m.group(2), true=m.group(3)))
        elif m := re.match(r"derive (12): (\S+) \(difference of 72 and 60\) ; to the second (\S+) ; true (\S+)$", ln):
            d["route"].append(dict(arc=m.group(1), rule="difference: 72° − 60°", work=m.group(2), table=m.group(3), true=m.group(4)))
        elif m := re.match(r"derive ([\d /]+): (\S+) \(half of ([\d /]+)\) ; to the second (\S+) ; true (\S+)$", ln):
            d["route"].append(dict(arc=m.group(1), rule=f"half of {m.group(3)}°", work=m.group(2), table=m.group(4), true=m.group(5)))
        elif m := re.match(r"squeeze 1: between (\S+) and (\S+), so (\S+) ; true (\S+)$", ln):
            d["squeeze"] = dict(lo=m.group(1), hi=m.group(2), value=m.group(3), true=m.group(4))
        elif m := re.match(r"derive 1/2: (\S+) \(half of 1\) ; true (\S+)$", ln):
            d["half"] = dict(value=m.group(1), true=m.group(2))
        elif m := re.match(r"chain: 360 entries by adding 1/2 degree each time: (\d+) right to the second, (\d+) one second off, worst (\d+) seconds off at ([\d /]+)$", ln):
            d["chain"] = dict(exact=int(m.group(1)), one=int(m.group(2)), worst=int(m.group(3)), at=m.group(4))
        elif m := re.match(r"anchored: restarting the sums at each known chord: (\d+) of 360 right to the second, worst (\d+) seconds off$", ln):
            d["anchored"] = dict(exact=int(m.group(1)), worst=int(m.group(2)))
        elif m := re.match(r"row ([\d /]+): chord (\S+) ; increment per minute (\S+)$", ln):
            d["rows"].append(dict(arc=m.group(1), chord=m.group(2), inc=m.group(3)))
        elif m := re.match(r"interpolate: every minute of arc from 0 to 180 degrees: worst error (\S+) seconds at (\d+) degrees (\d+) minutes ; curvature alone allows (\S+) seconds", ln):
            d["interp"] = dict(err=m.group(1), deg=int(m.group(2)), min=int(m.group(3)), bound=m.group(4))
        elif m := re.match(r"pi: 360 x (\S+) / 120 = (\S+) = 377/120 = (\S+) \(true (\S+)\)$", ln):
            d["pi"] = dict(c1=m.group(1), sexa=m.group(2), dec=m.group(3), true=m.group(4))
        elif m := re.match(r"root3: (\S+) / 60 = (\S+) = (\S+) \(true (\S+)\)$", ln):
            d["root3"] = dict(c120=m.group(1), sexa=m.group(2), dec=m.group(3), true=m.group(4))
        elif m := re.match(r"library: (\d+) random angles: table of (\d+) sines and cosines plus the sum rule, worst (\S+) units in the last place ; half-degree table with interpolation, worst error (\S+)$", ln):
            d["lib"] = dict(n=int(m.group(1)), size=int(m.group(2)), ulp=m.group(3), lin=m.group(4))
    d["checks"] = C.checks(text)
    return d


POLY = {36: ("decagon", 10), 60: ("hexagon", 6), 72: ("pentagon", 5), 90: ("square", 4), 120: ("triangle", 3)}


def seeds_svg(d):
    """The five seed chords: one side of each regular polygon inscribed in the circle."""
    def draw(t, standalone):
        out = []
        R, step = 66, 190
        for i, s in enumerate(d["seeds"]):
            cx, cy = 20 + R + 12 + i * step, 110
            name, n = POLY[s["arc"]]
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" style="fill:none;stroke:{t["ink2"]};stroke-width:1.2"/>')
            pts = [(cx + R * math.cos(math.radians(-90 + k * 360 / n)), cy + R * math.sin(math.radians(-90 + k * 360 / n))) for k in range(n + 1)]
            out.append(C.path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts), t["muted"], "none", 1))
            out.append(C.line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], t["red"], 3))
            out.append(C.text(cx, 30, f"{s['arc']}°", t["ink"], 15, "middle", 700))
            out.append(C.text(cx, 200, name, t["ink2"], 13, "middle"))
            out.append(C.text(cx, 220, s["value"], t["red"], 14, "middle", 700))
        out.append(C.text(20, 250, "Red: the chord of the arc, one side of the polygon. Values in base 60 on a circle of diameter 120, to the second.", t["muted"], 12.5))
        return C.svg_doc(960, 262, "".join(out), "The five seed chords, from inscribed regular polygons", t, standalone, 0.6, 960)
    return draw


def route(d):
    """Ptolemy's route from the seed to half a degree."""
    D = Diagram(1000, 430, "Ptolemy's route from the seed chords to the chord of half a degree")
    W, H = 150, 70
    for i, s in enumerate(d["seeds"]):
        D.node(f"s{s['arc']}", 20 + i * 196, 20, W, H, [(f"{s['arc']}°", "title"), (POLY[s["arc"]][0], "note")], color="ink")
    r = {x["arc"]: x for x in d["route"]}
    D.node("d12", 216, 150, W, H, [("12°", "title"), ("72° − 60°", "combo"), (r["12"]["table"], "note")], color="blue")
    D.edge("s72", "d12", ports=("bottom", "top:0.7"))
    D.edge("s60", "d12", ports=("bottom", "top:0.3"))
    xs = [412, 608, 804]
    for (key, arc), x in zip([("d6", "6"), ("d3", "3"), ("d1h", "1 1/2")], xs):
        D.node(key, x, 150, W, H, [(f"{arc.replace('1 1/2', '1½')}°", "title"), ("halve", "combo"), (r[arc]["table"], "note")], color="ink")
    D.edge("d12", "d6", ports=("right", "left"))
    D.edge("d6", "d3", ports=("right", "left"))
    D.edge("d3", "d1h", ports=("right", "left"))
    D.node("d3q", 804, 290, W, H, [("¾°", "title"), ("halve", "combo"), (r["3/4"]["table"], "note")], color="ink")
    D.edge("d1h", "d3q", ports=("bottom", "top"))
    sq = d["squeeze"]
    D.node("d1", 548, 290, 214, H, [("1°", "title"), ("squeezed by ¾° and 1½°", "combo"), (sq["value"], "note")], color="red")
    D.edge("d3q", "d1", ports=("left", "right"))
    D.edge("d1h", "d1", ports=("bottom:0.2", "top:0.8"))
    D.node("dh", 316, 290, 190, H, [("½°", "title"), ("halve 1°", "combo"), (d["half"]["value"], "note")], color="red")
    D.edge("d1", "dh", ports=("left", "right"))
    D.node("all", 20, 290, 240, H, [("Every ½° to 180°", "title"), ("add ½° with the sum rule", "combo"), ("360 entries", "note")], color="blue")
    D.edge("dh", "all", ports=("left", "right"))
    D.text(20, 405, "Blue: the sum and difference rules (Ptolemy's theorem). Red: where halving and differences cannot reach.", "caption")
    return D


def family():
    D = Diagram(1000, 640, "How Ptolemy's table combined older ideas, and where the sine came from")
    W, H = 210, 86
    nodes = {
        "bab": (20, 20, "Base 60 and tables", "", "Babylon, Era 1 topic 3", "ink"),
        "poly": (270, 20, "Inscribed polygons", "", "Euclid XIII; Archimedes, topics 7–8", "ink"),
        "hip": (520, 20, "Hipparchus's chords", "the first table, now lost", "c. 140 BCE", "ink"),
        "pt": (395, 160, "Ptolemy's table", "⊕ a seed, growth rules, interpolation", "Almagest, c. 150 CE", "red"),
        "jya": (145, 320, "Half-chords: jya", "⊕ use half the chord", "Aryabhata, c. 500", "ink"),
        "word": (145, 470, "jya → jiba → sinus", "the word travels", "Arabic, then Latin", "ink"),
        "reg": (520, 320, "Regiomontanus", "De triangulis omnimodis", "written c. 1464, printed 1533", "ink"),
        "lib": (770, 320, "The C library's sin(x)", "⊕ table + the sum rule", "glibc (IBM's library)", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("bab", "pt", ports=("bottom", "top:0.2"))
    D.edge("poly", "pt", ports=("bottom", "top:0.45"))
    D.edge("hip", "pt", ports=("bottom", "top:0.75"), dashed=True)
    D.edge("pt", "jya", ports=("bottom:0.2", "top"))
    D.edge("jya", "word", ports=("bottom", "top"))
    D.edge("pt", "reg", ports=("bottom:0.7", "top"))
    D.edge("pt", "lib", ports=("bottom:0.95", "top"))
    D.text(20, 610, "Dashed: Hipparchus's table is lost, so how much Ptolemy took from it is not known.", "caption")
    return D


def chain(d):
    ch, an = d["chain"], d["anchored"]
    it = d["interp"]
    lib = d["lib"]
    steps = [
        ("Astronomy needs the chord of every angle, and nobody can measure them all",
         "A seed of exact chords from regular polygons, and rules to grow more: halves, sums, differences", "Ptolemy, c. 150 CE"),
        ("Halving and differences from the seed reach 12°, 6°, 3°, 1½°, ¾°, but never 1°",
         f"Pin 1° between what ¾° and 1½° give: {d['squeeze']['value']}", "Ptolemy, Almagest I"),
        (f"Adding ½° 360 times lets rounding pile up: only {ch['exact']} of 360 entries right to the second",
         f"Restart the sums from every exact chord: {an['exact']} right, none worse than {an['worst']} seconds", "the program's experiment"),
        ("A table only has every half degree; the reader needs every minute",
         f"A column of increments for straight-line interpolation: at worst {it['err']} seconds off", "Ptolemy's third column"),
        ("A computer needs 16 digits, not 5",
         f"A table of sines and cosines plus the sum rule: {float(lib['ulp']):g} units in the last place here; glibc adds corrections", "GNU C library"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a seed of chords to the C library")
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


# ----------------------------------------------------------------------------------------------------------------------
PC_HTML = """
<div class="board pc-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="pc-arc">Arc <input id="pc-arc" type="range" min="0" max="10800" step="1" value="2000"></label>
      <span class="pc-arcval" id="pc-arcval"></span>
    </div>
    <div class="controls">
      <button id="pc-next" class="primary" type="button">Next step of Ptolemy's route</button>
      <button id="pc-reset" type="button">Start again</button>
    </div>
    <svg id="pc-svg" viewBox="0 0 360 330" role="img" aria-label="The chord of the chosen arc in a circle of diameter 120"></svg>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Reading the table</div>
    <p class="say" id="pc-say" aria-live="polite"></p>
    <table class="pc-read"><tbody id="pc-read"></tbody></table>
  </div>
</div>
"""

PC_CSS = """
.pc-board input[type=range]{width:min(320px,62vw)}
.pc-board .pc-arcval{font-family:var(--mono);font-size:14px;font-weight:600}
.pc-board .say{font-size:15px}
.pc-board svg{max-width:420px;margin:0 auto}
.pc-read{border-collapse:collapse;font-size:13.5px;width:100%;margin-top:6px}
.pc-read td{padding:5px 6px;border-bottom:1px solid var(--rule);vertical-align:top}
.pc-read td:first-child{color:var(--muted);width:46%}
.pc-read td:last-child{font-family:var(--mono)}
"""

PC_JS = r"""
(() => {
  const svg = document.getElementById("pc-svg");
  if (!svg) return;
  const ROUTE = __ROUTE__;
  const slider = document.getElementById("pc-arc");
  const crd = a => 120 * Math.sin(a * Math.PI / 360);
  const sec = v => Math.round(v * 3600) / 3600;
  function sexa(v, places) {
    let n = Math.round(Math.abs(v) * 60 ** places);
    const dg = [];
    for (let i = 0; i < places; i++) { dg.unshift(n % 60); n = Math.floor(n / 60); }
    return n + ";" + dg.join(",");
  }
  const arcText = m => `${Math.floor(m / 60)}° ${m % 60}′`;
  const POLY = { 36: 10, 60: 6, 72: 5, 90: 4, 120: 3 };
  let at = -1;
  function draw(arcDeg, poly) {
    svg.innerHTML = "";
    const cx = 180, cy = 165, R = 140;
    sv("circle", { cx, cy, r: R, fill: "none", stroke: "var(--ink-2)", "stroke-width": 1.5 }, svg);
    sv("line", { x1: cx - R, y1: cy, x2: cx + R, y2: cy, stroke: "var(--rule)", "stroke-width": 1 }, svg);
    if (poly) {
      const n = POLY[poly], pts = [];
      for (let k = 0; k <= n; k++) { const t = k * 2 * Math.PI / n; pts.push(`${cx + R * Math.cos(t)},${cy - R * Math.sin(t)}`); }
      sv("polyline", { points: pts.join(" "), fill: "none", stroke: "var(--muted)", "stroke-width": 1 }, svg);
    }
    const t = arcDeg * Math.PI / 180;
    const P = [cx + R, cy], Q = [cx + R * Math.cos(t), cy - R * Math.sin(t)];
    const M = [(P[0] + Q[0]) / 2, (P[1] + Q[1]) / 2];
    const large = arcDeg > 180 ? 1 : 0;
    sv("path", { d: `M ${P[0]} ${P[1]} A ${R} ${R} 0 ${large} 0 ${Q[0].toFixed(2)} ${Q[1].toFixed(2)}`, fill: "none", stroke: "var(--blue)", "stroke-width": 4 }, svg);
    sv("line", { x1: cx, y1: cy, x2: P[0], y2: P[1], stroke: "var(--ink-2)", "stroke-width": 1 }, svg);
    sv("line", { x1: cx, y1: cy, x2: Q[0], y2: Q[1], stroke: "var(--ink-2)", "stroke-width": 1 }, svg);
    sv("line", { x1: P[0], y1: P[1], x2: Q[0], y2: Q[1], stroke: "var(--red)", "stroke-width": 3 }, svg);
    // the half-chord: the line from the centre bisects the chord at a right angle (the sine)
    if (arcDeg > 2) {
      sv("line", { x1: cx, y1: cy, x2: M[0], y2: M[1], stroke: "var(--muted)", "stroke-width": 1, "stroke-dasharray": "3 3" }, svg);
      sv("line", { x1: M[0], y1: M[1], x2: Q[0], y2: Q[1], stroke: "var(--yellow)", "stroke-width": 5 }, svg);
    }
    sv("circle", { cx, cy, r: 3, fill: "var(--ink)" }, svg);
    if (arcDeg > 0 && arcDeg < 20) {                       // a magnified view of a small arc
      const len = Math.hypot(Q[0] - P[0], Q[1] - P[1]), k = 76 / len, bx = 238, by = 214, bw = 116, bh = 106;
      const id = "pc-clip";
      const defs = sv("defs", {}, svg), cp = sv("clipPath", { id }, defs);
      sv("rect", { x: bx, y: by, width: bw, height: bh }, cp);
      sv("rect", { x: bx, y: by, width: bw, height: bh, fill: "var(--surface)", stroke: "var(--axis)", "stroke-width": 1 }, svg);
      const g = sv("g", { "clip-path": `url(#${id})` }, svg);
      const ox = bx + bw / 2 + 10, oy = by + bh / 2 + 6;          // where the chord's midpoint sits in the inset
      const map = ([x, y]) => [ox + (x - M[0]) * k, oy + (y - M[1]) * k];
      const pts = [];
      for (let i = 0; i <= 40; i++) { const u = t * i / 40; pts.push(map([cx + R * Math.cos(u), cy - R * Math.sin(u)]).map(v => v.toFixed(1)).join(",")); }
      sv("polyline", { points: pts.join(" "), fill: "none", stroke: "var(--blue)", "stroke-width": 3 }, g);
      const [p1, q1, m1] = [map(P), map(Q), map(M)];
      sv("line", { x1: p1[0], y1: p1[1], x2: q1[0], y2: q1[1], stroke: "var(--red)", "stroke-width": 2 }, g);
      sv("line", { x1: m1[0], y1: m1[1], x2: q1[0], y2: q1[1], stroke: "var(--yellow)", "stroke-width": 4 }, g);
      sv("text", { x: bx + 4, y: by + 12, fill: "var(--muted)", "font-size": 9 }, svg, `magnified ${Math.round(k)}×`);
      sv("text", { x: bx + 4, y: by + bh - 6, fill: "var(--muted)", "font-size": 9 }, svg, "arc ≈ chord");
    }
    sv("text", { x: 8, y: 16, fill: "var(--muted)", "font-size": 10 }, svg, "diameter 120 · red: chord · yellow: half-chord · blue: arc");
  }
  function read(m) {
    const arcDeg = m / 60, k = Math.floor(arcDeg * 2), a0 = k / 2;
    const y0 = k === 0 ? 0 : sec(crd(a0)), y1 = sec(crd(Math.min(180, a0 + 0.5)));
    const inc = (y1 - y0) / 30, past = m - a0 * 60;
    const val = y0 + inc * past, truth = crd(arcDeg);
    const rows = [
      ["Table entry for " + (a0 % 1 ? Math.floor(a0) + "½" : a0) + "°", sexa(y0, 2)],
      ["Increment per minute of arc", sexa(inc, 3)],
      [`${past} minute${past === 1 ? "" : "s"} past the entry`, sexa(val, 2)],
      ["True chord", sexa(truth, 3)],
      ["Error", (Math.abs(val - truth) * 3600).toFixed(2) + " seconds"],
      ["Sine of half the arc", (truth / 120).toFixed(6)],
    ];
    const tb = document.getElementById("pc-read");
    tb.innerHTML = "";
    for (const [a, b] of rows) { const tr = el("tr", {}, tb); el("td", {}, tr, a); el("td", {}, tr, b); }
    document.getElementById("pc-arcval").textContent = arcText(m);
    return arcDeg;
  }
  function update(poly) { draw(read(+slider.value), poly); }
  slider.addEventListener("input", () => { at = -1; document.getElementById("pc-say").textContent = "Drag the arc. The table holds every half degree; between entries, add the increment once for each minute of arc."; update(); });
  document.getElementById("pc-next").addEventListener("click", () => {
    at = (at + 1) % ROUTE.length;
    const s = ROUTE[at];
    slider.value = Math.round(s.arc * 60);
    document.getElementById("pc-say").innerHTML = `<b>Step ${at + 1} of ${ROUTE.length}.</b> ${s.say}`;
    update(s.poly);
  });
  document.getElementById("pc-reset").addEventListener("click", () => { at = -1; slider.value = 2000; slider.dispatchEvent(new Event("input")); });
  slider.dispatchEvent(new Event("input"));
})();
"""


def route_steps(d):
    steps = []
    for s in d["seeds"]:
        name = POLY[s["arc"]][0]
        steps.append(dict(arc=s["arc"], poly=s["arc"], say=f"The seed: {s['arc']}° is one side of the inscribed {name}, known exactly. To the second it is {s['value']}."))
    for r in d["route"]:
        a = arc_value(r["arc"])
        how = "the difference rule: 72° − 60°, from Ptolemy's theorem" if r["arc"] == "12" else f"halving: {r['rule']}"
        steps.append(dict(arc=a, poly=None, say=f"{r['arc'].replace('1 1/2', '1½').replace('3/4', '¾')}° by {how}. Worked to thirds: {r['work']}; true {r['true']}."))
    sq = d["squeeze"]
    steps.append(dict(arc=1, poly=None, say=f"1° cannot be reached by halving or differences. A chord grows more slowly than its arc, so it lies between ⅔ of the chord of 1½° ({sq['lo']}) and 4/3 of the chord of ¾° ({sq['hi']}). Both give {sq['value']}."))
    steps.append(dict(arc=0.5, poly=None, say=f"½° by halving 1°: {d['half']['value']}, the first entry of the table. Every other entry follows by adding ½° with the sum rule."))
    return steps


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    ch, an, it, lib = d["chain"], d["anchored"], d["interp"], d["lib"]
    pi, r3, sq = d["pi"], d["root3"], d["squeeze"]
    js = PC_JS.replace("__ROUTE__", json.dumps(route_steps(d), ensure_ascii=False))
    pretty = lambda a: a.replace("1 1/2", "1½").replace("3/4", "¾").replace("1/2", "½").replace("179 ½", "179½")
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Ptolemy inherited base-60 fractions and the habit of tables from Babylon (Era 1, topic 3), and the sides of regular polygons from Greek geometry (topics 7 and 8). He added a way to grow a whole table from a handful of exact values. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Ptolemy's table. Blue: the same two moves, a table and the sum rule, inside a computer's sine function today."),
        ]),
        dict(id="table", eyebrow="Try it", title="Read the table, and walk Ptolemy's route", toc="Try it", blocks=[
            dict(type="p", text="Drag the arc to read its chord from a table with an entry every half degree, interpolating with the increment column. Then press **Next step** to walk Ptolemy's route from the five seed polygons down to half a degree. The yellow segment is half the chord: Indian astronomers later tabulated half-chords instead, and the half-chord became the sine."),
            dict(type="widget", html=PC_HTML, js=js, css=PC_CSS,
                 fallback=dict(type="svg", name="seeds", draw=seeds_svg(d), alt="The five seed chords from inscribed regular polygons", width=960),
                 note="In the interactive edition you can drag the arc, read the table with interpolation, and step through Ptolemy's route."),
            dict(type="p", text=f"On a circle of diameter 120, the chord of an arc *a* is 120 sin(*a*/2): a table of chords is a table of sines in disguise. The numbers are in base 60, with a semicolon after the whole parts: {d['seeds'][0]['value']} means 37 + 4/60 + 55/3600 parts."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="steps", eyebrow="How it works", title="From five polygons to half a degree", toc="How it works", blocks=[
            dict(type="p", text="Three rules do all the work. The **supplement**: the angle in a semicircle is a right angle, so the chord of 180° − *a* is √(120² − crd²*a*). **Halving**: crd²(*a*/2) = 60 × (120 − crd(180° − *a*)). **Sums and differences**: in a quadrilateral inside a circle, the two diagonals multiplied equal the two pairs of opposite sides multiplied and added (Ptolemy's theorem); with one side a diameter, that gives the chord of *a* − *b* or *a* + *b* from the chords of *a* and *b*."),
            dict(type="diagram", name="route", diagram=route(d)),
            dict(type="table", head=["Arc", "Rule", "Worked to thirds", "In the table", "True value"], num=[],
                 rows=[[f"{s['arc']}°", f"side of the {POLY[s['arc']][0]}", "", s["value"], s["true"]] for s in d["seeds"]] +
                      [[f"{pretty(r['arc'])}°", r["rule"].replace("1 1/2", "1½"), r["work"], r["table"], r["true"]] for r in d["route"]] +
                      [["1°", "squeeze between ¾° and 1½°", f"{sq['lo']} to {sq['hi']}", sq["value"], sq["true"]],
                       ["½°", "half of 1°", "", d["half"]["value"], d["half"]["true"]]]),
            dict(type="p", text=f"Why squeeze? Every arc that halving, sums and differences can reach from 36°, 60°, 72°, 90° and 120° is 3° times a fraction whose bottom is a power of 2, so 1° is out of reach (it would mean trisecting an angle). The program pins it down instead: a chord grows more slowly than its arc, so crd 1° lies between ⅔ × crd 1½° = {sq['lo']} and 4/3 × crd ¾° = {sq['hi']}. To the second both are **{sq['value']}**. Halving that gives **{d['half']['value']}** for half a degree, the value MacTutor reports from Ptolemy's table."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A table can be grown, not measured: a seed of exact values and a few rules that make new entries from old ones. The same pattern, a small table and an addition rule, is how a computer's sine function works today."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A table in Book I of the Almagest", toc="The evidence", blocks=[
            dict(type="p", text="Ptolemy observed at Alexandria between 127 and 141 CE (**documented**); the *Almagest* is usually placed about 150 CE. His life dates differ even within MacTutor, about 85–165 CE in one article and about 100–170 CE in another (**disputed**). The table runs from ½° to 180° in steps of ½°, with a third column of increments for interpolating. With its chords he obtained π ≈ 3 17/120 and √3 ≈ 1.73205 (**documented**, MacTutor)."),
            dict(type="p", text="Hipparchus made the first known chord table about 140 BCE; it is lost, and the claim that he wrote twelve books of chord tables cannot be checked (**conjecture** for its contents). Whether Hipparchus already used Ptolemy's theorem is **disputed**: Toomer doubts it. Whether Ptolemy computed his own table by the methods he describes is also **disputed**: course notes from Florida State University say there is good reason to think it was not computed that way, or by him."),
            dict(type="p", text="Indian astronomers tabulated half-chords instead. Aryabhata (about 500) called the function *jya*, and Brahmagupta reproduced the table in 628. In Arabic *jya* became *jiba*, then *jaib*, \"fold\", which Latin translators rendered *sinus*: the word **sine** (MacTutor)."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How good is a hand-built table?", toc="Measured", blocks=[
            dict(type="table", head=["How the 360 entries were made", "Right to the second", "Worst error"], num=[1, 2],
                 rows=[["Add ½° to the previous entry, 360 times", f"{ch['exact']} of 360", f"{ch['worst']} seconds (at {pretty(ch['at'])}°)"],
                       ["Restart the sums at every exact or derived chord", f"{an['exact']} of 360", f"{an['worst']} seconds"]]),
            dict(type="p", text=f"Each sum is rounded to the second, and a long chain of sums lets those roundings pile up: the plain chain gets only {ch['exact']} entries exactly right. Restarting from the chords known independently (the seeds, 12°, 1½°, 1° and ½°) keeps the worst error to {an['worst']} seconds. How Ptolemy's own table was actually computed is not recorded."),
            dict(type="table", head=["Arc", "Chord", "Increment per minute of arc"], num=[],
                 rows=[[f"{pretty(r['arc'])}°", r["chord"], r["inc"]] for r in d["rows"]]),
            dict(type="p", text=f"Between entries the reader adds the increment once for each minute of arc. The program tried every minute from 0° to 180°: the worst error is **{it['err']} seconds**, at {it['deg']}° {it['min']}′. The curve of the chord alone allows {it['bound']} seconds, and rounding the entries half a second more. A half-degree step makes interpolation about as accurate as the table itself."),
            dict(type="p", text=f"Two by-products. A polygon of 360 sides has perimeter 360 × crd 1°, so π ≈ 360 × {pi['c1']} / 120 = **{pi['sexa']}** = 377/120 = {pi['dec']} (true {pi['true']}). And the chord of 120° over the radius is √3: {r3['c120']} / 60 = {r3['sexa']} = {r3['dec']} (true {r3['true']})."),
            dict(type="p", text=f"The program also checked Ptolemy's theorem itself on {d['theorem']['n']:,} random quadrilaterals inside a circle: the largest relative gap between the two sides was {d['theorem']['gap']}, rounding error."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A table and the sum rule, inside your computer", toc="Full circle", blocks=[
            dict(type="p", text="The GNU C library computes sin(*x*) for most arguments the way Ptolemy filled his table: it looks up the sine and cosine of a nearby tabulated point, computes a short series for the small remainder, and combines them with the sum rule, sin(*x*₀ + *dx*) = sin *x*₀ cos *dx* + cos *x*₀ sin *dx*. The source comment in `s_sin.c` describes \"combining the sin and cos of X ... with the values looked up from the sin/cos table\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program built a table of {lib['size']} sines and cosines and used the sum rule on {lib['n']:,} random angles: the worst error was {float(lib['ulp']):g} units in the last place of a double. A half-degree table with Ptolemy's straight-line interpolation is off by up to {lib['lin']}, five correct decimals, about what his seconds gave. The library also looks up a small correction alongside each table value, and its source states a worst case of 0.518 units."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why did Ptolemy use a circle of diameter 120 rather than 1?",
             "Base 60: with a radius of 60, the chords come out as whole parts plus sixtieths, and the hexagon's side is exactly 60."),
            ("The chord of 60° is 60. What is the chord of 120°?",
             f"By the supplement rule, √(120² − 60²) = √10800 = 60√3 ≈ **{d['seeds'][4]['value']}**."),
            ("Why can't halving and differences reach 1°?",
             "Starting from 36°, 60°, 72°, 90° and 120°, they only make 3° times a fraction with a power of 2 below. 1° would need a third of 3°: trisecting an angle."),
            (f"The table gives {d['rows'][1]['chord']} for 1° and the increment {d['rows'][1]['inc']} per minute. What is the chord of 1° 20′?",
             f"{d['rows'][1]['chord']} plus 20 increments: {to_sexa(from_sexa(d['rows'][1]['chord']) + 20 * from_sexa(d['rows'][1]['inc']), 2)}. Set the widget's arc to 1° 20′ to compare it with the true value."),
            ("What is the chord of an arc in modern terms?",
             "On a circle of diameter 120, 120 sin(a/2). Half a chord, over the radius, is the sine of half the arc."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Almagest, Vat. gr. 1594", text="A Greek manuscript of Ptolemy's *Syntaxis mathematica* in the Vatican Library, dated about 900 in its record, digitized by the Library and shown by Source Library.",
                 draw=C.draw_manuscript, link="https://sourcelibrary.org/book/vat-gr-1594-ptolemy", link_text="Source Library page",
                 licence="Drawn placeholder. The English on that page is an AI translation; its licence fields conflict, so no image is copied here."),
            dict(title="The Almagest in Latin, Vat. lat. 2054", text="George of Trebizond's 15th-century Latin translation, a paper codex of 235 folios that he corrected himself: the table travelling into Latin.",
                 draw=C.draw_book, link="https://ptolemaeus.badw.de/ms/446", link_text="Ptolemaeus Arabus et Latinus record",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Euclid's Elements, Book XIII, Proposition 10", "David E. Joyce, Clark University", "https://mathcs.clarku.edu/~djoyce/elements/bookXIII/propXIII10.html", "The pentagon's side squared equals the hexagon's plus the decagon's, which gives the seed chord of 72°"),
            ("scholar", "s_sin.c (IBM Accurate Mathematical Library)", "GNU C library source, on codebrowser.dev", "https://codebrowser.dev/glibc/glibc/sysdeps/ieee754/dbl-64/s_sin.c.html", "do_sin: a sin/cos table plus the sum rule, with a stated worst case of 0.518 units in the last place"),
            ("scholar", "Vat. lat. 2054", "Ptolemaeus Arabus et Latinus, Bavarian Academy of Sciences", "https://ptolemaeus.badw.de/ms/446", "George of Trebizond's Latin Almagest, 15th century, with images"),
        ]),
        C.prove_it_section(ctx, "PtolemyChords", d["checks"],
                           "Ptolemy's theorem on 20,000 random quadrilaterals, the seed and derived chords against the true values, the squeeze for 1°, the half-degree value 0;31,25, π = 377/120, the interpolation bound, and the table-plus-sum-rule sine on a million angles.",
                           ["static double half(", "static double difference(", "static double sum("]),
    ]
    return dict(
        title="Ptolemy's Table of Chords", date="c. 150 CE",
        description="Era 2, topic 2 of The Algorithm Evolution Atlas: Ptolemy's table of chords, grown from five polygons by halving, sums and differences, with interpolation, and the same pattern inside today's sine function.",
        lede="Nobody can measure the chord of every angle. Ptolemy grew a table of 360 chords from five exact ones, with rules that make new entries from old, and a column for reading between the lines.",
        fieldnote="The sky-watchers of Alexandria met the same geometry problem a thousand times a night: given an angle, how long is the chord across it? Ptolemy did not measure. He started from five chords he knew exactly and grew the rest.",
        card=[("When", "*Almagest*, Book I, c. 150 CE; observations 127–141 CE (**documented**)"),
              ("Where", "Alexandria"),
              ("What hurt", "Astronomy needs the chord of every angle"),
              ("The fix", "A seed of exact chords, rules for halves, sums and differences, and linear interpolation"),
              ("Cost", f"360 entries; interpolation at worst {it['err']} seconds off")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `PtolemyChords.java`.",
    )
