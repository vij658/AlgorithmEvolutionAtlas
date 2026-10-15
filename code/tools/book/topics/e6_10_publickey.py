"""Era 6, topic 10: public-key cryptography. Every number is parsed from PublicKey.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"dh: public prime p of (\d+) bits \(p = 2q \+ 1 with q prime, found after testing ([\d,]+) candidates for q\) and g = (\d+) ; .*? both get the same (\d+)-bit key, beginning ([0-9a-f]+) ; computing g\^a took (\d+) multiplications", ln):
            d["dh"] = dict(bits=m.group(1), tried=m.group(2), g=m.group(3), kbits=m.group(4), key=m.group(5), mults=m.group(6))
        elif ln.startswith("oneway: "):
            d["oneway"] = re.findall(r"(\d+)-bit prime: the power took (\d+) multiplications, the search ([\d,]+)", ln)
        elif m := re.match(r"paper: p = (\d+), q = (\d+), n = (\d+), \(p-1\)\(q-1\) = (\d+), e = (\d+), d = (\d+) .*? ; \"(.*?)\" as two-digit letters .*?, blocks of four: ([\d ]+) ; each block M sent as M\^17 mod 2773: ([\d ]+) ; each received block C turned back by C\^157 mod 2773: \"(.*?)\"", ln):
            d["paper"] = dict(p=m.group(1), q=m.group(2), n=m.group(3), phi=m.group(4), e=m.group(5), d=m.group(6), msg=m.group(7),
                              plain=m.group(8).split(), cipher=m.group(9).split(), back=m.group(10))
        elif m := re.match(r"primes: .*? by the (\d+) Carmichael numbers below ([\d,]+): (.*?), \.\.\. ; .*? checked exhaustively for all ([\d,]+) odd composites below ([\d,]+): at most half the bases ever pass, the largest share being ([\d.]+) for n = ([\d,]+) ; it catches all (\d+) Carmichael numbers", ln):
            d["primes"] = dict(carm=m.group(1), below=m.group(2), first=m.group(3), comps=m.group(4), below2=m.group(5), share=m.group(6), worst=m.group(7), caught=m.group(8))
        elif m := re.match(r"rsa: two random (\d+)-bit primes, found after testing (\d+) and (\d+) odd candidates .*? n = pq has (\d+) bits \((\d+) decimal digits\) ; e = (\d+), .*? ; (\d+) random messages .*? encrypting (\d+), decrypting (\d+)", ln):
            d["rsa"] = dict(pbits=m.group(1), t1=m.group(2), t2=m.group(3), nbits=m.group(4), digits=m.group(5), e=m.group(6), msgs=m.group(7), enc=m.group(8), dec=m.group(9))
        elif ln.startswith("factor: "):
            d["factor"] = re.findall(r"(\d+)-bit n = ([\d,]+): ([\d,]+) trial divisions", ln)
            d["factor_growth"] = re.search(r"multiplied the work by ([\d.]+) on average", ln).group(1)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def dh_svg(d):
    dh = d["dh"]

    def draw(t, standalone):
        o = []
        W, H = 780, 330
        o.append(C.text(20, 24, "Agreeing on a secret key with everyone listening (Diffie and Hellman)", t["ink"], 13, "start", 700))
        o.append(C.rect(20, 50, 220, 210, t["surface"], t["blue"], 1.8, 6))
        o.append(C.rect(540, 50, 220, 210, t["surface"], t["blue"], 1.8, 6))
        o.append(C.rect(290, 50, 200, 210, t["wash"], t["axis"], 1.2, 6))
        o.append(C.text(130, 74, "Alice", t["blue"], 14, "middle", 700))
        o.append(C.text(650, 74, "Bob", t["blue"], 14, "middle", 700))
        o.append(C.text(390, 74, "Public: everyone sees", t["muted"], 12, "middle", 700))
        rows = [("picks a secret a", "p and g", "picks a secret b"),
                ("computes A = g^a mod p", "A  →", "computes B = g^b mod p"),
                ("", "←  B", ""),
                ("key = B^a mod p", "", "key = A^b mod p")]
        for i, (l, mid, r) in enumerate(rows):
            y = 110 + i * 40
            o.append(C.text(130, y, l, t["ink"], 12, "middle"))
            o.append(C.text(390, y, mid, t["ink"], 13, "middle", 700))
            o.append(C.text(650, y, r, t["ink"], 12, "middle"))
        o.append(C.text(390, 250, "an eavesdropper sees p, g, A, B; not a or b", t["red"], 12, "middle", 700))
        o.append(C.text(20, 290, f"Both keys equal g^(ab) mod p. In the program: a {dh['bits']}-bit prime p, g = {dh['g']}; both sides got the same {dh['kbits']}-bit key,", t["muted"], 12))
        o.append(C.text(20, 310, f"beginning {dh['key']}…; each power took {dh['mults']} multiplications. Finding a from A means a discrete logarithm.", t["muted"], 12))
        return C.svg_doc(W, H, "".join(o), "Diffie and Hellman's key exchange", t, standalone, 0.55, 780)
    return draw


PK_HTML = """
<div class="board pk-board">
  <div style="min-width:0">
    <div class="pk-row2">
      <label>Prime p <select id="pk-p"></select></label>
      <label>Prime q <select id="pk-q"></select></label>
    </div>
    <label class="pk-row">Message (letters and spaces) <input type="text" id="pk-msg" maxlength="40"></label>
    <div class="pk-out" id="pk-out"></div>
  </div>
  <div style="min-width:0">
    <div class="pk-keys" id="pk-keys"></div>
    <button type="button" id="pk-break">Break it: factor n</button>
    <p class="say" id="pk-say" aria-live="polite"></p>
  </div>
