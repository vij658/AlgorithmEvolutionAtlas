"""Era 2, topic 5: the chakravala and Pell's equation. Every number is parsed from Chakravala.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"trace": {61: [], 67: []}, "answers": {}}
    for ln in text.splitlines():
        if m := re.match(r"compose: .* on (\d+) random cases$", ln):
            d["compose"] = int(m.group(1))
        elif m := re.match(r"n92: start (\(.+?\)) ; composed with itself (\(.+?\)) ; divided by 8 (\(.+?\)) ; composed again (\(.+?\))$", ln):
            d["n92"] = m.groups()
        elif m := re.match(r"chakravala (\d+): start (\d+) (\d+) (-?\d+)$", ln):
            d["trace"][int(m.group(1))].append(dict(m=None, a=int(m.group(2)), b=int(m.group(3)), k=int(m.group(4))))
        elif m := re.match(r"chakravala (\d+): m (\d+) -> (\d+) (\d+) (-?\d+)$", ln):
            d["trace"][int(m.group(1))].append(dict(m=int(m.group(2)), a=int(m.group(3)), b=int(m.group(4)), k=int(m.group(5))))
        elif m := re.match(r"answer (\d+): a = (\d+), b = (\d+) ; chakravala (\d+) steps ; stopping at k = (-?\d+) after (\d+) steps? and finishing by (\d+) compositions? ; continued fractions (\d+) convergents$", ln):
            g = m.groups()
            d["answers"][int(g[0])] = dict(a=int(g[1]), b=int(g[2]), steps=int(g[3]), stopk=int(g[4]), stopn=int(g[5]), comp=int(g[6]), cf=int(g[7]))
        elif m := re.match(r"short 61: \(39, 5, -4\) halved (\(.+?\)) ; squared (\(.+?\)) ; cubed (\(.+?\)) ; cube squared (\(.+?\))$", ln):
            d["short"] = m.groups()
        elif m := re.match(r"survey: (\d+) values .* chakravala (\S+) steps on average, at most (\d+) ; stopping early and composing (\S+) operations on average ; continued fractions (\S+) convergents on average, at most (\d+)$", ln):
            g = m.groups()
            d["survey"] = dict(n=int(g[0]), avg=g[1], max=int(g[2]), early=g[3], cfavg=g[4], cfmax=int(g[5]))
        elif m := re.match(r"biggest: N = (\d+) has the largest smallest answer below 1000: a = (\d+) \((\d+) digits\)$", ln):
            d["big"] = dict(N=int(m.group(1)), a=m.group(2), digits=int(m.group(3)))
        elif m := re.match(r"search: for 92, trying b = 1, 2, 3, \.\.\. finds the answer after (\d+) tries ; for 61 it would need (\d+) tries ; for (\d+), (\d+) tries$", ln):
            d["search"] = dict(t92=int(m.group(1)), t61=int(m.group(2)), N=int(m.group(3)), tbig=int(m.group(4)))
    d["checks"] = C.checks(text)
    return d


def cycle_svg(d):
    """The values of k along the chakravala for N = 61: a cycle that comes back on itself."""
    tr = d["trace"][61]

    def draw(t, standalone):
        out = []
        n = len(tr)
        step = 900 / (n - 1)
        y0 = 120
        out.append(C.line(30, y0, 30 + 900, y0, t["rule"], 1))
        for i, s in enumerate(tr):
            x = 30 + i * step
            y = y0 - s["k"] * 16
            if i:
                px = 30 + (i - 1) * step
                py = y0 - tr[i - 1]["k"] * 16
                out.append(C.line(px, py, x, y, t["ink2"], 1.5))
        for i, s in enumerate(tr):
            x = 30 + i * step
            y = y0 - s["k"] * 16
            special = s["k"] in (-4, -1, 1) and i in (1, 6, n - 1)
            out.append(C.circle(x, y, 13, t["red"] if special else t["surface"], t["red"] if special else t["ink"], 1.8))
            out.append(C.text(x, y + 4.5, s["k"], t["paper"] if special else t["ink"], 12, "middle", 700))
            out.append(C.text(x, 228, str(i), t["muted"], 11, "middle"))
        out.append(C.text(30, 252, "step", t["muted"], 11))
        out.append(C.text(30, 22, "k at each step of the chakravala for N = 61, where a² − 61b² = k. Red: k = −4 (step 1), −1 (step 6), 1 (the answer).", t["ink2"], 12.5))
        return C.svg_doc(960, 262, "".join(out), "The values of k along the chakravala for N = 61", t, standalone, 0.6, 960)
    return draw


CK_HTML = """
<div class="board ck-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="ck-n">N <input id="ck-n" type="number" min="2" max="2000" value="61"></label>
      <label><input id="ck-early" type="checkbox"> stop at k = ±1, ±2, ±4 and finish by composition</label>
    </div>
    <div class="controls">
      <button id="ck-next" class="primary" type="button">Next step</button>
      <button id="ck-all" type="button">Finish</button>
      <button id="ck-reset" type="button">Start again</button>
    </div>
    <div class="presets" id="ck-pre"></div>
    <div class="scrollx"><table class="ck-tab"><thead><tr><th>step</th><th>m</th><th>a</th><th>b</th><th>k</th></tr></thead><tbody id="ck-rows"></tbody></table></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The cycle</div>
    <p class="say" id="ck-say" aria-live="polite"></p>
    <p class="tally" id="ck-tally"></p>
  </div>
