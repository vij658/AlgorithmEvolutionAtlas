"""Era 5, topic 6: linked lists and garbage collection. Every number is parsed from ListsAndGarbage.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"front: ([\d,]+) items .*? linked list: ([\d,]+) cells taken from the free list and ([\d,]+) addresses written ; array: ([\d,]+) items moved", ln):
            d["front"] = dict(n=m.group(1), cells=m.group(2), writes=m.group(3), moves=m.group(4))
        elif m := re.match(r"reverse: (\(.*?\)) becomes (\(.*?\)) by turning (\d+) arrows", ln):
            d["rev"] = dict(a=m.group(1), b=m.group(2), n=m.group(3))
        elif m := re.match(r"diff: f = (.+?), stored as (\(.*?\)) ; derivatives, simplified as they are made: 1: (.*?) ; 2: (.*?) ; 3: (.*?) ; 4: (\S+) ; .*? ; ([\d,]+) cells taken in all$", ln):
            g = m.groups()
            d["diff"] = dict(f=g[0], tree=g[1], d1=g[2], d2=g[3], d3=g[4], d4=g[5], cells=g[6])
        elif m := re.match(r"gc: the same four derivatives computed (\d+) times in a memory of only (\d+) cells ; ([\d,]+) cells taken in all, ([\d,]+) times the memory ; the free list ran out ([\d,]+) times, .*? \(([\d,]+) in all\) ; .*? the smallest memory in which the work can be done at all: (\d+) cells", ln):
            g = m.groups()
            d["gc"] = dict(rounds=g[0], mem=g[1], taken=g[2], times=g[3], ran=g[4], back=g[5], least=g[6])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def cells_svg(d):
    def draw(t, standalone):
        o = []

        def cell(x, y, item, hot=False):
            col = t["red"] if hot else t["ink2"]
            s = C.rect(x, y, 44, 32, t["wash"] if hot else t["surface"], col, 1.5, 3) + C.rect(x + 44, y, 30, 32, t["surface"], col, 1.5, 3)
            s += C.text(x + 22, y + 21, item, t["ink"], 15, "middle", 700)
            return s

        def arrow(x1, y1, x2, y2, col, sw=1.6):
            import math
            a = math.atan2(y2 - y1, x2 - x1)
            bx, by = x2 - 8 * math.cos(a), y2 - 8 * math.sin(a)
            head = f"M{x2:.1f},{y2:.1f} L{bx - 4 * math.sin(a):.1f},{by + 4 * math.cos(a):.1f} L{bx + 4 * math.sin(a):.1f},{by - 4 * math.cos(a):.1f} Z"
            return C.line(x1, y1, bx, by, col, sw) + C.path(head, None, col)
        o.append(C.text(20, 22, "A list is a chain of cells: an item (car) and the address of the next cell (cdr).", t["ink"], 13, "start", 700))
        xs = [60, 190, 320, 450]
        o.append(C.text(20, 66, "head", t["muted"], 12))
        o.append(arrow(52, 62, xs[0], 62, t["ink2"]))
        for i, (x, it) in enumerate(zip(xs, "ABCD")):
            o.append(cell(x, 46, it))
            if i < 3:
                o.append(C.circle(x + 59, 62, 3, t["ink2"]))
                o.append(arrow(x + 59, 62, xs[i + 1], 62, t["ink2"]))
            else:
                o.append(C.text(x + 59, 67, "/", t["muted"], 15, "middle", 700))
        o.append(C.text(20, 116, "To insert X after B: take a free cell, point it at C, point B at it.", t["ink"], 13, "start", 700))
        o.append(C.text(20, 134, "Two addresses change; nothing moves.", t["ink"], 13, "start", 700))
        ys = 160
        for i, (x, it) in enumerate(zip(xs, "ABCD")):
            o.append(cell(x, ys, it))
        o.append(cell(255, ys + 62, "X", True))
        o.append(arrow(xs[0] + 59, ys + 16, xs[1], ys + 16, t["ink2"]))
        o.append(C.circle(xs[1] + 59, ys + 16, 3, t["red"]))
        o.append(arrow(xs[1] + 59, ys + 16, 255, ys + 74, t["red"], 1.8))
        o.append(C.circle(255 + 59, ys + 78, 3, t["red"]))
        o.append(arrow(255 + 59, ys + 78, xs[2], ys + 24, t["red"], 1.8))
        o.append(C.text(xs[2] + 37, ys - 8, "C now reached through X", t["muted"], 11, "middle"))
        o.append(arrow(xs[2] + 59, ys + 16, xs[3], ys + 16, t["ink2"]))
        o.append(C.text(xs[3] + 59, ys + 21, "/", t["muted"], 15, "middle", 700))
        o.append(C.text(20, 290, "When nothing points to a cell any more, it is garbage:", t["muted"], 12))
        o.append(C.text(20, 307, "a collector marks every cell it can reach from the program's roots and frees the rest.", t["muted"], 12))
        return C.svg_doc(600, 320, "".join(o), "A linked list of cells, and inserting a new cell by changing two addresses", t, standalone, 0.55, 600)
    return draw


GC_HTML = """
<div class="board gc-board">
  <div style="min-width:0">
    <div class="eyebrow">A memory of 16 cells</div>
    <div class="gc-mem" id="gc-mem"></div>
    <div class="gc-key"><span class="k free">free</span><span class="k a">list A</span><span class="k b">list B</span><span class="k junk">garbage</span><span class="k mark">marked</span></div>
  </div>
  <div style="min-width:0">
    <div class="gc-lists" id="gc-lists"></div>
    <div class="gc-btns">
      <button type="button" id="gc-pa">Push onto A</button><button type="button" id="gc-oa">Pop A</button>
      <button type="button" id="gc-pb">Push onto B</button><button type="button" id="gc-db">Drop list B</button>
      <button type="button" id="gc-gc">Collect garbage</button>
    </div>
    <p class="say" id="gc-say" aria-live="polite"></p>
  </div>
