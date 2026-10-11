"""Era 2, topic 3: the Chinese remainder problem. Every number is parsed from ChineseRemainder.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"dayan": [], "qin_steps": [], "scale": []}
    for ln in text.splitlines():
        if m := re.match(r"sunzi: multipliers (\d+) (\d+) (\d+) ; (.+?) = (\d+) ; cast out (\d+) -> (\d+) ; search needs (\d+) tries$", ln):
            g = m.groups()
            d["sunzi"] = dict(mult=[int(g[0]), int(g[1]), int(g[2])], terms=g[3], sum=int(g[4]), out=int(g[5]), ans=int(g[6]), tries=int(g[7]))
        elif m := re.match(r"dayan (\d+) mod (\d+): reduce to (\d+) ; k = (\d+) ; multiplier (\d+) x (\d+) = (\d+) ; (\d+) steps$", ln):
            g = [int(x) for x in m.groups()]
            d["dayan"].append(dict(others=g[0], mod=g[1], red=g[2], k=g[3], mult=g[6], steps=g[7]))
        elif m := re.match(r"qin step (\d+): (lower by upper|upper by lower): quotient (\d+) ; board (\d+) (\d+) / (\d+) (\d+)$", ln):
            g = m.groups()
            d["qin_steps"].append(dict(how=g[1], q=int(g[2]), ul=int(g[3]), ur=int(g[4]), ll=int(g[5]), lr=int(g[6])))
        elif m := re.match(r"qin answer: 377873 x (\d+) = (\d+) = (\d+) x 499067 \+ 1 ; (\d+) divisions$", ln):
            g = [int(x) for x in m.groups()]
            d["qin"] = dict(k=g[0], prod=g[1], quot=g[2], div=g[3])
        elif m := re.match(r"dayan random: (\d+) random divisors below 10\^9, same answer as extended Euclid every time ; (\S+) divisions on average, at most (\d+)$", ln):
            d["random"] = dict(n=int(m.group(1)), avg=m.group(2), max=int(m.group(3)))
        elif m := re.match(r"qin cycles: leaves 1 by 19, 14 by 17, 1 by 12 -> (\d+) \(repeats every (\d+)\)$", ln):
            d["cycles"] = dict(ans=int(m.group(1)), every=int(m.group(2)))
        elif m := re.match(r"shared: leaves 5 by 12 and 11 by 18 -> divisors 4 and 9 -> (\d+), every (\d+) ;", ln):
            d["shared"] = dict(ans=int(m.group(1)), every=int(m.group(2)))
        elif m := re.match(r"shared random: (\d+) systems", ln):
            d["shared_n"] = int(m.group(1))
        elif m := re.match(r"scale (\d+) cycles: repeat every (\d+) ; answer (\d+) ; search needs (\d+) tries ; the rule needs (\d+) divisions and (\d+) multiplications$", ln):
            g = [int(x) for x in m.groups()]
            d["scale"].append(dict(k=g[0], every=g[1], ans=g[2], tries=g[3], div=g[4], mul=g[5]))
        elif m := re.match(r"rsa: 2048-bit key, (\d+) messages decrypted both ways ; plain: (\d+) multiplications of 2048-bit numbers ; by remainders: (\d+) of 1024-bit numbers ; word products (\d+) against (\d+), (\S+) times fewer$", ln):
            g = m.groups()
            d["rsa"] = dict(n=int(g[0]), plain=int(g[1]), crt=int(g[2]), wp=int(g[3]), wc=int(g[4]), ratio=g[5])
    d["checks"] = C.checks(text)
    return d


def pebbles_svg(d):
    """Sunzi's answer, 23 pebbles, counted off in threes, fives and sevens."""
    n = d["sunzi"]["ans"]

    def draw(t, standalone):
        out = []
        for col, (k, left) in enumerate([(3, n % 3), (5, n % 5), (7, n % 7)]):
            x0 = 20 + col * 320
            out.append(C.text(x0, 26, f"In {['threes', 'fives', 'sevens'][col]}: {n // k} groups, {left} left", t["ink"], 14, "start", 700))
            for i in range(n):
                g, j = divmod(i, k)
                full = i < n - left
                x = x0 + j * 26 + 12
                y = 50 + g * 26 + 12
                out.append(C.circle(x, y, 9, t["surface"] if full else t["red"], t["ink2"] if full else t["red"], 1.5))
        out.append(C.text(20, 290, f"{n} pebbles: 2 left in threes, 3 in fives, 2 in sevens. Red: what is left over.", t["muted"], 12.5))
        return C.svg_doc(960, 302, "".join(out), f"Sunzi's answer, {n} things, counted in threes, fives and sevens", t, standalone, 0.6, 960)
    return draw


