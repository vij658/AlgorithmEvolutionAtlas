# 20. Integer hazards and the pigeonhole principle

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#20-integer-hazards-and-the-pigeonhole-principle)

## How it works

Fixed-width integers wrap around: Math.abs(Integer.MIN_VALUE) is negative, (lo + hi) / 2 can overflow, and % keeps the sign of the dividend. The pigeonhole principle sets hard limits: no lossless compressor can shrink every input, and any hash must collide.

## In depth (from the catalog page)

```java
Math.abs(Integer.MIN_VALUE)          // still negative: -2147483648
-7 % 3                               // -1, the remainder takes the dividend's sign
Math.floorMod(-7, 3)                 // 2, the mathematical modulus
Math.addExact(Integer.MAX_VALUE, 1)  // throws ArithmeticException instead of wrapping
int mid = (lo + hi) >>> 1;           // safe midpoint; (lo + hi) / 2 can overflow
```

> **Verified.** All five lines behave as commented. With lo = 1,500,000,000 and hi = 2,000,000,000, `(lo + hi) / 2` is negative, while `(lo + hi) >>> 1` gives 1,750,000,000. A bug of exactly this shape sat in the JDK's own binary search for about nine years before Joshua Bloch's 2006 write-up.

The pigeonhole principle: if you map more inputs than outputs, two inputs must share an output. There are 2¹⁰ = 1,024 distinct 10-bit inputs but only 2⁰ + 2¹ + … + 2⁹ = 1,023 bit strings that are shorter. So no lossless compressor can shrink every input, and any hash into fewer bits than its input must collide.

> **Verified.** The program computes 1,024 inputs against 1,023 shorter outputs.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/20-integer-hazards-and-pigeonhole
java IntegerHazards.java
```

JDK 17 or newer, no build step. It prints 5 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
IntegerHazards: 5 checks passed
```

## References

- Bloch, J., [Extra, Extra – Read All About It: Nearly All Binary Searches and Mergesorts are Broken](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/) (2006): the `(low + high) / 2` overflow.
