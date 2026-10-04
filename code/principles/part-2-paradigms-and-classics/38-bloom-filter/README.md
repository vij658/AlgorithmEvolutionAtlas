# 38. Bloom filter

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#38-bloom-filter)

## How it works

A bit array plus k hash functions: insert sets k bits, a query checks them. It can say 'maybe present' wrongly but never 'absent' wrongly. The false-positive rate is about (1 − e^(−kn/m))^k, and two base hashes are enough to generate all k.

## In depth (from the catalog page)

A Bloom filter (Bloom, 1970) answers "have I seen this key?" with a bit array and k hash functions. Adding a key sets k bits. A lookup says "definitely not present" if any of its k bits is 0 and "probably present" if all are 1. There are no false negatives. After n insertions into m bits, the false-positive probability is about `(1 − e^(−kn/m))^k`. That is smallest at `k = (m/n)·ln 2`, and hitting a target rate p takes `m = −n·ln p / (ln 2)²` bits: about 9.585 bits per key for 1%, plus about 4.8 more bits per key for every further factor of ten. The code derives its k bit positions from two hashes as `h1 + i·h2`, a trick Kirsch and Mitzenmacher showed costs nothing in the asymptotic false-positive rate.

```java
static long mix(long z) {                              // splitmix64 finalizer: a strong 64-bit mixer
    z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
    z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
    return z ^ (z >>> 31);
}

static final class Bloom {
    final BitSet bits;
    final int m, k;
    Bloom(int expectedItems, double fpRate) {
        m = (int) Math.ceil(-expectedItems * Math.log(fpRate) / (Math.log(2) * Math.log(2)));
        k = Math.max(1, (int) Math.round((double) m / expectedItems * Math.log(2)));
        bits = new BitSet(m);
    }
    private int index(long key, int i) {                         // double hashing: h1 + i * h2
        long h1 = mix(key), h2 = mix(key ^ 0x9e3779b97f4a7c15L) | 1;
        return (int) Long.remainderUnsigned(h1 + i * h2, m);
    }
    void add(long key) { for (int i = 0; i < k; i++) bits.set(index(key, i)); }
    boolean mightContain(long key) {
        for (int i = 0; i < k; i++) if (!bits.get(index(key, i))) return false;
        return true;
    }
}

static double bloomTheory(double m, double n, int k) { return Math.pow(1 - Math.exp(-k * n / m), k); }
```

> **Verified.** For 100,000 keys at a 1% target the constructor chose m = 958,506 bits (9.585 per key, 117 KiB) and k = 7. All 100,000 inserted keys were found, so there were no false negatives. Over 1,000,000 keys that had never been inserted, the measured false-positive rate was 0.0100, the same as the formula's 0.0100, and the formula's best whole number of hash functions is 7. The same filter after 200,000 insertions, twice its design size, measured 0.1587 against 0.1575 from the formula: a 1% filter had turned into a 16% filter.

<!-- -->

> **Pitfall.** A plain Bloom filter cannot delete a key, because clearing a bit may erase other keys; counting Bloom filters and cuckoo filters support deletion at some cost in space. And size the filter for the count you will really insert. Guava's documentation warns that overflowing a `BloomFilter` with significantly more elements than specified saturates it and sharply worsens the false-positive probability, which is the 1%-to-16% jump measured above.

**Use it for** skipping expensive lookups. Once a filter policy is set, RocksDB writes a Bloom filter into every new on-disk file to decide whether that file may contain the key, at about 10 bits per key for a 1% false-positive rate, in line with the 9.585 bits above. Guava ships a ready-made `BloomFilter`. Bloom filters also suit "already seen" sets in crawlers and caches, where a rare false "yes" is cheap and a false "no" is not allowed.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/38-bloom-filter
java BloomFilter.java
```

JDK 17 or newer, no build step. It prints 100,004 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Bloom filter for 100000 items at 1%: m = 958506 bits (9.585 per item, 117 KiB), k = 7; measured false-positive rate 0.0100 over 1000000 absent keys; formula 0.0100
the same filter after 200,000 insertions (twice its design size): measured false-positive rate 0.1587, formula 0.1575
BloomFilter: 100004 checks passed
```

## References

- Kirsch and Mitzenmacher, [Less Hashing, Same Performance: Building a Better Bloom Filter](https://www.eecs.harvard.edu/~michaelm/postscripts/rsa2008.pdf): two hash functions suffice, with no loss in the asymptotic false-positive probability. RocksDB, [Bloom filter wiki](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter): a filter in every new SST file, about 10 bits per key for a 1% rate. Guava, [`BloomFilter`](https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/hash/BloomFilter.html): overflowing a filter sharply worsens its false-positive probability.
