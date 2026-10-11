# Gödel's Numbering: the program

*Era 4 · topic 5 · 1931* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/05-godel-numbering/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/05-godel-numbering/godel-numbering.html) · [All era 4 programs](../README.md)

## How it works

```text
Gödel gave each basic sign of his formal system a number:
    "0" 1   "f" (the next number) 3   "~" (not) 5   "v" (or) 7   "P" (for all) 9   "(" 11   ")" 13
and each variable a prime above 13 (or a power of one, for variables of higher type). A formula, a string of signs
with numbers n1, n2, ..., nk, becomes the single number 2^n1 * 3^n2 * 5^n3 * ... * pk^nk. Because a number
factors into primes in only one way, the formula can be read back from its number. A proof, a list of formulas,
is coded the same way, with the formulas' numbers as the exponents. Then "x is the number of a proof of the
formula numbered y" is a statement about whole numbers that can be checked with loops of known length (Gödel's
"primitive recursive" functions), so arithmetic can talk about its own proofs. With a substitution trick
(the diagonal) he wrote a formula that says, in effect, "the formula with this number is not provable", where
the number is its own.
```

## What the program does

```text
1. Gödel's sign table, and the numbers of a few formulas, from "f0" (the number 1, coded as 24) upward.
2. Codes 10,000 random formulas and reads every one back by factoring; all numbers are different.
3. The size of a proof's number, which is too large to write down.
4. Reading an exponent back with loops of fixed length only (no open-ended search), checked against division
   for every number up to 200,000 and the first ten primes.
5. The diagonal trick with a modern numbering of English sentences: a sentence G that names, by a number, a
   recipe whose result is G itself.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java GodelNumbering.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Gödel's incompleteness theorems](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems) — Wikipedia | The two theorems, the Königsberg announcement, and the link to the halting problem |
| Start | [Gödel numbering](https://en.wikipedia.org/wiki/G%C3%B6del_numbering) — Wikipedia | The sign table and the prime-power code, with modern variants |
| Start | [Kurt Gödel](https://mathshistory.st-andrews.ac.uk/Biographies/Godel/) — MacTutor | Gödel's life and the reception of his results |
| Deeper | [On Formally Undecidable Propositions of Principia Mathematica and Related Systems](https://en.wikipedia.org/wiki/On_Formally_Undecidable_Propositions_of_Principia_Mathematica_and_Related_Systems) — Wikipedia | The paper itself: dates, structure, the 45 primitive recursive definitions, translations |
| Scholar | [Hilbert's Program Then and Now](https://arxiv.org/pdf/math/0508572) — Richard Zach, arXiv math/0508572 | What Hilbert wanted, what Gödel showed, and what survived |
| Scholar | [On Formally Undecidable Propositions of Principia Mathematica and Related Systems](https://gtts.ehu.es/German/Docencia/2021/MTBYC/pdf/Godel.pdf) — Gödel (1931), translated by B. Meltzer with an introduction by R. B. Braithwaite (1962), on a University of the Basque Country course page | The whole paper in English, with the original page numbers |
| Scholar | [On formally undecidable propositions … (sections 1 and 2)](https://www.hirzels.com/martin/papers/canon00-goedel.pdf) — Gödel (1931), translated by Martin Hirzel (27 November 2000) | A free modern translation of the sign table, the primitive recursive functions and the main argument |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
