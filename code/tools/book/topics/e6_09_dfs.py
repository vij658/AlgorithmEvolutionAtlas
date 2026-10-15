"""Era 6, topic 9: depth-first search and linear-time graph algorithms. Every number is parsed from DepthFirst.java's output."""
import math
import re

import common as C
from diagrams import Diagram

UPOS = {"A": (40, 120), "B": (120, 60), "C": (120, 180), "J": (210, 40), "D": (220, 200), "E": (305, 150),
        "F": (310, 260), "G": (210, 300), "H": (140, 370), "I": (280, 380)}
DPOS = {"A": (40, 60), "B": (130, 40), "C": (90, 140), "D": (230, 60), "E": (320, 40), "F": (290, 150),
        "G": (290, 260), "H": (180, 260), "I": (160, 370), "J": (290, 370)}


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"small: edges ([A-Z ]+) ; search from A, vertices in the order reached: ([A-Z ]+) ; tree edges ([A-Z ]+) ; fronds ([A-Z ]+) ; number/lowpoint: (.*?) ; cut vertices .*?: ([A-Z ]+) ; biconnected components: (.*)$", ln):
            d["small"] = dict(edges=m.group(1).split(), order=m.group(2).split(), tree=m.group(3).split(), fronds=m.group(4).split(),
                              nl={k: (a, b) for k, a, b in re.findall(r"([A-Z])=(\d+)/(\d+)", m.group(5))}, cuts=m.group(6).split(),
                              comps=[c.strip() for c in m.group(7).split(";")])
        elif m := re.match(r"directed: edges ([A-Z ]+) ; strong components, in the order Tarjan's method completes them: (.*?) ;", ln):
            d["dir"] = dict(edges=m.group(1).split(), comps=re.findall(r"\{([A-Z]+)\}", m.group(2)))
        elif m := re.match(r"check: ([\d,]+) random undirected graphs and ([\d,]+) random directed graphs of (\d+) to (\d+) vertices ; .*?\(([\d,]+) cut vertices in all\) ; .*?\(([\d,]+) components in all\)", ln):
            d["check"] = dict(u=m.group(1), dgr=m.group(2), lo=m.group(3), hi=m.group(4), cuts=m.group(5), comps=m.group(6))
        elif ln.startswith("linear: "):
            d["linear"] = re.findall(r"V=([\d,]+), E=([\d,]+): ([\d,]+) steps", ln)
            m = re.search(r"on the graph of ([\d,]+) vertices, finding everything each vertex can reach takes ([\d,]+) steps against ([\d,]+) \(([\d,]+) times more\)", ln)
            d["slow"] = dict(n=m.group(1), slow=m.group(2), fast=m.group(3), times=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def graphs_svg(d):
    sm, dr = d["small"], d["dir"]

    def draw(t, standalone):
        o = []
        W, H = 800, 500
        o.append(C.text(20, 22, "Undirected: tree edges solid, fronds dashed, cut vertices red", t["ink"], 12, "start", 700))
        o.append(C.text(440, 22, "Directed: the four strong components", t["ink"], 12, "start", 700))
        ox, oy = 20, 30
        tree = set(sm["tree"])
        for e in sm["edges"]:
            (x1, y1), (x2, y2) = UPOS[e[0]], UPOS[e[1]]
            is_tree = e in tree or e[::-1] in tree
            o.append(C.line(ox + x1, oy + y1, ox + x2, oy + y2, t["ink2"] if is_tree else t["axis"], 2 if is_tree else 1.5,
                            "" if is_tree else ";stroke-dasharray:5 4"))
        for v, (x, y) in UPOS.items():
            cut = v in sm["cuts"]
            o.append(C.circle(ox + x, oy + y, 17, t["red"] if cut else t["surface"], t["red"] if cut else t["ink2"], 1.6))
            o.append(C.text(ox + x, oy + y + 5, v, t["on_red"] if cut else t["ink"], 13, "middle", 700))
            num, low = sm["nl"][v]
            o.append(C.text(ox + x + 21, oy + y - 12, f"{num}/{low}", t["blue"], 11, "start", 700))
        o.append(C.text(20, H - 30, "Blue: number / lowpoint.", t["muted"], 11))
        # directed
        ox2 = 430
        groups = dr["comps"]
        for gi, g in enumerate(groups):
            xs = [DPOS[v][0] for v in g]
            ys = [DPOS[v][1] for v in g]
            o.append(C.rect(ox2 + min(xs) - 28, oy + min(ys) - 28, max(xs) - min(xs) + 56, max(ys) - min(ys) + 56, t["wash"], t["blue"], 1.4, 14))
        for e in dr["edges"]:
            (x1, y1), (x2, y2) = DPOS[e[0]], DPOS[e[1]]
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy)
            ux, uy = dx / L, dy / L
            # two edges in opposite directions are drawn side by side
            twin = e[::-1] in dr["edges"]
            px, py = (-uy * 5, ux * 5) if twin else (0, 0)
            sx, sy = ox2 + x1 + ux * 18 + px, oy + y1 + uy * 18 + py
            ex, ey = ox2 + x2 - ux * 20 + px, oy + y2 - uy * 20 + py
            o.append(C.line(sx, sy, ex, ey, t["ink2"], 1.5))
            o.append(C.path(f"M{ex:.1f},{ey:.1f} L{ex - ux * 9 - uy * 4.5:.1f},{ey - uy * 9 + ux * 4.5:.1f} L{ex - ux * 9 + uy * 4.5:.1f},{ey - uy * 9 - ux * 4.5:.1f} Z", None, t["ink2"]))
        for v, (x, y) in DPOS.items():
            o.append(C.circle(ox2 + x, oy + y, 16, t["surface"], t["ink2"], 1.6))
            o.append(C.text(ox2 + x, oy + y + 5, v, t["ink"], 13, "middle", 700))
        o.append(C.text(430, H - 30, "Inside a box every vertex can reach every other.", t["muted"], 11))
        o.append(C.text(20, H - 10, f"Cut vertices {', '.join(sm['cuts'])}; strong components completed in the order {' '.join('{' + g + '}' for g in groups)}.", t["muted"], 11))
        return C.svg_doc(W, H, "".join(o), "Depth-first search on the program's two small graphs", t, standalone, 0.55, 800)
    return draw


