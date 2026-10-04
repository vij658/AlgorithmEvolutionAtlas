import java.util.*;

/**
 * Entry 23 of the principles catalog (Part 2): Dynamic programming
 *
 * HOW IT WORKS
 *   When a problem's answer is built from answers to overlapping subproblems, compute each subproblem once and
 *   store it, either top-down with memoisation or bottom-up in a table. Fibonacci, knapsack, longest common
 *   subsequence and coin change are the worked examples.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java DynamicProgramming.java
 *   Expected: the output in expected-output.txt, ending "DynamicProgramming: 1504 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class DynamicProgramming {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int knapsack(int[] w, int[] v, int cap) {
        int[] best = new int[cap + 1];
        for (int i = 0; i < w.length; i++)
            for (int c = cap; c >= w[i]; c--)              // go downward so each item is used at most once
                best[c] = Math.max(best[c], best[c - w[i]] + v[i]);
        return best[cap];
    }

    static int lcsLength(String a, String b) {
        int[][] dp = new int[a.length() + 1][b.length() + 1];
        for (int i = 1; i <= a.length(); i++)
            for (int j = 1; j <= b.length(); j++)
                dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1)
                        ? dp[i - 1][j - 1] + 1
                        : Math.max(dp[i - 1][j], dp[i][j - 1]);
        return dp[a.length()][b.length()];
    }

    static int minCoins(int[] coins, int amount) {
        final int INF = Integer.MAX_VALUE / 2;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, INF);
        dp[0] = 0;
        for (int a = 1; a <= amount; a++)
            for (int c : coins)
                if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
        return dp[amount] >= INF ? -1 : dp[amount];
    }

    static long calls;

    static long fibNaive(int n) { calls++; return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2); }

    static long fibMemo(int n, long[] memo) {
        calls++;
        if (n < 2) return n;
        if (memo[n] != 0) return memo[n];
        return memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    }

    static boolean isSubsequence(String s, String t) {
        int j = 0;
        for (int i = 0; i < t.length() && j < s.length(); i++) if (t.charAt(i) == s.charAt(j)) j++;
        return j == s.length();
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java DynamicProgramming.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 500; t++) {
            int n = 1 + rnd.nextInt(12), cap = 1 + rnd.nextInt(40);
            int[] w = new int[n], v = new int[n];
            for (int i = 0; i < n; i++) { w[i] = 1 + rnd.nextInt(15); v[i] = 1 + rnd.nextInt(30); }
            int brute = 0;
            for (int mask = 0; mask < (1 << n); mask++) {
                int ws = 0, vs = 0;
                for (int i = 0; i < n; i++) if ((mask >> i & 1) == 1) { ws += w[i]; vs += v[i]; }
                if (ws <= cap) brute = Math.max(brute, vs);
            }
            check(knapsack(w, v, cap) == brute, "knapsack vs subset enumeration");
        }
        check(knapsack(new int[]{1, 3, 4, 5}, new int[]{1, 4, 5, 7}, 7) == 9, "knapsack textbook example");
        for (int t = 0; t < 500; t++) {
            StringBuilder sa = new StringBuilder(), sb = new StringBuilder();
            for (int i = 0, n = rnd.nextInt(10); i < n; i++) sa.append((char) ('a' + rnd.nextInt(3)));
            for (int i = 0, n = rnd.nextInt(10); i < n; i++) sb.append((char) ('a' + rnd.nextInt(3)));
            String a = sa.toString(), b = sb.toString();
            int brute = 0;
            for (int mask = 0; mask < (1 << a.length()); mask++) {
                StringBuilder sub = new StringBuilder();
                for (int i = 0; i < a.length(); i++) if ((mask >> i & 1) == 1) sub.append(a.charAt(i));
                if (sub.length() > brute && isSubsequence(sub.toString(), b)) brute = sub.length();
            }
            check(lcsLength(a, b) == brute, "LCS vs subsequence enumeration");
        }
        check(lcsLength("AGGTAB", "GXTXAYB") == 4, "LCS textbook example");
        for (int t = 0; t < 500; t++) {
            int[] coins = new int[1 + rnd.nextInt(4)];
            for (int i = 0; i < coins.length; i++) coins[i] = 1 + rnd.nextInt(12);
            int amount = rnd.nextInt(60);
            int[] dist = new int[amount + 1];
            Arrays.fill(dist, -1);
            dist[0] = 0;
            ArrayDeque<Integer> q = new ArrayDeque<>();
            q.add(0);
            while (!q.isEmpty()) {
                int cur = q.poll();
                for (int c : coins) if (cur + c <= amount && dist[cur + c] < 0) { dist[cur + c] = dist[cur] + 1; q.add(cur + c); }
            }
            check(minCoins(coins, amount) == dist[amount], "coin change DP vs breadth-first search");
        }
        calls = 0;
        long f = fibNaive(30);
        long naiveCalls = calls;
        calls = 0;
        long g = fibMemo(30, new long[31]);
        check(f == 832040 && g == 832040, "fib(30)");
        check(naiveCalls == 2_692_537 && calls == 59, "call counts");
        System.out.println("fib(30): naive recursion made " + naiveCalls + " calls, memoized made " + calls);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("DynamicProgramming: " + passed + " checks passed");
    }
}
