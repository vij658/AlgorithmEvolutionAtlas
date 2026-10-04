# 1. Euclidean algorithm (GCD)

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#1-euclidean-algorithm-gcd)

## How it works

Replace the pair (a, b) by (b, a mod b) until the second number is 0; the first is then the greatest common divisor. The larger number at least halves every two steps, so the loop runs O(log min(a, b)) times; consecutive Fibonacci numbers are the worst case (Lamé). The binary GCD (Stein) gets the same answer with shifts and subtraction only.

## In depth (from the catalog page)

`gcd(a, b) = gcd(b, a mod b)`, repeated until the remainder is zero. It comes from Euclid's *Elements*, Book VII (about 300 BC), and takes O(log min(a, b)) division steps.

```java
static long gcd(long a, long b) {
    while (b != 0) { long t = a % b; a = b; b = t; }
    return Math.abs(a);
}

static long lcm(long a, long b) {
    if (a == 0 || b == 0) return 0;
    return Math.abs(a / gcd(a, b) * b);      // divide first to keep the intermediate small
}

// Stein's binary GCD (1967): shifts and subtraction only, no division
static long binaryGcd(long a, long b) {      // a, b >= 0
    if (a == 0) return b;
    if (b == 0) return a;
    int shift = Long.numberOfTrailingZeros(a | b);
    a >>= Long.numberOfTrailingZeros(a);
    while (b != 0) {
        b >>= Long.numberOfTrailingZeros(b);
        if (a > b) { long t = a; a = b; b = t; }
        b -= a;
    }
    return a << shift;
}
```

> **Verified.** `gcd(48, 18)` is 6, and zero, negative and coprime inputs behave. The worst case is two consecutive Fibonacci numbers: `gcd(F82, F81)` takes exactly 80 steps, in line with Lamé's theorem (1844), which caps the steps at 5 times the decimal digits of the smaller input. That cap held on 10,000 random pairs. `binaryGcd` agreed with `gcd` on 10,000 random pairs below 2^62.

**Use it for** reducing fractions, finding when periodic events line up (lcm), tiling problems and RSA arithmetic.

> **Pitfall.** `a * b / gcd(a, b)` can overflow before the division happens. Divide first, as `lcm` does above.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/01-euclidean-algorithm
java EuclideanAlgorithm.java
```

JDK 17 or newer, no build step. It prints 20,085 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
steps for gcd(F82, F81) = 80
EuclideanAlgorithm: 20085 checks passed
```

## References

- **Watch:** [Euclid's Algorithm — Numberphile](https://www.youtube.com/watch?v=6Y3jHHE_hbA)
- **Lecture:** [MIT 6.042J Lec 4: number theory, GCD and the Pulverizer](https://www.youtube.com/watch?v=NuY7szYSXSw)
- **Read:** [Euclid's Algorithm — Cut the Knot](https://www.cut-the-knot.org/blue/Euclid.shtml)
- **Original:** [Euclid's Elements, Book VII, Proposition 2 (D. E. Joyce)](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII2.html)
- **History and more links:** [Era 1 reference catalog](../../../../book/era-01-the-first-algorithms/reference-catalog.md#7-euclids-algorithm)
