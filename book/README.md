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

### Era 2 — Algorithms travel (c. 200 BCE to 1424 CE)

- **[Era 2 front page](era-02-algorithms-travel/README.md)**: the time line, a map of how the eleven ideas combine, and the topics. [Interactive edition](era-02-algorithms-travel/index.html) (download the folder and open `index.html` in a browser). [Plan](era-02-algorithms-travel/plan.md).
- [Reference catalog](era-02-algorithms-travel/reference-catalog.md): each development with checked videos, lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [Elimination on the Counting Board](era-02-algorithms-travel/01-fangcheng/README.md) | Work the board |
| 2 | [Ptolemy's Table of Chords](era-02-algorithms-travel/02-ptolemys-chords/README.md) | Read the table, and walk Ptolemy's route |
| 3 | [The Chinese Remainder Problem](era-02-algorithms-travel/03-chinese-remainder-problem/README.md) | Count in threes, fives and sevens |
| 4 | [Zero Becomes a Number](era-02-algorithms-travel/04-zero-becomes-a-number/README.md) | Read it without a zero |
| 5 | [The Chakravala and Pell's Equation](era-02-algorithms-travel/05-chakravala/README.md) | Run the cycle |
| 6 | [Algorism and Al-Jabr](era-02-algorithms-travel/06-algorism-and-al-jabr/README.md) | Restore, balance, and follow the recipe |
| 7 | [Frequency Analysis](era-02-algorithms-travel/07-frequency-analysis/README.md) | Break a cipher |
| 8 | [Fibonacci's Liber Abaci](era-02-algorithms-travel/08-liber-abaci/README.md) | Breed the rabbits; multiply like a merchant |
| 9 | [Horner's Method, Nearly Six Centuries Early](era-02-algorithms-travel/09-qin-jiushao/README.md) | Find a root one digit at a time |
| 10 | [Madhava's Series for Pi](era-02-algorithms-travel/10-madhava-series/README.md) | Add terms, then correct for the rest |
| 11 | [Al-Kashi's Pi](era-02-algorithms-travel/11-al-kashi-pi/README.md) | Double the sides until the error is a horse's hair |

### Era 3 — Tables and Machines (1545 to 1890 CE)

- **[Era 3 front page](era-03-tables-and-machines/README.md)**: the time line, a map of how the thirteen ideas combine, and the topics. [Interactive edition](era-03-tables-and-machines/index.html) (download the folder and open `index.html` in a browser). [Plan](era-03-tables-and-machines/plan.md).
- [Reference catalog](era-03-tables-and-machines/reference-catalog.md): each development with checked lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [Cardano's Cubic](era-03-tables-and-machines/01-cardanos-cubic/README.md) | Follow the recipe, even through √−1 |
| 2 | [Logarithms](era-03-tables-and-machines/02-logarithms/README.md) | Multiply by adding; build the table from square roots |
| 3 | [The Carry, Mechanized](era-03-tables-and-machines/03-mechanical-carry/README.md) | Turn the wheels and watch the carries |
| 4 | [The Problem of Points](era-03-tables-and-machines/04-problem-of-points/README.md) | Fill in Pascal's table |
| 5 | [Newton's Method](era-03-tables-and-machines/05-newtons-method/README.md) | Follow the tangent |
| 6 | [Binary Arithmetic](era-03-tables-and-machines/06-binary-arithmetic/README.md) | Flip the bits |
| 7 | [The Bridges of Königsberg](era-03-tables-and-machines/07-konigsberg-bridges/README.md) | Cross every bridge once |
| 8 | [Least Squares, and the Lost Planet](era-03-tables-and-machines/08-least-squares/README.md) | Drag the points; watch the squares |
| 9 | [Gauss's Fast Fourier Transform](era-03-tables-and-machines/09-gauss-fft/README.md) | Fit twelve observations, then split them |
| 10 | [Babbage's Difference Engine](era-03-tables-and-machines/10-difference-engine/README.md) | Turn the handle |
| 11 | [Lovelace's Note G](era-03-tables-and-machines/11-note-g/README.md) | Run the cards |
| 12 | [Boole's Algebra of Logic](era-03-tables-and-machines/12-boolean-algebra/README.md) | Check a syllogism by algebra |
| 13 | [Hollerith's Tabulator](era-03-tables-and-machines/13-hollerith-tabulator/README.md) | Punch a card, feed the press |

### Era 4 — What Can Be Computed (1895 to 1950)

- **[Era 4 front page](era-04-what-can-be-computed/README.md)**: the time line, a map of how the thirteen ideas combine, and the topics. [Interactive edition](era-04-what-can-be-computed/index.html) (download the folder and open `index.html` in a browser). [Plan](era-04-what-can-be-computed/plan.md).
- [Reference catalog](era-04-what-can-be-computed/reference-catalog.md): each development with checked lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [Hilbert's Questions](era-04-what-can-be-computed/01-hilberts-questions/README.md) | Search for a solution, or prove there is none |
| 2 | [Runge–Kutta](era-04-what-can-be-computed/02-runge-kutta/README.md) | Keep a spring on its circle |
| 3 | [Markov Chains](era-04-what-can-be-computed/03-markov-chains/README.md) | Write a text with a one-letter memory |
| 4 | [The Cheapest Network](era-04-what-can-be-computed/04-cheapest-network/README.md) | Wire forty towns, Borůvka's way or Jarník's |
| 5 | [Gödel's Numbering](era-04-what-can-be-computed/05-godel-numbering/README.md) | Turn a formula into a number |
| 6 | [Church's Lambda Calculus](era-04-what-can-be-computed/06-lambda-calculus/README.md) | Compute by substitution |
| 7 | [Turing's Machines](era-04-what-can-be-computed/07-turing-machines/README.md) | Run a machine, and read its number |
| 8 | [Breaking Enigma](era-04-what-can-be-computed/08-breaking-enigma/README.md) | Type on an Enigma |
| 9 | [The Stored Program, and Merge Sort](era-04-what-can-be-computed/09-stored-program/README.md) | Run a program that lives in its own data |
| 10 | [Monte Carlo](era-04-what-can-be-computed/10-monte-carlo/README.md) | Throw points; make your own random numbers |
| 11 | [The Simplex Method](era-04-what-can-be-computed/11-simplex-method/README.md) | Walk the corners |
| 12 | [Shannon's Bits](era-04-what-can-be-computed/12-information-theory/README.md) | Switches, and imitation English |
| 13 | [Hamming's Codes](era-04-what-can-be-computed/13-hamming-codes/README.md) | Flip a bit and watch the checks find it |

### Coming next (proposed eras; open to change)

| Era | Span | Topics (from the Evolutionary Atlas) |
|---|---|---|
| 5 onward | 1950–2026 | The loop and the subroutine, sorting and searching, data structures, graphs, dynamic programming, complexity, cryptography, databases, networks, distributed systems, streaming, machine learning, transformers, and the algorithms of 2026 |

### Plans

- [Sample B — Finding a word](plans/sample-B-finding-a-word.md): deriving Rabin–Karp from the pain of plain string search (plan only).

### Companion volume: the principles catalog

- [The principles catalog](principles-catalog/README.md): 62 named principles with verified Java. Parts 1 and 2 are written; Part 3's programs are verified and its page is not written.
