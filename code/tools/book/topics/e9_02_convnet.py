"""Era 9, topic 2: Deep convolutional networks. Every number is parsed from ConvNet.java's output."""
import json
import re

import common as C
from diagrams import Diagram

NAMES = ["horizontal", "vertical", "diagonal down", "diagonal up"]


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"data: .*? ; training: (\d+) images .*? ; tests: (\d+) in the left half, (\d+) in the right half", ln):
            d["data"] = dict(train=m.group(1), left=m.group(2), right=m.group(3))
        elif m := re.match(r"cnn: .*?softmax: (\d+) numbers ; gradient check: largest difference ([\d.eE+-]+) ; (\d+) passes of SGD ; error: training ([\d.]+)%, new left-half images ([\d.]+)%, right-half images \(never seen\) ([\d.]+)% ; right half by class: (.*)$", ln):
            d["cnn"] = dict(params=m.group(1), grad=m.group(2), passes=m.group(3), train=m.group(4), left=m.group(5), right=m.group(6),
                            byclass=re.findall(r"([a-z ]+?) (\d+)/(\d+)", m.group(7)))
        elif m := re.match(r"mlp: .*?(\d+) ReLU units, softmax: ([\d,]+) numbers ; (\d+) passes of SGD ; error: training ([\d.]+)%, new left-half images ([\d.]+)%, right-half images ([\d.]+)%", ln):
            d["mlp"] = dict(hidden=m.group(1), params=m.group(2), passes=m.group(3), train=m.group(4), left=m.group(5), right=m.group(6))
        elif ln.startswith("relu: "):
            d["relu"] = dict(rows=re.findall(r"start (\d+): ReLU (\d+), tanh (\d+)", ln),
                             tot=re.search(r"total ReLU ([\d,]+), tanh ([\d,]+): tanh needed ([\d.]+) times", ln).groups(),
                             wins=re.search(r"ReLU faster in (\d+) of 8", ln).group(1))
        elif ln.startswith("dropout: "):
            d["dropout"] = dict(hidden=re.search(r"with (\d+) hidden units", ln).group(1), n=re.search(r"(\d+) training images", ln).group(1),
                                no=re.search(r"without dropout: training error ([\d.]+)%, error on new left-half images ([\d.]+)%", ln).groups(),
                                yes=re.search(r"dropout 0.5 on the hidden units: training error ([\d.]+)%, error on new images ([\d.]+)%", ln).groups(),
                                wins=re.search(r"dropout better in (\d+) of 5", ln).group(1))
        elif ln.startswith("widget: "):
            filt = re.findall(r"filter (\d): ([-\d.,]+) bias (-?[\d.]+)", ln)
            cls = re.findall(r"class (\d): ([-\d.,]+) bias (-?[\d.]+)", ln)
            d["widget"] = dict(W=[[float(x) for x in f[1].split(",")] for f in filt], B=[float(f[2]) for f in filt],
                               V=[[float(x) for x in c[1].split(",")] for c in cls], C=[float(c[2]) for c in cls],
                               same=re.search(r"same answer on (\d+) of (\d+)", ln).groups(),
                               clean=re.findall(r"(horizontal|vertical|diagonal down|diagonal up) ([\d.]+)", ln.split("probability of the right class: ")[1]))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def filters_svg(d):
    W, B = d["widget"]["W"], d["widget"]["B"]
    mx = max(abs(x) for f in W for x in f)

    def draw(t, standalone):
        Wd, H = 760, 230
        o = [C.text(20, 26, "The six 3 × 3 filters the network learned (blue: positive weight, red: negative)", t["ink"], 13, "start", 700)]
        cell = 26
        for f in range(6):
            x0, y0 = 30 + f * 122, 50
            for a in range(3):
                for b in range(3):
                    v = W[f][a * 3 + b]
                    op = min(1, abs(v) / mx)
                    o.append(C.rect(x0 + b * cell, y0 + a * cell, cell - 2, cell - 2, t["blue"] if v > 0 else t["red"], extra=f";opacity:{0.15 + 0.85 * op:.2f}"))
            o.append(C.text(x0 + 38, y0 + 100, f"filter {f}", t["ink"], 12, "middle", 700))
            o.append(C.text(x0 + 38, y0 + 118, f"bias {B[f]:+.2f}", t["muted"], 11, "middle"))
        o.append(C.text(20, 205, "Nobody drew these. Some look like short strokes in one direction; training found them from the examples.", t["muted"], 12))
        return C.svg_doc(Wd, H, "".join(o), "The learned filters", t, standalone, 0.55, 760)
    return draw


