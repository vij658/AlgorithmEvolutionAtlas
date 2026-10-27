"""The video list: one search round per concept, results kept in book/videos/videos.json, pages built from it.

    python3 code/tools/videos/videos.py next            # the next concept to search, as JSON
    python3 code/tools/videos/videos.py record FILE     # merge one round's results (JSON) and rebuild the pages
    python3 code/tools/videos/videos.py build [--artifact OUT]
    python3 code/tools/videos/videos.py status

A round's FILE: {"cid": "e1-01-c2", "query": "tally marks", "host": "youtube.com",
                 "videos": [{"url": "...", "title": "...", "channel": "...", "channel_url": "...",
                             "level": "start|deeper|scholar", "checked": "YouTube oEmbed"}],
                 "candidates": 10, "rejected": "why the others were left out", "error": ""}
Only videos whose title and channel were confirmed (YouTube's oEmbed lookup, or the page itself for other sites) go in
"videos". A round whose search or checks failed records "error" and stays pending, so it is tried again next round.
"""
import datetime
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import concepts as K  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "book" / "videos" / "videos.json"
LEVELS = [("start", "Start", "No background needed"), ("deeper", "Deeper", "University level"), ("scholar", "Scholar", "Research talks and the inventors themselves")]


def load():
    if DATA.exists():
        return json.loads(DATA.read_text())
    return {"updated": None, "rounds": 0, "concepts": {}}


def save(db):
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(db, indent=1, ensure_ascii=False) + "\n")


def today():
    return datetime.date.today().isoformat()


def nxt():
    db = load()
    rows = K.all_concepts()
    done = [r for r in rows if r[0] in db["concepts"] and not db["concepts"][r[0]].get("error")]
    for r in rows:
        c = db["concepts"].get(r[0])
        if c is None or c.get("error"):
            cid, group, gtitle, num, slug, ttitle, folder, concept = r
            print(json.dumps(dict(cid=cid, concept=concept, topic=ttitle, group=gtitle, query=concept,
                                  tries=(c or {}).get("tries", 0), progress=f"{len(done)} of {len(rows)} concepts searched"), ensure_ascii=False))
            return
    print(json.dumps(dict(cid=None, progress=f"all {len(rows)} concepts searched")))


def record(path):
    rnd = json.loads(Path(path).read_text())
    ids = {r[0] for r in K.all_concepts()}
    cid = rnd["cid"]
    if cid not in ids:
        raise SystemExit(f"unknown concept {cid}")
    db = load()
    prev = db["concepts"].get(cid, {})
    vids = []
    seen = set()
    for v in rnd.get("videos", []):
        for k in ("url", "title", "channel", "level", "checked"):
            if not v.get(k):
                raise SystemExit(f"video missing {k}: {v}")
        if v["level"] not in {l for l, _, _ in LEVELS}:
            raise SystemExit(f"bad level {v['level']}")
        key = re.sub(r"[&?](xstg|si|pp)=[^&]*", "", v["url"])
        if key in seen:
            continue
        seen.add(key)
        vids.append(dict(url=key, title=" ".join(v["title"].split()), channel=" ".join(v["channel"].split()), channel_url=v.get("channel_url", ""), level=v["level"],
                         checked=f"{v['checked']}, {today()}"))
    entry = dict(searched=today(), query=rnd.get("query", ""), host=rnd.get("host", ""), candidates=rnd.get("candidates", 0),
                 rejected=rnd.get("rejected", ""), videos=vids, tries=prev.get("tries", 0) + 1)
    if rnd.get("error"):
        entry["error"] = rnd["error"]
    db["concepts"][cid] = entry
    db["rounds"] = db.get("rounds", 0) + 1
    db["updated"] = today()
    save(db)
    build()
    print(f"recorded {cid}: {len(vids)} video(s)" + (f", error: {rnd['error']}" if rnd.get("error") else ""))


