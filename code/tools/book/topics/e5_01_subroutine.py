"""Era 5, topic 1: the subroutine. Every number is parsed from Subroutines.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"call: the caller's word at (\d+) is LDA \d+ = (\d+) .*? JMP (\d+) enters the routine ; the routine adds (\d+) and gets (\d+) ; it stores that in its last word, (\d+), where it reads as JMP (\d+), .*?square root of 30: (\d+) ; (\d+) instructions executed$", ln):
            g = m.groups()
            d["call"] = dict(n=int(g[0]), word=int(g[1]), sub=int(g[2]), back=int(g[3]), planted=int(g[4]), exit=int(g[5]), ret=int(g[6]), root=g[7], instr=g[8])
        elif ln.startswith("trace: "):
            d["trace"] = ln[len("trace: "):].split(" | ")
        elif m := re.match(r"memory: square-root routine (\d+) words \((\d+) without the return machinery\), call sequence (\d+) words ; (.*) ; the closed subroutine saves memory from (\d+) call sites on ; each call costs (\d+) extra instructions", ln):
            rows = re.findall(r"(\d+) places?: closed (\d+) words, open (\d+)", m.group(4))
            d["mem"] = dict(sub=m.group(1), body=m.group(2), seq=m.group(3), rows=rows, cross=m.group(5), extra=m.group(6))
        elif m := re.match(r"library: three routines \(square root (\d+) words, multiply (\d+), power (\d+), which calls multiply\) ; (.*?) ; both layouts print the squares ([\d ]+), the square root of each, and 2\^10 = (\d+)$", ln):
            lays = re.findall(r"square root at (\d+), multiply at (\d+), power at (\d+): first word of the loop in multiply is (\d+)", m.group(4))
            d["lib"] = dict(sq=m.group(1), mul=m.group(2), pow=m.group(3), lays=lays, squares=m.group(5).split(), p210=m.group(6))
        elif m := re.match(r"roots: .* every number from 1 to (\d+)$", ln):
            d["roots"] = m.group(1)
        elif m := re.match(r"wheeler: .*? the same exit word, (\d+), so after the innermost return the word holds JMP (\d+), .*? stopped after ([\d,]+) instructions without finishing \(R had reached ([\d,]+)\)$", ln):
            d["wh"] = dict(exit=m.group(1), jmp=m.group(2), limit=m.group(3), r=m.group(4))
        elif m := re.match(r"stack: .*? correct for every k from 0 to (\d+) ; SUM\(100\) = 5050 took ([\d,]+) instructions and a stack (\d+) deep$", ln):
            d["st"] = dict(k=m.group(1), instr=m.group(2), depth=m.group(3))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def call_svg(d):
    c = d["call"]

    def draw(t, standalone):
        o = []
        bx, rx, w, h = 20, 410, 300, 30
        o.append(C.text(bx, 24, "the caller", t["ink"], 14, "start", 700))
        o.append(C.text(rx, 24, "the square-root routine", t["ink"], 14, "start", 700))
        caller = [(c["n"] - 2, "LDA X", "the number"), (c["n"] - 1, "STA P", "into the parameter word"),
                  (c["n"], f"LDA {c['n']}", "load my own word"), (c["n"] + 1, f"JMP {c['sub']}", "enter the routine"),
                  (c["n"] + 2, "OUT R", "the answer comes back here")]
        for i, (a, ins, note) in enumerate(caller):
            y = 40 + i * (h + 8)
            hot = a == c["n"]
            o.append(C.rect(bx, y, w, h, t["wash"] if hot else t["surface"], t["red"] if hot else t["rule"], 1.5, 4))
            o.append(C.text(bx + 8, y + 20, str(a), t["muted"], 12))
            o.append(C.text(bx + 48, y + 20, ins, t["ink"], 14, "start", 700))
            o.append(C.text(bx + 120, y + 20, note, t["muted"], 11))
        sub = [(c["sub"], "ADD BACK", f"acc {c['word']} + {c['back']} = {c['planted']}"),
               (c["sub"] + 1, f"STA {c['exit']}", "plant the way home"),
               (None, "...", "subtract 1, 3, 5, ... while possible"),
               (c["exit"], f"JMP {c['ret']}", f"was empty; now {c['planted']}")]
        for i, (a, ins, note) in enumerate(sub):
            y = 40 + i * (h + 8) + (0 if i < 3 else 38)
            hot = a == c["exit"]
            o.append(C.rect(rx, y, w + 30, h, t["wash"] if hot else t["surface"], t["blue"] if hot else t["rule"], 1.5, 4))
            o.append(C.text(rx + 8, y + 20, "" if a is None else str(a), t["muted"], 12))
            o.append(C.text(rx + 48, y + 20, ins, t["blue"] if hot else t["ink"], 14, "start", 700))
            o.append(C.text(rx + 145, y + 20, note, t["muted"], 11))
        y_call = 40 + 3 * (h + 8) + h / 2
        y_ent = 40 + h / 2
        o.append(C.path(f"M{bx + w},{y_call} C{bx + w + 45},{y_call} {rx - 45},{y_ent} {rx},{y_ent}", t["ink2"], "none", 1.6))
        y_exit = 40 + 3 * (h + 8) + 38 + h / 2
        y_back = 40 + 4 * (h + 8) + h / 2
        o.append(C.path(f"M{rx},{y_exit} C{rx - 45},{y_exit} {bx + w + 45},{y_back} {bx + w},{y_back}", t["blue"], "none", 1.6, ";stroke-dasharray:5 4"))
        o.append(C.text(30, 260, f"Each word is operation x 1000 + address: LDA {c['n']} is {c['word']}; JMP {c['ret']} is {c['planted']}.", t["muted"], 12))
        o.append(C.text(30, 280, f"The routine adds {c['back']} to the caller's own word and stores the result as its last instruction.", t["muted"], 12))
        return C.svg_doc(760, 296, "".join(o), "The Wheeler jump: the caller loads its own word, the routine turns it into a jump back", t, standalone, 0.55, 760)
    return draw


WJ_HTML = """
<div class="board wj-board">
  <div style="min-width:0">
    <div class="eyebrow">Call from</div>
    <div class="wj-pick" id="wj-pick"></div>
    <div class="wj-cols">
      <div><div class="eyebrow">Memory: callers</div><ol class="wj-mem" id="wj-callers"></ol></div>
      <div><div class="eyebrow">Memory: routine "add one"</div><ol class="wj-mem" id="wj-sub"></ol></div>
    </div>
  </div>
  <div style="min-width:0">
    <div class="wj-regs"><span>acc <b id="wj-acc">0</b></span><span>next <b id="wj-pc">-</b></span></div>
    <div class="wj-btns"><button type="button" id="wj-step">Step</button><button type="button" id="wj-reset">Start again</button></div>
    <p class="say" id="wj-say" aria-live="polite"></p>
  </div>
