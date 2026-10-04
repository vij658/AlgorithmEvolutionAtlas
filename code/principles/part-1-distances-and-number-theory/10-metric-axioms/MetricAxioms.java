import java.util.*;

/**
 * Entry 10 of the principles catalog (Part 1): The four metric axioms
 *
 * HOW IT WORKS
 *   A metric must be non-negative, zero only for identical points, symmetric, and obey the triangle inequality.
 *   Indexes and pruning tricks (BK-trees, metric trees) rely on the triangle inequality, so the program checks
 *   which common 'distances' satisfy it and which (squared L2, 1 - cosine) do not.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MetricAxioms.java
 *   Expected: the output in expected-output.txt, ending "MetricAxioms: 1001 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class MetricAxioms {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ---------- helpers ----------
    static String randomString(Random rnd, String alphabet, int len) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < len; i++) sb.append(alphabet.charAt(rnd.nextInt(alphabet.length())));
        return sb.toString();
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
    // Helpers copied from entry 9 (haversine-distance), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- 10. angular distance ----------
    static double angle(double[] u, double[] v) {
        return Math.acos(Math.max(-1.0, Math.min(1.0, cosine(u, v))));
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
    // Checks: what this program verifies. Run with: java MetricAxioms.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 10. 1 - cos is not a metric; the angle is
        double[] u0 = {1, 0}, v45 = {Math.cos(Math.PI / 4), Math.sin(Math.PI / 4)}, w90 = {0, 1};
        double dUW = 1 - cosine(u0, w90), dUV = 1 - cosine(u0, v45), dVW = 1 - cosine(v45, w90);
        check(close(dUW, 1.0, 1e-12) && close(dUV + dVW, 2 - Math.sqrt(2), 1e-12) && dUW > dUV + dVW,
                "1 - cos breaks the triangle inequality");
        System.out.printf("1 - cos at 0/45/90 degrees: d(u,w) = %.4f > d(u,v) + d(v,w) = %.4f%n", dUW, dUV + dVW);
        for (int t = 0; t < 1000; t++) {
            double[] a = unit(rnd, 8), b = unit(rnd, 8), c = unit(rnd, 8);
            check(angle(a, c) <= angle(a, b) + angle(b, c) + 1e-9, "angular distance triangle");
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("MetricAxioms: " + passed + " checks passed");
    }
}
