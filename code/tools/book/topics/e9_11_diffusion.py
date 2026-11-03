"""Era 9, topic 11: Diffusion models. Every number is parsed from Diffusion.java's output."""
import json
import math
import random
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("forward: "):
            d["fwd"] = re.findall(r"t = (\d+): abar ([\d.]+), step by step the leftover noise has variance ([\d.]+), the closed form says ([\d.]+) ; spread of x ([\d.]+)", ln)
            d["left"] = re.search(r"sqrt\(abar_T\) = ([\d.]+)", ln).group(1)
            d["npts"] = re.search(r"([\d,]+) spiral points", ln).group(1)
        elif ln.startswith("train: "):
            d["params"] = re.search(r"([\d,]+) parameters", ln).group(1)
            d["grad"] = re.search(r"largest relative difference ([\d.eE+-]+)", ln).group(1)
            d["steps"] = re.search(r"Adam, ([\d,]+) steps of (\d+)", ln).groups()
            d["curve"] = [float(x) for x in re.search(r"every 1,000 steps: ([\d.,]+)", ln).group(1).split(",")]
        elif ln.startswith("sample: "):
            m = re.search(r"generated ([\d.]+), fresh spiral points ([\d.]+), Gaussian noise ([\d.]+), reverse process with the network replaced by 0: ([\d.]+) ; generated points on the first arm (\d+), on the second (\d+)", ln)
            d["sample"] = m.groups()
            d["nsample"] = re.match(r"sample: (\d+)", ln).group(1)
        elif ln.startswith("paths: "):
            d["paths"] = [[tuple(map(float, p.split(","))) for p in part.split()] for part in ln.split(" ; ")[1:]]
        elif ln.startswith("points: "):
            d["points"] = [tuple(map(float, p.split(","))) for p in ln.split(" ; ")[1].split()]
        elif ln.startswith("weights:"):
            d["W"] = {}
            for part in ln.split(" ; ")[1:]:
                name, shape, vals = part.split(" ")
                r, c = map(int, shape.split("x"))
                v = [float(x) for x in vals.split(",")]
                d["W"][name] = [v[i * c:(i + 1) * c] for i in range(r)]
    d["checks"] = C.checks(text)
    return d


def spiral_pts(n, seed):
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        s = math.sqrt(rnd.random())
        a = 4.2 * s + (math.pi if rnd.random() < 0.5 else 0)
        out.append((1.6 * s * math.cos(a) + 0.04 * rnd.gauss(0, 1), 1.6 * s * math.sin(a) + 0.04 * rnd.gauss(0, 1)))
    return out


