"""Era 8, topic 9: Genome assembly with de Bruijn graphs. Every number is parsed from GenomeAssembly.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"exact: random genome of ([\d,]+) letters ; ([\d,]+) reads of (\d+) letters \(coverage (\d+)\) ; k = (\d+): ([\d,]+) distinct \d+-mers = arrows, ([\d,]+) points ; Euler's rule: ([\d,]+) balanced points, 1 start, 1 end ; .*? compare ([\d,]+) pairs of reads", ln):
            d["exact"] = dict(g=m.group(1), reads=m.group(2), rl=m.group(3), cov=m.group(4), k=m.group(5), arrows=m.group(6), points=m.group(7), bal=m.group(8), pairs=m.group(9))
        elif ln.startswith("coverage: "):
            d["cov"] = re.findall(r"coverage (\d+): (\d+) contigs?, longest ([\d,]+) letters, ([\d.]+)% of the 31-mers read", ln)
        elif m := re.match(r"repeat: .*?R the same (\d+) letters three times \(([\d,]+) letters\) ; .*? ; (\d+) contigs, .*? ; genomes that fit the words exactly: (\d+)", ln):
            d["repeat"] = dict(r=m.group(1), total=m.group(2), contigs=m.group(3), fits=m.group(4))
        elif m := re.match(r"errors: .*? ; ([\d,]+) different 31-mers seen: ([\d,]+) true, ([\d,]+) false ; seen once, twice, 3, 4, 5\+ times: true ([\d ]+), false ([\d, ]+) ; using every word: ([\d,]+) contigs ; keeping words seen at least (\d+) times keeps ([\d,]+) of ([\d,]+) true words and (\d+) false ones: (\d+) contigs?, the longest ([\d,]+) letters", ln):
            d["err"] = dict(seen=m.group(1), true=m.group(2), false=m.group(3), th=m.group(4).split(), fh=m.group(5).split(), raw=m.group(6), thr=m.group(7),
                            kept=m.group(8), of=m.group(9), fk=m.group(10), contigs=m.group(11), longest=m.group(12))
        elif ln.startswith("widget: "):
            m = re.search(r"genome ([ACGT]+) .*? seed (\d+)", ln)
            d["widget"] = dict(genome=m.group(1), rows=[dict(k=int(a), points=int(b), arrows=int(c), fits=int(e.replace(",", ""))) for a, b, c, e in
                                                         re.findall(r"k = (\d+): (\d+) points, (\d+) arrows, ([\d,]+) genomes? fits?", ln)])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def words_svg(d):
    g = d["widget"]["genome"][:9]
    k = 4

    def draw(t, standalone):
        o = []
        W, H = 760, 230
        o.append(C.text(20, 26, f"{g}, the start of the widget's genome, cut into 4-letter words: each word is an arrow between its halves", t["ink"], 12.5, "start", 700))
        nodes = [g[i:i + k - 1] for i in range(len(g) - k + 2)]
        bw, gap = 64, 33
        x0 = 20
        y = 110
        for i, n in enumerate(nodes):
            x = x0 + i * (bw + gap)
            o.append(C.rect(x, y - 20, bw, 40, t["surface"], t["blue"], 2))
            o.append(C.text(x + bw / 2, y + 5, n, t["ink"], 14, "middle", 700))
            if i + 1 < len(nodes):
                xa, xb = x + bw + 2, x + bw + gap - 3
                o.append(C.line(xa, y, xb - 6, y, t["ink"], 1.6))
                o.append(C.path(f"M{xb - 8},{y - 5} L{xb},{y} L{xb - 8},{y + 5} z", None, t["ink"]))
                o.append(C.text((xa + xb) / 2, y - 30, g[i:i + k], t["red"], 12.5, "middle", 700))
        o.append(C.text(20, 175, "Red: the 4-letter words (arrows). Blue: the 3-letter halves (points). Reading the arrows in order spells the genome;", t["ink"], 12.5))
        o.append(C.text(20, 195, "with all of a genome's words, the genome is a path that uses every arrow exactly once: an Eulerian path.", t["ink"], 12.5))
        return C.svg_doc(W, H, "".join(o), "Words of four letters as arrows between their halves", t, standalone, 0.55, 760)
    return draw


GA_HTML = """
<div class="board ga-board">
  <div style="min-width:0"><div class="ga-view" id="ga-view"></div></div>
  <div style="min-width:0">
    <div class="ga-row" role="group" aria-label="Word length k"><span class="lbl">Word length k</span><span id="ga-ks"></span></div>
    <div class="ga-row"><button type="button" class="primary" id="ga-walk">Walk the genome</button></div>
    <div class="ga-genome" id="ga-genome"></div>
    <div class="ga-stats" id="ga-stats"></div>
    <p class="say" id="ga-say" aria-live="polite"></p>
  </div>
