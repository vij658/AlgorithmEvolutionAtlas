"""Era 5, topic 4: hashing. Every number is parsed from Hashing.java's output."""
import re

import common as C
from diagrams import Diagram


def parse(text: str) -> dict:
    d = {}
    for ln in text.splitlines():
        if m := re.match(r"luhn: the number (\d+) in pairs ([\d ]+?) ; add each pair and keep the last digit: (\d+), the bucket number ; ([\d,]+) random 10-digit numbers into the ([\d,]+) buckets: ([\d,]+) buckets empty \(random throws would leave about ([\d,]+)\), the fullest holds (\d+)", ln):
            g = m.groups()
            d["luhn"] = dict(num=g[0], pairs=g[1].split(), bucket=g[2], n=g[3], buckets=g[4], empty=g[5], expect=g[6], most=g[7])
        elif ln.startswith("probes: "):
            d["probes"] = re.findall(r"([\d.]+) full: chaining ([\d.]+) / ([\d.]+) \(formula ([\d.]+) / ([\d.]+)\), linear probing ([\d.]+) / ([\d.]+) \(formula ([\d.]+) / ([\d.]+)\)", ln)
            d["slots"] = re.search(r"table of ([\d,]+) slots", ln).group(1)
        elif ln.startswith("peterson: "):
            parts = ln.split("buckets of 1,")
            d["pet20"] = re.findall(r"(\d+)%: ([\d.]+) \(his ([\d.]+)\)", parts[0])
            d["pet1"] = re.findall(r"(\d+)%: ([\d.]+) \(his ([\d.]+)\)", parts[1])
            d["petruns"] = re.search(r"(\d+) random fillings each ; average", ln).group(1)
        elif m := re.match(r"prime: ([\d,]+) keys that are multiples of 64, .*? dividing by 1024 uses (\d+) slots, dividing by the prime 1021 uses (\d+) ; ([\d,]+) phone-like keys ending in 00: the last three digits give (\d+) slots, the remainder after the prime 1009 gives (\d+)$", ln):
            d["prime"] = dict(n=m.group(1), p2=m.group(2), pr=m.group(3), m=m.group(4), dec=m.group(5), decp=m.group(6))
        elif ln.startswith("growth: "):
            d["growth"] = re.findall(r"([\d,]+) keys: hashing ([\d.]+) probes, binary search ([\d.]+)", ln)
    d["checks"] = C.checks(text)
    return d


# ----------------------------------------------------------------------------------------------------------------------
def luhn_svg(d):
    L = d["luhn"]

    def draw(t, standalone):
        o = []
        x0, w = 40, 110
        o.append(C.text(20, 24, f"Luhn's bucket number for {L['num']} (as retold by IEEE Spectrum)", t["ink"], 13, "start", 700))
        for i, p in enumerate(L["pairs"]):
            x = x0 + i * w
            s = int(p[0]) + int(p[1])
            o.append(C.rect(x, 40, 80, 34, t["surface"], t["ink2"], 1.5, 5))
            o.append(C.text(x + 40, 63, f"{p[0]}  {p[1]}", t["ink"], 16, "middle", 700))
            o.append(C.line(x + 40, 76, x + 40, 98, t["axis"], 1.5))
            o.append(C.text(x + 40, 116, f"{p[0]} + {p[1]} = {s}", t["muted"], 13, "middle"))
            o.append(C.line(x + 40, 124, x + 40, 146, t["axis"], 1.5))
            o.append(C.rect(x + 22, 148, 36, 34, t["wash"], t["red"], 1.5, 5))
            o.append(C.text(x + 40, 171, str(s % 10), t["red"], 17, "middle", 700))
        o.append(C.text(20, 212, f"bucket {L['bucket']}: of {L['buckets']} buckets, a search reads only this one", t["ink"], 13, "start", 700))
        o.append(C.text(20, 234, f"{L['n']} random numbers: {L['empty']} buckets empty (about {L['expect']} expected for random throws), the fullest holds {L['most']}.", t["muted"], 12))
        return C.svg_doc(600, 248, "".join(o), "Luhn's bucket number: add the digits in pairs and keep the last digit of each sum", t, standalone, 0.55, 600)
    return draw


