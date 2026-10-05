"""The box-and-arrow diagrams for Era 1, topic 7 (Euclid's algorithm). Every number comes from the parsed program output."""
from diagrams import Diagram


def fmt(n):
    return f"{n:,}"


def family():
    D = Diagram(1000, 690, "How Euclid's algorithm combined with other ideas, from repeated subtraction to RSA and the 2012 weak-key hunt")
    W, H = 180, 70
    nodes = {
        "sub": (410, 20, "Repeated subtraction", "", "anthyphairesis", "ink"),
        "euc": (410, 150, "Euclid's algorithm", "⊕ division", "c. 300 BCE", "red"),
        "ext": (20, 300, "Extended Euclid", "⊕ carry the steps back", "Aryabhata, 499 CE", "blue"),
        "lam": (215, 300, "Lamé's bound", "⊕ Fibonacci numbers", "1844", "blue"),
        "key": (410, 300, "Weak-key hunt", "⊕ millions of public keys", "2012", "red"),
        "bin": (605, 300, "Binary GCD", "⊕ halving", "Stein, 1967", "blue"),
        "cf": (800, 300, "Continued fractions", "same quotients", "", "ink"),
        "inv": (20, 450, "Modular inverse", "⊕ arithmetic mod n", "", "blue"),
        "egy": (410, 450, "Egyptian doubling", "", "topic 5, c. 1550 BCE", "ink"),
        "sqm": (410, 590, "Square-and-multiply", "⊕ squaring", "", "ink"),
        "rsa": (20, 590, "RSA", "⊕ fast powers", "1977", "red"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        lines = [(t, "title")] + ([(combo, "combo")] if combo else []) + ([(date, "note")] if date else [])
        D.node(k, x, y, W, H, lines, color=c)
    for a, b in [("sub", "euc"), ("euc", "ext"), ("euc", "lam"), ("euc", "key"), ("euc", "bin"), ("ext", "inv"), ("inv", "rsa"), ("egy", "sqm"), ("sqm", "rsa")]:
        D.edge(a, b)
    D.edge("euc", "cf", dashed=True)
    return D


def chain(d):
    big = next(c for c in d["compare"] if (c["a"], c["b"]) == (1000000, 1))
    steps = [
        ("Try every candidate until one divides both numbers", "Take the smaller from the larger, again and again", "Elements VII, c. 300 BCE"),
        (f"{fmt(big['a'])} and {big['b']} need {fmt(big['subtracting'])} subtractions", "One division does a whole run of subtractions: a mod b", ""),
        ("Knowing the gcd is not enough: find x, y with ax + by = gcd", "Carry the steps back", "Aryabhata's kuttaka, the pulverizer, 499 CE"),
        ("How slow can it get?", "Never more than 5 × the digits of the smaller number", "Lamé, 1844 (others had partial results first)"),
        ("Division is costly in hardware", "Halving and subtraction only", "Stein, 1967; a halving rule appears in China's Nine Chapters"),
    ]
    rowh, gap = 84, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from trying every candidate to the binary GCD")
    L, R, bw = 20, 560, 380
    for i, (pain, fix, src) in enumerate(steps):
        y = 20 + i * (rowh + gap)
        px, fx = (L, R) if i % 2 == 0 else (R, L)          # rows alternate direction, so each new pain sits under the fix that caused it
        D.node(f"p{i}", px, y, bw, rowh, [("WHAT HURT", "tag"), (pain, "combo")], color="red")
        D.node(f"f{i}", fx, y, bw, rowh, [("THE FIX", "tag"), (fix, "combo")] + ([(src, "note")] if src else []), color="blue")
        D.edge(f"p{i}", f"f{i}", ports=("right", "left") if i % 2 == 0 else ("left", "right"), label="fixed by", at=0.5, dy=-8)
        if i + 1 < len(steps):
            D.edge(f"f{i}", f"p{i + 1}", ports=("bottom", "top"), label="which leaves a new problem" if i == 0 else None,
                   at=0.5, dx=12, dy=5, anchor="start")
    return D


def four(d):
    cmp = {(c["a"], c["b"]): c for c in d["compare"]}
    ex, big = cmp[(1071, 462)], cmp[(1000000, 1)]
    rows = [
        ("Try every candidate", "count down from the smaller number until one divides both",
         f"1071 and 462: {fmt(ex['trying'])} tries · 1,000,000 and 1: {fmt(big['trying'])}", "the size of the numbers", "ink"),
        ("Repeated subtraction (Euclid)", "take the smaller from the larger",
         f"1071 and 462: {fmt(ex['subtracting'])} subtractions · 1,000,000 and 1: {fmt(big['subtracting'])}", "the size of the quotients", "red"),
        ("Division", "replace (a, b) by (b, a mod b)",
         f"1071 and 462: {fmt(ex['dividing'])} divisions · 1,000,000 and 1: {fmt(big['dividing'])}", "the number of digits", "blue"),
        ("Binary GCD (Stein, 1967)", "halve away factors of 2, then subtract",
         f"1071 and 462: {fmt(ex['binary'])} rounds · 1,000,000 and 1: {fmt(big['binary'])}", "the number of bits; no division at all", "blue"),
    ]
    combos = ["⊕ subtract instead of testing", "⊕ do the subtractions in bulk", "⊕ halve instead of dividing"]
    bh, gap = 104, 44
    D = Diagram(800, 20 + 4 * (bh + gap) - gap + 20, "Four ways to find a gcd, each built from the one before, with the work each needs")
    for i, (t, how, counts, grows, c) in enumerate(rows):
        y = 20 + i * (bh + gap)
        D.node(f"m{i}", 20, y, 430, bh, [(t, "title"), (how, "note"), (counts, "combo")], color=c)
        D.text(480, y + bh / 2 - 6, "WORK GROWS WITH", "tag")
        D.text(480, y + bh / 2 + 14, grows, "combo")
        if i < 3:
            D.edge(f"m{i}", f"m{i + 1}", ports=("bottom", "top"), label=combos[i], at=0.5, dx=14, dy=5, anchor="start")
    return D


def ladder(d):
    tr = d["trace"]["89,55"]
    pairs = [(r[0], r[2]) for r in tr] + [(tr[-1][2], tr[-1][3])]
    qs = [r[1] for r in tr]
    D = Diagram(800, 300, f"The slowest pair below 100: {pairs[0][0]} and {pairs[0][1]} take {len(tr)} divisions, because almost every quotient is 1")
    w, h, gap = 110, 60, 52
    pos = []
    for i in range(len(pairs)):
        row, col = divmod(i, 5)
        x = 20 + (col if row == 0 else 4 - col) * (w + gap)
        pos.append((x, 30 + row * 140))
    for i, ((a, b), (x, y)) in enumerate(zip(pairs, pos)):
        last = i == len(pairs) - 1
        D.node(f"s{i}", x, y, w, h, [(f"{a} and {b}", "title"), ("gcd = " + str(a) if last else f"pair {i + 1}", "note")],
               color="red" if last else ("blue" if i == 0 else "ink"))
    for i in range(len(pairs) - 1):
        same_row = (i // 5) == ((i + 1) // 5)
        if same_row:
            side = ("right", "left") if i < 5 else ("left", "right")
            D.edge(f"s{i}", f"s{i + 1}", ports=side, label=f"q = {qs[i]}", at=0.5, dy=-9)
        else:
            D.edge(f"s{i}", f"s{i + 1}", ports=("bottom", "top"), label=f"q = {qs[i]}", at=0.5, dx=10, dy=5, anchor="start")
    D.text(20, 276, f"Each arrow is one division; q is the quotient. With q = 1 almost every time, each step takes away as little as possible.", "caption")
    return D


def lame(d):
    picks = [w for w in d["worst"] if w["digits"] in (1, 3, 6, 9, 12, 15, 18)]
    D = Diagram(800, 190, "The worst case against Lamé's limit of 5 steps per digit: it reaches the limit up to 3 digits and stays just below it after that")
    w, gap = 100, 10
    for i, p in enumerate(picks):
        at_limit = p["steps"] == p["lame"]
        D.node(f"l{i}", 20 + i * (w + gap), 20, w, 110,
               [(f"{p['digits']} DIGIT{'S' if p['digits'] > 1 else ''}", "tag"), (f"{p['steps']} steps", "title"),
                (f"limit {p['lame']}", "note"), ("at the limit" if at_limit else f"{p['lame'] - p['steps']} below", "combo")],
               color="red" if at_limit else "blue")
    D.text(20, 160, "Worst case = consecutive Fibonacci numbers whose smaller one has that many digits. Red: exactly at Lamé's limit; blue: below it.", "caption")
    return D


def growth(d):
    avg = {a["digits"]: a["mean"] for a in d["average"]}
    picks = [1, 6, 12, 18]
    D = Diagram(800, 230, f"Average steps for random pairs grow by about {d['slope']:.2f} per extra digit: {avg[1]:.1f} at 1 digit, {avg[18]:.1f} at 18 digits")
    w, gap = 150, 56
    for i, k in enumerate(picks):
        D.node(f"g{i}", 20 + i * (w + gap), 76, w, 84,
               [(f"{k}-DIGIT NUMBERS", "tag"), (f"{avg[k]:.1f} steps", "title"), ("on average", "note")], color="blue" if i < 3 else "red")
    for i in range(3):
        dd = picks[i + 1] - picks[i]
        D.edge(f"g{i}", f"g{i + 1}", ports=("right", "left"), label=f"+{dd} digits: +{avg[picks[i + 1]] - avg[picks[i]]:.1f} steps", at=0.5, dy=-56)
    D.text(20, 196, f"Measured over {fmt(d['samples'])} random pairs at each size: +{d['slope']:.2f} steps per extra digit.", "caption")
    D.text(20, 214, f"Heilbronn's formula for the average, 0.843 ln n, predicts +{d['slope_predicted']:.2f}.", "caption")
    return D


def split(d):
    hist = d["histogram"]
    total = d["hist_samples"]
    lo, hi = hist[0][0], hist[-1][0]
    groups = [(lo, 29), (30, 40), (41, hi)]
    counts = [sum(c for s, c in hist if a <= s <= b) for a, b in groups]
    mode = max(hist, key=lambda p: p[1])
    worst18 = d["worst"][-1]
    D = Diagram(800, 380, f"{fmt(total)} random 18-digit pairs: most need 30 to 40 division steps; the slowest needed {hi}, far below Lamé's limit of {worst18['lame']}")
    D.node("root", 230, 20, 340, 64, [(f"{fmt(total)} random pairs", "title"), ("both numbers have 18 digits", "note")], color="ink")
    names = [f"FEWER THAN 30 STEPS", "30 TO 40 STEPS", "MORE THAN 40 STEPS"]
    for i, ((a, b), n) in enumerate(zip(groups, counts)):
        D.node(f"c{i}", 20 + i * 265, 150, 230, 90,
               [(names[i], "tag"), (f"{fmt(n)} pairs", "title"), (f"{n / total * 100:.1f}% · {a} to {b} steps", "note")],
               color="red" if i == 1 else "blue")
        D.edge("root", f"c{i}")
    notes = [f"fastest: {lo} steps", f"most common: {mode[0]} steps, {fmt(mode[1])} pairs", f"slowest: {hi} steps; Lamé's limit is {worst18['lame']}"]
    for i, t in enumerate(notes):
        D.node(f"n{i}", 20 + i * 265, 290, 230, 56, [(t, "combo")], color="ink", fill="wash", weight=1)
        D.edge(f"c{i}", f"n{i}")
    return D


def build(d):
    return {"family": family(), "chain": chain(d), "four": four(d), "ladder": ladder(d), "lame": lame(d), "growth": growth(d), "split": split(d)}
