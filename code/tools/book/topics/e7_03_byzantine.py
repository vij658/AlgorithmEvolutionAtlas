"""Era 7, topic 3: the Byzantine generals. Every number is parsed from ByzantineGenerals.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("three: "):
            m = re.search(r"lieutenant 1 hears (\w+) from the commander and (\w+) from lieutenant 2", ln)
            d["three"] = dict(fromc=m.group(1), from2=m.group(2))
        elif m := re.match(r"om: [^;]* ; [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"n=(\d+), m=(\d+) \(([\w ]+)\): ([\d,]+) runs, (n >= 3m\+1|n = 3m), ([\d,]+) broke IC1 or IC2", part)
                rows.append(dict(n=int(mm.group(1)), m=int(mm.group(2)), how=mm.group(3), runs=mm.group(4), cond=mm.group(5), broke=mm.group(6)))
            d["om"] = rows
        elif m := re.match(r"messages: [^;]* ; (.*?) ; OM's count", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"m=(\d+), n=(\d+): OM ([\d,]+) messages, SM ([\d,]+)", part)
                rows.append(dict(m=mm.group(1), n=mm.group(2), om=mm.group(3), sm=mm.group(4)))
            d["msgs"] = rows
        elif m := re.match(r"sm: [^;]* ; (.*?) ; with signatures", ln):
            rows, ctrl = [], None
            for part in m.group(1).split(" ; "):
                if mm := re.match(r"control, n=3, m=1 but lieutenants never pass orders on: ([\d,]+) runs, ([\d,]+) failures", part):
                    ctrl = dict(runs=mm.group(1), fail=mm.group(2))
                else:
                    mm = re.match(r"n=(\d+), m=(\d+): ([\d,]+) runs, (\d+) failures", part)
                    rows.append(dict(n=mm.group(1), m=mm.group(2), runs=mm.group(3), fail=mm.group(4)))
            d["sm"] = dict(rows=rows, ctrl=ctrl)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def three_svg(d):
    """The two situations lieutenant 1 cannot tell apart."""
    th = d["three"]

    def draw(t, standalone):
        o = []
        W, H = 780, 330
        o.append(C.text(20, 26, "Three generals, one traitor: lieutenant 1 sees the same thing in both situations", t["ink"], 13, "start", 700))

        def panel(x0, title, cmd_traitor):
            o.append(C.text(x0 + 170, 54, title, t["ink"], 13, "middle", 700))
            pc, p1, p2 = (x0 + 170, 100), (x0 + 60, 240), (x0 + 280, 240)

            def gen(p, name, traitor):
                o.append(C.circle(*p, 22, t["ink"] if traitor else t["surface"], t["ink"], 2))
                o.append(C.text(p[0], p[1] + 5, name, t["paper"] if traitor else t["ink"], 13, "middle", 700))
                if traitor:
                    if name == "C":
                        o.append(C.text(p[0] + 30, p[1] - 14, "traitor", t["red"], 12, "start", 700))
                    else:
                        o.append(C.text(p[0], p[1] + 40, "traitor", t["red"], 12, "middle", 700))

            def arrow(a, b, label, col, lx, ly, anchor="middle"):
                ux, uy = b[0] - a[0], b[1] - a[1]
                L = (ux * ux + uy * uy) ** 0.5
                ux, uy = ux / L, uy / L
                sx, sy, ex, ey = a[0] + ux * 26, a[1] + uy * 26, b[0] - ux * 26, b[1] - uy * 26
                o.append(C.line(sx, sy, ex, ey, col, 2))
                o.append(C.path(f"M{ex:.1f},{ey:.1f} L{ex - ux * 10 - uy * 5:.1f},{ey - uy * 10 + ux * 5:.1f} L{ex - ux * 10 + uy * 5:.1f},{ey - uy * 10 - ux * 5:.1f} Z", None, col))
                o.append(C.text(lx, ly, label, col, 12, anchor, 700))
            gen(pc, "C", cmd_traitor)
            gen(p1, "L1", False)
            gen(p2, "L2", not cmd_traitor)
            arrow(pc, p1, f"\"{th['fromc']}\"", t["red"], x0 + 90, 160, "end")
            arrow(pc, p2, "\"ATTACK\"" if not cmd_traitor else "\"RETREAT\"", t["blue"] if cmd_traitor else t["red"], x0 + 250, 160, "start")
            arrow(p2, p1, f"\"he said {th['from2']}\"", t["blue"], x0 + 170, 228)
        panel(20, "A: the commander is loyal", False)
        panel(410, "B: the commander is a traitor", True)
        o.append(C.line(390, 50, 390, 280, t["axis"], 1.2))
        o.append(C.text(20, H - 28, f"In both, L1 hears {th['fromc']} from the commander and \"he said {th['from2']}\" from L2. In A it must attack (it must obey a loyal commander),", t["muted"], 12))
        o.append(C.text(20, H - 10, "so it attacks in B too; by the same reasoning L2 must retreat in B, and the two loyal lieutenants disagree.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Two situations that look the same to lieutenant 1", t, standalone, 0.55, 780)
    return draw


BZ_HTML = """
<div class="board bz-board">
  <div style="min-width:0">
    <div class="bz-view" id="bz-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls">
      <label>Generals <select id="bz-n"><option value="3">3</option><option value="4" selected>4</option></select></label>
      <label>Traitor <select id="bz-t"></select></label>
      <label>Order <select id="bz-v"><option value="1">ATTACK</option><option value="0">RETREAT</option></select></label>
    </div>
    <div class="bz-lies" id="bz-lies"></div>
    <div class="bz-btns"><button type="button" id="bz-all">Try every lie</button></div>
    <div class="bz-stats" id="bz-stats"></div>
    <p class="say" id="bz-say" aria-live="polite"></p>
  </div>
