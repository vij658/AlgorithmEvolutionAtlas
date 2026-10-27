"""Era 8, topic 13: Bitcoin's proof-of-work ledger. Every number is parsed from Bitcoin.java's output."""
import json
import math
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if ln.startswith("genesis: "):
            m = re.search(r"header ([0-9a-f]+) \(80 bytes: version (\d+), previous hash zero, Merkle root, time (\d+), bits (0x[0-9a-f]+), nonce (\d+)\) ; SHA-256 twice, bytes reversed: ([0-9a-f]+), the published hash ; (\d+) leading zero bits ; target (.*?) = 2\^(\d+) x ([\d.]+), so about 2\^(\d+) = ([\d,]+) tries", ln)
            d["gen"] = dict(header=m.group(1), version=m.group(2), time=m.group(3), bits=m.group(4), nonce=m.group(5), hash=m.group(6), zeros=m.group(7),
                            target=m.group(8), texp=m.group(9), tman=m.group(10), tries_exp=m.group(11), tries=m.group(12))
        elif ln.startswith("mining: "):
            d["mining"] = re.findall(r"(\d+) zero bits: (\d+) blocks, ([\d,]+) tries per block on average \(2\^\d+ = ([\d,]+)\)", ln)
        elif ln.startswith("tamper: "):
            m = re.search(r"a chain of (\d+) blocks at (\d+) zero bits ; one payment in block (\d+) changed ; .*? ; the old nonce (no longer gives|still gives \(by luck\)) .*? ; re-mining blocks (\d+) to (\d+) took ([\d,]+) tries \(about (\d+) x 2\^\d+ = ([\d,]+)\)", ln)
            d["tamper"] = dict(len=m.group(1), bits=m.group(2), block=m.group(3), old=m.group(4), a=m.group(5), b=m.group(6), tries=m.group(7), k=m.group(8), expect=m.group(9))
        elif ln.startswith("section11: "):
            m = re.search(r"q = 0.1, z:P ([\d:. ]+) ; q = 0.3, z:P ([\d:. ]+) ;", ln)
            d["q1"] = [tuple(e.split(":")) for e in m.group(1).split()]
            d["q3"] = [tuple(e.split(":")) for e in m.group(2).split()]
            d["zmin"] = [tuple(e.split(":")) for e in re.search(r"q:z ([\d:. ]+), as in the paper", ln).group(1).split()]
            d["paper7"] = "every value equals the paper's to 7 decimals" in ln
        elif ln.startswith("race: "):
            d["trials"] = re.search(r"q = 0.1, ([\d,]+) simulated races", ln).group(1)
            d["race"] = re.findall(r"z = (\d+): simulated ([\d.]+), formula ([\d.]+)", ln)
        elif ln.startswith("widget: "):
            d["msg"] = re.search(r'the text "(.*?)\|nonce:N"', ln).group(1)
            d["wg"] = [dict(bits=int(b), nonce=int(n), hash=h) for b, n, h in re.findall(r"(\d+) bits: nonce (\d+), hash ([0-9a-f]{64})", ln)]
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def blocks_svg(d):
    tp = d["tamper"]

    def draw(t, standalone):
        W, H = 760, 330
        o = []
        bw, bh, gap, x0 = 150, 150, 36, 20

        def block(i, x, y, bad=False, title=None):
            col = t["red"] if bad else t["ink"]
            o.append(C.rect(x, y, bw, bh, t["surface"], col, 1.8 if bad else 1.4))
            o.append(C.text(x + 10, y + 20, title or f"block {i}", col, 13, "start", 700))
            rows = [("previous hash", f"hash of block {i - 1}"), ("Merkle root", "of its payments"), ("nonce", "found by trying")]
            for j, (k, v) in enumerate(rows):
                yy = y + 42 + j * 34
                o.append(C.rect(x + 8, yy - 13, bw - 16, 28, t["wash"], t["axis"], 0.8))
                o.append(C.text(x + 14, yy - 1, k, t["muted"], 10))
                o.append(C.text(x + 14, yy + 11, v, t["ink"], 11))
        bad = int(tp["block"])
        for i in range(4):
            x = x0 + i * (bw + gap)
            block(i + 1, x, 40, bad=(i + 1 == bad), title=f"block {i + 1}: changed" if i + 1 == bad else None)
            if i < 3:
                broken = i + 1 == bad
                o.append(C.line(x + bw, 40 + 29 + 13, x + bw + gap - 4, 40 + 29 + 13, t["red"] if broken else t["ink"], 1.6,
                                ";stroke-dasharray:4 3" if broken else ";marker-end:url(#bk-arrow)"))
                if broken:
                    o.append(C.text(x + bw + gap / 2, 40 + 29 + 5, "✗", t["red"], 14, "middle", 700))
        o.append(C.text(20, 26, "Each block's header holds the previous block's hash; its own hash must start with enough zero bits.", t["ink"], 12.5, "start", 700))
        o.append(C.text(20, 222, f"Change one payment in block {tp['block']}: its Merkle root changes, so its hash, so the next block's link breaks.", t["red"], 12.5, "start", 700))
        o.append(C.text(20, 244, f"To repair the chain the attacker must re-mine block {tp['a']} and every block after it: in the program,", t["ink"], 12.5))
        o.append(C.text(20, 264, f"{tp['len']} blocks at {tp['bits']} zero bits, re-mining blocks {tp['a']} to {tp['b']} took {tp['tries']} tries (about {tp['k']} × 2^{tp['bits']} = {tp['expect']}),", t["ink"], 12.5))
        o.append(C.text(20, 284, "while the honest computers keep adding blocks to the real chain.", t["ink"], 12.5))
        defs = f'<defs><marker id="bk-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" markerUnits="userSpaceOnUse" orient="auto"><path d="M0,0 L10,5 L0,10 z" style="fill:{t["ink"]}"/></marker></defs>'
        return C.svg_doc(W, H, defs + "".join(o), "Four blocks, each holding the previous block's hash", t, standalone, 0.5, 760)
    return draw


