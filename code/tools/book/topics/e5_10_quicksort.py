"""Era 5, topic 10: Hoare's Quicksort. Every number is parsed from Quicksort.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r'words: "(.+?)" \(Hoare, recalling Moscow\) ; bound "(\w+)" ; after the first partition: \[(.*?)\] \[(.*?)\] ; sorted with (\d+) comparisons: (.*)$', ln):
            d["words"] = dict(s=m.group(1), bound=m.group(2), left=m.group(3).split(), right=m.group(4).split(), comps=m.group(5), sorted=m.group(6).split())
        elif ln.startswith("exact: "):
            d["exact"] = re.findall(r"n=(\d+): ([\d,]+) orderings, ([\d.]+)", ln)
        elif ln.startswith("random: "):
            d["rand"] = re.findall(r"([\d,]+) items: ([\d,]+) comparisons = ([\d.]+) n log2 n \(no method can use fewer than log2 n! = ([\d.]+) n log2 n", ln)
        elif ln.startswith("insertion: "):
            d["ins"] = re.findall(r"([\d,]+) items: insertion ([\d,]+) comparisons, Quicksort ([\d,]+)", ln)
        elif m := re.match(r"worst: an already sorted list of ([\d,]+) items ; .*?: ([\d,]+) comparisons, more than n\^2/2 = ([\d,]+) ; with the bound chosen at random: ([\d,]+) \(([\d.]+) n log2 n\)$", ln):
            d["worst"] = dict(n=m.group(1), first=m.group(2), half=m.group(3), rand=m.group(4), ratio=m.group(5))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def words_svg(d):
    w = d["words"]

    def draw(t, standalone):
        o = []
        words = w["s"].split()

        def row(y, items, colour_of, label):
            o.append(C.text(20, y - 8, label, t["muted"], 12))
            x = 20
            for it, col in ((it, colour_of(i, it)) for i, it in enumerate(items)):
                wd = 9 + 7.4 * len(it)
                if x + wd > 760:
                    x, y = 20, y + 34
                o.append(C.rect(x, y, wd, 26, t["wash"] if col else t["surface"], col or t["rule"], 1.4, 4))
                o.append(C.text(x + wd / 2, y + 17, it, t["ink"], 12, "middle", 700 if it == w["bound"] else 400))
                x += wd + 5
            return y + 34
        y = row(40, words, lambda i, it: t["red"] if i == 0 else None, f"The words of Hoare's sentence; the first, \"{w['bound']}\", is the bound")
        y = row(y + 32, w["left"] + w["right"], lambda i, it: t["blue"] if i < len(w["left"]) else t["yellow"],
                "After one partition: blue words come before the bound alphabetically, yellow words do not")
        o.append(C.text(20, y + 18, f"Each part is then sorted the same way: {w['comps']} comparisons in all.", t["muted"], 12))
        return C.svg_doc(780, y + 32, "".join(o), "The first partition of the words of Hoare's sentence", t, standalone, 0.55, 780)
    return draw


QS_HTML = """
<div class="board qs-board">
  <div style="min-width:0">
    <div class="qs-bars" id="qs-bars"></div>
    <div class="qs-btns"><button type="button" id="qs-step">Step</button><button type="button" id="qs-run">Run to the end</button>
      <button type="button" id="qs-shuf">Shuffle</button><button type="button" id="qs-sorted">Sorted input</button></div>
    <div class="qs-mode" id="qs-mode"></div>
  </div>
  <div style="min-width:0">
    <div class="qs-stats" id="qs-stats"></div>
    <p class="say" id="qs-say" aria-live="polite"></p>
  </div>
