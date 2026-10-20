"""Era 7, topic 10: TCP congestion control. Every number is parsed from TcpCongestion.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def _rows(s):
    rows = []
    for part in s.split(" ; "):
        mm = re.match(r"(\d+) senders?: useful ([\d.]+), link busy ([\d.]+), duplicates ([\d.]+), dropped ([\d.]+)%, fairness ([\d.]+)", part)
        rows.append(dict(n=mm.group(1), useful=mm.group(2), busy=mm.group(3), dup=mm.group(4), drop=mm.group(5), fair=mm.group(6)))
    return rows


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"network: .*? a (\d+)-packet buffer, a round trip of (\d+) ticks without queueing ; ([\d,]+) ticks measured after ([\d,]+) to settle", ln):
            d["net"] = dict(buf=m.group(1), rtt=m.group(2), ticks=m.group(3), warm=m.group(4))
        elif m := re.match(r"fixed: [^;]* ; (.*)$", ln):
            d["fixed"] = _rows(m.group(1))
        elif m := re.match(r"jacobson: [^;]* ; (.*)$", ln):
            d["jac"] = _rows(m.group(1))
        elif m := re.match(r"chiujain: .*? starting at rates ([\d.]+) and ([\d.]+) ; .*? averages over the last (\d+) of ([\d,]+) steps, [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(5).split(" ; "):
                mm = re.match(r"(\w+): fairness ([\d.]+), total use ([\d.]+), ending at \(([\d.]+), ([\d.]+)\)", part)
                rows.append(dict(pol=mm.group(1), fair=mm.group(2), use=mm.group(3), x1=mm.group(4), x2=mm.group(5)))
            d["cj"] = dict(x1=m.group(1), x2=m.group(2), last=m.group(3), steps=m.group(4), rows=rows)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def sawtooth_svg(d):
    """A schematic of one sender's congestion window under Jacobson's rules."""
    def draw(t, standalone):
        o = []
        W, H = 760, 300
        x0, x1, y0, y1 = 70, 720, 240, 50
        o.append(C.text(20, 26, "One sender's window under Jacobson's rules (a schematic, not measured)", t["ink"], 13, "start", 700))
        o.append(C.line(x0, y0, x1, y0, t["axis"], 1.2))
        o.append(C.line(x0, y0, x0, y1, t["axis"], 1.2))
        o.append(C.text(x0 - 10, y1 + 4, "window", t["muted"], 12, "end"))
        o.append(C.text(x1, y0 + 20, "round trips →", t["muted"], 12, "end"))
        # slow start: doubling each round trip up to 32, then a loss: threshold 16, window 1, slow start to 16, linear growth
        pts, w, ss, x = [], 1.0, 64.0, 0
        seq = []
        for _ in range(6):
            seq.append(w); w *= 2
        seq.append(64)          # loss at 64
        lossx = len(seq) - 1
        w, ss = 1.0, 32.0
        while w < ss:
            seq.append(w); w *= 2
        while w < 44:
            seq.append(w); w += 1
        loss2 = len(seq) - 1
        w, ss = 1.0, 22.0
        while w < ss:
            seq.append(w); w *= 2
        while len(seq) < 52:
            seq.append(w); w += 1
        X = lambda i: x0 + i * (x1 - x0) / (len(seq) - 1)
        Y = lambda v: y0 - v / 70 * (y0 - y1)
        o.append(C.path(" ".join(f"{'M' if i == 0 else 'L'}{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(seq)), t["red"], "none", 2.2))
        for lx in (lossx, loss2):
            o.append(C.circle(X(lx), Y(seq[lx]), 5, t["ink"]))
            o.append(C.text(X(lx) + 8, Y(seq[lx]) - 8, "loss: threshold = half, window = 1", t["ink"], 11.5, "start", 700))
        o.append(C.text(X(2), Y(20), "slow start: doubles", t["blue"], 12, "start", 700))
        o.append(C.text(X(14), Y(18), "congestion avoidance: +1 per round trip", t["blue"], 12, "start", 700))
        return C.svg_doc(W, H, "".join(o), "A schematic congestion window sawtooth", t, standalone, 0.55, 760)
    return draw


CJ_HTML = """
<div class="board cj-board">
  <div style="min-width:0">
    <div class="cj-view" id="cj-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls"><label>Rule <select id="cj-pol"><option>AIMD</option><option>AIAD</option><option>MIMD</option><option>MIAD</option></select></label></div>
    <div class="cj-btns"><button type="button" class="primary" id="cj-step">20 steps</button><button type="button" id="cj-run">2,000 steps</button><button type="button" id="cj-reset">Start again</button></div>
    <div class="cj-stats" id="cj-stats"></div>
    <p class="say" id="cj-say" aria-live="polite"></p>
  </div>
