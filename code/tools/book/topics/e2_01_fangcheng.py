"""Era 2, topic 1: elimination on the counting board (fangcheng). Every number is parsed from FangCheng.java's output."""
import math
import re

import common as C
from diagrams import Diagram


def mn(v):
    """A number with a true minus sign."""
    return str(v).replace("-", "−")


def sup(n):
    return str(n).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


def nums(s):
    return [int(x) for x in s.split()]


def parse(text: str) -> dict:
    d = {"p1_steps": [], "an_steps": [], "growth": [], "work": [], "wilk": []}
    for ln in text.splitlines():
        if m := re.match(r"p1 board: (.+)$", ln):
            d["p1_board"] = [nums(c) for c in m.group(1).split(" | ")]
        elif m := re.match(r"p1 step (\d+): column (\d) x (-?\d+) = ([-\d ]+) ; (subtract|add) column (\d) (\d+) times? -> ([-\d ]+)$", ln):
            g = m.groups()
            d["p1_steps"].append(dict(col=int(g[1]), p=int(g[2]), times=nums(g[3]), op=g[4], by=int(g[5]), a=int(g[6]), after=nums(g[7])))
        elif m := re.match(r"p1 triangle: (.+)$", ln):
            d["p1_tri"] = [nums(c) for c in m.group(1).split(" | ")]
        elif m := re.match(r"p1 back: divisor (\d+) ; dividends (\d+) (\d+) (\d+)$", ln):
            d["fa"], d["shi"] = int(m.group(1)), [int(m.group(k)) for k in (2, 3, 4)]
        elif m := re.match(r"p1 answer: top (.+?) ; medium (.+?) ; low (.+?) dou ; (\d+) multiplications ; largest number (\d+)$", ln):
            d["p1_ans"], d["p1_mults"], d["p1_big"] = [m.group(k) for k in (1, 2, 3)], int(m.group(4)), int(m.group(5))
        elif m := re.match(r"animals board: (.+)$", ln):
            d["an_board"] = [nums(c) for c in m.group(1).split(" | ")]
        elif m := re.match(r"animals step (\d+): column (\d) x (-?\d+) = ([-\d ]+) ; (subtract|add) column (\d) (\d+) times? -> ([-\d ]+)$", ln):
            g = m.groups()
            d["an_steps"].append(dict(col=int(g[1]), p=int(g[2]), times=nums(g[3]), op=g[4], by=int(g[5]), a=int(g[6]), after=nums(g[7])))
        elif m := re.match(r"animals answer: cattle (\d+) ; sheep (\d+) ; pig (\d+) ; sign rule: (\d+) like-sign subtractions, (\d+) unlike-sign \(added\), (\d+) from an empty place ; (\d+) negative numbers left", ln):
            g = [int(x) for x in m.groups()]
            d["an_ans"], d["like"], d["unlike"], d["empty"], d["negleft"] = g[:3], g[3], g[4], g[5], g[6]
        elif m := re.match(r"growth (\d+) unknowns: plain (\d+) digits ; common factors cancelled (\d+) digits ; Bareiss (\d+) digits ; answer (\d+) digits$", ln):
            g = [int(x) for x in m.groups()]
            d["growth"].append(dict(n=g[0], plain=g[1], reduced=g[2], bareiss=g[3], answer=g[4]))
        elif m := re.match(r"steps 15 unknowns plain: ([\d ]+)$", ln):
            d["steps_plain"] = nums(m.group(1))
        elif m := re.match(r"steps 15 unknowns bareiss: ([\d ]+)$", ln):
            d["steps_bareiss"] = nums(m.group(1))
        elif m := re.match(r"work (\d+) unknowns: by division (\d+) multiplications ; cross-multiplying (\d+) ; n\^3/3 = (\d+)$", ln):
            g = [int(x) for x in m.groups()]
            d["work"].append(dict(n=g[0], div=g[1], cross=g[2], n3=g[3]))
        elif m := re.match(r"tiny pivot: without pivoting x = (\S+), y = (\S+) ; with partial pivoting x = (\S+), y = (\S+) ; exactly x = (\d+)/(\d+)$", ln):
            d["tiny"] = m.groups()
        elif m := re.match(r"worst case (\d+): growth 2\^(\d+), error (\S+) ; random matrix growth (\S+), error (\S+)$", ln):
            d["wilk"].append(dict(n=int(m.group(1)), exp=int(m.group(2)), err=float(m.group(3)), rgrowth=m.group(4), rerr=float(m.group(5))))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
# rod numerals: units upright, tens lying flat, and so on alternately; a crossing rod stands for five; an empty place
# is left blank. Red rods are positive numbers, black rods negative.
# ----------------------------------------------------------------------------------------------------------------------
def rods(xr, y, v, t, dw=20, h=26):
    """Rod numeral for v, its units cell ending at xr."""
    color = t["red"] if v > 0 else t["ink"]
    out = []
    s = str(abs(v))
    for p, ch in enumerate(reversed(s)):
        dgt = int(ch)
        if dgt == 0:
            continue
        x0 = xr - (p + 1) * dw + 3
        x1 = x0 + dw - 7
        y0, y1 = y + 3, y + h - 3
        ln = lambda a, b, c, e: out.append(C.line(a, b, c, e, color, 2))
        spread = lambda k, lo, hi: [(lo + hi) / 2] if k == 1 else [lo + i * (hi - lo) / (k - 1) for i in range(k)]
        if p % 2 == 0:                                   # upright form
            if dgt <= 5:
                for x in spread(dgt, x0, x1):
                    ln(x, y0, x, y1)
            else:
                ln(x0 - 1, y0, x1 + 1, y0)
                for x in spread(dgt - 5, x0 + 1, x1 - 1):
                    ln(x, y0, x, y1)
        else:                                            # lying form
            ym = (y0 + y1) / 2 - 1
            if dgt <= 5:
                for yy in spread(dgt, y0 + 2, y1 - 2):
                    ln(x0, yy, x1, yy)
            else:
                ln((x0 + x1) / 2, y0 - 1, (x0 + x1) / 2, ym + 2)
                for yy in spread(dgt - 5, ym + 2, y1):
                    ln(x0, yy, x1, yy)
    return "".join(out)


