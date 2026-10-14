"""Era 5, topic 8: the compiler, and a grammar for languages. Every number is parsed from Compiler.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"parse: (.+?) ; the grammar's structure, every operation in its own brackets: (\S.*?) ; powers first", ln):
            d["parse"] = dict(f=m.group(1), full=m.group(2))
        elif m := re.match(r"code: plain generator, (\d+) instructions: (.*?) ; careful generator, (\d+) instructions: (.*?) ; with (.*?) both give (-?\d+)$", ln):
            d["code"] = dict(np=m.group(1), plain=m.group(2).split(" ; "), ng=m.group(3), good=m.group(4).split(" ; "), vals=m.group(5), result=m.group(6))
        elif m := re.match(r"random: ([\d,]+) random formulas .*? such as (.+?) ; .*? run ([\d,]+) times .*? instructions in all: plain ([\d,]+), careful ([\d,]+) \((\d+)% fewer\)$", ln):
            d["rand"] = dict(n=m.group(1), ex=m.group(2), runs=m.group(3), plain=m.group(4), good=m.group(5), pct=m.group(6))
        elif m := re.match(r"assoc: (.+?) with (.+?) ; .*? tree: (\(.*\)) = (-?\d+), not (.+?) = (-?\d+)$", ln):
            d["assoc"] = dict(f=m.group(1), vals=m.group(2), left=m.group(3), lv=m.group(4), right=m.group(5), rv=m.group(6))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def tree_of(full: str):
    """Parse the fully bracketed form '((A + B) - C)' into nested tuples (op, left, right) or a leaf string."""
    toks = re.findall(r"\*\*|[()+\-*]|\w+", full)
    pos = [0]

    def node():
        t = toks[pos[0]]
        if t == "(":
            pos[0] += 1
            left = node()
            op = toks[pos[0]]
            pos[0] += 1
            right = node()
            pos[0] += 1                               # ')'
            return (op, left, right)
        pos[0] += 1
        return t
    return node()


def tree_svg(d):
    root = tree_of(d["parse"]["full"])

    def draw(t, standalone):
        leaves = []

        def place(n, depth):
            if isinstance(n, str):
                x = len(leaves)
                leaves.append(n)
                return dict(x=x, depth=depth, label=n, kids=[])
            l, r = place(n[1], depth + 1), place(n[2], depth + 1)
            return dict(x=(l["x"] + r["x"]) / 2, depth=depth, label=n[0], kids=[l, r])
        tr = place(root, 0)
        nl = len(leaves)
        W, dx, dy, top = 640, (640 - 80) / max(1, nl - 1), 64, 58
        maxd = [0]
        o = []

        def walk(n):
            maxd[0] = max(maxd[0], n["depth"])
            x, y = 40 + n["x"] * dx, top + n["depth"] * dy
            for k in n["kids"]:
                o.append(C.line(x, y, 40 + k["x"] * dx, top + k["depth"] * dy, t["axis"], 1.5))
                walk(k)
        walk(tr)

        def dots(n):
            x, y = 40 + n["x"] * dx, top + n["depth"] * dy
            if n["kids"]:
                o.append(C.circle(x, y, 17, t["surface"], t["red"], 1.8))
                o.append(C.text(x, y + 5, n["label"], t["red"], 15, "middle", 700))
            else:
                o.append(C.rect(x - 15, y - 14, 30, 28, t["wash"], t["ink2"], 1.4, 5))
                o.append(C.text(x, y + 5, n["label"], t["ink"], 14, "middle", 700))
            for k in n["kids"]:
                dots(k)
        dots(tr)
        o.append(C.text(20, 20, f"{d['parse']['f']}: the tree the grammar gives", t["muted"], 12))
        return C.svg_doc(W, top + maxd[0] * dy + 30, "".join(o), f"The syntax tree of {d['parse']['f']}", t, standalone, 0.55, W)
    return draw


CP_HTML = """
<div class="board cp-board">
  <div style="min-width:0">
    <label class="eyebrow" for="cp-in">A formula (letters A to H, whole numbers, + - * ** and brackets)</label>
    <input id="cp-in" type="text" value="A + B * C ** 2 - D * (E - F)" spellcheck="false" autocomplete="off">
    <div class="cp-full" id="cp-full"></div>
    <div class="cp-vals" id="cp-vals"></div>
  </div>
  <div style="min-width:0">
    <div class="cp-cols">
      <div><div class="eyebrow" id="cp-h1">plain</div><ol class="cp-code" id="cp-plain"></ol></div>
      <div><div class="eyebrow" id="cp-h2">careful</div><ol class="cp-code" id="cp-good"></ol></div>
    </div>
    <p class="say" id="cp-say" aria-live="polite"></p>
  </div>
