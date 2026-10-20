"""Era 8, topic 4: Consistent hashing. Every number is parsed from ConsistentHashing.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"grow: ([\d,]+) keys, 10 servers become 11 ; hash mod N: ([\d,]+) keys move \(([\d.]+)%\) ; circle, 100 points per server: ([\d,]+) move \(([\d.]+)%\), all to the new server ; rendezvous: ([\d,]+) move \(([\d.]+)%\), all to the new server ; a fair share for the newcomer is 1/11 = ([\d.]+)%", ln):
            d["grow"] = dict(k=m.group(1), mod=m.group(2), modp=m.group(3), ring=m.group(4), ringp=m.group(5), rv=m.group(6), rvp=m.group(7), fair=m.group(8))
        elif m := re.match(r"leave: .*? server 3 leaves: its ([\d,]+) keys \(([\d.]+)% of all\) move, every one to server (\d+)", ln):
            d["leave"] = dict(n=m.group(1), p=m.group(2), succ=m.group(3))
        elif ln.startswith("balance: "):
            d["balance"] = [dict(reps=a, avg=b, worst=c) for a, b, c in re.findall(r"([\d,]+) points? per server: busiest server carries ([\d.]+) times its fair share on average \(worst of 50: ([\d.]+)\)", ln)]
        elif m := re.match(r"spread: (\d+) servers ; (\d+) clients, each knowing a random (\d+) to (\d+) of them ; .*? circle ([\d.]+) on average \(at most (\d+)\), hash mod \(servers known\) ([\d.]+) \(at most (\d+)\)", ln):
            d["spread"] = dict(s=m.group(1), c=m.group(2), lo=m.group(3), hi=m.group(4), ring=m.group(5), ringMax=m.group(6), mod=m.group(7), modMax=m.group(8))
        elif m := re.match(r"chord: ([\d,]+) nodes .*? ; ([\d,]+) lookups from random nodes: ([\d.]+) hops on average, at most (\d+) \(log2 [\d,]+ = (\d+)\) ; hops:lookups (.*)$", ln):
            d["chord"] = dict(nodes=m.group(1), lookups=m.group(2), avg=m.group(3), max=m.group(4), log=m.group(5),
                              hist=[(int(a), int(b)) for a, b in (p.split(":") for p in m.group(6).split())])
        elif ln.startswith("widget: "):
            pts = re.search(r"points (.*?) ; keys per server: \{(.*?)\} ; gamma joins: (\d+) keys move, all to gamma \(keys ([\d,]+)\) ; cedar leaves instead: (\d+) keys move ; with hash mod 6 becoming mod 7, (\d+) of 40 keys would move", ln)
            d["widget"] = dict(points=[(p.split(":")[0], int(p.split(":")[1])) for p in pts.group(1).split()],
                               loads=dict((a.split("=")[0], int(a.split("=")[1])) for a in pts.group(2).split(", ")),
                               gamma=int(pts.group(3)), gammaKeys=[int(x) for x in pts.group(4).split(",")], cedar=int(pts.group(5)), mod=int(pts.group(6)))
    d["checks"] = C.checks(text)
    return d


def fnv1a(s):
    """The program's widget hash: 32-bit FNV-1a, then MurmurHash3's finalizer."""
    h = 0x811C9DC5
    for ch in s:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    h ^= h >> 16; h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0xC2B2AE35) & 0xFFFFFFFF
    h ^= h >> 16
    return h


NAMES = ["amber", "basil", "cedar", "delta", "ember", "fjord"]


def owner(points, h):
    after = [p for p in points if p[1] >= h]
    return min(after, key=lambda p: p[1])[0] if after else min(points, key=lambda p: p[1])[0]


# ----------------------------------------------------------------------------------------------------------------------
def ring_svg(d):
    """The widget's circle: 6 servers at 3 points each, 40 keys, each key's owner the next point clockwise."""
    pts = [(n.split("#")[0], pos) for n, pos in d["widget"]["points"]]

    def draw(t, standalone):
        o = []
        W, H = 760, 470
        cols = {"amber": t["red"], "basil": t["blue"], "cedar": t["yellow"], "delta": t["ink"], "ember": t["muted"], "fjord": t["red"]}
        dash = {"fjord": True}
        cx, cy, R = 250, 245, 175
        ang = lambda h: -math.pi / 2 + 2 * math.pi * h / 2 ** 32
        P = lambda h, r: (cx + r * math.cos(ang(h)), cy + r * math.sin(ang(h)))
        o.append(C.text(20, 26, "The circle: 6 servers at 3 points each, 40 keys; each key belongs to the next server point clockwise", t["ink"], 13, "start", 700))
        o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="{t["axis"]}" stroke-width="2"/>')
        for k in range(40):
            h = fnv1a(f"key{k}")
            own = owner(pts, h)
            x, y = P(h, R - 16)
            if dash.get(own):
                o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="{t["wash"]}" stroke="{cols[own]}" stroke-width="1.8"/>')
            else:
                o.append(C.circle(x, y, 4, cols[own]))
        for name, pos in pts:
            x1, y1 = P(pos, R - 8)
            x2, y2 = P(pos, R + 14)
            o.append(C.line(x1, y1, x2, y2, cols[name], 6 if dash.get(name) else 4))
            if dash.get(name):
                o.append(C.line(x1, y1, x2, y2, t["wash"], 2.4))
        o.append(C.text(cx, cy - 6, "2³² positions", t["muted"], 12, "middle"))
        o.append(C.text(cx, cy + 12, "clockwise from the top", t["muted"], 12, "middle"))
        lx, ly = 480, 90
        loads = d["widget"]["loads"]
        o.append(C.text(lx, ly, "server: keys it holds", t["ink"], 12.5, "start", 700))
        for i, nm in enumerate(NAMES):
            y = ly + 26 + i * 26
            o.append(C.line(lx, y - 4, lx + 22, y - 4, cols[nm], 6 if dash.get(nm) else 4))
            if dash.get(nm):
                o.append(C.line(lx, y - 4, lx + 22, y - 4, t["wash"], 2.4))
            o.append(C.text(lx + 32, y, f"{nm}: {loads.get(nm, 0)}", t["ink"], 12.5))
        o.append(C.text(lx, ly + 26 * 7 + 6, "Bars: the servers' points (fjord's hollow).", t["muted"], 12))
        o.append(C.text(lx, ly + 26 * 7 + 24, "Dots: keys, coloured by the server holding them.", t["muted"], 12))
        o.append(C.text(lx, ly + 26 * 7 + 42, "Three points each are not enough to even out", t["muted"], 12))
        o.append(C.text(lx, ly + 26 * 7 + 60, "the arcs: one server holds no key at all.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Six servers and forty keys on a hash circle", t, standalone, 0.55, 760)
    return draw


CH_HTML = """
<div class="board ch-board">
  <div style="min-width:0"><div class="ch-view" id="ch-view"></div></div>
  <div style="min-width:0">
    <div class="ch-btns"><button type="button" id="ch-gamma">gamma joins</button><button type="button" id="ch-cedar">cedar leaves</button><button type="button" id="ch-reset">The six servers</button></div>
    <div class="ch-btns"><label><input type="checkbox" id="ch-mod"> show what hash mod N would do</label></div>
    <div class="ch-stats" id="ch-stats"></div>
    <p class="say" id="ch-say" aria-live="polite"></p>
  </div>
