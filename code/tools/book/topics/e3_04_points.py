"""Era 3, topic 4: the problem of points. Every number is parsed from ProblemOfPoints.java's output."""
import re

import common as C
from diagrams import Diagram

sci = C.sci


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"pascal: .*? at 2 rounds to 1 the leader's share is (\S+) of 64 = (\d+) pistoles \(the other (\d+)\) ; at 2 to 0, (\d+) \(the other (\d+)\) ; at 1 to 0, (\d+) \(the other (\d+)\)$", ln):
            g = m.groups()
            d["p"] = dict(frac=g[0], s21=g[1], o21=g[2], s20=g[3], o20=g[4], s10=g[5], o10=g[6])
        elif m := re.match(r"agree: .* in all (\d+) positions with up to (\d+) rounds", ln):
            d["agree"] = dict(n=m.group(1), N=m.group(2))
        elif m := re.match(r"three: .*? within (\d+) rounds, (\d+) equally likely sequences ; the first wins (\d+), the second (\d+), the third (\d+)", ln):
            d["three"] = dict(rounds=m.group(1), total=m.group(2), a=m.group(3), b=m.group(4), c=m.group(5))
        elif m := re.match(r"pacioli: a game to (\d+) rounds, the leader's share of the stakes ; (.+)$", ln):
            d["pac"] = dict(target=m.group(1), rows=re.findall(r"(\d+) to (\d+): proportional ([\d.]+)%, fair ([\d.]+)%", m.group(2)))
        elif m := re.match(r"triangle: rows 0 to 6: (.+?) ; when A needs 2", ln):
            d["tri"] = [r.split() for r in m.group(1).split(" / ")]
        elif m := re.match(r"work: (.+?) ; a simulation of ([\d,]+) finished games .*? estimates (\S+), the table's exact (\S+) = (\S+) \(error (\S+)\)$", ln):
            d["work"] = [dict(k=g[0], cells=g[1], outcomes=g[2]) for g in re.findall(r"(\d+) rounds each: table ([\d,]+) cells, enumeration ([\d,]+) outcomes", m.group(1))]
            d["mc"] = dict(n=m.group(2), est=m.group(3), frac=m.group(4), exact=m.group(5), err=m.group(6))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def table_svg(d):
    """Pascal's table for a game to 3: each share is the average of the two to its right and below."""
    import fractions

    def draw(t, standalone):
        out = []
        cw, ch, x0, y0 = 150, 64, 190, 70
        share = {}
        for a in range(0, 4):
            for b in range(0, 4):
                if a == 0 and b == 0:
                    continue
                share[(a, b)] = fractions.Fraction(1) if a == 0 else fractions.Fraction(0) if b == 0 else None
        for a in range(1, 4):
            for b in range(1, 4):
                share[(a, b)] = (share[(a - 1, b)] + share[(a, b - 1)]) / 2
        out.append(C.text(x0 + 2 * cw, 30, "rounds B still needs", t["muted"], 13, "middle"))
        for b in range(0, 4):
            out.append(C.text(x0 + b * cw + cw / 2, 56, str(b), t["ink"], 14, "middle", 700))
        out.append(C.text(20, y0 + 2 * ch, "rounds A", t["muted"], 13))
        out.append(C.text(20, y0 + 2 * ch + 16, "still needs", t["muted"], 13))
        for a in range(0, 4):
            out.append(C.text(x0 - 16, y0 + a * ch + ch / 2 + 5, str(a), t["ink"], 14, "end", 700))
            for b in range(0, 4):
                x, y = x0 + b * cw, y0 + a * ch
                if a == 0 and b == 0:
                    out.append(C.rect(x, y, cw - 6, ch - 6, t["paper"], t["axis"], 1))
                    continue
                s = share[(a, b)]
                pist = s * 64
                hot = (a, b) in [(1, 2), (1, 3)]
                out.append(C.rect(x, y, cw - 6, ch - 6, t["surface"], t["red"] if hot else t["axis"], 2 if hot else 1))
                out.append(C.text(x + (cw - 6) / 2, y + 24, f"{pist} of 64" if pist.denominator == 1 else f"{float(pist):.1f} of 64", t["red"] if hot else t["ink"], 14, "middle", 700))
                out.append(C.text(x + (cw - 6) / 2, y + 44, "A wins" if a == 0 else "B wins" if b == 0 else f"share {s}", t["muted"], 12, "middle"))
        out.append(C.text(20, y0 + 4 * ch + 24, "Each inner cell is the average of the cell to its left (A wins the next round) and the cell above (B wins it).", t["muted"], 12.5))
        out.append(C.text(20, y0 + 4 * ch + 42, f"Red: Pascal's two cases from 29 July 1654, {d['p']['s21']} and {d['p']['s20']} pistoles to the leader. Numbers checked by ProblemOfPoints.java.", t["muted"], 12.5))
        return C.svg_doc(800, y0 + 4 * ch + 56, "".join(out), "Pascal's table of fair shares for a game to three rounds", t, standalone, 0.55, 800)
    return draw


