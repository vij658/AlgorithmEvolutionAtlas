import java.util.*;

/**
 * Entry 15 of the principles catalog (Part 1): Horner's method and rolling hashes
 *
 * HOW IT WORKS
 *   Horner's rule evaluates a polynomial with one multiply and one add per coefficient. Treating a string as a
 *   polynomial gives String.hashCode and the rolling hash: slide a window by subtracting the outgoing
 *   character's term and adding the new one, in O(1). A hash match only means 'check here', so Rabin-Karp
 *   verifies every match.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HornerAndRollingHash.java
 *   Expected: the output in expected-output.txt, ending "HornerAndRollingHash: 5002 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class HornerAndRollingHash {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int rabinKarp(String text, String pat) {
        int n = text.length(), m = pat.length();
        if (m == 0) return 0;
        if (m > n) return -1;
        final long MOD = 1_000_000_007L, B = 256;
        long hp = 0, ht = 0, pow = 1;                      // pow = B^(m-1) mod MOD
        for (int i = 0; i < m; i++) {
            hp = (hp * B + pat.charAt(i)) % MOD;
            ht = (ht * B + text.charAt(i)) % MOD;
            if (i > 0) pow = pow * B % MOD;
        }
        for (int i = 0; ; i++) {
            if (hp == ht && text.startsWith(pat, i)) return i;   // verify: equal hashes can still collide
            if (i + m >= n) return -1;
            ht = ((ht - text.charAt(i) * pow % MOD + MOD) * B + text.charAt(i + m)) % MOD;
        }
    }

    // ---------- entropy, checksum ----------
    static double entropyBits(double... p) {
        double h = 0;
        for (double x : p) if (x > 0) h -= x * (Math.log(x) / Math.log(2));
        return h;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 14 (bit-tricks-and-gray-code), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- Horner and rolling hash ----------
    static double horner(double[] coeffs, double x) {      // highest degree first
        double acc = 0;
        for (double c : coeffs) acc = acc * x + c;
        return acc;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java HornerAndRollingHash.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // Horner, String.hashCode, Rabin-Karp
        check(horner(new double[]{2, 3, 4}, 5) == 69, "horner");
        int h = 0;
        for (char ch : "hello".toCharArray()) h = 31 * h + ch;
        check(h == "hello".hashCode(), "String.hashCode is Horner with base 31");
        for (int t = 0; t < 5000; t++) {
            StringBuilder sb = new StringBuilder(), pb = new StringBuilder();
            int tl = rnd.nextInt(60), pl = rnd.nextInt(6);
            for (int i = 0; i < tl; i++) sb.append((char) ('a' + rnd.nextInt(2)));
            for (int i = 0; i < pl; i++) pb.append((char) ('a' + rnd.nextInt(2)));
            check(rabinKarp(sb.toString(), pb.toString()) == sb.toString().indexOf(pb.toString()), "Rabin-Karp vs indexOf");
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("HornerAndRollingHash: " + passed + " checks passed");
    }
}
