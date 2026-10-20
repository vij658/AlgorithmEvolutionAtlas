"""Era 7, topic 12: the Burrows-Wheeler transform. Every number is parsed from BurrowsWheeler.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"small: the rotations of (\w+), sorted: (.*?) ; last letters L = (\w+), the original is row I = (\d+) ; L has (\d+) runs of equal letters, the text (\d+)", ln):
            d["small"] = dict(word=m.group(1), rots=m.group(2).split(), L=m.group(3), I=int(m.group(4)), runsL=m.group(5), runsT=m.group(6))
        elif m := re.match(r"context: in the field notes, (\d+) places where \"he\" .*? ; the character before it: (.*?) ; so", ln):
            d["ctx"] = dict(count=m.group(1), top=m.group(2))
        elif m := re.match(r"notes: this book's field notes, ([\d,]+) bytes ; runs of equal letters: ([\d,]+) in the text, ([\d,]+) in L ; after move-to-front, ([\d.]+)% of the numbers are 0 and ([\d.]+)% are below 4 ; bits per byte: Huffman's code on single bytes ([\d.]+) ; Era 6's LZ77 ([\d.]+) .*? ; Deflate .*? ([\d.]+) ; Burrows-Wheeler, move-to-front, then Huffman ([\d.]+)", ln):
            d["notes"] = dict(n=m.group(1), runsT=m.group(2), runsL=m.group(3), zeros=m.group(4), small=m.group(5), huff=m.group(6), lz=m.group(7), defl=m.group(8), bwt=m.group(9))
        elif m := re.match(r"blocks: [^;]* ; (.*)$", ln):
            d["blocks"] = [dict(size=mm.group(1), bpb=mm.group(2)) for mm in re.finditer(r"blocks of ([\d,]+) bytes: ([\d.]+) bits per byte", m.group(1))]
        elif m := re.match(r"fmindex: [^;]* ; (.*?) ; (\d+) more patterns agree", ln):
            d["fm"] = dict(rows=[dict(p=mm.group(1).replace("_", " "), count=mm.group(2), steps=mm.group(3)) for mm in re.finditer(r"\"([^\"]+)\": (\d+) \((\d+) steps\)", m.group(1))], more=m.group(2))
        elif m := re.match(r"trips: ([\d,]+) random strings", ln):
            d["trips"] = m.group(1)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def lf_svg(d):
    """The sorted rotations of abracadabra, with the LF mapping drawn for the letter a."""
    sm = d["small"]
    rots, L = sm["rots"], sm["L"]
    F = "".join(r[0] for r in rots)

    def draw(t, standalone):
        o = []
        n = len(rots)
        W, H = 780, 90 + n * 26 + 50
        o.append(C.text(20, 26, f"The sorted rotations of {sm['word']}: the k-th a in L is the k-th a in F", t["ink"], 13, "start", 700))
        xF, xL, xF2, y0 = 130, 400, 640, 80
        o.append(C.text(xF, y0 - 26, "F", t["blue"], 13, "middle", 700))
        o.append(C.text(xL, y0 - 26, "L", t["red"], 13, "middle", 700))
        o.append(C.text(xF2, y0 - 26, "F again", t["blue"], 13, "middle", 700))
        lr, fr, lrank, frank = {}, {}, [], []
        for ch in L:
            lr[ch] = lr.get(ch, 0) + 1
            lrank.append(lr[ch])
        for ch in F:
            fr[ch] = fr.get(ch, 0) + 1
            frank.append(fr[ch])
        for j, r in enumerate(rots):
            y = y0 + j * 26
            if j == sm["I"]:
                o.append(C.rect(xF - 26, y - 16, xL - xF + 52, 22, t["wash"], t["ink"], 1.2, 3))
            o.append(C.text(xF - 40, y, str(j) + (" I" if j == sm["I"] else ""), t["ink"] if j == sm["I"] else t["muted"], 11.5, "end", 700 if j == sm["I"] else 400))
            o.append(C.text(xF, y, r[0], t["blue"], 15, "middle", 700))
            o.append(C.text((xF + xL) / 2, y, r[1:-1], t["axis"], 14, "middle"))
            o.append(C.text(xL, y, r[-1], t["red"], 15, "middle", 700))
            o.append(C.text(xF2, y, r[0], t["blue"], 15, "middle", 700))
            if r[-1] == "a":
                o.append(C.text(xL + 14, y, f"{lrank[j]}", t["red"], 10.5, "start"))
            if r[0] == "a":
                o.append(C.text(xF - 14, y, f"{frank[j]}", t["blue"], 10.5, "end"))
                o.append(C.text(xF2 + 14, y, f"{frank[j]}", t["blue"], 10.5, "start"))
        frows = [j for j, ch in enumerate(F) if ch == "a"]
        k = 0
        for j, ch in enumerate(L):
            if ch == "a":
                tgt = frows[k]
                k += 1
                y1, y2 = y0 + j * 26 - 5, y0 + tgt * 26 - 5
                o.append(C.line(xL + 30, y1, xF2 - 18, y2, t["red"], 1.4))
                ux, uy = (xF2 - 18) - (xL + 30), y2 - y1
                L_ = (ux * ux + uy * uy) ** 0.5
                ux, uy = ux / L_, uy / L_
                ex, ey = xF2 - 18, y2
                o.append(C.path(f"M{ex:.1f},{ey:.1f} L{ex - ux * 9 - uy * 4:.1f},{ey - uy * 9 + ux * 4:.1f} L{ex - ux * 9 + uy * 4:.1f},{ey - uy * 9 - ux * 4:.1f} Z", None, t["red"]))
        o.append(C.text(20, H - 28, "Small numbers count the a's from the top. On every row, L's letter comes just before F's in the text, so the a's in L", t["muted"], 12))
        o.append(C.text(20, H - 10, "are sorted by what follows them, exactly as the a's in F are: their order matches, 1 to 1, 2 to 2, and so on.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "The LF mapping on the sorted rotations of abracadabra", t, standalone, 0.55, 780)
    return draw


BW_HTML = """
<div class="board bw-board">
  <div style="min-width:0">
    <div class="controls"><label>Text <input id="bw-text" type="text" value="abracadabra" maxlength="24"></label><label>Search <input id="bw-pat" type="text" value="abra" maxlength="12"></label></div>
    <div class="bw-view scrollx" id="bw-view"></div>
  </div>
  <div style="min-width:0">
    <div class="bw-btns"><button type="button" class="primary" id="bw-inv">Invert one letter</button><button type="button" id="bw-search">Search one letter</button><button type="button" id="bw-reset">Start again</button></div>
    <div class="bw-stats" id="bw-stats"></div>
    <p class="say" id="bw-say" aria-live="polite"></p>
  </div>
