"""Era 6, topic 3: objects, classes and subclasses (Simula). Every number is parsed from Objects.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("classes: "):
            d["calls"] = re.findall(r"(\w+): declared as Customer, the call reaches (\w+)\.serviceTime, mean of ([\d,]+) calls ([\d.]+)", ln)
        elif m := re.match(r"oneclerk: customers arrive at random, ([\d.]+) a minute on average ; one clerk, service (\d+) minute on average ; ([\d,]+) customers simulated: average wait in the queue ([\d.]+) minutes \(formula .*? = ([\d.]+)\), average time in the office ([\d.]+) \(formula ([\d.]+)\)", ln):
            d["one"] = dict(rate=m.group(1), svc=m.group(2), n=m.group(3), wq=m.group(4), wq_f=m.group(5), w=m.group(6), w_f=m.group(7))
        elif m := re.match(r"twoclerks: twice as many customers \(([\d.]+) a minute\) and two clerks ; average wait ([\d.]+) minutes \(Erlang's formula ([\d.]+)\) ; one queue shared by two clerks cuts the wait to (\d+)% of what two separate one-clerk offices give \(([\d.]+)\)", ln):
            d["two"] = dict(rate=m.group(1), wq=m.group(2), wq_f=m.group(3), pct=m.group(4), sep=m.group(5))
        elif m := re.match(r"mixed: (\d+)% letters \(([\d.]+) minutes on average\) and (\d+)% parcels \((\d+) minutes\), ([\d.]+) customers a minute, one clerk ; .*? ; average wait ([\d.]+) minutes \(Pollaczek-Khinchine formula ([\d.]+)\) ; the clerk is busy (\d+)% of the time, yet the parcels make the wait ([\d.]+) times what it would be if every service took exactly ([\d.]+) minutes", ln):
            d["mix"] = dict(lp=m.group(1), lt=m.group(2), pp=m.group(3), pt=m.group(4), rate=m.group(5), wq=m.group(6), pk=m.group(7),
                            busy=m.group(8), factor=m.group(9), mean=m.group(10))
        elif m := re.match(r"twin: .*? average wait ([\d.]+) and ([\d.]+), identical", ln):
            d["twin"] = dict(a=m.group(1), b=m.group(2))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def classes_svg(d):
    calls = {c[0]: c for c in d["calls"]}

    def draw(t, standalone):
        o = []
        W, H = 760, 350
        def box(x, y, w, title, lines, col):
            h = 40 + 18 * len(lines)
            o.append(C.rect(x, y, w, h, t["surface"], col, 1.8, 4))
            o.append(C.text(x + 12, y + 21, title, col, 14, "start", 700))
            o.append(C.line(x, y + 30, x + w, y + 30, col, 1))
            for i, ln in enumerate(lines):
                o.append(C.text(x + 12, y + 48 + i * 18, ln, t["ink"], 12))
        box(270, 20, 220, "class Customer", ["arrived (a time)", "serviceTime(): about 1 minute", "kind()"], t["ink"])
        box(60, 180, 230, "class Letter extends Customer", [f"serviceTime(): about {0.5} minute", "everything else inherited"], t["blue"])
        box(470, 180, 230, "class Parcel extends Customer", ["serviceTime(): about 2 minutes", "everything else inherited"], t["red"])
        for x in (175, 585):
            o.append(C.line(x, 180, 380, 124, t["ink2"], 1.5))
        o.append(C.path("M371,124 L380,114 L389,124 Z", t["ink2"], t["surface"], 1.5))
        o.append(C.text(20, 288, "The simulator holds a Customer c and calls c.serviceTime(). Which procedure runs is decided by the object's own class:", t["muted"], 12))
        rows = "  ·  ".join(f"{v[1]}.serviceTime: mean {v[3]}" for k, v in calls.items()) + f"  ({next(iter(calls.values()))[2]} calls each)"
        o.append(C.text(20, 310, rows, t["ink"], 12, "start", 700))
        o.append(C.text(20, 336, "Adding a third kind of customer means one new subclass; the simulator does not change.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Class Customer and its subclasses Letter and Parcel", t, standalone, 0.55, 760)
    return draw


OB_HTML = """
<div class="board ob-board">
  <div style="min-width:0">
    <div class="ob-plot" id="ob-plot"></div>
    <div class="ob-stats" id="ob-stats"></div>
  </div>
  <div style="min-width:0">
    <label class="ob-row">Customers per minute <input type="range" id="ob-rate" min="2" max="18" value="6"><output id="ob-rateo"></output></label>
    <label class="ob-row">Share that are parcels <input type="range" id="ob-parcel" min="0" max="100" value="20"><output id="ob-parcelo"></output></label>
    <label class="ob-row">Clerks <select id="ob-clerks"><option value="1">1</option><option value="2">2</option><option value="3">3</option></select></label>
    <p class="say" id="ob-say" aria-live="polite"></p>
  </div>
