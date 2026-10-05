# The code

Every program is a single Java file in its own folder, with:

- a **header comment** that explains how the algorithm works and how the file is organised;
- a **README.md** with the idea in depth, how to run it, the program's full output, and references (videos, lectures, articles, original sources);
- **expected-output.txt**, exactly what the program prints. Randomized checks use fixed seeds, so the output reproduces.

Each program counts the checks it makes (known answers, edge cases, randomized comparisons against a slower reference) and prints the count last. A failed check throws an `AssertionError` and exits with a non-zero status.

## Layout

| Folder | What is in it |
|---|---|
| [`chapter-01-adding-two-numbers/`](chapter-01-adding-two-numbers/README.md) | The book's chapter 1 program: carries, counting boards, carry-lookahead |
| [`era-01-the-first-algorithms/`](era-01-the-first-algorithms/07-euclids-algorithm/EuclidsAlgorithm.java) | The book's topic programs, one folder per topic (so far: topic 7, Euclid's algorithm) |
| [`principles/`](principles/README.md) | The 62 programs of the principles catalog, one folder per entry, grouped by part |
| [`tools/`](tools/README.md) | Python scripts that build and check the book's pages |
| [`run-all.sh`](run-all.sh) | Runs every program and compares its output with `expected-output.txt` |

As the book's chapters are written, each gets its own `chapter-NN-…` folder here.

## Run one program

```
cd code/principles/part-2-paradigms-and-classics/33-dijkstra
java Dijkstra.java
```

JDK 17 or newer. No build tool and no dependencies: `java File.java` compiles and runs a single-file program.

## Run everything

```
bash code/run-all.sh            # all programs
bash code/run-all.sh dijkstra   # only folders whose path contains "dijkstra"
```

## Verified results

Runs on OpenJDK 21.0.12; every program exited with status 0.

| Collection | Programs | Checks passed |
|---|---|---|
| Chapter 1 | 1 | 14,072,170 |
| Part 1 — Distances, similarity and number theory (entries 1–20) | 20 | 1,221,141 |
| Part 2 — Algorithm paradigms and classics (entries 21–42) | 22 | 6,914,381 |
| Part 3 — Performance laws and distributed systems (entries 43–62) | 20 | 154,369,152 |
| **Total** | **63** | **176,576,844** |