</div>
"""

BW_CSS = """
.bw-board .controls input{width:100%;box-sizing:border-box}
.bw-board .controls label{flex:1 1 10em}
.bw-tbl{border-collapse:collapse;font:14px var(--mono);margin-top:4px}
.bw-tbl td{padding:2px 6px;border:none;text-align:center;color:var(--muted)}
.bw-tbl td.f{color:var(--blue);font-weight:700} .bw-tbl td.l{color:var(--red);font-weight:700}
.bw-tbl td.n{color:var(--muted);font-size:11px}
.bw-tbl tr.cur td{background:var(--wash)} .bw-tbl tr.cur td.l{background:var(--red);color:var(--on-red)}
.bw-tbl tr.rng td{background:var(--wash)} .bw-tbl tr.rng td.f{background:var(--blue);color:var(--on-blue)}
.bw-tbl tr.org td.n{color:var(--ink);font-weight:700}
.bw-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.bw-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px;word-break:break-all}
"""

BW_JS = r"""
(() => {
  const view = document.getElementById("bw-view");
  if (!view) return;
  const PROG = __PROG__;
  let s, rots, L, F, I, lf, C, occ, inv, row, rng, pk;
  function setup() {
    s = document.getElementById("bw-text").value || "a";
    const n = s.length;
    rots = Array.from({length: n}, (_, i) => s.slice(i) + s.slice(0, i)).map((r, i) => ({r, i})).sort((a, b) => a.r < b.r ? -1 : a.r > b.r ? 1 : a.i - b.i);
    L = rots.map(x => x.r[n - 1]).join(""); F = rots.map(x => x.r[0]).join(""); I = rots.findIndex(x => x.i === 0);
    const seen = {}, cnt = {}; [...L].forEach(c => cnt[c] = (cnt[c] || 0) + 1);
    C = {}; let acc = 0; Object.keys(cnt).sort().forEach(c => { C[c] = acc; acc += cnt[c]; });
    lf = [...L].map(c => { seen[c] = (seen[c] || 0) + 1; return C[c] + seen[c] - 1; });
    inv = ""; row = I; rng = null; pk = 0;
    draw(`The ${n} rotations of "${s}", sorted. F (blue) is the first column, L (red) the last; the transform keeps only L and the row of the original text.`);
  }
  function occBefore(c, j) { let k = 0; for (let x = 0; x < j; x++) if (L[x] === c) k++; return k; }
  function draw(msg) {
    view.innerHTML = "";
    const tb = el("table", {class: "bw-tbl"}, view);
    rots.forEach((x, j) => {
      const inRng = rng && j >= rng[0] && j < rng[1];
      const tr = el("tr", {class: (j === row && inv.length ? "cur " : "") + (inRng ? "rng " : "") + (j === I ? "org" : "")}, tb);
      el("td", {class: "n"}, tr, j === I ? `${j} I` : String(j));
      el("td", {class: "f"}, tr, x.r[0]);
      el("td", {}, tr, x.r.slice(1, -1));
      el("td", {class: "l"}, tr, x.r[x.r.length - 1]);
    });
    const st = document.getElementById("bw-stats"); st.innerHTML = "";
    el("div", {}, st, `L = ${L}, I = ${I}`);
    if (s === "abracadabra") el("div", {}, st, `the program: L = ${PROG.L}, I = ${PROG.I}`);
    let runs = 1; for (let k = 1; k < L.length; k++) if (L[k] !== L[k - 1]) runs++;
    el("div", {}, st, `runs of equal letters: ${runs} in L`);
    if (inv) el("div", {}, st, `rebuilt so far (from the end): ${inv}`);
    if (rng) el("div", {}, st, `rows starting with "${document.getElementById("bw-pat").value.slice(-pk)}": ${rng[1] - rng[0]}`);
    if (msg) document.getElementById("bw-say").textContent = msg;
  }
  document.getElementById("bw-inv").addEventListener("click", () => {
    if (inv.length >= s.length) { draw(`Done: "${inv}" is the original text, rebuilt from L and I alone.`); return; }
    rng = null;
    const c = L[row]; inv = c + inv; const next = lf[row];
    draw(`Row ${row}: its last letter "${c}" is the letter before the current one. It is the k-th "${c}" in L, so it sits in the k-th "${c}" row of F: row ${next}. Move there.`);
    row = next;
  });
  document.getElementById("bw-search").addEventListener("click", () => {
    const p = document.getElementById("bw-pat").value;
    inv = ""; row = I;
    if (!p) return;
    if (pk >= p.length || (rng && rng[0] >= rng[1])) { pk = 0; rng = null; }
    const c = p[p.length - 1 - pk];
    let lo = rng ? rng[0] : 0, hi = rng ? rng[1] : s.length;
    if (C[c] === undefined) { rng = [0, 0]; draw(`"${c}" does not occur: 0 matches.`); return; }
    lo = C[c] + occBefore(c, lo); hi = C[c] + occBefore(c, hi); rng = [lo, hi]; pk++;
    draw(pk === p.length ? `Done: "${p}" occurs ${hi - lo} time${hi - lo === 1 ? "" : "s"} (as a piece of the rotations), found in ${p.length} steps, one per letter, using only L.` :
      `Step ${pk}: the rows starting with "${p.slice(-pk)}" are ${lo} to ${hi - 1}. Next, look one letter further back.`);
  });
  document.getElementById("bw-reset").addEventListener("click", setup);
  document.getElementById("bw-text").addEventListener("input", setup);
  document.getElementById("bw-pat").addEventListener("input", () => { rng = null; pk = 0; draw("Press Search one letter: backward search reads the pattern from its last letter."); });
  setup();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the Burrows–Wheeler transform combined older ideas, and where it led")
    W = 210
    nodes = {
        "sort": (20, 20, "Sorting", "put the rotations in order", "Eras 4 and 5", "ink"),
        "mtf": (395, 20, "Move-to-front", "recent letters get small numbers", "", "ink"),
        "huf": (770, 20, "Huffman and Lempel–Ziv", "short codes; pointers to earlier copies", "Eras 5 and 6", "ink"),
        "bwt": (395, 180, "Block sorting", "⊕ keep the last column: similar contexts side by side", "Wheeler 1983; report 1994", "red"),
        "bz": (20, 340, "bzip2", "a widely used compressor built on it", "", "ink"),
        "fm": (770, 340, "The FM index", "⊕ count and find patterns from the last column", "Ferragina and Manzini, 2000", "ink"),
        "today": (395, 490, "Today", "Bowtie, BWA and SOAP2 align DNA reads to genomes", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sort", "bwt", ports=("bottom", "top:0.15"))
    D.edge("mtf", "bwt", ports=("bottom", "top"))
    D.edge("huf", "bwt", ports=("bottom", "top:0.85"), dashed=True, label="what it competed with", at=0.5, dx=8, anchor="start")
    D.edge("bwt", "bz", ports=("bottom:0.15", "top"))
    D.edge("bwt", "fm", ports=("bottom:0.85", "top"))
    D.edge("fm", "today", ports=("bottom", "top:0.85"))
    D.text(20, 615, "Today: alignment programs Wikipedia names as using the transform. Dashed: the methods it was measured against.", "caption")
    return D


def chain(d):
    nt, bl, fm = d["notes"], d["blocks"], d["fm"]
    steps = [
        (f"Fast compressors based on Lempel and Ziv compressed less than slow statistical models: {nt['lz']} bits per byte here for Era 6's LZ77",
         f"Sort the rotations, keep the last column, move-to-front, Huffman: {nt['bwt']} bits per byte", "Burrows and Wheeler, 1994"),
        ("A sorted, scrambled text looks impossible to undo",
         f"The LF mapping: the k-th copy of a letter in L is the k-th in F; all {d['trips']} random strings came back exactly", "the inverse"),
        (f"Small blocks lose the context: {bl[0]['bpb']} bits per byte in blocks of {bl[0]['size']} bytes",
         f"Use large blocks: {bl[-1]['bpb']} bits per byte for {bl[-1]['size']} bytes", "\"a few kilobytes\" at least"),
        ("Indexes for searching a text took many times its space",
         "The FM index: count a pattern from L alone, one step per letter", "Ferragina and Manzini, 2000"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a better compressor to a genome index")
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
    sm, cx, nt, bl, fm = d["small"], d["ctx"], d["notes"], d["blocks"], d["fm"]
    rot_rows = [[str(j), r[0], r[1:-1], r[-1]] for j, r in enumerate(sm["rots"])]
    comp_rows = [["Huffman's code on single bytes", nt["huff"]], ["LZ77 (Era 6's program)", nt["lz"]], ["Deflate (gzip's method, level 9)", nt["defl"]], ["Burrows–Wheeler, move-to-front, Huffman", nt["bwt"]]]
    bl_rows = [[b["size"], b["bpb"]] for b in bl]
    fm_rows = [[f"\"{r['p']}\"", r["count"], r["steps"]] for r in fm["rows"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Lempel and Ziv (Era 6) compressed by pointing back at earlier copies; Huffman (Era 5) gave common symbols short codes. Wheeler found a third way: sort every rotation of a block of text, keep only the last letter of each, and the letters come out grouped by the context that follows them, ready for move-to-front and Huffman. Ferragina and Manzini later used the same column as an index. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the transform. Blue: where it is used today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Sort, keep the last column, undo it", toc="Try it", blocks=[
            dict(type="p", text=f"Type a short text. The table shows its rotations, sorted: F in blue, L in red, and the row marked I holds the text itself. The transform keeps only L and I. Press Invert one letter to rebuild the text from L alone, backwards, by the LF mapping. Then type a pattern and press Search one letter: backward search narrows the range of rows that begin with longer and longer pieces of the pattern, looking only at L. For {sm['word']} the widget's L and I match the program's."),
            dict(type="widget", html=BW_HTML, js=BW_JS.replace("__PROG__", json.dumps(dict(L=sm["L"], I=sm["I"]))), css=BW_CSS,
                 fallback=dict(type="table", head=["Row", "F", "Middle", "L"], rows=rot_rows, hl=[sm["I"]]),
                 note="In the interactive edition you can transform your own text, invert it and search it."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="The last column remembers everything", toc="How it works", blocks=[
            dict(type="p", text=f"**The transform.** Write every rotation of the block, sort them, keep the last column L and the row I where the original sits. For {sm['word']}, L = {sm['L']} and I = {sm['I']}: the {sm['runsT']} runs of the text became {sm['runsL']} in L."),
            dict(type="p", text=f"**Why it groups letters.** Rotations that begin with the same context are sorted together, and L holds the letter just before each. In this book's field notes, \"he\" is preceded {cx['count']} times by: {cx['top']}. In L, those letters sit side by side."),
            dict(type="svg", name="lf", draw=lf_svg(d), alt="The LF mapping on the sorted rotations of abracadabra", width=780),
            dict(type="p", text="**Undoing it.** F is just L sorted. The LF mapping takes row j to the row whose F letter is the same letter as L[j], counting copies in order. Start at row I, read L, move by LF, and the text comes out backwards."),
            dict(type="p", text="**Compressing it.** Move-to-front replaces each letter by its position in a list of recently used letters, then moves it to the front; runs of the same letter become runs of zeros. A Huffman code then packs those small numbers into few bits."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Sorting by what comes after a letter gathers letters that share a context, which makes text easy to compress, and the sorted order is so regular that one column and one number are enough to rebuild everything, or to search it."),
        ]),
        dict(id="measured", eyebrow="Measured", title="This book's own text", toc="Measured", blocks=[
            dict(type="p", text=f"**Compression,** on this book's field notes ({nt['n']} bytes, the same text as Era 6's Lempel–Ziv program). Runs of equal letters: {nt['runsT']} in the text, {nt['runsL']} in L. After move-to-front, {nt['zeros']}% of the numbers were 0 and {nt['small']}% below 4."),
            dict(type="table", head=["Method", "Bits per byte"], num=[1], rows=comp_rows, hl=[3]),
            dict(type="p", text="**Block size.** The field notes cut into blocks, each transformed and coded on its own (32 bits per block to record I):"),
            dict(type="table", head=["Block size (bytes)", "Bits per byte"], num=[0, 1], rows=bl_rows),
            dict(type="p", text=f"**Searching.** Occurrences counted from L alone by backward search, one step per pattern letter, against scanning all {nt['n']} positions; {fm['more']} more random patterns agreed with scanning:"),
            dict(type="table", head=["Pattern", "Occurrences", "Steps"], num=[1, 2], rows=fm_rows),
            dict(type="p", text=f"**Round trips.** {d['trips']} random strings, 1 to 300 letters over alphabets of 1 to 26, and every block above, transformed and inverted: every one came back exactly."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A research report from Palo Alto", toc="The evidence", blocks=[
            dict(type="p", text="M. Burrows and D. J. Wheeler, \"A Block-sorting Lossless Data Compression Algorithm\", SRC Research Report 124 (Systems Research Center of Digital Equipment Corporation, Palo Alto, 10 May 1994): \"The algorithm works by applying a reversible transformation to a block of input text. The transformation does not itself compress the data, but reorders it to make it easy to compress with simple algorithms such as move-to-front coding.\" It achieves \"speed comparable to algorithms based on the techniques of Lempel and Ziv, but obtains compression close to the best statistical modelling techniques\", and \"The size of the input block must be large (a few kilobytes) to achieve good compression.\" \"The algorithm described here was discovered by one of the authors (Wheeler) in 1983 while he was working at AT&T Bell Laboratories, though it has not previously been published.\" On the Calgary Corpus they report mean bits per character of 3.63 for compress, 2.71 for gzip and 2.43 for theirs."),
            dict(type="p", text="Langmead's tutorial (2013) explains the LF mapping and backward search, and that in 2000 Ferragina and Manzini showed the transform with small auxiliary tables is a space-efficient index, the FM index. Wikipedia names bzip2 as a user, and Bowtie, BWA and SOAP2 as alignment programs \"that use the Burrows–Wheeler transform\"; Bowtie (Langmead and others, 2009) needs \"around 2.2GB for the human genome\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Compression, then search", toc="Full circle", blocks=[
            dict(type="p", text="Era 6's Lempel and Ziv and this era's Karp and Rabin treated compressing text and searching it as separate jobs. The Burrows–Wheeler transform does both with one column: the same L that compresses well also answers \"how many times does this pattern occur?\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"On the same {nt['n']} bytes, Era 6's LZ77 used {nt['lz']} bits per byte; the transform, with move-to-front and Huffman, {nt['bwt']}. And from that same L, \"the\" was counted ({next(r['count'] for r in fm['rows'] if r['p'] == 'the')} times) in 3 steps."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write the sorted rotations of \"banana\" and read off L.", "abanan, anaban, ananab, banana, nabana, nanaba: L = nnbaaa, and the text is row 3."),
            ("Why is F not stored?", "F is just the letters of L in sorted order, so it can be rebuilt from L."),
            ("Move-to-front on \"aaab\" with the list a, b, …: what numbers come out?", "0 0 0 1: three a's at the front, then b in position 1."),
            ("Why do small blocks compress worse?", "There are fewer rotations with each context, so letters are grouped less, and each block also pays for its own bookkeeping."),
            ("How many steps does backward search take for a pattern of 20 letters in a genome of 3 billion?", "20, one per pattern letter, whatever the genome's size (with the counting tables precomputed)."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="SRC Research Report 124 (1994)", text="\"A Block-sorting Lossless Data Compression Algorithm\", Burrows and Wheeler.",
                 draw=C.draw_manuscript, link="https://www.cl.cam.ac.uk/teaching/0304/DSAlgs/SRC-124.pdf", link_text="The report (PDF, on a Cambridge course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "BurrowsWheeler", d["checks"],
                           "the transform and its inverse on abracadabra, the field notes and every block of four sizes, compression against Huffman and Deflate, backward search against scanning for 506 patterns, and 2,000 random round trips.",
                           ["static byte[] inverse(byte[] L, int I)", "static int fmCount(byte[] p)"]),
    ]
    return dict(
        title="The Burrows–Wheeler Transform", date="1983–1994",
        description="Era 7, topic 12 of The Algorithm Evolution Atlas: Burrows and Wheeler's block-sorting transform, its inverse by the LF mapping, move-to-front compression, and the FM index used to align DNA.",
        lede="Sort every rotation of a block of text and keep only the last letter of each: the letters come out grouped by context, easy to compress, and, surprisingly, the original can be rebuilt from that one column.",
        fieldnote=f"I sorted the rotations of this book's own field notes. The {nt['runsT']} runs of letters became {nt['runsL']}, and the text compressed to {nt['bwt']} bits per byte, better than gzip's method on the same text. From the same column I could count any word without reading the text at all.",
        card=[("When", "Found 1983; published 1994"),
              ("Where", "AT&T Bell Laboratories; DEC Systems Research Center, Palo Alto"),
              ("What hurt", "Fast compressors compressed less than slow ones"),
              ("The fix", "Sort the rotations, keep the last column"),
              ("Checked", f"{nt['bwt']} bits per byte; {d['trips']} round trips exact")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BurrowsWheeler.java`.",
    )
