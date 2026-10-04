import java.util.*;

/**
 * Entry 1 of the principles catalog (Part 1): Euclidean algorithm (GCD)
 *
 * HOW IT WORKS
 *   Replace the pair (a, b) by (b, a mod b) until the second number is 0; the first is then the greatest common
 *   divisor. The larger number at least halves every two steps, so the loop runs O(log min(a, b)) times;
 *   consecutive Fibonacci numbers are the worst case (Lame). The binary GCD (Stein) gets the same answer with
 *   shifts and subtraction only.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java EuclideanAlgorithm.java
 *   Expected: the output in expected-output.txt, ending "EuclideanAlgorithm: 20085 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class EuclideanAlgorithm {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---------- 1. Euclidean algorithm ----------
    static long gcd(long a, long b) {
        while (b != 0) { long t = a % b; a = b; b = t; }
        return Math.abs(a);
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long lcm(long a, long b) {
        if (a == 0 || b == 0) return 0;
        return Math.abs(a / gcd(a, b) * b);          // divide first to keep the intermediate small
    }

    static int gcdSteps(long a, long b) {
        int steps = 0;
        while (b != 0) { long t = a % b; a = b; b = t; steps++; }
        return steps;
    }

    static long binaryGcd(long a, long b) {          // a, b >= 0; shifts and subtraction only
        if (a == 0) return b;
        if (b == 0) return a;
        int shift = Long.numberOfTrailingZeros(a | b);
        a >>= Long.numberOfTrailingZeros(a);
        while (b != 0) {
            b >>= Long.numberOfTrailingZeros(b);
            if (a > b) { long t = a; a = b; b = t; }
            b -= a;
        }
        return a << shift;
    }

    // ---------- 2. Extended Euclid ----------
    static long[] egcd(long a, long b) {             // returns {g, x, y} with a*x + b*y = g
        if (b == 0) return new long[]{a, 1, 0};
        long[] r = egcd(b, a % b);
        return new long[]{r[0], r[2], r[1] - (a / b) * r[2]};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java EuclideanAlgorithm.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 1. Euclidean algorithm
        check(gcd(48, 18) == 6, "gcd(48,18)");
        check(gcd(0, 5) == 5 && gcd(5, 0) == 5 && gcd(0, 0) == 0, "gcd with zero");
        check(gcd(-12, 18) == 6, "gcd negative input");
        check(gcd(17, 13) == 1, "coprime");
        check(lcm(4, 6) == 12 && lcm(0, 3) == 0, "lcm");
        long[] fib = new long[93];
        fib[1] = fib[2] = 1;
        for (int i = 3; i <= 92; i++) fib[i] = fib[i - 1] + fib[i - 2];
        for (int n = 1; n <= 80; n++)
            check(gcdSteps(fib[n + 2], fib[n + 1]) == n, "Lame worst case n=" + n);
        for (int i = 0; i < 10_000; i++) {
            long a = rnd.nextLong(2, 1_000_000_000_000L), b = rnd.nextLong(1, a);
            check(gcdSteps(a, b) <= 5 * Long.toString(b).length(), "Lame: steps <= 5 * digits");
        }
        for (int i = 0; i < 10_000; i++) {
            long a = rnd.nextLong(0, 1L << 62), b = rnd.nextLong(0, 1L << 62);
            check(binaryGcd(a, b) == gcd(a, b), "binary gcd matches Euclid");
        }
        System.out.println("steps for gcd(F82, F81) = " + gcdSteps(fib[82], fib[81]));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("EuclideanAlgorithm: " + passed + " checks passed");
    }
}
