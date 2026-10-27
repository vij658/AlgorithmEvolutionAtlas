"""Era 8, topic 7: PageRank. Every number is parsed from PageRank.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram

LINKS = [[1, 2], [2], [0], [2, 4], [5], [3, 6], [], [2, 6]]   # the widget's web, as the program prints it (checked below)
POS = [(110, 70), (300, 60), (210, 190), (420, 200), (520, 90), (560, 300), (330, 330), (100, 300)]


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"web: ([\d,]+) pages, ([\d,]+) links, ([\d,]+) dangling pages ; d = ([\d.]+) ; power method from 1/N: (\d+) rounds .*? ; each round shrank the change by a factor of at most ([\d.]+) .*? ; top pages page:rank:links in (.*)$", ln):
            d["web"] = dict(n=m.group(1), links=m.group(2), dang=m.group(3), d=m.group(4), rounds=m.group(5), rate=m.group(6),
                            top=[tuple(p.split(":")) for p in m.group(7).split()])
        elif m := re.match(r"exact: (\d+) pages ; Gaussian elimination against the power method: largest difference ([\d.eE+-]+) ; a random surfer, ([\d,]+) steps: largest difference between share of visits and rank ([\d.]+), (\d+) of the top 10 the same ; N times the ranks satisfies Brin and Page's form \(1 - d\) \+ d sum to ([\d.eE+-]+)", ln):
            d["exact"] = dict(n=m.group(1), diff=m.group(2), steps=m.group(3), surf=m.group(4), same=m.group(5), bp=m.group(6))
        elif ln.startswith("damping: "):
            d["damp"] = re.findall(r"d = ([\d.]+): (\d+) rounds \(bound (\d+)\)", ln)
        elif ln.startswith("farm: "):
            d["farm"] = dict(page=re.search(r"page (\d+) of", ln).group(1), base=re.search(r"no farm: rank ([\d.]+), place (\d+) of (\d+)", ln).groups(),
                             rows=re.findall(r"(\d+) farm pages?: rank ([\d.]+), place (\d+) of (\d+)", ln))
        elif m := re.match(r"hits: (\d+) pages ; (\d+) rounds .*? ; top authorities ([\d ]+), top hubs ([\d ]+) ; (\d+) of the 10 best authorities", ln):
            d["hits"] = dict(n=m.group(1), rounds=m.group(2), auth=m.group(3), hubs=m.group(4), overlap=m.group(5))
        elif ln.startswith("widget: "):
            links = re.search(r"links (A->.*?) ; d", ln).group(1)
            rounds = re.findall(r"(\d+): ([\d.,]+)(?: ;|$)", ln.split("rounds of the power method from 1/8: ")[1].split(" ; exact")[0] + " ;")
            d["widget"] = dict(links=links, rounds=[[float(x) for x in r.split(",")] for _, r in rounds],
                               exact=[float(x) for x in re.search(r"exact: ([\d.,]+)", ln).group(1).split(",")])
    d["checks"] = C.checks(text)
    return d


def links_text():
    parts = []
    for i, outs in enumerate(LINKS):
        parts.append(f"{'ABCDEFGH'[i]}->" + ",".join("ABCDEFGH"[j] for j in outs) if outs else f"{'ABCDEFGH'[i]} (none: dangling)")
    return " ".join(parts)


# ----------------------------------------------------------------------------------------------------------------------
def web_svg(d):
    ex = d["widget"]["exact"]

    def draw(t, standalone):
        o = []
        W, H = 760, 470
        POS = [(x + 40, y + 55) for x, y in globals()["POS"]]
        o.append(C.text(20, 26, "The widget's 8 pages: area of each circle in proportion to its PageRank (d = 0.85)", t["ink"], 13, "start", 700))
        o.append(f'<defs><marker id="pr-ar{"s" if standalone else ""}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:{t["ink"]}"/></marker></defs>')
        R = [12 + 70 * math.sqrt(v) for v in ex]
        for a, outs in enumerate(LINKS):
            for b in outs:
                (x1, y1), (x2, y2) = POS[a], POS[b]
                dx, dy = x2 - x1, y2 - y1
                L = math.hypot(dx, dy)
                sx, sy = x1 + dx / L * (R[a] + 2), y1 + dy / L * (R[a] + 2)
                ex2, ey2 = x2 - dx / L * (R[b] + 4), y2 - dy / L * (R[b] + 4)
                o.append(f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex2:.1f}" y2="{ey2:.1f}" style="stroke:{t["ink"]};stroke-width:1.4" marker-end="url(#pr-ar{"s" if standalone else ""})"/>')
        for i, (x, y) in enumerate(POS):
            col = t["red"] if ex[i] == max(ex) else (t["muted"] if not LINKS[i] else t["blue"])
            o.append(C.circle(x, y, R[i], col))
            o.append(C.text(x, y + 5, "ABCDEFGH"[i], t["on_red"] if col == t["red"] else t["on_blue"], 14, "middle", 700))
            o.append(C.text(x + R[i] + 6, y - R[i] + 6, f"{ex[i]:.4f}", t["ink"], 12, "start"))
        o.append(C.text(640, 415, "G has no links:", t["muted"], 12))
        o.append(C.text(640, 433, "its rank is spread", t["muted"], 12))
        o.append(C.text(640, 451, "over all 8 pages.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Eight pages with their PageRanks", t, standalone, 0.55, 760)
    return draw


PR_HTML = """
<div class="board pr-board">
  <div style="min-width:0"><div class="pr-view" id="pr-view"></div></div>
  <div style="min-width:0">
    <div class="pr-btns"><button type="button" class="primary" id="pr-1">One round</button><button type="button" id="pr-10">Ten rounds</button><button type="button" id="pr-reset">Start again</button></div>
    <div class="pr-btns"><button type="button" id="pr-surf">Let a surfer click 1,000 times</button></div>
    <div class="pr-stats" id="pr-stats"></div>
    <p class="say" id="pr-say" aria-live="polite"></p>
  </div>
