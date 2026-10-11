"""Era 2, topic 6: algorism and al-jabr. Every number is parsed from AlKhwarizmi.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"examples": [], "float": []}
    for ln in text.splitlines():
        if m := re.match(r"example (.+?): type (\d), (.+?) ; recipe: (.+?) ; x = (.+)$", ln):
            d["examples"].append(dict(words=m.group(1), type=int(m.group(2)), tname=m.group(3), recipe=m.group(4), x=m.group(5)))
        elif m := re.match(r"random: (\d+) equations .* ; (\d+) reduce to nothing ; (\d+) have every term on one side ; (\d+) sorted into the six types, all agreeing with the quadratic formula: (.+)$", ln):
            types = [(re.match(r"(.+) (\d+)$", t.strip()).group(1), int(re.match(r"(.+) (\d+)$", t.strip()).group(2))) for t in m.group(5).split(";")]
            d["random"] = dict(n=int(m.group(1)), none=int(m.group(2)), oneside=int(m.group(3)), sorted=int(m.group(4)), types=types)
        elif m := re.match(r"reduce: (.+?) ; al-jabr: (.+?) ; al-muqabala: (.+?) ; recipe: (.+?) ; x = (.+)$", ln):
            d["reduce"] = dict(eq=m.group(1), jabr=m.group(2), muq=m.group(3), recipe=m.group(4), x=m.group(5))
        elif m := re.match(r"sqrt2: (\d+) digits of the root of 2 ; digit by digit (\d+) steps \((\d+) trial digits\) ; averaging (\d+) steps ; (.+)$", ln):
            d["sqrt"] = dict(digits=int(m.group(1)), dsteps=int(m.group(2)), trials=int(m.group(3)), avg=int(m.group(4)), value=m.group(5))
        elif m := re.match(r"float x\^2 \+ 1 = (\S+) x: small root by the recipe (\S+) ; rearranged (\S+) ; recipe error (\S+) of the answer$", ln):
            d["float"].append(dict(big=m.group(1), recipe=m.group(2), stable=m.group(3), err=float(m.group(4))))
    d["checks"] = C.checks(text)
    return d


def square_svg(d):
    """Completing the square for x² + 10x = 39: the square, two strips of 5 by x, and the missing corner of 25."""
    def draw(t, standalone):
        u = 20                                            # pixels per unit; x = 3, half the roots = 5
        x0, y0, X, H = 40, 50, 3 * u, 5 * u
        out = [C.rect(x0, y0, X, X, t["surface"], t["ink"], 2), C.text(x0 + X / 2, y0 + X / 2 + 5, "x²", t["ink"], 15, "middle", 700),
               C.rect(x0 + X, y0, H, X, t["wash"], t["blue"], 2), C.text(x0 + X + H / 2, y0 + X / 2 + 5, "5x", t["blue"], 14, "middle", 700),
               C.rect(x0, y0 + X, X, H, t["wash"], t["blue"], 2), C.text(x0 + X / 2, y0 + X + H / 2 + 5, "5x", t["blue"], 14, "middle", 700),
               C.rect(x0 + X, y0 + X, H, H, "none", t["red"], 2.5, extra='style="stroke-dasharray:6 4"'),
               C.text(x0 + X + H / 2, y0 + X + H / 2 + 5, "25", t["red"], 16, "middle", 700),
               C.text(x0 + X / 2, y0 - 10, "x", t["muted"], 13, "middle"), C.text(x0 + X + H / 2, y0 - 10, "5", t["muted"], 13, "middle")]
        ex = d["examples"][0]
        steps = ["A square and 10 roots equal 39.", "Split the 10 roots into two strips of 5, along two sides.",
                 "The figure lacks a corner of 5 × 5 = 25.", "39 + 25 = 64 completes a square, so its side is 8.",
                 f"Take away the 5: x = {ex['x']}, and the square is 9."]
        for i, s in enumerate(steps):
            out.append(C.text(260, 70 + i * 30, f"{i + 1}. {s}", t["ink"] if i < 4 else t["red"], 14, "start", 700 if i == 4 else 400))
        return C.svg_doc(760, 230, "".join(out), "Completing the square for a square and ten roots equal to thirty-nine", t, standalone, 0.6, 760)
    return draw


AJ_HTML = """
<div class="board aj-board">
  <div style="min-width:0">
    <div class="aj-eq" id="aj-eq">
      <div class="side"><b>Left</b></div>
      <div class="side"><b>Right</b></div>
    </div>
    <div class="controls">
      <button id="aj-next" class="primary" type="button">Next step</button>
      <button id="aj-all" type="button">Solve</button>
      <button id="aj-reset" type="button">Start again</button>
    </div>
    <div class="presets" id="aj-pre"></div>
    <svg id="aj-fig" viewBox="0 0 360 250" role="img" aria-label="The completed square"></svg>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Al-jabr, al-muqabala, and the recipe</div>
    <ol class="aj-steps" id="aj-steps" aria-live="polite"></ol>
  </div>
