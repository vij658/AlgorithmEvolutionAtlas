"""Era 8, topic 1: Support vector machines. Every number is parsed from SupportVectorMachines.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"separable: (\d+) points .*? ; widest street: half-width ([\d.]+), found by ([\d,]+) two-alpha steps, (\d+) support vectors ; a search over ([\d,]+) directions with refinement gives ([\d.]+) ; line: w = \(([-\d.]+), ([-\d.]+)\), b = ([-\d.]+) ; perceptron, same points in the same order: (\d+) sweeps, (\d+) corrections, half-width ([\d.]+) \((\d+)% of the widest\)", ln):
            d["sep"] = dict(n=m.group(1), street=m.group(2), steps=m.group(3), sv=m.group(4), dirs=m.group(5), searched=m.group(6),
                            w0=m.group(7), w1=m.group(8), b=m.group(9), sweeps=m.group(10), corr=m.group(11), pm=m.group(12), pct=m.group(13))
        elif m := re.match(r"trick: .*? for ([\d,]+) random pairs: largest relative difference ([\d.eE+-]+)", ln):
            d["trick"] = dict(n=m.group(1), worst=m.group(2))
        elif ln.startswith("kernel: "):
            rows = []
            for part in ln.split(" ; ")[1:]:
                mm = re.match(r"(.*?) kernel: (\d+) of 200 training points wrong, ([\d,]+) of 4,000 test points wrong \(([\d.]+)%\), (\d+) support vectors", part)
                rows.append(dict(k=mm.group(1), tr=mm.group(2), te=mm.group(3), tep=mm.group(4), sv=mm.group(5)))
            d["kernel"] = rows
        elif ln.startswith("soft: "):
            parts = ln.split(" ; ")
            rows = []
            for part in parts[2:-1]:
                mm = re.match(r"C = ([\d.]+): half-width ([\d.]+), (\d+) support vectors, (\d+) points inside the street or beyond, (\d+) training errors, test error ([\d.]+)%", part)
                rows.append(dict(C=mm.group(1), half=mm.group(2), sv=mm.group(3), inside=mm.group(4), tr=mm.group(5), te=mm.group(6)))
            d["soft"] = dict(rows=rows, best=re.search(r"best test error at C = ([\d.]+)", parts[-1]).group(1))
        elif ln.startswith("widget: "):
            parts = ln.split(" ; ")
            seed = int(re.search(r"seed (\d+)", parts[0]).group(1))
            runs = []
            for part in parts[1:]:
                mm = re.match(r"C=([\d.]+): w=\(([-\d.]+), ([-\d.]+)\) b=([-\d.]+) half-width=([\d.]+) steps=(\d+) errors=(\d+) support=([\d,]+)", part)
                runs.append(dict(C=float(mm.group(1)), w0=float(mm.group(2)), w1=float(mm.group(3)), b=float(mm.group(4)), half=float(mm.group(5)),
                                 steps=int(mm.group(6)), errors=int(mm.group(7)), support=[int(x) for x in mm.group(8).split(",")]))
            d["widget"] = dict(seed=seed, runs=runs)
    d["checks"] = C.checks(text)
    return d


def widget_points(seed):
    """The program's 32-bit generator and point rule, repeated here to draw the figure."""
    s = seed
    pts = []
    for _ in range(40):
        u = []
        for _ in range(3):
            s = (s * 1664525 + 1013904223) & 0xFFFFFFFF
            u.append(s / 4294967296.0)
        pts.append((u[0], u[1], 1 if u[0] + u[1] + 0.4 * (u[2] - 0.5) > 1 else -1))
    return pts


