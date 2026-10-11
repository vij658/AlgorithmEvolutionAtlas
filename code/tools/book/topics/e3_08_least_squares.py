"""Era 3, topic 8: least squares, and the lost planet. Every number is parsed from LeastSquares.java's output."""
import re

import common as C
from diagrams import Diagram

sci = C.sci


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"fit: (\d+) observations .*? straight line y = (\S+) \+ (\S+)x, sum of squares (\S+) ; quadratic y = (\S+) \+ (\S+)x \+ (\S+)x\^2, sum of squares (\S+) ;", ln):
            g = m.groups()
            d["fit"] = dict(m=g[0], la=g[1], lb=g[2], lsse=g[3], qa=g[4], qb=g[5], qc=g[6], qsse=g[7])
        elif m := re.match(r"rules: ([\d,]+) data sets .*?: least squares (\S+), least absolute errors (\S+), least largest error (\S+)$", ln):
            d["rules"] = dict(n=m.group(1), ls=m.group(2), lad=m.group(3), mm=m.group(4))
        elif m := re.match(r"wild: .*?: least squares (\S+) -> (\S+) ; least absolute errors (\S+) -> (\S+) ; least largest error (\S+) -> (\S+)$", ln):
            g = m.groups()
            d["wild"] = dict(ls0=g[0], ls1=g[1], lad0=g[2], lad1=g[3], mm0=g[4], mm1=g[5])
        elif m := re.match(r"work: (.+)$", ln):
            d["work"] = re.findall(r"([\d,]+) observations: ([\d,]+) multiply-adds", m.group(1))
        elif m := re.match(r"digits: .*? ; (degree.+)$", ln):
            d["digits"] = re.findall(r"degree (\d+): normal equations error (\S+), QR (\S+?)(?: ;|$)", m.group(1))
        elif m := re.match(r"circle: .*? after ([\d,]+) small steps y = (\S+) \+ (\S+)x, the normal equations' y = (\S+) \+ (\S+)x", ln):
            d["gd"] = dict(steps=m.group(1), a=m.group(2), b=m.group(3), na=m.group(4), nb=m.group(5))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def rules_diagram(d):
    r, w = d["rules"], d["wild"]
    D = Diagram(1000, 250, "Three rules for the best line, compared on the program's data")
    W, H = 300, 130
    boxes = [("ls", "Least squares", ["minimise the sum of squared errors", f"slope error (mean square) {r['ls']}", f"one wild point: slope {w['ls0']} → {w['ls1']}"], "red"),
             ("lad", "Least absolute errors", ["minimise the sum of |errors|", f"slope error (mean square) {r['lad']}", f"one wild point: slope {w['lad0']} → {w['lad1']}"], "ink"),
             ("mm", "Least largest error", ["minimise the worst error", f"slope error (mean square) {r['mm']}", f"one wild point: slope {w['mm0']} → {w['mm1']}"], "ink")]
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 325, 50, W, H, [(t, "title")] + [(s, "combo" if j == 1 else "note") for j, s in enumerate(sub)], color=col)
    D.text(20, 30, f"{r['n']} NOISY DATA SETS, AND ONE OBSERVATION COPIED WRONGLY", "tag")
    D.text(20, 210, "With bell-shaped errors, least squares estimates the slope best; a single wild point pulls it, but less than it pulls the worst-error rule.", "caption")
    D.text(20, 228, "Numbers from LeastSquares.java.", "caption")
    return D


LS_HTML = """
<div class="board ls-board">
  <div style="min-width:0">
    <svg id="ls-svg" viewBox="0 0 360 260" role="img" aria-label="Points and the fitted line; drag a point to move it"></svg>
    <div class="controls">
      <label><input type="checkbox" id="ls-sq" checked> show the squares</label>
      <label><input type="checkbox" id="ls-lad"> least absolute errors</label>
      <label><input type="checkbox" id="ls-mm"> least largest error</label>
      <button type="button" id="ls-wild">Copy one wrongly</button>
      <button type="button" id="ls-reset">Reset</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The best line, by Legendre's rule</div>
    <div class="ls-out" id="ls-out"></div>
    <p class="say" id="ls-say" aria-live="polite"></p>
  </div>
</div>
"""

