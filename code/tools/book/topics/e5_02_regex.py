"""Era 5, topic 2: regular expressions. Every number is parsed from RegularExpressions.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"thompson: (\S+) has s = (\d+) symbols .*? c = (\d+) joins ; the machine has 2s - c = (\d+) states ; the same count held for (\d+) random", ln):
            d["th"] = dict(rx=m.group(1), s=m.group(2), c=m.group(3), states=m.group(4), n=m.group(5))
        elif m := re.match(r"three: (\S+) matches .*? checked on all ([\d,]+) strings of 1 to (\d+) digits \(([\d,]+) accepted\) ; the first numerals it accepts: ([01 ]+) ; Thompson machine (\d+) states, subset machine (\d+), smallest machine (\d+)$", ln):
            g = m.groups()
            d["three"] = dict(rx=g[0], n=g[1], digits=g[2], acc=g[3], first=g[4].split(), th=g[5], sub=g[6], min=g[7])
        elif m := re.match(r"random: ([\d,]+) random expressions, (\d+) random strings each ; .*? all ([\d,]+) cases \(([\d,]+) matches\)$", ln):
            d["rand"] = dict(e=m.group(1), s=m.group(2), cases=m.group(3), yes=m.group(4))
        elif m := re.match(r"subset: (\S+): (\d+) Thompson states become (\d+) sets of states ; (.*) ; smallest equivalent machine: (\d+) states$", ln):
            rows = re.findall(r"D(\d+) = \{([\d, ]+)\} a->D(\d+) b->D(\d+)( accept)?", m.group(4))
            d["sub"] = dict(rx=m.group(1), th=m.group(2), n=m.group(3), rows=rows, min=m.group(5))
        elif ln.startswith("blowup: "):
            d["blow"] = re.findall(r"n=(\d+): (\d+) / (\d+) / (\d+)", ln)
        elif ln.startswith("backtrack: "):
            d["bt"] = re.findall(r"(\d+) letters: backtracking ([\d,]+) steps, state sets ([\d,]+)", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def nfa_svg(d):
    th = d["th"]

    def draw(t, standalone):
        o = []
        # Thompson's pieces: a symbol, either, repeat
        def state(x, y, label, accept=False):
            s = C.circle(x, y, 15, t["surface"], t["ink2"], 1.5)
            if accept:
                s += C.circle(x, y, 11, "none", t["ink2"], 1.2)
            return s + C.text(x, y + 4, label, t["muted"], 10, "middle")

        def arrow(x1, y1, x2, y2, lab="", col=None, curve=0):
            col = col or t["ink2"]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + curve
            p = C.path(f"M{x1},{y1} Q{mx},{my} {x2},{y2}", col, "none", 1.4)
            import math
            ang = math.atan2(y2 - my, x2 - mx)
            hx, hy = x2 - 6 * math.cos(ang), y2 - 6 * math.sin(ang)
            p += C.path(f"M{x2},{y2} L{hx - 4 * math.sin(ang)},{hy + 4 * math.cos(ang)} L{hx + 4 * math.sin(ang)},{hy - 4 * math.cos(ang)} Z", None, col)
            if lab:
                p += C.text(mx, my - 6 if curve <= 0 else my + 14, lab, t["blue"] if lab not in ("ε",) else t["muted"], 13, "middle", 700)
            return p
        o.append(C.text(20, 22, "a symbol", t["ink"], 13, "start", 700))
        o += [state(40, 60, ""), state(130, 60, ""), arrow(56, 60, 114, 60, "a")]
        o.append(C.text(200, 22, "E | F (either)", t["ink"], 13, "start", 700))
        o += [state(220, 75, ""), C.rect(280, 30, 70, 30, t["wash"], t["rule"], 1, 4), C.text(315, 50, "E", t["ink"], 13, "middle", 700),
              C.rect(280, 90, 70, 30, t["wash"], t["rule"], 1, 4), C.text(315, 110, "F", t["ink"], 13, "middle", 700), state(410, 75, ""),
              arrow(234, 68, 278, 46, "ε", curve=-6), arrow(234, 82, 278, 104, "ε", curve=6), arrow(352, 46, 396, 68, "ε", curve=-6), arrow(352, 104, 396, 82, "ε", curve=6)]
        o.append(C.text(470, 22, "E* (repeat)", t["ink"], 13, "start", 700))
        o += [state(490, 75, ""), C.rect(545, 60, 70, 30, t["wash"], t["rule"], 1, 4), C.text(580, 80, "E", t["ink"], 13, "middle", 700), state(670, 75, ""),
              arrow(506, 75, 543, 75, "ε"), arrow(617, 75, 654, 75, "ε"), arrow(615, 62, 547, 62, "ε", curve=-26), arrow(494, 90, 666, 90, "ε", curve=40)]
        o.append(C.text(20, 168, "Then (EF): the end of E becomes the start of F, so each join removes one state.", t["muted"], 12))
        o.append(C.text(20, 188, f"Two states per symbol, |, or *, minus one per join: for {th['rx']}, s = {th['s']} and c = {th['c']}, so 2s - c = {th['states']} states.", t["muted"], 12))
        o.append(C.text(20, 208, "ε marks an arrow the machine may follow without reading a letter.", t["muted"], 12))
        return C.svg_doc(720, 222, "".join(o), "Thompson's construction: the pieces for a symbol, for either, and for repeat", t, standalone, 0.55, 720)
    return draw


RX_HTML = """
<div class="board rx-board">
  <div style="min-width:0">
    <label class="eyebrow" for="rx-pat">Pattern (letters, | , * and brackets)</label>
    <input id="rx-pat" type="text" value="(a|b)*abb" spellcheck="false" autocomplete="off">
    <label class="eyebrow" for="rx-text" style="display:block;margin-top:10px">Text to match, all of it</label>
    <input id="rx-text" type="text" value="babaabb" spellcheck="false" autocomplete="off">
    <div class="rx-ex" id="rx-ex"></div>
  </div>
  <div style="min-width:0">
    <div class="rx-steps" id="rx-steps"></div>
    <p class="say" id="rx-say" aria-live="polite"></p>
  </div>