CR_HTML = """
<div class="board cr-board">
  <div style="min-width:0">
    <div class="controls cr-in" id="cr-in"></div>
    <div class="controls">
      <button id="cr-solve" class="primary" type="button">Solve by Sunzi's rule</button>
      <button id="cr-search" type="button">Search instead</button>
      <button id="cr-reset" type="button">Sunzi's problem</button>
    </div>
    <div class="cr-tabs" id="cr-tabs" role="group" aria-label="Count the answer off in groups"></div>
    <div class="cr-peb" id="cr-peb" aria-label="The answer, counted off in groups"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The rule, step by step</div>
    <div class="cr-steps" id="cr-steps" aria-live="polite"></div>
  </div>
</div>
"""

CR_CSS = """
.cr-in label{font-size:13px}
.cr-in input{width:4.2em}
.cr-tabs{display:flex;flex-wrap:wrap;gap:6px;margin:4px 0 10px}
.cr-tabs button{font-weight:400;font-size:13px;padding:3px 9px;border-width:1px;border-color:var(--axis)}
.cr-tabs button.on{background:var(--ink);color:var(--paper)}
.cr-peb{display:flex;flex-direction:column;gap:4px;max-height:380px;overflow:auto;padding:8px;background:var(--wash);border:1px solid var(--rule)}
.cr-peb .row{display:flex;gap:4px;flex-wrap:nowrap}
.cr-peb i{width:14px;height:14px;border-radius:50%;border:1.5px solid var(--ink-2);background:var(--surface);flex:none}
.cr-peb i.left{background:var(--red);border-color:var(--red)}
.cr-peb .more{font-size:12px;color:var(--muted)}
.cr-steps{font-size:14px}
.cr-steps p{margin:0 0 8px}
.cr-steps .mono{font-family:var(--mono);font-size:13px}
.cr-steps .dy{font-family:var(--mono);font-size:12px;color:var(--ink-2);margin:2px 0 8px 10px}
"""

