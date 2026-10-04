import java.util.*;

/**
 * Entry 47 of the principles catalog (Part 3): Zipf's law and cache sizing
 *
 * HOW IT WORKS
 *   In a Zipf distribution the k-th most popular item is requested in proportion to 1/k^s, so a small cache of
 *   the most popular items serves a large share of requests. The program measures the hit ratio for different
 *   cache sizes and exponents.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ZipfCacheSizing.java
 *   Expected: the output in expected-output.txt, ending "ZipfCacheSizing: 5 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ZipfCacheSizing {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double harmonic(long k, double s) { double h = 0; for (long i = 1; i <= k; i++) h += Math.pow(i, -s); return h; }

    static double zipfHitRate(long cached, long items, double s) { return harmonic(cached, s) / harmonic(items, s); }

    /** Inverse-CDF sampling: binary search (entry 22) in the cumulative distribution. Returns zero-based ranks. */
    static int[] zipfSample(int items, double s, int count, Random rnd) {
        double[] cdf = new double[items];
        double acc = 0;
        for (int i = 0; i < items; i++) { acc += Math.pow(i + 1, -s); cdf[i] = acc; }
        int[] out = new int[count];
        for (int j = 0; j < count; j++) {
            double u = rnd.nextDouble() * acc;
            int lo = 0, hi = items - 1;
            while (lo < hi) { int mid = (lo + hi) >>> 1; if (cdf[mid] < u) lo = mid + 1; else hi = mid; }
            out[j] = lo;
        }
        return out;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ZipfCacheSizing.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(47);
        int items = 100_000, count = 3_000_000;
        int[] trace = zipfSample(items, 1.0, count, rnd);
        StringBuilder sb = new StringBuilder();
        for (int k : new int[]{100, 1_000, 10_000}) {
            int hits = 0;
            for (int r : trace) if (r < k) hits++;
            double measured = hits / (double) count, formula = zipfHitRate(k, items, 1.0);
            check(close(measured, formula, 0.002), "measured hit rate of a static top-" + k + " cache matches the harmonic-number formula");
            sb.append(String.format("top %,d of %,d: measured %.4f, formula %.4f; ", k, items, measured, formula));
        }
        System.out.println("Zipf, exponent 1, sampled " + count + " requests: " + sb);
        StringBuilder table = new StringBuilder();
        for (double s : new double[]{0.8, 1.0, 1.2}) {
            table.append(String.format("s = %.1f: top 0.1%% -> %.1f%%, top 1%% -> %.1f%%, top 10%% -> %.1f%%; ", s,
                    100 * zipfHitRate(1_000, 1_000_000, s), 100 * zipfHitRate(10_000, 1_000_000, s), 100 * zipfHitRate(100_000, 1_000_000, s)));
        }
        System.out.println("share of requests served by caching the most popular items out of 1,000,000: " + table);
        check(zipfHitRate(10_000, 1_000_000, 1.0) > 0.65 && zipfHitRate(10_000, 1_000_000, 1.0) < 0.70, "with s = 1, the top 1% of a million items serves about two thirds of requests");
        check(zipfHitRate(1, 1_000_000, 1.0) < 0.07 && zipfHitRate(1, 1_000_000, 1.0) > 0.06, "with s = 1 the single most popular of a million items takes about 7%");
        System.out.printf("with s = 1 over 1,000,000 items the single most popular item takes %.2f%% of all requests and the top 10 take %.1f%%%n", 100 * zipfHitRate(1, 1_000_000, 1.0), 100 * zipfHitRate(10, 1_000_000, 1.0));
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("ZipfCacheSizing: " + passed + " checks passed");
    }
}
