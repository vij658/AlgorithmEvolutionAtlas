# Compressed Sensing: the program

*Era 8 · topic 12 · 2004–2006* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/12-compressed-sensing/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/12-compressed-sensing/compressed-sensing.html) · [All era 8 programs](../README.md)

## How it works

```text
A signal x has N numbers, but only k of them are not zero, and we do not know which. Take m measurements, each a
fixed random combination of all N numbers: y = A x, with A an m-by-N matrix of random numbers. With m < N the
equations A x = y have infinitely many solutions. The usual choice, the solution with the smallest sum of
squares, spreads the signal thinly over every position and is almost never right. Candès, Romberg and Tao
proved that the solution with the smallest sum of absolute values (the l1 norm) is, with high probability,
exactly x, as soon as m is a modest multiple of k log(N / k). Why l1: the set of points with a given l1 norm is
a diamond with corners on the axes, and a random flat set of solutions touches the smallest diamond at a corner,
where most numbers are zero.
Minimizing |x_1| + ... + |x_N| subject to A x = y is a linear program (Era 7): write x = u - v with u, v >= 0 and
minimize the sum of u and v. This program solves it with a primal-dual interior-point method (Mehrotra's
predictor-corrector, as in Era 7's program).
```

## What the program does

```text
1. One signal: N = 128, k = 5, m = 40 random measurements: the l1 solution against the smallest-squares one.
2. The phase transition: for m from 16 to 64 and k from 2 to 16, how often l1 minimization recovers the signal
   exactly (10 random signals and matrices each), and how often the smallest-squares solution does.
3. A small signal (N = 32, k = 3) recovered from 4 to 20 measurements, for the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java CompressedSensing.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Fill in the Blanks: Using Math to Turn Lo-Res Datasets Into Hi-Res Samples](https://maa.org/news/math-news/fill-in-the-blanks-using-math-to-turn-lo-res-datasets-into-hi-res-samples) — MAA Math News (2010), on J. Ellenberg's *Wired* article | How the discovery happened |
| Deeper | [Compressed sensing](https://en.wikipedia.org/wiki/Compressed_sensing) — Wikipedia | Sparsity, incoherence, ℓ1 and applications |
| Scholar | [Robust Uncertainty Principles](https://arxiv.org/pdf/math/0409186) — E. Candès, J. Romberg, T. Tao (2004; journal 2006) | The theorem and the 22-line phantom |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
