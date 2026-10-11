"""Era 2, topic 11: al-Kashi's pi. Every number is parsed from AlKashiPi.java's output."""
import math
import re

import common as C
from diagrams import Diagram

SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci(s: str) -> str:
    """'2.3E-17' -> '2.3 × 10⁻¹⁷'."""
    m = re.match(r"(-?[\d.]+)E([-+]?\d+)$", s)
    if not m:
        return s
    return f"{m.group(1).lstrip('-')} × 10{str(int(m.group(2))).translate(SUP)}"


def parse(text: str) -> dict:
    d = {"chords": []}
    for ln in text.splitlines():
        if m := re.match(r"target: .*? inscribed alone (\d+), circumscribed alone (\d+), the average of the two (\d+) ; al-Kashi's 3 x 2\^28 = (\d+) sides is (\d+) doublings$", ln):
            d["need"] = dict(inn=int(m.group(1)), out=int(m.group(2)), avg=int(m.group(3)), sides=int(m.group(4)), his=int(m.group(5)))
        elif m := re.match(r"precision: .*?: (\d+ places.+)$", ln):
            d["prec"] = [tuple(int(v) for v in re.match(r"(\d+) places: (\d+) decimals", x.strip()).groups()) for x in m.group(1).split(";")]
        elif m := re.match(r"bounds: (.+)$", ln):
            d["bounds"] = [dict(n=int(a), lo=b, hi=c) for a, b, c in re.findall(r"(\d+) sides (\S+) < pi < (\S+)", m.group(1))]
        elif m := re.match(r"chord (.+?) degrees: (\S+)$", ln):
            d["chords"].append((m.group(1), m.group(2)))
        elif m := re.match(r"roots: (\d+) square roots in base 60, each carried to (\d+) sexagesimal places .* the polygon's side (\S+) parts$", ln):
            d["roots"] = dict(n=int(m.group(1)), places=int(m.group(2)), side=m.group(3))
        elif m := re.match(r"two pi: inscribed (\S+) \((\S+)\) ; circumscribed (\S+) \((\S+)\) ; true (\S+) \((\S+)\)$", ln):
            g = m.groups()
            d["two"] = dict(in_s=g[0], in_d=g[1], out_s=g[2], out_d=g[3], true_s=g[4], true_d=g[5])
        elif m := re.match(r"mean: .* is (\S+) ; 2 pi rounded the same way is (\S+)$", ln):
            d["mean"] = dict(his=m.group(1), true=m.group(2))
        elif m := re.match(r"places: inscribed correct to (\d+) decimals, circumscribed to (\d+), their average (\S+) to (\d+) ; .*\(error (\S+)\)$", ln):
            d["places"] = dict(inn=int(m.group(1)), out=int(m.group(2)), avg=m.group(3), avg_dec=int(m.group(4)), dsb_err=m.group(5))
        elif m := re.match(r"sin1: from sin 3 degrees = (\S+), iterating .* correct decimals after (.+) ; true sin 1 = (\S+)$", ln):
            d["sin"] = dict(sin3=m.group(1), true=m.group(3),
                            prog=[tuple(int(v) for v in x) for x in re.findall(r"(\d+): (\d+) decimals", m.group(2))])
        elif m := re.match(r"sin1 his: (\S+) \(radius 60\) ; true (\S+) ; first (\d+) places agree ; as a decimal (\S+), correct to (\d+) decimals \(error (\S+)\) ; the printed decimal (\S+) shares its first (\d+) digits with the true value but is correct to (\d+) \(error (\S+)\)", ln):
            g = m.groups()
            d["his"] = dict(sexa=g[0], true=g[1], agree=int(g[2]), dec=g[3], ok=int(g[4]), err=g[5], printed=g[6], share=int(g[7]), pok=int(g[8]), perr=g[9])
        elif m := re.match(r"double: 2 \* Math.PI prints (\S+) and is exactly (\S+) ; error (\S+) ; al-Kashi's error (\S+), (\d+) times smaller$", ln):
            d["dbl"] = dict(prints=m.group(1), exact=m.group(2), err=m.group(3), kerr=m.group(4), ratio=int(m.group(5)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def plan(d):
    """The computation as al-Kashi planned it: target first, then the size of the polygon, then the roots."""
    nd, ro, mn = d["need"], d["roots"], d["mean"]
    D = Diagram(1000, 230, "Al-Kashi's plan: the error he would accept, then the polygon that meets it, then the roots")
    W, H = 220, 116
    boxes = [("t", "1. The target", ["a horse's hair on a circle", "600,000 Earths wide:", "error in π ≤ 0.5 × 10⁻¹⁷"], "ink"),
             ("n", "2. The polygon", [f"3 × 2²⁸ = {nd['sides']:,} sides", f"{nd['his']} doublings", "from the hexagon"], "ink"),
             ("r", "3. The roots", [f"{ro['n']} square roots in base 60", "each checked by squaring", "and by casting out 59"], "ink"),
             ("m", "4. The answer", ["mean of the two perimeters:", f"2π = {mn['his']}", "= 6.2831853071795865"], "red")]
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title")] + [(s, "combo" if j == 2 else "note") for j, s in enumerate(sub)], color=col)
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "FIXED BEFORE THE FIRST ROOT WAS TAKEN: HOW GOOD THE ANSWER MUST BE, AND SO HOW FAR TO GO", "tag")
    D.text(20, 210, "Numbers from AlKashiPi.java, which repeats the computation; the target and the polygon are al-Kashi's (DSB).", "caption")
    return D


def polygons_svg(d):
    """Inscribed and circumscribed polygons for the first four sizes, with the bounds on π the program computed."""
    def draw(t, standalone):
        out, R, step = [], 70, 235
        for i, b in enumerate(d["bounds"]):
            cx, cy, n = 20 + R + 30 + i * step, 120, b["n"]
            ri = R / math.cos(math.pi / n)
            inner = [(cx + R * math.sin(2 * math.pi * k / n), cy - R * math.cos(2 * math.pi * k / n)) for k in range(n + 1)]
            outer = [(cx + ri * math.sin(2 * math.pi * k / n), cy - ri * math.cos(2 * math.pi * k / n)) for k in range(n + 1)]
            out.append(C.path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in outer), t["red"], "none", 1.6))
            out.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" style="fill:none;stroke:{t["ink2"]};stroke-width:1"/>')
            out.append(C.path("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in inner), t["blue"], "none", 1.6))
            out.append(C.text(cx, 22, f"{n} sides", t["ink"], 15, "middle", 700))
            out.append(C.text(cx, 222, f"{b['lo']} < π", t["blue"], 13, "middle", 700))
            out.append(C.text(cx, 240, f"π < {b['hi']}", t["red"], 13, "middle", 700))
        out.append(C.text(20, 272, "Blue: inscribed polygon (perimeter below the circle's). Red: circumscribed (above). Each doubling squeezes π about four times tighter.", t["muted"], 12.5))
        return C.svg_doc(960, 284, "".join(out), "Inscribed and circumscribed polygons with 6, 12, 24 and 48 sides, and the bounds they give for pi", t, standalone, 0.6, 960)
    return draw


# ----------------------------------------------------------------------------------------------------------------------
AK_HTML = """
<div class="board ak-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="ak-k">Doublings <input id="ak-k" type="range" min="0" max="27" value="0"></label>
      <span class="ak-kv" id="ak-kv"></span>
    </div>
    <svg id="ak-svg" viewBox="0 0 300 300" role="img" aria-label="A circle with its inscribed and circumscribed polygons"></svg>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Squeezing π</div>
    <div class="ak-rows" id="ak-rows"></div>
    <div class="ak-meter" aria-hidden="true"><div class="ak-track"><i id="ak-mark"></i><b id="ak-goal"></b></div>
      <div class="ak-scale"><span>error 1</span><span>10⁻¹⁰</span><span>10⁻²⁰</span></div></div>
    <p class="say" id="ak-say" aria-live="polite"></p>
  </div>
</div>
"""

AK_CSS = """
.ak-board input[type=range]{width:min(240px,50vw)}
.ak-kv{font-family:var(--mono);font-size:13px}
.ak-board svg{max-width:340px;margin:0 auto;display:block}
.ak-rows{display:grid;gap:6px;margin:6px 0 12px}
.ak-rows .r{display:grid;grid-template-columns:minmax(0,9.5em) minmax(0,1fr);gap:2px 10px;font-size:13px;align-items:baseline}
.ak-rows .r .lab{color:var(--ink-2)}
.ak-rows .r .val{font-family:var(--mono);font-size:13px;overflow-wrap:anywhere}
.ak-rows .r .val b{color:var(--red)}
.ak-rows .r .val .dc{display:block;color:var(--muted);font-size:12px;font-family:var(--body)}
.ak-meter{margin:4px 0 8px}
.ak-track{position:relative;height:12px;background:var(--wash)}
.ak-track i{position:absolute;top:0;bottom:0;left:0;background:var(--blue)}
.ak-track b{position:absolute;top:-4px;bottom:-4px;width:3px;background:var(--red)}
.ak-scale{display:flex;justify-content:space-between;font-size:11px;color:var(--muted);margin-top:3px}
.ak-board .say{font-size:14.5px}
@media (max-width:600px){.ak-rows .r{grid-template-columns:1fr}}
"""

AK_JS = r"""
(() => {
  const rows = document.getElementById("ak-rows");
  if (!rows) return;
  const S = 10n ** 40n;
  const PI = 31415926535897932384626433832795028841971n;          // pi x 10^40
  const HIS = "__HIS__".split(/[;,]/).map(Number);                 // al-Kashi's 2 pi, nine sexagesimal places
  const GOAL = 5n * 10n ** 22n;                                     // 0.5e-17 x 10^40
  const isqrt = n => {
    if (n < 2n) return n;
    let x = BigInt(Math.ceil(Math.sqrt(Number(n)) * (1 + 1e-12))) + 1n;
    for (;;) { const y = (x + n / x) >> 1n; if (y >= x) return x; x = y; }
  };
  // al-Kashi's recursion on a circle of radius 60: chord(180 - a/2)^2 = 60 (120 + chord(180 - a))
  const r = 60n * S, D = 2n * r, steps = [];
  let d = r;
  for (let k = 0; k < 28; k++) {
    d = isqrt(r * (2n * r + d));
    const side = isqrt((D - d) * (D + d)), n = 6n << BigInt(k);
    const lo = n * side / 120n, hi = n * side * S / d;
    steps.push({ n, lo, hi, mean: (lo + hi) / 2n });
  }
  const dec = v => { const s = v.toString().padStart(41, "0"); return s.slice(0, -40) + "." + s.slice(-40); };
  const correct = v => { const e = v > PI ? v - PI : PI - v; let c = 0; while (c < 38 && e * 2n * 10n ** BigInt(c + 1) < S) c++; return c; };
  const sexa9 = v => {                                              // 2 x v, rounded to nine places of base 60
    const u = (2n * v * 60n ** 9n + S / 2n) / S, out = [];
    let q = u; for (let i = 0; i < 9; i++) { out.unshift(Number(q % 60n)); q /= 60n; }
    return [Number(q), ...out];
  };
  const sup = t => t.replace(/[-0-9]/g, c => "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"["-0123456789".indexOf(c)]);
  const ex = x => { const [m, e] = x.toExponential(1).split("e"); return `${m} × 10${sup(String(+e))}`; };
  const svg = document.getElementById("ak-svg");
  function draw(n) {
    svg.innerHTML = "";
    const cx = 150, cy = 150, R = 118, m = Math.min(Number(n), 768);
    const poly = (rad, col) => {
      const pts = []; for (let i = 0; i <= m; i++) { const a = 2 * Math.PI * i / m; pts.push(`${(cx + rad * Math.sin(a)).toFixed(2)},${(cy - rad * Math.cos(a)).toFixed(2)}`); }
      sv("polyline", { points: pts.join(" "), fill: "none", stroke: col, "stroke-width": 1.6 }, svg);
    };
    poly(R / Math.cos(Math.PI / m), "var(--red)");
    sv("circle", { cx, cy, r: R, fill: "none", stroke: "var(--ink-2)", "stroke-width": 1 }, svg);
    poly(R, "var(--blue)");
    sv("text", { x: 8, y: 16, fill: "var(--muted)", "font-size": 10 }, svg, "blue: inscribed · red: circumscribed");
    if (n > 48n) sv("text", { x: 8, y: 292, fill: "var(--muted)", "font-size": 10 }, svg, "the polygons and the circle are now one line at this size");
  }
  function show() {
    const k = +document.getElementById("ak-k").value, s = steps[k];
    document.getElementById("ak-kv").textContent = `${k} → ${s.n.toLocaleString("en-US")} sides`;
    draw(s.n);
    rows.innerHTML = "";
    const add = (lab, html) => { const r = el("div", { class: "r" }, rows); el("span", { class: "lab" }, r, lab); el("span", { class: "val" }, r).innerHTML = html; };
    const bold = v => { const c = correct(v), t = dec(v).slice(0, 22); return `<b>${t.slice(0, 2 + c)}</b>${t.slice(2 + c)}<span class="dc">${c} correct decimal${c === 1 ? "" : "s"}</span>`; };
    add("Square roots so far", `${k + 2}`);
    add("π, inscribed", bold(s.lo));
    add("π, circumscribed", bold(s.hi));
    add("π, their mean", bold(s.mean));
    const sx = sexa9(s.mean);
    let same = 0; while (same < 10 && sx[same] === HIS[same]) same++;
    add("2π in base 60", sx.map((v, i) => (i < same ? `<b>${v}</b>` : `${v}`) + (i === 0 ? ";" : i < 9 ? "," : "")).join(""));
    const e = s.mean > PI ? s.mean - PI : PI - s.mean;
    const lg = e === 0n ? -40 : Math.log10(Number(e)) - 40;
    document.getElementById("ak-mark").style.width = `${Math.max(2, Math.min(100, -lg * 5))}%`;
    document.getElementById("ak-goal").style.left = `${17.3 * 5}%`;
    const ratio = Number(e * 1000n / GOAL) / 1000;
    const ok = e <= GOAL;
    const es = Number(e) / 1e40;
    document.getElementById("ak-say").innerHTML = ok
      ? `<b>Inside the target.</b> With ${s.n.toLocaleString("en-US")} sides the mean is off by ${ex(es)}, ${ratio.toFixed(2)} of al-Kashi's allowance of 0.5 × 10⁻¹⁷. All nine base-60 places agree with his 6;16,59,28,1,34,51,46,14,50.`
      : `The mean is off by ${ex(es)}, about ${ratio >= 1e6 ? ex(ratio) : Math.round(ratio).toLocaleString("en-US")} times the error al-Kashi would accept (red line). Each doubling divides it by about 4.`;
  }
  document.getElementById("ak-k").addEventListener("input", show);
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family(d):
    D = Diagram(1000, 640, "How al-Kashi's computation combined older ideas, and what came after it")
    W, H = 210, 86
    nodes = {
        "arc": (20, 20, "Polygons around a circle", "double the sides, trap π", "Archimedes, Era 1 topic 8", "ink"),
        "pto": (270, 20, "Chords by halving", "a chord from the one before", "Ptolemy, topic 2", "ink"),
        "bab": (520, 20, "Base 60 place value", "fractions in sixtieths", "Babylon, Era 1 topic 3", "ink"),
        "zer": (770, 20, "Decimal place value", "with a zero", "topic 4", "ink"),
        "kas": (395, 170, "al-Kashi's π", "⊕ the error fixed first; every root checked", "Samarkand, July 1424", "red"),
        "sam": (770, 170, "Samarkand astronomy", "tables that need precision", "Ulugh Beg's observatory", "ink"),
        "sin": (20, 330, "sin 1° by iteration", "a cubic solved place by place", "Treatise on the Chord and Sine", "ink"),
        "vc": (395, 330, "van Ceulen", "polygons to 20 decimals", "1596", "ink"),
        "dec": (770, 330, "π as a decimal fraction", "6.2831853071795865", "decimals for real numbers", "ink"),
        "dbl": (770, 480, "64-bit floating point", f"2π off by {sci(d['dbl']['err'])}", "the computer's default", "blue"),
        "ser": (395, 480, "Infinite series", "π without polygons", "Madhava, topic 10; Era 3", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("arc", "kas", ports=("bottom", "top:0.1"))
    D.edge("pto", "kas", ports=("bottom", "top:0.37"))
    D.edge("bab", "kas", ports=("bottom", "top:0.63"))
    D.edge("zer", "kas", ports=("bottom", "top:0.9"))
    D.edge("sam", "kas", ports=("left", "right"))
    D.edge("kas", "sin", ports=("bottom:0.1", "top:0.7"))
    D.edge("kas", "vc", ports=("bottom", "top"), label="record passed", at=0.5, dx=8, anchor="start")
    D.edge("kas", "dec", ports=("bottom:0.9", "top:0.3"))
    D.edge("dec", "dbl", ports=("bottom", "top"))
    D.edge("vc", "ser", ports=("bottom", "top"), dashed=True)
    D.text(20, 615, "Dashed: polygons gave way to series for computing π; van Ceulen himself still used polygons.", "caption")
    return D


def chain(d):
    nd, ro, pl = d["need"], d["roots"], d["places"]
    steps = [
        ("Earlier values of π were not good enough for the astronomers' tables",
         "Decide the accuracy first: a horse's hair on a circle 600,000 Earths wide", "al-Kashi, 1424"),
        ("How far must the polygons go to meet it?",
         f"Work it out in advance: 3 × 2²⁸ = {nd['sides']:,} sides, {nd['his']} doublings", "al-Kashi, as the DSB reports"),
        (f"{ro['n']} long square roots in base 60: one slip spoils everything after it",
         "Check every root twice: square it back, and cast out 59", "al-Kashi"),
        ("A base-60 answer is hard to compare with other values",
         f"Give it as a decimal fraction too: 2π = 6.2831853071795865, {pl['avg_dec']} decimals", "al-Kashi"),
        ("Each doubling divides the error by only 4; more digits mean ever larger polygons",
         "Series that converge faster", "Madhava (topic 10); Era 3"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a target to sixteen decimals")
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
def build(ctx):
    d = parse(ctx["out"])
    nd, pr, ch, ro, tw, mn, pl, sn, hs, db = (d["need"], d["prec"], d["chords"], d["roots"], d["two"], d["mean"], d["places"],
                                              d["sin"], d["his"], d["dbl"])
    enough = next(p for p, dd in pr if dd >= 16)
    js = AK_JS.replace("__HIS__", mn["his"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Al-Kashi's method was Archimedes' polygons (Era 1, topic 8), with chords found by halving as Ptolemy did (topic 2), all in Babylonian base 60 (Era 1, topic 3). What he added was accounting: how accurate the answer had to be, decided before he began, and a check on every step. He then wrote the answer in decimal fractions too. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(d),
                 caption="Red: al-Kashi's computation. Blue: where computing π went next, and where it sits today."),
        ]),
        dict(id="squeeze", eyebrow="Try it", title="Double the sides until the error is a horse's hair", toc="Try it", blocks=[
            dict(type="p", text="Move the slider to double the sides, starting from a hexagon. The page repeats al-Kashi's recursion exactly, in whole-number arithmetic: one square root per doubling, plus one for the side. Bold digits are correct. The bar shows the error of the mean on a scale from 1 down to 10⁻²⁰; the red line is al-Kashi's target."),
            dict(type="widget", html=AK_HTML, js=js, css=AK_CSS,
                 fallback=dict(type="diagram", name="plan", diagram=plan(d)),
                 note="In the interactive edition you can step from the hexagon to al-Kashi's 805,306,368 sides and watch the error fall below his target."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="method", eyebrow="How it works", title="A target, a polygon, and twenty-nine square roots", toc="How it works", blocks=[
            dict(type="p", text="**First the target.** Al-Kashi asked for the circumference of a circle 600,000 times as wide as the Earth, with an error no larger than the breadth of a horse's hair. The *Dictionary of Scientific Biography* (DSB) converts this into an error in π of at most 0.5 × 10⁻¹⁷."),
            dict(type="p", text="**Then the polygon.** A polygon inside the circle has a shorter perimeter than the circle, and one outside has a longer one. Doubling the sides squeezes π between them:"),
            dict(type="svg", name="polygons", draw=polygons_svg(d), alt="Inscribed and circumscribed polygons with 6, 12, 24 and 48 sides and the bounds they give for π", width=960),
            dict(type="p", text=f"Each doubling makes the gap about four times smaller. The program worked out how many doublings, starting from the hexagon, meet the target:"),
            dict(type="table", head=["Using", "Doublings needed"], num=[1],
                 rows=[["The inscribed polygon alone", str(nd["inn"])], ["The circumscribed polygon alone", str(nd["out"])],
                       ["The mean of the two", str(nd["avg"])]]),
            dict(type="p", text=f"Al-Kashi's polygon has 3 × 2²⁸ = {nd['sides']:,} sides: {nd['his']} doublings. The DSB says he took the arithmetic mean of the two perimeters as his answer, exactly what the table shows the target needs."),
            dict(type="p", text="**Then the roots.** On a circle of radius 60, the chord of 180° minus half an arc follows from the chord of 180° minus the whole arc: square it, and you get 60 × (120 + the old chord). So each doubling is one square root. Starting from the chord of 60°, which is the radius, the program's chords (base 60, to four places) are:"),
            dict(type="table", head=["Chord of", "Length (radius 60)"], num=[],
                 rows=[[a.replace("180 - 60/2^27", "180° − 60°/2²⁷").replace(" degrees", "") + ("" if "2^" in a else "°"), v] for a, v in ch]),
            dict(type="p", text=f"Twenty-eight chords, then one more root for the side by Pythagoras: {ro['n']} square roots in all. Al-Kashi set out his chords in 28 tables, and checked each root by squaring it and by \"casting out 59\", the base-60 cousin of casting out nines: a number and the sum of its base-60 digits leave the same remainder when divided by 59, so root × root + remainder must match the number under the root modulo 59. The program does both checks on every root. The side of the final polygon is {ro['side']} parts."),
            dict(type="table", head=["2π from", "Base 60", "Decimal"], num=[],
                 rows=[["Inscribed polygon", tw["in_s"], tw["in_d"]], ["Circumscribed polygon", tw["out_s"], tw["out_d"]],
                       ["Their mean", f"{mn['his']} (rounded)", pl["avg"]], ["True value", tw["true_s"], tw["true_d"]]]),
            dict(type="p", text=f"The mean, rounded to nine base-60 places, is **{mn['his']}**, the true value rounded the same way. Al-Kashi converted his result into the decimal fraction **6.2831853071795865**, which is 2π rounded to sixteen decimals (error {sci(pl['dsb_err'])})."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Decide how good the answer must be, then work out how much computation that takes, then check every step. Archimedes' method was 1,700 years old; the new thing was an error budget, set before the first root was taken."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How many places to carry, and sin 1°", toc="Measured", blocks=[
            dict(type="p", text="Al-Kashi also had to decide how many base-60 places to carry in every chord: too few and rounding errors pile up over 29 roots. The DSB says he worked this out too, without saying how many places he used. The program ran the whole computation at different precisions:"),
            dict(type="table", head=["Base-60 places carried", "Correct decimals of 2π (mean)"], num=[0, 1], rows=[[str(p), str(dd)] for p, dd in pr]),
            dict(type="p", text=f"From {enough} places on, the answer is good to sixteen decimals; the page uses {ro['places']}."),
            dict(type="p", text=f"In his last work, the *Treatise on the Chord and Sine*, al-Kashi computed sin 1° \"to the same accuracy as he had computed π\" (MacTutor). Sin 3° follows from Ptolemy's chords; sin 1° is then the root of a cubic, from sin 3t = 3 sin t − 4 sin³ t. His iteration x = (sin 3° + 4x³)/3, started from sin 3°/3, gains about three decimals a round:"),
            dict(type="table", head=["Round", "Correct decimals of sin 1°"], num=[0, 1], rows=[[str(a), str(b)] for a, b in sn["prog"]]),
            dict(type="p", text=f"The DSB gives his value for radius 60 as {hs['sexa']}. The program's true value is {hs['true']} (truncated), so the first {hs['agree']} places agree and the ninth is one unit low. Converted, his value is {hs['dec']}: correct to **{hs['ok']} decimals**. The decimal the DSB prints beside it, {hs['printed']}, shares the first {hs['share']} digits with the true value but is {sci(hs['perr'])} off, so it is not an exact conversion of his base-60 digits."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="One treatise, dated to the month", toc="The evidence", blocks=[
            dict(type="p", text="Al-Kashi finished *al-Risala al-muhitiyya*, the *Treatise on the Circumference*, in July 1424 (Sha'ban 827 AH) in Samarkand, where he worked for Ulugh Beg; at least eight manuscripts survive (ISMI lists 9 witnesses). Whether one of them is in his own hand is **disputed**. He died in 1429 according to MacTutor (Muslim Heritage: c. 1436, **disputed**)."),
            dict(type="p", text="How many decimals are correct? Sixteen, say MacTutor, the DSB and Strick; Gourdon and Sebah write \"about 14 correct decimals\" (**disputed**; the program finds sixteen for the decimal fraction the DSB prints). MacTutor: \"It would be almost 200 years before van Ceulen surpassed Al-Kashi's accuracy with 20 decimal places\"; van Ceulen's book with 20 decimals is from 1596. Al-Kashi did not invent decimal fractions: \"the idea had been present in the work of several mathematicians\" (MacTutor), but he used them methodically (DSB) and for a number like π (Rashed, as quoted by MacTutor)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Your computer's 2π is less accurate", toc="Full circle", blocks=[
            dict(type="p", text="A computer's default number, the 64-bit double, carries about 16 significant digits. Java's `2 * Math.PI` prints as 6.283185307179586."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The double nearest 2π is exactly {db['exact']}…, off by {sci(db['err'])}. Al-Kashi's 6.2831853071795865 is off by {sci(db['kerr'])}: about **{db['ratio']} times** closer. A value computed by hand in Samarkand in 1424 beats the 2π built into every laptop. His habit of fixing the error first and then planning the computation to meet it is the same question a programmer asks when choosing between float and double."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does doubling the sides make the error about four times smaller, not two?", "The gap between polygon and circle grows like the square of the angle each side cuts off; halving the angle quarters the gap."),
            (f"Why did al-Kashi's polygon need only {nd['avg']} doublings, when either polygon alone needs {nd['inn']}?", "The inscribed perimeter is too small by some amount e, and the circumscribed one too big by about 2e. Their mean is off by only about e/2, half the inscribed error: just enough, at this target, to save one doubling."),
            ("What does casting out 59 check?", "In base 60, a number and the sum of its digits leave the same remainder on division by 59, as a number and its digit sum do for 9 in base 10. If a² + remainder doesn't match the radicand modulo 59, the root is wrong."),
            ("Why give the answer as a decimal fraction as well?", "To compare it with values written in other notations, and because decimals were familiar to readers who did not use base 60."),
            ("Is 6.2831853071795865 correct to 16 decimals or 15?", "Sixteen by rounding: the true value is 6.28318530717958647…, which rounds to …865. The 16th digit differs if you only truncate."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="al-Risala al-muhitiyya, Istanbul and Mashhad manuscripts", text="Jan Hogendijk's Samarkand page gives facsimiles of two manuscripts of the treatise, with a bibliography; ISMI catalogues nine witnesses.",
                 draw=lambda t, s=False: C.draw_manuscript(t, s, note="827"), link="https://www.jphogendijk.nl/samarkand.html", link_text="Hogendijk, Utrecht",
                 licence="Drawn placeholder (827 AH = 1424 CE)."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "AlKashiPi", d["checks"],
                           "every one of the 29 square roots by squaring and by casting out 59 (at nine precisions), the two polygons trapping π, the mean rounded to nine base-60 places, the DSB's decimal against 2π, sin 1° by al-Kashi's iteration and his base-60 value, and his 2π against a 64-bit double.",
                           ["static BigInteger root(", "static BigDecimal[] polygons("]),
    ]
    return dict(
        title="Al-Kashi's Pi", date="1424 CE",
        description="Era 2, topic 11 of The Algorithm Evolution Atlas: al-Kashi's computation of 2π to sixteen decimals, with the error fixed in advance and every square root checked.",
        lede="A circle 600,000 times as wide as the Earth, measured to the breadth of a horse's hair. Al-Kashi decided how accurate π had to be before he began, worked out that a polygon of 805,306,368 sides would do it, and took twenty-nine square roots in base 60 to get there.",
        fieldnote="Archimedes' method was already seventeen centuries old. What was new in Samarkand was the accounting: a precision fixed before the work began, a computation planned to meet it, and every root checked twice. His sixteen decimals stood for almost two hundred years.",
        card=[("When", "July 1424 (Sha'ban 827 AH)"),
              ("Where", "Samarkand, at Ulugh Beg's court"),
              ("What hurt", "Values of π not accurate enough for astronomical tables"),
              ("The fix", "Fix the error first; double the polygon to 3 × 2²⁸ sides; check every root"),
              ("Cost", f"{ro['n']} square roots in base 60 for 16 decimals")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AlKashiPi.java`.",
    )
