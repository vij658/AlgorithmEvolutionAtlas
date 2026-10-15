"""Era 7, topic 11: Shor's factoring algorithm. Every number is parsed from ShorFactoring.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"reduction: for (\d+) products .*? from 15 to ([\d,]+), [^;]* ; (.*?) ; the smallest share over all \d+ was (\d+)%", ln):
            rows = []
            for part in m.group(3).split(" ; "):
                mm = re.match(r"N=([\d,]+): ([\d,]+) of ([\d,]+) choices of a work \((\d+)%\)", part)
                rows.append(dict(n=mm.group(1), good=mm.group(2), tried=mm.group(3), pct=mm.group(4)))
            d["red"] = dict(count=m.group(1), maxn=m.group(2), rows=rows, worst=m.group(4))
        elif m := re.match(r"peaks: [^;]* ; N=15, a=7, period (\d+), Q=(\d+): probability ([\d.]+) at each of y = ([\d, ]+), and ([\d.]+) everywhere else ; N=21, a=2, period (\d+), Q=(\d+): Q/r = ([\d.]+) .*?\(([\d, ]+)\) carry ([\d.]+) of the probability", ln):
            d["peaks"] = dict(r15=m.group(1), q15=m.group(2), p15=m.group(3), ys15=m.group(4), rest15=m.group(5), r21=m.group(6), q21=m.group(7), qr21=m.group(8), ys21=m.group(9), near21=m.group(10))
        elif m := re.match(r"shor: [^;]* ; (.*?) ; (\d+) simulated measurements in all", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"N=([\d,]+) = (\d+) x (\d+): Q=2\^(\d+), (\d+) choices? of a, (\d+) measurements?", part)
                rows.append(dict(n=mm.group(1), p=mm.group(2), q=mm.group(3), bits=mm.group(4), choices=mm.group(5), meas=mm.group(6)))
            d["shor"] = dict(rows=rows, total=m.group(2))
        elif m := re.match(r"cost: [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"a ([\d,]+)-bit N: ([\d,]+) qubits in the first register, 2\^([\d,]+) amplitudes to store", part)
                rows.append(dict(bits=mm.group(1), qubits=mm.group(2), amps=mm.group(3)))
            d["cost"] = rows
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def flow_svg(d):
    """The algorithm as a pipeline: classical, quantum, classical."""
    def draw(t, standalone):
        o = []
        W, H = 780, 250
        o.append(C.text(20, 26, "Factoring N: only the middle step needs a quantum computer", t["ink"], 13, "start", 700))
        boxes = [("Pick a at random", "if gcd(a, N) > 1, done", t["ink"]),
                 ("Find the period r", "a^r ≡ 1 (mod N), by a quantum Fourier transform", t["red"]),
                 ("If r is even, compute", "gcd(a^(r/2) − 1, N)", t["ink"]),
                 ("A factor of N", "for at least half of all a", t["blue"])]
        bw, gap, y = 160, 30, 70
        for i, (a, b, col) in enumerate(boxes):
            x = 20 + i * (bw + gap)
            o.append(C.rect(x, y, bw, 96, t["surface"], col, 2.2 if col != t["ink"] else 1.5, 3))
            o.append(C.text(x + 10, y + 26, a, col, 13, "start", 700))
            words, line, yy = b.split(), "", y + 48
            for w in words:
                if len(line + " " + w) > 22:
                    o.append(C.text(x + 10, yy, line.strip(), t["ink"], 12)); yy += 16; line = ""
                line += " " + w
            o.append(C.text(x + 10, yy, line.strip(), t["ink"], 12))
            if i < 3:
                ax = x + bw
                o.append(C.line(ax + 3, y + 48, ax + gap - 5, y + 48, t["ink"], 1.6))
                o.append(C.path(f"M{ax + gap - 3},{y + 48} L{ax + gap - 12},{y + 43} L{ax + gap - 12},{y + 53} Z", None, t["ink"]))
        o.append(C.text(20 + 1 * (bw + gap) + bw / 2, y + 120, "quantum", t["red"], 12, "middle", 700))
        o.append(C.text(20 + bw / 2, y + 120, "classical", t["muted"], 12, "middle"))
        o.append(C.text(20 + 2 * (bw + gap) + bw / 2, y + 120, "classical (Euclid, Era 1)", t["muted"], 12, "middle"))
        o.append(C.text(20, H - 10, "If r is odd, or a^(r/2) ≡ −1 (mod N), pick another a and try again.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Shor's algorithm as a pipeline", t, standalone, 0.55, 780)
    return draw


SH_HTML = """
<div class="board sh-board">
  <div style="min-width:0">
    <div class="sh-view" id="sh-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls">
      <label>N <select id="sh-n"><option>15</option><option>21</option><option>35</option><option>77</option><option>143</option><option>221</option></select></label>
      <label>a <select id="sh-a"></select></label>
    </div>
    <div class="sh-btns"><button type="button" class="primary" id="sh-measure">Measure</button></div>
    <div class="sh-stats" id="sh-stats"></div>
    <p class="say" id="sh-say" aria-live="polite"></p>
  </div>
