"""Era 6, topic 1: the fast Fourier transform. Every number is parsed from FastFourier.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"bitrev: positions 0 to 7 hold samples ([\d ]+) \(.*?\) ; for 16: ([\d ]+)$", ln):
            d["bitrev"] = dict(b8=m.group(1).split(), b16=m.group(2).split())
        elif m := re.match(r"agree: ([\d,]+) random complex samples ; direct sum ([\d,]+) complex multiplications, FFT ([\d,]+) \(([\d,]+) times fewer\) ; largest difference between the two answers ([\d.eE+-]+)", ln):
            d["agree"] = dict(n=m.group(1), direct=m.group(2), fft=m.group(3), times=m.group(4), diff=m.group(5))
        elif ln.startswith("counts: "):
            d["counts"] = re.findall(r"N=([\d,]+): direct ([\d,]+), fast ([\d,]+), ([\d,]+) times fewer", ln)
            m = re.search(r"ran the ([\d,]+)-point FFT and counted ([\d,]+)", ln)
            d["ran"] = dict(n=m.group(1), counted=m.group(2))
        elif m := re.match(r"signal: ([\d,]+) samples ; waves of (\d+) and (\d+) cycles, heights ([\d.]+) and ([\d.]+), buried in random noise of spread ([\d.]+) ; the two tallest peaks of the transform are at (\d+) and (\d+) cycles, (\d+) and (\d+) times", ln):
            d["signal"] = dict(m=m.group(1), f1=m.group(2), f2=m.group(3), h1=m.group(4), h2=m.group(5), noise=m.group(6),
                               p1=m.group(7), p2=m.group(8), r1=m.group(9), r2=m.group(10))
        elif m := re.match(r"multiply: two random ([\d,]+)-digit numbers ; their digits convolved through three FFTs of ([\d,]+) points: ([\d,]+) complex multiplications, against ([\d,]+) digit products by schoolbook ; the ([\d,]+)-digit product, starting (\d+) and ending (\d+), equals Java's BigInteger result ; largest rounding error ([\d.]+)", ln):
            d["mul"] = dict(digits=m.group(1), size=m.group(2), mults=m.group(3), school=m.group(4), plen=m.group(5),
                            start=m.group(6), end=m.group(7), err=m.group(8))
        elif m := re.match(r"inverse: (\d+) random samples .*? largest difference from the original ([\d.eE+-]+)", ln):
            d["inverse"] = dict(n=m.group(1), diff=m.group(2))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def butterfly_svg(d):
    order = [int(x) for x in d["bitrev"]["b8"]]

    def draw(t, standalone):
        o = []
        W, H = 760, 400
        xs = [90, 270, 450, 630]
        ys = [52 + i * 38 for i in range(8)]
        o.append(C.text(20, 26, "Eight samples, three stages of butterflies: 4 + 4 + 4 = 12 multiplications instead of 64", t["ink"], 13, "start", 700))
        for s in range(3):
            half = 1 << s
            for blk in range(0, 8, 2 * half):
                for k in range(half):
                    a, b = blk + k, blk + k + half
                    col = t["red"] if s == 2 and k == 1 else t["axis"]
                    sw = 2.2 if s == 2 and k == 1 else 1.4
                    for (i, j) in [(a, a), (b, b), (a, b), (b, a)]:
                        o.append(C.line(xs[s] + 14, ys[i], xs[s + 1] - 14, ys[j], col, sw))
        for s in range(4):
            for i in range(8):
                o.append(C.circle(xs[s], ys[i], 12, t["surface"], t["ink2"], 1.4))
                lab = f"x{order[i]}" if s == 0 else (f"X{i}" if s == 3 else "")
                if lab:
                    o.append(C.text(xs[s] + (-20 if s == 0 else 20), ys[i] + 4, lab, t["ink"], 12, "end" if s == 0 else "start", 700))
        for s, lab in enumerate(["bit-reversed input", "pairs", "quads", "all eight"]):
            o.append(C.text(xs[s], 356, lab, t["muted"], 11, "middle"))
        o.append(C.text(20, 388, "Each crossing (a butterfly) costs one multiplication by a power of w: out = E + w·O and E − w·O. Red: one butterfly of the last stage.", t["muted"], 11))
        return C.svg_doc(W, H, "".join(o), "The FFT's butterflies for eight samples", t, standalone, 0.55, 760)
    return draw


FF_HTML = """
<div class="board ff-board">
  <div style="min-width:0">
    <div class="ff-plot" id="ff-time"></div>
    <div class="ff-plot" id="ff-freq"></div>
  </div>
  <div style="min-width:0">
    <label class="ff-row">Wave 1, cycles <input type="range" id="ff-f1" min="1" max="127" value="17"><output id="ff-f1o"></output></label>
    <label class="ff-row">Wave 2, cycles <input type="range" id="ff-f2" min="1" max="127" value="70"><output id="ff-f2o"></output></label>
    <label class="ff-row">Noise <input type="range" id="ff-noise" min="0" max="40" value="10"><output id="ff-no"></output></label>
    <div class="ff-stats" id="ff-stats"></div>
    <p class="say" id="ff-say" aria-live="polite"></p>
  </div>