</div>
"""

PR_CSS = """
.pr-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.pr-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.pr-stats{font:13px var(--mono);display:grid;gap:2px;margin-top:8px}
"""

PR_JS = r"""
(() => {
  const view = document.getElementById("pr-view");
  if (!view) return;
  const L = __LINKS__, POS = __POS__, PROG = __PROG__, EXACT = __EXACT__, n = 8, d = 0.85, N = "ABCDEFGH";
  let pr, round, visits, steps, at;
  function step() {
    const nx = new Array(n).fill(0); let dang = 0;
    for (let v = 0; v < n; v++) { if (!L[v].length) { dang += pr[v]; continue; } const share = pr[v] / L[v].length; for (const u of L[v]) nx[u] += share; }
    for (let u = 0; u < n; u++) nx[u] = (1 - d) / n + d * (nx[u] + dang / n);
    pr = nx; round++;
  }
  function draw(msg) {
    view.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 640 400", role: "img", "aria-label": "Eight linked pages"}, view);
    const defs = sv("defs", {}, svg), mk = sv("marker", {id: "pr-arw", viewBox: "0 0 10 10", refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse"}, defs);
    sv("path", {d: "M0,0 L10,5 L0,10 z", fill: "var(--ink)"}, mk);
    const R = pr.map(v => 12 + 70 * Math.sqrt(v));
    L.forEach((outs, a) => outs.forEach(b => {
      const [x1, y1] = POS[a], [x2, y2] = POS[b], dx = x2 - x1, dy = y2 - y1, len = Math.hypot(dx, dy);
      sv("line", {x1: x1 + dx / len * (R[a] + 2), y1: y1 + dy / len * (R[a] + 2), x2: x2 - dx / len * (R[b] + 4), y2: y2 - dy / len * (R[b] + 4), stroke: "var(--ink)", "stroke-width": 1.4, "marker-end": "url(#pr-arw)"}, svg);
    }));
    const top = Math.max(...pr);
    POS.forEach(([x, y], i) => {
      sv("circle", {cx: x, cy: y, r: R[i], fill: pr[i] === top ? "var(--red)" : L[i].length ? "var(--blue)" : "var(--muted)", stroke: at === i ? "var(--yellow)" : "none", "stroke-width": 5}, svg);
      sv("text", {x, y: y + 5, "text-anchor": "middle", "font-size": 14, "font-weight": 700, fill: "var(--paper)"}, svg, N[i]);
    });
    const st = document.getElementById("pr-stats"); st.innerHTML = "";
    el("div", {}, st, `round ${round}`);
    pr.forEach((v, i) => el("div", {}, st, `${N[i]}  ${v.toFixed(4)}  exact ${EXACT[i].toFixed(4)}${visits ? `  surfer ${(visits[i] / steps).toFixed(3)}` : ""}`));
    if (msg) document.getElementById("pr-say").textContent = msg;
  }
  function rounds(k) {
    for (let j = 0; j < k; j++) step();
    const pg = PROG[round - 1];
    const same = pg && pg.every((v, i) => v.toFixed(4) === pr[i].toFixed(4));
    draw(`After ${round} round${round === 1 ? "" : "s"}: each page passed its rank along its links, 85% of it, and every page got an equal share of the rest.` + (pg ? ` The program's round ${round}: ${same ? "the same to 4 decimals" : "different"}.` : ""));
  }
  function surf() {
    if (!visits) { visits = new Array(n).fill(0); steps = 0; at = 0; }
    for (let k = 0; k < 1000; k++) {
      visits[at]++; steps++;
      if (!L[at].length || Math.random() >= d) at = Math.floor(Math.random() * n);
      else at = L[at][Math.floor(Math.random() * L[at].length)];
    }
    draw(`A random surfer has clicked ${steps.toLocaleString("en-US")} times (85% of the time a link, otherwise a random page). Its share of visits to each page approaches the page's rank.`);
  }
  function reset() { pr = new Array(n).fill(1 / n); round = 0; visits = null; at = -1; draw("Every page starts with 1/8. Press One round."); }
  document.getElementById("pr-1").addEventListener("click", () => rounds(1));
  document.getElementById("pr-10").addEventListener("click", () => rounds(10));
  document.getElementById("pr-reset").addEventListener("click", reset);
  document.getElementById("pr-surf").addEventListener("click", surf);
  reset();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How PageRank combined older ideas, and where it led")
    W = 210
    nodes = {
        "mk": (20, 20, "Markov chains", "a walk settles into fixed shares", "Era 4", "ink"),
        "kw": (395, 20, "Keyword search", "matches words, returns junk", "the engines of 1998", "ink"),
        "web": (770, 20, "The link graph", "518 million links among 24 million pages", "Brin and Page, 1998", "ink"),
        "pr": (395, 180, "PageRank", "⊕ the random surfer, with damping 0.85", "Page and Brin, Stanford, 1998", "red"),
        "hits": (20, 340, "Hubs and authorities", "two scores, computed per query", "Kleinberg, 1999", "ink"),
        "pat": (770, 340, "The patent", "assigned to Stanford; licensed to Google", "granted 2001", "ink"),
        "today": (395, 490, "Google", "the search engine built on it", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("mk", "pr", ports=("bottom", "top:0.15"))
    D.edge("kw", "pr", ports=("bottom", "top"), label="replaced", at=0.5, dx=8, anchor="start")
    D.edge("web", "pr", ports=("bottom", "top:0.85"))
    D.edge("pr", "hits", ports=("bottom:0.15", "top"), label="a contemporary", at=0.4, dx=-8, anchor="end")
    D.edge("pr", "pat", ports=("bottom:0.85", "top"))
    D.edge("pr", "today", ports=("bottom", "top"))
    D.text(20, 615, "HITS is a contemporary, not a descendant: Kleinberg's paper appeared in 1999.", "caption")
    return D


def chain(d):
    w, f = d["web"], d["farm"]
    big = f["rows"][-1]
    steps = [
        ("Keyword engines returned \"Junk results\" that \"wash out\" what the user wanted",
         "Rank by links: a page is important if important pages link to it", "Brin and Page, 1998"),
        ("That definition is circular: every rank depends on every other",
         f"The power method: {w['rounds']} rounds settle {w['n']} pages", "repeated multiplication"),
        ("Pages without links, and closed loops, trap a surfer that only follows links",
         "Damping: 15% of the time, jump to a random page", "d = 0.85"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from keywords to links")
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
    w, ex, dm, fm, hi, wg = d["web"], d["exact"], d["damp"], d["farm"], d["hits"], d["widget"]
    assert links_text() == wg["links"], (links_text(), wg["links"])
    top_rows = [[p, r, f"{int(l):,}"] for p, r, l in w["top"]]
    damp_rows = [[a, b, c] for a, b, c in dm]
    farm_rows = [["none", fm["base"][0], f"{fm['base'][1]} of {fm['base'][2]}"]] + [[k, r, f"{p} of {n}"] for k, r, p, n in fm["rows"]]
    big = fm["rows"][-1]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Markov chains (Era 4) settle into fixed long-run shares. The search engines of 1998 matched keywords and drowned the good pages in junk. Page and Brin treated the Web's links as a Markov chain, a random surfer clicking forever, and ranked each page by the share of time the surfer spends there. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: PageRank. Blue: the search engine built on it."),
        ]),
        dict(id="play", eyebrow="Try it", title="Pass the rank along the links", toc="Try it", blocks=[
            dict(type="p", text="Eight pages, A to H, with their links. Every page starts with rank 1/8. Each round, every page passes 85% of its rank, split equally, along its links; G has no links, so its rank is spread over all pages; and every page gets an equal share of the remaining 15%. The circles grow and shrink and settle. The rounds are exactly the program's. Or let a random surfer click around and count its visits."),
            dict(type="widget", html=PR_HTML, js=PR_JS.replace("__LINKS__", json.dumps(LINKS)).replace("__POS__", json.dumps(POS)).replace("__PROG__", json.dumps(wg["rounds"])).replace("__EXACT__", json.dumps(wg["exact"])), css=PR_CSS,
                 fallback=dict(type="table", head=["Round"] + list("ABCDEFGH"), num=list(range(9)),
                               rows=[[str(i + 1)] + [f"{v:.4f}" for v in r] for i, r in enumerate(wg["rounds"])] + [["exact"] + [f"{v:.4f}" for v in wg["exact"]]]),
                 note="In the interactive edition you can run the rounds one at a time and send a random surfer around the pages."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A surfer who never stops", toc="How it works", blocks=[
            dict(type="p", text="**The equation.** With N pages and damping d = 0.85, page u's rank is PR(u) = (1 − d)/N + d × Σ PR(v)/L(v), summed over the pages v that link to u, where L(v) is the number of links on v. One equation per page, all at once."),
            dict(type="p", text="**The surfer.** Read the equation as a random surfer: at each step, with probability d, click a random link on the current page; otherwise jump to a page chosen at random. PR(u) is the long-run share of time spent on u. A page with no links sends the surfer to a random page. The random jumps also stop the surfer from being trapped in a closed loop, so the shares exist and are unique."),
            dict(type="p", text="**The power method.** Start with every page at 1/N and apply the right-hand side again and again. Each round shrinks the remaining error by a factor of at most d, whatever the size of the Web, and each round costs one pass over the links. Brin and Page wrote the formula as PR(A) = (1 − d) + d Σ …, which gives the same ranking multiplied by N."),
            dict(type="svg", name="web8", draw=web_svg(d), alt="Eight pages with their links and PageRanks", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Let the pages vote with their links, and weigh each vote by the voter's own rank. The circularity is not a problem: it is an eigenvector, and repeated multiplication finds it."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Ten thousand pages, one surfer", toc="Measured", blocks=[
            dict(type="p", text=f"**A made-up web** of {w['n']} pages and {w['links']} links, grown so that new pages tend to link to pages that are already well linked; {w['dang']} pages have no links. From 1/N, the power method needed {w['rounds']} rounds to change by less than 10⁻¹⁰; each round shrank the change by a factor of at most {w['rate']}, well under d. The top pages are the oldest and most linked:"),
            dict(type="table", head=["Page", "Rank", "Links in"], num=[0, 1, 2], rows=top_rows),
            dict(type="p", text=f"**Checked three ways** on a web of {ex['n']} pages: the power method agrees with Gaussian elimination on the {ex['n']} equations to {C.sci(ex['diff'])}; a random surfer taking {ex['steps']} steps visits each page in proportion to its rank (largest difference {ex['surf']}, and {ex['same']} of the top 10 the same); and N times the ranks satisfies Brin and Page's form to {C.sci(ex['bp'])}."),
            dict(type="p", text="**The damping factor**: rounds to a change below 10⁻¹⁰ on the 10,000-page web, against the worst-case bound log(10⁻¹⁰/2)/log d:"),
            dict(type="table", head=["d", "Rounds", "Bound"], num=[0, 1, 2], rows=damp_rows, hl=1),
            dict(type="p", text=f"On this well-connected web the rounds barely depend on d; the bound is for the worst case. Wikipedia reports 52 rounds for a 322-million-link network in the original work, and the AMS Feature Column \"50 – 100\"."),
            dict(type="p", text=f"**A link farm.** Page {fm['page']} sits in the middle of the {ex['n']}-page web. New pages that link only to it lift it:"),
            dict(type="table", head=["Farm pages", "Rank", "Place"], num=[0, 1], rows=farm_rows, hl=len(farm_rows) - 1),
            dict(type="p", text=f"**Hubs and authorities** (HITS) on the same {hi['n']} pages settled in {hi['rounds']} rounds; {hi['overlap']} of the 10 best authorities are among PageRank's top 10."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Twenty-four million pages at Stanford", toc="The evidence", blocks=[
            dict(type="p", text="Brin and Page (Computer Science Department, Stanford University), *Computer Networks and ISDN Systems* 30 (1998): PR(A) = (1 − d) + d (PR(T₁)/C(T₁) + … + PR(Tₙ)/C(Tₙ)); \"We usually set d to 0.85\"; the PageRanks \"form a probability distribution over Web pages\"; at least 24 million pages and link maps with \"as many as 518 million of these hyperlinks\"; PageRank \"can be calculated using a simple iterative algorithm\", for 26 million pages \"in a few hours on a medium size workstation\". Keyword engines gave \"Junk results\" that \"often wash out any results that a user is interested in\"."),
            dict(type="p", text="Wikipedia: PageRank was developed at Stanford \"as a research project\" from 1996; Robin Li's RankDex (1996) used a related ranking; the patent, assigned to Stanford and granted in 2001, earned Stanford 1.8 million Google shares, sold in 2005 for $336 million; the normalized form sums to one, which the original paper confused with a variant that sums to N. The AMS Feature Column (Austin, 2006) explains the Google matrix, the power method and why d near 0.85 is a compromise. Kleinberg's HITS (*Journal of the ACM*, 1999) scores hubs and authorities per query."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Markov's chains, on the Web", toc="Full circle", blocks=[
            dict(type="p", text="Markov (Era 4) counted vowels and consonants in a poem and showed that a chain of dependent steps still settles into fixed shares. PageRank is those shares, for a chain whose states are Web pages and whose steps are clicks. MapReduce (topic 11) was built partly to run computations like this one on thousands of machines."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"A surfer clicking {ex['steps']} times visited every page of a {ex['n']}-page web within {ex['surf']} of its rank. The equations and the random walk are the same thing, seen two ways."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Two pages link only to each other, and nothing else exists. With d = 0.85, what are their ranks?", "By symmetry, ½ each: (0.15)/2 + 0.85 × ½ = ½."),
            ("A page with rank 0.2 has 4 links. How much does it pass along each, before damping?", "0.2/4 = 0.05; with damping, 0.85 × 0.05 = 0.0425."),
            ("Why do the random jumps matter?", "Without them a surfer can be trapped in a loop or on a page with no links, and the long-run shares need not be unique."),
            ("Why does the change shrink by at least a factor of d each round?", "The 15% that is spread evenly is the same every round; only the 85% that follows links carries the error forward."),
            ("Can a page raise its own rank by linking to more pages?", "No: its outgoing links pass its rank on and do not bring any back; incoming links do."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Anatomy of a Large-Scale Hypertextual Web Search Engine (1998)", text="Brin and Page's paper on the Google prototype, with the PageRank formula.",
                 draw=C.draw_manuscript, link="https://www.ics.uci.edu/~djp3/classes/2008_01_01_INF141/Materials/brin1998.pdf", link_text="The paper (PDF, on a UC Irvine course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "PageRank", d["checks"],
                           "the ranks against the equations, Gaussian elimination and a random surfer, every page's share of random jumps, the link farm, and the widget's ten rounds.",
                           ["static double[] round(int[][] g, double[] pr, double d)"]),
    ]
    return dict(
        title="PageRank", date="1998",
        description="Era 8, topic 7 of The Algorithm Evolution Atlas: Page and Brin's PageRank (Stanford, 1998), the random surfer and the power method, checked by Gaussian elimination and by a surfer clicking four million times.",
        lede="Search engines in 1998 matched keywords and returned junk. Page and Brin ranked pages by their links instead: a page is important if important pages link to it, which is the share of time a random surfer spends there.",
        fieldnote=f"I grew a web of {w['n']} pages and let the ranks pass along its links. They settled in {w['rounds']} rounds. Then I sent a surfer clicking at random through a smaller web, {ex['steps']} times; its visits matched the ranks to within {ex['surf']}. A hundred pages that did nothing but link to one obscure page lifted it to place {big[2]}.",
        card=[("When", "Project 1996; paper April 1998"),
              ("Where", "Stanford University"),
              ("What hurt", "Keyword search returned junk"),
              ("The fix", "Rank by links: a damped random surfer, by the power method"),
              ("Checked", f"Power method = Gaussian elimination to {C.sci(ex['diff'])}")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `PageRank.java`.",
    )
