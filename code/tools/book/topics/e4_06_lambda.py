"""Era 4, topic 6: Church's lambda calculus. Every number is parsed from LambdaCalculus.java's output."""
import re

import common as C
from diagrams import Diagram


def lam(s):
    return s.replace("\\", "λ")


def parse(text: str) -> dict:
    d = {"trace": []}
    for ln in text.splitlines():
        if m := re.match(r"numerals: Church 1936 \(from 1\): 1 = (\S+), 2 = (\S+), 3 = (\S+) ; today \(from 0\): 0 = (\S+),", ln):
            d["num"] = dict(one=m.group(1), two=m.group(2), three=m.group(3), zero=m.group(4))
        elif m := re.match(r"arith: .*?: (\d+) results, all equal to ordinary arithmetic, (\d+) reduction steps in all ; EXP m 0 gives (\S+) in all (\d+) cases.*? ; steps: (.+)$", ln):
            d["ar"] = dict(n=int(m.group(1)), steps=int(m.group(2)), eta=m.group(3), etan=m.group(4),
                           sample=re.findall(r"(\w+ \d+(?: \d+)?) in (\d+)", m.group(5)))
        elif m := re.match(r"trace: (\d+) (.+)$", ln):
            d["trace"].append((int(m.group(1)), m.group(2)))
        elif m := re.match(r"fact: factorial with Y and no named recursion: (.+)$", ln):
            d["fact"] = re.findall(r"(\d)! = (\d+) in (\d+) steps", m.group(1))
        elif m := re.match(r"omega: .*? leftmost-outermost order reaches (\S+) in (\d+) step, arguments-first order is still working after (\d+) steps$", ln):
            d["om"] = dict(nf=m.group(1), steps=m.group(2), app=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def trace_svg(d):
    def draw(t, standalone):
        out = [C.text(20, 30, "PLUS 2 3, reduced step by step (leftmost, outermost redex first)", t["ink"], 15, "start", 700)]
        for k, (i, s) in enumerate(d["trace"]):
            y = 66 + k * 34
            out.append(C.text(30, y, str(i), t["red"] if i in (0, len(d["trace"]) - 1) else t["muted"], 14, "end", 700))
            out.append(f'<text x="44" y="{y}" style="fill:{t["ink"]};font-size:14px;font-family:ui-monospace,Menlo,Consolas,monospace">{lam(s).replace("&", "&amp;").replace("<", "&lt;")}</text>')
        y = 66 + len(d["trace"]) * 34
        out.append(C.text(20, y + 4, f"Step 0 is PLUS applied to 2 and 3; step {d['trace'][-1][0]} is the numeral 5: λab. a applied five times to b.", t["muted"], 12.5))
        out.append(C.text(20, y + 22, "Variable names are given by depth, in Church's compact style: λab.a(b) means λa.λb.a b.", t["muted"], 12.5))
        return C.svg_doc(860, y + 36, "".join(out), "The reduction of PLUS 2 3 to 5 in the lambda calculus", t, standalone, 0.55, 860)
    return draw


LC_HTML = """
<div class="board lc-board">
  <div style="min-width:0">
    <div class="presets" id="lc-pre"></div>
    <div class="controls">
      <button class="primary" id="lc-step">Reduce one step</button>
      <button id="lc-run">Run to the end</button>
    </div>
    <p class="lc-note">The highlighted part is the next redex: a function applied to an argument. Names are given by depth: λab.a(b) means λa.λb.a b.</p>
  </div>
  <div style="min-width:0">
    <ol class="lc-steps" id="lc-steps" start="0"></ol>
    <p class="say" id="lc-say" aria-live="polite"></p>
  </div>
</div>
"""

LC_CSS = """
.lc-board .presets button{font-family:var(--mono);font-size:12.5px}
.lc-steps{margin:6px 0 10px;padding-left:2.2em;font:13px var(--mono);display:grid;gap:5px;max-height:420px;overflow:auto}
.lc-steps li{overflow-wrap:anywhere}
.lc-steps mark{background:color-mix(in srgb,var(--yellow) 45%,transparent);color:inherit;padding:0 1px}
.lc-note{font-size:12.5px;color:var(--muted)}
"""

LC_JS = r"""
(() => {
  const ol = document.getElementById("lc-steps");
  if (!ol) return;
  const V = i => ({k: "v", i}), L = b => ({k: "l", b}), A = (f, a) => ({k: "a", f, a});
  const shift = (t, d, c) => t.k === "v" ? (t.i >= c ? V(t.i + d) : t) : t.k === "l" ? L(shift(t.b, d, c + 1)) : A(shift(t.f, d, c), shift(t.a, d, c));
  const subst = (t, j, s) => t.k === "v" ? (t.i === j ? s : t) : t.k === "l" ? L(subst(t.b, j + 1, shift(s, 1, 0))) : A(subst(t.f, j, s), subst(t.a, j, s));
  const beta = (b, a) => shift(subst(b, 0, shift(a, 1, 0)), -1, 0);
  function redex(t, path = []) {           // path to the leftmost, outermost redex
    if (t.k === "a") {
      if (t.f.k === "l") return path;
      const p = redex(t.f, path.concat("f")); if (p) return p;
      return redex(t.a, path.concat("a"));
    }
    if (t.k === "l") return redex(t.b, path.concat("b"));
    return null;
  }
  function at(t, path, fn) {
    if (!path.length) return fn(t);
    const [h, ...r] = path;
    return h === "f" ? A(at(t.f, r, fn), t.a) : h === "a" ? A(t.f, at(t.a, r, fn)) : L(at(t.b, r, fn));
  }
  function show(t, depth, mark, path = []) {
    const hit = mark && mark.length === path.length && mark.every((x, i) => x === path[i]);
    let s;
    if (t.k === "v") s = String.fromCharCode(97 + depth - 1 - t.i);
    else if (t.k === "l") {
      let names = "", b = t, d = depth, p = path;
      while (b.k === "l") { names += String.fromCharCode(97 + d); d++; b = b.b; p = p.concat("b"); }
      s = "λ" + names + "." + show(b, d, mark, p);
    } else {
      const f = show(t.f, depth, mark, path.concat("f"));
      s = (t.f.k === "l" ? "(" + f + ")" : f) + "(" + show(t.a, depth, mark, path.concat("a")) + ")";
    }
    return hit ? "<mark>" + s + "</mark>" : s;
  }
  // a small parser: \x.M, application by juxtaposition, numerals and the names below
  const DEF = {};
  function parse(src) {
    let i = 0;
    const ws = () => { while (src[i] === " ") i++; };
    function term(env) {
      ws();
      if (src[i] === "\\") { i++; let n = ""; while (/\w/.test(src[i])) n += src[i++]; i++; return L(term([n, ...env])); }
      let t = atom(env);
      for (;;) { ws(); if (i >= src.length || src[i] === ")") return t; if (src[i] === "\\") return A(t, term(env)); t = A(t, atom(env)); }
    }
    function atom(env) {
      ws();
      if (src[i] === "(") { i++; const t = term(env); ws(); i++; return t; }
      let n = ""; while (i < src.length && /\w/.test(src[i])) n += src[i++];
      const k = env.indexOf(n);
      if (k >= 0) return V(k);
      if (/^\d+$/.test(n)) { let b = V(0); for (let j = 0; j < +n; j++) b = A(V(1), b); return L(L(b)); }
      return DEF[n];
    }
    return term([]);
  }
  [["SUCC", "\\n.\\f.\\x.f (n f x)"], ["PLUS", "\\m.\\n.\\f.\\x.m f (n f x)"], ["MULT", "\\m.\\n.\\f.m (n f)"], ["EXP", "\\m.\\n.n m"],
   ["PRED", "\\n.\\f.\\x.n (\\g.\\h.h (g f)) (\\u.x) (\\u.u)"], ["OMEGA", "(\\x.x x) (\\x.x x)"]].forEach(([k, v]) => { DEF[k] = parse(v); });
  const PRE = ["PLUS 2 3", "MULT 2 3", "SUCC 2", "PRED 2", "EXP 2 2", "(\\x.\\y.y) OMEGA", "OMEGA"];
  let term, n;
  const unchurch = t => { if (t.k !== "l" || t.b.k !== "l") return -1; let b = t.b.b, c = 0; while (b.k === "a" && b.f.k === "v" && b.f.i === 1) { c++; b = b.a; } return b.k === "v" && b.i === 0 ? c : -1; };
  function load(src) { term = parse(src); n = 0; ol.innerHTML = ""; add(); document.getElementById("lc-say").textContent = "Source: " + src.replace(/\\/g, "λ"); }
  function add() {
    const r = redex(term);
    const li = el("li", {}, ol);
    li.innerHTML = show(term, 0, r);            // letters, λ, dots and brackets only, plus the <mark>
    ol.scrollTop = ol.scrollHeight;
    return r;
  }
  function step() {
    const r = redex(term);
    const say = document.getElementById("lc-say");
    if (!r) { const v = unchurch(term); say.textContent = `Normal form after ${n} step${n === 1 ? "" : "s"}` + (v >= 0 ? `: the numeral ${v}.` : "."); return false; }
    term = at(term, r, t => beta(t.f.b, t.a));
    n++;
    add();
    if (!redex(term)) { const v = unchurch(term); say.textContent = `Normal form after ${n} step${n === 1 ? "" : "s"}` + (v >= 0 ? `: the numeral ${v}.` : "."); }
    else if (n >= 60) say.textContent = `${n} steps and still going: this term may have no normal form.`;
    else say.textContent = `${n} step${n === 1 ? "" : "s"} so far.`;
    return true;
  }
  const pre = document.getElementById("lc-pre");
  PRE.forEach(p => { const b = el("button", {type: "button"}, pre, p.replace(/\\/g, "λ")); b.addEventListener("click", () => load(p)); });
  document.getElementById("lc-step").addEventListener("click", step);
  document.getElementById("lc-run").addEventListener("click", () => { for (let k = 0; k < 60 && step(); k++); });
  load(PRE[0]);
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the lambda calculus combined older ideas, and where it led")
    W = 210
    nodes = {
        "hil": (20, 20, "Hilbert's questions", "\"a finite number of operations\"", "topic 1", "ink"),
        "comb": (395, 20, "Combinators", "logic without variables", "Schönfinkel, 1920", "ink"),
        "rec": (770, 20, "Recursive functions", "defined by equations", "Herbrand and Gödel", "ink"),
        "lc": (395, 170, "Church's λ-calculus", "⊕ functions and substitution are enough", "1932–1936", "red"),
        "th": (20, 330, "Church's thesis", "calculable = λ-definable = recursive", "1936", "ink"),
        "un": (395, 330, "Unsolvable problems", "normal forms; the Entscheidungsproblem", "1936", "ink"),
        "tm": (770, 330, "Turing's machines", "the same functions, by a machine", "topic 7", "ink"),
        "today": (395, 480, "Functional programming", "programs as λ-terms; types", "later", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("hil", "lc", ports=("bottom", "top:0.15"))
    D.edge("comb", "lc", ports=("bottom", "top"))
    D.edge("rec", "lc", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("lc", "th", ports=("bottom:0.1", "top:0.7"))
    D.edge("lc", "un", ports=("bottom", "top"))
    D.edge("lc", "tm", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("un", "today", ports=("bottom", "top"))
    D.edge("th", "today", ports=("bottom:0.7", "left:0.5"))
    D.text(20, 615, "Dashed: recursive functions were shown to define the same functions (Kleene), and so were Turing's machines; not lines of descent.", "caption")
    return D


def chain(d):
    steps = [
        ("Hilbert's \"process\" had no mathematical definition",
         "Functions and substitution only: call a function calculable if a λ-term computes it", "Church, 1932–1936"),
        ("Is that the right definition?",
         "It defines the same functions as recursion (Kleene) and as Turing's machines", "1936"),
        ("Some terms never finish reducing: (λx.x x)(λx.x x)",
         "No effective test can tell which terms have a normal form", "Church, Theorem XVIII, 1936"),
        ("Hilbert's decision problem for logic",
         "Unsolvable: no process decides first-order validity", "Church, J. Symbolic Logic, 1936"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a definition of computing to unsolvable problems")
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
    nm, ar, fa, om = d["num"], d["ar"], d["fact"], d["om"]
    samp = dict(ar["sample"])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Hilbert asked for \"a finite number of operations\" without saying what an operation is (topic 1). Schönfinkel's combinators (1920) had shown that logic can be built from functions alone. Church's addition was a notation for functions with variables, λx.M, and a single rule for computing with it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Church's λ-calculus. Blue: where it went."),
        ]),
        dict(id="reduce", eyebrow="Try it", title="Compute by substitution", toc="Try it", blocks=[
            dict(type="p", text=f"Pick an expression and reduce it one step at a time. Each step finds the leftmost, outermost place where a function λx.M meets an argument N, and replaces the pair by M with N put in place of x. PLUS 2 3 becomes the numeral 5 in {samp.get('PLUS 2 3')} steps, as in the program. Try the last two: one never finishes, and the other finishes only because the first step throws the endless part away."),
            dict(type="widget", html=LC_HTML, js=LC_JS, css=LC_CSS,
                 fallback=dict(type="svg", name="trace", draw=trace_svg(d), alt="The reduction of PLUS 2 3 to 5 in the lambda calculus", width=860),
                 note="In the interactive edition you can reduce several expressions one step at a time."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 4, what can be computed", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Three kinds of term, one rule", toc="How it works", blocks=[
            dict(type="p", text="**Terms.** A variable x; a function λx.M, which given x returns M; an application M N, which applies M to N. **The rule.** (λx.M) N becomes M with N in place of x (β-reduction). A term with nothing left to reduce is in normal form: that is the answer."),
            dict(type="p", text=f"**Numbers.** The numeral n applies a function n times: Church wrote 1 = {lam(nm['one'])}, 2 = {lam(nm['two'])}, 3 = {lam(nm['three'])} in 1936, starting from 1; today the list starts with 0 = {lam(nm['zero'])}. Arithmetic composes: PLUS = λm.λn.λf.λx.m f (n f x) applies f n times and then m times more; MULT = λm.λn.λf.m (n f) applies \"f n times\" m times; EXP = λm.λn.n m."),
            dict(type="table", head=["Term", "Reduction steps to the answer"], num=[1], rows=[[k, v] for k, v in ar["sample"]]),
            dict(type="p", text=f"The program checks PLUS, MULT and EXP on all numerals from 0 to 6, and the predecessor on 0 to 10: {ar['n']} results, every one equal to ordinary arithmetic. One wrinkle: EXP m 0 reduces to {lam(ar['eta'])}, the identity function, which is the numeral 1 only after a further rule (η-conversion) that this program does not use."),
            dict(type="p", text="**Recursion without names.** Y = λg.(λx.g (x x)) (λx.g (x x)) reduces Y g to g (Y g), so a function can call itself without having a name. The program builds factorial from Y, the predecessor and a test for zero:"),
            dict(type="table", head=["n", "n! by λ-reduction", "Reduction steps"], num=[0, 1, 2], rows=[[n, v, f"{int(s):,}"] for n, v, s in fa]),
            dict(type="callout", kind="key", label="Key idea",
                 text="Nothing but functions and substitution is enough to compute anything that can be computed, which is why Church proposed λ-definability as the meaning of \"effectively calculable\". The same power means that whether a term ever reaches a normal form cannot be decided in general."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Order matters, and some terms never stop", toc="Measured", blocks=[
            dict(type="p", text=f"(λx.x x)(λx.x x) reduces in one step to itself, so it has no normal form; the program confirms it is unchanged after 1,000 steps. Applied as the argument of λx.λy.y, which ignores its argument, it is thrown away: the leftmost, outermost order reaches {lam(om['nf'])} in {om['steps']} step, while reducing the argument first is still working after {int(om['app']):,} steps. Factorial's cost grows fast in this unary world: 5! = 120 takes {int(fa[-1][2]):,} steps."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Princeton, 1935–1936", toc="The evidence", blocks=[
            dict(type="p", text="\"An Unsolvable Problem of Elementary Number Theory\" was presented to the American Mathematical Society on 19 April 1935 and printed in the *American Journal of Mathematics* in April 1936. It proposes that \"a function of positive integers shall be called effectively calculable if it is recursive\", credits the definition of recursiveness jointly to Herbrand and Gödel and \"the proof of equivalence of the two notions\" chiefly to Kleene, and proves that \"There is no recursive function of a formula C, whose value is 2 or 1 according as C has a normal form or not\" (Theorem XVIII)."),
            dict(type="p", text="\"A Note on the Entscheidungsproblem\" (*Journal of Symbolic Logic* 1, received 15 April 1936) concludes that the general case \"is unsolvable\" (Church). Church's original logical system was \"logically inconsistent in 1935\"; the computational part survived as the untyped λ-calculus (Wikipedia). That calculability means λ-definability is a thesis, not a theorem: MacTutor quotes the view that it \"is probably true but cannot be rigorously proved\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Programs built from functions", toc="Full circle", blocks=[
            dict(type="p", text="Programming languages that treat functions as values, pass them to other functions and build recursion from them carry Church's notation forward; many still spell an anonymous function with the word lambda. Typed versions of the calculus, begun by Church in 1940, underlie the type systems that check programs before they run."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"PLUS 2 3 reaches 5 in {samp.get('PLUS 2 3')} substitutions. Nothing else happens in this calculus, and yet it computes everything a computer can."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Reduce (λx.x) y.", "Put y in place of x in x: the answer is y. The identity function returns its argument."),
            ("What does the numeral 2 do to a function f?", "It returns λx.f (f x): f applied twice."),
            ("Why does MULT = λm.λn.λf.m (n f) multiply?", "n f applies f n times; m (n f) applies that m times: f applied m × n times."),
            ("What is one step of (λx.x x)(λx.x x)?", "Put λx.x x in place of x in x x: (λx.x x)(λx.x x) again. It never changes, so it never ends."),
            ("Why is reducing the leftmost, outermost redex first a safe choice?", "If any order reaches a normal form, this one does: it never wastes effort on an argument that will be thrown away."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="An Unsolvable Problem of Elementary Number Theory (1936)", text="Church's paper with his numerals and Theorem XVIII.",
                 draw=C.draw_manuscript, link="https://courses.fit.cvut.cz/NI-VYC/church-an-unsolvable-problem-of-elementary-number-theory.pdf", link_text="Czech Technical University course page", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "LambdaCalculus", d["checks"],
                           f"{ar['n']} arithmetic results against ordinary arithmetic, the identity from EXP m 0, the trace of PLUS 2 3, factorial up to 5! through the Y combinator, and the term that reduces to itself.",
                           ["static T beta(", "static T stepNormal("]),
    ]
    return dict(
        title="Church's Lambda Calculus", date="1936",
        description="Era 4, topic 6 of The Algorithm Evolution Atlas: Church's lambda calculus, Church numerals, the Y combinator, and the first unsolvable problem.",
        lede="Church built a calculus with three kinds of term and one rule, substitution, and proposed that a function is calculable exactly when this calculus can compute it. With that definition he proved the first problems unsolvable.",
        fieldnote=f"In this calculus the number 3 is the instruction \"do it three times\", and adding is doing it a few times more. PLUS 2 3 became 5 in {samp.get('PLUS 2 3')} substitutions. One term, fed to itself, substitutes for ever, and Church proved that no procedure can always tell such terms from the rest.",
        card=[("When", "Presented 19 April 1935; printed 1936"),
              ("Where", "Princeton"),
              ("What hurt", "No definition of \"effectively calculable\""),
              ("The fix", "λ-definable functions; one rule, substitution"),
              ("Cost", f"5! takes {int(fa[-1][2]):,} reduction steps")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `LambdaCalculus.java`.",
    )
