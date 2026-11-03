"""Era 9, topic 13: Algorithms that find algorithms. Every number is parsed from AlgorithmDiscovery.java's output."""
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("classical: "):
            d["classical"] = ln
        elif ln.startswith("alphatensor: "):
            d["at_ones"] = re.search(r"nonzero coefficients: AlphaTensor (\d+), Strassen twice (\d+)", ln).groups()
            d["at_first"] = re.search(r"first multiplication: (.*)$", ln).group(1)
            d["at_trials"] = re.search(r"([\d,]+) random 0/1 matrix pairs", ln).group(1)
        elif ln.startswith("flip2: "):
            d["f2"] = re.search(r"flips needed: ([\d, ]+) ;", ln).group(1).split(", ")
            d["f2_alg"] = re.search(r"the first walk's algorithm: (.*)$", ln).group(1).split(" ; ")
        elif ln.startswith("flip3: "):
            d["f3_reached"] = re.search(r"reached 23 \(Laderman's 1976 record\): (\d+) of 10", ln).group(1)
            d["f3"] = re.search(r"flips needed: (.*?) ; the first walk", ln).group(1).split(", ")
            d["f3_log"] = [tuple(map(int, e.split(":"))) for e in re.search(r"each new low: (.*)$", ln).group(1).split()]
        elif ln.startswith("flip4: "):
            d["f4_flips"] = re.search(r"one walk of ([\d,]+) flips", ln).group(1)
            d["f4_rank"] = re.search(r"lowest rank reached (\d+)", ln).group(1)
            d["f4_log"] = [tuple(map(int, e.split(":"))) for e in re.search(r"each new low: (.*)$", ln).group(1).split()]
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def walk_svg(d):
    def draw(t, standalone):
        W, H = 760, 380
        o = [C.text(20, 26, "Random walks on the flip graph: the number of multiplications at each new low", t["ink"], 13, "start", 700)]
        X0, X1 = 90, 600
        lx = lambda f: X0 + math.log10(max(f, 1)) / 7 * (X1 - X0)
        for e in range(0, 8):
            o.append(C.line(lx(10 ** e), 50, lx(10 ** e), 320, t["rule"], 1))
            o.append(C.text(lx(10 ** e), 338, f"10{''.join('⁰¹²³⁴⁵⁶⁷'[int(c)] for c in str(e))}", t["muted"], 11, "middle"))
        o.append(C.text((X0 + X1) / 2, 358, "flips (log scale)", t["muted"], 11, "middle"))
        panels = [(d["f3_log"], 20, 30, "3 × 3", t["blue"], [(23, "Laderman, 23")]), (d["f4_log"], 44, 66, "4 × 4", t["red"], [(49, "Strassen twice, 49"), (47, "AlphaTensor, 47")])]
        for log, lo, hi, lab, col, marks in panels:
            pass
        lo, hi = 20, 66
        sy = lambda r: 320 - (r - lo) / (hi - lo) * 270
        for v in [23, 27, 47, 49, 53, 64]:
            o.append(C.text(X0 - 8, sy(v) + 4, str(v), t["muted"], 11, "end"))
        for log, _, _, lab, col, marks in panels:
            pts = []
            for k, (f, r) in enumerate(log):
                if k > 0:
                    pts.append((lx(f), sy(log[k - 1][1])))
                pts.append((lx(f), sy(r)))
            o.append(C.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), col, "none", 2.4))
            o.append(C.text(pts[-1][0] + 8, pts[-1][1] + 4, f"{lab}: {log[-1][1]}", col, 12, "start", 700))
            for v, ml in marks:
                o.append(C.line(X0, sy(v), X1, sy(v), col, 1, ";stroke-dasharray:4 4"))
                o.append(C.text(X1 + 6, sy(v) + 4, ml, col, 11))
        return C.svg_doc(W, H, "".join(o), "Rank of the multiplication scheme along random flip-graph walks", t, standalone, 0.55, 760)
    return draw


