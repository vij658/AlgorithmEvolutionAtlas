# The book

*Working title: **Why Algorithms Exist** — a historian's journey from adding two numbers to 2026.*

> A historian from another planet has come to catalog how this species learned to compute. For every new development the historian records when it appeared, what problem forced it, what it changed, and where the evidence can be seen. The book follows those field notes in order of time, and asks the same question of every algorithm: **what hurt?**

## How to read it

- **Start** links and sections need no background. **Deeper** is university level. **Scholar** is the primary sources and the research literature.
- Historical claims carry labels: **documented**, **conjecture**, **disputed**, **reconstructed** (an imagined scene around documented facts), **myth** (a popular story the sources contradict).
- Every chapter ends with *Prove it*: a Java program in [`code/`](../code/README.md) that was compiled and run. Every number quoted in the book comes from a program's output.
- *A ⊕ B = C* marks a new algorithm built by combining an older idea with a new one. *Full circle* marks where an old idea returns in modern computing, especially machine learning.

## Contents

### About the book

- [Design decisions](00-about-the-book/design-decisions.md): what was asked for, what was decided, and what is open.
- [Page kit design](00-about-the-book/page-kit-design.md): how a chapter becomes a page.

### Era 1 — The first algorithms (c. 44,000 years ago to c. 240 BCE)

- **[Era 1 front page](era-01-the-first-algorithms/README.md)**: the time line, a map of how the nine ideas combine, and the topics. [Interactive edition](era-01-the-first-algorithms/index.html) (download the folder and open `index.html` in a browser).
- [Reference catalog](era-01-the-first-algorithms/reference-catalog.md): each development with checked videos, lectures, articles and original sources, certainty labels and gaps.
- The topics. Each has a GitHub edition (diagrams, tables, fold-out answers), an interactive edition (one HTML page with a widget), and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [Tally Marks](era-01-the-first-algorithms/01-tally-marks/README.md) | Pair sheep with stones; switch between readings of the Ishango bone |
| 2 | [Grouping and the First Carry](era-01-the-first-algorithms/02-grouping-and-the-first-carry/README.md) | Pool and exchange in Egyptian or Sumerian signs |
| 3 | [Babylonian Place Value](era-01-the-first-algorithms/03-babylonian-place-value/README.md) | Read a number in wedges; divide with the reciprocal table |
| 4 | [The Square Root of Two](era-01-the-first-algorithms/04-square-root-of-two/README.md) | Square up a rectangle by averaging |
| 5 | [Egyptian Doubling](era-01-the-first-algorithms/05-egyptian-doubling/README.md) | Double and tick; switch to square-and-multiply |
| 6 | [Counting Boards](era-01-the-first-algorithms/06-counting-boards/README.md) | Push counters and settle, with or without fives |
| 7 | [Euclid's Algorithm](era-01-the-first-algorithms/07-euclids-algorithm/README.md) | Cut squares from a rectangle |
| 8 | [Archimedes Squeezes Pi](era-01-the-first-algorithms/08-archimedes-pi/README.md) | Double a polygon's sides, with a magnified gap |
| 9 | [The Sieve of Eratosthenes](era-01-the-first-algorithms/09-sieve-of-eratosthenes/README.md) | Sieve by primes, by every odd number, or by every number |

- Chapter 1, *Two numbers, one answer*: [outline](era-01-the-first-algorithms/chapter-01-adding-two-numbers/outline.md) · [history fact sheet](era-01-the-first-algorithms/chapter-01-adding-two-numbers/history-fact-sheet.md) · [program](../code/chapter-01-adding-two-numbers/README.md)
- The pages are built from the programs' outputs by [`code/tools/book/build.py`](../code/tools/book/build.py); see [the tools README](../code/tools/README.md).

### Coming next (proposed eras; open to change)

| Era | Span | Topics (from the Evolutionary Atlas) |
|---|---|---|
| 2 | c. 500–1500 CE | Indian zero and positional arithmetic, al-Khwarizmi and the word "algorithm", al-Kindi's frequency analysis, Fibonacci's *Liber Abaci*, the pulverizer (extended Euclid) |
| 3 | 1600–1900 | Logarithms and Napier's bones, Pascal's and Leibniz's calculators, binary, Newton's method, Gauss and least squares, Babbage and Lovelace, Boole |
| 4 | 1900–1950 | Hilbert's program, Gödel, Turing machines, the lambda calculus, Shannon's switching circuits, the stored-program computer, merge sort (von Neumann) |
| 5 onward | 1950–2026 | The loop and the subroutine, sorting and searching, data structures, graphs, dynamic programming, complexity, cryptography, databases, networks, distributed systems, streaming, machine learning, transformers, and the algorithms of 2026 |

### Plans

- [Sample B — Finding a word](plans/sample-B-finding-a-word.md): deriving Rabin–Karp from the pain of plain string search (plan only).

### Companion volume: the principles catalog

- [The principles catalog](principles-catalog/README.md): 62 named principles with verified Java. Parts 1 and 2 are written; Part 3's programs are verified and its page is not written.
