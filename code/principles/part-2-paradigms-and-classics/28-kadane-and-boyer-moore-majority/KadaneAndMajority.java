import java.util.*;

/**
 * Entry 28 of the principles catalog (Part 2): Kadane's algorithm and the Boyer-Moore majority vote
 *
 * HOW IT WORKS
 *   Kadane's algorithm finds the maximum-sum subarray in one pass: the best sum ending here is either this
 *   element alone or this element plus the best sum ending at the previous one. Boyer-Moore majority vote finds
 *   an element occurring more than n/2 times with one counter, then a second pass confirms it.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java KadaneAndMajority.java
 *   Expected: the output in expected-output.txt, ending "KadaneAndMajority: 3925 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class KadaneAndMajority {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long maxSubarray(int[] a) {
        long best = a[0], cur = a[0];
        for (int i = 1; i < a.length; i++) {
            cur = Math.max(a[i], cur + a[i]);
            best = Math.max(best, cur);
        }
        return best;
    }

    static int majority(int[] a) {                          // correct only if a majority element exists
        int cand = 0, count = 0;
        for (int x : a) {
            if (count == 0) cand = x;
            count += (x == cand) ? 1 : -1;
        }
        return cand;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java KadaneAndMajority.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 3000; t++) {
            int n = 1 + rnd.nextInt(30);
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = rnd.nextInt(41) - 20;
            long brute = Long.MIN_VALUE;
            for (int i = 0; i < n; i++) { long s = 0; for (int j = i; j < n; j++) { s += a[j]; brute = Math.max(brute, s); } }
            check(maxSubarray(a) == brute, "Kadane vs all subarrays");
        }
        check(maxSubarray(new int[]{-2, 1, -3, 4, -1, 2, 1, -5, 4}) == 6 && maxSubarray(new int[]{-3, -1, -2}) == -1, "Kadane examples");
        for (int t = 0; t < 3000; t++) {
            int n = 1 + rnd.nextInt(25);
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = rnd.nextInt(3);
            Map<Integer, Integer> cnt = new HashMap<>();
            for (int x : a) cnt.merge(x, 1, Integer::sum);
            for (Map.Entry<Integer, Integer> e : cnt.entrySet())
                if (e.getValue() * 2 > n) check(majority(a) == e.getKey(), "majority vote finds the majority element");
        }
        check(majority(new int[]{1, 2, 3}) == 3, "with no majority the candidate is arbitrary");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("KadaneAndMajority: " + passed + " checks passed");
    }
}
