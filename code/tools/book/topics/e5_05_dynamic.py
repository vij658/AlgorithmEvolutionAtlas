"""Era 5, topic 5: dynamic programming. Every number is parsed from DynamicProgramming.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"stages: a start, (\d+) stages of (\d+) towns, a finish, random costs from 1 to 99 ; all ([\d,]+) routes priced: ([\d,]+) additions, cheapest (\d+) ; backwards, .*?: ([\d,]+) additions, cheapest (\d+), the same ; the route, as town numbers stage by stage: ([\d ]+)$", ln):
            g = m.groups()
            d["st"] = dict(stages=g[0], towns=g[1], routes=g[2], adds=g[3], best=g[4], dpadds=g[5], dpbest=g[6], route=g[7].split())
        elif ln.startswith("grid: "):
            d["grid"] = re.findall(r"(\d+)x\d+ grid: ([\d,]+) routes ; plain recursion made ([\d,]+) calls, the table filled (\d+) entries", ln)
        elif ln.startswith("dice: "):
            d["dice"] = re.findall(r"(\d+) rolls?: ([\d/]+) = ([\d.]+)(?:, keep the first roll if it shows (\d+) or more)?", ln)
            d["diceavg"] = re.search(r"averaged ([\d.]+)$", ln).group(1)
            d["games"] = re.search(r"a ([\w,]+) 3-roll games", ln).group(1)
        elif m := re.match(r"knapsack: (\d+) random sets of (\d+) items .*? all ([\d,]+) choices .*? work: ([\d,]+) table steps against ([\d,]+) subsets looked at ; first set: capacity (\d+), best value (\d+)$", ln):
            g = m.groups()
            d["ks"] = dict(sets=g[0], items=g[1], choices=g[2], table=g[3], subsets=g[4], cap=g[5], best=g[6])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def stages_svg(d):
    st = d["st"]
    n, k = int(st["stages"]), int(st["towns"])
    route = [int(x) for x in st["route"]]

    def draw(t, standalone):
        o = []
        cols = n + 2
        x0, dx, y0, dy = 40, 62, 50, 40
        pos = {}
        for c in range(cols):
            rows = 1 if c in (0, cols - 1) else k
            for r in range(rows):
                y = y0 + (2 * dy if rows == 1 else r * dy)
                pos[(c, r)] = (x0 + c * dx, y)
        for c in range(cols - 1):
            ra = 1 if c == 0 else k
            rb = 1 if c + 1 == cols - 1 else k
            for a in range(ra):
                for b in range(rb):
                    (x1, y1), (x2, y2) = pos[(c, a)], pos[(c + 1, b)]
                    o.append(C.line(x1, y1, x2, y2, t["rule"], 0.8))
        path = [(0, 0)] + [(i + 1, route[i]) for i in range(n)] + [(cols - 1, 0)]
        for (c1, r1), (c2, r2) in zip(path, path[1:]):
            (x1, y1), (x2, y2) = pos[(c1, r1)], pos[(c2, r2)]
            o.append(C.line(x1, y1, x2, y2, t["red"], 3))
        for (c, r), (x, y) in pos.items():
            on = (c, r) in path
            o.append(C.circle(x, y, 8 if on else 6, t["red"] if on else t["surface"], t["ink2"], 1.2))
        o.append(C.text(x0, 28, "start", t["muted"], 12, "middle"))
        o.append(C.text(x0 + (cols - 1) * dx, 28, "finish", t["muted"], 12, "middle"))
        o.append(C.text(20, y0 + k * dy + 16, f"{st['routes']} routes; the cheapest (red, cost {st['best']}) found by working backwards with {st['dpadds']} additions instead of {st['adds']}.", t["muted"], 12))
        return C.svg_doc(x0 * 2 + (cols - 1) * dx, y0 + k * dy + 30, "".join(o), "A journey in stages: every possible road, and the cheapest route", t, standalone, 0.55, 760)
    return draw


DP_HTML = """
<div class="board dp-board">
  <div style="min-width:0">
    <div class="eyebrow">Rolls allowed</div>
    <div class="dp-n" id="dp-n"></div>
    <table class="dp-tab" id="dp-tab"></table>
  </div>
  <div style="min-width:0">
    <div class="dp-game" id="dp-game"></div>
    <div class="dp-btns"><button type="button" id="dp-roll">Roll</button><button type="button" id="dp-keep">Keep it</button><button type="button" id="dp-auto">Play 10,000 games by the rule</button></div>
    <p class="say" id="dp-say" aria-live="polite"></p>
  </div>
