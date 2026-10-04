import java.math.BigInteger;
import java.util.*;

/**
 * Entry 41 of the principles catalog (Part 2): Newton's method
 *
 * HOW IT WORKS
 *   To solve f(x) = 0, follow the tangent line: x <- x - f(x)/f'(x). Near a simple root the number of correct
 *   digits roughly doubles each step (quadratic convergence); for sqrta this is the ancient 'average x and a/x'
 *   rule.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java NewtonsMethod.java
 *   Expected: the output in expected-output.txt, ending "NewtonsMethod: 1600023 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class NewtonsMethod {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double newtonSqrt(double a) {                     // a > 0
        double x = a >= 1 ? a : 1;                           // start at or above sqrt(a) so iterates decrease
        for (int i = 0; i < 200; i++) {
            double next = 0.5 * (x + a / x);
            if (next >= x) break;                            // no further progress: converged to machine precision
            x = next;
        }
        return x;
    }

    static int newtonIterations(double a) {
        double x = a >= 1 ? a : 1;
        int it = 0;
        for (; it < 200; it++) {
            double next = 0.5 * (x + a / x);
            if (next >= x) break;
            x = next;
        }
        return it;
    }

    static long isqrt(long n) {                              // floor(sqrt(n)), exact for every non-negative long
        if (n < 2) return n;
        long x = (long) Math.sqrt((double) n);               // good first guess, can be off by one for large n
        while (x > n / x) x--;                               // x * x > n, written without overflow
        while (x + 1 <= n / (x + 1)) x++;                    // (x + 1)^2 <= n
        return x;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java NewtonsMethod.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        double x = 2;
        double root = Math.sqrt(2);
        StringBuilder sb = new StringBuilder();
        for (int i = 1; i <= 5; i++) {
            double before = x;
            x = 0.5 * (x + 2 / x);
            double err = Math.abs(x - root);
            if (i <= 4) {                                      // exact identity: x' - r = (x - r)^2 / (2x)
                double predicted = (before - root) * (before - root) / (2 * before);
                check(Math.abs(err - predicted) <= 1e-3 * predicted, "error squares each step (iteration " + i + ")");
            }
            sb.append(String.format("%d: %.3e  ", i, err));
        }
        System.out.println("Newton for sqrt(2) from x0 = 2, absolute error per iteration: " + sb);
        double maxRel = 0;
        for (int t = 0; t < 200_000; t++) {
            double a = Math.pow(10, rnd.nextDouble() * 20 - 10);
            maxRel = Math.max(maxRel, Math.abs(newtonSqrt(a) - Math.sqrt(a)) / Math.sqrt(a));
        }
        check(maxRel < 1e-15, "newtonSqrt matches Math.sqrt to a few ulps, worst " + maxRel);
        System.out.printf("newtonSqrt vs Math.sqrt over 200,000 values in [1e-10, 1e10]: worst relative error %.2e; iterations for a = 2: %d, for a = 1e10: %d%n",
                maxRel, newtonIterations(2), newtonIterations(1e10));
        int naiveWrong = 0, naiveTooBig = 0, tested = 0;
        for (int t = 0; t < 1_000_000; t++) {
            long n = rnd.nextLong(0, Long.MAX_VALUE);
            check(isqrt(n) == BigInteger.valueOf(n).sqrt().longValue(), "isqrt vs BigInteger.sqrt");
        }
        for (int t = 0; t < 200_000; t++) {
            long k = 1 + rnd.nextLong(3_037_000_499L);
            for (long n : new long[]{k * k - 1, k * k, k * k + 1}) {
                if (n < 0) continue;
                long expect = BigInteger.valueOf(n).sqrt().longValue();
                check(isqrt(n) == expect, "isqrt near perfect squares");
                tested++;
                long naive = (long) Math.sqrt((double) n);
                if (naive != expect) naiveWrong++;
                if (naive > expect) naiveTooBig++;
            }
        }
        for (long n : new long[]{0, 1, 2, 3, 4, Long.MAX_VALUE, Long.MAX_VALUE - 1, 3_037_000_499L * 3_037_000_499L, 3_037_000_499L * 3_037_000_499L - 1})
            check(isqrt(n) == BigInteger.valueOf(n).sqrt().longValue(), "isqrt edge case " + n);
        check(naiveWrong > 0, "(long) Math.sqrt is wrong for some large inputs");
        System.out.println("isqrt exact on 1,000,000 random longs and " + tested + " near-square values; plain (long) Math.sqrt(n) was wrong for " + naiveWrong + " of those near-square values, too big in " + naiveTooBig + " of them");
        double v = 1;
        for (int i = 0; i < 8; i++) {                          // Newton on f(x) = cbrt(x): x - f/f' = -2x
            double fx = Math.cbrt(v), dfx = 1.0 / (3 * Math.cbrt(v) * Math.cbrt(v));
            double next = v - fx / dfx;
            check(close(next, -2 * v, 1e-9 * Math.abs(v)), "Newton on cbrt doubles and flips sign each step");
            v = next;
        }
        System.out.println("Newton on cbrt(x) from x0 = 1 diverges: after 8 steps x = " + v);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(41));
        System.out.println("NewtonsMethod: " + passed + " checks passed");
    }
}
