import java.math.BigInteger;
import java.util.*;

/**
 * Entry 2 of the principles catalog (Part 1): Extended Euclidean algorithm
 *
 * HOW IT WORKS
 *   Run Euclid's algorithm but also track how each remainder is built from a and b. That yields x and y with
 *   a*x + b*y = gcd(a, b) (Bezout). When gcd(a, m) = 1, x is the inverse of a modulo m, which is how RSA
 *   computes its private exponent.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ExtendedEuclid.java
 *   Expected: the output in expected-output.txt, ending "ExtendedEuclid: 1003 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ExtendedEuclid {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long modInverse(long a, long m) {
        long[] r = egcd(Math.floorMod(a, m), m);
        if (r[0] != 1) throw new ArithmeticException("no inverse: gcd = " + r[0]);
        return Math.floorMod(r[1], m);
    }

    // ---------- 3-5. Distances ----------
    static double dist2(double[] p, double[] q) {    // squared Euclidean
        double s = 0;
        for (int i = 0; i < p.length; i++) { double d = p[i] - q[i]; s += d * d; }
        return s;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 1 (euclidean-algorithm), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- 2. Extended Euclid ----------
    static long[] egcd(long a, long b) {             // returns {g, x, y} with a*x + b*y = g
        if (b == 0) return new long[]{a, 1, 0};
        long[] r = egcd(b, a % b);
        return new long[]{r[0], r[2], r[1] - (a / b) * r[2]};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ExtendedEuclid.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 2. Extended Euclid
        long[] r = egcd(240, 46);
        check(r[0] == 2 && 240 * r[1] + 46 * r[2] == 2, "Bezout identity");
        check(modInverse(17, 3120) == 2753, "RSA toy private exponent");
        boolean threw = false;
        try { modInverse(6, 9); } catch (ArithmeticException e) { threw = true; }
        check(threw, "no inverse when gcd != 1");
        BigInteger P = BigInteger.valueOf(1_000_000_007L);
        for (int i = 0; i < 1000; i++) {
            long a = rnd.nextLong(1, 1_000_000_007L);
            check(modInverse(a, 1_000_000_007L) == BigInteger.valueOf(a).modInverse(P).longValue(), "inverse vs BigInteger");
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("ExtendedEuclid: " + passed + " checks passed");
    }
}
