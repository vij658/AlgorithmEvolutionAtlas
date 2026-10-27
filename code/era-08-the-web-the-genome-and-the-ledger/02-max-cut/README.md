# Approximation by Semidefinite Programming: the program

*Era 8 · topic 2 · 1994–1995* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/02-max-cut/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/02-max-cut/max-cut.html) · [All era 8 programs](../README.md)

## How it works

```text
MAX CUT: split the nodes of a network into two groups so that as many links as possible run between the groups.
It is NP-hard (Era 6), so a fast method can only promise to come close. Flipping a coin for each node cuts each
link with probability 1/2, so on average half of all links: at least half of the best.
Goemans and Williamson give each node i a unit arrow v_i in n dimensions instead of a side (+1 or -1) and maximize
sum over links of (1 - v_i . v_j) / 2. With arrows in one dimension this is exactly MAX CUT; with arrows in many it
is a semidefinite program, which can be solved to any accuracy in polynomial time, and its value is at least the
best cut. Then cut the arrows with a random plane through the origin: two arrows at angle theta fall on opposite
sides with probability theta / pi. Since theta / pi >= 0.87856 (1 - cos theta) / 2 for every angle, the expected
cut is at least 0.87856 times the program's value, and so at least 0.87856 times the best cut.
This program solves the semidefinite program with a simple low-rank method: repeatedly turn each arrow to point
exactly away from the weighted sum of its neighbours' arrows. Each turn can only improve the value. It then
proves the answer optimal with a certificate from the dual program: the matrix Diag(|g_i|) + A must have no
negative eigenvalue, where g_i is the sum of node i's neighbours' arrows and A is the adjacency matrix.
```

## What the program does

```text
1. The constant: the minimum of 2 theta / (pi (1 - cos theta)), and where it is reached.
2. The 5-cycle, where the program's value is (5/2)(1 + cos(pi/5)) and the best cut is 4.
3. 200 random networks of 16 nodes: the program's value, the best cut by trying all 32,768 splits, the expected
   random-plane cut, the coin flip and a simple local search.
4. A network of 400 nodes, too big to try every split: the program's value as a certificate of quality.
5. The Petersen graph, with the random planes of the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java GoemansWilliamson.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Williamson and Goemans receive 2022 Steele Prize](https://bowers.cornell.edu/news-stories/david-williamson-and-michel-goemans-receive-2022-steele-prize-seminal-contribution-research) — Cornell University (2022) | What the paper did and why it mattered |
| Deeper | [Goemans and Williamson (1995): Algorithm for MAXCUT](https://www.cs.toronto.edu/~deepkush/teaching/373s22/hwk/tutorial6-max-cut.pdf) — University of Toronto course notes | The relaxation and the rounding, step by step |
| Scholar | [Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming](https://math.mit.edu/~goemans/PAPERS/maxcut-jacm.pdf) — M. Goemans, D. Williamson, *J. ACM* (1995) | The algorithm, the constant and the proofs |
| Scholar | [SDP gaps and UGC-hardness for Max-Cut-Gain](https://zesty2.cs.uchicago.edu/articles/v005a004/v005a004.pdf) — S. Khot, R. O'Donnell, *Theory of Computing* (2009) | Why 0.878 may be the best possible |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
