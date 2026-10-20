"""Era 7, topic 5: splay trees and amortized analysis. Every number is parsed from SplayTrees.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"lemma: ([\d,]+) random accesses on a splay tree of ([\d,]+) keys ; .*?\(closest margin ([\d.]+)\) ; total rotations ([\d,]+), ([\d.]+) per access on average, against an average bound of ([\d.]+) from the lemma ; final potential ([\d,]+) of at most n log2 n = ([\d,]+)", ln):
            d["lemma"] = dict(ops=m.group(1), n=m.group(2), margin=m.group(3), rot=m.group(4), avg=m.group(5), bound=m.group(6), phi=m.group(7), phimax=m.group(8))
        elif m := re.match(r"sorted: [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; ")[0::1]:
                pass
            for mm in re.finditer(r"([\d,]+) keys: plain tree ([\d,]+) nodes visited inserting and ([\d,]+) reading ; splay tree ([\d,]+) and ([\d,]+) \(([\d,]+) rotations reading\) ; balanced tree ([\d,]+) reading", m.group(1)):
                rows.append(dict(n=mm.group(1), pins=mm.group(2), pread=mm.group(3), sins=mm.group(4), sread=mm.group(5), srot=mm.group(6), bal=mm.group(7)))
            d["sorted"] = rows
        elif m := re.match(r"zipf: ([\d,]+) keys, .*?, ([\d,]+) accesses ; average nodes visited per access: balanced tree ([\d.]+) ; optimal fixed tree for the true frequencies ([\d.]+) ; splay tree, knowing nothing, ([\d.]+) ; entropy of the frequencies ([\d.]+) bits", ln):
            d["zipf"] = dict(n=m.group(1), acc=m.group(2), bal=m.group(3), opt=m.group(4), splay=m.group(5), ent=m.group(6))
        elif m := re.match(r"workingset: a splay tree of ([\d,]+) keys, [^;]* ; (.*?) ; a balanced tree would visit about (\d+) every time", ln):
            rows = []
            for part in m.group(2).split(" ; "):
                mm = re.match(r"([\d,]+) keys? in use: ([\d.]+) nodes per access \(log2 = ([\d.]+)\)", part)
                rows.append(dict(w=mm.group(1), avg=mm.group(2), lg=mm.group(3)))
            d["ws"] = dict(n=m.group(1), rows=rows, bal=m.group(3))
        elif m := re.match(r"stack: ([\d,]+) operations, .*? the slowest single operation did ([\d,]+) pushes and pops, but all of them together did ([\d,]+), under the 2m = ([\d,]+)", ln):
            d["stack"] = dict(m=m.group(1), worst=m.group(2), total=m.group(3), two=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def rotations_svg(d):
    """Zig-zig and zig-zag, before and after."""
    def draw(t, standalone):
        o = []
        W, H = 780, 330

        def tree(x0, y0, shape, hot):
            # shape: list of (label, x, y, parent index or -1); subtrees drawn as triangles
            for lab, x, y, p in shape:
                if p >= 0:
                    px, py = shape[p][1], shape[p][2]
                    o.append(C.line(x0 + px, y0 + py + 12, x0 + x, y0 + y - 12, t["axis"], 1.4))
            for lab, x, y, p in shape:
                if lab in "ABCD":
                    o.append(C.path(f"M{x0 + x:.1f},{y0 + y - 12:.1f} L{x0 + x - 13:.1f},{y0 + y + 12:.1f} L{x0 + x + 13:.1f},{y0 + y + 12:.1f} Z", t["axis"], t["wash"], 1.2))
                    o.append(C.text(x0 + x, y0 + y + 8, lab, t["muted"], 11, "middle", 700))
                else:
                    col = t["red"] if lab == hot else t["ink"]
                    o.append(C.circle(x0 + x, y0 + y, 13, t["surface"], col, 2))
                    o.append(C.text(x0 + x, y0 + y + 5, lab, col, 13, "middle", 700))

        o.append(C.text(20, 26, "The two double steps of splaying: x climbs two levels at a time", t["ink"], 13, "start", 700))
        # zig-zig: g(p(x(A,B),C),D) -> x(A,p(B,g(C,D)))
        o.append(C.text(20, 56, "Zig-zig: x and its parent p lean the same way", t["ink"], 12.5, "start", 700))
        before = [("g", 120, 90, -1), ("p", 80, 140, 0), ("D", 160, 140, 0), ("x", 50, 190, 1), ("C", 110, 190, 1), ("A", 25, 240, 3), ("B", 75, 240, 3)]
        after = [("x", 60, 90, -1), ("A", 25, 140, 0), ("p", 100, 140, 0), ("B", 70, 190, 2), ("g", 130, 190, 2), ("C", 105, 240, 4), ("D", 155, 240, 4)]
        tree(0, 0, before, "x")
        o.append(C.text(205, 175, "→", t["ink"], 24, "middle", 700))
        o.append(C.text(205, 198, "p up, then x up", t["muted"], 11, "middle"))
        tree(230, 0, after, "x")
        # zig-zag: g(p(A,x(B,C)),D) -> x(p(A,B),g(C,D))
        o.append(C.text(420, 56, "Zig-zag: x and p lean opposite ways", t["ink"], 12.5, "start", 700))
        before2 = [("g", 120, 90, -1), ("p", 80, 140, 0), ("D", 160, 140, 0), ("A", 50, 190, 1), ("x", 110, 190, 1), ("B", 85, 240, 4), ("C", 135, 240, 4)]
        after2 = [("x", 100, 110, -1), ("p", 60, 160, 0), ("g", 140, 160, 0), ("A", 35, 210, 1), ("B", 85, 210, 1), ("C", 115, 210, 2), ("D", 165, 210, 2)]
        tree(400, 0, before2, "x")
        o.append(C.text(605, 175, "→", t["ink"], 24, "middle", 700))
        o.append(C.text(605, 198, "x up twice", t["muted"], 11, "middle"))
        tree(600, 0, after2, "x")
        o.append(C.text(20, H - 30, "A, B, C, D stand for whole subtrees; their order from left to right never changes, so the tree stays a search tree.", t["muted"], 12))
        o.append(C.text(20, H - 12, "Zig-zig (p before x) is what makes splaying roughly halve the depth of every node on the path; rotating x up alone would not.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Zig-zig and zig-zag rotations", t, standalone, 0.55, 780)
    return draw


SP_HTML = """
<div class="board sp-board">
  <div style="min-width:0">
    <div class="sp-view" id="sp-view"></div>
  </div>
  <div style="min-width:0">
    <div class="sp-btns"><button type="button" class="primary" id="sp-seq">Read 1 to 15 in order</button><button type="button" id="sp-reset">Insert 1 to 15 again</button></div>
    <div class="sp-btns"><button type="button" id="sp-big">The program's test: 1,000 keys</button></div>
    <div class="sp-stats" id="sp-stats"></div>
    <p class="say" id="sp-say" aria-live="polite"></p>
  </div>
