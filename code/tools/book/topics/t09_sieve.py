"""Era 1, topic 9: the sieve of Eratosthenes. Every number is parsed from SieveOfEratosthenes.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"work": []}
    for ln in text.splitlines():
        if m := re.match(r"primes to 100: ([\d ]+)$", ln):
            d["primes100"] = [int(x) for x in m.group(1).split()]
        elif m := re.match(r"smallest factor 2-100: ([\d ]+)$", ln):
            d["spf"] = [int(x) for x in m.group(1).split()]
        elif m := re.match(r"sieve 100: (\d+) crossings by (\d+) primes", ln):
            d["w100"], d["p100"] = int(m.group(1)), int(m.group(2))
        elif m := re.match(r"work (\d+): primes=(\d+) trial-division=(\d+) unfaithful-sieve=(\S+) every-odd=(\d+) odd-primes=(\d+) sieve=(\d+) linear=(\d+) ; n ln ln n = (\d+) ; n / ln n = (\d+)$", ln):
            g = m.groups()
            d["work"].append(dict(n=int(g[0]), primes=int(g[1]), trial=int(g[2]), unf=None if g[3] == "-" else int(g[3]), odd_all=int(g[4]),
                                  odd_p=int(g[5]), sieve=int(g[6]), linear=int(g[7]), nll=int(g[8]), nln=int(g[9])))
        elif m := re.match(r"segmented: (\d+) primes up to 100,000,000 with a window of (\d+) numbers and (\d+) sieving primes", ln):
            d["seg"] = dict(count=int(m.group(1)), window=int(m.group(2)), base=int(m.group(3)))
        elif m := re.match(r"gaps up to 10,000,000: largest gap (\d+) after the prime (\d+); (\d+) twin-prime pairs", ln):
            d["gaps"] = dict(gap=int(m.group(1)), at=int(m.group(2)), twins=int(m.group(3)))
    d["checks"] = C.checks(text)
    return d


PALETTE = ["red", "blue", "yellow", "ink2"]


def grid_svg(d):
    """1 to 100, each composite coloured by the prime that crosses it first; primes outlined."""
    spf = [0, 0] + d["spf"]
    crossing = [p for p in d["primes100"] if p * p <= 100]

    def draw(t, standalone):
        out = []
        cell = 46
        for v in range(1, 101):
            r, c = divmod(v - 1, 10)
            x, y = 20 + c * cell, 40 + r * cell
            if v == 1:
                out.append(C.rect(x, y, cell - 4, cell - 4, t["surface"], t["rule"], 1))
                out.append(C.text(x + 21, y + 27, 1, t["muted"], 14, "middle"))
            elif spf[v] == v:
                out.append(C.rect(x, y, cell - 4, cell - 4, t["surface"], t["ink"], 2.5))
                out.append(C.text(x + 21, y + 27, v, t["ink"], 15, "middle", 700))
            else:
                col = t[PALETTE[crossing.index(spf[v]) % 4]]
                out.append(C.rect(x, y, cell - 4, cell - 4, t["wash"], col, 1.5))
                out.append(C.text(x + 21, y + 27, v, col, 14, "middle"))
                out.append(C.line(x + 6, y + cell - 10, x + cell - 10, y + 6, col, 1.2))
        out.append(C.text(20, 24, "Crossed first by 2 (red), 3 (blue), 5 (yellow), 7 (grey). Outlined: the primes.", t["ink2"], 13))
        return C.svg_doc(20 + 10 * cell + 10, 40 + 10 * cell + 10, "".join(out), "The numbers 1 to 100 sieved: composites coloured by their smallest prime factor", t, standalone, 0.6, 560)
    return draw


SV_HTML = """
<div class="board sv-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="sv-mode">Sieve with <select id="sv-mode"><option value="primes">primes only</option><option value="odd">every odd number (as in Nicomachus)</option><option value="all">every number</option></select></label>
      <label><input id="sv-sq" type="checkbox" checked> start at p × p</label>
    </div>
    <div class="controls">
      <button id="sv-next" class="primary" type="button">Next sieving number</button>
      <button id="sv-all" type="button">Finish</button>
      <button id="sv-reset" type="button">Reset</button>
      <label for="sv-n">up to <select id="sv-n"><option>100</option><option>200</option><option>400</option></select></label>
    </div>
    <div class="sv-grid" id="sv-grid" aria-label="The numbers being sieved"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The sieve so far</div>
    <p class="say" id="sv-say" aria-live="polite"></p>
    <p class="tally" id="sv-count"></p>
  </div>
