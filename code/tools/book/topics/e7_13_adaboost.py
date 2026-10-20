"""Era 7, topic 13: AdaBoost. Every number is parsed from AdaBoost.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"circle: ([\d,]+) training points and ([\d,]+) test points .*? ; one stump [^;]* ; (.*?) ; training error first reached 0 after (\d+) rounds ; the stumps' weighted errors ranged from ([\d.]+) to ([\d.]+)", ln):
            rows = []
            for part in m.group(3).split(" ; "):
                mm = re.match(r"(\d+) rounds?: training error ([\d.]+)% \(bound ([\d.]+)%\), test error ([\d.]+)%", part)
                rows.append(dict(t=int(mm.group(1)), tr=mm.group(2), bound=mm.group(3), te=mm.group(4)))
            d["circle"] = dict(ntr=m.group(1), nte=m.group(2), rows=rows, zero=m.group(4), emin=m.group(5), emax=m.group(6))
        elif m := re.match(r"noise: .*? with (\d+) labels \((\d+)%\) flipped .*? ; (.*?) ; the best test error along the way was ([\d.]+)%", ln):
            rows = []
            for part in m.group(3).split(" ; "):
                mm = re.match(r"(\d+) rounds: training error ([\d.]+)%, test error ([\d.]+)%, (\d+)% of the weight on the flipped examples", part)
                rows.append(dict(t=mm.group(1), tr=mm.group(2), te=mm.group(3), w=mm.group(4)))
            d["noise"] = dict(flips=m.group(1), pct=m.group(2), rows=rows, best=m.group(4))
        elif m := re.match(r"widget: 120 points .*? seed (\d+), .*? ; first stump: ([xy]) < ([\d.]+) predicts (\w+) ; [^;]* ; (.*)$", ln):
            d["widget"] = dict(seed=int(m.group(1)), f=m.group(2), t=m.group(3), side=m.group(4),
                               rounds=[[int(p.split(":")[0]), int(p.split(":")[1]), float(p.split(":")[2])] for p in m.group(5).split()])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def errors_svg(d):
    """Training error, test error and the proven bound against the number of rounds (log scale)."""
    rows = d["circle"]["rows"]

    def draw(t, standalone):
        o = []
        W, H = 760, 320
        x0, x1, y0, y1 = 70, 720, 250, 50
        lo, hi = 0, math.log10(rows[-1]["t"])
        X = lambda r: x0 + (math.log10(r) - lo) / (hi - lo) * (x1 - x0)
        Y = lambda p: y0 - p / 100 * (y0 - y1)
        o.append(C.text(20, 26, "The circle: errors as rounds are added, with Freund and Schapire's bound on the training error", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        for p in (0, 25, 50, 75, 100):
            o.append(C.text(x0 - 8, Y(p) + 4, f"{p}%", t["muted"], 11.5, "end"))
            o.append(C.line(x0 - 4, Y(p), x0, Y(p), t["axis"], 1.2))
        for r in rows:
            o.append(C.text(X(r["t"]), y0 + 18, str(r["t"]), t["muted"], 11.5, "middle"))
        o.append(C.text((x0 + x1) / 2, y0 + 40, "rounds (one stump each), on a log scale", t["muted"], 12, "middle"))
        for key, col, lab, dash, at, dy in (("bound", t["muted"], "bound", ";stroke-dasharray:6 4", 3, -10), ("tr", t["red"], "training error", "", 2, 18), ("te", t["blue"], "test error", "", 1, -10)):
            o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(r['t']):.1f},{Y(min(100, float(r[key]))):.1f}" for i, r in enumerate(rows)), col, "none", 2.2, dash))
            r = rows[at]
            o.append(C.text(X(r["t"]) + 6, Y(min(100, float(r[key]))) + dy, lab, col, 12, "start", 700))
        return C.svg_doc(W, H, "".join(o), "Training error, test error and the bound against rounds", t, standalone, 0.55, 760)
    return draw


AB_HTML = """
<div class="board ab-board">
  <div style="min-width:0">
    <div class="ab-view" id="ab-view"></div>
  </div>
  <div style="min-width:0">
    <div class="ab-btns"><button type="button" class="primary" id="ab-1">One round</button><button type="button" id="ab-10">Ten rounds</button><button type="button" id="ab-reset">Start again</button></div>
    <div class="ab-stats" id="ab-stats"></div>
    <p class="say" id="ab-say" aria-live="polite"></p>
  </div>
