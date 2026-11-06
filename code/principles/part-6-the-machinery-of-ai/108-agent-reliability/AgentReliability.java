import java.util.*;

/**
 * Entry 108 of the principles catalog (Part 6): The arithmetic of agents: compounding errors, verification,
 * voting, idempotent tool calls and context growth
 *
 * HOW IT WORKS
 *   An agent is a loop: the model reads the conversation so far, picks a tool call, the program runs it, and the
 *   result is appended to the conversation. Five pieces of arithmetic decide whether such a loop is usable:
 *     1. Errors compound. If every step is right with probability p, n steps are all right with probability p^n:
 *        95% per step is only 36% over 20 steps.
 *     2. Verification is the multiplier. A check that catches a fraction d of bad steps, with a retry, turns
 *        per-step success p into p + (1 - p) d p + ...; d matters more than a slightly better model.
 *     3. Voting helps only when errors are independent. Sampling k answers and taking the most common one
 *        (self-consistency) raises accuracy when each answer is right more often than any single wrong answer,
 *        lowers it when the model is usually wrong in the same way, and cannot beat a shared blind spot.
 *        (For a strict majority, entry 28's Boyer-Moore vote finds it in one pass.)
 *     4. Tool calls are remote calls. A timeout does not say whether the action happened; retrying a payment
 *        without an idempotency key (entry 60) pays twice.
 *     5. Context grows with every step and the whole history is re-read each time, so the total tokens read by an
 *        n-step loop grow like n^2. Caching the shared prefix turns most of that into reuse.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AgentReliability.java
 *   Expected: the output in expected-output.txt, ending "AgentReliability: 400048 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class AgentReliability {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    static boolean within(double observed, double p, int trials, double sigmas) {
        return Math.abs(observed - p) <= sigmas * Math.sqrt(Math.max(p * (1 - p), 1e-12) / trials) + 1e-12;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** 1. A chain of n independent steps, each right with probability p. */
    static double chainSuccess(double p, int n) { return Math.pow(p, n); }

    /** 2. One step with up to `attempts` tries; a bad result is caught with probability `detect` and retried. */
    static double stepSuccess(double p, double detect, int attempts) {
        double s = p;
        for (int m = 2; m <= attempts; m++) s = p + (1 - p) * detect * s;
        return s;
    }

    static double expectedAttempts(double p, double detect, int attempts) {
        double e = 1;
        for (int m = 2; m <= attempts; m++) e = 1 + (1 - p) * detect * e;
        return e;
    }

    /** 3. Plurality vote; ties broken by the random generator. Answer 0 is the correct one. */
    static int plurality(int[] answers, int options, Random rnd) {
        int[] count = new int[options];
        for (int a : answers) count[a]++;
        int best = -1, bestCount = -1, ties = 0;
        for (int o = 0; o < options; o++) {
            if (count[o] > bestCount) { best = o; bestCount = count[o]; ties = 1; }
            else if (count[o] == bestCount && rnd.nextInt(++ties) == 0) best = o;
        }
        return best;
    }

    /** Exact probability that a strict majority of k (odd) independent binary votes is right. */
    static double majorityExact(double p, int k) {
        double s = 0;
        for (int j = k / 2 + 1; j <= k; j++) s += choose(k, j) * Math.pow(p, j) * Math.pow(1 - p, k - j);
        return s;
    }

    static double choose(int n, int k) { double r = 1; for (int i = 0; i < k; i++) r = r * (n - i) / (i + 1); return r; }

    // ----------------------------------------------------------------------------------------------------
    // Helper copied from entry 28 (kadane-and-boyer-moore-majority): Boyer-Moore majority vote
    // ----------------------------------------------------------------------------------------------------
    static int boyerMoore(int[] a) {
        int cand = 0, count = 0;
        for (int x : a) {
            if (count == 0) { cand = x; count = 1; }
            else if (x == cand) count++;
            else count--;
        }
        return cand;
    }

    // ----------------------------------------------------------------------------------------------------
    // 4. A tool that charges a card, behind a network that loses requests and responses
    // ----------------------------------------------------------------------------------------------------
    static final class PaymentTool {
        final Map<String, String> byKey = new HashMap<>();
        long executions = 0;

        String call(String operation, String idempotencyKey) {
            if (idempotencyKey != null) {
                String earlier = byKey.get(idempotencyKey);
                if (earlier != null) return earlier;
            }
            executions++;
            String receipt = "receipt-" + executions;
            if (idempotencyKey != null) byKey.put(idempotencyKey, receipt);
            return receipt;
        }
    }

    /** The agent retries until it sees a response. Returns the number of attempts. */
    static int callWithRetries(PaymentTool tool, String op, String key, double loseRequest, double loseResponse, Random rnd) {
        for (int attempt = 1; attempt <= 50; attempt++) {
            if (rnd.nextDouble() < loseRequest) continue;               // never arrived: nothing happened
            tool.call(op, key);                                         // arrived: the charge happened
            if (rnd.nextDouble() < loseResponse) continue;              // ...but the agent sees only a timeout
            return attempt;
        }
        throw new IllegalStateException("gave up");
    }

    // ----------------------------------------------------------------------------------------------------
    // 5. Tokens read by an agent loop that re-sends its whole history every step
    // ----------------------------------------------------------------------------------------------------
    static long tokensRead(long system, long perStep, int steps) {
        long total = 0;
        for (int t = 0; t < steps; t++) total += system + t * perStep;
        return total;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java AgentReliability.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 1. Compounding: formula against simulation.
        StringBuilder sb = new StringBuilder("all steps right: ");
        int trials = 100_000;
        for (double[] c : new double[][]{{0.99, 10}, {0.99, 100}, {0.95, 20}, {0.90, 20}, {0.999, 1000}}) {
            double p = c[0]; int n = (int) c[1];
            int ok = 0;
            for (int t = 0; t < trials; t++) {
                boolean all = true;
                for (int s = 0; s < n && all; s++) all = rnd.nextDouble() < p;
                if (all) ok++;
            }
            double formula = chainSuccess(p, n);
            check(within(ok / (double) trials, formula, trials, 4.5), "p^n");
            sb.append(f("%s per step x %d steps = %.3f (simulated %.3f); ", c[0], n, formula, ok / (double) trials));
        }
        System.out.println(sb.toString().trim());

        // 2. Verification with retries: p = 0.9 per step, 20 steps, up to 3 attempts per step.
        StringBuilder vb = new StringBuilder("p = 0.9 per step, 20 steps, up to 3 attempts, checker catches a fraction d of bad steps: ");
        double prev = -1;
        for (double d : new double[]{0, 0.5, 0.9, 0.99, 1.0}) {
            double step = stepSuccess(0.9, d, 3);
            int ok = 0, steps = 20, runs = 50_000;
            for (int r = 0; r < runs; r++) {
                boolean all = true;
                for (int s = 0; s < steps && all; s++) {
                    boolean done = false;
                    for (int a = 1; a <= 3 && !done; a++) {
                        if (rnd.nextDouble() < 0.9) { done = true; }
                        else if (a == 3 || rnd.nextDouble() >= d) { all = false; done = true; }
                    }
                }
                if (all) ok++;
            }
            double chain = chainSuccess(step, steps);
            check(within(ok / (double) runs, chain, runs, 4.5), "verified chain matches formula");
            check(chain > prev, "better detection, better chain");
            prev = chain;
            vb.append(f("d=%s: step %.4f, chain %.3f (simulated %.3f), %.3f attempts per step; ",
                    d, step, chain, ok / (double) runs, expectedAttempts(0.9, d, 3)));
        }
        System.out.println(vb.toString().trim());
        check(close(stepSuccess(0.9, 1.0, 3), 1 - Math.pow(0.1, 3), 1e-15), "perfect checker: 1 - (1-p)^attempts");

        // 3. Voting. Binary answers: exact formula, simulation, and Boyer-Moore agreeing with the count.
        StringBuilder mb = new StringBuilder("majority of k samples, two possible answers: ");
        for (double p : new double[]{0.6, 0.4}) {
            mb.append(f("right %.0f%% of the time:", 100 * p));
            double last = p;
            for (int k : new int[]{1, 3, 5, 11, 25}) {
                double exact = majorityExact(p, k);
                int ok = 0, runs = 40_000;
                for (int r = 0; r < runs; r++) {
                    int[] votes = new int[k];
                    int right = 0;
                    for (int i = 0; i < k; i++) { votes[i] = rnd.nextDouble() < p ? 0 : 1; if (votes[i] == 0) right++; }
                    int majority = 2 * right > k ? 0 : 1;
                    check(boyerMoore(votes) == majority, "Boyer-Moore finds the strict majority");
                    if (majority == 0) ok++;
                }
                check(within(ok / (double) runs, exact, runs, 4.5), "majority simulation matches formula");
                if (k > 1) check(p > 0.5 ? exact > last : exact < last, "Condorcet: more votes push away from 1/2");
                last = exact;
                mb.append(f(" k=%d %.3f;", k, exact));
            }
            mb.append(" ");
        }
        System.out.println(mb.toString().trim());

        // Many possible answers: right 40% of the time, wrong answers spread over 5 options, or a shared blind spot.
        StringBuilder pb = new StringBuilder("plurality of k samples, right 40% of the time, wrong answers spread over 5 options: ");
        StringBuilder cb = new StringBuilder("same, but 25% of questions are a shared blind spot where every sample gives the same wrong answer: ");
        double prevSpread = 0;
        for (int k : new int[]{1, 5, 15, 45}) {
            int okSpread = 0, okBlind = 0, runs = 40_000;
            for (int r = 0; r < runs; r++) {
                int[] votes = new int[k];
                for (int i = 0; i < k; i++) votes[i] = rnd.nextDouble() < 0.4 ? 0 : 1 + rnd.nextInt(5);
                if (plurality(votes, 6, rnd) == 0) okSpread++;
                boolean blind = rnd.nextDouble() < 0.25;
                for (int i = 0; i < k; i++) votes[i] = blind ? 1 : (rnd.nextDouble() < 0.4 / 0.75 ? 0 : 1 + rnd.nextInt(5));
                if (plurality(votes, 6, rnd) == 0) okBlind++;
            }
            double spread = okSpread / (double) runs, blindAcc = okBlind / (double) runs;
            check(spread > prevSpread, "spread-out errors: voting helps");
            check(blindAcc <= 0.75 + 0.01, "a shared blind spot caps accuracy");
            prevSpread = spread;
            pb.append(f("k=%d %.3f; ", k, spread));
            cb.append(f("k=%d %.3f; ", k, blindAcc));
        }
        System.out.println(pb.toString().trim());
        System.out.println(cb.toString().trim() + " (ceiling 0.75, up to sampling noise)");

        // 4. Idempotency keys on tool calls: 5% of requests and 5% of responses are lost; the agent retries on timeout.
        int ops = 100_000;
        PaymentTool noKey = new PaymentTool(), withKey = new PaymentTool();
        long attemptsNoKey = 0, attemptsKey = 0;
        Random r1 = new Random(1), r2 = new Random(1);
        for (int i = 0; i < ops; i++) {
            attemptsNoKey += callWithRetries(noKey, "charge order " + i, null, 0.05, 0.05, r1);
            attemptsKey += callWithRetries(withKey, "charge order " + i, "order-" + i, 0.05, 0.05, r2);
        }
        double dupRate = (noKey.executions - ops) / (double) ops, formula = 0.05 / 0.95;
        check(Math.abs(dupRate - formula) < 4.5 * Math.sqrt(formula / ops), "duplicate rate = loseResponse / (1 - loseResponse)");
        check(withKey.executions == ops, "with keys: every order charged exactly once");
        check(attemptsNoKey == attemptsKey, "same network, same attempts");
        System.out.println(f("%,d payments over a network that loses 5%% of requests and 5%% of responses: %.3f attempts each; "
                + "without idempotency keys %,d duplicate charges (%.2f%%, formula 0.05/0.95 = %.2f%%); with keys %,d",
                ops, attemptsNoKey / (double) ops, noKey.executions - ops, 100 * dupRate, 100 * formula, withKey.executions - ops));

        // 5. Context growth: 5,000-token instructions, 1,500 new tokens per step.
        StringBuilder tb = new StringBuilder("tokens read by an agent that re-sends its history (5,000-token start, 1,500 new per step): ");
        for (int steps : new int[]{10, 50, 200}) {
            long total = tokensRead(5000, 1500, steps);
            long formulaTotal = 5000L * steps + 1500L * steps * (steps - 1) / 2;
            long fresh = 5000 + 1500L * (steps - 1);
            check(total == formulaTotal, "sum = nS + D n(n-1)/2");
            tb.append(f("%d steps: %,d read, of which %,d are new (%.0f times reuse); ", steps, total, fresh, total / (double) fresh));
        }
        System.out.println(tb.toString().trim());
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(108));
        System.out.println("AgentReliability: " + passed + " checks passed");
    }
}
