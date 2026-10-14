"""Era 5, topic 3: Huffman's codes. Every number is parsed from HuffmanCodes.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"phrase: (.+?) \((\d+) characters, _ is the space\) ; merges: (.*?) ; code: (.*?) ; (\d+) bits, against (\d+) with 3 bits each$", ln):
            merges = re.findall(r"(\S+)\((\d+)\) \+ (\S+)\((\d+)\) = (\S+)\((\d+)\)", m.group(3))
            codes = dict(re.findall(r"(\S)=([01]+)", m.group(4)))
            d["ph"] = dict(text=m.group(1), n=m.group(2), merges=merges, codes=codes, bits=m.group(5), fixed=m.group(6))
        elif ln.startswith("bits: "):
            d["bits"] = ln[6:]
        elif m := re.match(r"corpus: ([\d,]+) letters .*? entropy H = ([\d.]+) bits per letter ; five bits each: ([\d,]+) bits ; Shannon's code: ([\d,]+) \(([\d.]+) per letter\) ; Fano's splitting: ([\d,]+) \(([\d.]+)\) ; Huffman: ([\d,]+) \(([\d.]+)\) ; Huffman's codewords: (.*)$", ln):
            g = m.groups()
            d["corp"] = dict(n=g[0], h=g[1], five=g[2], sh=g[3], shp=g[4], fa=g[5], fap=g[6], hu=g[7], hup=g[8],
                             words=re.findall(r"(space|[A-Z]) ([01]+)", g[9]))
        elif m := re.match(r"roundtrip: the text encoded into ([\d,]+) bits", ln):
            d["rt"] = m.group(1)
        elif m := re.match(r"optimal: ([\d,]+) random alphabets of 2 to 8 symbols ; .*? Fano's splitting was worse in ([\d,]+) of them \(([\d.]+)%\) ; smallest such case, counts ([\d ]+): Fano ([01 ]+) = (\d+) bits, Huffman ([01 ]+) = (\d+) bits$", ln):
            g = m.groups()
            d["opt"] = dict(n=g[0], worse=g[1], pct=g[2], counts=g[3].split(), fano=g[4].split(), fbits=g[5], huff=g[6].split(), hbits=g[7])
        elif m := re.match(r"fibonacci: .*?\.\.\. (\d+) for (\d+) symbols: .*? get (\d+)-bit codewords", ln):
            d["fib"] = dict(last=m.group(1), n=m.group(2), longest=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def tree_layout(codes, counts):
    """Rebuild the code tree from the codewords: leaves left to right (0 before 1), internal nodes above."""
    nodes = {}
    for sym, code in codes.items():
        for k in range(len(code) + 1):
            nodes.setdefault(code[:k], dict(leaf=None, w=0))
        nodes[code]["leaf"] = sym
    for sym, code in codes.items():
        for k in range(len(code) + 1):
            nodes[code[:k]]["w"] += counts[sym]
    leaves = sorted([c for c in nodes if nodes[c]["leaf"] is not None])
    xs = {c: i for i, c in enumerate(leaves)}

    def x(c):
        if c in xs:
            return xs[c]
        xs[c] = (x(c + "0") + x(c + "1")) / 2
        return xs[c]
    x("")
    return nodes, xs, len(leaves)


def tree_svg(d):
    ph = d["ph"]
    counts = {}
    for ch in ph["text"]:
        k = "_" if ch == " " else ch
        counts[k] = counts.get(k, 0) + 1

    def draw(t, standalone):
        nodes, xs, nl = tree_layout(ph["codes"], counts)
        depth = max(len(c) for c in nodes)
        W, top, dy = 640, 40, 62
        sx = (W - 80) / max(1, nl - 1)
        pos = {c: (40 + xs[c] * sx, top + len(c) * dy) for c in nodes}
        o = []
        for c in nodes:
            if c:
                (x1, y1), (x2, y2) = pos[c[:-1]], pos[c]
                o.append(C.line(x1, y1, x2, y2, t["axis"], 1.5))
                o.append(C.text((x1 + x2) / 2 + (-9 if c[-1] == "0" else 9), (y1 + y2) / 2, c[-1], t["blue"], 12, "middle", 700))
        for c, nd in nodes.items():
            x, y = pos[c]
            if nd["leaf"]:
                o.append(C.rect(x - 17, y - 14, 34, 28, t["wash"], t["red"], 1.5, 5))
                o.append(C.text(x, y + 5, nd["leaf"], t["ink"], 15, "middle", 700))
                o.append(C.text(x, y + 30, f"{nd['w']}x", t["muted"], 11, "middle"))
                o.append(C.text(x, y + 45, c, t["blue"], 11, "middle"))
            else:
                o.append(C.circle(x, y, 14, t["surface"], t["ink2"], 1.5))
                o.append(C.text(x, y + 4, nd["w"], t["ink"], 12, "middle", 700))
        h = top + depth * dy + 60
        o.append(C.text(20, 20, f"{ph['text']}: counts at the leaves, sums in the circles, 0 = left, 1 = right", t["muted"], 12))
        return C.svg_doc(W, h, "".join(o), f"Huffman's tree for the phrase {ph['text']}", t, standalone, 0.55, W)
    return draw


HF_HTML = """
<div class="board hf-board">
  <div style="min-width:0">
    <label class="eyebrow" for="hf-in">Type a phrase</label>
    <input id="hf-in" type="text" value="MISSISSIPPI RIVER" spellcheck="false" autocomplete="off">
    <div class="hf-tree" id="hf-tree"></div>
  </div>
  <div style="min-width:0">
    <ol class="hf-steps" id="hf-steps"></ol>
    <div class="hf-codes" id="hf-codes"></div>
    <p class="say" id="hf-say" aria-live="polite"></p>
  </div>
