"""Era 6, topic 4: A*, search guided by an estimate. Every number is parsed from AStar.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"maps": {}}
    for ln in text.splitlines():
        if m := re.match(r"small: a (\d+) x (\d+) map, .*? Dijkstra \(h not used\) takes (\d+) squares, path (\d+) steps ; greedy \(h only\) takes (\d+) squares, path (\d+) steps ; A\* \(g \+ h\) takes (\d+) squares, path (\d+) steps", ln):
            d["small"] = dict(w=m.group(1), h=m.group(2), dij=m.group(3), dij_len=m.group(4), gre=m.group(5), gre_len=m.group(6), ast=m.group(7), ast_len=m.group(8))
        elif m := re.match(r"map-(\w+): (.*)$", ln):
            d["maps"][m.group(1)] = m.group(2).split("/")
        elif m := re.match(r"large: a (\d+) x \d+ map, (\d+)% of squares walled at random, ([\d,]+) open ; .*? shortest path (\d+) steps", ln):
            d["large"] = dict(n=m.group(1), pct=m.group(2), open=m.group(3), path=m.group(4),
                              rows=re.findall(r"h = ([^;:]+?): ([\d,]+) squares taken", ln))
        elif m := re.match(r"many: ([\d,]+) random (\d+) x \d+ maps, (\d+)% walls, .*? the greedy method returned a longer path on ([\d,]+) \((\d+)%\), at worst ([\d.]+) times too long ; squares taken on average: Dijkstra (\d+), A\* (\d+), greedy (\d+)", ln):
            d["many"] = dict(maps=m.group(1), size=m.group(2), walls=m.group(3), longer=m.group(4), pct=m.group(5), worst=m.group(6),
                             dij=m.group(7), ast=m.group(8), gre=m.group(9))
        elif ln.startswith("weighted: "):
            d["weighted"] = re.findall(r"w = ([\d.]+): ([\d,]+) squares, path (\d+) \(([\d.]+) times the shortest\)", ln)
        elif m := re.match(r"inconsistent: the same ([\d,]+) maps, .*? never takes a square twice returned a longer path on ([\d,]+) maps, at worst ([\d.]+) times too long ; .*? right on all ([\d,]+), reopening ([\d,]+) squares on ([\d,]+) maps", ln):
            d["inc"] = dict(maps=m.group(1), wrong=m.group(2), worst=m.group(3), right=m.group(4), reopened=m.group(5), mapsre=m.group(6))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def maps_svg(d):
    mp, sm = d["maps"], d["small"]
    names = [("dijkstra", f"Dijkstra: {sm['dij']} squares taken, path {sm['dij_len']}"),
             ("greedy", f"Greedy: {sm['gre']} squares, path {sm['gre_len']}"),
             ("astar", f"A*: {sm['ast']} squares, path {sm['ast_len']}")]

    def draw(t, standalone):
        o = []
        rows = mp["astar"]
        cell = 11
        gw, gh = len(rows[0]) * cell, len(rows) * cell
        W = 20 + 3 * (gw + 22)
        H = gh + 70
        for k, (key, label) in enumerate(names):
            x0, y0 = 20 + k * (gw + 22), 34
            o.append(C.text(x0, 22, label, t["ink"], 12, "start", 700))
            for i, row in enumerate(mp[key]):
                for j, ch in enumerate(row):
                    fill = {"#": t["ink"], "o": t["axis"], "*": t["red"], "S": t["blue"], "G": t["blue"]}.get(ch, t["wash"])
                    o.append(C.rect(x0 + j * cell, y0 + i * cell, cell - 1, cell - 1, fill))
        o.append(C.text(20, H - 14, "Black: wall. Grey: squares taken by the search. Red: the path found. Blue: start (left) and goal (right).", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Three searches on the same small map", t, standalone, 0.55, W)
    return draw


AS_HTML = """
<div class="board as-board">
  <div style="min-width:0">
    <div class="as-grid" id="as-grid"></div>
  </div>
  <div style="min-width:0">
    <div class="as-btns">
      <button type="button" id="as-dij">Dijkstra</button><button type="button" id="as-gre">Greedy</button><button type="button" id="as-ast">A*</button>
    </div>
    <div class="as-btns"><button type="button" id="as-clear">Clear the walls</button><button type="button" id="as-cup">The cup</button></div>
    <div class="as-stats" id="as-stats"></div>
    <p class="say" id="as-say" aria-live="polite"></p>
  </div>
