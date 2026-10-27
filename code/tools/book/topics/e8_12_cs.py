"""Era 8, topic 12: Compressed sensing. Every number is parsed from CompressedSensing.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("one: "):
            m = re.search(r"N = (\d+), k = (\d+) nonzero entries, m = (\d+) random Gaussian measurements ; l1 minimization: (\d+) interior-point iterations, duality gap (\S+), largest error (\S+) ; smallest sum of squares: largest error (\S+), (\d+) of the (\d+) entries above 0.01 in size ; position:true:l1:squares (.*)$", ln)
            d["one"] = dict(N=m.group(1), k=m.group(2), m=m.group(3), it=m.group(4), gap=m.group(5), err=m.group(6), err2=m.group(7), above=m.group(8), of=m.group(9),
                            rows=[e.split(":") for e in m.group(10).split()])
        elif ln.startswith("transition: "):
            d["ks"] = [int(v) for v in re.search(r"k = \[([\d,]+)\]", ln).group(1).split(",")]
            d["trials"] = re.search(r"out of (\d+)", ln).group(1)
            d["grid"] = [(int(m), [int(v) for v in vs.split(",")]) for m, vs in re.findall(r"m = (\d+): ([\d,]+)", ln)]
            d["l2"] = re.search(r"the smallest-squares solution: (\d+) of (\d+)", ln).groups()
        elif ln.startswith("widget: "):
            head = re.search(r"N = (\d+), k = (\d+) ; signal ([-\d.,]+) ;", ln)
            d["wN"], d["wk"] = int(head.group(1)), int(head.group(2))
            d["signal"] = [float(v) for v in head.group(3).split(",")]
            d["wm"] = [dict(m=int(m), ok=ok == "exact", l1=[float(v) for v in a.split(",")], l2=[float(v) for v in b.split(",")])
                       for m, ok, a, b in re.findall(r"m=(\d+) (exact|wrong) l1=([-\d.,]+) squares=([-\d.,]+)", ln)]
            d["wrows"] = re.search(r"the first m rows of one (\d+)-by-(\d+) Gaussian matrix", ln).groups()
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def diamond_svg(d):
    """Pure geometry: the line x1 + 2.5 x2 = 2 meets the smallest l1 diamond at a corner and the smallest circle off the axes."""
    a1, a2, y = 1.0, 2.5, 2.0
    corner = y / a2                                    # the l1 solution: (0, 0.8)
    n2 = a1 * a1 + a2 * a2
    p = (a1 * y / n2, a2 * y / n2)                     # the least-squares solution: the foot of the perpendicular
    rad = math.hypot(*p)

    def draw(t, standalone):
        W, H = 760, 400
        o = []
        panels = [(20, "smallest |x₁| + |x₂|", "l1"), (400, "smallest x₁² + x₂²", "l2")]
        for px, title, kind in panels:
            cx, cy, sc = px + 170, 200, 150
            X = lambda v: cx + v * sc
            Y = lambda v: cy - v * sc
            o.append(C.text(px + 10, 26, title, t["ink"], 14, "start", 700))
            o.append(C.line(X(-1.1), Y(0), X(1.15), Y(0), t["axis"], 1.2))
            o.append(C.line(X(0), Y(-0.9), X(0), Y(1.15), t["axis"], 1.2))
            o.append(C.text(X(1.15), Y(0) + 16, "x₁", t["muted"], 12, "end"))
            o.append(C.text(X(0) + 8, Y(1.12), "x₂", t["muted"], 12))
            # every solution of x1 + 2.5 x2 = 2
            x0, x1 = 2 - a2 * 1.1, 1.15
            o.append(C.line(X(x0), Y((y - a1 * x0) / a2), X(x1), Y((y - a1 * x1) / a2), t["red"], 2.2))
            if kind == "l1":
                r = corner
                pts = f"M{X(r):.1f},{Y(0):.1f} L{X(0):.1f},{Y(r):.1f} L{X(-r):.1f},{Y(0):.1f} L{X(0):.1f},{Y(-r):.1f} Z"
                o.append(C.path(pts, t["blue"], t["blue"], 1.8, ";fill-opacity:0.15"))
                o.append(C.circle(X(0), Y(r), 6, t["ink"], t["ink"], 1))
                o.append(C.text(X(0) + 12, Y(r) - 10, f"({0:.2f}, {r:.2f}): x₁ is exactly 0", t["ink"], 12.5, "start", 700))
            else:
                o.append(f'<circle cx="{X(0):.1f}" cy="{Y(0):.1f}" r="{rad * sc:.1f}" style="fill:{t["blue"]};fill-opacity:0.15;stroke:{t["blue"]};stroke-width:1.8"/>')
                o.append(C.circle(X(p[0]), Y(p[1]), 6, t["ink"], t["ink"], 1))
                o.append(C.text(X(p[0]) - 45, Y(p[1]) + 52, f"({p[0]:.2f}, {p[1]:.2f}): both non-zero", t["ink"], 12.5, "middle", 700))
        o.append(C.text(20, 372, "Red: every (x₁, x₂) with x₁ + 2.5 x₂ = 2, one measurement of two unknowns. Blue: the smallest shape that touches it.", t["ink"], 12.5))
        o.append(C.text(20, 392, "A diamond's corners lie on the axes, so it usually touches first at a corner, where a number is zero.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "The smallest l1 diamond touches the line of solutions at a corner; the smallest circle does not", t, standalone, 0.5, 760)
    return draw


def transition_svg(d):
    def draw(t, standalone):
        ks, grid, trials = d["ks"], d["grid"], int(d["trials"])
        cw, ch, L, top = 70, 34, 120, 56
        W, H = L + cw * len(ks) + 30, top + ch * len(grid) + 70
        o = [C.text(20, 24, f"Signals recovered exactly by l1 minimization, out of {trials} (N = 128)", t["ink"], 13.5, "start", 700),
             C.text(L - 10, top - 10, "m", t["muted"], 12, "end", 700)]
        for j, k in enumerate(ks):
            o.append(C.text(L + j * cw + cw / 2, top + ch * len(grid) + 18, str(k), t["muted"], 12, "middle"))
        o.append(C.text(L + cw * len(ks) / 2, top + ch * len(grid) + 38, "k, the number of non-zero entries", t["muted"], 12, "middle"))
        for i, (m, vals) in enumerate(grid):
            y = top + i * ch
            o.append(C.text(L - 10, y + ch / 2 + 4, str(m), t["muted"], 12, "end"))
            for j, v in enumerate(vals):
                f = v / trials
                o.append(C.rect(L + j * cw + 1, y + 1, cw - 2, ch - 2, t["blue"], t["axis"], 0.6, 0, f";fill-opacity:{0.08 + 0.92 * f:.2f}"))
                o.append(C.text(L + j * cw + cw / 2, y + ch / 2 + 5, str(v), t["on_blue"] if f >= 0.6 else t["ink"], 13, "middle", 700 if v == trials else 400))
        o.append(C.text(20, H - 10, f"The smallest-squares solution recovered {d['l2'][0]} of the {d['l2'][1]} signals.", t["ink"], 12.5))
        return C.svg_doc(W, H, "".join(o), "A grid of recovery counts: many measurements and few non-zero entries always succeed", t, standalone, 0.5, W)
    return draw


CS_HTML = """
<div class="board cs-board">
  <div style="min-width:0">
    <div class="controls"><label>measurements m <input id="cs-m" type="range" min="0" max="__LAST__" step="1" value="0"></label><output id="cs-mv"></output></div>
    <div id="cs-plots"></div>
  </div>
  <div style="min-width:0">
    <p class="say" id="cs-say" aria-live="polite"></p>
  </div>
