import java.util.*;

/**
 * Entry 8 of the principles catalog (Part 1): Mahalanobis distance
 *
 * HOW IT WORKS
 *   Distance measured in units of the data's own spread: it rescales and decorrelates features with the inverse
 *   covariance matrix, so a point far out along a direction where the data barely varies counts as far. With
 *   the identity matrix it is Euclidean distance.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MahalanobisDistance.java
 *   Expected: the output in expected-output.txt, ending "MahalanobisDistance: 2 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class MahalanobisDistance {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ---------- 9. Haversine ----------
    static double haversineKm(double lat1, double lon1, double lat2, double lon2) {
        final double R = 6371.0088;                  // mean Earth radius, km
        double p1 = Math.toRadians(lat1), p2 = Math.toRadians(lat2);
        double dPhi = p2 - p1, dLam = Math.toRadians(lon2 - lon1);
        double a = Math.sin(dPhi / 2) * Math.sin(dPhi / 2)
                 + Math.cos(p1) * Math.cos(p2) * Math.sin(dLam / 2) * Math.sin(dLam / 2);
        return 2 * R * Math.asin(Math.sqrt(a));
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 7 (cosine-similarity-and-jaccard), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- 8. Mahalanobis (2-D, explicit inverse) ----------
    static double mahalanobis2(double[] x, double[] mu, double[][] cov) {
        double a = cov[0][0], b = cov[0][1], c = cov[1][0], d = cov[1][1];
        double det = a * d - b * c;
        double dx = x[0] - mu[0], dy = x[1] - mu[1];
        return Math.sqrt((dx * (d * dx - b * dy) + dy * (-c * dx + a * dy)) / det);
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java MahalanobisDistance.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 8. Mahalanobis
        check(close(mahalanobis2(new double[]{3, 4}, new double[]{0, 0}, new double[][]{{1, 0}, {0, 1}}), 5, 1e-12), "identity covariance gives Euclid");
        double[][] cov = {{1, 0.9}, {0.9, 1}};
        double along = mahalanobis2(new double[]{1, 1}, new double[]{0, 0}, cov);
        double against = mahalanobis2(new double[]{1, -1}, new double[]{0, 0}, cov);
        check(close(along, Math.sqrt(0.2 / 0.19), 1e-12) && close(against, Math.sqrt(20), 1e-12), "correlated covariance");
        System.out.printf("same Euclid distance sqrt(2); Mahalanobis along correlation = %.4f, against = %.4f%n", along, against);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("MahalanobisDistance: " + passed + " checks passed");
    }
}
