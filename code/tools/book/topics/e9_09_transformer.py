"""Era 9, topic 9: The Transformer. Every number is parsed from Transformer.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram

KEYS = [chr(ord("A") + i) for i in range(16)]


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"gradient: .*?finite differences ([\d.eE+-]+)", ln):
            d["grad"] = m.group(1)
        elif ln.startswith("lookup: "):
            m = re.match(r"lookup: (\d+) \(key, value\) pairs then a query key ; (\d+) keys, (\d+) values ; d_model (\d+), d_k (\d+), ([\d,]+) parameters ; Adam rate ([\d.]+), ([\d,]+) steps of (\d+) sequences ; on 5,000 new sequences: attention ([\d.]+)% right, mean attention on the matching pair ([\d.]+) ; averaging the positions instead: ([\d.]+)% right \(one value in (\d+) by chance is ([\d.]+)%\) ; loss every 250 steps: attention ([\d.,]+) ; averaging ([\d.,]+)", ln)
            g = m.groups()
            d["lookup"] = dict(pairs=g[0], nk=g[1], nv=g[2], d=g[3], dk=g[4], params=g[5], lr=g[6], steps=g[7], batch=g[8], acc=g[9], att=g[10], avg=g[11], chance=g[13],
                               ca=[float(x) for x in g[14].split(",")], cv=[float(x) for x in g[15].split(",")])
        elif ln.startswith("scaling: "):
            d["scaling"] = re.findall(r"d_k (\d+) (scaled|unscaled): variance of q\.k (\d+), largest weight ([\d.]+), softmax slope ([\d.]+)", ln)
        elif ln.startswith("positions: "):
            d["pos"] = re.findall(r"(\d+) apart: ([\d.]+)", ln)
            d["pos_dev"] = re.search(r"same distance ([\d.eE+-]+)", ln).group(1)
        elif ln.startswith("cost: "):
            d["cost"] = re.findall(r"n ([\d,]+), d (\d+): attention ([\d,]+) multiply-adds in 1 step, recurrent ([\d,]+) in ([\d,]+) steps", ln)
        elif ln.startswith("weights:"):
            d["W"] = {}
            for part in ln.split(" ; ")[1:]:
                name, shape, vals = part.split(" ")
                r, c = map(int, shape.split("x"))
                v = [float(x) for x in vals.split(",")]
                d["W"][name] = [v[i * c:(i + 1) * c] for i in range(r)]
    d["checks"] = C.checks(text)
    return d


def forward(W, keys, vals, query):
    """The trained model's forward pass, the same arithmetic as Transformer.run."""
    mul = lambda M, x: [sum(a * b for a, b in zip(row, x)) for row in M]
    xs = [[a + b for a, b in zip(W["Ek"][k], W["Ev"][v])] for k, v in zip(keys, vals)]
    xq = W["Ek"][query]
    q = mul(W["Wq"], xq)
    dk = len(q)
    s = [sum(a * b for a, b in zip(q, mul(W["Wk"], x))) / math.sqrt(dk) for x in xs]
    mx = max(s)
    e = [math.exp(v - mx) for v in s]
    a = [v / sum(e) for v in e]
    vs = [mul(W["Wv"], x) for x in xs]
    o = [sum(a[i] * vs[i][t] for i in range(len(xs))) + xq[t] for t in range(len(xq))]
    lg = mul(W["Wo"], o)
    m2 = max(lg)
    p = [math.exp(v - m2) for v in lg]
    p = [v / sum(p) for v in p]
    return a, p


EXAMPLE = ([2, 9, 4, 13, 0, 7], [5, 11, 5, 3, 14, 8], 13)


