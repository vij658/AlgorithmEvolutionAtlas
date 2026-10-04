import java.util.*;
import java.util.function.DoubleUnaryOperator;

/**
 * Entry 42 of the principles catalog (Part 2): Monte Carlo and the 1/sqrtn law
 *
 * HOW IT WORKS
 *   Estimate a quantity by random sampling and averaging. The error shrinks like 1/sqrtn whatever the
 *   dimension, so each extra decimal digit costs 100 times more samples; the program measures that law on pi
 *   and on an integral.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MonteCarlo.java
 *   Expected: the output in expected-output.txt, ending "MonteCarlo: 5 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class MonteCarlo {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double estimatePi(long samples, Random rnd) {
        long inside = 0;
        for (long i = 0; i < samples; i++) {
            double x = rnd.nextDouble(), y = rnd.nextDouble();
            if (x * x + y * y <= 1.0) inside++;
        }
        return 4.0 * inside / samples;
    }

    static double integrate(DoubleUnaryOperator f, int n, boolean stratified, Random rnd) {
        double sum = 0;
        for (int i = 0; i < n; i++) {
            double u = stratified ? (i + rnd.nextDouble()) / n : rnd.nextDouble();   // one random point per stratum
            sum += f.applyAsDouble(u);
        }
        return sum / n;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java MonteCarlo.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        long[] sizes = {100, 10_000, 1_000_000};
        int[] trials = {300, 300, 100};
        for (int s = 0; s < sizes.length; s++) {
            double sq = 0;
            for (int t = 0; t < trials[s]; t++) { double e = estimatePi(sizes[s], rnd) - Math.PI; sq += e * e; }
            double rms = Math.sqrt(sq / trials[s]);
            double predicted = Math.sqrt(Math.PI * (4 - Math.PI) / sizes[s]);
            check(rms / predicted > 0.75 && rms / predicted < 1.25, "RMS error follows sqrt(pi(4-pi)/n) at n = " + sizes[s]);
            System.out.printf("pi estimate with n = %,d samples: measured RMS error %.5f, predicted %.5f (%d trials)%n", sizes[s], rms, predicted, trials[s]);
        }
        DoubleUnaryOperator f = x -> 4 / (1 + x * x);
        int n = 10_000, trialsInt = 200;
        double sqPlain = 0, sqStrat = 0;
        for (int t = 0; t < trialsInt; t++) {
            double e1 = integrate(f, n, false, rnd) - Math.PI, e2 = integrate(f, n, true, rnd) - Math.PI;
            sqPlain += e1 * e1; sqStrat += e2 * e2;
        }
        double rmsPlain = Math.sqrt(sqPlain / trialsInt), rmsStrat = Math.sqrt(sqStrat / trialsInt);
        double predictedPlain = Math.sqrt(2 * Math.PI + 4 - Math.PI * Math.PI) / Math.sqrt(n);
        check(rmsPlain / predictedPlain > 0.8 && rmsPlain / predictedPlain < 1.2, "plain Monte Carlo error matches sigma / sqrt(n)");
        check(rmsStrat < rmsPlain / 20, "stratified sampling is at least 20x more accurate with the same n");
        System.out.printf("integral of 4/(1+x^2) on [0,1] with n = 10,000: plain Monte Carlo RMS error %.2e (sigma/sqrt(n) = %.2e), stratified %.2e%n",
                rmsPlain, predictedPlain, rmsStrat);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(42));
        System.out.println("MonteCarlo: " + passed + " checks passed");
    }
}
