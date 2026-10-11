"""Era 4, topic 10: Monte Carlo and the middle-square method. Every number is parsed from MonteCarlo.java's output."""
import random
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"middle: .*? one of (\d+) cycles: (.+?) ; the longest run before a number repeats is (\d+) numbers, from seed (\d+) ; on average ([\d.]+)$", ln):
            d["mid"] = dict(n=int(m.group(1)), cycles=[(c, int(k)) for c, k in re.findall(r"\[([\d ]+)\] from (\d+) seeds?", m.group(2))],
                            longest=int(m.group(3)), lseed=m.group(4), avg=m.group(5))
        elif m := re.match(r"seq: from seed 1234: (.+?), then (\d+) again ; (\d+) different numbers$", ln):
            d["seq"] = dict(nums=m.group(1).split(), rep=m.group(2), n=int(m.group(3)))
        elif m := re.match(r"pi: .*? ; ((?:[\d,]+ points: [\d.]+ ; )+)typical error over 200 runs: (.+?) ; ratios (.+?) ; theory for 1,000 points .*? = ([\d.]+)$", ln):
            d["pi"] = dict(est=re.findall(r"([\d,]+) points: ([\d.]+)", m.group(1)), rms=re.findall(r"([\d,]+): ([\d.]+)", m.group(2)),
                           ratios=m.group(3).split(", "), theory=m.group(4))
        elif m := re.match(r"ball: .*? ; (d = .+?) ; a grid", ln):
            d["ball"] = re.findall(r"d = (\d+): estimate ([\d.]+), exact ([\d.]+), ([\d.]+)% of points inside", m.group(1))
        elif m := re.match(r"bad: .*?: ([\d.]+) ; only (\d+) different numbers", ln):
            d["bad"] = dict(pi=m.group(1), n=int(m.group(2)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def darts_svg(d):
    def draw(t, standalone):
        out, s, x0, y0 = [], 300, 30, 30
        out.append(C.rect(x0, y0, s, s, t["surface"], t["ink2"], 1.5))
        out.append(C.path(f"M{x0},{y0 + s} A{s},{s} 0 0 1 {x0 + s},{y0}", t["blue"], "none", 2))
        rnd = random.Random(1946)
        for _ in range(1200):
            x, y = rnd.random(), rnd.random()
            out.append(C.circle(x0 + x * s, y0 + s - y * s, 1.6, t["red"] if x * x + y * y < 1 else t["muted"]))
        out.append(C.text(x0, y0 + s + 22, "1,200 random points (an illustration): red inside the quarter circle", t["muted"], 12))
        X = 380
        out.append(C.text(X, 50, "Share inside × 4 → π", t["ink"], 15, "start", 700))
        for i, (n, v) in enumerate(d["pi"]["est"]):
            out.append(C.text(X, 82 + i * 22, f"{n} points: {v}", t["ink"], 13.5))
        y = 82 + len(d["pi"]["est"]) * 22 + 20
        out.append(C.text(X, y, "Four times the points, about half the error:", t["muted"], 12.5))
        for i, (n, v) in enumerate(d["pi"]["rms"]):
            out.append(C.text(X, y + 22 + i * 20, f"{n} points: typical error {v}", t["blue"], 13))
        y2 = y + 22 + len(d["pi"]["rms"]) * 20 + 16
        out.append(C.text(X, y2, f"With middle-square numbers from seed 1234: {d['bad']['pi']}", t["red"], 13, "start", 700))
        return C.svg_doc(780, max(370, y2 + 16), "".join(out), "Estimating pi from random points", t, standalone, 0.55, 780)
    return draw


MC_HTML = """
<div class="board mc-board">
  <div style="min-width:0">
    <svg id="mc-svg" viewBox="0 0 320 320" role="img" aria-label="Random points in a square; those inside the quarter circle are red"></svg>
    <div class="controls">
      <button class="primary" id="mc-100">+100 points</button><button id="mc-10k">+10,000</button><button id="mc-1m">+1,000,000</button><button id="mc-clear">Clear</button>
    </div>
    <div class="controls"><label for="mc-gen">Random numbers from <select id="mc-gen"><option value="good">a good generator</option><option value="ms">middle-square, seed 1234</option></select></label></div>
  </div>
  <div style="min-width:0">
    <ol class="mc-steps" id="mc-steps"></ol>
    <div class="eyebrow">Middle-square by hand</div>
    <div class="controls"><label for="mc-seed">Seed <input id="mc-seed" type="number" min="0" max="9999" value="540"></label></div>
    <div class="mc-seq" id="mc-seq"></div>
    <p class="say" id="mc-say" aria-live="polite"></p>
  </div>
</div>
"""

MC_CSS = """
#mc-svg{width:100%;max-width:320px;height:auto}
.mc-board .controls{flex-wrap:wrap;gap:6px}
.mc-board select{font:inherit;font-size:13.5px}
.mc-board input[type=number]{width:6em}
.mc-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.mc-steps .m{font-family:var(--mono);font-size:12.5px}
.mc-seq{font:12.5px var(--mono);display:flex;flex-wrap:wrap;gap:4px;margin:6px 0}
.mc-seq span{padding:1px 4px;border:1px solid var(--axis);background:var(--surface)}
.mc-seq span.cyc{background:var(--red);color:var(--on-red);border-color:var(--red)}
"""

MC_JS = r"""
(() => {
  const svg = document.getElementById("mc-svg");
  if (!svg) return;
  let state = 2026, ms = 1234, n = 0, inside = 0, drawn = 0;
  const good = () => { state = (Math.imul(state, 1664525) + 1013904223) >>> 0; return state / 4294967296; };
  const msq = x => Math.floor(x * x / 100) % 10000;
  const nextMs = () => { const v = ms; ms = msq(ms); return v / 10000; };
  function reset() { svg.innerHTML = ""; n = 0; inside = 0; drawn = 0; ms = 1234; state = 2026;
    sv("rect", {x: 10, y: 10, width: 300, height: 300, fill: "var(--surface)", stroke: "var(--ink-2)"}, svg);
    sv("path", {d: "M10,310 A300,300 0 0 1 310,10", fill: "none", stroke: "var(--blue)", "stroke-width": 2}, svg);
    show(); }
  function add(k) {
    const gen = document.getElementById("mc-gen").value === "ms" ? nextMs : good;
    for (let i = 0; i < k; i++) {
      const x = gen(), y = gen(), hit = x * x + y * y < 1;
      if (hit) inside++; n++;
      if (drawn < 4000) { sv("circle", {cx: 10 + x * 300, cy: 310 - y * 300, r: 1.6, fill: hit ? "var(--red)" : "var(--muted)"}, svg); drawn++; }
    }
    show();
  }
  function show() {
    const ol = document.getElementById("mc-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    if (!n) { li("Add points: each lands at a random spot in the square."); return; }
    const est = 4 * inside / n;
    li(`${fmt(n)} points, ${fmt(inside)} inside the quarter circle`);
    li(`estimate of π = 4 × ${fmt(inside)} / ${fmt(n)} = <span class="m">${est.toFixed(6)}</span>`);
    li(`error <span class="m">${(est - Math.PI).toFixed(6)}</span>; typical error for ${fmt(n)} points is about ${Math.sqrt(Math.PI * (4 - Math.PI) / n).toFixed(5)}`);
  }
  function seq() {
    let x = Math.max(0, Math.min(9999, Math.round(+document.getElementById("mc-seed").value || 0)));
    const seen = new Map(), list = [];
    while (!seen.has(x)) { seen.set(x, list.length); list.push(x); x = msq(x); }
    const start = seen.get(x);
    const box = document.getElementById("mc-seq"); box.innerHTML = "";
    list.forEach((v, i) => el("span", {class: i >= start ? "cyc" : ""}, box, String(v).padStart(4, "0")));
    document.getElementById("mc-say").textContent = `${list.length} different numbers, then ${String(x).padStart(4, "0")} again: a cycle of ${list.length - start} (red). Every seed ends in a cycle, because each number fixes the next.`;
  }
  document.getElementById("mc-100").addEventListener("click", () => add(100));
  document.getElementById("mc-10k").addEventListener("click", () => add(10000));
  document.getElementById("mc-1m").addEventListener("click", () => add(1000000));
  document.getElementById("mc-clear").addEventListener("click", reset);
  document.getElementById("mc-gen").addEventListener("change", reset);
  document.getElementById("mc-seed").addEventListener("input", seq);
  reset(); seq();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the Monte Carlo method combined older ideas, and where it led")
    W = 210
    nodes = {
        "buf": (20, 20, "Random throws", "Buffon's needle estimates π", "an early variant", "ink"),
        "mk": (395, 20, "Markov chains", "chance that depends on the last step", "topic 3", "ink"),
        "en": (770, 20, "Electronic computers", "millions of operations", "ENIAC; topic 9", "ink"),
        "mc": (395, 170, "Monte Carlo", "⊕ simulate many random cases, by machine", "1946–1949", "red"),
        "ms": (20, 330, "Middle-square", "random-looking digits by arithmetic", "1949", "ink"),
        "nuc": (395, 330, "Neutron chains", "the first calculations, on the ENIAC", "1948", "ink"),
        "mcmc": (770, 330, "Sampling by chains", "walk randomly to sample", "after this era", "ink"),
        "today": (395, 480, "Simulation today", "risk, physics, graphics, machine learning", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("buf", "mc", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("mk", "mc", ports=("bottom", "top"))
    D.edge("en", "mc", ports=("bottom", "top:0.85"))
    D.edge("mc", "ms", ports=("bottom:0.1", "top:0.7"))
    D.edge("mc", "nuc", ports=("bottom", "top"))
    D.edge("mc", "mcmc", ports=("bottom:0.9", "top:0.3"))
    D.edge("nuc", "today", ports=("bottom", "top"))
    D.edge("mcmc", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: Buffon's needle is \"an early variant\" (Wikipedia), not a documented source of the 1946 idea.", "caption")
    return D


def chain(d):
    pi, md, bd = d["pi"], d["mid"], d["bad"]
    steps = [
        ("Patience, or a chain of neutrons: far too many cases to calculate",
         "Play many random games by machine and count", "Ulam and von Neumann, 1946–1947"),
        ("A sample gives only an approximate answer",
         f"Measure the error: four times the points, about half the error ({pi['rms'][0][1]} → {pi['rms'][1][1]})", "error ∝ 1/√N"),
        ("Reading random digits from cards is too slow for the machine",
         "Let the machine make them: square, keep the middle digits", "von Neumann, middle-square, 1949"),
        (f"Middle-square repeats: from seed 1234 only {d['seq']['n']} numbers, then 0000 for ever",
         "Better generators, tested before they are trusted", "after this era"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from patience to pseudo-random numbers")
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
    md, sq, pi, ball, bad = d["mid"], d["seq"], d["pi"], d["ball"], d["bad"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Estimating by random trials is old (Buffon's needle); chains of chance events had been studied since Markov (topic 3). What was new in 1946 was a machine fast enough to run the trials by the million, and a problem, neutron chains in a weapon core, too tangled for any formula. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the Monte Carlo method at Los Alamos. Blue: simulation today."),
        ]),
        dict(id="darts", eyebrow="Try it", title="Throw points, and make your own random numbers", toc="Try it", blocks=[
            dict(type="p", text="Add random points to the square. The share that lands inside the quarter circle, times 4, estimates π, and the error shrinks slowly: a hundred times the points for one more correct digit. Then switch to middle-square numbers from seed 1234 and watch the estimate go wrong. Below, enter any 4-digit seed: the sequence always ends in a cycle (red)."),
            dict(type="widget", html=MC_HTML, js=MC_JS, css=MC_CSS,
                 fallback=dict(type="svg", name="darts", draw=darts_svg(d), alt="Estimating pi from random points", width=780),
                 note="In the interactive edition you can throw points and run the middle-square method from any seed."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Count, and know how wrong you are", toc="How it works", blocks=[
            dict(type="p", text="**Estimate by counting.** Choose random points in a square of side 1; a point (x, y) lies in the quarter circle when x² + y² < 1, which happens with probability π/4. So 4 × (share inside) estimates π. The program's estimates:"),
            dict(type="table", head=["Points", "Estimate of π"], num=[0, 1], rows=[[n, v] for n, v in pi["est"]]),
            dict(type="p", text=f"**The error.** Over 200 independent runs, the typical (root-mean-square) error at 1,000 points was {pi['rms'][0][1]}, close to the theoretical √(π(4 − π)/N) = {pi['theory']}. Each fourfold increase in points roughly halved it (ratios {', '.join(pi['ratios'])}). The same holds in any number of dimensions, which is why the method beats a grid in high dimensions:"),
            dict(type="table", head=["Dimension", "Ball volume estimated from 1,000,000 points", "Exact", "Share of points inside"], num=[0, 1, 2, 3],
                 rows=[[a, b, c, f"{e}%"] for a, b, c, e in ball]),
            dict(type="p", text="A grid with only 10 points per side would need 10¹⁰ points in ten dimensions. The ten-dimensional estimate is the roughest here, because only a quarter of one per cent of the points fall in the ball: the error depends on the number of hits, not the dimension directly."),
            dict(type="p", text=f"**Middle-square.** Square a 4-digit number, pad the square to 8 digits, keep the middle 4. From seed 1234: {' '.join(sq['nums'][:12])} … and after {sq['n']} different numbers the sequence reaches {sq['rep']} and stays there. The program ran every one of the 10,000 seeds: each ends in one of {md['n']} cycles."),
            dict(type="table", head=["Final cycle", "Seeds that end there"], num=[1], rows=[[c, f"{k:,}"] for c, k in md["cycles"]]),
            dict(type="callout", kind="key", label="Key idea",
                 text="When a quantity is too tangled to calculate, sample it at random and count, and report the error with the answer: it falls like one over the square root of the number of samples, in any dimension. The random numbers themselves can be made by arithmetic, but only if someone checks that the arithmetic does not repeat or collapse."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How fast middle-square fails", toc="Measured", blocks=[
            dict(type="p", text=f"Over all 10,000 seeds, a 4-digit middle-square sequence runs on average {md['avg']} numbers before repeating; the longest run, from seed {md['lseed']}, is {md['longest']}. Estimating π from 100,000 points built from middle-square numbers (seed 1234) gives {bad['pi']}: only {bad['n']} different numbers ever appear, and once the sequence reaches 0000 every point is the corner (0, 0), inside the circle."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Los Alamos, 1946–1949", toc="The evidence", blocks=[
            dict(type="p", text="Ulam: the method was \"suggested by a question which occurred to me in 1946 as I was convalescing from an illness and playing solitaires\" (Eckhardt, *Los Alamos Science*, 1987). Metropolis places \"the spark\" at the spring 1946 review of the ENIAC's results, and dates von Neumann's letter to Richtmyer outlining a statistical calculation of neutron diffusion 11 March 1947; Metropolis suggested the name, after Ulam's uncle who \"just had to go to Monte Carlo\" (Metropolis, 1987). The first fully automated Monte Carlo calculations ran on the ENIAC in spring 1948 (Wikipedia)."),
            dict(type="p", text="Von Neumann described middle-square in 1949, printed in 1951: \"Anyone who considers arithmetical methods of producing random digits is, of course, in a state of sin\"; such methods were \"hundreds of times faster than reading 'truly' random numbers off punch cards\" (Wikipedia, Middle-square method). That a Franciscan friar invented it in the 1240s rests on one book's report of a lost manuscript (**disputed**)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Simulation is everywhere", toc="Full circle", blocks=[
            dict(type="p", text="Monte Carlo methods now price financial risk, render light in films, design reactors and train machine-learning models, and every one of them needs pseudo-random numbers. The generators are better than middle-square, and they are tested statistically before they are trusted, but they are still arithmetic, which is why von Neumann's joke about sin is still quoted."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Ten million points estimate π as {pi['est'][-1][1]}: three correct decimals for ten million random numbers. Monte Carlo is slow to converge, and it is still the method of choice when nothing else works."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does the share of points inside the quarter circle tend to π/4?", "The quarter circle has area π/4 and the square area 1; random points land in each region in proportion to its area."),
            ("You have an estimate with typical error 0.01 from 10,000 points. How many points for error 0.001?", "A hundred times as many, 1,000,000: the error shrinks like 1/√N."),
            ("Square 0540 and keep the middle digits. What comes next?", "540² = 291,600, padded to 00291600; the middle four digits are 2916."),
            ("Why must every middle-square sequence repeat?", "There are only 10,000 four-digit numbers, and each one fixes the next, so within 10,001 steps some number recurs and the sequence cycles from there."),
            ("Why does Monte Carlo beat a grid in ten dimensions?", "A grid needs (points per side)¹⁰ points; random sampling's error depends on the number of samples, not on the dimension."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Beginning of the Monte Carlo Method (1987)", text="Metropolis's account in the Los Alamos Science special issue for Ulam.",
                 draw=C.draw_book, link="https://mcnpx.lanl.gov/pdf_files/Article_1987_LAS_Metropolis_125--130.pdf", link_text="Los Alamos National Laboratory", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MonteCarlo", d["checks"],
                           "every 4-digit middle-square seed followed to its cycle (including the fixed points and the cycle 0540 2916 5030 3009 that Wikipedia lists), π from ten million points, the error ratio when the points are quadrupled, the ball's volume in 2, 5 and 10 dimensions, and the failure of middle-square numbers.",
                           ["static int middleSquare(", "static double ballVolume("]),
    ]
    return dict(
        title="Monte Carlo", date="1946–1949",
        description="Era 4, topic 10 of The Algorithm Evolution Atlas: the Monte Carlo method at Los Alamos, and von Neumann's middle-square random numbers.",
        lede="A mathematician playing patience asked what fraction of games come out, and realised it was easier to deal many and count. With the first electronic computers, counting random trials became a way to compute, provided the machine could make its own random numbers.",
        fieldnote=f"Ten million random points told me π to three decimals, {pi['est'][-1][1]}. Then I tried von Neumann's home-made random numbers, starting from 1234: after {sq['n']} numbers they reached 0000 and never left, and my estimate of π became {bad['pi']}. He warned that using them was a sin, and he used them anyway.",
        card=[("When", "1946 idea; ENIAC runs 1948; papers 1949"),
              ("Where", "Los Alamos"),
              ("What hurt", "Problems with too many interacting chances"),
              ("The fix", "Simulate random cases and count; machine-made random digits"),
              ("Cost", "Error ∝ 1/√N, in any dimension")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MonteCarlo.java`.",
    )
