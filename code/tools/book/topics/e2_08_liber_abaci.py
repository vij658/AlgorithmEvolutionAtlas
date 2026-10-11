"""Era 2, topic 8: Fibonacci's Liber abaci. Every number is parsed from LiberAbaci.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"numerals: 1 to 3999 ; Roman (\S+) symbols on average, longest (\d+) \((\d+) = (\w+)\) ; Indian figures (\S+) on average, at most 4$", ln):
            d["num"] = dict(roman=m.group(1), longest=int(m.group(2)), at=int(m.group(3)), rom=m.group(4), ind=m.group(5))
        elif m := re.match(r"multiply: (\d+) x (\d+) \((\w+) x (\w+)\) ; partial products (.+?) ; total (\d+) \((.+?)\) ; (\d+) digit products$", ln):
            d["mul"] = dict(a=int(m.group(1)), b=int(m.group(2)), ra=m.group(3), rb=m.group(4), parts=m.group(5).split(" ; "), total=int(m.group(6)), products=int(m.group(8)))
        elif m := re.match(r"rabbits: pairs at the end of months 1 to 12: ([\d ]+)$", ln):
            d["rabbits"] = [int(x) for x in m.group(1).split()]
        elif m := re.match(r"recursion: (.+)$", ln):
            d["rec"] = [tuple(int(v) for v in re.match(r"F\((\d+)\) = (\d+) in (\d+) calls", x.strip()).groups()) for x in m.group(1).split(";")]
        elif m := re.match(r"fast: F\(1000\) has (\d+) digits: loop 1000 additions, fast doubling (\d+) steps ; F\(1000000\) has (\d+) digits, in (\d+) doubling steps$", ln):
            d["fast"] = dict(d1000=int(m.group(1)), s1000=int(m.group(2)), dmil=int(m.group(3)), smil=int(m.group(4)))
        elif m := re.match(r"binet: .* exactly up to n = (\d+), and first goes wrong at n = (\d+)$", ln):
            d["binet"] = dict(ok=int(m.group(1)), wrong=int(m.group(2)))
        elif m := re.match(r"lame: .* ; (.+)$", ln):
            d["lame"] = [tuple(int(v) for v in re.match(r"(\d+) steps: (\d+), (\d+)", x.strip()).groups()) for x in m.group(1).split(";")]
        elif m := re.match(r"false position: (\d+) random linear problems solved exactly from two guesses ; for x\^2 = 2, guesses 1 and 2 give (\S+) ; repeated, (\d+) rounds reach (\S+)$", ln):
            d["fp"] = dict(n=int(m.group(1)), once=m.group(2), rounds=int(m.group(3)), final=m.group(4))
        elif m := re.match(r"heap: .*checked for k up to (\d+)\) ; so a heap of a million items has rank at most (\d+) ; log_phi\(10\^6\) = (\S+)$", ln):
            d["heap"] = dict(k=int(m.group(1)), rank=int(m.group(2)), log=m.group(3))
    d["checks"] = C.checks(text)
    return d


def rabbits_svg(d):
    """Months 1 to 7: each pair a dot, filled once it can breed."""
    counts = d["rabbits"][:7]

    def draw(t, standalone):
        out = []
        pairs = [0]
        for m in range(1, 8):
            nxt = []
            for age in pairs:
                nxt.append(age + 1)
                if age + 1 >= 2:
                    nxt.append(0)
            pairs = nxt
            y = 26 + (m - 1) * 34
            out.append(C.text(20, y + 5, f"month {m}", t["muted"], 12.5))
            for i, age in enumerate(pairs):
                x = 110 + i * 26
                adult = age >= 1
                out.append(C.circle(x, y, 9, t["red"] if adult else t["surface"], t["red"] if adult else t["ink2"], 1.6))
            out.append(C.text(110 + len(pairs) * 26 + 6, y + 5, f"{len(pairs)} pairs", t["ink"], 13, "start", 700))
        out.append(C.text(20, 268, "Hollow: a pair born this month. Filled: a pair that will breed next month. Each month adds as many newborns as there were pairs two months before.", t["muted"], 12))
        return C.svg_doc(960, 280, "".join(out), "The rabbit pairs month by month", t, standalone, 0.6, 960)
    assert counts[3] == 5
    return draw


LA_HTML = """
<div class="board la-board">
  <div style="min-width:0">
    <div class="controls">
      <button id="la-next" class="primary" type="button">Next month</button>
      <button id="la-reset" type="button">Start again</button>
      <span class="la-m" id="la-m"></span>
    </div>
    <div class="la-field" id="la-field" aria-label="The rabbit pairs"></div>
    <p class="say" id="la-say" aria-live="polite"></p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">A merchant's multiplication</div>
    <div class="controls">
      <input id="la-a" type="number" min="1" max="3999" value="1202" aria-label="first number"> ×
      <input id="la-b" type="number" min="1" max="3999" value="1228" aria-label="second number">
    </div>
    <div class="la-rom" id="la-rom"></div>
    <pre class="la-work" id="la-work"></pre>
  </div>
