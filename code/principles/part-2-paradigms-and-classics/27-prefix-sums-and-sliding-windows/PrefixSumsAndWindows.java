import java.util.*;

/**
 * Entry 27 of the principles catalog (Part 2): Prefix sums, difference arrays, sliding windows and the monotonic deque
 *
 * HOW IT WORKS
 *   Precompute running totals so any range sum is one subtraction; a difference array does the reverse for
 *   range updates. A sliding window moves two pointers through the array once, and a monotonic deque keeps the
 *   window's maximum available in O(1).
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java PrefixSumsAndWindows.java
 *   Expected: the output in expected-output.txt, ending "PrefixSumsAndWindows: 33846 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class PrefixSumsAndWindows {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long[] prefix(int[] a) {                         // p[i] = sum of a[0..i)
        long[] p = new long[a.length + 1];
        for (int i = 0; i < a.length; i++) p[i + 1] = p[i] + a[i];
        return p;
    }

    static int[] slidingMax(int[] a, int k) {               // maximum of every window of size k, O(n)
        int[] out = new int[a.length - k + 1];
        Deque<Integer> dq = new ArrayDeque<>();             // indices whose values are decreasing
        for (int i = 0; i < a.length; i++) {
            while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();
            dq.addLast(i);
            if (dq.peekFirst() <= i - k) dq.pollFirst();
            if (i >= k - 1) out[i - k + 1] = a[dq.peekFirst()];
        }
        return out;
    }

    static int countSubarraysWithSum(int[] a, int target) {
        Map<Long, Integer> seen = new HashMap<>();
        seen.put(0L, 1);
        long sum = 0;
        int count = 0;
        for (int x : a) {
            sum += x;
            count += seen.getOrDefault(sum - target, 0);
            seen.merge(sum, 1, Integer::sum);
        }
        return count;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java PrefixSumsAndWindows.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 2000; t++) {
            int n = 1 + rnd.nextInt(40);
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = rnd.nextInt(21) - 10;
            long[] p = prefix(a);
            int l = rnd.nextInt(n + 1), r = l + rnd.nextInt(n - l + 1);
            long brute = 0;
            for (int i = l; i < r; i++) brute += a[i];
            check(p[r] - p[l] == brute, "range sum from prefix sums");
            int k = 1 + rnd.nextInt(n);
            int[] got = slidingMax(a, k);
            for (int s = 0; s + k <= n; s++) {
                int m = Integer.MIN_VALUE;
                for (int i = s; i < s + k; i++) m = Math.max(m, a[i]);
                check(got[s] == m, "sliding window maximum");
            }
            int target = rnd.nextInt(11) - 5, brute2 = 0;
            for (int i = 0; i < n; i++) { int s = 0; for (int j = i; j < n; j++) { s += a[j]; if (s == target) brute2++; } }
            check(countSubarraysWithSum(a, target) == brute2, "subarrays with a given sum");
        }
        for (int t = 0; t < 500; t++) {                     // difference array
            int n = 1 + rnd.nextInt(30);
            long[] diff = new long[n + 1], naive = new long[n];
            for (int op = 0; op < 20; op++) {
                int l = rnd.nextInt(n), r = l + rnd.nextInt(n - l + 1);
                long v = rnd.nextInt(11) - 5;
                diff[l] += v; diff[r] -= v;
                for (int i = l; i < r; i++) naive[i] += v;
            }
            long run = 0;
            for (int i = 0; i < n; i++) { run += diff[i]; check(run == naive[i], "difference array"); }
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("PrefixSumsAndWindows: " + passed + " checks passed");
    }
}
