import java.util.*;
import java.util.function.DoubleUnaryOperator;

/**
 * Entry 22 of the principles catalog (Part 2): Binary search, and binary search on the answer
 *
 * HOW IT WORKS
 *   Keep an interval that must contain the answer and halve it each step: O(log n) comparisons. The same idea
 *   finds the smallest value that makes a monotone yes/no test succeed ('binary search on the answer'). Compute
 *   the midpoint as lo + (hi - lo)/2 to avoid overflow.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BinarySearch.java
 *   Expected: the output in expected-output.txt, ending "BinarySearch: 2372505 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BinarySearch {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static double log2(double x) { return Math.log(x) / Math.log(2); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int lowerBound(int[] a, int key) {          // first index i with a[i] >= key, or a.length
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] < key) lo = mid + 1; else hi = mid;
        }
        return lo;
    }

    static int upperBound(int[] a, int key) {          // first index i with a[i] > key, or a.length
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (a[mid] <= key) lo = mid + 1; else hi = mid;
        }
        return lo;
    }

    static int probes;                                 // instrumented copy

    static int lowerBoundCounted(int[] a, int key) {
        int lo = 0, hi = a.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            probes++;
            if (a[mid] < key) lo = mid + 1; else hi = mid;
        }
        return lo;
    }

    static int daysNeeded(int[] w, int cap) {
        int days = 1, load = 0;
        for (int x : w) {
            if (load + x > cap) { days++; load = 0; }
            load += x;
        }
        return days;
    }

    static int minShipCapacity(int[] weights, int days) {   // smallest capacity that ships in order within `days`
        int lo = Arrays.stream(weights).max().getAsInt();    // must fit the heaviest package
        int hi = Arrays.stream(weights).sum();               // ships everything on day one
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (daysNeeded(weights, mid) <= days) hi = mid; else lo = mid + 1;
        }
        return lo;
    }

    static double bisect(DoubleUnaryOperator f, double lo, double hi, int iterations) {   // f increasing, f(lo) <= 0 < f(hi)
        for (int i = 0; i < iterations; i++) {
            double mid = 0.5 * (lo + hi);
            if (f.applyAsDouble(mid) > 0) hi = mid; else lo = mid;
        }
        return 0.5 * (lo + hi);
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BinarySearch.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 5000; t++) {
            int[] a = new int[rnd.nextInt(30)];
            for (int i = 0; i < a.length; i++) a[i] = rnd.nextInt(20);
            Arrays.sort(a);
            for (int key = -1; key <= 21; key++) {
                int lb = 0, ub = 0;
                while (lb < a.length && a[lb] < key) lb++;
                while (ub < a.length && a[ub] <= key) ub++;
                check(lowerBound(a, key) == lb && upperBound(a, key) == ub, "lower/upper bound vs linear scan");
            }
        }
        check(lowerBound(new int[0], 5) == 0, "empty array");
        int worstSeen = 0;
        for (int n = 1; n <= 1500; n++) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = 2 * i;
            int bound = 31 - Integer.numberOfLeadingZeros(n) + 1;      // floor(log2 n) + 1
            for (int key = -1; key <= 2 * n; key++) {                  // hits every distinct outcome
                probes = 0;
                lowerBoundCounted(a, key);
                check(probes <= bound, "probe bound floor(log2 n) + 1");
                worstSeen = Math.max(worstSeen, probes);
            }
        }
        int[] big = new int[1_000_000];
        for (int i = 0; i < big.length; i++) big[i] = i;
        int maxProbes = 0;
        for (int t = 0; t < 20000; t++) {
            probes = 0;
            lowerBoundCounted(big, rnd.nextInt(1_100_000) - 50_000);
            maxProbes = Math.max(maxProbes, probes);
        }
        check(maxProbes <= 20, "at most 20 probes for a million elements");
        System.out.println("1,000,000 sorted ints: at most " + maxProbes + " probes observed (bound 20)");

        for (int t = 0; t < 3000; t++) {
            int[] w = new int[1 + rnd.nextInt(12)];
            for (int i = 0; i < w.length; i++) w[i] = 1 + rnd.nextInt(30);
            int days = 1 + rnd.nextInt(w.length);
            int brute = Arrays.stream(w).max().getAsInt();
            while (daysNeeded(w, brute) > days) brute++;
            check(minShipCapacity(w, days) == brute, "binary search on the answer vs linear scan");
        }
        check(minShipCapacity(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 5) == 15, "classic shipping example");
        double root = bisect(x -> x * x - 2, 1, 2, 40);
        check(Math.abs(root - Math.sqrt(2)) < 1e-12, "bisection: 40 halvings give 1e-12");
        check((int) Math.ceil(log2(1e12)) == 40, "ceil(log2(1e12)) = 40");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("BinarySearch: " + passed + " checks passed");
    }
}
