"""Era 1, topic 1: tally marks. Every number on the page is parsed from the output of TallyMarks.java."""
import random
import re

import common as C
import diagrams
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"match": [], "read": [], "ishango": {}, "pattern": {}}
    for ln in text.splitlines():
        if m := re.match(r"match (\d+) (\d+): pairs=(\d+) winner=(\w+) by=(\d+) counting-needs=(\d+)$", ln):
            d["match"].append(dict(a=int(m.group(1)), b=int(m.group(2)), pairs=int(m.group(3)), winner=m.group(4),
                                   by=int(m.group(5)), counting=int(m.group(6))))
        elif m := re.match(r"matchcheck: (\d+) random pairs", ln):
            d["matchcheck"] = int(m.group(1))
        elif m := re.match(r"read (\d+): one-by-one=(\d+) by-fives=(\d+)$", ln):
            d["read"].append(tuple(int(m.group(i)) for i in (1, 2, 3)))
        elif m := re.match(r"ishango ([GMD]): ([\d ]+) total=(\d+) all-prime=(\w+) near-ten=(\w+) doubling-pairs=(\d+)$", ln):
            d["ishango"][m.group(1)] = dict(groups=[int(x) for x in m.group(2).split()], total=int(m.group(3)),
                                            prime=m.group(4) == "true", near=m.group(5) == "true", dbl=int(m.group(6)))
        elif m := re.match(r"ishango total: (\d+) notches", ln):
            d["notches"] = int(m.group(1))
        elif m := re.match(r"regroup M: ([\d ]+) total=(\d+) doubling-pairs=(\d+) \(was (\d+)\)$", ln):
            d["regroup"] = dict(groups=[int(x) for x in m.group(1).split()], total=int(m.group(2)), dbl=int(m.group(3)), was=int(m.group(4)))
        elif m := re.match(r"model: group sizes equally likely from (\d+) to (\d+)", ln):
            d["lo"], d["hi"] = int(m.group(1)), int(m.group(2))
        elif m := re.match(r"pattern ([\w-]+): (\d+) of (\d+)", ln):
            d["pattern"][m.group(1)] = (int(m.group(2)), int(m.group(3)))
        elif m := re.match(r"combination: probability ([\d.e+-]+), about 1 in ([\d,]+) random bones", ln):
            d["one_in"] = int(m.group(2).replace(",", ""))
        elif m := re.match(r"any-pattern: .* ([\d.]+)% of the time, the eight-group column ([\d.]+)%; a random bone shows at least one somewhere ([\d.]+)%", ln):
            d["any4"], d["any8"], d["any"] = float(m.group(1)), float(m.group(2)), float(m.group(3))
        elif m := re.match(r"split: (\d+) honest stick pairs matched, (\d+) of (\d+) forged", ln):
            d["split"] = dict(honest=int(m.group(1)), caught=int(m.group(2)), n=int(m.group(3)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
# the Ishango bone, drawn notch by notch, with one layer per reading
# ----------------------------------------------------------------------------------------------------------------------
# Column M as notches: the UNESCO listing writes the fifth group as 10 (9+1) and the sixth as 5 (1+4).
M_SUBGROUPS = {4: (9, 1), 5: (1, 4)}
READINGS = {
    "marks": [],
    "count": ["numG", "numM", "numD"],
    "primes": ["numG", "boxG"],
    "tens": ["numD", "boxD"],
    "doubling": ["numM", "dbl"],
    "totals": ["numG", "numM", "numD", "totals"],
    "regroup": ["numMsplit", "dblSplit"],
}


def bone_layout(d):
    """Notch positions: for each column, a list of groups; each group a list of sub-groups; each a list of x values."""
    S, GAP, SUB, X0 = 10, 22, 16, 96
    cols = {}
    for key in "GMD":
        x, groups = X0, []
        for gi, n in enumerate(d["ishango"][key]["groups"]):
            parts = M_SUBGROUPS.get(gi, (n,)) if key == "M" else (n,)
            subs = []
            for pi, k in enumerate(parts):
                subs.append([x + j * S for j in range(k)])
                x = subs[-1][-1] + (SUB if pi + 1 < len(parts) else GAP)
            groups.append(subs)
        cols[key] = groups
    return cols


def bone_svg(d, layers_on=None):
    """The three columns of the Ishango bone as three strips. layers_on=None: every reading layer is drawn, all hidden
    but 'count' (the interactive edition switches them); otherwise only the named layers are drawn (GitHub edition)."""
    cols = bone_layout(d)
    rows = {"G": 78, "M": 186, "D": 294}
    W, H = 900, 350

    def draw(t, standalone):
        rnd = random.Random(20000)
        out = [C.text(20, 22, "The Ishango bone's three columns of notches, unrolled", t["muted"], 12, weight=600)]
        layers = {k: [] for k in ["numG", "numM", "numD", "numMsplit", "boxG", "boxD", "dbl", "dblSplit", "totals"]}
        for key, yc in rows.items():
            groups = cols[key]
            xs = [x for g in groups for s in g for x in s]
            out.append(C.rect(80, yc - 28, xs[-1] - 80 + 18, 56, t["wash"], t["axis"], 1.2, rx=26))
            out.append(C.text(44, yc + 6, key, t["ink"], 18, "middle", 700))
            for x in xs:
                tilt = rnd.uniform(-2.5, 2.5)
                top, bot = yc - 17 + rnd.uniform(-3, 2), yc + 17 + rnd.uniform(-2, 3)
                out.append(C.line(x, top, x + tilt, bot, t["ink"], 2.2))
            for gi, g in enumerate(groups):
                gx0, gx1 = g[0][0], g[-1][-1]
                n = sum(len(s) for s in g)
                layers["num" + key].append(C.text((gx0 + gx1) / 2, yc - 34, n, t["ink"], 13, "middle", 700))
                if key == "G":
                    layers["boxG"].append(C.rect(gx0 - 5, yc - 23, gx1 - gx0 + 10, 46, "none", t["red"], 2.5))
                if key == "D":
                    layers["boxD"].append(C.rect(gx0 - 5, yc - 23, gx1 - gx0 + 10, 46, "none", t["blue"], 2.5))
                if key == "M":
                    for s in g:
                        layers["numMsplit"].append(C.text((s[0] + s[-1]) / 2, yc - 34, len(s), t["ink"], 13, "middle", 700))
            layers["totals"].append(C.text(W - 24, yc + 7, d["ishango"][key]["total"], t["red"], 22, "end", 700))

        def brackets(groups, layer, color):
            """A bracket under each neighbouring pair where one group is twice the other."""
            for i in range(len(groups) - 1):
                a, b = groups[i], groups[i + 1]
                if a[1] == 2 * b[1] or b[1] == 2 * a[1]:
                    y = rows["M"] + 32
                    path = f"M{a[0]:.1f},{y} v12 H{b[0]:.1f} v-12"
                    layer.append(C.path(path, color, "none", 2.5))
                    layer.append(C.text((a[0] + b[0]) / 2, y + 28, "×2", color, 13, "middle", 700))

        m_groups = cols["M"]
        whole = [(((g[0][0] + g[-1][-1]) / 2), sum(len(s) for s in g)) for g in m_groups]
        split = [(((s[0] + s[-1]) / 2), len(s)) for g in m_groups for s in g]
        brackets(whole, layers["dbl"], t["yellow"])
        brackets(split, layers["dblSplit"], t["yellow"])
        for name, items in layers.items():
            if layers_on is None:
                shown = name in READINGS["count"]
                out.append(f'<g class="rd" data-layer="{name}"{"" if shown else " style=" + chr(34) + "display:none" + chr(34)}>{"".join(items)}</g>')
            elif name in layers_on:
                out.append("".join(items))
        return C.svg_doc(W, H, "".join(out), "The Ishango bone's notch groups: column G 11, 13, 17, 19; column M 3, 6, 4, 8, 10, 5, 5, 7; column D 11, 21, 19, 9",
                         t, standalone, 0.62)
    return draw


BONE_CSS = """
.bone-board{grid-template-columns:1fr}
.bone-board .readings{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.bone-board .readings button{font-weight:400;font-size:13.5px;padding:4px 10px;border-width:1px;border-color:var(--axis)}
.bone-board .readings button[aria-pressed="true"]{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.bone-board svg{background:none}
.bone-board .say{font-size:15px;max-width:var(--col);min-height:3.4em;margin:12px 0 0}
.match-board svg{background:var(--wash)}
.match-board .say{font-size:15px;min-height:4.5em}
.match-board .tally-count{font-family:var(--mono);font-size:13px;color:var(--muted)}
"""

BONE_JS = r"""
(() => {
  const root = document.getElementById("bone");
  if (!root) return;
  const layers = READINGS_JSON;
  const say = SAY_JSON;
  const out = document.getElementById("bone-say");
  function show(r) {
    root.querySelectorAll("g.rd").forEach(g => { g.style.display = layers[r].includes(g.dataset.layer) ? "" : "none"; });
    document.querySelectorAll("#bone-readings button").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.r === r)));
    out.innerHTML = say[r];
  }
  document.querySelectorAll("#bone-readings button").forEach(b => b.addEventListener("click", () => show(b.dataset.r)));
  show("count");
})();
"""

MATCH_HTML = """
<div class="board match-board">
  <div style="min-width:0">
    <div class="controls">
      <button id="m-step" class="primary" type="button">A sheep comes home</button>
      <button id="m-all" type="button">All of them</button>
      <button id="m-new" type="button">Another day</button>
    </div>
    <svg id="m-svg" viewBox="0 0 640 250" role="img" aria-label="Stones in a pouch paired with sheep coming home"></svg>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">What the herder knows</div>
    <p class="say" id="m-say" aria-live="polite"></p>
    <p class="tally-count" id="m-cost"></p>
  </div>
</div>
"""

MATCH_JS = r"""
(() => {
  const svg = document.getElementById("m-svg");
  if (!svg) return;
  let stones = START_A, sheep = START_B, paired = 0, timer = null;
  const say = document.getElementById("m-say"), cost = document.getElementById("m-cost");
  const X = i => 26 + i * 24;
  function draw() {
    svg.innerHTML = "";
    sv("text", {x: 14, y: 22, fill: "var(--muted)", "font-size": 12, "font-weight": 600}, svg, "STONES IN THE POUCH: ONE FOR EACH SHEEP THAT WENT OUT");
    sv("text", {x: 14, y: 236, fill: "var(--muted)", "font-size": 12, "font-weight": 600}, svg, "SHEEP COMING HOME");
    for (let i = 0; i < paired; i++) sv("line", {x1: X(i), y1: 62, x2: X(i), y2: 178, stroke: "var(--axis)", "stroke-width": 1.5}, svg);
    for (let i = 0; i < stones; i++) sv("rect", {x: X(i) - 8, y: 44, width: 16, height: 16, rx: 3,
        fill: i < paired ? "var(--axis)" : "var(--red)"}, svg);
    for (let i = 0; i < sheep; i++) {
      const done = i < paired;
      sv("circle", {cx: X(i), cy: 194, r: 9, fill: done ? "var(--axis)" : (i === paired ? "var(--blue)" : "var(--surface)"),
          stroke: done ? "var(--axis)" : "var(--blue)", "stroke-width": 2}, svg);
    }
    const left = Math.min(stones, sheep) === paired;
    if (!left) {
      say.textContent = paired === 0 ? "Each sheep that comes through the gate takes one stone out of the pouch. Nobody counts."
                                     : `${"A sheep is home, a stone comes out. ".repeat(1)}Still pairing...`;
    } else if (stones > sheep) {
      say.innerHTML = `<b>${stones - sheep} stone${stones - sheep === 1 ? " is" : "s are"} left in the pouch</b>, so ${stones - sheep === 1 ? "a sheep is" : "sheep are"} still out. The herder never needed the word for ${stones}.`;
    } else if (sheep > stones) {
      say.innerHTML = `<b>${sheep - stones} sheep ${sheep - stones === 1 ? "has" : "have"} no stone</b>: more came home than went out. A stray joined the flock.`;
    } else {
      say.innerHTML = "<b>Every stone has a sheep.</b> The whole flock is home, and nobody counted.";
    }
    cost.textContent = `Pairs made: ${paired}. Counting both instead would take ${stones + sheep} counts.`;
  }
  function step() {
    if (paired < Math.min(stones, sheep)) { paired++; draw(); return true; }
    return false;
  }
  document.getElementById("m-step").addEventListener("click", () => { clearInterval(timer); step(); });
  document.getElementById("m-all").addEventListener("click", () => {
    clearInterval(timer);
    if (reduceMotion) { while (step()); return; }
    timer = setInterval(() => { if (!step()) clearInterval(timer); }, 180);
  });
  document.getElementById("m-new").addEventListener("click", () => {
    clearInterval(timer);
    stones = 6 + Math.floor(Math.random() * 19);
    sheep = Math.max(3, stones - Math.floor(Math.random() * 5) + (Math.random() < 0.15 ? 2 : 0));
    sheep = Math.min(sheep, 24);
    paired = 0; draw();
  });
  draw();
})();
"""


def match_fallback(m):
    """Static picture for the GitHub edition: the stones and sheep of the program's first example, fully paired."""
    a, b = m["a"], m["b"]

    def draw(t, standalone):
        X = lambda i: 26 + i * 24
        out = [C.text(14, 22, "STONES IN THE POUCH: ONE FOR EACH SHEEP THAT WENT OUT", t["muted"], 12, weight=600),
               C.text(14, 236, "SHEEP COMING HOME", t["muted"], 12, weight=600)]
        for i in range(min(a, b)):
            out.append(C.line(X(i), 62, X(i), 178, t["axis"], 1.5))
        for i in range(a):
            out.append(C.rect(X(i) - 8, 44, 16, 16, t["axis"] if i < b else t["red"], rx=3))
        for i in range(b):
            out.append(C.circle(X(i), 194, 9, t["axis"], t["axis"], 2))
        out.append(C.text(X(a) + 10, 57, f"{a - b} left over", t["red"], 13, weight=700))
        return C.svg_doc(640, 250, "".join(out), f"{a} stones paired with {b} sheep: {a - b} stones left over", t, standalone, 0.6)
    return draw


# ----------------------------------------------------------------------------------------------------------------------
# diagrams
# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 420, "How tally marks combined with other ideas, from pairing things off to append-only logs")
    W, H = 210, 76
    nodes = {
        "pair": (395, 20, "Pairing things off", "", "one from each pile", "ink"),
        "tally": (395, 165, "Tally marks", "⊕ a mark that lasts", "c. 44,000 years ago", "red"),
        "cantor": (760, 165, "Sizes of infinite sets", "⊕ infinite collections", "Cantor, 1878", "blue"),
        "group": (30, 320, "Grouped numerals", "⊕ bundles of marks", "topic 2, c. 3000 BCE", "ink"),
        "split": (395, 320, "Split tally stick", "⊕ two halves must match", "English Exchequer, to 1826", "blue"),
        "log": (760, 320, "Append-only log", "⊕ replay to rebuild", "databases and data streams", "red"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("pair", "tally", ports=("bottom", "top"))
    D.edge("pair", "cantor", ports=("right", "top"))
    D.edge("tally", "group", ports=("bottom", "top"))
    D.edge("tally", "split", ports=("bottom", "top"))
    D.edge("tally", "log", ports=("bottom", "top"))
    return D


def chain(d, r168):
    steps = [
        ("Is one pile bigger than the other?", "Pair them off, one from each; the pile with things left over is bigger", "before writing"),
        ("The things do not stay put: days pass, animals wander off", "Cut one mark for each, on something that lasts", "notched bones, c. 44,000 years ago"),
        (f"A long row cannot be read at a glance: {r168[0]} marks take {r168[1]} looks", f"Bundle the marks: in fives, {r168[0]} marks take {r168[2]} looks", "topic 2"),
        ("Anyone can cut one more notch", "Notch a stick, then split it: both halves must match", "English Exchequer, until 1826"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from pairing piles to the split tally stick")
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


def readings(d):
    G, M, Dd = (d["ishango"][k]["total"] for k in "GMD")
    D = Diagram(1000, 340, "Four readings of the same notches; none is proven")
    D.node("marks", 330, 20, 340, 84, [("The marks", "title"), (f"{d['notches']} notches in 3 columns: {G}, {M}, {Dd}", "combo"),
                                        ("documented: the holding museum", "note")], color="ink")
    boxes = [("just", 20, "Just a record", "matching, no arithmetic", "Keller, 2010"),
             ("arith", 265, "Arithmetic", "primes, doubling, tens", "de Heinzelin, 1962"),
             ("moon", 510, "A moon calendar", "about 5½ months of phases", "Marshack, 1972"),
             ("twelve", 755, "Counting in twelves", f"{G} and {M} are multiples of 12", "Pletser and Huylebrouck")]
    for k, x, t, combo, who in boxes:
        D.node(k, x, 200, 225, 84, [(t, "title"), (combo, "combo"), (who, "note")], color="blue")
        D.edge("marks", k, ports=("bottom", "top"))
    D.text(500, 318, "FOUR READINGS: EACH A CONJECTURE, TOGETHER DISPUTED", "tag", "middle")
    return D


def surprise(d):
    p = d["pattern"]
    f = lambda k: f"{p[k][0]:,} of {p[k][1]:,} columns"
    D = Diagram(1000, 510, "How surprising are the bone's patterns, if group sizes were random?")
    D.node("model", 250, 20, 500, 76, [("THE ASSUMPTION", "tag"), (f"Every group is equally likely to be any size from {d['lo']} to {d['hi']}", "combo")], color="ink")
    cols = [("g", 20, "Column G: all prime, total a multiple of 12", f("all-prime-and-total-multiple-of-12")),
            ("m", 350, "Column M: 3 doubling pairs, total a multiple of 12", f("three-doublings-and-total-multiple-of-12")),
            ("dd", 680, "Column D: all one from 10 or 20, total a multiple of 12", f("near-ten-and-total-multiple-of-12"))]
    for k, x, t, n in cols:
        D.node(k, x, 170, 300, 96, [(t, "combo"), (n, "note")], color="ink")
        D.edge("model", k, ports=("bottom", "top"))
    D.node("all", 140, 360, 320, 96, [("ALL THREE AT ONCE, AS ON THE BONE", "tag"), (f"about 1 in {d['one_in']:,} random bones", "title")], color="red")
    D.node("any", 540, 360, 320, 96, [("AT LEAST ONE PATTERN SOMEWHERE", "tag"), (f"{d['any']}% of random bones", "title")], color="blue")
    for k in ("g", "m", "dd"):
        D.edge(k, "all", ports=("bottom", "top"))
    for k in ("g", "m", "dd"):
        D.edge(k, "any", ports=("bottom", "top"), dashed=True)
    D.text(500, 488, "SOLID: ALL THREE MUST HOLD · DASHED: ANY ONE OF THE PATTERNS IS ENOUGH", "tag", "middle")
    return D


def circle():
    rows = [("Cut a notch for each sheep", "Append a record for each event"),
            ("Count the notches to know how many", "Replay the log to rebuild the state"),
            ("Lay stock and foil side by side", "Compare the copies two parties keep")]
    bh, gap = 64, 26
    D = Diagram(900, 60 + len(rows) * (bh + gap) - gap + 20, "The tally then and the log now: the same three moves")
    D.text(20, 36, "THEN: THE TALLY", "tag")
    D.text(520, 36, "NOW: THE LOG", "tag")
    for i, (then, now) in enumerate(rows):
        y = 60 + i * (bh + gap)
        D.node(f"t{i}", 20, y, 360, bh, [(then, "combo")], color="ink")
        D.node(f"n{i}", 520, y, 360, bh, [(now, "combo")], color="blue")
        D.edge(f"t{i}", f"n{i}", ports=("right", "left"), label="same move", dy=-8)
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    import json
    d = parse(ctx["out"])
    ish = d["ishango"]
    m0 = d["match"][0]
    reads = {r[0]: r for r in d["read"]}
    r168 = reads[d["notches"]]
    rg = d["regroup"]
    sp = d["split"]
    p = d["pattern"]
    G, M, Dd = ish["G"], ish["M"], ish["D"]
    js_list = lambda xs: ", ".join(map(str, xs))
    say = {
        "marks": f"What the museum documents: **{d['notches']} notches in three columns** on a bone handle with a quartz tip. Everything else here is a reading of them.",
        "count": f"The group sizes as read by Jean de Heinzelin (1962) and listed by the UNESCO astronomy portal. Some groups are uncertain: the NRICH activity brackets them.",
        "primes": f"Column G holds {js_list(G['groups'])}, the four primes between 10 and 20. De Heinzelin read this as arithmetic. **Conjecture**: nothing else shows the carvers knew primes.",
        "tens": f"Column D holds {js_list(Dd['groups'])}: 10 + 1, 20 + 1, 20 − 1, 10 − 1. Read as counting in tens. **Conjecture**.",
        "doubling": f"In column M, 3 sits next to 6, 4 next to 8, and 10 next to 5: **{M['dbl']} doubling pairs**. Read as doubling. **Conjecture**.",
        "totals": f"The totals are {G['total']}, {M['total']} and {Dd['total']}. Some read a moon calendar of about 5½ months (Marshack, 1972), others counting in twelves. **Disputed**.",
        "regroup": f"The UNESCO listing itself writes two groups as 9 + 1 and 1 + 4. Split them and the doubling pairs fall from **{rg['was']} to {rg['dbl']}**: the pattern depends on where you think a group ends.",
    }
    say_html = {k: C.page.md_inline(v) for k, v in say.items()}
    bone_buttons = "".join(f'<button type="button" data-r="{k}">{lbl}</button>' for k, lbl in [
        ("marks", "Just the marks"), ("count", "Count the groups"), ("primes", "Primes"), ("tens", "Tens, ±1"),
        ("doubling", "Doubling"), ("totals", "Totals"), ("regroup", "Group them differently")])
    bone_html = (f'<div class="board bone-board"><div style="min-width:0"><div class="readings" id="bone-readings" aria-label="Readings">{bone_buttons}</div>'
                 f'<div id="bone" class="scrollx">{bone_svg(d)(diagrams.HTML_THEME, False)}</div>'
                 f'<p class="say" id="bone-say" aria-live="polite"></p></div></div>')
    bone_js = BONE_JS.replace("READINGS_JSON", json.dumps(READINGS)).replace("SAY_JSON", json.dumps(say_html))
    match_js = MATCH_JS.replace("START_A", str(m0["a"])).replace("START_B", str(m0["b"]))

    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The tally is the oldest entry in this book, so it starts with something even older: pairing things off. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the tally and its most direct descendant today. Blue: refinements that kept the core idea, one mark for one thing."),
        ]),
        dict(id="match", eyebrow="Try it", title="Which is more, with no numbers at all?", toc="Try it", blocks=[
            dict(type="p", text="A herder drops a stone into a pouch for each sheep that goes out to graze. In the evening, each sheep that comes home takes one stone back out. Stones left in the pouch mean sheep still out. The herder needs no word for *twelve*: only the pairing."),
            dict(type="widget", html=MATCH_HTML, js=match_js, css=BONE_CSS,
                 fallback=dict(type="svg", name="match", draw=match_fallback(m0), alt=f"{m0['a']} stones paired with {m0['b']} sheep"),
                 note="In the interactive edition the sheep come home one at a time, and you can try another day."),
            dict(type="p", text=f"The program pairs off **{d['matchcheck']:,}** random pairs of collections and checks the answer against counting: they agree every time. "
                                f"For {m0['a']} stones and {m0['b']} sheep it makes {m0['pairs']} pairs and finds {m0['by']} left over, where counting both would take {m0['counting']} counts. "
                                "The story of the herder is an illustration, not a historical record."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Two collections are the same size when their things can be paired off with none left over. Georg Cantor made exactly this the definition of *same size* (1878). With it, some infinite sets turn out to be bigger than others: the real numbers cannot be paired off with the whole numbers, as he had shown in 1874."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d, r168), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
            dict(type="p", text="Why is a long tally hard to read? People can see how many things are in a small group at a glance, but past a handful they have to count one by one. "
                                "Psychologists named the glance *subitizing* in 1949; studies put its limit somewhere between about 3 and 6 things. "
                                "So a tally costs one look per mark to read back, and bundling the marks cuts that down:"),
            dict(type="table", head=["Marks", "Looks, one by one", "Looks, in bundles of five"], num=[0, 1, 2], hl=list(reads).index(d["notches"]),
                 rows=[[f"{n:,}", f"{a:,}", f"{b:,}"] for n, a, b in d["read"]]),
            dict(type="p", text="One look per bundle, plus one for the leftover marks. The model is deliberately simple, and the bundles are the subject of topic 2."),
        ]),
        dict(id="bone", eyebrow="The evidence", title="The Ishango bone, notch by notch", toc="The bone", blocks=[
            dict(type="p", text=f"The best-known notched bone was excavated in 1950 at Ishango, in what is now the Democratic Republic of the Congo. It is a fossilised bone handle with a quartz tip, and it carries **{d['notches']} notches** in three columns. "
                                "The museum that holds it says it is still not clear what the marks represent. The group sizes below are those read by Jean de Heinzelin, who first proposed an arithmetic reading in 1962, as listed by the UNESCO astronomy portal. "
                                "The readings scholars have proposed follow; in the interactive edition you can switch between them."),
            dict(type="widget", html=bone_html, js=bone_js,
                 fallback=dict(type="svg", name="ishango", draw=bone_svg(d, layers_on=["numG", "numM", "numD", "totals"]),
                               alt="The Ishango bone's notch groups and column totals"),
                 note="In the interactive edition you can switch between the readings: primes, tens, doubling, totals, and a different grouping."),
            dict(type="table", head=["Column", "Groups (de Heinzelin's reading)", "Total", "All prime?", "All 10 ± 1 or 20 ± 1?", "Doubling pairs"], num=[2, 5],
                 rows=[[k, js_list(ish[k]["groups"]), ish[k]["total"], "yes" if ish[k]["prime"] else "no", "yes" if ish[k]["near"] else "no", ish[k]["dbl"]] for k in "GMD"]),
            dict(type="callout", kind="wrong", label="Wrong turn",
                 text=f"Group the same marks differently and the pattern changes. The UNESCO portal's listing writes two of column M's groups as 9 + 1 and 1 + 4. Split them ({js_list(rg['groups'])}) and the total is still {rg['total']}, "
                      f"but the doubling pairs fall from {rg['was']} to **{rg['dbl']}**. Where a group ends is itself a judgement, and NRICH's version of the same column groups it differently again."),
            dict(type="diagram", name="readings", diagram=readings(d),
                 caption="Each reading is a conjecture; together they are disputed. Keller's sceptical analysis argues the marks show nothing beyond one-to-one matching."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How surprising are the patterns?", toc="Measured", blocks=[
            dict(type="p", text=f"Suppose the carver had cut groups of random sizes. How often would random groups show the bone's patterns? The program counts every possible column exactly, "
                                f"under one stated assumption: each group is equally likely to be any size from {d['lo']} to {d['hi']}, the range of the bone's main groups."),
            dict(type="diagram", name="surprise", diagram=surprise(d)),
            dict(type="callout", kind="wrong", label="Careful",
                 text=f"Both numbers are honest, and they pull in opposite directions. The combination is rare (about 1 in {d['one_in']:,}), which suggests the groups were not cut at random. "
                      f"But the patterns were chosen *after* looking at the bone. Any particular set of numbers is rare, and a reader who checks enough patterns will find one: "
                      f"under the same assumption, **{d['any']}%** of random bones show at least one of these patterns somewhere. Rare is not the same as meaningful."),
            dict(type="details", summary="Show the counts", block=dict(type="table", head=["Pattern", "Columns showing it", "Columns possible"], num=[1, 2],
                 rows=[[k.replace("-", " "), f"{a:,}", f"{b:,}"] for k, (a, b) in p.items()])),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The tally became the log", toc="Full circle", blocks=[
            dict(type="p", text="A tally is only ever added to; the count is its length. Modern systems keep their most important records the same way. "
                                "In 2013 Jay Kreps, one of the creators of the Kafka messaging system at LinkedIn, defined a log as \"an append-only, totally-ordered sequence of records ordered by time\": a tally of events. "
                                "A database writes each change to such a log before applying it; in his words, \"the log is the record of what happened\", and every table is rebuilt from it after a crash."),
            dict(type="diagram", name="circle", diagram=circle()),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The English Exchequer kept accounts on split tally sticks until 1826. Burning the old sticks in the Palace's furnaces led to the great fire of 16 October 1834 at the Palace of Westminster. "
                      f"The program checks the split-tally idea: {sp['honest']:,} honest stick pairs matched, and **{sp['caught']:,} of {sp['n']:,}** forged halves were caught."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Without counting, how can a herder tell that sheep are missing?",
             f"Pair each returning sheep with a stone from the pouch. For {m0['a']} stones and {m0['b']} sheep: **{m0['pairs']} pairs, {m0['by']} stones left over**, so {m0['by']} sheep are still out. Counting both would take {m0['counting']} counts."),
            (f"Add up column G: {' + '.join(map(str, G['groups']))}.", f"**{G['total']}**. Column D also totals {Dd['total']}, and column M {M['total']}: {d['notches']} notches in all."),
            (f"How many looks does a tally of {r168[0]} marks take, one by one and in bundles of five?",
             f"**{r168[1]}** one by one; **{r168[2]}** in fives ({r168[0] // 5} full bundles and one look for the {r168[0] % 5} left over)."),
            ("Why can't the holder of one half of a split tally add a notch?",
             f"The notches were cut across the whole stick before it was split, so the other half would no longer line up. The program forged {sp['n']:,} halves and caught **{sp['caught']:,}**."),
            (f"The bone's patterns, all at once, would appear about once in {d['one_in']:,} random bones. Does that prove the carver knew about primes?",
             f"No. The patterns were picked after looking at the bone, and any particular set of numbers is rare. With several patterns to check, {d['any']}% of random bones show at least one. "
             "The calculation also assumes group sizes are equally likely from 3 to 21, and that de Heinzelin's groups are the right ones."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Ishango bone", text=f"A bone handle with a quartz tip and {d['notches']} notches, excavated in 1950; about 25,000 to 20,000 years old by most sources, 25,000 to 16,000 by a re-evaluation cited by the UNESCO portal. Royal Belgian Institute of Natural Sciences, Brussels.",
                 draw=C.draw_bone, link="https://ishango.naturalsciences.be/en/en-ishango-20.html", link_text="The museum's page",
                 licence="Drawn placeholder; the museum's photographs are at the link."),
            dict(title="Notched bones from Border Cave", text="South Africa, about 44,000 years old. The excavators conclude that people there \"used notched bones for notational purposes\" (d'Errico et al., PNAS 2012).",
                 draw=lambda t, s: C.draw_bone(t, s, groups=[16], tip=False), link="https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1073/pnas.1204213109&format=json&resultType=core",
                 link_text="The paper's Europe PMC record", licence="Drawn placeholder."),
            dict(title="Medieval Exchequer tally sticks", text="London, about 1440. Science Museum Group, object 1952-431. The lender kept the stock, the debtor the foil.",
                 draw=C.draw_split_tally, link="https://collection.sciencemuseumgroup.org.uk/objects/co60506/medieval-exchequer-tally-sticks",
                 link_text="Science Museum Group record", licence="Drawn placeholder. The museum's photograph is CC BY-NC-SA 4.0, so it is linked, not copied."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Georg Cantor", "MacTutor History of Mathematics", "https://mathshistory.st-andrews.ac.uk/Biographies/Cantor/", "1878: sets of equal power are those in one-to-one correspondence"),
            ("start", "Tally sticks", "UK Parliament", "https://www.parliament.uk/about/living-heritage/building/palace/estatehistory/from-the-parliamentary-collections/fire-of-westminster/tallysticks/", "Abolished in 1826; burning them caused the fire of 16 October 1834"),
            ("start", "Medieval Exchequer tally sticks", "Science Museum Group", "https://collection.sciencemuseumgroup.org.uk/objects/co60506/medieval-exchequer-tally-sticks", "A real pair, c. 1440: stock for the lender, foil for the debtor"),
            ("deeper", "The Log: What every software engineer should know about real-time data's unifying abstraction", "Jay Kreps, LinkedIn Engineering (2013)", "https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying", "The append-only log as the core of modern data systems"),
            ("scholar", "Subitizing: An Analysis of Its Component Processes", "Mandler and Shebo, J. Exp. Psychology: General (1982)", "https://escholarship.org/content/qt9fn27772/qt9fn27772_noSplash_758e0f7f6e6c0393e6eb156f48bd67b2.pdf", "Why small groups are seen at a glance and long rows must be counted"),
        ]),
        C.prove_it_section(ctx, "TallyMarks", d["checks"],
                           f"matching against counting on {d['matchcheck']:,} random pairs, the Ishango column arithmetic, the counting programme against brute force, and {sp['n']:,} honest and {sp['n']:,} forged split tallies.",
                           ["static <T> Match match(List<T> first, List<T> second)", "static int doublingPairs(int[] col)"]),
    ]
    return dict(
        title="Tally Marks", date="c. 44,000–20,000 years ago",
        description="Era 1, topic 1 of The Algorithm Evolution Atlas: tally marks and the Ishango bone, with pairing you can try, the readings of the bone, and verified links.",
        lede="The first data structure: one notch per thing, added and never erased. It needs no words for numbers at all.",
        fieldnote="Before numbers, there is matching: one notch for each animal, each day, each debt. You need no idea of \"seventeen\" to keep this record; you only need to be able to make one mark per thing.",
        card=[("When", "Border Cave, c. 44,000 years ago · Ishango, c. 25,000–20,000 years ago by most sources (a re-evaluation cited by the UNESCO portal gives 25,000–16,000)"),
              ("Where", "South Africa and the DR Congo (**documented**)"),
              ("What hurt", "Remembering *how many* with no words for big numbers"),
              ("The fix", "One mark per thing, on something that lasts"),
              ("Cost", f"One look per mark to read it back: {r168[0]} marks, {r168[1]} looks"),
              ("Atlas", "Ch. 7 Early Number Systems · Ch. 89 Numeral Systems")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `TallyMarks.java`. The bone is drawn for this book from the published group counts; it is not a photograph.",
    )
