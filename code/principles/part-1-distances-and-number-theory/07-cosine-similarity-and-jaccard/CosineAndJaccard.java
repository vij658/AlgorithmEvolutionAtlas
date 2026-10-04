import java.util.*;

/**
 * Entry 7 of the principles catalog (Part 1): Cosine similarity and Jaccard index
 *
 * HOW IT WORKS
 *   Cosine similarity is the dot product of two vectors divided by the product of their lengths: it measures
 *   angle and ignores size. Jaccard similarity is |A n B| / |A u B| for sets. 1 - cosine is not a true distance
 *   (it breaks the triangle inequality); the angle is.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CosineAndJaccard.java
 *   Expected: the output in expected-output.txt, ending "CosineAndJaccard: 104 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class CosineAndJaccard {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static <T> double jaccard(Set<T> a, Set<T> b) {
        Set<T> inter = new HashSet<>(a); inter.retainAll(b);
        Set<T> union = new HashSet<>(a); union.addAll(b);
        return union.isEmpty() ? 1.0 : (double) inter.size() / union.size();
    }

    // ---------- 8. Mahalanobis (2-D, explicit inverse) ----------
    static double mahalanobis2(double[] x, double[] mu, double[][] cov) {
        double a = cov[0][0], b = cov[0][1], c = cov[1][0], d = cov[1][1];
        double det = a * d - b * c;
        double dx = x[0] - mu[0], dy = x[1] - mu[1];
        return Math.sqrt((dx * (d * dx - b * dy) + dy * (-c * dx + a * dy)) / det);
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
    // Helpers copied from entry 6 (levenshtein-edit-distance), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- 7. Cosine, Jaccard ----------
    static double cosine(double[] u, double[] v) {
        double dot = 0, nu = 0, nv = 0;
        for (int i = 0; i < u.length; i++) { dot += u[i] * v[i]; nu += u[i] * u[i]; nv += v[i] * v[i]; }
        return dot / (Math.sqrt(nu) * Math.sqrt(nv));
    }

    // ----------------------------------------------------------------------------------------------------
    // Shared helpers
    // ----------------------------------------------------------------------------------------------------
    static double[] unit(Random rnd, int n) {
        double[] v = new double[n];
        double s = 0;
        for (int i = 0; i < n; i++) { v[i] = rnd.nextGaussian(); s += v[i] * v[i]; }
        s = Math.sqrt(s);
        for (int i = 0; i < n; i++) v[i] /= s;
        return v;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java CosineAndJaccard.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 7. Cosine, Jaccard
        check(close(cosine(new double[]{1, 0}, new double[]{0, 1}), 0, 1e-12), "orthogonal");
        check(close(cosine(new double[]{1, 2, 3}, new double[]{2, 4, 6}), 1, 1e-12), "parallel");
        check(close(cosine(new double[]{1, 0}, new double[]{-1, 0}), -1, 1e-12), "opposite");
        for (int t = 0; t < 100; t++) {
            double[] u = unit(rnd, 8), v = unit(rnd, 8);
            check(close(dist2(u, v), 2 - 2 * cosine(u, v), 1e-12), "unit vectors: |u-v|^2 = 2 - 2cos");
        }
        check(jaccard(Set.of(1, 2, 3), Set.of(2, 3, 4)) == 0.5, "jaccard");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("CosineAndJaccard: " + passed + " checks passed");
    }
}
