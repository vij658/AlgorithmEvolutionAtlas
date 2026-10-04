import java.util.*;

/**
 * Entry 44 of the principles catalog (Part 3): Universal Scalability Law
 *
 * HOW IT WORKS
 *   Gunther's Universal Scalability Law, C(N) = N / (1 + alpha(N - 1) + betaN(N - 1)), adds a coherence cost
 *   beta to Amdahl's contention alpha, so throughput peaks at N* = sqrt((1 - alpha)/beta) and then falls. The
 *   program fits alpha and beta from noisy measurements and shows how unreliable a peak predicted from a narrow
 *   range is.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java UniversalScalabilityLaw.java
 *   Expected: the output in expected-output.txt, ending "UniversalScalabilityLaw: 2364 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class UniversalScalabilityLaw {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double usl(double n, double alpha, double beta) { return n / (1 + alpha * (n - 1) + beta * n * (n - 1)); }

    static double uslPeak(double alpha, double beta) { return Math.sqrt((1 - alpha) / beta); }

    /** Least-squares fit of alpha and beta: with y = (n/C - 1)/(n - 1) the law becomes the straight line y = alpha + beta * n. */
    static double[] fitUsl(double[] n, double[] c) {
        int k = 0;
        double sx = 0, sy = 0, sxx = 0, sxy = 0;
        for (int i = 0; i < n.length; i++) {
            if (n[i] <= 1) continue;
            double y = (n[i] / c[i] - 1) / (n[i] - 1);
            k++; sx += n[i]; sy += y; sxx += n[i] * n[i]; sxy += n[i] * y;
        }
        double beta = (k * sxy - sx * sy) / (k * sxx - sx * sx);
        return new double[]{(sy - beta * sx) / k, beta};
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 43 (amdahl-gustafson-karp-flatt), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    static double amdahl(double p, double n) { return 1.0 / ((1 - p) + p / n); }       // p = parallelizable fraction of the one-worker run

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java UniversalScalabilityLaw.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 1000; t++) {
            double alpha = 0.001 + 0.5 * rnd.nextDouble(), n = 1 + 2000 * rnd.nextDouble();
            check(rel(usl(n, alpha, 0), amdahl(1 - alpha, n), 1e-12), "with beta = 0 the USL is Amdahl's law");
            check(usl(1, alpha, 0.01) == 1.0, "one worker gives capacity 1");
        }
        double alpha = 0.03, beta = 0.0005, peakN = uslPeak(alpha, beta);
        int argmax = 1;
        for (int n = 1; n <= 400; n++) if (usl(n, alpha, beta) > usl(argmax, alpha, beta)) argmax = n;
        check(argmax == (int) Math.floor(peakN) || argmax == (int) Math.ceil(peakN), "integer peak sits next to sqrt((1 - alpha) / beta)");
        for (int n = argmax; n < 400; n++) check(usl(n + 1, alpha, beta) < usl(n, alpha, beta), "past the peak, more workers means less throughput");
        double[] ns = {1, 2, 4, 8, 16, 32, 64, 128}, cs = new double[ns.length];
        for (int i = 0; i < ns.length; i++) cs[i] = usl(ns[i], alpha, beta);
        double[] exact = fitUsl(ns, cs);
        check(close(exact[0], alpha, 1e-9) && close(exact[1], beta, 1e-9), "noise-free fit recovers alpha and beta");
        double[] ns2 = {1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128}, cs2 = new double[ns2.length];
        for (int i = 0; i < ns2.length; i++) cs2[i] = usl(ns2[i], alpha, beta) * (1 + 0.02 * (2 * rnd.nextDouble() - 1));   // up to 2% noise
        double[] noisy = fitUsl(ns2, cs2);
        check(close(noisy[0], alpha, 0.01) && rel(noisy[1], beta, 0.3), "fit with 2% noise lands near alpha and beta, got " + Arrays.toString(noisy));
        System.out.printf("USL with alpha = %.2f, beta = %.4f: capacity %.2f at %d workers (peak at sqrt((1-a)/b) = %.1f), %.2f at 100, %.2f at 200%n",
                alpha, beta, usl(argmax, alpha, beta), argmax, peakN, usl(100, alpha, beta), usl(200, alpha, beta));
        System.out.printf("fit from 12 measurements with up to 2%% noise: alpha = %.4f, beta = %.5f; predicted peak %.1f workers%n", noisy[0], noisy[1], uslPeak(noisy[0], noisy[1]));

        // the range of the measurements matters: 20 noisy data sets fitted from 1-16 workers (all below the peak at 44) and 20 fitted from 1-128
        double[] lowGrid = {1, 2, 4, 6, 8, 10, 12, 16}, wideGrid = {1, 2, 4, 8, 12, 16, 24, 32, 48, 64, 96, 128};
        double lowMin = Double.MAX_VALUE, lowMax = 0, wideMin = Double.MAX_VALUE, wideMax = 0;
        int noPeak = 0;
        for (int run = 0; run < 20; run++) {
            for (int g = 0; g < 2; g++) {
                double[] grid = g == 0 ? lowGrid : wideGrid, c = new double[grid.length];
                for (int i = 0; i < grid.length; i++) c[i] = usl(grid[i], alpha, beta) * (1 + 0.02 * (2 * rnd.nextDouble() - 1));
                double[] fit = fitUsl(grid, c);
                if (fit[1] <= 0) { check(g == 0, "the wide fit always finds a positive beta"); noPeak++; continue; }      // a non-positive beta predicts no peak at all
                double peak = uslPeak(fit[0], fit[1]);
                if (g == 0) { lowMin = Math.min(lowMin, peak); lowMax = Math.max(lowMax, peak); }
                else { wideMin = Math.min(wideMin, peak); wideMax = Math.max(wideMax, peak); }
            }
        }
        check(wideMax / wideMin < 1.15 && (lowMax / lowMin > 1.5 || noPeak > 0), "fits that reach past the peak are tight; fits that stop below it are not, got " + lowMin + " to " + lowMax + ", " + noPeak + " without a peak");
        System.out.printf("predicted peak over 20 noisy fits (true peak %.1f): from measurements at 1-16 workers %.0f to %.0f, and %d of the 20 fits found no peak at all; from measurements at 1-128 workers %.1f to %.1f%n",
                peakN, lowMin, lowMax, noPeak, wideMin, wideMax);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2028));
        System.out.println("UniversalScalabilityLaw: " + passed + " checks passed");
    }
}
