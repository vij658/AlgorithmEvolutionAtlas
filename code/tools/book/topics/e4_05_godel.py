"""Era 4, topic 5: Gödel's numbering. Every number is parsed from GodelNumbering.java's output."""
import json
import re

import common as C
from diagrams import Diagram

SHOW = {"P": "Π", "v": "∨", "~": "~"}


def nice(f):
    """Gödel's signs for display: P -> Π, v -> ∨, x1 -> x₁."""
    f = re.sub(r"([xyz])([12])", lambda m: m.group(1) + "₁₂"[int(m.group(2)) - 1], f)
    return "".join(SHOW.get(ch, ch) for ch in f)


def parse(text: str) -> dict:
    d = {"formulas": []}
    for ln in text.splitlines():
        if m := re.match(r"formula: (\S+) ; signs (.+?) ; (.+?) = (.+)$", ln):
            d["formulas"].append(dict(f=m.group(1), signs=m.group(2), prod=m.group(3), num=m.group(4)))
        elif m := re.match(r"roundtrip: (\d+) random strings of 1 to 8 signs \((\d+) different\) .*? the largest number has (\d+) digits$", ln):
            d["rt"] = dict(n=int(m.group(1)), diff=int(m.group(2)), digits=int(m.group(3)))
        elif m := re.match(r"proof: .*? about 10\^([\d.]+) digits", ln):
            d["proof"] = m.group(1)
        elif m := re.match(r"bounded: .*?: (\d+) cases$", ln):
            d["bounded"] = int(m.group(1))
        elif m := re.match(r'diag: A = "(.+?)" \((\d+) characters\) ; its number has (\d+) digits ; .*? \((\d+) characters, number of (\d+) digits\) ; .*? G = "(.+)"$', ln):
            d["diag"] = dict(A=m.group(1), alen=int(m.group(2)), adig=int(m.group(3)), glen=int(m.group(4)), gdig=int(m.group(5)), G=m.group(6))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def code_svg(d):
    """ff0 -> signs -> prime powers -> 1080, and back."""
    f = next(x for x in d["formulas"] if x["f"] == "ff0")

    def draw(t, standalone):
        out = []
        signs, nums, primes = list("ff0"), f["signs"].split(), ["2", "3", "5"]
        out.append(C.text(30, 40, "the formula", t["muted"], 12.5))
        out.append(C.text(30, 110, "sign numbers", t["muted"], 12.5))
        out.append(C.text(30, 180, "prime powers", t["muted"], 12.5))
        for i in range(3):
            x = 180 + i * 120
            out.append(C.rect(x, 18, 64, 34, t["surface"], t["red"], 2))
            out.append(C.text(x + 32, 41, signs[i], t["ink"], 18, "middle", 700))
            out.append(C.line(x + 32, 54, x + 32, 88, t["axis"], 1.5))
            out.append(C.text(x + 32, 112, nums[i], t["red"], 17, "middle", 700))
            out.append(C.line(x + 32, 120, x + 32, 158, t["axis"], 1.5))
            out.append(C.text(x + 32, 184, C.pretty(f"{primes[i]}^{nums[i]}"), t["blue"], 17, "middle", 700))
        out.append(C.text(560, 184, f"= {f['num']}", t["ink"], 20, "start", 700))
        out.append(C.text(30, 236, "\"ff0\" is the number 2 (the successor of the successor of 0). Its Gödel number is 2³ · 3³ · 5¹ = 1080.", t["muted"], 12.5))
        out.append(C.text(30, 256, "Read it back by dividing by 2, then 3, then 5, ... and counting: 3, 3, 1, which are f, f, 0.", t["muted"], 12.5))
        return C.svg_doc(780, 270, "".join(out), "A formula coded as a number and read back", t, standalone, 0.55, 780)
    return draw


GN_HTML = """
<div class="board gn-board">
  <div style="min-width:0">
    <div class="eyebrow">Type a formula with Gödel's signs</div>
    <div class="presets" id="gn-keys"></div>
    <div class="gn-formula" id="gn-f" aria-live="polite"></div>
    <div class="controls"><button id="gn-back" type="button">Delete last</button><button id="gn-clear" type="button">Clear</button></div>
  </div>
  <div style="min-width:0">
    <ol class="gn-steps" id="gn-steps"></ol>
    <p class="say" id="gn-say" aria-live="polite"></p>
  </div>
</div>
"""