ROWS = ["top grade", "medium grade", "low grade", "total (dou)"]


def board_svg(d):
    """Problem 1 laid out on the board, and the same board after elimination."""
    start, tri = d["p1_board"], d["p1_tri"]

    def draw(t, standalone):
        out = []
        cw, rh, lab = 72, 52, 112

        def one(x, y, cols, title):
            out.append(C.text(x, y - 32, title, t["ink"], 14, "start", 700))
            for j, name in enumerate(["left", "middle", "right"]):
                out.append(C.text(x + lab + j * cw + cw / 2, y - 10, name, t["muted"], 12, "middle"))
            for i, rn in enumerate(ROWS):
                yy = y + i * rh
                out.append(C.text(x + lab - 10, yy + 22, rn, t["ink2"], 12.5, "end"))
                for j, c in enumerate(cols):
                    cx = x + lab + j * cw
                    out.append(C.rect(cx, yy, cw - 4, rh - 4, t["wash"] if i < 3 else t["surface"], t["rule"], 1))
                    v = c[i]
                    if v:
                        out.append(rods(cx + cw / 2 - 2 + len(str(abs(v))) * 10, yy + 4, v, t))
                    out.append(C.text(cx + cw / 2 - 2, yy + rh - 10, v if v else "(empty)", t["muted"] if not v else t["ink2"], 11, "middle"))
        one(20, 60, start, "Problem 1 laid out: one column per condition")
        one(520, 60, tri, "After elimination: a triangle")
        out.append(C.line(460, 150, 505, 150, t["ink2"], 1.5))
        out.append(C.path("M505 150 l-9 -5 v10 z", None, t["ink2"], 0))
        out.append(C.text(20, 290, "Red rods: positive. Units stand upright and tens lie flat; an empty place is left blank.", t["muted"], 12.5))
        return C.svg_doc(860, 300, "".join(out), "Problem 1 of chapter 8 on the counting board, before and after elimination", t, standalone, 0.6, 860)
    return draw


def quarter_svg(d):
    """The board's columns become the rows of the modern matrix."""
    start = d["p1_board"]

    def draw(t, standalone):
        out = []
        cw, rh = 52, 34
        x0, y0 = 40, 50
        out.append(C.text(x0, 28, "THE BOARD: CONDITIONS IN COLUMNS", t["muted"], 12, "start", 700))
        for j, c in enumerate(start):
            for i, v in enumerate(c):
                out.append(C.rect(x0 + j * cw, y0 + i * rh + (8 if i == 3 else 0), cw - 4, rh - 4, t["surface"], t["red"] if j == 2 else t["rule"], 2 if j == 2 else 1))
                out.append(C.text(x0 + j * cw + cw / 2 - 2, y0 + i * rh + (8 if i == 3 else 0) + 20, v, t["ink"], 14, "middle", 700 if j == 2 else 400))
        out.append(C.text(x0 + 2 * cw + cw / 2 - 2, y0 + 4 * rh + 30, "first condition", t["red"], 12, "middle"))
        out.append(C.line(250, 115, 330, 115, t["ink2"], 1.5))
        out.append(C.path("M330 115 l-9 -5 v10 z", None, t["ink2"], 0))
        out.append(C.text(290, 104, "a quarter turn", t["ink2"], 12, "middle"))
        mx, my = 360, 50
        out.append(C.text(mx, 28, "THE MODERN MATRIX: CONDITIONS IN ROWS", t["muted"], 12, "start", 700))
        for r, c in enumerate(reversed(start)):
            for i, v in enumerate(c):
                xx = mx + i * cw + (14 if i == 3 else 0)
                out.append(C.rect(xx, my + r * rh, cw - 4, rh - 4, t["surface"], t["red"] if r == 0 else t["rule"], 2 if r == 0 else 1))
                out.append(C.text(xx + cw / 2 - 2, my + r * rh + 20, v, t["ink"], 14, "middle", 700 if r == 0 else 400))
        out.append(C.line(mx + 3 * cw + 5, my - 2, mx + 3 * cw + 5, my + 3 * rh - 2, t["ink2"], 1.5))
        out.append(C.text(mx, my + 3 * rh + 26, "Row 1: 3x + 2y + z = 39", t["ink2"], 12.5))
        out.append(C.text(mx, my + 3 * rh + 44, "x, y, z: the yield of one bundle of each grade", t["muted"], 12))
        return C.svg_doc(700, 250, "".join(out), "The board turned a quarter turn is the modern matrix", t, standalone, 0.6, 700)
    return draw


# ----------------------------------------------------------------------------------------------------------------------
# the widget: work the board yourself
# ----------------------------------------------------------------------------------------------------------------------
FC_HTML = """
<div class="board fc-board" id="fc-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="fc-prob">Problem <select id="fc-prob"><option value="grain">1: three grades of grain</option><option value="animals">cattle, sheep, pigs</option></select></label>
    </div>
    <div class="controls">
      <button id="fc-next" class="primary" type="button">Next step</button>
      <button id="fc-all" type="button">Finish</button>
      <button id="fc-reset" type="button">Reset</button>
      <label><input id="fc-turn" type="checkbox"> turn it a quarter turn</label>
    </div>
    <div class="scrollx"><div class="fc-grid" id="fc-grid" aria-label="The counting board"></div></div>
    <div class="fc-matrix" id="fc-matrix" hidden></div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">On the board</div>
    <p class="fc-intro" id="fc-intro"></p>
    <p class="say" id="fc-say" aria-live="polite"></p>
    <p class="tally" id="fc-count"></p>
  </div>
</div>
"""

