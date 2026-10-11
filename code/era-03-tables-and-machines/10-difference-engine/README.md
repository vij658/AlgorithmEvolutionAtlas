# Babbage's Difference Engine: the program

*Era 3 · topic 10 · 1822* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/10-difference-engine/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/10-difference-engine/difference-engine.html) · [All era 3 programs](../README.md)

## How it works

```text
Take any polynomial, list its values at x = 0, 1, 2, ..., and subtract neighbours: the first differences. Subtract
neighbours again: the second differences. For a polynomial of degree n the nth differences are constant. So the
table can be run backwards: keep one value and one difference of each order in a column of wheels, and each turn
of the handle adds every difference into the one above it. The value column then steps through the table using
additions only, which is exactly what wheels with a carry (topic 3) can do. Babbage's first model had two orders
of difference and made a table of x^2 + x + 41.
```

## What the program does

```text
1. Runs a two-difference engine on x^2 + x + 41, as Babbage's model did, checking every value.
2. Runs engines of higher order on random polynomials of degree up to 7, with exact whole numbers.
3. Counts the work: additions per entry against Horner's multiplications and additions.
4. Makes a 7-place table of common logarithms from 1,000 to 9,999 by a seventh-order engine, restarting from exact
   values every 50 entries, and compares every entry with the true rounded value.
5. Shows how differences expose an error in a printed table.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java DifferenceEngine.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [200 Years Ago Charles Babbage Proposed His Difference Engine](https://i-programmer.info/news/82-heritage/15481-difference-engine-reported-14-june-1822.html) — Mike James, I Programmer (14 June 2022) | The note of 1822, the model, x² + x + 41, Clement, and why Engine No. 1 stopped |
| Start | [A Modern Sequel](https://www.computerhistory.org/babbage/modernsequel/) — Computer History Museum | How the Science Museum built Difference Engine No. 2 and found that it works |
| Start | [Difference Engine No. 2](https://collection.sciencemuseumgroup.org.uk/objects/co62748) — Science Museum Group collection | The machine itself, with Doron Swade's role |
| Scholar | [Letter to Sir Humphry Davy (excerpt)](https://ed-thelen.org/bab/bab-letter.html) — Babbage, 1822, from *The Works of Charles Babbage* vol. 2 (ed. Campbell-Kelly), on Ed Thelen's site | Babbage on his working model: x² + x + 41 at forty-four figures a minute |
| Scholar | [The Calculating Engine (Edinburgh Review, 1834)](https://gutenberg.org/files/71292/71292-h/71292-h.htm) — Project Gutenberg eBook 71292 | A contemporary explanation of the method of differences and of errors in printed tables |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
