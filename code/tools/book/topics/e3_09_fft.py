"""Era 3, topic 9: Gauss's fast Fourier transform. Every number is parsed from GaussFFT.java's output."""
import json
import re

import common as C
from diagrams import Diagram

sci = C.sci


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"twelve: observations at 0, 30, \.\.\., 330 degrees: (.+?) ; coefficients (.+?) ; direct (\d+) products ; Gauss's split 4 x 3: (\d+) .*? ; 3 x 4: (\d+) ;", ln):
            d["t"] = dict(obs=[int(v) for v in m.group(1).split(", ")], coef=m.group(2), direct=m.group(3), s43=m.group(4), s34=m.group(5))
        elif m := re.match(r"interpolate: .*?\(largest miss (\S+)\) ; at 15 degrees, between the first two, it gives (\S+)$", ln):
            d["i"] = dict(miss=m.group(1), mid=m.group(2))
        elif m := re.match(r"random: .*?\((\d+) lengths\)$", ln):
            d["rnd"] = m.group(1)
        elif m := re.match(r"count: complex multiplications ; (.+)$", ln):
            d["count"] = re.findall(r"N = ([\d,]+): direct ([\d,]+), fast ([\d,]+) \(([\d,]+) times fewer\)", m.group(1))
        elif m := re.match(r"circle: two random ([\d,]+)-digit numbers .*? the ([\d,]+)-digit product matches Java's BigInteger ; ([\d,]+) complex multiplications, against ([\d,]+) digit products", ln):
            d["circ"] = dict(digits=m.group(1), pdigits=m.group(2), fft=m.group(3), naive=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def split_diagram(d):
    t = d["t"]
    D = Diagram(1000, 270, "Gauss's split of twelve observations: three interleaved groups of four, then four small combinations")
    W, H = 200, 110
    groups = [("g0", "Group 0", "observations 0, 3, 6, 9"), ("g1", "Group 1", "observations 1, 4, 7, 10"), ("g2", "Group 2", "observations 2, 5, 8, 11")]
    for i, (k, tt, sub) in enumerate(groups):
        D.node(k, 20, 30 + i * 74, W, 62, [(tt, "title"), (sub, "note")], color="ink")
    D.node("tw", 300, 85, 200, 90, [("Twiddle", "title"), ("turn each result by an angle", "note"), ("6 products", "combo")], color="ink")
    D.node("cm", 580, 85, 200, 90, [("Combine", "title"), ("four fits of three", "note"), ("4 × 9 = 36 products", "combo")], color="ink")
    D.node("res", 840, 70, 140, 120, [("12 coefficients", "title"), (f"{t['s43']} products", "combo"), (f"direct: {t['direct']}", "note")], color="red")
    for k, _, _ in groups:
        D.edge(k, "tw", ports=("right", "left"))
    D.edge("tw", "cm", ports=("right", "left"))
    D.edge("cm", "res", ports=("right", "left"))
    D.text(20, 20, "THREE FITS OF FOUR: 3 × 16 = 48 PRODUCTS", "tag")
    D.text(20, 258, f"Twelve is three times four, so twelve observations become three groups of four (n = 3n₁ + n₂). Numbers from GaussFFT.java: {t['s43']} products against {t['direct']}.", "caption")
    return D


FT_HTML = """
<div class="board ft-board">
  <div style="min-width:0">
    <svg id="ft-svg" viewBox="0 0 380 250" role="img" aria-label="Twelve observations around a period, and the sum of sines and cosines through them; drag a point up or down"></svg>
    <div class="controls">
      <label><input type="checkbox" id="ft-groups"> show Gauss's three groups</label>
      <button type="button" id="ft-reset">Reset</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The fit</div>
    <div class="ft-out" id="ft-out"></div>
    <div class="eyebrow">How much work</div>
    <div class="controls"><label for="ft-n">N = 2^<input id="ft-n" type="range" min="3" max="24" value="10"></label></div>
    <p class="ft-count" id="ft-count"></p>
  </div>
</div>
"""

FT_CSS = """
.ft-board svg{max-width:440px;display:block;margin:0 auto;touch-action:none}
.ft-board .controls{flex-wrap:wrap;font-size:13.5px}
.ft-board .controls input[type=checkbox]{width:auto;padding:0;margin:0 4px 0 0}
.ft-board .controls label{display:inline-flex;align-items:center}
.ft-board input[type=range]{width:min(200px,45vw)}
.ft-out{font-family:var(--mono);font-size:12.5px;line-height:1.6;margin:4px 0 10px}
.ft-count{font-family:var(--mono);font-size:13px;line-height:1.6}
"""

FT_JS = r"""
(() => {
  const svg = document.getElementById("ft-svg");
  if (!svg) return;
  const BASE = __OBS__, N = 12, W = 380, H = 250;
  let obs = BASE.slice(), drag = -1;
  const lo = -400, hi = 1800;
  const sx = t => 24 + t / 360 * (W - 44), sy = v => H - 22 - (v - lo) / (hi - lo) * (H - 40), iv = py => lo + (H - 22 - py) / (H - 40) * (hi - lo);
  function coeffs() {
    const a = [], b = [];
    for (let k = 0; k <= N / 2; k++) { let c = 0, s = 0; for (let n = 0; n < N; n++) { const t = 2 * Math.PI * n * k / N; c += obs[n] * Math.cos(t); s += obs[n] * Math.sin(t); }
      a.push((k === 0 || k === N / 2 ? 1 : 2) * c / N); b.push((k === 0 || k === N / 2 ? 0 : 2) * s / N); }
    return [a, b];
  }
  const COL = ["var(--red)", "var(--blue)", "var(--yellow)"];
  function draw() {
    svg.innerHTML = "";
    sv("line", { x1: 24, y1: sy(0), x2: W - 20, y2: sy(0), stroke: "var(--axis)", "stroke-width": 1 }, svg);
    for (let g = 0; g <= 360; g += 90) sv("text", { x: sx(g), y: H - 6, "text-anchor": "middle", "font-size": 10, fill: "var(--muted)" }, svg, `${g}°`);
    const [a, b] = coeffs(), pts = [];
    for (let i = 0; i <= 360; i += 2) { const t = i * Math.PI / 180; let v = 0; for (let k = 0; k <= N / 2; k++) v += a[k] * Math.cos(k * t) + b[k] * Math.sin(k * t); pts.push(`${sx(i).toFixed(1)},${sy(v).toFixed(1)}`); }
    sv("polyline", { points: pts.join(" "), fill: "none", stroke: "var(--ink-2)", "stroke-width": 2 }, svg);
    const grp = document.getElementById("ft-groups").checked;
    obs.forEach((v, n) => {
      const c = sv("circle", { cx: sx(n * 30), cy: sy(v), r: 7, fill: grp ? COL[n % 3] : "var(--ink)" }, svg);
      c.addEventListener("pointerdown", e => { drag = n; e.preventDefault(); });
    });
    let html = `mean ${a[0].toFixed(1)}`;
    for (let k = 1; k <= 3; k++) html += `<br>cos ${k}t ${a[k].toFixed(1)}, sin ${k}t ${b[k].toFixed(1)}`;
    html += `<br>(and three more terms, up to 6t)`;
    if (grp) html += `<br><br>red: 0, 3, 6, 9 · blue: 1, 4, 7, 10 · yellow: 2, 5, 8, 11<br>three fits of four, twiddled, then combined: 90 products instead of 144`;
    document.getElementById("ft-out").innerHTML = html;
  }
  function count() {
    const p = +document.getElementById("ft-n").value, n = 2 ** p, direct = n * n, fast = n / 2 * p;
    document.getElementById("ft-count").innerHTML = `N = ${n.toLocaleString("en-US")}<br>direct: ${direct.toLocaleString("en-US")} products<br>fast: ${fast.toLocaleString("en-US")} products<br>${Math.floor(direct / fast).toLocaleString("en-US")} times fewer`;
  }
  svg.addEventListener("pointermove", e => { if (drag < 0) return; const r = svg.getBoundingClientRect(), py = (e.clientY - r.top) / r.height * H; obs[drag] = Math.max(lo, Math.min(hi, Math.round(iv(py)))); draw(); });
  window.addEventListener("pointerup", () => { drag = -1; });
  document.getElementById("ft-groups").addEventListener("change", draw);
  document.getElementById("ft-reset").addEventListener("click", () => { obs = BASE.slice(); draw(); });
  document.getElementById("ft-n").addEventListener("input", count);
  draw(); count();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Gauss's FFT combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "chd": (20, 20, "Sines and chords", "periodic tables", "Ptolemy, Era 2 topic 2", "ink"),
        "lsq": (395, 20, "Fitting observations", "least squares", "topic 8", "ink"),
        "fac": (770, 20, "Factoring the count", "12 = 3 × 4", "Euclid, Era 1 topic 7", "ink"),
        "fft": (395, 170, "Gauss's fast transform", "⊕ split into interleaved groups, then combine", "1805; printed 1866", "red"),
        "fou": (20, 330, "Fourier's series", "heat, 1807; printed 1822", "Paris", "ink"),
        "red": (395, 330, "Rediscoveries", "Runge 1903; Danielson–Lanczos 1942; Good 1958", "", "ink"),
        "ct": (770, 330, "Cooley and Tukey", "N log N for computers", "1965", "blue"),
        "now": (770, 480, "Signals and big numbers", "audio, images, long multiplication", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("chd", "fft", ports=("bottom", "top:0.15"))
    D.edge("lsq", "fft", ports=("bottom", "top"))
    D.edge("fac", "fft", ports=("bottom", "top:0.85"))
    D.edge("fft", "fou", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("fft", "red", ports=("bottom", "top"), dashed=True)
    D.edge("red", "ct", ports=("right", "left"))
    D.edge("ct", "now", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: Gauss's treatise stayed unpublished until 1866; Fourier and the later rediscoverers did not build on it.", "caption")
    return D


def chain(d):
    t, c = d["t"], d["count"]
    big = c[-1]
    steps = [
        (f"A periodic fit from N observations takes N × N products: {t['direct']} for twelve",
         f"Split N = N₁ × N₂ into interleaved groups: {t['s43']} for twelve", "Gauss, 1805"),
        ("Gauss never published it; the treatise appeared only in his collected works, 1866",
         "Found again, and again: Runge 1903, Danielson and Lanczos 1942, Good 1958", "before computers"),
        (f"With computers, N runs to millions: N² is {big[1]} products for N = {big[0]}",
         f"Split all the way down, N a power of 2: {big[2]} products", "Cooley and Tukey, 1965"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from twelve observations to a million")
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
    t, it, cnt, ci = d["t"], d["i"], d["count"], d["circ"]
    js = FT_JS.replace("__OBS__", json.dumps(t["obs"]))
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Astronomers had described periodic motion with sines and chords since Ptolemy (Era 2, topic 2); fitting curves to observations was Gauss's daily work (topic 8). The new idea was arithmetic: if the number of observations factors, the fit can be done in pieces. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Gauss's fast transform. Blue: its return in 1965, and where it runs today."),
        ]),
        dict(id="fit", eyebrow="Try it", title="Fit twelve observations, then split them", toc="Try it", blocks=[
            dict(type="p", text="Twelve observations around a full period, like the positions of an asteroid at twelve points of its orbit. The grey curve is the sum of sines and cosines through all twelve; drag any point up or down. Tick the box to colour Gauss's three interleaved groups of four. On the right, choose N to compare the work done directly and by the fast transform."),
            dict(type="widget", html=FT_HTML, js=js, css=FT_CSS,
                 fallback=dict(type="diagram", name="split", diagram=split_diagram(d)),
                 note="In the interactive edition you can drag the observations, show Gauss's three groups, and compare the work for any N."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Twelve is three times four", toc="How it works", blocks=[
            dict(type="p", text=f"Twelve observations at 0°, 30°, …, 330° (the program's test data: {', '.join(str(v) for v in t['obs'])}) determine a sum of sines and cosines that passes through all of them. The program's coefficients: {t['coef']}. The curve misses no observation by more than {sci(it['miss'])}, and between them it interpolates: at 15° it gives {it['mid']}."),
            dict(type="p", text=f"**Directly**, each of the twelve coefficients uses all twelve observations: {t['direct']} products. **Gauss's way**: take the observations three at a stride, as three interleaved groups of four (observation n = 3n₁ + n₂). Fit each group of four (3 × 16 = 48 products), turn each result by an angle that depends on its group (the \"twiddle\", 6 products), then combine the three groups with four fits of three (4 × 9 = 36). Total **{t['s43']}**. Splitting the other way, 3 × 4, also gives {t['s34']}, and all three methods give the same coefficients."),
            dict(type="diagram", name="split-steps", diagram=split_diagram(d)),
            dict(type="p", text="For twelve observations the saving is modest. But the split can be repeated: when N is a power of 2, split in halves again and again, and the N² products of the direct method become (N/2)·log₂N."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Divide and conquer: break a big computation into small ones of the same kind, solve those, and combine. The order in which the work is done can matter more than the work itself."),
        ]),
        dict(id="measured", eyebrow="Measured", title="From 64 products to a trillion", toc="Measured", blocks=[
            dict(type="table", head=["N", "Direct (N²)", "Fast ((N/2) log₂ N)", "Times fewer"], num=[1, 2, 3], rows=[list(r) for r in cnt]),
            dict(type="p", text=f"The program checked the fast transform against the direct one, and its inverse against the data, on random sequences of {d['rnd']} lengths from 2 to 2,048. For a million points the direct method needs over a trillion products; the fast one about ten million."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A Latin treatise in a drawer", toc="The evidence", blocks=[
            dict(type="p", text="Heideman, Johnson and Burrus \"infer that GAUSS wrote this treatise in October-November, 1805\" (a well-argued **conjecture** from his notes and dated entries); the *Theoria interpolationis methodo nova tractata* \"appeared only in his collected works\", volume 3, in 1866. \"The example of N = 12 for the orbit of the asteroid Pallas was worked out in Article 28\", both as 4 × 3 and as 3 × 4. The treatise predates Fourier's presentation of December 1807. Gauss's own Pallas observations are not printed in the sources opened for this book, so the page uses test data."),
            dict(type="p", text="The method was found again by Runge (1903), by Danielson and Lanczos (1942) and, in another form, by Good (1958). Cooley and Tukey's paper of 1965 promised \"a number of operations proportional to N log N rather than N²\"; they later wrote that it \"was at first credited with a great discovery\", and that the algorithm \"should be put in the public domain to prevent anyone from patenting it\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Multiplying long numbers by fitting curves", toc="Full circle", blocks=[
            dict(type="p", text="Multiplying two numbers digit by digit is a convolution, and a fast transform turns a convolution into a single multiplication at each point. Transform the digits of both numbers, multiply point by point, transform back, and carry as on Pascal's wheels (topic 3)."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program multiplied two random {ci['digits']}-digit numbers this way: the {ci['pdigits']}-digit product matches Java's BigInteger exactly, using {ci['fft']} complex multiplications against {ci['naive']} digit products by long multiplication. An idea Gauss wrote down for an asteroid in 1805 is how computers multiply very long numbers, and how they process sound and images."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does the direct method need N × N products?", "Each of the N coefficients is a weighted sum of all N observations."),
            ("Which observations go into Gauss's first group of four?", "Every third one: 0, 3, 6 and 9 (then 1, 4, 7, 10 and 2, 5, 8, 11)."),
            ("How many products does a radix-2 FFT need for N = 1,024?", f"(N/2) log₂ N = 512 × 10 = 5,120, against 1,048,576 directly."),
            ("Why must the numbers be carried after the inverse transform?", "Each point of the result is a sum of digit products and can exceed 9; carrying turns it back into digits."),
            ("Why did nobody use Gauss's method for 160 years?", "It sat unpublished until 1866, in Latin, in his collected works; and before computers, nobody had a million observations to transform."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Gauss and the History of the Fast Fourier Transform", text="Heideman, Johnson and Burrus (1985): the article that found Gauss's FFT in his collected works.",
                 draw=C.draw_book, link="https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-3.pdf", link_text="PDF",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "GaussFFT", d["checks"],
                           "Gauss's 4 × 3 and 3 × 4 splits against the direct fit, the fitted curve through all twelve observations, the fast transform and its inverse on random data of eleven lengths, the product counts, and a 2,000-digit multiplication against BigInteger.",
                           ["static double[][] split(", "static void fft("]),
    ]
    return dict(
        title="Gauss's Fast Fourier Transform", date="1805",
        description="Era 3, topic 9 of The Algorithm Evolution Atlas: Gauss's 1805 method for fitting periodic data by splitting it into interleaved groups, 160 years before Cooley and Tukey.",
        lede="To fit sines and cosines to twelve observations of an asteroid, every coefficient needs every observation. Gauss noticed that twelve is three times four, and did the work in pieces. He left it in Latin among his papers, 160 years before the computer age rediscovered it.",
        fieldnote="I have seen many methods found twice. This one waited longest: written in a few weeks of 1805, printed after its author's death, and rediscovered three more times before anyone had the machines that made it indispensable.",
        card=[("When", "Probably October–November 1805; printed 1866; Cooley and Tukey 1965"),
              ("Where", "Göttingen"),
              ("What hurt", "A periodic fit from N observations costs N² products"),
              ("The fix", "Split N = N₁ × N₂ and combine small fits"),
              ("Cost", f"{t['s43']} products instead of {t['direct']} for twelve; N log N in general")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `GaussFFT.java`.",
    )
