"""Era 9, topic 8: Monte Carlo tree search and AlphaGo. Every number is parsed from MonteCarloTreeSearch.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("tictactoe: "):
            d["ttt_n"] = re.search(r"([\d,]+) positions in play", ln).group(1)
            d["ttt_sample"] = re.search(r"UCT on (\d+) random positions", ln).group(1)
            d["ttt"] = re.findall(r"([\d,]+) rounds: a best move in (\d+) of (\d+) \((\d+) of (\d+) where a wrong move exists\)", ln)
        elif ln.startswith("connect4: "):
            d["random"] = re.search(r"against random moves: (\d+) wins, (\d+) draws, (\d+) losses", ln).groups()
            d["more"] = re.search(r"against UCT 500: (\d+) wins, (\d+) draws, (\d+) losses", ln).groups()
        elif ln.startswith("prior: "):
            d["prior"] = re.search(r"plain UCT, 500 rounds: (\d+) wins, (\d+) draws, (\d+) losses", ln).groups()
        elif ln.startswith("position: "):
            d["pos_moves"] = [int(x) for x in re.search(r"moves ([\d, ]+) \(columns", ln).group(1).split(", ")]
            d["pos"] = [(int(c), int(v), int(w)) for c, v, w in re.findall(r"column (\d+): (\d+) visits, wins (\d+)%", ln)]
            d["chosen"] = re.search(r"chosen: column (\d+)", ln).group(1)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def position_svg(d):
    def draw(t, standalone):
        W, H = 760, 400
        o = [C.text(20, 26, f"Yellow to move. 5,000 rounds of UCT: where the search spent them", t["ink"], 13, "start", 700)]
        cs, x0, y0 = 46, 40, 60
        h = [0] * 7
        board = {}
        for i, c in enumerate(d["pos_moves"]):
            board[(h[c - 1], c - 1)] = "R" if i % 2 == 0 else "Y"
            h[c - 1] += 1
        o.append(C.rect(x0 - 6, y0 - 6, 7 * cs + 12, 6 * cs + 12, t["blue"], None, 0, 8, ";fill-opacity:0.18"))
        for r in range(6):
            for c in range(7):
                cx, cy = x0 + c * cs + cs / 2, y0 + (5 - r) * cs + cs / 2
                who = board.get((r, c))
                fill = t["red"] if who == "R" else t["yellow"] if who == "Y" else t["paper"]
                o.append(C.circle(cx, cy, cs / 2 - 5, fill, t["rule"], 1))
        for c in range(7):
            o.append(C.text(x0 + c * cs + cs / 2, y0 + 6 * cs + 22, str(c + 1), t["muted"], 12, "middle"))
        bx, bw = 440, 260
        mx = max(v for _, v, _ in d["pos"])
        for i, (c, v, w) in enumerate(d["pos"]):
            y = 64 + i * 40
            o.append(C.text(bx - 10, y + 16, f"col {c}", t["ink"], 12, "end"))
            col = t["red"] if str(c) == d["chosen"] else t["blue"]
            o.append(C.rect(bx, y, bw * v / mx, 22, col, None, 0, 2))
            o.append(C.text(bx + bw * v / mx + 6, y + 16, f"{v:,} visits, {w}% wins", t["ink"], 12))
        o.append(C.text(20, H - 12, f"The search spent most of its rounds on column {d['chosen']}, the move it plays. Win rates are from Yellow's side.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A Connect Four position and the visit counts of Monte Carlo tree search", t, standalone, 0.55, 760)
    return draw


C4_HTML = """
<div class="board c4-board">
  <div style="min-width:0"><div class="c4-view" id="c4-view"></div></div>
  <div style="min-width:0">
    <label class="c4-row">Rounds per move: <select id="c4-rounds"><option>50</option><option>300</option><option selected>2000</option><option>8000</option></select></label>
    <div class="c4-btns"><button type="button" class="primary" id="c4-new">New game, you first</button><button type="button" id="c4-ai">Let the computer move</button></div>
    <div class="c4-h">The computer's last search</div>
    <div class="c4-bars" id="c4-bars"></div>
    <p class="say" id="c4-say" aria-live="polite"></p>
  </div>