# ----------------------------------------------------------------------------------------------------------------------
def esc(s):
    return html.escape(str(s), quote=True)


def grouped(db):
    groups = []
    for r in K.all_concepts():
        cid, group, gtitle, num, slug, ttitle, folder, concept = r
        if not groups or groups[-1]["id"] != group:
            groups.append(dict(id=group, title=gtitle, topics=[]))
        g = groups[-1]
        if not g["topics"] or g["topics"][-1]["slug"] != slug:
            g["topics"].append(dict(num=num, slug=slug, title=ttitle, folder=folder, concepts=[]))
        g["topics"][-1]["concepts"].append(dict(cid=cid, name=concept, data=db["concepts"].get(cid)))
    return groups


def stats(db):
    rows = K.all_concepts()
    searched = [r for r in rows if r[0] in db["concepts"] and not db["concepts"][r[0]].get("error")]
    vids = sum(len(db["concepts"][r[0]]["videos"]) for r in searched)
    return len(rows), len(searched), vids


CSS = """
/* Layout: the book's Byrne palette; one reading column of topics, concepts as rows, each video a line with a coloured level mark. */
:root{
  --paper:#fbfbf9; --surface:#ffffff; --ink:#17171a; --ink-2:#55545a; --muted:#77767e; --rule:#e4e3dd; --axis:#c4c3bb;
  --red:#d5352a; --yellow:#e8a317; --blue:#1f5ba8; --wash:#f1f0ea; --on-red:#ffffff; --on-yellow:#17171a; --on-blue:#ffffff; --link:#1f5ba8;
  --display:"Libre Caslon Display","Big Caslon","Book Antiqua",Georgia,serif;
  --body:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#121418; --surface:#1a1d22; --ink:#ecebe6; --ink-2:#b9b8b2; --muted:#8f8e96; --rule:#2b2e34; --axis:#41444b;
    --red:#f0584d; --yellow:#d9a227; --blue:#5b8fe0; --wash:#1d2026; --on-red:#14161a; --on-yellow:#14161a; --on-blue:#14161a; --link:#7ea8ec; color-scheme:dark;
  }
}
:root[data-theme="dark"]{
  --paper:#121418; --surface:#1a1d22; --ink:#ecebe6; --ink-2:#b9b8b2; --muted:#8f8e96; --rule:#2b2e34; --axis:#41444b;
  --red:#f0584d; --yellow:#d9a227; --blue:#5b8fe0; --wash:#1d2026; --on-red:#14161a; --on-yellow:#14161a; --on-blue:#14161a; --link:#7ea8ec; color-scheme:dark;
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);font:16px/1.6 var(--body);margin:0}
a{color:var(--link);text-underline-offset:2px}
:focus-visible{outline:2px solid var(--blue);outline-offset:2px;border-radius:2px}
.wrap{max-width:900px;margin:0 auto;padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));padding-block:40px 72px}
header h1{font:400 clamp(34px,6vw,52px)/1.05 var(--display);margin:0 0 14px;text-wrap:balance}
header .lede{max-width:64ch;color:var(--ink-2);margin:0 0 18px}
.tally{display:flex;flex-wrap:wrap;gap:8px 28px;font:13px var(--mono);color:var(--muted);border-top:2px solid var(--ink);padding-top:10px;font-variant-numeric:tabular-nums}
.tally b{color:var(--ink);font-weight:600;font-size:15px}
.key{display:flex;flex-wrap:wrap;gap:6px 18px;margin:14px 0 0;font-size:13px;color:var(--ink-2)}
.mark{display:inline-block;width:0;height:0;border-style:solid;border-width:6px 0 6px 10px;border-color:transparent;vertical-align:-1px;margin-right:6px}
.mark.start{border-left-color:var(--yellow)} .mark.deeper{border-left-color:var(--blue)} .mark.scholar{border-left-color:var(--red)}
.tools{position:sticky;top:env(safe-area-inset-top, 0px);z-index:5;background:var(--paper);display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;padding:12px 0;margin-top:22px;border-bottom:1px solid var(--rule)}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top, 0px);z-index:10;background:var(--paper)}
.tools input[type=search],.tools select{font:inherit;font-size:14px;padding:6px 10px;border:1px solid var(--axis);background:var(--surface);color:var(--ink);border-radius:2px;min-width:0}
.tools input[type=search]{flex:1 1 220px}
.chips{display:flex;gap:6px;flex-wrap:wrap}
.chip{font:600 12px var(--body);letter-spacing:.04em;text-transform:uppercase;padding:6px 10px;border:1px solid var(--axis);background:var(--surface);color:var(--ink-2);border-radius:2px;cursor:pointer}
.chip[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.tools label.chk{font-size:13px;color:var(--ink-2);display:flex;gap:6px;align-items:center}
.group{margin-top:44px}
.group > h2{font:400 26px/1.2 var(--display);margin:0;text-wrap:balance}
.group .gstat{font:12px var(--mono);color:var(--muted);margin:4px 0 0}
.topic{margin-top:22px;border-top:1px solid var(--rule);padding-top:12px}
.topic h3{font:600 17px/1.35 var(--body);margin:0;display:flex;flex-wrap:wrap;gap:4px 12px;align-items:baseline}
.topic h3 .n{font:12px var(--mono);color:var(--muted);font-weight:400}
.topic h3 a.book{font-size:13px;font-weight:400}
.concept{display:grid;grid-template-columns:minmax(0,13em) minmax(0,1fr);gap:4px 18px;padding:8px 0;border-bottom:1px dashed var(--rule)}
.concept:last-child{border-bottom:0}
.cname{font-size:14.5px;color:var(--ink);min-width:0}
.cname .step{font:11px var(--mono);color:var(--muted);display:block}
.vids{list-style:none;margin:0;padding:0;display:grid;gap:6px;min-width:0}
.vids li{min-width:0;overflow-wrap:anywhere}
.vids a{font-weight:500}
.vids .by{font-size:13px;color:var(--muted)}
.none{font-size:13.5px;color:var(--muted);font-style:italic}
.pending{font-size:13px;color:var(--muted)}
.empty-state{margin-top:30px;color:var(--muted)}
footer{margin-top:56px;border-top:1px solid var(--rule);padding-top:14px;font-size:13px;color:var(--muted);max-width:70ch}
@media (max-width:620px){.concept{grid-template-columns:1fr}}
@media (prefers-reduced-motion: reduce){*{scroll-behavior:auto}}
"""