# ----------------------------------------------------------------------------------------------------------------------
def street_svg(d):
    """The widget's 40 points with the street for C = 100 and for C = 1, side by side."""
    wg = d["widget"]
    pts = widget_points(wg["seed"])
    picks = [r for r in wg["runs"] if r["C"] in (1.0, 100.0)]

    def draw(t, standalone):
        o = []
        W, H = 760, 400
        o.append(C.text(20, 26, "The same 40 points, two prices for standing in the street", t["ink"], 13, "start", 700))
        for k, r in enumerate(picks):
            x0, y0, S = 30 + k * 370, 50, 300
            X = lambda v: x0 + v * S
            Y = lambda v: y0 + (1 - v) * S
            o.append(C.rect(x0, y0, S, S, t["wash"], t["axis"], 1))
            # the line w.x + b = c, clipped to the square: solve for y at x = 0 and x = 1
            for cval, sw, dash in ((0, 2.2, ""), (1, 1.2, ";stroke-dasharray:5 4"), (-1, 1.2, ";stroke-dasharray:5 4")):
                ya = (cval - r["b"]) / r["w1"]
                yb = (cval - r["b"] - r["w0"]) / r["w1"]
                o.append(f'<clipPath id="cl{k}{cval + 1}"><rect x="{x0}" y="{y0}" width="{S}" height="{S}"/></clipPath>')
                o.append(f'<g clip-path="url(#cl{k}{cval + 1})">' + C.line(X(0), Y(ya), X(1), Y(yb), t["ink"], sw, f'style="stroke-linecap:round{dash}"' if dash else "") + "</g>")
            for i, (px, py, lab) in enumerate(pts):
                col = t["red"] if lab > 0 else t["blue"]
                o.append(C.circle(X(px), Y(py), 5, col))
                if i in r["support"]:
                    o.append(f'<circle cx="{X(px):.1f}" cy="{Y(py):.1f}" r="8.5" fill="none" stroke="{t["ink"]}" stroke-width="1.3"/>')
            o.append(C.text(x0 + S / 2, y0 + S + 22, f"C = {r['C']:g}: half-width {r['half']:.3f}", t["ink"], 12.5, "middle", 700))
            o.append(C.text(x0 + S / 2, y0 + S + 40, f"{len(r['support'])} support vectors (ringed), {r['errors']} on the wrong side", t["muted"], 12, "middle"))
        return C.svg_doc(W, H, "".join(o), "Two soft-margin streets on the same points", t, standalone, 0.55, 760)
    return draw


SVM_HTML = """
<div class="board svm-board">
  <div style="min-width:0"><div class="svm-view" id="svm-view"></div></div>
  <div style="min-width:0">
    <div class="svm-row" role="group" aria-label="Price C"><span class="lbl">Price C</span><span id="svm-cs"></span></div>
    <div class="svm-row" role="group" aria-label="New point"><span class="lbl">Click adds</span>
      <button type="button" id="svm-red" class="primary">red (+1)</button><button type="button" id="svm-blue">blue (−1)</button></div>
    <div class="svm-row"><button type="button" id="svm-reset">The program's 40 points</button></div>
    <div class="svm-stats" id="svm-stats"></div>
    <p class="say" id="svm-say" aria-live="polite"></p>
  </div>
</div>
"""

