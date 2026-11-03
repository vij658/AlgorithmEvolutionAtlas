"""Era 9, topic 3: Word embeddings (word2vec). Every number is parsed from WordEmbeddings.java's output."""
import json
import re

import common as C
from diagrams import Diagram

GROUPS = {
    "country": ["france", "italy", "spain", "germany", "japan", "egypt", "peru", "kenya"],
    "capital": ["paris", "rome", "madrid", "berlin", "tokyo", "cairo", "lima", "nairobi"],
    "language": ["french", "italian", "spanish", "german", "japanese", "arabic", "quechua", "swahili"],
    "male": ["king", "man", "boy", "brother", "father", "prince"],
    "female": ["queen", "woman", "girl", "sister", "mother", "princess"],
    "role": ["crown", "adult", "school", "sibling", "parent", "palace"],
}


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"corpus: ([\d,]+) sentences, ([\d,]+) words, vocabulary of (\d+) ; .*? most frequent: (.*)$", ln):
            d["corpus"] = dict(sent=m.group(1), words=m.group(2), vocab=m.group(3), top=m.group(4))
        elif m := re.match(r"train: .*?d = (\d+), window (\d+), k = (\d+) .*?(\d+) passes ; gradient check: largest difference ([\d.eE+-]+) ; frequent words subsampled: ([\d,]+) of ([\d,]+) occurrences skipped ; ([\d,]+) \(centre, neighbour\) pairs ; share of noise draws for \"the\": ([\d.]+) instead of ([\d.]+)", ln):
            d["train"] = dict(d=m.group(1), win=m.group(2), k=m.group(3), passes=m.group(4), grad=m.group(5), skipped=m.group(6), occ=m.group(7),
                              pairs=m.group(8), the=m.group(9), the0=m.group(10))
        elif ln.startswith("near: "):
            d["near"] = re.findall(r"(\w+): (\w+) ([\d.]+), (\w+) ([\d.]+), (\w+) ([\d.]+)", ln.split(" ; ", 1)[1])
            d["ncontent"] = re.search(r"of the (\d+) content words", ln).group(1)
        elif ln.startswith("analogy: "):
            d["analogy"] = dict(rows=re.findall(r"(country:capital|country:language|male:female) (\d+) of (\d+)", ln),
                                all=re.search(r"all (\d+) of (\d+) \((\d+)%\)", ln).groups(),
                                rnd=re.search(r"random vectors: (\d+) of (\d+)", ln).groups(),
                                rome=re.search(r"paris - france \+ italy = (\w+)", ln).group(1),
                                queen=re.search(r"king - man \+ woman = (\w+)", ln).group(1))
        elif m := re.match(r"cost: .*?full softmax over (\d+) words ([\d,]+) ; negative sampling with k = (\d+): ([\d,]+) ; for a vocabulary of ([\d,]+) words and d = (\d+): ([\d,]+) against ([\d,]+)", ln):
            d["cost"] = m.groups()
        elif ln.startswith("widget: "):
            share = re.search(r"components, (\d+)% and (\d+)% of the spread", ln).groups()
            words = []
            for part in ln.split(" ; ")[1:]:
                w, x, y, vec = part.split(" ")
                words.append(dict(w=w, x=float(x), y=float(y), v=[float(t) for t in vec.split(",")]))
            d["widget"] = dict(share=share, words=words)
    d["checks"] = C.checks(text)
    return d


def group_of(w):
    return next(g for g, ws in GROUPS.items() if w in ws)


# ----------------------------------------------------------------------------------------------------------------------
def pca2(vecs):
    """The two main directions of a set of vectors (power iteration), and each vector's coordinates on them."""
    n, D = len(vecs), len(vecs[0])
    mean = [sum(v[k] for v in vecs) / n for k in range(D)]
    X = [[v[k] - mean[k] for k in range(D)] for v in vecs]
    pcs = []
    for c in range(2):
        u = [1.0] * D
        if c == 1:
            u[0] = -1.0
        for _ in range(300):
            nu = [0.0] * D
            for x in X:
                s = sum(a * b for a, b in zip(x, u))
                for k in range(D):
                    nu[k] += s * x[k]
            if c == 1:
                s = sum(a * b for a, b in zip(nu, pcs[0]))
                nu = [a - s * b for a, b in zip(nu, pcs[0])]
            nn = sum(a * a for a in nu) ** 0.5
            u = [a / nn for a in nu]
        pcs.append(u)
    return [(sum(a * b for a, b in zip(x, pcs[0])), sum(a * b for a, b in zip(x, pcs[1]))) for x in X]