JS = """
(() => {
  const q = document.getElementById("vq"), grp = document.getElementById("vg"), showAll = document.getElementById("vall");
  const chips = [...document.querySelectorAll(".chip")];
  const on = new Set(chips.map(c => c.dataset.level));
  function apply() {
    const term = q.value.trim().toLowerCase(), g = grp.value, all = showAll.checked;
    let shown = 0;
    document.querySelectorAll(".group").forEach(G => {
      let gAny = false;
      const gOk = !g || G.dataset.group === g;
      G.querySelectorAll(".topic").forEach(T => {
        let tAny = false;
        T.querySelectorAll(".concept").forEach(C => {
          const searched = C.dataset.searched === "1";
          let cAny = false;
          C.querySelectorAll(".vids li").forEach(L => {
            const ok = on.has(L.dataset.level) && (!term || (C.dataset.text + " " + L.dataset.text).includes(term));
            L.hidden = !ok; if (ok) cAny = true;
          });
          const plain = !C.querySelector(".vids li");
          const textOk = !term || C.dataset.text.includes(term);
          const vis = gOk && (cAny || (plain && textOk && (searched || all)));
          C.hidden = !vis; if (vis) { tAny = true; shown++; }
        });
        T.hidden = !tAny; if (tAny) gAny = true;
      });
      G.hidden = !gAny;
    });
    document.getElementById("vempty").hidden = shown > 0;
  }
  chips.forEach(c => c.addEventListener("click", () => {
    const l = c.dataset.level, p = c.getAttribute("aria-pressed") === "true";
    c.setAttribute("aria-pressed", String(!p)); p ? on.delete(l) : on.add(l); apply();
  }));
  [q, grp].forEach(e => e.addEventListener("input", apply)); showAll.addEventListener("change", apply);
  apply();
})();
"""


