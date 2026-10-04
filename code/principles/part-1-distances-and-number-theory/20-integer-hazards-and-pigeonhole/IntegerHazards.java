import java.util.*;

/**
 * Entry 20 of the principles catalog (Part 1): Integer hazards and the pigeonhole principle
 *
 * HOW IT WORKS
 *   Fixed-width integers wrap around: Math.abs(Integer.MIN_VALUE) is negative, (lo + hi) / 2 can overflow, and
 *   % keeps the sign of the dividend. The pigeonhole principle sets hard limits: no lossless compressor can
 *   shrink every input, and any hash must collide.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java IntegerHazards.java
 *   Expected: the output in expected-output.txt, ending "IntegerHazards: 5 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class IntegerHazards {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java IntegerHazards.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // integer hazards
        check(Math.abs(Integer.MIN_VALUE) == Integer.MIN_VALUE, "abs(MIN_VALUE) stays negative");
        check(-7 % 3 == -1 && Math.floorMod(-7, 3) == 2, "% keeps the sign of the dividend");
        boolean overflow = false;
        try { Math.addExact(Integer.MAX_VALUE, 1); } catch (ArithmeticException ex) { overflow = true; }
        check(overflow, "addExact throws on overflow");
        int lo = 1_500_000_000, hi = 2_000_000_000;
        check((lo + hi) / 2 < 0 && ((lo + hi) >>> 1) == 1_750_000_000, "midpoint overflow");

        // pigeonhole
        long shorter = 0;
        for (int k = 0; k < 10; k++) shorter += 1L << k;
        check(shorter == 1023 && (1L << 10) == 1024, "1024 inputs, only 1023 shorter outputs");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("IntegerHazards: " + passed + " checks passed");
    }
}