</div>
"""

LA_CSS = """
.la-field{display:flex;flex-wrap:wrap;gap:4px;min-height:60px;max-height:260px;overflow:auto;padding:8px;background:var(--wash);border:1px solid var(--rule)}
.la-field i{width:14px;height:14px;border-radius:50%;border:1.6px solid var(--ink-2);background:var(--surface);flex:none}
.la-field i.ad{background:var(--red);border-color:var(--red)}
.la-field i.new{box-shadow:0 0 0 2px var(--yellow)}
.la-m{font-family:var(--mono);font-size:13px}
.la-board .say{font-size:14.5px}
.la-board input{width:6em;font:inherit;font-family:var(--mono);font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.la-rom{font-family:var(--mono);font-size:13px;color:var(--ink-2);margin-bottom:6px;overflow-wrap:anywhere}
.la-work{font-family:var(--mono);font-size:13.5px;background:var(--surface);border:1px solid var(--rule);padding:10px;margin:0;overflow-x:auto}
"""

LA_JS = r"""
(() => {
  const field = document.getElementById("la-field");
  if (!field) return;
  let pairs, month;
  function reset() { pairs = [0]; month = 0; paint(); document.getElementById("la-say").textContent = "One newborn pair. A pair can breed at one month old and gives birth a month later, every month after that."; }
  function next() {
    if (month >= 12) return;
    const n = []; let born = 0;
    for (const a of pairs) { n.push(a + 1); if (a + 1 >= 2) { n.push(0); born++; } }
    pairs = n; month++;
    paint();
    const hist = counts.slice(-3);
    document.getElementById("la-say").textContent = born ? `${born} pair${born === 1 ? " was" : "s were"} born: one for every pair that was already alive two months ago. Total ${pairs.length} = ${hist.length >= 3 ? hist[hist.length - 2] + " + " + hist[hist.length - 3] : pairs.length}.` : "Nobody can breed yet.";
  }
  const counts = [];
  function paint() {
    field.innerHTML = "";
    pairs.forEach(a => el("i", { class: (a >= 1 ? "ad" : "") + (a === 0 && month ? " new" : "") }, field));
    document.getElementById("la-m").textContent = `month ${month}: ${pairs.length} pair${pairs.length === 1 ? "" : "s"}`;
    counts[month] = pairs.length;
  }
  // Roman numerals and the written multiplication
  const roman = n => { const v = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1], s = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]; let r = ""; v.forEach((x, i) => { while (n >= x) { r += s[i]; n -= x; } }); return r; };
  function work() {
    const a = Math.max(1, Math.min(3999, Math.floor(+document.getElementById("la-a").value || 1)));
    const b = Math.max(1, Math.min(3999, Math.floor(+document.getElementById("la-b").value || 1)));
    document.getElementById("la-rom").textContent = `In Roman numerals: ${roman(a)} × ${roman(b)}. Nothing on the page shows how the answer was found.`;
    const bs = String(b), lines = [], w = String(a * b).length + 2;
    lines.push(String(a).padStart(w)); lines.push(("× " + b).padStart(w)); lines.push("-".repeat(w));
    let total = 0;
    for (let i = bs.length - 1, sh = 0; i >= 0; i--, sh++) { const p = a * +bs[i] * 10 ** sh; total += p; lines.push(String(p).padStart(w) + `   ${a} × ${bs[i]}${sh ? " × " + 10 ** sh : ""}`); }
    lines.push("-".repeat(w)); lines.push(String(total).padStart(w) + "   every step can be checked");
    document.getElementById("la-work").textContent = lines.join("\n");
  }
  document.getElementById("la-next").addEventListener("click", next);
  document.getElementById("la-reset").addEventListener("click", () => { counts.length = 0; reset(); });
  ["la-a", "la-b"].forEach(id => document.getElementById(id).addEventListener("input", work));
  reset(); work();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 650, "How Liber abaci combined older ideas, and where the rabbit numbers went")
    W, H = 210, 86
    nodes = {
        "zero": (20, 20, "Indian numerals with zero", "", "topic 4", "ink"),
        "alk": (270, 20, "Algorism and al-jabr", "al-Khwarizmi; Abu Kamil; al-Karaji", "topic 6", "ink"),
        "trade": (520, 20, "Merchants' reckoning", "fingers, the abacus, Roman numerals", "Pisa, Bugia", "ink"),
        "skt": (770, 20, "Sanskrit counts", "the same sequence", "c. 200 BCE", "ink"),
        "lib": (395, 170, "Liber abaci", "⊕ written algorithms for trade", "Pisa, 1202; second edition 1228", "red"),
        "sch": (20, 330, "Abacus schools", "at least 600 abacus books", "direct influence a conjecture", "ink"),
        "lam": (395, 330, "Euclid's worst case", "consecutive Fibonacci numbers", "Lamé, 1844", "ink"),
        "heap": (770, 330, "Fibonacci heaps", "⊕ Fibonacci numbers bound the trees", "Fredman and Tarjan, 1987", "blue"),
        "dij": (770, 480, "Faster shortest paths", "O(n log n + m)", "Dijkstra with F-heaps", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("zero", "lib", ports=("bottom", "top:0.1"))
    D.edge("alk", "lib", ports=("bottom", "top:0.35"))
    D.edge("trade", "lib", ports=("bottom", "top:0.65"))
    D.edge("skt", "lib", ports=("bottom", "top:0.9"), dashed=True)
    D.edge("lib", "sch", ports=("bottom:0.1", "top:0.6"), dashed=True)
    D.edge("lib", "lam", ports=("bottom", "top"))
    D.edge("lib", "heap", ports=("bottom:0.9", "top:0.4"))
    D.edge("heap", "dij", ports=("bottom", "top"))
    D.text(20, 625, "Dashed: the Sanskrit sequence is older but no line to Pisa is documented; how far the book shaped the abacus schools is argued over.", "caption")
    return D


def chain(d):
    nm, fp, rec, fast, hp = d["num"], d["fp"], d["rec"], d["fast"], d["heap"]
    r35 = next(r for r in rec if r[0] == 35)
    steps = [
        (f"Roman numerals take {nm['roman']} symbols on average below 4000, and leave no working on the page",
         f"Nine Indian figures and a zero ({nm['ind']} on average), with written rules for every operation", "Liber abaci, 1202"),
        ("Merchants' problems all look different: prices, barter, partners, exchange",
         f"Standard methods; double false position solves any linear problem from two guesses: {fp['n']:,} of {fp['n']:,}", "chapter 13, elchataym"),
        (f"For a curved problem two guesses only approximate: {fp['once']} for the root of 2",
         f"Repeat the method on the new guesses: {fp['rounds']} rounds give {fp['final']}", "regula falsi (the program)"),
        (f"Computing the rabbit numbers from their definition explodes: {r35[2]:,} calls for F(35)",
         f"Keep the last two in a loop, or double the index each step: F(1,000,000) in {fast['smil']} steps", "fast doubling"),
        ("The numbers keep turning up in other algorithms",
         f"They bound the trees of a Fibonacci heap: rank at most {hp['rank']} for a million items", "Fredman and Tarjan, 1987"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from Roman numerals to Fibonacci heaps")
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
    nm, mu, rb, rec, fast, bn, lm, fp, hp = d["num"], d["mul"], d["rabbits"], d["rec"], d["fast"], d["binet"], d["lame"], d["fp"], d["heap"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The Indian figures with zero (topic 4) and al-Khwarizmi's written methods (topic 6) reached Leonardo in North Africa; Pisa's merchants supplied the problems. *Liber abaci* put the two together in fifteen chapters. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Liber abaci. Blue: a data structure of 1987 that is named after the rabbit numbers because they bound its size."),
        ]),
        dict(id="rabbits", eyebrow="Try it", title="Breed the rabbits; multiply like a merchant", toc="Try it", blocks=[
            dict(type="p", text="On the left, follow the rabbits month by month: a newborn pair can breed at one month old and gives birth a month later, and every month after. On the right, multiply two numbers below 4000 the way the book teaches: in Indian figures, with every partial product written down."),
            dict(type="widget", html=LA_HTML, js=LA_JS, css=LA_CSS,
                 fallback=dict(type="svg", name="rabbits", draw=rabbits_svg(d), alt="The rabbit pairs month by month", width=960),
                 note="In the interactive edition you can breed the rabbits for a year and multiply any two numbers below 4000."),
            dict(type="p", text=f"By these rules the program counts the pairs at the end of each month as {', '.join(map(str, rb))}. There are five pairs at the end of the fourth month, as Strick's retelling says, and each month is the sum of the two before it."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="figures", eyebrow="How it works", title="Nine figures, a zero, and the working on the page", toc="How it works", blocks=[
            dict(type="p", text=f"Chapter 1 begins: \"These are the nine figures of the Indians: 9 8 7 6 5 4 3 2 1.\" With a zero they write any number in a few figures: from 1 to 3999, Roman numerals take **{nm['roman']} symbols** on average and up to {nm['longest']} ({nm['at']:,} = {nm['rom']}), the Indian figures {nm['ind']}. Chapters 2 to 7 teach multiplication, addition, subtraction, division and fractions, chapters 8 to 11 merchants' problems, chapter 12 many posed problems, rabbits included, chapter 13 double false position, chapter 14 roots, and chapter 15 geometry and algebra."),
            dict(type="table", head=["Partial product", ""], num=[],
                 rows=[[p.split(" = ")[0], p.split(" = ")[1]] for p in mu["parts"]] + [["Total", f"**{mu['total']:,}**"]]),
            dict(type="p", text=f"{mu['a']} × {mu['b']}, the years of the two editions, written as the book teaches: {mu['products']} digit products, each line checkable. In Roman numerals the factors are {mu['ra']} and {mu['rb']}, and the answer, {mu['total']:,}, is beyond what standard Roman numerals can write. Devlin stresses this \"audit trail\": a written calculation can be checked by someone else."),
            dict(type="callout", kind="key", label="Key idea",
                 text="The book's export was the written algorithm itself: a calculation whose every step stays on the page, so that a partner, a customs officer or a court can check it. Numerals that can be calculated with, not only recorded."),
        ]),
        dict(id="computing", eyebrow="Measured", title="Four ways to compute the rabbit numbers", toc="Measured", blocks=[
            dict(type="table", head=["n", "F(n)", "Calls made by plain recursion"], num=[0, 1, 2], rows=[[str(n), f"{f:,}", f"{c:,}"] for n, f, c in rec]),
            dict(type="p", text=f"Computing F(n) straight from the definition, F(n) = F(n−1) + F(n−2), calls itself 2F(n+1) − 1 times, so the work grows as fast as the rabbits. A loop that keeps the last two numbers needs n additions: F(1000), with {fast['d1000']} digits, takes 1,000. Fast doubling, F(2k) = F(k)(2F(k+1) − F(k)) and F(2k+1) = F(k)² + F(k+1)², halves the index each step: F(1000) in {fast['s1000']} steps, and F(1,000,000), a number of **{fast['dmil']:,} digits**, in {fast['smil']}. Binet's formula, the nearest whole number to φⁿ/√5, is exact in double precision up to n = {bn['ok']} and first goes wrong at n = {bn['wrong']}."),
            dict(type="table", head=["Division steps", "Smallest pair a > b needing them"], num=[0], rows=[[str(s), f"{a:,} and {b:,}"] for s, a, b in lm]),
            dict(type="p", text="Euclid's algorithm (Era 1, topic 7) is slowest on consecutive Fibonacci numbers: the program checked that the smallest pair needing k division steps is always (F(k+2), F(k+1)), as Lamé showed in 1844."),
            dict(type="p", text=f"Double false position, chapter 13's *elchataym*, solved all {fp['n']:,} random linear problems exactly from two guesses: if guess g₁ misses by e₁ and g₂ by e₂, the answer is (g₁e₂ − g₂e₁)/(e₂ − e₁). For a curved problem it only approximates: x² = 2 from guesses 1 and 2 gives {fp['once']}. Repeating it, the method later called *regula falsi*, took {fp['rounds']} rounds to reach {fp['final']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A book known from its second edition", toc="The evidence", blocks=[
            dict(type="p", text="Leonardo of Pisa lived about 1170 to about 1250 (MacTutor; MAA's Mathematical Treasures gives about 1180–1241, **disputed**). His father was public notary at the customs in Bugia, now Bejaia in Algeria, acting for Pisan merchants, and Leonardo learned the Indian figures there (**documented**). *Liber abaci* was published in 1202, after his return to Italy. No copy of the first edition survives; every manuscript descends from the second edition of 1228, of which about a dozen copies exist, three complete (**documented**; one MAA page prints 1212 for the second edition, probably a slip)."),
            dict(type="p", text="Pisa paid him a salary: from 1228, says Strick; MacTutor quotes a decree of 1240 (**disputed**). Whether a vernacular arithmetic of about 1290, the *Livero de l'abbecho*, copies a lost simpler book by Leonardo is **disputed** between Keith Devlin and Raffaella Franci. Abacus books \"became standard in schools; at least 600 were written over the next few centuries\", but how far *Liber abaci* directly inspired them is a **conjecture**. The rabbit sequence had appeared in Sanskrit writing around 200 BCE (**documented**); Sigler's English translation of 2002 is the first complete one in a modern language."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The rabbits in a data structure", toc="Full circle", blocks=[
            dict(type="p", text="In 1987 Michael Fredman and Robert Tarjan published Fibonacci heaps in the *Journal of the ACM*: a priority queue that does every standard operation in constant amortized time except deletion, which takes O(log n). With it, Dijkstra's shortest-path algorithm runs in O(n log n + m) on a graph with n vertices and m edges. The name comes from a lemma: the smallest tree of rank k in the heap has at least F(k+2) items, so ranks stay below log base φ of n."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program built the smallest possible tree of each rank and found exactly F(k+2) items, for every k up to {hp['k']}. So a heap of a million items never has a tree of rank above **{hp['rank']}** (log base φ of a million is {hp['log']}). A puzzle about rabbits, posed among merchants' problems in 1202, bounds the running time of route-finding algorithms."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write 1999 in Roman numerals and in Indian figures.", "MCMXCIX, seven symbols, against four figures: 1999."),
            ("Why does each month's rabbit count equal the sum of the two before?", "This month's pairs are last month's pairs, all still alive, plus one newborn pair for every pair alive two months ago (those are old enough to breed)."),
            ("A guess of 10 misses by −6 and a guess of 20 misses by 14. By double false position, what is the answer?", "(10 × 14 − 20 × (−6)) / (14 − (−6)) = 260 / 20 = **13**."),
            (f"How many calls does plain recursion make for F(30)?", f"{next(r for r in rec if r[0] == 30)[2]:,}, which is 2F(31) − 1. A loop needs 29 additions."),
            ("Why are consecutive Fibonacci numbers the slowest pair for Euclid's algorithm?", "Each division step on (F(k+2), F(k+1)) has quotient 1 and leaves (F(k+1), F(k)): the numbers shrink as slowly as they can."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Liber abaci, 14th-century copy, Florence", text="Pages from a copy in the Biblioteca Nazionale Centrale di Firenze, including the page of the nine Indian figures, shown in MAA's Mathematical Treasures.",
                 draw=C.draw_manuscript, link="https://old.maa.org/node/1734149", link_text="MAA Mathematical Treasures",
                 licence="Drawn placeholder; the photographs are on the MAA page."),
            dict(title="Scritti di Leonardo Pisano, 1857", text="Boncompagni's edition of the Latin text, from a single manuscript.",
                 draw=C.draw_book, link="https://archive.org/details/bub_gb_w86fLKi88pYC/page/n7/mode/2up", link_text="Internet Archive scan",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("scholar", "Fibonacci heaps and their uses in improved network optimization algorithms", "Michael L. Fredman and Robert E. Tarjan, Journal of the ACM 34(3), 1987, 596–615", "https://collaborate.princeton.edu/en/publications/fibonacci-heaps-and-their-uses-in-improved-network-optimization-a-2/", "Constant amortized time for most heap operations; shortest paths in O(n log n + m)"),
            ("deeper", "Fibonacci Heaps (lecture slides)", "Kevin Wayne, Princeton, for Kleinberg and Tardos's Algorithm Design", "https://www.cs.princeton.edu/~wayne/kleinberg-tardos/pdf/FibonacciHeaps.pdf", "The lemma: a tree of rank k has at least F(k+2) elements, so ranks are at most log base φ of n"),
            ("deeper", "Euclidean Algorithm", "Wolfram MathWorld", "https://mathworld.wolfram.com/EuclideanAlgorithm.html", "Lamé's bound and the Fibonacci worst case"),
        ]),
        C.prove_it_section(ctx, "LiberAbaci", d["checks"],
                           "Roman numerals read back for 1 to 3999, the rabbits pair by pair against the recurrence, plain recursion's 2F(n+1) − 1 calls, the loop against fast doubling, the Fibonacci worst case of Euclid's algorithm, double false position on 10,000 linear problems, and the Fibonacci-heap lemma.",
                           ["static BigInteger[] doubling("]),
    ]
    return dict(
        title="Fibonacci's Liber Abaci", date="1202 CE",
        description="Era 2, topic 8 of The Algorithm Evolution Atlas: Fibonacci's Liber abaci, the written algorithms it brought to Pisa's merchants, the rabbit numbers and four ways to compute them, and Fibonacci heaps.",
        lede="Pisa's merchants wrote amounts in Roman numerals, fine for recording and miserable for calculating. Leonardo brought them nine Indian figures, a zero and written methods; almost in passing, a puzzle about rabbits.",
        fieldnote="The son of a customs official, who had learned the Indian figures in North Africa, wrote the merchants a manual in fifteen chapters. His real export was the written algorithm itself, put into the hands of people who did sums for a living.",
        card=[("When", "1202; the surviving text is the second edition, 1228 (**documented**)"),
              ("Where", "Pisa; learned at Bugia (Bejaia, Algeria)"),
              ("What hurt", "Roman numerals are clumsy to calculate with and leave no working to check"),
              ("The fix", "Indian figures with zero, and written step-by-step methods for trade"),
              ("Cost", f"{nm['ind']} figures per number below 4000 against {nm['roman']} Roman symbols")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LiberAbaci.java`.",
    )
