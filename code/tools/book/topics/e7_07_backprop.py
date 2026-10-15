"""Era 7, topic 7: backpropagation. Every number is parsed from Backpropagation.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"perceptron: .*? AND learned in (\d+) epochs ; XOR never learned in ([\d,]+) epochs, at best (\d) of 4 right at once ; of ([\d,]+) straight lines .*? the best managed (\d)", ln):
            d["perc"] = dict(andep=m.group(1), epochs=m.group(2), best=m.group(3), lines=m.group(4), bestline=m.group(5))
        elif m := re.match(r"xor: .*? rate ([\d.]+), momentum ([\d.]+), .*? ; (\d+) of (\d+) starts learned XOR .*? within ([\d,]+) epochs, the median after (\d+) epochs, the fastest (\d+), the slowest (\d+) ; the other (\d+) got stuck", ln):
            d["xor"] = dict(rate=m.group(1), mom=m.group(2), ok=m.group(3), starts=m.group(4), max=m.group(5), med=m.group(6), fast=m.group(7), slow=m.group(8), stuck=m.group(9))
        elif m := re.match(r"gradcheck: a network of (\d+) inputs, (\d+) hidden units and (\d+) outputs, (\d+) weights ; backpropagation: one forward run \(([\d,]+) multiplications\) and one backward run \(([\d,]+)\) ; wiggling each weight up and down: ([\d,]+) forward runs, ([\d,]+) multiplications ; the (\d+) slopes agree to a relative difference of at most ([\d.eE-]+)", ln):
            d["grad"] = dict(nin=m.group(1), nh=m.group(2), nout=m.group(3), w=m.group(4), fwd=m.group(5), bwd=m.group(6), runs=m.group(7), wig=m.group(8), diff=m.group(10))
        elif m := re.match(r"xorinit: (.*)$", ln):
            d["init"] = [float(x) for x in m.group(1).split()]
        elif m := re.match(r"xorrun: .*? XOR learned after (\d+) epochs ; .*? epoch:error ; (.*)$", ln):
            d["run"] = dict(epochs=int(m.group(1)), curve=[(int(p.split(":")[0]), float(p.split(":")[1])) for p in m.group(2).split()])
        elif m := re.match(r"xorfinal: outputs (.*?) ; final weights (.*)$", ln):
            d["final"] = dict(outs=[(p.split("->")[0], p.split("->")[1]) for p in m.group(1).split()], w=m.group(2).split())
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def network_svg(d):
    """The 2-2-1 network: forward in black, the chain rule backwards in red."""
    def draw(t, standalone):
        o = []
        W, H = 780, 330
        o.append(C.text(20, 26, "Forward: compute the output. Backward: pass the error's slope back through every weight", t["ink"], 13, "start", 700))
        P = {"x1": (110, 110), "x2": (110, 230), "h1": (380, 110), "h2": (380, 230), "y": (640, 170)}
        for a, b in [("x1", "h1"), ("x1", "h2"), ("x2", "h1"), ("x2", "h2"), ("h1", "y"), ("h2", "y")]:
            (x1, y1), (x2, y2) = P[a], P[b]
            o.append(C.line(x1 + 26, y1, x2 - 26, y2, t["ink"], 1.6))
            o.append(C.path(f"M{x2 - 26:.1f},{y2:.1f} L{x2 - 36:.1f},{y2 - 5 + (y2 - y1) * 0.04:.1f} L{x2 - 36:.1f},{y2 + 5 + (y2 - y1) * 0.04:.1f} Z", None, t["ink"]))
        for a, b in [("y", "h1"), ("y", "h2"), ("h1", "x1"), ("h2", "x2")]:
            (x1, y1), (x2, y2) = P[a], P[b]
            off = -16
            qx, qy, ex, ey = (x1 + x2) / 2, (y1 + y2) / 2 + off - 30, x2 + 26, y2 + off
            o.append(C.path(f"M{x1 - 26:.1f},{y1 + off:.1f} Q{qx:.1f},{qy:.1f} {ex:.1f},{ey:.1f}", t["red"], "none", 1.8, ";stroke-dasharray:6 4"))
            ux, uy = ex - qx, ey - qy
            L = (ux * ux + uy * uy) ** 0.5
            ux, uy = ux / L, uy / L
            o.append(C.path(f"M{ex:.1f},{ey:.1f} L{ex - ux * 10 - uy * 5:.1f},{ey - uy * 10 + ux * 5:.1f} L{ex - ux * 10 + uy * 5:.1f},{ey - uy * 10 - ux * 5:.1f} Z", None, t["red"]))
        for k, (x, y) in P.items():
            o.append(C.circle(x, y, 26, t["surface"], t["red"] if k == "y" else t["ink"], 2))
            o.append(C.text(x, y + 5, k.replace("1", "₁").replace("2", "₂"), t["ink"], 15, "middle", 700))
        o.append(C.text(110, 285, "inputs", t["muted"], 12, "middle"))
        o.append(C.text(380, 285, "hidden units", t["muted"], 12, "middle"))
        o.append(C.text(640, 230, "output", t["muted"], 12, "middle"))
        o.append(C.text(510, 70, "δ_y = (y − target) · y(1 − y)", t["red"], 12.5, "middle", 700))
        o.append(C.text(245, 70, "δ_h = δ_y · v_h · h(1 − h)", t["red"], 12.5, "middle", 700))
        o.append(C.text(20, H - 10, "Each weight's slope is δ of the unit it feeds times the value it carries: one backward pass gives them all.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A 2-2-1 network with forward and backward passes", t, standalone, 0.55, 780)
    return draw


def curve_svg(d):
    """The XOR run's error, epoch by epoch."""
    curve, ep = d["run"]["curve"], d["run"]["epochs"]

    def draw(t, standalone):
        o = []
        W, H = 760, 300
        x0, x1, y0, y1 = 70, 730, 240, 50
        X = lambda e: x0 + e / max(ep, curve[-1][0]) * (x1 - x0)
        Y = lambda v: y0 - v / 0.55 * (y0 - y1)
        o.append(C.text(20, 26, f"Learning XOR from the program's starting weights: the error, every 10 epochs, until it is learned at epoch {ep}", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
            o.append(C.text(x0 - 8, Y(v) + 4, f"{v:.1f}", t["muted"], 11.5, "end"))
            o.append(C.line(x0 - 4, Y(v), x0, Y(v), t["axis"], 1.2))
        for e in range(0, ep + 1, 50):
            o.append(C.text(X(e), y0 + 18, str(e), t["muted"], 11.5, "middle"))
        o.append(C.text((x0 + x1) / 2, y0 + 40, "epoch (one pass over the four cases)", t["muted"], 12, "middle"))
        o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(e):.1f},{Y(v):.1f}" for i, (e, v) in enumerate(curve)), t["red"], "none", 2.2))
        flat = next(e for e, v in curve if v < 0.49)
        o.append(C.text(X(60), Y(0.5) - 10, "a long plateau: the hidden units have not yet split the job", t["ink"], 12, "start"))
        o.append(C.text(X(flat) - 6, Y(0.12), "then they do, and the error falls fast", t["ink"], 12, "end"))
        return C.svg_doc(W, H, "".join(o), "Error against epoch while learning XOR", t, standalone, 0.55, 760)
    return draw


BP_HTML = """
<div class="board bp-board">
  <div style="min-width:0">
    <div class="bp-view" id="bp-view"></div>
  </div>
  <div style="min-width:0">
    <div class="bp-btns"><button type="button" class="primary" id="bp-10">Train 10 epochs</button><button type="button" id="bp-end">Train until learned</button></div>
    <div class="bp-btns"><button type="button" id="bp-prog">The program's start</button><button type="button" id="bp-rand">A random start</button></div>
    <div class="bp-stats" id="bp-stats"></div>
    <p class="say" id="bp-say" aria-live="polite"></p>
  </div>
</div>
"""

BP_CSS = """
.bp-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.bp-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.bp-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

BP_JS = r"""
(() => {
  const view = document.getElementById("bp-view");
  if (!view) return;
  const INIT = __INIT__, PROG = __PROG__, RATE = __RATE__, MOM = __MOM__;
  const IN = [[0, 0], [0, 1], [1, 0], [1, 1]], XOR = [0, 1, 1, 0];
  const sig = x => 1 / (1 + Math.exp(-x));
  let w, step, epoch, curve, fromProg;
  function fwd(x) { const h0 = sig(w[0] * x[0] + w[1] * x[1] + w[2]), h1 = sig(w[3] * x[0] + w[4] * x[1] + w[5]); return [sig(w[6] * h0 + w[7] * h1 + w[8]), h0, h1]; }
  // exactly the program's errorAndGradient and train loop, in the same order
  function grad(g) {
    g.fill(0); let E = 0;
    for (let i = 0; i < 4; i++) {
      const x = IN[i], [y, h0, h1] = fwd(x);
      E += 0.5 * (y - XOR[i]) * (y - XOR[i]);
      const dy = (y - XOR[i]) * y * (1 - y);
      g[6] += dy * h0; g[7] += dy * h1; g[8] += dy;
      const d0 = dy * w[6] * h0 * (1 - h0), d1 = dy * w[7] * h1 * (1 - h1);
      g[0] += d0 * x[0]; g[1] += d0 * x[1]; g[2] += d0; g[3] += d1 * x[0]; g[4] += d1 * x[1]; g[5] += d1;
    }
    return E;
  }
  const solved = () => IN.every((x, i) => Math.abs(fwd(x)[0] - XOR[i]) < 0.1);
  function start(ws, prog) { w = ws.slice(); step = new Array(9).fill(0); epoch = 0; curve = []; fromProg = prog; const g = new Array(9); curve.push(grad(g)); draw(prog ? "The program's starting weights. Train, and watch the four corners of the square." : "Random starting weights in [−1, 1]. Some starts learn XOR quickly, some slowly, and some get stuck."); }
  function train(n) {
    const g = new Array(9);
    for (let k = 0; k < n; k++) {
      if (solved()) return true;
      grad(g);
      for (let j = 0; j < 9; j++) { step[j] = -RATE * g[j] + MOM * step[j]; w[j] += step[j]; }
      epoch++; curve.push(grad(g));
    }
    return solved();
  }
  function draw(msg) {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 420 300"}, view), G = 24, S = 240, ox = 20, oy = 20;
    for (let a = 0; a < G; a++) for (let b = 0; b < G; b++) {
      const x = (a + 0.5) / G, y = 1 - (b + 0.5) / G, v = fwd([x, y])[0];
      sv("rect", {x: ox + a * S / G, y: oy + b * S / G, width: S / G + 0.5, height: S / G + 0.5, fill: v > 0.5 ? "var(--red)" : "var(--blue)", "fill-opacity": Math.min(0.85, Math.abs(v - 0.5) * 1.7 + 0.08)}, svg);
    }
    IN.forEach((x, i) => {
      const out = fwd(x)[0];
      sv("circle", {cx: ox + x[0] * S, cy: oy + (1 - x[1]) * S, r: 11, fill: XOR[i] ? "var(--red)" : "var(--blue)", stroke: "var(--paper)", "stroke-width": 3}, svg);
      const t = sv("text", {x: ox + x[0] * S + (x[0] ? -16 : 16), y: oy + (1 - x[1]) * S + (x[1] ? 26 : -16), "text-anchor": x[0] ? "end" : "start", "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg);
      t.textContent = `${x[0]}${x[1]} → ${out.toFixed(3)}`;
    });
    const c = sv("text", {x: ox, y: oy + S + 22, "font-size": 11.5, fill: "var(--muted)"}, svg); c.textContent = "red: output above 0.5 · blue: below";
    // the error curve
    const cx0 = 285, cw = 125, cy0 = 260, ch = 200, maxE = Math.max(...curve, 0.55), n = Math.max(curve.length - 1, 1);
    sv("line", {x1: cx0, y1: cy0, x2: cx0 + cw, y2: cy0, stroke: "var(--axis)"}, svg); sv("line", {x1: cx0, y1: cy0, x2: cx0, y2: cy0 - ch, stroke: "var(--axis)"}, svg);
    sv("path", {d: curve.map((e, i) => `${i ? "L" : "M"}${cx0 + i / n * cw},${cy0 - e / maxE * ch}`).join(" "), fill: "none", stroke: "var(--red)", "stroke-width": 2}, svg);
    const lt = sv("text", {x: cx0, y: cy0 + 18, "font-size": 11.5, fill: "var(--muted)"}, svg); lt.textContent = "error by epoch";
    const st = document.getElementById("bp-stats"); st.innerHTML = "";
    el("div", {}, st, `epoch: ${epoch}`);
    el("div", {}, st, `error: ${curve[curve.length - 1].toFixed(4)}`);
    if (fromProg) { const p = PROG.find(([e]) => e === epoch); if (p) el("div", {}, st, `the program's error at epoch ${epoch}: ${p[1].toFixed(4)}`); }
    if (msg) document.getElementById("bp-say").textContent = msg;
  }
  document.getElementById("bp-10").addEventListener("click", () => { const ok = train(10); draw(ok ? `Learned: every output within 0.1 of its target, after ${epoch} epochs.` : `Epoch ${epoch}: the hidden units are still finding their roles.`); });
  document.getElementById("bp-end").addEventListener("click", () => { const ok = train(5000); draw(ok ? `Learned after ${epoch} epochs${fromProg ? ` (the program: ${__EP__})` : ""}.` : `Stuck after ${epoch} epochs: this start found a dead end. Try another.`); });
  document.getElementById("bp-prog").addEventListener("click", () => start(INIT, true));
  document.getElementById("bp-rand").addEventListener("click", () => start(Array.from({length: 9}, () => Math.random() * 2 - 1), false));
  start(INIT, true);
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How backpropagation combined older ideas, and where it led")
    W = 210
    nodes = {
        "cr": (20, 20, "The chain rule", "slopes of a chain of steps multiply", "calculus", "ink"),
        "pc": (395, 20, "The perceptron", "one layer of weights, nudged by errors", "Era 5, topic 9", "ink"),
        "ad": (770, 20, "Reverse mode", "all the slopes of a program in one backward pass", "Linnainmaa, 1970", "ink"),
        "wb": (770, 180, "Applied to networks", "⊕ the method for neural networks", "Werbos, 1974 and 1981", "ink"),
        "bp": (395, 180, "Backpropagation", "⊕ hidden units learn their own features", "Rumelhart, Hinton, Williams, 1986", "red"),
        "ml": (20, 340, "Multi-layer networks", "hidden layers solve what one layer cannot, such as XOR", "", "ink"),
        "today": (395, 490, "Today", "\"triggered a boom in neural network research\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("cr", "bp", ports=("bottom", "top:0.15"))
    D.edge("pc", "bp", ports=("bottom", "top"))
    D.edge("ad", "wb", ports=("bottom", "top"))
    D.edge("wb", "bp", ports=("left", "right"), dashed=True, label="found again", at=0.5, dy=-8)
    D.edge("bp", "ml", ports=("bottom:0.15", "top"))
    D.edge("bp", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: Wikipedia on the 1986 paper's effect. Dashed: the sources differ on who should be credited for what (see the evidence).", "caption")
    return D


def chain(d):
    pc, gr, xr = d["perc"], d["grad"], d["xor"]
    steps = [
        (f"One layer cannot learn XOR: the perceptron never got all 4 cases (at best {pc['best']} at once), and none of {pc['lines']} lines separates them",
         "Hidden units between input and output: a 2-2-1 network can represent XOR", "multi-layer networks"),
        ("But how should a hidden unit change? Its error is not seen at the output",
         f"Backpropagation: the chain rule run backwards gives all {gr['w']} slopes for {gr['fwd']} + {gr['bwd']} multiplications, against {gr['wig']} by wiggling each weight", "Rumelhart, Hinton and Williams, 1986"),
        (f"Gradient descent can stall: {xr['stuck']} of {xr['starts']} random starts never learned XOR",
         f"Start again from other random weights: {xr['ok']} of {xr['starts']} starts succeed, the median in {xr['med']} epochs", "the program's runs"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from one layer to many, and how to train them")
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
    pc, xr, gr, run, fin = d["perc"], d["xor"], d["grad"], d["run"], d["final"]
    out_rows = [[f"({p[0][0]}, {p[0][1]})", "1" if p[0] in ("01", "10") else "0", p[1]] for p in fin["outs"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The perceptron (Era 5) learned one layer of weights. Networks with hidden layers could do more, but needed a way to tell each hidden weight how to change. The chain rule of calculus, run backwards through a computation, gives every slope at once; Linnainmaa described that for computer programs in 1970, Werbos applied it to networks, and Rumelhart, Hinton and Williams showed in 1986 what hidden units learn with it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the 1986 paper that made the method famous. Blue: what followed."),
        ]),
        dict(id="play", eyebrow="Try it", title="Teach a network exclusive-or", toc="Try it", blocks=[
            dict(type="p", text=f"Two inputs, two hidden units, one output, all sigmoid, trained by backpropagation exactly as the program does it (rate {xr['rate']}, momentum {xr['mom']}), from the program's starting weights. The square shows the network's output for every input between 0 and 1: red above 0.5, blue below. XOR wants red at (0, 1) and (1, 0) and blue at (0, 0) and (1, 1), which no straight line can split. Train and watch: for a long time nothing seems to happen, then the hidden units divide the job and the colours snap into place. The widget repeats the program's arithmetic, so its error matches the program's at every tenth epoch. Then try random starts."),
            dict(type="widget", html=BP_HTML,
                 js=BP_JS.replace("__INIT__", json.dumps(d["init"])).replace("__PROG__", json.dumps(run["curve"])).replace("__RATE__", xr["rate"]).replace("__MOM__", xr["mom"]).replace("__EP__", str(run["epochs"])),
                 css=BP_CSS,
                 fallback=dict(type="table", head=["Input", "Target", "Output after training"], num=[1, 2], rows=out_rows),
                 note="In the interactive edition you can train the network yourself and watch its output change."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="The chain rule, run backwards", toc="How it works", blocks=[
            dict(type="p", text="**Forward.** Each unit adds its inputs times their weights, plus a bias, and squashes the sum with the sigmoid 1/(1 + e⁻ˢ). The error is half the sum of the squared misses."),
            dict(type="p", text="**Backward.** The slope of the error with respect to the output unit's sum is δ_y = (y − target) · y(1 − y). A hidden unit's δ is the δ of the unit it feeds, times the weight between them, times its own h(1 − h). The slope for any weight is the δ of the unit it feeds times the value flowing through it. One backward pass computes every δ, so every slope, for about the cost of one more forward pass."),
            dict(type="svg", name="network", draw=network_svg(d), alt="A 2-2-1 network with forward and backward passes", width=780),
            dict(type="p", text="**Descent.** Move every weight a little against its slope (here with momentum: part of the previous step is repeated), and repeat over the training cases until the error is small."),
            dict(type="callout", kind="key", label="Key idea",
                 text="To learn, every weight needs to know which way to move. Measuring that by wiggling each weight costs one run of the network per weight; the chain rule run backwards gets all of them for the price of about one run."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Slopes, starts and a plateau", toc="Measured", blocks=[
            dict(type="p", text=f"**One layer.** The perceptron rule learned AND in {pc['andep']} epochs, but in {pc['epochs']} epochs never got all four XOR cases right (at best {pc['best']} at once); of {pc['lines']} straight lines tried on a grid, the best put {pc['bestline']} of the 4 cases on the right side."),
            dict(type="p", text=f"**The slopes.** In a network of {gr['nin']} inputs, {gr['nh']} hidden units and {gr['nout']} outputs ({gr['w']} weights), backpropagation took one forward run ({gr['fwd']} multiplications) and one backward run ({gr['bwd']}); wiggling each weight up and down took {gr['runs']} forward runs ({gr['wig']} multiplications). The two sets of {gr['w']} slopes agreed to a relative difference of at most {C.sci(gr['diff'])}."),
            dict(type="p", text=f"**Random starts.** From 100 random starting weights in [−1, 1], {xr['ok']} learned XOR within {xr['max']} epochs (the median after {xr['med']}, the fastest {xr['fast']}, the slowest {xr['slow']}); the other {xr['stuck']} got stuck."),
            dict(type="svg", name="curve", draw=curve_svg(d), alt="Error against epoch while learning XOR", width=760),
            dict(type="table", head=["Input", "Target", "Output after training"], num=[1, 2], rows=out_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Found several times, famous once", toc="The evidence", blocks=[
            dict(type="p", text="David Rumelhart, Geoffrey Hinton and Ronald Williams, \"Learning representations by back-propagating errors\" (*Nature* 323: 533–536, October 1986): \"We describe a new learning procedure, back-propagation, for networks of neurone-like units.\" The abstract explains that adjusting the weights to reduce the output error makes hidden units come to represent important features of the task, which sets it apart from the perceptron-convergence procedure. Wikipedia's article on Williams says the paper \"triggered a boom in neural network research\"."),
            dict(type="p", text="The method had been found before. Linnainmaa's 1970 master's thesis at Helsinki \"introduced the reverse mode of automatic differentiation\", without reference to neural networks (Wikipedia). Schmidhuber's survey traces the idea to Kelley (1960), Bryson (1961) and Dreyfus (1962), dates \"the first NN-specific application of efficient BP\" to Werbos in 1981, and says the 1986 paper \"significantly contributed to the popularisation of BP for NNs\". Widrow and Lehr (1990) instead credit Werbos's 1974 dissertation with first publishing the method, note Parker's rediscovery (1982, MIT report 1985), and say Rumelhart, Hinton and Williams \"also rediscovered the technique\". The catalog marks the credit for 1974 **Disputed**."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The perceptron, with depth", toc="Full circle", blocks=[
            dict(type="p", text="Era 5's perceptron adjusted its weights by the error at its single output. Backpropagation keeps that idea and passes the error back through any number of layers, so each hidden unit gets its share of the blame."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The perceptron could not learn XOR in {pc['epochs']} epochs. Two hidden units trained by backpropagation learned it in {run['epochs']}, from the starting weights shown above."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why can no single layer learn XOR?", "Its output is a threshold on a weighted sum, so it separates the plane with a straight line, and no line puts (0, 1) and (1, 0) on one side and (0, 0) and (1, 1) on the other."),
            ("The output is 0.9 and the target 1. What is δ_y?", "(0.9 − 1) × 0.9 × 0.1 = −0.009."),
            ("A network has a million weights. How many forward runs does wiggling each weight need, and how many does backpropagation need?", "Two million (up and down for each); backpropagation needs one forward and one backward run."),
            ("Why does the error stay near 0.5 for a long time before falling?", "At first both hidden units do nearly the same thing; only after small differences grow do they split the job, and then the error drops quickly."),
            ("Some random starts never learn XOR. What can you do?", "Start again from other random weights, or change the learning rate or the number of hidden units."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Learning representations by back-propagating errors (1986)", text="*Nature* 323: 533–536, by Rumelhart, Hinton and Williams; the text was not opened for this book, only its record and abstract.",
                 draw=C.draw_manuscript, link="https://mlanthology.org/misc/1986/rumelhart1986misc-learning", link_text="The paper's record (ML Anthology)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Backpropagation", d["checks"],
                           "the perceptron on AND and XOR (and 531,441 lines, none separating XOR), 100 random starts on XOR, every one of 325 backpropagated slopes against wiggling the weight, and one XOR run from fixed weights.",
                           ["static double errorAndGradient(double[] w, double[] t, double[] grad)"]),
    ]
    return dict(
        title="Backpropagation", date="1970–1986",
        description="Era 7, topic 7 of The Algorithm Evolution Atlas: training hidden layers with the chain rule run backwards, from Linnainmaa and Werbos to Rumelhart, Hinton and Williams.",
        lede="A single layer of weights cannot learn even exclusive-or. Networks with hidden layers can, if each hidden weight can be told which way to move. Running the chain rule backwards tells all of them at once.",
        fieldnote=f"I watched two hidden units learn exclusive-or. For two hundred epochs the error barely moved; then the units divided the work between them and the error fell to almost nothing by epoch {run['epochs']}. The method had been found several times; it took a four-page paper in 1986 for this species to notice it.",
        card=[("When", "1970 (Linnainmaa); 1981 (Werbos); 1986 (Rumelhart, Hinton, Williams)"),
              ("Where", "Helsinki; the 1986 paper in Nature"),
              ("What hurt", "No well-known way to train hidden layers"),
              ("The fix", "The chain rule, backwards: every slope in one pass"),
              ("Checked", f"{gr['w']} slopes agree with wiggling to {C.sci(gr['diff'])}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Backpropagation.java`.",
    )
