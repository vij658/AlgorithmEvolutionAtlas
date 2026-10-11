"""Era 3, topic 6: binary arithmetic. Every number is parsed from BinaryArithmetic.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"harriot: 1101101 = (.+?) = (\d+) ; back again by halving 109: (.+?) ; reading", ln):
            d["h"] = dict(places=m.group(1), value=m.group(2), halve=m.group(3).split(", "))
        elif m := re.match(r"convert: every number below 2\^20 = ([\d,]+)", ln):
            d["conv"] = m.group(1)
        elif m := re.match(r"tables: base 10 has (\d+) single-digit sums and (\d+) products \((\d+) each, .*?\), of which (\d+) products have no factor 0 or 1 ; base 2 has (\d+) of each \((\d+) counted once\)", ln):
            d["tab"] = dict(dec=m.group(1), decsym=m.group(3), hard=m.group(4), bin=m.group(5), binsym=m.group(6))
        elif m := re.match(r"random: ([\d,]+) pairs .*? on average ([\d.]+) additions for multipliers of ([\d.]+) bits$", ln):
            d["rnd"] = dict(n=m.group(1), adds=m.group(2), bits=m.group(3))
        elif m := re.match(r"egypt: (\d+) x (\d+) by doubling: (.+?) ; ticked rows (.+?) = (\d+) ; the ticks, read from the bottom, are (\d+),", ln):
            d["eg"] = dict(a=m.group(1), b=m.group(2), rows=re.findall(r"(\d+): (\d+)( \(ticked\))?", m.group(3)), sum=m.group(4), prod=m.group(5), bits=m.group(6))
        elif m := re.match(r"length: the numbers 1 to ([\d,]+) take ([\d,]+) decimal digits and ([\d,]+) binary digits, ([\d.]+) times as many ; log2\(10\) = (\S+)$", ln):
            d["len"] = dict(n=m.group(1), dec=m.group(2), bin=m.group(3), ratio=m.group(4), log=m.group(5))
        elif m := re.match(r"circle: Integer.toBinaryString\(109\) = (\d+) ; -109 in an 8-bit byte is (\d+) = 256 - 109 = (\d+), the ones' complement (\d+) plus 1 ; there are 2\^6 = (\d+)", ln):
            d["circ"] = dict(java=m.group(1), neg=m.group(2), val=m.group(3), ones=m.group(4), hex=m.group(5))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def places_diagram(d):
    """Harriot's 1101101 = 109: one box per place."""
    D = Diagram(1000, 220, "Harriot's 1101101: each place is worth twice the place to its right")
    bits = "1101101"
    W, H = 118, 92
    for i, b in enumerate(bits):
        val = 2 ** (6 - i)
        D.node(f"b{i}", 20 + i * 136, 50, W, H, [(b, "title"), (f"× {val}", "note"), (f"= {val if b == '1' else 0}", "combo")],
               color="red" if b == "1" else "ink")
    D.text(20, 30, "PLACE VALUES 64, 32, 16, 8, 4, 2, 1", "tag")
    D.text(20, 190, f"64 + 32 + 8 + 4 + 1 = {d['h']['value']}. Harriot's conversion of 109 survives in his unpublished papers (MacTutor, after Shirley 1951).", "caption")
    return D


def egypt_diagram(d):
    eg = d["eg"]
    D = Diagram(1000, 240, "Egyptian doubling is binary multiplication: the ticked rows are the 1s of the multiplier")
    W, H = 200, 92
    for i, (p, v, t) in enumerate(eg["rows"]):
        D.node(f"r{i}", 20 + i * 240, 50, W, H, [(f"{p} × {eg['b']}", "title"), (f"= {v}", "combo"), ("ticked: a 1" if t else "not ticked: a 0", "note")],
               color="red" if t else "ink")
        if i:
            D.edge(f"r{i - 1}", f"r{i}", ports=("right", "left"), label="double")
    D.text(20, 30, f"{eg['a']} × {eg['b']} AS THE SCRIBES DID IT (ERA 1, TOPIC 5)", "tag")
    D.text(20, 200, f"Ticked: {eg['sum']} = {eg['prod']}. Read from the last row to the first, the ticks spell {eg['bits']}, which is {eg['a']} in binary.", "caption")
    return D