</div>
"""

CJ_CSS = """
.cj-view svg{display:block;width:100%;height:auto;background:var(--wash);cursor:crosshair}
.cj-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.cj-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
.cj-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:3px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
"""

CJ_JS = r"""
(() => {
  const view = document.getElementById("cj-view");
  if (!view) return;
  const PROG = __PROG__, X1 = __X1__, X2 = __X2__;
  let s1 = X1, s2 = X2, x1, x2, k, path, sumF, sumE, cnt, fromProg;
  // exactly the program's rules, in the same order
  function step(pol) {
    const over = x1 + x2 > 1;
    if (pol === "AIMD") { if (over) { x1 *= 0.5; x2 *= 0.5; } else { x1 += 0.01; x2 += 0.01; } }
    else if (pol === "AIAD") { if (over) { x1 = Math.max(0, x1 - 0.02); x2 = Math.max(0, x2 - 0.02); } else { x1 += 0.01; x2 += 0.01; } }
    else if (pol === "MIMD") { if (over) { x1 *= 0.5; x2 *= 0.5; } else { x1 *= 1.05; x2 *= 1.05; } }
    else { if (over) { x1 = Math.max(0, x1 - 0.02); x2 = Math.max(0, x2 - 0.02); } else { x1 *= 1.05; x2 *= 1.05; } }
    if (k >= 2000 - 200) { sumF += (x1 + x2) * (x1 + x2) / (2 * (x1 * x1 + x2 * x2)); sumE += x1 + x2; cnt++; }
    k++; path.push([x1, x2]);
  }
  function reset() { x1 = s1; x2 = s2; k = 0; path = [[x1, x2]]; sumF = 0; sumE = 0; cnt = 0; fromProg = s1 === X1 && s2 === X2; draw("Two senders share a link of capacity 1. Each step both learn only whether together they were over or under 1, and adjust by the rule. Click in the square to start elsewhere."); }
  function draw(msg) {
    view.innerHTML = "";
    const S = 380, pad = 30, svg = sv("svg", {viewBox: `0 0 ${S + pad + 10} ${S + pad + 10}`}, view);
    const X = v => pad + v / 1.2 * S, Y = v => S - v / 1.2 * S + 10;
    svg.addEventListener("click", ev => {
      const r = svg.getBoundingClientRect(), sx = (ev.clientX - r.left) / r.width * (S + pad + 10), sy = (ev.clientY - r.top) / r.height * (S + pad + 10);
      s1 = Math.max(0, Math.min(1.1, (sx - pad) / S * 1.2)); s2 = Math.max(0, Math.min(1.1, (S + 10 - sy) / S * 1.2)); reset();
    });
    sv("line", {x1: X(0), y1: Y(0), x2: X(1.2), y2: Y(0), stroke: "var(--axis)"}, svg); sv("line", {x1: X(0), y1: Y(0), x2: X(0), y2: Y(1.2), stroke: "var(--axis)"}, svg);
    sv("line", {x1: X(0), y1: Y(1), x2: X(1), y2: Y(0), stroke: "var(--ink)", "stroke-width": 1.5}, svg);
    sv("line", {x1: X(0), y1: Y(0), x2: X(1.2), y2: Y(1.2), stroke: "var(--blue)", "stroke-width": 1.5, "stroke-dasharray": "6 4"}, svg);
    const t1 = sv("text", {x: X(0.08), y: Y(1.02), "font-size": 12, fill: "var(--ink)"}, svg); t1.textContent = "full use: x₁ + x₂ = 1";
    const t2 = sv("text", {x: X(0.9), y: Y(0.8), "font-size": 12, fill: "var(--blue)"}, svg); t2.textContent = "equal shares";
    const t3 = sv("text", {x: X(1.18), y: Y(0) + 22, "font-size": 12, fill: "var(--muted)", "text-anchor": "end"}, svg); t3.textContent = "sender 1's rate x₁";
    const t4 = sv("text", {x: X(0) + 6, y: Y(1.18), "font-size": 12, fill: "var(--muted)"}, svg); t4.textContent = "sender 2's rate x₂";
    const shown = path;
    sv("path", {d: shown.map((p, i) => `${i ? "L" : "M"}${X(p[0])},${Y(p[1])}`).join(" "), fill: "none", stroke: "var(--red)", "stroke-width": 1.4}, svg);
    sv("circle", {cx: X(path[0][0]), cy: Y(path[0][1]), r: 5, fill: "var(--ink)"}, svg);
    sv("circle", {cx: X(x1), cy: Y(x2), r: 6, fill: "var(--red)"}, svg);
    const st = document.getElementById("cj-stats"); st.innerHTML = "";
    el("div", {}, st, `step ${k}: x₁ = ${x1.toFixed(3)}, x₂ = ${x2.toFixed(3)}`);
    const f = (x1 + x2) ** 2 / (2 * (x1 * x1 + x2 * x2) || 1);
    el("div", {}, st, `fairness now: ${f.toFixed(3)} (1 = equal)`);
    if (cnt === 200) {
      el("div", {}, st, `last 200 of 2,000 steps: fairness ${(sumF / cnt).toFixed(3)}, total use ${(sumE / cnt).toFixed(3)}`);
      const p = PROG.find(r => r.pol === document.getElementById("cj-pol").value);
      if (fromProg && p) el("div", {}, st, `the program: fairness ${p.fair}, total use ${p.use}, ending at (${p.x1}, ${p.x2})`);
    }
    if (msg) document.getElementById("cj-say").textContent = msg;
  }
  document.getElementById("cj-step").addEventListener("click", () => { const pol = document.getElementById("cj-pol").value; for (let i = 0; i < 20 && k < 2000; i++) step(pol); draw(); });
  document.getElementById("cj-run").addEventListener("click", () => {
    const pol = document.getElementById("cj-pol").value; while (k < 2000) step(pol);
    const m = {AIMD: "AIMD zig-zags towards the crossing of the two lines: full use and equal shares, from any start.", AIAD: "AIAD moves parallel to the equal-shares line: the difference between the senders never changes.", MIMD: "MIMD moves along a line through the origin: the ratio between the senders never changes.", MIAD: "MIAD drifts away from fairness: the bigger sender ends with almost everything."}[pol];
    draw(m);
  });
  document.getElementById("cj-reset").addEventListener("click", () => { s1 = X1; s2 = X2; reset(); });
  document.getElementById("cj-pol").addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How TCP congestion control combined older ideas, and where it led")
    W = 210
    nodes = {
        "tcp": (20, 20, "TCP's sliding window", "send up to the receiver's window, resend on a timer", "", "ink"),
        "col": (395, 20, "Congestion collapse", "LBL to UC Berkeley: 32 Kbps fell to 40 bps", "October 1986", "ink"),
        "karn": (770, 20, "Karn's backoff", "don't time resent packets; back off the timer", "one of Jacobson's seven", "ink"),
        "vj": (395, 180, "Jacobson's rules", "⊕ loss means congestion: slow start, halve, grow by one", "Jacobson and Karels, 1988", "red"),
        "cj": (770, 340, "Chiu and Jain", "⊕ why AIMD reaches fair shares", "DEC, 1989", "ink"),
        "rfc": (20, 340, "The standard", "four intertwined algorithms, Jacobson's at the core", "RFC 5681, 2009", "ink"),
        "today": (395, 490, "Today", "RFC 5681, updated for fast, long links by CUBIC (RFC 9438)", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("tcp", "vj", ports=("bottom", "top:0.15"))
    D.edge("col", "vj", ports=("bottom", "top"))
    D.edge("karn", "vj", ports=("bottom", "top:0.85"))
    D.edge("vj", "cj", ports=("bottom:0.85", "top"), dashed=True, label="the theory behind it", at=0.5, dx=8, anchor="start")
    D.edge("vj", "rfc", ports=("bottom:0.15", "top"))
    D.edge("rfc", "today", ports=("bottom", "top:0.15"))
    D.text(20, 615, "Today: RFC 5681 lists RFC 9438 (CUBIC) as an update. Dashed: an analysis published a year later by other authors.", "caption")
    return D


def chain(d):
    fx, jc, cj = d["fixed"], d["jac"], d["cj"]
    f32 = next(r for r in fx if r["n"] == "32")
    j32 = next(r for r in jc if r["n"] == "32")
    f64 = next(r for r in fx if r["n"] == "64")
    j64 = next(r for r in jc if r["n"] == "64")
    aimd = next(r for r in cj["rows"] if r["pol"] == "AIMD")
    steps = [
        (f"Senders that ignore congestion: with 32 of them, {f32['drop']}% of packets dropped and {float(f32['dup']) * 100:.0f}% of the link carrying duplicates",
         f"Treat a loss as congestion: start with one packet, double, then add one per round trip, halve on loss: {j32['drop']}% dropped, duplicates {j32['dup']}", "Jacobson and Karels, 1988"),
        ("Timers that ignore how much the round trip varies resend packets still on their way",
         f"Timer = smoothed round trip + 4 × its variation, doubled after each timeout: duplicates {j64['dup']} per tick even with 64 senders", "the same paper"),
        (f"Senders share unequally: fairness {f64['fair']} with 64 uncontrolled senders",
         f"Additive increase, multiplicative decrease: fairness {j64['fair']}; in Chiu and Jain's model AIMD reaches {aimd['fair']}", "Chiu and Jain, 1989"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from collapse to polite sharing")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx_ = (L, R) if i % 2 == 0 else (R, L)
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx_, y, bw, rowh, [("THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="fixed by", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    net, fx, jc, cj = d["net"], d["fixed"], d["jac"], d["cj"]
    rows = []
    for a, b in zip(fx, jc):
        rows.append([a["n"], a["useful"], a["dup"], a["drop"] + "%", a["fair"], b["useful"], b["dup"], b["drop"] + "%", b["fair"]])
    cj_rows = [[r["pol"], r["fair"], r["use"], f"({r['x1']}, {r['x2']})"] for r in cj["rows"]]
    f32 = next(r for r in fx if r["n"] == "32")
    j32 = next(r for r in jc if r["n"] == "32")
    aimd = next(r for r in cj["rows"] if r["pol"] == "AIMD")
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. TCP already sent as much as the receiver allowed and resent anything not acknowledged in time. In October 1986 that brought the early Internet to a standstill. Jacobson and Karels added one idea: a lost packet is a sign that the network is overloaded, so slow down. Chiu and Jain explained a year later why the particular way of slowing down they chose leads to fair shares. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Jacobson's rules. Blue: the standard today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Two senders, one link", toc="Try it", blocks=[
            dict(type="p", text=f"Chiu and Jain's picture. The horizontal axis is sender 1's rate, the vertical sender 2's; the black line is full use of the link, the dashed blue line equal shares. Each step both senders learn only one bit, over or under capacity, and both apply the same rule: increase by adding 0.01 or multiplying by 1.05; decrease by subtracting 0.02 or halving. Starting from ({cj['x1']}, {cj['x2']}), run each rule for 2,000 steps: only additive increase with multiplicative decrease (AIMD) ends at equal shares. The widget repeats the program's arithmetic, so from that start its averages equal the program's. Click anywhere to start elsewhere."),
            dict(type="widget", html=CJ_HTML, js=CJ_JS.replace("__PROG__", json.dumps(cj["rows"])).replace("__X1__", cj["x1"]).replace("__X2__", cj["x2"]), css=CJ_CSS,
                 fallback=dict(type="table", head=["Rule", "Fairness", "Total use", "Ending at"], num=[1, 2], rows=cj_rows, hl=[0]),
                 note="In the interactive edition you can run the four rules from any starting point."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Loss means slow down", toc="How it works", blocks=[
            dict(type="p", text="**Conservation of packets.** In Jacobson's words, \"A new packet isn't put into the network until an old packet leaves.\" Acknowledgements clock the sender: each one that returns makes room for one more packet."),
            dict(type="p", text="**The window.** Keep a congestion window, cwnd: at most that many packets in flight. *Slow start:* begin at one packet and add one for every acknowledgement, which doubles the window every round trip. *Congestion avoidance:* past a threshold, add one packet per round trip. *On a loss:* set the threshold to half the window and start again from one packet. *Fast retransmit:* three duplicate acknowledgements mean a packet was lost, so resend it at once without waiting for the timer."),
            dict(type="svg", name="sawtooth", draw=sawtooth_svg(d), alt="A schematic congestion window sawtooth", width=760),
            dict(type="p", text="**The timer.** Measure the round trip, keep a smoothed average and a smoothed variation, and wait the average plus four times the variation; after each timeout, double the wait. Never time a packet that was resent (Karn), since its acknowledgement may belong to either copy."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A network has no central controller, but every sender can infer congestion from its own losses. If every sender backs off by halving and probes by adding, they share the link fully and fairly without ever talking to each other."),
        ]),
        dict(id="measured", eyebrow="Measured", title="One bottleneck, many senders", toc="Measured", blocks=[
            dict(type="p", text=f"**The simulation.** Senders share one link that carries 1 packet per tick, behind a {net['buf']}-packet buffer; a round trip takes {net['rtt']} ticks when the queue is empty; {net['ticks']} ticks were measured after {net['warm']} to settle. *Useful:* new packets delivered per tick (at most 1). *Duplicates:* copies of packets already delivered, per tick. *Fairness:* Jain's index of the senders' useful rates, 1 when equal. Without congestion control: a fixed window of 32 packets, a timer of twice the smoothed round trip, and everything resent from the oldest unacknowledged packet on a timeout. With Jacobson's rules: slow start, congestion avoidance, fast retransmit and the variance-based timer with backoff."),
            dict(type="table", head=["Senders", "Fixed: useful", "duplicates", "dropped", "fairness", "Jacobson: useful", "duplicates", "dropped", "fairness"], num=[0, 1, 2, 3, 4, 5, 6, 7, 8], rows=rows, hl=[5]),
            dict(type="p", text=f"With 32 senders the uncontrolled ones lost {f32['drop']}% of what they sent and filled {float(f32['dup']) * 100:.0f}% of the link with duplicates; Jacobson's lost {j32['drop']}% and sent almost no duplicates. This small model shows the mechanism, not the thousandfold collapse of 1986: a single link loses no capacity to packets dropped before it."),
            dict(type="p", text=f"**Chiu and Jain's model,** two users starting at ({cj['x1']}, {cj['x2']}), averaged over the last {cj['last']} of {cj['steps']} steps:"),
            dict(type="table", head=["Rule", "Fairness", "Total use", "Ending at"], num=[1, 2], rows=cj_rows, hl=[0]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="From 32 kilobits to 40 bits", toc="The evidence", blocks=[
            dict(type="p", text="Van Jacobson (Lawrence Berkeley Laboratory) and Michael Karels (University of California at Berkeley), \"Congestion Avoidance and Control\" (SIGCOMM '88; revised November 1988): \"In October of '86, the Internet had the first of what became a series of 'congestion collapses'\"; \"the data throughput from LBL to UC Berkeley\" \"dropped from 32 Kbps to 40 bps\". The paper lists seven new algorithms, from \"(i) round-trip-time variance estimation\" and \"(iii) slow-start\" to \"(vi) Karn's clamped retransmit backoff\" and \"(vii) fast retransmit\", and states the rules: \"On any timeout, set cwnd to half the current window size (this is the multiplicative decrease)\"; \"On each ack for new data, increase cwnd by 1/cwnd (this is the additive increase).\""),
            dict(type="p", text="Dah-Ming Chiu and Raj Jain (Digital Equipment Corporation), \"Analysis of the Increase and Decrease Algorithms for Congestion Avoidance in Computer Networks\" (*Computer Networks and ISDN Systems* 17, 1989): \"a simple additive increase and multiplicative decrease algorithm satisfies the sufficient conditions for convergence to an efficient and fair state regardless of the starting state of the network\", shown with \"a trajectory through an n-dimensional vector space\". Byers's seminar notes add that the paper proves sufficiency, not necessity, and assumes synchronous feedback."),
            dict(type="p", text="RFC 5681 (2009), the Internet standard, \"defines TCP's four intertwined congestion control algorithms\" (slow start, congestion avoidance, fast retransmit and fast recovery) and says \"The core algorithms we describe were developed by Van Jacobson\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Agreement without a referee", toc="Full circle", blocks=[
            dict(type="p", text="This era's Byzantine generals (topic 3) agree by exchanging many messages. TCP's senders exchange none at all with each other, yet they converge on sharing a link equally, because each reacts to the same signal, loss, with the same rule."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Two users who learn only \"over\" or \"under\" each step, starting at {cj['x1']} and {cj['x2']}: with AIMD they end at ({aimd['x1']}, {aimd['x2']}), fairness {aimd['fair']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Slow start begins at 1 packet. How large is the window after 5 round trips without loss?", "32 packets: it doubles every round trip."),
            ("Why halve on a loss rather than subtract one?", "Multiplicative decrease shrinks large senders more than small ones, which pulls them towards equal shares; it also backs off fast enough to drain a queue."),
            ("In AIAD, why does the difference between the senders never change?", "Both add or subtract the same amount at every step."),
            ("Why should a resent packet not be used to time the round trip?", "Its acknowledgement could answer the original or the copy, so the measurement could be wildly wrong (Karn's rule)."),
            ("The average round trip is 100 ms and its variation 10 ms. What is the timer?", "100 + 4 × 10 = 140 ms; after a timeout, 280 ms."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Congestion Avoidance and Control (1988)", text="Jacobson and Karels, revised November 1988.",
                 draw=C.draw_manuscript, link="https://www.cs.princeton.edu/courses/archive/fall08/cos561/papers/jacobson88.pdf", link_text="The paper (PDF, on a Princeton course page)", licence="Drawn placeholder."),
            dict(title="RFC 5681, TCP Congestion Control (2009)", text="The standard that carries Jacobson's algorithms.",
                 draw=C.draw_book, link="https://rfc-editor.org/rfc/rfc5681", link_text="RFC 5681", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "TcpCongestion", d["checks"],
                           "a packet-level simulation of 1 to 64 senders, both kinds, with the link's capacity and the measured useful rate checked in every run, and Chiu and Jain's four rules from the same start.",
                           ["static void onAck(Sender x, int ack, long t)", "static void onTimeout(Sender x, long t)"]),
    ]
    return dict(
        title="TCP Congestion Control", date="1986–1989",
        description="Era 7, topic 10 of The Algorithm Evolution Atlas: the 1986 congestion collapse, Jacobson and Karels's slow start, AIMD and variance-based timers, and Chiu and Jain's proof that AIMD is fair.",
        lede="In October 1986 a connection that should carry 32,000 bits a second carried 40. Every computer was obeying the protocol. Jacobson and Karels taught each sender to read a lost packet as a sign of congestion, and to back off.",
        fieldnote=f"I watched 32 uncontrolled senders lose {f32['drop']}% of their packets and spend {float(f32['dup']) * 100:.0f}% of the link on copies. With Jacobson's rules they lost {j32['drop']}%, kept the link full, and shared it almost equally, without exchanging a single word.",
        card=[("When", "Collapse 1986; paper 1988; analysis 1989"),
              ("Where", "Lawrence Berkeley Laboratory and UC Berkeley; DEC"),
              ("What hurt", "Congestion collapse: losses, timeouts and duplicate packets"),
              ("The fix", "Slow start, AIMD, variance-based timers"),
              ("Checked", f"32 senders: {f32['drop']}% dropped became {j32['drop']}%")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `TcpCongestion.java`.",
    )
