"""Era 4, topic 8: breaking Enigma. Every number is parsed from Enigma.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"test: .*?: AAAAA becomes (\w+)$", ln):
            d["test"] = m.group(1)
        elif m := re.match(r"self: (\d+) random 60-letter messages.*?\((\d+) cases\)$", ln):
            d["self"] = dict(n=int(m.group(1)), cases=int(m.group(2)))
        elif m := re.match(r"catalogue: (\d+) settings .*? \((\d+) products\) ; (\d+) different characteristics, (\d+) of them belonging to a single setting, at most (\d+) settings sharing one ;", ln):
            d["cat"] = dict(settings=int(m.group(1)), products=int(m.group(2)), distinct=int(m.group(3)), unique=int(m.group(4)), largest=int(m.group(5)))
        elif m := re.match(r"day: (\d+) intercepted indicators fixed all three products ; their cycle lengths \[(.+?)\] ; the catalogue lists (\d+) settings?", ln):
            d["day"] = dict(n=int(m.group(1)), cyc=m.group(2), cand=int(m.group(3)))
        elif m := re.match(r"bombe: crib (\w+) under cipher (\w+) ; test letter (\w) ; (\d+) rotor positions x 26 guesses tested ; (\d+) stops? survives?, .*? partners of (\d+) letters", ln):
            d["bombe"] = dict(crib=m.group(1), cipher=m.group(2), test=m.group(3), pos=int(m.group(4)), stops=int(m.group(5)), known=int(m.group(6)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def path_svg(d):
    """The path of one key press through the machine."""
    def draw(t, standalone):
        out = []
        boxes = [("key", 20), ("plugboard", 110), ("rotor III", 230), ("rotor II", 330), ("rotor I", 430), ("reflector", 540)]
        for name, x in boxes:
            w = 90 if name != "key" else 60
            out.append(C.rect(x, 40, w, 120, t["surface"], t["red"] if name == "reflector" else t["ink2"], 2))
            out.append(C.text(x + w / 2, 182, name, t["muted"], 12.5, "middle"))
        out.append(C.path("M50,80 L630,80", t["blue"], "none", 3) + C.path("M630,80 L630,120", t["red"], "none", 3) + C.path("M630,120 L50,120", t["red"], "none", 3))
        out.append(C.text(50, 72, "in", t["blue"], 12, "start", 700))
        out.append(C.text(50, 140, "out to a lamp", t["red"], 12, "start", 700))
        out.append(C.text(20, 220, "The rightmost rotor turns before every key press, so the wiring changes with every letter.", t["ink"], 13.5))
        out.append(C.text(20, 242, "The reflector sends the current back by another route: no letter can light its own lamp.", t["ink"], 13.5))
        out.append(C.text(20, 274, f"Rotors I, II, III, reflector B, start AAA: AAAAA becomes {d['test']} (checked by Enigma.java).", t["muted"], 12.5))
        out.append(C.text(20, 294, f"Rejewski's catalogue: {d['cat']['settings']:,} settings, {d['cat']['distinct']:,} different characteristics; a simulated day falls to {d['day']['cand']} settings.", t["muted"], 12.5))
        out.append(C.text(20, 314, f"A Bombe run on a {len(d['bombe']['crib'])}-letter crib over all {d['bombe']['pos']:,} positions leaves {d['bombe']['stops']} stop{'s' if d['bombe']['stops'] != 1 else ''}: the true setting.", t["muted"], 12.5))
        return C.svg_doc(780, 330, "".join(out), "The path of a key press through an Enigma machine", t, standalone, 0.55, 780)
    return draw


EN_HTML = """
<div class="board en-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="en-o">Rotors <select id="en-o"></select></label>
      <label>Start <select id="en-p0"></select><select id="en-p1"></select><select id="en-p2"></select></label>
    </div>
    <div class="controls"><label for="en-plug">Plug cables <input id="en-plug" type="text" value="AV BS CG DL FU HZ IN KM OW RX" spellcheck="false"></label></div>
    <div class="controls"><label for="en-msg">Message <input id="en-msg" type="text" value="WETTERVORHERSAGE" spellcheck="false" maxlength="80"></label></div>
    <div class="presets" id="en-pre"></div>
  </div>
  <div style="min-width:0">
    <ol class="en-steps" id="en-steps"></ol>
    <div class="eyebrow">The 13 swaps at the next key press</div>
    <div class="en-pairs" id="en-pairs"></div>
    <p class="say" id="en-say" aria-live="polite"></p>
  </div>
