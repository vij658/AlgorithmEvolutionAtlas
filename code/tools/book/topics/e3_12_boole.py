"""Era 3, topic 12: Boole's algebra of logic. Every number is parsed from BooleanAlgebra.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"law: .*?: only (.+?) ; among ([\d,]+) fractions", ln):
            d["law"] = dict(sols=m.group(1), fracs=m.group(2))
        elif m := re.match(r"expand: .*? all (\d+) functions of two variables .*? all (\d+) of three", ln):
            d["exp"] = dict(two=m.group(1), three=m.group(2))
        elif m := re.match(r"syllogism: all (\d+) forms .*? ; valid: (\d+) ; valid if every class has members: (\d+) ; the first valid form is (\S+),", ln):
            d["syl"] = dict(forms=m.group(1), valid=m.group(2), imp=m.group(3), first=m.group(4))
        elif m := re.match(r"adder: .*? checked on all (\d+) inputs ; chained sixteen times, it added ([\d,]+) random pairs", ln):
            d["add"] = dict(inputs=m.group(1), pairs=m.group(2))
        elif m := re.match(r"circuit: .*?: (\d+) contacts ; .*?: (\d+) ; the majority of three, .*?\((\d+) contacts\), .*?: (\d+) ;", ln):
            d["circ"] = dict(before=m.group(1), after=m.group(2), mb=m.group(3), ma=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def barbara_diagram(d):
    D = Diagram(1000, 250, "A syllogism as algebra: Boole's equations for 'All M are P; all S are M; so all S are P'")
    W, H = 220, 116
    boxes = [("p1", "All M are P", ["nothing is M without P", "m(1 − p) = 0", "so m = mp"], "ink"),
             ("p2", "All S are M", ["nothing is S without M", "s(1 − m) = 0", "so s = sm"], "ink"),
             ("al", "Algebra", ["s = sm = s(mp) = (sm)p", "= sp", ""], "ink"),
             ("c", "So all S are P", ["s = sp", "s(1 − p) = 0", f"one of the {d['syl']['valid']} valid forms"], "red")]
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title")] + [(s, "combo" if j == 1 else "note") for j, s in enumerate(sub) if s], color=col)
    D.edge("p2", "al", ports=("right", "left"))
    D.edge("al", "c", ports=("right", "left"))
    D.edge("p1", "p2", ports=("right", "left"), label="and")
    D.text(20, 30, "WORDS BECOME EQUATIONS IN 0 AND 1; REASONING BECOMES SUBSTITUTION", "tag")
    D.text(20, 215, f"The program tested all {d['syl']['forms']} forms of the syllogism this way: {d['syl']['valid']} valid, {d['syl']['imp']} if every class has members. Numbers from BooleanAlgebra.java.", "caption")
    return D


BL_HTML = """
<div class="board bl-board">
  <div style="min-width:0">
    <div class="eyebrow">Build a syllogism</div>
    <div class="bl-row"><select id="bl-t1"></select><select id="bl-o1"><option value="MP">M … P</option><option value="PM">P … M</option></select><span class="bl-eq" id="bl-e1"></span></div>
    <div class="bl-row"><select id="bl-t2"></select><select id="bl-o2"><option value="SM">S … M</option><option value="MS">M … S</option></select><span class="bl-eq" id="bl-e2"></span></div>
    <div class="bl-row">so <select id="bl-t3"></select> S … P <span class="bl-eq" id="bl-e3"></span></div>
    <label class="bl-imp"><input type="checkbox" id="bl-imp"> every class has members</label>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The eight regions (S, M, P each in or out)</div>
    <div class="bl-grid" id="bl-grid"></div>
    <p class="say" id="bl-say" aria-live="polite"></p>
  </div>
