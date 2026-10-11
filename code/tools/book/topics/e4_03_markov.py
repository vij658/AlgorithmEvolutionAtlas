"""Era 4, topic 3: Markov chains. Every number is parsed from MarkovChains.java's output."""
import random
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"counts: (\d+) letters, (\d+) vowels, (\d+) consonants ; pairs (\d+) vowel-vowel, (\d+) consonant-consonant, (\d+) mixed, total (\d+)$", ln):
            d["c"] = dict(zip(["N", "V", "C", "VV", "CC", "MIX", "tot"], [int(x) for x in m.groups()]))
        elif m := re.match(r"pairs: .*? a closed loop needs (\d+) mixed pairs, not (\d+) ; .*? fit with vowel->consonant (\d+) and consonant->vowel (\d+), only if (.+)$", ln):
            d["pairs"] = dict(loop=int(m.group(1)), mix=int(m.group(2)), VC=int(m.group(3)), CV=int(m.group(4)), cond=m.group(5))
        elif m := re.match(r"probabilities: a vowel ([\d.]+) ; a vowel after a vowel (\d+)/(\d+) = ([\d.]+) ; a vowel after a consonant (\d+)/(\d+) = ([\d.]+) ; independent letters would give .*? = (\d+) double vowels, the poem has (\d+)$", ln):
            g = m.groups()
            d["p"] = dict(p=g[0], p1=g[3], p2=g[6], indep=int(g[7]), vv=int(g[8]))
        elif m := re.match(r"longrun: share of vowels p2 / \(1 - p1 \+ p2\) = ([\d.]+) ; d = p1 - p2 = (-?[\d.]+) ; chance of a vowel n letters after a vowel vs after a consonant: (.+)$", ln):
            d["lr"] = dict(pi=m.group(1), d=m.group(2), rows=re.findall(r"(\d+) letters on: ([\d.]+) vs ([\d.]+)", m.group(3)))
        elif m := re.match(r"spread: dispersion factor \(1 \+ d\) / \(1 - d\) = ([\d.]+) ; groups of (\d+) letters: independent letters, variance n p q = ([\d.]+), simulated ([\d.]+) ; the chain, exact variance ([\d.]+) \(ratio ([\d.]+)\), simulated ([\d.]+), over (\d+) groups$", ln):
            d["sp"] = dict(zip(["factor", "len", "npq", "simI", "exact", "ratio", "simC", "groups"], m.groups()))
        elif m := re.match(r"lln: .*? share of vowels after (.+) ; long-run value ([\d.]+)$", ln):
            d["lln"] = dict(rows=re.findall(r"([\d,]+) letters: ([\d.]+)", m.group(1)), pi=m.group(2))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def grid_svg(d):
    """A hundred letters from a two-state chain with the Onegin probabilities, written ten by ten as Markov did."""
    p1, p2 = float(d["p"]["p1"]), float(d["p"]["p2"])

    def draw(t, standalone):
        rnd = random.Random(1913)
        v = rnd.random() < 0.432
        out, s, x0, y0 = [], 30, 30, 40
        for i in range(100):
            v = rnd.random() < (p1 if v else p2)
            x, y = x0 + (i % 10) * s, y0 + (i // 10) * s
            out.append(C.rect(x, y, s - 4, s - 4, t["red"] if v else t["surface"], t["axis"], 1))
            out.append(C.text(x + (s - 4) / 2, y + 18, "V" if v else "C", t["on_red"] if v else t["muted"], 12, "middle", 700))
        out.append(C.text(x0, 26, "100 letters from the chain, ten by ten", t["muted"], 12.5))
        X = 360
        rows = [("After a vowel:", f"vowel {p1:.3f}, consonant {1 - p1:.3f}", t["red"]),
                ("After a consonant:", f"vowel {p2:.3f}, consonant {1 - p2:.3f}", t["blue"])]
        for i, (a, b, col) in enumerate(rows):
            out.append(C.text(X, 80 + i * 52, a, col, 14, "start", 700))
            out.append(C.text(X, 100 + i * 52, b, t["ink"], 13.5))
        out.append(C.text(X, 200, f"Long-run share of vowels: {d['lr']['pi']}", t["ink"], 14, "start", 700))
        out.append(C.text(X, 222, "Vowels and consonants alternate far more", t["muted"], 13))
        out.append(C.text(X, 240, "often than independent letters would.", t["muted"], 13))
        out.append(C.text(X, 280, "Probabilities from the counts reported for", t["muted"], 12))
        out.append(C.text(X, 296, "Markov's 20,000 letters of Eugene Onegin.", t["muted"], 12))
        return C.svg_doc(720, 350, "".join(out), "A hundred letters from a two-state Markov chain", t, standalone, 0.55, 720)
    return draw


MK_HTML = """
<div class="board mk-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="mk-p1">Vowel after a vowel <input id="mk-p1" type="range" min="0.02" max="0.98" step="0.01" value="0.13"></label><span class="mk-v" id="mk-p1v"></span>
    </div>
    <div class="controls">
      <label for="mk-p2">Vowel after a consonant <input id="mk-p2" type="range" min="0.02" max="0.98" step="0.01" value="0.66"></label><span class="mk-v" id="mk-p2v"></span>
    </div>
    <div class="presets" id="mk-pre"></div>
    <div class="mk-grid" id="mk-grid" aria-label="One hundred letters, ten by ten"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The share of vowels as the text grows</div>
    <svg id="mk-svg" viewBox="0 0 420 220" role="img" aria-label="Running share of vowels over 20,000 letters"></svg>
    <ol class="mk-steps" id="mk-steps"></ol>
    <button id="mk-again" type="button">New text</button>
  </div>
</div>
"""

MK_CSS = """
.mk-board .controls{flex-wrap:wrap}
.mk-board input[type=range]{width:min(160px,40vw)}
.mk-v{font-family:var(--mono);font-size:13px;min-width:3.5em}
.mk-grid{display:grid;grid-template-columns:repeat(10,1fr);gap:3px;max-width:330px;margin:10px 0}
.mk-grid span{aspect-ratio:1;display:flex;align-items:center;justify-content:center;font:600 12px var(--mono);border:1px solid var(--axis);background:var(--surface);color:var(--muted)}
.mk-grid span.v{background:var(--red);color:var(--on-red);border-color:var(--red)}
.mk-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.mk-steps .m{font-family:var(--mono);font-size:12.5px}
#mk-svg{width:100%;max-width:420px;height:auto}
"""

MK_JS = r"""
(() => {
  const grid = document.getElementById("mk-grid");
  if (!grid) return;
  let seed = 1913;
  const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const pre = document.getElementById("mk-pre");
  [["Onegin", 0.13, 0.66], ["Independent", 0.43, 0.43], ["Sticky", 0.9, 0.1], ["Strict alternation", 0.02, 0.98]].forEach(([n, a, b]) => {
    const bt = el("button", {type: "button"}, pre, n);
    bt.addEventListener("click", () => { document.getElementById("mk-p1").value = a; document.getElementById("mk-p2").value = b; show(); });
  });
  function show() {
    const p1 = +document.getElementById("mk-p1").value, p2 = +document.getElementById("mk-p2").value;
    document.getElementById("mk-p1v").textContent = p1.toFixed(2); document.getElementById("mk-p2v").textContent = p2.toFixed(2);
    const s0 = seed;
    const pi = p2 / (1 - p1 + p2), d = p1 - p2;
    let v = rnd() < pi;
    const N = 20000, L = 100, G = N / L;
    let count = 0, sum = 0, sum2 = 0, g = 0, vv = 0, prev = null;
    const share = [];
    grid.innerHTML = "";
    for (let i = 1; i <= N; i++) {
      v = rnd() < (v ? p1 : p2);
      if (v) { count++; g++; }
      if (prev === true && v) vv++;
      prev = v;
      if (i <= 100) el("span", {class: v ? "v" : ""}, grid, v ? "V" : "C");
      if (i % L === 0) { sum += g; sum2 += g * g; g = 0; }
      if (i % 100 === 0) share.push(count / i);
    }
    seed = s0;
    const svg = document.getElementById("mk-svg"); svg.innerHTML = "";
    const x0 = 40, x1 = 410, y0 = 20, y1 = 190, lo = 0, hi = 1;
    const X = i => x0 + (x1 - x0) * i / (share.length - 1), Y = s => y1 - (y1 - y0) * (s - lo) / (hi - lo);
    sv("line", {x1: x0, y1: y1, x2: x1, y2: y1, stroke: "var(--axis)"}, svg);
    sv("line", {x1: x0, y1: y0, x2: x0, y2: y1, stroke: "var(--axis)"}, svg);
    sv("line", {x1: x0, y1: Y(pi), x2: x1, y2: Y(pi), stroke: "var(--blue)", "stroke-dasharray": "5 4", "stroke-width": 1.5}, svg);
    sv("path", {d: share.map((s, i) => (i ? "L" : "M") + X(i).toFixed(1) + "," + Y(s).toFixed(1)).join(" "), fill: "none", stroke: "var(--red)", "stroke-width": 2}, svg);
    sv("text", {x: x0 - 6, y: Y(1) + 4, "text-anchor": "end", "font-size": 11, fill: "var(--muted)"}, svg, "1");
    sv("text", {x: x0 - 6, y: Y(0) + 4, "text-anchor": "end", "font-size": 11, fill: "var(--muted)"}, svg, "0");
    sv("text", {x: x1, y: y1 + 18, "text-anchor": "end", "font-size": 11, fill: "var(--muted)"}, svg, "20,000 letters");
    sv("text", {x: x1, y: Y(pi) - 6, "text-anchor": "end", "font-size": 11, fill: "var(--blue)"}, svg, "long-run share " + pi.toFixed(3));
    const mean = sum / G, varG = sum2 / G - mean * mean, npq = L * pi * (1 - pi);
    const ol = document.getElementById("mk-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    li(`vowels: <span class="m">${fmt(count)}</span> of 20,000 = ${(count / N).toFixed(4)}; the chain's long-run share is ${pi.toFixed(4)}`);
    li(`double vowels: <span class="m">${fmt(vv)}</span>; independent letters with the same share would give about ${fmt(Math.round(N * pi * pi))}`);
    li(`spread of vowels in ${G} groups of 100: variance <span class="m">${varG.toFixed(1)}</span>, against ${npq.toFixed(1)} for independent letters; Markov's factor (1 + d)/(1 − d) = ${((1 + d) / (1 - d)).toFixed(3)}`);
  }
  ["mk-p1", "mk-p2"].forEach(id => document.getElementById(id).addEventListener("input", show));
  document.getElementById("mk-again").addEventListener("click", () => { seed = (seed + 7919) >>> 0; show(); });
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Markov chains combined older ideas, and where they led")
    W = 210
    nodes = {
        "bern": (20, 20, "Law of large numbers", "averages of independent trials settle", "Bernoulli, 1713", "ink"),
        "pts": (395, 20, "Counting chances", "the problem of points", "Era 3 topic 4", "ink"),
        "nek": (770, 20, "Nekrasov's claim", "independence is necessary", "1902", "ink"),
        "mk": (395, 170, "Markov chains", "⊕ each trial depends on the one before", "1906; Onegin 1913", "red"),
        "phys": (20, 330, "Physics and shuffling", "Ehrenfest 1907, Poincaré 1912", "read later as chains", "ink"),
        "kol": (395, 330, "Kolmogorov", "continuous-time Markov processes", "1931", "ink"),
        "sh": (770, 330, "Shannon", "English as a Markov process", "topic 12, 1948", "ink"),
        "today": (395, 480, "Chains today", "speech, genes, web search, sampling", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("bern", "mk", ports=("bottom", "top:0.15"))
    D.edge("pts", "mk", ports=("bottom", "top"))
    D.edge("nek", "mk", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("mk", "phys", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("mk", "kol", ports=("bottom", "top"))
    D.edge("mk", "sh", ports=("bottom:0.9", "top:0.3"))
    D.edge("kol", "today", ports=("bottom", "top"))
    D.edge("sh", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed from Nekrasov: the claim Markov set out to refute. Dashed to physics: models found independently, recognised as chains later.", "caption")
    return D


def chain(d):
    p, sp = d["p"], d["sp"]
    steps = [
        ("The law of large numbers was proved only for independent trials",
         "Let each trial depend on the one before; prove the averages still settle", "Markov, 1906"),
        ("Are such chains anything more than a mathematician's example?",
         f"Count 20,000 letters of Onegin: a vowel follows a vowel with chance {p['p1']}, a consonant with {p['p2']}", "Markov, 1913"),
        ("Dependence changes how far a count strays from its average",
         f"Measure it: the dispersion factor (1 + d)/(1 − d) = {sp['factor']}", "Markov, 1913"),
        ("Real text depends on more than the last letter",
         "Longer memories: chains of two letters back; word statistics", "Markov 1911; Shannon 1948"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from independent trials to chains of letters")
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
    c, pr, p, lr, sp, lln = d["c"], d["pairs"], d["p"], d["lr"], d["sp"], d["lln"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Bernoulli's law of large numbers (1713) said that the share of heads in many independent tosses settles near one half. In 1902 Nekrasov claimed that independence is necessary for this. Markov added one idea, that each trial may depend on the one before through a fixed table of chances, and proved that the averages settle anyway. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Markov's chains. Blue: where chains are used today (Hayes, *American Scientist*, 2013)."),
        ]),
        dict(id="grid", eyebrow="Try it", title="Write a text with a one-letter memory", toc="Try it", blocks=[
            dict(type="p", text="Set two chances: that a vowel follows a vowel, and that a vowel follows a consonant. The page writes 20,000 letters, shows the first hundred ten by ten (as Markov wrote out Pushkin's letters), and plots the share of vowels as the text grows. The share settles at the dashed line whatever you choose, unless both chances are extreme. What changes is how much the counts wobble on the way."),
            dict(type="widget", html=MK_HTML, js=MK_JS, css=MK_CSS,
                 fallback=dict(type="svg", name="grid", draw=grid_svg(d), alt="A hundred letters from a two-state Markov chain", width=720),
                 note="In the interactive edition you can set the two chances and watch the share of vowels settle."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A table of four chances", toc="How it works", blocks=[
            dict(type="p", text=f"**The counts.** The figures reported for Markov's sample (Hayes, 2013): {c['N']:,} letters, {c['V']:,} vowels and {c['C']:,} consonants; {c['VV']:,} vowel–vowel pairs, {c['CC']:,} consonant–consonant pairs and {c['MIX']:,} mixed. From them the program recomputes the chances: a vowel {p['p']}; a vowel after a vowel {p['p1']}; a vowel after a consonant {p['p2']}. If letters were independent, about {p['indep']:,} double vowels would be expected; the poem has {p['vv']:,}."),
            dict(type="table", head=["", "next is a vowel", "next is a consonant"], num=[1, 2],
                 rows=[["after a vowel", p["p1"], f"{1 - float(p['p1']):.4f}"], ["after a consonant", p["p2"], f"{1 - float(p['p2']):.4f}"]]),
            dict(type="p", text=f"**A small puzzle in the counts.** The pairs add up to {c['tot']:,}, one for each letter. That does not fit 19,999 pairs inside the sample, nor a closed loop (which would need {pr['loop']:,} mixed pairs, not {pr['mix']:,}). It fits exactly if every letter starts a pair and the last pair reaches one letter past the sample, and only if the sample's first letter is a consonant and the 20,001st a vowel. Chapter one begins «Мой дядя», with a consonant. Markov's own text, which would settle how he counted, was not opened (see the catalog)."),
            dict(type="p", text=f"**The long run.** Whatever the first letter, the chance of a vowel n letters later approaches p₂ / (1 − p₁ + p₂) = {lr['pi']}, and the difference shrinks by a factor |p₁ − p₂| = {abs(float(lr['d'])):.4f} each letter:"),
            dict(type="table", head=["Letters later", "Chance of a vowel, after a vowel", "after a consonant"], num=[0, 1, 2],
                 rows=[[n, a, b] for n, a, b in lr["rows"]]),
            dict(type="callout", kind="key", label="Key idea",
                 text="Dependence does not stop averages from settling, as long as the chain cannot get stuck or trapped in a cycle. It changes the size of the wobble: here the counts of vowels in groups of 100 letters vary about a third as much as they would for independent letters."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The wobble, and the settling", toc="Measured", blocks=[
            dict(type="table", head=["Groups of 100 letters", "Variance of the vowel count"], num=[1],
                 rows=[["independent letters: n·p·q", sp["npq"]], ["independent letters, simulated", sp["simI"]],
                       ["the chain: exact formula", sp["exact"]], ["the chain, simulated", sp["simC"]]], hl=2),
            dict(type="p", text=f"Over {int(sp['groups']):,} simulated groups, the chain's variance is {sp['ratio']} times that of independent letters; for very long groups the ratio tends to Markov's dispersion factor (1 + d)/(1 − d) = {sp['factor']}, with d = p₁ − p₂. Markov's own value for his \"simple\" coefficient was 0.303, which a recount reproduced (Sabatini)."),
            dict(type="table", head=["Letters simulated", "Share of vowels"], num=[0, 1], rows=[[a, b] for a, b in lln["rows"]] + [["long-run value", lln["pi"]]]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A quarrel, then a poem", toc="The evidence", blocks=[
            dict(type="p", text="Nekrasov (1902) argued that the law of large numbers requires independence; Markov called this \"an abuse of mathematics\" and showed that the law \"applies perfectly well to systems of dependent variables if they meet certain criteria\" (Hayes, *American Scientist*, 2013). His first paper on the subject was written in 1906 and printed in 1907 in the Kazan *Izvestiya* (Basharin, Langville and Naumov)."),
            dict(type="p", text="On 23 January 1913 he presented the Onegin analysis to the Imperial Academy in St Petersburg (Harvard Gazette, 2013); the letters were written out without punctuation or spaces, in 200 grids of 10 by 10 (Schwartz, IEEE Spectrum). How much of the poem he used is **disputed** among the opened sources: \"the first 70 stanzas\" (Angelino) or \"the first 76 stanzas\" (Sabatini)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="From Pushkin to predictive text", toc="Full circle", blocks=[
            dict(type="p", text="Markov chose letters to show that dependence is everywhere. Shannon (topic 12) used the same counts, on longer stretches of text, to generate imitation English in 1948; today chains with very long memories model speech, genes and the order of web pages (Hayes). Monte Carlo methods (topic 10) later ran chains on purpose, as a way to sample."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Independent letters would have given Pushkin about {p['indep']:,} double vowels in 20,000 letters. He wrote {p['vv']:,}: the evidence, in one count, that a letter remembers the letter before it."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("If a vowel follows a vowel with chance 0.128, what is the chance that a consonant follows a vowel?", "1 − 0.128 = 0.872: after a vowel, one of the two must come next."),
            (f"Why would independent letters give about {p['indep']:,} double vowels?", f"Each pair of neighbours would be two vowels with chance {p['p']}² ≈ 0.187, and there are 20,000 pairs."),
            ("What long-run share of vowels does the chain with p₁ = 0.5, p₂ = 0.5 give?", "0.5 / (1 − 0.5 + 0.5) = 0.5: with p₁ = p₂ the letters are independent, and the share is just that chance."),
            ("Why does strict alternation (p₁ near 0, p₂ near 1) make the counts in a group of 100 almost fixed?", "Vowels and consonants take turns, so any 100 letters hold almost exactly 50 of each: dependence has squeezed out the wobble."),
            ("What did Markov's chains show against Nekrasov?", "That the law of large numbers does not need independence: dependent trials can still have averages that settle."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Sur un cas d'épreuves liées en chaîne multiple (1911)", text="One of Markov's papers on trials linked in a chain, in the Academy's Bulletin (in Russian).",
                 draw=C.draw_manuscript, link="https://mathnet.ru/eng/im6871", link_text="Math-Net.Ru", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MarkovChains", d["checks"],
                           "the reported counts against three ways of counting pairs, the chances 0.432, 0.128 and 0.663 and the 3,731 independent double vowels, the long-run share, the shrinking gap |d|ⁿ in the table's powers, and simulated variances against the exact formula.",
                           ["static double varExact("]),
    ]
    return dict(
        title="Markov Chains", date="1906–1913",
        description="Era 4, topic 3 of The Algorithm Evolution Atlas: Markov's chains of dependent trials, and his count of vowels and consonants in Eugene Onegin.",
        lede="Probability's law of averages had been proved only for independent trials. Markov proved it for trials that each depend on the one before, and then tested the idea on 20,000 letters of Pushkin.",
        fieldnote=f"After a vowel, Pushkin wrote a vowel only {float(p['p1']) * 100:.0f} times in a hundred; after a consonant, {float(p['p2']) * 100:.0f} times. His letters remember their neighbours, and still the share of vowels settles, at {lr['pi']}. Markov wrote them out in 200 grids of ten by ten.",
        card=[("When", "1906; 23 January 1913"),
              ("Where", "St Petersburg"),
              ("What hurt", "The law of large numbers assumed independent trials"),
              ("The fix", "A chain: the next state depends on the present one"),
              ("Cost", "A table of chances; the averages still settle")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MarkovChains.java`.",
    )
