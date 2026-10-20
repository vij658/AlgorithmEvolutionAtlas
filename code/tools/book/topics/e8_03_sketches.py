"""Era 8, topic 3: Streaming sketches. Every number is parsed from StreamingSketches.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"stream: ([\d,]+) items drawn from ([\d,]+) keys .*? ; exactly: ([\d,]+) distinct keys seen \(F0\), F1 = ([\d,]+), F2 = ([\d,]+), the commonest key ([\d,]+) times", ln):
            d["stream"] = dict(m=m.group(1), n=m.group(2), f0=m.group(3), f1=m.group(4), f2=m.group(5), top=m.group(6))
        elif ln.startswith("ams: "):
            rows = [dict(copies=a, bytes=b, err=c, promised=e, within=f, trials=g) for a, b, c, e, f, g in
                    re.findall(r"([\d,]+) copies \(([\d,]+) bytes\): average error ([\d.]+)%, within the promised ([\d.]+)% in (\d+) of (\d+) trials", ln)]
            mm = re.search(r"median of 9 averages of 256 copies: ([\d,]+) against ([\d,]+) \(error ([\d.]+)%\)", ln)
            d["ams"] = dict(rows=rows, med=mm.group(1), truth=mm.group(2), err=mm.group(3))
        elif m := re.match(r"countmin: epsilon = ([\d.]+), delta = ([\d.]+), so (\d+) rows of ([\d,]+) counters \(([\d,]+) counters in all, against ([\d,]+) for exact counts\) ; all ([\d,]+) keys queried: none too low, ([\d,]+) exact, ([\d,]+) too high by more than epsilon m = ([\d,]+) \(allowed: ([\d,]+)\), largest overestimate ([\d,]+) ; keys with at least 1% of the stream: (\d+) really, (\d+) reported, none missed", ln):
            d["cm"] = dict(eps=m.group(1), delta=m.group(2), d=m.group(3), w=m.group(4), total=m.group(5), exact=m.group(6), keys=m.group(7),
                           same=m.group(8), high=m.group(9), em=m.group(10), allowed=m.group(11), worst=m.group(12), truly=m.group(13), rep=m.group(14))
        elif ln.startswith("distinct: "):
            rows = [dict(m=a, hll=b, th=c, hb=e, fm=f, fth=g, fb=h) for a, b, c, e, f, g, h in
                    re.findall(r"m = ([\d,]+): HyperLogLog ([\d.]+)% \(theory ([\d.]+)%, ([\d,]+) bytes at 6 bits a register\), Flajolet-Martin ([\d.]+)% \(theory ([\d.]+)%, ([\d,]+) bytes of bitmaps\)", ln)]
            mm = re.search(r"([\d,]+) distinct items in ([\d,]+) registers \(([\d,]+) bytes\): estimate ([\d,]+) \(error ([\d.]+)%\)", ln)
            d["distinct"] = dict(rows=rows, big=mm.group(1), regs=mm.group(2), bytes=mm.group(3), est=mm.group(4), err=mm.group(5))
        elif ln.startswith("widget: "):
            m = re.search(r"widget: (\d+) words, (\d+) different .*? counters: (.*?) ; (\d+) of (\d+) words overestimated ; [^;]*: (.*)$", ln)
            rows = [[int(x) for x in r.split(",")] for r in m.group(3).split(" | ")]
            d["widget"] = dict(words=int(m.group(1)), diff=int(m.group(2)), counters=rows, over=int(m.group(4)),
                               freq=[(a, int(b), int(c)) for a, b, c in (p.split(":") for p in m.group(6).split())])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def countmin_svg(d):
    """A Count-Min sketch: one word hashed into one counter of each row; the estimate is the smallest."""
    def draw(t, standalone):
        o = []
        W, H = 760, 290
        o.append(C.text(20, 26, "Count-Min: every word adds 1 to one counter in each row; ask for a word, take the smallest of its counters", t["ink"], 13, "start", 700))
        x0, y0, cw, ch = 150, 84, 56, 40
        vals = [[3, 0, 7, 2, 5, 1, 4, 2, 6, 0], [1, 5, 2, 8, 0, 3, 2, 4, 1, 6], [2, 4, 0, 1, 6, 9, 3, 1, 2, 4]]
        hit = [2, 3, 5]
        o.append(C.text(20, 58, "The word \"the\": hash 1 picks counter 3 of row 1, hash 2 counter 4 of row 2, hash 3 counter 6 of row 3.", t["ink"], 12.5, "start"))
        for r in range(3):
            o.append(C.text(x0 - 12, y0 + r * (ch + 10) + ch / 2 + 5, f"row {r + 1}", t["muted"], 12, "end"))
            for c in range(10):
                x, y = x0 + c * cw, y0 + r * (ch + 10)
                on = c == hit[r]
                o.append(C.rect(x, y, cw - 4, ch, t["yellow"] if on else t["surface"], t["ink"] if on else t["axis"], 2 if on else 1))
                o.append(C.text(x + (cw - 4) / 2, y + ch / 2 + 5, str(vals[r][c]), t["on_yellow"] if on else t["ink"], 14 if on else 12.5, "middle", 700 if on else 400))
        o.append(C.text(20, y0 + 3 * (ch + 10) + 22, "Estimate for \"the\": min(7, 8, 9) = 7. Each counter also holds the other words that share it, so none is", t["ink"], 12.5, "start"))
        o.append(C.text(20, y0 + 3 * (ch + 10) + 40, "ever too low, and the smallest is the least spoiled. (An illustration; the widget and the program use real counts.)", t["ink"], 12.5, "start"))
        return C.svg_doc(W, H, "".join(o), "A Count-Min sketch with three rows", t, standalone, 0.55, 760)
    return draw


CM_HTML = """
<div class="board cm-board">
  <div style="min-width:0">
    <div class="cm-text" id="cm-text"></div>
    <div class="cm-grid" id="cm-grid"></div>
  </div>
  <div style="min-width:0">
    <div class="cm-btns"><button type="button" class="primary" id="cm-1">Next word</button><button type="button" id="cm-all">All the rest</button><button type="button" id="cm-reset">Start again</button></div>
    <div class="cm-stats" id="cm-stats"></div>
    <p class="say" id="cm-say" aria-live="polite"></p>
  </div>