</div>
"""

OB_CSS = """
.ob-plot svg{display:block;width:100%;height:auto}
.ob-row{display:grid;gap:2px;font-size:14px;margin:6px 0}
.ob-row input,.ob-row select{width:100%;font:inherit}
.ob-row output{font:13px var(--mono);color:var(--muted)}
.ob-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

OB_JS = r"""
(() => {
  const plotBox = document.getElementById("ob-plot");
  if (!plotBox) return;
  let seed = 1967;
  const u = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return (seed + 0.5) / 2147483648; };
  const expo = m => -m * Math.log(u());
  class Customer { constructor(t) { this.arrived = t; } serviceTime() { return expo(1.0); } }
  class Letter extends Customer { serviceTime() { return expo(0.5); } }
  class Parcel extends Customer { serviceTime() { return expo(2.0); } }
  function simulate(rate, share, clerks, n) {
    seed = 1967;
    const events = [];               // [time, type, customer], kept sorted by time
    const push = e => { let i = events.length; events.push(e); while (i > 0 && events[i - 1][0] > e[0]) { events[i] = events[i - 1]; i--; } events[i] = e; };
    const queue = [], trace = [];
    let busy = 0, served = 0, arrivals = 0, wait = 0, calls = {Letter: 0, Parcel: 0}, now = 0;
    push([expo(1 / rate), 0, null]);
    while (served < n) {
      const [t, type, who] = events.shift(); now = t;
      if (type === 0) {
        const c = u() < share ? new Parcel(t) : new Letter(t);
        arrivals++;
        if (arrivals < n) push([t + expo(1 / rate), 0, null]);
        if (busy < clerks) { busy++; calls[c.constructor.name]++; push([t + c.serviceTime(), 1, c]); } else queue.push(c);
      } else {
        served++;
        if (queue.length) { const c = queue.shift(); wait += t - c.arrived; calls[c.constructor.name]++; push([t + c.serviceTime(), 1, c]); } else busy--;
      }
      if (trace.length < 400 && now < 240) trace.push([now, queue.length]);
    }
    return {wait: wait / n, trace, calls};
  }
  function update() {
    const rate = +document.getElementById("ob-rate").value / 10, share = +document.getElementById("ob-parcel").value / 100, clerks = +document.getElementById("ob-clerks").value;
    document.getElementById("ob-rateo").textContent = `${rate.toFixed(1)} a minute`;
    document.getElementById("ob-parcelo").textContent = `${Math.round(share * 100)}% parcels (about 2 minutes each), the rest letters (about 0.5)`;
    const load = rate * (share * 2 + (1 - share) * 0.5) / clerks;
    const st = document.getElementById("ob-stats"); st.innerHTML = "";
    plotBox.innerHTML = "";
    const svg = document.createElementNS(NS, "svg"); svg.setAttribute("viewBox", "0 0 520 170"); plotBox.appendChild(svg);
    const lab = sv("text", {x: 10, y: 14, "font-size": 12, fill: "var(--muted)"}, svg);
    if (load >= 1) {
      lab.textContent = "people waiting, first 4 hours";
      el("div", {}, st, `the clerks would be busy ${Math.round(load * 100)}% of the time: more than they can do`);
      document.getElementById("ob-say").textContent = "Customers arrive faster than the clerks can serve them: the queue grows without limit. Add a clerk, or slow the arrivals.";
      return;
    }
    const r = simulate(rate, share, clerks, 20000);
    const mx = Math.max(4, ...r.trace.map(p => p[1]));
    const pts = r.trace.map(([t, q]) => `${(10 + t / 240 * 500).toFixed(1)},${(160 - q / mx * 135).toFixed(1)}`).join(" ");
    sv("polyline", {points: pts, fill: "none", stroke: "var(--blue)", "stroke-width": 1.5}, svg);
    sv("line", {x1: 10, y1: 160, x2: 510, y2: 160, stroke: "var(--ink)", "stroke-width": 1}, svg);
    lab.textContent = `people waiting in the first 4 hours (most: ${mx})`;
    el("div", {}, st, `clerks busy ${Math.round(load * 100)}% of the time`);
    el("div", {}, st, `average wait over 20,000 customers: ${r.wait.toFixed(2)} minutes`);
    el("div", {}, st, `calls of Letter.serviceTime: ${fmt(r.calls.Letter)}, of Parcel.serviceTime: ${fmt(r.calls.Parcel)}`);
    document.getElementById("ob-say").textContent = load > 0.85 ? "Near full load the queue swings wildly: small changes in the arrivals make long waits." :
      "Each customer is an object; the simulator calls serviceTime() and each object answers by its own class.";
  }
  ["ob-rate", "ob-parcel", "ob-clerks"].forEach(id => document.getElementById(id).addEventListener("input", update));
  document.getElementById("ob-clerks").addEventListener("change", update);
  update();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Simula's objects combined older ideas, and where they led")
    W = 210
    nodes = {
        "blk": (20, 20, "Algol 60 blocks", "local data with its own procedures", "", "ink"),
        "sim": (395, 20, "Simulation models", "many things acting on their own", "Nygaard's simulation projects", "ink"),
        "sub": (770, 20, "The subroutine", "code written once, called from anywhere", "Era 5, topic 1", "ink"),
        "sim67": (395, 180, "Simula 67", "⊕ classes, objects and subclasses", "Dahl and Nygaard, 1967", "red"),
        "st": (20, 340, "Smalltalk", "Kay took classes, objects and references; inheritance from 1976", "", "ink"),
        "cpp": (395, 340, "C++", "Simula's classes added to C", "Stroustrup", "ink"),
        "java": (770, 340, "Java", "the language of this book's programs", "Gosling", "ink"),
        "today": (395, 490, "Today", "object-oriented programming, \"dominant in systems development\"", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("blk", "sim67", ports=("bottom", "top:0.15"))
    D.edge("sim", "sim67", ports=("bottom", "top"))
    D.edge("sub", "sim67", ports=("bottom", "top:0.85"))
    D.edge("sim67", "st", ports=("bottom:0.15", "top"))
    D.edge("sim67", "cpp", ports=("bottom", "top"))
    D.edge("sim67", "java", ports=("bottom:0.85", "top"))
    D.edge("cpp", "today", ports=("bottom", "top"))
    D.text(20, 615, "Black: the class is \"the generalisation and liberalisation of the Algol 60 block\". The IEEE Milestone names Smalltalk, C++ and Java among Simula's heirs.", "caption")
    return D


def chain(d):
    o, t, m, tw = d["one"], d["two"], d["mix"], d["twin"]
    steps = [
        ("A post office is many things acting on their own; in a program they were arrays and scattered code",
         "A class: data with its own procedures; objects made as the program runs", "Simula I and Simula 67"),
        ("Letters and parcels differ in one procedure; without objects every kind means a new case in many places",
         f"A subclass overrides serviceTime(); the simulator is unchanged, with the same result to the last digit ({tw['a']})", "virtual procedures, 1967"),
        (f"Two one-clerk offices: an average wait of {t['sep']} minutes. Is a second clerk worth it, and how?",
         f"Simulate it: one queue for two clerks cuts the wait to {t['pct']}% ({t['wq']} minutes)", "what simulation is for"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from scattered arrays to objects")
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
    o, t, m, tw = d["one"], d["two"], d["mix"], d["twin"]
    res = [["One clerk, all customers alike", o["rate"], o["wq"], o["wq_f"], "M/M/1 queue: ρ / (1 − ρ)"],
           ["Two clerks, one queue, twice the customers", t["rate"], t["wq"], t["wq_f"], "Erlang's formula"],
           [f"One clerk, {m['lp']}% letters and {m['pp']}% parcels", m["rate"], m["wq"], m["pk"], "Pollaczek and Khinchine's formula"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. An Algol 60 block already kept local data next to the procedures that use it; Dahl and Nygaard let a block outlive the call that made it, gave it a name, let the program make as many copies as it needed, and let one kind of block extend another. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Simula 67. Blue: where its ideas are today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Run a post office", toc="Try it", blocks=[
            dict(type="p", text="Simula was made for simulation, so here is one: customers arrive at random, letters take about half a minute, parcels about two, and the clerks serve them in turn. Each customer is an object of class Letter or Parcel; the simulator only ever calls serviceTime(), and each object answers by its own class. Change the arrivals, the share of parcels and the number of clerks."),
            dict(type="widget", html=OB_HTML, js=OB_JS, css=OB_CSS,
                 fallback=dict(type="table", head=["Post office", "Customers per minute", "Average wait, simulated (minutes)", "Formula", "Which formula"], num=[1, 2, 3], rows=res),
                 note="In the interactive edition you can run the post office with your own numbers."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A class, its objects, and a subclass", toc="How it works", blocks=[
            dict(type="p", text="**A class** describes one kind of thing: the data it holds and the procedures that act on it. **Objects** of the class are made while the program runs, as many as needed, each with its own data, and each lives as long as anything refers to it."),
            dict(type="p", text="**A subclass** is declared by naming its class as a prefix: it inherits everything and adds or changes what differs. A procedure declared **virtual** is looked up in the object's own class at the moment it is called, so code written for the general class works unchanged for every subclass. Java, the language of this book's programs, works the same way."),
            dict(type="svg", name="classes", draw=classes_svg(d), alt="Class Customer and its subclasses Letter and Parcel", width=760,
                 caption="The program's own classes. Every call measured here went to the subclass's procedure."),
            dict(type="p", text="**The simulation.** A list of future events, ordered by time: take the earliest, let the object concerned act (a customer arrives and queues, or a clerk finishes and calls the next), which may schedule new events, and repeat."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Put the data and the procedures of each kind of thing together, and let the program ask each thing to act for itself. A new kind of thing is then one new class, not a change in every place that handles things."),
        ]),
        dict(id="measured", eyebrow="Measured", title="A million customers", toc="Measured", blocks=[
            dict(type="p", text=f"The program simulated {o['n']} customers in each post office and compared the average wait in the queue with the formulas of queueing theory."),
            dict(type="table", head=["Post office", "Customers per minute", "Average wait, simulated (minutes)", "Formula", "Which formula"], num=[1, 2, 3], rows=res),
            dict(type="p", text=f"With one clerk the average time in the office was {o['w']} minutes (formula {o['w_f']}). One queue shared by two clerks cuts the wait to {t['pct']}% of what two separate one-clerk offices give ({t['sep']} minutes). With parcels mixed in, the clerk is busy only {m['busy']}% of the time, yet the parcels' long and variable service makes the wait {m['factor']} times what it would be if every service took exactly {m['mean']} minutes."),
            dict(type="p", text=f"**The same thing without objects.** The program also simulates the mixed post office with arrays and a switch statement, fed the same random numbers: the average waits are {tw['a']} and {tw['b']}, identical. The difference is in the code: to add a third kind of customer, the object version needs one new subclass; the plain version needs a new number, a new case in the switch, and a new branch where customers are made."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Oslo, 1961 to 1967", toc="The evidence", blocks=[
            dict(type="p", text="The IEEE Milestone dedicated at the University of Oslo in 2017 reads: \"Ole-Johan Dahl and Kristen Nygaard created the Simula programming languages in the 1960s at the Norwegian Computer Center. They introduced a new way of modeling and simulating complex tasks.\" Work began in 1961 to \"develop a description language for computer simulations\"; SIMULA introduced \"the class concept for encapsulation of data structure and code\", \"subclasses for reuse of code\" and \"late binding for flexible inheritance\"."),
            dict(type="p", text="The University of Oslo recalls that \"Kristen persuaded Ole-Johan to join him at the Norwegian Computing Center to help developing a simulation language\". Andrew Black quotes the 1967 paper \"Class and subclass declarations\": by \"using C as a prefix to another class, the latter would be taken to be a subclass of C inheriting all properties of C\"; Dahl called virtual procedures \"a last minute extension\". Dahl and Nygaard received the Turing Award \"for ideas fundamental to the emergence of object oriented programming\"; the ACM and the IEEE Milestone say 2001, the University of Oslo says 2002, and the catalog marks the year as disputed."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="From a simulation language to everything", toc="Full circle", blocks=[
            dict(type="p", text="Alan Kay \"took from Simula the ideas of classes, objects and object references\" for Smalltalk, whose first version, Smalltalk-72, \"did not include inheritance\"; Smalltalk-76 added \"a Simula-like inheritance scheme\" (Black). Through Smalltalk, C++ and Java, the Milestone says, object-oriented programming became \"dominant in systems development\". Every program in this book is written in classes, because Java is one of Simula's descendants."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"A language invented to simulate post offices and harbours, used here for what it was made for: {o['n']} customers, letters and parcels, each an object."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("A variable is declared as Customer but holds a Parcel. Which serviceTime() runs?", "Parcel's: a virtual procedure is chosen by the object's own class when it is called."),
            ("Why does the plain version need a change \"where customers are made\" for a new kind?", "It must store a new kind number for each new customer, and every switch on that number must learn it too."),
            ("With one clerk and customers arriving 0.8 a minute, service 1 minute, how busy is the clerk?", "80% of the time: 0.8 customers a minute × 1 minute each."),
            ("Why does a second clerk sharing one queue help more than splitting customers into two queues?", "With one queue no clerk sits idle while someone waits in the other line."),
            ("What does \"subclass by prefixing\" mean?", "Writing the class's name in front of a new class declaration: the new class inherits all the old one's data and procedures."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="IEEE Milestone: Object-Oriented Programming, 1961–1967", text="Plaque dedicated on 27 September 2017 at the University of Oslo, Gaustadalléen 23B.",
                 draw=C.draw_book, link="https://ethw.org/Milestones:Object-Oriented_Programming,_1961-1967", link_text="Engineering and Technology History Wiki", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Objects", d["checks"],
                           "that each call reaches its subclass's procedure, the simulated waits for one clerk, two clerks and a mix of letters and parcels against the formulas of queueing theory (within 5%), and that the version without objects gives identical results.",
                           ["static class Customer {", "static class Parcel extends Customer {"]),
    ]
    return dict(
        title="Objects, Classes and Subclasses", date="1961–1967",
        description="Era 6, topic 3 of The Algorithm Evolution Atlas: Dahl and Nygaard's Simula, classes, objects, subclasses and virtual procedures, shown in a simulated post office.",
        lede="Simula was built to simulate harbours and post offices, places made of many things that act on their own. Its answer was to let the program be made of such things: classes, objects and subclasses.",
        fieldnote=f"I simulated {o['n']} customers in a post office written the way Dahl and Nygaard proposed, and again without objects. The answers agreed to six decimal places; the difference was in how much of the program a new kind of customer would disturb.",
        card=[("When", "1961–1967 (Simula 67)"),
              ("Where", "Norwegian Computing Center, Oslo"),
              ("What hurt", "Models of many interacting things were hard to write and to change"),
              ("The fix", "Classes, objects, subclasses, virtual procedures"),
              ("Heirs", "Smalltalk, C++, Java")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Objects.java`.",
    )