BN_HTML = """
<div class="board bn-board">
  <div style="min-width:0">
    <div class="eyebrow">Two 8-bit numbers: click a bit to flip it</div>
    <div class="bn-row"><span class="bn-lab">a</span><div class="bn-bits" id="bn-a"></div><span class="bn-dec" id="bn-ad"></span></div>
    <div class="bn-row"><span class="bn-lab">b</span><div class="bn-bits" id="bn-b"></div><span class="bn-dec" id="bn-bd"></span></div>
    <div class="bn-places" aria-hidden="true"><span></span><span>128</span><span>64</span><span>32</span><span>16</span><span>8</span><span>4</span><span>2</span><span>1</span></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">a + b, with the carries</div>
    <pre class="bn-work" id="bn-sum"></pre>
    <div class="eyebrow">a × b by shift and add</div>
    <pre class="bn-work" id="bn-mul"></pre>
    <p class="say" id="bn-say" aria-live="polite"></p>
  </div>
</div>
"""

BN_CSS = """
.bn-row{display:flex;align-items:center;gap:8px;margin:6px 0}
.bn-lab{font-family:var(--mono);width:1.2em}
.bn-bits{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:4px;flex:1;max-width:340px}
.bn-bits button{font-family:var(--mono);font-size:16px;padding:6px 0;border:1px solid var(--axis);background:var(--surface);color:var(--ink);border-radius:2px;cursor:pointer}
.bn-bits button.on{background:var(--red);color:var(--on-red);border-color:var(--red)}
.bn-dec{font-family:var(--mono);font-size:14px;min-width:3em}
.bn-places{display:grid;grid-template-columns:1.2em repeat(8,minmax(0,1fr));gap:4px;max-width:360px;font-family:var(--mono);font-size:10.5px;color:var(--muted);text-align:center}
.bn-work{font-family:var(--mono);font-size:13px;line-height:1.45;background:var(--wash);padding:8px 10px;overflow-x:auto;margin:6px 0 10px}
.bn-board .say{font-size:14.5px}
"""

