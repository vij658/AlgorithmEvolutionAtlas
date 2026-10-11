"""Era 3, topic 1: Cardano's cubic. Every number is parsed from CardanoCubic.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"depress: (.+?) ; shift x = y \+ (\S+) ; (.+?) ; D = \(q/2\)\^2 \+ \(p/3\)\^3 = (\S+) ; u\^3 = (\S+), v\^3 = (\S+) ; y = (\S+) ; x = (\S+)$", ln):
            d["dep"] = dict(eq=m.group(1), shift=m.group(2), depressed=m.group(3), D=m.group(4), u3=m.group(5), v3=m.group(6), y=m.group(7), x=m.group(8))
        elif m := re.match(r"formula: x\^3 \+ 6x = 20 ; D = (\S+) ; u = .*? = (\S+) ; v = .*? = (\S+) ; x = u \+ v = (\S+)$", ln):
            d["f"] = dict(D=m.group(1), u=m.group(2), v=m.group(3), x=m.group(4))
        elif m := re.match(r"product: .* = (\d+)$", ln):
            d["prod"] = int(m.group(1))
        elif m := re.match(r"bombelli: x\^3 = 15x \+ 4 ; D = .*? = (\S+) ; u\^3 = (.+?), v\^3 = (.+?) ; trying .*?\((\d+) tries\): \((.+?)\)\^3 = .+?, \((.+?)\)\^3 = .+? ; x = (\S+) ; the other roots -2 \+ sqrt3 = (\S+) and -2 - sqrt3 = (\S+), all real$", ln):
            g = m.groups()
            d["b"] = dict(D=g[0], u3=g[1], v3=g[2], tries=int(g[3]), u=g[4], v=g[5], x=g[6], o1=g[7], o2=g[8])
        elif m := re.match(r"survey: ([\d,]+) random cubics .*?: ([\d,]+) with three real roots \(([\d.]+)%\), ([\d,]+) with one ; .*?\(([\d,]+) with D = 0, a repeated root\) ; ([\d,]+) cubics with three distinct whole-number roots: D < 0 in (\d+)%$", ln):
            g = m.groups()
            d["s"] = dict(n=g[0], three=g[1], pct=g[2], one=g[3], zero=g[4], n2=g[5], neg=g[6])
        elif m := re.match(r"random: ([\d,]+) cubics .* worst error (\S+)$", ln):
            d["r"] = dict(n=m.group(1), worst=m.group(2))
        elif m := re.match(r"cancel: (.+?) in 64-bit floating point ; u = (\S+), v = (\S+) ; root (\S+) ; plain formula u \+ v = (\S+) \(relative error (\S+)\) ; as .*? (\S+) \((\S+)\) ; plain formula then one Newton step (\S+) \((\S+)\)$", ln):
            g = m.groups()
            d["c"] = dict(eq=g[0], u=g[1], v=g[2], root=g[3], naive=g[4], rel=g[5], stable=g[6], srel=g[7], fixed=g[8], frel=g[9])
    d["checks"] = C.checks(text)
    return d


sci, pretty = C.sci, C.pretty


# ----------------------------------------------------------------------------------------------------------------------
def bombelli(d):
    """Bombelli's calculation, as a chain of boxes."""
    b = d["b"]
    D = Diagram(1000, 220, "Bombelli's calculation for x³ = 15x + 4: through square roots of negatives to the real root 4")
    W, H = 220, 110
    boxes = [("q", "The recipe", ["D = (q/2)² + (p/3)³", f"= 4 − 125 = {b['D']}", "√D needs √−121"], "ink"),
             ("u", "Two cubes", [f"u³ = {b['u3']}", f"v³ = {b['v3']}", "(11i is √−121)"], "ink"),
             ("r", "Their cube roots", [f"({b['u']})³ = {b['u3']}", f"({b['v']})³ = {b['v3']}", f"found in {b['tries']} tries"], "ink"),
             ("x", "The answer", [f"x = ({b['u']}) + ({b['v']})", f"= {b['x']}", "4³ = 15·4 + 4 ✓"], "red")]
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title")] + [(s, "combo" if j == 1 else "note") for j, s in enumerate(sub)], color=col)
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "THE IMAGINARY PARTS CANCEL: THE ROUTE PASSES THROUGH √−1, THE ANSWER DOES NOT", "tag")
    D.text(20, 200, f"The other two roots, −2 ± √3 ({b['o1']} and {b['o2']}), are real as well. Numbers from CardanoCubic.java.", "caption")
    return D


