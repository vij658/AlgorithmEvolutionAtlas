"""Era 2, topic 4: zero becomes a number. Every number is parsed from ZeroAsANumber.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"gwalior": [], "rules": []}
    for ln in text.splitlines():
        if m := re.match(r"base10 no mark: of (\d+) numbers, (\d+) share their written form with another ; largest group (\d+) \(written \"(.+)\"\)$", ln):
            d["dec"] = dict(n=int(m.group(1)), shared=int(m.group(2)), big=int(m.group(3)), form=m.group(4))
        elif m := re.match(r"base60 no mark: of (\d+) numbers \(three sexagesimal places\), (\d+) share their written form ; largest group (\d+)$", ln):
            d["bab"] = dict(n=int(m.group(1)), shared=int(m.group(2)), big=int(m.group(3)))
        elif m := re.match(r"base60 medial mark: with a placeholder never written at the end, (\d+) still share ; largest group (\d+)$", ln):
            d["med"] = dict(shared=int(m.group(1)), big=int(m.group(2)))
        elif m := re.match(r"gwalior (\d+): without a zero it is written \"(\d+)\" ; below 100000 that also means (\d+) other numbers(?:, starting (.+))?$", ln):
            d["gwalior"].append(dict(n=int(m.group(1)), form=m.group(2), others=int(m.group(3)), first=m.group(4) or ""))
        elif m := re.match(r"brahmagupta: (\d+) pairs from -60 to 60 ; .* division on all (\d+) with a non-zero divisor ; 0/0 gives (\d+) ; 7/0 gives the fraction (\S+)$", ln):
            d["bra"] = dict(pairs=int(m.group(1)), div=int(m.group(2)), zz=m.group(3), nz=m.group(4))
        elif m := re.match(r"rule (.+?): (.+)$", ln):
            d["rules"].append((m.group(1), m.group(2)))
        elif m := re.match(r"java: 7 / 0 \(int\) -> (.+?) ; 7\.0 / 0\.0 -> (\S+) ; -7\.0 / 0\.0 -> (\S+) ; 0\.0 / 0\.0 -> (\S+) ; 0\.0 == -0\.0 is (\S+) ; 1 / -0\.0 -> (\S+) ; NaN == NaN is (\S+)$", ln):
            d["java"] = m.groups()
        elif m := re.match(r"convention: (\d+) fractions, x/0 = 0 ; .* hold in all (\d+) cases ; \(a/b\) x b = a holds in (\d+) of (\d+) pairs", ln):
            d["conv"] = dict(fr=int(m.group(1)), triples=int(m.group(2)), cancel=int(m.group(3)), pairs=int(m.group(4)))
    d["checks"] = C.checks(text)
    return d


def draw_stone(theme, standalone=False):
    """Drawn placeholder: a stone slab with the number 270 in a modern hand."""
    t = theme
    b = [C.rect(0, 0, 200, 150, t["wash"], t["rule"], 1),
         C.rect(36, 18, 128, 114, t["surface"], t["ink2"], 1.5, 6)]
    for i in range(5):
        b.append(C.line(50, 36 + i * 9, 150, 36 + i * 9, t["muted"], 1))
    b.append(C.text(100, 106, "270", t["ink"], 30, "middle", 700))
    b.append(C.circle(124, 96, 13, "none", t["red"], 2.5))
    return C.svg_doc(200, 150, "".join(b), "Drawn placeholder of the Gwalior inscription's 270", theme, standalone, 0.3, 220)


def readings_svg(d):
    """The number 270 written with and without a zero, and what it could be taken for."""
    g = next(x for x in d["gwalior"] if x["n"] == 270)

    def draw(t, standalone):
        out = [C.text(20, 30, "With a zero", t["ink"], 15, "start", 700),
               C.rect(20, 44, 170, 70, t["surface"], t["red"], 2.5),
               C.text(105, 92, "270", t["ink"], 34, "middle", 700),
               C.text(20, 140, "one reading", t["muted"], 13),
               C.text(260, 30, "Without a mark for the empty place", t["ink"], 15, "start", 700),
               C.rect(260, 44, 170, 70, t["surface"], t["ink2"], 1.5),
               C.text(345, 92, g["form"], t["ink"], 34, "middle", 700),
               C.line(440, 79, 500, 79, t["ink2"], 1.5), C.path("M500 79 l-9 -5 v10 z", None, t["ink2"], 0)]
        for i, v in enumerate(["27", "207", "270", "2007", "2070", "2700"]):
            x, y = 515 + (i % 3) * 140, 50 + (i // 3) * 60
            out.append(C.rect(x, y, 124, 46, t["wash"], t["red"] if v == "270" else t["rule"], 2 if v == "270" else 1))
            out.append(C.text(x + 62, y + 31, v, t["ink"], 20, "middle"))
        out.append(C.text(260, 140, f"below 100,000 it could be {g['others'] + 1} different numbers", t["muted"], 13))
        return C.svg_doc(960, 160, "".join(out), "270 with a zero, and the readings it allows without one", t, standalone, 0.6, 960)
    return draw


ZR_HTML = """
<div class="board zr-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="zr-n">A number <input id="zr-n" type="number" min="1" max="999999" value="270"></label>
      <div class="presets" id="zr-pre"></div>
    </div>
    <div class="zr-out" id="zr-out" aria-live="polite"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Brahmagupta's rules, and today's</div>
    <div class="controls zr-calc">
      <select id="zr-a" aria-label="first number"></select>
      <select id="zr-op" aria-label="operation"><option>+</option><option>−</option><option>×</option><option>÷</option></select>
      <select id="zr-b" aria-label="second number"></select>
    </div>
    <table class="zr-tab"><tbody id="zr-res"></tbody></table>
  </div>
