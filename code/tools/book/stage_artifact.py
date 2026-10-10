#!/usr/bin/env python3
"""Stage an era's interactive edition for publishing as one multi-file web page.

  python3 code/tools/book/stage_artifact.py OUTDIR

Writes OUTDIR/index.html (the era front page, without its own <!doctype> wrapper, because the host adds one) and
OUTDIR/NN-topic/topic.html for every built topic (full documents). The host stores the front page as index.html, so the
topics' links back to ../index.html work unchanged.
"""
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "topics"))
import era01  # noqa: E402
import era_index  # noqa: E402

ROOT = HERE.parents[2]
BOOK, CODE = ROOT / "book", ROOT / "code"


def main():
    out = pathlib.Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    era = era01
    folder = BOOK / era.ERA["folder"]
    catalog = (folder / "reference-catalog.md").read_text()
    chain = era_index.chain_rows(catalog)
    D = era_index.era_map(era)
    label = f"Era {era.ERA['num']}: {era.ERA['title']}, from {era.ERA['span']}"
    index = era_index.render_index_html(era, BOOK, CODE, chain, D, era.timeline_events(), label, standalone_doc=False)
    (out / "index.html").write_text(index)
    for t in era.TOPICS:
        if not era_index.built(era, t, BOOK, CODE):
            continue
        rel = f"{t[0]:02d}-{t[1]}/{t[1]}.html"
        html = (folder / rel).read_text()                         # the host stores the front page as index.html
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_text(html)
        print(rel)


if __name__ == "__main__":
    main()