</div>
"""

WJ_CSS = """
.wj-pick{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 10px}
.wj-pick button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.wj-cols{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:560px){.wj-cols{grid-template-columns:1fr}}
.wj-mem{list-style:none;margin:6px 0;padding:0;display:grid;gap:3px;font-family:var(--mono);font-size:12.5px}
.wj-mem li{display:grid;grid-template-columns:3.2em 1fr;gap:6px;padding:3px 6px;border:1px solid var(--rule);border-radius:4px;min-width:0}
.wj-mem li .a{color:var(--muted)}
.wj-mem li.now{border-color:var(--red);background:var(--wash)}
.wj-mem li.planted{border-color:var(--blue);color:var(--blue)}
.wj-regs{display:flex;gap:16px;font-family:var(--mono);margin:6px 0}
.wj-btns{display:flex;gap:8px;margin:8px 0}
"""

WJ_JS = r"""
(() => {
  const pick = document.getElementById("wj-pick");
  if (!pick) return;
  const OPS = ["HLT", "LDA", "ADD", "SUB", "STA", "JMP"];
  // two callers of the same routine; the routine adds 1 to word 90 and leaves it in word 91
  const callers = {A: 40, B: 70};
  let who = "A", mem, acc, pc, done, planted;
  function word(op, a) { return OPS.indexOf(op) * 1000 + a; }
  function load() {
    mem = {};
    const S = 200, EXIT = 205;
    for (const [k, base] of Object.entries(callers)) {
      mem[base] = word("LDA", k === "A" ? 80 : 81); mem[base + 1] = word("STA", 90);
      mem[base + 2] = word("LDA", base + 2); mem[base + 3] = word("JMP", S); mem[base + 4] = word("HLT", 0);
    }
    mem[80] = 41; mem[81] = 99; mem[89] = 5000 + 2 - 1000; mem[88] = 1;
    mem[S] = word("ADD", 89); mem[S + 1] = word("STA", EXIT); mem[S + 2] = word("LDA", 90);
    mem[S + 3] = word("ADD", 88); mem[S + 4] = word("STA", 91); mem[EXIT] = 0;
    acc = 0; pc = callers[who]; done = false; planted = false;
  }
  function show(msg) {
    const fmtW = (w, at) => { const op = Math.floor(w / 1000), a = w % 1000; return w === 0 ? (at === 205 ? "0 (empty)" : "HLT (0)") : `${OPS[op] || "?"} ${a}  (${w})`; };
    const list = (id, addrs) => {
      const ol = document.getElementById(id); ol.innerHTML = "";
      addrs.forEach(a => {
        const li = el("li", {class: (a === pc && !done ? "now " : "") + (a === 205 && planted ? "planted" : "")}, ol);
        el("span", {class: "a"}, li).textContent = a;
        el("span", {}, li).textContent = fmtW(mem[a], a);
      });
    };
    const base = callers[who];
    list("wj-callers", [base, base + 1, base + 2, base + 3, base + 4]);
    list("wj-sub", [200, 201, 202, 203, 204, 205]);
    document.getElementById("wj-acc").textContent = acc;
    document.getElementById("wj-pc").textContent = done ? "stopped" : pc;
    document.getElementById("wj-say").textContent = msg;
  }
  function step() {
    if (done) return;
    const w = mem[pc], op = Math.floor(w / 1000), a = w % 1000, at = pc;
    pc++;
    let msg = "";
    if (op === 0) { done = true; msg = `Back in the caller and stopped. Word 91 holds ${mem[91]}: the routine's answer.`; }
    else if (op === 1) { acc = mem[a]; msg = a === at ? `LDA ${a}: the caller loads its own instruction word, ${acc}. It contains the caller's address, ${at}.` : `LDA ${a}: acc = ${acc}.`; }
    else if (op === 2) { acc += mem[a]; msg = a === 89 ? `ADD 89: ${acc - mem[a]} + ${mem[a]} = ${acc}, which read as an instruction is JMP ${acc % 1000}: two words after the caller's LDA.` : `ADD ${a}: acc = ${acc}.`; }
    else if (op === 4) { mem[a] = acc; if (a === 205) planted = true; msg = a === 205 ? `STA 205: the routine plants JMP ${acc % 1000} in its own last word. Its way home is now written down.` : `STA ${a}: word ${a} = ${acc}.`; }
    else if (op === 5) { pc = a; msg = at === 205 ? `The planted jump sends the machine back to ${a}, just after the call.` : `JMP ${a}: into the routine.`; }
    show(msg);
  }
  Object.keys(callers).forEach(k => {
    const b = el("button", {type: "button", "aria-pressed": String(k === who)}, pick);
    b.textContent = `caller ${k} (at ${callers[k]})`;
    b.addEventListener("click", () => { who = k; pick.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); load(); show("Press Step to run the call one instruction at a time."); });
  });
  document.getElementById("wj-step").addEventListener("click", step);
  document.getElementById("wj-reset").addEventListener("click", () => { load(); show("Press Step to run the call one instruction at a time."); });
  load(); show("Press Step to run the call one instruction at a time. Then try the other caller: the same routine finds its own way back.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How the subroutine combined older ideas, and where it led")
    W = 210
    nodes = {
        "sp": (20, 20, "The stored program", "instructions are numbers in memory", "Era 4 topic 9", "ink"),
        "tab": (395, 20, "Printed tables", "compute once, look up many times", "Era 3", "ink"),
        "ord": (770, 20, "Initial orders", "load and place a program from tape", "credited to Wheeler", "ink"),
        "sub": (395, 170, "The closed subroutine", "⊕ the caller passes its own address", "Cambridge, 1949–1951", "red"),
        "lib": (20, 330, "A library", "88 routines on punched tape, with a catalogue", "1951", "ink"),
        "rel": (395, 330, "Relocation", "the same routine at any address", "the initial orders", "ink"),
        "stk": (770, 330, "A stack of returns", "routines may call themselves", "later", "ink"),
        "today": (395, 480, "Functions today", "libraries, calls, recursion", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("sp", "sub", ports=("bottom", "top:0.15"))
    D.edge("tab", "sub", ports=("bottom", "top"), dashed=True)
    D.edge("ord", "sub", ports=("bottom", "top:0.85"))
    D.edge("sub", "lib", ports=("bottom:0.1", "top:0.7"))
    D.edge("sub", "rel", ports=("bottom", "top"))
    D.edge("sub", "stk", ports=("bottom:0.9", "top:0.3"))
    D.edge("lib", "today", ports=("bottom:0.6", "left:0.5"))
    D.edge("stk", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: a resemblance, not a documented influence. The library count (88) is the book's; the EDSAC article counts 87.", "caption")
    return D


def chain(d):
    m, lib, st = d["mem"], d["lib"], d["st"]
    steps = [
        ("Every program wrote its own square root, its own printing, its own input",
         f"One copy, called from anywhere: from {m['cross']} call sites on, it saves memory", "Wheeler, Wilkes and Gill"),
        ("The machine has no instruction for \"go back to where you came from\"",
         f"The caller loads its own word; the routine turns it into a jump back ({m['extra']} extra instructions a call)", "the Wheeler jump"),
        ("A routine written for one address cannot be loaded at another",
         "Addresses adjusted as the routine is read in: the same tape works anywhere", "the initial orders"),
        ("A routine that calls itself overwrites its own way home",
         f"Return addresses kept on a stack: SUM(100) runs with a stack {st['depth']} deep", "later machines"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from repeated code to the call stack")
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
    c, m, lib, wh, st = d["call"], d["mem"], d["lib"], d["wh"], d["st"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. The stored-program computer (Era 4) kept instructions in memory as numbers. The Cambridge group added a way for any program to borrow a routine and come back: since the call is itself a number in memory, the caller can hand that number to the routine, and the routine can turn it into the jump home."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: the closed subroutine. Blue: functions as programmers use them today."),
        ]),
        dict(id="step", eyebrow="Try it", title="Step through a call, and watch the way home being written", toc="Try it", blocks=[
            dict(type="p", text="Two callers, at addresses 40 and 70, use the same four-instruction routine at 200. Press Step to run one instruction at a time. Watch word 205, the routine's last word: it starts empty, and the routine fills it with a jump back to whichever caller called it."),
            dict(type="widget", html=WJ_HTML, js=WJ_JS, css=WJ_CSS,
                 fallback=dict(type="svg", name="call", draw=call_svg(d), alt="The Wheeler jump: the caller loads its own word, the routine turns it into a jump back", width=760),
                 note="In the interactive edition you can step through calls from two different places."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A jump that knows its way back", toc="How it works", blocks=[
            dict(type="p", text=f"**The machine.** The program uses a small accumulator machine of its own, not the EDSAC's order code. Each instruction is one word, operation × 1000 + address: LDA 42 (load word 42) is 1042, JMP 44 (jump to 44) is 5044. Because instructions are numbers, arithmetic on them is allowed, and the Wheeler jump depends on that."),
            dict(type="p", text=f"**The call, as the program traced it.** The caller's word at {c['n']} is LDA {c['n']}: it loads *itself*, the number {c['word']}. Then JMP {c['sub']} enters the square-root routine. The routine's first instruction adds {c['back']}, giving {c['planted']}, which is the instruction JMP {c['ret']}; its second stores that in word {c['exit']}, its own last word. When the routine finishes, it runs into word {c['exit']} and jumps to {c['ret']}, the word after the call. The square root of 30 came back as {c['root']}, after {c['instr']} instructions in all."),
            dict(type="details", summary="The first six and the last three instructions of the traced call", block=dict(type="table", head=["Address: instruction → accumulator afterwards"], num=[],
                 rows=[[s.replace("... ", "… ")] for s in d["trace"]])),
            dict(type="callout", kind="key", label="Key idea",
                 text="Write a routine once and let anyone call it. The routine cannot know in advance who will call it, so the caller must tell it where to return; the Wheeler jump writes that address into the routine itself."),
            dict(type="callout", kind="wrong", label="What it cannot do",
                 text=f"A routine that calls itself stores its new return address in the same word, {wh['exit']}, wiping out the old one. The program's SUM routine, written that way, was stopped after {wh['limit']} instructions without finishing: the exit word held JMP {wh['jmp']}, a place inside the routine itself, so it kept returning to itself."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Memory saved, time spent, places to load", toc="Measured", blocks=[
            dict(type="p", text=f"The square-root routine is {m['sub']} words; without its return machinery the same code is {m['body']} words. A call takes {m['seq']} words. The program built both versions for 1 to 8 call sites and ran them on the same numbers:"),
            dict(type="table", head=["Call sites", "Closed subroutine (words)", "Code written out at each site (words)"], num=[0, 1, 2],
                 rows=[[k, cl, op] for k, cl, op in m["rows"]], hl=int(m["cross"]) - 1),
            dict(type="p", text=f"From {m['cross']} call sites on, one shared copy uses less memory, and the gap grows with every call. The price is time: each call costs {m['extra']} extra instructions (load the caller's own word, jump, build and store the return, jump back). On machines with 512 words of memory, memory was the scarcer of the two."),
            dict(type="table", head=["Layout", "Square root at", "Multiply at", "Power at", "Word 7 of multiply (LDA of its counter)"], num=[1, 2, 3, 4],
                 rows=[[f"layout {i + 1}", a, b, p, w] for i, (a, b, p, w) in enumerate(lib["lays"])]),
            dict(type="p", text=f"**Relocation.** A small library (square root {lib['sq']} words, multiply {lib['mul']}, power {lib['pow']}, which itself calls multiply) was loaded at two different sets of addresses. The loader adjusts every address inside each routine as it places it, so the same instruction becomes a different number, yet both layouts printed the same table of squares ({', '.join(lib['squares'])}), the square root of each, and 2¹⁰ = {lib['p210']}. The square-root routine was also checked against Java for every number from 1 to {d['roots']}."),
            dict(type="p", text=f"**Recursion with a stack.** With return addresses and saved values pushed onto a stack, the same SUM routine works: SUM(k) = k(k+1)/2 for every k from 0 to {st['k']}, and SUM(100) = 5050 took {st['instr']} instructions and a stack {st['depth']} deep."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Cambridge, 1949 to 1952", toc="The evidence", blocks=[
            dict(type="p", text="The EDSAC \"ran its first programs on 6 May 1949, when it calculated a table of square numbers and a list of prime numbers\"; it had 512 words of mercury delay-line memory, and \"There was no unconditional jump instruction\" (Wikipedia, EDSAC). David Wheeler \"invented the subroutine (or mark place and return) 'jump,' then called the 'Wheeler jump'\"; his dissertation \"Automatic Computing with the EDSAC\" was accepted in 1951 (IEEE Computer Society)."),
            dict(type="p", text="*The Preparation of Programs for an Electronic Digital Computer* (Wilkes, Wheeler and Gill, 1951), \"the first book on computer programming\", described a library of subroutines on punched tape with a catalogue; one article counts 88 routines, the EDSAC article 87. Wheeler's paper \"The use of sub-routines in programmes\" was read at the ACM national meeting in Pittsburgh in 1952. The mechanism of the jump \"is not capable of expressing recursion\" (Wikipedia, Wheeler Jump)."),
            dict(type="p", text="Wheeler is \"often quoted\" as saying \"All problems in computer science can be solved by another level of indirection\"; no original source was found, so the catalog marks it as conjecture."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Every call you make", toc="Full circle", blocks=[
            dict(type="p", text="Every function call in a modern program does what the Wheeler jump did, with one change: the return address goes onto a stack instead of into the routine, so a function may call itself, and many calls may be in progress at once. Libraries of tested routines, shared by programmers who never meet, began as a drawer of punched tapes in Cambridge."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The EDSAC's first program printed a table of squares. This topic's program prints one too ({', '.join(lib['squares'][:6])}, …), but by calling a multiply routine that another routine also calls, loaded wherever there was room."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            (f"The caller is at address 57. What number does LDA 57 load, and what does the routine turn it into?", "LDA 57 is 1 × 1000 + 57 = 1057. Adding 4002 gives 5059, which is JMP 59: two words after the call."),
            ("Why does the caller load its *own* word, rather than the number 57?", "Because the machine has no instruction that loads a constant: the only way to get the caller's address into the accumulator is to load a word that contains it, and the caller's own instruction does."),
            ("Three places call a 20-word routine with a 6-word call sequence. Closed or open?", "Closed: 20 + 3 × 6 = 38 words. Written out at each place, it takes at least 3 × 20 = 60. The more callers, the bigger the saving."),
            ("Why does recursion fail with the Wheeler jump?", "The return address lives in one fixed word of the routine. The inner call overwrites it, so the outer call's way home is lost."),
            ("What does a stack add?", "A fresh place for each call's return address (and its saved values), used last-in first-out: the most recent call returns first."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The Preparation of Programs for an Electronic Digital Computer (1951)", text="Wilkes, Wheeler and Gill: the first book on programming, built around the EDSAC's library of subroutines.",
                 draw=C.draw_book, link="https://en.wikipedia.org/wiki/The_Preparation_of_Programs_for_an_Electronic_Digital_Computer", link_text="Wikipedia", licence="Drawn placeholder."),
            dict(title="The EDSAC reconstruction", text="A working replica at The National Museum of Computing, Bletchley Park, filmed as it was built.",
                 draw=C.draw_manuscript, link="https://www.tnmoc.org/edsac-videos", link_text="TNMOC film record", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Subroutines", d["checks"],
                           f"the traced call and its planted return, closed against open routines at 1 to 8 call sites, a library loaded at two layouts, the square root of every number up to {d['roots']}, and recursion with and without a stack.",
                           ["static Map<String, Integer> load(Machine m"]),
    ]
    return dict(
        title="The Subroutine", date="1949–1952",
        description="Era 5, topic 1 of The Algorithm Evolution Atlas: the closed subroutine and the Wheeler jump on the EDSAC, with a library of routines and the reason recursion needed a stack.",
        lede="The first programmers wrote the same routines again and again. At Cambridge they wrote each one once and let any program call it; the only difficulty was finding the way back.",
        fieldnote=f"The caller loads its own instruction, {c['word']}, and jumps. The routine adds {c['back']} and stores the result, {c['planted']}, in its last word: a jump back to {c['ret']}. I watched one square root come home this way. Every function call on this planet still leaves a note of where to return.",
        card=[("When", "1949–1951; paper 1952"),
              ("Where", "University of Cambridge, the EDSAC"),
              ("What hurt", "Every program rewrote the same routines"),
              ("The fix", "One copy; the caller passes its own address"),
              ("Cost", f"{m['extra']} extra instructions a call; saves memory from {m['cross']} calls")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Subroutines.java`.",
    )
