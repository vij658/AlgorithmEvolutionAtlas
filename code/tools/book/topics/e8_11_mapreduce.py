"""Era 8, topic 11: MapReduce. Every number is parsed from MapReduce.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("wordcount: "):
            m = re.search(r"corpus.txt, ([\d,]+) words, ([\d,]+) different ; (\d+) map tasks, (\d+) reduce tasks, (\d+) machines", ln)
            d["wc"] = dict(words=m.group(1), distinct=m.group(2), M=m.group(3), R=m.group(4), W=m.group(5))
            d["cases"] = re.findall(r"(normal|machine [^:;]+): finished at ([\d.]+), (\d+) map runs and (\d+) reduce runs for \d+ and \d+ tasks, (\d+) backup cop(?:y|ies), (\d+) cop(?:y|ies) stopped", ln)
            d["longer"] = re.search(r"makes the job (\d+)% longer", ln).group(1)
        elif ln.startswith("counts: "):
            d["top"] = re.findall(r"([a-z']+):(\d+)", ln.split("words", 1)[1])
        elif ln.startswith("pagerank: "):
            d["ranks"] = re.search(r"ranks ([\d.,]+) ;", ln).group(1).split(",")
            d["prdiff"] = re.search(r"direct computation (\S+)$", ln).group(1)
        elif ln.startswith("widget: "):
            m = re.match(r"widget: (\w+) ; .*? ; finished at ([\d.]+) ; task@machine:start-end:outcome (.*)$", ln)
            d.setdefault("widget", {})[m.group(1)] = dict(finish=m.group(2), sched=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def flow_svg(d):
    def draw(t, standalone):
        o = []
        W, H = 760, 360
        part = [t["red"], t["yellow"], t["blue"]]
        on = [t["on_red"], t["on_yellow"], t["on_blue"]]
        heads = [(20, "input, in M pieces"), (170, "map tasks"), (440, "reduce tasks"), (615, "output files")]
        for x, s in heads:
            o.append(C.text(x, 24, s, t["muted"], 12, "start", 700))
        o.append(C.text(330, 24, "hash(word) mod R", t["muted"], 12, "middle", 700))
        my = [44, 114, 184, 254]
        ry = [64, 149, 234]
        for i, y in enumerate(my):
            o.append(C.rect(20, y, 110, 50, t["wash"], t["axis"], 1))
            o.append(C.text(75, y + 30, f"text piece {i}", t["ink"], 12, "middle"))
            o.append(C.line(130, y + 25, 168, y + 25, t["ink"], 1.2))
            o.append(C.rect(170, y, 130, 50, t["surface"], t["ink"], 1.4))
            o.append(C.text(180, y + 21, f"map {i}", t["ink"], 12.5, "start", 700))
            o.append(C.text(180, y + 39, "(word, 1) per word", t["muted"], 11))
            for j in range(3):
                o.append(C.rect(300, y + 2 + j * 15.5, 14, 14, part[j], part[j], 1))
                o.append(C.line(314, y + 9 + j * 15.5, 438, ry[j] + 25, part[j], 1.3, ";opacity:0.8"))
        for j, y in enumerate(ry):
            o.append(C.rect(440, y, 140, 50, part[j], part[j], 1.4))
            o.append(C.text(450, y + 21, f"reduce {j}", on[j], 12.5, "start", 700))
            o.append(C.text(450, y + 39, "add up each word's 1s", on[j], 11))
            o.append(C.line(580, y + 25, 613, y + 25, t["ink"], 1.2))
            o.append(C.rect(615, y, 125, 50, t["wash"], t["axis"], 1))
            o.append(C.text(625, y + 30, f"(word, total), part {j}", t["ink"], 11.5))
        o.append(C.text(20, 330, "The shuffle: every map task sends its part j to reduce task j, so all the (the, 1) pairs meet in one place.", t["ink"], 12.5))
        o.append(C.text(20, 350, "A map task's output stays on its own machine's disk; a reduce task writes to the shared file system.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Map tasks send each part of their output to one reduce task", t, standalone, 0.5, 760)
    return draw


MR_HTML = """
<div class="board mr-board">
  <div style="min-width:0">
    <div class="presets" id="mr-pre"></div>
    <div class="controls">
      <label>machine 0 dies at <select id="mr-fail"><option value="never">never</option><option>0.5</option><option>1.0</option><option>1.5</option><option>2.2</option><option>3.0</option><option>3.5</option></select></label>
      <label>machine 4 speed <select id="mr-slow"><option value="1">1</option><option value="0.5">1/2</option><option value="0.25">1/4</option><option value="0.125">1/8</option></select></label>
      <label class="chk"><input type="checkbox" id="mr-back"> backup copies</label>
    </div>
    <div id="mr-gantt" class="mr-gantt"></div>
    <p class="say" id="mr-say" aria-live="polite"></p>
  </div>