CNN_HTML = """
<div class="board cnn-board">
  <div style="min-width:0">
    <div class="cnn-grid" id="cnn-grid" aria-label="Drawing grid, 12 by 12"></div>
    <div class="cnn-btns"><button type="button" id="cnn-clear">Clear</button><button type="button" id="cnn-shift">Shift right</button><button type="button" id="cnn-ex">An example</button></div>
  </div>
  <div style="min-width:0">
    <div class="cnn-probs" id="cnn-probs"></div>
    <div class="cnn-maps" id="cnn-maps"></div>
    <p class="say" id="cnn-say" aria-live="polite"></p>
  </div>
</div>
"""

CNN_CSS = """
.cnn-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
@media (max-width:700px){.cnn-board{grid-template-columns:1fr}}
.cnn-grid{display:grid;grid-template-columns:repeat(12,1fr);gap:2px;max-width:330px;touch-action:none;user-select:none}
.cnn-grid div{aspect-ratio:1;background:var(--wash);border:1px solid var(--rule);cursor:pointer}
.cnn-grid div.on{background:var(--ink)}
.cnn-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.cnn-probs{display:grid;gap:4px;font:13px var(--mono)}
.cnn-row{display:grid;grid-template-columns:110px 1fr 54px;gap:6px;align-items:center}
.cnn-bar{height:14px;background:var(--blue);border-radius:3px}
.cnn-bar.top{background:var(--red)}
.cnn-maps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:12px}
.cnn-maps svg{width:100%;height:auto;display:block}
.cnn-maps .cap{font:11px var(--mono);text-align:center}
"""

