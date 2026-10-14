"""Era 5, topic 7: Dijkstra's shortest paths. Every number is parsed from ShortestPaths.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"map: (\d+) invented towns .*? its (\d+) nearest neighbours: (\d+) roads ; from town (\d+) \(bottom left\) to town (\d+) \(top right\) the shortest route is ([\d ]+), length (\d+), through (\d+) towns ; Dijkstra's method moved (\d+) towns into A and looked along (\d+) road ends$", ln):
            g = m.groups()
            d["map"] = dict(n=g[0], k=g[1], roads=g[2], p=g[3], q=g[4], route=g[5].split(), len=g[6], through=g[7], moved=g[8], looks=g[9])
        elif ln.startswith("sets: "):
            d["sets"] = re.findall(r"after step (\d+): A \{([^}]*)\} B \{([^}]*)\}", ln)
        elif m := re.match(r"random: ([\d,]+) random maps of (\d+) to (\d+) towns, road lengths 1 to (\d+) ; .*? Dijkstra ([\d,]+), Ford ([\d,]+) \(([\d.]+) times as many\)", ln):
            d["rand"] = dict(maps=m.group(1), lo=m.group(2), hi=m.group(3), maxlen=m.group(4), dij=m.group(5), ford=m.group(6), ratio=m.group(7))
        elif ln.startswith("storage: "):
            d["store"] = re.findall(r"(\d+) towns, (\d+) roads: set B at most (\d+) towns", ln)
        elif m := re.match(r"negative: .*? gives town 3 the distance (\d+) ; Ford's method finds (\d+) \(([\d, ]+)\)", ln):
            d["neg"] = dict(dij=m.group(1), ford=m.group(2), path=m.group(3))
        elif m := re.match(r"tree: .*? growing one tree from town 0: length (\d+) ; Kruskal's method, .*?: length (\d+), (\d+) roads, the same$", ln):
            d["tree"] = dict(dij=m.group(1), kr=m.group(2), roads=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def neg_svg(d):
    ng = d["neg"]

    def draw(t, standalone):
        import math
        P = {0: (60, 110), 1: (260, 50), 2: (260, 170), 3: (460, 50)}
        o = []

        def arrow(a, b, lab, col):
            (x1, y1), (x2, y2) = P[a], P[b]
            ang = math.atan2(y2 - y1, x2 - x1)
            sx, sy = x1 + 20 * math.cos(ang), y1 + 20 * math.sin(ang)
            ex, ey = x2 - 20 * math.cos(ang), y2 - 20 * math.sin(ang)
            bx, by = ex - 9 * math.cos(ang), ey - 9 * math.sin(ang)
            s = C.line(sx, sy, bx, by, col, 1.8)
            s += C.path(f"M{ex:.1f},{ey:.1f} L{bx - 5 * math.sin(ang):.1f},{by + 5 * math.cos(ang):.1f} L{bx + 5 * math.sin(ang):.1f},{by - 5 * math.cos(ang):.1f} Z", None, col)
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            s += C.text(mx + (14 if a == 2 else 0), my - 8, lab, col, 14, "middle", 700)
            return s
        o.append(arrow(0, 1, "2", t["ink2"]))
        o.append(arrow(0, 2, "5", t["ink2"]))
        o.append(arrow(2, 1, "-4", t["red"]))
        o.append(arrow(1, 3, "2", t["ink2"]))
        for k, (x, y) in P.items():
            o.append(C.circle(x, y, 18, t["surface"], t["ink2"], 1.6))
            o.append(C.text(x, y + 5, str(k), t["ink"], 15, "middle", 700))
        o.append(C.text(520, 40, f"Dijkstra: town 1 settled at 2,", t["muted"], 12))
        o.append(C.text(520, 58, f"so town 3 gets {ng['dij']}.", t["muted"], 12))
        o.append(C.text(520, 90, f"True shortest: {ng['ford']},", t["muted"], 12))
        o.append(C.text(520, 108, f"by {ng['path'].replace(', ', ' → ')}.", t["muted"], 12))
        return C.svg_doc(720, 200, "".join(o), "A road of negative length breaks Dijkstra's argument", t, standalone, 0.55, 720)
    return draw


DJ_HTML = """
<div class="board dj-board">
  <div style="min-width:0">
    <div class="eyebrow">Click a town to start from it</div>
    <div class="dj-map" id="dj-map"></div>
  </div>
  <div style="min-width:0">
    <div class="dj-sets" id="dj-sets"></div>
    <div class="dj-btns"><button type="button" id="dj-step">Next step</button><button type="button" id="dj-all">Finish</button><button type="button" id="dj-reset">Start again</button></div>
    <p class="say" id="dj-say" aria-live="polite"></p>
  </div>
