"""Era 2, topic 9: Qin Jiushao's root method (Horner's method). Every number is parsed from QinJiushao.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"steps": {}, "roots": {}}
    for ln in text.splitlines():
        if m := re.match(r"evaluate: degree 10 ; term by term (\d+) multiplications ; keeping the powers (\d+) ; Horner's rule (\d+) ; the circular-city polynomial at x = 3 is (\S+)$", ln):
            d["eval"] = dict(term=int(m.group(1)), keep=int(m.group(2)), horner=int(m.group(3)), city3=m.group(4))
        elif m := re.match(r"(cubic|quartic|city|fifth) digit (\d) at 10\^(-?\d+) -> root so far (\S+) ; shifted: (.+)$", ln):
            d["steps"].setdefault(m.group(1), []).append(dict(digit=int(m.group(2)), place=int(m.group(3)), root=m.group(4), coef=m.group(5).split()))
        elif m := re.match(r"(cubic|quartic|city|fifth) root: (\S+) ; (\d+) digits ; (\d+) multiply-adds$", ln):
            d["roots"][m.group(1)] = dict(root=m.group(2), digits=int(m.group(3)), work=int(m.group(4)))
        elif m := re.match(r"quartic other: searching above 300 gives (\d+) ;", ln):
            d["other"] = int(m.group(1))
        elif m := re.match(r"random: (\d+) polynomials", ln):
            d["random"] = int(m.group(1))
        elif m := re.match(r"speed: fifth root of 2 to 15 digits ; digit by digit (\d+) steps \((\d+) multiply-adds\) ; bisection (\d+) halvings ; Newton (\d+) steps ; (\S+)$", ln):
            d["speed"] = dict(dd=int(m.group(1)), work=int(m.group(2)), bis=int(m.group(3)), newton=int(m.group(4)), value=m.group(5))
    d["checks"] = C.checks(text)
    return d


def board_svg(d):
    """The cubic's coefficients on the board: before, after shifting by 20, after shifting by 2 more."""
    cols = [("x³ + 2x² + 6x − 13258", ["1", "2", "6", "-13258"])] + \
           [(f"after the digit {s['digit']} (root so far {s['root']})", s["coef"]) for s in d["steps"]["cubic"][:2]]

    def draw(t, standalone):
        out = []
        for j, (title, coef) in enumerate(cols):
            x = 30 + j * 310
            out.append(C.text(x, 28, title, t["ink"], 13.5, "start", 700))
            for i, v in enumerate(coef):
                y = 46 + i * 46
                neg = v.startswith("-")
                out.append(C.rect(x, y, 230, 38, t["wash"], t["ink"] if not neg else t["ink2"], 1.2))
                out.append(C.text(x + 12, y + 25, ["cubes", "squares", "roots", "number"][i], t["muted"], 12))
                out.append(C.text(x + 218, y + 25, v.replace("-", "−"), t["red"] if not neg else t["ink"], 15, "end", 700))
            if j < 2:
                out.append(C.line(x + 240, 120, x + 296, 120, t["ink2"], 1.5))
                out.append(C.path(f"M{x + 296} 120 l-9 -5 v10 z", None, t["ink2"], 0))
        out.append(C.text(30, 244, "Each shift replaces x by y + d using only multiply-and-add down the column. The number at the foot shrinks toward 0 as the root is approached.", t["muted"], 12))
        return C.svg_doc(960, 256, "".join(out), "The cubic's coefficients on the counting board, shifted digit by digit", t, standalone, 0.6, 960)
    return draw


QJ_HTML = """
<div class="board qj-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="qj-prob">Equation <select id="qj-prob">
        <option value="cubic">x³ + 2x² + 6x − 13258 = 0</option>
        <option value="quartic">−x⁴ + 763200x² − 40642560000 = 0</option>
        <option value="city">the circular city, degree 10</option>
        <option value="fifth">x⁵ − 2 = 0</option>
      </select></label>
    </div>
    <div class="controls">
      <button id="qj-next" class="primary" type="button">Next digit</button>
      <button id="qj-reset" type="button">Start again</button>
    </div>
    <div class="qj-board-col" id="qj-col" aria-label="The coefficients on the counting board"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Digit by digit</div>
    <p class="qj-root" id="qj-root"></p>
    <p class="say" id="qj-say" aria-live="polite"></p>
    <div class="qj-trials" id="qj-trials"></div>
  </div>
</div>
"""