</div>
"""

CP_CSS = """
.cp-board input{font:15px var(--mono);width:100%;box-sizing:border-box;padding:8px;margin-top:4px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink)}
.cp-full{font:13px var(--mono);margin:8px 0;overflow-wrap:anywhere}
.cp-vals{display:flex;flex-wrap:wrap;gap:6px;font:13px var(--mono)}
.cp-vals label{display:flex;gap:3px;align-items:center}
.cp-vals input{width:3.4em;padding:3px;font:13px var(--mono)}
.cp-cols{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.cp-code{margin:4px 0;padding-left:2.4em;font:12.5px var(--mono);max-height:300px;overflow-y:auto}
.cp-code li.st{color:var(--muted)}
"""

CP_JS = r"""
(() => {
  const inp = document.getElementById("cp-in");
  if (!inp) return;
  const vals = {A: 3, B: 4, C: 5, D: 6, E: 9, F: 2, G: 1, H: 7};
  const vb = document.getElementById("cp-vals");
  Object.keys(vals).forEach(k => {
    const l = el("label", {}, vb); l.append(k + "=");
    const i = el("input", {type: "number", value: vals[k]}, l);
    i.addEventListener("input", () => { vals[k] = Number(i.value) || 0; show(); });
  });
  // the grammar of the ALGOL 60 report, one procedure per rule
  function parse(s) {
    const toks = s.match(/\*\*|[()+\-*]|[A-Za-z]\w*|\d+|\S/g) || [];
    let p = 0;
    const peek = () => toks[p] || "";
    function expression() { let n = term(); while (peek() === "+" || peek() === "-") { const op = toks[p++]; n = {op, l: n, r: term()}; } return n; }
    function term() { let n = factor(); while (peek() === "*") { p++; n = {op: "*", l: n, r: factor()}; } return n; }
    function factor() { let n = primary(); while (peek() === "**") { p++; const r = primary(); if (r.leaf === undefined || !/^\d$/.test(r.leaf) || r.leaf === "0") throw "a power needs a whole number from 1 to 9"; n = {op: "**", l: n, r}; } return n; }
    function primary() {
      const t = peek();
      if (t === "(") { p++; const n = expression(); if (peek() !== ")") throw "a bracket is not closed"; p++; return n; }
      if (/^[A-H]$/.test(t) || /^\d+$/.test(t)) { p++; return {leaf: t}; }
      throw t ? `unexpected "${t}"` : "the formula ends too soon";
    }
    const n = expression();
    if (p !== toks.length) throw `unexpected "${toks[p]}"`;
    return n;
  }
  const full = n => n.leaf !== undefined ? n.leaf : `(${full(n.l)} ${n.op} ${full(n.r)})`;
  const opc = op => op === "+" ? "ADD" : op === "-" ? "SUB" : "MPY";
  function plainGen(n, code, T) {
    if (n.leaf !== undefined) { code.push("LDA " + n.leaf); return; }
    if (n.op === "**") { plainGen(n.l, code, T); const t = "T" + (++T.n); code.push("STO " + t); for (let k = 1; k < +n.r.leaf; k++) code.push("MPY " + t); return; }
    plainGen(n.l, code, T); const t1 = "T" + (++T.n); code.push("STO " + t1);
    plainGen(n.r, code, T); const t2 = "T" + (++T.n); code.push("STO " + t2);
    code.push("LDA " + t1); code.push(opc(n.op) + " " + t2);
  }
  function goodGen(n, code, T) {
    if (n.leaf !== undefined) { code.push("LDA " + n.leaf); return; }
    if (n.op === "**") {
      const k = +n.r.leaf; let base;
      if (n.l.leaf !== undefined) { base = n.l.leaf; code.push("LDA " + base); } else { goodGen(n.l, code, T); base = "T" + (++T.n); if (k > 1) code.push("STO " + base); }
      for (let i = 1; i < k; i++) code.push("MPY " + base); return;
    }
    if (n.r.leaf !== undefined) { goodGen(n.l, code, T); code.push(opc(n.op) + " " + n.r.leaf); return; }
    if (n.op !== "-" && n.l.leaf !== undefined) { goodGen(n.r, code, T); code.push(opc(n.op) + " " + n.l.leaf); return; }
    goodGen(n.r, code, T); const t = "T" + (++T.n); code.push("STO " + t); goodGen(n.l, code, T); code.push(opc(n.op) + " " + t);
  }
  function run(code) {
    const mem = Object.assign({}, vals); let acc = 0;
    for (const ins of code) {
      const [op, a] = ins.split(" "); const v = /^\d+$/.test(a) ? +a : mem[a];
      if (op === "LDA") acc = v; else if (op === "ADD") acc += v; else if (op === "SUB") acc -= v; else if (op === "MPY") acc *= v; else mem[a] = acc;
    }
    return acc;
  }
  function list(id, code) { const ol = document.getElementById(id); ol.innerHTML = ""; code.forEach(c => { el("li", {class: c.startsWith("STO") || c.startsWith("LDA T") ? "st" : ""}, ol).textContent = c; }); }
  function show() {
    const say = document.getElementById("cp-say"), fb = document.getElementById("cp-full");
    let n;
    try { n = parse(inp.value); } catch (e) { say.textContent = "Not a formula of this grammar: " + e + "."; fb.textContent = ""; list("cp-plain", []); list("cp-good", []); document.getElementById("cp-h1").textContent = "plain"; document.getElementById("cp-h2").textContent = "careful"; return; }
    fb.textContent = "Structure: " + full(n);
    const p = [], g = []; plainGen(n, p, {n: 0}); goodGen(n, g, {n: 0});
    list("cp-plain", p); list("cp-good", g);
    document.getElementById("cp-h1").textContent = `plain: ${p.length} instructions`;
    document.getElementById("cp-h2").textContent = `careful: ${g.length} instructions`;
    const a = run(p), b = run(g);
    say.textContent = `Both programs compute ${a}${a === b ? "" : " / " + b}. The careful one is ${p.length - g.length} instructions shorter: it uses a letter directly instead of storing and reloading it, and swaps the order of + and * when that saves a temporary word (greyed: stores and reloads of temporaries).`;
  }
  inp.addEventListener("input", show);
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 680, "How the compiler and BNF combined older ideas, and where they led")
    W = 210
    nodes = {
        "sub": (20, 20, "Subroutine libraries", "routines called by name", "topic 1", "ink"),
        "sc": (395, 20, "Speedcoding", "floating point written symbolically", "Backus, 1953", "ink"),
        "post": (770, 20, "Rewriting rules", "Post's systems, Chomsky's grammars", "1920s–1956", "ink"),
        "fort": (395, 170, "FORTRAN", "⊕ formulas translated into code as good as a coder's", "IBM, 1954–1957", "red"),
        "bnf": (770, 220, "BNF", "⊕ recursive rules that define a language", "Backus 1959; ALGOL 60, 1960", "red"),
        "opt": (20, 330, "Optimization", "fewer stores, better loops, index registers", "the 1957 paper, sections 2 to 6", "ink"),
        "pars": (395, 400, "Parsers from grammars", "one procedure per rule", "", "ink"),
        "today": (395, 530, "Compilers today", "every language, every machine", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sub", "fort", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("sc", "fort", ports=("bottom", "top"))
    D.edge("post", "bnf", ports=("bottom", "top"))
    D.edge("fort", "bnf", ports=("right", "left"), dashed=True)
    D.edge("fort", "opt", ports=("bottom:0.1", "top:0.7"))
    D.edge("bnf", "pars", ports=("bottom:0.3", "right:0.5"))
    D.edge("fort", "pars", ports=("bottom", "top"))
    D.edge("opt", "today", ports=("bottom:0.6", "left:0.5"))
    D.edge("pars", "today", ports=("bottom", "top"))
    D.text(20, 660, "Dashed: Backus links the two, and library routines are what compiled programs call; a likeness, not a documented line of descent.", "caption")
    return D


def chain(d):
    c, r = d["code"], d["rand"]
    steps = [
        ("Programs written instruction by instruction: slow to write, easy to get wrong",
         "FORTRAN: write the formula, let the machine translate it; 47 statements became about 1,000 instructions", "IBM, 1957"),
        ("A translator is worth using only if its programs are as good as a careful coder's",
         f"Generate carefully: {c['ng']} instructions for the sample formula where a plain translator writes {c['np']}", "18 man-years of work"),
        ("What exactly is a formula? Prose descriptions of languages leave room for argument",
         "BNF: a handful of recursive rules define the language and the structure of every sentence", "Backus 1959; the ALGOL 60 report"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from hand coding to defined languages")
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
    p, c, r, a = d["parse"], d["code"], d["rand"], d["assoc"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Backus's Speedcoding had already let programmers write floating-point operations symbolically. FORTRAN added a translator that read whole formulas and loops and wrote machine code nearly as good as a careful programmer's. Two years later Backus gave languages an exact definition. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: FORTRAN and BNF. Blue: compilers today."),
        ]),
        dict(id="compile", eyebrow="Try it", title="Type a formula and compile it two ways", toc="Try it", blocks=[
            dict(type="p", text="Type a formula. The page parses it with the grammar below (one procedure per rule), shows the structure it finds, and compiles it for a machine with one accumulator: LDA (load), ADD, SUB, MPY (multiply), STO (store). The plain translator stores every intermediate result; the careful one uses a letter directly when it can. Change the letters' values and both programs are run."),
            dict(type="widget", html=CP_HTML, js=CP_JS, css=CP_CSS,
                 fallback=dict(type="svg", name="syntax", draw=tree_svg(d), alt=f"The syntax tree of {p['f']}", width=640),
                 note="In the interactive edition you can type any formula and see both programs."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="From a grammar to instructions", toc="How it works", blocks=[
            dict(type="p", text="**The grammar.** The ALGOL 60 report defines arithmetic expressions with rules such as `<term> ::= <factor> | <term> <multiplying operator> <factor>`: a term is a factor, or a term followed by a multiplication sign and a factor. The program uses four such rules (expression, term, factor, primary), and each becomes one procedure of the parser, calling the others as the rule mentions them. Because the rule for expression puts the earlier operation deeper in the tree, A − B − C means (A − B) − C."),
            dict(type="p", text=f"**The structure.** For {p['f']} the parser finds {p['full']}: powers first, then products, then sums and differences, left to right. The FORTRAN paper describes the same idea: \"there is implicit in every arithmetic formula an order of computation\", and the translator assigns level numbers so that \"the operations are carried out in the order of increasing level number\"."),
            dict(type="table", head=["Plain translator", "Careful translator"], num=[],
                 rows=[[c["plain"][i] if i < len(c["plain"]) else "", c["good"][i] if i < len(c["good"]) else ""] for i in range(max(len(c["plain"]), len(c["good"])))]),
            dict(type="p", text=f"**Two translators.** The plain one stores every intermediate result in a temporary word and loads it back: {c['np']} instructions. The careful one computes D × (E − F) first and stores it once, then builds B × C² + A directly: {c['ng']} instructions. With {c['vals']}, both give {c['result']}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Define the language by rules, read each formula into the tree the rules give it, and walk the tree to write instructions. Then spend the effort where the FORTRAN team spent it: on making those instructions as few and as fast as a person would."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Twenty thousand random formulas", toc="Measured", blocks=[
            dict(type="p", text=f"The program built {r['n']} random formulas from the grammar's own rules (for example {r['ex']}), printed each with the fewest brackets, parsed it again and got the same structure, compiled it both ways and ran it {r['runs']} times in all with random values: every result matched direct evaluation."),
            dict(type="table", head=["Translator", "Instructions for all the formulas"], num=[1],
                 rows=[["plain", r["plain"]], ["careful", r["good"]]], hl=1),
            dict(type="p", text=f"The careful translator wrote {r['pct']}% fewer instructions. FORTRAN went much further, with sections that moved work out of loops and planned the use of index registers so that \"the time spent in loading and storing index registers will be nearly minimum\"."),
            dict(type="p", text=f"**Left to right.** {a['f']} with {a['vals']}: the grammar's structure {a['left']} gives {a['lv']}; read the other way, {a['right']} would give {a['rv']}. A rule decides it, not a convention left to the reader."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Forty-seven statements in four hours", toc="The evidence", blocks=[
            dict(type="p", text="\"The FORTRAN project was begun in the summer of 1954\"; \"Two and one-half years and 18 man years have elapsed since the beginning of the project.\" The aim: to \"produce as good programs as human coders (but without the errors)\", and \"It was expected that such a system would reduce the coding and debugging task to less than one-fifth of the job it had been.\" A user \"programmed the job in four hours, using 47 FORTRAN statements. These were compiled by the 704 in six minutes, producing about 1000 instructions\"; he \"estimated that it might have taken three days to code this job by hand\" (Backus et al. 1957, p. 189). The paper was read at the Western Joint Computer Conference in Los Angeles in February 1957; the first compiler was delivered in April 1957."),
            dict(type="p", text="Backus presented a notation for syntax at the UNESCO conference in Paris in 1959; the ALGOL 60 report, edited by Peter Naur, used it: \"Sequences of characters enclosed in the bracket <> represent metalinguistic variables\"; \"The marks ::= and | (the latter with the meaning of **or**) are metalinguistic connectives.\" Knuth (1964) argued for reading BNF as Backus–Naur form. Backus received the Turing Award in 1977."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Every program in this book", toc="Full circle", blocks=[
            dict(type="p", text="Every program in this book is compiled before it runs: `java File.java` translates the Java source, defined by a grammar written in a descendant of BNF, into instructions for a virtual machine. Regular expressions (topic 2) cut the text into words; a grammar gives the words their structure; the compiler writes the code."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The sample formula needs {c['np']} instructions written naively and {c['ng']} written carefully. The FORTRAN team spent most of 18 man-years on the difference."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What structure does the grammar give A * B + C * D?", "((A * B) + (C * D)): two terms joined by +."),
            ("And 2 ** 3 ** 2 in this grammar?", "((2 ** 3) ** 2) = 64, because the factor rule is left-recursive like the others. Many languages choose the other way."),
            ("Why does the careful translator never store a single letter?", "A letter is already in memory: the instruction can use it directly, as in ADD A."),
            ("Why can it swap A + (B × C) but not A − (B × C)?", "Addition gives the same result in either order; subtraction does not."),
            ("What does BNF add that a prose description does not?", "Exactness: a string either can or cannot be produced by the rules, and the rules also say how it is put together."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The FORTRAN Automatic Coding System (1957)", text="The first formal paper on the completed FORTRAN compiler, by Backus and twelve colleagues.",
                 draw=C.draw_manuscript, link="https://people.cs.umass.edu/~emery/classes/cmpsci691st/readings/PL/FORTRAN-102663113.05.01.acc.pdf", link_text="PDF on a course page", licence="Drawn placeholder."),
            dict(title="Revised Report on the Algorithmic Language Algol 60", text="A whole language defined in BNF, edited by Peter Naur.",
                 draw=C.draw_book, link="https://masswerk.at/algol60/report.htm", link_text="Transcription", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Compiler", d["checks"],
                           f"the sample formula's structure and code, {r['n']} random formulas parsed, printed, re-parsed, compiled two ways and run {r['runs']} times, and left-to-right subtraction.",
                           ["static Node expression()", "static void goodGen(Node n)"]),
    ]
    return dict(
        title="The Compiler, and a Grammar for Languages", date="1954–1960",
        description="Era 5, topic 8 of The Algorithm Evolution Atlas: FORTRAN's compiler and Backus's notation for grammars, with a parser written from the rules and two code generators compared.",
        lede="Programmers spent most of their time on bookkeeping: which word holds what, which register counts the loop. A team at IBM let the machine translate formulas into instructions, nearly as well as a person would; two years later Backus found a way to define such a language exactly.",
        fieldnote=f"Forty-seven statements in four hours; about a thousand instructions in six minutes. The team's condition was that the machine's code be as good as a careful coder's. My little translator writes {c['ng']} instructions where a naive one writes {c['np']}, for the same formula and the same answer, {c['result']}.",
        card=[("When", "FORTRAN 1954–1957; BNF 1959–1960"),
              ("Where", "IBM, New York; Paris; the ALGOL committee"),
              ("What hurt", "Programs written instruction by instruction"),
              ("The fix", "Formulas translated into efficient code; rules that define a language"),
              ("Cost", "18 man-years for the first FORTRAN compiler")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Compiler.java`.",
    )