GN_CSS = """
.gn-formula{font:600 22px var(--mono);min-height:1.6em;padding:8px 10px;border:1.5px solid var(--ink);background:var(--surface);margin:10px 0;overflow-wrap:anywhere}
.gn-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:6px}
.gn-steps .m{font-family:var(--mono);font-size:12.5px;overflow-wrap:anywhere}
.gn-board .presets button{font-family:var(--mono);min-width:2.6em}
"""

GN_JS = r"""
(() => {
  const box = document.getElementById("gn-f");
  if (!box) return;
  const KEYS = [["0", 1], ["f", 3], ["~", 5], ["∨", 7], ["Π", 9], ["(", 11], [")", 13], ["x₁", 17], ["y₁", 19], ["z₁", 23], ["x₂", 289], ["y₂", 361]];
  const PR = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71];
  let seq = [["f", 3], ["f", 3], ["0", 1]];
  const keys = document.getElementById("gn-keys");
  KEYS.forEach(k => { const b = el("button", {type: "button", title: "sign number " + k[1]}, keys, k[0]); b.addEventListener("click", () => { if (seq.length < 20) { seq.push(k); show(); } }); });
  document.getElementById("gn-back").addEventListener("click", () => { seq.pop(); show(); });
  document.getElementById("gn-clear").addEventListener("click", () => { seq = []; show(); });
  const sup = n => String(n).replace(/\d/g, c => "⁰¹²³⁴⁵⁶⁷⁸⁹"[c]);
  function show() {
    box.textContent = seq.map(s => s[0]).join(" ") || " ";
    const ol = document.getElementById("gn-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    const say = document.getElementById("gn-say");
    if (!seq.length) { say.textContent = "Press the signs to write a formula."; return; }
    li(`sign numbers: <span class="m">${seq.map(s => s[1]).join(", ")}</span>`);
    li(`Gödel's number: <span class="m">${seq.map((s, i) => PR[i] + sup(s[1])).join(" · ")}</span>`);
    let g = 1n;
    seq.forEach((s, i) => { g *= BigInt(PR[i]) ** BigInt(s[1]); });
    const str = g.toString();
    li(`= <span class="m">${str.length <= 60 ? fmt(str) : str.slice(0, 24) + "…" + str.slice(-12)}</span> (${fmt(str.length)} digit${str.length > 1 ? "s" : ""})`);
    let h = g; const back = [];
    for (let i = 0; h > 1n; i++) { const p = BigInt(PR[i]); let e = 0; while (h % p === 0n) { h /= p; e++; } back.push(e); }
    const names = Object.fromEntries(KEYS.map(k => [k[1], k[0]]));
    li(`factored back: exponents <span class="m">${back.join(", ")}</span>, which spell <span class="m">${back.map(e => names[e]).join(" ")}</span>`);
    say.textContent = str.length > 100 ? "A short formula already has a number too long to say aloud; a proof's number is unimaginably longer. But it is only a number, and arithmetic can talk about it." :
      "Every formula gets its own number, because every number factors into primes in only one way.";
  }
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Gödel's numbering combined older ideas, and where it led")
    W = 210
    nodes = {
        "hil": (20, 20, "Hilbert's program", "proofs as strings of signs, checked by rule", "topic 1", "ink"),
        "fac": (395, 20, "Unique factorization", "every number is one product of primes", "Euclid's Elements", "ink"),
        "diag": (770, 20, "The diagonal argument", "a list that cannot contain its own diagonal", "Cantor", "ink"),
        "god": (395, 170, "Gödel's numbering", "⊕ formulas and proofs coded as numbers", "1931", "red"),
        "inc": (20, 330, "Incompleteness", "true but unprovable statements", "1931", "ink"),
        "ct": (395, 330, "Church and Turing", "programs as data; undecidable problems", "topics 6, 7", "ink"),
        "sp": (770, 330, "The stored program", "instructions held as numbers", "topic 9", "ink"),
        "today": (395, 480, "Code as data today", "compilers, interpreters, programs that print themselves", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("hil", "god", ports=("bottom", "top:0.15"))
    D.edge("fac", "god", ports=("bottom", "top"))
    D.edge("diag", "god", ports=("bottom", "top:0.85"))
    D.edge("god", "inc", ports=("bottom:0.1", "top:0.7"))
    D.edge("god", "ct", ports=("bottom", "top"))
    D.edge("god", "sp", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("ct", "today", ports=("bottom", "top"))
    D.edge("sp", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: programs stored as numbers is this book's reading of the link, not a documented line of influence.", "caption")
    return D


def chain(d):
    ff0 = next(x for x in d["formulas"] if x["f"] == "ff0")
    dg = d["diag"]
    steps = [
        ("Hilbert wanted mathematics proved consistent by finite, mechanical means",
         "Write every proof as a string of signs, checkable by rule", "Hilbert's formalism"),
        ("Proofs are strings; arithmetic is about numbers",
         f"Code each formula as a number: ff0 → {ff0['num']}", "Gödel, 1931"),
        ("Can a formula say something about itself?",
         f"The diagonal: put a formula's own number into it ({dg['glen']} characters, here)", "Gödel, 1931"),
        ("\"I am not provable\" is then true and unprovable, if arithmetic is consistent",
         "No complete, consistent system for arithmetic; computation itself needs a definition", "Church, Turing, 1936"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from formal proofs to a sentence about itself")
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
    F, rt, dg = d["formulas"], d["rt"], d["diag"]
    num_a = dg["G"].split(" ")[3]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Hilbert's program (topic 1) treated proofs as strings of signs that a clerk could check by rule. Euclid had shown that every number factors into primes in only one way. Gödel combined them: if each string of signs is coded as a product of prime powers, statements about proofs become statements about numbers, and a formula can be made to speak about itself by the kind of diagonal construction Cantor had used. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Gödel's numbering (1931). Blue: code treated as data, today."),
        ]),
        dict(id="code", eyebrow="Try it", title="Turn a formula into a number", toc="Try it", blocks=[
            dict(type="p", text="Press Gödel's signs to write a formula: 0, f (the next number), ~ (not), ∨ (or), Π (for all), brackets and variables. The page gives each sign its number, raises the first prime to the first sign's number, the second prime to the second's, and multiplies. Then it factors the result to show that the formula comes back. \"ff0\", the number 2, is coded as 1080; a formula of a dozen signs already has hundreds of digits."),
            dict(type="widget", html=GN_HTML, js=GN_JS, css=GN_CSS,
                 fallback=dict(type="svg", name="code", draw=code_svg(d), alt="A formula coded as a number and read back", width=780),
                 note="In the interactive edition you can type any formula with Gödel's signs and see its number."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Signs, products of primes, and a diagonal", toc="How it works", blocks=[
            dict(type="p", text="**The sign table** (Gödel 1931, page 179 of the original): \"0\" is 1, f (the next number) 3, ~ (not) 5, ∨ (or) 7, Π (for all) 9, \"(\" 11 and \")\" 13. Variables get the primes above 13 (x₁ is 17, y₁ 19, z₁ 23), and variables of the next type their squares (x₂ is 289). A string of signs with numbers n₁, n₂, …, nₖ becomes 2^n₁ · 3^n₂ · … · pₖ^nₖ:"),
            dict(type="table", head=["Formula", "Sign numbers", "Gödel number"], num=[2],
                 rows=[[nice(x["f"]), x["signs"], C.pretty(x["num"]) if "digits" not in x["num"] else x["num"].replace("...", "…")] for x in F]),
            dict(type="p", text=f"**Reading back.** Divide by 2 as often as possible, then by 3, then by 5, and count: the counts are the sign numbers. Because factorization is unique, no two strings share a number; the program coded {rt['n']:,} random strings ({rt['diff']:,} different), read every one back, and found no collision. The largest had {rt['digits']:,} digits."),
            dict(type="p", text=f"**Proofs.** A proof is a list of formulas, coded the same way with the formulas' numbers as exponents. Even the three-line list f0, ff0, x₂(x₁) is 2²⁴ · 3¹⁰⁸⁰ · 5 raised to a {next(x for x in F if x['f'] == 'x2(x1)')['num'].split(' ')[0]}-digit number, whose last factor alone has about 10^{d['proof']} digits. Nobody writes these numbers down; the point is that \"x is the number of a proof of formula y\" is a property of whole numbers that loops of known length can check. The program checks one such step, reading an exponent back with loops of fixed length, against plain division in {d['bounded']:,} cases."),
            dict(type="p", text=f"**The diagonal.** The same trick works with any numbering. The program numbers English sentences (each printable character a digit from 1 to 95) and takes the sentence A: \"{dg['A']}\" Its number has {dg['adig']} digits. Writing that number in place of each at-sign gives a {dg['glen']}-character sentence G:"),
            dict(type="code", code=dg["G"].replace(num_a, num_a[:20] + "…" + num_a[-8:])),
            dict(type="p", text="Follow G's recipe: take sentence number … (that is A), put the number in place of each at-sign, and you get G itself. G says of itself that it is not provable. Gödel built the same sentence inside arithmetic, with \"provable\" spelled out as a property of numbers."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Code the objects of a system (formulas, proofs, programs) as the system's own data, and the system can describe itself. That is what makes self-reference, and therefore its limits, possible."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How fast the numbers grow", toc="Measured", blocks=[
            dict(type="table", head=["Formula", "Signs", "Digits in its number"], num=[1, 2],
                 rows=[[nice(x["f"]), str(len(x["signs"].split())), (x["num"].split(" ")[0] if "digits" in x["num"] else str(len(x["num"])))] for x in F]),
            dict(type="p", text=f"Each sign multiplies the number by a prime raised to the sign's number, so length grows with the sizes of the signs, not only their count. A variable of the second type (289) adds about 87 digits on the first prime alone. The sentence numbering grows more gently: {dg['alen']} characters give {dg['adig']} digits, about two per character, because it is ordinary positional notation in base 95."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Königsberg, 1930", toc="The evidence", blocks=[
            dict(type="p", text="Gödel announced the first incompleteness theorem at a conference in Königsberg in September 1930; the announcement \"drew little attention apart from that of von Neumann\", who soon proved the second theorem independently and wrote to Gödel on 20 November 1930 (Wikipedia; Zach). The paper was submitted on 17 November 1930 and printed in *Monatshefte für Mathematik und Physik* 38 (1931), 173–198, with 45 primitive recursive definitions; the promised part II never appeared (Wikipedia)."),
            dict(type="p", text="The sign table is in Meltzer's translation (1962) at the original page [179], and in Hirzel's (2000). How much of Hilbert's program the theorems refuted is still argued (**disputed**); finitary consistency proofs of the kind Hilbert wanted are ruled out (Zach)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Programs that read programs", toc="Full circle", blocks=[
            dict(type="p", text="Five years later Turing coded machines as numbers in the same spirit (topic 7), and fifteen years later the stored-program computer kept its instructions in memory as numbers (topic 9). Every compiler, interpreter and virus scanner today is a program that takes programs as data; the limits Gödel found reappear as the impossibility of a perfect bug-finder."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"A {dg['alen']}-character template and its own {dg['adig']}-digit number make a sentence that refers to itself. The same construction, written in a programming language, is a program that prints its own text."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What formula has the Gödel number 24?", "24 = 2³ · 3¹: sign numbers 3 and 1, that is, f0, the number 1."),
            ("Is 2⁵ · 5¹ the number of any formula?", "No: the exponent of 3 is zero, and every sign number is at least 1, so a gap means the number codes no string."),
            ("Why must the code use prime powers rather than, say, the digits of the sign numbers written side by side?", "Side by side, 1 followed by 13 and 11 followed by 3 both read 113. Prime powers are unambiguous because factorization is unique."),
            ("Does G contain its own number?", "No, it cannot: the number is longer than G. It contains A's number and a recipe whose result is G."),
            ("If G were provable, what would go wrong?", "G says it is not provable, so a proof of G would prove something false: the system would prove a falsehood. In a consistent system G is unprovable, and so it is true."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="On Formally Undecidable Propositions (1931)", text="Meltzer's English translation, with the original page numbers; the sign table is on [179].",
                 draw=C.draw_book, link="https://gtts.ehu.es/German/Docencia/2021/MTBYC/pdf/Godel.pdf", link_text="University of the Basque Country", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "GodelNumbering", d["checks"],
                           f"the numbers of six formulas and their factoring back, {rt['n']:,} random strings coded and read back without a collision, the exponent read with fixed-length loops in {d['bounded']:,} cases, and the self-referring sentence G.",
                           ["static BigInteger godel(", "static List<Integer> decode(", "static String diag("]),
    ]
    return dict(
        title="Gödel's Numbering", date="1931",
        description="Era 4, topic 5 of The Algorithm Evolution Atlas: Gödel's coding of formulas and proofs as numbers, and the diagonal sentence that says it is unprovable.",
        lede="Gödel gave every sign a number, every formula a product of prime powers, and every proof a number built from those. Arithmetic could then talk about its own proofs, and one of its sentences says, in effect, \"I am not provable\".",
        fieldnote=f"The formula \"ff0\", which means 2, is the number {next(x for x in F if x['f'] == 'ff0')['num']}. That is all the trick is: a formula becomes a number, and a number is something arithmetic can talk about. From it came the first proof that some true statements cannot be proved.",
        card=[("When", "Announced September 1930; printed 1931"),
              ("Where", "Königsberg (announcement); Monatshefte (paper)"),
              ("What hurt", "Proofs were strings; arithmetic was about numbers"),
              ("The fix", "Code signs, formulas and proofs as numbers"),
              ("Cost", "Numbers far too large to write, but only numbers")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `GodelNumbering.java`.",
    )
