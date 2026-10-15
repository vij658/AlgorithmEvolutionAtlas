"""Era 6, topic 6: the relational model of data. Every number is parsed from Relational.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"tree: (\d+) suppliers, ([\d,]+) parts, ([\d,]+) shipments .*? \"which parts does supplier (\d+) send\?\" reads ([\d,]+) records, \"who sends part (\d+)\?\" reads ([\d,]+) ; turn the tree over, parts on top: the first question now reads ([\d,]+), the second ([\d,]+) ; .*? supplier \d+ sends (\d+) parts, part \d+ comes from (\d+) suppliers", ln):
            d["tree"] = dict(sup=m.group(1), parts=m.group(2), ships=m.group(3), s=m.group(4), q1=m.group(5), p=m.group(6), q2=m.group(7),
                             q1f=m.group(8), q2f=m.group(9), a1=m.group(10), a2=m.group(11))
        elif m := re.match(r"relations: .*? with no index both read all ([\d,]+) rows ; after the system adds an index on s and on p, the same two lines read (\d+) and (\d+) rows", ln):
            d["rel"] = dict(scan=m.group(1), i1=m.group(2), i2=m.group(3))
        elif m := re.match(r"join: .*? restrict supplier to Genoa \((\d+) rows\) and part to gold \((\d+) rows\), join both with supply \(([\d,]+) rows\) ; nested loops \(every pair compared\): ([\d,]+) steps ; hashing \(one table put in buckets by key\): ([\d,]+) steps ; sorting both and merging: ([\d,]+) steps ; all three find the same (\d+) suppliers", ln):
            d["join"] = dict(gen=m.group(1), gold=m.group(2), sup=m.group(3), nested=m.group(4), hash=m.group(5), merge=m.group(6), ans=m.group(7))
        elif m := re.match(r"normal: (\d+) nested employee records .*? employee\(man, born\) (\d+) rows, jobhistory\(man, jobdate, title\) (\d+), salaryhistory\(man, jobdate, saldate, salary\) (\d+), children\(man, childname, childborn\) (\d+) ; all (\d+) employees rebuilt exactly", ln):
            d["norm"] = dict(n=m.group(1), emp=m.group(2), job=m.group(3), sal=m.group(4), kids=m.group(5), rebuilt=m.group(6))
        elif m := re.match(r"once: .*? repeats supplier (\d+)'s city in (\d+) rows ; .*? saying both (\w+) and (\w+)", ln):
            d["once"] = dict(s=m.group(1), rows=m.group(2), c1=m.group(3), c2=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def normal_svg(d):
    n = d["norm"]

    def draw(t, standalone):
        o = []
        W, H = 780, 346
        o.append(C.text(20, 24, "A nested record, and the same facts in normal form", t["ink"], 13, "start", 700))
        # nested record
        o.append(C.rect(20, 40, 250, 250, t["surface"], t["ink2"], 1.4, 4))
        lines = [("employee: man#, born", 0, t["ink"]), ("job history", 1, t["blue"]), ("jobdate, title", 2, t["ink"]),
                 ("salary history", 2, t["blue"]), ("saldate, salary", 3, t["ink"]), ("saldate, salary", 3, t["ink"]),
                 ("jobdate, title", 2, t["ink"]), ("salary history …", 2, t["blue"]), ("children", 1, t["red"]),
                 ("childname, childborn", 2, t["ink"]), ("childname, childborn", 2, t["ink"])]
        for i, (txt, ind, col) in enumerate(lines):
            o.append(C.text(34 + ind * 18, 64 + i * 21, txt, col, 12, "start", 700 if col != t["ink"] else 400))
        o.append(C.path("M285,165 L325,165", t["ink2"], "none", 1.8))
        o.append(C.path("M318,159 L326,165 L318,171", t["ink2"], "none", 1.8))
        tables = [("employee", "man#, born", n["emp"], t["ink"]),
                  ("jobhistory", "man#, jobdate, title", n["job"], t["blue"]),
                  ("salaryhistory", "man#, jobdate, saldate, salary", n["sal"], t["blue"]),
                  ("children", "man#, childname, childborn", n["kids"], t["red"])]
        for i, (name, cols, rows, col) in enumerate(tables):
            y = 40 + i * 64
            o.append(C.rect(340, y, 420, 52, t["surface"], col, 1.6, 4))
            o.append(C.text(352, y + 21, name, col, 13, "start", 700))
            o.append(C.text(352, y + 41, f"({cols})", t["ink"], 12))
            o.append(C.text(748, y + 21, f"{rows} rows", t["muted"], 12, "end"))
        o.append(C.text(20, 316, "Each parent's key (man#, and for salaries also jobdate) is copied into its children.", t["muted"], 12))
        o.append(C.text(20, 334, f"The program flattened {n['n']} employees this way and rebuilt all {n['rebuilt']} exactly from the four tables.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A nested record and its normal form", t, standalone, 0.55, 780)
    return draw


RL_HTML = """
<div class="board rl-board">
  <div style="min-width:0">
    <div class="rl-tables" id="rl-tables"></div>
  </div>
  <div style="min-width:0">
    <label class="rl-row">Question <select id="rl-q">
      <option value="q1">Which parts does supplier S3 send?</option>
      <option value="q2">Who sends part P5?</option>
      <option value="q3">Which suppliers in Genoa send a gold part?</option></select></label>
    <label class="rl-row">How the data are stored <select id="rl-st">
      <option value="ts">A tree, suppliers on top</option>
      <option value="tp">A tree, parts on top</option>
      <option value="rn">Tables (relations), no index</option>
      <option value="ri">Tables, with indexes</option></select></label>
    <div class="rl-stats" id="rl-stats"></div>
    <p class="say" id="rl-say" aria-live="polite"></p>
  </div>
