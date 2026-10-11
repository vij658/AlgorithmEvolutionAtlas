# Gauss's Fast Fourier Transform: the program

*Era 3 · topic 9 · 1805* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/09-gauss-fft/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/09-gauss-fft/gauss-fft.html) · [All era 3 programs](../README.md)

## How it works

```text
A periodic quantity measured at N equally spaced points (Gauss: positions of an asteroid around its orbit) can be
written as a sum of sines and cosines. Finding their coefficients directly, each from all N observations, takes
N x N products (the discrete Fourier transform). Gauss noticed that if N = N1 x N2, the observations fall into N2
interleaved groups of N1 (for N = 12: three groups of four, n = 3 n1 + n2). Fit each small group first, adjust
("twiddle") the results by a turn of angle, then combine the groups with N1 small fits of size N2. The work drops
from N^2 to about N (N1 + N2) products; splitting again and again, for N a power of 2, it drops to about
(N/2) log2 N.
```

## What the program does

```text
1. Fits 12 periodic observations directly and by Gauss's 4 x 3 and 3 x 4 splits, and counts the products.
2. Checks that the fitted sum of sines and cosines passes through all 12 observations.
3. Checks the fast transform against the direct one on random data for many sizes, and inverts it.
4. Counts the products, direct against fast, for N from 8 to 1,048,576.
5. Full circle: multiplies two 2,000-digit numbers by a fast transform of their digits.
The 12 observations are the program's own test data: the sources opened for this book do not print Gauss's.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java GaussFFT.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Deeper | [Historical Notes on the Fast Fourier Transform](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-2.pdf) — James W. Cooley, Peter A. W. Lewis and Peter D. Welch (1967), on a University of Washington course page | What was known before 1965, written two years after it |
| Scholar | [Gauss and the History of the Fast Fourier Transform](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-3.pdf) — Michael T. Heideman, Don H. Johnson and C. Sidney Burrus, *Archive for History of Exact Sciences* (1985) | The discovery that Gauss had the FFT in 1805, with his Pallas and Juno examples |
| Scholar | [An Algorithm for the Machine Calculation of Complex Fourier Series](https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf) — James W. Cooley and John W. Tukey, *Mathematics of Computation* 19:297–301 (1965), on a UC Davis course page | The paper that made the FFT standard |
| Scholar | [On the Origin and Publication of the FFT Paper](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-1.pdf) — Cooley and Tukey, *Current Contents* "Citation Classic" (1993) | The authors' own account of how the 1965 paper came about |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
