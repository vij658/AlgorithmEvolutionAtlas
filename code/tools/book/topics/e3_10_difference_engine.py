"""Era 3, topic 10: Babbage's difference engine. Every number is parsed from DifferenceEngine.java's output."""
import re

import common as C
from diagrams import Diagram

sci = C.sci


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"babbage: .*? starts with value (\d+), first difference (\d+), second difference (\d+) \(constant\) ; .*? the table: (.+?), \.\.\. ; .*? prime for x = 0 to (\d+), then (\d+) = 41 x 41 at x = (\d+)$", ln):
            d["b"] = dict(v=m.group(1), d1=m.group(2), d2=m.group(3), table=m.group(4).split(", "), primes=m.group(5), comp=m.group(6), at=m.group(7))
        elif m := re.match(r"orders: ([\d,]+) random polynomials of degree 1 to 7", ln):
            d["orders"] = m.group(1)
        elif m := re.match(r"logs: .*? for x = ([\d,]+) to ([\d,]+), by a seventh-order engine restarted from exact values every (\d+) entries ; ([\d,]+) entries printed, (\d+) differ .*? ; largest error before rounding (\S+) ; ([\d,]+) additions in all, (\S+) per entry$", ln):
            g = m.groups()
            d["logs"] = dict(frm=g[0], to=g[1], span=g[2], n=g[3], wrong=g[4], err=g[5], adds=g[6], per=g[7])
        elif m := re.match(r"work: (.+)$", ln):
            d["work"] = re.findall(r"degree (\d+): the engine (\d+) additions per entry ; Horner's rule (\d+) multiplications and (\d+) additions", m.group(1))
        elif m := re.match(r"misprint: .*? printed as (\d+) instead of (\d+) ; .*?: (.+?) ; the pattern", ln):
            d["mis"] = dict(bad=m.group(1), good=m.group(2), d3=m.group(3).split(", "))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def engine_diagram(d):
    b = d["b"]
    D = Diagram(1000, 260, "Babbage's model on x² + x + 41: three columns, and each turn of the handle is two additions")
    W, H = 220, 120
    cols = [("v", "Value", [f"starts at {b['v']}", "prints the table", "+= first difference"], "red"),
            ("d1", "First difference", [f"starts at {b['d1']}", "2, 4, 6, 8, …", "+= second difference"], "ink"),
            ("d2", "Second difference", [f"always {b['d2']}", "constant for degree 2", "never changes"], "ink")]
    for i, (k, t, sub, col) in enumerate(cols):
        D.node(k, 20 + i * 260, 50, W, H, [(t, "title")] + [(s, "combo" if j == 0 else "note") for j, s in enumerate(sub)], color=col)
    D.edge("d2", "d1", ports=("left", "right"), label="add")
    D.edge("d1", "v", ports=("left", "right"), label="add")
    D.node("out", 800, 50, 180, H, [("Printed", "title"), (", ".join(b["table"][:5]), "combo"), (", ".join(b["table"][5:]) + ", …", "note")], color="ink")
    D.edge("v", "out", ports=("right", "left"), dashed=True)
    D.text(20, 30, "NO MULTIPLICATION ANYWHERE: THE WHEELS ONLY ADD", "tag")
    D.text(20, 210, f"Every value is prime up to x = {b['primes']}; at x = {b['at']} the engine prints {b['comp']} = 41 × 41. The engine does not know: it only adds.", "caption")
    D.text(20, 228, "Numbers from DifferenceEngine.java.", "caption")
    return D


DE_HTML = """
<div class="board de-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="de-p">Polynomial <select id="de-p">
        <option value="0" selected>x² + x + 41 (Babbage's model)</option>
        <option value="1">x³ (cubes)</option>
        <option value="2">x⁴ − 6x² + 3</option>
      </select></label>
    </div>
    <div class="de-cols" id="de-cols"></div>
    <div class="controls">
      <button type="button" id="de-turn">Turn the handle</button>
      <button type="button" id="de-ten">Turn 10 times</button>
      <button type="button" id="de-reset">Reset</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The printed table</div>
    <div class="de-table" id="de-table"></div>
    <p class="say" id="de-say" aria-live="polite"></p>
  </div>
</div>
"""

