"""Era 8, topic 2: Goemans and Williamson's MAX CUT. Every number is parsed from GoemansWilliamson.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"constant: .*? is ([\d.]+), reached at theta = ([\d.]+) radians \(([\d.]+) degrees\)", ln):
            d["const"] = dict(alpha=m.group(1), theta=m.group(2), deg=m.group(3))
        elif m := re.match(r"cycle: the 5-cycle: relaxation ([\d.]+) \(formula .*? = ([\d.]+)\), certified ; best cut (\d+) ; best / relaxation = ([\d.]+) ; neighbouring arrows at ([\d.]+) degrees ; expected random-plane cut ([\d.]+)", ln):
            d["c5"] = dict(sdp=m.group(1), formula=m.group(2), best=m.group(3), ratio=m.group(4), angle=m.group(5), exp=m.group(6))
        elif m := re.match(r"random: (\d+) networks of (\d+) nodes, .*? ; relaxation certified optimal on all ; expected random-plane cut / best cut: average ([\d.]+), lowest ([\d.]+) ; best of 100 planes / best cut: average ([\d.]+), equal to the best on (\d+) ; best cut / relaxation: lowest ([\d.]+) ; coin flip \(expected\) / best: average ([\d.]+) ; local search from a coin flip / best: average ([\d.]+), lowest ([\d.]+), equal to the best on (\d+)", ln):
            d["rand"] = dict(g=m.group(1), n=m.group(2), avg=m.group(3), low=m.group(4), planes=m.group(5), planesEq=m.group(6), gap=m.group(7),
                             coin=m.group(8), loc=m.group(9), locLow=m.group(10), locEq=m.group(11))
        elif m := re.match(r"large: (\d+) nodes, (\d+) links .*?, arrows in (\d+) dimensions ; relaxation ([\d.]+) ; the dual certificate proves no cut exceeds ([\d.]+) ; expected random-plane cut ([\d.]+) ; best of 100 planes, each improved by local search: (\d+), so at least ([\d.]+)% of the best possible cut ; best of 100 coin flips with local search: (\d+)", ln):
            d["large"] = dict(n=m.group(1), links=m.group(2), dims=m.group(3), sdp=m.group(4), bound=m.group(5), exp=m.group(6), best=m.group(7), pct=m.group(8), coin=m.group(9))
        elif m := re.match(r"petersen: .*? start seed (\d+) ; relaxation ([\d.]+), certified ; best cut (\d+) ; expected random-plane cut ([\d.]+) ; arrows rounded to 4 decimals: (.*?) ; 20 random planes from seed (\d+) .*?: ([\d ]+) ; average ([\d.]+), best (\d+)", ln):
            d["pet"] = dict(sdp=m.group(2), best=int(m.group(3)), exp=m.group(4), arrows=[[float(x) for x in v.split(",")] for v in m.group(5).split()],
                            seed=int(m.group(6)), cuts=[int(x) for x in m.group(7).split()], avg=m.group(8), top=m.group(9))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def ratio_svg(d):
    """theta/pi against (1 - cos theta)/2, and their ratio, with the minimum marked."""
    a, th = float(d["const"]["alpha"]), float(d["const"]["theta"])

    def draw(t, standalone):
        o = []
        W, H = 760, 340
        x0, x1, y0, y1 = 70, 720, 270, 60
        X = lambda v: x0 + v / math.pi * (x1 - x0)
        Y = lambda p: y0 - p * (y0 - y1)
        o.append(C.text(20, 26, "Two arrows at angle θ: cut by a random plane, against what the relaxation counts", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        for p in (0, 0.5, 1):
            o.append(C.text(x0 - 8, Y(p) + 4, f"{p:g}", t["muted"], 11.5, "end"))
        for k, lab in ((0, "0"), (1, "π/4"), (2, "π/2"), (3, "3π/4"), (4, "π")):
            o.append(C.text(X(k * math.pi / 4), y0 + 18, lab, t["muted"], 11.5, "middle"))
        o.append(C.text((x0 + x1) / 2, y0 + 40, "the angle θ between the two arrows", t["muted"], 12, "middle"))
        pts = [i * math.pi / 120 for i in range(121)]
        o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(v):.1f},{Y(v / math.pi):.1f}" for i, v in enumerate(pts)), t["red"], "none", 2.4))
        o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(v):.1f},{Y((1 - math.cos(v)) / 2):.1f}" for i, v in enumerate(pts)), t["blue"], "none", 2.4))
        o.append(C.line(X(0.08), Y(0.95) - 4, X(0.22), Y(0.95) - 4, t["red"], 2.4))
        o.append(C.text(X(0.26), Y(0.95), "θ/π: the chance a random plane cuts the link", t["red"], 12, "start", 700))
        o.append(C.line(X(0.08), Y(0.86) - 4, X(0.22), Y(0.86) - 4, t["blue"], 2.4))
        o.append(C.text(X(0.26), Y(0.86), "(1 − cos θ)/2: what the relaxation counted", t["blue"], 12, "start", 700))
        o.append(C.line(X(th), Y(0), X(th), Y((1 - math.cos(th)) / 2), t["ink"], 1.2, 'stroke-dasharray="4 4"'))
        o.append(C.text(X(th) - 8, Y(0.08), f"θ = {d['const']['theta']}: the ratio is smallest, {d['const']['alpha']}", t["ink"], 12, "end", 700))
        return C.svg_doc(W, H, "".join(o), "The cut chance against the relaxation's count", t, standalone, 0.55, 760)
    return draw


GW_HTML = """
<div class="board gw-board">
  <div style="min-width:0"><div class="gw-view" id="gw-view"></div></div>
  <div style="min-width:0">
    <div class="gw-btns"><button type="button" class="primary" id="gw-plane">Throw a random plane</button><button type="button" id="gw-coin">Flip a coin per node</button><button type="button" id="gw-reset">Start again</button></div>
    <div class="gw-stats" id="gw-stats"></div>
    <p class="say" id="gw-say" aria-live="polite"></p>
  </div>
