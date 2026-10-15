# Era 6 — Hard Problems and Public Keys (plan)

*1965 to 1978. Topic list in order of time, with the exceptions noted below. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the fifth era the species learned to write programs well. In this one their programs begin to run side by side, share memory, and talk to each other across networks; their data outgrow memory and move to disks; and their machines begin to keep secrets in public. Some old problems turn out to have much faster methods than anyone expected: transforms, matrix products, searches through text and graphs. Others, a whole family of them, resist every attempt, and the species proves that they all stand or fall together without learning which. By the end of the era they have turned that hardness into a resource: the security of their messages rests on problems they believe nobody can solve quickly.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | The fast Fourier transform | 1963 meeting; 1964 demonstration; 1965 paper | Princeton, IBM Research | A transform of N samples took about N² operations | Split into even and odd samples, recursively: (N/2) log₂ N butterflies | Gauss's method (Era 3, 9) |
| 2 | Mutual exclusion and the semaphore | Dekker about 1962; semaphore 1962; EWD 123, 1965 | Amsterdam, Eindhoven | Shared memory, interleaved steps: lost updates and deadlock | The critical section stated; Dekker's solution; P and V | The stored program (Era 4, 9) |
| 3 | Objects, classes and subclasses | 1961–1967 | Norwegian Computing Center, Oslo | Simulations of many interacting things were arrays and scattered code | Classes, objects created at run time, subclasses, virtual procedures | The subroutine (Era 5, 1) |
| 4 | A* | 1967–1968 | Stanford Research Institute | Dijkstra's method wastes work; greedy search returns long paths | f = g + h with an estimate that never overestimates | Dijkstra's shortest paths (Era 5, 7) |
| 5 | Fast matrix multiplication | 1969 | Zürich | n³ operations to multiply or invert | Seven products for 2 × 2 blocks, recursively: n^2.807 | Divide and conquer (1) |
| 6 | The relational model of data | 1970 | IBM San Jose | Programs depended on how data were stored | Relations and operations on whole tables; normal form | Boole's algebra of logic (Era 3, 12) |
| 7 | B-trees | 1969–1972 | Boeing Scientific Research Laboratories | Indexes on disk: one slow access per tree step | Pages of k to 2k keys; split and merge; all leaves at one depth | AVL trees (Era 5, 11) |
| 8 | NP-completeness | 1971–1973 | Toronto, Berkeley, Moscow | Many problems resisted fast methods, with no explanation | Polynomial reductions; satisfiability is NP-complete; Karp's 21 problems | Turing machines (Era 4, 7); Edmonds's "good" algorithms (Era 5, 13) |
| 9 | Depth-first search | 1970–1974 | Stanford, Cornell | Graph structure took repeated searches | Search order, fronds and lowpoints: linear-time components | Graph search (Era 5, 7) |
| 10 | Public-key cryptography | 1976–1977 (GCHQ in secret 1970–1974) | Stanford, MIT | Every cipher needed a key shared in advance | Key exchange in public; RSA encryption and signatures; probabilistic primality tests | Euclid's algorithm (Era 1, 7); frequency analysis and Enigma (Era 2, 7; Era 4, 8) |
| 11 | Fast string searching | 1969–1977 | Berkeley, Stanford, SRI, Xerox PARC | Searching reread the text; m × n comparisons at worst | KMP's "next" table; Boyer and Moore's right-to-left jumps | Regular expressions (Era 5, 2) |
| 12 | Universal compression | 1977–1978 | Technion, Haifa | Codes needed the source's probabilities | Pointers into what was already sent; a growing phrase dictionary | Shannon (Era 4, 12); Huffman (Era 5, 3) |
| 13 | Logical clocks | 1978 | Massachusetts Computer Associates | No meaning for "before" across separate computers | Happened-before; counters advanced by messages; a total order | Mutual exclusion (2) |

## Decisions after the reference catalog

- The era runs from 1965 (Cooley and Tukey's paper, and Dijkstra's "Cooperating sequential processes") to 1978 (Lamport's paper and LZ78), and the topics are ordered by the year each development first appeared in public.
- The semaphore (2) is placed at 1965, the date of EWD 123, though Dekker's algorithm and the semaphore itself go back to about 1962; the page says so.
- Objects (3) are placed by Simula 67 (1967), with Simula I and the work begun in 1961 on the same page.
- B-trees (7) come after the relational model (6) by publication, though Bayer dates the idea to autumn 1969; the catalog gives both dates.
- Depth-first search (9) is placed by Tarjan's 1972 paper; the planarity test (1974) shares the page as the problem that led to it.
- Public-key cryptography (10) covers Diffie and Hellman (1976), RSA (1977) and the probabilistic primality testing RSA needed; the earlier secret work at GCHQ is told on the same page and labelled with its sources.
- String searching (11) is placed at 1977, the year both papers appeared, with Morris's 1969 text editor as its origin.
- Several pages could not be opened: no video page, and publishers' pages that redirected. The catalog lists them as gaps instead of citing them.
- Every program prints only plain ASCII and uses fixed seeds, so the outputs are the same on every machine.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
