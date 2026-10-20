"""Era 8, topic 5: MinHash and locality-sensitive hashing. Every number is parsed from MinHashLsh.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"exact: all ([\d,]+) pairs .*?, all ([\d,]+) orders", ln):
            d["exact"] = dict(pairs=m.group(1), orders=m.group(2))
        elif m := re.match(r"documents: corpus.txt, ([\d,]+) words, cut into (\d+) pieces of 40 words ; .*?: ([\d,]+) documents ; shingles of (\d+) words ; (.*)$", ln):
            d["docs"] = dict(words=m.group(1), pieces=m.group(2), n=m.group(3), w=m.group(4),
                             rates=re.findall(r"(\d+)% of words replaced: resemblance ([\d.]+) on average", m.group(5)))
        elif ln.startswith("estimate: "):
            d["est"] = dict(pairs=re.search(r"estimate: (\d+) pairs", ln).group(1),
                            rows=re.findall(r"(\d+) hash functions \(([\d,]+) bytes a document\): typical error ([\d.]+) \(theory ([\d.]+)\)", ln))
        elif ln.startswith("bands: "):
            m = re.match(r"bands: (\d+) bands of (\d+) rows", ln)
            d["bands"] = dict(b=int(m.group(1)), r=int(m.group(2)),
                              pts=[(float(a), float(b), float(c)) for a, b, c in re.findall(r"([\d.]+):([\d.]+):([\d.]+)", ln.split("theory 1 - (1 - J^4)^32 ; ")[1])])
        elif m := re.match(r"search: ([\d,]+) documents ; comparing every pair: ([\d,]+) comparisons, ([\d,]+) pairs with resemblance at least 0.5 ; .*?: ([\d,]+) candidate pairs to check, finding ([\d,]+) of them \(([\d.]+)%\), ([\d,]+) candidates below 0.5", ln):
            d["search"] = dict(n=m.group(1), comp=m.group(2), true=m.group(3), cand=m.group(4), found=m.group(5), pct=m.group(6), false=m.group(7))
        elif ln.startswith("widget: "):
            m = re.search(r'A: "(.*?)" ; B: "(.*?)" ; (\d+) and (\d+) shingles, (\d+) shared, resemblance (\d+)/(\d+) = ([\d.]+) ; minima agree for (\d+) of 32 hash functions \(estimate ([\d.]+)\) ; agreement by function: ([01]+)', ln)
            d["widget"] = dict(A=m.group(1), B=m.group(2), na=m.group(3), nb=m.group(4), shared=m.group(5), inter=m.group(6), union=m.group(7), J=m.group(8),
                               agree=int(m.group(9)), est=m.group(10), bits=m.group(11))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def scurve_svg(d):
    bd = d["bands"]

    def draw(t, standalone):
        o = []
        W, H = 760, 340
        x0, x1, y0, y1 = 70, 720, 270, 60
        X = lambda v: x0 + v * (x1 - x0)
        Y = lambda p: y0 - p * (y0 - y1)
        o.append(C.text(20, 26, f"{bd['b']} bands of {bd['r']} hashes: the chance two documents become candidates, by their resemblance", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        for p in (0, 0.5, 1):
            o.append(C.text(x0 - 8, Y(p) + 4, f"{p:g}", t["muted"], 11.5, "end"))
        for v in (0, 0.2, 0.4, 0.6, 0.8, 1):
            o.append(C.text(X(v), y0 + 18, f"{v:g}", t["muted"], 11.5, "middle"))
        o.append(C.text((x0 + x1) / 2, y0 + 40, "resemblance J of the two documents", t["muted"], 12, "middle"))
        curve = [i / 100 for i in range(101)]
        o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(j):.1f},{Y(1 - (1 - j ** bd['r']) ** bd['b']):.1f}" for i, j in enumerate(curve)), t["blue"], "none", 2.4))
        for j, got, th in bd["pts"]:
            o.append(C.circle(X(j), Y(got), 5, t["red"]))
        o.append(C.line(X(0.56), Y(0.42) - 4, X(0.61), Y(0.42) - 4, t["blue"], 2.4))
        o.append(C.text(X(0.625), Y(0.42), "predicted: 1 − (1 − J⁴)³²", t["blue"], 12, "start", 700))
        o.append(C.circle(X(0.585), Y(0.31) - 4, 5, t["red"]))
        o.append(C.text(X(0.625), Y(0.31), "measured: 2,000 pairs each", t["red"], 12, "start", 700))
        return C.svg_doc(W, H, "".join(o), "The banding S-curve, measured and predicted", t, standalone, 0.55, 760)
    return draw


MH_HTML = """
<div class="board mh-board">
  <div style="min-width:0">
    <label class="mh-l" for="mh-a">Document A</label><textarea id="mh-a" rows="3"></textarea>
    <label class="mh-l" for="mh-b">Document B</label><textarea id="mh-b" rows="3"></textarea>
    <div class="mh-sh" id="mh-sh"></div>
  </div>
  <div style="min-width:0">
    <div class="mh-row"><button type="button" id="mh-reset">The program's two sentences</button></div>
    <div class="mh-bits" id="mh-bits" aria-label="Agreement of the 32 hash functions"></div>
    <div class="mh-stats" id="mh-stats"></div>
    <p class="say" id="mh-say" aria-live="polite"></p>
  </div>
