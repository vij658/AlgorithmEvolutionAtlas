#!/usr/bin/env python3
"""Build the book's topic pages (GitHub and interactive editions) and the era index from the programs' outputs.

  python3 code/tools/book/build.py            build every topic whose program output exists, then the era index
  python3 code/tools/book/build.py 1 7        build only topics 1 and 7 (and the era index)
  python3 code/tools/book/build.py --run 7    run topic 7's program first and save its output as expected-output.txt

Topic modules live in code/tools/book/topics/; each has build(ctx) -> spec (see page.py for the spec format).
"""
import importlib
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "topics"))
import diagrams  # noqa: E402
import era01  # noqa: E402
import page  # noqa: E402

ROOT = HERE.parents[2]
BOOK = ROOT / "book"
CODE = ROOT / "code"


def topic_paths(era, t):
    num, slug = t[0], t[1]
    folder = f"{num:02d}-{slug}"
    return BOOK / era.ERA["folder"] / folder, CODE / era.ERA["folder"] / folder


def nav_for(era, i):
    topics = era.TOPICS
    t = topics[i]
    prev_t = topics[i - 1] if i > 0 else None
    next_t = topics[i + 1] if i + 1 < len(topics) else None
    rel = lambda x: f"../{x[0]:02d}-{x[1]}/"
    md = [f"[Era {era.ERA['num']} index](../README.md)"]
    html = [f'<a href="../index.html">Era {era.ERA["num"]}: {page.esc(era.ERA["title"])}</a>']
    if prev_t:
        md.append(f"[← {prev_t[2]}]({rel(prev_t)}README.md)")
        html.append(f'<a href="{rel(prev_t)}{prev_t[1]}.html">← {page.esc(prev_t[2])}</a>')
    if next_t:
        md.append(f"[{next_t[2]} →]({rel(next_t)}README.md)")
        html.append(f'<a href="{rel(next_t)}{next_t[1]}.html">{page.esc(next_t[2])} →</a>')
    book_dir, code_dir = topic_paths(era, t)
    return dict(md=" · ".join(md), html="".join(html), code_rel=os.path.relpath(code_dir, book_dir) + "/")


