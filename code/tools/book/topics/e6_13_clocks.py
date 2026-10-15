"""Era 6, topic 13: logical clocks (Lamport). Every number is parsed from LogicalClocks.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"three: processes ([A-Z, ]+) ; events with their clocks: (.*?) ; of the (\d+) pairs of events, (\d+) are ordered by happened-before and (\d+) are concurrent ; (.*?), so C\((\w+)\) = (\d+) < C\((\w+)\) = (\d+) ; (\w+) \(clock (\d+)\) and (\w+) \(clock (\d+)\) are concurrent", ln):
            evs = []
            for part in m.group(2).split(", "):
                mm = re.match(r"([pqr]\d)( sends to [PQR]| receives)? (\d+)$", part)
                evs.append(dict(name=mm.group(1), kind=(mm.group(2) or "").strip(), clock=int(mm.group(3))))
            d["three"] = dict(procs=[p.strip() for p in m.group(1).split(",")], events=evs, pairs=m.group(3), ordered=m.group(4), conc=m.group(5),
                              chain=m.group(6), a=m.group(7), ca=m.group(8), b=m.group(9), cb=m.group(10),
                              x=m.group(11), cx=m.group(12), y=m.group(13), cy=m.group(14))
        elif m := re.match(r"random: (\d+) random runs of (\d+) to (\d+) processes and (\d+) to (\d+) steps ; ([\d,]+) pairs of events ; ([\d,]+) ordered by happened-before, .*? ; ([\d,]+) concurrent pairs, of which ([\d,]+) \((\d+)%\) still have different clocks", ln):
            d["rand"] = dict(runs=m.group(1), plo=m.group(2), phi=m.group(3), slo=m.group(4), shi=m.group(5), pairs=m.group(6), hb=m.group(7),
                             conc=m.group(8), diff=m.group(9), pct=m.group(10))
        elif m := re.match(r"mutex: (\d+) processes .*? ; ([\d,]+) entries ; .*? ; ([\d,]+) messages, ([\d.]+) per entry \(.*?: (.*?)\)$", ln):
            d["mutex"] = dict(n=m.group(1), entries=m.group(2), msgs=m.group(3), per=m.group(4), formula=m.group(5))
        elif m := re.match(r"anomaly: .*? if A's clock had reached (\d+) and B's only (\d+), the system orders b \(clock (\d+)\) before a \(clock (\d+)\)", ln):
            d["anom"] = dict(ca=m.group(1), cb=m.group(2), b=m.group(3), a=m.group(4))
    d["checks"] = C.checks(text)
    return d


def scenario(d):
    """Events in creation order, each with its process, and the index of the send it receives (if any)."""
    evs = d["three"]["events"]
    out = []
    pending = {}                      # receiving process -> index of the send waiting for it
    for i, e in enumerate(evs):
        p = "pqr".index(e["name"][0])
        frm = -1
        if e["kind"].startswith("sends to"):
            pending["PQR".index(e["kind"][-1])] = i
        elif e["kind"] == "receives":
            frm = pending.pop(p)
        out.append(dict(p=p, name=e["name"], clock=e["clock"], frm=frm))
    return out


# ----------------------------------------------------------------------------------------------------------------------
def spacetime_svg(d):
    sc = scenario(d)
    th = d["three"]

    def draw(t, standalone):
        o = []
        W, H = 780, 300
        ys = [70, 150, 230]
        X = lambda i: 110 + i * 64
        o.append(C.text(20, 26, "Three processes; time runs to the right; arrows are messages; each event shows its clock", t["ink"], 13, "start", 700))
        for k, y in enumerate(ys):
            o.append(C.text(30, y + 5, th["procs"][k], t["ink"], 14, "start", 700))
            o.append(C.line(60, y, W - 30, y, t["axis"], 2))
        for i, e in enumerate(sc):
            if e["frm"] >= 0:
                s = sc[e["frm"]]
                x1, y1, x2, y2 = X(e["frm"]), ys[s["p"]], X(i), ys[e["p"]]
                o.append(C.line(x1, y1, x2, y2, t["blue"], 1.8))
                ux, uy = (x2 - x1), (y2 - y1)
                L = (ux * ux + uy * uy) ** 0.5
                ux, uy = ux / L, uy / L
                ex, ey = x2 - ux * 9, y2 - uy * 9
                o.append(C.path(f"M{ex:.1f},{ey:.1f} L{ex - ux * 9 - uy * 4.5:.1f},{ey - uy * 9 + ux * 4.5:.1f} L{ex - ux * 9 + uy * 4.5:.1f},{ey - uy * 9 - ux * 4.5:.1f} Z", None, t["blue"]))
        hot = {th["x"], th["y"]}
        sends_down = {e["frm"] for e in sc if e["frm"] >= 0 and sc[e["frm"]]["p"] < e["p"]}
        for i, e in enumerate(sc):
            col = t["red"] if e["name"] in hot else t["ink"]
            y = ys[e["p"]]
            from_above = e["frm"] >= 0 and sc[e["frm"]]["p"] < e["p"]
            o.append(C.circle(X(i), y, 8, t["surface"], col, 2))
            o.append(C.text(X(i) + (12 if from_above else -12), y - 12, e["name"], col, 12, "start" if from_above else "end", 700))
            o.append(C.text(X(i) + (-12 if i in sends_down else 12), y + 22, str(e["clock"]), t["blue"], 13, "end" if i in sends_down else "start", 700))
        o.append(C.text(20, H - 30, f"{th['chain'].replace(' -> ', ' → ')}: so C({th['a']}) = {th['ca']} < C({th['b']}) = {th['cb']}.", t["muted"], 12))
        o.append(C.text(20, H - 10, f"Red: {th['x']} (clock {th['cx']}) and {th['y']} (clock {th['cy']}) are concurrent: no chain of messages joins them, though their clocks differ.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A space-time diagram with logical clocks", t, standalone, 0.55, 780)
    return draw


LC_HTML = """
<div class="board lc-board">
  <div style="min-width:0">
    <div class="lc-diagram" id="lc-diagram"></div>
  </div>
  <div style="min-width:0">
    <div class="lc-btns"><button type="button" id="lc-prog">The program's run</button><button type="button" id="lc-rand">A random run</button></div>
    <div class="lc-stats" id="lc-stats"></div>
    <p class="say" id="lc-say" aria-live="polite"></p>
  </div>
