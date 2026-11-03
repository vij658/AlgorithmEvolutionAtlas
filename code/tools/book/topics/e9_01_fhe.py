"""Era 9, topic 1: Fully homomorphic encryption. Every number is parsed from FullyHomomorphic.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"scheme: secret p of (\d+) bits ; c = p\*q \+ 2r \+ m with q of (\d+) bits and noise r of (\d+) bits ; ciphertext of (\d+) bits ; (\d+) XOR", ln):
            d["scheme"] = dict(p=m.group(1), q=m.group(2), r=m.group(3), c=m.group(4), pairs=m.group(5))
        elif ln.startswith("noise: "):
            d["noise"] = dict(fresh=re.search(r"fresh: (\d+) bits", ln).group(1),
                              levels=re.findall(r"depth (\d+): ((?:over )?\d+) bits( \(decryption fails\))?", ln),
                              deepest=re.search(r"deepest working multiplication depth (\d+), doubling estimate (\d+)", ln).groups(),
                              add1=re.search(r"one addition: (\d+) bits", ln).group(1),
                              add1000=re.search(r"after 1,000 additions: (\d+) bits", ln).group(1))
        elif m := re.match(r"adder: .*? ; (\d+) pairs of 4-bit numbers, all sums correct ; noise in the final carry up to (\d+) bits of (\d+)", ln):
            d["adder"] = dict(pairs=m.group(1), bits=m.group(2), of=m.group(3))
        elif m := re.match(r"public: public key = (\d+) encryptions of 0 ; .*? ; (\d+) encryptions by subset sum", ln):
            d["public"] = dict(tau=m.group(1), n=m.group(2))
        elif m := re.match(r"gcd: .*?gcd has (\d+) bits and, after removing (\d+) small factors?, equals p ; with noise: gcd = (\d+) \((\d+) bits?\)", ln):
            d["gcd"] = dict(bits=m.group(1), removed=m.group(2), g=m.group(3))
        elif ln.startswith("widget: "):
            d["widget"] = dict(p=re.search(r"p = (\d+)", ln).group(1),
                               a=re.search(r"a = (.*?) = (\d+)", ln).groups(), b=re.search(r"b = (.*?) = (\d+)", ln).groups(),
                               sum=re.search(r"a \+ b = (\d+), noise (-?\d+), decrypts to (\d)", ln).groups(),
                               prod=re.search(r"a \* b = (\d+), noise (-?\d+), decrypts to (\d)", ln).groups(),
                               fit=re.search(r"products of (\d+) fresh ciphertexts", ln).group(1))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def fnoise(expr):
    """The noise 2r + m of a widget example written as p*q + 2*(r) + m."""
    r, m = re.search(r"2\*\((-?\d+)\) \+ (\d)", expr).groups()
    return str(2 * int(r) + int(m)).replace("-", "−")


def noise_svg(d):
    lv = d["noise"]["levels"]
    P = int(d["scheme"]["p"])
    rows = [("fresh", int(d["noise"]["fresh"]), False)] + [(f"depth {k}", P if v.startswith("over") else int(v), bool(f)) for k, v, f in lv]

    def draw(t, standalone):
        W, H = 760, 60 + 34 * len(rows) + 40
        o = [C.text(20, 26, f"Noise in bits after each level of multiplication (secret p of {P} bits)", t["ink"], 13, "start", 700)]
        x0, x1 = 120, 700
        sc = (x1 - x0) / P
        lim = x0 + (P - 1) * sc
        for i, (lab, bits, fail) in enumerate(rows):
            y = 50 + 34 * i
            o.append(C.text(x0 - 10, y + 16, lab, t["ink"], 12, "end"))
            w = min(bits, P) * sc
            o.append(C.rect(x0, y, w, 22, t["red"] if fail else t["blue"]))
            o.append(C.text(x0 + w + 6, y + 16, "fails: wrapped past p/2" if fail else f"{bits} bits", t["red"] if fail else t["ink"], 12))
        yb = 50 + 34 * len(rows)
        o.append(C.line(lim, 40, lim, yb, t["red"], 2, ";stroke-dasharray:5 4"))
        o.append(C.text(lim, yb + 18, "p/2: beyond this, decryption breaks", t["red"], 12, "end"))
        return C.svg_doc(W, H, "".join(o), "Noise growth under repeated multiplication", t, standalone, 0.55, 760)
    return draw


FHE_HTML = """
<div class="board fhe-board">
  <div style="min-width:0">
    <div class="fhe-key">Secret key <b>p = <span id="fhe-p"></span></b>. A ciphertext is c = p·q + 2r + m.</div>
    <div class="fhe-btns"><button type="button" class="primary" id="fhe-new0">Encrypt 0</button><button type="button" class="primary" id="fhe-new1">Encrypt 1</button></div>
    <div class="fhe-btns"><button type="button" id="fhe-add0">Add an encrypted 0 (XOR)</button><button type="button" id="fhe-add1">Add an encrypted 1 (XOR)</button></div>
    <div class="fhe-btns"><button type="button" id="fhe-mul0">Multiply by an encrypted 0 (AND)</button><button type="button" id="fhe-mul1">Multiply by an encrypted 1 (AND)</button></div>
    <div class="fhe-meter"><div class="fhe-bar" id="fhe-bar"></div><div class="fhe-lim"></div></div>
    <div class="fhe-stats" id="fhe-stats"></div>
    <p class="say" id="fhe-say" aria-live="polite"></p>
  </div>