def race_svg(d):
    def draw(t, standalone):
        W, H = 760, 380
        L, R, T, B = 80, 720, 40, 320
        zs = [int(z) for z, _ in d["q1"]]
        lo, hi = -7, 0
        X = lambda z: L + (z - zs[0]) / (zs[-1] - zs[0]) * (R - L)
        Y = lambda p: T + (hi - math.log10(p)) / (hi - lo) * (B - T)
        o = [C.text(20, 24, "Chance that an attacker with 10% of the computing power ever catches up from z blocks behind", t["ink"], 13, "start", 700)]
        for e in range(lo, hi + 1):
            o.append(C.line(L, Y(10 ** e), R, Y(10 ** e), t["axis"], 0.6))
            o.append(C.text(L - 8, Y(10 ** e) + 4, "1" if e == 0 else "10" + "⁻" + "⁰¹²³⁴⁵⁶⁷⁸⁹"[-e], t["muted"], 11, "end"))
        for z in zs:
            o.append(C.text(X(z), B + 18, str(z), t["muted"], 11, "middle"))
        o.append(C.text((L + R) / 2, B + 38, "z, blocks behind", t["muted"], 12, "middle"))
        pts = [(X(int(z)), Y(float(p))) for z, p in d["q1"]]
        o.append(C.path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts), t["blue"], "none", 2.2))
        for x, y in pts:
            o.append(C.circle(x, y, 4, t["blue"], t["blue"], 1))
        for z, sim, form in d["race"]:
            o.append(C.circle(X(int(z)), Y(float(sim)), 6, "none", t["red"], 2.2))
        lx, ly = 470, 70
        o.append(C.line(lx, ly, lx + 28, ly, t["blue"], 2.2))
        o.append(C.circle(lx + 14, ly, 4, t["blue"], t["blue"], 1))
        o.append(C.text(lx + 38, ly + 4, "Nakamoto's formula (Section 11)", t["ink"], 12))
        o.append(C.circle(lx + 14, ly + 24, 6, "none", t["red"], 2.2))
        o.append(C.text(lx + 38, ly + 28, f"the race simulated, {d['trials']} times", t["ink"], 12))
        return C.svg_doc(W, H, "".join(o), "The attacker's chance falls exponentially with z; the simulated race lies above the formula from z = 2", t, standalone, 0.5, 760)
    return draw