</div>
"""

QS_CSS = """
.qs-bars{display:flex;align-items:flex-end;gap:2px;height:180px;padding:4px;border:1px solid var(--rule);border-radius:6px;background:var(--surface)}
.qs-bars span{flex:1 1 0;min-width:0;background:var(--axis);border-radius:2px 2px 0 0}
.qs-bars span.bound{background:var(--red)}
.qs-bars span.i{background:var(--blue)}
.qs-bars span.j{background:var(--yellow)}
.qs-bars span.done{opacity:.45}
.qs-bars span.out{opacity:.25}
.qs-btns,.qs-mode{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.qs-mode button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.qs-stats{font:13px var(--mono);display:grid;gap:4px}
"""

QS_JS = r"""
(() => {
  const bars = document.getElementById("qs-bars");
  if (!bars) return;
  const N = 32;
  let a, stack, cur, comps, swaps, randomBound = false, seed = 1959, state, msg;
  const rnd = k => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 2147483648 * k); };
  function load(kind) {
    a = Array.from({length: N}, (_, i) => i + 1);
    if (kind === "shuffle") for (let i = N - 1; i > 0; i--) { const j = rnd(i + 1); [a[i], a[j]] = [a[j], a[i]]; }
    stack = [[0, N - 1]]; cur = null; comps = 0; swaps = 0; state = "pick"; msg = "Press Step: pick a bound, then move the two fingers inward.";
  }
  // one small step of Hoare's partition, so it can be watched
  function step() {
    if (state === "pick") {
      while (stack.length && stack[stack.length - 1][0] >= stack[stack.length - 1][1]) stack.pop();
      if (!stack.length) { state = "done"; msg = `Sorted, with ${comps} comparisons.`; return; }
      const [lo, hi] = stack.pop();
      if (randomBound) { const k = lo + rnd(hi - lo + 1); [a[lo], a[k]] = [a[k], a[lo]]; }
      cur = {lo, hi, bound: a[lo], i: lo - 1, j: hi + 1, phase: "i"};
      state = "part"; msg = `Partition positions ${lo} to ${hi} around the bound ${cur.bound} (red).`; return;
    }
    if (state === "part") {
      const c = cur;
      if (c.phase === "i") { do { c.i++; comps++; } while (a[c.i] < c.bound); c.phase = "j"; msg = `Left finger (blue) stops at ${a[c.i]}, not smaller than ${c.bound}.`; return; }
      if (c.phase === "j") {
        do { c.j--; comps++; } while (c.bound < a[c.j]);
        if (c.i >= c.j) { stack.push([c.j + 1, c.hi]); stack.push([c.lo, c.j]); msg = `Right finger (yellow) stops at ${a[c.j]}. The fingers have met: everything up to position ${c.j} is no larger than everything after it. Sort the two parts.`; state = "pick"; return; }
        [a[c.i], a[c.j]] = [a[c.j], a[c.i]]; swaps++;
        c.phase = "i"; msg = `Right finger stops at ${a[c.i]}; the two items are swapped.`; return;
      }
    }
  }
  function show() {
    bars.innerHTML = "";
    const pending = new Set(); stack.forEach(([lo, hi]) => { for (let k = lo; k <= hi; k++) pending.add(k); });
    a.forEach((v, k) => {
      let cls = "";
      if (state === "part" && k >= cur.lo && k <= cur.hi) cls = v === cur.bound ? "bound" : k === cur.i ? "i" : k === cur.j ? "j" : "";
      else if (state !== "part" && !pending.has(k)) cls = "done";
      if (state === "part" && (k < cur.lo || k > cur.hi) && !pending.has(k)) cls = "done";
      const s = el("span", {class: cls}, bars); s.style.height = (v / N * 100) + "%";
    });
    const st = document.getElementById("qs-stats"); st.innerHTML = "";
    el("div", {}, st).textContent = `comparisons ${comps}`;
    el("div", {}, st).textContent = `swaps ${swaps}`;
    el("div", {}, st).textContent = `pieces waiting ${stack.length}`;
    document.getElementById("qs-say").textContent = msg;
  }
  const mode = document.getElementById("qs-mode");
  [["first item as the bound", false], ["bound chosen at random", true]].forEach(([label, r]) => {
    const b = el("button", {type: "button", "aria-pressed": String(r === randomBound)}, mode); b.textContent = label;
    b.addEventListener("click", () => { randomBound = r; mode.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); });
  });
  document.getElementById("qs-step").addEventListener("click", () => { if (state !== "done") step(); show(); });
  document.getElementById("qs-run").addEventListener("click", () => { let k = 0; while (state !== "done" && k++ < 100000) step(); show(); });
  document.getElementById("qs-shuf").addEventListener("click", () => { load("shuffle"); show(); });
  document.getElementById("qs-sorted").addEventListener("click", () => { load("sorted"); msg = "Already sorted. With the first item as the bound, each partition peels off one item; try Run to the end with each kind of bound."; show(); });
  load("shuffle"); show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Quicksort combined older ideas, and where it led")
    W = 210
    nodes = {
        "ins": (20, 20, "Insertion sort", "Hoare's first idea: too slow", "about n²/4 comparisons", "ink"),
        "mrg": (395, 20, "Merge sort", "divide, sort the halves, merge", "Era 4 topic 9", "ink"),
        "rec": (770, 20, "Recursion", "a procedure that calls itself", "ALGOL, 1960", "ink"),
        "qs": (395, 170, "Quicksort", "⊕ divide by a bound, in place, from both ends", "Hoare, 1959–1962", "red"),
        "sel": (20, 330, "Sort, then look up", "sorted words meet the dictionary in order", "machine translation", "ink"),
        "rnd": (395, 330, "A random bound", "makes the bad case vanishingly rare", "", "ink"),
        "heap": (770, 330, "Heapsort", "n log n on every input", "topic 12, 1964", "ink"),
        "today": (395, 480, "Sorting today", "library sorts built around partitioning", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("ins", "qs", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("mrg", "qs", ports=("bottom", "top"))
    D.edge("rec", "qs", ports=("bottom", "top:0.85"))
    D.edge("qs", "sel", ports=("bottom:0.1", "top:0.7"))
    D.edge("qs", "rnd", ports=("bottom", "top"))
    D.edge("qs", "heap", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("rnd", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: a contrast, not a descent. Insertion sort was what Quicksort replaced; heapsort answered Quicksort's bad case.", "caption")
    return D


def chain(d):
    ins, w = d["ins"], d["worst"]
    steps = [
        (f"Sorting the words before looking them up: insertion sort needs about n²/4 comparisons ({ins[-1][1]} for {ins[-1][0]} items)",
         f"Partition around one word and sort each side: {ins[-1][2]} comparisons", "Hoare, Moscow, 1959"),
        ("The pieces still to be sorted were hard to keep track of in Mercury Autocode",
         "ALGOL's recursion: the procedure sorts each part by calling itself", "Algorithm 64, CACM 1961"),
        (f"A sorted list with the first item as the bound: {w['first']} comparisons for {w['n']} items",
         f"Choose the bound at random: {w['rand']}", "a fix, not a guarantee"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from insertion to partition")
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
    w, ex, rd, ins, wo = d["words"], d["exact"], d["rand"], d["ins"], d["worst"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Merge sort (Era 4) divided a list into halves, sorted them, and merged, but merging needs a second list as large as the first. Hoare divided differently: around one item, the bound, swapping items between the two ends of the list itself. Recursion, from ALGOL, made the rest a few lines. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Quicksort. Blue: sorting today."),
        ]),
        dict(id="part", eyebrow="Try it", title="Watch the two fingers", toc="Try it", blocks=[
            dict(type="p", text="Thirty-two bars. Step through Hoare's partition: the bound is red; the left finger (blue) moves right until it finds a bar not shorter than the bound, the right finger (yellow) moves left until it finds one not taller; the two are swapped, and so on until the fingers meet. Then each part is sorted the same way. Try a sorted input with each kind of bound, and compare the comparisons."),
            dict(type="widget", html=QS_HTML, js=QS_JS, css=QS_CSS,
                 fallback=dict(type="svg", name="words", draw=words_svg(d), alt="The first partition of the words of Hoare's sentence", width=780),
                 note="In the interactive edition you can step through the partition on 32 bars."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Partition, then do it again", toc="How it works", blocks=[
            dict(type="p", text=f"**Hoare's own sentence.** He recalled that \"it paid to sort the words of the sentence into the same alphabetical order before consulting the dictionary\". The program sorts that very sentence. The first word, \"{w['bound']}\", is the bound; after one partition the words [{' '.join(w['left'])}] come before it, and [{' '.join(w['right'])}] do not. Each part is sorted the same way: {w['comps']} comparisons in all, ending {' '.join(w['sorted'])}."),
            dict(type="p", text="**Why it is fast.** A partition looks at each item about once. If the bound splits the list roughly in half each time, there are about log₂ n levels of halving, so the work is about n log n comparisons. If every bound is the smallest item, each partition peels off one item and the work is about n²/2."),
            dict(type="table", head=["Items", "Orderings (all tried)", "Average comparisons"], num=[0, 1, 2], rows=[list(x) for x in ex]),
            dict(type="p", text="Sorting every ordering of up to 9 items, with each item compared with the bound once per partition: each average equals 2(n+1)(1 + 1/2 + … + 1/n) − 4n exactly, which grows like 2n ln n ≈ 1.39 n log₂ n."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Split the list in place around one item, so that everything on the left is no larger than everything on the right; then the two parts can be sorted separately, and nothing ever has to be merged."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Large lists, bad lists", toc="Measured", blocks=[
            dict(type="table", head=["Items (random order)", "Comparisons", "× n log₂ n", "Lower bound log₂ n! (× n log₂ n)"], num=[0, 1, 2, 3], rows=[list(x) for x in rd]),
            dict(type="p", text="The two-finger partition keeps the bound inside one of the parts and compares the items where the fingers meet twice, so it needs somewhat more than the 1.39 n log₂ n of the exact count above. No method that compares items can sort every list with fewer than log₂ n! comparisons."),
            dict(type="table", head=["Items", "Insertion sort (Hoare's first idea)", "Quicksort"], num=[0, 1, 2], rows=[list(x) for x in ins], hl=len(ins) - 1),
            dict(type="p", text=f"**The bad case.** An already sorted list of {wo['n']} items, with the first item as the bound: {wo['first']} comparisons, more than n²/2 = {wo['half']}. With the bound chosen at random, the same list takes {wo['rand']} ({wo['ratio']} n log₂ n)."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Moscow, a dictionary, and a sixpence", toc="The evidence", blocks=[
            dict(type="p", text="\"The quicksort algorithm was developed in 1959 by Tony Hoare while he was a visiting student at Moscow State University\", on a machine translation project for the National Physical Laboratory; his first idea, insertion sort, was too slow; he wrote the partition in Mercury Autocode but \"had trouble dealing with the list of unsorted segments\"; \"Later, Hoare learned about ALGOL and its ability to do recursion\". Back in England, asked to write Shellsort, he said he knew a faster algorithm, and \"his boss bet a sixpence that he did not\" (Wikipedia). The algorithms appeared as \"Algorithm 63: partition and Algorithm 64: Quicksort\" in *Communications of the ACM* in July 1961, and the analysis in *The Computer Journal* 5(1): 10–15 (1962)."),
            dict(type="p", text="Hoare, interviewed in 2006: \"I thought of Quicksort as the second thing. It didn't occur to me that this was anything very difficult\"; \"I think Quicksort is the only really interesting algorithm that I ever developed.\" He died on 5 March 2026, at the age of 92 (Wolfson College, Oxford; Computer History Museum)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The second thing he thought of", toc="Full circle", blocks=[
            dict(type="p", text="Hoare called Quicksort the second thing he thought of, after insertion sort, and the only really interesting algorithm he ever developed. The bad case he analysed is why a careful implementation chooses its bound at random or with care, and why heapsort (topic 12) was welcome two years later."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The sentence Hoare used to explain why he needed a sort, sorted by his own method: {w['comps']} comparisons."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Partition 5 3 8 1 9 2 around the bound 5 with two fingers. What happens first?", "The left finger stops at 5 itself (not smaller), the right finger at 2 (not larger): swap them, giving 2 3 8 1 9 5, and continue."),
            ("Why does a bound that splits the list in half give about n log₂ n comparisons?", "Each level of splitting looks at all n items once, and halving reaches single items after about log₂ n levels."),
            ("What does a sorted list do to Quicksort with the first item as the bound?", "Every partition splits off just the bound itself; there are n levels, and the work is about n²/2."),
            ("Why does a random bound help?", "No particular input is bad any more; a bad run needs bad luck at many levels, which is vanishingly rare."),
            ("What does Quicksort need that merge sort does not, and the other way round?", "Quicksort needs no second list, but it has a bad case; merge sort is n log n always, but needs room for a copy."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Quicksort (1962)", text="Hoare's paper in The Computer Journal 5(1): 10–15, with the analysis.",
                 draw=C.draw_manuscript, link="https://www.cs.ox.ac.uk/publications/publication8195-abstract.html", link_text="Oxford record", licence="Drawn placeholder."),
            dict(title="Oral history of Sir Antony Hoare (2006)", text="Interviewed by Jonathan P. Bowen for the Computer History Museum.",
                 draw=C.draw_book, link="https://www.computerhistory.org/collections/catalog/102658017", link_text="CHM catalogue", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Quicksort", d["checks"],
                           f"Hoare's sentence sorted, every ordering of up to 9 items against the exact formula, random lists up to a million items, insertion sort, and the sorted-input worst case with both kinds of bound.",
                           ["static <T extends Comparable<T>> int partition(T[] a, int lo, int hi)"]),
    ]
    return dict(
        title="Hoare's Quicksort", date="1959–1962",
        description="Era 5, topic 10 of The Algorithm Evolution Atlas: Hoare's Quicksort, invented in Moscow in 1959 to sort words before a dictionary look-up, with its exact average and its bad case.",
        lede="A visiting student in Moscow needed to sort the words of Russian sentences before looking them up. His first idea was too slow; his second was to split the list around one word, in place, and sort each side the same way.",
        fieldnote=f"I sorted the sentence in which Hoare explained why he needed a sort: {w['comps']} comparisons. On a million random items his method needed {rd[-1][1]}; on 50,000, insertion sort needed {ins[-1][1]}. He called it the second thing he thought of. He died in March 2026, sixty-seven years after Moscow.",
        card=[("When", "Moscow 1959; CACM 1961; paper 1962"),
              ("Where", "Moscow State University; Elliott Brothers"),
              ("What hurt", "Insertion sort's n² comparisons; merging needs a copy"),
              ("The fix", "Partition around a bound, in place; recurse"),
              ("Cost", f"About {rd[-1][2]} n log₂ n here; n²/2 in the bad case")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Quicksort.java`.",
    )