def run_program(code_dir, cls):
    env = {k: v for k, v in os.environ.items() if k != "JAVA_TOOL_OPTIONS"}
    r = subprocess.run(["java", f"{cls}.java"], cwd=code_dir, capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise SystemExit(f"{cls} failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}")
    (code_dir / "expected-output.txt").write_text(r.stdout)
    return r.stdout


def build_topic(era, i, run=False):
    t = era.TOPICS[i]
    num, slug, title, date, label, module, cls = t
    book_dir, code_dir = topic_paths(era, t)
    out_file = code_dir / "expected-output.txt"
    if run:
        run_program(code_dir, cls)
    if not out_file.exists():
        return None
    mod = importlib.import_module(module)
    catalog = (BOOK / era.ERA["folder"] / "reference-catalog.md").read_text()
    ctx = dict(out=out_file.read_text(), java=(code_dir / f"{cls}.java").read_text(), catalog=catalog, era=era, index=i,
               topic=t, code_dir=code_dir, book_dir=book_dir, repo_url=page.REPO_URL)
    spec = mod.build(ctx)
    spec.setdefault("era", era.ERA["num"])
    spec.setdefault("num", num)
    spec.setdefault("slug", slug)
    spec.setdefault("title", title)
    spec.setdefault("date", date)
    nav = nav_for(era, i)
    book_dir.mkdir(parents=True, exist_ok=True)
    (book_dir / "README.md").write_text(page.render_md(spec, book_dir, nav) + "\n")
    (book_dir / f"{slug}.html").write_text(page.render_html(spec, nav))
    (code_dir / "README.md").write_text(code_readme(era, t, spec, ctx["java"], nav))
    warnings = [w for b in all_blocks(spec) if b["type"] == "diagram" for w in b["diagram"].warnings]
    for w in warnings:
        print("  warning:", w)
    print(f"built topic {num}: {title}")
    return spec


def javadoc_section(java, heading):
    """The lines under `HEADING` in the program's header comment, up to the next heading (a line starting with a
    capitalised word right after the comment's star) or the end of the comment."""
    import re
    import textwrap
    out, on = [], False
    for ln in java.split("\n"):
        if ln.strip().startswith("*/"):
            break
        body = re.sub(r"^\s*/?\*+", "", ln)
        if re.match(r"^ ?[A-Z][A-Z]{2,}", body):
            if on:
                break
            on = body.strip() == heading
            continue
        if on:
            out.append(body)
    while out and not out[-1].strip():
        out.pop()
    return textwrap.dedent("\n".join(out))


def code_readme(era, t, spec, java, nav):
    num, slug, title, date, label, module, cls = t
    book_rel = os.path.relpath(topic_paths(era, t)[0], topic_paths(era, t)[1])
    L = [f"# {title}: the program", "",
         f"*Era {era.ERA['num']} · topic {num} · {date}* · Book page: [GitHub edition]({book_rel}/README.md) · "
         f"[interactive edition]({book_rel}/{slug}.html) · [All era {era.ERA['num']} programs](../README.md)", ""]
    how = javadoc_section(java, "HOW IT WORKS")
    what = javadoc_section(java, "WHAT THIS PROGRAM DOES")
    if how:
        L += ["## How it works", "", "```text", how, "```", ""]
    if what:
        L += ["## What the program does", "", "```text", what, "```", ""]
    L += ["## Run it", "", "```", f"java {cls}.java        # JDK 17 or newer, no build step", "```", "",
          "The output must match [`expected-output.txt`](expected-output.txt) line for line; "
          "[`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. "
          "Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, "
          "so every number in the book comes from this program.", ""]
    links = [b for s in spec["sections"] for b in s["blocks"] if b["type"] == "links"]
    if links:
        L += ["## Watch and read", "", "| Level | Link | Why |", "|---|---|---|"]
        for lvl, ltitle, source, url, why in links[0]["items"]:
            L.append(f"| {lvl.capitalize()} | [{ltitle}]({url}) — {source} | {why} |")
        L += ["", f"Every link was opened before it was listed. More, with certainty labels: "
                  f"[Era {era.ERA['num']} reference catalog](../../../book/{era.ERA['folder']}/reference-catalog.md).", ""]
    return "\n".join(L)


def era_code_readme(era):
    L = [f"# Era {era.ERA['num']} programs — {era.ERA['title']}", "",
         f"*{era.ERA['span']}* · [Era {era.ERA['num']} in the book](../../book/{era.ERA['folder']}/README.md) · "
         f"[All programs](../README.md)", "",
         "One folder per topic. Each holds a single-file Java program (run it with `java File.java`, JDK 17 or newer), "
         "the output it must print, and a README with how it works and where to watch and read more.", "",
         "| # | Topic | When | Program | Checks |", "|---|---|---|---|---|"]
    import re
    for t in era.TOPICS:
        folder = f"{t[0]:02d}-{t[1]}"
        out = CODE / era.ERA["folder"] / folder / "expected-output.txt"
        if out.exists():
            m = re.search(r": (\d+) checks passed", out.read_text())
            L.append(f"| {t[0]} | [{t[2]}]({folder}/README.md) | {t[3]} | [`{t[6]}.java`]({folder}/{t[6]}.java) | {int(m.group(1)):,} |")
        else:
            L.append(f"| {t[0]} | {t[2]} | {t[3]} | planned | |")
    return "\n".join(L) + "\n"


def all_blocks(spec):
    for s in spec["sections"]:
        for b in s["blocks"]:
            yield b
            if b["type"] == "details":
                yield b["block"]


def main():
    args = sys.argv[1:]
    run = "--run" in args
    nums = {int(a) for a in args if a.isdigit()}
    era = era01
    for i, t in enumerate(era.TOPICS):
        if nums and t[0] not in nums:
            continue
        build_topic(era, i, run=run)
    (CODE / era.ERA["folder"] / "README.md").write_text(era_code_readme(era))
    import era_index
    era_index.build(era, BOOK, CODE)


if __name__ == "__main__":
    main()
