"""Era 4, topic 11: the simplex method. Every number is parsed from SimplexMethod.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"plan: .*? Dantzig's rule walks (.+?) ; (\d+) pivots ; dual prices of the three limits \((.+?)\), .*? come to (\d+),", ln):
            d["plan"] = dict(path=[(a, b, v) for a, b, v in re.findall(r"\((\S+), (\S+)\) earning (\S+)", m.group(1))],
                             pivots=int(m.group(2)), y=m.group(3).split(", "), dual=m.group(4))
        elif m := re.match(r"random: (\d+) random programs .*? ; ([\d.]+) pivots on average, at most (\d+)$", ln):
            d["rand"] = dict(n=int(m.group(1)), avg=m.group(2), max=m.group(3))
        elif ln.startswith("grow: "):
            d["grow"] = re.findall(r"(\d+) x \d+: ([\d.]+) pivots", ln)
        elif ln.startswith("kleeminty: "):
            d["km"] = re.findall(r"(\d+): (\d+)", ln.split("for n = ")[1])
        elif m := re.match(r"assign: (\d+) people, .*? \(Bland's rule, (\d+) pivots\) assigns everyone at total cost (\d+) ; checking all (\d+) assignments .*? 70! = (\d+) assignments, a number of (\d+) digits$", ln):
            d["as"] = dict(n=int(m.group(1)), pivots=int(m.group(2)), cost=int(m.group(3)), all=int(m.group(4)), f70=m.group(5), digits=int(m.group(6)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def plan_svg(d):
    from fractions import Fraction
    path = [(float(Fraction(a)), float(Fraction(b))) for a, b, _ in d["plan"]["path"]]

    def draw(t, standalone):
        out, s, x0, y0 = [], 40, 60, 330
        X = lambda x: x0 + x * s
        Y = lambda y: y0 - y * s
        poly = [(0, 0), (4, 0), (4, 3), (2, 6), (0, 6)]                    # the corners of x <= 4, 2y <= 12, 3x + 2y <= 18
        out.append(C.path("M" + " L".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in poly) + " Z", t["ink2"], t["wash"], 1.5))
        out.append(C.line(X(0), Y(0), X(7), Y(0), t["axis"], 1.2))
        out.append(C.line(X(0), Y(0), X(0), Y(7.5), t["axis"], 1.2))
        out.append(C.text(X(7), Y(0) + 18, "x", t["muted"], 13, "end"))
        out.append(C.text(X(0) - 10, Y(7.5) + 4, "y", t["muted"], 13, "end"))
        for i in range(len(path) - 1):
            out.append(C.line(X(path[i][0]), Y(path[i][1]), X(path[i + 1][0]), Y(path[i + 1][1]), t["red"], 4))
        for (x, y), (_, _, v) in zip(path, d["plan"]["path"]):
            out.append(C.circle(X(x), Y(y), 6, t["red"]))
            out.append(C.text(X(x) + 10, Y(y) - 8, f"({x:g}, {y:g}): {v}", t["ink"], 13, "start", 700))
        R = 420
        out += [C.text(R, 60, "maximize 3x + 5y", t["ink"], 15, "start", 700),
                C.text(R, 86, "x ≤ 4,  2y ≤ 12,  3x + 2y ≤ 18,  x, y ≥ 0", t["muted"], 13),
                C.text(R, 126, "The grey region holds every allowed plan.", t["ink"], 13),
                C.text(R, 148, "The walk starts at the corner (0, 0) and moves", t["ink"], 13),
                C.text(R, 168, "to a better neighbouring corner while one exists.", t["ink"], 13),
                C.text(R, 206, f"{d['plan']['pivots']} pivots to the best plan, earning {d['plan']['path'][-1][2]}.", t["red"], 13.5, "start", 700),
                C.text(R, 230, f"Dual prices ({', '.join(d['plan']['y'])}) certify it:", t["blue"], 13),
                C.text(R, 250, f"4·0 + 12·3/2 + 18·1 = {d['plan']['dual']}.", t["blue"], 13)]
        return C.svg_doc(800, 360, "".join(out), "The simplex method walking the corners of a small production plan", t, standalone, 0.55, 800)
    return draw


SX_HTML = """
<div class="board sx-board">
  <div style="min-width:0">
    <svg id="sx-svg" viewBox="0 0 360 360" role="img" aria-label="The allowed region of a two-variable plan and the simplex walk over its corners"></svg>
  </div>
  <div style="min-width:0">
    <div class="presets" id="sx-pre"></div>
    <div class="controls"><label for="sx-c1">Value of x <input id="sx-c1" type="range" min="0" max="10" value="3"></label><span class="sx-v" id="sx-c1v"></span></div>
    <div class="controls"><label for="sx-c2">Value of y <input id="sx-c2" type="range" min="0" max="10" value="5"></label><span class="sx-v" id="sx-c2v"></span></div>
    <ol class="sx-steps" id="sx-steps"></ol>
    <p class="say" id="sx-say" aria-live="polite"></p>
  </div>
