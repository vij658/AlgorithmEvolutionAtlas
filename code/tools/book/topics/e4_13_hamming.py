"""Era 4, topic 13: Hamming's codes. Every number is parsed from HammingCodes.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"code: .*?: ([01 ]+) ; every two of them differ in at least (\d+) places \((\d+) pairs\)$", ln):
            d["code"] = dict(words=m.group(1).split(), dist=m.group(2), pairs=m.group(3))
        elif m := re.match(r"errors: all (\d+) single errors corrected.*? ; all (\d+) double errors fool .*? all (\d+) single errors are corrected and all (\d+) double errors detected$", ln):
            d["err"] = dict(s7=int(m.group(1)), d7=int(m.group(2)), s8=int(m.group(3)), d8=int(m.group(4)))
        elif ln.startswith("family: "):
            d["fam"] = re.findall(r"\((\d+),(\d+)\): (\d+) checks for \d+ message bits, (\d+)% of the bits", ln)
        elif m := re.match(r"channel: ([\d,]+) four-bit messages, each bit flipped with probability ([\d.]+) ; no code \(4 bits sent\): ([\d,]+) wrong \(([\d.]+)%, expected ([\d.]+)%\) ; Hamming \(7,4\), 7 bits: ([\d,]+) wrong \(([\d.]+)%, expected ([\d.]+)%\) ; each bit three times, 12 bits: ([\d,]+) wrong \(([\d.]+)%\)$", ln):
            g = m.groups()
            d["ch"] = dict(n=g[0], p=g[1], plain=g[2], plainp=g[3], plainx=g[4], ham=g[5], hamp=g[6], hamx=g[7], tri=g[8], trip=g[9])
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def checks_svg(d):
    word = d["code"]["words"][11]                       # the message 1011 (eleven)

    def draw(t, standalone):
        out = []
        x0, w = 150, 70
        out.append(C.text(20, 40, "position", t["muted"], 12.5))
        out.append(C.text(20, 66, "in binary", t["muted"], 12.5))
        for pos in range(1, 8):
            x = x0 + (pos - 1) * w
            out.append(C.text(x + w / 2, 40, str(pos), t["ink"], 15, "middle", 700))
            out.append(C.text(x + w / 2, 66, format(pos, "03b"), t["muted"], 13, "middle"))
        for r, k in enumerate([1, 2, 4]):
            y = 92 + r * 34
            out.append(C.text(20, y + 18, f"check {k} covers", t["blue"], 12.5, "start", 700))
            for pos in range(1, 8):
                if pos & k:
                    x = x0 + (pos - 1) * w
                    out.append(C.rect(x + 8, y, w - 16, 26, t["blue"] if pos == k else t["surface"], t["blue"], 1.5))
        y = 92 + 3 * 34 + 20
        out.append(C.text(20, y + 18, "sent (message 1011)", t["ink"], 12.5, "start", 700))
        recv = list(word)
        recv[5] = "1" if recv[5] == "0" else "0"
        for pos in range(1, 8):
            x = x0 + (pos - 1) * w
            out.append(C.text(x + w / 2, y + 18, word[pos - 1], t["ink"], 16, "middle", 700))
            out.append(C.text(x + w / 2, y + 52, recv[pos - 1], t["red"] if pos == 6 else t["ink"], 16, "middle", 700))
        out.append(C.text(20, y + 52, "received", t["red"], 12.5, "start", 700))
        out.append(C.text(20, y + 88, "Checks 2 and 4 fail (their positions now hold an odd number of 1s); check 1 passes.", t["muted"], 12.5))
        out.append(C.text(20, y + 108, "Failed checks 2 + 4 = 6: flip position 6 back. The code words are those listed by HammingCodes.java.", t["muted"], 12.5))
        return C.svg_doc(660, y + 122, "".join(out), "How the failed checks of the (7,4) code spell the position of an error", t, standalone, 0.55, 660)
    return draw


HM_HTML = """
<div class="board hm-board">
  <div style="min-width:0">
    <div class="eyebrow">Message: click to change</div>
    <div class="hm-row" id="hm-data"></div>
    <div class="eyebrow" style="margin-top:12px">Code word sent: positions 1 to 7 (checks at 1, 2, 4)</div>
    <div class="hm-row" id="hm-sent"></div>
    <div class="eyebrow" style="margin-top:12px">Received: click a bit to flip it</div>
    <div class="hm-row" id="hm-recv"></div>
  </div>
  <div style="min-width:0">
    <ol class="hm-steps" id="hm-steps"></ol>
    <p class="say" id="hm-say" aria-live="polite"></p>
  </div>