</div>
"""

CS_CSS = """
.cs-board .controls{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:8px}
.cs-board input[type=range]{width:14em;padding:0}
.cs-board output{font:600 15px var(--mono)}
.cs-board .plot-t{font-size:12.5px;color:var(--muted);margin:8px 0 2px}
.cs-board .plot-t b{color:var(--ink)}
"""

CS_JS = r"""
(() => {
  const inp = document.getElementById("cs-m");
  if (!inp) return;
  const X = __SIGNAL__, RUNS = __RUNS__, N = X.length;
  const plots = document.getElementById("cs-plots");
  function stems(title, v, color, ref) {
    el("p", {class: "plot-t"}, plots).innerHTML = title;
    const W = 640, H = 120, mid = 60, sc = 26, dx = (W - 20) / N;
    const svg = sv("svg", {viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": title.replace(/<[^>]+>/g, "")}, plots);
    sv("line", {x1: 10, y1: mid, x2: W - 10, y2: mid, stroke: "var(--axis)", "stroke-width": 1}, svg);
    v.forEach((a, i) => {
      const x = 10 + dx * (i + 0.5);
      if (ref && ref[i] !== 0) sv("circle", {cx: x, cy: mid - ref[i] * sc, r: 7, fill: "none", stroke: "var(--muted)", "stroke-width": 1.2, "stroke-dasharray": "2 2"}, svg);
      if (a === 0) { sv("circle", {cx: x, cy: mid, r: 1.6, fill: "var(--muted)"}, svg); return; }
      sv("line", {x1: x, y1: mid, x2: x, y2: mid - a * sc, stroke: color, "stroke-width": 2.4}, svg);
      sv("circle", {cx: x, cy: mid - a * sc, r: 3.6, fill: color}, svg);
    });
  }
  const nz = v => v.filter(a => a !== 0).length;
  function run() {
    const r = RUNS[+inp.value];
    document.getElementById("cs-mv").textContent = r.m;
    plots.innerHTML = "";
    stems(`<b>The signal</b>: ${N} numbers, ${nz(X)} of them not zero`, X, "var(--ink)");
    stems(`<b>Smallest sum of absolute values</b> (l1): ${r.ok ? "exactly the signal" : "wrong"}`, r.l1, r.ok ? "var(--blue)" : "var(--red)", X);
    stems(`<b>Smallest sum of squares</b>: wrong, ${nz(r.l2)} of ${N} entries non-zero to two decimals`, r.l2, "var(--red)", X);
    document.getElementById("cs-say").textContent = `m = ${r.m}: ${r.m} measurements, each a random mix of all ${N} numbers, so ${r.m} equations for ${N} unknowns. ` +
      (r.ok ? `The l1 solution is the signal itself, to two decimals in every position. ` : `The l1 solution fits all ${r.m} measurements but is not the signal: too few for k = ${nz(X)}. `) +
      `The smallest-squares solution also fits them, spread over ${nz(r.l2)} positions. Dashed rings mark where the signal's non-zero entries are.`;
  }
  inp.addEventListener("input", run);
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How compressed sensing combined older ideas, and where it led")
    W = 210
    nodes = {
        "nyq": (20, 20, "The sampling theorem", "how often to measure to capture a signal", "Nyquist and Shannon", "ink"),
        "l1": (395, 20, "ℓ1 minimization", "seismology 1970s, LASSO 1996, basis pursuit 1998", "", "ink"),
        "lp": (770, 20, "Linear programming", "interior-point methods", "Era 7, topic 1", "ink"),
        "cs": (395, 180, "Compressed sensing", "⊕ random measurements", "Candès, Romberg, Tao, 2004", "red"),
        "mri": (20, 340, "Faster MRI", "shorter scans", "", "ink"),
        "pix": (770, 340, "Single-pixel camera", "Rice University", "", "ink"),
        "next": (395, 490, "Could change", "conversion, optics, MRI, seismics", "Candès, Stanford talk, 2010", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("nyq", "cs", ports=("bottom", "top:0.15"), label="far fewer samples", at=0.45, dy=-6, anchor="start", dx=6)
    D.edge("l1", "cs", ports=("bottom", "top"))
    D.edge("lp", "cs", ports=("bottom", "top:0.85"))
    D.edge("cs", "mri", ports=("bottom:0.15", "top"))
    D.edge("cs", "pix", ports=("bottom:0.85", "top"))
    D.edge("cs", "next", ports=("bottom", "top"))
    D.text(20, 615, "Wikipedia: \"far fewer samples than required by the Nyquist–Shannon sampling theorem\".", "caption")
    return D


def chain(d):
    one = d["one"]
    steps = [
        ("The sampling theorem's rate ignores that most of a sparse signal is zero",
         "Measure less: m random mixes of all N numbers", "\"far fewer samples\" (Wikipedia)"),
        (f"Fewer equations than unknowns: infinitely many solutions; the smallest-squares one is wrong ({one['above']} of {one['of']} entries non-zero)",
         "Take the solution with the smallest sum of absolute values", "Candès, Romberg and Tao, 2004"),
        ("Too few measurements for the number of non-zero entries, and ℓ1 fails too",
         "Enough is about k log N: a proved threshold", "the phase transition, measured below"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from measuring everything to measuring enough")
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
    one, grid, ks, wm = d["one"], d["grid"], d["ks"], d["wm"]
    first_ok = next(r["m"] for r in wm if r["ok"])
    last_bad = max(r["m"] for r in wm if not r["ok"])
    one_rows = [[p, a, b, c] for p, a, b, c in one["rows"]]
    wfall = [[str(r["m"]), "exact" if r["ok"] else "wrong", str(sum(1 for v in r["l2"] if v != 0))] for r in wm]
    m40 = dict(grid)[40]
    g16 = grid[0][0]
    assert dict(grid)[g16][ks.index(6)] == 0 and m40[ks.index(6)] == int(d["trials"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The sampling theorem said how often to measure a signal. Minimizing a sum of absolute values had been used in seismology since the 1970s, and in the LASSO and basis pursuit in the 1990s. Linear programming (Era 7) could do the minimizing. Candès, Romberg and Tao added random measurements and a proof that, for sparse signals, far fewer of them are enough. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: compressed sensing. Blue: what Candès said it could change."),
        ]),
        dict(id="play", eyebrow="Try it", title="Recover a signal from too few measurements", toc="Try it", blocks=[
            dict(type="p", text=f"A signal of {d['wN']} numbers, {d['wk']} of them not zero. Slide the number of measurements m, from {wm[0]['m']} to {wm[-1]['m']}: each measurement is a random mix of all {d['wN']} numbers, the first m rows of one {d['wrows'][0]}-by-{d['wrows'][1]} random matrix. Every reconstruction shown fits all m measurements. They are the program's own solutions."),
            dict(type="widget", html=CS_HTML.replace("__LAST__", str(len(wm) - 1)), js=CS_JS.replace("__SIGNAL__", json.dumps(d["signal"])).replace("__RUNS__", json.dumps(wm)), css=CS_CSS,
                 fallback=dict(type="table", head=["m", "ℓ1", "Smallest squares: non-zero entries"], num=[0, 2], rows=wfall),
                 note="In the interactive edition you can slide m and watch the two reconstructions."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="The diamond and the circle", toc="How it works", blocks=[
            dict(type="p", text="**The setting.** A signal x has N numbers, only k of them not zero, and we do not know which. Each measurement is a fixed random combination of all N numbers, so m measurements give m equations y = A x. With m smaller than N there are infinitely many solutions."),
            dict(type="p", text="**Which solution?** The usual choice, the one with the smallest sum of squares, spreads the signal thinly over every position. The one with the smallest sum of absolute values, the ℓ1 norm, picks out sparse solutions. In two dimensions you can see why:"),
            dict(type="svg", name="diamond", draw=diamond_svg(d), alt="The smallest l1 diamond touches the line of solutions at a corner; the smallest circle does not", width=760),
            dict(type="p", text="**The theorem.** Candès, Romberg and Tao proved that with high probability the ℓ1 solution is exactly the sparse signal, once the number of measurements is a modest multiple of k log N. **The computation.** Minimizing |x₁| + … + |x_N| subject to A x = y is a linear program: write x = u − v with u and v not negative, and minimize the sum of all their entries. The program solves it with an interior-point method, as in Era 7."),
            dict(type="callout", kind="key", label="Key idea",
                 text="When most of a signal is zero, measure random mixtures of it and ask for the simplest explanation, in the sense of the smallest sum of absolute values. The proof is about random measurements."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Where ℓ1 succeeds, and where it stops", toc="Measured", blocks=[
            dict(type="p", text=f"**One signal**: N = {one['N']}, k = {one['k']} non-zero entries, m = {one['m']} random measurements. ℓ1 minimization took {one['it']} interior-point iterations (duality gap {one['gap']}) and recovered the signal with largest error {one['err']}. The smallest-squares solution had largest error {one['err2']}, with {one['above']} of the {one['of']} entries above 0.01 in size. The five non-zero positions:"),
            dict(type="table", head=["Position", "True value", "ℓ1 solution", "Smallest squares"], num=[0, 1, 2, 3], rows=one_rows),
            dict(type="p", text=f"**The phase transition**: for each m and k, {d['trials']} random signals and matrices. With m = 40 measurements, ℓ1 recovered every signal up to k = {max(k for k, v in zip(ks, m40) if v == int(d['trials']))} and {m40[-1]} of {d['trials']} at k = {ks[-1]}."),
            dict(type="svg", name="transition", draw=transition_svg(d), alt="Recovery counts for each number of measurements and non-zero entries", width=760),
            dict(type="p", text=f"In the widget's small signal (N = {d['wN']}, k = {d['wk']}), ℓ1 was wrong up to m = {last_bad} and exact from m = {first_ok}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Caltech and UCLA, June 2004", toc="The evidence", blocks=[
            dict(type="p", text="Candès and Romberg (Caltech) and Tao (UCLA), preprint dated 10 June 2004: \"exact recovery may be obtained by solving a convex optimization problem\", minimizing the ℓ1 norm subject to the observed Fourier coefficients; recovery holds with probability at least 1 − O(N^−M) when the number of non-zero entries is below about |Ω|/(29.6(M + 1) log N); the Logan–Shepp phantom, with \"512 samples along each of 22 radial lines\", is recovered exactly. Published in *IEEE Transactions on Information Theory* 52(2), 489–509, February 2006."),
            dict(type="p", text="Wikipedia: compressed sensing recovers signals from \"far fewer samples than required by the Nyquist–Shannon sampling theorem\"; \"around 2004\" Candès, Romberg, Tao and Donoho showed this; earlier ℓ1 work includes seismology in the 1970s, matching pursuit (1993), the LASSO (1996) and basis pursuit (1998); it speeds up MRI and made single-pixel cameras possible. MAA's summary of Jordan Ellenberg's *Wired* article (2010): Candès found the effect by chance in 2004, using ℓ1 minimization on a blurry image, with a result \"remarkably clear\". The abstract of Candès's Stanford talk of 20 October 2010: the theory could change analog-to-digital conversion, digital optics, MRI and seismics."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A linear program, again", toc="Full circle", blocks=[
            dict(type="p", text="Era 7's interior-point methods were invented to solve linear programs in polynomial time. Here the same method finds a sparse signal: the absolute values become a linear program once each number is split into a positive and a negative part. And where AKS (topic 10) removed randomness from primality testing, compressed sensing puts it in on purpose: the measurements are random."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"With m = {one['m']} measurements of {one['N']} numbers, the linear program recovered all {one['k']} non-zero entries with largest error {one['err']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With one equation x₁ + x₂ = 2, which solution has the smallest x₁² + x₂²? The smallest |x₁| + |x₂|?", "Smallest squares: (1, 1), not sparse. Smallest absolute values: every point from (2, 0) to (0, 2) ties at 2, including the two sparse corners."),
            ("Why does the smallest-squares solution spread the signal over every position?", "Squares punish large entries far more than small ones, so it prefers many small numbers to a few large ones."),
            ("Why must the measurements mix all N numbers, rather than read N/4 of them directly?", "Reading a few entries directly would miss the non-zero ones; a random mix records a little of every entry."),
            ("How is minimizing |x₁| + … + |x_N| a linear program?", "Write each xᵢ = uᵢ − vᵢ with uᵢ, vᵢ ≥ 0 and minimize the sum of all u and v, subject to A(u − v) = y."),
            (f"In the grid, why does recovery fail at m = {g16} for k = 6 but succeed at m = 40?", f"The theorem needs a modest multiple of k log N measurements; {g16} is too few for 6 non-zero entries out of 128."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Robust uncertainty principles (preprint, 2004)", text="The theorem and the 22-line phantom.",
                 draw=C.draw_manuscript, link="https://arxiv.org/pdf/math/0409186", link_text="The preprint (arXiv)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "CompressedSensing", d["checks"],
                           "that every solution fits its measurements, that ℓ1 minimization recovers the sparse signal where the smallest-squares solution never does, and where the recovery stops.",
                           ["static double[] basisPursuit(double[][] A, double[] y)"]),
    ]
    return dict(
        title="Compressed Sensing", date="2004–2006",
        description="Era 8, topic 12 of The Algorithm Evolution Atlas: Candès, Romberg and Tao's compressed sensing (2004), recovering sparse signals from few random measurements by ℓ1 minimization.",
        lede="The sampling theorem told the species how often to measure a signal. In 2004 Candès, Romberg and Tao proved that a sparse signal, mostly zeros, can be recovered exactly from far fewer random measurements, by asking for the solution with the smallest sum of absolute values.",
        fieldnote=f"I hid {one['k']} numbers among {one['N']} and took only {one['m']} random measurements. The answer with the smallest sum of squares was spread over {one['above']} of the {one['of']} positions and right in none of them. The answer with the smallest sum of absolute values was right everywhere, to {one['err']}.",
        card=[("When", "Preprint 10 June 2004; journal 2006"),
              ("Where", "Caltech and UCLA"),
              ("What hurt", "Fewer equations than unknowns: infinitely many solutions"),
              ("The fix", "Random measurements; minimize the sum of absolute values"),
              ("Checked", f"Recovery counts for {len(grid) * len(ks) * int(d['trials'])} random signals")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `CompressedSensing.java`.",
    )