</div>
"""

LC_CSS = """
.lc-diagram svg{display:block;width:100%;height:auto}
.lc-diagram circle{cursor:pointer}
.lc-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.lc-stats{font:13px var(--mono);display:grid;gap:3px}
"""

LC_JS = r"""
(() => {
  const box = document.getElementById("lc-diagram");
  if (!box) return;
  const PROG = __SCEN__, NAMES = ["P", "Q", "R"];
  let ev, hb, sel = [], seed = 1978;
  const r = n => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 2147483648 * n); };
  function load(list) {
    ev = list.map(e => ({...e}));
    const clock = [0, 0, 0];
    ev.forEach(e => { clock[e.p] = e.frm >= 0 ? Math.max(clock[e.p], ev[e.frm].clock) + 1 : clock[e.p] + 1; e.clock = clock[e.p]; });
    const n = ev.length; hb = ev.map(() => new Array(n).fill(false));
    ev.forEach((e, i) => {
      const prev = ev.slice(0, i).map((x, k) => k).filter(k => ev[k].p === e.p).pop();
      [prev, e.frm >= 0 ? e.frm : undefined].forEach(k => { if (k === undefined) return; hb[k][i] = true; for (let x = 0; x < n; x++) if (hb[x][k]) hb[x][i] = true; });
    });
    sel = []; show("Click two events to compare them.");
  }
  function random() {
    const list = [], waiting = [], count = [0, 0, 0];
    while (list.length < 11) {
      const p = r(3), u = r(10);
      if (u < 4 && waiting.length) {
        const w = waiting.findIndex(x => x.to === p);
        if (w >= 0) { const s = waiting.splice(w, 1)[0]; count[p]++; list.push({p, name: "pqr"[p] + count[p], frm: s.at}); continue; }
      }
      count[p]++;
      const e = {p, name: "pqr"[p] + count[p], frm: -1}; list.push(e);
      if (u >= 6) { let to = r(2); if (to >= p) to++; waiting.push({at: list.length - 1, to}); }
    }
    load(list);
  }
  function show(msg) {
    box.innerHTML = "";
    const W = 40 + ev.length * 52 + 20, svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", `0 0 ${W} 230`); box.appendChild(svg);
    const ys = [50, 120, 190], X = i => 50 + i * 52;
    ys.forEach((y, k) => { sv("line", {x1: 30, y1: y, x2: W - 10, y2: y, stroke: "var(--axis)", "stroke-width": 2}, svg); const t = sv("text", {x: 8, y: y + 5, "font-size": 13, "font-weight": 700, fill: "var(--ink)"}, svg); t.textContent = NAMES[k]; });
    ev.forEach((e, i) => { if (e.frm < 0) return; sv("line", {x1: X(e.frm), y1: ys[ev[e.frm].p], x2: X(i), y2: ys[e.p], stroke: "var(--blue)", "stroke-width": 1.8}, svg); });
    ev.forEach((e, i) => {
      const on = sel.includes(i);
      const c = sv("circle", {cx: X(i), cy: ys[e.p], r: 9, fill: on ? "var(--red)" : "var(--surface)", stroke: "var(--ink)", "stroke-width": 2}, svg);
      c.addEventListener("click", () => pick(i));
      const t = sv("text", {x: X(i), y: ys[e.p] - 14, "text-anchor": "middle", "font-size": 11, "font-weight": 700, fill: "var(--ink)"}, svg); t.textContent = e.name;
      const k = sv("text", {x: X(i), y: ys[e.p] + 25, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: "var(--blue)"}, svg); k.textContent = e.clock;
    });
    let ordered = 0, conc = 0;
    for (let a = 0; a < ev.length; a++) for (let b = a + 1; b < ev.length; b++) (hb[a][b] || hb[b][a]) ? ordered++ : conc++;
    const st = document.getElementById("lc-stats"); st.innerHTML = "";
    el("div", {}, st, `${ev.length} events, ${ordered + conc} pairs: ${ordered} ordered, ${conc} concurrent`);
    el("div", {}, st, "blue numbers: logical clocks (IR1 and IR2)");
    document.getElementById("lc-say").textContent = msg;
  }
  function pick(i) {
    sel = sel.length >= 2 ? [i] : sel.includes(i) ? sel : [...sel, i];
    if (sel.length < 2) { show(`${ev[i].name} chosen (clock ${ev[i].clock}); click another event.`); return; }
    const [a, b] = sel, A = ev[a], B = ev[b];
    const m = hb[a][b] ? `${A.name} happened before ${B.name}, and indeed C(${A.name}) = ${A.clock} < C(${B.name}) = ${B.clock}.` :
      hb[b][a] ? `${B.name} happened before ${A.name}, and indeed C(${B.name}) = ${B.clock} < C(${A.name}) = ${A.clock}.` :
      `${A.name} and ${B.name} are concurrent: no chain of steps and messages joins them` + (A.clock !== B.clock ? `, though their clocks (${A.clock} and ${B.clock}) differ.` : ".");
    show(m);
  }
  document.getElementById("lc-prog").addEventListener("click", () => load(PROG));
  document.getElementById("lc-rand").addEventListener("click", random);
  load(PROG);
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How logical clocks combined older ideas, and where they led")
    W = 210
    nodes = {
        "rel": (20, 20, "Special relativity", "no absolute \"at the same time\"", "a resemblance Lamport noted", "ink"),
        "net": (395, 20, "Computers joined by messages", "separate clocks, delayed messages", "", "ink"),
        "mx": (770, 20, "Mutual exclusion", "one at a time, with shared memory", "topic 2", "ink"),
        "lc": (395, 180, "Logical clocks", "⊕ happened-before; counters pushed by messages", "Lamport, 1978", "red"),
        "tot": (20, 340, "A total order", "ties broken by process number", "", "ink"),
        "dme": (395, 340, "Mutual exclusion by messages", "requests served in timestamp order", "", "ink"),
        "rsm": (770, 340, "Replicated state machines", "copies that apply the same steps in the same order", "", "ink"),
        "today": (395, 490, "Today", "\"causality and logical clocks, replicated state machines, and sequential consistency\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("rel", "lc", ports=("bottom", "top:0.15"), dashed=True)
    D.edge("net", "lc", ports=("bottom", "top"))
    D.edge("mx", "lc", ports=("bottom", "top:0.85"), label="the same task, without shared memory", at=0.5, dx=8, anchor="start")
    D.edge("lc", "tot", ports=("bottom:0.15", "top"))
    D.edge("lc", "dme", ports=("bottom", "top"))
    D.edge("lc", "rsm", ports=("bottom:0.85", "top"))
    D.edge("dme", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: the work the ACM's 2014 Turing Award announcement lists. Dashed: a resemblance the paper points out, not a source.", "caption")
    return D


def chain(d):
    th, rd, mx, an = d["three"], d["rand"], d["mutex"], d["anom"]
    steps = [
        ("Separate computers' clocks disagree and messages are late: what does \"before\" mean?",
         f"Happened-before: steps of one process, and messages; in the example {th['ordered']} of {th['pairs']} pairs ordered, {th['conc']} concurrent", "Lamport, 1978"),
        ("Each machine needs a number for each event that respects that order",
         f"Logical clocks (IR1, IR2): C(a) < C(b) on all {rd['hb']} ordered pairs in {rd['runs']} random runs", "the Clock Condition"),
        (f"A smaller clock does not mean \"before\": {rd['pct']}% of concurrent pairs have different clocks",
         f"Break ties by process number: one total order, consistent with happened-before in all {rd['runs']} runs", "every machine computes the same order"),
        ("Sharing one resource with no central scheduler",
         f"Requests served in timestamp order: {mx['entries']} entries, never two inside, {mx['per']} messages each", "Lamport's mutual exclusion"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from no common clock to one common order")
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
    th, rd, mx, an = d["three"], d["rand"], d["mutex"], d["anom"]
    sc = scenario(d)
    ev_rows = [[e["name"], th["procs"][e["p"]], (f"receives from {sc[e['frm']]['name']}" if e["frm"] >= 0 else
               next((f"sends to {th['procs'][x['p']]}" for x in sc if x["frm"] == i), "")), e["clock"]] for i, e in enumerate(sc)]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Mutual exclusion had been solved for processes that share memory (topic 2); computers joined by messages share nothing, not even a clock. Lamport defined \"before\" by what information could have flowed, as relativity defines it by what light could reach, and gave each machine a counter that respects it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: logical clocks. Blue: what the ACM credited them with."),
        ]),
        dict(id="play", eyebrow="Try it", title="Before, after, or neither", toc="Try it", blocks=[
            dict(type="p", text="The program's run: three processes, time running to the right, arrows for messages, and each event's logical clock in blue. Click two events: if a chain of steps and messages leads from one to the other, it happened before, and its clock is smaller; if not, they are concurrent, whatever their clocks say. Then try a random run."),
            dict(type="widget", html=LC_HTML, js=LC_JS.replace("__SCEN__", json.dumps(sc)), css=LC_CSS,
                 fallback=dict(type="table", head=["Event", "Process", "Message", "Logical clock"], num=[3], rows=ev_rows),
                 note="In the interactive edition you can compare any two events of the program's run, or of a random one."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Two rules for a counter", toc="How it works", blocks=[
            dict(type="p", text="**Happened before.** Event a happened before event b (a → b) if they are in the same process and a came first, or a is the sending of a message and b its receipt, or a chain of such steps leads from a to b. If neither a → b nor b → a, the two are *concurrent*: nothing inside the system can tell which came first."),
            dict(type="p", text="**The clock rules.** Each process keeps a counter. IR1: add one between any two of its events. IR2: stamp each message with the sender's counter; on receipt, set the counter above both its own value and the stamp. Then a → b always gives C(a) < C(b), the Clock Condition. The converse fails: a smaller clock does not mean happened-before."),
            dict(type="svg", name="spacetime", draw=spacetime_svg(d), alt="A space-time diagram with logical clocks", width=780),
            dict(type="p", text="**One order for all.** Order all events by clock, breaking ties by process number. Every machine can compute this order from the timestamps alone, and it never contradicts happened-before. Lamport's mutual exclusion uses it: a process asks every other for the resource, with a timestamp, and enters when its request is the earliest in that order and it has heard from everyone with a later timestamp."),
            dict(type="callout", kind="key", label="Key idea",
                 text="When there is no common clock, don't pretend there is one. Order events only as far as information could have travelled, and agree on an arbitrary but common way to order the rest."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Checked on every pair", toc="Measured", blocks=[
            dict(type="table", head=["Event", "Process", "Message", "Logical clock"], num=[3], rows=ev_rows),
            dict(type="p", text=f"**The example.** Of the {th['pairs']} pairs of events, {th['ordered']} are ordered by happened-before and {th['conc']} are concurrent. {th['a']} → {th['b']} through {th['chain'].replace(' -> ', ' → ')}, so C({th['a']}) = {th['ca']} < C({th['b']}) = {th['cb']}; {th['x']} (clock {th['cx']}) and {th['y']} (clock {th['cy']}) are concurrent, though their clocks differ."),
            dict(type="p", text=f"**Random runs.** {rd['runs']} random runs of {rd['plo']} to {rd['phi']} processes and {rd['slo']} to {rd['shi']} steps: {rd['pairs']} pairs of events, {rd['hb']} ordered by happened-before, and for every one of them C(a) < C(b). Of the {rd['conc']} concurrent pairs, {rd['diff']} ({rd['pct']}%) still had different clocks. The order by clock, ties broken by process number, respected happened-before in every run."),
            dict(type="p", text=f"**Mutual exclusion.** {mx['n']} processes sharing one resource with no central scheduler, messages delayed at random (each channel delivering in order): {mx['entries']} entries, never two inside at once, requests granted in the order of their timestamps, and {mx['msgs']} messages, {mx['per']} per entry ({mx['formula']})."),
            dict(type="p", text=f"**The anomaly.** A user issues request a at machine A, then telephones a colleague at B, who issues request b. The call is outside the system, so to it a and b are concurrent; if A's clock had reached {an['ca']} and B's only {an['cb']}, the system orders b (clock {an['b']}) before a (clock {an['a']}), the reverse of what happened. Lamport's remedies: carry the timestamp through the call, or keep physical clocks close enough."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Eight pages in 1978", toc="The evidence", blocks=[
            dict(type="p", text="Leslie Lamport, \"Time, Clocks, and the Ordering of Events in a Distributed System\" (Massachusetts Computer Associates; *Communications of the ACM* 21(7): 558–565, July 1978), defines happened-before as \"the smallest relation satisfying the following three conditions\", states the Clock Condition and the rules IR1 (\"Each process P_i increments C_i between any two successive events\") and IR2, builds a total order by breaking ties with an ordering of the processes, and solves mutual exclusion with it, noting that \"a central scheduler\" granting requests in arrival order fails. It discusses the anomaly of events outside the system, and remarks on the resemblance to the space-time formulation of special relativity."),
            dict(type="p", text="The ACM's announcement of the 2013 Turing Award (18 March 2014) recognized Lamport \"for imposing clear, well-defined coherence on the seemingly chaotic behavior of distributed computing systems\", naming \"causality and logical clocks, replicated state machines, and sequential consistency\"; it also notes that he developed LaTeX. Wikipedia gives the citation as \"fundamental contributions to the theory and practice of distributed and concurrent systems\"; the catalog records both wordings."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Mutual exclusion, again", toc="Full circle", blocks=[
            dict(type="p", text="Dijkstra's semaphore (topic 2) made processes take turns through a shared variable. Lamport's processes share nothing, yet the same safety holds: never two inside at once, every request served, in the order the timestamps give. The price is messages: a request, an acknowledgement and a release to every other process."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"In topic 2, three processes and one semaphore: four instructions each. Here, {mx['n']} processes and no shared memory at all: {mx['per']} messages per entry, and the same guarantee."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Process P's clock is 4 when it receives a message stamped 9. What is its clock after the receipt?", "10: above both its own value and the stamp."),
            ("If C(a) = 3 and C(b) = 7, did a happen before b?", "Not necessarily: they may be concurrent. Only the other direction holds: if a → b then C(a) < C(b)."),
            ("Why are ties broken by process number?", "Two concurrent events can have the same clock; any fixed rule that every machine knows gives them all the same order."),
            ("In the telephone example, how could the system get the order right?", "Have the first user pass a's timestamp along in the call, so b's clock is set above it."),
            ("How many messages does one entry cost with 10 processes?", "3 × 9 = 27: a request, an acknowledgement and a release to each of the 9 others."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Time, Clocks, and the Ordering of Events in a Distributed System (1978)", text="Lamport's paper, *Communications of the ACM* 21(7): 558–565.",
                 draw=C.draw_manuscript, link="https://amturing.acm.org/p558-lamport.pdf", link_text="The paper (PDF, on the ACM Turing Award site)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LogicalClocks", d["checks"],
                           "every pair of events of a small run and of 500 random runs against the Clock Condition and the total order, Lamport's mutual exclusion with 1,000 entries (safety checked after every event), and the telephone anomaly.",
                           ["Event receive(int p, Event send)", "boolean[][] happenedBefore()"]),
    ]
    return dict(
        title="Logical Clocks", date="1978",
        description="Era 6, topic 13 of The Algorithm Evolution Atlas: Lamport's happened-before relation, logical clocks, a total order of events, and mutual exclusion without shared memory.",
        lede="Computers joined by a network share no clock, and their messages arrive late. Lamport asked what \"before\" can mean between them, and answered with a counter in each machine and two rules.",
        fieldnote=f"In {rd['runs']} random runs I checked {rd['pairs']} pairs of events: whenever one could have influenced the other, its clock was smaller. The converse failed for {rd['pct']}% of the pairs that could not have influenced each other. Before, in this species' networks, means only what a message could have carried.",
        card=[("When", "1978"),
              ("Where", "Massachusetts Computer Associates"),
              ("What hurt", "No common clock; no meaning for \"before\""),
              ("The fix", "Happened-before; clocks pushed forward by messages"),
              ("Checked", f"{rd['hb']} ordered pairs, no exception")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LogicalClocks.java`.",
    )