</div>
"""

GC_CSS = """
.gc-mem{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;margin:6px 0}
.gc-mem .c{border:2px solid var(--rule);border-radius:5px;padding:3px;font:12px var(--mono);display:grid;grid-template-columns:auto 1fr;gap:2px 4px;min-width:0}
.gc-mem .c .n{color:var(--muted);grid-column:1/3;font-size:10px}
.gc-mem .c.a{border-color:var(--red)}
.gc-mem .c.b{border-color:var(--blue)}
.gc-mem .c.junk{border-color:var(--yellow);border-style:dashed}
.gc-mem .c.mark{background:var(--wash)}
.gc-mem .c.free{opacity:.55}
.gc-key{display:flex;gap:6px;flex-wrap:wrap;font-size:12px}
.gc-key .k{border:2px solid var(--rule);border-radius:4px;padding:1px 6px}
.gc-key .k.a{border-color:var(--red)} .gc-key .k.b{border-color:var(--blue)} .gc-key .k.junk{border-color:var(--yellow);border-style:dashed} .gc-key .k.mark{background:var(--wash)} .gc-key .k.free{opacity:.55}
.gc-lists{font:13px var(--mono);display:grid;gap:4px;margin:6px 0}
.gc-btns{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
"""

GC_JS = r"""
(() => {
  const memBox = document.getElementById("gc-mem");
  if (!memBox) return;
  const N = 16;
  let car, cdr, free, A, B, marked, next = 0;
  const LET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  function reset() {
    car = Array(N + 1).fill(null); cdr = Array(N + 1).fill(0); marked = new Set();
    free = 0; for (let c = N; c >= 1; c--) { cdr[c] = free; free = c; }
    A = 0; B = 0;
  }
  const inList = h => { const s = new Set(); for (let c = h; c; c = cdr[c]) s.add(c); return s; };
  const freeSet = () => { const s = new Set(); for (let c = free; c; c = cdr[c]) s.add(c); return s; };
  function collect() {
    marked = new Set();
    for (const r of [A, B]) for (let c = r; c && !marked.has(c); c = cdr[c]) marked.add(c);
    const fs = freeSet(); let back = 0;
    for (let c = 1; c <= N; c++) if (!marked.has(c) && !fs.has(c)) { car[c] = null; cdr[c] = free; free = c; back++; }
    return back;
  }
  function cons(item, rest) {
    let msg = "";
    if (!free) { const back = collect(); msg = `The free list was empty, so the collector ran first: it marked ${marked.size} reachable cells and returned ${back}. `; if (!free) return [null, msg + "Every cell is still reachable: memory is full."]; }
    const c = free; free = cdr[c]; car[c] = item; cdr[c] = rest;
    return [c, msg];
  }
  function show(msg) {
    memBox.innerHTML = "";
    const a = inList(A), b = inList(B), fs = freeSet();
    for (let c = 1; c <= N; c++) {
      const cls = a.has(c) ? "a" : b.has(c) ? "b" : fs.has(c) ? "free" : "junk";
      const d = el("div", {class: "c " + cls + (marked.has(c) ? " mark" : "")}, memBox);
      el("span", {class: "n"}, d).textContent = "cell " + c;
      el("span", {}, d).textContent = car[c] === null ? "-" : car[c];
      el("span", {}, d).textContent = "→" + (cdr[c] || "nil");
    }
    const lists = document.getElementById("gc-lists"); lists.innerHTML = "";
    const fmt = (name, h) => { const xs = []; for (let c = h; c; c = cdr[c]) xs.push(car[c]); return `${name}: (${xs.join(" ")})  head cell ${h || "nil"}`; };
    el("div", {}, lists).textContent = fmt("A", A);
    el("div", {}, lists).textContent = fmt("B", B);
    el("div", {}, lists).textContent = `free list: ${fs.size} cell${fs.size === 1 ? "" : "s"}`;
    const junk = N - a.size - b.size - fs.size;
    document.getElementById("gc-say").textContent = msg + (junk ? ` ${junk} cell${junk === 1 ? " is" : "s are"} garbage: nothing points to ${junk === 1 ? "it" : "them"}.` : "");
  }
  document.getElementById("gc-pa").addEventListener("click", () => { marked = new Set(); const [c, m] = cons(LET[next++ % 26], A); if (c) A = c; show(m + (c ? `New cell ${c} holds ${car[c]} and points to the old head of A.` : "")); });
  document.getElementById("gc-pb").addEventListener("click", () => { marked = new Set(); const [c, m] = cons(LET[next++ % 26].toLowerCase(), B); if (c) B = c; show(m + (c ? `New cell ${c} holds ${car[c]} and points to the old head of B.` : "")); });
  document.getElementById("gc-oa").addEventListener("click", () => { marked = new Set(); if (!A) { show("A is empty."); return; } const old = A; A = cdr[A]; show(`A now starts at its second cell; cell ${old} still holds ${car[old]}, but nothing points to it.`); });
  document.getElementById("gc-db").addEventListener("click", () => { marked = new Set(); B = 0; show("The program forgets list B. Its cells are still in memory, still pointing at each other, but unreachable."); });
  document.getElementById("gc-gc").addEventListener("click", () => { const back = collect(); show(`Mark: starting from A and B, ${marked.size} cells were reached (shaded). Sweep: ${back} unmarked cell${back === 1 ? " goes" : "s go"} back on the free list.`); });
  reset();
  for (let i = 0; i < 5; i++) { const [c] = cons(LET[next++], A); A = c; }
  for (let i = 0; i < 4; i++) { const [c] = cons(LET[next++].toLowerCase(), B); B = c; }
  show("Two lists in a memory of 16 cells. Pop A or drop B to make garbage, then collect it; or keep pushing until the free list runs out.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How linked lists and garbage collection combined older ideas, and where they led")
    W = 210
    nodes = {
        "sp": (20, 20, "Addresses in memory", "a number can say where another lives", "Era 4 topic 9", "ink"),
        "luhn": (395, 20, "Luhn's chains", "records in a bucket, one after another", "topic 4, 1953", "ink"),
        "sym": (770, 20, "Programs that reason", "goals and formulas that change shape", "Logic Theorist, 1956", "ink"),
        "ipl": (395, 170, "Linked lists", "⊕ each cell holds the address of the next", "IPL, about 1956", "red"),
        "free": (20, 330, "A free list", "unused cells chained together", "IPL's H2", "ink"),
        "lisp": (395, 330, "Lisp", "two-address cells; formulas as lists", "McCarthy, 1958–1960", "ink"),
        "gc": (770, 330, "Garbage collection", "⊕ mark what is reachable, free the rest", "about 1959", "red"),
        "today": (395, 480, "Today", "automatic memory in Java, Python and more", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sp", "ipl", ports=("bottom", "top:0.15"))
    D.edge("luhn", "ipl", ports=("bottom", "top"), dashed=True)
    D.edge("sym", "ipl", ports=("bottom", "top:0.85"))
    D.edge("ipl", "free", ports=("bottom:0.1", "top:0.7"))
    D.edge("ipl", "lisp", ports=("bottom", "top"))
    D.edge("lisp", "gc", ports=("right", "left"))
    D.edge("free", "today", ports=("bottom:0.6", "left:0.5"))
    D.edge("gc", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: Luhn's 1953 memorandum suggested linked lists for chained hash tables; whether the RAND group knew of it is not recorded in the sources opened.", "caption")
    return D


def chain(d):
    f, gc = d["front"], d["gc"]
    steps = [
        (f"Fixed blocks of memory: adding {f['n']} items at the front of an array moved items {f['moves']} times",
         f"Linked cells: the same {f['n']} items cost {f['writes']} address changes", "Newell, Shaw and Simon, IPL"),
        ("Every new cell must come from somewhere, and old ones be given back",
         "A free list: unused cells chained together; take from it, return to it", "IPL's free list"),
        ("Programs drop cells without returning them, and returning them by hand is error-prone",
         f"Garbage collection: when the free list runs out, mark what is reachable and free the rest ({gc['back']} cells returned in the program's run)", "McCarthy, about 1959"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from arrays to automatic memory")
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
    f, rv, df, gc = d["front"], d["rev"], d["diff"], d["gc"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Memory addresses are numbers, so one word can say where another lives. The RAND group put that to work for programs whose data kept changing shape: every item in a small cell with the address of the next. McCarthy then let the machine itself take back the cells nobody could reach. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: linked lists and garbage collection. Blue: automatic memory today."),
        ]),
        dict(id="cells", eyebrow="Try it", title="Make garbage, then collect it", toc="Try it", blocks=[
            dict(type="p", text="Sixteen cells, each with an item and the number of the next cell (→nil ends a list). Two lists, A and B, start from the program's two roots. Pop A or drop B and some cells become garbage: still in memory, but unreachable. Collect: the page marks every cell it can reach from A and B, then sweeps the rest onto the free list. Keep pushing and the collector runs by itself when the free list is empty."),
            dict(type="widget", html=GC_HTML, js=GC_JS, css=GC_CSS,
                 fallback=dict(type="svg", name="cells", draw=cells_svg(d), alt="A linked list of cells, and inserting a new cell by changing two addresses", width=600),
                 note="In the interactive edition you can push, pop, drop and collect in a 16-cell memory."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Cells, a free list, and a collector", toc="How it works", blocks=[
            dict(type="p", text=f"**Cells.** In the program each cell has two address fields, as in Lisp: the car (the item, or another list) and the cdr (the rest of the list). Adding {f['n']} items one at a time to the front of a list took {f['cells']} cells from the free list and wrote {f['writes']} addresses; doing the same with an array moved items along {f['moves']} times. Reversing {rv['a']} needs no new cells at all: turn its {rv['n']} arrows round and it reads {rv['b']}."),
            dict(type="p", text=f"**Formulas as lists.** Because a car can hold another list, cells make trees, and a formula is a tree. The program stores f = {df['f']} as {df['tree']}, and differentiates it by building new cells: the first derivative, simplified as it is made, is {df['d1']}; the fourth is {df['d4']}. Each one was checked by evaluating it at x = −3 to 3. The four derivatives took {df['cells']} cells, and most of them were thrown away along the way."),
            dict(type="p", text=f"**Mark and sweep.** The same work was repeated {gc['rounds']} times in a memory of only {gc['mem']} cells. The program took {gc['taken']} cells in all, {gc['times']} times the size of the memory: the free list ran out {gc['ran']} times, and each time the collector marked every cell reachable from the program's roots and swept {gc['back']} unreachable cells back onto the free list in all. Every round gave the same answers, and at the end, with no roots left, all {gc['mem']} cells were free. The smallest memory in which the work can be done at all is {gc['least']} cells, about the most that are ever in use at once."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Let data point to data. A list grows, shrinks and is spliced by changing addresses, not by moving items; and since the machine can follow the addresses too, it can find out for itself which cells are still in use."),
        ]),
        dict(id="measured", eyebrow="Measured", title="What the program counted", toc="Measured", blocks=[
            dict(type="table", head=["Task", "Linked cells", "Array"], num=[],
                 rows=[[f"add {f['n']} items at the front", f"{f['writes']} addresses written", f"{f['moves']} items moved"],
                       [f"reverse {rv['a']}", f"{rv['n']} arrows turned, no new cells", "(move every item)"]]),
            dict(type="table", head=["Garbage collection run", "Value"], num=[1],
                 rows=[["memory", f"{gc['mem']} cells"], ["cells taken in all", gc["taken"]], ["times the free list ran out", gc["ran"]],
                       ["cells returned by mark and sweep", gc["back"]], ["smallest memory that works", f"{gc['least']} cells"]]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="RAND, Carnegie Tech and MIT", toc="The evidence", blocks=[
            dict(type="p", text="IPL was \"created by Allen Newell, Cliff Shaw, and Herbert A. Simon at RAND Corporation and the Carnegie Institute of Technology about 1956\"; it ran the Logic Theorist (1956) and the General Problem Solver (1957), \"introduced the concepts of symbol processing and list processing\", and kept unused cells on a free list (\"H2 is the free-list\"). \"Many of these features were generalized, rationalized, and incorporated into Lisp.\" Newell and Shaw's \"Programming the Logic Theory Machine\" (1957) has the \"now-classic diagram\" of cells joined by arrows; Newell and Simon received the 1975 Turing Award."),
            dict(type="p", text="McCarthy: \"Around 1959, he invented so-called 'garbage collection' methods\"; Lisp \"soon became the programming language of choice for AI applications after its publication in 1960\". His 1960 paper: \"When a free register is wanted, and there is none left on the free-storage list, a reclamation cycle starts\", with his later remark: \"We already called this process 'garbage collection', but I guess that I chickened out of using it in the paper\" (quoted in Cambridge lecture slides)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The collector inside this book's programs", toc="Full circle", blocks=[
            dict(type="p", text="Every program in this book is written in Java, which collects its own garbage: the topic's program simulates a Lisp memory inside a language that does the same thing for real underneath it. Luhn's chained buckets (topic 4) were linked lists before the name existed, and AVL trees (topic 11) are built from cells with two links, like Lisp's."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{gc['taken']} cells used in a memory of {gc['mem']}: each cell was used about {gc['times']} times, returned by a collector the program never had to call."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many addresses change to remove the second cell of a list?", "One: the first cell's next-address now points to the third cell."),
            ("Why is finding the 1,000th item slow in a linked list?", "There is no arithmetic for it: you must follow 999 addresses from the head. An array finds it in one step."),
            ("After 'drop list B', why are B's cells not free yet?", "Nothing has returned them; they are garbage, unreachable but not yet on the free list, until a collection runs."),
            ("Can a collector free a cell the program will still use?", "Not if it knows every root: anything the program can still reach is reachable from a root, and is marked."),
            ("Why must the program in this topic register its intermediate results as roots?", "A cell referred to only from a local variable would look unreachable, and a collection in the middle of the work would free it."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Recursive Functions of Symbolic Expressions (1960)", text="McCarthy's Lisp paper in Communications of the ACM 3(4), with the free-storage list and its reclamation cycle.",
                 draw=C.draw_manuscript, link="https://www.cl.cam.ac.uk/teaching/0708/ConceptsPL/LISP.pdf", link_text="Lecture slides quoting it", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ListsAndGarbage", d["checks"],
                           f"lists against arrays, an in-place reversal, four symbolic derivatives each checked at seven points, and {gc['rounds']} rounds of the same work in a {gc['mem']}-cell memory kept alive by mark and sweep.",
                           ["static int cons(int a, int d)", "static void gc()"]),
    ]
    return dict(
        title="Linked Lists and Garbage Collection", date="1956–1960",
        description="Era 5, topic 6 of The Algorithm Evolution Atlas: linked lists in IPL, Lisp's two-address cells, and McCarthy's garbage collection by mark and sweep.",
        lede="Programs that reason need data that changes shape. The RAND group kept each item in a cell with the address of the next; McCarthy built a language from such cells and let the machine take back the ones nobody could reach.",
        fieldnote=f"Four derivatives of a formula, computed {gc['rounds']} times in a memory of {gc['mem']} cells: {gc['taken']} cells used, each one many times over. The collector ran {gc['ran']} times and never freed a cell still in use. McCarthy, they say, did not dare print the word garbage.",
        card=[("When", "IPL about 1956; garbage collection about 1959; Lisp 1960"),
              ("Where", "RAND and Carnegie Tech; MIT"),
              ("What hurt", "Fixed memory could not grow, shrink or be spliced"),
              ("The fix", "Cells with the address of the next; mark and sweep"),
              ("Cost", "Following addresses one by one; pauses to collect")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ListsAndGarbage.java`.",
    )