</div>
"""

FHE_CSS = """
.fhe-key{font:14px var(--mono);margin-bottom:8px}
.fhe-btns{display:flex;gap:8px;flex-wrap:wrap;margin:6px 0}
.fhe-meter{position:relative;height:22px;background:var(--wash);border:1px solid var(--rule);margin:10px 0;border-radius:4px;overflow:hidden}
.fhe-bar{position:absolute;left:0;top:0;bottom:0;background:var(--blue);width:0;transition:width .3s}
.fhe-bar.bad{background:var(--red)}
.fhe-lim{position:absolute;right:0;top:0;bottom:0;border-left:2px dashed var(--red)}
.fhe-stats{font:13px var(--mono);display:grid;gap:2px;word-break:break-all}
"""

FHE_JS = r"""
(() => {
  const root = document.getElementById("fhe-bar");
  if (!root) return;
  const P = BigInt(__P__), HALF = P / 2n;
  document.getElementById("fhe-p").textContent = P.toString();
  let c = null, truth = 0, ops = 0;
  const rnd = (lo, hi) => lo + Math.floor(Math.random() * (hi - lo + 1));
  function enc(m) { const q = BigInt(rnd(1000, 9999)), r = BigInt(rnd(-4, 4)); return P * q + 2n * r + BigInt(m); }
  function noise(x) { let r = ((x % P) + P) % P; if (r > HALF) r -= P; return r; }
  function dec(x) { const n = noise(x); return Number(((n % 2n) + 2n) % 2n); }
  function show(msg) {
    const st = document.getElementById("fhe-stats"); st.innerHTML = "";
    if (c === null) { el("div", {}, st, "No ciphertext yet."); document.getElementById("fhe-say").textContent = msg; root.style.width = "0"; return; }
    const n = noise(c);
    // the true noise of the computation: exact, because we track the combined noise term ourselves
    const trusted = (trueNoise < 0n ? -trueNoise : trueNoise) <= HALF, right = dec(c) === truth, ok = trusted && right;
    el("div", {}, st, `ciphertext c = ${c.toString()}  (${c.toString().length} digits)`);
    el("div", {}, st, `c mod p, centred = ${n.toString()}`);
    el("div", {}, st, `the noise the arithmetic carried = ${trueNoise.toString()}`);
    el("div", {}, st, `decrypts to ${dec(c)}; the right answer is ${truth}: ${trusted ? (right ? "OK" : "WRONG") : (right ? "right only by luck: the noise has wrapped" : "WRONG: the noise has wrapped")}`);
    const frac = Math.min(1, Number(trueNoise < 0n ? -trueNoise : trueNoise) / Number(HALF));
    root.style.width = (100 * frac).toFixed(1) + "%";
    root.className = "fhe-bar" + (ok ? "" : " bad");
    document.getElementById("fhe-say").textContent = msg;
  }
  let trueNoise = 0n;
  function fresh(m) { const q = BigInt(rnd(1000, 9999)), r = BigInt(rnd(-4, 4)); return [P * q + 2n * r + BigInt(m), 2n * r + BigInt(m)]; }
  function start(m) { const [x, nz] = fresh(m); c = x; trueNoise = nz; truth = m; ops = 0; show(`Encrypted ${m}. The noise ${nz} is tiny next to p/2 = ${HALF}.`); }
  function add(m) { if (c === null) return start(m); const [x, nz] = fresh(m); c += x; trueNoise += nz; truth ^= m; ops++; show(`Added: the noises add. Bar = |noise| / (p/2).`); }
  function mul(m) { if (c === null) return start(m); const [x, nz] = fresh(m); c *= x; trueNoise *= nz; truth &= m; ops++;
    const big = (trueNoise < 0n ? -trueNoise : trueNoise) > HALF;
    show(big ? `Multiplied: the noises multiply, and now the noise is larger than p/2. Reduction mod p wraps it around, and decryption can no longer be trusted. Bootstrapping would have refreshed it before this.` : `Multiplied: the noises multiply. Try another multiplication.`); }
  document.getElementById("fhe-new0").addEventListener("click", () => start(0));
  document.getElementById("fhe-new1").addEventListener("click", () => start(1));
  document.getElementById("fhe-add0").addEventListener("click", () => add(0));
  document.getElementById("fhe-add1").addEventListener("click", () => add(1));
  document.getElementById("fhe-mul0").addEventListener("click", () => mul(0));
  document.getElementById("fhe-mul1").addEventListener("click", () => mul(1));
  show("Press Encrypt 0 or Encrypt 1.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How fully homomorphic encryption combined older ideas, and where it led")
    W = 210
    nodes = {
        "rsa": (20, 20, "Public-key cryptography", "RSA can multiply ciphertexts, not add them", "Era 6", "ink"),
        "q": (395, 20, "Privacy homomorphisms", "compute on encrypted data?", "Rivest, Adleman, Dertouzos, 1978", "ink"),
        "lat": (770, 20, "Lattices and noise", "hard problems with small errors", "1990s–2005", "ink"),
        "g": (395, 180, "Fully homomorphic encryption", "⊕ bootstrapping: decrypt, encrypted", "Gentry, Stanford, 2009", "red"),
        "int": (20, 340, "Over the integers", "c = pq + 2r + m", "van Dijk, Gentry, Halevi, Vaikuntanathan, 2010", "ink"),
        "gen": (770, 340, "Later generations", "BGV 2011, GSW 2013, CKKS 2016", "", "ink"),
        "kem": (395, 490, "ML-KEM", "the same kind of noisy algebra, for key exchange", "topic 10", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 104, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("rsa", "g", ports=("bottom", "top:0.15"))
    D.edge("q", "g", ports=("bottom", "top"), label="answered", at=0.5, dx=8, anchor="start")
    D.edge("lat", "g", ports=("bottom", "top:0.85"))
    D.edge("g", "int", ports=("bottom:0.15", "top"))
    D.edge("g", "gen", ports=("bottom:0.85", "top"))
    D.edge("g", "kem", ports=("bottom", "top"), label="a relative", at=0.5, dx=8, anchor="start")
    D.text(20, 615, "ML-KEM (topic 10) does not compute on ciphertexts; it shares the idea of hiding a secret under small noise.", "caption")
    return D


def chain(d):
    nz = d["noise"]
    steps = [
        ("To compute on data, someone had to decrypt it and see it",
         "Ciphertexts that can be added and multiplied: c = pq + 2r + m", "somewhat homomorphic"),
        (f"Every multiplication roughly doubles the noise: here it broke at depth {int(nz['deepest'][0]) + 1}",
         "Bootstrapping: run the decryption circuit on an encrypted key, which resets the noise", "Gentry, 2009"),
        ("Bootstrapping was enormously slow at first",
         "Leveled schemes and better noise control in later generations", "BGV 2011, GSW 2013"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: computing on what you cannot read")
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
    s, nz, ad, pk, g, w = d["scheme"], d["noise"], d["adder"], d["public"], d["gcd"], d["widget"]
    lvl_rows = [["fresh", nz["fresh"], "yes"]] + [[k, ("more than " + v[5:]) if v.startswith("over") else v, "no" if f else "yes"] for k, v, f in nz["levels"]]
    deep, est = nz["deepest"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. RSA (Era 6) already let anyone multiply ciphertexts, but never add them. In 1978 Rivest, Adleman and Dertouzos asked for a scheme that does both, without limit. Gentry's answer in 2009 hid each message under a little noise, and added one new idea: when the noise grows too large, decrypt the ciphertext, encrypted, to start again with small noise."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: Gentry's step. Blue: a relative in this era."),
        ]),
        dict(id="play", eyebrow="Try it", title="Add and multiply what you cannot read", toc="Try it", blocks=[
            dict(type="p", text=f"The secret key here is p = {w['p']}. Encrypt a bit, then keep adding and multiplying encrypted bits. The computer that does the arithmetic never needs p. The bar shows the noise against p/2: additions barely move it, but each multiplication multiplies it, and after a couple of products it passes p/2 and decryption fails."),
            dict(type="widget", html=FHE_HTML, js=FHE_JS.replace("__P__", w["p"]), css=FHE_CSS,
                 fallback=dict(type="table", head=["Step", "Ciphertext", "Noise", "Decrypts to"], num=[1, 2, 3],
                               rows=[["a = " + w["a"][0], w["a"][1], fnoise(w["a"][0]), "1"], ["b = " + w["b"][0], w["b"][1], fnoise(w["b"][0]), "1"],
                                     ["a + b", w["sum"][0], w["sum"][1], w["sum"][2]], ["a × b", w["prod"][0], w["prod"][1].replace("-", "−"), w["prod"][2]]]),
                 note="In the interactive edition you can keep adding and multiplying until the noise breaks through."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 9, learning at scale", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="A message hidden under a little noise", toc="How it works", blocks=[
            dict(type="p", text="**Encrypt.** The secret key is a large odd number p. To encrypt a bit m, choose a large random q and a small random r and send c = p·q + 2r + m. To decrypt, take c modulo p, as a number between −p/2 and p/2: what is left is the noise 2r + m, and its last bit is m."),
            dict(type="p", text="**Compute.** Add two ciphertexts and the noises add: (2r₁ + m₁) + (2r₂ + m₂) is odd exactly when m₁ XOR m₂ is 1. Multiply them and the noises multiply: the product is odd exactly when m₁ AND m₂ is 1. XOR and AND are enough to build any circuit, so any computation can run on ciphertexts."),
            dict(type="p", text="**The limit.** As long as the noise stays below p/2, reduction modulo p gives it back exactly. Additions add a bit or so; each multiplication roughly doubles the number of noise bits. Past p/2 the reduction wraps around and the answer is garbage. The scheme is *somewhat* homomorphic."),
            dict(type="p", text="**Bootstrapping.** Gentry's step: give the computer an encryption of the secret key, and let it run the decryption circuit on a noisy ciphertext, homomorphically. The output encrypts the same bit with fresh noise, as long as decryption itself is shallow enough to fit in the noise budget. Then any depth is possible."),
            dict(type="svg", name="noise", draw=noise_svg(d), alt="Noise bits growing with each level of multiplication until they pass p/2", width=760),
            dict(type="callout", kind="key", label="Key idea",
                 text="Noise is what makes the scheme secure, and noise is what limits it. Bootstrapping turns the limit into a refresh: decrypt, but encrypted."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Five hundred bits of key, four levels of products", toc="Measured", blocks=[
            dict(type="p", text=f"**The scheme** with a secret p of {s['p']} bits, q of {s['q']} bits and noise r of {s['r']} bits: ciphertexts of about {s['c']} bits. {int(s['pairs']):,} XOR, AND and NOT combinations of encrypted bits all decrypted correctly."),
            dict(type="p", text=f"**The noise** when ciphertexts of 1 are multiplied in a balanced tree:"),
            dict(type="table", head=["Level", "Noise (bits)", "Decrypts"], num=[1], rows=lvl_rows, hl=len(lvl_rows) - 1),
            dict(type="p", text=f"The deepest working level was {deep}; a rough estimate that doubles the noise bits each level says {est}. Additions are cheap: one addition left {nz['add1']} bits, and a chain of 1,000 additions only {nz['add1000']}."),
            dict(type="p", text=f"**A 4-bit adder** built from XOR and AND gates (ripple carry), run on encrypted inputs: all {ad['pairs']} pairs of 4-bit numbers gave the right sum, with at most {ad['bits']} bits of noise in the last carry, well under {ad['of']}."),
            dict(type="p", text=f"**A public key**: {pk['tau']} encryptions of 0. Anyone can encrypt by adding a random subset of them to m plus a small even number; {pk['n']} such encryptions all decrypted correctly."),
            dict(type="p", text=f"**Why the noise is essential.** Two noise-free multiples of p give away p at once: their gcd had {g['bits']} bits, and removing {g['removed']} small factor{'' if g['removed'] == '1' else 's'} left exactly p. With the noise, the gcd of two encryptions of 0 was {g['g']}. Finding p from noisy multiples is the approximate-gcd problem, on which the scheme's security rests."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="A dissertation, and a paper with only integers", toc="The evidence", blocks=[
            dict(type="p", text="Wikipedia: the problem \"was first proposed in 1978, within a year of publishing of the RSA scheme\"; Gentry \"described the first plausible construction for a fully homomorphic encryption scheme in 2009\"; the noise \"grows as one adds and multiplies ciphertexts\" until it \"makes the resulting ciphertext indecipherable\"; bootstrapping \"effectively 'refreshes' the ciphertext by applying to it the decryption procedure homomorphically\". Gentry's dissertation (Stanford, September 2009, adviser Dan Boneh): \"We propose the first fully homomorphic encryption scheme, solving a central open problem in cryptography.\""),
            dict(type="p", text="van Dijk, Gentry, Halevi and Vaikuntanathan (Cryptology ePrint 2009/616; Eurocrypt 2010): \"a very simple 'somewhat homomorphic' encryption scheme using only elementary modular arithmetic\", made fully homomorphic with Gentry's techniques, and secure if it is hard to find \"a hidden integer\" from \"a list of integers that are near-multiples\" of it. This program follows their scheme, with a secret-key encryption and toy sizes."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Euclid's algorithm, defeated by noise", toc="Full circle", blocks=[
            dict(type="p", text="Euclid's algorithm (Era 1) finds the greatest common divisor of two numbers in a few steps. Applied to two noise-free ciphertexts of 0, it returns the secret key. A little noise, a few bits out of hundreds, is enough to make the gcd useless. Lattice cryptography (topic 10) protects its secrets the same way: linear algebra that would be easy without small errors."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"The gcd of two noise-free multiples of the key gave the key back; with noise, the gcd was {g['g']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            (f"With p = {w['p']}, decrypt c = {w['a'][1]}.", f"{w['a'][1]} mod {w['p']} = {int(w['a'][1]) % int(w['p'])}, which is odd: the bit is 1."),
            ("Why must the noise be even plus the message, 2r + m, and not just r + m?", "So that its last bit is the message: an even number plus m is odd exactly when m is 1."),
            ("Two ciphertexts have noise 5 and −3. What noise does their product have, and what does it decrypt to?", "−15, which is odd: 1 AND 1 = 1."),
            ("Why does a multiplication cost so much more noise than an addition?", "Adding noises of b bits gives at most b + 1 bits; multiplying them gives about 2b bits."),
            ("Why can't the computer doing the arithmetic just read the message?", "It would need p to reduce c; without p, c is a huge number with no visible pattern, and finding p from many ciphertexts is the approximate-gcd problem."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="A Fully Homomorphic Encryption Scheme (2009)", text="Craig Gentry's Stanford dissertation.",
                 draw=C.draw_manuscript, link="https://crypto.stanford.edu/craig/craig-thesis.pdf", link_text="The dissertation (PDF, Stanford Applied Cryptography Group)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "FullyHomomorphic", d["checks"],
                           "every XOR, AND and NOT on encrypted bits, the noise limit, an encrypted adder on all 256 pairs, public-key encryption, and the gcd attack with and without noise.",
                           ["static BigInteger enc(BigInteger p, int m, int qBits, int rBits)", "static BigInteger noise(BigInteger p, BigInteger c)"]),
    ]
    return dict(
        title="Fully Homomorphic Encryption", date="2009–2010",
        description="Era 9, topic 1 of The Algorithm Evolution Atlas: Gentry's fully homomorphic encryption (2009) in its integer form (2010): adding and multiplying encrypted bits, the noise limit, and why bootstrapping was needed.",
        lede="Encrypted data had to be decrypted before anyone could compute with it. In 2009 Gentry showed how to add and multiply ciphertexts without limit: hide each bit under a little noise, and when the noise grows too large, run the decryption itself on encrypted data to refresh it.",
        fieldnote=f"I hid single bits under a {s['p']}-bit key and asked a stranger's arithmetic to add and multiply them. It never saw a bit, and every answer was right, until the fifth level of multiplication, when the noise passed half the key and the answers turned to nonsense. Then I removed the noise from two ciphertexts, and Euclid's algorithm handed me the key.",
        card=[("When", "2009 (Gentry); 2010 (over the integers)"),
              ("Where", "Stanford University"),
              ("What hurt", "Computing on data meant decrypting it"),
              ("The fix", "Noisy ciphertexts that add and multiply; bootstrapping refreshes the noise"),
              ("Checked", f"An encrypted 4-bit adder, all {ad['pairs']} pairs correct")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `FullyHomomorphic.java`.",
    )
