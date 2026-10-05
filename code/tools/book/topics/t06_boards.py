"""Era 1, topic 6: counting boards and the abacus. Every number is parsed from CountingBoard.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"work": {"plain": [], "fives": []}, "avg": {}}
    for ln in text.splitlines():
        if m := re.match(r"work (plain|fives) (\d+) (\d+): (put down \d+|push on \d+|settled) -> ([\d| ]+) \((\d+) counters\)(?: value=(\d+) exchanges=(\d+) moves=(\d+))?$", ln):
            d["a"], d["b"] = int(m.group(2)), int(m.group(3))
            cols = m.group(5).split()
            d["work"][m.group(1)].append(dict(what=m.group(4), cols=cols, counters=int(m.group(6)),
                                              value=int(m.group(7)) if m.group(7) else None,
                                              exchanges=int(m.group(8)) if m.group(8) else None, moves=int(m.group(9)) if m.group(9) else None))
        elif m := re.match(r"average (plain|fives): (\d+) additions .*?: ([\d.]+) counters left on the board, ([\d.]+) counters moved, ([\d.]+) exchanges per addition; most counters in one settled column (\d+)$", ln):
            d["avg"][m.group(1)] = dict(n=int(m.group(2)), left=float(m.group(3)), moved=float(m.group(4)), ex=float(m.group(5)), most=int(m.group(6)))
        elif m := re.match(r"boardcheck: (\d+) additions and (\d+) subtractions", ln):
            d["boardcheck"] = (int(m.group(1)), int(m.group(2)))
        elif m := re.match(r"invariant: adding (\d+) random numbers below 100,000 \(total (\d+)\): settling after each one, (\d+) exchanges over (\d+) settlings; piling up and settling once, (\d+) exchanges \(a column held up to (\d+) counters\); counters put down (\d+), left (\d+), \(put down - left\) / 9 = (\d+)$", ln):
            d["inv"] = dict(zip(["n", "total", "eager", "settles", "lazy", "most", "down", "left", "div"], (int(m.group(i)) for i in range(1, 10))))
        elif m := re.match(r"invariant fives: settling after each one, (\d+) exchanges; settling once, (\d+) exchanges", ln):
            d["inv_f"] = (int(m.group(1)), int(m.group(2)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
LANE, X0 = 120, 70


def board_svg(states, label):
    """Board states with fives, drawn as lanes: a five above the bar, ones below. states = [(title, cols)], cols 'f|o' high first."""
    def draw(t, standalone):
        out = []
        W = X0 + 5 * LANE + 10
        y0 = 0
        for title, cols in states:
            cols = ["0|0"] * (5 - len(cols)) + cols
            out.append(C.text(20, y0 + 22, title, t["ink2"], 13, weight=700))
            top = y0 + 34
            out.append(C.rect(X0 - 20, top, 5 * LANE, 190, t["wash"], t["rule"], 1))
            out.append(C.line(X0 - 20, top + 54, X0 - 20 + 5 * LANE, top + 54, t["ink"], 2))
            for j, c in enumerate(cols):
                f, o = (int(x) for x in c.split("|"))
                cx = X0 + j * LANE + 40
                out.append(C.line(cx, top + 6, cx, top + 184, t["axis"], 1))
                for k in range(f):
                    out.append(C.circle(cx + (k % 2) * 22 - 11 * (f > 1), top + 26 + (k // 2) * 22, 9, t["blue"]))
                for k in range(o):
                    out.append(C.circle(cx - 11 + (k % 2) * 22, top + 74 + (k // 2) * 22, 9, t["red"]))
                out.append(C.text(cx, top + 208, ["10,000", "1,000", "100", "10", "1"][j], t["muted"], 11, "middle"))
            y0 = top + 220
        return C.svg_doc(W, y0 + 4, "".join(out), label, t, standalone, 0.6)
    return draw


BOARD_HTML = """
<div class="board cb-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="cb-mode">Board <select id="cb-mode"><option value="fives">with fives (like a soroban)</option><option value="plain">plain columns</option></select></label>
      <label for="cb-a">a <input id="cb-a" type="number" min="0" max="9999" value="AV" inputmode="numeric"></label>
      <label for="cb-b">b <input id="cb-b" type="number" min="0" max="9999" value="BV" inputmode="numeric"></label>
    </div>
    <div class="controls">
      <button id="cb-put" class="primary" type="button">Put down a</button>
      <button id="cb-push" type="button">Push on b</button>
      <button id="cb-one" type="button">One exchange</button>
      <button id="cb-all" type="button">Settle</button>
      <button id="cb-clear" type="button">Clear</button>
    </div>
    <div class="scrollx"><svg id="cb-svg" viewBox="0 0 690 400" role="img" aria-label="A counting board with columns for ten thousands, thousands, hundreds, tens and ones"></svg></div>
    <p class="zoomnote">Tap a column to add one counter by hand.</p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">On the board</div>
    <p class="say" id="cb-say" aria-live="polite"></p>
    <p class="tally" id="cb-count"></p>
  </div>
