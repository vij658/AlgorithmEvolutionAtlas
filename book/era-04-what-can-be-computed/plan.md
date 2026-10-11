# Era 4 — What Can Be Computed (plan)

*1895 to 1950. Topic list in order of time, with two exceptions noted below. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the third era, procedures were put into tables and machines. In this one, mathematicians ask what a procedure is. Hilbert wants a process that settles every question; within forty years Gödel, Church and Turing have defined computation precisely and proved that some questions have no such process. In the same years the first electronic computers are built, programs are stored in their memories as numbers, and the new machines are set to work on chance, planning, secrecy and their own errors.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | Hilbert's questions | Paris 1900; Hilbert and Ackermann 1928; Matiyasevich 1970 | Paris, Göttingen | "A process ... by a finite number of operations" had no definition | Ask for it: the tenth problem and the Entscheidungsproblem; a search halts on every solvable equation | Pell's equation (Era 2, 5) |
| 2 | Runge–Kutta | Runge 1895; Heun 1900; Kutta 1901 | Germany | Euler's steps need to be tiny to be accurate | Sample the slope several times inside each step, with weights that cancel the error up to h⁴ | Euler's method; Newton's method (Era 3, 5) |
| 3 | Markov chains | Markov 1906; *Eugene Onegin* 1913 | St Petersburg | Probability theory assumed independent trials | The next state depends on the present one; averages still settle | The problem of points (Era 3, 4) |
| 4 | The cheapest network | Borůvka 1926; Jarník 1930 | Brno, Prague | Connecting towns with the least wire | Every group of towns takes its shortest outgoing line, round after round | Euler's bridges (Era 3, 7) |
| 5 | Gödel's numbering | Königsberg 1930; printed 1931 | Königsberg | Hilbert wanted every statement settled by a proof | Formulas and proofs coded as numbers; a formula that says it is unprovable | Hilbert (1) |
| 6 | Church's lambda calculus | 1932–1936 | Princeton | No definition of "effectively calculable" | Functions and substitution only; λ-definable = computable; an unsolvable problem | Hilbert (1), Gödel (5) |
| 7 | Turing's machines | 1936 (printed 1937) | Cambridge, Princeton | The decision problem needed a model of a person computing | Tape, head, finite table; the universal machine; no general halting test | Gödel (5), Church (6) |
| 8 | Breaking Enigma | Rejewski 1932; bomba 1938; Bombe 1940 | Warsaw, Bletchley Park | A cipher with too many settings to try | Cycle lengths the plugboard cannot change; machines that reject settings by contradiction | Frequency analysis (Era 2, 7) |
| 9 | The stored program, and merge sort | EDVAC report and merging program 1945; Baby 1948 | Philadelphia, Manchester | Machines rewired for every problem; sorting on card machines | Orders stored as numbers beside the data; merge sorted runs | Turing (7), Hollerith (Era 3, 13) |
| 10 | Monte Carlo | Ulam 1946; ENIAC 1948; Metropolis and Ulam 1949 | Los Alamos | Too many interacting chances to calculate | Simulate many random cases and count; machine-made random digits | Markov (3), the stored program (9) |
| 11 | The simplex method | Dantzig 1947 | The Pentagon | Plans with astronomically many options | Walk from corner to better corner of the feasible region | Elimination (Era 2, 1) |
| 12 | Shannon's bits | Thesis 1937; *Mathematical Theory of Communication* 1948 | MIT, Bell Labs | Circuits by trial and error; no measure of information | Boolean algebra for switches; entropy in bits; channel capacity | Boole (Era 3, 12), Markov (3) |
| 13 | Hamming's codes | 1947; published 1950 | Bell Labs | A detected error meant starting again | Check digits at positions 1, 2, 4, …; failed checks spell out the error's position | Binary (Era 3, 6), Shannon (12) |

## Decisions after the reference catalog

- The era runs from 1895, not 1900: Runge's paper of 1895 opens the Runge–Kutta family, and Kutta's classical method (1901) completes it. Hilbert's questions stay first because they set the era's theme; Runge–Kutta follows as topic 2.
- Shannon's topic (12) covers both the switching-circuit thesis (1937) and information theory (1948). It is placed by the 1948 paper, so that it sits next to Hamming's codes (13), which answer it.
- Turing's Bombe is part of topic 8 (Breaking Enigma), with the Polish work of 1932–1938; topic 7 is the 1936 paper only.
- Merge sort shares topic 9 with the stored program: von Neumann's first program for the EDVAC design was a merge.
- Several pages could not be opened (the Stanford Encyclopedia of Philosophy, some DOI links, the AMS archive): the catalog lists them as gaps instead of citing them.
- Every program prints only plain ASCII, so the outputs are the same on every machine.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
