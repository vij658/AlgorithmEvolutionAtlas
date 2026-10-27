"""Era 8, topic 6: Long short-term memory. Every number is parsed from LongShortTermMemory.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"gradcheck: (\d+)-step sequence, (\d+) hidden units ; every one of the RNN's (\d+) weights and the LSTM's (\d+) weights .*? ; relative difference of the whole gradient: RNN ([\d.eE+-]+), LSTM ([\d.eE+-]+)", ln):
            d["grad"] = dict(T=m.group(1), H=m.group(2), nr=m.group(3), nl=m.group(4), r=m.group(5), l=m.group(6))
        elif ln.startswith("lag: "):
            d["lag"] = [dict(T=a, rnn=b, rs=c, lstm=e, ls=f) for a, b, c, e, f in
                        re.findall(r"T = (\d+): RNN ([\d.]+)% correct \(first input moves the output by ([\d.]+)\), LSTM ([\d.]+)% \(by ([\d.]+)\)", ln)]
            d["steps"] = re.search(r"([\d,]+) steps of Adam", ln).group(1)
        elif ln.startswith("decay: "):
            parts = re.findall(r"(untrained|trained for T = 80): ((?:\d+:[\d.e+-]+:[\d.e+-]+ ?)+)", ln)
            d["decay"] = {name: [(int(a), float(b), float(c)) for a, b, c in (p.split(":") for p in vals.split())] for name, vals in parts}
        elif ln.startswith("widget: "):
            m = re.search(r"T = (\d+), trained from seed (\d+), ([\d.]+)% correct .*? weights rounded to 4 decimals: ([-\d.,]+) ; example: sign (-?\d+), noise from the generator with seed (\d+) ; final output logit ([-\d.]+) ; memory c after each step: (.*)$", ln)
            d["widget"] = dict(T=int(m.group(1)), seed=m.group(2), acc=m.group(3), w=[float(x) for x in m.group(4).split(",")], sign=int(m.group(5)),
                               noise=int(m.group(6)), logit=m.group(7), cells=[[float(x) for x in s.split(",")] for s in m.group(8).split()])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def cell_svg(d):
    """The LSTM cell: the memory line with its forget and input gates, and the output gate."""
    def draw(t, standalone):
        o = []
        W, H = 760, 330
        o.append(C.text(20, 26, "One LSTM cell at step t: the memory c runs along the top, changed only by × and +", t["ink"], 13, "start", 700))
        y = 90
        # memory line
        o.append(C.text(40, y + 5, "cₜ₋₁", t["ink"], 15, "middle", 700))
        o.append(C.line(62, y, 690, y, t["red"], 3))
        o.append(C.text(720, y + 5, "cₜ", t["ink"], 15, "middle", 700))
        for cx, sym in ((230, "×"), (420, "+")):
            o.append(f'<circle cx="{cx}" cy="{y}" r="17" fill="{t["surface"]}" stroke="{t["ink"]}" stroke-width="2"/>')
            o.append(C.text(cx, y + 7, sym, t["ink"], 20, "middle", 700))
        # gates
        boxes = [(195, "f", "forget gate", "keep (1) or forget (0)", t["blue"]), (315, "i", "input gate", "let new content in", t["blue"]),
                 (455, "g", "candidate", "tanh: the new content", t["yellow"]), (590, "o", "output gate", "how much to show", t["blue"])]
        for x, sym, name, what, col in boxes:
            o.append(C.rect(x, 190, 90, 46, t["surface"], col, 2))
            o.append(C.text(x + 45, 211, sym, t["ink"], 15, "middle", 700))
            o.append(C.text(x + 45, 228, name, t["muted"], 11, "middle"))
            o.append(C.text(x + 45, 254, what, t["muted"], 11, "middle"))
        o.append(C.path(f"M240,190 L232,{y + 17}", t["ink"], "none", 1.6))
        # i and g meet at a ×, then go up to the +
        o.append(f'<circle cx="420" cy="150" r="15" fill="{t["surface"]}" stroke="{t["ink"]}" stroke-width="2"/>')
        o.append(C.text(420, 156, "×", t["ink"], 18, "middle", 700))
        o.append(C.path("M360,190 L408,160", t["ink"], "none", 1.6))
        o.append(C.path("M500,190 L432,160", t["ink"], "none", 1.6))
        o.append(C.path(f"M420,135 L420,{y + 17}", t["ink"], "none", 1.6))
        # output: tanh(c) x o -> h
        o.append(C.path(f"M620,{y} L620,140", t["ink"], "none", 1.6))
        o.append(C.text(632, 125, "tanh", t["muted"], 11.5))
        o.append(f'<circle cx="635" cy="160" r="15" fill="{t["surface"]}" stroke="{t["ink"]}" stroke-width="2"/>')
        o.append(C.text(635, 166, "×", t["ink"], 18, "middle", 700))
        o.append(C.path("M635,190 L635,175", t["ink"], "none", 1.6))
        o.append(C.path("M650,160 L710,160", t["ink"], "none", 1.6))
        o.append(C.text(722, 165, "hₜ", t["ink"], 15, "middle", 700))
        o.append(C.text(20, 290, "Each gate is a sigmoid of the input and the previous output hₜ₋₁. cₜ = f × cₜ₋₁ + i × g ; hₜ = o × tanh(cₜ).", t["ink"], 12.5))
        o.append(C.text(20, 310, "While f ≈ 1 and i ≈ 0, cₜ = cₜ₋₁, and the error flowing back along the top line passes unchanged.", t["ink"], 12.5))
        return C.svg_doc(W, H, "".join(o), "The LSTM cell", t, standalone, 0.55, 760)
    return draw


def decay_svg(d):
    dec = d["decay"]

    def draw(t, standalone):
        o = []
        W, H = 760, 360
        x0, x1, y0, y1 = 80, 700, 290, 50
        lo = -60
        X = lambda k: x0 + (k - 1) / 78 * (x1 - x0)
        Y = lambda v: y0 - (math.log10(max(v, 1e-60)) - lo) / (0 - lo) * (y0 - y1)
        o.append(C.text(20, 26, "The error signal on its way back through 80 steps (log scale)", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        for e in (0, -10, -20, -30, -40, -50, -60):
            o.append(C.text(x0 - 8, Y(10 ** e) + 4, "1" if e == 0 else f"10{str(e).translate(str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))}", t["muted"], 11.5, "end"))
        for k in (1, 20, 40, 60, 79):
            o.append(C.text(X(k), y0 + 18, str(k), t["muted"], 11.5, "middle"))
        o.append(C.text((x0 + x1) / 2, y0 + 40, "steps back from the end", t["muted"], 12, "middle"))
        series = [("untrained", 1, t["red"], "RNN, untrained", ";stroke-dasharray:6 4"), ("trained for T = 80", 1, t["red"], "RNN, trained", ""),
                  ("untrained", 2, t["blue"], "LSTM memory, untrained", ";stroke-dasharray:6 4"), ("trained for T = 80", 2, t["blue"], "LSTM memory, trained", "")]
        for name, col, colour, lab, dash in series:
            pts = dec[name]
            o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(p[0]):.1f},{Y(p[col]):.1f}" for i, p in enumerate(pts)), colour, "none", 2.2, dash))

        for i, (name, col, colour, lab, dash) in enumerate(series):
            ly = Y(1e-40) + i * 20
            o.append(C.line(X(4), ly - 4, X(10), ly - 4, colour, 2.2, dash))
            o.append(C.text(X(11), ly, lab, colour, 12, "start", 700))
        return C.svg_doc(W, H, "".join(o), "Error signal against steps back, RNN and LSTM", t, standalone, 0.55, 760)
    return draw


LS_HTML = """
<div class="board ls-board">
  <div style="min-width:0"><div class="ls-view" id="ls-view"></div></div>
  <div style="min-width:0">
    <div class="ls-btns"><button type="button" id="ls-plus">First sign +1</button><button type="button" id="ls-minus">First sign −1</button><button type="button" id="ls-noise">New noise</button><button type="button" id="ls-prog">The program's example</button></div>
    <div class="ls-stats" id="ls-stats"></div>
    <p class="say" id="ls-say" aria-live="polite"></p>
  </div>
