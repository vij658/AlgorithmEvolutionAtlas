import java.util.*;

/**
 * Entry 49 of the principles catalog (Part 3): Tail latency and fan-out
 *
 * HOW IT WORKS
 *   When one request fans out to many servers, it waits for the slowest. At fan-out 100, most user requests hit
 *   at least one server's p99. Hedged requests (send a backup after a delay) cut the tail for a few percent of
 *   extra load.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java TailLatency.java
 *   Expected: the output in expected-output.txt, ending "TailLatency: 12 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class TailLatency {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    static double gaussian(Random rnd) {                       // Box-Muller from nextDouble, so results do not depend on the JDK's nextGaussian
        double u1 = 1 - rnd.nextDouble(), u2 = rnd.nextDouble();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    static double nearestRank(double[] sorted, double p) { return sorted[(int) Math.ceil(p * sorted.length) - 1]; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double slowProbability(double p, int fanout) { return 1 - Math.pow(1 - p, fanout); }

    static double lognormalMs(Random rnd) { return 10 * Math.exp(gaussian(rnd)); }       // median 10 ms, sigma 1

    /** Latency of a request that is hedged: if the first answer has not come after `delay`, a second server is asked; the first answer to arrive wins. */
    static double hedgedLatency(double first, double delay, Random rnd) {
        return first <= delay ? first : Math.min(first, delay + lognormalMs(rnd));
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java TailLatency.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        final double z99 = 2.3263478740408408, z95 = 1.6448536269514722, z999 = 3.090232306167813;
        double p99 = 10 * Math.exp(z99), p95 = 10 * Math.exp(z95);
        Random rnd = new Random(49);
        int trials = 200_000;
        StringBuilder sb = new StringBuilder();
        for (int fanout : new int[]{1, 10, 100}) {
            int slow = 0;
            for (int t = 0; t < trials; t++) {
                double worst = 0;
                for (int i = 0; i < fanout; i++) worst = Math.max(worst, lognormalMs(rnd));
                if (worst > p99) slow++;
            }
            double measured = slow / (double) trials, formula = slowProbability(0.01, fanout);
            check(close(measured, formula, 0.004), "fan-out " + fanout + ": share of requests slower than the single-server p99 matches 1 - 0.99^n, got " + measured);
            sb.append(String.format("fan-out %d: %.1f%% (formula %.1f%%); ", fanout, 100 * measured, 100 * formula));
        }
        System.out.printf("share of user requests slower than one server's p99 (%.0f ms) when they wait for all of n servers: %s%n", p99, sb);
        double needed = Math.pow(0.99, 1.0 / 100);
        check(close(needed, 0.9998995, 1e-6), "to keep 99% of fan-out-100 requests fast, each server must be fast 99.99% of the time");
        System.out.printf("so with fan-out 100, a user-level p99 needs each server's %.4f%% quantile; the median of the slowest of 100 sits at the single-server %.2f%% quantile%n", 100 * needed, 100 * Math.pow(0.5, 1.0 / 100));
        int n = 1_000_000;
        double[] plain = new double[n], hedged = new double[n];
        int extra = 0;
        for (int i = 0; i < n; i++) {
            double first = lognormalMs(rnd);
            plain[i] = first;
            if (first > p95) extra++;                        // a second request was sent
            hedged[i] = hedgedLatency(first, p95, rnd);
        }
        Arrays.sort(plain);
        Arrays.sort(hedged);
        double extraShare = extra / (double) n;
        check(close(extraShare, 0.05, 0.002), "a hedge after the p95 adds about 5% load");
        double plain99 = nearestRank(plain, 0.99), hedged99 = nearestRank(hedged, 0.99), plain999 = nearestRank(plain, 0.999), hedged999 = nearestRank(hedged, 0.999);
        check(rel(plain99, p99, 0.03) && rel(plain999, 10 * Math.exp(z999), 0.05), "empirical single-server quantiles match the lognormal formula");
        check(hedged99 < plain99 && hedged999 < 0.6 * plain999, "hedging cuts the tail");
        System.out.printf("hedged requests (second request after the p95 = %.0f ms, first answer wins) on 1,000,000 requests: extra load %.1f%%, p99 %.0f ms -> %.0f ms, p99.9 %.0f ms -> %.0f ms%n",
                p95, 100 * extraShare, plain99, hedged99, plain999, hedged999);
        double[] zs = {0, 1.2815515655446004, z95, z99};     // quantiles of the standard normal for p50, p90, p95 and p99
        String[] labels = {"p50", "p90", "p95", "p99"};
        double[] tail999 = new double[zs.length];
        StringBuilder table = new StringBuilder();
        for (int j = 0; j < zs.length; j++) {
            double delay = 10 * Math.exp(zs[j]);
            double[] h = new double[n];
            int sent = 0;
            for (int i = 0; i < n; i++) {
                double first = lognormalMs(rnd);
                if (first > delay) sent++;
                h[i] = hedgedLatency(first, delay, rnd);
            }
            Arrays.sort(h);
            tail999[j] = nearestRank(h, 0.999);
            double q = new double[]{0.5, 0.9, 0.95, 0.99}[j];
            check(close(sent / (double) n, 1 - q, 0.003), "waiting for the " + labels[j] + " before hedging adds " + (1 - q) + " of extra requests");
            table.append(String.format("hedge after %s (%.0f ms): +%.1f%% load, p99 %.0f ms, p99.9 %.0f ms; ", labels[j], delay, 100.0 * sent / n, nearestRank(h, 0.99), tail999[j]));
        }
        check(tail999[0] < tail999[1] && tail999[1] < tail999[2] && tail999[2] < tail999[3] && tail999[3] < plain999, "the earlier the hedge, the lower the extreme tail");
        System.out.println("hedging delay against extra load: " + table);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("TailLatency: " + passed + " checks passed");
    }
}