</div>
"""

AB_CSS = """
.ab-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.ab-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.ab-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

AB_JS = r"""
(() => {
  const view = document.getElementById("ab-view");
  if (!view) return;
  const SEED = __SEED__, PROG = __PROG__;
  let s32, P, w, stumps, votes;
  // the program's 32-bit generator and point rule
  function next32() { s32 = (Math.imul(s32, 1664525) + 1013904223) | 0; return (s32 >>> 0) / 4294967296; }
  function points(n) { const p = []; for (let i = 0; i < n; i++) { const x = next32(), y = next32(), dx = x - 0.5, dy = y - 0.5; p.push([x, y, dx * dx + dy * dy < 0.35 * 0.35 ? 1 : -1]); } return p; }
  const pred = (h, q) => q[h.f] < h.t ? h.s : -h.s;
  // exactly the program's stump search, in the same order
  function best() {
    const n = P.length; let bestS = null, bestErr = Infinity;
    for (let f = 0; f < 2; f++) {
      const idx = Array.from({length: n}, (_, i) => i).sort((a, b) => P[a][f] < P[b][f] ? -1 : P[a][f] > P[b][f] ? 1 : 0);
      let errPlus = 0; for (let i = 0; i < n; i++) if (P[i][2] > 0) errPlus += w[i];
      for (let k = 0; k <= n; k++) {
        if (k > 0) { const i = idx[k - 1]; errPlus += P[i][2] > 0 ? -w[i] : w[i]; }
        if (k === 0 || k === n) continue;
        if (P[idx[k - 1]][f] === P[idx[k]][f]) continue;
        const t = (P[idx[k - 1]][f] + P[idx[k]][f]) / 2, errMinus = 1 - errPlus;
        if (errPlus < bestErr) { bestErr = errPlus; bestS = {f, t, s: 1}; }
        if (errMinus < bestErr) { bestErr = errMinus; bestS = {f, t, s: -1}; }
      }
    }
    return [bestS, bestErr];
  }
  function round() {
    const [h, eps] = best(), beta = eps / (1 - eps);
    for (let i = 0; i < P.length; i++) if (pred(h, P[i]) === P[i][2]) w[i] *= beta;
    let sum = 0; for (const x of w) sum += x; for (let i = 0; i < w.length; i++) w[i] /= sum;
    stumps.push(h); votes.push(Math.log(1 / beta));
    return eps;
  }
  const predict = q => { let s = 0; for (let k = 0; k < stumps.length; k++) s += votes[k] * pred(stumps[k], q); return s >= 0 ? 1 : -1; };
  let log = [];
  function reset() { s32 = SEED; P = points(120); w = new Array(120).fill(1 / 120); stumps = []; votes = []; log = []; draw("120 points: red inside the circle, blue outside, all with equal weight. Press One round."); }
  function step(n) {
    for (let k = 0; k < n && stumps.length < 40; k++) { const e = round(); const wrong = P.filter(q => predict(q) !== q[2]).length; log.push([stumps.length, wrong, e]); }
    const [t, wrong, e] = log[log.length - 1], h = stumps[stumps.length - 1], pg = PROG[t - 1];
    draw(`Round ${t}: the best stump, ${h.f ? "y" : "x"} ${h.s > 0 ? "<" : "≥"} ${h.t.toFixed(3)} means inside, has weighted error ${e.toFixed(4)}. The points it got right shrink (weight × ${(e / (1 - e)).toFixed(3)}); the vote now makes ${wrong} mistake${wrong === 1 ? "" : "s"}.` + (pg ? ` The program: ${pg[1]} mistakes, error ${pg[2].toFixed(4)}.` : ""));
  }
  function draw(msg) {
    view.innerHTML = "";
    const S = 400, svg = sv("svg", {viewBox: `0 0 ${S} ${S}`}, view), G = 40;
    if (stumps.length) for (let a = 0; a < G; a++) for (let b = 0; b < G; b++) {
      const q = [(a + 0.5) / G, 1 - (b + 0.5) / G]; sv("rect", {x: a * S / G, y: b * S / G, width: S / G + 0.4, height: S / G + 0.4, fill: predict(q) > 0 ? "var(--red)" : "var(--blue)", "fill-opacity": 0.14}, svg);
    }
    sv("circle", {cx: S / 2, cy: S / 2, r: 0.35 * S, fill: "none", stroke: "var(--ink)", "stroke-width": 1, "stroke-dasharray": "4 4"}, svg);
    if (stumps.length) { const h = stumps[stumps.length - 1]; if (h.f === 0) sv("line", {x1: h.t * S, y1: 0, x2: h.t * S, y2: S, stroke: "var(--ink)", "stroke-width": 2}, svg); else sv("line", {x1: 0, y1: (1 - h.t) * S, x2: S, y2: (1 - h.t) * S, stroke: "var(--ink)", "stroke-width": 2}, svg); }
    const mw = Math.max(...w);
    P.forEach((q, i) => sv("circle", {cx: q[0] * S, cy: (1 - q[1]) * S, r: 2 + 9 * Math.sqrt(w[i] / mw), fill: q[2] > 0 ? "var(--red)" : "var(--blue)", "fill-opacity": 0.85, stroke: predict(q) !== q[2] && stumps.length ? "var(--ink)" : "none", "stroke-width": 1.5}, svg));
    const st = document.getElementById("ab-stats"); st.innerHTML = "";
    el("div", {}, st, `rounds: ${stumps.length}`);
    if (log.length) { const l = log[log.length - 1]; el("div", {}, st, `training mistakes: ${l[1]} of 120`); }
    if (msg) document.getElementById("ab-say").textContent = msg;
  }
  document.getElementById("ab-1").addEventListener("click", () => step(1));
  document.getElementById("ab-10").addEventListener("click", () => step(10));
  document.getElementById("ab-reset").addEventListener("click", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How AdaBoost combined older ideas, and where it led")
    W = 210
    nodes = {
        "kv": (20, 20, "Weak versus strong", "can weak rules be combined?", "Kearns and Valiant, 1988", "ink"),
        "mw": (395, 20, "Multiplicative weights", "shrink the weight of what did badly", "Littlestone and Warmuth", "ink"),
        "sch": (770, 20, "Boosting exists", "yes, by construction, but impractical", "Schapire 1990; Freund", "ink"),
        "ada": (395, 180, "AdaBoost", "⊕ reweight the examples after every weak rule", "Freund and Schapire, 1995", "red"),
        "vj": (20, 340, "Viola–Jones detection", "a boosted cascade finds objects in images", "", "ink"),
        "tr": (770, 340, "Boosted trees", "\"the best out-of-the-box classifier\"", "", "ink"),
        "today": (395, 490, "Today", "the 2003 Gödel Prize; boosting in everyday machine learning", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("kv", "ada", ports=("bottom", "top:0.15"))
    D.edge("mw", "ada", ports=("bottom", "top"))
    D.edge("sch", "ada", ports=("bottom", "top:0.85"), label="made practical", at=0.5, dx=8, anchor="start")
    D.edge("ada", "vj", ports=("bottom:0.15", "top"))
    D.edge("ada", "tr", ports=("bottom:0.85", "top"))
    D.edge("ada", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: the prize and the uses Wikipedia records. Kearns and Valiant's question was first answered by Schapire's construction.", "caption")
    return D


def chain(d):
    ci, no = d["circle"], d["noise"]
    one, last = ci["rows"][0], ci["rows"][-1]
    steps = [
        (f"A single weak rule is barely better than a coin: one stump, test error {one['te']}%",
         "Combine many weak rules: possible in principle (Schapire 1990, Freund), but impractical", "Kearns and Valiant's question, answered"),
        ("The early constructions were too complicated to use",
         f"AdaBoost: reweight the examples, weighted vote; test error {last['te']}% after {last['t']} rounds", "Freund and Schapire, 1995"),
        (f"Weights pile onto mislabelled examples: {no['rows'][-1]['w']}% of the weight on {no['pct']}% flipped labels, test error up to {no['rows'][-1]['te']}%",
         f"Stop earlier: the best test error along the way was {no['best']}%", "an observation from the program's run"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from weak rules to a strong vote")
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
    ci, no, wg = d["circle"], d["noise"], d["widget"]
    ci_rows = [[str(r["t"]), r["tr"] + "%", r["bound"] + "%", r["te"] + "%"] for r in ci["rows"]]
    no_rows = [[r["t"], r["tr"] + "%", r["te"] + "%", r["w"] + "%"] for r in no["rows"]]
    wg_rows = [[str(r[0]), str(r[1]), f"{r[2]:.4f}"] for r in wg["rounds"][:12]]
    one, last = ci["rows"][0], ci["rows"][-1]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Kearns and Valiant asked whether rules only slightly better than chance could always be combined into accurate ones. Schapire proved in 1990 that they could, and Freund found another way, but neither was practical. Freund and Schapire then took the multiplicative weight updates that Littlestone and Warmuth had used for on-line learning and applied them to the training examples. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: AdaBoost. Blue: what followed."),
        ]),
        dict(id="play", eyebrow="Try it", title="Watch the weights move", toc="Try it", blocks=[
            dict(type="p", text="One hundred and twenty points, red inside the dashed circle and blue outside, made by the same simple generator as the program. Each round AdaBoost picks the stump (one vertical or horizontal line) with the smallest weighted error, then shrinks the weight of every point it got right, so the next round attends to the points still being missed (big dots). The shading is the vote of all the stumps so far; ringed points are its mistakes. No single line can draw a circle, but the vote of a few dozen comes close. The widget repeats the program's arithmetic, so its mistakes and errors match the program's, round by round."),
            dict(type="widget", html=AB_HTML, js=AB_JS.replace("__SEED__", str(wg["seed"])).replace("__PROG__", json.dumps(wg["rounds"])), css=AB_CSS,
                 fallback=dict(type="table", head=["Round", "Training mistakes (of 120)", "Weighted error of the round's stump"], num=[0, 1, 2], rows=wg_rows),
                 note="In the interactive edition you can run the rounds and watch the weights shift."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Reweight, then vote", toc="How it works", blocks=[
            dict(type="p", text="**Weights.** Start with every training example weighted equally. The weak learner must find a rule whose error, counted with these weights, is below ½."),
            dict(type="p", text="**The update.** With weighted error ε, multiply the weight of every example the rule got right by β = ε/(1 − ε), which is less than 1, and rescale so the weights sum to 1. The examples the rule missed now carry half the weight, so the next rule cannot ignore them."),
            dict(type="p", text="**The vote.** The final classifier adds up the rules' votes, each with weight log(1/β): accurate rules speak louder. Freund and Schapire proved that the training error is at most the product, over the rounds, of 2√(ε(1 − ε)), which falls exponentially as long as every rule beats a coin by some margin."),
            dict(type="svg", name="errors", draw=errors_svg(d), alt="Training error, test error and the bound against rounds", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="You do not need a clever learner, only one that is never quite useless. By changing which examples matter each round, AdaBoost forces a series of weak rules to cover each other's mistakes."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A circle from straight lines", toc="Measured", blocks=[
            dict(type="p", text=f"**The circle.** {ci['ntr']} training points and {ci['nte']} test points, labelled by whether they lie inside a circle of radius 0.35. The stumps' weighted errors ranged from {ci['emin']} to {ci['emax']}, all below ½; the training error never exceeded the bound, and reached 0 after {ci['zero']} rounds, while the test error kept falling."),
            dict(type="table", head=["Rounds", "Training error", "Bound", "Test error"], num=[0, 1, 2, 3], rows=ci_rows, hl=[len(ci_rows) - 1]),
            dict(type="p", text=f"**Noisy labels.** A new training set with {no['flips']} labels ({no['pct']}%) flipped at random, tested on the same clean points. The weights pile onto the flipped examples, which no honest rule can get right, and after a while the test error rises; the best along the way was {no['best']}%."),
            dict(type="table", head=["Rounds", "Training error", "Test error", "Weight on the flipped examples"], num=[0, 1, 2, 3], rows=no_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A question becomes a method", toc="The evidence", blocks=[
            dict(type="p", text="Yoav Freund and Robert Schapire (AT&T Labs), \"A decision-theoretic generalization of on-line learning and an application to boosting\" (*Journal of Computer and System Sciences* 55(1): 119–139, 1997; \"An extended abstract of this work appeared in the Proceedings of the Second European Conference on Computational Learning Theory, Barcelona, March, 1995\"): \"We show that the multiplicative weight-update rule of Littlestone and Warmuth can be adapted to this model\". In AdaBoost \"The update rule reduces the probability assigned to those examples on which the hypothesis makes a good prediction\", with β = ε/(1 − ε) and a final vote weighted by log(1/β); Theorem 6 bounds the training error by the product of 2√(ε(1 − ε)). The paper recalls that \"Schapire showed that any weak learning algorithm can be efficiently transformed\" into a strong one."),
            dict(type="p", text="Wikipedia: AdaBoost, \"short for Adaptive Boosting\", was \"formulated by Yoav Freund and Robert Schapire in 1995\", who \"won the 2003 Gödel Prize for their work\"; it \"is typically used to combine weak base learners (such as decision stumps)\"; its exponential loss can \"result in excessive weights being assigned to outliers\"; with trees it \"is often referred to as the best out-of-the-box classifier\"; and Viola and Jones's object detection framework uses a boosted cascade. Kearns's article dates the question \"is weakly learnability equivalent to strong learnability?\" to 1988–1989 and says Schapire's 1990 answer was a \"proof by construction, not practical\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The perceptron's mistakes, put to work", toc="Full circle", blocks=[
            dict(type="p", text="Era 5's perceptron adjusted its weights after each mistake. AdaBoost adjusts weights too, but on the examples rather than the rule: the examples it keeps getting wrong become the ones that matter. Backpropagation (topic 7) trains one strong model; AdaBoost trains many weak ones and lets them vote."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"One stump on the circle: test error {one['te']}%. {last['t']} stumps voting: {last['te']}%. None of them could draw a curve; together they drew a circle."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A stump has weighted error 0.25. By what factor are the weights of the examples it got right multiplied, and what is its vote?", "β = 0.25/0.75 = 1/3; its vote is log 3 ≈ 1.10."),
            ("After the update, how much of the total weight sits on the examples the stump got wrong?", "Exactly half: ε before rescaling, against (1 − ε)·β = ε for the right ones."),
            ("Why must every weak rule have weighted error below ½?", "Otherwise β ≥ 1 and the vote weight log(1/β) is zero or negative: the rule adds nothing, and the bound stops shrinking."),
            ("Why do mislabelled examples gather weight?", "No honest rule gets them right, so their weights are never shrunk while everything else's is."),
            ("With ε = 0.4 every round, about how many rounds bring the bound below 1%?", "2√(0.4 × 0.6) ≈ 0.98 per round, so about 230 rounds (0.98²³⁰ ≈ 0.01)."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Freund and Schapire's journal paper (1997)", text="*Journal of Computer and System Sciences* 55(1): 119–139; the 1995 extended abstract was not opened.",
                 draw=C.draw_manuscript, link="https://khoury.northeastern.edu/home/vip/teach/IRcourse/6_ML/other_notes/freund_schapire_adaboost_journal.pdf", link_text="The paper (PDF, on a Northeastern course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "AdaBoost", d["checks"],
                           "500 rounds on the circle with the bound checked after every one, 500 rounds on noisy labels, and the 40 rounds the widget repeats.",
                           ["static double round(double[][] p)"]),
    ]
    return dict(
        title="AdaBoost", date="1995–1997",
        description="Era 7, topic 13 of The Algorithm Evolution Atlas: Freund and Schapire's AdaBoost, from Kearns and Valiant's question about weak learners to reweighted examples, weighted votes and an exponential bound.",
        lede="Kearns and Valiant asked whether rules barely better than guessing could be combined into accurate ones. Freund and Schapire's AdaBoost answered in practice: train them one at a time on reweighted examples, and let them vote.",
        fieldnote=f"No straight line can draw a circle. I watched {last['t']} of them, each chosen to fix what the others missed, vote their way to a test error of {last['te']}%. When I mislabelled a tenth of the examples, the votes chased the mistakes, and I learned when to stop.",
        card=[("When", "Extended abstract 1995; journal 1997"),
              ("Where", "AT&T"),
              ("What hurt", "Weak rules of thumb; impractical ways to combine them"),
              ("The fix", "Reweight examples after each rule; weighted vote"),
              ("Checked", f"Test error {one['te']}% with 1 stump, {last['te']}% with {last['t']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AdaBoost.java`.",
    )
