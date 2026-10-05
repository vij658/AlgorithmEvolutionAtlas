"""Era 1, topic 4: the square root of 2 on YBC 7289. Every number is parsed from SquareRootOfTwo.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"iter": [], "method": []}
    for ln in text.splitlines():
        if m := re.match(r"tablet: 1;24,51,10 = ([\d.]+)\.\.\. ; sqrt\(2\) = ([\d.]+)\.\.\. ; error (\S+) ;", ln):
            d["tablet"], d["sqrt2"], d["error"] = m.group(1), m.group(2), m.group(3)
        elif m := re.match(r"tablet-places: (\d+) correct decimal places; square of the tablet value = ([\d.]+)", ln):
            d["tablet_places"], d["tablet_sq"] = int(m.group(1)), m.group(2)
        elif m := re.match(r"sqrt2 in base 60: ([\d;,]+),\.\.\.", ln):
            d["sqrt2_60"] = m.group(1)
        elif m := re.match(r"iterate (\d+): (\S+) = ([\d.]+) ; correct places (\d+)(?: ; three base-60 places cut ([\d;,]+) rounded ([\d;,]+) ; convergent (\d+))?", ln):
            d["iter"].append(dict(k=int(m.group(1)), frac=m.group(2), value=m.group(3), places=int(m.group(4)), cut=m.group(5), rounded=m.group(6),
                                  conv=int(m.group(7)) if m.group(7) else 0))
        elif m := re.match(r"method (\d+) digits: halving=(\d+) digit-by-digit=(\d+) averaging=(\d+)$", ln):
            d["method"].append(tuple(int(m.group(i)) for i in range(1, 5)))
        elif m := re.match(r"heron: .* average = 26 5/6 = (\S+) ; its square is 720 1/36", ln):
            d["heron"] = m.group(1)
        elif m := re.match(r"invsqrt: .* in (\d+) steps", ln):
            d["invsqrt"] = int(m.group(1))
        elif m := re.match(r"quake: (\d+) floats from 1 to 4; bit-trick guess worst relative error ([\d.]+)%, after one Newton step ([\d.]+)%", ln):
            d["quake"] = dict(n=int(m.group(1)), guess=float(m.group(2)), step=float(m.group(3)))
    d["checks"] = C.checks(text)
    return d


def tablet_drawing(t, standalone):
    """YBC 7289 redrawn: a round tablet, a tilted square with both diagonals, the numbers in modern notation."""
    b = [f'<ellipse cx="160" cy="150" rx="140" ry="132" style="fill:{t["wash"]};stroke:{t["ink2"]};stroke-width:1.5"/>',
         C.path("M160,40 L270,150 L160,260 L50,150 Z", t["ink"], "none", 2.2),
         C.line(50, 150, 270, 150, t["red"], 2.2), C.line(160, 40, 160, 260, t["ink2"], 1.4),
         C.text(92, 88, "30", t["ink"], 16, "middle", 700),
         C.text(160, 142, "1;24,51,10", t["red"], 15, "middle", 700),
         C.text(160, 172, "42;25,35", t["blue"], 15, "middle", 700)]
    return C.svg_doc(320, 300, "".join(b), "YBC 7289 redrawn: a square of side 30 with the diagonal marked 1;24,51,10 and 42;25,35",
                     t, standalone, 0.5, 360)


def squares_figure(d):
    """The first iterates as rectangles of area 2: g by 2/g, drawn to scale; the square of side sqrt 2 dashed."""
    its = d["iter"][:4]

    def draw(t, standalone):
        u = 90
        out = []
        for i, it in enumerate(its):
            g = float(it["value"])
            w, h = g * u, 2 / g * u
            x0, y0 = 30 + i * 230, 230
            s = 2 ** 0.5 * u
            out.append(C.rect(x0, y0 - s, s, s, "none", t["axis"], 1.5, extra=";stroke-dasharray:4 4"))
            out.append(C.rect(x0, y0 - h, w, h, t["wash"], t["red"] if i == 3 else t["ink"], 2))
            out.append(C.text(x0, y0 + 22, f"guess {it['frac']}", t["ink"], 13, weight=700))
            out.append(C.text(x0, y0 + 40, f"{it['places']} correct places", t["muted"], 12))
        out.append(C.text(30, 22, "Each rectangle has area 2: one side is the guess g, the other 2/g. Averaging the sides squares it up.", t["ink2"], 13))
        return C.svg_doc(940, 280, "".join(out), "Four guesses for the square root of 2 drawn as rectangles of area 2", t, standalone, 0.6)
    return draw


AVG_HTML = """
<div class="board avg-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="av-n">Square root of <input id="av-n" type="number" min="2" max="1000000" value="2" inputmode="numeric"></label>
      <label for="av-g">first guess <input id="av-g" type="number" min="0.001" step="any" value="1" inputmode="decimal"></label>
      <button id="av-step" class="primary" type="button">Average</button>
      <button id="av-reset" type="button">Reset</button>
    </div>
    <svg id="av-svg" viewBox="0 0 520 300" role="img" aria-label="The guess as a rectangle of the right area, squaring up"></svg>
    <p class="zoomnote" id="av-note"></p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The guesses</div>
    <ol class="steps" id="av-steps"></ol>
  </div>
