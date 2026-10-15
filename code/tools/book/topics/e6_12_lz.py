"""Era 6, topic 12: universal compression (Lempel and Ziv). Every number is parsed from LempelZiv.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"small: \"(.*?)\" \((\d+) letters, _ is a space\) ; LZ77 sends (\d+) triples .*?: ((?:\(\d+,\d+,.\) ?)+) ; LZ78 sends (\d+) pairs .*?: (.*)$", ln):
            d["small"] = dict(text=m.group(1), n=m.group(2), n77=m.group(3), t77=re.findall(r"\((\d+),(\d+),(.)\)", m.group(4)),
                              n78=m.group(5), t78=re.findall(r"\((\d+),(.)\)=(\S+)", m.group(6)))
        elif m := re.match(r"trips: ([\d,]+) random strings .*? field notes \(([\d,]+) bytes\)", ln):
            d["trips"] = dict(n=m.group(1), bytes=m.group(2))
        elif m := re.match(r"notes: the field notes as ([\d,]+) bytes of 8 bits ; Huffman's code for single bytes ([\d.]+) bits per byte ; LZ77 .*?: ([\d,]+) triples, ([\d.]+) bits per byte ; LZ78: ([\d,]+) pairs \(phrase number growing from 1 to (\d+) bits, plus 8\), ([\d.]+) bits per byte", ln):
            d["notes"] = dict(bytes=m.group(1), huff=m.group(2), n77=m.group(3), b77=m.group(4), n78=m.group(5), maxbits=m.group(6), b78=m.group(7))
        elif m := re.match(r"repeat: the first ([\d,]+) bytes of the notes, repeated (\d+) times \(([\d,]+) bytes\) ; Huffman's code for single bytes ([\d.]+) bits per byte, .*?: ([\d,]+) triples, ([\d.]+) bits per byte ; LZ78: ([\d,]+) pairs, ([\d.]+) bits per byte", ln):
            d["rep"] = dict(block=m.group(1), times=m.group(2), total=m.group(3), huff=m.group(4), n77=m.group(5), b77=m.group(6), n78=m.group(7), b78=m.group(8))
        elif m := re.match(r"universal: .*? with probability ([\d.]+) ; .*? cannot beat ([\d.]+) bits per symbol ; .*? entropy rate, from Era 4's Shannon\) is ([\d.]+) ; LZ78, told nothing about the source, bits per symbol: (.*?) ; still falling", ln):
            d["uni"] = dict(stay=m.group(1), h0=m.group(2), h=m.group(3), rows=re.findall(r"([\d,]+) symbols: ([\d.]+)", m.group(4)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def trie_svg(d):
    pairs = d["small"]["t78"]

    def draw(t, standalone):
        # build the phrase tree: node k (1-based) is the child of node `phrase` by letter `next`
        kids = {0: []}
        label = {0: "∅"}
        for k, (ph, ch, word) in enumerate(pairs, 1):
            kids.setdefault(int(ph), []).append(k)
            kids[k] = kids.get(k, [])
            label[k] = (ch if ch != "_" else "␣", word)
        pos, leaves = {}, [0]

        def place(v, depth):
            if not kids.get(v):
                pos[v] = (leaves[0], depth)
                leaves[0] += 1
                return pos[v][0]
            xs = [place(c, depth + 1) for c in kids[v]]
            pos[v] = ((min(xs) + max(xs)) / 2, depth)
            return pos[v][0]
        place(0, 0)
        n_leaf = leaves[0]
        depth = max(p[1] for p in pos.values())
        W = 780
        sx = (W - 80) / max(1, n_leaf - 1)
        H = 60 + depth * 78 + 60
        X = lambda v: 40 + pos[v][0] * sx
        Y = lambda v: 50 + pos[v][1] * 78
        o = [C.text(20, 22, f"LZ78's dictionary after \"{d['small']['text']}\": each phrase is an earlier phrase plus one letter", t["ink"], 13, "start", 700)]
        for v, cs in kids.items():
            for c in cs:
                o.append(C.line(X(v), Y(v) + 16, X(c), Y(c) - 16, t["axis"], 1.4))
                o.append(C.text(X(v) + (X(c) - X(v)) * 0.55 - 10, Y(v) + (Y(c) - Y(v)) * 0.55 + 2, label[c][0], t["red"], 13, "end", 700))
        for v in pos:
            o.append(C.circle(X(v), Y(v), 16, t["surface"], t["blue"] if v else t["ink2"], 1.6))
            o.append(C.text(X(v), Y(v) + 5, str(v) if v else "0", t["ink"], 12, "middle", 700))
            if v:
                o.append(C.text(X(v) + 20, Y(v) + 4, "“" + label[v][1].replace("_", "␣") + "”", t["muted"], 11, "start"))
        o.append(C.text(20, H - 10, "Red: the letter that extends the phrase. Beside each node: the phrase it stands for. The pair (6, r) means phrase 6 then r: \"abr\".", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "LZ78's phrase dictionary as a tree", t, standalone, 0.55, 780)
    return draw


LZ_HTML = """
<div class="board lz-board">
  <div style="min-width:0">
    <label class="lz-row">Text <input type="text" id="lz-text" maxlength="80"></label>
    <div class="lz-view" id="lz-view"></div>
    <div class="lz-toks" id="lz-toks"></div>
  </div>
  <div style="min-width:0">
    <div class="lz-btns"><button type="button" id="lz-step">Step</button><button type="button" id="lz-run">Run to the end</button><button type="button" id="lz-reset">Start again</button></div>
    <div class="lz-stats" id="lz-stats"></div>
    <p class="say" id="lz-say" aria-live="polite"></p>
  </div>
