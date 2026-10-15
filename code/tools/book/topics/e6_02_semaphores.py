"""Era 6, topic 2: mutual exclusion and the semaphore. Every number is parsed from Semaphores.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"race: .*? all (\d+) interleavings tried: the counter ends at 2 in (\d+) of them and at 1 in (\d+), an update lost ; with P\(s\) before and V\(s\) after, the (\d+) possible orders all end at 2", ln):
            d["race"] = dict(all=m.group(1), ok=m.group(2), lost=m.group(3), sem=m.group(4))
        elif ln.startswith("attempts: "):
            t = re.search(r"taking turns \(turn variable\): (\d+) states, both inside in (\d+)", ln)
            l = re.search(r"look at the other's flag, then raise yours: (\d+) states, both inside at once in (\d+)", ln)
            r = re.search(r"raise your flag, then wait for the other's to fall: (\d+) states, never both inside, but (\d+) state", ln)
            k = re.search(r"Dekker's algorithm \(flags and a turn\): (\d+) states", ln)
            d["att"] = dict(turn=t.group(1), turn_both=t.group(2), look=l.group(1), look_both=l.group(2),
                            raise_=r.group(1), raise_stuck=r.group(2), dekker=k.group(1))
        elif m := re.match(r"mutex: (\w+) processes, .*? ; (\d+) reachable states", ln):
            d["mutex"] = dict(procs=m.group(1), states=m.group(2))
        elif m := re.match(r"embrace: .*? ; (\d+) reachable states, (\d+) of them stuck .*? ; both taking A first: (\d+) states, none stuck", ln):
            d["emb"] = dict(states=m.group(1), stuck=m.group(2), same=m.group(3))
        elif m := re.match(r"buffer: a producer makes items 1 to (\d+), a consumer takes them, through (\d+) places, .*? ; (\d+) reachable states", ln):
            d["buf"] = dict(items=m.group(1), places=m.group(2), states=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def race_svg(d):
    r = d["race"]

    def draw(t, standalone):
        o = []
        W, H = 720, 262
        o.append(C.text(20, 24, "One interleaving that loses an update (counter starts at 0)", t["ink"], 13, "start", 700))
        rows = [("P", "load r = 0", 0), ("Q", "load r = 0", 1), ("P", "r = r + 1 (1)", 0), ("Q", "r = r + 1 (1)", 1), ("P", "store: counter = 1", 0), ("Q", "store: counter = 1", 1)]
        for i, (who, what, lane) in enumerate(rows):
            x = 44 + i * 110
            y = 52 if lane == 0 else 122
            col = t["red"] if i == 5 else (t["blue"] if lane == 0 else t["ink2"])
            o.append(C.rect(x, y, 104, 48, t["surface"], col, 1.6, 4))
            o.append(C.text(x + 52, y + 20, who, col, 13, "middle", 700))
            o.append(C.text(x + 52, y + 38, what, t["ink"], 11, "middle"))
        o.append(C.text(14, 80, "P", t["blue"], 13, "start", 700))
        o.append(C.text(14, 150, "Q", t["ink2"], 13, "start", 700))
        o.append(C.line(44, 190, 44 + 6 * 110 - 6, 190, t["axis"], 1.5))
        o.append(C.text(44, 208, "time →", t["muted"], 11))
        o.append(C.text(20, 232, f"Two additions, but the counter ends at 1. Of all {r['all']} interleavings, {r['lost']} lose an update;", t["muted"], 12))
        o.append(C.text(20, 250, "with P(s) before the steps and V(s) after them, none do.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Two processes interleaving and losing an update", t, standalone, 0.55, 720)
    return draw


SM_HTML = """
<div class="board sm-board">
  <div style="min-width:0">
    <label class="sm-pick">Algorithm
      <select id="sm-alg">
        <option value="race">No protection: add one to a shared counter</option>
        <option value="sem">Semaphore: P(s), add one, V(s)</option>
        <option value="look">Look at the other's flag, then raise yours</option>
        <option value="raise">Raise your flag, then wait for the other's to fall</option>
      </select></label>
    <div class="sm-procs" id="sm-procs"></div>
  </div>
  <div style="min-width:0">
    <div class="sm-btns"><button type="button" id="sm-p">Step P</button><button type="button" id="sm-q">Step Q</button><button type="button" id="sm-reset">Start again</button></div>
    <div class="sm-shared" id="sm-shared"></div>
    <p class="say" id="sm-say" aria-live="polite"></p>
  </div>
