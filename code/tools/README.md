# Tools

Small Python 3 scripts that build and check the book's pages.

| Script | What it does |
|---|---|
| `build_html.py` | Builds one self-contained HTML page (light and dark themes, phone layout, highlighted code with copy buttons, downloadable programs) from a Markdown chapter and the Java programs named in its front matter |
| `expand.py` | Expands `@@ File.java: member …` lines in a Markdown file into fenced Java blocks copied verbatim from the tested program, so the book never shows code that was not run |
| `shot.py` | Renders a built page in headless Chromium: checks anchors and horizontal overflow, and takes screenshots at desktop-light, desktop-dark and phone widths |
| `figures/euclid_topic.py` | Builds the visual topic page for Euclid's algorithm from its program's output: SVG figures (light and dark), the GitHub README, and the interactive HTML edition (from `figures/euclid-page.html`) |

## Requirements

```
pip install markdown pygments        # build_html.py, expand.py
pip install playwright               # shot.py only; it also needs a Chromium
```

## Rebuild the two catalog pages

From the repository root:

```
python3 code/tools/build_html.py book/principles-catalog/part-1-distances-and-number-theory.md book/principles-catalog/html/part-1-distances-and-number-theory.html
python3 code/tools/build_html.py book/principles-catalog/part-2-paradigms-and-classics.md book/principles-catalog/html/part-2-paradigms-and-classics.html
```

The front matter's `Java:` line names the programs to embed, relative to the Markdown file; a glob such as
`../../code/principles/part-1-distances-and-number-theory/*/*.java` embeds every entry's program in folder order.

## Expand code directives

```
python3 code/tools/expand.py chapter.md chapter.expanded.md --report
```

A directive looks like `@@ AddingTwoNumbers.java: value addColumns`; the Java file is looked up next to the Markdown file.
A range `first..last` copies everything between two members. The report lists the widest line of each block.
