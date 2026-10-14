"""Era 5, topic 11: AVL trees. Every number is parsed from AvlTrees.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"trace: insert (.*?) ; the result, root first with \(left right\) branches: (.+?), height (\d+) ; a plain search tree would be a chain of height (\d+)$", ln):
            steps = re.findall(r"(\d+)(?: \(([^)]*)\))?", m.group(1))
            d["trace"] = dict(steps=steps, tree=m.group(2), h=m.group(3), chain=m.group(4))
        elif ln.startswith("plain: "):
            d["plain"] = re.findall(r"([\d,]+) (sorted|random) keys: plain tree height ([\d,]+), average search ([\d.]+) steps ; AVL height (\d+), average search ([\d.]+) steps", ln)
        elif m := re.match(r"avl: ([\d,]+) random keys inserted ; .*? after each ([\d,]+) insertions ; ([\d,]+) single and ([\d,]+) double rotations, ([\d.]+) per insertion ; final height (\d+), against the bound .*? = ([\d.]+) and the least possible (\d+)$", ln):
            g = m.groups()
            d["avl"] = dict(n=g[0], every=g[1], single=g[2], double=g[3], per=g[4], h=g[5], bound=g[6], least=g[7])
        elif ln.startswith("fibonacci: "):
            d["fib"] = re.findall(r"height (\d+): ([\d,]+) nodes?", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def tree_parse(s):
    """'4(2(1 3) 6(5 7))' -> (key, left, right); '-' is an empty branch."""
    pos = [0]

    def node():
        if s[pos[0]] == "-":
            pos[0] += 1
            return None
        m = re.match(r"\d+", s[pos[0]:])
        key = m.group(0)
        pos[0] += len(key)
        if pos[0] < len(s) and s[pos[0]] == "(":
            pos[0] += 1
            left = node()
            pos[0] += 1                                   # space
            right = node()
            pos[0] += 1                                   # ')'
            return (key, left, right)
        return (key, None, None)
    return node()


def trees_svg(d):
    tr = d["trace"]

    def draw(t, standalone):
        o = []
        o.append(C.text(20, 22, "The keys 1 to 7, inserted in order", t["ink"], 13, "start", 700))
        o.append(C.text(20, 46, "plain search tree", t["muted"], 12))
        n = int(tr["chain"])
        for k in range(n):
            x, y = 40 + k * 34, 70 + k * 30
            if k:
                o.append(C.line(x - 34, y - 30, x, y, t["axis"], 1.5))
        for k in range(n):
            x, y = 40 + k * 34, 70 + k * 30
            o.append(C.circle(x, y, 14, t["surface"], t["ink2"], 1.5))
            o.append(C.text(x, y + 5, k + 1, t["ink"], 13, "middle", 700))
        o.append(C.text(40, 70 + n * 30 + 6, f"height {n}: a search may take {n} steps", t["muted"], 12))
        root = tree_parse(tr["tree"])
        o.append(C.text(360, 46, "AVL tree", t["muted"], 12))
        pos = {}

        def place(nd, lo, hi, depth):
            if nd is None:
                return
            x = (lo + hi) / 2
            pos[nd[0]] = (x, 80 + depth * 70)
            place(nd[1], lo, x, depth + 1)
            place(nd[2], x, hi, depth + 1)

        place(root, 360, 700, 0)

        def edges(nd):
            if nd is None:
                return
            for k in (nd[1], nd[2]):
                if k:
                    (x1, y1), (x2, y2) = pos[nd[0]], pos[k[0]]
                    o.append(C.line(x1, y1, x2, y2, t["axis"], 1.5))
                    edges(k)
        edges(root)
        for key, (x, y) in pos.items():
            o.append(C.circle(x, y, 16, t["wash"], t["red"], 1.8))
            o.append(C.text(x, y + 5, key, t["ink"], 14, "middle", 700))
        nrot = sum(1 for _, r in tr["steps"] if r)
        o.append(C.text(360, 80 + 3 * 70, f"height {tr['h']}: {nrot} rotations kept every node balanced", t["muted"], 12))
        return C.svg_doc(720, 70 + n * 30 + 20, "".join(o), "Keys 1 to 7 in order: a chain of height 7, or an AVL tree of height 3", t, standalone, 0.55, 720)
    return draw


AV_HTML = """
<div class="board av-board">
  <div style="min-width:0">
    <div class="av-btns">
      <label class="eyebrow" for="av-key" style="align-self:center">Key</label><input id="av-key" type="number" value="8" min="0" max="999">
      <button type="button" id="av-ins">Insert</button><button type="button" id="av-seq">Insert 1 to 15 in order</button>
      <button type="button" id="av-rnd">Insert 5 random</button><button type="button" id="av-clr">Empty</button>
    </div>
    <div class="eyebrow">AVL tree</div><div class="av-tree" id="av-avl"></div>
    <div class="eyebrow">plain search tree, same keys</div><div class="av-tree" id="av-plain"></div>
  </div>
  <div style="min-width:0">
    <div class="av-stats" id="av-stats"></div>
    <ol class="av-log" id="av-log"></ol>
  </div>
