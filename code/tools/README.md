# Tools

Small Python 3 scripts that build and check the book's pages.

| Script | What it does |
|---|---|
| `build_html.py` | Builds one self-contained HTML page (light and dark themes, phone layout, highlighted code with copy buttons, downloadable programs) from a Markdown chapter and the Java programs named in its front matter |
| `expand.py` | Expands `@@ File.java: member …` lines in a Markdown file into fenced Java blocks copied verbatim from the tested program, so the book never shows code that was not run |
| `shot.py` | Renders a built page in headless Chromium: checks anchors and horizontal overflow, and takes screenshots at desktop-light, desktop-dark and phone widths |
| `book/build.py` | Builds the visual topic pages of the book and each era's front page, in two editions, from the programs' outputs (see below) |
| `book/check.py` | Opens built topic pages in headless Chromium (desktop light, desktop dark, phone dark), reports script errors, sideways scrolling and broken anchors, and saves screenshots |

## The visual book (`book/`)

Every topic page is built from one *spec*, which renders to two editions:

- **GitHub edition**: `book/<era>/<NN-topic>/README.md`, with box-and-arrow diagrams as SVG files (a light and a dark copy, chosen by GitHub's theme) and Markdown tables.
- **Interactive edition**: `book/<era>/<NN-topic>/<topic>.html`, one self-contained page with the same diagrams inline, a widget to play with, and fold-out answers.

| File | Role |
|---|---|
| `book/build.py` | Runs the build: reads each program's `expected-output.txt`, calls the topic module, writes both editions, then the era index |
| `book/era01.py` | Era 1's topics in order, its time line labels, and the era map (which idea each development reuses) |
| `book/era_index.py` | The era front page: time line, era map and one card per topic (planned topics link to the reference catalog) |
| `book/page.py` | The spec format and both renderers |
| `book/diagrams.py` | The box-and-arrow renderer shared by both editions |
| `book/base.css` | The page style (Byrne's 1847 *Elements*: red, yellow and blue on white) |
| `book/topics/tNN_*.py` | One module per topic: `build(ctx)` returns the spec, with every number parsed from the program's output |
| `book/topics/common.py` | Shared pieces: drawn placeholders for objects, the era time line block, *Prove it* and *Watch and read* sections |

```
python3 code/tools/book/build.py              # every topic whose program output exists, then the era index
python3 code/tools/book/build.py --run 1 7    # run topics 1 and 7's programs first, saving expected-output.txt
python3 code/tools/book/check.py /tmp/shots book/era-01-the-first-algorithms/*/*.html
```

Rules the builder keeps: numbers on a page come from the program's output, never typed by hand; every link comes from
the era's reference catalog, where each was opened before it was listed; photographs are shown only when their licence
allows it (CC0 or public domain), and drawn placeholders are labelled as drawings.

## Requirements

```
pip install markdown pygments        # build_html.py, expand.py, book/build.py (markdown)
pip install playwright               # shot.py and book/check.py; they also need a Chromium
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
