"""Era 7, topic 1: linear programming in polynomial time. Every number is parsed from LinearProgramming.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"kmpath: .*? visits them: (.*)$", ln):
            d["path"] = [tuple(int(v) for v in p.strip("()").split(",")) for p in m.group(1).split()]
        elif m := re.match(r"kleeminty: .*? the optimum 5\^n ; (.*?) ; the simplex pivots are exactly 2\^n - 1 every time, the interior-point iterations never more than (\d+)", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"n=(\d+): simplex ([\d,]+) pivots?, interior point (\d+) iterations", part)
                rows.append(dict(n=int(mm.group(1)), piv=mm.group(2), ipm=mm.group(3)))
            d["km"] = dict(rows=rows, maxipm=m.group(2))
        elif m := re.match(r"random: .*? reaching the same optimum ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"(\d+) variables and (\d+) constraints: simplex ([\d.]+) pivots, interior point ([\d.]+) iterations", part)
                rows.append(dict(n=mm.group(1), m=mm.group(2), piv=mm.group(3), ipm=mm.group(4)))
            d["rand"] = rows
        elif m := re.match(r"ellipsoid: .*? by the factor ([\d.]+) ; (.*?) ; the bound", ln):
            rows = []
            for part in m.group(2).split(" ; "):
                mm = re.match(r"side ([\d.]+): (\d+) steps \(bound (\d+)\)", part)
                rows.append(dict(side=mm.group(1), steps=int(mm.group(2)), bound=mm.group(3)))
            d["ell"] = dict(ratio=m.group(1), rows=rows)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def cube_svg(d):
    """The three-dimensional Klee-Minty cube drawn as a cube, with the simplex method's path through all 8 corners."""
    path = d["path"]

    def pos(x):
        b = [1 if v > 0 else 0 for v in x]                 # at each corner, x_i = 0 or constraint i is tight
        return 150 + 260 * b[0] + 130 * b[1], 400 - 220 * b[2] - 90 * b[1]

    def draw(t, standalone):
        o = []
        W, H = 760, 490
        o.append(C.text(20, 26, "Klee and Minty's cube for n = 3: the simplex method visits all 2³ = 8 corners", t["ink"], 13, "start", 700))
        corners = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
        P = {k: (150 + 260 * k[0] + 130 * k[1], 400 - 220 * k[2] - 90 * k[1]) for k in corners}
        for k in corners:
            for i in range(3):
                if k[i] == 0:
                    k2 = tuple(1 if j == i else k[j] for j in range(3))
                    o.append(C.line(*P[k], *P[k2], t["axis"], 1.4))
        for i in range(len(path) - 1):
            (x1, y1), (x2, y2) = pos(path[i]), pos(path[i + 1])
            o.append(C.line(x1, y1, x2, y2, t["red"], 3))
            ux, uy = x2 - x1, y2 - y1
            L = (ux * ux + uy * uy) ** 0.5
            ux, uy = ux / L, uy / L
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            o.append(C.path(f"M{mx + ux * 8:.1f},{my + uy * 8:.1f} L{mx - ux * 6 - uy * 6:.1f},{my - uy * 6 + ux * 6:.1f} L{mx - ux * 6 + uy * 6:.1f},{my - uy * 6 - ux * 6:.1f} Z", None, t["red"]))
        for i, x in enumerate(path):
            cx, cy = pos(x)
            obj = 4 * x[0] + 2 * x[1] + x[2]
            o.append(C.circle(cx, cy, 13, t["surface"], t["red"] if i in (0, len(path) - 1) else t["ink"], 2))
            o.append(C.text(cx, cy + 4.5, str(i), t["ink"], 12, "middle", 700))
            right = x[0] > 0
            o.append(C.text(cx + (18 if right else -18), cy - 4, f"({x[0]}, {x[1]}, {x[2]})", t["ink"], 12, "start" if right else "end", 700))
            o.append(C.text(cx + (18 if right else -18), cy + 12, f"value {obj}", t["blue"], 11.5, "start" if right else "end"))
        o.append(C.text(20, H - 30, "Numbers in circles: the order of the visits. Each pivot raises the value 4x₁ + 2x₂ + x₃, yet every corner is visited.", t["muted"], 12))
        o.append(C.text(20, H - 12, "The cube is squashed: x₁ runs to 5, x₂ to 25, x₃ to 125. Drawn here as a plain cube to show which corner is which.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "The simplex method's path round the Klee-Minty cube", t, standalone, 0.55, 760)
    return draw


EL_HTML = """
<div class="board el-board">
  <div style="min-width:0">
    <div class="el-view" id="el-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls"><label>Target triangle's side <select id="el-side"></select></label></div>
    <div class="el-btns"><button type="button" class="primary" id="el-step">One cut</button><button type="button" id="el-run">Run to the end</button><button type="button" id="el-reset">Start again</button></div>
    <div class="el-stats" id="el-stats"></div>
    <p class="say" id="el-say" aria-live="polite"></p>
  </div>
</div>
"""

EL_CSS = """
.el-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.el-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.el-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
.el-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
"""

EL_JS = r"""
(() => {
  const view = document.getElementById("el-view");
  if (!view) return;
  const ROWS = __ROWS__, RATIO = __RATIO__, CX = 37, CY = -21;
  const sel = document.getElementById("el-side");
  ROWS.forEach((r, i) => { const o = document.createElement("option"); o.value = i; o.textContent = r.side; sel.appendChild(o); });
  sel.value = 2;
  let z, P, steps, cons, last, prev;
  function reset() {
    const side = parseFloat(ROWS[+sel.value].side_exact);
    cons = [[0, -1, -CY], [-1, 0, -CX], [1, 1, CX + CY + side]];
    z = [0, 0]; P = [[100 * 100, 0], [0, 100 * 100]]; steps = 0; last = null; prev = null;
    draw("Start: a disc of radius 100 that surely contains the target. Its centre (red) is outside the triangle.");
  }
  function violated() { for (const c of cons) if (c[0] * z[0] + c[1] * z[1] > c[2]) return c; return null; }
  function cut() {
    const v = violated();
    if (!v) return false;
    const a = [v[0], v[1]];
    const Pa = [P[0][0] * a[0] + P[0][1] * a[1], P[1][0] * a[0] + P[1][1] * a[1]];
    const aPa = a[0] * Pa[0] + a[1] * Pa[1];
    const g = [Pa[0] / Math.sqrt(aPa), Pa[1] / Math.sqrt(aPa)];
    prev = {z: z.slice(), P: P.map(r => r.slice())}; last = v;
    z[0] -= g[0] / 3; z[1] -= g[1] / 3;
    for (let i = 0; i < 2; i++) for (let j = 0; j < 2; j++) P[i][j] = (4.0 / 3.0) * (P[i][j] - (2.0 / 3.0) * g[i] * g[j]);
    steps++;
    return true;
  }
  function ellipse(Pm) {
    const a = Pm[0][0], b = Pm[0][1], d = Pm[1][1], tr = (a + d) / 2, df = Math.sqrt(((a - d) / 2) ** 2 + b * b);
    const l1 = tr + df, l2 = Math.max(tr - df, 1e-30), ang = Math.atan2(l1 - a, b === 0 ? 1e-300 : b);
    return {rx: Math.sqrt(l1), ry: Math.sqrt(l2), ang: b === 0 && a >= d ? 0 : b === 0 ? Math.PI / 2 : ang};
  }
  function draw(msg) {
    view.innerHTML = "";
    const side = parseFloat(ROWS[+sel.value].side_exact);
    const e = ellipse(P), r = Math.max(e.rx, side * 1.2, 1e-9);
    const half = Math.max(r * 1.35, side * 1.6), mx = z[0], my = z[1];
    const S = 380, k = S / (2 * half);
    const X = x => (x - mx) * k + S / 2, Y = y => S / 2 - (y - my) * k;
    const svg = sv("svg", {viewBox: `0 0 ${S} ${S}`}, view);
    // the target triangle
    sv("polygon", {points: `${X(CX)},${Y(CY)} ${X(CX + side)},${Y(CY)} ${X(CX)},${Y(CY + side)}`, fill: "var(--blue)", "fill-opacity": 0.35, stroke: "var(--blue)", "stroke-width": 1.5}, svg);
    const ell = (Pm, c, col, w, dash) => {
      const q = ellipse(Pm);
      sv("ellipse", {cx: X(c[0]), cy: Y(c[1]), rx: q.rx * k, ry: q.ry * k, transform: `rotate(${-q.ang * 180 / Math.PI} ${X(c[0])} ${Y(c[1])})`,
                     fill: "none", stroke: col, "stroke-width": w, "stroke-dasharray": dash || ""}, svg);
    };
    if (prev) {
      ell(prev.P, prev.z, "var(--muted)", 1.5, "5 4");
      // the cut: the line through the old centre parallel to the violated constraint
      const a = last, len = 3 * half, nx = -a[1], ny = a[0], nn = Math.hypot(nx, ny);
      sv("line", {x1: X(prev.z[0] - nx / nn * len), y1: Y(prev.z[1] - ny / nn * len), x2: X(prev.z[0] + nx / nn * len), y2: Y(prev.z[1] + ny / nn * len), stroke: "var(--muted)", "stroke-width": 1.2}, svg);
    }
    ell(P, z, "var(--ink)", 2);
    sv("circle", {cx: X(z[0]), cy: Y(z[1]), r: 4, fill: violated() ? "var(--red)" : "var(--blue)"}, svg);
    const st = document.getElementById("el-stats"); st.innerHTML = "";
    el("div", {}, st, `cuts so far: ${steps}`);
    el("div", {}, st, `area: ${(Math.pow(RATIO, steps) * 100).toPrecision(3)}% of the starting disc`);
    el("div", {}, st, `the program needed ${ROWS[+sel.value].steps} cuts for this target`);
    el("div", {}, st, `view width: ${(2 * half).toPrecision(3)} units`);
    document.getElementById("el-say").textContent = msg;
  }
  document.getElementById("el-step").addEventListener("click", () => {
    if (!cut()) { draw(`The centre is inside the triangle after ${steps} cuts: a feasible point.`); return; }
    draw(violated() ? `Cut ${steps}: the centre broke a constraint, so the half on the wrong side was thrown away and a smaller ellipse drawn round the rest (area × ${RATIO}).`
                    : `Cut ${steps}: the new centre is inside the triangle. Found after ${steps} cuts.`);
  });
  document.getElementById("el-run").addEventListener("click", () => {
    let guard = 0; while (cut() && guard++ < 10000) {}
    draw(`Done: the centre lands in the triangle after ${steps} cuts (the program: ${ROWS[+sel.value].steps}).`);
  });
  document.getElementById("el-reset").addEventListener("click", reset);
  sel.addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How polynomial-time linear programming combined older ideas, and where it led")
    W = 210
    nodes = {
        "sx": (20, 20, "The simplex method", "walk along edges from corner to corner", "Era 4, topic 11", "ink"),
        "km": (395, 20, "Klee and Minty's cube", "a squashed cube where every corner is visited", "1972", "ink"),
        "el": (770, 20, "The ellipsoid method", "Shor; Nemirovski and Yudin", "1970s, for convex problems", "ink"),
        "kh": (395, 180, "Khachiyan's algorithm", "⊕ ellipsoids applied to linear programs: polynomial", "Moscow, 1979", "red"),
        "dk": (20, 340, "Dikin's affine scaling", "steps inside, scaled by the distance to each wall", "1967; rediscovered 1985", "ink"),
        "ka": (395, 340, "Karmarkar's method", "⊕ through the interior: polynomial and fast", "Bell Labs, 1984", "ink"),
        "pd": (770, 340, "Primal-dual methods", "⊕ solve the program and its dual together", "Mehrotra's predictor-corrector", "ink"),
        "today": (395, 490, "Today", "\"competitive with, and often superior to\" simplex codes", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sx", "km", ports=("right", "left"), label="no guarantee", at=0.5, dy=-8)
    D.edge("km", "kh", ports=("bottom", "top"))
    D.edge("el", "kh", ports=("bottom", "top:0.85"))
    D.edge("kh", "ka", ports=("bottom", "top"), label="polynomial, but slow", at=0.5, dx=8, anchor="start")
    D.edge("dk", "ka", ports=("right", "left"), dashed=True)
    D.edge("ka", "pd", ports=("right", "left"))
    D.edge("ka", "today", ports=("bottom", "top"))
    D.edge("pd", "today", ports=("bottom", "top:0.85"))
    D.text(20, 615, "Today: in the NEOS Guide's words. Dashed: Karmarkar's later simplification turned out to repeat Dikin's 1967 method.", "caption")
    return D


def chain(d):
    km, ell, rnd = d["km"], d["ell"], d["rand"]
    n14 = next(r for r in km["rows"] if r["n"] == 14)
    steps = [
        (f"The simplex method has no polynomial guarantee: on Klee and Minty's cube (1972) it takes {n14['piv']} pivots at n = 14",
         f"Khachiyan's ellipsoid method: every cut shrinks the region by a fixed factor ({ell['ratio']} of the area in the plane)", "Khachiyan, 1979"),
        ("The ellipsoid method is slow in practice: close to its worst case",
         "Karmarkar's interior-point method: polynomial, and fast", "Karmarkar, 1984"),
        ("Karmarkar's projective method was intricate",
         f"Primal-dual interior-point methods: at most {km['maxipm']} Newton steps on every cube up to n = 14", "Mehrotra's predictor-corrector"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from no guarantee to a fast guarantee")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx = (L, R) if i % 2 == 0 else (R, L)
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx, y, bw, rowh, [("THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="answered by", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    km, rnd, ell = d["km"], d["rand"], d["ell"]
    n14 = next(r for r in km["rows"] if r["n"] == 14)
    km_rows = [[str(r["n"]), r["piv"], r["ipm"]] for r in km["rows"]]
    rnd_rows = [[f"{r['n']} × {r['m']}", r["piv"], r["ipm"]] for r in rnd]
    ell_rows = [[r["side"], str(r["steps"]), r["bound"]] for r in ell["rows"]]
    big = rnd[-1]
    js_rows = [dict(side=r["side"], side_exact=repr(10 * 0.1 ** (k / 2)), steps=r["steps"]) for k, r in enumerate(ell["rows"])]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The simplex method (Era 4) was fast in practice, but Klee and Minty's cube showed it had no polynomial guarantee. Khachiyan took the ellipsoid method, built for other convex problems, and applied it to linear programs: the first polynomial bound. Karmarkar then went through the inside of the region instead of round its edges. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Khachiyan's step. Blue: where it led."),
        ]),
        dict(id="play", eyebrow="Try it", title="Cut the ellipse in half, again and again", toc="Try it", blocks=[
            dict(type="p", text="The ellipsoid method in two dimensions, exactly as the program runs it. The target is a small triangle near (37, −21); we start from a disc of radius 100 round the origin. If the centre of the current ellipse breaks one of the triangle's three constraints, that constraint's line through the centre cuts the ellipse in half, and the method draws the smallest ellipse round the good half. Pick a smaller triangle and count the cuts: the area shrinks by the same factor every time, so a target a hundred times smaller costs only a fixed number of extra cuts."),
            dict(type="widget", html=EL_HTML, js=EL_JS.replace("__ROWS__", json.dumps(js_rows)).replace("__RATIO__", ell["ratio"]), css=EL_CSS,
                 fallback=dict(type="table", head=["Triangle's side", "Cuts needed", "Bound from the area"], num=[1, 2], rows=ell_rows),
                 note="In the interactive edition you can make the cuts one at a time and watch the ellipse close in on the triangle."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Round the edges, or through the middle", toc="How it works", blocks=[
            dict(type="p", text="**The problem.** Find the largest value of c·x over the points x that satisfy linear inequalities. The allowed points form a polytope, and the best value is at a corner. The simplex method walks from corner to better corner along the edges."),
            dict(type="p", text="**Klee and Minty's cube.** A cube squashed so that, with the usual rule for choosing the next edge (the variable with the largest coefficient), the walk visits every one of the 2ⁿ corners. In three dimensions:"),
            dict(type="svg", name="cube", draw=cube_svg(d), alt="The simplex method's path round all eight corners of the Klee-Minty cube", width=760),
            dict(type="p", text=f"**The ellipsoid method.** Keep an ellipsoid that surely contains a solution. If its centre breaks a constraint, the constraint cuts the ellipsoid in half; draw the smallest ellipsoid round the good half. Its volume shrinks by a fixed factor each time ({ell['ratio']} of the area in the plane), so after a number of cuts that grows like a polynomial in the size of the input, the centre lands in the region or the region is shown empty. Optimizing reduces to repeated feasibility tests."),
            dict(type="p", text="**Interior points.** Karmarkar's method moves through the inside of the polytope, taking long steps that keep well away from the walls. The kind in this topic's program, primal-dual path-following, solves the program and its dual together: at the optimum each variable times its matching dual slack is zero, so each Newton step aims at points where all those products are equal and a little smaller, stopping just short of the walls."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A guarantee and a fast program are different things. The ellipsoid method settled that linear programming can be solved in polynomial time and was too slow to use; interior-point methods were the first to be both."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Pivots against Newton steps", toc="Measured", blocks=[
            dict(type="p", text=f"**On Klee and Minty's cube.** The simplex method with Dantzig's rule took exactly 2ⁿ − 1 pivots every time; the interior-point method never more than {km['maxipm']} iterations. Both reached the optimum 5ⁿ."),
            dict(type="table", head=["n", "Simplex pivots", "Interior-point iterations"], num=[0, 1, 2], rows=km_rows, hl=[len(km_rows) - 1]),
            dict(type="p", text=f"**On random programs.** With positive random coefficients, 5 programs of each size, the simplex method is fast too: {big['piv']} pivots on average at {big['n']} variables and {big['m']} constraints, against {big['ipm']} interior-point iterations (each much more expensive). The cube is a worst case, not the usual case."),
            dict(type="table", head=["Variables × constraints", "Simplex pivots (mean)", "Interior-point iterations (mean)"], num=[1, 2], rows=rnd_rows),
            dict(type="p", text=f"**The ellipsoid method in the plane.** Each cut shrank the area by the factor {ell['ratio']}, checked on every cut. Smaller targets took more cuts, never more than the number of shrinkings that would take the starting disc's area below the triangle's:"),
            dict(type="table", head=["Triangle's side", "Cuts", "Bound from the area"], num=[1, 2], rows=ell_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Four pages that made headlines", toc="The evidence", blocks=[
            dict(type="p", text="Leonid Khachiyan's result \"was first published in a four-page note, without proofs, in Soviet Mathematics Doklady in February 1979\", and presented in the West at the Montreal Mathematical Programming Symposium that August, with proofs in 1980 (SIAM News, 2005). The press reaction, which Eugene Lawler called \"The Great Mathematical Sputnik of 1979\", explained it \"with very spotty results\"; the Guardian's headline read \"Soviet Answer to the 'Traveling Salesmen'\", which it was not. The same appreciation notes that the method \"seems to require in practice a number of iterations close to its worst-case bound\", while the simplex method remains \"highly competitive with the more recent interior-point methods\"."),
            dict(type="p", text="Narendra Karmarkar, at AT&T Bell Laboratories, published \"A New Polynomial-Time Algorithm for Linear Programming\" in *Combinatorica* in 1984, with a bound of O(n³·⁵L²) against O(n⁶L²) for the ellipsoid algorithm. It was patented in 1988. A 1985 simplification, affine scaling, turned out to be \"an algorithm published by Soviet mathematician I. I. Dikin in 1967\" (Wikipedia). Today \"The class of primal-dual path-following interior-point methods is considered the most successful\", and \"Mehrotra's predictor–corrector algorithm provides the basis for most implementations\" (Wikipedia); the NEOS Guide says interior-point codes \"have proven to be competitive with, and often superior to, the best simplex packages\"."),
            dict(type="p", text="Klee and Minty's paper, \"How good is the simplex algorithm?\", is dated 1972 in Wikipedia's citation and 1973 in its text; the catalog marks the year **Disputed**."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The simplex method, still standing", toc="Full circle", blocks=[
            dict(type="p", text=f"Era 4 ended with Dantzig's simplex method solving linear programs that had been out of reach. Era 7 shows it can be made to take {n14['piv']} pivots on a cube of 14 dimensions, and finds methods with guarantees. Yet on the random programs above it needed only {big['piv']} pivots for {big['n']} variables, and the sources agree it stayed in use beside the interior-point methods."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="The fastest method in the worst case and the fastest method on the problems people bring are not always the same method. Solvers today offer both."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many corners does Klee and Minty's cube have in 20 dimensions, and how many pivots would Dantzig's rule take?", "2²⁰ = 1,048,576 corners; 2²⁰ − 1 = 1,048,575 pivots."),
            ("Each cut keeps the same fraction of the ellipse's area. Why does that make the number of cuts grow only slowly as the target shrinks?", "Making the target a hundred times smaller in area costs only the number of cuts needed to shrink the area another hundredfold: log(100) / log(1/0.7698), about 18 cuts in the plane."),
            ("Why did the ellipsoid method's polynomial bound not make it the method of choice?", "It needs close to its worst-case number of iterations in practice, and each is costly; the simplex method was usually much faster."),
            ("What does an interior-point method do at each step?", "It solves one linear system (a Newton step) and moves through the inside of the region, stopping short of the walls."),
            ("On which kind of problem would you expect the simplex method to beat an interior-point method?", "On many ordinary problems, such as the random ones here, where it needs few pivots, each far cheaper than an interior-point iteration."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Khachiyan's note in Doklady (1979)", text="Four pages, without proofs, in *Doklady Akademii Nauk SSSR*; the note itself was not opened for this book.",
                 draw=C.draw_manuscript, link="https://en.wikipedia.org/wiki/Leonid_Khachiyan", link_text="Khachiyan's life and the note (Wikipedia)", licence="Drawn placeholder."),
            dict(title="Karmarkar's paper (1984)", text="\"A New Polynomial-Time Algorithm for Linear Programming\", *Combinatorica* 4(4).",
                 draw=C.draw_manuscript, link="https://users.cs.utah.edu/~tch/notes/PSSAT/EAGER/Ishaan/A_New_Polynomial-Time_Algorithm_for_Linear_Program.pdf",
                 link_text="The paper (PDF, on a University of Utah page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LinearProgramming", d["checks"],
                           "Klee and Minty's cube for n = 1 to 14 (2ⁿ − 1 pivots, and the interior-point method reaching the same optimum), the path round the 3-dimensional cube, 25 random programs solved both ways, and the ellipsoid method's area factor on every cut.",
                           ["static double simplex(double[][] A, double[] b, double[] c)", "static double[][] newton("]),
    ]
    return dict(
        title="Linear Programming in Polynomial Time", date="1979–1984",
        description="Era 7, topic 1 of The Algorithm Evolution Atlas: Klee and Minty's cube, Khachiyan's ellipsoid method, Karmarkar's interior points, and the primal-dual methods solvers use today.",
        lede="The simplex method was fast on the problems people brought it, but a squashed cube could make it visit every corner. In 1979 a 26-year-old in Moscow showed that linear programs can be solved in polynomial time; five years later Karmarkar showed how to do it fast.",
        fieldnote=f"I watched the old method walk all {n14['piv']} edges of a cube of 14 dimensions, one corner at a time, while the new one went through the middle in {n14['ipm']} steps. Then I gave both a random problem, and the old method won. This species keeps both.",
        card=[("When", "Khachiyan 1979; Karmarkar 1984"),
              ("Where", "Moscow; AT&T Bell Laboratories"),
              ("What hurt", "No polynomial guarantee for linear programming"),
              ("The fix", "Ellipsoids, then interior points"),
              ("Checked", f"Cubes to n = 14: {n14['piv']} pivots against {n14['ipm']} Newton steps")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LinearProgramming.java`.",
    )
