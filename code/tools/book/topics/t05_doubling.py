"""Era 1, topic 5: Egyptian multiplication by doubling. Every number is parsed from EgyptianDoubling.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"rows": [], "steps": [], "divide": [], "generic": {}}
    for ln in text.splitlines():
        if m := re.match(r"row (\d+) x (\d+): (\d+) (\d+)( ticked)?$", ln):
            d["a"], d["b"] = int(m.group(1)), int(m.group(2))
            d["rows"].append((int(m.group(3)), int(m.group(4)), bool(m.group(5))))
        elif m := re.match(r"multiply \d+ x \d+ = (\d+): doublings=(\d+) additions=(\d+); repeated addition would take (\d+)", ln):
            d["product"], d["doublings"], d["additions"], d["repeat"] = (int(m.group(i)) for i in range(1, 5))
        elif m := re.match(r"multiplycheck: (\d+) random pairs .* average ([\d.]+) doublings and additions, against an average of ([\d,]+) additions", ln):
            d["mc"] = dict(n=int(m.group(1)), avg=float(m.group(2)), rep=m.group(3))
        elif m := re.match(r"steps (\d+): doubling-and-adding=(\d+) repeated-adding=(\d+)$", ln):
            d["steps"].append(tuple(int(m.group(i)) for i in range(1, 4)))
        elif m := re.match(r"divide (\d+) / (\d+): quotient=(\d+) remainder=(\d+) rows=(\d+)$", ln):
            d["divide"].append(tuple(int(m.group(i)) for i in range(1, 6)))
        elif m := re.match(r"generic \+ : .* = (\d+) in (\d+) additions", ln):
            d["generic"]["plus"] = (m.group(1), int(m.group(2)))
        elif m := re.match(r"generic x : 3\^41 = (\d+) in (\d+) multiplications", ln):
            d["generic"]["times"] = (m.group(1), int(m.group(2)))
        elif m := re.match(r"generic matrix : Fibonacci number 90 = (\d+) in (\d+) matrix multiplications", ln):
            d["generic"]["fib"] = (m.group(1), int(m.group(2)))
        elif m := re.match(r"rsa: .* 65 encrypts to (\d+); decrypting \d+\^2753 mod 3233 takes (\d+) multiplications", ln):
            d["generic"]["rsa"] = (m.group(1), int(m.group(2)))
        elif m := re.match(r"rsa-2048: .* needs (\d+) squarings and (\d+) multiplications, (\d+) in all; one at a time would take a number of multiplications with (\d+) digits", ln):
            d["rsa2048"] = tuple(int(m.group(i)) for i in range(1, 5))
        elif m := re.match(r"chain 15: shortest ([\d, ]+) \((\d+) steps\); doubling and adding needs (\d+) \(([\d, ]+)\)", ln):
            d["c15"] = dict(short=m.group(1), short_n=int(m.group(2)), binary_n=int(m.group(3)), binary=m.group(4))
        elif m := re.match(r"chains 1-128: doubling and adding is not the shortest for (\d+) numbers; the first are ([\d ]+)$", ln):
            d["chains"] = dict(n=int(m.group(1)), first=m.group(2).split())
    d["checks"] = C.checks(text)
    return d


DBL_HTML = """
<div class="board dbl-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="db-mode">Rule <select id="db-mode"><option value="mul">double and add: a × b</option><option value="pow">square and multiply: b to the power a</option></select></label>
      <label for="db-a">a <input id="db-a" type="number" min="1" max="1000000" value="AV" inputmode="numeric"></label>
      <label for="db-b">b <input id="db-b" type="number" min="1" max="1000000" value="BV" inputmode="numeric"></label>
    </div>
    <div class="controls">
      <button id="db-step" class="primary" type="button">Next step</button>
      <button id="db-all" type="button">All steps</button>
      <button id="db-reset" type="button">Reset</button>
    </div>
    <div class="tbl"><table class="dbl"><thead><tr><th class="n">Left column</th><th class="n" id="db-head">Right column</th><th>Tick</th></tr></thead><tbody id="db-rows"></tbody></table></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">What the scribe does</div>
    <ol class="steps" id="db-log"></ol>
    <div class="result" id="db-result" aria-live="polite"></div>
  </div>
