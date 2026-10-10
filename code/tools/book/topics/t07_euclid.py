"""Era 1, topic 7: Euclid's algorithm."""
import pathlib
import re

import common as C
import t07_euclid_diagrams as ED

HERE = pathlib.Path(__file__).resolve().parent


def parse(text: str) -> dict:
    d = {"trace": {}, "extended": [], "compare": [], "worst": [], "average": [], "exhaustive": []}
    for ln in text.splitlines():
        if m := re.match(r"trace (\d+) (\d+): (\d+) = (\d+) x (\d+) \+ (\d+)$", ln):
            d["trace"].setdefault(f"{m.group(1)},{m.group(2)}", []).append([int(m.group(i)) for i in range(3, 7)])
        elif m := re.match(r"quotients (\d+)/(\d+) = \[(.+)\]", ln):
            d["quotients"] = [int(x) for x in re.split(r"[;,]\s*", m.group(3))]
        elif m := re.match(r"extended \d+ \d+: q=(-?\d+) r=(-?\d+) s=(-?\d+) t=(-?\d+)$", ln):
            d["extended"].append([int(m.group(i)) for i in range(1, 5)])
        elif m := re.match(r"bezout (\d+) (\d+): (\d+) = (-?\d+) x \d+ \+ (-?\d+) x \d+$", ln):
            d["bezout"] = dict(a=int(m.group(1)), b=int(m.group(2)), g=int(m.group(3)), x=int(m.group(4)), y=int(m.group(5)))
        elif m := re.match(r"compare (\d+) (\d+): gcd=(\d+) trying=(\d+) subtracting=(\d+) dividing=(\d+) binary=(\d+)$", ln):
            d["compare"].append(dict(zip(["a", "b", "gcd", "trying", "subtracting", "dividing", "binary"], map(int, m.groups()))))
        elif m := re.match(r"exhaustive below (\d+): most steps (\d+) at \((\d+), (\d+)\)$", ln):
            d["exhaustive"].append(dict(limit=int(m.group(1)), steps=int(m.group(2)), a=int(m.group(3)), b=int(m.group(4))))
        elif m := re.match(r"worst digits=(\d+): \((\d+), (\d+)\) steps=(\d+) lame=(\d+)$", ln):
            d["worst"].append(dict(digits=int(m.group(1)), a=int(m.group(2)), b=int(m.group(3)), steps=int(m.group(4)), lame=int(m.group(5))))
        elif m := re.match(r"average digits=(\d+): ([\d.]+) steps over (\d+) random pairs$", ln):
            d["average"].append(dict(digits=int(m.group(1)), mean=float(m.group(2))))
            d["samples"] = int(m.group(3))
        elif m := re.match(r"slope: ([\d.]+) more steps per extra digit .*= ([\d.]+)$", ln):
            d["slope"], d["slope_predicted"] = float(m.group(1)), float(m.group(2))
        elif m := re.match(r"histogram 18 digits \((\d+) random pairs\): (.+)$", ln):
            d["hist_samples"] = int(m.group(1))
            d["histogram"] = [[int(a), int(b)] for a, b in (p.split(":") for p in m.group(2).split())]
        elif m := re.match(r"rsa: e=(\d+), phi=(\d+), d=(\d+)", ln):
            d["rsa"] = dict(e=int(m.group(1)), phi=int(m.group(2)), d=int(m.group(3)))
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def squares(a, b):
    """The squares cut from an a-by-b rectangle, stage by stage: a list of stages, each a list of (x, y, side)."""
    x0, y0, w, h = 0, 0, a, b
    stages = []
    while w and h:
        s = min(w, h)
        n = max(w, h) // s
        stages.append([(x0 + i * s, y0, s) if w >= h else (x0, y0 + i * s, s) for i in range(n)])
        if w >= h:
            x0, w = x0 + n * s, w - n * s
        else:
            y0, h = y0 + n * s, h - n * s
    return stages


