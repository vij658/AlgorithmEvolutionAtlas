# 40. HyperLogLog

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#40-hyperloglog)

## How it works

Hash every item and, in each of m buckets, remember the longest run of leading zeros seen. Many distinct items make long runs likely, so a harmonic mean of 2^runs estimates the count with standard error about 1.04/√m, using a few kilobytes for billions of items.

## In depth (from the catalog page)

Counting distinct items exactly needs memory proportional to the number of distinct items. HyperLogLog (Flajolet, Fusy, Gandouet and Meunier, 2007) estimates the count within a couple of percent from a few kilobytes. Hash every item to a uniform 64-bit value. Use its first p bits to pick one of m = 2ᵖ registers, and in that register remember the largest "number of leading zeros in the remaining bits, plus one". A register that has seen ρ suggests that about 2^ρ distinct items went into it, and a harmonic mean across registers calms the noise: the standard error is about 1.04/√m. A linear-counting correction handles small counts.

```java
static final class HyperLogLog {
    final int p, m;
    final byte[] reg;
    HyperLogLog(int p) { this.p = p; m = 1 << p; reg = new byte[m]; }
    void add(long x) {
        long h = mix(x);                                          // mix from entry 38
        int idx = (int) (h >>> (64 - p));                         // first p bits choose a register
        long rest = (h << p) | (1L << (p - 1));                   // guard bit bounds the leading-zero count
        byte rank = (byte) (Long.numberOfLeadingZeros(rest) + 1);
        if (rank > reg[idx]) reg[idx] = rank;
    }
    void merge(HyperLogLog o) { for (int i = 0; i < m; i++) if (o.reg[i] > reg[i]) reg[i] = o.reg[i]; }
    double estimate() {
        double alpha = 0.7213 / (1 + 1.079 / m);
        double sum = 0;
        int zeros = 0;
        for (byte r : reg) { sum += Math.pow(2, -r); if (r == 0) zeros++; }
        double e = alpha * m * (double) m / sum;
        if (e <= 2.5 * m && zeros > 0) e = m * Math.log((double) m / zeros);   // small-range correction (linear counting)
        return e;
    }
}
```

> **Verified.** With p = 14, which is 16,384 one-byte registers, the theoretical standard error is 1.04/√16,384 = 0.81%. After adding 1,000, 10,000, 100,000 and 1,000,000 distinct keys, the estimates were 1,009 (+0.95%), 10,052 (+0.52%), 99,781 (−0.22%) and 997,636 (−0.24%), all within three standard errors. Adding each of 50,000 keys three times left the registers identical to adding each once. Merging the sketches of two overlapping ranges, 0 to 179,999 and 120,000 to 299,999, gave registers identical to the sketch of the union.

<!-- -->

> **Pitfall.** The error is a *standard* error relative to n, so roughly one estimate in three lands further out than 0.81%. A weak hash ruins the estimate, which is why `add` mixes its input first. The sketch cannot list or delete items, and it is the wrong tool when you need exact counts, such as billing.

**Use it for** unique visitors, distinct queries or users per day, and cardinality estimates inside databases. Redis exposes it as `PFADD`, `PFCOUNT` and `PFMERGE` and documents up to 12 KB per counter and a 0.81% standard error, the same figure as above. Because sketches merge by taking the maximum of each register, they combine across servers and time windows without moving the raw data.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/40-hyperloglog
java HyperLogLogDemo.java
```

JDK 17 or newer, no build step. It prints 6 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
HyperLogLog p = 14 (16384 one-byte registers, standard error 0.81%): n = 1,000 -> 1009 (+0.95%); n = 10,000 -> 10052 (+0.52%); n = 100,000 -> 99781 (-0.22%); n = 1,000,000 -> 997636 (-0.24%); 
HyperLogLogDemo: 6 checks passed
```

## References

- Flajolet, Fusy, Gandouet and Meunier, [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) (2007): standard error about 1.04/√m, the constant `0.7213/(1 + 1.079/m)` and the small-range correction. Redis, [HyperLogLog documentation](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/): up to 12 KB and a 0.81% standard error.