def map_svg(d):
    by = {w["w"]: w["v"] for w in d["widget"]["words"]}
    A, B = GROUPS["country"], GROUPS["capital"]
    pts = pca2([by[x] for x in A + B])
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]

    def draw(t, standalone):
        W, H = 760, 480
        o = [C.text(20, 26, "Countries (blue) and capitals (red), projected on their own two main directions", t["ink"], 13, "start", 700)]
        x0, x1, y0, y1 = 60, 680, 60, 440
        sx = lambda v: x0 + (v - min(xs)) / (max(xs) - min(xs)) * (x1 - x0)
        sy = lambda v: y1 - (v - min(ys)) / (max(ys) - min(ys)) * (y1 - y0)
        for i in range(len(A)):
            (ax, ay), (bx, by_) = pts[i], pts[len(A) + i]
            o.append(C.line(sx(ax), sy(ay), sx(bx), sy(by_), t["muted"], 1.2))
        for i, name in enumerate(A + B):
            X, Y = sx(pts[i][0]), sy(pts[i][1])
            o.append(C.circle(X, Y, 5, t["blue"] if i < len(A) else t["red"]))
            o.append(C.text(X + 8, Y + 4, name, t["ink"], 12))
        o.append(C.text(20, 470, "Grey lines join each country to its capital: they run nearly parallel, which is what makes the analogy arithmetic work.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Country and capital vectors projected onto their two main directions", t, standalone, 0.55, 760)
    return draw


W2V_HTML = """
<div class="board w2v-board">
  <div style="min-width:0"><div class="w2v-view" id="w2v-view"></div></div>
  <div style="min-width:0">
    <div class="w2v-ana"><select id="w2v-a"></select> is to <select id="w2v-b"></select> as <select id="w2v-c"></select> is to <b id="w2v-d">?</b></div>
    <div class="w2v-btns"><button type="button" class="primary" id="w2v-go">Compute b − a + c</button><button type="button" id="w2v-rnd">A random analogy</button></div>
    <div class="w2v-list" id="w2v-list"></div>
    <p class="say" id="w2v-say" aria-live="polite"></p>
  </div>
</div>
"""

W2V_CSS = """
.w2v-board{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.w2v-board{grid-template-columns:1fr}}
.w2v-view svg{width:100%;height:auto;display:block;background:var(--wash)}
.w2v-ana{font:14px var(--mono);line-height:2.2}
.w2v-ana select{font:inherit;max-width:9em}
.w2v-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.w2v-list{font:13px var(--mono);display:grid;gap:2px}
"""

W2V_JS = r"""
(() => {
  const view = document.getElementById("w2v-view");
  if (!view) return;
  const WORDS = __WORDS__, GROUP = __GROUP__, PAIRS = __PAIRS__, GROUPS = __GROUPS__;
  const col = {country: "var(--blue)", capital: "var(--red)", language: "var(--yellow)", male: "var(--blue)", female: "var(--red)", role: "var(--muted)"};
  const idx = {}; WORDS.forEach((w, i) => idx[w.w] = i);
  ["w2v-a", "w2v-b", "w2v-c"].forEach(id => { const s = document.getElementById(id); WORDS.forEach(w => el("option", {value: w.w}, s, w.w)); });
  const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0), cos = (a, b) => dot(a, b) / Math.sqrt(dot(a, a) * dot(b, b));
  function pca(ids) {
    const D = WORDS[0].v.length, mean = new Array(D).fill(0);
    ids.forEach(i => WORDS[i].v.forEach((x, k) => mean[k] += x / ids.length));
    const X = ids.map(i => WORDS[i].v.map((x, k) => x - mean[k])), pcs = [];
    for (let c = 0; c < 2; c++) {
      let u = new Array(D).fill(1); if (c === 1) u[0] = -1;
      for (let it = 0; it < 200; it++) {
        let nu = new Array(D).fill(0);
        X.forEach(x => { const s = dot(x, u); x.forEach((a, k) => nu[k] += s * a); });
        if (c === 1) { const s = dot(nu, pcs[0]); nu = nu.map((a, k) => a - s * pcs[0][k]); }
        const n = Math.sqrt(dot(nu, nu)); u = nu.map(a => a / n);
      }
      pcs.push(u);
    }
    const out = {}; ids.forEach((i, r) => out[i] = [dot(X[r], pcs[0]), dot(X[r], pcs[1])]); return out;
  }
  function draw(hl, arrows) {
    const groups = [...new Set(hl.map(i => GROUP[WORDS[i].w]))];
    const ids = groups.flatMap(g => GROUPS[g].map(w => idx[w]));
    const P = pca(ids), xs = ids.map(i => P[i][0]), ys = ids.map(i => P[i][1]);
    const X = v => 40 + (v - Math.min(...xs)) / (Math.max(...xs) - Math.min(...xs) || 1) * 520, Y = v => 370 - (v - Math.min(...ys)) / (Math.max(...ys) - Math.min(...ys) || 1) * 340;
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 640 400", role: "img", "aria-label": "Word vectors of the chosen groups, in two dimensions"}, view);
    const defs = sv("defs", {}, svg), mk = sv("marker", {id: "w2v-arw", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse"}, defs);
    sv("path", {d: "M0,0 L10,5 L0,10 z", fill: "var(--ink)"}, mk);
    PAIRS.forEach(([A, B]) => { if (groups.includes(GROUP[A[0]]) && groups.includes(GROUP[B[0]])) A.forEach((a, k) => sv("line", {x1: X(P[idx[a]][0]), y1: Y(P[idx[a]][1]), x2: X(P[idx[B[k]]][0]), y2: Y(P[idx[B[k]]][1]), stroke: "var(--muted)", "stroke-width": 1}, svg)); });
    arrows.forEach(([p, q]) => sv("line", {x1: X(P[p][0]), y1: Y(P[p][1]), x2: X(P[q][0]), y2: Y(P[q][1]), stroke: "var(--ink)", "stroke-width": 2.2, "marker-end": "url(#w2v-arw)"}, svg));
    ids.forEach(i => {
      const w = WORDS[i], g = GROUP[w.w], on = hl.includes(i);
      sv("circle", {cx: X(P[i][0]), cy: Y(P[i][1]), r: on ? 6.5 : 4.5, fill: col[g], stroke: on ? "var(--ink)" : "none", "stroke-width": 2}, svg);
      sv("text", {x: X(P[i][0]) + 8, y: Y(P[i][1]) + 4, "font-size": on ? 13 : 11, "font-weight": on ? 700 : 400, fill: "var(--ink)"}, svg, w.w);
    });
  }
  function go() {
    const a = idx[document.getElementById("w2v-a").value], b = idx[document.getElementById("w2v-b").value], c = idx[document.getElementById("w2v-c").value];
    const q = WORDS[b].v.map((x, k) => x - WORDS[a].v[k] + WORDS[c].v[k]);
    const ranked = WORDS.map((w, i) => [i, cos(w.v, q)]).filter(([i]) => i !== a && i !== b && i !== c).sort((p, r) => r[1] - p[1]);
    const best = ranked[0][0];
    document.getElementById("w2v-d").textContent = WORDS[best].w;
    const list = document.getElementById("w2v-list"); list.innerHTML = "";
    ranked.slice(0, 5).forEach(([i, s], r) => el("div", {}, list, `${r + 1}. ${WORDS[i].w.padEnd(10)} cosine ${s.toFixed(3)}`));
    draw([a, b, c, best], [[a, b], [c, best]]);
    document.getElementById("w2v-say").textContent = `${WORDS[b].w} − ${WORDS[a].w} + ${WORDS[c].w} is nearest to ${WORDS[best].w}. The map shows only the groups involved, on their own two main directions; grey lines join matching pairs, and the bold arrows are a → b and c → the answer.`;
  }
  function rnd() {
    const P = PAIRS[Math.floor(Math.random() * PAIRS.length)];
    let i = Math.floor(Math.random() * P[0].length), j; do { j = Math.floor(Math.random() * P[0].length); } while (j === i);
    document.getElementById("w2v-a").value = P[0][i]; document.getElementById("w2v-b").value = P[1][i]; document.getElementById("w2v-c").value = P[0][j];
    go();
  }
  document.getElementById("w2v-go").addEventListener("click", go);
  document.getElementById("w2v-rnd").addEventListener("click", rnd);
  document.getElementById("w2v-a").value = "france"; document.getElementById("w2v-b").value = "paris"; document.getElementById("w2v-c").value = "italy";
  go();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 660, "How word2vec combined older ideas, and where it led")
    W = 210
    nodes = {
        "dist": (20, 20, "Distributional hypothesis", "a word is known by its company", "linguistics, 1950s", "ink"),
        "nn": (395, 20, "Neural language models", "words as learned vectors, slow", "2000s", "ink"),
        "huff": (770, 20, "Huffman's codes", "a tree for the hierarchical softmax", "Era 5", "ink"),
        "w2v": (395, 190, "word2vec", "⊕ shallow models, negative sampling, billions of words", "Mikolov and colleagues, Google, 2013", "red"),
        "bpe": (20, 360, "Subword tokens", "vectors for pieces of words", "topic 6, 2015", "blue"),
        "tf": (770, 360, "The Transformer", "every token starts as a vector", "topic 9, 2017", "blue"),
        "llm": (395, 520, "Language models", "embeddings learned with everything else", "after 2017", "ink"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("dist", "w2v", ports=("bottom", "top:0.15"))
    D.edge("nn", "w2v", ports=("bottom", "top"))
    D.edge("huff", "w2v", ports=("bottom", "top:0.85"))
    D.edge("w2v", "bpe", ports=("bottom:0.15", "top"))
    D.edge("w2v", "tf", ports=("bottom:0.85", "top"))
    D.edge("w2v", "llm", ports=("bottom", "top"))
    D.text(20, 645, "The distributional hypothesis is attributed to Firth; his text was not opened, so the box gives no quotation.", "caption")
    return D


def chain(d):
    c = d["cost"]
    steps = [
        ("A word was a symbol: nothing learned about \"cat\" carried to \"kitten\"",
         "Learn a vector for each word by predicting its neighbours", "skip-gram"),
        (f"The full softmax costs a pass over the whole vocabulary for every pair",
         f"Negative sampling: tell the real neighbour from {c[2]} random words", "Mikolov and colleagues, 2013"),
        ("\"the\" and \"a\" appear everywhere and teach little",
         "Subsample frequent words; draw noise from count^(3/4)", "the same paper"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from symbols to vectors")
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
    co, tr, an, cs, w = d["corpus"], d["train"], d["analogy"], d["cost"], d["widget"]
    rel = {"country:capital": "country → capital", "country:language": "country → language", "male:female": "male → female"}
    ana_rows = [[rel[k], a, b, f"{100 * int(a) / int(b):.0f}%"] for k, a, b in an["rows"]] + [["all", an["all"][0], an["all"][1], an["all"][2] + "%"], ["random vectors", an["rnd"][0], an["rnd"][1], f"{100 * int(an['rnd'][0]) / int(an['rnd'][1]):.0f}%"]]
    lang = next(r for r in an["rows"] if r[0] == "country:language")
    near_rows = [[q, f"{a} {x}", f"{b} {y}", f"{c} {z}"] for q, a, x, b, y, c, z in d["near"]]
    group = {w2: g for g, ws in GROUPS.items() for w2 in ws}
    pairs = [GROUPS["country"], GROUPS["capital"]], [GROUPS["male"], GROUPS["female"]], [GROUPS["country"], GROUPS["language"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Linguists had long held that a word is known by the company it keeps, and neural language models of the 2000s already learned a vector for each word, slowly. Mikolov and his colleagues at Google made the model shallow, replaced the expensive softmax by a cheap guessing game against random words, and trained on billions of words in a day."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: word2vec. Blue: later topics in this era where every token is a vector."),
        ]),
        dict(id="play", eyebrow="Try it", title="Arithmetic with words", toc="Try it", blocks=[
            dict(type="p", text=f"These are the program's {len(w['words'])} trained word vectors, {tr['d']} numbers each, drawn on two dimensions. Choose an analogy, *a is to b as c is to ?*; the page computes v(b) − v(a) + v(c) with all {tr['d']} numbers and shows the nearest words by cosine. Country to capital and male to female work well; try country to language, which this small model learned badly."),
            dict(type="widget", html=W2V_HTML, js=W2V_JS.replace("__WORDS__", json.dumps(w["words"])).replace("__GROUP__", json.dumps(group)).replace("__PAIRS__", json.dumps(pairs)).replace("__GROUPS__", json.dumps(GROUPS)), css=W2V_CSS,
                 fallback=dict(type="svg", name="map", draw=map_svg(d), alt="Countries and capitals: the vectors projected on two dimensions", width=760),
                 note="In the interactive edition you can pick any analogy and see the nearest words."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Predict the neighbours", toc="How it works", blocks=[
            dict(type="p", text="**Two vectors per word.** Every word w gets a vector v_w for when it is in the centre and a vector u_c for when it is a neighbour. The skip-gram model reads the text and, for every centre word, looks at the words within a small window around it."),
            dict(type="p", text="**Negative sampling.** For each real pair (w, c), push σ(v_w · u_c) towards 1, where σ(x) = 1/(1 + e^−x). Then draw k random noise words n and push σ(v_w · u_n) towards 0. One step of gradient descent per pair adjusts v_w, u_c and the u_n. The noise words are drawn in proportion to count^(3/4), which gives rarer words a little more chance than their counts would."),
            dict(type="p", text="**Subsampling.** Words like \"the\" and \"is\" are thrown away at random each time they appear, more often the more frequent they are, so the window reaches past them to words that say something."),
            dict(type="p", text="**Why analogies work.** Words used in similar company end up with similar vectors. If capitals share some company (\"city\", \"capital\") and each capital shares its country's own company (the language, the sentence with its country), then v(paris) is roughly *capital* + *france-ness*, v(france) is *nation* + *france-ness*, and the difference v(paris) − v(france) is about the same for every pair. Add it to v(italy) and you land near v(rome)."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do not tell the model what words mean; make it predict their neighbours. Meaning ends up as geometry: similar words close together, consistent relations as consistent directions."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Sixty words, two million pairs", toc="Measured", blocks=[
            dict(type="p", text=f"**The corpus**: {co['sent']} sentences written from patterns about 8 countries, their capitals and languages, and 6 pairs of words that differ by gender, each pair with a context word of its own: {co['words']} words, a vocabulary of {co['vocab']}. Most frequent: {co['top']}. A real corpus would be ordinary text, billions of words long; this one is small so that the program can check what the vectors learn."),
            dict(type="p", text=f"**Training**: d = {tr['d']}, window {tr['win']}, k = {tr['k']} noise words, {tr['passes']} passes. Subsampling skipped {tr['skipped']} of {tr['occ']} word occurrences; {tr['pairs']} centre-neighbour pairs were trained. Raising counts to the 3/4 power cut \"the\"'s share of the noise draws from {tr['the0']} to {tr['the']}. The gradient of the loss agreed with finite differences to {C.sci(tr['grad'])}."),
            dict(type="p", text=f"**Nearest words** (cosine of the angle between vectors), among the {d['ncontent']} content words:"),
            dict(type="table", head=["Word", "Nearest", "Second", "Third"], rows=near_rows),
            dict(type="p", text=f"**Analogies**: every pair of pairs within a relation (\"a is to b as c is to ?\"), answered by the word nearest to v(b) − v(a) + v(c), excluding a, b and c:"),
            dict(type="table", head=["Relation", "Right", "Asked", "Share"], num=[1, 2, 3], rows=ana_rows, hl=len(ana_rows) - 2),
            dict(type="p", text=f"v(paris) − v(france) + v(italy) is nearest to **{an['rome']}**; v(king) − v(man) + v(woman) is nearest to **{an['queen']}**. Not every relation is learned equally: country to language was answered {lang[1]} times of {lang[2]}."),
            dict(type="p", text=f"**The cost per training pair**: a full softmax over these {cs[0]} words needs {cs[1]} multiply-adds; negative sampling with k = {cs[2]} needs {cs[3]}. For a vocabulary of a million words and d = {cs[5]}: {cs[6]} against {cs[7]}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two papers from Google, 2013", toc="The evidence", blocks=[
            dict(type="p", text="Mikolov, Chen, Corrado and Dean (submitted 16 January 2013): \"it takes less than a day to learn high quality word vectors from a 1.6 billion words data set\", with \"state-of-the-art performance on our test set for measuring syntactic and semantic word similarities\". Mikolov, Sutskever, Chen, Corrado and Dean (October 2013): negative sampling with 5 to 20 noise words for small datasets and 2 to 5 for large ones, noise from the unigram distribution to the 3/4 power, subsampling of frequent words, phrases learned as tokens, and vectors that add (\"Russian\" + \"river\" near \"Volga River\")."),
            dict(type="p", text="Wikipedia: in skip-gram \"the model uses the current word to predict the surrounding window of context words\"; continuous bag-of-words is \"a 'fill in the blank' task\"; hierarchical softmax \"uses a Huffman tree\"; the second paper \"received the 2023 NeurIPS Test of Time Award\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Huffman's tree, in a language model", toc="Full circle", blocks=[
            dict(type="p", text="Word2vec's other speed trick, the hierarchical softmax, puts the vocabulary at the leaves of a Huffman tree (Era 5, topic 3), so frequent words sit near the root and a prediction costs a few steps down the tree instead of a pass over the whole vocabulary. The code meant to compress telegrams ended up organizing a neural network's output."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Nothing told the program that Paris is a capital. v(paris) − v(france) + v(italy) landed on {an['rome']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("In \"in paris they speak french\", with a window of 2, which neighbours does \"paris\" have?", "in, they, speak (one word to its left, two to its right within the sentence); \"french\" is three away."),
            ("Why train against random noise words instead of the whole vocabulary?", "The whole vocabulary costs a dot product per word for every pair; k noise words cost k + 1. The model only has to tell real neighbours from random ones."),
            ("Counts 10,000 and 100. What are their noise weights with the 3/4 power, and how does the ratio change?", "1,000 and about 31.6: the ratio falls from 100 to about 32, so rare words are drawn more often than their counts alone would give."),
            ("Why exclude a, b and c when answering an analogy?", "v(b) − v(a) + v(c) is often closest to b or c themselves; the question asks for a fourth word."),
            ("If two words never appear near each other but always appear near the same words, will their vectors be close?", "Yes: their vectors are both pulled towards the same neighbour vectors. This is the distributional idea."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Efficient Estimation of Word Representations in Vector Space (2013)", text="Mikolov, Chen, Corrado and Dean.",
                 draw=C.draw_manuscript, link="https://arxiv.org/abs/1301.3781", link_text="arXiv:1301.3781", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "WordEmbeddings", d["checks"],
                           "the gradient against finite differences, the noise distribution, the analogies against random vectors, and the two famous examples.",
                           ["static double[] pairStep(int w, int c, int[] neg, double lr)"]),
    ]
    return dict(
        title="Word Embeddings", date="2013",
        description="Era 9, topic 3 of The Algorithm Evolution Atlas: word2vec (Google, 2013), skip-gram with negative sampling, and the analogies that appear as directions in the vectors.",
        lede="To a computer a word was a symbol, related to no other. In 2013 a team at Google gave every word a vector and trained it to predict the word's neighbours. Similar words ended up close together, and relations became directions.",
        fieldnote=f"I wrote the program a little world in {co['sent']} sentences and let it predict neighbours. I never told it what a capital is. Afterwards, Paris minus France plus Italy was {an['rome']}, and king minus man plus woman was {an['queen']}. Countries and their languages, it understood much less well.",
        card=[("When", "January and October 2013"),
              ("Where", "Google"),
              ("What hurt", "Words were symbols with nothing in common"),
              ("The fix", "Vectors trained to predict neighbours, with negative sampling"),
              ("Checked", f"{an['all'][0]} of {an['all'][1]} analogies, against {an['rnd'][0]} for random vectors")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `WordEmbeddings.java`.",
    )
