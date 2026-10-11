"""Era 2, topic 10: Madhava's series for pi. Every number is parsed from MadhavaSeries.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"corr": []}
    for ln in text.splitlines():
        if m := re.match(r"plain: .*? ; (.+)$", ln):
            d["plain"] = [tuple(int(v) for v in re.match(r"(\d+) decimals: (\d+) terms", x.strip()).groups()) for x in m.group(1).split(";")]
        elif m := re.match(r"corrected (\d+) terms: no correction (\d+) decimals \((\S+)\) ; 1/\(4n\) (\d+) ; n/\(4n\^2\+1\) (\d+) ; \(n\^2\+1\)/\(4n\^3\+5n\) (\d+) \((\S+)\)$", ln):
            g = m.groups()
            d["corr"].append(dict(n=int(g[0]), d0=int(g[1]), v0=g[2], d1=int(g[3]), d2=int(g[4]), d3=int(g[5]), v3=g[6]))
        elif m := re.match(r"sqrt12: 21 terms give (\S+), whose first 11 decimals are (\S+) ; error (\S+) ; correct decimals \(half-unit test\): (.+)$", ln):
            d["s12"] = dict(value=m.group(1), trunc=m.group(2), err=m.group(3),
                            prog=[tuple(int(v) for v in re.match(r"(\d+) terms (\d+)", x).groups()) for x in re.findall(r"\d+ terms \d+", m.group(4))])
        elif m := re.match(r"polygons: (\d+) doublings \(a (\d+)-sided polygon\) and (\d+) square roots before the two bounds agree to 11 decimals: (\S+) < pi < (\S+)$", ln):
            d["poly"] = dict(doublings=int(m.group(1)), sides=int(m.group(2)), roots=int(m.group(3)), lo=m.group(4), hi=m.group(5))
        elif m := re.match(r"chudnovsky: (\d+) terms give pi to (\d+) decimals .* about (\S+) digits per term ; Madhava's sqrt\(12\) series gains (\S+) digits per term$", ln):
            d["ch"] = dict(terms=int(m.group(1)), decimals=int(m.group(2)), per=m.group(3), s12per=m.group(4))
    d["checks"] = C.checks(text)
    return d


def corrections(d):
    """Twenty terms, then each correction in turn."""
    c20 = next(c for c in d["corr"] if c["n"] == 20)
    D = Diagram(1000, 200, "Twenty terms of Madhava's series, with each of the three end corrections")
    W, H = 220, 96
    boxes = [("s", "20 terms", "1 − 1/3 + … − 1/39", f"{c20['d0']} decimal", "ink"),
             ("a", "+ 1/(4n)", "first correction", f"{c20['d1']} decimals", "ink"),
             ("b", "+ n/(4n² + 1)", "second correction", f"{c20['d2']} decimals", "ink"),
             ("c", "+ (n² + 1)/(4n³ + 5n)", "third correction", f"{c20['d3']} decimals", "red")]
    for i, (k, t, sub, dd, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title"), (sub, "note"), (dd, "combo")], color=col)
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "THE SAME TWENTY TERMS, EACH TIME WITH A BETTER GUESS FOR EVERYTHING LEFT OUT (n = 20)", "tag")
    D.text(20, 180, "Each correction is added with the sign of the first term left out. Decimals: correct to within half a unit in the last place.", "caption")
    return D


MD_HTML = """
<div class="board md-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="md-n">Terms <input id="md-n" type="range" min="1" max="60" value="20"></label>
      <span class="md-nv" id="md-nv"></span>
    </div>
    <div class="md-rows" id="md-rows"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">How many digits?</div>
    <p class="say" id="md-say" aria-live="polite"></p>
    <p class="md-pi">π = 3.14159265358979…</p>
  </div>