</div>
"""

RX_CSS = """
.rx-board input{font:15px var(--mono);width:100%;box-sizing:border-box;padding:8px;margin-top:4px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink)}
.rx-ex{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.rx-ex button{font:13px var(--mono)}
.rx-steps{display:flex;flex-wrap:wrap;gap:4px;margin:6px 0}
.rx-steps .c{display:flex;flex-direction:column;align-items:center;min-width:30px;padding:4px 3px;border:1px solid var(--rule);border-radius:4px;font-family:var(--mono);font-size:13px}
.rx-steps .c b{font-size:15px}
.rx-steps .c small{color:var(--muted);font-size:11px}
.rx-steps .c.acc{border-color:var(--blue)}
.rx-steps .c.dead{border-color:var(--red)}
"""

RX_JS = r"""
(() => {
  const pat = document.getElementById("rx-pat");
  if (!pat) return;
  const txt = document.getElementById("rx-text");
  // Thompson's construction, as in the program: states with a label (or none) and up to two arrows
  function compile(src) {
    let pos = 0, made = [];
    const st = () => { const s = {label: null, out: []}; made.push(s); return s; };
    function alt() { let f = cat(); while (src[pos] === "|") { pos++; const g = cat(), s = st(), e = st(); s.out = [f.s, g.s]; f.e.out = [e]; g.e.out = [e]; f = {s, e}; } return f; }
    function cat() { let f = rep(); while (pos < src.length && src[pos] !== "|" && src[pos] !== ")") { const g = rep(); f.e.label = g.s.label; f.e.out = g.s.out; g.s.dead = true; f = {s: f.s, e: g.e}; } return f; }
    function rep() {
      let f; const c = src[pos];
      if (c === "(") { pos++; f = alt(); if (src[pos++] !== ")") throw "missing )"; }
      else if (/[a-z0-9]/i.test(c || "")) { pos++; const s = st(), e = st(); s.label = c; s.out = [e]; f = {s, e}; }
      else throw c === undefined ? "the pattern ends too soon" : `unexpected "${c}"`;
      while (src[pos] === "*") { pos++; const s = st(), e = st(); s.out = [f.s, e]; f.e.out = [f.s, e]; f = {s, e}; }
      return f;
    }
    const f = alt();
    if (pos !== src.length) throw `unexpected "${src[pos]}"`;
    const live = made.filter(s => !s.dead);
    return {start: f.s, accept: f.e, count: live.length};
  }
  function closure(set) {
    const out = new Set(set), todo = [...set];
    while (todo.length) { const s = todo.pop(); if (s.label === null) for (const t of s.out) if (!out.has(t)) { out.add(t); todo.push(t); } }
    return out;
  }
  function step(set, ch) { const nx = new Set(); for (const s of set) if (s.label === ch) nx.add(s.out[0]); return closure(nx); }
  function show() {
    const box = document.getElementById("rx-steps"), say = document.getElementById("rx-say");
    box.innerHTML = "";
    let m;
    try { m = compile(pat.value.replace(/\s+/g, "")); } catch (e) { say.textContent = "Not a pattern: " + e + "."; return; }
    let cur = closure(new Set([m.start])), work = 0;
    const cell = (ch, set) => {
      const c = el("div", {class: "c" + (set.has(m.accept) ? " acc" : "") + (set.size === 0 ? " dead" : "")}, box);
      el("small", {}, c).textContent = ch;
      el("b", {}, c).textContent = set.size;
    };
    cell("start", cur);
    for (const ch of txt.value) { work += cur.size; cur = step(cur, ch); cell(ch, cur); }
    const ok = cur.has(m.accept);
    say.textContent = `The machine has ${m.count} states. Each box shows how many it could be in after that letter (blue: one of them is the accepting state). ` +
      (ok ? `The whole text matches.` : `The whole text does not match.`) + ` Work: ${work} state visits for ${txt.value.length} letters.`;
  }
  const ex = document.getElementById("rx-ex");
  [["(a|b)*abb", "babaabb"], ["(0|1(01*0)*1)*", "1001"], ["(a|b)*a(a|b)(a|b)", "abaab"], ["(a|aa)*b", "aaaaaaaaaaaaaaaaaaaa"]].forEach(([p, t]) => {
    const b = el("button", {type: "button"}, ex); b.textContent = p;
    b.addEventListener("click", () => { pat.value = p; txt.value = t; show(); });
  });
  pat.addEventListener("input", show); txt.addEventListener("input", show);
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How regular expressions combined older ideas, and where they led")
    W = 210
    nodes = {
        "mp": (20, 20, "Nerve nets", "McCulloch and Pitts's yes-or-no neurons", "1943", "ink"),
        "tm": (395, 20, "Machines with a table", "finitely many states, read one symbol", "Era 4 topic 7", "ink"),
        "alg": (770, 20, "Algebra", "operations that build objects from smaller ones", "Era 3", "ink"),
        "kl": (395, 170, "Kleene's regular events", "⊕ three operations: either, then, repeat", "RAND, 1951", "red"),
        "rs": (20, 330, "Machines that guess", "several states at once; subsets as states", "Rabin and Scott, 1959", "ink"),
        "th": (395, 330, "Thompson's construction", "pattern to machine, piece by piece", "1968", "ink"),
        "per": (770, 330, "The perceptron", "the same neurons, learning their weights", "topic 9", "ink"),
        "today": (395, 480, "Search tools", "ed, grep, every editor's find", "1970s to today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("mp", "kl", ports=("bottom", "top:0.15"))
    D.edge("tm", "kl", ports=("bottom", "top"), dashed=True)
    D.edge("alg", "kl", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("kl", "rs", ports=("bottom:0.1", "top:0.7"))
    D.edge("kl", "th", ports=("bottom", "top"))
    D.edge("mp", "per", ports=("right:0.8", "top:0.2"), dashed=True)
    D.edge("rs", "today", ports=("bottom:0.6", "left:0.5"))
    D.edge("th", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: a likeness of ideas, not a documented influence. The 1943 date of McCulloch and Pitts is from the perceptron article (topic 9).", "caption")
    return D


def chain(d):
    th, sub, blow, bt = d["th"], d["sub"], d["blow"], d["bt"]
    big = blow[-1]
    steps = [
        ("What can a network of yes-or-no neurons recognise? No exact answer",
         "Kleene's regular events: three operations describe exactly what a finite machine recognises", "RAND memorandum, 1951"),
        ("The machine a pattern describes may have to be in several states at once",
         f"Rabin and Scott: treat each set of states as one state; for {sub['rx']}, {sub['th']} states become {sub['n']} sets", "1959"),
        (f"Some patterns need 2^n sets: {int(big[3]):,} for n = {big[0]}",
         f"Thompson: build the machine piece by piece ({th['states']} states for {th['rx']}) and carry the set while reading: {bt[-1][2]} state visits for {bt[-1][0]} letters", "1968"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from neurons to text search")
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
    th, three, rnd, sub, blow, bt = d["th"], d["three"], d["rand"], d["sub"], d["blow"], d["bt"]
    sub_rows = [[f"D{i}", "{" + s + "}", f"D{a}", f"D{b}", "yes" if acc else ""] for i, s, a, b, acc in sub["rows"]]
    walk, cur = ["D0"], 0
    for ch in "babaabb":                                                # read the example text through the program's table
        cur = int(sub["rows"][cur][2 if ch == "a" else 3])
        walk.append(f"D{cur}")
    walk_ok = bool(sub["rows"][cur][4])
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. McCulloch and Pitts had drawn networks of neurons that fire or do not. Kleene asked what patterns such a network can recognise, and answered with a small algebra: three ways of building patterns from smaller ones. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Kleene's regular events. Blue: text search today."),
        ]),
        dict(id="match", eyebrow="Try it", title="Type a pattern and watch the machine read", toc="Try it", blocks=[
            dict(type="p", text="Type a pattern using letters, | (either), * (repeat) and brackets, and a text. The page builds Thompson's machine and reads the text one letter at a time, keeping the set of states the machine could be in. Each box shows the size of that set; blue means the accepting state is in it. The last example is the pattern that makes backtracking matchers struggle: the state sets stay small."),
            dict(type="widget", html=RX_HTML, js=RX_JS, css=RX_CSS,
                 fallback=dict(type="table", head=["Set of states", "States in it", "After a", "After b", "Accepts?"], num=[], rows=sub_rows, hl=len(sub_rows) - 1),
                 note=f"In the interactive edition you can type any pattern and text. Here, the machine for {sub['rx']} as the program built it: reading babaabb goes {', '.join(walk)}, and {walk[-1]} {'accepts' if walk_ok else 'does not accept'}."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Three operations, and a machine for each", toc="How it works", blocks=[
            dict(type="p", text="**Kleene's operations.** Start from single letters. If E and F are patterns, so are E|F (either), EF (E then F) and E* (zero or more copies of E, one after another). Kleene's own repeat took two patterns, E*F, \"zero or more consecutive occurrences of E preceded by one of F\"; today's one-argument star is a simplification. He called the patterns \"regular events\" and added in a footnote: \"We would welcome any suggestions as to a more descriptive term.\""),
            dict(type="svg", name="pieces", draw=nfa_svg(d), alt="Thompson's construction: the pieces for a symbol, for either, and for repeat",
                 caption="Thompson's construction builds the machine from these pieces, one for each part of the pattern."),
            dict(type="p", text=f"**A pattern that does arithmetic.** {three['rx']} matches exactly the binary numerals divisible by 3. The program checked it on all {three['n']} strings of 1 to {three['digits']} digits ({three['acc']} accepted). It starts {', '.join(three['first'])}. Its Thompson machine has {three['th']} states; the subset machine has {three['sub']}, and the smallest machine that does the job has {three['min']}: one for each remainder, 0, 1 and 2."),
            dict(type="p", text=f"**Machines that guess, and machines that do not.** Thompson's machine can be in several states at once. Rabin and Scott (1959) turned each *set* of states into one state of an ordinary machine. For {sub['rx']} the {sub['th']} states become {sub['n']} sets:"),
            dict(type="table", head=["Set", "States in it", "After a", "After b", "Accepts?"], num=[], rows=sub_rows, hl=len(sub_rows) - 1),
            dict(type="p", text=f"Merging sets that behave alike leaves {sub['min']} states, the smallest machine for this pattern."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A pattern is a recipe for a machine. Build the machine from the pattern piece by piece, then read the text once, keeping track of every state the machine could be in. The work is the length of the text times the size of the machine, never more."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Three matchers that agree, and two that cost very different amounts", toc="Measured", blocks=[
            dict(type="p", text=f"**Agreement.** {rnd['e']} random patterns, each tried on {rnd['s']} random strings: the state-set method, the subset machine and Java's own regular-expression library agreed on all {rnd['cases']} cases ({rnd['yes']} matches). Thompson's state count 2s − c held for {th['n']} random patterns."),
            dict(type="table", head=["n", "Thompson states", "Subset states", "Smallest machine (2^n)"], num=[0, 1, 2, 3],
                 rows=[[n, a, f"{int(b):,}", f"{int(c):,}"] for n, a, b, c in blow]),
            dict(type="p", text="**The price of not guessing.** For \"the n-th letter from the end is a\", (a|b)*a(a|b)…(a|b), Thompson's machine grows by 5 states for each extra letter, but any machine that reads without guessing must remember the last n letters: exactly 2ⁿ states. So the subset construction is fast to run but can be enormous to build."),
            dict(type="table", head=["Length of text (all a)", "Backtracking matcher (steps)", "State-set method (state visits)"], num=[0, 1, 2],
                 rows=[[n, b, s] for n, b, s in bt], hl=len(bt) - 1),
            dict(type="p", text="**Backtracking.** Many matchers try one way to read the pattern, back up when it fails, and try another. For (a|aa)*b on a string of a's with no b, they try every way of splitting the a's into a and aa before giving up, and those ways grow like the Fibonacci numbers. Keeping the set of states instead visits a handful of states per letter."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A RAND memorandum about neurons", toc="The evidence", blocks=[
            dict(type="p", text="RAND lists RM-704, *Representation of Events in Nerve Nets and Finite Automata*, by S. C. Kleene, dated 15 December 1951, 102 pages. In section 7.1: \"Our class of regular events will be defined inductively, starting with the definite events, and using three operations\". Wikipedia: \"Regular expressions originated in 1951, when mathematician Stephen Cole Kleene described regular languages using his mathematical notation called regular events\"; Kleene \"introduced it as an alternative to McCulloch & Pitts's 'prehensible'\"."),
            dict(type="p", text="Rabin and Scott, \"Finite Automata and Their Decision Problems\" (*IBM Journal*, April 1959): \"Finite automata are considered in this paper as instruments for classifying finite tapes\"; their section 5 introduces \"the notion of a nondeterministic automaton\". Thompson's \"Regular expression search algorithm\" appeared in *Communications of the ACM* in June 1968; he built Kleene's notation into the QED editor, compiling patterns to IBM 7094 code, then into Unix's ed, whose command g/re/p gave grep its name."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="From neurons to the search box", toc="Full circle", blocks=[
            dict(type="p", text="A question about how brains recognise patterns produced the notation programmers now type every day to find text. Kernighan recalls that Thompson wrote grep overnight for a colleague who wanted to search the Federalist Papers, about a megabyte of text, too much to edit in ed. The same machines check the format of an e-mail address, and split a program into words before a compiler reads it (topic 8)."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Kleene's three operations on one line, {three['rx']}, contain a machine that divides by three: {three['min']} states, one for each possible remainder."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write a pattern for the strings of a's and b's that end in abb.", "(a|b)*abb"),
            ("Does (a|b)*abb match abbabb? And abba?", "abbabb ends in abb: yes. abba ends in bba: no."),
            ("How many states does Thompson's machine have for ab*?", "Symbols a, b and * give s = 3; one join gives c = 1; 2 × 3 − 1 = 5 states."),
            ("Why does a machine for 'the 3rd letter from the end is a' need 8 states?", "It must remember the last three letters (2³ = 8 possibilities), because any of them may turn out to be the 3rd from the end."),
            ("A pattern has 20 states and the text a million letters. At most how much work does the state-set method do?", "At most 20 states per letter: 20 million state visits, however the pattern is written."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Representation of Events in Nerve Nets and Finite Automata (1951)", text="Kleene's RAND research memorandum RM-704, 102 pages, with the three operations in section 7.",
                 draw=C.draw_manuscript, link="https://www.rand.org/pubs/research_memoranda/RM704.html", link_text="RAND", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "RegularExpressions", d["checks"],
                           f"Thompson's state count on {th['n']} random patterns, the multiples-of-three pattern on {three['n']} strings, {rnd['cases']} matches against Java's library, the subset and smallest machines, and the 2^n blow-up.",
                           ["static Frag build(Node n)", "boolean matches(String text)"]),
    ]
    return dict(
        title="Regular Expressions", date="1951",
        description="Era 5, topic 2 of The Algorithm Evolution Atlas: Kleene's regular events, Thompson's construction, the subset construction of Rabin and Scott, and why some matchers explode.",
        lede="Kleene asked what a network of simple neurons can recognise, and answered with three operations: either, then, repeat. Every pattern built from them is a machine with finitely many states, and every such machine is a pattern.",
        fieldnote=f"A line of eleven characters, {three['rx']}, picks out exactly the binary numbers divisible by three. I checked it on all {three['n']} strings up to {three['digits']} digits. The machine inside it has {three['min']} states, one for each remainder. The species now types such lines to search everything it writes.",
        card=[("When", "Kleene 1951; Rabin and Scott 1959; Thompson 1968"),
              ("Where", "RAND, Santa Monica; IBM; Bell Labs"),
              ("What hurt", "No exact description of what a finite machine recognises"),
              ("The fix", "Either, then, repeat; a pattern becomes a machine"),
              ("Cost", "Letters × states, reading the set of states as you go")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `RegularExpressions.java`.",
    )
