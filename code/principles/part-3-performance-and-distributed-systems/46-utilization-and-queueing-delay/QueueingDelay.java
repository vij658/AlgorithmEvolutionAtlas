import java.util.*;
import java.util.function.DoubleSupplier;

/**
 * Entry 46 of the principles catalog (Part 3): Utilization and queueing delay
 *
 * HOW IT WORKS
 *   As utilization rho approaches 1, waiting explodes: for an M/M/1 queue the time in system is 1/(1 - rho)
 *   service times. Pollaczek-Khinchine adds the effect of variable service times, and Erlang C gives the
 *   waiting probability for a pool of servers, which sets how many servers keep waits rare.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java QueueingDelay.java
 *   Expected: the output in expected-output.txt, ending "QueueingDelay: 35 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class QueueingDelay {
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

    static double exponential(Random rnd, double mean) { return -mean * Math.log(1 - rnd.nextDouble()); }

    static double nearestRank(double[] sorted, double p) { return sorted[(int) Math.ceil(p * sorted.length) - 1]; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** Pollaczek-Khinchine: mean time in system for a single server with Poisson arrivals and any service-time distribution. */
    static double pkResponse(double lambda, double meanS, double secondMoment) {
        double rho = lambda * meanS;
        return meanS + lambda * secondMoment / (2 * (1 - rho));
    }

    /** Lindley's recursion: wait[k+1] = max(0, wait[k] + service[k] - gap[k+1]). Returns the mean time in system. */
    static double simulateMG1(double lambda, DoubleSupplier service, long customers, Random rnd) {
        double wait = 0, sumResponse = 0;
        for (long k = 0; k < customers; k++) {
            double s = service.getAsDouble();
            sumResponse += wait + s;
            wait = Math.max(0, wait + s - exponential(rnd, 1 / lambda));
        }
        return sumResponse / customers;
    }

    /** Erlang C: probability that an arriving request must wait, with c servers and offered load a = lambda * meanService (in Erlangs). Needs a < c. */
    static double erlangC(int c, double a) {
        double b = 1;                                       // Erlang B through its stable recursion B(0) = 1, B(k) = a B(k-1) / (k + a B(k-1))
        for (int k = 1; k <= c; k++) b = a * b / (k + a * b);
        return b / (1 - (a / c) * (1 - b));
    }

    static double erlangMeanWait(int c, double a, double meanService) { return erlangC(c, a) * meanService / (c - a); }   // mean time in the queue

    /** Smallest pool for which at most `target` of the requests have to wait, at offered load a (in Erlangs). */
    static int poolSize(double a, double target) {
        int c = (int) Math.floor(a) + 1;                    // a pool needs more servers than the offered load
        while (erlangC(c, a) > target) c++;
        return c;
    }

    /** Standard normal density and distribution function (Simpson's rule, so no library is needed). */
    static double phi(double x) { return Math.exp(-x * x / 2) / Math.sqrt(2 * Math.PI); }

    static double bigPhi(double x) {
        int steps = 20_000;
        double h = x / steps, sum = phi(0) + phi(x);
        for (int i = 1; i < steps; i++) sum += phi(i * h) * (i % 2 == 1 ? 4 : 2);
        return 0.5 + sum * h / 3;
    }

    /** Halfin-Whitt limit: with c = a + beta sqrt(a) servers and a large, P(wait) tends to 1 / (1 + beta Phi(beta) / phi(beta)). Solved for beta by bisection. */
    static double betaFor(double waitProbability) {
        double lo = 0, hi = 10;
        for (int i = 0; i < 100; i++) {
            double mid = (lo + hi) / 2;
            if (1 / (1 + mid * bigPhi(mid) / phi(mid)) > waitProbability) lo = mid; else hi = mid;
        }
        return (lo + hi) / 2;
    }

    /** FIFO queue with c servers, Poisson arrivals and exponential service: every arrival takes the server that frees up first. Returns {share that waited, mean wait}. */
    static double[] simulateMMc(int c, double lambda, double meanService, long customers, Random rnd) {
        PriorityQueue<Double> free = new PriorityQueue<>();
        for (int i = 0; i < c; i++) free.add(0.0);
        double t = 0, sumWait = 0;
        long waited = 0;
        for (long k = 0; k < customers; k++) {
            t += exponential(rnd, 1 / lambda);
            double start = Math.max(t, free.poll());
            if (start > t) { waited++; sumWait += start - t; }
            free.add(start + exponential(rnd, meanService));
        }
        return new double[]{waited / (double) customers, sumWait / customers};
    }

    /** Time in system of every customer of a first-in first-out M/M/1 queue (Lindley's recursion again), for percentiles. */
    static double[] mm1ResponseTimes(double lambda, double meanService, int customers, Random rnd) {
        double[] response = new double[customers];
        double wait = 0;
        for (int k = 0; k < customers; k++) {
            double s = exponential(rnd, meanService);
            response[k] = wait + s;
            wait = Math.max(0, wait + s - exponential(rnd, 1 / lambda));
        }
        Arrays.sort(response);
        return response;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java QueueingDelay.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        double[] rhos = {0.5, 0.8, 0.9, 0.95, 0.99};
        double[] expected = {2, 5, 10, 20, 100};
        for (int i = 0; i < rhos.length; i++) check(close(pkResponse(rhos[i], 1, 2) , expected[i], 1e-9), "M/M/1: time in system is S / (1 - rho)");
        long N = 10_000_000;
        StringBuilder mm = new StringBuilder(), md = new StringBuilder();
        for (int i = 0; i < 4; i++) {
            double rho = rhos[i];
            Random rnd = new Random(460 + i);
            double w1 = simulateMG1(rho, () -> exponential(rnd, 1.0), N, rnd);
            check(rel(w1, 1 / (1 - rho), i < 3 ? 0.04 : 0.08), "M/M/1 simulation at rho = " + rho + ", got " + w1);
            mm.append(String.format("rho %.2f: simulated %.2f vs formula %.2f; ", rho, w1, 1 / (1 - rho)));
            double w2 = simulateMG1(rho, () -> 1.0, N, rnd);
            double f2 = pkResponse(rho, 1, 1);
            check(rel(w2, f2, i < 3 ? 0.04 : 0.08), "M/D/1 simulation at rho = " + rho + ", got " + w2);
            md.append(String.format("rho %.2f: simulated %.2f vs formula %.2f; ", rho, w2, f2));
        }
        double sigma2 = Math.log(5), sigma = Math.sqrt(sigma2);
        Random rnd = new Random(469);
        double w3 = simulateMG1(0.8, () -> Math.exp(-sigma2 / 2 + sigma * gaussian(rnd)), N, rnd);
        double f3 = pkResponse(0.8, 1, 5);
        check(rel(w3, f3, 0.10), "M/G/1 with squared coefficient of variation 4, got " + w3);
        System.out.println("M/M/1 mean time in system (service time 1): " + mm);
        System.out.println("M/D/1 (constant service time): " + md);
        System.out.printf("M/G/1 at rho = 0.8 with lognormal service, squared coefficient of variation 4: simulated %.2f, Pollaczek-Khinchine %.2f; constant service gives %.2f, exponential %.2f%n",
                w3, f3, pkResponse(0.8, 1, 1), pkResponse(0.8, 1, 2));
        System.out.println("time in system over service time: rho 0.5 -> 2, 0.8 -> 5, 0.9 -> 10, 0.95 -> 20, 0.99 -> 100");

        double[] resp = mm1ResponseTimes(0.8, 1.0, 3_000_000, new Random(4690));
        double mean80 = 0;
        for (double v : resp) mean80 += v / resp.length;
        check(rel(nearestRank(resp, 0.5), Math.log(2) * 5, 0.03) && rel(nearestRank(resp, 0.99), Math.log(100) * 5, 0.04) && rel(mean80, 5, 0.03), "M/M/1 time in system is exponential: median ln 2 x mean, p99 ln 100 x mean");
        System.out.printf("M/M/1 at rho = 0.8, mean time in system %.2f: median %.2f, p90 %.2f, p99 %.2f, p99.9 %.2f (an exponential distribution with mean 5 has %.2f, %.2f, %.2f, %.2f)%n",
                mean80, nearestRank(resp, 0.5), nearestRank(resp, 0.9), nearestRank(resp, 0.99), nearestRank(resp, 0.999), Math.log(2) * 5, Math.log(10) * 5, Math.log(100) * 5, Math.log(1000) * 5);

        // ---- one shared pool against separate queues, and the square-root rule for sizing a pool
        check(close(erlangC(1, 0.8), 0.8, 1e-12) && close(erlangMeanWait(1, 0.8, 1), 4.0, 1e-12), "one server: Erlang C is rho, and the wait is rho / (1 - rho) service times");
        check(close(erlangC(2, 1.0), 1.0 / 3, 1e-12), "two servers at offered load 1: waiting probability 1/3");
        StringBuilder pool = new StringBuilder();
        for (int c : new int[]{1, 2, 5, 10, 50, 100}) {
            double a = 0.8 * c;
            Random r = new Random(4600 + c);
            double[] sim = simulateMMc(c, a, 1.0, 3_000_000L, r);
            double pw = erlangC(c, a), wq = erlangMeanWait(c, a, 1.0);
            check(close(sim[0], pw, 0.01) && (Math.abs(sim[1] - wq) <= 0.05 * wq + 0.005), "M/M/" + c + " simulation matches Erlang C, simulated " + Arrays.toString(sim) + " formula " + pw + " " + wq);
            pool.append(String.format("%d servers: P(wait) %.3f, mean wait %.3f (simulated %.3f); ", c, pw, wq, sim[1]));
        }
        System.out.println("rho = 0.8 with the same total load, one shared pool of c servers (service time 1): " + pool);
        StringBuilder staffing = new StringBuilder();
        double lastRatio = 0;
        for (int a : new int[]{25, 100, 400, 1600, 6400}) {
            int c = poolSize(a, 0.05);
            check(erlangC(c, a) <= 0.05 && erlangC(c - 1, a) > 0.05, "poolSize returns the smallest pool that meets the target, a = " + a);
            double ratio = (c - a) / Math.sqrt(a);
            check(ratio > 1.0 && ratio < 2.6, "square-root staffing: the extra servers grow like sqrt(a), got " + ratio);
            lastRatio = ratio;
            staffing.append(String.format("a = %d: %d servers (%+d, %.2f sqrt(a)); ", a, c, c - a, ratio));
        }
        double beta = betaFor(0.05);
        check(close(bigPhi(1.0), 0.8413447460685429, 1e-9) && close(bigPhi(1.96), 0.9750021048517795, 1e-9), "Simpson integration reproduces the normal distribution function");
        check(Math.abs(lastRatio - beta) < 0.05, "the staffing ratio at a = 6400 is within 0.05 of the Halfin-Whitt value " + beta);
        System.out.printf("smallest pool with P(wait) <= 5%% for offered load a: %s Halfin-Whitt limit for 5%%: %.3f sqrt(a)%n", staffing, beta);
        StringBuilder sweep = new StringBuilder();
        for (int c : new int[]{101, 105, 110, 120, 130}) sweep.append(String.format("%d servers: %.4f; ", c, erlangC(c, 100)));
        System.out.println("offered load 100 Erlangs (for example 1000 requests/s at 0.1 s each), P(wait): " + sweep);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("QueueingDelay: " + passed + " checks passed");
    }
}
