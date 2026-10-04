import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 53 of the principles catalog (Part 3): Retry amplification and retry budgets
 *
 * HOW IT WORKS
 *   Retries multiply: three layers that each try four times turn one failed user request into 64 calls at the
 *   bottom. A retry budget (retries limited to a fraction of normal traffic) keeps a struggling system able to
 *   recover.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java RetryBudgets.java
 *   Expected: the output in expected-output.txt, ending "RetryBudgets: 13 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class RetryBudgets {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    static int poisson(double mean, Random rnd) {              // Knuth's multiplication method, fine for small means
        double limit = Math.exp(-mean), p = 1;
        int k = 0;
        do { k++; p *= rnd.nextDouble(); } while (p > limit);
        return k - 1;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** Expected number of calls that reach the bottom service per request entering the top, when `layers` layers each try up to `attempts` times
     *  and the bottom fails every call with probability q. */
    static double amplification(int layers, int attempts, double q) {
        double fail = q, product = 1;
        for (int i = 0; i < layers; i++) {                  // from the layer just above the bottom up to the top
            double expectedTries = 0, p = 1;
            for (int j = 0; j < attempts; j++) { expectedTries += p; p *= fail; }    // 1 + f + f^2 + ...: another try happens only if all earlier ones failed
            product *= expectedTries;
            fail = Math.pow(fail, attempts);                // a call at this layer fails only when all of its tries fail
        }
        return product;
    }

    /** The same chain simulated call by call. Returns {calls that reached the bottom, 1 if the request failed}. */
    static int[] callChain(int layersLeft, int attempts, double q, Random rnd) {
        if (layersLeft == 0) return new int[]{1, rnd.nextDouble() < q ? 1 : 0};      // the bottom service
        int calls = 0;
        for (int a = 0; a < attempts; a++) {
            int[] r = callChain(layersLeft - 1, attempts, q, rnd);
            calls += r[0];
            if (r[1] == 0) return new int[]{calls, 0};
        }
        return new int[]{calls, 1};
    }

    static final int NO_RETRY = 0, IMMEDIATE_RETRY = 1, BUDGETED_RETRY = 2, BACKOFF_RETRY = 3, IMMEDIATE_SKIP = 4;

    static final String[] STORM_NAMES = {"no retries", "3 immediate retries", "3 retries with a 10% budget", "3 retries with full-jitter backoff", "3 immediate retries, server skips expired requests"};

    /** Retry budget: every new request earns `ratio` of a retry token (up to `max`) and every retry spends one. No token, no retry. */
    static final class RetryBudget {
        private final double ratio, max;
        private double tokens;
        RetryBudget(double ratio, double max, double initial) { this.ratio = ratio; this.max = max; this.tokens = initial; }
        void onRequest() { tokens = Math.min(max, tokens + ratio); }
        boolean tryRetry() {
            if (tokens < 1) return false;
            tokens -= 1;
            return true;
        }
    }

    static final class Logical { int attempts = 1; boolean done; }

    record Attempt(Logical request, long deadline) {}

    record Due(long tick, Logical request) {}

    /** One tick is 10 ms. The server answers one request per tick (100 per second) from a first-in first-out queue, new requests arrive at 80 per second,
     *  and a client gives up on an attempt after 100 ticks (1 s). From tick 2000 to 2500 (5 s) the server only manages 20 per second.
     *  Returns {goodput before the stall, during it, in the 20 s after it, in the last 20 s (all in answered requests per second), final queue length}. */
    static double[] retryStorm(int policy, long seed) {
        Random rnd = new Random(seed);
        final int timeout = 100, ticks = 12_000, stallFrom = 2_000, stallTo = 2_500, maxAttempts = policy == NO_RETRY ? 1 : 4;
        ArrayDeque<Attempt> queue = new ArrayDeque<>(), watching = new ArrayDeque<>();      // watching: attempts in the order their deadlines fall
        PriorityQueue<Due> retries = new PriorityQueue<>((a, b) -> Long.compare(a.tick(), b.tick()));
        double credit = 0;
        RetryBudget budget = new RetryBudget(0.1, 100, 10);
        long[] answered = new long[ticks / 100];
        for (int now = 0; now < ticks; now++) {
            for (int k = poisson(0.8, rnd); k > 0; k--) {
                Attempt a = new Attempt(new Logical(), now + timeout);
                queue.add(a); watching.add(a);
                budget.onRequest();                          // the budget earns 0.1 retry per new request
            }
            while (!retries.isEmpty() && retries.peek().tick() <= now) {
                Attempt a = new Attempt(retries.poll().request(), now + timeout);
                queue.add(a); watching.add(a);
            }
            credit += (now >= stallFrom && now < stallTo) ? 0.2 : 1.0;
            while (credit >= 1 && !queue.isEmpty()) {
                Attempt a = queue.poll();
                if (policy == IMMEDIATE_SKIP && a.deadline() < now) continue;               // the client is gone: skip it for free
                credit -= 1;
                if (a.deadline() >= now && !a.request().done) { a.request().done = true; answered[now / 100]++; }   // otherwise the work is wasted
            }
            if (queue.isEmpty()) credit = Math.min(credit, 1.0);
            while (!watching.isEmpty() && watching.peek().deadline() <= now) {
                Logical r = watching.poll().request();
                if (r.done) continue;
                if (r.attempts < maxAttempts && (policy != BUDGETED_RETRY || budget.tryRetry())) {
                    long delay = policy == BACKOFF_RETRY ? Math.max(1, Math.round(backoff(FULL_JITTER, r.attempts - 1, 0, 50, 400, rnd))) : 1;
                    r.attempts++;
                    retries.add(new Due(now + delay, r));
                }
            }
        }
        double[] out = new double[5];
        int[][] windows = {{5, 20}, {20, 25}, {25, 45}, {100, 120}};
        for (int w = 0; w < 4; w++) {
            long sum = 0;
            for (int s = windows[w][0]; s < windows[w][1]; s++) sum += answered[s];
            out[w] = sum / (double) (windows[w][1] - windows[w][0]);
        }
        out[4] = queue.size();
        return out;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 52 (exponential-backoff-and-jitter), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    static final int IMMEDIATE = 0, EXPONENTIAL = 1, EQUAL_JITTER = 2, FULL_JITTER = 3, DECORRELATED = 4;

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

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java RetryBudgets.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        check(amplification(3, 4, 1.0) == 64 && amplification(4, 3, 1.0) == 81 && amplification(1, 1, 1.0) == 1, "when the bottom always fails, layers x attempts multiply: 4^3 = 64 and 3^4 = 81");
        check(close(amplification(3, 4, 0), 1, 1e-12), "when the bottom never fails, nobody retries");
        Random rnd = new Random(53);
        double[][] cases = {{3, 4, 1.0}, {4, 3, 1.0}, {3, 3, 0.5}, {3, 4, 0.7}, {2, 3, 0.9}, {5, 2, 0.8}};
        StringBuilder sb = new StringBuilder();
        for (double[] cs : cases) {
            int layers = (int) cs[0], attempts = (int) cs[1], trials = 300_000;
            double q = cs[2], sum = 0;
            for (int t = 0; t < trials; t++) sum += callChain(layers, attempts, q, rnd)[0];
            double formula = amplification(layers, attempts, q);
            check(rel(sum / trials, formula, 0.02), "retry amplification formula for " + Arrays.toString(cs) + ": simulated " + sum / trials + ", formula " + formula);
            sb.append(String.format("%d layers x %d attempts, bottom fails %.0f%%: %.2f calls at the bottom (simulated %.2f); ", layers, attempts, 100 * q, formula, sum / trials));
        }
        System.out.println("calls reaching the bottom service per user request: " + sb);

        double[][] storm = new double[5][5];
        int seeds = 5;
        for (int p = 0; p < 5; p++) {
            for (int s = 0; s < seeds; s++) {
                double[] r = retryStorm(p, 5300 + 100L * p + s);
                for (int j = 0; j < 5; j++) storm[p][j] += r[j] / seeds;
            }
        }
        check(storm[NO_RETRY][0] > 70 && storm[IMMEDIATE_RETRY][0] > 70 && storm[BUDGETED_RETRY][0] > 70, "before the stall every policy answers about 80 requests per second");
        check(storm[NO_RETRY][3] > 70 && storm[BUDGETED_RETRY][3] > 70, "without retries or with a budget the system is back to normal at the end");
        check(storm[IMMEDIATE_RETRY][3] < 5 && storm[IMMEDIATE_RETRY][4] > 10_000, "with three immediate retries the system never recovers");
        check(storm[BACKOFF_RETRY][3] < 20, "backoff and jitter alone do not rescue it, got " + storm[BACKOFF_RETRY][3]);
        check(storm[IMMEDIATE_SKIP][3] > 60, "when the server skips requests nobody waits for, retries no longer sustain the overload");
        sb.setLength(0);
        for (int p = 0; p < 5; p++)
            sb.append(String.format("%s: before %.0f/s, during %.0f/s, in the 20 s after %.0f/s, last 20 s %.0f/s, queue at the end %.0f; ", STORM_NAMES[p], storm[p][0], storm[p][1], storm[p][2], storm[p][3], storm[p][4]));
        System.out.println("80 requests/s into a server that does 100/s, with a 5 s stall at 20% speed, mean of 5 runs: " + sb);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("RetryBudgets: " + passed + " checks passed");
    }
}
