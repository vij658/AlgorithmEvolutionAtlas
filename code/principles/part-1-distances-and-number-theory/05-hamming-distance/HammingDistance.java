import java.util.*;

/**
 * Entry 5 of the principles catalog (Part 1): Hamming distance
 *
 * HOW IT WORKS
 *   Count the positions where two equal-length strings or bit patterns differ; for bits that is Long.bitCount(a
 *   ^ b). Two unrelated random codes disagree in about half their bits, which is why a fractional distance well
 *   below 0.5 means 'same source'.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HammingDistance.java
 *   Expected: the output in expected-output.txt, ending "HammingDistance: 403 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class HammingDistance {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int hamming(long a, long b) { return Long.bitCount(a ^ b); }

    static int hamming(String s, String t) {
        if (s.length() != t.length()) throw new IllegalArgumentException("lengths differ");
        int d = 0;
        for (int i = 0; i < s.length(); i++) if (s.charAt(i) != t.charAt(i)) d++;
        return d;
    }

    static int hamming(long[] a, long[] b) {
        int d = 0;
        for (int i = 0; i < a.length; i++) d += Long.bitCount(a[i] ^ b[i]);
        return d;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java HammingDistance.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 5. Hamming
        check(hamming("karolin", "kathrin") == 3, "hamming strings");
        check(hamming(0b1011101L, 0b1001001L) == 2, "hamming ints");
        double sum = 0;
        for (int t = 0; t < 200; t++) {
            long[] a = new long[32], b = new long[32];
            for (int i = 0; i < 32; i++) { a[i] = rnd.nextLong(); b[i] = rnd.nextLong(); }
            double frac = hamming(a, b) / 2048.0;
            check(frac > 0.4 && frac < 0.6, "unrelated 2048-bit codes sit near 0.5");
            check(hamming(a, a) == 0, "identical codes");
            sum += frac;
        }
        check(close(sum / 200, 0.5, 0.01), "mean fractional distance is about 0.5");
        System.out.printf("mean fractional Hamming distance of random 2048-bit codes = %.4f%n", sum / 200);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("HammingDistance: " + passed + " checks passed");
    }
}
