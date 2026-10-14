"""Era 5, topic 9: Rosenblatt's perceptron. Every number is parsed from Perceptron.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"cards: .*? last mistake came at card (\d+) \((\d+) mistakes in all\), then (\d+) right in a row ; on ([\d,]+) new cards it was right ([\d,]+) times \(([\d.]+)%\)$", ln):
            d["cards"] = dict(last=m.group(1), mistakes=m.group(2), run=m.group(3), test=m.group(4), right=m.group(5), pct=m.group(6))
        elif m := re.match(r"weights: ([.+\-/]+) \(row by row.*?\) ; (\d+) of the (\d+) strong \+ weights are on the left half, (\d+) of the (\d+) strong - weights on the right", ln):
            d["w"] = dict(rows=m.group(1).split("/"), pl=m.group(2), pc=m.group(3), mr=m.group(4), mc=m.group(5))
        elif ln.startswith("bound: "):
            d["bound"] = re.findall(r"(\d+) dimensions: (\d+) mistakes on average, bound (\d+)", ln)
            d["bn"] = re.search(r"bound: (\d+) random problems", ln).group(1)
        elif m := re.match(r"boolean: .*?: (\d+), (.*?) ; never learned in ([\d,]+) passes: (.*)$", ln):
            d["bool"] = dict(n=m.group(1), learned=m.group(2).split(), passes=m.group(3), not_=m.group(4).split())
        elif m := re.match(r"xor: .*? after (\d+) passes .*? still wrong on (\d+) ; with x AND y as a third input, learned in (\d+) passes: weights (-?\d+), (-?\d+), (-?\d+), bias (-?\d+)$", ln):
            d["xor"] = dict(cycle=m.group(1), wrong=m.group(2), passes=m.group(3), w=(m.group(4), m.group(5), m.group(6)), b=m.group(7))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def weights_svg(d):
    w = d["w"]

    def draw(t, standalone):
        o = []
        s = 16
        x0, y0 = 20, 40
        o.append(C.text(20, 24, "The 400 weights learned from the cards (one square per photocell)", t["ink"], 13, "start", 700))
        for r, row in enumerate(w["rows"]):
            for c, ch in enumerate(row):
                fill = t["red"] if ch == "+" else t["blue"] if ch == "-" else t["surface"]
                o.append(C.rect(x0 + c * s, y0 + r * s, s - 2, s - 2, fill, t["rule"], 0.5, 2))
        o.append(C.line(x0 + 10 * s - 1, y0 - 6, x0 + 10 * s - 1, y0 + 20 * s + 4, t["ink2"], 1.2, ";stroke-dasharray:4 3"))
        lx = x0 + 20 * s + 24
        o.append(C.rect(lx, 60, 16, 16, t["red"]))
        o.append(C.text(lx + 24, 73, "strong weight towards 'left'", t["muted"], 12))
        o.append(C.rect(lx, 88, 16, 16, t["blue"]))
        o.append(C.text(lx + 24, 101, "strong weight towards 'right'", t["muted"], 12))
        o.append(C.rect(lx, 116, 16, 16, t["surface"], t["rule"], 0.5))
        o.append(C.text(lx + 24, 129, "weak", t["muted"], 12))
        o.append(C.text(lx, 170, f"{w['pl']} of {w['pc']} red squares lie on", t["muted"], 12))
        o.append(C.text(lx, 188, f"the left half; {w['mr']} of {w['mc']} blue ones", t["muted"], 12))
        o.append(C.text(lx, 206, "on the right. The rest were learned", t["muted"], 12))
        o.append(C.text(lx, 224, "from specks of dirt.", t["muted"], 12))
        return C.svg_doc(lx + 230, y0 + 20 * s + 16, "".join(o), "The perceptron's learned weights: left half mostly positive, right half mostly negative", t, standalone, 0.5, 640)
    return draw


PC_HTML = """
<div class="board pc-board">
  <div style="min-width:0">
    <div class="eyebrow">Click to add a point: <span id="pc-colour"></span></div>
    <div class="pc-plane" id="pc-plane"></div>
  </div>
  <div style="min-width:0">
    <div class="pc-btns">
      <button type="button" id="pc-yes" aria-pressed="true">add yes (red)</button><button type="button" id="pc-no" aria-pressed="false">add no (blue)</button>
      <button type="button" id="pc-pass">One pass</button><button type="button" id="pc-ten">Ten passes</button>
      <button type="button" id="pc-rand">Random separable set</button><button type="button" id="pc-xor">XOR corners</button><button type="button" id="pc-clear">Clear</button>
    </div>
    <div class="pc-w" id="pc-w"></div>
    <p class="say" id="pc-say" aria-live="polite"></p>
  </div>