DF_HTML = """
<div class="board df-board">
  <div style="min-width:0">
    <div class="df-graph" id="df-graph"></div>
  </div>
  <div style="min-width:0">
    <div class="df-btns"><button type="button" id="df-step">Step</button><button type="button" id="df-run">Run to the end</button><button type="button" id="df-reset">Start again</button></div>
    <div class="df-stats" id="df-stats"></div>
    <p class="say" id="df-say" aria-live="polite"></p>
  </div>
</div>
"""

DF_CSS = """
.df-graph svg{display:block;width:100%;max-width:420px;height:auto;margin:0 auto}
.df-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.df-stats{font:13px var(--mono);display:grid;gap:3px}
"""

DF_JS = r"""
(() => {
  const box = document.getElementById("df-graph");
  if (!box) return;
  const EDGES = __EDGES__, POS = __POS__;
  const V = Object.keys(POS).sort(), idx = Object.fromEntries(V.map((v, i) => [v, i]));
  const adj = V.map(() => []);
  EDGES.forEach(e => { adj[idx[e[0]]].push(idx[e[1]]); adj[idx[e[1]]].push(idx[e[0]]); });
  let num, low, par, ei, stack, counter, kind, cut, comps, estack, done, msg;
  function reset() {
    num = V.map(() => -1); low = V.map(() => -1); par = V.map(() => -1); ei = V.map(() => 0);
    stack = [0]; counter = 1; num[0] = low[0] = 0; kind = {}; cut = new Set(); comps = []; estack = []; done = false;
    msg = "Start at A: it gets number 0.";
    show();
  }
  const key = (a, b) => a < b ? `${a}-${b}` : `${b}-${a}`;
  function step() {
    if (done) return;
    const u = stack[stack.length - 1];
    if (ei[u] < adj[u].length) {
      const v = adj[u][ei[u]++];
      if (num[v] < 0) {
        par[v] = u; num[v] = low[v] = counter++; stack.push(v); kind[key(u, v)] = "tree"; estack.push([u, v]);
        msg = `${V[u]}–${V[v]}: ${V[v]} is new, so this is a tree edge; ${V[v]} gets number ${num[v]}.`;
      } else if (v !== par[u] && num[v] < num[u]) {
        kind[key(u, v)] = "frond"; estack.push([u, v]);
        low[u] = Math.min(low[u], num[v]);
        msg = `${V[u]}–${V[v]}: ${V[v]} was reached earlier, so this is a frond back up the tree; lowpoint of ${V[u]} is now ${low[u]}.`;
      } else msg = `${V[u]}–${V[v]}: already seen from the other end.`;
      return;
    }
    stack.pop();
    const p = par[u];
    if (p < 0) { done = true; msg = `Back at A with nothing left: done. Cut vertices: ${[...cut].map(i => V[i]).join(", ") || "none"}.`; if ([...adj[0]].filter(v => par[v] === 0).length > 1) cut.add(0); return; }
    low[p] = Math.min(low[p], low[u]);
    msg = `${V[u]} is finished (lowpoint ${low[u]}); back to ${V[p]}.`;
    if (low[u] >= num[p]) {
      const comp = new Set(); let e;
      do { e = estack.pop(); comp.add(e[0]); comp.add(e[1]); } while (!(e[0] === p && e[1] === u));
      comps.push([...comp].map(i => V[i]).sort().join(""));
      if (p !== 0) { cut.add(p); msg += ` Nothing below ${V[u]} reaches above ${V[p]} (lowpoint ${low[u]} ≥ number ${num[p]}): ${V[p]} is a cut vertex.`; }
      msg += ` Biconnected component ${comps[comps.length - 1]}.`;
    }
  }
  function show() {
    box.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", "0 0 380 430"); box.appendChild(svg);
    EDGES.forEach(e => {
      const [x1, y1] = POS[e[0]], [x2, y2] = POS[e[1]], k = kind[key(idx[e[0]], idx[e[1]])];
      sv("line", {x1, y1, x2, y2, stroke: k === "tree" ? "var(--blue)" : k === "frond" ? "var(--ink-2)" : "var(--axis)", "stroke-width": k === "tree" ? 3 : 1.5, "stroke-dasharray": k === "frond" ? "6 4" : null}, svg);
    });
    const top = stack.length ? stack[stack.length - 1] : -1;
    V.forEach((v, i) => {
      const [x, y] = POS[v], c = cut.has(i);
      sv("circle", {cx: x, cy: y, r: 17, fill: c ? "var(--red)" : i === top && !done ? "var(--yellow)" : num[i] >= 0 ? "var(--surface)" : "var(--wash)", stroke: "var(--ink-2)", "stroke-width": 1.5}, svg);
      const t = sv("text", {x, y: y + 5, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: c ? "var(--on-red)" : "var(--ink)"}, svg); t.textContent = v;
      if (num[i] >= 0) { const s = sv("text", {x: x + 20, y: y - 12, "font-size": 11, "font-weight": 700, fill: "var(--blue)"}, svg); s.textContent = `${num[i]}/${low[i]}`; }
    });
    const st = document.getElementById("df-stats"); st.innerHTML = "";
    el("div", {}, st, `path from A: ${stack.map(i => V[i]).join(" → ") || "—"}`);
    el("div", {}, st, `components found: ${comps.join(", ") || "—"}`);
    el("div", {}, st, "blue numbers: number / lowpoint");
    document.getElementById("df-say").textContent = msg;
  }
  document.getElementById("df-step").addEventListener("click", () => { step(); show(); });
  document.getElementById("df-run").addEventListener("click", () => { while (!done) step(); show(); });
  document.getElementById("df-reset").addEventListener("click", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How depth-first search combined older ideas, and where it led")
    W = 210
    nodes = {
        "maze": (20, 20, "Trémaux's mazes", "go deep, back up at dead ends", "19th century", "ink"),
        "graph": (395, 20, "Graph search", "Euler's bridges to Dijkstra's paths", "Eras 3 and 5", "ink"),
        "plan": (770, 20, "Planarity", "can this network be drawn without crossings?", "the problem that started it", "ink"),
        "dfs": (395, 180, "Depth-first search", "⊕ numbers, fronds and lowpoints", "Tarjan, Hopcroft, 1972", "red"),
        "bic": (20, 340, "Cut vertices, components", "in one pass, time V + E", "1972", "ink"),
        "scc": (395, 340, "Strong components", "who can reach whom, one-way", "1972", "ink"),
        "pt": (770, 340, "Linear-time planarity", "the first such test", "Hopcroft and Tarjan, 1974", "ink"),
        "today": (395, 490, "Today", "components, planarity tests, topological sorting", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("maze", "dfs", ports=("bottom", "top:0.15"))
    D.edge("graph", "dfs", ports=("bottom", "top"))
    D.edge("plan", "dfs", ports=("bottom", "top:0.85"), label="the need", at=0.5, dx=8, anchor="start")
    D.edge("dfs", "bic", ports=("bottom:0.15", "top"))
    D.edge("dfs", "scc", ports=("bottom", "top"))
    D.edge("dfs", "pt", ports=("bottom:0.85", "top"))
    D.edge("scc", "today", ports=("bottom", "top"))
    D.text(20, 615, "Uses after Wikipedia (Depth-first search), which lists components, planarity testing and topological sorting among them.", "caption")
    return D


def chain(d):
    sl, ck, ln = d["slow"], d["check"], d["linear"]
    steps = [
        ("Is a network still connected if any one point fails? Remove each point and search again",
         "One depth-first search: a point is a cut vertex if a child's lowpoint does not reach above it", "Hopcroft and Tarjan"),
        (f"Who can reach whom in a one-way network: {sl['slow']} steps by searching from every vertex ({sl['n']} vertices)",
         f"Tarjan's strong components in one search: {sl['fast']} steps", "Tarjan, 1972"),
        ("Can one trust a clever one-pass method?",
         f"Checked on {ck['u']} undirected and {ck['dgr']} directed random graphs against the slow methods: no disagreement", "this program"),
        ("How does the work grow with the graph?",
         f"Exactly V + E steps, from {ln[0][0]} to {ln[-1][0]} vertices", "linear time"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from repeated searches to one")
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
    sm, dr, ck, ln, sl = d["small"], d["dir"], d["check"], d["linear"], d["slow"]
    edges = "[" + ",".join(f'"{e}"' for e in sm["edges"]) + "]"
    pos = "{" + ",".join(f'"{k}":[{x + 20},{y + 20}]' for k, (x, y) in UPOS.items()) + "}"
    nl_rows = [[v, sm["nl"][v][0], sm["nl"][v][1], "cut vertex" if v in sm["cuts"] else ""] for v in sm["order"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Exploring a maze by going as deep as possible and backing up only at dead ends is old. Hopcroft and Tarjan, looking for a fast test of whether a network can be drawn without crossings, studied what such a search leaves behind: the order of arrival, and the few edges that lead back up. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: depth-first search as a tool. Blue: where it is used today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Watch the lowpoints find the weak points", toc="Try it", blocks=[
            dict(type="p", text="The program's small graph. Step through the search from A: each new vertex gets the next number; an edge to a vertex not yet reached is a tree edge (blue), an edge back to an earlier vertex is a frond (dashed). When a vertex is finished, its lowpoint passes to its parent, and if nothing below a vertex reaches above it, that vertex is a cut vertex (red)."),
            dict(type="widget", html=DF_HTML, js=DF_JS.replace("__EDGES__", edges).replace("__POS__", pos), css=DF_CSS,
                 fallback=dict(type="table", head=["Vertex (in the order reached)", "Number", "Lowpoint", ""], num=[1, 2], rows=nl_rows),
                 note="In the interactive edition you can step through the search and watch the lowpoints."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="One pass, and one extra number", toc="How it works", blocks=[
            dict(type="p", text="**The search.** Number the vertices in the order the search reaches them. The edges used to arrive form a tree; in an undirected graph every other edge (a *frond*) leads from a vertex back to one of its ancestors, never sideways. Each edge is examined from each end once, so the search takes time proportional to V + E."),
            dict(type="p", text="**Lowpoints.** The lowpoint of v is the smallest number that can be reached from v by going down the tree and then along at most one frond. It is computed as the search backs up: a vertex's lowpoint is the least of its own number, the numbers its fronds reach, and its children's lowpoints. A vertex u other than the root is a cut vertex exactly when some child v has lowpoint(v) ≥ number(u): nothing below v can get round u."),
            dict(type="p", text="**Strong components.** In a directed graph the same bookkeeping (Tarjan's LOWLINK) finds the strongly connected components: the search completes a component when it backs out of the first vertex it reached in it."),
            dict(type="svg", name="graphs", draw=graphs_svg(d), alt="Depth-first search on the program's two small graphs", width=800),
            dict(type="callout", kind="key", label="Key idea",
                 text="Don't search again for each question. One search, with a number or two recorded at each vertex, already holds the answers to questions that seemed to need many searches."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Exactly V + E", toc="Measured", blocks=[
            dict(type="p", text=f"**The small graph.** Edges {' '.join(sm['edges'])}; the search from A reached {' '.join(sm['order'])}. Tree edges {' '.join(sm['tree'])}; fronds {' '.join(sm['fronds'])}. Cut vertices {', '.join(sm['cuts'])}; biconnected components {', '.join(sm['comps'])}."),
            dict(type="table", head=["Vertex (in the order reached)", "Number", "Lowpoint", ""], num=[1, 2], rows=nl_rows),
            dict(type="p", text=f"**The directed graph.** Edges {' '.join(dr['edges'])}: strong components {', '.join('{' + c + '}' for c in dr['comps'])}, in the order Tarjan's method completes them."),
            dict(type="p", text=f"**Checked.** {ck['u']} random undirected graphs and {ck['dgr']} random directed graphs of {ck['lo']} to {ck['hi']} vertices: every cut vertex found by lowpoints was one whose removal splits the graph, and no other ({ck['cuts']} in all); every pair of vertices was in the same strong component exactly when each can reach the other ({ck['comps']} components in all)."),
            dict(type="table", head=["Vertices V", "Edges E", "Steps (numbering a vertex or examining an edge)"], num=[0, 1, 2], rows=[list(x) for x in ln]),
            dict(type="p", text=f"On the graph of {sl['n']} vertices, finding everything each vertex can reach, one search per vertex, took {sl['slow']} steps against {sl['fast']} ({sl['times']} times more)."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A sabbatical at Stanford", toc="The evidence", blocks=[
            dict(type="p", text="Tarjan's Turing Award lecture, \"Algorithm Design\" (*Communications of the ACM*, March 1987), tells it: he entered Stanford after Caltech in 1969, and in June 1970 \"John Hopcroft arrived from Cornell to begin a sabbatical year at Stanford\". \"The focus of our activities became the problem of testing the planarity of a graph.\" \"After carefully studying the properties of depth-first search, we developed a way to generate paths in O(n) time using depth-first search.\""),
            dict(type="p", text="Tarjan's paper \"Depth-First Search and Linear Graph Algorithms\" (Cornell University; *SIAM Journal on Computing* 1(2), June 1972; received 30 August 1971) bounds the time and space of its two algorithms by k₁V + k₂E + k₃, and defines LOWLINK(v) as \"the smallest vertex which is in the same component as v and is reachable by traversing zero or more tree arcs followed by at most one frond or cross-link\". Hopcroft and Tarjan's planarity test followed in the *Journal of the ACM* in 1974, \"the first linear-time algorithm for planarity testing\" (Wikipedia). They shared the 1986 Turing Award \"For fundamental achievements in the design and analysis of algorithms and data structures\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Back to the maze", toc="Full circle", blocks=[
            dict(type="p", text="\"A version of depth-first search was investigated in the 19th century by French mathematician Charles Pierre Trémaux as a strategy for solving mazes\" (Wikipedia), and every depth-first search tree is what graph theorists now call a Trémaux tree. What Hopcroft and Tarjan added was not the walk but the bookkeeping, and the insistence that the whole job be done in one pass."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Euler asked of seven bridges whether a walk could cross each once (Era 3, topic 7). Here a walk that crosses each of {ln[-1][1]} one-way roads once finds who can reach whom, in {ln[-1][2]} steps."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("In an undirected graph, why can a non-tree edge never join two different branches of the search tree?", "When the search first reached the earlier of the two vertices, it would have followed that edge before backing out, making it a tree edge."),
            ("Vertex D has number 3; its child E has lowpoint 3. What does that tell you?", "Nothing below E reaches above D, so removing D cuts E's part off: D is a cut vertex."),
            ("Why is the root a special case?", "It has nothing above it; it is a cut vertex exactly when it has two or more children in the search tree."),
            ("How many steps does the search take on a graph with 100 vertices and 300 edges?", "About V + E = 400 for a directed graph (each edge examined once)."),
            ("What are the strong components of a one-way cycle A → B → C → A plus an edge C → D?", "{A, B, C} and {D}: D cannot get back."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Depth-First Search and Linear Graph Algorithms (1972)", text="Tarjan's paper, *SIAM Journal on Computing* 1(2).",
                 draw=C.draw_manuscript, link="https://www.cs.cmu.edu/~cdm/resources/Tarjan1972-sccs.pdf", link_text="The paper (PDF, on a Carnegie Mellon page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "DepthFirst", d["checks"],
                           "cut vertices and biconnected components of a small graph, strong components of a directed one, both against slow methods on 4,000 random graphs, and the exact step count V + E up to a million vertices.",
                           ["static int[] strongComponents(int[][] adj)"]),
    ]
    return dict(
        title="Depth-First Search", date="1970–1974",
        description="Era 6, topic 9 of The Algorithm Evolution Atlas: Hopcroft and Tarjan's depth-first search, fronds and lowpoints, cut vertices and strong components in linear time.",
        lede="Go as deep as you can, and back up only at a dead end: an old way through a maze. Hopcroft and Tarjan noticed what the walk leaves behind, and answered in one pass questions that had needed many.",
        fieldnote=f"Finding who can reach whom on a graph of {sl['n']} vertices took {sl['slow']} steps by searching from every vertex, and {sl['fast']} by Tarjan's single search. On a million vertices the count was exactly V + E, as the paper promised.",
        card=[("When", "Planarity work from 1970; paper 1972; planarity test 1974"),
              ("Where", "Stanford and Cornell"),
              ("What hurt", "Graph structure took repeated searches"),
              ("The fix", "Search order, fronds and lowpoints"),
              ("Cost", "V + E steps")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `DepthFirst.java`.",
    )