def page(db, artifact=False):
    total, searched, nvid = stats(db)
    groups = grouped(db)
    o = []
    o.append('<header><h1>Videos for Every Idea</h1>')
    o.append('<p class="lede">A watch list for the book, from counting with tally marks to Bitcoin: for every topic, its concepts '
             'from the simplest to the most advanced, each with the videos that explain it. A video is listed only after its title '
             'and channel were confirmed (YouTube\'s own oEmbed lookup, or the page itself on other sites).</p>')
    o.append(f'<div class="tally"><span><b>{searched}</b> of {total} concepts searched</span><span><b>{nvid}</b> videos listed</span>'
             f'<span>updated {esc(db.get("updated") or "not yet")}</span></div>')
    o.append('<div class="key">' + "".join(f'<span><span class="mark {k}" aria-hidden="true"></span><b>{n}</b>: {esc(d)}</span>' for k, n, d in LEVELS) + '</div></header>')
    o.append('<div class="tools" role="search"><input type="search" id="vq" placeholder="Search concepts, videos, channels" aria-label="Search the list">')
    o.append('<select id="vg" aria-label="Show one part of the book"><option value="">Whole book</option>' +
             "".join(f'<option value="{g["id"]}">{esc(g["title"])}</option>' for g in groups) + '</select>')
    o.append('<div class="chips" role="group" aria-label="Levels">' + "".join(f'<button type="button" class="chip" data-level="{k}" aria-pressed="true">{n}</button>' for k, n, _ in LEVELS) + '</div>')
    o.append('<label class="chk"><input type="checkbox" id="vall"> Show concepts not searched yet</label></div>')
    for g in groups:
        gc = [c for t in g["topics"] for c in t["concepts"]]
        gs = [c for c in gc if c["data"] and not c["data"].get("error")]
        gv = sum(len(c["data"]["videos"]) for c in gs)
        o.append(f'<section class="group" data-group="{g["id"]}"><h2>{esc(g["title"])}</h2>'
                 f'<p class="gstat">{len(gs)} of {len(gc)} concepts searched · {gv} videos</p>')
        for t in g["topics"]:
            num = f'<span class="n">{t["num"]:02d}</span>' if t["num"] else ""
            link = ""
            if t["folder"] and not artifact:
                link = f' <a class="book" href="../{esc(t["folder"])}/README.md">in the book</a>'
            o.append(f'<article class="topic"><h3>{num}<span>{esc(t["title"])}</span>{link}</h3>')
            n = len(t["concepts"])
            for i, c in enumerate(t["concepts"], 1):
                d = c["data"]
                searched_ok = bool(d and not d.get("error"))
                vids = d["videos"] if searched_ok else []
                text = esc((c["name"] + " " + t["title"]).lower())
                step = f'<span class="step">idea {i} of {n}</span>' if n > 1 else ""
                o.append(f'<div class="concept" data-searched="{1 if searched_ok else 0}" data-text="{text}"><div class="cname">{step}{esc(c["name"])}</div>')
                if vids:
                    o.append('<ul class="vids">')
                    for v in vids:
                        vt = esc((v["title"] + " " + v["channel"]).lower())
                        ch = f'<a href="{esc(v["channel_url"])}" target="_blank" rel="noopener">{esc(v["channel"])}</a>' if v.get("channel_url") else esc(v["channel"])
                        o.append(f'<li data-level="{v["level"]}" data-text="{vt}"><span class="mark {v["level"]}" aria-label="{v["level"]}"></span>'
                                 f'<a href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(v["title"])}</a> <span class="by">· {ch}</span></li>')
                    o.append('</ul>')
                elif searched_ok:
                    o.append(f'<div class="none">No suitable video found (searched {esc(d["searched"])}).</div>')
                else:
                    o.append('<div class="pending">Not searched yet.</div>')
                o.append('</div>')
            o.append('</article>')
        o.append('</section>')
    o.append('<p class="empty-state" id="vempty" hidden>Nothing matches. Clear the search, turn a level back on, or show the concepts not searched yet.</p>')
    o.append('<footer>Searched one concept at a time, with a two-minute pause between searches. Videos were chosen for accuracy and clarity; '
             'titles and channels are as their hosts report them. Levels are the book\'s own: Start, Deeper, Scholar.</footer>')
    body = "".join(o)
    fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Public+Sans:wght@400;500;600&family=JetBrains+Mono&display=swap">'
    head = f'<title>Videos for Every Idea</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n{fonts}\n<style>{CSS}</style>\n'
    content = f'<div class="wrap">{body}</div>\n<script>{JS}</script>\n'
    if artifact:
        return head + content
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + '</head>\n<body>\n' + content + '</body>\n</html>\n')