CR_JS = r"""
(() => {
  const box = document.getElementById("cr-in");
  if (!box) return;
  const SUNZI = { m: [3, 5, 7], r: [2, 3, 2] };
  const ins = [];
  for (let i = 0; i < 3; i++) {
    const lab = el("label", {}, box);
    lab.append("leaves ");
    const r = el("input", { type: "number", min: 0, value: SUNZI.r[i], "aria-label": `remainder ${i + 1}` }, lab);
    lab.append(" by ");
    const m = el("input", { type: "number", min: 2, max: 400, value: SUNZI.m[i], "aria-label": `divisor ${i + 1}` }, lab);
    ins.push([r, m]);
  }
  const gcd = (a, b) => b ? gcd(b, a % b) : Math.abs(a);
  const steps = document.getElementById("cr-steps");
  let group = 0, answer = null;
  // Qin Jiushao's dayan rule: k with a k = 1 (mod m)
  function dayan(a, m) {
    let ul = 1, ur = a % m, ll = 0, lr = m;
    const log = [`board ${ul} ${ur} / ${ll} ${lr}`];
    if (ur === 1) return [1, log];
    for (let guard = 0; guard < 200; guard++) {
      let q = Math.floor(lr / ur); lr -= q * ur; ll += q * ul;
      log.push(`lower ÷ upper, quotient ${q}: ${ul} ${ur} / ${ll} ${lr}`);
      q = lr === 1 ? ur - 1 : Math.floor(ur / lr); ur -= q * lr; ul += q * ll;
      log.push(`upper ÷ lower, quotient ${q}: ${ul} ${ur} / ${ll} ${lr}`);
      if (ur === 1) return [ul % m, log];
    }
    return [null, log];
  }
  function read() {
    return ins.map(([r, m]) => [Math.max(0, Math.floor(+r.value || 0)), Math.max(2, Math.min(400, Math.floor(+m.value || 2)))]);
  }
  function pebbles() {
    const peb = document.getElementById("cr-peb");
    peb.innerHTML = "";
    if (answer === null) return;
    const k = read()[group][1], n = answer, left = n % k, show = Math.min(n, 600);
    let row;
    for (let i = 0; i < show; i++) {
      if (i % k === 0) row = el("div", { class: "row" }, peb);
      el("i", { class: i >= n - left ? "left" : "" }, row);
    }
    if (n > show) el("div", { class: "more" }, peb, `… and ${fmt(n - show)} more`);
    el("div", { class: "more" }, peb, `${fmt(n)} counted in ${k}s: ${fmt(Math.floor(n / k))} full rows, ${left} left (red)`);
  }
  function tabs() {
    const t = document.getElementById("cr-tabs");
    t.innerHTML = "";
    read().forEach(([, m], i) => {
      const b = el("button", { type: "button", class: i === group ? "on" : "" }, t, `count in ${m}s`);
      b.addEventListener("click", () => { group = i; tabs(); pebbles(); });
    });
  }
  function solve() {
    const v = read(), m = v.map(x => x[1]), r = v.map((x, i) => x[0] % m[i]);
    steps.innerHTML = "";
    for (let i = 0; i < 3; i++) for (let j = i + 1; j < 3; j++) if (gcd(m[i], m[j]) !== 1) {
      el("p", {}, steps, `${m[i]} and ${m[j]} share the factor ${gcd(m[i], m[j])}. Sunzi's rule needs divisors with no common factor; Qin Jiushao first replaced such divisors with coprime ones. Try Search instead.`);
      answer = null; pebbles(); return;
    }
    const prod = m[0] * m[1] * m[2];
    let total = 0;
    const terms = [];
    for (let i = 0; i < 3; i++) {
      const others = prod / m[i];
      const [k, log] = dayan(others % m[i], m[i]);
      const mult = others * k;
      const p = el("p", {}, steps);
      p.innerHTML = `Divisor <b>${m[i]}</b>: the other two multiply to ${fmt(others)}, which leaves ${others % m[i]}. The dayan board finds k = <b>${k}</b>, so the ready-made number is ${fmt(others)} × ${k} = <b>${fmt(mult)}</b>: it leaves 1 by ${m[i]} and nothing by the others.`;
      const dy = el("div", { class: "dy" }, steps);
      dy.textContent = log.join(" → ");
      total += r[i] * mult;
      terms.push(`${r[i]} × ${fmt(mult)}`);
    }
    answer = total % prod;
    const p = el("p", { class: "mono" }, steps);
    p.innerHTML = `${terms.join(" + ")} = ${fmt(total)}<br>cast out ${fmt(prod)} as often as possible: <b>${fmt(answer)}</b>`;
    tabs(); pebbles();
  }
  function search() {
    const v = read(), m = v.map(x => x[1]), r = v.map((x, i) => x[0] % m[i]);
    let l = 1;
    for (const x of m) l = l / gcd(l, x) * x;
    steps.innerHTML = "";
    let tries = 0, found = null;
    for (let x = 0; x < l && x < 2e6; x++) { tries++; if (x % m[0] === r[0] && x % m[1] === r[1] && x % m[2] === r[2]) { found = x; break; } }
    answer = found;
    el("p", {}, steps, found === null ? `No number below ${fmt(l)} fits: the conditions contradict each other.` :
      `Searching 0, 1, 2, … finds ${fmt(found)} after ${fmt(tries)} tries. The pattern repeats every ${fmt(l)}.`);
    tabs(); pebbles();
  }
  document.getElementById("cr-solve").addEventListener("click", solve);
  document.getElementById("cr-search").addEventListener("click", search);
  document.getElementById("cr-reset").addEventListener("click", () => { ins.forEach(([r, m], i) => { r.value = SUNZI.r[i]; m.value = SUNZI.m[i]; }); group = 0; solve(); });
  ins.forEach(([r, m]) => [r, m].forEach(x => x.addEventListener("change", () => { group = 0; tabs(); })));
  solve();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 650, "How the remainder problem combined older ideas, from Sunzi to RSA")
    W, H = 210, 86
    nodes = {
        "cyc": (20, 20, "Calendar cycles", "", "60-day cycle, months, years", "ink"),
        "euc": (395, 20, "Euclid's algorithm", "", "Era 1, topic 7", "ink"),
        "sun": (20, 170, "Sunzi's rule", "⊕ ready-made multipliers 70, 21, 15", "3rd–5th century CE", "red"),
        "qin": (395, 170, "Qin's dayan rule", "⊕ find any multiplier on the board", "1247", "red"),
        "ary": (770, 170, "Aryabhata's kuttaka", "the pulverizer, found separately", "India, c. 500", "ink"),
        "gau": (395, 330, "Gauss", "the theorem, in congruences", "Disquisitiones, 1801", "ink"),
        "rsa": (395, 480, "RSA by remainders", "⊕ decrypt mod p and mod q, recombine", "PKCS #1, RFC 8017", "blue"),
        "fib": (20, 330, "Fibonacci", "solved such puzzles case by case", "Liber Abaci, 1202", "ink"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("cyc", "sun", ports=("bottom", "top"), dashed=True)
    D.edge("cyc", "qin", ports=("right:0.8", "left:0.2"))
    D.edge("euc", "qin", ports=("bottom", "top"))
    D.edge("sun", "qin", ports=("right", "left"))
    D.edge("euc", "ary", ports=("right", "top"), dashed=True)
    D.edge("qin", "gau", ports=("bottom", "top"), dashed=True)
    D.edge("sun", "fib", ports=("bottom", "top"), dashed=True)
    D.edge("gau", "rsa", ports=("bottom", "top"))
    D.text(20, 620, "Dashed: a link of ideas without a documented line of transmission. Sunzi's link to calendars is a conjecture.", "caption")
    return D


def chain(d):
    s, sc, rsa = d["sunzi"], d["scale"], d["rsa"]
    big = sc[-1]
    steps = [
        (f"Find a number from its remainders: searching takes {s['tries']} tries even for 3, 5 and 7",
         f"Ready-made multipliers: {s['mult'][0]}, {s['mult'][1]}, {s['mult'][2]}; multiply, add, cast out 105", "Sunzi, 3rd–5th century"),
        ("Those multipliers only work for 3, 5 and 7; every new set of cycles needs new ones",
         "The dayan rule finds any multiplier on the board: Euclid's divisions with a running record", "Qin Jiushao, 1247"),
        ("Cycles can share factors, like 12 and 18, and then the multipliers do not exist",
         "Replace them with coprime divisors that give the same answer, or show that none exists", "Qin Jiushao, 1247"),
        (f"Search grows with the product of the cycles: {len(str(big['every']))}-digit repeats for {big['k']} cycles near 1,000",
         f"The rule grows with the digits instead: {big['div']} divisions for {big['k']} cycles", "the program's measurement"),
        ("RSA decryption raises a 600-digit number to a 600-digit power",
         f"Do it modulo each prime and recombine: {rsa['ratio']} times fewer word products", "PKCS #1 (RFC 8017)"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from Sunzi's puzzle to RSA")
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
    s, q, rnd, cyc, sh, rsa = d["sunzi"], d["qin"], d["random"], d["cycles"], d["shared"], d["rsa"]
    dy = d["dayan"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Sunzi's rule needs a few ready-made numbers; finding them for any divisors needs Euclid's chain of divisions (Era 1, topic 7) with a running record kept on the counting board. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the two Chinese steps. Blue: the same rule inside every RSA private-key operation that follows PKCS #1."),
        ]),
        dict(id="rule", eyebrow="Try it", title="Count in threes, fives and sevens", toc="Try it", blocks=[
            dict(type="p", text="Set three remainders and three divisors. **Solve by Sunzi's rule** builds the ready-made numbers with Qin's dayan board, multiplies, adds and casts out the product; **Search instead** counts up from zero. Then count the answer off in groups and watch the leftovers."),
            dict(type="widget", html=CR_HTML, js=CR_JS, css=CR_CSS,
                 fallback=dict(type="svg", name="pebbles", draw=pebbles_svg(d), alt="Sunzi's answer counted in threes, fives and sevens", width=960),
                 note="In the interactive edition you can choose your own divisors and remainders and watch the dayan board find the multipliers."),
            dict(type="p", text=f"The problem, in MacTutor's translation: \"Suppose we have an unknown number of objects. When counted in threes, 2 are left over, when counted in fives, 3 are left over, and when counted in sevens, 2 are left over. How many objects are there?\" Sunzi's working: {s['terms']} = **{s['sum']}**; take away {s['out']} and **{s['ans']}** remains. The program checked that every one of the 105 triples of remainders has its own answer below 105, so the rule never fails and never gives two answers."),
            dict(type="callout", kind="key", label="Key idea",
                 text=f"Each ready-made number does one job and stays out of the others' way: {s['mult'][0]} leaves 1 by 3 and nothing by 5 or 7; {s['mult'][1]} leaves 1 by 5 and nothing by 3 or 7; {s['mult'][2]} leaves 1 by 7 and nothing by 3 or 5. Multiply each by the remainder you want, and the three jobs add up without interfering."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="dayan", eyebrow="How it works", title="Finding one: the dayan board", toc="The dayan rule", blocks=[
            dict(type="p", text="To build a ready-made number for the divisor *m*, multiply the other divisors to get *M* and find *k* so that *M* × *k* leaves 1 by *m*. Qin Jiushao's *dayan qiuyi* rule (\"finding one\") does it on four places of the counting board: *M* (reduced by *m*) at the upper right, *m* at the lower right, 1 at the upper left. Divide the lower number by the upper and the upper by the lower in turn, each time adding the quotient times the left-hand number to the other left-hand place, until the upper right is 1. The upper left is *k*."),
            dict(type="table", head=["Divisor", "Other divisors multiplied", "Reduced", "k", "Ready-made number"], num=[0, 1, 2, 3, 4],
                 rows=[[str(x["mod"]), str(x["others"]), str(x["red"]), str(x["k"]), str(x["mult"])] for x in dy]),
            dict(type="p", text=f"Qin's own book has far larger numbers. One calendar problem needs *k* with 377,873 × *k* leaving 1 by 499,067. The board takes {q['div']} divisions:"),
            dict(type="table", head=["Step", "Divide", "Quotient", "Upper left", "Upper right", "Lower left", "Lower right"], num=[0, 2, 3, 4, 5, 6],
                 rows=[[str(i + 1), x["how"], f"{x['q']:,}", f"{x['ul']:,}", f"{x['ur']:,}", f"{x['ll']:,}", f"{x['lr']:,}"] for i, x in enumerate(d["qin_steps"])]),
            dict(type="p", text=f"The upper left ends at **{q['k']:,}**: 377,873 × {q['k']:,} = {q['prod']:,} = {q['quot']:,} × 499,067 + 1. Shen Kangsheng's history prints the same answer for this problem. On {rnd['n']:,} random divisors below a billion, the board gave the same answer as the modern extended Euclidean algorithm every time, in {rnd['avg']} divisions on average and never more than {rnd['max']}."),
            dict(type="p", text=f"Two more of Qin's ideas. In his first example, three cycles of 19, 17 and 12 with remainders 1, 14 and 1 give **{cyc['ans']:,}**, repeating every {cyc['every']:,}. And when divisors share factors, he replaced them with coprime ones that give the same answer: 5 left by 12 and 11 left by 18 becomes a problem in 4 and 9, answer **{sh['ans']}**, repeating every {sh['every']}. The program checked this replacement against search on {d['shared_n']:,} systems, including those with no answer at all."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A puzzle in a primer, a method in a treatise", toc="The evidence", blocks=[
            dict(type="p", text="The *Sunzi Suanjing* is hard to date. MacTutor lists estimates from about 250 BCE to after 280 CE and notes that, as a whole, the text \"cannot be older than 473 AD\"; other sources give the 3rd, 4th or 5th century (**disputed**). The book was probably compiled from older material of different dates."),
            dict(type="p", text="Qin Jiushao (1202–1261) wrote the *Shushu jiuzhang* in 1247 (**documented**). He said he learned the method from calendar experts at the Board of Astronomy, who used it without understanding it. Chinese calendar-makers needed such congruences to find a *shangyuan*, a starting moment when the 60-day cycle, the winter solstice and the new moon coincide; Shen Kangsheng traces this to the Jingchu calendar of 237 CE. That Sunzi's own puzzle came from calendar work is a **conjecture**: no source opened here says so."),
            dict(type="p", text="In India, Aryabhata's 5th-century work contains instances of the same theorem. In 1874 Mathiesen pointed out that Sunzi's method matches Gauss's, which is why Western books call it the *Chinese* remainder theorem (one source). Cheng Dawei set the multipliers 70, 21 and 15 to verse in 1592."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Search against the rule", toc="Measured", blocks=[
            dict(type="table", head=["Cycles (primes near 1,000)", "Repeats every", "Answer", "Search: tries", "Rule: divisions"], num=[0, 2, 3, 4],
                 rows=[[str(x["k"]), f"{x['every']:,}", f"{x['ans']:,}", f"{x['tries']:,}", str(x["div"])] for x in d["scale"]]),
            dict(type="p", text="Searching has to walk up to the answer, which can be anywhere below the product of the cycles, so the work multiplies with every cycle added. The rule's work, a few divisions per cycle, only adds."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Decrypting by remainders", toc="Full circle", blocks=[
            dict(type="p", text="An RSA private key works modulo *n* = *p* × *q*, a number of about 600 digits. PKCS #1, the RSA standard (RFC 8017, 2016), stores the key a second way, as *p*, *q*, *dP*, *dQ* and *qInv*, so that decryption can work modulo *p* and modulo *q* separately: `m1 = c^dP mod p`, `m2 = c^dQ mod q`, `h = (m1 − m2) × qInv mod p`, `m = m2 + q × h`. The last two steps are Sunzi's rule for two divisors."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program made a 2048-bit key and decrypted {rsa['n']} messages both ways. Plain decryption took {rsa['plain']:,} multiplications of 2048-bit numbers; by remainders, {rsa['crt']:,} multiplications of 1024-bit numbers. Counting 64-bit word products, that is {rsa['wp']:,} against {rsa['wc']:,}: **{rsa['ratio']} times fewer**. A puzzle about counting things in threes, fives and sevens is inside every RSA decryption that follows the standard."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why is 70 the ready-made number for 3, and not 35?",
             "35 is divisible by 5 and 7 but leaves 2 by 3. Doubling it gives 70, which leaves 1 by 3 and is still divisible by 5 and 7."),
            ("Counted in threes, 1 is left; in fives, 1; in sevens, 1. How many?",
             "70 + 21 + 15 = 106; cast out 105: **1**. (Or notice that 1 itself leaves 1 every time.)"),
            ("Why cast out 105 and not some other number?",
             "105 = 3 × 5 × 7 leaves nothing by any of the three, so taking it away does not change any remainder. Any smaller number would."),
            (f"The dayan board for 377,873 by 499,067 ends with {q['k']:,} at the upper left. How can you check it without the board?",
             f"Multiply: 377,873 × {q['k']:,} = {q['prod']:,}, which is {q['quot']:,} × 499,067 + 1."),
            ("Why can 1 by 4 and 2 by 6 never both hold?",
             "Leaving 1 by 4 makes the number odd; leaving 2 by 6 makes it even. Divisors that share a factor must agree on it."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Sunzi Suanjing", text="The whole book in Chinese as a Project Gutenberg e-text; the remainder problem is Volume 3, Problem 26. The catalogue lists the Tang editor Li Chunfeng (602–670).",
                 draw=C.draw_book, link="https://m.gutenberg.org/ebooks/24038", link_text="Project Gutenberg #24038",
                 licence="Drawn placeholder."),
            dict(title="RFC 8017 (PKCS #1 v2.2)", text="The RSA standard, November 2016. Section 5.1.2 decrypts by the remainder theorem with dP, dQ and qInv.",
                 draw=C.draw_manuscript, link="https://rfc-editor.org/rfc/rfc8017", link_text="RFC Editor",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "RFC 8017: PKCS #1: RSA Cryptography Specifications Version 2.2", "K. Moriarty (ed.), B. Kaliski, J. Jonsson, A. Rusch, November 2016", "https://rfc-editor.org/rfc/rfc8017", "Section 3.2 (the key as p, q, dP, dQ, qInv) and 5.1.2 (decryption by remainders)"),
        ]),
        C.prove_it_section(ctx, "ChineseRemainder", d["checks"],
                           "Sunzi's multipliers and answer, all 105 triples of remainders, the dayan rule against the extended Euclidean algorithm on 100,000 random cases, Qin's calendar congruence, divisors with shared factors against search, and RSA decryption both ways.",
                           ["static long dayan("]),
    ]
    return dict(
        title="The Chinese Remainder Problem", date="3rd–5th century CE",
        description="Era 2, topic 3 of The Algorithm Evolution Atlas: Sunzi's remainder problem and Qin Jiushao's dayan rule, with a working dayan board and the same rule inside RSA decryption.",
        lede="Counted in threes, two are left; in fives, three; in sevens, two. Sunzi did not search: he kept three ready-made numbers. Eight centuries later Qin Jiushao found a way to make them for any cycles, and RSA still uses the rule.",
        fieldnote="A short puzzle in a Chinese primer turned out to hold a whole method. The answer comes from three numbers kept ready in advance, and a later treatise shows how to make such numbers for any cycles, by a chain of divisions my hosts would call Euclid's algorithm with a memory.",
        card=[("When", "*Sunzi Suanjing*, 3rd–5th century CE (**disputed**); Qin Jiushao's general rule, 1247"),
              ("Where", "China"),
              ("What hurt", "Finding a number from its remainders, when the cycles are long"),
              ("The fix", "Ready-made multipliers; the dayan rule computes them for any divisors"),
              ("Cost", f"A few divisions per cycle, instead of up to the product of the cycles; {q['div']} divisions for Qin's calendar congruence")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ChineseRemainder.java`.",
    )
