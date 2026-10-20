"""Era 8, topic 8: Paxos. Every number is parsed from Paxos.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"exhaustive: .*? ; ([\d,]+) reachable states, ([\d,]+) steps between them ; a value is chosen in ([\d,]+) of the states ; two different values chosen: in none", ln):
            d["ex"] = dict(states=m.group(1), steps=m.group(2), chosen=m.group(3))
        elif m := re.match(r"broken: .*? two values chosen after (\d+) steps \(found among ([\d,]+) states\) ; (.*)$", ln):
            d["broken"] = dict(n=m.group(1), states=m.group(2), trace=m.group(3).split(" ; "))
        elif m := re.match(r"quorum: .*? two values chosen after (\d+) steps ; (.*)$", ln):
            d["quorum"] = dict(n=m.group(1), trace=m.group(2).split(" ; "))
        elif m := re.match(r"random: ([\d,]+) runs, (\d+) acceptors, (\d+) proposers with up to (\d+) ballots each, (\d+)% of messages lost, .*? 2 acceptors crashing in ([\d,]+) of the runs ; two values chosen: never ; a value chosen in ([\d,]+) runs \(([\d.]+)%\), after (\d+) steps on average", ln):
            d["random"] = dict(runs=m.group(1), acc=m.group(2), prop=m.group(3), ballots=m.group(4), loss=m.group(5), crash=m.group(6), decided=m.group(7), pct=m.group(8), steps=m.group(9))
        elif m := re.match(r"duel: .*? after (\d+) ballots each, nothing is chosen.*? ; with P1 alone as leader: chosen in its first ballot, (\d) of 3 acceptors voting", ln):
            d["duel"] = dict(n=m.group(1), votes=m.group(2))
        elif m := re.match(r"widget: (rule kept|rule broken) ; (.*) ; chosen: \[(.*)\]$", ln):
            d.setdefault("widget", {})[m.group(1)] = dict(steps=m.group(2).split(" ; "), chosen=m.group(3))
    d["checks"] = C.checks(text)
    return d


def replay(steps):
    """Turn the program's step descriptions into a list of states for the widget."""
    acc = [dict(promised=0, vote=None) for _ in range(3)]
    prop = {1: dict(ballot=0, promises=[], value=None), 2: dict(ballot=0, promises=[], value=None)}
    votes = {}   # ballot -> (value, set of acceptors)
    states = []
    for s in steps:
        if m := re.match(r"P(\d) sends prepare\((\d)\)", s):
            prop[int(m.group(1))].update(ballot=int(m.group(2)), promises=[], value=None)
        elif m := re.match(r"acceptor (\d) promises ballot (\d)", s):
            acc[int(m.group(1)) - 1]["promised"] = int(m.group(2))
        elif m := re.match(r"P(\d) receives acceptor (\d)'s promise for ballot (\d)( and sends accept\(\d, ([AB])\))?", s):
            p = prop[int(m.group(1))]
            p["promises"] = p["promises"] + [int(m.group(2))]
            if m.group(5):
                p["value"] = m.group(5)
        elif m := re.match(r"acceptor (\d) votes \((\d), ([AB])\)", s):
            a, b, v = int(m.group(1)), int(m.group(2)), m.group(3)
            acc[a - 1].update(promised=b, vote=[b, v])
            votes.setdefault(b, [v, []])[1].append(a)
        else:
            raise ValueError(s)
        chosen = sorted({v for b, (v, who) in votes.items() if len(who) >= 2})
        states.append(dict(step=s, acc=json.loads(json.dumps(acc)), prop=json.loads(json.dumps(prop)), chosen=chosen))
    return states


# ----------------------------------------------------------------------------------------------------------------------
def overlap_svg(d):
    def draw(t, standalone):
        o = []
        W, H = 760, 250
        o.append(C.text(20, 26, "Why majorities: any two of them share an acceptor, who carries the earlier vote forward", t["ink"], 13, "start", 700))
        xs = [190, 380, 570]
        for i, x in enumerate(xs):
            o.append(C.rect(x - 55, 110, 110, 60, t["surface"], t["ink"], 2))
            o.append(C.text(x, 136, f"acceptor {i + 1}", t["ink"], 13, "middle", 700))
            o.append(C.text(x, 156, "voted (1, A)" if i < 2 else "", t["red"], 12, "middle"))
        o.append(C.rect(120, 92, 330, 96, "none", t["red"], 2.2, 8, ";stroke-dasharray:7 4"))
        o.append(C.text(130, 84, "ballot 1's majority: chose A", t["red"], 12.5, "start", 700))
        o.append(C.rect(310, 100, 330, 80, "none", t["blue"], 2.2, 8, ";stroke-dasharray:3 3"))
        o.append(C.text(630, 200, "ballot 2's majority of promises", t["blue"], 12.5, "end", 700))
        o.append(C.text(20, 228, "Acceptor 2 is in both. Its promise to ballot 2 reports its vote (1, A), so ballot 2 must propose A again.", t["ink"], 12.5))
        return C.svg_doc(W, H, "".join(o), "Two overlapping majorities of three acceptors", t, standalone, 0.55, 760)
    return draw