def strip_figure(a, b, trace):
    def draw(t, standalone):
        stages = squares(a, b)
        colors = [(t["red"], t["on_red"]), (t["yellow"], t["on_yellow"]), (t["blue"], t["on_blue"])]
        pw, gap, top = 228, 24, 28
        n_panels = len(stages) + 1
        W = n_panels * pw + (n_panels - 1) * gap
        scale = (pw - 8) / a
        rh = b * scale
        H = top + rh + 96
        out = []
        caps = [(f"A {a} × {b} rectangle", "Find the largest square tile that", "fits both sides exactly.")]
        for (big, q, small, r) in trace:
            caps.append((f"{big} = {q} × {small} + {r}",
                         f"Cut {q} square{'s' if q > 1 else ''} of side {small}." if r else f"{q} squares of side {small} fill it.",
                         f"A {small} × {r} piece is left." if r else "Nothing is left: done."))
        last = stages[-1]
        lx = min(s[0] for s in last); ly = min(s[1] for s in last)
        lw = max(s[0] + s[2] for s in last) - lx; lh = max(s[1] + s[2] for s in last) - ly
        zoom = min((pw - 8) / lw, rh / lh) / scale
        for p in range(n_panels):
            ox = p * (pw + gap) + 4
            if not (p == n_panels - 1 and zoom > 1.5):
                out.append(C.rect(ox, top, a * scale, rh, t["wash"], t["ink"]))
                for k in range(min(p, len(stages))):
                    fill, on = colors[k % 3]
                    for (x, y, s) in stages[k]:
                        out.append(C.rect(ox + x * scale, top + y * scale, s * scale, s * scale, fill, t["surface"]))
                        if s * scale >= 26:
                            out.append(C.text(ox + (x + s / 2) * scale, top + (y + s / 2) * scale + 5, s, on, 12 if s * scale < 34 else 13, "middle", 600))
                if p == n_panels - 2 and zoom > 1.5:
                    out.append(C.rect(ox + lx * scale - 3, top + ly * scale - 3, lw * scale + 6, lh * scale + 6, "none", t["ink"]))
                out.append(C.text(ox, top - 10, "the problem" if p == 0 else f"step {p}", t["muted"], 12))
            else:
                zs = scale * zoom
                zx, zy = ox, top + (rh - lh * zs) / 2
                fill, on = colors[(len(stages) - 1) % 3]
                for (x, y, s) in last:
                    out.append(C.rect(zx + (x - lx) * zs, zy + (y - ly) * zs, s * zs, s * zs, fill, t["surface"]))
                    if s * zs >= 26:
                        out.append(C.text(zx + (x - lx + s / 2) * zs, zy + (y - ly + s / 2) * zs + 5, s, on, 12, "middle", 600))
                out.append(C.text(ox, top - 10, f"step {p} · zoomed in ×{zoom:.1f}", t["muted"], 12))
            c1, c2, c3 = caps[p]
            out.append(C.text(ox, top + rh + 26, c1, t["ink"], 14, "start", 650))
            out.append(C.text(ox, top + rh + 46, c2, t["ink2"], 13))
            out.append(C.text(ox, top + rh + 64, c3, t["ink2"], 13))
        return C.svg_doc(W, H, "".join(out), f"Euclid's algorithm on {a} and {b} drawn as squares cut from a rectangle", t, standalone)
    return draw


def segments_figure(t, standalone):
    W, H, u = 560, 160, 0.42
    out = []
    def seg(y, length, color, l1, l2, label):
        out.append(C.line(40, y, 40 + length * u, y, color, 7))
        out.append(C.text(30, y + 5, l1, t["ink"], 15, "end", 700))
        out.append(C.text(50 + length * u, y + 5, l2, t["ink"], 15, "start", 700))
        out.append(C.text(40 + length * u / 2, y - 12, label, t["ink2"], 12.5, "middle"))
    seg(40, 1071, t["red"], "A", "B", "AB = 1071")
    seg(96, 462, t["blue"], "C", "D", "CD = 462")
    for i in range(2):
        out.append(C.line(40 + i * 462 * u, 140, 40 + (i + 1) * 462 * u - 3, 140, t["blue"], 7))
    out.append(C.line(40 + 924 * u, 140, 40 + 1071 * u, 140, t["yellow"], 7))
    return C.svg_doc(W, H, "".join(out), "Numbers as line segments: CD measured off along AB twice leaves 147", t, standalone, 0.5, 600)


