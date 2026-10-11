"""Era 4, topic 2: Runge–Kutta methods. Every number is parsed from RungeKutta.java's output."""
import math
import re

import common as C
from diagrams import Diagram

NAMES = {"Euler": "Euler", "Midpoint": "Runge's midpoint", "Heun3": "Heun-type third order",
         "Classical": "Kutta's classical", "ThreeEighths": "Kutta's 3/8 rule"}


def parse(text: str) -> dict:
    d = {"tab": [], "order": [], "cost": []}
    for ln in text.splitlines():
        if m := re.match(r"tableau: (\w+) \((.+?)\) ; (\d) slopes? ; weights (.+?) ; order conditions met (\d) of 8 ; order (\d)(?: ; first failure (.+))?$", ln):
            d["tab"].append(dict(name=m.group(1), who=m.group(2), s=m.group(3), w=m.group(4), met=m.group(5), order=m.group(6), fail=m.group(7)))
        elif m := re.match(r"order: (\w+) ; .*? ; errors (.+?) ; ratios (.+?) ; measured order ([\d.]+)$", ln):
            d["order"].append(dict(name=m.group(1), errs=m.group(2).split(", "), ratios=m.group(3).split(", "), p=m.group(4)))
        elif m := re.match(r"oscillator: x'' = -x, start \(1, 0\), (\d+) steps per period, (\d+) periods ; .*? ; Euler x\^2 \+ v\^2 = ([\d.]+), predicted \(1 \+ h\^2\)\^(\d+) = ([\d.]+) ; Midpoint ([\d.]+) ; Heun3 ([\d.]+) ; Classical ([\d.]+) ; ThreeEighths ([\d.]+)$", ln):
            g = m.groups()
            d["osc"] = dict(per=g[0], periods=g[1], euler=g[2], n=g[3], pred=g[4], mid=g[5], heun=g[6], rk4=g[7], te=g[8])
        elif ln.startswith("cost: "):
            d["cost"] = [dict(name=a, steps=int(b), evals=int(c)) for a, b, c in re.findall(r"(\w+) (\d+) steps, (\d+) slope evaluations", ln)]
        elif m := re.match(r"pendulum: .*? h = 1/1024, (\d+) slope evaluations: period ([\d.]+) ; .*? = ([\d.]+) ; difference (\S+) ; small-swing value 2 pi = ([\d.]+)$", ln):
            d["pend"] = dict(evals=int(m.group(1)), period=m.group(2), agm=m.group(3), diff=m.group(4), small=m.group(5))
    d["checks"] = C.checks(text)
    return d


# the tables of weights, for the drawings and the widget (the program checks the same tables)
TABLES = {
    "Euler": dict(c=[0], a=[[]], b=[1]),
    "Midpoint": dict(c=[0, 0.5], a=[[], [0.5]], b=[0, 1]),
    "Heun3": dict(c=[0, 1 / 3, 2 / 3], a=[[], [1 / 3], [0, 2 / 3]], b=[0.25, 0, 0.75]),
    "Classical": dict(c=[0, 0.5, 0.5, 1], a=[[], [0.5], [0, 0.5], [0, 0, 1]], b=[1 / 6, 1 / 3, 1 / 3, 1 / 6]),
}


def _run(name, steps_per_period, periods):
    T = TABLES[name]
    h = 2 * math.pi / steps_per_period
    y = [1.0, 0.0]
    pts = [tuple(y)]
    for _ in range(steps_per_period * periods):
        ks = []
        for i in range(len(T["b"])):
            yi = list(y)
            for j, aij in enumerate(T["a"][i]):
                for q in range(2):
                    yi[q] += h * aij * ks[j][q]
            ks.append([yi[1], -yi[0]])
        for i, bi in enumerate(T["b"]):
            for q in range(2):
                y[q] += h * bi * ks[i][q]
        pts.append(tuple(y))
    return pts


