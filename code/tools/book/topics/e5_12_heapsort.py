"""Era 5, topic 12: heapsort and the heap. Every number is parsed from Heapsort.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"heap: the numbers ([\d ]+) built into a heap by Floyd's method: ([\d ]+) ; read as a tree", ln):
            d["heap"] = dict(src=m.group(1).split(), heap=m.group(2).split())
        elif ln.startswith("build: "):
            d["build"] = re.findall(r"([\d,]+) random items: Williams ([\d,]+) comparisons, Floyd ([\d,]+) \(([\d.]+) per item\) ; Williams on ascending items ([\d,]+)", ln)
        elif ln.startswith("floyd: "):
            d["floyd"] = re.findall(r"n=(\d+): (\d+)", ln)
        elif ln.startswith("sort: "):
            d["sort"] = re.findall(r"([\d,]+) (random|sorted): ([\d,]+) comparisons = ([\d.]+) n log2 n", ln)
        elif m := re.match(r"stable: cards ([\w ]+) sorted by number only ; heapsort gives ([\w ]+) ; .*?would give ([\w ]+)\)$", ln):
            d["stable"] = dict(src=m.group(1), got=m.group(2), want=m.group(3))
        elif m := re.match(r"queue: Dijkstra's method on ([\d,]+) towns with ([\d,]+) roads ; .*?: ([\d,]+) steps ; keeping set B in a heap: ([\d,]+) removals from the heap and ([\d,]+) comparisons", ln):
            d["queue"] = dict(n=m.group(1), roads=m.group(2), scan=m.group(3), rem=m.group(4), comps=m.group(5))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def heap_svg(d):
    hp = d["heap"]["heap"]

    def draw(t, standalone):
        o = []
        n = len(hp)
        o.append(C.text(20, 22, "The heap as an array: the children of position i are at 2i+1 and 2i+2", t["ink"], 13, "start", 700))
        for i, v in enumerate(hp):
            x = 20 + i * 52
            o.append(C.rect(x, 34, 46, 32, t["surface"], t["ink2"], 1.4, 4))
            o.append(C.text(x + 23, 56, v, t["ink"], 14, "middle", 700))
            o.append(C.text(x + 23, 82, str(i), t["muted"], 11, "middle"))
        pos = {}
        levels = []
        i, lvl = 0, 0
        while i < n:
            levels.append(list(range(i, min(n, 2 * i + 1))))
            i = 2 * i + 1
        for lv, idxs in enumerate(levels):
            span = 2 ** lv
            for k, i in enumerate(idxs):
                x = 40 + (k + 0.5) * (520 / span)
                pos[i] = (x, 120 + lv * 62)
        for i in range(1, n):
            (x1, y1), (x2, y2) = pos[(i - 1) // 2], pos[i]
            o.append(C.line(x1, y1, x2, y2, t["axis"], 1.5))
        for i, (x, y) in pos.items():
            o.append(C.circle(x, y, 17, t["wash"] if i == 0 else t["surface"], t["red"] if i == 0 else t["ink2"], 1.6))
            o.append(C.text(x, y + 5, hp[i], t["ink"], 13, "middle", 700))
        o.append(C.text(20, 120 + len(levels) * 62, "Every number is at least as large as the numbers below it, so the largest is at the top.", t["muted"], 12))
        return C.svg_doc(600, 120 + len(levels) * 62 + 14, "".join(o), "A heap of ten numbers, as an array and as a tree", t, standalone, 0.55, 600)
    return draw


HS_HTML = """
<div class="board hs-board">
  <div style="min-width:0">
    <div class="hs-arr" id="hs-arr"></div>
    <div class="hs-tree" id="hs-tree"></div>
  </div>
  <div style="min-width:0">
    <div class="hs-btns"><button type="button" id="hs-step">Step</button><button type="button" id="hs-run">Run to the end</button><button type="button" id="hs-new">New numbers</button></div>
    <div class="hs-stats" id="hs-stats"></div>
    <p class="say" id="hs-say" aria-live="polite"></p>
  </div>
