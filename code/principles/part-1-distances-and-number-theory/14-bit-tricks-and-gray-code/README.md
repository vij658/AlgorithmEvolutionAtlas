# 14. Bit tricks and Gray code

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#14-bit-tricks-and-gray-code)

## How it works

Classic two's-complement tricks: x & (x − 1) clears the lowest set bit, x & −x isolates it, popcount counts bits, and the Gray code g = x ^ (x >>> 1) changes exactly one bit between consecutive numbers.

## In depth (from the catalog page)

```java
static boolean isPowerOfTwo(long n) { return n > 0 && (n & (n - 1)) == 0; }

static int popcountKernighan(long n) {
    int c = 0;
    while (n != 0) { n &= n - 1; c++; }                // each pass clears the lowest set bit
    return c;
}

long lowestSetBit = n & -n;                            // same as Long.lowestOneBit(n)

// Gray code: consecutive values differ in exactly one bit
static int gray(int n) { return n ^ (n >>> 1); }

static int grayInverse(int g) {
    int n = 0;
    for (; g != 0; g >>>= 1) n ^= g;
    return n;
}
```

> **Verified.** `isPowerOfTwo` is right for 0, 1, 6, 1024 and −8. Kernighan's loop matched `Long.bitCount` on 1,000 random longs, and `n & -n` isolated the lowest set bit. `gray(0)` to `gray(7)` is 0, 1, 3, 2, 6, 7, 5, 4. Across 2²⁰ consecutive values, neighbouring Gray codes differed in exactly one bit, the 10-bit sequence wraps around the same way, and `grayInverse(gray(i)) == i` for 100,000 values.

Gray codes avoid glitches when several bits would otherwise change at once (rotary encoders, asynchronous FIFO pointers), and they order the cells of a Karnaugh map. In production code prefer the JDK's intrinsics (`Long.bitCount`, `numberOfTrailingZeros`, `highestOneBit`); the loops above are for understanding.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/14-bit-tricks-and-gray-code
java BitTricks.java
```

JDK 17 or newer, no build step. It prints 1,149,586 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
BitTricks: 1149586 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
