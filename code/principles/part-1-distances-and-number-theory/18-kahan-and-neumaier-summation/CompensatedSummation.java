import java.math.BigDecimal;
import java.util.*;
import java.util.stream.DoubleStream;

/**
 * Entry 18 of the principles catalog (Part 1): Summing floating-point numbers: Kahan and Neumaier
 *
 * HOW IT WORKS
 *   Floating-point addition rounds, and the rounding errors pile up over long sums. Kahan summation carries the
 *   lost low-order part in a compensation variable and adds it back; Neumaier's variant also handles a new term
 *   larger than the running sum.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CompensatedSummation.java
 *   Expected: the output in expected-output.txt, ending "CompensatedSummation: 5 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class CompensatedSummation {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double neumaier(double[] xs) {
        double sum = 0, c = 0;
        for (double x : xs) {
            double t = sum + x;
            if (Math.abs(sum) >= Math.abs(x)) c += (sum - t) + x;
            else c += (x - t) + sum;
            sum = t;
        }
        return sum + c;
    }

    static double naiveSum(double[] xs) {
        double s = 0;
        for (double x : xs) s += x;
        return s;
    }

    static BigDecimal exactSum(double[] xs) {
        BigDecimal s = BigDecimal.ZERO;
        for (double x : xs) s = s.add(new BigDecimal(x));
        return s;
    }

    static BigDecimal err(double got, BigDecimal exact) { return new BigDecimal(got).subtract(exact).abs(); }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 16 (shannon-entropy), entry 17 (luhn-checksum), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- floating point ----------
    static double kahan(double[] xs) {
        double sum = 0, c = 0;
        for (double x : xs) {
            double y = x - c;
            double t = sum + y;
            c = (t - sum) - y;
            sum = t;
        }
        return sum;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java CompensatedSummation.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // floating point
        double[] tenth = new double[10];
        Arrays.fill(tenth, 0.1);
        double[] nasty = {1.0, 1e100, 1.0, -1e100};
        check(0.1 + 0.2 != 0.3, "0.1 + 0.2 != 0.3");
        check(naiveSum(tenth) != 1.0, "naive 10 x 0.1 is not 1.0");
        check(kahan(tenth) == 1.0 && neumaier(tenth) == 1.0, "compensated 10 x 0.1 is 1.0");
        check(naiveSum(nasty) == 0.0 && kahan(nasty) == 0.0 && neumaier(nasty) == 2.0, "Neumaier survives the large-term case");
        System.out.println("10 x 0.1: naive = " + naiveSum(tenth) + ", Kahan = " + kahan(tenth) + ", DoubleStream.sum = " + DoubleStream.of(tenth).sum());
        System.out.println("{1, 1e100, 1, -1e100} true answer 2: naive = " + naiveSum(nasty) + ", Kahan = " + kahan(nasty)
                + ", Neumaier = " + neumaier(nasty) + ", DoubleStream.sum = " + DoubleStream.of(nasty).sum());
        double[] xs = new double[100_000];
        for (int i = 0; i < xs.length; i++) xs[i] = rnd.nextGaussian() * Math.pow(10, rnd.nextInt(11) - 5);
        BigDecimal exact = exactSum(xs);
        BigDecimal eNaive = err(naiveSum(xs), exact), eKahan = err(kahan(xs), exact), eNeu = err(neumaier(xs), exact), eStream = err(DoubleStream.of(xs).sum(), exact);
        check(eNeu.compareTo(eNaive) <= 0 && eKahan.compareTo(eNaive) <= 0, "compensation never loses to naive here");
        System.out.printf("100k mixed-magnitude values, abs error vs exact: naive %.3e, Kahan %.3e, Neumaier %.3e, DoubleStream.sum %.3e%n",
                eNaive.doubleValue(), eKahan.doubleValue(), eNeu.doubleValue(), eStream.doubleValue());
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("CompensatedSummation: " + passed + " checks passed");
    }
}