CNN_JS = r"""
(() => {
  const grid = document.getElementById("cnn-grid");
  if (!grid) return;
  const W = __W__, B = __B__, V = __V__, C = __C__, N = ["horizontal", "vertical", "diagonal down", "diagonal up"], S = 12, M = 10;
  let img = new Array(S * S).fill(0), down = false, paint = 1;
  const cells = [];
  for (let i = 0; i < S * S; i++) {
    const c = el("div", {}, grid); cells.push(c);
    c.addEventListener("pointerdown", e => { down = true; paint = img[i] ? 0 : 1; img[i] = paint; e.preventDefault(); run(); });
    c.addEventListener("pointerenter", () => { if (down) { img[i] = paint; run(); } });
  }
  window.addEventListener("pointerup", () => down = false);
  function run() {
    cells.forEach((c, i) => c.className = img[i] ? "on" : "");
    const maps = [], feat = [], where = [];
    for (let f = 0; f < 6; f++) {
      const m = new Array(M * M); let best = -1e9, at = 0;
      for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) {
        let s = B[f];
        for (let a = 0; a < 3; a++) for (let b = 0; b < 3; b++) s += W[f][a * 3 + b] * img[(i + a) * S + j + b];
        const v = Math.max(0, s); m[i * M + j] = v;
        if (v > best) { best = v; at = i * M + j; }
      }
      maps.push(m); feat.push(best); where.push(at);
    }
    const lg = C.map((c, k) => c + V[k].reduce((s, v, f) => s + v * feat[f], 0));
    const mx = Math.max(...lg), ex = lg.map(x => Math.exp(x - mx)), sum = ex.reduce((a, b) => a + b, 0), p = ex.map(x => x / sum);
    const top = p.indexOf(Math.max(...p));
    const pr = document.getElementById("cnn-probs"); pr.innerHTML = "";
    p.forEach((v, k) => { const r = el("div", {class: "cnn-row"}, pr); el("span", {}, r, N[k]); const bw = el("div", {}, r); el("div", {class: "cnn-bar" + (k === top ? " top" : ""), style: `width:${(100 * v).toFixed(1)}%`}, bw); el("span", {}, r, v.toFixed(3)); });
    const mp = document.getElementById("cnn-maps"); mp.innerHTML = "";
    const big = Math.max(1e-9, ...maps.flat());
    maps.forEach((m, f) => {
      const box = el("div", {}, mp);
      const svg = sv("svg", {viewBox: "0 0 100 100", role: "img", "aria-label": `filter ${f} response`}, box);
      for (let i = 0; i < M; i++) for (let j = 0; j < M; j++) sv("rect", {x: j * 10, y: i * 10, width: 9.5, height: 9.5, fill: "var(--blue)", opacity: (0.06 + 0.94 * m[i * M + j] / big).toFixed(2)}, svg);
      if (feat[f] > 0) sv("rect", {x: (where[f] % M) * 10, y: Math.floor(where[f] / M) * 10, width: 10, height: 10, fill: "none", stroke: "var(--red)", "stroke-width": 2}, svg);
      el("div", {class: "cap"}, box, `filter ${f}: max ${feat[f].toFixed(2)}`);
    });
    const any = img.some(x => x);
    document.getElementById("cnn-say").textContent = any ? `The network says ${N[top]} (${(100 * p[top]).toFixed(0)}%). Each small square map shows where one filter fires; only its strongest response (red box) is passed on, wherever it is.` : "Draw a short stroke: a line of 4 to 6 squares, across, down or diagonal.";
  }
  document.getElementById("cnn-clear").addEventListener("click", () => { img.fill(0); run(); });
  document.getElementById("cnn-shift").addEventListener("click", () => { const n = new Array(S * S).fill(0); for (let i = 0; i < S; i++) for (let j = 0; j < S - 1; j++) n[i * S + j + 1] = img[i * S + j]; img = n; run(); });
  document.getElementById("cnn-ex").addEventListener("click", () => { img.fill(0); const k = Math.floor(Math.random() * 4), len = 5;
    const dx = k === 1 ? 0 : 1, dy = k === 0 ? 0 : (k === 3 ? -1 : 1), x0 = Math.floor(Math.random() * 7), y0 = k === 3 ? 4 + Math.floor(Math.random() * 7) : (k === 0 ? Math.floor(Math.random() * 12) : Math.floor(Math.random() * 7));
    for (let i = 0; i < len; i++) img[(y0 + dy * i) * S + x0 + dx * i] = 1; run(); });
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 660, "How AlexNet combined older ideas, and where it led")
    W = 210
    nodes = {
        "neo": (20, 20, "Convolutional networks", "shared filters slide over the image", "Fukushima 1980; LeCun 1989", "ink"),
        "bp": (395, 20, "Backpropagation", "gradients through every layer", "Era 7", "ink"),
        "gpu": (770, 20, "GPUs and ImageNet", "graphics cards; a million labelled photos", "2000s", "ink"),
        "ax": (395, 190, "AlexNet", "⊕ ReLU, dropout, two GPUs", "Krizhevsky, Sutskever, Hinton, 2012", "red"),
        "res": (20, 360, "Residual networks", "hundreds of layers", "topic 7, 2015", "blue"),
        "adam": (770, 360, "Adam", "steps that set themselves", "topic 5, 2014", "blue"),
        "tf": (395, 520, "Deep learning everywhere", "speech, translation, Go, images from noise", "this era", "ink"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("neo", "ax", ports=("bottom", "top:0.15"))
    D.edge("bp", "ax", ports=("bottom", "top"))
    D.edge("gpu", "ax", ports=("bottom", "top:0.85"))
    D.edge("ax", "res", ports=("bottom:0.15", "top"))
    D.edge("ax", "adam", ports=("bottom:0.85", "top"))
    D.edge("ax", "tf", ports=("bottom", "top"))
    return D


def chain(d):
    steps = [
        ("Hand-made image features had stopped improving",
         "Learn the features: layers of filters trained end to end", "convolutional networks"),
        ("Deep networks trained slowly: tanh and sigmoid units saturate",
         f"Rectified linear units, max(0, x): here {d['relu']['tot'][2]} times fewer images to 25% error", "ReLU"),
        ("Sixty million parameters memorize a million photographs",
         "Dropout and data augmentation", "Krizhevsky, Sutskever, Hinton, 2012"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from features to learning")
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
    da, cn, ml, rl, dr, w = d["data"], d["cnn"], d["mlp"], d["relu"], d["dropout"], d["widget"]
    weak = [c for c in cn["byclass"] if c[1] != c[2]]
    weak_txt = ", ".join(f"{n} strokes ({a} of {b} right)" for n, a, b in weak)
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Convolutional networks were old (Fukushima's neocognitron of 1980, LeCun's networks from 1989), and so was backpropagation (Era 7). What was new in 2012 was the scale, a million labelled photographs and two graphics cards, and three changes that made the scale trainable: rectified linear units, dropout and data augmentation."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: AlexNet. Blue: steps in this era that made deeper networks trainable."),
        ]),
        dict(id="play", eyebrow="Try it", title="Draw a stroke", toc="Try it", blocks=[
            dict(type="p", text=f"This is the program's trained network, all {cn['params']} of its numbers. Draw a short stroke on the grid (click or drag): across, down, or diagonal. Six filters slide over your drawing; each keeps only its strongest response, wherever it is; four weighted sums of those six numbers give the probabilities. The network was trained only on strokes in the left half. Press *Shift right* and watch it still recognize them."),
            dict(type="widget", html=CNN_HTML, js=CNN_JS.replace("__W__", json.dumps(w["W"])).replace("__B__", json.dumps(w["B"])).replace("__V__", json.dumps(w["V"])).replace("__C__", json.dumps(w["C"])), css=CNN_CSS,
                 fallback=dict(type="table", head=["Clean 5-pixel stroke in the middle", "Probability of the right class"], num=[1],
                               rows=[[n, p] for n, p in w["clean"]]),
                 note="In the interactive edition you can draw strokes and watch each filter respond."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="One filter, every position", toc="How it works", blocks=[
            dict(type="p", text="**Convolution.** A filter is a small grid of numbers, here 3 × 3. Place it over a patch of the image, multiply each number by the pixel under it, and add: the sum is large where the patch looks like the filter. Slide it to every position and you get a map of where the pattern occurs. The same nine numbers are used everywhere, so a pattern learned in one place is found in any other, and the layer has very few numbers to learn."),
            dict(type="p", text="**Rectified linear units.** Each sum passes through max(0, x). The older tanh and sigmoid flatten out for large inputs, so their slope, and with it the error signal that backpropagation passes back, nearly vanishes. ReLU's slope is 1 wherever it is on. Krizhevsky and colleagues found it reached 25% training error on CIFAR-10 six times faster than tanh."),
            dict(type="p", text="**Pooling and the output.** AlexNet pooled small neighbourhoods; this program keeps only each filter's maximum over the whole image (global max pooling), which makes the answer the same wherever the stroke is. A last layer turns the six maxima into four probabilities (softmax), and the whole network is trained by backpropagation."),
            dict(type="p", text="**Dropout.** During training, switch off each unit of a layer with probability 0.5 at every step, and double the survivors. No unit can count on another being there, so the network cannot build fragile, memorized combinations. At test time every unit is used."),
            dict(type="svg", name="filters", draw=filters_svg(d), alt="The six learned 3 by 3 filters", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Share the weights across positions, and the network learns a pattern once and finds it everywhere. Use units that do not saturate, and the gradient survives the trip back."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Trained on the left, tested on the right", toc="Measured", blocks=[
            dict(type="p", text=f"**The data**: 12 × 12 images of four kinds of stroke, with noise and three stray dots each. All {da['train']} training images have their stroke in the left half; the tests are {da['left']} new left-half images and {da['right']} right-half images, a half the networks never saw."),
            dict(type="table", head=["Network", "Numbers to learn", "Training error", "New left-half", "Right half (never seen)"], num=[1, 2, 3, 4],
                 rows=[["Convolutional (6 filters, global max)", cn["params"], cn["train"] + "%", cn["left"] + "%", cn["right"] + "%"],
                       [f"Fully connected ({ml['hidden']} hidden units)", ml["params"], ml["train"] + "%", ml["left"] + "%", ml["right"] + "%"]], hl=0),
            dict(type="p", text=f"The fully connected network, with {ml['params']} numbers against {cn['params']}, fits the training images and does no better than chance (75% error) on the right half: to it, a stroke on the right is a different set of pixels. The convolutional network's errors on the right half are mostly {weak_txt}. Its gradient was checked against finite differences: largest difference {C.sci(cn['grad'])}."),
            dict(type="p", text="**ReLU against tanh**, with the same starting weights and the same sequence of images, counting images until the training error first falls below 25%:"),
            dict(type="table", head=["Start", "ReLU", "tanh"], num=[0, 1, 2], rows=[[a, b, c] for a, b, c in rl["rows"]] + [["total", rl["tot"][0], rl["tot"][1]]], hl=len(rl["rows"])),
            dict(type="p", text=f"ReLU was faster in {rl['wins']} of 8 starts; tanh needed {rl['tot'][2]} times as many images in total. The paper's factor was six, for a much deeper network on photographs."),
            dict(type="p", text=f"**Dropout** on a fully connected network with {dr['hidden']} hidden units, trained on only {dr['n']} images: without dropout, training error {dr['no'][0]}% and error on new images {dr['no'][1]}%; with dropout, {dr['yes'][0]}% and {dr['yes'][1]}%. Dropout was better in {dr['wins']} of 5 starts."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two graphics cards, six days", toc="The evidence", blocks=[
            dict(type="p", text="Krizhevsky, Sutskever and Hinton (University of Toronto): on ILSVRC-2012, \"a winning top-5 test error rate of 15.3%\" against 26.2% for the second-best entry; the network \"has 60 million parameters and 650,000 neurons\"; \"non-saturating neurons\" and \"dropout\"; ReLU reached \"a 25% training error rate on CIFAR-10 six times faster\" than tanh; \"Our network takes between five and six days to train on two GTX 580 3GB GPUs.\""),
            dict(type="p", text="Wikipedia: AlexNet was submitted to the challenge on 30 September 2012 and won by \"more than 10.8% points\"; the neocognitron (1980) and LeNet (1989) came first; by early 2025 the paper had been cited over 198,000 times."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Rosenblatt's perceptron, stacked and shared", toc="Full circle", blocks=[
            dict(type="p", text="Each unit in this network is Rosenblatt's perceptron (Era 5): a weighted sum and a threshold, here a soft one. Backpropagation (Era 7) trains many of them in layers. A convolutional layer is many copies of one small perceptron, one at each position, sharing its weights. Residual networks (topic 7) will stack a hundred such layers."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{cn['params']} shared numbers recognized strokes in a half of the image they had never seen, with {cn['right']}% error; {ml['params']} unshared numbers did no better than guessing."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A 3 × 3 filter slides over a 12 × 12 image without going past the edges. How many positions does it visit?", "10 × 10 = 100."),
            ("Why does sharing one filter across all positions help a network trained only on the left half?", "The same filter, with the same numbers, also slides over the right half; a stroke there produces the same responses, just in a different place."),
            ("What is the slope of tanh at x = 3, roughly, and of ReLU?", "1 − tanh²(3) ≈ 0.01; ReLU's slope is 1. A gradient passing back through tanh at 3 shrinks a hundredfold."),
            ("With dropout 0.5, why double the surviving units during training?", "So that the expected input to the next layer is the same as at test time, when every unit is on."),
            ("Why did AlexNet need graphics cards?", "Convolutions are millions of independent multiply-adds, which a GPU does in parallel; on the CPUs of 2012 the training would have taken weeks or months."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="ImageNet Classification with Deep Convolutional Neural Networks (2012)", text="Krizhevsky, Sutskever and Hinton's paper.",
                 draw=C.draw_manuscript, link="https://courses.cs.duke.edu/fall16/compsci527/papers/Krizhevsky%20et%20al%20DNN%20ImageNet%202012.pdf", link_text="The paper (PDF, on a Duke course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ConvNet", d["checks"],
                           "backpropagation against finite differences, both networks on both halves, ReLU against tanh from eight starts, dropout from five, and the widget's rounded network against the trained one.",
                           ["static double conv(double[] img, int f, int i, int j)", "static void backward(double[] img, int y)"]),
    ]
    return dict(
        title="Deep Convolutional Networks", date="2012",
        description="Era 9, topic 2 of The Algorithm Evolution Atlas: AlexNet (Toronto, 2012) and the convolutional network: shared filters, ReLU, dropout, trained on one half of an image and tested on the other.",
        lede="Computer vision had stalled on hand-made features, and deep networks trained slowly. In 2012 a team in Toronto trained a convolutional network on a million photographs with two graphics cards, rectified linear units and dropout, and won the ImageNet challenge by more than ten points.",
        fieldnote=f"I taught two small networks to tell four kinds of stroke apart, showing them only the left half of the picture. The one with {ml['params']} numbers learned the left half perfectly and guessed on the right. The one with {cn['params']}, whose filters slide over every position, recognized the strokes on the right as if it had always seen them there.",
        card=[("When", "Submitted 30 September 2012"),
              ("Where", "University of Toronto"),
              ("What hurt", "Hand-made features had stalled; deep nets trained slowly"),
              ("The fix", "Convolutions on GPUs, ReLU, dropout"),
              ("Checked", f"Right-half error {cn['right']}% (convolutional) against {ml['right']}% (fully connected)")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ConvNet.java`.",
    )