</div>
"""

CK_CSS = """
.ck-board input[type=number]{width:6em}
.ck-board .controls input[type=checkbox]{width:auto}
.ck-board .controls label{flex-wrap:wrap}
.ck-tab{border-collapse:collapse;font-family:var(--mono);font-size:12.5px;width:100%;margin-top:10px}
.ck-tab th{font-family:var(--sans,inherit);font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);text-align:right;padding:4px 6px;border-bottom:1px solid var(--rule)}
.ck-tab td{text-align:right;padding:4px 6px;border-bottom:1px solid var(--rule);word-break:break-all}
.ck-tab tr.now td{background:var(--wash);font-weight:600}
.ck-tab tr.done td{color:var(--red);font-weight:700}
.ck-board .say{font-size:15px;overflow-wrap:anywhere}
.ck-board .tally{font-family:var(--mono);font-size:12.5px;color:var(--muted)}
"""

CK_JS = r"""
(() => {
  const inp = document.getElementById("ck-n");
  if (!inp) return;
  const rows = document.getElementById("ck-rows"), say = document.getElementById("ck-say"), tally = document.getElementById("ck-tally");
  const pre = document.getElementById("ck-pre");
  [61, 67, 92, 13, 109, 661].forEach(v => { const b = el("button", { type: "button" }, pre, `N = ${v}`); b.addEventListener("click", () => { inp.value = v; reset(); }); });
  const isqrt = n => { let r = BigInt(Math.floor(Math.sqrt(Number(n)))); while (r * r > n) r--; while ((r + 1n) * (r + 1n) <= n) r++; return r; };
  const abs = x => x < 0n ? -x : x;
  const mod = (x, m) => ((x % m) + m) % m;
  let N, a, b, k, r, steps, done, hist;
  function reset() {
    N = BigInt(Math.max(2, Math.min(2000, Math.floor(+inp.value || 2))));
    r = isqrt(N);
    rows.innerHTML = "";
    if (r * r === N) { say.textContent = `${N} is a square, so a² − ${N}b² = 1 has no answer with b > 0. Try another N.`; tally.textContent = ""; done = true; return; }
    a = (N - r * r < (r + 1n) * (r + 1n) - N) ? r : r + 1n; b = 1n; k = a * a - N; steps = 0; done = false; hist = [];
    add(null);
    say.innerHTML = `Start from the square nearest ${N}: ${a}² − ${N} × 1² = <b>${k}</b>. A near-miss, off by ${k}.`;
    check();
  }
  function add(m, cls) {
    rows.querySelectorAll("tr.now").forEach(t => t.classList.remove("now"));
    const tr = el("tr", { class: cls || "now" }, rows);
    [steps, m === null ? "" : m, a, b, k].forEach(v => el("td", {}, tr, String(v)));
  }
  function check() {
    const kk = abs(k);
    if (k === 1n) { finishMsg(`k = 1: ${a}² − ${N} × ${b}² = 1. Done in ${steps} step${steps === 1 ? "" : "s"}.`); return true; }
    if (document.getElementById("ck-early").checked && (kk === 1n || kk === 2n || kk === 4n)) { brahmagupta(); return true; }
    return false;
  }
  function finishMsg(t) { done = true; say.innerHTML = t; rows.lastChild.className = "done"; tally.textContent = `Continued fractions (Lagrange's way) need ${cf()} convergents for this N.`; }
  function cf() {
    const a0 = r; let m = 0n, dd = 1n, aa = a0, p0 = 1n, q0 = 0n, p1 = a0, q1 = 1n, c = 1;
    while (p1 * p1 - N * q1 * q1 !== 1n && c < 2000) { m = dd * aa - m; dd = (N - m * m) / dd; aa = (a0 + m) / dd; const p2 = aa * p1 + p0, q2 = aa * q1 + q0; p0 = p1; q0 = q1; p1 = p2; q1 = q2; c++; }
    return c;
  }
  // Brahmagupta's finish in exact fractions: [num, den] pairs
  function brahmagupta() {
    const g = (x, y) => { x = abs(x); y = abs(y); while (y) [x, y] = [y, x % y]; return x; };
    const Q = (n, d) => { if (d < 0n) { n = -n; d = -d; } const h = g(n, d) || 1n; return [n / h, d / h]; };
    const mul = (x, y) => Q(x[0] * y[0], x[1] * y[1]), plus = (x, y) => Q(x[0] * y[1] + y[0] * x[1], x[1] * y[1]);
    const comp = (x, y) => [plus(mul(x[0], y[0]), mul([N, 1n], mul(x[1], y[1]))), plus(mul(x[0], y[1]), mul(x[1], y[0])), mul(x[2], y[2])];
    const k0 = k, kk = abs(k), half = kk === 4n ? 2n : 1n;
    const h = [Q(a, half), Q(b, half), Q(k, half * half)];
    let t = h, n = 0;
    const log = [];
    if (kk === 2n) { t = comp(h, h); t = [Q(t[0][0], t[0][1] * 2n), Q(t[1][0], t[1][1] * 2n), Q(t[2][0], t[2][1] * 4n)]; n++; log.push("compose with itself, divide by 2"); }
    else if (kk === 4n) log.push(`halve: (${a}/2, ${b}/2, ${k / 4n})`);
    while (t[0][1] !== 1n || t[1][1] !== 1n) { t = comp(t, h); n++; log.push("compose with the halved triple"); }
    if (t[2][0] === -1n) { t = comp(t, t); n++; log.push("compose with itself (k = −1 becomes 1)"); }
    a = t[0][0]; b = t[1][0]; k = 1n;
    add("✓", "done");
    finishMsg(`k = ${k0} is one Brahmagupta can finish: ${log.join("; ")}. ${n} composition${n === 1 ? "" : "s"}, after ${steps} step${steps === 1 ? "" : "s"}: <b>${a}² − ${N} × ${b}² = 1</b>.`);
  }
  function step() {
    if (done) return false;
    const kk = abs(k);
    let best = null, gap = null, cands = [];
    const lo = r - 2n * kk > 1n ? r - 2n * kk : 1n;
    for (let m = lo; m <= r + 2n * kk + 1n; m++) {
      if (mod(a + b * m, kk) !== 0n) continue;
      const gp = abs(m * m - N);
      cands.push(m);
      if (gap === null || gp < gap) { best = m; gap = gp; }
    }
    const m = best;
    const na = (a * m + N * b) / kk, nb = (a + b * m) / kk, nk = (m * m - N) / k;
    hist.push([a, b, k]);
    a = na; b = nb; k = nk; steps++;
    add(m);
    const near = cands.filter(x => abs(x - r) <= 2n * kk).slice(0, 6).join(", ");
    say.innerHTML = `Choose m so that ${kk} divides a + b·m (allowed near √${N}: ${near}…) and m² − ${N} is smallest: <b>m = ${m}</b>. Compose with (m, 1, m² − ${N}) and divide by ${kk}: new k = (${m}² − ${N}) / ${hist[hist.length - 1][2]} = <b>${k}</b>.`;
    check();
    return true;
  }
  document.getElementById("ck-next").addEventListener("click", step);
  document.getElementById("ck-all").addEventListener("click", () => { let g = 0; while (step() && g++ < 400); });
  document.getElementById("ck-reset").addEventListener("click", reset);
  inp.addEventListener("change", reset);
  document.getElementById("ck-early").addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 660, "How the chakravala combined older ideas, and where the equation went next")
    W, H = 210, 86
    nodes = {
        "sq": (20, 20, "Square roots as fractions", "", "the √2 tablet, Era 1 topic 4", "ink"),
        "kut": (395, 20, "The pulverizer", "", "Euclid's divisions, Era 1 topic 7", "ink"),
        "neg": (770, 20, "Zero and debts", "", "Brahmagupta, topic 4", "ink"),
        "bha": (210, 170, "Composition", "⊕ multiply two near-misses", "Brahmagupta, 628", "red"),
        "chk": (580, 170, "The chakravala", "⊕ a cycle that shrinks the error", "Jayadeva; Bhaskara II, 1150", "red"),
        "fer": (20, 340, "Fermat's challenge", "N = 61, found again in Europe", "1657; Brouncker", "ink"),
        "lag": (395, 340, "Lagrange's proof", "⊕ continued fractions always end", "1766 or 1767", "ink"),
        "hal": (770, 340, "Quantum algorithm", "⊕ polynomial time, if quantum", "Hallgren, 2007", "blue"),
        "fac": (770, 490, "Factoring reduces to it", "and a key exchange built on its cousin", "Buchmann–Williams", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("sq", "bha", ports=("bottom", "top:0.2"))
    D.edge("kut", "chk", ports=("bottom", "top:0.3"))
    D.edge("neg", "chk", ports=("bottom", "top:0.8"))
    D.edge("bha", "chk", ports=("right", "left"))
    D.edge("chk", "fer", ports=("bottom:0.1", "top:0.8"), dashed=True)
    D.edge("chk", "lag", ports=("bottom:0.3", "top:0.6"))
    D.edge("chk", "hal", ports=("bottom:0.9", "top:0.3"))
    D.edge("hal", "fac", ports=("bottom", "top"))
    D.text(20, 640, "Dashed: Europe met the equation again five centuries later; no transmission is documented.", "caption")
    return D


def chain(d):
    s61 = d["answers"][61]
    sv, bg, se = d["survey"], d["big"], d["search"]
    steps = [
        (f"Whole-number answers can be enormous: for N = 61, b = {s61['b']:,}, so searching is hopeless",
         "Composition: multiply two near-misses into a new one, and divide out the error", "Brahmagupta, 628"),
        ("Composition finishes only once a near-miss is off by 1, 2 or 4",
         "The chakravala: choose m to keep the error small, compose, divide, repeat", "Jayadeva; Bhaskara II, 1150"),
        ("Does the cycle always end? Bhaskara II probably had no proof",
         "Continued fractions: Lagrange proves that an answer always exists and is reached", "Lagrange, 1766 or 1767"),
        (f"The answers themselves grow fast: {bg['digits']} digits for N = {bg['N']}",
         "A quantum algorithm solves the equation in polynomial time; factoring reduces to it", "Hallgren, 2007"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a near-miss to a quantum algorithm")
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
    a61, a67 = d["answers"][61], d["answers"][67]
    n92, sh, sv, bg, se = d["n92"], d["short"], d["survey"], d["big"], d["search"]
    tr = d["trace"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A solution of a² − Nb² = 1 makes a/b a superb fraction for √N, the problem of the √2 tablet (Era 1, topic 4). The chakravala's divisibility step is the pulverizer, Euclid's divisions run backwards (topic 7), and its errors are as often debts as fortunes (topic 4). Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the two Indian steps. Blue: where the equation stands today, as a problem for quantum computers."),
        ]),
        dict(id="cycle", eyebrow="Try it", title="Run the cycle", toc="Try it", blocks=[
            dict(type="p", text="Choose N and press **Next step**. Each row is a near-miss a² − Nb² = k. The method picks m so that k divides a + b·m with m² − N as small as possible, composes, and divides; k jumps about and comes back to 1. Tick the box to stop as soon as k is ±1, ±2 or ±4 and let Brahmagupta's compositions finish, as Dutta's account of N = 61 does."),
            dict(type="widget", html=CK_HTML, js=CK_JS, css=CK_CSS,
                 fallback=dict(type="svg", name="cycle", draw=cycle_svg(d), alt="The values of k along the chakravala for N = 61", width=960),
                 note="In the interactive edition you can run the chakravala for any N up to 2,000, with exact whole numbers."),
            dict(type="table", head=["Step", "m", "a", "b", "k"], num=[0, 1, 2, 3, 4],
                 rows=[[str(i), "" if s["m"] is None else str(s["m"]), f"{s['a']:,}", f"{s['b']:,}", str(s["k"])] for i, s in enumerate(tr[61])]),
            dict(type="p", text=f"For N = 61 the plain cycle takes **{a61['steps']} steps** to reach k = 1, and the values of k run out to −1 at step 6 and then back again in reverse order. But step 1 already gives 39² − 61 × 5² = −4, and from there Brahmagupta's compositions finish the job: halve to {sh[0]}, square it to {sh[1]}, multiply again to {sh[2]}, and square that: {sh[3]}. That is **{a61['comp']} compositions** after {a61['stopn']} step."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="compose", eyebrow="How it works", title="Composition, then the cycle", toc="How it works", blocks=[
            dict(type="p", text="**Composition.** If a² − Nb² = k and c² − Nd² = l, then (ac + Nbd)² − N(ad + bc)² = kl. Two near-misses multiply into a new near-miss, with the errors multiplied. Composing a near-miss with itself gives error k², which divides out, leaving an exact answer in fractions."),
            dict(type="p", text=f"Brahmagupta's own example, N = 92, in two compositions: start {n92[0]}; composed with itself {n92[1]}; divided by 8, {n92[2]}, an exact answer with a fraction; composed with itself again, **{n92[3]}**: 1151² − 92 × 120² = 1. Dutta quotes his boast: \"One who can solve it within a year [is truly a] mathematician.\" A plain search for N = 92 would need {se['t92']} tries; for N = 61, {se['t61']:,}."),
            dict(type="p", text="**The cycle.** From a triple (a, b, k), choose m > 0 so that k divides a + bm and |m² − N| is smallest. Compose with (m, 1, m² − N) and divide by |k|: a′ = (am + Nb)/|k|, b′ = (a + bm)/|k|, k′ = (m² − N)/k. The divisibility condition is a small pulverizer problem, and the choice of m keeps the error small. The cycle ends when k = 1."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Do not search for the answer; improve a near-miss. Composition turns any near-miss into a better one, and the cycle keeps the error small while the numbers grow, until the error is 1."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Who closed the cycle?", toc="The evidence", blocks=[
            dict(type="p", text="Brahmagupta (598–670) gave composition in the *Brahmasphutasiddhanta* of 628 (**documented**); it works only once a near-miss with error ±1, ±2 or ±4 is known. The earliest known account of the full cycle is Jayadeva's, whose verses survive only as quotations in Udayadivakara's *Sundari* of 1073; his own date is an estimate, about 1000 or earlier (**conjecture**). Bhaskara II (1114–1185) set out a variant in his *Bijaganita* of 1150, with the examples N = 61 and N = 67. MacTutor thinks he probably had no proof that the cycle always ends (**conjecture**)."),
            dict(type="p", text="Who first solved N = 61 is **disputed** even inside MacTutor: its Brahmagupta biography credits Brahmagupta, while its Pell's equation page, Dutta and Waldschmidt credit Bhaskara II. In 1657 Fermat set N = 61 as a challenge to European mathematicians; Brouncker answered with what is essentially continued fractions; Euler named the equation after John Pell, probably confusing him with Brouncker. Lagrange's complete theory is dated 1766 or 1767 (**disputed**)."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The cycle against continued fractions", toc="Measured", blocks=[
            dict(type="table", head=["N", "Smallest answer a", "b", "Chakravala steps", "Early stop + compositions", "Continued fraction convergents"], num=[0, 3, 4, 5],
                 rows=[[str(n), f"{x['a']:,}", f"{x['b']:,}", str(x["steps"]), f"{x['stopn']} + {x['comp']} (stop at k = {x['stopk']})", str(x["cf"])] for n, x in [(61, a61), (67, a67)]]),
            dict(type="p", text=f"Selenius counted 22 convergents for N = 61 by the European method; the program gets the same, {a61['cf']}. Over all {sv['n']} values of N from 2 to 1,000 that are not squares, both methods found the same smallest answer every time. The chakravala took **{sv['avg']} steps** on average (at most {sv['max']}), stopping early and composing {sv['early']} operations, and continued fractions **{sv['cfavg']} convergents** (at most {sv['cfmax']}). The chakravala never needed more steps. Selenius showed that it corresponds to a \"half-regular best approximating algorithm of minimal length\", not to Lagrange's regular continued fraction."),
            dict(type="p", text=f"The answers can be huge. Below 1,000, the largest smallest answer belongs to N = {bg['N']}: a = {bg['a']}, **{bg['digits']} digits**. A search for it would need {se['tbig']:,} tries."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A problem for quantum computers", toc="Full circle", blocks=[
            dict(type="p", text="Because the smallest answer can have far more digits than N itself, even writing it down can take a long time. In 2007 Sean Hallgren published \"Polynomial-time quantum algorithms for Pell's equation and the principal ideal problem\" in the *Journal of the ACM*. His abstract notes that \"factoring integers reduces to finding integer solutions of Pell's equation\", while the reverse reduction is not known, and that a related problem, at least as hard, is the one-way function of the Buchmann–Williams key exchange, which a quantum computer would therefore break."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"An equation that Brahmagupta set as a test of mathematicians in 628, and Bhaskara II solved for N = 61 with a cycle of a few steps, is now classed with factoring: at least as hard, and one of the first problems shown to fall to a quantum computer. The cycle that took {a61['steps']} steps for 61 needs {sv['max']} for the hardest N below 1,000, and the answers grow far faster than the steps."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Check Brahmagupta's answer for N = 92.", "1151² = 1,324,801 and 92 × 120² = 1,324,800. The difference is 1."),
            ("Why does a solution of a² − Nb² = 1 give a good fraction for √N?", "Divide by b²: (a/b)² − N = 1/b². When b is large, (a/b)² is extremely close to N."),
            ("Compose (3, 1, −1) with itself for N = 10. What do you get?", "(3·3 + 10·1·1, 3·1 + 1·3, 1) = (19, 6, 1): 19² − 10 × 6² = 361 − 360 = 1."),
            (f"For N = 61, the first step gives k = −4. Why stop there?", "Brahmagupta's compositions can finish from an error of ±4: halve the triple, compose, and square. Three compositions instead of twelve more steps."),
            ("Why can't the method work when N is a square?", "Then a² − Nb² = (a − √N b)(a + √N b) is a product of two whole numbers equal to 1, so b = 0: there is no real answer."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Brahmagupta and Bhaskara in English, 1817", text="Colebrooke's translation of the algebra of Brahmagupta (628) and Bhaskara II (1150), including the *Bijaganita*.",
                 draw=C.draw_book, link="https://archive.org/details/algebrawitharith00brahuoft/page/n5/mode/2up", link_text="Internet Archive scan",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("scholar", "Polynomial-time quantum algorithms for Pell's equation and the principal ideal problem", "Sean Hallgren, Journal of the ACM 54(1), 2007", "https://pure.psu.edu/en/publications/polynomial-time-quantum-algorithms-for-pells-equation-and-the-pri-2/", "Factoring reduces to Pell's equation; a quantum computer solves it in polynomial time"),
        ]),
        C.prove_it_section(ctx, "Chakravala", d["checks"],
                           "Brahmagupta's composition on 20,000 random cases, every chakravala triple along the way, N = 92 and N = 61 by composition, and the chakravala against continued fractions for every N up to 1,000.",
                           ["static T compose(", "static BigInteger[] chakravala(long N, boolean early)"]),
    ]
    return dict(
        title="The Chakravala and Pell's Equation", date="628–1150 CE",
        description="Era 2, topic 5 of The Algorithm Evolution Atlas: Brahmagupta's composition and the chakravala cycle for a² − Nb² = 1, run step by step, against Lagrange's continued fractions.",
        lede="For N = 61 the smallest whole-number answer to a² − 61b² = 1 has a ten-digit a. Indian mathematicians did not search: they improved near-misses, in a cycle that always comes back to an error of 1.",
        fieldnote="Guessing is hopeless here. Brahmagupta noticed that two near-misses can be multiplied into a new one; later mathematicians closed the loop into a cycle. Europeans met the same equation five centuries after Bhaskara II, and named it after the wrong man.",
        card=[("When", "Brahmagupta, 628; Jayadeva (quoted 1073); Bhaskara II, 1150 (**documented**)"),
              ("Where", "India: Bhillamala, Ujjain"),
              ("What hurt", "Whole-number answers to a² − Nb² = 1 can be enormous"),
              ("The fix", "Compose near-misses; cycle until the error is 1"),
              ("Cost", f"{sv['avg']} steps on average for N up to 1,000, against {sv['cfavg']} convergents")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Chakravala.java`.",
    )