SVM_CSS = """
.svm-view svg{display:block;width:100%;height:auto;background:var(--wash);cursor:crosshair}
.svm-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0}
.svm-row .lbl{font-size:13px;color:var(--muted);min-width:6.5em}
.svm-row button{font-weight:400;font-size:13px;padding:3px 9px}
.svm-row button.on{background:var(--ink);color:var(--paper)}
.svm-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

SVM_JS = r"""
(() => {
  const view = document.getElementById("svm-view");
  if (!view) return;
  const SEED = __SEED__, PROG = __PROG__;
  let pts, C = 10, addLabel = 1, edited = false, s32;
  function next32() { s32 = (Math.imul(s32, 1664525) + 1013904223) | 0; return (s32 >>> 0) / 4294967296; }
  function programPoints() { s32 = SEED; const p = []; for (let i = 0; i < 40; i++) { const x = next32(), y = next32(), u = next32(); p.push([x, y, x + y + 0.4 * (u - 0.5) > 1 ? 1 : -1]); } return p; }
  // the program's sequential minimal optimization, line for line
  function train(x, y, Cc) {
    const n = x.length, K = (a, b) => a[0] * b[0] + a[1] * b[1];
    const Q = x.map((xi, i) => x.map((xj, j) => y[i] * y[j] * K(xi, xj)));
    const a = new Array(n).fill(0), G = new Array(n).fill(-1);
    let it = 0;
    while (true) {
      let i = -1, j = -1, gmax = -Infinity, gmin = Infinity;
      for (let t = 0; t < n; t++) {
        const up = y[t] === 1 ? a[t] < Cc : a[t] > 0, low = y[t] === 1 ? a[t] > 0 : a[t] < Cc, v = -y[t] * G[t];
        if (up && v > gmax) { gmax = v; i = t; }
        if (low && v < gmin) { gmin = v; j = t; }
      }
      if (gmax - gmin < 1e-10 || it >= 2000000) break;
      it++;
      const ai = a[i], aj = a[j];
      if (y[i] !== y[j]) {
        let quad = Q[i][i] + Q[j][j] + 2 * Q[i][j]; if (quad <= 0) quad = 1e-12;
        const delta = (-G[i] - G[j]) / quad, diff = a[i] - a[j];
        a[i] += delta; a[j] += delta;
        if (diff > 0) { if (a[j] < 0) { a[j] = 0; a[i] = diff; } } else { if (a[i] < 0) { a[i] = 0; a[j] = -diff; } }
        if (diff > 0) { if (a[i] > Cc) { a[i] = Cc; a[j] = Cc - diff; } } else { if (a[j] > Cc) { a[j] = Cc; a[i] = Cc + diff; } }
      } else {
        let quad = Q[i][i] + Q[j][j] - 2 * Q[i][j]; if (quad <= 0) quad = 1e-12;
        const delta = (G[i] - G[j]) / quad, sum = a[i] + a[j];
        a[i] -= delta; a[j] += delta;
        if (sum > Cc) { if (a[i] > Cc) { a[i] = Cc; a[j] = sum - Cc; } } else { if (a[j] < 0) { a[j] = 0; a[i] = sum; } }
        if (sum > Cc) { if (a[j] > Cc) { a[j] = Cc; a[i] = sum - Cc; } } else { if (a[i] < 0) { a[i] = 0; a[j] = sum; } }
      }
      const di = a[i] - ai, dj = a[j] - aj;
      for (let k = 0; k < n; k++) G[k] += Q[i][k] * di + Q[j][k] * dj;
    }
    let sum = 0, free = 0, hi = Infinity, lo = -Infinity;
    for (let t = 0; t < n; t++) {
      const yg = y[t] * G[t];
      if (a[t] > 1e-12 && a[t] < Cc - 1e-12) { sum += yg; free++; }
      else if ((a[t] <= 1e-12) === (y[t] === 1)) hi = Math.min(hi, yg); else lo = Math.max(lo, yg);
    }
    const rho = free > 0 ? sum / free : (hi + lo) / 2;
    for (let t = 0; t < n; t++) if (a[t] < 1e-12) a[t] = 0;
    const w = [0, 0];
    for (let t = 0; t < n; t++) { w[0] += a[t] * y[t] * x[t][0]; w[1] += a[t] * y[t] * x[t][1]; }
    return {a, w, b: -rho, it};
  }
  function solve() {
    const m = train(pts.map(p => [p[0], p[1]]), pts.map(p => p[2]), C);
    const f = p => m.w[0] * p[0] + m.w[1] * p[1] + m.b;
    const errors = pts.filter(p => f(p) * p[2] <= 0).length;
    return Object.assign(m, {errors, half: 1 / Math.hypot(m.w[0], m.w[1])});
  }
  function draw() {
    const m = solve(), S = 400;
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: `0 0 ${S} ${S}`, role: "img", "aria-label": "Points and the street"}, view);
    const yAt = (c, x) => (c - m.b - m.w[0] * x) / m.w[1];   // the line w.x + b = c at this x
    const clip = sv("clipPath", {id: "svm-clip"}, sv("defs", {}, svg));
    sv("rect", {x: 0, y: 0, width: S, height: S}, clip);
    const band = [[0, yAt(-1, 0)], [1, yAt(-1, 1)], [1, yAt(1, 1)], [0, yAt(1, 0)]].map(([x, y]) => `${x * S},${(1 - y) * S}`).join(" ");
    sv("polygon", {points: band, fill: "var(--yellow)", "fill-opacity": 0.25, "clip-path": "url(#svm-clip)"}, svg);
    for (const [c, wd, da] of [[0, 2.2, null], [1, 1.2, "5 4"], [-1, 1.2, "5 4"]]) {
      const ya = (c - m.b) / m.w[1], yb = (c - m.b - m.w[0]) / m.w[1];
      sv("line", {x1: 0, y1: (1 - ya) * S, x2: S, y2: (1 - yb) * S, stroke: "var(--ink)", "stroke-width": wd, "stroke-dasharray": da}, svg);
    }
    pts.forEach((p, i) => {
      sv("circle", {cx: p[0] * S, cy: (1 - p[1]) * S, r: 5.5, fill: p[2] > 0 ? "var(--red)" : "var(--blue)"}, svg);
      if (m.a[i] > 0) sv("circle", {cx: p[0] * S, cy: (1 - p[1]) * S, r: 9, fill: "none", stroke: "var(--ink)", "stroke-width": 1.4}, svg);
    });
    const st = document.getElementById("svm-stats"); st.innerHTML = "";
    const nsv = m.a.filter(v => v > 0).length;
    el("div", {}, st, `points: ${pts.length}${edited ? " (edited)" : ""}`);
    el("div", {}, st, `w = (${m.w[0].toFixed(4)}, ${m.w[1].toFixed(4)}), b = ${m.b.toFixed(4)}`);
    el("div", {}, st, `half-width of the street: ${m.half.toFixed(4)}`);
    el("div", {}, st, `support vectors: ${nsv}, on the wrong side: ${m.errors}`);
    el("div", {}, st, `two-alpha steps: ${m.it}`);
    const pg = PROG.find(r => r.C === C);
    document.getElementById("svm-say").textContent = !edited && pg
      ? `The program, for C = ${C}: w = (${pg.w0.toFixed(4)}, ${pg.w1.toFixed(4)}), b = ${pg.b.toFixed(4)}, half-width ${pg.half.toFixed(4)}, ${pg.steps} steps, ${pg.errors} on the wrong side. The same.`
      : "Your own points: the street is recomputed from scratch with the same algorithm.";
  }
  const cs = document.getElementById("svm-cs");
  for (const c of [0.1, 1, 10, 100]) {
    const b = el("button", {type: "button", class: c === C ? "on" : ""}, cs, String(c));
    b.addEventListener("click", () => { C = c; [...cs.children].forEach(x => x.classList.toggle("on", x === b)); draw(); });
  }
  const red = document.getElementById("svm-red"), blue = document.getElementById("svm-blue");
  red.addEventListener("click", () => { addLabel = 1; red.classList.add("primary"); blue.classList.remove("primary"); });
  blue.addEventListener("click", () => { addLabel = -1; blue.classList.add("primary"); red.classList.remove("primary"); });
  view.addEventListener("click", e => {
    const svg = view.querySelector("svg"); if (!svg) return;
    const r = svg.getBoundingClientRect(), x = (e.clientX - r.left) / r.width, y = 1 - (e.clientY - r.top) / r.height;
    if (x < 0 || x > 1 || y < 0 || y > 1) return;
    pts.push([x, y, addLabel]); edited = true; draw();
  });
  document.getElementById("svm-reset").addEventListener("click", () => { pts = programPoints(); edited = false; draw(); });
  pts = programPoints();
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How support vector machines combined older ideas, and where they led")
    W = 210
    nodes = {
        "perc": (20, 20, "The perceptron", "any separating line will do", "Rosenblatt; Era 5", "ink"),
        "gp": (395, 20, "Generalised portrait", "the widest street between classes", "Vapnik, Chervonenkis, 1962–64", "ink"),
        "dot": (770, 20, "Only dot products", "the dual needs xᵢ · xⱼ and nothing else", "", "ink"),
        "kern": (395, 180, "Optimal margin + kernels", "⊕ a kernel replaces the dot product", "Boser, Guyon, Vapnik, 1992", "red"),
        "soft": (20, 340, "The soft margin", "⊕ pay C for each point inside the street", "Cortes and Vapnik, 1995", "red"),
        "smo": (770, 340, "SMO", "⊕ solve for two multipliers at a time", "Platt, 1998", "ink"),
        "today": (395, 490, "Digits", "degree 2 and up beat LeNet1 on postal digits", "Cortes and Vapnik, 1995", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("perc", "kern", ports=("bottom", "top:0.15"))
    D.edge("gp", "kern", ports=("bottom", "top"))
    D.edge("dot", "kern", ports=("bottom", "top:0.85"))
    D.edge("kern", "soft", ports=("bottom:0.15", "top"))
    D.edge("kern", "smo", ports=("bottom:0.85", "top"))
    D.edge("soft", "today", ports=("bottom", "left"))
    D.edge("smo", "today", ports=("bottom", "right"))
    D.text(20, 615, "Digits: the US Postal Service benchmark in Cortes and Vapnik's paper. SMO is how the program trains.", "caption")
    return D


def chain(d):
    s, k, so = d["sep"], d["kernel"], d["soft"]
    lin = next(r for r in k if r["k"] == "linear")
    poly = next(r for r in k if r["k"].startswith("degree-2"))
    steps = [
        (f"A perceptron stops at the first line that separates: its street is {s['pct']}% as wide as the widest",
         f"The widest street, fixed by {s['sv']} support vectors (half-width {s['street']})", "Vapnik and Chervonenkis"),
        (f"No line separates a disc from a ring: {lin['tr']} of 200 wrong", f"A kernel bends the street: degree 2, {poly['tr']} wrong, {poly['te']} of 4,000 test points wrong", "Boser, Guyon and Vapnik, 1992"),
        ("Real classes overlap: no street is empty",
         f"The soft margin: pay C per point inside; best test error here at C = {so['best']}", "Cortes and Vapnik, 1995"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from any line to the widest street")
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
    s, tr, k, so, wg = d["sep"], d["trick"], d["kernel"], d["soft"], d["widget"]
    k_rows = [[r["k"], r["tr"], f"{r['te']} ({r['tep']}%)", r["sv"]] for r in k]
    so_rows = [[r["C"], r["half"], r["sv"], r["inside"], r["tr"], r["te"] + "%"] for r in so["rows"]]
    best_i = next(i for i, r in enumerate(so["rows"]) if r["C"] == so["best"])
    wg_rows = [[f"{r['C']:g}", f"({r['w0']:.4f}, {r['w1']:.4f})", f"{r['b']:.4f}", f"{r['half']:.4f}", str(len(r["support"])), str(r["errors"]), str(r["steps"])] for r in wg["runs"]]
    lin = next(r for r in k if r["k"] == "linear")
    poly = next(r for r in k if r["k"].startswith("degree-2"))
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The perceptron (Era 5) learned a separating line by correcting mistakes. Vapnik and Chervonenkis asked for the best separating line: the one with the widest margin. Boser, Guyon and Vapnik noticed that the method touches the examples only through dot products, and swapped in kernels; Cortes and Vapnik let points stand inside the margin, at a price. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the support vector machine's steps. Blue: the result Cortes and Vapnik reported."),
        ]),
        dict(id="play", eyebrow="Try it", title="Find the widest street", toc="Try it", blocks=[
            dict(type="p", text="Forty points from the program's generator, red (+1) and blue (−1), labelled by which side of a slightly noisy diagonal they fall. The solid line is the machine's boundary, the dashed lines the edges of its street, the yellow band the street itself; ringed points are the support vectors, the only ones that decide where the street goes. Change the price C: a small C buys a wide street with many points inside it, a large C a narrow one. Click to add points of your own. With the program's points, the widget repeats the program's arithmetic step for step and shows the same numbers."),
            dict(type="widget", html=SVM_HTML, js=SVM_JS.replace("__SEED__", str(wg["seed"])).replace("__PROG__", json.dumps(wg["runs"])), css=SVM_CSS,
                 fallback=dict(type="table", head=["C", "w", "b", "Half-width", "Support vectors", "Wrong side", "Steps"], num=[3, 4, 5, 6], rows=wg_rows),
                 note="In the interactive edition you can change C and add points, and watch the street move."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="The widest street", toc="How it works", blocks=[
            dict(type="p", text="**The street.** Write the boundary as w · x + b = 0 and ask every example to satisfy y(w · x + b) ≥ 1, with y = +1 or −1. The two lines w · x + b = ±1 are the edges of an empty street of width 2/|w|. The widest street has the smallest |w|: a quadratic program."),
            dict(type="p", text="**Support vectors.** The program's dual form has one multiplier αᵢ ≥ 0 per example, with w = Σ αᵢ yᵢ xᵢ. At the optimum αᵢ is zero for every example strictly outside the street; only the examples on its edges, the support vectors, have αᵢ > 0. Move any other point (without crossing the edge) and nothing changes."),
            dict(type="p", text="**Kernels.** The dual needs the examples only through dot products xᵢ · xⱼ. Replace each by a function K(xᵢ, xⱼ) that is a dot product in some other space, and the same algorithm draws a straight street there, which is a curved one here. (x · z + 1)² is the dot product of six features, 1, √2x₁, √2x₂, x₁², x₂², √2x₁x₂, without ever computing them."),
            dict(type="p", text="**The soft margin.** Let example i stand inside the street, or on the wrong side, by a slack ξᵢ ≥ 0 and pay C ξᵢ for it. In the dual this changes only one thing: every αᵢ is capped at C."),
            dict(type="p", text="**Training.** The program uses sequential minimal optimization: change two multipliers at a time, the pair that most violates the optimality conditions, by a formula; repeat until no pair violates them by more than 10⁻¹⁰."),
            dict(type="svg", name="street", draw=street_svg(d), alt="The widget's 40 points with the streets for C = 1 and C = 100", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do not just separate: separate with room to spare, and let only the examples at the edge decide. Then compare examples by any kernel you like; the algorithm never needs to see the new coordinates."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Street, curve and price", toc="Measured", blocks=[
            dict(type="p", text=f"**The widest street.** {s['n']} points, separable, none closer than 0.06 to the line x + y = 1. The machine found a street of half-width {s['street']} in {s['steps']} two-multiplier steps, decided by {s['sv']} support vectors; a direct search over {s['dirs']} directions of the line, refined, found the same {s['searched']}. Rosenblatt's perceptron on the same points, in the same order, separated them after {s['corr']} corrections in {s['sweeps']} sweeps, with a street of half-width {s['pm']}: {s['pct']}% of the widest."),
            dict(type="p", text=f"**The kernel trick.** (x · z + 1)² against the dot product of the six features, for {tr['n']} random pairs of points: the largest relative difference was {C.sci(tr['worst'])}, rounding error."),
            dict(type="p", text="**A disc inside a ring.** 100 points inside a disc of radius 0.3, 100 in the ring from 0.5 to 0.8, C = 10, tested on 4,000 more:"),
            dict(type="table", head=["Kernel", "Training points wrong (of 200)", "Test points wrong (of 4,000)", "Support vectors"], num=[1, 3], rows=k_rows, hl=1),
            dict(type="p", text="**Two overlapping clouds.** 100 points around (−1, 0) and 100 around (1, 0), spread 0.8, so no street can be empty; tested on 5,000 more:"),
            dict(type="table", head=["C", "Half-width", "Support vectors", "Inside the street or beyond", "Training errors", "Test error"], num=[1, 2, 3, 4, 5], rows=so_rows, hl=best_i),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Moscow to Holmdel", toc="The evidence", blocks=[
            dict(type="p", text="Royal Holloway's Centre for Reliable Machine Learning: the ideas were \"first proposed by V. N. Vapnik and A. Ya. Chervonenkis\" as the \"Generalised Portrait Method\" at the Institute of Control Sciences in Moscow; \"the development of these ideas started in 1962\", first published in 1964; in 1992 Boser, Guyon and Vapnik \"suggested a way to create nonlinear classifiers\". Wikipedia dates the invention to 1964 (with *citation needed*) and the soft margin to 1993, published 1995."),
            dict(type="p", text="Boser, Guyon and Vapnik (AT&T Bell Laboratories, 1992): \"A training algorithm that maximizes the margin between the training patterns and the decision boundary is presented\"; the solution rests on \"the subset of training patterns that are closest to the decision boundary\". Cortes and Vapnik (AT&T Bell Labs, Holmdel; *Machine Learning* 20, 1995): \"The support-vector network is a new learning machine for two-group classification problems\"; \"We here extend this result to non-separable training data\". On the US Postal Service digits, polynomials of degree 1 to 7 gave 12.0, 4.7, 4.4, 4.3, 4.3, 4.2 and 4.3% raw error, against 2.5% for people and 5.1% for LeNet1. The paper's text also says a single classifier's error \"does not exceed 1.5%\", which does not match its own table; the catalog marks that **disputed**."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The perceptron, with room to spare", toc="Full circle", blocks=[
            dict(type="p", text="The perceptron (Era 5) and the support vector machine both draw a line w · x + b = 0. The difference is which line: the perceptron takes the first that works, the support vector machine the one that works with the most room. Backpropagation (Era 7) bent the boundary by learning features in hidden layers; kernels bend it by choosing the comparison instead. LSTM (topic 6) goes the other way, and learns its features over time."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"On the same {s['n']} points the perceptron's street was {s['pct']}% as wide as the widest. The line it found was correct; it just had no reason to prefer a safer one."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("The boundary is 3x₁ + 4x₂ − 2 = 0, scaled so that the nearest points satisfy |w · x + b| = 1. How wide is the street?", "2/|w| = 2/5 = 0.4."),
            ("You delete a training point that is not a support vector and retrain. What changes?", "Nothing: its multiplier was zero, so it never entered w or b."),
            ("Why can the kernel (x · z + 1)² separate a disc from a ring?", "Its features include x₁² and x₂², and x₁² + x₂² < r² is a straight cut in those features."),
            ("What happens to the street as C grows very large?", "Standing inside costs almost infinitely much, so the machine narrows the street until as few points as possible are inside: the hard margin, if one exists."),
            ("Why did the soft margin choose σ = 1 (a penalty proportional to the slack) rather than counting errors?", "Counting errors makes the problem NP-complete; Cortes and Vapnik chose the case that keeps a unique solution."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Cortes and Vapnik's paper (1995)", text="*Machine Learning* 20, 273–297: the soft margin and the digit experiments.",
                 draw=C.draw_manuscript, link="https://homepages.math.uic.edu/~lreyzin/papers/cortes95.pdf", link_text="The paper (PDF, on a University of Illinois Chicago page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "SupportVectorMachines", d["checks"],
                           "the optimality conditions for every example after every training run, the widest street against a direct search, 100,000 kernel evaluations against the explicit features, and the widget's four runs.",
                           ["static Svm train(double[][] x, int[] y, Kernel kern, double C)"]),
    ]
    return dict(
        title="Support Vector Machines", date="1992–1995",
        description="Era 8, topic 1 of The Algorithm Evolution Atlas: the widest-margin classifier of Vapnik and Chervonenkis, kernels (Boser, Guyon and Vapnik, 1992) and the soft margin (Cortes and Vapnik, 1995), with a widget that trains by sequential minimal optimization.",
        lede="A perceptron settles for any line that separates. Vapnik and his colleagues asked for the line with the widest empty street on either side, bent it with kernels, and let a few examples stand in the street at a price.",
        fieldnote=f"I gave a perceptron and a support vector machine the same {s['n']} points. Both drew a correct line. The machine's left a street of half-width {s['street']}, held in place by {s['sv']} points; the perceptron's left {s['pm']}. On a disc inside a ring, a straight line got {lin['tr']} of 200 wrong; a kernel of degree 2 got {poly['tr']}.",
        card=[("When", "1962–64 (Moscow); kernels 1992; soft margin 1995"),
              ("Where", "Institute of Control Sciences, Moscow; AT&T Bell Laboratories"),
              ("What hurt", "Any separating line, curved boundaries, overlapping classes"),
              ("The fix", "The widest margin; kernels; a price C for slack"),
              ("Checked", f"Street {s['street']} = direct search {s['searched']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `SupportVectorMachines.java`.",
    )
