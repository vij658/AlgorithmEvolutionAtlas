# Design decisions

*Status, October 2026: the design is settled, Era 1's reference catalog is written, and chapter 1's program and history are verified. The chapter text is not written yet. This note records what was asked for, what was decided, and what is open.*

Related: [Era 1 reference catalog](../era-01-the-first-algorithms/reference-catalog.md) · [Chapter 1 outline](../era-01-the-first-algorithms/chapter-01-adding-two-numbers/outline.md) · [Chapter 1 history fact sheet](../era-01-the-first-algorithms/chapter-01-adding-two-numbers/history-fact-sheet.md) · [Page kit design](page-kit-design.md) · [Chapter 1 program](../../code/chapter-01-adding-two-numbers/README.md)

## What was asked for

1. **A book about why algorithms evolved, not a list of them.** "Think like a historian who time travels … the main target is to make the readers understand the logical nature of it rather than saying here is Rabin–Karp." Start with adding two numbers; think deeply about the history.
2. **A historical journey from simple addition to 2026**, written by "a historian from another planet" who catalogs every new development from the time it was created.
3. **Head First style:** a high-school student can follow it, and a PhD scholar can track the evolution in depth.
4. **References for every topic** (videos, lectures, blogs, original sources), so the reader never has to search.
5. **Java** for the code.
6. **Book and code kept separately**, with every program in its own folder, commented, and carrying its documents and references.

## Choices made with the author

| Question | Choice |
|---|---|
| How is the book ordered? | **Strict timeline.** Each development appears when it was invented. Atlas chapter numbers and Pattern/Blind/Foundation labels are cross-references. |
| What comes first? | **The reference catalog**, era by era: date, who, what problem it solved, and checked links. Chapters are written on top of it. |
| Where do programming fundamentals (loops, functions, objects, async, garbage collection) go? | **Woven into the timeline**: the FORTRAN DO loop in 1957, Simula's objects in 1967, alongside the algorithms of the same years. |
| Which references? | **All four kinds:** explainer videos, lectures, blog articles, original sources. |

## How this book relates to the Evolutionary Atlas

The Atlas (31 table-of-contents installments, about 180 chapters, plus ML-era notes) is the map. This book keeps from it:

- its chapter list as the inventory of topics, re-ordered by date of invention;
- the ⊕ notation, *A ⊕ B = C*, for a new algorithm made by combining an older idea with a new one;
- the *Came from / Leads to* signposts, which become the "what hurt" chain;
- the full-circle callouts to machine learning;
- the Pattern/Blind/Foundation labels, so each topic links to practice problems.

What changes: the Atlas orders its middle eras by pattern family (two pointers, hashing, trees …). The book orders everything by time, so a reader watches each idea appear in response to a need.

## Decisions

1. **One question for every algorithm: "What hurt?"** Each algorithm enters as the fix for a pain the previous one left. The reader is asked to name the pain and rebuild the fix before seeing it.
2. **The historian's voice.** Each topic opens with a short *field note* from the visiting historian: an outsider's view, which makes familiar things strange enough to explain.
3. **Three reading levels on every topic:** *Start* (no background), *Deeper* (university), *Scholar* (primary sources and the research debate). Links are tagged with the same levels.
4. **Labels on every historical claim:** *documented*, *conjecture*, *disputed*, *reconstructed* (an imagined scene around documented facts, with invented wording), *myth* (a popular story the sources contradict).
5. **Devices, kept light, in every chapter:** *Pause and try* (an exercise, answer hidden), *Wrong turn* (the obvious idea that fails), *Time-travel scene* (always labelled reconstructed), *A ⊕ B = C*, *Full circle*, *Key idea*, *Prove it* (the Java, after the idea has been derived by hand).
6. **Verification rules.** Every link is opened before it is listed (YouTube links are checked against YouTube's own title record). Every number in the text comes from a program's output. Every code block is copied verbatim from a program that was compiled and run. Gaps are listed, not papered over.
7. **Code layout.** `code/` holds one folder per program: the Java file with a header comment that explains how it works, a README with the idea in depth and the references, and `expected-output.txt`. Programs are single files run with `java File.java`, need no build tool, and use fixed random seeds so the output reproduces exactly.
8. **The principles catalog is a companion volume.** Its 62 verified programs are reused as *Prove it* layers when the timeline reaches their topics.

## What exists

| Piece | State |
|---|---|
| Era 1 reference catalog (9 topics, 123 checked links) | Done |
| Chapter 1 program (`AddingTwoNumbers.java`) | Verified: 14,072,170 checks passed |
| Chapter 1 history | Checked against sources; see the fact sheet |
| Chapter 1 text | **Not written.** The outline is the plan |
| Sample B (finding a word, Rabin–Karp) | Plan only; history not yet verified |
| Page kit | `expand.py` built and tested; the chapter builder is designed, not built |
| Principles catalog | Parts 1–2 written; Part 3 programs verified, page not written; all 62 programs split into their own folders |

## Open items

- **Era boundaries.** The proposed eras in the [book's contents](../README.md) are a first cut.
- **Chapter length.** The chapter 1 outline implies a long chapter (about 6,000–8,000 words with code).
- **Interactive pieces** (a counting board to push counters on, a carry-ripple slider) for the HTML edition.
- **References for the 62 catalog programs.** Most have the catalog's sources only; video and article links are added as the reference catalog reaches each topic.
