"""Era 7, topic 9: Karp-Rabin fingerprints. Every number is parsed from KarpRabin.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"search: a text of ([\d,]+) random letters .*? a pattern of (\d+) letters .*? ; the obvious method: ([\d,]+) letter comparisons ; fingerprints modulo a random prime p = ([\d,]+): ([\d,]+) rolling steps, ([\d,]+) letter comparisons, ([\d,]+) false alarms? ; (\d+) match(?:es)? ; on a text of ([\d,]+) A's and the pattern AAA...AC, the obvious method makes ([\d,]+) comparisons \(m at every position\), the fingerprints ([\d,]+) rolling steps and ([\d,]+) comparisons", ln):
            d["search"] = dict(n=m.group(1), m=m.group(2), naive=m.group(3), p=m.group(4), steps=m.group(5), comp=m.group(6), fa=m.group(7), matches=m.group(8), worst=m.group(10), wsteps=m.group(11), wcomp=m.group(12))
        elif m := re.match(r"falsealarms: [^;]* ; (.*?) ; the bound", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"primes up to 2\^(\d+) \(([\d,]+) of them\): ([\d,.]+) false alarms on average, bound ([\d,]+)", part)
                rows.append(dict(bits=mm.group(1), count=mm.group(2), avg=mm.group(3), bound=mm.group(4)))
            d["fa"] = rows
        elif m := re.match(r"adversary: a text of ([\d,]+) letters built from ([\d,]+) blocks, .*? ; searching with p = 101: ([\d,]+) false alarms, ([\d,]+) letter comparisons ; with a prime chosen at random afterwards \(p = ([\d,]+)\): ([\d,]+) false alarms, ([\d,]+) letter comparisons", ln):
            d["adv"] = dict(n=m.group(1), blocks=m.group(2), fa=m.group(3), comp=m.group(4), p=m.group(5), fa2=m.group(6), comp2=m.group(7))
        elif m := re.match(r"many: ([\d,]+) patterns of (\d+) letters, .*? ; one pass .*?: ([\d,]+) rolling steps and ([\d,]+) letter comparisons, (\d+) patterns found ; ([\d,]+) separate searches by the obvious method: ([\d,]+) letter comparisons", ln):
            d["many"] = dict(k=m.group(1), m=m.group(2), steps=m.group(3), comp=m.group(4), found=m.group(5), naive=m.group(7))
        elif m := re.match(r"grid: a ([\d,]+) x ([\d,]+) grid .*? a (\d+) x (\d+) block copied from row (\d+), column (\d+) ; two-dimensional fingerprints: ([\d,]+) rolling steps, (\d+) windows? checked .*? ; the obvious method: ([\d,]+) letter comparisons", ln):
            d["grid"] = dict(N=m.group(1), M=m.group(3), r=m.group(5), c=m.group(6), steps=m.group(7), checked=m.group(8), naive=m.group(9))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def roll_svg(d):
    """Rolling the fingerprint one place to the right."""
    def draw(t, standalone):
        o = []
        W, H = 780, 290
        o.append(C.text(20, 26, "Rolling: the next window's fingerprint from the last one, in a few steps", t["ink"], 13, "start", 700))
        text = "GATTACAGC"
        x0, y0, cw = 90, 70, 56
        for i, ch in enumerate(text):
            o.append(C.rect(x0 + i * cw, y0, cw - 4, 40, t["surface"], t["axis"], 1.2, 3))
            o.append(C.text(x0 + i * cw + (cw - 4) / 2, y0 + 26, ch, t["ink"], 16, "middle", 700))
        # window i: positions 1..5, bracketed above in blue; window i + 1: positions 2..6, bracketed below in red
        def bracket(a, b, y, up, col, label):
            xa, xb = x0 + a * cw, x0 + (b + 1) * cw - 4
            tick = -8 if up else 8
            o.append(C.line(xa, y, xb, y, col, 2.5))
            o.append(C.line(xa, y, xa, y - tick, col, 2.5))
            o.append(C.line(xb, y, xb, y - tick, col, 2.5))
            o.append(C.text((xa + xb) / 2, y - 8 if up else y + 18, label, col, 12, "middle", 700))
        bracket(1, 5, y0 - 8, True, t["blue"], "window i")
        bracket(2, 6, y0 + 48, False, t["red"], "window i + 1")
        lines = [("1. Drop the first letter:", "h − c_out · B^(m−1)"), ("2. Shift one place:", "× B"),
                 ("3. Bring in the new letter:", "+ c_in"), ("4. Keep it small:", "mod p")]
        for k, (a, b) in enumerate(lines):
            o.append(C.text(90, 180 + 22 * k, a, t["ink"], 13, "start", 700))
            o.append(C.text(330, 180 + 22 * k, b, t["red"], 13.5, "start", 700))
        o.append(C.text(20, H - 8, "B is the number of letters in the alphabet (4 for A, C, G, T); m is the pattern's length; p is a prime chosen at random.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Rolling a fingerprint one place to the right", t, standalone, 0.55, 780)
    return draw


KR_HTML = """
<div class="board kr-board">
  <div style="min-width:0">
    <div class="controls">
      <label>Text <input id="kr-text" type="text" value="GATTACAGATTACACATTAGATTACAGGATTACATTAC"></label>
      <label>Pattern <input id="kr-pat" type="text" value="TTACA"></label>
    </div>
    <div class="kr-view scrollx" id="kr-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls"><label>Prime p <select id="kr-p"><option>7</option><option selected>13</option><option>101</option><option>1009</option><option>1000003</option></select></label></div>
    <div class="kr-stats" id="kr-stats"></div>
    <p class="say" id="kr-say" aria-live="polite"></p>
  </div>
