"""Era 8, topic 10: PRIMES is in P. Every number is parsed from AksPrimality.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"sieve: n = 2 to ([\d,]+): AKS agrees with the sieve on all ([\d,]+) ; decided at step 1 \(perfect power\): (\d+), step 3 \(a small common factor\): ([\d,]+), step 4 \(n <= r, prime\): (\d+), step 5 \(a polynomial check fails\): (\d+), step 6 \(all polynomial checks pass, prime\): (\d+) ; largest r (\d+), largest number of values of a (\d+)", ln):
            d["sieve"] = dict(N=m.group(1), all=m.group(2), s1=m.group(3), s3=m.group(4), s4=m.group(5), s5=m.group(6), s6=m.group(7), r=m.group(8), a=m.group(9))
        elif ln.startswith("tricky: "):
            d["tricky"] = re.findall(r"(\d+): Fermat's test fooled by every coprime base: (yes|no), Miller-Rabin base 2 fooled: (yes|no), AKS: composite at step (\d) \((.*?)\)(?: ;|$)", ln)
        elif ln.startswith("polynomial: "):
            d["poly"] = re.findall(r"([\d,]+) = ([\d,]+) x ([\d,]+): r = (\d+), so no factor is found by step 3 ; composite at step 5 \((.*?)\)", ln)
        elif ln.startswith("cost: "):
            d["cost"] = re.findall(r"([\d,]+): r = (\d+), a up to (\d+), ([\d,]+) coefficient multiplications \(Miller-Rabin with bases 2, 3, 5, 7: (\d+) multiplications\)", ln)
        elif ln.startswith("widget: "):
            d["widget"] = [dict(n=int(a), verdict=b, step=int(c), r=int(e), amax=int(f), why=g) for a, b, c, e, f, g in
                           re.findall(r"(\d+): (prime|composite) at step (\d), r = (\d+), a up to (\d+) \((.*?)\)(?: ;|$)", ln)]
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def pascal_svg(d):
    def draw(t, standalone):
        o = []
        W, H = 760, 440
        o.append(C.text(20, 26, "Pascal's triangle, rows 2 to 16: a middle number is shaded when the row number divides it", t["ink"], 13, "start", 700))
        rows = list(range(2, 17))
        cw, ch, top = 40, 23, 50
        for i, n in enumerate(rows):
            vals = [math.comb(n, k) for k in range(n + 1)]
            prime = all(n % p for p in range(2, int(n ** 0.5) + 1))
            y = top + i * ch
            x0 = 410 - (n + 1) * cw / 2
            o.append(C.text(18, y + 15, f"{n}", t["red"] if prime else t["muted"], 12, "start", 700 if prime else 400))
            for k, v in enumerate(vals):
                if 0 < k < n:
                    shaded = v % n == 0
                    o.append(C.rect(x0 + k * cw + 1, y + 1, cw - 2, ch - 2, t["yellow"] if shaded else t["surface"], t["axis"], 0.8))
                txt = str(v) if v < 100000 else f"{v // 1000}k"
                o.append(C.text(x0 + k * cw + cw / 2, y + 15, txt, t["on_yellow"] if (0 < k < n and v % n == 0) else t["ink"], 9.5 if v >= 1000 else 11, "middle"))
        o.append(C.text(18, H - 12, "Red row numbers are prime: only their rows are shaded all the way across.", t["ink"], 12.5))
        return C.svg_doc(W, H, "".join(o), "Pascal's triangle with entries divisible by their row number shaded", t, standalone, 0.5, 760)
    return draw


AK_HTML = """
<div class="board ak-board">
  <div style="min-width:0">
    <div class="controls"><label>n <input id="ak-n" type="number" min="2" max="20000" value="97"></label><button type="button" class="primary" id="ak-go">Run AKS</button></div>
    <div class="presets" id="ak-pre"></div>
    <ol class="steps ak-steps" id="ak-steps"></ol>
  </div>
  <div style="min-width:0">
    <div class="ak-row" id="ak-row" aria-label="Row n of Pascal's triangle, modulo n"></div>
    <p class="say" id="ak-say" aria-live="polite"></p>
  </div>