</div>
"""

C4_CSS = """
.c4-board{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:18px}
@media (max-width:760px){.c4-board{grid-template-columns:1fr}}
.c4-view svg{width:100%;height:auto;display:block}
.c4-view .colhit{cursor:pointer}
.c4-row{display:block;font-size:13px;margin-bottom:8px}
.c4-btns{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.c4-h{font-size:12px;font-weight:700;color:var(--muted);margin:10px 0 4px}
.c4-bars{font:12.5px var(--mono);display:grid;gap:3px}
.c4-bar{display:grid;grid-template-columns:3.2em 1fr;align-items:center;gap:6px}
.c4-bar>span:last-child{display:flex;align-items:center;gap:6px;white-space:nowrap}
.c4-bar span.b{display:block;height:14px;background:var(--blue);flex:none}
.c4-bar span.b.top{background:var(--red)}
"""

C4_JS = r"""
(() => {
  const view = document.getElementById("c4-view");
  if (!view) return;
  let b, h, turn, n, last, over, human = 1, seed = 42;
  const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
  function reset() { b = new Array(42).fill(0); h = new Array(7).fill(0); turn = 1; n = 0; last = -1; over = 0; }
  const copy = () => ({b: b.slice(), h: h.slice(), turn, n, last});
  const moves = g => [0, 1, 2, 3, 4, 5, 6].filter(c => g.h[c] < 6);
  function play(g, c) { g.last = g.h[c] * 7 + c; g.b[g.last] = g.turn; g.h[c]++; g.turn = 3 - g.turn; g.n++; }
  function winner(g) {
    if (g.last < 0) return 0;
    const p = g.b[g.last], r = Math.floor(g.last / 7), c = g.last % 7;
    for (const [dr, dc] of [[0, 1], [1, 0], [1, 1], [1, -1]]) {
      let k = 1;
      for (const s of [-1, 1]) { let rr = r + s * dr, cc = c + s * dc; while (rr >= 0 && rr < 6 && cc >= 0 && cc < 7 && g.b[rr * 7 + cc] === p) { k++; rr += s * dr; cc += s * dc; } }
      if (k >= 4) return p;
    }
    return g.n === 42 ? 3 : 0;
  }
  function search(rounds) {
    const root = {move: -1, mover: 3 - turn, kids: [], untried: moves(copy()), wins: 0, visits: 0, parent: null};
    for (let it = 0; it < rounds; it++) {
      let nd = root; const g = copy();
      while (!nd.untried.length && nd.kids.length) {
        let best = null, bs = -Infinity;
        for (const k of nd.kids) { const s = k.wins / k.visits + Math.SQRT2 * Math.sqrt(Math.log(nd.visits) / k.visits); if (s > bs) { bs = s; best = k; } }
        nd = best; play(g, nd.move);
      }
      if (nd.untried.length) {
        const i = Math.floor(rnd() * nd.untried.length), m = nd.untried[i];
        nd.untried[i] = nd.untried[nd.untried.length - 1]; nd.untried.pop();
        const mover = g.turn; play(g, m);
        const k = {move: m, mover, kids: [], untried: winner(g) ? [] : moves(g), wins: 0, visits: 0, parent: nd};
        nd.kids.push(k); nd = k;
      }
      let w;
      while (!(w = winner(g))) { const ms = moves(g); play(g, ms[Math.floor(rnd() * ms.length)]); }
      for (let a = nd; a; a = a.parent) { a.visits++; a.wins += w === 3 ? 0.5 : (w === a.mover ? 1 : 0); }
    }
    return root;
  }
  function draw() {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 350 320", role: "img", "aria-label": "Connect Four board; click a column to drop a disc"}, view);
    sv("rect", {x: 0, y: 0, width: 350, height: 300, rx: 10, fill: "var(--blue)", "fill-opacity": 0.22}, svg);
    for (let r = 0; r < 6; r++) for (let c = 0; c < 7; c++) {
      const v = b[r * 7 + c];
      sv("circle", {cx: 25 + c * 50, cy: 275 - r * 50, r: 20, fill: v === 1 ? "var(--red)" : v === 2 ? "var(--yellow)" : "var(--paper)", stroke: r * 7 + c === last ? "var(--ink)" : "var(--rule)", "stroke-width": r * 7 + c === last ? 3 : 1}, svg);
    }
    for (let c = 0; c < 7; c++) {
      sv("text", {x: 25 + c * 50, y: 316, "text-anchor": "middle", "font-size": 12, fill: "var(--muted)"}, svg, String(c + 1));
      const hit = sv("rect", {x: c * 50, y: 0, width: 50, height: 300, fill: "transparent", class: "colhit", id: `c4-col${c + 1}`}, svg);
      hit.addEventListener("click", () => humanMove(c));
    }
  }
  function say(t) { document.getElementById("c4-say").textContent = t; }
  function end() {
    const w = winner(copy()); if (!w) return false;
    over = w; say(w === 3 ? "A draw." : w === human ? "You win. Try more rounds per move." : "The computer wins."); return true;
  }
  function aiMove() {
    if (over) return;
    const R = +document.getElementById("c4-rounds").value, root = search(R);
    const kids = root.kids.slice().sort((a, c) => a.move - c.move), best = root.kids.reduce((a, c) => c.visits > a.visits ? c : a);
    const bars = document.getElementById("c4-bars"); bars.innerHTML = "";
    const mx = Math.max(...kids.map(k => k.visits));
    kids.forEach(k => { const row = el("div", {class: "c4-bar"}, bars); el("span", {}, row, `col ${k.move + 1}`); const cell = el("span", {}, row); el("span", {class: "b" + (k === best ? " top" : ""), style: `width:${45 * k.visits / mx}%`}, cell); el("span", {}, cell, ` ${k.visits} visits, ${Math.round(100 * k.wins / k.visits)}% wins`); });
    const g = {b, h, turn, n, last}; play(g, best.move); ({b, h, turn, n, last} = g);
    draw();
    if (!end()) say(`The computer ran ${R} rounds and played column ${best.move + 1}, its most visited move (${Math.round(100 * best.wins / best.visits)}% wins in its playouts). Your move.`);
  }
  function humanMove(c) {
    if (over || turn !== human || h[c] >= 6) return;
    const g = {b, h, turn, n, last}; play(g, c); ({b, h, turn, n, last} = g);
    draw();
    if (!end()) { say("Thinking..."); setTimeout(aiMove, 30); }
  }
  document.getElementById("c4-new").addEventListener("click", () => { reset(); human = 1; draw(); document.getElementById("c4-bars").innerHTML = ""; say("You are red. Click a column."); });
  document.getElementById("c4-ai").addEventListener("click", () => { if (turn !== human || over) return; human = 3 - human; aiMove(); });
  reset(); draw(); say("You are red. Click a column, or let the computer move first.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 520, "How AlphaGo's search combined older ideas, and where it led")
    W = 220
    nodes = {
        "mm": (20, 20, "Game-tree search", "look ahead, score positions, back up the best", "", "ink"),
        "mc": (265, 20, "Random playouts", "judge a position by playing it out at random", "Abramson, 1987; Brügmann, 1992", "ink"),
        "ucb": (510, 20, "UCB1", "a bandit formula: win rate plus a bonus for few tries", "", "ink"),
        "nn": (755, 20, "Deep networks", "learn to propose and to judge", "topics 2 and 7", "ink"),
        "uct": (265, 200, "MCTS and UCT", "⊕ a tree grown from playouts, guided by UCB1", "Coulom; Kocsis and Szepesvári, 2006", "red"),
        "ag": (630, 200, "AlphaGo", "⊕ policy and value networks inside the search", "DeepMind, 2016", "red"),
        "az": (630, 380, "AlphaZero", "no playouts: the value network judges", "2017", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("mm", "uct", ports=("bottom", "top:0.15"))
    D.edge("mc", "uct", ports=("bottom", "top"))
    D.edge("ucb", "uct", ports=("bottom", "top:0.85"))
    D.edge("uct", "ag", ports=("right", "left"))
    D.edge("nn", "ag", ports=("bottom", "top:0.7"))
    D.edge("ag", "az", ports=("bottom", "top"))
    D.text(20, 505, "Game-tree search means looking ahead move by move, as chess programs did; UCB1 comes from the study of multi-armed bandits.", "caption")
    return D


def chain():
    steps = [
        ("Go has too many moves for exhaustive search, and no good rule to score a position",
         "Score a position by random playouts to the end", "Abramson, 1987; Brügmann, 1992"),
        ("Playouts from the root alone spend as much effort on bad moves as on good ones",
         "Grow a tree, and choose where to look by UCB1: UCT", "Coulom; Kocsis and Szepesvári, 2006"),
        ("Random playouts judge Go positions badly, and every move gets tried",
         "A policy network to propose moves, a value network to judge positions", "AlphaGo, 2016"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from playouts to AlphaGo")
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
    ttt = d["ttt"]
    ra, mo, pr = d["random"], d["more"], d["prior"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Chess programs searched a tree of moves and scored positions with hand-written rules. Go has too many moves for that and no good rule. Random playouts gave a crude score; in 2006 Coulom grew a tree from them, and Kocsis and Szepesvári chose where to look with UCB1, a formula from the study of gambling machines. Ten years later DeepMind put two neural networks inside that search."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Monte Carlo tree search and AlphaGo. Blue: what came after."),
        ]),
        dict(id="play", eyebrow="Try it", title="Play against the search", toc="Try it", blocks=[
            dict(type="p", text="The computer knows only the rules of Connect Four. For each move it runs the chosen number of rounds of UCT with random playouts, then plays its most visited column; the bars show where its rounds went. Beat it at 50 rounds, then try 2,000."),
            dict(type="widget", html=C4_HTML, js=C4_JS, css=C4_CSS,
                 fallback=dict(type="svg", name="position", draw=position_svg(d), alt="A Connect Four position and the search's visit counts", width=760),
                 note="In the interactive edition you can play Connect Four against the search."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Four steps, many times", toc="How it works", blocks=[
            dict(type="p", text="**Selection.** Start at the root. While every move from the current node has been tried, go to the child with the largest score w/n + c·√(ln N / n), where w is the child's wins, n its visits, N the parent's visits and c = √2 here. The first term favours moves that have done well; the second, moves tried only a few times. This is the standard UCB1 form; the sources opened for this page describe it without printing it."),
            dict(type="p", text="**Expansion.** Add one untried move as a new node. **Simulation.** From there, play random moves to the end of the game. **Backpropagation.** Walk back to the root, adding one visit to every node on the path and a win (or half for a draw) to every node whose move was made by the winner."),
            dict(type="p", text="**Choosing.** After the last round, play the root's most visited move. The bonus term shrinks as a move is visited, so moves that keep winning keep getting rounds and the rest are tried just often enough not to be overlooked."),
            dict(type="p", text="**AlphaGo's changes.** A policy network, trained on expert games, gives each move a prior probability, and the search tries likely moves first and longest. A value network judges positions, alone or together with playouts. The program here has no networks; it tests the first change with a hand-written prior that prefers central columns."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Spend the simulations where they are most informative: on the moves that look best, and on the moves you know least about. No evaluation rule is needed; the game's own ending is the judge."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Checked against perfect play", toc="Measured", blocks=[
            dict(type="p", text=f"**Tic-tac-toe, solved.** The program computes the exact value of all {d['ttt_n']} positions that can arise in play (the empty board is a draw), then gives UCT {d['ttt_sample']} of them at random. A move counts as right if it keeps the best result available. The harder test is the positions where some move is wrong:"),
            dict(type="table", head=["Rounds per move", "Best move, all positions", "Best move where a wrong one exists"], num=[0, 1, 2],
                 rows=[[a, f"{b} of {c}", f"{e} of {f}"] for a, b, c, e, f in ttt], hl=len(ttt) - 1),
            dict(type="p", text=f"**Connect Four** (7 columns, 6 rows; each side moves first in half the games). UCT with 200 rounds against random moves: {ra[0]} wins, {ra[1]} draws, {ra[2]} losses. UCT with 2,000 rounds against UCT with 500: {mo[0]} wins, {mo[1]} draws, {mo[2]} losses. More search is stronger."),
            dict(type="p", text=f"**A prior.** Give the search a hand-written prior over the columns, 1, 2, 3, 4, 3, 2, 1 (out of 16), and select by win rate + 1.5 · prior · √N / (1 + n), the shape of AlphaGo's selection rule. At an equal 500 rounds, against plain UCT: {pr[0]} wins, {pr[1]} draws, {pr[2]} losses. A prior that proposes sensible moves makes the same number of rounds go further; AlphaGo's came from a network trained on 30 million expert moves."),
            dict(type="p", text=f"**Where the rounds go.** In one position (Red has played 4, 3, 3 and Yellow 4, 5), 5,000 rounds split as follows; the search plays column {d['chosen']}:"),
            dict(type="table", head=["Column", "Visits", "Yellow's wins in playouts"], num=[0, 1, 2],
                 rows=[[c, f"{v:,}", f"{w}%"] for c, v, w in d["pos"]], hl=int(d["chosen"]) - 1),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="From 1987 to Seoul", toc="The evidence", blocks=[
            dict(type="p", text="Wikipedia: Abramson's 1987 thesis used random playouts in an expected-outcome model; Brügmann used Monte Carlo methods in a Go program in 1992; in 2006 Coulom coined the name \"Monte Carlo tree search\", and Kocsis and Szepesvári developed UCT from UCB1; each round has four steps, selection, expansion, simulation and backpropagation; AlphaGo beat Lee Sedol in March 2016 in \"a five-game match with a final score of four games to one\"; AlphaZero \"replaces the simulation step with an evaluation based on a neural network\"."),
            dict(type="p", text="Silver and Hassabis, 27 January 2016: Go's search space is \"more than a googol times larger than chess\"; the policy network was trained on 30 million moves \"until it could predict the human move 57% of the time\" (the previous record was 44%); AlphaGo \"won all but one of its 500 games\" against other Go programs and beat the European champion Fan Hui \"by 5 games to 0\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Monte Carlo comes home", toc="Full circle", blocks=[
            dict(type="p", text="The Monte Carlo method was born at Los Alamos (Era 4, topic 10) to estimate what could not be calculated, by sampling. Sixty years later it became a way to choose moves in the hardest board game: sample the future, and let the samples decide where to sample next."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Knowing nothing but the rules, UCT with 3,000 rounds found a best move in {ttt[-1][3]} of {ttt[-1][4]} tic-tac-toe positions where a wrong move was possible."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A child has 6 wins in 10 visits, its parent 100 visits. What is its UCB1 score with c = √2?", "0.6 + √2 · √(ln 100 / 10) = 0.6 + 1.414 · 0.679 ≈ 1.56."),
            ("Why play the most visited move rather than the one with the best win rate?", "A move with a high win rate from few visits may be lucky; many visits mean the search kept finding it good."),
            ("What does the bonus term do to a move that is never visited again?", "Its bonus grows slowly with the parent's visits (ln N), so it will eventually be tried again."),
            ("Why can random playouts misjudge a position?", "Random players miss threats a real player would see; a position that is lost against good play can win many random games."),
            ("What did AlphaZero remove from the four steps?", "The simulation: a value network judges the new position instead of random playouts."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="AlphaGo: Mastering the ancient game of Go with Machine Learning (2016)", text="Silver and Hassabis, Google Research blog.",
                 draw=C.draw_manuscript, link="https://research.google/blog/alphago-mastering-the-ancient-game-of-go-with-machine-learning/", link_text="Google Research blog", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MonteCarloTreeSearch", d["checks"],
                           "UCT's moves against the exact solution of tic-tac-toe, wins against random play and weaker search, and the effect of a prior.",
                           ["static Node search(Game root, int rounds, Random r, double[] prior)"]),
    ]
    return dict(
        title="Monte Carlo Tree Search and AlphaGo", date="2006–2016",
        description="Era 9, topic 8 of The Algorithm Evolution Atlas: Monte Carlo tree search and UCT (2006), checked against perfect tic-tac-toe and played at Connect Four, and the networks AlphaGo added (2016).",
        lede="Chess fell to search with hand-written scoring. Go resisted: too many moves, and no good way to score a position. The answer began as something almost absurd, playing the game out at random many times, and grew into the search that beat Lee Sedol in 2016.",
        fieldnote=f"I gave the program only the rules of two games. To judge a move it played the rest of the game at random, again and again, and spent its effort where the results were promising or uncertain. In tic-tac-toe, with 3,000 rounds, it found a best move in {ttt[-1][3]} of {ttt[-1][4]} positions where a wrong one was possible.",
        card=[("When", "1987 to 2006; AlphaGo 2016"),
              ("Where", "Abramson, Brügmann, Coulom, Kocsis and Szepesvári; DeepMind"),
              ("What hurt", "Go's tree was too large, and no rule could score a position"),
              ("The fix", "Random playouts, a growing tree and UCB1; then networks"),
              ("Checked", f"{ttt[-1][3]} of {ttt[-1][4]} hard tic-tac-toe positions right")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MonteCarloTreeSearch.java`.",
    )
