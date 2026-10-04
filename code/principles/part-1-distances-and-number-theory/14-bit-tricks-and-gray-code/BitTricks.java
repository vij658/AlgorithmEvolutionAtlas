import java.util.*;

/**
 * Entry 14 of the principles catalog (Part 1): Bit tricks and Gray code
 *
 * HOW IT WORKS
 *   Classic two's-complement tricks: x & (x - 1) clears the lowest set bit, x & -x isolates it, popcount counts
 *   bits, and the Gray code g = x ^ (x >>> 1) changes exactly one bit between consecutive numbers.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BitTricks.java
 *   Expected: the output in expected-output.txt, ending "BitTricks: 1149586 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BitTricks {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int popcountKernighan(long n) {
        int c = 0;
        while (n != 0) { n &= n - 1; c++; }                // each pass clears the lowest set bit
        return c;
    }

    static int gray(int n) { return n ^ (n >>> 1); }

    static int grayInverse(int g) {
        int n = 0;
        for (; g != 0; g >>>= 1) n ^= g;
        return n;
    }

    // ---------- Horner and rolling hash ----------
    static double horner(double[] coeffs, double x) {      // highest degree first
        double acc = 0;
        for (double c : coeffs) acc = acc * x + c;
        return acc;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 13 (birthday-bound), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- bit tricks ----------
    static boolean isPowerOfTwo(long n) { return n > 0 && (n & (n - 1)) == 0; }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BitTricks.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // bit tricks
        check(isPowerOfTwo(1) && isPowerOfTwo(1024) && !isPowerOfTwo(0) && !isPowerOfTwo(6) && !isPowerOfTwo(-8), "power of two");
        for (int i = 0; i < 1000; i++) { long x = rnd.nextLong(); check(popcountKernighan(x) == Long.bitCount(x), "Kernighan popcount"); }
        check(Long.lowestOneBit(0b101000L) == 0b1000L && (0b101000L & -0b101000L) == 0b1000L, "lowest set bit");
        int[] expectGray = {0, 1, 3, 2, 6, 7, 5, 4};
        for (int i = 0; i < 8; i++) check(gray(i) == expectGray[i], "gray(" + i + ")");
        for (int i = 0; i < (1 << 20) - 1; i++) check(Integer.bitCount(gray(i) ^ gray(i + 1)) == 1, "gray neighbours differ in one bit");
        check(Integer.bitCount(gray(1023) ^ gray(0)) == 1, "gray code is cyclic");
        for (int i = 0; i < 100_000; i++) check(grayInverse(gray(i)) == i, "gray inverse");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("BitTricks: " + passed + " checks passed");
    }
}
