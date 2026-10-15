# Shor's Factoring Algorithm: the program

*Era 7 · topic 11 · 1994* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/11-shor-factoring/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/11-shor-factoring/shor-factoring.html) · [All era 7 programs](../README.md)

## How it works

```text
Factoring N reduces to finding a period. Pick a number a at random. The powers a, a^2, a^3, ... modulo N repeat
with some period r (the "order" of a). If r is even, then (a^(r/2) - 1)(a^(r/2) + 1) is a multiple of N, and
for at least half of the choices of a, a greatest common divisor (Euclid, Era 1) with N splits N. Finding r is the
hard part: no fast classical method is known. A quantum computer puts a register into a superposition of all x
from 0 to Q - 1 (Q at least N^2) at once, computes a^x mod N into a second register, and measures it: what is left
is a superposition of the x that share one value, spaced r apart. A quantum Fourier transform (the FFT, Era 6,
done by interference) turns that comb into peaks near multiples of Q / r; one measurement gives a number y near
one of them, and continued fractions recover r from y / Q. This program does every step with ordinary arithmetic,
storing all Q amplitudes, which is exactly why simulating it is hopeless for large N, and why a quantum computer
would not be.
```

## What the program does

```text
1. The classical reduction: for many N, the share of choices of a whose period splits N.
2. The quantum step for N = 15 and N = 21: where the measurement probabilities pile up.
3. The whole algorithm, simulated, for N up to 1,007: measurements needed until a factor appears.
4. The cost of simulating it: amplitudes needed against the number of digits of N.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ShorFactoring.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) — Wikipedia | The reduction, the quantum step, and the experiments so far |
| Deeper | [Pretending to factor large numbers on a quantum computer](https://ar5iv.labs.arxiv.org/html/1301.7007) — J. Smolin, G. Smith, A. Vargo (IBM, 2013) | Why "we factored N on a quantum computer" needs careful reading |
| Deeper | [How to factor 2048 bit RSA integers with less than a million noisy qubits](https://research.google/pubs/how-to-factor-2048-bit-rsa-integers-with-less-than-a-million-noisy-qubits/) — C. Gidney, Google (2025) | What breaking real RSA would take, as currently estimated |
| Scholar | [Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer](https://arxiv.org/abs/quant-ph/9508027) — P. Shor, arXiv (1995), *SIAM J. Computing* | The algorithm and its analysis |
| Scholar | [Algorithms for Quantum Computation: Discrete Log and Factoring](https://archive.dimacs.rutgers.edu/TechnicalReports/abstracts/1994/94-37.html) — P. Shor, DIMACS TR 94-37 (1994) | The 1994 announcement |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