</div>
"""

BL_CSS = """
.bl-row{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:6px 0;font-size:14px}
.bl-row select{font:inherit;font-size:13.5px;padding:3px 4px}
.bl-eq{font-family:var(--mono);font-size:13px;color:var(--blue)}
.bl-imp{font-size:13.5px;display:inline-flex;align-items:center;gap:4px;margin-top:6px}
.bl-imp input{width:auto}
.bl-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;margin:6px 0 10px}
.bl-grid div{white-space:pre-line;border:1px solid var(--axis);padding:6px 4px;text-align:center;font-family:var(--mono);font-size:11.5px;background:var(--surface);line-height:1.4}
.bl-grid div.empty{background:var(--wash);color:var(--muted);text-decoration:line-through}
.bl-grid div.some{border-color:var(--blue);color:var(--blue);font-weight:700}
.bl-grid div.cex{border-color:var(--red);color:var(--red);font-weight:700}
.bl-board .say{font-size:14.5px}
"""

BL_JS = r"""
(() => {
  const grid = document.getElementById("bl-grid");
  if (!grid) return;
  const TYPES = { A: "All", E: "No", I: "Some", O: "Some … not" };
  ["bl-t1", "bl-t2", "bl-t3"].forEach((id, i) => { const s = document.getElementById(id); Object.entries(TYPES).forEach(([k, v]) => el("option", { value: k }, s, `${k}: ${v}`)); s.value = "A"; });
  const IDX = { S: 0, M: 1, P: 2 };
  const reg = r => [(r >> 2) & 1, (r >> 1) & 1, r & 1];
  const holds = (w, t, x, y) => { let xy = false, xny = false;
    for (let r = 0; r < 8; r++) { if (!((w >> r) & 1)) continue; const b = reg(r); if (b[x] && b[y]) xy = true; if (b[x] && !b[y]) xny = true; }
    return t === "A" ? !xny : t === "E" ? !xy : t === "I" ? xy : xny; };
  const nonEmpty = (w, c) => { for (let r = 0; r < 8; r++) if (((w >> r) & 1) && reg(r)[c]) return true; return false; };
  const eq = (t, x, y) => { x = x.toLowerCase(); y = y.toLowerCase(); return t === "A" ? `${x}(1 − ${y}) = 0` : t === "E" ? `${x}${y} = 0` : t === "I" ? `${x}${y} ≠ 0` : `${x}(1 − ${y}) ≠ 0`; };
  const name = r => { const b = reg(r); return ["S", "M", "P"].map((n, i) => b[i] ? n : "not " + n).join(", "); };
  function show() {
    const t1 = document.getElementById("bl-t1").value, t2 = document.getElementById("bl-t2").value, t3 = document.getElementById("bl-t3").value;
    const o1 = document.getElementById("bl-o1").value, o2 = document.getElementById("bl-o2").value, imp = document.getElementById("bl-imp").checked;
    const [a1, b1] = [o1[0], o1[1]], [a2, b2] = [o2[0], o2[1]];
    document.getElementById("bl-e1").textContent = eq(t1, a1, b1);
    document.getElementById("bl-e2").textContent = eq(t2, a2, b2);
    document.getElementById("bl-e3").textContent = eq(t3, "S", "P");
    let cex = -1;
    for (let w = 0; w < 256 && cex < 0; w++) {
      if (imp && !(nonEmpty(w, 0) && nonEmpty(w, 1) && nonEmpty(w, 2))) continue;
      if (holds(w, t1, IDX[a1], IDX[b1]) && holds(w, t2, IDX[a2], IDX[b2]) && !holds(w, t3, 0, 2)) cex = w;
    }
    grid.innerHTML = "";
    for (let r = 7; r >= 0; r--) {
      let cls = "", tag = "";
      if (cex >= 0) { if ((cex >> r) & 1) { cls = "cex"; tag = "has members"; } else { cls = "empty"; tag = "empty"; } }
      el("div", { class: cls }, grid, name(r) + (tag ? `\n${tag}` : ""));
    }
    document.getElementById("bl-say").textContent = cex < 0
      ? `Valid: no way of filling the eight regions makes both premises true and the conclusion false${imp ? ", when every class has members" : ""}. Boole's equations for the premises force the equation of the conclusion.`
      : "Not valid. The red regions have members and the struck-out ones are empty: both premises hold, yet the conclusion fails.";
  }
  ["bl-t1", "bl-t2", "bl-t3", "bl-o1", "bl-o2", "bl-imp"].forEach(id => document.getElementById(id).addEventListener("change", show));
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Boole's algebra combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "syl": (20, 20, "Syllogisms", "valid argument forms, learned by heart", "Aristotle", "ink"),
        "alg": (395, 20, "Symbolic algebra", "letters obey rules", "al-jabr, Era 2 topic 6", "ink"),
        "bin": (770, 20, "Two values", "binary arithmetic", "topic 6", "ink"),
        "boo": (395, 170, "Boole's algebra", "⊕ classes as symbols, with x² = x", "1847; 1854", "red"),
        "ven": (20, 330, "Regions of classes", "eight regions for three classes", "how the program checks", "ink"),
        "sha": (395, 330, "Switching circuits", "relays obey Boole's algebra", "Shannon, 1937", "blue"),
        "cpu": (770, 330, "Logic gates", "every digital circuit", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("syl", "boo", ports=("bottom", "top:0.15"))
    D.edge("alg", "boo", ports=("bottom", "top"))
    D.edge("bin", "boo", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("boo", "ven", ports=("bottom:0.1", "top:0.7"), dashed=True)
    D.edge("boo", "sha", ports=("bottom", "top"))
    D.edge("sha", "cpu", ports=("right", "left"))
    D.text(20, 615, "Dashed: Boole's 0 and 1 are 'nothing' and 'everything', not binary digits; the identification came later. ", "caption")
    return D


def chain(d):
    s, c = d["syl"], d["circ"]
    steps = [
        ("Logic was a catalogue of argument forms, checked by memory",
         "Write classes as symbols; reasoning becomes algebra with x² = x", "Boole, 1847 and 1854"),
        (f"Which of the {s['forms']} syllogism forms are valid?",
         f"Calculate it: {s['valid']} valid, {s['imp']} if every class has members", "algebra over 0 and 1"),
        ("Circuits of relays grew large and were hard to reason about",
         "Contacts in series multiply, in parallel add: Boole's algebra designs circuits", "Shannon, 1937"),
        (f"Circuits as first drawn waste parts: {c['before']} contacts",
         f"Simplify by the algebra: {c['after']} contacts do the same", "Shannon"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from syllogisms to circuits")
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
    lw, ex, sy, ad, ci = d["law"], d["exp"], d["syl"], d["add"], d["circ"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Logic since Aristotle was a list of valid argument forms; algebra since al-Khwarizmi (Era 2, topic 6) let letters obey rules. Boole wrote logic in letters, found the one rule that sets it apart from arithmetic, x² = x, and turned reasoning into calculation. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Boole's algebra. Blue: where it went in the twentieth century."),
        ]),
        dict(id="syllogism", eyebrow="Try it", title="Check a syllogism by algebra", toc="Try it", blocks=[
            dict(type="p", text="Choose two premises and a conclusion. Each becomes one of Boole's equations (blue). The page then checks every way the eight regions of three classes can be filled: if some way makes both premises true and the conclusion false, it shows it in red. The starting form is the classic \"All M are P; all S are M; so all S are P\"."),
            dict(type="widget", html=BL_HTML, js=BL_JS, css=BL_CSS,
                 fallback=dict(type="diagram", name="barbara", diagram=barbara_diagram(d)),
                 note="In the interactive edition you can build any of the 256 syllogism forms and see whether it is valid, with a counterexample when it is not."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="An algebra of 0 and 1", toc="How it works", blocks=[
            dict(type="p", text=f"Let x stand for a class (men) and xy for the things in both x and y (mortal men). Selecting men from men gives men, so xx = x. Boole: \"x² = x\" is \"the expression of a second general law\" of these symbols, and \"the equation x² = x, considered as algebraic, has no other roots than 0 and 1\". The program checked: among the whole numbers from −1,000 to 1,000 only {lw['sols']} satisfy it, and none of {lw['fracs']} fractions does."),
            dict(type="p", text="So the symbols behave like numbers that are only 0 (nothing) or 1 (everything); 1 − x means \"not x\", and x(1 − x) = 0: nothing is both x and not x. \"All x are y\" says nothing is x without y: x(1 − y) = 0. Then a syllogism is substitution:"),
            dict(type="diagram", name="barbara-steps", diagram=barbara_diagram(d)),
            dict(type="p", text=f"Boole also showed that any expression can be expanded as f(x) = f(1) x + f(0)(1 − x), a truth table written as one formula. The program checked the expansion for all {ex['two']} functions of two variables and all {ex['three']} of three."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Find the algebra that a subject obeys, and its reasoning becomes calculation. For logic the algebra is that of 0 and 1, with the single extra law x² = x."),
        ]),
        dict(id="measured", eyebrow="Measured", title="All 256 syllogisms, and two circuits", toc="Measured", blocks=[
            dict(type="table", head=["Test", "Result"], num=[],
                 rows=[[f"All {sy['forms']} syllogism forms (4 figures × 4³ moods), against every way three classes can share members", f"{sy['valid']} valid"],
                       ["The same, if every class is assumed to have members", f"{sy['imp']} valid"],
                       ["A full adder written in Boole's algebra", f"correct on all {ad['inputs']} inputs"],
                       ["Sixteen of them chained", f"{ad['pairs']} random 16-bit additions, all correct"],
                       ["xy + x(1 − y) + (1 − x)y, as relay contacts", f"{ci['before']} contacts; simplified to x + y − xy: {ci['after']}"],
                       ["Majority of three, xy + xz + yz", f"{ci['mb']} contacts; factored as x(y + z) + yz: {ci['ma']}"]]),
            dict(type="p", text="Which syllogisms are valid had been a matter of memorised lists for two thousand years. With Boole's algebra a program can simply check every form against every possibility."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="From a schoolroom in Lincoln to Cork", toc="The evidence", blocks=[
            dict(type="p", text="Boole was born on 2 November 1815 in Lincoln and died on 8 December 1864 near Cork; in August 1849 he was announced as \"the first Professor of Mathematics at Queen's College, Cork\" (MacTutor). *The Mathematical Analysis of Logic* (1847) was subtitled \"a calculus of deductive reasoning\"; *An Investigation of the Laws of Thought* (1854), his \"greatest work\" (Lynch), \"approached logic in a new way reducing it to a simple algebra\" (MacTutor). What prompted the 1847 book is often said to be the dispute between De Morgan and Hamilton, but the opened sources do not say so (**conjecture**)."),
            dict(type="p", text="Shannon's MIT thesis (signed 10 August 1937, published 1938) showed that Boolean algebra \"could be used to simplify the arrangement of the relays\", and that \"This calculus is shown to be exactly analogous to the Calculus of Propositions used in the symbolic study of logic\". Goldstine called it \"surely ... one of the most important master's theses ever written\"; Gardner \"possibly the most important, and also the most famous, master's thesis of the century\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Thought, then circuits", toc="Full circle", blocks=[
            dict(type="p", text="Boole called his book the laws of thought. Eighty-three years later, a student noticed that a relay contact obeys the same laws: closed is 1, open is 0, contacts in series multiply, contacts in parallel add."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program wrote an adder in nothing but Boole's algebra, chained sixteen copies and added {ad['pairs']} random pairs of 16-bit numbers without an error: binary arithmetic (topic 6) with the carry of Pascal's wheels (topic 3), built from the laws of thought. Digital circuits are still designed in this algebra."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why is xx = x for classes?", "Selecting the men from the class of men gives the class of men again."),
            ("Write \"No x are y\" as an equation.", "xy = 0: nothing is in both."),
            ("What does x(1 − x) = 0 say?", "Nothing is both x and not x: the principle of contradiction, as algebra."),
            ("Why are there 256 syllogism forms?", "Each of the three statements is one of four types (4³ = 64 moods), and the middle term can sit in four arrangements (figures): 64 × 4 = 256."),
            ("Why does a parallel pair of contacts compute x + y − xy?", "Current flows if either is closed; when both are closed, x + y would count 2, so subtract xy."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="An Investigation of the Laws of Thought (1854)", text="Boole's book, public domain, as Project Gutenberg eBook 15114.",
                 draw=C.draw_book, link="https://www.gutenberg.org/etext/15114", link_text="Project Gutenberg",
                 licence="Drawn placeholder."),
            dict(title="A Symbolic Analysis of Relay and Switching Circuits", text="Claude Shannon's MIT master's thesis, signed 10 August 1937.",
                 draw=C.draw_manuscript, link="https://dspace.mit.edu/bitstream/handle/1721.1/11173/34541425.pdf%20?sequence=1", link_text="MIT DSpace",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "BooleanAlgebra", d["checks"],
                           "that only 0 and 1 satisfy x² = x, Boole's expansion on every function of two and three variables, all 256 syllogism forms against all 256 ways three classes can share members, a full adder and 200,000 16-bit additions, and two circuit simplifications.",
                           ["static boolean holds("]),
    ]
    return dict(
        title="Boole's Algebra of Logic", date="1847–1854",
        description="Era 3, topic 12 of The Algorithm Evolution Atlas: George Boole's algebra of logic with x² = x, the 256 syllogisms checked by algebra, and Shannon's relay circuits.",
        lede="A self-taught schoolmaster wrote logic as algebra: letters for classes, multiplication for \"and\", and one law that ordinary numbers break, x × x = x. Only two numbers obey it, 0 and 1. Reasoning became calculation, and eighty years later, circuitry.",
        fieldnote="For two thousand years, valid arguments were a list to be memorised. In Lincoln I found a man who turned the list into algebra, so that the valid forms could be calculated rather than remembered. A student later found the same algebra in a box of relays.",
        card=[("When", "1847 and 1854; Shannon 1937"),
              ("Where", "Lincoln and Cork; Shannon at MIT"),
              ("What hurt", "Logic as a catalogue of syllogisms"),
              ("The fix", "Classes as symbols, with x² = x: an algebra of 0 and 1"),
              ("Cost", "Substitution and multiplication instead of memory")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `BooleanAlgebra.java`.",
    )
