"""Era 9, topic 7: Residual networks. Every number is parsed from ResidualNetworks.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"depth": []}
    for ln in text.splitlines():
        if m := re.match(r"gradient: .*? largest relative difference from finite differences ([\d.eE+-]+)", ln):
            d["grad"] = m.group(1)
        elif ln.startswith("depth: "):
            d["setup"] = re.match(r"depth: fit (.*?) on (\d+) points \(variance ([\d.]+)\), width (\d+), Adam rate ([\d.]+), ([\d,]+) steps of (\d+), mean of (\d+) seeds", ln).groups()
            for m in re.finditer(r"(\d+) blocks \((\d+) weight layers, ([\d,]+) parameters\): plain ([\d.]+), residual ([\d.]+) ; first-block gradient at the start: plain ([\d.eE+-]+), residual ([\d.eE+-]+) ; a residual network started like the plain one: error at the start ([\d.eE+-]+), first-block gradient ([\d.eE+-]+)", ln):
                d["depth"].append(dict(zip(["B", "layers", "params", "plain", "res", "gp", "gr", "he_err", "he_g"], m.groups())))
        elif m := re.match(r"degradation: the best plain network had (\d+) blocks \(([\d.]+)\) ; the 32-block plain network ([\d.]+), ([\d.]+) times worse.*? ; the 32-block residual network ([\d.]+)", ln):
            d["deg"] = m.groups()
        elif ln.startswith("curves: "):
            d["every"] = int(re.search(r"every (\d+) steps", ln).group(1))
            d["curves"] = {f"{k} {b}": [float(x) for x in v.split(",")] for k, b, v in re.findall(r"(plain|residual) (\d+) ([\d.,]+)", ln)}
        elif m := re.match(r"identity: a 4-block residual network after (\d+) steps \(error ([\d.]+)\), extended to (\d+) blocks.*?over all (\d+) points: ([\d.]+) ; the same weights in a plain network: error ([\d.]+)", ln):
            d["identity"] = m.groups()
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def depth_svg(d):
    def draw(t, standalone):
        W, H = 760, 380
        o = [C.text(20, 26, "Error on the training data after training, by depth (log scale)", t["ink"], 13, "start", 700)]
        X0, X1, Y0, Y1 = 90, 600, 50, 320
        lo, hi = math.log10(2e-4), math.log10(0.5)
        sy = lambda v: Y1 - (math.log10(v) - lo) / (hi - lo) * (Y1 - Y0)
        n = len(d["depth"])
        sx = lambda i: X0 + i / (n - 1) * (X1 - X0)
        for v in [1e-3, 1e-2, 1e-1]:
            o.append(C.line(X0, sy(v), X1, sy(v), t["rule"], 1))
            o.append(C.text(X0 - 8, sy(v) + 4, f"{v:g}", t["muted"], 11, "end"))
        for i, r in enumerate(d["depth"]):
            o.append(C.text(sx(i), Y1 + 20, f"{r['B']}", t["muted"], 11, "middle"))
        o.append(C.text((X0 + X1) / 2, Y1 + 40, "blocks of two layers", t["muted"], 11, "middle"))
        for key, col, lab in [("plain", t["muted"], "plain"), ("res", t["red"], "residual")]:
            pts = [(sx(i), sy(float(r[key]))) for i, r in enumerate(d["depth"])]
            o.append(C.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), col, "none", 2.4))
            for x, y in pts:
                o.append(C.circle(x, y, 4, col))
            o.append(C.text(pts[-1][0] + 10, pts[-1][1] + 4, f"{lab} {d['depth'][-1][key]}", col, 12, "start", 700))
        o.append(C.text(20, H - 8, "Plain networks get worse beyond a few blocks; residual networks keep getting better.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Training error of plain and residual networks by depth", t, standalone, 0.55, 760)
    return draw


RES_HTML = """
<div class="res-board">
  <div class="res-btns" id="res-depths"></div>
  <div class="res-grid">
    <div style="min-width:0"><div class="res-h">Training error while training (log scale)</div><div class="res-view" id="res-curve"></div></div>
    <div style="min-width:0"><div class="res-h">Gradient reaching each block, at the start (log scale)</div><div class="res-view" id="res-sig"></div>
      <button type="button" id="res-new">New random weights</button></div>
  </div>
  <p class="say" id="res-say" aria-live="polite"></p>