</div>
"""

HS_CSS = """
.hs-arr{display:grid;grid-template-columns:repeat(15,minmax(0,1fr));gap:2px;font:12px var(--mono)}
.hs-arr span{border:1px solid var(--rule);border-radius:3px;text-align:center;padding:3px 0}
.hs-arr span.sorted{background:var(--blue);color:var(--on-blue);border-color:var(--blue)}
.hs-arr span.hot{background:var(--red);color:var(--on-red);border-color:var(--red)}
.hs-tree svg{display:block;width:100%;max-width:440px;height:auto;margin-top:8px}
.hs-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.hs-stats{font:13px var(--mono);display:grid;gap:3px}
"""

HS_JS = r"""
(() => {
  const arrBox = document.getElementById("hs-arr");
  if (!arrBox) return;
  const N = 15, NS = "http://www.w3.org/2000/svg";
  let a, phase, k, end, comps, hot = [], msg, seed = 1964;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return 1 + Math.floor(seed / 2147483648 * 99); };
  function fresh() { a = Array.from({length: N}, rnd); phase = "build"; k = Math.floor(N / 2) - 1; end = N; comps = 0; hot = []; msg = "Floyd's method: starting from the last parent, let each one sink below any larger child."; }
  function sink(i, n) {
    const path = [i];
    while (2 * i + 1 < n) {
      let c = 2 * i + 1;
      if (c + 1 < n) { comps++; if (a[c] < a[c + 1]) c++; }
      comps++;
      if (a[i] < a[c]) { [a[i], a[c]] = [a[c], a[i]]; i = c; path.push(i); } else break;
    }
    return path;
  }
  function step() {
    if (phase === "build") {
      const v = a[k]; hot = sink(k, N);
      msg = hot.length > 1 ? `Position ${k} (${v}) sinks to position ${hot[hot.length - 1]}.` : `Position ${k} (${v}) is already at least as large as its children.`;
      k--; if (k < 0) { phase = "sort"; msg += " The heap is built: the largest number is at the top."; }
      return;
    }
    if (phase === "sort") {
      end--; [a[0], a[end]] = [a[end], a[0]];
      const top = a[end]; hot = sink(0, end);
      msg = `The top, ${top}, is swapped to position ${end} and joins the sorted part (blue); the new top sinks back into place.`;
      if (end === 1) { phase = "done"; msg = `Sorted in place, with ${comps} comparisons.`; hot = []; }
    }
  }
  function show() {
    arrBox.innerHTML = "";
    a.forEach((v, i) => { el("span", {class: i >= end || phase === "done" ? "sorted" : hot.includes(i) ? "hot" : ""}, arrBox).textContent = v; });
    const box = document.getElementById("hs-tree"); box.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", "0 0 440 200"); box.appendChild(svg);
    const P = i => { const lv = Math.floor(Math.log2(i + 1)), first = 2 ** lv - 1, span = 2 ** lv; return [20 + (i - first + 0.5) * (400 / span), 20 + lv * 50]; };
    const live = phase === "done" ? 0 : end;
    for (let i = 1; i < live; i++) { const [x1, y1] = P((i - 1) >> 1), [x2, y2] = P(i); sv("line", {x1, y1, x2, y2, stroke: "var(--axis)", "stroke-width": 1.5}, svg); }
    for (let i = 0; i < live; i++) {
      const [x, y] = P(i);
      sv("circle", {cx: x, cy: y, r: 14, fill: hot.includes(i) ? "var(--red)" : "var(--surface)", stroke: "var(--ink2)", "stroke-width": 1.5}, svg);
      const t = sv("text", {x, y: y + 4, "text-anchor": "middle", "font-size": 11, "font-weight": 700, fill: hot.includes(i) ? "var(--on-red)" : "var(--ink)"}, svg); t.textContent = a[i];
    }
    const st = document.getElementById("hs-stats"); st.innerHTML = "";
    el("div", {}, st).textContent = `phase: ${phase === "build" ? "building the heap" : phase === "sort" ? "sorting" : "done"}`;
    el("div", {}, st).textContent = `comparisons ${comps}`;
    document.getElementById("hs-say").textContent = msg;
  }
  document.getElementById("hs-step").addEventListener("click", () => { if (phase !== "done") step(); show(); });
  document.getElementById("hs-run").addEventListener("click", () => { while (phase !== "done") step(); show(); });
  document.getElementById("hs-new").addEventListener("click", () => { fresh(); show(); });
  fresh(); show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How heapsort and the heap combined older ideas, and where they led")
    W = 210
    nodes = {
        "sel": (20, 20, "Selection sort", "take the largest, again and again", "", "ink"),
        "tree": (395, 20, "Trees", "parents and children", "topics 6 and 11", "ink"),
        "arr": (770, 20, "Arrays", "position i, by arithmetic", "", "ink"),
        "heap": (395, 170, "Heap and heapsort", "⊕ a tree in an array, parents ≥ children", "Williams, 1964", "red"),
        "fl": (20, 330, "Floyd's construction", "build the heap in under 2n comparisons", "1964", "ink"),
        "pq": (395, 330, "Priority queues", "always serve the most urgent first", "", "ink"),
        "dij": (770, 330, "Dijkstra with a heap", "the nearest of set B, quickly", "topic 7", "ink"),
        "today": (395, 480, "Today", "schedulers, event simulations, route finding", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sel", "heap", ports=("bottom", "top:0.15"))
    D.edge("tree", "heap", ports=("bottom", "top"))
    D.edge("arr", "heap", ports=("bottom", "top:0.85"))
    D.edge("heap", "fl", ports=("bottom:0.1", "top:0.7"))
    D.edge("heap", "pq", ports=("bottom", "top"))
    D.edge("pq", "dij", ports=("right", "left"))
    D.edge("pq", "today", ports=("bottom", "top"))
    D.text(20, 615, "Wikipedia: heapsort removes the largest item repeatedly \"in a similar manner to Selection sort\", and heaps \"are also crucial in several efficient graph algorithms such as Dijkstra's algorithm\".", "caption")
    return D


def chain(d):
    b, s, q = d["build"], d["sort"], d["queue"]
    steps = [
        ("Quicksort has bad cases, and merging needs a second list",
         f"Heapsort: sorted in place, about the same work on sorted input ({s[-1][3]} n log2 n) as on random ({s[-2][3]})", "Williams, 1964"),
        (f"Building the heap by insertions can cost n log n: {b[-1][4]} comparisons on ascending items",
         f"Floyd: let the lower half sink, from the back: {b[-1][3]} comparisons per item", "Floyd, 1964"),
        (f"Finding the most urgent item by scanning: {q['scan']} steps for Dijkstra on {q['n']} towns",
         f"Keep them in a heap: {q['comps']} comparisons", "the heap as a priority queue"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from bad cases to a guaranteed sort")
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
    h, b, fl, s, st, q = d["heap"], d["build"], d["floyd"], d["sort"], d["stable"], d["queue"]
    fl_rows = []
    for n, worst in fl:
        n_ = int(n)
        s2, e2 = bin(n_).count("1"), (n_ & -n_).bit_length() - 1
        fl_rows.append([n, worst, f"2·{n} − 2·{s2} − {e2} = {2 * n_ - 2 * s2 - e2}"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Selection sort takes the largest item again and again, but finding it means searching everything that is left. Williams kept the remaining items in a heap, a tree packed into the array itself, so that the largest is always at the top and the tree can be repaired in a few steps. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the heap and heapsort. Blue: priority queues today."),
        ]),
        dict(id="sort", eyebrow="Try it", title="Build a heap, then take it apart", toc="Try it", blocks=[
            dict(type="p", text="Fifteen numbers in an array, drawn also as a tree (the children of position i are at 2i+1 and 2i+2). Step through Floyd's construction: each parent, from the last one back to the top, sinks below any larger child. Then the sort: swap the top with the last item of the heap, which joins the sorted part (blue), and let the new top sink."),
            dict(type="widget", html=HS_HTML, js=HS_JS, css=HS_CSS,
                 fallback=dict(type="svg", name="heap", draw=heap_svg(d), alt="A heap of ten numbers, as an array and as a tree", width=600),
                 note="In the interactive edition you can step through heapsort on fifteen numbers."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A tree with no pointers", toc="How it works", blocks=[
            dict(type="p", text=f"**The heap.** Read an array as a tree: position 0 is the top, and the children of position i sit at 2i+1 and 2i+2, so no addresses need to be stored. In a heap every item is at least as large as its children. The program built the numbers {' '.join(h['src'])} into the heap {' '.join(h['heap'])}: {h['heap'][0]} at the top."),
            dict(type="p", text="**Two repairs.** To add an item, put it at the end and let it climb past smaller parents (Williams). To remove the largest, move the last item to the top and let it sink below the larger of its children. Each repair walks one path from top to bottom, about log₂ n steps."),
            dict(type="p", text="**Heapsort.** Build a heap, then repeatedly swap the top with the last item of the heap and let the new top sink. The sorted part grows at the back of the same array, so no second list is needed."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Don't keep everything in order; keep just enough order that the largest item is always at the top. That much order costs a few steps per change, and it is all a sort, or a queue of urgent tasks, needs."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Building, sorting, queueing", toc="Measured", blocks=[
            dict(type="table", head=["Random items", "Williams's insertions", "Floyd's construction", "Floyd per item", "Williams on ascending items"], num=[0, 1, 2, 3, 4], rows=[list(x) for x in b]),
            dict(type="p", text="Floyd's construction needs fewer than two comparisons per item, because most items sit near the bottom and sink only a level or two. The program found the most comparisons it ever needs by trying every ordering of up to 10 items; each matches the formula 2n − 2s(n) − e(n), where s(n) counts the 1s of n in binary and e(n) its trailing 0s:"),
            dict(type="table", head=["n", "Most comparisons (every ordering tried)", "2n − 2s(n) − e(n)"], num=[0, 1], rows=fl_rows),
            dict(type="table", head=["Items", "Input", "Comparisons", "× n log₂ n"], num=[0, 2, 3], rows=[list(x) for x in s]),
            dict(type="p", text=f"Sorted input costs about the same as random input; Quicksort with the first item as its bound needed more than n²/2 comparisons on a sorted list (topic 10). Heapsort is not stable: cards {st['src']}, sorted by number only, come out as {st['got']}, where a stable sort would give {st['want']}."),
            dict(type="p", text=f"**The heap as a queue.** Dijkstra's method (topic 7) on {q['n']} towns with {q['roads']} roads: finding the nearest town of set B by scanning every town took {q['scan']} steps; keeping set B in a heap took {q['rem']} removals and {q['comps']} comparisons, with the same distance to every town."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two algorithms in one volume of CACM", toc="The evidence", blocks=[
            dict(type="p", text="J. W. J. Williams devised heapsort in 1964 (\"Algorithm 232 – Heapsort\", *Communications of the ACM* 7(6): 347–348); his paper also \"introduced the binary heap as a useful data structure in its own right\". In the same year Robert W. Floyd \"published an improved version that could sort an array in-place\" (\"Algorithm 245 – Treesort 3\", *CACM* 7(12): 701), with a heap construction that \"operates in O(n) time\". Heapsort is \"not a stable sort\" and needs \"2n log₂ n + O(n) comparisons worst-case and on average\"; the worst case of Floyd's construction \"is known to be equal to 2n − 2s₂(n) − e₂(n)\" (Wikipedia, Heapsort)."),
            dict(type="p", text="Williams (1930–2012) worked as a programmer for Elliot Automation, formerly Elliott Brothers, and later for English Electric and GEC, before moving to Bell-Northern Research in Ottawa in 1974. His biography dates the invention to 1963, the year before publication; the catalog marks the year as disputed."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The sort that outlived itself", toc="Full circle", blocks=[
            dict(type="p", text="\"The heap data structure, specifically the binary heap, was introduced by J. W. J. Williams in 1964, as a data structure for the heapsort sorting algorithm\" (Wikipedia). It became more useful than the sort: any program that must keep serving the most urgent of many waiting items, from Dijkstra's frontier to Huffman's \"take the two smallest\" (topic 3), uses a heap."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Dijkstra's frontier, kept in a heap: {q['comps']} comparisons instead of {q['scan']} scanning steps, and the same distances."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("In an array heap, where are the children of position 4? Its parent?", "Children at 9 and 10; parent at (4 − 1) ÷ 2 = 1 (rounding down)."),
            ("Is 9 7 8 3 6 5 a heap?", "Yes: 9 ≥ 7, 8; 7 ≥ 3, 6; 8 ≥ 5."),
            ("Why does Floyd start from the middle of the array?", "Positions after n/2 have no children: they are already heaps of one item."),
            ("Why is heapsort's bad case no worse than its average?", "Every step walks at most one path of length about log₂ n, whatever the input."),
            ("Why is heapsort not stable?", "Swapping the top to the back can jump an item past others with the same key."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Algorithm 232 – Heapsort (1964)", text="Williams's algorithm in Communications of the ACM 7(6): 347–348.",
                 draw=C.draw_manuscript, link="https://hjemmesider.diku.dk/~henglein/bib/publications/williams1964.html", link_text="Bibliographic record", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Heapsort", d["checks"],
                           f"a small heap, Williams's and Floyd's constructions, Floyd's exact worst case for every ordering of up to 10 items, heapsort on up to a million random and sorted items, stability, and Dijkstra's method with and without a heap.",
                           ["static void sink(long[] a, int i, int n)", "static void heapsort(long[] a)"]),
    ]
    return dict(
        title="Heapsort and the Heap", date="1964",
        description="Era 5, topic 12 of The Algorithm Evolution Atlas: Williams's heapsort and binary heap, Floyd's linear-time construction, and the heap as a priority queue for Dijkstra's method.",
        lede="Quicksort is fast on average and dreadful on a bad day. Williams packed a tree into the array itself, every parent at least as large as its children, and sorted with no bad days at all.",
        fieldnote=f"Floyd built a heap of a million items with {b[-1][2]} comparisons, fewer than two per item; the formula for his worst case matched every ordering I tried. The sort was the reason for the heap, but the heap outlived the sort: it is how a program keeps the most urgent of many waiting items at hand.",
        card=[("When", "Williams 1964; Floyd 1964"),
              ("Where", "Elliott Automation (Williams); CACM"),
              ("What hurt", "Quicksort's bad case; finding the largest of a changing set"),
              ("The fix", "A heap in the array; sink and climb"),
              ("Cost", f"About {s[-2][3]} n log₂ n here, whatever the input")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Heapsort.java`.",
    )