</div>
"""

LZ_CSS = """
.lz-row{display:grid;gap:2px;font-size:14px}
.lz-row input{font:14px var(--mono);width:100%}
.lz-view{font:16px var(--mono);margin:10px 0;word-break:break-all;line-height:1.7}
.lz-view span.done{color:var(--muted)}
.lz-view span.src{background:var(--blue);color:var(--on-blue)}
.lz-view span.cur{background:var(--yellow);color:var(--on-yellow)}
.lz-view span.nx{background:var(--red);color:var(--on-red)}
.lz-toks{font:12.5px var(--mono);display:flex;flex-wrap:wrap;gap:4px}
.lz-toks span{border:1px solid var(--rule);padding:1px 4px;border-radius:3px}
.lz-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.lz-stats{font:13px var(--mono);display:grid;gap:3px}
"""

LZ_JS = r"""
(() => {
  const view = document.getElementById("lz-view");
  if (!view) return;
  document.getElementById("lz-text").value = __TEXT__;
  let s, toks, k;
  function encode() {
    s = document.getElementById("lz-text").value; toks = [];
    let i = 0;
    while (i < s.length) {
      let best = 0, back = 0;
      for (let j = Math.max(0, i - 4096); j < i; j++) { let q = 0; while (q < 255 && i + q < s.length - 1 && s[j + q] === s[i + q]) q++; if (q > best) { best = q; back = i - j; } }
      toks.push({at: i, back, len: best, next: s[i + best]});
      i += best + 1;
    }
    k = 0; show();
  }
  function show() {
    view.innerHTML = "";
    const t = k > 0 ? toks[k - 1] : null;
    [...s].forEach((ch, i) => {
      let cls = "";
      if (t) {
        if (i >= t.at && i < t.at + t.len) cls = "cur";
        else if (i === t.at + t.len) cls = "nx";
        else if (t.len && i >= t.at - t.back && i < t.at - t.back + t.len) cls = "src";
        else if (i < t.at) cls = "done";
      }
      el("span", {class: cls}, view, ch === " " ? "␣" : ch);
    });
    const tb = document.getElementById("lz-toks"); tb.innerHTML = "";
    toks.slice(0, k).forEach(x => el("span", {}, tb, `(${x.back},${x.len},${x.next === " " ? "␣" : x.next})`));
    const st = document.getElementById("lz-stats"); st.innerHTML = "";
    el("div", {}, st, `${s.length} letters, ${toks.length} triples in all`);
    el("div", {}, st, `at 28 bits a triple: ${toks.length * 28} bits, against ${s.length * 8} at 8 bits a letter`);
    document.getElementById("lz-say").textContent = !t ? "Step through: each triple says how far back to look, how many letters to copy, and the next letter." :
      t.len ? `Copy ${t.len} letter${t.len > 1 ? "s" : ""} from ${t.back} back (blue to yellow), then add ${t.next === " " ? "a space" : "“" + t.next + "”"} (red).` + (t.back < t.len ? " The copy overlaps itself: each letter copied becomes the source of a later one." : "") :
      `Nothing to copy: send the letter ${t.next === " " ? "space" : "“" + t.next + "”"} itself.`;
  }
  document.getElementById("lz-step").addEventListener("click", () => { if (k < toks.length) k++; show(); });
  document.getElementById("lz-run").addEventListener("click", () => { k = toks.length; show(); });
  document.getElementById("lz-reset").addEventListener("click", () => { k = 0; show(); });
  document.getElementById("lz-text").addEventListener("input", encode);
  encode();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Lempel and Ziv's compression combined older ideas, and where it led")
    W = 210
    nodes = {
        "sh": (20, 20, "Entropy", "the best average for a known source", "Shannon, Era 4", "ink"),
        "hf": (395, 20, "Huffman's code", "optimal, letter by letter, if told the odds", "Era 5, topic 3", "ink"),
        "ss": (770, 20, "Finding repeats", "the longest match in a window", "topic 11", "ink"),
        "lz77": (20, 180, "LZ77", "⊕ a pointer into what was already sent", "Ziv and Lempel, 1977", "red"),
        "lz78": (770, 180, "LZ78", "⊕ a dictionary of phrases, grown as it goes", "1978", "red"),
        "lzw": (770, 340, "LZW", "a faster form of the dictionary method", "Welch, 1984", "ink"),
        "zip": (20, 340, "Compression programs", "Unix compress; WinZip, gzip", "1980s and 1990s", "ink"),
        "img": (395, 340, "Image formats", "GIF, TIFF and others", "", "ink"),
        "today": (395, 490, "Today", "compressed files, images and Internet traffic", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("sh", "lz77", ports=("bottom", "top"), label="the target", at=0.5, dx=-8, anchor="end")
    D.edge("hf", "lz77", ports=("bottom:0.2", "top:0.8"), dashed=True)
    D.edge("ss", "lz77", ports=("bottom:0.2", "right"), dashed=True)
    D.edge("lz77", "lz78", ports=("right", "left"), label="a year later", at=0.5, dy=-8)
    D.edge("lz78", "lzw", ports=("bottom", "top"))
    D.edge("lz77", "zip", ports=("bottom", "top"))
    D.edge("lzw", "img", ports=("left", "right"))
    D.edge("img", "today", ports=("bottom", "top"))
    D.edge("zip", "today", ports=("bottom", "left"))
    D.text(20, 615, "Uses as given by IEEE Spectrum (2023) and the IEEE Milestone. Dashed: related ideas, not sources the papers name.", "caption")
    return D


def chain(d):
    r, u, n = d["rep"], d["uni"], d["notes"]
    steps = [
        (f"A text that repeats itself: Huffman's code still needs {r['huff']} bits per byte, letter by letter",
         f"LZ77 sends pointers to earlier copies: {r['b77']} bits per byte", "Ziv and Lempel, 1977"),
        (f"Codes need the source's odds; coded symbol by symbol, this source cannot beat {u['h0']} bits",
         f"LZ78, told nothing, approaches the source's rate ({u['h']}): {u['rows'][-1][1]} at {u['rows'][-1][0]} symbols", "1978: universal"),
        (f"On a short text, the field notes, LZ77 ({n['b77']}) and LZ78 ({n['b78']}) lose to Huffman ({n['huff']})",
         "The promise is for long inputs: the phrases must have time to grow", "measured here"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from known odds to no odds at all")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx = (L, R) if i % 2 == 0 else (R, L)
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx, y, bw, rowh, [("THE FIX" if i < 2 else "WHAT IT SHOWED", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="fixed by" if i < 2 else "and", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    sm, tr, n, r, u = d["small"], d["trips"], d["notes"], d["rep"], d["uni"]
    t77_rows = [[b, l, ch.replace("_", "(space)")] for b, l, ch in sm["t77"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Shannon had said how few bits a source needs on average (Era 4); Huffman had built the best code for single letters, if told how often each occurs (Era 5). Ziv and Lempel asked for a code that is told nothing, and found one that refers back to what it has already sent. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the two methods of 1977 and 1978. Blue: where they went."),
        ]),
        dict(id="play", eyebrow="Try it", title="Copy from what was sent", toc="Try it", blocks=[
            dict(type="p", text="LZ77 on a text of your choice (the program's example is loaded). Each step sends a triple: how far back to look, how many letters to copy, and the next letter. Blue is the earlier copy, yellow the letters it stands for, red the new letter. Try a text that repeats itself many times."),
            dict(type="widget", html=LZ_HTML, js=LZ_JS.replace("__TEXT__", f'"{sm["text"]}"'), css=LZ_CSS,
                 fallback=dict(type="table", head=["How far back", "How long", "Next letter"], num=[0, 1], rows=t77_rows),
                 note=f"In the interactive edition you can step through LZ77 on your own text. The table: the program's {sm['n77']} triples for \"{sm['text']}\"."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Refer to the past", toc="How it works", blocks=[
            dict(type="p", text="**LZ77.** Keep the last W letters already sent (the window). At each step find the longest string, starting at the current letter, that also starts somewhere in the window, and send three things: how far back it starts, how long it is, and the letter after it. The receiver copies from what it already has. The copy may overlap itself, so a run of one letter repeated a hundred times costs one triple."),
            dict(type="p", text=f"**LZ78.** Build a dictionary of phrases. At each step find the longest phrase in the dictionary that matches what comes next, send its number and the next letter, and add that phrase plus the letter as a new entry. On \"{sm['text']}\" the program sent {sm['n78']} pairs:"),
            dict(type="svg", name="trie", draw=trie_svg(d), alt="LZ78's phrase dictionary as a tree", width=780),
            dict(type="p", text="**Why it is universal.** Neither method knows anything about the source. But anything that recurs, at any distance, is sent as a reference, and the longer the input runs, the longer the phrases grow and the fewer bits each letter costs. Ziv and Lempel proved that for long inputs the rate approaches the best any code designed for the source could achieve."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Don't model the data; let the data be its own dictionary. Whatever has been seen before can be named instead of spelled out."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Bits per letter", toc="Measured", blocks=[
            dict(type="p", text=f"**Round trips.** {tr['n']} random strings and this book's field notes ({tr['bytes']} bytes) were encoded and decoded by both methods; every one came back exactly."),
            dict(type="table", head=["Input", "Huffman, single bytes", "LZ77", "LZ78"], num=[1, 2, 3], rows=[
                [f"The field notes ({n['bytes']} bytes)", n["huff"], n["b77"], n["b78"]],
                [f"The first {r['block']} bytes, repeated {r['times']} times", r["huff"], r["b77"], r["b78"]]], hl=1),
            dict(type="p", text=f"Bits per byte. On the field notes, LZ77 sent {n['n77']} triples of 24 bits and LZ78 {n['n78']} pairs whose phrase numbers grew to {n['maxbits']} bits; on a text this short, Huffman's code for single bytes still wins. On the repeated text, Huffman's rate is exactly what it is for one copy, since the bytes' frequencies do not change; LZ77 sent {r['n77']} triples, and LZ78's phrases grew longer with every copy ({r['n78']} pairs)."),
            dict(type="p", text=f"**Universality.** A source of 0s and 1s that repeats its last symbol with probability {u['stay']}: 0s and 1s are equally common, so coding symbols one at a time cannot beat {u['h0']} bits per symbol, but the source's entropy rate (Shannon, Era 4) is {u['h']}. LZ78, told nothing about the source:"),
            dict(type="table", head=["Symbols coded", "LZ78 bits per symbol"], num=[0, 1], rows=[list(x) for x in u["rows"]], hl=len(u["rows"]) - 1),
            dict(type="p", text=f"Still falling towards {u['h']}: universality is a promise about long inputs, and here it is kept slowly."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two colleagues in Haifa", toc="The evidence", blocks=[
            dict(type="p", text="Ziv and Lempel, \"A Universal Algorithm for Sequential Data Compression\" (*IEEE Transactions on Information Theory* IT-23(3), May 1977; received 23 June 1975), both of the Technion, Haifa: \"A universal algorithm for sequential data compression is presented\"; its compression ratio \"uniformly approaches the lower bounds on the compression ratios attainable by block-to-variable codes and variable-to-block codes designed to match a completely specified source\". The encoder sends \"the pointer of the reproduction\", a length, and the last symbol. The dictionary method followed in \"Compression of Individual Sequences via Variable-Rate Coding\" (IT-24(5), September 1978)."),
            dict(type="p", text="IEEE Spectrum (Amanda Davis, 2023): Ziv, who \"died on 26 March at the age of 91\", published the first method with Lempel in 1977 while on sabbatical at Bell Labs; it led to Unix compression programs in the early 1980s and to WinZip and Gzip in the early 1990s, and the methods \"are used today in GIF, TIFF and other image formats\". The IEEE Milestone in Haifa (2004) says the algorithm \"contributed significantly in making the internet a global communications medium\". Lempel taught at the Technion from 1963 to 2004 and died in 2023."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Shannon's limit, reached without the odds", toc="Full circle", blocks=[
            dict(type="p", text="Shannon showed in 1948 how few bits a source needs, given its statistics (Era 4, topic 12); Huffman built the best code for single letters, given their frequencies (Era 5, topic 3). Lempel and Ziv reached towards Shannon's limit without being given anything, by letting the data describe themselves. And at its core LZ77 is a string search (topic 11): for every position, the longest match in the window."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"On a source whose entropy rate is {u['h']} bits per symbol, LZ78 reached {u['rows'][-1][1]} after {u['rows'][-1][0]} symbols, without ever being told the source's rule."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Encode aaaaaaaa (8 letters) with LZ77.", "(0,0,a), then (1,6,a): copy 6 letters from 1 back, overlapping itself, then one more a."),
            ("Encode abab with LZ78.", "(0,a)=a, (0,b)=b, (1,b)=ab: three pairs."),
            ("Why can't Huffman's code see that a text repeats itself?", "It codes each letter by its frequency alone; a repeated block has the same frequencies as a single copy."),
            ("Why does LZ78 do badly on short texts?", "Its phrases are still short, and every pair carries a phrase number as well as a letter."),
            ("What does \"universal\" promise, and what does it not?", "That for long enough inputs the rate approaches the best possible for the source; not that it wins on any particular short text."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Universal Algorithm for Sequential Data Compression (1977)", text="Ziv and Lempel's paper, *IEEE Transactions on Information Theory* IT-23(3).",
                 draw=C.draw_manuscript, link="https://www.icst.pku.edu.cn/mipl/docs/ziv1977.pdf", link_text="The paper (PDF, on a Peking University page)", licence="Drawn placeholder."),
            dict(title="IEEE Milestone: Lempel-Ziv Data Compression Algorithm, 1977", text="Dedicated in Haifa on 6 September 2004.",
                 draw=C.draw_book, link="https://ethw.org/Milestones:Lempel-Ziv_Data_Compression_Algorithm,_1977", link_text="Engineering and Technology History Wiki", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LempelZiv", d["checks"],
                           "both methods on a short string, round trips on 2,000 random strings and on the field notes, bits per byte against Huffman's code, a repeated text, and LZ78's rate on a source with memory from 1,000 to 10,000,000 symbols.",
                           ["static List<Triple> lz77(String s, int window, int maxLen)", "static List<Pair> lz78(String s)"]),
    ]
    return dict(
        title="Universal Compression", date="1977–1978",
        description="Era 6, topic 12 of The Algorithm Evolution Atlas: Ziv and Lempel's LZ77 and LZ78, compression that refers to what was already sent and approaches the entropy rate without a model.",
        lede="Huffman's code is the best possible for single letters, if someone tells it the odds. Ziv and Lempel built codes that are told nothing, refer back to what they have already sent, and on long inputs do as well as any code made for the source.",
        fieldnote=f"Fifty copies of the same thousand bytes: Huffman's code needed {r['huff']} bits a byte, exactly as for one copy, while LZ77 needed {r['b77']}. On a source with memory LZ78 crept down towards its entropy rate, {u['h']}, never having been told what it was.",
        card=[("When", "1977 and 1978"),
              ("Where", "Technion, Haifa (and Bell Labs, on sabbatical)"),
              ("What hurt", "Good codes needed the source's statistics"),
              ("The fix", "Pointers to the past; a growing dictionary"),
              ("Measured", f"{r['b77']} bits per byte on repeated text, against {r['huff']}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LempelZiv.java`.",
    )
