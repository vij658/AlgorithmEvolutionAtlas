"""Era 4, topic 12: Shannon's switches, bits and entropy. Every number is parsed from InformationTheory.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"imit": []}
    for ln in text.splitlines():
        if m := re.match(r"relays: .*? needs (\d+) contacts ; .*?, (\d+) contacts, the same on all (\d+) inputs", ln):
            d["relay"] = dict(three=int(m.group(1)), five=int(m.group(2)), inputs=m.group(3))
        elif m := re.match(r"text: (\d+) characters .*?, (\d+) words, (\d+) different words ; commonest: (.+?) ; .*? = ([\d.]+) bits, with letter frequencies ([\d.]+), given one letter before ([\d.]+), given two ([\d.]+) ; redundancy by the last estimate (\d+)%$", ln):
            d["text"] = dict(chars=int(m.group(1)), words=int(m.group(2)), diff=int(m.group(3)),
                             top=re.findall(r"(\S+) ([\d.]+)", m.group(4)), h0=m.group(5), h1=m.group(6), h2=m.group(7), h3=m.group(8), red=m.group(9))
        elif m := re.match(r"imitation: (\w+) \((.+?)\): (.+)$", ln):
            d["imit"].append((m.group(1), m.group(2), m.group(3)))
        elif m := re.match(r"code: .*?: space (\d+), E (\d+), T (\d+), \.\.\. Z (\S+) ; .*? average ([\d.]+) bits per letter, .*? the whole text in (\d+) bits, against (\d+) with 5 bits", ln):
            d["code"] = dict(space=m.group(1), e=m.group(2), t=m.group(3), z=m.group(4), avg=m.group(5), bits=int(m.group(6)), five=int(m.group(7)))
    d["checks"] = C.checks(text)
    return d


# the two relay networks, as branches of contacts in series (the branches are in parallel)
NET8 = [["x", "y"], ["x", "y'", "z"], ["x'", "y", "z"]]


def relay_svg(d):
    def draw(t, standalone):
        out = []

        def network(x0, y0, branches, title):
            out.append(C.text(x0, y0 - 14, title, t["ink"], 14, "start", 700))
            h = 46 * len(branches)
            out.append(C.line(x0, y0, x0, y0 + h - 46, t["ink2"], 2))
            out.append(C.line(x0 + 300, y0, x0 + 300, y0 + h - 46, t["ink2"], 2))
            for b, br in enumerate(branches):
                y = y0 + b * 46
                out.append(C.line(x0, y, x0 + 300, y, t["ink2"], 2))
                for k, c in enumerate(br):
                    cx = x0 + 40 + k * 80
                    out.append(C.rect(cx, y - 13, 46, 26, t["surface"], t["blue"] if "'" not in c else t["red"], 2))
                    out.append(C.text(cx + 23, y + 5, c, t["ink"], 14, "middle", 700))
        network(30, 60, NET8, f"x y + x y' z + x' y z: {d['relay']['three']} contacts")
        network(420, 60, [["x", "y"], ["z", "x or y"]], f"x y + z (x + y): {d['relay']['five']} contacts")
        out.append(C.text(30, 220, "Branches in parallel; contacts in a branch in series. Blue: closed when the switch is on; red (primed): closed when it is off.", t["muted"], 12.5))
        out.append(C.text(30, 240, f"Both networks conduct for exactly the same {d['relay']['inputs']} settings of x, y, z: whenever at least two are on (the carry of an adder).", t["muted"], 12.5))
        out.append(C.text(30, 260, "\"x or y\" stands for two contacts in parallel, so the second network has five.", t["muted"], 12.5))
        return C.svg_doc(780, 276, "".join(out), "Two relay networks for the same function, eight contacts and five", t, standalone, 0.55, 780)
    return draw


SH_HTML = """
<div class="board sh-board">
  <div style="min-width:0">
    <div class="eyebrow">Switches</div>
    <div class="controls" id="sh-sw"></div>
    <div class="sh-lamps" id="sh-lamps"></div>
    <div class="eyebrow" style="margin-top:14px">Imitation text</div>
    <div class="controls"><label for="sh-k">Statistics <select id="sh-k">
      <option value="-1">none (random letters)</option><option value="0">letter frequencies</option><option value="1">letter pairs</option>
      <option value="2" selected>letter triples</option><option value="3">four letters</option><option value="w1">word frequencies</option><option value="w2">word pairs</option></select></label>
      <button class="primary" id="sh-go">Generate</button></div>
  </div>
  <div style="min-width:0">
    <p class="sh-text" id="sh-text" aria-live="polite"></p>
    <ol class="sh-steps" id="sh-steps"></ol>
  </div>
