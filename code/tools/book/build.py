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
    warnings = [w for b in all_blocks(spec) if b["type"] == "diagram" for w in b["diagram"].warnings]
    for w in warnings:
        print("  warning:", w)
    print(f"built topic {num}: {title}")
    return spec


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
    import era_index
    era_index.build(era, BOOK, CODE)


if __name__ == "__main__":
    main()
