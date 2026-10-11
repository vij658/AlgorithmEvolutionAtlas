"""Era 3, topic 5: Newton's method. Every number is parsed from NewtonsMethod.java's output."""
import re

import common as C
from diagrams import Diagram

sci, pretty = C.sci, C.pretty


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"newton: .*?dropping the cubic term before the third step: x = 2 \+ p: (.+?) = 0 ; (.+) ; keeping every term instead ends at (\S+) ; true root (\S+) ; (\d+) correct decimals$", ln):
            d["nw"] = dict(poly=m.group(1), keepall=m.group(3), root=m.group(4), dec=m.group(5),
                           steps=[dict(lin=g[0], sign=g[1], con=g[2], corr=g[3], fig=g[4], x=g[5]) for g in
                                  re.findall(r"(\S+) p ([+-]) (\S+) = 0 gives (\S+) \((\d+) figures?\) ; x = (\S+)", m.group(2))])
        elif m := re.match(r"raphson: .*?: (.+)$", ln):
            d["rp"] = [(int(a), int(b)) for a, b in re.findall(r"step (\d+): (\d+)", m.group(1))]
        elif m := re.match(r"work: (\d+) correct decimals of the root ; Newton (\d+) steps ; digit by digit (\d+) steps .*? ; bisection (\d+) halvings$", ln):
            d["work"] = dict(target=m.group(1), newton=m.group(2), digit=m.group(3), bis=m.group(4))
        elif m := re.match(r"survey: ([\d,]+) polynomials .*?: (.+?) ; average (\S+) steps$", ln):
            d["sv"] = dict(n=m.group(1), hist=re.findall(r"(\d+) steps: ([\d,]+)", m.group(2)), avg=m.group(3))
        elif m := re.match(r"simpson: cos x = x from 1: x = (\S+) in (\d+) steps ; .*?: (.+?) ; solution \((\S+), (\S+)\)$", ln):
            d["sp"] = dict(cos=m.group(1), cosn=m.group(2), it=re.findall(r"\((\S+), (\S+)\)", m.group(3)), u=m.group(4), v=m.group(5))
        elif m := re.match(r"fail: x\^3 - 2x \+ 2 from 0 cycles (.+?), \.\.\. ; a double root, .*? needs (\d+) steps .*? needs (\d+)\) ; z\^3 = 1 from ([\d,]+) starting points .*?: ([\d,]+) converge \(to 1: ([\d,]+) ; to the other two: ([\d,]+) and ([\d,]+)\), ([\d,]+) take more than 20 steps, on average (\S+) steps$", ln):
            g = m.groups()
            d["fail"] = dict(cyc=g[0], dbl=g[1], simple=g[2], n=g[3], conv=g[4], r1=g[5], r2=g[6], r3=g[7], slow=g[8], avg=g[9])
        elif m := re.match(r"circle: .*? at every step: (.+?) ; 1/7 without division, .*?correct decimals: (.+)$", ln):
            d["circ"] = dict(fr=m.group(1).split(", "), rec=m.group(2).split(", "))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def newton_steps(d):
    nw = d["nw"]
    D = Diagram(1000, 250, "Newton's own steps on x³ − 2x − 5 = 0: keep the two lowest terms, solve, shift, repeat")
    W, H = 220, 130
    boxes = [("s0", "Start", ["x = 2 + p", pretty(nw["poly"]) + " = 0", ""], "ink")]
    for i, s in enumerate(nw["steps"]):
        boxes.append((f"s{i + 1}", f"Step {i + 1}", [f"{s['lin']} p {'−' if s['sign'] == '-' else '+'} {s['con']} = 0", f"p = {s['corr']}", f"x = {s['x']}"],
                      "red" if i == len(nw["steps"]) - 1 else "ink"))
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title")] + [(s, "combo" if j == 2 else "note") for j, s in enumerate(sub) if s], color=col)
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "EACH STEP KEEPS TWICE AS MANY FIGURES: 1, 2, 4", "tag")
    D.text(20, 210, f"Newton's 2.09455147 has {nw['dec']} correct decimals (true root {nw['root']}). The cubic term is dropped before the third step;", "caption")
    D.text(20, 228, f"keeping it ends at {nw['keepall']}. Numbers from NewtonsMethod.java.", "caption")
    return D


