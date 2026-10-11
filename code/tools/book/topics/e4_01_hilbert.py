"""Era 4, topic 1: Hilbert's questions. Every number is parsed from HilbertsQuestions.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {"found": [], "imp": [], "cubes": []}
    for ln in text.splitlines():
        if m := re.match(r"shells: three unknowns, shells 0 to (\d+): (\d+) tuples", ln):
            d["shells"] = dict(R=m.group(1), n=int(m.group(2)))
        elif m := re.match(r"found: (.+?) ; the search stops at shell (\d+) after (\d+) tuples with \((.+)\)$", ln):
            d["found"].append(dict(eq=m.group(1), shell=m.group(2), tried=int(m.group(3)), sol=m.group(4)))
        elif m := re.match(r"impossible: (.+?) ; (squares|cubes) leave remainders \{(.+?)\} mod (\d+), and no (\d) of them add up to (\d+) mod \d+ ; the search through shell (\d+) tried (\d+) tuples", ln):
            d["imp"].append(dict(eq=m.group(1), what=m.group(2), res=m.group(3), m=m.group(4), k=m.group(5), t=m.group(6), cap=m.group(7), tried=int(m.group(8))))
        elif m := re.match(r"cubes: (\d+) ; no remainder rule up to (\d+) forbids it ; shells 0 to (\d+): (\d+) tuples, none ; known solution \((.+?)\) checked, cubes sum to \d+ ; it lies on shell (\d+) ; the shells inside it hold (\d+) tuples \(about 10\^(\d+)\)", ln):
            d["cubes"].append(dict(n=m.group(1), M=m.group(2), cap=m.group(3), tried=int(m.group(4)), sol=m.group(5), shell=int(m.group(6)), inside=m.group(7), exp=m.group(8)))
        elif m := re.match(r"onevar: (.+?): divisors of 6 give (\d+) tests, roots \[(.+?)\] ; (.+?): (\d+) tests, no integer root ; (\d+) random polynomials of degree 1 to 4: the divisor test \((\d+) evaluations\) and a full search \((\d+) evaluations\) agree on all, (\d+) have integer roots", ln):
            d["one"] = dict(p1=m.group(1), t1=m.group(2), r1=m.group(3), p2=m.group(4), t2=m.group(5), n=m.group(6), div=int(m.group(7)), full=int(m.group(8)), roots=m.group(9))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def shells_svg(d):
    """Shells of whole-number points around the origin, and where x^2 + y^2 = 1105 is first met."""
    f = d["found"][0]
    sx, sy = [int(v) for v in f["sol"].split(",")]

    def draw(t, standalone):
        out, R, s, cx, cy = [], 6, 26, 200, 190
        cols = [t["red"], t["yellow"], t["blue"]]
        for x in range(-R, R + 1):
            for y in range(-R, R + 1):
                r = max(abs(x), abs(y))
                out.append(C.circle(cx + x * s, cy - y * s, 5 if r else 6, cols[r % 3] if r else t["ink"]))
        for r in range(1, R + 1):
            out.append(C.rect(cx - r * s - 9, cy - r * s - 9, 2 * r * s + 18, 2 * r * s + 18, "none", t["axis"], 1))
        out.append(C.text(cx, 30, "shells 0 to 6 (two unknowns)", t["muted"], 12.5, "middle"))
        X = 420
        lines = [("The search tries shell 0, then shell 1, then 2, ...", t["ink"], 14, 700),
                 ("Shell r holds the points whose larger coordinate", t["muted"], 13, 400),
                 ("(in size) is exactly r. Every point is reached.", t["muted"], 13, 400),
                 (f"x² + y² = 1105: stops on shell {f['shell']},", t["red"], 14, 700),
                 (f"after {f['tried']:,} points, at ({sx}, {sy}).", t["red"], 14, 700),
                 ("If no solution exists, it never stops.", t["blue"], 14, 700)]
        for i, (txt, col, size, w) in enumerate(lines):
            out.append(C.text(X, 90 + i * 30 + (14 if i >= 3 else 0) + (14 if i >= 5 else 0), txt, col, size, "start", w))
        out.append(C.text(20, 372, "Numbers checked by HilbertsQuestions.java.", t["muted"], 12))
        return C.svg_doc(780, 384, "".join(out), "Shells of whole-number points searched in order", t, standalone, 0.55, 780)
    return draw


HQ_HTML = """
<div class="board hq-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="hq-k">Equation <select id="hq-k"><option value="2">x² + y² = n</option><option value="3">x³ + y³ + z³ = n</option></select></label>
      <label for="hq-n">n = <input id="hq-n" type="number" min="0" max="99999" value="1105"></label>
      <button class="primary" id="hq-go">Search</button>
    </div>
    <div class="presets" id="hq-pre"></div>
    <svg id="hq-svg" viewBox="0 0 420 150" role="img" aria-label="Progress of the search, shell by shell"></svg>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">What happened</div>
    <ol class="hq-steps" id="hq-steps"></ol>
    <p class="say" id="hq-say" aria-live="polite"></p>
  </div>
