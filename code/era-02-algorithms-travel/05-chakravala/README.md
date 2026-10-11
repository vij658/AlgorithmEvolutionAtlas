# The Chakravala and Pell's Equation: the program

*Era 2 · topic 5 · 628–1150 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/05-chakravala/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/05-chakravala/chakravala.html) · [All era 2 programs](../README.md)

## How it works

```text
Find whole numbers with a^2 - N b^2 = 1. (The Indian texts write N x^2 + 1 = y^2.) Guessing fails because the
smallest answer can be enormous: for N = 61, b = 226,153,980.
Composition (Brahmagupta's bhavana): if a^2 - N b^2 = k and c^2 - N d^2 = l, then
  (ac + Nbd)^2 - N (ad + bc)^2 = kl,
so two near-misses multiply into a new one. Composing a near-miss with itself and dividing by k makes an exact
answer, in fractions, and when k is 1, 2 or 4 (either sign) a few more compositions make it whole.
The chakravala ("cyclic") method makes this work for every N: from a triple (a, b, k), choose m so that k divides
a + b m and m^2 - N is as small as possible; compose with (m, 1, m^2 - N) and divide by k:
  a' = (a m + N b) / |k|,   b' = (a + b m) / |k|,   k' = (m^2 - N) / k.
Repeat until k = 1. The cycle always ends, though the proof came in Europe, with Lagrange's theory (1766-1767).
```

## What the program does

```text
1. Checks Brahmagupta's composition identity on random triples.
2. Solves Brahmagupta's N = 92 in two compositions.
3. Runs the chakravala step by step for Bhaskara II's N = 61 and N = 67, and the short route for 61: one step to
   k = -4, then Brahmagupta's finish.
4. For every N up to 1000 that is not a square, compares the chakravala with Lagrange's continued fractions (steps
   to the smallest answer) and checks that both find the same answer.
5. Measures how big the smallest answers get, and how long a plain search would take.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Chakravala.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Pell's Equation and Continued Fractions](https://mathcircle.berkeley.edu/sites/default/files/archivedocs/2008_2009/lectures/0809lecturespdf/PellBMC.pdf) — Tom Rike, Berkeley Math Circle, 28 April 2009 | High-school handout with exercises, covering Brahmagupta, Bhaskara and Fermat's N = 61 challenge |
| Start | [Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell) — MacTutor | The whole story: Brahmagupta (628), Bhaskara II (1150), Fermat, Brouncker, Euler's misnaming, Lagrange |
| Start | [Indian Mathematics – Redressing the balance, ch. 14](https://mathshistory.st-andrews.ac.uk/Projects/Pearce/chapter-14) — MacTutor (Pearce project) | A worked chakravala example, and the comparison with Lagrange |
| Start | [Chakravala method](https://en.wikipedia.org/wiki/Chakravala_method) — Wikipedia | The step rule, written as an algorithm, with the N = 61 example |
| Deeper | [Mathematics in India – From Vedic Period to Modern Times](https://nptel.ac.in/courses/111101080) — NPTEL, IIT Bombay (K. Ramasubramanian, M. D. Srinivas, M. S. Sriram) | Video course. The syllabus PDF lists lectures 11–13 on the *Brahmasphutasiddhanta* and 23–24 on the *Bijaganita* of Bhaskara II |
| Deeper | [Indian Mathematics](https://www.ms.uky.edu/~sohum/ma330/files/varadarajan.pdf) — V. S. Varadarajan, notes of two lectures at UCLA, March 2008 (copy on a University of Kentucky course site) | From Brahmagupta to Bhaskara's chakravala, and how Lagrange's theory of continued fractions shows it works |
| Deeper | [The bhāvanā in Mathematics](https://bhavana.org.in/the-bhavana-in-mathematics/) — Amartya Kumar Dutta (ISI Kolkata), *Bhāvanā* 1(1), January 2017 | Composition, Jayadeva and the chakravala, with worked boxes for N = 92 and N = 61 |
| Deeper | [Bhaskara II](https://mathshistory.st-andrews.ac.uk/Biographies/Bhaskara_II/) — MacTutor | Life (1114–1185) at Ujjain. Lists his examples (N = 8, 11, 32, 61, 67), but does not describe the cyclic method |
| Scholar | [On the Brahmagupta–Fermat–Pell equation x² − dy² = ±1](https://webusers.imj-prg.fr/%7Emichel.waldschmidt/articles/pdf/BrahmaguptaFermatPellEnVI.pdf) — Michel Waldschmidt (Sorbonne Université), slides, ICMMSIS'20 web conference, 23 July 2020 | A number theorist's tour from Brahmagupta's N = 92 and Bhaskara's N = 61 through Fermat to Lagrange |
| Scholar | [Rationale of the chakravala process of Jayadeva and Bhaskara II](https://www.ms.uky.edu/~sohum/ma330/files/Rationale-of-the-chakrav-la-process-of-Jayadeva-and-Bh-skara-II_1975_Historia-Mathematica.pdf) — Clas-Olof Selenius, *Historia Mathematica* 2 (1975), 167–184 | The method is a minimal-length semiregular continued-fraction algorithm, distinct from Lagrange's |
| Scholar | [Algebra, with Arithmetic and Mensuration, from the Sanscrit of Brahmegupta and Bháscara](https://archive.org/details/algebrawitharith00brahuoft/page/n5/mode/2up) — H. T. Colebrooke (trans.), London: J. Murray, 1817. Internet Archive (University of Toronto copy) | Colebrooke's English translation of Brahmagupta's and Bhaskara's algebra |
| Scholar | [Polynomial-time quantum algorithms for Pell's equation and the principal ideal problem](https://pure.psu.edu/en/publications/polynomial-time-quantum-algorithms-for-pells-equation-and-the-pri-2/) — Sean Hallgren, *Journal of the ACM* 54(1), 2007 (Penn State record) | "Factoring integers reduces to finding integer solutions of Pell's equation"; a quantum algorithm solves it in polynomial time and breaks the Buchmann–Williams key exchange |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
