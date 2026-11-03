"""Era 9, topic 5: Adam. Every number is parsed from Adam.java's output."""
import math
import re

import common as C
from diagrams import Diagram

NAMES = ["SGD", "momentum", "AdaGrad", "RMSProp", "Adam"]


def parse(text: str) -> dict:
    d = {"race": []}
    for ln in text.splitlines():
        if ln.startswith("race: "):
            head = re.match(r"race: ([\w ]+) ; ([\d,]+) parameters, ([\d,]+) steps, ([^,]+), loss at the start ([\d.]+)", ln).groups()
            rows = re.findall(r"(SGD|momentum|AdaGrad|RMSProp|Adam) best rate ([\d.e-]+) loss ([\d.]+), by rate ([\d. a-z]+?)(?= ;|$)", ln)
            d["race"].append(dict(name=head[0], params=head[1], steps=head[2], kind=head[3], start=head[4],
                                  rows=[dict(m=m, best=b, loss=l, all=a.split()) for m, b, l, a in rows]))
        elif ln.startswith("tuning: "):
            d["grid"] = re.search(r"rates tried ([\d.e -]+?) ;", ln).group(1).split()
            d["spread"] = re.findall(r"(SGD|momentum|AdaGrad|RMSProp|Adam) ([\d.e-]+), ([\d.e-]+), ([\d.e-]+) \(factor (\d+)\)", ln)
            d["default"] = re.findall(r"(spirals|rare features|valley) ([\d.]+) \(best of all methods ([\d.]+)\)", ln)
        elif ln.startswith("bias: "):
            d["bias"] = dict(steps=re.findall(r"step (\d+): ([\d.]+)", ln.split(" ; ")[2]),
                             worst=re.search(r"largest ([\d.]+) at step (\d+)", ln).groups(),
                             rates=re.findall(r"rate ([\d.e-]+): ([\d.]+) corrected, ([\d.]+) uncorrected", ln))
        elif m := re.match(r"scale: .*?largest difference in any parameter ([\d.eE+-]+) ; SGD fed the same gradients: parameter 1 differs by ([\d.]+)", ln):
            d["scale"] = m.groups()
        elif ln.startswith("convex: "):
            d["convex"] = re.findall(r"(SGD|Adam \(beta1 0, beta2 0\.1\)|AMSGrad \(the same betas\)) (?:ends )?at (-?[\d.]+)", ln)
        elif ln.startswith("paths: "):
            d["paths"] = []
            for part in ln.split(" ; ")[1:]:
                m = re.match(r"(\w+) rate ([\d.]+) end ([\d.]+) (.*)$", part)
                d["paths"].append(dict(m=m.group(1), rate=float(m.group(2)), end=m.group(3),
                                       pts=[tuple(map(float, p.split(","))) for p in m.group(4).split()]))
    d["checks"] = C.checks(text)
    return d


COL = {"SGD": "muted", "momentum": "ink", "AdaGrad": "yellow", "RMSProp": "blue", "Adam": "red"}


