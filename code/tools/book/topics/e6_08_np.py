"""Era 6, topic 8: NP-completeness. Every number is parsed from NpComplete.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"tiny: formula (.*?) ; graph: (\d+) vertices \(one per literal\), (\d+) edges \((\d+) inside the (\d+) triangles, (\d+) joining a literal to its negation\) ; an independent set of (\d+), one vertex per triangle: (.*?) ; set those literals true \(others false\): (.*?), and every clause", ln):
            clauses = [[l.strip() for l in c.strip("() ").split(" or ")] for c in m.group(1).split(" and ")]
            d["tiny"] = dict(formula=m.group(1), clauses=clauses, v=m.group(2), e=m.group(3), tri=m.group(4), ntri=m.group(5), neg=m.group(6),
                             size=m.group(7), chosen=[x.strip() for x in m.group(8).split(",")], assign=m.group(9))
        elif m := re.match(r"chain: ([\d,]+) random formulas in (\d+) variables, (\d+) to (\d+) clauses of (\d+) to (\d+) literals ; .*? all five answers agree on every formula: (\d+) satisfiable, (\d+) not ; graphs of up to (\d+) vertices", ln):
            d["chain"] = dict(n=m.group(1), vars=m.group(2), cmin=m.group(3), cmax=m.group(4), lmin=m.group(5), lmax=m.group(6), sat=m.group(7), unsat=m.group(8), maxv=m.group(9))
        elif m := re.match(r"check: a random formula of (\d+) variables and (\d+) clauses of 3 ; .*? after (\d+) steps of its tree ; checking it takes one look at each of the (\d+) clauses ; trying every assignment could take up to 2\^(\d+) = ([\d,]+)", ln):
            d["check"] = dict(vars=m.group(1), clauses=m.group(2), steps=m.group(3), looks=m.group(4), exp=m.group(5), all=m.group(6))
        elif ln.startswith("threshold: "):
            d["thr"] = re.findall(r"([\d.]+) clauses per variable: (\d+)% satisfiable, median ([\d,]+) steps", ln)
            m = re.match(r"threshold: random formulas of (\d+) variables, (\d+) formulas", ln)
            d["thr_n"] = dict(vars=m.group(1), per=m.group(2), peak=re.search(r"works hardest at ([\d.]+)", ln).group(1))
        elif ln.startswith("growth: "):
            d["growth"] = re.findall(r"n=(\d+): ([\d,]+)", ln)
            d["growth_last"] = re.search(r"by ([\d.]+) at the last step", ln).group(1)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def graph_svg(d):
    tn = d["tiny"]
    cl = tn["clauses"]
    chosen = tn["chosen"]

    def draw(t, standalone):
        o = []
        W, H = 760, 446
        o.append(C.text(20, 24, "One triangle per clause; an edge between every literal and its negation", t["ink"], 13, "start", 700))
        centers = [(130, 125), (630, 125), (130, 335), (630, 335)]
        pos = {}
        for ci, clause in enumerate(cl):
            cx, cy = centers[ci]
            pts = [(cx, cy - 55), (cx - 62, cy + 35), (cx + 62, cy + 35)]
            for li, lit in enumerate(clause):
                pos[(ci, li)] = pts[li]
            for a in range(3):
                for b in range(a + 1, 3):
                    o.append(C.line(*pts[a], *pts[b], t["ink2"], 1.6))
        # negation edges
        keys = list(pos)
        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                a, b = keys[i], keys[j]
                la, lb = cl[a[0]][a[1]], cl[b[0]][b[1]]
                if a[0] != b[0] and (la == "not " + lb or lb == "not " + la):
                    (x1, y1), (x2, y2) = pos[a], pos[b]
                    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
                    dx, dy = x2 - x1, y2 - y1
                    qx, qy = mx - dy * 0.12, my + dx * 0.12          # bend each line a little, so none runs through a vertex
                    o.append(C.path(f"M{x1:.1f},{y1:.1f} Q{qx:.1f},{qy:.1f} {x2:.1f},{y2:.1f}", t["axis"], "none", 1.3, ";stroke-dasharray:5 4"))
        picked = set()
        for ci, lit in enumerate(chosen):
            li = cl[ci].index(lit)
            picked.add((ci, li))
        for (ci, li), (x, y) in pos.items():
            on = (ci, li) in picked
            o.append(C.circle(x, y, 22, t["red"] if on else t["surface"], t["red"] if on else t["ink2"], 1.6))
            lab = cl[ci][li].replace("not x", "¬x")
            o.append(C.text(x, y + 5, lab, t["on_red"] if on else t["ink"], 12, "middle", 700))
        for ci, (cx, cy) in enumerate(centers):
            o.append(C.text(cx, cy + 74, f"clause {ci + 1}", t["muted"], 11, "middle"))
        o.append(C.text(20, H - 8, f"Red: an independent set of {tn['size']} (no two joined), one per triangle. Make those literals true: {tn['assign'].replace(' ', ', ').replace('=', ' = ')}.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A formula turned into a graph", t, standalone, 0.55, 760)
    return draw


NP_HTML = """
<div class="board np-board">
  <div style="min-width:0">
    <div class="np-clauses" id="np-clauses"></div>
  </div>
  <div style="min-width:0">
    <div class="np-vars" id="np-vars"></div>
    <div class="np-btns"><button type="button" id="np-solve">Let the search find one</button><button type="button" id="np-new">New formula</button></div>
    <div class="np-stats" id="np-stats"></div>
    <p class="say" id="np-say" aria-live="polite"></p>
  </div>