def orbit_svg(d):
    """The oscillator x'' = -x in the (position, velocity) plane: the true circle, Euler and the classical method."""
    def draw(t, standalone):
        out, cx, cy, s = [], 200, 200, 90
        out.append(C.circle(cx, cy, s, "none", t["axis"], 2))
        for name, col, lab in [("Euler", t["red"], "Euler, 16 steps a turn"), ("Classical", t["blue"], "Kutta's classical, 16 steps a turn")]:
            pts = _run(name, 16, 3)
            dd = "M" + " L".join(f"{cx + s * x:.1f},{cy - s * v:.1f}" for x, v in pts if abs(x) < 2.1 and abs(v) < 2.1)
            out.append(C.path(dd, col, "none", 2.2))
        out.append(C.line(cx - 190, cy, cx + 190, cy, t["axis"], 1))
        out.append(C.line(cx, cy - 190, cx, cy + 190, t["axis"], 1))
        out.append(C.text(cx + 186, cy - 6, "position", t["muted"], 12, "end"))
        out.append(C.text(cx + 6, cy - 178, "velocity", t["muted"], 12))
        X = 420
        out += [C.text(X, 80, "Three turns of a spring, x'' = −x, 16 steps a turn", t["ink"], 15, "start", 700),
                C.text(X, 112, "Grey: the true path, a circle.", t["muted"], 13),
                C.text(X, 136, "Red: Euler's method spirals outward;", t["red"], 13, "start", 700),
                C.text(X, 156, "each step multiplies x² + v² by 1 + h².", t["red"], 13),
                C.text(X, 186, "Blue: Kutta's four-slope method", t["blue"], 13, "start", 700),
                C.text(X, 206, "stays on the circle at this scale.", t["blue"], 13),
                C.text(X, 250, f"With {d['osc']['per']} steps a turn for {d['osc']['periods']} turns, the program finds", t["muted"], 12.5),
                C.text(X, 270, f"x² + v² = {float(d['osc']['euler']):,.0f} for Euler, {d['osc']['rk4']} for Kutta's.", t["muted"], 12.5)]
        return C.svg_doc(800, 400, "".join(out), "Euler's method and the classical Runge–Kutta method on an oscillator", t, standalone, 0.55, 800)
    return draw


RK_HTML = """
<div class="board rk-board">
  <div style="min-width:0">
    <svg id="rk-svg" viewBox="0 0 400 400" role="img" aria-label="The path of an oscillator computed step by step, against the true circle"></svg>
  </div>
  <div style="min-width:0">
    <div class="controls">
      <label for="rk-m">Method <select id="rk-m">
        <option value="Euler">Euler (1 slope)</option><option value="Midpoint">Runge's midpoint (2)</option>
        <option value="Heun3">Heun-type third order (3)</option><option value="Classical" selected>Kutta's classical (4)</option></select></label>
    </div>
    <div class="controls">
      <label for="rk-s">Steps per turn <input id="rk-s" type="range" min="4" max="64" value="16"></label><span class="rk-v" id="rk-sv"></span>
    </div>
    <div class="controls">
      <label for="rk-p">Turns <input id="rk-p" type="range" min="1" max="20" value="3"></label><span class="rk-v" id="rk-pv"></span>
    </div>
    <ol class="rk-steps" id="rk-steps"></ol>
    <p class="say" id="rk-say" aria-live="polite"></p>
  </div>
</div>
"""

RK_CSS = """
.rk-board select{font:inherit;font-size:14px;padding:3px 6px}
.rk-board input[type=range]{width:min(170px,42vw)}
.rk-v{font-family:var(--mono);font-size:13px}
.rk-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.rk-steps .m{font-family:var(--mono);font-size:12.5px}
#rk-svg{width:100%;max-width:400px;height:auto}
"""