LS_CSS = """
.ls-board svg{max-width:420px;display:block;margin:0 auto;touch-action:none}
.ls-board .controls{flex-wrap:wrap;font-size:13.5px}
.ls-board .controls input[type=checkbox]{width:auto;padding:0;margin:0 4px 0 0;vertical-align:-2px}
.ls-board .controls label{display:inline-flex;align-items:center}
.ls-out{font-family:var(--mono);font-size:13px;line-height:1.7;margin:4px 0 8px}
.ls-board .say{font-size:14.5px}
"""

LS_JS = r"""
(() => {
  const svg = document.getElementById("ls-svg");
  if (!svg) return;
  const W = 360, H = 260, X0 = 0, X1 = 10, Y0 = 0, Y1 = 8;
  const sx = x => 20 + (x - X0) / (X1 - X0) * (W - 40), sy = y => H - 20 - (y - Y0) / (Y1 - Y0) * (H - 40);
  const ix = px => X0 + (px - 20) / (W - 40) * (X1 - X0), iy = py => Y0 + (H - 20 - py) / (H - 40) * (Y1 - Y0);
  const base = [[0.5, 1.4], [1.5, 1.6], [2.5, 2.5], [3.5, 2.4], [4.5, 3.4], [5.5, 3.3], [6.5, 4.3], [7.5, 4.2], [8.5, 5.1], [9.5, 5.6]];
  let pts = base.map(p => p.slice()), drag = -1;
  const ls = P => { const n = P.length; let sx_ = 0, sy_ = 0, sxx = 0, sxy = 0; P.forEach(([x, y]) => { sx_ += x; sy_ += y; sxx += x * x; sxy += x * y; });
    const b = (n * sxy - sx_ * sy_) / (n * sxx - sx_ * sx_); return [(sy_ - b * sx_) / n, b]; };
  const lad = P => { let best = Infinity, bc = null; for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) { if (P[i][0] === P[j][0]) continue;
    const b = (P[j][1] - P[i][1]) / (P[j][0] - P[i][0]), a = P[i][1] - b * P[i][0]; let s = 0; P.forEach(([x, y]) => s += Math.abs(y - a - b * x)); if (s < best) { best = s; bc = [a, b]; } } return bc; };
  const mm = P => { const err = b => { let lo = Infinity, hi = -Infinity; P.forEach(([x, y]) => { const r = y - b * x; lo = Math.min(lo, r); hi = Math.max(hi, r); }); return [(hi - lo) / 2, (hi + lo) / 2]; };
    let lo = -10, hi = 10; for (let i = 0; i < 120; i++) { const m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3; if (err(m1)[0] < err(m2)[0]) hi = m2; else lo = m1; } const b = (lo + hi) / 2; return [err(b)[1], b]; };
  const line = ([a, b], col, dash) => sv("line", { x1: sx(X0), y1: sy(a + b * X0), x2: sx(X1), y2: sy(a + b * X1), stroke: col, "stroke-width": 2.2, "stroke-dasharray": dash || "" }, svg);
  function draw() {
    svg.innerHTML = "";
    sv("rect", { x: 20, y: 20, width: W - 40, height: H - 40, fill: "none", stroke: "var(--axis)", "stroke-width": 1 }, svg);
    const c = ls(pts);
    let sse = 0;
    if (document.getElementById("ls-sq").checked) pts.forEach(([x, y]) => {
      const r = y - (c[0] + c[1] * x), side = Math.abs(sy(y) - sy(y - r));
      sv("rect", { x: r > 0 ? sx(x) : sx(x) - side, y: Math.min(sy(y), sy(y - r)), width: side, height: side, fill: "var(--red)", "fill-opacity": 0.18, stroke: "var(--red)", "stroke-width": 0.8 }, svg);
    });
    pts.forEach(([x, y]) => { const r = y - (c[0] + c[1] * x); sse += r * r; });
    if (document.getElementById("ls-mm").checked) line(mm(pts), "var(--yellow)", "6 4");
    if (document.getElementById("ls-lad").checked) line(lad(pts), "var(--ink-2)", "3 3");
    line(c, "var(--blue)");
    pts.forEach(([x, y], i) => { const p = sv("circle", { cx: sx(x), cy: sy(y), r: 6, fill: "var(--ink)" }, svg); p.addEventListener("pointerdown", e => { drag = i; e.preventDefault(); }); });
    const out = document.getElementById("ls-out");
    let html = `least squares (blue): y = ${c[0].toFixed(3)} + ${c[1].toFixed(3)}x<br>sum of the squares (red): ${sse.toFixed(3)}`;
    if (document.getElementById("ls-lad").checked) { const l = lad(pts); html += `<br>least absolute errors (grey): slope ${l[1].toFixed(3)}`; }
    if (document.getElementById("ls-mm").checked) { const l = mm(pts); html += `<br>least largest error (yellow): slope ${l[1].toFixed(3)}`; }
    out.innerHTML = html;
    document.getElementById("ls-say").textContent = "Drag any point. The blue line is the one that makes the total area of the red squares as small as possible; no other line has a smaller total.";
  }
  svg.addEventListener("pointermove", e => { if (drag < 0) return; const r = svg.getBoundingClientRect(), px = (e.clientX - r.left) / r.width * W, py = (e.clientY - r.top) / r.height * H;
    pts[drag] = [Math.min(X1, Math.max(X0, ix(px))), Math.min(Y1, Math.max(Y0, iy(py)))]; draw(); });
  window.addEventListener("pointerup", () => { drag = -1; });
  ["ls-sq", "ls-lad", "ls-mm"].forEach(id => document.getElementById(id).addEventListener("change", draw));
  document.getElementById("ls-wild").addEventListener("click", () => { pts[pts.length - 1][1] = 7.8; draw(); });
  document.getElementById("ls-reset").addEventListener("click", () => { pts = base.map(p => p.slice()); draw(); });
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How least squares combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "fc": (20, 20, "Elimination", "solve n equations in n unknowns", "fangcheng, Era 2 topic 1", "ink"),
        "pr": (395, 20, "Probability", "chances of errors", "topic 4", "ink"),
        "ob": (770, 20, "Too many observations", "astronomy and surveying", "Ceres, 1801", "ink"),
        "ls": (395, 170, "Least squares", "⊕ minimise the sum of squared errors", "Legendre 1805; Gauss 1809", "red"),
        "fft": (20, 330, "Fitting periodic data", "Gauss's FFT", "topic 9", "ink"),
        "qr": (395, 330, "Orthogonal methods", "QR, without squaring the problem", "Era 5", "blue"),
        "ml": (770, 330, "Machine learning", "linear models trained on squared error", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("fc", "ls", ports=("bottom", "top:0.15"))
    D.edge("pr", "ls", ports=("bottom", "top"))
    D.edge("ob", "ls", ports=("bottom", "top:0.85"))
    D.edge("ls", "fft", ports=("bottom:0.1", "top:0.7"))
    D.edge("ls", "qr", ports=("bottom", "top"))
    D.edge("ls", "ml", ports=("bottom:0.9", "top:0.3"))
    D.text(20, 615, "Gauss linked least squares to the probability of errors in 1809; Legendre justified it by the balance it sets up among the errors.", "caption")
    return D


def chain(d):
    r, w, dg = d["rules"], d["wild"], d["digits"]
    d12 = next(x for x in dg if x[0] == "12")
    steps = [
        ("More observations than unknowns, and they disagree",
         "Minimise the sum of squared errors; solve the normal equations by elimination", "Legendre 1805; Gauss 1809"),
        (f"One wild observation pulls the line: slope {w['ls0']} → {w['ls1']}",
         f"Least absolute errors resists it ({w['lad0']} → {w['lad1']}), at a price for ordinary noise", "robust fitting"),
        (f"Forming the normal equations squares the difficulty: degree 12 loses all its digits ({sci(d12[1])})",
         f"Orthogonal (QR) methods that never form them: {sci(d12[2])}", "Householder, Era 5"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a rule for 'best' to stable algorithms")
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
    f, r, w, wk, dg, gd = d["fit"], d["rules"], d["wild"], d["work"], d["digits"], d["gd"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Chinese elimination (Era 2, topic 1) solves as many equations as unknowns; Pascal and Fermat (topic 4) began the calculation of chances; astronomers had more observations than unknowns, and the observations disagreed. Legendre's rule turns the too-many equations into exactly as many as unknowns, which elimination can solve. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: least squares. Blue: where it went after this era."),
        ]),
        dict(id="fit", eyebrow="Try it", title="Drag the points; watch the squares", toc="Try it", blocks=[
            dict(type="p", text="Each red square is a residual squared: the gap between a point and the blue line, drawn as a square. The blue line is the one with the smallest total area. Drag the points, copy one wrongly, and switch on the other two rules to compare them."),
            dict(type="widget", html=LS_HTML, js=LS_JS, css=LS_CSS,
                 fallback=dict(type="diagram", name="rules", diagram=rules_diagram(d)),
                 note="In the interactive edition you can drag the points and compare least squares with the other two rules."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="As many equations as unknowns", toc="How it works", blocks=[
            dict(type="p", text="Fit y = c₀ + c₁x (or more terms) to m observations. Each observation gives an equation that will not hold exactly; its error is the residual. Legendre's rule: make the sum of the squared residuals as small as possible. At the minimum, the derivative with respect to each coefficient is zero, which gives one linear equation per coefficient: the normal equations. However many observations there are, a straight line gives 2 equations and a quadratic 3, solved by elimination."),
            dict(type="table", head=["Model, fitted to " + f["m"] + " noisy observations", "Coefficients", "Sum of squared residuals"], num=[2],
                 rows=[["Straight line", f"{f['la']} + {f['lb']}x", f["lsse"]], ["Quadratic (the true curve is 2 + 0.7x + 0.15x²)", f"{f['qa']} + {f['qb']}x + {f['qc']}x²", f["qsse"]]]),
            dict(type="p", text="The program also nudged the coefficients of each fit a little in 2,000 random ways: no nudge ever lowered the sum of squares."),
            dict(type="diagram", name="rules-steps", diagram=rules_diagram(d)),
            dict(type="callout", kind="key", label="Key idea",
                 text="When the data cannot all be satisfied, decide what \"best\" means, as a number to minimise, and then minimise it. Squares make the minimum a set of linear equations, which an old algorithm already solves."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Cheap in observations, fragile in digits", toc="Measured", blocks=[
            dict(type="table", head=["Observations (quadratic fit)", "Multiply-adds to form and solve the normal equations"], num=[0, 1], rows=[[a, b] for a, b in wk]),
            dict(type="p", text="The work grows only in proportion to the number of observations: each observation adds its share to a 3 × 3 system, and the system is the same size for 22 observations or 100,000."),
            dict(type="table", head=["Polynomial degree", "Largest coefficient error, normal equations", "Largest coefficient error, QR"], num=[1, 2],
                 rows=[[a, sci(b), sci(c)] for a, b, c in dg]),
            dict(type="p", text="The price: forming the normal equations squares the sensitivity of the problem. On exact data, the coefficients of a degree-12 fit come out completely wrong from the normal equations in 64-bit floating point, while an orthogonal (QR) method, which never forms them, keeps most of its digits."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A planet found, lost and found again", toc="The evidence", blocks=[
            dict(type="p", text="Piazzi discovered Ceres on 1 January 1801 and \"had only been able to observe 9 degrees of its orbit before it disappeared behind the Sun\" (MacTutor); Weiss counts 22 observations over 41 days. Gauss's prediction \"differed greatly from the others\", and Ceres was found \"almost exactly where Gauss had predicted\": by Zach on 7 December (MacTutor) or by Zach and Olbers in December, Olbers on the 31st (Weiss; **disputed** dates). Whether Gauss used least squares for the Ceres orbit is **disputed**: MacTutor and Weiss say yes; *thatsmaths* says it is unclear."),
            dict(type="p", text="Legendre published first, in 1805: the method \"consiste à rendre minimum la somme des quarrés des erreurs\", which sets up \"entre les erreurs une sorte d'équilibre\" that keeps the extreme errors from prevailing. Gauss, in 1809, called it \"principium nostrum quo jam inde ab anno 1795 usi sumus\": our principle, used since 1795. The priority dispute is **disputed** to this day; Stigler could not reproduce Gauss's 1799 results with least squares (Chalberg)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Training a model is fitting a line", toc="Full circle", blocks=[
            dict(type="p", text="Machine-learning libraries rarely solve normal equations. They start from a guess and repeatedly nudge the coefficients downhill on the sum of squared errors: gradient descent."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program trained a straight line by gradient descent on the 15 points with the wild one. After {gd['steps']} small steps it reached y = {gd['a']} + {gd['b']}x, exactly the line the normal equations give in one elimination: y = {gd['na']} + {gd['nb']}x. Legendre's sum of squares is still the loss function of a linear model."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why squares rather than plain errors?", "Plain errors cancel (+3 and −3 sum to 0). Squares are always positive, and their sum has a minimum found by setting derivatives to zero: linear equations."),
            ("How many normal equations for a quadratic fitted to 1,000 points?", "Three: one per coefficient, however many points."),
            ("Why does one wild point move least squares so much?", "Its error is squared: an error of 20 counts 400, outweighing many small errors."),
            ("Why does least absolute errors resist it?", "Each point counts in proportion to its error, not its square, and the best line passes through two of the points; a single wild point cannot drag it far."),
            ("What is the point of the QR method?", "It finds the same least-squares answer without forming FᵀF, which would square the problem's sensitivity to rounding."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Sur la méthode des moindres quarrés (1805)", text="Legendre's appendix to his book on comet orbits: the first publication of least squares, in French.",
                 draw=C.draw_book, link="https://www.york.ac.uk/depts/maths/histstat/legendre2.pdf", link_text="University of York",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LeastSquares", d["checks"],
                           "that no nearby coefficients beat the least-squares fit (4,000 random nudges), the three rules on 10,000 noisy data sets, the pull of one wild point, the work of forming normal equations, their loss of digits against QR, and gradient descent reaching the same line.",
                           ["static double[] normalEquations(", "static double[] solve("]),
    ]
    return dict(
        title="Least Squares, and the Lost Planet", date="1801–1809",
        description="Era 3, topic 8 of The Algorithm Evolution Atlas: Legendre's and Gauss's method of least squares, the lost and recovered Ceres, and why least squares still trains linear models.",
        lede="A new planet was found on the first day of the nineteenth century and lost in the Sun's glare six weeks later. Recovering it needed an orbit from a few disagreeing measurements. The rule that settles which answer is best, the sum of squared errors, was published four years later, and two great mathematicians claimed it.",
        fieldnote="I expected the astronomers to argue about which measurement to trust. Instead a geometer in Paris proposed a rule for trusting all of them a little: make the sum of the squared errors as small as possible. The old algorithm for equations then did the rest.",
        card=[("When", "Ceres 1801; Legendre 1805; Gauss 1809"),
              ("Where", "Palermo, Paris, Göttingen"),
              ("What hurt", "More observations than unknowns, and they disagree"),
              ("The fix", "Minimise the sum of squared errors; solve the normal equations"),
              ("Cost", "A small system of equations, the same size for any number of observations")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LeastSquares.java`.",
    )
