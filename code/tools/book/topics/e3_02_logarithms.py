"""Era 3, topic 2: logarithms. Every number is parsed from Logarithms.java's output."""
import re

import common as C
from diagrams import Diagram

sci, pretty = C.sci, C.pretty


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"multiply: (.+)$", ln):
            d["mult"] = [dict(a=g[0], b=g[1], la=g[2], lb=g[3], s=g[4], back=g[5], exact=g[6], rel=g[7]) for g in
                         re.findall(r"(\d+) x (\d+): (\S+) \+ (\S+) = (\S+) -> (\d+) \(exact (\d+), relative error (\S+)\)", m.group(1))]
        elif m := re.match(r"precision: .*? ; (\d+ places.+)$", ln):
            d["prec"] = [dict(places=g[0], worst=g[1], avg=g[2]) for g in re.findall(r"(\d+) places: worst relative error (\S+), average (\S+?)(?: ;|$)", m.group(1))]
        elif m := re.match(r"roots: (.+?) ; the excess over 1 after 54 roots is (\S+), and its logarithm is exactly 1/2\^54 = (\S+)$", ln):
            d["roots"] = [(int(a), v) for a, v in re.findall(r"root (\d+): (\S+?)(?: ;|$)", m.group(1))]
            d["excess"], d["inv"] = m.group(2), m.group(3)
        elif m := re.match(r"briggs: (.+)$", ln):
            d["logs"] = [dict(x=g[0], v=g[1], true=g[2], k=g[3], dec=g[4]) for g in
                         re.findall(r"log (\d+) = (\S+) \(true (\S+) ; (\d+) roots of \d+ ; (\d+) correct decimals\)", m.group(1))]
        elif m := re.match(r"truth: log 2 = (\S+)$", ln):
            d["log2"] = m.group(1)
        elif m := re.match(r"depth: .*?: (.+)$", ln):
            d["depth"] = [(int(a), int(b)) for a, b in re.findall(r"(\d+) roots: (\d+)", m.group(1))]
        elif m := re.match(r"table: .*? has ([\d,]+) entries ; ([\d,]+) are prime .*?\(([\d,]+) below 20,000, ([\d,]+) above 90,000\) ; ([\d,]+) follow .*? ; ([\d,]+) have", ln):
            d["table"] = dict(entries=m.group(1), primes=m.group(2), small=m.group(3), big=m.group(4), sums=m.group(5), outside=m.group(6))
        elif m := re.match(r"underflow: the product of (\d+) probabilities .*? is (\S+) \(the smallest positive double is (\S+)\) ; the sum of their base-10 logarithms is (\S+),", ln):
            d["uf"] = dict(n=m.group(1), prod=m.group(2), min=m.group(3), log=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def roots_diagram(d):
    """Briggs's square roots of 10, closing in on 1."""
    D = Diagram(1000, 230, "Briggs's method: take the square root of ten again and again, until the number is next to 1")
    W, H = 150, 96
    picks = d["roots"]
    for i, (n, v) in enumerate(picks):
        D.node(f"r{i}", 20 + i * 162, 50, W, H, [(f"{n} root{'s' if n > 1 else ''}", "title"), (v[:14], "combo"), (v[14:], "note")],
               color="red" if n == 54 else "ink")
        if i:
            D.edge(f"r{i - 1}", f"r{i}", ports=("right", "left"))
    D.text(20, 30, "EACH SQUARE ROOT HALVES THE LOGARITHM: AFTER 54 ROOTS IT IS EXACTLY 1/2⁵⁴", "tag")
    D.text(20, 205, f"After 54 roots the number exceeds 1 by {sci(d['excess'])}; near 1 the logarithm is proportional to that excess. Numbers from Logarithms.java (40 digits).", "caption")
    return D


LG_HTML = """
<div class="board lg-board">
  <div style="min-width:0">
    <div class="eyebrow">Multiply by adding</div>
    <div class="controls">
      <label for="lg-a">a <input id="lg-a" type="number" min="1" max="99999" value="4567"></label>
      <label for="lg-b">b <input id="lg-b" type="number" min="1" max="99999" value="8912"></label>
      <label for="lg-p">table <select id="lg-p"><option value="4">4 places</option><option value="7" selected>7 places</option><option value="14">14 places</option></select></label>
    </div>
    <ol class="lg-steps" id="lg-steps"></ol>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">How Briggs made the table</div>
    <div class="controls"><label for="lg-n">Square roots of 10 <input id="lg-n" type="range" min="1" max="60" value="54"></label><span class="lg-nv" id="lg-nv"></span></div>
    <ol class="lg-steps" id="lg-briggs"></ol>
    <p class="say" id="lg-say" aria-live="polite"></p>
  </div>
</div>
"""

LG_CSS = """
.lg-board .controls{flex-wrap:wrap}
.lg-board input[type=number]{width:7em}
.lg-board input[type=range]{width:min(200px,45vw)}
.lg-nv{font-family:var(--mono);font-size:13px}
.lg-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.lg-steps li{overflow-wrap:anywhere}
.lg-steps .m{font-family:var(--mono);font-size:12.5px}
.lg-steps .m b{color:var(--red)}
.lg-board .say{font-size:14.5px}
"""

LG_JS = r"""
(() => {
  const st = document.getElementById("lg-steps");
  if (!st) return;
  const TRUE2 = "__LOG2__";
  const li = (ol, h) => { el("li", {}, ol).innerHTML = h; };
  function mult() {
    let a = Math.round(+document.getElementById("lg-a").value), b = Math.round(+document.getElementById("lg-b").value);
    a = Math.min(99999, Math.max(1, a || 1)); b = Math.min(99999, Math.max(1, b || 1));
    const P = +document.getElementById("lg-p").value, k = 10 ** P;
    const la = Math.round(Math.log10(a) * k) / k, lb = Math.round(Math.log10(b) * k) / k, s = la + lb;
    const ch = Math.floor(s), back = 10 ** s, exact = a * b, rel = Math.abs(back - exact) / exact;
    st.innerHTML = "";
    li(st, `look up log ${a} = <span class="m">${la.toFixed(P)}</span>`);
    li(st, `look up log ${b} = <span class="m">${lb.toFixed(P)}</span>`);
    li(st, `add: <span class="m">${s.toFixed(P)}</span> (whole part ${ch}: the product has ${ch + 1} digits)`);
    li(st, `look up the number whose log is ${(s - ch).toFixed(P)}, and shift by 10<sup>${ch}</sup>: <span class="m">${back.toFixed(P >= 7 ? 2 : 0)}</span>`);
    li(st, `exact product <span class="m">${exact.toLocaleString("en-US")}</span>; relative error <span class="m">${rel.toExponential(1)}</span>`);
  }
  const S = 10n ** 40n;
  const isqrt = n => { if (n < 2n) return n; let x = BigInt(Math.ceil(Math.sqrt(Number(n)) * (1 + 1e-12))) + 1n; for (;;) { const y = (x + n / x) >> 1n; if (y >= x) return x; x = y; } };
  const sq = v => isqrt(v * S);
  const r10 = [10n * S]; for (let i = 1; i <= 60; i++) r10.push(sq(r10[i - 1]));
  const dec = (v, n) => { const s = v.toString().padStart(41, "0"); return s.slice(0, -40) + "." + s.slice(-40, -40 + n); };
  function briggs() {
    const n = +document.getElementById("lg-n").value;
    document.getElementById("lg-nv").textContent = n;
    const d10 = r10[n] - S;
    let rx = 2n * S, k = 0;
    while (rx - S > d10) { rx = sq(rx); k++; }
    const l2 = (rx - S) * S * (2n ** BigInt(k)) / (d10 * 2n ** BigInt(n));
    const s = dec(l2, 20);
    let c = 0; while (c < 20 && s[2 + c] === TRUE2[2 + c]) c++;
    const ol = document.getElementById("lg-briggs"); ol.innerHTML = "";
    li(ol, `after ${n} square roots, 10 has become <span class="m">${dec(r10[n], 22)}</span>; its log is 1/2<sup>${n}</sup>`);
    li(ol, `take ${k} square roots of 2 to come as close to 1: <span class="m">${dec(rx, 22)}</span>`);
    li(ol, `proportion: log 2 ≈ (excess of 2's root) ÷ (excess of 10's root) × 2<sup>${k}</sup>/2<sup>${n}</sup>`);
    li(ol, `<span class="m"><b>${s.slice(0, 2 + c)}</b>${s.slice(2 + c)}</span>`);
    document.getElementById("lg-say").textContent = `${c} decimal${c === 1 ? "" : "s"} agree with the true log 2. Each extra square root of 10 makes the proportion more accurate; Briggs stopped at 54 and printed 14 decimals.`;
  }
  ["lg-a", "lg-b", "lg-p"].forEach(id => document.getElementById(id).addEventListener("input", mult));
  document.getElementById("lg-p").addEventListener("change", mult);
  document.getElementById("lg-n").addEventListener("input", briggs);
  mult(); briggs();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family(d):
    D = Diagram(1000, 640, "How logarithms combined older ideas, and where they went")
    W, H = 210, 86
    nodes = {
        "dbl": (20, 20, "Doubling", "multiply powers, add exponents", "Egypt, Era 1 topic 5", "ink"),
        "chd": (395, 20, "Tables for astronomy", "chords and sines, looked up", "Ptolemy, Era 2 topic 2", "ink"),
        "dec": (770, 20, "Decimal fractions", "places after the point", "al-Kashi, Era 2 topic 11", "ink"),
        "log": (395, 170, "Logarithms", "⊕ add partners instead of multiplying numbers", "Napier 1614; Briggs 1624", "red"),
        "bon": (20, 330, "Napier's bones", "rods for multiplication", "Rabdologiae, 1617", "ink"),
        "dif": (395, 330, "The difference engine", "tables computed and printed by machine", "topic 10", "ink"),
        "flt": (770, 330, "Floating point", "a number as exponent and fraction", "today", "blue"),
        "llk": (770, 480, "Log-probabilities", "add logs, so products do not underflow", "statistics, machine learning", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("dbl", "log", ports=("bottom", "top:0.15"))
    D.edge("chd", "log", ports=("bottom", "top"))
    D.edge("dec", "log", ports=("bottom", "top:0.85"))
    D.edge("log", "bon", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("log", "dif", ports=("bottom", "top"))
    D.edge("log", "flt", ports=("bottom:0.9", "top:0.3"))
    D.edge("flt", "llk", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: Napier's bones are a separate invention by the same man, published three years later.", "caption")
    return D


def chain(d):
    t = d["table"]
    steps = [
        ("Astronomers and navigators spent nights on long multiplications",
         "A table of partners: add the partners instead of multiplying the numbers", "Napier, 1614"),
        ("Which partners? Powers of ten should be easy",
         "Base 10, with log 1 = 0 and log 10 = 1", "Napier and Briggs, 1615"),
        ("Every logarithm to 14 places, by hand",
         f"54 square roots of 10, then a proportion; only primes need it ({t['primes']} of {t['entries']} entries)", "Briggs, 1624"),
        ("Printed tables carry errors of computing and of typesetting",
         "Compute and print the table by machine", "Babbage, topic 10"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from long multiplication to machine-made tables")
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
    mu, pr, lg, dp, t, uf = d["mult"], d["prec"], d["logs"], d["depth"], d["table"], d["uf"]
    m0 = mu[0]
    js = LG_JS.replace("__LOG2__", d["log2"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Egyptian scribes multiplied by doubling (Era 1, topic 5), which hides a fact: multiplying powers of 2 means adding their exponents. Astronomers had long worked from printed tables (Era 2, topic 2), and decimal fractions had arrived (Era 2, topic 11). Napier made every number a power, so that every multiplication becomes an addition of exponents read from a table. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(d),
                 caption="Red: logarithms. Blue: where the idea lives in today's computers."),
        ]),
        dict(id="multiply", eyebrow="Try it", title="Multiply by adding, and build the table", toc="Try it", blocks=[
            dict(type="p", text="On the left, multiply two numbers the way a navigator would in 1630: look up two logarithms, add them, look up the answer. Change the table's precision to see the price of fewer decimals. On the right, repeat Briggs's construction: choose how many square roots of 10 to take, and watch how many decimals of log 2 come out right (the page computes with 40-digit whole numbers)."),
            dict(type="widget", html=LG_HTML, js=js, css=LG_CSS,
                 fallback=dict(type="diagram", name="roots", diagram=roots_diagram(d)),
                 note="In the interactive edition you can multiply any two numbers by look-up and addition, and choose how many square roots of 10 Briggs takes."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Partners that add", toc="How it works", blocks=[
            dict(type="p", text=f"**Using the table.** log(ab) = log a + log b. To multiply {m0['a']} by {m0['b']} with a 7-place table: log {m0['a']} = {m0['la']}, log {m0['b']} = {m0['lb']}, the sum is {m0['s']}, and the number with that logarithm is {int(m0['back']):,}. The exact product is {int(m0['exact']):,}: a relative error of {sci(m0['rel'])}, from the table's rounding. The program's examples:"),
            dict(type="table", head=["Product", "log a + log b", "Read back", "Exact", "Relative error"], num=[2, 3, 4],
                 rows=[[f"{x['a']} × {x['b']}", f"{x['la']} + {x['lb']} = {x['s']}", f"{int(x['back']):,}", f"{int(x['exact']):,}", sci(x["rel"])] for x in mu]),
            dict(type="p", text="**Making the table.** In base 10, log 10 = 1. A square root halves a logarithm, so the square root of 10 has logarithm ½, its square root ¼, and so on. Briggs took 54 square roots in a row:"),
            dict(type="diagram", name="roots-steps", diagram=roots_diagram(d)),
            dict(type="p", text=f"So close to 1, the logarithm is proportional to the excess over 1. To find log 2, take square roots of 2 until it is just as close to 1, compare the two excesses, and multiply back by the number of halvings. The program did exactly this with 40-digit arithmetic:"),
            dict(type="table", head=["Number", "By Briggs's method", "True value", "Roots of the number", "Correct decimals"], num=[3, 4],
                 rows=[[x["x"], x["v"], x["true"], x["k"], x["dec"]] for x in lg]),
            dict(type="p", text=f"Only primes need this work: log 6 = log 2 + log 3. A table of 1 to 20,000 and 90,001 to 100,000 (the ranges of Briggs's 1624 table, as Roegel gives them) has {t['entries']} entries; {t['primes']} are prime ({t['small']} below 20,000), {t['sums']} follow by adding logarithms of smaller entries, and {t['outside']} have a prime factor above 20,000 that is not in the table, and need more work."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do the hard work once, print it, and let everyone look it up. A table converts an expensive operation (multiplication) into a cheap one (addition) plus memory, the trade every cache and lookup table still makes."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Decimals cost square roots, and tables cost accuracy", toc="Measured", blocks=[
            dict(type="table", head=["Square roots of 10", "Correct decimals of log 2"], num=[0, 1], rows=[[str(a), str(b)] for a, b in dp]),
            dict(type="p", text="Each ten extra square roots buys three more decimals: the proportion's error shrinks as the root comes closer to 1. Briggs's 54 roots were enough for his 14 decimals."),
            dict(type="table", head=["Table precision", "Worst relative error", "Average relative error"], num=[1, 2],
                 rows=[[f"{x['places']} places", sci(x["worst"]), sci(x["avg"])] for x in pr]),
            dict(type="p", text="Twenty thousand random products of five-digit numbers, by look-up: the error is set by the table's last decimal, never by the arithmetic. A 4-place school table gives about four significant figures, a 14-place table about fourteen."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Twenty years, and a month in Edinburgh", toc="The evidence", blocks=[
            dict(type="p", text="\"Napier published his system in 1614, but he wrote that it took him some twenty years to invent it\" (Stewart, Gresham College). His *Rabdologiae* of 1617 described numbering rods made of ivory, \"Napier's bones\"; he died on 4 April 1617 (MacTutor). Henry Briggs, Gresham College's first professor of geometry, visited him in the summer of 1615 and again in 1616; Napier proposed tables with log 1 = 0 and base 10, which Briggs built (**documented**, MacTutor)."),
            dict(type="p", text="*Arithmetica logarithmica* (1624) gives the logarithms of 1 to 20,000 and of 90,000 to 100,000 \"computed to 14 decimal places\" (MacTutor; Roegel starts the second range at 90,001: a small **dispute**). Briggs \"computed these values until n = 54\" square roots of 10, then used a proportion for numbers near 1 and finite differences to speed the roots (Roegel, **documented**). Adriaan Vlacq's table of 1628 cut Briggs's figures to 10 places and was called a second edition, \"although it actually wasn't\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Adding logarithms still saves the day", toc="Full circle", blocks=[
            dict(type="p", text="Every 64-bit floating-point number is stored as a power of 2 and a fraction: in effect, the whole part of its binary logarithm and the rest. And when a computation multiplies many small numbers, logarithms come back in their original role."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program multiplied {uf['n']} probabilities near 0.01 in 64-bit floating point. The answer came out as {uf['prod']}: the true product is too small for the format. Adding their logarithms instead gives {uf['log']}, so the product is 10 to that power, exactly right. Statistics and machine learning work with log-probabilities for this reason: Napier's trade of products for sums, four centuries on."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With a log table, how do you take a square root?", "Halve the logarithm and look up the number that has it: log √x = ½ log x."),
            ("Why is base 10 convenient?", "log(10x) = 1 + log x: moving the decimal point only changes the whole part of the logarithm, so one table of fractions serves every size of number."),
            ("Why does each square root of 10 bring the number closer to 1?", "Its logarithm halves each time: 1, ½, ¼, …, 1/2⁵⁴. A number whose logarithm is nearly 0 is nearly 1."),
            ("Why compute logarithms only for primes?", "Every other whole number is a product of primes, and the logarithm of a product is the sum of the logarithms."),
            ("Why did the 400 probabilities come out as 0?", f"Their product is 10 to the power {uf['log']}, far below the smallest positive 64-bit double, {sci(uf['min'])}, so it underflows to zero. Its logarithm is an ordinary number."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Napier's Descriptio (1614), translated", text="Ian Bruce's English translation of Napier's own description and construction of his logarithms, with the Latin.",
                 draw=C.draw_book, link="https://www.17centurymaths.com/contents/napiercontents.html", link_text="17centurymaths.com",
                 licence="Drawn placeholder."),
            dict(title="Arithmetica logarithmica (1624), reconstructed", text="Denis Roegel's reconstruction of Briggs's table, with an account of how it was computed.",
                 draw=C.draw_book, link="https://locomat.loria.fr/briggs1624/briggs1624doc.pdf", link_text="LOCOMAT",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Logarithms", d["checks"],
                           "60,000 products by table look-up against the bound set by each table's rounding, Briggs's square roots against ln 10/2⁵⁴, log 2, log 3 and log 7 by his proportion to 14 decimals or more, the addition law on every composite entry of a Briggs-sized table, and the underflow of a product of probabilities.",
                           ["static BigDecimal briggs("]),
    ]
    return dict(
        title="Logarithms", date="1614–1624",
        description="Era 3, topic 2 of The Algorithm Evolution Atlas: Napier's logarithms, Briggs's base-10 tables built from 54 square roots of 10, and why computers still add logarithms.",
        lede="Give every number a partner, chosen so that adding the partners does the work of multiplying the numbers. Print the partners in a book, and a night of long multiplication becomes a few look-ups and an addition.",
        fieldnote="The table is the algorithm's output, printed once and used by everyone. Its maker paid in square roots: fifty-four of them, one after another, each to thirty decimals, so that navigators would never have to.",
        card=[("When", "Napier 1614; Briggs 1617 and 1624"),
              ("Where", "Edinburgh and London"),
              ("What hurt", "Long multiplications for astronomy and navigation"),
              ("The fix", "A printed table: multiplication becomes addition"),
              ("Cost", "54 square roots of 10, and logarithms of the primes only")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Logarithms.java`.",
    )