</div>
"""

AJ_CSS = """
.aj-eq{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}
.aj-eq .side{background:var(--wash);border:1px solid var(--rule);padding:8px;display:flex;flex-direction:column;gap:6px;min-width:0}
.aj-eq label{display:flex;justify-content:space-between;gap:6px;font-size:13px;color:var(--ink-2);align-items:center}
.aj-eq input{width:4.6em;font:inherit;font-family:var(--mono);font-size:14px;padding:3px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.aj-steps{margin:0;padding-left:20px;font-size:14px}
.aj-steps li{margin-bottom:8px}
.aj-steps li b{font-family:var(--mono)}
.aj-board svg{max-width:360px;margin:8px auto 0;background:var(--wash)}
"""

AJ_JS = r"""
(() => {
  const eq = document.getElementById("aj-eq");
  if (!eq) return;
  const kinds = ["squares", "roots", "units"];
  const inputs = [[], []];
  eq.querySelectorAll(".side").forEach((sd, s) => kinds.forEach(k => {
    const lab = el("label", {}, sd, k);
    inputs[s].push(el("input", { type: "number", min: -99, max: 99, value: 0, "aria-label": `${s ? "right" : "left"} ${k}` }, lab));
  }));
  const PRE = [["a square and 10 roots = 39", [1, 10, 0], [0, 0, 39]], ["a square and 21 = 10 roots", [1, 0, 21], [0, 10, 0]],
    ["3 roots and 4 = a square", [0, 3, 4], [1, 0, 0]], ["10 roots − a square = 4 roots and 9", [-1, 10, 0], [0, 4, 9]],
    ["2 squares − 10 roots = 48 − 6 roots", [2, -10, 0], [0, -6, 48]]];
  const pre = document.getElementById("aj-pre");
  PRE.forEach(([n, L, R]) => { const b = el("button", { type: "button" }, pre, n); b.addEventListener("click", () => { set(L, R); reset(); }); });
  function set(L, R) { L.forEach((v, i) => inputs[0][i].value = v); R.forEach((v, i) => inputs[1][i].value = v); }
  const gcd = (a, b) => b ? gcd(b, a % b) : Math.abs(a);
  const F = (n, d = 1) => { if (d < 0) { n = -n; d = -d; } const g = gcd(n, d) || 1; return [n / g, d / g]; };
  const fs = ([n, d]) => d === 1 ? String(n) : (Math.abs(n) > d ? `${Math.trunc(n / d)} ${Math.abs(n % d)}/${d}` : `${n}/${d}`);
  const fv = ([n, d]) => n / d;
  const side = t => {
    const p = [];
    if (t[0]) p.push([t[0], `square${Math.abs(t[0]) === 1 ? "" : "s"}`]);
    if (t[1]) p.push([t[1], `root${Math.abs(t[1]) === 1 ? "" : "s"}`]);
    if (t[2]) p.push([t[2], ""]);
    if (!p.length) return "0";
    return p.map(([v, w], i) => (i === 0 ? (v < 0 ? "−" : "") : (v < 0 ? " − " : " + ")) + Math.abs(v) + (w ? " " + w : "")).join("");
  };
  const fmtX = v => Math.abs(v - Math.round(v)) < 1e-12 ? String(Math.round(v)) : v.toPrecision(10).replace(/0+$/, "");
  let plan, at;
  function makePlan() {
    const L = inputs[0].map(i => Math.round(+i.value || 0)), R = inputs[1].map(i => Math.round(+i.value || 0));
    const out = [[`Start: <b>${side(L)} = ${side(R)}</b>`, null]];
    for (let i = 0; i < 3; i++) { if (L[i] < 0) { R[i] -= L[i]; L[i] = 0; } if (R[i] < 0) { L[i] -= R[i]; R[i] = 0; } }
    out.push([`<i>Al-jabr</i>, restoring: move every subtracted term to the other side. <b>${side(L)} = ${side(R)}</b>`, null]);
    for (let i = 0; i < 3; i++) { const m = Math.min(L[i], R[i]); L[i] -= m; R[i] -= m; }
    out.push([`<i>Al-muqabala</i>, balancing: cancel like terms on both sides. <b>${side(L)} = ${side(R)}</b>`, null]);
    let sq = L[0] - R[0], rt = L[1] - R[1], un = L[2] - R[2];
    if (sq < 0 || (sq === 0 && rt < 0)) { sq = -sq; rt = -rt; un = -un; }
    if (sq === 0 && rt === 0) { out.push(["Nothing is left: every number fits, or none does.", null]); return out; }
    const b = sq ? F(Math.abs(rt), sq) : F(Math.abs(rt)), c = sq ? F(Math.abs(un), sq) : F(Math.abs(un));
    if (sq > 1) out.push([`Divide by ${sq}, the number of squares, to leave one square.`, null]);
    const half = F(b[0], b[1] * 2), sqh = F(half[0] * half[0], half[1] * half[1]);
    const add = (p, q) => F(p[0] * q[1] + q[0] * p[1], p[1] * q[1]), sub = (p, q) => F(p[0] * q[1] - q[0] * p[1], p[1] * q[1]);
    if (sq === 0) { const x = -un / rt; out.push([`Type 3, <b>roots equal numbers</b>: x = ${fmtX(Math.abs(un) / Math.abs(rt))}${x > 0 ? "" : ", but the signs leave no positive answer"}.`, null]); return out; }
    if (rt === 0) { out.push([un < 0 ? `Type 2, <b>squares equal numbers</b>: x is the root of ${fs(c)}: <b>x = ${fmtX(Math.sqrt(fv(c)))}</b>.` : "Squares and a number on one side, nothing on the other: no positive answer.", null]); return out; }
    if (un === 0) { out.push([rt < 0 ? `Type 1, <b>squares equal roots</b>: x = <b>${fs(b)}</b>.` : "Squares and roots on one side: no positive answer.", null]); return out; }
    if (rt > 0 && un < 0) {
      const tot = add(sqh, c), x = Math.sqrt(fv(tot)) - fv(half);
      out.push([`Type 4, <b>squares and roots equal numbers</b>: halve the roots, ${fs(half)}; square it, ${fs(sqh)}; add the number, ${fs(tot)}; take its root, ${fmtX(Math.sqrt(fv(tot)))}; take away half the roots: <b>x = ${fmtX(x)}</b>.`, { half: fv(half), x }]);
    } else if (rt < 0 && un > 0) {
      const disc = sub(sqh, c);
      if (disc[0] < 0) out.push([`Type 5, <b>squares and numbers equal roots</b>: halve the roots, ${fs(half)}; square it, ${fs(sqh)}; it is smaller than the number ${fs(c)}, so the problem is impossible.`, null]);
      else { const r = Math.sqrt(fv(disc)); out.push([`Type 5, <b>squares and numbers equal roots</b>: halve the roots, ${fs(half)}; square it, ${fs(sqh)}; take away the number, ${fs(disc)}; its root ${fmtX(r)} taken from or added to half the roots: <b>x = ${fmtX(fv(half) - r)}${r ? " or " + fmtX(fv(half) + r) : ""}</b>.`, null]); }
    } else if (rt < 0 && un < 0) {
      const tot = add(sqh, c), x = Math.sqrt(fv(tot)) + fv(half);
      out.push([`Type 6, <b>roots and numbers equal squares</b>: halve the roots, ${fs(half)}; square it, ${fs(sqh)}; add the number, ${fs(tot)}; take its root, ${fmtX(Math.sqrt(fv(tot)))}; add half the roots: <b>x = ${fmtX(x)}</b>.`, null]);
    } else out.push(["Every term is on one side: no positive answer.", null]);
    return out;
  }
  function figure(f) {
    const svg = document.getElementById("aj-fig");
    svg.innerHTML = "";
    if (!f) { sv("text", { x: 180, y: 128, "text-anchor": "middle", fill: "var(--muted)", "font-size": 12 }, svg, "The picture appears for type 4, as in al-Khwarizmi's book."); return; }
    const s = 200 / (f.x + f.half), X = f.x * s, H = f.half * s, x0 = 60, y0 = 30;
    const R = (x, y, w, h, fill, stroke, dash) => sv("rect", { x, y, width: w, height: h, fill, stroke, "stroke-width": 2, "stroke-dasharray": dash || null }, svg);
    R(x0, y0, X, X, "var(--surface)", "var(--ink)"); R(x0 + X, y0, H, X, "var(--wash)", "var(--blue)"); R(x0, y0 + X, X, H, "var(--wash)", "var(--blue)");
    R(x0 + X, y0 + X, H, H, "none", "var(--red)", "6 4");
    const T = (x, y, t, c) => sv("text", { x, y, "text-anchor": "middle", fill: c, "font-size": 12, "font-weight": 700 }, svg, t);
    T(x0 + X / 2, y0 + X / 2 + 4, "x²", "var(--ink)"); T(x0 + X + H / 2, y0 + X / 2 + 4, `${fmtX(f.half)}x`, "var(--blue)");
    T(x0 + X / 2, y0 + X + H / 2 + 4, `${fmtX(f.half)}x`, "var(--blue)"); T(x0 + X + H / 2, y0 + X + H / 2 + 4, fmtX(f.half * f.half), "var(--red)");
    T(x0 + X / 2, y0 - 8, `x = ${fmtX(f.x)}`, "var(--muted)"); T(x0 + X + H / 2, y0 - 8, fmtX(f.half), "var(--muted)");
  }
  function reset() { plan = makePlan(); at = 0; render(); }
  function render() {
    const ol = document.getElementById("aj-steps");
    ol.innerHTML = "";
    plan.slice(0, at + 1).forEach(([t]) => { el("li", {}, ol).innerHTML = t; });
    figure(at === plan.length - 1 ? plan[at][1] : null);
  }
  document.getElementById("aj-next").addEventListener("click", () => { if (at < plan.length - 1) { at++; render(); } });
  document.getElementById("aj-all").addEventListener("click", () => { at = plan.length - 1; render(); });
  document.getElementById("aj-reset").addEventListener("click", reset);
  inputs.flat().forEach(i => i.addEventListener("change", reset));
  set([-1, 10, 0], [0, 4, 9]);
  set([1, 10, 0], [0, 0, 39]);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 650, "How al-Khwarizmi's two books combined older ideas, and where his name went")
    W, H = 210, 86
    nodes = {
        "zero": (20, 20, "Indian numerals with zero", "", "topic 4", "ink"),
        "euc": (395, 20, "Euclid, Elements II", "areas that complete a square", "influence disputed", "ink"),
        "ind": (770, 20, "Indian rules", "the rule of three, rhetorical style", "influence disputed", "ink"),
        "alg": (20, 170, "Algorism", "⊕ written step-by-step arithmetic", "c. 825 (estimate)", "red"),
        "jab": (580, 170, "Al-jabr", "⊕ six types, a recipe for each", "c. 820 (estimate)", "red"),
        "lat": (20, 330, "Dixit Algorizmi", "Latin algorisms", "12th–13th century", "ink"),
        "fib": (20, 480, "Liber Abaci", "the numerals reach Pisa", "1202, topic 8", "ink"),
        "word": (395, 330, "The word algorithm", "from his name", "", "ink"),
        "for": (770, 330, "Forsythe's pitfall", "⊕ rearrange to avoid cancellation", "1970", "blue"),
        "urg": (395, 480, "Urgench symposium", "algorithms, in the land of his name", "1979; Ershov and Knuth", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("zero", "alg", ports=("bottom", "top"))
    D.edge("euc", "jab", ports=("bottom", "top:0.3"), dashed=True)
    D.edge("ind", "jab", ports=("bottom", "top:0.8"), dashed=True)
    D.edge("alg", "lat", ports=("bottom", "top"))
    D.edge("lat", "fib", ports=("bottom", "top"))
    D.edge("lat", "word", ports=("right", "left"))
    D.edge("jab", "for", ports=("bottom:0.8", "top:0.4"))
    D.edge("word", "urg", ports=("bottom", "top"))
    D.text(20, 625, "Dashed: sources argued over by historians (Toomer and Rashed for Euclid; Gandz against; Toomer for Indian influence).", "caption")
    return D


def chain(d):
    rnd = d["random"]
    big = d["float"][-1]
    steps = [
        ("Indian numerals reached Baghdad, but the ways of computing with them still had to be written out",
         "A written, step-by-step arithmetic: the algorism, with square roots digit by digit", "al-Khwarizmi, c. 825"),
        ("Practical problems led to quadratic equations, each solved as a special case",
         f"Al-jabr and al-muqabala reduce any problem to one of six types, each with a recipe: {rnd['sorted']:,} random equations, all solved", "al-Khwarizmi, c. 820"),
        ("A recipe in words has to be believed: why does adding 25 work?",
         "A picture: the square with its two strips lacks a corner of 25", "completing the square"),
        (f"In floating point, the recipe can lose the small root completely: x² + 1 = {big['big']}x gives {big['recipe']}",
         f"Rearrange: the small root is 1 divided by the large one, {big['stable']}", "Forsythe, 1970"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from written numerals to a floating-point pitfall")
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
    ex, rnd, red, sq, fl = d["examples"], d["random"], d["reduce"], d["sqrt"], d["float"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Indian numerals with a zero (topic 4) needed written methods; quadratic problems needed a general procedure. Al-Khwarizmi wrote both down, in two books, and his name became the word for what they contain. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the two books. Blue: a pitfall that computers met in his recipe, and the symposium that brought algorithms back to the land of his name."),
        ]),
        dict(id="jabr", eyebrow="Try it", title="Restore, balance, and follow the recipe", toc="Try it", blocks=[
            dict(type="p", text="Write an equation as squares, roots and units on each side; a negative count means a subtracted term. **Next step** applies *al-jabr* (move subtracted terms across), then *al-muqabala* (cancel like terms), then sorts the equation into one of the six types and follows its recipe in words. For type 4 the picture shows the square being completed."),
            dict(type="widget", html=AJ_HTML, js=AJ_JS, css=AJ_CSS,
                 fallback=dict(type="svg", name="square", draw=square_svg(d), alt="Completing the square for x² + 10x = 39", width=760),
                 note="In the interactive edition you can enter any equation and watch al-jabr, al-muqabala and the recipe solve it."),
            dict(type="table", head=["Al-Khwarizmi's example", "Type", "Recipe", "Answer"], num=[],
                 rows=[[e["words"].capitalize(), f"{e['type']}: {e['tname']}", e["recipe"].capitalize(), e["x"]] for e in ex]),
            dict(type="p", text=f"A reduction from scratch: {red['eq'].replace(' - ', ' − ')}. *Al-jabr* gives {red['jabr']}; *al-muqabala* gives {red['muq']}; the recipe of type 5 ({red['recipe']}) gives **x = {red['x']}**."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="six", eyebrow="How it works", title="Six types, six recipes", toc="Six types", blocks=[
            dict(type="p", text="After restoring and balancing, and dividing by the number of squares, every linear or quadratic problem with a positive answer is one of six types: (1) squares equal roots, (2) squares equal numbers, (3) roots equal numbers, (4) squares and roots equal numbers, (5) squares and numbers equal roots, (6) roots and numbers equal squares. The first three need one division or one root. The three mixed types are solved by halving the roots and completing the square."),
            dict(type="table", head=["Type", "Random equations sorted into it"], num=[1],
                 rows=[[f"{i + 1}. {n}", f"{c:,}"] for i, (n, c) in enumerate(rnd["types"])]),
            dict(type="p", text=f"The program wrote {rnd['n']:,} random equations with terms subtracted on both sides, reduced each by *al-jabr* and *al-muqabala*, sorted it, and solved it by the recipe. {rnd['sorted']:,} fell into the six types, and every answer matched the modern quadratic formula. Another {rnd['oneside']:,} ended with every term on one side, which has no positive answer, and {rnd['none']} cancelled away entirely. The three mixed types are about equally common, and so are the three simple ones, because the type depends only on which reduced terms are left and on which side."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Two moves turn any problem into a standard form, and a standard form has a fixed recipe. That is what made the book an algorithm, even with no symbols: the reader never has to be clever, only to follow the steps."),
        ]),
        dict(id="algorism", eyebrow="The other book", title="Algorism: arithmetic written out", toc="Algorism", blocks=[
            dict(type="p", text="Al-Khwarizmi's second book taught the Indian place-value numerals, with nine figures and a sign for an empty place, and step-by-step written rules for each operation, for fractions and for square roots. Its Arabic original is lost. A Latin copy at Cambridge, of the 13th century, begins \"Dixit Algorizmi\" (\"al-Khwarizmi said\"), and from such copies came the word *algorism*, later *algorithm*."),
            dict(type="p", text=f"Written square roots come out one digit at a time: bring down two digits, find the largest next digit that fits, subtract, repeat. The program computed {sq['digits']} digits of √2 this way in **{sq['dsteps']} steps**, trying {sq['trials']} candidate digits in all: {sq['value']} The Babylonian averaging of Era 1, topic 4, doubles the correct digits at each step and got there in **{sq['avg']} steps**, but each of its steps is a full long division."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two books, one name, many arguments", toc="The evidence", blocks=[
            dict(type="p", text="Al-Khwarizmi lived about 780 to about 850 and worked at the House of Wisdom in Baghdad under the caliph al-Ma'mun, to whom he dedicated the algebra (**documented**). No source gives a firm year for the algebra: estimates run from 813 to 833, often about 820 (**conjecture**). The arithmetic cites the algebra, so it came later (**documented**). Its Latin text survives in only two copies, Cambridge University Library MS Ii.6.5 (the first half only) and New York, Hispanic Society of America, HC 397/726 (**documented**); its attribution to Adelard of Bath is a **conjecture**."),
            dict(type="p", text="Where he came from is itself argued over. His name may mean that he or his ancestors came from Khwarizm, south of the Aral Sea; Rashed reads the key source differently (**disputed**). Where his algebra came from is **disputed**: Toomer and Rashed see Book II of Euclid's *Elements* behind the geometric proofs, Gandz says the *Elements* were unknown to him, and Toomer also argues for Indian influence. How original he was is **disputed** too. Rashed calls the originality \"impossible to overstress\"; Toomer judged his achievements \"at best mediocre, but ... uncommonly influential\"."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The recipe in floating point", toc="Measured", blocks=[
            dict(type="table", head=["Equation", "Small root by the recipe", "Rearranged", "Recipe's error"], num=[3],
                 rows=[[f"x² + 1 = {f['big']}x", f["recipe"], f["stable"], f"{f['err']:.1e} of the answer"] for f in fl]),
            dict(type="p", text=f"For squares and numbers equal roots, the small root is half the roots minus a root that is almost exactly as big. Subtracting two nearly equal numbers throws away their shared digits. George Forsythe used this very example in 1970 (\"Pitfalls in computation, or why a math book isn't enough\"): the formula gives one root well and the other \"100 percent wrong\". The fix is to compute the large root by the recipe and the small one from it, since their product is the number: here, 1 divided by the large root. With {fl[-1]['big']} the recipe returns **{fl[-1]['recipe']}** and the rearranged form {fl[-1]['stable']}."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Algorithms come home", toc="Full circle", blocks=[
            dict(type="p", text="In September 1979 the Academy of Sciences of the Uzbek SSR organized a symposium in Urgench, \"Algorithms in modern mathematics and computer science\". Its proceedings, edited by Andrei Ershov and Donald Knuth, appeared in 1981 as volume 122 of Springer's *Lecture Notes in Computer Science*. Urgench is the capital of the Xorazm region, the old Khwarizm, and a large statue of al-Khwarizmi stands in the city."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="A Latin copyist's \"Dixit Algorizmi\", \"al-Khwarizmi said\", became the name of a whole science. Eleven and a half centuries after he wrote, computer scientists, Knuth among them, met in the land his name points to, to discuss algorithms."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Solve a square and 6 roots equal 16 by the recipe.", "Half the roots 3; squared 9; add 16: 25; root 5; take away 3: **x = 2**. Check: 4 + 12 = 16."),
            ("Why does type 5 sometimes give two answers?", "x² + 21 = 10x is true for x = 3 and x = 7: half the roots, 5, plus or minus the root of 25 − 21 = 4."),
            ("What does al-jabr do to 10 roots minus a square = 4 roots and 9?", "It restores the subtracted square by adding it to both sides: 10 roots = a square and 4 roots and 9."),
            ("Why does the recipe for x² + 1 = 10⁹x return 0 for the small root in floating point?",
             "Half the roots is 500,000,000 and the root of its square minus 1 rounds to exactly the same number, so the subtraction leaves 0."),
            ("Where does the word 'algorithm' come from?", "From al-Khwarizmi's name, through Latin copies of his arithmetic that begin \"Dixit Algorizmi\"; 'algebra' comes from al-jabr in the title of his other book."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Cambridge University Library, MS Ii.6.5", text="A 13th-century Latin copy of the arithmetic, the first half only: one of the two known copies. Fully digitized.",
                 draw=C.draw_manuscript, link="https://cudl.lib.cam.ac.uk/view/MS-II-00006-00005/1", link_text="Cambridge Digital Library",
                 licence="Drawn placeholder; the digitized pages are on the library's site."),
            dict(title="The Algebra of Mohammed ben Musa, 1831", text="Frederic Rosen's edition and English translation of the algebra, with the six types and the completed squares.",
                 draw=C.draw_book, link="https://archive.org/details/algebraofmohamme00khuwuoft/algebraofmohamme00khuwuoft", link_text="Internet Archive scan",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Pitfalls in Computation, or Why a Math Book Isn't Enough", "George E. Forsythe, Stanford CS Technical Report 147, January 1970", "https://apps.dtic.mil/sti/pdfs/AD0699897.pdf", "The quadratic formula's catastrophic cancellation, and formulas that avoid it"),
            ("scholar", "Algorithms in modern mathematics and computer science: proceedings, Urgench, Uzbek SSR, September 16–22, 1979", "A. P. Ershov and D. E. Knuth (eds.), LNCS 122, Springer, 1981 (CiNii record)", "https://ci.nii.ac.jp/ncid/BA02973768", "The symposium on algorithms held in Urgench"),
            ("start", "Urgench", "Wikipedia", "https://en.wikipedia.org/wiki/Urgench", "Capital of the Xorazm region, with a large statue of al-Khwarizmi"),
        ]),
        C.prove_it_section(ctx, "AlKhwarizmi", d["checks"],
                           "the three worked examples, 100,000 random equations reduced by al-jabr and al-muqabala and solved by the recipes against the quadratic formula, the digit-by-digit square root against averaging, and Forsythe's floating-point example.",
                           ["static double[] solve("]),
    ]
    return dict(
        title="Algorism and Al-Jabr", date="c. 820–830 CE",
        description="Era 2, topic 6 of The Algorithm Evolution Atlas: al-Khwarizmi's written arithmetic and his algebra of six types, with an al-jabr machine and completing the square.",
        lede="Restore the subtracted terms, balance the like ones, and every problem falls into one of six types with a fixed recipe. Al-Khwarizmi wrote it without a single symbol, and his name became the word algorithm.",
        fieldnote="In Baghdad I found the man whose name became the word for what I study. One of his books teaches the Indian way of writing numbers and computing with them; the other sorts every quadratic problem into six forms with a recipe for each. His species disagrees about whether he was original. Nobody disputes that he was copied.",
        card=[("When", "c. 820–830 CE (**conjecture**: no firm year); the arithmetic after the algebra"),
              ("Where", "Baghdad, the House of Wisdom"),
              ("What hurt", "Indian numerals needed written methods; quadratic problems were solved case by case"),
              ("The fix", "Written step-by-step arithmetic; al-jabr, al-muqabala and six recipes"),
              ("Cost", f"Two moves and one recipe per problem; {rnd['sorted']:,} random equations solved, every one right")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AlKhwarizmi.java`.",
    )
