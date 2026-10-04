# The principles catalog (companion volume)

Named, mathematically grounded principles that keep showing up in real code, each explained from scratch and each backed by a Java program that was compiled, run and checked. It came before the book and is organized by topic, not by time; the book reuses its programs as *Prove it* layers when the timeline reaches each topic.

| Part | Entries | Text | Programs |
|---|---|---|---|
| [Part 1 — Distances, similarity and number theory](part-1-distances-and-number-theory.md) | 1–20 | Written | [20 programs](../../code/principles/README.md#part-1--distances-similarity-and-number-theory-entries-120), 1,221,141 checks |
| [Part 2 — Algorithm paradigms and classics](part-2-paradigms-and-classics.md) | 21–42 | Written | [22 programs](../../code/principles/README.md#part-2--algorithm-paradigms-and-classics-entries-2142), 6,914,381 checks |
| [Part 3 — Performance laws and distributed systems](part-3-status-and-plan.md) | 43–62 | **Not written** (status and plan) | [20 programs](../../code/principles/README.md#part-3--performance-laws-and-distributed-systems-entries-4362), 154,369,152 checks |
| Part 4 — Security and identity | | Not started | |
| Part 5 — Design laws and engineering principles | | Not started | |

## Reading the pages

The Markdown pages read directly on GitHub. Self-contained HTML editions (light and dark themes, phone layout, copy buttons, every program embedded and downloadable) are in [`html/`](html/); download one and open it in a browser. To rebuild them, see [the tools](../../code/tools/README.md).

## A note on the numbers

Each entry's program used to be one section of a larger file sharing one random-number stream. When the programs were split into one folder per entry, each got its own fixed seed, so a few measured numbers changed slightly (for example the mean Hamming distance of random codes, 0.4987 → 0.5006). The pages were updated to match the new outputs; every number on them now comes from the program in that entry's folder.