HT_HTML = """
<div class="board ht-board">
  <div style="min-width:0">
    <div class="eyebrow">Collisions handled by</div>
    <div class="ht-mode" id="ht-mode"></div>
    <div class="ht-add">
      <label class="eyebrow" for="ht-key">Key (a whole number)</label>
      <div style="display:flex;gap:6px;flex-wrap:wrap"><input id="ht-key" type="number" value="1953" min="0">
      <button type="button" id="ht-put">Store</button><button type="button" id="ht-find">Find</button><button type="button" id="ht-rand">Store 5 random</button><button type="button" id="ht-clear">Empty</button></div>
    </div>
    <p class="say" id="ht-say" aria-live="polite"></p>
  </div>
  <div style="min-width:0">
    <div class="eyebrow">13 slots: the key's slot is its remainder after dividing by 13</div>
    <ol class="ht-slots" id="ht-slots" start="0"></ol>
  </div>
</div>
"""

HT_CSS = """
.ht-mode{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 10px}
.ht-mode button[aria-pressed=true]{background:var(--ink);color:var(--paper)}
.ht-add input{font:15px var(--mono);width:8em;padding:6px;border:1px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--ink)}
.ht-slots{list-style:none;margin:6px 0;padding:0;display:grid;gap:3px;font:13px var(--mono)}
.ht-slots li{display:grid;grid-template-columns:2.2em 1fr;gap:6px;align-items:center;min-width:0}
.ht-slots li .i{color:var(--muted);text-align:right}
.ht-slots li .b{display:flex;gap:4px;flex-wrap:wrap;min-height:26px;border:1px solid var(--rule);border-radius:4px;padding:2px 4px}
.ht-slots li .b span{padding:1px 5px;border-radius:3px;background:var(--wash)}
.ht-slots li .b span.hit{background:var(--blue);color:var(--on-blue)}
.ht-slots li .b span.seen{outline:2px solid var(--yellow)}
.ht-slots li.full .b{border-color:var(--ink2)}
"""