CC_HTML = """
<div class="board cc-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="cc-p">p <input id="cc-p" type="range" min="-30" max="30" value="-15"></label><span class="cc-v" id="cc-pv"></span>
      <label for="cc-q">q <input id="cc-q" type="range" min="-60" max="60" value="4"></label><span class="cc-v" id="cc-qv"></span>
    </div>
    <svg id="cc-svg" viewBox="0 0 320 220" role="img" aria-label="The graph of x cubed plus p x minus q, with its real roots marked"></svg>
  </div>
  <div style="min-width:0">
    <div class="cc-eq" id="cc-eq">Solve x³ + px = q</div>
    <ol class="cc-steps" id="cc-steps"></ol>
    <p class="say" id="cc-say" aria-live="polite"></p>
  </div>
</div>
"""

CC_CSS = """
.cc-board .controls{flex-wrap:wrap}
.cc-board input[type=range]{width:min(170px,40vw)}
.cc-v{font-family:var(--mono);font-size:13px;min-width:2.5em;display:inline-block}
.cc-board svg{max-width:360px;display:block;margin:0 auto}
.cc-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.cc-steps li{overflow-wrap:anywhere}
.cc-steps .m{font-family:var(--mono);font-size:12.5px}
.cc-steps .im{color:var(--red)}
.cc-board .say{font-size:14.5px}
.cc-eq{font-family:var(--mono);font-size:14px;font-weight:600;color:var(--ink)}
"""

