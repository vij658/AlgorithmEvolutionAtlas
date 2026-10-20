"""Era 7, topic 6: zero-knowledge proofs. Every number is parsed from ZeroKnowledge.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"iso: two graphs of (\d+) vertices and (\d+) edges ; .*? passed all (\d+) rounds in ([\d,]+) of ([\d,]+) runs ; .*? caught in ([\d,]+) of ([\d,]+) single rounds \(([\d.]+)\) ; (.*)$", ln):
            rows = []
            for part in m.group(9).split(" ; "):
                mm = re.match(r"(\d+) rounds?: ([\d,]+) of ([\d,]+) cheaters passed \(2\^-k predicts ([\d,]+)\)", part)
                rows.append(dict(k=mm.group(1), passed=mm.group(2), of=mm.group(3), pred=mm.group(4)))
            d["iso"] = dict(n=m.group(1), e=m.group(2), rounds=m.group(3), ok=m.group(4), runs=m.group(5), caught=m.group(6), single=m.group(7), rate=m.group(8), rows=rows)
        elif m := re.match(r"simulate: graphs of (\d+) vertices ; ([\d,]+) real conversations .*? same (\d+) different transcripts, .*? distance of ([\d.]+), sampling noise ; the simulator needed ([\d.]+) attempts", ln):
            d["sim"] = dict(n=m.group(1), samples=m.group(2), kinds=m.group(3), tv=m.group(4), att=m.group(5))
        elif m := re.match(r"colour: a graph of (\d+) vertices and (\d+) edges .*? the honest prover passed all ([\d,]+) rounds, .*? possibilities: (.*?) ; add one edge .*?\((\d+) edges\) .*? caught in ([\d.]+) of rounds, about 1/(\d+) ; (.*)$", ln):
            pairs = [(p.split(":")[0], p.split(":")[1]) for p in m.group(4).split()]
            rows = []
            for part in m.group(8).split(" ; "):
                mm = re.match(r"([\d,]+) rounds: ([\d,]+) of ([\d,]+) cheaters passed \(predicted ([\d,]+)\)", part)
                rows.append(dict(k=mm.group(1), passed=mm.group(2), of=mm.group(3), pred=mm.group(4)))
            d["col"] = dict(v=m.group(1), e=m.group(2), honest=m.group(3), pairs=pairs, e2=m.group(5), rate=m.group(6), inv=m.group(7), rows=rows)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def protocol_svg(d):
    """One round of the graph-isomorphism protocol as a conversation."""
    iso = d["iso"]

    def draw(t, standalone):
        o = []
        W, H = 780, 340
        o.append(C.text(20, 26, "One round of the graph-isomorphism proof: the prover knows a renaming π with G₁ = π(G₀)", t["ink"], 13, "start", 700))
        xp, xv = 170, 610
        for x, name, sub in ((xp, "Prover", "knows π"), (xv, "Verifier", "knows only G₀ and G₁")):
            o.append(C.rect(x - 80, 44, 160, 44, t["surface"], t["ink"], 1.8, 3))
            o.append(C.text(x, 63, name, t["ink"], 14, "middle", 700))
            o.append(C.text(x, 80, sub, t["muted"], 11.5, "middle"))
            o.append(C.line(x, 88, x, 290, t["axis"], 1.4, ";stroke-dasharray:5 4"))

        def msg(y, a, b, label, sub, col):
            o.append(C.line(a, y, b - (10 if b > a else -10), y, col, 2))
            s = 1 if b > a else -1
            o.append(C.path(f"M{b},{y} L{b - s * 11},{y - 5.5} L{b - s * 11},{y + 5.5} Z", None, col))
            o.append(C.text((a + b) / 2, y - 9, label, col, 13, "middle", 700))
            o.append(C.text((a + b) / 2, y + 18, sub, t["muted"], 11.5, "middle"))
        msg(130, xp, xv, "1. H = σ(G₀) for a fresh random σ", "a random renaming of G₀: it looks like a random copy of either graph", t["ink"])
        msg(190, xv, xp, "2. a coin α: 0 or 1", "\"show me how H comes from G_α\"", t["blue"])
        msg(250, xp, xv, "3. ρ = σ if α = 0, else σ ∘ π⁻¹", "the verifier checks that ρ(G_α) = H", t["red"])
        o.append(C.text(20, H - 28, "A cheater with two different graphs can prepare H for only one α.", t["muted"], 12))
        o.append(C.text(20, H - 10, f"In the program it was caught in {iso['rate']} of single rounds, so k rounds leave it 1 chance in 2ᵏ.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "One round of the zero-knowledge proof of graph isomorphism", t, standalone, 0.55, 780)
    return draw


ZK_HTML = """
<div class="board zk-board">
  <div style="min-width:0">
    <div class="zk-view" id="zk-view"></div>
  </div>
  <div style="min-width:0">
    <div class="controls"><label><input type="checkbox" id="zk-cheat"> The prover cheats (one extra edge, same colours)</label></div>
    <div class="zk-btns"><button type="button" class="primary" id="zk-commit">New round: seal the colours</button><button type="button" id="zk-auto">Run 100 rounds</button><button type="button" id="zk-reset">Reset</button></div>
    <div class="zk-stats" id="zk-stats"></div>
    <p class="say" id="zk-say" aria-live="polite"></p>
  </div>