HT_JS = r"""
(() => {
  const mode = document.getElementById("ht-mode");
  if (!mode) return;
  const M = 13;
  let how = "chain", chains, linear, mark = {seen: [], hit: null};
  function empty() { chains = Array.from({length: M}, () => []); linear = Array(M).fill(null); mark = {seen: [], hit: null}; }
  let seed = 1953;
  const rnd = () => { seed = (seed * 1103515245 + 12345) % 2147483648; return seed % 100000; };
  function put(k) {
    const h = k % M;
    if (how === "chain") { if (!chains[h].includes(k)) chains[h].push(k); return `Key ${k}: ${k} ÷ 13 leaves ${h}, so it goes into bucket ${h}${chains[h].length > 1 ? `, which now holds ${chains[h].length} keys` : ""}.`; }
    if (linear.includes(k)) return `Key ${k} is already stored.`;
    if (!linear.includes(null)) return "The table is full: open addressing cannot store more keys than slots.";
    let i = h, tries = 1; while (linear[i] !== null) { i = (i + 1) % M; tries++; }
    linear[i] = k;
    return `Key ${k}: home slot ${h}${i !== h ? `, taken; it moves on to slot ${i} after ${tries} looks` : ""}.`;
  }
  function find(k) {
    const h = k % M; mark = {seen: [], hit: null};
    if (how === "chain") {
      const b = chains[h]; let n = 0;
      for (const x of b) { n++; mark.seen.push([h, x]); if (x === k) { mark.hit = [h, x]; return `Found ${k} in bucket ${h} after comparing ${n} key${n > 1 ? "s" : ""}.`; } }
      return `Bucket ${h} holds ${b.length} key${b.length === 1 ? "" : "s"}; ${k} is not among them (${n} compared).`;
    }
    let i = h, n = 0;
    while (linear[i] !== null && n < M) { n++; mark.seen.push([i, linear[i]]); if (linear[i] === k) { mark.hit = [i, k]; return `Found ${k} in slot ${i} after ${n} look${n > 1 ? "s" : ""}, starting from its home slot ${h}.`; } i = (i + 1) % M; }
    return `${k} is not stored: the search from slot ${h} reached ${n === M ? "every slot" : "an empty slot"} after ${n + (n < M ? 1 : 0)} looks.`;
  }
  function show(msg) {
    const ol = document.getElementById("ht-slots"); ol.innerHTML = "";
    for (let i = 0; i < M; i++) {
      const items = how === "chain" ? chains[i] : (linear[i] === null ? [] : [linear[i]]);
      const li = el("li", {class: items.length ? "full" : ""}, ol);
      el("span", {class: "i"}, li).textContent = i;
      const b = el("span", {class: "b"}, li);
      items.forEach(x => {
        const hit = mark.hit && mark.hit[0] === i && mark.hit[1] === x, seen = mark.seen.some(([a, y]) => a === i && y === x);
        el("span", {class: hit ? "hit" : seen ? "seen" : ""}, b).textContent = x;
      });
    }
    const n = how === "chain" ? chains.reduce((a, c) => a + c.length, 0) : linear.filter(x => x !== null).length;
    document.getElementById("ht-say").textContent = (msg ? msg + " " : "") + `${n} key${n === 1 ? "" : "s"} stored in 13 slots (load ${(n / M).toFixed(2)}).`;
  }
  [["chain", "a chain in each slot (Luhn)"], ["linear", "the next free slot (Amdahl)"]].forEach(([k, label]) => {
    const b = el("button", {type: "button", "aria-pressed": String(k === how)}, mode); b.textContent = label;
    b.addEventListener("click", () => { how = k; mode.querySelectorAll("button").forEach(x => x.setAttribute("aria-pressed", String(x === b))); empty(); [1953, 1954, 1956, 1957, 1966].forEach(put); show("Same five keys, the other way."); });
  });
  const key = () => Math.max(0, Math.floor(Number(document.getElementById("ht-key").value) || 0));
  document.getElementById("ht-put").addEventListener("click", () => { mark = {seen: [], hit: null}; show(put(key())); });
  document.getElementById("ht-find").addEventListener("click", () => { const m = find(key()); show(m); });
  document.getElementById("ht-rand").addEventListener("click", () => { mark = {seen: [], hit: null}; let last = ""; for (let i = 0; i < 5; i++) last = put(rnd()); show(last); });
  document.getElementById("ht-clear").addEventListener("click", () => { empty(); show("Empty."); });
  empty(); [1953, 1954, 1956, 1957, 1966].forEach(put);
  show("Five keys stored: 1953 and 1966 both leave remainder 3, and collide. Try Find, or switch to the next-free-slot method.");
})();
"""


# ----------------------------------------------------------------------------------------------------------------------
def family():
    D = Diagram(1000, 640, "How hashing combined older ideas, and where it led")
    W = 210
    nodes = {
        "tab": (20, 20, "Tables and indexes", "look a key up instead of computing", "Eras 1 to 3", "ink"),
        "ram": (395, 20, "Random-access memory", "any word reached in the same time", "Era 4 topic 9", "ink"),
        "mod": (770, 20, "Remainders", "a number divided, the rest kept", "Era 1", "ink"),
        "hash": (395, 170, "Hashing", "⊕ compute the address from the key", "IBM, 1953–1957", "red"),
        "chain": (20, 330, "Chaining", "a list of records in each bucket", "Luhn, 1953", "ink"),
        "open": (395, 330, "Open addressing", "if taken, try the next slot", "Amdahl, 1954; Peterson, 1957", "ink"),
        "prime": (770, 330, "Division by a prime", "spread keys that share a pattern", "Dumey, 1956", "ink"),
        "today": (395, 480, "Hash tables today", "dictionaries, sets, databases, caches", "today", "blue"),
    }
    for k, (x, y, t, combo, date, c) in nodes.items():
        D.node(k, x, y, W, 86, [(t, "title"), (combo, "combo"), (date, "note")], color=c)
    D.edge("tab", "hash", ports=("bottom", "top:0.15"))
    D.edge("ram", "hash", ports=("bottom", "top"))
    D.edge("mod", "hash", ports=("bottom", "top:0.85"), dashed=True)
    D.edge("hash", "chain", ports=("bottom:0.1", "top:0.7"))
    D.edge("hash", "open", ports=("bottom", "top"))
    D.edge("hash", "prime", ports=("bottom:0.9", "top:0.3"))
    D.edge("chain", "today", ports=("bottom:0.6", "left:0.5"))
    D.edge("open", "today", ports=("bottom", "top"))
    D.edge("prime", "today", ports=("bottom:0.3", "right:0.5"))
    D.text(20, 615, "Dashed: a likeness of ideas. Luhn's chained buckets are also the first linked lists on record (topic 6).", "caption")
    return D