</div>
"""

SH_CSS = """
.sh-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.sh-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.sh-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
.sh-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:3px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
"""

SH_JS = r"""
(() => {
  const view = document.getElementById("sh-view");
  if (!view) return;
  const PROG = __PROG__;
  const gcd = (a, b) => { while (b) [a, b] = [b, a % b]; return a; };
  const powmod = (a, e, n) => { let r = 1 % n; a %= n; while (e > 0) { if (e & 1) r = r * a % n; a = a * a % n; e >>= 1; } return r; };
  const order = (a, n) => { let x = a % n, r = 1; while (x !== 1) { x = x * a % n; r++; } return r; };
  function fft(re, im) {
    const n = re.length;
    for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [re[i], re[j]] = [re[j], re[i]]; [im[i], im[j]] = [im[j], im[i]]; } }
    for (let len = 2; len <= n; len <<= 1) {
      const ang = 2 * Math.PI / len;
      for (let i = 0; i < n; i += len) for (let k = 0; k < len / 2; k++) {
        const wr = Math.cos(ang * k), wi = Math.sin(ang * k), u = i + k, v = i + k + len / 2;
        const xr = re[v] * wr - im[v] * wi, xi = re[v] * wi + im[v] * wr;
        re[v] = re[u] - xr; im[v] = im[u] - xi; re[u] += xr; im[u] += xi;
      }
    }
  }
  let N, a, Q, prob, r;
  const nSel = document.getElementById("sh-n"), aSel = document.getElementById("sh-a");
  function setN() {
    N = +nSel.value; aSel.innerHTML = "";
    for (let x = 2; x < N; x++) if (gcd(x, N) === 1) { const o = document.createElement("option"); o.textContent = x; aSel.appendChild(o); }
    aSel.value = N === 15 ? "7" : "2"; setA();
  }
  function setA() {
    a = +aSel.value; let bits = 1; while ((1 << bits) < N * N) bits++; Q = 1 << bits;
    // the state after the second register is measured and gave a^0 mod N = 1: x = 0, r, 2r, ... below Q
    r = order(a, N);
    const re = new Float64Array(Q), im = new Float64Array(Q);
    let cnt = 0; for (let x = 0; x < Q; x += r) { re[x] = 1; cnt++; }
    for (let x = 0; x < Q; x += r) re[x] /= Math.sqrt(cnt);
    fft(re, im);
    prob = new Float64Array(Q); for (let y = 0; y < Q; y++) prob[y] = (re[y] * re[y] + im[y] * im[y]) / Q;
    draw(`N = ${N}, a = ${a}: the powers of a repeat every ${r}. Each bar is the chance that measuring the first register gives that y; the peaks sit near multiples of Q/r = ${(Q / r).toFixed(2)}.`);
  }
  function draw(msg, picked) {
    view.innerHTML = "";
    const W = 420, H = 300, svg = sv("svg", {viewBox: `0 0 ${W} ${H}`}, view), bins = Math.min(Q, 256), per = Q / bins;
    const bp = new Float64Array(bins); for (let y = 0; y < Q; y++) bp[Math.floor(y / per)] += prob[y];
    const mx = Math.max(...bp), x0 = 30, w = W - 45, base = 200;
    sv("line", {x1: x0, y1: base, x2: x0 + w, y2: base, stroke: "var(--axis)"}, svg);
    bp.forEach((p, i) => { if (p > 1e-9) sv("rect", {x: x0 + i * w / bins, y: base - p / mx * 160, width: Math.max(w / bins - 0.3, 0.6), height: p / mx * 160, fill: "var(--blue)"}, svg); });
    if (picked !== undefined) { const px = x0 + (picked / per) * w / bins; sv("line", {x1: px, y1: 30, x2: px, y2: base, stroke: "var(--red)", "stroke-width": 2}, svg); }
    const t1 = sv("text", {x: x0, y: base + 18, "font-size": 11.5, fill: "var(--muted)"}, svg); t1.textContent = "0";
    const t2 = sv("text", {x: x0 + w, y: base + 18, "font-size": 11.5, fill: "var(--muted)", "text-anchor": "end"}, svg); t2.textContent = `Q − 1 = ${Q - 1}`;
    const t3 = sv("text", {x: x0, y: 22, "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg); t3.textContent = `chance of each measured y (Q = ${Q}${bins < Q ? ", grouped in " + bins + " bars" : ""})`;
    // the sequence of powers
    const seq = []; for (let x = 0; x < Math.min(13, 3 * r + 3); x++) seq.push(powmod(a, x, N));
    const t4 = sv("text", {x: x0, y: base + 44, "font-size": 11.5, fill: "var(--ink)", "font-family": "var(--mono)"}, svg); t4.textContent = `a^x mod N: ${seq.join(" ")}${seq.length < 3 * r + 3 ? " …" : ""}`;
    const t5 = sv("text", {x: x0, y: base + 62, "font-size": 11.5, fill: "var(--muted)"}, svg); t5.textContent = `the period r = ${r} (found here by brute force, to check)`;
    const st = document.getElementById("sh-stats"); st.innerHTML = "";
    let onPeaks = 0; for (let k = 0; k < r; k++) onPeaks += prob[Math.round(k * Q / r) % Q];
    el("div", {}, st, `qubits in the first register: ${Math.log2(Q)}; amplitudes stored: ${Q.toLocaleString("en-US")}`);
    el("div", {}, st, `probability on the integers nearest k·Q/r: ${onPeaks.toFixed(3)}`);
    const p = PROG[`${N},${a}`]; if (p) el("div", {}, st, `the program, same N and a: ${p}`);
    if (msg) document.getElementById("sh-say").textContent = msg;
  }
  function convergents(y) {
    const out = []; let h0 = 0, h1 = 1, k0 = 1, k1 = 0, num = y, den = Q;
    while (den !== 0) { const q = Math.floor(num / den), h2 = q * h1 + h0, k2 = q * k1 + k0; if (k2 >= N) break; out.push([h2, k2]); h0 = h1; h1 = h2; k0 = k1; k1 = k2; const t = num - q * den; num = den; den = t; }
    return out;
  }
  document.getElementById("sh-measure").addEventListener("click", () => {
    let u = Math.random(), y = 0; for (let c = 0; y < Q; y++) { c += prob[y]; if (u < c) break; }
    y = Math.min(y, Q - 1);
    const conv = convergents(y);
    let found = 0; for (const [h, k] of conv) { for (let m = 1; m <= 4 && k * m < N; m++) if (k > 0 && powmod(a, k * m, N) === 1) { found = k * m; break; } if (found) break; }
    let msg = `Measured y = ${y}. y/Q = ${y}/${Q}; continued fractions give denominators ${conv.map(c => c[1]).join(", ") || "none"}. `;
    if (!found) msg += "None of them is a period: measure again.";
    else if (found % 2) msg += `Period ${found} is odd: pick another a.`;
    else { const h = powmod(a, found / 2, N); if (h === N - 1) msg += `Period ${found}, but a^(r/2) ≡ −1 (mod N): pick another a.`; else { const f = gcd(h - 1, N); msg += `Period ${found}: gcd(${h} − 1, ${N}) = ${f}, so ${N} = ${f} × ${N / f}.`; } }
    draw(msg, y);
  });
  nSel.addEventListener("change", setN); aSel.addEventListener("change", setA);
  setN();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Shor's algorithm combined older ideas, and where it led")
    W = 210
    nodes = {
        "fft": (20, 20, "The FFT", "finds the frequencies in a signal", "Era 6, topic 1", "ink"),
        "rsa": (395, 20, "RSA", "security from hard number theory", "Era 6, topic 10", "ink"),
        "qc": (770, 20, "Quantum computers", "registers in superposition, amplitudes that interfere", "hypothetical in 1994", "ink"),
        "sh": (395, 180, "Shor's algorithm", "⊕ find the period by quantum interference", "Bell Labs, 1994", "red"),
        "ibm": (20, 340, "15 = 3 × 5", "a 7-qubit NMR experiment", "IBM, 2001", "ink"),
        "pq": (770, 340, "Hash-based signatures", "believed safe against quantum computers", "this era, topic 2", "ink"),
        "today": (395, 490, "Today", "RSA-2048 with under a million noisy qubits (an estimate)", "Gidney, 2025", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("fft", "sh", ports=("bottom", "top:0.15"))
    D.edge("rsa", "sh", ports=("bottom", "top"), label="the target", at=0.5, dx=8, anchor="start")
    D.edge("qc", "sh", ports=("bottom", "top:0.85"))
    D.edge("sh", "ibm", ports=("bottom:0.15", "top"))
    D.edge("sh", "pq", ports=("bottom:0.85", "top"), dashed=True, label="a reason to prefer", at=0.5, dx=8, anchor="start")
    D.edge("sh", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: an estimate of what a machine would need, not a demonstration. Dashed: a consequence, not a descendant.", "caption")
    return D


def chain(d):
    rd, pk, cost = d["red"], d["peaks"], d["cost"]
    big = cost[-1]
    steps = [
        ("RSA's security rests on factoring, and every known classical method takes superpolynomial time",
         f"Factoring reduces to finding a period: for every N tried, at least {rd['worst']}% of the choices of a split N", "the classical half of Shor's algorithm"),
        ("Finding the period is itself hard for an ordinary computer",
         f"A quantum Fourier transform piles the probability onto multiples of Q/r: {pk['p15']} on each of {pk['r15']} peaks for N = 15", "Shor, 1994"),
        (f"Simulating it classically needs 2^{big['amps']} amplitudes for a {big['bits']}-bit N",
         "Build the quantum computer: 15 was factored in 2001; a 2025 estimate puts RSA-2048 under a million noisy qubits", "the step that remains"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from factoring to periods to a machine not yet built")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx = (L, R) if i % 2 == 0 else (R, L)
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx, y, bw, rowh, [("THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="answered by", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    rd, pk, sh, cost = d["red"], d["peaks"], d["shor"], d["cost"]
    red_rows = [[r["n"], r["good"], r["tried"], r["pct"] + "%"] for r in rd["rows"]]
    sh_rows = [[r["n"], f"{r['p']} × {r['q']}", f"2^{r['bits']}", r["choices"], r["meas"]] for r in sh["rows"]]
    cost_rows = [[r["bits"], r["qubits"], f"2^{r['amps']}"] for r in cost]
    prog = {"15,7": f"{pk['p15']} on each of y = {pk['ys15']}", "21,2": f"{pk['near21']} on the integers nearest k·Q/r"}
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The fast Fourier transform (Era 6) finds the frequencies hidden in a signal. RSA (Era 6) bet that factoring is hard. Quantum computers, in 1994 still hypothetical machines, hold many values at once as amplitudes that can interfere. Shor saw that factoring reduces to finding a frequency, the period of a repeating sequence, and that a quantum computer could find it by interference. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Shor's algorithm. Blue: where things stand."),
        ]),
        dict(id="play", eyebrow="Try it", title="Find the period, then the factors", toc="Try it", blocks=[
            dict(type="p", text="The quantum step, simulated in your browser the way the program does it: store every one of the Q amplitudes, keep the x whose a^x mod N equals 1 (the second register's measurement), and apply a Fourier transform. The bars show the chance of each measurement y; they pile up near multiples of Q/r. Press Measure: the widget picks a y with those chances, runs continued fractions on y/Q to guess the period, and finishes with Euclid's gcd. For N = 15 with a = 7 and N = 21 with a = 2, the probabilities match the program's."),
            dict(type="widget", html=SH_HTML, js=SH_JS.replace("__PROG__", json.dumps(prog)), css=SH_CSS,
                 fallback=dict(type="table", head=["N", "Factors", "Q", "Choices of a", "Measurements"], num=[0, 3, 4], rows=sh_rows),
                 note="In the interactive edition you can measure the simulated register and watch the factors appear."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Factoring is finding a period", toc="How it works", blocks=[
            dict(type="svg", name="flow", draw=flow_svg(d), alt="Shor's algorithm as a pipeline", width=780),
            dict(type="p", text="**Why a period helps.** If a^r ≡ 1 (mod N) and r is even, then (a^(r/2) − 1)(a^(r/2) + 1) is a multiple of N. Unless a^(r/2) ≡ −1, neither factor is a multiple of N by itself, so each shares a proper factor with N, and Euclid's algorithm finds it."),
            dict(type="p", text="**The quantum step.** A register of about 2 log₂ N qubits holds every x from 0 to Q − 1 at once; a second register gets a^x mod N. Measuring the second register leaves the first holding only the x with that value: x₀, x₀ + r, x₀ + 2r, … The quantum Fourier transform makes those amplitudes interfere so that measuring gives a y close to a multiple of Q/r. Continued fractions turn y/Q into a fraction with denominator r (or a divisor of it)."),
            dict(type="p", text="**Why simulation does not help.** An ordinary computer must store one complex number for every value the register can hold: Q of them, about N². The program does exactly that, which is why it stops at N = 1,007."),
            dict(type="callout", kind="key", label="Key idea",
                 text="The hard part of factoring hides a regularity: a period. A Fourier transform is the tool for finding periods, and a quantum computer can apply it to an exponentially large register in polynomial time."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The reduction, the peaks and the cost", toc="Measured", blocks=[
            dict(type="p", text=f"**The reduction.** For {rd['count']} products of two distinct odd primes from 15 to {rd['maxn']}, every a with no factor in common with N, its period found by brute force: the share of a's that split N was never below {rd['worst']}%."),
            dict(type="table", head=["N", "a that work", "a tried", "Share"], num=[0, 1, 2, 3], rows=red_rows),
            dict(type="p", text=f"**The peaks.** N = 15, a = 7: the period is {pk['r15']} and Q = {pk['q15']} is a multiple of it, so all the probability sits exactly on y = {pk['ys15']} ({pk['p15']} each, {pk['rest15']} elsewhere). N = 21, a = 2: the period is {pk['r21']}, Q/r = {pk['qr21']} is not a whole number, and the integers nearest the multiples ({pk['ys21']}) carry {pk['near21']} of the probability together."),
            dict(type="p", text=f"**The whole algorithm,** simulated with every amplitude stored, a chosen at random with no factor in common with N: {sh['total']} simulated measurements in all."),
            dict(type="table", head=["N", "Factors", "Q", "Choices of a", "Measurements"], num=[0, 3, 4], rows=sh_rows),
            dict(type="p", text="**The cost of simulating:**"),
            dict(type="table", head=["Bits in N", "Qubits in the first register", "Amplitudes a simulation stores"], num=[0, 1], rows=cost_rows, hl=[len(cost_rows) - 1]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="On a hypothetical computer", toc="The evidence", blocks=[
            dict(type="p", text="Peter Shor, at Bell Labs in Murray Hill, announced the result in 1994 (\"Algorithms for Quantum Computation: Discrete Log and Factoring\", DIMACS technical report 94-37: these computers \"can factor integers and find discrete logarithms in polynomial time\"). The full version, \"Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer\" (arXiv quant-ph/9508027, 1995; *SIAM Journal on Computing*), gives \"Efficient randomized algorithms ... for these two problems on a hypothetical quantum computer\"."),
            dict(type="p", text="Wikipedia describes the algorithm as \"A classical reduction of the factoring problem to the problem of order-finding\" plus a quantum step, with continued fractions to \"extract the period from the measurement outcomes\"; it records a 2001 IBM experiment using \"an NMR implementation of a quantum computer with seven qubits\" (which factored 15, per the History of Information page, with doubts since \"no entanglement was observed\"), and says that of later small demonstrations \"none of these demonstrations fulfill the requirements of Shor's algorithm\". Smolin, Smith and Vargo of IBM showed that \"compiled\" versions can factor any product of two primes with two qubits, so \"the correct measure of difficulty ... is not the size of number factored\"."),
            dict(type="p", text="Craig Gidney's 2025 estimate: \"a 2048 bit RSA integer could be factored in less than a week using less than one million noisy qubits\", \"compared to 20 million in Gidney+Ekerå 2019\". That is an estimate of what a machine would need, not a report of one."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Euclid and Fourier, with qubits", toc="Full circle", blocks=[
            dict(type="p", text="Shor's algorithm ends with the oldest algorithm in this book, Euclid's greatest common divisor (Era 1), and turns on the fast Fourier transform (Era 6). The only new ingredient is the machine that runs the transform."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Era 6 built public-key cryptography on the hardness of factoring. Era 7 shows that the hardness belongs to the kind of computer, not to the problem: a {cost[-1]['bits']}-bit number needs {cost[-1]['qubits']} qubits in the first register, or 2^{cost[-1]['amps']} stored numbers to simulate them."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("The powers of 7 modulo 15 are 1, 7, 4, 13, 1, … What is r, and what factors does it give?", "r = 4; 7² = 49 ≡ 4, and gcd(4 − 1, 15) = 3, gcd(4 + 1, 15) = 5."),
            ("Why must r be even?", "To split a^r − 1 into (a^(r/2) − 1)(a^(r/2) + 1)."),
            ("For N = 15, Q = 256 and r = 4. Which y can be measured?", "Only 0, 64, 128 and 192, each with probability ¼."),
            ("Why is Q chosen at least N²?", "So that continued fractions can recover r from y/Q: the peaks are close enough to k/r to pin down a fraction with denominator below N."),
            ("Why can't an ordinary computer just run this simulation for a 2,048-bit number?", "It would need to store 2^4,096 complex numbers, far more than there are atoms in the observable universe."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Shor's paper (1995 version)", text="\"Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer\".",
                 draw=C.draw_manuscript, link="https://arxiv.org/abs/quant-ph/9508027", link_text="arXiv quant-ph/9508027", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ShorFactoring", d["checks"],
                           "the classical reduction for every a and 18 values of N, the exact probability peaks for N = 15 and 21, and the whole algorithm simulated with every amplitude stored for 12 values of N, each factor checked.",
                           ["static long splitWith(long a, long r, long n)", "static List<Long> convergentDenominators(long y, long Q, long limit)"]),
    ]
    return dict(
        title="Shor's Factoring Algorithm", date="1994",
        description="Era 7, topic 11 of The Algorithm Evolution Atlas: Shor's quantum algorithm for factoring and discrete logarithms, the reduction to period finding, the quantum Fourier transform, and what it would take to run it.",
        lede="Public-key cryptography bet that factoring large numbers is hopelessly slow. In 1994 Peter Shor showed that on a quantum computer it is not: factoring becomes finding a period, and a period is what a Fourier transform finds.",
        fieldnote=f"I simulated the quantum computer on an ordinary one, storing every amplitude, and it factored N = 1,007 after a couple of measurements. For a number of 2,048 bits the same simulation would need 2^{cost[-1]['amps']} stored numbers. This species has the algorithm; it does not yet have the machine.",
        card=[("When", "1994"),
              ("Where", "Bell Labs, Murray Hill"),
              ("What hurt", "Factoring seemed superpolynomial on any computer"),
              ("The fix", "Period finding by a quantum Fourier transform"),
              ("Checked", f"12 numbers factored in {sh['total']} simulated measurements")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ShorFactoring.java`.",
    )