</div>
"""

BZ_CSS = """
.bz-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.bz-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:3px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.bz-lies{display:grid;gap:4px;margin:8px 0}
.bz-lies button{font-weight:400;font-size:12.5px;padding:3px 8px;border-width:1px;text-align:left}
.bz-lies button.a{border-color:var(--red);color:var(--red)} .bz-lies button.r{border-color:var(--blue);color:var(--blue)}
.bz-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.bz-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

BZ_JS = r"""
(() => {
  const view = document.getElementById("bz-view");
  if (!view) return;
  const PROG = __PROG__;
  const nSel = document.getElementById("bz-n"), tSel = document.getElementById("bz-t"), vSel = document.getElementById("bz-v");
  let lies = [];                         // the traitor's messages, in the order the algorithm sends them: 1 = ATTACK
  // OM(m), exactly as the program runs it: traitors' messages are read from `src` in the order they are sent
  function run(n, traitor, v, src) {
    let used = 0; const log = [];
    function om(m, cmd, lts, val, path) {
      const rec = new Array(n).fill(0);
      lts.forEach(l => {
        const lie = traitor === cmd, x = lie ? src(used++) : val;
        rec[l] = x; log.push({from: cmd, to: l, val: x, lie, path});
      });
      const dec = new Array(n).fill(0);
      if (m === 0) { lts.forEach(l => dec[l] = rec[l]); return dec; }
      const rel = Array.from({length: n}, () => new Array(n).fill(0));
      lts.forEach(i => { const others = lts.filter(x => x !== i), sub = om(m - 1, i, others, rec[i], path.concat([cmd])); others.forEach(j => rel[j][i] = sub[j]); });
      lts.forEach(j => { let att = rec[j], tot = 1; lts.forEach(i => { if (i !== j) { att += rel[j][i]; tot++; } }); dec[j] = 2 * att > tot ? 1 : 0; });
      return dec;
    }
    const lts = Array.from({length: n - 1}, (_, i) => i + 1);
    const dec = om(1, 0, lts, v, []);
    let ok = true, first = -1;
    lts.forEach(l => { if (l === traitor) return; if (first < 0) first = dec[l]; if (dec[l] !== first) ok = false; if (traitor !== 0 && dec[l] !== v) ok = false; });
    return {dec, ok, log, used};
  }
  const NAME = i => i === 0 ? "C" : "L" + i, WORD = x => x ? "ATTACK" : "RETREAT";
  function setup() {
    const n = +nSel.value, keep = tSel.value;
    tSel.innerHTML = "";
    ["none"].concat(Array.from({length: n}, (_, i) => NAME(i))).forEach((s, i) => { const o = document.createElement("option"); o.value = i - 1; o.textContent = s === "none" ? "none" : (s === "C" ? "C (the commander)" : s); tSel.appendChild(o); });
    tSel.value = [...tSel.options].some(o => o.value === keep) ? keep : (n === 3 ? "2" : "3");
    const t = +tSel.value, probe = run(n, t, +vSel.value, () => 0);
    lies = new Array(probe.used).fill(0).map((_, k) => k % 2);
    draw();
  }
  function draw(extra) {
    const n = +nSel.value, t = +tSel.value, v = +vSel.value;
    const r = run(n, t, v, k => lies[k]);
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 420 330"}, view);
    const pos = n === 4 ? [[210, 45], [80, 185], [210, 245], [340, 185]] : [[210, 45], [110, 215], [310, 215]];
    // every message as an arrow; the two directions between two lieutenants bow to opposite sides
    r.log.forEach(msg => {
      const a = pos[msg.from], b = pos[msg.to], col = msg.val ? "var(--red)" : "var(--blue)";
      const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, px = -uy, py = ux;
      const bow = msg.from === 0 ? 0 : 16, cx = (a[0] + b[0]) / 2 + px * bow, cy = (a[1] + b[1]) / 2 + py * bow;
      const sx = a[0] + ux * 24 + px * bow * 0.4, sy = a[1] + uy * 24 + py * bow * 0.4;
      const ex = b[0] - ux * 26 + px * bow * 0.4, ey = b[1] - uy * 26 + py * bow * 0.4;
      sv("path", {d: `M${sx},${sy} Q${cx},${cy} ${ex},${ey}`, fill: "none", stroke: col, "stroke-width": msg.lie ? 3 : 1.8, "stroke-dasharray": msg.lie ? "6 4" : ""}, svg);
      const tx = ex - cx, ty = ey - cy, tl = Math.hypot(tx, ty), vx = tx / tl, vy = ty / tl;
      sv("path", {d: `M${ex},${ey} L${ex - vx * 10 - vy * 5},${ey - vy * 10 + vx * 5} L${ex - vx * 10 + vy * 5},${ey - vy * 10 - vx * 5} Z`, fill: col}, svg);
    });
    pos.forEach((p, i) => {
      const traitor = i === t;
      sv("circle", {cx: p[0], cy: p[1], r: 22, fill: traitor ? "var(--ink)" : "var(--surface)", stroke: "var(--ink)", "stroke-width": 2}, svg);
      const tx = sv("text", {x: p[0], y: p[1] + 5, "text-anchor": "middle", "font-size": 14, "font-weight": 700, fill: traitor ? "var(--paper)" : "var(--ink)"}, svg); tx.textContent = NAME(i);
      if (i > 0 && !traitor) { const dx = sv("text", {x: p[0], y: p[1] + 46, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: r.dec[i] ? "var(--red)" : "var(--blue)"}, svg); dx.textContent = "decides " + WORD(r.dec[i]); }
      if (traitor) { const dx = sv("text", {x: p[0], y: p[1] + 46, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: "var(--ink)"}, svg); dx.textContent = "traitor"; }
    });
    const key = sv("text", {x: 10, y: 322, "font-size": 12, fill: "var(--muted)"}, svg); key.textContent = "red: ATTACK · blue: RETREAT · dashed: a lie";
    // the traitor's choices
    const box = document.getElementById("bz-lies"); box.innerHTML = "";
    if (t >= 0) {
      el("div", {style: "font-size:12.5px;color:var(--muted)"}, box, "The traitor's messages (click to change what it says):");
      r.log.filter(m => m.lie).forEach((m, k) => {
        const what = m.path.length === 0 ? `${NAME(m.from)} → ${NAME(m.to)}: "${WORD(m.val)}"` : `${NAME(m.from)} → ${NAME(m.to)}: "the commander said ${WORD(m.val)}"`;
        const b = el("button", {type: "button", class: m.val ? "a" : "r"}, box, what);
        b.addEventListener("click", () => { lies[k] = 1 - lies[k]; draw(); });
      });
    }
    const st = document.getElementById("bz-stats"); st.innerHTML = "";
    el("div", {}, st, `messages sent: ${r.log.length}`);
    el("div", {}, st, `loyal lieutenants ${r.ok ? "agree" + (t !== 0 ? " and obey" : "") : "FAIL: " + (t !== 0 ? "they disagree or disobey" : "they disagree")}`);
    if (extra) el("div", {}, st, extra);
    document.getElementById("bz-say").textContent = r.ok
      ? `OM(1) with ${n} generals: each lieutenant takes the majority of what it heard from the commander and what the others say they heard.`
      : `Broken: with ${n} generals, this traitor's lies split the loyal lieutenants. That is why ${n === 3 ? "three generals cannot survive one traitor" : "the bound is n ≥ 3m + 1"}.`;
  }
  document.getElementById("bz-all").addEventListener("click", () => {
    const n = +nSel.value; let runs = 0, broke = 0;
    for (let t = 0; t < n; t++) for (let v = 0; v <= 1; v++) {
      const k = run(n, t, v, () => 0).used;
      for (let mask = 0; mask < (1 << k); mask++) { runs++; if (!run(n, t, v, b => (mask >> b) & 1).ok) broke++; }
    }
    const p = PROG[n];
    draw(`every traitor, both orders, every lie: ${runs} runs, ${broke} broke IC1 or IC2 (the program: ${p.runs} runs, ${p.broke} broke)`);
  });
  nSel.addEventListener("change", setup); tSel.addEventListener("change", setup); vSel.addEventListener("change", () => draw());
  setup();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Byzantine agreement combined older ideas, and where it led")
    W = 210
    nodes = {
        "two": (20, 20, "Two generals", "agree to attack over an unreliable link", "the \"Chinese generals\" problem", "ink"),
        "sift": (395, 20, "SIFT at SRI", "a fault-tolerant computer that votes among copies", "", "ink"),
        "sig": (770, 20, "Digital signatures", "messages that cannot be forged", "Era 6, topic 10", "ink"),
        "bz": (395, 180, "Byzantine agreement", "⊕ a faulty part may lie to anyone", "Pease, Shostak, Lamport, 1980", "red"),
        "story": (20, 340, "The story", "⊕ generals around a city: a name that stuck", "Lamport, Shostak, Pease, 1982", "ink"),
        "sm": (770, 340, "Signed messages", "⊕ SM(m): any number of generals", "Lamport's part of the 1980 work", "ink"),
        "today": (395, 490, "Today", "\"in a system with 3f + 1 generals, no more than f may be malicious\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("two", "bz", ports=("bottom", "top:0.15"))
    D.edge("sift", "bz", ports=("bottom", "top"))
    D.edge("sig", "sm", ports=("bottom", "top"))
    D.edge("bz", "story", ports=("bottom:0.15", "top"))
    D.edge("bz", "sm", ports=("bottom:0.85", "top"))
    D.edge("bz", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: as Kleppmann's Cambridge lecture notes state the theorem. Who did what comes from Lamport's own note on the 1980 paper.", "caption")
    return D


def chain(d):
    om, msgs, sm = d["om"], d["msgs"], d["sm"]
    o3 = next(r for r in om if r["n"] == 3)
    ok = [r for r in om if r["cond"] != "n = 3m"]
    total_ok = sum(int(r["runs"].replace(",", "")) for r in ok)
    big = msgs[-1]
    steps = [
        ("A faulty part can tell different parts different things, and simple voting is fooled",
         f"OM(m): relay what you heard and take the majority; with n ≥ 3m + 1, none of {total_ok:,} runs failed", "Pease, Shostak and Lamport, 1980"),
        (f"Three generals cannot survive one traitor: {o3['broke']} of {o3['runs']} possible lies break OM(1)",
         "Signed messages, SM(m): a traitor cannot forge a loyal general's signature, so any number of generals suffices", "Lamport's signed-message solution"),
        (f"OM(m)'s messages multiply: {big['om']} for m = {big['m']}",
         f"SM passes each order on once: {big['sm']} messages for the same {big['n']} generals", "the 1982 paper"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from lying parts to a bound, and around it")
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
    om, msgs, sm = d["om"], d["msgs"], d["sm"]
    o3 = next(r for r in om if r["n"] == 3)
    o4 = next(r for r in om if r["n"] == 4)
    big = msgs[-1]
    om_rows = [[str(r["n"]), str(r["m"]), r["cond"].replace(">=", "≥").replace("3m+1", "3m + 1"), r["how"], r["runs"], r["broke"]] for r in om]
    om_hl = [i for i, r in enumerate(om) if r["cond"] == "n = 3m"]
    msg_rows = [[r["m"], r["n"], r["om"], r["sm"]] for r in msgs]
    sm_rows = [[r["n"], r["m"], r["runs"], r["fail"]] for r in sm["rows"]]
    prog = {3: dict(runs=o3["runs"], broke=o3["broke"]), 4: dict(runs=o4["runs"], broke=o4["broke"])}
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Fault-tolerant computers voted among copies of a computation, assuming a broken copy would simply give a wrong answer. Engineers at SRI saw that a broken part might give different answers to different voters. Pease, Shostak and Lamport worked out exactly how many parts are needed to survive that, and Lamport later told it as a story about generals. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Byzantine agreement. Blue: how it is taught today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Be the traitor", toc="Try it", blocks=[
            dict(type="p", text="OM(1), exactly as the program runs it. The commander C sends an order to each lieutenant; each lieutenant then tells the others what it heard; each loyal lieutenant takes the majority (RETREAT on a tie). Choose a traitor and make it lie by clicking its messages. With four generals the loyal lieutenants always agree, and obey a loyal commander. With three, find the lies that split them. Then press \"Try every lie\": the widget runs every traitor, both orders and every combination of lies, and counts the failures, as the program does."),
            dict(type="widget", html=BZ_HTML, js=BZ_JS.replace("__PROG__", __import__("json").dumps(prog)), css=BZ_CSS,
                 fallback=dict(type="table", head=["Generals", "Traitors", "Condition", "Lies tried", "Runs", "Broke IC1 or IC2"], num=[0, 1, 4, 5], rows=om_rows, hl=om_hl),
                 note="In the interactive edition you can play the traitor and try every lie."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Relay, then vote", toc="How it works", blocks=[
            dict(type="p", text="**The problem.** A commander sends ATTACK or RETREAT to n − 1 lieutenants. Up to m of the n generals, possibly the commander, are traitors who may say anything to anyone. IC1: all loyal lieutenants decide the same. IC2: if the commander is loyal, they decide what he ordered."),
            dict(type="p", text="**Why three are not enough.** Lieutenant 1 cannot tell these two situations apart:"),
            dict(type="svg", name="three", draw=three_svg(d), alt="Two situations that look the same to lieutenant 1", width=780),
            dict(type="p", text="**OM(m).** The commander sends his order. Each lieutenant then acts as commander in OM(m − 1), passing on what it heard to the others, and finally takes the majority of the value it heard directly and the values the others report. With n ≥ 3m + 1 the loyal majority always outweighs the lies; the price is messages: (n − 1) + (n − 1)(n − 2) + … + (n − 1)(n − 2)…(n − m − 1)."),
            dict(type="p", text="**SM(m), with signatures.** The commander signs his order. A lieutenant who receives an order with a valid chain of signatures adds it to its set and, if fewer than m lieutenants have signed, signs it and passes it on. At the end it obeys if it received exactly one order, and retreats otherwise. A traitor can sign anything with its own key, but cannot forge a loyal general's signature, so a traitorous commander who sends two orders is exposed: every loyal lieutenant ends with the same set."),
            dict(type="callout", kind="key", label="Key idea",
                 text="When a part can lie, two out of three is not a majority you can trust: you need more than two thirds honest. Unforgeable signatures change the arithmetic, because a lie about what someone else said can be caught."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Every lie a traitor can tell", toc="Measured", blocks=[
            dict(type="p", text="**OM(m).** Traitors placed in every possible way, both orders, and the traitors' messages chosen by an adversary: every combination when there are few enough, otherwise many random ones. Failures appear exactly when n = 3m:"),
            dict(type="table", head=["Generals n", "Traitors m", "Condition", "Lies tried", "Runs", "Broke IC1 or IC2"], num=[0, 1, 4, 5], rows=om_rows, hl=om_hl),
            dict(type="p", text="**Messages,** with no traitors present, when n = 3m + 1. OM's count grows like n to the power m; SM sends each order on once, (n − 1)² in all:"),
            dict(type="table", head=["m", "n", "OM messages", "SM messages"], num=[0, 1, 2, 3], rows=msg_rows, hl=[len(msg_rows) - 1]),
            dict(type="p", text=f"**SM(m).** Traitors may sign anything with their own keys and send it to anyone in any round, or not at all, but cannot forge a loyal signature. No failures, even with three generals and one traitor. As a control, the same traitors against lieutenants who never pass orders on: {sm['ctrl']['fail']} failures in {sm['ctrl']['runs']} runs, so the adversary is strong enough to break a weaker rule."),
            dict(type="table", head=["Generals n", "Traitors m", "Runs", "Failures"], num=[0, 1, 2, 3], rows=sm_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A problem renamed on purpose", toc="The evidence", blocks=[
            dict(type="p", text="Lamport, Shostak and Pease, \"The Byzantine Generals Problem\" (SRI International; *ACM Transactions on Programming Languages and Systems* 4(3): 382–401, July 1982): \"Reliable computer systems must handle malfunctioning components that give conflicting information\"; \"no solution with fewer than 3m + 1 generals can cope with m traitors\"; OM(m) and SM(m) \"involve sending up to (n - 1)(n - 2) ... (n - m - 1) messages\". The abstract states that with oral messages the problem \"is solvable if and only if more than two-thirds of the generals are loyal\", and that \"With unforgeable written messages, the problem is solvable for any number of generals and possible traitors\"."),
            dict(type="p", text="Lamport's own note explains the name: \"the best way to attract attention to a problem is to present it in terms of a story\"; \"the original title of this paper was The Albanian Generals Problem\", until Jack Goldberg pointed out \"that there were Albanians in the world outside Albania\"; \"The obviously more appropriate Byzantine generals then occurred to me.\" \"The main reason for writing this paper was to assign the new name to the problem.\""),
            dict(type="p", text="On the 1980 paper, \"Reaching Agreement in the Presence of Faults\" (*Journal of the ACM*), which won the 2005 Dijkstra Prize, Lamport writes that the problem was posed by people working on SIFT at SRI before he arrived; Shostak found the 4-processor solution and the impossibility result, Pease the general 3n + 1 solution, and Lamport the signed-message solution. He adds that a former Boeing engineer told him in 1997 that Boeing's commercial-aircraft designers knew of the work by 1986."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Logical clocks, then lying clocks", toc="Full circle", blocks=[
            dict(type="p", text="Era 6 ended with Lamport's logical clocks: separate computers agreeing on an order of events, assuming each one follows the rules. Here the same author asks what happens when some of them do not. The answer has the same flavour: agreement is possible, but only within limits that can be proved, and only by sending more messages."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Three generals and one traitor: impossible with spoken messages ({o3['broke']} of {o3['runs']} possible lies succeed), possible with signatures. A tool from Era 6's public-key cryptography rescues a problem from distributed computing."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many generals are needed to survive 2 traitors with spoken messages?", "7, since n ≥ 3m + 1 = 7."),
            ("In OM(1) with 4 generals, a traitorous lieutenant lies to everyone. Why do the loyal lieutenants still obey a loyal commander?", "Each hears the true order from the commander and from the other loyal lieutenant: two votes against one lie."),
            ("Why does a tie go to RETREAT?", "Any fixed default works, as long as every loyal lieutenant uses the same one; RETREAT is the safe choice for an army."),
            ("How many messages does OM(2) send with 7 generals?", f"6 + 6 × 5 + 6 × 5 × 4 = 156, as the program counted ({next(r for r in msgs if r['m'] == '2')['om']})."),
            ("What can a traitorous commander do in SM(m), and what happens?", "Sign two different orders and send them to different lieutenants; the loyal ones pass both on, all end with both, and all retreat."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Byzantine Generals Problem (1982)", text="*ACM TOPLAS* 4(3): 382–401, by Lamport, Shostak and Pease of SRI International.",
                 draw=C.draw_manuscript, link="https://people.cs.umass.edu/~arun/cs677/reading/LSP.pdf", link_text="The paper (PDF, on a UMass course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ByzantineGenerals", d["checks"],
                           "OM(m) against every possible traitor placement and adversarial lies (every combination for small cases, random ones for larger), the message counts against the formula, SM(m) against traitors who sign anything they can, and a control showing those traitors break a weaker rule.",
                           ["static int[] om(int m, int commander, int[] lieutenants, int v, int n)"]),
    ]
    return dict(
        title="The Byzantine Generals", date="1980–1982",
        description="Era 7, topic 3 of The Algorithm Evolution Atlas: agreement when some parts lie, the 3m + 1 bound, the OM and SM algorithms, and how the problem got its name.",
        lede="A broken computer that stops is easy to spot. One that keeps running and tells different parts of a system different things is not. Pease, Shostak and Lamport found exactly how many parts it takes to agree anyway.",
        fieldnote=f"I played the traitor among three generals, and {o3['broke']} of my {o3['runs']} possible lies split the loyal ones. Among four, none of my lies worked. With signatures, even three were enough. This species named the problem after an empire known for its intrigues, and the name stuck.",
        card=[("When", "1980 (the proof); 1982 (the story)"),
              ("Where", "SRI International"),
              ("What hurt", "Parts that send conflicting information"),
              ("The fix", "n ≥ 3m + 1 with OM(m); any n with signatures"),
              ("Checked", f"{o3['broke']} of {o3['runs']} lies break 3 generals; 0 of {o4['runs']} break 4")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ByzantineGenerals.java`.",
    )