</div>
"""

RL_CSS = """
.rl-tables{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;font:12px var(--mono)}
.rl-tables table{border-collapse:collapse;width:100%}
.rl-tables caption{font-weight:700;text-align:left;padding-bottom:3px}
.rl-tables td,.rl-tables th{border:1px solid var(--rule);padding:1px 3px;text-align:left}
.rl-tables tr.hit td{background:var(--blue);color:var(--on-blue)}
.rl-tables tr.read td{background:var(--wash)}
.rl-row{display:grid;gap:2px;font-size:14px;margin:6px 0}
.rl-row select{width:100%;font:inherit}
.rl-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
@media (max-width:560px){.rl-tables{grid-template-columns:1fr 1fr}}
"""

RL_JS = r"""
(() => {
  const tb = document.getElementById("rl-tables");
  if (!tb) return;
  const cities = ["Genoa", "Bergen", "Cork"], colors = ["red", "gold", "blue"];
  const supplier = [["S1", "Genoa"], ["S2", "Bergen"], ["S3", "Genoa"], ["S4", "Cork"], ["S5", "Bergen"]];
  const part = [["P1", "red"], ["P2", "blue"], ["P3", "gold"], ["P4", "red"], ["P5", "gold"], ["P6", "blue"]];
  const supply = [["S1", "P1"], ["S1", "P3"], ["S2", "P5"], ["S2", "P2"], ["S3", "P1"], ["S3", "P4"], ["S3", "P5"], ["S4", "P5"], ["S4", "P6"], ["S5", "P2"], ["S5", "P3"], ["S1", "P6"]];
  function render(hits, reads) {
    tb.innerHTML = "";
    const draw = (name, head, rows, key) => {
      const t = el("table", {}, tb); el("caption", {}, t, name);
      const hr = el("tr", {}, t); head.forEach(h => el("th", {}, hr, h));
      rows.forEach((r, i) => { const tr = el("tr", {class: hits.has(key + i) ? "hit" : reads.has(key + i) ? "read" : ""}, t); r.forEach(c => el("td", {}, tr, c)); });
    };
    draw("supplier", ["s", "city"], supplier, "s"); draw("part", ["p", "color"], part, "p"); draw("supply", ["s", "p"], supply, "y");
  }
  function run() {
    const q = document.getElementById("rl-q").value, st = document.getElementById("rl-st").value;
    const hits = new Set(), reads = new Set(); let n = 0, answer = [], note = "";
    if (q === "q3" && (st === "ts" || st === "tp")) {
      render(hits, reads);
      out(["—"], "?", "In a tree the program walks one fixed path. Combining suppliers, shipments and parts needs a new program, written for this tree.");
      return;
    }
    if (q === "q1" || q === "q2") {
      const [col, val] = q === "q1" ? [0, "S3"] : [1, "P5"];
      const grain = (q === "q1" && st === "ts") || (q === "q2" && st === "tp");
      supply.forEach((r, i) => {
        if (st === "rn" || (!grain && (st === "ts" || st === "tp"))) { reads.add("y" + i); n++; if (r[col] === val) hits.add("y" + i); }
        else if (r[col] === val) { hits.add("y" + i); n++; }
      });
      if (grain) n += 1;
      if ((st === "ts" || st === "tp") && !grain) n += st === "ts" ? supplier.length : part.length;
      answer = supply.filter(r => r[col] === val).map(r => r[1 - col]);
      note = st === "rn" ? "With no index the system reads every row; the question is still one line." :
        st === "ri" ? "The system added an index; the question did not change, but only matching rows are read." :
        grain ? "With the grain of the tree: go to the record, read its children." :
        "Against the grain: every record and every child must be read, and the program is a different one.";
    } else {
      // join: Genoa suppliers, gold parts, supply
      supplier.forEach((r, i) => { reads.add("s" + i); n++; });
      part.forEach((r, i) => { reads.add("p" + i); n++; });
      const g = new Set(supplier.filter(r => r[1] === "Genoa").map(r => r[0])), au = new Set(part.filter(r => r[1] === "gold").map(r => r[0]));
      supply.forEach((r, i) => { if (st === "rn") { reads.add("y" + i); n++; } if (g.has(r[0]) && au.has(r[1])) { hits.add("y" + i); if (st === "ri") n++; } });
      supplier.forEach((r, i) => { if (g.has(r[0]) && supply.some(y => y[0] === r[0] && au.has(y[1]))) hits.add("s" + i); });
      answer = [...new Set(supply.filter(r => g.has(r[0]) && au.has(r[1])).map(r => r[0]))];
      note = "Restrict suppliers to Genoa, parts to gold, and join both with supply: the system decides the order and the method.";
    }
    render(hits, reads);
    out(answer, n, note);
  }
  function out(ans, n, note) {
    const s = document.getElementById("rl-stats"); s.innerHTML = "";
    el("div", {}, s, `answer: ${ans.join(", ") || "none"}`);
    el("div", {}, s, `records or rows read: ${n}`);
    document.getElementById("rl-say").textContent = note;
  }
  document.getElementById("rl-q").addEventListener("change", run);
  document.getElementById("rl-st").addEventListener("change", run);
  run();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the relational model combined older ideas, and where it led")
    W = 210
    nodes = {
        "tree": (20, 20, "Trees and chains", "programs walk the links, record by record", "1960s databases", "ink"),
        "set": (395, 20, "Relations in mathematics", "a relation is a set of n-tuples", "", "ink"),
        "logic": (770, 20, "Boole's algebra of logic", "conditions that are true or false", "Era 3, topic 12", "ink"),
        "codd": (395, 180, "The relational model", "⊕ users see only tables; they say what, not how", "Codd, 1970", "red"),
        "sysr": (20, 340, "System R", "IBM's research prototype", "from 1973", "ink"),
        "sql": (395, 340, "SQL", "Chamberlin and Boyce's query language", "first called SEQUEL", "ink"),
        "bt": (770, 340, "B-trees under the tables", "indexes the user never sees", "topic 7", "ink"),
        "today": (395, 490, "Today", "relational databases, \"the standard for processing financial records\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("tree", "codd", ports=("bottom", "top:0.15"), label="the pain", at=0.5, dx=-8, anchor="end")
    D.edge("set", "codd", ports=("bottom", "top"))
    D.edge("logic", "codd", ports=("bottom", "top:0.85"))
    D.edge("codd", "sysr", ports=("bottom:0.15", "top"))
    D.edge("codd", "sql", ports=("bottom", "top"))
    D.edge("codd", "bt", ports=("bottom:0.85", "top"), dashed=True)
    D.edge("sql", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: B-trees were invented separately (topic 7) and became the usual index under relational tables. Quotes: Codd 1970; IBM History.", "caption")
    return D


def chain(d):
    t, r, j, n, o = d["tree"], d["rel"], d["join"], d["norm"], d["once"]
    steps = [
        (f"A tree with suppliers on top: \"who sends part {t['p']}?\" reads {t['q2']} records",
         f"Turn the tree over: {t['q2f']}; but now \"what does supplier {t['s']} send?\" reads {t['q1f']}", "a new program for each"),
        ("Every way of storing the data favours some questions and breaks the programs written for others",
         f"Relations: one line per question; with indexes {r['i1']} and {r['i2']} rows read", "Codd, 1970"),
        (f"Joining three tables by comparing every pair: {j['nested']} steps",
         f"The system chooses how: hashing, {j['hash']} steps", "say what, not how"),
        (f"A city stored in every shipment: change it in {o['rows']} rows or the table says both {o['c1']} and {o['c2']}",
         "Store each fact once: supplier(s, city), one row to change", "normal forms"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from walking trees to asking tables")
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
    t, r, j, n, o = d["tree"], d["rel"], d["join"], d["norm"], d["once"]
    reads = [[f"Tree, suppliers on top", t["q1"], t["q2"], "two programs"],
             [f"Tree, parts on top", t["q1f"], t["q2f"], "two more programs"],
             ["Relations, no index", r["scan"], r["scan"], "two one-line questions"],
             ["Relations, with indexes", r["i1"], r["i2"], "the same two lines"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The databases of the 1960s were trees and chains of records that programs walked link by link. Mathematics already had relations, sets of tuples, and logic already had conditions that are true or false. Codd proposed that users should see nothing but relations, and ask for what they want, never how to find it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: the relational model. Blue: where it is today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Same question, different storage", toc="Try it", blocks=[
            dict(type="p", text="A tiny supplier-and-part database, five suppliers, six parts, twelve shipments. Choose a question and a way of storing the data. Grey rows are read; blue rows are the answer. In a tree, a question against the grain reads everything; in tables, the question is the same whatever the storage, and an index only changes how much is read."),
            dict(type="widget", html=RL_HTML, js=RL_JS, css=RL_CSS,
                 fallback=dict(type="table", head=["Storage", f"\"What does supplier {t['s']} send?\": records read", f"\"Who sends part {t['p']}?\": records read", "Programs"], num=[1, 2], rows=reads, hl=3),
                 note="In the interactive edition you can ask three questions of a small database stored four ways."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Tables, and three operations on them", toc="How it works", blocks=[
            dict(type="p", text="**Relations.** A relation is a table: each row a tuple of values, the rows in no particular order, with no pointers from one row to another. The supplier-and-part data become supplier(s, city), part(p, color) and supply(s, p, qty)."),
            dict(type="p", text="**Operations on whole tables.** *Restriction* keeps the rows that satisfy a condition. *Projection* keeps some columns and drops duplicate rows. *Join* combines the rows of two tables that agree on a column. \"Which parts does supplier 7 send?\" is the projection on p of the restriction of supply to s = 7."),
            dict(type="p", text="**Normal form.** Records with lists inside them (an employee with a job history, each job with a salary history) are flattened by copying each parent's key into its children."),
            dict(type="svg", name="normal", draw=normal_svg(d), alt="A nested record and its normal form", width=780),
            dict(type="p", text="**Independence.** Because a question names only tables and columns, the system may store the rows in any order, add or drop indexes, and choose how to compute a join, without changing a single question."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Separate what is wanted from how to find it. A program that says only what it wants survives every reorganization of the data underneath it."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Records read, steps taken", toc="Measured", blocks=[
            dict(type="p", text=f"The program's database: {t['sup']} suppliers, {t['parts']} parts, {t['ships']} shipments. Supplier {t['s']} sends {t['a1']} parts; part {t['p']} comes from {t['a2']} suppliers. Every way of storing gave the same answers."),
            dict(type="table", head=["Storage", f"\"What does supplier {t['s']} send?\": records read", f"\"Who sends part {t['p']}?\": records read", "Programs"], num=[1, 2], rows=reads, hl=3),
            dict(type="p", text=f"**A join.** \"Which suppliers in Genoa send a gold part?\": restrict supplier to Genoa ({j['gen']} rows) and part to gold ({j['gold']} rows), and join both with supply ({j['sup']} rows). Three methods, the same {j['ans']} suppliers, checked against every shipment:"),
            dict(type="table", head=["Join method", "Steps"], num=[1], rows=[["Nested loops (compare every pair)", j["nested"]], ["Sort both tables and merge", j["merge"]], ["Hashing (put one table in buckets by key)", j["hash"]]], hl=2),
            dict(type="p", text=f"**Normal form.** {n['n']} nested employee records became employee ({n['emp']} rows), jobhistory ({n['job']}), salaryhistory ({n['sal']}) and children ({n['kids']}), and all {n['rebuilt']} employees were rebuilt exactly from the flat tables."),
            dict(type="p", text=f"**One fact, one place.** In a single wide table, supplier {o['s']}'s city is repeated in {o['rows']} rows. An update that changes only one of them leaves the table saying both {o['c1']} and {o['c2']}. Stored once, in supplier(s, city), the city has one row to change."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="San Jose, 1970", toc="The evidence", blocks=[
            dict(type="p", text="E. F. Codd, \"A Relational Model of Data for Large Shared Data Banks\" (IBM Research Laboratory, San Jose; *Communications of the ACM* 13(6): 377–387, June 1970), opens: \"Future users of large data banks must be protected from having to know how the data is organized in the machine.\" It names the dependences it wants to remove, \"ordering dependence, indexing dependence, and access path dependence\"; defines a relation as \"a set of ntuples\" [sic]; describes normalization from the top of a tree, taking \"its primary key\" and expanding \"each of the immediately subordinate relations\"; and offers the model as a basis for \"treating derivability, redundancy, and consistency of relations\"."),
            dict(type="p", text="IBM's history pages: Codd was \"an Oxford-educated mathematician working at the IBM San Jose Research Lab\"; \"The early databases used rigid hierarchical structures and convoluted navigational plans\"; \"A group of programmers in 1973 undertook an industrial-strength implementation: the System R project\"; Chamberlin and Boyce \"developed SQL\" (first named SEQUEL, renamed \"because of a trademark issue\", according to LearnSQL); Codd received the Turing Award in 1981. Born on the Isle of Portland in 1923, he had flown in the Royal Air Force in the Second World War and joined IBM in 1949 as a mathematical programmer."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Boole's conditions, on whole tables", toc="Full circle", blocks=[
            dict(type="p", text="A restriction keeps the rows for which a condition is true: city = Genoa and color = gold. Such conditions are Boole's algebra of logic (Era 3, topic 12), now applied to millions of rows at once. And the index under the table, which the user never sees, is usually the next topic's B-tree."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The same one-line question read {r['scan']} rows without an index and {r['i2']} with one. Nothing in the question changed."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Write \"which cities have a supplier?\" with the operations above.", "The projection of supplier on city (duplicates dropped)."),
            ("Why does a tree with suppliers on top make \"who sends part 42?\" expensive?", "Shipments are reached only through their supplier, so every supplier and every shipment must be read."),
            ("What does adding an index change, and what does it not?", "It changes how many rows are read; it does not change any question or any answer."),
            ("In normal form, which key is copied into salaryhistory?", "The employee's man# and the job's jobdate: together they say which job the salary belongs to."),
            ("Why can repeating a fact in many rows lead to a contradiction?", "An update may change some copies and miss others."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Relational Model of Data for Large Shared Data Banks (1970)", text="Codd's paper, *Communications of the ACM* 13(6): 377–387.",
                 draw=C.draw_manuscript, link="https://cs-people.bu.edu/mathan/reading-groups/papers-classics/codd.pdf", link_text="The paper (PDF, on a Boston University page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Relational", d["checks"],
                           "the same two questions on two trees and on tables with and without indexes, a three-table join by three methods against a check of every shipment, nested records flattened and rebuilt exactly, and a contradiction made by a careless update.",
                           ["Relation where(String c, int v)", "static List<int[]> join(List<int[]> R, int a, List<int[]> S, int b, String method)"]),
    ]
    return dict(
        title="The Relational Model of Data", date="1970",
        description="Era 6, topic 6 of The Algorithm Evolution Atlas: Codd's relations, restriction, projection and join, normal form, and why questions should say what and not how.",
        lede="The databases of the 1960s were trees and chains that programs walked one link at a time; change the storage and the programs broke. Codd proposed that users see only tables, and ask for what they want.",
        fieldnote=f"Asked of a tree against its grain, \"who sends part {t['p']}?\" cost {t['q2']} reads. Asked of tables with an index, the same question, written once, cost {r['i2']}. The storage changed; the question did not.",
        card=[("When", "1970"),
              ("Where", "IBM Research Laboratory, San Jose"),
              ("What hurt", "Programs depended on how the data were stored"),
              ("The fix", "Relations, and operations on whole tables"),
              ("Measured", f"{r['i2']} rows read instead of {t['q2']}, same answer")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Relational.java`.",
    )