DE_CSS = """
.de-board .controls{flex-wrap:wrap}
.de-cols{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:8px;margin:10px 0}
.de-col{border:2px solid var(--ink-2);padding:8px 6px;text-align:center;background:var(--surface)}
.de-col .h{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.de-col .n{font-family:var(--mono);font-size:clamp(15px,3.6vw,22px);margin-top:4px;overflow-wrap:anywhere}
.de-col.hot{border-color:var(--red)}
.de-table{font-family:var(--mono);font-size:13px;line-height:1.6;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:18px}
.de-table .p{color:var(--blue)}
.de-table .c{color:var(--red);font-weight:700}
.de-board .say{font-size:14.5px}
"""

DE_JS = r"""
(() => {
  const host = document.getElementById("de-cols");
  if (!host) return;
  const P = [x => x * x + x + 41, x => x ** 3, x => x ** 4 - 6 * x * x + 3], DEG = [2, 3, 4];
  const NAMES = ["value", "1st difference", "2nd", "3rd", "4th"];
  let col = [], x = 0, rows = [];
  const isPrime = n => { if (n < 2) return false; for (let d = 2; d * d <= n; d++) if (n % d === 0) return false; return true; };
  function setup() {
    const k = +document.getElementById("de-p").value, f = P[k], n = DEG[k];
    let row = []; for (let i = 0; i <= n; i++) row.push(f(i));
    col = [];
    for (let j = 0; j <= n; j++) { col.push(row[0]); const nx = []; for (let i = 0; i + 1 < row.length; i++) nx.push(row[i + 1] - row[i]); row = nx; }
    x = 0; rows = [[0, col[0]]]; draw(-1);
  }
  function draw(hot) {
    host.innerHTML = "";
    col.forEach((v, j) => { const c = el("div", { class: "de-col" + (j <= hot ? " hot" : "") }, host); el("div", { class: "h" }, c, NAMES[j]); el("div", { class: "n" }, c, v.toLocaleString("en-US")); });
    const k = +document.getElementById("de-p").value, t = document.getElementById("de-table");
    t.innerHTML = rows.slice(-24).map(([xx, v]) => k === 0 ? `<div class="${isPrime(v) ? "p" : "c"}">x = ${xx}: ${v}</div>` : `<div>x = ${xx}: ${v.toLocaleString("en-US")}</div>`).join("");
    const say = document.getElementById("de-say");
    const ok = rows.every(([xx, v]) => v === P[k](xx));
    say.textContent = (k === 0 ? (rows.some(([, v]) => !isPrime(v)) ? `At x = 40 the engine prints 1681 = 41 × 41, the first value that is not prime (shown in red). ` : "Blue: prime. ") : "") +
      `${DEG[k]} additions per turn, no multiplication${ok ? "; every value checked against the polynomial" : ""}.`;
  }
  function turn() { for (let j = 0; j < col.length - 1; j++) col[j] += col[j + 1]; x++; rows.push([x, col[0]]); }
  document.getElementById("de-turn").addEventListener("click", () => { turn(); draw(col.length - 1); });
  document.getElementById("de-ten").addEventListener("click", () => { for (let i = 0; i < 10; i++) turn(); draw(col.length - 1); });
  document.getElementById("de-reset").addEventListener("click", setup);
  document.getElementById("de-p").addEventListener("change", setup);
  setup();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the difference engine combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "tab": (20, 20, "Printed tables", "logarithms, navigation", "topic 2", "ink"),
        "dif": (395, 20, "Finite differences", "constant at the nth order", "Briggs used them, topic 2", "ink"),
        "car": (770, 20, "Wheels that carry", "addition in brass", "topic 3", "ink"),
        "de": (395, 170, "The difference engine", "⊕ a column of adders that prints its own table", "Babbage, 1822", "red"),
        "ae": (20, 330, "The Analytical Engine", "a store, a mill, and cards", "topic 11", "ink"),
        "de2": (395, 330, "Difference Engine No. 2", "designed 1847–1849", "built 1991; printer 2002", "blue"),
        "chk": (770, 330, "Checking tables", "differences expose misprints", "table makers", "ink"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("tab", "de", ports=("bottom", "top:0.15"))
    D.edge("dif", "de", ports=("bottom", "top"))
    D.edge("car", "de", ports=("bottom", "top:0.85"))
    D.edge("de", "ae", ports=("bottom:0.1", "top:0.7"))
    D.edge("de", "de2", ports=("bottom", "top"))
    D.edge("dif", "chk", ports=("right", "left:0.3"), dashed=True)
    D.text(20, 615, "Briggs's use of differences is from Roegel (topic 2); the dashed line marks an old use of differences, not a link through Babbage.", "caption")
    return D


def chain(d):
    lg, m = d["logs"], d["mis"]
    steps = [
        ("Printed tables full of errors, from computing and from copying into type",
         "Generate the table by additions only, with wheels; print it from the wheels", "Babbage, 1822"),
        ("Real tables (logarithms) are not polynomials",
         f"A polynomial for each stretch, restarted from exact values: {lg['n']} entries, {lg['wrong']} wrong", "the method of differences"),
        ("Engine No. 1 stopped in 1833 with about a seventh built",
         "Difference Engine No. 2, built by the Science Museum, works as Babbage intended", "1991; printer 2002"),
        ("A machine that only adds makes only one kind of table",
         "A general machine with a store, a mill, and cards for instructions", "the Analytical Engine, topic 11"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from tables by hand to a general machine")
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
    b, lg, m = d["b"], d["logs"], d["mis"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The world ran on printed tables (topic 2), whose makers had long used differences to speed and check their work; the carry had been put into wheels (topic 3). Babbage saw that the method of differences needs nothing but addition, and addition is what wheels do. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the difference engine. Blue: the engine built to Babbage's later design."),
        ]),
        dict(id="engine", eyebrow="Try it", title="Turn the handle", toc="Try it", blocks=[
            dict(type="p", text="Each column holds one number: the value, then its differences. A turn of the handle adds each column into the one to its left, and the value column prints the next entry of the table. Start with Babbage's x² + x + 41 and turn past x = 40. Then try a cubic and a quartic: they need more columns, but still only additions."),
            dict(type="widget", html=DE_HTML, js=DE_JS, css=DE_CSS,
                 fallback=dict(type="diagram", name="model", diagram=engine_diagram(d)),
                 note="In the interactive edition you can turn the handle on three polynomials and watch the table print."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Constant differences", toc="How it works", blocks=[
            dict(type="p", text="List a polynomial's values at x = 0, 1, 2, …, and subtract neighbours: the first differences. Subtract again: the second differences. For a polynomial of degree n, the nth differences never change. Run the table backwards and every new value needs only n additions:"),
            dict(type="diagram", name="model-steps", diagram=engine_diagram(d)),
            dict(type="p", text=f"Babbage's first model had two orders of difference and made \"a table from the formula x² + x + 41\". The program repeats it: {', '.join(b['table'])}, …, every value checked against the formula. It also ran engines of every order up to 7 on {d['orders']} random polynomials, 200 values each, all exact."),
            dict(type="p", text=f"**Tables that are not polynomials.** A logarithm is not a polynomial, but over a short stretch a polynomial imitates it closely. The program made a 7-place table of log₁₀ x for x = {lg['frm']} to {lg['to']} with a seventh-order engine, restarting from exact values every {lg['span']} entries: {lg['n']} entries, **{lg['wrong']}** different from the true rounded value; the largest error before rounding was {sci(lg['err'])}, using {lg['per']} additions per entry."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Reformulate the work so that it needs only the operation your machine does well. The method of differences turns multiplication-heavy tables into chains of additions, and then removes the person who copies the numbers into type."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Differences catch misprints", toc="Measured", blocks=[
            dict(type="p", text=f"Differences also check a finished table. The program printed x² + x + 41 for x = 0 to 11 with one entry wrong ({m['bad']} instead of {m['good']}). Its third differences should all be zero; instead they read {', '.join(m['d3'])}. The pattern 1, −3, 3, −1 times the error points straight at the bad entry."),
            dict(type="table", head=["Degree", "Engine: additions per entry", "Horner's rule: multiplications and additions"], num=[1, 2],
                 rows=[[a, b_, f"{c} and {e}"] for a, b_, c, e in d["work"]]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="By steam", toc="The evidence", blocks=[
            dict(type="p", text="Checking astronomical tables, Babbage exclaimed, \"I wish to God these calculations had been executed by steam\"; Herschel replied, \"It is quite possible.\" On 14 June 1822 he announced a finished model, \"limited ... to two orders of differences\", that made tables \"of square and triangular numbers, as well as a table from the singular x² + x + 41\" (James, I Programmer). In his letter to Davy he reported thirty numbers in \"two minutes and thirty seconds\" and, in another trial, figures \"at the rate of forty-four in a minute\". Difference Engine No. 1, built with Joseph Clement, stopped in 1833 after a dispute over compensation, with about a seventh assembled."),
            dict(type="p", text="Difference Engine No. 2 was designed in 1847–1849. The Science Museum's calculating section \"was finished in 1991 in time for the bicentenary of Babbage's birth\", and \"the printing and stereotyping apparatus was completed in 2002\": 8,000 parts, five tons. \"The completed machine works as Babbage intended\" (Computer History Museum). The cost of Engine No. 1 to the government, often quoted, was not found in an opened source."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A machine finished in 1991", toc="Full circle", blocks=[
            dict(type="p", text="Babbage never saw a difference engine complete. The one in the Science Museum was built from his drawings with the tolerances of his day, to settle whether his design could have worked."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="It does: designed in 1847–1849, calculating in 1991, printing in 2002. And the idea outlived the machine. Stepping a polynomial forward by additions alone is still how a computer can walk along a curve without multiplying, and differences still expose a wrong entry in a table, exactly as the program found the misprinted 93."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What are the first differences of 41, 43, 47, 53, 61?", "2, 4, 6, 8: and their differences, 2, 2, 2, are constant."),
            ("Why does a cubic need four columns?", "Its third differences are constant, so the engine holds the value and three differences."),
            ("Why must the logarithm engine restart every so often?", "Its polynomial only imitates the logarithm over a short stretch; small errors in the differences grow with every turn."),
            ("How does one misprint show in the third differences?", "As the error times 1, −3, 3, −1: the binomial coefficients, centred on the bad entry."),
            ("What does x² + x + 41 give at x = 40?", "40² + 40 + 41 = 1681 = 41 × 41: the first value that is not prime."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Difference Engine No. 2", text="Built by the Science Museum from Babbage's designs of 1847–1849: calculating section 1991, printer 2002.",
                 draw=C.draw_board, link="https://collection.sciencemuseumgroup.org.uk/objects/co62748", link_text="Science Museum Group",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "DifferenceEngine", d["checks"],
                           "every value of Babbage's x² + x + 41 to x = 50, 2,000 random polynomials of degree up to 7 for 200 values each, a 9,000-entry table of 7-place logarithms against the true rounded values, and the misprint pattern.",
                           ["BigInteger turn(", "static BigInteger[] setUp("]),
    ]
    return dict(
        title="Babbage's Difference Engine", date="1822",
        description="Era 3, topic 10 of The Algorithm Evolution Atlas: Babbage's difference engine, tables by additions only, x² + x + 41, a logarithm table by differences, and the engine built in 1991.",
        lede="The world ran on printed tables, and the tables were full of mistakes. Babbage noticed that a polynomial's table can be made by additions alone, and that wheels can add. He designed a machine to compute the table and print it, so that no person ever copied a number.",
        fieldnote="Until now every table I have recorded was computed by people and set in type by people, and errors crept in at both steps. Babbage's answer removed the people from both, and his engine was finished by others, from his drawings, in 1991.",
        card=[("When", "1821–1822; Engine No. 2 designed 1847–1849, built 1991"),
              ("Where", "London"),
              ("What hurt", "Printed tables full of errors"),
              ("The fix", "Constant differences: every entry by additions, printed by the machine"),
              ("Cost", "n additions per entry for a polynomial of degree n")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `DifferenceEngine.java`.",
    )
