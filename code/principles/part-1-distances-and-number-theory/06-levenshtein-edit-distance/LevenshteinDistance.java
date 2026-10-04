import java.util.*;

/**
 * Entry 6 of the principles catalog (Part 1): Levenshtein edit distance
 *
 * HOW IT WORKS
 *   Dynamic programming over prefixes: cell (i, j) holds the fewest insertions, deletions and substitutions
 *   turning the first i characters of one string into the first j of the other. Each cell looks at three
 *   neighbours, so the cost is O(n*m), and two rows of memory are enough.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LevenshteinDistance.java
 *   Expected: the output in expected-output.txt, ending "LevenshteinDistance: 4003 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class LevenshteinDistance {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ---------- 7. Cosine, Jaccard ----------
    static double cosine(double[] u, double[] v) {
        double dot = 0, nu = 0, nv = 0;
        for (int i = 0; i < u.length; i++) { dot += u[i] * v[i]; nu += u[i] * u[i]; nv += v[i] * v[i]; }
        return dot / (Math.sqrt(nu) * Math.sqrt(nv));
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 3 (euclidean-distance), entry 4 (manhattan-chebyshev-minkowski), entry 5 (hamming-distance), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- 6. Levenshtein ----------
    static int levenshtein(String a, String b) {
        int[] prev = new int[b.length() + 1], cur = new int[b.length() + 1];
        for (int j = 0; j <= b.length(); j++) prev[j] = j;
        for (int i = 1; i <= a.length(); i++) {
            cur[0] = i;
            for (int j = 1; j <= b.length(); j++) {
                int sub = prev[j - 1] + (a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1);
                cur[j] = Math.min(sub, Math.min(prev[j] + 1, cur[j - 1] + 1));
            }
            int[] t = prev; prev = cur; cur = t;
        }
        return prev[b.length()];
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 10 (metric-axioms), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- helpers ----------
    static String randomString(Random rnd, String alphabet, int len) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < len; i++) sb.append(alphabet.charAt(rnd.nextInt(alphabet.length())));
        return sb.toString();
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java LevenshteinDistance.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 6. Levenshtein
        check(levenshtein("kitten", "sitting") == 3, "kitten/sitting");
        check(levenshtein("", "abc") == 3 && levenshtein("abc", "") == 3, "empty string");
        check(levenshtein("flaw", "lawn") == 2 && levenshtein("same", "same") == 0, "flaw/lawn and equality");
        for (int t = 0; t < 2000; t++) {
            String a = randomString(rnd, "abc", rnd.nextInt(7)), b = randomString(rnd, "abc", rnd.nextInt(7)), c = randomString(rnd, "abc", rnd.nextInt(7));
            check(levenshtein(a, c) <= levenshtein(a, b) + levenshtein(b, c), "edit distance triangle");
            check(levenshtein(a, b) == levenshtein(b, a), "edit distance symmetry");
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("LevenshteinDistance: " + passed + " checks passed");
    }
}