</div>
"""

SX_CSS = """
#sx-svg{width:100%;max-width:360px;height:auto}
.sx-board input[type=range]{width:min(160px,40vw)}
.sx-v{font-family:var(--mono);font-size:13px}
.sx-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.sx-steps .m{font-family:var(--mono);font-size:12.5px}
"""

SX_JS = r"""
(() => {
  const svg = document.getElementById("sx-svg");
  if (!svg) return;
  const P = {
    "Production plan": {A: [[1, 0], [0, 2], [3, 2]], b: [4, 12, 18], c: [3, 5], lim: 8},
    "Klee–Minty, two dimensions": {A: [[1, 0], [4, 1]], b: [5, 25], c: [2, 1], lim: 27},
  };
  let cur = P["Production plan"];
  function simplex(A, b, c) {                       // Dantzig's rule, recording the corners visited
    const m = A.length, n = 2, w = n + m + 1;
    const T = A.map((r, i) => [...r, ...Array.from({length: m}, (_, j) => (i === j ? 1 : 0)), b[i]]);
    T.push([...c.map(v => -v), ...Array(m).fill(0), 0]);
    const basis = A.map((_, i) => n + i);
    const corner = () => { const x = [0, 0]; basis.forEach((v, i) => { if (v < n) x[v] = T[i][w - 1]; }); return x; };
    const path = [corner()];
    for (let it = 0; it < 50; it++) {
      let e = -1; for (let j = 0; j < w - 1; j++) if (T[m][j] < -1e-12 && (e < 0 || T[m][j] < T[m][e])) e = j;
      if (e < 0) break;
      let l = -1; for (let i = 0; i < m; i++) if (T[i][e] > 1e-12 && (l < 0 || T[i][w - 1] / T[i][e] < T[l][w - 1] / T[l][e] - 1e-12)) l = i;
      if (l < 0) return {path, unbounded: true};
      const p = T[l][e]; T[l] = T[l].map(v => v / p);
      for (let i = 0; i <= m; i++) if (i !== l) { const f = T[i][e]; T[i] = T[i].map((v, j) => v - f * T[l][j]); }
      basis[l] = e; path.push(corner());
    }
    return {path, value: T[m][w - 1]};
  }
  function region(A, b, lim) {                      // corners of the allowed region, by intersecting boundary lines
    const lines = A.map((r, i) => [r[0], r[1], b[i]]).concat([[-1, 0, 0], [0, -1, 0]]);
    const pts = [];
    for (let i = 0; i < lines.length; i++) for (let j = i + 1; j < lines.length; j++) {
      const [a1, b1, c1] = lines[i], [a2, b2, c2] = lines[j], det = a1 * b2 - a2 * b1;
      if (Math.abs(det) < 1e-12) continue;
      const x = (c1 * b2 - c2 * b1) / det, y = (a1 * c2 - a2 * c1) / det;
      if (lines.every(([a, bb, cc]) => a * x + bb * y <= cc + 1e-9)) pts.push([x, y]);
    }
    const cx = pts.reduce((s, p) => s + p[0], 0) / pts.length, cy = pts.reduce((s, p) => s + p[1], 0) / pts.length;
    return pts.sort((p, q) => Math.atan2(p[1] - cy, p[0] - cx) - Math.atan2(q[1] - cy, q[0] - cx));
  }
  function show() {
    const c = [+document.getElementById("sx-c1").value, +document.getElementById("sx-c2").value];
    document.getElementById("sx-c1v").textContent = c[0]; document.getElementById("sx-c2v").textContent = c[1];
    const S = 300 / cur.lim, X = x => 40 + x * S, Y = y => 330 - y * S;
    svg.innerHTML = "";
    sv("line", {x1: X(0), y1: Y(0), x2: 350, y2: Y(0), stroke: "var(--axis)"}, svg);
    sv("line", {x1: X(0), y1: Y(0), x2: X(0), y2: 10, stroke: "var(--axis)"}, svg);
    const reg = region(cur.A, cur.b, cur.lim);
    sv("path", {d: "M" + reg.map(p => X(p[0]).toFixed(1) + "," + Y(p[1]).toFixed(1)).join(" L") + " Z", fill: "var(--wash)", stroke: "var(--ink-2)", "stroke-width": 1.5}, svg);
    const r = simplex(cur.A, cur.b, c);
    for (let i = 0; i + 1 < r.path.length; i++) sv("line", {x1: X(r.path[i][0]), y1: Y(r.path[i][1]), x2: X(r.path[i + 1][0]), y2: Y(r.path[i + 1][1]), stroke: "var(--red)", "stroke-width": 4}, svg);
    r.path.forEach((p, i) => { sv("circle", {cx: X(p[0]), cy: Y(p[1]), r: 6, fill: "var(--red)"}, svg); sv("text", {x: X(p[0]) + 8, y: Y(p[1]) - 8, "font-size": 12, fill: "var(--ink)"}, svg, String(i)); });
    const ol = document.getElementById("sx-steps"); ol.innerHTML = "";
    r.path.forEach((p, i) => { el("li", {}, ol).innerHTML = `corner <span class="m">(${+p[0].toFixed(3)}, ${+p[1].toFixed(3)})</span> earns ${+(c[0] * p[0] + c[1] * p[1]).toFixed(3)}`; });
    document.getElementById("sx-say").textContent = `${r.path.length - 1} pivot${r.path.length === 2 ? "" : "s"}, ${r.path.length} corner${r.path.length > 1 ? "s" : ""} visited out of ${reg.length}. ` +
      (cur === P["Klee–Minty, two dimensions"] && r.path.length === reg.length ? "Dantzig's rule visits every corner: the Klee–Minty trap." : "Each step moves to a better neighbouring corner; none is better at the last.");
  }
  const pre = document.getElementById("sx-pre");
  Object.keys(P).forEach(k => { const b = el("button", {type: "button"}, pre, k); b.addEventListener("click", () => { cur = P[k]; document.getElementById("sx-c1").value = cur.c[0]; document.getElementById("sx-c2").value = cur.c[1]; show(); }); });
  ["sx-c1", "sx-c2"].forEach(id => document.getElementById(id).addEventListener("input", show));
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the simplex method combined older ideas, and where it led")
    W = 210
    nodes = {
        "elim": (20, 20, "Elimination", "solve linear equations step by step", "Era 2 topic 1", "ink"),
        "ineq": (395, 20, "Linear inequalities", "Fourier's method, 1827", "Fourier", "ink"),
        "plan": (770, 20, "Planning by rules", "Air Force programmes; Kantorovich, Koopmans", "1930s–1946", "ink"),
        "sx": (395, 170, "The simplex method", "⊕ walk the corners, pivot by elimination", "Dantzig, 1947", "red"),
        "dual": (20, 330, "Duality", "every plan has a pricing twin", "von Neumann, 1947", "ink"),
        "km": (395, 330, "The worst case", "Klee–Minty: every corner visited", "1972", "ink"),
        "poly": (770, 330, "Polynomial methods", "ellipsoid 1979; interior points 1984", "Khachiyan; Karmarkar", "ink"),
        "today": (395, 480, "Optimization today", "airlines, supply chains, power grids", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("elim", "sx", ports=("bottom", "top:0.15"))
    D.edge("ineq", "sx", ports=("bottom", "top"))
    D.edge("plan", "sx", ports=("bottom", "top:0.85"))
    D.edge("sx", "dual", ports=("bottom:0.1", "top:0.7"))
    D.edge("sx", "km", ports=("bottom", "top"))
    D.edge("km", "poly", ports=("right", "left"), dashed=True)
    D.edge("km", "today", ports=("bottom", "top"))
    D.edge("poly", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: the polynomial-time methods answered the theoretical worst case; in practice the simplex method remains in use.", "caption")
    return D


def chain(d):
    a, km = d["as"], d["km"]
    steps = [
        ("Air Force plans: hundreds of interacting limits, worked out by rules of thumb",
         "Write the limits as linear inequalities and the goal as a linear quantity", "Dantzig, 1947"),
        (f"Too many possible plans: assigning 70 people to 70 jobs has 70!, a {a['digits']}-digit number",
         "Walk from corner to better corner of the allowed region (pivots)", "the simplex method, 1947"),
        ("How do you know the last corner is the best?",
         f"The dual's prices certify it: here both come to {d['plan']['dual']}", "von Neumann's duality, 1947"),
        (f"On the Klee–Minty cubes the walk visits every corner: {km[-1][1]} pivots in 10 dimensions",
         "Methods with a polynomial bound; the simplex method stays in use", "1979, 1984"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from rules of thumb to linear programming")
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
    pl, rd, gr, km, a = d["plan"], d["rand"], d["grow"], d["km"], d["as"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Elimination for linear equations is two thousand years old (Era 2, topic 1); Fourier had studied systems of linear inequalities in 1827; in the late 1930s Kantorovich and Koopmans wrote economic problems in that form. Dantzig's addition, in 1947, was a goal to maximize and a way to reach it: walk from corner to corner of the allowed region, each step a round of elimination. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Dantzig's simplex method. Blue: optimization today."),
        ]),
        dict(id="walk", eyebrow="Try it", title="Walk the corners", toc="Try it", blocks=[
            dict(type="p", text="The grey region holds every plan that obeys the limits. Change what x and y are worth, and the walk (red) starts again from (0, 0), moving each time to the neighbouring corner that gains fastest, as Dantzig's rule does. Then choose the two-dimensional Klee–Minty plan: the walk visits every corner before it reaches the best one."),
            dict(type="widget", html=SX_HTML, js=SX_JS, css=SX_CSS,
                 fallback=dict(type="svg", name="plan", draw=plan_svg(d), alt="The simplex method walking the corners of a small production plan", width=800),
                 note="In the interactive edition you can change the objective and watch the walk change."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Corners, pivots and prices", toc="How it works", blocks=[
            dict(type="p", text=f"**A small plan.** Maximize 3x + 5y with x ≤ 4, 2y ≤ 12, 3x + 2y ≤ 18 and x, y ≥ 0. The allowed plans form a five-sided region, and the best plan is at a corner. Starting from (0, 0), Dantzig's rule raises the variable that gains most per unit (y), as far as the limits allow, and then asks again: {' → '.join(f'({x}, {y}) earning {v}' for x, y, v in pl['path'])}. That is {pl['pivots']} pivots; no neighbour of (2, 6) is better."),
            dict(type="p", text=f"**Pivots.** In table form, the plan's limits get one extra \"slack\" variable each, and a corner is a choice of which variables may be non-zero. A pivot swaps one in and one out, and rewrites the table by elimination, exactly as in solving equations. **Prices.** The final table also gives the dual: a price for each limit such that every activity is priced at least at its value. Here the prices are ({', '.join(pl['y'])}); the limits 4, 12 and 18 priced at them come to {pl['dual']}, the best plan's value, which proves that no plan does better."),
            dict(type="p", text=f"**Checked.** On {rd['n']:,} random small programs the program compares the simplex answer, in exact fractions, with the best of every corner found by brute force, runs Bland's rule as well, and checks the dual: every answer agreed, and the dual's value matched every time. They took {rd['avg']} pivots on average and at most {rd['max']}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="The best plan sits at a corner, and from any corner that is not best there is a better neighbour. So walk uphill from corner to corner. The number of corners grows explosively, but on practical problems the walk is short, and the dual prices prove the answer."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Short walks, and one very long one", toc="Measured", blocks=[
            dict(type="table", head=["Random dense program (variables × limits)", "Average pivots, Dantzig's rule"], num=[1],
                 rows=[[f"{s} × {s}", p] for s, p in gr]),
            dict(type="p", text="On random problems the number of pivots grows roughly in proportion to the size, not explosively. The Klee–Minty cubes (1972) are built to defeat Dantzig's rule: a cube squashed so that the walk visits every one of its 2ⁿ corners."),
            dict(type="table", head=["Dimension n", "Pivots on the Klee–Minty cube"], num=[0, 1], rows=[[n, p] for n, p in km]),
            dict(type="p", text=f"**Assignment.** Dantzig's own illustration was assigning 70 people to 70 jobs: 70! = {a['f70'][:12]}… possible assignments, a number of {a['digits']} digits. The program does it for {a['n']} people with random costs: Bland's rule needs {a['pivots']} pivots and assigns everyone at a total cost of {a['cost']}, and checking all {a['all']:,} assignments finds the same minimum. The simplex answer comes out in whole numbers by itself."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="The Pentagon, 1947", toc="The evidence", blocks=[
            dict(type="p", text="Dantzig completed his PhD at Berkeley in 1946 and became mathematical adviser to the comptroller of the U.S. Air Force, where \"in 1947 ... the linear programming problem and the simplex method took shape\" (Cottle, NAS memoir). A colleague had challenged him \"to mechanize the planning process\"; the name simplex was suggested by T. S. Motzkin (Wikipedia). In his own account the method's efficiency came from \"viewing the problem in the geometry of the columns rather than the rows\"; in the fall of 1947 he visited von Neumann and had the Bureau of Standards test the method on Stigler's diet problem (Dantzig, 1987)."),
            dict(type="p", text="Von Neumann \"immediately conjectured the theory of duality\"; Kantorovich and Koopmans shared the 1975 Nobel Memorial Prize in Economic Sciences; Khachiyan (1979) and Karmarkar (1984) gave polynomial-time methods (Wikipedia, Linear programming). Stigler's own diet cost $39.93 a year in 1939 prices; the exact minimum is $39.69 (Wikipedia, Stigler diet)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Planning, still by pivots", toc="Full circle", blocks=[
            dict(type="p", text="Airline crews, refinery blends, delivery routes and electricity markets are planned by linear programs with thousands or millions of variables. Interior-point methods, descendants of Karmarkar's, now share the work, but the simplex method, with better pivoting rules, is still one of the two standard ways to solve them."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Ten people, {a['all']:,} possible assignments; the simplex method found the cheapest in {a['pivots']} pivots. For seventy people the possibilities run to {a['digits']} digits, and the walk is still short."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why must a best plan sit at a corner?", "The value is linear: along any line through the region it rises in one direction, so from a non-corner point you can slide along an edge or face without losing value until you hit a corner."),
            ("In the small plan, why does Dantzig's rule raise y first?", "y earns 5 per unit, x only 3: the rule picks the larger gain per unit."),
            ("How far can y rise from (0, 0)?", "Until a limit stops it: 2y ≤ 12 allows 6, and 3x + 2y ≤ 18 allows 9, so y stops at 6."),
            ("Check the dual prices: why do 0, 3/2 and 1 prove that 36 is best?", "Any allowed plan has 3x + 5y ≤ 0·x + (3/2)(2y) + 1·(3x + 2y) ≤ 0·4 + (3/2)·12 + 1·18 = 36."),
            ("How many pivots does Dantzig's rule take on the 10-dimensional Klee–Minty cube?", f"2¹⁰ − 1 = {km[-1][1]}: it visits every corner."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Origins of the Simplex Method (1987)", text="Dantzig's own account of 1947, as a Stanford technical report.",
                 draw=C.draw_manuscript, link="https://apps.dtic.mil/sti/pdfs/ADA182708.pdf", link_text="DTIC", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "SimplexMethod", d["checks"],
                           f"the small plan and its dual, {rd['n']:,} random programs against brute force and duality, Dantzig's rule against Bland's, the Klee–Minty cubes up to 10 dimensions, and the 10-person assignment against all {a['all']:,} possibilities.",
                           ["static Result simplex("]),
    ]
    return dict(
        title="The Simplex Method", date="1947",
        description="Era 4, topic 11 of The Algorithm Evolution Atlas: Dantzig's simplex method for linear programming, duality, and the Klee–Minty worst case.",
        lede="Dantzig wrote the Air Force's planning rules as linear inequalities and its goal as a linear quantity to maximize. The best plan sits at a corner of the region the rules allow; his method walks from corner to better corner until no neighbour is better.",
        fieldnote=f"There are {a['all']:,} ways to give ten people ten jobs, and the walk found the cheapest in {a['pivots']} steps. For seventy people the number of ways has {a['digits']} digits; the walk is still short. Nobody could say why for twenty-five years, and then someone built a solid on which it is not.",
        card=[("When", "1947"),
              ("Where", "The Pentagon (U.S. Air Force)"),
              ("What hurt", "Plans with astronomically many options"),
              ("The fix", "Linear programming; walk the corners by pivots"),
              ("Cost", f"Usually a few pivots per limit; 2ⁿ − 1 on Klee–Minty")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `SimplexMethod.java`.",
    )
