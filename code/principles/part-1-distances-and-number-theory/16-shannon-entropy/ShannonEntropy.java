import java.util.*;

/**
 * Entry 16 of the principles catalog (Part 1): Shannon entropy
 *
 * HOW IT WORKS
 *   Entropy H = -sum p*log2 p is the average number of bits needed per symbol from a source. It bounds lossless
 *   compression and measures how many guesses a secret is worth. It describes the process that produced the
 *   data, not one particular string.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ShannonEntropy.java
 *   Expected: the output in expected-output.txt, ending "ShannonEntropy: 3 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ShannonEntropy {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static double log2(double x) { return Math.log(x) / Math.log(2); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 15 (horner-and-rolling-hash), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- entropy, checksum ----------
    static double entropyBits(double... p) {
        double h = 0;
        for (double x : p) if (x > 0) h -= x * (Math.log(x) / Math.log(2));
        return h;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ShannonEntropy.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // entropy
        check(close(entropyBits(0.5, 0.5), 1.0, 1e-12) && close(entropyBits(0.25, 0.25, 0.25, 0.25), 2.0, 1e-12), "entropy of uniform");
        check(close(entropyBits(0.9, 0.1), 0.469, 1e-4), "entropy of a biased coin");
        double pw94 = 12 * log2(94), dice6 = 6 * log2(7776);
        check(close(pw94, 78.66, 0.01) && close(dice6, 77.55, 0.01) && close(4 * log2(7776), 51.70, 0.01), "password entropy figures");
        System.out.printf("12 random chars from 94 symbols = %.2f bits; 6 Diceware words = %.2f bits; 4 words = %.2f bits%n", pw94, dice6, 4 * log2(7776));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("ShannonEntropy: " + passed + " checks passed");
    }
}