</div>
"""

ZR_CSS = """
.zr-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px}
.zr-out{font-size:14px}
.zr-out h4{margin:12px 0 4px;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.zr-out .big{font-family:var(--mono);font-size:26px;font-weight:600}
.zr-out .chips{display:flex;flex-wrap:wrap;gap:4px}
.zr-out .chips span{font-family:var(--mono);font-size:12.5px;padding:2px 7px;border:1px solid var(--rule);background:var(--surface)}
.zr-out .chips span.me{border-color:var(--red);color:var(--red);font-weight:600}
.zr-out .sx{font-family:var(--mono);font-size:15px}
.zr-out .sx b{display:inline-block;min-width:1.8em;text-align:center;border:1px solid var(--rule);background:var(--surface);margin-right:3px;padding:1px 3px}
.zr-out .sx b.e{color:var(--muted);border-style:dashed}
.zr-tab{border-collapse:collapse;width:100%;font-size:13.5px}
.zr-tab td{padding:6px;border-bottom:1px solid var(--rule);vertical-align:top}
.zr-tab td:first-child{color:var(--muted);width:40%}
.zr-tab td:last-child{font-family:var(--mono)}
"""

ZR_JS = r"""
(() => {
  const inp = document.getElementById("zr-n");
  if (!inp) return;
  const out = document.getElementById("zr-out");
  const pre = document.getElementById("zr-pre");
  [270, 50, 933, 105, 3600, 61].forEach(v => { const b = el("button", { type: "button" }, pre, String(v)); b.addEventListener("click", () => { inp.value = v; show(); }); });
  const digits = (n, base) => { const d = []; while (n > 0) { d.unshift(n % base); n = Math.floor(n / base); } return d; };
  const noZero = (n, base) => digits(n, base).filter(x => x).join(" ");
  const medial = (n, base) => { const d = digits(n, base); while (d.length && d[d.length - 1] === 0) d.pop(); return d.map(x => x || ".").join(" "); };
  function show() {
    const n = Math.max(1, Math.min(999999, Math.floor(+inp.value || 1)));
    out.innerHTML = "";
    el("h4", {}, out, "With a zero");
    el("div", { class: "big" }, out, String(n));
    el("h4", {}, out, "Without a mark for the empty place");
    const f = noZero(n, 10), same = [];
    for (let x = 1; x <= 999999; x++) if (noZero(x, 10) === f) same.push(x);
    el("div", { class: "big" }, out, f.replace(/ /g, ""));
    el("p", {}, out, same.length === 1 ? "No other number below a million is written this way." : `Below a million, ${fmt(same.length)} numbers are written this way:`);
    const ch = el("div", { class: "chips" }, out);
    same.slice(0, 40).forEach(x => el("span", { class: x === n ? "me" : "" }, ch, fmt(x)));
    if (same.length > 40) el("span", {}, ch, `… ${fmt(same.length - 40)} more`);
    el("h4", {}, out, "In base 60, as on a Babylonian tablet");
    const d = digits(n, 60), sx = el("div", { class: "sx" }, out);
    d.forEach(x => el("b", { class: x ? "" : "e" }, sx, x ? String(x) : "·"));
    let a = 0, b = 0;
    const fa = noZero(n, 60), fb = medial(n, 60);
    for (let x = 1; x < 216000; x++) { if (noZero(x, 60) === fa) a++; if (medial(x, 60) === fb) b++; }
    el("p", {}, out, `Below 60³ = 216,000: with no mark at all, ${fmt(a)} number${a === 1 ? "" : "s"} look${a === 1 ? "s" : ""} the same; with a placeholder that is never written at the end, ${fmt(b)}.`);
  }
  // Brahmagupta's rules
  const A = document.getElementById("zr-a"), O = document.getElementById("zr-op"), B = document.getElementById("zr-b");
  [-5, -3, 0, 3, 5].forEach(v => { el("option", { value: v }, A, v < 0 ? `debt ${-v}` : v ? `fortune ${v}` : "zero"); el("option", { value: v }, B, v < 0 ? `debt ${-v}` : v ? `fortune ${v}` : "zero"); });
  A.value = 0; B.value = 0; O.value = "÷";
  const name = v => v < 0 ? `a debt of ${-v}` : v ? `a fortune of ${v}` : "zero";
  function calc() {
    const a = +A.value, b = +B.value, op = O.value;
    let bra, rule, jint, jdbl, lean;
    if (op === "+") { bra = name(a + b); rule = a === 0 || b === 0 ? "Zero added to a number leaves it unchanged." : Math.sign(a) === Math.sign(b) ? "Like kinds add." : "Unlike kinds give their difference."; jint = jdbl = lean = String(a + b); }
    if (op === "−") { bra = name(a - b); rule = b === 0 ? (a < 0 ? "\"A debt minus zero is a debt.\"" : a > 0 ? "\"A fortune minus zero is a fortune.\"" : "\"Zero minus zero is a zero.\"") : a === 0 ? (b < 0 ? "\"A debt subtracted from zero is a fortune.\"" : "\"A fortune subtracted from zero is a debt.\"") : "Subtract by the rules for fortunes and debts."; jint = jdbl = lean = String(a - b); }
    if (op === "×") { bra = name(a * b); rule = a === 0 || b === 0 ? "\"The product of zero multiplied by a debt or fortune is zero.\"" : Math.sign(a) === Math.sign(b) ? "Two fortunes, or two debts, give a fortune." : "A debt and a fortune give a debt."; jint = jdbl = lean = String(a * b); }
    if (op === "÷") {
      if (b === 0 && a === 0) { bra = "zero"; rule = "\"Zero divided by zero is zero.\" Later rejected."; }
      else if (b === 0) { bra = `${a}/0, a fraction with zero below`; rule = "A fortune or debt divided by zero is a fraction with zero as denominator."; }
      else { const g = (x, y) => y ? g(y, x % y) : Math.abs(x); const k = g(a, b); bra = a === 0 ? "zero" : `${Math.sign(a) * Math.sign(b) < 0 ? "a debt" : "a fortune"} of ${Math.abs(a / k)}${Math.abs(b / k) === 1 ? "" : "/" + Math.abs(b / k)}`; rule = "Like kinds give a fortune, unlike a debt."; }
      jint = b === 0 ? "ArithmeticException: / by zero" : String(Math.trunc(a / b));
      const q = a / b; jdbl = Number.isNaN(q) ? "NaN" : q === Infinity ? "Infinity" : q === -Infinity ? "-Infinity" : String(q);
      lean = b === 0 ? "0" : String(q);
    }
    const tb = document.getElementById("zr-res");
    tb.innerHTML = "";
    [["Brahmagupta, 628", bra], ["His rule", rule], ["Java, whole numbers", jint], ["Java, floating point", jdbl], ["Lean and Isabelle (x/0 = 0)", lean]]
      .forEach(([k, v]) => { const tr = el("tr", {}, tb); el("td", {}, tr, k); el("td", {}, tr, v); });
  }
  [A, O, B].forEach(x => x.addEventListener("change", calc));
  inp.addEventListener("change", show);
  show(); calc();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How zero became a number, and where its rules ended up")
    W, H = 210, 86
    nodes = {
        "bab": (20, 20, "Babylonian place value", "", "Era 1, topic 3", "ink"),
        "ph": (270, 20, "A placeholder", "two wedges, never at the end", "c. 400 BCE", "ink"),
        "neg": (770, 20, "Negative numbers", "black rods, a sign rule", "Nine Chapters, topic 1", "ink"),
        "dig": (145, 170, "Zero as a digit", "⊕ a mark that can stand anywhere", "Gwalior, 876", "ink"),
        "bra": (520, 170, "Zero as a number", "⊕ rules beside fortunes and debts", "Brahmagupta, 628", "red"),
        "alk": (145, 330, "Algorism", "written column arithmetic", "al-Khwarizmi, topic 6", "ink"),
        "fib": (145, 470, "Liber Abaci", "the numerals reach Pisa", "1202, topic 8", "ink"),
        "ieee": (520, 330, "Floating point", "signed zero, infinity, NaN", "Java, 2026", "blue"),
        "lean": (770, 330, "Proof assistants", "⊕ define x / 0 = 0", "Lean, Isabelle, Coq", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("bab", "ph", ports=("right", "left"))
    D.edge("ph", "dig", ports=("bottom", "top:0.7"))
    D.edge("dig", "bra", ports=("right", "left"))
    D.edge("neg", "bra", ports=("bottom", "top:0.8"), dashed=True)
    D.edge("dig", "alk", ports=("bottom", "top"))
    D.edge("alk", "fib", ports=("bottom", "top"))
    D.edge("bra", "ieee", ports=("bottom:0.3", "top"))
    D.edge("bra", "lean", ports=("bottom:0.8", "top:0.3"))
    D.text(20, 615, "Dashed: negative numbers appear in China earlier, but no transmission to India is documented.", "caption")
    return D


def chain(d):
    dec, med = d["dec"], d["med"]
    conv = d["conv"]
    steps = [
        (f"Place value with no mark for an empty place: {dec['shared']:,} of the numbers below a million share their written form",
         "A placeholder for the empty place", "Babylon, c. 400 BCE"),
        (f"The placeholder is never written at the end, so 1 and 60 still look alike: {med['shared']:,} base-60 numbers below 216,000 collide",
         "A zero that can stand anywhere, even last: 270 and 50 at Gwalior", "Gwalior, 876 CE"),
        ("A mark is not a number: what is 5 − 5, or zero times a debt?",
         "Rules for zero beside fortunes and debts", "Brahmagupta, 628"),
        ("His rule 0 ÷ 0 = 0 breaks (a ÷ b) × b = a",
         "Leave division by zero undefined: Java throws, floating point gives NaN", "modern arithmetic"),
        ("Undefined values make every proof check its denominators",
         f"Define x ÷ 0 = 0; the laws survive except (a ÷ b) × b = a, which fails in {conv['pairs'] - conv['cancel']} of {conv['pairs']:,} cases", "Lean, Isabelle"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from an empty place to x ÷ 0 = 0")
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
    dec, bab, med, bra, conv = d["dec"], d["bab"], d["med"], d["bra"], d["conv"]
    j = d["java"]
    pct = lambda a, b: f"{100 * a / b:.1f}%"
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Place value came from Babylon (Era 1, topic 3), with a placeholder for an empty place added late. Indian numerals let the mark stand anywhere, and Brahmagupta gave it rules, next to the rules for positive and negative numbers. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: zero as a number. Blue: two modern answers to the question Brahmagupta answered first, what dividing by zero gives."),
        ]),
        dict(id="read", eyebrow="Try it", title="Read it without a zero", toc="Try it", blocks=[
            dict(type="p", text="Type a number and see how it would be written with no mark for an empty place, and how many other numbers would look the same. Then try Brahmagupta's rules on fortunes, debts and zero, next to what Java and the proof assistants answer today."),
            dict(type="widget", html=ZR_HTML, js=ZR_JS, css=ZR_CSS,
                 fallback=dict(type="svg", name="readings", draw=readings_svg(d), alt="270 with a zero, and the readings it allows without one", width=960),
                 note="In the interactive edition you can type any number below a million, and try Brahmagupta's rules."),
            dict(type="table", head=["System", "Numbers", "Written like another number", "Share", "Largest group"], num=[1, 2, 4],
                 rows=[["Base 10, no mark", f"1 to {dec['n']:,}", f"{dec['shared']:,}", pct(dec["shared"], dec["n"]), f"{dec['big']} (all written \"{dec['form'].replace(' ', '')}\")"],
                       ["Base 60, no mark", f"1 to {bab['n']:,}", f"{bab['shared']:,}", pct(bab["shared"], bab["n"]), str(bab["big"])],
                       ["Base 60, placeholder never at the end", f"1 to {bab['n']:,}", f"{med['shared']:,}", pct(med["shared"], bab["n"]), str(med["big"])],
                       ["Any base, with a zero", "", "0", "0%", "1"]]),
            dict(type="p", text=f"Without a mark, almost half the numbers below a million can be misread. Base 60 suffers less, because an empty place is rarer when each place holds 60 values, but {bab['shared']:,} numbers still collide. A placeholder inside the number removes most of the problem; what is left is exactly the numbers that differ by a factor of 60, like 1 and 60, which only a final zero can tell apart."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="rules", eyebrow="How it works", title="Fortunes, debts and zero", toc="The rules", blocks=[
            dict(type="p", text="Brahmagupta defined zero as a number subtracted from itself, and gave it rules beside those for \"fortunes\" and \"debts\", positive and negative numbers. In MacTutor's translation: \"A debt minus zero is a debt.\" \"Zero minus zero is a zero.\" \"A debt subtracted from zero is a fortune.\" \"The product of zero multiplied by a debt or fortune is zero.\" The program implements them:"),
            dict(type="table", head=["Rule", "Example: 5 and 3"], num=[], rows=[[r[0].capitalize(), r[1]] for r in d["rules"]]),
            dict(type="p", text=f"On all {bra['pairs']:,} pairs of whole numbers from −60 to 60, his addition, subtraction and multiplication give exactly what modern arithmetic gives, and so does his division on the {bra['div']:,} pairs with a divisor other than zero. Two rules differ. A fortune or debt divided by zero is left as \"a fraction with zero as denominator\" (7/0 stays {bra['nz']}), which says little. And \"zero divided by zero is zero\": MacTutor calls this wrong."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A placeholder only says that a place is empty. A number has to answer every question arithmetic can ask of it: what is it plus 5, times a debt, divided by itself? Brahmagupta answered all of them, and only one answer was later taken back."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Which zero was first?", toc="The evidence", blocks=[
            dict(type="p", text="Brahmagupta (598–670) wrote the *Brahmasphutasiddhanta* in 628 at Bhillamala, modern Bhinmal (**documented**). The Babylonians wrote place-value numbers with no mark for an empty place for over a thousand years; from about 400 BCE they used two wedges as a placeholder, but never at the end of a number (**documented**, MacTutor)."),
            dict(type="p", text="The inscription at a temple in Gwalior records a garden of 187 by 270 *hastas* and a daily gift of 50 garlands, dated 933 in an era beginning in 57 BCE, that is 876 CE. It is the earliest dated Indian zero that everyone accepts. But stone inscriptions in Southeast Asia are two centuries older: the Cambodian stele K-127 is dated in the Khmer year 604 or 605, 682–685 CE depending on the reading, and three Sumatran stones date from the 680s (**disputed**: which is oldest, and the exact year of K-127)."),
            dict(type="p", text="The Bakhshali manuscript, full of dot zeros, gave radiocarbon dates of CE 224–383, 680–779 and 885–993 for three of its folios. Oxford announced in 2017 that it was \"as early as the 3rd or 4th century\"; Plofker, Keller, Hayashi, Montelle and Wujastyk argue that the latest folio dates the copying, most likely the 9th to 10th century (**disputed**)."),
        ]),
        dict(id="today", eyebrow="Measured", title="What dividing by zero gives today", toc="Today", blocks=[
            dict(type="table", head=["Expression", "Java's answer"], num=[],
                 rows=[["7 / 0 (whole numbers)", j[0]], ["7.0 / 0.0", j[1]], ["−7.0 / 0.0", j[2]], ["0.0 / 0.0", j[3]],
                       ["0.0 == −0.0", j[4]], ["1 / −0.0", j[5]], ["NaN == NaN", j[6]]]),
            dict(type="p", text="Whole-number division by zero stops the program. Floating point keeps going: a non-zero number over zero is an infinity with a sign, and zero over zero is NaN, \"not a number\", a value so strange that it is not equal even to itself. Zero itself has a sign: 0.0 and −0.0 are equal, yet dividing 1 by each gives opposite infinities."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Zero divided by zero is zero, again", toc="Full circle", blocks=[
            dict(type="p", text="Proof assistants, the programs that check mathematical proofs line by line, need division to give an answer for every input. Lean and Isabelle (and Coq) define *x* / 0 = 0, Hillel Wayne explains: division is not one of the axioms of a field, so it can be completed with any value at zero without contradiction, because the theorems about division all assume a non-zero denominator anyway."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program defined *x* / 0 = 0 on {conv['fr']} fractions and tested three laws on all {conv['triples']:,} triples: (a/b)/c = a/(bc), (a+b)/c = a/c + b/c and a/b + c/b = (a+c)/b all hold, zero denominators included. Only (a/b) × b = a breaks, in {conv['pairs'] - conv['cancel']} of {conv['pairs']:,} pairs: exactly those with b = 0 and a not 0. Brahmagupta's rejected rule, 0 ÷ 0 = 0, is the answer these systems give."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Without a zero, which numbers below 1,000 are written \"5\"?", "5, 50 and 500: the digit 5 with any number of empty places after it."),
            ("Why could a Babylonian placeholder in the middle of a number still not tell 1 from 60?",
             "It was never written at the end. 1 and 60 (one sixty and an empty units place) both appear as a single 1."),
            ("By Brahmagupta's rules, what is zero minus a debt of 5?", "\"A debt subtracted from zero is a fortune\": a fortune of 5, which is 0 − (−5) = 5."),
            ("Why is 0 ÷ 0 = 0 a problem if we also want (a ÷ b) × b = a?",
             "With b = 0 that law would make (a ÷ 0) × 0 = a for every a, but anything times 0 is 0. No single value of 0 ÷ 0 can satisfy it for all a."),
            ("In Java, why does 1 / −0.0 differ from 1 / 0.0?",
             f"Floating-point zero carries a sign: 1 / 0.0 is {j[1]} and 1 / −0.0 is {j[5]}, even though 0.0 == −0.0 is {j[4]}."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Gwalior inscription, 876 CE", text="A temple grant recording a garden of 187 by 270 hastas and 50 garlands a day: the earliest Indian zero dated beyond dispute. Casselman's AMS column gives a translation.",
                 draw=draw_stone, link="https://www.ams.org/publicoutreach/feature-column/fcarc-india-zero", link_text="AMS Feature Column",
                 licence="Drawn placeholder; photographs of the stone are linked from the Smithsonian article in the reading list."),
            dict(title="Brahmagupta in English, 1817", text="Colebrooke's translation of Brahmagupta's and Bhaskara's arithmetic and algebra, the classic source for the rules of zero.",
                 draw=C.draw_book, link="https://archive.org/details/algebrawitharith00brahuoft/page/n5/mode/2up", link_text="Internet Archive scan",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "1/0 = 0", "Hillel Wayne (2018, disclaimer added 2024)", "https://hillelwayne.com/post/divide-by-zero/", "Why Lean, Isabelle and Coq can define x/0 = 0 without contradiction"),
        ]),
        C.prove_it_section(ctx, "ZeroAsANumber", d["checks"],
                           "the ambiguity counts, Brahmagupta's rules against modern integers on every pair from −60 to 60, Java's floating-point zeros, and three laws of fractions under x/0 = 0 on every triple of the grid.",
                           ["static B subtract(", "static long[] divide("]),
    ]
    return dict(
        title="Zero Becomes a Number", date="628 CE",
        description="Era 2, topic 4 of The Algorithm Evolution Atlas: how a mark for an empty place became a number with rules, from Babylon to Brahmagupta to Gwalior, and what dividing by zero gives today.",
        lede="A mark for an empty place tells you how to read a number. A number with rules tells you how to calculate with it. Brahmagupta wrote the rules in 628, and his one rejected answer, zero divided by zero is zero, is back.",
        fieldnote="For more than a thousand years the Babylonians wrote place-value numbers with no mark for an empty place, and readers guessed. In India the mark became a number. Brahmagupta wrote down what zero does in every operation, next to the rules for fortunes and debts.",
        card=[("When", "Brahmagupta, 628 CE; the Gwalior inscription, 876 CE (earlier Southeast Asian zeros, **disputed**)"),
              ("Where", "India: Bhillamala (Bhinmal), Gwalior"),
              ("What hurt", "Place value needs a mark for an empty place, and arithmetic needs rules for it"),
              ("The fix", "Zero as a digit that can stand anywhere, and as a number with its own rules"),
              ("Cost", f"Without it, {pct(dec['shared'], dec['n'])} of the numbers below a million can be misread")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ZeroAsANumber.java`.",
    )
