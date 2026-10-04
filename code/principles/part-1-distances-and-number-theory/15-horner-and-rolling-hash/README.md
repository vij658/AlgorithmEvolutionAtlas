# 15. Horner's method and rolling hashes

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#15-horners-method-and-rolling-hashes)

## How it works

Horner's rule evaluates a polynomial with one multiply and one add per coefficient. Treating a string as a polynomial gives String.hashCode and the rolling hash: slide a window by subtracting the outgoing character's term and adding the new one, in O(1). A hash match only means 'check here', so Rabin–Karp verifies every match.

## In depth (from the catalog page)

Evaluate `a₀xⁿ + a₁xⁿ⁻¹ + … + aₙ` with n multiplications by nesting it: `((a₀x + a₁)x + a₂)x + …`. The same idea computes polynomial hashes, and because the hash of a sliding window can be updated in O(1), it powers substring search.

```java
static double horner(double[] coeffs, double x) {      // highest degree first
    double acc = 0;
    for (double c : coeffs) acc = acc * x + c;
    return acc;
}

// Rabin-Karp: expected O(n + m) substring search with a rolling hash
static int rabinKarp(String text, String pat) {
    int n = text.length(), m = pat.length();
    if (m == 0) return 0;
    if (m > n) return -1;
    final long MOD = 1_000_000_007L, B = 256;
    long hp = 0, ht = 0, pow = 1;                      // pow = B^(m-1) mod MOD
    for (int i = 0; i < m; i++) {
        hp = (hp * B + pat.charAt(i)) % MOD;
        ht = (ht * B + text.charAt(i)) % MOD;
        if (i > 0) pow = pow * B % MOD;
    }
    for (int i = 0; ; i++) {
        if (hp == ht && text.startsWith(pat, i)) return i;   // verify: equal hashes can still collide
        if (i + m >= n) return -1;
        ht = ((ht - text.charAt(i) * pow % MOD + MOD) * B + text.charAt(i + m)) % MOD;
    }
}
```

> **Verified.** `horner([2, 3, 4], 5)` is 69. Computing `h = 31*h + ch` over "hello" reproduces `"hello".hashCode()`, because Java's `String.hashCode` is a Horner evaluation with base 31. Rabin–Karp agreed with `String.indexOf` on 5,000 random cases.

<!-- -->

> **Pitfall.** Always confirm a match when the hashes agree, as the `startsWith` call does. Equal hashes do not guarantee equal strings.

Content-defined chunking in backup and file-sync tools uses the same rolling-fingerprint idea to find block boundaries that survive insertions.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/15-horner-and-rolling-hash
java HornerAndRollingHash.java
```

JDK 17 or newer, no build step. It prints 5,002 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
HornerAndRollingHash: 5002 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
