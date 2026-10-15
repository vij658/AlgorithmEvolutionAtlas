"""Era 7, topic 4: simulated annealing. Every number is parsed from SimulatedAnnealing.java's output."""
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"exact: (\d+) sets of (\d+) random cities.*? from a random tour found it (\d+) times, on average ([\d.]+)% too long ; annealing found it (\d+) times, on average ([\d.]+)% too long", ln):
            d["exact"] = dict(sets=m.group(1), n=m.group(2), dh=m.group(3), dx=m.group(4), ah=m.group(5), ax=m.group(6))
        elif m := re.match(r"tour: (\d+) sets of (\d+) random cities.*? ; random tour ([\d.]+) ; iterative improvement ([\d.]+) \(([\d,]+) changes tried\) ; annealing ([\d.]+) \(([\d,]+) changes tried\), shorter in (\d+) of (\d+) sets", ln):
            d["tour"] = dict(sets=m.group(1), n=m.group(2), rand=m.group(3), desc=m.group(4), dtries=m.group(5), ann=m.group(6), atries=m.group(7), wins=m.group(8))
        elif m := re.match(r"cooling: [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"factor ([\d.]+): length ([\d.]+), ([\d,]+) changes tried", part)
                rows.append(dict(f=mm.group(1), len=mm.group(2), work=mm.group(3)))
            d["cool"] = rows
        elif m := re.match(r"accept: one run on (\d+) cities, (\d+) temperatures, [^;]* ; (.*)$", ln):
            pts = [tuple(float(x) for x in p.split(":")) for p in m.group(3).split()]
            d["acc"] = dict(n=m.group(1), temps=m.group(2), pts=pts)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def accept_svg(d):
    """The share of changes accepted at each temperature, from the program's one run."""
    pts = d["acc"]["pts"]

    def draw(t, standalone):
        o = []
        W, H = 760, 330
        x0, x1, y0, y1 = 70, 730, 270, 50
        ts = [p[0] for p in pts]
        lo, hi = math.log10(min(ts)), math.log10(max(ts))
        X = lambda v: x1 - (math.log10(v) - lo) / (hi - lo) * (x1 - x0)          # hot on the left
        X = lambda v, lo=lo, hi=hi: x0 + (hi - math.log10(v)) / (hi - lo) * (x1 - x0)
        Y = lambda s: y0 - s * (y0 - y1)
        o.append(C.text(20, 26, f"One run on {d['acc']['n']} cities: the share of proposed changes accepted at each temperature", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        for s in (0, 0.25, 0.5, 0.75, 1.0):
            o.append(C.line(x0 - 4, Y(s), x0, Y(s), t["axis"], 1.2))
            o.append(C.text(x0 - 8, Y(s) + 4, f"{int(s * 100)}%", t["muted"], 11.5, "end"))
        for v in (2, 1, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005):
            if min(ts) <= v <= max(ts):
                o.append(C.line(X(v), y0, X(v), y0 + 4, t["axis"], 1.2))
                o.append(C.text(X(v), y0 + 18, f"{v:g}", t["muted"], 11.5, "middle"))
        o.append(C.text((x0 + x1) / 2, y0 + 38, "temperature T (cooling to the right, by a factor 0.9 each step)", t["muted"], 12, "middle"))
        dpath = " ".join(f"{'M' if i == 0 else 'L'}{X(p[0]):.1f},{Y(p[1]):.1f}" for i, p in enumerate(pts))
        o.append(C.path(dpath, t["red"], "none", 2.2))
        for p in pts:
            o.append(C.circle(X(p[0]), Y(p[1]), 2.6, t["red"]))
        o.append(C.text(X(pts[0][0]) + 8, Y(pts[0][1]) - 8, f"hot: {pts[0][1] * 100:.0f}% accepted", t["ink"], 12, "start", 700))
        o.append(C.text(X(pts[-1][0]) - 4, Y(pts[-1][1]) - 12, f"frozen: {pts[-1][1] * 100:.1f}%", t["ink"], 12, "end", 700))
        return C.svg_doc(W, H, "".join(o), "Acceptance rate against temperature in one annealing run", t, standalone, 0.55, 760)
    return draw


SA_HTML = """
<div class="board sa-board">
  <div style="min-width:0">
    <div class="sa-view" id="sa-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls"><label>Cooling factor <select id="sa-cool"><option>0.5</option><option>0.8</option><option selected>0.9</option><option>0.95</option><option>0.99</option></select></label></div>
    <div class="sa-btns"><button type="button" class="primary" id="sa-anneal">Anneal</button><button type="button" id="sa-descend">Only improve</button><button type="button" id="sa-new">New cities</button></div>
    <div class="sa-stats" id="sa-stats"></div>
    <p class="say" id="sa-say" aria-live="polite"></p>
  </div>
</div>
"""

SA_CSS = """
.sa-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.sa-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.sa-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
.sa-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:3px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
"""

SA_JS = r"""
(() => {
  const view = document.getElementById("sa-view");
  if (!view) return;
  const N = 60;
  let seed = 1983, cities, tour, timer = null, start, results = {};
  const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const dist = (a, b) => Math.hypot(cities[a][0] - cities[b][0], cities[a][1] - cities[b][1]);
  const len = t => t.reduce((s, c, i) => s + dist(c, t[(i + 1) % t.length]), 0);
  function fresh() {
    cities = Array.from({length: N}, () => [rnd(), rnd()]);
    start = Array.from({length: N}, (_, i) => i);
    for (let i = N - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [start[i], start[j]] = [start[j], start[i]]; }
    tour = start.slice(); results = {};
    draw(null, "A random tour of 60 cities. Press Anneal, or Only improve, and compare.");
  }
  function delta(t, i, j) {
    const n = t.length, a = t[(i - 1 + n) % n], b = t[i], c = t[j], d = t[(j + 1) % n];
    if (a === c || b === d) return 0;                     // reversing the whole tour changes nothing
    return dist(a, c) + dist(b, d) - dist(a, b) - dist(c, d);
  }
  function rev(t, i, j) { while (i < j) { [t[i], t[j]] = [t[j], t[i]]; i++; j--; } }
  function draw(info, msg) {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 400 400"}, view), X = v => 15 + v * 370;
    sv("polygon", {points: tour.map(c => `${X(cities[c][0])},${X(cities[c][1])}`).join(" "), fill: "none", stroke: "var(--red)", "stroke-width": 1.8}, svg);
    cities.forEach(p => sv("circle", {cx: X(p[0]), cy: X(p[1]), r: 3.2, fill: "var(--ink)"}, svg));
    const st = document.getElementById("sa-stats"); st.innerHTML = "";
    el("div", {}, st, `tour length: ${len(tour).toFixed(3)}`);
    if (info) Object.entries(info).forEach(([k, v]) => el("div", {}, st, `${k}: ${v}`));
    Object.entries(results).forEach(([k, v]) => el("div", {}, st, `${k}: ${v}`));
    if (msg) document.getElementById("sa-say").textContent = msg;
  }
  function stop() { if (timer) cancelAnimationFrame(timer); timer = null; }
  function anneal() {
    stop(); tour = start.slice();
    const cool = parseFloat(document.getElementById("sa-cool").value);
    let T = 2.0, cold = 0, tries = 0;
    const step = () => {
      let accepted = 0, tried = 0;
      while (tried < 100 * N && accepted < 10 * N) {
        let i = Math.floor(rnd() * N), j = Math.floor(rnd() * N);
        if (i === j) continue; if (i > j) [i, j] = [j, i]; if (j - i >= N - 2) continue;
        const dd = delta(tour, i, j); tried++; tries++;
        if (dd <= 0 || rnd() < Math.exp(-dd / T)) { rev(tour, i, j); accepted++; }
      }
      cold = accepted * 1000 < tried ? cold + 1 : 0;
      draw({"temperature": T.toPrecision(3), "accepted at this temperature": (100 * accepted / tried).toFixed(1) + "%", "changes tried": tries.toLocaleString("en-US")},
           `Annealing with cooling factor ${cool}: hot at first, so the tour wanders; it settles as T falls.`);
      T *= cool;
      if (cold < 3) timer = requestAnimationFrame(step);
      else { timer = null; results[`annealed (×${cool})`] = len(tour).toFixed(3); draw({"changes tried": tries.toLocaleString("en-US")}, `Frozen after ${tries.toLocaleString("en-US")} changes. Try Only improve on the same cities, or a slower cooling factor.`); }
    };
    step();
  }
  function descend() {
    stop(); tour = start.slice();
    let improved = true, tries = 0;
    while (improved) { improved = false; for (let i = 0; i < N - 1; i++) for (let j = i + 1; j < N; j++) { tries++; if (delta(tour, i, j) < -1e-12) { rev(tour, i, j); improved = true; } } }
    results["only improving"] = len(tour).toFixed(3);
    draw({"changes tried": tries.toLocaleString("en-US")}, "Only improving: stuck at a tour that no single reversal can shorten.");
  }
  document.getElementById("sa-anneal").addEventListener("click", anneal);
  document.getElementById("sa-descend").addEventListener("click", descend);
  document.getElementById("sa-new").addEventListener("click", () => { stop(); fresh(); });
  fresh();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How simulated annealing combined older ideas, and where it led")
    W = 210
    nodes = {
        "mc": (20, 20, "The Metropolis rule", "accept a worse state with probability e^(−Δ/T)", "1953; Monte Carlo, Era 4", "ink"),
        "ii": (395, 20, "Iterative improvement", "keep a change only if it helps", "", "ink"),
        "an": (770, 20, "Annealing metal", "cool slowly to avoid a disordered, glassy state", "metallurgy", "ink"),
        "sa": (395, 180, "Simulated annealing", "⊕ a temperature that falls slowly", "Kirkpatrick, Gelatt, Vecchi, 1983", "red"),
        "chip": (20, 340, "Chip design", "partitioning, placement and wiring", "IBM, 1983", "ink"),
        "tsp": (395, 340, "The travelling salesman", "thousands of cities", "Kirkpatrick et al.; Černý, 1985", "ink"),
        "today": (395, 490, "Today", "satisfiability, protein structure, job-shop scheduling", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("mc", "sa", ports=("bottom", "top:0.15"))
    D.edge("ii", "sa", ports=("bottom", "top"))
    D.edge("an", "sa", ports=("bottom", "top:0.85"), dashed=True, label="an analogy", at=0.5, dx=8, anchor="start")
    D.edge("sa", "chip", ports=("bottom:0.15", "top"))
    D.edge("sa", "tsp", ports=("bottom", "top"))
    D.edge("tsp", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: uses listed by Wikipedia's article. Dashed: an analogy from physics, not an algorithm borrowed.", "caption")
    return D


def chain(d):
    ex, tr, cool = d["exact"], d["tour"], d["cool"]
    slow, fast = cool[-1], cool[0]
    steps = [
        ("Hard problems (Era 6) still need good answers: chips must be placed, tours driven",
         f"Iterative improvement: from a random tour of length {tr['rand']}, down to {tr['desc']} on {tr['n']} cities", "the usual method"),
        (f"It stops at the first dead end: it found the best {ex['n']}-city tour only {ex['dh']} times in {ex['sets']}",
         f"Accept worse changes with probability e^(−Δ/T), and lower T slowly: {ex['ah']} times in {ex['sets']}", "Kirkpatrick, Gelatt and Vecchi, 1983"),
        (f"Slow cooling costs work: {slow['work']} changes at factor {slow['f']}, against {fast['work']} at {fast['f']}",
         "A schedule found by experiment: start hot, multiply T by about 0.9, stop when frozen", "\"empirically adjusted for each problem\""),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from dead ends to a temperature")
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
    ex, tr, cool, acc = d["exact"], d["tour"], d["cool"], d["acc"]
    cool_rows = [[r["f"], r["len"], r["work"]] for r in cool]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Physicists had simulated atoms at a temperature since 1953 with the Metropolis rule, which sometimes accepts a worse state. Engineers improved designs by small changes that help. Kirkpatrick, Gelatt and Vecchi joined the two and added a temperature that falls slowly, as in annealing metal. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: simulated annealing. Blue: where it is used."),
        ]),
        dict(id="play", eyebrow="Try it", title="Cool it slowly", toc="Try it", blocks=[
            dict(type="p", text="Sixty cities and a random tour. Only improve tries reversing every stretch of the tour and keeps any reversal that shortens it, until none does. Anneal tries random reversals and also accepts some that lengthen the tour, with probability e^(−Δ/T); the temperature T starts at 2 and is multiplied by the cooling factor each round, with the same rules as the program. Compare the two lengths, then try faster and slower cooling. This is a live run on the widget's own cities, so its numbers are not the program's."),
            dict(type="widget", html=SA_HTML, js=SA_JS, css=SA_CSS,
                 fallback=dict(type="table", head=["Cooling factor", "Mean tour length (200 cities)", "Changes tried"], num=[0, 1, 2], rows=cool_rows),
                 note="In the interactive edition you can anneal a tour of 60 cities and watch it settle."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Sometimes go uphill", toc="How it works", blocks=[
            dict(type="p", text="**A change.** Pick two places in the tour and reverse the stretch between them. That removes two roads and adds two; the change in length, Δ, takes four distances to compute."),
            dict(type="p", text="**The rule.** If Δ ≤ 0, accept. If Δ > 0, accept with probability e^(−Δ/T). At a high temperature T nearly everything is accepted and the tour wanders; at a low one almost only improvements are, and the method becomes iterative improvement."),
            dict(type="p", text="**The schedule.** Start hot enough that most changes are accepted. At each temperature try up to 100 changes per city, moving on after 10 acceptances per city; then multiply T by a factor such as 0.9. Stop when three temperatures in a row accept fewer than 1 change in 1,000, and finish with a pass of iterative improvement."),
            dict(type="svg", name="accept", draw=accept_svg(d), alt="Acceptance rate against temperature", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="To escape a dead end you must sometimes accept a worse position. Doing so freely at first, and more and more rarely, lets the search find a deep valley rather than the first hollow."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Against the exact answer", toc="Measured", blocks=[
            dict(type="p", text=f"**Twelve cities,** where the best tour can be found exactly by Held and Karp's dynamic programme. In {ex['sets']} random sets, iterative improvement from a random tour found the best tour {ex['dh']} times and was {ex['dx']}% too long on average; annealing found it {ex['ah']} times, {ex['ax']}% too long on average."),
            dict(type="p", text=f"**Two hundred cities,** {tr['sets']} random sets in a unit square. Mean lengths: a random tour {tr['rand']}; iterative improvement {tr['desc']} ({tr['dtries']} changes tried); annealing {tr['ann']} ({tr['atries']} changes tried), shorter in {tr['wins']} of {tr['sets']} sets."),
            dict(type="table", head=["Method", "Mean tour length", "Changes tried"], num=[1, 2],
                 rows=[["Random tour", tr["rand"], "0"], ["Iterative improvement", tr["desc"], tr["dtries"]], ["Annealing, factor 0.9", tr["ann"], tr["atries"]]], hl=[2]),
            dict(type="p", text="**The cooling rate,** the same 5 sets of 200 cities each time. Slower cooling usually gives shorter tours and always costs more work; the ordering is not perfect (0.95 did slightly worse than 0.9 on these 5 sets), which is one reason schedules are tuned by experiment:"),
            dict(type="table", head=["Cooling factor", "Mean tour length", "Changes tried"], num=[0, 1, 2], rows=cool_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two discoveries, one name", toc="The evidence", blocks=[
            dict(type="p", text="S. Kirkpatrick, C. D. Gelatt Jr. and M. P. Vecchi, \"Optimization by Simulated Annealing\" (IBM Thomas J. Watson Research Center; *Science* 220, 13 May 1983): \"There is a deep and useful connection between statistical mechanics ... and multivariate or combinatorial optimization.\" They describe \"partitioning, component placement, and wiring of electronic systems\" and travelling salesman problems \"with as many as several thousand cities\". Annealing \"differs from iterative improvement in that the procedure need not get stuck\"; accepting only improvements is like rapid quenching, whose results \"are usually metastable\". Their schedule multiplies the temperature by 0.9 each step; in one partitioning example quenching gave about 700 pins, slow annealing 353 and 321."),
            dict(type="p", text="V. Černý of Comenius University, Bratislava, published \"Thermodynamical Approach to the Traveling Salesman Problem: An Efficient Simulation Algorithm\" in the *Journal of Optimization Theory and Applications* in January 1985: on 100 points on a circle, \"After a total of 25,000 Monte Carlo trials a value 6.28 was reached, which means that the true optimum was found.\" Wikipedia lists earlier independent versions (Pincus 1970; Khachaturyan and others 1979, 1981) and credits Kirkpatrick and colleagues with the name. It also warns that the time for a good chance of the global optimum \"will usually exceed the time required for a complete search\", and that the cooling rate \"should be empirically adjusted for each problem\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Monte Carlo, put to work", toc="Full circle", blocks=[
            dict(type="p", text="Era 4's Monte Carlo methods used random numbers to estimate what could not be computed exactly. Annealing uses them to search: the same Metropolis rule that sampled the states of atoms now samples tours and chip layouts, and the temperature turns sampling into optimizing."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Era 6 proved the travelling salesman problem is NP-complete. Era 7 answered with a method that guarantees nothing useful and, on {ex['n']} cities, found the best tour {ex['ah']} times in {ex['sets']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A change lengthens the tour by 0.1. What is the chance of accepting it at T = 0.1? At T = 0.01?", "e^(−1) ≈ 37%; e^(−10) ≈ 0.005%."),
            ("What does annealing become when T is close to 0?", "Iterative improvement: only changes that do not lengthen the tour are accepted."),
            ("Why reverse a stretch of the tour rather than swap two cities?", "A reversal changes only two roads, so Δ takes four distances to compute; swapping two cities changes four roads."),
            ("Slower cooling took more work in the program. Why not always cool as slowly as possible?", "The work grows quickly and the gains shrink; for a guarantee the time can exceed trying every tour."),
            ("Why finish with a pass of iterative improvement?", "So the result cannot be shortened by any single reversal, whatever the last random choices were."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Optimization by Simulated Annealing (1983)", text="*Science* 220 (4598), 13 May 1983, by Kirkpatrick, Gelatt and Vecchi of IBM.",
                 draw=C.draw_manuscript, link="https://zhanggroup.org/teaching/literature/Kirkpatrick_Annealing_Science_1983.pdf", link_text="The paper (PDF, on a research group's teaching page)", licence="Drawn placeholder."),
            dict(title="Černý's paper (1985)", text="*Journal of Optimization Theory and Applications* 45 (1), January 1985.",
                 draw=C.draw_manuscript, link="https://mk.bcgsc.ca/papers/cerny-travelingsalesman.pdf", link_text="The paper (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "SimulatedAnnealing", d["checks"],
                           "50 sets of 12 cities against Held and Karp's exact optimum, 10 sets of 200 cities, five cooling rates, and one run's acceptance at every temperature; every result is checked to be a tour, and nothing beats the exact optimum.",
                           ["static int[] anneal(double[][] c, int[] t, double cool)"]),
    ]
    return dict(
        title="Simulated Annealing", date="1983–1985",
        description="Era 7, topic 4 of The Algorithm Evolution Atlas: Kirkpatrick, Gelatt and Vecchi's simulated annealing, Černý's travelling salesman, the Metropolis rule and cooling schedules.",
        lede="Improving a design one small change at a time gets stuck at the first dead end. Three physicists at IBM borrowed a rule for simulating hot atoms: sometimes accept a change for the worse, and do it less and less often as the temperature falls.",
        fieldnote=f"On {ex['n']} cities, where the best tour can be found exactly, the careful improver found it {ex['dh']} times in {ex['sets']}; the annealer, which sometimes made things worse on purpose, found it {ex['ah']} times. I recorded that this species learned to search by imitating the cooling of metal.",
        card=[("When", "1983 (Černý independently, 1985)"),
              ("Where", "IBM Yorktown Heights; Bratislava"),
              ("What hurt", "Small improving steps stop at the first dead end"),
              ("The fix", "Accept worse steps with probability e^(−Δ/T); cool slowly"),
              ("Checked", f"Best 12-city tour found {ex['ah']} of {ex['sets']} times (improving only: {ex['dh']})")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `SimulatedAnnealing.java`.",
    )