</div>
"""

BOARD_CSS = """
.cb-board select{font:inherit;font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink);border-radius:2px;max-width:100%}
.cb-board .controls input{width:6.5em}
.cb-board svg{background:none;min-width:480px}
.cb-board .say{font-size:15px}
.cb-board .tally{font-family:var(--mono);font-size:13px;color:var(--muted)}
"""

BOARD_JS = r"""
(() => {
  const svg = document.getElementById("cb-svg");
  if (!svg) return;
  const N = 5, LANE = 120, X0 = 70;
  let mode, ones, fives, moves, exchanges, last;
  const val = () => ones.reduce((s, c, i) => s + (c.length + 5 * fives[i].length) * 10 ** i, 0);
  function clear() {
    mode = document.getElementById("cb-mode").value;
    ones = Array.from({length: N + 1}, () => []); fives = Array.from({length: N + 1}, () => []);
    moves = 0; exchanges = 0; last = "The board is empty. Put down the first number.";
    draw();
  }
  function put(n, color) {
    for (let i = 0; n > 0; i++, n = Math.floor(n / 10)) {
      let dg = n % 10;
      if (mode === "fives" && dg >= 5) { fives[i].push(color); moves++; dg -= 5; }
      for (let k = 0; k < dg; k++) { ones[i].push(color); moves++; }
    }
  }
  function exchangeOnce() {
    for (let i = 0; i < N; i++) {
      if (mode === "fives") {
        if (ones[i].length >= 5) { ones[i].splice(-5); fives[i].push("var(--yellow)"); moves += 6; exchanges++; last = `Five ones in the ${name(i)} column become one five.`; return true; }
        if (fives[i].length >= 2) { fives[i].splice(-2); ones[i + 1].push("var(--yellow)"); moves += 3; exchanges++; last = `Two fives in the ${name(i)} column become one counter in the ${name(i + 1)} column.`; return true; }
      } else if (ones[i].length >= 10) { ones[i].splice(-10); ones[i + 1].push("var(--yellow)"); moves += 11; exchanges++; last = `Ten counters in the ${name(i)} column become one in the ${name(i + 1)} column.`; return true; }
    }
    return false;
  }
  const name = i => ["ones", "tens", "hundreds", "thousands", "ten-thousands", "hundred-thousands"][i];
  function draw() {
    svg.innerHTML = "";
    const fiveMode = mode === "fives";
    sv("rect", {x: X0 - 20, y: 20, width: N * LANE, height: 340, fill: "var(--wash)", stroke: "var(--rule)"}, svg);
    if (fiveMode) sv("line", {x1: X0 - 20, y1: 100, x2: X0 - 20 + N * LANE, y2: 100, stroke: "var(--ink)", "stroke-width": 2}, svg);
    for (let j = 0; j < N; j++) {
      const i = N - 1 - j, cx = X0 + j * LANE + 40;
      const lane = sv("rect", {x: cx - 55, y: 20, width: 110, height: 340, fill: "transparent", style: "cursor:pointer"}, svg);
      lane.addEventListener("click", () => { ones[i].push("var(--ink)"); moves++; last = `You added one counter to the ${name(i)} column.`; draw(); });
      sv("line", {x1: cx, y1: 26, x2: cx, y2: 354, stroke: "var(--axis)"}, svg);
      fives[i].forEach((c, k) => sv("circle", {cx: cx - 11 + (k % 2) * 22, cy: 44 + Math.floor(k / 2) * 22, r: 9, fill: c, stroke: "var(--ink)", "stroke-width": 1}, svg));
      const startY = fiveMode ? 122 : 44;
      ones[i].forEach((c, k) => sv("circle", {cx: cx - 11 + (k % 2) * 22, cy: startY + Math.floor(k / 2) * 22, r: 9, fill: c, stroke: "var(--ink)", "stroke-width": 1}, svg));
      const over = fiveMode ? (ones[i].length >= 5 || fives[i].length >= 2) : ones[i].length >= 10;
      sv("text", {x: cx, y: 382, "text-anchor": "middle", fill: over ? "var(--red)" : "var(--muted)", "font-size": 12, "font-weight": over ? 700 : 400}, svg, fmt(10 ** i));
    }
    document.getElementById("cb-say").innerHTML = `${last}<br><b>${fmt(val())}</b> is on the board.`;
    const count = ones.reduce((s, c) => s + c.length, 0) + fives.reduce((s, c) => s + c.length, 0);
    document.getElementById("cb-count").textContent = `${count} counters on the board · ${moves} counters moved · ${exchanges} exchanges. Red: a. Blue: b. Yellow: exchanged.`;
  }
  const A = () => Math.max(0, Math.min(9999, Math.floor(+document.getElementById("cb-a").value || 0)));
  const B = () => Math.max(0, Math.min(9999, Math.floor(+document.getElementById("cb-b").value || 0)));
  document.getElementById("cb-put").addEventListener("click", () => { clear(); put(A(), "var(--red)"); last = `${fmt(A())} is put down: one counter per unit in each column${mode === "fives" ? ", with a five where it saves counters" : ""}.`; draw(); });
  document.getElementById("cb-push").addEventListener("click", () => { put(B(), "var(--blue)"); last = `${fmt(B())} is pushed on. Columns with too many counters are marked red below.`; draw(); });
  document.getElementById("cb-one").addEventListener("click", () => { if (!exchangeOnce()) last = "Every column is settled: nothing to exchange."; draw(); });
  document.getElementById("cb-all").addEventListener("click", () => { let k = 0; while (exchangeOnce()) k++; last = k ? `Settled with ${k} more exchange${k === 1 ? "" : "s"}.` : "Every column is settled: nothing to exchange."; draw(); });
  document.getElementById("cb-clear").addEventListener("click", clear);
  document.getElementById("cb-mode").addEventListener("change", clear);
  clear();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 660, "How the counting board combined with other ideas, from pebbles to carry-save adders")
    W, H = 210, 86
    nodes = {
        "peb": (180, 20, "Pebbles as counters", "", "Latin calculus: a pebble", "ink"),
        "car": (610, 20, "Columns and exchanges", "", "topics 2 and 3", "ink"),
        "brd": (395, 150, "Counting board", "⊕ columns hold the place", "Salamis tablet, c. 300 BCE", "red"),
        "rom": (20, 300, "Roman hand abacus", "⊕ beads in grooves, a five", "bronze; three survive", "ink"),
        "exq": (270, 300, "Exchequer table", "⊕ a chequered cloth", "first mentioned 1110", "ink"),
        "sor": (520, 300, "Suanpan and soroban", "⊕ beads on rods", "suanpan pictured by 1573", "ink"),
        "pen": (770, 300, "Column arithmetic on paper", "⊕ zero and written digits", "era 2", "ink"),
        "mec": (180, 450, "Mechanical calculators", "⊕ gears carry by themselves", "era 3", "blue"),
        "csa": (610, 450, "Carry-save adders", "⊕ settle the carries last", "Wallace's multiplier, 1964", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    D.edge("peb", "brd", ports=("bottom", "top"))
    D.edge("car", "brd", ports=("bottom", "top"))
    for k in ("rom", "exq", "sor", "pen"):
        D.edge("brd", k, ports=("bottom", "top"))
    D.edge("exq", "mec", ports=("bottom", "top"), dashed=True)
    D.edge("sor", "csa", ports=("bottom", "top"), dashed=True)
    D.text(20, 610, "Dashed: the same move in a new material, not a line of descent.", "caption")
    return D


def chain(d):
    av = d["avg"]
    inv = d["inv"]
    steps = [
        ("Greek and Roman numerals are poor for calculating", "Calculate on a board: columns hold the place, counters the digit", "Salamis tablet, c. 300 BCE"),
        (f"A column can hold up to {av['plain']['most']} counters, too many to read at a glance", f"A counter worth five: never more than {av['fives']['most']} in a settled column", "Roman hand abacus, soroban"),
        ("The board keeps no record: the work vanishes as the counters move", "Write the digits, and later do the whole sum on paper", "era 2"),
        ("Settling after every addition means carries ripple every time", f"Pile up and settle once: still {inv['lazy']:,} exchanges for {inv['n']:,} numbers, but one pass", "carry-save adders"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from written numerals to delayed carries")
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


def invariant(d):
    inv = d["inv"]
    D = Diagram(1000, 250, "However you order the exchanges, their number is the same")
    boxes = [("down", f"{inv['down']:,} counters put down", f"{inv['n']:,} numbers below 100,000"),
             ("ex", "Each exchange: 10 off, 1 on", "9 counters fewer every time"),
             ("left", f"{inv['left']} counters left", f"the total, {inv['total']:,}, settled"),
             ("res", f"({inv['down']:,} − {inv['left']}) ÷ 9 = {inv['div']:,}", f"settle each time: {inv['eager']:,} · settle once: {inv['lazy']:,}")]
    for i, (k, t, n) in enumerate(boxes):
        D.node(k, 20 + i * 245, 60, 215, 100, [(t, "combo"), (n, "note")], color="red" if k == "res" else "ink")
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 38, "A PLAIN BOARD, ADDING A THOUSAND NUMBERS", "tag")
    D.text(20, 200, f"Piling up first, one column held {inv['most']:,} counters before settling. Same exchanges, but one pass instead of {inv['settles']:,}.", "caption")
    return D


def words():
    D = Diagram(1000, 200, "Words the counting board left behind")
    pairs = [("calc", "calculus", "Latin: a pebble used as a reckoning counter", "calculate, calculus, calculator"),
             ("exq", "Exchequer", "named after the chequered cloth of the royal accounts", "Chancellor of the Exchequer")]
    for i, (k, w, meaning, now) in enumerate(pairs):
        y = 20 + i * 90
        D.node(k, 20, y, 300, 70, [(w, "title"), (meaning, "note")])
        D.node(k + "n", 620, y, 360, 70, [(now, "combo")], color="blue")
        D.edge(k, k + "n", ports=("right", "left"), label="lives on in", dy=-8)
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    wf, wp = d["work"]["fives"], d["work"]["plain"]
    av = d["avg"]
    inv = d["inv"]
    html = BOARD_HTML.replace("AV", str(d["a"])).replace("BV", str(d["b"]))
    states = [(f"Put down {d['a']:,}", wf[0]["cols"]), (f"Push on {d['b']:,}", wf[1]["cols"]), (f"Settled: {wf[2]['value']:,}", wf[2]["cols"])]
    fmtcols = lambda cols: " · ".join(c.replace("|", "+") for c in cols)
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The counting board puts the exchange of topic 2 and the place value of topic 3 into the hands: columns hold the place, and pebbles hold the count. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the counting board. Blue: machines that settle carries for you, or put it off on purpose."),
        ]),
        dict(id="board", eyebrow="Try it", title="Push the counters, then settle", toc="Try it", blocks=[
            dict(type="p", text="Put down the first number: in each column, as many counters as its digit, with a five-counter above the bar when it saves counters. Push on the second number. Then settle: five ones make a five, and two fives make one counter in the next column."),
            dict(type="widget", html=html, js=BOARD_JS, css=BOARD_CSS,
                 fallback=dict(type="svg", name="board", draw=board_svg(states, f"{d['a']:,} + {d['b']:,} on a counting board with fives"),
                               alt=f"{d['a']:,} + {d['b']:,} on a counting board with fives"),
                 note="In the interactive edition you can push counters on and settle them one exchange at a time."),
            dict(type="p", text="No digit is written at any point. The Latin name for a reckoning pebble, *calculus*, is where the word *calculate* comes from."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="steps", eyebrow="Step by step", title=f"{d['a']:,} + {d['b']:,} on two boards", toc="Step by step", blocks=[
            dict(type="table", head=["Stage", "Plain board (counters per column)", "Counters", "Board with fives (fives + ones)", "Counters"], num=[2, 4],
                 rows=[[wp[i]["what"].capitalize(), " · ".join(wp[i]["cols"]), wp[i]["counters"], fmtcols(wf[i]["cols"]), wf[i]["counters"]] for i in range(3)]),
            dict(type="p", text=f"Both boards end at **{wp[2]['value']:,}**. The plain board needed {wp[2]['exchanges']} exchanges and {wp[2]['moves']} counter moves in all; "
                                f"the board with fives needed {wf[2]['exchanges']} smaller exchanges but only {wf[2]['moves']} moves, because there are fewer counters to push."),
            dict(type="callout", kind="key", label="Key idea",
                 text="The board is a machine for place value. The person adding never thinks about tens or hundreds: they only push counters and make one kind of swap. Later, gears would make that swap by themselves."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="What survives, and what is guessed", toc="The evidence", blocks=[
            dict(type="p", text="The Salamis tablet (Epigraphical Museum, Athens, EM 11515) is a marble slab with ruled lines and Greek number signs, dated to about 300 BCE (the Computer History Museum says the 4th century BCE). "
                                "The museum calls it \"a table of mathematical calculations or a toy\"; it was once thought to be a gaming board. Its use is **disputed**."),
            dict(type="p", text="Three bronze Roman hand abaci survive, in Aosta, Paris and Rome (**documented**). In England, the *Dialogue concerning the Exchequer* (about 1179) describes the royal accounts being reckoned with counters on a table covered with a chequered cloth, which gave the Exchequer its name (**documented**). Early dates for the Chinese suanpan and the Japanese soroban vary widely between sources (**disputed**)."),
            dict(type="diagram", name="words", diagram=words()),
        ]),
        dict(id="measured", eyebrow="Measured", title="Is a five-counter worth it?", toc="Measured", blocks=[
            dict(type="table", head=["Per addition of two numbers below 10,000", "Plain board", "Board with fives"], num=[1, 2],
                 rows=[["Counters left on the board", f"{av['plain']['left']:.2f}", f"{av['fives']['left']:.2f}"],
                       ["Counters moved", f"{av['plain']['moved']:.2f}", f"**{av['fives']['moved']:.2f}**"],
                       ["Exchanges", f"{av['plain']['ex']:.2f}", f"{av['fives']['ex']:.2f}"],
                       ["Most counters in a settled column", av["plain"]["most"], av["fives"]["most"]]]),
            dict(type="p", text=f"Fives halve the counters on the board and cut the moves by about a third, at the price of twice as many (smaller) exchanges. The program checked {d['boardcheck'][0]:,} additions and {d['boardcheck'][1]:,} subtractions, with borrowing, on both boards."),
            dict(type="diagram", name="invariant", diagram=invariant(d)),
            dict(type="p", text=f"On the board with fives the count is also fixed: {d['inv_f'][0]:,} exchanges either way. Each column's exchanges are forced by what lands in it, so their order cannot change their number."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Settle the carries last", toc="Full circle", blocks=[
            dict(type="p", text="A board lets you pile counters up and settle once at the end; nothing breaks while a column is overfull. Fast hardware multipliers do the same. They add many rows of bits at once and keep the carries unsettled, as a second row of numbers, until a single final addition: the carry-save idea."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"C. S. Wallace's 1964 design for a fast multiplier generated \"the product of two numbers using purely combinational logic, i.e., in one gating step\". The program shows why delaying is safe: adding {inv['n']:,} numbers, settling after each one and settling once at the end make exactly the same **{inv['lazy']:,}** exchanges. Only the waiting changes."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Put 3,746 on a board with fives. How many counters?", "Thousands 3 ones; hundreds 1 five + 2 ones; tens 4 ones; ones 1 five + 1 one: **12 counters**, against 20 on a plain board."),
            ("On a plain board, a column holds 14 counters. What do you do?", "Take 10 off and put 1 in the next column: 4 stay. That is the carry."),
            (f"Why does the board with fives make more exchanges ({wf[2]['exchanges']}) than the plain board ({wp[2]['exchanges']}) for {d['a']:,} + {d['b']:,}?",
             "Each carry takes two smaller steps: five ones become a five, then two fives become one counter in the next column."),
            ("If you add 1,000 numbers and settle only at the end, do you save exchanges?",
             f"No: {inv['lazy']:,} either way. Every exchange removes exactly 9 counters, so their number is fixed by the counters put down ({inv['down']:,}) and left ({inv['left']}). You save passes, not exchanges."),
            ("Where does the word *calculate* come from?", "From Latin *calculus*, a pebble used as a reckoning counter."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Salamis tablet", text="Marble counting board, c. 300 BCE. Epigraphical Museum, Athens, EM 11515.",
                 draw=C.draw_board, link="https://epigraphicmuseum.gr/en/permanent-exhibition/", link_text="The museum's permanent exhibition",
                 licence="Drawn placeholder."),
            dict(title="Salamis counting table, replica", text="Marble replica made in 1966 by Dorothy M. Briggs. Smithsonian, National Museum of American History.",
                 draw=lambda t, s: C.draw_board(t, s), link="https://www.si.edu/object/nmah_690540", link_text="Smithsonian record",
                 licence="Drawn placeholder. The record is CC0; its photograph can be viewed at the link."),
            dict(title="The Exchequer", text="The *Dialogue concerning the Exchequer*, c. 1179, describes the counting table and its chequered cloth.",
                 draw=C.draw_book, link="https://avalon.law.yale.edu/medieval/excheq.asp", link_text="The text, Avalon Project (Yale Law School)",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx, extra=[
            ("scholar", "A Suggestion for a Fast Multiplier", "C. S. Wallace, IEEE Transactions on Electronic Computers 13 (1964)", "https://scispace.com/papers/a-suggestion-for-a-fast-multiplier-12zf7tphek", "Adding many rows at once and settling the carries at the end"),
        ]),
        C.prove_it_section(ctx, "CountingBoard", d["checks"],
                           f"{d['boardcheck'][0]:,} additions and {d['boardcheck'][1]:,} subtractions with borrowing on plain boards and boards with fives, every settled column in standard form, and the exchange invariant.",
                           ["void settle()"]),
    ]
    return dict(
        title="Counting Boards", date="c. 300 BCE",
        description="Era 1, topic 6 of The Algorithm Evolution Atlas: counting boards and the abacus, with a board you can push counters on and settle, and verified links.",
        lede="On these boards nobody writes a digit. Counters go in columns; adding is pushing more on, then settling full columns into the next. The procedure lives in the hands.",
        fieldnote="Their word calculus is Latin for a small pebble, and the English Exchequer is named after the chequered cloth its officials counted on.",
        card=[("When", "Salamis tablet c. 300 BCE · Roman hand abaci · Exchequer table first mentioned 1110"),
              ("Where", "Greece, Rome, England, China, Japan"),
              ("What hurt", "Written Greek and Roman numerals were poor for calculating"),
              ("The fix", "A place-value machine: push counters, then settle"),
              ("Cost", f"{av['fives']['moved']:.1f} counter moves per 4-digit addition with fives"),
              ("Atlas", "Ch. 7.2 The abacus: an early physical algorithm machine")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `CountingBoard.java`. The boards are drawn for this book.",
    )
