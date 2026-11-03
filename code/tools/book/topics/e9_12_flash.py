"""Era 9, topic 12: FlashAttention. Every number is parsed from FlashAttention.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("online: "):
            d["online"] = re.search(r"against two passes: largest difference ([\d.eE+-]+)", ln).group(1)
            d["safe"] = re.search(r"weights are ([\d.]+), ([\d.]+), ([\d.]+)", ln).groups()
        elif ln.startswith("exact: "):
            d["M"] = re.search(r"fast memory M = ([\d,]+) numbers", ln).group(1)
            d["d"] = re.search(r"exact: d (\d+)", ln).group(1)
            d["exact"] = re.findall(r"N ([\d,]+): blocks Bc (\d+), Br (\d+) ; largest difference in O ([\d.eE+-]+) ; main-memory traffic standard ([\d,]+), FlashAttention ([\d,]+) \(([\d.]+) times less\)", ln)
        elif ln.startswith("traffic: "):
            d["traffic"] = re.findall(r"N ([\d,]+): standard ([\d,]+), FlashAttention ([\d,]+) \(12 N\^2 d\^2 / M = ([\d,]+)\), ratio ([\d.]+) ; extra memory: standard ([\d,]+) numbers for S and P, FlashAttention ([\d,]+) for m and l", ln)
            d["byd"] = re.findall(r"d (\d+): ratio ([\d.]+)", ln.split("by head size: ")[1])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def tiles_svg(d):
    def draw(t, standalone):
        W, H = 760, 340
        o = [C.text(20, 26, "Standard attention writes the whole score table to main memory; FlashAttention works one tile at a time", t["ink"], 13, "start", 700)]
        n = 6
        for p, (x0, lab) in enumerate([(40, "standard: S and P, N × N, in main memory"), (420, "FlashAttention: one tile in fast memory")]):
            for i in range(n):
                for j in range(n):
                    x, y = x0 + j * 38, 50 + i * 38
                    if p == 0:
                        o.append(C.rect(x, y, 34, 34, t["red"], None, 0, 2, ";fill-opacity:0.55"))
                    else:
                        on = (i == 2 and j == 3)
                        done = j < 3
                        o.append(C.rect(x, y, 34, 34, t["blue"] if on else t["wash"], t["blue"] if done or on else t["rule"], 1.5, 2, ";fill-opacity:0.9" if on else ""))
            o.append(C.text(x0, 300, lab, t["muted"], 12))
        o.append(C.text(420, 285, "columns: blocks of K and V; rows: blocks of Q", t["muted"], 11))
        o.append(C.text(20, 330, "Outlined tiles have been visited and thrown away; only O and two numbers per row (m and l) are kept in main memory.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Standard attention against FlashAttention's tiles", t, standalone, 0.55, 760)
    return draw


FA_HTML = """
<div class="board fa-board">
  <div style="min-width:0"><div class="fa-view" id="fa-view"></div></div>
  <div style="min-width:0">
    <label class="fa-row">Blocks per side <input type="range" id="fa-n" min="2" max="8" value="4"> <b id="fa-nv"></b></label>
    <div class="fa-btns"><button type="button" class="primary" id="fa-step">Next tile</button><button type="button" id="fa-all">Run to the end</button><button type="button" id="fa-reset">Start over</button></div>
    <div class="fa-h">Row 1 of the scores, so far</div>
    <div class="fa-res" id="fa-row1"></div>
    <div class="fa-h">Main-memory traffic, in numbers (N = 128 per block side, d = 64)</div>
    <div class="fa-res" id="fa-traffic"></div>
    <p class="say" id="fa-say" aria-live="polite"></p>
  </div>
