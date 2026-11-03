"""Era 9, topic 4: Raft. Every number is parsed from Raft.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"chaos: (\d+) runs of ([\d,]+) simulated ms, (\d+) servers, (\d+)% of messages lost, delays (\d+) to (\d+) ms.*? ; ([\d,]+) elections, ([\d,]+) leaders elected, ([\d,]+) ended by a timeout without a winner ; ([\d,]+) entries committed ; no leader ([\d.]+)% of the time ; safety violations: (\d+)", ln):
            d["chaos"] = dict(zip(["runs", "ms", "n", "loss", "dmin", "dmax", "elections", "leaders", "nowin", "committed", "noleader", "viol"], m.groups()))
        elif ln.startswith("timeouts: "):
            d["timeouts"] = re.findall(r"(random 150-300 ms|fixed 150 ms): median (\d+) ms, slowest (over 100 s|\d+ ms), (\d+) of 200 still without a leader after 100 s, ([\d,]+) elections ended", ln)
        elif m := re.match(r"broken: .*? the same (\d+) runs: (\d+) with a safety violation ; first in run (\d+): (.*)$", ln):
            d["broken"] = m.groups()
        elif ln.startswith("story: "):
            parts = ln.split(" ; ")
            d["events"] = [p for p in parts if re.match(r"\d+ ms: ", p)]
            d["entries"] = re.search(r"holds the same (\d+) entries", ln).group(1)
            d["logs"] = re.findall(r"(S\d) term (\d+) commit (\d+) log ([\d:,]+)", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def story_svg(d):
    def draw(t, standalone):
        W = 760
        H = 56 + 20 * len(d["events"]) + 16 + 34 * len(d["logs"]) + 30
        o = [C.text(20, 26, "The program's scripted run: who leads, and what every log holds at the end", t["ink"], 13, "start", 700)]
        y = 56
        for e in d["events"]:
            o.append(C.text(30, y, e, t["ink"], 12))
            y += 20
        y0 = y + 16
        term_col = {"1": t["blue"], "2": t["red"], "3": t["yellow"]}
        for k, (s, term, commit, log) in enumerate(d["logs"]):
            yy = y0 + k * 34
            o.append(C.text(30, yy + 17, s, t["ink"], 13, "start", 700))
            for i, ent in enumerate(log.split(",")):
                tm, cmd = ent.split(":")
                x = 70 + i * 52
                o.append(C.rect(x, yy, 46, 26, t["paper"], term_col.get(tm, t["muted"]), 2, 3))
                o.append(C.text(x + 23, yy + 17, f"{tm}:{cmd}", t["ink"], 11, "middle"))
        o.append(C.text(20, H - 10, "Each box is one entry, term:command. Blue outlines: written in term 1; red: term 2. Every server ends with the same log.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Raft scripted run: leaders, a crash, and five identical logs", t, standalone, 0.55, 760)
    return draw


RAFT_HTML = """
<div class="board raft-board">
  <div style="min-width:0"><div class="raft-view" id="raft-view"></div></div>
  <div style="min-width:0">
    <div class="raft-btns">
      <button type="button" class="primary" id="raft-run">Run</button>
      <button type="button" id="raft-step">+100 ms</button>
      <button type="button" id="raft-cmd">Client command</button>
      <button type="button" id="raft-crash">Crash the leader</button>
      <button type="button" id="raft-restart">Restart crashed</button>
      <button type="button" id="raft-reset">Start over</button>
    </div>
    <label class="raft-opt"><input type="checkbox" id="raft-fixed"> fixed 150 ms timeouts instead of random 150–300 ms</label>
    <div class="raft-ev" id="raft-ev"></div>
    <p class="say" id="raft-say" aria-live="polite"></p>
  </div>
