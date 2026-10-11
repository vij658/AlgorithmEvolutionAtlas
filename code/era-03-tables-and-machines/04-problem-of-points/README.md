# The Problem of Points: the program

*Era 3 · topic 4 · 1654* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/04-problem-of-points/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/04-problem-of-points/problem-of-points.html) · [All era 3 programs](../README.md)

## How it works

```text
Two players stake equal sums on a game of rounds, each round a fair toss; the first to win a set number of rounds
takes everything. The game is stopped early. How should the stakes be split? Fermat's way: count. If A still needs a
rounds and B needs b, the game would certainly be decided within a + b - 1 more rounds; list all 2^(a+b-1) equally
likely ways those rounds could fall, and split the stakes in proportion to the number each player would win.
Pascal's way: work backward. If A needs 0 rounds, A gets everything; if B needs 0, A gets nothing. Otherwise one more
round leaves A needing a - 1 or B needing b - 1, each with chance 1/2, so A's fair share is the average of the two
shares one step later. Filling in a table from the finished games backward gives every answer, without listing
the 2^(a+b-1) outcomes.
```

## What the program does

```text
1. Pascal's example from his letter of 29 July 1654: 64 pistoles split 48 to 16 and 56 to 8.
2. Fermat's enumeration and Pascal's table agree, in exact fractions, for every position up to 12 rounds each.
3. Fermat's three-player count from his letter of 25 September 1654: 17 combinations against 5 and 5.
4. The proportional rule (Pacioli, 1494) against the fair shares.
5. Pascal's triangle gives each share in closed form.
6. Work: table cells against enumerated outcomes, and a Monte Carlo estimate against the exact table.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ProblemOfPoints.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Lottery-Winning Maths](https://www.gresham.ac.uk/node/15381) — Gresham College, Sarah Hart, 31 January 2023 (video and transcript) | How a nobleman's dispute led Pascal and Fermat to the problem of points, and the triangle "known as Pascal's triangle now" |
| Start | [Problem of points](https://en.wikipedia.org/wiki/Problem_of_points) — Wikipedia | Pacioli, Tartaglia, de Méré, the two methods, the triangle and Huygens |
| Start | [Blaise Pascal](https://mathshistory.st-andrews.ac.uk/Biographies/Pascal/) — MacTutor | The 1654 letters, the arithmetical triangle, and the calculating machine |
| Scholar | [Fermat and Pascal on Probability](https://www.uu.nl/sites/default/files/correspondentie_fermat_en_pascal.pdf) — The 1654 letters, trans. Vera Sanford (Smith, *A Source Book in Mathematics*) and Maxine Merrington (David, *Games, Gods and Gambling*), on a Utrecht University page | Pascal's 64 pistoles divided 48 to 16 and 56 to 8; Fermat's "combinations" |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
