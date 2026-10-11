"""Era 2, topic 7: frequency analysis. Every number is parsed from FrequencyAnalysis.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def text_block(java, name):
    """The text of a Java text block `static final String NAME = \"\"\" ... \"\"\";`, as the program reads it."""
    m = re.search(rf'static final String {name} = """\n(.*?)"""', java, re.S)
    return " ".join(line.strip() for line in m.group(1).splitlines() if line.strip())


def parse(text: str) -> dict:
    d = {"breaks": []}
    for ln in text.splitlines():
        if m := re.match(r"sample: (\d+) letters of English ; ranking (\w+) ; the 12 most common: (\w+)$", ln):
            d["sample"] = dict(n=int(m.group(1)), rank=m.group(2), top=m.group(3))
        elif m := re.match(r"percent: (.+)$", ln):
            d["percent"] = [(x.split("=")[0], float(x.split("=")[1])) for x in m.group(1).split()]
        elif m := re.match(r"keys: 26! = (\d+) substitution keys ; at a billion a second, trying them all takes (\d+) years$", ln):
            d["keys"] = dict(n=int(m.group(1)), years=int(m.group(2)))
        elif m := re.match(r"break (\d+) letters: ranking alone (\S+)% right \((\d+) of (\d+) keys read\) ; ranking then letter pairs (\S+)% right \((\d+) of (\d+) keys read\)$", ln):
            g = m.groups()
            d["breaks"].append(dict(n=int(g[0]), rank=float(g[1]), rankread=int(g[2]), trials=int(g[3]), pairs=float(g[4]), pairsread=int(g[5])))
        elif m := re.match(r"example 400: cipher (\w+) ; by ranking (\w+) ; with letter pairs (\w+)$", ln):
            d["example"] = m.groups()
        elif m := re.match(r"ioc: plain (\S+) ; substitution (\S+) ; Vigenere with key \"(\w+)\" (\S+) ; one-time pad (\S+) ; uniform 1/26 = (\S+)$", ln):
            g = m.groups()
            d["ioc"] = dict(plain=g[0], sub=g[1], key=g[2], vig=g[3], pad=g[4], uni=g[5])
        elif m := re.match(r"period: average index of the columns for each guessed key length: (.+) ; the key has (\d+) letters$", ln):
            d["period"] = dict(cols=[(int(x.split("=")[0]), x.split("=")[1]) for x in m.group(1).split()], len=int(m.group(2)))
    d["checks"] = C.checks(text)
    return d


def example_svg(d):
    """The 400-letter example: cipher, ranking alone, then letter pairs."""
    cipher, rank, pairs = d["example"]
    plain = pairs  # the pairs line is nearly the plain text; mark letters that differ from it in the ranking line

    def draw(t, standalone):
        out = []
        rows = [("Cipher", cipher, None), ("Ranking alone", rank, plain), ("Then letter pairs", pairs, None)]
        for r, (label, s, ref) in enumerate(rows):
            y = 46 + r * 52
            out.append(C.text(20, y, label, t["muted"], 13))
            for i, ch in enumerate(s[:48]):
                x = 160 + i * 16.5
                col = t["ink"] if r == 0 else (t["red"] if ref and ch != ref[i] else t["blue"])
                out.append(C.text(x, y, ch, col, 15, "middle", 700 if r else 400))
        out.append(C.text(20, 192, "The first 48 letters of a 400-letter message. Red: wrong after ranking alone. Spaces are removed, as in a cipher.", t["muted"], 12.5))
        return C.svg_doc(960, 204, "".join(out), "A 400-letter cipher, read by ranking and then by letter pairs", t, standalone, 0.6, 960)
    return draw


FA_HTML = """
<div class="board fa-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="fa-len">Message length <input id="fa-len" type="range" min="40" max="1275" value="400"></label>
      <span class="fa-n" id="fa-n"></span>
    </div>
    <div class="controls">
      <button id="fa-new" type="button">New key</button>
      <button id="fa-rank" class="primary" type="button">1. Rank the counts</button>
      <button id="fa-pairs" type="button">2. Letter pairs</button>
    </div>
    <div class="fa-bars" id="fa-bars" aria-label="Letter counts: the cipher against English"></div>
    <div class="fa-text" id="fa-text" aria-live="polite"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Your decryption</div>
    <p class="say" id="fa-say"></p>
    <p class="fa-hint">To fix a letter by hand, click a cipher letter in the key below, then type the plain letter it stands for.</p>
    <div class="fa-key" id="fa-key"></div>
  </div>