</div>
"""

DJ_CSS = """
.dj-map svg{display:block;width:100%;max-width:460px;height:auto;cursor:pointer}
.dj-sets{font:13px var(--mono);display:grid;gap:6px;margin:6px 0}
.dj-sets div{border-left:4px solid var(--rule);padding:3px 8px;min-width:0;overflow-wrap:anywhere}
.dj-sets .a{border-color:var(--red)} .dj-sets .b{border-color:var(--blue)}
.dj-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
"""

DJ_JS = r"""
(() => {
  const box = document.getElementById("dj-map");
  if (!box) return;
  // an invented map of 12 towns; road lengths are the straight-line distances, rounded
  const T = [[40, 60], [150, 30], [270, 70], [380, 40], [80, 170], [200, 140], [320, 180], [420, 150], [50, 280], [170, 260], [300, 290], [410, 270]];
  const R = [[0, 1], [0, 4], [1, 2], [1, 5], [2, 3], [2, 5], [2, 6], [3, 7], [4, 5], [4, 8], [5, 6], [5, 9], [6, 7], [6, 10], [7, 11], [8, 9], [9, 10], [10, 11], [6, 11]];
  const len = (a, b) => Math.round(Math.hypot(T[a][0] - T[b][0], T[a][1] - T[b][1]) / 10);
  const NS = "http://www.w3.org/2000/svg";
  let src = 0, dist, prev, set, done, last;
  function reset(s) {
    src = s; dist = T.map(() => Infinity); prev = T.map(() => -1); set = T.map(() => "C");
    dist[s] = 0; set[s] = "B"; done = false; last = -1;
  }
  function step() {
    let u = -1;
    T.forEach((_, i) => { if (set[i] === "B" && (u < 0 || dist[i] < dist[u])) u = i; });
    if (u < 0) { done = true; return "Set B is empty: every town has its shortest distance."; }
    set[u] = "A"; last = u;
    const changed = [];
    for (const [a, b] of R) for (const [x, y] of [[a, b], [b, a]]) if (x === u && set[y] !== "A" && dist[u] + len(u, y) < dist[y]) { dist[y] = dist[u] + len(u, y); prev[y] = u; set[y] = "B"; changed.push(`${y} → ${dist[y]}`); }
    return `Town ${u} is the nearest in set B (distance ${dist[u]}): no other route can beat it, so it moves into A.` + (changed.length ? ` Its roads improve ${changed.join(", ")}.` : " Its roads improve nothing.");
  }
  function draw() {
    box.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", "0 0 460 320"); box.appendChild(svg);
    for (const [a, b] of R) {
      const tree = prev[a] === b || prev[b] === a;
      sv("line", {x1: T[a][0], y1: T[a][1], x2: T[b][0], y2: T[b][1], stroke: tree ? "var(--red)" : "var(--rule)", "stroke-width": tree ? 3 : 1.5}, svg);
      const t = sv("text", {x: (T[a][0] + T[b][0]) / 2 + 4, y: (T[a][1] + T[b][1]) / 2 - 4, "font-size": 11, fill: "var(--muted)"}, svg); t.textContent = len(a, b);
    }
    T.forEach(([x, y], i) => {
      const fill = set[i] === "A" ? "var(--red)" : set[i] === "B" ? "var(--blue)" : "var(--surface)";
      const c = sv("circle", {cx: x, cy: y, r: i === last ? 16 : 13, fill, stroke: "var(--ink2)", "stroke-width": 1.5}, svg);
      const t = sv("text", {x, y: y + 4, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: set[i] === "C" ? "var(--ink)" : "var(--paper)"}, svg); t.textContent = i;
      if (dist[i] < Infinity) { const d = sv("text", {x, y: y - 20, "text-anchor": "middle", "font-size": 11, fill: "var(--ink)"}, svg); d.textContent = dist[i]; }
      [c, t].forEach(n => n.addEventListener("click", () => { reset(i); show(`Starting from town ${i}. It goes into set B with distance 0.`); }));
    });
  }
  function show(msg) {
    draw();
    const s = document.getElementById("dj-sets"); s.innerHTML = "";
    const fmt = k => T.map((_, i) => i).filter(i => set[i] === k).map(i => `${i}=${dist[i] === Infinity ? "?" : dist[i]}`).join(" ");
    el("div", {class: "a"}, s).textContent = "A (settled): " + (fmt("A") || "none");
    el("div", {class: "b"}, s).textContent = "B (frontier): " + (fmt("B") || "none");
    el("div", {}, s).textContent = "C (not yet reached): " + T.map((_, i) => i).filter(i => set[i] === "C").join(" ");
    document.getElementById("dj-say").textContent = msg;
  }
  document.getElementById("dj-step").addEventListener("click", () => { if (!done) show(step()); });
  document.getElementById("dj-all").addEventListener("click", () => { let m = ""; while (!done) m = step(); show(m + " The red roads are the shortest routes from the start."); });
  document.getElementById("dj-reset").addEventListener("click", () => { reset(src); show(`Starting from town ${src}.`); });
  reset(0); show("Starting from town 0. Press Next step: each step moves the nearest town of the frontier B into the settled set A.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Dijkstra's shortest paths combined older ideas, and where they led")
    W = 210
    nodes = {
        "jar": (20, 20, "Jarník's tree", "grow one tree, shortest edge first", "Era 4 topic 4", "ink"),
        "dp": (395, 20, "Bellman's principle", "parts of a best route are best", "topic 5", "ink"),
        "ford": (770, 20, "Ford's method", "improve every road until nothing changes", "1950s", "ink"),
        "dij": (395, 170, "Dijkstra's method", "⊕ settle the nearest frontier town, one at a time", "1956; published 1959", "red"),
        "mst": (20, 330, "Shortest wiring", "the same paper: least wire for the X1", "1959", "ink"),
        "heap": (395, 330, "With a heap", "find the nearest of set B quickly", "topic 12", "ink"),
        "neg": (770, 330, "Negative roads", "need Ford's method instead", "", "ink"),
        "today": (395, 480, "Route finding today", "maps, networks, games", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("jar", "dij", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("dp", "dij", ports=("bottom", "top"))
    D.edge("ford", "dij", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("dij", "mst", ports=("bottom:0.1", "top:0.7"))
    D.edge("dij", "heap", ports=("bottom", "top"))
    D.edge("dij", "neg", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("heap", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: a likeness, or a contrast; Dijkstra's paper compares his method with Ford's as Berge described it. Whether he knew Jarník's 1930 paper is not recorded in the sources opened.", "caption")
    return D


def chain(d):
    r, st, ng = d["rand"], d["store"], d["neg"]
    steps = [
        ("A network of roads: the routes between two towns are far too many to list",
         "Settle towns one at a time, always the nearest of the frontier", "Dijkstra, 1956"),
        ("Ford's method goes over every road again and again, keeping data for all of them",
         f"Each road end looked at once: {r['dij']} looks against Ford's {r['ford']}; only the frontier is stored", "the 1959 paper"),
        ("Finding the nearest frontier town means scanning the whole frontier each step",
         "Keep the frontier in a heap", "topic 12, 1964"),
        ("A road of negative length breaks the argument",
         f"Use Ford's method: it finds {ng['ford']} where Dijkstra's gives {ng['dij']}", "lengths must be ≥ 0"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from listing routes to settling towns")
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
    mp, sets, r, st, ng, tr = d["map"], d["sets"], d["rand"], d["store"], d["neg"], d["tree"]
    set_rows = [[s, a, b] for s, a, b in sets]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The shortest route to a town passes through towns whose shortest routes are its own beginnings (the principle of topic 5). Dijkstra added an order: settle the towns one at a time, nearest first, so that each is settled once and for all. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Dijkstra's method. Blue: route finding today."),
        ]),
        dict(id="map", eyebrow="Try it", title="Grow the settled set, one town at a time", toc="Try it", blocks=[
            dict(type="p", text="An invented map of 12 towns (road lengths beside the roads). Red towns are in set A, settled; blue towns are in set B, reached by some road with the best distance so far; white towns are in C. Each step moves the nearest town of B into A and looks along its roads. Click any town to start from it."),
            dict(type="widget", html=DJ_HTML, js=DJ_JS, css=DJ_CSS,
                 fallback=dict(type="table", head=["After step", "Set A (town = distance)", "Set B (town = distance so far)"], num=[0], rows=set_rows),
                 note=f"In the interactive edition you can step through the method on a small map. Here, the first four steps on the program's 64-town map, from town {mp['p']}."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Three sets of towns", toc="How it works", blocks=[
            dict(type="p", text="**The paper's words.** Dijkstra divides the nodes into set A, \"the nodes for which the path of minimum length from P is known\"; set B, \"the nodes from which the next node to be added to set A will be selected\"; and set C, \"the remaining nodes\". At each step \"the node with minimum distance from P is transferred from set B to set A\", and the roads out of it update its neighbours."),
            dict(type="p", text="**Why the nearest is safe.** Any other route to that town must leave set A somewhere, through a town of B that is already at least as far, and roads cannot have negative length; so nothing found later can be shorter."),
            dict(type="p", text=f"**On the program's map.** {mp['n']} invented towns, each joined to its {mp['k']} nearest neighbours ({mp['roads']} roads; the ARMAC demonstration used 64 Dutch cities). From town {mp['p']} to town {mp['q']} the shortest route is {' → '.join(mp['route'])}, length {mp['len']}, through {mp['through']} towns. The method moved all {mp['moved']} towns into A and looked along {mp['looks']} road ends, each road from both of its ends once."),
            dict(type="svg", name="negative", draw=neg_svg(d), alt="A road of negative length breaks Dijkstra's argument",
                 caption="With one-way roads 0→1 (2), 0→2 (5), 2→1 (−4), 1→3 (2), town 1 is settled at 2 before the road from town 2 is seen."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Settle the nearest unsettled place: its distance can never improve. Each place is settled once, and each road is looked at once from each end."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Against Ford's method, and what must be stored", toc="Measured", blocks=[
            dict(type="p", text=f"On {r['maps']} random maps of {r['lo']} to {r['hi']} towns (road lengths 1 to {r['maxlen']}), Dijkstra's method and Ford's method (improve every road, pass after pass, until nothing changes) gave the same distance to every town. Dijkstra's looked at {r['dij']} road ends; Ford's at {r['ford']}, {r['ratio']} times as many. Dijkstra's method also scanned set B once per town to find its nearest member, as the 1959 version did; a heap (topic 12) makes that fast."),
            dict(type="table", head=["Towns", "Roads", "Largest size of set B"], num=[0, 1, 2], rows=[list(x) for x in st]),
            dict(type="p", text="The paper's other boast: against Ford's method, \"we need not store the data for all branches simultaneously but only those for the branches in sets I and II, and this number is always less than n\". Set B stays far smaller than the number of roads."),
            dict(type="p", text=f"**The paper's first problem**, the shortest network joining all the towns, by growing one tree from a town: on the 64 towns joined every way, length {tr['dij']}; Kruskal's method, shortest roads first unless they close a loop, gives {tr['kr']} with {tr['roads']} roads, the same."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Twenty minutes on a café terrace", toc="The evidence", blocks=[
            dict(type="p", text="For the official inauguration of the ARMAC in 1956, Dijkstra wanted a problem a nontechnical audience could follow: \"Given a network of roads connecting cities, what is the shortest route between two designated cities?\" (ACM Turing Award page). In a 2001 interview he recalled the question \"What's the shortest way to travel from Rotterdam to Groningen\", worked out on a \"café terrace\" in Amsterdam with \"my young fiancée\" in about twenty minutes, \"without pencil and paper\"; \"it was published in 1959, three years later\". Wikipedia gives the reason for the wait: \"Because of the absence of journals dedicated to automatic computing, he did not publish the result until 1959.\""),
            dict(type="p", text="The paper, \"A note on two problems in connexion with graphs\" (*Numerische Mathematik* 1: 269–271, 1959), poses two problems: \"Construct the tree of minimum total length between the n nodes\", for the wiring of the X1 computer, and \"Find the path of minimum total length between two given nodes P and Q\". The 64-city demonstration map is reported by Vice (2015) and *Chalkdust* (2018), not in Dijkstra's own words."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Two problems, three pages", toc="Full circle", blocks=[
            dict(type="p", text="The method, usually with its frontier kept in a heap (topic 12), is still the first one taught for finding routes. The paper's other problem, the shortest wiring, is Jarník's tree of 1930 (Era 4, topic 4) found again: the program grows it from one town and gets exactly the length Kruskal's method gives."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Designed for an audience of non-mathematicians at a computer's opening, without pencil or paper: from town {mp['p']} to town {mp['q']}, {mp['len']} units, found by settling {mp['moved']} towns in order of distance."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            (f"In the program's first step, set B holds towns 1, 14, 22, 55 at 220, 143, 320, 312. Which moves into A next?", "Town 14, at 143: the nearest in B."),
            ("Why can't a town in A ever get a shorter distance later?", "Every other route to it leaves A through a town of B that is already at least as far, and the remaining roads only add length."),
            ("How many times is each road looked at?", "Once from each end, when that end's town is moved into A."),
            ("Why does a negative road break the method?", "A town settled early could be reached more cheaply later through the negative road, but settled towns are never revisited."),
            ("What does a heap change?", "Finding the nearest town of B takes about log n steps instead of a scan of all of B."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A note on two problems in connexion with graphs (1959)", text="Dijkstra's three-page paper in Numerische Mathematik: the shortest wiring, and the shortest path.",
                 draw=C.draw_manuscript, link="https://ir.cwi.nl/pub/9256", link_text="CWI repository", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ShortestPaths", d["checks"],
                           f"the 64-town map against Ford's method, {r['maps']} random maps, the size of set B, a negative road, and the shortest network by two methods.",
                           ["static int[] dijkstra(List<List<Road>> g, int p, int[] prev)"]),
    ]
    return dict(
        title="Dijkstra's Shortest Paths", date="1956–1959",
        description="Era 5, topic 7 of The Algorithm Evolution Atlas: Dijkstra's shortest-path method with its three sets of towns, against Ford's method, with the shortest network from the same 1959 paper.",
        lede="A computer was to be shown to the public, and its programmer wanted a problem anyone could follow: the shortest road between two cities. He worked out the method in his head in about twenty minutes: settle the towns one at a time, nearest first.",
        fieldnote=f"From town {mp['p']} to town {mp['q']} of an invented map: {mp['len']} units, through {mp['through']} towns. Each town was settled exactly once, nearest first, and the argument that this is safe fits in one sentence. Its author waited three years to publish it, for want of a journal that cared.",
        card=[("When", "1956; published 1959"),
              ("Where", "Mathematical Centre, Amsterdam"),
              ("What hurt", "Too many routes; methods that stored every road"),
              ("The fix", "Settle the nearest frontier town, one at a time"),
              ("Cost", f"Each road looked at twice; {r['ratio']} times fewer looks than Ford's here")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ShortestPaths.java`.",
    )