</div>
"""

AS_CSS = """
.as-grid{display:grid;grid-template-columns:repeat(22,minmax(0,1fr));gap:1px;background:var(--rule);border:1px solid var(--rule);touch-action:none}
.as-grid span{aspect-ratio:1;background:var(--surface);cursor:pointer}
.as-grid span.w{background:var(--ink)}
.as-grid span.v{background:var(--axis)}
.as-grid span.p{background:var(--red)}
.as-grid span.s,.as-grid span.g{background:var(--blue)}
.as-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.as-stats{font:13px var(--mono);display:grid;gap:3px}
"""

AS_JS = r"""
(() => {
  const gridBox = document.getElementById("as-grid");
  if (!gridBox) return;
  const CUP = __CUP__;
  const R = CUP.length, Cc = CUP[0].length;
  let wall, S, G, last = null, painting = null;
  function load(rows) {
    wall = rows.map(r => [...r].map(ch => ch === "#"));
    rows.forEach((r, i) => [...r].forEach((ch, j) => { if (ch === "S") S = [i, j]; if (ch === "G") G = [i, j]; }));
  }
  function search(kind) {
    const h = (r, c) => Math.abs(r - G[0]) + Math.abs(c - G[1]);
    const gw = kind === "gre" ? 0 : 1, hw = kind === "dij" ? 0 : 1;
    const g = Array.from({length: R}, () => new Array(Cc).fill(Infinity)), par = {}, closed = new Set(), taken = [];
    const open = [[hw * h(...S), 0, S[0], S[1], 0]];
    let order = 1;
    g[S[0]][S[1]] = 0;
    while (open.length) {
      open.sort((a, b) => a[0] - b[0] || b[1] - a[1] || a[4] - b[4]);
      const [f, gg, r, c] = open.shift(), key = r * Cc + c;
      if (closed.has(key) || gg !== g[r][c]) continue;
      closed.add(key); taken.push(key);
      if (r === G[0] && c === G[1]) break;
      for (const [dr, dc] of [[-1, 0], [0, 1], [1, 0], [0, -1]]) {
        const a = r + dr, b = c + dc;
        if (a < 0 || b < 0 || a >= R || b >= Cc || wall[a][b] || closed.has(a * Cc + b)) continue;
        const ng = gg + 1;
        if (ng >= g[a][b]) continue;
        if (gw === 0 && g[a][b] !== Infinity) continue;
        g[a][b] = ng; par[a * Cc + b] = key;
        open.push([gw * ng + hw * h(a, b), ng, a, b, order++]);
      }
    }
    const goal = G[0] * Cc + G[1], path = [];
    if (closed.has(goal)) for (let k = par[goal]; k !== undefined && k !== S[0] * Cc + S[1]; k = par[k]) path.push(k);
    return {taken, path, found: closed.has(goal), len: closed.has(goal) ? path.length + 1 : 0};
  }
  function show() {
    gridBox.innerHTML = "";
    const tk = new Set(last ? last.taken : []), pt = new Set(last ? last.path : []);
    for (let i = 0; i < R; i++) for (let j = 0; j < Cc; j++) {
      const k = i * Cc + j;
      let cls = wall[i][j] ? "w" : pt.has(k) ? "p" : tk.has(k) ? "v" : "";
      if (i === S[0] && j === S[1]) cls = "s"; if (i === G[0] && j === G[1]) cls = "g";
      el("span", {class: cls, "data-k": k}, gridBox);
    }
  }
  function run(kind) {
    last = search(kind);
    const names = {dij: "Dijkstra (h not used)", gre: "Greedy (h only)", ast: "A* (g + h)"};
    const st = document.getElementById("as-stats"); st.innerHTML = "";
    el("div", {}, st, names[kind]);
    el("div", {}, st, `squares taken: ${last.taken.length}`);
    el("div", {}, st, last.found ? `path: ${last.len} steps` : "no path: the goal is walled off");
    document.getElementById("as-say").textContent = !last.found ? "Open a gap in the walls." :
      kind === "dij" ? "Dijkstra spreads evenly in every direction, nearest first." :
      kind === "gre" ? "Greedy heads straight for the goal and keeps the first way it found to each square, however roundabout." :
      "A* spends a little on the distance already travelled, and returns a shortest path.";
    show();
  }
  gridBox.addEventListener("pointerdown", e => {
    const k = e.target.dataset && e.target.dataset.k; if (k === undefined) return;
    const i = Math.floor(k / Cc), j = k % Cc;
    if ((i === S[0] && j === S[1]) || (i === G[0] && j === G[1])) return;
    painting = !wall[i][j]; wall[i][j] = painting; last = null; show();
    document.getElementById("as-say").textContent = "Walls changed: run a search again.";
  });
  gridBox.addEventListener("pointerover", e => {
    if (painting === null || !(e.buttons & 1)) return;
    const k = e.target.dataset && e.target.dataset.k; if (k === undefined) return;
    const i = Math.floor(k / Cc), j = k % Cc;
    if ((i === S[0] && j === S[1]) || (i === G[0] && j === G[1])) return;
    wall[i][j] = painting; show();
  });
  window.addEventListener("pointerup", () => { painting = null; });
  document.getElementById("as-dij").addEventListener("click", () => run("dij"));
  document.getElementById("as-gre").addEventListener("click", () => run("gre"));
  document.getElementById("as-ast").addEventListener("click", () => run("ast"));
  const fresh = () => { last = null; document.getElementById("as-stats").innerHTML = ""; document.getElementById("as-say").textContent = "Run a search."; show(); };
  document.getElementById("as-clear").addEventListener("click", () => { load(CUP.map(r => r.replace(/#/g, "."))); fresh(); });
  document.getElementById("as-cup").addEventListener("click", () => { load(CUP); fresh(); });
  load(CUP); run("ast");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How A* combined older ideas, and where it led")
    W = 210
    nodes = {
        "dij": (20, 20, "Dijkstra's method", "settle the nearest place first", "Era 5, topic 7", "ink"),
        "gt": (395, 20, "The Graph Traverser", "step towards what looks nearest the goal", "a heuristic search", "ink"),
        "shk": (770, 20, "Shakey the robot", "must plan routes across a room", "SRI, 1966–1972", "ink"),
        "ast": (395, 180, "A*", "⊕ f = g + h, with h never too high", "Hart, Nilsson and Raphael, 1968", "red"),
        "w": (20, 340, "Weighted A*", "trade a longer path for less search", "", "ink"),
        "games": (395, 340, "Games and robots", "path-finding on maps", "", "ink"),
        "nav": (770, 340, "Driving directions", "web services and car navigation", "IEEE Milestone page", "ink"),
        "today": (395, 490, "Today", "\"the path-finding algorithm of choice\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("dij", "ast", ports=("bottom", "top:0.15"), label="h = 0", at=0.5, dx=-8, anchor="end")
    D.edge("gt", "ast", ports=("bottom", "top"), label="g ignored", at=0.5, dx=8, anchor="start")
    D.edge("shk", "ast", ports=("bottom", "top:0.85"), label="the need", at=0.5, dx=8, anchor="start")
    D.edge("ast", "w", ports=("bottom:0.15", "top"))
    D.edge("ast", "games", ports=("bottom", "top"))
    D.edge("ast", "nav", ports=("bottom:0.85", "top"))
    D.edge("games", "today", ports=("bottom", "top"))
    D.text(20, 615, "A* with h = 0 is Dijkstra's method; with the distance so far ignored it is the greedy Graph Traverser. Quote: the IEEE Milestone page for Shakey.", "caption")
    return D


def chain(d):
    sm, mn, inc = d["small"], d["many"], d["inc"]
    lg = d["large"]["rows"]
    steps = [
        (f"Dijkstra's method spreads in every direction: {sm['dij']} squares taken on the small map",
         f"Greedy search heads for the goal: {sm['gre']} squares", "the Graph Traverser"),
        (f"Greedy paths can be long: {sm['gre_len']} steps where {sm['dij_len']} would do; longer on {mn['pct']}% of random maps",
         f"A*: f = g + h; a shortest path every time, with {sm['ast']} squares", "Hart, Nilsson and Raphael, 1968"),
        (f"A weak estimate barely helps: {lg[1][1]} squares on the large map",
         f"A better estimate (rows + columns apart): {lg[2][1]} squares; a perfect one: {lg[3][1]}", "more informed, less search"),
        (f"An estimate that is never too high but jumps about: wrong on {inc['wrong']} of {inc['maps']} maps",
         f"Reopen a square when a shorter way to it appears: right on all {inc['right']}", "the consistency question, 1968 to 1985"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from blind search to a guided one")
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
    sm, lg, mn, wt, inc = d["small"], d["large"], d["many"], d["weighted"], d["inc"]
    cup = "[" + ",".join(f'"{r.replace("o", ".").replace("*", ".")}"' for r in d["maps"]["astar"]) + "]"
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Dijkstra's method counts only the distance already travelled; the Graph Traverser looked only at an estimate of the distance still to go. A* adds the two. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: A*. Blue: where it is used today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Three searches, one map", toc="Try it", blocks=[
            dict(type="p", text="The program's small map: start on the left (blue), goal on the right, a cup-shaped wall between. Run each search and compare the squares it takes (grey) and the path it returns (red). Then draw your own walls by clicking or dragging on the grid. The estimate h is the number of rows apart plus columns apart, ignoring walls."),
            dict(type="widget", html=AS_HTML, js=AS_JS.replace("__CUP__", cup), css=AS_CSS,
                 fallback=dict(type="table", head=["Search on the small map", "Squares taken", "Path (steps)"], num=[1, 2],
                               rows=[["Dijkstra (h not used)", sm["dij"], sm["dij_len"]], ["Greedy (h only)", sm["gre"], sm["gre_len"]], ["A* (g + h)", sm["ast"], sm["ast_len"]]], hl=2),
                 note="In the interactive edition you can draw walls and run the three searches yourself."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Cost so far, plus an estimate of the rest", toc="How it works", blocks=[
            dict(type="p", text="**The rule.** Keep a set of places reached but not yet taken. Take next the place n with the smallest f(n) = g(n) + h(n): g(n) is the length of the best path found so far from the start to n, and h(n) an estimate of the distance from n to the goal. Taking a place means looking at its neighbours and recording any shorter way to them."),
            dict(type="p", text="**Admissible.** If h never overestimates the true remaining distance, the first time the goal is taken its path is a shortest one: any place on a shorter path would have had a smaller f, and been taken first. With h = 0 the rule is Dijkstra's method; with a perfect h it walks straight along a shortest path and takes nothing else."),
            dict(type="p", text="**Consistent.** If also h never drops by more than the length of a step (h(m) ≤ cost(m, n) + h(n)), no place ever needs to be taken twice. Without that, A* must be allowed to reopen a place when a shorter way to it appears."),
            dict(type="svg", name="maps", draw=maps_svg(d), alt="Three searches on the same small map", width=800,
                 caption="The program's three searches on the small map, as it printed them."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Knowledge about where the goal lies can cut the search, as long as it never promises the goal is nearer than it is. A guess that is too optimistic costs time; a guess that is too pessimistic can cost the right answer."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Squares taken, paths returned", toc="Measured", blocks=[
            dict(type="p", text=f"**A large map.** {lg['n']} × {lg['n']} squares, {lg['pct']}% walled at random ({lg['open']} open), from one corner to the other. All four searches found the shortest path, {lg['path']} steps; the better the estimate, the fewer squares taken."),
            dict(type="table", head=["Estimate h", "Squares taken"], num=[1], rows=[[a, b] for a, b in lg["rows"]], hl=3),
            dict(type="p", text=f"**Random maps.** On {mn['maps']} random {mn['size']} × {mn['size']} maps with {mn['walls']}% walls, A* found a shortest path every time; the greedy method returned a longer path on {mn['longer']} of them ({mn['pct']}%), at worst {mn['worst']} times too long. Squares taken on average: Dijkstra {mn['dij']}, A* {mn['ast']}, greedy {mn['gre']}."),
            dict(type="p", text="**Weighted A*.** Multiplying the estimate by w > 1 makes the search greedier: fewer squares, and a path never more than w times the shortest."),
            dict(type="table", head=["w", "Squares taken", "Path", "× shortest"], num=[0, 1, 2, 3], rows=[list(x) for x in wt]),
            dict(type="p", text=f"**An estimate that is never too high but jumps about.** The true distance times a random number between 0 and 1, fixed for each square: admissible, but not consistent. On the same {inc['maps']} maps, A* that never takes a square twice returned a longer path on {inc['wrong']}, at worst {inc['worst']} times too long; A* that reopens a square when a shorter way to it appears was right on all {inc['right']}, reopening {inc['reopened']} squares on {inc['mapsre']} maps."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A robot that needed a route", toc="The evidence", blocks=[
            dict(type="p", text="Hart, Nilsson and Raphael's paper, \"A Formal Basis for the Heuristic Determination of Minimum Cost Paths\" (manuscript received 24 November 1967; *IEEE Transactions on Systems Science and Cybernetics* SSC-4(2): 100–107, July 1968), begins with a complaint: \"there has been no underlying theory to guide the development of efficient search procedures.\" It defines f(n) = g(n) + h(n), proves that A* is admissible when the estimate is a lower bound, introduces what it calls \"the consistency assumption\", and shows that A* \"expands the fewest possible nodes necessary to guarantee finding an optimal path\"."),
            dict(type="p", text="The method was made for Shakey, Stanford Research Institute's mobile robot. In Raphael's recollection, Nilsson presented a route-planning method he called Algorithm A \"For lack of anything better\"; Raphael proposed a change, Hart suggested the new version might be optimal, they proved under what conditions, and called it A* (Communications of the ACM). Wikipedia notes that a later correction claimed consistency was not needed, and that Dechter and Pearl showed in 1985 that this was false: the program's last experiment shows the same effect."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Dijkstra's method, with a sense of direction", toc="Full circle", blocks=[
            dict(type="p", text="Set h to zero and A* is exactly Dijkstra's method of 1956 (Era 5, topic 7); Wikipedia calls Dijkstra's algorithm \"a special case of A*\". The IEEE Milestone page for Shakey calls A* \"the path-finding algorithm of choice for a wide variety of applications\", including \"computing driving directions (whether by a web service or a car navigation system)\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"On the large map, Dijkstra's method took {lg['rows'][0][1]} squares; the same search with an estimate of the distance to go took {lg['rows'][2][1]}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("On a grid with moves up, down, left and right, why is \"rows apart + columns apart\" never too high?", "Every path must cover at least that many rows and columns, one step each; walls can only make it longer."),
            ("Why is the straight-line distance a weaker estimate on such a grid?", "It is smaller than rows + columns (the diagonal is shorter), so it tells the search less, and more squares look promising."),
            ("What does A* become if h is the true remaining distance?", "It walks straight along a shortest path, taking only the squares on it."),
            ("Why can the greedy method return a long path?", "It ignores the distance already travelled, so it keeps the first way it found to each square, however roundabout."),
            ("With w = 2, how long can weighted A*'s path be?", "At most twice the shortest, if h is admissible."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Formal Basis for the Heuristic Determination of Minimum Cost Paths (1968)", text="Hart, Nilsson and Raphael, *IEEE Transactions on Systems Science and Cybernetics* SSC-4(2): 100–107.",
                 draw=C.draw_manuscript, link="https://people.stfx.ca/jdelamer/courses/csci-564/_downloads/b2220c66675ddde471ca1795147b8e86/A_Formal_Basis_for_the_Heuristic_Determination_of_Minimum_Cost_Paths.pdf", link_text="The paper (PDF scan, on a course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "AStar", d["checks"],
                           "three searches on a small map, four estimates on a 400 × 400 map, A* against breadth-first distances on 2,000 random maps, weighted A* within its bound, and an inconsistent estimate with and without reopening.",
                           ["static Result search(boolean[][] wall, int sr, int sc, int tr, int tc, Estimate est, double gw, double hw, boolean reopen)"]),
    ]
    return dict(
        title="A*: Search Guided by an Estimate", date="1968",
        description="Era 6, topic 4 of The Algorithm Evolution Atlas: Hart, Nilsson and Raphael's A* for the robot Shakey, admissible and consistent estimates, measured on grids.",
        lede="Dijkstra's method finds the shortest route by spreading out in every direction. A robot that knows roughly where its goal lies can do better, if its guess never promises the goal is nearer than it is.",
        fieldnote=f"On a map of {lg['n']} × {lg['n']} squares the blind search took {lg['rows'][0][1]} squares to find the way; guided by a simple estimate it took {lg['rows'][2][1]}. The robot that needed it was Shakey; the method outlived the robot, and the IEEE now calls it the path-finding algorithm of choice.",
        card=[("When", "Received 1967; published 1968"),
              ("Where", "Stanford Research Institute"),
              ("What hurt", "Blind search wastes work; greedy search returns long paths"),
              ("The fix", "f = g + h, with h never too high"),
              ("Measured", f"{lg['rows'][2][1]} squares instead of {lg['rows'][0][1]}, same path")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AStar.java`.",
    )
