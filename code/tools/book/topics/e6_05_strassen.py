"""Era 6, topic 5: fast matrix multiplication (Strassen). Every number is parsed from Strassen.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("seven: "):
            parts = ln[len("seven: "):].split(" ; ")
            d["seven"] = dict(products=[p.strip() for p in parts[0].split(", ")], results=[r.strip() for r in parts[1].split(", ")])
        elif ln.startswith("counts: "):
            d["counts"] = re.findall(r"n=([\d,]+): school ([\d,]+) multiplications \+ ([\d,]+) additions, Strassen to 1 x 1 ([\d,]+) \+ ([\d,]+)", ln)
            d["first_win"] = re.search(r"first beats the school method at n = ([\d,]+)", ln).group(1)
            d["cut"] = re.findall(r"(\d+): ([\d,]+)", re.search(r"block size c gives totals (.*?) ; best", ln).group(1))
            m = re.search(r"best c = (\d+), ([\d,]+) operations against ([\d,]+) for the school method \(([\d.]+) times fewer\)", ln)
            d["best"] = dict(c=m.group(1), ops=m.group(2), school=m.group(3), times=m.group(4))
            d["cut_n"] = re.search(r"for n = ([\d,]+), switching", ln).group(1)
        elif m := re.match(r"agree: two random (\d+) x \d+ matrices .*? all ([\d,]+) entries identical, school and Strassen ; school ([\d,]+) multiplications and ([\d,]+) additions ; Strassen to 1 x 1 ([\d,]+) and ([\d,]+) ; Strassen with school blocks of (\d+) ([\d,]+) and ([\d,]+)", ln):
            d["agree"] = dict(n=m.group(1), entries=m.group(2), sm=m.group(3), sa=m.group(4), fm=m.group(5), fa=m.group(6), c=m.group(7), cm=m.group(8), ca=m.group(9))
        elif m := re.match(r"rounding: two random (\d+) x \d+ matrices .*? school ([\d.e+-]+), Strassen to 1 x 1 ([\d.e+-]+) \((\d+) times larger\), Strassen with school blocks of (\d+) ([\d.e+-]+)", ln):
            d["round"] = dict(n=m.group(1), school=m.group(2), fast=m.group(3), times=m.group(4), c=m.group(5), mixed=m.group(6))
        elif m := re.match(r"inverse: a random (\d+) x \d+ matrix .*? Gauss-Jordan elimination ([\d,]+) multiplications and divisions ; .*? Strassen products\) ([\d,]+) ; matrix times inverse differs from the identity by at most ([\d.e+-]+) and ([\d.e+-]+) ; at ([\d,]+) the counts would be ([\d,]+) against ([\d,]+)", ln):
            d["inv"] = dict(n=m.group(1), gj=m.group(2), blk=m.group(3), e1=m.group(4), e2=m.group(5), big=m.group(6), gj_big=m.group(7), blk_big=m.group(8))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def seven_svg(d):
    prods, res = d["seven"]["products"], d["seven"]["results"]

    def draw(t, standalone):
        o = []
        W, H = 760, 420
        o.append(C.text(20, 30, "A = [a b; c d], B = [e f; g h]: seven products, then additions and subtractions only", t["ink"], 13, "start", 700))
        ys = [70 + i * 46 for i in range(7)]
        for i, p in enumerate(prods):
            o.append(C.rect(20, ys[i] - 16, 220, 32, t["surface"], t["blue"], 1.6, 4))
            o.append(C.text(32, ys[i] + 5, p.replace("m", "m", 1), t["ink"], 13, "start", 700))
        rys = [100 + i * 82 for i in range(4)]
        names = ["top left", "top right", "bottom left", "bottom right"]
        for j, r in enumerate(res):
            lhs, rhs = r.split(" = ")
            o.append(C.rect(520, rys[j] - 22, 220, 44, t["surface"], t["red"], 1.6, 4))
            o.append(C.text(532, rys[j] - 3, f"{names[j]}: {lhs}", t["ink"], 12, "start", 700))
            o.append(C.text(532, rys[j] + 14, f"= {rhs}", t["ink"], 12))
            for term in re.findall(r"([+-]?)m(\d)", rhs):
                sign, k = term
                k = int(k) - 1
                col = t["red"] if sign == "-" else t["axis"]
                o.append(C.line(240, ys[k], 520, rys[j], col, 1.4, ";stroke-dasharray:5 4" if sign == "-" else ""))
        o.append(C.text(20, H - 10, "Grey lines add a product, red dashed lines subtract it. No step uses ab = ba, so the letters may be blocks of a larger matrix.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Strassen's seven products and how they combine", t, standalone, 0.55, 760)
    return draw


ST_HTML = """
<div class="board st-board">
  <div style="min-width:0">
    <div class="st-mats">
      <div class="st-m" id="st-a"></div><span class="st-x">×</span><div class="st-m" id="st-b"></div><span class="st-x">=</span><div class="st-m st-out" id="st-c"></div>
    </div>
    <div class="st-prods" id="st-prods"></div>
    <button type="button" id="st-new">New numbers</button>
  </div>
  <div style="min-width:0">
    <label class="st-row">Matrix size n = 2^k <input type="range" id="st-k" min="1" max="12" value="10"><output id="st-ko"></output></label>
    <label class="st-row">Switch to the school rule for blocks up to <select id="st-cut"><option value="1">1 × 1 (Strassen all the way)</option><option value="8" selected>8 × 8</option><option value="32">32 × 32</option><option value="128">128 × 128</option></select></label>
    <div class="st-stats" id="st-stats"></div>
    <p class="say" id="st-say" aria-live="polite"></p>
  </div>
