"""Era 1, topic 2: grouping, written numerals and the first carry. Every number is parsed from GroupingAndCarry.java's output."""
import json
import re

import common as C
import diagrams
import page
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"ladder": {}, "signs": [], "work": {}, "pattern": {}}
    for ln in text.splitlines():
        if m := re.match(r"ladder ([\w-]+): rates=([\d ]+) values=([\d ]+)$", ln):
            d["ladder"][m.group(1)] = dict(rates=[int(x) for x in m.group(2).split()], values=[int(x) for x in m.group(3).split()])
        elif m := re.match(r"signs (\d+): tally=(\d+) egyptian=(\d+) sumerian-S=(\d+) egyptian-signs=([\d ]+) sumerian-S-signs=([\d ]+)$", ln):
            d["signs"].append(dict(n=int(m.group(1)), tally=int(m.group(2)), egy=int(m.group(3)), sum=int(m.group(4)),
                                   egy_c=[int(x) for x in m.group(5).split()], sum_c=[int(x) for x in m.group(6).split()]))
        elif m := re.match(r"average 1-9999: tally=([\d.]+) egyptian=([\d.]+) sumerian-S=([\d.]+)$", ln):
            d["avg"] = dict(tally=float(m.group(1)), egy=float(m.group(2)), sum=float(m.group(3)))
        elif m := re.match(r"most 1-9999: egyptian=(\d+) at (\d+) sumerian-S=(\d+) at (\d+)$", ln):
            d["most"] = dict(egy=int(m.group(1)), egy_at=int(m.group(2)), sum=int(m.group(3)), sum_at=int(m.group(4)))
        elif m := re.match(r"work ([\w-]+) (\d+) (\d+): (pool|exchange \d+)=([\d ]+)$", ln):
            w = d["work"].setdefault(m.group(1), dict(a=int(m.group(2)), b=int(m.group(3)), states=[]))
            w["states"].append([int(x) for x in m.group(5).split()])
        elif m := re.match(r"work ([\w-]+) \d+ \d+: result=(\d+) exchanges=(\d+)$", ln):
            d["work"][m.group(1)].update(result=int(m.group(2)), exchanges=int(m.group(3)))
        elif m := re.match(r"cascade egyptian 9999 1: exchanges=(\d+) result=(\d+)$", ln):
            d["cascade"] = int(m.group(1))
        elif m := re.match(r"addcheck: (\d+) random pairs", ln):
            d["addcheck"] = int(m.group(1))
        elif m := re.match(r"exchanges egyptian: ([\d.]+) per addition", ln):
            d["avg_exchanges"] = float(m.group(1))
        elif m := re.match(r"carry-share base 10: ([\d.]+) of columns over (\d+) additions of two (\d+)-digit numbers; first column ([\d.]+)", ln):
            d["share"] = dict(all=float(m.group(1)), trials=int(m.group(2)), digits=int(m.group(3)), first=float(m.group(4)))
        elif m := re.match(r"carry-share base 10 columns 21-40: ([\d.]+)", ln):
            d["share"]["late"] = float(m.group(1))
        elif m := re.match(r"transitions base 10: .*?(\d+) of 100 digit pairs pass one on; with a carry coming in, (\d+) of 100", ln):
            d["t01"], d["t11"] = int(m.group(1)), int(m.group(2))
        elif m := re.match(r"longest-carry base 2: (\d+) bits, average longest carry chain ([\d.]+) over (\d+) random pairs; log2\(\d+\) = ([\d.]+)", ln):
            d["chain"] = dict(bits=int(m.group(1)), avg=float(m.group(2)), trials=int(m.group(3)), log2=float(m.group(4)))
        elif m := re.match(r"longest-carry spread: most common (\d+), longest seen (\d+), worst possible (\d+)", ln):
            d["chain"].update(mode=int(m.group(1)), max=int(m.group(2)), worst=int(m.group(3)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
# simplified drawings of the signs, as SVG symbols coloured by currentColor
# ----------------------------------------------------------------------------------------------------------------------
SW = 'fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"'
SYMBOLS = {
    # Egyptian hieroglyphic signs for 1, 10, 100, 1,000 and 10,000 (simplified)
    "e0": f'<line x1="10" y1="3" x2="10" y2="21" {SW} stroke-width="3"/>',
    "e1": f'<path d="M4,21 V11 A6,6 0 0 1 16,11 V21" {SW}/>',
    "e2": f'<path d="M10,12 a1.6,1.6 0 1 1 3.2,0 a3.6,3.6 0 1 1 -7.2,0 a5.6,5.6 0 1 1 11.2,0 a7.4,7.4 0 0 1 -6,7.3 V22" {SW}/>',
    "e3": f'<path d="M10,22 V9 M10,15 C6,15 5,12 6,10 M10,9 C7,8 6,5 7,2 C8.5,4 9.5,5 10,6.5 C10.5,5 11.5,4 13,2 C14,5 13,8 10,9" {SW}/>',
    "e4": f'<path d="M9,22 V7 a2.6,2.6 0 0 1 5.2,0 V12 l-2.5,2" {SW}/>',
    # Sumerian signs for counted objects: 1, 10, 60, 600, 3,600, 36,000 (simplified impressions)
    "s0": '<path d="M10,3 L13,20 Q10,23 7,20 Z" fill="currentColor"/>',
    "s1": '<circle cx="10" cy="12" r="5.5" fill="currentColor"/>',
    "s2": '<path d="M10,1 L16,21 Q10,25 4,21 Z" fill="currentColor"/>',
    "s3": '<path d="M10,1 L16,21 Q10,25 4,21 Z" fill="currentColor"/><circle cx="10" cy="15" r="3.2" fill="var(--surface, #fff)"/>',
    "s4": '<circle cx="10" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="3.2"/>',
    "s5": '<circle cx="10" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="3.2"/><circle cx="10" cy="12" r="3.4" fill="currentColor"/>',
}


def defs(standalone, theme=None):
    body = "".join(f'<symbol id="g-{k}" viewBox="0 0 20 24">{v}</symbol>' for k, v in SYMBOLS.items())
    if standalone and theme:                                          # files have no CSS variables: write the colour out
        body = body.replace("var(--surface, #fff)", theme["surface"])
    return f"<defs>{body}</defs>"


def use(sym, x, y, color, size=1.0):
    return f'<use href="#g-{sym}" x="{x:.1f}" y="{y:.1f}" width="{20 * size:.1f}" height="{24 * size:.1f}" style="color:{color}"/>'


def piles_svg(bands, prefix, values, label, highlight=None):
    """Bands of sign piles: bands = [(title, counts)], counts smallest sign first; drawn with the largest sign on the left."""
    ncols = 5
    colw, cell, rowh, perrow = 128, 22, 26, 5

    def draw(t, standalone):
        out = [defs(standalone, t)]
        y = 14
        for j in range(ncols):
            i = ncols - 1 - j
            x = 96 + j * colw
            out.append(use(f"{prefix}{i}", x, y, t["ink"], 0.9))
            out.append(C.text(x + 24, y + 16, f"{values[i]:,}", t["muted"], 12))
        y += 36
        for title, counts in bands:
            rows = max(1, max((c + perrow - 1) // perrow for c in counts[:ncols]))
            h = rows * rowh + 14
            out.append(C.line(20, y, 96 + ncols * colw - 20, y, t["rule"], 1))
            for k, part in enumerate(diagrams.wrap(title, 12, 600, 70)):
                out.append(C.text(20, y + 20 + k * 15, part, t["ink2"], 12, weight=600))
            for j in range(ncols):
                i = ncols - 1 - j
                n = counts[i] if i < len(counts) else 0
                for k in range(n):
                    gx = 96 + j * colw + (k % perrow) * cell
                    gy = y + 8 + (k // perrow) * rowh
                    hot = highlight and highlight[0] == title and highlight[1] == i
                    out.append(use(f"{prefix}{i}", gx, gy, t["red"] if hot else t["ink"], 0.9))
            y += h
        return C.svg_doc(96 + ncols * colw, y + 6, "".join(out), label, t, standalone, 0.66)
    return draw


PE_HTML = """
<div class="board pe-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="pe-sys">Signs <select id="pe-sys"><option value="egyptian">Egyptian (tens)</option><option value="sumerian">Sumerian (tens and sixes)</option></select></label>
      <label for="pe-a">a <input id="pe-a" type="number" min="0" max="9999" value="AV" inputmode="numeric"></label>
      <label for="pe-b">b <input id="pe-b" type="number" min="0" max="9999" value="BV" inputmode="numeric"></label>
    </div>
    <div class="controls">
      <button id="pe-pool" class="primary" type="button">Pool</button>
      <button id="pe-ex" type="button">Exchange</button>
      <button id="pe-all" type="button">All exchanges</button>
      <button id="pe-reset" type="button">Reset</button>
    </div>
    <div class="scrollx"><svg id="pe-svg" role="img" aria-label="The signs of two numbers, pooled and exchanged"></svg></div>
    <div class="presets" aria-label="Examples">
      <button type="button" data-s="egyptian" data-a="2763" data-b="1489">2,763 + 1,489</button>
      <button type="button" data-s="egyptian" data-a="9999" data-b="1">9,999 + 1</button>
      <button type="button" data-s="sumerian" data-a="47" data-b="38">47 + 38 in Sumerian signs</button>
      <button type="button" data-s="sumerian" data-a="3599" data-b="1">3,599 + 1 in Sumerian signs</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">What happened</div>
    <ol class="steps" id="pe-steps"></ol>
    <div class="result" id="pe-result" aria-live="polite"></div>
  </div>
</div>
"""

PE_CSS = """
.pe-board{grid-template-columns:1fr}
.pe-board .steps{columns:2 18em;column-gap:22px}
.pe-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px}
.pe-board .controls input{width:6.5em}
.pe-board svg{background:none;min-width:560px}
"""

PE_JS = r"""
(() => {
  const svg = document.getElementById("pe-svg");
  if (!svg) return;
  const SYS = SYSTEMS_JSON;
  const DEFS = DEFS_HTML;
  let sys = "egyptian", A = AV, B = BV, pooled = null, ex = 0, justIn = -1, log = [];
  const val = s => { const v = [1]; for (const r of SYS[s].rates) v.push(v[v.length - 1] * r); return v; };
  const toSigns = (s, n) => { const v = val(s), c = v.map(() => 0); for (let i = v.length - 1; i >= 0; i--) { c[i] = Math.floor(n / v[i]); n %= v[i]; } return c; };
  const total = (s, c) => val(s).reduce((t, v, i) => t + v * c[i], 0);
  const W = 128, CELL = 22, ROWH = 26, PER = 5, N = 5;
  function band(y, title, counts, faded, hotCol) {
    const rows = Math.max(1, ...counts.map(c => Math.ceil(c / PER)));
    sv("line", {x1: 20, y1: y, x2: 96 + N * W - 20, y2: y, stroke: "var(--rule)"}, svg);
    sv("text", {x: 20, y: y + 20, fill: "var(--ink-2)", "font-size": 12, "font-weight": 600}, svg, title);
    for (let j = 0; j < N; j++) {
      const i = N - 1 - j;
      for (let k = 0; k < (counts[i] || 0); k++) {
        const u = sv("use", {href: `#g-${SYS[sys].prefix}${i}`, x: 96 + j * W + (k % PER) * CELL, y: y + 8 + Math.floor(k / PER) * ROWH, width: 18, height: 21.6}, svg);
        u.style.color = faded ? "var(--axis)" : (i === justIn && k === counts[i] - 1 ? "var(--yellow)" : (i === hotCol ? "var(--red)" : "var(--ink)"));
      }
    }
    return y + rows * ROWH + 14;
  }
  function draw() {
    svg.innerHTML = DEFS;
    const v = val(sys);
    for (let j = 0; j < N; j++) {
      const i = N - 1 - j, x = 96 + j * W;
      const u = sv("use", {href: `#g-${SYS[sys].prefix}${i}`, x, y: 14, width: 18, height: 21.6}, svg);
      u.style.color = "var(--ink)";
      sv("text", {x: x + 24, y: 30, fill: "var(--muted)", "font-size": 12}, svg, fmt(v[i]));
    }
    let y = 50;
    y = band(y, fmt(A), toSigns(sys, A), pooled !== null, -1);
    y = band(y, fmt(B), toSigns(sys, B), pooled !== null, -1);
    if (pooled) {
      const k = pooled.findIndex((c, i) => i < SYS[sys].rates.length && c >= SYS[sys].rates[i]);
      y = band(y, "Pooled", pooled, false, k);
    }
    svg.setAttribute("viewBox", `0 0 ${96 + N * W} ${y + 6}`);
    const steps = document.getElementById("pe-steps");
    steps.innerHTML = "";
    const items = [pooled ? "Pool the signs of both numbers." : "Press Pool to put the two piles together.", ...log];
    items.forEach((t, i) => el("li", {class: i === items.length - 1 ? "current" : ""}, steps, t));
    const res = document.getElementById("pe-result");
    if (!pooled) { res.textContent = ""; return; }
    const k = pooled.findIndex((c, i) => i < SYS[sys].rates.length && c >= SYS[sys].rates[i]);
    res.innerHTML = k < 0 ? `<b>${fmt(total(sys, pooled))}</b> = ${fmt(A)} + ${fmt(B)}, after ${ex} exchange${ex === 1 ? "" : "s"}. No sign appears too often: the sum is written.`
                          : `${ex} exchange${ex === 1 ? "" : "s"} so far. The red signs are too many: ${SYS[sys].rates[k]} of them make one of the next size. ${justIn >= 0 ? "The yellow sign is the one just carried in." : ""}`;
  }
  function exchange() {
    if (!pooled) return false;
    const k = pooled.findIndex((c, i) => i < SYS[sys].rates.length && c >= SYS[sys].rates[i]);
    if (k < 0) return false;
    const r = SYS[sys].rates[k], v = val(sys);
    pooled[k] -= r; pooled[k + 1] += 1; ex++; justIn = k + 1;
    log.push(`${r} signs of ${fmt(v[k])} out, one sign of ${fmt(v[k + 1])} in.`);
    return true;
  }
  function read() {
    sys = document.getElementById("pe-sys").value;
    A = Math.max(0, Math.min(9999, Math.floor(+document.getElementById("pe-a").value || 0)));
    B = Math.max(0, Math.min(9999, Math.floor(+document.getElementById("pe-b").value || 0)));
    pooled = null; ex = 0; justIn = -1; log = []; draw();
  }
  ["pe-sys", "pe-a", "pe-b"].forEach(id => document.getElementById(id).addEventListener("change", read));
  document.getElementById("pe-pool").addEventListener("click", () => {
    if (pooled) return;
    const a = toSigns(sys, A), b = toSigns(sys, B);
    pooled = a.map((x, i) => x + b[i]); draw();
  });
  document.getElementById("pe-ex").addEventListener("click", () => { if (!pooled) document.getElementById("pe-pool").click(); else { exchange(); draw(); } });
  document.getElementById("pe-all").addEventListener("click", () => { if (!pooled) document.getElementById("pe-pool").click(); while (exchange()); draw(); });
  document.getElementById("pe-reset").addEventListener("click", read);
  document.querySelectorAll(".pe-board .presets button").forEach(b => b.addEventListener("click", () => {
    document.getElementById("pe-sys").value = b.dataset.s;
    document.getElementById("pe-a").value = b.dataset.a;
    document.getElementById("pe-b").value = b.dataset.b;
    read();
  }));
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
# diagrams
# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How grouped numerals combined with other ideas, from tally marks to the carry inside a computer")
    W, H = 210, 76
    nodes = {
        "tok": (30, 20, "Clay tokens", "", "from c. 7500 BCE", "ink"),
        "tal": (395, 20, "Tally marks", "", "topic 1", "ink"),
        "sig": (395, 160, "A sign for each bundle", "⊕ bundles get names", "Egypt and Sumer, c. 3000 BCE", "red"),
        "pex": (180, 300, "Pool and exchange", "⊕ an exchange rate", "the first carry", "red"),
        "pv": (610, 300, "Place value", "⊕ position names the bundle", "topic 3", "ink"),
        "col": (395, 430, "Column addition", "⊕ carry into the next column", "", "ink"),
        "add": (180, 550, "Electronic adder", "⊕ switches", "designed 1946", "blue"),
        "chn": (610, 550, "How far carries run", "⊕ probability", "1946; Holte, 1997", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("tok", "sig", dashed=True)
    D.edge("tal", "sig", ports=("bottom", "top"))
    D.edge("sig", "pex", ports=("bottom", "top"))
    D.edge("sig", "pv", ports=("bottom", "top"))
    D.edge("pex", "col", ports=("bottom", "top"))
    D.edge("pv", "col", ports=("bottom", "top"))
    D.edge("col", "add", ports=("bottom", "top"))
    D.edge("add", "chn", ports=("right", "left"))
    return D


def chain(d):
    s168 = next(s for s in d["signs"] if s["n"] == 168)
    w = d["work"]["egyptian"]
    pool = w["states"][0]
    most = d["most"]
    steps = [
        (f"A tally of {s168['n']} needs {s168['tally']} marks", f"A new sign for each bundle: {s168['n']} takes {s168['egy']} Egyptian signs", "Egypt and Sumer, c. 3000 BCE"),
        (f"Pooled signs pile up: {w['a']:,} + {w['b']:,} gives {pool[0]} ones, {pool[1]} tens, {pool[2]} hundreds",
         "Exchange ten of a sign for one of the next: the carry", ""),
        ("Each kind of goods had its own ladder: one sign could mean 6, 10 or 18 units", "One abstract system for everything", "topic 3"),
        (f"Every power needs its own sign, and {most['egy_at']:,} takes {most['egy']} signs", "Let the position say which bundle: place value", "topic 3"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from long tallies to place value")
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


def ladders(d):
    rows = [("egyptian", "Egyptian signs", "ink"), ("sumerian-S", "Sumerian, counted objects", "red"), ("sumerian-B", "Sumerian, rations", "blue")]
    bw, gap, rowh = 96, 46, 120
    D = Diagram(30 + 7 * (bw + gap), 30 + len(rows) * rowh, "Three ladders of exchange rates: Egyptian tens, and two Sumerian ladders of tens and sixes")
    for r, (key, title, color) in enumerate(rows):
        lad = d["ladder"][key]
        y = 40 + r * rowh
        D.text(20, y - 12, title.upper(), "tag")
        for i, v in enumerate(lad["values"]):
            D.node(f"{key}{i}", 20 + i * (bw + gap), y, bw, 52, [(f"{v:,}", "title")], color=color)
            if i:
                D.edge(f"{key}{i - 1}", f"{key}{i}", ports=("right", "left"), label=f"×{lad['rates'][i - 1]}", dy=-6)
    return D


def cascade(d):
    names = ["ones", "tens", "hundreds", "thousands", "ten-thousands"]
    D = Diagram(980, 170, "9,999 + 1: one carry ripples through four exchanges")
    for i in range(d["cascade"] + 1):
        x = 20 + i * 192
        if i < d["cascade"]:
            D.node(i, x, 40, 150, 76, [(f"10 {names[i]}", "title"), (f"become 1 of the {names[i + 1]}", "note")], color="red" if i == 0 else "ink")
        else:
            D.node(i, x, 40, 150, 76, [("10,000", "big"), ("one sign", "note")], color="blue")
        if i:
            D.edge(i - 1, i, ports=("right", "left"))
    D.text(20, 22, "9,999 + 1, POOLED: TEN ONES", "tag")
    D.text(20, 150, "Each exchange makes the next one necessary. This is the carry that a computer's adder must pass along too.", "caption")
    return D


def markov(d):
    t01, t11 = d["t01"], d["t11"]
    D = Diagram(900, 280, "Carries as a two-state chain: with or without a carry coming in")
    D.node("no", 60, 90, 260, 100, [("NO CARRY COMING IN", "tag"), (f"{t01} of 100 digit pairs pass one on", "combo"), (f"{100 - t01} of 100 do not", "note")], color="ink")
    D.node("yes", 580, 90, 260, 100, [("A CARRY COMING IN", "tag"), (f"{t11} of 100 digit pairs pass one on", "combo"), (f"{100 - t11} of 100 do not", "note")], color="red")
    D.edge("no", "yes", ports=("right:0.3", "left:0.3"), label=f"a carry: {t01} in 100", at=0.5, dy=-8)
    D.edge("yes", "no", ports=("left:0.7", "right:0.7"), label=f"no carry: {100 - t11} in 100", at=0.5, dy=20)
    D.text(450, 40, "THE NEXT COLUMN DEPENDS ONLY ON THIS ONE", "tag", "middle")
    D.text(450, 250, f"Leaving each state is equally likely ({t01} in 100), so in the long run half of all columns carry.", "caption", "middle")
    return D


def debate():
    D = Diagram(1000, 330, "Where did written numbers come from? Two accounts")
    D.text(20, 30, "SCHMANDT-BESSERAT: ONE LINE OF DESCENT", "tag")
    steps = ["Plain clay tokens", "Tokens sealed in clay envelopes", "Token shapes pressed into tablets", "Number signs, then writing"]
    for i, s in enumerate(steps):
        D.node(f"a{i}", 20 + i * 245, 44, 210, 64, [(s, "combo")], color="ink")
        if i:
            D.edge(f"a{i - 1}", f"a{i}", ports=("right", "left"))
    D.text(20, 178, "VALERIO AND FERRARA (2022): TWO DEVELOPMENTS THAT CONVERGE", "tag")
    D.node("n", 20, 196, 300, 56, [("Number signs", "combo")], color="blue")
    D.node("w", 20, 264, 300, 56, [("Proto-cuneiform word signs", "combo")], color="blue")
    D.node("c", 600, 223, 340, 70, [("Accounts that use both", "combo"), ("Uruk, c. 3200–3000 BCE", "note")], color="red")
    D.edge("n", "c", ports=("right", "left"))
    D.edge("w", "c", ports=("right", "left"))
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    egy, sumS = d["ladder"]["egyptian"], d["ladder"]["sumerian-S"]
    w, ws = d["work"]["egyptian"], d["work"]["sumerian-S"]
    s168 = next(s for s in d["signs"] if s["n"] == 168)
    s1999 = next(s for s in d["signs"] if s["n"] == 1999)
    sh, ch = d["share"], d["chain"]
    systems = {"egyptian": dict(rates=egy["rates"][:4], prefix="e"), "sumerian": dict(rates=sumS["rates"][:4], prefix="s")}
    pe_js = (PE_JS.replace("SYSTEMS_JSON", json.dumps(systems)).replace("DEFS_HTML", json.dumps(defs(False)))
             .replace("AV", str(w["a"])).replace("BV", str(w["b"])))
    pe_html = PE_HTML.replace("AV", str(w["a"])).replace("BV", str(w["b"]))
    cols = ["ones", "tens", "hundreds", "thousands"]
    work_rows = []
    for k, st in enumerate(w["states"]):
        what = "Pool the signs of both numbers" if k == 0 else f"Ten {cols[k - 1]} out, one of the {cols[k]} in"
        work_rows.append([k, *[st[i] for i in (3, 2, 1, 0)], what])
    scols = ["ones (small cones)", "tens (small circles)", "sixties (large cones)"]
    work_rows_s = []
    for k, st in enumerate(ws["states"]):
        what = "Pool the signs" if k == 0 else (f"Ten small cones out, one small circle in" if k == 1 else "Six small circles out, one large cone in")
        work_rows_s.append([k, st[2], st[1], st[0], what])

    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Here the tally (topic 1) gains names for its bundles, and adding gains its first rule: the exchange. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: grouped signs and the carry they made necessary. Blue: where the carry went in the twentieth century. The dashed arrow from tokens is disputed (see below)."),
        ]),
        dict(id="pool", eyebrow="Try it", title="Pool the signs, then exchange", toc="Try it", blocks=[
            dict(type="p", text="Write each number with its signs. To add, put the two piles together, then wherever there are too many of one sign, swap them for one sign of the next size. "
                                "In Egyptian signs the rate is always ten; in the oldest Sumerian accounts it alternates between ten and six."),
            dict(type="widget", html=pe_html, js=pe_js, css=PE_CSS,
                 fallback=dict(type="svg", name="pool", draw=piles_svg([("Pooled", w["states"][0]), (f"After {w['exchanges']} exchanges", w["states"][-1])], "e", egy["values"],
                                                                     f"{w['a']:,} + {w['b']:,} in Egyptian signs, pooled and then exchanged"),
                               alt=f"{w['a']:,} + {w['b']:,} in Egyptian signs, pooled and then exchanged"),
                 note="In the interactive edition you can pool and exchange your own numbers, in Egyptian or Sumerian signs."),
            dict(type="p", text="The signs are simplified drawings made for this book. MacTutor puts the rule in one sentence: \"One just adds the individual symbols, but replacing ten copies of a symbol by a single symbol of the next higher value.\""),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
            dict(type="p", text="Signs for bundles shrink the writing dramatically. The program counts the signs each system needs:"),
            dict(type="table", head=["Number", "Tally marks", "Egyptian signs", "Sumerian signs (counted objects)"], num=[0, 1, 2, 3],
                 hl=[s["n"] for s in d["signs"]].index(168),
                 rows=[[f"{s['n']:,}", f"{s['tally']:,}", s["egy"], s["sum"]] for s in d["signs"]] +
                      [["average, 1 to 9,999", f"{d['avg']['tally']:,.1f}", f"{d['avg']['egy']:.2f}", f"{d['avg']['sum']:.2f}"]]),
            dict(type="p", text=f"The worst number below 10,000 is {d['most']['egy_at']:,} for Egyptian signs ({d['most']['egy']} signs) and {d['most']['sum_at']:,} for the Sumerian ones ({d['most']['sum']}). "
                                "Bigger bundles mean fewer signs, but more kinds of sign to learn."),
        ]),
        dict(id="steps", eyebrow="Step by step", title=f"{w['a']:,} + {w['b']:,}, by exchange", toc="Step by step", blocks=[
            dict(type="table", head=["Step", "Thousands", "Hundreds", "Tens", "Ones", "What happened"], num=[0, 1, 2, 3, 4], hl=0, rows=work_rows),
            dict(type="p", text=f"Result: **{w['result']:,}**, after **{w['exchanges']} exchanges**. The Sumerian ladder works the same way with a different rate at each step. {ws['a']} + {ws['b']} counted objects:"),
            dict(type="table", head=["Step", "Sixties", "Tens", "Ones", "What happened"], num=[0, 1, 2, 3], hl=0, rows=work_rows_s),
            dict(type="p", text=f"Result: **{ws['result']}** = 1 sixty, 2 tens and 5 ones, after {ws['exchanges']} exchanges. Nothing in the method needs ten: only an agreed rate for each step."),
            dict(type="diagram", name="ladders", diagram=ladders(d),
                 caption="The Sumerian ladders follow Duncan Melville's account: the counted-objects system reaches 36,000 units and the rations system 7,200. The same sign could mean different amounts in different systems."),
            dict(type="callout", kind="key", label="Key idea",
                 text="An exchange can trigger the next one. In 9,999 + 1 the ten ones become a ten, which makes ten tens, which makes ten hundreds, and so on. One added stroke forces four exchanges:"),
            dict(type="diagram", name="cascade", diagram=cascade(d)),
        ]),
        dict(id="debate", eyebrow="The evidence", title="Where did written numbers come from?", toc="The evidence", blocks=[
            dict(type="p", text="Denise Schmandt-Besserat's account runs in one line: plain clay tokens (about 7500 to 3500 BCE), then tokens sealed in clay envelopes, then tablets with impressed signs, then abstract numerals. "
                                "Valerio and Ferrara (2022) argue instead that numerals and proto-cuneiform signs were \"two distinct but converging developments\". **Disputed**."),
            dict(type="diagram", name="debate", diagram=debate(), caption="The token account is widely taught; the critique is recent. Both agree that by about 3200–3000 BCE the accounts of Uruk wrote numbers with bundled signs (**documented**)."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How often does a carry happen?", toc="Measured", blocks=[
            dict(type="p", text=f"Add two long random numbers. How many columns pass a carry on? The program added {sh['trials']:,} pairs of {sh['digits']}-digit numbers. "
                                f"In the first column {d['t01']} of the 100 possible digit pairs make a carry, so it carries {sh['first']:.4f} of the time. Further along, a carry coming in makes the next carry more likely:"),
            dict(type="diagram", name="markov", diagram=markov(d)),
            dict(type="table", head=["What was measured", "Share of columns that carry"], num=[1],
                 rows=[["First column (no carry can come in)", f"{sh['first']:.4f}"], [f"All {sh['digits']} columns", f"{sh['all']:.4f}"], ["Columns 21 to 40 of 40-digit numbers", f"**{sh['late']:.4f}**"]]),
            dict(type="p", text="John Holte proved in 1997 that the long-run share is exactly one half, and that the carries form a Markov chain: the chance of the next carry depends only on whether this column carried."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The carry inside the computer", toc="Full circle", blocks=[
            dict(type="p", text=f"In 1946 Arthur Burks, Herman Goldstine and John von Neumann wrote the design of a stored-program computer that worked in binary, with 40-digit numbers. For its adder they worked out how far a carry travels. "
                                f"Their answer: the longest carry chain averages no more than log₂ 40, about 5.3 places, \"an average length of about 5 for the longest carry sequence\"."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program added {ch['trials']:,} pairs of random {ch['bits']}-bit numbers. The longest carry chain averaged **{ch['avg']:.3f}** places (their bound: {ch['log2']:.3f}). "
                      f"The most common longest chain was {ch['mode']}, the longest seen {ch['max']}, against a worst case of {ch['worst']}. Five thousand years after the first exchange of ten strokes for one sign, how far a carry travels had become a question about how fast a computer can add."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many Egyptian signs does 1,999 need? How many tally marks?",
             f"**{s1999['egy']}** signs (1 thousand, 9 hundreds, 9 tens, 9 ones) against **{s1999['tally']:,}** marks. In the Sumerian counted-objects system it takes {s1999['sum']}."),
            (f"Add {w['a']:,} + {w['b']:,} in Egyptian signs. How many exchanges?",
             f"Pooled: {w['states'][0][0]} ones, {w['states'][0][1]} tens, {w['states'][0][2]} hundreds, {w['states'][0][3]} thousands. Exchanging gives **{w['result']:,}** in **{w['exchanges']}** exchanges."),
            ("Why can adding two numbers in Egyptian signs never need two exchanges in the same column?",
             "Each number has at most 9 of a sign, so the pool has at most 9 + 9 = 18, plus 1 carried in: 19. That is less than 20, so one exchange always clears the column."),
            ("In the Sumerian counted-objects system, how many units is the sign after 600 worth?",
             f"**{sumS['values'][4]:,}**: 600 × 6. The ladder is {', '.join(f'{v:,}' for v in sumS['values'])}."),
            ("If half of all columns carry in the long run, why does the first column carry less often?",
             f"Nothing can carry into the first column. Without a carry coming in, only {d['t01']} of the 100 digit pairs reach ten; with one, {d['t11']} do."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Proto-cuneiform tablet, account of barley", text="Jemdet Nasr period, c. 3100–2900 BCE. The round and conical impressions are numbers. Metropolitan Museum of Art, 1988.433.1.",
                 photo="https://images.metmuseum.org/CRDImages/an/web-large/DP293243.jpg", draw=lambda t, s: C.draw_tablet(t, s),
                 link="https://www.metmuseum.org/art/collection/search/329081", link_text="The Met's record",
                 licence="Photo: The Metropolitan Museum of Art, Open Access, public domain."),
            dict(title="Clay envelope with tokens, Susa", text="A hollow clay ball (bulla) that held tokens, with impressions on its surface. Musée du Louvre, SB 1967.",
                 draw=C.draw_bulla, link="https://collections.louvre.fr/en/ark:/53355/cl010176019", link_text="The Louvre's record",
                 licence="Drawn placeholder; the museum's photographs are at the link."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "Carries, Combinatorics, and an Amazing Matrix", "John M. Holte, American Mathematical Monthly 104 (1997)", "https://sites.math.washington.edu/~billey/classes/561.fall.2019/past.articles/holte.pdf", "Carries form a Markov chain; in the long run half the columns carry"),
            ("scholar", "Preliminary discussion of the logical design of an electronic computing instrument", "Burks, Goldstine and von Neumann (1946)", "https://www.cs.unc.edu/~adyilie/comp265/vonNeumann.html", "Section 5.6: the longest carry sequence averages about 5 for 40 digits"),
            ("scholar", "Carries, Shuffling and An Amazing Matrix", "Diaconis and Fulman (2008), arXiv", "https://ar5iv.labs.arxiv.org/html/0806.3583", "Where Holte's carries chain leads: card shuffling and Eulerian numbers"),
        ]),
        C.prove_it_section(ctx, "GroupingAndCarry", d["checks"],
                           f"pool-and-exchange against ordinary addition on {d['addcheck']:,} random pairs in three systems, the ladders against Melville's totals, and every binary carry against the machine's own addition.",
                           ["static Sum add(NumberSystem s, int[] a, int[] b, boolean keepStates)"]),
    ]
    return dict(
        title="Grouping and the First Carry", date="c. 3200–3000 BCE",
        description="Era 1, topic 2 of The Algorithm Evolution Atlas: grouped numerals in Egypt and Sumer and the first carry, with a pool-and-exchange board, diagrams and verified links.",
        lede="Give each bundle of marks its own sign, and adding becomes two moves: pool the signs, then exchange ten of one for one of the next. That exchange is the carry, and it is older than place value.",
        fieldnote="Fourteen strokes in a row cannot be read at a glance; ten strokes swapped for one new sign can. Once the signs exist, adding is pooling them, and whenever too many of one sign pile up you exchange them for one of the next.",
        card=[("When", "Uruk accounts c. 3200–3000 BCE · Egyptian numerals from c. 3000 BCE (**documented**)"),
              ("Where", "Mesopotamia and Egypt"),
              ("What hurt", "Long rows of marks are slow to write and impossible to read at a glance"),
              ("The fix", "A sign for each bundle; add by pooling and exchanging"),
              ("Cost", f"{s168['n']} takes {s168['egy']} Egyptian signs instead of {s168['tally']} marks"),
              ("Atlas", "Ch. 7.1 Computational limits of additive numerals · Ch. 89 Numeral Systems")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `GroupingAndCarry.java`. The signs are simplified drawings made for this book.",
    )