</div>
"""

NP_CSS = """
.np-clauses{display:flex;flex-wrap:wrap;gap:4px;font:12px var(--mono)}
.np-clauses span{border:1px solid var(--rule);padding:2px 5px;border-radius:3px}
.np-clauses span.ok{border-color:var(--blue);color:var(--blue)}
.np-clauses span.bad{background:var(--red);color:var(--on-red);border-color:var(--red)}
.np-vars{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:4px}
.np-vars button{font:13px var(--mono);padding:4px}
.np-vars button.t{background:var(--blue);color:var(--on-blue);border-color:var(--blue)}
.np-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.np-stats{font:13px var(--mono);display:grid;gap:3px}
"""

NP_JS = r"""
(() => {
  const cBox = document.getElementById("np-clauses");
  if (!cBox) return;
  const N = 16, M = 68;
  let seed = 1971, F, val;
  const r = n => { seed = (seed * 1103515245 + 12345) % 2147483648; return Math.floor(seed / 2147483648 * n); };
  function fresh() {
    while (true) {
      F = [];
      for (let i = 0; i < M; i++) { const vs = []; while (vs.length < 3) { const v = 1 + r(N); if (!vs.includes(v)) vs.push(v); } F.push(vs.map(v => r(2) ? v : -v)); }
      if (dpll(new Array(N + 1).fill(0)).ok) break;          // keep only formulas that can be satisfied
    }
    val = new Array(N + 1).fill(false); show("Click the variables to switch them between false and true. Can you make every clause true?");
  }
  let steps = 0;
  function dpll(a) {
    steps++;
    a = a.slice();
    while (true) {
      let unit = 0, all = true, branch = 0, best = 9;
      for (const c of F) {
        let free = 0, last = 0, sat = false;
        for (const l of c) { const v = a[Math.abs(l)]; if (v === 0) { free++; last = l; } else if ((v === 1) === (l > 0)) { sat = true; break; } }
        if (sat) continue; all = false;
        if (free === 0) return {ok: false};
        if (free === 1) { unit = last; break; }
        if (free < best) { best = free; branch = last; }
      }
      if (all) return {ok: true, a};
      if (unit) { a[Math.abs(unit)] = unit > 0 ? 1 : -1; continue; }
      const v = Math.abs(branch);
      a[v] = branch > 0 ? 1 : -1; let res = dpll(a); if (res.ok) return res;
      a[v] = -a[v]; res = dpll(a); return res;
    }
  }
  const sat = c => c.some(l => val[Math.abs(l)] === (l > 0));
  function show(msg) {
    cBox.innerHTML = "";
    let good = 0;
    F.forEach(c => { const ok = sat(c); if (ok) good++; el("span", {class: ok ? "ok" : "bad"}, cBox, "(" + c.map(l => (l < 0 ? "¬" : "") + "x" + Math.abs(l)).join(" ∨ ") + ")"); });
    const vb = document.getElementById("np-vars"); vb.innerHTML = "";
    for (let v = 1; v <= N; v++) { const b = el("button", {type: "button", class: val[v] ? "t" : ""}, vb, `x${v} ${val[v] ? "T" : "F"}`); b.addEventListener("click", () => { val[v] = !val[v]; show(); }); }
    const st = document.getElementById("np-stats"); st.innerHTML = "";
    el("div", {}, st, `clauses true: ${good} of ${M}`);
    el("div", {}, st, `assignments in all: 2^${N} = ${fmt(2 ** N)}`);
    document.getElementById("np-say").textContent = msg || (good === M ? "Every clause is true. Checking that took one look at each clause; finding it was the hard part." : `${M - good} clause${M - good === 1 ? " is" : "s are"} still false (red).`);
  }
  document.getElementById("np-solve").addEventListener("click", () => {
    steps = 0; const res = dpll(new Array(N + 1).fill(0));
    for (let v = 1; v <= N; v++) val[v] = res.a[v] === 1;
    show(`The search with unit propagation found an assignment in ${steps} steps of its tree, out of 2^${N} assignments.`);
  });
  document.getElementById("np-new").addEventListener("click", fresh);
  fresh();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How NP-completeness combined older ideas, and where it led")
    W = 210
    nodes = {
        "tm": (20, 20, "Turing machines", "a precise meaning of computation", "Era 4, topic 7", "ink"),
        "good": (395, 20, "\"Good\" algorithms", "work that grows like a power of the size", "Edmonds, Era 5, topic 13", "ink"),
        "logic": (770, 20, "Formulas of logic", "true-or-false variables, and or not", "Boole, Era 3", "ink"),
        "cook": (395, 180, "NP-completeness", "⊕ every problem in NP reduces to satisfiability", "Cook 1971; Levin 1973", "red"),
        "karp": (20, 340, "Karp's 21 problems", "graphs, sets and numbers, all equally hard", "1972", "ink"),
        "many": (395, 340, "Hundreds, if not thousands", "NP-complete problems found since", "", "ink"),
        "pk": (770, 340, "Public keys", "security from problems believed hard", "topic 10", "ink"),
        "today": (395, 490, "Today", "P = NP? Still open: a Millennium Prize Problem", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("tm", "cook", ports=("bottom", "top:0.15"))
    D.edge("good", "cook", ports=("bottom", "top"))
    D.edge("logic", "cook", ports=("bottom", "top:0.85"))
    D.edge("cook", "karp", ports=("bottom:0.15", "top"))
    D.edge("karp", "many", ports=("right", "left"))
    D.edge("cook", "pk", ports=("bottom:0.85", "top"), dashed=True)
    D.edge("many", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: public-key cryptography rests on problems believed hard, a belief of the same kind, not a proof.", "caption")
    return D


def chain(d):
    ch, ck, th, g = d["chain"], d["check"], d["thr_n"], d["growth"]
    steps = [
        ("Many problems resisted every attempt at a fast method, and nobody could say why",
         "Cook: every problem whose answers can be checked quickly reduces to satisfiability", "Cook 1971; Levin, independently"),
        ("Does that say anything about graphs, schedules or packing?",
         f"Karp: 21 such problems all reduce to each other; the program's chain of five agreed on all {ch['n']} formulas", "Karp 1972"),
        (f"Checking an answer: one look at each of {ck['looks']} clauses. Finding one: up to 2^{ck['exp']} tries?",
         "Nobody knows a fast way to find, or a proof that none exists", "P = NP?, open since 1971"),
        (f"On random formulas the search works hardest near {th['peak']} clauses per variable",
         f"and there its work multiplied by {d['growth_last']} for the last 10 variables added", "measured, not proved"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from many hard problems to one question")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx = (L, R) if i % 2 == 0 else (R, L)
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx, y, bw, rowh, [("WHAT IT SHOWED" if i >= 2 else "THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="answered by" if i < 2 else "and", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    tn, ch, ck, thr, th, g = d["tiny"], d["chain"], d["check"], d["thr"], d["thr_n"], d["growth"]
    thr_rows = [[r, f"{s}%", m] for r, s, m in thr]
    peak_i = next(i for i, r in enumerate(thr) if r[0] == th["peak"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one; this time the new idea is about problems rather than methods. Turing had made computation precise, Edmonds had proposed that a good algorithm is one whose work grows like a power of the input's size, and logic had its formulas of true-or-false variables. Cook joined them: one formula problem carries all the problems of a large class inside it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: NP-completeness. Blue: where the question stands today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Checking is easy; finding is not", toc="Try it", blocks=[
            dict(type="p", text="A random formula: 16 true-or-false variables and 68 clauses, each of three literals (¬ means not). Click the variables to set them; every clause turns blue as soon as it is true. Checking an assignment is instant. Finding one that makes all 68 true is the hard part; when you give up, let the search find one."),
            dict(type="widget", html=NP_HTML, js=NP_JS, css=NP_CSS,
                 fallback=dict(type="table", head=["Clauses per variable", "Satisfiable", "Median steps of the search"], num=[0, 1, 2], rows=thr_rows, hl=peak_i),
                 note=f"In the interactive edition you can try to satisfy a random formula yourself. The table: {th['per']} random formulas of {th['vars']} variables for each number of clauses."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what it showed", title="Each answer leaves a new question", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new question sits directly under the answer that raised it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Translations that keep the answer", toc="How it works", blocks=[
            dict(type="p", text="**P and NP.** A problem is in P if some method answers it in a number of steps bounded by a polynomial in the size of the input. It is in NP if a proposed answer can be *checked* in polynomial time. Satisfiability (can these clauses all be made true?) is in NP: given an assignment, check each clause."),
            dict(type="p", text="**Reductions.** A reduction is a quick translation of every instance of one problem into an instance of another, with the same answer. If B has a fast method and A reduces to B, then A has one too. Cook showed that every problem in NP reduces to satisfiability; Karp then reduced satisfiability to 21 other problems, so all of them are NP-complete: a fast method for any one would give a fast method for all."),
            dict(type="p", text=f"**One reduction, drawn.** A formula with m clauses of three literals becomes a graph: one triangle per clause, and an edge between every literal and its negation. The graph has m vertices with no edge between any two exactly when the formula can be satisfied: pick one true literal from each clause. The program's formula, {len(tn['clauses'])} clauses, gives {tn['v']} vertices and {tn['e']} edges ({tn['tri']} in triangles, {tn['neg']} between negations):"),
            dict(type="svg", name="graph", draw=graph_svg(d), alt="A formula turned into a graph", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Instead of solving a hard problem, show that it is as hard as a problem everyone has failed to solve. Then a whole family of problems stands or falls together."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Five problems, one answer", toc="Measured", blocks=[
            dict(type="p", text=f"**The chain.** {ch['n']} random formulas in {ch['vars']} variables ({ch['cmin']} to {ch['cmax']} clauses of {ch['lmin']} to {ch['lmax']} literals) were each turned into 3-satisfiability, then a graph (an independent set of size m?), then vertex cover, then clique in the complementary graph. Each of the five questions was answered by its own exhaustive method. All five answers agreed on every formula: {ch['sat']} satisfiable, {ch['unsat']} not, with graphs of up to {ch['maxv']} vertices."),
            dict(type="p", text=f"**Checking against finding.** A random formula of {ck['vars']} variables and {ck['clauses']} clauses: a search with unit propagation found a satisfying assignment after {ck['steps']} steps of its tree, and checking it took one look at each of the {ck['looks']} clauses. Trying every assignment could take up to 2^{ck['exp']} = {ck['all']}."),
            dict(type="p", text=f"**Where it is hard.** Random formulas of {th['vars']} variables, {th['per']} for each number of clauses. With few clauses almost every formula can be satisfied, with many almost none; the search works hardest where the share falls, at {th['peak']} clauses per variable here:"),
            dict(type="table", head=["Clauses per variable", "Satisfiable", "Median steps of the search"], num=[0, 1, 2], rows=thr_rows, hl=peak_i),
            dict(type="p", text=f"**Growth.** Near that ratio (4.26 clauses per variable), the median work grows with the number of variables: {', '.join(f'{n} variables {s}' for n, s in g)} steps. The last 10 variables multiplied it by {d['growth_last']}. That is a measurement of one method on random formulas, not a proof about all methods."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Toronto, Berkeley and Moscow", toc="The evidence", blocks=[
            dict(type="p", text="Stephen Cook, \"The Complexity of Theorem-Proving Procedures\" (University of Toronto; ACM Symposium on the Theory of Computing, 1971): \"any recognition problem solved by a polynomial time-bounded nondeterministic Turing machine\" can be reduced to deciding whether a formula is a tautology; \"it is fruitless to search for a polynomial decision procedure for the subgraph problem\" unless tautologies have one. He added: \"I feel it is worth spending considerable effort trying to prove this conjecture. Such a proof would be a major breakthrough in complexity theory.\" Berkeley's mathematics department had not reappointed him; Karp later said: \"It is to our everlasting shame that we were unable to persuade the math department to give him tenure.\""),
            dict(type="p", text="Leonid Levin found the same result independently in the Soviet Union (\"Universal search problems\", 1973); it is \"often called the Cook–Levin theorem\". Richard Karp's \"Reducibility Among Combinatorial Problems\" (1972) reduced satisfiability to 21 problems. Lance Fortnow: \"If Cook made the P versus NP question interesting to logicians, Karp made the question important to everyone else.\" Cook received the Turing Award in 1982; the question \"remains open and is among the seven famous Millennium Prize Problems\" (Wikipedia)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="From \"good\" algorithms to hard problems", toc="Full circle", blocks=[
            dict(type="p", text="Edmonds asked in 1965 for algorithms whose work grows like a power of the size (Era 5, topic 13); his matching method was one. Cook and Karp found a family of problems for which nobody has such an algorithm, and showed they all stand or fall together. Four years later, cryptographers turned the same kind of hardness into a resource (topic 10)."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Checking the program's satisfying assignment took {ck['looks']} looks. Whether finding one can always be made nearly as easy is the question P = NP."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Is (x1 ∨ x2) ∧ (¬x1 ∨ x2) ∧ (¬x2 ∨ x1) ∧ (¬x1 ∨ ¬x2) satisfiable?", "No: the first and second need x2, the third then needs x1, and the fourth forbids both."),
            ("If someone found a fast method for clique, what would follow?", "A fast method for every problem in NP, satisfiability included, since they all reduce to clique."),
            ("Why is checking easy for satisfiability?", "An assignment is a short certificate: one pass over the clauses checks it."),
            ("In the graph reduction, why must the independent set use exactly one vertex per triangle?", "A triangle's three vertices are all joined, so at most one can be chosen; to reach m, every triangle must give one."),
            ("Does a slow search on random formulas prove that satisfiability is hard?", "No. It measures one method on one kind of input; hardness for every method is exactly the open question."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Complexity of Theorem-Proving Procedures (1971)", text="Cook's paper for the third ACM Symposium on the Theory of Computing.",
                 draw=C.draw_manuscript, link="https://www.cs.umd.edu/~gasarch/COURSES/452/F14/cookpaper.pdf", link_text="The paper (PDF, on a course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "NpComplete", d["checks"],
                           "the graph reduction on a small formula, a chain of five reductions on 1,000 formulas with every problem solved exhaustively, every satisfying assignment found by the search, and the threshold and growth of the search's work.",
                           ["static long[] toGraph(List<int[]> g)", "static Object[] toThreeSat(List<int[]> f, int n)"]),
    ]
    return dict(
        title="NP-Completeness", date="1971–1973",
        description="Era 6, topic 8 of The Algorithm Evolution Atlas: Cook's theorem, Levin's independent discovery, Karp's 21 problems, reductions that keep the answer, and the open question P = NP.",
        lede="For some problems nobody could find a fast method, and nobody could prove there was none. Cook showed that a large family of them stand or fall together: solve one quickly, and you have solved them all.",
        fieldnote=f"I translated {ch['n']} small formulas into graphs four different ways and solved every version by brute force; the answers never disagreed. Checking a solution took one look at each clause. Whether finding one can ever be as easy, nobody here knows.",
        card=[("When", "Cook 1971; Karp 1972; Levin 1973"),
              ("Where", "Toronto, Berkeley, Moscow"),
              ("What hurt", "Many problems resisted every fast method"),
              ("The step", "Reductions; satisfiability is NP-complete"),
              ("Still open", "P = NP?")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `NpComplete.java`.",
    )
