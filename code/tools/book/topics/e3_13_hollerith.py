"""Era 3, topic 13: Hollerith's tabulator. Every number is parsed from HollerithTabulator.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"trial: .*? rivals (\S+) and (\S+) hours, Hollerith (\S+), (\S+) and (\S+) times faster ; .*? rivals (\S+) and (\S+) hours, Hollerith (\S+), (\S+) and (\S+) times faster$", ln):
            g = m.groups()
            d["trial"] = dict(c1=g[0], c2=g[1], ch=g[2], cs1=g[3], cs2=g[4], p1=g[5], p2=g[6], ph=g[7], ps1=g[8], ps2=g[9])
        elif m := re.match(r"count: ([\d,]+) cards ; by hand, ([\d,]+) tally marks .*?(\d+) questions\).*? ; males ([\d,]+), females ([\d,]+) ; native ([\d,]+), foreign-born ([\d,]+)$", ln):
            g = m.groups()
            d["count"] = dict(n=g[0], marks=g[1], q=g[2], m=g[3], f=g[4], nat=g[5], frn=g[6])
        elif m := re.match(r"combine: .*? native males aged 20 to 29: ([\d,]+) ; foreign-born females aged 60 to 69: ([\d,]+) ; .*? would read ([\d,]+) cards instead of ([\d,]+)$", ln):
            d["comb"] = dict(nm20=m.group(1), ff60=m.group(2), sep=m.group(3), one=m.group(4))
        elif m := re.match(r"sort: dropping the cards into 6 drawers by region: (.+?) ; one drawer .*? ; sorting ([\d,]+) shuffled cards .*?: (\d+) passes, ([\d,]+) card handlings ; a comparison sort needs about ([\d,]+) comparisons$", ln):
            d["sort"] = dict(drawers=m.group(1).split(", "), n=m.group(2), passes=m.group(3), handlings=m.group(4), comps=m.group(5))
        elif m := re.match(r"circle: .*?: \{(.+?)\} ; at 80 cards a minute, one clerk feeds ([\d,]+) cards in ([\d,]+) minutes \(([\d,]+) hours\) per pass$", ln):
            d["circ"] = dict(groups=re.findall(r"([a-z -]+)=(\d+)", m.group(1)), n=m.group(2), minutes=m.group(3), hours=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def press_diagram(d):
    D = Diagram(1000, 250, "One card through Hollerith's press: a hole lets a pin reach the mercury, and a dial moves on")
    W, H = 220, 116
    boxes = [("c", "A punched card", ["one person", "a hole per answer", "e.g. male, native, 20–29"], "ink"),
             ("p", "The press", ["pins come down on the card", "a hole lets a pin through", "into a cup of mercury"], "ink"),
             ("r", "Circuits and relays", ["each closed circuit", "advances a dial by one", "relays need several holes"], "ink"),
             ("t", "Dials and drawer", ["40 dials counted at once", "a bell for each card", "the table names a drawer"], "red")]
    for i, (k, t, sub, col) in enumerate(boxes):
        D.node(k, 20 + i * 245, 50, W, H, [(t, "title")] + [(s, "combo" if j == 1 else "note") for j, s in enumerate(sub)], color=col)
        if i:
            D.edge(boxes[i - 1][0], k, ports=("right", "left"))
    D.text(20, 30, "THE CARD IS READ BY ELECTRICITY, NOT BY EYE", "tag")
    D.text(20, 210, "After the US Census Bureau's description of the 1890 machine and Hollerith's own article of 1889.", "caption")
    return D


HT_HTML = """
<div class="board ht-board">
  <div style="min-width:0">
    <div class="eyebrow">Punch a card</div>
    <div class="ht-card" id="ht-card"></div>
    <div class="controls">
      <button type="button" id="ht-feed">Feed this card</button>
      <button type="button" id="ht-feed100">Feed 100 random cards</button>
      <button type="button" id="ht-reset">Clear the dials</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">The dials</div>
    <div class="ht-dials" id="ht-dials"></div>
    <p class="say" id="ht-say" aria-live="polite"></p>
  </div>
