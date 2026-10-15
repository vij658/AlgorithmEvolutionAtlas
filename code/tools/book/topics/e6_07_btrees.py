"""Era 6, topic 7: B-trees. Every number is parsed from BTrees.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"small: pages of (\d+) to (\d+) keys \(k = (\d+)\) ; keys inserted in the order ([\d ]+) ; (.*) ; the tree, level by level: (.*) ; (\d+) splits, height (\d+)", ln):
            levels = [re.findall(r"\[([\d ]+)\]", lv) for lv in m.group(6).split(" / ")]
            d["small"] = dict(lo=m.group(1), hi=m.group(2), k=m.group(3), order=m.group(4).split(), steps=m.group(5).split(" ; "),
                              levels=[[p.split() for p in lv] for lv in levels], splits=m.group(7), height=m.group(8))
        elif ln.startswith("million: "):
            d["mil"] = re.findall(r"pages of (\d+) to (\d+) keys: height (\d+), ([\d.]+) pages read per search, ([\d,]+) pages, (\d+)% full", ln)
            m = re.match(r"million: ([\d,]+) random keys, ([\d,]+) searches .*? a perfectly balanced binary tree has (\d+) levels", ln)
            d["mil_n"] = dict(n=m.group(1), searches=m.group(2), binary=m.group(3))
        elif m := re.match(r"fill: pages of (\d+) to (\d+) keys ; keys inserted in random order: ([\d,]+) pages, ([\d.]+)% full on average ; the same keys inserted in sorted order: ([\d,]+) pages, ([\d.]+)% full", ln):
            d["fill"] = dict(lo=m.group(1), hi=m.group(2), rp=m.group(3), rf=m.group(4), sp=m.group(5), sf=m.group(6))
        elif m := re.match(r"delete: ([\d,]+) of the keys deleted .*? ; ([\d,]+) borrows from a neighbour, ([\d,]+) merges ; .*? every leaf is at depth (\d+), and all ([\d,]+) searches .*? ; ([\d,]+) pages, ([\d.]+)% full", ln):
            d["del"] = dict(n=m.group(1), borrows=m.group(2), merges=m.group(3), depth=m.group(4), searches=m.group(5), pages=m.group(6), full=m.group(7))
        elif ln.startswith("bounds: "):
            d["bounds"] = re.findall(r"k=(\d+), n=([\d,]+): ([\d.]+) <= (\d+) <= ([\d.]+)", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def tree_svg(d):
    lv = d["small"]["levels"]

    def draw(t, standalone):
        o = []
        W = 800
        H = 44 + len(lv) * 80 + 16
        pos = {}
        o.append(C.text(20, 22, f"The program's small B-tree: pages of {d['small']['lo']} to {d['small']['hi']} keys, every leaf at the same depth", t["ink"], 13, "start", 700))
        for li, pages in enumerate(lv):
            widths = [len(p) * 26 + 12 for p in pages]
            gap = 14
            total = sum(widths) + gap * (len(pages) - 1)
            x = (W - total) / 2
            y = 44 + li * 80
            for pi, p in enumerate(pages):
                w = widths[pi]
                col = t["red"] if li == 0 else (t["blue"] if li < len(lv) - 1 else t["ink2"])
                o.append(C.rect(x, y, w, 30, t["surface"], col, 1.6, 4))
                for ki, key in enumerate(p):
                    o.append(C.text(x + 6 + ki * 26 + 13, y + 20, key, t["ink"], 13, "middle", 700))
                    if ki:
                        o.append(C.line(x + 6 + ki * 26, y + 4, x + 6 + ki * 26, y + 26, t["axis"], 1))
                pos[(li, pi)] = (x, y, w, len(p))
                x += w + gap
        # links: page (li, pi) has len+1 children, taken in order from the next level
        for li in range(len(lv) - 1):
            child = 0
            for pi in range(len(lv[li])):
                x, y, w, nk = pos[(li, pi)]
                for c in range(nk + 1):
                    cx, cy, cw, _ = pos[(li + 1, child)]
                    o.append(C.line(x + 6 + c * 26, y + 30, cx + cw / 2, cy, t["axis"], 1.3))
                    child += 1
        o.append(C.text(20, H - 12, "Each key separates the keys of the children on its left and its right. A search reads one page per level.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A small B-tree", t, standalone, 0.55, 800)
    return draw


BT_HTML = """
<div class="board bt-board">
  <div style="min-width:0">
    <div class="bt-tree" id="bt-tree"></div>
  </div>
  <div style="min-width:0">
    <div class="bt-btns"><input type="number" id="bt-key" min="1" max="99" value="31" aria-label="Key"><button type="button" id="bt-ins">Insert</button><button type="button" id="bt-del">Delete</button></div>
    <div class="bt-btns"><button type="button" id="bt-rand">Insert a random key</button><button type="button" id="bt-reset">Start again</button></div>
    <div class="bt-stats" id="bt-stats"></div>
    <p class="say" id="bt-say" aria-live="polite"></p>
  </div>