</div>
"""

GW_CSS = """
.gw-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.gw-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.gw-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

GW_JS = r"""
(() => {
  const view = document.getElementById("gw-view");
  if (!view) return;
  const V = __ARROWS__, PROG = __CUTS__, SEED = __SEED__, BEST = __BEST__, SDP = "__SDP__", EXP = "__EXP__";
  const E = [[0,1],[1,2],[2,3],[3,4],[4,0],[0,5],[1,6],[2,7],[3,8],[4,9],[5,7],[7,9],[9,6],[6,8],[8,5]];
  const pos = [];
  for (let i = 0; i < 5; i++) { const a = -Math.PI / 2 + i * 2 * Math.PI / 5; pos[i] = [200 + 160 * Math.cos(a), 205 + 160 * Math.sin(a)]; pos[i + 5] = [200 + 75 * Math.cos(a), 205 + 75 * Math.sin(a)]; }
  let s32, side = null, planes = [], coins = [];
  function next32() { s32 = (Math.imul(s32, 1664525) + 1013904223) | 0; return (s32 >>> 0) / 4294967296; }
  function direction() { const r = [0, 0, 0, 0, 0]; while (true) { let len = 0; for (let d = 0; d < 5; d++) { r[d] = 2 * next32() - 1; len += r[d] * r[d]; } if (len <= 1 && len > 1e-12) return r; } }
  const cut = sd => E.filter(([a, b]) => sd[a] !== sd[b]).length;
  function plane() {
    const r = direction();
    side = V.map(v => { let s = 0; for (let d = 0; d < 5; d++) s += v[d] * r[d]; return s >= 0; });
    const c = cut(side); planes.push(c);
    const k = planes.length, pg = PROG[k - 1];
    draw(`Plane ${k}: the nodes whose arrows point to one side of it are red, the rest blue; ${c} of the 15 links are cut.` + (pg !== undefined ? ` The program's plane ${k} cut ${pg}.` : ""));
  }
  function coin() { side = V.map(() => Math.random() < 0.5); const c = cut(side); coins.push(c); draw(`A coin for each node: ${c} links cut. On average a coin cuts half the links, 7.5.`); }
  function draw(msg) {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 400 400", role: "img", "aria-label": "The Petersen graph"}, view);
    for (const [a, b] of E) {
      const isCut = side && side[a] !== side[b];
      sv("line", {x1: pos[a][0], y1: pos[a][1], x2: pos[b][0], y2: pos[b][1], stroke: isCut ? "var(--ink)" : "var(--axis)", "stroke-width": isCut ? 3 : 1.5, "stroke-dasharray": isCut ? null : "4 4"}, svg);
    }
    pos.forEach((p, i) => sv("circle", {cx: p[0], cy: p[1], r: 13, fill: side ? (side[i] ? "var(--red)" : "var(--blue)") : "var(--paper)", stroke: "var(--ink)", "stroke-width": 1.5}, svg));
    const st = document.getElementById("gw-stats"); st.innerHTML = "";
    const avg = a => a.length ? (a.reduce((x, y) => x + y, 0) / a.length).toFixed(2) : "–";
    el("div", {}, st, `best possible cut: ${BEST} of 15 (relaxation ${SDP})`);
    el("div", {}, st, `random planes: ${planes.length}, average ${avg(planes)}, best ${planes.length ? Math.max(...planes) : "–"}`);
    el("div", {}, st, `expected for a random plane: ${EXP}`);
    el("div", {}, st, `coin flips: ${coins.length}, average ${avg(coins)}`);
    if (msg) document.getElementById("gw-say").textContent = msg;
  }
  function reset() { s32 = SEED; side = null; planes = []; coins = []; draw("The Petersen graph: 10 nodes, 15 links. Each node has an arrow in 5 dimensions from the relaxation. Throw a plane through the middle and split the nodes by side."); }
  document.getElementById("gw-plane").addEventListener("click", plane);
  document.getElementById("gw-coin").addEventListener("click", coin);
  document.getElementById("gw-reset").addEventListener("click", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Goemans and Williamson combined older ideas, and where they led")
    W = 210
    nodes = {
        "np": (20, 20, "NP-hardness", "no fast exact MAX CUT expected", "Era 6", "ink"),
        "coin": (395, 20, "A coin per node", "cuts half the links: a 1/2 guarantee", "Sahni and Gonzales", "ink"),
        "sdp": (770, 20, "Interior points", "convex programs solved in polynomial time", "Era 7", "ink"),
        "gw": (395, 180, "Goemans–Williamson", "⊕ arrows for sides, a random plane to round", "MIT and IBM, 1994–1995", "red"),
        "ugc": (20, 340, "Maybe optimal", "none better, if Unique Games holds", "Khot and colleagues", "ink"),
        "more": (770, 340, "Many relaxations", "other problems attacked the same way", "Steele Prize citation, 2022", "ink"),
        "today": (395, 490, "0.87856", "a guarantee, not just a good average", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("np", "gw", ports=("bottom", "top:0.15"))
    D.edge("coin", "gw", ports=("bottom", "top"), label="beaten", at=0.5, dx=8, anchor="start")
    D.edge("sdp", "gw", ports=("bottom", "top:0.85"))
    D.edge("gw", "ugc", ports=("bottom:0.15", "top"))
    D.edge("gw", "more", ports=("bottom:0.85", "top"))
    D.edge("gw", "today", ports=("bottom", "top"))
    D.text(20, 615, "The hardness result is conditional: the Unique Games Conjecture is unproved.", "caption")
    return D


def chain(d):
    r, lg = d["rand"], d["large"]
    steps = [
        (f"Trying every split of {r['n']} nodes means 32,768 cuts; of 400 nodes, 2³⁹⁹",
         f"Flip a coin per node: half the links on average, {float(r['coin']) * 100:.0f}% of the best here", "the 1/2 guarantee"),
        ("Half is all a coin can promise, and for years no method promised more",
         f"Arrows and a random plane: expected {float(r['avg']) * 100:.1f}% of the best, never below {float(r['low']) * 100:.1f}%", "Goemans and Williamson, 1994"),
        ("On a big network the best cut is unknown: how good is a cut?",
         f"The relaxation bounds every cut: {lg['best']} is at least {lg['pct']}% of the best on {lg['n']} nodes", "the dual certificate"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a coin flip to a certified 0.878")
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
    k, c5, r, lg, pe = d["const"], d["c5"], d["rand"], d["large"], d["pet"]
    rand_rows = [
        ["Coin flip (expected)", f"{float(r['coin']):.4f}", "—", "—"],
        ["Local search from a coin flip", f"{float(r['loc']):.4f}", f"{float(r['locLow']):.4f}", f"{r['locEq']} of {r['g']}"],
        ["Random plane (expected)", f"{float(r['avg']):.4f}", f"{float(r['low']):.4f}", "—"],
        ["Best of 100 random planes", f"{float(r['planes']):.4f}", "—", f"{r['planesEq']} of {r['g']}"],
    ]
    pet_rows = [[str(i + 1), str(c)] for i, c in enumerate(pe["cuts"])]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. NP-completeness (Era 6) said that MAX CUT probably has no fast exact method. A coin flip per node promised half the links. Interior-point methods (Era 7) had made convex programs, including semidefinite ones, solvable in polynomial time. Goemans and Williamson relaxed each node's side into an arrow, solved for the best arrows, and rounded them with a random plane. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Goemans and Williamson's algorithm. Blue: its guarantee."),
        ]),
        dict(id="play", eyebrow="Try it", title="Throw a plane through the arrows", toc="Try it", blocks=[
            dict(type="p", text=f"The Petersen graph has 10 nodes and 15 links; its best cut has {pe['best']} links. The program solved the relaxation and gave every node an arrow in 5 dimensions. Each throw picks a random plane through the middle; nodes on one side turn red, the rest blue, and the cut links are drawn solid. The planes come from the program's own generator, so the widget's cuts match the program's, throw by throw. Compare with a coin per node."),
            dict(type="widget", html=GW_HTML, js=GW_JS.replace("__ARROWS__", json.dumps(pe["arrows"])).replace("__CUTS__", json.dumps(pe["cuts"])).replace("__SEED__", str(pe["seed"]))
                 .replace("__BEST__", str(pe["best"])).replace("__SDP__", pe["sdp"]).replace("__EXP__", pe["exp"]), css=GW_CSS,
                 fallback=dict(type="table", head=["Plane", "Links cut (of 15)"], num=[0, 1], rows=pet_rows),
                 note="In the interactive edition you can throw the planes yourself and compare them with coin flips."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Relax, solve, round", toc="How it works", blocks=[
            dict(type="p", text="**The problem.** Give each node i a side xᵢ = +1 or −1. A link between i and j is cut when xᵢ ≠ xⱼ, so the cut counts (1 − xᵢxⱼ)/2 over the links. Maximize that."),
            dict(type="p", text="**The relaxation.** Replace each number xᵢ by a unit arrow vᵢ in n dimensions and the product xᵢxⱼ by the dot product vᵢ · vⱼ. Arrows in one dimension are just ±1, so the best arrows do at least as well as the best cut. Finding the best arrows is a semidefinite program, which can be solved to any accuracy in polynomial time. (The program uses a simple low-rank method: turn each arrow to point away from the sum of its neighbours', over and over, then prove the answer optimal with a certificate from the dual program.)"),
            dict(type="p", text="**The rounding.** Pick a random plane through the origin and put each node on the side its arrow points to. Two arrows at angle θ land on opposite sides with probability θ/π. The relaxation counted that link as (1 − cos θ)/2. The ratio of the two is never below 0.87856, so the expected cut is at least 0.87856 times the relaxation, and so at least 0.87856 times the best cut."),
            dict(type="svg", name="ratio", draw=ratio_svg(d), alt="Theta over pi against one minus cos theta over two", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Solve an easier problem exactly, then round its answer at random in a way whose loss you can bound. The random plane loses at most 12% of what the relaxation counted, link by link."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Guarantee and practice", toc="Measured", blocks=[
            dict(type="p", text=f"**The constant.** The smallest value of 2θ/(π(1 − cos θ)) is {k['alpha']}, at θ = {k['theta']} radians ({k['deg']}°), as the paper states."),
            dict(type="p", text=f"**The 5-cycle.** The relaxation's value is {c5['sdp']}, which equals (5/2)(1 + cos(π/5)) = {c5['formula']}; neighbouring arrows sit {c5['angle']}° apart. The best cut has {c5['best']} links, so here the best cut is only {c5['ratio']} of the relaxation, and the random plane's expected cut is exactly {float(c5['exp']):g}."),
            dict(type="p", text=f"**{r['g']} random networks of {r['n']} nodes**, each link present with probability ½. Every relaxation was certified optimal by its dual, and every best cut found by trying all 32,768 splits. As fractions of the best cut:"),
            dict(type="table", head=["Method", "Average", "Lowest", "Found the best"], num=[1, 2], rows=rand_rows, hl=2),
            dict(type="p", text=f"The best cut was never less than {r['gap']} of the relaxation, so the relaxation itself was always within {100 - float(r['gap']) * 100:.0f}% of the truth."),
            dict(type="p", text=f"**{lg['n']} nodes**, {lg['links']} links: far too many splits to try. The relaxation (arrows in {lg['dims']} dimensions) is {lg['sdp']}, and its dual proves that no cut exceeds {lg['bound']}. The expected random-plane cut is {lg['exp']}; the best of 100 planes, each improved by local search, cut {lg['best']} links, so at least {lg['pct']}% of the best possible. The best of 100 coin flips with the same local search cut {lg['coin']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A constant that stood still for years", toc="The evidence", blocks=[
            dict(type="p", text="Goemans (MIT) and Williamson (IBM T. J. Watson), *Journal of the ACM* 42(6), November 1995 (preliminary version at STOC, Montreal, 1994): \"We present randomized approximation algorithms for the maximum cut (MAX CUT)\" that \"always deliver solutions of expected value at least .87856 times the optimal value\". The rounding picks \"a random hyperplane through the origin (with r as its normal)\"; the constant \"achieves its value for θ = 2.331122...\". Before them, the 1/2 of Sahni and Gonzales stood, and \"no progress was made in improving the constant\". The journal version notes that the conference version's derandomization \"had a subtle error\"."),
            dict(type="p", text="The 2022 AMS Steele Prize for Seminal Contribution to Research went to the paper, which \"yields an approximation ratio of 0.878\" and led many problems to be \"studied via relaxation to semidefinite programs\". Khot and O'Donnell (*Theory of Computing*, 2009) report hardness results that \"match the above two guarantees of Goemans and Williamson, assuming Khot's 'Unique Games Conjecture'\": if that unproved conjecture holds, no fast algorithm can promise more than 0.878."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Linear programming, one dimension up", toc="Full circle", blocks=[
            dict(type="p", text="The interior-point methods of Era 7 solve linear programs by walking through the inside of a region of numbers. Semidefinite programs are the same idea with matrices in place of numbers, and the same methods solve them. Compressed sensing (topic 12) is another relaxation that turned out to be exact: swap a hard count of nonzero entries for a sum of absolute values."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"A coin promised half. Arrows and a plane promised {k['alpha']}, and on {r['g']} random networks delivered {float(r['avg']) * 100:.1f}% on average."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Two arrows point in opposite directions (θ = π). What is the chance a random plane separates them, and what did the relaxation count?", "Both are 1: the plane always separates them, and (1 − cos π)/2 = 1."),
            ("Two arrows are at right angles. Compare θ/π with (1 − cos θ)/2.", "θ/π = 1/2 and (1 − cos θ)/2 = 1/2: no loss at all."),
            ("Why is the relaxation's value at least the best cut?", "Any cut is a choice of arrows that all lie on one line (±1), so it is one of the relaxation's options."),
            ("A triangle (3 nodes, 3 links): what is the best cut, and roughly what is the relaxation?", "The best cut has 2 links. Three arrows 120° apart give 3 × (1 − cos 120°)/2 = 2.25."),
            ("Why is 0.878 called a guarantee and not a typical result?", "It holds for every network, in expectation; on the random networks here the plane did much better, 96% on average."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Goemans and Williamson's paper (1995)", text="*Journal of the ACM* 42(6): the relaxation, the random hyperplane and the constant.",
                 draw=C.draw_manuscript, link="https://math.mit.edu/~goemans/PAPERS/maxcut-jacm.pdf", link_text="The paper (PDF, MIT)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "GoemansWilliamson", d["checks"],
                           "the constant on a grid of 100,000 angles, every sweep of the coordinate method, the dual certificate for every relaxation, the guarantee on 200 random networks against exhaustive search, and the Petersen graph's planes.",
                           ["static double[][] relax(double[][] w, int k)", "static double expectedCut(double[][] w, double[][] v)"]),
    ]
    return dict(
        title="Approximation by Semidefinite Programming", date="1994–1995",
        description="Era 8, topic 2 of The Algorithm Evolution Atlas: Goemans and Williamson's 0.878-approximation for MAX CUT, with arrows for sides, a semidefinite relaxation and a random hyperplane, checked against exhaustive search.",
        lede="MAX CUT has no known fast exact method, and for years nothing beat the half that a coin flip guarantees. Goemans and Williamson gave each node an arrow, found the best arrows, and cut them with a random plane: at least 87.856% of the best, always.",
        fieldnote=f"I asked for the best way to split {r['g']} small networks and checked every answer by trying all 32,768 splits. A coin got {float(r['coin']) * 100:.0f}% of the best links on average; a random plane through the arrows got {float(r['avg']) * 100:.1f}%, and never less than {float(r['low']) * 100:.1f}%. On a network of {lg['n']} nodes nobody can try every split, but the arrows themselves proved my best cut was within {100 - float(lg['pct']):.1f}% of perfect.",
        card=[("When", "STOC 1994; Journal of the ACM, November 1995"),
              ("Where", "MIT; IBM T. J. Watson Research Center"),
              ("What hurt", "MAX CUT is NP-hard; the best guarantee was 1/2"),
              ("The fix", "Arrows for sides, a semidefinite program, a random plane"),
              ("Checked", f"Constant {k['alpha']} at θ = {k['theta']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `GoemansWilliamson.java`.",
    )
