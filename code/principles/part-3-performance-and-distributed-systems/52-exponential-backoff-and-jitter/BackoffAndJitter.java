import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 52 of the principles catalog (Part 3): Exponential backoff and jitter
 *
 * HOW IT WORKS
 *   Retry after a delay that doubles each attempt, with a cap. Adding jitter (randomising the delay) breaks up
 *   synchronised retry waves; the program counts the total calls needed by plain, full-jitter and decorrelated-
 *   jitter strategies against an overloaded server.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BackoffAndJitter.java
 *   Expected: the output in expected-output.txt, ending "BackoffAndJitter: 400016 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BackoffAndJitter {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final int IMMEDIATE = 0, EXPONENTIAL = 1, EQUAL_JITTER = 2, FULL_JITTER = 3, DECORRELATED = 4;

    static final String[] BACKOFF_NAMES = {"retry at once", "exponential, no jitter", "equal jitter", "full jitter", "decorrelated jitter"};

    /** Delay before retry number `attempt` (0 for the first retry), in milliseconds. `previous` is the delay used last time (decorrelated jitter needs it). */
    static double backoff(int kind, int attempt, double previous, double base, double cap, Random rnd) {
        double ceiling = Math.min(cap, base * Math.pow(2, Math.min(attempt, 30)));          // base * 2^attempt, capped
        switch (kind) {
            case IMMEDIATE:    return 1;
            case EXPONENTIAL:  return ceiling;
            case EQUAL_JITTER: return ceiling / 2 + rnd.nextDouble() * ceiling / 2;          // half fixed, half random
            case FULL_JITTER:  return rnd.nextDouble() * ceiling;                            // anywhere between 0 and the ceiling
            default:           return Math.min(cap, base + rnd.nextDouble() * (previous * 3 - base));   // uniform in [base, 3 * previous], capped
        }
    }

    /** `clients` clients all try at time 0. The server accepts `perTick` requests per millisecond and rejects the rest; a rejected client waits and tries again.
     *  Returns {requests sent in total, time when the last client got through, largest number of requests in one millisecond after the first}. */
    static double[] contend(int kind, int clients, int perTick, double base, double cap, Random rnd) {
        PriorityQueue<long[]> due = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));      // {time, client}
        int[] attempt = new int[clients];
        double[] previous = new double[clients];
        for (int c = 0; c < clients; c++) { due.add(new long[]{0, c}); previous[c] = base; }
        long total = 0, finish = 0;
        int peakRetry = 0, done = 0;
        while (done < clients) {
            long now = due.peek()[0];
            ArrayList<Integer> batch = new ArrayList<>();
            while (!due.isEmpty() && due.peek()[0] == now) batch.add((int) due.poll()[1]);
            Collections.shuffle(batch, rnd);                // the server lets an arbitrary subset through
            total += batch.size();
            if (now > 0) peakRetry = Math.max(peakRetry, batch.size());
            for (int i = 0; i < batch.size(); i++) {
                int c = batch.get(i);
                if (i < perTick) { done++; finish = now; continue; }
                double wait = backoff(kind, attempt[c]++, previous[c], base, cap, rnd);
                previous[c] = wait;
                due.add(new long[]{now + Math.max(1, Math.round(wait)), c});
            }
        }
        return new double[]{total, finish, peakRetry};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BackoffAndJitter.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(52);
        for (int t = 0; t < 100_000; t++) {
            int attempt = rnd.nextInt(40);
            double base = 1 + 20 * rnd.nextDouble(), cap = base * (1 + 100 * rnd.nextDouble());
            double ceiling = Math.min(cap, base * Math.pow(2, attempt)), previous = base + rnd.nextDouble() * (cap - base);
            double full = backoff(FULL_JITTER, attempt, previous, base, cap, rnd), equal = backoff(EQUAL_JITTER, attempt, previous, base, cap, rnd), dec = backoff(DECORRELATED, attempt, previous, base, cap, rnd);
            check(backoff(EXPONENTIAL, attempt, previous, base, cap, rnd) == ceiling, "plain exponential backoff is base * 2^attempt, capped");
            check(full >= 0 && full <= ceiling, "full jitter stays between 0 and the ceiling");
            check(equal >= ceiling / 2 && equal <= ceiling, "equal jitter stays between half the ceiling and the ceiling");
            check(dec >= base && dec <= cap && dec <= 3 * previous * (1 + 1e-12), "decorrelated jitter stays between base and min(cap, 3 * previous)");
        }
        double sumFull = 0, sumEqual = 0;
        int draws = 400_000;
        for (int i = 0; i < draws; i++) { sumFull += backoff(FULL_JITTER, 4, 0, 10, 1000, rnd); sumEqual += backoff(EQUAL_JITTER, 4, 0, 10, 1000, rnd); }
        check(rel(sumFull / draws, 80, 0.01) && rel(sumEqual / draws, 120, 0.01), "at attempt 4 (ceiling 160 ms) full jitter averages 80 ms and equal jitter 120 ms");

        int clients = 200, perTick = 5, trials = 200;
        double base = 10, cap = 1000;
        double[][] mean = new double[5][3];
        for (int kind = 0; kind < 5; kind++) {
            for (int t = 0; t < trials; t++) {
                double[] r = contend(kind, clients, perTick, base, cap, new Random(5200 + 1000L * kind + t));
                for (int j = 0; j < 3; j++) mean[kind][j] += r[j] / trials;
            }
        }
        double lockstep = perTick * (clients / perTick) * (clients / perTick + 1) / 2.0;      // 200 + 195 + ... + 5 requests when every survivor retries together
        check(mean[IMMEDIATE][0] == lockstep && mean[EXPONENTIAL][0] == lockstep, "without jitter the clients stay in lockstep and send exactly " + lockstep + " requests");
        double floor = clients + (clients - perTick);       // every client sends once, and every rejected client needs at least one more request
        check(mean[FULL_JITTER][0] < 0.25 * lockstep && mean[EQUAL_JITTER][0] < 0.25 * lockstep && mean[DECORRELATED][0] < 0.25 * lockstep, "every kind of jitter does far less work than lockstep retries, got " + Arrays.deepToString(mean));
        check(mean[FULL_JITTER][1] < mean[EXPONENTIAL][1] / 100 && mean[FULL_JITTER][2] < 0.25 * mean[EXPONENTIAL][2], "full jitter finishes sooner and flattens the retry waves");
        StringBuilder sb = new StringBuilder();
        for (int kind = 0; kind < 5; kind++) sb.append(String.format("%s: %.0f requests, done after %.0f ms, worst millisecond %.1f requests; ", BACKOFF_NAMES[kind], mean[kind][0], mean[kind][1], mean[kind][2]));
        System.out.println("200 clients, server accepts 5 requests per ms, base 10 ms, cap 1000 ms, mean of 200 runs: " + sb);
        sb.setLength(0);
        for (double b : new double[]{2, 10, 50, 200}) {      // the ranking among the jitter kinds depends on the base delay; the gap to lockstep does not
            sb.append(String.format("base %.0f ms: ", b));
            for (int kind = EQUAL_JITTER; kind <= DECORRELATED; kind++) {
                double requests = 0, finish = 0;
                for (int t = 0; t < 100; t++) {
                    double[] r = contend(kind, clients, perTick, b, cap, new Random(5250 + 1000L * kind + t));
                    requests += r[0] / 100; finish += r[1] / 100;
                }
                check(requests >= floor - 1e-6 && requests < 0.25 * lockstep, "jitter sends between " + floor + " and a quarter of " + lockstep + " requests at base " + b + ", got " + requests);
                sb.append(String.format("%s %.0f requests / %.0f ms; ", BACKOFF_NAMES[kind], requests, finish));
            }
        }
        System.out.println("the same experiment for other base delays, mean of 100 runs, the least possible is " + (int) floor + " requests: " + sb);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("BackoffAndJitter: " + passed + " checks passed");
    }
}