</div>
"""

AV_CSS = """
.av-btns{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 10px}
.av-btns input{width:5em;font:14px var(--mono);padding:5px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink)}
.av-tree{overflow-x:auto;margin:4px 0 10px}
.av-tree svg{display:block;height:auto}
.av-stats{font:13px var(--mono);display:grid;gap:4px}
.av-log{font:12.5px var(--mono);padding-left:2.8em;max-height:260px;overflow-y:auto}
"""

AV_JS = r"""
(() => {
  const avlBox = document.getElementById("av-avl");
  if (!avlBox) return;
  const NS = "http://www.w3.org/2000/svg";
  let avl = null, plain = null, keys = [], log = [], seed = 1962;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 2147483648 * 100); };
  const h = n => n ? n.h : 0;
  const fix = n => { n.h = 1 + Math.max(h(n.l), h(n.r)); };
  const rotR = y => { const x = y.l; y.l = x.r; x.r = y; fix(y); fix(x); return x; };
  const rotL = x => { const y = x.r; x.r = y.l; y.l = x; fix(x); fix(y); return y; };
  function ins(n, k) {
    if (!n) return {k, l: null, r: null, h: 1};
    if (k < n.k) n.l = ins(n.l, k); else n.r = ins(n.r, k);
    fix(n);
    const bal = h(n.l) - h(n.r);
    if (bal > 1) { if (k < n.l.k) { log.push(`${k}: single rotation (right) at ${n.k}`); return rotR(n); } log.push(`${k}: double rotation (left-right) at ${n.k}`); n.l = rotL(n.l); return rotR(n); }
    if (bal < -1) { if (k >= n.r.k) { log.push(`${k}: single rotation (left) at ${n.k}`); return rotL(n); } log.push(`${k}: double rotation (right-left) at ${n.k}`); n.r = rotR(n.r); return rotL(n); }
    return n;
  }
  function insPlain(n, k) { if (!n) return {k, l: null, r: null}; if (k < n.k) n.l = insPlain(n.l, k); else n.r = insPlain(n.r, k); return n; }
  const height = n => n ? 1 + Math.max(height(n.l), height(n.r)) : 0;
  function draw(box, root) {
    box.innerHTML = "";
    if (!root) return;
    const order = []; (function io(n, d) { if (!n) return; io(n.l, d + 1); n.x = order.length; n.d = d; order.push(n); io(n.r, d + 1); })(root, 0);
    const H = height(root), W = Math.max(200, order.length * 30 + 20), Ht = Math.min(H, 16) * 40 + 30;
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", `0 0 ${W} ${Ht}`); svg.setAttribute("width", W); box.appendChild(svg);
    const X = n => 20 + n.x * 30, Y = n => 20 + Math.min(n.d, 15) * 40;
    order.forEach(n => { for (const c of [n.l, n.r]) if (c) sv("line", {x1: X(n), y1: Y(n), x2: X(c), y2: Y(c), stroke: "var(--axis)", "stroke-width": 1.5}, svg); });
    order.forEach(n => {
      sv("circle", {cx: X(n), cy: Y(n), r: 12, fill: "var(--surface)", stroke: "var(--ink2)", "stroke-width": 1.5}, svg);
      const t = sv("text", {x: X(n), y: Y(n) + 4, "text-anchor": "middle", "font-size": 11, "font-weight": 700, fill: "var(--ink)"}, svg); t.textContent = n.k;
    });
  }
  function add(k) { if (keys.includes(k)) return; keys.push(k); avl = ins(avl, k); plain = insPlain(plain, k); }
  function show() {
    draw(avlBox, avl); draw(document.getElementById("av-plain"), plain);
    const st = document.getElementById("av-stats"); st.innerHTML = "";
    const best = Math.ceil(Math.log2(keys.length + 1));
    el("div", {}, st).textContent = `${keys.length} keys`;
    el("div", {}, st).textContent = `AVL height ${h(avl)} (the least possible is ${best})`;
    el("div", {}, st).textContent = `plain tree height ${height(plain)}`;
    const ol = document.getElementById("av-log"); ol.innerHTML = "";
    (log.length ? log.slice(-14) : ["no rotations yet"]).forEach(x => { el("li", {}, ol).textContent = x; });
  }
  const reset = () => { avl = null; plain = null; keys = []; log = []; };
  document.getElementById("av-ins").addEventListener("click", () => { add(Math.max(0, Math.min(999, Math.floor(Number(document.getElementById("av-key").value) || 0)))); show(); });
  document.getElementById("av-seq").addEventListener("click", () => { reset(); for (let k = 1; k <= 15; k++) add(k); show(); });
  document.getElementById("av-rnd").addEventListener("click", () => { for (let i = 0; i < 5; i++) add(rnd()); show(); });
  document.getElementById("av-clr").addEventListener("click", () => { reset(); show(); });
  reset(); for (let k = 1; k <= 7; k++) add(k); show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How AVL trees combined older ideas, and where they led")
    W = 210
    nodes = {
        "bs": (20, 20, "Searching by halves", "smaller or larger? go left or right", "", "ink"),
        "cell": (395, 20, "Cells with two links", "nodes joined by addresses", "topic 6", "ink"),
        "fib": (770, 20, "Fibonacci numbers", "each the sum of the two before", "Era 2 topic 8", "ink"),
        "avl": (395, 170, "AVL trees", "⊕ heights within one; repair by rotations", "Moscow, 1962", "red"),
        "rot": (20, 330, "Rotations", "turn three links, keep the order", "", "ink"),
        "bnd": (395, 330, "A height bound", "never much over 1.44 log2 n", "via Fibonacci trees", "ink"),
        "more": (770, 330, "Other balanced trees", "different rules, the same rotations", "later", "ink"),
        "today": (395, 480, "Ordered maps today", "sorted keys with guaranteed search time", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("bs", "avl", ports=("bottom", "top:0.15"))
    D.edge("cell", "avl", ports=("bottom", "top"))
    D.edge("fib", "bnd", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("avl", "rot", ports=("bottom:0.1", "top:0.7"))
    D.edge("avl", "bnd", ports=("bottom", "top"))
    D.edge("avl", "more", ports=("bottom:0.9", "top:0.3"))
    D.edge("bnd", "today", ports=("bottom", "top"))
    D.edge("more", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: the Fibonacci numbers were not built into the method; they turn up in its worst case.", "caption")
    return D


def chain(d):
    p, a = d["plain"], d["avl"]
    srt, rnd = p[0], p[1]
    steps = [
        (f"Keys arriving in order make a search tree a chain: height {srt[2]} for {srt[0]} keys",
         f"Keep every node's two branches within one in height: height {srt[4]}", "Adelson-Velsky and Landis, 1962"),
        ("Each insertion can break the rule somewhere above it",
         f"Turn three links (a rotation) at the first unbalanced node: {a['per']} rotations per insertion on average", "single and double rotations"),
        ("Is the balanced tree close enough to perfect?",
         f"The thinnest legal trees follow the Fibonacci numbers: height {a['h']} for {a['n']} keys, against the least possible {a['least']}", "the bound 1.44 log2 n"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from chains to balanced trees")
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
    tr, p, a, fb = d["trace"], d["plain"], d["avl"], d["fib"]
    steps_txt = "; ".join(f"{k}" + (f" ({r})" if r else "") for k, r in tr["steps"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A search tree asks \"smaller or larger?\" at each node, like searching a sorted list by halves, and its nodes are cells joined by addresses (topic 6). Adelson-Velsky and Landis added a rule that keeps the tree bushy whatever order the keys arrive in, and a cheap repair for when an insertion breaks it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: AVL trees. Blue: ordered maps today."),
        ]),
        dict(id="grow", eyebrow="Try it", title="Insert keys and watch the rotations", toc="Try it", blocks=[
            dict(type="p", text="Insert keys into an AVL tree and, for comparison, into a plain search tree. Insert 1 to 15 in order: the plain tree becomes a chain while the AVL tree stays as short as a tree of 15 keys can be. The list on the right records each rotation."),
            dict(type="widget", html=AV_HTML, js=AV_JS, css=AV_CSS,
                 fallback=dict(type="svg", name="trees", draw=trees_svg(d), alt="Keys 1 to 7 in order: a chain of height 7, or an AVL tree of height 3", width=720),
                 note="In the interactive edition you can insert your own keys."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Heights within one, repaired by rotations", toc="How it works", blocks=[
            dict(type="p", text="**The rule.** At every node, \"the heights of the two child subtrees ... differ by not more than one\". After an insertion, walk back up from the new key; at the first node where the difference has become two, turn its branches round. If the new key went down the outside (left of the left child, or right of the right child), one rotation does it; if it went down the inside, two. A rotation changes three links, keeps the keys in order, and gives the subtree back the height it had before the insertion, so nothing higher up needs repair."),
            dict(type="p", text=f"**Keys 1 to 7, in order**, as the program inserted them: {steps_txt}. The result is {tr['tree']} (root first, with left and right branches), height {tr['h']}; a plain search tree would be a chain of height {tr['chain']}."),
            dict(type="table", head=["Height", "Fewest nodes an AVL tree of this height can have"], num=[0, 1], rows=[list(x) for x in fb]),
            dict(type="p", text="**The bound.** The thinnest AVL tree of height h has one branch of height h−1 and one of h−2, so its size is F(h+2) − 1, where F are the Fibonacci numbers. Since the Fibonacci numbers grow like powers of the golden ratio, a tree of n nodes can never be taller than about 1.44 log₂ n. The program built these thinnest trees, checked the rule at every node, and checked the bound against them."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Don't insist on a perfect tree, which would be costly to keep. Insist on a looser rule, heights within one, that a three-link rotation can always restore, and that still keeps the height within a constant factor of the best."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A million insertions", toc="Measured", blocks=[
            dict(type="table", head=["Keys", "Order", "Plain tree height", "Plain average search", "AVL height", "AVL average search"], num=[0, 2, 3, 4, 5],
                 rows=[list(x) for x in p], hl=0),
            dict(type="p", text=f"{a['n']} random keys inserted, with the order of the keys and the balance rule checked at every node after each {a['every']} insertions: {a['single']} single and {a['double']} double rotations, {a['per']} per insertion. The final height, {a['h']}, sits between the least possible, {a['least']}, and the bound 1.44 log₂(n+2) − 0.33 = {a['bound']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Four pages in the Doklady", toc="The evidence", blocks=[
            dict(type="p", text="G. M. Adel'son-Vel'skii and E. M. Landis, \"An algorithm for the organization of information\", *Doklady Akademii Nauk SSSR* 146(2): 263–266 (1962), presented by I. G. Petrovskii and received on 13 April 1962 (Math-Net.Ru); English translation by Myron J. Ricci in *Soviet Mathematics – Doklady* 3: 1259–1263 (1962). The AVL tree is \"the first self-balancing binary search tree [data structure] to be invented\" (Wikipedia)."),
            dict(type="p", text="Adelson-Velsky (1922–2014) led a chess program at ITEP from 1963 that defeated the Kotok–McCarthy program in 1966, \"the first chess match between computer programs\", and grew into Kaissa, \"the first world computer chess champion\". That the AVL paper was written for the chess work is often said, but no opened source says so; the catalog marks it as conjecture."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Order, kept cheaply", toc="Full circle", blocks=[
            dict(type="p", text="A hash table (topic 4) finds a key in a few looks but forgets the order of the keys; a balanced tree keeps them in order and still finds any key in about log₂ n steps, whatever order they arrived in. Many later kinds of balanced tree use different rules, but repair them with the same rotations."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{p[0][0]} keys inserted in order: a plain tree needs {p[0][3]} steps on average to find one, the AVL tree {p[0][5]}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Insert 3, 2, 1 into an AVL tree. What happens?", "After 1, node 3 has a left branch of height 2 and a right branch of height 0: one right rotation makes 2 the root with children 1 and 3."),
            ("Insert 3, 1, 2. Why is one rotation not enough?", "2 went down the inside (right of the left child). Rotate 1 left first, making 3–2–1 a straight line, then rotate 3 right: a double rotation."),
            ("Can an AVL tree of height 4 have 6 nodes?", "No: the thinnest has F(6) − 1 = 7 nodes."),
            ("Why does a rotation never need repeating higher up after an insertion?", "It restores the subtree to the height it had before the insertion, so the nodes above see no change."),
            ("What is the shortest possible tree for 1,000,000 keys?", "Height 20, since 2²⁰ − 1 = 1,048,575 ≥ 1,000,000. The program's AVL tree had height 24."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="An algorithm for the organization of information (1962)", text="Adelson-Velsky and Landis's four pages in the Doklady of the USSR Academy of Sciences.",
                 draw=C.draw_manuscript, link="https://mathnet.ru/eng/dan26964", link_text="Math-Net.Ru", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "AvlTrees", d["checks"],
                           f"the keys 1 to 7 with their rotations, plain against AVL trees on sorted and random keys, {a['n']} insertions with order and balance checked, and the Fibonacci trees against the height bound.",
                           ["static Node insert(Node n, int key)"]),
    ]
    return dict(
        title="AVL Trees", date="1962",
        description="Era 5, topic 11 of The Algorithm Evolution Atlas: Adelson-Velsky and Landis's balanced search trees, kept within one level by rotations, with the Fibonacci trees that bound their height.",
        lede="A search tree is fast while it stays bushy, and useless when keys arrive in order and it becomes a chain. Two Moscow mathematicians kept every node's two branches within one level of each other, repairing the tree by turning three links.",
        fieldnote=f"The keys 1 to 7 in order: a plain tree becomes a line of 7; this one, after {sum(1 for _, r in tr['steps'] if r)} turns of its branches, is a perfect tree of height {tr['h']}. A million random keys made a tree of height {a['h']}, never more than the Fibonacci numbers allow.",
        card=[("When", "Paper received 13 April 1962"),
              ("Where", "Moscow"),
              ("What hurt", "Search trees degenerate into chains"),
              ("The fix", "Heights within one; single or double rotations"),
              ("Guarantee", "Height at most about 1.44 log2 n")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AvlTrees.java`.",
    )
