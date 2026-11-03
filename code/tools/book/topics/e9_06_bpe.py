"""Era 9, topic 6: Byte-pair encoding for words. Every number is parsed from BytePairEncoding.java's output."""
import re

import common as C
from diagrams import Diagram

DOT = "·"


def unesc(s):
    return re.sub(r"\\u\{([0-9a-f]+)\}", lambda m: chr(int(m.group(1), 16)), s)


def dot(s):
    return s.replace("_", DOT)


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("gage: "):
            parts = ln.split(" ; ")
            d["gage"] = dict(steps=parts[0][6:].split(" -> "), table=parts[1][6:], counts=parts[2].split(": ", 1)[1],
                             sizes=re.search(r"(\d+) symbols down to (\d+)", ln).groups())
        elif ln.startswith("figure: "):
            parts = ln.split(" ; ")
            d["figure"] = dict(paper=[dot(p) for p in re.findall(r"(?:when made: )?([\w_]+ [\w_]+) \(count \d+, tied with \d+ other pairs\)", ln)],
                               ties=re.findall(r"tied with (\d+) other pairs", ln),
                               after=dot(re.search(r"the words afterwards: (.*?) ; this program", ln).group(1)),
                               mine=dot(re.search(r"seen first: (.*)$", ln).group(1)))
        elif m := re.match(r"corpus: 20,000 sentences, ([\d,]+) words, ([\d,]+) distinct, (\d+) letters plus the end symbol ; (\d+) stems.*?: (\d+) words never seen, such as (.*)$", ln):
            d["corpus"] = m.groups()
        elif ln.startswith("merges: "):
            d["merges"] = [dot(x).replace("+", " + ") for x in ln.split(": ", 1)[1].split(", ")]
        elif ln.startswith("growth: "):
            d["growth"] = re.findall(r"(\d+) merges: ([\d.]+) symbols per word, vocabulary (\d+)", ln)
            d["whole"] = re.search(r"needs a vocabulary of (\d+)", ln).group(1)
        elif ln.startswith("unseen: "):
            m = re.match(r"unseen: after (\d+) merges, the (\d+) held-out words in ([\d.]+) pieces each ; cut exactly where stem meets ending: (\d+) of (\d+) ; (.*)$", ln)
            d["unseen"] = dict(K=m.group(1), n=m.group(2), pieces=m.group(3), cut=m.group(4),
                               ex=[(w, [dot(p) for p in seg.split(" + ")]) for w, seg in (e.split(" = ") for e in m.group(6).split(" ; "))])
        elif ln.startswith("bytes: "):
            d["bytes"] = [(unesc(t), u, b, k) for t, u, b, k in re.findall(r"\"(.*?)\": (\d+) unknown letters, (\d+) UTF-8 bytes in (\d+) byte tokens", ln)]
            d["letters"] = re.search(r"letter vocabulary of (\d+) letters", ln).group(1)
            d["exact"] = re.search(r"decoded exactly from bytes: (\d+) of (\d+)", ln).groups()
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def unseen_svg(d):
    u = d["unseen"]

    def draw(t, standalone):
        W = 760
        H = 70 + 34 * len(u["ex"]) + 30
        o = [C.text(20, 26, f"Words the program never saw, cut into pieces after {u['K']} merges", t["ink"], 13, "start", 700)]
        for i, (w, seg) in enumerate(u["ex"]):
            y = 50 + i * 34
            o.append(C.text(30, y + 18, w, t["ink"], 13, "start", 700))
            x = 170
            for k, p in enumerate(seg):
                wpx = 14 + 9 * len(p)
                o.append(C.rect(x, y, wpx, 26, t["paper"], t["blue"] if k % 2 == 0 else t["red"], 2, 3))
                o.append(C.text(x + wpx / 2, y + 18, p, t["ink"], 13, "middle"))
                x += wpx + 8
        o.append(C.text(20, H - 12, f"Each piece is a symbol learned from other words; {DOT} marks the end of a word. {u['cut']} of {u['n']} unseen words were cut exactly where stem meets ending.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Unseen words segmented into learned pieces", t, standalone, 0.55, 760)
    return draw


BPE_HTML = """
<div class="board bpe-board">
  <div style="min-width:0">
    <label class="bpe-lab" for="bpe-text">Training text (edit it)</label>
    <textarea id="bpe-text" rows="4" spellcheck="false"></textarea>
    <div class="bpe-btns"><button type="button" class="primary" id="bpe-step">Merge once</button><button type="button" id="bpe-ten">Merge 10 times</button><button type="button" id="bpe-reset">Start over</button></div>
    <div class="bpe-words" id="bpe-words"></div>
  </div>
  <div style="min-width:0">
    <div class="bpe-h">Most frequent pairs now</div><div class="bpe-pairs" id="bpe-pairs"></div>
    <div class="bpe-h">Merges so far</div><div class="bpe-merges" id="bpe-merges"></div>
    <label class="bpe-lab" for="bpe-test">Cut a new word with these merges</label>
    <input id="bpe-test" type="text" value="oldest" spellcheck="false">
    <div class="bpe-words" id="bpe-out"></div>
    <p class="say" id="bpe-say" aria-live="polite"></p>
  </div>
</div>
"""

BPE_CSS = """
.bpe-board{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.bpe-board{grid-template-columns:1fr}}
.bpe-board textarea,.bpe-board input[type=text]{width:100%;box-sizing:border-box;font:13px var(--mono);padding:6px;background:var(--paper);color:var(--ink);border:1px solid var(--rule)}
.bpe-lab,.bpe-h{display:block;font-size:12px;font-weight:700;margin:8px 0 4px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
.bpe-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.bpe-words{display:flex;flex-wrap:wrap;gap:6px 12px;font:13px var(--mono);margin:6px 0}
.bpe-w{display:inline-flex;gap:2px;align-items:center}
.bpe-w i{font-style:normal;color:var(--muted);font-size:11px;margin-left:3px}
.bpe-t{border:1.5px solid var(--blue);border-radius:3px;padding:1px 4px;background:var(--paper)}
.bpe-t.alt{border-color:var(--red)}
.bpe-t.new{background:var(--yellow);color:#111}
.bpe-pairs,.bpe-merges{font:12.5px var(--mono);display:grid;gap:2px}
.bpe-merges{max-height:9em;overflow:auto}
"""

BPE_JS = r"""
(() => {
  const ta = document.getElementById("bpe-text");
  if (!ta) return;
  const END = "·", DEF = "low low low lower lowest lowest new new newer newest newest wide wider wider widest slow slower slowest old older";
  let vocab, merges, last;
  const pairKey = (a, b) => a + "\u0001" + b;
  function reset() {
    vocab = new Map(); merges = []; last = null;
    ta.value.toLowerCase().split(/\s+/).filter(Boolean).forEach(w => { const k = [...w, END].join(" "); vocab.set(k, (vocab.get(k) || 0) + 1); });
  }
  function counts() {
    const c = new Map();
    vocab.forEach((n, k) => { const s = k.split(" "); for (let i = 0; i + 1 < s.length; i++) { const p = pairKey(s[i], s[i + 1]); c.set(p, (c.get(p) || 0) + n); } });
    return [...c.entries()].sort((a, b) => b[1] - a[1]);
  }
  function apply(syms, a, b) {
    const out = [];
    for (let i = 0; i < syms.length; i++) { if (i + 1 < syms.length && syms[i] === a && syms[i + 1] === b) { out.push(a + b); i++; } else out.push(syms[i]); }
    return out;
  }
  function step() {
    const c = counts();
    if (!c.length || c[0][1] < 1) return false;
    const [a, b] = c[0][0].split("\u0001");
    merges.push([a, b, c[0][1]]); last = a + b;
    const nv = new Map();
    vocab.forEach((n, k) => { const s = apply(k.split(" "), a, b).join(" "); nv.set(s, (nv.get(s) || 0) + n); });
    vocab = nv; return true;
  }
  function segment(word) {
    let s = [...word.toLowerCase(), END];
    const rank = new Map(merges.map(([a, b], i) => [pairKey(a, b), i]));
    for (;;) {
      let best = -1, br = Infinity;
      for (let i = 0; i + 1 < s.length; i++) { const r = rank.get(pairKey(s[i], s[i + 1])); if (r !== undefined && r < br) { br = r; best = i; } }
      if (best < 0) return s;
      s = apply(s, s[best], s[best + 1]);
    }
  }
  function chips(parent, syms, n) {
    const w = el("span", {class: "bpe-w"}, parent);
    syms.forEach((p, k) => el("span", {class: "bpe-t" + (k % 2 ? " alt" : "") + (p === last ? " new" : "")}, w, p));
    if (n !== undefined) el("i", {}, w, "×" + n);
  }
  function draw() {
    const W = document.getElementById("bpe-words"); W.innerHTML = "";
    let total = 0, syms = 0;
    vocab.forEach((n, k) => { chips(W, k.split(" "), n); total += n; syms += n * k.split(" ").length; });
    const P = document.getElementById("bpe-pairs"); P.innerHTML = "";
    counts().slice(0, 5).forEach(([k, n], i) => el("div", {}, P, `${i === 0 ? "▶" : " "} ${k.split("\u0001").join(" + ").padEnd(14)} ${n}`));
    const M = document.getElementById("bpe-merges"); M.innerHTML = "";
    merges.forEach(([a, b, n], i) => el("div", {}, M, `${String(i + 1).padStart(2)}. ${a} + ${b} → ${a + b}   (${n})`));
    if (!merges.length) el("div", {}, M, "none yet");
    const O = document.getElementById("bpe-out"); O.innerHTML = "";
    const tw = document.getElementById("bpe-test").value.trim().split(/\s+/)[0] || "";
    if (tw) chips(O, segment(tw));
    const sym = new Set(); vocab.forEach((n, k) => k.split(" ").forEach(s => sym.add(s)));
    document.getElementById("bpe-say").textContent = `${merges.length} merges. The text is ${syms} symbols for ${total} words (${(syms / total).toFixed(2)} per word). Yellow marks the symbol just made.`;
  }
  document.getElementById("bpe-step").addEventListener("click", () => { step(); draw(); });
  document.getElementById("bpe-ten").addEventListener("click", () => { for (let k = 0; k < 10 && step(); k++); draw(); });
  document.getElementById("bpe-reset").addEventListener("click", () => { reset(); draw(); });
  ta.addEventListener("change", () => { reset(); draw(); });
  document.getElementById("bpe-test").addEventListener("input", draw);
  ta.value = DEF; reset(); draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How subword units combined older ideas, and where they led")
    W = 250
    nodes = {
        "gage": (40, 20, "Gage's byte-pair encoding", "replace the most frequent pair, again and again", "The C Users Journal, 1994", "ink"),
        "nmt": (375, 20, "Neural translation", "a fixed vocabulary of whole words", "", "ink"),
        "w2v": (710, 20, "Word vectors", "a row of numbers for every symbol", "topic 3, 2013", "ink"),
        "sub": (375, 200, "Subword units", "⊕ merges learned on letters; any word can be spelled", "Sennrich, Haddow and Birch, Edinburgh, 2015", "red"),
        "byte": (40, 380, "Byte-level BPE", "start from the 256 bytes of UTF-8", "", "blue"),
        "llm": (710, 380, "Language-model tokens", "the Transformer's input (topic 9)", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("gage", "sub", ports=("bottom", "top:0.15"))
    D.edge("nmt", "sub", ports=("bottom", "top"))
    D.edge("w2v", "sub", ports=("bottom", "top:0.85"))
    D.edge("sub", "byte", ports=("bottom:0.15", "top"))
    D.edge("sub", "llm", ports=("bottom:0.85", "top"))
    return D


def chain():
    steps = [
        ("A translator knows a fixed list of words; every other word is \"unknown\"",
         "Cut words into pieces learned by byte-pair merges", "Sennrich, Haddow and Birch, 2015"),
        ("Letters the training text never contained are still unknown",
         "Start from the 256 bytes of UTF-8 instead of letters", "byte-level BPE"),
        ("Byte pieces can cross word and character boundaries in odd ways",
         "Split text into words first, then merge bytes within each word", "today's tokenizers"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from whole words to bytes")
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
    g, f, co, u = d["gage"], d["figure"], d["corpus"], d["unseen"]
    growth = {k: (v, s) for k, v, s in d["growth"]}
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. In 1994 Philip Gage compressed files by replacing their most frequent pair of bytes with a spare byte, again and again. Twenty-one years later, neural translators still worked with a fixed list of whole words. Sennrich, Haddow and Birch at Edinburgh ran Gage's loop on words written as letters, and the pieces it learned became a vocabulary that can spell any word."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: subword units. Blue: what came after."),
        ]),
        dict(id="play", eyebrow="Try it", title="Merge by merge", toc="Try it", blocks=[
            dict(type="p", text=f"Each word is written as letters followed by the end symbol {DOT}. Press *Merge once*: the most frequent pair of neighbouring symbols, counted over all the words, becomes one new symbol. Watch common endings form, then whole words. Type a word that is not in the text to see it cut into the pieces learned so far, or edit the text and start over."),
            dict(type="widget", html=BPE_HTML, js=BPE_JS, css=BPE_CSS,
                 fallback=dict(type="svg", name="unseen", draw=unseen_svg(d), alt="Unseen words cut into learned pieces", width=760),
                 note="In the interactive edition you can run the merges yourself on any text."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it. The third row describes common practice, not a single paper."),
        ]),
        dict(id="how", eyebrow="How it works", title="Count, merge, repeat", toc="How it works", blocks=[
            dict(type="p", text=f"**Learning.** Count every word in the training text. Write each as its letters and an end symbol {DOT}, so that \"low\" is l o w {DOT}. Count every pair of neighbouring symbols, each word weighted by how often it occurs. Merge the most frequent pair everywhere into a new symbol, write it down, and count again. Stop after a chosen number of merges: the vocabulary is the letters plus one symbol per merge."),
            dict(type="p", text=f"**Cutting a word.** Write it as letters and {DOT}; then, among the merges that apply, apply the one learned earliest, and repeat until none applies. A frequent word ends as one symbol; a rare one as a few pieces; a word made of letters never seen keeps those letters as they are."),
            dict(type="p", text=f"**Why the end symbol.** \"er\" at the end of a word (newer, wider) is a different thing from \"er\" inside one (very); the end symbol keeps them apart, and lets the pieces be joined back into words exactly."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Let the data choose the vocabulary. A fixed number of merges gives a fixed-size vocabulary, yet every word can still be spelled, because the letters themselves remain in it."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Forty stems, forty unseen words", toc="Measured", blocks=[
            dict(type="p", text=f"**Gage's compressor** on Wikipedia's example: {' → '.join(g['steps'])}, with the table {g['table']}. At each step the pair replaced was a most frequent one: {g['counts']}. {g['sizes'][0]} symbols became {g['sizes'][1]}, and the table, applied backwards, restores the text exactly."),
            dict(type="p", text=f"**The paper's Figure 1** learns from the four words low, lowest, newer, wider, and shows the merges {', '.join(f['paper'])}. The program checks that each was a most frequent pair when it was made; all four had count 2, tied with {', '.join(f['ties'][:3])} and {f['ties'][3]} other pairs. Ties may be broken either way: this program, taking the pair it saw first, learns {f['mine']} instead. Afterwards the paper's four words read {f['after']}."),
            dict(type="p", text=f"**A corpus.** {co[0]} words in 20,000 sentences, built from {co[3]} stems (low, walk, ...) with their endings (-er, -est, -ly, -ness; -s, -ed, -ing, -er, -ers): {co[1]} distinct words over {co[2]} letters. One ending of every stem was held out, so {co[4]} words never appear, among them {co[5]}. The first merges: {', '.join(d['merges'][:12])}."),
            dict(type="table", head=["Merges", "Symbols per word", "Vocabulary"], num=[0, 1, 2], rows=[[k, v, s] for k, (v, s) in growth.items()], hl=4),
            dict(type="p", text=f"Giving every distinct word of this corpus its own symbol would need {d['whole']} symbols, and would still fail on the next new word."),
            dict(type="p", text=f"**Words never seen.** After {u['K']} merges, the {u['n']} held-out words are cut into {u['pieces']} pieces on average, and **{u['cut']} of {u['n']}** are cut exactly where the stem meets the ending: " + "; ".join(f"{w} = {' + '.join(p)}" for w, p in u["ex"]) + ". No grammar was given; the boundaries come from counting."),
            dict(type="p", text=f"**Letters against bytes.** A vocabulary built from this corpus's {d['letters']} letters cannot write a letter it never saw; a byte vocabulary starts from all 256 values of UTF-8 and can write anything:"),
            dict(type="table", head=["Text", "Unknown letters", "UTF-8 bytes", "Byte tokens"], num=[1, 2, 3], rows=[[t, a, b, k] for t, a, b, k in d["bytes"]]),
            dict(type="p", text=f"All {d['exact'][0]} of {d['exact'][1]} strings decode from their byte tokens back to exactly the original text. Characters the merges never met simply stay as single bytes, three or four per character."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Edinburgh, 2015", toc="The evidence", blocks=[
            dict(type="p", text="Sennrich, Haddow and Birch (School of Informatics, University of Edinburgh; arXiv, first version 31 August 2015): translation is \"an open-vocabulary problem\"; byte-pair encoding is \"a simple data compression technique\"; words end in a \"special end-of-word symbol\". Their Algorithm 1 is a minimal Python implementation; their experiments used 59,500 merge operations (89,500 for a vocabulary shared by both languages), and subword models improved on a back-off dictionary baseline \"by up to 1.1 and 1.3 BLEU, respectively\" for English→German and English→Russian."),
            dict(type="p", text="Wikipedia: byte-pair encoding was \"first described in 1994 by Philip Gage\"; the original \"replaces the highest-frequency pair of bytes with a new byte that was not contained in the initial dataset\"; \"A slightly modified version of the algorithm is used in large language model tokenizers\"; byte-level BPE \"converts the text into UTF-8 first\". GPT-3.5 and GPT-4 use a vocabulary of 100,258 tokens."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A compressor becomes a reader", toc="Full circle", blocks=[
            dict(type="p", text="Gage wanted fewer bytes. The same loop, run on text, finds the pieces a language is built from, and those pieces became the units in which today's language models read and write. The algorithm did not change; the question asked of its output did."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Nobody told the program that -ness is an ending. {u['cut']} of {u['n']} words it had never seen were cut exactly there."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Apply Gage's method by hand to abababcab. Which pair goes first?", "ab, 4 times: XXXcX with X = ab. Now every pair occurs only once (XXX holds XX once without overlap), so another replacement would save nothing and the compressor stops."),
            (f"Why add {DOT} to the end of each word?", "So that endings and word-internal pieces are different symbols, and the pieces can be joined back into the original words."),
            ("A vocabulary of 30 letters and 1,000 merges: how many symbols?", "1,030: each merge adds exactly one symbol."),
            ("Why are the merges replayed in the order learned when cutting a new word?", "That reproduces how the training words were cut, so a new word gets the same pieces a training word with the same letters would have."),
            ("A byte vocabulary meets a Chinese character it never saw. What happens?", "It is written as its three UTF-8 bytes, which are always in the vocabulary; nothing is unknown."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Neural Machine Translation of Rare Words with Subword Units (2015)", text="Sennrich, Haddow and Birch, arXiv:1508.07909.",
                 draw=C.draw_manuscript, link="https://arxiv.org/pdf/1508.07909", link_text="arXiv:1508.07909 (PDF)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "BytePairEncoding", d["checks"],
                           "Wikipedia's example and the paper's figure as valid runs, that the pieces always spell the word, that unseen words are cut at the stem, and that bytes decode exactly.",
                           ["static List<Pair> learn(Map<String, Long> words, int merges, Map<List<String>, Long>[] finalVocab)",
                            "static List<String> segment(List<String> w, Map<Pair, Integer> rank)"]),
    ]
    return dict(
        title="Byte-Pair Encoding for Words", date="2015",
        description="Era 9, topic 6 of The Algorithm Evolution Atlas: byte-pair encoding, from Gage's 1994 compressor to the subword units of Sennrich, Haddow and Birch (2015) and byte-level tokens.",
        lede="A neural translator knew a fixed list of words and called every other word unknown. In 2015 three researchers at Edinburgh borrowed a compression trick from 1994: merge the most frequent pair of symbols, again and again. The pieces it learns can spell any word.",
        fieldnote=f"I gave the program {co[3]} stems and their endings, and hid one ending of each stem. It counted pairs of letters and merged them, {u['K']} times. Then I showed it the {u['n']} words it had never seen. It cut {u['cut']} of them exactly between stem and ending, and it had never been told what an ending is.",
        card=[("When", "1994; August 2015"),
              ("Where", "The C Users Journal; University of Edinburgh"),
              ("What hurt", "Fixed vocabularies, and unknown words"),
              ("The fix", "Learned merges: pieces that spell any word"),
              ("Checked", f"{u['cut']} of {u['n']} unseen words cut at the stem")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BytePairEncoding.java`.",
    )