# ----------------------------------------------------------------------------------------------------------------------
def panels_svg(d):
    def draw(t, standalone):
        W, H = 760, 330
        o = [C.text(20, 24, "Left: the data. Middle: the paths of six points from noise. Right: 200 points the trained network generated", t["ink"], 13, "start", 700)]
        boxes = [(20, "data (a two-armed spiral)"), (270, "six reverse paths"), (520, "generated")]
        S = 220
        for x0, lab in boxes:
            o.append(C.rect(x0, 40, S, S, t["wash"], t["rule"], 1))
            o.append(C.text(x0 + S / 2, 280, lab, t["muted"], 12, "middle"))
        P = lambda x0, x, y: (x0 + S / 2 + x * S / 5, 40 + S / 2 - y * S / 5)
        for x, y in spiral_pts(300, 5):
            X, Y = P(20, x, y)
            o.append(C.circle(X, Y, 1.8, t["blue"]))
        for path in d["paths"]:
            pts = [P(270, max(-2.4, min(2.4, x)), max(-2.4, min(2.4, y))) for x, y in path]
            o.append(C.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), t["muted"], "none", 1.2))
            o.append(C.circle(*pts[0], 3, t["muted"]))
            o.append(C.circle(*pts[-1], 3.5, t["red"]))
        for x, y in d["points"]:
            X, Y = P(520, x, y)
            if 520 <= X <= 740 and 40 <= Y <= 260:
                o.append(C.circle(X, Y, 1.8, t["red"]))
        o.append(C.text(20, 318, "Grey dots: where each path starts, in pure noise. Red: where it ends, on the spiral.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Spiral data, reverse diffusion paths, and generated points", t, standalone, 0.55, 760)
    return draw


DF_HTML = """
<div class="board df-board">
  <div style="min-width:0"><div class="df-view" id="df-view"></div></div>
  <div style="min-width:0">
    <label class="df-row">Forward process, step t = <b id="df-tv">0</b><br><input type="range" id="df-t" min="0" max="1000" step="10" value="0"></label>
    <div class="df-btns"><button type="button" class="primary" id="df-gen">Generate from noise</button><button type="button" id="df-stop">Stop</button></div>
    <div class="df-res" id="df-res"></div>
    <p class="say" id="df-say" aria-live="polite"></p>
  </div>
</div>
"""

DF_CSS = """
.df-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.df-board{grid-template-columns:1fr}}
.df-view svg{width:100%;height:auto;display:block;background:var(--wash)}
.df-row{display:block;font-size:13px;margin:4px 0}
.df-row input{width:100%}
.df-btns{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.df-res{font:12.5px var(--mono)}
"""

DF_JS = r"""
(() => {
  const view = document.getElementById("df-view");
  if (!view) return;
  const W = __W__, T = 1000, F = 8, H = W.b1[0].length;
  const beta = [0], alpha = [1], abar = [1];
  for (let t = 1; t <= T; t++) { beta.push(1e-4 + (0.02 - 1e-4) * (t - 1) / (T - 1)); alpha.push(1 - beta[t]); abar.push(abar[t - 1] * alpha[t]); }
  let seed = 9;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const gauss = () => { let u = 0; while (u === 0) u = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd()); };
  const data = [...Array(300)].map(() => { const s = Math.sqrt(rnd()), a = 4.2 * s + (rnd() < 0.5 ? Math.PI : 0); return [1.6 * s * Math.cos(a) + 0.04 * gauss(), 1.6 * s * Math.sin(a) + 0.04 * gauss()]; });
  const noise = data.map(() => [gauss(), gauss()]);
  function net(x, y, t) {
    const e = [x, y]; for (let k = 0; k < F; k++) { const w = t / 1000 * 2 ** k * Math.PI / 2; e.push(Math.sin(w), Math.cos(w)); }
    const h1 = W.W1.map((r, i) => Math.max(0, r.reduce((s, w, j) => s + w * e[j], W.b1[0][i])));
    const h2 = W.W2.map((r, i) => Math.max(0, r.reduce((s, w, j) => s + w * h1[j], W.b2[0][i])));
    return W.W3.map((r, i) => r.reduce((s, w, j) => s + w * h2[j], W.b3[0][i]));
  }
  function plot(pts, col, label) {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 400 400", role: "img", "aria-label": label}, view);
    sv("text", {x: 12, y: 22, "font-size": 13, "font-weight": 700, fill: "var(--ink)"}, svg, label);
    pts.forEach(([x, y]) => { const X = 200 + x * 75, Y = 210 - y * 75; if (X > 0 && X < 400 && Y > 30 && Y < 400) sv("circle", {cx: X, cy: Y, r: 2.4, fill: col}, svg); });
  }
  function forward() {
    const t = +document.getElementById("df-t").value; document.getElementById("df-tv").textContent = t;
    const a = Math.sqrt(abar[t]), s = Math.sqrt(1 - abar[t]);
    plot(data.map(([x, y], i) => [a * x + s * noise[i][0], a * y + s * noise[i][1]]), "var(--blue)", `Data at step ${t}`);
    document.getElementById("df-res").textContent = `x_t = ${a.toFixed(3)} · x_0 + ${s.toFixed(3)} · noise`;
    document.getElementById("df-say").textContent = t < 1000 ? "Drag towards 1,000: each step keeps a little less of the data and adds a little noise. This direction needs no learning." : "At step 1,000 almost nothing of the spiral is left: the points are plain Gaussian noise.";
  }
  let timer = null;
  function stop() { if (timer) { clearInterval(timer); timer = null; } }
  function generate() {
    stop();
    let x = [...Array(200)].map(() => [gauss(), gauss()]), t = T;
    timer = setInterval(() => {
      for (let k = 0; k < 40 && t >= 1; k++, t--) {
        x = x.map(([a, b]) => { const e = net(a, b, t), z = t > 1 ? Math.sqrt(beta[t]) : 0; return [(a - beta[t] / Math.sqrt(1 - abar[t]) * e[0]) / Math.sqrt(alpha[t]) + z * gauss(), (b - beta[t] / Math.sqrt(1 - abar[t]) * e[1]) / Math.sqrt(alpha[t]) + z * gauss()]; });
      }
      plot(x, "var(--red)", `Generating: step ${Math.max(t, 0)}`);
      document.getElementById("df-res").textContent = `${(T - Math.max(t, 0)).toLocaleString("en-US")} of 1,000 reverse steps done`;
      if (t < 1) { stop(); document.getElementById("df-say").textContent = "200 new points, made from noise by the program's trained network, running in your browser. The network stores no points; it only learned to guess noise."; }
      else document.getElementById("df-say").textContent = "Each step subtracts the noise the network predicts, scales up a little, and adds a little fresh noise.";
    }, 30);
  }
  document.getElementById("df-t").addEventListener("input", () => { stop(); forward(); });
  document.getElementById("df-gen").addEventListener("click", generate);
  document.getElementById("df-stop").addEventListener("click", stop);
  forward();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How diffusion models combined older ideas, and where they led")
    W = 220
    nodes = {
        "phys": (20, 20, "Nonequilibrium thermodynamics", "a process that slowly destroys structure", "physics", "ink"),
        "mc": (265, 20, "Markov chains", "each step depends only on the last", "Era 4, topic 3", "ink"),
        "sm": (510, 20, "Denoising score matching", "learn to undo small noise", "", "ink"),
        "nn": (755, 20, "Deep networks", "trained by gradient descent with Adam", "topics 2, 5, 7", "ink"),
        "dif": (265, 200, "Diffusion models", "⊕ learn to reverse a fixed noising chain", "Sohl-Dickstein and colleagues, 2015", "red"),
        "ddpm": (630, 200, "DDPM", "⊕ predict the added noise; 1,000 steps", "Ho, Jain and Abbeel, Berkeley, 2020", "red"),
        "img": (630, 380, "Image and video generators", "the same idea at far larger scale", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("phys", "dif", ports=("bottom", "top:0.15"))
    D.edge("mc", "dif", ports=("bottom", "top"))
    D.edge("dif", "ddpm", ports=("right", "left"))
    D.edge("sm", "ddpm", ports=("bottom", "top:0.3"))
    D.edge("nn", "ddpm", ports=("bottom", "top:0.8"))
    D.edge("ddpm", "img", ports=("bottom", "top"))
    return D


def chain():
    steps = [
        ("No simple recipe for drawing new samples from a distribution as complicated as photographs",
         "Destroy data slowly with noise, and learn to run the process backwards", "Sohl-Dickstein and colleagues, 2015"),
        ("Learning each backward step directly was hard to train well",
         "Train the network to predict the added noise, at a random step: a single squared error", "Ho, Jain and Abbeel, 2020"),
        ("Sampling runs the network a thousand times for every new sample",
         "Later work takes fewer, larger steps", ""),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from noise to pictures")
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
    sm = d["sample"]
    fwd = d["fwd"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. In 2015 Sohl-Dickstein, Weiss, Maheswaranathan and Ganguli took an idea from the physics of systems out of equilibrium: destroy the structure in data slowly, with a Markov chain (Era 4) of small noise steps, then learn the reverse chain. In 2020 Ho, Jain and Abbeel at Berkeley reduced the learning to one instruction, guess the noise, and the samples became excellent."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the two diffusion papers. Blue: what came after."),
        ]),
        dict(id="play", eyebrow="Try it", title="Noise one way, pictures the other", toc="Try it", blocks=[
            dict(type="p", text="The data is a two-armed spiral of points. Drag the slider to run the forward process: the formula is fixed, nothing is learned. Then press *Generate from noise*: your browser starts from 200 points of pure noise and runs 1,000 reverse steps with the program's trained network."),
            dict(type="widget", html=DF_HTML, js=DF_JS.replace("__W__", json.dumps(d["W"], separators=(",", ":"))), css=DF_CSS,
                 fallback=dict(type="svg", name="panels", draw=panels_svg(d), alt="Spiral data, reverse paths and generated points", width=760),
                 note="In the interactive edition you can noise the data and generate new points yourself."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it. The last fix is described generally; no source for it was opened."),
        ]),
        dict(id="how", eyebrow="How it works", title="Learn to guess the noise", toc="How it works", blocks=[
            dict(type="p", text="**Forward.** For t = 1 to T = 1,000, xₜ = √(1 − βₜ) xₜ₋₁ + √βₜ · noise, with βₜ rising linearly from 0.0001 to 0.02. Every step is a little Gaussian blur of the data's distribution. Writing αₜ = 1 − βₜ and ᾱₜ for their product up to t, any step can be reached in one jump: xₜ = √ᾱₜ x₀ + √(1 − ᾱₜ) ε with ε standard Gaussian noise."),
            dict(type="p", text="**Training.** Take a data point x₀, a step t chosen uniformly from 1 to 1,000 and fresh noise ε; form xₜ in one jump; ask the network ε_θ(xₜ, t) for its guess of ε, and take a gradient step on the squared error. The network is told t through sines and cosines of several frequencies."),
            dict(type="p", text="**Sampling.** Start from pure noise x_T. For t = T down to 1: xₜ₋₁ = (xₜ − βₜ/√(1 − ᾱₜ) · ε_θ(xₜ, t)) / √αₜ + √βₜ · z, with fresh Gaussian z, except at the last step. The guessed noise is removed a little at a time; the added z keeps the result random, so every run gives new samples."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Destroying data is easy and needs no learning. Learn only the small step that undoes a little of it, and repeat that step a thousand times."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A spiral from static", toc="Measured", blocks=[
            dict(type="p", text=f"**The forward process** on {d['npts']} spiral points, run as 1,000 separate small steps, against the one-jump formula: the leftover noise xₜ − √ᾱₜ x₀ should have variance 1 − ᾱₜ."),
            dict(type="table", head=["Step t", "ᾱₜ", "Variance, step by step", "Closed form 1 − ᾱₜ", "Spread of x"], num=[0, 1, 2, 3, 4], rows=[list(r) for r in fwd]),
            dict(type="p", text=f"After 1,000 steps √ᾱ_T = {d['left']} of each point is left: the spiral is gone, and the points have the spread of plain Gaussian noise."),
            dict(type="p", text=f"**Training.** The network takes the point and 16 sines and cosines of t, has two hidden layers of 64, and has {d['params']} parameters; its hand-written gradients agree with finite differences to {C.sci(d['grad'])}. Trained with Adam for {d['steps'][0]} steps of {d['steps'][1]} noisy points. The mean squared error of its noise guess (a guess of zero scores 2.0) fell from {d['curve'][0]} after the first 1,000 steps to {d['curve'][-1]}; much of the noise at large t cannot be guessed at all, so it never approaches zero."),
            dict(type="p", text=f"**Sampling.** {d['nsample']} new points, each from pure noise through 1,000 reverse steps. The mean distance from each point to the nearest of 3,000 spiral points:"),
            dict(type="table", head=["Points", "Mean distance to the spiral"], num=[1], rows=[
                ["fresh points from the spiral itself", sm[1]],
                ["generated by the reverse process", sm[0]],
                ["Gaussian noise", sm[2]],
                ["the reverse process with the network replaced by 0", sm[3]],
            ], hl=1),
            dict(type="p", text=f"The generated points sit close to the spiral, not as tightly as real points, and {sm[4]} landed on one arm and {sm[5]} on the other. Without the trained network the reverse steps only divide by √αₜ again and again, and the points fly apart."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="2015, and Berkeley in 2020", toc="The evidence", blocks=[
            dict(type="p", text="Sohl-Dickstein, Weiss, Maheswaranathan and Ganguli (submitted 12 March 2015): the idea \"is to systematically and slowly destroy structure in a data distribution through an iterative forward diffusion process\", then to \"learn a reverse diffusion process that restores structure in data\"."),
            dict(type="p", text="Ho, Jain and Abbeel (UC Berkeley, 2020): the forward process \"is fixed to a Markov chain that gradually adds Gaussian noise to the data according to a variance schedule\" and \"admits sampling xt at an arbitrary timestep t in closed form\"; \"We set T = 1000 for all experiments\", with β rising linearly from 10⁻⁴ to 0.02; the training objective is the squared error of the predicted noise with \"t is uniform between 1 and T\"; sampling runs \"for t = T, . . . , 1\" with fresh noise \"if t > 1, else z = 0\". On CIFAR10: \"an Inception score of 9.46 and a state-of-the-art FID score of 3.17\". Their parameterization \"reveals an equivalence with denoising score matching over multiple noise levels\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Markov's chains, run backwards", toc="Full circle", blocks=[
            dict(type="p", text="Markov (Era 4) studied chains in which each step depends only on the one before. A diffusion model is such a chain, run forwards to turn data into noise, and then, with a learned network, run backwards to turn noise into data. The Monte Carlo method (Era 4) supplies the randomness at every step."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Plain noise lies {sm[2]} from the spiral on average. After 1,000 learned steps, the same kind of noise lies {sm[0]} from it."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("ᾱₜ = 0.25. What are the weights of x₀ and of the noise in xₜ?", "√0.25 = 0.5 for x₀ and √0.75 ≈ 0.866 for the noise."),
            ("Why can training pick any t at random without running the earlier steps?", "Because xₜ has a closed form in x₀ and one draw of noise."),
            ("Why add fresh noise z during sampling, rather than only subtract?", "Each reverse step is itself a random step; without z every run from the same start would give the same point, and the samples lose their variety."),
            ("Why does the noise-guessing error stay well above zero?", "At large t the data contributes almost nothing to xₜ, so the noise cannot be told from the data's own position; only an average guess is possible."),
            ("How many network evaluations does one sample need here?", "1,000, one per reverse step."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Denoising Diffusion Probabilistic Models (2020)", text="Ho, Jain and Abbeel, arXiv:2006.11239.",
                 draw=C.draw_manuscript, link="https://arxiv.org/pdf/2006.11239v2", link_text="arXiv:2006.11239 (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Diffusion", d["checks"],
                           "the forward process against its closed form, the hand-written gradients, that generated points lie near the spiral on both arms, and that the reverse process fails without the network.",
                           ["static double[][] sample(Net n, int count, Random r, boolean zeroNet, List<double[][]> paths)"]),
    ]
    return dict(
        title="Diffusion Models", date="2015–2020",
        description="Era 9, topic 11 of The Algorithm Evolution Atlas: diffusion models (Sohl-Dickstein and colleagues, 2015; Ho, Jain and Abbeel, 2020), a network trained to guess noise, generating a spiral from static.",
        lede="Destroying a picture is easy: add a little noise, a thousand times. In 2015 a team proposed generating data by learning to run that process backwards, and in 2020 three researchers at Berkeley made it simple: show a network a noisy example and ask it what noise was added.",
        fieldnote=f"I drew a spiral of points and buried it under a thousand thin layers of noise until nothing was left. Then I taught a small network one skill, guessing the noise in a noisy point. Starting from pure static, it removed its guesses step by step, and new points gathered on both arms of the spiral, {sm[0]} from it on average.",
        card=[("When", "March 2015; June 2020"),
              ("Where", "Sohl-Dickstein and colleagues; UC Berkeley"),
              ("What hurt", "No simple recipe for sampling complicated distributions"),
              ("The fix", "Learn to reverse a fixed noising chain, by guessing the noise"),
              ("Checked", f"Generated points {sm[0]} from the spiral; noise {sm[2]}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Diffusion.java`.",
    )
