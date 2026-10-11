# Fibonacci's Liber Abaci: the program

*Era 2 · topic 8 · 1202 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/08-liber-abaci/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/08-liber-abaci/liber-abaci.html) · [All era 2 programs](../README.md)

## How it works

```text
"These are the nine figures of the Indians: 9 8 7 6 5 4 3 2 1." With them and a zero, any number is written in a
few figures, and every operation becomes a written procedure whose working stays on the page for anyone to check.
The book teaches the four operations and fractions (chapters 2-7), then merchants' problems: prices, barter,
partnerships and money changing (8-11), many posed problems including the rabbits (12), and double false position,
the method "elchataym" (13): try two guesses, see how far each misses, and combine them to hit the answer.
The rabbits: a newborn pair can breed at one month old, gives birth a month later, and so on; each month's count is
the sum of the two before it, F(n) = F(n-1) + F(n-2).
```

## What the program does

```text
1. Compares the length of Roman and Hindu-Arabic numerals from 1 to 3999, and writes out a merchant's
   multiplication with its partial products, the working that Roman numerals do not leave.
2. Breeds the rabbits month by month as individual pairs, and checks the count against the recurrence.
3. Computes Fibonacci numbers four ways: plain recursion (counting the calls), a loop, fast doubling, and Binet's
   formula in floating point (finding where it first goes wrong).
4. Shows that consecutive Fibonacci numbers are the worst case of Euclid's algorithm (Lame, 1844).
5. Solves linear problems by double false position, and shows it is only approximate for curved ones.
6. Full circle: the Fibonacci lemma behind Fibonacci heaps (Fredman and Tarjan, 1987).
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LiberAbaci.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Who invented algebra?](https://www.gresham.ac.uk/node/11558) — Gresham College, Robin Wilson, 5 October 2005 (video and transcript) | Islamic mathematics and its route into Europe, including through Fibonacci. Context more than detail |
| Start | [Fibonacci's Rabbits](https://mathcenter.oxford.emory.edu/site/math125/fibonacciRabbits) — Math 125 notes, Oxford College of Emory University math center site | Turns the rabbit puzzle from *Liber Abaci* (1202) into the recurrence |
| Start | [Leonardo of Pisa, also known as Fibonacci (1170–1250)](https://mathshistory.st-andrews.ac.uk/Strick/Fibonacci.pdf) — Heinz Klaus Strick, trans. David Kramer, MacTutor | Short illustrated life and a tour of the book, rabbits included |
| Start | [Fibonacci's real mathematical legacy](https://blogs.nature.com/aviewfromthebridge/2017/04/20/fibonaccis-mathematical-legacy/) — Davide Castelvecchi, *Nature* blog | Argues that the numerals, not the sequence, were the legacy, and reports the Devlin–Franci dispute |
| Deeper | [Supplement: Leonardo of Pisa (Fibonacci) and the Liber abbaci](https://faculty.etsu.edu/gardnerr/3040/Notes-Eves6/Leonardo-Fibonacci-Liber-abbaci.pdf) — MATH 3040 course notes, East Tennessee State University faculty site, based on Devlin's *The Man of Numbers* (2011) | Chapter-by-chapter contents of the book, editions, and the *Livero de l'abbecho* |
| Deeper | [Fibonacci](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/) — MacTutor | Life, the 1202 and 1228 editions, the 1240 decree, and the other works (1220, 1225) |
| Deeper | [Fibonacci's Liber Abaci](https://old.maa.org/node/116274) — Frank J. Swetz, MAA *Convergence* (July 2007) | Review of Sigler's translation, with the book's Arabic sources (al-Khwarizmi, Abu Kamil, al-Karaji) |
| Deeper | [Fibonacci Heaps](https://www.cs.princeton.edu/~wayne/kleinberg-tardos/pdf/FibonacciHeaps.pdf) — Kevin Wayne, lecture slides for Kleinberg and Tardos, *Algorithm Design* (updated 2017) | The lemma: a heap of rank k has at least F(k+2) elements, so rank ≤ log base φ of n |
| Deeper | [Euclidean Algorithm](https://mathworld.wolfram.com/EuclideanAlgorithm.html) — Wolfram MathWorld | Lamé's bound and the Fibonacci worst case |
| Scholar | [Review of Sigler, *Fibonacci's Liber Abaci*](https://ircps.org/wp-content/uploads/2021/04/2004-02-01_Cuomo.pdf) — Serafina Cuomo, *Aestimatio* 1 (2004), 19–27 | The manuscript tradition (12 copies, 3 complete), and why the surviving text is the 1228 edition |
| Scholar | [Il Liber abbaci di Leonardo Pisano](https://archive.org/details/bub_gb_w86fLKi88pYC/page/n7/mode/2up) — Baldassarre Boncompagni (ed.), *Scritti di Leonardo Pisano*, 1857. Internet Archive (Google Books scan of the Florence National Central Library copy) | The Latin text, edited from a single manuscript |
| Scholar | [Fibonacci's Liber Abaci: A Translation into Modern English of Leonardo Pisano's Book of Calculation](https://link.springer.com/book/9780387407371) — Laurence Sigler, Springer, 2002 (Sources and Studies in the History of Mathematics and Physical Sciences) | The only complete translation into a modern language |
| Scholar | [Mathematical Treasures: Fibonacci's Liber abaci](https://old.maa.org/node/1734149) — MAA *Convergence* | Images from a 14th-century copy in the Biblioteca Nazionale Centrale di Firenze, including the page of nine Indian figures, and a translation of the autobiographical preface |
| Scholar | [Fibonacci heaps and their uses in improved network optimization algorithms](https://collaborate.princeton.edu/en/publications/fibonacci-heaps-and-their-uses-in-improved-network-optimization-a-2/) — Michael L. Fredman and Robert E. Tarjan, Journal of the ACM 34(3), 1987, 596–615 | Constant amortized time for most heap operations; shortest paths in O(n log n + m) |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
