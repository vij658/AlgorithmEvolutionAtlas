"""Era 7, topic 8: the Barnes-Hut tree code. Every number is parsed from BarnesHut.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"tree: ([\d,]+) stars in a Plummer sphere ; the tree has ([\d,]+) cubes and is (\d+) levels deep ; .*?\(([\d,]+) interactions = N\(N-1\)\) and the forces equal the direct sum to a relative difference of ([\d.eE-]+)", ln):
            d["tree"] = dict(n=m.group(1), cells=m.group(2), depth=m.group(3), inter=m.group(4), diff=m.group(5))
        elif m := re.match(r"scaling: [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"N=([\d,]+): direct ([\d,]+) \(([\d,]+) per star\), tree ([\d,]+) \(([\d,]+) per star\), (\d+) times fewer", part)
                rows.append(dict(n=mm.group(1), direct=mm.group(2), dper=mm.group(3), tree=mm.group(4), tper=mm.group(5), ratio=mm.group(6)))
            d["scale"] = rows
        elif m := re.match(r"accuracy: ([\d,]+) stars, [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(2).split(" ; "):
                mm = re.match(r"theta ([\d.]+): ([\d,]+) interactions per star, median error ([\d.]+)%, 99th percentile ([\d.]+)%", part)
                rows.append(dict(theta=mm.group(1), per=mm.group(2), med=mm.group(3), p99=mm.group(4)))
            d["acc"] = dict(n=m.group(1), rows=rows)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def criterion_svg(d):
    """The opening test: a cube of width s at distance d is one mass if s / d < theta."""
    def draw(t, standalone):
        o = []
        W, H = 760, 340
        o.append(C.text(20, 26, "The opening test: seen from the star, does the cube look small?", t["ink"], 13, "start", 700))
        sx, sy = 110, 170
        o.append(C.circle(sx, sy, 8, t["red"]))
        o.append(C.text(sx, sy + 28, "the star", t["red"], 12, "middle", 700))
        cx, cy, half = 560, 150, 70
        o.append(C.rect(cx - half, cy - half, 2 * half, 2 * half, t["wash"], t["ink"], 1.8))
        pts = [(520, 110), (545, 175), (590, 125), (600, 190), (530, 200), (575, 150), (610, 105)]
        for x, y in pts:
            o.append(C.circle(x, y, 3.5, t["ink"]))
        gx, gy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        o.append(C.circle(gx, gy, 6, t["blue"]))
        o.append(C.text(gx + 10, gy - 8, "centre of mass", t["blue"], 12, "start", 700))
        o.append(C.line(sx + 10, sy, gx - 8, gy, t["axis"], 1.4, ";stroke-dasharray:5 4"))
        o.append(C.text((sx + gx) / 2, (sy + gy) / 2 - 10, "d", t["ink"], 15, "middle", 700))
        o.append(C.line(cx - half, cy + half + 18, cx + half, cy + half + 18, t["ink"], 1.4))
        o.append(C.line(cx - half, cy + half + 12, cx - half, cy + half + 24, t["ink"], 1.4))
        o.append(C.line(cx + half, cy + half + 12, cx + half, cy + half + 24, t["ink"], 1.4))
        o.append(C.text(cx, cy + half + 38, "s", t["ink"], 15, "middle", 700))
        o.append(C.text(20, H - 30, "If s / d < θ, the star feels the cube as one point with the cube's total mass at its centre of mass.", t["muted"], 12))
        o.append(C.text(20, H - 12, "If not, the cube is opened and its eight smaller cubes are tested the same way. θ = 0 opens everything: the exact sum.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "The Barnes-Hut opening criterion", t, standalone, 0.55, 760)
    return draw


BH_HTML = """
<div class="board bh-board">
  <div style="min-width:0">
    <div class="bh-view" id="bh-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls"><label>θ <input type="range" id="bh-theta" min="0" max="1.5" step="0.05" value="0.5"></label><span id="bh-tv" class="bh-tv">0.50</span></div>
    <div class="bh-btns"><button type="button" id="bh-new">New cluster</button></div>
    <div class="bh-stats" id="bh-stats"></div>
    <p class="say" id="bh-say" aria-live="polite"></p>
  </div>
