"""Era 5, topic 13: Edmonds's matching and the "good" algorithm. Every number is parsed from Matching.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"flower: (\d+) vertices, edges ([\d\- ]+?) \(.*?\), pairs ([\d\- ]+?) to start, .*? the matching stays at (\d+) pairs ; .*? the path ([\d ]+) is found, and the matching grows to (\d+) pairs$", ln):
            d["fl"] = dict(n=m.group(1), edges=[tuple(map(int, e.split("-"))) for e in m.group(2).split()],
                           pairs=[tuple(map(int, e.split("-"))) for e in m.group(3).split()], naive=m.group(4), path=[int(x) for x in m.group(5).split()], ed=m.group(6))
        elif m := re.match(r"random: ([\d,]+) random graphs of 2 to (\d+) vertices ; .*? ; ([\d,]+) blossoms shrunk .*? looked at ([\d,]+) matchings in all, Edmonds's searches ([\d,]+) edge-steps$", ln):
            d["rand"] = dict(n=m.group(1), maxv=m.group(2), bl=m.group(3), brute=m.group(4), steps=m.group(5))
        elif ln.startswith("growth: "):
            d["growth"] = re.findall(r"(\d+) vertices: matchings of the complete graph (about [\d.]+ x 10\^\d+|[\d,]+) ; Edmonds on a random graph with a third of the edges: ([\d,]+) steps, (\d+) pairs", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
POS = {0: (40, 130), 1: (140, 130), 2: (250, 130), 3: (340, 60), 4: (450, 80), 5: (450, 180), 6: (340, 200), 7: (420, 10)}


def flower_svg(d):
    fl = d["fl"]

    def draw(t, standalone):
        o = []
        P = {k: (x, y + 30) for k, (x, y) in POS.items()}
        pairs = {tuple(sorted(p)) for p in fl["pairs"]}
        path = fl["path"]
        on_path = {tuple(sorted((path[i], path[i + 1]))) for i in range(len(path) - 1)}
        for a, b in fl["edges"]:
            e = tuple(sorted((a, b)))
            (x1, y1), (x2, y2) = P[a], P[b]
            if e in pairs:
                o.append(C.line(x1, y1, x2, y2, t["blue"], 6))
            else:
                o.append(C.line(x1, y1, x2, y2, t["axis"], 1.6))
            if e in on_path:
                o.append(C.line(x1, y1, x2, y2, t["red"], 2.2, ";stroke-dasharray:6 4"))
        for k, (x, y) in P.items():
            unp = all(k not in p for p in fl["pairs"])
            o.append(C.circle(x, y, 16, t["wash"] if unp else t["surface"], t["red"] if unp else t["ink2"], 1.8))
            o.append(C.text(x, y + 5, k, t["ink"], 14, "middle", 700))
        o.append(C.text(530, 60, "thick blue: the pairs to start with", t["muted"], 12))
        o.append(C.text(530, 80, "red rings: unpaired vertices", t["muted"], 12))
        o.append(C.text(530, 100, "dashed red: the augmenting path", t["muted"], 12))
        o.append(C.text(530, 120, " ".join(map(str, path)), t["red"], 13, "start", 700))
        o.append(C.text(530, 150, f"Without blossoms: {fl['naive']} pairs.", t["muted"], 12))
        o.append(C.text(530, 170, f"With Edmonds's shrinking: {fl['ed']} pairs.", t["muted"], 12))
        o.append(C.text(20, 268, "2 3 4 5 6 is an odd cycle, a blossom. A search that reaches 3 the short way, from 2, calls it inner and never looks past it.", t["muted"], 12))
        return C.svg_doc(780, 282, "".join(o), "The flower: an augmenting path that only Edmonds's shrinking finds", t, standalone, 0.55, 780)
    return draw


MT_HTML = """
<div class="board mt-board">
  <div style="min-width:0">
    <div class="mt-g" id="mt-g"></div>
  </div>
  <div style="min-width:0">
    <div class="mt-btns">
      <button type="button" id="mt-flower">The flower</button><button type="button" id="mt-naive">Search without blossoms</button><button type="button" id="mt-ed">Search with Edmonds's shrinking</button>
      <button type="button" id="mt-rand">Random graph, maximum matching</button>
    </div>
    <p class="say" id="mt-say" aria-live="polite"></p>
  </div>
