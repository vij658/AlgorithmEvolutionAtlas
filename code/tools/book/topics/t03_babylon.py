"""Era 1, topic 3: Babylonian place value and reciprocal tables. Every number is parsed from BabylonianPlaceValue.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"sexa": {}, "table": [], "repeat": [], "divide": [], "regular": [], "magic": {}}
    for ln in text.splitlines():
        if m := re.match(r"sexa (\d+): digits=([\d,]+) wedges=(\d+) egyptian-signs=(\d+)$", ln):
            d["sexa"][int(m.group(1))] = dict(digits=m.group(2), wedges=int(m.group(3)), egy=int(m.group(4)))
        elif m := re.match(r"average 1-9999: wedges=([\d.]+) egyptian-signs=([\d.]+) most-wedges=(\d+) at (\d+) \(([\d,]+)\)$", ln):
            d["avg"] = dict(wedges=float(m.group(1)), egy=float(m.group(2)), most=int(m.group(3)), at=int(m.group(4)), at_s=m.group(5))
        elif m := re.match(r"look below (\d+): no point: (\d+) numbers look like another; no point and no zero: (\d+); largest look-alike group (\d+)", ln):
            d["look"] = dict(limit=int(m.group(1)), point=int(m.group(2)), zero=int(m.group(3)), group=int(m.group(4)))
        elif m := re.match(r"table ([\d,]+): reciprocal=([\d,]+) head=(\d+)$", ln):
            d["table"].append((m.group(1), m.group(2), int(m.group(3))))
        elif m := re.match(r"tablecheck: (\d+) of (\d+) entries", ln):
            d["tablecheck"] = (int(m.group(1)), int(m.group(2)))
        elif m := re.match(r"skipped 2-81: (\d+) regular numbers listed, (\d+) skipped; first skipped ([\d ]+)$", ln):
            d["listed"], d["skipped"], d["first_skipped"] = int(m.group(1)), int(m.group(2)), m.group(3).split()
        elif m := re.match(r"repeat 1/(\d+): 0;([\d,]+),\.\.\. repeats every (\d+) digits$", ln):
            d["repeat"].append(dict(n=int(m.group(1)), digits=m.group(2), period=int(m.group(3))))
        elif m := re.match(r"divide (\d+) / (\d+): reciprocal of ([\d,]+) is ([\d,]+), so ([\d,]+) x ([\d,]+) = ([\d,;]+) \(decimal (.+)\)$", ln):
            d["divide"].append(dict(a=int(m.group(1)), b=int(m.group(2)), b_s=m.group(3), rec=m.group(4), a_s=m.group(5), result=m.group(7), dec=m.group(8)))
        elif m := re.match(r"regular-count up to (\d+): (\d+) numbers \(([\d.]+)%\)$", ln):
            d["regular"].append((int(m.group(1)), int(m.group(2)), float(m.group(3))))
        elif m := re.match(r"plimpton row 1: .* short side ([\d,]+) \((\d+)\), diagonal ([\d,]+) \((\d+)\), long side (\d+)", ln):
            d["plimpton"] = dict(s=m.group(1), s_n=int(m.group(2)), dg=m.group(3), dg_n=int(m.group(4)), l=int(m.group(5)))
        elif m := re.match(r"magic (\d+): multiply by (\d+), then shift right (\d+) bits", ln):
            d["magic"][int(m.group(1))] = (int(m.group(2)), int(m.group(3)))
        elif m := re.match(r"magiccheck: (\d+) divisions", ln):
            d["magiccheck"] = int(m.group(1))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
# wedges: a vertical wedge for 1 and a corner wedge for 10 (simplified drawings)
# ----------------------------------------------------------------------------------------------------------------------
WEDGE_DEFS = ('<defs><symbol id="w-v" viewBox="0 0 12 26"><path d="M1,1 H11 L6,8 Z" fill="currentColor"/>'
              '<line x1="6" y1="6" x2="6" y2="25" stroke="currentColor" stroke-width="2"/></symbol>'
              '<symbol id="w-c" viewBox="0 0 16 22"><path d="M15,2 L3,11 L15,20" fill="none" stroke="currentColor" stroke-width="2"/>'
              '<path d="M2,11 L9,6 L9,16 Z" fill="currentColor"/></symbol></defs>')


def digit_parts(dgt):
    """(kind, dx, dy) for each wedge of one base-60 digit: corner wedges for the tens on the left, units in rows of three."""
    t, o = divmod(dgt, 10)
    parts = []
    for k in range(t):
        parts.append(("c", (k // 3) * 14 + (k % 3) * 2, (k % 3) * 18))
    x0 = (0 if t == 0 else ((t - 1) // 3) * 14 + 22)
    for k in range(o):
        parts.append(("v", x0 + (k % 3) * 11, (k // 3) * 26))
    width = x0 + (min(o, 3) * 11 if o else 0)
    return parts, max(width, 14)


def wedge_number_svg(groups, label):
    """Draw rows of base-60 digits. groups = [(caption, [digits or None for an empty place], note)]."""
    def draw(t, standalone):
        out = [WEDGE_DEFS]
        y = 20
        W = 760
        for caption, digits, note in groups:
            out.append(C.text(20, y + 14, caption, t["ink2"], 13, weight=600))
            x = 200
            for dg in digits:
                if dg is None:
                    out.append(C.rect(x, y, 30, 70, "none", t["axis"], 1, extra=";stroke-dasharray:3 3"))
                    x += 44
                    continue
                parts, w = digit_parts(dg)
                for kind, dx, dy in parts:
                    sym, sw, sh = ("w-v", 12, 26) if kind == "v" else ("w-c", 16, 22)
                    out.append(f'<use href="#{sym}" x="{x + dx}" y="{y + dy}" width="{sw}" height="{sh}" style="color:{t["ink"]}"/>')
                out.append(C.text(x + w / 2, y + 92, dg, t["muted"], 11, "middle"))
                x += w + 26
            out.append(C.text(W - 20, y + 40, note, t["red"], 13, "end", 700))
            y += 118
        return C.svg_doc(W, y, "".join(out), label, t, standalone, 0.6)
    return draw


WEDGE_JS_COMMON = r"""
const WDEFS = WEDGE_DEFS_JSON;
function sexa(n) { if (n === 0) return [0]; const d = []; while (n > 0) { d.unshift(n % 60); n = Math.floor(n / 60); } return d; }
function digitParts(dg) {
  const t = Math.floor(dg / 10), o = dg % 10, parts = [];
  for (let k = 0; k < t; k++) parts.push(["c", Math.floor(k / 3) * 14 + (k % 3) * 2, (k % 3) * 18]);
  const x0 = t === 0 ? 0 : Math.floor((t - 1) / 3) * 14 + 22;
  for (let k = 0; k < o; k++) parts.push(["v", x0 + (k % 3) * 11, Math.floor(k / 3) * 26]);
  return [parts, Math.max(x0 + (o ? Math.min(o, 3) * 11 : 0), 14)];
}
function drawDigit(svg, dg, x, y, color) {
  const [parts, w] = digitParts(dg);
  for (const [kind, dx, dy] of parts) {
    const u = sv("use", {href: kind === "v" ? "#w-v" : "#w-c", x: x + dx, y: y + dy, width: kind === "v" ? 12 : 16, height: kind === "v" ? 26 : 22}, svg);
    u.style.color = color;
  }
  return w;
}
"""

READ_HTML = """
<div class="board wedge-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="wr-n">Number <input id="wr-n" type="number" min="0" max="12959999" value="4622" inputmode="numeric"></label>
      <label><input id="wr-zero" type="checkbox"> No zero: empty places vanish</label>
    </div>
    <div class="scrollx"><svg id="wr-svg" role="img" aria-label="The number written in wedges, one group per base-60 place"></svg></div>
    <div class="presets" aria-label="Examples">
      <button type="button" data-n="4622">4,622</button><button type="button" data-n="59">59</button>
      <button type="button" data-n="60">60</button><button type="button" data-n="61">61</button>
      <button type="button" data-n="3601">3,601</button><button type="button" data-n="7199">7,199</button>
      <button type="button" data-n="12959999">12,959,999</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">How a reader sees it</div>
    <p class="say" id="wr-say" aria-live="polite"></p>
    <p class="say" id="wr-alike"></p>
  </div>
