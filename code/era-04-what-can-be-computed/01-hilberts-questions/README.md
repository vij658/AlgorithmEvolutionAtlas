# Hilbert's Questions: the program

*Era 4 · topic 1 · 1900–1928* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/01-hilberts-questions/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/01-hilberts-questions/hilberts-questions.html) · [All era 4 programs](../README.md)

## How it works

```text
Hilbert's tenth problem (Paris, 1900) asks for "a process according to which it can be determined by a finite
number of operations" whether an equation with whole-number coefficients, such as x^3 + y^3 + z^3 = 30, has a
solution in whole numbers. Half of such a process is easy: try every tuple of integers, shell by shell (first all
tuples whose largest entry is 0, then 1, then 2, ...). If a solution exists, the search reaches it after finitely
many tries and stops. If none exists, the search never stops, and watching it tells you nothing. Sometimes a proof
settles the "no" side instead: x^2 + y^2 is never 3 more than a multiple of 4, so x^2 + y^2 = 1103 has no solution,
because 1103 = 4 x 275 + 3. Hilbert hoped some finite process would always decide. In 1970 Matiyasevich, building
on Davis, Putnam and Robinson, proved that none exists. For one unknown there is one: an integer root of a
polynomial must divide its constant term, so only finitely many candidates need testing.
```

## What the program does

```text
1. The shell-by-shell search reaches every tuple exactly once (checked for three unknowns, shells 0 to 25).
2. Search: x^2 + y^2 = 1105 and x^3 + y^3 + z^3 = 29 stop with a solution.
3. Proof by remainders: x^2 + y^2 = 1103 is impossible modulo 4, x^3 + y^3 + z^3 = 4 modulo 9; the search agrees
   as far as it goes (millions of tuples, none a solution).
4. x^3 + y^3 + z^3 = 30, 33 and 42: no remainder rules them out, a search through shell 200 finds nothing, and the
   solutions found by computer in 1999 and 2019 are checked exactly, with the number of tuples a blind search
   would have tried before reaching them.
5. One unknown: the divisor test decides 3,000 random polynomials, and a full search agrees every time.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java HilbertsQuestions.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [David Hilbert](https://mathshistory.st-andrews.ac.uk/Biographies/Hilbert/) — MacTutor | The Paris problems, the Königsberg speech, and what Gödel did to the programme |
| Start | [Entscheidungsproblem](https://en.wikipedia.org/wiki/Entscheidungsproblem) — Wikipedia | The decision problem of 1928 and its negative answer in 1936 |
| Start | [Hilbert's tenth problem](https://en.wikipedia.org/wiki/Hilbert%27s_tenth_problem) — Wikipedia | Why searching for solutions works only one way |
| Start | [Sums of three cubes](https://en.wikipedia.org/wiki/Sums_of_three_cubes) — Wikipedia | A search that halts only if an answer exists, run for decades |
| Deeper | [Computation Theory (lecture slides)](https://www.cl.cam.ac.uk/teaching/2324/CompTheory/slides.pdf) — Anuj Dawar (after Andrew Pitts), University of Cambridge, 2024 | The Entscheidungsproblem as the starting point of computation theory: register machines, Turing machines, the lambda calculus and the halting problem |
| Deeper | [Yuri Matiyasevich](https://mathshistory.st-andrews.ac.uk/Biographies/Matiyasevich/) — MacTutor | The final step of 1970, in Matiyasevich's own words |
| Scholar | [Mathematical Problems (1900)](https://gutenberg.org/files/71655/71655-h/71655-h.htm) — David Hilbert, trans. Mary Winston Newson (1902), Project Gutenberg | The address itself, with problem 10 and "no ignorabimus" |
| Scholar | [Mathematical problems (reprint)](https://www.ams.org/bull/2000-37-04/S0273-0979-00-00881-8/) — *Bulletin of the AMS* 37:407–436 (2000), reprinting Bull. AMS 8 (1902) | The same translation in the journal of record |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