</div>
"""

MR_CSS = """
.mr-board{grid-template-columns:1fr}
.mr-board .presets{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.mr-board .controls{display:flex;gap:14px;align-items:end;flex-wrap:wrap;margin-bottom:10px}
.mr-board .chk{display:flex;gap:6px;align-items:center}
.mr-board .chk input{width:auto;padding:0}
.mr-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.mr-gantt{overflow:hidden}
"""

MR_JS = r"""
(() => {
  const box = document.getElementById("mr-gantt");
  if (!box) return;
  const PROG = __PROG__;
  const M = 12, R = 3, W = 6;
  const words = m => 100 + (m % 3) * 50;
  let total = 0; for (let m = 0; m < M; m++) total += words(m);
  const work = t => t < M ? words(t) / 100.0 : total / R / 200.0;
  // the scheduler of MapReduce.java, line for line
  function simulate(speeds, failAt, backups) {
    const mapDone = new Array(M).fill(false), mapWhere = new Array(M).fill(-1), reduceDone = new Array(R).fill(false);
    const running = [], pending = [], sched = [];
    let dead = false, now = 0, nb = 0, killed = 0, guard = 0, failedDuringReduce = false;
    for (let m = 0; m < M; m++) pending.push(m);
    while (true) {
      if (++guard > 100000) return null;
      const allMaps = mapDone.every(x => x), allReduces = reduceDone.every(x => x);
      if (allMaps && allReduces) break;
      if (allMaps && !pending.length && !running.length) for (let r = 0; r < R; r++) if (!reduceDone[r]) pending.push(M + r);
      for (let w = 0; w < W; w++) {
        if (w === 0 && dead) continue;
        if (running.some(c => c[1] === w)) continue;
        let task = pending.length ? pending.shift() : null, backup = false;
        if (task === null && backups && running.length) {
          let latest = null;
          for (const c of running) {
            const t = c[0], copies = running.filter(x => x[0] === t).length;
            if (copies === 1 && now + work(t) / speeds[w] < c[3] && (latest === null || c[3] > latest[3])) latest = c;
          }
          if (latest) { task = latest[0]; backup = true; }
        }
        if (task === null) continue;
        if (task >= M && !allMaps) { pending.unshift(task); continue; }
        running.push([task, w, now, now + work(task) / speeds[w]]);
        if (backup) nb++;
      }
      let next = Infinity, first = null;
      for (const c of running) if (c[3] < next) { next = c[3]; first = c; }
      if (!dead && failAt < next) {
        now = failAt; dead = true;
        if (allMaps) failedDuringReduce = true;
        for (let i = 0; i < running.length;) {
          const c = running[i];
          if (c[1] === 0) { sched.push({t: c[0], w: 0, s: c[2], e: now, how: "lost"}); running.splice(i, 1); if (!running.some(x => x[0] === c[0])) pending.unshift(c[0]); }
          else i++;
        }
        for (let m = 0; m < M; m++) if (mapDone[m] && mapWhere[m] === 0) { mapDone[m] = false; pending.push(m); sched.push({note: m}); }
        continue;
      }
      if (!first) return null;
      now = next; running.splice(running.indexOf(first), 1);
      const t = first[0], w = first[1];
      sched.push({t, w, s: first[2], e: now, how: "done"});
      for (let i = 0; i < running.length;) { const c = running[i]; if (c[0] === t) { sched.push({t: c[0], w: c[1], s: c[2], e: now, how: "stopped"}); running.splice(i, 1); killed++; } else i++; }
      if (t < M) { mapDone[t] = true; mapWhere[t] = w; } else reduceDone[t - M] = true;
    }
    return {finish: now, sched, nb, killed, failedDuringReduce};
  }
  const name = t => t < M ? "m" + t : "r" + (t - M);
  const str = res => res.sched.map(e => e.note !== undefined ? `machine 0's finished map ${e.note} must run again` : `${name(e.t)}@${e.w}:${e.s.toFixed(2)}-${e.e.toFixed(2)}:${e.how}`).join(" ");
  const PRE = {normal: ["never", "1", false], failure: ["2.2", "1", false], straggler: ["never", "0.25", false], backups: ["never", "0.25", true]};
  const fail = document.getElementById("mr-fail"), slow = document.getElementById("mr-slow"), back = document.getElementById("mr-back");
  function draw(res, failAt, sp) {
    box.innerHTML = "";
    const narrow = box.clientWidth > 0 && box.clientWidth < 560, T = Math.max(10, Math.ceil(res.finish + 0.5)), L = 100, WD = narrow ? 290 : 610, rowH = 36, top = 26, H = top + W * rowH + 34;
    const X = t => L + t / T * WD;
    const svg = sv("svg", {viewBox: `0 0 ${L + WD + 20} ${H}`, role: "img", "aria-label": `Which machine ran which task when; the job finished at ${res.finish.toFixed(2)}`}, box);
    for (let t = 0; t <= T; t++) {
      sv("line", {x1: X(t), y1: top - 4, x2: X(t), y2: top + W * rowH, stroke: "var(--axis)", "stroke-width": 0.6}, svg);
      sv("text", {x: X(t), y: top + W * rowH + 16, "text-anchor": "middle", "font-size": 11, fill: "var(--muted)"}, svg, String(t));
    }
    sv("text", {x: L, y: H - 2, "font-size": 11, fill: "var(--muted)"}, svg, "time (1 = 100 words mapped at full speed)");
    for (let w = 0; w < W; w++) {
      const y = top + w * rowH;
      sv("text", {x: 8, y: y + rowH / 2 + 4, "font-size": 12, fill: "var(--ink)"}, svg, `machine ${w}` + (w === 4 && sp < 1 ? ` (${sp === 0.5 ? "½" : sp === 0.25 ? "¼" : "⅛"})` : ""));
      if (w === 0 && failAt < Infinity) {
        sv("rect", {x: X(failAt), y: y + 3, width: X(T) - X(failAt), height: rowH - 6, fill: "var(--red)", opacity: 0.18}, svg);
        sv("text", {x: X(failAt) + 4, y: y + rowH / 2 + 4, "font-size": 11, fill: "var(--red)", "font-weight": 700}, svg, `dies at ${failAt}`);
      }
    }
    const rerun = new Set(res.sched.filter(e => e.note !== undefined).map(e => e.note));
    for (const e of res.sched) {
      if (e.note !== undefined) continue;
      const y = top + e.w * rowH + 5, x = X(e.s), wd = Math.max(1, X(e.e) - X(e.s)), isMap = e.t < M;
      const gone = e.how === "done" && e.w === 0 && isMap && rerun.has(e.t) && e.e <= failAt;
      if (gone) {
        sv("rect", {x: x + 1, y, width: wd - 2, height: rowH - 10, rx: 3, fill: "var(--wash)", stroke: "var(--red)", "stroke-width": 1.5, "stroke-dasharray": "4 3"}, svg);
        if (wd > 24) sv("text", {x: x + wd / 2, y: y + rowH / 2, "text-anchor": "middle", "font-size": 11, "font-weight": 600, fill: "var(--red)"}, svg, name(e.t) + " ✗");
        continue;
      }
      const done = e.how === "done";
      sv("rect", {x: x + 1, y, width: wd - 2, height: rowH - 10, rx: 3, fill: done ? (isMap ? "var(--blue)" : "var(--yellow)") : "var(--wash)",
        stroke: done ? "none" : e.how === "lost" ? "var(--red)" : "var(--muted)", "stroke-width": 1.5, "stroke-dasharray": done ? null : "4 3"}, svg);
      if (wd > 24) sv("text", {x: x + wd / 2, y: y + rowH / 2, "text-anchor": "middle", "font-size": 11, "font-weight": 600,
        fill: done ? (isMap ? "var(--on-blue)" : "var(--on-yellow)") : e.how === "lost" ? "var(--red)" : "var(--muted)"}, svg, name(e.t) + (done ? "" : e.how === "lost" ? " lost" : " stopped"));
    }
    sv("line", {x1: X(res.finish), y1: top - 8, x2: X(res.finish), y2: top + W * rowH, stroke: "var(--ink)", "stroke-width": 1.5, "stroke-dasharray": "5 3"}, svg);
    const late = X(res.finish) > L + 0.7 * WD;
    sv("text", {x: X(res.finish) + (late ? -4 : 4), y: top - 10, "text-anchor": late ? "end" : "start", "font-size": 11, "font-weight": 700, fill: "var(--ink)"}, svg, `finished at ${res.finish.toFixed(2)}`);
  }
  function run() {
    const failAt = fail.value === "never" ? Infinity : parseFloat(fail.value), sp = parseFloat(slow.value);
    const speeds = [1, 1, 1, 1, sp, 1];
    const res = simulate(speeds, failAt, back.checked);
    if (!res) { box.innerHTML = ""; document.getElementById("mr-say").textContent = "This combination stalls the simulated scheduler."; return; }
    draw(res, failAt, sp);
    const maps = res.sched.filter(e => e.how === "done" && e.t < M).length, notes = res.sched.filter(e => e.note !== undefined).map(e => "m" + e.note);
    let s = `Finished at ${res.finish.toFixed(2)}: ${maps} map runs for 12 map tasks, 3 reduce runs, ${res.nb} backup cop${res.nb === 1 ? "y" : "ies"}, ${res.killed} cop${res.killed === 1 ? "y" : "ies"} stopped.`;
    if (notes.length) s += ` Machine 0's finished ${notes.join(" and ")} were on its disk and ran again.`;
    const key = Object.keys(PRE).find(k => PRE[k][0] === fail.value && PRE[k][1] === slow.value && PRE[k][2] === back.checked);
    if (key) s += PROG[key].sched === str(res) && PROG[key].finish === res.finish.toFixed(2) ? ` The program printed this same schedule for its "${key}" case.` : ` The program's "${key}" schedule differs.`;
    document.getElementById("mr-say").textContent = s;
  }
  const pre = document.getElementById("mr-pre");
  for (const k of Object.keys(PRE)) {
    const b = el("button", {type: "button"}, pre, k);
    b.addEventListener("click", () => { [fail.value, slow.value, back.checked] = PRE[k]; run(); });
  }
  for (const c of [fail, slow, back]) c.addEventListener("change", run);
  let narrowNow = null;
  window.addEventListener("resize", () => { const n = box.clientWidth < 560; if (n !== narrowNow) { narrowNow = n; run(); } });
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How MapReduce combined older ideas, and where it led")
    W = 210
    nodes = {
        "lisp": (20, 20, "Map and reduce", "apply to every item, then combine", "Lisp and functional languages", "ink"),
        "hash": (395, 20, "Hash partitioning", "hash(key) mod R picks the machine", "as keys spread in topic 4", "ink"),
        "clu": (770, 20, "Cheap clusters", "commodity machines, any of which may fail", "about 1,800 in the paper's sort", "ink"),
        "mr": (395, 180, "MapReduce", "⊕ a library that re-runs pure tasks", "Google, OSDI, December 2004", "red"),
        "had": (20, 340, "Hadoop", "an open-source implementation", "", "ink"),
        "pr": (770, 340, "PageRank as map and reduce", "one round is one job", "topic 7, in this topic's program", "ink"),
        "past": (395, 490, "Moved on", "by 2014 not Google's primary model", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("lisp", "mr", ports=("bottom", "top:0.15"))
    D.edge("hash", "mr", ports=("bottom", "top"))
    D.edge("clu", "mr", ports=("bottom", "top:0.85"))
    D.edge("mr", "had", ports=("bottom:0.15", "top"))
    D.edge("mr", "pr", ports=("bottom:0.85", "top"))
    D.edge("mr", "past", ports=("bottom", "top"))
    D.text(20, 615, "DeWitt and Stonebraker called it \"a major step backwards\" (Wikipedia).", "caption")
    return D


def chain(d):
    steps = [
        ("Every program for a cluster of failure-prone machines handled distribution and failures itself",
         "Write two functions, map and reduce; a library does the rest", "Dean and Ghemawat, 2004"),
        ("Machines die, and a finished map task's output dies with its disk",
         "Run those tasks again: safe, because map and reduce are deterministic", "\"Completed map tasks are re-executed\""),
        (f"One slow machine holds up the whole job: {d['longer']}% longer in the program's word count",
         "Backup copies of the last tasks; the first copy to finish counts", "the paper's sort: 44% longer without them"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from writing it all by hand to slow machines")
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
    wc, cases, wg = d["wc"], d["cases"], d["widget"]
    case_rows = [[c[0][0].upper() + c[0][1:], c[1], c[2], c[3], c[4], c[5]] for c in cases]
    wg_rows = [[k, v["finish"]] for k, v in wg.items()]
    top_txt = ", ".join(f"*{w}* {n}" for w, n in d["top"])
    rank_rows = [[str(i), r] for i, r in enumerate(d["ranks"])]
    fail = cases[1]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Map and reduce came from Lisp and other functional languages: apply a function to every item, then combine the results. Hashing a key to choose a machine was already how data was spread (topic 4). Dean and Ghemawat at Google added a library that runs these two functions over a cluster of cheap machines and simply runs a task again when its machine fails. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: MapReduce. Blue: where it stands today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Kill a machine, slow one down", toc="Try it", blocks=[
            dict(type="p", text="A small word-count job: 12 map tasks of 100, 150 or 200 words, 3 reduce tasks, 6 machines. Each bar is one task copy on one machine: blue for map, yellow for reduce, dashed for a copy that was lost or stopped; ✗ marks a finished map task whose output died with its machine. Make machine 0 die, slow machine 4 down, or allow backup copies, and the widget runs the program's own scheduler. For the four named cases it prints the same schedule as the program, entry by entry."),
            dict(type="widget", html=MR_HTML, js=MR_JS.replace("__PROG__", json.dumps(wg)), css=MR_CSS,
                 fallback=dict(type="table", head=["Case", "Finished at"], num=[1], rows=wg_rows),
                 note="In the interactive edition you can choose when machine 0 dies, how slow machine 4 is, and whether backups run."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Two functions, and a library", toc="How it works", blocks=[
            dict(type="p", text="**What the programmer writes.** For counting words, map takes a piece of text and emits the pair (word, 1) for each word in it; reduce takes one word and all its 1s and adds them up. Nothing else."),
            dict(type="p", text="**What the library does.** It cuts the input into M pieces and runs a map task on each, on whichever machine is free. Each map task sorts its pairs into R parts by hash(word) mod R and keeps them on its own disk. Then R reduce tasks each fetch their part from every map task, group the pairs by word, and write the totals to a shared file system."),
            dict(type="svg", name="flow", draw=flow_svg(d), alt="Map tasks send each part of their output to one reduce task", width=760),
            dict(type="p", text="**When things go wrong.** Because map and reduce are deterministic and change nothing else, any task can be run again with the same result. When a machine dies, the master runs its tasks again elsewhere, including its finished map tasks, whose output was on the dead machine's disk. When the job is nearly done, idle machines start backup copies of the tasks still running; whichever copy finishes first counts."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Restrict what the programmer may write, pure functions over key–value pairs, and the library can do everything else, including doing work twice."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Counting the words of this book", toc="Measured", blocks=[
            dict(type="p", text=f"**Word count** on this book's field notes: {wc['words']} words, {wc['distinct']} different; {wc['M']} map tasks, {wc['R']} reduce tasks, {wc['W']} simulated machines. Time is simulated: a task takes its amount of data divided by its machine's speed. In every case the counts were checked equal to a plain count."),
            dict(type="table", head=["Case", "Finished at", "Map runs", "Reduce runs", "Backup copies", "Copies stopped"], num=[1, 2, 3, 4, 5], rows=case_rows),
            dict(type="p", text=f"When machine 0 died at {fail[0].split(' at time ')[1]}, {int(fail[2]) - int(wc['M'])} of its finished map tasks ran again: {fail[2]} map runs for {wc['M']} tasks. Without backups, the slow machine made the job **{d['longer']}% longer** than with them; Dean and Ghemawat measured 44% for their sort. The commonest words: {top_txt}."),
            dict(type="p", text=f"**PageRank as MapReduce**: topic 7's 8-page web, 10 rounds, each round one map (each page sends its rank divided by its number of links along each link) and one reduce (each page adds what it received). Largest difference from the direct computation: {d['prdiff']}."),
            dict(type="table", head=["Page", "Rank after 10 rounds"], num=[0, 1], rows=rank_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Google, December 2004", toc="The evidence", blocks=[
            dict(type="p", text="Dean and Ghemawat, OSDI 2004: MapReduce is \"a programming model and an associated implementation for processing and generating large data sets\"; programs are \"automatically parallelized and executed on a large cluster of commodity machines\"; the keys are split into R pieces \"(e.g., hash(key) mod R)\"; \"Completed map tasks are re-executed on a failure\"; \"the sort program described in Section 5.3 takes 44% longer to complete when the backup task mechanism is disabled\"; the sort ran on \"approximately 1800 machines\"; \"upwards of one thousand MapReduce jobs are executed on Google's clusters every day\"."),
            dict(type="p", text="Wikipedia: \"Our abstraction is inspired by the map and reduce primitives present in Lisp and many other functional languages\" (quoting the paper); Apache Hadoop is a popular open-source implementation; by 2014 Google no longer used MapReduce as its primary model (\"We don't really use MapReduce anymore\", Urs Hölzle); DeWitt and Stonebraker called it \"a major step backwards\". MIT's distributed-systems course (6.5840, 2026): \"MR manages, and hides, all aspects of distribution!\", \"Coordinator re-runs just the failed Map()s and Reduce()s\", and \"Map and Reduce should be pure deterministic functions\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="An old pair of functions", toc="Full circle", blocks=[
            dict(type="p", text="Map and reduce are ideas from programming languages, about functions with no side effects. MapReduce put that purity to a new use: a function with no side effects can be run twice, on another machine, after a failure, and nobody can tell."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Topic 7's PageRank, written as one map and one reduce per round, gave the same ranks as the direct computation: largest difference {d['prdiff']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why is it safe to run a map task twice?", "It is deterministic and changes nothing else: the second run produces exactly the same pairs."),
            ("Why are finished map tasks run again when their machine dies, but not finished reduce tasks?", "A map task's output is on its own machine's disk, which is gone; a reduce task's output is already in the shared file system."),
            ("Which reduce task receives the word \"the\"?", "The one numbered hash(\"the\") mod R. Every map task sends its (the, 1) pairs to that same task."),
            ("Why do backup copies help only near the end?", "Earlier, a free machine has new tasks to start. At the end, one slow task leaves every other machine idle."),
            ("Write one round of PageRank as a map and a reduce.", "Map: each page emits (linked page, its rank ÷ its number of links). Reduce: each page adds what it received, times d, plus (1 − d)/N."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="MapReduce: Simplified Data Processing on Large Clusters (OSDI 2004)", text="The model, the implementation and the measurements.",
                 draw=C.draw_manuscript, link="https://courses.cs.cornell.edu/cs5410/2008fa/Readings/mapreduce-osdi04.pdf", link_text="The paper (PDF, on a Cornell course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MapReduce", d["checks"],
                           "that word counts are identical to a plain count whether machines die, run slowly or run backups, that no machine runs two tasks at once, and that PageRank by map and reduce equals PageRank computed directly.",
                           ["static Run simulate(List<List<String>> splits, int R, double[] speeds, double failAt, boolean backups)"]),
    ]
    return dict(
        title="MapReduce", date="2004",
        description="Era 8, topic 11 of The Algorithm Evolution Atlas: Dean and Ghemawat's MapReduce (Google, 2004), with a simulated cluster that loses a machine, slows one down and runs backup copies.",
        lede="A program that runs on a cluster of cheap computers has to split the data, schedule the work and survive machines that die. In 2004 Dean and Ghemawat at Google showed that many jobs fit one shape, map and then reduce, and that a library could do all the hard parts for any program written that way.",
        fieldnote=f"I simulated {wc['W']} of the species' machines counting the words of my own field notes. When one machine died, the library ran its finished pieces again and the counts came out identical. When one machine ran five times slower, the job took {d['longer']}% longer than when backup copies were allowed.",
        card=[("When", "OSDI, San Francisco, December 2004"),
              ("Where", "Google"),
              ("What hurt", "Every cluster program handled failures itself"),
              ("The fix", "Map and reduce; lost tasks simply run again"),
              ("Checked", "Identical counts in all four runs")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MapReduce.java`.",
    )