</div>
"""

PK_CSS = """
.pk-row2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.pk-row2 label,.pk-row{display:grid;gap:2px;font-size:14px;margin:4px 0}
.pk-row2 select,.pk-row input{font:inherit;width:100%}
.pk-out{font:12.5px var(--mono);display:grid;gap:4px;margin-top:8px;word-break:break-all}
.pk-out b{font-family:var(--body)}
.pk-keys{font:13px var(--mono);display:grid;gap:3px;margin-bottom:8px}
"""

PK_JS = r"""
(() => {
  const pSel = document.getElementById("pk-p");
  if (!pSel) return;
  const PAPER = __PAPER__;
  const primes = [];
  for (let n = 31; primes.length < 40; n += 2) { let ok = true; for (let d = 3; d * d <= n; d += 2) if (n % d === 0) { ok = false; break; } if (ok) primes.push(n); }
  [pSel, document.getElementById("pk-q")].forEach((s, k) => primes.forEach(x => { const o = el("option", {value: x}, s, x); if (x === (k ? PAPER.q : PAPER.p)) o.selected = true; }));
  document.getElementById("pk-msg").value = PAPER.msg;
  const gcd = (a, b) => b ? gcd(b, a % b) : a;
  function inverse(e, m) { let [a, b, x0, x1] = [e, m, 1n, 0n]; while (b) { const q = a / b; [a, b] = [b, a - q * b]; [x0, x1] = [x1, x0 - q * x1]; } return ((x0 % m) + m) % m; }
  function pow(b, e, m) { let r = 1n; b %= m; while (e > 0n) { if (e & 1n) r = r * b % m; b = b * b % m; e >>= 1n; } return r; }
  let n, e, d;
  function update() {
    const p = BigInt(pSel.value), q = BigInt(document.getElementById("pk-q").value);
    const say = document.getElementById("pk-say"), out = document.getElementById("pk-out"), keys = document.getElementById("pk-keys");
    out.innerHTML = ""; keys.innerHTML = "";
    if (p === q) { say.textContent = "Choose two different primes."; return; }
    n = p * q; const phi = (p - 1n) * (q - 1n);
    e = 3n; while (gcd(Number(phi), Number(e)) !== 1) e += 2n;
    if (p === BigInt(PAPER.p) && q === BigInt(PAPER.q)) e = BigInt(PAPER.e);
    d = inverse(e, phi);
    el("div", {}, keys, `public key: n = ${n}, e = ${e}`);
    el("div", {}, keys, `private key: d = ${d}`);
    el("div", {}, keys, `check: e × d = ${e * d} = 1 more than a multiple of (p−1)(q−1) = ${phi}`);
    const msg = document.getElementById("pk-msg").value.toUpperCase().replace(/[^A-Z ]/g, "");
    let digits = [...msg].map(c => c === " " ? "00" : String(c.charCodeAt(0) - 64).padStart(2, "0")).join("");
    const w = n > 2626n ? 4 : 2;
    while (digits.length % w) digits += "0";
    const blocks = []; for (let i = 0; i < digits.length; i += w) blocks.push(BigInt(digits.slice(i, i + w)));
    const enc = blocks.map(m => pow(m, e, n)), dec = enc.map(c => pow(c, d, n));
    const text = dec.map(x => x.toString().padStart(w, "0")).join("").match(/../g) || [];
    const back = text.map(t => t === "00" ? " " : String.fromCharCode(64 + +t)).join("").trimEnd();
    el("div", {}, out).innerHTML = `<b>as numbers:</b> ${blocks.map(x => x.toString().padStart(w, "0")).join(" ")}`;
    el("div", {}, out).innerHTML = `<b>sent, M^e mod n:</b> ${enc.map(x => x.toString().padStart(4, "0")).join(" ")}`;
    el("div", {}, out).innerHTML = `<b>received, C^d mod n:</b> ${back}`;
    say.textContent = (p === BigInt(PAPER.p) && q === BigInt(PAPER.q) ? "These are the paper's own numbers. " : "") + "Anyone may encrypt with n and e; only d decrypts.";
  }
  document.getElementById("pk-break").addEventListener("click", () => {
    let k = 0, f = 0n; for (let x = 3n; x * x <= n; x += 2n) { k++; if (n % x === 0n) { f = x; break; } }
    document.getElementById("pk-say").textContent = `Dividing by 3, 5, 7, … found ${f} × ${n / f} after ${k} divisions. From p and q, d follows at once. With the 100-digit primes the RSA paper recommended, there would be about 10^100 divisions to try.`;
  });
  [pSel, document.getElementById("pk-q")].forEach(s => s.addEventListener("change", update));
  document.getElementById("pk-msg").addEventListener("input", update);
  update();
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How public-key cryptography combined older ideas, and where it led")
    W = 210
    nodes = {
        "euc": (20, 20, "Euclid's algorithm", "the inverse d of e, modulo (p−1)(q−1)", "Era 1, topic 7", "ink"),
        "pow": (395, 20, "Powers modulo a prime", "fast to compute, hard to undo", "", "ink"),
        "hard": (770, 20, "Problems believed hard", "factoring, discrete logarithms", "topic 8, in spirit", "ink"),
        "dh": (20, 180, "Key exchange in public", "⊕ g^a, g^b, and g^(ab) for both", "Diffie and Hellman, 1976", "ink"),
        "rsa": (395, 180, "RSA", "⊕ a public key to encrypt, a private one to decrypt", "Rivest, Shamir, Adleman, 1977", "red"),
        "prime": (770, 180, "Probabilistic primality", "random bases that rarely lie", "Solovay and Strassen", "ink"),
        "sig": (395, 340, "Digital signatures", "anyone can check, one person can make", "", "ink"),
        "gchq": (20, 340, "Found first, in secret", "Ellis, Cocks, Williamson", "GCHQ, 1970–1974; revealed 1997", "ink"),
        "today": (395, 490, "Today", "keys agreed in public; signatures anyone can check", "", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo")] + ([(date, "note")] if date else []), color=c)
    D.edge("euc", "rsa", ports=("bottom:0.8", "top:0.15"))
    D.edge("pow", "dh", ports=("bottom:0.2", "top"))
    D.edge("pow", "rsa", ports=("bottom", "top"))
    D.edge("hard", "rsa", ports=("bottom:0.2", "top:0.85"), dashed=True)
    D.edge("prime", "rsa", ports=("left", "right"))
    D.edge("dh", "rsa", ports=("right", "left"), label="the idea", at=0.5, dy=-8)
    D.edge("rsa", "sig", ports=("bottom", "top"))
    D.edge("gchq", "sig", ports=("right", "left"), dashed=True, label="unknown to them", at=0.5, dy=-8)
    D.edge("sig", "today", ports=("bottom", "top"))
    D.text(20, 615, "Dashed: RSA rests on factoring being hard, which is believed, not proved; the GCHQ work stayed secret until 1997.", "caption")
    return D


def chain(d):
    dh, pa, pr, f = d["dh"], d["paper"], d["primes"], d["factor"]
    steps = [
        ("Every cipher needs a secret key shared in advance, by courier or by hand",
         f"Diffie and Hellman: agree on a key in public; here a {dh['kbits']}-bit key, {dh['mults']} multiplications each", "1976"),
        ("Key agreement is not yet encryption, nor a signature",
         f"RSA: publish n and e, keep d; the paper's n = {pa['n']}, e = {pa['e']}, d = {pa['d']}", "1977"),
        (f"Keys need large primes, and Fermat's test is fooled by {pr['carm']} Carmichael numbers below {pr['below']}",
         f"Solovay and Strassen's test: at most half the bases ever lie (worst {pr['share']}, at {pr['worst']})", "recommended in the RSA paper"),
        (f"Everything rests on factoring being slow: {f[-1][2]} divisions for a {f[-1][0]}-bit n",
         "For a 1,024-bit n, about 2^510 divisions; encrypting takes a few dozen multiplications", "a belief, not a proof"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from shared secrets to public keys")
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
    dh, ow, pa, pr, rs, f = d["dh"], d["oneway"], d["paper"], d["primes"], d["rsa"], d["factor"]
    paper_js = '{"p":%s,"q":%s,"e":%s,"msg":"%s"}' % (pa["p"], pa["q"], pa["e"], pa["msg"])
    paper_rows = [[a, b] for a, b in zip(pa["plain"], pa["cipher"])]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Raising numbers to powers modulo a prime is fast; undoing it seems not to be. Diffie and Hellman used that to let two strangers agree on a key in public, and asked for a way to encrypt with a public key. Rivest, Shamir and Adleman found one in the arithmetic of two large primes, with Euclid's algorithm to make the private key and a new probabilistic test to find the primes. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(), caption="Red: RSA. Blue: what public keys made possible."),
        ]),
        dict(id="play", eyebrow="Try it", title="The RSA paper's own example", toc="Try it", blocks=[
            dict(type="p", text=f"The paper worked a small example: p = {pa['p']}, q = {pa['q']}, n = {pa['n']}, e = {pa['e']}, d = {pa['d']}, encoding \"{pa['msg']}\" two digits per letter. Change the primes or the message; the public key (n, e) encrypts, the private key d decrypts. Then break it: with numbers this small, factoring n takes a few divisions."),
            dict(type="widget", html=PK_HTML, js=PK_JS.replace("__PAPER__", paper_js), css=PK_CSS,
                 fallback=dict(type="table", head=["Block M", f"M^{pa['e']} mod {pa['n']}"], num=[0, 1], rows=paper_rows),
                 note=f"In the interactive edition you can encrypt your own message. The table: the program's encryption of \"{pa['msg']}\", block by block."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 6, hard problems and public keys", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Easy one way, hard the other", toc="How it works", blocks=[
            dict(type="p", text="**Powers are fast.** To compute x^e mod n, square and multiply, one bit of e at a time: at most two multiplications per bit, so a few hundred multiplications even for numbers hundreds of digits long. Undoing it, finding e from x^e mod p (a *discrete logarithm*), has no known fast method."),
            dict(type="svg", name="dh", draw=dh_svg(d), alt="Diffie and Hellman's key exchange", width=780),
            dict(type="p", text="**RSA.** Pick two large primes p and q and publish n = pq and a number e. Keep d, the inverse of e modulo (p − 1)(q − 1), found by Euclid's algorithm. Anyone encrypts a block M as C = M^e mod n; the holder of d decrypts M = C^d mod n. Run the other way, the holder of d *signs* (S = M^d mod n) and anyone checks with e. Finding d from n and e seems to require factoring n."),
            dict(type="p", text="**Finding the primes.** Pick random odd numbers and test them. Fermat's test (a^(n−1) = 1 mod n for every prime) is fooled by Carmichael numbers. Solovay and Strassen's test compares a^((n−1)/2) with the Jacobi symbol (a/n): every base passes for a prime, and for a composite at most half do, so 100 random bases mistake a composite for a prime with chance at most 2^−100."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Use a calculation that is easy to do and, as far as anyone knows, hard to undo, with a secret that makes it easy to undo for one person. Then the key that locks can be published, and only the key that unlocks kept secret."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Fast to lock, slow to pick", toc="Measured", blocks=[
            dict(type="p", text=f"**Key exchange.** A {dh['bits']}-bit prime p = 2q + 1 (found after testing {dh['tried']} candidates for q) and g = {dh['g']}: Alice and Bob got the same {dh['kbits']}-bit key, beginning {dh['key']}…, with {dh['mults']} multiplications for each power."),
            dict(type="table", head=["Prime of", "Power by squaring: multiplications", "Logarithm by trying exponents: tries"], num=[0, 1, 2], rows=[[f"{b} bits", m, s] for b, m, s in ow]),
            dict(type="p", text=f"**The paper's example.** \"{pa['msg']}\" as blocks {' '.join(pa['plain'])}; sent as {' '.join(pa['cipher'])}; turned back by C^{pa['d']} mod {pa['n']}: \"{pa['back']}\"."),
            dict(type="p", text=f"**Primality.** Fermat's test is passed, for every base sharing no factor with n, by the {pr['carm']} Carmichael numbers below {pr['below']} ({pr['first']}, …). Solovay and Strassen's test was checked for every base and every odd number below {pr['below2']}: every prime passes; of the {pr['comps']} odd composites, at most half the bases ever pass, the largest share being {pr['share']} for n = {pr['worst']}. It catches all {pr['caught']} Carmichael numbers."),
            dict(type="p", text=f"**A real-sized key.** Two random {rs['pbits']}-bit primes (found after testing {rs['t1']} and {rs['t2']} odd candidates) give an n of {rs['nbits']} bits, {rs['digits']} decimal digits. {rs['msgs']} random messages were encrypted and decrypted, signed and verified, and a signature changed by 1 was always rejected. Average multiplications: encrypting {rs['enc']} (with e = {rs['e']}), decrypting {rs['dec']}."),
            dict(type="table", head=["n (p and q of equal size)", "Trial divisions to factor it"], num=[0, 1], rows=[[f"{b}-bit {n}", k] for b, n, k in f]),
            dict(type="p", text=f"Each 8 more bits multiplied the work by {d['factor_growth']} on average. For the {rs['nbits']}-bit n, trial division would need about 2^510 divisions. Faster factoring methods than trial division exist; this one only shows how the work grows with the size."),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Stanford, MIT, and a secret kept by GCHQ", toc="The evidence", blocks=[
            dict(type="p", text="Diffie and Hellman, \"New Directions in Cryptography\" (Stanford University; *IEEE Transactions on Information Theory* IT-22(6): 644–654, November 1976), opens: \"We stand today on the brink of a revolution in cryptography.\" It proposes public key cryptosystems, key exchange by exponentiation modulo a prime, and a digital equivalent of a signature, \"a digital phenomenon with the same properties as a written signature\"; it notes that \"Merkle [1] has independently studied the problem\" of distributing keys over an insecure channel."),
            dict(type="p", text="Rivest, Shamir and Adleman (MIT; received 4 April 1977; *Communications of the ACM* 21: 120–126, 1978) give C ≡ M^e (mod n) and M ≡ C^d (mod n), recommend \"100-digit (decimal) prime numbers p and q\", recommend \"the elegant 'probabilistic' algorithm due to Solovay and Strassen\" for finding them, work the example with p = 47 and q = 59, credit public keys to \"an elegant concept invented by Diffie and Hellman\", and end with a dare: \"The reader is challenged to find a way to 'break' our method.\""),
            dict(type="p", text="On 1 December 1997 GCHQ, the British signals agency, released a document claiming the invention years earlier (Bruce Schneier, 1998): James Ellis's idea of \"non-secret encryption\" (a report of January 1970; the sources give 1960, 1969 and 1970 for the idea itself, and the catalog marks the date as disputed), Clifford Cocks's 1973 note describing \"what was essentially RSA\", and Malcolm Williamson's 1974 method \"remarkably similar to Diffie-Hellman\". Ellis died on 25 November 1997, a month before the announcement. Schneier's verdict: \"while they may have discovered the mathematics, it is clear that they never understood its significance.\""),
        ]),
        dict(id="circle", eyebrow="Full circle", title="Euclid holds the key", toc="Full circle", blocks=[
            dict(type="p", text="The private key d is the inverse of e modulo (p − 1)(q − 1), and it is found by extending Euclid's algorithm (Era 1, topic 7), two thousand years old. The ciphers that frequency analysis broke (Era 2, topic 7) and the Enigma that the Bombe broke (Era 4, topic 8) both needed a key shared in advance; public keys do not. And the hardness they rely on is of the kind topic 8 describes, believed but not proved."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"In the paper's example, Euclid's algorithm turns e = {pa['e']} into d = {pa['d']}, because {pa['e']} × {pa['d']} is 1 more than a multiple of {pa['phi']}."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("With p = 5, q = 11, e = 3: what are n, (p − 1)(q − 1) and d?", "n = 55, (p − 1)(q − 1) = 40, d = 27, since 3 × 27 = 81 = 2 × 40 + 1."),
            ("Encrypt M = 2 with n = 55, e = 3, then decrypt.", "C = 2³ mod 55 = 8; 8²⁷ mod 55 = 2."),
            ("Why may e be public but not d?", "From e and n alone, finding d seems to need p and q, that is, factoring n; with d, anyone could decrypt."),
            ("Why does a signature made with d prove who made it?", "Only the holder of d could produce S with S^e mod n = M; anyone can check that with the public e."),
            ("Why is 561 dangerous for Fermat's test?", "It is composite (3 × 11 × 17), yet a^560 = 1 mod 561 for every a sharing no factor with it."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="New Directions in Cryptography (1976)", text="Diffie and Hellman's paper, on Hellman's Stanford page.",
                 draw=C.draw_manuscript, link="https://ee.stanford.edu/~hellman/publications/24.pdf", link_text="The paper (PDF)", licence="Drawn placeholder."),
            dict(title="A Method for Obtaining Digital Signatures and Public-Key Cryptosystems (1978)", text="The RSA paper, with its worked example and its challenge.",
                 draw=C.draw_manuscript, link="https://people.csail.mit.edu/vinodv/COURSES/MAT302-S13/RSApaper.pdf", link_text="The paper (PDF, on an MIT course page)", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "PublicKey", d["checks"],
                           "a Diffie-Hellman exchange, discrete logarithms by search for growing primes, the RSA paper's example, Solovay and Strassen's test against every base for every odd number below 3,000, Carmichael numbers below 100,000, a 1,024-bit key with 100 round trips and signatures, and factoring by trial division.",
                           ["static BigInteger power(BigInteger x, BigInteger e, BigInteger m)", "static boolean solovayStrassen(long n, long a)"]),
    ]
    return dict(
        title="Public-Key Cryptography", date="1976–1977",
        description="Era 6, topic 10 of The Algorithm Evolution Atlas: Diffie and Hellman's key exchange, RSA with the paper's own example, Solovay and Strassen's primality test, and the secret history at GCHQ.",
        lede="Every cipher the species had used needed a secret key shared in advance. Diffie and Hellman showed how strangers could agree on one in public; Rivest, Shamir and Adleman made a key that locks but cannot unlock.",
        fieldnote=f"I ran the RSA paper's own example and got its message back. Then I made a key of {rs['digits']} digits from two random primes: encrypting took {rs['enc']} multiplications, and picking the lock by trial division would take about 2^510. The secret is safe for exactly as long as nobody finds a fast way to factor.",
        card=[("When", "Diffie and Hellman 1976; RSA 1977 (GCHQ in secret, 1970–1974)"),
              ("Where", "Stanford; MIT"),
              ("What hurt", "Every cipher needed a key shared in advance"),
              ("The fix", "A public key to encrypt, a private key to decrypt"),
              ("Rests on", "Factoring and discrete logarithms being slow")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `PublicKey.java`.",
    )