</div>
"""

MH_CSS = """
.mh-l{display:block;font-size:12.5px;color:var(--muted);margin:6px 0 2px}
.mh-board textarea{width:100%;box-sizing:border-box;font:14px var(--body);padding:6px 8px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px;resize:vertical}
.mh-sh{display:flex;flex-wrap:wrap;gap:4px;margin-top:10px;font:12px var(--mono)}
.mh-sh span{padding:1px 6px;border:1px solid var(--axis);border-radius:2px;background:var(--surface)}
.mh-sh span.both{background:var(--yellow);color:var(--on-yellow);border-color:var(--yellow)}
.mh-sh span.a{border-color:var(--red);color:var(--red)} .mh-sh span.b{border-color:var(--blue);color:var(--blue)}
.mh-row{margin:6px 0}
.mh-bits{display:grid;grid-template-columns:repeat(16,minmax(0,1fr));gap:3px;margin:8px 0}
.mh-bits div{height:22px;background:var(--wash);border:1px solid var(--axis)}
.mh-bits div.on{background:var(--ink);border-color:var(--ink)}
.mh-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

MH_JS = r"""
(() => {
  const ta = document.getElementById("mh-a"), tb = document.getElementById("mh-b");
  if (!ta) return;
  const A0 = __A__, B0 = __B__, PROG = __PROG__;
  function fnv(s) { let h = 0x811c9dc5 | 0; for (const ch of s) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); } return h | 0; }
  function fmix(h) { h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16; return h >>> 0; }
  const words = s => s.trim().split(/\s+/).filter(Boolean);
  function shingles(s) { const w = words(s), m = new Map(); for (let i = 0; i + 1 < w.length; i++) { const t = w[i] + " " + w[i + 1]; m.set(fnv(t), t); } return m; }
  const hashI = (x, i) => fmix(x ^ Math.imul(i + 1, 0x9e3779b9 | 0));
  function draw() {
    const SA = shingles(ta.value), SB = shingles(tb.value);
    const both = [...SA.keys()].filter(k => SB.has(k)), uni = new Set([...SA.keys(), ...SB.keys()]);
    const sh = document.getElementById("mh-sh"); sh.innerHTML = "";
    for (const [k, t] of SA) el("span", {class: SB.has(k) ? "both" : "a"}, sh, t);
    for (const [k, t] of SB) if (!SA.has(k)) el("span", {class: "b"}, sh, t);
    const bits = document.getElementById("mh-bits"); bits.innerHTML = "";
    let agree = 0, pattern = "";
    for (let i = 0; i < 32; i++) {
      let ma = Infinity, mb = Infinity;
      for (const x of SA.keys()) ma = Math.min(ma, hashI(x, i));
      for (const x of SB.keys()) mb = Math.min(mb, hashI(x, i));
      const on = SA.size && SB.size && ma === mb; if (on) agree++; pattern += on ? "1" : "0";
      el("div", {class: on ? "on" : "", title: `hash ${i}: ${on ? "same" : "different"} minimum`}, bits);
    }
    const J = uni.size ? both.length / uni.size : 0;
    const st = document.getElementById("mh-stats"); st.innerHTML = "";
    el("div", {}, st, `shingles: A ${SA.size}, B ${SB.size}, shared ${both.length} (yellow)`);
    el("div", {}, st, `resemblance: ${both.length}/${uni.size} = ${J.toFixed(3)}`);
    el("div", {}, st, `minima agree: ${agree} of 32, estimate ${(agree / 32).toFixed(3)}`);
    const same = ta.value === A0 && tb.value === B0;
    document.getElementById("mh-say").textContent = same
      ? `The program's two sentences: it found the same ${PROG.agree} agreements, in the same places (${PROG.bits === pattern ? "pattern identical" : "pattern differs"}).`
      : "Edit either sentence: every shingle you change can change a minimum. With 32 hashes the estimate is typically within about 0.09 of the true resemblance.";
  }
  ta.addEventListener("input", draw); tb.addEventListener("input", draw);
  document.getElementById("mh-reset").addEventListener("click", () => { ta.value = A0; tb.value = B0; draw(); });
  ta.value = A0; tb.value = B0; draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How MinHash combined older ideas, and where it led")
    W = 210
    nodes = {
        "fp": (20, 20, "Fingerprints", "a short number for a long text", "Rabin; Karp–Rabin, Era 7", "ink"),
        "sh": (395, 20, "Shingles", "a document as its runs of w words", "Broder, 1997", "ink"),
        "jac": (770, 20, "Resemblance", "shared runs over all runs", "the Jaccard index", "ink"),
        "mh": (395, 180, "Min-wise samples", "⊕ keep the first shingle in a random order", "Broder, DEC SRC, 1997", "red"),
        "av": (20, 340, "AltaVista's crawl", "30 million pages clustered", "Broder and colleagues, 1997", "ink"),
        "lsh": (770, 340, "Locality-sensitive", "⊕ hashes where similar items collide", "Indyk and Motwani, 1998", "ink"),
        "today": (395, 490, "Near neighbours", "searching millions of points in high dimensions", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("fp", "mh", ports=("bottom", "top:0.15"))
    D.edge("sh", "mh", ports=("bottom", "top"))
    D.edge("jac", "mh", ports=("bottom", "top:0.85"))
    D.edge("mh", "av", ports=("bottom:0.15", "top"))
    D.edge("mh", "lsh", ports=("bottom:0.85", "top"), label="an instance of", at=0.45, dx=8, anchor="start")
    D.edge("lsh", "today", ports=("bottom", "right"))
    D.text(20, 615, "Near neighbours: the 2012 journal paper combining Indyk and Motwani's STOC 1998 and FOCS 2001 work.", "caption")
    return D


def chain(d):
    sr, es = d["search"], d["est"]
    k256 = es["rows"][-1]
    steps = [
        ("Exact fingerprints match only exact copies; a page with one word changed looks new",
         f"Shingles and resemblance: copies with 5% of words replaced still resemble at {d['docs']['rates'][0][1]}", "Broder, 1997"),
        ("Resemblance needs both full sets of shingles for every pair",
         f"A sketch of {k256[0]} minimum hashes: typical error {k256[2]}", "min-wise sampling"),
        (f"Still every pair: {sr['comp']} comparisons for {sr['n']} documents",
         f"Bands of hashes in hash tables: {sr['cand']} candidates, {sr['pct']}% of the similar pairs found", "locality-sensitive hashing"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from exact copies to near ones")
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
    ex, dc, es, bd, sr, wg = d["exact"], d["docs"], d["est"], d["bands"], d["search"], d["widget"]
    rate_rows = [[f"{p}%", r] for p, r in dc["rates"]]
    est_rows = [[k, b, e, t] for k, b, e, t in es["rows"]]
    band_rows = [[f"{j:.2f}", f"{g:.3f}", f"{t:.3f}"] for j, g, t in bd["pts"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Fingerprints (Era 7) give a long text a short number, but only exact copies share one. Broder cut documents into overlapping runs of words, measured how much two sets of runs overlap, and then sampled that overlap cheaply: the smallest shingle under a random order. Indyk and Motwani made hashing that puts similar things together into a general method for finding near neighbours. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: MinHash. Blue: where the idea led."),
        ]),
        dict(id="play", eyebrow="Try it", title="Two sentences, 32 minimum hashes", toc="Try it", blocks=[
            dict(type="p", text=f"Two sentences cut into shingles of two words: yellow ones are shared, red only in A, blue only in B. The resemblance is shared shingles over all shingles. Each of the 32 squares is one hash function: it is dark when the smallest hash of A's shingles equals the smallest hash of B's. The fraction of dark squares estimates the resemblance. With the program's sentences the widget computes the same hashes and finds the same {wg['agree']} agreements; edit the sentences and watch the squares change."),
            dict(type="widget", html=MH_HTML, js=MH_JS.replace("__A__", json.dumps(wg["A"])).replace("__B__", json.dumps(wg["B"])).replace("__PROG__", json.dumps(dict(agree=wg["agree"], bits=wg["bits"]))), css=MH_CSS,
                 fallback=dict(type="table", head=["", "Value"], num=[1], rows=[["Shingles in A, in B", f"{wg['na']}, {wg['nb']}"], ["Shared", wg["shared"]], ["Resemblance", f"{wg['inter']}/{wg['union']} = {wg['J']}"], ["Minima that agree (of 32)", str(wg["agree"])], ["Estimate", wg["est"]]]),
                 note="In the interactive edition you can edit both sentences and watch the 32 minima agree and disagree."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="The first shingle in a random order", toc="How it works", blocks=[
            dict(type="p", text="**Shingles and resemblance.** Cut a document into its overlapping runs of w words: \"a search engine\", \"search engine that\", and so on. Two documents resemble each other in proportion to the runs they share: resemblance J = |A ∩ B| / |A ∪ B|, from 0 (nothing shared) to 1 (the same set)."),
            dict(type="p", text="**The one-line proof.** Put every possible shingle in a random order and look at the first one, among all the shingles of A and B together. It is equally likely to be any member of the union. A and B have the same first shingle exactly when that member is in both, which happens with probability |A ∩ B| / |A ∪ B| = J. Repeat with k independent orders (in practice, k hash functions) and the fraction of agreements estimates J with an error of about √(J(1 − J)/k)."),
            dict(type="p", text="**Banding.** To find similar pairs without comparing all of them, cut each document's sketch into b bands of r hashes and put each band in a hash table. Two documents become candidates if any whole band matches, which happens with probability 1 − (1 − J^r)^b: close to 0 for unlike documents, close to 1 for similar ones, with a steep step between."),
            dict(type="svg", name="scurve", draw=scurve_svg(d), alt="Candidate rate against resemblance: measured points on the predicted S-curve", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Make the hash fit the question. An ordinary hash scatters near-copies; a minimum hash collides with exactly the probability that two documents resemble each other, so similarity turns into a lookup."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Near-copies of this book's field notes", toc="Measured", blocks=[
            dict(type="p", text=f"**The key fact, exactly.** For all {ex['pairs']} pairs of non-empty subsets of a 7-element universe and all {ex['orders']} orders of it, the minima agree in exactly the fraction |A ∩ B| / |A ∪ B| of the orders, as a fraction with no rounding."),
            dict(type="p", text=f"**Documents.** The field notes ({dc['words']} words) cut into {dc['pieces']} pieces of 40 words, each with 4 copies in which a share of the words was replaced at random: {dc['n']} documents, shingles of {dc['w']} words. Replacing a word spoils every shingle that contains it, so resemblance falls fast:"),
            dict(type="table", head=["Words replaced", "Average resemblance to the original"], num=[1], rows=rate_rows),
            dict(type="p", text=f"**MinHash estimates** over the {es['pairs']} pairs of a piece and its copies:"),
            dict(type="table", head=["Hash functions", "Bytes per document", "Typical error", "Theory √(J(1 − J)/k)"], num=[0, 1, 2, 3], rows=est_rows),
            dict(type="p", text=f"**Banding**, {bd['b']} bands of {bd['r']}, on 2,000 pairs of 200-element sets at each resemblance:"),
            dict(type="table", head=["Resemblance", "Became candidates", "1 − (1 − J⁴)³²"], num=[0, 1, 2], rows=band_rows),
            dict(type="p", text=f"**Finding every similar pair** among {sr['n']} documents. Comparing every pair took {sr['comp']} comparisons and found {sr['true']} pairs with resemblance at least 0.5. Banding the first 128 of the 256 hashes gave {sr['cand']} candidate pairs to check, and they included {sr['found']} of the {sr['true']} ({sr['pct']}%); {sr['false']} candidates turned out to be below 0.5."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Thirty million pages in Palo Alto", toc="The evidence", blocks=[
            dict(type="p", text="Broder (Digital Systems Research Center, Palo Alto), \"On the resemblance and containment of documents\" (Compression and Complexity of Sequences, 1997): resemblance |S(A,w) ∩ S(B,w)| / |S(A,w) ∪ S(B,w)|; under a random permutation the smallest element of the union lies in both sets with probability equal to the resemblance; \"100 samples seems reasonable and 200 seems more than enough\", with sketches of 300 to 800 bytes. With Glassman, Manasse and Zweig (SRC Technical Note 1997-015) he clustered \"a collection of over 30,000,000 documents\" from an AltaVista Web walk of April 1996, about 150 GB, at 50% resemblance: 3.6 million clusters holding 12.3 million documents, in about 10.5 CPU-days."),
            dict(type="p", text="Wikipedia: MinHash \"was published by Andrei Broder in a 1997 conference\" and \"initially used in the AltaVista search engine to detect duplicate web pages\"; \"The probability that hmin(A) = hmin(B) is true is equal to the similarity J(A,B)\"; with k hash functions \"its expected error is O(1/√k)\". Har-Peled, Indyk and Motwani (*Theory of Computing*, 2012), \"based on the material from the authors' STOC'98 and FOCS'01 papers\": approximate nearest neighbours in high dimensions with query times \"sub-linear\" in the data."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Fingerprints that tolerate change", toc="Full circle", blocks=[
            dict(type="p", text="Karp and Rabin's fingerprints (Era 7) were built so that different texts almost never collide. MinHash is built so that similar texts collide often. Both are hashing; the difference is what a collision should mean. Genome assembly (topic 9) cuts reads into k-letter words just as Broder cut documents into shingles."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Comparing every pair of {sr['n']} documents took {sr['comp']} comparisons. Bands of minimum hashes proposed {sr['cand']}, and {sr['pct']}% of the similar pairs were among them."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A = {1, 2, 3, 4}, B = {3, 4, 5}. What is the resemblance?", "Shared {3, 4}, union {1, 2, 3, 4, 5}: 2/5 = 0.4."),
            ("Why can changing one word of a 40-word piece remove up to 4 of its 4-word shingles?", "Every shingle that contains the word changes, and with w = 4 up to four shingles contain it."),
            ("With 100 hash functions and J = 0.5, about how far off is the estimate?", "√(0.5 × 0.5 / 100) = 0.05."),
            ("With 32 bands of 4, what is the chance a pair with J = 0.5 becomes a candidate?", "1 − (1 − 0.5⁴)³² = 1 − (15/16)³² ≈ 0.87; the program measured 0.877."),
            ("Why does banding miss some similar pairs and propose some dissimilar ones?", "The S-curve is steep but not a step: near the threshold the chance is neither 0 nor 1."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Syntactic Clustering of the Web (1997)", text="SRC Technical Note 1997-015: 30 million pages from AltaVista, clustered by resemblance.",
                 draw=C.draw_manuscript, link="https://archives.iw3c2.org/www2010/pubs/77977/src-tn-1997-015.pdf", link_text="The technical note (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MinHashLsh", d["checks"],
                           "the minima's agreement against the resemblance for every pair of subsets and every order of a 7-element universe, the error for 16 to 256 hashes, the banding curve, and every similar pair found by LSH coming from the same piece.",
                           ["static long[] sketch(long[] set, int k)"]),
    ]
    return dict(
        title="MinHash and Locality-Sensitive Hashing", date="1997–1998",
        description="Era 8, topic 5 of The Algorithm Evolution Atlas: Broder's MinHash (DEC SRC, 1997) for near-duplicate web pages, and banding for locality-sensitive hashing, tested on near-copies of this book's own field notes.",
        lede="A search engine finds that millions of its pages are near-copies of each other, and exact fingerprints cannot see it. Broder measured resemblance by shared runs of words and estimated it from a few hundred minimum hashes, one random order at a time.",
        fieldnote=f"I copied pieces of my own notes and spoiled a few words in each. With 256 minimum hashes per piece I could tell how alike any two were to within {es['rows'][-1][2]}, and by banding the hashes I found {sr['pct']}% of the near-copies while checking {sr['cand']} pairs instead of {sr['comp']}.",
        card=[("When", "1997 (MinHash); 1998 (locality-sensitive hashing)"),
              ("Where", "Digital Systems Research Center, Palo Alto; Stanford"),
              ("What hurt", "Near-duplicates among millions of pages; n² comparisons"),
              ("The fix", "Minimum hashes estimate resemblance; bands make similar pages collide"),
              ("Checked", f"Exactly, on all {ex['pairs']} subset pairs; {sr['pct']}% of similar pairs found")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MinHashLsh.java`.",
    )
