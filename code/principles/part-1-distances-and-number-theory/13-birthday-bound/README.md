# 13. The birthday bound (collisions in hashes and IDs)

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#13-the-birthday-bound-collisions-in-hashes-and-ids)

## How it works

With N equally likely values, the chance that k random picks are all different falls like e^(−k²/2N), so collisions become likely after about √N picks (1.18·√N for 50%). This sizes hash lengths and random IDs.

## In depth (from the catalog page)

With N equally likely values, a collision becomes about as likely as not after roughly 1.1774·√N draws, far fewer than N. For a small target probability p, holding n items needs a space of about n²/(2p).

```java
static double birthdayExact(int n, double space) {
    double noCollision = 1.0;
    for (int i = 0; i < n; i++) noCollision *= (space - i) / space;
    return 1 - noCollision;
}

static double birthdayApprox(double n, double space) {
    return 1 - Math.exp(-n * (n - 1) / (2 * space));
}
```

> **Verified.** For 23 people and 365 days the exact probability is 0.5073 (22 people give less than 0.5), and 1.1774·√365 = 22.49. A 32-bit hash reaches 50% at about 77,162 items, and a 64-bit hash at about 5.06×10⁹ items. A UUIDv4 has 122 random bits, so a 1-in-a-billion collision chance arrives at about 1.03×10¹⁴ IDs. Storing a billion items with a 1-in-a-billion collision chance needs a space of about 5×10²⁶, which is 2^88.7.

Consequences: a 64-bit hash is not a safe unique ID once you have billions of items, 128 bits is comfortable, and an n-bit cryptographic hash gives only about n/2 bits of collision resistance. The same square-root effect sizes hash-table buckets and Bloom filters (Part 2).

## Run it

```
cd code/principles/part-1-distances-and-number-theory/13-birthday-bound
java BirthdayBound.java
```

JDK 17 or newer, no build step. It prints 6 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
birthday: P(23/365) = 0.5073; 32-bit hash 50% at n = 77162; 64-bit hash 50% at n = 5.057e+09
UUIDv4 (122 random bits): p = 1e-9 at n = 1.0312e+14; 1e9 items at p = 1e-9 needs 2^88.7
BirthdayBound: 6 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
