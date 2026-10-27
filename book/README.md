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

### Era 5 — The Programmer's Craft (1949 to 1965)

- **[Era 5 front page](era-05-the-programmers-craft/README.md)**: the time line, a map of how the thirteen ideas combine, and the topics. [Interactive edition](era-05-the-programmers-craft/index.html) (download the folder and open `index.html` in a browser). [Plan](era-05-the-programmers-craft/plan.md).
- [Reference catalog](era-05-the-programmers-craft/reference-catalog.md): each development with checked lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [The Subroutine](era-05-the-programmers-craft/01-the-subroutine/README.md) | Step through a call and watch the way home being written |
| 2 | [Regular Expressions](era-05-the-programmers-craft/02-regular-expressions/README.md) | Type a pattern and watch the machine read |
| 3 | [Huffman's Codes](era-05-the-programmers-craft/03-huffman-codes/README.md) | Type a phrase and grow its tree |
| 4 | [Hashing](era-05-the-programmers-craft/04-hashing/README.md) | Store keys, make them collide, find them again |
| 5 | [Dynamic Programming](era-05-the-programmers-craft/05-dynamic-programming/README.md) | Roll, or stop? Ask the table |
| 6 | [Linked Lists and Garbage Collection](era-05-the-programmers-craft/06-linked-lists/README.md) | Make garbage, then collect it |
| 7 | [Dijkstra's Shortest Paths](era-05-the-programmers-craft/07-shortest-paths/README.md) | Grow the settled set, one town at a time |
| 8 | [The Compiler, and a Grammar for Languages](era-05-the-programmers-craft/08-the-compiler/README.md) | Type a formula and compile it two ways |
| 9 | [Rosenblatt's Perceptron](era-05-the-programmers-craft/09-perceptron/README.md) | Watch a line learn where to fall |
| 10 | [Hoare's Quicksort](era-05-the-programmers-craft/10-quicksort/README.md) | Watch the two fingers |
| 11 | [AVL Trees](era-05-the-programmers-craft/11-avl-trees/README.md) | Insert keys and watch the rotations |
| 12 | [Heapsort and the Heap](era-05-the-programmers-craft/12-heapsort/README.md) | Build a heap, then take it apart |
| 13 | [Edmonds's Matching](era-05-the-programmers-craft/13-matching/README.md) | Find the path that the simple search misses |

### Era 6 — Hard Problems and Public Keys (1965 to 1978)

- **[Era 6 front page](era-06-hard-problems-and-public-keys/README.md)**: the time line, a map of how the thirteen ideas combine, and the topics. [Interactive edition](era-06-hard-problems-and-public-keys/index.html) (download the folder and open `index.html` in a browser). [Plan](era-06-hard-problems-and-public-keys/plan.md).
- [Reference catalog](era-06-hard-problems-and-public-keys/reference-catalog.md): each development with checked lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [The Fast Fourier Transform](era-06-hard-problems-and-public-keys/01-fast-fourier-transform/README.md) | Hide two waves in noise and watch the FFT find them |
| 2 | [Mutual Exclusion and the Semaphore](era-06-hard-problems-and-public-keys/02-semaphores/README.md) | Be the scheduler and try to break each algorithm |
| 3 | [Objects, Classes and Subclasses](era-06-hard-problems-and-public-keys/03-objects/README.md) | Run a post office of letters and parcels |
| 4 | [A*: Search Guided by an Estimate](era-06-hard-problems-and-public-keys/04-a-star/README.md) | Draw walls and race three searches |
| 5 | [Fast Matrix Multiplication](era-06-hard-problems-and-public-keys/05-strassen/README.md) | Seven products instead of eight |
| 6 | [The Relational Model of Data](era-06-hard-problems-and-public-keys/06-relational-model/README.md) | Ask the same question of four kinds of storage |
| 7 | [B-Trees](era-06-hard-problems-and-public-keys/07-b-trees/README.md) | Insert and delete keys; watch pages split and merge |
| 8 | [NP-Completeness](era-06-hard-problems-and-public-keys/08-np-completeness/README.md) | Try to satisfy a random formula |
| 9 | [Depth-First Search](era-06-hard-problems-and-public-keys/09-depth-first-search/README.md) | Watch the lowpoints find the weak points |
| 10 | [Public-Key Cryptography](era-06-hard-problems-and-public-keys/10-public-key-cryptography/README.md) | Encrypt with the RSA paper's own key, then break it |
| 11 | [Fast String Searching](era-06-hard-problems-and-public-keys/11-string-search/README.md) | Step through three searches for one word |
| 12 | [Universal Compression](era-06-hard-problems-and-public-keys/12-lempel-ziv/README.md) | Copy from what was already sent |
| 13 | [Logical Clocks](era-06-hard-problems-and-public-keys/13-logical-clocks/README.md) | Before, after, or neither? |

### Era 7 — Randomness, Networks and Learning (1979 to 1995)

- **[Era 7 front page](era-07-randomness-networks-and-learning/README.md)**: the time line, a map of how the thirteen ideas combine, and the topics. [Interactive edition](era-07-randomness-networks-and-learning/index.html) (download the folder and open `index.html` in a browser). [Plan](era-07-randomness-networks-and-learning/plan.md).
- [Reference catalog](era-07-randomness-networks-and-learning/reference-catalog.md): each development with checked lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [Linear Programming in Polynomial Time](era-07-randomness-networks-and-learning/01-linear-programming/README.md) | Cut an ellipse in half until its centre lands in the target |
| 2 | [Merkle's Hash Trees](era-07-randomness-networks-and-learning/02-merkle-trees/README.md) | Edit a block and watch the hashes change up to the root |
| 3 | [The Byzantine Generals](era-07-randomness-networks-and-learning/03-byzantine-generals/README.md) | Play the traitor, then try every lie |
| 4 | [Simulated Annealing](era-07-randomness-networks-and-learning/04-simulated-annealing/README.md) | Cool a tour of 60 cities slowly |
| 5 | [Splay Trees and Amortized Analysis](era-07-randomness-networks-and-learning/05-splay-trees/README.md) | Click a key and splay it to the root |
| 6 | [Zero-Knowledge Proofs](era-07-randomness-networks-and-learning/06-zero-knowledge/README.md) | Be the verifier: open two sealed colours at a time |
| 7 | [Backpropagation](era-07-randomness-networks-and-learning/07-backpropagation/README.md) | Teach two hidden units exclusive-or |
| 8 | [The Barnes–Hut Tree Code](era-07-randomness-networks-and-learning/08-barnes-hut/README.md) | Change θ and see which cells a star feels as one mass |
| 9 | [Karp–Rabin Fingerprints](era-07-randomness-networks-and-learning/09-karp-rabin/README.md) | Fingerprints under every window, and false alarms |
| 10 | [TCP Congestion Control](era-07-randomness-networks-and-learning/10-tcp-congestion-control/README.md) | Two senders, one link: four rules for sharing it |
| 11 | [Shor's Factoring Algorithm](era-07-randomness-networks-and-learning/11-shor-factoring/README.md) | Measure a simulated register and find the factors |
| 12 | [The Burrows–Wheeler Transform](era-07-randomness-networks-and-learning/12-burrows-wheeler/README.md) | Sort the rotations, then undo and search them |
| 13 | [AdaBoost](era-07-randomness-networks-and-learning/13-adaboost/README.md) | Watch the weights move as stumps vote |

### Era 8 — The Web, the Genome and the Ledger (1995 to 2008)

- **[Era 8 front page](era-08-the-web-the-genome-and-the-ledger/README.md)**: the time line, a map of how the thirteen ideas combine, and the topics. [Interactive edition](era-08-the-web-the-genome-and-the-ledger/index.html) (download the folder and open `index.html` in a browser). [Plan](era-08-the-web-the-genome-and-the-ledger/plan.md).
- [Reference catalog](era-08-the-web-the-genome-and-the-ledger/reference-catalog.md): each development with checked lectures, articles and original sources, certainty labels and gaps.
- The topics, each with a GitHub edition, an interactive edition and a tested program:

| # | Topic | Interactive widget |
|---|---|---|
| 1 | [Support Vector Machines](era-08-the-web-the-genome-and-the-ledger/01-support-vector-machines/README.md) | Find the widest street |
| 2 | [Approximation by Semidefinite Programming](era-08-the-web-the-genome-and-the-ledger/02-max-cut/README.md) | Throw a plane through the arrows |
| 3 | [Streaming Sketches](era-08-the-web-the-genome-and-the-ledger/03-streaming-sketches/README.md) | Count words you cannot keep |
| 4 | [Consistent Hashing](era-08-the-web-the-genome-and-the-ledger/04-consistent-hashing/README.md) | Add a server, take one away |
| 5 | [MinHash and Locality-Sensitive Hashing](era-08-the-web-the-genome-and-the-ledger/05-minhash/README.md) | Two sentences, 32 minimum hashes |
| 6 | [Long Short-Term Memory](era-08-the-web-the-genome-and-the-ledger/06-lstm/README.md) | Carry one sign through thirty steps of noise |
| 7 | [PageRank](era-08-the-web-the-genome-and-the-ledger/07-pagerank/README.md) | Pass the rank along the links |
| 8 | [Paxos](era-08-the-web-the-genome-and-the-ledger/08-paxos/README.md) | One rule between agreement and chaos |
| 9 | [Genome Assembly with de Bruijn Graphs](era-08-the-web-the-genome-and-the-ledger/09-genome-assembly/README.md) | How long must the words be? |
| 10 | [PRIMES is in P](era-08-the-web-the-genome-and-the-ledger/10-primes-is-in-p/README.md) | Run AKS on a number |
| 11 | [MapReduce](era-08-the-web-the-genome-and-the-ledger/11-mapreduce/README.md) | Kill a machine, slow one down |
| 12 | [Compressed Sensing](era-08-the-web-the-genome-and-the-ledger/12-compressed-sensing/README.md) | Recover a signal from too few measurements |
| 13 | [Bitcoin's Proof-of-Work Ledger](era-08-the-web-the-genome-and-the-ledger/13-bitcoin/README.md) | Mine a block, then break it |

### Coming next (proposed eras; open to change)

| Era | Span | Topics (from the Evolutionary Atlas) |
|---|---|---|
| 9 | 2009–2026 | Deep learning at scale, attention and transformers, diffusion models, modern consensus and cryptography, and the algorithms of 2026 |

### Plans

- [Sample B — Finding a word](plans/sample-B-finding-a-word.md): deriving Rabin–Karp from the pain of plain string search (plan only).

### Companion volume: the principles catalog

- [The principles catalog](principles-catalog/README.md): 62 named principles with verified Java. Parts 1 and 2 are written; Part 3's programs are verified and its page is not written.