BT_HTML = """
<div class="board bt-board">
  <div style="min-width:0">
    <div class="controls">
      <label>block <input id="bt-msg" type="text" value="__MSG__" spellcheck="false"></label>
      <label>zero bits <select id="bt-bits"><option>4</option><option>8</option><option selected>12</option><option>16</option><option>20</option></select></label>
      <button type="button" class="primary" id="bt-go">Mine</button>
    </div>
    <p class="bt-line">nonce <b id="bt-n">0</b> · SHA-256 of “<span id="bt-text"></span>”</p>
    <div class="bt-hash" id="bt-hash" aria-live="off"></div>
    <div class="bt-bits" id="bt-bitrow" aria-hidden="true"></div>
  </div>
  <div style="min-width:0">
    <p class="say" id="bt-say" aria-live="polite"></p>
  </div>
</div>
"""

BT_CSS = """
.bt-board .controls{display:flex;gap:10px;align-items:end;flex-wrap:wrap}
.bt-board #bt-msg{width:14em}
.bt-board select{font:inherit;font-family:var(--mono);font-size:14px;padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.bt-line{font-size:13px;color:var(--muted);margin:12px 0 4px;overflow-wrap:anywhere}
.bt-line b{color:var(--ink);font-family:var(--mono)}
.bt-hash{font:14px/1.5 var(--mono);overflow-wrap:anywhere;background:var(--wash);padding:8px 10px}
.bt-hash .z{background:var(--yellow);color:var(--on-yellow)}
.bt-hash.ok{outline:2px solid var(--blue)}
.bt-hash.bad{outline:2px solid var(--red)}
.bt-bits{display:flex;flex-wrap:wrap;gap:1px;margin-top:6px}
.bt-bits span{width:9px;height:12px;background:var(--axis)}
.bt-bits span.z{background:var(--yellow)}
.bt-bits span.need{outline:1px solid var(--ink)}
"""