NM_HTML = """
<div class="board nm-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="nm-f">f(x) = <select id="nm-f">
        <option value="0" selected>x³ − 2x − 5 (Newton's)</option>
        <option value="1">cos x − x (Simpson's kind)</option>
        <option value="2">x³ − 2x + 2 (a trap)</option>
        <option value="3">(x − 1)²(x + 2) (a double root)</option>
      </select></label>
    </div>
    <div class="controls">
      <label for="nm-x">start <input id="nm-x" type="range" min="-300" max="350" value="320"></label><span class="nm-v" id="nm-xv"></span>
      <button type="button" id="nm-step">Step</button>
      <button type="button" id="nm-reset">Reset</button>
    </div>
    <svg id="nm-svg" viewBox="0 0 340 240" role="img" aria-label="The curve, its tangent at the current guess, and where the tangent crosses zero"></svg>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Guesses</div>
    <ol class="nm-steps" id="nm-steps"></ol>
    <p class="say" id="nm-say" aria-live="polite"></p>
  </div>
</div>
"""

NM_CSS = """
.nm-board .controls{flex-wrap:wrap}
.nm-board input[type=range]{width:min(180px,40vw)}
.nm-v{font-family:var(--mono);font-size:13px;min-width:3em;display:inline-block}
.nm-board svg{max-width:380px;display:block;margin:0 auto}
.nm-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13px;display:grid;gap:4px;font-family:var(--mono)}
.nm-steps b{color:var(--red)}
.nm-board .say{font-size:14.5px}
"""