</div>
"""

HQ_CSS = """
.hq-board select{font:inherit;font-size:14px;padding:3px 6px}
.hq-board input[type=number]{width:6.5em}
.hq-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:6px}
.hq-steps .m{font-family:var(--mono);font-size:12.5px;overflow-wrap:anywhere}
.hq-board .say{font-size:14.5px}
#hq-svg{width:100%;max-width:420px;height:auto}
"""

HQ_JS_TEMPLATE = r"""
(() => {
  const svg = document.getElementById("hq-svg");
  if (!svg) return;
  const KNOWN = __KNOWN__;
  const OPEN = ["114", "390", "627", "633", "732", "921", "975"];
  const CAP = {2: 600, 3: 70};
  const pre = document.getElementById("hq-pre");
  [["2", 1105], ["2", 1103], ["3", 29], ["3", 4], ["3", 30], ["3", 42]].forEach(([k, n]) => {
    const b = el("button", {type: "button"}, pre, (k === "2" ? "x²+y²=" : "x³+y³+z³=") + n);
    b.addEventListener("click", () => { document.getElementById("hq-k").value = k; document.getElementById("hq-n").value = n; run(); });
  });
  let job = 0;
  const pw = (a, k) => (k === 2 ? a * a : a * a * a);
  function obstruction(k, n) {
    for (let m = 2; m <= 60; m++) {
      const isP = new Array(m).fill(false), res = new Set();
      for (let a = 0; a < m; a++) { const r = ((k === 2 ? a * a : a * a * a) % m + m) % m; isP[r] = true; res.add(r); }
      const t = ((n % m) + m) % m;
      let ok = false;
      if (k === 2) { for (let a = 0; a < m && !ok; a++) if (isP[a] && isP[((t - a) % m + m) % m]) ok = true; }
      else { for (let a = 0; a < m && !ok; a++) for (let b = 0; b < m && !ok; b++) if (isP[a] && isP[b] && isP[((t - a - b) % m + 2 * m) % m]) ok = true; }
      if (!ok) return {m, res: [...res].sort((x, y) => x - y), t};
    }
    return null;
  }
  function draw(k, r, cap, tried, hit) {
    svg.innerHTML = "";
    const W = 420, H = 150, x0 = 40, x1 = 400, y = 52;
    sv("line", {x1: x0, y1: y, x2: x1, y2: y, stroke: "var(--axis)", "stroke-width": 2}, svg);
    const frac = Math.min(1, r / cap);
    sv("rect", {x: x0, y: y - 14, width: (x1 - x0) * frac, height: 28, fill: hit ? "var(--blue)" : "var(--yellow)"}, svg);
    sv("text", {x: x0, y: y - 30, fill: "var(--muted)", "font-size": 13}, svg, "shell 0");
    sv("text", {x: x1, y: y - 30, fill: "var(--muted)", "font-size": 13, "text-anchor": "end"}, svg, "shell " + cap + " (this page stops here)");
    sv("text", {x: W / 2, y: y + 50, fill: "var(--ink)", "font-size": 16, "font-weight": 700, "text-anchor": "middle"}, svg, "shell " + r + " · " + fmt(tried) + " tuples tried");
    sv("text", {x: W / 2, y: y + 76, fill: "var(--muted)", "font-size": 13, "text-anchor": "middle"}, svg, k === 2 ? "two unknowns: shell r holds 8r points" : "three unknowns: shell r holds 24r² + 2 points");
  }
  function run() {
    const my = ++job;
    const k = +document.getElementById("hq-k").value;
    let n = Math.max(0, Math.min(99999, Math.round(+document.getElementById("hq-n").value || 0)));
    const ol = document.getElementById("hq-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    const say = document.getElementById("hq-say");
    const name = k === 2 ? "x² + y² = " + n : "x³ + y³ + z³ = " + n;
    const ob = obstruction(k, n);
    if (ob) {
      li(`Remainders first: ${k === 2 ? "squares" : "cubes"} leave only <span class="m">{${ob.res.join(", ")}}</span> when divided by ${ob.m}.`);
      li(`No ${k} of them add up to ${ob.t}, the remainder of ${n}. So ${name} has no solution at all.`);
      say.textContent = "Proved impossible without searching: a finite argument settles the infinite question.";
      draw(k, 0, CAP[k], 0, false);
      return;
    }
    li(`No remainder rule up to 60 rules it out, so search: shell 0, 1, 2, ...`);
    let r = 0, tried = 0;
    const cap = CAP[k];
    function test(v) { tried++; let s = 0; for (const a of v) s += pw(a, k); return s === n; }
    function shell(r) {
      if (r === 0) return test(k === 2 ? [0, 0] : [0, 0, 0]) ? (k === 2 ? [0, 0] : [0, 0, 0]) : null;
      for (let i = 0; i < k; i++) for (const s of [-r, r]) {
        const lim = j => (j < i ? r - 1 : r);
        if (k === 2) {
          const j = 1 - i;
          for (let a = -lim(j); a <= lim(j); a++) { const v = i === 0 ? [s, a] : [a, s]; if (test(v)) return v; }
        } else {
          const o = [0, 1, 2].filter(j => j !== i);
          for (let a = -lim(o[0]); a <= lim(o[0]); a++) for (let b = -lim(o[1]); b <= lim(o[1]); b++) {
            const v = [0, 0, 0]; v[i] = s; v[o[0]] = a; v[o[1]] = b;
            if (test(v)) return v;
          }
        }
      }
      return null;
    }
    function chunk() {
      if (my !== job) return;
      const t0 = performance.now();
      while (r <= cap && performance.now() - t0 < 25) {
        const hit = shell(r);
        if (hit) {
          draw(k, r, cap, tried, true);
          li(`Found <span class="m">(${hit.join(", ")})</span> on shell ${r}, after ${fmt(tried)} tuples.`);
          say.textContent = "The search stops: a yes can always be confirmed by searching.";
          return;
        }
        r++;
      }
      draw(k, Math.min(r, cap), cap, tried, false);
      if (r <= cap) { requestAnimationFrame(chunk); return; }
      li(`No solution through shell ${cap}: ${fmt(tried)} tuples tried.`);
      if (k === 3 && KNOWN[n]) {
        const kn = KNOWN[n];
        li(`A solution is known: <span class="m">(${kn.sol})</span>. It lies on shell ${fmt(kn.shell)}; the shells inside it hold about 10<sup>${kn.exp}</sup> tuples.`);
        say.textContent = "This search would have stopped, but not in the lifetime of the universe. Cleverer searches found it.";
      } else if (k === 3 && OPEN.includes(String(n))) {
        say.textContent = "Nobody knows whether this search ever stops: " + n + " is one of the open cases below 1,000.";
      } else {
        say.textContent = "Still searching. If no solution exists, the search runs for ever, and watching it tells you nothing.";
      }
    }
    chunk();
  }
  document.getElementById("hq-go").addEventListener("click", run);
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Hilbert's questions combined older ideas, and where they led")
    W, H = 210, 86
    nodes = {
        "pell": (20, 20, "Pell's equation", "special methods for special equations", "Era 2 topic 5", "ink"),
        "boole": (395, 20, "Boole's algebra", "logic as calculation", "Era 3 topic 12", "ink"),
        "frege": (770, 20, "Formal logic", "proofs as strings of symbols", "Frege, Russell", "ink"),
        "hil": (395, 170, "Hilbert's questions", "⊕ ask for one process that decides everything", "1900, 1928", "red"),
        "god": (20, 330, "Gödel", "true but unprovable", "topic 5, 1931", "ink"),
        "ct": (395, 330, "Church and Turing", "⊕ a definition of process; the decision problem has none", "topics 6, 7, 1936", "ink"),
        "mat": (770, 330, "Matiyasevich", "no process for Diophantine equations", "1970", "blue"),
        "today": (395, 480, "Undecidability today", "searches that halt only on yes", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("pell", "hil", ports=("bottom", "top:0.15"))
    D.edge("boole", "hil", ports=("bottom", "top"))
    D.edge("frege", "hil", ports=("bottom", "top:0.85"))
    D.edge("hil", "god", ports=("bottom:0.1", "top:0.7"))
    D.edge("hil", "ct", ports=("bottom", "top"))
    D.edge("hil", "mat", ports=("bottom:0.9", "top:0.3"))
    D.edge("ct", "today", ports=("bottom", "top"))
    D.edge("mat", "today", ports=("bottom:0.3", "right:0.5"), dashed=True)
    D.text(20, 615, "Frege and Russell are named for context only; this book has no topic on them. Arrows link ideas, not documented lines of influence.", "caption")
    return D


def chain(d):
    c30 = next(c for c in d["cubes"] if c["n"] == "30")
    steps = [
        ("Each kind of equation needs its own method",
         "Ask for one process that settles them all", "Hilbert, Paris 1900"),
        ("To prove that no process exists, \"process\" must be defined",
         "Define it: λ-calculus and Turing machines", "Church, Turing, 1936"),
        ("A search confirms every yes, but never a no",
         "Remainders rule some equations out: mod 4, mod 9", "elementary number theory"),
        (f"x³ + y³ + z³ = 30: no remainder rule, and the solution lies on shell {c30['shell']:,}",
         "No general process exists, so cleverness is unavoidable", "Matiyasevich, 1970"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from Hilbert's question to its negative answer")
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
    f1105, f29 = d["found"]
    i1103, i4 = d["imp"]
    one, sh = d["one"], d["shells"]
    known = {c["n"]: dict(sol=c["sol"], shell=str(c["shell"]), exp=c["exp"]) for c in d["cubes"]}
    js = HQ_JS_TEMPLATE.replace("__KNOWN__", json.dumps(known))
    c30 = next(c for c in d["cubes"] if c["n"] == "30")
    cube_rows = [[f"x³ + y³ + z³ = {c['n']}", f"none through shell {c['cap']} ({c['tried']:,} tuples)", f"({C.pretty(c['sol'])})",
                  f"{c['shell']:,}", "about 10" + str(c['exp']).translate(C._SUP)] for c in d["cubes"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Here the new idea is a question. Earlier eras invented a method for each kind of problem: Pell's equation (Era 2, topic 5), roots of polynomials (Era 2, topic 9), logic as algebra (Era 3, topic 12). In 1900 Hilbert asked for one process that decides every equation of a kind, and in 1928, with Ackermann, for one that decides every statement of logic. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Hilbert's questions. Blue: the negative answers and what they mean today."),
        ]),
        dict(id="search", eyebrow="Try it", title="Search for a solution, or prove there is none", toc="Try it", blocks=[
            dict(type="p", text="Pick an equation. The page first tries remainders: if the left side can never leave the same remainder as n for some divisor m up to 60, there is no solution, and no search is needed. Otherwise it searches outward, shell by shell, as the program does, and stops at the first solution. Try 1103 (impossible), 29 (quick), 30 or 42 (solutions exist, far out of reach) and 114 (nobody knows)."),
            dict(type="widget", html=HQ_HTML, js=js, css=HQ_CSS,
                 fallback=dict(type="svg", name="shells", draw=shells_svg(d), alt="Shells of whole-number points searched in order", width=780),
                 note="In the interactive edition you can choose the equation and watch the search run."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Half a process is easy", toc="How it works", blocks=[
            dict(type="p", text="**Search, shell by shell.** List every tuple of whole numbers so that each one comes up after finitely many steps: first the tuple whose largest entry (in size) is 0, then those whose largest entry is 1, then 2, and so on. Each shell is finite, so the list reaches every tuple. The program checked this for three unknowns, shells 0 to " + sh["R"] + f": {sh['n']:,} tuples, each visited exactly once."),
            dict(type="p", text=f"Run down the list and test each tuple. If the equation has a solution, the search finds one and stops: x² + y² = 1105 stops on shell {f1105['shell']} after {f1105['tried']:,} tuples, at ({f1105['sol']}); x³ + y³ + z³ = 29 stops on shell {f29['shell']} after {f29['tried']} tuples, at ({f29['sol']}). This is the half of Hilbert's tenth problem that is easy: a yes can always be confirmed."),
            dict(type="p", text=f"**Proof by remainders.** The other half needs an argument. Squares leave only the remainders {{{i1103['res']}}} when divided by 4, and no two of them add up to 3; since 1103 = 4 × 275 + 3, x² + y² = 1103 has no solution. Cubes leave only {{{i4['res']}}} when divided by 9, and no three of them add up to 4, so x³ + y³ + z³ = 4 is impossible. The program's search agrees as far as it goes: {i1103['tried']:,} tuples and {i4['tried']:,} tuples, none a solution."),
            dict(type="table", head=["Remainder of a cube mod 9", "Possible sums of three, mod 9"], num=[],
                 rows=[[i4["res"], "0, 1, 2, 3, 6, 7, 8 (never 4 or 5)"]]),
            dict(type="p", text=f"**When neither works.** For x³ + y³ + z³ = 30, no remainder up to 60 forbids a solution, and the program's search through shell {c30['cap']} ({c30['tried']:,} tuples) finds nothing. A solution does exist; the program checks it exactly. It lies on shell {c30['shell']:,}, and the shells inside that one hold about 10{str(c30['exp']).translate(C._SUP)} tuples:"),
            dict(type="table", head=["Equation", "The program's search", "Known solution (checked)", "Its shell", "Tuples in the shells inside"], num=[3],
                 rows=cube_rows),
            dict(type="p", text=f"**One unknown is easy.** For a polynomial in one unknown with whole-number coefficients, any whole-number root divides the constant term, so only finitely many candidates need testing. {C.pretty(one['p1'])} has roots {one['r1']}, found with {one['t1']} tests; {C.pretty(one['p2'])} has none, shown with {one['t2']} tests. On {one['n']} random polynomials the divisor test needed {one['div']:,} evaluations against {one['full']:,} for a full search, and the two agreed every time."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A search that stops whenever the answer is yes is not a decision procedure: it can run for ever when the answer is no. Hilbert asked for a procedure that always stops. For one unknown it exists; for equations in general, Matiyasevich proved in 1970 that it does not."),
        ]),
        dict(id="measured", eyebrow="Measured", title="What each equation cost", toc="Measured", blocks=[
            dict(type="table", head=["Equation", "Outcome", "Tuples tried"], num=[2],
                 rows=[[C.pretty(f1105["eq"]), f"solution on shell {f1105['shell']}", f"{f1105['tried']:,}"],
                       [C.pretty(f29["eq"]), f"solution on shell {f29['shell']}", f"{f29['tried']:,}"],
                       [C.pretty(i1103["eq"]), f"impossible mod {i1103['m']}; searched through shell {i1103['cap']}", f"{i1103['tried']:,}"],
                       [C.pretty(i4["eq"]), f"impossible mod {i4['m']}; searched through shell {i4['cap']}", f"{i4['tried']:,}"]]
                      + [[f"x³ + y³ + z³ = {c['n']}", f"nothing through shell {c['cap']}", f"{c['tried']:,}"] for c in d["cubes"]]),
            dict(type="p", text="A remainder argument settles the question for every tuple at once, not just for those searched. The blind searches for 30, 33 and 42 are hopeless at any speed; the known solutions were found by other methods."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Two questions and their answers", toc="The evidence", blocks=[
            dict(type="p", text="Hilbert's tenth problem (Paris, 1900) asks \"to devise a process according to which it can be determined by a finite number of operations\" whether a Diophantine equation is solvable in whole numbers, and the address insists that \"in mathematics there is no ignorabimus\" (Newson's translation, Project Gutenberg). MacTutor speaks of 23 Paris problems while its own links say 24 (**disputed** count). In 1928 Hilbert and Ackermann posed the Entscheidungsproblem; Church and Turing proved it unsolvable in 1936 (Wikipedia; Dawar, Cambridge)."),
            dict(type="p", text="Matiyasevich completed the negative answer to the tenth problem in January 1970, building on Davis, Putnam and Julia Robinson (MacTutor). Sums of three cubes: no number that leaves 4 or 5 mod 9 is one, and \"it is unknown whether this necessary condition is sufficient\"; 33 and 42 were settled in 2019 (Booker; Booker and Sutherland); 114, 390, 627, 633, 732, 921 and 975 are the open cases below 1,000 (Wikipedia, Sums of three cubes)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Searches that halt only on yes", toc="Full circle", blocks=[
            dict(type="p", text="Hilbert's question is now asked of programs. A tool that looks for a bug, a counterexample or a proof halts when it finds one; when there is none, it may run for ever, and Turing (topic 7) showed that no tool can always tell the difference. Practical tools therefore combine a search with arguments, like the remainders here, that settle some of the no cases."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Remainders mod 9 settle infinitely many sums of three cubes in one line. For 30 a blind search would need about 10{str(c30['exp']).translate(C._SUP)} tries; for 114, nobody knows whether any number of tries will do."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why search in shells instead of trying x = 0, 1, 2, ... with y = 0 fixed?", "That order never reaches y = 1. Shells are finite, so every tuple comes up after finitely many steps."),
            ("Show that x² + y² = 1103 has no solution.", "Squares leave remainder 0 or 1 when divided by 4, so x² + y² leaves 0, 1 or 2. But 1103 leaves 3."),
            ("Can x³ + y³ + z³ = 23 be ruled out by remainders mod 9?", "Yes. 23 leaves 5 when divided by 9; cubes leave 0, 1 or 8, and no three of these add up to 5 mod 9."),
            ("Find the whole-number roots of x³ − 6x² + 11x − 6.", "They must divide 6: try ±1, ±2, ±3, ±6. The roots are 1, 2 and 3."),
            ("If a search has run for a year without finding a solution, what do you know?", "Only that there is no solution in the shells searched so far. Without a separate argument, nothing about the rest."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Mathematical Problems (1900)", text="Hilbert's Paris address in Mary Winston Newson's English translation of 1902, problem 10 included.",
                 draw=C.draw_book, link="https://gutenberg.org/files/71655/71655-h/71655-h.htm", link_text="Project Gutenberg",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "HilbertsQuestions", d["checks"],
                           "every tuple of three unknowns visited exactly once through shell 25, the searches for 1105 and 29, millions of tuples tested against the remainder proofs for 1103 and 4, the known solutions for 30, 33 and 42 checked exactly, and the divisor test against a full search on 3,000 polynomials.",
                           ["static boolean shell(", "static int obstruction("]),
    ]
    return dict(
        title="Hilbert's Questions", date="1900–1928",
        description="Era 4, topic 1 of The Algorithm Evolution Atlas: Hilbert's tenth problem and the Entscheidungsproblem, a search that halts only on yes, and proofs by remainders.",
        lede="In 1900 Hilbert asked for a process that decides, in a finite number of operations, whether any equation in whole numbers has a solution; in 1928 he asked the same of logic. Searching gives half an answer: it confirms every yes and never confirms a no.",
        fieldnote=f"He was certain the process existed: in mathematics, he said, there is no ignorabimus, nothing we shall not know. The search I ran for x³ + y³ + z³ = 30 found nothing in {c30['tried']:,} tries, though an answer exists. Whether one exists for 114, nobody on this planet knows.",
        card=[("When", "Paris 1900; Hilbert and Ackermann 1928"),
              ("Where", "Paris and Göttingen"),
              ("What hurt", "Each kind of equation needed its own method"),
              ("The fix", "Ask for one process that decides them all"),
              ("Answer", "No such process exists (1936 for logic, 1970 for equations)")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `HilbertsQuestions.java`.",
    )