</div>
"""

DBL_CSS = """
.dbl-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px;max-width:100%}
.dbl-board .controls input{width:7.5em}
table.dbl td{font-family:var(--mono);font-size:13.5px;word-break:break-all}
table.dbl tr.tick td{background:var(--wash);font-weight:700}
table.dbl tr.tick td:last-child{color:var(--red)}
table.dbl tr.now td{outline:2px solid var(--blue);outline-offset:-2px}
.dbl-board .steps li{font-size:12.5px}
"""

DBL_JS = r"""
(() => {
  const body = document.getElementById("db-rows");
  if (!body) return;
  let mode, A, B, rows, phase, cursor, left, log;
  const big = v => { const s = v.toString(); return s.length > 24 ? s.slice(0, 10) + "…" + s.slice(-6) + ` (${s.length} digits)` : s.replace(/\B(?=(\d{3})+(?!\d))/g, ","); };
  function reset() {
    mode = document.getElementById("db-mode").value;
    A = Math.max(1, Math.min(mode === "pow" ? 4096 : 1000000, Math.floor(+document.getElementById("db-a").value || 1)));
    B = BigInt(Math.max(1, Math.min(1000000, Math.floor(+document.getElementById("db-b").value || 1))));
    rows = [[1, B]]; phase = "build"; cursor = -1; left = A; log = [`Write 1 and ${big(B)}.`];
    document.getElementById("db-head").textContent = mode === "pow" ? "Right column (squared)" : "Right column (doubled)";
    draw();
  }
  function step() {
    if (phase === "build") {
      const [m, v] = rows[rows.length - 1];
      if (m * 2 <= A) {
        const nv = mode === "pow" ? v * v : v + v;
        rows.push([m * 2, nv]);
        log.push(mode === "pow" ? `Square: ${m * 2} → ${big(nv)}.` : `Double both: ${m * 2} and ${big(nv)}.`);
      } else { phase = "tick"; cursor = rows.length; log.push(`The next doubling, ${m * 2}, would pass ${fmt(A)}. Now tick rows from the bottom.`); }
      return true;
    }
    if (phase === "tick") {
      cursor--;
      if (cursor < 0) { phase = "done"; return false; }
      const m = rows[cursor][0];
      if (m <= left) { rows[cursor].push(true); left -= m; log.push(`${m} fits in ${fmt(left + m)}: tick it; ${fmt(left)} left.`); }
      else log.push(`${m} does not fit in ${fmt(left)}.`);
      if (cursor === 0) phase = "done";
      return true;
    }
    return false;
  }
  function draw() {
    body.innerHTML = "";
    rows.forEach(([m, v, t], i) => {
      const tr = el("tr", {class: (t ? "tick " : "") + (i === cursor && phase !== "build" ? "now" : "")}, body);
      el("td", {class: "n"}, tr, fmt(m)); el("td", {class: "n"}, tr, big(v)); el("td", {}, tr, t ? "✓" : "");
    });
    const lg = document.getElementById("db-log");
    lg.innerHTML = "";
    log.slice(-8).forEach((t, i, arr) => el("li", {class: i === arr.length - 1 ? "current" : ""}, lg, t));
    const res = document.getElementById("db-result");
    if (phase === "done") {
      const ticked = rows.filter(r => r[2]);
      const total = mode === "pow" ? ticked.reduce((p, r) => p * r[1], 1n) : ticked.reduce((s, r) => s + r[1], 0n);
      const check = mode === "pow" ? B ** BigInt(A) : B * BigInt(A);
      const ops = rows.length - 1 + ticked.length - 1;
      res.innerHTML = `${mode === "pow" ? "Multiply" : "Add"} the ticked rows: <b>${big(total)}</b> ${total === check ? "✓" : "✗"}. ` +
        `${ops} ${mode === "pow" ? "squarings and multiplications" : "doublings and additions"}, against ${fmt(A - 1)} by ${mode === "pow" ? "multiplying" : "adding"} one at a time. ` +
        `The ticks spell ${fmt(A)} in binary: ${A.toString(2)}.`;
    } else res.textContent = "";
  }
  document.getElementById("db-step").addEventListener("click", () => { step(); draw(); });
  document.getElementById("db-all").addEventListener("click", () => { let guard = 0; while (phase !== "done" && guard++ < 200) step(); draw(); });
  document.getElementById("db-reset").addEventListener("click", reset);
  ["db-mode", "db-a", "db-b"].forEach(id => document.getElementById(id).addEventListener("change", reset));
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 660, "How doubling combined with other ideas, from grouped numerals to RSA")
    W, H = 210, 86
    nodes = {
        "grp": (395, 20, "Adding grouped signs", "", "topic 2", "ink"),
        "dbl": (395, 150, "Multiply by doubling", "⊕ double, then add the rows", "Rhind papyrus, c. 1550 BCE", "red"),
        "div": (30, 300, "Divide by doubling", "⊕ double the divisor", "Rhind papyrus", "ink"),
        "pea": (395, 300, "Halving and doubling", "⊕ halve the other number", "'Russian peasant' (conjecture)", "ink"),
        "sqm": (760, 300, "Square and multiply", "⊕ × in place of +", "Pingala to al-Kashi", "red"),
        "euc": (30, 440, "Euclid's division step", "same question: how many times?", "topic 7", "ink"),
        "gen": (760, 440, "The generic power", "⊕ any associative operation", "Stepanov", "blue"),
        "fib": (530, 560, "Fast Fibonacci", "⊕ 2 × 2 matrices", "", "blue"),
        "rsa": (770, 560, "RSA", "⊕ arithmetic mod n", "1977", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("grp", "dbl", ports=("bottom", "top"))
    D.edge("dbl", "div", ports=("bottom", "top"))
    D.edge("dbl", "pea", ports=("bottom", "top"), dashed=True)
    D.edge("dbl", "sqm", ports=("bottom", "top"))
    D.edge("div", "euc", ports=("bottom", "top"), dashed=True)
    D.edge("sqm", "gen", ports=("bottom", "top"))
    D.edge("gen", "fib", ports=("bottom:0.25", "top"))
    D.edge("gen", "rsa", ports=("bottom:0.6", "top"))
    return D


def chain(d):
    gr = d["generic"]
    c15 = d["c15"]
    steps = [
        (f"No times table: {d['a']} × {d['b']} by repeated adding takes {d['repeat']} additions",
         f"Double {d['b']} five times and add the ticked rows: {d['doublings']} doublings and {d['additions']} additions", "Rhind papyrus, c. 1550 BCE"),
        ("Dividing: how many times does one number fit in another?", "Double the divisor and pick rows from the top", "Rhind papyrus"),
        ("Powers: 2790 to the power 2753 means 2,752 multiplications", f"Square and multiply: {gr['rsa'][1]} multiplications", "Pingala to al-Kashi"),
        (f"Doubling is not always shortest: 15 takes {c15['binary_n']} steps", f"Search for a shorter chain: {c15['short']} ({c15['short_n']} steps)", "addition chains"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from repeated adding to addition chains")
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


def ticks(d):
    rows = d["rows"]
    D = Diagram(1000, 280, f"{d['a']} × {d['b']}: the ticked rows add up to the answer")
    n = len(rows)
    for i, (m, v, t) in enumerate(rows):
        D.node(i, 20 + i * 162, 40, 138, 70, [(f"{m}", "big"), (f"{v:,}", "combo")], color="red" if t else "ink", weight=3 if t else 1.2)
    D.text(20, 26, f"LEFT COLUMN DOUBLES FROM 1; RIGHT COLUMN DOUBLES FROM {d['b']}", "tag")
    ticked = [(i, m, v) for i, (m, v, t) in enumerate(rows) if t]
    D.node("sum", 260, 190, 480, 70, [(" + ".join(str(m) for _, m, _ in sorted(ticked, key=lambda x: -x[1])) + f" = {d['a']}", "title"),
                                        (" + ".join(f"{v:,}" for _, _, v in sorted(ticked, key=lambda x: -x[1])) + f" = {d['product']:,}", "combo")], color="red")
    for i, m, v in ticked:
        D.edge(i, "sum", ports=("bottom", "top"))
    return D


def generic(d):
    g = d["generic"]
    D = Diagram(1000, 330, "One algorithm, four operations: the doubling table with a different 'add'")
    D.node("alg", 300, 20, 400, 84, [("THE DOUBLING TABLE", "tag"), ("Combine x with itself again and again; combine the rows you need", "combo")])
    items = [("plus", 20, "+ on numbers", "multiplication", f"59 × 41: {g['plus'][1]} additions"),
             ("times", 265, "× on numbers", "powers", f"3 to the 41: {g['times'][1]} multiplications"),
             ("fib", 510, "× on 2 × 2 matrices", "Fibonacci numbers", f"F(90): {g['fib'][1]} matrix products"),
             ("rsa", 755, "× modulo n", "RSA decryption", f"2790^2753 mod 3233: {g['rsa'][1]}")]
    for k, x, t, what, n in items:
        D.node(k, x, 200, 225, 100, [(t, "title"), (what, "combo"), (n, "note")], color="blue" if k != "plus" else "red")
        D.edge("alg", k, ports=("bottom", "top"))
    return D


def chains15(d):
    c = d["c15"]
    D = Diagram(1000, 240, "Two addition chains for 15: doubling and adding, and the shortest")
    rows = [("b", 40, "DOUBLING AND ADDING", [int(x) for x in c["binary"].split(", ")], "ink"),
            ("s", 150, "THE SHORTEST", [int(x) for x in c["short"].split(", ")], "red")]
    for key, y, tag, nums, color in rows:
        D.text(20, y - 10, tag + f": {len(nums) - 1} STEPS", "tag")
        for i, v in enumerate(nums):
            D.node(f"{key}{i}", 20 + i * 136, y, 96, 52, [(str(v), "big")], color=color)
            if i:
                D.edge(f"{key}{i - 1}", f"{key}{i}", ports=("right", "left"))
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    js = DBL_JS
    html = DBL_HTML.replace("AV", str(d["a"])).replace("BV", str(d["b"]))
    g = d["generic"]
    sq, mu, tot, digits = d["rsa2048"]
    ch = d["chains"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Here adding (topic 2) is combined with itself: double, double again, and add only the rows you need. Swap the addition for multiplication and the same table computes powers. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the Egyptian method, and square-and-multiply, which reuses its idea with × in place of +. Blue: where it went next. Dashed: a likely relative, not a proven descendant."),
        ]),
        dict(id="dbl", eyebrow="Try it", title="Double, then tick", toc="Try it", blocks=[
            dict(type="p", text=f"Write 1 beside {d['b']}. Double both, again and again, while the left column stays at most {d['a']}. Then, from the bottom, tick each row whose left number still fits into what is left of {d['a']}. Add the ticked right numbers. Switch the rule to square-and-multiply and the same steps compute a power."),
            dict(type="widget", html=html, js=js, css=DBL_CSS,
                 fallback=dict(type="table", head=["Left column", "Right column", "Tick"], num=[0, 1],
                               rows=[[m, f"{v:,}", "✓" if t else ""] for m, v, t in d["rows"]]),
                 note="In the interactive edition you can build the table for any numbers, by doubling or by squaring."),
            dict(type="diagram", name="ticks", diagram=ticks(d)),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="steps", eyebrow="Step by step", title="Multiplying and dividing with one table", toc="Step by step", blocks=[
            dict(type="table", head=["Left column", "Right column", "Ticked?", "Why"], num=[0, 1], hl=None,
                 rows=[[m, f"{v:,}", "✓" if t else "", "part of " + str(d["a"]) if t else ""] for m, v, t in d["rows"]]),
            dict(type="p", text=f"{d['a']} = {' + '.join(str(m) for m, v, t in reversed(d['rows']) if t)}, so {d['a']} × {d['b']} = {' + '.join(f'{v:,}' for m, v, t in reversed(d['rows']) if t)} = **{d['product']:,}**: "
                                f"{d['doublings']} doublings and {d['additions']} additions, where adding {d['b']} again and again takes {d['repeat']}."),
            dict(type="p", text="Division runs the same table the other way: double the divisor while it fits, then take rows from the biggest down. The quotient is the sum of the left numbers taken."),
            dict(type="table", head=["Division", "Quotient", "Remainder", "Rows in the table"], num=[1, 2, 3],
                 rows=[[f"{a:,} ÷ {b}", q, r, n] for a, b, q, r, n in d["divide"]]),
            dict(type="callout", kind="key", label="Key idea",
                 text="The ticked rows are the binary digits of the multiplier: MacTutor calls the method \"a very early use of binary arithmetic\". That is a modern reading. The scribes had no idea of base 2; they only needed to double and to add."),
        ]),
        dict(id="generic", eyebrow="Before and after", title="One table, any operation", toc="Any operation", blocks=[
            dict(type="p", text="The table works for any operation that can be regrouped freely (an associative one). Alexander Stepanov, who designed C++'s Standard Template Library, built a course on this idea, from the Egyptian method to the generic power algorithm. The program runs the same code four times. "
                                "(A 2 × 2 matrix is a square of four numbers that can be multiplied like a single number; *mod n* means keeping only the remainder after dividing by n.)"),
            dict(type="diagram", name="generic", diagram=generic(d)),
            dict(type="table", head=["Operation", "Result", "Steps", "One at a time"], num=[2, 3],
                 rows=[["41 copies of 59 added together", g["plus"][0], g["plus"][1], 40],
                       ["3 to the power 41 (41 copies of 3 multiplied)", g["times"][0], g["times"][1], 40],
                       ["Fibonacci number 90, by 2 × 2 matrix powers", g["fib"][0], g["fib"][1], 89],
                       ["RSA: 2790^2753 mod 3233", "65", g["rsa"][1], "2,752"]]),
        ]),
        dict(id="measured", eyebrow="Measured", title="How many steps?", toc="Measured", blocks=[
            dict(type="table", head=["Multiplier", "Doubling and adding", "Adding one at a time"], num=[0, 1, 2],
                 rows=[[f"{n:,}", a, f"{r:,}"] for n, a, r in d["steps"]]),
            dict(type="p", text=f"Over {d['mc']['n']:,} random pairs below a million, the program checked doubling, and the halving-and-doubling form (halve one number, double the other), against ordinary multiplication. The method needed **{d['mc']['avg']}** doublings and additions on average, against {d['mc']['rep']} additions one at a time."),
            dict(type="p", text=f"Doubling is not always the shortest route. An *addition chain* builds a number from 1, each step adding two numbers already made. For 15, doubling and adding needs {d['c15']['binary_n']} steps; the shortest chain needs {d['c15']['short_n']}:"),
            dict(type="diagram", name="chains15", diagram=chains15(d)),
            dict(type="p", text=f"The program searched every number up to 128: doubling and adding is beaten for **{ch['n']}** of them, starting with {', '.join(ch['first'][:8])}."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The scribe's table inside every secure connection", toc="Full circle", blocks=[
            dict(type="p", text="RSA encryption needs powers of huge numbers modulo another huge number. A course note from the University of Alaska Fairbanks puts the link in one line: \"replacing + with * gives the fast exponentiation by squaring trick\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"For a random 2048-bit exponent the program counts **{sq:,} squarings and {mu:,} multiplications**, {tot:,} in all. Multiplying one at a time would take a number of steps with {digits} digits. The same doubling idea as the Rhind papyrus's table makes it possible."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Multiply 13 × 24 by doubling.", "Rows: 1 24, 2 48, 4 96, 8 192. 13 = 8 + 4 + 1, so add 192 + 96 + 24 = **312**."),
            (f"Why does {d['a']} need exactly {len(d['rows'])} rows?", f"The left column must reach the biggest power of two not above {d['a']}, which is {d['rows'][-1][0]}: rows 1, 2, 4, …, {d['rows'][-1][0]}."),
            ("Divide 1,000 by 7 by doubling the divisor.", "".join(f"Double 7 while it fits: 7, 14, …, 896 ({n} rows). Taking rows from the top gives quotient **{q}**, remainder **{r}**." for a, b, q, r, n in d["divide"] if (a, b) == (1000, 7))),
            ("How do you get 3 to the power 41 with 7 multiplications?", "Square 3 five times: 3, 3², 3⁴, 3⁸, 3¹⁶, 3³². Then multiply the rows for 32, 8 and 1: two more multiplications."),
            ("Is doubling and adding always the fastest way to build a number?", f"No. 15 takes {d['c15']['binary_n']} steps by doubling ({d['c15']['binary']}) but {d['c15']['short_n']} by the chain {d['c15']['short']}."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Rhind Mathematical Papyrus", text="Copied by the scribe Ahmose (also spelled Ahmes) from an older text, about 1550 BCE (other sources: c. 1650). 84 problems. British Museum EA10057 and EA10058.",
                 draw=C.draw_papyrus, link="https://www.britishmuseum.org/collection/object/Y_EA10057", link_text="British Museum record",
                 licence="Drawn placeholder; the museum's photographs are at the link."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "EgyptianDoubling", d["checks"],
                           f"doubling and halving-and-doubling against ordinary multiplication on {d['mc']['n']:,} random pairs, division by doubling on 200,000 more, the generic power on four operations, and a search for the shortest addition chain of every number up to 128.",
                           ["static List<Row> table(long a, long b)", "static <T> T power(T x, long n, BinaryOperator<T> op)"]),
    ]
    return dict(
        title="Egyptian Doubling", date="c. 1550 BCE",
        description="Era 1, topic 5 of The Algorithm Evolution Atlas: multiplication by doubling from the Rhind papyrus, and how the same table became square-and-multiply and RSA.",
        lede="No times table, only two skills: doubling and adding. The scribe's table quietly writes the multiplier in binary, and with one swap it computes powers.",
        fieldnote="These scribes had no times table. To multiply, say, 41 by 59, a scribe doubled 59 again and again and added the rows whose multipliers make 41. They never named base 2, yet every multiplication split the multiplier into powers of two.",
        card=[("When", "Rhind papyrus, c. 1550 BCE, copied from an older text (dates differ: **disputed**)"),
              ("Where", "Egypt · British Museum (**documented**)"),
              ("What hurt", "Multiplying with additive numerals and no times table"),
              ("The fix", "Double and add: about log₂ n rows (the number of times n can be halved)"),
              ("Cost", f"{d['a']} × {d['b']}: {d['doublings'] + d['additions']} steps instead of {d['repeat']}"),
              ("Atlas", "Ch. 2 Egyptian Algorithms · Ch. 94 Exponentiation")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `EgyptianDoubling.java`.",
    )