NM_JS = r"""
(() => {
  const svg = document.getElementById("nm-svg");
  if (!svg) return;
  const F = [
    [x => x ** 3 - 2 * x - 5, x => 3 * x * x - 2, [-1, 3.5]],
    [x => Math.cos(x) - x, x => -Math.sin(x) - 1, [-1, 3]],
    [x => x ** 3 - 2 * x + 2, x => 3 * x * x - 2, [-2.5, 2]],
    [x => (x - 1) ** 2 * (x + 2), x => 2 * (x - 1) * (x + 2) + (x - 1) ** 2, [-2.6, 3]],
  ];
  let xs = [];
  const ref = k => { if (k === 3) return 1; let x = [2, 1, -2][k]; for (let i = 0; i < 80; i++) x -= F[k][0](x) / F[k][1](x); return x; };
  function digits(x, r) { const e = Math.abs(x - r); if (e === 0) return 16; let d = 0; while (d < 16 && e < 0.5 * 10 ** -(d + 1)) d++; return d; }
  function draw() {
    const k = +document.getElementById("nm-f").value, [f, fp, [lo, hi]] = F[k];
    svg.innerHTML = "";
    const W = 340, H = 240;
    let ylo = Infinity, yhi = -Infinity; for (let i = 0; i <= 200; i++) { const y = f(lo + (hi - lo) * i / 200); ylo = Math.min(ylo, y); yhi = Math.max(yhi, y); }
    ylo = Math.max(ylo, -40); yhi = Math.min(yhi, 40); const pad = (yhi - ylo) * 0.08; ylo -= pad; yhi += pad;
    const sx = x => 10 + (x - lo) / (hi - lo) * (W - 20), sy = y => H - 10 - (Math.max(ylo, Math.min(yhi, y)) - ylo) / (yhi - ylo) * (H - 20);
    sv("line", { x1: 10, y1: sy(0), x2: W - 10, y2: sy(0), stroke: "var(--axis)", "stroke-width": 1 }, svg);
    const pts = []; for (let i = 0; i <= 240; i++) { const x = lo + (hi - lo) * i / 240; pts.push(`${sx(x).toFixed(1)},${sy(f(x)).toFixed(1)}`); }
    sv("polyline", { points: pts.join(" "), fill: "none", stroke: "var(--blue)", "stroke-width": 2 }, svg);
    xs.forEach((x, i) => {
      if (i === xs.length - 1 || !isFinite(x)) return;
      const y = f(x), m = fp(x), xn = xs[i + 1];
      if (!isFinite(xn)) return;
      sv("line", { x1: sx(x), y1: sy(0), x2: sx(x), y2: sy(y), stroke: "var(--muted)", "stroke-width": 1, "stroke-dasharray": "3 3" }, svg);
      sv("line", { x1: sx(x), y1: sy(y), x2: sx(xn), y2: sy(0), stroke: "var(--red)", "stroke-width": 1.6 }, svg);
    });
    xs.forEach((x, i) => { if (isFinite(x) && x >= lo && x <= hi) sv("circle", { cx: sx(x), cy: sy(0), r: i === xs.length - 1 ? 5 : 3, fill: i === xs.length - 1 ? "var(--red)" : "var(--ink-2)" }, svg); });
    sv("text", { x: 12, y: 16, fill: "var(--muted)", "font-size": 10 }, svg, `x from ${lo} to ${hi}; red: tangent lines`);
    const r = ref(k), ol = document.getElementById("nm-steps"); ol.innerHTML = "";
    xs.forEach((x, i) => { const dg = isFinite(x) ? digits(x, r) : 0; const s = isFinite(x) ? x.toFixed(15) : "—"; const cut = s.indexOf(".") + 1 + dg; el("li", {}, ol).innerHTML = isFinite(x) ? `<b>${s.slice(0, x === r ? s.length : Math.max(0, dg ? cut : 0))}</b>${s.slice(x === r ? s.length : Math.max(0, dg ? cut : 0))} · ${dg} dec.` : "—"; });
    const last = xs[xs.length - 1];
    const say = document.getElementById("nm-say");
    if (k === 2 && xs.length > 3 && Math.abs(last - xs[xs.length - 3]) < 1e-12) say.textContent = "The guesses jump back and forth between 0 and 1 for ever: from this start, the tangent never leads to the root near −1.77.";
    else if (k === 3) say.textContent = "At a double root the curve is flat, the tangent is a poor guide, and the error only halves each step instead of squaring.";
    else say.textContent = xs.length > 1 ? "Near the root the number of correct decimals roughly doubles at each step." : "Press Step to follow the tangent.";
  }
  function reset() {
    const v = +document.getElementById("nm-x").value / 100, k = +document.getElementById("nm-f").value;
    const start = k === 2 && Math.abs(v) < 0.005 ? 0 : v;
    xs = [start]; document.getElementById("nm-xv").textContent = start.toFixed(2); draw();
  }
  document.getElementById("nm-step").addEventListener("click", () => { const k = +document.getElementById("nm-f").value, x = xs[xs.length - 1]; if (xs.length < 14 && isFinite(x)) { const d = F[k][1](x); xs.push(d === 0 ? NaN : x - F[k][0](x) / d); } draw(); });
  document.getElementById("nm-reset").addEventListener("click", reset);
  document.getElementById("nm-x").addEventListener("input", reset);
  document.getElementById("nm-f").addEventListener("change", () => { const k = +document.getElementById("nm-f").value; document.getElementById("nm-x").value = [320, 280, 0, 250][k]; reset(); });
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Newton's method combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "bab": (20, 20, "Average x and a/x", "the Babylonian square root", "Era 1 topic 4", "ink"),
        "qin": (395, 20, "Shift the polynomial", "root digit by digit", "Qin Jiushao, Era 2 topic 9", "ink"),
        "flx": (770, 20, "Tangents and fluxions", "the slope of a curve", "the calculus, 1660s", "ink"),
        "nm": (395, 170, "Newton's method", "⊕ follow the tangent, then repeat", "Newton 1669; Raphson 1690; Simpson 1740", "red"),
        "cub": (20, 330, "Formulas that cancel", "repaired by one step", "topic 1", "ink"),
        "lsq": (395, 330, "Orbits and least squares", "iteration on real data", "topic 8", "ink"),
        "frc": (770, 330, "Basins and fractals", "where each start ends up", "z³ = 1 in the plane", "blue"),
        "div": (395, 480, "Division without dividing", "x ← x(2 − ax)", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("bab", "nm", ports=("bottom", "top:0.15"))
    D.edge("qin", "nm", ports=("bottom", "top"))
    D.edge("flx", "nm", ports=("bottom", "top:0.85"))
    D.edge("nm", "cub", ports=("bottom:0.1", "top:0.7"))
    D.edge("nm", "lsq", ports=("bottom", "top"), dashed=True)
    D.edge("nm", "frc", ports=("bottom:0.9", "top:0.3"))
    D.edge("lsq", "div", ports=("bottom", "top"), dashed=True)
    D.text(20, 615, "Dashed: iteration as a way of working, not a documented borrowing.", "caption")
    return D


def chain(d):
    w, f = d["work"], d["fail"]
    steps = [
        ("Formulas stop at degree four, and digit-by-digit extraction gains one digit a step",
         "Guess, then correct by the tangent line; the digits roughly double", "Newton, 1669"),
        ("Newton rewrote the whole polynomial at every step",
         "Apply the same correction to the original equation again and again", "Raphson, 1690"),
        ("Only polynomials, only one unknown",
         "Any equation by fluxions, and two equations in two unknowns", "Simpson, 1740"),
        (f"From a bad start it can cycle for ever ({f['cyc']}, …); at a double root it slows to {f['dbl']} steps",
         "Start close, bracket the root, or switch method", "safeguarded solvers"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from Newton's polynomials to safeguarded solvers")
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
    nw, rp, w, sv, sp, fl, ci = d["nw"], d["rp"], d["work"], d["sv"], d["sp"], d["fail"], d["circ"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The Babylonians improved a square root by averaging (Era 1, topic 4); Qin Jiushao shifted a polynomial so that its next digit could be read off (Era 2, topic 9); in the 1660s Newton learned to find the slope of any curve. Put together: shift the polynomial by a guess, and read the next correction from the slope. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Newton's method. Blue: two places where it shows up today."),
        ]),
        dict(id="tangent", eyebrow="Try it", title="Follow the tangent", toc="Try it", blocks=[
            dict(type="p", text="Choose a function and a starting guess, then press Step. Each step draws the tangent at the current guess (red) and moves to where it crosses zero. Bold digits are correct. Try Newton's own equation (he started at 2; the default start here is further away, so the tangents show), then the trap and the double root."),
            dict(type="widget", html=NM_HTML, js=NM_JS, css=NM_CSS,
                 fallback=dict(type="diagram", name="newton-steps", diagram=newton_steps(d)),
                 note="In the interactive edition you can step Newton's method on four equations from any starting point and watch the tangents."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Guess, correct, repeat", toc="How it works", blocks=[
            dict(type="p", text=f"**Newton's way (1669).** For x³ − 2x − 5 = 0, start at 2 and put x = 2 + p. The polynomial in p is {pretty(nw['poly'])} = 0. For small p the last two terms matter most: 10p − 1 = 0, so p ≈ 0.1. Put p = 0.1 + q, write out the polynomial in q, and repeat, keeping twice as many figures each time:"),
            dict(type="diagram", name="newton-own", diagram=newton_steps(d)),
            dict(type="p", text=f"The program repeats these shifts exactly. With the cubic term dropped before the third step, as negligible, it arrives at Newton's **2.09455147**, with the intermediate equations {nw['steps'][2]['lin']} p + {nw['steps'][2]['con']} = 0; keeping every term instead gives {nw['keepall']}."),
            dict(type="p", text="**Raphson's way (1690).** Skip the new polynomials: apply x ← x − f(x)/f′(x) to the original equation again and again. Geometrically, slide down the tangent line to where it crosses zero. The program, with 80-digit arithmetic:"),
            dict(type="table", head=["Step", "Correct decimals"], num=[0, 1], rows=[[str(a), str(b)] for a, b in rp]),
            dict(type="p", text=f"The correct decimals roughly double each step: the error is roughly squared. Over {sv['n']} random polynomials of degree 3 to 6, started 1% away from a known root, Newton's method reached 12 significant figures in {', '.join(f'{k} steps for {v}' for k, v in sv['hist'])} (average {sv['avg']})."),
            dict(type="p", text=f"**Simpson's way (1740).** Any equation, not only polynomials: cos x = x from 1 gives {sp['cos']} in {sp['cosn']} steps. And two equations in two unknowns: for x² + y² = 4 and xy = 1, each step solves a 2 × 2 linear system by Cramer's rule, giving ({sp['u']}, {sp['v']})."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Replace a hard problem by an easy one that is nearly the same (a curve by its tangent), solve the easy one, and repeat. When each repetition squares the error, a few steps are enough for any precision."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Steps for sixty decimals, and where it fails", toc="Measured", blocks=[
            dict(type="table", head=["Method", f"Steps for {w['target']} correct decimals of Newton's root"], num=[1],
                 rows=[["Newton's method", w["newton"]], ["Digit by digit (Era 2, topic 9)", w["digit"]], ["Bisection (halve the bracket)", w["bis"]]]),
            dict(type="p", text=f"The price is reliability. From 0, x³ − 2x + 2 = 0 gives the guesses {fl['cyc']}, … for ever. At a double root the curve is flat and the error only halves: (x − 1)²(x + 2) needs {fl['dbl']} steps to come within 10⁻⁶ of 1, where the simple root of x³ − 1 needs {fl['simple']}. In the complex plane, z³ = 1 has three roots; of {fl['n']} starting points in a square around 0, {fl['conv']} converged ({fl['r1']} to 1, {fl['r2']} and {fl['r3']} to the other two), but {fl['slow']} needed more than 20 steps, and the borders between the three regions are endlessly intricate."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Three names for one method", toc="The evidence", blocks=[
            dict(type="p", text="*De analysi* was written \"probably mid-1669\" and printed in 1711; the earliest printed account of the method is chapter 94 of John Wallis's *A Treatise of Algebra* (1685). Raphson's *Analysis aequationum universalis* (1690) iterated on the original equation and, in his words, was \"not only, I believe, not of the same origin, but also, certainly, not with the same development\". Simpson's *Essays* (1740) gave the general form and the case of two equations. Ypma concludes that \"the Newton-Raphson-Simpson method is a designation more nearly representing the facts of history\"; Kollerstrom argues that \"this invention has migrated back in time\" from Simpson to Newton (**disputed**)."),
            dict(type="p", text="Earlier forms: Ypma reports a method algebraically equivalent to Newton's in al-Ṭūsī, and a form of it in al-Kashi for xᴾ − N = 0. The modern notation f′(x) comes from Lagrange (1798 per Ypma; 1797 per the DNB: **disputed**)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The Babylonian rule was Newton's method all along", toc="Full circle", blocks=[
            dict(type="p", text=f"Applied to x² − 2 = 0, Newton's step is x − (x² − 2)/(2x) = (x + 2/x)/2: the Babylonian rule of averaging x and 2/x (Era 1, topic 4). The program computed both in exact fractions from 1: {', '.join(ci['fr'])}, identical at every step."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Newton's method can even divide without dividing: for 1/a, iterate x ← x(2 − ax), which uses only multiplication and subtraction. For 1/7 from 0.1 the correct decimals went {', '.join(ci['rec'])}. A method from 1669 turns the slowest arithmetic operation into a few of the fastest."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does Newton keep only the two lowest terms, 10p − 1?", "For small p, p² and p³ are much smaller than p, so the line 10p − 1 is a good stand-in for the whole polynomial near p = 0."),
            ("What does one step of x ← x − f(x)/f′(x) mean on a graph?", "Draw the tangent at the current guess and slide down it to where it meets the x-axis."),
            ("Why do the correct digits double?", "Near a simple root the new error is proportional to the square of the old one: an error of 10⁻⁵ becomes about 10⁻¹⁰."),
            ("Why is a double root slow?", "There f′ is also zero, the curve is flat, and each step only halves the distance to the root."),
            ("What does x ← x(2 − ax) converge to?", "1/a: if x = 1/a exactly, then 2 − ax = 1 and x stays put; near it, the error is squared each step."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Ypma, Historical Development of the Newton–Raphson Method", text="SIAM Review 37 (1995): Newton's worked example, Raphson's tract and Simpson's essays, side by side.",
                 draw=C.draw_book, link="https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/NewtonRaphson_SIAMRev.pdf", link_text="PDF",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "NewtonsMethod", d["checks"],
                           "Newton's own shifts reaching 2.09455147, the doubling of correct digits, 10,000 random polynomials converging from 1% away, Simpson's system by Cramer's rule, the 2-cycle, the Babylonian rule as Newton's step in exact fractions, and division without dividing.",
                           ["static BigDecimal[] shift("]),
    ]
    return dict(
        title="Newton's Method", date="1669–1740",
        description="Era 3, topic 5 of The Algorithm Evolution Atlas: Newton's, Raphson's and Simpson's versions of root-finding by tangent lines, the doubling of correct digits, and where the method fails.",
        lede="Guess a root. Pretend the curve is a straight line near your guess, solve the straight line, and repeat. With each round the number of correct digits roughly doubles. Three people, over seventy years, made it the method every computer still uses.",
        fieldnote="Qin Jiushao dug out roots one digit at a time. Here the digits arrive in growing heaps: one, two, four, eight. The cost is trust: start in the wrong place and the method may wander for ever.",
        card=[("When", "Newton 1669 (printed 1685, 1711); Raphson 1690; Simpson 1740"),
              ("Where", "Cambridge and London"),
              ("What hurt", "Formulas stop at degree four; digit-by-digit roots are slow"),
              ("The fix", "Follow the tangent line, and repeat"),
              ("Cost", f"{w['newton']} steps for {w['target']} decimals, against {w['bis']} halvings by bisection")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `NewtonsMethod.java`.",
    )