</div>
"""

BH_CSS = """
.bh-view svg{display:block;width:100%;height:auto;background:var(--wash);cursor:crosshair}
.bh-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.bh-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
.bh-board input[type=range]{width:12em;padding:0;border:none;background:none}
.bh-tv{font:14px var(--mono)}
"""

BH_JS = r"""
(() => {
  const view = document.getElementById("bh-view");
  if (!view) return;
  const N = 400;
  let seed = 1986, P = [], root, chosen = 0;
  const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  function cluster() {
    P = [];
    const centres = [[0.32, 0.4, 0.09], [0.7, 0.62, 0.12], [0.55, 0.22, 0.05]];
    while (P.length < N) {
      const c = centres[P.length % 3], r = c[2] * Math.sqrt(-2 * Math.log(rnd() + 1e-12)), a = 2 * Math.PI * rnd();
      const x = c[0] + r * Math.cos(a), y = c[1] + r * Math.sin(a);
      if (x > 0.01 && x < 0.99 && y > 0.01 && y < 0.99) P.push([x, y]);
    }
    build();
    let bd = 1e9; P.forEach((p, i) => { const dd = (p[0] - 0.36) ** 2 + (p[1] - 0.44) ** 2; if (dd < bd) { bd = dd; chosen = i; } });
  }
  // a quadtree: each cell has a centre, half-width, mass and mass-weighted position
  function cell(cx, cy, h) { return {cx, cy, h, m: 0, mx: 0, my: 0, body: -1, kids: null}; }
  function insert(c, b) {
    if (!c.kids && c.body < 0 && c.m === 0) { c.body = b; c.m = 1; c.mx = P[b][0]; c.my = P[b][1]; return; }
    if (!c.kids) { c.kids = [null, null, null, null]; const old = c.body; c.body = -1; place(c, old); }
    place(c, b); c.m += 1; c.mx += P[b][0]; c.my += P[b][1];
  }
  function place(c, b) {
    const k = (P[b][0] > c.cx ? 1 : 0) | (P[b][1] > c.cy ? 2 : 0);
    if (!c.kids[k]) { const h = c.h / 2; c.kids[k] = cell(c.cx + (k & 1 ? h : -h), c.cy + (k & 2 ? h : -h), h); }
    insert(c.kids[k], b);
  }
  function build() { root = cell(0.5, 0.5, 0.5); P.forEach((_, b) => insert(root, b)); }
  const SOFT = 1e-4;
  function force(c, b, theta, acc, used) {
    if (c.m === 0 || c.body === b) return;
    const gx = c.mx / c.m, gy = c.my / c.m, dx = gx - P[b][0], dy = gy - P[b][1], d2 = dx * dx + dy * dy;
    if (!c.kids || 4 * c.h * c.h < theta * theta * d2) {
      const inv = 1 / Math.sqrt(d2 + SOFT), f = c.m * inv * inv * inv;
      acc[0] += f * dx; acc[1] += f * dy; used.push(c); return;
    }
    c.kids.forEach(k => k && force(k, b, theta, acc, used));
  }
  function direct(b) {
    const a = [0, 0];
    P.forEach((p, j) => { if (j === b) return; const dx = p[0] - P[b][0], dy = p[1] - P[b][1], inv = 1 / Math.sqrt(dx * dx + dy * dy + SOFT), f = inv * inv * inv; a[0] += f * dx; a[1] += f * dy; });
    return a;
  }
  function draw() {
    const theta = parseFloat(document.getElementById("bh-theta").value);
    document.getElementById("bh-tv").textContent = theta.toFixed(2);
    view.innerHTML = "";
    const S = 400, svg = sv("svg", {viewBox: `0 0 ${S} ${S}`}, view);
    svg.addEventListener("click", ev => {
      const r = svg.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width, y = 1 - (ev.clientY - r.top) / r.height;
      let best = 0, bd = 1e9; P.forEach((p, i) => { const dd = (p[0] - x) ** 2 + (p[1] - y) ** 2; if (dd < bd) { bd = dd; best = i; } });
      chosen = best; draw();
    });
    const acc = [0, 0], used = [];
    force(root, chosen, theta, acc, used);
    const ex = direct(chosen), err = Math.hypot(acc[0] - ex[0], acc[1] - ex[1]) / Math.hypot(ex[0], ex[1]);
    used.forEach(c => {
      if (c.kids) sv("rect", {x: (c.cx - c.h) * S, y: (1 - c.cy - c.h) * S, width: 2 * c.h * S, height: 2 * c.h * S, fill: "var(--blue)", "fill-opacity": 0.12, stroke: "var(--blue)", "stroke-width": 1}, svg);
    });
    P.forEach((p, i) => sv("circle", {cx: p[0] * S, cy: (1 - p[1]) * S, r: i === chosen ? 6 : 1.9, fill: i === chosen ? "var(--red)" : "var(--ink)"}, svg));
    used.forEach(c => { if (c.kids) sv("circle", {cx: c.mx / c.m * S, cy: (1 - c.my / c.m) * S, r: 2 + Math.sqrt(c.m) * 0.6, fill: "none", stroke: "var(--blue)", "stroke-width": 1.4}, svg); });
    const cells = used.filter(c => c.kids).length, singles = used.length - cells;
    const st = document.getElementById("bh-stats"); st.innerHTML = "";
    el("div", {}, st, `stars: ${N}`);
    el("div", {}, st, `interactions for the red star: ${used.length} (direct: ${N - 1})`);
    el("div", {}, st, `  of which ${cells} blue cells used as one mass, ${singles} single stars`);
    el("div", {}, st, `force error against the exact sum: ${(100 * err).toFixed(3)}%`);
    document.getElementById("bh-say").textContent = theta === 0
      ? "θ = 0: every cell is opened, so the red star meets every other star one by one: the exact sum."
      : `Each blue square is a whole cell felt as one mass at its centre of mass (blue ring). Click another star, or move θ: larger θ uses bigger cells, fewer interactions, larger error.`;
  }
  document.getElementById("bh-theta").addEventListener("input", draw);
  document.getElementById("bh-new").addEventListener("click", () => { cluster(); draw(); });
  cluster(); draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the Barnes–Hut tree code combined older ideas, and where it led")
    W = 210
    nodes = {
        "cm": (20, 20, "Centre of mass", "a distant body pulls like one point", "\"not new\": Newton", "ink"),
        "tr": (395, 20, "Trees that divide space", "split a box into smaller boxes", "", "ink"),
        "dc": (770, 20, "Divide and conquer", "split the problem, solve the parts", "Era 6", "ink"),
        "bh": (395, 180, "Barnes–Hut", "⊕ an opening angle θ decides which cells to summarize", "Barnes and Hut, 1986", "red"),
        "fmm": (20, 340, "Fast multipole method", "⊕ boxes exchange expansions: O(N)", "Greengard and Rokhlin, 1987", "ink"),
        "par": (770, 340, "Parallel tree codes", "trees split across many processors", "", "ink"),
        "today": (395, 490, "Today", "1992 Gordon Bell Prize: 17 million particles on the Intel Delta", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("cm", "bh", ports=("bottom", "top:0.15"))
    D.edge("tr", "bh", ports=("bottom", "top"))
    D.edge("dc", "bh", ports=("bottom", "top:0.85"))
    D.edge("bh", "fmm", ports=("bottom:0.15", "top"))
    D.edge("bh", "par", ports=("bottom:0.85", "top"))
    D.edge("par", "today", ports=("bottom", "top:0.85"))
    D.text(20, 615, "Today: from Demmel's Berkeley lecture (Warren and Salmon). The fast multipole method is separate work by other authors.", "caption")
    return D


def chain(d):
    sc, ac = d["scale"], d["acc"]
    big = sc[-1]
    half = next(r for r in ac["rows"] if r["theta"] == "0.5")
    steps = [
        (f"Direct gravity takes N(N − 1) interactions: {big['direct']} for {big['n']} stars, every time step",
         f"A tree of cubes, distant cubes felt as one mass: {big['tree']}, {big['ratio']} times fewer", "Barnes and Hut, 1986"),
        ("An approximation has an error, and no single error suits every problem",
         f"One knob, θ: at θ = 0.5 the median force error was {half['med']}%; θ = 0 gives the exact sum", "the opening angle"),
        ("Still N log N, and \"Good for low accuracy calculations\"",
         "The fast multipole method: O(N), with more information per box for more accuracy", "Greengard and Rokhlin, 1987"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from every pair to a tree of summaries")
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
    tr, sc, ac = d["tree"], d["scale"], d["acc"]
    big = sc[-1]
    half = next(r for r in ac["rows"] if r["theta"] == "0.5")
    sc_rows = [[r["n"], r["dper"], r["tper"], r["ratio"]] for r in sc]
    ac_rows = [[r["theta"], r["per"], r["med"] + "%", r["p99"] + "%"] for r in ac["rows"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A distant crowd of stars pulls almost like one heavy star at its centre of mass, an approximation as old as Newton. Barnes and Hut made it systematic: a tree of cubes, each split into eight, and one rule (the opening angle θ) for when a cube is far enough away to be summarized. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Barnes and Hut's step. Blue: where tree codes went."),
        ]),
        dict(id="play", eyebrow="Try it", title="Which cells does one star feel?", toc="Try it", blocks=[
            dict(type="p", text="Four hundred stars in three clusters, in a quadtree (the flat version of Barnes and Hut's octree). The red star needs the pull of all the others. Each blue square is a whole cell that, seen from the red star, looks small enough (its width divided by its distance below θ) to be felt as one mass at its centre of mass, the blue ring; everything else is felt star by star. Move θ, click other stars, and compare the number of interactions and the error with the exact sum. These are the widget's own stars, so its numbers are not the program's."),
            dict(type="widget", html=BH_HTML, js=BH_JS, css=BH_CSS,
                 fallback=dict(type="table", head=["θ", "Interactions per star", "Median force error", "99th percentile"], num=[0, 1, 2, 3], rows=ac_rows),
                 note="In the interactive edition you can choose a star and change θ, and see which cells it feels as one mass."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A tree of cubes", toc="How it works", blocks=[
            dict(type="p", text="**Build.** Put all the stars in one box. Split any box holding more than one star into eight equal cubes, and repeat until every cube holds at most one star. Each cube records its total mass and its centre of mass."),
            dict(type="p", text="**Walk.** To find the pull on one star, start at the top:"),
            dict(type="svg", name="criterion", draw=criterion_svg(d), alt="The Barnes-Hut opening criterion", width=760),
            dict(type="p", text="A star meets a few cubes at each level of the tree, so it feels about log N of them instead of N − 1 stars, and a whole time step costs about N log N."),
            dict(type="callout", kind="key", label="Key idea",
                 text="You do not need to know every star in a far-away cluster to feel its pull: its total mass and centre are enough. A tree lets each star decide, cube by cube, how much detail it needs."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Interactions and errors", toc="Measured", blocks=[
            dict(type="p", text=f"**The tree.** {tr['n']} stars in a Plummer sphere (a standard model of a star cluster) gave a tree of {tr['cells']} cubes, {tr['depth']} levels deep. With θ = 0 every cube is opened: {tr['inter']} interactions, exactly N(N − 1), and forces equal to the direct sum to a relative difference of {C.sci(tr['diff'])}."),
            dict(type="p", text="**Interactions,** θ = 0.5. The direct count per star grows like N; the tree's grows far more slowly:"),
            dict(type="table", head=["Stars N", "Direct, per star", "Tree, per star", "Times fewer"], num=[0, 1, 2, 3], rows=sc_rows, hl=[len(sc_rows) - 1]),
            dict(type="p", text=f"**Accuracy,** {ac['n']} stars, every star's tree force against the exact sum:"),
            dict(type="table", head=["θ", "Interactions per star", "Median force error", "99th percentile"], num=[0, 1, 2, 3], rows=ac_rows, hl=[2]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A letter to Nature", toc="The evidence", blocks=[
            dict(type="p", text="Josh Barnes and Piet Hut, \"A hierarchical O(N log N) force-calculation algorithm\", *Nature* 324 (6096): 446–449, published 4 December 1986, a letter. Wikipedia's account: the method \"is notable for having order O(n log n) compared to a direct-sum algorithm which would be O(n2)\"; \"The space is recursively subdivided into octants until each subdivision contains 0 or 1 bodies\"; a cell is far enough away when the ratio of its width to its distance is \"smaller than a threshold value θ\"; \"larger values of θ increase the speed of the simulation but decreases its accuracy\", and with θ = 0 it \"degenerates to a direct-sum algorithm\"."),
            dict(type="p", text="Demmel's Berkeley lecture (2016) calls Barnes–Hut \"An O(N log N) approximate algorithm for the N-Body problem\", \"Good for low accuracy calculations\", and Greengard and Rokhlin's fast multipole method (1987) \"An O(N) approximate algorithm\", noting that the centre-of-mass approximation is \"not new\", going back to Newton, and that Warren and Salmon won the 1992 Gordon Bell Prize for a 17-million-particle simulation. Greengard's Wikipedia article says the fast multipole method is \"recognized as one of the top-ten algorithms of the 20th century\". The NEMO toolkit still distributes a tree code by Joshua E. Barnes, `hackforce`, whose opening tolerance defaults to 1.0."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Divide and conquer, in space", toc="Full circle", blocks=[
            dict(type="p", text="Era 6's fast algorithms split a problem into halves (the FFT) or blocks (Strassen) and combined the answers. Barnes and Hut split space itself, and combine not answers but summaries: a mass and a centre for each cube."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"For {big['n']} stars the direct sum needs {big['direct']} interactions per step; the tree, {big['tree']}. The cost of that saving, at θ = 0.5, is a median error of {half['med']}% in each force."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A cube 1 light-year wide is 10 light-years away. Is it opened at θ = 0.5?", "No: s/d = 0.1 < 0.5, so it is felt as one mass."),
            ("What happens with θ = 0?", "No cube passes the test, so every cube is opened down to single stars: the exact direct sum."),
            ("Doubling N roughly doubles the direct work per star. What does it do to the tree's work per star?", f"Adds roughly a constant: in the program, 100 times more stars took about {int(big['tper'].replace(',', '')) // int(sc[0]['tper'].replace(',', ''))} times more interactions per star."),
            ("Why does the error grow with θ?", "Larger θ summarizes nearer and bigger cubes, where the centre-of-mass approximation is cruder."),
            ("Why would astronomers accept any error at all?", "Because the direct sum limited simulations to a few thousand stars, far too few to look like a galaxy; a small, controlled error buys many more stars."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Barnes and Hut's letter (1986)", text="*Nature* 324: 446–449, 4 December 1986; only its record was opened for this book.",
                 draw=C.draw_manuscript, link="https://isidore.co/misc/Physics%20papers%20and%20books/Zotero/storage/IMT92TIC/324446a0.html", link_text="A saved copy of the Nature page", licence="Drawn placeholder."),
            dict(title="hackforce, a tree code by J. E. Barnes", text="Part of the NEMO stellar dynamics toolkit.",
                 draw=C.draw_book, link="https://bima.astro.umd.edu/nemo/man_html/hackforce.1.html", link_text="The manual page", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "BarnesHut", d["checks"],
                           "the exact forces with θ = 0 on 2,000 stars, the interaction counts for 1,000 to 100,000 stars, and the force error of every one of 10,000 stars at five values of θ.",
                           ["static void force(Cell c, int b, double theta, double[] acc)"]),
    ]
    return dict(
        title="The Barnes–Hut Tree Code", date="1986",
        description="Era 7, topic 8 of The Algorithm Evolution Atlas: Barnes and Hut's octree for gravity, the opening angle θ, N log N interactions, and the fast multipole method that followed.",
        lede="To move a galaxy's stars, every star must feel every other: the work grows with the square of their number. Barnes and Hut grouped the stars in a tree of cubes and let distant cubes pull as one.",
        fieldnote=f"For {big['n']} stars, the direct sum needs {big['direct']} interactions per step. The tree needed {big['tree']}, and each force came out within a fraction of a percent. This species learned to simulate its galaxies by agreeing not to look too closely at the far side.",
        card=[("When", "1986"),
              ("Where", "Published in Nature"),
              ("What hurt", "N(N − 1) interactions per time step"),
              ("The fix", "An octree; distant cubes as one mass; the opening angle θ"),
              ("Checked", f"{big['ratio']} times fewer interactions at N = {big['n']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BarnesHut.java`.",
    )