</div>
"""

READ_JS = r"""
(() => {
  const svg = document.getElementById("wr-svg");
  if (!svg) return;
  const place = ["1s", "60s", "3,600s", "216,000s"];
  function lookZero(n) { return sexa(n).filter(x => x !== 0).join(","); }
  function lookPoint(n) { const d = sexa(n); while (d.length > 1 && d[d.length - 1] === 0) d.pop(); return d.join(","); }
  function draw() {
    let n = Math.max(0, Math.min(12959999, Math.floor(+document.getElementById("wr-n").value || 0)));
    const noZero = document.getElementById("wr-zero").checked;
    const d = sexa(n);
    svg.innerHTML = WDEFS;
    let x = 20;
    d.forEach((dg, i) => {
      const p = d.length - 1 - i;
      if (dg === 0) {
        if (!noZero) { sv("rect", {x, y: 16, width: 30, height: 70, fill: "none", stroke: "var(--axis)", "stroke-dasharray": "3 3"}, svg); }
        if (!noZero) { sv("text", {x: x + 15, y: 116, "text-anchor": "middle", fill: "var(--muted)", "font-size": 11}, svg, place[p]); x += 64; }
        return;
      }
      const w = drawDigit(svg, dg, x, 16, "var(--ink)");
      sv("text", {x: x + w / 2, y: 104, "text-anchor": "middle", fill: "var(--ink-2)", "font-size": 12, "font-weight": 600}, svg, String(dg));
      if (!noZero) sv("text", {x: x + w / 2, y: 120, "text-anchor": "middle", fill: "var(--muted)", "font-size": 11}, svg, place[p]);
      x += Math.max(w, 40) + 30;
    });
    svg.setAttribute("viewBox", `0 0 ${Math.max(x, 300)} 130`);
    const say = document.getElementById("wr-say");
    const parts = d.map((dg, i) => `${dg} × ${fmt(60 ** (d.length - 1 - i))}`).join(" + ");
    say.innerHTML = `<b>${fmt(n)}</b> = ${d.join(",")} in base 60 = ${parts}. Only two signs are needed: a corner wedge for each ten and a vertical wedge for each one.`;
    const alike = document.getElementById("wr-alike");
    if (n >= 216000 || n === 0) { alike.textContent = ""; return; }
    const key = noZero ? lookZero(n) : lookPoint(n), same = [];
    for (let m = 1; m < 216000 && same.length < 12; m++) if (m !== n && (noZero ? lookZero(m) : lookPoint(m)) === key) same.push(fmt(m));
    alike.innerHTML = same.length ? `With no point${noZero ? " and no zero" : ""}, these numbers below 216,000 look exactly the same: <b>${same.join(", ")}</b>. The reader had to know from context.`
                                  : `No other number below 216,000 looks like this one${noZero ? ", even without a zero" : ""}.`;
  }
  document.getElementById("wr-n").addEventListener("input", draw);
  document.getElementById("wr-zero").addEventListener("change", draw);
  document.querySelectorAll(".wedge-board .presets button").forEach(b => b.addEventListener("click", () => { document.getElementById("wr-n").value = b.dataset.n; draw(); }));
  draw();
})();
"""

DIV_HTML = """
<div class="board div-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="dv-a">Divide <input id="dv-a" type="number" min="1" max="999999" value="100" inputmode="numeric"></label>
      <label for="dv-b">by <input id="dv-b" type="number" min="1" max="999999" value="16" inputmode="numeric"></label>
    </div>
    <div class="recip-grid" id="dv-grid" aria-label="The standard reciprocal table"></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Divide by multiplying</div>
    <p class="say" id="dv-say" aria-live="polite"></p>
  </div>
