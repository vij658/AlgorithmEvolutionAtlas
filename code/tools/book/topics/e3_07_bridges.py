"""Era 3, topic 7: the bridges of Königsberg. Every number is parsed from KonigsbergBridges.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"city: .*? ; bridges at A (\d+), B (\d+), C (\d+), D (\d+) ; total (\d+) = .*? ; pieces with an odd number of bridges: (\d+)$", ln):
            d["city"] = dict(A=m.group(1), B=m.group(2), C=m.group(3), D=m.group(4), total=m.group(5), odd=m.group(6))
        elif m := re.match(r"euler: a route over (\d+) bridges is a string of (\d+) letters ; .*?: (.+?) ; that is (\d+) letters", ln):
            d["eu"] = dict(bridges=m.group(1), letters=m.group(2), apps=m.group(3), need=m.group(4))
        elif m := re.match(r"search: .*?: ([\d,]+) walks examined ; the longest crosses (\d+) of the (\d+) bridges$", ln):
            d["search"] = dict(walks=m.group(1), longest=m.group(2), total=m.group(3))
        elif m := re.match(r"eighth: .*? bridges at A (\d+), B (\d+), C (\d+), D (\d+) ; .*? finds ([A-D]+), crossing all (\d+) bridges$", ln):
            d["eighth"] = dict(A=m.group(1), B=m.group(2), C=m.group(3), D=m.group(4), route=m.group(5), n=m.group(6))
        elif m := re.match(r"random: ([\d,]+) random multigraphs .*? finds a full route in ([\d,]+), .*? none of the other ([\d,]+) has one ; work: search examined ([\d,]+) walks in all, Hierholzer took ([\d,]+) steps$", ln):
            d["rnd"] = dict(n=m.group(1), yes=m.group(2), no=m.group(3), search=m.group(4), hier=m.group(5))
        elif m := re.match(r"large: a connected graph with (\d+) pieces of land and ([\d,]+) bridges, .*? in ([\d,]+) steps$", ln):
            d["large"] = dict(n=m.group(1), m=m.group(2), steps=m.group(3))
        elif m := re.match(r"circle: .*? spells (\d+) \((\d+) digits\), .*? would take (\d+) digits$", ln):
            d["db"] = dict(seq=m.group(1), len=m.group(2), naive=m.group(3))
    d["checks"] = C.checks(text)
    return d


# the layout used by both the static figure and the widget: A the island in the middle, B north bank, C south bank, D east
POS = {"A": (330, 160), "B": (330, 40), "C": (330, 280), "D": (610, 160)}
BRIDGES = [("A", "B", -40), ("A", "B", 40), ("A", "C", -40), ("A", "C", 40), ("A", "D", 0), ("B", "D", 0), ("C", "D", 0)]


def city_svg(d):
    """The four pieces of land as dots and the seven bridges as lines (the later graph form, not Euler's own drawing)."""
    c = d["city"]

    def draw(t, standalone):
        out = []
        for i, (u, v, bend) in enumerate(BRIDGES):
            (x1, y1), (x2, y2) = POS[u], POS[v]
            L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 or 1
            mx, my = (x1 + x2) / 2 - bend * (y2 - y1) / L, (y1 + y2) / 2 + bend * (x2 - x1) / L
            out.append(C.path(f"M{x1} {y1} Q{mx} {my} {x2} {y2}", t["blue"], "none", 3))
            out.append(C.text((x1 + 2 * mx + x2) / 4 + (8 if mx >= (x1 + x2) / 2 else -8), (y1 + 2 * my + y2) / 4 - 4, "abcdefg"[i], t["muted"], 12, "start" if mx >= (x1 + x2) / 2 else "end"))
        for k, (x, y) in POS.items():
            out.append(f'<circle cx="{x}" cy="{y}" r="22" style="fill:{t["surface"]};stroke:{t["red"]};stroke-width:2.5"/>')
            out.append(C.text(x, y + 6, k, t["ink"], 17, "middle", 700))
            out.append(C.text(x + 32, y + (30 if k == "C" else -14), f"{c[k]} bridges", t["red"], 12.5, "start", 700))
        out.append(C.text(20, 330, "A: the island (Kneiphof). B, C: the two banks. D: the land between the two branches of the river.", t["muted"], 12.5))
        out.append(C.text(20, 348, f"Every piece of land has an odd number of bridges ({c['odd']} odd pieces), so no walk crosses each bridge exactly once.", t["muted"], 12.5))
        return C.svg_doc(780, 362, "".join(out), "Königsberg as four pieces of land joined by seven bridges", t, standalone, 0.55, 780)
    return draw


KB_HTML = """
<div class="board kb-board">
  <div style="min-width:0">
    <svg id="kb-svg" viewBox="0 0 700 330" role="img" aria-label="Four pieces of land and their bridges; click a bridge to cross it"></svg>
    <div class="controls">
      <label for="kb-extra">Extra bridge <select id="kb-extra">
        <option value="" selected>none (Königsberg)</option><option value="BC">B to C</option><option value="BD">B to D</option><option value="AD">A to D</option><option value="BC2">B to C and A to D</option>
      </select></label>
      <button type="button" id="kb-reset">Start again</button>
      <button type="button" id="kb-solve">Show a route</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Euler's test</div>
    <div class="kb-deg" id="kb-deg"></div>
    <div class="eyebrow">Your walk</div>
    <p class="kb-walk" id="kb-walk"></p>
    <p class="say" id="kb-say" aria-live="polite"></p>
  </div>
</div>
"""

KB_CSS = """
.kb-board svg{max-width:520px;display:block;margin:0 auto}
.kb-board svg path,.kb-board svg circle{cursor:pointer}
.kb-board .controls{flex-wrap:wrap}
.kb-deg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin:6px 0 12px}
.kb-deg div{border:1px solid var(--axis);padding:6px;text-align:center;font-family:var(--mono);font-size:13px;background:var(--surface)}
.kb-deg div.odd{border-color:var(--red);color:var(--red);font-weight:700}
.kb-walk{font-family:var(--mono);font-size:15px;letter-spacing:.08em;overflow-wrap:anywhere;min-height:1.5em}
.kb-board .say{font-size:14.5px}
"""

KB_JS = r"""
(() => {
  const svg = document.getElementById("kb-svg");
  if (!svg) return;
  const POS = __POS__, BASE = __BRIDGES__;
  const EXTRA = { "": [], BC: [["B", "C", 150]], BD: [["B", "D", 40]], AD: [["A", "D", 40]], BC2: [["B", "C", 150], ["A", "D", 40]] };
  let bridges = [], used = [], walk = [], at = null;
  function setup() {
    bridges = BASE.concat(EXTRA[document.getElementById("kb-extra").value]);
    used = bridges.map(() => false); walk = []; at = null; draw();
  }
  const deg = () => { const d = { A: 0, B: 0, C: 0, D: 0 }; bridges.forEach(([u, v]) => { d[u]++; d[v]++; }); return d; };
  function draw() {
    svg.innerHTML = "";
    bridges.forEach(([u, v, bend], i) => {
      const [x1, y1] = POS[u], [x2, y2] = POS[v];
      const L = Math.hypot(x2 - x1, y2 - y1) || 1, mx = (x1 + x2) / 2 - bend * (y2 - y1) / L, my = (y1 + y2) / 2 + bend * (x2 - x1) / L;
      const p = sv("path", { d: `M${x1} ${y1} Q${mx} ${my} ${x2} ${y2}`, fill: "none", stroke: used[i] ? "var(--muted)" : "var(--blue)", "stroke-width": used[i] ? 3 : 6, "stroke-dasharray": used[i] ? "4 5" : "" }, svg);
      p.addEventListener("click", () => cross(i));
    });
    Object.entries(POS).forEach(([k, [x, y]]) => {
      const g = sv("circle", { cx: x, cy: y, r: 24, fill: k === at ? "var(--red)" : "var(--surface)", stroke: "var(--red)", "stroke-width": 2.5 }, svg);
      g.addEventListener("click", () => { if (!walk.length) { at = k; walk = [k]; draw(); } });
      sv("text", { x, y: y + 6, "text-anchor": "middle", "font-size": 18, "font-weight": 700, fill: k === at ? "var(--on-red)" : "var(--ink)", "pointer-events": "none" }, svg, k);
    });
    const d = deg(), host = document.getElementById("kb-deg"); host.innerHTML = "";
    let odd = 0;
    Object.entries(d).forEach(([k, v]) => { if (v % 2) odd++; el("div", { class: v % 2 ? "odd" : "" }, host, `${k}: ${v}`); });
    document.getElementById("kb-walk").textContent = walk.length ? walk.join(" → ") : "Click a piece of land to start, then click bridges.";
    const n = used.filter(Boolean).length, say = document.getElementById("kb-say");
    if (n === bridges.length) say.textContent = `Every bridge crossed exactly once! ${odd === 2 ? "It had to start and end at the two odd pieces." : "With no odd pieces, the walk ends where it began."}`;
    else if (walk.length && !bridges.some(([u, v], i) => !used[i] && (u === at || v === at))) say.textContent = `Stuck at ${at} with ${bridges.length - n} bridge${bridges.length - n === 1 ? "" : "s"} uncrossed.` + (odd > 2 ? ` Euler: with ${odd} odd pieces, no walk can work.` : " Try again: start at an odd piece.");
    else say.textContent = odd > 2 ? `${odd} pieces have an odd number of bridges: Euler says no walk can cross every bridge once.` : odd === 2 ? "Exactly two odd pieces: a walk exists, starting at one and ending at the other." : "No odd pieces: a closed walk exists from anywhere.";
  }
  function cross(i) {
    const [u, v] = bridges[i];
    if (used[i] || !at || (u !== at && v !== at)) return;
    used[i] = true; at = u === at ? v : u; walk.push(at); draw();
  }
  function solve() {
    const d = deg(), odd = Object.keys(d).filter(k => d[k] % 2);
    if (odd.length !== 0 && odd.length !== 2) { document.getElementById("kb-say").textContent = `No route: ${odd.length} odd pieces.`; return; }
    const start = odd.length ? odd[0] : "A";
    const usedE = bridges.map(() => false), stack = [start], route = [];
    while (stack.length) {
      const v = stack[stack.length - 1];
      const i = bridges.findIndex(([a, b], j) => !usedE[j] && (a === v || b === v));
      if (i < 0) route.unshift(stack.pop());
      else { usedE[i] = true; const [a, b] = bridges[i]; stack.push(a === v ? b : a); }
    }
    used = bridges.map(() => true); walk = route; at = route[route.length - 1]; draw();
  }
  document.getElementById("kb-extra").addEventListener("change", setup);
  document.getElementById("kb-reset").addEventListener("click", setup);
  document.getElementById("kb-solve").addEventListener("click", solve);
  setup();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Euler's bridges combined older ideas, and where they went")
    W, H = 210, 86
    nodes = {
        "cnt": (20, 20, "Counting", "pair things off; odd and even", "Era 1 topic 1", "ink"),
        "sit": (395, 20, "Geometry of position", "Leibniz's geometria situs", "a name without a theory", "ink"),
        "puz": (770, 20, "A citizens' puzzle", "seven bridges, one walk?", "Königsberg", "ink"),
        "eul": (395, 170, "Euler's solution", "⊕ keep only what joins what, and count", "1735–1736", "red"),
        "hie": (20, 330, "Hierholzer", "build the walk by splicing loops", "1873", "ink"),
        "rb": (395, 330, "The graph drawing", "dots and lines", "Rouse Ball, 1892", "ink"),
        "net": (770, 330, "Networks and routes", "graph algorithms", "Eras 4–5", "blue"),
        "db": (395, 480, "de Bruijn sequences", "every code once, by an Euler route", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("cnt", "eul", ports=("bottom", "top:0.15"))
    D.edge("sit", "eul", ports=("bottom", "top"))
    D.edge("puz", "eul", ports=("bottom", "top:0.85"))
    D.edge("eul", "hie", ports=("bottom:0.1", "top:0.7"))
    D.edge("eul", "rb", ports=("bottom", "top"))
    D.edge("eul", "net", ports=("bottom:0.9", "top:0.3"))
    D.edge("hie", "db", ports=("bottom", "top:0.2"))
    D.text(20, 615, "Euler drew no graph: the picture of dots and lines first appeared in Rouse Ball's book of 1892 (Hopkins and Wilson).", "caption")
    return D


def chain(d):
    s, r = d["search"], d["rnd"]
    steps = [
        ("Trying every walk: too many cases, and no branch of mathematics for it",
         "Keep only which land each bridge joins, and count bridges per piece", "Euler, 1736"),
        ("Euler showed when a walk is impossible, but not how to find one when it is possible",
         "Walk until stuck, then splice in closed loops", "Hierholzer, 1873"),
        (f"Exhaustive search grows explosively: {r['search']} walks for 20,000 small cases",
         f"Splicing visits each bridge once: {r['hier']} steps in all", "linear time"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a puzzle to a linear-time algorithm")
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
    c, eu, s, e8, r, lg, db = d["city"], d["eu"], d["search"], d["eighth"], d["rnd"], d["large"], d["db"]
    import json
    js = KB_JS.replace("__POS__", json.dumps({k: [v[0] + 20, v[1] + 5] for k, v in POS.items()})).replace("__BRIDGES__", json.dumps([list(b) for b in BRIDGES]))
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Counting in pairs, odd and even, is as old as tally marks (Era 1, topic 1). Leibniz had asked for a \"geometry of position\" that would deal with arrangement rather than size, but no one had written one. The citizens of Königsberg supplied the question. Euler answered it by throwing away everything except which land each bridge joins, and counting. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Euler's solution. Blue: where routes through networks went."),
        ]),
        dict(id="walk", eyebrow="Try it", title="Cross every bridge once", toc="Try it", blocks=[
            dict(type="p", text="Click a piece of land to start, then click bridges to cross them. Euler's test, on the right, counts the bridges at each piece; odd counts are red. Choose \"none\" for Königsberg itself and try to cross all seven. Then add an eighth bridge and try again, or let the page find a route by Hierholzer's splicing."),
            dict(type="widget", html=KB_HTML, js=js, css=KB_CSS,
                 fallback=dict(type="svg", name="city", draw=city_svg(d), alt="Königsberg as four pieces of land and seven bridges", width=780),
                 note="In the interactive edition you can walk the bridges yourself, add extra bridges, and ask for a route."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Count the bridges, not the walks", toc="How it works", blocks=[
            dict(type="p", text=f"**The city, reduced.** Four pieces of land: the island A and the regions B, C and D, joined by seven bridges. A has {c['A']} bridges; B, C and D have {c['B']}, {c['C']} and {c['D']}. Their total, {c['total']}, is twice the number of bridges, because \"each bridge is counted twice, once for each of the two areas which it joins\" (Euler, in Hopkins and Wilson's translation)."),
            dict(type="svg", name="city-steps", draw=city_svg(d), alt="Königsberg as four pieces of land and seven bridges", width=780),
            dict(type="p", text=f"**Euler's count.** A route over {eu['bridges']} bridges can be written as a string of {eu['letters']} letters, the pieces of land in the order visited. A piece with an odd number k of bridges must appear (k + 1)/2 times: {eu['apps']}. That is {eu['need']} letters, more than {eu['letters']}: no route exists. Euler's general rule: \"If there are more than two areas to which an odd number of bridges lead, then such a journey is impossible.\""),
            dict(type="p", text=f"**Checking by brute force.** The program tried every walk that never repeats a bridge, from every piece of land: {s['walks']} walks, the longest crossing {s['longest']} of the {s['total']} bridges."),
            dict(type="p", text=f"**Hierholzer's construction (1873).** Euler's condition is also enough. Walk until you are stuck, which can only happen at the end; then, from any place on the walk that still has unused bridges, walk a closed loop and splice it into the route. With an eighth bridge from B to C, the counts become {e8['A']}, {e8['B']}, {e8['C']} and {e8['D']}: two odd pieces. The program's route: **{' → '.join(e8['route'])}**, all {e8['n']} bridges."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Decide what to ignore. Distances, shapes and the river itself do not matter; only which land touches which bridge. Once the problem is a list of connections, a parity count settles it, and a simple procedure builds the answer."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Counting against searching", toc="Measured", blocks=[
            dict(type="table", head=["Test", "Result"], num=[],
                 rows=[[f"{r['n']} random small networks (3–6 pieces, 4–10 bridges)", f"a full route exists in {r['yes']}: exactly those where the land is connected and 0 or 2 pieces are odd; in the other {r['no']}, none"],
                       ["Work, exhaustive search", f"{r['search']} walks examined"],
                       ["Work, Hierholzer's splicing", f"{r['hier']} steps"],
                       [f"A network of {lg['n']} pieces and {lg['m']} bridges", f"Hierholzer: a closed route in {lg['steps']} steps"]]),
            dict(type="p", text="Euler's count needs one look at each bridge; Hierholzer's splicing needs about two steps per bridge. Exhaustive search grows explosively with the number of bridges. On every one of the random cases, Euler's rule agreed with the search."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A banal question, and a paper dated 1736", toc="The evidence", blocks=[
            dict(type="p", text="Euler presented his solution to the St Petersburg Academy on 26 August 1735; the paper is dated 1736 (*Commentarii* 8, pp. 128–140) but \"was not actually published until 1741\" (Hopkins and Wilson; Sachs, Stiebitz and Wilson). To Marinoni, on 13 March 1736, he called the question \"so banal\" but \"worthy of attention\"; to Ehler he wrote that \"the solution is based on reason alone\". Euler stated, but did not prove, that his condition is sufficient; \"A valid proof was not published until 1873, by Carl Hierholzer\" (*Mathematische Annalen* 6). That the paper appeared after Hierholzer's death is often said but was not found in an opened source (**conjecture**)."),
            dict(type="p", text="Euler drew no graph: \"graphs of this kind didn't make their first appearance until the second half of the nineteenth century\", and the dots-and-lines Königsberg graph first appeared in W. W. Rouse Ball's book of 1892 (Hopkins and Wilson). The figure on this page is that later form. Today two of the seven bridges are gone, lost to bombing in the Second World War, two were replaced by a highway, and three remain (Wikipedia)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Every code exactly once", toc="Full circle", blocks=[
            dict(type="p", text="Turn codes into bridges: let each three-digit binary string be a piece of land, and each four-digit string xyzw a one-way bridge from xyz to yzw. Every piece then has two bridges in and two out, so an Euler route exists."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program's route spells {db['seq']}: {db['len']} digits in which every one of the 16 four-digit codes appears exactly once, against {db['naive']} digits to type them one by one. Such de Bruijn sequences come straight out of Euler's bridges, and Hierholzer's splicing builds them in time proportional to their length."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why must the bridges at a piece of land pair up?", "Every time the walker enters by one bridge, they leave by another, except at the start and the end."),
            ("Why can there never be exactly one odd piece?", "The bridge counts add up to twice the number of bridges, an even number, so the odd counts come in pairs."),
            ("Why does A, with 5 bridges, appear 3 times in a route?", "Each visit in the middle uses 2 bridges; 5 bridges need at least 3 appearances (2 + 2 + 1, the last as start or end)."),
            ("With two odd pieces, where must a route start?", "At one odd piece, ending at the other."),
            ("Why is Hierholzer's splicing fast?", "Each bridge is crossed once when walking and looked at once when backing up: the work is proportional to the number of bridges."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Solutio problematis ad geometriam situs pertinentis", text="Euler's paper of 1736 (printed 1741), in Latin, from the Euler Archive.",
                 draw=C.draw_manuscript, link="https://phantom.cs.qc.cuny.edu/gavva/teaching/s24/euler-bridges-paper.pdf", link_text="PDF",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "KonigsbergBridges", d["checks"],
                           "Euler's count on Königsberg, an exhaustive search of every walk, Hierholzer's route with an eighth bridge, Euler's condition against search on 20,000 random networks, a closed route over 2,000 bridges, and a de Bruijn sequence built as an Euler route.",
                           ["static List<Integer> hierholzer("]),
    ]
    return dict(
        title="The Bridges of Königsberg", date="1736",
        description="Era 3, topic 7 of The Algorithm Evolution Atlas: Euler's solution to the Königsberg bridge problem, Hierholzer's construction of the walk, and Euler routes today.",
        lede="Seven bridges joined the islands and banks of a Prussian city, and its citizens asked whether a walk could cross each one exactly once. Euler answered without trying a single walk: he counted bridges.",
        fieldnote="Listing every walk was hopeless. Euler threw away the river, the distances and the shapes, kept only which land touched which bridge, and counted. He called the question banal. It is the first time I have seen a problem solved by deciding what to ignore.",
        card=[("When", "Presented 1735; dated 1736; printed 1741; Hierholzer 1873"),
              ("Where", "St Petersburg, about Königsberg"),
              ("What hurt", "A route question with too many cases to try"),
              ("The fix", "Keep only the connections, and count: zero or two odd places"),
              ("Cost", "One look at each bridge")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `KonigsbergBridges.java`.",
    )