RK_JS = r"""
(() => {
  const svg = document.getElementById("rk-svg");
  if (!svg) return;
  const T = {
    Euler: {c: [0], a: [[]], b: [1]},
    Midpoint: {c: [0, 1 / 2], a: [[], [1 / 2]], b: [0, 1]},
    Heun3: {c: [0, 1 / 3, 2 / 3], a: [[], [1 / 3], [0, 2 / 3]], b: [1 / 4, 0, 3 / 4]},
    Classical: {c: [0, 1 / 2, 1 / 2, 1], a: [[], [1 / 2], [0, 1 / 2], [0, 0, 1]], b: [1 / 6, 1 / 3, 1 / 3, 1 / 6]},
  };
  function show() {
    const name = document.getElementById("rk-m").value, S = +document.getElementById("rk-s").value, P = +document.getElementById("rk-p").value;
    document.getElementById("rk-sv").textContent = S; document.getElementById("rk-pv").textContent = P;
    const M = T[name], h = 2 * Math.PI / S;
    let y = [1, 0];
    const pts = [y.slice()];
    for (let n = 0; n < S * P; n++) {
      const k = [];
      for (let i = 0; i < M.b.length; i++) {
        const yi = y.slice();
        for (let j = 0; j < M.a[i].length; j++) for (let q = 0; q < 2; q++) yi[q] += h * M.a[i][j] * k[j][q];
        k.push([yi[1], -yi[0]]);
      }
      const out = y.slice();
      for (let i = 0; i < M.b.length; i++) for (let q = 0; q < 2; q++) out[q] += h * M.b[i] * k[i][q];
      y = out; pts.push(y.slice());
    }
    svg.innerHTML = "";
    const cx = 200, cy = 200, s = 80;
    sv("line", {x1: 10, y1: cy, x2: 390, y2: cy, stroke: "var(--axis)"}, svg);
    sv("line", {x1: cx, y1: 10, x2: cx, y2: 390, stroke: "var(--axis)"}, svg);
    sv("circle", {cx, cy, r: s, fill: "none", stroke: "var(--muted)", "stroke-width": 2, "stroke-dasharray": "4 4"}, svg);
    let d = "", clipped = false;
    for (const [x, v] of pts) {
      if (Math.abs(x) > 2.4 || Math.abs(v) > 2.4) { clipped = true; break; }
      d += (d ? " L" : "M") + (cx + s * x).toFixed(1) + "," + (cy - s * v).toFixed(1);
    }
    sv("path", {d, fill: "none", stroke: name === "Euler" ? "var(--red)" : "var(--blue)", "stroke-width": 2.2}, svg);
    for (const [x, v] of pts.slice(0, S + 1)) if (Math.abs(x) <= 2.4 && Math.abs(v) <= 2.4) sv("circle", {cx: cx + s * x, cy: cy - s * v, r: 2.6, fill: "var(--ink)"}, svg);
    sv("text", {x: 386, y: cy - 6, fill: "var(--muted)", "font-size": 12, "text-anchor": "end"}, svg, "position");
    sv("text", {x: cx + 6, y: 22, fill: "var(--muted)", "font-size": 12}, svg, "velocity");
    const r2 = y[0] * y[0] + y[1] * y[1];
    const ol = document.getElementById("rk-steps"); ol.innerHTML = "";
    const li = t => { el("li", {}, ol).innerHTML = t; };
    li(`${M.b.length} slope${M.b.length > 1 ? "s" : ""} per step, ${fmt(S * P)} steps: <span class="m">${fmt(M.b.length * S * P)}</span> slope evaluations`);
    li(`after ${P} turn${P > 1 ? "s" : ""}: x² + v² = <span class="m">${r2 < 1e6 ? r2.toFixed(8) : r2.toExponential(4)}</span> (true value 1)`);
    li(`position <span class="m">${y[0].toFixed(6)}</span>, true value 1`);
    document.getElementById("rk-say").textContent = clipped ? "The path left the picture: the method's errors grow faster than the motion." :
      Math.abs(r2 - 1) < 1e-3 ? "The computed path stays on the circle to within a thousandth." : "The path drifts away from the circle; try more steps, or more slopes per step.";
  }
  ["rk-m", "rk-s", "rk-p"].forEach(id => document.getElementById(id).addEventListener("input", show));
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the Runge–Kutta methods combined older ideas, and where they led")
    W = 210
    nodes = {
        "eu": (20, 20, "Euler's method", "follow the slope at the start of each step", "1768", "ink"),
        "quad": (395, 20, "Midpoint and trapezoid rules", "better areas from a few samples", "quadrature", "ink"),
        "tay": (770, 20, "Taylor series", "how a solution changes, term by term", "Newton, Taylor", "ink"),
        "rk": (395, 170, "Runge, Heun, Kutta", "⊕ several slopes per step, weighted to cancel error", "1895–1901", "red"),
        "nys": (20, 330, "Nyström", "order 5 completed", "1925", "ink"),
        "but": (395, 330, "Order conditions as trees", "a theory for every order", "Butcher", "ink"),
        "ad": (770, 330, "Adaptive steps", "two estimates per step; the step size follows the error", "later", "blue"),
        "today": (395, 480, "Simulation today", "orbits, circuits, chemistry, weather", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("eu", "rk", ports=("bottom", "top:0.15"))
    D.edge("quad", "rk", ports=("bottom", "top"))
    D.edge("tay", "rk", ports=("bottom", "top:0.85"))
    D.edge("rk", "nys", ports=("bottom:0.1", "top:0.7"))
    D.edge("rk", "but", ports=("bottom", "top"))
    D.edge("rk", "ad", ports=("bottom:0.9", "top:0.3"))
    D.edge("but", "today", ports=("bottom", "top"))
    D.edge("ad", "today", ports=("bottom:0.3", "right:0.5"), dashed=True)
    D.text(20, 615, "Euler's method is from Euler's Institutiones calculi integralis (1768–1770); Butcher's theory and adaptive methods are later than this era.", "caption")
    return D


def chain(d):
    cost = {c["name"]: c for c in d["cost"]}
    steps = [
        ("Most differential equations have no formula for their solution",
         "Walk forward along the slope (Euler)", "1768"),
        (f"The error is proportional to the step: {cost['Euler']['steps']:,} steps for an error below 10⁻⁶ on y' = y",
         f"Sample the slope at the middle of the step: {cost['Midpoint']['steps']:,} steps", "Runge, 1895"),
        (f"Still {cost['Midpoint']['evals']:,} slope evaluations; halving the step only quarters the error",
         f"Four slopes weighted 1/6, 1/3, 1/3, 1/6: {cost['Classical']['steps']} steps, {cost['Classical']['evals']} evaluations", "Kutta, 1901"),
        ("One step size for the whole journey wastes work where the solution is smooth",
         "Estimate each step's error and adjust the step", "adaptive methods, later"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from Euler's steps to Kutta's four slopes")
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
    tab, order, osc, cost, pend = d["tab"], d["order"], d["osc"], d["cost"], d["pend"]
    cl = next(o for o in order if o["name"] == "Classical")
    eu = next(o for o in order if o["name"] == "Euler")
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Euler had shown how to follow a differential equation forward in small steps; the midpoint and trapezoid rules had shown that a few well-placed samples estimate an area far better than one. Runge combined the two in 1895: sample the slope more than once inside each step. Heun and Kutta then chose the samples and weights so that the step agrees with the true solution's Taylor series to higher and higher powers of the step. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the Runge–Kutta methods of 1895–1901. Blue: where the idea went."),
        ]),
        dict(id="orbit", eyebrow="Try it", title="Keep a spring on its circle", toc="Try it", blocks=[
            dict(type="p", text="A weight on a spring, x'' = −x, moves so that position and velocity trace a circle. Pick a method and a number of steps per turn, and watch the computed path against the true circle (dashed). The dots mark the first turn's steps. Euler's method spirals out whatever you do; Kutta's four slopes, with 32 steps a turn, stay within a thousandth of the circle for 20 turns."),
            dict(type="widget", html=RK_HTML, js=RK_JS, css=RK_CSS,
                 fallback=dict(type="svg", name="orbit", draw=orbit_svg(d), alt="Euler's method and the classical Runge–Kutta method on an oscillator", width=800),
                 note="In the interactive edition you can choose the method, the steps per turn and the number of turns."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Several slopes, weighted to cancel the error", toc="How it works", blocks=[
            dict(type="p", text="A differential equation y' = f(t, y) gives the slope of the solution at every point. **Euler's step** follows the slope at the start: y(t + h) ≈ y + h·f(t, y). The true solution curves away during the step, and the error of a whole journey is proportional to h."),
            dict(type="p", text="**Kutta's classical step** samples four slopes: k₁ at the start; k₂ at the middle, reached with k₁; k₃ at the middle again, reached with k₂; k₄ at the end, reached with k₃. Then y(t + h) ≈ y + h·(k₁ + 2k₂ + 2k₃ + k₄)/6. The weights are not guesses: they make the step agree with the Taylor series of the true solution through the h⁴ term, which comes to eight equations (the order conditions). The program writes each method as a table of weights and tests the eight equations in exact fractions:"),
            dict(type="table", head=["Method", "Slopes per step", "Weights", "Conditions met", "Order", "First failure"], num=[1, 3, 4],
                 rows=[[NAMES[r["name"]] + f" ({r['who']})", r["s"], r["w"], f"{r['met']} of 8", r["order"], r["fail"] or "—"] for r in tab], hl=3),
            dict(type="p", text="\"First failure\" is the first condition a method misses: the sum it gives against the value the Taylor series needs. Order p means the error of a journey shrinks like hᵖ: halve the step and the error falls by 2ᵖ."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do a little more work inside each step, arranged so that the errors of the samples cancel. Four slope evaluations per step buy an error proportional to h⁴ instead of h, and that is far cheaper than taking smaller steps."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Halve the step, divide the error", toc="Measured", blocks=[
            dict(type="p", text="On y' = y from y(0) = 1, the answer at t = 1 is e. The program's errors with 10, 20, 40, 80 and 160 steps, and the ratio each time the step is halved:"),
            dict(type="table", head=["Method", "10 steps", "20", "40", "80", "160", "Ratio when halved", "Measured order"], num=[1, 2, 3, 4, 5, 6, 7],
                 rows=[[NAMES[o["name"]]] + [C.sci(e) for e in o["errs"]] + [o["ratios"][-1], o["p"]] for o in order]),
            dict(type="p", text="The two four-slope methods give identical numbers here: on an equation as simple as y' = y, any four-slope method of order 4 reproduces the first five terms of the exponential series exactly. They differ on harder equations."),
            dict(type="table", head=["Method", "Steps for an error below 10⁻⁶", "Slope evaluations"], num=[1, 2],
                 rows=[[NAMES[c["name"]], f"{c['steps']:,}", f"{c['evals']:,}"] for c in cost]),
            dict(type="p", text=f"**The spring.** With {osc['per']} steps per turn for {osc['periods']} turns, x² + v² should stay 1. Euler's method multiplies it by exactly 1 + h² every step, and the program confirms the prediction: {float(osc['euler']):,.1f} against (1 + h²)^{osc['n']} = {float(osc['pred']):,.1f}. Runge's midpoint gives {osc['mid']}, the third-order method {osc['heun']}, and Kutta's two methods {osc['rk4']} and {osc['te']}."),
            dict(type="p", text=f"**A pendulum** swinging through 90 degrees obeys θ'' = −sin θ, and its period has no elementary formula. Kutta's classical method with h = 1/1024 ({pend['evals']:,} slope evaluations, including the search for the turning point) gives a period of {pend['period']}; Gauss's arithmetic–geometric mean gives {pend['agm']}, a difference of {C.sci(pend['diff'])}. The small-swing approximation 2π = {pend['small'][:8]} is off by {float(pend['agm']) - float(pend['small']):.3f}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Euler, Runge, Heun, Kutta", toc="The evidence", blocks=[
            dict(type="p", text="Euler proposed his method in the *Institutionum calculi integralis* (1768–1770); it is first order (Wikipedia, Euler method). Runge's idea was to base the step \"not on this unsymmetrical and relatively inaccurate Riemann rule, but on such improved formulas as the midpoint and trapezoidal rules\"; Heun \"took the order conditions as far as 4\"; Kutta \"made a complete classification of order 4 methods\" and reached order 5, a gap closed by Nyström in 1925 (Butcher, *Applied Numerical Mathematics*, 1996)."),
            dict(type="p", text="Kutta's doctoral thesis of 1901 \"contains the now famous Runge-Kutta method\" (MacTutor); the 3/8 rule is \"also due to Kutta in 1901\" (Wikipedia). The third-order weights used here (1/4, 0, 3/4) are the commonly quoted ones for a method of Heun's kind; Butcher's printed table could not be read in the opened copy, so the program checks their order rather than their attribution (**conjecture** for the attribution)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Every simulation takes steps", toc="Full circle", blocks=[
            dict(type="p", text="Planets, circuits, chemical reactions and weather are all described by differential equations that no formula solves. Programs that simulate them still take steps, and the idea of this topic, several slope samples per step with weights that cancel the error, is inside the standard solvers, usually paired with a second estimate that tells the program how large its next step may safely be."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"For an error below 10⁻⁶ on the simplest equation, Euler's method needs {next(c for c in cost if c['name'] == 'Euler')['evals']:,} slope evaluations and Kutta's classical method {next(c for c in cost if c['name'] == 'Classical')['evals']}: the same answer for about 1/{round(next(c for c in cost if c['name'] == 'Euler')['evals'] / next(c for c in cost if c['name'] == 'Classical')['evals']):,} of the work."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Take one Euler step of size 1 on y' = y from y(0) = 1. What do you get, and what is the truth?", "1 + 1·1 = 2, against e = 2.718...: Euler's step follows the starting slope, which is too small for a solution that keeps getting steeper."),
            ("Halving the step of a fourth-order method divides the error by about how much?", f"2⁴ = 16. The program measures ratios of {cl['ratios'][0]} to {cl['ratios'][-1]} as the step shrinks."),
            ("Why does Euler's method make a spring's circle grow?", "Each step moves along the tangent to the circle, which always leads slightly outward: x² + v² gains a factor 1 + h²."),
            ("The classical method uses four slopes per step and Euler one. Why can the classical method still be cheaper?", f"Its error shrinks like h⁴, so it can take far longer steps for the same accuracy: {next(c for c in cost if c['name'] == 'Classical')['evals']} evaluations against {next(c for c in cost if c['name'] == 'Euler')['evals']:,} here."),
            ("What does an order condition say?", "That some weighted sum of the method's coefficients equals the number the Taylor series of the true solution requires, for example Σ bᵢcᵢ = 1/2."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Ueber die numerische Auflösung von Differentialgleichungen (1895)", text="Runge's paper, in an open-access scan.",
                 draw=C.draw_manuscript, link="https://zenodo.org/record/2178704", link_text="Zenodo (CC0)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "RungeKutta", d["checks"],
                           "the eight order conditions for each of five methods in exact fractions, the measured error ratios, Euler's growth factor on the spring, the smallest step count for an error below 10⁻⁶ (and that one fewer step misses it), and the pendulum's period against Gauss's arithmetic–geometric mean.",
                           ["static double[] step(", "static Object[][] conditions("]),
    ]
    return dict(
        title="Runge–Kutta", date="1895–1901",
        description="Era 4, topic 2 of The Algorithm Evolution Atlas: Runge, Heun and Kutta's methods for differential equations, which sample the slope several times per step.",
        lede="Most laws of motion are differential equations that no formula solves. Euler stepped along the slope; Runge, Heun and Kutta sampled the slope several times inside each step and weighted the samples so that their errors cancel.",
        fieldnote=f"With one slope per step, I needed {next(c for c in cost if c['name'] == 'Euler')['steps']:,} steps to get e right to six places. With four slopes, weighted one sixth, one third, one third and one sixth, I needed {next(c for c in cost if c['name'] == 'Classical')['steps']}. The weights came from a German doctoral thesis of 1901.",
        card=[("When", "Runge 1895; Heun 1900; Kutta 1901"),
              ("Where", "Germany"),
              ("What hurt", "Euler's steps must be tiny to be accurate"),
              ("The fix", "Several slopes per step, weighted to cancel error"),
              ("Cost", f"Error ∝ h⁴ for 4 slopes a step; error ∝ h for 1")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `RungeKutta.java`.",
    )
