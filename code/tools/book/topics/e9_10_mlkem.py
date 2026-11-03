"""Era 9, topic 10: Lattice cryptography and ML-KEM. Every number is parsed from LatticeKem.java's output."""
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("lwe: "):
            d["lwe"] = re.match(r"lwe: (\d+) equations in (\d+) unknowns modulo (\d+), .*?, (\d+) trials ; without errors .*? recovers the secret (\d+) times ; with errors .*?: (\d+) times, and on average ([\d.]+) of the", ln).groups()
        elif ln.startswith("ntt: "):
            d["ntt"] = re.search(r"schoolbook ([\d,]+), through the NTT about ([\d,]+)", ln).groups()
            d["ntt_pow"] = re.search(r"17\^128 = (\d+)", ln).group(1)
        elif ln.startswith("params: "):
            d["params"] = re.findall(r"(ML-KEM-\d+) k (\d), eta1 (\d), eta2 (\d), du (\d+), dv (\d): public key 384k\+32 = ([\d,]+) bytes, ciphertext 32\(du k \+ dv\) = ([\d,]+) bytes, secret key 768k\+96 = ([\d,]+) bytes \(published: ([\d,]+), ([\d,]+), ([\d,]+)\) ; ([\d,]+) messages under (\d+) keys, (\d+) wrong bits, largest noise (\d+) against the margin (\d+)", ln)
        elif ln.startswith("noise: "):
            d["noise"] = re.findall(r"(ML-KEM-768 as published|eta1 = eta2 = \d+|du = \d+, dv = \d+): (\d+) wrong bits in ([\d,]+), largest noise (\d+)", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def circle_svg(d):
    def draw(t, standalone):
        W, H = 760, 380
        o = [C.text(20, 26, "Decryption reads each coefficient of v − sᵀu on a circle of 3,329 steps", t["ink"], 13, "start", 700)]
        cx, cy, R = 200, 200, 130
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" style="fill:none;stroke:{t["rule"]};stroke-width:2"/>')
        # decision regions: within q/4 of 0 reads 0, within q/4 of q/2 reads 1
        for ang, lab, col in [(0, "0", t["blue"]), (math.pi, "q/2", t["red"])]:
            x, y = cx + R * math.sin(ang), cy - R * math.cos(ang)
            o.append(C.circle(x, y, 7, col))
            o.append(C.text(x + (14 if ang == 0 else 14), y + (-6 if ang == 0 else 18), lab, t["ink"], 13, "start", 700))
        for ang in [math.pi / 2, 3 * math.pi / 2]:
            o.append(C.line(cx + (R - 18) * math.sin(ang), cy - (R - 18) * math.cos(ang), cx + (R + 18) * math.sin(ang), cy - (R + 18) * math.cos(ang), t["ink"], 2))
        o.append(C.text(cx, cy - 6, "reads 0 above,", t["muted"], 12, "middle"))
        o.append(C.text(cx, cy + 12, "1 below", t["muted"], 12, "middle"))
        rows = d["params"]
        o.append(C.text(400, 70, "Largest noise seen, against the margin q/4 = 832", t["ink"], 12, "start", 700))
        for i, r in enumerate(rows):
            y = 90 + i * 40
            noise, margin = int(r[15]), int(r[16])
            o.append(C.text(400, y + 15, r[0], t["ink"], 12))
            o.append(C.rect(500, y, 220 * noise / (2 * margin), 20, t["blue"], None, 0, 2))
            o.append(C.line(500 + 110, y - 4, 500 + 110, y + 24, t["red"], 2))
            o.append(C.text(505 + 220 * noise / (2 * margin), y + 15, str(noise), t["ink"], 12))
        o.append(C.text(610, 230, "margin", t["red"], 11, "middle"))
        o.append(C.text(20, H - 14, "A 0 is sent as 0 and a 1 as about q/2; noise moves each coefficient along the circle. Past a quarter turn, the bit flips.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "How ML-KEM decryption reads bits, and how much noise it tolerates", t, standalone, 0.55, 760)
    return draw


KEM_HTML = """
<div class="board kem-board">
  <div style="min-width:0"><div class="kem-view" id="kem-view"></div></div>
  <div style="min-width:0">
    <label class="kem-row">k (module rank) <input type="range" id="kem-k" min="1" max="4" value="2"> <b id="kem-kv"></b></label>
    <label class="kem-row">η, size of the small errors <input type="range" id="kem-eta" min="1" max="14" value="2"> <b id="kem-etav"></b></label>
    <label class="kem-row">d_u, bits kept of u <input type="range" id="kem-du" min="3" max="11" value="10"> <b id="kem-duv"></b></label>
    <label class="kem-row">d_v, bits kept of v <input type="range" id="kem-dv" min="1" max="5" value="4"> <b id="kem-dvv"></b></label>
    <div class="kem-btns"><button type="button" class="primary" id="kem-go">Encrypt a random message</button><button type="button" id="kem-std">ML-KEM-768</button></div>
    <div class="kem-res" id="kem-res"></div>
    <p class="say" id="kem-say" aria-live="polite"></p>
  </div>
</div>
"""

KEM_CSS = """
.kem-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.kem-board{grid-template-columns:1fr}}
.kem-view svg{width:100%;height:auto;display:block;background:var(--wash)}
.kem-row{display:block;font-size:13px;margin:6px 0}
.kem-row input{vertical-align:middle;width:8em}
.kem-btns{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
.kem-res{font:12.5px var(--mono);display:grid;gap:2px}
"""

KEM_JS = r"""
(() => {
  const view = document.getElementById("kem-view");
  if (!view) return;
  const N = 256, Q = 3329;
  let seed = 3;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  const md = x => ((x % Q) + Q) % Q, centre = x => x > Q / 2 ? x - Q : x;
  const uni = () => Array.from({length: N}, () => Math.floor(rnd() * Q));
  const cbd = eta => Array.from({length: N}, () => { let x = 0; for (let i = 0; i < eta; i++) x += (rnd() < 0.5) - (rnd() < 0.5); return md(x); });
  function mul(a, b) { const c = new Float64Array(N); for (let i = 0; i < N; i++) { if (!a[i]) continue; for (let j = 0; j < N; j++) { const p = a[i] * b[j]; if (i + j < N) c[i + j] += p; else c[i + j - N] -= p; } } return Array.from(c, md); }
  const add = (a, b) => a.map((x, i) => md(x + b[i])), sub = (a, b) => a.map((x, i) => md(x - b[i]));
  const comp = (x, d) => Math.floor((x * 2 ** d + Math.floor(Q / 2)) / Q) % 2 ** d, decomp = (y, d) => Math.floor((y * Q + 2 ** (d - 1)) / 2 ** d);
  const rt = (a, d) => a.map(x => decomp(comp(x, d), d));
  const val = id => +document.getElementById(id).value;
  function go() {
    const k = val("kem-k"), eta = val("kem-eta"), du = val("kem-du"), dv = val("kem-dv");
    ["k", "eta", "du", "dv"].forEach(n => document.getElementById(`kem-${n}v`).textContent = val(`kem-${n}`));
    const A = [...Array(k)].map(() => [...Array(k)].map(uni)), s = [...Array(k)].map(() => cbd(eta)), e = [...Array(k)].map(() => cbd(eta));
    const t = A.map((row, i) => row.reduce((acc, a, j) => add(acc, mul(a, s[j])), e[i]));
    const m = Array.from({length: N}, () => rnd() < 0.5 ? 1 : 0), r = [...Array(k)].map(() => cbd(eta));
    const u = [...Array(k)].map((_, i) => rt(A.reduce((acc, row, j) => add(acc, mul(row[i], r[j])), cbd(eta)), du));
    const v = rt(add(t.reduce((acc, ti, j) => add(acc, mul(ti, r[j])), cbd(eta)), m.map(b => b * 1665)), dv);
    const w = sub(v, s.reduce((acc, si, j) => add(acc, mul(si, u[j])), new Array(N).fill(0)));
    let wrong = 0, worst = 0;
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 400 400", role: "img", "aria-label": "The 256 decrypted coefficients on a circle modulo q"}, view);
    sv("circle", {cx: 200, cy: 200, r: 150, fill: "none", stroke: "var(--rule)", "stroke-width": 2}, svg);
    sv("line", {x1: 30, x2: 370, y1: 200, y2: 200, stroke: "var(--ink)", "stroke-dasharray": "4 4"}, svg);
    sv("text", {x: 200, y: 32, "text-anchor": "middle", "font-size": 12, fill: "var(--ink)"}, svg, "0: reads as 0");
    sv("text", {x: 200, y: 380, "text-anchor": "middle", "font-size": 12, fill: "var(--ink)"}, svg, "q/2: reads as 1");
    w.forEach((x, i) => {
      const bit = comp(x, 1), bad = bit !== m[i]; if (bad) wrong++;
      worst = Math.max(worst, Math.abs(centre(md(x - m[i] * 1665))));
      const ang = 2 * Math.PI * x / Q, rr = 96 + (i % 8) * 7;
      sv("circle", {cx: 200 + rr * Math.sin(ang), cy: 200 - rr * Math.cos(ang), r: bad ? 5 : 3, fill: m[i] ? "var(--red)" : "var(--blue)", stroke: bad ? "var(--ink)" : "none", "stroke-width": 2}, svg);
    });
    const res = document.getElementById("kem-res"); res.innerHTML = "";
    [`public key  ${384 * k + 32} bytes`, `ciphertext  ${32 * (du * k + dv)} bytes`, `wrong bits  ${wrong} of 256`, `largest noise ${worst} (margin ${Math.floor(Q / 4)})`].forEach(x => el("div", {}, res, x));
    document.getElementById("kem-say").textContent = wrong
      ? `Too much noise: ${wrong} bits landed on the wrong side of the dashed line. Real parameters keep the noise far inside the margin, so that a failure is astronomically rare.`
      : "Blue dots are 0 bits, red dots are 1 bits, after decryption. The noise spreads them around 0 and q/2, but none crosses the dashed line. Raise η or lower d_u and d_v to make the noise larger.";
  }
  ["kem-k", "kem-eta", "kem-du", "kem-dv"].forEach(id => document.getElementById(id).addEventListener("change", go));
  document.getElementById("kem-go").addEventListener("click", go);
  document.getElementById("kem-std").addEventListener("click", () => { document.getElementById("kem-k").value = 3; document.getElementById("kem-eta").value = 2; document.getElementById("kem-du").value = 10; document.getElementById("kem-dv").value = 4; go(); });
  go();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How ML-KEM combined older ideas, and where it led")
    W = 220
    nodes = {
        "pk": (20, 20, "Public-key cryptography", "anyone can lock, only the key holder can open", "Era 6, topic 10", "ink"),
        "shor": (265, 20, "Shor's algorithm", "a quantum computer would break RSA and Diffie–Hellman", "Era 7, topic 11", "ink"),
        "lwe": (510, 20, "Learning with errors", "linear equations nudged by small errors", "Regev, 2005", "ink"),
        "fft": (755, 20, "The fast Fourier transform", "and its modular cousin, the NTT", "Era 6, topic 1", "ink"),
        "kyber": (387, 200, "Kyber, then ML-KEM", "⊕ module LWE over polynomials, NTT arithmetic, compression", "submitted 2017; FIPS 203, 2024", "red"),
        "signal": (140, 380, "Signal's PQXDH", "a Kyber-based protocol for messages", "2023", "blue"),
        "hyb": (635, 380, "Hybrid key exchange", "classical and post-quantum together", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("pk", "kyber", ports=("bottom", "top:0.1"))
    D.edge("shor", "kyber", ports=("bottom", "top:0.37"))
    D.edge("lwe", "kyber", ports=("bottom", "top:0.63"))
    D.edge("fft", "kyber", ports=("bottom", "top:0.9"))
    D.edge("kyber", "signal", ports=("bottom:0.2", "top"))
    D.edge("kyber", "hyb", ports=("bottom:0.8", "top"))
    return D


def chain():
    steps = [
        ("A large quantum computer would break RSA and elliptic-curve key exchange, and messages recorded today",
         "Rest on learning with errors, which no known quantum algorithm solves", "Regev, 2005"),
        ("Plain LWE keys are large matrices of numbers",
         "Use polynomials modulo X²⁵⁶ + 1: one row describes a whole block", "Kyber, 2017"),
        ("Polynomial products cost n² multiplications, and ciphertexts are still long",
         "Multiply through the NTT; round ciphertexts to fewer bits", "FIPS 203, 2024"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from RSA to ML-KEM")
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
    lw, nt = d["lwe"], d["ntt"]
    prow = [[r[0], r[1], r[2], f"{r[4]}, {r[5]}", f"{r[6]} ({r[9]})", f"{r[7]} ({r[10]})", f"{r[8]} ({r[11]})", f"{r[14]} in {r[12]}", r[15]] for r in d["params"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Public-key cryptography (Era 6) rests on factoring and discrete logarithms, both of which Shor's algorithm (Era 7) would solve on a large quantum computer. In 2005 Oded Regev described a different hard problem, learning with errors. Kyber built a key exchange on it from polynomials, multiplied fast with the number-theoretic transform, the fast Fourier transform's modular cousin; in August 2024 NIST standardized it as ML-KEM."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Kyber and ML-KEM. Blue: where it went next."),
        ]),
        dict(id="play", eyebrow="Try it", title="Noise, and the margin", toc="Try it", blocks=[
            dict(type="p", text="Your browser runs the scheme's arithmetic: a key pair, then one encryption and decryption of 256 random bits. Each decrypted coefficient is drawn on a circle of 3,329 steps: 0 bits should land near the top, 1 bits near the bottom. Make the errors larger, or keep fewer bits of the ciphertext, and watch the dots spread until some cross the line."),
            dict(type="widget", html=KEM_HTML, js=KEM_JS, css=KEM_CSS,
                 fallback=dict(type="svg", name="circle", draw=circle_svg(d), alt="How decryption reads bits on a circle, and the noise measured for each parameter set", width=760),
                 note="In the interactive edition you can change the parameters and encrypt messages yourself."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Equations with errors", toc="How it works", blocks=[
            dict(type="p", text="**Learning with errors.** Pick a random matrix A and a secret vector s with small entries, and publish A and b = As + e (mod q), where e is a vector of small random errors. Without e, Gaussian elimination recovers s at once. With e, nobody knows an efficient way, on an ordinary or a quantum computer."),
            dict(type="p", text="**Polynomials.** ML-KEM's numbers are polynomials of degree below 256 with coefficients modulo q = 3,329, multiplied modulo X²⁵⁶ + 1; A is a k × k matrix of them, s and e vectors of k. Small means coefficients from a centred binomial distribution: η coin flips minus η more."),
            dict(type="p", text="**Keys and encryption.** The public key is A (sent as a seed) and t = As + e. To send 256 bits m, pick small r, e₁ and e₂ and send u = Aᵀr + e₁ and v = tᵀr + e₂ + ⌈q/2⌋·m, each rounded to d_u and d_v bits. The receiver computes v − sᵀu = eᵀr + e₂ − sᵀe₁ + rounding + ⌈q/2⌋·m. Everything but the last term is small, so each coefficient is near 0 for a 0 bit and near q/2 for a 1."),
            dict(type="p", text="**The NTT.** Because 17 is a primitive 256th root of unity modulo 3,329, a polynomial can be transformed so that multiplication becomes 128 small products of pairs. ML-KEM wraps this encryption scheme (K-PKE) with hashing to make a key-encapsulation mechanism: a shared secret key that two parties can agree on."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Hide the secret under noise small enough for the key holder to round away and large enough that no one else can solve the equations."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Three parameter sets", toc="Measured", blocks=[
            dict(type="p", text=f"**With and without errors.** {lw[0]} equations in {lw[1]} unknowns modulo {lw[2]}, {lw[3]} random trials. Without errors, Gaussian elimination recovered the secret **{lw[4]}** times. With errors from −2 to 2 added: **{lw[5]}** times; on average {lw[6]} of the {lw[1]} entries came out wrong. A tiny error ruins the method completely."),
            dict(type="p", text=f"**The NTT.** 17¹²⁸ = {d['ntt_pow']} = −1 modulo 3,329, so 17 is a primitive 256th root of unity. On 50 random pairs of polynomials, multiplying through the NTT gave exactly the schoolbook product modulo X²⁵⁶ + 1, with about {nt[1]} multiplications instead of {nt[0]}."),
            dict(type="p", text="**The parameter sets.** The program computes key and ciphertext sizes from the formulas (public key 384k + 32 bytes, ciphertext 32(d_u·k + d_v), secret key 768k + 96) and compares them with the published sizes, in brackets; then it encrypts 1,000 random 256-bit messages under 20 keys for each set:"),
            dict(type="table", head=["Set", "k", "η₁", "d_u, d_v", "Public key", "Ciphertext", "Secret key", "Wrong bits", "Largest noise"], num=[1, 2, 4, 5, 6, 8], rows=prow),
            dict(type="p", text="A bit is read wrongly only when the noise passes q/4 = 832. The largest noise seen in 256,000 coefficients per set stayed well under half of that. FIPS 203 puts the probability that a decapsulation fails at 2⁻¹³⁸·⁸, 2⁻¹⁶⁴·⁸ and 2⁻¹⁷⁴·⁸ for the three sets."),
            dict(type="p", text="**Too much noise.** k = 3 and 100 messages each, with larger errors or harsher rounding:"),
            dict(type="table", head=["Variant", "Wrong bits", "Out of", "Largest noise"], num=[1, 2, 3], rows=[[a, b, c, e] for a, b, c, e in d["noise"]], hl=0),
            dict(type="p", text="The parameters are a balance: more noise makes the equations harder to solve, until it makes decryption fail."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="NIST, August 2024", toc="The evidence", blocks=[
            dict(type="p", text="NIST, FIPS 203, \"Published August 13, 2024\": \"ML-KEM is derived from the round-three version of the CRYSTALS-KYBER KEM\"; \"The security of ML-KEM is related to the computational difficulty of the Module Learning with Errors problem\"; q is \"the prime integer 3329\"; \"𝜁 = 17 ∈ ℤ𝑞 is a primitive 256-th root of unity modulo 𝑞\"; decapsulation failure probabilities 2⁻¹³⁸·⁸, 2⁻¹⁶⁴·⁸ and 2⁻¹⁷⁴·⁸."),
            dict(type="p", text="Wikipedia: Kyber was submitted to NIST in 2017 and was \"the first key encapsulation mechanism that has been selected for standardization\"; it is \"based on the module learning with errors (M-LWE) problem, in conjunction with cyclotomic rings\", \"derived from a method published in 2005 by Oded Regev\"; Signal adopted the Kyber-based PQXDH protocol in 2023. The parameter sets' sizes are from the chapter on ML-KEM in *Elements of Cryptanalysis* and agree with Wikipedia's for ML-KEM-768."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Two thousand years of linear equations", toc="Full circle", blocks=[
            dict(type="p", text="The Nine Chapters' fangcheng (Era 2) solved systems of linear equations by elimination on a counting board. ML-KEM's security rests on the same equations, made unsolvable by a little noise in each. The fast Fourier transform (Era 6), in its modular form, makes the arithmetic quick."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Gaussian elimination solved {lw[4]} of {lw[3]} systems exactly. Add errors of at most 2 to each equation, and it solved {lw[5]}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What is the ML-KEM-768 public key size from 384k + 32 with k = 3?", "384 × 3 + 32 = 1,184 bytes."),
            ("Why does a bit flip only when the noise passes q/4?", "0 is sent as 0 and 1 as about q/2; the receiver picks the nearer of the two, and they are q/2 apart, so a coefficient is read wrongly only if it moves more than q/4."),
            ("With η = 2, what values can one coefficient of a small polynomial take?", "−2 to 2: two coin flips minus two coin flips."),
            ("Why does rounding u and v to fewer bits not break decryption?", "Rounding adds at most half a step of the coarser scale, a little extra noise that stays inside the margin for the published parameters."),
            ("Why would an attacker record encrypted traffic today?", "To decrypt it later, if a large quantum computer is ever built; this is why the replacement started before such a computer exists."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard (2024)", text="NIST.",
                 draw=C.draw_manuscript, link="https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf", link_text="FIPS 203 (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LatticeKem", d["checks"],
                           "Gaussian elimination with and without errors, the NTT against schoolbook multiplication, every message of every parameter set, the sizes against the published ones, and decryption failing when the noise is too large.",
                           ["static int[] ntt(int[] a)", "static int roundTripMessage(Params P, Keys K, Random r, int[] noise, int du, int dv)"]),
    ]
    return dict(
        title="Lattice Cryptography and ML-KEM", date="2017–2024",
        description="Era 9, topic 10 of The Algorithm Evolution Atlas: learning with errors and ML-KEM (Kyber; FIPS 203, 2024), its arithmetic implemented and its noise measured.",
        lede="A large quantum computer would break the public-key methods that protect the internet, and messages recorded today could be read later. The replacement rests on linear equations that a little noise makes unsolvable. In August 2024 it became a United States standard, ML-KEM.",
        fieldnote=f"I gave the program sixteen equations and asked for the secret behind them. It found it {lw[4]} times out of {lw[3]}. Then I nudged every equation by at most two, and it found it {lw[5]} times. The receiver of an ML-KEM message carries a little of that noise too, but knows the secret, and rounds it away.",
        card=[("When", "Regev 2005; Kyber 2017; FIPS 203, August 2024"),
              ("Where", "The CRYSTALS-Kyber team; NIST"),
              ("What hurt", "Quantum computers would break RSA and Diffie–Hellman"),
              ("The fix", "Module learning with errors, NTT arithmetic, compression"),
              ("Checked", "Sizes of all three sets; every test message decrypted")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LatticeKem.java`.",
    )