</div>
"""

DIV_JS = r"""
(() => {
  const grid = document.getElementById("dv-grid");
  if (!grid) return;
  const TABLE = TABLE_JSON;
  TABLE.forEach(([h, r, n]) => {
    const b = el("button", {type: "button", "data-n": n, title: `reciprocal of ${h} (${n}) is ${r}`}, grid);
    el("span", {class: "h"}, b, h); el("span", {class: "r"}, b, r);
    b.addEventListener("click", () => { document.getElementById("dv-b").value = n; run(); });
  });
  const regular = n => { for (const p of [2, 3, 5]) while (n % p === 0) n /= p; return n === 1; };
  const sx = n => { n = BigInt(n); if (n === 0n) return "0"; const d = []; while (n > 0n) { d.unshift(String(n % 60n)); n /= 60n; } return d.join(","); };
  const pad = (k, j) => { const d = sx(k).split(","); while (d.length < j) d.unshift("0"); return d.join(","); };
  function recipDigits(b) {             // 60^j / b, with the smallest j that works
    let p = 1n, j = 0; const B = BigInt(b);
    while (p % B !== 0n) { p *= 60n; j++; }
    return [p / B, j, p];
  }
  function fracDigits(num, den, max) {   // base-60 digits of num/den after the point
    const out = []; let r = num % den;
    for (let i = 0; i < max && r !== 0n; i++) { r *= 60n; out.push(String(r / den)); r %= den; }
    return [out, r !== 0n];
  }
  function run() {
    const a = Math.max(1, Math.floor(+document.getElementById("dv-a").value || 1));
    const b = Math.max(1, Math.floor(+document.getElementById("dv-b").value || 1));
    grid.querySelectorAll("button").forEach(x => x.classList.toggle("on", +x.dataset.n === b));
    const say = document.getElementById("dv-say");
    const A = BigInt(a), B = BigInt(b);
    if (!regular(b)) {
      const [f] = fracDigits(1n, B, 7);
      const q = A / B, [qf, more] = fracDigits(A, B, 4);
      say.innerHTML = `<b>${fmt(b)}</b> has a prime factor other than 2, 3 and 5, so its reciprocal never ends: 1/${fmt(b)} = 0;${f.join(",")},… The standard table skips it. ` +
                      `The quotient can only be approximated: ${fmt(a)} / ${fmt(b)} ≈ ${sx(q)};${qf.join(",")}${more ? ",…" : ""}.`;
      return;
    }
    const [k, j, p] = recipDigits(b);
    const prod = A * k;                 // a × (1/b) × 60^j
    const whole = prod / p, [fd] = fracDigits(prod, p, 12);
    const inTable = TABLE.some(t => t[2] === b);
    say.innerHTML = `${inTable ? "Look up" : "Work out"} the reciprocal: 1/${fmt(b)} = ${j === 0 ? "1" : "0;" + pad(k, j)}` +
                    ` (written ${sx(k)}, with no point). ${inTable ? "It is in the table." : "It is not in the standard table, but it still ends."}<br>` +
                    `Multiply: ${sx(A)} × ${sx(k)} = ${sx(prod)}. Placing the point: <b>${fmt(a)} / ${fmt(b)} = ${sx(whole)}${fd.length ? ";" + fd.join(",") : ""}</b>` +
                    ` (in decimal, ${(a / b).toLocaleString("en-US", {maximumFractionDigits: 8})}).`;
  }
  ["dv-a", "dv-b"].forEach(id => document.getElementById(id).addEventListener("input", run));
  run();
})();
"""

BAB_CSS = """
.wedge-board svg, .div-board svg{background:none}
.wedge-board .scrollx svg{min-width:300px;width:100%;max-height:150px}
.wedge-board .controls input[type=checkbox]{width:auto}
.wedge-board .say, .div-board .say{font-size:15px;margin:0 0 10px}
.recip-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(112px,1fr));gap:6px}
.recip-grid button{display:flex;justify-content:space-between;gap:6px;font-family:var(--mono);font-weight:400;font-size:12.5px;padding:4px 8px;border-width:1px;border-color:var(--axis)}
.recip-grid button .r{color:var(--muted)}
.recip-grid button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.recip-grid button.on .r{color:var(--paper)}
"""


# ----------------------------------------------------------------------------------------------------------------------
# diagrams
# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 620, "How place value combined with other ideas, from grouped signs to compilers that divide by multiplying")
    W, H = 210, 76
    nodes = {
        "grp": (200, 20, "Grouped signs", "", "topic 2", "ink"),
        "lad": (590, 20, "The 10-and-6 ladder", "", "Sumer, topic 2", "ink"),
        "pv": (395, 150, "Place value, base 60", "⊕ position names the bundle", "probably c. 2100 BCE", "red"),
        "rt": (180, 290, "Reciprocal tables", "⊕ work out 1/n in advance", "school tablets, c. 1800 BCE", "red"),
        "sq": (610, 290, "√2 to three places", "⊕ approximation", "topic 4", "ink"),
        "dm": (180, 420, "Division as multiplication", "⊕ look up, then multiply", "a / b = a × 1/b", "ink"),
        "zr": (610, 420, "A sign for nothing", "⊕ zero in empty places", "later Babylonian; era 2", "ink"),
        "cc": (180, 540, "Compiler division", "⊕ binary: multiply, then shift", "Granlund and Montgomery, 1994", "blue"),
        "tm": (610, 540, "Minutes and seconds", "", "base 60, still on every clock", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    for a, b in [("grp", "pv"), ("lad", "pv"), ("pv", "rt"), ("pv", "sq"), ("rt", "dm"), ("dm", "cc")]:
        D.edge(a, b, ports=("bottom", "top"))
    D.edge("pv", "zr", ports=("right", "top"))
    D.edge("zr", "tm", ports=("bottom", "top"), dashed=True)
    return D


def chain(d):
    s9999 = d["sexa"][9999]
    steps = [
        (f"Every power needs its own sign: 9,999 takes {s9999['egy']} Egyptian signs", f"Let position name the bundle: 9,999 is {s9999['digits']}, {s9999['wedges']} wedges of two kinds", "probably c. 2100 BCE"),
        ("Dividing piles of signs is slow and error-prone", "Divide by multiplying with a reciprocal from a table", "school tables, c. 1800 BCE"),
        (f"Only some numbers have reciprocals that end: 1/7 = 0;{d['repeat'][0]['digits'].split(',')[0]},{d['repeat'][0]['digits'].split(',')[1]},{d['repeat'][0]['digits'].split(',')[2]}, ... forever",
         "Work with regular numbers, and approximate the rest", "topic 4"),
        ("No zero and no point: 61 and 3,601 look the same", "A sign for an empty place, then zero", "later Babylonian; era 2"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from too many signs to the missing zero")
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


def division_then_now(d):
    dv = d["divide"][0]
    m7, s7 = d["magic"][7]
    D = Diagram(1000, 300, "Dividing by multiplying with a precomputed reciprocal, then and now")
    D.text(20, 30, "A SCRIBE, C. 1800 BCE", "tag")
    D.text(20, 180, "A COMPILER, SINCE 1994", "tag")
    rows = [("s", 44, [f"{dv['a']} ÷ {dv['b']}", f"look up 1/{dv['b']}: {dv['rec']}", f"multiply: {dv['a_s']} × {dv['rec']}", f"place the point: {dv['result']}"], "ink"),
            ("c", 194, ["n ÷ 7", f"precomputed m = {m7:,}", "multiply: n × m", f"shift right {s7} bits"], "blue")]
    for key, y, boxes, color in rows:
        for i, txt in enumerate(boxes):
            D.node(f"{key}{i}", 20 + i * 245, y, 210, 64, [(txt, "combo")], color=color if i else "ink")
            if i:
                D.edge(f"{key}{i - 1}", f"{key}{i}", ports=("right", "left"))
    return D


def plimpton(d):
    p = d["plimpton"]
    D = Diagram(1000, 250, "Row 1 of Plimpton 322 rebuilt from the reciprocal pair 2;24 and 0;25")
    steps = [("A reciprocal pair", "x = 2;24 and 1/x = 0;25", "both from the table's world"),
             ("Half the difference, half the sum", "0;59,30 and 1;24,30", ""),
             ("Clear common factors 2, 3, 5", f"{p['s']} and {p['dg']}", f"= {p['s_n']} and {p['dg_n']}"),
             ("A right triangle", f"{p['dg_n']}² − {p['s_n']}² = {p['l']}²", "row 1 of the tablet")]
    for i, (t, combo, note) in enumerate(steps):
        D.node(i, 20 + i * 245, 60, 210, 100, [(t, "title"), (combo, "combo")] + ([(note, "note")] if note else []), color="red" if i == 3 else "ink")
        if i:
            D.edge(i - 1, i, ports=("right", "left"))
    D.text(20, 34, "ROBSON'S READING, FOLLOWING BRUINS: THE TABLET STARTS FROM RECIPROCAL PAIRS", "tag")
    D.text(20, 210, "Other readings: Pythagorean triples (Neugebauer and Sachs, 1945); an exact trigonometric table (Mansfield and Wildberger, 2017). Disputed.", "caption")
    return D


def lookalike(d):
    lk = d["look"]
    D = Diagram(1000, 250, "Without zero or point, different numbers look the same")
    D.node("a", 20, 30, 200, 60, [("1", "big"), ("one", "note")])
    D.node("b", 20, 100, 200, 60, [("1,0", "big"), ("sixty", "note")])
    D.node("c", 20, 170, 200, 60, [("1,0,0", "big"), ("3,600", "note")])
    D.node("x", 380, 100, 220, 60, [("All written alike", "title"), ("one vertical wedge", "note")], color="red")
    for k in "abc":
        D.edge(k, "x", ports=("right", "left"))
    D.node("p", 700, 30, 280, 90, [("NO POINT", "tag"), (f"{lk['point']:,} of the numbers below {lk['limit']:,} look like another", "combo")], color="ink")
    D.node("z", 700, 140, 280, 90, [("NO POINT AND NO ZERO", "tag"), (f"{lk['zero']:,} of them look like another", "combo")], color="red")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    import json
    d = parse(ctx["out"])
    av, lk = d["avg"], d["look"]
    s4622, s9999 = d["sexa"][4622], d["sexa"][9999]
    dv = d["divide"]
    m7 = d["magic"][7]
    js_table = [[h, r, n] for h, r, n in d["table"]]
    read_js = WEDGE_JS_COMMON.replace("WEDGE_DEFS_JSON", json.dumps(WEDGE_DEFS)) + READ_JS
    div_js = DIV_JS.replace("TABLE_JSON", json.dumps(js_table))
    table_rows = []
    rows = d["table"]
    half = (len(rows) + 1) // 2
    for i in range(half):
        a = rows[i]
        b = rows[i + half] if i + half < len(rows) else ("", "", "")
        table_rows.append([a[0], a[2], a[1], b[0], b[2] if b[2] != "" else "", b[1]])
    reg = d["regular"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Here the grouped signs of topic 2 meet the Sumerian ladder of tens and sixes, and position takes over the work that new signs did before. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: place value and the tables it made possible. Blue: where the ideas live in 2026. The dashed arrow is survival rather than descent: base 60 lives on in clocks and angles."),
        ]),
        dict(id="read", eyebrow="Try it", title="Two signs, sixty digits", toc="Try it", blocks=[
            dict(type="p", text="A Babylonian number is a row of base-60 digits. Each digit is written with two signs only: a corner wedge for each ten and a vertical wedge for each one. Type a number, then switch off the empty places, as an Old Babylonian scribe would have written it."),
            dict(type="widget", html=READ_HTML, js=read_js, css=BAB_CSS,
                 fallback=dict(type="svg", name="wedges", alt="4,622, 61 and 3,601 written in wedges",
                               draw=wedge_number_svg([("4,622 = 1,17,2", [1, 17, 2], ""), ("61 = 1,1", [1, 1], ""), ("3,601 = 1,0,1", [1, None, 1], "looks like 61")],
                                                     "4,622, 61 and 3,601 written in wedges")),
                 note="In the interactive edition you can type any number and see which others look the same."),
            dict(type="p", text=f"The wedges are simplified drawings. Two signs suffice for any number, and the average number below 10,000 needs **{av['wedges']:.2f}** wedges against {av['egy']:.2f} Egyptian signs."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
            dict(type="diagram", name="lookalike", diagram=lookalike(d),
                 caption=f"MacTutor: \"The numbers 1 and 1,0, namely 1 and 60 in decimals, had exactly the same representation.\" The counts are for the {lk['limit'] - 1:,} numbers from 1 to {lk['limit'] - 1:,}."),
        ]),
        dict(id="steps", eyebrow="Step by step", title="Divide by looking up", toc="Step by step", blocks=[
            dict(type="p", text="\"For Old Babylonians, division by n amounted to multiplication by 1/n\" (AMS Feature Column). Pick a divisor in the standard reciprocal table, or type any number:"),
            dict(type="widget", html=DIV_HTML, js=div_js,
                 fallback=dict(type="table", head=["Number", "In decimal", "Reciprocal", "Number", "In decimal", "Reciprocal"], num=[1, 4], rows=table_rows),
                 note="In the interactive edition you can divide any two numbers with the table."),
            dict(type="table", head=["Division", "Reciprocal of the divisor", "Multiply", "Result (base 60)", "Decimal"], num=[],
                 rows=[[f"{x['a']:,} ÷ {x['b']}", x["rec"], f"{x['a_s']} × {x['rec']}", f"**{x['result']}**", x["dec"]] for x in dv]),
            dict(type="callout", kind="key", label="Key idea",
                 text=f"The table holds exactly the **{d['listed']}** regular numbers from 2 to 81, those with no prime factors but 2, 3 and 5; the program recomputed all {d['tablecheck'][0]} entries of Duncan Melville's transcription. "
                      f"The other {d['skipped']} are skipped, starting with {', '.join(d['first_skipped'][:6])}: their reciprocals never end in base 60. And base 60 ends where base 10 cannot: {dv[2]['a']} ÷ {dv[2]['b']} is exactly {dv[2]['result']}, but {dv[2]['dec']} in decimal."),
            dict(type="table", head=["Reciprocal", "Base-60 digits", "Repeats every"], num=[2],
                 rows=[[f"1/{r['n']}", f"0;{r['digits']},…", f"{r['period']} digits"] for r in d["repeat"]]),
        ]),
        dict(id="plimpton", eyebrow="The evidence", title="Plimpton 322: what was it for?", toc="The evidence", blocks=[
            dict(type="p", text="Plimpton 322, probably from Larsa about 1820–1762 BCE, is a table of fifteen rows of large base-60 numbers. Each row gives two sides of a right triangle with whole-number sides. Scholars agree on that, and disagree on why the table was made. One reading builds every row from a reciprocal pair, the same kind of number the reciprocal tables list:"),
            dict(type="diagram", name="plimpton", diagram=plimpton(d)),
            dict(type="p", text="The program follows the reciprocal-pair route for row 1 and gets the tablet's numbers exactly. That shows the route works, not that the scribe took it. The trigonometric reading drew wide press attention in 2017 and pointed criticism; Robson had already called trigonometry here \"conceptually anachronistic\" (2002)."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How far does a table of regular numbers reach?", toc="Measured", blocks=[
            dict(type="p", text="Regular numbers thin out fast. A table that covers most small divisors covers almost none of the large ones:"),
            dict(type="table", head=["Up to", "Regular numbers", "Share"], num=[0, 1, 2], rows=[[f"{n:,}", f"{c:,}", f"{p:.3f}%"] for n, c, p in reg]),
            dict(type="p", text=f"Below 10,000 the most wedges any number needs is **{av['most']}**, for {av['at']:,} = {av['at_s']}. With place value, the cost of writing grows with the number of places, not with the size of the number."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Your compiler divides like a scribe", toc="Full circle", blocks=[
            dict(type="p", text="Division is slower than multiplication on a processor. In 1994 Torbjörn Granlund and Peter Montgomery published code sequences that divide by a constant using a multiplication, and implemented them in the GCC compiler. The constant's \"reciprocal\" is worked out once, when the program is compiled, just as the scribe's reciprocals were worked out once and copied onto tablets."),
            dict(type="diagram", name="thennow", diagram=division_then_now(d)),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"To divide a 32-bit number by 7, multiply by **{m7[0]:,}** and shift right {m7[1]} bits. The program checked the method on **{d['magiccheck']:,}** divisions by every divisor from 1 to 1,000: it never disagreed with ordinary division."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write 4,622 in base 60. How many wedges does it need?",
             f"4,622 = 1 × 3,600 + 17 × 60 + 2, so **{s4622['digits']}**: {s4622['wedges']} wedges (1, then 1 ten and 7 ones, then 2). Egyptian signs need {s4622['egy']}."),
            ("Why do 1 and 60 look the same on an Old Babylonian tablet?",
             "60 is 1,0: a 1 in the sixties place and nothing in the ones place. With no zero and no point, the empty place is invisible, so both are a single vertical wedge."),
            (f"Divide {dv[0]['a']} by {dv[0]['b']} the Babylonian way.",
             f"The table gives 1/{dv[0]['b']} = {dv[0]['rec']}. Multiply {dv[0]['a_s']} × {dv[0]['rec']} and place the point: **{dv[0]['result']}**, which is {dv[0]['dec']}."),
            ("Why is 7 missing from the reciprocal table?",
             f"7 is not a factor of any power of 60, so 1/7 never ends in base 60: 0;{d['repeat'][0]['digits']},… repeating every {d['repeat'][0]['period']} digits."),
            ("Which numbers have reciprocals that end in base 60, and which in base 10?",
             "Base 60: numbers whose only prime factors are 2, 3 and 5. Base 10: only 2 and 5. So 1/3, 1/6, 1/12 end in base 60 but not in base 10."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Plimpton 322", text="Probably Larsa, c. 1820–1762 BCE. Fifteen rows of right-triangle numbers. Columbia University Library.",
                 draw=lambda t, s: C.draw_tablet(t, s), link="https://cdli.earth/artifacts/254790", link_text="CDLI record, with photographs",
                 licence="Drawn placeholder; photographs at the link."),
            dict(title="A school multiplication table", text="Old Babylonian, from Nippur. Penn Museum B6063, shown in the exhibition *Before Pythagoras*.",
                 draw=lambda t, s: C.draw_tablet(t, s, round_=True), link="https://isaw.nyu.edu/exhibitions/before-pythagoras/items/b-6063/", link_text="ISAW exhibition page",
                 licence="Drawn placeholder; photographs at the link."),
        ])]),
        C.links_section(ctx, extra=[
            ("deeper", "The numbers behind Plimpton 322", "Anthony Phillips, arXiv", "https://arxiv.org/html/1109.3814", "Row 1 from the reciprocal pair 2;24 and 0;25, worked through"),
            ("deeper", "Division by Invariant Integers using Multiplication", "Granlund and Montgomery (1994)", "https://gmplib.org/~tege/divcnst-pldi94.pdf", "Dividing by a constant with one multiplication; implemented in GCC"),
        ]),
        C.prove_it_section(ctx, "BabylonianPlaceValue", d["checks"],
                           f"every entry of the standard reciprocal table recomputed, the table shown to hold exactly the regular numbers from 2 to 81, Plimpton 322's first row rebuilt, and {d['magiccheck']:,} compiler-style divisions checked.",
                           ["static int[] reciprocal(long n)", "static long divideByMagic(long n, long m, int shift)"]),
    ]
    return dict(
        title="Babylonian Place Value", date="c. 2100–1800 BCE",
        description="Era 1, topic 3 of The Algorithm Evolution Atlas: base-60 place value, the missing zero, and division by reciprocal tables, with a wedge reader, a working reciprocal table and verified links.",
        lede="The same wedge means one, sixty or three thousand six hundred, depending only on where it stands. With position comes a new trick: to divide, look up the reciprocal and multiply.",
        fieldnote="Position does the work that new signs did before. With position comes the first precomputed table I have found: division turns into a lookup and a multiplication.",
        card=[("When", "Place value probably by c. 2100 BCE (Ur III) · school tables c. 1800 BCE (**documented**)"),
              ("Where", "Mesopotamia"),
              ("What hurt", "In additive numerals, multiplying and dividing means juggling piles of signs"),
              ("The fix", "Base-60 place value with two signs, and tables of reciprocals"),
              ("Cost", f"9,999 is {s9999['digits']}: {s9999['wedges']} wedges of 2 kinds, against {s9999['egy']} Egyptian signs"),
              ("Atlas", "Ch. 1.2 Clay-tablet procedures · 1.3 Lookup tables · 1.5 Plimpton 322")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BabylonianPlaceValue.java`. The wedges are simplified drawings made for this book.",
    )