def chain(d):
    g, pr, pb = d["growth"], d["prime"], d["probes"]
    last = pb[-1]
    steps = [
        (f"A sorted file searched by halves: {g[-1][2]} looks for {g[-1][0]} keys, one more every time it doubles",
         "Luhn: compute the bucket from the key, and read only that bucket", "IBM memorandum, January 1953"),
        ("Two keys can land in the same bucket",
         f"A chain in each bucket, or the next free slot: {g[-1][1]} looks at half full, at any size", "Luhn 1953; Amdahl 1954"),
        (f"Keys with a pattern crowd together: multiples of 64 fill {pr['p2']} of 1024 slots",
         f"Divide by a prime and keep the remainder: all {pr['pr']} slots used", "Dumey, 1956"),
        (f"A nearly full table slows down: at {last[0]} full, a failed search took {last[6]} looks",
         "Measure it, and keep tables well below full", "Peterson, 1957"),
    ]
    rowh, gap = 92, 50
    D = Diagram(960, 20 + len(steps) * (rowh + gap) - gap + 20, "Each fix leaves a new pain: from searching to computing the address")
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
    L, pb, p20, p1, pr, g = d["luhn"], d["probes"], d["pet20"], d["pet1"], d["prime"], d["growth"]
    sections = [
        dict(id="tree", eyebrow="A ⊕ B = C", title="How ideas combined", toc="How ideas combined", blocks=[
            dict(type="p", text="A new algorithm is usually an older idea combined with a new one. Tables and indexes had always let people look things up instead of working them out, and the new machines could reach any word of memory in the same short time. Hashing joined the two: work the address out from the key itself, and go straight there. Each box names the idea that was added."),
            dict(type="diagram", name="family", diagram=family(),
                 caption="Red: hashing. Blue: hash tables today."),
        ]),
        dict(id="table", eyebrow="Try it", title="Store keys, make them collide, find them again", toc="Try it", blocks=[
            dict(type="p", text="A table of 13 slots. A key's home slot is its remainder after dividing by 13 (Dumey's prime remainder). Store keys and watch two of them collide; then switch between Luhn's chains and Amdahl's next-free-slot method, and use Find to see which slots a search has to look at (yellow) before it hits (blue)."),
            dict(type="widget", html=HT_HTML, js=HT_JS, css=HT_CSS,
                 fallback=dict(type="svg", name="luhn", draw=luhn_svg(d), alt="Luhn's bucket number: add the digits in pairs and keep the last digit of each sum", width=600),
                 note="In the interactive edition you can store and find keys in a small table, by either method."),
        ]),
        dict(id="time", eyebrow="Where it sits in time", title="Era 5, the programmer's craft", toc="Timeline",
             blocks=[C.era_timeline_block(ctx["index"], ctx["era"])]),
        dict(id="hurt", eyebrow="What hurt, and what fixed it", title="Each fix leaves a new pain", toc="What hurt", blocks=[
            dict(type="diagram", name="chain", diagram=chain(d), caption="Read it as a snake: each new problem sits directly under the fix that exposed it."),
        ]),
        dict(id="how", eyebrow="How it works", title="Compute where it lives", toc="How it works", blocks=[
            dict(type="p", text=f"**Luhn's bucket number.** As IEEE Spectrum retells his 1953 memorandum: take a phone number such as {L['num']}, add its digits in pairs ({' '.join(L['pairs'])}), keep the last digit of each sum, and the digits together, {L['bucket']}, name a bucket. To find the number again, compute the same five digits and read that one bucket. The program threw {L['n']} random numbers into the {L['buckets']} buckets: {L['empty']} stayed empty (pure chance would leave about {L['expect']}) and the fullest held {L['most']}."),
            dict(type="p", text="**When two keys collide.** Luhn's buckets each hold a short list (chaining). Amdahl, writing an assembler for the IBM 701, used one table: if a key's slot is taken, try the next, and the next (open addressing with linear probing). Peterson published it in 1957: \"If that is already occupied, the second listed position would be used. If that also is full, the third would be tried, etc., until an empty position is found.\""),
            dict(type="p", text=f"**Patterns in the keys.** Dumey (1956) treated the key as a number and kept the remainder after dividing \"by a number slightly less than the number of addressable locations\", preferably a prime. The program's {pr['n']} keys that are multiples of 64 land in only {pr['p2']} of 1,024 slots when divided by 1,024, but spread over all {pr['pr']} when divided by the prime 1,021. Phone-like keys ending in 00: their last three digits give {pr['dec']} slots; the remainder after 1,009 gives {pr['decp']}."),
            dict(type="callout", kind="key", label="Key idea",
                 text="Don't search for the record: compute its address from its key. Collisions are inevitable, but if the table is kept from getting too full, they cost a few extra looks, however large the file."),
        ]),
        dict(id="measured", eyebrow="Measured", title="Probes, and Peterson's tables repeated", toc="Measured", blocks=[
            dict(type="table", head=["Load", "Chaining: found / not found", "Linear probing: found / not found", "Linear probing, formula"], num=[0],
                 rows=[[a, f"{c1} / {c2}", f"{l1} / {l2}", f"{f1} / {f2}"] for a, c1, c2, _, _, l1, l2, f1, f2 in pb], hl=3),
            dict(type="p", text=f"A table of {d['slots']} slots filled with random keys. Chaining follows 1 + a/2 looks for a key that is there and a for one that is not; linear probing follows (1 + 1/(1−a))/2 and (1 + 1/(1−a)²)/2, which explode as the table fills. At 0.95 a single table strays far from the formula, because a few very long runs of filled slots dominate."),
            dict(type="table", head=["Store full", "Our average (buckets read)", "Peterson 1957, Table 5A"], num=[1, 2],
                 rows=[[f"{p}%", o, h] for p, o, h in p20]),
            dict(type="p", text=f"Peterson's own experiment repeated: 10,000 records in 500 buckets of 20, overflow into the next bucket with room, averaged over {d['petruns']} random fillings. Our averages match his figures to within 0.03 up to 95% full; at 100% his single runs ranged from about 3.3 to 4.7. With buckets of one record (500 slots): {'; '.join(f'{p}% full {o} (his {h})' for p, o, h in p1)}."),
            dict(type="table", head=["Keys", "Hashing, half-full table (looks)", "Binary search (looks)"], num=[0, 1, 2],
                 rows=[[n, h, b] for n, h, b in g], hl=len(g) - 1),
        ]),
        dict(id="evidence", eyebrow="The evidence", title="Memoranda at IBM", toc="The evidence", blocks=[
            dict(type="p", text="Knuth's history: \"H. P. Luhn, who wrote an internal IBM memorandum in January 1953 that suggested the use of chaining\"; at the same time Gene M. Amdahl, Elaine M. Boehme, N. Rochester and Arthur L. Samuel \"were building an assembly program for the IBM 701\", and \"Amdahl originated the idea of open addressing with linear probing.\" \"Hash coding was first described in the open literature by Arnold I. Dumey, Computers and Automation 5,12 (December 1956), 6-9.\" A. P. Ershov \"independently discovered linear open addressing in 1957\"."),
            dict(type="p", text="The name came later: \"The first published appearance of the word seems to have been in H. Hellerman's book\" (1967), though \"it had already become common jargon\"; an earlier use is in \"an unpublished memorandum written by W. W. Peterson in 1961\". Luhn (1896–1964) joined IBM in 1941 and is also remembered for the Luhn checksum and the KWIC index."),
        ]),
        dict(id="circle", eyebrow="Full circle", title="A look-up in one step", toc="Full circle", blocks=[
            dict(type="p", text="Every programming language now has a hash table built in (a dictionary, a map, a set), and databases and caches lean on them. The choice Luhn and Amdahl faced in 1953–1954, a chain in each slot or the next free slot, is still argued over by people who tune them."),
            dict(type="callout", kind="circle", label="Full circle",
                 text=f"With a million keys, binary search needs {g[-1][2]} looks on average; a half-full hash table needs {g[-1][1]}, the same as with a thousand keys."),
        ]),
        dict(id="try", eyebrow="Pause and try", title="Before you read on", toc="Pause and try", blocks=[dict(type="tries", items=[
            ("Luhn's method for the number 5550123456?", "Pairs 55 50 12 34 56; sums 10 5 3 7 11; last digits 0 5 3 7 1: bucket 05371."),
            ("With 13 slots and division by 13, where do 26, 39 and 52 go?", "All to slot 0: they collide, because they are all multiples of 13."),
            ("Why is dividing by 1024 a bad idea for keys that are multiples of 64?", "The remainder is then always a multiple of 64: only 16 of the 1,024 slots can ever be used."),
            ("A linear-probing table is 90% full. About how many looks does a search for a missing key take?", "About (1 + 1/0.1²)/2 = 50.5: it must walk to the end of a long run of filled slots."),
            ("What does a hash table give up compared with a sorted list?", "Order: it cannot list the keys in order or find the next larger key without looking at them all."),
        ])]),
        dict(id="objects", eyebrow="The objects", title="Where the evidence lives", toc="The objects", blocks=[dict(type="objects", items=[
            dict(title="Addressing for Random-Access Storage (1957)", text="Peterson's paper in the IBM Journal, with the tables this page repeats.",
                 draw=C.draw_manuscript, link="https://www.Gwern.net/doc/cs/algorithm/1957-peterson.pdf", link_text="PDF", licence="Drawn placeholder."),
            dict(title="Computers and Automation, December 1956", text="The issue with Dumey's \"Indexing for Rapid Random Access Memory Systems\".",
                 draw=C.draw_book, link="https://bitsavers.mirrorservice.org/magazines/Computers_And_Automation/195612.pdf", link_text="Scan at bitsavers", licence="Drawn placeholder."),
        ])]),
        C.links_section(ctx),
        C.prove_it_section(ctx, "Hashing", d["checks"],
                           f"Luhn's buckets for {L['n']} numbers, chaining and linear probing against their formulas, Peterson's 1957 tables repeated, remainders by powers of two and by primes, and hashing against binary search up to a million keys.",
                           ["static double peterson(int nb, int c, int n)"]),
    ]
    return dict(
        title="Hashing", date="1953–1957",
        description="Era 5, topic 4 of The Algorithm Evolution Atlas: hashing at IBM, from Luhn's buckets and Amdahl's linear probing to Dumey's prime remainder and Peterson's 1957 measurements.",
        lede="Searching a file takes longer as the file grows. At IBM, Luhn proposed computing a record's place from the record itself; collisions are handled by a chain in each bucket, or by trying the next free slot.",
        fieldnote=f"Peterson filled a store of 10,000 records with random keys in 1957 and counted how many buckets a search had to read. I repeated his experiment {d['petruns']} times: at 90% full, {p20[3][1]} buckets on average; he printed {p20[3][2]}. With a million keys, binary search takes {g[-1][2]} looks; a half-full hash table takes {g[-1][1]}.",
        card=[("When", "Luhn 1953; Amdahl 1954; Dumey 1956; Peterson 1957"),
              ("Where", "IBM"),
              ("What hurt", "Finding a record took longer as the file grew"),
              ("The fix", "Compute the address from the key"),
              ("Cost", f"About {g[-1][1]} looks at half full, at any size")],
        sections=sections,
        footer="Every number on this page is parsed from the output of `Hashing.java`.",
    )
