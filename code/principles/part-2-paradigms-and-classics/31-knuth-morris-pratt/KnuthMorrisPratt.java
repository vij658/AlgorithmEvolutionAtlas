import java.util.*;

/**
 * Entry 31 of the principles catalog (Part 2): Knuth-Morris-Pratt string search
 *
 * HOW IT WORKS
 *   Knuth-Morris-Pratt never re-reads text. A failure table, computed from the pattern alone, says how far the
 *   pattern can shift after a mismatch while keeping the characters already matched, so the search runs in O(n
 *   + m).
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java KnuthMorrisPratt.java
 *   Expected: the output in expected-output.txt, ending "KnuthMorrisPratt: 40005 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class KnuthMorrisPratt {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int[] prefixFunction(String p) {                // pi[i] = longest proper prefix of p[0..i] that is also a suffix
        int[] pi = new int[p.length()];
        for (int i = 1, k = 0; i < p.length(); i++) {
            while (k > 0 && p.charAt(i) != p.charAt(k)) k = pi[k - 1];
            if (p.charAt(i) == p.charAt(k)) k++;
            pi[i] = k;
        }
        return pi;
    }

    static int kmpSearch(String text, String p) {          // first match or -1, O(n + m)
        if (p.isEmpty()) return 0;
        int[] pi = prefixFunction(p);
        for (int i = 0, k = 0; i < text.length(); i++) {
            while (k > 0 && text.charAt(i) != p.charAt(k)) k = pi[k - 1];
            if (text.charAt(i) == p.charAt(k)) k++;
            if (k == p.length()) return i - k + 1;
        }
        return -1;
    }

    static int smallestPeriod(String s) {                  // shortest p such that s is s[0, p) repeated
        int m = s.length();
        if (m == 0) return 0;
        int p = m - prefixFunction(s)[m - 1];
        return m % p == 0 ? p : m;
    }

    static long kmpCompares;                                // instrumented copy

    static int kmpSearchCounted(String text, String p) {
        int[] pi = prefixFunction(p);
        for (int i = 0, k = 0; i < text.length(); i++) {
            while (k > 0) { kmpCompares++; if (text.charAt(i) != p.charAt(k)) k = pi[k - 1]; else break; }
            kmpCompares++;
            if (text.charAt(i) == p.charAt(k)) k++;
            if (k == p.length()) return i - k + 1;
        }
        return -1;
    }

    static long naiveCompares;

    static int naiveSearchCounted(String t, String p) {
        for (int i = 0; i + p.length() <= t.length(); i++) {
            int j = 0;
            while (j < p.length()) { naiveCompares++; if (t.charAt(i + j) != p.charAt(j)) break; j++; }
            if (j == p.length()) return i;
        }
        return -1;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java KnuthMorrisPratt.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        check(Arrays.equals(prefixFunction("abacabad"), new int[]{0, 0, 1, 0, 1, 2, 3, 0}), "prefix function of abacabad");
        for (int t = 0; t < 20_000; t++) {
            StringBuilder sb = new StringBuilder(), pb = new StringBuilder();
            for (int i = 0, n = rnd.nextInt(60); i < n; i++) sb.append((char) ('a' + rnd.nextInt(2)));
            for (int i = 0, n = rnd.nextInt(7); i < n; i++) pb.append((char) ('a' + rnd.nextInt(2)));
            check(kmpSearch(sb.toString(), pb.toString()) == sb.toString().indexOf(pb.toString()), "KMP vs indexOf");
        }
        for (int t = 0; t < 20_000; t++) {
            StringBuilder sb = new StringBuilder();
            for (int i = 0, len = 1 + rnd.nextInt(12); i < len; i++) sb.append((char) ('a' + rnd.nextInt(2)));
            String w = sb.toString();
            int brute = w.length();
            for (int per = 1; per < w.length(); per++)
                if (w.length() % per == 0 && w.substring(0, per).repeat(w.length() / per).equals(w)) { brute = per; break; }
            check(smallestPeriod(w) == brute, "smallest period from the prefix function");
        }
        check(smallestPeriod("abcabcabc") == 3 && smallestPeriod("abcabca") == 7 && smallestPeriod("aaaa") == 1, "period examples");
        int n = 100_000, m = 1000;
        String text = "a".repeat(n), pat = "a".repeat(m - 1) + "b";
        naiveCompares = 0; kmpCompares = 0;
        check(naiveSearchCounted(text, pat) == -1 && kmpSearchCounted(text, pat) == -1, "no match in the adversarial case");
        check(naiveCompares == (long) (n - m + 1) * m, "naive search does (n - m + 1) * m comparisons");
        check(kmpCompares <= 3L * n, "KMP does at most 3n comparisons");
        System.out.println("text a^100000, pattern a^999 b: naive search made " + naiveCompares + " comparisons, KMP made " + kmpCompares);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("KnuthMorrisPratt: " + passed + " checks passed");
    }
}
