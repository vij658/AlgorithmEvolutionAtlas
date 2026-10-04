import java.util.*;

/**
 * Entry 13 of the principles catalog (Part 1): The birthday bound (collisions in hashes and IDs)
 *
 * HOW IT WORKS
 *   With N equally likely values, the chance that k random picks are all different falls like e^(-k^2/2N), so
 *   collisions become likely after about sqrtN picks (1.18*sqrtN for 50%). This sizes hash lengths and random
 *   IDs.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BirthdayBound.java
 *   Expected: the output in expected-output.txt, ending "BirthdayBound: 6 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BirthdayBound {
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
    static double birthdayApprox(double n, double space) {
        return 1 - Math.exp(-n * (n - 1) / (2 * space));
    }

    // ---------- bit tricks ----------
    static boolean isPowerOfTwo(long n) { return n > 0 && (n & (n - 1)) == 0; }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 12 (sieve-of-eratosthenes), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- birthday bound ----------
    static double birthdayExact(int n, double space) {
        double noCollision = 1.0;
        for (int i = 0; i < n; i++) noCollision *= (space - i) / space;
        return 1 - noCollision;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BirthdayBound.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // birthday bound
        double p23 = birthdayExact(23, 365), p22 = birthdayExact(22, 365);
        check(close(p23, 0.5073, 5e-4) && p22 < 0.5 && p23 > 0.5, "23 people");
        check(close(1.1774 * Math.sqrt(365), 22.49, 0.01), "1.1774 sqrt(N)");
        int n32 = (int) Math.round(1.1774 * Math.pow(2, 16));
        check(close(birthdayExact(n32, Math.pow(2, 32)), 0.5, 0.002), "32-bit space");
        double n64 = 1.1774 * Math.pow(2, 32);
        check(close(birthdayApprox(n64, Math.pow(2, 64)), 0.5, 0.002), "64-bit space");
        System.out.printf("birthday: P(23/365) = %.4f; 32-bit hash 50%% at n = %d; 64-bit hash 50%% at n = %.3e%n", p23, n32, n64);
        double uuidSpace = Math.pow(2, 122);
        double nUuid = Math.sqrt(2 * uuidSpace * 1e-9);
        check(close(-Math.expm1(-nUuid * (nUuid - 1) / (2 * uuidSpace)), 1e-9, 1e-12), "UUIDv4: n for p = 1e-9");
        double spaceNeeded = 1e9 * 1e9 / (2 * 1e-9);
        check(close(log2(spaceNeeded), 88.7, 0.05), "space for 1e9 items at p = 1e-9 is 2^88.7");
        System.out.printf("UUIDv4 (122 random bits): p = 1e-9 at n = %.4e; 1e9 items at p = 1e-9 needs 2^%.1f%n", nUuid, log2(spaceNeeded));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("BirthdayBound: " + passed + " checks passed");
    }
}