BN_JS = r"""
(() => {
  const A = document.getElementById("bn-a");
  if (!A) return;
  const st = { a: 109, b: 13 };
  function bits(id, key) {
    const host = document.getElementById(id); host.innerHTML = "";
    for (let i = 7; i >= 0; i--) {
      const on = (st[key] >> i) & 1;
      const btn = el("button", { type: "button", class: on ? "on" : "", "aria-label": `bit worth ${2 ** i}` }, host, String(on));
      btn.addEventListener("click", () => { st[key] ^= 1 << i; show(); });
    }
    document.getElementById(id + "d").textContent = "= " + st[key];
  }
  const b2 = (v, w) => v.toString(2).padStart(w, "0");
  function show() {
    bits("bn-a", "a"); bits("bn-b", "b");
    const { a, b } = st, s = a + b;
    const into = new Array(9).fill(" ");
    let carry = 0;
    for (let i = 0; i < 8; i++) { const t = ((a >> i) & 1) + ((b >> i) & 1) + carry; carry = t >> 1; if (carry) into[i + 1] = "1"; }
    const cs = into.slice().reverse().join("");
    document.getElementById("bn-sum").textContent = `carries ${cs}\n  a     ${b2(a, 9)}  (${a})\n+ b     ${b2(b, 9)}  (${b})\n=       ${b2(s, 9)}  (${s})`;
    const lines = []; let acc = 0, adds = 0;
    for (let i = 0; i < 8; i++) if ((b >> i) & 1) { lines.push(`  ${b2(a << i, 16)}  a shifted ${i}`); acc += a << i; adds++; }
    lines.push(`= ${b2(acc, 16)}  (${acc})`);
    document.getElementById("bn-mul").textContent = lines.join("\n");
    document.getElementById("bn-say").textContent = `b has ${adds} one${adds === 1 ? "" : "s"}, so the product needs ${adds} shifted cop${adds === 1 ? "y" : "ies"} of a, and no multiplication table at all. With a = 109, a shows Harriot's 1101101.`;
  }
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How binary arithmetic combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "egy": (20, 20, "Doubling", "multiply by halving and doubling", "Egypt, Era 1 topic 5", "ink"),
        "plc": (395, 20, "Place value", "a digit's worth set by its place", "Babylon, Era 1 topic 3; zero, Era 2 topic 4", "ink"),
        "fux": (770, 20, "Fuxi's figures", "64 hexagrams, sent by Bouvet", "China; letter of 1701", "ink"),
        "bin": (395, 170, "Binary arithmetic", "⊕ two digits: every rule is 1 + 1 = 10", "Harriot c. 1604; Leibniz 1703", "red"),
        "boo": (20, 330, "Boole's algebra", "logic with 0 and 1", "topic 12", "ink"),
        "hol": (395, 330, "Holes in cards", "a hole or no hole", "Hollerith, topic 13", "ink"),
        "cmp": (770, 330, "Complements", "negative numbers as complements", "topic 3", "ink"),
        "cpu": (395, 480, "Every computer", "all data in bits", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("egy", "bin", ports=("bottom", "top:0.15"))
    D.edge("plc", "bin", ports=("bottom", "top"))
    D.edge("fux", "bin", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("bin", "boo", ports=("bottom:0.1", "top:0.7"))
    D.edge("bin", "hol", ports=("bottom", "top"), dashed=True)
    D.edge("cmp", "cpu", ports=("bottom", "top:0.85"))
    D.edge("bin", "cpu", ports=("bottom:0.3", "top:0.3"))
    D.text(20, 615, "Dashed: Fuxi's figures confirmed Leibniz's system to him after he had it; Hollerith's holes are two-valued but counted in decimal.", "caption")
    return D


def chain(d):
    t, ln = d["tab"], d["len"]
    steps = [
        (f"Base-ten arithmetic needs {t['dec']} sums and {t['dec']} products learned by heart",
         "Two digits: every product has a factor 0 or 1, and 1 + 1 = 10 is the only carry", "Harriot c. 1604; Leibniz 1703"),
        (f"The numerals get long: {ln['ratio']} times as many digits",
         "Leave daily counting in tens; use binary where its simplicity pays", "Leibniz: \"I am not in any way recommending\""),
        ("Where does the simplicity pay?",
         "In machines and in logic, where a part is either on or off", "Boole, topic 12; Shannon, 1937"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from memorised tables to switches")
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
    h, t, r, eg, ln, ci = d["h"], d["tab"], d["rnd"], d["eg"], d["len"], d["circ"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Egyptian scribes multiplied by doubling (Era 1, topic 5), which secretly writes every number as a sum of powers of two; place value (Era 1, topic 3, with zero from Era 2, topic 4) lets a digit's position carry its worth. Put the two together and a number needs only two digits. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: binary arithmetic. Blue: where it lives today."),
        ]),
        dict(id="bits", eyebrow="Try it", title="Flip the bits", toc="Try it", blocks=[
            dict(type="p", text="Click any bit to flip it between 0 and 1. The right side adds the two numbers with the carries written above, and multiplies them the way Leibniz recommended: one shifted copy of a for each 1 in b. The starting value of a is Harriot's 1101101 = 109."),
            dict(type="widget", html=BN_HTML, js=BN_JS, css=BN_CSS,
                 fallback=dict(type="diagram", name="places", diagram=places_diagram(d)),
                 note="In the interactive edition you can set two 8-bit numbers bit by bit and watch the sum and the shift-and-add product."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Two digits, one rule", toc="How it works", blocks=[
            dict(type="p", text=f"**Reading and writing.** Each place is worth twice the place to its right. Harriot's 1101101 is {h['places']} = **{h['value']}**. To go back, halve and keep the remainders: {', '.join(h['halve'])}; the remainders read upward are 1101101. The program converted every number below 2²⁰ ({d['conv']} of them) both ways."),
            dict(type="diagram", name="places-steps", diagram=places_diagram(d)),
            dict(type="p", text=f"**Nothing to memorise.** Base ten has {t['dec']} single-digit sums and {t['dec']} products ({t['decsym']} of each if a + b and b + a count once), and {t['hard']} of the products have no factor 0 or 1, so they must be learned. Base two has {t['bin']} of each ({t['binsym']} counted once), and every product has a factor 0 or 1. Leibniz: in binary \"there would no longer be any need to learn anything by heart\"."),
            dict(type="p", text=f"**Multiplying is doubling.** Each digit of the multiplier says: add a shifted copy of the number, or don't. That is exactly the scribes' table of doublings:"),
            dict(type="diagram", name="egypt", diagram=egypt_diagram(d)),
            dict(type="p", text=f"The program added and multiplied {r['n']} random pairs bit by bit, with no multiplication table: all correct. Multipliers of about {r['bits']} bits needed on average {r['adds']} shifted additions, one per 1."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Choose the representation that makes the algorithm simplest. In base two, every arithmetic rule collapses to \"1 + 1 = 10\" and \"add it or don't\": rules a machine can follow without understanding numbers at all."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The price is length", toc="Measured", blocks=[
            dict(type="table", head=["Numbers 1 to " + ln["n"], "Digits used"], num=[1], rows=[["In decimal", ln["dec"]], ["In binary", ln["bin"]]]),
            dict(type="p", text=f"Binary needed {ln['ratio']} times as many digits; for very large numbers the ratio approaches log₂ 10 = {ln['log']}. Leibniz saw this and wrote, \"I am not in any way recommending this way of counting\" for everyday use: counting by ten is shorter."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Invented in a drawer, published from Paris", toc="The evidence", blocks=[
            dict(type="p", text="Thomas Harriot converted numbers to binary (1101101 = 109) and added, subtracted and multiplied in it, in papers left unpublished at his death; \"He saw no practical applications for his theory in his day, and he dropped it\" (MacTutor, after Shirley 1951). Strickland dates the work between September 1601 and November 1605 and treats the often-quoted 1604 as Knuth's conjecture (**documented** range)."),
            dict(type="p", text="Juan Caramuel's *Mathesis biceps* of 1670 \"probably contains ... the first known publication in Europe on the binary system\" (Ineichen, quoted by Bruderer; Wikipedia gives 1700: **disputed**). Leibniz's first binary paper dates from 1679; his *Explication de l'Arithmétique Binaire* appeared for 1703, after Joachim Bouvet wrote from China in 1701 of Fuxi's \"grand figure, which goes up to 64\". Reading the hexagrams as an independent invention of binary is Bouvet's and Leibniz's interpretation (**conjecture**)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Harriot's numeral, printed by Java", toc="Full circle", blocks=[
            dict(type="p", text=f"Ask Java for the binary form of 109 and it prints {ci['java']}, the numeral in Harriot's papers. Negative numbers reuse the complement trick of Pascal's machine (topic 3): in an 8-bit byte, −109 is stored as {ci['neg']} = 256 − 109 = {ci['val']}, which is the ones' complement {ci['ones']} plus 1."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Leibniz did not recommend binary for counting, and he was right: people still count in tens. But a switch, a relay, a transistor or a hole in a card has two states, and for machines binary's one rule is worth any length. There are 2⁶ = {ci['hex']} six-digit binary numbers, as many as the hexagrams Bouvet sent; a computer's 64-bit word has 2⁶⁴."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("What is 1101101 in decimal?", f"64 + 32 + 8 + 4 + 1 = {h['value']}."),
            ("How do you write 13 in binary?", "Halve and keep remainders: 13 r 1, 6 r 0, 3 r 1, 1 r 1; read upward: 1101."),
            ("Why does binary multiplication need no table?", "Each multiplier digit is 0 or 1: the partial product is either nothing or a shifted copy of the number."),
            ("Why did Leibniz not recommend binary for everyday use?", "Its numerals are about three and a third times as long; counting by ten is shorter."),
            ("Where are the Egyptian scribe's ticks in binary?", f"They are the 1s of the multiplier: for {eg['a']} the ticked rows are 1, 4 and 8, and {eg['a']} is {eg['bits']} in binary."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Explanation of binary arithmetic (1703)", text="Leibniz's own case for binary, in English, with Bouvet's report of Fuxi's figures.",
                 draw=C.draw_manuscript, link="https://kastalia.medienhaus.udk-berlin.de/odl/Leibniz.pdf", link_text="PDF",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "BinaryArithmetic", d["checks"],
                           "conversion of every number below 2²⁰ both ways against Java's own, 100,000 sums and shift-and-add products bit by bit, Egyptian doubling as binary, the length of a million numerals, and two's complement.",
                           ["static String add(", "static String multiply("]),
    ]
    return dict(
        title="Binary Arithmetic", date="1703",
        description="Era 3, topic 6 of The Algorithm Evolution Atlas: Harriot's unpublished binary, Leibniz's 1703 Explication, arithmetic with two digits and no tables, and why machines use it.",
        lede="Write every number with two digits. The numerals grow long, but every rule of arithmetic collapses to one: one and one make ten. Leibniz published it in 1703 and said plainly that he did not recommend it for ordinary use.",
        fieldnote="An Englishman worked it out around 1604 and left it in a drawer; a German philosopher made it public a century later and admired its simplicity without finding a use. The use came with machines, which care nothing for the length of a numeral and everything for the simplicity of its rules.",
        card=[("When", "Harriot c. 1601–1605 (unpublished); Caramuel 1670; Leibniz 1679, 1703"),
              ("Where", "England, Paris, Hanover"),
              ("What hurt", "Base-ten arithmetic needs memorised tables"),
              ("The fix", "Two digits; every operation reduces to 1 + 1 = 10"),
              ("Cost", f"{ln['ratio']} times as many digits")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BinaryArithmetic.java`.",
    )
