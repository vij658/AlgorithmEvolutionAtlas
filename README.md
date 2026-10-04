# The Algorithm Evolution Atlas

*A historian's journey through algorithms, from adding two numbers to the algorithms of 2026, told as a story of needs: every algorithm enters as the fix for something that hurt.*

The repository has two halves:

| Folder | What is in it |
|---|---|
| [`book/`](book/README.md) | **The book.** The design, the reference catalog (era by era, with checked video, lecture, article and original-source links for every topic), chapter outlines and history fact sheets, and the earlier *principles catalog* as a companion volume. All Markdown, readable on GitHub. |
| [`code/`](code/README.md) | **The code.** One folder per algorithm. Each folder has a self-contained Java program with a header comment explaining how it works, a README with the idea in depth and its references, and the exact output the program prints. Plus the tools that build the book's pages. |

## How the book is built

- **A strict timeline.** Each development appears when it was invented: tally marks, written numerals, Babylonian tables, Euclid … the stored-program computer … transformers and the algorithms of 2026. Programming fundamentals (the loop, the function, the object, the thread) appear in the same timeline, in the year they were invented.
- **One question for every algorithm: what hurt?** The reader is asked to name the pain and rebuild the fix before being shown it.
- **Two readers at once.** Every topic has a *Start* path a high-school student can follow, and *Deeper* and *Scholar* paths with the proofs, the original papers and the arguments among historians.
- **Nothing unverified.** Every link was opened before it was listed; every historical claim carries a label (*documented*, *conjecture*, *disputed*, *reconstructed*, *myth*); every number quoted comes from a program's output; every code block is copied from a program that was compiled and run.
- **The Evolutionary Atlas** (the 180-chapter table of contents developed earlier) supplies the chapter map, the ⊕ notation (*A ⊕ B = C*: a new algorithm is an older idea combined with a new one), the full-circle callouts to machine learning, and the Pattern/Blind/Foundation problem labels. The book's topics point to Atlas chapters.

## Status (October 2026)

| Piece | State |
|---|---|
| Reference catalog, Era 1 (tally marks to the sieve, 9 topics) | Done: 123 checked links ([read it](book/era-01-the-first-algorithms/reference-catalog.md)) |
| Chapter 1, *Two numbers, one answer* | Program verified (14,072,170 checks); history checked; outline written; chapter text not written |
| Reference catalog, Era 2 onward | Not started |
| Principles catalog, Parts 1–2 (entries 1–42) | Pages written; 42 programs verified (8,135,522 checks) |
| Principles catalog, Part 3 (entries 43–62) | 20 programs verified (154,369,152 checks); page not written |

## Run the code

JDK 17 or newer; no build tool. Every program is a single file:

```
cd code/principles/part-1-distances-and-number-theory/01-euclidean-algorithm
java EuclideanAlgorithm.java
```

To run everything and compare each program's output with its `expected-output.txt`:

```
bash code/run-all.sh
```

## License

Apache License 2.0; see [LICENSE](LICENSE).
