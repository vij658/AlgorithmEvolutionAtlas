import java.util.*;

/**
 * Entry 3 of the principles catalog (Part 1): Euclidean distance (L2)
 *
 * HOW IT WORKS
 *   The straight-line distance: the square root of the sum of squared coordinate differences. Comparing squared
 *   distances avoids the square root when only the order matters. Math.hypot avoids the overflow that the naive
 *   formula hits with huge coordinates.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java EuclideanDistance.java
 *   Expected: the output in expected-output.txt, ending "EuclideanDistance: 206 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class EuclideanDistance {
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
    // Checks: what this program verifies. Run with: java EuclideanDistance.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 3. Euclidean distance
        check(euclid(new double[]{0, 0}, new double[]{3, 4}) == 5.0, "3-4-5");
        check(Math.hypot(3, 4) == 5.0, "hypot 3-4-5");
        double big = 1e200;
        check(Double.isInfinite(Math.sqrt(big * big + big * big)), "naive formula overflows");
        check(close(Math.hypot(big, big) / big, Math.sqrt(2), 1e-15), "hypot survives the same input");
        for (int t = 0; t < 200; t++) {
            double[][] pts = new double[50][5];
            for (double[] p : pts) for (int k = 0; k < 5; k++) p[k] = rnd.nextGaussian();
            double[] q = new double[5];
            for (int k = 0; k < 5; k++) q[k] = rnd.nextGaussian();
            int bestSq = 0, bestD = 0;
            for (int i = 1; i < pts.length; i++) {
                if (dist2(q, pts[i]) < dist2(q, pts[bestSq])) bestSq = i;
                if (euclid(q, pts[i]) < euclid(q, pts[bestD])) bestD = i;
            }
            check(bestSq == bestD, "squared distance preserves nearest-neighbour ranking");
        }
        double[] z0 = {0}, z1 = {1}, z2 = {2};
        check(dist2(z0, z2) > dist2(z0, z1) + dist2(z1, z2), "squared L2 breaks the triangle inequality");
        check(euclid(z0, z2) <= euclid(z0, z1) + euclid(z1, z2), "L2 obeys the triangle inequality");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("EuclideanDistance: " + passed + " checks passed");
    }
}