</div>
"""

CH_CSS = """
.ch-view svg{display:block;width:100%;height:auto;background:var(--wash)}
.ch-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0;align-items:center}
.ch-btns label{font-size:13px;color:var(--ink-2);display:flex;gap:6px;align-items:center}
.ch-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
"""

CH_JS = r"""
(() => {
  const view = document.getElementById("ch-view");
  if (!view) return;
  const PROG = __PROG__;
  const COL = {amber: "var(--red)", basil: "var(--blue)", cedar: "var(--yellow)", delta: "var(--ink)", ember: "var(--muted)", fjord: "var(--red)", gamma: "var(--blue)"};
  const DASH = {fjord: "3 2", gamma: "3 2"};
  function h32(s) {
    let h = 0x811c9dc5 | 0;
    for (const ch of s) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619); }
    h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b); h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35); h ^= h >>> 16;
    return h >>> 0;
  }
  const BASE = ["amber", "basil", "cedar", "delta", "ember", "fjord"];
  const KEYS = Array.from({length: 40}, (_, k) => h32("key" + k));
  const pointsOf = names => names.flatMap(n => [0, 1, 2].map(v => [n, h32(n + "#" + v)])).sort((a, b) => a[1] - b[1]);
  const ownerOn = (pts, h) => { for (const p of pts) if (p[1] >= h) return p[0]; return pts[0][0]; };
  let servers = BASE.slice(), before = null;
  function draw(msg) {
    const pts = pointsOf(servers), own = KEYS.map(h => ownerOn(pts, h));
    const base = pointsOf(BASE), baseOwn = KEYS.map(h => ownerOn(base, h));
    const mod = document.getElementById("ch-mod").checked;
    view.innerHTML = "";
    const S = 400, cx = 200, cy = 200, R = 165, svg = sv("svg", {viewBox: `0 0 ${S} ${S}`, role: "img", "aria-label": "A hash circle"}, view);
    const ang = h => -Math.PI / 2 + 2 * Math.PI * h / 4294967296, P = (h, r) => [cx + r * Math.cos(ang(h)), cy + r * Math.sin(ang(h))];
    sv("circle", {cx, cy, r: R, fill: "none", stroke: "var(--axis)", "stroke-width": 2}, svg);
    let moved = 0;
    KEYS.forEach((h, k) => {
      const [x, y] = P(h, R - 16), changed = own[k] !== baseOwn[k];
      if (changed) moved++;
      const hollow = DASH[own[k]];
      sv("circle", {cx: x, cy: y, r: changed ? 6 : 4, fill: hollow ? "var(--wash)" : COL[own[k]], stroke: changed ? "var(--ink)" : hollow ? COL[own[k]] : "none", "stroke-width": 2}, svg);
    });
    for (const [n, h] of pts) {
      const [x1, y1] = P(h, R - 7), [x2, y2] = P(h, R + 14);
      sv("line", {x1, y1, x2, y2, stroke: COL[n], "stroke-width": DASH[n] ? 7 : 5}, svg);
      if (DASH[n]) sv("line", {x1, y1, x2, y2, stroke: "var(--wash)", "stroke-width": 3}, svg);
    }
    const st = document.getElementById("ch-stats"); st.innerHTML = "";
    el("div", {}, st, `servers: ${servers.join(", ")}`);
    const counts = {}; own.forEach(o => counts[o] = (counts[o] || 0) + 1);
    el("div", {}, st, servers.map(n => `${n} ${counts[n] || 0}`).join(" · "));
    el("div", {}, st, `keys moved since the six: ${moved} of 40 (ringed)`);
    if (mod) {
      const n0 = BASE.length, n1 = servers.length;
      const mm = KEYS.filter(h => h % n0 !== h % n1).length;
      el("div", {}, st, `hash mod ${n0} → mod ${n1}: ${n0 === n1 ? 0 : mm} of 40 would move`);
    }
    if (msg) document.getElementById("ch-say").textContent = msg;
  }
  document.getElementById("ch-gamma").addEventListener("click", () => { servers = BASE.concat(["gamma"]); draw(`gamma takes 3 points on the circle and only the keys just before them. The program: ${PROG.gamma} keys move, all to gamma.`); });
  document.getElementById("ch-cedar").addEventListener("click", () => { servers = BASE.filter(n => n !== "cedar"); draw(`cedar's keys pass to the next point clockwise; no other key moves. The program: ${PROG.cedar} keys move.`); });
  document.getElementById("ch-reset").addEventListener("click", () => { servers = BASE.slice(); draw("Six servers, three points each, forty keys."); });
  document.getElementById("ch-mod").addEventListener("change", () => draw());
  draw("Six servers, three points each, forty keys. Each key belongs to the first server point clockwise from it.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How consistent hashing combined older ideas, and where it led")
    W = 210
    nodes = {
        "hash": (20, 20, "Hashing", "spread keys evenly over buckets", "Era 5", "ink"),
        "hot": (395, 20, "Hot spots", "everyone asks one server at once", "comet impact, election night", "ink"),
        "rv": (770, 20, "Rendezvous hashing", "highest hash(key, server) wins", "1996", "ink"),
        "ch": (395, 180, "Consistent hashing", "⊕ keys and caches on one circle", "MIT, STOC 1997", "red"),
        "ak": (20, 340, "Akamai", "founded by two of the authors", "1998", "ink"),
        "chord": (770, 340, "Chord", "⊕ fingers: find a key's node in log N hops", "MIT, SIGCOMM 2001", "ink"),
        "today": (395, 490, "Today", "Dynamo, Cassandra and other stores", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("hash", "ch", ports=("bottom", "top:0.15"))
    D.edge("hot", "ch", ports=("bottom", "top"))
    D.edge("rv", "ch", ports=("bottom", "top:0.85"), label="a relative", at=0.5, dx=8, anchor="start")
    D.edge("ch", "ak", ports=("bottom:0.15", "top"))
    D.edge("ch", "chord", ports=("bottom:0.85", "top"))
    D.edge("chord", "today", ports=("bottom", "right"))
    D.edge("ch", "today", ports=("bottom", "top"))
    D.text(20, 615, "Today: the users Wikipedia lists. Rendezvous hashing was designed in 1996 and is a more general relative.", "caption")
    return D


def chain(d):
    g, b, ch = d["grow"], d["balance"], d["chord"]
    steps = [
        (f"Hash mod N: 10 servers become 11 and {g['modp']}% of the keys move",
         f"The circle: only {g['ringp']}% move, all to the newcomer (a fair share is {g['fair']}%)", "Karger and colleagues, 1997"),
        (f"One point per server leaves uneven arcs: the busiest carries {b[0]['avg']} times its share",
         f"Many points per server: with {b[-1]['reps']}, {b[-1]['avg']} times", "virtual nodes"),
        ("Who knows where the circle's points are, without a central list?",
         f"Chord's fingers: {ch['avg']} hops on average among {ch['nodes']} nodes", "Stoica and colleagues, 2001"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from hash mod N to a circle with fingers")
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
    g, lv, b, sp, ch, wg = d["grow"], d["leave"], d["balance"], d["spread"], d["chord"], d["widget"]
    # the figure and widget recompute the hashes; they must agree with the program
    for name, pos in wg["points"]:
        assert fnv1a(name) == pos, name
    grow_rows = [["hash mod N", g["mod"], g["modp"] + "%", "almost all, everywhere"],
                 ["circle, 100 points per server", g["ring"], g["ringp"] + "%", "only to the new server"],
                 ["rendezvous hashing", g["rv"], g["rvp"] + "%", "only to the new server"]]
    bal_rows = [[r["reps"], r["avg"], r["worst"]] for r in b]
    hist_rows = [[str(h), f"{n:,}"] for h, n in ch["hist"]]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Hashing (Era 5) spreads keys evenly over a fixed number of buckets. The Web's hot spots needed caches that come and go. Karger and his colleagues at MIT put the caches on the same circle of hash values as the keys, so that a change of caches moves only a few keys. Two of them founded Akamai the next year, and Chord turned the circle into a network that needs no central list. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: consistent hashing. Blue: where it is used now."),
        ]),
        dict(id="play", eyebrow="Try it", title="Add a server, take one away", toc="Try it", blocks=[
            dict(type="p", text="Six servers, each at three points on a circle of 2³² hash values (the coloured bars; fjord's and gamma's are hollow), and forty keys (dots), each belonging to the first server point clockwise from it. Let gamma join, or let cedar leave: the keys that change hands are ringed, and they are only the ones next to the change. Tick the box to see what dividing the hash by the number of servers would have moved instead. The widget computes the same hashes as the program."),
            dict(type="widget", html=CH_HTML, js=CH_JS.replace("__PROG__", json.dumps(dict(gamma=wg["gamma"], cedar=wg["cedar"]))), css=CH_CSS,
                 fallback=dict(type="table", head=["Change", "Keys that move (of 40)"], num=[1],
                               rows=[["gamma joins", str(wg["gamma"])], ["cedar leaves", str(wg["cedar"])], ["hash mod 6 → mod 7", str(wg["mod"])]]),
                 note="In the interactive edition you can add and remove servers and compare with hash mod N."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="One circle for keys and servers", toc="How it works", blocks=[
            dict(type="p", text="**Hash mod N.** server = hash(key) mod N spreads keys evenly. But a key stays put when N goes from 10 to 11 only if its hash leaves the same remainder for both, which happens for about one key in eleven: the other ten elevenths move."),
            dict(type="p", text="**The circle.** Hash every key and every server onto the same circle of numbers, and give each key to the first server point clockwise from it. A new server takes over only the keys between its point and the point before it; a server that leaves hands its keys to the next point. Nothing else moves. The 1997 paper calls this property *monotonicity*."),
            dict(type="svg", name="ring", draw=ring_svg(d), alt="Six servers and forty keys on a hash circle", width=760),
            dict(type="p", text="**Many points per server.** With one point each, the arcs between points are uneven, and so are the loads. Place every server at many points (\"virtual nodes\") and each server's share is the sum of many small arcs, which evens out."),
            dict(type="p", text="**Chord.** To find a key's server without a central list, each node of Chord keeps \"fingers\": the nodes 1, 2, 4, 8, … places ahead of it on the circle. A lookup jumps along the farthest finger that does not overshoot the key, at least halving the remaining distance each time, so it needs about log₂ N hops."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Make the assignment depend on positions, not on the number of servers. Then a change of servers is a local event: only the neighbours of the change are affected."),
        ]),
        dict(id="measured", eyebrow="Measured", title="What moves, and how even", toc="Measured", blocks=[
            dict(type="p", text=f"**Ten servers become eleven**, {g['k']} keys:"),
            dict(type="table", head=["Method", "Keys that move", "Share", "Where they go"], num=[1, 2], rows=grow_rows, hl=1),
            dict(type="p", text=f"**A server leaves** (one point per server): server 3's {lv['n']} keys ({lv['p']}% of all; an uneven arc) all moved to server {lv['succ']}, the next point clockwise, and no other key moved."),
            dict(type="p", text="**Load balance**, 10 servers and 100,000 keys, over 50 different sets of servers:"),
            dict(type="table", head=["Points per server", "Busiest server, times its fair share (average)", "Worst of 50"], num=[0, 1, 2], rows=bal_rows, hl=len(bal_rows) - 1),
            dict(type="p", text=f"**Clients that disagree.** {sp['s']} servers; {sp['c']} clients each know only a random {sp['lo']} to {sp['hi']} of them. Over all clients, one key is sent to {sp['ring']} different servers on average (at most {sp['ringMax']}) with the circle, against {sp['mod']} (at most {sp['modMax']}) with hash mod the number of servers each knows. The 1997 paper calls this the *spread*."),
            dict(type="p", text=f"**Chord**: {ch['nodes']} nodes at random places on a circle of 2³² identifiers, {ch['lookups']} lookups from random nodes: {ch['avg']} hops on average and at most {ch['max']} (log₂ {ch['nodes']} = {ch['log']})."),
            dict(type="table", head=["Hops", "Lookups"], num=[0, 1], rows=hist_rows),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Swamped servers and a circle", toc="The evidence", blocks=[
            dict(type="p", text="Karger, Lehman, Leighton, Levine, Lewin and Panigrahy (MIT Laboratory for Computer Science): \"Hot spots occur any time a large number of clients wish to simultaneously access data from a single server\", as at JPL during the Shoemaker–Levy 9 comet impact and at political sites on election night; \"a consistent hash function is one which changes minimally as the range of the function changes\", judged by balance, monotonicity, spread and load. Their construction maps buckets and items to the unit interval, each bucket at about a constant times log C points. The opened copy prints no venue; Wikipedia gives the 1997 Symposium on Theory of Computing and records that Lewin and Leighton founded Akamai in 1998, that on average only K/N keys are remapped, and that Teradata had used the technique in 1986 without the name."),
            dict(type="p", text="Stoica, Morris, Karger, Kaashoek and Balakrishnan (MIT, SIGCOMM, August 2001): \"given a key, it maps the key onto a node\", using \"a variant of consistent hashing\", with a finger table and O(log N) hops, and \"adding virtual nodes as an indirection layer can significantly improve load balance\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Hashing, made to forgive change", toc="Full circle", blocks=[
            dict(type="p", text="Era 5's hash tables assumed a fixed number of buckets; when the table grew, everything was rehashed at once. A web of caches cannot stop to rehash. MapReduce (topic 11) still sends each key to a reducer by hash mod R, because its R is fixed for one job; long-lived stores like Dynamo use the circle."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"Ten servers became eleven. Dividing by the count moved {g['modp']}% of the keys; the circle moved {g['ringp']}%, and every one of them to the newcomer."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With hash mod N, about what share of keys keeps its server when N goes from 4 to 5?", "About 1/5: a key stays only if hash mod 4 = hash mod 5, which holds for 4 of every 20 consecutive hashes."),
            ("On the circle, a server leaves. Which keys move, and where to?", "Only its own keys, each to the next server point clockwise."),
            ("Why do many points per server even out the load?", "Each server's share becomes the sum of many independent small arcs, whose total varies much less than one arc."),
            ("Chord has 1,024 nodes. Roughly how many hops should a lookup take?", "About log₂ 1024 = 10 at most; the program measured 5.86 on average."),
            ("Two clients know different sets of servers. Why does the circle keep their answers close?", "A key's owner changes only if a server near it on the circle is missing from a client's list; with hash mod N, any difference in the count changes almost every answer."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Karger and colleagues' paper (1997)", text="Consistent hashing and random trees, for relieving hot spots on the World Wide Web.",
                 draw=C.draw_manuscript, link="https://cs.brown.edu/courses/csci2950-u/f09/papers/chash97stoc.pdf", link_text="The paper (PDF, on a Brown University course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "ConsistentHashing", d["checks"],
                           "that every key that moves goes to the new server (100,000 keys, two methods), that a leaving server's keys all go to its successor, 10,000 Chord lookups ending at the right node, and the widget's circle.",
                           ["static int owner(TreeMap<Long, Integer> r, long h)"]),
    ]
    return dict(
        title="Consistent Hashing", date="1997",
        description="Era 8, topic 4 of The Algorithm Evolution Atlas: Karger and colleagues' consistent hashing (MIT, 1997), virtual nodes and Chord, with a widget that adds and removes servers on a hash circle.",
        lede="Dividing a key's hash by the number of servers spreads keys evenly, until a server joins or leaves and nearly every key moves. Karger and his colleagues put keys and servers on one circle, so that a change moves only the keys next to it.",
        fieldnote=f"I gave {g['k']} keys to ten servers and added an eleventh. Dividing by the count, {g['modp']}% of the keys had to move. On the circle, {g['ringp']}% moved, every one of them to the newcomer.",
        card=[("When", "STOC 1997; Akamai 1998; Chord 2001"),
              ("Where", "MIT Laboratory for Computer Science"),
              ("What hurt", "Hash mod N moves nearly every key when N changes"),
              ("The fix", "Keys and servers on one circle; many points per server"),
              ("Checked", f"{g['ringp']}% of keys moved, all to the new server")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `ConsistentHashing.java`.",
    )