FC_CSS = """
.fc-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px;max-width:100%}
.fc-board .controls input[type=checkbox]{width:auto}
.fc-board .controls label{flex-wrap:wrap;min-width:0}
.fc-grid{display:grid;grid-template-columns:7.5em repeat(3,minmax(76px,1fr));gap:3px;min-width:330px}
.fc-grid .h{font-size:12px;color:var(--muted);text-align:center;align-self:end}
.fc-grid .rl{font-size:12.5px;color:var(--ink-2);align-self:center;text-align:right;padding-right:6px}
.fc-grid .c{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:56px;background:var(--wash);border:1.5px solid var(--rule);padding:4px 2px;min-width:0}
.fc-grid .c.tot{background:var(--surface)}
.fc-grid .c svg{display:block;height:26px;width:auto;max-width:100%;background:none}
.fc-grid .c .v{font-family:var(--mono);font-size:11.5px;color:var(--ink-2)}
.fc-grid .c .v.z{color:var(--muted)}
.fc-grid .c.piv{border-color:var(--blue);box-shadow:inset 0 0 0 1px var(--blue)}
.fc-grid .c.work{border-color:var(--red);box-shadow:inset 0 0 0 1px var(--red)}
.fc-grid .c.done{border-color:var(--ink)}
.fc-matrix{margin-top:12px;font-family:var(--mono);font-size:13.5px;background:var(--surface);border:1px solid var(--rule);padding:10px 12px;overflow-x:auto}
.fc-matrix .r{white-space:pre}
.fc-board .say{font-size:15px}
.fc-board .fc-intro{font-size:13.5px;color:var(--ink-2)}
.fc-board .tally{font-family:var(--mono);font-size:12.5px;color:var(--muted)}
@media (max-width:600px){.fc-grid{grid-template-columns:4.6em repeat(3,minmax(0,1fr));min-width:0}.fc-grid .rl{font-size:11px;padding-right:3px}.fc-grid .c .v{font-size:10.5px}}
"""