</div>
"""

RES_CSS = """
.res-btns{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px;align-items:center;font-size:13px}
.res-btns button.on{background:var(--ink);color:var(--paper)}
.res-grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.res-grid{grid-template-columns:1fr}}
.res-view svg{width:100%;height:auto;display:block;background:var(--wash)}
.res-h{font-size:12px;font-weight:700;color:var(--muted);margin-bottom:4px}
#res-new{margin-top:8px}
"""

RES_JS = r"""
(() => {
  const cv = document.getElementById("res-curve");
  if (!cv) return;
  const CURVES = __CURVES__, EVERY = __EVERY__, DEPTHS = __DEPTHS__, W = 12;
  let B = 32, seed = 1;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
  const gauss = () => { let u = 0, v = 0; while (u === 0) u = rnd(); v = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const bar = document.getElementById("res-depths");
  el("span", {}, bar, "Blocks:");
  DEPTHS.forEach(b => { const x = el("button", {type: "button", id: `res-d${b}`}, bar, String(b)); x.addEventListener("click", () => { B = b; draw(); }); });
  function logPlot(host, series, xmax, ylo, yhi, xlab) {
    host.innerHTML = "";
    const svg = sv("svg", {viewBox: `0 0 400 ${262 + 15 * series.length}`, role: "img", "aria-label": xlab}, host);
    const X = x => 50 + x / xmax * 330, Y = v => 225 - (Math.log10(Math.max(v, 10 ** ylo)) - ylo) / (yhi - ylo) * 205;
    for (let e = Math.ceil(ylo); e <= yhi; e++) { sv("line", {x1: 50, x2: 380, y1: Y(10 ** e), y2: Y(10 ** e), stroke: "var(--rule)"}, svg); sv("text", {x: 45, y: Y(10 ** e) + 4, "text-anchor": "end", "font-size": 10, fill: "var(--muted)"}, svg, e === 0 ? "1" : `1e${e}`); }
    sv("text", {x: 215, y: 254, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}, svg, xlab);
    series.forEach(([pts, col, lab], k) => {
      sv("polyline", {points: pts.map(([x, y]) => `${X(x)},${Y(y)}`).join(" "), fill: "none", stroke: col, "stroke-width": 2.4}, svg);
      sv("line", {x1: 50, x2: 66, y1: 268 + 15 * k, y2: 268 + 15 * k, stroke: col, "stroke-width": 3}, svg);
      sv("text", {x: 72, y: 272 + 15 * k, "font-size": 11, "font-weight": 700, fill: col}, svg, lab);
    });
  }
  function grads(residual, zero) {
    const Win = [...Array(W)].map(() => [gauss(), gauss()]);
    const W1 = [], W2 = [];
    for (let b = 0; b < B; b++) {
      W1.push([...Array(W)].map(() => [...Array(W)].map(() => gauss() * Math.sqrt(2 / W))));
      W2.push([...Array(W)].map(() => [...Array(W)].map(() => zero ? 0 : gauss() * Math.sqrt(2 / W))));
    }
    const wout = [...Array(W)].map(() => gauss() * Math.sqrt(1 / W));
    const sum = new Array(B + 1).fill(0), S = 60;
    for (let s = 0; s < S; s++) {
      const x = [rnd() * 2 - 1, rnd() * 2 - 1];
      const hs = [Win.map(w => Math.max(0, w[0] * x[0] + w[1] * x[1]))], mids = [];
      for (let b = 0; b < B; b++) {
        const h = hs[b], mid = W1[b].map(r => Math.max(0, r.reduce((a, w, k) => a + w * h[k], 0)));
        mids.push(mid);
        hs.push(W2[b].map((r, j) => Math.max(0, (residual ? h[j] : 0) + r.reduce((a, w, k) => a + w * mid[k], 0))));
      }
      let dd = wout.slice();
      sum[B] += dd.reduce((a, v) => a + v * v, 0) / W;
      for (let b = B - 1; b >= 0; b--) {
        const out = hs[b + 1], mid = mids[b], ds = dd.map((v, j) => out[j] > 0 ? v : 0);
        const dmid = mid.map((m, k) => m > 0 ? ds.reduce((a, v, j) => a + v * W2[b][j][k], 0) : 0);
        dd = hs[b].map((_, k) => (residual ? ds[k] : 0) + dmid.reduce((a, v, j) => a + v * W1[b][j][k], 0));
        sum[b] += dd.reduce((a, v) => a + v * v, 0) / W;
      }
    }
    return sum.map((v, b) => [b, Math.sqrt(v / S)]);
  }
  function draw() {
    DEPTHS.forEach(b => document.getElementById(`res-d${b}`).classList.toggle("on", b === B));
    const pc = CURVES[`plain ${B}`], rc = CURVES[`residual ${B}`], xmax = (pc.length - 1) * EVERY;
    logPlot(cv, [[pc.map((v, i) => [i * EVERY, v]), "var(--muted)", `plain: ${pc[pc.length - 1]}`], [rc.map((v, i) => [i * EVERY, v]), "var(--red)", `residual: ${rc[rc.length - 1]}`]], xmax, -4, 0, "training steps");
    const s0 = seed, gp = grads(false, false); seed = s0; const gh = grads(true, false); seed = s0; const gz = grads(true, true);
    const all = [...gp, ...gh, ...gz].map(p => p[1]).filter(v => v > 0);
    const lo = Math.floor(Math.log10(Math.min(...all))), hi = Math.ceil(Math.log10(Math.max(...all)));
    logPlot(document.getElementById("res-sig"), [[gp, "var(--muted)", "plain"], [gz, "var(--red)", "residual, branches start at zero"], [gh, "var(--blue)", "residual, started like the plain one"]], B, lo, Math.max(hi, lo + 1), "block (0 = nearest the input; the output is on the right)");
    const ratio = gp[0][1] / gp[B][1], fmt = v => v < 100 ? v.toPrecision(2) : Math.round(v).toLocaleString("en-US");
    document.getElementById("res-say").textContent = `${B} blocks. Left: the program's training runs. Right: a fresh random network in your browser; in the plain one the gradient arriving at the first block is ${ratio > 1 ? fmt(ratio) + " times larger" : fmt(1 / ratio) + " times smaller"} than at the last. Started like the plain one, a residual network's signal grows block after block; started with its branches at zero, it passes the gradient through unchanged.`;
  }
  document.getElementById("res-new").addEventListener("click", () => { seed = (seed * 7919 + 13) % 2147483647 || 1; draw(); });
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How residual networks combined older ideas, and where they led")
    W = 250
    nodes = {
        "cnn": (40, 20, "Deep convolutional networks", "more layers, better results, up to a point", "topic 2, 2012", "ink"),
        "lstm": (375, 20, "The LSTM's cell state", "a path along which the signal is added to, not rewritten", "Era 8", "ink"),
        "hw": (710, 20, "Highway networks", "gated shortcuts in a feed-forward network", "2015", "ink"),
        "res": (375, 200, "Residual networks", "⊕ identity shortcuts: y = F(x) + x", "He, Zhang, Ren and Sun, Microsoft Research, 2015", "red"),
        "tf": (40, 380, "The Transformer", "residual connections throughout", "topic 9, 2017", "blue"),
        "go": (710, 380, "AlphaGo Zero, AlphaFold", "deep residual networks at work", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("cnn", "res", ports=("bottom", "top:0.15"))
    D.edge("lstm", "res", ports=("bottom", "top"))
    D.edge("hw", "res", ports=("bottom", "top:0.85"))
    D.edge("res", "tf", ports=("bottom:0.15", "top"))
    D.edge("res", "go", ports=("bottom:0.85", "top"))
    return D


def chain():
    steps = [
        ("Deeper plain networks train worse, even on their own training data",
         "Identity shortcuts: each block learns only a correction, y = F(x) + x", "He and colleagues, 2015"),
        ("Each block adds to the signal, so without care it grows block after block",
         "Normalize each layer (batch normalization in the paper), or start every branch near zero", ""),
        ("Shortcuts trained deep networks for images; language still went through recurrent layers one step at a time",
         "The Transformer: attention layers, with residual connections throughout", "topic 9, 2017"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from plain to residual")
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
    st, dg, idn = d["setup"], d["deg"], d["identity"]
    last = d["depth"][-1]
    rows = [[r["B"], r["layers"], r["params"], r["plain"], r["res"], C.sci(r["gp"]), C.sci(r["gr"])] for r in d["depth"]]
    he_rows = [[r["B"], C.sci(r["he_err"]) if "e" in r["he_err"] else r["he_err"], C.sci(r["he_g"])] for r in d["depth"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. After 2012 (topic 2) deeper networks did better, up to a point, and then worse. The LSTM (Era 8) had already shown that a signal survives many steps if it is carried along and added to rather than rewritten each time; highway networks applied a gated version of that to feed-forward networks. He, Zhang, Ren and Sun at Microsoft Research removed the gate: every block simply adds its input to its output."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: residual networks. Blue: where the shortcut went next."),
        ]),
        dict(id="play", eyebrow="Try it", title="Deeper and worse, or deeper and better", toc="Try it", blocks=[
            dict(type="p", text="Choose a depth. On the left are the program's training runs: plain against residual, the same data, optimizer and steps. On the right, your browser builds a fresh random network of that depth and measures how much gradient reaches each block. Try 32 blocks, then press *New random weights*."),
            dict(type="widget", html=RES_HTML,
                 js=RES_JS.replace("__CURVES__", json.dumps(d["curves"])).replace("__EVERY__", str(d["every"])).replace("__DEPTHS__", json.dumps([int(r["B"]) for r in d["depth"]])),
                 css=RES_CSS,
                 fallback=dict(type="svg", name="depth", draw=depth_svg(d), alt="Training error of plain and residual networks by depth", width=760),
                 note="In the interactive edition you can choose the depth and see the training curves and gradients."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it. Starting branches at zero is what this program does; the paper normalizes instead."),
        ]),
        dict(id="how", eyebrow="How it works", title="Learn the correction, not the whole", toc="How it works", blocks=[
            dict(type="p", text="**A plain block** of two layers maps its input h to relu(W₂ relu(W₁h + b₁) + b₂). A stack of them has to carry everything the network knows through every layer; if a block should change nothing, its weights must learn to reproduce their input exactly, which is hard for layers of random numbers and rectifiers."),
            dict(type="p", text="**A residual block** maps h to relu(h + F(h)), where F is the same two layers. The block only learns a correction F(h) = H(h) − h to its input. If nothing needs to change, F can shrink to zero, and setting W₂ = 0 passes the signal through exactly. The shortcut has no weights: the paper's words, it adds \"neither extra parameter nor computational complexity\"."),
            dict(type="p", text="**Gradients flow along the shortcut too.** Going backwards, each block passes its output's gradient straight to its input, plus whatever comes through F. In a plain stack, the gradient must pass through every layer's weights and rectifiers in turn, and it can shrink (or grow) by a factor at each one."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Make doing nothing the easiest thing for a block to do. Then adding blocks cannot make the network worse at the start, and each block only has to learn what is still missing."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Thirty-two blocks", toc="Measured", blocks=[
            dict(type="p", text=f"**The task**: fit f(x, y) = sin 3x · cos 3y + 0.5 sin 5xy at {st[1]} random points (the values have variance {st[2]}). Every network has hidden layers {st[3]} wide and is trained with Adam (topic 5), rate {st[4]}, for {st[5]} steps of {st[6]} points; each number is the mean of {st[7]} runs. The error is on the training points themselves, so overfitting cannot explain it. Plain blocks start with random (He) weights; residual blocks start with their second layer at zero, so that each starts as the identity. The program's backpropagation agrees with finite differences to {C.sci(d['grad'])}."),
            dict(type="table", head=["Blocks", "Weight layers", "Parameters", "Plain error", "Residual error", "Gradient at block 1, plain", "residual"], num=[0, 1, 2, 3, 4, 5, 6], rows=rows, hl=len(rows) - 1),
            dict(type="p", text=f"The best plain network had {dg[0]} blocks ({dg[1]}). With 32 blocks the plain network's error was {dg[2]}, **{dg[3]} times worse** on its own training data: the degradation problem. The residual network's error kept falling with depth, to {dg[4]} at 32 blocks. At the start of training, the gradient reaching the first block of the 32-block plain network was {C.sci(last['gp'])}, against {C.sci(d['depth'][0]['gp'])} for one block."),
            dict(type="p", text="**The shortcut alone is not enough.** A residual network started with the same random weights as the plain one adds a full random correction in every block, and the signal grows block after block. At the start of training:"),
            dict(type="table", head=["Blocks", "Error at the start", "Gradient at block 1"], num=[0, 1, 2], rows=he_rows, hl=len(he_rows) - 1),
            dict(type="p", text="The paper's networks avoid this by normalizing every layer (batch normalization); this program avoids it by starting every branch at zero. Either way, the shortcut only helps if the corrections start small."),
            dict(type="p", text=f"**A deeper network can copy a shallower one.** A 4-block residual network trained for {idn[0]} steps (error {idn[1]}) was extended to {idn[2]} blocks whose second weights are zero. Over all {idn[3]} points the largest difference in output was **{idn[4]}**: exactly the same function. The same weights in a plain network give every input the same output (error {idn[5]}): zero weights there do not pass the signal, they cut it."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Microsoft Research, December 2015", toc="The evidence", blocks=[
            dict(type="p", text="He, Zhang, Ren and Sun (Microsoft Research, submitted 10 December 2015): \"with the network depth increasing, accuracy gets saturated (which might be unsurprising) and then degrades rapidly. Unexpectedly, such degradation is not caused by overfitting\"; \"we let the stacked nonlinear layers fit another mapping of F(x) := H(x)−x\"; \"the 34-layer plain net has higher training error throughout the whole training procedure\". On ImageNet validation (10-crop, top-1 error): plain 18 layers 27.94%, plain 34 layers 28.54%; ResNet-18 27.88%, ResNet-34 25.03%. Networks of up to 152 layers; an ensemble reached 3.57% error on the ImageNet test set and won the ILSVRC 2015 classification task."),
            dict(type="p", text="Wikipedia: \"ResNet is equivalent to an open-gated highway network\"; an LSTM's cell state can \"function as a generalized residual connection\"; \"All transformer architectures include residual connections\"; residual connections ease vanishing gradients \"to some extent\", but vanishing gradients are not the root cause of the degradation problem."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The LSTM's trick, turned sideways", toc="Full circle", blocks=[
            dict(type="p", text="In 1997 the LSTM (Era 8) let a signal cross hundreds of time steps by adding to a cell rather than rewriting it. A residual network does the same thing across layers instead of across time: the signal is carried forward and each block adds a correction. Two years later the Transformer (topic 9) was built with residual connections throughout; Wikipedia: \"All transformer architectures include residual connections\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Thirty-two plain blocks trained {dg[3]} times worse than two. Thirty-two residual blocks trained better than any plain network: {dg[4]}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A residual block's branch outputs F(h) = 0. What does the block compute, if h ≥ 0?", "relu(h + 0) = h: the identity."),
            ("Why is higher training error, not test error, the telling sign of degradation?", "Overfitting raises test error while lowering training error. Higher training error means the optimizer failed to find a solution a deeper network could represent."),
            ("In a plain stack, each layer multiplies the gradient by about 0.75. How much reaches the first of 64 layers?", "0.75⁶⁴, about 10⁻⁸: almost nothing."),
            ("How many extra parameters does an identity shortcut add?", "None: it adds the input as it is."),
            ("Why might a residual network started with full random weights in every branch blow up?", "Each block adds a random correction of about the size of its input, so the signal can roughly double per block: 32 blocks, a factor of billions."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Deep Residual Learning for Image Recognition (2015)", text="He, Zhang, Ren and Sun, arXiv:1512.03385.",
                 draw=C.draw_manuscript, link="https://arxiv.org/abs/1512.03385v1", link_text="arXiv:1512.03385", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ResidualNetworks", d["checks"],
                           "backpropagation against finite differences, the degradation of the deepest plain network, the residual networks improving with depth, and the exact copy of a shallower network.",
                           ["double forward(double[] x, double[][] h, double[][] u)", "double backward(double[] x, double y, double[] g)"]),
    ]
    return dict(
        title="Residual Networks", date="2015",
        description="Era 9, topic 7 of The Algorithm Evolution Atlas: residual networks (He, Zhang, Ren and Sun, Microsoft Research, 2015), identity shortcuts and the degradation problem, measured.",
        lede="Deeper networks did better, until they did worse, even on the data they were trained on. In December 2015 a team at Microsoft Research made every block of layers add its input to its output. Doing nothing became the easiest thing for a layer to learn, and networks of 152 layers trained.",
        fieldnote=f"I stacked layers on a small network and taught it a wavy surface. Two blocks did well. Thirty-two blocks did {dg[3]} times worse, on the very points they were taught. Then I let every block add its input back to its output, and the thirty-two-block network became the best of all.",
        card=[("When", "December 2015"),
              ("Where", "Microsoft Research"),
              ("What hurt", "Deeper plain networks trained worse"),
              ("The fix", "Identity shortcuts: y = F(x) + x"),
              ("Checked", f"32 blocks: plain {dg[2]}, residual {dg[4]}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ResidualNetworks.java`.",
    )
