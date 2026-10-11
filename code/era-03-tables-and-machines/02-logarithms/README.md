# Logarithms: the program

*Era 3 · topic 2 · 1614–1624* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/02-logarithms/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/02-logarithms/logarithms.html) · [All era 3 programs](../README.md)

## How it works

```text
Give every number a partner, its logarithm, so that the partner of a product is the sum of the partners:
log(ab) = log a + log b. With a printed table, a long multiplication becomes two look-ups, one addition and one
look-up backwards; division becomes subtraction, and a square root becomes halving. Briggs chose base 10, so that
log 10 = 1 and log 1 = 0. To compute the table he took the square root of 10 again and again (54 times), reaching a
number 1 + d extremely close to 1, whose logarithm is exactly 1/2^54. Very close to 1, the logarithm is
proportional to the excess over 1, so a number x near 1 has logarithm (x - 1)/d times 1/2^54. To find log 2, take
square roots of 2 until it is near 1, use the proportion, and multiply back by the number of halvings. Only the
primes need this work: log 6 = log 2 + log 3.
```

## What the program does

```text
1. Multiplies by adding, with tables of 4, 7 and 14 decimals, and measures the error the table's rounding causes.
2. Runs Briggs's 54 square roots of 10 to 40 digits and finds log 2, log 3 and log 7 by his proportion,
   measuring how many decimals are right for 10 to 60 roots.
3. Counts the work in a table like Briggs's 1624 table: how many entries need a computation of their own (primes).
4. Counts digit operations: long multiplication against the look-up and addition.
5. Full circle: a product of many small probabilities in 64-bit floating point, directly and by adding logarithms.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Logarithms.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Four Centuries of Logarithms](https://www.gresham.ac.uk/sites/default/files/27jan97ianstewart_fourcenturiesoflogorithms.pdf) — Ian Stewart, Gresham Professor of Geometry, 27 January 1997 (transcript) | From Napier's twenty years of work and Briggs's base 10 to the slide rule |
| Start | [John Napier](https://mathshistory.st-andrews.ac.uk/Biographies/Napier/) — MacTutor | The 1614 book, the bones, and the agreement with Briggs |
| Start | [Henry Briggs](https://mathshistory.st-andrews.ac.uk/Biographies/Briggs/) — MacTutor | Gresham College, the 1615 visit and the 1624 tables |
| Deeper | [Arithmetica logarithmica (1624): a reconstruction](https://locomat.loria.fr/briggs1624/briggs1624doc.pdf) — Denis Roegel, LOCOMAT project (2011, revised 2014) | How Briggs computed: 54 square roots of 10, proportions near 1, finite differences, and what Vlacq did with the table |
| Scholar | [Napier's Descriptio and Constructio, translated](https://www.17centurymaths.com/contents/napiercontents.html) — Ian Bruce, 17centurymaths.com | Napier's own description (1614) and construction (1619) of his logarithms, in English with the Latin |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