PP_HTML = """
<div class="board pp-board">
  <div style="min-width:0">
    <div class="controls">
      <label for="pp-n">Game to <input id="pp-n" type="range" min="2" max="8" value="3"></label><span class="pp-v" id="pp-nv"></span>
      <label for="pp-s">Stakes <input id="pp-s" type="number" min="2" max="10000" value="64"></label>
    </div>
    <div class="scrollx"><table class="pp-grid" id="pp-grid"></table></div>
    <p class="pp-note">Rows: rounds A still needs. Columns: rounds B still needs. Click a cell.</p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The fair split</div>
    <ol class="pp-steps" id="pp-steps"></ol>
    <p class="say" id="pp-say" aria-live="polite"></p>
  </div>
</div>
"""

PP_CSS = """
.pp-board .controls{flex-wrap:wrap}
.pp-board input[type=range]{width:min(160px,40vw)}
.pp-board input[type=number]{width:6em}
.pp-v{font-family:var(--mono);font-size:13px}
.pp-grid{border-collapse:collapse;margin:8px 0;font-family:var(--mono);font-size:12px}
.pp-grid th{color:var(--muted);font-weight:400;padding:3px 5px}
.pp-grid td{border:1px solid var(--axis);padding:5px 6px;text-align:center;cursor:pointer;min-width:3.6em;background:var(--surface)}
.pp-grid td.end{color:var(--muted);background:var(--wash);cursor:default}
.pp-grid td.sel{outline:3px solid var(--red);outline-offset:-3px}
.pp-grid td.nb{background:color-mix(in srgb,var(--blue) 16%,var(--surface))}
.pp-note{font-size:12.5px;color:var(--muted)}
.pp-steps{margin:6px 0 10px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.pp-steps .m{font-family:var(--mono);font-size:12.5px}
.pp-board .say{font-size:14.5px}
"""