</div>
"""

SH_CSS = """
.sh-board select{font:inherit;font-size:13.5px}
.sh-lamps{display:grid;gap:6px;font-size:13.5px;margin:8px 0}
.sh-lamps .lamp{display:inline-block;width:14px;height:14px;border-radius:50%;border:2px solid var(--ink-2);vertical-align:-2px;margin-right:6px}
.sh-lamps .lamp.on{background:var(--yellow);border-color:var(--yellow)}
.sh-text{font:14px var(--mono);min-height:4.5em;padding:10px;border:1px solid var(--axis);background:var(--surface);overflow-wrap:anywhere}
.sh-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.sh-steps .m{font-family:var(--mono);font-size:12.5px}
"""

SH_JS_TEMPLATE = r"""
(() => {
  const textEl = document.getElementById("sh-text");
  if (!textEl) return;
  const RAW = __CORPUS__, PROG = __PROG__;
  const S = RAW.toUpperCase().replace(/[^A-Z]+/g, " ").trim(), WORDS = S.split(" ");
  let seed = 1948;
  const rnd = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  const sw = {x: false, y: true, z: true};
  const box = document.getElementById("sh-sw");
  ["x", "y", "z"].forEach(k => { const b = el("button", {type: "button"}, box, k + ": " + (sw[k] ? "on" : "off")); b.addEventListener("click", () => { sw[k] = !sw[k]; b.textContent = k + ": " + (sw[k] ? "on" : "off"); lamps(); }); });
  function lamps() {
    const {x, y, z} = sw;
    const n8 = (x && y) || (x && !y && z) || (!x && y && z), n5 = (x && y) || (z && (x || y));
    const L = document.getElementById("sh-lamps"); L.innerHTML = "";
    el("div", {}, L).innerHTML = `<span class="lamp ${n8 ? "on" : ""}"></span>x y + x y' z + x' y z (8 contacts)`;
    el("div", {}, L).innerHTML = `<span class="lamp ${n5 ? "on" : ""}"></span>x y + z (x + y) (5 contacts)`;
    el("div", {}, L).innerHTML = `<span class="lamp ${x !== y ? "on" : ""}"></span>x y' + x' y (the two-way switch: x and y only)`;
  }
  function entropy(k) {                     // entropy of the next letter given k letters before, as in the program
    const ctx = new Map(), full = new Map();
    for (let i = k; i < S.length; i++) { const c = S.slice(i - k, i), f = S.slice(i - k, i + 1); ctx.set(c, (ctx.get(c) || 0) + 1); full.set(f, (full.get(f) || 0) + 1); }
    const total = S.length - k; let h = 0;
    for (const [f, n] of full) h -= (n / total) * Math.log2(n / ctx.get(f.slice(0, k)));
    return h;
  }
  function draw(m) { let t = 0; for (const v of m.values()) t += v; let r = rnd() * t; for (const [k, v] of m) { r -= v; if (r < 0) return k; } return [...m.keys()].pop(); }
  function gen() {
    const k = document.getElementById("sh-k").value;
    let out = "";
    if (k === "-1") { const A = " ABCDEFGHIJKLMNOPQRSTUVWXYZ"; for (let i = 0; i < 160; i++) out += A[Math.floor(rnd() * 27)]; }
    else if (k[0] === "w") {
      const next = new Map(); const counts = new Map();
      WORDS.forEach((w, i) => { counts.set(w, (counts.get(w) || 0) + 1); if (i) { const p = WORDS[i - 1]; if (!next.has(p)) next.set(p, new Map()); next.get(p).set(w, (next.get(p).get(w) || 0) + 1); } });
      let w = WORDS[Math.floor(rnd() * WORDS.length)]; const list = [w];
      for (let i = 1; i < 28; i++) { w = k === "w1" ? draw(counts) : (next.has(w) ? draw(next.get(w)) : WORDS[0]); list.push(w); }
      out = list.join(" ");
    } else {
      const n = +k, next = new Map();
      for (let i = n; i < S.length; i++) { const c = S.slice(i - n, i); if (!next.has(c)) next.set(c, new Map()); const m = next.get(c); m.set(S[i], (m.get(S[i]) || 0) + 1); }
      const st = Math.floor(rnd() * (S.length - n)); out = S.slice(st, st + n);
      while (out.length < 160) { const c = n ? out.slice(-n) : ""; const m = next.get(c); if (!m) { out += " "; continue; } out += draw(m); }
    }
    textEl.textContent = out;
    const ol = document.getElementById("sh-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    li(`the sample: ${fmt(S.length)} letters and spaces from this book's field notes`);
    if (k[0] !== "w") {
      const n = +k;
      const h = n < 0 ? Math.log2(27) : entropy(n);
      li(`entropy of the next letter ${n < 0 ? "with no statistics" : n === 0 ? "from letter frequencies" : "given " + n + " letter" + (n > 1 ? "s" : "") + " before"}: <span class="m">${h.toFixed(3)}</span> bits` +
         (n >= 0 && n <= 2 ? ` (the program: ${PROG[n]})` : ""));
    }
    li("the more context the statistics use, the more the imitation looks like the text, and the fewer bits each letter carries");
  }
  document.getElementById("sh-go").addEventListener("click", gen);
  document.getElementById("sh-k").addEventListener("change", gen);
  lamps(); gen();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Shannon's work combined older ideas, and where it led")
    W = 210
    nodes = {
        "boole": (20, 20, "Boole's algebra", "logic with 0 and 1", "Era 3 topic 12", "ink"),
        "relay": (395, 20, "Relay exchanges", "telephone switching", "early 20th century", "ink"),
        "mk": (770, 20, "Markov chains", "letters depend on letters", "topic 3", "ink"),
        "sh": (395, 170, "Shannon", "⊕ circuits as algebra; information in bits", "1937, 1948", "red"),
        "logic": (20, 330, "Logic design", "computers built from switching algebra", "1940s on", "ink"),
        "code": (395, 330, "Compression", "codes near the entropy", "Shannon's code, 1948", "ink"),
        "ham": (770, 330, "Error-correcting codes", "redundancy put to work", "topic 13", "ink"),
        "today": (395, 480, "Communication today", "every file, every signal", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("boole", "sh", ports=("bottom", "top:0.15"))
    D.edge("relay", "sh", ports=("bottom", "top"))
    D.edge("mk", "sh", ports=("bottom", "top:0.85"))
    D.edge("sh", "logic", ports=("bottom:0.1", "top:0.7"))
    D.edge("sh", "code", ports=("bottom", "top"))
    D.edge("sh", "ham", ports=("bottom:0.9", "top:0.3"))
    D.edge("code", "today", ports=("bottom", "top"))
    D.edge("ham", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Shannon's 1948 paper names its sources as \"discrete Markoff processes\"; relays were the switches of the telephone network he worked for.", "caption")
    return D


def chain(d):
    r, t = d["relay"], d["text"]
    steps = [
        ("Relay circuits designed by trial and error",
         f"Boole's algebra for switches: {r['three']} contacts become {r['five']}", "Shannon, 1937"),
        ("What is information, and how much does a message carry?",
         f"Count it in bits: H = −Σ p log₂ p; this book's letters carry {t['h1']}", "Shannon, 1948"),
        ("Letters depend on their neighbours, so frequencies overstate the information",
         f"Condition on context: {t['h2']} bits given one letter, {t['h3']} given two", "Markov sources"),
        ("Noise corrupts the bits on the way",
         "Below the channel's capacity, errors can be made as rare as you like", "Shannon, 1948; topic 13"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from relays to the measure of information")
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
    r, t, im, cd = d["relay"], d["text"], d["imit"], d["code"]
    corpus = (ctx["code_dir"] / "corpus.txt").read_text()
    js = SH_JS_TEMPLATE.replace("__CORPUS__", json.dumps(corpus)).replace("__PROG__", json.dumps([t["h1"], t["h2"], t["h3"]]))
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Boole's algebra of 0 and 1 (Era 3, topic 12) had been pure logic for eighty years; telephone exchanges were full of relays, switches that are either open or closed. In 1937 Shannon put the two together. In 1948, working for the telephone company, he asked what a message is worth, and measured it with Markov's statistics (topic 3). Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Shannon's thesis (1937) and paper (1948). Blue: where they led."),
        ]),
        dict(id="play", eyebrow="Try it", title="Switches, and imitation English", toc="Try it", blocks=[
            dict(type="p", text="Flip the switches: the eight-contact and five-contact networks always light together, because they are the same Boolean formula. Then generate imitation text from the statistics of this book's own field notes, as Shannon did from English: random letters, then letter frequencies, pairs, triples, and words. Watch the bits per letter fall as the statistics use more context."),
            dict(type="widget", html=SH_HTML, js=js, css=SH_CSS,
                 fallback=dict(type="svg", name="relays", draw=relay_svg(d), alt="Two relay networks for the same function, eight contacts and five", width=780),
                 note="In the interactive edition you can flip the switches and generate imitation text."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Contacts as variables, messages as surprise", toc="How it works", blocks=[
            dict(type="p", text=f"**Switching algebra (1937).** A contact is a variable: x when it closes as the switch turns on, x' when it closes as the switch turns off. Contacts in series conduct only if all do (x·y); in parallel if any does (x + y). The network x y + x y' z + x' y z needs {r['three']} contacts; Boole's algebra rewrites it as x y + z (x + y), with {r['five']}, and the program checks that the two conduct for the same settings, all {r['inputs']} of them. It is the carry of a binary adder: on whenever at least two inputs are."),
            dict(type="p", text=f"**Entropy (1948).** A source that emits symbol i with probability pᵢ carries H = −Σ pᵢ log₂ pᵢ bits per symbol on average. The program measures a sample of this book's own text, {t['chars']:,} letters and spaces from the field notes of Eras 1 to 3:"),
            dict(type="table", head=["What the next letter is predicted from", "Bits per letter"], num=[1],
                 rows=[["nothing: 27 equally likely symbols, log₂ 27", t["h0"]], ["letter frequencies", t["h1"]], ["the letter before", t["h2"]], ["the two letters before", t["h3"]]], hl=3),
            dict(type="p", text=f"The last figure is too low for real English: in a sample of only {t['chars']:,} letters, many three-letter strings occur once, so they look more predictable than they are. Shannon, judging English over about eight letters, put its redundancy at roughly 50 per cent; this small sample gives {t['red']}% at three letters, a coincidence rather than a confirmation."),
            dict(type="p", text="**Imitations**, generated by the program from the same sample, in the manner of Shannon's series:"),
            dict(type="table", head=["Statistics used", "Generated text"], num=[], rows=[[b, f"`{c}`"] for a, b, c in im]),
            dict(type="p", text=f"**Coding.** Give each letter a codeword of about −log₂ p bits: Shannon's code takes the first ⌈−log₂ p⌉ binary digits of the running total of the probabilities. Space gets {cd['space']}, E {cd['e']}, T {cd['t']}, and Z {cd['z']}. No codeword begins another, so a string of bits can be read back without separators, and the average length, {cd['avg']} bits, lies between H = {t['h1']} and H + 1, as Shannon proved it must. The whole sample takes {cd['bits']:,} bits instead of {cd['five']:,} at five bits a letter."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Information is surprise. A source's entropy, in bits per symbol, is the least any code can average; context lowers it; and the gap between the entropy and the bits actually sent is redundancy, which can be removed to compress or added to protect against noise."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The commonest letters", toc="Measured", blocks=[
            dict(type="table", head=["Symbol", "Share of the sample"], num=[1], rows=[[a, b] for a, b in t["top"]]),
            dict(type="p", text=f"The sample has {t['words']:,} words, {t['diff']:,} of them different. Space is the commonest symbol, then E and T."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A thesis and a paper", toc="The evidence", blocks=[
            dict(type="p", text="The thesis was written at MIT in 1937 and published in the *Transactions of the American Institute of Electrical Engineers* in 1938; Howard Gardner called it \"possibly the most important, and also the most famous, master's thesis of the century\" (Wikipedia). MIT's catalogue dates it 1940, the year of the degree (DSpace@MIT), and MacTutor gives the MIT master's and PhD both as 1940."),
            dict(type="p", text="\"A Mathematical Theory of Communication\" appeared in the *Bell System Technical Journal* in July and October 1948 and was reissued as a book with Warren Weaver in 1949 (Wikipedia). In it, units of base 2 \"may be called binary digits, or more briefly bits, a word suggested by J. W. Tukey\"; Theorem 2 gives H = −K Σ pᵢ log pᵢ, \"the entropy of the set of probabilities\"; the sources of English text \"are known mathematically as discrete Markoff processes\"; and below the capacity a noisy channel can carry messages with as few errors as desired (Theorems 11 and 12)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Every file, every signal", toc="Full circle", blocks=[
            dict(type="p", text="Every compressed file is a code that tries to get close to its source's entropy, and every phone call and download is protected by redundancy added on purpose, the subject of Hamming's codes (topic 13). Computers themselves are built from switching algebra: millions of transistors arranged by the rules of the 1937 thesis."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Five bits a letter would be enough for 32 symbols; this book's letters carry {t['h1']} bits each on their own, and {t['h3']} given their neighbours. Everything between is redundancy, which is why a text can still be read with letters missing."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Two switches in series light a lamp when? In parallel?", "In series, only when both are on (x·y); in parallel, when either is (x + y)."),
            ("How many bits does a fair coin toss carry? A coin that lands heads 90% of the time?", "1 bit; −0.9 log₂ 0.9 − 0.1 log₂ 0.1 ≈ 0.469 bits: a predictable outcome tells you less."),
            ("Why can no code average fewer bits than the entropy?", "That is Shannon's theorem: the entropy is the average surprise, and a code that beats it would let you predict the source better than its own probabilities allow."),
            ("Why must the codewords be prefix-free?", "So that a string of bits can be split back into codewords without separators: no codeword may be the start of another."),
            ("Why does the entropy fall when the previous letter is known?", "Some pairs are common (TH) and many are rare (QZ): knowing the last letter narrows the choice of the next."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Mathematical Theory of Communication (1948)", text="The paper, with bits, entropy, the imitations of English and channel capacity.",
                 draw=C.draw_book, link="https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf", link_text="MIT course page", licence="Drawn placeholder."),
            dict(title="A symbolic analysis of relay and switching circuits", text="Shannon's master's thesis, catalogued at MIT.",
                 draw=C.draw_manuscript, link="https://dspace.mit.edu/handle/1721.1/11173", link_text="DSpace@MIT", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "InformationTheory", d["checks"],
                           "the two relay networks and the adder on every input, the letter entropy computed two ways and falling with context, the imitations, and Shannon's code (prefix-free, with average length between H and H + 1).",
                           ["static double conditionalEntropy("]),
    ]
    return dict(
        title="Shannon's Bits", date="1937–1948",
        description="Era 4, topic 12 of The Algorithm Evolution Atlas: Shannon's switching algebra (1937) and his mathematical theory of communication (1948): bits, entropy and codes.",
        lede="In 1937 Shannon showed that relay circuits obey Boole's algebra, so circuits can be designed and simplified on paper. In 1948 he measured information itself, in bits, and found the limits of compression and of communication over noise.",
        fieldnote=f"I fed the statistics of this book's own field notes to a machine and asked it to write. With letter pairs it wrote nonsense; with word pairs it wrote \"{im[-1][2].lower()}\". Each letter of mine carries about {t['h1']} bits; given its neighbours, much less. The rest is what lets you read me through noise.",
        card=[("When", "Thesis 1937 (printed 1938); paper 1948"),
              ("Where", "MIT; Bell Telephone Laboratories"),
              ("What hurt", "Circuits by trial and error; no measure of information"),
              ("The fix", "Switching algebra; entropy in bits"),
              ("Measure", f"{t['h1']} bits per letter here, {t['h3']} with context")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `InformationTheory.java`.",
    )
