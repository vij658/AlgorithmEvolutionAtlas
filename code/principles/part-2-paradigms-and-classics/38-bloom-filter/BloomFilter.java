import java.util.*;

/**
 * Entry 38 of the principles catalog (Part 2): Bloom filter
 *
 * HOW IT WORKS
 *   A bit array plus k hash functions: insert sets k bits, a query checks them. It can say 'maybe present'
 *   wrongly but never 'absent' wrongly. The false-positive rate is about (1 - e^(-kn/m))^k, and two base hashes
 *   are enough to generate all k.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BloomFilter.java
 *   Expected: the output in expected-output.txt, ending "BloomFilter: 100004 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BloomFilter {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long mix(long z) {                              // splitmix64 finalizer: a strong 64-bit mixer
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
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

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BloomFilter.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        int n = 100_000;
        Bloom bf = new Bloom(n, 0.01);
        for (long i = 0; i < n; i++) bf.add(i);
        for (long i = 0; i < n; i++) check(bf.mightContain(i), "no false negatives");
        int probes = 1_000_000, fp = 0;
        for (long i = 0; i < probes; i++) if (bf.mightContain((1L << 40) + i)) fp++;
        double rate = fp / (double) probes;
        check(rate > 0.0085 && rate < 0.0115, "false-positive rate near the 1% target, got " + rate);
        check(bf.m / (double) n > 9.58 && bf.m / (double) n < 9.59 && bf.k == 7, "9.585 bits per item and 7 hash functions");
        int best = 1;
        for (int k = 1; k <= 20; k++) if (bloomTheory(bf.m, n, k) < bloomTheory(bf.m, n, best)) best = k;
        check(best == 7, "the formula's best integer k is 7");
        System.out.printf("Bloom filter for %d items at 1%%: m = %d bits (%.3f per item, %d KiB), k = %d; measured false-positive rate %.4f over %d absent keys; formula %.4f%n",
                n, bf.m, bf.m / (double) n, bf.m / 8 / 1024, bf.k, rate, probes, bloomTheory(bf.m, n, bf.k));
        Bloom over = new Bloom(n, 0.01);                          // sized for 100,000 items ...
        for (long i = 0; i < 2L * n; i++) over.add(i);            // ... but fed 200,000
        int fp2 = 0;
        for (long i = 0; i < probes; i++) if (over.mightContain((1L << 40) + i)) fp2++;
        double rate2 = fp2 / (double) probes, theory2 = bloomTheory(over.m, 2.0 * n, over.k);
        check(Math.abs(rate2 - theory2) < 0.01 && rate2 > 0.10, "an overfilled filter's false-positive rate follows the formula, got " + rate2);
        System.out.printf("the same filter after 200,000 insertions (twice its design size): measured false-positive rate %.4f, formula %.4f%n", rate2, theory2);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("BloomFilter: " + passed + " checks passed");
    }
}