</div>
"""

AK_CSS = """
.ak-board .controls{display:flex;gap:8px;align-items:end;flex-wrap:wrap}
.ak-board .presets{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}
.ak-steps{margin-top:8px}
.ak-steps li{padding:3px 6px}
.ak-steps li.bad{color:var(--red);font-weight:600}
.ak-row{display:flex;flex-wrap:wrap;gap:2px;font:11px var(--mono)}
.ak-row span{min-width:22px;text-align:center;padding:2px 3px;background:var(--wash)}
.ak-row span.z{background:var(--yellow);color:var(--on-yellow)}
"""

AK_JS = r"""
(() => {
  const inp = document.getElementById("ak-n");
  if (!inp) return;
  const PROG = __PROG__;
  const gcd = (a, b) => { while (b) [a, b] = [b, a % b]; return a; };
  function perfectPower(n) {
    for (let b = 2; 2 ** b <= n; b++) { const a = Math.round(Math.pow(n, 1 / b)); for (let c = Math.max(2, a - 1); c <= a + 1; c++) { let p = 1; for (let i = 0; i < b && p <= n; i++) p *= c; if (p === n) return [c, b]; } }
    return null;
  }
  function order(n, r) { const x = n % r; let k = 1, v = x; while (v !== 1) { v = v * x % r; k++; if (k > r) return -1; } return k; }
  function phi(r) { let res = r, x = r; for (let p = 2; p * p <= x; p++) if (x % p === 0) { while (x % p === 0) x /= p; res -= res / p; } if (x > 1) res -= res / x; return res; }
  function mulMod(a, b, r, n) { const c = new Array(r).fill(0); for (let i = 0; i < r; i++) if (a[i]) for (let j = 0; j < r; j++) { let k = i + j; if (k >= r) k -= r; c[k] += a[i] * b[j]; } for (let k = 0; k < r; k++) c[k] %= n; return c; }
  function powXa(a, n, r) { let res = new Array(r).fill(0); res[0] = 1; let base = new Array(r).fill(0); base[0] = a % n; base[1 % r] = (base[1 % r] + 1) % n; let e = n; while (e > 0) { if (e & 1) res = mulMod(res, base, r, n); e = Math.floor(e / 2); if (e > 0) base = mulMod(base, base, r, n); } return res; }
  function aks(n) {
    const lines = [];
    const pp = perfectPower(n);
    if (pp) { lines.push([`Step 1: ${n} = ${pp[0]}^${pp[1]}, a perfect power: composite.`, true]); return {lines, prime: false, step: 1, r: 0, amax: 0}; }
    lines.push([`Step 1: ${n} is not a perfect power.`]);
    const l = Math.log(n) / Math.log(2);
    let r = 2; while (true) { if (gcd(n, r) === 1 && order(n, r) > l * l) break; r++; }
    lines.push([`Step 2: (log₂ n)² = ${(l * l).toFixed(1)}; the smallest r whose powers of n take longer to return to 1 is r = ${r}.`]);
    for (let a = 2; a <= Math.min(r, n - 1); a++) { const g = gcd(a, n); if (g > 1 && g < n) { lines.push([`Step 3: gcd(${a}, ${n}) = ${g}: composite.`, true]); return {lines, prime: false, step: 3, r, amax: 0}; } }
    lines.push([`Step 3: no a up to ${Math.min(r, n - 1)} shares a factor with ${n}.`]);
    if (n <= r) { lines.push([`Step 4: n = ${n} ≤ r = ${r}: prime.`]); return {lines, prime: true, step: 4, r, amax: 0}; }
    const amax = Math.floor(Math.sqrt(phi(r)) * l);
    for (let a = 1; a <= amax; a++) {
      const p = powXa(a, n, r), want = new Array(r).fill(0); want[n % r] = 1; want[0] = (want[0] + a) % n;
      if (p.some((v, i) => v !== want[i])) { lines.push([`Step 5: (X + ${a})^${n} is not X^${n % r} + ${a} modulo (X^${r} − 1, ${n}): composite.`, true]); return {lines, prime: false, step: 5, r, amax}; }
    }
    lines.push([`Step 5: (X + a)^${n} = X^${n % r} + a modulo (X^${r} − 1, ${n}) for every a from 1 to ${amax}.`]);
    lines.push([`Step 6: prime.`]);
    return {lines, prime: true, step: 6, r, amax};
  }
  function pascalRow(n) {
    const row = el("div", {}, null), box = document.getElementById("ak-row"); box.innerHTML = "";
    if (n > 60) { el("span", {}, box, `row ${n} of Pascal's triangle has ${n + 1} numbers; try n ≤ 60 to see them`); return; }
    let r = [1]; for (let m = 1; m <= n; m++) { const nx = [1]; for (let k = 1; k < m; k++) nx.push((r[k - 1] + r[k]) % n); nx.push(1); r = nx; }
    r.forEach((v, k) => el("span", {class: k > 0 && k < n && v === 0 ? "z" : ""}, box, String(v)));
  }
  function run() {
    const n = Math.max(2, Math.min(20000, parseInt(inp.value) || 2)); inp.value = n;
    const res = aks(n), ol = document.getElementById("ak-steps"); ol.innerHTML = "";
    res.lines.forEach(([txt, bad]) => el("li", {class: bad ? "bad" : ""}, ol, txt));
    pascalRow(n);
    const pg = PROG.find(p => p.n === n);
    document.getElementById("ak-say").textContent = `${n} is ${res.prime ? "prime" : "composite"} (decided at step ${res.step}). Right: row ${n} of Pascal's triangle modulo ${n}; yellow marks middle numbers divisible by ${n}.` + (pg ? ` The program: ${pg.verdict} at step ${pg.step}, r = ${pg.r}.` : "");
  }
  const pre = document.getElementById("ak-pre");
  for (const n of [7, 9, 31, 97, 341, 561, 1009]) { const b = el("button", {type: "button"}, pre, String(n)); b.addEventListener("click", () => { inp.value = n; run(); }); }
  document.getElementById("ak-go").addEventListener("click", run);
  inp.addEventListener("keydown", e => { if (e.key === "Enter") run(); });
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How PRIMES is in P combined older ideas, and where it led")
    W = 210
    nodes = {
        "pas": (20, 20, "Pascal's triangle", "the middle of row n is divisible by n only when n is prime", "the binomial numbers", "ink"),
        "rand": (395, 20, "Randomized tests", "fast, wrong with tiny probability", "Solovay–Strassen; Era 6", "ink"),
        "cond": (770, 20, "Conditional tests", "deterministic, if an unproved hypothesis holds", "generalized Riemann hypothesis", "ink"),
        "aks": (395, 180, "AKS", "⊕ the identity checked modulo Xʳ − 1", "IIT Kanpur, 6 August 2002", "red"),
        "pz": (20, 340, "Prizes", "Gödel and Fulkerson, 2006", "", "ink"),
        "lp": (770, 340, "Conjectured speed-ups", "Õ(log⁶ n), perhaps Õ(log³ n)", "in the 2002 preprint", "ink"),
        "today": (395, 490, "Known, not used", "practice keeps faster tests such as Baillie–PSW", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("pas", "aks", ports=("bottom", "top:0.15"))
    D.edge("rand", "aks", ports=("bottom", "top"), label="without chance", at=0.5, dx=8, anchor="start")
    D.edge("cond", "aks", ports=("bottom", "top:0.85"))
    D.edge("aks", "pz", ports=("bottom:0.15", "top"))
    D.edge("aks", "lp", ports=("bottom:0.85", "top"))
    D.edge("aks", "today", ports=("bottom", "top"))
    D.text(20, 615, "Wikipedia: \"of immense theoretical importance\" but \"not used in practice, rendering it a galactic algorithm\".", "caption")
    return D


def chain(d):
    tr, cost = d["tricky"], d["cost"]
    last = cost[-1]
    steps = [
        (f"Fermat's test is fooled by every coprime base for Carmichael numbers like {tr[0][0]}",
         "Randomized tests: a composite slips through only with a probability that can be made tiny", "Solovay and Strassen, Era 6"),
        ("Every fast test was randomized, limited to special numbers, or relied on an unproved hypothesis",
         "AKS: general, polynomial, deterministic and unconditional", "Agrawal, Kayal and Saxena, 2002"),
        (f"Polynomial is not fast: {last[3]} coefficient multiplications for {last[0]}",
         f"In practice, other tests: Miller–Rabin needed {last[4]} multiplications", "Baillie–PSW, per Wikipedia"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from chance to certainty to cost")
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
    sv, tr, po, co, wg = d["sieve"], d["tricky"], d["poly"], d["cost"], d["widget"]
    step_rows = [["1: a perfect power", sv["s1"]], ["3: a common factor with some a ≤ r", sv["s3"]], ["4: n ≤ r, so prime", sv["s4"]],
                 ["5: a polynomial check fails", sv["s5"]], ["6: every polynomial check passes, so prime", sv["s6"]]]
    tr_rows = [[n, f, m, f"step {s}: {w}"] for n, f, m, s, w in tr]
    po_rows = [[n, f"{a} × {b}", r, w] for n, a, b, r, w in po]
    co_rows = [[n, r, a, m, mr] for n, r, a, m, mr in co]
    wg_rows = [[str(w["n"]), w["verdict"], str(w["step"]), str(w["r"]), str(w["amax"]), w["why"]] for w in wg]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Row n of Pascal's triangle is divisible by n, apart from its two 1s, exactly when n is prime. The fast primality tests of Era 6 flipped coins; others were deterministic only if an unproved hypothesis is true. Agrawal, Kayal and Saxena checked the Pascal identity in a much smaller world, polynomials modulo Xʳ − 1, and proved that a few checks there are enough. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: AKS. Blue: its place today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Run AKS on a number", toc="Try it", blocks=[
            dict(type="p", text="Type a number up to 20,000 and run the test step by step: the perfect-power check, the choice of r, the common-factor check, and the polynomial checks. On the right, row n of Pascal's triangle modulo n: for a prime every middle number is 0. The buttons are the numbers the program traced; for them the widget reaches the same verdict at the same step with the same r."),
            dict(type="widget", html=AK_HTML, js=AK_JS.replace("__PROG__", json.dumps(wg)), css=AK_CSS,
                 fallback=dict(type="table", head=["n", "Verdict", "Step", "r", "a up to", "Why"], num=[0, 2, 3, 4], rows=wg_rows),
                 note="In the interactive edition you can run the test on any number up to 20,000."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Pascal's triangle, in a smaller world", toc="How it works", blocks=[
            dict(type="p", text="**The identity.** For n > 1 and any a with no factor in common with n: n is prime exactly when (X + a)ⁿ = Xⁿ + a, with every coefficient taken modulo n. The middle coefficients of (X + a)ⁿ are the numbers of row n of Pascal's triangle times powers of a, and all of them are divisible by n exactly when n is prime."),
            dict(type="svg", name="pascal", draw=pascal_svg(d), alt="Pascal's triangle with entries divisible by their row shaded", width=760),
            dict(type="p", text="**The trouble.** (X + a)ⁿ has n + 1 coefficients, so checking them all is no faster than trying divisors."),
            dict(type="p", text="**The idea.** Compute (X + a)ⁿ modulo Xʳ − 1 as well, so every polynomial has fewer than r coefficients, by repeated squaring. The steps: (1) if n is a perfect power, it is composite; (2) find the smallest r whose powers of n take more than (log₂ n)² steps to return to 1 modulo r; (3) if some a ≤ r shares a factor with n, n is composite; (4) if n ≤ r, n is prime; (5) for a = 1 to ⌊√φ(r) log₂ n⌋, if (X + a)ⁿ ≠ X^(n mod r) + a modulo (Xʳ − 1, n), n is composite; (6) otherwise n is prime. The proof shows that r stays small, so every step takes time polynomial in the number of digits."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A test that is exact but too big can become small without becoming wrong, if you can prove that every composite fails it even in the small version. The proof is the algorithm."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Every number up to 3,000", toc="Measured", blocks=[
            dict(type="p", text=f"**The identity in full**: for every n from 2 to 300, the middle numbers of row n of Pascal's triangle are all divisible by n exactly when n is prime."),
            dict(type="p", text=f"**AKS against a sieve**, n = 2 to {sv['N']}: they agree on all {sv['all']}. Which step decided each number (largest r: {sv['r']}; most values of a checked: {sv['a']}):"),
            dict(type="table", head=["Decided at step", "Numbers"], num=[1], rows=step_rows),
            dict(type="p", text="For numbers this small, every composite that is not a perfect power has a factor no larger than r, so step 3 finds it: the polynomial check never rejected a number here, it only confirmed primes. **Numbers that fool quick tests**:"),
            dict(type="table", head=["n", "Fermat fooled by every coprime base", "Miller–Rabin base 2 fooled", "AKS"], num=[0], rows=tr_rows),
            dict(type="p", text="**Composites only the polynomial check can catch**: products of two primes larger than r:"),
            dict(type="table", head=["n", "Factors", "r", "Step 5"], num=[0, 2], rows=po_rows),
            dict(type="p", text="**The cost** for primes, counted in multiplications of polynomial coefficients, against Miller–Rabin with four bases:"),
            dict(type="table", head=["Prime n", "r", "a up to", "AKS multiplications", "Miller–Rabin multiplications"], num=[0, 1, 2, 3, 4], rows=co_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Three computer scientists at Kanpur", toc="The evidence", blocks=[
            dict(type="p", text="Agrawal, Kayal and Saxena (Department of Computer Science and Engineering, IIT Kanpur), 6 August 2002: \"We present a deterministic polynomial-time algorithm that determines whether an input number n is prime or composite\"; the preprint's version checks the congruence modulo (x^r − 1, n) for a up to 2√r log n and runs in time Õ(log¹² n). *Annals of Mathematics* 160(2), 781–793 (2004). The 2006 Gödel Prize citation: earlier polynomial-time tests \"were based on probabilistic methods or they relied on an unproven assumption\", and \"the arguments come in a brilliantly simple manner; they remain completely elementary\"."),
            dict(type="p", text="Wikipedia: the first test \"simultaneously general, polynomial-time, deterministic, and unconditionally correct\"; earlier methods \"achieved three of these properties at most\"; the authors received the Gödel and Fulkerson Prizes in 2006; the version now usually presented, which the program follows, takes the smallest r whose order exceeds (log₂ n)²; AKS is \"of immense theoretical importance\" but \"not used in practice, rendering it a galactic algorithm\". Granville's survey in the *Bulletin of the AMS* (2005) opens with Gauss on the problem of telling primes from composites."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Chance, removed", toc="Full circle", blocks=[
            dict(type="p", text="Era 6's public-key cryptography needed large primes, and Rivest, Shamir and Adleman recommended Solovay and Strassen's \"probabilistic\" test to find them, accepting a tiny chance of error. AKS shows the chance is not necessary in principle. Compressed sensing (topic 12) makes the opposite move: it measures at random on purpose."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The Carmichael number {tr[0][0]} fools Fermat's test for every base it could choose. AKS rejected it at step {tr[0][3]}, without tossing a coin."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write row 6 of Pascal's triangle. Which middle numbers are divisible by 6?", "1 6 15 20 15 6 1: only the two 6s; 15 and 20 are not, so 6 is composite."),
            ("Why must perfect powers like 9 = 3² be removed first?", "The proof ends by showing that a number passing every polynomial check is a power of a prime; step 1 is what rules out the powers, leaving only the prime itself."),
            ("Why is it enough, for small n, that step 3 checks a up to r?", "Every composite n has a factor at most √n, and when r ≥ √n that factor is found by the gcd check."),
            ("Why is checking (X + a)ⁿ modulo Xʳ − 1 fast?", "Every polynomial has fewer than r coefficients, and repeated squaring needs about log₂ n multiplications of such polynomials."),
            ("If AKS is polynomial, why is it not used?", "Its polynomial has a large exponent and big constants: for 100,003 it needed hundreds of millions of multiplications against under a hundred for Miller–Rabin."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="PRIMES is in P (preprint, 6 August 2002)", text="The version that was announced, from IIT Kanpur.",
                 draw=C.draw_manuscript, link="https://www.cse.iitk.ac.in/users/nitin/papers/aug02.pdf", link_text="The preprint (PDF, IIT Kanpur)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "AksPrimality", d["checks"],
                           "the Pascal identity for every n up to 300, AKS against a sieve for every n up to 3,000, the numbers that fool quick tests, and composites that only the polynomial check can catch.",
                           ["static Verdict aks(long n)"]),
    ]
    c3 = co[-1]
    return dict(
        title="PRIMES is in P", date="2002",
        description="Era 8, topic 10 of The Algorithm Evolution Atlas: Agrawal, Kayal and Saxena's deterministic polynomial-time primality test (IIT Kanpur, 2002), checked against a sieve, Carmichael numbers and Miller–Rabin.",
        lede="Every fast primality test either tossed coins, worked only for special numbers, or relied on an unproved hypothesis. In August 2002 three computer scientists at Kanpur gave one that does none of these: it checks Pascal's identity for primes in a small world of polynomials, and proves that is enough.",
        fieldnote=f"I ran the Kanpur test on every number up to {sv['N']} and it never disagreed with a sieve. It caught the Carmichael numbers that fool Fermat's test for every base. But for the prime {c3[0]} it needed {c3[3]} multiplications where Miller–Rabin needed {c3[4]}: the species proved it could do without chance, and kept its faster tests.",
        card=[("When", "Preprint 6 August 2002; Annals of Mathematics 2004"),
              ("Where", "Indian Institute of Technology Kanpur"),
              ("What hurt", "Fast tests were randomized, special or conditional"),
              ("The fix", "(X + a)ⁿ = Xⁿ + a modulo (Xʳ − 1, n) for a few a"),
              ("Checked", f"Every n up to {sv['N']} against a sieve")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `AksPrimality.java`.",
    )