</div>
"""

ZK_CSS = """
.zk-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.zk-view line.e{cursor:pointer}
.zk-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.zk-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
.zk-board .controls label{color:var(--ink)}
.zk-board input[type=checkbox]{width:auto}
"""

ZK_JS = r"""
(() => {
  const view = document.getElementById("zk-view");
  if (!view) return;
__SHA__
  const COLS = ["var(--red)", "var(--blue)", "var(--yellow)"], NAMES = ["red", "blue", "yellow"];
  const colour = [0, 1, 2, 0, 1, 2, 0, 1];
  const base = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,6],[6,7],[7,0],[0,4],[1,5],[2,6],[3,7],[0,2],[4,6]], extra = [0, 3];
  const pos = Array.from({length: 8}, (_, i) => [210 + 150 * Math.sin(i * Math.PI / 4), 190 - 150 * Math.cos(i * Math.PI / 4)]);
  const hex = b => Array.from(b, x => x.toString(16).padStart(2, "0")).join("");
  let round = null, rounds = 0, caught = 0, seen = {}, opened = null;
  const edges = () => document.getElementById("zk-cheat").checked ? base.concat([extra]) : base;
  function seal() {
    const perm = [0, 1, 2]; for (let i = 2; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [perm[i], perm[j]] = [perm[j], perm[i]]; }
    const c = colour.map(x => perm[x]);
    const nonces = c.map(() => crypto.getRandomValues ? crypto.getRandomValues(new Uint8Array(16)) : Uint8Array.from({length: 16}, () => Math.floor(Math.random() * 256)));
    const boxes = c.map((x, i) => { const m = new Uint8Array(17); m.set(nonces[i]); m[16] = x; return sha256(m); });
    round = {c, nonces, boxes}; opened = null;
  }
  function open(e) {
    if (!round) return null;
    const [a, b] = e, r = round;
    const check = i => { const m = new Uint8Array(17); m.set(r.nonces[i]); m[16] = r.c[i]; return hex(sha256(m)) === hex(r.boxes[i]); };
    const ok = check(a) && check(b) && r.c[a] !== r.c[b];
    rounds++; if (!ok) caught++;
    const key = NAMES[r.c[a]] + "–" + NAMES[r.c[b]]; seen[key] = (seen[key] || 0) + 1;
    opened = {e, ok}; const res = {a, b, ca: r.c[a], cb: r.c[b], ok}; round = null;
    return res;
  }
  function draw(msg) {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 420 390"}, view), E = edges();
    E.forEach(e => {
      const [a, b] = e, isOpen = opened && opened.e === e;
      const ln = sv("line", {x1: pos[a][0], y1: pos[a][1], x2: pos[b][0], y2: pos[b][1], stroke: isOpen ? (opened.ok ? "var(--ink)" : "var(--red)") : "var(--axis)", "stroke-width": isOpen ? 4 : 2.2, class: "e"}, svg);
      sv("line", {x1: pos[a][0], y1: pos[a][1], x2: pos[b][0], y2: pos[b][1], stroke: "transparent", "stroke-width": 14, class: "e"}, svg)
        .addEventListener("click", () => { if (!round) { draw("Seal the colours first: press New round."); return; } const r = open(e); draw(r.ok ? `Opened ${r.a + 1} and ${r.b + 1}: ${NAMES[r.ca]} and ${NAMES[r.cb]}, different. The verifier learns only that two neighbours differ, in colours the prover just shuffled.` : `Opened ${r.a + 1} and ${r.b + 1}: both ${NAMES[r.ca]}. Caught!`); });
    });
    pos.forEach((p, i) => {
      const show = opened && (opened.e[0] === i || opened.e[1] === i) && !round;
      sv("rect", {x: p[0] - 26, y: p[1] - 17, width: 52, height: 34, rx: 4, fill: show ? COLS[lastColour(i)] : "var(--surface)", stroke: "var(--ink)", "stroke-width": 1.8}, svg);
      const t = sv("text", {x: p[0], y: p[1] - 2, "text-anchor": "middle", "font-size": 12, "font-weight": 700, fill: show ? "var(--paper)" : "var(--ink)"}, svg); t.textContent = i + 1;
      const h = sv("text", {x: p[0], y: p[1] + 11, "text-anchor": "middle", "font-size": 9.5, fill: show ? "var(--paper)" : "var(--muted)", "font-family": "var(--mono)"}, svg);
      h.textContent = round ? hex(round.boxes[i]).slice(0, 6) : (show ? "open" : "");
    });
    const st = document.getElementById("zk-stats"); st.innerHTML = "";
    const m = E.length, p = Math.pow(1 - 1 / m, rounds);
    el("div", {}, st, `edges: ${m}${document.getElementById("zk-cheat").checked ? " (one of them joins two vertices of the same colour)" : ""}`);
    el("div", {}, st, `rounds: ${rounds}, caught: ${caught}`);
    el("div", {}, st, `a cheater with one bad edge survives this many rounds with chance ${(100 * p).toPrecision(3)}%`);
    const pairs = Object.entries(seen).sort();
    if (pairs.length) el("div", {}, st, "colour pairs seen: " + pairs.map(([k, v]) => `${k} ${v}`).join(", "));
    if (msg) document.getElementById("zk-say").textContent = msg;
  }
  let lastC = null;
  function lastColour(i) { return lastC ? lastC[i] : 0; }
  document.getElementById("zk-commit").addEventListener("click", () => { seal(); lastC = round.c.slice(); draw("Sealed: each box holds SHA-256(random nonce, colour), with the three colours renamed at random. Click an edge to open its two boxes."); });
  document.getElementById("zk-auto").addEventListener("click", () => {
    const E = edges(); let c0 = caught;
    for (let k = 0; k < 100; k++) { seal(); lastC = round.c.slice(); open(E[Math.floor(Math.random() * E.length)]); }
    draw(`100 rounds, each on a random edge: ${caught - c0} caught. ${document.getElementById("zk-cheat").checked ? "The bad edge is found about once in " + E.length + " rounds." : "An honest prover is never caught."}`);
  });
  document.getElementById("zk-reset").addEventListener("click", () => { round = null; rounds = 0; caught = 0; seen = {}; opened = null; draw("Press New round to start."); });
  document.getElementById("zk-cheat").addEventListener("change", () => { round = null; rounds = 0; caught = 0; seen = {}; opened = null; draw(document.getElementById("zk-cheat").checked ? "Now the graph has one more edge, between vertices 1 and 4, which share a colour; the prover keeps its colouring and hopes you never pick that edge." : "An honest prover with a proper colouring."); });
  draw("You are the verifier. Press New round: the prover seals every vertex's colour in a box. Then click any edge to open its two boxes.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How zero-knowledge proofs combined older ideas, and where they led")
    W = 210
    nodes = {
        "np": (20, 20, "Proofs as certificates", "NP: a solution anyone can check", "Era 6, topic 8", "ink"),
        "rnd": (395, 20, "Randomness", "random questions a cheater cannot predict", "", "ink"),
        "ow": (770, 20, "One-way functions", "sealed boxes: commitments", "Era 6, topic 10", "ink"),
        "ip": (20, 180, "Interactive proofs", "⊕ a conversation, convincing with high probability", "Goldwasser and others, 1985", "ink"),
        "zk": (395, 180, "Zero knowledge", "⊕ a simulator could fake the conversation", "1985", "red"),
        "gmw": (770, 340, "All of NP", "⊕ commit to a 3-colouring, open one edge", "Goldreich and others, 1986", "ink"),
        "cave": (20, 340, "The Ali Baba cave", "a story for children", "Quisquater and others, 1990", "ink"),
        "today": (395, 490, "Today", "cryptographic protocols; private payments in cryptocurrencies (2016)", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("np", "ip", ports=("bottom", "top"))
    D.edge("rnd", "ip", ports=("bottom:0.2", "top:0.85"))
    D.edge("ip", "zk", ports=("right", "left"))
    D.edge("zk", "gmw", ports=("bottom:0.85", "top:0.3"))
    D.edge("ow", "gmw", ports=("bottom", "top:0.7"))
    D.edge("zk", "cave", ports=("bottom:0.15", "top:0.7"), dashed=True)
    D.edge("zk", "today", ports=("bottom", "top"))
    D.edge("gmw", "today", ports=("bottom", "top:0.85"))
    D.text(20, 615, "Today: from the ACM's 2013 Turing Award announcement and Wikipedia. Dashed: an explanation, not a new algorithm.", "caption")
    return D


def chain(d):
    iso, sim, col = d["iso"], d["sim"], d["col"]
    ten = next(r for r in iso["rows"] if r["k"] == "10")
    steps = [
        ("To prove you know a secret, you show it, or something about it",
         f"An interactive proof with random challenges: {ten['passed']} of {ten['of']} cheaters survived 10 rounds (2⁻¹⁰ predicts {ten['pred']})", "Goldwasser, Micali, Rackoff, 1985"),
        ("But does the verifier learn something from the conversation?",
         f"A simulator with no secret produces the same transcripts: total variation distance {sim['tv']}, sampling noise", "zero knowledge"),
        ("Graph isomorphism is one special kind of statement",
         f"Sealed colours of a 3-colouring, one edge opened per round: any NP statement; one bad edge caught in {col['rate']} of rounds", "Goldreich, Micali, Wigderson, 1986"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from showing the secret to proving without a trace")
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
    iso, sim, col = d["iso"], d["sim"], d["col"]
    iso_rows = [[r["k"], r["passed"], r["of"], r["pred"]] for r in iso["rows"]]
    col_rows = [[r["k"], r["passed"], r["of"], r["pred"]] for r in col["rows"]]
    pair_rows = [[f"({p})", s] for p, s in col["pairs"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. A proof in the NP sense (Era 6) is a certificate anyone can check, and checking it teaches you the certificate. Goldwasser, Micali and Rackoff replaced the certificate with a conversation, using random questions the prover cannot predict, and asked how much knowledge the conversation gives away. Goldreich, Micali and Wigderson then used sealed boxes, built from one-way functions, to make such proofs for every NP statement. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: zero knowledge. Blue: where it is used."),
        ]),
        dict(id="play", eyebrow="Try it", title="Be the verifier", toc="Try it", blocks=[
            dict(type="p", text="The prover claims this graph can be coloured with three colours so that no edge joins two vertices of the same colour. Each round it renames the three colours at random and seals every vertex's colour in a box: SHA-256 of a random nonce and the colour (the hex shows the start of each seal). You pick one edge; only its two boxes are opened, and you check the seals and that the colours differ. You never see more than two colours of one shuffled colouring. Then let the prover cheat: one extra edge joins two vertices of the same colour, and you catch it only when you happen to pick that edge. The widget uses your browser's random numbers, so its counts are its own; the program's are below."),
            dict(type="widget", html=ZK_HTML, js=ZK_JS.replace("__SHA__", C.SHA256_JS), css=ZK_CSS,
                 fallback=dict(type="table", head=["Opened pair of colours", "Share of 60,000 honest rounds"], num=[1], rows=pair_rows),
                 note="In the interactive edition you can play the verifier against an honest or a cheating prover."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Convincing without telling", toc="How it works", blocks=[
            dict(type="p", text="**Graph isomorphism.** Two graphs G₀ and G₁ are the same graph with the vertices renamed, and the prover knows the renaming π. Revealing π would prove it, and give π away. Instead, each round:"),
            dict(type="svg", name="protocol", draw=protocol_svg(d), alt="One round of the zero-knowledge proof of graph isomorphism", width=780),
            dict(type="p", text="**Three properties.** *Completeness:* an honest prover always passes. *Soundness:* if the graphs differ, H can be a renaming of at most one of them, so each round catches a cheater with probability ½, and k rounds leave 2⁻ᵏ. *Zero knowledge:* whatever the verifier sees, a *simulator* who knows no secret could have produced with the same probabilities: pick α first, rename G_α at random to get H, and if the verifier's coin differs from the guess, start again. Since the conversation could be faked without π, it cannot reveal π."),
            dict(type="p", text="**All of NP.** Goldreich, Micali and Wigderson used 3-colouring, to which every NP statement can be reduced. The prover shuffles the three colours, seals each vertex's colour in a commitment, and the verifier opens one edge. A proper colouring always passes; a colouring with a bad edge among E is caught with probability at least 1/E per round, so about E rounds per factor of e."),
            dict(type="callout", kind="key", label="Key idea",
                 text="If a conversation could have been produced by someone who does not know the secret, then the conversation cannot reveal the secret. Randomness makes a cheater's success unlikely; the simulator shows the honest prover's answers teach nothing."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Cheaters, simulators and sealed boxes", toc="Measured", blocks=[
            dict(type="p", text=f"**Graph isomorphism,** two graphs of {iso['n']} vertices and {iso['e']} edges. The honest prover passed all {iso['rounds']} rounds in {iso['ok']} of {iso['runs']} runs. A cheater whose graphs are not isomorphic (checked over all 8! renamings) was caught in {iso['caught']} of {iso['single']} single rounds ({iso['rate']}). Cheaters surviving k rounds in a row:"),
            dict(type="table", head=["Rounds k", "Cheaters who passed", "Out of", "2⁻ᵏ predicts"], num=[0, 1, 2, 3], rows=iso_rows),
            dict(type="p", text=f"**The simulator,** graphs of {sim['n']} vertices: {sim['samples']} real conversations and {sim['samples']} simulated ones contain the same {sim['kinds']} different transcripts (2 coins × 5! renamings), with frequencies differing by a total variation distance of {sim['tv']}, which is sampling noise. The simulator needed {sim['att']} attempts per transcript."),
            dict(type="p", text=f"**3-colouring with SHA-256 seals,** {col['v']} vertices and {col['e']} edges: the honest prover passed all {col['honest']} rounds, and the opened pairs of colours were spread evenly over the 6 possibilities:"),
            dict(type="table", head=["Opened pair of colours", "Share of rounds"], num=[1], rows=pair_rows),
            dict(type="p", text=f"With one extra edge between two vertices of the same colour ({col['e2']} edges), the prover was caught in {col['rate']} of rounds, about 1 in {col['inv']}:"),
            dict(type="table", head=["Rounds", "Cheaters who passed", "Out of", "Predicted"], num=[0, 1, 2, 3], rows=col_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Knowledge as something to measure", toc="The evidence", blocks=[
            dict(type="p", text="Shafi Goldwasser and Silvio Micali (MIT) and Charles Rackoff (Toronto), \"The Knowledge Complexity of Interactive Proof-Systems\" (© 1985 ACM): \"we introduce a new theorem-proving procedure, that is a new efficient method of communicating a proof\"; \"Our 'proofs' are probabilistic in nature\"; \"Our proofs are interactive.\" Knowledge is defined through a probabilistic polynomial-time machine whose output cannot be told apart from the real conversation, and the first example, quadratic non-residuosity, has knowledge complexity 0. Wikipedia records that this paper and Babai and Moran's work invented interactive proof systems, and that all five authors shared the first Gödel Prize in 1993."),
            dict(type="p", text="Oded Goldreich, Silvio Micali and Avi Wigderson, \"Proofs that Yield Nothing But Their Validity or All Languages in NP Have Zero-Knowledge Proof Systems\" (IEEE FOCS 1986; *Journal of the ACM*, July 1991): proofs that \"efficiently demonstrate membership in the language without conveying any additional knowledge\"; the graph isomorphism protocol, in which the prover \"generates a graph H, which is a random isomorphic copy\", repeated \"m times, each time using independent random coin tosses\"; and 3-colouring for all of NP, assuming \"secure encryption functions\", where each round shows the verifier only \"a pair of different randomly selected elements\" of the three colours."),
            dict(type="p", text="The ACM's announcement of the 2012 Turing Award to Goldwasser and Micali (13 March 2013) says the 1985 paper \"initiated the idea of 'zero-knowledge' proofs\", now \"the essential language for speaking about security of cryptographic protocols\". In 1990 Quisquater, Guillou and Berson's \"How to Explain Zero-Knowledge Protocols to Your Children\" told it as a story of Ali Baba and a magic door, to show \"that it is possible to convince without revealing\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="NP, from both sides", toc="Full circle", blocks=[
            dict(type="p", text="Era 6 used NP-completeness to say that some problems are probably hard, and public keys to turn hardness into secrecy. Zero knowledge uses both: an NP statement as the thing to prove, and a one-way function to seal the boxes. The same reductions that showed 3-colouring is as hard as anything in NP now carry a zero-knowledge proof from 3-colouring to everything in NP."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"In the program the honest prover answered {col['honest']} challenges and the verifier saw only shuffled pairs of different colours, each about 1/6 of the time. It ends convinced that a colouring exists, and knows nothing about what it is."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many rounds of the isomorphism protocol leave a cheater less than one chance in a million?", "20, since 2²⁰ is just over a million."),
            ("Why must the prover use a fresh random renaming σ every round?", "Reusing σ would let the verifier ask α = 0 one round and α = 1 the next and combine the answers into π."),
            ("Why does the prover shuffle the three colours every round in the 3-colouring proof?", "Otherwise the opened colours, collected over many rounds, would reveal the colouring itself."),
            ("A graph has 100 edges and the cheater has one bad edge. About how many rounds give a 1-in-e chance of escape? A 1-in-a-million chance?", "About 100 rounds for 1/e; about 100 × ln(10⁶) ≈ 1,380 rounds for one in a million."),
            ("Why does the simulator need about 2 attempts per transcript?", "It guesses the verifier's coin before choosing H, and is right half the time."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Knowledge Complexity of Interactive Proof-Systems (1985)", text="Goldwasser, Micali and Rackoff, extended abstract, © 1985 ACM.",
                 draw=C.draw_manuscript, link="https://resources.mpi-inf.mpg.de/departments/d1/teaching/ss13/gitcs/GMR85.pdf", link_text="The paper (PDF, on a Max Planck Institute page)", licence="Drawn placeholder."),
            dict(title="Proofs that Yield Nothing But Their Validity (1986, 1991)", text="Goldreich, Micali and Wigderson, *Journal of the ACM*, July 1991.",
                 draw=C.draw_manuscript, link="https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Zero%20Knowledge/Proofs_That_Yield_Nothing_But_Their_Validity_or_All_Languages_in_NP_Have_Zero-Knowledge_Proof_Systems.pdf", link_text="The paper (PDF, on Silvio Micali's MIT page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ZeroKnowledge", d["checks"],
                           "the honest prover on 20,000 rounds, a cheater's survival over 1, 2, 5 and 10 rounds against 2⁻ᵏ, real and simulated transcripts compared over all 240 possibilities, and the 3-colouring protocol with SHA-256 commitments, honest and cheating.",
                           ["static boolean honestRound(boolean[][] g0, boolean[][] g1, int[] pi)", "static boolean colourRound(int[] colouring)"]),
    ]
    return dict(
        title="Zero-Knowledge Proofs", date="1985–1986",
        description="Era 7, topic 6 of The Algorithm Evolution Atlas: Goldwasser, Micali and Rackoff's interactive proofs, the simulator that makes them zero-knowledge, and Goldreich, Micali and Wigderson's proofs for all of NP.",
        lede="For two thousand years, a proof showed why something was true. In 1985 three cryptographers proposed proofs that convince you something is true and show you nothing else at all.",
        fieldnote=f"I played the verifier: {col['honest']} rounds, and every time I opened two boxes I saw two different colours, each pair as often as any other. I was convinced, and I learned nothing. A cheater with one bad edge among {col['e2']} lasted about {col['inv']} rounds.",
        card=[("When", "1985; for all of NP, 1986"),
              ("Where", "MIT and Toronto; Technion, MIT, Hebrew University"),
              ("What hurt", "Proving you know a secret meant revealing it"),
              ("The fix", "Random challenges, and a simulator that could fake the conversation"),
              ("Checked", f"Cheaters caught in {iso['rate']} of rounds; transcripts indistinguishable")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ZeroKnowledge.java`.",
    )
