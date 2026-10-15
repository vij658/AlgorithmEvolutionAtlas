"""Era 7, topic 2: Merkle's hash trees. Every number is parsed from MerkleTrees.java's output."""
import json
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"proofs: trees of 1 to (\d+) leaves.*? ; ([\d,]+) inclusion proofs checked, every one accepted ; ([\d,]+) forged ones", ln):
            d["proofs"] = dict(maxn=m.group(1), ok=m.group(2), forged=m.group(3))
        elif m := re.match(r"eight: .*? levels separated by \| : (.*?) ; root ([0-9a-f]+)$", ln):
            d["eight"] = dict(levels=[lv.split() for lv in m.group(1).split(" | ")], root=m.group(2))
        elif m := re.match(r"pathcost: [^;]* ; (.*)$", ln):
            rows = []
            for part in m.group(1).split(" ; "):
                mm = re.match(r"([\d,]+) blocks: a proof needs (\d+) hashes plus the leaf's own, a plain list of fingerprints needs all ([\d,]+)", part)
                rows.append(dict(n=mm.group(1), proof=mm.group(2), plain=mm.group(3)))
            d["path"] = rows
        elif m := re.match(r"repair: two copies of ([\d,]+) blocks, [^;]* ; (.*?) ; comparing block by block takes ([\d,]+)", ln):
            rows = []
            for part in m.group(2).split(" ; "):
                mm = re.match(r"([\d,]+) changed: ([\d,]+) comparisons?", part)
                rows.append(dict(d=mm.group(1), cmp=mm.group(2)))
            d["repair"] = dict(n=m.group(1), rows=rows, plain=m.group(3))
        elif m := re.match(r"preimage: [^;]* ; without the bytes: four blocks give root ([0-9a-f]+)\.\.\., two 64-byte forged blocks give root ([0-9a-f]+)\.\.\., (the same|different) ; with 0x00 and 0x01: four blocks give root ([0-9a-f]+)\.\.\., two 64-byte forged blocks give root ([0-9a-f]+)\.\.\., (the same|different)", ln):
            d["pre"] = dict(h0=m.group(1), f0=m.group(2), s0=m.group(3), h1=m.group(4), f1=m.group(5), s1=m.group(6))
        elif m := re.match(r"lamport: .*?their 512 hashes \(([\d,]+) bytes\) ; .*?\(([\d,]+) bytes\) ; .*? revealed (\d+), both secrets at (\d+) positions", ln):
            d["lamport"] = dict(pub=m.group(1), sig=m.group(2), revealed=m.group(3), both=m.group(4))
        elif m := re.match(r"mss: .*? with (\d+) one-time keys in a tree of height (\d+) ; public key: the 32-byte root ([0-9a-f]+)\.\.\. ; making the keys took ([\d,]+) hashes ; (\d+) signatures verified, (\d+) forgeries rejected ; each signature is ([\d,]+) bytes", ln):
            d["mss"] = dict(keys=m.group(1), h=m.group(2), root=m.group(3), keygen=m.group(4), good=m.group(5), bad=m.group(6), size=m.group(7))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def proof_svg(d):
    """An eight-leaf tree with the proof for leaf 5: the path in red, the hashes sent in blue."""
    def draw(t, standalone):
        o = []
        W, H = 760, 350
        o.append(C.text(20, 26, "Proving that block 5 belongs: send only the three blue hashes", t["ink"], 13, "start", 700))
        ys = [270, 200, 130, 60]
        leaf = 5
        path = {(0, leaf), (1, leaf // 2), (2, leaf // 4), (3, 0)}
        sibs = {(0, leaf ^ 1), (1, (leaf // 2) ^ 1), (2, (leaf // 4) ^ 1)}
        names = {0: lambda i: f"h{i}", 1: lambda i: f"h{2 * i}{2 * i + 1}", 2: lambda i: f"h{4 * i}–{4 * i + 3}", 3: lambda i: "root"}
        for lev in range(4):
            cnt = 8 >> lev
            span = 720 / cnt
            for i in range(cnt):
                x = 20 + span * i + span / 2
                if lev < 3:
                    px = 20 + (720 / (cnt // 2)) * (i // 2) + (720 / (cnt // 2)) / 2
                    o.append(C.line(x, ys[lev] - 16, px, ys[lev + 1] + 16, t["axis"], 1.4))
                col = t["red"] if (lev, i) in path else t["blue"] if (lev, i) in sibs else t["ink"]
                fill = t["wash"] if (lev, i) in sibs else t["surface"]
                o.append(C.rect(x - 34, ys[lev] - 16, 68, 32, fill, col, 2.5 if col != t["ink"] else 1.2, 3))
                o.append(C.text(x, ys[lev] + 5, names[lev](i), col, 13, "middle", 700))
            if lev == 0:
                for i in range(8):
                    x = 20 + 90 * i + 45
                    o.append(C.text(x, ys[0] + 34, f"block {i}", t["red"] if i == leaf else t["muted"], 11.5, "middle", 700 if i == leaf else 400))
        o.append(C.text(20, H - 8, "The checker hashes block 5 (red), combines it with h4, then h67, then h0–3, and compares the result with the root it trusts.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "A Merkle tree with the proof for one block", t, standalone, 0.55, 760)
    return draw


MK_HTML = """
<div class="board mk-board">
  <div style="min-width:0">
    <div class="mk-tree" id="mk-tree"></div>
    <div class="mk-leaves" id="mk-leaves"></div>
  </div>
  <div style="min-width:0">
    <div class="mk-btns"><button type="button" id="mk-reset">Restore the blocks</button></div>
    <div class="mk-stats" id="mk-stats"></div>
    <p class="say" id="mk-say" aria-live="polite"></p>
  </div>
</div>
"""

MK_CSS = """
.mk-tree svg{display:block;width:100%;height:auto;background:var(--wash)}
.mk-tree text{font-family:var(--mono)}
.mk-leaves{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:8px}
.mk-leaves input{width:100%;box-sizing:border-box;font:12.5px var(--mono);padding:4px 6px;border:1px solid var(--axis);background:var(--paper);color:var(--ink)}
.mk-leaves input.sel{border:2px solid var(--red)}
.mk-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.mk-stats{font:13px var(--mono);display:grid;gap:3px;margin-top:8px}
@media (max-width:600px){.mk-leaves{grid-template-columns:repeat(2,minmax(0,1fr))}}
"""

MK_JS = r"""
(() => {
  const host = document.getElementById("mk-tree");
  if (!host) return;
  const PROG = __PROG__, ROOT = "__ROOT__";
  // SHA-256, written out so the page needs no secure context
  const K = [0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
  function sha256(bytes) {
    const l = bytes.length, n = ((l + 9 + 63) >> 6) << 6, m = new Uint8Array(n);
    m.set(bytes); m[l] = 0x80;
    const bits = l * 8; for (let i = 0; i < 8; i++) m[n - 1 - i] = Math.floor(bits / Math.pow(2, 8 * i)) & 255;
    let h = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];
    const w = new Array(64), rot = (x, k) => (x >>> k) | (x << (32 - k));
    for (let o = 0; o < n; o += 64) {
      for (let i = 0; i < 16; i++) w[i] = (m[o + 4 * i] << 24) | (m[o + 4 * i + 1] << 16) | (m[o + 4 * i + 2] << 8) | m[o + 4 * i + 3];
      for (let i = 16; i < 64; i++) {
        const s0 = rot(w[i - 15], 7) ^ rot(w[i - 15], 18) ^ (w[i - 15] >>> 3), s1 = rot(w[i - 2], 17) ^ rot(w[i - 2], 19) ^ (w[i - 2] >>> 10);
        w[i] = (w[i - 16] + s0 + w[i - 7] + s1) | 0;
      }
      let [a, b, c, d, e, f, g, hh] = h;
      for (let i = 0; i < 64; i++) {
        const t1 = (hh + (rot(e, 6) ^ rot(e, 11) ^ rot(e, 25)) + ((e & f) ^ (~e & g)) + K[i] + w[i]) | 0;
        const t2 = ((rot(a, 2) ^ rot(a, 13) ^ rot(a, 22)) + ((a & b) ^ (a & c) ^ (b & c))) | 0;
        hh = g; g = f; f = e; e = (d + t1) | 0; d = c; c = b; b = a; a = (t1 + t2) | 0;
      }
      h = [h[0] + a, h[1] + b, h[2] + c, h[3] + d, h[4] + e, h[5] + f, h[6] + g, h[7] + hh].map(x => x | 0);
    }
    const out = new Uint8Array(32);
    h.forEach((x, i) => { out[4 * i] = x >>> 24; out[4 * i + 1] = (x >>> 16) & 255; out[4 * i + 2] = (x >>> 8) & 255; out[4 * i + 3] = x & 255; });
    return out;
  }
  const enc = new TextEncoder(), hex = b => Array.from(b, x => x.toString(16).padStart(2, "0")).join("");
  const cat = (...parts) => { const n = parts.reduce((s, p) => s + p.length, 0), r = new Uint8Array(n); let k = 0; parts.forEach(p => { r.set(p, k); k += p.length; }); return r; };
  const leafH = s => sha256(cat(Uint8Array.of(0), enc.encode(s))), nodeH = (a, b) => sha256(cat(Uint8Array.of(1), a, b));
  const orig = Array.from({length: 8}, (_, i) => "log block " + i);
  let blocks = orig.slice(), chosen = 5;
  const leavesBox = document.getElementById("mk-leaves");
  const inputs = blocks.map((b, i) => {
    const inp = el("input", {type: "text", value: b, "aria-label": "block " + i}, leavesBox);
    inp.addEventListener("input", () => { blocks[i] = inp.value; chosen = i; draw(); });
    inp.addEventListener("focus", () => { chosen = i; draw(); });
    return inp;
  });
  function levels(bs) {
    const L = [bs.map(leafH)];
    while (L[L.length - 1].length > 1) { const p = L[L.length - 1], q = []; for (let i = 0; i < p.length; i += 2) q.push(nodeH(p[i], p[i + 1])); L.push(q); }
    return L;
  }
  const base = levels(orig);
  function draw() {
    const L = levels(blocks);
    host.innerHTML = "";
    const svg = sv("svg", {viewBox: "0 0 760 250"}, host), ys = [215, 150, 85, 22];
    const path = new Set(), sibs = new Set();
    for (let lev = 0, i = chosen; lev < 3; lev++, i >>= 1) { path.add(lev + ":" + i); sibs.add(lev + ":" + (i ^ 1)); }
    path.add("3:0");
    L.forEach((row, lev) => row.forEach((h, i) => {
      const span = 740 / row.length, x = 10 + span * i + span / 2, y = ys[lev];
      if (lev < 3) { const ps = 740 / (row.length / 2), px = 10 + ps * (i >> 1) + ps / 2; sv("line", {x1: x, y1: y, x2: px, y2: ys[lev + 1] + 26, stroke: "var(--axis)", "stroke-width": 1.4}, svg); }
      const changed = hex(h) !== hex(base[lev][i]), key = lev + ":" + i;
      const stroke = sibs.has(key) ? "var(--blue)" : path.has(key) ? "var(--ink)" : "var(--axis)";
      sv("rect", {x: x - 40, y: y - 2, width: 80, height: 28, rx: 3, fill: changed ? "var(--red)" : "var(--surface)", stroke, "stroke-width": sibs.has(key) || path.has(key) ? 2.5 : 1}, svg);
      const t = sv("text", {x, y: y + 17, "text-anchor": "middle", "font-size": 12.5, "font-weight": 700, fill: changed ? "var(--on-red)" : "var(--ink)"}, svg);
      t.textContent = hex(h).slice(0, 8);
    }));
    inputs.forEach((inp, i) => inp.classList.toggle("sel", i === chosen));
    // the proof for the chosen block, checked against the original root
    let r = leafH(blocks[chosen]), i = chosen;
    for (let lev = 0; lev < 3; lev++, i >>= 1) r = (i & 1) ? nodeH(base[lev][i ^ 1], r) : nodeH(r, base[lev][i ^ 1]);
    const ok = hex(r) === hex(base[3][0]), same = hex(L[3][0]) === ROOT;
    const st = document.getElementById("mk-stats"); st.innerHTML = "";
    el("div", {}, st, `root: ${hex(L[3][0]).slice(0, 16)}…`);
    el("div", {}, st, same ? "same root as the program's run" : "root no longer matches the program's");
    el("div", {}, st, `block ${chosen}'s proof: 3 hashes (blue)`);
    el("div", {}, st, `proof against the trusted root: ${ok ? "valid" : "rejected"}`);
    const changedLeaves = blocks.filter((b, k) => b !== orig[k]).length;
    document.getElementById("mk-say").textContent = changedLeaves === 0
      ? `Click a block to see its proof, or edit one. Red boxes are hashes that changed.`
      : `${changedLeaves} block${changedLeaves > 1 ? "s" : ""} edited: every hash on the way up turned red, so the root changed. Block ${chosen}'s proof ${ok ? "still checks, because its own path was untouched" : "fails against the trusted root"}.`;
  }
  document.getElementById("mk-reset").addEventListener("click", () => { blocks = orig.slice(); inputs.forEach((x, i) => x.value = orig[i]); draw(); });
  const want = PROG.map(r => r.join(" ")).join(" | "), got = base.map(r => r.map(h => hex(h).slice(0, 8)).join(" ")).join(" | ");
  if (want !== got) console.error("widget hashes differ from the program's");
  draw();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How Merkle's trees combined older ideas, and where they led")
    W = 210
    nodes = {
        "ow": (20, 20, "One-way functions", "easy to compute, infeasible to invert", "", "ink"),
        "ld": (395, 20, "One-time signatures", "Lamport and Diffie: one message per key", "", "ink"),
        "bt": (770, 20, "Binary trees", "pairs, then pairs of pairs", "", "ink"),
        "mk": (395, 180, "Merkle's tree", "⊕ hash pairs up to one root; log₂ n hashes per proof", "Stanford, 1979", "red"),
        "ms": (20, 340, "Hash-based signatures", "many one-time keys under one root", "NIST SP 800-208, 2020", "ink"),
        "ct": (395, 340, "Certificate logs", "⊕ markers for leaves and pairs", "RFC 6962, 2013", "ink"),
        "rep": (770, 340, "Checking copies", "file systems, version control, replicas, peer-to-peer", "", "ink"),
        "today": (395, 490, "Today", "Git, Bitcoin, BitTorrent, ZFS, Cassandra, certificate logs", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("ow", "mk", ports=("bottom", "top:0.15"))
    D.edge("ld", "mk", ports=("bottom", "top"))
    D.edge("bt", "mk", ports=("bottom", "top:0.85"))
    D.edge("mk", "ms", ports=("bottom:0.15", "top"))
    D.edge("mk", "ct", ports=("bottom", "top"))
    D.edge("mk", "rep", ports=("bottom:0.85", "top"))
    D.edge("ct", "today", ports=("bottom", "top"))
    D.edge("rep", "today", ports=("bottom", "top:0.85"))
    D.text(20, 615, "Today: uses listed by Wikipedia's article on Merkle trees (Git technically uses a graph of hashes rather than a tree).", "caption")
    return D


def chain(d):
    mss, pth, rep = d["mss"], d["path"], d["repair"]
    million = next(r for r in pth if r["n"] == "1,000,000")
    one = next(r for r in rep["rows"] if r["d"] == "1")
    steps = [
        ("A hash-based one-time key signs only one message",
         f"Merkle: put 2^h one-time public keys under one root; here {mss['keys']} messages under one 32-byte key", "Merkle, 1979"),
        ("Checking one block of a big collection needs a fingerprint for every block",
         f"A proof of log₂ n hashes: {million['proof']} for a million blocks, instead of {million['plain']}", "the same tree"),
        ("Two copies of a collection: where do they differ?",
         f"Compare the roots, then walk down only the halves that differ: {one['cmp']} comparisons for one change in {rep['n']} blocks", "replicas and file systems"),
        ("Without markers, a different list of leaves can give the same root",
         "Prefix 0x00 to leaves and 0x01 to pairs, so a pair can never pass for a leaf", "Certificate Transparency, 2013"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from one signature to a tree that vouches for anything")
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
    pr, pth, rep, pre, lp, mss, eight = d["proofs"], d["path"], d["repair"], d["pre"], d["lamport"], d["mss"], d["eight"]
    million = next(r for r in pth if r["n"] == "1,000,000")
    one = next(r for r in rep["rows"] if r["d"] == "1")
    path_rows = [[r["n"], r["proof"], r["plain"]] for r in pth]
    rep_rows = [[r["d"], r["cmp"]] for r in rep["rows"]]
    fallback_rows = [[f"level {k}" if k < 3 else "root", " ".join(lv)] for k, lv in enumerate(eight["levels"])]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Lamport and Diffie had shown how to sign a message with nothing but a one-way function, but each key could sign only once. Merkle hashed many such keys together in pairs, and pairs of pairs, up to a single root: one short public key for many signatures. The same tree turned out to vouch for any piece of any large collection of data. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Merkle's tree. Blue: where it is used today."),
        ]),
        dict(id="play", eyebrow="Try it", title="Change one letter, watch the root change", toc="Try it", blocks=[
            dict(type="p", text=f"Eight blocks of data, hashed with SHA-256 the way Certificate Transparency does it: 0x00 before a block, 0x01 before a pair. Each box shows the first 8 hex digits of a hash; the root at the top is the one the program printed ({eight['root'][:16]}…). Click a block to see its proof, the three blue hashes a checker needs. Then edit a block: every hash on the way up changes, so the root does too, while the proofs of blocks on untouched paths still check."),
            dict(type="widget", html=MK_HTML, js=MK_JS.replace("__PROG__", json.dumps(eight["levels"])).replace("__ROOT__", eight["root"]), css=MK_CSS,
                 fallback=dict(type="table", head=["Level", "Hashes (first 8 hex digits)"], rows=fallback_rows),
                 note="In the interactive edition you can edit the blocks and watch the hashes change."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 7, randomness, networks and learning", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A hash of hashes of hashes", toc="How it works", blocks=[
            dict(type="p", text="**A hash.** SHA-256 turns any data into 32 bytes. Nobody knows how to find two different inputs with the same output, so the 32 bytes can stand for the data."),
            dict(type="p", text="**The tree.** Hash each block. Hash the hashes in pairs, then the pairs of those, up to one root. Whoever trusts the root can check any block from that block plus one hash per level: the siblings along the path to the root."),
            dict(type="svg", name="proof", draw=proof_svg(d), alt="A Merkle tree with the proof for block 5", width=760),
            dict(type="p", text=f"**Finding differences.** Two copies of {rep['n']} blocks compare their roots. If the roots agree, so does everything. If not, compare the two children and go down only where they differ. One changed block is found with {one['cmp']} comparisons; block by block would take {rep['plain']}."),
            dict(type="p", text=f"**Signatures.** A Lamport one-time key is 512 secrets; the public key is their hashes ({lp['pub']} bytes). To sign, hash the message and, for each of its 256 bits, reveal the secret for that bit's value ({lp['sig']} bytes). A second signature with the same key revealed {lp['revealed']} of the 512 secrets, both secrets at {lp['both']} positions, enough to forge. Merkle's scheme hashes {mss['keys']} one-time public keys into a tree; the root is the public key, and each signature carries its one-time key and {mss['h']} path hashes."),
            dict(type="callout", kind="key", label="Key idea",
                 text="A hash makes data short; a tree of hashes makes the proof short. Trust one root, and any piece of anything under it can be checked in log₂ n steps."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Every proof, every forgery", toc="Measured", blocks=[
            dict(type="p", text=f"**Proofs.** For every tree of 1 to {pr['maxn']} leaves and every leaf: {pr['ok']} proofs checked and accepted, and {pr['forged']} forged ones (a changed leaf, a wrong position, a wrong root) rejected. The longest proof in a tree of n leaves always had ⌈log₂ n⌉ hashes."),
            dict(type="table", head=["Blocks", "Hashes in a proof", "Hashes in a plain list"], num=[0, 1, 2], rows=path_rows),
            dict(type="p", text=f"**Finding changed blocks** in two copies of {rep['n']} blocks:"),
            dict(type="table", head=["Blocks changed", "Hashes compared"], num=[0, 1], rows=rep_rows),
            dict(type="p", text=f"**Why the 0x00 and 0x01.** Without them, four blocks gave the root {pre['h0']}…, and a forger's list of two 64-byte \"blocks\" (each two leaf hashes glued together) gave {pre['f0']}…: {pre['s0']}. With the markers the roots were {pre['h1']}… and {pre['f1']}…: {pre['s1']}."),
            dict(type="p", text=f"**Signatures.** Merkle's scheme with {mss['keys']} one-time keys: public key {mss['root']}…, {mss['keygen']} hashes to make the keys, {mss['good']} signatures verified, {mss['bad']} forgeries rejected, {mss['size']} bytes per signature."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A thesis and a patent", toc="The evidence", blocks=[
            dict(type="p", text="Ralph Merkle's Stanford thesis, *Secrecy, Authentication, and Public Key Systems* (technical report 1979-1, June 1979), introduces \"tree authentication\" in chapter V: \"This method lets us selectively authenticate any 'leaf'\", and \"only log2 n transmissions are required, each of about 200 bits\". It builds on the one-time signatures of Lamport and Diffie, which on their own are \"not practical for most applications without further refinements\"."),
            dict(type="p", text="The patent, \"Method of providing digital signatures\" (US 4,309,569, assigned to Stanford), was filed on 5 September 1979 and granted on 5 January 1982; it names \"the root of the authentication tree\". The cryptographers' version appeared as \"A Digital Signature Based on a Conventional Encryption Function\" in *CRYPTO '87*."),
            dict(type="p", text="Certificate Transparency (RFC 6962, Google, 2013) fixed the tree's exact form, 0x00 before leaves and 0x01 before pairs, splitting at \"the largest power of two smaller than n\". Wikipedia lists the tree's uses, from Git and BitTorrent to Bitcoin and Cassandra, and notes that without such markers the root \"does not indicate the tree depth, enabling a second-preimage attack\"."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Public keys without number theory", toc="Full circle", blocks=[
            dict(type="p", text="Era 6's public keys rest on factoring and discrete logarithms. Merkle's signatures rest only on a hash function, and Wikipedia's article on them notes that they are \"believed to be resistant against attacks by quantum computers\", the machines of this era's topic 11. In 2020 NIST approved hash-based signature schemes descended from them."),
            dict(type="callout", kind="circle", label="Full circle",
                 text="In 1979 the tree was a way to make one-time signatures practical. Forty years later its descendants are a hedge against the quantum computers that would break the number-theory signatures it was competing with."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("How many hashes are in a proof for one block among 4,000,000,000?", "32, since 2³² is about 4.3 billion."),
            ("You change one block. Which hashes in the tree change?", "The block's own hash and every hash on the path up to the root: log₂ n + 1 of them."),
            ("Why can a Lamport key not sign two messages?", "The two signatures together reveal both secrets at every position where the messages' hashes differ, so an attacker can mix them to sign other messages."),
            ("Two replicas differ in one block out of 1,048,576. About how many hashes must they compare?", f"About 2 per level, 2 × 20 + 1 = 41, which is exactly what the program counted ({one['cmp']})."),
            ("What do the bytes 0x00 and 0x01 prevent?", "Passing off an inner node's two children, glued together, as a leaf: a different list of leaves with the same root."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Merkle's thesis (1979)", text="*Secrecy, Authentication, and Public Key Systems*, Stanford, June 1979; chapter V, section 4, \"tree authentication\".",
                 draw=C.draw_book, link="https://www.ralphmerkle.com/papers/Thesis1979.pdf", link_text="The thesis (PDF, Merkle's site)", licence="Drawn placeholder."),
            dict(title="US patent 4,309,569 (1982)", text="\"Method of providing digital signatures\", filed 5 September 1979.",
                 draw=C.draw_manuscript, link="https://patents.google.com/patent/US4309569", link_text="The patent (Google Patents)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "MerkleTrees", d["checks"],
                           "every inclusion proof in every tree of 1 to 200 leaves, three kinds of forgery, change-finding in two copies of a million blocks, the second-preimage forgery with and without markers, and Merkle's signature scheme with 64 one-time keys.",
                           ["static List<byte[]> proof(byte[][] leaf, int m, int lo, int hi)", "static byte[] rootFromProof("]),
    ]
    return dict(
        title="Merkle's Hash Trees", date="1979",
        description="Era 7, topic 2 of The Algorithm Evolution Atlas: Merkle's tree of hashes, short proofs that a block belongs, finding differences between copies, and many one-time signatures under one public key.",
        lede="A hash turns any data into 32 bytes that stand for it. Merkle hashed the hashes in pairs, up to one root, so that any piece of a huge collection can be checked against that root with a handful of hashes.",
        fieldnote=f"Two copies of {rep['n']} blocks disagreed in one place. They found it by comparing {one['cmp']} hashes. This species now builds its file systems, its version control and its money on the same trick.",
        card=[("When", "Thesis and patent filing, 1979"),
              ("Where", "Stanford University"),
              ("What hurt", "One-time signatures; checking a block meant checking everything"),
              ("The fix", "Hash pairs up to one root"),
              ("Checked", f"{pr['ok']} proofs accepted, {pr['forged']} forgeries rejected")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `MerkleTrees.java`.",
    )