</div>
"""

HF_CSS = """
.hf-board input{font:15px var(--mono);width:100%;box-sizing:border-box;padding:8px;margin-top:4px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink)}
.hf-tree{margin-top:10px;overflow-x:auto}
.hf-tree svg{display:block;max-width:100%;height:auto}
.hf-steps{margin:4px 0 8px;padding-left:2.2em;font:12.5px var(--mono);display:grid;gap:3px;max-height:220px;overflow-y:auto}
.hf-codes{display:flex;flex-wrap:wrap;gap:4px;font:12.5px var(--mono)}
.hf-codes span{border:1px solid var(--rule);border-radius:4px;padding:2px 5px}
"""

HF_JS = r"""
(() => {
  const inp = document.getElementById("hf-in");
  if (!inp) return;
  const NS = "http://www.w3.org/2000/svg";
  function build(s) {
    const order = [], count = {};
    for (const ch of s) { const k = ch === " " ? "_" : ch; if (!(k in count)) { count[k] = 0; order.push(k); } count[k]++; }
    let made = 0;
    let q = order.map(k => ({w: count[k], sym: k, order: made++, name: k}));
    const steps = [];
    if (q.length === 1) return {root: {w: q[0].w, zero: q[0], name: q[0].name}, steps, order, count};
    while (q.length > 1) {
      q.sort((a, b) => a.w - b.w || a.order - b.order);
      const a = q.shift(), b = q.shift();
      const c = {w: a.w + b.w, zero: a, one: b, order: made++, name: a.name + b.name};
      steps.push(`${a.name}(${a.w}) + ${b.name}(${b.w}) = ${c.w}`);
      q.push(c);
    }
    return {root: q[0], steps, order, count};
  }
  function codes(n, p, out) { if (n.sym !== undefined) { out[n.sym] = p || "0"; return; } codes(n.zero, p + "0", out); if (n.one) codes(n.one, p + "1", out); }
  function drawTree(root) {
    const leaves = [];
    (function walk(n, depth) { n.depth = depth; if (n.sym !== undefined) { n.x = leaves.length; leaves.push(n); return; } walk(n.zero, depth + 1); if (n.one) walk(n.one, depth + 1); n.x = n.one ? (n.zero.x + n.one.x) / 2 : n.zero.x; })(root, 0);
    let depth = 0; (function m(n) { depth = Math.max(depth, n.depth); if (n.zero) m(n.zero); if (n.one) m(n.one); })(root);
    const W = Math.max(260, leaves.length * 40 + 40), H = depth * 46 + 70, sx = (W - 40) / Math.max(1, leaves.length - 1 || 1);
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", `0 0 ${W} ${H}`); svg.style.width = "100%"; svg.style.maxWidth = W + "px";
    const X = n => 20 + (leaves.length === 1 ? (W - 40) / 2 : n.x * sx), Y = n => 20 + n.depth * 46;
    (function lines(n) { for (const [k, c] of [["0", n.zero], ["1", n.one]]) if (c) { sv("line", {x1: X(n), y1: Y(n), x2: X(c), y2: Y(c), stroke: "var(--axis)", "stroke-width": 1.5}, svg); const t = sv("text", {x: (X(n) + X(c)) / 2 + (k === "0" ? -8 : 8), y: (Y(n) + Y(c)) / 2, fill: "var(--blue)", "font-size": 11, "text-anchor": "middle"}, svg); t.textContent = k; lines(c); } })(root);
    (function dots(n) {
      if (n.sym !== undefined) { sv("rect", {x: X(n) - 13, y: Y(n) - 12, width: 26, height: 24, rx: 4, fill: "var(--wash)", stroke: "var(--red)"}, svg); const t = sv("text", {x: X(n), y: Y(n) + 5, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: "var(--ink)"}, svg); t.textContent = n.sym; const w = sv("text", {x: X(n), y: Y(n) + 26, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)"}, svg); w.textContent = n.w; return; }
      sv("circle", {cx: X(n), cy: Y(n), r: 11, fill: "var(--surface)", stroke: "var(--ink2)"}, svg); const t = sv("text", {x: X(n), y: Y(n) + 4, "text-anchor": "middle", "font-size": 10, fill: "var(--ink)"}, svg); t.textContent = n.w;
      if (n.zero) dots(n.zero); if (n.one) dots(n.one);
    })(root);
    return svg;
  }
  function show() {
    const s = inp.value.toUpperCase().replace(/[^A-Z ]/g, "").slice(0, 60);
    const say = document.getElementById("hf-say"), tree = document.getElementById("hf-tree"), ol = document.getElementById("hf-steps"), cd = document.getElementById("hf-codes");
    tree.innerHTML = ""; ol.innerHTML = ""; cd.innerHTML = "";
    if (!s) { say.textContent = "Type some letters."; return; }
    const {root, steps, order, count} = build(s);
    steps.forEach(x => { el("li", {}, ol).textContent = x; });
    const c = {}; codes(root, "", c);
    const total = [...s].reduce((a, ch) => a + c[ch === " " ? "_" : ch].length, 0);
    const k = order.length, fixed = Math.max(1, Math.ceil(Math.log2(k)));
    [...order].sort((a, b) => count[b] - count[a]).forEach(x => { el("span", {}, cd).textContent = `${x}=${c[x]}`; });
    tree.appendChild(drawTree(root));
    let H = 0; for (const x of order) { const p = count[x] / s.length; H -= p * Math.log2(p); }
    say.textContent = `${s.length} characters, ${k} different (_ is the space). Huffman's code: ${total} bits, ${(total / s.length).toFixed(3)} per character. Equal-length codes need ${fixed} bits each: ${fixed * s.length} bits. Entropy: ${H.toFixed(3)} bits per character, the floor no code can go below.`;
  }
  inp.addEventListener("input", show);
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Huffman's codes combined older ideas, and where they led")
    W = 210
    nodes = {
        "sh": (20, 20, "Shannon's entropy", "the floor: H bits per symbol", "Era 4 topic 12", "ink"),
        "fa": (395, 20, "Fano's splitting", "halve the probabilities, from the top", "MIT, 1949", "ink"),
        "tr": (770, 20, "Trees", "a prefix code is a path from the root", "", "ink"),
        "hu": (395, 170, "Huffman's code", "⊕ merge the two rarest, from the bottom", "MIT, 1951–1952", "red"),
        "pq": (20, 330, "Priority queues", "take the smallest, again and again", "the heap, topic 12", "ink"),
        "def": (395, 330, "DEFLATE", "the back end of zip files", "later", "ink"),
        "med": (770, 330, "JPEG and MP3", "a model, then prefix codes", "later", "ink"),
        "today": (395, 480, "Compression today", "files, pictures, sound, fax", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sh", "hu", ports=("bottom", "top:0.15"))
    D.edge("fa", "hu", ports=("bottom", "top"))
    D.edge("tr", "hu", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("hu", "pq", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("hu", "def", ports=("bottom", "top"))
    D.edge("hu", "med", ports=("bottom:0.9", "top:0.3"))
    D.edge("def", "today", ports=("bottom", "top"))
    D.edge("med", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: a likeness of ideas. The heap (1964) later made the repeated 'take the two smallest' fast.", "caption")
    return D


def chain(d):
    co, op = d["corp"], d["opt"]
    steps = [
        ("Five bits for every letter wastes space on rare letters",
         f"Shannon's code: about -log2 p bits for a letter of probability p ({co['shp']} bits per letter here)", "Era 4, topic 12"),
        (f"Shannon's lengths are rounded up and waste room: H is {co['h']}",
         f"Fano's splitting, from the top: {co['fap']} bits per letter", "MIT, 1949"),
        (f"Splitting from the top is sometimes wrong: worse in {op['pct']}% of {op['n']} small alphabets",
         f"Huffman, from the bottom: {co['hup']} bits per letter, and never beaten by any prefix code", "MIT, 1951"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from fixed lengths to the best prefix code")
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
    ph, co, op, fib = d["ph"], d["corp"], d["opt"], d["fib"]
    gap = float(co["hup"]) - float(co["h"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Shannon (Era 4) had shown that no code can beat the entropy, and Fano had a good way to approach it: split the symbols into two halves of nearly equal probability, and split again. Huffman built the tree the other way up, starting from the two rarest symbols. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Huffman's code. Blue: compression today."),
        ]),
        dict(id="build", eyebrow="Try it", title="Type a phrase and grow its tree", toc="Try it", blocks=[
            dict(type="p", text="Type any phrase. The page counts its letters, then repeatedly joins the two smallest counts into a new node (ties go to the older node, as in the program), and reads each letter's codeword off the path from the top: 0 for left, 1 for right. Compare its length with equal-length codes, and with the entropy, the floor that no code can go below."),
            dict(type="widget", html=HF_HTML, js=HF_JS, css=HF_CSS,
                 fallback=dict(type="svg", name="tree-phrase", draw=tree_svg(d), alt=f"Huffman's tree for the phrase {ph['text']}", width=640),
                 note="In the interactive edition you can type your own phrase."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Start from the rarest", toc="How it works", blocks=[
            dict(type="p", text=f"**Why the bottom?** The tree in the figure above is the one the program built for {ph['text']}; each circle holds the count of everything below it. In a best code the two rarest symbols have the longest codewords, and they can be made to differ only in the last bit. So join them into one imaginary symbol whose count is their sum, and solve the smaller problem the same way. Each join adds one bit to every symbol beneath it."),
            dict(type="table", head=["Merge", "Joined", "New count"], num=[0, 2],
                 rows=[[str(i + 1), f"{a} ({x}) + {b} ({y})", z] for i, (a, x, b, y, n, z) in enumerate(ph["merges"])]),
            dict(type="p", text=f"For {ph['text']} ({ph['n']} characters, _ is the space) the codewords are {', '.join(f'{k} = {v}' for k, v in ph['codes'].items())}. The phrase becomes {d['bits']}: {ph['bits']} bits, against {ph['fixed']} with three bits for each character (it has {len(ph['codes'])} different ones). No codeword is the beginning of another, so the bits can be cut back into letters without any separators."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do not decide the first bit first. Decide the last bit of the two rarest symbols, merge them, and repeat: the problem shrinks by one symbol at every step, and each step is safe."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Four codes for the same text", toc="Measured", blocks=[
            dict(type="p", text=f"The program coded the letters and spaces of this book's own field notes (Eras 1 to 3, {co['n']} characters, the same text Era 4's Shannon program measured):"),
            dict(type="table", head=["Code", "Bits for the whole text", "Bits per letter"], num=[1, 2],
                 rows=[["five bits for every letter", co["five"], "5.000"], ["Shannon's code (Era 4)", co["sh"], co["shp"]],
                       ["Fano's splitting", co["fa"], co["fap"]], ["Huffman's code", co["hu"], co["hup"]], ["entropy (the floor)", "", co["h"]]], hl=3),
            dict(type="p", text=f"Huffman's code is {gap:.3f} bits per letter above the entropy. Its codewords run from {co['words'][0][1]} for the space to {co['words'][-1][1]} for {co['words'][-1][0]}. The {d['rt']} bits were decoded again, letter for letter, by walking the tree from the top."),
            dict(type="p", text=f"**Best of all prefix codes.** For {op['n']} random alphabets of 2 to 8 symbols, the program searched every possible set of codeword lengths: Huffman's total matched the best every time. Fano's splitting was worse in {op['worse']} of them ({op['pct']}%). The smallest such case has counts {', '.join(op['counts'])}: Fano's code {' '.join(op['fano'])} needs {op['fbits']} bits, Huffman's {' '.join(op['huff'])} needs {op['hbits']}."),
            dict(type="p", text=f"**The worst shape.** With Fibonacci counts (1, 1, 2, 3, 5, … {fib['last']}) for {fib['n']} symbols, every merge joins the newest node with the next count, and the rarest symbols get {fib['longest']}-bit codewords, the longest any {fib['n']}-symbol code can need."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A term paper instead of an exam", toc="The evidence", blocks=[
            dict(type="p", text="\"In 1951, David A. Huffman and his MIT information theory classmates were given the choice of a term paper or a final exam. The professor, Robert M. Fano, assigned a term paper on the problem of finding the most efficient binary code.\" Huffman, \"unable to prove any codes were the most efficient, was about to give up\" when he found the method (Wikipedia). A classroom project in the MAA's *Convergence* adds: \"What Professor Fano did not tell his students was the fact that it was an open problem and that he was working on the problem himself.\""),
            dict(type="p", text="The paper, \"A Method for the Construction of Minimum-Redundancy Codes\", appeared in the *Proceedings of the IRE* 40(9): 1098–1101 (1952). Huffman (1925–1999) later worked at UC Santa Cruz, was a pioneer of mathematical origami, and received the IEEE Richard W. Hamming Medal in 1999."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Inside every zip file", toc="Full circle", blocks=[
            dict(type="p", text="Huffman codes are the last stage of DEFLATE, the method inside zip files, and prefix codes follow the modelling stage of JPEG pictures and MP3 sound. When Huffman died in 1999, his university said his codes \"are used in nearly every application that involves the compression and transmission of digital data\", naming fax machines, modems, computer networks and high-definition television."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Era 4's Shannon program coded this book's field notes in {co['sh']} bits. Huffman's procedure, on the same letters, needs {co['hu']}, and no code that gives each letter its own fixed codeword can do better."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Counts A 5, B 2, C 1, D 1. Which two are merged first, and then?", "C and D (1 + 1 = 2); then B and CD (2 + 2 = 4); then A and BCD (5 + 4 = 9)."),
            ("What are the codeword lengths in that example, and the total?", "A 1 bit, B 2 bits, C and D 3 bits: 5 + 4 + 3 + 3 = 15 bits, against 18 with 2 bits each."),
            ("Why must no codeword be the start of another?", "Otherwise a stream of bits could be cut into letters in two ways, and the reader could not tell which was meant."),
            ("Can Huffman's code ever beat the entropy?", "No. The entropy is a floor for any code; Huffman's code is the best prefix code, at most one bit per symbol above it."),
            ("Why does each merge take only the two smallest?", "The two rarest symbols belong at the deepest level; joining anything else first could push a common symbol deeper than it needs to be."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Method for the Construction of Minimum-Redundancy Codes (1952)", text="Huffman's paper in the Proceedings of the IRE, from his MIT term paper.",
                 draw=C.draw_manuscript, link="https://en.wikipedia.org/wiki/Huffman_coding", link_text="Wikipedia (the paper itself was not opened)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "HuffmanCodes", d["checks"],
                           f"the phrase and its tree, four codes on {co['n']} characters with a full decode, Huffman against every prefix code for {op['n']} random alphabets, and the Fibonacci worst case.",
                           ["static Node huffman(long[] w, String[] names)"]),
    ]
    return dict(
        title="Huffman's Codes", date="1951–1952",
        description="Era 5, topic 3 of The Algorithm Evolution Atlas: Huffman's minimum-redundancy codes, built by merging the two rarest symbols, compared with Shannon's and Fano's codes on this book's own text.",
        lede="Fano's students were offered a term paper instead of an exam: find the most efficient binary code. Huffman nearly gave up, then built the code tree from the bottom, joining the two rarest symbols again and again. No prefix code is shorter.",
        fieldnote=f"Seventeen characters, MISSISSIPPI RIVER: {ph['bits']} bits instead of {ph['fixed']}. On this book's field notes the code needs {co['hup']} bits a letter, {gap:.3f} above the floor Shannon proved. A student who wanted to avoid an exam found the best code there is, of its kind.",
        card=[("When", "Term paper 1951; paper 1952"),
              ("Where", "MIT, Robert Fano's course"),
              ("What hurt", "Codes near the entropy, none provably best"),
              ("The fix", "Merge the two rarest, repeat; read codes off the tree"),
              ("Result", f"{co['hup']} bits a letter; entropy {co['h']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `HuffmanCodes.java`.",
    )