# ----------------------------------------------------------------------------------------------------------------------
def build(ctx):
    d = parse(ctx["out"])
    A, B = 1071, 462
    trace = d["trace"][f"{A},{B}"]
    g = trace[-1][2]
    cmp = {(c["a"], c["b"]): c for c in d["compare"]}
    big, ex = cmp[(1000000, 1)], cmp[(A, B)]
    bz, rsa = d["bezout"], d["rsa"]
    small = d["trace"]["48,18"]
    ex100 = next(e for e in d["exhaustive"] if e["limit"] == 100)
    diags = ED.build(d)
    avg = {a["digits"]: a["mean"] for a in d["average"]}
    label = lambda c: {(1071, 462): "the worked example", (89, 55): "consecutive Fibonacci numbers", (1000000, 1): "a huge and a tiny number"}.get(
        (c["a"], c["b"]), "10-digit consecutive Fibonacci numbers" if c["gcd"] == 1 and c["subtracting"] - c["dividing"] <= 2 else "a random 18-digit pair")
    board_html = (HERE / "t07_euclid.board.html").read_text()
    board_js = (HERE / "t07_euclid.board.js").read_text()
    signed = lambda s, t: f"{s} × {A} {'−' if t < 0 else '+'} {abs(t)} × {B}"

    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. This is the map of the topic: where Euclid's algorithm came from, and what grew out of it. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=diags["family"],
                 caption="Red: the algorithm and its best-known descendants. Blue: the mathematical steps in between. The dashed line is a relationship rather than a descendant: Euclid's quotients are exactly the terms of a continued fraction."),
        ]),
        dict(id="board", eyebrow="Try it", title="Two numbers are the sides of a rectangle", toc="Try it", blocks=[
            dict(type="p", text="Cut off the biggest square that fits, as many times as it fits, then do the same to the piece that is left. When a piece is filled exactly, the side of its squares is the greatest common divisor."),
            dict(type="widget", html=board_html, js=board_js,
                 fallback=dict(type="svg", name="euclid-squares", draw=strip_figure(A, B, trace),
                               alt=f"Euclid's algorithm on {A} and {B} as squares cut from a rectangle"),
                 note="In the interactive edition you can type your own numbers and cut them stage by stage."),
            dict(type="p", text=f"The number of squares cut at each stage, **{', '.join(map(str, d['quotients']))}**, is also the continued fraction "
                                f"{A}/{B} = [{d['quotients'][0]}; {', '.join(map(str, d['quotients'][1:]))}]. Every Euclid computation hides one."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 1, the first algorithms", toc="Timeline", blocks=[C.era_timeline_block(ctx["index"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=diags["chain"], caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="steps", eyebrow="Step by step", title=f"{A} and {B}, by hand", toc="Step by step", blocks=[
            dict(type="table", head=["Step", "Division", "Quotient (squares cut)", "Remainder"], num=[0, 2, 3], hl=len(trace) - 2,
                 rows=[[i + 1, f"{bg:,} = {q} × {sm:,} + {r:,}", q, f"{r:,}"] for i, (bg, q, sm, r) in enumerate(trace)]),
            dict(type="p", text=f"The last non-zero remainder, **{g}**, is gcd({A}, {B}). Euclid himself drew numbers as line segments and measured one off along the other:"),
            dict(type="svg", name="segments", draw=segments_figure, alt="Numbers as line segments",
                 caption="Drawn for this book in the style of Euclid's Elements, not copied from a manuscript.", width=560),
            dict(type="callout", kind="wrong", label="Wrong turn",
                 text=f"Euclid subtracted one copy at a time. That is fine for {A} and {B} ({ex['subtracting']} subtractions), but {big['a']:,} and {big['b']} need "
                      f"**{big['subtracting']:,} subtractions** where one division is enough. Division is subtraction done in bulk."),
            dict(type="p", text=f"**Going backwards: the pulverizer.** Run the steps in reverse and every remainder becomes a combination of the two starting numbers. "
                                f"Each row keeps the promise *remainder = s × {A} + t × {B}*. Aryabhata (499 CE) called the method *kuttaka*, \"pulverizing\", because the numbers get smaller with every step."),
            dict(type="table", head=["Row", "Quotient", "Remainder", "s", "t", "Check"], num=[0, 1, 2, 3, 4], hl=len(d["extended"]) - 2,
                 rows=[[i, "—" if i < 2 else q, f"{r:,}", s, t, f"{signed(s, t)} = {s * A + t * B:,}"] for i, (q, r, s, t) in enumerate(d["extended"])]),
            dict(type="callout", kind="key", label="Key idea",
                 text=f"**{bz['g']} = {bz['x']} × {A} + {bz['y']} × {B}** (Bézout's identity). When the gcd is 1, the s column gives the inverse of one number modulo the other, "
                      f"which is how RSA key generation finds its matching exponent: {rsa['e']} × {rsa['d']:,} = 1 (mod {rsa['phi']:,})."),
        ]),
        dict(id="four", eyebrow="Before and after", title="Four ways to find a gcd", toc="Four ways", blocks=[
            dict(type="p", text="Each method keeps the goal and changes one thing. The counts of basic operations come from the program."),
            dict(type="diagram", name="four", diagram=diags["four"]),
            dict(type="table", head=["Pair", "gcd", "Trying every candidate", "Subtracting (Euclid)", "Dividing", "Binary (Stein)"], num=[1, 2, 3, 4, 5],
                 rows=[[f"{c['a']:,} and {c['b']:,} ({label(c)})", c["gcd"], f"{c['trying']:,}", f"{c['subtracting']:,}", f"**{c['dividing']}**", c["binary"]] for c in d["compare"]]),
        ]),
        dict(id="measured", eyebrow="Measured", title="How fast is it?", toc="Measured", blocks=[
            dict(type="p", text="**The worst case.** Consecutive Fibonacci numbers make the algorithm work hardest: almost every quotient is 1, so each step takes away as little as possible."),
            dict(type="diagram", name="ladder", diagram=diags["ladder"]),
            dict(type="p", text="Lamé proved in 1844 that the steps never exceed five times the number of digits of the smaller number. The worst cases sit exactly at that limit for small numbers and just below it after that."),
            dict(type="diagram", name="lame", diagram=diags["lame"]),
            dict(type="p", text="**The average.** Random numbers are much kinder. Each extra digit adds about two steps, as Heilbronn's formula predicts."),
            dict(type="diagram", name="growth", diagram=diags["growth"]),
            dict(type="p", text="**The spread.** For random 18-digit pairs the counts bunch tightly around the middle."),
            dict(type="diagram", name="split", diagram=diags["split"]),
            dict(type="details", summary="Show the numbers", block=dict(type="table",
                 head=["Digits", "Worst-case pair (consecutive Fibonacci)", "Steps", "Lamé's limit", "Average, random pairs"], num=[0, 2, 3, 4],
                 rows=[[w["digits"], f"{w['a']:,} and {w['b']:,}", w["steps"], w["lame"], f"{avg[w['digits']]:.3f}"] for w in d["worst"]])),
        ]),
        dict(id="circle", eyebrow="Full circle", title="An algorithm from 300 BCE finds weak locks in 2012", toc="Full circle", blocks=[
            dict(type="callout", kind="circle", label="Full circle",
                 text="A team from UC San Diego and the University of Michigan collected the public keys of millions of internet hosts and computed greatest common divisors between them. "
                      "Keys made with poor randomness can share a prime factor, and a shared factor gives the private key away. They recovered RSA private keys for **0.50% of TLS hosts** "
                      "and **0.03% of SSH hosts** (Heninger, Durumeric, Wustrow and Halderman, *Mining Your Ps and Qs*, USENIX Security 2012; [factorable.net](https://factorable.net/))."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Find gcd(48, 18). How many divisions does it take?",
             "<br>".join(f"{a} = {q} × {b} + {r}" for a, q, b, r in small) + f"<br>So gcd(48, 18) = **{small[-1][2]}**, in **{len(small)}** divisions."),
            ("Why must the algorithm stop?",
             "Each remainder is smaller than the number it was divided by, so the second number of the pair gets strictly smaller at every step. Whole numbers cannot keep getting smaller forever, so it reaches 0."),
            ("Which pair of numbers below 100 makes it work hardest?",
             f"**({ex100['a']}, {ex100['b']})**, two consecutive Fibonacci numbers, with **{ex100['steps']}** divisions. The program checked every pair below 100."),
            (f"Write {bz['g']} as a combination of {A} and {B}.",
             f"{bz['g']} = **{bz['x']}** × {A} + **{bz['y']}** × {B}. Check: {bz['x'] * A:,} + {bz['y'] * B:,} = {bz['g']}."),
            ("Is gcd(1,000,000, 1) faster by subtraction or by division?",
             f"Division: **{big['dividing']}** step against **{big['subtracting']:,}** subtractions."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="The first printed edition", text="Printed by Erhard Ratdolt, Venice, 25 May 1482.",
                 photo="https://library.si.edu/sites/default/files/books/covers/preclarissimusl00eucl_cover.jpg", draw=C.draw_book,
                 link="https://library.si.edu/digital-library/book/preclarissimusl00eucl", link_text="Smithsonian Libraries' digitised copy",
                 licence="Photo: Smithsonian Libraries, CC0 (public domain)"),
            dict(title="MS. D'Orville 301, Bodleian Library", text="A Byzantine manuscript of the *Elements*, dated 888, written by Stephanos the clerk.",
                 draw=lambda t, s: C.draw_manuscript(t, s, "888"), link="https://medieval.bodleian.ox.ac.uk/catalog/manuscript_4146", link_text="Catalogue entry and digital facsimile",
                 licence="Drawn placeholder. Most Digital Bodleian images are CC BY-NC 4.0, so the photographs are linked, not copied."),
            dict(title="P. Oxy. 29, Penn Museum E2748", text="A papyrus fragment of Book II, Proposition 5, with its diagram. Dated 200–400 CE by the museum, 75–125 CE by the papyrologist Eric Turner (**disputed**).",
                 draw=C.draw_papyrus, link="https://collections.penn.museum/collections/object/63505", link_text="Penn Museum record",
                 licence="Drawn placeholder; no image licence is stated, so the photographs are linked."),
        ])]),
        C.links_section(ctx, extra=[
            ("scholar", "Aryabhata I", "MacTutor History of Mathematics", "https://mathshistory.st-andrews.ac.uk/Biographies/Aryabhata_I/", "The kuttaka and its link to Euclid's algorithm"),
            ("scholar", "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems", "Rivest, Shamir and Adleman (1977)", "https://people.csail.mit.edu/rivest/Rsapaper.pdf", "RSA computes its exponents with \"a variation of Euclid's algorithm\""),
        ]),
        C.prove_it_section(ctx, "EuclidsAlgorithm", d["checks"],
                           "every method against Java's `BigInteger.gcd`, Bézout's identity on 200,000 random pairs, Lamé's bound for every pair below 1,000, and every continued fraction rebuilt exactly.",
                           ["static long gcd(long a, long b)", "static List<long[]> extendedRows(long a, long b)"]),
    ]
    return dict(
        title="Euclid's Algorithm", date="c. 300 BCE",
        description="Era 1, topic 7 of The Algorithm Evolution Atlas: Euclid's algorithm as a rectangle you can cut step by step, with its history, diagrams and verified links.",
        lede="The oldest procedure still in daily use. Cut the biggest square off a rectangle, again and again; the last square measures both sides.",
        fieldnote="Earlier procedures computed a value. This one stops on its own and is proved to work for every pair of numbers. Twenty-three centuries later it still runs, in spirit unchanged, inside every encryption library.",
        card=[("When", "c. 300 BCE (earlier origins: **conjecture**)"), ("Where", "Alexandria · *Elements*, Book VII, Props. 1–2 (**documented**)"),
              ("What hurt", "Finding a common measure meant trying every candidate"), ("The fix", "Replace (a, b) by (b, a mod b) until the remainder is 0"),
              ("Cost", "At most 5 × the digits of the smaller number (Lamé, 1844)"), ("Atlas", "Ch. 4 The Euclidean Algorithm · Ch. 92 Number Theory")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `EuclidsAlgorithm.java`; the drawings are made for this book in the style of Byrne's 1847 coloured edition of the *Elements*.",
    )