# ----------------------------------------------------------------------------------------------------------------------
def attn_svg(d):
    keys, vals, query = EXAMPLE
    a, p = forward(d["W"], keys, vals, query)
    best = max(range(len(p)), key=lambda i: p[i])

    def draw(t, standalone):
        W, H = 760, 330
        o = [C.text(20, 26, f"The trained model reads six pairs and the query {KEYS[query]}; the bars are its attention weights", t["ink"], 13, "start", 700)]
        for i, (k, v) in enumerate(zip(keys, vals)):
            y = 50 + i * 36
            hit = k == query
            o.append(C.rect(30, y, 110, 28, t["paper"], t["red"] if hit else t["rule"], 2 if hit else 1, 3))
            o.append(C.text(85, y + 19, f"{KEYS[k]} → {v}", t["ink"], 14, "middle", 700 if hit else 400))
            o.append(C.rect(160, y + 4, 400 * a[i], 20, t["red"] if hit else t["blue"], None, 0, 2))
            o.append(C.text(170 + 400 * a[i], y + 19, f"{a[i]:.3f}", t["ink"], 12))
        o.append(C.text(30, 290, f"Query {KEYS[query]}: answer {best}, with probability {p[best]:.3f}", t["ink"], 14, "start", 700))
        o.append(C.text(20, 318, "Computed by the page from the program's trained weights, with the program's formula.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Attention weights of the trained model on one example", t, standalone, 0.55, 760)
    return draw


def scaling_svg(d):
    rows = d["scaling"]

    def draw(t, standalone):
        W, H = 760, 300
        o = [C.text(20, 26, "Ten random keys: the softmax's largest weight, with and without dividing by √d_k", t["ink"], 13, "start", 700)]
        dks = sorted({int(r[0]) for r in rows})
        for gi, dk in enumerate(dks):
            x0 = 80 + gi * 220
            o.append(C.text(x0 + 70, 260, f"d_k = {dk}", t["ink"], 13, "middle", 700))
            for si, kind in enumerate(["unscaled", "scaled"]):
                r = next(r for r in rows if int(r[0]) == dk and r[1] == kind)
                v = float(r[3])
                h = 190 * v
                x = x0 + si * 75
                col = t["muted"] if kind == "unscaled" else t["red"]
                o.append(C.rect(x, 240 - h, 60, h, col, None, 0, 2))
                o.append(C.text(x + 30, 234 - h, f"{v:.2f}", t["ink"], 12, "middle"))
                o.append(C.text(x + 30, 278, kind, t["muted"], 11, "middle"))
        o.append(C.line(60, 240, 720, 240, t["rule"], 1))
        o.append(C.text(20, 296, "A weight near 1 means the softmax has picked one key and passes almost no gradient to the others.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Largest softmax weight with and without scaling", t, standalone, 0.55, 760)
    return draw


TF_HTML = """
<div class="board tf-board">
  <div style="min-width:0">
    <div class="tf-h">Six (key, value) pairs</div>
    <div class="tf-pairs" id="tf-pairs"></div>
    <div class="tf-q">Query key: <select id="tf-query"></select></div>
    <div class="tf-btns"><button type="button" class="primary" id="tf-rand">Random sequence</button><button type="button" id="tf-dup">Make two keys equal</button></div>
  </div>
  <div style="min-width:0">
    <div class="tf-h">Attention weights</div>
    <div class="tf-bars" id="tf-bars"></div>
    <div class="tf-h">The model's answer</div>
    <div class="tf-out" id="tf-out"></div>
    <p class="say" id="tf-say" aria-live="polite"></p>
  </div>
</div>
"""

TF_CSS = """
.tf-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:18px}
@media (max-width:760px){.tf-board{grid-template-columns:1fr}}
.tf-h{font-size:12px;font-weight:700;color:var(--muted);margin:6px 0 4px}
.tf-pairs{display:grid;grid-template-columns:repeat(3,auto);gap:6px 10px;justify-content:start;font:13px var(--mono)}
.tf-pairs select,.tf-q select{font:inherit}
.tf-q{font:13px var(--mono);margin:10px 0}
.tf-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.tf-bars{font:12.5px var(--mono);display:grid;gap:3px}
.tf-bar{display:grid;grid-template-columns:4.5em 1fr;align-items:center;gap:6px}
.tf-bar>span:last-child{display:flex;align-items:center;gap:6px}
.tf-bar span.b{display:block;height:14px;background:var(--blue);flex:none}
.tf-bar span.b.hit{background:var(--red)}
.tf-out{font:14px var(--mono)}
"""

TF_JS = r"""
(() => {
  const host = document.getElementById("tf-pairs");
  if (!host) return;
  const W = __W__, K = "ABCDEFGHIJKLMNOP".split(""), P = 6;
  let seed = 5;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const mul = (M, x) => M.map(r => r.reduce((s, w, j) => s + w * x[j], 0));
  const ks = [], vs = [];
  for (let i = 0; i < P; i++) {
    const wrap = el("span", {}, host);
    const k = el("select", {id: `tf-k${i}`, "aria-label": `key ${i + 1}`}, wrap); K.forEach((c, j) => el("option", {value: j}, k, c));
    el("span", {}, wrap, " → ");
    const v = el("select", {id: `tf-v${i}`, "aria-label": `value ${i + 1}`}, wrap); for (let j = 0; j < 16; j++) el("option", {value: j}, v, String(j));
    ks.push(k); vs.push(v); k.addEventListener("change", go); v.addEventListener("change", go);
  }
  const qs = document.getElementById("tf-query"); K.forEach((c, j) => el("option", {value: j}, qs, c)); qs.addEventListener("change", go);
  function go() {
    const keys = ks.map(s => +s.value), vals = vs.map(s => +s.value), q = +qs.value;
    const xs = keys.map((k, i) => W.Ek[k].map((a, t) => a + W.Ev[vals[i]][t])), xq = W.Ek[q];
    const qq = mul(W.Wq, xq), s = xs.map(x => mul(W.Wk, x).reduce((a, b, t) => a + b * qq[t], 0) / Math.sqrt(qq.length));
    const mx = Math.max(...s), e = s.map(v => Math.exp(v - mx)), z = e.reduce((a, b) => a + b), a = e.map(v => v / z);
    const v = xs.map(x => mul(W.Wv, x)), h = xq.map((x0, t) => x0 + a.reduce((acc, ai, i) => acc + ai * v[i][t], 0));
    const lg = mul(W.Wo, h), m2 = Math.max(...lg), pe = lg.map(x => Math.exp(x - m2)), pz = pe.reduce((x, y) => x + y), p = pe.map(x => x / pz);
    const best = p.indexOf(Math.max(...p));
    const bars = document.getElementById("tf-bars"); bars.innerHTML = "";
    a.forEach((w, i) => { const row = el("div", {class: "tf-bar"}, bars); el("span", {}, row, `${K[keys[i]]} → ${vals[i]}`); const c = el("span", {}, row); el("span", {class: "b" + (keys[i] === q ? " hit" : ""), style: `width:${60 * w}%`}, c); el("span", {}, c, w.toFixed(3)); });
    const top = p.map((x, i) => [i, x]).sort((x, y) => y[1] - x[1]).slice(0, 3);
    document.getElementById("tf-out").textContent = top.map(([i, x]) => `${i}: ${(100 * x).toFixed(1)}%`).join("   ");
    const hits = keys.filter(k => k === q).length;
    document.getElementById("tf-say").textContent = hits === 0
      ? `The query ${K[q]} matches no key, a case the model never saw in training: its attention spreads out and its answer is a guess.`
      : hits > 1 ? `${hits} pairs have the key ${K[q]}, a case never seen in training. Attention on them: ${keys.map((k, i) => k === q ? (100 * a[i]).toFixed(1) + "%" : null).filter(Boolean).join(" and ")}; the model answers ${best} (${(100 * p[best]).toFixed(1)}%).`
      : `The query ${K[q]} matches one key; the model puts ${(100 * a[keys.indexOf(q)]).toFixed(1)}% of its attention there and answers ${best}.`;
  }
  function rand() {
    const pool = [...Array(16).keys()];
    for (let i = 15; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [pool[i], pool[j]] = [pool[j], pool[i]]; }
    ks.forEach((s, i) => s.value = pool[i]); vs.forEach(s => s.value = Math.floor(rnd() * 16));
    qs.value = pool[Math.floor(rnd() * P)]; go();
  }
  document.getElementById("tf-rand").addEventListener("click", rand);
  document.getElementById("tf-dup").addEventListener("click", () => { const q = qs.value; const i = ks.findIndex(s => s.value === q); const j = (i + 1) % P; ks[j].value = q; go(); });
  rand();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How the Transformer combined older ideas, and where it led")
    W = 220
    nodes = {
        "rnn": (20, 20, "Recurrent networks", "read one word at a time", "Era 7; the LSTM, Era 8", "ink"),
        "att": (265, 20, "Attention for translation", "look back at every input word", "Bahdanau, Cho and Bengio, 2014", "ink"),
        "emb": (510, 20, "Word vectors and subwords", "every token a learned vector", "topics 3 and 6", "ink"),
        "res": (755, 20, "Residual connections", "add each layer's input to its output", "topic 7, 2015", "ink"),
        "tf": (387, 200, "The Transformer", "⊕ attention only, many heads, positions as sinusoids", "Vaswani and seven co-authors, Google, 2017", "red"),
        "flash": (140, 380, "FlashAttention", "the same attention, computed in tiles", "topic 12, 2022", "blue"),
        "lm": (635, 380, "Language models", "stacks of Transformer layers", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("rnn", "tf", ports=("bottom", "top:0.1"))
    D.edge("att", "tf", ports=("bottom", "top:0.37"))
    D.edge("emb", "tf", ports=("bottom", "top:0.63"))
    D.edge("res", "tf", ports=("bottom", "top:0.9"))
    D.edge("tf", "flash", ports=("bottom:0.2", "top"))
    D.edge("tf", "lm", ports=("bottom:0.8", "top"))
    return D


def chain():
    steps = [
        ("A translator squeezed the whole sentence into one fixed-length vector",
         "Attention: at each output word, look back at every input word", "Bahdanau, Cho and Bengio, 2014"),
        ("The recurrent network underneath still reads one word after another",
         "Drop the recurrence: attention alone, all positions at once", "Vaswani and colleagues, 2017"),
        ("Attention compares every pair of positions: n² work and memory",
         "Compute it in tiles that fit in fast memory (FlashAttention)", "topic 12, 2022"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from one vector to attention")
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
    lk = d["lookup"]
    sc = {(int(a), b): (v, w, s) for a, b, v, w, s in d["scaling"]}
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Recurrent networks read a sentence word by word. In 2014 Bahdanau, Cho and Bengio let a translator look back at all the input words through attention. In 2017 eight researchers at Google kept the attention and threw away the recurrence, added several attention heads side by side, encoded word positions as sinusoids, and wrapped every layer in a residual connection (topic 7)."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the Transformer. Blue: what came after in this era."),
        ]),
        dict(id="play", eyebrow="Try it", title="A trained attention head", toc="Try it", blocks=[
            dict(type="p", text=f"This is the program's trained model, running in your browser: one attention head that has learned to answer \"what value is stored under this key?\". Change the pairs or the query and watch where it attends. Then give it something it never saw in training: a query that matches no key, or two equal keys."),
            dict(type="widget", html=TF_HTML, js=TF_JS.replace("__W__", json.dumps(d["W"], separators=(",", ":"))), css=TF_CSS,
                 fallback=dict(type="svg", name="attn", draw=attn_svg(d), alt="Attention weights of the trained model on one example", width=760),
                 note="In the interactive edition the trained model runs in your browser on any sequence you choose."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Queries, keys and values", toc="How it works", blocks=[
            dict(type="p", text="**Three projections.** Every position's vector x is multiplied by three learned matrices to give a query q, a key k and a value v. The query says what this position is looking for; the key says what each position offers; the value is what it hands over."),
            dict(type="p", text="**Scaled dot-product attention.** For one query, score every position by q · kᵢ / √d_k, turn the scores into weights with a softmax, and take the weighted sum of the values. For all positions at once this is softmax(QKᵀ/√d_k)V: two matrix products and a softmax, with no position waiting for another."),
            dict(type="p", text="**Why √d_k.** If q and k have d_k independent parts of size about 1, their dot product has variance d_k. Without the division, long vectors give large scores, the softmax puts nearly all its weight on one position, and the gradient through it nearly vanishes."),
            dict(type="p", text="**Heads, positions, layers.** The paper runs 8 heads side by side, each with its own projections of size d_k = 64 from d_model = 512, and joins their outputs. Attention by itself ignores order, so each position's vector gets a positional encoding made of sinusoids of different wavelengths. Each layer adds a small feed-forward network, and residual connections around both."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Let every position look at every other position directly, with weights it computes from the content. Distance in the sentence no longer matters, and the whole sequence is processed at once."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A lookup, learned", toc="Measured", blocks=[
            dict(type="p", text=f"**The task.** A sequence of {lk['pairs']} (key, value) pairs, keys from {lk['nk']} letters and values from {lk['nv']} numbers, then a query key; the answer is the value stored under it. The model is one attention head: d_model = {lk['d']}, d_k = {lk['dk']}, a residual connection and an output layer, {lk['params']} parameters. Its gradients are written out by hand and agree with finite differences to {C.sci(d['grad'])}. Training: Adam (topic 5), rate {lk['lr']}, {lk['steps']} steps of {lk['batch']} random sequences."),
            dict(type="table", head=["Model", "Right, on 5,000 new sequences"], num=[1], rows=[
                ["one attention head", lk["acc"] + "%"],
                ["the same model, averaging all positions equally", lk["avg"] + "%"],
                ["a random value", lk["chance"] + "%"],
            ], hl=0),
            dict(type="p", text=f"The trained head puts on average **{lk['att']}** of its attention on the pair whose key matches the query. Averaging cannot pick out one pair; it mixes all six values, and can do little better than guess among them."),
            dict(type="p", text="**The scaling.** Ten random keys, query and keys with independent parts of variance 1, 2,000 trials: the variance of q · k, the largest softmax weight, and the softmax's slope (Σ aⱼ(1 − aⱼ), zero when one weight is 1):"),
            dict(type="table", head=["d_k", "Variance of q·k", "Largest weight, unscaled", "scaled", "Slope, unscaled", "scaled"], num=[0, 1, 2, 3, 4, 5],
                 rows=[[dk, sc[(dk, "unscaled")][0], sc[(dk, "unscaled")][1], sc[(dk, "scaled")][1], sc[(dk, "unscaled")][2], sc[(dk, "scaled")][2]] for dk in sorted({k for k, _ in sc})], hl=2),
            dict(type="svg", name="scaling", draw=scaling_svg(d), alt="Largest softmax weight with and without scaling", width=760),
            dict(type="p", text=f"**Positions.** With the paper's sinusoids (d = 64), the dot product of the encodings of positions p and p + k is the same for every p: " + ", ".join(f"{k} apart {v}" for k, v in d["pos"]) + f" (largest difference {C.sci(d['pos_dev'])}). Position becomes something a dot product, and so attention, can measure."),
            dict(type="p", text="**The cost.** Attention compares every pair of positions, n² · d work per layer, but all of it can run at once; a recurrent layer does d² work per position, n steps one after another:"),
            dict(type="table", head=["Positions n", "d", "Attention multiply-adds", "Recurrent multiply-adds", "Steps in sequence"], num=[0, 1, 2, 3, 4],
                 rows=[[n, dd, a, r, s] for n, dd, a, r, s in d["cost"]]),
            dict(type="p", text="For short sequences attention is cheaper as well as parallel; for long ones its n² grows past the recurrent cost, which is the pain FlashAttention (topic 12) works on."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Montréal 2014, Google 2017", toc="The evidence", blocks=[
            dict(type="p", text="Bahdanau (Jacobs University Bremen), Cho and Bengio (Université de Montréal), ICLR 2015: \"the use of a fixed-length vector is a bottleneck in improving the performance\"; the fix is \"allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word\"."),
            dict(type="p", text="Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser and Polosukhin (Google Brain, Google Research, University of Toronto; \"Equal contribution. Listing order is random.\"), submitted 12 June 2017: a model \"based solely on attention mechanisms, dispensing with recurrence and convolutions entirely\"; \"Attention(Q, K, V) = softmax(QKᵀ/√dk)V\"; the scaling because large dot products push the softmax \"into regions where it has extremely small gradients\"; \"h = 8 parallel attention layers, or heads\"; \"each dimension of the positional encoding corresponds to a sinusoid\"; 28.4 BLEU on WMT 2014 English-to-German, and 41.8 on English-to-French \"after training for 3.5 days on eight GPUs\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A lookup table that learns", toc="Full circle", blocks=[
            dict(type="p", text="A hash table (Era 5) finds a value by its exact key. Attention is a soft version: every key is compared with the query, and the values are blended by how well they match. The model here learned to behave like a lookup table, with nothing but a softmax over dot products."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"One attention head, {lk['params']} parameters, {lk['acc']}% right on lookups it had never seen, against {lk['avg']}% when it may only average."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Scores 2, 1 and 0 go into a softmax. What are the weights?", "e², e¹, e⁰ divided by their sum: about 0.665, 0.245 and 0.090."),
            ("With d_k = 64, by what number are the scores divided, and why?", "By 8 = √64, so that their spread stays about 1 however long the vectors are."),
            ("Why does attention need a positional encoding?", "The weighted sum treats the positions as a set; shuffling them would give the same output without it."),
            ("How many query-key scores does one head compute for 1,000 positions?", "1,000 × 1,000 = 1,000,000."),
            ("A recurrent network needs n steps one after another. How many does an attention layer need?", "One: every position's output depends only on the layer's inputs, so all can be computed at once."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Attention Is All You Need (2017)", text="Vaswani and seven co-authors, arXiv:1706.03762.",
                 draw=C.draw_manuscript, link="https://arxiv.org/abs/1706.03762v3", link_text="arXiv:1706.03762", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Transformer", d["checks"],
                           "the hand-written gradients, that attention learns the lookup and averaging cannot, the softmax saturating without √d_k, the sinusoids' dot products, and that the rounded weights shown to the widget behave the same.",
                           ["static double run(Model m, Example e, Model g, double[] probsOut, double[] attnOut)"]),
    ]
    return dict(
        title="The Transformer", date="2017",
        description="Era 9, topic 9 of The Algorithm Evolution Atlas: attention (Bahdanau, Cho and Bengio, 2014) and the Transformer (Vaswani and colleagues, Google, 2017), with a trained attention head that runs in the page.",
        lede="A recurrent network reads a sentence one word at a time and carries it all in one vector. In 2014 translators learned to look back at every word through attention; in 2017 eight researchers at Google kept only the attention. Every position looks at every other one, all at once.",
        fieldnote=f"I gave a single attention head sequences of keys and values and asked it, again and again, for the value under one key. It learned to put {float(lk['att']) * 100:.0f}% of its attention on the right pair, and answered {lk['acc']}% of new questions correctly. The same model made to average instead of attend managed {lk['avg']}%.",
        card=[("When", "September 2014; June 2017"),
              ("Where", "Montréal and Bremen; Google Brain, Google Research, Toronto"),
              ("What hurt", "One fixed vector, read one word at a time"),
              ("The fix", "softmax(QKᵀ/√d_k)V, many heads, no recurrence"),
              ("Checked", f"{lk['acc']}% of lookups right, against {lk['avg']}% by averaging")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Transformer.java`.",
    )