PP_JS = r"""
(() => {
  const grid = document.getElementById("pp-grid");
  if (!grid) return;
  let sel = [1, 2];
  const fmtS = v => (Math.abs(v - Math.round(v)) < 1e-9 ? Math.round(v).toLocaleString("en-US") : v.toFixed(2));
  const C = (n, k) => { let r = 1; for (let i = 0; i < k; i++) r = r * (n - i) / (i + 1); return Math.round(r); };
  function show() {
    const N = +document.getElementById("pp-n").value, S = Math.max(2, +document.getElementById("pp-s").value || 64);
    document.getElementById("pp-nv").textContent = N;
    const t = [];
    for (let a = 0; a <= N; a++) { t.push([]); for (let b = 0; b <= N; b++) t[a].push(a === 0 ? 1 : b === 0 ? 0 : (t[a - 1][b] + t[a][b - 1]) / 2); }
    if (sel[0] > N || sel[1] > N) sel = [1, Math.min(2, N)];
    grid.innerHTML = "";
    const hr = el("tr", {}, grid); el("th", {}, hr, "");
    for (let b = 0; b <= N; b++) el("th", {}, hr, String(b));
    for (let a = 0; a <= N; a++) {
      const tr = el("tr", {}, grid); el("th", {}, tr, String(a));
      for (let b = 0; b <= N; b++) {
        const td = el("td", {}, tr, a === 0 && b === 0 ? "" : fmtS(t[a][b] * S));
        if (a === 0 || b === 0) td.className = "end";
        else {
          if (a === sel[0] && b === sel[1]) td.className = "sel";
          else if ((a === sel[0] - 1 && b === sel[1]) || (a === sel[0] && b === sel[1] - 1)) td.className = "nb";
          td.addEventListener("click", () => { sel = [a, b]; show(); });
        }
      }
    }
    const [a, b] = sel, n = a + b - 1;
    let wins = 0; for (let k = a; k <= n; k++) wins += C(n, k);
    const ol = document.getElementById("pp-steps"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    const scoreA = N - a, scoreB = N - b;
    li(`score ${scoreA} to ${scoreB} in a game to ${N}: A needs ${a}, B needs ${b}`);
    li(`Pascal: average of the next two cells, (${fmtS(t[a - 1][b] * S)} + ${fmtS(t[a][b - 1] * S)}) ÷ 2 = <span class="m">${fmtS(t[a][b] * S)}</span> for A`);
    li(`Fermat: play out ${n} more round${n === 1 ? "" : "s"}: A wins in ${wins.toLocaleString("en-US")} of ${(2 ** n).toLocaleString("en-US")} ways, so A gets ${wins}/${2 ** n} of ${S} = <span class="m">${fmtS(wins / 2 ** n * S)}</span>`);
    const prop = scoreA + scoreB === 0 ? 0.5 : scoreA / (scoreA + scoreB);
    li(`proportional to rounds won (Pacioli): <span class="m">${fmtS(prop * S)}</span> for A`);
    document.getElementById("pp-say").textContent = Math.abs(prop - t[a][b]) < 1e-9 ? "Here the proportional rule happens to agree with the fair share."
      : `The proportional rule ${prop > t[a][b] ? "overpays" : "underpays"} the leader by ${fmtS(Math.abs(prop - t[a][b]) * S)}: it looks at the past, not at what can still happen.`;
  }
  ["pp-n", "pp-s"].forEach(id => document.getElementById(id).addEventListener("input", show));
  show();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the problem of points combined older ideas, and where it led")
    W, H = 210, 86
    nodes = {
        "tal": (20, 20, "Counting cases", "tallies and enumeration", "Era 1 topic 1", "ink"),
        "pac": (395, 20, "The merchants' rule", "split in proportion to rounds won", "Pacioli, 1494", "ink"),
        "tri": (770, 20, "The arithmetic triangle", "known long before Pascal", "many cultures", "ink"),
        "pf": (395, 170, "Pascal and Fermat", "⊕ value a game by what can still happen", "letters of 1654", "red"),
        "huy": (20, 330, "Huygens", "the first treatise on probability", "1657", "ink"),
        "lsq": (395, 330, "Probability of errors", "least squares", "topic 8", "ink"),
        "dp": (770, 330, "Dynamic programming", "a table of smaller answers", "Bellman, Era 5", "blue"),
        "rl": (770, 480, "Game-playing programs", "values computed back from the end", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("tal", "pf", ports=("bottom", "top:0.15"))
    D.edge("pac", "pf", ports=("bottom", "top"), dashed=True)
    D.edge("tri", "pf", ports=("bottom", "top:0.85"))
    D.edge("pf", "huy", ports=("bottom:0.1", "top:0.7"))
    D.edge("pf", "lsq", ports=("bottom", "top"))
    D.edge("pf", "dp", ports=("bottom:0.9", "top:0.3"), dashed=True)
    D.edge("dp", "rl", ports=("bottom", "top"))
    D.text(20, 615, "Dashed from Pacioli: the rule Pascal and Fermat replaced. Dashed to dynamic programming: the same method, named three centuries later (a reading, not a documented line).", "caption")
    return D


def chain(d):
    pac, w = d["pac"], d["work"]
    one = next(r for r in pac["rows"] if r[0] == "1" and r[1] == "0")
    w20 = next(x for x in w if x["k"] == "20")
    steps = [
        ("A game stopped early: who gets the stakes?",
         "Split in proportion to rounds won", "Pacioli, 1494"),
        (f"At 1 round to 0 that gives the leader {one[2]}% of the stakes, though the game is far from won",
         "Count every way the game could still end", "Fermat, 1654"),
        (f"The cases double with every round: {w20['outcomes']} for a game to 20",
         f"Work backward one round at a time: {w20['cells']} averages", "Pascal, 1654"),
        ("More players, more rounds, unequal chances",
         "The same backward rule, in a bigger table", "Huygens 1657; today"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from a merchants' rule to a table of fair shares")
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
    p, ag, th, pac, tri, w, mc = d["p"], d["agree"], d["three"], d["pac"], d["tri"], d["work"], d["mc"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Counting cases is as old as tally marks (Era 1, topic 1); merchants' arithmetic books had offered rules for interrupted games since Pacioli (1494); the arithmetic triangle was known in several cultures. In the summer of 1654 two Frenchmen turned the question around: a share should depend on what can still happen, not on what has happened. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the Pascal–Fermat letters. Blue: where backward reasoning over a table went."),
        ]),
        dict(id="table", eyebrow="Try it", title="Fill in Pascal's table", toc="Try it", blocks=[
            dict(type="p", text="Each cell is the fair amount for A when A still needs the row's number of rounds and B the column's. The edges are finished games: A has everything or nothing. Every inner cell is the average of its two neighbours one round later (shaded blue). Click a cell to see Pascal's average, Fermat's count and the old proportional rule side by side."),
            dict(type="widget", html=PP_HTML, js=PP_JS, css=PP_CSS,
                 fallback=dict(type="svg", name="pascal-table", draw=table_svg(d), alt="Pascal's table of fair shares for a game to three rounds", width=800),
                 note="In the interactive edition you can choose the length of the game and the stakes, and click any position."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Two routes to the same fair share", toc="How it works", blocks=[
            dict(type="p", text=f"**Pascal's example.** In his letter of 29 July 1654, two players have put 32 pistoles each on a game of three. If one leads by two rounds to one and the game stops, Pascal reasons: if the next round went to the leader he would have all 64; if not, they would be level and each deserve 32. Either is equally likely, so he is owed the average, (64 + 32) ÷ 2 = **{p['s21']}**, and the other {p['o21']}. One round further back, at two to none, the leader is owed the average of 64 and 48, **{p['s20']}**, the other {p['o20']}. The program's table repeats both figures exactly:"),
            dict(type="svg", name="pascal-table-steps", draw=table_svg(d), alt="Pascal's table for a game to three rounds", width=800),
            dict(type="p", text=f"**Fermat's route.** If A needs a rounds and B needs b, the game is surely over within a + b − 1 more. List every way those rounds could fall; each is equally likely; count. The program compared both methods in exact fractions for all {ag['n']} positions up to {ag['N']} rounds each: they agree every time."),
            dict(type="p", text=f"Fermat's letter of 25 September 1654 counts a game for three players: \"I find here only 17 combinations for the first and 5 for each of the others.\" The case that gives these numbers is one player needing 1 round and the other two needing 2: the game is over within {th['rounds']} rounds, and of the {th['total']} equally likely sequences the first player wins **{th['a']}**, the others {th['b']} and {th['c']}."),
            dict(type="p", text="**Pascal's triangle.** Counting Fermat's cases is reading a row of the arithmetic triangle: when A needs 2 and B needs 3, four more rounds settle it, and A wins whenever A takes at least 2 of the 4: 6 + 4 + 1 = 11 of the 16 equally likely outcomes in row 4."),
            dict(type="table", head=["Row", "Entries"], num=[], rows=[[str(i), " ".join(r)] for i, r in enumerate(tri)]),
            dict(type="callout", kind="key", label="Key idea",
                 text="Build a table of answers to smaller problems, starting from the ones whose answers are obvious, and fill in each new answer from earlier ones. Pascal's shares are the oldest example in this book of what is now called dynamic programming."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Counting against filling in", toc="Measured", blocks=[
            dict(type="table", head=["Rounds each player needs", "Pascal's table (cells)", "Fermat's list (outcomes)"], num=[1, 2],
                 rows=[[x["k"], x["cells"], x["outcomes"]] for x in w]),
            dict(type="p", text="Fermat's method is the clearest proof that a share is fair; Pascal's is the one that scales. The list of outcomes doubles with every extra round, while the table grows only with the square of the length of the game."),
            dict(type="table", head=["Score in a game to " + pac["target"], "Proportional (Pacioli)", "Fair (Pascal, Fermat)"], num=[1, 2],
                 rows=[[f"{a} to {b}", f"{pr}%", f"{fa}%"] for a, b, pr, fa in pac["rows"]]),
            dict(type="p", text=f"The proportional rule gives the whole stake to a player who leads 1 to 0, and too little to one who leads 4 to 3. A simulation of {mc['n']} finished games for A needing 3 and B needing 5 estimated {mc['est']}; the table's exact answer is {mc['frac']} = {mc['exact']}, with no sampling error at all."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Five letters in one summer", toc="The evidence", blocks=[
            dict(type="p", text="Pacioli's *Summa* (1494) divided the stakes \"in proportion to the number of rounds won by each player\"; Tartaglia found \"counterintuitive results\" and wrote that \"in whatever way the division is made there will be cause for litigation\" (Wikipedia). The question reached Pascal from the Chevalier de Méré around 1654 (Wikipedia; Hart, Gresham College)."),
            dict(type="p", text="The letters are dated: Pascal's of 29 July 1654 with the 48-to-16 and 56-to-8 divisions; Pascal on 24 August, \"your theory which proceeds by combinations is very just\"; Fermat's replies of 29 August and 25 September (translation by Vera Sanford, in Smith's *Source Book*). MacTutor: they \"laid the foundation for the theory of probability\", solving the problem of points only for two players, and \"Pascal was not the first to study the Pascal triangle\". Calling Pascal's backward table the first dynamic programming is this book's reading (**conjecture**)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Values computed backward from the end", toc="Full circle", blocks=[
            dict(type="p", text="Pascal's move, reasoning from the finished game backward, one step at a time, is how a computer finds the value of a position in any game of chance or strategy with a known end: start from the positions where the outcome is settled, and fill in the rest from them."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"For a game to 20 rounds, Fermat's list would have {next(x for x in w if x['k'] == '20')['outcomes']} entries; Pascal's table has {next(x for x in w if x['k'] == '20')['cells']}. Richard Bellman's dynamic programming (Era 5) gives the method a name and a theory, and it is still how programs plan when each step's value depends on the steps that follow."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("At two rounds to one in a game to three, why is the leader owed 48 of 64?", "One more round: if he wins, he has 64; if he loses, it is level and he deserves 32. Each is equally likely: (64 + 32) ÷ 2 = 48."),
            ("Why may Fermat play out a + b − 1 rounds even if the game would have ended sooner?", "Extra rounds after the end do not change who won, and they make every listed outcome equally likely."),
            ("Why does Pacioli's rule fail at 1 to 0?", "It gives everything to the leader, though the other player can easily still win: it measures the past, not the future."),
            ("How many cells does Pascal need for a game in which each player needs 10 rounds?", "One per position: 10 × 10 = 100 averages, against 524,288 outcomes to list."),
            ("Where are the 17, 5 and 5 in Fermat's three-player game?", "Three more rounds, each won by any of the three players: 27 sequences. The player needing one round wins in 17; each of the others in 5."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Fermat and Pascal on Probability", text="The letters of 1654 in English, translated by Vera Sanford and Maxine Merrington.",
                 draw=C.draw_manuscript, link="https://www.uu.nl/sites/default/files/correspondentie_fermat_en_pascal.pdf", link_text="Utrecht University",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ProblemOfPoints", d["checks"],
                           "Pascal's 48 to 16 and 56 to 8, Fermat's enumeration against Pascal's table in exact fractions in 144 positions, the 17, 5 and 5 of Fermat's three-player game, the triangle's row sums in every position, and a million simulated games against the exact share.",
                           ["static Q[][] pascalTable(", "static Q fermat("]),
    ]
    return dict(
        title="The Problem of Points", date="1654",
        description="Era 3, topic 4 of The Algorithm Evolution Atlas: Pascal and Fermat on dividing the stakes of an unfinished game, by enumeration and by a table filled in backward.",
        lede="Two gamblers stop a game before the end. Merchants' books had disagreed for a century and a half about how to split the money. In one summer of letters, two Frenchmen settled it by two different routes: count every way the game could finish, or reason backward from the end.",
        fieldnote="Pascal never listed the futures. He started from the games that were already over, where the answer is obvious, and filled in a table backward, each answer the average of two easier ones. I have seen the same table, under other names, in every century since.",
        card=[("When", "Letters of July to September 1654"),
              ("Where", "Paris and Toulouse"),
              ("What hurt", "No fair rule for a game stopped early"),
              ("The fix", "Value a position by what can still happen: count, or work backward"),
              ("Cost", "One average per position, instead of a list that doubles every round")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ProblemOfPoints.java`.",
    )
