import java.util.*;

/**
 * Entry 50 of the principles catalog (Part 3): Percentiles, histograms and coordinated omission
 *
 * HOW IT WORKS
 *   Percentiles cannot be averaged across servers; merge histograms instead. A log-bucketed histogram keeps
 *   percentiles within a chosen relative error in little memory. A closed-loop load generator that waits for
 *   each response hides stalls (coordinated omission).
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Percentiles.java
 *   Expected: the output in expected-output.txt, ending "Percentiles: 9 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Percentiles {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static double gaussian(Random rnd) {                       // Box-Muller from nextDouble, so results do not depend on the JDK's nextGaussian
        double u1 = 1 - rnd.nextDouble(), u2 = rnd.nextDouble();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    static double nearestRank(double[] sorted, double p) { return sorted[(int) Math.ceil(p * sorted.length) - 1]; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** Geometric buckets of ratio (1 + eps)^2; reporting a bucket's middle keeps every value within eps (relative) of the truth. */
    static final class LogHistogram {
        final double eps, gamma, lnGamma, min;
        final long[] counts;
        long total;
        LogHistogram(double min, double max, double eps) {
            this.eps = eps; this.min = min;
            gamma = (1 + eps) * (1 + eps);
            lnGamma = Math.log(gamma);
            counts = new long[(int) Math.ceil(Math.log(max / min) / lnGamma) + 1];
        }
        void add(double v) {
            int i = v <= min ? 0 : Math.min(counts.length - 1, (int) (Math.log(v / min) / lnGamma));
            counts[i]++;
            total++;
        }
        double percentile(double p) {                       // nearest rank: smallest value with at least p * total samples at or below it
            long rank = (long) Math.ceil(p * total), seen = 0;
            for (int i = 0; i < counts.length; i++) {
                seen += counts[i];
                if (seen >= rank) return min * Math.pow(gamma, i) * (1 + eps);
            }
            return Double.NaN;
        }
        void merge(LogHistogram o) {
            for (int i = 0; i < counts.length; i++) counts[i] += o.counts[i];
            total += o.total;
        }
    }

    /** One request is intended every 1 ms and takes 0.5 ms; the server freezes from 10,000 ms to 11,000 ms. A closed-loop client sends the next request only after the
     *  previous answer. Returns {latency as the closed-loop client records it, latency measured from the moment the request should have been sent}. */
    static double[][] closedLoopWithStall(int requests) {
        double[] naive = new double[requests], corrected = new double[requests];
        double finish = 0;
        for (int i = 0; i < requests; i++) {
            double send = Math.max(i, finish);              // a client that waits for each answer sends late once it is behind
            double start = (send >= 10_000 && send < 11_000) ? 11_000 : send;
            finish = start + 0.5;
            naive[i] = finish - send;                       // what a closed-loop benchmark records
            corrected[i] = finish - i;                      // measured from the moment the request should have been sent
        }
        return new double[][]{naive, corrected};
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 49 (tail-latency-and-fan-out), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    static double lognormalMs(Random rnd) { return 10 * Math.exp(gaussian(rnd)); }       // median 10 ms, sigma 1

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Percentiles.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(50);
        int n = 300_000;
        double[] samples = new double[n];
        LogHistogram all = new LogHistogram(0.01, 100_000, 0.01), a = new LogHistogram(0.01, 100_000, 0.01), b = new LogHistogram(0.01, 100_000, 0.01);
        for (int i = 0; i < n; i++) {
            samples[i] = lognormalMs(rnd);
            all.add(samples[i]);
            (i < n / 2 ? a : b).add(samples[i]);
        }
        double[] sorted = samples.clone();
        Arrays.sort(sorted);
        double worst = 0;
        StringBuilder sb = new StringBuilder();
        for (double p : new double[]{0.5, 0.9, 0.99, 0.999}) {
            double exact = nearestRank(sorted, p), est = all.percentile(p), err = Math.abs(est - exact) / exact;
            worst = Math.max(worst, err);
            check(err <= 0.01 * (1 + 1e-9), "histogram percentile within 1% at p = " + p);
            sb.append(String.format("p%s exact %.2f ms, histogram %.2f ms; ", p * 100, exact, est));
        }
        a.merge(b);
        check(Arrays.equals(a.counts, all.counts) && a.total == all.total, "merging two histograms gives exactly the histogram of the combined data");
        System.out.printf("log histogram with 1%% relative error (%d buckets covering 0.01 ms to 100 s) on 300,000 lognormal samples, worst percentile error %.3f%%: %s%n", all.counts.length, 100 * worst, sb);

        int fast = 995_000, slow = 5_000;                   // server A takes 99.5% of the traffic, server B (a sick one) 0.5%
        double[] serverA = new double[fast], serverB = new double[slow], merged = new double[fast + slow];
        LogHistogram histA = new LogHistogram(0.01, 100_000, 0.01), histB = new LogHistogram(0.01, 100_000, 0.01);
        for (int i = 0; i < fast; i++) { serverA[i] = 8 + 4 * rnd.nextDouble(); histA.add(serverA[i]); }
        for (int i = 0; i < slow; i++) { serverB[i] = 900 + 200 * rnd.nextDouble(); histB.add(serverB[i]); }
        System.arraycopy(serverA, 0, merged, 0, fast);
        System.arraycopy(serverB, 0, merged, fast, slow);
        Arrays.sort(serverA); Arrays.sort(serverB); Arrays.sort(merged);
        double pa = nearestRank(serverA, 0.99), pb = nearestRank(serverB, 0.99), avg = (pa + pb) / 2;
        double truth99 = nearestRank(merged, 0.99), truth999 = nearestRank(merged, 0.999);
        histA.merge(histB);
        double hist99 = histA.percentile(0.99), hist999 = histA.percentile(0.999);
        check(truth99 < 13 && truth999 > 900 && avg > 400, "averaging per-server p99 values gives the p99 of neither the traffic nor any server");
        check(Math.abs(hist99 - truth99) <= 0.01 * truth99 && Math.abs(hist999 - truth999) <= 0.01 * truth999, "merged histograms recover the true percentiles of the combined traffic within 1%");
        System.out.printf("server A: 995,000 requests between 8 and 12 ms, p99 %.1f ms; server B: 5,000 requests between 900 and 1,100 ms, p99 %.1f ms; average of the two p99s %.1f ms; true p99 of all traffic %.1f ms, true p99.9 %.1f ms; merged histograms say p99 %.1f ms and p99.9 %.1f ms%n",
                pa, pb, avg, truth99, truth999, hist99, hist999);

        int requests = 20_000;
        double[][] latencies = closedLoopWithStall(requests);
        double[] naive = latencies[0], corrected = latencies[1];
        Arrays.sort(naive); Arrays.sort(corrected);
        int naiveSlow = 0, correctedSlow = 0;
        for (int i = 0; i < requests; i++) { if (naive[i] > 100) naiveSlow++; if (corrected[i] > 100) correctedSlow++; }
        check(nearestRank(naive, 0.99) < 1 && nearestRank(corrected, 0.99) > 500 && naive[requests - 1] > 1000, "coordinated omission hides the stall from the percentiles");
        check(naiveSlow == 1 && correctedSlow > 1500, "the closed-loop benchmark records one slow request, the intended-time view records the whole backlog");
        System.out.printf("a 1 s stall seen by a closed-loop benchmark: p50 %.1f ms, p99 %.1f ms, p99.9 %.1f ms, max %.1f ms, %d of %d requests slower than 100 ms; measured from the intended send time: p50 %.1f ms, p99 %.1f ms, p99.9 %.1f ms, max %.1f ms, %d slower than 100 ms%n",
                nearestRank(naive, 0.5), nearestRank(naive, 0.99), nearestRank(naive, 0.999), naive[requests - 1], naiveSlow, requests,
                nearestRank(corrected, 0.5), nearestRank(corrected, 0.99), nearestRank(corrected, 0.999), corrected[requests - 1], correctedSlow);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("Percentiles: " + passed + " checks passed");
    }
}
