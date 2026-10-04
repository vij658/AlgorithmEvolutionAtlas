# 12. Sieve of Eratosthenes

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#12-sieve-of-eratosthenes)

## How it works

Write down 2..n; for each number still unmarked, cross out its multiples starting from its square. What survives is prime. Only primes up to √n need sieving, and the total work is O(n log log n).

## In depth (from the catalog page)

List every prime up to n by crossing out the multiples of each prime, starting at its square. Time is O(n log log n).

```java
static int[] primesUpTo(int n) {
    boolean[] composite = new boolean[n + 1];
    for (long i = 2; i * i <= n; i++)
        if (!composite[(int) i])
            for (long j = i * i; j <= n; j += i) composite[(int) j] = true;
    return IntStream.rangeClosed(2, n).filter(i -> !composite[i]).toArray();
}
```

> **Verified.** The primes up to 30 are 2, 3, 5, 7, 11, 13, 17, 19, 23 and 29. The counts π(10,000) = 1,229 and π(1,000,000) = 78,498 match the known values.

Memory here is one byte per number; use a `BitSet` for one bit per number, or a segmented sieve to go past what fits in memory. A "smallest prime factor" variant of the same sieve lets you factor any number below n in O(log n) steps.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/12-sieve-of-eratosthenes
java SieveOfEratosthenes.java
```

JDK 17 or newer, no build step. It prints 3 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
SieveOfEratosthenes: 3 checks passed
```

## References

- **Watch:** [Sieve of Eratosthenes — Khan Academy](https://www.youtube.com/watch?v=klcIklsWzrY)
- **Read:** [Sieve of Eratosthenes — CP-Algorithms](https://cp-algorithms.com/algebra/sieve-of-eratosthenes.html)
- **Original:** [M. E. O'Neill, The Genuine Sieve of Eratosthenes (J. Functional Programming, 2009)](https://www.cs.hmc.edu/~oneill/papers/Sieve-JFP.pdf)
- **History and more links:** [Era 1 reference catalog](../../../../book/era-01-the-first-algorithms/reference-catalog.md#9-the-sieve-of-eratosthenes)