</div>
"""

DP_CSS = """
.dp-n{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 10px}
.dp-n button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.dp-tab{border-collapse:collapse;font:13px var(--mono);width:100%}
.dp-tab th,.dp-tab td{border-bottom:1px solid var(--rule);padding:4px 6px;text-align:right}
.dp-tab th{color:var(--muted);font-weight:600}
.dp-tab tr.now td{color:var(--red);font-weight:700}
.dp-game{display:flex;gap:6px;flex-wrap:wrap;min-height:52px;align-items:center}
.dp-game span{display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;border:2px solid var(--ink2);border-radius:8px;font:700 20px var(--mono)}
.dp-game span.kept{border-color:var(--blue);background:var(--blue);color:var(--on-blue)}
.dp-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
"""

DP_JS = r"""
(() => {
  const nBox = document.getElementById("dp-n");
  if (!nBox) return;
  // value of the game with k rolls left, worked backwards: V1 = 3.5, Vk = average of max(face, V(k-1))
  const V = [0, 3.5];
  for (let k = 2; k <= 8; k++) { let s = 0; for (let f = 1; f <= 6; f++) s += Math.max(f, V[k - 1]); V.push(s / 6); }
  let N = 3, rolls = [], kept = false, seed = 1957;
  const die = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return 1 + Math.floor(seed / 2147483648 * 6); };
  function table() {
    const tb = document.getElementById("dp-tab"); tb.innerHTML = "";
    const h = el("tr", {}, tb); ["rolls left", "value of the game", "keep a roll of"].forEach(x => { el("th", {}, h).textContent = x; });
    for (let k = 1; k <= N; k++) {
      const r = el("tr", {class: N - rolls.length === k && !kept ? "now" : ""}, tb);
      el("td", {}, r).textContent = k;
      el("td", {}, r).textContent = V[k].toFixed(4);
      el("td", {}, r).textContent = k === 1 ? "anything (last roll)" : `${Math.ceil(V[k - 1] + 1e-9)} or more`;
    }
  }
  function show(msg) {
    const g = document.getElementById("dp-game"); g.innerHTML = "";
    rolls.forEach((r, i) => { el("span", {class: kept && i === rolls.length - 1 ? "kept" : ""}, g).textContent = r; });
    table();
    document.getElementById("dp-say").textContent = msg;
  }
  function roll() {
    if (kept || rolls.length >= N) return;
    const r = die(); rolls.push(r);
    const left = N - rolls.length;
    if (left === 0) { kept = true; show(`Last roll: you must keep ${r}. The game is worth ${V[N].toFixed(4)} on average if played well.`); return; }
    const need = Math.ceil(V[left] + 1e-9);
    show(`You rolled ${r}. With ${left} roll${left > 1 ? "s" : ""} left, the rest of the game is worth ${V[left].toFixed(4)} on average, so ${r >= need ? "keep it" : "roll again"}: ${r} is ${r >= need ? "at least" : "less than"} ${V[left].toFixed(2)}.`);
  }
  function keep() { if (!rolls.length || kept) return; kept = true; show(`You kept ${rolls[rolls.length - 1]}.`); }
  function auto() {
    let total = 0, G = 10000;
    for (let g = 0; g < G; g++) {
      let k = N, r;
      while (true) { r = die(); k--; if (k === 0 || r > V[k]) break; }
      total += r;
    }
    rolls = []; kept = false;
    show(`10,000 games of up to ${N} rolls, each stopping as soon as the roll beats the value of the rest: average ${(total / G).toFixed(4)}; the table predicts ${V[N].toFixed(4)}.`);
  }
  for (let n = 1; n <= 6; n++) {
    const b = el("button", {type: "button", "aria-pressed": String(n === N)}, nBox); b.textContent = n;
    b.addEventListener("click", () => { N = n; rolls = []; kept = false; nBox.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); show("Roll the die. After each roll, keep it or roll again; the last roll must be kept."); });
  }
  document.getElementById("dp-roll").addEventListener("click", roll);
  document.getElementById("dp-keep").addEventListener("click", keep);
  document.getElementById("dp-auto").addEventListener("click", auto);
  show("Roll the die. After each roll, keep it or roll again; the last roll must be kept. The table, worked backwards from the last roll, says when to stop.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How dynamic programming combined older ideas, and where it led")
    W = 210
    nodes = {
        "pts": (20, 20, "The problem of points", "Pascal's table, filled from the end", "Era 3 topic 4", "ink"),
        "tab": (395, 20, "Tables", "compute each entry once, keep it", "Eras 1 to 3", "ink"),
        "rec": (770, 20, "Decisions in stages", "the RAND questions of the 1950s", "", "ink"),
        "dp": (395, 170, "Dynamic programming", "⊕ the principle of optimality", "Bellman, RAND, 1952–1957", "red"),
        "dij": (20, 330, "Shortest paths", "the principle, one town at a time", "topic 7", "ink"),
        "ks": (395, 330, "Knapsacks and schedules", "a table over capacities or times", "", "ink"),
        "be": (770, 330, "The Bellman equation", "value = best of (reward + value next)", "", "ink"),
        "today": (395, 480, "Today", "route planners, sequence alignment, game play", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("pts", "dp", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("tab", "dp", ports=("bottom", "top"))
    D.edge("rec", "dp", ports=("bottom", "top:0.85"))
    D.edge("dp", "dij", ports=("bottom:0.1", "top:0.7"))
    D.edge("dp", "ks", ports=("bottom", "top"))
    D.edge("dp", "be", ports=("bottom:0.9", "top:0.3"))
    D.edge("ks", "today", ports=("bottom", "top"))
    D.edge("be", "today", ports=("bottom:0.3", "right:0.5"))
    D.edge("dij", "today", ports=("bottom:0.6", "left:0.5"))
    D.text(20, 615, "Dashed: the same method, not a documented influence. Wikipedia calls Dijkstra's logic a paraphrase of Bellman's principle.", "caption")
    return D


def chain(d):
    st, g, dice = d["st"], d["grid"], d["dice"]
    steps = [
        (f"Decisions in stages: {st['routes']} complete routes to price, {st['adds']} additions",
         f"Work backwards, each town keeping only its best way on: {st['dpadds']} additions, the same answer", "Bellman's principle of optimality"),
        (f"Plain recursion asks the same questions again: {g[-1][2]} calls for a {g[-1][0]}x{g[-1][0]} grid",
         f"Keep each answer in a table: {g[-1][3]} entries", "store, don't recompute"),
        ("Chance enters: the next stage is a roll of a die",
         f"Best expected value, worked backwards: {dice[2][1]} for three rolls", "the same principle, with averages"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from listing plans to working backwards")
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
    st, g, dice, ks = d["st"], d["grid"], d["dice"], d["ks"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Pascal had already valued an unfinished game by filling a table from the last round backwards (Era 3). Bellman, set to study \"multistage decision processes\" at RAND, turned that into a principle for every plan made in stages: whatever the first decision, the rest must be best for the situation it leaves. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: dynamic programming. Blue: where it works today."),
        ]),
        dict(id="dice", eyebrow="Try it", title="Roll, or stop? Ask the table", toc="Try it", blocks=[
            dict(type="p", text="You may roll a die up to n times and you keep the last roll. When should you stop? Work backwards: with one roll left the game is worth 3.5 on average, so with two left you should keep a first roll of 4 or more, and so on. Play against the table, or let the page play 10,000 games by its rule."),
            dict(type="widget", html=DP_HTML, js=DP_JS, css=DP_CSS,
                 fallback=dict(type="table", head=["Rolls allowed", "Value of the game", "Keep the first roll if it shows"], num=[0, 1],
                               rows=[[n, v, (k + " or more") if k else "(must keep)"] for n, f, v, k in dice]),
                 note="In the interactive edition you can play the dice game against the table."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Start at the end", toc="How it works", blocks=[
            dict(type="p", text=f"**A journey in stages.** A start, {st['stages']} stages of {st['towns']} towns, a finish, and a cost on every road between neighbouring stages. Trying every route means pricing {st['routes']} routes, {st['adds']} additions. Working backwards, each town of the last stage knows its cost to the finish; each town of the stage before takes the cheapest of (road + that town's cost); and so on to the start: {st['dpadds']} additions, and the same cheapest cost, {st['dpbest']}. The route can be read off by following each town's best choice forwards: towns {' → '.join(st['route'])}."),
            dict(type="svg", name="stages", draw=stages_svg(d), alt="A journey in stages: every possible road, and the cheapest route"),
            dict(type="p", text="**Overlapping questions.** How many routes run from one corner of a grid to the other, moving right or down? Plain recursion asks \"how many from here?\" for the same corners over and over; a table asks each corner once:"),
            dict(type="table", head=["Grid", "Routes", "Calls by plain recursion", "Entries in the table"], num=[1, 2, 3],
                 rows=[[f"{n}×{n}", r, c, e] for n, r, c, e in g], hl=len(g) - 1),
            dict(type="callout", kind="key", label="Key idea",
                 text="An optimal plan is made of optimal pieces. So solve the smallest pieces first, keep their answers, and build every larger answer from stored ones; nothing is solved twice."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Exact values, and a knapsack", toc="Measured", blocks=[
            dict(type="table", head=["Rolls allowed", "Value of the game (exact)", "Decimal", "Keep the first roll if it shows"], num=[0, 2],
                 rows=[[n, f, v, (k + " or more") if k else "(must keep)"] for n, f, v, k in dice], hl=2),
            dict(type="p", text=f"Worked backwards as exact fractions. A {d['games']} three-roll games played by the rule averaged {d['diceavg']}, against the exact {dice[2][1]} = {dice[2][2]}."),
            dict(type="p", text=f"**The knapsack.** For {ks['sets']} random sets of {ks['items']} items, a table indexed by capacity (each item considered once, every capacity updated) agreed every time with a search through all {ks['choices']} choices. The table took {ks['table']} steps in all; the search looked at {ks['subsets']} subsets. In the first set the sack held {ks['cap']} units and the best value was {ks['best']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A name chosen at RAND", toc="The evidence", blocks=[
            dict(type="p", text="\"Bellman left Stanford in 1952 and took up the position of Research Mathematician at RAND\"; \"Bellman's first publication on dynamic programming appeared in 1952\", and RAND published his first book on it in 1953 (MacTutor). RAND lists his memorandum RM-813, \"On a problem in dynamic programming\" (1952). The book *Dynamic Programming* followed in 1957."),
            dict(type="p", text="Bellman's own story of the name, from his autobiography (1984): \"I spent the Fall quarter (of 1950) at RAND. My first task was to find a name for multistage decision processes\"; the Secretary of Defense, Wilson, \"had a pathological fear and hatred of the word, research\"; \"it's impossible to use the word, dynamic, in a pejorative sense\"; \"It was something not even a Congressman could object to.\" The story does not fit the calendar: Wilson became Secretary of Defense in 1953, after Bellman's first paper using the term, and Kushner recalled Bellman saying he \"was trying to upstage Dantzig's linear programming by adding dynamic\". The catalog marks the story as disputed."),
            dict(type="p", text="On the principle of optimality, asked whether it was rigorous: \"Of course not. It's not even precise. A good principle should guide the intuition.\""),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Pascal's table, a principle at last", toc="Full circle", blocks=[
            dict(type="p", text="Pascal valued an interrupted game by filling a table backwards from the last round (Era 3, topic 4). Bellman's principle says why that works for any process in stages, with or without chance. Dijkstra's shortest paths (topic 7) are described as a paraphrase of it, and the Bellman equation, which restates an optimization problem in recursive form, is the centre of the subject."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{st['routes']} routes, {st['dpadds']} additions. The table does not make the problem smaller; it makes sure each piece is solved only once."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With two rolls allowed, why keep a first roll of 4 but not of 3?", "Rolling again is worth 3.5 on average: 4 beats it, 3 does not."),
            ("Check the value of the two-roll game.", "Keep 4, 5 or 6 (worth 4, 5, 6); otherwise roll again (worth 3.5 each for faces 1, 2, 3): (3 × 3.5 + 4 + 5 + 6)/6 = 25.5/6 = 4.25 = 17/4."),
            ("How many routes cross a 3×3 grid, moving right or down?", "Choose which 3 of the 6 moves go right: C(6,3) = 20. The table has 4 × 4 = 16 entries."),
            ("Why does working backwards need fewer additions than pricing every route?", "Every route shares its tail with many others; working backwards prices each tail once and reuses it."),
            ("When does dynamic programming not help?", "When the sub-problems do not repeat, or when there are so many different situations that the table itself is too large."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Richard Bellman on the Birth of Dynamic Programming (2002)", text="Stuart Dreyfus's introduction to excerpts from Bellman's autobiography, in Operations Research.",
                 draw=C.draw_manuscript, link="https://web.cs.miami.edu/home/odelia/teaching/csc317_fall19/syllabus/dy_birth.pdf", link_text="PDF on a course page", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "DynamicProgramming", d["checks"],
                           f"the cheapest of {st['routes']} routes both ways, path counts by recursion and by table, the exact values of the dice game with a simulation, and the knapsack table against every subset for {ks['sets']} random sets.",
                           ["static long pathsNaive(int r, int c)"]),
    ]
    return dict(
        title="Dynamic Programming", date="1952–1957",
        description="Era 5, topic 5 of The Algorithm Evolution Atlas: Bellman's dynamic programming, with a journey in stages, overlapping sub-problems, an exactly valued dice game and the knapsack.",
        lede="Plans made in stages multiply beyond counting. Bellman's principle: whatever you do first, the rest of a best plan must be best from where you then stand. So start at the end, and work backwards.",
        fieldnote=f"I priced all {st['routes']} routes of a ten-stage journey: {st['adds']} additions. Working backwards took {st['dpadds']}. The answer was the same, {st['best']}. The method's inventor said he chose its name so that no official could object to it; the dates in his story do not quite agree.",
        card=[("When", "1952 papers; 1957 book"),
              ("Where", "RAND Corporation, Santa Monica"),
              ("What hurt", "Plans in stages multiply beyond listing"),
              ("The fix", "The principle of optimality: work backwards, store each answer"),
              ("Saving", f"{st['dpadds']} additions instead of {st['adds']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `DynamicProgramming.java`.",
    )