</div>
"""

PC_CSS = """
.pc-plane svg{display:block;width:100%;max-width:360px;height:auto;cursor:crosshair;border:1px solid var(--rule);border-radius:6px;background:var(--surface)}
.pc-btns{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}
.pc-btns button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.pc-w{font:13px var(--mono);margin:6px 0}
"""

PC_JS = r"""
(() => {
  const plane = document.getElementById("pc-plane");
  if (!plane) return;
  const NS = "http://www.w3.org/2000/svg", S = 300;
  let pts = [], w = [0, 0], b = 0, mistakes = 0, passes = 0, adding = true, seed = 1958;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", `0 0 ${S} ${S}`); plane.appendChild(svg);
  // inputs are scaled to -1..1 so that the weights stay readable
  const toX = px => px / S * 2 - 1, toY = py => 1 - py / S * 2, fromX = x => (x + 1) / 2 * S, fromY = y => (1 - y) / 2 * S;
  const answer = p => w[0] * p.x + w[1] * p.y + b > 0;
  function pass() {
    let wrong = 0;
    for (const p of pts) if (answer(p) !== p.yes) { const s = p.yes ? 1 : -1; w[0] += s * p.x; w[1] += s * p.y; b += s; wrong++; mistakes++; }
    passes++;
    return wrong;
  }
  function draw() {
    svg.innerHTML = "";
    // the cut: w0 x + w1 y + b = 0
    if (w[0] || w[1]) {
      const ends = [];
      if (Math.abs(w[1]) > 1e-9) for (const x of [-1, 1]) ends.push([x, -(b + w[0] * x) / w[1]]);
      else for (const y of [-1, 1]) ends.push([-b / w[0], y]);
      sv("line", {x1: fromX(ends[0][0]), y1: fromY(ends[0][1]), x2: fromX(ends[1][0]), y2: fromY(ends[1][1]), stroke: "var(--ink)", "stroke-width": 2}, svg);
    }
    for (const p of pts) {
      const ok = answer(p) === p.yes;
      sv("circle", {cx: fromX(p.x), cy: fromY(p.y), r: 7, fill: p.yes ? "var(--red)" : "var(--blue)", stroke: ok ? "var(--paper)" : "var(--yellow)", "stroke-width": ok ? 1.5 : 4}, svg);
    }
    document.getElementById("pc-w").textContent = `weights ${w[0].toFixed(2)}, ${w[1].toFixed(2)}, bias ${b.toFixed(2)} ; passes ${passes}, corrections ${mistakes}`;
  }
  function show(msg) { draw(); document.getElementById("pc-say").textContent = msg; }
  function reset() { w = [0, 0]; b = 0; mistakes = 0; passes = 0; }
  svg.addEventListener("click", e => {
    const r = svg.getBoundingClientRect();
    pts.push({x: toX((e.clientX - r.left) / r.width * S), y: toY((e.clientY - r.top) / r.height * S), yes: adding});
    show(`${pts.length} points. Press One pass: every wrongly answered point pulls the line towards answering it right.`);
  });
  const yes = document.getElementById("pc-yes"), no = document.getElementById("pc-no");
  yes.addEventListener("click", () => { adding = true; yes.setAttribute("aria-pressed", "true"); no.setAttribute("aria-pressed", "false"); });
  no.addEventListener("click", () => { adding = false; yes.setAttribute("aria-pressed", "false"); no.setAttribute("aria-pressed", "true"); });
  const run = k => { let wrong = 0; for (let i = 0; i < k; i++) wrong = pass(); show(wrong === 0 ? `Every point is on its own side of the line: learned, after ${mistakes} corrections in ${passes} passes.` : `${wrong} point${wrong === 1 ? " was" : "s were"} wrong in the last pass (yellow rings show who is wrong now).`); };
  document.getElementById("pc-pass").addEventListener("click", () => run(1));
  document.getElementById("pc-ten").addEventListener("click", () => run(10));
  document.getElementById("pc-rand").addEventListener("click", () => {
    pts = []; reset();
    const a = rnd() * 2 * Math.PI, c = (rnd() - 0.5) * 0.6;
    while (pts.length < 30) { const x = rnd() * 2 - 1, y = rnd() * 2 - 1, s = Math.cos(a) * x + Math.sin(a) * y - c; if (Math.abs(s) > 0.08) pts.push({x, y, yes: s > 0}); }
    show("30 points that a straight line can separate (the page knows one such line, the perceptron does not). Press One pass, or Ten passes.");
  });
  document.getElementById("pc-xor").addEventListener("click", () => {
    pts = [{x: -0.6, y: -0.6, yes: false}, {x: -0.6, y: 0.6, yes: true}, {x: 0.6, y: -0.6, yes: true}, {x: 0.6, y: 0.6, yes: false}]; reset();
    show("XOR: yes at two opposite corners, no at the other two. No straight line separates them; press Ten passes and watch the line go round and round.");
  });
  document.getElementById("pc-clear").addEventListener("click", () => { pts = []; reset(); show("Empty. Click to add points."); });
  document.getElementById("pc-rand").click();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the perceptron combined older ideas, and where it led")
    W = 210
    nodes = {
        "mp": (20, 20, "The artificial neuron", "fire if the weighted inputs are enough", "McCulloch and Pitts, 1943", "ink"),
        "rf": (395, 20, "Reinforcement", "strengthen what led to the right answer", "psychology", "ink"),
        "ibm": (770, 20, "An IBM 704", "the network simulated first", "1957", "ink"),
        "pc": (395, 170, "The perceptron", "⊕ weights corrected after each wrong answer", "Rosenblatt, 1957–1958", "red"),
        "mk": (20, 330, "The Mark I", "400 photocells, motor-driven weights", "built by 1960", "ink"),
        "conv": (395, 330, "Convergence", "finitely many mistakes if a cut exists", "Novikoff, 1962", "ink"),
        "xor": (770, 330, "Limits", "one unit cannot learn XOR", "Minsky and Papert, 1969", "ink"),
        "today": (395, 480, "Layered networks today", "many units, the same idea of correcting weights", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("mp", "pc", ports=("bottom", "top:0.15"))
    D.edge("rf", "pc", ports=("bottom", "top"))
    D.edge("ibm", "pc", ports=("bottom", "top:0.85"))
    D.edge("pc", "mk", ports=("bottom:0.1", "top:0.7"))
    D.edge("pc", "conv", ports=("bottom", "top"))
    D.edge("pc", "xor", ports=("bottom:0.9", "top:0.3"))
    D.edge("xor", "today", ports=("bottom:0.3", "right:0.5"), dashed=True)
    D.edge("conv", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: the limit was answered by networks with more than one layer, which the 1969 book's critics noted could compute XOR.", "caption")
    return D


def chain(d):
    c, xr = d["cards"], d["xor"]
    steps = [
        ("Recognising a pattern meant writing a rule for every case",
         f"Correct the weights after each wrong answer: the cards were learned, last mistake at card {c['last']}", "Rosenblatt, 1957–1958"),
        ("Will the corrections ever stop?",
         f"Yes, if a straight cut exists: never more than (R/margin)^2 mistakes; checked on {d['bn']} problems", "Novikoff, 1962"),
        ("If no straight cut exists (XOR), the weights go round in circles",
         f"Give the unit a better input, or more units in layers: with x AND y added, learned in {xr['passes']} passes", "Minsky and Papert, 1969, and later"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from hand-written rules to learning")
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
    c, w, bd, bl, xr = d["cards"], d["w"], d["bound"], d["bool"], d["xor"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. McCulloch and Pitts had described a neuron that fires when its weighted inputs are enough. Rosenblatt, a psychologist, let the weights change: after every wrong answer, each weight moves a little towards the answer that would have been right. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the perceptron. Blue: layered networks today."),
        ]),
        dict(id="learn", eyebrow="Try it", title="Watch a line learn where to fall", toc="Try it", blocks=[
            dict(type="p", text="A perceptron with two inputs draws a straight line: yes on one side, no on the other. Each pass shows it every point; for each wrong answer it adds the point to its weights (or subtracts it, for a false yes), which pulls the line towards answering that point correctly. Try the random set, add your own points, then try the XOR corners."),
            dict(type="widget", html=PC_HTML, js=PC_JS, css=PC_CSS,
                 fallback=dict(type="table", head=["Two-input function", "Learned by one perceptron?"], num=[],
                               rows=[[f, "yes"] for f in bl["learned"]] + [[f, f"no (never, in {bl['passes']} passes)"] for f in bl["not_"]], hl=None),
                 note="In the interactive edition you can add points and train a two-input perceptron."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Add the input, or subtract it", toc="How it works", blocks=[
            dict(type="p", text="**The unit.** Multiply each input by its weight, add them up with a bias, and answer yes if the total is positive. **The rule.** If the answer is wrong, add the input to the weights (for a missed yes) or subtract it (for a false yes), and change the bias by one; if it is right, do nothing. The modern statement is a simplification: Rosenblatt's 1958 paper describes several systems of reinforcement."),
            dict(type="p", text=f"**The cards.** Like the 1958 demonstration, cards marked on the left or the right; here 20 × 20 cells, the Mark I's 400 photocells, with a 3 × 3 mark anywhere in one half and 8 specks of dirt. The weights it learned: The perceptron's last mistake came at card {c['last']} ({c['mistakes']} mistakes in all); then it was right {c['run']} times in a row, and on {c['test']} new cards it was right {c['right']} times ({c['pct']}%)."),
            dict(type="svg", name="weights", draw=weights_svg(d), alt="The perceptron's learned weights: left half mostly positive, right half mostly negative"),
            dict(type="callout", kind="key", label="Key idea",
                 text="Don't write the rule: correct the machine every time it is wrong. If a straight cut can separate the two kinds of example, the corrections stop after a limited number of mistakes."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The mistake bound, and what one unit cannot learn", toc="Measured", blocks=[
            dict(type="p", text=f"**The bound.** {d['bn']} random problems: 400 points in a cube, a random cut through the centre, no point closer to it than 0.05. The perceptron always finished, and its mistakes never exceeded (R / 0.05)², R being the largest distance of a point from the centre."),
            dict(type="table", head=["Dimensions", "Mistakes on average", "Bound on average"], num=[0, 1, 2], rows=[list(x) for x in bd]),
            dict(type="p", text=f"**Two inputs, sixteen functions.** Of the 16 yes/no functions of two inputs, {bl['n']} were learned: {', '.join(bl['learned'])}. Never learned in {bl['passes']} passes: {' and '.join(bl['not_'])}, the two for which no straight line separates the yes corners from the no corners."),
            dict(type="p", text=f"**XOR.** After {xr['cycle']} passes through the four examples, the weights were back at a setting they had held before, still wrong on {xr['wrong']} of them: they would cycle for ever. Given x AND y as a third input, the perceptron learned XOR in {xr['passes']} passes, with weights {', '.join(xr['w'])} and bias {xr['b']}: (1,1) gives 1 + 1 − 3 = −1, no."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A Navy press conference", toc="The evidence", blocks=[
            dict(type="p", text="At the Cornell Aeronautical Laboratory, Rosenblatt \"simulated the perceptron on an IBM 704\" (1957); the Office of Naval Research and the Rome Air Development Center funded the Mark I, with \"An array of 400 photocells arranged in a 20x20 grid\" and weights in potentiometers whose updates \"were performed by electric motors\" (Wikipedia). \"In July 1958, the U.S. Office of Naval Research unveiled a remarkable invention\"; \"After 50 trials, the computer taught itself to distinguish cards marked on the left from cards marked on the right\" (Cornell Chronicle)."),
            dict(type="p", text="The *New York Times* headline: \"NEW NAVY DEVICE LEARNS BY DOING: Psychologist Shows Embryo of Computer Designed to Read and Grow Wiser\"; it called the perceptron \"the embryo of an electronic computer that [the Navy] expects will be able to walk, talk, see\", and the claims caused controversy. The paper, in *Psychological Review* (1958), begins: \"If we are eventually to understand the capability of higher organisms for perceptual recognition, generalization, recall, and thinking, we must first have answers to three fundamental questions.\" Minsky and Papert's book (1969) showed that such networks could not learn XOR, and interest fell for about a decade. Rosenblatt died in 1971, on his 43rd birthday."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Sixty years too soon", toc="Full circle", blocks=[
            dict(type="p", text="The Cornell Chronicle's headline in 2019 called it the perceptron that \"paved the way for AI – 60 years too soon\", and quoted a Cornell professor: \"in hindsight, his algorithm is still fundamental to how we're training deep networks today.\" Today's networks stack many layers of such units and correct all their weights at once; the XOR that defeated one unit is easy for two layers."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The machine was never told what \"left\" means. After {c['mistakes']} corrections its weights, drawn as a picture, show the answer: mostly red on the left half, mostly blue on the right."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Weights 0, 0, bias 0; the example (1, 1) should be yes. What happens?", "The total is 0, not positive: a wrong no. Add the input: weights 1, 1, bias 1."),
            ("Why does a right answer change nothing?", "The rule only corrects mistakes; a right answer gives no reason to move the line."),
            ("Can a single perceptron learn AND? OR? XOR?", "AND and OR, yes: a straight line separates their yes corners. XOR, no."),
            ("Why did adding x AND y as an input fix XOR?", "In three dimensions the four corners can be cut by a flat plane: the new input lifts the (1,1) corner away from the others."),
            ("What does the mistake bound depend on?", "On how far the points spread (R) compared with the gap around the cut (the margin), not on how many points there are."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Mark I Perceptron", text="The machine with 400 photocells and motor-driven weights, now in the Smithsonian Institution.",
                 draw=C.draw_board, link="https://news.cornell.edu/node/313946", link_text="Cornell Chronicle", licence="Drawn placeholder."),
            dict(title="The Perceptron (1958)", text="Rosenblatt's paper in Psychological Review 65(6): 386–408.",
                 draw=C.draw_manuscript, link="https://homepages.math.uic.edu/~lreyzin/papers/rosenblatt58.pdf", link_text="PDF on a course page", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Perceptron", d["checks"],
                           f"cards learned and tested on {c['test']} new ones, the mistake bound on {d['bn']} random problems, all 16 two-input functions, and XOR with and without a helping input.",
                           ["boolean learn(double[] x, boolean yes)"]),
    ]
    return dict(
        title="Rosenblatt's Perceptron", date="1957–1958",
        description="Era 5, topic 9 of The Algorithm Evolution Atlas: Rosenblatt's perceptron, the first learning machine, with its mistake bound and the XOR it cannot learn.",
        lede="Every procedure so far had been written by someone who understood the problem. Rosenblatt built a machine that found its own: a weighted sum and a threshold, corrected after every wrong answer.",
        fieldnote=f"Cards marked on the left or the right: the machine's last mistake came at card {c['last']}, and it then judged {c['pct']}% of new cards correctly. Its weights, drawn as a picture, show what it learned. The newspapers of 1958 promised far more than it could do; a Cornell headline later called it sixty years too soon.",
        card=[("When", "Simulated 1957; demonstrated July 1958"),
              ("Where", "Cornell Aeronautical Laboratory, Buffalo"),
              ("What hurt", "A hand-written rule for every pattern"),
              ("The fix", "Correct the weights after each wrong answer"),
              ("Limit", "Only patterns a straight cut can separate")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Perceptron.java`.",
    )
