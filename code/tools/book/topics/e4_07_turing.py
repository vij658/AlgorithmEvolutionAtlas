"""Era 4, topic 7: Turing's machines. Every number is parsed from TuringMachines.java's output."""
import re

import common as C
from diagrams import Diagram


def brk(s, n=8):
    """Long digit strings with zero-width spaces, so they can wrap on a phone."""
    return "\u200b".join(s[i:i + n] for i in range(0, len(s), n))


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"machine1: .*? after 40 moves: (.+?) ; ", ln):
            d["tape1"] = m.group(1)
        elif m := re.match(r"sd: standard description (\S+) ; .*? description number (\d+), the number printed in the paper$", ln):
            d["sd"], d["dn"] = m.group(1), m.group(2)
        elif m := re.match(r"universal: the description number read back as (\d+) instructions ; .*? for (\d+) moves$", ln):
            d["uni"] = dict(n=m.group(1), moves=int(m.group(2)))
        elif m := re.match(r"example: .*? standard description (\S+) ; description number (\d+), as published$", ln):
            d["wsd"], d["wdn"] = m.group(1), m.group(2)
        elif m := re.match(r"two: all (\d+) machines .*? ; (\d+) halt \((.+?)\) ; the slowest takes (\d+) moves and the most ones left is (\d+) ; the other (\d+) are still running after (\d+) moves", ln):
            d["two"] = dict(total=int(m.group(1)), halt=int(m.group(2)), by=re.findall(r"(\d) moves: (\d+)", m.group(3)),
                            slow=m.group(4), ones=m.group(5), run=int(m.group(6)), cap=int(m.group(7)))
        elif m := re.match(r"bb5: .*? halts after (\d+) moves, leaving (\d+) ones on a stretch of (\d+) squares ; after (\d+) moves", ln):
            d["bb5"] = dict(moves=int(m.group(1)), ones=int(m.group(2)), width=int(m.group(3)), budget=int(m.group(4)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def machine_svg(d):
    def draw(t, standalone):
        out = [C.text(20, 30, "Turing's first example: four m-configurations, one symbol read (blank)", t["ink"], 15, "start", 700)]
        rows = [("b", "blank", "print 0, move right", "c"), ("c", "blank", "move right", "e"),
                ("e", "blank", "print 1, move right", "f"), ("f", "blank", "move right", "b")]
        heads = ["config", "reads", "does", "then"]
        xs = [30, 120, 220, 440]
        for i, h in enumerate(heads):
            out.append(C.text(xs[i], 62, h, t["muted"], 12.5))
        for r, row in enumerate(rows):
            for i, v in enumerate(row):
                out.append(C.text(xs[i], 88 + r * 24, v, t["red"] if i in (0, 3) else t["ink"], 14, "start", 700 if i in (0, 3) else 400))
        cells = d["tape1"].split()[:16]
        for i, c in enumerate(cells):
            x = 30 + i * 44
            out.append(C.rect(x, 200, 40, 40, t["surface"], t["axis"], 1.5))
            if c != "_":
                out.append(C.text(x + 20, 227, c, t["blue"], 18, "middle", 700))
        out.append(C.text(30, 262, "The tape after the first moves: figures on every other square, the squares between left free.", t["muted"], 12.5))
        out.append(C.text(30, 296, "Description number (1936):", t["ink"], 13.5, "start", 700))
        out.append(f'<text x="30" y="318" style="fill:{t["red"]};font-size:13.5px;font-family:ui-monospace,Menlo,Consolas,monospace">{d["dn"]}</text>')
        out.append(C.text(30, 342, "The program rebuilds this number from the table and runs the machine from the number alone.", t["muted"], 12.5))
        return C.svg_doc(760, 356, "".join(out), "Turing's first example machine, its tape and its description number", t, standalone, 0.55, 760)
    return draw


TM_HTML = """
<div class="board tm-board">
  <div style="min-width:0">
    <div class="presets" id="tm-pre"></div>
    <div class="tm-tape" id="tm-tape" aria-label="The tape around the head"></div>
    <div class="controls">
      <button class="primary" id="tm-step">One move</button>
      <button id="tm-100">100 moves</button>
      <button id="tm-run">Run until it halts</button>
    </div>
    <table class="tm-table" id="tm-table"></table>
  </div>
  <div style="min-width:0">
    <ol class="tm-steps" id="tm-steps"></ol>
    <p class="say" id="tm-say" aria-live="polite"></p>
  </div>
</div>
"""

TM_CSS = """
.tm-tape{display:grid;grid-template-columns:repeat(17,minmax(0,1fr));gap:2px;margin:10px 0;max-width:460px}
.tm-tape span{aspect-ratio:1;min-width:0;display:flex;align-items:center;justify-content:center;font:600 12px var(--mono);border:1px solid var(--axis);background:var(--surface);color:var(--ink)}
.tm-tape span.h{outline:3px solid var(--red);outline-offset:-3px}
.tm-table{border-collapse:collapse;font:12.5px var(--mono);margin-top:8px;max-width:100%}
.tm-table td,.tm-table th{border:1px solid var(--axis);padding:3px 7px;text-align:center}
.tm-table th{color:var(--muted);font-weight:400}
.tm-table td.now{background:color-mix(in srgb,var(--yellow) 40%,transparent)}
.tm-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.tm-steps .m{font-family:var(--mono);font-size:12px;overflow-wrap:anywhere}
"""

TM_JS_TEMPLATE = r"""
(() => {
  const tapeEl = document.getElementById("tm-tape");
  if (!tapeEl) return;
  // rules: [state, symbol, write, move (-1/1), next (-1 = halt)]; symbols: 0 blank, 1, 2
  const M = {
    "Turing's machine I": {names: ["b", "c", "e", "f"], sym: ["", "0", "1"], rules: [[0, 0, 1, 1, 1], [1, 0, 0, 1, 2], [2, 0, 2, 1, 3], [3, 0, 0, 1, 0]]},
    "Two-state busy beaver": {names: ["A", "B"], sym: ["0", "1"], rules: [[0, 0, 1, 1, 1], [0, 1, 1, -1, 1], [1, 0, 1, -1, 0], [1, 1, 1, 1, -1]]},
    "Five-state busy beaver": {names: ["A", "B", "C", "D", "E"], sym: ["0", "1"], rules: [[0, 0, 1, 1, 1], [0, 1, 1, -1, 2], [1, 0, 1, 1, 2], [1, 1, 1, 1, 1], [2, 0, 1, 1, 3], [2, 1, 0, -1, 4], [3, 0, 1, -1, 0], [3, 1, 1, -1, 3], [4, 0, 1, 1, -1], [4, 1, 0, -1, 0]]},
  };
  const BB5 = __BB5__;
  let cur, tape, head, state, moves, rule, busy = 0;
  function dn(m) {                       // Turing's standard description and description number
    const sd = m.rules.map(([q, s, w, mv, n]) => "D" + "A".repeat(q + 1) + "D" + "C".repeat(s) + "D" + "C".repeat(w) + (mv < 0 ? "L" : "R") + "D" + "A".repeat(n + 1) + ";").join("");
    return [sd, [...sd].map(c => "ACDLRN;".indexOf(c) + 1).join("")];
  }
  function load(name) {
    busy++; cur = M[name]; tape = new Map(); head = 0; state = 0; moves = 0; rule = null; show();
    const [sd, num] = dn(cur);
    const ol = document.getElementById("tm-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    li(`${cur.rules.length} lines in the table, ${cur.names.length} states`);
    li(`standard description <span class="m">${sd.length > 90 ? sd.slice(0, 60) + "…" : sd}</span>`);
    li(`description number <span class="m">${num.length > 90 ? num.slice(0, 60) + "… (" + num.length + " digits)" : num}</span>`);
    document.getElementById("tm-say").textContent = name === "Turing's machine I" ? "This machine never halts: it prints 0 and 1 on alternate squares for ever." :
      name === "Two-state busy beaver" ? "Of all two-state machines that halt from a blank tape, none runs longer or leaves more ones." :
      `This one halts, but only after ${fmt(BB5.moves)} moves. Press "Run until it halts".`;
  }
  function find() { const s = tape.get(head) || 0; return cur.rules.find(r => r[0] === state && r[1] === s); }
  function step() {
    if (state < 0) return false;
    const r = find(); if (!r) return false;
    tape.set(head, r[2]); head += r[3]; state = r[4]; moves++; rule = r;
    return state >= 0;
  }
  function show() {
    tapeEl.innerHTML = "";
    for (let i = head - 8; i <= head + 8; i++) {
      const s = tape.get(i) || 0;
      el("span", {class: i === head ? "h" : ""}, tapeEl, cur.sym[s]);
    }
    const tb = document.getElementById("tm-table"); tb.innerHTML = "";
    const hr = el("tr", {}, tb); ["state", "reads", "writes", "moves", "next"].forEach(h => el("th", {}, hr, h));
    for (const r of cur.rules) {
      const tr = el("tr", {}, tb);
      [cur.names[r[0]], cur.sym[r[1]] || "blank", cur.sym[r[2]] || "blank", r[3] < 0 ? "L" : "R", r[4] < 0 ? "halt" : cur.names[r[4]]].forEach(v => el("td", {class: r === rule ? "now" : ""}, tr, v));
    }
    let ones = 0; for (const v of tape.values()) if (v === 1 && cur.sym[1] === "1") ones++;
    const st = state < 0 ? "halted" : "state " + cur.names[state];
    const say = document.getElementById("tm-say");
    if (state < 0) say.textContent = `Halted after ${fmt(moves)} moves${cur.sym[1] === "1" ? ", leaving " + fmt(ones) + " ones" : ""}.`;
    else if (moves) say.textContent = `${fmt(moves)} moves, ${st}${cur.sym[1] === "1" ? ", " + fmt(ones) + " ones on the tape" : ""}.`;
  }
  const pre = document.getElementById("tm-pre");
  Object.keys(M).forEach(n => { const b = el("button", {type: "button"}, pre, n); b.addEventListener("click", () => load(n)); });
  document.getElementById("tm-step").addEventListener("click", () => { step(); show(); });
  document.getElementById("tm-100").addEventListener("click", () => { for (let i = 0; i < 100 && step(); i++); show(); });
  document.getElementById("tm-run").addEventListener("click", () => {
    const my = ++busy, t0 = moves;
    if (cur === M["Turing's machine I"]) { for (let i = 0; i < 1000 && step(); i++); show(); document.getElementById("tm-say").textContent = "Stopped watching after 1,000 more moves: this machine never halts."; return; }
    // the five-state machine: an array tape is much faster than a map
    const arr = new Uint8Array(1 << 16), off = 1 << 15;
    for (const [k, v] of tape) arr[k + off] = v;
    let h = head + off, q = state;
    const R = {}; for (const r of cur.rules) R[r[0] * 4 + r[1]] = r;
    function chunk() {
      if (my !== busy) return;
      const end = moves + 2000000;
      while (q >= 0 && moves < end) { const r = R[q * 4 + arr[h]]; arr[h] = r[2]; h += r[3]; q = r[4]; moves++; }
      tape = new Map(); for (let i = 0; i < arr.length; i++) if (arr[i]) tape.set(i - off, arr[i]);
      head = h - off; state = q; rule = null; show();
      if (q >= 0) requestAnimationFrame(chunk);
      else if (cur === M["Five-state busy beaver"]) document.getElementById("tm-say").textContent += ` The program found the same: ${fmt(BB5.moves)} moves and ${fmt(BB5.ones)} ones.`;
    }
    chunk();
  });
  load("Turing's machine I");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Turing's machines combined older ideas, and where they led")
    W = 210
    nodes = {
        "hil": (20, 20, "The decision problem", "is there a process for every statement?", "topic 1", "ink"),
        "clerk": (395, 20, "The human computer", "a clerk with pencil, paper and rules", "Turing's model", "ink"),
        "god": (770, 20, "Gödel's numbering", "objects coded as numbers; the diagonal", "topic 5", "ink"),
        "tm": (395, 170, "Turing's machines", "⊕ tape, head and table; machines as numbers", "1936", "red"),
        "uni": (20, 330, "The universal machine", "one machine runs any table it is given", "1936", "ink"),
        "halt": (395, 330, "No general halting test", "the decision problem is unsolvable", "1936", "ink"),
        "bb": (770, 330, "Busy beavers", "how long can a small machine run?", "Radó 1962; 2024", "ink"),
        "today": (395, 480, "Computers and their limits", "stored programs; undecidable questions about code", "topic 9; today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("hil", "tm", ports=("bottom", "top:0.15"))
    D.edge("clerk", "tm", ports=("bottom", "top"))
    D.edge("god", "tm", ports=("bottom", "top:0.85"))
    D.edge("tm", "uni", ports=("bottom:0.1", "top:0.7"))
    D.edge("tm", "halt", ports=("bottom", "top"))
    D.edge("tm", "bb", ports=("bottom:0.9", "top:0.3"))
    D.edge("halt", "today", ports=("bottom", "top"))
    D.edge("uni", "today", ports=("bottom:0.7", "left:0.5"), dashed=True)
    D.text(20, 615, "Dashed: whether the stored-program design drew on Turing's paper is not settled in the sources opened here.", "caption")
    return D


def chain(d):
    b5 = d["bb5"]
    steps = [
        ("The decision problem needed an exact meaning for \"mechanical process\"",
         "A tape, a head, a finite table: a clerk at work, stripped down", "Turing, 1936"),
        ("Every task seems to need its own machine",
         "A universal machine reads any table, written as a number, and runs it", "Turing, 1936"),
        ("Can a machine decide, from a description, whether a machine runs properly for ever?",
         "No: the diagonal argument. So Hilbert's decision problem is unsolvable", "Turing, 1936"),
        (f"Waiting is no test: a five-state machine runs {b5['moves']:,} moves, then halts",
         "Proofs about particular machines: all five-state machines settled", "bbchallenge, 2024"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a definition of mechanical to the limits of machines")
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
    import json
    d = parse(ctx["out"])
    two, b5 = d["two"], d["bb5"]
    js = TM_JS_TEMPLATE.replace("__BB5__", json.dumps(dict(moves=b5["moves"], ones=b5["ones"])))
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Hilbert's decision problem (topic 1) asked for a mechanical process; Gödel had just coded formulas as numbers and used a diagonal argument (topic 5). Turing's addition was a picture of the person doing the computing, a clerk following rules, reduced to a machine so simple that its tables could be listed, numbered, and fed to other machines. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Turing's paper of 1936. Blue: where it led."),
        ]),
        dict(id="machine", eyebrow="Try it", title="Run a machine, and read its number", toc="Try it", blocks=[
            dict(type="p", text=f"Pick a machine and step it. The tape shows 17 squares around the head (outlined); the table highlights the line just used. Turing's own first example prints 0 and 1 on alternate squares for ever. The two-state busy beaver halts after {two['slow']} moves; the five-state one halts too, after {b5['moves']:,} moves. Each machine's description number is shown: that number, given to a universal machine, is the program."),
            dict(type="widget", html=TM_HTML, js=js, css=TM_CSS,
                 fallback=dict(type="svg", name="machine", draw=machine_svg(d), alt="Turing's first example machine, its tape and its description number", width=760),
                 note="In the interactive edition you can run three machines move by move, or until they halt."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A table, a number, and a question with no answer", toc="How it works", blocks=[
            dict(type="p", text="**The machine.** A tape of squares, a head over one of them, and a table. Each line says: in this state, reading this symbol, write a symbol, move one square, and go to that state. Turing's first example has four states, b, c, e and f, and prints \"the sequence 010101...\": b prints 0 and moves right; c just moves right; e prints 1 and moves right; f moves right and starts again."),
            dict(type="p", text=f"**The number.** Turing wrote each line in letters: D followed by A's for the state, D followed by C's for the symbol read and the symbol written, L, R or N for the move, and D with A's for the next state; then he replaced A, C, D, L, R, N and ; by the digits 1 to 7. For the first example the program builds the standard description {brk(d['sd'], 10)} and the description number {brk(d['dn'])}, digit for digit the number printed in the paper. It then reads the number back into a table of {d['uni']['n']} lines and runs the machine from the number alone: the tape is the same for {d['uni']['moves']:,} moves. A universal machine does exactly this, on its own tape."),
            dict(type="p", text="**The question with no answer.** Suppose some machine H could read any description number and say whether that machine halts. Build a machine that, given a number, asks H about the machine with that number fed its own number, and does the opposite: loops if H says \"halts\", halts if H says \"loops\". Feed this machine its own number, and H must be wrong. So H cannot exist. Turing's own version asks whether a machine is \"circle-free\" (prints for ever without getting stuck); the conclusion is the same, and with it the Entscheidungsproblem falls."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A machine's table is finite, so it can be written as a number and handed to another machine: one universal machine can run them all. The same fact lets a machine be fed its own description, which is why no machine can decide, for every machine, whether it will halt."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Small machines, long runs", toc="Measured", blocks=[
            dict(type="table", head=["Two-state, two-symbol machines from a blank tape", "Count"], num=[1],
                 rows=[["all machines (each of 4 lines: write 0 or 1, move left or right, go to A, B or halt)", f"{two['total']:,}"],
                       ["halt", f"{two['halt']:,}"]] + [[f"…of which halt after {m} move{'s' if m != '1' else ''}", f"{int(c):,}"] for m, c in two["by"]] +
                      [[f"still running after {two['cap']:,} moves", f"{two['run']:,}"]], hl=7),
            dict(type="p", text=f"No two-state machine that halts takes more than {two['slow']} moves or leaves more than {two['ones']} ones, which are Radó's values for two states. Knowing that number settles halting for every two-state machine: run it for {two['slow']} moves, and if it has not halted, it never will. For five states the number is {b5['moves']:,}, found in 1989 and proved only in 2024; the program runs that machine to the end, leaving {b5['ones']:,} ones on a stretch of {b5['width']:,} squares. A test that waited {b5['budget']:,} moves would have called it a machine that never halts."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Cambridge and Princeton, 1936", toc="The evidence", blocks=[
            dict(type="p", text="Turing took Max Newman's course on the foundations of mathematics in spring 1935, which covered Gödel's results and Hilbert's decision problem; he finished the paper in April 1936 and revised it in August, and Newman had to argue for publishing it after Church's paper appeared (MacTutor). The paper was received on 28 May 1936 and read on 12 November 1936; its appendix, \"Added 28 August, 1936\", shows that Church's \"effective calculability\" is \"equivalent to my 'computability'\"."),
            dict(type="p", text="\"It is possible to invent a single machine which can be used to compute any computable sequence\", and \"there can be no general process for determining whether a given number is satisfactory or not\" (Turing 1936). Turing \"did not use the terms 'halt' or 'halting'\"; the name halting problem is credited to Martin Davis (Wikipedia). The five-state busy beaver of Marxen and Buntrock (1989) was \"only proved to be the winning fifth busy beaver in 2024\" by the bbchallenge collective (Wikipedia, Busy beaver)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Every computer is universal", toc="Full circle", blocks=[
            dict(type="p", text="The machine you are reading this on is, apart from its finite memory, a universal machine: it runs whatever program it is given, and its programs are stored as numbers (topic 9). Turing's negative result came with it. No program can decide, for every program, whether it halts; tools that look for bugs in code must therefore sometimes say \"I don't know\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Turing's first machine is the {len(d['dn'])}-digit number {brk(d['dn'])}. A five-state machine, whose table fits on a postcard, ran {b5['moves']:,} moves before halting, and proving that no five-state machine runs longer took until 2024."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What does Turing's machine I write on its first eight squares?", "0, blank, 1, blank, 0, blank, 1, blank: figures on alternate squares."),
            ("In Turing's code, what does DAA stand for, and DCC?", "DAA is the second state (q2); DCC is the second symbol (S2), which in the first example is the figure 1."),
            ("Why can a universal machine exist at all?", "A machine is a finite table, so it can be written on a tape as a string of symbols; one machine can then read that string and do what each line says."),
            ("Why is \"run it for a long time and see\" not a halting test?", f"A machine that has not halted yet may halt later: the five-state busy beaver is still running after {b5['budget']:,} moves and halts at {b5['moves']:,}."),
            ("If someone knew the longest a six-state machine can run before halting, what could they do?", "Decide halting for every six-state machine from a blank tape: run it that long. Radó's function grows too fast to be computed, so no general method can supply those numbers."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="On Computable Numbers (1936)", text="The paper, with the first example machine and its description number.",
                 draw=C.draw_manuscript, link="https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf", link_text="University of Virginia (scan)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "TuringMachines", d["checks"],
                           f"Turing's first machine and its description number against the one printed in 1936, the number decoded and run, every one of the {two['total']:,} two-state machines, and the five-state busy beaver run to its halt at move {b5['moves']:,}.",
                           ["static String standardDescription(", "static List<Rule> decode("]),
    ]
    return dict(
        title="Turing's Machines", date="1936",
        description="Era 4, topic 7 of The Algorithm Evolution Atlas: Turing's machines, his description numbers, the universal machine, and why no machine can decide halting.",
        lede="Turing defined computation by watching a person compute: a tape, a head that reads one square, and a finite table of rules. Tables can be written as numbers, so one machine can run all the others, and no machine can decide whether every other one halts.",
        fieldnote=f"Turing's first machine is the number {brk(d['dn'])}. I gave that number to a program that knew nothing else, and it printed 0 and 1 on alternate squares, exactly as the paper says. A machine is a number; a number can be a machine.",
        card=[("When", "Received 28 May 1936; printed 1937"),
              ("Where", "Cambridge; Princeton"),
              ("What hurt", "No exact meaning for \"mechanical process\""),
              ("The fix", "Tape, head, table; a universal machine"),
              ("Limit", "No machine decides halting for all machines")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `TuringMachines.java`.",
    )