</div>
"""

MT_CSS = """
.mt-g svg{display:block;width:100%;max-width:480px;height:auto}
.mt-btns{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}
"""

MT_JS = r"""
(() => {
  const box = document.getElementById("mt-g");
  if (!box) return;
  const NS = "http://www.w3.org/2000/svg";
  const FP = [[40, 160], [140, 160], [250, 160], [340, 90], [450, 110], [450, 210], [340, 230], [420, 40]];
  const FE = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 2], [3, 7]], FM = [[1, 2], [3, 4], [5, 6]];
  let P, E, match, adj, pathEdges = [], seed = 1965;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  function setGraph(pos, edges, pairs) {
    P = pos; E = edges; adj = P.map(() => []); edges.forEach(([a, b]) => { adj[a].push(b); adj[b].push(a); });
    match = P.map(() => -1); pairs.forEach(([a, b]) => { match[a] = b; match[b] = a; }); pathEdges = [];
  }
  // Edmonds's search, as in the program (the shrinking can be switched off)
  function findPath(root, shrink) {
    const n = P.length, p = Array(n).fill(-1), base = [...Array(n).keys()], used = Array(n).fill(false), q = [root]; used[root] = true;
    const lca = (a, b) => { const seen = Array(n).fill(false); for (;;) { a = base[a]; seen[a] = true; if (match[a] === -1) break; a = p[match[a]]; } for (;;) { b = base[b]; if (seen[b]) return b; b = p[match[b]]; } };
    let blossom;
    const mark = (v, b, child) => { while (base[v] !== b) { blossom[base[v]] = blossom[base[match[v]]] = true; p[v] = child; child = match[v]; v = p[match[v]]; } };
    for (let h = 0; h < q.length; h++) {
      const v = q[h];
      for (const to of adj[v]) {
        if (base[v] === base[to] || match[v] === to) continue;
        if (to === root || (match[to] !== -1 && p[match[to]] !== -1)) {
          if (!shrink) continue;
          const cur = lca(v, to); blossom = Array(n).fill(false); mark(v, cur, to); mark(to, cur, v);
          for (let i = 0; i < n; i++) if (blossom[base[i]]) { base[i] = cur; if (!used[i]) { used[i] = true; q.push(i); } }
        } else if (p[to] === -1) { p[to] = v; if (match[to] === -1) return [to, p]; used[match[to]] = true; q.push(match[to]); }
      }
    }
    return [-1, p];
  }
  function augment(root, shrink) {
    const [u, p] = findPath(root, shrink);
    if (u === -1) return null;
    const path = []; let x = u;
    while (x !== -1) { const pv = p[x], ppv = match[pv]; path.push([x, pv]); match[x] = pv; match[pv] = x; x = ppv; }
    return path;
  }
  function draw() {
    box.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", "0 0 500 270"); box.appendChild(svg);
    const onPath = (a, b) => pathEdges.some(([x, y]) => (x === a && y === b) || (x === b && y === a));
    E.forEach(([a, b]) => {
      const m = match[a] === b;
      sv("line", {x1: P[a][0], y1: P[a][1], x2: P[b][0], y2: P[b][1], stroke: m ? "var(--blue)" : "var(--axis)", "stroke-width": m ? 6 : 1.6}, svg);
      if (onPath(a, b)) sv("line", {x1: P[a][0], y1: P[a][1], x2: P[b][0], y2: P[b][1], stroke: "var(--red)", "stroke-width": 2.2, "stroke-dasharray": "6 4"}, svg);
    });
    P.forEach(([x, y], i) => {
      const un = match[i] === -1;
      sv("circle", {cx: x, cy: y, r: 14, fill: un ? "var(--wash)" : "var(--surface)", stroke: un ? "var(--red)" : "var(--ink2)", "stroke-width": 1.8}, svg);
      const t = sv("text", {x, y: y + 4, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg); t.textContent = i;
    });
  }
  const pairsNow = () => match.filter((m, i) => m > i).length;
  function say(m) { draw(); document.getElementById("mt-say").textContent = m; }
  const flower = () => { setGraph(FP, FE, FM); say("The flower: pairs 1-2, 3-4, 5-6 (thick blue); 0 and 7 are unpaired (red rings). 2 3 4 5 6 is an odd cycle. Is there an augmenting path from 0 to 7?"); };
  document.getElementById("mt-flower").addEventListener("click", flower);
  document.getElementById("mt-naive").addEventListener("click", () => { setGraph(FP, FE, FM); const path = augment(0, false); pathEdges = path || []; say(path ? "Found a path." : `Searching from 0 without shrinking blossoms: 1 is inner, 2 outer, 3 inner (reached from 2), so 3's neighbour 7 is never examined. No path found: still ${pairsNow()} pairs.`); });
  document.getElementById("mt-ed").addEventListener("click", () => { setGraph(FP, FE, FM); const path = augment(0, true); pathEdges = path || []; say(path ? `When 4 and 5 (both outer) are found to be joined, the odd cycle 2 3 4 5 6 is shrunk to one outer vertex, so 3 counts as outer and 7 is reached. Swapping along the dashed path gives ${pairsNow()} pairs.` : "No path."); });
  document.getElementById("mt-rand").addEventListener("click", () => {
    const n = 14, pos = [], edges = [];
    for (let i = 0; i < n; i++) { const a = 2 * Math.PI * i / n; pos.push([250 + 180 * Math.cos(a), 135 + 115 * Math.sin(a)]); }
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) if (rnd() < 0.18) edges.push([i, j]);
    setGraph(pos, edges, []);
    for (let v = 0; v < n; v++) if (match[v] === -1) augment(v, true);
    const un = match.filter(m => m === -1).length;
    say(`A random graph of ${n} vertices and ${edges.length} edges: Edmonds's algorithm found ${pairsNow()} pairs, leaving ${un} ${un === 1 ? "vertex" : "vertices"} unpaired; no larger matching exists, because no augmenting path remains.`);
  });
  flower();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Edmonds's matching combined older ideas, and where it led")
    W = 210
    nodes = {
        "berge": (20, 20, "Berge's theorem", "maximum exactly when no augmenting path", "1957", "ink"),
        "srch": (395, 20, "Searching a graph", "grow a tree from a root, level by level", "topic 7", "ink"),
        "brute": (770, 20, "Trying everything", "finite, but grows faster than any power", "", "ink"),
        "ed": (395, 170, "Edmonds's blossoms", "⊕ shrink each odd cycle to one vertex", "1961; published 1965", "red"),
        "good": (20, 330, "\"Good\" algorithms", "work bounded by a power of the size", "Edmonds 1965; Cobham 1965", "red"),
        "poly": (395, 330, "The matching polytope", "a linear-programming description", "Edmonds", "ink"),
        "pnp": (770, 330, "P and NP", "which problems have good algorithms?", "Edmonds's conjectures, 1966", "ink"),
        "today": (395, 480, "Complexity theory", "the dividing line of the next era", "Era 6", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("berge", "ed", ports=("bottom", "top:0.15"))
    D.edge("srch", "ed", ports=("bottom", "top"))
    D.edge("brute", "good", ports=("left:0.5", "top:0.8"), dashed=True)
    D.edge("ed", "good", ports=("bottom:0.1", "top:0.7"))
    D.edge("ed", "poly", ports=("bottom", "top"))
    D.edge("ed", "pnp", ports=("bottom:0.9", "top:0.3"))
    D.edge("good", "today", ports=("bottom:0.6", "left:0.5"))
    D.edge("pnp", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: the contrast that gave \"good\" its meaning. Both nodes in red are Edmonds's: an algorithm, and a way of judging algorithms.", "caption")
    return D


def chain(d):
    fl, g, r = d["fl"], d["growth"], d["rand"]
    steps = [
        (f"Trying every matching: {g[1][1]} of them for a complete graph of {g[1][0]} vertices",
         "Berge: grow the matching one augmenting path at a time", "1957"),
        ("Odd cycles hide augmenting paths from the search",
         f"Shrink each odd cycle (a blossom) to one vertex: the flower's path is found, {fl['naive']} pairs become {fl['ed']}", "Edmonds, 1961–1965"),
        ("No agreed meaning of \"efficient\": every finite method was, in principle, an algorithm",
         "A \"good\" algorithm is one whose work grows like a power of the input's size", "Edmonds; Cobham, 1965"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from trying everything to good algorithms")
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


def sup(s):
    m = re.match(r"about ([\d.]+) x 10\^(\d+)", s)
    return f"about {m.group(1)} × 10{m.group(2).translate(C._SUP)}" if m else s


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    fl, r, g = d["fl"], d["rand"], d["growth"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Berge had shown in 1957 that a matching is as large as possible exactly when no augmenting path exists. Searching for such paths works on two-sided graphs, but odd cycles fool it. Edmonds added the blossom: shrink the odd cycle and search on. His paper then asked what makes any algorithm good. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Edmonds's algorithm, and his test for a good one. Blue: the question that took over the next era."),
        ]),
        dict(id="flower", eyebrow="Try it", title="Find the path that the simple search misses", toc="Try it", blocks=[
            dict(type="p", text="The graph from the program: pairs 1-2, 3-4 and 5-6 to start (thick blue), vertices 0 and 7 unpaired. An augmenting path from 0 to 7 would add a pair. Search without blossoms, then with Edmonds's shrinking; then try a random graph."),
            dict(type="widget", html=MT_HTML, js=MT_JS, css=MT_CSS,
                 fallback=dict(type="svg", name="flower", draw=flower_svg(d), alt="The flower: an augmenting path that only Edmonds's shrinking finds", width=780),
                 note="In the interactive edition you can run both searches on the flower, and Edmonds's algorithm on random graphs."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Paths, trees, and flowers", toc="How it works", blocks=[
            dict(type="p", text="**Augmenting paths.** A matching pairs vertices along edges, each vertex in at most one pair. An augmenting path starts and ends at unpaired vertices and alternates between edges outside and inside the matching; swapping the edges along it adds one pair. Berge: no augmenting path, no larger matching."),
            dict(type="p", text="**The search.** Grow a tree from an unpaired vertex: its neighbours are \"inner\", their partners \"outer\", and the search continues only from outer vertices. In a two-sided graph each vertex can only ever be one or the other. In a graph with an odd cycle, the search may reach a vertex the short way round as inner when the long way round would have made it outer, and the path beyond it is never seen."),
            dict(type="p", text=f"**The flower.** In the program's graph, 2 3 4 5 6 is a 5-cycle. Searching from 0 without blossoms reaches 3 from 2 as inner, never looks at its neighbour 7, and the matching stays at {fl['naive']} pairs. Edmonds's search notices that two outer vertices are joined, closing an odd cycle, shrinks the whole cycle to a single outer vertex and carries on; it finds {' '.join(map(str, fl['path']))}, and the matching grows to {fl['ed']} pairs."),
            dict(type="callout", kind="key", label="Key idea",
                 text="When an odd cycle confuses the search, shrink it to a point, find the path in the smaller graph, and expand the cycle again afterwards: inside a blossom every vertex can be reached either way round."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Polynomial against everything", toc="Measured", blocks=[
            dict(type="p", text=f"On {r['n']} random graphs of 2 to {r['maxv']} vertices, Edmonds's algorithm found a matching as large as the best of all matchings every time, shrinking {r['bl']} blossoms along the way. Trying every matching looked at {r['brute']} matchings in all; Edmonds's searches took {r['steps']} edge-steps."),
            dict(type="table", head=["Vertices", "Matchings of the complete graph", "Edmonds on a random graph (steps)", "Pairs found"], num=[0, 2, 3],
                 rows=[[n, sup(c), s, p] for n, c, s, p in g], hl=len(g) - 1),
            dict(type="p", text="The number of matchings of a complete graph (the telephone numbers, checked against brute force up to 10 vertices) grows faster than any power of n; the steps of Edmonds's search grow like a small power. That is the difference Edmonds named."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A paper about flowers, and about efficiency", toc="The evidence", blocks=[
            dict(type="p", text="Edmonds (born 5 April 1934) worked at the National Bureau of Standards from 1959 to 1969 (Wikipedia); \"In 1959 he joined NBS, became a founding member of Alan Goldman's newly created Operations Research Section in 1961\" (NIST). \"Paths, trees, and flowers\", *Canadian Journal of Mathematics* 17: 449–467 (1965), introduced the blossom algorithm: \"This was the first polynomial-time algorithm for maximum matching in graphs\"; he \"characterizes feasible problems as those solvable in polynomial time\" (Wikipedia). The algorithm was developed in 1961 and runs in O(|E||V|²) time; it \"gave the first proof that a maximum-size matching could be found using a polynomial amount of computation time\" (Wikipedia, Blossom algorithm)."),
            dict(type="p", text="NIST's history calls Edmonds's matching algorithm \"the very first instance of a good algorithm for a problem outside that mold\", and recalls his phrase \"the curse of exponentiality\". Cobham's paper of the same year proposed polynomial time as the meaning of \"feasibly computable\"; Edmonds's paper is credited with \"identifying P with tractable problems\" (Wikipedia, Cobham's thesis). In 1966 Edmonds \"originated the conjectures NP ≠ P and NP ∩ coNP = P\"; he received the John von Neumann Theory Prize in 1985."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Hilbert asked whether; Edmonds asked how fast", toc="Full circle", blocks=[
            dict(type="p", text="Era 4 opened with Hilbert asking for a process that decides, and closed with proofs that some questions have none. This era closes with a sharper question: among problems that can be solved, which can be solved in a time that grows only like a power of their size? Edmonds's word for those algorithms was \"good\". Whether every problem whose answers can be checked quickly also has a good algorithm, the question of P and NP, is open still."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"For 400 vertices the complete graph has {sup(g[-1][1])} matchings. Edmonds's algorithm, on a random graph that size, took {g[-1][2]} steps."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A path a–b–c–d with b–c paired. Is there an augmenting path?", "Yes: a, b, c, d (outside, inside, outside). Swapping gives the pairs a–b and c–d: one more."),
            ("Why can't a triangle have more than one pair?", "Three vertices: a second pair would need four."),
            ("In the flower, why is 3 called inner?", "The search reaches it from 2 along an unpaired edge, so it sits an odd number of steps from the root."),
            ("Is an algorithm whose work grows like n³ 'good' in Edmonds's sense? Like 2ⁿ?", "n³: yes, a power of the size. 2ⁿ: no, it grows faster than any power."),
            ("Why is trying every matching hopeless at 50 vertices?", f"The complete graph on 50 vertices has {sup(g[2][1])} matchings."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Paths, Trees, and Flowers", text="NIST's history of Edmonds's work at the National Bureau of Standards.",
                 draw=C.draw_book, link="https://nvlpubs.nist.gov/nistpubs/sp958-lide/html/140-144.html", link_text="NIST SP 958", licence="Drawn placeholder."),
            dict(title="Edmonds's Blossom Algorithm", text="An interactive applet from the Technische Universität München that runs the algorithm step by step.",
                 draw=C.draw_board, link="https://algorithms.discrete.ma.tum.de/graph-algorithms/matchings-blossom-algorithm/index_en.html", link_text="TUM applet", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Matching", d["checks"],
                           f"the flower with and without blossoms, {r['n']} random graphs against trying every matching, the telephone numbers, and the growth of the search up to 400 vertices.",
                           ["static int findPath(int root)"]),
    ]
    return dict(
        title="Edmonds's Matching", date="1965",
        description="Era 5, topic 13 of The Algorithm Evolution Atlas: Edmonds's blossom algorithm for maximum matching, and his proposal that a good algorithm is one that runs in polynomial time.",
        lede="Pairing up as many vertices of a network as possible looks easy until odd cycles appear. Edmonds shrank each odd cycle to a point and searched on; and he proposed that an algorithm is good when its work grows only like a power of the input's size.",
        fieldnote=f"On a graph of 8 vertices the obvious search missed an improvement, and shrinking one pentagon found it. For 400 vertices there are {sup(g[-1][1])} matchings to try; Edmonds's search took {g[-1][2]} steps. The species ends this era able to say not only that a problem can be solved, but whether it can be solved well.",
        card=[("When", "Developed 1961; published 1965"),
              ("Where", "National Bureau of Standards"),
              ("What hurt", "Odd cycles; no agreed meaning of \"efficient\""),
              ("The fix", "Shrink blossoms; call polynomial-time algorithms good"),
              ("Cost", "O(|E||V|²) for the original algorithm")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Matching.java`.",
    )