</div>
"""

AVG_JS = r"""
(() => {
  const svg = document.getElementById("av-svg");
  if (!svg) return;
  let N = 2, guesses = [1];
  const base60 = x => { let w = Math.floor(x), f = x - w, d = []; for (let i = 0; i < 3; i++) { f *= 60; const k = Math.floor(f + 1e-12); d.push(k); f -= k; } return w + ";" + d.join(","); };
  const correct = x => { const e = Math.abs(x - Math.sqrt(N)); return e === 0 ? "all" : Math.max(0, Math.floor(-Math.log10(e))); };
  function draw() {
    svg.innerHTML = "";
    const g = guesses[guesses.length - 1], other = N / g, r = Math.sqrt(N);
    const big = Math.max(g, other, r), scale = 240 / big;
    const x0 = 40, y0 = 270;
    sv("rect", {x: x0, y: y0 - r * scale, width: r * scale, height: r * scale, fill: "none", stroke: "var(--axis)", "stroke-dasharray": "5 4", "stroke-width": 1.5}, svg);
    sv("rect", {x: x0, y: y0 - other * scale, width: g * scale, height: other * scale, fill: "var(--wash)", stroke: "var(--red)", "stroke-width": 2.5}, svg);
    sv("text", {x: x0 + g * scale / 2, y: y0 + 20, "text-anchor": "middle", fill: "var(--ink)", "font-size": 13, "font-weight": 700}, svg, `g = ${+g.toPrecision(8)}`);
    sv("text", {x: x0 + g * scale + 8, y: y0 - other * scale / 2, fill: "var(--ink)", "font-size": 13, "font-weight": 700}, svg, `${fmt(N)}/g = ${+other.toPrecision(8)}`);
    sv("text", {x: 500, y: 24, "text-anchor": "end", fill: "var(--muted)", "font-size": 12}, svg, `dashed: the square of area ${fmt(N)}`);
    const steps = document.getElementById("av-steps");
    steps.innerHTML = "";
    guesses.forEach((x, i) => {
      el("li", {class: i === guesses.length - 1 ? "current" : ""}, steps, `${i}: ${x.toPrecision(16)}  (${correct(x)} places; base 60 ${base60(x)})`);
    });
    document.getElementById("av-note").textContent = guesses.length > 1
      ? `g and ${fmt(N)}/g always sit on opposite sides of the root, so their average is closer. The page computes in ordinary floating point, so it stops at about 16 digits.`
      : "Press Average: the new guess is the average of the two sides.";
  }
  function reset() {
    N = Math.max(2, Math.floor(+document.getElementById("av-n").value || 2));
    const g0 = +document.getElementById("av-g").value;
    guesses = [g0 > 0 ? g0 : 1]; draw();
  }
  document.getElementById("av-step").addEventListener("click", () => {
    const g = guesses[guesses.length - 1], next = (g + N / g) / 2;
    if (guesses.length < 12 && next !== g) guesses.push(next);
    draw();
  });
  document.getElementById("av-reset").addEventListener("click", reset);
  ["av-n", "av-g"].forEach(id => document.getElementById(id).addEventListener("change", reset));
  draw();
})();
"""

AVG_CSS = """
.avg-board svg{background:var(--wash)}
.avg-board .controls input{width:7em}
.avg-board .steps li{font-size:12.5px;white-space:normal}
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 650, "How the square root of 2 combined with other ideas, from place value to the fast inverse square root")
    W, H = 210, 86
    nodes = {
        "pv": (180, 20, "Base-60 place value", "", "topic 3", "ink"),
        "rt": (610, 20, "Reciprocal tables", "", "topic 3", "ink"),
        "yb": (180, 160, "√2 to three places", "⊕ a value no ruler gives", "YBC 7289, c. 1800–1600 BCE", "red"),
        "hr": (610, 160, "Averaging g and N/g", "⊕ a rule to improve a guess", "Heron's Metrica, 1st century CE", "red"),
        "ar": (180, 300, "Bounds for √3", "⊕ squeezing from both sides", "Archimedes, topic 8", "ink"),
        "cf": (610, 300, "Continued fractions", "same guesses: 3/2, 17/12, 577/408", "", "ink"),
        "nw": (395, 420, "Newton's method", "⊕ any equation f(x) = 0", "17th century", "blue"),
        "qk": (180, 540, "Fast inverse square root", "⊕ a bit-trick first guess", "Quake III Arena source", "blue"),
        "hp": (610, 540, "Millions of digits", "⊕ fast multiplication", "today's big-number libraries", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("pv", "yb", ports=("bottom", "top"))
    D.edge("rt", "hr", ports=("bottom", "top"))
    D.edge("yb", "hr", ports=("right", "left"), dashed=True, label="disputed", dy=-8)
    D.edge("yb", "ar", ports=("bottom", "top"))
    D.edge("hr", "cf", ports=("bottom", "top"), dashed=True)
    D.edge("hr", "nw", ports=("bottom", "top"))
    D.edge("nw", "qk", ports=("bottom", "top"))
    D.edge("nw", "hp", ports=("bottom", "top"))
    return D


def chain(d):
    m1000 = next(m for m in d["method"] if m[0] == 1000)
    steps = [
        ("The diagonal of a square cannot be measured exactly", f"Compute it: 1;24,51,10, right to {d['tablet_places']} decimal places", "YBC 7289, c. 1800–1600 BCE"),
        ("A single guess is always too big or too small", "Average a guess g with N/g: they lie on opposite sides of the root", "Heron, 1st century CE"),
        ("Every step needs a division", "Iterate on 1/√N instead: multiplications only", "a modern variant"),
        (f"Halving the interval needs {m1000[1]:,} steps for 1,000 digits", f"Averaging doubles the correct digits: {m1000[3]} steps", ""),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from measuring to computing roots")
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


def iterates(d):
    its = d["iter"][:5]
    D = Diagram(1000, 230, "Averaging from the guess 1: each step roughly doubles the correct digits")
    for i, it in enumerate(its):
        frac = it["frac"] if len(it["frac"]) < 16 else it["frac"].split("/")[0][:6] + "…"
        lines = [(frac, "title"), (it["value"][:12], "combo"), (f"{it['places']} correct places", "note")]
        D.node(i, 20 + i * 196, 50, 156, 96, lines, color="red" if i == 3 else "ink")
        if i:
            D.edge(i - 1, i, ports=("right", "left"))
    D.text(20, 30, "THE GUESSES, AS EXACT FRACTIONS; EACH ARROW AVERAGES g AND 2/g", "tag")
    t = d["iter"][3]
    D.text(20, 186, f"{t['frac']} cut to three base-60 places is {t['cut']}, the tablet's value; rounded, it would be {t['rounded']}.", "caption")
    D.text(20, 208, "Every guess is a continued-fraction convergent of √2, and p² − 2q² = 1 for each one.", "caption")
    return D


def readings():
    D = Diagram(1000, 330, "How did the scribe get 1;24,51,10? Four answers")
    D.node("t", 330, 20, 340, 84, [("The tablet", "title"), ("side 30; diagonal 1;24,51,10 and 42;25,35", "combo"), ("documented: YBC 7289", "note")])
    boxes = [("cp", 20, "Copied from a list", "of standard coefficients", "Fowler and Robson, 1998"),
             ("cut", 265, "Cut and paste", "a geometric step, equal to one averaging step", "Fowler and Robson, 1998"),
             ("av", 510, "Repeated averaging", "reaches it at the third new guess", "possible, not shown (Baez)"),
             ("bk", 755, "Another route", "a different reconstruction", "Buckle, 2023")]
    for k, x, t, combo, who in boxes:
        D.node(k, x, 200, 225, 92, [(t, "title"), (combo, "combo"), (who, "note")], color="blue")
        D.edge("t", k, ports=("bottom", "top"))
    D.text(500, 318, "THE METHOD IS DISPUTED; THE VALUE AND ITS ARITHMETIC ARE NOT", "tag", "middle")
    return D


def three_ways(d):
    D = Diagram(1000, 200, "Three ways to the digits of a square root")
    m = {x[0]: x for x in d["method"]}
    boxes = [("h", "Halve the interval", "about 3.3 steps per decimal digit", f"1,000 digits: {m[1000][1]:,} steps"),
             ("dd", "Digit by digit", "one digit per step, as taught in schools", f"1,000 digits: {m[1000][2]:,} steps"),
             ("av", "Average g and N/g", "the correct digits double each step", f"1,000 digits: {m[1000][3]} steps")]
    for i, (k, t, combo, n) in enumerate(boxes):
        D.node(k, 20 + i * 330, 50, 290, 110, [(t, "title"), (combo, "combo"), (n, "note")], color="red" if k == "av" else "ink")
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "FASTER TO THE RIGHT, FOR THE SAME ANSWER", "tag")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    it3 = d["iter"][3]
    q = d["quake"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Base-60 place value (topic 3) made a value like 1;24,51,10 writable; a rule that improves any guess made it computable. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the tablet's value and the averaging rule. Blue: what the rule became. The dashed arrow from the tablet to Heron is disputed: nobody knows that the scribe averaged."),
        ]),
        dict(id="avg", eyebrow="Try it", title="Square up a rectangle", toc="Try it", blocks=[
            dict(type="p", text="To find the square root of N, start with any guess g. A rectangle with sides g and N/g has area N. If g is too small, N/g is too big, and the other way round, so the average of the two sides is a better guess. Repeat."),
            dict(type="widget", html=AVG_HTML, js=AVG_JS, css=AVG_CSS,
                 fallback=dict(type="svg", name="squares", draw=squares_figure(d), alt="Four guesses for the square root of 2 drawn as rectangles of area 2"),
                 note="In the interactive edition you can average your way to the square root of any number."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="tablet", eyebrow="The evidence", title="A student's tablet, 3,800 years old", toc="The evidence", blocks=[
            dict(type="p", text="YBC 7289 is a small round school tablet in the Yale Babylonian Collection. It shows a square with its diagonals. One side is marked 30. Along the diagonal are two base-60 numbers: 1;24,51,10, which is √2, and 42;25,35, which is 30 × √2, the length of this diagonal."),
            dict(type="svg", name="tablet", draw=tablet_drawing, alt="YBC 7289 redrawn", width=360,
                 caption="Redrawn for this book, with the numbers in modern notation. It is not a copy of the tablet."),
            dict(type="table", head=["", "Value", "Notes"], num=[],
                 rows=[["The tablet: 1;24,51,10", d["tablet"] + "…", f"{d['tablet_places']} correct decimal places; its square is {d['tablet_sq']}…"],
                       ["√2", d["sqrt2"] + "…", f"in base 60: {d['sqrt2_60']},…"],
                       ["Difference", d["error"], "smaller than any measurement could detect"],
                       ["30 × 1;24,51,10", "42;25,35", "exactly, as the program checks"]]),
            dict(type="diagram", name="readings", diagram=readings(),
                 caption="Fowler and Robson (1998) is the standard study. Repeated averaging reaching the tablet's value shows the method is possible, not that it was used."),
        ]),
        dict(id="steps", eyebrow="Step by step", title="Averaging from the guess 1", toc="Step by step", blocks=[
            dict(type="diagram", name="iterates", diagram=iterates(d)),
            dict(type="table", head=["Step", "Guess (exact)", "Value", "Correct places", "Three base-60 places, cut", "Rounded"], num=[0, 3],
                 hl=3, rows=[[it["k"], it["frac"], it["value"], it["places"], it["cut"] or "—", it["rounded"] or "—"] for it in d["iter"]]),
            dict(type="callout", kind="wrong", label="Careful",
                 text=f"The third new guess, {it3['frac']}, gives the tablet's digits only if you cut it off after three base-60 places: rounded, it is {it3['rounded']}. "
                      "Whether the scribe cut, rounded, or never averaged at all is part of the dispute."),
            dict(type="callout", kind="key", label="Key idea",
                 text=f"Heron wrote the rule down in his *Metrica* (1st century CE) for √720: 720 is not a square, the next square is 729 = 27², so divide 720 by 27 and average. "
                      f"The program repeats it: 720/27 = 26 2/3, and the average is 26 5/6 = {d['heron']}, whose square is 720 1/36."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How fast does it get there?", toc="Measured", blocks=[
            dict(type="diagram", name="threeways", diagram=three_ways(d)),
            dict(type="table", head=["Correct digits wanted", "Halving the interval", "Digit by digit", "Averaging (Heron, Newton)"], num=[0, 1, 2, 3],
                 hl=len(d["method"]) - 1, rows=[[f"{a:,}", f"{b:,}", f"{c:,}", f"**{e}**"] for a, b, c, e in d["method"]]),
            dict(type="p", text=f"Averaging doubles the correct digits at each step: 1, 2, 5, 11, 24 places for the first guesses. A division-free version, which improves a guess y for 1/√2 by y ← y(3 − 2y²)/2, reaches 15 digits in {d['invsqrt']} steps."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="One averaging step in a video game", toc="Full circle", blocks=[
            dict(type="p", text="The source code of the video game *Quake III Arena*, published by id Software, computes 1/√x with a bit trick for the first guess and then one Newton step, the averaging idea applied to 1/√x. The program checks it on every float from 1 to 4, where the error pattern repeats."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Over {q['n']:,} floats, the bit trick alone is off by at most **{q['guess']}%**. One Newton step cuts that to **{q['step']}%**: the same move that lands on 577/408, 3,800 years later, inside a game loop."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Average 1 and 2/1. Then average the result with 2 divided by it.", "1 and 2 average to **3/2**. Then 2 ÷ 3/2 = 4/3, and the average of 3/2 and 4/3 is **17/12** = 1.41666…"),
            ("Why must g and N/g lie on opposite sides of √N?", "Their product is N. If both were bigger than √N the product would be bigger than N; if both were smaller it would be smaller."),
            ("Check the tablet: is 30 × 1;24,51,10 really 42;25,35?",
             "30 × 1 = 30; 30 × 24/60 = 12; 30 × 51/3600 = 0;25,30; 30 × 10/216000 = 0;0,5. Total: **42;25,35**. The program checks it with exact fractions."),
            ("How many steps does averaging need for 1,000 digits of √2? And halving?",
             "".join(f"**{e}** averaging steps against **{b:,}** halvings." for a, b, c, e in d["method"] if a == 1000)),
            ("Why is 577/408 special besides matching the tablet?", "577² − 2 × 408² = 1, so 577/408 is a solution of Pell's equation, and it is a continued-fraction convergent of √2."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="YBC 7289", text="Old Babylonian school tablet, c. 1800–1600 BCE (sources range from 1900 to 1600). Yale Babylonian Collection.",
                 draw=lambda t, s: tablet_drawing(t, s), link="https://cdli.earth/artifacts/255048", link_text="CDLI record, with transliteration",
                 licence="Drawn for this book; photographs at the link and in Yale's film below."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Heron of Alexandria", "MacTutor History of Mathematics", "https://mathshistory.st-andrews.ac.uk/Biographies/Heron/", "The Metrica's square root of 720, in Heron's words"),
            ("deeper", "q_math.c, Quake III Arena source", "id Software, on GitHub", "https://github.com/id-Software/Quake-III-Arena/blob/master/code/game/q_math.c", "Q_rsqrt: a bit-trick guess and one Newton step"),
        ]),
        C.prove_it_section(ctx, "SquareRootOfTwo", d["checks"],
                           "the tablet's arithmetic with exact fractions, every averaging step against the continued-fraction convergents and Pell's equation, the digits of three methods to 1,000 places, and the Quake III inverse square root on every float from 1 to 4.",
                           ["static Frac average(Frac g, long n)"]),
    ]
    return dict(
        title="The Square Root of Two", date="c. 1800–1600 BCE",
        description="Era 1, topic 4 of The Algorithm Evolution Atlas: the square root of 2 on YBC 7289 and the averaging rule that became Newton's method, with an interactive square-up and verified links.",
        lede="A student wrote the square root of 2 to six decimal places on a clay tablet. No ruler measures that finely: it had to be computed.",
        fieldnote="A student drew a square and its diagonals, wrote 30 on a side and two numbers along the diagonal. How the value was computed is still argued over, 3,800 years later.",
        card=[("When", "c. 1800–1600 BCE (sources range from 1900 to 1600)"),
              ("Where", "Mesopotamia · Yale Babylonian Collection (**documented**)"),
              ("What hurt", "Some lengths, like a square's diagonal, can never be written exactly"),
              ("The fix", "A computed value; later, average g and N/g to improve any guess"),
              ("Cost", "Averaging doubles the correct digits with every step"),
              ("Atlas", "Ch. 1.4 Babylonian square root · Ch. 102 Newton–Raphson")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `SquareRootOfTwo.java`. The tablet is redrawn for this book.",
    )