</div>
"""

GA_CSS = """
.ga-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.ga-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin:6px 0}
.ga-row .lbl{font-size:13px;color:var(--muted);min-width:7em}
.ga-row button{font-size:13px;padding:3px 10px}
.ga-row button.on{background:var(--ink);color:var(--paper)}
.ga-genome{font:15px var(--mono);letter-spacing:.06em;margin:8px 0;word-break:break-all}
.ga-genome b{background:var(--yellow);color:var(--on-yellow)}
.ga-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

GA_JS = r"""
(() => {
  const view = document.getElementById("ga-view");
  if (!view) return;
  const G = __GENOME__, PROG = __PROG__;
  let k = 4, timer = null, at = -1;
  function graph(k) {
    const order = [], idx = new Map(), mult = new Map();
    const node = s => { if (!idx.has(s)) { idx.set(s, order.length); order.push(s); } return idx.get(s); };
    const path = [];
    for (let i = 0; i + k <= G.length; i++) {
      const a = node(G.slice(i, i + k - 1)), b = node(G.slice(i + 1, i + k));
      const key = a + ">" + b; mult.set(key, (mult.get(key) || 0) + 1); path.push([a, b]);
    }
    return {order, mult, path};
  }
  function countFits(gr) {
    const out = new Map();
    for (const [key, m] of gr.mult) { const [a, b] = key.split(">").map(Number); if (!out.has(a)) out.set(a, []); out.get(a).push([b, m]); }
    const cnt = new Map(); for (const [a, l] of out) for (const e of l) cnt.set(a + ">" + e[0], e[1]);
    let edges = 0; for (const m of gr.mult.values()) edges += m;
    const found = new Set(), start = gr.path[0][0];
    (function walk(v, spelled, left) {
      if (found.size >= 100000) return;
      if (left === 0) { found.add(spelled); return; }
      for (const [b] of out.get(v) || []) {
        const key = v + ">" + b, m = cnt.get(key);
        if (m > 0) { cnt.set(key, m - 1); walk(b, spelled + gr.order[b].slice(-1), left - 1); cnt.set(key, m); }
      }
    })(start, gr.order[start], edges);
    return found.size;
  }
  function draw(msg) {
    const gr = graph(k), n = gr.order.length, S = 420, cx = 210, cy = 210, R = 175;
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: `0 0 ${S} ${S}`, role: "img", "aria-label": "The de Bruijn graph"}, view);
    const pos = gr.order.map((_, i) => { const a = -Math.PI / 2 + 2 * Math.PI * i / n; return [cx + R * Math.cos(a), cy + R * Math.sin(a)]; });
    const onPath = new Set(); if (at >= 0) for (let i = 0; i <= at; i++) onPath.add(i);
    const defs = sv("defs", {}, svg);
    for (const [id, col] of [["ga-a", "var(--axis)"], ["ga-r", "var(--red)"]]) {
      const mk = sv("marker", {id, viewBox: "0 0 10 10", refX: 10, refY: 5, markerWidth: 9, markerHeight: 9, markerUnits: "userSpaceOnUse", orient: "auto"}, defs);
      sv("path", {d: "M0,0 L10,5 L0,10 z", fill: col}, mk);
    }
    const rad = n > 20 ? 5 : 8;
    gr.path.forEach(([a, b], i) => {
      const hot = onPath.has(i), stroke = hot ? "var(--red)" : "var(--axis)", w = hot ? 2.6 : 1.3, mark = `url(#${hot ? "ga-r" : "ga-a"})`;
      const [x1, y1] = pos[a], [x2, y2] = pos[b];
      if (a === b) { // a word like GGG: a loop on its point
        const ox = (x1 - cx) / R * 22, oy = (y1 - cy) / R * 22;
        sv("path", {d: `M${x1 + oy * 0.4},${y1 - ox * 0.4} C${x1 + ox * 2 + oy},${y1 + oy * 2 - ox} ${x1 + ox * 2 - oy},${y1 + oy * 2 + ox} ${x1 - oy * 0.4},${y1 + ox * 0.4}`, fill: "none", stroke, "stroke-width": w, "marker-end": mark}, svg);
        return;
      }
      const mx = (x1 + x2) / 2 + (cy - (y1 + y2) / 2) * 0.25, my = (y1 + y2) / 2 - (cx - (x1 + x2) / 2) * 0.25;
      const dx = x2 - mx, dy = y2 - my, L = Math.hypot(dx, dy), ex = x2 - dx / L * (rad + 2), ey = y2 - dy / L * (rad + 2);
      sv("path", {d: `M${x1},${y1} Q${mx},${my} ${ex},${ey}`, fill: "none", stroke, "stroke-width": w, "stroke-opacity": hot ? 1 : 0.85, "marker-end": mark}, svg);
    });
    gr.order.forEach((s, i) => {
      const [x, y] = pos[i];
      sv("circle", {cx: x, cy: y, r: rad, fill: "var(--blue)"}, svg);
      if (n <= 16) sv("text", {x: x + (x - cx) * 0.12, y: y + (y - cy) * 0.12 + 4, "text-anchor": "middle", "font-size": 11, fill: "var(--ink)"}, svg, s);
    });
    const fits = countFits(gr), pg = PROG.find(r => r.k === k);
    const gEl = document.getElementById("ga-genome");
    gEl.innerHTML = at < 0 ? G : `<b>${G.slice(0, at + k)}</b>${G.slice(at + k)}`;
    const st = document.getElementById("ga-stats"); st.innerHTML = "";
    el("div", {}, st, `points (${k - 1}-letter halves): ${n}`);
    el("div", {}, st, `arrows (${k}-letter words): ${gr.path.length}`);
    el("div", {}, st, `genomes that use every arrow once: ${fits.toLocaleString("en-US")}`);
    if (pg) el("div", {}, st, `the program: ${pg.points} points, ${pg.arrows} arrows, ${pg.fits.toLocaleString("en-US")}`);
    document.getElementById("ga-say").textContent = msg || (fits === 1 ? `With words of ${k} letters only one genome fits: the words decide it.` : `With words of ${k} letters, repeated short stretches make crossroads, and ${fits.toLocaleString("en-US")} different genomes use the same words.`);
  }
  const ks = document.getElementById("ga-ks");
  for (let kk = 3; kk <= 8; kk++) {
    const b = el("button", {type: "button", class: kk === k ? "on" : ""}, ks, String(kk));
    b.addEventListener("click", () => { k = kk; at = -1; if (timer) clearInterval(timer); [...ks.children].forEach(x => x.classList.toggle("on", x === b)); draw(); });
  }
  document.getElementById("ga-walk").addEventListener("click", () => {
    if (timer) clearInterval(timer);
    at = 0; draw("Walking the true genome: each step crosses one arrow and adds one letter.");
    timer = setInterval(() => { const gr = graph(k); if (at >= gr.path.length - 1) { clearInterval(timer); timer = null; draw("The walk used every arrow once and spelled the genome."); return; } at++; draw("Walking the true genome: each step crosses one arrow and adds one letter."); }, 180);
  });
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How de Bruijn assembly combined older ideas, and where it led")
    W = 210
    nodes = {
        "euler": (20, 20, "Euler's bridges", "a path using every bridge once", "Era 3", "ink"),
        "olc": (395, 20, "Overlap assembly", "reads as points: a Hamiltonian path", "overlap–layout–consensus", "ink"),
        "sbh": (770, 20, "k-tuples", "all short words of a sequence", "sequencing by hybridization", "ink"),
        "iw": (395, 180, "Idury and Waterman", "⊕ words as arrows between halves", "USC, 1995", "red"),
        "eu": (20, 340, "EULER", "⊕ Eulerian superpaths, error correction", "Pevzner, Tang, Waterman, 2001", "red"),
        "vel": (770, 340, "Velvet", "de Bruijn graphs for very short reads", "Zerbino and Birney, 2008", "ink"),
        "today": (395, 490, "Short-read assembly", "the method the short-read machines use", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("euler", "iw", ports=("bottom", "top:0.15"))
    D.edge("olc", "iw", ports=("bottom", "top"), label="replaced", at=0.5, dx=8, anchor="start")
    D.edge("sbh", "iw", ports=("bottom", "top:0.85"))
    D.edge("iw", "eu", ports=("bottom:0.15", "top"))
    D.edge("iw", "vel", ports=("bottom:0.85", "top"))
    D.edge("eu", "today", ports=("bottom", "left"))
    D.edge("vel", "today", ports=("bottom", "right"))
    D.text(20, 615, "Short-read assembly: Wikipedia says the de Bruijn approach is \"most widely applied to the short reads\".", "caption")
    return D


def chain(d):
    ex, rp, er = d["exact"], d["repeat"], d["err"]
    steps = [
        (f"Reads as points, overlaps as links: a Hamiltonian path; {ex['pairs']} pairs to compare",
         f"Words as arrows: an Eulerian path, found in linear time; the {ex['g']}-letter genome rebuilt exactly", "Idury and Waterman; Pevzner and colleagues"),
        (f"A repeat longer than the reads: {rp['fits']} genomes fit the same words",
         "Pairs of reads a known distance apart; EULER's 149 contigs fell to 91", "Pevzner, Tang and Waterman, 2001"),
        (f"Misread letters: {er['false']} false words against {er['true']} true ones",
         f"Keep words seen at least {er['thr']} times: {er['fk']} false words survive, {er['contigs']} contigs", "error correction by word counts"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from overlaps to words")
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
    ex, cv, rp, er, wg = d["exact"], d["cov"], d["repeat"], d["err"], d["widget"]
    cov_rows = [[c, n, l, p + "%"] for c, n, l, p in cv]
    err_rows = [["true words", *er["th"]], ["false words", *er["fh"]]]
    wg_rows = [[str(r["k"]), str(r["points"]), str(r["arrows"]), f"{r['fits']:,}"] for r in wg["rows"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Euler (Era 3) settled when a walk can cross every bridge exactly once. The first genome assemblers joined reads by their overlaps, which asks for a walk through every read once, a much harder problem. Idury and Waterman cut the reads into short words and made each word an arrow; Pevzner, Tang and Waterman turned that into an Eulerian path problem with error correction. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the de Bruijn method's two steps. Blue: what it became."),
        ]),
        dict(id="play", eyebrow="Try it", title="How long must the words be?", toc="Try it", blocks=[
            dict(type="p", text=f"A genome of 32 letters, {wg['genome']}, cut into all its words of k letters. Each word is an arrow from its first k − 1 letters to its last k − 1 letters (the points around the circle). Walk the genome and watch it cross every arrow once. Then count how many different 32-letter genomes use exactly the same words: with short words, repeated short stretches create crossroads and many genomes fit; long enough words leave only one. The widget counts by trying every walk, as the program does, and gets the same numbers."),
            dict(type="widget", html=GA_HTML, js=GA_JS.replace("__GENOME__", json.dumps(wg["genome"])).replace("__PROG__", json.dumps(wg["rows"])), css=GA_CSS,
                 fallback=dict(type="table", head=["k", "Points", "Arrows", "Genomes that fit"], num=[0, 1, 2, 3], rows=wg_rows),
                 note="In the interactive edition you can change k and walk the genome through its graph."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Every word once", toc="How it works", blocks=[
            dict(type="p", text="**Reads.** A sequencer reads short pieces of many copies of a genome, cut at random places. The genome must be put back together from the pieces, like a book from many shredded copies."),
            dict(type="p", text="**Overlaps (the old way).** Make each read a point and link two reads if the end of one overlaps the start of the other. The genome is then a path through every point once, a Hamiltonian path, for which no fast method is known; and every pair of reads must be compared."),
            dict(type="p", text="**Words (the new way).** Cut every read into all its words of k letters. Make the points the words of k − 1 letters, and draw one arrow for each k-letter word, from its first k − 1 letters to its last. The genome crosses every arrow exactly once: an Eulerian path. Euler's rule says such a path exists when every point has as many arrows in as out, except the two ends, and Hierholzer's method walks it in time proportional to the number of arrows."),
            dict(type="svg", name="words", draw=words_svg(d), alt="Four-letter words as arrows between three-letter halves", width=760),
            dict(type="p", text="**What goes wrong.** A stretch no read covered breaks the path into pieces (contigs). A repeat longer than the words creates crossroads where the path can go more than one way. A misread letter creates up to k false words, but each is seen once or twice while true words are seen many times, so rare words can be discarded first."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Change what the points are. Reads as points ask for a Hamiltonian path; words as arrows ask for an Eulerian one. The same data, rearranged, turns a problem with no known fast method into one Euler solved."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Twenty thousand letters from six thousand reads", toc="Measured", blocks=[
            dict(type="p", text=f"**Perfect reads.** A random genome of {ex['g']} letters and {ex['reads']} error-free reads of {ex['rl']} letters (coverage {ex['cov']}). With k = {ex['k']}: {ex['arrows']} different words (arrows) and {ex['points']} points; Euler's rule holds, with {ex['bal']} balanced points, one start and one end; Hierholzer's walk spells the genome exactly. An overlap graph would have compared {ex['pairs']} pairs of reads."),
            dict(type="p", text="**Fewer reads.** The same genome with lower coverage: gaps break the path into contigs, every one of them a true piece of the genome."),
            dict(type="table", head=["Coverage", "Contigs", "Longest (letters)", "Words read"], num=[0, 1, 2, 3], rows=cov_rows, hl=len(cov_rows) - 1),
            dict(type="p", text=f"**A repeat.** A genome X R Y R Z R W ({rp['total']} letters) with the same {rp['r']} letters R three times. Even with every word and its exact count, {rp['fits']} genomes fit: the true one and X R Z R Y R W. The graph stores R once, among {rp['contigs']} contigs. A repeat longer than the reads cannot be crossed by any method; the reads would have to be longer, or come in pairs a known distance apart."),
            dict(type="p", text=f"**Misread letters.** The same {ex['reads']} reads with 1% of their letters misread: {er['seen']} different 31-letter words, {er['true']} true and {er['false']} false. Using every word gives {er['raw']} contigs. How often each kind of word was seen:"),
            dict(type="table", head=["", "Once", "Twice", "3 times", "4 times", "5 or more"], num=[1, 2, 3, 4, 5], rows=err_rows),
            dict(type="p", text=f"Keeping only words seen at least {er['thr']} times keeps {er['kept']} of the {er['of']} true words and {er['fk']} false ones: {er['contigs']} contigs, the longest {er['longest']} letters, every one a true piece of the genome. (A false word seen twice is two reads misread the same way at the same place.)"),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="From hybridization to EULER", toc="The evidence", blocks=[
            dict(type="p", text="Idury and Waterman (University of Southern California), *Journal of Computational Biology* 2(2), 1995: reads and their reverse complements are cut into k-tuples; the vertices are the distinct (k − 1)-tuples, and each k-tuple is an edge from its prefix to its suffix; the reconstruction is \"not an exact Eulerian tour, but a variation of it\"; with k = 15 on simulated data with 0.5% to 3% errors, more than 99.8% of bases were called correctly."),
            dict(type="p", text="Pevzner, Tang (UC San Diego) and Waterman (USC), *PNAS*, 14 August 2001: assembly traditionally followed the \"overlap–layout–consensus\" paradigm, and \"there is still no polynomial algorithm for the solution of the notorious 'repeat problem'\"; in the de Bruijn graph it becomes an Eulerian path problem, solvable in linear time; correcting reads by the spectrum of solid words reduced errors \"by a factor of 35–50\"; on *Neisseria meningitidis* EULER gave 149 contigs with none misassembled, against 160 (17 misassembled) for Phrap, and mate pairs reduced them to 91. Wikipedia: \"It is impossible to assemble through a perfect repeat that is longer than the maximum read length\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Königsberg's bridges, in DNA", toc="Full circle", blocks=[
            dict(type="p", text="Euler answered a question about seven bridges in 1736 (Era 3) and proved that a walk crossing every bridge once exists exactly when the odd places number zero or two. Two and a half centuries later the same theorem, applied to millions of short words, became the standard way to read genomes from short reads. MinHash (topic 5) cuts documents into overlapping words in just the same way."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{ex['reads']} reads, {ex['arrows']} words, one walk: the {ex['g']}-letter genome, exactly. No pair of reads was ever compared."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write the 3-letter words of ACGTAC and the arrows they make between 2-letter points.", "ACG, CGT, GTA, TAC: arrows AC→CG, CG→GT, GT→TA, TA→AC; the walk AC CG GT TA AC spells ACGTAC."),
            ("In a de Bruijn graph of one genome, which points have one more arrow out than in?", "Only the start (the first k − 1 letters); the end has one more in than out; every other point is balanced."),
            ("Why do longer words make fewer genomes fit?", "A crossroads needs a repeated stretch of k − 1 letters; the longer k is, the rarer such repeats are."),
            ("A misread letter sits in the middle of a 100-letter read, with k = 31. How many false words can it create?", "Up to 31: every word that covers the misread position."),
            ("Why can't any method resolve a 300-letter repeat from 100-letter reads?", "No read reaches from the unique sequence before the repeat to the unique sequence after it, so nothing records which copy connects where."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="An Eulerian path approach to DNA fragment assembly (2001)", text="Pevzner, Tang and Waterman, *PNAS* 98(17).",
                 draw=C.draw_manuscript, link="https://pmc.ncbi.nlm.nih.gov/articles/PMC55524", link_text="The paper (PubMed Central)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "GenomeAssembly", d["checks"],
                           "Euler's rule at every point, the genome rebuilt exactly, every contig a true piece at every coverage, the two genomes that fit the repeat, the word counts with misread letters, and the widget's counts.",
                           ["static String euler(Map<String, List<String>> g)"]),
    ]
    return dict(
        title="Genome Assembly with de Bruijn Graphs", date="1995–2001",
        description="Era 8, topic 9 of The Algorithm Evolution Atlas: genome assembly by Eulerian paths in de Bruijn graphs (Idury and Waterman, 1995; Pevzner, Tang and Waterman, 2001), with repeats, coverage and misread letters.",
        lede="A genome can only be read in short pieces, and joining pieces by their overlaps asks for a path through every piece once, a problem with no known fast method. Cut the pieces into short words instead, make each word an arrow, and the genome becomes a path across every arrow once: the problem Euler solved.",
        fieldnote=f"I shredded a {ex['g']}-letter genome into {ex['reads']} reads and cut them into words of {ex['k']} letters. One walk across every word, the kind Euler described for the bridges of Königsberg, gave the genome back exactly. Then I hid a 300-letter repeat in another genome three times, and found {rp['fits']} genomes that fit the same words, with nothing in the reads to choose between them.",
        card=[("When", "Idury and Waterman 1995; EULER 2001"),
              ("Where", "University of Southern California; UC San Diego"),
              ("What hurt", "Overlap assembly is a Hamiltonian path problem, broken by repeats"),
              ("The fix", "Words as arrows: an Eulerian path in a de Bruijn graph"),
              ("Checked", f"{ex['g']} letters rebuilt exactly from {ex['reads']} reads")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `GenomeAssembly.java`.",
    )
