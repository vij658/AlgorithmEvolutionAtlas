"""Era 3, topic 11: Lovelace's Note G. Every number is parsed from NoteG.java's output (and its operation table from the source)."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"noteg: .*? ; (\d+) operations executed \(25 cards, operations 13 to 23 repeated (\d+) times\) ; B7 = (\S+)$", ln):
            d["ng"] = dict(ops=m.group(1), reps=m.group(2), b7=m.group(3))
        elif m := re.match(r"trace: (.+)$", ln):
            d["trace"] = m.group(1).split(" ; ")
        elif m := re.match(r"series: each result fed into the next run: (.+?) ; every one", ln):
            d["series"] = re.findall(r"B(\d+) = (\S+?)(?:,|$)", m.group(1))
        elif m := re.match(r"bug: .*? B7 comes out (\S+) instead of (\S+) ; fed forward from B1, the run gives (.+)$", ln):
            d["bug"] = dict(wrong=m.group(1), right=m.group(2), chain=re.findall(r"B(\d+) = (\S+?)(?:,|$)", m.group(3)))
        elif m := re.match(r"growth: (.+?) ; operations for .*? ; all of B3 to B39 in ([\d,]+) operations ; B39 = (\S+)$", ln):
            d["grow"] = dict(rows=re.findall(r"B(\d+): (\d+) operations", m.group(1)), total=m.group(2), b39=m.group(3))
    d["checks"] = C.checks(text)
    return d


def program(java: str):
    """The 25 operation cards, read from the program's source."""
    return [dict(num=int(a), kind=k, a=int(b), b=int(c), dest=int(e), note=n)
            for a, k, b, c, e, n in re.findall(r"new Op\((\d+), '(.)', (\d+), (\d+), (\d+), \"(.*?)\"\)", java)]


# ----------------------------------------------------------------------------------------------------------------------
def plan_diagram(d):
    ng = d["ng"]
    D = Diagram(1000, 250, "The plan of the calculation: set up, a repeated group, finish")
    W, H = 220, 120
    boxes = [("s", "Operations 1–12", ["2n, 2n − 1, 2n + 1", "A0 = −½ (2n − 1)/(2n + 1)", "A1 B1 added in"], "ink"),
             ("l", "Operations 13–23", ["the next A from the last", "times the next B, added in", f"repeated {ng['reps']} times for B7"], "red"),
             ("f", "Operations 24–25", ["B7 = −(the sum)", f"= {ng['b7']}", "n + 1, for the next run"], "ink"),
             ("t", "In all", [f"{ng['ops']} operations", "on numbered columns", "of the store"], "ink")]
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title")] + [(s, "combo" if j == 1 else "note") for j, s in enumerate(sub)], color=col)
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "A RECONSTRUCTION IN THE STYLE OF NOTE G: 25 OPERATION CARDS, ONE GROUP REPEATED", "tag")
    D.text(20, 210, "Lovelace's numbering: B1 = 1/6, B3 = −1/30, B5 = 1/42, B7 = −1/30 (today's B2, B4, B6, B8). Numbers from NoteG.java.", "caption")
    return D


NG_HTML = """
<div class="board ng-board">
  <div style="min-width:0">
    <div class="controls">
      <button type="button" id="ng-step">Next operation</button>
      <button type="button" id="ng-run">Run to the end</button>
      <button type="button" id="ng-reset">Reset</button>
      <label><input type="checkbox" id="ng-bug"> operation 4 the wrong way round</label>
    </div>
    <div class="ng-op" id="ng-op"></div>
    <div class="scrollx"><table class="ng-store" id="ng-store"></table></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The cards</div>
    <ol class="ng-cards" id="ng-cards"></ol>
    <p class="say" id="ng-say" aria-live="polite"></p>
  </div>
</div>
"""

NG_CSS = """
.ng-board .controls{flex-wrap:wrap;font-size:13.5px}
.ng-board .controls input[type=checkbox]{width:auto;padding:0;margin:0 4px 0 0}
.ng-board .controls label{display:inline-flex;align-items:center}
.ng-op{font-family:var(--mono);font-size:14px;margin:8px 0;min-height:1.6em;color:var(--red)}
.ng-store{border-collapse:collapse;font-family:var(--mono);font-size:12px}
.ng-store th{color:var(--muted);font-weight:400;padding:2px 6px;text-align:left}
.ng-store td{border:1px solid var(--axis);padding:3px 6px;min-width:4.5em;background:var(--surface)}
.ng-store td.hot{border-color:var(--red);color:var(--red);font-weight:700}
.ng-cards{margin:4px 0;padding-left:2.8em;font-family:var(--mono);font-size:11.5px;line-height:1.5;max-height:330px;overflow:auto}
.ng-cards li.now{color:var(--red);font-weight:700}
.ng-cards li.loop{background:var(--wash)}
.ng-board .say{font-size:14.5px}
"""

