"""Era 3, topic 3: the carry, mechanized. Every number is parsed from MechanicalCarry.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"count: .*?: ([\d,]+) carries in all ; (.+?) ; then 999,999 \+ 1 sets off a chain through all (\d+) wheels$", ln):
            d["count"] = dict(total=m.group(1), wheels=m.group(3),
                              chains=[(int(k), v) for k, v in re.findall(r"(\d) carr(?:y|ies): ([\d,]+) times", m.group(2))])
        elif m := re.match(r"column: adding a column of ([\d,]+) five-digit figures on eight wheels: total ([\d,]+) ; ([\d,]+) carries \(([\d.]+) per figure\) ; longest chain (\d+)$", ln):
            d["col"] = dict(rows=m.group(1), total=m.group(2), carries=m.group(3), per=m.group(4), longest=m.group(5))
        elif m := re.match(r"subtract: (\d+) - (\d+) on six wheels: enter the nines' complement (\d+), add \d+ to get (\d+), read its complement (\d+) = (\d+) ; checked on ([\d,]+) random pairs$", ln):
            d["sub"] = dict(a=m.group(1), b=m.group(2), ca=m.group(3), mid=m.group(4), comp=m.group(5), res=m.group(6), n=m.group(7))
        elif m := re.match(r"leibniz: (\d+) x (\d+) = (\d+) in (\d+) turns of the crank and (\d+) shifts .*?would take ([\d,]+) turns\) ; (\d+) / (\d+) = (\d+) remainder (\d+) in (\d+) turns and (\d+) shifts$", ln):
            g = m.groups()
            d["lz"] = dict(x=g[0], y=g[1], p=g[2], turns=g[3], shifts=g[4], naive=g[5], a=g[6], b=g[7], q=g[8], r=g[9], dturns=g[10], dshifts=g[11])
        elif m := re.match(r"leibniz survey: ([\d,]+) random products .*?: on average ([\d.]+) crank turns per product, against ([\d,]+) additions", ln):
            d["lzs"] = dict(n=m.group(1), turns=m.group(2), naive=m.group(3))
        elif m := re.match(r"binary: ([\d,]+) random 64-bit additions .*? averages ([\d.]+) bits \(median (\d+), the largest seen (\d+)\)", ln):
            d["bin"] = dict(n=m.group(1), avg=m.group(2), median=m.group(3), max=m.group(4))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def wheels_diagram(d):
    """999,999 + 1: the carry travels through every wheel."""
    D = Diagram(1000, 240, "999,999 + 1 on a six-wheel adding machine: one carry sets off the next, wheel by wheel")
    W, H = 128, 90
    for i in range(6):
        D.node(f"w{i}", 20 + i * 160, 60, W, H, [(f"wheel {6 - i}", "note"), ("9 → 0", "title"), ("carry ←" if i else "carry out ←", "note")],
               color="red" if i == 5 else "ink")
    for i in range(5, 0, -1):
        D.edge(f"w{i}", f"w{i - 1}", ports=("left", "right"))
    D.text(20, 36, "PASCAL'S SAUTOIR DROPS EACH CARRY BY GRAVITY, ONE WHEEL AFTER ANOTHER; SCHICKARD'S GEARS HAD TO TURN THEM ALL AT ONCE", "tag")
    c = d["count"]
    D.text(20, 190, f"Counting from 1 to 999,999 makes {c['total']} carries, but a chain through five wheels happens only "
                    f"{next(v for k, v in c['chains'] if k == 5)} times.", "caption")
    D.text(20, 210, "Red: the units wheel, where the 1 is added. Numbers from MechanicalCarry.java.", "caption")
    return D


MC_HTML = """
<div class="board mc-board">
  <div style="min-width:0">
    <div class="mc-wheels" id="mc-wheels" aria-label="Six number wheels"></div>
    <div class="controls">
      <button type="button" id="mc-one">+ 1</button>
      <label for="mc-n">add <input id="mc-n" type="number" min="0" max="999999" value="1"></label>
      <button type="button" id="mc-add">Add</button>
      <button type="button" id="mc-set">999,999</button>
      <button type="button" id="mc-clear">Clear</button>
    </div>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">Carries</div>
    <div class="mc-stats" id="mc-stats"></div>
    <p class="say" id="mc-say" aria-live="polite"></p>
    <div class="eyebrow">Subtract without turning backwards</div>
    <div class="controls">
      <label for="mc-a">a <input id="mc-a" type="number" min="0" max="999999" value="4567"></label>
      <label for="mc-b">b <input id="mc-b" type="number" min="0" max="999999" value="1234"></label>
    </div>
    <ol class="mc-steps" id="mc-sub"></ol>
  </div>