</div>
"""

ST_CSS = """
.st-mats{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.st-m{display:grid;grid-template-columns:repeat(2,3.2em);gap:3px;border-left:2px solid var(--ink);border-right:2px solid var(--ink);padding:2px 4px}
.st-m span{font:14px var(--mono);text-align:center;padding:3px 0}
.st-out span{color:var(--red);font-weight:600}
.st-x{font-size:20px}
.st-prods{font:12.5px var(--mono);display:grid;gap:2px;margin:10px 0}
.st-row{display:grid;gap:2px;font-size:14px;margin:6px 0}
.st-row input,.st-row select{width:100%;font:inherit}
.st-row output{font:13px var(--mono);color:var(--muted)}
.st-stats{font:13px var(--mono);display:grid;gap:3px}
"""

ST_JS = r"""
(() => {
  const aBox = document.getElementById("st-a");
  if (!aBox) return;
  let seed = 1969, M;
  const r = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 2147483648 * 19) - 9; };
  function fresh() { M = Array.from({length: 8}, r); showMats(); }
  function showMats() {
    const [a, b, c, dd, e, f, g, h] = M;
    const fill = (box, vals) => { box.innerHTML = ""; vals.forEach(v => el("span", {}, box, v)); };
    const m = [(a + dd) * (e + h), (c + dd) * e, a * (f - h), dd * (g - e), (a + b) * h, (c - a) * (e + f), (b - dd) * (g + h)];
    fill(aBox, [a, b, c, dd]); fill(document.getElementById("st-b"), [e, f, g, h]);
    fill(document.getElementById("st-c"), [m[0] + m[3] - m[4] + m[6], m[2] + m[4], m[1] + m[3], m[0] - m[1] + m[2] + m[5]]);
    const p = document.getElementById("st-prods"); p.innerHTML = "";
    const txt = [`(a+d)(e+h) = ${a + dd}·${e + h}`, `(c+d)e = ${c + dd}·${e}`, `a(f−h) = ${a}·${f - h}`, `d(g−e) = ${dd}·${g - e}`, `(a+b)h = ${a + b}·${h}`, `(c−a)(e+f) = ${c - a}·${e + f}`, `(b−d)(g+h) = ${b - dd}·${g + h}`];
    m.forEach((v, i) => el("div", {}, p, `m${i + 1} = ${txt[i]} = ${v}`));
    const ok = m[0] + m[3] - m[4] + m[6] === a * e + b * g && m[2] + m[4] === a * f + b * h && m[1] + m[3] === c * e + dd * g && m[0] - m[1] + m[2] + m[5] === c * f + dd * h;
    el("div", {}, p, ok ? "7 multiplications; the school rule's 8 give the same four numbers." : "mismatch");
  }
  function count(n, c) { if (n <= c) return [n * n * n, n * n * (n - 1)]; const [m, a] = count(n / 2, c); return [7 * m, 7 * a + 18 * (n / 2) * (n / 2)]; }
  function update() {
    const k = +document.getElementById("st-k").value, n = 2 ** k, c = +document.getElementById("st-cut").value;
    document.getElementById("st-ko").textContent = `n = ${fmt(n)}`;
    const [sm, sa] = count(n, n), [fm, fa] = count(n, Math.min(c, n));
    const st = document.getElementById("st-stats"); st.innerHTML = "";
    el("div", {}, st, `school rule: ${fmt(sm)} multiplications + ${fmt(sa)} additions`);
    el("div", {}, st, `Strassen: ${fmt(fm)} multiplications + ${fmt(fa)} additions`);
    const ratio = (sm + sa) / (fm + fa);
    const same = Math.abs(ratio - 1) < 1e-9;
    el("div", {}, st, `all operations: ${same ? "the same" : ratio > 1 ? ratio.toFixed(2) + " times fewer with Strassen" : (1 / ratio).toFixed(2) + " times more with Strassen"}`);
    document.getElementById("st-say").textContent = same ? "At this size the whole matrix is one small block: the school rule does all the work." : ratio > 1 ? "Seven products at every level: the saving grows with the size." :
      "For small matrices the extra additions cost more than the saved multiplications. Switch to the school rule for small blocks, or try a larger n.";
  }
  document.getElementById("st-new").addEventListener("click", fresh);
  document.getElementById("st-k").addEventListener("input", update);
  document.getElementById("st-cut").addEventListener("change", update);
  fresh(); update();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Strassen's method combined older ideas, and where it led")
    W = 210
    nodes = {
        "rule": (20, 20, "The school rule", "every row against every column: n³", "", "ink"),
        "elim": (395, 20, "Elimination", "solve, invert: also about n³", "Era 2, topic 1; Gauss", "ink"),
        "dc": (770, 20, "Divide and conquer", "split in halves, recurse", "the FFT, topic 1", "ink"),
        "str": (395, 180, "Strassen's products", "⊕ seven products for 2 × 2 blocks: n^2.807", "Zürich, 1969", "red"),
        "inv": (20, 340, "Faster inversion", "blocks, with fast products inside", "", "ink"),
        "race": (395, 340, "The exponent race", "2.796 (1978) … 2.3755 (1990)", "galactic algorithms", "ink"),
        "ai": (770, 340, "Found with AI", "ω < 2.371177", "AlphaEvolve, 2026", "ink"),
        "today": (395, 490, "Today", "Strassen's method in practice; the record far below it", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("rule", "str", ports=("bottom", "top:0.15"))
    D.edge("elim", "str", ports=("bottom", "top"), label="\"not optimal\"", at=0.5, dx=8, anchor="start")
    D.edge("dc", "str", ports=("bottom", "top:0.85"))
    D.edge("str", "inv", ports=("bottom:0.15", "top"))
    D.edge("str", "race", ports=("bottom", "top"))
    D.edge("race", "ai", ports=("right", "left"))
    D.edge("race", "today", ports=("bottom", "top"))
    D.text(20, 615, "Bounds from Wikipedia's table and the 2026 arXiv paper. Galactic: faster only for matrices far too large for present-day computers.", "caption")
    return D


def chain(d):
    a, b, r, i = d["agree"], d["best"], d["round"], d["inv"]
    steps = [
        (f"Multiplying {a['n']} × {a['n']} matrices: {a['sm']} multiplications",
         f"Seven products per level: {a['fm']} multiplications, the same {a['entries']} entries", "Strassen, 1969"),
        (f"But {a['fa']} additions: all the way down, Strassen wins only from n = {d['first_win']}",
         f"Use the school rule for small blocks: at n = {d['cut_n']}, {b['times']} times fewer operations", "best block size here: " + b["c"]),
        (f"Rounding: errors {r['times']} times larger than the school rule's",
         f"School blocks of {r['c']} cut the error to {C.sci(r['mixed'])}", "a trade, not a free lunch"),
        (f"Inverting a {i['n']} × {i['n']} matrix by Gauss–Jordan: {i['gj']} multiplications",
         f"Invert by blocks with fast products: {i['blk']}", "\"Gaussian elimination is not optimal\""),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from n³ to n^2.807 and its price")
    L, R, bw = 20, 560, 380
    for k, (pain, fix, src) in enumerate(steps):
        y = 20 + k * (rowh + gap)
        px, fx = (L, R) if k % 2 == 0 else (R, L)
        D.node(f"p{k}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{k}", fx, y, bw, rowh, [("THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{k}", f"f{k}", ports=("right", "left") if k % 2 == 0 else ("left", "right"), label="fixed by", at=0.5, dy=-8)
        if k + 1 < len(steps):
            D.edge(f"f{k}", f"p{k + 1}", ports=("bottom", "top"), label="which leaves a new problem" if k == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    cn, b, a, r, i = d["counts"], d["best"], d["agree"], d["round"], d["inv"]
    count_rows = [[n, sm, fm, sa, fa] for n, sm, sa, fm, fa in cn]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Splitting a problem in halves had made the Fourier transform fast (topic 1). Split two matrices into four blocks each, and the school rule needs eight products of blocks; Strassen found seven that are enough, and the split can be repeated inside every block. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Strassen's seven products. Blue: where matters stand today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Seven products instead of eight", toc="Try it", blocks=[
            dict(type="p", text="Left: two 2 × 2 matrices of small random numbers, their product, and Strassen's seven products that make it. Right: the counts for matrices of size n = 2^k, split again and again, with the option of switching to the school rule when the blocks become small."),
            dict(type="widget", html=ST_HTML, js=ST_JS, css=ST_CSS,
                 fallback=dict(type="table", head=["n", "School: multiplications", "Strassen: multiplications", "School: additions", "Strassen: additions"], num=[0, 1, 2, 3, 4], rows=count_rows),
                 note="In the interactive edition you can multiply matrices with seven products and watch the counts grow with the size."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="One saved product, at every level", toc="How it works", blocks=[
            dict(type="p", text="**Seven products.** For [a b; c d] × [e f; g h] the school rule makes eight products (ae, bg, af, …). Strassen's seven products, each of one sum by another, give all four entries by additions and subtractions alone. The program checked the formulas exactly, coefficient by coefficient, and on 1,000 random pairs."),
            dict(type="svg", name="seven", draw=seven_svg(d), alt="Strassen's seven products and how they combine", width=760),
            dict(type="p", text="**Blocks.** None of the formulas uses ab = ba, which fails for matrices. So a, b, … h may be blocks: cut each n × n matrix into four blocks of n/2 × n/2, make seven products of blocks, and make each of those the same way. For n = 2^k that is 7^k multiplications instead of 8^k, which is n^(log₂ 7) = n^2.807 instead of n³."),
            dict(type="p", text="**The price.** Each level adds 18 additions of blocks. They cost little for large blocks and a lot for small ones, so a practical version switches to the school rule below some block size."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Saving one multiplication in eight looks like nothing. Saved again inside every one of the seven, at every level of the split, it changes the exponent, and with large enough matrices any change in the exponent wins."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Counting operations", toc="Measured", blocks=[
            dict(type="table", head=["n", "School: multiplications", "Strassen: multiplications", "School: additions", "Strassen: additions"], num=[0, 1, 2, 3, 4], rows=count_rows, hl=len(count_rows) - 1),
            dict(type="p", text=f"Counting multiplications and additions together, Strassen all the way down to single numbers first beats the school rule at n = {d['first_win']}. Switching to the school rule for small blocks does better: for n = {d['cut_n']} the program tried block sizes from 8 to 256, and the best, {b['c']}, needs {b['ops']} operations against {b['school']} ({b['times']} times fewer)."),
            dict(type="table", head=["Switch below block size", f"Operations for n = {d['cut_n']}"], num=[0, 1], rows=[list(x) for x in d["cut"]], hl=0),
            dict(type="p", text=f"**Real products.** Two random {a['n']} × {a['n']} matrices of whole numbers between −1000 and 1000, multiplied both ways: all {a['entries']} entries identical. School: {a['sm']} multiplications and {a['sa']} additions; Strassen to 1 × 1: {a['fm']} and {a['fa']}; Strassen with school blocks of {a['c']}: {a['cm']} and {a['ca']}."),
            dict(type="p", text=f"**Rounding.** With decimals, the extra additions and subtractions cost accuracy. Two random {r['n']} × {r['n']} matrices of decimals, against the exact product: largest error {C.sci(r['school'])} for the school rule, {C.sci(r['fast'])} for Strassen all the way down ({r['times']} times larger), {C.sci(r['mixed'])} with school blocks of {r['c']}."),
            dict(type="p", text=f"**Inversion.** A {i['n']} × {i['n']} matrix inverted by Gauss–Jordan elimination took {i['gj']} multiplications and divisions; inverted by 2 × 2 blocks (two half-size inverses and six half-size Strassen products) it took {i['blk']}. Both inverses times the matrix give the identity to within {C.sci(i['e2'])}. At n = {i['big']} the counts would be {i['gj_big']} against {i['blk_big']}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Three pages with a claim for a title", toc="The evidence", blocks=[
            dict(type="p", text="Volker Strassen, \"Gaussian elimination is not optimal\", *Numerische Mathematik* 13: 354–356 (1969). MacTutor: in 1969 he \"discovered a novel way to multiply two matrices\", with exponent log₂ 7 = 2.808, showing that Gaussian elimination \"is not an optimal solution\"; he had joined the Institute of Applied Mathematics at the University of Zürich in 1968. Peter Bürgisser's lecture notes add that 2 × 2 matrices cannot be multiplied with fewer than seven multiplications, and that nine years passed before Pan first improved the exponent."),
            dict(type="p", text="The exponent has been lowered many times since: 2.796 (Pan, 1978), 2.3755 (Coppersmith and Winograd, 1990), 2.3728639 (Le Gall, 2014), 2.371339 (Alman, Duan, Vassilevska Williams, Xu, Xu and Zhou, 2024), and, in August 2026, 2.371177, by a team using the AI system AlphaEvolve (arXiv 2608.16884). Wikipedia: \"Unlike algorithms with faster asymptotic complexity, Strassen's algorithm is used in practice\"; the later ones \"are not used in practice, because they are galactic algorithms\". Why Strassen looked for the method is not in any source the catalog opened."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Elimination, not optimal", toc="Full circle", blocks=[
            dict(type="p", text="The elimination that Strassen's title names was done with rods on Chinese counting boards two thousand years ago (Era 2, topic 1) and later named after Gauss. For most of that time nobody asked whether it was the fastest possible. Strassen's three pages turned the question into a race that, in 2026, is still being run, partly by machines."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Gauss–Jordan on a {i['n']} × {i['n']} matrix: {i['gj']} multiplications and divisions. The same inverse by blocks with seven-product multiplication: {i['blk']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many multiplications does Strassen's method use for 8 × 8 matrices, all the way down?", "7³ = 343, against 8³ = 512."),
            ("Why must the formulas not use ab = ba?", "Because the letters stand for blocks, and matrix products do not commute."),
            ("Why is Strassen all the way down slower for small n?", "Each level adds 18 block additions; for small blocks they cost more than the multiplication saved."),
            ("What does log₂ 7 ≈ 2.807 measure?", "How fast the work grows: doubling n multiplies the work by 7, not 8."),
            ("Why do the later, faster methods go unused?", "Their hidden constants are so large that they win only for matrices far too large for present-day computers."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Gaussian elimination is not optimal (1969)", text="Strassen's paper, *Numerische Mathematik* 13: 354–356.",
                 draw=C.draw_manuscript, link="https://cr.yp.to/bib/1969/strassen.bibtex", link_text="Bibliographic entry", licence="Drawn placeholder."),
            dict(title="Improving the matrix multiplication exponent with modern optimization and AlphaEvolve (2026)", text="The latest bound, 2.371177.",
                 draw=C.draw_book, link="https://arxiv.org/pdf/2608.16884", link_text="arXiv 2608.16884", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Strassen", d["checks"],
                           "the seven-product formulas exactly and on 1,000 random pairs, operation counts for n up to 4,096, all 65,536 entries of a 256 × 256 product against the school rule, rounding against exact arithmetic, and inversion by blocks against Gauss–Jordan elimination.",
                           ["static double[][] fast(double[][] A, double[][] B, int cutoff)"]),
    ]
    return dict(
        title="Fast Matrix Multiplication", date="1969",
        description="Era 6, topic 5 of The Algorithm Evolution Atlas: Strassen's seven products, n^2.807 instead of n³, its price in additions and rounding, and the exponent race to 2026.",
        lede="Multiplying two-by-two matrices takes eight multiplications, and it seemed it had to. Strassen found seven, and because his trick works on blocks, it works at every level of a split: the exponent drops from 3 to 2.807.",
        fieldnote=f"I multiplied two {a['n']} × {a['n']} matrices with {a['fm']} multiplications instead of {a['sm']}, and every entry matched. The saving has a price, in additions and in rounding, and the program counted that too.",
        card=[("When", "1969"),
              ("Where", "University of Zürich"),
              ("What hurt", "n³ operations to multiply or invert"),
              ("The fix", "Seven block products, recursively"),
              ("Cost", f"n^2.807; {b['times']} times fewer operations at n = {d['cut_n']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Strassen.java`, except the published bounds on the exponent, which are quoted from the reference catalog.",
    )