</div>
"""

BT_CSS = """
.bt-tree svg{display:block;width:100%;height:auto}
.bt-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0;align-items:center}
.bt-btns input{width:5em;font:inherit;padding:3px}
.bt-stats{font:13px var(--mono);display:grid;gap:3px}
"""

BT_JS = r"""
(() => {
  const box = document.getElementById("bt-tree");
  if (!box) return;
  const K = 2, START = __START__;
  let root, log, seed = 1970;
  const leaf = () => ({keys: [], kids: null});
  function find(p, x) { let i = 0; while (i < p.keys.length && p.keys[i] < x) i++; return i; }
  function ins(p, x) {
    const i = find(p, x);
    if (p.keys[i] === x) return null;
    if (p.kids) {
      const up = ins(p.kids[i], x);
      if (!up || !up.length) return up;
      p.keys.splice(i, 0, up[0]); p.kids.splice(i + 1, 0, up[1]);
    } else p.keys.splice(i, 0, x);
    if (p.keys.length <= 2 * K) return [];
    const mid = p.keys[K], right = {keys: p.keys.slice(K + 1), kids: p.kids ? p.kids.slice(K + 1) : null};
    p.keys = p.keys.slice(0, K); if (p.kids) p.kids = p.kids.slice(0, K + 1);
    log.push(`the page splits; ${mid} moves up`);
    return [mid, right];
  }
  function insert(x) {
    const up = ins(root, x);
    if (up === null) { log.push(`${x} is already there`); return; }
    if (up.length) { root = {keys: [up[0]], kids: [root, up[1]]}; log.push("the root split: the tree grows a new root"); }
  }
  function del(p, x) {
    const i = find(p, x), here = p.keys[i] === x;
    if (!p.kids) { if (!here) return false; p.keys.splice(i, 1); return true; }
    let found;
    if (here) { let q = p.kids[i]; while (q.kids) q = q.kids[q.kids.length - 1]; const pred = q.keys[q.keys.length - 1]; p.keys[i] = pred; log.push(`${x} replaced by ${pred}, the largest key to its left`); found = del(p.kids[i], pred); }
    else found = del(p.kids[i], x);
    if (p.kids[i].keys.length < K) repair(p, i);
    return found;
  }
  function repair(p, i) {
    const c = p.kids[i];
    if (i > 0 && p.kids[i - 1].keys.length > K) { const l = p.kids[i - 1]; c.keys.unshift(p.keys[i - 1]); p.keys[i - 1] = l.keys.pop(); if (c.kids) c.kids.unshift(l.kids.pop()); log.push("a page borrows a key from its left neighbour"); }
    else if (i < p.keys.length && p.kids[i + 1].keys.length > K) { const r = p.kids[i + 1]; c.keys.push(p.keys[i]); p.keys[i] = r.keys.shift(); if (c.kids) c.kids.push(r.kids.shift()); log.push("a page borrows a key from its right neighbour"); }
    else { const j = i > 0 ? i - 1 : i, l = p.kids[j], r = p.kids[j + 1]; l.keys = l.keys.concat([p.keys[j]], r.keys); if (l.kids) l.kids = l.kids.concat(r.kids); p.keys.splice(j, 1); p.kids.splice(j + 1, 1); log.push("two pages merge, pulling down the key between them"); }
  }
  function remove(x) {
    const ok = del(root, x);
    if (!ok) log.push(`${x} is not in the tree`);
    if (!root.keys.length && root.kids) { root = root.kids[0]; log.push("the root emptied: the tree shrinks"); }
  }
  function levels() { const out = []; let lv = [root]; while (lv.length) { out.push(lv); lv = lv.flatMap(p => p.kids || []); } return out; }
  function show() {
    const L = levels(), W = 620, H = 30 + L.length * 70;
    box.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", `0 0 ${W} ${H}`); box.appendChild(svg);
    const pos = new Map();
    L.forEach((pages, li) => {
      const widths = pages.map(p => Math.max(1, p.keys.length) * 22 + 8), gap = 8;
      const total = widths.reduce((a, b) => a + b, 0) + gap * (pages.length - 1);
      let x = Math.max(4, (W - total) / 2); const y = 14 + li * 70;
      pages.forEach((p, pi) => {
        const w = widths[pi];
        sv("rect", {x, y, width: w, height: 26, rx: 3, fill: "var(--surface)", stroke: li === 0 ? "var(--red)" : p.kids ? "var(--blue)" : "var(--ink-2)", "stroke-width": 1.5}, svg);
        p.keys.forEach((k, ki) => { const t = sv("text", {x: x + 4 + ki * 22 + 11, y: y + 18, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg); t.textContent = k; });
        pos.set(p, [x, y, w]);
        x += w + gap;
      });
    });
    L.forEach(pages => pages.forEach(p => { if (!p.kids) return; const [x, y] = pos.get(p);
      p.kids.forEach((c, ci) => { const [cx, cy, cw] = pos.get(c); sv("line", {x1: x + 4 + ci * 22, y1: y + 26, x2: cx + cw / 2, y2: cy, stroke: "var(--axis)", "stroke-width": 1.2}, svg); }); }));
    const n = L.flat().reduce((a, p) => a + p.keys.length, 0);
    const st = document.getElementById("bt-stats"); st.innerHTML = "";
    el("div", {}, st, `${n} keys, ${L.flat().length} pages, height ${L.length}`);
    el("div", {}, st, `pages hold ${K} to ${2 * K} keys (the root 1 to ${2 * K})`);
    document.getElementById("bt-say").textContent = log.length ? log.join("; ") + "." : "Insert or delete a key.";
  }
  function reset() { root = leaf(); log = []; START.forEach(x => insert(x)); log = [`the program's ${START.length} keys, inserted in its order`]; show(); }
  const keyBox = document.getElementById("bt-key");
  document.getElementById("bt-ins").addEventListener("click", () => { const x = +keyBox.value; log = []; insert(x); if (!log.length) log.push(`${x} goes into its leaf; no page overflows`); show(); });
  document.getElementById("bt-del").addEventListener("click", () => { const x = +keyBox.value; log = []; remove(x); if (!log.length) log.push(`${x} removed from its leaf, which still holds enough keys`); show(); });
  document.getElementById("bt-rand").addEventListener("click", () => { seed = (seed * 1103515245 + 12345) % 2147483648; const x = 1 + Math.floor(seed / 2147483648 * 99); keyBox.value = x; log = [`insert ${x}`]; insert(x); show(); });
  document.getElementById("bt-reset").addEventListener("click", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How B-trees combined older ideas, and where they led")
    W = 210
    nodes = {
        "avl": (20, 20, "Balanced search trees", "about log₂ n steps per search", "AVL, Era 5, topic 11", "ink"),
        "disk": (395, 20, "Disks", "one access brings a whole page", "", "ink"),
        "idx": (770, 20, "Indexes of large files", "too big for main memory", "Boeing's \"Jumbo\" parts data", "ink"),
        "bt": (395, 180, "The B-tree", "⊕ pages of k to 2k keys; split, borrow, merge", "Bayer and McCreight, 1970–72", "red"),
        "db": (20, 340, "Relational databases", "the index under the tables", "topic 6", "ink"),
        "fs": (395, 340, "File systems", "HFS+, APFS, NTFS, ext4", "", "ink"),
        "nr": (770, 340, "Non-relational databases", "many use it too", "", "ink"),
        "today": (395, 490, "Today", "\"the standard index implementation in almost all relational databases\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("avl", "bt", ports=("bottom", "top:0.15"))
    D.edge("disk", "bt", ports=("bottom", "top"))
    D.edge("idx", "bt", ports=("bottom", "top:0.85"), label="the need", at=0.5, dx=8, anchor="start")
    D.edge("bt", "db", ports=("bottom:0.15", "top"))
    D.edge("bt", "fs", ports=("bottom", "top"))
    D.edge("bt", "nr", ports=("bottom:0.85", "top"))
    D.edge("db", "today", ports=("bottom", "top:0.3"))
    D.text(20, 615, "Uses as listed by Wikipedia (B-tree). The memoir's \"Jumbo\" is Bayer's own word for the Boeing programme whose parts data overwhelmed the computers.", "caption")
    return D


def chain(d):
    mn, mil, de, bd = d["mil_n"], d["mil"], d["del"], d["bounds"]
    big = next(r for r in mil if r[0] == "50")
    b50 = next(r for r in bd if r[0] == "50")
    steps = [
        (f"A balanced binary tree of {mn['n']} keys has {mn['binary']} levels: a disk read for each",
         f"Pages of {big[0]} to {big[1]} keys: height {big[2]}, {big[3]} pages read per search", "Bayer and McCreight"),
        ("Inserting keys can unbalance a tree, and rebalancing a tree on disk is costly",
         "Split a full page and pass its middle key up; grow only at the root, so all leaves stay at one depth", "insertion"),
        (f"Deleting {de['n']} keys could leave pages almost empty",
         f"Borrow from a neighbour ({de['borrows']} times) or merge ({de['merges']} times): every page still half full", "deletion"),
        ("How tall can such a tree ever get?",
         f"The rules bound it: for {b50[1]} keys in pages of 50 to 100, between {b50[2]} and {b50[4]}; it was {b50[3]}", "a guarantee, not a hope"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from binary trees to pages")
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
    sm, mn, mil, fl, de, bd = d["small"], d["mil_n"], d["mil"], d["fill"], d["del"], d["bounds"]
    start = "[" + ",".join(sm["order"]) + "]"
    mil_rows = [[f"{a} to {b}", h, r, p, f"{f}%"] for a, b, h, r, p, f in mil]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A balanced binary tree finds a key in about log₂ n steps; a disk delivers a whole page at a time, and each delivery is slow. Bayer and McCreight made each node of the tree a whole page, holding many keys, so that each slow read does as much work as possible. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the B-tree. Blue: where it is today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Grow and shrink a B-tree", toc="Try it", blocks=[
            dict(type="p", text=f"The program's small tree, with pages of {sm['lo']} to {sm['hi']} keys, built from its {len(sm['order'])} keys. Insert keys and watch full pages split and pass their middle key up, until the root itself splits and the tree grows a level. Delete keys and watch pages borrow from a neighbour or merge."),
            dict(type="widget", html=BT_HTML, js=BT_JS.replace("__START__", start), css=BT_CSS,
                 fallback=dict(type="table", head=["Keys per page", "Height", "Pages read per search", "Pages", "Full"], num=[1, 2, 3], rows=mil_rows, hl=2),
                 note=f"In the interactive edition you can insert and delete keys in a small B-tree. The table: {mn['n']} random keys in trees with pages of four sizes."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Pages that split and merge", toc="How it works", blocks=[
            dict(type="p", text="**Pages.** Every page holds between k and 2k keys in order (the root may hold fewer), and a page that is not a leaf has one more child than keys: the keys of the i-th child lie between the page's keys i − 1 and i. A search reads the root, finds where the key would go, reads that child, and so on down."),
            dict(type="p", text="**Insertion.** Put the key in its leaf. If the leaf now holds 2k + 1 keys, split it: the middle key moves up into the parent, and the two halves of k keys each become pages. The parent may overflow in turn; when the root splits, a new root is made above it. The tree grows at the top, so every leaf is always at the same depth."),
            dict(type="svg", name="small", draw=tree_svg(d), alt="A small B-tree", width=800,
                 caption=f"Built by inserting {' '.join(sm['order'])}: {sm['splits']} splits, height {sm['height']}."),
            dict(type="p", text="**Deletion.** Remove the key (from a leaf, or by replacing it with the largest key to its left). A page left with k − 1 keys borrows one from a neighbour, through the parent, if the neighbour can spare it; otherwise the two merge, pulling down the key that separated them."),
            dict(type="callout", kind="key", label="Key idea",
                 text="When each step is slow but brings a lot, make each step decide among many choices. With a hundred keys per page, a million keys are four pages deep."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A million keys", toc="Measured", blocks=[
            dict(type="p", text=f"{mn['n']} random keys, and {mn['searches']} searches, half of them for keys present. A perfectly balanced binary tree of that many keys has {mn['binary']} levels."),
            dict(type="table", head=["Keys per page", "Height", "Pages read per search", "Pages", "Full"], num=[1, 2, 3], rows=mil_rows, hl=2),
            dict(type="p", text=f"**How full.** With pages of {fl['lo']} to {fl['hi']} keys, keys inserted in random order filled the pages {fl['rf']}% on average ({fl['rp']} pages); the same keys inserted in sorted order filled them only {fl['sf']}% ({fl['sp']} pages), because every split leaves a half-full page behind that never receives another key."),
            dict(type="p", text=f"**Deletion.** {de['n']} keys deleted in random order: {de['borrows']} borrows from a neighbour and {de['merges']} merges. Afterwards every page still held 50 to 100 keys, every leaf was at depth {de['depth']}, and all {de['searches']} searches, for deleted and kept keys, answered correctly."),
            dict(type="p", text="**Bounds.** The rules alone limit the height h of a tree of n keys: log(n + 1) / log(2k + 1) ≤ h ≤ 1 + log((n + 1)/2) / log(k + 1). Every tree the program built kept within them:"),
            dict(type="table", head=["k", "Keys n", "Lower bound", "Height", "Upper bound"], num=[0, 1, 2, 3, 4], rows=[list(x) for x in bd]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="An idea at Boeing", toc="The evidence", blocks=[
            dict(type="p", text="Rudolf Bayer's memoir (in German) remembers it: \"Am weitaus wichtigsten war die Arbeit über B-Bäume im Herbst 1969\" (by far the most important was the work on B-trees in autumn 1969), and \"Ich erinnere mich noch genau, wie ich in das Büro meines Kollegen Ed McCreight spaziert bin\" (I remember exactly how I walked into my colleague Ed McCreight's office). The data processing of the time, he writes, had reached its limits in managing the many individual parts of Boeing's \"Jumbo\" programme. The work appeared as a Boeing technical report, at the 1970 ACM SIGFIDET Workshop on Data Description and Access, and, refereed, in *Acta Informatica* 1(3): 173–189 (1972)."),
            dict(type="p", text="Wikipedia: they wanted to \"efficiently manage index pages for large random-access files\", and \"Organization and maintenance of large ordered indices\" was first circulated in July 1970. They never said what the B stands for; suggestions include \"Boeing, balanced, between, broad, bushy, and Bayer\". McCreight said in 2013 that \"It has to do with Balance\", and reported Bayer's view: \"the more you think about what the B in B-Tree means, the better you understand B-Trees!\""),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Under every table", toc="Full circle", blocks=[
            dict(type="p", text="The relational model (topic 6) lets a question say what it wants and leaves the how to the system; the B-tree is very often the how. Wikipedia calls it \"the standard index implementation in almost all relational databases\", and it also organizes the files on many disks (HFS+, APFS, NTFS, ext4)."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The AVL tree of Era 5 balanced a binary tree by rotations. The B-tree balances by splitting and merging pages, and reads {next(r for r in mil if r[0] == '50')[3]} pages per search where a binary tree would need about {mn['binary']} levels."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With pages of 2 to 4 keys, insert 1, 2, 3, 4, 5 into an empty tree. What happens at 5?", "The leaf holds 1 2 3 4 5: it splits, 3 moves up to a new root, and the leaves are [1 2] and [4 5]."),
            ("Why does the tree grow at the root and not at the leaves?", "Splits push keys upward; only a split of the root adds a level, and it adds it above every leaf at once."),
            ("Why do sorted insertions leave pages half full?", "Each split leaves the left half behind, and later keys are all larger, so it never receives another key."),
            ("A page of 50 to 100 keys: how many pages must be read to find one of a million keys?", "About 4: each level divides the possibilities by 50 to 100."),
            ("When does deletion merge rather than borrow?", "When the neighbouring page has only k keys and cannot spare one."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Rudolf Bayer, Memoiren", text="The inventor's memoir, in German, at the Technical University of Munich.",
                 draw=C.draw_book, link="https://db.cit.tum.de/~bayer/Memoiren-Bayer.pdf", link_text="Memoir (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "BTrees", d["checks"],
                           "every rule (page sizes, key order, equal leaf depths) after every build and after half a million deletions, a million searches against the set of kept keys, and the height bounds for every tree.",
                           ["Object[] insert(Page p, long x)"]),
    ]
    return dict(
        title="B-Trees", date="1969–1972",
        description="Era 6, topic 7 of The Algorithm Evolution Atlas: Bayer and McCreight's B-trees, pages that split and merge, and why a million keys are four reads deep.",
        lede="A balanced binary tree finds a key among a million in about twenty steps. On a disk, each step is a slow trip. Bayer and McCreight made every node a whole page of keys, and the trip count fell to four.",
        fieldnote=f"I built trees of {mn['n']} keys with pages of four sizes, then deleted half the keys. With a hundred keys to a page, a search read {next(r for r in mil if r[0] == '50')[3]} pages on average, and through all the splits and merges every leaf stayed at the same depth.",
        card=[("When", "Idea 1969; report 1970; paper 1972"),
              ("Where", "Boeing Scientific Research Laboratories"),
              ("What hurt", "Indexes on disk: one slow access per tree step"),
              ("The fix", "Pages of k to 2k keys; split, borrow, merge"),
              ("Measured", f"{next(r for r in mil if r[0] == '50')[3]} pages per search, not {mn['binary']} levels")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BTrees.java`.",
    )
