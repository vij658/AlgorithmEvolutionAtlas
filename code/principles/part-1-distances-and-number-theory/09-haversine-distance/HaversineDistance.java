import java.util.*;

/**
 * Entry 9 of the principles catalog (Part 1): Haversine (great-circle) distance
 *
 * HOW IT WORKS
 *   Great-circle distance on a sphere from latitudes and longitudes, using the haversine formula, which stays
 *   numerically stable for small distances. Treating the Earth as a sphere costs about 0.5% error compared with
 *   the ellipsoid.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HaversineDistance.java
 *   Expected: the output in expected-output.txt, ending "HaversineDistance: 4 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class HaversineDistance {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ---------- 10. angular distance ----------
    static double angle(double[] u, double[] v) {
        return Math.acos(Math.max(-1.0, Math.min(1.0, cosine(u, v))));
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
    // Helpers copied from entry 8 (mahalanobis-distance), used here for comparison or cross-checking
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
    // Checks: what this program verifies. Run with: java HaversineDistance.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 9. Haversine
        double nycLa = haversineKm(40.7128, -74.0060, 34.0522, -118.2437);
        check(nycLa > 3900 && nycLa < 3970, "NYC-LA about 3,936 km");
        check(haversineKm(10, 20, 10, 20) == 0, "same point");
        check(close(haversineKm(0, 0, 0, 180), Math.PI * 6371.0088, 1e-3), "antipodal = pi * R");
        double eq = haversineKm(0, 0, 0, 1), at60 = haversineKm(60, 0, 60, 1);
        check(close(at60 / eq, 0.5, 0.001), "one degree of longitude at 60N is half as long as at the equator");
        System.out.printf("NYC-LA = %.1f km; 1 deg lon at equator = %.2f km, at 60N = %.2f km%n", nycLa, eq, at60);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("HaversineDistance: " + passed + " checks passed");
    }
}
