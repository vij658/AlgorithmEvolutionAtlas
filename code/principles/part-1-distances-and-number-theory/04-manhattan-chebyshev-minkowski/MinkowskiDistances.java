import java.util.*;

/**
 * Entry 4 of the principles catalog (Part 1): Manhattan (L1), Chebyshev (Linfinity) and Minkowski (Lp)
 *
 * HOW IT WORKS
 *   Manhattan (L1) adds absolute coordinate differences, Chebyshev (Linfinity) takes the largest one, and
 *   Minkowski (Lp) generalises both: p = 1 is Manhattan, p = 2 is Euclidean, and p -> infinity approaches
 *   Chebyshev. The right one is the one that matches how things move.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MinkowskiDistances.java
 *   Expected: the output in expected-output.txt, ending "MinkowskiDistances: 5003 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class MinkowskiDistances {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double euclid(double[] p, double[] q) { return Math.sqrt(dist2(p, q)); }

    static double manhattan(double[] p, double[] q) {
        double s = 0;
        for (int i = 0; i < p.length; i++) s += Math.abs(p[i] - q[i]);
        return s;
    }

    static double chebyshev(double[] p, double[] q) {
        double m = 0;
        for (int i = 0; i < p.length; i++) m = Math.max(m, Math.abs(p[i] - q[i]));
        return m;
    }

    static double minkowski(double[] p, double[] q, double r) {
        double s = 0;
        for (int i = 0; i < p.length; i++) s += Math.pow(Math.abs(p[i] - q[i]), r);
        return Math.pow(s, 1.0 / r);
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 2 (extended-euclidean-algorithm), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- 3-5. Distances ----------
    static double dist2(double[] p, double[] q) {    // squared Euclidean
        double s = 0;
        for (int i = 0; i < p.length; i++) { double d = p[i] - q[i]; s += d * d; }
        return s;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java MinkowskiDistances.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 4. L1, L-infinity, Minkowski
        for (int t = 0; t < 1000; t++) {
            double[] a = new double[4], b = new double[4], c = new double[4];
            for (int k = 0; k < 4; k++) { a[k] = rnd.nextGaussian(); b[k] = rnd.nextGaussian(); c[k] = rnd.nextGaussian(); }
            check(manhattan(a, c) <= manhattan(a, b) + manhattan(b, c) + 1e-9, "L1 triangle");
            check(euclid(a, c) <= euclid(a, b) + euclid(b, c) + 1e-9, "L2 triangle");
            check(chebyshev(a, c) <= chebyshev(a, b) + chebyshev(b, c) + 1e-9, "Linf triangle");
            check(euclid(a, b) == euclid(b, a), "symmetry");
            check(chebyshev(a, b) <= euclid(a, b) + 1e-12 && euclid(a, b) <= manhattan(a, b) + 1e-12, "Linf <= L2 <= L1");
        }
        double[] o = {0, 0}, f = {3, 4};
        check(manhattan(o, f) == 7 && chebyshev(o, f) == 4, "L1 and Linf of (3,4)");
        check(close(minkowski(o, f, 1), 7, 1e-12) && close(minkowski(o, f, 2), 5, 1e-12), "minkowski p=1 and p=2");
        check(close(minkowski(o, f, 50), 4, 1e-6), "minkowski p=50 is close to Chebyshev");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("MinkowskiDistances: " + passed + " checks passed");
    }
}
