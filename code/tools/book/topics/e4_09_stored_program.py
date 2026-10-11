"""Era 4, topic 9: the stored program, and merge sort. Every number is parsed from StoredProgram.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"baby: highest proper factor of 2\^18 = (\d+) by repeated subtraction: (\d+) ; a program of (\d+) instructions and (\d+) words of data in a store of (\d+) words ; (\d+) instructions executed$", ln):
            d["baby"] = dict(N=int(m.group(1)), ans=int(m.group(2)), ins=int(m.group(3)), data=int(m.group(4)), store=int(m.group(5)), steps=int(m.group(6)))
        elif m := re.match(r"merge: runs \[(.+?)\] and \[(.+?)\] ; merged by a program of (\d+) instructions into \[(.+?)\] ; (\d+) instructions executed ; instruction words rewritten as it ran: LA (.+?) -> (.+?), LB (.+?) -> (.+?), SC (.+?) -> (.+)$", ln):
            g = m.groups()
            d["merge"] = dict(A=[int(x) for x in g[0].split(", ")], B=[int(x) for x in g[1].split(", ")], ins=int(g[2]), out=g[3], steps=int(g[4]),
                              la=(g[5], g[6]), lb=(g[7], g[8]), sc=(g[9], g[10]))
        elif m := re.match(r"worst: .*?: ([\d, ]+) ; the formula .*? gives ([\d, ]+) ; .*? = ([\d, ]+)$", ln):
            d["worst"] = dict(w=m.group(1).split(", "), f=m.group(2).split(", "), lb=m.group(3).split(", "))
        elif ln.startswith("scale: "):
            d["scale"] = [dict(n=int(a), cmp=int(b), nlogn=int(c), shifts=int(e)) for a, b, c, e in
                          re.findall(r"n = (\d+): merge sort (\d+) comparisons \(n log2 n = (\d+)\), insertion sort (\d+) shifts", ln)]
    d["checks"] = C.checks(text)
    return d


def program_lines(java, name, N):
    """The assembly lines of a program, read from the Java source (so the page shows exactly what ran)."""
    if name == "factor":
        body = re.search(r"String\[\] factor = \{(.*?)\};", java, re.S).group(1)
    else:
        body = re.search(r"mp = new ArrayList<>\(List\.of\((.*?)\)\);", java, re.S).group(1)
    out = []
    for m in re.finditer(r'"([^"]*)"(\s*\+\s*N)?', body):
        out.append(m.group(1) + (str(N) if m.group(2) else ""))
    return out


# ----------------------------------------------------------------------------------------------------------------------
SP_HTML = """
<div class="board sp-board">
  <div style="min-width:0">
    <div class="presets" id="sp-pre"></div>
    <div class="controls" id="sp-nrow"><label for="sp-n">Find the highest proper factor of <input id="sp-n" type="number" min="4" max="1000000" value="60"></label></div>
    <div class="controls">
      <button class="primary" id="sp-step">One instruction</button>
      <button id="sp-run">Run to STP</button>
      <button id="sp-reset">Reload</button>
    </div>
    <div class="sp-regs" id="sp-regs"></div>
    <p class="say" id="sp-say" aria-live="polite"></p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The store: instructions and numbers in the same words</div>
    <ol class="sp-store" id="sp-store" start="0"></ol>
  </div>
