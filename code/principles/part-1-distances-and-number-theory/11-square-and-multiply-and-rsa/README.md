# 11. Square-and-multiply, Fermat's little theorem and RSA

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#11-square-and-multiply-fermats-little-theorem-and-rsa)

## How it works

Compute a^e mod m by reading e in binary: square for every bit, multiply in a when the bit is 1, so only about 2·log₂ e multiplications are needed. Fermat's little theorem gives a fast (fallible) primality test, and together with the extended Euclid inverse it is enough for textbook RSA.

## In depth (from the catalog page)

Computing `base^exp mod m` by repeated squaring takes O(log exp) multiplications instead of exp of them. Fermat's little theorem says that for a prime p and an a not divisible by p, `a^(p−1) ≡ 1 (mod p)`, so `a^(p−2)` is the inverse of a modulo p.

```java
static long modPow(long base, long exp, long mod) {   // needs mod <= ~3.03e9 so products fit in a long
    long result = 1 % mod;
    base %= mod;
    while (exp > 0) {
        if ((exp & 1) == 1) result = result * base % mod;
        base = base * base % mod;
        exp >>= 1;
    }
    return result;
}

// Fermat inverse for a prime modulus: a^(p-2) mod p
long inverse = modPow(a, MOD - 2, MOD);               // MOD = 1_000_000_007
```

> **Verified.** On 2,000 random (base, exponent, modulus) triples with moduli up to 3×10⁹, `modPow` matched `BigInteger.modPow`. On 1,000 random values, `a · modPow(a, p − 2, p) mod p` equalled 1 for p = 1,000,000,007. The textbook RSA example (p = 61, q = 53, n = 3233, e = 17, d = 2753) encrypts 65 to 2790 and decrypts it back to 65. And `modPow(2, 560, 561)` is 1 even though 561 = 3 × 11 × 17 is composite, so a base-2 Fermat test is fooled by this smallest Carmichael number.

<!-- -->

> **Pitfall.** The `long` version overflows once the modulus passes about 3.03×10⁹, because its square no longer fits in 63 bits. Beyond that use `BigInteger.modPow`. For primality testing don't use a plain Fermat test; use Miller–Rabin through `BigInteger.isProbablePrime`. Textbook RSA with tiny numbers is for illustration only, never for real systems.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/11-square-and-multiply-and-rsa
java SquareAndMultiply.java
```

JDK 17 or newer, no build step. It prints 3,002 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
SquareAndMultiply: 3002 checks passed
```

## References

- **Watch:** [Russian Multiplication — Numberphile](https://www.youtube.com/watch?v=HJ_PP5rqLg0)
- **Lecture:** [Four Algorithmic Journeys Part 1: Spoils of the Egyptians — Alexander Stepanov](https://www.youtube.com/playlist?list=PLHxtyCq_WDLV5N5zUCBCDC2WqF1VBDGg1)
- **Read:** [Fast multiplication / exponentiation — University of Alaska Fairbanks CS 463](https://www.cs.uaf.edu/2013/spring/cs463/lecture/02_13_multiplication.html)
- **History and more links:** [Era 1 reference catalog](../../../../book/era-01-the-first-algorithms/reference-catalog.md#5-egyptian-multiplication-by-doubling)