</div>
"""

SM_CSS = """
.sm-pick{display:grid;gap:4px;font-size:14px}
.sm-pick select{font:inherit;padding:4px;max-width:100%}
.sm-procs{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.sm-proc{border:1px solid var(--rule);padding:8px;min-width:0}
.sm-proc b{display:block;margin-bottom:4px}
.sm-proc ol{margin:0;padding-left:22px;font:12.5px var(--mono)}
.sm-proc li{padding:2px 4px;border-radius:3px}
.sm-proc li.pc{background:var(--blue);color:var(--on-blue)}
.sm-proc li.pc.cs{background:var(--red);color:var(--on-red)}
.sm-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.sm-shared{font:13px var(--mono);display:grid;gap:3px}
"""

SM_JS = r"""
(() => {
  const box = document.getElementById("sm-procs");
  if (!box) return;
  const BLOCK = -2, DONE = -1;
  const A = {
    race: {sh: {counter: 0}, cs: [], loop: false, code: [
      ["r = counter", (s, l) => { l.r = s.counter; }],
      ["r = r + 1", (s, l) => { l.r++; }],
      ["counter = r", (s, l) => { s.counter = l.r; }]]},
    sem: {sh: {counter: 0, s: 1}, cs: [1, 2, 3], loop: false, code: [
      ["P(s): wait until s > 0, then s = s - 1", s => s.s > 0 ? (s.s--, undefined) : BLOCK],
      ["r = counter", (s, l) => { l.r = s.counter; }],
      ["r = r + 1", (s, l) => { l.r++; }],
      ["counter = r", (s, l) => { s.counter = l.r; }],
      ["V(s): s = s + 1", s => { s.s++; }]]},
    look: {sh: {flagP: 0, flagQ: 0}, cs: [2], loop: true, code: [
      ["wait until the other's flag = 0", (s, l, me) => s[me === 0 ? "flagQ" : "flagP"] === 0 ? undefined : BLOCK],
      ["my flag = 1", (s, l, me) => { s[me === 0 ? "flagP" : "flagQ"] = 1; }],
      ["critical section", () => {}],
      ["my flag = 0", (s, l, me) => { s[me === 0 ? "flagP" : "flagQ"] = 0; }]]},
    raise: {sh: {flagP: 0, flagQ: 0}, cs: [2], loop: true, code: [
      ["my flag = 1", (s, l, me) => { s[me === 0 ? "flagP" : "flagQ"] = 1; }],
      ["wait until the other's flag = 0", (s, l, me) => s[me === 0 ? "flagQ" : "flagP"] === 0 ? undefined : BLOCK],
      ["critical section", () => {}],
      ["my flag = 0", (s, l, me) => { s[me === 0 ? "flagP" : "flagQ"] = 0; }]]},
  };
  let alg, sh, pc, loc, log;
  function reset() {
    alg = A[document.getElementById("sm-alg").value];
    sh = {...alg.sh}; pc = [0, 0]; loc = [{r: 0}, {r: 0}]; log = "You are the scheduler: choose which process takes its next step.";
    show();
  }
  function canMove(p) {
    if (pc[p] === DONE) return false;
    const trial = {...sh}, tl = {...loc[p]};
    return alg.code[pc[p]][1](trial, tl, p) !== BLOCK;
  }
  function move(p) {
    if (!canMove(p)) return;
    const [txt, f] = alg.code[pc[p]];
    f(sh, loc[p], p);
    pc[p]++;
    if (pc[p] === alg.code.length) pc[p] = alg.loop ? 0 : DONE;
    log = `${p === 0 ? "P" : "Q"}: ${txt}.`;
    show();
  }
  const inCS = p => pc[p] >= 0 && alg.cs.includes(pc[p]);
  function show() {
    box.innerHTML = "";
    ["P", "Q"].forEach((name, p) => {
      const d = el("div", {class: "sm-proc"}, box);
      el("b", {}, d, `Process ${name}` + (pc[p] === DONE ? " (finished)" : "") + (alg.code.length && "r" in loc[p] && !alg.loop ? `, r = ${loc[p].r}` : ""));
      const ol = el("ol", {}, d);
      alg.code.forEach(([txt], i) => el("li", {class: (pc[p] === i ? "pc" : "") + (alg.cs.includes(i) || (alg.cs.length === 0 && i < 3) ? " cs" : "")}, ol, txt));
    });
    const st = document.getElementById("sm-shared"); st.innerHTML = "";
    el("div", {}, st, "shared: " + Object.entries(sh).map(([k, v]) => `${k} = ${v}`).join(", "));
    document.getElementById("sm-p").disabled = !canMove(0);
    document.getElementById("sm-q").disabled = !canMove(1);
    let msg = log;
    if (inCS(0) && inCS(1)) msg += " Both processes are in the critical section at once: mutual exclusion has failed.";
    else if (!canMove(0) && !canMove(1) && !(pc[0] === DONE && pc[1] === DONE)) msg += " Neither process can move: each waits for the other for ever (a deadlock).";
    if (pc[0] === DONE && pc[1] === DONE) msg += sh.counter === 2 ? " Both added one: the counter is 2." : ` Both added one, but the counter is ${sh.counter}: an update was lost.`;
    document.getElementById("sm-say").textContent = msg;
  }
  document.getElementById("sm-p").addEventListener("click", () => move(0));
  document.getElementById("sm-q").addEventListener("click", () => move(1));
  document.getElementById("sm-reset").addEventListener("click", reset);
  document.getElementById("sm-alg").addEventListener("change", reset);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How mutual exclusion and the semaphore combined older ideas, and where they led")
    W = 210
    nodes = {
        "mp": (20, 20, "Multiprogramming", "several programs share one machine", "", "ink"),
        "mem": (395, 20, "Shared memory", "both read and write the same words", "", "ink"),
        "ind": (770, 20, "Indivisible steps", "a load or a store happens whole", "", "ink"),
        "dek": (20, 180, "Dekker's algorithm", "⊕ flags and a turn: the first correct solution", "about 1962", "ink"),
        "sem": (395, 180, "The semaphore", "⊕ P waits and lowers, V raises, indivisibly", "Dijkstra, 1962–1965", "red"),
        "dl": (770, 180, "The deadly embrace", "two processes, each holding what the other needs", "named in EWD 123", "ink"),
        "pc": (20, 340, "Producer and consumer", "a buffer guarded by two semaphores", "", "ink"),
        "os": (395, 340, "Operating systems", "locks, queues, schedulers", "", "ink"),
        "lc": (770, 340, "Exclusion by messages", "no shared memory at all", "Lamport, topic 13", "ink"),
        "today": (395, 490, "Today", "locks and semaphores in operating systems and language libraries", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("mp", "dek", ports=("bottom", "top"))
    D.edge("mem", "sem", ports=("bottom", "top"))
    D.edge("ind", "sem", ports=("bottom", "top:0.85"))
    D.edge("dek", "sem", ports=("right", "left"), label="simpler", at=0.5, dy=-8)
    D.edge("sem", "dl", ports=("right", "left"))
    D.edge("sem", "pc", ports=("bottom:0.2", "top:0.8"))
    D.edge("sem", "os", ports=("bottom", "top"))
    D.edge("sem", "lc", ports=("bottom:0.8", "top:0.2"), dashed=True)
    D.edge("os", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: Lamport's mutual exclusion (topic 13) solves the same problem with messages instead of shared memory.", "caption")
    return D


def chain(d):
    r, a, e = d["race"], d["att"], d["emb"]
    steps = [
        (f"Two processes add one to a counter: {r['lost']} of {r['all']} interleavings lose an update",
         "A critical section that only one process may enter at a time", "the problem, stated by Dijkstra"),
        (f"Obvious flag schemes fail: both inside in {a['look_both']} state, or stuck for ever in {a['raise_stuck']}",
         f"Dekker's flags and a turn: {a['dekker']} states, all safe", "Dekker, credited in EWD 123"),
        ("Dekker's method is long and only for two processes",
         f"The semaphore: P(s) before, V(s) after; {d['mutex']['procs']} processes, {d['mutex']['states']} states, all safe", "Dijkstra"),
        (f"Two semaphores taken in opposite orders: {e['stuck']} state stuck for ever",
         f"Take them in the same order: {e['same']} states, none stuck", "the deadly embrace, named"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from lost updates to deadlock")
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
    r, a, mx, e, b = d["race"], d["att"], d["mutex"], d["emb"], d["buf"]
    rows = [["Take turns (a turn variable)", a["turn"], a["turn_both"], "0", "a process waits for the other's turn even when the other is not interested"],
            ["Look at the other's flag, then raise yours", a["look"], a["look_both"], "0", "both look, both see 0, both go in"],
            ["Raise your flag, then wait for the other's to fall", a["raise_"], "0", a["raise_stuck"], "both raise, both wait for ever"],
            ["Dekker: flags and a turn", a["dekker"], "0", "0", "correct; every process can always still get in"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Machines of the 1960s ran several programs at once, and programs that share memory can trip over each other. Dekker found a correct way for two processes to take turns using nothing but shared variables; Dijkstra replaced it with a new kind of variable whose two operations cannot be interrupted. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the semaphore. Blue: where it is used today."),
        ]),
        dict(id="play", eyebrow="Try it", title="You are the scheduler", toc="Try it", blocks=[
            dict(type="p", text="Two processes, P and Q, run the same little program. You decide which one takes the next step, as an operating system would, and you are allowed to be unlucky. Can you make the counter lose an update? Can you get both processes into the critical section (red) at once, or make both wait for ever? Then try the semaphore."),
            dict(type="widget", html=SM_HTML, js=SM_JS, css=SM_CSS,
                 fallback=dict(type="svg", name="race", draw=race_svg(d), alt="Two processes interleaving and losing an update", width=720),
                 note="In the interactive edition you choose which process moves next, and try to break each algorithm."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Try every interleaving", toc="How it works", blocks=[
            dict(type="p", text="**The trouble.** A process that adds one to a shared counter does three steps: load the counter into a register, add one, store it back. If two processes interleave those steps, both may load the same old value, and one addition vanishes. The error appears only for some orders of the steps, which is why it is so hard to find by testing."),
            dict(type="p", text="**The critical section.** Mark the steps that must not overlap. The task is a protocol before and after the critical section that guarantees, for every possible order of steps, that at most one process is inside, and that neither waits for ever while the other is not even interested."),
            dict(type="p", text="**The semaphore.** A shared non-negative integer s with two operations that happen indivisibly. P(s) waits until s is positive, then lowers it by one; V(s) raises it by one. Start s at 1, put P(s) before the critical section and V(s) after it: the first process to arrive lowers s to 0, and every other waits in P until the V."),
            dict(type="p", text="**How the program checks it.** Rather than run the processes and hope for a bad order, the program explores every state the processes can reach, taking every possible next step from every state, and checks each state."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Programs that share memory must be correct for every order in which their steps can interleave, not just the orders seen in testing. A small set of indivisible operations, used by a fixed protocol, makes that checkable."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Every state searched", toc="Measured", blocks=[
            dict(type="p", text=f"**The lost update.** Two processes, three steps each: all {r['all']} interleavings tried. The counter ends at 2 in {r['ok']} of them and at 1 in {r['lost']}. With P(s) before and V(s) after, only {r['sem']} orders are possible, and both end at 2."),
            dict(type="table", head=["Attempt at mutual exclusion (two processes)", "Reachable states", "States with both inside", "States where both wait for ever", "Verdict"], num=[1, 2, 3], rows=rows, hl=3),
            dict(type="p", text=f"**One semaphore, {mx['procs']} processes.** P(s), critical section, V(s), with s = 1 at the start: {mx['states']} reachable states, never two inside, never stuck, and every process can always still get in. Four instructions instead of Dekker's ten, and for any number of processes."),
            dict(type="p", text=f"**The deadly embrace.** Process 1 takes semaphore A then B; process 2 takes B then A. Of {e['states']} reachable states, {e['stuck']} is stuck for ever: each holds one and waits for the other. If both take A first: {e['same']} states, none stuck."),
            dict(type="p", text=f"**Producer and consumer.** A producer makes items 1 to {b['items']}, a consumer takes them, through {b['places']} places, with two semaphores counting the empty and the full places. All {b['states']} reachable states were checked: the producer never gets more than {b['places']} ahead, the consumer never takes from an empty place, and every item arrives in order."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Cooperating sequential processes", toc="The evidence", blocks=[
            dict(type="p", text="Dijkstra's essay \"Cooperating sequential processes\" (manuscript EWD 123, Technological University, Eindhoven, finalized in September 1965 and published in 1968) states the problem: in each cycle \"a so-called 'critical section' occurs\", and \"at any moment at most one of the two is engaged in its critical section\". It credits a colleague: \"To the Dutch mathematician Th.J.Dekker the credit is due for the first correct solution\". It defines semaphores as \"essentially non-negative integers\", with the V-operation \"to increase the value of its argument semaphore by 1\" and the P-operation \"to decrease the value of its argument semaphore by 1 as soon as the resulting value would be non-negative\". Its section 6 is \"The Problem of the Deadly Embrace\"."),
            dict(type="p", text="Krzysztof Apt's portrait of Dijkstra dates the semaphore to 1962 (EWD 51) and says the essay \"originated the field of concurrent programming\". What the letters P and V stand for is disputed: Apt gives the invented word \"Prolaag\", for lowering; a note at New York University, quoting Gert Vegter, gives *Probeer* (try) and *Verhoog* (increase). EWD 123 itself does not say."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Correct on paper, wrong on a chip", toc="Full circle", blocks=[
            dict(type="p", text="Dekker's algorithm assumes that every load and store happens whole and in program order. Modern processors reorder memory operations for speed, and Wikipedia notes that the algorithm \"won't work on SMP machines equipped with these CPUs without the use of memory barriers\". The semaphore survived because it puts the indivisibility where it belongs: in one operation that the hardware and the operating system promise to perform whole."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="Thirteen years later Lamport solved the same problem for computers that share no memory at all, only messages (topic 13)."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Two processes each add one to a counter that starts at 5. What values can it end with?", "7 if the additions do not overlap; 6 if both load 5 before either stores."),
            ("A semaphore starts at 3. What does P, P, P, P do?", "The first three lower it to 2, 1, 0; the fourth waits until some process does V."),
            ("Why is \"take turns\" not good enough, though it never lets both in?", "A process that wants to enter must wait for the other's turn, even if the other never wants to enter again."),
            ("How do you avoid the deadly embrace with two semaphores?", "Make every process take them in the same order."),
            ("In the producer and consumer, what do the two semaphores count?", "One counts empty places (the producer does P on it), the other full places (the consumer does P on it)."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="EWD 123, Cooperating sequential processes (1965)", text="Dijkstra's handwritten-and-typed essay, numbered in his own series of manuscripts.",
                 draw=C.draw_manuscript, link="https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html", link_text="Transcription, E. W. Dijkstra Archive", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Semaphores", d["checks"],
                           "every interleaving of two processes adding to a counter, every reachable state of four attempts at mutual exclusion (Dekker's among them), a semaphore with three processes, the deadly embrace, and a producer and consumer.",
                           ["static Instr P(int s)", "static Instr V(int s)", "long bothInCS()"]),
    ]
    return dict(
        title="Mutual Exclusion and the Semaphore", date="1962–1965",
        description="Era 6, topic 2 of The Algorithm Evolution Atlas: critical sections, Dekker's algorithm, Dijkstra's semaphore and the deadly embrace, checked over every reachable state.",
        lede="Two programs that share memory can each be correct and still be wrong together. Dijkstra stated the problem, credited Dekker with the first solution, and gave the species a simpler tool: the semaphore.",
        fieldnote=f"Two processes adding one to a counter can interleave in {r['all']} ways; {r['lost']} of them lose an addition. No test run would show me which, so the program tried them all, and then tried every state of every remedy.",
        card=[("When", "Dekker about 1962; semaphore 1962; EWD 123, 1965"),
              ("Where", "Amsterdam and Eindhoven"),
              ("What hurt", "Lost updates and processes waiting for ever"),
              ("The fix", "Critical sections guarded by P and V"),
              ("Checked", f"{mx['states']} states for three processes, none unsafe")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Semaphores.java`.",
    )