# ----------------------------------------------------------------------------------------------------------------------
def paths_svg(d):
    def draw(t, standalone):
        W, H = 760, 360
        o = [C.text(20, 26, "f(x, y) = (x²/10 + 10y²)/2: a valley 100 times steeper across than along. 120 steps from the same start.", t["ink"], 13, "start", 700)]
        X0, X1, Y0, Y1 = 40, 600, 50, 330
        sx = lambda x: X0 + (x + 10) / 12 * (X1 - X0)
        sy = lambda y: Y0 + (2.5 - y) / 5 * (Y1 - Y0)
        for lev in [0.05, 0.3, 1, 2.5, 5]:
            a, b = math.sqrt(20 * lev), math.sqrt(lev / 5)
            o.append(f'<ellipse cx="{sx(0):.1f}" cy="{sy(0):.1f}" rx="{a / 12 * (X1 - X0):.1f}" ry="{b / 5 * (Y1 - Y0):.1f}" style="fill:none;stroke:{t["rule"]};stroke-width:1"/>')
        o.append(C.circle(sx(0), sy(0), 4, t["ink"]))
        for k, p in enumerate(d["paths"]):
            c = t[COL[p["m"]]]
            o.append(C.path("M" + " L".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in p["pts"]), c, "none", 2.2 if p["m"] == "Adam" else 1.6))
            o.append(C.text(620, 70 + k * 24, f"{p['m']} (rate {p['rate']:g}): f = {p['end']}", c if p["m"] != "SGD" else t["muted"], 12, "start", 700 if p["m"] == "Adam" else 400))
        o.append(C.text(20, 352, "Each method at a rate that suits it. Ellipses are contours; the dot is the minimum.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Paths of five optimizers on a narrow valley", t, standalone, 0.55, 760)
    return draw


def heat_svg(d):
    grid = d["grid"]

    def draw(t, standalone):
        cw, lw, rh = 62, 92, 22
        W = lw + cw * len(grid) + 20
        blocks = []
        y = 34
        o = [C.text(20, 22, "Final loss at each learning rate (mean of 3 seeds); the darker the cell, the closer to that problem's best", t["ink"], 13, "start", 700)]
        for pr in d["race"]:
            best = min(float(r["loss"]) for r in pr["rows"])
            start = float(pr["start"])
            o.append(C.text(20, y + 16, f"{pr['name']} (start {pr['start']})", t["ink"], 12, "start", 700))
            y += 24
            for k, g in enumerate(grid):
                o.append(C.text(lw + cw * k + cw / 2, y + 12, g, t["muted"], 11, "middle"))
            y += 18
            for r in pr["rows"]:
                o.append(C.text(20, y + 15, r["m"], t["ink"], 12, "start", 700 if r["m"] == "Adam" else 400))
                for k, v in enumerate(r["all"]):
                    x = lw + cw * k
                    if v == "diverged":
                        o.append(C.rect(x + 1, y + 1, cw - 2, rh - 2, t["paper"], t["rule"], 1))
                        o.append(C.text(x + cw / 2, y + 15, "blew up", t["muted"], 10, "middle"))
                        continue
                    L = float(v)
                    # 1 at the best loss, 0 at the starting loss or worse, on a log scale
                    q = max(0.0, min(1.0, math.log(start / L) / math.log(start / best))) if start > best else 0
                    q = q ** 1.5
                    o.append(C.rect(x + 1, y + 1, cw - 2, rh - 2, t["blue"], None, 0, 2, f";fill-opacity:{0.08 + 0.8 * q:.2f}"))
                    s = f"{L:.3g}" if L < 100 else f"{L:.0f}"
                    o.append(C.text(x + cw / 2, y + 15, s, t["paper"] if q > 0.55 else t["ink"], 11, "middle", 700 if v == r["all"][[float(a) if a != "diverged" else 1e99 for a in r["all"]].index(min(float(a) if a != "diverged" else 1e99 for a in r["all"]))] else 400))
                y += rh
            y += 12
        H = y + 6
        return C.svg_doc(W, H, "".join(o), "Final loss of five optimizers at ten learning rates on three problems", t, standalone, 0.5, W)
    return draw


ADAM_HTML = """
<div class="board adam-board">
  <div style="min-width:0"><div class="adam-view" id="adam-view"></div></div>
  <div style="min-width:0">
    <div class="adam-meth" id="adam-meth"></div>
    <label class="adam-row">learning rate × <input type="range" id="adam-lr" min="-1" max="1" step="0.1" value="0"> <b id="adam-lrv">1</b></label>
    <label class="adam-row"><input type="checkbox" id="adam-scale"> multiply every gradient along y by 100</label>
    <div class="adam-btns"><button type="button" class="primary" id="adam-go">Run 120 steps</button><button type="button" id="adam-reset">Start point back</button></div>
    <div class="adam-res" id="adam-res"></div>
    <p class="say" id="adam-say" aria-live="polite"></p>
  </div>
</div>
"""

ADAM_CSS = """
.adam-board{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.adam-board{grid-template-columns:1fr}}
.adam-view svg{width:100%;height:auto;display:block;background:var(--wash);cursor:crosshair}
.adam-meth{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:13px;margin-bottom:8px}
.adam-row{display:block;font-size:13px;margin:6px 0}
.adam-row input[type=range]{vertical-align:middle;width:9em}
.adam-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.adam-res{font:12.5px var(--mono);display:grid;gap:2px}
"""

ADAM_JS = r"""
(() => {
  const view = document.getElementById("adam-view");
  if (!view) return;
  const M = [["SGD", 0.15, "var(--muted)"], ["momentum", 0.015, "var(--ink)"], ["AdaGrad", 0.5, "var(--yellow)"], ["RMSProp", 0.1, "var(--blue)"], ["Adam", 0.1, "var(--red)"]];
  const on = M.map(() => true);
  const box = document.getElementById("adam-meth");
  M.forEach(([n, , c], k) => { const l = el("label", {}, box); const i = el("input", {type: "checkbox", id: `adam-m${k}`}, l); i.checked = true; i.addEventListener("change", () => { on[k] = i.checked; go(); }); const s = el("span", {style: `color:${c};font-weight:700`}, l, " " + n); });
  let start = [-9, 2.2];
  const f = (x, y) => 0.5 * (x * x / 10 + 10 * y * y);
  const X = x => 30 + (x + 10) / 12 * 580, Y = y => 20 + (2.5 - y) / 5 * 360, iX = px => (px - 30) / 580 * 12 - 10, iY = py => 2.5 - (py - 20) / 360 * 5;
  function run(k, lr, scale) {
    let w = start.slice(), m = [0, 0], v = [0, 0], t = 0;
    const pts = [w.slice()];
    for (let s = 0; s < 120; s++) {
      const g = [w[0] / 10, 10 * w[1] * scale];
      t++;
      for (let i = 0; i < 2; i++) {
        let step;
        if (k === 0) step = lr * g[i];
        else if (k === 1) { m[i] = 0.9 * m[i] + g[i]; step = lr * m[i]; }
        else if (k === 2) { v[i] += g[i] * g[i]; step = lr * g[i] / (Math.sqrt(v[i]) + 1e-8); }
        else if (k === 3) { v[i] = 0.9 * v[i] + 0.1 * g[i] * g[i]; step = lr * g[i] / (Math.sqrt(v[i]) + 1e-8); }
        else { m[i] = 0.9 * m[i] + 0.1 * g[i]; v[i] = 0.999 * v[i] + 0.001 * g[i] * g[i]; step = lr * (m[i] / (1 - 0.9 ** t)) / (Math.sqrt(v[i] / (1 - 0.999 ** t)) + 1e-8); }
        w[i] -= step;
      }
      if (!isFinite(w[0]) || !isFinite(w[1]) || Math.abs(w[0]) > 1e6 || Math.abs(w[1]) > 1e6) { pts.push([NaN, NaN]); break; }
      pts.push(w.slice());
    }
    return pts;
  }
  function go() {
    const mult = Math.pow(10, +document.getElementById("adam-lr").value), scale = document.getElementById("adam-scale").checked ? 100 : 1;
    document.getElementById("adam-lrv").textContent = mult.toPrecision(2);
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 640 400", role: "img", "aria-label": "Paths of the chosen optimizers on a narrow valley; click to move the start"}, view);
    [0.05, 0.3, 1, 2.5, 5, 10].forEach(l => sv("ellipse", {cx: X(0), cy: Y(0), rx: Math.sqrt(20 * l) / 12 * 580, ry: Math.sqrt(l / 5) / 5 * 360, fill: "none", stroke: "var(--rule)"}, svg));
    sv("circle", {cx: X(0), cy: Y(0), r: 4, fill: "var(--ink)"}, svg);
    const res = document.getElementById("adam-res"); res.innerHTML = "";
    M.forEach(([n, base, c], k) => {
      if (!on[k]) return;
      const lr = base * mult, pts = run(k, lr, scale), last = pts[pts.length - 1], blew = !isFinite(last[0]);
      const ok = pts.filter(p => isFinite(p[0]));
      sv("polyline", {points: ok.map(([x, y]) => `${X(Math.max(-14, Math.min(4, x)))},${Y(Math.max(-3, Math.min(3, y)))}`).join(" "), fill: "none", stroke: c, "stroke-width": n === "Adam" ? 2.6 : 1.7}, svg);
      el("div", {style: `color:${c}`}, res, `${n.padEnd(9)} rate ${lr.toPrecision(2).padEnd(6)} ${blew ? "blew up" : "f = " + f(last[0], last[1]).toPrecision(3)}`);
    });
    sv("circle", {cx: X(start[0]), cy: Y(start[1]), r: 5, fill: "var(--paper)", stroke: "var(--ink)", "stroke-width": 2}, svg);
    document.getElementById("adam-say").textContent = scale > 1
      ? "Every gradient along y is now 100 times larger. SGD and momentum take steps 100 times longer and blow up; AdaGrad, RMSProp and Adam divide by the gradient's own size and trace the same path as before."
      : "Across the valley the slope is steep, along it gentle. SGD must keep its rate small enough not to bounce across, so it crawls along; Adam takes steps of about the same size in both directions.";
  }
  view.addEventListener("click", e => {
    const r = view.querySelector("svg").getBoundingClientRect(), px = (e.clientX - r.left) / r.width * 640, py = (e.clientY - r.top) / r.height * 400;
    start = [Math.max(-10, Math.min(2, iX(px))), Math.max(-2.5, Math.min(2.5, iY(py)))]; go();
  });
  document.getElementById("adam-lr").addEventListener("input", go);
  document.getElementById("adam-scale").addEventListener("change", go);
  document.getElementById("adam-go").addEventListener("click", go);
  document.getElementById("adam-reset").addEventListener("click", () => { start = [-9, 2.2]; go(); });
  go();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How Adam combined older ideas, and where it led")
    W = 220
    nodes = {
        "sgd": (20, 20, "Stochastic gradient descent", "step against a noisy gradient", "Robbins and Monro, 1951", "ink"),
        "mom": (265, 20, "Momentum", "keep moving the way you were going", "backpropagation paper, 1986", "ink"),
        "ada": (510, 20, "AdaGrad", "divide by the size of all past gradients", "2011", "ink"),
        "rms": (755, 20, "RMSProp", "the same, forgetting the distant past", "a Coursera lecture", "ink"),
        "adam": (387, 200, "Adam", "⊕ momentum, RMSProp and a correction for the zero start", "Kingma and Ba, 2014", "red"),
        "ams": (140, 380, "AMSGrad", "keep the largest mean square so far", "", "blue"),
        "nets": (635, 380, "Training large networks", "the Transformer (topic 9) and after", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sgd", "adam", ports=("bottom", "top:0.1"))
    D.edge("mom", "adam", ports=("bottom", "top:0.37"))
    D.edge("ada", "adam", ports=("bottom", "top:0.63"))
    D.edge("rms", "adam", ports=("bottom", "top:0.9"))
    D.edge("adam", "ams", ports=("bottom:0.2", "top"))
    D.edge("adam", "nets", ports=("bottom:0.8", "top"))
    return D


def chain():
    steps = [
        ("One step size for every parameter: too large across a steep valley, too small along it",
         "AdaGrad: divide each step by the size of that parameter's past gradients", "2011"),
        ("AdaGrad's sum only grows, so its steps shrink towards nothing",
         "RMSProp, then Adam: a running average that forgets, plus momentum", "Kingma and Ba, 2014"),
        ("Running averages that start at zero make the first steps wrong",
         "Divide by (1 − βᵗ): the bias correction", "the same paper"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from one step size to Adam")
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


def race_rows(d, m):
    return [v for p in d["race"] for r in p["rows"] if r["m"] == m for v in r["all"]]


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    last_ok = lambda r: d["grid"][max(i for i, v in enumerate(r["all"]) if v != "diverged")]
    assert all(v != "diverged" for v in race_rows(d, "Adam")), "the text says Adam never blew up"
    race = {p["name"]: p for p in d["race"]}
    b = d["bias"]
    spread = {m: (a, bb, c, f) for m, a, bb, c, f in d["spread"]}
    dflt = {n: (v, best) for n, v, best in d["default"]}
    cv = {k.split(" ")[0]: v for k, v in d["convex"]}
    best_rows = []
    for k, m in enumerate(NAMES):
        row = [m]
        for p in d["race"]:
            r = p["rows"][k]
            row += [r["best"], r["loss"]]
        row.append(spread[m][3])
        best_rows.append(row)
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Every neural network in this era is trained by stochastic gradient descent: nudge each weight against a gradient measured on a few examples. Momentum smooths the nudges; AdaGrad and RMSProp give every weight its own step size. Kingma and Ba combined momentum with RMSProp and added one correction, and called the result Adam, from *adaptive moment estimation*."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Adam. Blue: what came after. Dates for the four older methods are those Wikipedia gives."),
        ]),
        dict(id="play", eyebrow="Try it", title="Five ways down a valley", toc="Try it", blocks=[
            dict(type="p", text="The valley is 100 times steeper across than along. Each method starts with a rate that suits it; the slider multiplies all of them. Click anywhere to move the start. Then tick the box that multiplies every gradient along y by 100, and see which methods notice."),
            dict(type="widget", html=ADAM_HTML, js=ADAM_JS, css=ADAM_CSS,
                 fallback=dict(type="svg", name="paths", draw=paths_svg(d), alt="Paths of SGD, momentum, AdaGrad, RMSProp and Adam on a narrow valley", width=760),
                 note="In the interactive edition you can change the rates, the start and the units."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Two running averages", toc="How it works", blocks=[
            dict(type="p", text="**For every parameter**, with gradient g at step t, Adam keeps a running mean and a running mean square: m ← β₁m + (1 − β₁)g and v ← β₂v + (1 − β₂)g². The defaults are β₁ = 0.9 (about the last 10 gradients) and β₂ = 0.999 (about the last 1,000)."),
            dict(type="p", text="**The correction.** m and v start at 0, so for the first steps they are too small: after one step m = 0.1g and v = 0.001g². Dividing by (1 − β₁ᵗ) and (1 − β₂ᵗ) removes that bias exactly when the gradient is steady."),
            dict(type="p", text="**The step** is α · m̂ / (√v̂ + ε), with α = 0.001 and ε = 10⁻⁸ by default. If a parameter's gradients are all 1,000 times larger, m̂ and √v̂ are both 1,000 times larger and the step does not change: Adam moves each parameter by about α, whatever the units its gradient happens to come in. When the gradient's sign keeps changing, m̂ is small next to √v̂ and the steps shrink."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Measure each parameter's gradient against its own recent history. A step of m̂ / √v̂ is a signal-to-noise ratio: large and confident when the gradient is steady, small when it is noise."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Three problems, ten rates", toc="Measured", blocks=[
            dict(type="p", text=f"**The race.** Five methods on three problems: a network with {race['spirals']['params']} weights learning two interleaved spirals ({race['spirals']['steps']} steps of 16 examples), logistic regression with {race['rare features']['params']} features where most features are rare ({race['rare features']['steps']} steps), and a {race['valley']['params']}-dimensional valley whose curvature ranges from 1 to 1,000, with noise in every gradient ({race['valley']['steps']} steps). Each method was run at the ten learning rates {', '.join(d['grid'])}, three times each."),
            dict(type="svg", name="heat", draw=heat_svg(d), alt="Final loss of each method at each learning rate on the three problems", width=760),
            dict(type="p", text="Each method's best rate and the loss it reached, and how far apart the best rates of the three problems are:"),
            dict(type="table", head=["Method", "Spirals: rate", "loss", "Rare: rate", "loss", "Valley: rate", "loss", "Best rates differ by ×"], num=[1, 2, 3, 4, 5, 6, 7], rows=best_rows, hl=4),
            dict(type="p", text=f"With its best rate, no method wins everywhere: RMSProp reached the lowest loss on the spirals, AdaGrad on rare features, Adam on the valley. The difference is in the tuning: SGD's best rate was {spread['SGD'][0]} on one problem and {spread['SGD'][2]} on another, a factor of {spread['SGD'][3]}; Adam's best rates differed by a factor of {spread['Adam'][3]}. On the valley SGD blew up at every rate above {last_ok(race['valley']['rows'][0])} and momentum above {last_ok(race['valley']['rows'][1])}; Adam's steps stay close to its rate in size, and it never blew up."),
            dict(type="p", text=f"Adam's default rate, 0.001, untuned, was not good enough in this many steps: {dflt['spirals'][0]} on the spirals (best of all methods {dflt['spirals'][1]}), {dflt['rare features'][0]} on rare features ({dflt['rare features'][1]}), {dflt['valley'][0]} on the valley ({dflt['valley'][1]}). The defaults set the shape of the steps; the rate still needs choosing."),
            dict(type="p", text=f"**The bias correction.** For a steady gradient, the uncorrected step divided by the corrected one is (1 − 0.9ᵗ)/√(1 − 0.999ᵗ): " + ", ".join(f"{v} at step {s}" for s, v in b["steps"]) + f". The largest, {b['worst'][0]}, comes at step {b['worst'][1]}. On the spirals, after 300 steps:"),
            dict(type="table", head=["Rate", "With the correction", "Without"], num=[1, 2], rows=[[r, a, u] for r, a, u in b["rates"]], hl=len(b["rates"]) - 1),
            dict(type="p", text="At small rates the uncorrected early steps act like a larger rate and happen to help; at rate 0.1 they are several times too long, the network is thrown off, and it has not recovered after 300 steps. This is the instability the paper describes: without the correction, β₂ near 1 makes the first steps far too large."),
            dict(type="p", text=f"**Units do not matter.** Multiply the gradient of one parameter of the valley by 1,000 at every step, and run Adam (with ε = 0) for 500 steps: no parameter's path changed by more than {C.sci(d['scale'][0])}. SGD fed the same gradients ended {d['scale'][1]} away in that parameter."),
            dict(type="p", text=f"**A convex problem Adam gets wrong.** Wikipedia: \"Adam does not converge for all convex objectives.\" The program builds one: on every third step the gradient is +3, on the others −1, and x stays in [−1, 1]. On average the slope is +1/3, so the best x is −1. With β₁ = 0, β₂ = 0.1 and step 0.1/√t for 30,000 steps, SGD ends at {cv['SGD']} and Adam at **{cv['Adam']}**: the rare large gradient is divided by its own large size and counts no more than a common small one. AMSGrad, which divides by the largest mean square seen so far, ends at {cv['AMSGrad']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A short paper with long defaults", toc="The evidence", blocks=[
            dict(type="p", text="Kingma (University of Amsterdam, OpenAI) and Ba (University of Toronto), first posted on 22 December 2014, \"Published as a conference paper at ICLR 2015\": a method based on \"adaptive estimates of lower-order moments\" that \"has little memory requirements\" and \"is invariant to diagonal rescaling of the gradients\"; defaults α = 0.001, β₁ = 0.9, β₂ = 0.999, ε = 10⁻⁸; \"the name Adam is derived from adaptive moment estimation\"."),
            dict(type="p", text="Wikipedia on what came before and after: momentum \"appeared in Rumelhart, Hinton and Williams' paper on backpropagation learning\"; AdaGrad was \"first published in 2011\"; RMSProp was \"not published in an article but merely described in a Coursera lecture\"; \"The initial proof establishing the convergence of Adam was incomplete\"; AMSGrad uses the \"maximum of past squared gradients\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Robbins and Monro's question, again", toc="Full circle", blocks=[
            dict(type="p", text="In 1951 Robbins and Monro asked how to find a root when every measurement is noisy, and answered with steps that shrink on a schedule. Adam answers the same question for millions of parameters at once, with a schedule each parameter sets for itself from its own noise."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Multiply one gradient by 1,000 and Adam's path moves by {C.sci(d['scale'][0])}: the step depends on the gradient's ratio to its own history, not on its size."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With β₁ = 0.9, what is m after the first step if g = 5 and m started at 0? And m̂?", "m = 0.1 × 5 = 0.5; m̂ = 0.5 / (1 − 0.9) = 5, the gradient itself."),
            ("A parameter's gradient is always exactly 2. How far does Adam move it each step, with α = 0.001?", "m̂ = 2 and √v̂ = 2 after correction, so the step is 0.001 · 2/2 = 0.001: α itself."),
            ("Why can AdaGrad's steps become too small in a long training run?", "It divides by the square root of the sum of all past squared gradients, which only grows."),
            ("A weight belongs to a word seen once in 10,000 examples. Why might Adam suit it better than SGD?", "When its gradient finally arrives, it is divided by a small √v̂, so the step is large; SGD would give it the same small rate as every common weight."),
            ("If gradients flip between +1 and −1 every step, what happens to Adam's steps?", "m̂ stays near 0 while √v̂ is near 1, so the steps become tiny: noise is recognized as noise."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Adam: A Method for Stochastic Optimization (2014)", text="Kingma and Ba, arXiv:1412.6980.",
                 draw=C.draw_manuscript, link="https://arxiv.org/abs/1412.6980", link_text="arXiv:1412.6980", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Adam", d["checks"],
                           "the bias correction's first factor, that Adam's path ignores the scale of a gradient, the convex counterexample, and that Adam's best rate moves less than SGD's.",
                           ["void step(double[] w, double[] g)"]),
    ]
    return dict(
        title="Adam", date="2014",
        description="Era 9, topic 5 of The Algorithm Evolution Atlas: Adam (Kingma and Ba, 2014), momentum and RMSProp with a bias correction, compared with SGD, AdaGrad and RMSProp.",
        lede="A neural network learns by nudging each of its weights against a gradient. But some weights see large, steady gradients and others small, rare, noisy ones. In December 2014 Kingma and Ba gave every weight a step size of its own, measured from two running averages.",
        fieldnote=f"I raced five ways of descending through three landscapes. None won everywhere. But SGD's best stride changed by a factor of {spread['SGD'][3]} from one landscape to another, and Adam's by {spread['Adam'][3]}; and when I measured one direction in different units, Adam walked exactly the same path.",
        card=[("When", "December 2014; ICLR 2015"),
              ("Where", "Amsterdam and Toronto"),
              ("What hurt", "One step size for parameters of every scale"),
              ("The fix", "Per-parameter steps from running moments, bias-corrected"),
              ("Checked", f"Path unchanged to {C.sci(d['scale'][0])} when a gradient is scaled by 1,000")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Adam.java`.",
    )
