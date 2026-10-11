"""Era 4, topic 4: the cheapest network (Borůvka, Jarník). Every number is parsed from CheapestNetwork.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("towns: "):
            d["towns"] = [tuple(int(v) for v in p.split(",")) for p in ln[7:].split()]
        elif m := re.match(r"boruvka: pieces after each round (.+?) ; (\d+) rounds, (\d+) comparisons of a line$", ln):
            d["bor"] = dict(pieces=[int(x) for x in m.group(1).split(" -> ")], rounds=int(m.group(2)), cmp=int(m.group(3)))
        elif m := re.match(r"same: Boruvka, Jarnik \((\d+) comparisons\) and Kruskal \((\d+) lines examined after sorting (\d+)\) choose the same (\d+) lines, total length ([\d.]+) ; lines (.+)$", ln):
            d["same"] = dict(jar=int(m.group(1)), kru=int(m.group(2)), sorted=int(m.group(3)), n=int(m.group(4)), length=m.group(5),
                             lines=[tuple(int(v) for v in e.split("-")) for e in m.group(6).split()])
        elif m := re.match(r"rounds: (\d+) more sets of 40 towns ; (.+?) ; every round", ln):
            d["rounds"] = dict(sets=int(m.group(1)), hist=[(int(a), int(b)) for a, b in re.findall(r"(\d+) rounds: (\d+)", m.group(2))])
        elif m := re.match(r"brute: (\d+) sets of (\d+) towns, every one of the (\d+) possible networks each \((\d+) in all\)", ln):
            d["brute"] = dict(sets=int(m.group(1)), n=int(m.group(2)), each=int(m.group(3)), total=int(m.group(4)))
        elif m := re.match(r"cut: (\d+) random splits", ln):
            d["cut"] = int(m.group(1))
    d["checks"] = C.checks(text)
    return d


def _d2(P, i, j):
    return (P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2


def _key(P, i, j):
    return (_d2(P, i, j), min(i, j), max(i, j))


def boruvka_rounds(P):
    """Borůvka's rounds with the program's tie-breaking rule: a list of rounds, each a list of new lines."""
    n = len(P)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    rounds, count = [], n
    while count > 1:
        best = {}
        for i in range(n):
            for j in range(i + 1, n):
                a, b = find(i), find(j)
                if a == b:
                    continue
                for r in (a, b):
                    if r not in best or _key(P, i, j) < _key(P, *best[r]):
                        best[r] = (i, j)
        new = []
        for r, (i, j) in sorted(best.items()):
            a, b = find(i), find(j)
            if (min(i, j), max(i, j)) not in new:
                new.append((min(i, j), max(i, j)))
            if a != b:
                parent[a] = b
                count -= 1
        rounds.append(new)
    return rounds


# ----------------------------------------------------------------------------------------------------------------------
def network_svg(d):
    P = d["towns"]
    rounds = boruvka_rounds(P)
    assert sorted(e for r in rounds for e in r) == sorted(d["same"]["lines"]), "Python rounds disagree with the program"

    def draw(t, standalone):
        out, sc, x0, y0 = [], 0.5, 20, 20
        cols = [t["red"], t["yellow"], t["blue"], t["ink"]]
        for k, r in enumerate(rounds):
            for i, j in r:
                out.append(C.line(x0 + P[i][0] * sc, y0 + P[i][1] * sc, x0 + P[j][0] * sc, y0 + P[j][1] * sc, cols[k % 4], 3))
        for x, y in P:
            out.append(C.circle(x0 + x * sc, y0 + y * sc, 4.5, t["surface"], t["ink"], 1.5))
        X = 560
        out.append(C.text(X, 60, "Borůvka's rounds on 40 towns", t["ink"], 15, "start", 700))
        pcs = d["bor"]["pieces"]
        for k in range(len(rounds)):
            out.append(C.line(X, 96 + k * 34, X + 34, 96 + k * 34, cols[k % 4], 4))
            out.append(C.text(X + 44, 101 + k * 34, f"round {k + 1}: {len(rounds[k])} lines, {pcs[k]} → {pcs[k + 1]} pieces", t["ink"], 13.5))
        y = 110 + len(rounds) * 34
        out.append(C.text(X, y, f"Total length {d['same']['length']}.", t["muted"], 13))
        out.append(C.text(X, y + 20, "Jarník's growth and Kruskal's sort", t["muted"], 13))
        out.append(C.text(X, y + 38, f"choose the same {d['same']['n']} lines.", t["muted"], 13))
        out.append(C.text(X, y + 70, "Towns at random points; numbers checked", t["muted"], 12))
        out.append(C.text(X, y + 86, "by CheapestNetwork.java.", t["muted"], 12))
        return C.svg_doc(860, 540, "".join(out), "The cheapest network on forty towns, coloured by Borůvka's rounds", t, standalone, 0.55, 860)
    return draw


NW_HTML = """
<div class="board nw-board">
  <div style="min-width:0">
    <svg id="nw-svg" viewBox="0 0 520 520" role="img" aria-label="Forty towns and the lines chosen so far"></svg>
  </div>
  <div style="min-width:0">
    <div class="controls">
      <button class="primary" id="nw-b">Borůvka: next round</button>
      <button id="nw-j">Jarník: next line</button>
      <button id="nw-r">Start again</button>
    </div>
    <ol class="nw-steps" id="nw-steps"></ol>
    <p class="say" id="nw-say" aria-live="polite"></p>
  </div>