</div>
"""

HM_CSS = """
.hm-row{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}
.hm-row button{font:600 16px var(--mono);width:44px;height:48px;padding:0;display:flex;flex-direction:column;align-items:center;justify-content:center;line-height:1.1}
.hm-row button small{font-size:10px;font-weight:400;color:var(--muted)}
.hm-row button.chk{border-color:var(--blue);color:var(--blue)}
.hm-row button.bad{background:var(--red);color:var(--on-red);border-color:var(--red)}
.hm-row button.bad small{color:var(--on-red)}
.hm-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.hm-steps .m{font-family:var(--mono);font-size:12.5px}
"""

HM_JS = r"""
(() => {
  const dataEl = document.getElementById("hm-data");
  if (!dataEl) return;
  let data = [1, 1, 0, 1], flips = new Set([6]);
  const DATA_POS = [3, 5, 6, 7];
  function encode() {
    const w = Array(8).fill(0);
    DATA_POS.forEach((p, i) => { w[p] = data[i]; });
    for (const k of [1, 2, 4]) { let s = 0; for (let p = 1; p <= 7; p++) if (p & k && p !== k) s ^= w[p]; w[k] = s; }
    return w;
  }
  function show() {
    const sent = encode(), recv = sent.slice();
    flips.forEach(p => { recv[p] ^= 1; });
    dataEl.innerHTML = "";
    data.forEach((b, i) => { const bt = el("button", {type: "button"}, dataEl); bt.innerHTML = `${b}<small>d${i + 1}</small>`; bt.addEventListener("click", () => { data[i] ^= 1; show(); }); });
    const row = (id, w, click) => {
      const r = document.getElementById(id); r.innerHTML = "";
      for (let p = 1; p <= 7; p++) {
        const bt = el("button", {type: "button", class: ([1, 2, 4].includes(p) ? "chk " : "") + (click && flips.has(p) ? "bad" : "")}, r);
        bt.innerHTML = `${w[p]}<small>${p}</small>`;
        if (click) bt.addEventListener("click", () => { flips.has(p) ? flips.delete(p) : flips.add(p); show(); });
      }
    };
    row("hm-sent", sent, false); row("hm-recv", recv, true);
    const failed = [1, 2, 4].filter(k => { let s = 0; for (let p = 1; p <= 7; p++) if (p & k) s ^= recv[p]; return s === 1; });
    const syn = failed.reduce((a, b) => a + b, 0);
    const fixed = recv.slice(); if (syn) fixed[syn] ^= 1;
    const ok = fixed.every((v, i) => i === 0 || v === sent[i]);
    const ol = document.getElementById("hm-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    [1, 2, 4].forEach(k => li(`check ${k} (positions ${[1, 2, 3, 4, 5, 6, 7].filter(p => p & k).join(", ")}): ${failed.includes(k) ? "<b>fails</b>" : "passes"}`));
    li(`failed checks add up to <span class="m">${syn}</span>${syn ? ": flip position " + syn : ": nothing to correct"}`);
    const say = document.getElementById("hm-say");
    say.textContent = flips.size === 0 ? "No errors: every check passes." :
      flips.size === 1 ? `One error, at position ${[...flips][0]}: the failed checks point straight at it, and it is corrected.` :
      ok ? "Corrected." : `${flips.size} errors: the checks point at position ${syn || "none"}, and the "correction" ${syn ? "makes things worse" : "misses them"}. One code word can only be told from its neighbours one error away.`;
  }
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Hamming's codes combined older ideas, and where they led")
    W = 210
    nodes = {
        "bin": (20, 20, "Binary digits", "every symbol a 0 or a 1", "Era 3 topic 6", "ink"),
        "par": (395, 20, "Parity checks", "relay computers stop on an odd count", "1940s", "ink"),
        "sh": (770, 20, "Shannon's redundancy", "extra bits can beat noise", "topic 12", "ink"),
        "hm": (395, 170, "Hamming's codes", "⊕ overlapping checks that spell the position", "1947–1950", "red"),
        "dist": (20, 330, "Distance", "count the places where words differ", "Hamming 1950", "ink"),
        "secded": (395, 330, "One more parity bit", "correct one error, detect two", "Hamming 1950", "ink"),
        "strong": (770, 330, "Stronger codes", "many errors, bursts, erasures", "later", "ink"),
        "today": (395, 480, "Codes today", "memory, storage, discs, links to space", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("bin", "hm", ports=("bottom", "top:0.15"))
    D.edge("par", "hm", ports=("bottom", "top"))
    D.edge("sh", "hm", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("hm", "dist", ports=("bottom:0.1", "top:0.7"))
    D.edge("hm", "secded", ports=("bottom", "top"))
    D.edge("hm", "strong", ports=("bottom:0.9", "top:0.3"))
    D.edge("secded", "today", ports=("bottom", "top"))
    D.edge("strong", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: Shannon's theorem says codes like these exist; whether Hamming's code reached Shannon before 1950 is not settled in the sources opened.", "caption")
    return D


def chain(d):
    e, f = d["err"], d["fam"]
    steps = [
        ("A relay computer finds an error by parity, and at weekends simply drops the job",
         "Several parity checks over overlapping positions: 1, 2, 4, 8, …", "Hamming, 1947–1950"),
        ("A failed check says something is wrong, not where",
         f"The failed checks spell the position in binary: all {e['s7']} single errors corrected", "the (7,4) code"),
        (f"Two errors fool it: all {e['d7']} double errors are mis-corrected",
         f"An eighth bit for the whole word's parity: all {e['d8']} double errors detected", "distance 4"),
        ("Three check bits for every four of message is expensive",
         f"Longer codes: ({f[-1][0]},{f[-1][1]}) carries {f[-1][3]}% message", "the same rule, more positions"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from parity to error correction")
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
    cw, e, f, ch = d["code"], d["err"], d["fam"], d["ch"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A parity check (is the number of 1s even?) was already how relay computers noticed their own errors. Hamming's addition was to use several checks over overlapping groups of positions, arranged so that the pattern of failures is the binary number of the faulty position. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Hamming's codes. Blue: error correction today."),
        ]),
        dict(id="flip", eyebrow="Try it", title="Flip a bit and watch the checks find it", toc="Try it", blocks=[
            dict(type="p", text="Choose a 4-bit message; the page adds the three check bits (blue) at positions 1, 2 and 4. Then flip any bit of the received word. With one flipped bit, the failed checks add up to its position and the word is repaired. Flip two and see what goes wrong."),
            dict(type="widget", html=HM_HTML, js=HM_JS, css=HM_CSS,
                 fallback=dict(type="svg", name="checks", draw=checks_svg(d), alt="How the failed checks of the (7,4) code spell the position of an error", width=660),
                 note="In the interactive edition you can choose the message and flip any bits."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Checks that spell a position", toc="How it works", blocks=[
            dict(type="p", text="**The arrangement.** Number the positions 1 to 7 and write each number in binary: 1 = 001, 2 = 010, 3 = 011, …, 7 = 111. Check bit 1 makes the parity even over every position whose number ends in 1 (1, 3, 5, 7); check bit 2 over those with the middle digit 1 (2, 3, 6, 7); check bit 4 over those with the first digit 1 (4, 5, 6, 7). The message goes in positions 3, 5, 6 and 7. If one bit flips, exactly the checks whose groups contain it fail, and they add up to its position."),
            dict(type="p", text=f"**The sixteen code words**, as the program builds them (position 1 first): {', '.join(cw['words'])}. Every two differ in at least {cw['dist']} places (all {cw['pairs']} pairs checked), so one error leaves a word nearer its own code word than any other. Each code word and its 7 one-bit neighbours make 8 words, and 16 × 8 = 128 = 2⁷: every 7-bit word is within one place of exactly one code word. Hamming: \"a seven-position single error correcting code admits of 16 code symbols\"."),
            dict(type="table", head=["Errors in a 7-bit word", "Cases tried (all of them)", "What happens"], num=[1],
                 rows=[["one", f"{e['s7']}", "corrected every time"], ["two", f"{e['d7']}", "mis-corrected every time: the checks point at a third position"],
                       ["one, with an eighth parity bit", f"{e['s8']}", "corrected every time"], ["two, with an eighth parity bit", f"{e['d8']}", "detected every time"]]),
            dict(type="callout", kind="key", label="Key idea",
                 text="Spread the code words apart: if every two differ in at least three places, a single error cannot carry one into the territory of another, and the nearest code word is the one that was sent. Hamming's checks make finding that nearest word a matter of adding up the failed checks."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Cheaper codes, and a noisy channel", toc="Measured", blocks=[
            dict(type="table", head=["Code (positions, message bits)", "Check bits", "Share of bits carrying the message"], num=[1, 2],
                 rows=[[f"({n},{k})", r, f"{pct}%"] for n, k, r, pct in f]),
            dict(type="p", text=f"Each of these longer codes corrected one random error in each of 20,000 random words. Over a channel that flips each bit with probability {ch['p']}, the program sent {ch['n']} four-bit messages three ways:"),
            dict(type="table", head=["Method", "Bits sent per message", "Messages wrong", "Share wrong"], num=[1, 2, 3],
                 rows=[["no code", "4", ch["plain"], f"{ch['plainp']}% (expected {ch['plainx']}%)"],
                       ["Hamming (7,4)", "7", ch["ham"], f"{ch['hamp']}% (about {ch['hamx']}%)"],
                       ["each bit three times", "12", ch["tri"], f"{ch['trip']}%"]], hl=1),
            dict(type="p", text=f"Hamming's code cuts the failures about {round(int(ch['plain'].replace(',', '')) / int(ch['ham'].replace(',', '')))}-fold for less than double the bits; repeating every bit three times does a little better at three times the cost. Shannon's theorem (topic 12) says much better codes exist, and finding them took the rest of the century."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Weekends at Bell Labs", toc="The evidence", blocks=[
            dict(type="p", text="Hamming ran the IBM computing machines at Los Alamos from 1945 and joined Bell Labs in 1946; in 1947 a weekend job ruined by an early error led him to ask why a machine that can detect an error cannot locate and correct it (MacTutor). The Bell Model V was \"an electromechanical, relay-based computer\"; at weekends it moved on to the next job when it found an error, and in a taped interview Hamming said: \"Damn it, if the machine can detect an error, why can't it locate the position of the error and correct it?\" (Wikipedia)."),
            dict(type="p", text="The paper, \"Error Detecting and Error Correcting Codes\", appeared in the *Bell System Technical Journal* 29(2), April 1950: \"a large number of operations must be performed without a single error in the end result\"; \"The choice of the positions 1, 2, 4, 8, ... for check positions\"; distance at least three for single-error correction, four for \"single error correction plus double error detection\". The paper calls its distance a \"metric\"; the name Hamming distance came later. Hamming received the Turing Award in 1968 (MacTutor)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Errors fixed without anyone noticing", toc="Full circle", blocks=[
            dict(type="p", text="Error-correcting memory in servers still uses Hamming's arrangement with the extra parity bit: correct one error, detect two. Discs, QR codes, mobile networks and links to spacecraft use stronger codes built on the same idea of spreading code words apart. This era began by asking what can be computed at all; it ends with computing that can be trusted."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Seven bits, sixteen code words, every one of the {e['s7']} possible single errors repaired by adding up the failed checks. Hamming's weekend jobs would have run to the end."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Which checks cover position 6?", "6 = 110 in binary: checks 2 and 4."),
            ("Checks 1 and 4 fail and check 2 passes. Which bit is wrong?", "1 + 4 = 5: position 5."),
            ("Why can the (7,4) code not correct two errors?", "Two errors can carry a code word to within one place of a different code word, and the decoder picks that one."),
            ("How many check bits does a code with 15 positions need?", "Four, at positions 1, 2, 4 and 8: 15 = 1111 in binary needs four digits. That leaves 11 positions for the message."),
            ("Why does an eighth bit for the whole word's parity detect double errors?", "Two errors leave the overall parity unchanged while the other checks fail; one error changes the overall parity. So the two cases can be told apart."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Error Detecting and Error Correcting Codes (1950)", text="Hamming's paper in the Bell System Technical Journal, April 1950.",
                 draw=C.draw_manuscript, link="https://archive.org/details/bstj29-2-147", link_text="Internet Archive", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "HammingCodes", d["checks"],
                           f"the 16 code words and their distances, the perfect packing of all 128 words, every single and double error with and without the eighth bit, the longer codes on random words, and {ch['n']} messages over a noisy channel.",
                           ["static long encode(", "static int syndrome("]),
    ]
    return dict(
        title="Hamming's Codes", date="1950",
        description="Era 4, topic 13 of The Algorithm Evolution Atlas: Hamming's error-correcting codes, with check bits at positions 1, 2, 4 whose failures spell the position of an error.",
        lede="A relay computer that found an error simply gave up. Hamming arranged a few parity checks so that the ones that fail spell, in binary, the position of the wrong bit, and the machine can put it right.",
        fieldnote=f"Three check bits guard four bits of message. Flip any one of the seven, and the checks that fail add up to its position: 2 and 4 point at 6. I tried all {e['s7']} single errors; every one was repaired. The machines of this planet have been correcting themselves quietly ever since.",
        card=[("When", "1947 idea; paper April 1950"),
              ("Where", "Bell Telephone Laboratories"),
              ("What hurt", "A detected error meant starting again"),
              ("The fix", "Checks at 1, 2, 4 whose failures spell the position"),
              ("Cost", "3 check bits for 4 of message; 6 for 57")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `HammingCodes.java`.",
    )
