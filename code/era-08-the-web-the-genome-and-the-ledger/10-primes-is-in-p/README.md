# PRIMES is in P: the program

*Era 8 · topic 10 · 2002* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/10-primes-is-in-p/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/10-primes-is-in-p/primes-is-in-p.html) · [All era 8 programs](../README.md)

## How it works

```text
For n > 1 and any a with gcd(a, n) = 1:  n is prime exactly when (X + a)^n = X^n + a as polynomials with every
coefficient taken modulo n. (The middle coefficients of (X + a)^n are the binomial numbers C(n, k) times powers of
a; all of them are divisible by n exactly when n is prime.) But (X + a)^n has n + 1 coefficients: checking them is
no faster than trying divisors. Agrawal, Kayal and Saxena check the identity only modulo X^r - 1 as well, so every
polynomial has fewer than r coefficients, for a small r and a few values of a, and prove that this is enough:
  1. If n = a^b with b > 1, n is composite.
  2. Find the smallest r for which the powers of n modulo r take more than (log2 n)^2 steps to return to 1.
  3. If some a <= r has 1 < gcd(a, n) < n, n is composite.
  4. If n <= r, n is prime.
  5. For a = 1 to floor(sqrt(phi(r)) log2 n): if (X + a)^n is not X^(n mod r) + a modulo (X^r - 1, n), composite.
  6. Otherwise n is prime.
r is at most about (log2 n)^5, so every step takes time polynomial in the number of digits of n. No coin is
tossed, and nothing unproved is assumed. (This is the version on Wikipedia; the August 2002 preprint chose r
differently.)
```

## What the program does

```text
1. The identity checked in full for every n up to 300.
2. AKS run on every n from 2 to 3,000 and compared with a sieve; which step decides each one.
3. Carmichael numbers and a strong pseudoprime, which fool Fermat's and Miller's quick tests, against AKS; and
   products of two primes larger than r, which only the polynomial check can catch.
4. The cost for primes near 1,000, 10,000 and 100,000, counted in coefficient multiplications, against Miller-Rabin.
5. Pascal's triangle modulo n and the AKS steps for a few numbers, for the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AksPrimality.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [AKS primality test](https://en.wikipedia.org/wiki/AKS_primality_test) — Wikipedia | The four properties, the algorithm and a worked example |
| Deeper | [It is easy to determine whether a given integer is prime](https://www.ams.org/bull/2005-42-01/S0273-0979-04-01037-7/) — A. Granville, *Bulletin of the AMS* (2005) | A mathematician's account of the proof and its background |
| Scholar | [PRIMES is in P (preprint, 6 August 2002)](https://www.cse.iitk.ac.in/users/nitin/papers/aug02.pdf) — M. Agrawal, N. Kayal, N. Saxena, IIT Kanpur | The version that was announced |
| Scholar | [PRIMES is in P](https://annals.math.princeton.edu/2004/160-2/p12) — *Annals of Mathematics* 160 (2004) | The published version |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
