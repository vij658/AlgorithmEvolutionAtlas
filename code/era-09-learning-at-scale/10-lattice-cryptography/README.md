# Lattice Cryptography and ML-KEM: the program

*Era 9 · topic 10 · 2017–2024* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/10-lattice-cryptography/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/10-lattice-cryptography/lattice-cryptography.html) · [All era 9 programs](../README.md)

## How it works

```text
Learning with errors: given a random matrix A and b = A s + e (mod q), where s is secret and e is a vector of
small random errors, find s. Without e, Gaussian elimination finds s at once; with e, no efficient method is
known, on ordinary or quantum computers. Kyber works with polynomials of degree below n = 256, coefficients
modulo q = 3329, and arithmetic modulo X^256 + 1; a "module" is a short vector (k = 2, 3 or 4) of them.
  Key generation: public t = A s + e, with s and e small; A comes from a public seed.
  Encryption of a 256-bit message m: pick small r, e1, e2; send u = A^T r + e1 and
    v = t^T r + e2 + (q/2 rounded) * m, each rounded to fewer bits (Compress with d_u and d_v bits).
  Decryption: v - s^T u = e^T r + e2 + (q/2) m - s^T e1 + rounding: a small noise plus m times q/2,
    so each coefficient near q/2 is a 1 and near 0 is a 0.
Polynomials are multiplied with the number-theoretic transform, the Fourier transform modulo q, using
zeta = 17, a primitive 256th root of unity modulo 3329.
This program implements the arithmetic of ML-KEM's inner encryption scheme (K-PKE) as FIPS 203 describes it,
with java.util.Random in place of the standard's SHA-3 and SHAKE hashing; it is a model for study, not a
conforming or secure implementation.
```

## What the program does

```text
1. Learning with and without errors: Gaussian elimination recovers s from exact equations and fails with errors.
2. The number-theoretic transform: 17 is a primitive 256th root of unity, and multiplication through the NTT
   equals schoolbook multiplication modulo X^256 + 1.
3. The three parameter sets: thousands of encryptions each, every message recovered, the largest noise against
   the margin q/4; key and ciphertext sizes from the formulas, against the published sizes.
4. Too much noise: larger errors or harsher rounding, and decryption starts to fail.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LatticeKem.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Learning with errors: Encrypting with unsolvable equations](https://www.youtube.com/watch?v=K026C5YaB3A) — Chalk Talk | Equations with errors, and why they hide a secret |
| Start | [ML-KEM](https://en.wikipedia.org/wiki/ML-KEM) — Wikipedia | From Regev to the standard |
| Deeper | [Learning With Errors (LWE) and Public Key Encryption \|\| @ CMU \|\| Lecture 25d of CS Theory Toolkit](https://www.youtube.com/watch?v=QcVns57MTxg) — Ryan O'Donnell | Regev's public-key scheme, in a Carnegie Mellon course |
| Deeper | [ML-KEM (Kyber) – Design and Implementation](https://bnaskrecki.faculty.wmi.amu.edu.pl/crypto/book/part14_lattice_crypto/ch41_ml_kem_kyber.html) — *Elements of Cryptanalysis*, chapter 41 | The parameter sets, worked through |
| Scholar | [FIPS 203: Module-Lattice-Based Key-Encapsulation Mechanism Standard](https://nvlpubs.nist.gov/nistpubs/fips/nist.fips.203.pdf) — NIST (13 August 2024) | The standard |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