</div>
"""

EN_CSS = """
.en-board select{font:inherit;font-size:13.5px;padding:2px 4px;margin-right:3px}
.en-board input[type=text]{font:13px var(--mono);width:min(260px,70vw);padding:4px 6px;text-transform:uppercase}
.en-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:6px}
.en-steps .m{font-family:var(--mono);font-size:13px;overflow-wrap:anywhere;letter-spacing:.06em}
.en-pairs{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0;font:600 12.5px var(--mono)}
.en-pairs span{border:1px solid var(--axis);padding:2px 6px;background:var(--surface)}
"""

EN_JS = r"""
(() => {
  const msgEl = document.getElementById("en-msg");
  if (!msgEl) return;
  const ROT = ["EKMFLGDQVZNTOWYHXUSPAIBRCJ", "AJDKSIRUXBLHWTMCQGZNPYFVOE", "BDFHJLCPRTXVZNYEIWGAKMUSQO"].map(s => [...s].map(c => c.charCodeAt(0) - 65));
  const BWD = ROT.map(w => { const b = []; w.forEach((v, i) => { b[v] = i; }); return b; });
  const NOTCH = [16, 4, 21], REF = [..."YRUHQSLDPXNGOKMIEBFZCWVJAT"].map(c => c.charCodeAt(0) - 65);
  const ORD = [[0, 1, 2], [0, 2, 1], [1, 0, 2], [1, 2, 0], [2, 0, 1], [2, 1, 0]], RN = ["I", "II", "III"];
  const oSel = document.getElementById("en-o");
  ORD.forEach((o, i) => el("option", {value: i}, oSel, o.map(r => RN[r]).join("-")));
  const pSel = [0, 1, 2].map(k => document.getElementById("en-p" + k));
  pSel.forEach(s => { for (let i = 0; i < 26; i++) el("option", {value: i}, s, String.fromCharCode(65 + i)); });
  function machine() {
    const order = ORD[+oSel.value], pos = pSel.map(s => +s.value), plug = [...Array(26).keys()];
    let bad = "";
    (document.getElementById("en-plug").value.toUpperCase().match(/[A-Z]{2}/g) || []).forEach(p => {
      const a = p.charCodeAt(0) - 65, b = p.charCodeAt(1) - 65;
      if (a === b || plug[a] !== a || plug[b] !== b) bad = p; else { plug[a] = b; plug[b] = a; }
    });
    const step = () => {
      const mid = pos[1] === NOTCH[order[1]], right = pos[2] === NOTCH[order[2]];
      if (mid) { pos[0] = (pos[0] + 1) % 26; pos[1] = (pos[1] + 1) % 26; } else if (right) pos[1] = (pos[1] + 1) % 26;
      pos[2] = (pos[2] + 1) % 26;
    };
    const scr = c => {
      for (let k = 2; k >= 0; k--) c = (ROT[order[k]][(c + pos[k]) % 26] - pos[k] + 26) % 26;
      c = REF[c];
      for (let k = 0; k <= 2; k++) c = (BWD[order[k]][(c + pos[k]) % 26] - pos[k] + 26) % 26;
      return c;
    };
    return {type: s => [...s].map(ch => { step(); return String.fromCharCode(65 + plug[scr(plug[ch.charCodeAt(0) - 65])]); }).join(""),
            pairs: () => { const p0 = pos.slice(); step(); const out = []; for (let c = 0; c < 26; c++) { const x = plug[scr(plug[c])]; if (c < x) out.push(String.fromCharCode(65 + c, 65 + x)); } pos.splice(0, 3, ...p0); return out; },
            bad, pos};
  }
  const L = n => String.fromCharCode(65 + n);
  function show() {
    const msg = msgEl.value.toUpperCase().replace(/[^A-Z]/g, "");
    const m1 = machine(), cipher = m1.type(msg);
    const back = machine().type(cipher);
    const m3 = machine(); m3.type(msg); const after = m3.pos.map(L).join("");
    const ol = document.getElementById("en-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    li(`message <span class="m">${msg || "—"}</span>`);
    li(`cipher <span class="m">${cipher || "—"}</span>`);
    li(`the cipher typed on a machine set the same way: <span class="m">${back || "—"}</span>`);
    li(`rotor positions after the message: <span class="m">${after}</span>`);
    const pairs = machine().pairs();
    const pe = document.getElementById("en-pairs"); pe.innerHTML = "";
    pairs.forEach(p => el("span", {}, pe, p[0] + "↔" + p[1]));
    let same = 0; for (let i = 0; i < msg.length; i++) if (msg[i] === cipher[i]) same++;
    document.getElementById("en-say").textContent = m1.bad ? `The cable ${m1.bad} clashes with another and was left out.` :
      `${msg.length} letters, and ${same === 0 ? "not one" : same} enciphered as itself. Every position swaps the alphabet in 13 pairs, so the same setting deciphers.`;
  }
  const pre = document.getElementById("en-pre");
  [["The published test", () => { oSel.value = 0; pSel.forEach(s => { s.value = 0; }); document.getElementById("en-plug").value = ""; msgEl.value = "AAAAA"; }],
   ["Ten cables, a weather report", () => { oSel.value = 3; pSel[0].value = 7; pSel[1].value = 20; pSel[2].value = 2; document.getElementById("en-plug").value = "AV BS CG DL FU HZ IN KM OW RX"; msgEl.value = "WETTERVORHERSAGE"; }]]
    .forEach(([n, f]) => { const b = el("button", {type: "button"}, pre, n); b.addEventListener("click", () => { f(); show(); }); });
  [oSel, ...pSel].forEach(s => s.addEventListener("change", show));
  ["en-plug", "en-msg"].forEach(id => document.getElementById(id).addEventListener("input", show));
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the breaking of Enigma combined older ideas, and where it led")
    W = 210
    nodes = {
        "freq": (20, 20, "Frequency analysis", "count letters to read a cipher", "Era 2 topic 7", "ink"),
        "perm": (395, 20, "Permutations", "the algebra of rearrangements", "19th century", "ink"),
        "mach": (770, 20, "Electrical machines", "circuits that count and sort", "Era 3 topic 13", "ink"),
        "rej": (395, 170, "Rejewski, Różycki, Zygalski", "⊕ cycle structure the plugboard cannot hide", "1932–1938", "red"),
        "bomba": (20, 330, "The bomba", "a machine that searches settings", "1938", "ink"),
        "bombe": (395, 330, "Turing and Welchman's Bombe", "test a crib; reject by contradiction", "1940", "ink"),
        "sh": (770, 330, "Shannon's secrecy theory", "ciphers judged by information", "1949", "ink"),
        "today": (395, 480, "Cryptography today", "designed for attackers with computers", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("freq", "rej", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("perm", "rej", ports=("bottom", "top"))
    D.edge("mach", "rej", ports=("bottom", "top:0.85"))
    D.edge("rej", "bomba", ports=("bottom:0.1", "top:0.7"))
    D.edge("rej", "bombe", ports=("bottom", "top"))
    D.edge("rej", "sh", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("bombe", "today", ports=("bottom", "top"))
    D.edge("sh", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: frequency counts were what Enigma defeated; Shannon's 1949 theory of secrecy is named for context and is not a topic here.", "caption")
    return D


def chain(d):
    c, dy, b = d["cat"], d["day"], d["bombe"]
    steps = [
        ("A machine cipher: letter counts tell nothing, and the settings change every day",
         "Permutation theory: the doubled message key links letters 1 and 4, 2 and 5, 3 and 6", "Rejewski, 1932"),
        (f"{c['settings']:,} rotor settings, and a plugboard on top",
         f"Cycle lengths ignore the plugboard: catalogue them. Here, a day's traffic leaves {dy['cand']} settings", "cyclometer, about 1934–1937"),
        ("A new reflector (1937), a new key procedure (1938): the catalogue is useless",
         "Machines that search: the bomba; Zygalski's perforated sheets", "1938"),
        ("More rotors and cables, and no doubled keys to exploit",
         f"Turing's Bombe: test a guessed text at every position. Here, {b['stops']} stop in {b['pos'] * 26:,} guesses", "Turing and Welchman, 1940"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from permutations to machines that search")
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
    s, c, dy, b = d["self"], d["cat"], d["day"], d["bombe"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Frequency analysis (Era 2, topic 7) had broken ciphers for a thousand years; Enigma's turning rotors defeated it. The Polish mathematicians brought in the algebra of permutations, and then machines of their own to search the settings; the British scaled the search up. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the Polish Cipher Bureau's work of 1932–1938. Blue: where it led."),
        ]),
        dict(id="machine", eyebrow="Try it", title="Type on an Enigma", toc="Try it", blocks=[
            dict(type="p", text="Choose the rotor order and start positions, plug some cables, and type. The page enciphers your message, then types the cipher text on a second machine set the same way, and gets the message back. Watch for two things: no letter is ever enciphered as itself, and at every position the machine simply swaps the alphabet in 13 pairs (shown on the right for the next key press)."),
            dict(type="widget", html=EN_HTML, js=EN_JS, css=EN_CSS,
                 fallback=dict(type="svg", name="path", draw=path_svg(d), alt="The path of a key press through an Enigma machine", width=780),
                 note="In the interactive edition you can set an Enigma I and type on it."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Swaps, cycles, and contradictions", toc="How it works", blocks=[
            dict(type="p", text=f"**The machine.** A key press goes through the plugboard, three rotors, the reflector, back through the rotors and the plugboard, to a lamp. The right rotor turns before every letter and carries the next one at its notch. The program builds the Enigma I with the wirings of 1930 and reproduces the published test: rotors I, II, III, reflector B, start AAA, AAAAA becomes **{d['test']}**. Because of the reflector, each position swaps the letters in pairs: the program enciphered {s['n']:,} random messages twice and got them back every time, and checked all {s['cases']:,} letter–position cases for rotors I-II-III: no letter ever goes to itself."),
            dict(type="p", text="**Rejewski's characteristic.** Until 1938 operators enciphered each message's three-letter key twice, so cipher letters 1 and 4 come from the same letter. If A and D are the machine's swaps at positions 1 and 4, then letter 1 → letter 4 is the product of A and D, and a day's traffic reveals it completely. Its cycles always come in pairs of equal length, and the plugboard only relabels the letters in them, never the lengths."),
            dict(type="table", head=["Catalogue (reflector A, used until November 1937)", "Count"], num=[1],
                 rows=[["rotor settings (6 orders × 17,576 positions)", f"{c['settings']:,}"],
                       ["products AD, BE, CF checked: cycles in pairs every time", f"{c['products']:,}"],
                       ["different characteristics", f"{c['distinct']:,}"],
                       ["characteristics that belong to a single setting", f"{c['unique']:,}"],
                       ["most settings sharing one characteristic", f"{c['largest']:,}"]]),
            dict(type="p", text=f"The program then simulates a day: a secret setting and plugboard, and the doubled keys of {dy['n']} messages, enough to fix all three products. The first product's cycle lengths are [{dy['cyc']}]; looking up the three together, the catalogue lists **{dy['cand']}** settings, the true one among them. What is left is a short list to try by hand."),
            dict(type="p", text=f"**The Bombe.** From 1940 the doubled key was gone and the search started from a crib, a guessed piece of plain text. The program takes the crib {b['crib']} and its cipher text {b['cipher']}. At each rotor position it assumes a plug partner for the commonest letter ({b['test']}) and follows what the crib forces: if plain letter x is plugged to a, the rotors send a to some b, so cipher letter y must be plugged to b. A letter plugged to two different letters is a contradiction, and the guess is rejected. Of {b['pos']:,} positions × 26 guesses, **{b['stops']}** survive{'s' if b['stops'] == 1 else ''}: the true setting, where the crib fixes the partners of {b['known']} letters, all correct."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Find a property of the secret that ignores most of the key: cycle lengths that the plugboard cannot change, or a contradiction that rules out a rotor position whatever the plugs are. Then search only what is left, by machine."),
        ]),
        dict(id="measured", eyebrow="Measured", title="From a hundred thousand settings to one", toc="Measured", blocks=[
            dict(type="table", head=["Stage", "Candidates left"], num=[1],
                 rows=[["rotor order and position, before any analysis", f"{c['settings']:,}"],
                       ["after Rejewski's catalogue, on one simulated day", f"{dy['cand']:,}"],
                       [f"Bombe guesses (positions × 26 plug guesses), {len(b['crib'])}-letter crib", f"{b['pos'] * 26:,}"],
                       ["Bombe stops", f"{b['stops']:,}"]]),
            dict(type="p", text="The program's Bombe follows each forced plug in both directions (if x is plugged to y, then y is plugged to x), which is the effect of Welchman's diagonal board; the first Bombe of March 1940 had none, and would have stopped more often. Ring settings are fixed at A throughout, a simplification the real attacks did not have."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Warsaw, 1932 to 1939", toc="The evidence", blocks=[
            dict(type="p", text="Rejewski joined the Cipher Bureau in Warsaw full-time on 1 September 1932 with Różycki and Zygalski (MacTutor); in December 1932 he worked out the rotor wirings using \"the theory of permutations and groups\", with German manuals and keys that French intelligence had bought from Hans-Thilo Schmidt (Wikipedia). The cyclometer, \"probably in 1934 or 1935\", catalogued 105,456 settings; making the catalogue \"was laborious and took over a year\"; it had to be redone after the reflector change of 1 November 1937 and became \"completely useless\" on 15 September 1938 (Wikipedia, Cyclometer)."),
            dict(type="p", text="The bomba, built with the AVA Radio Manufacturing Company, was \"the first cryptanalytic machine to break Enigma codes\" (IEEE Milestone, 2014); the Poles shared their work with the British and French near Warsaw in July 1939. The first British Bombe, \"Victory\", was installed at Bletchley Park on 18 March 1940; each position that led to \"a logical contradiction\" was ruled out (Wikipedia, Bombe). The wirings are from Wikipedia's Enigma rotor details, whose test vector is marked \"citation needed\"; the program reproduces it."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Search as a weapon", toc="Full circle", blocks=[
            dict(type="p", text="Enigma was strong against people with pencils and weak against people with machines that could test thousands of settings an hour. Modern ciphers are designed the other way round: their keys are so long that no machine could try a useful fraction of them, and they are designed on the assumption that the attacker knows everything except the key, as the Poles knew the machine from its manuals."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Rejewski's cycles turn {c['settings']:,} settings into {c['distinct']:,} fingerprints; Turing's contradictions turn {b['pos'] * 26:,} guesses into {b['stops']} stop{'s' if b['stops'] != 1 else ''}. Both find what the secret cannot hide."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does typing the cipher text on a machine set the same way give back the message?", "At each position the machine swaps letters in pairs: if A becomes Q, then Q becomes A."),
            ("A crib says ATTACK is under the cipher letters QTXBNE. Can that alignment be right?", "No: the second letter would have T enciphered as T, and Enigma never enciphers a letter as itself. Slide the crib along."),
            ("Why do the plug cables not change the cycle lengths of AD?", "The plugboard P acts on the way in and on the way out, so the product becomes P·AD·P: the same cycles with the letters renamed. Renaming letters cannot change a cycle's length."),
            ("Why were the doubled message keys a gift?", "Letters 1 and 4 hid the same letter, so every message linked the machine's swaps at positions 1 and 4, day after day."),
            ("What does a Bombe stop mean?", "That the guess for this position caused no contradiction. It is a candidate, checked by hand on a replica Enigma."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="IEEE Milestone plaque, Warsaw (2014)", text="\"First Breaking of Enigma Code by the Team of Polish Cipher Bureau, 1932–1939\".",
                 draw=C.draw_manuscript, link="https://ethw.org/Milestones:First_Breaking_of_Enigma_Code_by_the_Team_of_Polish_Cipher_Bureau%2C_1932-1939", link_text="ETHW", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Enigma", d["checks"],
                           f"the published test vector, {s['n']:,} messages enciphered and recovered, {s['cases']:,} positions without a fixed letter, cycles in pairs for all {c['products']:,} products, the plugboard's invariance, the simulated day, and the Bombe run over every position.",
                           ["int scramble(", "static boolean assign("]),
    ]
    return dict(
        title="Breaking Enigma", date="1932–1940",
        description="Era 4, topic 8 of The Algorithm Evolution Atlas: Rejewski's permutation attack on Enigma and the Bombe's search by contradiction.",
        lede="The German army's cipher machine changed its wiring with every letter and its settings every day. Three Polish mathematicians attacked it with the theory of permutations and machines of their own; the British turned their methods into a search by contradiction, run by machine.",
        fieldnote=f"The machine could not hide two things: a letter is never itself, and the lengths of certain cycles do not care about the plug cables. On my simulated day, {dy['n']} intercepted indicators narrowed {c['settings']:,} settings to {dy['cand']}. Rejewski did it with paper, a catalogue, and a year of patience.",
        card=[("When", "Rejewski 1932; bomba 1938; Bombe 1940"),
              ("Where", "Warsaw; Bletchley Park"),
              ("What hurt", "Too many settings to try, changed daily"),
              ("The fix", "Invariants that ignore the plugboard; search by contradiction"),
              ("Result", f"{c['settings']:,} settings → {dy['cand']}; {b['pos'] * 26:,} guesses → {b['stops']} stop")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Enigma.java`.",
    )