</div>
"""

FF_CSS = """
.ff-plot svg{display:block;width:100%;height:auto;margin-bottom:8px}
.ff-row{display:grid;grid-template-columns:1fr;gap:2px;font-size:14px;margin:6px 0}
.ff-row input{width:100%}
.ff-row output{font:13px var(--mono);color:var(--muted)}
.ff-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

FF_JS = r"""
(() => {
  const tBox = document.getElementById("ff-time");
  if (!tBox) return;
  const N = 256;
  let mults = 0;
  function fft(re, im) {
    const n = re.length, bits = Math.log2(n);
    for (let i = 0; i < n; i++) {
      let j = 0; for (let b = 0, x = i; b < bits; b++) { j = (j << 1) | (x & 1); x >>= 1; }
      if (j > i) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; }
    }
    for (let len = 2; len <= n; len <<= 1) {
      const ang = -2 * Math.PI / len;
      for (let s = 0; s < n; s += len) for (let k = 0; k < len / 2; k++) {
        const wr = Math.cos(ang * k), wi = Math.sin(ang * k), a = s + k, b = a + len / 2;
        const tr = re[b] * wr - im[b] * wi, ti = re[b] * wi + im[b] * wr; mults++;
        re[b] = re[a] - tr; im[b] = im[a] - ti; re[a] += tr; im[a] += ti;
      }
    }
  }
  let seed = 1965;
  const u = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return (seed + 0.5) / 2147483648; };
  const gauss = () => Math.sqrt(-2 * Math.log(u())) * Math.cos(2 * Math.PI * u());
  function plot(box, ys, w, h, bars, mark) {
    box.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", `0 0 ${w} ${h}`); box.appendChild(svg);
    const mx = Math.max(...ys.map(Math.abs)) || 1;
    if (bars) {
      ys.forEach((y, i) => { const x = 10 + i * (w - 20) / ys.length, hh = (h - 30) * y / mx;
        sv("rect", {x, y: h - 20 - hh, width: Math.max(1, (w - 20) / ys.length - 0.5), height: hh, fill: mark.includes(i) ? "var(--red)" : "var(--blue)"}, svg); });
      sv("line", {x1: 10, y1: h - 20, x2: w - 10, y2: h - 20, stroke: "var(--ink)", "stroke-width": 1}, svg);
    } else {
      const pts = ys.map((y, i) => `${(10 + i * (w - 20) / (ys.length - 1)).toFixed(1)},${(h / 2 - (h / 2 - 10) * y / mx).toFixed(1)}`).join(" ");
      sv("polyline", {points: pts, fill: "none", stroke: "var(--ink-2)", "stroke-width": 1}, svg);
    }
    const lab = sv("text", {x: 10, y: 14, "font-size": 12, fill: "var(--muted)"}, svg);
    lab.textContent = bars ? "the transform: height of each frequency, 1 to 127 cycles" : `the signal: ${N} samples`;
  }
  function update() {
    const f1 = +document.getElementById("ff-f1").value, f2 = +document.getElementById("ff-f2").value, nz = +document.getElementById("ff-noise").value / 10;
    document.getElementById("ff-f1o").textContent = `${f1} cycles, height 1.0`;
    document.getElementById("ff-f2o").textContent = `${f2} cycles, height 0.6`;
    document.getElementById("ff-no").textContent = `random noise of spread ${nz.toFixed(1)}`;
    seed = 1965;
    const re = Array.from({length: N}, (_, i) => Math.sin(2 * Math.PI * f1 * i / N) + 0.6 * Math.sin(2 * Math.PI * f2 * i / N) + nz * gauss());
    const im = new Array(N).fill(0);
    plot(tBox, re, 520, 120, false, []);
    mults = 0; fft(re, im);
    const pw = []; for (let k = 1; k < N / 2; k++) pw.push(Math.hypot(re[k], im[k]));
    const top = pw.map((v, i) => [v, i]).sort((a, b) => b[0] - a[0]).slice(0, 2).map(x => x[1]);
    plot(document.getElementById("ff-freq"), pw, 520, 140, true, top);
    const found = top.map(i => i + 1).sort((a, b) => a - b);
    const want = [f1, f2].sort((a, b) => a - b);
    const st = document.getElementById("ff-stats"); st.innerHTML = "";
    el("div", {}, st, `direct sum: ${fmt(N * N)} multiplications`);
    el("div", {}, st, `this FFT: ${fmt(mults)} multiplications`);
    el("div", {}, st, `two tallest peaks: ${found.join(" and ")} cycles`);
    const say = document.getElementById("ff-say");
    if (f1 === f2) say.textContent = top[0] + 1 === f1 ? "Both waves have the same frequency, so they add up to one peak: the tallest bar." : "Even the combined wave is lost in this much noise.";
    else say.textContent = found[0] === want[0] && found[1] === want[1] ? "The two tallest peaks (red) are exactly the two waves, though the signal itself looks like noise." :
      "The noise is now strong enough to hide a wave: one of the tallest peaks is noise. The program's longer record (__M__ samples) finds both waves in noise of spread __NOISE__; more samples, more help.";
  }
  ["ff-f1", "ff-f2", "ff-noise"].forEach(id => document.getElementById(id).addEventListener("input", update));
  update();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the fast Fourier transform combined older ideas, and where it led")
    W = 210
    nodes = {
        "gauss": (20, 20, "Gauss's method", "split, transform the halves, combine", "about 1805 (Era 3)", "ink"),
        "dft": (395, 20, "Fourier series", "a signal as a sum of waves", "N² multiplications", "ink"),
        "good": (770, 20, "Earlier versions", "Runge, Danielson and Lanczos, Good", "1903–1958", "ink"),
        "fft": (395, 180, "The FFT", "⊕ halving, again and again, programmed for a computer", "Cooley and Tukey, 1965", "red"),
        "seis": (20, 340, "Seismograms", "telling earthquakes from bomb tests", "1963 committee", "ink"),
        "mul": (395, 340, "Fast multiplication", "a product of numbers is a convolution of digits", "", "ink"),
        "sig": (770, 340, "Signal processing", "filters, spectra, in real time", "", "ink"),
        "today": (395, 490, "Today", "sound and video compression, scanners that see inside a body", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("gauss", "fft", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("dft", "fft", ports=("bottom", "top"))
    D.edge("good", "fft", ports=("bottom", "top:0.85"))
    D.edge("seis", "fft", ports=("top", "left"), label="the need", at=0.5, dx=8, anchor="start")
    D.edge("fft", "mul", ports=("bottom", "top"))
    D.edge("fft", "sig", ports=("right", "top"))
    D.edge("mul", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: Gauss's notes were not known to Cooley and Tukey; the method was found again. The IEEE Milestone lists uses from tomography to compression.", "caption")
    return D


def chain(d):
    a, s, m = d["agree"], d["signal"], d["mul"]
    steps = [
        (f"A transform of {a['n']} samples: {a['direct']} multiplications",
         f"The FFT: {a['fft']}, the same answer to within {C.sci(a['diff'])}", "Cooley and Tukey, 1965"),
        (f"Waves of height {s['h1']} and {s['h2']} hidden in noise of spread {s['noise']}",
         f"Transform the record: peaks {s['r1']} and {s['r2']} times the average, at the right frequencies", "what the 1963 committee wanted"),
        (f"Multiplying two {m['digits']}-digit numbers: {m['school']} digit products",
         f"Convolve the digits through FFTs: {m['mults']} multiplications", "the same trick, for arithmetic"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a slow sum to fast arithmetic")
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
    br, a, cn, ran, s, m, inv = d["bitrev"], d["agree"], d["counts"], d["ran"], d["signal"], d["mul"], d["inverse"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The Fourier transform breaks a signal into waves, at a cost of N² multiplications for N samples. Splitting the samples into halves and combining the halves' transforms had been found before, by Gauss among others; in 1965 it was found again, written down for computers, and applied at every level. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the FFT. Blue: where it is used today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Find two waves in the noise", toc="Try it", blocks=[
            dict(type="p", text="A signal of 256 samples: two waves (choose their frequencies) and random noise (choose how much). The upper picture is what a seismometer or a microphone records; the lower one is its transform, computed by the FFT in your browser. The two tallest bars (red) are where the transform finds waves."),
            dict(type="widget", html=FF_HTML, js=FF_JS.replace("__M__", s["m"]).replace("__NOISE__", s["noise"]), css=FF_CSS,
                 fallback=dict(type="table", head=["Samples N", "Direct sum (N²)", "FFT ((N/2) log₂ N)", "Times fewer"], num=[0, 1, 2, 3],
                               rows=[list(x) for x in cn]),
                 note="In the interactive edition you can hide two waves in noise and watch the FFT find them."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Split, transform the halves, combine", toc="How it works", blocks=[
            dict(type="p", text="**The sum.** The transform of N samples x₀ … x_{N−1} is N numbers X_k = Σ xₙ wⁿᵏ, where w = e^(−2πi/N) is a turn of one N-th of a circle. Each X_k needs N multiplications, so all of them need N²."),
            dict(type="p", text="**The split.** If N is even, the sum falls into the even-numbered samples and the odd-numbered ones: X_k = E_k + wᵏ O_k and X_{k+N/2} = E_k − wᵏ O_k, where E and O are transforms of half the length. One multiplication (by wᵏ) gives two outputs: that pair is a *butterfly*. Repeating the split down to single samples gives log₂ N stages of N/2 butterflies."),
            dict(type="svg", name="butterfly", draw=butterfly_svg(d), alt="The FFT's butterflies for eight samples", width=760,
                 caption=f"Done in place, the samples must first be put in bit-reversed order: position 6 (110 in binary) holds sample 3 (011). The program's order for eight samples: {' '.join(br['b8'])}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A problem of size N becomes two problems of size N/2 plus N/2 cheap steps. Done once, that halves the work; done at every level, it turns N² into (N/2) log₂ N."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Counting the multiplications", toc="Measured", blocks=[
            dict(type="p", text=f"The program transformed {a['n']} random complex samples both ways: the direct sum took {a['direct']} complex multiplications, the FFT {a['fft']} ({a['times']} times fewer), and the two answers differ by at most {C.sci(a['diff'])}, the size of rounding error. It also ran a {ran['n']}-point FFT and counted {ran['counted']} multiplications, exactly (N/2) log₂ N."),
            dict(type="table", head=["Samples N", "Direct sum (N²)", "FFT ((N/2) log₂ N)", "Times fewer"], num=[0, 1, 2, 3], rows=[list(x) for x in cn], hl=len(cn) - 1),
            dict(type="p", text=f"**A seismogram.** {s['m']} samples holding waves of {s['f1']} and {s['f2']} cycles, of heights {s['h1']} and {s['h2']}, buried in random noise of spread {s['noise']}. The two tallest peaks of the transform are at {s['p1']} and {s['p2']} cycles, {s['r1']} and {s['r2']} times the average height of the others."),
            dict(type="p", text=f"**Long multiplication.** Multiplying numbers is a convolution of their digits, and the transform turns convolution into simple products. Two random {m['digits']}-digit numbers, multiplied through three FFTs of {m['size']} points: {m['mults']} complex multiplications, against {m['school']} digit products by the schoolbook method. The {m['plen']}-digit product (starting {m['start']}…, ending …{m['end']}) equals Java's own BigInteger result; the largest rounding error before rounding to whole numbers was {m['err']}."),
            dict(type="p", text=f"**And back.** Transforming {inv['n']} random samples and transforming the result back (with the opposite sign of the turn, and a division by {inv['n']}) returned the samples to within {C.sci(inv['diff'])}."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A committee, a physicist and a programmer", toc="The evidence", blocks=[
            dict(type="p", text="Cooley and Tukey's paper, \"An Algorithm for the Machine Calculation of Complex Fourier Series\", was received on 17 August 1964 and printed in *Mathematics of Computation* 19: 297–301 (1965). Its abstract promises \"a number of operations proportional to N log N rather than N²\", and it ends: \"The authors wish to thank Richard Garwin for his essential role in communication and encouragement.\""),
            dict(type="p", text="The IEEE Milestone dedicated in 2025 tells the rest: at a 1963 meeting of President Kennedy's Science Advisory Committee on detecting underground nuclear tests, Garwin heard that Tukey had \"a scheme to do a complete discrete Fourier transform with a vastly reduced number of mathematical calculations\", and asked IBM for a mathematician to program it; that was Cooley. The 1964 demonstration on an IBM 7094 was, for large problems of the time, about 100 times faster than existing codes. IEEE Spectrum reports that sensors using the algorithm could detect nuclear explosions within 15 kilometres; that figure is not in the paper."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Found again after 160 years", toc="Full circle", blocks=[
            dict(type="p", text="Gauss used the same splitting about 1805, to fit the orbits of asteroids, and left it in Latin among his papers (Era 3, topic 9); Runge (1903), Danielson and Lanczos (1942) and Good (1958) had versions too. What changed in 1965 was not the idea but the machine: a computer could apply the split at every level, to transforms of thousands and then millions of samples."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Era 3's page showed Gauss's splitting by hand. Here the same splitting, applied twenty times, transforms {ran['n']} samples with {ran['counted']} multiplications."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many butterflies does a 16-point FFT need, and in how many stages?", "4 stages of 8 butterflies: 32 multiplications, against 256 for the direct sum."),
            ("In an 8-point FFT done in place, which sample sits in position 1?", "Position 1 is 001 in binary; reversed, 100 = 4. Sample 4."),
            ("Why must N be a power of two in this version?", "Each stage halves the samples; if a half had odd length the split into even and odd would not divide evenly. (Other versions split into threes, fives, and so on.)"),
            ("Why does multiplying long numbers become cheap?", "The digits of a product are a convolution of the digits of the factors, and the transform turns a convolution into one product per frequency."),
            ("A transform shows a tall peak at 50 cycles in a 1-second record. What does it mean?", "The record contains a wave that repeats 50 times a second, such as the hum of mains electricity in many countries."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="An Algorithm for the Machine Calculation of Complex Fourier Series (1965)", text="Cooley and Tukey's five-page paper, *Mathematics of Computation* 19: 297–301.",
                 draw=C.draw_manuscript, link="https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf", link_text="The paper (PDF, on a UC Davis course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "FastFourier", d["checks"],
                           "bit reversal, the FFT against the direct sum on every one of 1,024 frequencies, the multiplication count for N up to 1,048,576, two waves found in noise, a 4,000-digit multiplication against Java's BigInteger, and the inverse transform.",
                           ["static void fft(double[] re, double[] im, int sign)"]),
    ]
    return dict(
        title="The Fast Fourier Transform", date="1964–1965",
        description="Era 6, topic 1 of The Algorithm Evolution Atlas: Cooley and Tukey's FFT, from nuclear-test detection to fast multiplication, with every count measured.",
        lede="Breaking a signal into its waves took N² multiplications, too slow for the seismograms of the 1960s. Halve the samples, transform each half, combine, and repeat: the work falls to (N/2) log₂ N.",
        fieldnote=f"A transform of {ran['n']} samples needs {cn[-1][1]} multiplications done directly; the program did it with {ran['counted']}. The trick was Gauss's, found again because a committee needed to hear bombs in the shaking of the ground.",
        card=[("When", "Demonstrated 1964; published 1965"),
              ("Where", "Princeton and IBM Research"),
              ("What hurt", "N² multiplications for N samples"),
              ("The fix", "Split into even and odd samples, recursively"),
              ("Cost", f"(N/2) log₂ N: {a['fft']} instead of {a['direct']} for {a['n']} samples")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `FastFourier.java`.",
    )