</div>
"""

SV_CSS = """
.sv-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px;max-width:100%}
.sv-board .controls input[type=checkbox]{width:auto}
.sv-grid{display:grid;grid-template-columns:repeat(20,minmax(0,1fr));gap:2px;font-family:var(--mono);font-size:11px}
.sv-grid span{display:flex;align-items:center;justify-content:center;aspect-ratio:1;background:var(--surface);border:1px solid var(--rule);color:var(--ink);min-width:0}
.sv-grid span.x{background:var(--wash);color:var(--muted);text-decoration:line-through}
.sv-grid span.p{border:2px solid var(--ink);font-weight:700}
.sv-grid span.now{background:var(--ink);color:var(--paper)}
.sv-grid span.twice{box-shadow:inset 0 0 0 2px var(--yellow)}
.sv-board .say{font-size:15px}
.sv-board .tally{font-family:var(--mono);font-size:13px;color:var(--muted)}
@media (max-width:600px){.sv-grid{grid-template-columns:repeat(10,minmax(0,1fr))}}
"""

SV_JS = r"""
(() => {
  const grid = document.getElementById("sv-grid");
  if (!grid) return;
  const COLS = ["var(--red)", "var(--blue)", "var(--yellow)", "var(--ink-2)"];
  let N, crossed, hits, k, crossings, used, cells, done;
  function reset() {
    N = +document.getElementById("sv-n").value;
    crossed = new Array(N + 1).fill(0); hits = new Array(N + 1).fill(0);
    k = 1; crossings = 0; used = []; done = false;
    grid.innerHTML = ""; cells = [];
    for (let v = 1; v <= N; v++) cells[v] = el("span", {}, grid, String(v));
    say("Press Next: the first sieving number is 2.");
    paint();
  }
  const say = t => { document.getElementById("sv-say").innerHTML = t; };
  function nextSiever() {
    const mode = document.getElementById("sv-mode").value;
    let c = k + 1;
    if (mode === "odd" && c > 2 && c % 2 === 0) c++;
    while (c <= N) {
      if (mode === "primes" && crossed[c]) { c++; continue; }
      if (mode === "odd" && c > 2 && c % 2 === 0) { c++; continue; }
      break;
    }
    return c;
  }
  function step() {
    if (done) return false;
    const p = nextSiever();
    const fromSq = document.getElementById("sv-sq").checked;
    if (p * p > N || p > N) {
      done = true;
      const primes = []; for (let v = 2; v <= N; v++) if (!crossed[v]) primes.push(v);
      say(`The next sieving number would be ${p}, and ${p} × ${p} = ${fmt(p * p)} passes ${N}: every number not crossed out is prime. <b>${primes.length} primes</b> up to ${N}.`);
      paint(); return false;
    }
    k = p; used.push(p);
    let n = 0, wasted = 0;
    for (let m = fromSq ? p * p : 2 * p; m <= N; m += p) {
      if (crossed[m]) wasted++; else crossed[m] = p;
      hits[m]++; crossings++; n++;
    }
    say(`Sieve with <b>${p}</b>${crossed[p] ? " (itself already crossed out: a composite, so this work is wasted)" : ""}: ${n} crossings from ${fromSq ? p + " × " + p : "2 × " + p}, ${wasted} of them on numbers already crossed.`);
    paint(p);
    return true;
  }
  function paint(now) {
    for (let v = 1; v <= N; v++) {
      const c = cells[v];
      c.className = (crossed[v] ? "x" : (v > 1 && (done || v <= k) ? "p" : "")) + (v === now ? " now" : "") + (hits[v] > 1 ? " twice" : "");
      c.style.color = crossed[v] && v !== now ? COLS[used.indexOf(crossed[v]) % 4] : "";
    }
    const twice = hits.filter(h => h > 1).length;
    document.getElementById("sv-count").textContent = `${crossings} crossings so far · ${twice} numbers crossed more than once (yellow ring) · sieving numbers used: ${used.join(", ") || "none"}`;
  }
  document.getElementById("sv-next").addEventListener("click", step);
  document.getElementById("sv-all").addEventListener("click", () => { let g = 0; while (step() && g++ < 500); });
  document.getElementById("sv-reset").addEventListener("click", reset);
  ["sv-mode", "sv-sq", "sv-n"].forEach(id => document.getElementById(id).addEventListener("change", reset));
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the sieve combined with other ideas, from Euclid's primes to lazy functional programs")
    W, H = 210, 86
    nodes = {
        "euc": (180, 20, "Primes defined", "", "Euclid's Elements VII, topic 7", "ink"),
        "stp": (610, 20, "Counting on by p", "", "repeated addition, topics 2 and 5", "ink"),
        "sv": (395, 150, "The sieve", "⊕ cross out multiples", "Eratosthenes, c. 240 BCE", "red"),
        "seg": (20, 300, "Segmented sieve", "⊕ one window at a time", "", "ink"),
        "lin": (270, 300, "Linear sieve", "⊕ cross each number once", "1978 or 1987 (disputed)", "ink"),
        "pnt": (520, 300, "How many primes?", "π(n) ≈ n / ln n", "proved 1896", "ink"),
        "fp": (770, 300, "Lazy sieves", "⊕ infinite lists", "O'Neill 2009; Gibbons 2025", "blue"),
        "unf": (770, 450, "The 'unfaithful sieve'", "trial division in disguise", "O'Neill's warning", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("euc", "sv", ports=("bottom", "top"))
    D.edge("stp", "sv", ports=("bottom", "top"))
    for k in ("seg", "lin", "fp"):
        D.edge("sv", k, ports=("bottom", "top"))
    D.edge("sv", "pnt", ports=("bottom", "top"), dashed=True)
    D.edge("fp", "unf", ports=("bottom", "top"))
    D.text(20, 600, "Dashed: the sieve supplies the counts; the theorem came from analysis, not from sieving.", "caption")
    return D


def chain(d):
    w6 = next(w for w in d["work"] if w["n"] == 1_000_000)
    seg = d["seg"]
    steps = [
        (f"Testing each number by division repeats work: {w6['trial']:,} divisions up to a million",
         f"Cross out multiples of each prime: {w6['sieve']:,} crossings", "Eratosthenes, c. 240 BCE"),
        (f"Sieving with every odd number wastes work on composites like 9 and 15: {w6['odd_all']:,} crossings",
         f"Sieve with primes only, from p × p: {w6['odd_p']:,} crossings on the odd numbers", ""),
        ("A table of every number up to N needs N cells of memory", f"Sieve one window at a time: {seg['window']:,} cells for primes up to 100 million", "segmented sieve"),
        ("Composites are still crossed more than once: 12 by 2 and by 3", f"Cross each composite exactly once: {w6['linear']:,} crossings", "linear sieve"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from trial division to the linear sieve")
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


def methods(d):
    w5 = next(w for w in d["work"] if w["n"] == 100_000)
    D = Diagram(1000, 250, "Six ways to list the primes below 100,000, by the work they do")
    items = [("u", "Unfaithful sieve", f"{w5['unf']:,} divisions", "red"), ("t", "Trial division", f"{w5['trial']:,} divisions", "ink"),
             ("s", "Textbook sieve", f"{w5['sieve']:,} crossings", "ink"), ("o", "Every odd number", f"{w5['odd_all']:,} crossings", "ink"),
             ("l", "Linear sieve", f"{w5['linear']:,} crossings", "ink"), ("p", "Odd primes only", f"{w5['odd_p']:,} crossings", "blue")]
    for i, (k, t, n, c) in enumerate(items):
        D.node(k, 20 + i * 163, 60, 145, 90, [(t, "title"), (n, "combo")], color=c)
        if i:
            D.edge(items[i - 1][0], k, ports=("right", "left"))
    D.text(20, 38, "LESS WORK TO THE RIGHT; ALL SIX FIND THE SAME 9,592 PRIMES", "tag")
    D.text(20, 190, "Divisions and crossings are not the same cost, but each is one basic step of its method.", "caption")
    D.text(20, 212, "The every-odd and odd-primes rows skip even numbers; the textbook sieve crosses them too.", "caption")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    w = {x["n"]: x for x in d["work"]}
    w5, w6 = w[100_000], w[1_000_000]
    seg, gp = d["seg"], d["gaps"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Euclid's *Elements* defined primes (topic 7); counting on by a fixed step is repeated addition (topics 2 and 5). The sieve turns the question round: instead of asking whether each number is prime, it crosses out what cannot be. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the sieve. Blue: where it is argued about today, in functional programming."),
        ]),
        dict(id="sieve", eyebrow="Try it", title="Cross out, and see what survives", toc="Try it", blocks=[
            dict(type="p", text="Take the first number not yet crossed out: it is prime. Cross out its multiples, starting at its square. Repeat until the square passes the end of the table. Switch the sieving numbers to every odd number, as in Nicomachus's account, or start at 2p instead of p × p, and watch the wasted crossings."),
            dict(type="widget", html=SV_HTML, js=SV_JS, css=SV_CSS,
                 fallback=dict(type="svg", name="grid", draw=grid_svg(d), alt="The numbers 1 to 100 sieved", width=560),
                 note="In the interactive edition you can sieve up to 400, by primes, by every odd number or by every number."),
            dict(type="p", text=f"Up to 100 the sieve makes **{d['w100']}** crossings with just {d['p100']} primes: 2, 3, 5 and 7. 11 × 11 = 121 passes 100, so the {len(d['primes100'])} numbers left are prime."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A method known from a later book", toc="The evidence", blocks=[
            dict(type="p", text="Eratosthenes of Cyrene (276–194 BCE) was librarian at Alexandria from about 240 BCE (**documented**). None of his writing on the sieve survives. The earliest account is in Nicomachus of Gerasa's *Introduction to Arithmetic*, about 100 CE, three centuries later, and it sieves with odd numbers rather than only with primes. So \"c. 240 BCE\" dates the man, not the method."),
            dict(type="callout", kind="key", label="Key idea",
                 text="The sieve trades memory for time: it keeps a table of every number, and in return never divides. The reciprocal tables of topic 3 made the same trade as a reference book, worked out once and copied; here the table is working memory, built and used inside one computation."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How much work?", toc="Measured", blocks=[
            dict(type="p", text="Six ways to list the primes. *Trial division* tests each number by the primes up to its square root. The *unfaithful sieve* is the one-line functional program described below. "
                                "*Every odd number* and *odd primes only* sieve the odd numbers, crossing out with every odd number (as in Nicomachus's account) or with the odd primes. "
                                "The *textbook sieve* crosses out the multiples of each prime from p × p over all the numbers. The *linear sieve* crosses out each composite exactly once."),
            dict(type="diagram", name="methods", diagram=methods(d)),
            dict(type="table", head=["Up to", "Primes", "Trial division", "Unfaithful sieve", "Every odd number", "Odd primes only", "Textbook sieve", "Linear sieve", "n ln ln n"],
                 num=[0, 1, 2, 3, 4, 5, 6, 7, 8],
                 rows=[[f"{x['n']:,}", f"{x['primes']:,}", f"{x['trial']:,}", f"{x['unf']:,}" if x["unf"] else "—", f"{x['odd_all']:,}", f"{x['odd_p']:,}", f"{x['sieve']:,}", f"{x['linear']:,}", f"{x['nll']:,}"] for x in d["work"]]),
            dict(type="p", text=f"The textbook sieve's crossings stay below n ln ln n, the classic estimate, at every size. (ln is the natural logarithm; ln ln n grows so slowly that n ln ln n is barely more than a few times n.) The program also counted **{seg['count']:,}** primes up to 100 million with a segmented sieve, holding only {seg['base']:,} sieving primes and a window of {seg['window']:,} numbers in memory."),
            dict(type="p", text=f"Up to 10 million, the largest gap between consecutive primes is {gp['gap']}, after {gp['at']:,}; there are {gp['twins']:,} pairs of twin primes (primes 2 apart)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The sieve that was not a sieve", toc="Full circle", blocks=[
            dict(type="p", text="Functional programming has a famous one-line \"sieve\": take the first number, then filter every later number that it divides, and repeat. In 2009 Melissa O'Neill showed in the *Journal of Functional Programming* that this is really trial division, and far slower than the real thing: it tests each number against each earlier prime until one divides it, instead of crossing out multiples. In 2025 Jeremy Gibbons returned in the same journal to lazy sieves, programs that produce the primes one at a time, only as they are asked for."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Up to 100,000 the program counts **{w5['unf']:,}** divisions for the one-line version against {w5['sieve']:,} crossings for the sieve, about {round(w5['unf'] / w5['sieve'])} times the work. An algorithm named after a librarian of about 240 BCE was still being argued over in a journal in 2025."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why can the sieve stop at 7 when listing primes up to 100?", "Any composite up to 100 has a prime factor at most √100 = 10. The primes up to 10 are 2, 3, 5, 7, so after them nothing composite is left."),
            ("Why start crossing out the multiples of 7 at 49?", "14, 21, 28, 35 and 42 have smaller prime factors (2, 3, 5), so they were crossed out already. The first multiple of 7 with no smaller factor is 7 × 7."),
            ("Sieving with 9 as well as the primes: does it change the answer?", "No: every multiple of 9 is a multiple of 3 and is already crossed out. It only adds work, as the every-odd-number column shows."),
            (f"How many primes are there below 1,000,000? And what does n / ln n estimate?", f"**{w6['primes']:,}**; n / ln n gives about {w6['nln']:,}, an underestimate of about {100 * (w6['primes'] - w6['nln']) / w6['primes']:.0f}%."),
            ("Why is the one-line functional 'sieve' slow?", f"It divides each number by every earlier prime until one divides it, with no square-root stop: {w5['unf']:,} divisions up to 100,000."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Introduction to Arithmetic", text="Nicomachus of Gerasa, about 100 CE, Book I, Chapter 13: the earliest surviving account of the sieve. D'Ooge's English translation, 1926.",
                 draw=C.draw_book, link="https://archive.org/details/nicomachus-introduction-to-arithmetic", link_text="Internet Archive scan",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "SieveOfEratosthenes", d["checks"],
                           "six methods agreeing on the primes up to 10 million, the known prime counts up to 10⁸, the linear sieve crossing each composite exactly once, and the segmented sieve against the plain one.",
                           ["static boolean[] sieve(int n)"]),
    ]
    return dict(
        title="The Sieve of Eratosthenes", date="c. 240 BCE",
        description="Era 1, topic 9 of The Algorithm Evolution Atlas: the sieve of Eratosthenes, with an interactive sieve, six methods compared, and verified links.",
        lede="Never ask whether a number is prime. For each prime, cross out its multiples; whatever survives is prime. A table of numbers does the work that division did.",
        fieldnote="Testing each number for divisors repeats the same work again and again. The sieve turns the problem inside out.",
        card=[("When", "Eratosthenes active c. 240 BCE; first account by Nicomachus, c. 100 CE"),
              ("Where", "Alexandria (**documented**); the method's exact origin is unknown"),
              ("What hurt", "Trial division tests each number from scratch"),
              ("The fix", "Cross out multiples instead; stop at √n"),
              ("Cost", f"About n ln ln n crossings: {w6['sieve']:,} up to a million"),
              ("Atlas", "Ch. 3 The Sieve of Eratosthenes")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `SieveOfEratosthenes.java`.",
    )