</div>
"""

RAFT_CSS = """
.raft-board{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.raft-board{grid-template-columns:1fr}}
.raft-view svg{width:100%;height:auto;display:block;background:var(--wash)}
.raft-view g.srv{cursor:pointer}
.raft-btns{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 8px}
.raft-opt{font-size:13px;display:block;margin:4px 0 8px}
.raft-ev{font:12.5px var(--mono);display:grid;gap:2px;min-height:6.5em}
"""

RAFT_JS = r"""
(() => {
  const view = document.getElementById("raft-view");
  if (!view) return;
  const N = 5, HB = 50, DMIN = 10, DMAX = 30, TCOL = ["var(--blue)", "var(--red)", "var(--yellow)", "var(--ink)", "var(--muted)"];
  let S, net, now, seed, cmdNo, events, timer = null;
  const rnd = () => { seed = (seed + 0x6D2B79F5) | 0; let t = seed; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const fixed = () => document.getElementById("raft-fixed").checked;
  const timeout = () => fixed() ? 150 : 150 + Math.floor(rnd() * 151);
  const lastTerm = s => s.log.length ? s.log[s.log.length - 1].t : 0, termAt = (s, i) => i === 0 ? 0 : s.log[i - 1].t;
  const note = m => { events.unshift(`${String(now).padStart(5)} ms  ${m}`); events = events.slice(0, 6); };
  function reset() {
    seed = 7; now = 0; cmdNo = 1; net = []; events = [];
    S = [...Array(N)].map((_, i) => ({id: i, term: 0, voted: -1, role: "follower", commit: 0, log: [], deadline: timeout(), beat: 0, next: Array(N).fill(1), match: Array(N).fill(0), votes: new Set(), up: true}));
  }
  function send(m) { m.sent = now; m.at = now + DMIN + Math.floor(rnd() * (DMAX - DMIN + 1)); net.push(m); }
  function follow(s, term) { if (term > s.term) { s.term = term; s.voted = -1; } s.role = "follower"; }
  function elect(s) {
    s.role = "candidate"; s.term++; s.voted = s.id; s.votes = new Set([s.id]); s.deadline = now + timeout();
    note(`S${s.id + 1} times out, stands for term ${s.term}`);
    for (let j = 0; j < N; j++) if (j !== s.id) send({k: "RV", from: s.id, to: j, term: s.term, a: s.log.length, b: lastTerm(s)});
  }
  function append(s, j) {
    const p = s.next[j] - 1;
    send({k: "AE", from: s.id, to: j, term: s.term, a: p, b: termAt(s, p), e: s.log.slice(p), c: s.commit});
  }
  function deliver(m) {
    const s = S[m.to];
    if (!s.up) return;
    if (m.term > s.term) follow(s, m.term);
    if (m.k === "RV") {
      const ok = m.b > lastTerm(s) || (m.b === lastTerm(s) && m.a >= s.log.length);
      const g = m.term === s.term && (s.voted === -1 || s.voted === m.from) && ok;
      if (g) { s.voted = m.from; s.deadline = now + timeout(); }
      send({k: "RVR", from: s.id, to: m.from, term: s.term, a: g});
    } else if (m.k === "RVR") {
      if (s.role === "candidate" && m.term === s.term && m.a) {
        s.votes.add(m.from);
        if (s.votes.size > N / 2) {
          s.role = "leader"; s.next.fill(s.log.length + 1); s.match.fill(0); s.beat = now;
          note(`S${s.id + 1} wins ${s.votes.size} votes: leader of term ${s.term}`);
        }
      }
    } else if (m.k === "AE") {
      if (m.term < s.term) { send({k: "AER", from: s.id, to: m.from, term: s.term, a: false}); return; }
      s.role = "follower"; s.deadline = now + timeout();
      if (m.a > s.log.length || termAt(s, m.a) !== m.b) { send({k: "AER", from: s.id, to: m.from, term: s.term, a: false}); return; }
      m.e.forEach((e, k) => {
        const idx = m.a + 1 + k;
        if (idx <= s.log.length && s.log[idx - 1].t !== e.t) s.log.length = idx - 1;
        if (idx > s.log.length) s.log.push(e);
      });
      const last = m.a + m.e.length;
      if (m.c > s.commit) s.commit = Math.min(m.c, last);
      send({k: "AER", from: s.id, to: m.from, term: s.term, a: true, b: last});
    } else if (m.k === "AER") {
      if (s.role !== "leader" || m.term !== s.term) return;
      if (m.a) {
        s.match[m.from] = Math.max(s.match[m.from], m.b); s.next[m.from] = s.match[m.from] + 1;
        for (let n = s.log.length; n > s.commit; n--) {
          if (s.log[n - 1].t !== s.term) break;
          let c = 1; for (let j = 0; j < N; j++) if (j !== s.id && s.match[j] >= n) c++;
          if (c > N / 2) { note(`entries up to ${n} committed: stored on ${c} of 5`); s.commit = n; break; }
        }
      } else s.next[m.from] = Math.max(1, s.next[m.from] - 1);
    }
  }
  function tick() {
    net.sort((p, q) => p.at - q.at);
    while (net.length && net[0].at <= now) deliver(net.shift());
    S.forEach(s => {
      if (!s.up) return;
      if (s.role === "leader") { if (now >= s.beat) { for (let j = 0; j < N; j++) if (j !== s.id) append(s, j); s.beat = now + HB; } }
      else if (now >= s.deadline) elect(s);
    });
    now++;
  }
  const leader = () => S.filter(s => s.up && s.role === "leader").sort((a, b) => b.term - a.term)[0];
  const pos = i => [200 + 130 * Math.cos(-Math.PI / 2 + i * 2 * Math.PI / N), 165 + 130 * Math.sin(-Math.PI / 2 + i * 2 * Math.PI / N)];
  function draw() {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 640 500", role: "img", "aria-label": "Five Raft servers, the messages between them, and their logs"}, view);
    sv("text", {x: 400, y: 30, "font-size": 13, "font-weight": 700, fill: "var(--ink)"}, svg, `time ${now} ms`);
    const L = leader();
    sv("text", {x: 400, y: 50, "font-size": 12, fill: "var(--muted)"}, svg, L ? `leader S${L.id + 1}, term ${L.term}` : "no leader");
    net.forEach(m => {
      const [x1, y1] = pos(m.from), [x2, y2] = pos(m.to), f = Math.min(1, Math.max(0, (now - m.sent) / (m.at - m.sent)));
      const vote = m.k === "RV" || m.k === "RVR";
      sv("circle", {cx: x1 + (x2 - x1) * f, cy: y1 + (y2 - y1) * f, r: m.k.endsWith("R") ? 3 : 5, fill: vote ? "var(--yellow)" : "var(--blue)", stroke: "var(--ink)", "stroke-width": 0.6}, svg);
    });
    S.forEach((s, i) => {
      const [x, y] = pos(i), g = sv("g", {class: "srv", id: `raft-s${i + 1}`}, svg);
      const fill = !s.up ? "var(--paper)" : s.role === "leader" ? "var(--blue)" : s.role === "candidate" ? "var(--yellow)" : "var(--paper)";
      sv("circle", {cx: x, cy: y, r: 30, fill, stroke: s.up ? "var(--ink)" : "var(--muted)", "stroke-width": 2, "stroke-dasharray": s.up ? "none" : "4 3"}, g);
      if (s.up && s.role !== "leader") {
        const left = Math.max(0, s.deadline - now) / 300, a = 2 * Math.PI * Math.min(1, left);
        sv("path", {d: `M${x} ${y - 36} A36 36 0 ${a > Math.PI ? 1 : 0} 1 ${x + 36 * Math.sin(a)} ${y - 36 * Math.cos(a)}`, fill: "none", stroke: "var(--muted)", "stroke-width": 3}, g);
      }
      sv("text", {x, y: y - 2, "text-anchor": "middle", "font-size": 14, "font-weight": 700, fill: s.role === "leader" && s.up ? "var(--paper)" : "var(--ink)"}, g, `S${i + 1}`);
      sv("text", {x, y: y + 14, "text-anchor": "middle", "font-size": 11, fill: s.role === "leader" && s.up ? "var(--paper)" : "var(--ink)"}, g, s.up ? `term ${s.term}` : "crashed");
      g.addEventListener("click", () => { if (s.up) { s.up = false; note(`S${i + 1} crashes`); } else restart(s); draw(); });
    });
    sv("text", {x: 20, y: 342, "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg, "Logs (term:command; solid = committed)");
    S.forEach((s, i) => {
      const y = 354 + i * 28;
      sv("text", {x: 20, y: y + 16, "font-size": 12, "font-weight": 700, fill: "var(--ink)"}, svg, `S${i + 1}`);
      s.log.slice(-14).forEach((e, k) => {
        const idx = Math.max(0, s.log.length - 14) + k, c = idx < s.commit, col = TCOL[(e.t - 1) % TCOL.length];
        sv("rect", {x: 52 + k * 41, y, width: 37, height: 22, rx: 3, fill: c ? col : "var(--paper)", stroke: col, "stroke-width": 1.6, "fill-opacity": c ? 0.35 : 1}, svg);
        sv("text", {x: 70 + k * 41, y: y + 15, "text-anchor": "middle", "font-size": 10, fill: "var(--ink)"}, svg, `${e.t}:${e.c}`);
      });
    });
    const ev = document.getElementById("raft-ev"); ev.innerHTML = ""; events.forEach(e => el("div", {}, ev, e));
  }
  function restart(s) { s.up = true; s.role = "follower"; s.commit = 0; s.deadline = now + timeout(); note(`S${s.id + 1} restarts with its term, vote and log`); }
  function say(t) { document.getElementById("raft-say").textContent = t; }
  function run(ms) { for (let k = 0; k < ms; k++) tick(); draw(); }
  const runBtn = document.getElementById("raft-run");
  function stop() { if (timer) { clearInterval(timer); timer = null; runBtn.textContent = "Run"; } }
  runBtn.addEventListener("click", () => { if (timer) stop(); else { timer = setInterval(() => run(2), 40); runBtn.textContent = "Pause"; } });
  document.getElementById("raft-step").addEventListener("click", () => run(100));
  document.getElementById("raft-cmd").addEventListener("click", () => {
    const L = leader();
    if (!L) { say("No leader right now: a client would retry until one is elected."); return; }
    L.log.push({t: L.term, c: cmdNo}); note(`client: command ${cmdNo} to leader S${L.id + 1}`); cmdNo++;
    say("The leader appended the command to its own log. It is committed once a majority of the five stores it; watch the blue messages carry it."); draw();
  });
  document.getElementById("raft-crash").addEventListener("click", () => {
    const L = leader();
    if (!L) { say("There is no leader to crash."); return; }
    L.up = false; note(`S${L.id + 1} crashes`);
    say(`S${L.id + 1} is down. The others stop hearing heartbeats; the first whose election timer (the grey arc) runs out stands for the next term.`); draw();
  });
  document.getElementById("raft-restart").addEventListener("click", () => { S.filter(s => !s.up).forEach(restart); say("Restarted servers come back as followers and catch up from the leader."); draw(); });
  document.getElementById("raft-reset").addEventListener("click", () => { stop(); reset(); run(400); say("A fresh cluster, run for 400 ms. Press Run, or send a command."); });
  reset(); run(400);
  say("Click a server to crash or restart it. Yellow dots are votes, blue dots are AppendEntries; time runs 25 times slower than real.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How Raft combined older ideas, and where it led")
    W = 250
    nodes = {
        "paxos": (40, 20, "Paxos", "agreement in spite of loss and crashes, hard to explain", "Era 8, topic 8", "ink"),
        "rand": (375, 20, "Randomized timeouts", "break the symmetry between candidates", "", "ink"),
        "log": (710, 20, "Replicated log", "the same commands in the same order on every server", "", "ink"),
        "raft": (375, 200, "Raft", "⊕ a strong leader, terms, and five safety rules", "Ongaro and Ousterhout, Stanford, 2014", "red"),
        "study": (40, 380, "A user study", "43 students, quizzes on Raft and Paxos", "the same paper", "blue"),
        "scope": (710, 380, "RaftScope", "an interactive cluster on the Raft site", "raft.github.io", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("paxos", "raft", ports=("bottom", "top:0.15"))
    D.edge("rand", "raft", ports=("bottom", "top"))
    D.edge("log", "raft", ports=("bottom", "top:0.85"))
    D.edge("raft", "study", ports=("bottom:0.15", "top"))
    D.edge("raft", "scope", ports=("bottom:0.85", "top"))
    return D


def chain():
    steps = [
        ("Paxos was correct, and almost nobody could explain it or build it as written",
         "Design for understanding: one leader, and the problem split in three", "Ongaro and Ousterhout, 2014"),
        ("Candidates that time out together split the vote, again and again",
         "Random election timeouts, 150 to 300 ms", "the same paper"),
        ("A new leader might lack entries that were already committed",
         "Vote only for candidates whose log is at least as up to date as yours", "the same paper"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from Paxos to Raft")
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
    ch, br = d["chaos"], d["broken"]
    to = {k: dict(median=a, slowest=b, stuck=c, nowin=e) for k, a, b, c, e in d["timeouts"]}
    r, f = to["random 150-300 ms"], to["fixed 150 ms"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Paxos (Era 8) let a group of computers agree on one history in spite of lost messages and crashes. Diego Ongaro and John Ousterhout kept the goal and changed the design: one strong leader per numbered term, elections broken up by random timeouts, and a log that flows only from the leader outwards."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Raft. Blue: how its authors tested and taught it."),
        ]),
        dict(id="play", eyebrow="Try it", title="A cluster to break", toc="Try it", blocks=[
            dict(type="p", text="Five servers run the same rules as the program, 25 times slower than real time. Send client commands, crash the leader and watch an election; click any server to crash or restart it. Tick the box to give every server the same fixed timeout and watch candidates split the vote."),
            dict(type="widget", html=RAFT_HTML, js=RAFT_JS, css=RAFT_CSS,
                 fallback=dict(type="svg", name="story", draw=story_svg(d), alt="A scripted Raft run: leaders, a crash and the final logs", width=760),
                 note="In the interactive edition the cluster runs in your browser, and you can crash servers yourself."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Terms, votes and one log", toc="How it works", blocks=[
            dict(type="p", text="**Terms.** Time is divided into numbered terms. Each server stores the latest term it has seen; any message carrying a higher term makes the receiver adopt it and become a follower. In each term at most one leader is elected."),
            dict(type="p", text="**Elections.** A follower that hears nothing from a leader for its election timeout, chosen at random between 150 and 300 ms, becomes a candidate: it moves to the next term, votes for itself and asks the others. A server gives one vote per term, and only to a candidate whose log is at least as up to date as its own: the last entry has a later term, or the same term and the log is at least as long. Votes from a majority (3 of 5) make a leader."),
            dict(type="p", text="**Replication.** The leader appends each client command to its log and sends it to the followers in AppendEntries messages, which double as heartbeats. Each message names the index and term of the entry just before the new ones; a follower whose log does not have that entry refuses, and the leader tries one entry earlier until the logs meet, then overwrites the follower's disagreeing tail."),
            dict(type="p", text="**Commitment.** Once a majority stores an entry from the leader's current term, it and everything before it are committed, and each server applies committed entries to its state machine in order. Older-term entries are committed only by counting a newer entry after them."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Any two majorities of five share a server. A committed entry is on a majority, a new leader needs votes from a majority, and no one votes for a log that is behind, so every new leader already holds every committed entry."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Three hundred runs of chaos", toc="Measured", blocks=[
            dict(type="p", text=f"**Chaos**: {ch['runs']} runs of {ch['ms']} simulated milliseconds, {ch['n']} servers, {ch['loss']}% of messages lost, every message delayed {ch['dmin']} to {ch['dmax']} ms (so they arrive out of order), servers crashing and restarting, the network cut into two groups for up to a second, and a client command every 20 ms. There were {ch['elections']} elections and {ch['leaders']} leaders; {ch['nowin']} elections ended in a timeout without a winner; {ch['committed']} entries were committed. The cluster had no leader {ch['noleader']}% of the time. Safety violations: **{ch['viol']}**: the program checked all five properties throughout."),
            dict(type="table", head=["Property (the paper's words, shortened)", "How the program checks it"], rows=[
                ["Election Safety: at most one leader in a term", "records the leader of every term"],
                ["Leader Append-Only: a leader never overwrites or deletes its entries", "compares each leader's log with its log a millisecond before"],
                ["Log Matching: same index and term means identical up to there", "compares every pair of logs every 50 ms"],
                ["Leader Completeness: committed entries are in every later leader's log", "checks each new leader against all committed entries"],
                ["State Machine Safety: no two servers apply different commands at one index", "records the command applied at every index"],
            ]),
            dict(type="p", text="**Random against fixed timeouts**: in a calm cluster, crash the leader and time how long until a new one is elected, 200 trials each:"),
            dict(type="table", head=["Election timeout", "Median", "Slowest", "No leader after 100 s", "Elections without a winner"], num=[1, 2, 3, 4], rows=[
                ["random, 150 to 300 ms", r["median"] + " ms", r["slowest"], r["stuck"], r["nowin"]],
                ["fixed, 150 ms", f["median"] + " ms", f["slowest"], f["stuck"], f["nowin"]],
            ], hl=0),
            dict(type="p", text=f"With one fixed timeout, the four survivors often time out together, each votes for itself, nobody wins, and they time out together again. Only the small spread of message delays ever breaks the tie, and in {f['stuck']} of 200 trials it never did."),
            dict(type="p", text=f"**Break one rule**: let servers vote for any candidate, without checking that its log is up to date. In the same {ch['runs']} runs the checker found a violation in **{br[1]}**. The first, in run {br[2]}: \"{br[3]}\": a server with a short log won an election and the committed entry was lost."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Stanford, 2014", toc="The evidence", blocks=[
            dict(type="p", text="Ongaro and Ousterhout, USENIX ATC '14, Philadelphia, June 2014 (Best Paper): Raft is \"a consensus algorithm for managing a replicated log\"; \"It produces a result equivalent to (multi-)Paxos, and it is as efficient as Paxos\". The paper begins from a complaint: \"Unfortunately, Paxos is quite difficult to understand, in spite of numerous attempts to make it more approachable.\""),
            dict(type="p", text="It names the five properties (Election Safety: \"at most one leader can be elected in a given term\"), and says that \"election timeouts are chosen randomly from a fixed interval (e.g., 150–300ms)\". In the user study, 43 students at Stanford and Berkeley took a quiz on each algorithm: the mean was 25.7 on Raft and 20.8 on Paxos, out of 60, and 33 of the 43 scored higher on Raft."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Testing an algorithm on people", toc="Full circle", blocks=[
            dict(type="p", text="Algorithms are usually judged by time, space and correctness. Raft's authors added a fourth measure, how well people understand it, and tested it the way a teaching method is tested: lectures, a quiz, and a comparison. The rules that make Raft easy to explain are the same ones this program checks: one leader, one direction for the log, one vote per term."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Take away one rule, the up-to-date check on votes, and {br[1]} of {ch['runs']} runs lose something that was already committed."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A cluster has 5 servers. How many can crash while it keeps working?", "2: the other 3 still form a majority, which is enough to elect a leader and commit entries."),
            ("S1 has log 1:a 1:b 2:c and S2 has 1:a 1:b 1:d 1:e. Whose log is more up to date?", "S1's: its last entry has term 2, later than S2's term 1. Length only matters when the last terms are equal."),
            ("Why can two leaders never exist in the same term?", "Each needs votes from a majority, any two majorities share a server, and a server votes once per term."),
            ("A leader of term 3 crashes before a term-3 entry reaches a majority. Is the entry lost?", "It may be: it was never committed, and a new leader without it will overwrite it on the followers. The client did not get a reply and will retry."),
            ("Why must a crashed server keep its term, its vote and its log on disk?", "Otherwise it could vote twice in one term after a restart, or forget entries it helped commit."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="In Search of an Understandable Consensus Algorithm (2014)", text="Ongaro and Ousterhout, USENIX ATC '14.",
                 draw=C.draw_manuscript, link="https://usenix.org/node/184041", link_text="USENIX conference page", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Raft", d["checks"],
                           "the five safety properties in every run, that random timeouts elect a leader where fixed ones can stall, and that removing the voting rule breaks safety.",
                           ["static void deliver(Msg m)", "static void checkLogMatching()"]),
    ]
    return dict(
        title="Raft", date="2014",
        description="Era 9, topic 4 of The Algorithm Evolution Atlas: Raft (Ongaro and Ousterhout, Stanford, 2014), consensus designed to be understood, simulated with lost messages and crashes.",
        lede="Paxos let computers agree in spite of failures, and almost nobody could explain it. In 2014 two researchers at Stanford designed a consensus algorithm whose first goal was to be understood: one leader, numbered terms, random timeouts, and a log that flows one way.",
        fieldnote=f"I ran five servers through {ch['runs']} storms of lost messages, crashes and broken links. Leaders came and went {ch['leaders']} times and the logs never disagreed. Then I removed one rule about voting, and in {br[1]} of the storms the cluster forgot something it had promised to keep.",
        card=[("When", "June 2014"),
              ("Where", "Stanford University"),
              ("What hurt", "Paxos was hard to understand and to build"),
              ("The fix", "A strong leader, terms, random timeouts, one-way logs"),
              ("Checked", f"0 safety violations in {ch['runs']} chaotic runs; {br[1]} without the voting rule")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Raft.java`.",
    )