def seven_svg(d):
    def draw(t, standalone):
        W = 760
        H = 60 + 30 * len(d["f2_alg"]) + 30
        o = [C.text(20, 26, "Seven multiplications for 2 × 2 matrices (modulo 2), found by random flips from the schoolbook 8", t["ink"], 13, "start", 700)]
        for i, a in enumerate(d["f2_alg"]):
            o.append(C.text(30, 56 + 30 * i, f"M{i + 1} = {a}", t["ink"], 13))
        o.append(C.text(20, H - 12, "Each line: one multiplication, and the entries of C it is added to.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A seven-multiplication 2 × 2 algorithm", t, standalone, 0.55, 760)
    return draw


FG_HTML = """
<div class="board fg-board">
  <div style="min-width:0">
    <div class="fg-h">The algorithm, one multiplication per row</div>
    <div class="fg-terms" id="fg-terms"></div>
  </div>
  <div style="min-width:0">
    <div class="fg-rank" id="fg-rank"></div>
    <div class="fg-btns"><button type="button" class="primary" id="fg-flip">One random flip</button><button type="button" id="fg-walk">Walk until a multiplication disappears</button><button type="button" id="fg-reset">Back to the schoolbook 8</button></div>
    <div class="fg-res" id="fg-res"></div>
    <p class="say" id="fg-say" aria-live="polite"></p>
  </div>
</div>
"""

FG_CSS = """
.fg-board{display:grid;grid-template-columns:minmax(0,1.3fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.fg-board{grid-template-columns:1fr}}
.fg-h{font-size:12px;font-weight:700;color:var(--muted);margin-bottom:6px}
.fg-terms{font:12.5px var(--mono);display:grid;gap:3px}
.fg-terms div{padding:2px 4px;border-left:3px solid var(--rule)}
.fg-terms div.hit{border-left-color:var(--red);background:var(--wash)}
.fg-rank{font:600 28px var(--mono);margin-bottom:8px}
.fg-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.fg-res{font:12.5px var(--mono)}
"""

FG_JS = r"""
(() => {
  const host = document.getElementById("fg-terms");
  if (!host) return;
  const n = 2;
  let S, flips, seed = 17, hit = [];
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const pick = k => Math.floor(rnd() * k);
  function reset() { S = []; for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) for (let k = 0; k < n; k++) S.push([1 << (i * n + j), 1 << (j * n + k), 1 << (k * n + i)]); flips = 0; hit = []; }
  function name(m, M, tr) { const out = []; for (let b = 0; b < n * n; b++) if (m >> b & 1) { const r = tr ? b % n : Math.floor(b / n), c = tr ? Math.floor(b / n) : b % n; out.push(`${M}${r + 1}${c + 1}`); } return out.join("+"); }
  function correct() {
    const m = n * n, t = new Map();
    const key = (a, b, c) => a * 256 + b * 16 + c;
    S.forEach(([x, y, z]) => { for (let a = 0; a < m; a++) if (x >> a & 1) for (let b = 0; b < m; b++) if (y >> b & 1) for (let c = 0; c < m; c++) if (z >> c & 1) { const k = key(a, b, c); t.set(k, (t.get(k) || 0) ^ 1); } });
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) for (let k = 0; k < n; k++) { const kk = key(i * n + j, j * n + k, k * n + i); t.set(kk, (t.get(kk) || 0) ^ 1); }
    return [...t.values()].every(v => v === 0);
  }
  function reduce(touched) {
    let merged = 0;
    while (touched.length) {
      const x = touched.pop(); if (!S.includes(x)) continue;
      if (!x[0] || !x[1] || !x[2]) { S.splice(S.indexOf(x), 1); continue; }
      for (const y of S) {
        if (y === x) continue;
        let done = false;
        for (let p = 0; p < 3; p++) { const q = (p + 1) % 3, s = (p + 2) % 3; if (x[q] === y[q] && x[s] === y[s]) { y[p] ^= x[p]; S.splice(S.indexOf(x), 1); merged++; touched.push(y); hit = [y]; done = true; break; } }
        if (done) break;
      }
    }
    return merged;
  }
  function flip() {
    for (let tries = 0; tries < 1000; tries++) {
      const x = S[pick(S.length)], p = pick(3), js = S.filter(y => y !== x && y[p] === x[p]);
      if (!js.length) continue;
      const y = js[pick(js.length)];
      let q = (p + 1) % 3, s = (p + 2) % 3; if (rnd() < 0.5) [q, s] = [s, q];
      x[q] ^= y[q]; y[s] ^= x[s]; flips++; hit = [x, y];
      return reduce([x, y]);
    }
    return 0;
  }
  function draw(msg) {
    host.innerHTML = "";
    S.forEach(x => el("div", {class: hit.includes(x) ? "hit" : ""}, host, `(${name(x[0], "A")}) × (${name(x[1], "B")}) → ${name(x[2], "C", true)}`));
    document.getElementById("fg-rank").textContent = `${S.length} multiplications`;
    document.getElementById("fg-res").textContent = `${flips.toLocaleString("en-US")} flips · adds up to matrix multiplication: ${correct() ? "yes" : "NO"}`;
    document.getElementById("fg-say").textContent = msg;
  }
  document.getElementById("fg-flip").addEventListener("click", () => {
    const m = flip();
    draw(m ? "Two rows came to share two of their three factors and merged: one multiplication fewer." : "A flip: two rows sharing a factor were rewritten (highlighted). The sum, and so the algorithm's result, is unchanged.");
  });
  document.getElementById("fg-walk").addEventListener("click", () => {
    if (S.length <= 7) { draw("Seven, as many as Strassen's algorithm. This simple walk does not go lower; press Back to start again."); return; }
    let k = 0; while (!flip() && k++ < 200000);
    draw(S.length === 7 ? `After ${flips.toLocaleString("en-US")} flips: 7 multiplications, as many as Strassen's algorithm, found by random rewriting.` : "One multiplication fewer. Keep walking.");
  });
  document.getElementById("fg-reset").addEventListener("click", () => { reset(); draw("The schoolbook method: one multiplication for each i, j, k."); });
  reset(); draw("The schoolbook method: one multiplication for each i, j, k. Each row multiplies a sum of entries of A by a sum of entries of B and adds the product to the listed entries of C (arithmetic modulo 2).");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How algorithm discovery combined older ideas, and where it led")
    W = 220
    nodes = {
        "str": (20, 20, "Strassen's algorithm", "2 × 2 matrices with 7 multiplications", "Era 6, topic 5", "ink"),
        "ten": (265, 20, "Tensor rank", "an algorithm is a sum of rank-one pieces", "", "ink"),
        "az": (510, 20, "AlphaZero's search", "tree search guided by networks", "topic 8", "ink"),
        "llm": (755, 20, "Language models", "programs written by a model", "topic 9 and after", "ink"),
        "at": (140, 200, "AlphaTensor", "⊕ a game played on the tensor; 47 for 4 × 4 mod 2", "DeepMind, October 2022", "red"),
        "fg": (387, 380, "Flip graphs", "⊕ random walks that keep the sum; 47 again, 95 for 5 × 5", "Kauers and Moosbauer, Linz, December 2022", "red"),
        "ae": (635, 200, "AlphaEvolve", "⊕ evolving programs, checked automatically; 48 for 4 × 4 complex", "Google DeepMind, May 2025", "red"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 116, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("str", "at", ports=("bottom", "top:0.2"))
    D.edge("ten", "at", ports=("bottom", "top:0.8"))
    D.edge("az", "at", ports=("bottom", "right"))
    D.edge("at", "fg", ports=("bottom", "left"))
    D.edge("ten", "fg", ports=("bottom", "top"))
    D.edge("llm", "ae", ports=("bottom", "top"))
    return D


def chain():
    steps = [
        ("After Strassen, people searched by hand for fewer multiplications, size by size",
         "Turn the search into a game and let a learning system play it: AlphaTensor", "DeepMind, 2022"),
        ("Was a learning system needed to find such algorithms at all?",
         "No: a simple random walk on a graph of schemes, flips and reductions, matched 47", "Kauers and Moosbauer, 2022"),
        ("Each search is built for one kind of problem",
         "Evolve whole programs with a language model, and check each automatically", "AlphaEvolve, 2025"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from hand search to machine search")
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
    f3n = [int(x) for x in d["f3"] if x.isdigit()]
    f2n = [int(x) for x in d["f2"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Strassen (Era 6) multiplied 2 × 2 matrices with 7 multiplications instead of 8. Every such algorithm is a way of writing one fixed table of zeros and ones, the matrix multiplication tensor, as a sum of simple pieces, one per multiplication. In 2022 DeepMind searched for short sums with a version of AlphaZero (topic 8); two months later two mathematicians in Linz matched its best result with a random walk; in 2025 a system that evolves programs with a language model joined the search."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: three ways of searching for algorithms."),
        ]),
        dict(id="play", eyebrow="Try it", title="Walk the flip graph", toc="Try it", blocks=[
            dict(type="p", text="Here is the schoolbook method for 2 × 2 matrices, written as 8 multiplications. A flip picks two rows that share a factor and rewrites them so that their sum stays the same; when two rows come to share two factors they merge, and the algorithm needs one multiplication fewer. Flip at random, or walk until a multiplication disappears. The check on the right adds up the rows after every step."),
            dict(type="widget", html=FG_HTML, js=FG_JS, css=FG_CSS,
                 fallback=dict(type="svg", name="seven", draw=seven_svg(d), alt="A 2 × 2 algorithm with seven multiplications, found by a random walk", width=760),
                 note="In the interactive edition you can walk the 2 × 2 flip graph yourself."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="An algorithm is a sum of pieces", toc="How it works", blocks=[
            dict(type="p", text="**The tensor.** For n × n matrices, number the entries of A, B and C from 1 to n². The multiplication tensor T has a 1 at (entry (i, j) of A, entry (j, k) of B, entry (k, i) of the result) for every i, j, k, and 0 elsewhere: it lists which products of an A entry and a B entry contribute to which entry of the product."),
            dict(type="p", text="**Pieces are multiplications.** A rank-one piece u ⊗ v ⊗ w says: form the sum of A's entries weighted by u, the sum of B's entries weighted by v, multiply them once, and add the product to C's entries as w says. If R pieces add up to T exactly, those R multiplications compute AB. The schoolbook method has n³ pieces; Strassen's has 7 for n = 2."),
            dict(type="p", text="**Flips and reductions.** Two pieces that share a factor, a ⊗ b ⊗ c + a ⊗ b′ ⊗ c′, equal a ⊗ (b + b′) ⊗ c + a ⊗ b′ ⊗ (c′ − c): a flip, which changes the algorithm but not what it computes. If two pieces come to share two factors, a ⊗ b ⊗ c + a ⊗ b ⊗ c′ = a ⊗ b ⊗ (c + c′), and the algorithm loses a multiplication. Kauers and Moosbauer's method is a random walk of flips, taking every reduction it meets."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Make the search space precise and the answers checkable. Then any searcher, a learning system, a random walk or an evolving program, can propose algorithms, and a few lines of code can confirm them."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Twenty-three, and forty-seven", toc="Measured", blocks=[
            dict(type="p", text="**The classical schemes**, all with arithmetic modulo 2, each checked against T and on random 0/1 matrices: the schoolbook method for 2 × 2, 3 × 3 and 4 × 4 (8, 27 and 64 multiplications); Strassen's 7; and Strassen applied to 2 × 2 blocks of 2 × 2 blocks, 49 for 4 × 4. All correct."),
            dict(type="p", text=f"**AlphaTensor's 47.** DeepMind published its algorithms as data. The program embeds the 47 pieces for 4 × 4 matrices modulo 2 (file factorizations_f2.npz, key 4,4,4) and checks them: they add up to T exactly, and they multiplied {d['at_trials']} random pairs of 0/1 matrices correctly; leave out the last piece and they no longer do. They use {d['at_ones'][0]} nonzero coefficients against {d['at_ones'][1]} for Strassen twice. The first of the 47 multiplications is {d['at_first']}."),
            dict(type="p", text=f"**Flip graphs, 2 × 2.** Ten random walks from the schoolbook 8 all reached 7, after between {min(f2n):,} and {max(f2n):,} flips. One walk's 7 multiplications, found by random rewriting:"),
            dict(type="table", head=["#", "Multiplication → added to"], num=[0], rows=[[i + 1, a] for i, a in enumerate(d["f2_alg"])]),
            dict(type="p", text=f"**3 × 3.** Ten walks from the schoolbook 27: **{d['f3_reached']} of 10** reached 23 multiplications, Laderman's 1976 record, after between {min(f3n):,} and {max(f3n):,} flips. A few seconds of random flipping matches what took a mathematician's ingenuity."),
            dict(type="p", text=f"**4 × 4.** One walk of {d['f4_flips']} flips from the schoolbook 64 reached **{d['f4_rank']}**: better than the schoolbook, but not Strassen twice (49) or AlphaTensor's 47. Kauers and Moosbauer report 47 over ℤ₂; this program's simple walk, with this budget, does not get there."),
            dict(type="svg", name="walks", draw=walk_svg(d), alt="Rank of the multiplication scheme along random flip-graph walks for 3 × 3 and 4 × 4", width=760),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="DeepMind, Linz, and DeepMind again", toc="The evidence", blocks=[
            dict(type="p", text="DeepMind, 5 October 2022: AlphaTensor is \"the first artificial intelligence (AI) system for discovering novel, efficient, and provably correct algorithms\"; it \"builds upon AlphaZero\" and treats the problem as a \"single-player game\"; \"AlphaTensor's algorithm improves on Strassen's two-level algorithm in a finite field for the first time since its discovery 50 years ago\"; it finds \"up to thousands of matrix multiplication algorithms for each size\". Wikipedia: for 4 × 4 over the two-element field, \"47 multiplication operations, improving on the 49 operations\"."),
            dict(type="p", text="Kauers and Moosbauer (Institute for Algebra, J. Kepler University Linz, 2 December 2022): a flip \"can be done for any two rank-one tensors that share a common factor\"; a reduction \"always leads to a vertex belonging to a lower level\"; \"Starting from the standard algorithm we easily find schemes of rank 23, matching the record set by Laderman in 1976\"; over ℤ₂ they matched 47 for 4 × 4 and found 95 for 5 × 5 \"within seconds\"."),
            dict(type="p", text="Google DeepMind, 14 May 2025: AlphaEvolve is \"an evolutionary coding agent powered by large language models for general-purpose algorithm discovery and optimization\", with \"automated evaluators that verify answers\"; it found a way to multiply 4 × 4 complex-valued matrices with \"48 scalar multiplications\"; on \"over 50 open problems\" it matched the best known solutions in about 75% and improved them in 20%."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The search becomes the subject", toc="Full circle", blocks=[
            dict(type="p", text="This book has followed algorithms found by people, from tally marks onward. Its last topic is algorithms found by algorithms: tree search, random walks and evolving programs, each proposing, each checked by the oldest test there is, doing the arithmetic and comparing."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Strassen's trick saved one multiplication in eight. A random walk, knowing nothing but the rule for a flip, reached Laderman's 23 for 3 × 3 in {d['f3_reached']} walks of 10."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many entries does the 3 × 3 multiplication tensor have, and how many are 1?", "9 × 9 × 9 = 729 entries; 27 of them are 1, one for each i, j, k."),
            ("Apply a flip to a ⊗ b ⊗ c + a ⊗ b′ ⊗ c′. What do you get, and why is the sum unchanged?", "a ⊗ (b + b′) ⊗ c + a ⊗ b′ ⊗ (c′ − c). Expanding gives a⊗b⊗c + a⊗b′⊗c + a⊗b′⊗c′ − a⊗b′⊗c: the middle terms cancel."),
            ("Strassen applied twice to 4 × 4 uses how many multiplications? And to 8 × 8, three times?", "7² = 49; 7³ = 343, against 512 for the schoolbook method."),
            ("Why is a discovered algorithm easy to trust, even if the search is not?", "Its pieces can be added up and compared with the tensor exactly, in a fraction of a second."),
            ("Why does arithmetic modulo 2 matter for AlphaTensor's 47?", "Its pieces were found and checked with 1 + 1 = 0; Wikipedia calls the result \"restricted to mod 2 arithmetic\". AlphaEvolve's 48 (2025) is for complex numbers, an improvement on Strassen's algorithm there."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="AlphaTensor's algorithms, as data (2022)", text="Google DeepMind, factorizations_f2.npz, CC BY 4.0.",
                 draw=C.draw_manuscript, link="https://github.com/google-deepmind/alphatensor", link_text="github.com/google-deepmind/alphatensor", licence="Drawn placeholder."),
            dict(title="Flip Graphs for Matrix Multiplication (2022)", text="Kauers and Moosbauer, arXiv:2212.01175.",
                 draw=C.draw_manuscript, link="https://arxiv.org/abs/2212.01175", link_text="arXiv:2212.01175", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "AlgorithmDiscovery", d["checks"],
                           "the schoolbook, Strassen and Strassen-twice schemes, AlphaTensor's 47 pieces against the tensor and on 10,000 random products, and every scheme the flip walks find.",
                           ["static boolean isMultiplication(List<int[]> S, int n)",
                            "static List<int[]> walk(List<int[]> start, int target, long maxFlips, long patience, Random r, long[] flipsUsed, List<long[]> log)"]),
    ]
    return dict(
        title="Algorithms That Find Algorithms", date="2022–2025",
        description="Era 9, topic 13 of The Algorithm Evolution Atlas: matrix multiplication algorithms found by AlphaTensor (2022), flip graphs (Kauers and Moosbauer, 2022) and AlphaEvolve (2025), with AlphaTensor's 47 checked and Laderman's 23 found by random walk.",
        lede="For half a century people searched for ways to multiply matrices with fewer multiplications. In 2022 a learning system found one for 4 × 4 matrices that beat Strassen applied twice, at least modulo 2; two mathematicians matched it with a random walk two months later. Whatever finds an algorithm, checking it takes a fraction of a second.",
        fieldnote=f"I gave the program DeepMind's 47 multiplications for 4 × 4 matrices, and it confirmed every one of them by adding up the pieces. Then I let it rewrite the schoolbook method at random, two pieces at a time. For 3 × 3 it arrived at 23 multiplications, Laderman's record of 1976, in {d['f3_reached']} walks of ten. The species had begun to search for its algorithms with its algorithms.",
        card=[("When", "October 2022; December 2022; May 2025"),
              ("Where", "DeepMind; J. Kepler University Linz; Google DeepMind"),
              ("What hurt", "An astronomically large space of algorithms, searched by hand"),
              ("The fix", "Algorithms as tensor decompositions, found by machine search and checked exactly"),
              ("Checked", f"AlphaTensor's 47; 23 for 3 × 3 in {d['f3_reached']} of 10 walks")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AlgorithmDiscovery.java`.",
    )