def readme(db):
    total, searched, nvid = stats(db)
    o = ["# Videos for every idea", "",
         "A watch list for the book: for every topic, its concepts from the simplest to the most advanced, each with videos that explain it. "
         "A video is listed only after its title and channel were confirmed (YouTube's oEmbed lookup, or the page itself on other sites). "
         "Levels: **Start** (no background needed), **Deeper** (university level), **Scholar** (research talks and the inventors themselves).", "",
         f"**{searched} of {total} concepts searched, {nvid} videos listed** (updated {db.get('updated') or 'not yet'}). "
         "The [interactive edition](index.html) can be searched and filtered by level. The data is in [`videos.json`](videos.json); "
         "the procedure is in [`code/tools/videos/README.md`](../../code/tools/videos/README.md).", ""]
    for g in grouped(db):
        gc = [c for t in g["topics"] for c in t["concepts"]]
        if not any(c["data"] and not c["data"].get("error") for c in gc):
            continue
        o += [f"## {g['title']}", ""]
        for t in g["topics"]:
            if not any(c["data"] and not c["data"].get("error") for c in t["concepts"]):
                continue
            link = f" ([in the book](../{t['folder']}/README.md))" if t["folder"] else ""
            o += [f"### {t['title']}{link}", "", "| Idea | Video | Channel | Level |", "|---|---|---|---|"]
            for c in t["concepts"]:
                d = c["data"]
                if not d or d.get("error"):
                    o.append(f"| {c['name']} | *not searched yet* | | |")
                elif not d["videos"]:
                    o.append(f"| {c['name']} | *no suitable video found* | | |")
                else:
                    for j, v in enumerate(d["videos"]):
                        name = c["name"] if j == 0 else ""
                        title = v["title"].replace("|", "\\|")
                        o.append(f"| {name} | [{title}]({v['url']}) | {v['channel'].replace('|', '/')} | {v['level'].capitalize()} |")
            o.append("")
    return "\n".join(o) + "\n"


def build(artifact_out=None):
    db = load()
    out = DATA.parent
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(page(db))
    (out / "README.md").write_text(readme(db))
    if artifact_out:
        Path(artifact_out).write_text(page(db, artifact=True))


def status():
    db = load()
    total, searched, nvid = stats(db)
    errs = [k for k, v in db["concepts"].items() if v.get("error")]
    print(f"{searched} of {total} concepts searched, {nvid} videos, {db.get('rounds', 0)} rounds, {len(errs)} pending after errors")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "next":
        nxt()
    elif cmd == "record":
        record(sys.argv[2])
    elif cmd == "build":
        build(sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--artifact" else None)
    else:
        status()