</div>
"""

NW_CSS = """
.nw-board .controls{flex-wrap:wrap;gap:8px}
.nw-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.nw-steps .m{font-family:var(--mono);font-size:12.5px}
#nw-svg{width:100%;max-width:520px;height:auto}
"""

NW_JS_TEMPLATE = r"""
(() => {
  const svg = document.getElementById("nw-svg");
  if (!svg) return;
  const P = __TOWNS__, PROG = new Set(__LINES__);
  const n = P.length, COL = ["var(--red)", "var(--yellow)", "var(--blue)", "var(--ink)"];
  const d2 = (i, j) => (P[i][0] - P[j][0]) ** 2 + (P[i][1] - P[j][1]) ** 2;
  const shorter = (i, j, k, l) => { const a = d2(i, j), b = d2(k, l); if (a !== b) return a < b;
    const mi = Math.min(i, j), mk = Math.min(k, l); if (mi !== mk) return mi < mk; return Math.max(i, j) < Math.max(k, l); };
  const key = (i, j) => Math.min(i, j) + "-" + Math.max(i, j);
  let lines, parent, mode, rounds, inTree, log;
  const find = a => { while (parent[a] !== a) a = parent[a] = parent[parent[a]]; return a; };
  function reset() { lines = []; parent = [...Array(n).keys()]; mode = null; rounds = 0; inTree = new Set([0]); log = []; draw(); }
  function pieces() { const s = new Set(); for (let i = 0; i < n; i++) s.add(find(i)); return s.size; }
  function total() { return lines.reduce((s, l) => s + Math.sqrt(d2(l.i, l.j)), 0); }
  function boruvka() {
    if (mode === "j" || pieces() === 1) return;
    mode = "b";
    const bi = {}, before = pieces();
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) {
      const a = find(i), b = find(j); if (a === b) continue;
      for (const r of [a, b]) if (!(r in bi) || shorter(i, j, bi[r][0], bi[r][1])) bi[r] = [i, j];
    }
    const added = new Set();
    for (const r of Object.keys(bi)) {
      const [i, j] = bi[r], a = find(i), b = find(j);
      if (!added.has(key(i, j))) { added.add(key(i, j)); lines.push({i, j, c: rounds}); }
      if (a !== b) parent[a] = b;
    }
    rounds++;
    log.push(`round ${rounds}: every piece takes its shortest line out; <span class="m">${added.size}</span> lines, ${before} → ${pieces()} pieces`);
    draw();
  }
  function jarnik() {
    if (mode === "b" || inTree.size === n) return;
    mode = "j";
    let best = null;
    for (const i of inTree) for (let j = 0; j < n; j++) if (!inTree.has(j) && (!best || shorter(i, j, best[0], best[1]))) best = [i, j];
    inTree.add(best[1]);
    parent[find(best[1])] = find(best[0]);
    lines.push({i: best[0], j: best[1], c: 2});
    if (inTree.size <= 4 || inTree.size === n) log.push(`line ${lines.length}: town ${best[0]} to town ${best[1]}, the shortest line from the network to a new town`);
    else if (inTree.size === 5) log.push("…");
    draw();
  }
  function draw() {
    svg.innerHTML = "";
    const s = 0.5, o = 10;
    for (const l of lines) sv("line", {x1: o + P[l.i][0] * s, y1: o + P[l.i][1] * s, x2: o + P[l.j][0] * s, y2: o + P[l.j][1] * s,
      stroke: mode === "j" ? "var(--blue)" : COL[l.c % 4], "stroke-width": 3.2}, svg);
    for (let i = 0; i < n; i++) sv("circle", {cx: o + P[i][0] * s, cy: o + P[i][1] * s, r: i === 0 && mode === "j" ? 6 : 4.5,
      fill: mode === "j" && inTree.has(i) ? "var(--blue)" : "var(--surface)", stroke: "var(--ink)", "stroke-width": 1.5}, svg);
    const ol = document.getElementById("nw-steps"); ol.innerHTML = "";
    for (const h of log) el("li", {}, ol).innerHTML = h;
    const say = document.getElementById("nw-say");
    if (lines.length === n - 1) {
      const same = lines.every(l => PROG.has(key(l.i, l.j)));
      say.textContent = `Done: ${n - 1} lines, total length ${total().toFixed(3)}. ${same ? "The same lines as the program found by all three methods." : "Different from the program!"}`;
    } else if (!mode) say.textContent = "Choose a method. Borůvka works on every piece at once; Jarník grows one network from town 0.";
    else say.textContent = `${lines.length} lines so far, ${pieces()} piece${pieces() > 1 ? "s" : ""}, length ${total().toFixed(1)}.`;
    document.getElementById("nw-b").disabled = mode === "j" || lines.length === n - 1;
    document.getElementById("nw-j").disabled = mode === "b" || lines.length === n - 1;
  }
  document.getElementById("nw-b").addEventListener("click", boruvka);
  document.getElementById("nw-j").addEventListener("click", jarnik);
  document.getElementById("nw-r").addEventListener("click", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the cheapest network combined older ideas, and where it led")
    W = 210
    nodes = {
        "eul": (20, 20, "Euler's bridges", "keep only what connects to what", "Era 3 topic 7", "ink"),
        "elec": (395, 20, "Electrifying Moravia", "lines are expensive; towns are many", "1920s", "ink"),
        "near": (770, 20, "Nearest neighbour", "join each point to the closest", "a greedy choice", "ink"),
        "bor": (395, 170, "Borůvka and Jarník", "⊕ greedy choices, proved optimal", "1926, 1930", "red"),
        "re": (20, 330, "Found again", "Choquet 1938; Florek et al. 1951; Sollin", "rediscoveries", "ink"),
        "kp": (395, 330, "Kruskal and Prim", "sort the lines; grow from one town", "1956, 1957", "ink"),
        "clu": (770, 330, "Clustering", "cut the longest lines of the tree", "Czekanowski's precursor, 1909", "ink"),
        "today": (395, 480, "Networks today", "cables, pipes, circuits; a step in harder problems", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("eul", "bor", ports=("bottom", "top:0.15"))
    D.edge("elec", "bor", ports=("bottom", "top"))
    D.edge("near", "bor", ports=("bottom", "top:0.85"))
    D.edge("bor", "re", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("bor", "kp", ports=("bottom", "top"))
    D.edge("bor", "clu", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("kp", "today", ports=("bottom", "top"))
    D.edge("clu", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: the same methods found independently, and a precursor whose method was not checked here (see the catalog).", "caption")
    return D


def chain(d):
    b, s, br = d["bor"], d["same"], d["brute"]
    steps = [
        ("Connect every town for the least total length of line; trying every network is out of the question",
         f"Each town joins its nearest neighbour, then each piece the nearest piece: {' → '.join(map(str, b['pieces']))}", "Borůvka, 1926"),
        ("Is a run of greedy choices really the cheapest?",
         "Proof: the shortest line out of any group belongs to the cheapest network", "Borůvka; Jarník"),
        ("Rounds must track every piece at once",
         f"Grow one network from one town, always by its shortest line out: {s['jar']:,} comparisons", "Jarník, 1930"),
        ("Equal distances can make a round close a loop",
         "Break every tie by one shared rule", "the program's rule: length, then town numbers"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from nearest neighbours to a proved method")
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
    b, s, rd, br = d["bor"], d["same"], d["rounds"], d["brute"]
    js = NW_JS_TEMPLATE.replace("__TOWNS__", json.dumps([list(p) for p in d["towns"]])).replace(
        "__LINES__", json.dumps([f"{i}-{j}" for i, j in s["lines"]]))
    n = len(d["towns"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Euler had shown how to keep only the connections in a problem about places (Era 3, topic 7); joining each point to its nearest neighbour is the most obvious greedy move there is. Borůvka's contribution, asked for by a friend at the West-Moravian power company, was to repeat that move on pieces instead of points, and to prove that the result is the cheapest network possible. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Borůvka (1926) and Jarník (1930). Blue: where the cheapest network is used today."),
        ]),
        dict(id="build", eyebrow="Try it", title="Wire forty towns", toc="Try it", blocks=[
            dict(type="p", text=f"Forty towns, at the random points the program used. Press Borůvka's button to run one round: every piece (at first, every town) takes its shortest line to another piece. Or start again and press Jarník's button to grow a single network from town 0, one line at a time. Either way you end with the same {s['n']} lines, the ones the program found by three methods."),
            dict(type="widget", html=NW_HTML, js=js, css=NW_CSS,
                 fallback=dict(type="svg", name="network", draw=network_svg(d), alt="The cheapest network on forty towns, coloured by Borůvka's rounds", width=860),
                 note="In the interactive edition you can run Borůvka's rounds or Jarník's growth one step at a time."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="The shortest line out of any group", toc="How it works", blocks=[
            dict(type="p", text="**The one fact.** Split the towns into two groups in any way. The shortest line that joins the groups belongs to the cheapest network (if no two distances are equal). For suppose a cheapest network did without it: adding it closes a loop, the loop must cross between the groups a second time by a longer line, and swapping the longer line for the shorter one gives a cheaper network, which is impossible."),
            dict(type="p", text=f"**Borůvka (1926).** Treat every town as a piece. In each round, every piece picks the shortest line from itself to any other piece, and all picked lines are added at once. Every piece joins at least one other, so the number of pieces at least halves each round. On the program's forty towns: {' → '.join(map(str, b['pieces']))} pieces in {b['rounds']} rounds (Borůvka's own forty cities went 40 → 13 → 4 → 1)."),
            dict(type="p", text=f"**Jarník (1930).** Start from one town. Repeatedly add the shortest line from the network built so far to a town not yet in it. After {n - 1} additions every town is in. **Kruskal (1956)** sorts all {s['sorted']} lines and keeps each one that joins two separate pieces. All three methods are the one fact applied in different orders, and the program checks that they choose exactly the same {s['n']} lines, total length {s['length']}."),
            dict(type="p", text=f"**Brute force agrees.** On {br['sets']} sets of {br['n']} towns, the program lists every one of the {br['each']:,} possible networks ({br['total']:,} in all; Cayley's count {br['n']}^{br['n'] - 2}) and finds that the algorithms' network is the unique cheapest every time. It also tests the one fact directly on {d['cut']:,} random splits of the forty towns."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A greedy choice is usually a gamble. Here it is safe, because of a fact you can check: the cheapest line out of any group is always part of a cheapest network. With equal distances, every choice must break ties by the same rule, or Borůvka's simultaneous picks can close a loop."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Three orders, one network", toc="Measured", blocks=[
            dict(type="table", head=["Method", "Work on 40 towns", "Result"], num=[],
                 rows=[["Borůvka, 1926", f"{b['rounds']} rounds, {b['cmp']:,} comparisons of a line", f"{s['n']} lines, length {s['length']}"],
                       ["Jarník, 1930", f"{s['jar']:,} comparisons", "the same lines"],
                       ["Kruskal, 1956", f"sort {s['sorted']} lines, then examine {s['kru']}", "the same lines"]]),
            dict(type="table", head=["Rounds Borůvka needed", f"Sets of 40 random towns (of {rd['sets']:,})"], num=[0, 1],
                 rows=[[str(r), f"{k:,}"] for r, k in rd["hist"]]),
            dict(type="p", text="Since each round at least halves the pieces, 40 towns can never need more than 5 rounds (40 → 20 → 10 → 5 → 2 → 1); in practice pieces merge faster, because several towns often pick the same nearest neighbour."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A friend at the power company", toc="The evidence", blocks=[
            dict(type="p", text="The problem \"was communicated to him by a friend Jindrich Saxel - an employee of Zapadomoravske elektrarny\", during the electrification of southern Moravia; Borůvka's two papers of 1926 appeared in *Práce moravské přírodovědecké společnosti* and *Elektrotechnický obzor*, the second \"by means of a geometric example with 40 cities\" (Nešetřil, Milková and Nešetřilová). Jarník's paper of 1930 is a letter to Borůvka: \"In your article ... you solved an interesting problem\" (Korte and Nešetřil)."),
            dict(type="p", text="Kruskal's sort (1956) and Prim's growth (1957, the method Jarník had published) made the problem famous; Choquet (1938), Florek and colleagues (1951) and Sollin found Borůvka's method again. Sollin's date is **disputed** in the opened sources: 1961 (Graham and Hell) or 1965 (Wikipedia)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Still the first network you build", toc="Full circle", blocks=[
            dict(type="p", text="The cheapest connecting network is still the first step in designing cable and pipe networks, and Kruskal's 1956 paper already tied it to the travelling salesman problem, where a cheapest network gives a lower bound for the length of any tour. Borůvka's rounds, which work on every piece at once, suit machines that do many things in parallel."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Borůvka's own forty cities needed three rounds; so did {next(k for r, k in rd['hist'] if r == 3):,} of the program's {rd['sets']:,} random sets of forty towns."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Four towns sit at the corners of a 3 by 4 rectangle. Which lines does the cheapest network use?", "Three sides: two of length 3 and one of length 4, total 10. The diagonals (length 5) are never needed."),
            ("Why must every Borůvka round at least halve the number of pieces?", "Every piece joins at least one other piece, so the pieces pair up or merge in larger groups: no piece survives alone."),
            ("How many lines does the cheapest network on n towns have?", "n − 1: it connects everything without a loop, so it is a tree."),
            ("Why do equal distances cause trouble for Borůvka but not for Jarník?", "Borůvka's pieces choose at the same time, so three towns at equal distances can each pick a different line and close a loop. Jarník adds one line at a time, always to a new town."),
            ("Is the cheapest network the same as the shortest round trip through all towns?", "No. The round trip must visit the towns in a single loop; the cheapest network may branch. But the network is never longer than the round trip minus one line."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Borůvka's two papers of 1926, in English", text="Both papers translated, with the 40-city example, by Nešetřil, Milková and Nešetřilová.",
                 draw=C.draw_manuscript, link="https://www.dml.cz/bitstream/handle/10338.dmlcz/500413/Boruvka_03-0000-60_1.pdf", link_text="Czech Digital Mathematics Library",
                 licence="Drawn placeholder."),
            dict(title="Jarník's letter of 1930", text="In Czech and in English, with Korte and Nešetřil's commentary.",
                 draw=C.draw_manuscript, link="https://www.dml.cz/bitstream/handle/10338.dmlcz/500662/Jarnik_04-0000-19_1.pdf", link_text="Czech Digital Mathematics Library",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "CheapestNetwork", d["checks"],
                           f"the three methods against each other on forty towns and on {rd['sets']:,} more sets, every round halving the pieces, brute force over all {br['each']:,} networks on {br['n']} towns {br['sets']} times, the cut rule on {d['cut']:,} random splits, and the tie that closes a loop.",
                           ["static TreeSet<Long> boruvka(", "static TreeSet<Long> jarnik("]),
    ]
    return dict(
        title="The Cheapest Network", date="1926–1930",
        description="Era 4, topic 4 of The Algorithm Evolution Atlas: Borůvka's and Jarník's methods for connecting towns with the least total length of line, the minimum spanning tree.",
        lede="Southern Moravia was being wired for electricity. How do you connect every town with the least total length of line? Borůvka's answer, and Jarník's a few years later, are greedy, simple, and provably the best.",
        fieldnote=f"Every town reaches for its nearest neighbour. That leaves pieces; every piece reaches for the nearest piece. On my forty towns, {' pieces, then '.join(map(str, b['pieces'][1:-1]))} pieces, then one network. I have seen few algorithms so obviously right that also needed a proof.",
        card=[("When", "Borůvka 1926; Jarník 1930"),
              ("Where", "Brno and Prague"),
              ("What hurt", "Connecting many towns with the least line"),
              ("The fix", "Greedy choices that are provably optimal"),
              ("Cost", f"{b['rounds']} rounds for 40 towns; at most log₂ n rounds")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `CheapestNetwork.java`.",
    )
