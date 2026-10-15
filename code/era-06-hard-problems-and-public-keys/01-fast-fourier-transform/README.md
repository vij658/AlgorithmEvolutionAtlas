# The Fast Fourier Transform: the program

*Era 6 · topic 1 · 1964–1965* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/01-fast-fourier-transform/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/01-fast-fourier-transform/fast-fourier-transform.html) · [All era 6 programs](../README.md)

## How it works

```text
The discrete Fourier transform turns N samples x_0 ... x_(N-1) into N frequencies
    X_k = sum over n of x_n * w^(nk),   w = e^(-2 pi i / N),
about N^2 multiplications. If N is even, the sum splits into the even-numbered samples and the odd-numbered ones:
    X_k = E_k + w^k O_k,   X_(k + N/2) = E_k - w^k O_k,
where E and O are transforms of half the length. Each pair of outputs costs one multiplication (a "butterfly").
Repeating the split down to single samples gives log2 N stages of N/2 butterflies. Done in place, the samples
must first be put in "bit-reversed" order: sample n goes to the position whose binary digits are n's reversed.
Because multiplying two numbers is a convolution of their digits, and the transform turns a convolution into
pointwise products, the same trick multiplies very long numbers quickly.
```

## What the program does

```text
1. The bit-reversed order for 8 and 16 samples.
2. The FFT against the direct sum on random data of 1,024 samples: the largest difference.
3. Complex multiplications counted for N = 2^4 ... 2^20, direct against fast.
4. A "seismogram": two waves hidden in noise four times their size, found as the two tallest peaks.
5. Two 4,000-digit numbers multiplied through the FFT, against Java's BigInteger.
6. The inverse transform gives the samples back.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java FastFourier.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The 60-Year Old Algorithm Underlying Today's Tech](https://spectrum.ieee.org/fft-algorithm-ieee-milestone) — Kathy Pretz, IEEE Spectrum (2025) | The nuclear-test story and the IEEE Milestone |
| Start | [First Demonstration of the Fast Fourier Transform, 1964](https://ethw.org/Milestones:First_Demonstration_of_the_Fast_Fourier_Transform_(FFT) — Engineering and Technology History Wiki | The milestone citation and its history |
| Deeper | [James Cooley](https://en.wikipedia.org/wiki/James_Cooley) — Wikipedia | The IBM mathematician who wrote the program |
| Scholar | [An Algorithm for the Machine Calculation of Complex Fourier Series](https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf) — J. W. Cooley and J. W. Tukey, *Mathematics of Computation* 19: 297–301 (1965), on a UC Davis course page | The five-page paper |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