</div>
"""

FA_CSS = """
.fa-board input[type=range]{width:min(260px,55vw)}
.fa-n{font-family:var(--mono);font-size:13px}
.fa-bars{display:grid;grid-template-columns:repeat(26,minmax(0,1fr));gap:2px;align-items:end;height:120px;margin:8px 0 2px}
.fa-bars .col{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;gap:1px}
.fa-bars .pr{display:flex;align-items:flex-end;justify-content:center;gap:1px;width:100%;flex:1}
.fa-bars .b1{width:45%;background:var(--red)} .fa-bars .b2{width:45%;background:var(--blue);opacity:.8}
.fa-bars .l{font-family:var(--mono);font-size:10px;color:var(--ink-2)}
.fa-legend{font-size:12px;color:var(--muted);margin-bottom:8px}
.fa-text{font-family:var(--mono);font-size:13px;line-height:1.6;word-break:break-all;background:var(--wash);border:1px solid var(--rule);padding:8px;max-height:220px;overflow:auto}
.fa-text .ok{color:var(--blue)} .fa-text .no{color:var(--red);font-weight:600}
.fa-key{display:grid;grid-template-columns:repeat(13,minmax(0,1fr));gap:3px;font-family:var(--mono);font-size:13px}
.fa-key button{padding:2px 0;font-weight:400;font-size:12px;border-width:1px;display:flex;flex-direction:column;align-items:center;min-width:0}
.fa-key button i{font-style:normal;color:var(--muted);font-size:10px}
.fa-key button.sel{background:var(--yellow);color:#000}
.fa-key button.ok{border-color:var(--blue)} .fa-key button.no{border-color:var(--red)}
.fa-board .say{font-size:15px}
.fa-hint{font-size:12.5px;color:var(--muted)}
@media (max-width:600px){.fa-key{grid-template-columns:repeat(7,minmax(0,1fr))}}
"""

FA_JS = r"""
(() => {
  const bars = document.getElementById("fa-bars");
  if (!bars) return;
  const SAMPLE = __SAMPLE__, MESSAGE = __MESSAGE__;
  const letters = s => s.toLowerCase().replace(/[^a-z]/g, "");
  const ref = letters(SAMPLE), msgAll = letters(MESSAGE);
  const A = "abcdefghijklmnopqrstuvwxyz";
  const counts = t => { const c = new Array(26).fill(0); for (const ch of t) c[ch.charCodeAt(0) - 97]++; return c; };
  const rankOf = c => [...Array(26).keys()].sort((a, b) => c[b] - c[a] || a - b);
  const rc = counts(ref), refRank = rankOf(rc);
  const pair = Array.from({ length: 26 }, () => new Array(26).fill(1));
  for (let i = 1; i < ref.length; i++) pair[ref.charCodeAt(i - 1) - 97][ref.charCodeAt(i) - 97]++;
  const pl = pair.map(row => { const s = row.reduce((a, b) => a + b, 0); return row.map(v => Math.log(v / s)); });
  let seed = 7;
  const rand = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed / 2147483648; };
  let key, plain, cipher, dec, sel = null;
  function newKey() {
    const l = A.split(""); for (let i = 25; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [l[i], l[j]] = [l[j], l[i]]; }
    key = l; // key[plain] = cipher
    load();
  }
  function load() {
    const n = +document.getElementById("fa-len").value;
    document.getElementById("fa-n").textContent = `${n} letters`;
    plain = msgAll.slice(0, n);
    cipher = [...plain].map(ch => key[ch.charCodeAt(0) - 97]).join("");
    dec = new Array(26).fill("?");
    say("A new secret message. Press <b>1. Rank the counts</b>: pair the cipher's most common sign with English's most common letter, and so on down.");
    paint();
  }
  const say = h => { document.getElementById("fa-say").innerHTML = h; };
  const decoded = () => [...cipher].map(ch => dec[ch.charCodeAt(0) - 97]).join("");
  const score = t => { let s = 0; for (let i = 1; i < t.length; i++) s += pl[t.charCodeAt(i - 1) - 97][t.charCodeAt(i) - 97]; return s; };
  function rank() {
    const cr = rankOf(counts(cipher));
    for (let i = 0; i < 26; i++) dec[cr[i]] = A[refRank[i]];
    say(`Ranked: ${acc()}% of the letters are right. Al-Kindi warned that a short message does not settle the counts.`);
    paint();
  }
  function pairs() {
    if (dec.includes("?")) rank();
    const tryClimb = start => {
      const d = start.slice(); let best = score([...cipher].map(ch => d[ch.charCodeAt(0) - 97]).join("")), imp = true;
      while (imp) { imp = false; for (let i = 0; i < 26; i++) for (let j = i + 1; j < 26; j++) { [d[i], d[j]] = [d[j], d[i]]; const s = score([...cipher].map(ch => d[ch.charCodeAt(0) - 97]).join("")); if (s > best + 1e-9) { best = s; imp = true; } else [d[i], d[j]] = [d[j], d[i]]; } }
      return [d, best];
    };
    let [bd, bs] = tryClimb(dec);
    for (let r = 0; r < 8; r++) { const s = dec.slice(); for (let k = 0; k < 6; k++) { const i = Math.floor(rand() * 26), j = Math.floor(rand() * 26); [s[i], s[j]] = [s[j], s[i]]; } const [d2, s2] = tryClimb(s); if (s2 > bs) { bs = s2; bd = d2; } }
    dec = bd;
    say(`After the letter-pair search: ${acc()}% right. Common pairs such as th, he, in and an pull the letters into place.`);
    paint();
  }
  const acc = () => { const t = decoded(); let ok = 0; for (let i = 0; i < t.length; i++) if (t[i] === plain[i]) ok++; return Math.round(1000 * ok / t.length) / 10; };
  function paint() {
    const cc = counts(cipher), cr = rankOf(cc), max = Math.max(cc[cr[0]] / cipher.length, rc[refRank[0]] / ref.length);
    bars.innerHTML = "";
    for (let i = 0; i < 26; i++) {
      const col = el("div", { class: "col" }, bars), pr = el("div", { class: "pr" }, col);
      const b1 = el("div", { class: "b1" }, pr); b1.style.height = `${96 * cc[cr[i]] / cipher.length / max}%`;
      const b2 = el("div", { class: "b2" }, pr); b2.style.height = `${96 * rc[refRank[i]] / ref.length / max}%`;
      el("span", { class: "l" }, col, A[cr[i]]);
      el("span", { class: "l" }, col, A[refRank[i]]);
    }
    let lg = bars.nextElementSibling;
    if (!lg || !lg.classList.contains("fa-legend")) { lg = el("div", { class: "fa-legend" }); bars.after(lg); }
    lg.textContent = "Ranked from most to least common. Red bars and top letters: the cipher's signs. Blue bars and bottom letters: English, from the program's sample.";
    const tx = document.getElementById("fa-text"); tx.innerHTML = "";
    const t = decoded();
    for (let i = 0; i < Math.min(t.length, 600); i++) el("span", { class: t[i] === "?" ? "" : (t[i] === plain[i] ? "ok" : "no") }, tx, t[i] === "?" ? cipher[i].toUpperCase() : t[i]);
    const kb = document.getElementById("fa-key"); kb.innerHTML = "";
    for (let c = 0; c < 26; c++) {
      if (!cc[c]) continue;
      const truth = A[key.indexOf(A[c])];
      const b = el("button", { type: "button", class: (sel === c ? "sel " : "") + (dec[c] === "?" ? "" : dec[c] === truth ? "ok" : "no") }, kb);
      b.append(A[c].toUpperCase()); el("i", {}, b, `→ ${dec[c]}`);
      b.addEventListener("click", () => { sel = sel === c ? null : c; paint(); });
    }
  }
  // manual swap: choose a cipher letter, then type the plain letter on the keyboard
  document.addEventListener("keydown", e => {
    if (sel === null || !/^[a-z]$/i.test(e.key)) return;
    const p = e.key.toLowerCase(), other = dec.indexOf(p);
    if (other >= 0) dec[other] = dec[sel];
    dec[sel] = p; sel = null;
    say(`Swapped by hand: ${acc()}% right.`);
    paint();
  });
  document.getElementById("fa-new").addEventListener("click", newKey);
  document.getElementById("fa-rank").addEventListener("click", rank);
  document.getElementById("fa-pairs").addEventListener("click", pairs);
  document.getElementById("fa-len").addEventListener("change", load);
  newKey();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def first_read(br):
    """In words: from which length the letter-pair search reads most messages."""
    for b in br:
        if b["pairsread"] * 2 > b["trials"]:
            return f"{b['pairsread']} of {b['trials']} messages at {b['n']:,} letters, and more as the messages grow"
    return "no message"


def family():
    D = Diagram(1000, 640, "How frequency analysis combined older ideas, and the arms race it started")
    W, H = 210, 86
    nodes = {
        "cnt": (20, 20, "Counting", "", "tally marks, Era 1 topic 1", "ink"),
        "sub": (395, 20, "Substitution ciphers", "", "one sign for each letter", "ink"),
        "qur": (770, 20, "Close study of texts", "letters of the Qur'an", "a conjecture", "ink"),
        "kin": (395, 170, "Al-Kindi's method", "⊕ count, rank, pair; then letter company", "Baghdad, c. 850 (estimate)", "red"),
        "alb": (20, 330, "Polyalphabetic ciphers", "many alphabets in turn", "Alberti, first to propose", "ink"),
        "fri": (20, 480, "Index of coincidence", "⊕ counting finds the key length", "Friedman, 1922", "ink"),
        "sim": (395, 330, "Simonetta's manual", "deciphering Latin and Italian", "by 1474", "ink"),
        "mar": (770, 330, "Markov's chained events", "vowels and consonants in a text", "Ycart 2013", "blue"),
        "mac": (770, 480, "Machine decipherment", "⊕ search by letter pairs", "this page's program", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("cnt", "kin", ports=("bottom", "top:0.2"))
    D.edge("sub", "kin", ports=("bottom", "top"))
    D.edge("qur", "kin", ports=("bottom", "top:0.8"), dashed=True)
    D.edge("kin", "alb", ports=("bottom:0.1", "top:0.7"))
    D.edge("alb", "fri", ports=("bottom", "top"))
    D.edge("kin", "sim", ports=("bottom", "top"), dashed=True)
    D.edge("kin", "mar", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("mar", "mac", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: links of ideas whose transmission is not documented (the Qur'an hypothesis; how Europe learned the method).", "caption")
    return D


def chain(d):
    k, io, br = d["keys"], d["ioc"], d["breaks"]
    b800 = next(b for b in br if b["n"] == 800)
    steps = [
        (f"A substitution cipher has 26! keys, {k['n']:.2e}: trying them all is hopeless".replace("e+", " × 10^"),
         "Count the signs, rank them, and pair them with a language's letters", "al-Kindi, 9th century"),
        (f"Counts alone never settle: ranking reads only {b800['rank']}% of an 800-letter message",
         f"Look at which letters keep company: a search on letter pairs reads {b800['pairs']}%", "al-Kindi's second method, by machine"),
        ("Ciphers learn to hide the counts",
         f"Polyalphabetic ciphers use several alphabets in turn: the index of coincidence falls from {io['plain']} to {io['vig']}", "Alberti"),
        ("But a repeating key repeats its alphabets",
         f"The index of coincidence of every k-th letter finds the key length: {d['period']['len']}", "Friedman, 1922"),
        ("Any repetition can be counted",
         f"A one-time pad, a fresh random key for every letter: index {io['pad']}, the uniform {io['uni']}", "nothing left to count"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: the arms race between ciphers and counting")
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
    sample, message = text_block(ctx["java"], "SAMPLE"), text_block(ctx["java"], "MESSAGE")
    js = FA_JS.replace("__SAMPLE__", json.dumps(sample)).replace("__MESSAGE__", json.dumps(message))
    s, k, br, io, per = d["sample"], d["keys"], d["breaks"], d["ioc"], d["period"]
    top12 = s["top"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Counting is as old as tally marks (Era 1, topic 1), and substitution ciphers are older than al-Kindi. His step was to count the secret signs against the letters of a whole language, gathered in advance. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: al-Kindi's method. Blue: the letter-pair statistics that his second method needs, as Markov later used them and as this page's program does."),
        ]),
        dict(id="break", eyebrow="Try it", title="Break a cipher", toc="Try it", blocks=[
            dict(type="p", text="A secret message has been enciphered with a random substitution key. **1. Rank the counts** pairs its signs with English letters by how common they are, al-Kindi's first method. **2. Letter pairs** then swaps letters while the text's letter pairs grow more like English, his second method done by machine. Shorten the message and watch the counts stop working. You can also fix letters by hand: click a cipher letter in the key, then type the plain letter."),
            dict(type="widget", html=FA_HTML, js=js, css=FA_CSS,
                 fallback=dict(type="svg", name="example", draw=example_svg(d), alt="A 400-letter cipher read by ranking and then by letter pairs", width=960),
                 note="In the interactive edition you can break a fresh cipher, change the message length, and swap letters by hand."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="method", eyebrow="How it works", title="Count, rank, pair; then look at the company", toc="How it works", blocks=[
            dict(type="p", text="In al-Kindi's own words, in an English excerpt: \"Among the expedients we use in cryptanalyzing a cryptogram if the language is already known, is to acquire a fairly long\" sample of plain text, count and rank its letters, and match the ranking to the cryptogram. For short cryptograms, where the counts cannot be trusted, he adds a \"qualitative\" method: look at which letters occur together."),
            dict(type="p", text=f"The program's reference sample is {s['n']:,} letters of ordinary English written for it. Its letters ranked: **{s['rank']}**. The twelve most common, {top12}, are close to the printers' \"etaoin shrdlu\", which Wikipedia gives as the twelve most frequent letters of typical English; a different sample shuffles the middle of the list."),
            dict(type="table", head=["Letters in the message", "Ranking alone: letters right", "Messages read (95% right)", "Then letter pairs: letters right", "Messages read"], num=[0, 1, 2, 3, 4],
                 rows=[[f"{b['n']:,}", f"{b['rank']}%", f"{b['rankread']} of {b['trials']}", f"{b['pairs']}%", f"{b['pairsread']} of {b['trials']}"] for b in br]),
            dict(type="p", text=f"Ranking alone never read a message, even the whole one: close letters swap places in the ranking, and every swap garbles a word. Adding letter pairs read {first_read(br)}. Al-Kindi's two methods, ranks for a first guess and letter company to correct it, are the two halves of a working attack. There are {k['n']:,} keys; at a billion keys a second, trying them all would take {k['years']:,} years."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A cipher that changes each letter into another hides the letters but not their habits. Facts about a whole language, collected in advance, can be set against the message: the first procedure in this book that needs data as well as the problem in front of it."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A treatise found in an Istanbul archive", toc="The evidence", blocks=[
            dict(type="p", text="Abu Yusuf Ya'qub ibn Ishaq al-Kindi was born in Kufa about 801 (MacTutor's page title says 805) and died in Baghdad in 873; al-Ma'mun appointed him to the House of Wisdom (**documented**; the birth year is **disputed**). His *Risalah fi Istikhraj al-Mu'amma*, \"A Manuscript on Deciphering Cryptographic Messages\", is usually dated about 850, an estimate (**conjecture**). It is the earliest known description of frequency analysis; who first noticed the idea is unknown."),
            dict(type="p", text="The treatise came back to light only recently, and the date of its rediscovery is itself **disputed**: Simon Singh says 1987, in the Süleymaniye Ottoman Archive in Istanbul; Muslim Heritage says a search by Mrayati, Alam and al-Tayyan found it in 1979 and published it in Arabic in 1987. An Arabic–English edition followed in 2002. That close study of the Qur'an first revealed Arabic letter frequencies is a suggestion (**conjecture**). Whether Europe learned the method from Arabic sources is not settled: by 1474 Cicco Simonetta had written a manual on deciphering Latin and Italian (**conjecture** for the transmission)."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The index of coincidence", toc="Measured", blocks=[
            dict(type="p", text="In 1922 William Friedman defined the index of coincidence: the chance that two letters picked at random from a text are the same. It counts letters too, but it ignores which letter is which, so a substitution cannot change it."),
            dict(type="table", head=["Text", "Index of coincidence"], num=[1],
                 rows=[["The message, plain", io["plain"]], ["Substitution cipher", io["sub"]], [f"Vigenère cipher, key \"{io['key']}\"", io["vig"]],
                       ["One-time pad (a random key letter for every letter)", io["pad"]], ["Uniform: every letter equally likely, 1/26", io["uni"]]]),
            dict(type="p", text="A polyalphabetic cipher flattens the counts, which is what Alberti's idea was for. But if the key repeats, every k-th letter shares one alphabet. Guess a key length, split the text into that many columns, and take the average index of the columns:"),
            dict(type="table", head=["Guessed key length"] + [str(c[0]) for c in per["cols"]], num=list(range(1, len(per["cols"]) + 1)),
                 rows=[["Average index"] + [c[1] for c in per["cols"]]]),
            dict(type="p", text=f"Lengths {per['len']} and {2 * per['len']} jump back to the index of plain English: the key has **{per['len']} letters**, and each column is an ordinary substitution cipher, open to al-Kindi's method again."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Letters that keep company", toc="Full circle", blocks=[
            dict(type="p", text="Al-Kindi's second method asks which letters follow which. A thousand years later that question became mathematics. Bernard Ycart's history of letter counting notes that \"the alternation vowel-consonants was the only example that Markov ever gave of his theory of chained events\": a Markov chain, the probability of each symbol given the one before."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program's attack is exactly such a chain: it scores a decryption by the probability of each letter given the one before, learned from {s['n']:,} letters of English, and swaps letters until the chain is happy. Al-Kindi's \"qualitative\" method, mechanized with Markov's chains, read the whole message for 20 keys out of 20."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why can't the cipher hide which sign is most common?", "Each letter always becomes the same sign, so the sign for e appears exactly as often as e does."),
            ("Why does ranking alone fail even on a long message?", "Letters with similar frequencies (r, s, h, i, n, o) swap places from one text to another, and every swap garbles words. Ranking gets the shape; letter pairs fix the details."),
            ("A cipher sign appears as a doubled pair, like xx, many times. What might it be?", "In English, common doubled letters include ll, ee, ss and oo: a hint of the kind al-Kindi's qualitative method uses."),
            ("Why doesn't a substitution change the index of coincidence?", "The index only asks how often two letters match. Renaming the letters does not change which positions match."),
            ("What does a one-time pad leave to count?", f"Nothing useful: its index is {io['pad']}, the value for letters chosen at random."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Al-Kindi's Treatise on Cryptanalysis", text="The Arabic–English edition by Mrayati, Meer Alam and at-Tayyan (KFCRIS and KACST), volume 1 of a series on the Arabic origins of cryptology; the treatise's shelfmark in the Süleymaniye library is not given in the sources opened.",
                 draw=C.draw_manuscript, link="https://iacr.org/newsletter/v20n3/newbooks.html", link_text="IACR Newsletter notice",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Index of coincidence", "Wikipedia", "https://en.wikipedia.org/wiki/Index_of_coincidence", "Friedman's 1922 measure, its values for English and random text, and how it finds a Vigenère key length"),
        ]),
        C.prove_it_section(ctx, "FrequencyAnalysis", d["checks"],
                           "for every message length and key: the substitution keeps the index of coincidence, the true key reads the message, and the attack's accuracy; then the indexes of the Vigenère cipher and one-time pad, and the key length.",
                           ["static char[] byRanking(", "static char[] climb("]),
    ]
    return dict(
        title="Frequency Analysis", date="9th century CE",
        description="Era 2, topic 7 of The Algorithm Evolution Atlas: al-Kindi's frequency analysis, with a cipher to break by ranks and letter pairs, and Friedman's index of coincidence.",
        lede="A substitution cipher hides each letter but not how often it appears. Al-Kindi counted the secret signs against the letters of a whole language, and for short messages looked at which letters keep company.",
        fieldnote="A philosopher in Baghdad wrote the trick down: count, rank, pair. It is the first procedure in my catalog that needs facts about a whole language, gathered in advance, as well as the message itself.",
        card=[("When", "Al-Kindi, c. 801–873; the treatise usually dated about 850 (**conjecture**)"),
              ("Where", "Baghdad, the House of Wisdom"),
              ("What hurt", f"26! substitution keys: far too many to try"),
              ("The fix", "Count and rank the signs against a language's letters; then use letter company"),
              ("Cost", f"One pass to count; ranking plus letter pairs read 400-letter messages {next(b for b in br if b['n'] == 400)['pairsread']} times in 20")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `FrequencyAnalysis.java`.",
    )