</div>
"""

KR_CSS = """
.kr-board .controls input{width:100%;min-width:6em;box-sizing:border-box}
.kr-board .controls label{flex:1 1 12em}
.kr-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:3px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.kr-view{overflow-x:auto;margin-top:6px}
.kr-row{display:grid;gap:2px;font:12px var(--mono);margin-bottom:2px}
.kr-row div{text-align:center;padding:4px 0;min-width:0}
.kr-ch{background:var(--surface);border:1px solid var(--rule);font-weight:700;font-size:13px}
.kr-h{color:var(--muted);font-size:10.5px}
.kr-h.hit{color:var(--paper);background:var(--blue);font-weight:700}
.kr-h.fa{color:var(--paper);background:var(--red);font-weight:700}
.kr-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

KR_JS = r"""
(() => {
  const view = document.getElementById("kr-view");
  if (!view) return;
  const B = 256;
  function run() {
    const text = document.getElementById("kr-text").value, pat = document.getElementById("kr-pat").value, p = parseInt(document.getElementById("kr-p").value);
    const n = text.length, m = pat.length;
    view.innerHTML = "";
    if (m === 0 || m > n) { document.getElementById("kr-say").textContent = "Type a pattern no longer than the text."; return; }
    // fingerprints with BigInt so large primes stay exact
    const P = BigInt(p), BB = BigInt(B);
    let top = 1n; for (let k = 1; k < m; k++) top = top * BB % P;
    let hp = 0n, h = 0n;
    for (let k = 0; k < m; k++) { hp = (hp * BB + BigInt(pat.charCodeAt(k) & 255)) % P; h = (h * BB + BigInt(text.charCodeAt(k) & 255)) % P; }
    const hs = [];
    for (let i = 0; i + m <= n; i++) {
      if (i > 0) { h = (h + P - BigInt(text.charCodeAt(i - 1) & 255) * top % P) % P; h = (h * BB + BigInt(text.charCodeAt(i + m - 1) & 255)) % P; }
      hs.push(h);
    }
    let matches = 0, alarms = 0, comps = 0;
    const kind = hs.map((x, i) => {
      if (x !== hp) return "";
      let j = 0; while (j < m) { comps++; if (text[i + j] !== pat[j]) break; j++; }
      if (j === m) { matches++; return "hit"; } alarms++; return "fa";
    });
    const cols = `repeat(${n},minmax(1.7em,1fr))`;
    const r1 = el("div", {class: "kr-row", style: `grid-template-columns:${cols}`}, view);
    [...text].forEach(ch => el("div", {class: "kr-ch"}, r1, ch));
    const r2 = el("div", {class: "kr-row", style: `grid-template-columns:${cols}`}, view);
    for (let i = 0; i < n; i++) el("div", {class: "kr-h " + (kind[i] || ""), title: i < hs.length ? `window ${i + 1}: ${hs[i]}` : ""}, r2, i < hs.length ? String(hs[i]) : "");
    let naive = 0; for (let i = 0; i + m <= n; i++) { let j = 0; while (j < m) { naive++; if (text[i + j] !== pat[j]) break; j++; } }
    const st = document.getElementById("kr-stats"); st.innerHTML = "";
    el("div", {}, st, `pattern's fingerprint: ${hp}`);
    el("div", {}, st, `windows: ${hs.length}, matches: ${matches}, false alarms: ${alarms}`);
    el("div", {}, st, `letters compared: ${comps} (the obvious method: ${naive})`);
    document.getElementById("kr-say").textContent = alarms
      ? `Red: windows whose fingerprint equals the pattern's but whose letters differ. With p = ${p} there are only ${p} possible fingerprints, so collisions are common; try a bigger prime.`
      : `Blue: true matches. Under each letter is the fingerprint of the window starting there (each character a digit in base 256, modulo p). Letters are compared only where the fingerprints agree.`;
  }
  ["kr-text", "kr-pat", "kr-p"].forEach(id => { document.getElementById(id).addEventListener("input", run); document.getElementById(id).addEventListener("change", run); });
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Karp–Rabin fingerprints combined older ideas, and where they led")
    W = 210
    nodes = {
        "hs": (20, 20, "Hashing", "a short number that stands for a key", "Era 5, topic 4", "ink"),
        "kmp": (395, 20, "Fast string searching", "KMP and Boyer–Moore: careful bookkeeping", "Era 6, topic 11", "ink"),
        "rf": (770, 20, "Rabin's fingerprints", "remainders by a randomly chosen divisor", "Harvard report, 1981", "ink"),
        "kr": (395, 180, "Karp–Rabin", "⊕ a rolling fingerprint, compared at every position", "presented 1985; published 1987", "red"),
        "many": (20, 340, "Many patterns at once", "one pass, a table of fingerprints", "", "ink"),
        "two": (395, 340, "Two dimensions", "fingerprints of columns, then of rows", "in the 1987 paper", "ink"),
        "cdc": (770, 340, "Block boundaries", "a rolling fingerprint picks where file blocks end", "LBFS", "ink"),
        "today": (395, 490, "Today", "detecting plagiarism; finding repeated data in files", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("hs", "kr", ports=("bottom", "top:0.15"))
    D.edge("kmp", "kr", ports=("bottom", "top"), label="the same job, no bookkeeping", at=0.5, dx=8, anchor="start")
    D.edge("rf", "kr", ports=("bottom", "top:0.85"))
    D.edge("kr", "many", ports=("bottom:0.15", "top"))
    D.edge("kr", "two", ports=("bottom", "top"))
    D.edge("rf", "cdc", ports=("bottom", "top"), dashed=True)
    D.edge("many", "today", ports=("bottom", "top:0.15"))
    D.edge("cdc", "today", ports=("bottom", "top:0.85"))
    D.text(20, 615, "Today: uses named by Wikipedia's articles on the algorithm and on Rabin's fingerprint. Dashed: the same fingerprint, used for a different job.", "caption")
    return D


def chain(d):
    s, fa, adv, many = d["search"], d["fa"], d["adv"], d["many"]
    steps = [
        (f"The obvious search can compare m letters at every position: {s['worst']} comparisons on a text of A's",
         f"Compare fingerprints, rolled one place at a time: {s['wsteps']} steps and {s['wcomp']} letter comparisons", "Karp and Rabin"),
        ("Different windows can share a fingerprint",
         f"Choose p at random among many primes: false alarms fell from {fa[0]['avg']} (primes up to 2^{fa[0]['bits']}) to {fa[-1]['avg']} (up to 2^{fa[-1]['bits']})", "a number has few prime factors"),
        (f"A prime fixed in advance can be attacked: {adv['fa']} false alarms",
         f"Pick the prime after the text is fixed: {adv['fa2']} false alarms on the same text", "randomness the attacker cannot see"),
        (f"Searching for {many['k']} patterns: {many['naive']} comparisons, one search each",
         f"One pass, all fingerprints in a hash table: {many['comp']} comparisons", "many patterns at once"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from letters to fingerprints, and fooling-proof primes")
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
    s, fa, adv, many, g = d["search"], d["fa"], d["adv"], d["many"], d["grid"]
    fa_rows = [[f"2^{r['bits']}", r["count"], r["avg"], r["bound"]] for r in fa]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Knuth, Morris, Pratt, Boyer and Moore (Era 6) searched text fast by careful bookkeeping about the pattern. Hashing (Era 5) had long turned keys into short numbers. Rabin had shown in 1981 that remainders by a randomly chosen divisor make fingerprints that are hard to fool. Karp and Rabin made the fingerprint roll along the text, one letter at a time. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Karp and Rabin's step. Blue: where rolling fingerprints are used."),
        ]),
        dict(id="play", eyebrow="Try it", title="Fingerprints under every window", toc="Try it", blocks=[
            dict(type="p", text="Type a text and a pattern. Under each letter is the fingerprint of the window that starts there: the window's characters read as one big number (each character a digit in base 256) and reduced modulo the prime p. Letters are compared only where a window's fingerprint equals the pattern's: blue for a true match, red for a false alarm. With p = 7 or 13 false alarms are everywhere; with a larger prime they vanish. The program uses an alphabet of 4 letters and random primes below 2³¹."),
            dict(type="widget", html=KR_HTML, js=KR_JS, css=KR_CSS,
                 fallback=dict(type="table", head=["Primes up to", "How many primes", "False alarms (mean of 20)", "Bound"], num=[1, 2, 3], rows=fa_rows),
                 note="In the interactive edition you can type a text and a pattern and change the prime."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Compare numbers, not letters", toc="How it works", blocks=[
            dict(type="p", text="**A fingerprint.** Read the m letters of the pattern as the digits of one big number, and keep its remainder modulo a prime p. Do the same for each window of m letters in the text."),
            dict(type="svg", name="roll", draw=roll_svg(d), alt="Rolling a fingerprint one place to the right", width=780),
            dict(type="p", text="**Why a random prime.** Two different windows have the same fingerprint only if p divides the difference of the two numbers. A number below 2⁶⁴ has at most 15 different prime factors, so if p is chosen at random from a large set of primes, after the text is written, the chance that it happens to be one of those few is tiny, for every window, whatever the text. A prime fixed in advance has no such protection: knowing it, one can write a text full of collisions."),
            dict(type="p", text="**Extensions.** Put the fingerprints of many patterns in a hash table and check each window against all of them in one pass. In two dimensions, roll fingerprints down each column of the grid, then roll the column fingerprints across each row."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Randomness chosen after the input is fixed cannot be exploited by whoever chose the input. A cheap fingerprint plus a random prime turns \"probably the same\" into \"the same\", with a check only when it matters."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A million letters", toc="Measured", blocks=[
            dict(type="p", text=f"**One pattern,** {s['m']} letters, in {s['n']} random letters A, C, G, T: the obvious method made {s['naive']} letter comparisons; fingerprints modulo the random prime {s['p']} took {s['steps']} rolling steps, {s['comp']} letter comparisons and {s['fa']} false alarms, and found {s['matches']} match. On a text of {s['n']} A's with the pattern AAA…AC, the obvious method made {s['worst']} comparisons (m at every position); the fingerprints {s['wsteps']} rolling steps and {s['wcomp']} comparisons."),
            dict(type="p", text="**False alarms against the size of the prime,** a 32-letter pattern that does not occur, 20 random primes of each size; the bound is positions × 15 / (number of primes):"),
            dict(type="table", head=["Primes up to", "How many primes", "False alarms (mean of 20)", "Bound"], num=[1, 2, 3], rows=fa_rows),
            dict(type="p", text=f"**The adversary.** A text of {adv['n']} letters built from {adv['blocks']} copies of the pattern, each with its last 4 letters changed so that the fingerprint modulo 101 is unchanged. With p = 101: {adv['fa']} false alarms and {adv['comp']} letter comparisons. With a prime chosen at random afterwards ({adv['p']}): {adv['fa2']} false alarms, {adv['comp2']} comparisons."),
            dict(type="p", text=f"**Many patterns.** {many['k']} patterns of {many['m']} letters, half copied from the text: one pass with all their fingerprints in a hash table took {many['steps']} rolling steps and {many['comp']} letter comparisons and found all {many['found']} that occur; {many['k']} separate searches by the obvious method made {many['naive']} comparisons."),
            dict(type="p", text=f"**Two dimensions.** A {g['M']} × {g['M']} block copied from row {g['r']}, column {g['c']} of a {g['N']} × {g['N']} grid of random letters: {g['steps']} rolling steps, {g['checked']} window checked letter by letter, found in the right place. Here the obvious method made only {g['naive']} letter comparisons, because random letters mismatch at once; fingerprints pay off when many windows look alike."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Fingerprints, not strings", toc="The evidence", blocks=[
            dict(type="p", text="Richard Karp and Michael Rabin, \"Efficient randomized pattern-matching algorithms\" (*IBM Journal of Research and Development* 31(2): 249–260, 1987, from a conference held on 1 December 1985 at Yorktown Heights): randomized algorithms for finding a pattern in a text that work on much shorter fingerprints of the strings, use a constant amount of storage, run essentially in real time, are simple to implement, and extend to higher-dimensional pattern matching (summarized from the abstract in the Hebrew University's record)."),
            dict(type="p", text="Wikipedia: the algorithm \"uses a rolling hash to quickly filter out positions of the text that cannot match the pattern\"; its expected time is \"linear in the combined length of the pattern and text\" and its worst case \"the product of the two lengths\"; it is \"a useful algorithm for multiple pattern search\"; \"A practical application of the algorithm is detecting plagiarism\"; and \"the hash function should be selected randomly from a family of hash functions\". Rabin's fingerprint (1981) divides by a randomly chosen irreducible polynomial; LBFS uses it to \"implement variable size shift-resistant blocks\"."),
            dict(type="p", text="Lecture notes on fingerprinting (CS 174, 2007) give the argument this page uses: \"pick a random prime p ∈ {2, ..., T}\", a false match needs p to divide the difference, and \"the number of primes that divide any given n-bit number is at most π(n)\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="String search, again", toc="Full circle", blocks=[
            dict(type="p", text="Era 6 made string search fast by knowing the pattern well. Karp and Rabin make it fast by knowing the pattern hardly at all, a single number, and by leaving the choice of prime to chance."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"On the worst text for the obvious method, {s['worst']} letter comparisons became {s['wcomp']}; on an attacker's text built for p = 101, {adv['fa']} false alarms became {adv['fa2']} once the prime was chosen at random."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With p = 13, about what fraction of non-matching windows will be false alarms?", "About 1 in 13, if the fingerprints are spread evenly."),
            ("Why must the prime be chosen after the text is fixed?", "If the text's author knows p, they can make many windows' numbers differ from the pattern's by multiples of p."),
            ("How does the fingerprint of the next window come from the last one?", "Subtract the first letter times B^(m−1), multiply by B, add the new letter, take the remainder modulo p."),
            ("Why is a false alarm harmless to the answer?", "Every fingerprint match is checked letter by letter, so a false alarm costs time but never gives a wrong result."),
            ("Searching for 1,000 patterns at once: what makes one pass enough?", "Each window's fingerprint is looked up in a table of all the patterns' fingerprints, so one rolling pass serves them all."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Efficient randomized pattern-matching algorithms (1987)", text="*IBM Journal of Research and Development* 31(2): 249–260; the text was not opened for this book.",
                 draw=C.draw_manuscript, link="https://cris.huji.ac.il/en/publications/efficient-randomized-pattern-matching-algorithms/", link_text="The paper's record (Hebrew University)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "KarpRabin", d["checks"],
                           "a search in a million letters and the worst case for the obvious method, false alarms for 80 random primes against the prime-counting bound, an attacker's text against a fixed and a random prime, 1,000 patterns in one pass (each checked against its own search), and a block in a million-letter grid.",
                           ["static int karpRabin(byte[] t, byte[] pat, long p)"]),
    ]
    return dict(
        title="Karp–Rabin Fingerprints", date="1985–1987",
        description="Era 7, topic 9 of The Algorithm Evolution Atlas: Karp and Rabin's rolling fingerprints for pattern matching, why the prime must be random, many patterns at once, and two dimensions.",
        lede="Instead of comparing a pattern with the text letter by letter, Karp and Rabin compared one short number with another, rolling the text's number along one letter at a time, and chose the number's prime at random so that no text can fool it.",
        fieldnote=f"An adversary built a text for the prime 101, and it raised {adv['fa']} false alarms. I chose a prime at random after reading the text, and the same text raised {adv['fa2']}. This species discovered that a coin tossed at the right moment beats any opponent who has to move first.",
        card=[("When", "Presented 1985; published 1987"),
              ("Where", "IBM Journal of Research and Development"),
              ("What hurt", "Intricate preprocessing; m × n comparisons at worst"),
              ("The fix", "Rolling fingerprints modulo a random prime"),
              ("Checked", f"{s['worst']} comparisons became {s['wcomp']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `KarpRabin.java`.",
    )