</div>
"""

SP_CSS = """
.sp-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.sp-view circle{cursor:pointer}
.sp-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.sp-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

SP_JS = r"""
(() => {
  const view = document.getElementById("sp-view");
  if (!view) return;
  const PROG = __PROG__;
  // the splay tree, as in the program: nodes are the keys themselves, -1 means none
  function Tree(n) { this.L = new Int32Array(n).fill(-1); this.R = new Int32Array(n).fill(-1); this.P = new Int32Array(n).fill(-1); this.S = new Int32Array(n); this.root = -1; this.rot = 0; this.vis = 0; }
  Tree.prototype.sz = function (x) { return x < 0 ? 0 : this.S[x]; };
  Tree.prototype.rotate = function (x) {
    const L = this.L, R = this.R, P = this.P, p = P[x], g = P[p];
    if (L[p] === x) { L[p] = R[x]; if (R[x] >= 0) P[R[x]] = p; R[x] = p; } else { R[p] = L[x]; if (L[x] >= 0) P[L[x]] = p; L[x] = p; }
    P[p] = x; P[x] = g;
    if (g >= 0) { if (L[g] === p) L[g] = x; else R[g] = x; } else this.root = x;
    this.S[p] = 1 + this.sz(L[p]) + this.sz(R[p]); this.S[x] = 1 + this.sz(L[x]) + this.sz(R[x]); this.rot++;
  };
  Tree.prototype.splay = function (x) {
    const P = this.P, L = this.L;
    while (P[x] >= 0) { const p = P[x], g = P[p]; if (g < 0) this.rotate(x); else if ((L[g] === p) === (L[p] === x)) { this.rotate(p); this.rotate(x); } else { this.rotate(x); this.rotate(x); } }
  };
  Tree.prototype.access = function (k) { let x = this.root; while (x !== k) { this.vis++; x = k < x ? this.L[x] : this.R[x]; } this.vis++; this.splay(x); };
  Tree.prototype.insert = function (k) {
    this.S[k] = 1;
    if (this.root < 0) { this.root = k; return; }
    let x = this.root, p = -1; while (x >= 0) { this.vis++; p = x; x = k < x ? this.L[x] : this.R[x]; }
    this.P[k] = p; if (k < p) this.L[p] = k; else this.R[p] = k;
    for (let a = p; a >= 0; a = this.P[a]) this.S[a]++;
    this.splay(k);
  };
  Tree.prototype.phi = function () { let s = 0; for (let i = 0; i < this.S.length; i++) if (this.S[i] > 0) s += Math.log2(this.S[i]); return s; };
  Tree.prototype.depth = function (k) { let x = this.root, d = 1; while (x !== k) { x = k < x ? this.L[x] : this.R[x]; d++; } return d; };
  const N = 15;
  let T, next = 0;
  function reset() { T = new Tree(N); for (let k = 0; k < N; k++) T.insert(k); next = 0; draw("Keys 1 to 15 inserted in order: every insert splays the new key to the root, so the tree is a long path. Click any key to access it."); }
  function access(k) {
    const d = T.depth(k), phi0 = T.phi(), r0 = T.rot, n = N, sx = T.S[k];
    T.access(k);
    const rot = T.rot - r0, dphi = T.phi() - phi0, bound = 3 * (Math.log2(n) - Math.log2(sx)) + 1;
    draw(`Accessed ${k + 1}: it was at depth ${d}; ${rot} rotation${rot === 1 ? "" : "s"} brought it to the root. Rotations + change in potential = ${(Math.max(rot, 1) + dphi).toFixed(2)} ≤ ${bound.toFixed(2)}, the access lemma's bound.`);
  }
  function draw(msg) {
    view.innerHTML = "";
    const pos = {}, order = [];
    (function walk(x, dep) { if (x < 0) return; walk(T.L[x], dep + 1); pos[x] = [order.length, dep]; order.push(x); walk(T.R[x], dep + 1); })(T.root, 0);
    const maxd = Math.max(...Object.values(pos).map(p => p[1])), H = 40 + maxd * 34 + 30;
    const svg = sv("svg", {viewBox: `0 0 420 ${Math.max(H, 220)}`}, view), X = i => 20 + i * (380 / (N - 1)), Y = dd => 30 + dd * 34;
    for (let x = 0; x < N; x++) { const p = T.P[x]; if (p >= 0) sv("line", {x1: X(pos[x][0]), y1: Y(pos[x][1]), x2: X(pos[p][0]), y2: Y(pos[p][1]), stroke: "var(--axis)", "stroke-width": 1.5}, svg); }
    for (let x = 0; x < N; x++) {
      const c = sv("circle", {cx: X(pos[x][0]), cy: Y(pos[x][1]), r: 12, fill: x === T.root ? "var(--red)" : "var(--surface)", stroke: "var(--ink)", "stroke-width": 1.8}, svg);
      c.addEventListener("click", () => access(x));
      const t = sv("text", {x: X(pos[x][0]), y: Y(pos[x][1]) + 4.5, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: x === T.root ? "var(--on-red)" : "var(--ink)", "pointer-events": "none"}, svg); t.textContent = x + 1;
    }
    const st = document.getElementById("sp-stats"); st.innerHTML = "";
    el("div", {}, st, `depth of the tree: ${maxd + 1}`);
    el("div", {}, st, `potential (sum of log2 sizes): ${T.phi().toFixed(2)}`);
    el("div", {}, st, `rotations so far: ${T.rot}`);
    if (msg) document.getElementById("sp-say").textContent = msg;
  }
  document.getElementById("sp-reset").addEventListener("click", reset);
  document.getElementById("sp-seq").addEventListener("click", () => {
    const v0 = T.vis, r0 = T.rot;
    for (let k = 0; k < N; k++) T.access(k);
    draw(`Read 1 to 15 in order: ${T.vis - v0} nodes visited and ${T.rot - r0} rotations in all. The first read was slow; the rest were cheap, because each splay roughly halved the path.`);
  });
  document.getElementById("sp-big").addEventListener("click", () => {
    const B = new Tree(1000); for (let k = 0; k < 1000; k++) B.insert(k);
    const ins = B.vis; B.vis = 0; const r0 = B.rot;
    for (let k = 0; k < 1000; k++) B.access(k);
    const p = PROG;
    draw(`1,000 keys inserted in order, then read in order: ${ins} nodes visited inserting, ${B.vis.toLocaleString("en-US")} reading, ${(B.rot - r0).toLocaleString("en-US")} rotations reading. The program: ${p.sins}, ${p.sread} and ${p.srot}. A plain search tree would visit ${p.pread} reading.`);
  });
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How splay trees combined older ideas, and where they led")
    W = 210
    nodes = {
        "bst": (20, 20, "Search trees", "walk down: left if smaller, right if larger", "", "ink"),
        "avl": (395, 20, "Balanced trees", "extra fields and rules keep paths short", "Era 5, topic 11", "ink"),
        "mtf": (770, 20, "Self-adjusting lists", "move what you used to the front", "", "ink"),
        "sp": (395, 180, "Splay trees", "⊕ rotate every accessed key to the root", "Sleator and Tarjan, 1985", "red"),
        "am": (20, 340, "Amortized analysis", "⊕ a potential pays for slow steps", "Tarjan, 1985", "ink"),
        "conj": (770, 340, "Dynamic optimality", "as good as any search tree? still open", "conjectured 1985", "ink"),
        "today": (395, 490, "Today", "caches and garbage collection", "uses Wikipedia names", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("bst", "sp", ports=("bottom", "top:0.15"))
    D.edge("avl", "sp", ports=("bottom", "top"), label="the same job, no bookkeeping", at=0.5, dx=8, anchor="start")
    D.edge("mtf", "sp", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("sp", "am", ports=("bottom:0.15", "top"))
    D.edge("sp", "conj", ports=("bottom:0.85", "top"))
    D.edge("sp", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: Wikipedia calls splay trees \"particularly useful\" for these. Dashed: the same idea for lists, one of Tarjan's examples of amortization.", "caption")
    return D


def chain(d):
    lm, srt, zp = d["lemma"], d["sorted"][0], d["zipf"]
    steps = [
        ("Balanced trees (Era 5) need extra fields in every node and intricate rules after every change",
         "Splaying: after every access, rotate the key to the root, two levels at a time", "Sleator and Tarjan, 1985"),
        ("One access can cost as much as the tree is deep: no single operation is guaranteed fast",
         f"Amortized analysis: a potential pays for slow accesses; the access lemma held on all {lm['ops']} splays", "Tarjan, 1985"),
        ("Real workloads use some keys far more than others",
         f"Used keys drift to the top: {zp['splay']} nodes per access on skewed use, without knowing the frequencies", "static optimality"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from bookkeeping to amortization")
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
    lm, srt, zp, ws, stk = d["lemma"], d["sorted"], d["zipf"], d["ws"], d["stack"]
    s1 = srt[0]
    sorted_rows = [[r["n"], r["pins"], r["pread"], r["sins"], r["sread"], r["bal"]] for r in srt]
    ws_rows = [[r["w"], r["avg"], r["lg"]] for r in ws["rows"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Balanced search trees (Era 5) kept every path short by bookkeeping. Self-adjusting lists simply moved whatever was used to the front. Sleator and Tarjan did the same for trees: rotate whatever was used to the root. To prove it works they judged whole sequences of operations rather than single ones, which Tarjan called amortized analysis. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: splay trees. Blue: where they are used."),
        ]),
        dict(id="play", eyebrow="Try it", title="Splay a key to the root", toc="Try it", blocks=[
            dict(type="p", text="Fifteen keys inserted in order 1, 2, 3, …: each insertion splays the new key to the root, so the tree ends as a long path. Click a key to access it: it is rotated to the root (red), two levels at a time, and the path it came from is folded roughly in half. Each access also checks the access lemma, the inequality at the heart of the proof. Then read every key in order, and try the program's own test with 1,000 keys, done the same way in your browser."),
            dict(type="widget", html=SP_HTML, js=SP_JS.replace("__PROG__", json.dumps(s1)), css=SP_CSS,
                 fallback=dict(type="table", head=["Keys", "Plain tree, inserting", "Plain tree, reading", "Splay tree, inserting", "Splay tree, reading", "Balanced tree, reading"], num=[0, 1, 2, 3, 4, 5], rows=sorted_rows),
                 note="In the interactive edition you can click keys and watch the tree reshape itself."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Rotate it to the top, and pay later", toc="How it works", blocks=[
            dict(type="p", text="**A rotation** lifts a node above its parent while keeping the left-to-right order of everything, so the tree is still a search tree. Splaying a node x repeats rotations until x is the root, looking two levels up each time:"),
            dict(type="svg", name="rotations", draw=rotations_svg(d), alt="Zig-zig and zig-zag rotations", width=780),
            dict(type="p", text="When x's parent is the root, one rotation (zig) finishes the job."),
            dict(type="p", text="**Amortized cost.** Give the tree a potential Φ, the sum over all nodes of log₂ of the size of the subtree below them. Define an operation's amortized cost as its actual cost plus the change in Φ. A splay that takes many rotations flattens a long path and lowers Φ a lot, so its amortized cost stays small. Sleator and Tarjan's access lemma: splaying x in a tree with root t costs, amortized, at most 3(log₂ size(t) − log₂ size(x)) + 1. Over any sequence, the total actual cost is the total amortized cost plus the drop in Φ, so m accesses take O(m log n) in all."),
            dict(type="p", text=f"**The simplest example,** from Tarjan's paper: a stack where each operation pops any number of items and then pushes one. A single operation can be slow (the program saw one with {stk['worst']} pushes and pops), but every item is popped at most once after it is pushed, so {stk['m']} operations do at most 2m = {stk['two']} pushes and pops; the program counted {stk['total']}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Judge a data structure by what a whole sequence of operations costs, not by its worst single step. Then a structure that does something cheap and silly-looking every time (move what you just used to the top) can be proved as good as one that keeps careful books."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A million accesses", toc="Measured", blocks=[
            dict(type="p", text=f"**The access lemma,** checked on every one of {lm['ops']} random accesses in a splay tree of {lm['n']} keys: rotations plus the change in potential never exceeded the bound (closest margin {lm['margin']}). In all, {lm['rot']} rotations, {lm['avg']} per access on average, against an average bound of {lm['bound']}. The potential ended at {lm['phi']}, of at most n log₂ n = {lm['phimax']}."),
            dict(type="p", text="**Sorted insertions, then reading in order.** A plain search tree becomes a path and visits 1 + 2 + … + n nodes; the splay tree's reading pass costs only a few nodes per key (the scanning theorem):"),
            dict(type="table", head=["Keys", "Plain tree, inserting", "Plain tree, reading", "Splay tree, inserting", "Splay tree, reading", "Balanced tree, reading"], num=[0, 1, 2, 3, 4, 5], rows=sorted_rows),
            dict(type="p", text=f"**Skewed use.** {zp['n']} keys, the k-th most popular used with probability proportional to 1/k, {zp['acc']} accesses. Average nodes visited per access: a perfectly balanced tree {zp['bal']}; the best fixed tree for the true frequencies (Knuth's dynamic programme) {zp['opt']}; the splay tree, which knows nothing about the frequencies, {zp['splay']}. Static optimality promises the splay tree is within a constant factor of the best fixed tree; here the factor is about {float(zp['splay']) / float(zp['opt']):.1f}."),
            dict(type="p", text=f"**Working sets.** A splay tree of {ws['n']} keys, but only a few keys are used, at random. The cost depends on how many are in use, not on the size of the tree; a balanced tree would visit about {ws['bal']} nodes every time:"),
            dict(type="table", head=["Keys in use", "Nodes per access", "log₂ of keys in use"], num=[0, 1, 2], rows=ws_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two papers in 1985", toc="The evidence", blocks=[
            dict(type="p", text="Daniel Sleator and Robert Tarjan, \"Self-Adjusting Binary Search Trees\" (AT&T Bell Laboratories; *Journal of the ACM* 32(3): 652–686, July 1985): \"The splay tree, a self-adjusting form of binary search tree, is developed and analyzed.\" Its operations have an amortized bound of O(log n), \"where by 'amortized time' is meant the time per operation averaged over a worst-case sequence of operations\", and \"for sufficiently long access sequences, splay trees are as efficient, to within a constant factor, as static optimum search trees.\" The efficiency comes \"from applying a simple restructuring heuristic, called splaying, whenever the tree is accessed.\" The access lemma (p. 658) and the dynamic optimality conjecture (p. 684) are in the paper; the conjecture is still open."),
            dict(type="p", text="Robert Tarjan, \"Amortized Computational Complexity\" (*SIAM Journal on Algebraic and Discrete Methods* 6(2), April 1985): \"A powerful technique in the complexity analysis of data structures is amortization, or averaging over time.\" It gives the banker's view (\"To each operation we allocate a certain number of credits\") and the physicist's view (a potential function), starting from the multipop stack, and argues that amortization leads to \"self-adjusting\" data structures."),
            dict(type="p", text="Wikipedia notes the trade-offs: \"recently accessed elements are quick to access again\" and \"Splay trees do not need to store any bookkeeping data\", but \"the height of a splay tree can be linear\", and because reads reshape the tree, concurrent use needs extra care."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Balanced trees, without the balance", toc="Full circle", blocks=[
            dict(type="p", text="Era 5's AVL trees guaranteed every search a short path by storing a balance in every node. Splay trees store nothing, let single searches be slow, and still match balanced trees over any sequence, and beat them when some keys are used more than others."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Reading 1,000 keys in sorted order: a plain search tree visited {s1['pread']} nodes; a balanced tree {s1['bal']}; the splay tree, which started as a path, {s1['sread']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("After inserting 1, 2, …, 15 in order into a splay tree, where is key 1?", "At the bottom of a path of 15 nodes: each insertion splayed the newest (largest) key to the root."),
            ("Why is one access allowed to be slow?", "Because it lowers the potential by about as much as it costs, paying for itself; only the total over a sequence is promised."),
            ("A splay tree of a million keys is used for only 10 of them. About how many nodes per access?", f"A few, about log₂ 10 plus a constant; the program measured {ws['rows'][1]['avg']} in a tree of {ws['n']}."),
            ("In the multipop stack, why can m operations do at most 2m pushes and pops?", "Each operation pushes once (m pushes), and each item can be popped at most once after its push (at most m pops)."),
            ("What does the dynamic optimality conjecture claim?", "That splay trees are, up to a constant factor, as good as any binary search tree algorithm on every sequence of accesses. It has not been proved."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Self-Adjusting Binary Search Trees (1985)", text="*Journal of the ACM* 32(3): 652–686, by Sleator and Tarjan of AT&T Bell Laboratories.",
                 draw=C.draw_manuscript, link="https://www.cs.princeton.edu/courses/archive/fall07/cos521/handouts/self-adjusting.pdf", link_text="The paper (PDF, on a Princeton course page)", licence="Drawn placeholder."),
            dict(title="Amortized Computational Complexity (1985)", text="*SIAM J. Alg. Disc. Meth.* 6(2), by Tarjan.",
                 draw=C.draw_manuscript, link="https://courses.cs.duke.edu/fall11/cps234/reading/Tarjan85_AmortizedComplexity.pdf", link_text="The paper (PDF, on a Duke course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "SplayTrees", d["checks"],
                           "the access lemma on every one of 1,000,000 splays (with the potential kept up to date and recounted at the end), sorted insertions against a plain tree, skewed use against Knuth's optimal fixed tree, working sets, and the multipop stack.",
                           ["void rotate(int x)", "void splay(int x)"]),
    ]
    return dict(
        title="Splay Trees and Amortized Analysis", date="1985",
        description="Era 7, topic 5 of The Algorithm Evolution Atlas: Sleator and Tarjan's splay trees, Tarjan's amortized analysis, the access lemma, and why a tree that rotates every used key to the root is as good as a balanced one.",
        lede="Balanced trees promise every search a short path, and pay with bookkeeping in every node. Sleator and Tarjan's splay tree keeps no books at all: it rotates whatever you touch to the top, and they proved that it is fast over any sequence of operations.",
        fieldnote=f"I inserted a thousand keys in order and the tree became a single long path. Then I read them in order: the first read walked a thousand nodes, and all thousand reads together walked {s1['sread']}. This species learned to judge its structures by the whole journey, not the worst step.",
        card=[("When", "1985"),
              ("Where", "AT&T Bell Laboratories"),
              ("What hurt", "Balanced trees' bookkeeping; judging each step alone"),
              ("The fix", "Splay every accessed key to the root; amortize"),
              ("Checked", f"The access lemma on {lm['ops']} splays, no exception")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `SplayTrees.java`.",
    )