</div>
"""

HT_CSS = """
.ht-card{display:grid;gap:6px;background:var(--paper);border:1px solid var(--axis);padding:10px;margin:6px 0 10px}
.ht-card .row{display:flex;flex-wrap:wrap;align-items:center;gap:5px;font-size:12.5px}
.ht-card .row span.l{width:6.5em;color:var(--muted)}
.ht-card button{font-family:var(--mono);font-size:11.5px;padding:4px 6px;border:1px solid var(--axis);background:var(--surface);color:var(--ink);border-radius:10px;cursor:pointer}
.ht-card button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.ht-board .controls{flex-wrap:wrap}
.ht-dials{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px;margin:6px 0 10px}
.ht-dials div{border:1px solid var(--axis);padding:5px;font-size:11px;text-align:center;background:var(--surface);line-height:1.3}
.ht-dials div b{display:block;font-family:var(--mono);font-size:15px}
.ht-dials div.hot{border-color:var(--red);color:var(--red)}
.ht-board .say{font-size:14.5px}
"""

HT_JS = r"""
(() => {
  const card = document.getElementById("ht-card");
  if (!card) return;
  const F = [["sex", ["male", "female"]], ["born", ["native", "abroad"]], ["age", ["0–9", "10–19", "20–29", "30–39", "40–49", "50–59", "60–69", "70–79", "80–89", "90+"]]];
  let sel = [0, 0, 2];
  const dial = new Array(40).fill(0);
  let fed = 0, hot = -1;
  function drawCard() {
    card.innerHTML = "";
    F.forEach(([name, opts], f) => {
      const row = el("div", { class: "row" }, card); el("span", { class: "l" }, row, name);
      opts.forEach((o, i) => { const b = el("button", { type: "button", class: sel[f] === i ? "on" : "" }, row, o); b.addEventListener("click", () => { sel[f] = i; drawCard(); }); });
    });
  }
  const idx = s => (s[0] * 2 + s[1]) * 10 + s[2];
  function drawDials() {
    const host = document.getElementById("ht-dials"); host.innerHTML = "";
    const s = sel.slice(), pairs = [[0, 0], [0, 1], [1, 0], [1, 1]];
    pairs.forEach(([sx, nt]) => {
      const ag = s[2], i = (sx * 2 + nt) * 10 + ag;
      const t = el("div", { class: i === hot ? "hot" : "" }, host);
      t.innerHTML = `${F[0][1][sx]}, ${F[1][1][nt]}, ${F[2][1][ag]}<b>${dial[i]}</b>`;
    });
    const totals = [0, 0, 0, 0]; for (let i = 0; i < 40; i++) totals[Math.floor(i / 10)] += dial[i];
    pairs.forEach(([sx, nt], k) => { const t = el("div", {}, host); t.innerHTML = `all ${F[0][1][sx]}, ${F[1][1][nt]}<b>${totals[k]}</b>`; });
    document.getElementById("ht-say").textContent = `${fed} card${fed === 1 ? "" : "s"} fed. The 1890 machine had 40 dials: here 2 sexes × 2 birthplaces × 10 age groups = 40 combinations, each counted by a relay that closes only when all three holes are present. Showing the dials for the age group selected on the card.`;
  }
  function feed(s) { const i = idx(s); dial[i]++; fed++; hot = i; }
  document.getElementById("ht-feed").addEventListener("click", () => { feed(sel); drawDials(); });
  document.getElementById("ht-feed100").addEventListener("click", () => { for (let k = 0; k < 100; k++) feed([Math.random() < 0.5 ? 0 : 1, Math.random() < 0.15 ? 1 : 0, Math.min(9, Math.floor(Math.abs(Math.random() + Math.random() + Math.random() - 1.5) * 4))]); hot = -1; drawDials(); });
  document.getElementById("ht-reset").addEventListener("click", () => { dial.fill(0); fed = 0; hot = -1; drawDials(); });
  card.addEventListener("click", () => setTimeout(drawDials, 0));
  drawCard(); drawDials();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Hollerith's tabulator combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "tal": (20, 20, "Tally marks", "one mark per thing counted", "Era 1 topic 1", "ink"),
        "jac": (395, 20, "Punched cards", "holes that control a machine", "the Jacquard loom; topic 11", "ink"),
        "ele": (770, 20, "Electric circuits", "relays and counters", "telegraphy", "ink"),
        "hol": (395, 170, "Hollerith's tabulator", "⊕ one card per person, counted by circuits", "patent 1889; census 1890", "red"),
        "dia": (20, 330, "Counting dials", "wheels that carry", "topic 3", "ink"),
        "rad": (395, 330, "Sorting by columns", "radix sort", "later card sorters", "blue"),
        "db": (770, 330, "Databases", "group by, count", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("tal", "hol", ports=("bottom", "top:0.15"))
    D.edge("jac", "hol", ports=("bottom", "top"), dashed=True)
    D.edge("ele", "hol", ports=("bottom", "top:0.85"))
    D.edge("dia", "hol", ports=("top", "bottom:0.15"))
    D.edge("hol", "rad", ports=("bottom", "top"), dashed=True)
    D.edge("hol", "db", ports=("bottom:0.9", "top:0.3"))
    D.text(20, 615, "Dashed: the link to the Jacquard loom, and from Hollerith to column-by-column sorting, are not documented in the sources opened here.", "caption")
    return D


def chain(d):
    t, c, s = d["trial"], d["count"], d["sort"]
    steps = [
        ("Census tallies by hand: a mark per person per question, then the marks counted",
         "One punched card per person, counted by electric circuits", "Hollerith, patent 1889"),
        (f"Preparing the returns for counting took the rival methods {t['p1']} and {t['p2']} hours in the trial",
         f"{t['ph']} hours with Hollerith's cards: {t['ps1']} and {t['ps2']} times faster", "1888 trial"),
        ("New questions mean counting everything again",
         "Sort the cards into drawers and count only the drawer you need", "the sorting table"),
        ("Sorting a deck completely by its numbers",
         f"One column per pass, last digit first: {s['passes']} passes for {s['n']} cards", "later sorters (radix sort)"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from tally sheets to sorted decks")
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
    t, c, cb, s, ci = d["trial"], d["count"], d["comb"], d["sort"], d["circ"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The census clerks of 1880 still counted by tally marks (Era 1, topic 1). Cards with holes had controlled looms, and were to control Babbage's engine (topic 11); counting dials went back to Pascal (topic 3); electric circuits and relays were everyday telegraph technology. Hollerith put a person on a card and let electricity read it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: Hollerith's tabulator. Blue: where counting and sorting cards led."),
        ]),
        dict(id="punch", eyebrow="Try it", title="Punch a card, feed the press", toc="Try it", blocks=[
            dict(type="p", text="Choose one person's answers on the card, then feed it: the dial for that combination of sex, birthplace and age group moves on by one, as a relay closes only when all three holes are present. Feed a hundred random cards to fill the dials faster."),
            dict(type="widget", html=HT_HTML, js=HT_JS, css=HT_CSS,
                 fallback=dict(type="diagram", name="press", diagram=press_diagram(d)),
                 note="In the interactive edition you can punch cards and feed them to forty combination dials."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A person on a card", toc="How it works", blocks=[
            dict(type="p", text="By hand, a census clerk made a tally mark in a small square for every person and every property, then added and counted the marks. Hollerith punched each person's answers as holes in one card instead. In the press, \"Pins that passed through the punch card completed an electrical circuit when contacting the mercury below\", advancing one of 40 dials (US Census Bureau)."),
            dict(type="diagram", name="press-steps", diagram=press_diagram(d)),
            dict(type="p", text=f"The program punched an invented population of {c['n']} people. By hand, {c['q']} questions mean {c['marks']} tally marks, each later counted again. The tabulator reads each card once and fills every question's dials in the same pass: males {c['m']}, females {c['f']}; native {c['nat']}, foreign-born {c['frn']}."),
            dict(type="p", text=f"Relays count combinations. With 2 sexes × 2 birthplaces × 10 age groups = 40 dials, as many as the 1890 machine had, one pass gives, for example, {cb['nm20']} native males aged 20 to 29 and {cb['ff60']} foreign-born females aged 60 to 69. Counting each combination separately would read {cb['sep']} cards instead of {cb['one']}."),
            dict(type="p", text=f"**Sorting.** After a card is read, the sorting table names a drawer. Dropping the cards by region gives drawers of {', '.join(s['drawers'])}; one drawer can then be counted again for a new question, without punching anything. Sorting the whole deck by card number, one digit column per pass and the last digit first, needs {s['passes']} passes ({s['handlings']} card handlings) for {s['n']} cards."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Record each case once, in a form a machine can read, and let the machine count it as many ways as you like. The data, not the tally, becomes the thing that is kept."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The 1888 trial in hours", toc="Measured", blocks=[
            dict(type="table", head=["1880 returns from four areas of St Louis", "Rival 1", "Rival 2", "Hollerith", "Hollerith faster by"], num=[1, 2, 3],
                 rows=[["Capturing the data (hours)", t["c1"], t["c2"], t["ch"], f"{t['cs1']}× and {t['cs2']}×"],
                       ["Preparing it for tabulation (hours)", t["p1"], t["p2"], t["ph"], f"{t['ps1']}× and {t['ps2']}×"]]),
            dict(type="p", text=f"The hours are the Census Bureau's; the ratios are the program's. Capturing the data was about twice as fast, preparing it for tabulation eight to ten times. At the documented rate of 80 cards a minute, one clerk would feed the program's {ci['n']} cards in {ci['minutes']} minutes, about {ci['hours']} hours, per pass."),
            dict(type="table", head=["Sorting " + s["n"] + " cards by a 6-digit number", "Work"], num=[], rows=[["Column by column, last digit first", f"{s['passes']} passes, {s['handlings']} card handlings"], ["A comparison sort", f"about {s['comps']} comparisons"]]),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Tally marks in small squares", toc="The evidence", blocks=[
            dict(type="p", text="Hollerith described hand tabulation as \"making tally-marks in small squares and then adding and counting such tally-marks\", and warned that without new methods the next census would be \"impossible\" \"on account of the time and expense involved\"; records become machine-readable by \"punching holes in cards or strips of paper, which perforations can then be used to control circuits\" (*An Electric Tabulating System*, April 1889). His patent, US 395,782, issued on 8 January 1889, claims \"recording separate statistical items pertaining to the individual by holes or combinations of holes punched in sheets\"."),
            dict(type="p", text="The Census Bureau's history page gives the 1888 trial hours, the mercury cups, the 40 dials, the bell and the sorting table, and \"An experienced clerk could process 80 cards per minute\". Columbia's history says the machines \"reduced a ten-year job to three months\" and saved \"five million dollars\", while noting that other sources give different timeframes (**disputed**). The work earned Hollerith a Columbia PhD in 1890. Column-by-column sorting machines came later and are not covered by the opened sources (**conjecture** as a direct descendant)."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Group by, count", toc="Full circle", blocks=[
            dict(type="p", text="A tabulator pass is what a database calls a group-by with a count: read every record once, and add one to the counter for its combination of values."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program counted its cards once more as a modern group-by on sex and birthplace: {', '.join(f'{k.strip()} {int(v):,}' for k, v in ci['groups'])}, exactly the totals of the dials. The tally marks of the first era became holes, the holes became bits, and counting became a query."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How does the press know where the holes are?", "Where there is a hole, a pin passes through into mercury and closes a circuit; where there is none, the card stops the pin."),
            ("How can one pass count \"native males aged 20 to 29\"?", "A relay closes only when the holes for male, native and 20–29 are all present, so that combination's dial moves only for such cards."),
            ("Why is sorting into drawers useful?", "A drawer can be counted again for a new question, without punching or reading the rest of the deck."),
            ("Why sort by the last digit first?", "Each pass keeps the order of the previous one within each pocket, so after the last pass (the first digit) the whole number is in order."),
            ("How many passes to sort cards numbered up to 999,999?", f"One per digit: {s['passes']}."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="An Electric Tabulating System (1889)", text="Hollerith's own account in Columbia's School of Mines Quarterly: the problem, the cards, the circuits and the sorting box.",
                 draw=C.draw_manuscript, link="https://columbia.edu/cu/computinghistory/hh/index.html", link_text="Columbia University",
                 licence="Drawn placeholder."),
            dict(title="US patent 395,782: Art of compiling statistics", text="Issued 8 January 1889: holes for statistical items, counted by electric circuits.",
                 draw=C.draw_manuscript, link="https://patents.google.com/patent/US395782", link_text="Google Patents",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "HollerithTabulator", d["checks"],
                           "every card counted once per question, the 40 relay combinations against separate counts, a drawer recounted, a million shuffled cards sorted by six column passes, and the dials against a group-by. The population is invented test data.",
                           ["record Card("]),
    ]
    return dict(
        title="Hollerith's Tabulator", date="1890",
        description="Era 3, topic 13 of The Algorithm Evolution Atlas: Hollerith's punched cards and electric tabulator for the 1890 US census, counting combinations with relays, sorting into drawers, and the group-by.",
        lede="The census of the young republic was taking nearly as long to count as the ten years between censuses. An engineer put each person on a card, as holes, and let electricity do the counting: where there is a hole, a pin reaches mercury, and a dial moves on.",
        fieldnote="My first entry in this record was a tally mark on a bone. Here, at the end of the third era, the tally marks have become holes in cards, read by electricity, and the cards can be counted again for questions nobody thought of when they were punched.",
        card=[("When", "Patent issued 8 January 1889; trial 1888; census of 1890"),
              ("Where", "New York and Washington"),
              ("What hurt", "Census tallies took years"),
              ("The fix", "One punched card per person, counted by circuits and sorted into drawers"),
              ("Cost", "One pass of the cards per set of questions; 80 cards a minute")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `HollerithTabulator.java`; the trial hours are the Census Bureau's.",
    )
