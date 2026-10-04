# 29. Fisher–Yates shuffle and reservoir sampling

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#29-fisheryates-shuffle-and-reservoir-sampling)

## How it works

Fisher–Yates shuffles by walking backwards and swapping each position with a random earlier (or same) position, giving every permutation exactly once. Reservoir sampling keeps k items from a stream of unknown length, replacing an item with probability k/i at step i, so every item ends up kept with probability k/n.

## In depth (from the catalog page)

A fair shuffle walks from the end of the array and swaps each position with a random position at or before it. Reservoir sampling picks k items uniformly from a stream of unknown length in one pass: keep the first k, then let item number i (counting from 0) replace a random slot with probability k/(i + 1).

```java
static void shuffle(int[] a, Random rnd) {
    for (int i = a.length - 1; i > 0; i--) {
        int j = rnd.nextInt(i + 1);                     // 0..i inclusive
        int t = a[i]; a[i] = a[j]; a[j] = t;
    }
}

static int[] reservoirSample(int[] stream, int k, Random rnd) {   // reads the stream once, keeps k items
    int[] res = Arrays.copyOf(stream, k);
    for (int i = k; i < stream.length; i++) {
        int j = rnd.nextInt(i + 1);
        if (j < k) res[j] = stream[i];
    }
    return res;
}
```

> **Verified.** The tempting shuffle that swaps every position with a random position *anywhere* is biased, for a counting reason: it makes nⁿ equally likely choices, and nⁿ is not a multiple of n!. For three items it has 3³ = 27 choice sequences for 6 permutations. Enumerated exactly, the permutations 012, 021, 102, 120, 201 and 210 get 4, 5, 5, 5, 4 and 4 of them, so none gets the fair share of 4.5. With four items there are 256 sequences, and the per-permutation counts run from 8 to 15 where a fair shuffle would give 10.67. Fisher–Yates, enumerated over all of its n! choice sequences for n = 3, 4 and 5, produced 6, 24 and 120 distinct permutations: every permutation exactly once. Keeping 3 of 10 items with `reservoirSample` over 200,000 trials, every item was kept with a frequency within 0.0010 of the ideal 0.3.

<!-- -->

> **Pitfall.** Fisher–Yates breaks if you are off by one. Draw `j` from `0..i-1` instead of `0..i` (that is Sattolo's algorithm, which produces only cyclic permutations) and no element can ever stay where it started. For n = 3, 4 and 5 the program found no fixed points and only 2, 6 and 24 of the 6, 24 and 120 permutations reachable.

<!-- -->

> **Pitfall.** A shuffle can be no more random than its generator's state. `java.util.Random` keeps a 48-bit state, so it can produce at most 2⁴⁸ ≈ 2.8×10¹⁴ different shuffles. 16! = 2.09×10¹³ fits under that, 17! = 3.56×10¹⁴ does not, and a 52-card deck needs log₂(52!) = 225.58, so 226 bits of seed. For anything with money or security attached, use `SecureRandom`. And don't hand-roll the shuffle at all: `Collections.shuffle` implements Fisher–Yates, and its Javadoc describes walking the list backwards and swapping a randomly selected element, taken from the part up to and including the current position, into the current position.

**Use it for** shuffling, sampling without replacement, A/B-test assignment, bootstrap resampling, and keeping a uniform sample of a log or event stream you can only read once.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/29-fisher-yates-and-reservoir-sampling
java ShuffleAndReservoir.java
```

JDK 17 or newer, no build step. It prints 160 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
naive shuffle of [0,1,2]: outcome counts out of 27 = {[0, 1, 2]=4, [0, 2, 1]=5, [1, 0, 2]=5, [1, 2, 0]=5, [2, 0, 1]=4, [2, 1, 0]=4}
naive shuffle of 4 items: 256 equally likely index sequences, per-permutation counts range from 8 to 15 (a uniform shuffle would give 256/24 = 10.67 each)
reservoir sample of 3 from 10: every item kept with frequency within 0.0010 of 0.3
shuffle with nextInt(i) instead of nextInt(i + 1): for n = 3, 4, 5 no element ever stays in place, and only 2, 6, 24 of the 6, 24, 120 permutations are reachable
java.util.Random keeps a 48-bit state: at most 2^48 = 281474976710656 shuffles. 16! = 20922789888000 fits under that, 17! = 355687428096000 does not; a 52-card deck needs log2(52!) = 225.58, so 226 bits of seed
ShuffleAndReservoir: 160 checks passed
```

## References

- Oracle, [`Collections` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collections.html): `shuffle` walks the list backwards swapping a randomly selected earlier element into the current position; `binarySearch` gives no guarantee which duplicate is found and returns `-(insertion point) - 1` for a missing key.
- Oracle, [`Random` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Random.html): a 48-bit seed, and not cryptographically secure.
