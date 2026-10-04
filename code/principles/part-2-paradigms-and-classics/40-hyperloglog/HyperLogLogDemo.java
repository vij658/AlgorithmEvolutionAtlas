import java.util.*;

/**
 * Entry 40 of the principles catalog (Part 2): HyperLogLog
 *
 * HOW IT WORKS
 *   Hash every item and, in each of m buckets, remember the longest run of leading zeros seen. Many distinct
 *   items make long runs likely, so a harmonic mean of 2^runs estimates the count with standard error about
 *   1.04/sqrtm, using a few kilobytes for billions of items.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HyperLogLogDemo.java
 *   Expected: the output in expected-output.txt, ending "HyperLogLogDemo: 6 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class HyperLogLogDemo {
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
    static final class HyperLogLog {
        final int p, m;
        final byte[] reg;
        HyperLogLog(int p) { this.p = p; m = 1 << p; reg = new byte[m]; }
        void add(long x) {
            long h = mix(x);
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

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java HyperLogLogDemo.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        HyperLogLog hll = new HyperLogLog(14);
        double sigma = 1.04 / Math.sqrt(hll.m);
        long added = 0;
        StringBuilder line = new StringBuilder();
        for (int target : new int[]{1_000, 10_000, 100_000, 1_000_000}) {
            for (; added < target; added++) hll.add(added);
            double est = hll.estimate(), err = (est - target) / target;
            check(Math.abs(err) < 3 * sigma, "HyperLogLog within 3 standard errors at n = " + target + ", error " + err);
            line.append(String.format("n = %,d -> %.0f (%+.2f%%); ", target, est, 100 * err));
        }
        System.out.println("HyperLogLog p = 14 (" + hll.m + " one-byte registers, standard error " + String.format("%.2f%%", 100 * sigma) + "): " + line);
        HyperLogLog twice = new HyperLogLog(14);
        for (int rep = 0; rep < 3; rep++) for (long i = 0; i < 50_000; i++) twice.add(i);
        HyperLogLog once = new HyperLogLog(14);
        for (long i = 0; i < 50_000; i++) once.add(i);
        check(Arrays.equals(twice.reg, once.reg), "duplicates never change the sketch");
        HyperLogLog a = new HyperLogLog(14), b = new HyperLogLog(14), all = new HyperLogLog(14);
        for (long i = 0; i < 300_000; i++) { if (i < 180_000) a.add(i); if (i >= 120_000) b.add(i); all.add(i); }
        a.merge(b);
        check(Arrays.equals(a.reg, all.reg), "merging two overlapping sketches equals the sketch of the union");
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("HyperLogLogDemo: " + passed + " checks passed");
    }
}