BT_JS = r"""
(() => {
  const msgIn = document.getElementById("bt-msg");
  if (!msgIn) return;
__SHA__
  const PROG = __PROG__, MSG = __MSGJS__;
  const enc = new TextEncoder();
  const hex = b => Array.from(b, x => x.toString(16).padStart(2, "0")).join("");
  function zeros(b) { let n = 0; for (const x of b) { if (x === 0) { n += 8; continue; } n += Math.clz32(x) - 24; break; } return n; }
  const hashOf = (m, n) => sha256(enc.encode(`${m}|nonce:${n}`));
  let nonce = 0, sealedFor = null, sealedBits = 0, job = 0;
  const bitsSel = document.getElementById("bt-bits");
  function show(h, need) {
    const z = zeros(h), hx = hex(h), box = document.getElementById("bt-hash");
    const zd = Math.floor(z / 4);
    box.innerHTML = "";
    el("span", {class: "z"}, box, hx.slice(0, zd));
    el("span", {}, box, hx.slice(zd));
    box.className = "bt-hash " + (z >= need ? "ok" : "bad");
    const row = document.getElementById("bt-bitrow"); row.innerHTML = "";
    for (let i = 0; i < 32; i++) {
      const bit = (h[i >> 3] >> (7 - (i & 7))) & 1;
      el("span", {class: (bit === 0 && i < z ? "z" : "") + (i < need ? " need" : ""), title: String(bit)}, row);
    }
    return z;
  }
  function refresh(note) {
    const m = msgIn.value, need = +bitsSel.value, h = hashOf(m, nonce);
    document.getElementById("bt-n").textContent = nonce.toLocaleString("en-US");
    document.getElementById("bt-text").textContent = `${m}|nonce:${nonce}`;
    const z = show(h, need);
    let s = note || "";
    if (!note) {
      if (sealedFor !== null && m !== sealedFor) s = `You changed the block. With the same nonce the hash now starts with ${z} zero bit${z === 1 ? "" : "s"}, not ${sealedBits}: the seal is broken, and the block must be mined again.`;
      else s = z >= need ? `The hash starts with ${z} zero bits: at least ${need}, so the block is sealed. Checking it took one hash.` : `The hash starts with ${z} zero bit${z === 1 ? "" : "s"}; ${need} are needed. Press Mine to try nonce after nonce.`;
    }
    document.getElementById("bt-say").textContent = s;
  }
  function mine() {
    const m = msgIn.value, need = +bitsSel.value, my = ++job;
    let n = 0;
    const t0 = performance.now();
    function chunk() {
      if (my !== job) return;
      const end = n + 20000;
      for (; n < end; n++) {
        const h = hashOf(m, n);
        if (zeros(h) >= need) {
          nonce = n; sealedFor = m; sealedBits = zeros(h);
          const pg = m === MSG ? PROG.find(p => p.bits === need) : null;
          let s = `Found after ${(n + 1).toLocaleString("en-US")} tries (about 2^${need} = ${(2 ** need).toLocaleString("en-US")} expected), in ${Math.round(performance.now() - t0)} ms. Checking it takes one hash.`;
          if (pg) s += pg.nonce === n && pg.hash === hex(h) ? ` The program found the same nonce, ${pg.nonce}, and the same hash.` : ` The program found nonce ${pg.nonce}.`;
          s += " Now change one letter of the block.";
          refresh(s);
          return;
        }
      }
      nonce = n; refresh(`Trying… ${n.toLocaleString("en-US")} nonces so far.`);
      setTimeout(chunk, 0);
    }
    chunk();
  }
  document.getElementById("bt-go").addEventListener("click", mine);
  msgIn.addEventListener("input", () => { job++; refresh(); });
  bitsSel.addEventListener("change", () => { job++; refresh(); });
  refresh();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Bitcoin combined older ideas, and where it led")
    W = 210
    nodes = {
        "hc": (20, 20, "Hashcash", "proof of work against spam", "Adam Back, 1997", "ink"),
        "mk": (395, 20, "Merkle trees", "one hash seals many items", "Era 7, topic 2", "ink"),
        "bz": (770, 20, "Byzantine agreement", "agreement despite traitors", "Era 7, topic 3", "ink"),
        "bc": (395, 180, "Bitcoin", "⊕ the longest chain of work decides", "Nakamoto, 31 October 2008", "red"),
        "gen": (20, 340, "The genesis block", "3 January 2009", "", "ink"),
        "fin": (770, 340, "The first transaction", "10 bitcoins to Hal Finney", "12 January 2009, block 170", "ink"),
        "txt": (395, 490, "A textbook subject", "Princeton University Press, 2016", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("hc", "bc", ports=("bottom", "top:0.15"))
    D.edge("mk", "bc", ports=("bottom", "top"))
    D.edge("bz", "bc", ports=("bottom", "top:0.85"), label="among strangers", at=0.55, dy=-6, dx=-8, anchor="end")
    D.edge("bc", "gen", ports=("bottom:0.15", "top"))
    D.edge("bc", "fin", ports=("bottom:0.85", "top"))
    D.edge("bc", "txt", ports=("bottom", "top"))
    D.text(20, 615, "The announcement: \"No mint or other trusted parties\".", "caption")
    return D


def chain(d):
    q1 = dict(d["q1"])
    steps = [
        ("Without a trusted party, the payee can't tell whether a coin was spent twice",
         "Everyone keeps the ledger: blocks chained by hashes, sealed by proof of work", "Nakamoto, 2008"),
        ("Strangers, with no list of members, must agree on one history",
         "\"Nodes always consider the longest chain to be the correct one\"", "the chain with the most work"),
        ("An attacker can secretly build a rival chain",
         f"Wait z blocks: with 10% of the power, z = 5 leaves a chance of {q1['5']}", "Section 11"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from the bank to the longest chain")
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
    g, mi, tp, race, wg = d["gen"], d["mining"], d["tamper"], d["race"], d["wg"]
    assert d["paper7"]
    q1, q3 = d["q1"], d["q3"]
    over = [z for z, s, f in race if float(s) > float(f)]
    z5 = next(r for r in race if r[0] == "5")
    ratio = float(z5[1]) / float(z5[2])
    hdr = g["header"]
    gen_rows = [["version", hdr[0:8], g["version"]], ["previous block's hash", hdr[8:24] + "…", "zero: there is none"],
                ["Merkle root", hdr[72:88] + "…", "of its one transaction"], ["time", hdr[136:144], g["time"] + " seconds since 1970"],
                ["bits (the target)", hdr[144:152], g["bits"]], ["nonce", hdr[152:160], g["nonce"]]]
    mine_rows = [[b, n, t, e] for b, n, t, e in mi]
    sec_rows = [[q1[i][0], q1[i][1], q3[i][0], q3[i][1]] for i in range(len(q1))]
    zmin_rows = [[q, z] for q, z in d["zmin"]]
    race_rows = [[z, s, f] for z, s, f in race]
    w16 = wg[-1]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Hashcash (1997) made a computer prove it had done work, against spam. Merkle's trees (Era 7) sealed many items under one hash. The Byzantine generals (Era 7) showed how to agree despite traitors, among a known list of participants. Nakamoto chained blocks of payments by their hashes, sealed each with a proof of work, and let the chain with the most work decide. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Bitcoin. Blue: where it stands today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Mine a block, then break it", toc="Try it", blocks=[
            dict(type="p", text=f"The block here is just a line of text. Mining means trying nonce after nonce until the SHA-256 hash of \"text|nonce:N\" starts with enough zero bits; the yellow digits are the zeros. Each extra zero bit doubles the expected work. With the program's text, \"{d['msg']}\", the widget finds the same nonces the program did: {', '.join(str(w['nonce']) + ' for ' + str(w['bits']) + ' bits' for w in wg)}. Then change one letter."),
            dict(type="widget", html=BT_HTML.replace("__MSG__", d["msg"]), js=BT_JS.replace("__SHA__", C.SHA256_JS).replace("__PROG__", json.dumps(wg)).replace("__MSGJS__", json.dumps(d["msg"])), css=BT_CSS,
                 fallback=dict(type="table", head=["Zero bits", "Nonce", "Hash"], num=[0, 1], rows=[[str(w["bits"]), str(w["nonce"]), w["hash"][:24] + "…"] for w in wg]),
                 note="In the interactive edition you can mine your own text and watch the seal break when you change it."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 8, the Web, the genome and the ledger", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A chain of sealed blocks", toc="How it works", blocks=[
            dict(type="p", text="**A block.** Each block holds a batch of payments, summarized by the root of a Merkle tree of their hashes; the hash of the block before it; and a number called the nonce. It counts only if the SHA-256 hash of its header, read as a number, is below a target: it starts with enough zero bits. Nobody knows how to find such a nonce except by trying, about 2^d tries for d zero bits. Checking takes one hash."),
            dict(type="svg", name="blocks", draw=blocks_svg(d), alt="Four blocks, each holding the previous block's hash", width=760),
            dict(type="p", text="**The longest chain.** Every node keeps a copy and always extends the chain with the most work. To rewrite an old payment an attacker must redo that block and every block after it, and then overtake the honest computers, which keep adding blocks. **Section 11.** Nakamoto computed the attacker's chance. While the honest side finds z blocks, he counts the attacker's blocks with a Poisson distribution of mean z q/p, where q is the attacker's share of the computing power and p = 1 − q; from k blocks behind, the attacker ever draws level with probability (q/p)^k."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Make each vote cost computation, and let the history with the most computation behind it win. Then rewriting history means out-computing everyone else."),
        ]),
        dict(id="measured", eyebrow="Measured", title="The first block, and the attacker's chances", toc="Measured", blocks=[
            dict(type="p", text=f"**The genesis block** of 3 January 2009: its 80-byte header, hashed twice with SHA-256 and read with its bytes reversed, gives `{g['hash']}`, the published hash, with {g['zeros']} leading zero bits. The target encoded in the header is {g['target']} = 2^{g['texp']} × {g['tman']}, so about 2^{g['tries_exp']} = {g['tries']} tries were expected."),
            dict(type="table", head=["Field", "Bytes (hex)", "Value"], num=[], rows=gen_rows),
            dict(type="p", text="**Mining a toy chain**, blocks of 4 payments, at 4 to 16 zero bits:"),
            dict(type="table", head=["Zero bits", "Blocks", "Tries per block", "2^d"], num=[0, 1, 2, 3], rows=mine_rows),
            dict(type="p", text=f"**Tampering**: in a chain of {tp['len']} blocks at {tp['bits']} zero bits, one payment in block {tp['block']} was changed. Its Merkle root and hash changed, the old nonce {tp['old']} {tp['bits']} zero bits, and block {int(tp['block']) + 1}'s link broke. Re-mining blocks {tp['a']} to {tp['b']} took {tp['tries']} tries."),
            dict(type="p", text="**Section 11, recomputed** from Nakamoto's formula: every value equals the paper's to 7 decimals."),
            dict(type="table", head=["z (q = 0.1)", "P", "z (q = 0.3)", "P"], num=[0, 1, 2, 3], rows=sec_rows),
            dict(type="p", text="The smallest z with P below 0.1%, as in the paper:"),
            dict(type="table", head=["Attacker's share q", "Blocks to wait"], num=[0, 1], rows=zmin_rows),
            dict(type="p", text=f"**The race itself**, simulated {d['trials']} times for each z with q = 0.1, block by block: first the attacker's blocks while the honest side finds z, then the race until the attacker draws level. The simulation came out above the formula for z = {', '.join(over)}; at z = 5 it was {ratio:.1f} times the formula. The formula's Poisson count is an approximation: counted block by block, the attacker's blocks follow a different distribution with the same mean."),
            dict(type="table", head=["z", "Simulated", "Formula"], num=[0, 1, 2], rows=race_rows),
            dict(type="svg", name="race", draw=race_svg(d), alt="The attacker's chance falls exponentially with z", width=760),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A paper on a mailing list", toc="The evidence", blocks=[
            dict(type="p", text="Nakamoto's paper: \"A purely peer-to-peer version of electronic cash would allow online payments to be sent directly\"; \"The problem of course is the payee can't verify that one of the owners did not double-spend the coin\"; the block's hash must begin with a number of zero bits, \"similar to Adam Back's Hashcash\"; transactions are \"hashed in a Merkle Tree\"; \"Nodes always consider the longest chain to be the correct one\"; the system is secure \"As long as a majority of CPU power is controlled by nodes that are not cooperating to attack the network\"; Section 11 gives the attacker's chance with tables for q = 0.1 and 0.3. The announcement to the Cryptography Mailing List, Friday 31 October 2008: \"No mint or other trusted parties\"."),
            dict(type="p", text="Wikipedia's history: bitcoin.org was registered on 18 August 2008; the genesis block of 3 January 2009 carries the text \"The Times 03/Jan/2009 Chancellor on brink of second bailout for banks\"; the first client was released on 9 January 2009; Hal Finney received 10 bitcoins in the first transaction, on 12 January 2009 (block 170); hashcash was \"a proof-of-work scheme for spam control in 1997\". The Bitcoin Wiki lists the genesis header's fields and hash; its 50-bitcoin reward cannot be spent. Narayanan, Bonneau, Felten, Miller and Goldfeder's *Bitcoin and Cryptocurrency Technologies* (Princeton, 2016) is a textbook on \"decentralization, mining, the politics of bitcoin\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Agreement, paid for in work", toc="Full circle", blocks=[
            dict(type="p", text="Paxos (topic 8) agrees on one history among a known set of machines, by majorities of votes. Bitcoin agrees among strangers who may join or leave at any time, so it counts work instead of votes. Each block seals its payments with a Merkle root, Era 7's idea, and the first block's 80 bytes can still be checked by anyone."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The genesis block's header still hashes to {g['hash'][:20]}…, with {g['zeros']} zero bits: one hash to check work that was expected to take about {g['tries']} tries."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Why does each extra zero bit double the work?", "Each bit of a good hash is 0 with probability ½, independently of the others, so d zero bits need about 2^d tries."),
            ("How much work does it take to check a proof of work?", "One hash of the header (in Bitcoin, SHA-256 applied twice), and a count of its zero bits."),
            (f"If a payment in block {tp['block']} changes, why must every later block be mined again?", "Each block holds the previous block's hash. The changed block gets a new hash, which breaks the next block's link, and so on to the end."),
            ("With 30% of the computing power against you, how many blocks should you wait for a chance below 0.1%?", f"{dict(d['zmin'])['0.30']}, from Section 11's table."),
            ("Why is a Poisson count only an approximation here?", "The number of attacker blocks found while the honest side finds exactly z is counted block by block; the Poisson distribution with the same mean is close, but not the same."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Bitcoin: A Peer-to-Peer Electronic Cash System (2008)", text="The design and the Section 11 calculations.",
                 draw=C.draw_manuscript, link="https://courses.csail.mit.edu/6.857/2015/files/L07-nakamoto-bitcoin-a-peer-to-peer-electronic-cash-system.pdf", link_text="The paper (PDF, on an MIT course page)", licence="Drawn placeholder."),
            dict(title="The announcement (31 October 2008)", text="Posted to the Cryptography Mailing List.",
                 draw=C.draw_manuscript, link="https://www.metzdowd.com/pipermail/cryptography/2008-October/014810.html", link_text="The mailing-list archive", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Bitcoin", d["checks"],
                           "that the genesis header hashes to the published hash and lies below its target, that mined blocks need about 2^d tries, that tampering breaks the chain, and that Section 11's tables match the paper to 7 decimals.",
                           ["static long mine(byte[] prev, byte[] root, int bits)", "static double attackerSuccess(double q, int z)"]),
    ]
    return dict(
        title="Bitcoin's Proof-of-Work Ledger", date="2008",
        description="Era 8, topic 13 of The Algorithm Evolution Atlas: Nakamoto's Bitcoin (2008) as an algorithm: a hash-chained ledger sealed by proof of work, with the genesis block and Section 11 recomputed.",
        lede="Digital money has an obvious flaw: a file can be copied, so a coin can be spent twice. In October 2008 a paper signed Satoshi Nakamoto described a ledger kept by everyone, sealed block by block with proof of work, in which rewriting history means outrunning the majority of the computing power.",
        fieldnote=f"I hashed the ledger's first block, 80 bytes from 3 January 2009, and got its published hash, {g['zeros']} zero bits long. Nakamoto's table of an attacker's chances matched his formula to seven decimals. But when I ran the race itself {d['trials']} times, an attacker 5 blocks behind won {ratio:.1f} times as often as the formula says.",
        card=[("When", "31 October 2008; genesis block 3 January 2009"),
              ("Where", "The Cryptography Mailing List"),
              ("What hurt", "Without a trusted party, coins could be spent twice"),
              ("The fix", "A hash-chained ledger sealed by proof of work"),
              ("Checked", "The genesis header hashes to the published hash")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Bitcoin.java`.",
    )