</div>
"""

SP_CSS = """
.sp-board input[type=number]{width:7em}
.sp-regs{font:13px var(--mono);display:grid;gap:3px;margin:8px 0}
.sp-store{font:12.5px var(--mono);max-height:430px;overflow:auto;margin:6px 0;padding-left:3.2em;border:1px solid var(--axis);background:var(--surface)}
.sp-store li{padding:1px 6px;white-space:nowrap}
.sp-store li.now{background:color-mix(in srgb,var(--yellow) 45%,transparent)}
.sp-store li.changed{color:var(--red);font-weight:600}
.sp-store .lab{color:var(--blue);display:inline-block;min-width:5.5em}
"""

SP_JS_TEMPLATE = r"""
(() => {
  const storeEl = document.getElementById("sp-store");
  if (!storeEl) return;
  const FACTOR = __FACTOR__, MERGE = __MERGE__, RUNS = __RUNS__;
  const OPS = ["JMP", "JRP", "LDN", "STO", "SUB", "SUB", "CMP", "STP"];
  function assemble(lines, size) {
    const lab = {}, mem = new Array(size).fill(0), name = {};
    lines.forEach((l, a) => { const i = l.indexOf(":"); if (i >= 0) { lab[l.slice(0, i).trim()] = a; name[a] = l.slice(0, i).trim(); } });
    const ev = e => { let t = 0, s = 1, tok = "", i = 0; if (e[0] === "-") { s = -1; i = 1; }
      for (; i <= e.length; i++) { if (i === e.length || e[i] === "+" || e[i] === "-") { t += s * (/^\d+$/.test(tok) ? +tok : lab[tok]); if (i < e.length) s = e[i] === "+" ? 1 : -1; tok = ""; } else tok += e[i]; }
      return t; };
    lines.forEach((l, a) => {
      let x = l.includes(":") ? l.slice(l.indexOf(":") + 1).trim() : l.trim();
      const p = x.split(/\s+/);
      mem[a] = p[0] === "NUM" ? ev(p[1]) : OPS.indexOf(p[0]) * 8192 + (p.length > 1 ? ev(p[1]) : 0);
    });
    return {mem, lab, name, code: new Set(lines.map((l, a) => (/\b(NUM)\b/.test(l) ? -1 : a)).filter(a => a > 0))};
  }
  const word = w => { const f = (w >>> 13) & 7; return OPS[f] + (f === 6 || f === 7 ? "" : " " + (w & 8191)); };
  let P, mem, orig, acc, ci, executed, stopped, mode = "factor", shown;
  function load() {
    if (mode === "factor") {
      const N = Math.max(4, Math.min(1000000, Math.round(+document.getElementById("sp-n").value || 60)));
      P = assemble(FACTOR.map(l => l.replace("__N__", N)), 32); shown = 32;
    } else {
      const lines = MERGE.slice();
      RUNS.A.concat([1000000]).forEach((v, i) => lines.push((i ? "" : "A0: ") + "NUM " + v));
      RUNS.B.concat([1000000]).forEach((v, i) => lines.push((i ? "" : "B0: ") + "NUM " + v));
      for (let i = 0; i < 16; i++) lines.push((i ? "" : "C0: ") + "NUM 0");
      P = assemble(lines, 256); shown = lines.length;
    }
    mem = P.mem.slice(); orig = P.mem.slice(); acc = 0; ci = 0; executed = 0; stopped = false; show();
  }
  function step() {
    if (stopped) return false;
    ci++; const w = mem[ci], f = (w >>> 13) & 7, s = w & 8191; executed++;
    if (f === 0) ci = mem[s]; else if (f === 1) ci += mem[s]; else if (f === 2) acc = -mem[s]; else if (f === 3) mem[s] = acc;
    else if (f === 4 || f === 5) acc -= mem[s]; else if (f === 6) { if (acc < 0) ci++; } else { stopped = true; return false; }
    return true;
  }
  function show() {
    storeEl.innerHTML = "";
    for (let a = 0; a < shown; a++) {
      const isCode = P.code.has(a);
      const li = el("li", {class: (a === ci + 1 && !stopped ? "now " : "") + (mem[a] !== orig[a] && isCode ? "changed" : "")}, storeEl);
      el("span", {class: "lab"}, li, P.name[a] ? P.name[a] : "");
      li.appendChild(document.createTextNode(isCode ? word(mem[a]) : String(mem[a])));
    }
    const nx = storeEl.querySelector("li.now"); if (nx) nx.scrollIntoView({block: "nearest"});
    document.getElementById("sp-regs").innerHTML = `<div>accumulator <b>${acc}</b></div><div>next instruction at <b>${ci + 1}</b></div><div>instructions executed <b>${fmt(executed)}</b></div>`;
    const say = document.getElementById("sp-say");
    if (!stopped) say.textContent = mode === "factor" ? "Word b holds the divisor being tried; it counts down from the number until one divides it." : "Watch LB, LA and SC (in red once changed): the program adds 1 to the address inside them.";
    else if (mode === "factor") say.textContent = `Stopped. Word b holds the highest proper factor: ${mem[P.lab.b]}.`;
    else say.textContent = `Stopped after ${fmt(executed)} instructions; C0 onward holds the merged list. The program found the same: __MSTEPS__ instructions.`;
  }
  const pre = document.getElementById("sp-pre");
  [["Highest factor (32 words)", "factor"], ["Merge that rewrites itself", "merge"]].forEach(([n, m]) => {
    const b = el("button", {type: "button"}, pre, n);
    b.addEventListener("click", () => { mode = m; document.getElementById("sp-nrow").style.display = m === "factor" ? "" : "none"; load(); });
  });
  document.getElementById("sp-step").addEventListener("click", () => { step(); show(); });
  document.getElementById("sp-run").addEventListener("click", () => { let k = 0; while (k++ < 5e7 && step()); show(); });
  document.getElementById("sp-reset").addEventListener("click", load);
  document.getElementById("sp-n").addEventListener("change", load);
  load();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the stored program and merge sort combined older ideas, and where they led")
    W = 210
    nodes = {
        "tm": (20, 20, "The universal machine", "a table given as data", "topic 7", "ink"),
        "eniac": (395, 20, "Electronic speed", "thousands of operations a second", "the ENIAC years", "ink"),
        "cards": (770, 20, "Punched-card sorting", "one column at a time", "Era 3 topic 13", "ink"),
        "sp": (395, 170, "The stored program", "⊕ orders kept in memory as numbers", "EDVAC report, 1945", "red"),
        "self": (20, 330, "Programs that change themselves", "adding 1 to an address", "1945–1948", "ink"),
        "ms": (395, 330, "Merge sort", "merge sorted runs: n log₂ n", "von Neumann, 1945", "ink"),
        "baby": (770, 330, "The Baby runs", "the first stored program", "21 June 1948", "ink"),
        "today": (395, 480, "Every computer since", "programs as data; sorting files too big for memory", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("tm", "sp", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("eniac", "sp", ports=("bottom", "top"))
    D.edge("cards", "ms", ports=("bottom", "right:0.3"), dashed=True)
    D.edge("sp", "self", ports=("bottom:0.1", "top:0.7"))
    D.edge("sp", "ms", ports=("bottom", "top"))
    D.edge("sp", "baby", ports=("bottom:0.9", "top:0.3"))
    D.edge("ms", "today", ports=("bottom", "top"))
    D.edge("baby", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: Turing's influence on the 1945 report is not settled in the sources opened; card sorting is the job merge sort was written to beat.", "caption")
    return D


def chain(d):
    mg, sc, b = d["merge"], d["scale"][-1], d["baby"]
    steps = [
        ("A machine set up for each problem by cables and switches",
         "Keep the orders in memory, as numbers, beside the data", "EDVAC report, 1945"),
        ("No index registers: how does a program walk along a list?",
         f"Do arithmetic on its own instructions: {mg['la'][0]} becomes {mg['la'][1]}", "von Neumann's merging program, 1945"),
        ("Sorting on punched-card machines, one column at a time",
         f"Merge sorted runs: {sc['cmp']:,} comparisons for {sc['n']:,} items", "merge sort, 1945"),
        ("A design on paper is not a working machine",
         f"The Baby runs a stored program; here, {b['steps']:,} instructions", "Manchester, 21 June 1948"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from rewiring to stored programs")
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
    b, mg, w, sc = d["baby"], d["merge"], d["worst"], d["scale"]
    factor = program_lines(ctx["java"], "factor", "__N__")
    merge = program_lines(ctx["java"], "mp", "")
    js = (SP_JS_TEMPLATE.replace("__FACTOR__", json.dumps(factor)).replace("__MERGE__", json.dumps(merge))
          .replace("__RUNS__", json.dumps(dict(A=mg["A"], B=mg["B"]))).replace("__MSTEPS__", f"{mg['steps']:,}"))
    listing = [[str(a), (ln.split(":")[0] if ":" in ln else ""), (ln.split(":", 1)[1].strip() if ":" in ln else ln).replace("__N__", str(b["N"]))]
               for a, ln in enumerate(factor)]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Turing's universal machine (topic 7) read its instructions from its tape; the wartime electronic machines were fast but were set up for each problem by hand. The 1945 design report put the two together: instructions in the same fast memory as the numbers. To show that such a machine could do clerical work, not just arithmetic, von Neumann wrote out a program for merging sorted files. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the stored-program design of 1945. Blue: every computer since."),
        ]),
        dict(id="machine", eyebrow="Try it", title="Run a program that lives in its own data", toc="Try it", blocks=[
            dict(type="p", text=f"The store on the right holds the program and its numbers side by side, in the Baby's seven instructions. The first program finds the highest proper factor of a number by repeated subtraction, the task of the Baby's first run; set the number to 262144 (2¹⁸) and run it: it executes {b['steps']:,} instructions, as in the program. The second merges two sorted lists, and adds 1 to the addresses inside its own instructions LA, LB and SC as it goes (they turn red)."),
            dict(type="widget", html=SP_HTML, js=js, css=SP_CSS,
                 fallback=dict(type="table", head=["Word", "Label", "Contents"], num=[0], rows=listing),
                 note="In the interactive edition you can run both programs one instruction at a time and watch the store change."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Instructions are numbers", toc="How it works", blocks=[
            dict(type="p", text="**The machine.** The Baby had 32 words of store, an accumulator and seven instructions: JMP and JRP (jump to an address held in a word, or forward by a number held in one), LDN (load minus a word), STO (store), SUB (subtract), CMP (skip the next instruction if the accumulator is negative) and STP (stop). There is no add: x + 1 is −(−x − 1). Each instruction is a single word: a function number times 8,192, plus an address."),
            dict(type="p", text=f"**A program in 32 words.** The program's own version of the Baby's first task uses {b['ins']} instructions and {b['data']} words of data: it tries divisors from {b['N'] - 1:,} downward and divides by repeated subtraction. It stops with {b['ans']:,} after {b['steps']:,} instructions. (Kilburn's program of 21 June 1948 had 17 instructions and took about 3.5 million operations; this one is not his, so the counts differ.)"),
            dict(type="p", text=f"**A program that rewrites itself.** With no index registers, a program steps through a list by changing the address inside an instruction. The merging program ({mg['ins']} instructions) loads the front of each run with instructions LA and LB and writes with SC; after each move it adds 1 to the instruction it used. Merging {mg['A']} with {mg['B']} took {mg['steps']} instructions, and afterwards LA had become {mg['la'][1]} (from {mg['la'][0]}), LB {mg['lb'][1]} (from {mg['lb'][0]}) and SC {mg['sc'][1]} (from {mg['sc'][0]}). A large sentinel at the end of each run saves testing which run is empty, and equal keys are taken from the first run, so the merge is stable."),
            dict(type="p", text="**Merge sort.** Merging two sorted runs of total length n takes at most n − 1 comparisons. Sorting merges runs of 1 into runs of 2, then 4, then 8: about log₂ n rounds of about n comparisons. The program checks the exact worst case over every permutation of up to 8 items:"),
            dict(type="table", head=["Items n", "Merge sort, worst case (all permutations)", "n⌈lg n⌉ − 2^⌈lg n⌉ + 1", "Lower bound ⌈lg n!⌉ for any comparison sort"], num=[0, 1, 2, 3],
                 rows=[[str(i + 1), w["w"][i], w["f"][i], w["lb"][i]] for i in range(len(w["w"]))]),
            dict(type="callout", kind="key", label="Key idea",
                 text="Keep the program in memory as numbers, and the machine can load it, change it and run it like data. And sort by merging: combining two sorted lists costs one comparison per item, so halving and merging costs about n log₂ n."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Merging against inserting", toc="Measured", blocks=[
            dict(type="table", head=["Random items", "Merge sort comparisons", "n log₂ n", "Insertion sort shifts"], num=[0, 1, 2, 3],
                 rows=[[f"{x['n']:,}", f"{x['cmp']:,}", f"{x['nlogn']:,}", f"{x['shifts']:,}"] for x in sc]),
            dict(type="p", text="Insertion sort moves each item past every larger item before it, about n²/4 moves on random data; merge sort's comparisons stay just under n log₂ n. For a million items that is the difference between a quarter of a trillion steps and under twenty million. The program counts insertion sort's moves directly up to 10,000 items and, beyond that, as the number of out-of-order pairs, which merge sort counts as it merges."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A report, a manuscript and a small machine", toc="The evidence", blocks=[
            dict(type="p", text="The \"First Draft of a Report on the EDVAC\" is dated 30 June 1945 and describes \"a uniform memory containing both numbers (data) and orders (instructions)\"; that it bears only von Neumann's name is **disputed** as credit, since Eckert and Mauchly designed the machine, and the report's circulation made the EDVAC patent unenforceable (Wikipedia). Knuth calls von Neumann's handwritten merging program \"probably the earliest extant program for a stored program digital computer\"; its aim was \"to formulate code instructions for sorting and for meshing\", and the planned machine would be \"definitely faster than\" IBM's card sorters (Knuth, *Computing Surveys*, 1970)."),
            dict(type="p", text="The Manchester Baby \"ran its first program on 21 June 1948\": Kilburn's 17 instructions searched for the highest proper factor of 2¹⁸ by repeated subtraction, in 52 minutes and about 3.5 million operations, on 32 words of 32 bits (Wikipedia). Merge sort \"was invented by John von Neumann in 1945\" and analysed by Goldstine and von Neumann in 1948 (Wikipedia)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Programs as data, sorting as merging", toc="Full circle", blocks=[
            dict(type="p", text="Every computer since keeps programs in memory as numbers; loading an app is copying numbers into memory and jumping to them. Later machines added index registers, so programs no longer had to rewrite themselves, but the principle stayed: a program is data. Merge sort, meanwhile, is still how files too large for memory are sorted: sort pieces that fit, then merge them."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"A million random items: {sc[-1]['cmp']:,} comparisons by merging, {sc[-1]['shifts']:,} moves by insertion. The argument von Neumann made in 1945, that the new machine could out-sort the card machines, rests on that gap."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("The Baby has no add instruction. How do you compute x + 1?", "LDN x gives −x; SUB one gives −x − 1; store it and LDN it again: −(−x − 1) = x + 1."),
            ("Why does adding 1 to the word holding LDN 100 give LDN 101?", "An instruction is a number: function × 8192 + address. Adding 1 adds 1 to the address part."),
            ("Merge [2, 5, 9] and [3, 4, 10]. How many comparisons?", "2–3, 5–3, 5–4, 5–10, 9–10: five comparisons, then 10 is copied. At most n − 1 = 5 for six items."),
            ("Why is merge sort's worst case for 8 items 17 comparisons?", "Four merges of 1 + 1 (1 each), two of 2 + 2 (up to 3 each), one of 4 + 4 (up to 7): 4 + 6 + 7 = 17."),
            ("Can any sort by comparisons do 8 items in fewer than 16 comparisons in the worst case?", "No: there are 8! = 40,320 orders, and 15 yes-or-no answers can tell apart at most 2¹⁵ = 32,768 of them."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="First Draft of a Report on the EDVAC (1945)", text="The design report: CA, CC, M, I and O, and orders stored as numbers.",
                 draw=C.draw_book, link="https://cs.carleton.edu/faculty/jondich/courses/cs207_f03/assignments/edvac.pdf", link_text="Carleton College course page", licence="Drawn placeholder."),
            dict(title="Von Neumann's First Computer Program (1970)", text="Knuth's reading of the 1945 merging manuscript, line by line.",
                 draw=C.draw_manuscript, link="https://fermatslibrary.com/s/von-neumanns-first-computer-program", link_text="Fermat's Library", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "StoredProgram", d["checks"],
                           "the factor program's answer, the merge program's output and its rewritten instructions, merge sort's worst case over every permutation of up to 8 items against the formula and the lower bound, and insertion sort's moves against the inversions counted by merge sort.",
                           ["long run(", "static void mergeSort("]),
    ]
    return dict(
        title="The Stored Program, and Merge Sort", date="1945–1948",
        description="Era 4, topic 9 of The Algorithm Evolution Atlas: instructions stored as numbers, self-modifying programs in the Baby's seven instructions, and von Neumann's merge sort.",
        lede="In 1945 a design report proposed keeping a computer's instructions in its memory, as numbers, beside the data. Programs could then be loaded and even rewritten like data, and the first program written for such a machine was a merge, the heart of merge sort.",
        fieldnote=f"An instruction is a number: function times 8,192, plus an address. My merging program adds one to its own instructions to step along the lists, and after {mg['steps']} instructions the word that said {mg['sc'][0]} says {mg['sc'][1]}. The machine cannot tell its program from its data, and that is the point.",
        card=[("When", "EDVAC report 1945; the Baby, 21 June 1948"),
              ("Where", "The EDVAC project; Manchester"),
              ("What hurt", "Machines rewired for each problem; slow card sorting"),
              ("The fix", "Orders stored as numbers; sorting by merging"),
              ("Cost", f"{sc[-1]['cmp']:,} comparisons for {sc[-1]['n']:,} items")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `StoredProgram.java`.",
    )