FC_JS = r"""
(() => {
  const grid = document.getElementById("fc-grid");
  if (!grid) return;
  const PROBLEMS = {
    grain: { rows: ["top grade", "medium grade", "low grade", "total (dou)"], unk: ["top grade", "medium grade", "low grade"], unit: "dou",
      cnt: (c, k) => `${signed(c)} bundle${Math.abs(c) === 1 ? "" : "s"} of ${["top grade", "medium grade", "low grade"][k]}`,
      one: k => `one bundle of ${["top grade", "medium grade", "low grade"][k]} gives`,
      cols: [[3, 2, 1, 39], [2, 3, 1, 34], [1, 2, 3, 26]],
      intro: "Problem 1: 3 bundles of top grade, 2 of medium and 1 of low grade give 39 dou of grain; 2, 3 and 1 bundles give 34; 1, 2 and 3 give 26. How much does one bundle of each grade give?" },
    animals: { rows: ["cattle", "sheep", "pigs", "cash"], unk: ["cattle", "sheep", "pigs"], unit: "cash",
      cnt: (c, k) => `${signed(c)} ${Math.abs(c) === 1 ? ["cow", "sheep", "pig"][k] : ["cattle", "sheep", "pigs"][k]}`,
      one: k => `one ${["cow", "sheep", "pig"][k]} is worth`,
      cols: [[2, 5, -13, 1000], [3, -9, 3, 0], [-5, 6, 8, -600]],
      intro: "Sell 2 cattle and 5 sheep, buy 13 pigs: 1000 cash left. Sell 3 cattle and 3 pigs, buy 9 sheep: exactly enough. Sell 6 sheep and 8 pigs, buy 5 cattle: 600 short. Selling is laid down positive (red), buying and a shortfall negative (black)." }
  };
  const NAMES = ["right", "middle", "left"];
  const gcd = (a, b) => { a = Math.abs(a); b = Math.abs(b); while (b) [a, b] = [b, a % b]; return a || 1; };
  const frac = (n, d) => { if (d < 0) { n = -n; d = -d; } const g = gcd(n, d); return [n / g, d / g]; };
  const mixed = ([n, d]) => { if (d === 1) return signed(n); const w = Math.trunc(n / d), r = Math.abs(n % d); return w ? `${w} ${r}/${d}` : `${n}/${d}`; };
  const signed = v => v < 0 ? "−" + fmt(-v) : fmt(v);
  let P, B, acts, at, counts;

  function plan(cols) {
    const n = cols.length, b = cols.map(c => c.slice()), out = [];
    for (let k = 0; k < n; k++) {
      for (let j = k + 1; j < n; j++) {
        const a = b[j][k], p = b[k][k];
        if (a === 0) continue;
        const times = b[j].map((v, i) => i < k ? 0 : v * p);
        out.push({ kind: "mul", j, k, board: b.map((c, q) => q === j ? times.slice() : c.slice()),
          say: `Multiply the whole ${NAMES[j]} column by <b>${signed(p)}</b>, the ${NAMES[k]} column's number in place ${k + 1}, so that both have a multiple of the same number there.` });
        const res = [], ev = { like: 0, unlike: 0, empty: 0 };
        for (let i = 0; i <= n; i++) {
          if (i < k) { res.push(0); continue; }
          const x = times[i], y = a * b[k][i];
          if (i > k && y !== 0) { if (x === 0) ev.empty++; else if (Math.sign(x) === Math.sign(y)) ev.like++; else ev.unlike++; }
          res.push(i === k ? 0 : x - y);
        }
        b[j] = res;
        const verb = a > 0 ? `Subtract the ${NAMES[k]} column ${a} time${a === 1 ? "" : "s"}` : `Its number there is negative, so <b>add</b> the ${NAMES[k]} column ${-a} time${a === -1 ? "" : "s"}`;
        const rule = (ev.unlike || ev.empty) ? ` Sign rule on the way: ${ev.like} like-sign subtraction${ev.like === 1 ? "" : "s"}, ${ev.unlike} unlike-sign (which add)${ev.empty ? `, ${ev.empty} taken from an empty place (the sign changes)` : ""}.` : "";
        out.push({ kind: "sub", j, k, ev, board: b.map(c => c.slice()),
          say: `${verb}: place ${k + 1} of the ${NAMES[j]} column is now empty.${rule}` });
      }
    }
    // back up the triangle, with exact fractions
    const x = [];
    for (let k = n - 1; k >= 0; k--) {
      let rest = [b[k][n], 1];
      const terms = [];
      for (let i = k + 1; i < n; i++) {
        if (b[k][i] === 0) continue;
        terms.push(`${signed(b[k][i])} × ${mixed(x[i])}`);
        rest = frac(rest[0] * x[i][1] - b[k][i] * x[i][0] * rest[1], rest[1] * x[i][1]);
      }
      x[k] = frac(rest[0], rest[1] * b[k][k]);
      const known = terms.length ? ` Take away the ${P.unk.slice(k + 1).join(" and ")} already found (${terms.join(", ")}): ` : " ";
      out.push({ kind: "back", j: k, k, board: b.map(c => c.slice()),
        say: `The ${NAMES[k]} column: ${P.cnt(b[k][k], k)}${terms.length ? " and the rest" : ""} make ${signed(b[k][n])}.${known}${P.one(k)} <b>${mixed(x[k])}</b> ${P.unit}.` });
    }
    return out;
  }

  function rods(v) {
    const s = String(Math.abs(v)), DW = 21, H = 26, n = s.length;
    const svg = sv("svg", { viewBox: `0 0 ${n * DW} ${H}`, width: n * DW, height: H, "aria-hidden": "true" });
    const col = v > 0 ? "var(--red)" : "var(--ink)";
    const L = (a, b, c, d) => sv("line", { x1: a, y1: b, x2: c, y2: d, stroke: col, "stroke-width": 2, "stroke-linecap": "round" }, svg);
    const spread = (k, lo, hi) => k === 1 ? [(lo + hi) / 2] : Array.from({ length: k }, (_, i) => lo + i * (hi - lo) / (k - 1));
    for (let q = 0; q < n; q++) {
      const dgt = +s[q], place = n - 1 - q, x0 = q * DW + 3, x1 = x0 + DW - 7, y0 = 3, y1 = H - 3;
      if (!dgt) continue;
      if (place % 2 === 0) {
        if (dgt <= 5) spread(dgt, x0, x1).forEach(x => L(x, y0, x, y1));
        else { L(x0 - 1, y0, x1 + 1, y0); spread(dgt - 5, x0 + 1, x1 - 1).forEach(x => L(x, y0, x, y1)); }
      } else {
        const ym = (y0 + y1) / 2 - 1;
        if (dgt <= 5) spread(dgt, y0 + 2, y1 - 2).forEach(y => L(x0, y, x1, y));
        else { L((x0 + x1) / 2, y0 - 1, (x0 + x1) / 2, ym + 2); spread(dgt - 5, ym + 2, y1).forEach(y => L(x0, y, x1, y)); }
      }
    }
    return svg;
  }

  function paint() {
    const a = at >= 0 ? acts[at] : null, n = B.length;
    grid.innerHTML = "";
    el("div", {}, grid);
    for (let j = n - 1; j >= 0; j--) el("div", { class: "h" }, grid, NAMES[j]);
    for (let i = 0; i <= n; i++) {
      el("div", { class: "rl" }, grid, P.rows[i]);
      for (let j = n - 1; j >= 0; j--) {
        const v = B[j][i];
        let cls = "c" + (i === n ? " tot" : "");
        if (a && a.kind !== "back" && j === a.k) cls += " piv";
        if (a && j === a.j && a.kind !== "back") cls += " work";
        if (a && a.kind === "back" && j === a.j) cls += " done";
        const c = el("div", { class: cls }, grid);
        if (v) c.appendChild(rods(v));
        el("span", { class: "v" + (v ? "" : " z") }, c, v ? signed(v) : "empty");
      }
    }
    const mx = document.getElementById("fc-matrix");
    mx.innerHTML = "";
    el("div", { class: "r" }, mx, "Each condition is a row now, the first at the top:");
    const w = Math.max(...B.flat().map(v => signed(v).length)) + 1;
    for (let j = 0; j < n; j++) el("div", { class: "r" }, mx, "[ " + B[j].slice(0, n).map(v => signed(v).padStart(w)).join("") + "  |" + signed(B[j][n]).padStart(w + 1) + " ]");
    document.getElementById("fc-count").textContent = `step ${at + 1} of ${acts.length} · sign rule so far: ${counts.like} like, ${counts.unlike} unlike, ${counts.empty} from an empty place`;
  }

  function reset() {
    P = PROBLEMS[document.getElementById("fc-prob").value];
    acts = plan(P.cols);
    B = P.cols.map(c => c.slice());
    at = -1;
    counts = { like: 0, unlike: 0, empty: 0 };
    document.getElementById("fc-intro").textContent = P.intro;
    document.getElementById("fc-say").innerHTML = "Each condition is one column of rods, the first on the right. Press <b>Next step</b> to clear the top place of the middle column.";
    paint();
  }
  function step() {
    if (at + 1 >= acts.length) return false;
    at++;
    const a = acts[at];
    B = a.board.map(c => c.slice());
    if (a.ev) for (const k in a.ev) counts[k] += a.ev[k];
    document.getElementById("fc-say").innerHTML = a.say + (at + 1 === acts.length ? " <b>Done.</b>" : "");
    paint();
    return true;
  }
  document.getElementById("fc-next").addEventListener("click", step);
  document.getElementById("fc-all").addEventListener("click", () => { while (step()); });
  document.getElementById("fc-reset").addEventListener("click", reset);
  document.getElementById("fc-prob").addEventListener("change", reset);
  document.getElementById("fc-turn").addEventListener("change", e => { document.getElementById("fc-matrix").hidden = !e.target.checked; });
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 700, "How fangcheng combined with other ideas, from the counting board to the TOP500 list")
    W, H = 210, 86
    nodes = {
        "brd": (180, 20, "Rods in columns", "", "the counting board, Era 1 topic 6", "ink"),
        "sub": (610, 20, "Subtract until it is gone", "", "as in Euclid's algorithm, Era 1 topic 7", "ink"),
        "fc": (370, 160, "Fangcheng", "⊕ eliminate column against column", "Nine Chapters, c. 200 BCE – 50 CE", "red"),
        "neg": (20, 320, "Negative numbers", "⊕ red and black rods, a sign rule", "same chapter", "ink"),
        "qin": (270, 320, "Qin Jiushao", "⊕ shift a polynomial on the board", "1247, topic 9", "ink"),
        "eu": (520, 320, "Elimination in Europe", "found again, independently", "Newton c. 1670; Gauss 1809", "ink"),
        "bar": (770, 320, "Bareiss", "⊕ divide exactly as you go", "1968", "blue"),
        "tur": (520, 470, "Turing; von Neumann", "⊕ rounding error, LU, condition number", "1947–1948", "blue"),
        "hpl": (520, 610 - 20, "LINPACK benchmark", "⊕ rank the fastest computers", "the TOP500 list", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, 260 if k == "fc" else W, H, lines, color=c)
    D.edge("brd", "fc", ports=("bottom", "top:0.3"))
    D.edge("sub", "fc", ports=("bottom", "top:0.7"))
    D.edge("fc", "neg", ports=("bottom:0.15", "top"))
    D.edge("fc", "qin", ports=("bottom:0.35", "top"))
    D.edge("fc", "eu", ports=("bottom:0.65", "top"), dashed=True)
    D.edge("fc", "bar", ports=("bottom:0.85", "top"))
    D.edge("eu", "tur", ports=("bottom", "top"))
    D.edge("tur", "hpl", ports=("bottom", "top"))
    D.text(20, 690, "Dashed: Europe's elimination arose independently (Grcar). Blue: what machines needed.", "caption")
    return D


def chain(d):
    g15 = next(g for g in d["growth"] if g["n"] == 15)
    w60 = next(w for w in d["wilk"] if w["n"] == 60)
    steps = [
        ("Several unknowns tied together: no single condition gives any one of them",
         "Lay each condition down as a column of rods; cross-multiply and subtract, column against column", "Nine Chapters, chapter 8"),
        (f"Subtracting can leave less than nothing: {d['negleft']} numbers on the finished animals board are negative",
         "Red rods for positive, black for negative, and a rule for each case", "Nine Chapters; Liu Hui, 263 CE"),
        (f"Never dividing, the numbers about double in length at each step: {g15['plain']:,} digits with 15 unknowns",
         f"Divide exactly by the previous pivot as you go: {g15['bareiss']} digits", "Bareiss, 1968"),
        ("Machines round off: a pivot of 10⁻²⁰ turns x = 1 into x = 0",
         "Partial pivoting: use the largest number in the column as the pivot", "Wilkinson's term"),
        (f"Partial pivoting can still let numbers grow as 2ⁿ⁻¹: a {w60['err']:.0%} error with 60 unknowns",
         "In practice such growth is almost never seen; why is still an open problem", "Higham; Dopico 2013"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from the counting board to partial pivoting")
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
    s1, s2, s3 = d["p1_steps"]
    a1, a2, a3 = d["an_steps"]
    g = {x["n"]: x for x in d["growth"]}
    w = {x["n"]: x for x in d["work"]}
    wl = {x["n"]: x for x in d["wilk"]}
    tiny = d["tiny"]
    assert int(tiny[4]) == 10 ** 20 and int(tiny[5]) == 10 ** 20 - 1, "the exact answer is 10^20 / (10^20 - 1)"
    exact_x = "10²⁰ / (10²⁰ − 1)"
    ans = d["p1_ans"]
    cat, sheep, pig = d["an_ans"]
    sp, sb = d["steps_plain"], d["steps_bareiss"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The counting board already held numbers in columns of rods (Era 1, topic 6), and repeated subtraction already wore a number down to nothing (topic 7). Chapter 8 of the *Nine Chapters* combined them: each condition of a problem becomes a column, and one column is subtracted from another until a place is empty. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the procedure of this page. Blue: what calculating machines needed from it, two thousand years later."),
        ]),
        dict(id="board", eyebrow="Try it", title="Work the board", toc="Try it", blocks=[
            dict(type="p", text="Each condition is one column of rods, with the first condition on the right. Press **Next step**: the middle column is multiplied by the right column's top number, then the right column is subtracted from it until its top place is empty. When the board is a triangle, the last column holds one unknown alone, and the answer is worked back up. Switch to the animals problem to see negative numbers, as black rods, and turn the board a quarter turn to see the modern matrix."),
            dict(type="widget", html=FC_HTML, js=FC_JS, css=FC_CSS,
                 fallback=dict(type="svg", name="board", draw=board_svg(d), alt="Problem 1 on the counting board, before and after elimination", width=860),
                 note="In the interactive edition you can step through both problems on a board of rods, and turn it into the modern matrix."),
            dict(type="table", head=["Step", "Column", "Multiply by", "Becomes", "Then", "Leaves"], num=[2],
                 rows=[[str(i + 1), ["right", "middle", "left"][s["col"] - 1], mn(s["p"]), " ".join(map(mn, s["times"])),
                        f"{s['op']} the {['right', 'middle', 'left'][s['by'] - 1]} column {s['a']} time{'s' if s['a'] != 1 else ''}", " ".join(map(mn, s["after"]))]
                       for i, s in enumerate(d["p1_steps"])]),
            dict(type="p", text=f"The left column ends as {' '.join(map(str, d['p1_tri'][0]))}: 36 bundles of low grade give 99 dou. The book keeps 36 as a common divisor and works back up with whole numbers: the dividends are {d['shi'][0]}, {d['shi'][1]} and {d['shi'][2]}, so one bundle gives **{ans[0]}**, **{ans[1]}** and **{ans[2]}** dou of grain for the top, medium and low grades. The whole problem took {d['p1_mults']} multiplications, and no number on the board was ever bigger than {d['p1_big']}."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 2, algorithms travel", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="negative", eyebrow="Less than nothing", title="Black rods", toc="Negative numbers", blocks=[
            dict(type="p", text="Another problem of chapter 8 trades animals. Sell 2 cattle and 5 sheep and buy 13 pigs, and 1,000 cash is left. Sell 3 cattle and 3 pigs and buy 9 sheep, and the cash is exactly enough. Sell 6 sheep and 8 pigs and buy 5 cattle, and 600 is short. The method says to lay down the cattle and sheep sold as positive and the 13 pigs bought as negative; red rods were positive and black rods negative."),
            dict(type="table", head=["Step", "Column", "Multiply by", "Becomes", "Then", "Leaves"], num=[2],
                 rows=[[str(i + 1), ["right", "middle", "left"][s["col"] - 1], mn(s["p"]), " ".join(map(mn, s["times"])),
                        f"{s['op']} the {['right', 'middle', 'left'][s['by'] - 1]} column {s['a']} time{'s' if s['a'] != 1 else ''}", " ".join(map(mn, s["after"]))]
                       for i, s in enumerate(d["an_steps"])]),
            dict(type="p", text=f"The answer is a cow **{cat:,}**, a sheep **{sheep}** and a pig **{pig}** cash. On the way the board made {d['like']} subtractions of like signs, {d['unlike']} of unlike signs, which add, and {d['empty']} from an empty place, where the number changes its sign; {d['negleft']} numbers on the finished board are negative. Wikipedia translates the chapter's rule for subtracting as \"divide by the same name, benefit by different names\": take the difference of like signs, add unlike signs. A number taken from an empty place changes its sign."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Negative numbers did not arrive as a philosophy. They arrived as a bookkeeping need inside a procedure: subtracting columns sometimes leaves less than nothing, and the procedure must carry on. Martzloff notes that negative numbers never appear in the statements of the problems, only in the working."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A book known from late copies", toc="The evidence", blocks=[
            dict(type="p", text="The *Nine Chapters on the Mathematical Art* was compiled from older material. Most historians put its origin around 200 BCE; others place it between 100 BCE and 50 CE, and Britannica gives the 1st century BCE to the 1st century CE (**disputed**). Its first explicit mention is on bronze standard measures of 179 CE. Liu Hui wrote his commentary in 263 CE (**documented**). Chapter 8 has 18 problems, with up to six equations in six unknowns."),
            dict(type="p", text="No ancient copy survives. The earliest surviving edition is from 1213, and chapters 6 to 9, chapter 8 among them, were reconstructed from 18th-century quotations of a lost 15th-century encyclopedia. The name \"Gaussian elimination\" is modern: Legendre called the method \"ordinary\" and Gauss called it \"common\" elimination. Grcar argues that European elimination arose independently of China; Hart argues that *fangcheng* was a practice of rod manipulation, recorded by literati who did not perform it (**conjecture**: one author's reading)."),
            dict(type="svg", name="quarter", draw=quarter_svg(d), alt="The board turned a quarter turn is the modern matrix", width=700,
                 caption="The only differences from a first-year linear algebra course: columns instead of rows, and cross-multiplying instead of dividing."),
        ]),
        dict(id="measured", eyebrow="Measured", title="How big do the numbers get?", toc="Measured", blocks=[
            dict(type="p", text="Cross-multiplying keeps every number whole, but it never divides anything out, so each step multiplies two numbers from the step before. On random systems with entries from −9 to 9, the program measured the largest number on the board, in digits, for plain cross-multiplication, for the same with each column's common factor cancelled, and for Bareiss's 1968 method, which divides exactly by the previous pivot."),
            dict(type="table", head=["Unknowns", "Plain cross-multiplying", "Common factors cancelled", "Bareiss (1968)", "Digits in the answer"], num=[0, 1, 2, 3, 4],
                 rows=[[str(x["n"]), f"{x['plain']:,}", str(x["reduced"]), str(x["bareiss"]), str(x["answer"])] for x in d["growth"]]),
            dict(type="details", summary="Place by place, for the 15-unknown system",
                 block=dict(type="table", head=["After place", "Plain cross-multiplying (digits)", "Bareiss (digits)"], num=[0, 1, 2],
                            rows=[[str(i + 1), f"{p:,}", str(b)] for i, (p, b) in enumerate(zip(sp, sb))])),
            dict(type="p", text=f"The plain board about doubles in length at every place: {sp[1]}, {sp[2]}, {sp[3]}, {sp[4]}, {sp[5]}, … {sp[-1]:,} digits. Bareiss's board grows by about a digit a place, ending at {sb[-1]}, about the size of the answer itself."),
            dict(type="table", head=["Unknowns", "Multiplications, dividing", "Multiplications, cross-multiplying", "n³ / 3"], num=[0, 1, 2, 3],
                 rows=[[f"{x['n']:,}", f"{x['div']:,}", f"{x['cross']:,}", f"{x['n3']:,}"] for x in d["work"]]),
            dict(type="p", text="Elimination by division needs (n³ − n) / 3 multiplications; cross-multiplying needs exactly twice as many, because both columns are multiplied. Either way the work grows as the cube of the number of unknowns."),
        ]),
        dict(id="rounding", eyebrow="What machines added", title="Rounding, and the largest pivot", toc="Rounding", blocks=[
            dict(type="p", text=f"A board of rods is exact. A computer's floating-point numbers are not: they keep about 16 significant digits. Take x/10²⁰ + y = 1 and x + y = 2, where x and y are both very nearly 1. Eliminating with the tiny number 10⁻²⁰ as the pivot gives x = **{tiny[0]}** and y = {tiny[1]}: subtracting 10²⁰ times one row from the other rounds away everything the 1s and 2s were saying. Swapping the rows first, so the pivot is the largest number in its column (*partial pivoting*), gives x = {tiny[2]} and y = {tiny[3]}, both right to double precision. Exactly, x = {exact_x}, a hair above 1."),
            dict(type="table", head=["Unknowns", "Worst case: growth", "Its error", "Random matrix: growth", "Its error"], num=[0, 2, 3, 4],
                 rows=[[str(x["n"]), f"2{sup(x['exp'])}", f"{x['err']:.1e}", x["rgrowth"], f"{x['rerr']:.1e}"] for x in d["wilk"]]),
            dict(type="p", text=f"Partial pivoting is not a guarantee: Wilkinson showed in 1954 that the numbers can still grow. On the textbook worst case (1 on the diagonal, −1 below it, 1 in the last column) the last column doubles at every step, the numbers grow as 2ⁿ⁻¹, and with 60 unknowns the error is {wl[60]['err']:.0%} of the answer. On random matrices the growth stays below {math.ceil(max(float(x['rgrowth']) for x in d['wilk']))} and the error near 10⁻¹⁵. Dopico quotes Higham: the growth factor \"is almost invariably found to be small\", and why remains an open problem."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Eighteen equations", toc="Full circle", blocks=[
            dict(type="p", text="When the first electronic computers were being built, Gaussian elimination became the first algorithm whose rounding errors were analysed. Von Neumann and Goldstine's 1947 paper was, in Grcar's words, \"the first modern paper in numerical analysis\". Turing's 1948 paper \"Rounding-off errors in matrix processes\" named the LU factorization and introduced the condition number, and argued that earlier warnings about rounding were \"far too pessimistic\". Fox recalled that in 1946 four mathematicians, Turing among them, needed about two weeks to solve 18 equations with desk calculators."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Chapter 8 of the *Nine Chapters* has 18 problems. Eighteen unknowns take {w[18]['div']:,} multiplications by division, plus the work back up: the job that took four people about two weeks in 1946. Today the TOP500 list ranks the world's fastest computers by the LINPACK benchmark: solve one huge dense system of linear equations by LU factorization with partial pivoting, about ⅔n³ operations. The procedure laid out in rods two thousand years ago is still the yardstick for the largest machines."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why multiply the middle column by 3 instead of dividing the right column by 3?",
             "Rods can show whole numbers, not thirds. Cross-multiplying keeps every number on the board whole; the price is that the numbers grow."),
            (f"After two steps the middle column reads {' '.join(map(str, s1['after']))} and the left {' '.join(map(str, s2['after']))}. What next?",
             f"Multiply the left column by {s3['p']}, the middle column's number in the second place, giving {' '.join(map(str, s3['times']))}; then subtract the middle column {s3['a']} times: {' '.join(map(str, s3['after']))}."),
            (f"In the animals problem, the left column times {a2['p']} begins with {mn(a2['times'][0])}. Why is the right column added, not subtracted?",
             f"The right column begins with {d['an_board'][2][0]}. Adding it {a2['a']} times brings {mn(a2['times'][0])} up to 0; subtracting would drive it further below zero."),
            ("How many digits does the plain board reach with 15 unknowns? And with Bareiss's method?",
             f"**{g[15]['plain']:,}** digits plain, **{g[15]['bareiss']}** with Bareiss: one about doubles at each place, the other grows by about a digit."),
            ("Why did the pivot 10⁻²⁰ give x = 0?",
             "Multiplying a row by 10²⁰ and subtracting leaves numbers near 10²⁰, and the 1s and 2s of the problem are rounded away. With the larger number as pivot, nothing big is subtracted, and nothing is lost."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Nine Chapters, Siku Quanshu edition", text="The imperial library copy of 1773, scanned by Zhejiang University Library. Chapter 8, \"Rectangular Arrays\", is in the volume of chapters 7–9.",
                 draw=C.draw_book, link="https://sourcelibrary.org/book/nine-chapters-on-the-mathematical-art-vols-7-9", link_text="Source Library scan",
                 licence="Drawn placeholder. The English shown beside the scan is a machine translation."),
            dict(title="Counting rods", text="Rod numerals were used from the Warring States period (c. 475 BCE) to the 16th century: units upright, tens lying flat, and an empty place for zero; red for positive, black for negative.",
                 draw=draw_rods, link="https://en.wikipedia.org/wiki/Counting_rods", link_text="Wikipedia: Counting rods",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("start", "The Linpack Benchmark", "TOP500", "https://top500.org/project/linpack/", "The benchmark behind the TOP500 list: a dense linear system by LU factorization with partial pivoting, 2/3 n³ + O(n²) operations"),
            ("start", "Fangcheng (mathematics)", "Wikipedia", "https://en.wikipedia.org/wiki/Fangcheng_(mathematics)", "Problem 1's answer, the procedure for positive and negative numbers, and references"),
            ("start", "Counting rods", "Wikipedia", "https://en.wikipedia.org/wiki/Counting_rods", "How rod numerals are formed; red for positive, black for negative"),
            ("deeper", "Use of the History of Negative Numbers in Education", "Lenka Molitorisová, Comenius University, Bratislava", "https://bibnum.publimath.fr/ACF/ACF11039.pdf", "Quotes the cattle, sheep and pigs problem and Liu Hui's commentary on red and black rods from Shen, Crossley and Lun (1999), p. 405"),
            ("deeper", "Bareiss algorithm", "Wikipedia", "https://en.wikipedia.org/wiki/Bareiss_algorithm", "Fraction-free elimination with exact divisions (Bareiss, Mathematics of Computation, 1968)"),
            ("deeper", "The Suan shu shu and the Nine Chapters on the Mathematical Art: A Comparison", "Megan Ferguson, Adelphi University, 2021 (MAA HOMSIGMAA)", "https://old.maa.org/sites/default/files/images/upload_library/46/HOMSIGMAA/2021-Megan%20Ferguson.pdf", "Quotes Martzloff: negative numbers are never found in the statements of problems"),
            ("scholar", "Alan Turing and the origins of modern Gaussian elimination", "Froilán M. Dopico, Arbor 189 (764), 2013", "https://arbor.revistas.csic.es/index.php/arbor/article/download/1886/2073?inline=1", "Turing's 1948 paper, the name LU, the condition number, partial pivoting and the growth factor"),
            ("scholar", "John von Neumann's Analysis of Gaussian Elimination and the Origins of Modern Numerical Analysis", "Joseph F. Grcar, SIAM Review 53(4), 2011, 607–682", "https://epubs.siam.org/doi/10.1137/080734716", "Why von Neumann and Goldstine's 1947 paper is called the first modern paper in numerical analysis"),
            ("scholar", "The Chinese Rod Numeral Legacy and its Impact on Mathematics", "Lam Lay Yong, presidential address, Singapore Mathematical Society, 1987", "https://sms.math.nus.edu.sg/smsmedley/Vol-15-2/The%20Chinese%20rod%20numeral%20legacy%20and%20its%20impact%20on%20mathematics(Lam%20Lay%20Yong).pdf", "Two sets of rod notations, alternating by place; a horizontal rod for five"),
        ]),
        C.prove_it_section(ctx, "FangCheng", d["checks"],
                           "Problem 1 against its published intermediate columns, the animals problem's answer, plain and cancelled cross-multiplication and Bareiss's method against exact fractions (with every Bareiss division checked for exactness), the multiplication counts, and the rounding examples.",
                           ["static BigInteger boardSubtract(", "static BigInteger[][] fangcheng("]),
    ]
    return dict(
        title="Elimination on the Counting Board", date="c. 200 BCE – 263 CE",
        description="Era 2, topic 1 of The Algorithm Evolution Atlas: fangcheng, elimination on the Chinese counting board, with a board of rods to work, negative numbers, and what computers added.",
        lede="Lay each condition down as a column of rods. Multiply one column by the head of another and subtract, until the board is a triangle and the last unknown stands alone. The world's fastest computers are still ranked by the same procedure.",
        fieldnote="The clerks here faced a knot: several unknowns tied together by several conditions. They did not untie it with words. They laid it out, column by column, and subtracted until it came apart. When subtraction left less than nothing, they changed the colour of the rods and carried on.",
        card=[("When", "*Nine Chapters*, c. 200 BCE – 50 CE (**disputed**); Liu Hui's commentary 263 CE"),
              ("Where", "Han China"),
              ("What hurt", "Several unknowns tied together by several conditions"),
              ("The fix", "One column of rods per condition; cross-multiply and subtract until the board is a triangle"),
              ("Cost", f"(n³ − n) / 3 multiplications dividing, twice that cross-multiplying; plain numbers about double in length each step ({g[15]['plain']:,} digits at 15 unknowns)")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `FangCheng.java`.",
    )


def draw_rods(theme, standalone=False):
    """Drawn placeholder: a few counting rods and the numeral 39 laid out in them."""
    t = theme
    b = [C.rect(0, 0, 200, 150, t["wash"], t["rule"], 1)]
    for i in range(7):
        b.append(C.line(24 + i * 9, 20, 24 + i * 9 + 18, 128, t["red"] if i % 3 else t["ink"], 3))
    b.append(rods(170, 60, 39, t, dw=24, h=36))
    b.append(C.text(134, 120, "39", t["ink2"], 13, "middle"))
    return C.svg_doc(200, 150, "".join(b), "Drawn placeholder of counting rods", theme, standalone, 0.3, 220)