QJ_CSS = """
.qj-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px;max-width:100%}
.qj-board-col{display:grid;gap:4px;margin-top:6px}
.qj-board-col div{display:flex;justify-content:space-between;gap:10px;font-family:var(--mono);font-size:14px;padding:6px 10px;background:var(--wash);border:1px solid var(--rule);min-width:0}
.qj-board-col div span:first-child{color:var(--muted);font-family:inherit;font-size:12px}
.qj-board-col div b{overflow-wrap:anywhere;text-align:right}
.qj-board-col div.foot{border-color:var(--red)}
.qj-root{font-family:var(--mono);font-size:24px;font-weight:600;margin:4px 0}
.qj-board .say{font-size:14.5px}
.qj-trials{font-family:var(--mono);font-size:12.5px;color:var(--ink-2)}
.qj-trials span{display:inline-block;margin:2px 6px 2px 0;padding:1px 5px;border:1px solid var(--rule)}
.qj-trials span.ok{border-color:var(--blue);color:var(--blue)} .qj-trials span.no{border-color:var(--red);color:var(--red)}
"""

QJ_JS = r"""
(() => {
  const col = document.getElementById("qj-col");
  if (!col) return;
  const P = {
    cubic: { c: [1, 2, 6, -13258], top: 1, dec: 4 },
    quartic: { c: [-1, 0, 763200, 0, -40642560000], top: 2, dec: 0 },
    city: { c: [1, 0, 15, 0, 72, 0, -864, 0, -11664, 0, -34992], top: 0, dec: 0 },
    fifth: { c: [1, 0, 0, 0, 0, -2], top: 0, dec: 6 },
  };
  const sup = k => String(k).split("").map(ch => "⁰¹²³⁴⁵⁶⁷⁸⁹"[+ch]).join("");
  const names = n => Array.from({ length: n + 1 }, (_, i) => { const p = n - i; return p === 0 ? "number" : p === 1 ? "x" : `x${sup(p)}`; });
  let c, place, root, s0, done, prob;
  const horner = (a, x) => a.reduce((v, k) => v * x + k, 0);
  const shift = (a, d) => { a = a.slice(); const n = a.length - 1; for (let k = 0; k < n; k++) for (let i = 1; i <= n - k; i++) a[i] += a[i - 1] * d; return a; };
  const show = v => { const r = Math.round(v * 1e9) / 1e9; return (Math.abs(r) >= 1e15 ? r.toExponential(6) : String(r)).replace("-", "−"); };
  function reset() {
    prob = P[document.getElementById("qj-prob").value];
    c = prob.c.slice(); place = prob.top; root = 0; s0 = Math.sign(c[c.length - 1]); done = false;
    document.getElementById("qj-trials").innerHTML = "";
    document.getElementById("qj-say").textContent = `Start at the ${10 ** place >= 1 ? 10 ** place + "s" : "units"} place. Try digits 1, 2, 3, … and keep the largest that does not carry the polynomial past zero.`;
    paint();
  }
  function paint() {
    col.innerHTML = "";
    const nm = names(c.length - 1);
    c.forEach((v, i) => { const r = el("div", { class: i === c.length - 1 ? "foot" : "" }, col); el("span", {}, r, nm[i]); el("b", {}, r, show(v)); });
    document.getElementById("qj-root").textContent = root ? show(root) : "…";
  }
  function next() {
    if (done) return;
    const pv = 10 ** place, tr = document.getElementById("qj-trials");
    tr.innerHTML = "";
    let dgt = 0;
    for (let t = 1; t <= 9; t++) {
      const v = horner(c, t * pv);
      const ok = Math.abs(v) < 1e-9 || Math.sign(v) === s0;
      el("span", { class: ok ? "ok" : "no" }, tr, `${t}: ${show(v)}`);
      if (Math.abs(v) < 1e-9) { dgt = t; break; }
      if (!ok) break;
      dgt = t;
    }
    if (dgt) { c = shift(c, dgt * pv); root += dgt * pv; }
    const exact = Math.abs(c[c.length - 1]) < 1e-9;
    document.getElementById("qj-say").innerHTML = dgt ? `Digit <b>${dgt}</b> at the ${pv >= 1 ? pv + "s" : pv} place. Replace x by y + ${show(dgt * pv)}: the column is updated by multiply-and-add only.` + (exact ? " The number at the foot is 0: the root is exact." : "")
      : `Digit 0 at the ${pv >= 1 ? pv + "s" : pv} place: even 1 would carry the polynomial past zero.`;
    place--;
    if (exact || place < -prob.dec) done = true;
    paint();
  }
  document.getElementById("qj-next").addEventListener("click", next);
  document.getElementById("qj-reset").addEventListener("click", reset);
  document.getElementById("qj-prob").addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Qin Jiushao's root method combined older ideas, and where nested multiplication went")
    W, H = 210, 86
    nodes = {
        "sqr": (20, 20, "Root extraction", "square and cube roots, digit by digit", "Era 1 topic 4; Han China", "ink"),
        "fc": (395, 20, "Columns of rods", "the board of fangcheng", "topic 1", "ink"),
        "dy": (770, 20, "The Da Yan rule", "finding unity", "topic 3", "ink"),
        "qin": (395, 170, "Qin's root method", "⊕ shift the polynomial, digit by digit", "Shushu jiuzhang, 1247", "red"),
        "li": (20, 330, "Li Zhi, Yang Hui", "the same equations, same century", "13th century", "ink"),
        "rh": (395, 330, "Ruffini; Horner", "found again in Europe", "c. 1805; 1819", "ink"),
        "wy": (395, 480, "Wylie", "Chinese methods reach Western readers", "1852", "ink"),
        "lib": (770, 330, "Nested multiplication", "⊕ every polynomial in a math library", "glibc's sin(x)", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("sqr", "qin", ports=("bottom", "top:0.15"))
    D.edge("fc", "qin", ports=("bottom", "top"))
    D.edge("dy", "qin", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("qin", "li", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("qin", "rh", ports=("bottom", "top"), dashed=True)
    D.edge("rh", "wy", ports=("bottom", "top"), dashed=True)
    D.edge("qin", "lib", ports=("bottom:0.9", "top:0.3"))
    D.text(20, 615, "Dashed: no transmission is documented; Europe's method was found independently, and Wylie only reported the Chinese one in 1852.", "caption")
    return D


def chain(d):
    ev, sp, cu = d["eval"], d["speed"], d["roots"]["cubic"]
    steps = [
        ("Surveying and area problems lead to equations of degree 3, 4, even 10",
         f"Find the root digit by digit, shifting the polynomial after each digit: the cubic's root {cu['root']}", "Qin Jiushao, 1247"),
        (f"Each trial digit means evaluating a polynomial: {ev['term']} multiplications term by term for degree 10",
         f"Nested multiply-and-add down the column: {ev['horner']} multiplications", "Horner's rule"),
        (f"One digit per step is slow: {sp['dd']} steps for 15 digits of the fifth root of 2",
         f"Newton's method doubles the correct digits each step: {sp['newton']} steps, but it needs calculus", "Newton; Joyce's comparison"),
        ("Computers evaluate polynomials billions of times a second",
         "Every math library writes them in nested form: sin(x) in the GNU C library", "glibc"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a degree-10 equation to nested multiplication")
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
    ev, st, rt, sp = d["eval"], d["steps"], d["roots"], d["speed"]
    mn = lambda s: s.replace("-", "−")
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Digit-by-digit square and cube roots were old (Era 1, topic 4), and the counting board already held the columns of an equation (topic 1). Qin's step was to treat any polynomial the way root extraction treats x²: find a digit, shift, repeat. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Qin's method. Blue: nested multiplication, the half of it that every computer uses."),
        ]),
        dict(id="board", eyebrow="Try it", title="Find a root one digit at a time", toc="Try it", blocks=[
            dict(type="p", text="Choose an equation and press **Next digit**. The board tries 1, 2, 3, … at the current place and keeps the largest digit that does not carry the polynomial past zero. Then it replaces x by y + that digit, updating the column of coefficients by multiply-and-add alone. The number at the foot of the column shrinks toward zero."),
            dict(type="widget", html=QJ_HTML, js=QJ_JS, css=QJ_CSS,
                 fallback=dict(type="svg", name="board", draw=board_svg(d), alt="The cubic's coefficients on the counting board, shifted digit by digit", width=960),
                 note="In the interactive edition you can step through four equations, including the degree-10 circular-city equation."),
            dict(type="table", head=["Digit", "Root so far", "Shifted coefficients (highest power first)"], num=[],
                 rows=[[f"{s['digit']} × 10^{s['place']}".replace("10^0", "1").replace("10^1", "10").replace("10^-", "10⁻"), s["root"], mn(" ".join(s["coef"]))] for s in st["cubic"]]),
            dict(type="p", text=f"Joyce's worked cubic, x³ + 2x² + 6x − 13258 = 0: the root lies between 20 and 30, so the first digit is 2; shifting by 20 leaves 1, 62, 1286, −4338, and so on. The program carried it to **{rt['cubic']['root']}** in {rt['cubic']['work']} multiply-adds; Joyce notes the root is \"closer to 22.9375\" than to his rounded 22.93."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="equations", eyebrow="How it works", title="Qin's equations on the board", toc="How it works", blocks=[
            dict(type="p", text=f"Two equations that the *Dictionary of Scientific Biography* lists from the *Shushu jiuzhang*. The quartic −x⁴ + 763,200x² − 40,642,560,000 = 0 has two positive roots: digit by digit from zero the program finds **{rt['quartic']['root']}**, and searching above 300 finds **{d['other']}**. The \"circular city\" equation, x¹⁰ + 15x⁸ + 72x⁶ − 864x⁴ − 11,664x² − 34,992 = 0, has the root **{rt['city']['root']}**, found in one digit; MacTutor gives the same answer, a city 9 *li* across."),
            dict(type="table", head=["Evaluating a polynomial of degree 10", "Multiplications"], num=[1],
                 rows=[["Term by term (each power from scratch)", str(ev["term"])], ["Keeping each power for the next", str(ev["keep"])], ["Nested, as on the board (Horner's rule)", str(ev["horner"])]]),
            dict(type="p", text=f"The shift and the evaluation use the same move: multiply by the digit and add the next coefficient. Nested this way, a polynomial of degree 10 costs {ev['horner']} multiplications instead of {ev['term']}; the city polynomial at x = 3 comes out exactly {ev['city3']}. The program also built {d['random']:,} random polynomials with a known root of up to four digits, and recovered every root digit by digit."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Make the hard problem look like the easy one again. After each digit, shifting the polynomial turns \"the rest of the root\" into a fresh root of a new polynomial, so the same simple step repeats until the root is found."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Digits per step", toc="Measured", blocks=[
            dict(type="table", head=["Method", "Steps for 15 digits of the fifth root of 2"], num=[1],
                 rows=[["Digit by digit (Qin)", f"{sp['dd']} ({sp['work']} multiply-adds)"], ["Bisection (halve the interval)", str(sp["bis"])], ["Newton's method", str(sp["newton"])]]),
            dict(type="p", text=f"Joyce calls the Chinese algorithm \"pretty much the same thing as the bisection algorithm, but the interval is divided into ten parts instead of into two parts\". It gains one decimal digit per step, bisection about a third of one, and Newton's method, which needs the derivative, doubles the correct digits each step. All three agree: {sp['value']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Earliest surviving, not first", toc="The evidence", blocks=[
            dict(type="p", text="Qin Jiushao (1202–1261) wrote the *Shushu jiuzhang* in 1247, during the mourning period after his mother's death (**documented**). It was not printed in his lifetime; the text read today was published in 1842 from a Korean copy. MacTutor says he solved his equations by the standard Chinese method, \"namely that which today is called the Ruffini-Horner method\". Britannica calls the book the earliest surviving description and thinks the method was widely known earlier: his contemporaries Li Zhi and Yang Hui solved similar equations, and Wang Ling and Needham traced it to Han root extraction (**conjecture** for who devised it)."),
            dict(type="p", text="Europe found it again: Britannica dates the rediscovery about 1802, the DSB says Ruffini about 1805 and Horner in 1819 (**disputed** for Ruffini's date). Horner's paper came 572 years after Qin's book: nearly six centuries. No source opened here says the method travelled from China to Europe; Alexander Wylie described Chinese equation-solving to Western readers in 1852. The *Shushu jiuzhang* is also the oldest surviving Chinese mathematical text with a zero symbol, and it used red and black rods for positive and negative numbers."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Nested multiplication everywhere", toc="Full circle", blocks=[
            dict(type="p", text="The GNU C library's sine function (topic 2) finishes with short polynomials, written in exactly this nested form: `xx * (cs2 + xx * (cs4 + xx * cs6))` for the cosine part and `x * xx * (sn3 + xx * sn5)` for the sine part. Each pair of parentheses is one step down Qin's column: multiply, then add the next coefficient."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"A degree-10 equation about a walled city, solved on a counting board in 1247, used the same multiply-and-add that a computer uses to evaluate any polynomial: {ev['horner']} multiplications for degree 10 instead of {ev['term']}. Europe named it after Horner, 572 years later."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Evaluate 2x³ − 6x² + 2x − 1 at x = 3 by nested multiplication.", "2; 2·3 − 6 = 0; 0·3 + 2 = 2; 2·3 − 1 = **5**. Three multiplications."),
            ("Why does the first digit of the cubic's root have to be 2?", "At x = 20 the left side x³ + 2x² + 6x is still below 13,258, and at x = 30 it is above, so the root is in the twenties. In the widget, the trials 1 and 2 keep the sign at the tens place and 3 changes it."),
            (f"After shifting by 20, the cubic becomes y³ + 62y² + 1286y − 4338. What is its root?", f"The rest of the original root: about {float(rt['cubic']['root']) - 20:.6f}, whose first digit is 2."),
            ("Why does the quartic need care?", f"It has two positive roots, {rt['quartic']['root']} and {d['other']}. Counting up from zero finds the smaller; to find the larger, shift past the first."),
            ("What does Newton's method need that Qin's does not?", "The derivative: the slope of the polynomial at the current guess. In exchange it doubles the correct digits each step."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Ch'in Chiu-shao in the Dictionary of Scientific Biography", text="Ho Peng-yoke's entry, with the quartic and the degree-10 circular-city equation, the zero symbol and the red and black rods.",
                 draw=C.draw_book, link="https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf", link_text="DSB entry (MacTutor)",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("scholar", "s_sin.c (IBM Accurate Mathematical Library)", "GNU C library source, on codebrowser.dev", "https://codebrowser.dev/glibc/glibc/sysdeps/ieee754/dbl-64/s_sin.c.html", "Polynomials written in nested (Horner) form inside do_sin"),
        ]),
        C.prove_it_section(ctx, "QinJiushao", d["checks"],
                           "the circular-city root, the cubic, the quartic's two roots and the fifth root of 2 digit by digit in exact decimals, 5,000 random polynomials with known roots, and the comparison with bisection and Newton's method.",
                           ["static BigDecimal[] shift(", "static BigDecimal digitRoot("]),
    ]
    return dict(
        title="Horner's Method, Nearly Six Centuries Early", date="1247 CE",
        description="Era 2, topic 9 of The Algorithm Evolution Atlas: Qin Jiushao's digit-by-digit root method of 1247, on a counting board you can step through, with the degree-10 circular-city equation.",
        lede="Find the root one digit at a time; after each digit, shift the polynomial so the rest of the root is a fresh root of a new equation. Qin Jiushao wrote it down in 1247. Europe named it after Horner in 1819.",
        fieldnote="This official wrote his mathematics while in mourning, and he put on the counting board a procedure the West would find again centuries later. Each new digit shifts the whole polynomial, so the next digit is found the same way, and no power is ever computed directly.",
        card=[("When", "*Shushu jiuzhang*, 1247 (**documented**); Ruffini c. 1805 and Horner 1819 (**disputed** for Ruffini)"),
              ("Where", "Southern Song China"),
              ("What hurt", "Equations of degree 3, 4 and 10 from surveying and areas"),
              ("The fix", "Digit by digit, shifting the polynomial by multiply-and-add"),
              ("Cost", f"{ev['horner']} multiplications to evaluate degree 10, against {ev['term']} term by term")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `QinJiushao.java`.",
    )