CC_JS = r"""
(() => {
  const steps = document.getElementById("cc-steps");
  if (!steps) return;
  const svg = document.getElementById("cc-svg");
  const f6 = v => (Math.abs(v) < 5e-7 ? 0 : v).toFixed(6).replace(/\.?0+$/, "") || "0";
  const cx = (re, im) => { const a = f6(Math.abs(im)); return a === "0" ? f6(re) : `${f6(re)} ${im < 0 ? "−" : "+"} ${a === "1" ? "" : a}i`; };
  const cbrtC = (re, im) => { const r = Math.cbrt(Math.hypot(re, im)), t = Math.atan2(im, re) / 3; return [r * Math.cos(t), r * Math.sin(t)]; };
  function draw(p, q, roots) {
    svg.innerHTML = "";
    const W = 320, H = 220, X = 7, f = x => x * x * x + p * x - q;
    let lo = Infinity, hi = -Infinity; for (let i = 0; i <= 200; i++) { const y = f(-X + 2 * X * i / 200); lo = Math.min(lo, y); hi = Math.max(hi, y); }
    const Y = Math.min(Math.max(Math.abs(lo), Math.abs(hi)), 120);
    const sx = x => 10 + (x + X) / (2 * X) * (W - 20), sy = y => H / 2 - Math.max(-1, Math.min(1, y / Y)) * (H / 2 - 12);
    sv("line", { x1: 10, y1: H / 2, x2: W - 10, y2: H / 2, stroke: "var(--axis)", "stroke-width": 1 }, svg);
    sv("line", { x1: sx(0), y1: 6, x2: sx(0), y2: H - 6, stroke: "var(--axis)", "stroke-width": 1 }, svg);
    const pts = []; for (let i = 0; i <= 240; i++) { const x = -X + 2 * X * i / 240; pts.push(`${sx(x).toFixed(1)},${sy(f(x)).toFixed(1)}`); }
    sv("polyline", { points: pts.join(" "), fill: "none", stroke: "var(--blue)", "stroke-width": 2 }, svg);
    roots.forEach(r => { if (Math.abs(r) <= X) sv("circle", { cx: sx(r), cy: H / 2, r: 4.5, fill: "var(--red)" }, svg); });
    sv("text", { x: 12, y: 16, fill: "var(--muted)", "font-size": 10 }, svg, `y = x³ ${p < 0 ? "−" : "+"} ${Math.abs(p)}x ${q < 0 ? "+" : "−"} ${Math.abs(q)}, x from −7 to 7`);
  }
  function show() {
    const p = +document.getElementById("cc-p").value, q = +document.getElementById("cc-q").value;
    document.getElementById("cc-pv").textContent = p; document.getElementById("cc-qv").textContent = q;
    document.getElementById("cc-eq").textContent = `Solve x³ ${p < 0 ? "−" : "+"} ${Math.abs(p)}x = ${q}`;
    const D = (q / 2) ** 2 + (p / 3) ** 3;
    steps.innerHTML = "";
    const li = h => { el("li", {}, steps).innerHTML = h; };
    li(`D = (q/2)² + (p/3)³ = <span class="m">${f6(D)}</span>`);
    let roots = [], say;
    if (D >= 0) {
      const u = Math.cbrt(q / 2 + Math.sqrt(D)), v = Math.cbrt(q / 2 - Math.sqrt(D));
      li(`u = ∛(q/2 + √D) = <span class="m">${f6(u)}</span>, v = ∛(q/2 − √D) = <span class="m">${f6(v)}</span>`);
      li(`x = u + v = <span class="m">${f6(u + v)}</span>`);
      roots = [u + v];
      say = D > 0 ? "D is positive: the recipe uses only real numbers, and the cubic has one real root (the other two are complex)."
                  : "D is zero: a repeated root.";
    } else {
      const s = Math.sqrt(-D), [ur, ui] = cbrtC(q / 2, s);
      li(`√D = √(${f6(D)}) = <span class="m im">${f6(s)}i</span>: the square root of a negative number`);
      li(`u³ = <span class="m">${cx(q / 2, s)}</span>, v³ = <span class="m">${cx(q / 2, -s)}</span>`);
      li(`u = <span class="m">${cx(ur, ui)}</span>, v = <span class="m">${cx(ur, -ui)}</span>`);
      li(`x = u + v = <span class="m">${f6(2 * ur)}</span> <span class="im">(the imaginary parts cancel)</span>`);
      const w = [[1, 0], [-0.5, Math.sqrt(3) / 2], [-0.5, -Math.sqrt(3) / 2]];
      roots = w.map(([a, b]) => 2 * (ur * a - ui * b));
      say = `D is negative, so the recipe passes through √−1, yet all three roots are real: ${roots.map(f6).join(", ")}. This is the case Bombelli calculated through in 1572.`;
    }
    const res = Math.max(...roots.map(r => Math.abs(r ** 3 + p * r - q)));
    li(`check: x³ + px − q = <span class="m">${res.toExponential(1)}</span>`);
    document.getElementById("cc-say").textContent = say;
    draw(p, q, roots);
  }
  ["cc-p", "cc-q"].forEach(id => document.getElementById(id).addEventListener("input", show));
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Cardano's cubic combined older ideas, and where it led")
    W, H = 210, 86
    nodes = {
        "jab": (20, 20, "Completing the square", "a quadratic by recipe", "al-Khwarizmi, Era 2 topic 6", "ink"),
        "qin": (395, 20, "Roots digit by digit", "any degree, slowly", "Qin Jiushao, Era 2 topic 9", "ink"),
        "con": (770, 20, "Public contests", "secret methods won prizes", "Fior and Tartaglia, 1535", "ink"),
        "car": (395, 170, "Cardano's formula", "⊕ a substitution: cubic → quadratic + cube roots", "Ars Magna, 1545", "red"),
        "fer": (20, 330, "Ferrari's quartic", "reduce degree 4 to degree 3", "in Ars Magna, 1545", "ink"),
        "bom": (395, 330, "Bombelli's √−1", "rules for 'plus of minus'", "Algebra, 1572", "ink"),
        "new": (770, 330, "Newton's method", "when formulas cancel or stop", "topic 5", "ink"),
        "fft": (395, 480, "Complex numbers at work", "the FFT runs on roots of unity", "topic 9; today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("jab", "car", ports=("bottom", "top:0.15"))
    D.edge("qin", "car", ports=("bottom", "top"))
    D.edge("con", "car", ports=("bottom", "top:0.85"))
    D.edge("car", "fer", ports=("bottom:0.1", "top:0.7"))
    D.edge("car", "bom", ports=("bottom", "top"))
    D.edge("car", "new", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("bom", "fft", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: Newton's method answers the formula's weaknesses; it does not reuse the formula itself.", "caption")
    return D


def chain(d):
    s, c = d["s"], d["c"]
    steps = [
        ("Cubic equations were solved case by case, or one digit at a time",
         "A substitution turns the cubic into a quadratic in u³, then two cube roots", "del Ferro, Tartaglia; Cardano, 1545"),
        ("And the fourth degree?",
         "Ferrari reduces a quartic to a cubic", "Ars Magna, 1545"),
        (f"For three real roots the formula needs √ of a negative: D < 0 in {s['neg']}% of such cubics",
         "Calculate with √−1 anyway: the imaginary parts cancel", "Bombelli, 1572"),
        (f"In floating point the formula can cancel: relative error {sci(c['rel'])}",
         "Rearrange it, or correct the answer with Newton's method", "topic 5"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a secret recipe to complex numbers")
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
    dp, f, b, s, r, c = d["dep"], d["f"], d["b"], d["s"], d["r"], d["c"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Al-Khwarizmi had solved quadratics by completing the square (Era 2, topic 6); Qin Jiushao dug out roots of any degree one digit at a time (Era 2, topic 9). In Renaissance Italy, where mathematicians won pupils and prizes in public contests, the cubic fell to a substitution that turns it into a quadratic. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Cardano's formula. Blue: where its complex numbers work today."),
        ]),
        dict(id="solve", eyebrow="Try it", title="Follow the recipe, even through √−1", toc="Try it", blocks=[
            dict(type="p", text="Choose p and q in x³ + px = q. The steps on the right are Cardano's recipe. When D is positive, everything stays real. When D is negative, the recipe takes the square root of a negative number, and Bombelli's rules carry it through: watch the imaginary parts cancel. The graph marks the real roots. The starting values are Bombelli's x³ = 15x + 4."),
            dict(type="widget", html=CC_HTML, js=CC_JS, css=CC_CSS,
                 fallback=dict(type="diagram", name="bombelli", diagram=bombelli(d)),
                 note="In the interactive edition you can change p and q and follow the recipe for any cubic of this form."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="recipe", eyebrow="How it works", title="A cubic becomes a quadratic", toc="How it works", blocks=[
            dict(type="p", text="**Step 1: remove the square term.** Any cubic ax³ + bx² + cx + d = 0 loses its x² term when x is shifted by b/(3a). The program on one example:"),
            dict(type="table", head=["Cubic", "Shift", "Without the square term", "Root"], num=[],
                 rows=[[pretty(dp["eq"]), f"x = y + {dp['shift']}", pretty(dp["depressed"]), f"y = {dp['y']}, so x = {dp['x']}"]]),
            dict(type="p", text="**Step 2: split the unknown in two.** Write y = u + v. Then y³ = u³ + v³ + 3uv(u + v). Choose 3uv = −p, and the cubic y³ + py + q = 0 becomes u³ + v³ = −q. Knowing both the sum and the product of u³ and v³ means they are the two roots of a quadratic, which al-Khwarizmi could already solve:"),
            dict(type="callout", kind="key", label="The formula",
                 text="u³, v³ = −q/2 ± √D, where D = (q/2)² + (p/3)³, and y = ∛(u³) + ∛(v³)."),
            dict(type="p", text=f"On x³ + 6x = 20 (here written with q on the right): D = {f['D']}, u = ∛(√108 + 10) = {f['u']}, v = −∛(√108 − 10) = {f['v']}, and x = u + v = **{f['x']}**. A cubic has become a quadratic plus two cube roots."),
            dict(type="p", text=f"**Step 3: the trap.** When the cubic has three real roots, D is negative. The program checked {s['n2']} cubics with three distinct whole-number roots: D < 0 in **{s['neg']}%** of them. Among {s['n']} random cubics, {s['three']} ({s['pct']}%) had three real roots, so the recipe needs square roots of negatives about half the time. Cardano had already multiplied (5 + √−15)(5 − √−15) = {d['prod']} and called it \"so subtle that it is useless\". Bombelli calculated straight through:"),
            dict(type="diagram", name="bombelli-steps", diagram=bombelli(d)),
            dict(type="p", text=f"The program then solved {r['n']} random cubics with known roots by the formula in complex arithmetic. It recovered every root; the worst error was {sci(r['worst'])}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Reduce a new problem to one you can already solve: the cubic to a quadratic, the quartic to a cubic. And when the method passes through something that \"cannot exist\", calculate anyway; the impossible quantities cancel and the answer is real."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Where the formula breaks", toc="Measured", blocks=[
            dict(type="p", text=f"A formula is exact; a computer is not. For {pretty(c['eq'])} the root is tiny, and u and v are large and nearly opposite, so u + v subtracts two nearly equal numbers and loses most of its digits:"),
            dict(type="table", head=["Method (64-bit floating point)", "Value", "Relative error"], num=[2],
                 rows=[["True root", c["root"], "—"], ["Plain formula, u + v", c["naive"], sci(c["rel"])],
                       ["Rearranged: (u³ + v³)/(u² − uv + v²)", c["stable"], sci(c["srel"])],
                       ["Plain formula, then one Newton step (topic 5)", c["fixed"], sci(c["frel"])]]),
            dict(type="p", text="The rearranged form adds only positive quantities, so nothing cancels. A single correction step of Newton's method (topic 5) repairs the plain formula too. This is one reason computers find roots by iteration rather than by formula."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A secret, an oath, and a book", toc="The evidence", blocks=[
            dict(type="p", text="Scipione del Ferro solved one form of the cubic \"around 1515 but kept his work a complete secret until just before his death, in 1526\" (MacTutor). Antonio Fior challenged Niccolò Tartaglia to a contest in 1535; \"in the early hours of 13 February 1535, inspiration came to Tartaglia\", and he solved Fior's problems in under two hours. In March 1539 Tartaglia gave the method to Girolamo Cardano, in verse, after Cardano swore to keep it secret. In 1543 Cardano and Lodovico Ferrari saw del Ferro's notes in Bologna, and Cardano felt free to publish: *Ars Magna* (Nuremberg, 1545), with Ferrari's solution of the quartic. Tartaglia's dislike \"turned into a pathological hatred\" (all **documented**, MacTutor)."),
            dict(type="p", text="Rafael Bombelli's *Algebra* (1572) named √−n \"plus of minus\" and gave rules such as \"plus of minus times plus of minus makes minus\". The example x³ = 15x + 4 is given as Bombelli's in secondary sources (Merino); the *Algebra* itself was not opened for this page (**documented** in secondary sources only)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The cube roots of one", toc="Full circle", blocks=[
            dict(type="p", text="A cube root has three values: one, and that one times ω or ω², where ω = −½ + (√3/2)i is a cube root of 1. The program finds all three roots of every cubic exactly this way."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="The numbers Cardano called useless and Bombelli made rules for are now the working material of computation. Gauss's fast Fourier transform (topic 9) is built from roots of unity like ω; it runs inside phones and in audio and image software, in complex arithmetic."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does shifting x by b/(3a) remove the x² term?", "Expanding a(y − b/(3a))³ gives −b y² from the cube, which cancels the +b y² from b(y − b/(3a))²."),
            ("Why must 3uv = −p?", "Then the 3uv(u + v) term cancels the py term, leaving only u³ + v³ = −q."),
            ("Is the irreducible case rare?", f"No. Every cubic with three distinct real roots has D < 0; in the program's random sample that was {s['pct']}% of all cubics."),
            ("What is (2 + i)³?", "(2 + i)² = 3 + 4i, and (3 + 4i)(2 + i) = 2 + 11i. That is why 2 + i is a cube root of 2 + √−121."),
            ("Why did the plain formula lose its digits?", f"u = {c['u']} and v = {c['v']} are large and nearly opposite, while their sum is {c['root']}: subtracting nearly equal numbers leaves mostly rounding error."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Ars Magna (Nuremberg, 1545)", text="Cardano's book, with the cubic and Ferrari's quartic. The Source Library has all 172 pages, scanned by Smithsonian Libraries, with an English translation.",
                 draw=C.draw_book, link="https://sourcelibrary.org/book/cardano-ars-magna-1545-first-edition-cardano", link_text="Source Library",
                 licence="Drawn placeholder; the scans are public domain."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "CardanoCubic", d["checks"],
                           "Bombelli's cube roots in exact integer complex arithmetic, the sign of D against the number of real roots for 100,000 random cubics, all three roots of 100,000 more cubics by the formula, and the cancellation and its repairs.",
                           ["static C[] cardano("]),
    ]
    return dict(
        title="Cardano's Cubic", date="1545 CE",
        description="Era 3, topic 1 of The Algorithm Evolution Atlas: the cubic formula of del Ferro, Tartaglia and Cardano, Bombelli's calculation through square roots of negative numbers, and where the formula fails in floating point.",
        lede="For three thousand years, equations of the second degree were solved by recipe. In sixteenth-century Italy the third degree fell, in secret, in a contest and in a quarrel over a broken oath. The recipe had a trap: for many cubics it insists on the square root of a negative number.",
        fieldnote="I expected the people of this century to throw away a recipe that asks for impossible numbers. Instead, one of them wrote rules for the impossible numbers and calculated straight through, and the real answer came out at the other end.",
        card=[("When", "del Ferro c. 1515; Tartaglia 1535; Ars Magna 1545; Bombelli 1572"),
              ("Where", "Bologna, Venice, Milan"),
              ("What hurt", "Cubic equations had no general method"),
              ("The fix", "A substitution that turns the cubic into a quadratic; rules for √−1"),
              ("Cost", "One square root and two cube roots, sometimes of complex numbers")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `CardanoCubic.java`.",
    )
