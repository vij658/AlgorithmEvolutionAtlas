"""Era 6, topic 11: fast string searching (KMP, Boyer-Moore). Every number is parsed from StringSearch.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"unlucky: text of ([\d,]+) a's then b, pattern of (\d+) a's then b ; the simple method makes ([\d,]+) comparisons and backs up in the text ([\d,]+) times ; Knuth-Morris-Pratt ([\d,]+) comparisons, never backing up ; Boyer-Moore ([\d,]+)", ln):
            d["bad"] = dict(na=m.group(1), pa=m.group(2), simple=m.group(3), back=m.group(4), kmp=m.group(5), bm=m.group(6))
        elif m := re.match(r"next: pattern (\w+) ; .*? has length: ([\d ]+) ; text (\w+) ; found at position \[(\d+)\] with (\d+) comparisons for (\d+) letters of text", ln):
            d["next"] = dict(pat=m.group(1), vals=m.group(2).split(), text=m.group(3), at=m.group(4), cmp=m.group(5), n=m.group(6))
        elif m := re.match(r"tables: pattern (\S+) ; delta1 \(.*?\): (.*?) ; delta2 \(.*?\): ([\d ]+) ; text (\S+) ; found at position \[(\d+)\] after looking at (\d+) of its (\d+) letters", ln):
            d["tables"] = dict(pat=m.group(1), d1=m.group(2), d2=m.group(3).split(), text=m.group(4), at=m.group(5), looks=m.group(6), n=m.group(7))
        elif m := re.match(r"agree: ([\d,]+) random searches .*? report the same ([\d,]+) matches", ln):
            d["agree"] = dict(n=m.group(1), matches=m.group(2))
        elif ln.startswith("speed: "):
            d["speed"] = {name: re.findall(r"m=(\d+): ([\d.]+)", part) for name, part in
                          re.findall(r"(English|binary|100 symbols) ((?:m=\d+: [\d.]+ ?)+)", ln)}
            m = re.search(r"in English, ([\d.]+) at m = 5 and ([\d.]+) at m = 14 ; texts of ([\d,]+) letters", ln)
            d["eng"] = dict(m5=m.group(1), m14=m.group(2), n=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def tables_svg(d):
    nx, tb = d["next"], d["tables"]

    def draw(t, standalone):
        o = []
        W, H = 760, 300
        o.append(C.text(20, 24, "Knuth, Morris and Pratt: after j letters match, how much of the pattern is still matched", t["ink"], 13, "start", 700))
        cw = 46
        for i, ch in enumerate(nx["pat"]):
            x = 120 + i * cw
            o.append(C.rect(x, 40, cw - 4, 30, t["surface"], t["blue"], 1.4, 3))
            o.append(C.text(x + (cw - 4) / 2, 61, ch, t["ink"], 15, "middle", 700))
            o.append(C.text(x + (cw - 4) / 2, 92, nx["vals"][i], t["red"], 14, "middle", 700))
        o.append(C.text(20, 61, "pattern", t["muted"], 12))
        o.append(C.text(20, 92, "j letters →", t["muted"], 12))
        o.append(C.text(20, 116, "Under each letter: for j = 1, 2, … letters matched, the longest ending of them that is also a beginning of the pattern.", t["muted"], 11))
        o.append(C.text(20, 160, "Boyer and Moore: compare from the right end; shift by a table", t["ink"], 13, "start", 700))
        for i, ch in enumerate(tb["pat"]):
            x = 120 + i * cw
            o.append(C.rect(x, 176, cw - 4, 30, t["surface"], t["red"], 1.4, 3))
            o.append(C.text(x + (cw - 4) / 2, 197, ch, t["ink"], 15, "middle", 700))
            o.append(C.text(x + (cw - 4) / 2, 228, tb["d2"][i], t["blue"], 14, "middle", 700))
        o.append(C.text(20, 197, "pattern", t["muted"], 12))
        o.append(C.text(20, 228, "delta2 →", t["muted"], 12))
        o.append(C.text(20, 258, f"delta1, by the text's letter at a mismatch: {tb['d1']}.", t["muted"], 12))
        o.append(C.text(20, 280, f"delta2: how far to advance after a mismatch at each position, given the ending already matched.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "The tables of Knuth, Morris and Pratt, and of Boyer and Moore", t, standalone, 0.55, 760)
    return draw


SS_HTML = """
<div class="board ss-board">
  <div style="min-width:0">
    <label class="ss-row">Text <input type="text" id="ss-text" maxlength="60"></label>
    <label class="ss-row">Pattern <input type="text" id="ss-pat" maxlength="14"></label>
    <div class="ss-view" id="ss-view"></div>
  </div>
  <div style="min-width:0">
    <div class="ss-btns"><button type="button" id="ss-simple">Simple</button><button type="button" id="ss-kmp">Knuth–Morris–Pratt</button><button type="button" id="ss-bm">Boyer–Moore</button></div>
    <div class="ss-btns"><button type="button" id="ss-step">Step</button><button type="button" id="ss-run">Run to the end</button></div>
    <div class="ss-stats" id="ss-stats"></div>
    <p class="say" id="ss-say" aria-live="polite"></p>
  </div>
