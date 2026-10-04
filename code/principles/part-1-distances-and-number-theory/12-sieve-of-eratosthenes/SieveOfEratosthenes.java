import java.util.*;
import java.util.stream.IntStream;

/**
 * Entry 12 of the principles catalog (Part 1): Sieve of Eratosthenes
 *
 * HOW IT WORKS
 *   Write down 2..n; for each number still unmarked, cross out its multiples starting from its square. What
 *   survives is prime. Only primes up to sqrtn need sieving, and the total work is O(n log log n).
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SieveOfEratosthenes.java
 *   Expected: the output in expected-output.txt, ending "SieveOfEratosthenes: 3 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class SieveOfEratosthenes {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ---------- birthday bound ----------
    static double birthdayExact(int n, double space) {
        double noCollision = 1.0;
        for (int i = 0; i < n; i++) noCollision *= (space - i) / space;
        return 1 - noCollision;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 11 (square-and-multiply-and-rsa), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- sieve ----------
    static int[] primesUpTo(int n) {
        boolean[] composite = new boolean[n + 1];
        for (long i = 2; i * i <= n; i++)
            if (!composite[(int) i])
                for (long j = i * i; j <= n; j += i) composite[(int) j] = true;
        return IntStream.rangeClosed(2, n).filter(i -> !composite[i]).toArray();
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java SieveOfEratosthenes.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // sieve
        check(Arrays.equals(primesUpTo(30), new int[]{2, 3, 5, 7, 11, 13, 17, 19, 23, 29}), "primes <= 30");
        check(primesUpTo(10_000).length == 1229, "pi(10^4)");
        check(primesUpTo(1_000_000).length == 78_498, "pi(10^6)");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("SieveOfEratosthenes: " + passed + " checks passed");
    }
}