</div>
"""

CM_CSS = """
.cm-text{font-size:13.5px;line-height:1.7;margin-bottom:10px}
.cm-text span{cursor:pointer;padding:0 1px;border-radius:2px}
.cm-text span.done{color:var(--ink)} .cm-text span.todo{color:var(--muted)}
.cm-text span.cur{background:var(--yellow);color:var(--on-yellow)}
.cm-text span.ask{outline:2px solid var(--blue)}
.cm-grid{display:grid;grid-template-columns:repeat(16,minmax(0,1fr));gap:2px;font:11px var(--mono)}
.cm-grid div{background:var(--wash);text-align:center;padding:3px 0;border:1px solid transparent}
.cm-grid div.hit{background:var(--yellow);color:var(--on-yellow);border-color:var(--ink)}
.cm-grid div.ask{border-color:var(--blue);font-weight:700}
.cm-grid .rl{grid-column:1/-1;background:none;text-align:left;color:var(--muted);padding:6px 0 1px}
.cm-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.cm-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

CM_JS = r"""
(() => {
  const gridEl = document.getElementById("cm-grid");
  if (!gridEl) return;
  const WORDS = __WORDS__, PROG = __COUNTERS__, A = [3, 7, 11], B = [1, 5, 9], P = 65521, W = 32;
  function hash(w) { let h = 0; for (const ch of w) h = (31 * h + ch.charCodeAt(0)) % P; return h; }
  const cell = (w, r) => ((A[r] * hash(w) + B[r]) % P) % W;
  let cm, at, asked = null;
  const textEl = document.getElementById("cm-text");
  const spans = WORDS.map((w, i) => { const s = el("span", {}, textEl, w); textEl.appendChild(document.createTextNode(" ")); s.addEventListener("click", () => { asked = w; draw(); }); return s; });
  function reset() { cm = [0, 1, 2].map(() => new Array(W).fill(0)); at = 0; asked = null; draw("Press Next word: each word adds 1 to one counter in each of the three rows. Click any word to ask how often it has been seen."); }
  function add(n) { for (let k = 0; k < n && at < WORDS.length; k++, at++) for (let r = 0; r < 3; r++) cm[r][cell(WORDS[at], r)]++; }
  function draw(msg) {
    spans.forEach((s, i) => { s.className = (i < at ? "done" : "todo") + (i === at - 1 ? " cur" : "") + (asked === WORDS[i] ? " ask" : ""); });
    gridEl.innerHTML = "";
    const last = at > 0 ? WORDS[at - 1] : null;
    for (let r = 0; r < 3; r++) {
      el("div", {class: "rl"}, gridEl, `row ${r + 1}: counter ((${A[r]} h + ${B[r]}) mod 65521) mod 32`);
      for (let c = 0; c < W; c++) el("div", {class: (last && cell(last, r) === c ? "hit" : "") + (asked && cell(asked, r) === c ? " ask" : "")}, gridEl, String(cm[r][c]));
    }
    const st = document.getElementById("cm-stats"); st.innerHTML = "";
    el("div", {}, st, `words read: ${at} of ${WORDS.length}`);
    el("div", {}, st, `memory: 96 counters, whatever the text`);
    if (asked) {
      const est = Math.min(...[0, 1, 2].map(r => cm[r][cell(asked, r)])), truth = WORDS.slice(0, at).filter(w => w === asked).length;
      el("div", {}, st, `"${asked}": estimate ${est}, true count ${truth}`);
    }
    if (at === WORDS.length) {
      const same = cm.every((row, r) => row.every((v, c) => v === PROG[r][c]));
      msg = (msg ? msg + " " : "") + `All ${WORDS.length} words read. ${same ? "Every counter equals the program's." : "The counters differ from the program's."}`;
    }
    if (msg) document.getElementById("cm-say").textContent = msg;
  }
  document.getElementById("cm-1").addEventListener("click", () => { add(1); draw(`"${WORDS[at - 1]}" goes to counters ${[0, 1, 2].map(r => cell(WORDS[at - 1], r)).join(", ")} of the three rows.`); });
  document.getElementById("cm-all").addEventListener("click", () => { add(WORDS.length); draw(); });
  document.getElementById("cm-reset").addEventListener("click", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How streaming sketches combined older ideas, and where they led")
    W = 210
    nodes = {
        "hash": (20, 20, "Hashing", "spread items evenly at random", "Era 5", "ink"),
        "fm": (395, 20, "Probabilistic counting", "distinct items from hashed bit patterns", "Flajolet and Martin, 1983–85", "ink"),
        "rand": (770, 20, "Random signs", "cross terms cancel on average", "", "ink"),
        "ams": (395, 180, "Frequency moments", "⊕ one pass, small memory, proved bounds", "Alon, Matias, Szegedy, 1996", "red"),
        "cm": (20, 340, "Count-Min", "⊕ the smallest of d counters", "Cormode, Muthukrishnan, 2005", "ink"),
        "hll": (770, 340, "HyperLogLog", "⊕ registers and a harmonic mean", "Flajolet and others, 2007", "ink"),
        "today": (395, 490, "Sketches", "the 2005 Gödel Prize; databases and networks", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("hash", "ams", ports=("bottom", "top:0.15"))
    D.edge("fm", "ams", ports=("bottom", "top"))
    D.edge("rand", "ams", ports=("bottom", "top:0.85"))
    D.edge("ams", "cm", ports=("bottom:0.15", "top"))
    D.edge("fm", "hll", ports=("right", "top"), label="LogLog, 2003", at=0.55, dx=8, anchor="start")
    D.edge("ams", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: the Gödel Prize as Wikipedia records it; the uses named in the prize citation.", "caption")
    return D


def chain(d):
    s, a, cm, ds = d["stream"], d["ams"], d["cm"], d["distinct"]
    r256 = a["rows"][-1]
    hl = ds["rows"][-2]
    steps = [
        (f"Exact counts of a stream need a counter for every key: {s['n']} here",
         f"A sketch: {r256['copies']} signed sums ({r256['bytes']} bytes) estimate F₂ within {r256['err']}% on average", "Alon, Matias and Szegedy, 1996"),
        ("F₂ says how repetitive a stream is, not how often one item came",
         f"Count-Min: {cm['total']} counters, every one of {cm['keys']} keys within {cm['em']} and never too low", "Cormode and Muthukrishnan, 2005"),
        ("How many different items? Counting needs a list of all seen",
         f"HyperLogLog: {hl['m']} registers ({hl['hb']} bytes), error {hl['hll']}%", "Flajolet and others, 2007"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from exact counts to sketches")
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
    s, a, cm, ds, wg = d["stream"], d["ams"], d["cm"], d["distinct"], d["widget"]
    para = re.search(r'PARAGRAPH = (".*?");', ctx["java"], re.S).group(1)
    words = "".join(re.findall(r'"(.*?)"', para)).split(" ")
    assert len(words) == wg["words"], "the widget's text matches the program's"
    ams_rows = [[r["copies"], r["bytes"], r["err"] + "%", r["promised"] + "%", f"{r['within']} of {r['trials']}"] for r in a["rows"]]
    ds_rows = [[r["m"], r["hll"] + "%", r["th"] + "%", r["hb"], r["fm"] + "%", r["fth"] + "%", r["fb"]] for r in ds["rows"]]
    wf_rows = [[w, str(t), str(e)] for w, t, e in wg["freq"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Hashing (Era 5) scatters items at random. Flajolet and Martin used the bit patterns of hashed items to count distinct ones in a single pass. Alon, Matias and Szegedy multiplied counts by random signs so that the cross terms cancel, and proved which questions about a stream need little memory and which need a lot. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the 1996 paper credited with founding the field. Blue: where it led."),
        ]),
        dict(id="play", eyebrow="Try it", title="Count words you cannot keep", toc="Try it", blocks=[
            dict(type="p", text=f"A paragraph of {wg['words']} words ({wg['diff']} different) streams into a Count-Min sketch of three rows of 32 counters. Each word adds 1 to one counter in each row, chosen by that row's hash. Click any word to ask how often it has been seen: the answer is the smallest of its three counters, which is never too low but often too high, because other words share the cells. The widget uses the program's hash functions, and after the last word its 96 counters equal the program's."),
            dict(type="widget", html=CM_HTML, js=CM_JS.replace("__WORDS__", json.dumps(words)).replace("__COUNTERS__", json.dumps(wg["counters"])), css=CM_CSS,
                 fallback=dict(type="table", head=["Word", "True count", "Estimate"], num=[1, 2], rows=wf_rows),
                 note=f"In the interactive edition you can feed the words in one by one and query any of them. In the program's run, {wg['over']} of {wg['diff']} words were overestimated."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Three questions, three sketches", toc="How it works", blocks=[
            dict(type="p", text="**How repetitive is the stream?** The second frequency moment is F₂ = Σ (count of item i)². Give every item a random sign s(i) = ±1 and keep one number, Z = the sum of s(item) over the stream. Then Z² = Σ count² + Σ (cross terms with random signs), and the cross terms cancel on average, so Z² averages to F₂. Average many independent copies to narrow the spread; take the median of several averages to make a bad answer rare. The signs come from a random cubic polynomial modulo a prime, which makes any four of them independent: exactly what the proof needs."),
            dict(type="p", text="**How often did this item come?** Count-Min keeps d rows of w counters, each row with its own hash. Every item adds 1 to its counter in each row. Other items that share a counter only add, so each counter is an overestimate and the smallest of the d is the best one. With w = e/ε and d = ln(1/δ), the estimate exceeds the truth by more than ε times the stream's length with probability at most δ."),
            dict(type="svg", name="countmin", draw=countmin_svg(d), alt="A Count-Min sketch with three rows and one word hashed into each", width=760),
            dict(type="p", text="**How many different items?** Hash every item to a random-looking string of bits. Among n different items, about one in 2ᵏ has a hash starting with k zeros, so the longest run of leading zeros says roughly log₂ n. One such guess is crude; HyperLogLog splits the items into m groups by the first bits of the hash, keeps the longest run in each group (a register of 6 bits), and combines the m guesses with a harmonic mean. Its error is about 1.04/√m, however many items there are. Repeats change nothing: a second copy of an item hashes to the same bits."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Decide in advance which question you will ask, and keep only a small random summary that answers it, with an error you can state. A different question needs a different sketch, and some questions, like the largest count exactly, need memory proportional to the stream whatever you do."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A million items, a few kilobytes", toc="Measured", blocks=[
            dict(type="p", text=f"**The stream.** {s['m']} items drawn from {s['n']} keys with a Zipf law, so a few keys are very common: exactly {s['f0']} different keys appeared, F₂ = {s['f2']}, and the commonest key appeared {s['top']} times."),
            dict(type="p", text="**F₂ from signed sums.** Each average below was repeated 40 times with fresh random signs:"),
            dict(type="table", head=["Copies averaged", "Memory", "Average error", "Promised within", "Trials within"], num=[0, 1, 2, 3], rows=ams_rows, hl=len(ams_rows) - 1),
            dict(type="p", text=f"The median of 9 averages of 256 copies gave {a['med']} against {a['truth']}, an error of {a['err']}%."),
            dict(type="p", text=f"**Count-Min**, ε = {cm['eps']}, δ = {cm['delta']}: {cm['d']} rows of {cm['w']} counters, {cm['total']} in all, against {cm['exact']} for exact counts. All {cm['keys']} keys were queried: none was too low, {cm['high']} were too high by more than εm = {cm['em']} (at most {cm['allowed']} are allowed), and the largest overestimate was {cm['worst']}. Every one of the {cm['truly']} keys holding at least 1% of the stream was reported."),
            dict(type="p", text=f"**Distinct items** ({s['f0']} of them), with 200 different hash functions; the spread is the root-mean-square relative error:"),
            dict(type="table", head=["Registers m", "HyperLogLog", "Theory 1.04/√m", "Bytes", "Flajolet–Martin", "Theory 0.78/√m", "Bytes"], num=[0, 1, 2, 3, 4, 5, 6], rows=ds_rows),
            dict(type="p", text=f"HyperLogLog's registers are smaller than Flajolet and Martin's bitmaps, so for the same memory it is more accurate. Ten million distinct items in {ds['regs']} registers ({ds['bytes']} bytes): estimate {ds['est']}, error {ds['err']}%."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Founding a field in logarithmic space", toc="The evidence", blocks=[
            dict(type="p", text="Alon (Tel Aviv University), Matias (Bell Laboratories) and Szegedy (AT&T Research), first at STOC in May 1996: \"Surprisingly, it turns out that the numbers F0, F1 and F2 can be approximated in logarithmic space\", while F_k for k ≥ 6 needs polynomial space and the largest count needs Ω(n). The F₂ estimator uses four-wise independent ±1 values, E(X) = F₂ and variance at most 2F₂², with averages of 16/λ² copies and a median of 2 log(1/δ) averages. Wikipedia: the field \"was first formalized and popularized\" by this paper, whose authors won the Gödel Prize in 2005."),
            dict(type="p", text="Flajolet (INRIA) and Martin (IBM, Hursley), *JCSS* 1985: algorithms that \"estimate the number of distinct elements in a large collection of data\" in one pass, about 5% error with 256 words. Cormode and Muthukrishnan, *Journal of Algorithms*, April 2005: \"We introduce a new sublinear space data structure-the Count-Min Sketch- for summarizing data streams\", with aᵢ ≤ âᵢ and, with probability 1 − δ, âᵢ ≤ aᵢ + ε‖a‖₁. Flajolet, Fusy, Gandouet and Meunier, 2007: HyperLogLog's error is \"typically about 1.04/√m\", estimating cardinalities \"well beyond 10⁹\" with \"a typical accuracy of 2% while using a memory of only 1.5 kilobytes\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Hashing, used for forgetting", toc="Full circle", blocks=[
            dict(type="p", text="Era 5's hash tables used hashing to find things quickly. Sketches use it to forget most of what they see, on purpose and with a known cost. MinHash (topic 5) is a sketch for similarity; consistent hashing (topic 4) uses the same scattering to decide which machine holds what."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{s['m']} items, {s['f0']} different. A list of them would take hundreds of kilobytes; HyperLogLog with 4,096 registers ({ds['rows'][-1]['hb']} bytes) counted them to within {ds['rows'][-1]['hll']}%."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A stream has the items a, a, b. With signs s(a) = +1, s(b) = −1, what is Z² and what is F₂?", "Z = 1 + 1 − 1 = 1, so Z² = 1; F₂ = 2² + 1² = 5. One copy is a poor guess; the average over random signs is exactly 5."),
            ("Why can Count-Min never report a count below the truth?", "Every occurrence of the item added 1 to each of its counters, and nothing ever subtracts."),
            ("You want ε = 0.01 and δ = 0.001. How many counters?", "w = ⌈e/0.01⌉ = 272 per row, d = ⌈ln 1000⌉ = 7 rows: 1,904 counters."),
            ("HyperLogLog with m = 1,024 registers: roughly what error should you expect?", "1.04/√1024 = 1.04/32 ≈ 3.3%; the program measured 3.04%."),
            ("Why does a stream with every item repeated ten times give the same HyperLogLog estimate?", "Each register keeps a maximum over hashed values, and a repeat hashes to the same value."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Alon, Matias and Szegedy's paper (1996)", text="First presented at STOC in May 1996; the author's copy of the journal version.",
                 draw=C.draw_manuscript, link="https://web.math.princeton.edu/~nalon/PDFS/amsz4.pdf", link_text="The paper (PDF, Princeton)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "StreamingSketches", d["checks"],
                           "every one of 100,000 Count-Min queries, the one-pass sums against key-by-key sums, the error bands of the F₂ sketch, HyperLogLog and Flajolet–Martin over 200 hash functions, and the widget's 96 counters.",
                           ["static double hyperLogLog(int[] keys, int b, long salt)"]),
    ]
    hl = ds["rows"][-1]
    return dict(
        title="Streaming Sketches", date="1996",
        description="Era 8, topic 3 of The Algorithm Evolution Atlas: Alon, Matias and Szegedy's frequency moments (1996), with Flajolet and Martin's counting, the Count-Min sketch and HyperLogLog, measured on a stream of a million items.",
        lede="A stream that goes past once cannot be read twice, and exact counts need a counter for every item. Alon, Matias and Szegedy showed in 1996 that some questions can be answered from a few kilobytes of random summaries, with a guaranteed error, and that others cannot.",
        fieldnote=f"I let {s['m']} items flow past and kept almost nothing. {a['rows'][-1]['bytes']} bytes of signed sums told me how repetitive the stream was to within {a['rows'][-1]['err']}%; {cm['total']} counters told me how often any one key came, never too low; {hl['hb']} bytes of registers told me there were about {s['f0']} different keys, to {hl['hll']}%.",
        card=[("When", "Flajolet–Martin 1983–85; AMS 1996; Count-Min 2005; HyperLogLog 2007"),
              ("Where", "Tel Aviv, Bell Labs, AT&T; INRIA, IBM; Rutgers"),
              ("What hurt", "Exact counts need memory for every item"),
              ("The fix", "Small random summaries, updated in one pass"),
              ("Checked", f"All {cm['keys']} Count-Min queries; HyperLogLog {hl['hll']}% at m = {hl['m']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `StreamingSketches.java`.",
    )