</div>
"""

SS_CSS = """
.ss-row{display:grid;gap:2px;font-size:14px;margin:4px 0}
.ss-row input{font:14px var(--mono);width:100%}
.ss-view{font:15px var(--mono);overflow-x:auto;margin-top:10px;line-height:1.6}
.ss-view div{white-space:pre}
.ss-view span.c{background:var(--yellow);color:var(--on-yellow)}
.ss-view span.x{background:var(--red);color:var(--on-red)}
.ss-view span.m{background:var(--blue);color:var(--on-blue)}
.ss-view span.s{color:var(--muted)}
.ss-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.ss-stats{font:13px var(--mono);display:grid;gap:3px}
"""

SS_JS = r"""
(() => {
  const view = document.getElementById("ss-view");
  if (!view) return;
  const T0 = __TEXT__, P0 = __PAT__;
  document.getElementById("ss-text").value = T0; document.getElementById("ss-pat").value = P0;
  let events = [], k = 0, algo = "bm", T, P;
  function* simple() { for (let s = 0; s + P.length <= T.length; s++) { let j = 0; while (j < P.length) { const ok = T[s + j] === P[j]; yield {s, i: s + j, ok}; if (!ok) break; j++; } if (j === P.length) yield {s, found: s}; } }
  function* kmp() {
    const f = [-1]; let q = -1; for (let j = 0; j < P.length; j++) { while (q >= 0 && P[q] !== P[j]) q = f[q]; q++; f[j + 1] = q; }
    let j = 0;
    for (let i = 0; i < T.length; i++) {
      while (true) { const ok = P[j] === T[i]; yield {s: i - j, i, ok}; if (ok) { j++; break; } j = f[j]; if (j < 0) { j = 0; break; } }
      if (j === P.length) { yield {s: i - P.length + 1, found: i - P.length + 1}; j = f[P.length]; }
    }
  }
  function* bm() {
    const m = P.length, d1 = {}; for (let j = 0; j < m - 1; j++) d1[P[j]] = m - 1 - j;
    const fail = [-1]; let fq = -1; for (let j = 0; j < m; j++) { while (fq >= 0 && P[fq] !== P[j]) fq = fail[fq]; fq++; fail[j + 1] = fq; }
    const suff = new Array(m).fill(0); suff[m - 1] = m;
    for (let i = m - 2; i >= 0; i--) { let q = 0; while (q <= i && P[i - q] === P[m - 1 - q]) q++; suff[i] = q; }
    const g = new Array(m).fill(m); let jj = 0;
    for (let i = m - 1; i >= 0; i--) if (suff[i] === i + 1) for (; jj < m - 1 - i; jj++) if (g[jj] === m) g[jj] = m - 1 - i;
    for (let i = 0; i <= m - 2; i++) g[m - 1 - suff[i]] = m - 1 - i;
    let pos = m - 1;
    while (pos < T.length) {
      let j = m - 1, q = pos;
      while (true) { const ok = T[q] === P[j]; yield {s: pos - m + 1, i: q, ok}; if (!ok || j === 0) break; j--; q--; }
      if (j === 0 && T[q] === P[0]) { yield {s: q, found: q}; pos += m - fail[m]; continue; }
      pos = Math.max(q + (d1[T[q]] !== undefined ? d1[T[q]] : m), pos + g[j]);
      if (pos <= q) pos = q + 1;
    }
  }
  function start(a) {
    algo = a; T = document.getElementById("ss-text").value; P = document.getElementById("ss-pat").value;
    if (!P.length || P.length > T.length) { events = []; k = 0; show(); return; }
    events = [...(a === "simple" ? simple() : a === "kmp" ? kmp() : bm())]; k = 0; show();
  }
  function show() {
    view.innerHTML = "";
    const done = events.slice(0, k), last = done[done.length - 1];
    const looked = new Set(done.filter(e => e.i !== undefined).map(e => e.i)), found = done.filter(e => e.found !== undefined).map(e => e.found);
    const tl = el("div", {}, view);
    [...(T || "")].forEach((ch, i) => el("span", {class: found.some(f => i >= f && i < f + P.length) ? "m" : last && last.i === i ? (last.ok ? "c" : "x") : looked.has(i) ? "c" : "s"}, tl, ch));
    const pl = el("div", {}, view);
    const s = last ? last.s : 0;
    pl.appendChild(document.createTextNode(" ".repeat(Math.max(0, s))));
    [...(P || "")].forEach((ch, j) => el("span", {class: last && last.i === s + j ? (last.ok ? "c" : "x") : ""}, pl, ch));
    const comps = done.filter(e => e.i !== undefined).length;
    const st = document.getElementById("ss-stats"); st.innerHTML = "";
    const names = {simple: "simple method", kmp: "Knuth–Morris–Pratt", bm: "Boyer–Moore"};
    el("div", {}, st, `${names[algo]}: ${comps} comparisons so far`);
    el("div", {}, st, `letters of the text looked at: ${looked.size} of ${T ? T.length : 0}`);
    el("div", {}, st, `matches at: ${found.join(", ") || "—"}`);
    document.getElementById("ss-say").textContent = !events.length ? "Type a text and a shorter pattern." : k >= events.length ? "Done." :
      algo === "bm" ? "Boyer–Moore compares from the pattern's right end; a mismatch on a letter not in the pattern lets it jump the whole length." :
      algo === "kmp" ? "Knuth–Morris–Pratt never moves back in the text; on a mismatch it slides the pattern by its table." :
      "The simple method tries every starting place, rereading letters it has already seen.";
  }
  document.getElementById("ss-simple").addEventListener("click", () => start("simple"));
  document.getElementById("ss-kmp").addEventListener("click", () => start("kmp"));
  document.getElementById("ss-bm").addEventListener("click", () => start("bm"));
  document.getElementById("ss-step").addEventListener("click", () => { if (k < events.length) k++; show(); });
  document.getElementById("ss-run").addEventListener("click", () => { k = events.length; show(); });
  ["ss-text", "ss-pat"].forEach(id => document.getElementById(id).addEventListener("input", () => start(algo)));
  start("bm");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How fast string searching combined older ideas, and where it led")
    W = 210
    nodes = {
        "fa": (20, 20, "Finite automata", "a machine reads each letter once", "Era 5, topic 2", "ink"),
        "cook": (395, 20, "Cook's theorem", "on pushdown automata: Knuth's route in", "early 1970", "ink"),
        "ed": (770, 20, "Text editors", "Morris's editor for the CDC 6400", "1969", "ink"),
        "kmp": (20, 180, "Knuth–Morris–Pratt", "⊕ the next table: never back up", "1977", "red"),
        "bm": (770, 180, "Boyer–Moore", "⊕ compare from the right; jump", "1977; Gosper too", "red"),
        "proof": (395, 340, "Worst-case proofs", "Knuth 1976; Guibas and Odlyzko; Cole, 3n", "", "ink"),
        "lz": (770, 340, "Longest-match search", "the heart of LZ77", "topic 12", "ink"),
        "today": (395, 490, "Today", "Boyer–Moore, \"the standard benchmark\" for practical string search", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("fa", "kmp", ports=("bottom", "top"))
    D.edge("cook", "kmp", ports=("bottom:0.2", "top:0.8"))
    D.edge("ed", "kmp", ports=("bottom:0.2", "right"), label="the same method, found twice", at=0.5, dy=-8)
    D.edge("ed", "bm", ports=("bottom", "top"), dashed=True)
    D.edge("bm", "proof", ports=("bottom:0.2", "top:0.8"))
    D.edge("kmp", "proof", ports=("bottom:0.8", "top:0.2"))
    D.edge("bm", "lz", ports=("bottom", "top"), dashed=True)
    D.edge("proof", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: related, not derived. Wikipedia calls Boyer–Moore \"the standard benchmark for practical string-search literature\".", "caption")
    return D


def chain(d):
    b, e = d["bad"], d["eng"]
    steps = [
        (f"The simple method on an unlucky text: {b['simple']} comparisons, backing up {b['back']} times",
         f"Knuth, Morris and Pratt: {b['kmp']} comparisons, never backing up", "1977 (Morris's editor, 1969)"),
        ("Still at least one look at every letter of the text",
         f"Boyer and Moore: compare from the right; on English text, {e['m5']} letters looked at per letter passed (5-letter patterns)", "1977"),
        ("How bad can Boyer–Moore get?",
         "Linear in the worst case, proved with an improved table (Knuth, 1976); later 3n comparisons (Cole, 1991)", "Boyer and Moore; Wikipedia"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from rereading to skipping")
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
    b, nx, tb, ag, sp, e = d["bad"], d["next"], d["tables"], d["agree"], d["speed"], d["eng"]
    ms = [m for m, _ in sp["English"]]
    speed_rows = [[m] + [dict(sp[k])[m] for k in ("English", "binary", "100 symbols")] for m in ms]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A finite automaton reads each letter once and never goes back (Era 5, topic 2); Morris, writing a text editor, wanted a search that behaved the same way, and Knuth reached the same method from a theorem of Cook's. Boyer and Moore asked a different question: why read every letter at all? Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the two 1977 methods. Blue: where they stand today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Three ways to find a word", toc="Try it", blocks=[
            dict(type="p", text=f"A text and a pattern (the program's Boyer–Moore example is loaded). Choose a method and step through it: yellow letters have been compared, red is a mismatch, blue a match. Count how many letters of the text each method looks at. Then try an unlucky text such as aaaaaaaaab with the pattern aaab."),
            dict(type="widget", html=SS_HTML, js=SS_JS.replace("__TEXT__", f'"{tb["text"]}"').replace("__PAT__", f'"{tb["pat"]}"'), css=SS_CSS,
                 fallback=dict(type="table", head=["Pattern length m", "English", "Binary", "100 symbols"], num=[0, 1, 2, 3], rows=speed_rows, hl=2),
                 note="In the interactive edition you can step through the three searches. The table: letters Boyer–Moore examined per letter of text passed."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Remember what has been matched", toc="How it works", blocks=[
            dict(type="p", text="**Knuth, Morris and Pratt.** When a mismatch comes after j letters have matched, those j letters are known: they are the first j letters of the pattern. So the pattern can slide forward to the longest ending of those j letters that is also a beginning of the pattern, and the search continues with the same letter of the text. A table computed once from the pattern gives that length for every j. The text pointer never moves back; each letter is read once, and the work is proportional to m + n."),
            dict(type="p", text="**Boyer and Moore.** Line the pattern up and compare from its *right* end. If the text's letter there does not occur in the pattern at all, no alignment covering it can match, and the pattern jumps its whole length. Two tables say how far to shift: delta1 by the mismatched letter of the text, delta2 by the ending already matched. The longer the pattern, the longer the jumps."),
            dict(type="svg", name="tables", draw=tables_svg(d), alt="The tables of Knuth, Morris and Pratt, and of Boyer and Moore", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="A failed comparison is information. Knuth, Morris and Pratt use what has matched to avoid looking back; Boyer and Moore use what did not match to avoid looking at most of the text."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Comparisons counted", toc="Measured", blocks=[
            dict(type="p", text=f"**An unlucky text.** {b['na']} a's then b, with a pattern of {b['pa']} a's then b: the simple method made {b['simple']} comparisons and backed up in the text {b['back']} times; Knuth–Morris–Pratt made {b['kmp']}, never backing up; Boyer–Moore {b['bm']}."),
            dict(type="p", text=f"**The tables.** For the pattern {nx['pat']}, the program's next table is {' '.join(nx['vals'])}; searching {nx['text']} it found the pattern at position {nx['at']} with {nx['cmp']} comparisons for {nx['n']} letters of text. For {tb['pat']} in {tb['text']}, Boyer–Moore found it at position {tb['at']} after looking at {tb['looks']} of the {tb['n']} letters."),
            dict(type="p", text=f"**Agreement.** On {ag['n']} random searches all three methods reported the same {ag['matches']} matches."),
            dict(type="p", text=f"**Skipping.** For each pattern length, 300 patterns taken at random from each text, the work counted up to the first match. In English (this book's own field notes, {e['n']} letters), Boyer–Moore looked at {e['m5']} letters per letter passed with 5-letter patterns and {e['m14']} with 14-letter ones; Knuth–Morris–Pratt always looks at least once at each."),
            dict(type="table", head=["Pattern length m", "English", "Binary", "100 symbols"], num=[0, 1, 2, 3], rows=speed_rows, hl=2),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Found three times", toc="The evidence", blocks=[
            dict(type="p", text="Knuth, Morris and Pratt, \"Fast Pattern Matching in Strings\" (*SIAM Journal on Computing* 6(2): 323–350, June 1977; received 29 August 1974): the algorithm \"finds all occurrences of one given string within another, in running time proportional to the sum of the lengths of the strings\", and it \"was discovered in a rather interesting way\". \"One of the authors (J. H. Morris) was implementing a text-editor for the CDC 6400 computer during the summer of 1969\"; \"Another author (D. E. Knuth) learned early in 1970 of S. A. Cook's surprising theorem\" about two-way pushdown automata and derived the method from it; \"Pratt modified Knuth's data structure so that the running-time was independent of the alphabet size\", and when Pratt described it, Morris recognized his own algorithm."),
            dict(type="p", text="Boyer (Stanford Research Institute) and Moore (Xerox PARC), \"A Fast String Searching Algorithm\" (*Communications of the ACM* 20(10): 762–772, October 1977): the algorithm is \"usually sublinear\"; for English patterns of length 5 it inspected about 0.24 characters per character passed, where Knuth–Morris–Pratt inspects 1 and the simple algorithm about 1.1. R. W. Gosper found the delta1-only version independently, and Knuth proved in January 1976 that an improved delta2 makes the worst case linear."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A measurement repeated", toc="Full circle", blocks=[
            dict(type="p", text=f"Boyer and Moore measured about 0.24 letters examined per letter passed for 5-letter English patterns in 1977. On a different English text, this book's field notes, the program measured {e['m5']}. And the next topic's compressor spends most of its time on exactly this job: searching what it has already sent for the longest match."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="Kleene's finite automata (Era 5) read every letter once. Knuth, Morris and Pratt built such a reader for one pattern; Boyer and Moore found it could skip most of them."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What is the next table of the pattern aaab?", "After 1, 2, 3, 4 letters matched: 0, 1, 2, 0."),
            ("Why does Knuth–Morris–Pratt never need to back up in the text?", "The letters already matched are the pattern's own first letters, so the table says how much of them still counts."),
            ("Searching for HALT, Boyer–Moore compares the text's letter Q with the pattern's T. How far can it jump?", "Four places: Q is not in HALT, so no alignment that covers it can match."),
            ("Why does Boyer–Moore do worse on binary text?", "With two letters, almost every letter occurs in the pattern, so the jumps are short."),
            ("Which method would you choose for text arriving one letter at a time over a wire?", "Knuth–Morris–Pratt: it never needs a letter it has already passed."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Fast Pattern Matching in Strings (1977)", text="Knuth, Morris and Pratt, with its section on how the method was found.",
                 draw=C.draw_manuscript, link="https://cs.brown.edu/courses/csci1810/fall-2023/resources/ch2_readings/kmp_strings.pdf", link_text="The paper (PDF, on a Brown course page)", licence="Drawn placeholder."),
            dict(title="A Fast String Searching Algorithm (1977)", text="Boyer and Moore, with their measurements on English and random text.",
                 draw=C.draw_manuscript, link="https://www.cs.utexas.edu/%7Emoore/publications/fstrpos.pdf", link_text="The paper (PDF, on Moore's page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "StringSearch", d["checks"],
                           "the three methods on an unlucky text, the two worked tables, 20,000 random searches with identical results, and the letters examined on English, binary and 100-symbol text.",
                           ["static int[] failure(String p)", "static List<Integer> kmp(String t, String p)"]),
    ]
    return dict(
        title="Fast String Searching", date="1969–1977",
        description="Era 6, topic 11 of The Algorithm Evolution Atlas: Knuth, Morris and Pratt's never-back-up search, Boyer and Moore's right-to-left jumps, measured on this book's own text.",
        lede="Finding a word in a text looks too simple to improve. Knuth, Morris and Pratt made a search that never rereads a letter; Boyer and Moore made one that does not read most letters at all.",
        fieldnote=f"Boyer and Moore reported that their search looked at about a quarter of an English text for five-letter patterns. On my own field notes the program measured {e['m5']}, and {e['m14']} for fourteen-letter patterns: the longer the word sought, the less of the text is read.",
        card=[("When", "Morris 1969; both papers 1977"),
              ("Where", "Berkeley and Stanford; SRI and Xerox PARC"),
              ("What hurt", "Rereading text; m × n comparisons at worst"),
              ("The fix", "A table from the pattern; compare from the right"),
              ("Measured", f"{e['m5']} letters examined per letter, English, m = 5")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `StringSearch.java`, except Boyer and Moore's own 1977 figures, quoted from their paper.",
    )
