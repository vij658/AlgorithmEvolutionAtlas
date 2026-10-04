# 2. Extended Euclidean algorithm

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#2-extended-euclidean-algorithm)

## How it works

Run Euclid's algorithm but also track how each remainder is built from a and b. That yields x and y with a·x + b·y = gcd(a, b) (Bézout). When gcd(a, m) = 1, x is the inverse of a modulo m, which is how RSA computes its private exponent.

## In depth (from the catalog page)

Finds integers x and y with `a·x + b·y = gcd(a, b)` (Bézout's identity). When the gcd is 1, x is the inverse of a modulo b, which is the building block of modular division.

```java
static long[] egcd(long a, long b) {         // returns {g, x, y} with a*x + b*y = g
    if (b == 0) return new long[]{a, 1, 0};
    long[] r = egcd(b, a % b);
    return new long[]{r[0], r[2], r[1] - (a / b) * r[2]};
}

static long modInverse(long a, long m) {
    long[] r = egcd(Math.floorMod(a, m), m);
    if (r[0] != 1) throw new ArithmeticException("no inverse: gcd = " + r[0]);
    return Math.floorMod(r[1], m);
}
```

> **Verified.** `egcd(240, 46)` gives g = 2 with 240x + 46y = 2. `modInverse(17, 3120)` is 2753, the private exponent of the textbook RSA example. `modInverse(6, 9)` throws because gcd(6, 9) = 3. On 1,000 random values modulo 1,000,000,007 it matched `BigInteger.modInverse`.

**Use it for** key generation in RSA and elliptic-curve systems, the Chinese Remainder Theorem, secret sharing and exact fraction arithmetic. For numbers beyond `long`, call `BigInteger.modInverse`.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/02-extended-euclidean-algorithm
java ExtendedEuclid.java
```

JDK 17 or newer, no build step. It prints 1,003 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
ExtendedEuclid: 1003 checks passed
```

## References

- **Lecture:** [MIT 6.042J Lec 4: number theory, GCD and the Pulverizer](https://www.youtube.com/watch?v=NuY7szYSXSw)
- **History and more links:** [Era 1 reference catalog](../../../../book/era-01-the-first-algorithms/reference-catalog.md#7-euclids-algorithm)