NG_JS = r"""
(() => {
  const store = document.getElementById("ng-store");
  if (!store) return;
  const PROG = __PROG__;
  const B0 = [[1n, 6n], [-1n, 30n], [1n, 42n]];
  const gcd = (a, b) => { a = a < 0n ? -a : a; b = b < 0n ? -b : b; while (b) [a, b] = [b, a % b]; return a; };
  const Q = (n, d = 1n) => { if (d < 0n) { n = -n; d = -d; } const g = gcd(n, d) || 1n; return [n / g, d / g]; };
  const add = (x, y) => Q(x[0] * y[1] + y[0] * x[1], x[1] * y[1]), sub = (x, y) => Q(x[0] * y[1] - y[0] * x[1], x[1] * y[1]);
  const mul = (x, y) => Q(x[0] * y[0], x[1] * y[1]), dv = (x, y) => Q(x[0] * y[1], x[1] * y[0]);
  const show = x => x[1] === 1n ? `${x[0]}` : `${x[0]}/${x[1]}`;
  const COLS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 21, 22, 24];
  let V, pc, bIndex, done, count, last;
  function reset() {
    V = {}; for (let c = 0; c <= 24; c++) V[c] = Q(0n);
    V[1] = Q(1n); V[2] = Q(2n); V[3] = Q(4n); V[21] = B0[0];
    pc = 0; bIndex = 1; done = false; count = 0; last = -1; draw("");
  }
  function step() {
    if (done) return;
    const op = PROG[pc];
    let a = op.a, b = op.b;
    if (op.num === 4 && document.getElementById("ng-bug").checked) [a, b] = [b, a];
    if (op.num === 21) V[22] = B0[bIndex] || Q(0n);
    const x = V[a], y = V[b];
    const r = op.kind === "+" ? add(x, y) : op.kind === "-" ? sub(x, y) : op.kind === "x" ? mul(x, y) : dv(x, y);
    if (op.num === 1) { V[4] = r; V[5] = r; V[6] = r; } else V[op.dest] = r;
    count++; last = op.dest;
    const txt = `${op.num}: V${a} ${op.kind === "x" ? "×" : op.kind === "/" ? "÷" : op.kind} V${b} → V${op.dest} = ${show(r)}   (${op.note})`;
    if (op.num === 21) bIndex++;
    if (op.num === 12 && V[10][0] === 0n) pc = 23;
    else if (op.num === 23 && V[10][0] !== 0n) pc = 12;
    else pc++;
    if (pc >= PROG.length) done = true;
    draw(txt);
  }
  function draw(txt) {
    store.innerHTML = "";
    const h = el("tr", {}, store), r = el("tr", {}, store);
    COLS.forEach(c => { el("th", {}, h, `V${c}`); el("td", { class: c === last ? "hot" : "" }, r, show(V[c])); });
    document.getElementById("ng-op").textContent = txt;
    const ol = document.getElementById("ng-cards"); ol.innerHTML = "";
    PROG.forEach((op, i) => el("li", { class: (i === pc && !done ? "now" : "") + (op.num >= 13 && op.num <= 23 ? " loop" : ""), value: op.num }, ol,
      `V${op.a} ${op.kind === "x" ? "×" : op.kind === "/" ? "÷" : op.kind} V${op.b} → V${op.dest}: ${op.note}`));
    const say = document.getElementById("ng-say");
    if (done) {
      const right = V[24][0] === -1n && V[24][1] === 30n;
      say.textContent = `${count} operations. V24 holds B7 = ${show(V[24])}` + (right ? ": Lovelace's value." : ": wrong. The printed operation 4 divides the wrong way round.");
    } else say.textContent = `${count} operations so far. Shaded cards (13–23) are the group that repeats, once for each middle term.`;
  }
  document.getElementById("ng-step").addEventListener("click", step);
  document.getElementById("ng-run").addEventListener("click", () => { let g = 0; while (!done && g++ < 200) step(); });
  document.getElementById("ng-reset").addEventListener("click", reset);
  document.getElementById("ng-bug").addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Note G combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "de": (20, 20, "The difference engine", "columns of wheels that add", "topic 10", "ink"),
        "jq": (395, 20, "The Jacquard loom", "punched cards choose the pattern", "weaving", "ink"),
        "bn": (770, 20, "Bernoulli numbers", "each from the ones before", "a recurrence", "ink"),
        "ng": (395, 170, "Note G", "⊕ a calculation as numbered operations on a store, with repetition", "Lovelace, 1843", "red"),
        "ae": (20, 330, "The Analytical Engine", "store, mill, cards", "Babbage, never built", "ink"),
        "bb": (395, 330, "Babbage's own programs", "several dozen, 1837–1840", "unpublished", "ink"),
        "pg": (770, 330, "Programs", "loops, variables, and bugs", "Eras 4–5", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("de", "ng", ports=("bottom", "top:0.15"))
    D.edge("jq", "ng", ports=("bottom", "top"))
    D.edge("bn", "ng", ports=("bottom", "top:0.85"))
    D.edge("ng", "ae", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("bb", "ng", ports=("top", "bottom"), dashed=True)
    D.edge("ng", "pg", ports=("bottom:0.9", "top:0.3"))
    D.text(20, 615, "Dashed: Note G describes the Analytical Engine; Babbage's earlier programs (Bromley) were simpler and unpublished.", "caption")
    return D


def chain(d):
    b = d["bug"]
    steps = [
        ("A machine that follows one fixed pattern makes only one kind of table",
         "A store of numbered columns, a mill, and cards that say what to do", "Babbage's Analytical Engine"),
        ("How would anyone tell such a machine what to do?",
         "Write the calculation as a numbered sequence of operations on the columns", "Lovelace, Note G, 1843"),
        ("The same few operations are needed again and again",
         "Repeat a group of cards: a loop", "Note G"),
        (f"One operation the wrong way round: B7 = {b['wrong']} instead of {b['right']}",
         "Run the plan and check it: finding the bug", "modern testing"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a fixed pattern to a program")
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
    ng, sr, bg, gr = d["ng"], d["series"], d["bug"], d["grow"]
    prog = program(ctx["java"])
    js = NG_JS.replace("__PROG__", json.dumps(prog))
    sym = {"x": "×", "/": "÷", "+": "+", "-": "−"}
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Babbage's difference engine (topic 10) held numbers in columns of wheels; the Jacquard loom chose its pattern from punched cards; Bernoulli numbers are defined each from the ones before. Babbage's Analytical Engine combined the first two: a store of columns, a mill, and cards. Lovelace's Note G showed, step by step, what the cards would say. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Note G. Blue: what it anticipates."),
        ]),
        dict(id="run", eyebrow="Try it", title="Run the cards", toc="Try it", blocks=[
            dict(type="p", text="Twenty-five operation cards act on the numbered columns of the store, V1 to V24, in exact fractions. Press Next operation to feed one card to the mill; the shaded cards 13 to 23 repeat once for each middle term. Run to the end to get Lovelace's B7. Then tick the box to make operation 4 divide the wrong way round, as Wikipedia reports for the printed table, and run again."),
            dict(type="widget", html=NG_HTML, js=js, css=NG_CSS,
                 fallback=dict(type="diagram", name="plan", diagram=plan_diagram(d)),
                 note="In the interactive edition you can step through all the operations, watch the store change, and switch on the bug."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A calculation as a list of operations", toc="How it works", blocks=[
            dict(type="p", text="In Lovelace's numbering, B1 = 1/6, B3 = −1/30, B5 = 1/42. Each new one follows from those before by one identity: 0 = A0 + A1 B1 + A3 B3 + … + B₂ₙ₋₁, with A0 = −½ (2n − 1)/(2n + 1), A1 = 2n/2, and each later A obtained from the one before by two more factors on top and two more below. For B7, n = 4."),
            dict(type="p", text="The calculation becomes a list of operations, each naming two columns of the store, an operation for the mill, and a column for the result. The middle terms all have the same shape, so one group of cards, repeated, computes them all. The program's 25 cards:"),
            dict(type="table", head=["Card", "Operation", "What it computes"], num=[0],
                 rows=[[str(p["num"]), f"V{p['a']} {sym[p['kind']]} V{p['b']} → V{p['dest']}", p["note"]] for p in prog]),
            dict(type="p", text=f"For B7 the mill executes **{ng['ops']}** operations, the group 13–23 twice, and column V24 ends holding **{ng['b7']}**. The first steps, as the program traced them: {'; '.join(d['trace'][:6])}."),
            dict(type="diagram", name="plan-steps", diagram=plan_diagram(d)),
            dict(type="callout", kind="key", label="Key idea",
                 text="Separate the machine from the instructions. The same store and mill compute anything the cards describe; the description, with named storage and a repeated group, is what we now call a program."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Feeding each answer into the next", toc="Measured", blocks=[
            dict(type="table", head=["Lovelace's numbering", "The program's value"], num=[], rows=[[f"B{a}", v] for a, v in sr]),
            dict(type="p", text=f"Run after run, each result is fed into the next, and every value agrees with the standard recurrence. The work grows by one pass of the group per new term: {'; '.join(f'B{a}: {o} operations' for a, o in gr['rows'])}; all of B3 to B39 take {gr['total']} operations, and B39 = {gr['b39']}."),
            dict(type="p", text=f"**The bug.** With operation 4 dividing (2n + 1) by (2n − 1) instead, A0 for n = 4 becomes −½ · 9/7 and B7 comes out **{bg['wrong']}** instead of {bg['right']}. Fed forward from B1, the errors grow: {', '.join(f'B{a} = {v}' for a, v in bg['chain'])}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Forty-one pages of notes, signed A.A.L.", toc="The evidence", blocks=[
            dict(type="p", text="Lovelace's translation of Menabrea appeared in *Taylor's Scientific Memoirs* in August 1843: 66 pages, of which \"forty-one make up her appendices\", signed only \"A.A.L.\" (Hollings, Martin and Rice). Note A says the Analytical Engine \"weaves algebraical patterns just as the Jacquard-loom weaves flowers and leaves\". Note G computes the eighth Bernoulli number (B₈ today, B7 in her numbering), choosing a method whose \"object is not simplicity or facility of computation, but the illustration of the powers of the engine\"; and it insists that \"The Analytical Engine has no pretensions whatever to originate any thing.\""),
            dict(type="p", text="Wikipedia reports that in operation 4 of the printed table \"the division is the wrong way round\" and that, run as printed, it \"would fail to generate Bernoulli numbers correctly\"; the program was never run in Babbage's or Lovelace's lifetime. Is it \"the first computer program\"? Hollings, Martin and Rice call the table an execution trace, the program proper being the card decks, and Bromley found \"several dozen sample programs prepared by Babbage between 1837 and 1840\" (**disputed**). The table itself could not be read in an opened copy, so the 25 cards on this page are this book's reconstruction in its style, not a transcription."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Variables, loops, and a bug", toc="Full circle", blocks=[
            dict(type="p", text="Every element of the plan has a name now: the numbered columns are variables, the repeated group is a loop with a counter (V10), the cards are instructions, and the wrong-way division is a bug."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The bug was found the modern way: by running the plan. The program on this page runs the corrected cards to {ng['b7']} and the reversed ones to {bg['wrong']}. Lovelace wrote her plan for a machine that was never built; it took machines of the kind she imagined to test it."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why is a Bernoulli number a good test for an engine?", "Each is defined from the ones before by a fixed rule, so the same operations repeat, and the answer can be checked."),
            ("What is A0 for n = 4?", "−½ × 7/9 = −7/18."),
            ("Why do cards 13–23 repeat?", "Each middle term A B has the same shape: two new factors into A, times the next B, added to the sum."),
            ("What does the wrong-way division change?", "It replaces 7/9 by 9/7 in A0, so the sum and every later B is wrong."),
            ("Is Note G the first program?", "It is the first such plan to be published; Babbage had written simpler, unpublished ones from 1837, and historians disagree on what counts."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Sketch of the Analytical Engine, with notes by the translator", text="Menabrea's paper and Lovelace's notes A to G (London, 1843), as a Project Gutenberg text.",
                 draw=C.draw_book, link="https://gutenberg.org/files/75107/75107-src/75107-src.htm", link_text="Project Gutenberg",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "NoteG", d["checks"],
                           "Lovelace's B7 from 25 operation cards in exact fractions, B1 to B39 fed run to run against the standard recurrence, the operation count 14 + 11(n − 2) for every run, and the wrong-way division of operation 4.",
                           ["static Q run("]),
    ]
    return dict(
        title="Lovelace's Note G", date="1843",
        description="Era 3, topic 11 of The Algorithm Evolution Atlas: Ada Lovelace's Note G, a calculation of Bernoulli numbers laid out as operations for the Analytical Engine, with its loop and its bug.",
        lede="A translator's notes, longer than the paper they annotate, ended with a table: every step of a calculation, written for a machine that did not exist. It has numbered storage, a group of steps that repeats, and one operation the wrong way round.",
        fieldnote="Babbage's machines carried numbers; this note carried instructions. It is the first time I have found a calculation written down not for a person to follow, but for a machine to obey, step by numbered step.",
        card=[("When", "Menabrea 1842; Lovelace's notes, August 1843"),
              ("Where", "London"),
              ("What hurt", "A general machine has to be told what to do"),
              ("The fix", "Numbered operations on a store, with a repeated group"),
              ("Cost", f"{ng['ops']} operations for B7")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `NoteG.java`; the operation table is read from its source.",
    )
