# 5. Hamming distance

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#5-hamming-distance)

## How it works

Count the positions where two equal-length strings or bit patterns differ; for bits that is Long.bitCount(a ^ b). Two unrelated random codes disagree in about half their bits, which is why a fractional distance well below 0.5 means 'same source'.

## In depth (from the catalog page)

The number of positions at which two equal-length sequences differ. For bit strings it is XOR followed by a population count.

```java
static int hamming(long a, long b) { return Long.bitCount(a ^ b); }

static int hamming(String s, String t) {
    if (s.length() != t.length()) throw new IllegalArgumentException("lengths differ");
    int d = 0;
    for (int i = 0; i < s.length(); i++) if (s.charAt(i) != t.charAt(i)) d++;
    return d;
}

static int hamming(long[] a, long[] b) {         // long bit strings packed 64 bits per long
    int d = 0;
    for (int i = 0; i < a.length; i++) d += Long.bitCount(a[i] ^ b[i]);
    return d;
}
```

> **Verified.** `hamming("karolin", "kathrin")` is 3, and `0b1011101` versus `0b1001001` differ in 2 bits. For 200 pairs of random, unrelated 2,048-bit codes, the fraction of differing bits averaged 0.5006, with every pair between 0.4 and 0.6. Independent bits disagree half the time.

That 0.5 baseline is why binary biometric templates work. Daugman's iris-code paper reports a mean fractional distance of 0.499 (standard deviation 0.0317) over 9.1 million comparisons of different eyes, and notes that a decision criterion just under 0.33 perfectly separated same-eye from different-eye comparisons on the data sets it shows. Hamming distance also underlies error-correcting codes (Hamming, 1950), perceptual image hashes, SimHash near-duplicate detection and DNA mismatch counts. HotSpot compiles `Long.bitCount` to a hardware popcount instruction where the CPU has one.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/05-hamming-distance
java HammingDistance.java
```

JDK 17 or newer, no build step. It prints 403 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
mean fractional Hamming distance of random 2048-bit codes = 0.5006
HammingDistance: 403 checks passed
```

## References

- Daugman, J., [How Iris Recognition Works](https://www.cl.cam.ac.uk/~jgd1000/irisrecog.pdf): impostor mean Hamming distance 0.499 (σ = 0.0317) over 9.1 million pairs, and the 0.32–0.33 decision criterion.