</div>
"""

FA_CSS = """
.fa-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.fa-board{grid-template-columns:1fr}}
.fa-view svg{width:100%;height:auto;display:block;background:var(--wash)}
.fa-row{display:block;font-size:13px;margin:4px 0}
.fa-row input{vertical-align:middle}
.fa-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.fa-h{font-size:12px;font-weight:700;color:var(--muted);margin:10px 0 4px}
.fa-res{font:12.5px var(--mono);display:grid;gap:2px}
"""

FA_JS = r"""
(() => {
  const view = document.getElementById("fa-view");
  if (!view) return;
  const B = 128, d = 64;
  let n, j, i, done, row, m, l, seed = 4, traffic;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const gauss = () => { let u = 0; while (u === 0) u = rnd(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd()); };
  function reset() {
    n = +document.getElementById("fa-n").value; document.getElementById("fa-nv").textContent = n;
    j = 0; i = 0; done = new Set(); m = -Infinity; l = 0; traffic = 0;
    row = [...Array(n * 4)].map(() => 3 * gauss()); // 4 scores per block, a stand-in for one row of S
    draw("Each tile is a block of queries against a block of keys and values. Step through: the outer loop walks the key blocks, the inner loop the query blocks.");
  }
  function draw(msg) {
    view.innerHTML = "";
    const S = 340 / n, svg = sv("svg", {viewBox: "0 0 400 400", role: "img", "aria-label": "The score table cut into tiles"}, view);
    sv("text", {x: 30, y: 20, "font-size": 12, fill: "var(--muted)"}, svg, "K and V blocks →");
    sv("text", {x: 14, y: 40, "font-size": 12, fill: "var(--muted)", transform: "rotate(90 14 40)"}, svg, "Q blocks →");
    for (let a = 0; a < n; a++) for (let b = 0; b < n; b++) {
      const cur = a === i && b === j && done.size < n * n, was = done.has(a * n + b);
      sv("rect", {x: 30 + b * S, y: 30 + a * S, width: S - 3, height: S - 3, rx: 3, fill: cur ? "var(--blue)" : "var(--paper)", "fill-opacity": cur ? 0.85 : 1, stroke: was ? "var(--blue)" : "var(--rule)", "stroke-width": was ? 2 : 1}, svg);
      if (was) sv("text", {x: 30 + b * S + S / 2 - 1, y: 30 + a * S + S / 2 + 4, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}, svg, "done");
    }
    const r1 = document.getElementById("fa-row1"); r1.innerHTML = "";
    el("div", {}, r1, `running max m = ${isFinite(m) ? m.toFixed(3) : "−∞"}`);
    el("div", {}, r1, `running sum l = ${l.toFixed(4)}`);
    const N = n * B, std = 4 * N * N + 4 * N * d;
    const tr = document.getElementById("fa-traffic"); tr.innerHTML = "";
    el("div", {}, tr, `standard, whole run   ${std.toLocaleString("en-US")}`);
    el("div", {}, tr, `FlashAttention so far ${traffic.toLocaleString("en-US")}`);
    document.getElementById("fa-say").textContent = msg;
  }
  function step() {
    if (done.size === n * n) return;
    if (i === 0) traffic += 2 * B * d; // K_j and V_j into fast memory
    traffic += 3 * B * d + 4 * B; // Q_i and O_i (and l, m) in, O_i (and l, m) out
    done.add(i * n + j);
    let msg = `Tile (query block ${i + 1}, key block ${j + 1}): scores computed in fast memory, used, and thrown away.`;
    if (i === 0) {
      const blk = row.slice(4 * j, 4 * j + 4), mt = Math.max(...blk), mNew = Math.max(m, mt);
      const scale = isFinite(m) ? Math.exp(m - mNew) : 0;
      l = l * scale + blk.reduce((s, v) => s + Math.exp(v - mNew), 0);
      msg += isFinite(m) && mNew > m ? ` Row 1 found a new maximum, so its partial sum and output were multiplied by exp(m − m′) = ${scale.toFixed(3)}.` : " Row 1's maximum did not change, so nothing is rescaled.";
      m = mNew;
    }
    i++; if (i === n) { i = 0; j++; }
    if (done.size === n * n) {
      const exact = row.reduce((s, v) => s + Math.exp(v - Math.max(...row)), 0);
      msg = `Finished. Row 1's running sum ${l.toFixed(4)} equals the two-pass sum ${exact.toFixed(4)}: the same softmax, without ever holding the whole row.`;
    }
    draw(msg);
  }
  document.getElementById("fa-step").addEventListener("click", step);
  document.getElementById("fa-all").addEventListener("click", () => { while (done.size < n * n) step(); });
  document.getElementById("fa-reset").addEventListener("click", reset);
  document.getElementById("fa-n").addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How FlashAttention combined older ideas, and where it led")
    W = 250
    nodes = {
        "tf": (40, 20, "Attention", "softmax(QKᵀ/√d)V over all pairs", "topic 9, 2017", "ink"),
        "on": (375, 20, "Online softmax", "a running maximum and sum, one pass", "Milakov and Gimelshein, 2018", "ink"),
        "io": (710, 20, "Thinking in memory traffic", "count reads and writes, not only arithmetic", "", "ink"),
        "fa": (375, 200, "FlashAttention", "⊕ tiles in fast memory, exact, linear memory", "Dao, Fu, Ermon, Rudra and Ré, 2022", "red"),
        "long": (40, 380, "Longer contexts", "sequences of thousands of tokens", "", "blue"),
        "fast": (710, 380, "Faster training", "the same model, less waiting on memory", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("tf", "fa", ports=("bottom", "top:0.15"))
    D.edge("on", "fa", ports=("bottom", "top"))
    D.edge("io", "fa", ports=("bottom", "top:0.85"))
    D.edge("fa", "long", ports=("bottom:0.15", "top"))
    D.edge("fa", "fast", ports=("bottom:0.85", "top"))
    return D


def chain():
    steps = [
        ("Attention's N × N table: memory grows with the square of the length",
         "Never store the table: compute it tile by tile", "Dao and colleagues, 2022"),
        ("The softmax of a row seems to need the whole row before any weight is known",
         "Keep a running maximum and sum; rescale when the maximum grows", "Milakov and Gimelshein, 2018"),
        ("Moving numbers to and from slow memory, not arithmetic, set the speed",
         "Load each block of K and V once, and count the traffic", "the same paper"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from the full table to tiles")
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
    ex, tr = d["exact"], d["traffic"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The Transformer's attention (topic 9) compares every position with every other. In 2018 Milakov and Gimelshein showed how to compute a softmax in one pass, keeping a running maximum and sum. Dao, Fu, Ermon, Rudra and Ré combined that with a habit from the analysis of algorithms for slow memory: count the reads and writes. The result computes exactly the same attention with far less traffic."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: FlashAttention. Blue: what it was for."),
        ]),
        dict(id="play", eyebrow="Try it", title="One tile at a time", toc="Try it", blocks=[
            dict(type="p", text="The square is the table of attention scores, cut into tiles. Step through FlashAttention's loops: each tile is computed in fast memory and thrown away. Watch the first row's running maximum and sum, and the traffic to main memory, which standard attention spends on writing and reading the whole table."),
            dict(type="widget", html=FA_HTML, js=FA_JS, css=FA_CSS,
                 fallback=dict(type="svg", name="tiles", draw=tiles_svg(d), alt="Standard attention's full table against FlashAttention's tiles", width=760),
                 note="In the interactive edition you can step through the tiles and watch the running softmax."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A running maximum and sum", toc="How it works", blocks=[
            dict(type="p", text="**Standard attention** computes S = QKᵀ/√d, writes it to main memory, reads it back to compute P = softmax(S) row by row, writes P, then reads P again to compute O = PV. For N positions that is about 4N² numbers moved, and N² numbers of memory for S and P."),
            dict(type="p", text="**The online softmax.** Read a row's scores one block at a time, keeping the largest so far, m, and the sum so far of e^(score − m), l. When a new block brings a larger maximum m′, multiply l (and the partial output) by e^(m − m′) before adding the new block's terms. At the end, l and m are exactly what two passes would give."),
            dict(type="p", text="**Tiling.** FlashAttention's outer loop loads one block of K and V into fast memory; the inner loop loads each block of Q with its partial output O and its m and l, computes that tile's scores, updates O, m and l, and writes them back. Nothing of size N × N is ever stored. Main-memory traffic is about 12N²d²/M numbers for a fast memory of M numbers, and the extra memory is two numbers per row."),
            dict(type="callout", kind="key", label="Key idea",
                 text="When moving data costs more than computing with it, reorder the computation to move less. A softmax can be built up block by block, as long as the partial sums are rescaled whenever the maximum changes."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Same numbers, less traffic", toc="Measured", blocks=[
            dict(type="p", text=f"**The online softmax**, one pass against two on 1,000 scores: largest difference {C.sci(d['online'])}. For the scores 1000, 999 and 998, the sum of e^score overflows to infinity; subtracting the maximum first gives the weights {', '.join(d['safe'])}."),
            dict(type="p", text=f"**Both methods, computed.** Random Q, K and V with d = {d['d']}, a fast memory of M = {d['M']} numbers (192 KB of 4-byte numbers, one streaming multiprocessor's SRAM on the paper's GPU). The program counts every number each method reads from or writes to main memory:"),
            dict(type="table", head=["N", "Blocks Bc × Br", "Largest difference in O", "Standard traffic", "FlashAttention traffic", "Less by"], num=[0, 3, 4, 5],
                 rows=[[n, f"{bc} × {br}", C.sci(df), s, f, r + "×"] for n, bc, br, df, s, f, r in ex]),
            dict(type="p", text="The outputs agree to the last few bits of a double: FlashAttention is exact attention, computed in a different order."),
            dict(type="p", text="**Longer sequences**, counted by running FlashAttention's loops without the arithmetic:"),
            dict(type="table", head=["N", "Standard", "FlashAttention", "12N²d²/M", "Less by", "Extra memory, standard", "FlashAttention"], num=[0, 1, 2, 3, 4, 5, 6],
                 rows=[[n, s, f, fm, r + "×", es, ef] for n, s, f, fm, r, es, ef in tr], hl=len(tr) - 1),
            dict(type="p", text=f"The traffic saving tends to a constant, about M/(3d²); it depends on the head size: at N = 16,384, " + ", ".join(f"d = {a}: {b}×" for a, b in d["byd"]) + ". The memory saving grows without limit: N² numbers against 2N. In this simple model, with 4-byte numbers and d = 128 the tiles are too small to save traffic at all; real GPU kernels differ from this simple count in ways it leaves out."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Stanford and Buffalo, 2022", toc="The evidence", blocks=[
            dict(type="p", text="Dao, Fu, Ermon and Ré (Stanford University) and Rudra (University at Buffalo, SUNY), NeurIPS 2022: an \"IO-aware exact attention algorithm\" that \"uses tiling to reduce the number of memory reads/writes between GPU high bandwidth memory (HBM)\" and on-chip SRAM; it needs \"less memory—linear in sequence length—than standard attention\"; with a running maximum and sum \"we can compute softmax one block at a time\"; Θ(N²d²M⁻¹) accesses to HBM against Θ(Nd + N²). An A100 has \"192KB of on-chip SRAM per each of 108 streaming multiprocessors\". Measured: \"15% end-to-end wall-clock speedup on BERT-large (seq. length 512)\", \"3× speedup on GPT-2 (seq. length 1K)\"."),
            dict(type="p", text="The NeurIPS abstract states the problem: \"Transformers are slow and memory-hungry on long sequences, since the time and memory complexity of self-attention are\" quadratic in the sequence length."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="B-trees for a graphics card", toc="Full circle", blocks=[
            dict(type="p", text="In the 1970s B-trees (Era 6) were designed around a slow disk: read a whole block at a time and do as much as possible with it. FlashAttention applies the same thinking one level down, between a GPU's main memory and the small memory beside its arithmetic units."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"At N = {tr[-1][0]}, standard attention needs {tr[-1][5]} numbers of extra memory; FlashAttention needs {tr[-1][6]}, and gives the same answer."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A row's scores so far have maximum 2 and l = 1.5. The next block has maximum 3. By what is l multiplied?", "e^(2 − 3) = e^−1 ≈ 0.368, before the new block's terms (relative to 3) are added."),
            ("How many numbers does standard attention store for N = 10,000?", "S and P, 10,000² each: 200 million."),
            ("Why is FlashAttention not an approximation?", "Every score is computed and used; only the order of the sums changes, and the rescaling makes the result equal to the softmax."),
            ("Why does a larger fast memory M help?", "Larger blocks of K and V mean fewer passes over Q and O: traffic falls as 1/M."),
            ("Why does subtracting the maximum not change the softmax?", "e^(sᵢ − m) / Σ e^(sⱼ − m) = e^sᵢ / Σ e^sⱼ: the factor e^−m cancels."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness (2022)", text="Dao, Fu, Ermon, Rudra and Ré, arXiv:2205.14135.",
                 draw=C.draw_manuscript, link="https://arxiv.org/pdf/2205.14135", link_text="arXiv:2205.14135 (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "FlashAttention", d["checks"],
                           "the online softmax, the outputs of the two methods, the traffic counts against 12N²d²/M, and the overflow the maximum prevents.",
                           ["static double[][] flash(double[][] Q, double[][] K, double[][] V, int N, int d, long M, boolean compute)"]),
    ]
    return dict(
        title="FlashAttention", date="2022",
        description="Era 9, topic 12 of The Algorithm Evolution Atlas: FlashAttention (Dao and colleagues, 2022), exact attention in tiles with an online softmax, its main-memory traffic counted.",
        lede="Attention compares every position with every other, and the standard method writes the whole table of scores to slow memory and reads it back. In 2022 a team at Stanford and Buffalo computed exactly the same answer without ever storing the table, one tile at a time.",
        fieldnote=f"I computed attention twice, once the standard way and once in tiles with a running maximum and sum. The answers matched to {ex[-1][3]}. The tiled method moved {ex[-1][6]} times fewer numbers through slow memory at N = {ex[-1][0]}, and at N = {tr[-1][0]} it needed {tr[-1][6]} numbers of extra memory instead of {tr[-1][5]}.",
        card=[("When", "2018; May 2022"),
              ("Where", "Stanford University; University at Buffalo"),
              ("What hurt", "An N × N table moved through slow memory"),
              ("The fix", "Tiles in fast memory, with a rescaled running softmax"),
              ("Checked", f"Same output to {C.sci(ex[-1][3])}; traffic {tr[-1][4]}× less at N = {tr[-1][0]}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `FlashAttention.java`.",
    )
