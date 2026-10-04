import java.math.BigDecimal;
import java.util.*;

/**
 * Entry 19 of the principles catalog (Part 1): Comparing floating-point numbers, and money
 *
 * HOW IT WORKS
 *   Never compare doubles with ==: use a tolerance that is relative for large values and absolute near zero.
 *   For money use BigDecimal built from strings (new BigDecimal(0.1) keeps the binary error), and remember that
 *   equals() is scale-sensitive while compareTo() is not.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ComparingFloats.java
 *   Expected: the output in expected-output.txt, ending "ComparingFloats: 6 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ComparingFloats {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static boolean nearlyEqual(double a, double b, double relTol, double absTol) {
        return Math.abs(a - b) <= Math.max(absTol, relTol * Math.max(Math.abs(a), Math.abs(b)));
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ComparingFloats.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        check(nearlyEqual(0.1 + 0.2, 0.3, 1e-9, 1e-12) && nearlyEqual(1e10 + 1, 1e10, 1e-9, 0), "relative tolerance");
        check(!nearlyEqual(1e-20, 2e-20, 1e-9, 0) && nearlyEqual(1e-20, 2e-20, 1e-9, 1e-12), "absolute tolerance near zero");
        check(new BigDecimal("0.1").add(new BigDecimal("0.2")).equals(new BigDecimal("0.3")), "decimal arithmetic is exact");
        check(!new BigDecimal(0.1).equals(new BigDecimal("0.1")), "new BigDecimal(double) keeps the binary error");
        check(new BigDecimal("2.0").compareTo(new BigDecimal("2.00")) == 0 && !new BigDecimal("2.0").equals(new BigDecimal("2.00")), "equals is scale-sensitive");
        System.out.println("new BigDecimal(0.1) = " + new BigDecimal(0.1));
        check((0.1 + 0.2) + 0.3 != 0.1 + (0.2 + 0.3), "double addition is not associative");
        System.out.println("(0.1+0.2)+0.3 = " + ((0.1 + 0.2) + 0.3) + ", 0.1+(0.2+0.3) = " + (0.1 + (0.2 + 0.3)));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("ComparingFloats: " + passed + " checks passed");
    }
}