</div>
"""

MC_CSS = """
.mc-wheels{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:8px;margin:6px 0 12px}
.mc-wheel{border:2px solid var(--ink-2);border-radius:50%;aspect-ratio:1;display:grid;place-items:center;font-family:var(--mono);font-size:clamp(18px,4.5vw,30px);background:var(--surface);transition:background .15s}
.mc-wheel.hot{background:var(--red);color:var(--on-red);border-color:var(--red)}
.mc-board .controls{flex-wrap:wrap}
.mc-board input[type=number]{width:7.5em}
.mc-stats{font-family:var(--mono);font-size:13px;line-height:1.7;margin:4px 0 8px}
.mc-steps{margin:6px 0 4px;padding-left:1.4em;font-size:13.5px;display:grid;gap:5px}
.mc-steps .m{font-family:var(--mono);font-size:12.5px}
.mc-board .say{font-size:14.5px}
"""

MC_JS = r"""
(() => {
  const host = document.getElementById("mc-wheels");
  if (!host) return;
  const N = 6, w = new Array(N).fill(0), els = [];
  for (let i = N - 1; i >= 0; i--) els[i] = el("div", { class: "mc-wheel" }, host, "0");
  let carries = 0, longest = 0, last = 0, busy = false;
  const draw = () => { for (let i = 0; i < N; i++) els[i].textContent = w[i]; };
  const stats = () => {
    document.getElementById("mc-stats").innerHTML = `value <b>${Number(w.slice().reverse().join("")).toLocaleString("en-US")}</b><br>carries so far ${carries}<br>longest chain ${longest}<br>last chain ${last}`;
  };
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  async function addAt(i, dgt) {
    let chain = 0;
    w[i] += dgt;
    while (i < N && w[i] >= 10) {
      w[i] -= 10; carries++; chain++;
      els[i].classList.add("hot"); draw(); await sleep(170); els[i].classList.remove("hot");
      i++;
      if (i < N) w[i] += 1;
    }
    draw();
    return chain;
  }
  async function add(x) {
    if (busy) return; busy = true;
    let mx = 0;
    for (let i = 0; i < N && x > 0; i++, x = Math.floor(x / 10)) mx = Math.max(mx, await addAt(i, x % 10));
    last = mx; longest = Math.max(longest, mx); stats();
    document.getElementById("mc-say").textContent = mx === 0 ? "No wheel passed 9: no carry." :
      mx >= N ? "The carry ran off the last wheel: the machine has overflowed and shows 0." :
      `A chain of ${mx} carr${mx === 1 ? "y" : "ies"}: each wheel passing 9 dropped a carry onto the next.`;
    busy = false;
  }
  document.getElementById("mc-one").addEventListener("click", () => add(1));
  document.getElementById("mc-add").addEventListener("click", () => add(Math.max(0, Math.min(999999, Math.round(+document.getElementById("mc-n").value || 0)))));
  document.getElementById("mc-set").addEventListener("click", () => { if (busy) return; for (let i = 0; i < N; i++) w[i] = 9; draw(); stats(); document.getElementById("mc-say").textContent = "Now press + 1."; });
  document.getElementById("mc-clear").addEventListener("click", () => { if (busy) return; w.fill(0); carries = longest = last = 0; draw(); stats(); document.getElementById("mc-say").textContent = ""; });
  const pad = v => String(v).padStart(6, "0");
  function sub() {
    let a = Math.round(+document.getElementById("mc-a").value || 0), b = Math.round(+document.getElementById("mc-b").value || 0);
    a = Math.max(0, Math.min(999999, a)); b = Math.max(0, Math.min(999999, b));
    const ol = document.getElementById("mc-sub"); ol.innerHTML = "";
    const li = h => { el("li", {}, ol).innerHTML = h; };
    const ca = 999999 - a, s = (ca + b) % 1000000, r = 999999 - s;
    li(`enter the nines' complement of a: 999999 − ${a} = <span class="m">${pad(ca)}</span>`);
    li(`add b, turning wheels forward only: <span class="m">${pad(ca)} + ${b} = ${pad(s)}</span>`);
    li(`read the complement: 999999 − ${pad(s)} = <span class="m">${pad(r)}</span>`);
    li(a >= b ? `a − b = <span class="m">${a - b}</span> ✓` : `b is larger than a: the wheels show ${pad(r)}, which is 1,000,000 − ${b - a}. A negative answer appears as its complement.`);
  }
  ["mc-a", "mc-b"].forEach(id => document.getElementById(id).addEventListener("input", sub));
  draw(); stats(); sub();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the mechanical carry combined older ideas, and where it went")
    W, H = 210, 86
    nodes = {
        "brd": (20, 20, "Counting boards", "ten counters become one", "Era 1 topic 6", "ink"),
        "clk": (395, 20, "Clockwork", "gear trains that count turns", "Schickard's clockmaker, Pfister", "ink"),
        "cmp": (770, 20, "Complements", "subtract by adding", "nines' complement", "ink"),
        "pas": (395, 170, "Mechanical adding machines", "⊕ wheels of ten with an automatic carry", "Schickard 1623; Pascal 1642", "red"),
        "lei": (20, 330, "Leibniz's stepped drum", "multiply by turns and shifts", "1673–1694", "ink"),
        "dif": (395, 330, "The difference engine", "columns of wheels that add", "topic 10", "ink"),
        "hol": (770, 330, "Hollerith's dials", "a counter per question", "topic 13", "ink"),
        "alu": (395, 480, "The processor's adder", "carries in binary, computed ahead", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, H, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("brd", "pas", ports=("bottom", "top:0.15"))
    D.edge("clk", "pas", ports=("bottom", "top"))
    D.edge("cmp", "pas", ports=("bottom", "top:0.85"))
    D.edge("pas", "lei", ports=("bottom:0.1", "top:0.7"))
    D.edge("pas", "dif", ports=("bottom", "top"))
    D.edge("pas", "hol", ports=("bottom:0.9", "top:0.3"))
    D.edge("dif", "alu", ports=("bottom", "top"), dashed=True)
    D.text(20, 615, "Dashed: an electronic adder reuses the idea of the carry, not the mechanism.", "caption")
    return D


def chain(d):
    lz, b = d["lz"], d["bin"]
    steps = [
        ("Columns of addition by hand, every carry a chance for error",
         "Wheels of ten: passing 9 turns the next wheel by one", "Schickard, 1623"),
        ("A long carry turns every wheel at once and strains the gears",
         "A falling weight delivers each carry in turn", "Pascal's sautoir, 1642–1645"),
        ("Wheels that turn one way cannot subtract",
         "Add the nines' complement and read the complement back", "Pascal"),
        (f"Multiplying by {lz['y']} means {lz['naive']} additions",
         f"A stepped drum and a shifting carriage: {lz['turns']} turns and {lz['shifts']} shifts", "Leibniz, 1673–1694"),
        ("A carry can ripple through every place, so the slowest addition sets the pace",
         "Compute the carries ahead, in parallel", "today's adders"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from counters to the processor's adder")
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
    c, col, sb, lz, lzs, b = d["count"], d["col"], d["sub"], d["lz"], d["lzs"], d["bin"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. On a counting board (Era 1, topic 6), ten counters in one column become one in the next, but a person has to notice. Clockmakers already built gear trains that count turns. Put a digit on every gear, and make each gear passing 9 nudge the next: the carry becomes a mechanism. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the mechanical adding machine. Blue: where the carry lives today."),
        ]),
        dict(id="machine", eyebrow="Try it", title="Turn the wheels and watch the carries", toc="Try it", blocks=[
            dict(type="p", text="Six wheels, each showing one digit. Press + 1 to count, or add any number. A wheel turns red when it passes 9 and drops a carry onto its left neighbour. Set 999,999 and press + 1 to see the longest chain. Below, subtract the way Pascal's machine had to: its wheels only turn forward."),
            dict(type="widget", html=MC_HTML, js=MC_JS, css=MC_CSS,
                 fallback=dict(type="diagram", name="wheels", diagram=wheels_diagram(d)),
                 note="In the interactive edition you can turn the wheels yourself, watch each carry travel, and subtract by complements."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 3, tables and machines", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Wheels of ten, a carry, and a complement", toc="How it works", blocks=[
            dict(type="p", text="**The carry.** Each wheel has ten positions. When a wheel turns from 9 to 0, the next wheel must advance by one. Most of the time nothing happens; occasionally one carry sets off another. The program counted from 1 to 999,999 on six wheels:"),
            dict(type="table", head=["Carries set off by one step", "How often"], num=[0, 1], rows=[[str(k), v] for k, v in c["chains"]]),
            dict(type="p", text=f"{c['total']} carries in all, but only nine steps set off a chain through five wheels, and 999,999 + 1 runs through all {c['wheels']}. In Schickard's machine a single tooth on each wheel pushed the next, so a long chain made every wheel turn together, driven from the first; Pascal's sautoir is a weighted lever that falls when its wheel passes 9, delivering each carry in turn without the wheels pushing one another."),
            dict(type="diagram", name="ripple", diagram=wheels_diagram(d)),
            dict(type="p", text=f"Adding a column of {col['rows']} five-digit figures (total {col['total']}) took {col['carries']} carries, {col['per']} per figure, and the longest chain was {col['longest']} wheels."),
            dict(type="p", text=f"**Subtraction.** Pascal's wheels turn one way, so the machine can only add. The nines' complement of x is 999,999 − x. Enter the complement of a, add b, and read the complement of the result: it is a − b. For {sb['a']} − {sb['b']}: enter {sb['ca']}, add {sb['b']} to get {sb['mid']}, read its complement {sb['comp']} = **{sb['res']}**. The program checked this on {sb['n']} random pairs."),
            dict(type="p", text=f"**Multiplication.** Leibniz's stepped drum has nine teeth of different lengths; setting a digit d engages d of them, so one turn of the crank adds the whole number set on the drums. A carriage shifts the setting one place left for each digit of the multiplier. {lz['x']} × {lz['y']} takes {lz['turns']} turns and {lz['shifts']} shifts, where repeated addition would take {lz['naive']}. Division runs the same way with subtraction: {lz['a']} ÷ {lz['b']} = {lz['q']}, remainder {lz['r']}, in {lz['dturns']} turns."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Turn a rule into a mechanism, and the rule is obeyed every time. The carry, the complement and the shift are the three tricks every adding circuit since has used."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Turns against additions", toc="Measured", blocks=[
            dict(type="table", head=["Method", "Work per product of two numbers below 100,000 (average)"], num=[],
                 rows=[["Repeated addition", f"{lzs['naive']} additions"], ["Leibniz's stepped drum, with the shifting carriage", f"{lzs['turns']} turns of the crank"]]),
            dict(type="p", text=f"Over {lzs['n']} random products, the stepped drum needs the sum of the multiplier's digits in turns, never more than nine per digit: the shift turns a count of additions into a count of digits."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A fire, fifty prototypes and a wooden model", toc="The evidence", blocks=[
            dict(type="p", text="Schickard wrote to Kepler on 20 September 1623: \"What you have done by calculation I have just tried to do by way of mechanics.\" The first machine \"was destroyed in a fire while still incomplete\"; the drawings were found among Kepler's papers in the 1950s and the machine reconstructed at Tübingen (MacTutor). Wikipedia notes that the drawings had in fact been published at least once a century from 1718 (**disputed** as a rediscovery)."),
            dict(type="p", text="Pascal began in 1642, at 18, because of \"the laborious arithmetical calculations required by his father's\" work in Rouen; he built 50 prototypes, nine machines survive, and the royal privilege dates from 1649 (Wikipedia). His 18-page *Lettre dédicatoire* appeared in 1645; a machine signed in 1652 is in the Musée des Arts et Métiers, Paris (History of Information). Leibniz showed a wooden model to the Royal Society on 1 February 1673 and completed his machine in 1694; \"a design flaw in the carry mechanism\" kept it from working reliably, and the survivor is in Hanover. How many machines he built is **disputed** between Wikipedia's two articles."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="The carry is still the slow part", toc="Full circle", blocks=[
            dict(type="p", text="A processor adds in binary, but the problem is Pascal's: a carry may have to travel through every place. If each bit waits for the carry from the one before, a 64-bit addition must allow for a chain of 64."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The program added {b['n']} random pairs of 64-bit numbers bit by bit. The longest carry chain averaged {b['avg']} bits (median {b['median']}); the longest seen was {b['max']}. Long chains are rare, exactly as on Pascal's wheels, but a circuit must be ready for the worst case, so fast adders work out the carries for many places at once instead of waiting for them to ripple."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("When counting up by one, how often does the tens wheel receive a carry?", "Once every ten steps: whenever the units wheel passes from 9 to 0."),
            ("Why does C(C(a) + b) = a − b work?", "C(x) = 999,999 − x. So C(C(a) + b) = 999,999 − (999,999 − a + b) = a − b."),
            (f"How many crank turns does {lz['x']} × {lz['y']} take on Leibniz's machine?", f"The sum of the multiplier's digits: 8 + 9 + 1 + 2 = {lz['turns']}, with {lz['shifts']} shifts."),
            ("Why did Pascal use a falling weight rather than gears to carry?", "With gears, a long chain of carries makes every wheel turn at once, all driven from the first wheel; the force adds up and can damage the mechanism."),
            ("What happens when you add 1 to 999,999 on six wheels?", "Every wheel returns to 0 and the last carry falls off the end: the machine overflows."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Pascaline signed in 1652", text="Pascal's adding machine in the Musée des Arts et Métiers, Paris, as recorded by Jeremy Norman's History of Information.",
                 draw=C.draw_board, link="https://historyofinformation.com/detail.php?id=382", link_text="History of Information",
                 licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MechanicalCarry", d["checks"],
                           "every step of counting to 999,999 on six wheels, a column of 1,000 figures, nines'-complement subtraction on 100,000 pairs, 100,000 products on a simulated stepped drum, and 200,000 64-bit additions bit by bit against the processor's own.",
                           ["int addAt(", "static long[] leibnizMultiply("]),
    ]
    return dict(
        title="The Carry, Mechanized", date="1623–1694",
        description="Era 3, topic 3 of The Algorithm Evolution Atlas: Schickard's and Pascal's adding machines, subtraction by nines' complements, Leibniz's stepped drum, and the carry in today's processors.",
        lede="On a counting board the carry was a decision a person had to make. In the seventeenth century three men put it into brass: a wheel that passes 9 turns its neighbour, and the rule is obeyed every time.",
        fieldnote="What impressed me was not the arithmetic but the forgetting. A merchant with one of these boxes no longer needed to remember to carry; the box remembered for him.",
        card=[("When", "Schickard 1623; Pascal 1642–1645; Leibniz 1673–1694"),
              ("Where", "Tübingen, Rouen and Paris, London and Hanover"),
              ("What hurt", "Columns of addition, and every carry by hand"),
              ("The fix", "Wheels of ten with an automatic carry; complements; a stepped drum"),
              ("Cost", f"{lz['turns']} crank turns for {lz['x']} × {lz['y']}, against {lz['naive']} additions")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MechanicalCarry.java`.",
    )