PX_HTML = """
<div class="board px-board">
  <div style="min-width:0"><div class="px-view" id="px-view"></div></div>
  <div style="min-width:0">
    <div class="px-btns" role="group" aria-label="Rule"><button type="button" id="px-keep" class="on">Rule kept</button><button type="button" id="px-break">Rule broken</button></div>
    <div class="px-btns"><button type="button" class="primary" id="px-next">Next step</button><button type="button" id="px-back">Back</button><button type="button" id="px-reset">Start again</button></div>
    <ol class="steps px-steps" id="px-steps"></ol>
    <p class="say" id="px-say" aria-live="polite"></p>
  </div>
</div>
"""

PX_CSS = """
.px-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.px-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.px-btns button.on{background:var(--ink);color:var(--paper)}
.px-steps{font-size:12.5px;max-height:260px;overflow:auto}
.px-steps li{padding:2px 4px}
"""

PX_JS = r"""
(() => {
  const view = document.getElementById("px-view");
  if (!view) return;
  const RUNS = __RUNS__;
  let rule = "rule kept", k = 0;
  function draw() {
    const run = RUNS[rule], st = k > 0 ? run.states[k - 1] : null;
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 460 300", role: "img", "aria-label": "Two proposers and three acceptors"}, view);
    const P = {1: [90, 50], 2: [370, 50]}, A = [[90, 210], [230, 210], [370, 210]];
    for (const p of [1, 2]) {
      const s = st ? st.prop[p] : {ballot: 0, promises: [], value: null};
      sv("rect", {x: P[p][0] - 70, y: P[p][1] - 30, width: 140, height: 62, fill: "var(--surface)", stroke: p === 1 ? "var(--red)" : "var(--blue)", "stroke-width": 2}, svg);
      sv("text", {x: P[p][0], y: P[p][1] - 10, "text-anchor": "middle", "font-size": 14, "font-weight": 700, fill: "var(--ink)"}, svg, `P${p} (own value ${p === 1 ? "A" : "B"})`);
      sv("text", {x: P[p][0], y: P[p][1] + 8, "text-anchor": "middle", "font-size": 12, fill: "var(--ink-2)"}, svg, s.ballot ? `ballot ${s.ballot}, promises ${s.promises.length}` : "idle");
      sv("text", {x: P[p][0], y: P[p][1] + 24, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg, s.value ? `sent accept(${s.ballot}, ${s.value})` : "");
    }
    A.forEach(([x, y], i) => {
      const a = st ? st.acc[i] : {promised: 0, vote: null};
      const v = a.vote ? a.vote[1] : null;
      sv("rect", {x: x - 58, y: y - 32, width: 116, height: 64, fill: v === "A" ? "var(--red)" : v === "B" ? "var(--blue)" : "var(--surface)", "fill-opacity": v ? 0.25 : 1, stroke: "var(--ink)", "stroke-width": 1.5}, svg);
      sv("text", {x, y: y - 12, "text-anchor": "middle", "font-size": 13, "font-weight": 700, fill: "var(--ink)"}, svg, `acceptor ${i + 1}`);
      sv("text", {x, y: y + 6, "text-anchor": "middle", "font-size": 12, fill: "var(--ink-2)"}, svg, `promised ${a.promised || "–"}`);
      sv("text", {x, y: y + 22, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg, a.vote ? `voted (${a.vote[0]}, ${a.vote[1]})` : "no vote");
    });
    if (st) {
      const m = st.step.match(/^(P\d|acceptor \d)/), who = m ? m[1] : "";
      const at = who.startsWith("P") ? P[+who[1]] : A[+who.slice(-1) - 1];
      sv("circle", {cx: at[0] + 62, cy: at[1] - 28, r: 7, fill: "var(--yellow)"}, svg);
    }
    const ch = st ? st.chosen : [];
    sv("text", {x: 230, y: 290, "text-anchor": "middle", "font-size": 14, "font-weight": 700, fill: ch.length > 1 ? "var(--red)" : "var(--ink)"}, svg,
       ch.length === 0 ? "nothing chosen yet" : ch.length === 1 ? `chosen: ${ch[0]}` : `chosen: ${ch.join(" and ")}: agreement broken`);
    const ol = document.getElementById("px-steps"); ol.innerHTML = "";
    run.states.forEach((s, i) => el("li", {class: i === k - 1 ? "current" : i >= k ? "pending" : ""}, ol, s.step));
    const say = document.getElementById("px-say");
    if (k === run.states.length) say.textContent = rule === "rule kept"
      ? `P2's promises included acceptor 1's vote (1, A), so P2 proposed A. Every majority that votes chooses A. The program: chosen ${run.chosen}.`
      : `P2 ignored the reported vote and proposed its own B. Acceptors 1 and 2 voted A in ballot 1, acceptors 3 and 1 voted B in ballot 2: two values chosen. The program: chosen ${run.chosen}.`;
    else say.textContent = k ? st.step + "." : "Two proposers, three acceptors. Press Next step to follow the program's scripted run.";
  }
  document.getElementById("px-next").addEventListener("click", () => { if (k < RUNS[rule].states.length) k++; draw(); });
  document.getElementById("px-back").addEventListener("click", () => { if (k > 0) k--; draw(); });
  document.getElementById("px-reset").addEventListener("click", () => { k = 0; draw(); });
  const keep = document.getElementById("px-keep"), brk = document.getElementById("px-break");
  keep.addEventListener("click", () => { rule = "rule kept"; k = 0; keep.classList.add("on"); brk.classList.remove("on"); draw(); });
  brk.addEventListener("click", () => { rule = "rule broken"; k = 0; brk.classList.add("on"); keep.classList.remove("on"); draw(); });
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Paxos combined older ideas, and where it led")
    W = 210
    nodes = {
        "byz": (20, 20, "The Byzantine generals", "agreement despite traitors, in rounds", "Era 7", "ink"),
        "flp": (395, 20, "FLP impossibility", "no deterministic protocol always decides", "Fischer, Lynch, Paterson", "ink"),
        "clk": (770, 20, "Logical clocks", "order events without a shared clock", "Lamport; Era 6", "ink"),
        "px": (395, 180, "Paxos", "⊕ numbered ballots and overlapping majorities", "Lamport; published 1998", "red"),
        "vr": (20, 340, "Viewstamped replication", "a similar protocol", "Oki and Liskov, 1988", "ink"),
        "simple": (770, 340, "Paxos Made Simple", "the algorithm in plain English", "Lamport, 2001", "ink"),
        "today": (395, 490, "Today", "Chubby, Spanner, Megastore and more", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("byz", "px", ports=("bottom", "top:0.15"))
    D.edge("flp", "px", ports=("bottom", "top"), label="safety always, progress not", at=0.5, dx=8, anchor="start")
    D.edge("clk", "px", ports=("bottom", "top:0.85"))
    D.edge("px", "vr", ports=("bottom:0.15", "top"), label="a contemporary", at=0.45, dx=-8, anchor="end")
    D.edge("px", "simple", ports=("bottom:0.85", "top"))
    D.edge("px", "today", ports=("bottom", "top"))
    D.text(20, 615, "Viewstamped replication was published in 1988, before Paxos appeared in print; Today: the systems Wikipedia names.", "caption")
    return D


def chain(d):
    b, du = d["broken"], d["duel"]
    steps = [
        ("Messages are lost or late, and a stopped computer looks like a slow one",
         "Numbered ballots; a value is chosen when a majority votes for it", "Lamport"),
        ("A later ballot could choose a different value",
         f"Promise first, and repropose the highest vote reported; break that rule and two values are chosen in {b['n']} steps", "the rule the program checks"),
        (f"Two proposers can pre-empt each other forever: {du['n']} ballots each, nothing chosen",
         "One distinguished proposer at a time", "Paxos Made Simple, 2001"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from lost messages to one leader")
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
    ex, br, q, rn, du, wg = d["ex"], d["broken"], d["quorum"], d["random"], d["duel"], d["widget"]
    runs = {k: dict(states=replay(v["steps"]), chosen=v["chosen"]) for k, v in wg.items()}
    assert runs["rule kept"]["states"][-1]["chosen"] == ["A"] and runs["rule broken"]["states"][-1]["chosen"] == ["A", "B"]
    br_rows = [[str(i + 1), s] for i, s in enumerate(br["trace"])]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The Byzantine generals (Era 7) agreed in lockstep rounds. Fischer, Lynch and Paterson had shown that without timing assumptions no deterministic protocol can promise to decide. Lamport's Paxos gives up the promise to decide, and keeps the promise never to decide two different things: numbered ballots and majorities that must overlap. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Paxos. Blue: the systems that use it."),
        ]),
        dict(id="play", eyebrow="Try it", title="One rule between agreement and chaos", toc="Try it", blocks=[
            dict(type="p", text="Two proposers, P1 (wanting A) and P2 (wanting B), and three acceptors, following a run the program checked step by step. P1 gets promises from acceptors 1 and 2 and sends accept(1, A); only acceptor 1 votes before P2 starts ballot 2. Acceptor 1's promise to P2 reports that vote. With the rule kept, P2 must propose A; switch to the broken rule and P2 proposes its own B, and two different values end up chosen."),
            dict(type="widget", html=PX_HTML, js=PX_JS.replace("__RUNS__", json.dumps(runs)), css=PX_CSS,
                 fallback=dict(type="table", head=["Step", "Rule kept", "Rule broken"], num=[0],
                               rows=[[str(i + 1), a, b] for i, (a, b) in enumerate(zip(wg["rule kept"]["steps"], wg["rule broken"]["steps"]))] + [["chosen", wg["rule kept"]["chosen"], wg["rule broken"]["chosen"]]]),
                 note="In the interactive edition you can step through both runs and watch the acceptors' promises and votes."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Promise, then accept", toc="How it works", blocks=[
            dict(type="p", text="**Roles.** Proposers suggest values; acceptors vote; a value is *chosen* once a majority of acceptors have voted for it in the same numbered ballot. Messages may be delayed, repeated or lost; computers may stop; nothing is assumed about timing."),
            dict(type="p", text="**Phase 1.** The proposer of ballot n sends prepare(n). An acceptor that has not promised anything higher promises to ignore every ballot below n, and reports the last vote it cast, if any."),
            dict(type="p", text="**Phase 2.** With promises from a majority, the proposer sends accept(n, v), and here is the rule: v must be the value of the highest-numbered vote reported to it. Only if nobody reported a vote may it use its own value. An acceptor votes for (n, v) unless it has promised a higher ballot."),
            dict(type="svg", name="overlap", draw=overlap_svg(d), alt="Two overlapping majorities of three acceptors", width=760),
            dict(type="p", text="**Why it is safe.** If v was chosen in ballot m, a majority voted for it. Any later ballot's majority of promises overlaps that majority in at least one acceptor, which reports a vote of ballot m or later; by induction that vote is for v, so the later ballot proposes v again. **Why it may not finish.** Two proposers can keep pre-empting each other with higher ballots; in practice one proposer at a time acts as leader."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Separate safety from progress. Safety (never two values) holds whatever the timing, because majorities overlap and each ballot inherits the highest earlier vote. Progress needs only a period in which one leader can talk to a majority."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Every state, checked", toc="Measured", blocks=[
            dict(type="p", text=f"**Exhaustive search.** Two proposers (P1 with ballots 1 and 3 and value A, P2 with ballot 2 and value B) and three acceptors. Every message stays in the network and may be delivered at any moment, again and again, which covers delay, repetition and loss. The search visited all {ex['states']} reachable states and the {ex['steps']} steps between them; a value is chosen in {ex['chosen']} of the states, and in none are two different values chosen."),
            dict(type="p", text=f"**The rule broken.** If a proposer always uses its own value, the same search finds two values chosen after {br['n']} steps (the shortest such run, among {br['states']} states):"),
            dict(type="table", head=["Step", "What happens"], num=[0], rows=br_rows),
            dict(type="p", text=f"**Quorums that need not overlap.** With the rule kept but a \"majority\" of 1 acceptor, two values are chosen after {q['n']} steps."),
            dict(type="p", text=f"**Random runs.** {rn['runs']} runs with {rn['acc']} acceptors and {rn['prop']} proposers with up to {rn['ballots']} ballots each, {rn['loss']}% of messages lost, messages delivered in random order and sometimes twice, and 2 acceptors crashing in {rn['crash']} of the runs: two values were never chosen; a value was chosen in {rn['decided']} runs ({rn['pct']}%), after {rn['steps']} steps on average."),
            dict(type="p", text=f"**Duelling proposers.** If each prepare arrives just before the other proposer's accept, every accept is refused: after {du['n']} ballots each nothing is chosen, and the schedule can go on forever. With P1 alone as leader, its first ballot is chosen, with {du['votes']} of 3 acceptors voting."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A parliament on a Greek island", toc="The evidence", blocks=[
            dict(type="p", text="Lamport's commentary: the paper was \"first submitted in 1990, setting a personal record for publication delay\"; \"All three referees said that the paper was mildly interesting, though not very important\"; it appeared in *ACM Transactions on Computer Systems* 16(2), May 1998, with notes by Keith Marzullo; Leo Guibas suggested the name; it won an ACM SIGOPS Hall of Fame Award in 2012. Wikipedia says it was \"first submitted in 1989\": the year is **disputed**. The published paper begins \"Recent archaeological discoveries on the island of Paxos\", and Marzullo's note says it \"was recently discovered behind a filing cabinet in the TOCS editorial office\"."),
            dict(type="p", text="\"Paxos Made Simple\" (1 November 2001): \"The Paxos algorithm, when presented in plain English, is very simple\"; \"Because any two majorities have at least one acceptor in common, this works if an acceptor can accept at most one value\"; a prepare request brings \"a promise not to accept any more proposals numbered less than n\", and the accept request carries \"the value of the highest-numbered proposal among the responses\". Two proposers can keep issuing higher numbers, so \"a distinguished proposer must be selected\", and by Fischer, Lynch and Paterson that choice \"must use either randomness or real time\". Wikipedia: \"Paxos guarantees safety (consistency)\" but \"is not guaranteed to terminate\"; it runs in Google's Chubby, Spanner and Megastore, among others."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The generals, without the drumbeat", toc="Full circle", blocks=[
            dict(type="p", text="The Byzantine generals (Era 7) tolerated liars but needed rounds. Paxos tolerates only crashes, not lies, but needs no rounds at all. Bitcoin (topic 13) will tolerate liars without rounds, among strangers, by a different trade: it gives up certainty for a probability that shrinks block by block."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"{ex['states']} states, every interleaving of every message, and never two values. Change one rule, repropose the highest vote, and the same search finds a disagreement in {br['n']} steps."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With 5 acceptors, how many must vote for a value to choose it, and how many can crash without stopping progress?", "A majority, 3; up to 2 can crash, since 2f + 1 = 5 tolerates f = 2."),
            ("An acceptor promised ballot 7. It receives accept(5, A). What does it do?", "Ignores it: it promised not to accept anything numbered below 7."),
            ("A proposer gets promises reporting votes (2, A) and (4, B). What must it propose?", "B, the value of the highest-numbered vote."),
            ("Why can a value never be 'unchosen' by a later ballot?", "Any later majority of promises includes an acceptor that voted in the choosing majority, and the reported highest vote carries the chosen value forward."),
            ("Why does Paxos not promise to decide?", "Fischer, Lynch and Paterson proved no deterministic protocol can in a fully asynchronous network; duelling proposers are the concrete way it fails."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Part-Time Parliament (1998)", text="*ACM Transactions on Computer Systems* 16(2): the parliament of Paxos and its proofs.",
                 draw=C.draw_manuscript, link="https://www.cs.princeton.edu/courses/archive/spring13/cos598C/lamport-paxos.pdf", link_text="The paper (PDF, on a Princeton course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Paxos", d["checks"],
                           "every reachable state of the small system, the shortest violations with the rule broken, 20,000 random runs with losses and crashes, and the widget's two scripted runs.",
                           ["static List<Object[]> successors(S s, boolean keepRule, int quorum)"]),
    ]
    return dict(
        title="Paxos", date="1989–1998",
        description="Era 8, topic 8 of The Algorithm Evolution Atlas: Lamport's Paxos, the part-time parliament, checked by exhaustive search over every interleaving of a small system and by 20,000 random runs with lost messages and crashes.",
        lede="Several computers must agree on one value, though messages are delayed, repeated or lost and a stopped computer looks like a slow one. Lamport's Paxos never lets two values be chosen, whatever the timing: ballots are numbered, majorities overlap, and every ballot repropose the highest vote it hears of.",
        fieldnote=f"I let a small Paxos run every way it could: {ex['states']} states, messages delivered late, early, twice or never. Not once were two values chosen. Then I took away one rule, that a proposer must repropose the highest vote it is told of, and the same search found a disagreement in {br['n']} steps.",
        card=[("When", "Written and submitted 1989 or 1990; published May 1998"),
              ("Where", "Lamport, at the Systems Research Center (SRC)"),
              ("What hurt", "Replicas must agree through lost messages and stopped computers"),
              ("The fix", "Numbered ballots, promise then accept, overlapping majorities"),
              ("Checked", f"{ex['states']} states, never two values")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Paxos.java`.",
    )