</div>
"""

LS_CSS = """
.ls-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.ls-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.ls-btns button{font-size:13px}
.ls-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

LS_JS = r"""
(() => {
  const view = document.getElementById("ls-view");
  if (!view) return;
  const P = __W__, T = __T__, PROG = __PROG__, H = 4, Z = 6, G = H * Z + H, NP = P.length;
  let s32, sign = PROG.sign, seed = PROG.noise, x;
  function next32() { s32 = (Math.imul(s32, 1664525) + 1013904223) | 0; return (s32 >>> 0) / 4294967296; }
  const sig = a => 1 / (1 + Math.exp(-a));
  function sequence() { s32 = seed; x = []; for (let t = 0; t < T; t++) x.push([t === 0 ? sign : 0, 0]); for (let t = 0; t < T; t++) x[t][1] = 2 * next32() - 1; }
  function run() {
    let h = [0, 0, 0, 0], c = [0, 0, 0, 0];
    const cs = [], fs = [];
    for (let t = 0; t < T; t++) {
      const z = [x[t][0], x[t][1], h[0], h[1], h[2], h[3]], gate = [[], [], [], []];
      for (let q = 0; q < 4; q++) for (let u = 0; u < H; u++) {
        let a = P[q * G + H * Z + u];
        for (let k = 0; k < Z; k++) a += P[q * G + u * Z + k] * z[k];
        gate[q][u] = q === 3 ? Math.tanh(a) : sig(a);
      }
      const nc = [], nh = [];
      for (let u = 0; u < H; u++) { nc[u] = gate[1][u] * c[u] + gate[0][u] * gate[3][u]; nh[u] = gate[2][u] * Math.tanh(nc[u]); }
      c = nc; h = nh; cs.push(c.slice()); fs.push(gate[1].slice());
    }
    let s = P[NP - 1];
    for (let u = 0; u < H; u++) s += P[4 * G + u] * h[u];
    return {logit: s, cs, fs};
  }
  const COL = ["var(--red)", "var(--blue)", "var(--yellow)", "var(--ink)"];
  function draw(msg) {
    const r = run();
    view.innerHTML = "";
    const W = 440, Hh = 300, x0 = 36, x1 = 430, y0 = 270, y1 = 20;
    let mx = 0; for (const c of r.cs) for (const v of c) mx = Math.max(mx, Math.abs(v)); mx = Math.max(1, Math.ceil(mx));
    const X = t => x0 + t / (T - 1) * (x1 - x0), Y = v => (y0 + y1) / 2 - v / mx * (y0 - y1) / 2;
    const svg = sv("svg", {viewBox: `0 0 ${W} ${Hh + 10}`, role: "img", "aria-label": "Memory cells over time"}, view);
    sv("line", {x1: x0, y1: Y(0), x2: x1, y2: Y(0), stroke: "var(--axis)"}, svg);
    sv("text", {x: x0 - 6, y: Y(mx) + 4, "text-anchor": "end", "font-size": 11, fill: "var(--muted)"}, svg, `+${mx}`);
    sv("text", {x: x0 - 6, y: Y(-mx) + 4, "text-anchor": "end", "font-size": 11, fill: "var(--muted)"}, svg, `−${mx}`);
    sv("text", {x: x0, y: Hh + 6, "font-size": 11, fill: "var(--muted)"}, svg, "step 1");
    sv("text", {x: x1, y: Hh + 6, "font-size": 11, fill: "var(--muted)", "text-anchor": "end"}, svg, `step ${T}`);
    sv("rect", {x: X(0) - 4, y: Y(0) - 18 * sign - (sign > 0 ? 0 : 0), width: 8, height: 18, fill: sign > 0 ? "var(--red)" : "var(--blue)", transform: sign < 0 ? `translate(0,18)` : null}, svg);
    for (let u = 0; u < H; u++) sv("path", {d: r.cs.map((c, t) => `${t ? "L" : "M"}${X(t).toFixed(1)},${Y(c[u]).toFixed(1)}`).join(" "), stroke: COL[u], fill: "none", "stroke-width": 2}, svg);
    const p = sig(r.logit);
    const st = document.getElementById("ls-stats"); st.innerHTML = "";
    el("div", {}, st, `first sign: ${sign > 0 ? "+1" : "−1"}, then ${T - 1} steps of noise only`);
    el("div", {}, st, `memory cells after the last step: ${r.cs[T - 1].map(v => v.toFixed(3)).join(", ")}`);
    el("div", {}, st, `output: ${r.logit.toFixed(4)} → says ${r.logit > 0 ? "+1" : "−1"} (chance of +1: ${p.toFixed(4)})`);
    const isProg = sign === PROG.sign && seed === PROG.noise;
    document.getElementById("ls-say").textContent = msg || (isProg ? `The program's example: its output was ${PROG.logit}.` : "");
  }
  document.getElementById("ls-plus").addEventListener("click", () => { sign = 1; sequence(); draw("The sign is seen once, at step 1; the network must carry it through the noise."); });
  document.getElementById("ls-minus").addEventListener("click", () => { sign = -1; sequence(); draw("The sign is seen once, at step 1; the network must carry it through the noise."); });
  document.getElementById("ls-noise").addEventListener("click", () => { seed = (seed * 7 + 13) % 100000; sequence(); draw(`New noise (seed ${seed}). The sign at step 1 is unchanged.`); });
  document.getElementById("ls-prog").addEventListener("click", () => { sign = PROG.sign; seed = PROG.noise; sequence(); draw(); });
  sequence(); draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How LSTM combined older ideas, and where it led")
    W = 210
    nodes = {
        "bp": (20, 20, "Backpropagation", "slopes by the chain rule", "Era 7", "ink"),
        "rnn": (395, 20, "Recurrent networks", "a hidden state carried step to step", "", "ink"),
        "van": (770, 20, "Vanishing gradients", "the error shrinks or explodes with distance", "Hochreiter, 1991", "ink"),
        "lstm": (395, 180, "LSTM", "⊕ a memory cell with a constant error carousel", "Hochreiter, Schmidhuber, 1997", "red"),
        "fg": (20, 340, "The forget gate", "⊕ the cell can reset itself", "Gers, Schmidhuber, Cummins, 1999", "ink"),
        "pp": (770, 340, "Peepholes", "gates that see the cell", "2000", "ink"),
        "today": (395, 490, "Speech and translation", "Google Voice, 2015; Google Translate, 2016", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("bp", "lstm", ports=("bottom", "top:0.15"))
    D.edge("rnn", "lstm", ports=("bottom", "top"))
    D.edge("van", "lstm", ports=("bottom", "top:0.85"), label="the problem", at=0.5, dx=8, anchor="start")
    D.edge("lstm", "fg", ports=("bottom:0.15", "top"))
    D.edge("lstm", "pp", ports=("bottom:0.85", "top"))
    D.edge("fg", "today", ports=("bottom", "left"))
    D.text(20, 615, "Today: the uses Wikipedia records. The program uses the cell with a forget gate.", "caption")
    return D


def chain(d):
    lag = {r["T"]: r for r in d["lag"]}
    dec = d["decay"]["untrained"]
    steps = [
        (f"A recurrent net learns a 20-step lag ({lag['20']['rnn']}%) but not 40 ({lag['40']['rnn']}%)",
         f"An LSTM cell: {lag['80']['lstm']}% correct at 80 steps", "Hochreiter and Schmidhuber, 1997"),
        (f"Why: the error signal shrinks at every step; 79 steps back it is {C.sci(f'{dec[-1][1]:.1e}')} of its size",
         f"The constant error carousel: a memory changed only by × and +, which keeps {C.sci(f'{dec[-1][2]:.1e}')} even untrained", "Hochreiter and Schmidhuber, 1997"),
        ("A cell that can only add cannot clear an old memory for the next sequence",
         "A gate for forgetting, learned like the others", "Gers, Schmidhuber and Cummins, 1999"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from short memories to long ones")
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
    g, lag, dec, wg = d["grad"], d["lag"], d["decay"], d["widget"]
    lag_rows = [[r["T"], r["rnn"] + "%", r["rs"], r["lstm"] + "%", r["ls"]] for r in lag]
    dec_rows = [[str(k), C.sci(f"{a:.1e}"), C.sci(f"{b:.1e}"), C.sci(f"{c:.1e}"), C.sci(f"{e:.1e}")]
                for (k, a, b), (_, c, e) in zip(dec["untrained"], dec["trained for T = 80"])]
    last = wg["cells"][-1]
    l80 = next(r for r in lag if r["T"] == "80")
    l40 = next(r for r in lag if r["T"] == "40")
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Backpropagation (Era 7) gives every weight its slope; run backwards through a recurrent network's steps, it trains networks that read sequences. Hochreiter's 1991 thesis showed why such training fails over long gaps: the error signal shrinks or explodes exponentially. Hochreiter and Schmidhuber's answer was a memory that the error can cross unchanged, guarded by gates that learn. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: LSTM. Blue: where it was used."),
        ]),
        dict(id="play", eyebrow="Try it", title="Carry one sign through thirty steps of noise", toc="Try it", blocks=[
            dict(type="p", text=f"The program trained this small LSTM (4 memory cells) on sequences of {wg['T']} steps: at step 1 one input carries a sign, +1 or −1; after that it is 0, while a second input carries random noise at every step. At the last step the network must say which sign it saw; it was right on {wg['acc']}% of 1,000 new sequences. The lines are its four memory cells over the 30 steps. Flip the first sign and watch the memories take the other path; try new noise and watch them hold. The widget runs the program's weights."),
            dict(type="widget", html=LS_HTML, js=LS_JS.replace("__W__", json.dumps(wg["w"])).replace("__T__", str(wg["T"]))
                 .replace("__PROG__", json.dumps(dict(sign=wg["sign"], noise=wg["noise"], logit=wg["logit"]))), css=LS_CSS,
                 fallback=dict(type="table", head=["Step", "Cell 1", "Cell 2", "Cell 3", "Cell 4"], num=[0, 1, 2, 3, 4],
                               rows=[[str(t + 1)] + [f"{v:.3f}" for v in c] for t, c in enumerate(wg["cells"]) if t in (0, 4, 9, 14, 19, 24, 29)]),
                 note=f"In the interactive edition you can flip the first sign and change the noise. In the program's example (sign −1) the output was {wg['logit']}."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A memory the error can cross", toc="How it works", blocks=[
            dict(type="p", text="**A recurrent network** reads a sequence one step at a time: hₜ = tanh(W [xₜ, hₜ₋₁] + b). To train it, backpropagation runs backwards through the steps, and at every step the error is multiplied by W and by the slope of tanh. Multiply by something smaller than 1 eighty times and almost nothing is left; larger than 1, and it explodes."),
            dict(type="p", text="**The LSTM cell** keeps a separate memory c that is changed only by multiplying and adding: cₜ = f × cₜ₋₁ + i × g. The gates f (forget), i (input) and o (output) are numbers between 0 and 1 computed from the input and the previous output; g is the proposed new content. The output is hₜ = o × tanh(cₜ). While f stays near 1 and i near 0, the memory, and the error flowing back through it, pass unchanged: the \"constant error carousel\". (In the 1997 cell f was always 1; the forget gate came in 1999.)"),
            dict(type="svg", name="cell", draw=cell_svg(d), alt="The LSTM cell with its forget, input and output gates", width=760),
            dict(type="svg", name="decay", draw=decay_svg(d), alt="The error signal against steps back, for an RNN and an LSTM", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do not make the network learn to preserve a memory through repeated multiplications; give it a path where preserving is the default, and let it learn when to write and when to read."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Twenty steps, forty, eighty", toc="Measured", blocks=[
            dict(type="p", text=f"**Slopes checked.** On a {g['T']}-step sequence, backpropagation through time against central differences for every one of the RNN's {g['nr']} weights and the LSTM's {g['nl']}: the whole gradients differ by {C.sci(g['r'])} and {C.sci(g['l'])} of their size."),
            dict(type="p", text=f"**The long-lag task.** A plain recurrent network and an LSTM, each with 4 hidden units, trained by {d['steps']} steps of Adam and tested on 1,000 new sequences. \"First input moves the output by\" is half the change in the output when only the first sign is flipped: zero means the network has forgotten it."),
            dict(type="table", head=["Steps T", "RNN correct", "First input moves the RNN by", "LSTM correct", "First input moves the LSTM by"], num=[0, 1, 2, 3, 4], rows=lag_rows, hl=3),
            dict(type="p", text="**The error signal on its way back**, on one 80-step sequence, relative to its size one step back:"),
            dict(type="table", head=["Steps back", "RNN, untrained", "LSTM memory, untrained", "RNN, trained (T = 80)", "LSTM memory, trained"], num=[0, 1, 2, 3, 4], rows=dec_rows),
            dict(type="p", text="Training the RNN did not save it: its error signal 79 steps back is still far too small to learn from. The trained LSTM's memory still carries a few percent."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A thousand steps in Munich and Lugano", toc="The evidence", blocks=[
            dict(type="p", text="Hochreiter (Technische Universität München) and Schmidhuber (IDSIA, Lugano), *Neural Computation* 9(8), 1997: LSTM can learn to \"bridge minimal time lags in excess of 1000 discrete time steps\" by enforcing constant error flow through \"constant error carrousels\"; \"Multiplicative gate units learn to open and close access to the constant error flow\"; \"LSTM is local in space and time; its computational complexity per time step and weight is O(1)\". With backpropagation through time, error signals tend \"to either (1) blow up or (2) vanish\". On the hardest noise-free task, \"LSTM solves it, while BPTT and RTRL already fail in case of 10-step minimal time lags\"."),
            dict(type="p", text="Wikipedia: \"Sepp Hochreiter's 1991 German diploma thesis analyzed the vanishing gradient problem\"; an early version appeared in a 1995 technical report; the forget gate (Gers, Schmidhuber and Cummins, 1999) is \"the most commonly used version today\"; Google used an LSTM for speech recognition on Google Voice in 2015 and in its neural machine translation system in 2016. *Dive into Deep Learning* gives the gates as now written: Cₜ = Fₜ ⊙ Cₜ₋₁ + Iₜ ⊙ C̃ₜ and Hₜ = Oₜ ⊙ tanh(Cₜ)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Backpropagation, kept alive", toc="Full circle", blocks=[
            dict(type="p", text="Era 7's backpropagation worked for networks a few layers deep. Read through time, a recurrent network is as deep as its sequence is long, and the same chain rule that made backpropagation work made its error signal vanish. LSTM did not change the chain rule; it changed the network so that the chain contains a link of exactly 1."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"At 40 steps the plain network was right {l40['rnn']}% of the time, a coin; its first input moved its answer by {l40['rs']}. The LSTM, with the same four hidden units, was right {l80['lstm']}% of the time at 80."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("An error signal is multiplied by 0.9 at every step. How much is left after 80 steps?", "0.9⁸⁰ ≈ 0.0002."),
            ("In the cell, f = 1 and i = 0 for ten steps. What happens to the memory c?", "Nothing: cₜ = 1 × cₜ₋₁ + 0, so it is carried unchanged."),
            ("Why does the output gate matter if the memory is kept anyway?", "It decides when the memory affects the output; otherwise a stored sign would disturb every step's answer."),
            ("The plain RNN got 100% at 20 steps and about 50% at 40. What does 50% mean here?", "Guessing: with two signs equally likely, a network that has forgotten the first input is right half the time."),
            ("Why might a cell need to forget?", "To clear one sequence's memory before the next; without it the memory could only grow, as Gers, Schmidhuber and Cummins found."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Hochreiter and Schmidhuber's paper (1997)", text="*Neural Computation* 9(8), 1735–1780.",
                 draw=C.draw_manuscript, link="https://papers.baulab.info/papers/Hochreiter-1997.pdf", link_text="The paper (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LongShortTermMemory", d["checks"],
                           "every weight's slope against central differences for both networks, the accuracy at each lag, the error signal's decay, and the widget's trained network.",
                           ["double logit(double[][] x, boolean keep)"]),
    ]
    return dict(
        title="Long Short-Term Memory", date="1997",
        description="Era 8, topic 6 of The Algorithm Evolution Atlas: Hochreiter and Schmidhuber's LSTM (1997), the vanishing gradient it fixed, and a trained cell carrying one sign through thirty steps of noise.",
        lede="A recurrent network trained by backpropagation forgets anything more than a few steps old, because its error signal shrinks at every step back. Hochreiter and Schmidhuber gave it a memory the error can cross unchanged, with gates that learn when to write and when to read.",
        fieldnote=f"I showed two small networks a sign and then nothing but noise. After 20 steps both remembered it. After 40 the plain one had forgotten (it was right {l40['rnn']}% of the time); the LSTM was still right {l80['lstm']}% of the time after 80. On the way back through 79 steps the plain network's error signal had shrunk to {C.sci(f'{dec['untrained'][-1][1]:.1e}')} of its size.",
        card=[("When", "Thesis 1991; report 1995; journal 1997; forget gate 1999"),
              ("Where", "Technische Universität München; IDSIA, Lugano"),
              ("What hurt", "The error signal vanishes over long gaps"),
              ("The fix", "A gated memory cell with a constant error carousel"),
              ("Checked", f"RNN {l40['rnn']}% at 40 steps; LSTM {l80['lstm']}% at 80")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LongShortTermMemory.java`.",
    )