</div>
"""

MD_CSS = """
.md-board input[type=range]{width:min(260px,55vw)}
.md-nv{font-family:var(--mono);font-size:13px}
.md-rows{display:grid;gap:8px;margin-top:8px}
.md-rows .r{display:grid;grid-template-columns:minmax(0,12em) minmax(0,1fr);gap:4px 10px;align-items:center;font-size:13px}
.md-rows .r .lab{color:var(--ink-2)}
.md-rows .r .val{font-family:var(--mono);font-size:13px;overflow-wrap:anywhere}
.md-rows .r .bar{grid-column:2;height:10px;background:var(--wash);position:relative}
.md-rows .r .bar i{position:absolute;left:0;top:0;bottom:0;background:var(--blue)}
.md-rows .r.best .bar i{background:var(--red)}
.md-rows .r .val b{color:var(--blue)} .md-rows .r.best .val b{color:var(--red)}
.md-pi{font-family:var(--mono);font-size:13px;color:var(--muted)}
.md-board .say{font-size:14.5px}
@media (max-width:600px){.md-rows .r{grid-template-columns:1fr}.md-rows .r .bar{grid-column:1}}
"""

MD_JS = r"""
(() => {
  const rows = document.getElementById("md-rows");
  if (!rows) return;
  const PI = Math.PI;
  const digits = v => { const e = Math.abs(v - PI); if (e === 0) return 15; let d = 0; while (d < 15 && e < 0.5 * 10 ** -(d + 1)) d++; return d; };
  function show() {
    const n = +document.getElementById("md-n").value;
    document.getElementById("md-nv").textContent = `${n} term${n === 1 ? "" : "s"}`;
    let s = 0; for (let k = 1; k <= n; k++) s += (k % 2 ? 1 : -1) / (2 * k - 1);
    const sg = n % 2 === 0 ? 1 : -1;
    const r1 = 1 / (4 * n), r2 = n / (4 * n * n + 1), r3 = (n * n + 1) / (4 * n ** 3 + 5 * n);
    let t = 0; for (let k = 0; k < n; k++) t += (k % 2 ? -1 : 1) / ((2 * k + 1) * 3 ** k);
    const L = [["1 − 1/3 + 1/5 − …", 4 * s], ["+ 1/(4n)", 4 * (s + sg * r1)], ["+ n/(4n² + 1)", 4 * (s + sg * r2)], ["+ (n² + 1)/(4n³ + 5n)", 4 * (s + sg * r3)], ["√12 (1 − 1/(3·3) + …)", Math.sqrt(12) * t]];
    rows.innerHTML = "";
    const ds = L.map(x => digits(x[1])), best = Math.max(...ds);
    L.forEach(([lab, v], i) => {
      const r = el("div", { class: "r" + (ds[i] === best ? " best" : "") }, rows);
      el("span", { class: "lab" }, r, lab);
      const val = el("span", { class: "val" }, r);
      const str = v.toFixed(14), cut = Math.min(str.length, 2 + ds[i]);
      val.innerHTML = `<b>${str.slice(0, cut)}</b>${str.slice(cut)} · ${ds[i]} decimal${ds[i] === 1 ? "" : "s"}`;
      const bar = el("div", { class: "bar" }, r); const fill = el("i", {}, bar); fill.style.width = `${100 * ds[i] / 15}%`;
    });
    document.getElementById("md-say").innerHTML = `With ${n} terms the plain series gives ${ds[0]} correct decimal${ds[0] === 1 ? "" : "s"}; the third correction gives ${ds[3]}, and the √12 series ${ds[4]}. (Double precision stops at about 15.)`;
  }
  document.getElementById("md-n").addEventListener("input", show);
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Madhava's series combined older ideas, and where series for π went")
    W, H = 210, 86
    nodes = {
        "arc": (20, 20, "Polygons around a circle", "a square root per doubling", "Archimedes, Era 1 topic 8", "ink"),
        "sin": (395, 20, "Indian sine tables", "half-chords, step by step", "Aryabhata; topic 2", "ink"),
        "ast": (770, 20, "Kerala astronomy", "computing for the calendar", "the Kerala school", "ink"),
        "mad": (395, 170, "Madhava's series", "⊕ an endless sum, with an end correction", "c. 1400 (writings lost)", "red"),
        "yuk": (20, 330, "Tantrasangraha; Yuktibhasa", "where the series survive", "c. 1500; c. 1530", "ink"),
        "eur": (395, 330, "Gregory and Leibniz", "the same series in Europe", "two centuries later", "ink"),
        "wh": (395, 480, "Whish", "reports the Kerala series to Europe", "1834", "ink"),
        "chu": (770, 330, "Chudnovsky series", "⊕ about 14 digits per term", "1988", "blue"),
        "rec": (770, 480, "Record computations", "314 trillion digits", "November 2025", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("arc", "mad", ports=("bottom", "top:0.15"))
    D.edge("sin", "mad", ports=("bottom", "top"))
    D.edge("ast", "mad", ports=("bottom", "top:0.85"))
    D.edge("mad", "yuk", ports=("bottom:0.1", "top:0.7"))
    D.edge("mad", "eur", ports=("bottom", "top"), dashed=True)
    D.edge("eur", "wh", ports=("bottom", "top"), dashed=True)
    D.edge("mad", "chu", ports=("bottom:0.9", "top:0.3"))
    D.edge("chu", "rec", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: whether the Kerala series reached Europe before Gregory and Leibniz is disputed; Whish's report of 1834 is documented.", "caption")
    return D


def chain(d):
    pl, po, s12, ch = d["plain"], d["poly"], d["s12"], d["ch"]
    p5 = next(p for p in pl if p[0] == 5)
    c20 = next(c for c in d["corr"] if c["n"] == 20)
    steps = [
        (f"Polygons cost a square root for every doubling: {po['roots']} square roots for 11 decimals",
         "An endless sum with no square roots: π/4 = 1 − 1/3 + 1/5 − …", "Madhava, c. 1400"),
        (f"The sum crawls: {p5[1]:,} terms for 5 decimals",
         f"Stop early and estimate the rest: 20 terms and one correction give {c20['d3']} decimals", "Madhava's end corrections"),
        ("Even corrected, each digit still costs more terms",
         f"A faster series, √12 (1 − 1/(3·3) + 1/(5·3²) − …): 21 terms, error {s12['err'].replace('E', ' × 10^')}", "Madhava"),
        ("Records need trillions of digits",
         f"Series that gain about {ch['per']} digits per term", "the Chudnovskys, 1988"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from polygons to record computations")
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
    pl, co, s12, po, ch = d["plain"], d["corr"], d["s12"], d["poly"], d["ch"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Archimedes trapped π between polygons (Era 1, topic 8), paying a square root for every doubling. Indian astronomers had long built sine tables step by step (topic 2). In Kerala, Madhava replaced the polygons by a sum that never ends, and then found a way not to need all of it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Madhava's series. Blue: the series that compute π today."),
        ]),
        dict(id="sum", eyebrow="Try it", title="Add terms, then correct for the rest", toc="Try it", blocks=[
            dict(type="p", text="Move the slider to choose how many terms to add. The top row is the plain series, which creeps toward π. The next three rows add Madhava's three corrections for everything left out. The last row is his faster series with √12. The bold digits are the correct ones."),
            dict(type="widget", html=MD_HTML, js=MD_JS, css=MD_CSS,
                 fallback=dict(type="diagram", name="corrections", diagram=corrections(d)),
                 note="In the interactive edition you can choose the number of terms from 1 to 60 and compare all five ways."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="series", eyebrow="How it works", title="An endless sum, and an honest estimate of the rest", toc="How it works", blocks=[
            dict(type="p", text="The series π/4 = 1 − 1/3 + 1/5 − 1/7 + … needs no square roots, only divisions. But its error after n terms is about 1/(4n), so each new decimal costs ten times as many terms:"),
            dict(type="table", head=["Correct decimals", "Terms of the plain series"], num=[0, 1], rows=[[str(a), f"{b:,}"] for a, b in pl]),
            dict(type="p", text="The Kerala texts stop after n terms and add one correction R for everything left out, with the sign of the first term omitted. MacTutor gives the three forms: R = 1/(4n), R = n/(4n² + 1) and R = (n² + 1)/(4n³ + 5n). The program applied each, in exact arithmetic:"),
            dict(type="diagram", name="corrections-measured", diagram=corrections(d)),
            dict(type="table", head=["Terms", "No correction", "1/(4n)", "n/(4n² + 1)", "(n² + 1)/(4n³ + 5n)", "Value with the third"], num=[0, 1, 2, 3, 4],
                 rows=[[str(c["n"]), str(c["d0"]), str(c["d1"]), str(c["d2"]), str(c["d3"]), c["v3"]] for c in co]),
            dict(type="p", text=f"Madhava's other series converges on its own: π = √12 (1 − 1/(3·3) + 1/(5·3²) − 1/(7·3³) + …). Each term is a third the size of the one before. With 21 terms the program gets {s12['value']}: its first 11 decimals, **{s12['trunc']}**, are the value MacTutor credits to Madhava, and the error is {s12['err'].replace('E', ' × 10^')}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Compute with an infinite process, then deal honestly with the part you did not compute. The end correction turns a hopeless series into a practical one, the first time in this book that someone estimates the error of stopping early."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Square roots against terms", toc="Measured", blocks=[
            dict(type="table", head=["Method", "Work for 11 decimals"], num=[],
                 rows=[[f"Archimedes' polygons (Era 1, topic 8)", f"{po['doublings']} doublings, to a {po['sides']:,}-sided polygon: {po['roots']} square roots"],
                       ["Plain series", f"more than {pl[-1][1]:,} terms (that is only 7 decimals)"],
                       ["Plain series + third correction", f"{next(c for c in co if c['d3'] >= 11)['n']} terms"],
                       ["√12 series", f"21 terms (error {s12['err'].replace('E', ' × 10^')})"]]),
            dict(type="p", text=f"The polygons trap π between {po['lo']} and {po['hi']} after {po['roots']} square roots, each one a long calculation by hand. The corrected series and the √12 series reach the same accuracy with a few dozen divisions."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A mathematician known only through his students", toc="The evidence", blocks=[
            dict(type="p", text="Madhava of Sangamagrama lived about 1350 to 1425 (other estimates: about 1340–1420, **disputed**). \"All the mathematical writings of Madhava have been lost\" (MacTutor); his series are known from Nilakantha's *Tantrasangraha* (about 1500) and Jyesthadeva's Malayalam *Yuktibhasa* (about 1530, dated anywhere from about 1500 to 1550, **disputed**), which gives the derivations. How he found the correction terms is not recorded: Krishnachandran concludes that \"the rationale presented by Kerala authors is not strong enough to convince modern mathematical scholarship\" (**conjecture** for the method)."),
            dict(type="p", text="Did the series reach Europe before Gregory and Leibniz found them in the 17th century? In 2007 the University of Manchester announced \"strong circumstantial evidence\" that they passed through Jesuit missionaries; Kim Plofker, reviewing the later book, found it \"hard to help feeling disappointed that this hypothesis ultimately came to nothing\" (**disputed**). Europe learned of the Kerala series in print from Charles Whish in 1834. Whether this counts as \"calculus\" is a question of framing (**disputed**)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Series still compute π", toc="Full circle", blocks=[
            dict(type="p", text="The fastest way to compute π is still to add up a series, only a far faster one. The Chudnovsky brothers published theirs in 1988; each term adds about 14 correct digits. Wikipedia lists the records computed with it, the latest 314 trillion digits on 18 November 2025, done with the program y-cruncher."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program summed {ch['terms']} terms of the Chudnovsky series and got π to {ch['decimals']:,} decimals, about {ch['per']} digits a term, checked against an arctangent formula. Madhava's √12 series gains {ch['s12per']} digits a term. The idea he wrote down around 1400, that an endless sum can be the best way to a number, is how π is still computed today."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does the plain series need ten times as many terms for each new decimal?", "Its error after n terms is about 1/(4n) of π/4, so to divide the error by ten you must multiply n by ten."),
            ("The sum 1 − 1/3 + 1/5 − 1/7 is too small or too big?", "Too small: the next term, +1/9, is positive, so the correction must be added. That is why the correction takes the sign of the first term left out."),
            ("Why does the √12 series converge so much faster?", "Each term is divided by 3 more than the last, so the terms shrink geometrically, about half a decimal digit per term."),
            (f"How many square roots did the polygons need for 11 decimals?", f"{po['roots']}, for a polygon of {po['sides']:,} sides."),
            ("Is it known how Madhava found his corrections?", "No. The Kerala texts give a rationale, but modern scholars find it unconvincing; the derivation is reconstructed, not recorded."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Ganita-Yukti-Bhasa of Jyesthadeva", text="The Malayalam text of about 1530 that gives the derivations, in K. V. Sarma's English translation with notes by Ramasubramanian, Srinivas and Sriram (Springer and Hindustan Book Agency, 2008).",
                 draw=C.draw_book, link="https://link.springer.com/book/9781848820722", link_text="Springer",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("start", "Chudnovsky algorithm", "Wikipedia", "https://en.wikipedia.org/wiki/Chudnovsky_algorithm", "Published 1988; about 14 digits per term; the list of record computations to 314 trillion digits (2025)"),
        ]),
        C.prove_it_section(ctx, "MadhavaSeries", d["checks"],
                           "the three corrections for every n from 2 to 300 (each better than the last), the √12 series against MacTutor's value, Archimedes' polygons trapping π, and the Chudnovsky series against an arctangent formula to 1,000 decimals.",
                           ["static int decimals("]),
    ]
    return dict(
        title="Madhava's Series for Pi", date="c. 1400 CE",
        description="Era 2, topic 10 of The Algorithm Evolution Atlas: Madhava's series for π with its three end corrections, the √12 series, and the series that compute π today.",
        lede="One minus a third, plus a fifth, minus a seventh: an endless sum for π with no square roots. On its own it is hopeless. Madhava stopped after a few terms and added one correction for everything left out.",
        fieldnote="Archimedes' polygons cost a new square root for every doubling. In Kerala I found a sum that never ends, and astronomers who stopped after a few terms and estimated the rest. It is the first time I have seen anyone compute with an infinite process and deal honestly with the part they did not compute.",
        card=[("When", "Madhava, c. 1350–1425 (**disputed**); his writings lost, known from texts of c. 1500 and c. 1530"),
              ("Where", "Kerala, southwestern India"),
              ("What hurt", "Polygons need a square root for every doubling; the plain series converges too slowly"),
              ("The fix", "An infinite series with an end correction; a faster series with √12"),
              ("Cost", f"20 terms and a correction for {next(c for c in co if c['n'] == 20)['d3']} decimals; {po['roots']} square roots by polygons for 11")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MadhavaSeries.java`.",
    )
