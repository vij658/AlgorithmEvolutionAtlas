import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 54 of the principles catalog (Part 3): Circuit breaker
 *
 * HOW IT WORKS
 *   Wrap calls to a dependency in a state machine: closed (calls pass), open (fail fast after too many
 *   failures), half-open (let a probe through after a timeout). During an outage it stops wasting calls and
 *   gives the dependency room to recover.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CircuitBreakerDemo.java
 *   Expected: the output in expected-output.txt, ending "CircuitBreakerDemo: 579040 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class CircuitBreakerDemo {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class CircuitBreaker {
        enum State { CLOSED, OPEN, HALF_OPEN }
        private final int threshold;                        // consecutive failures that trip the breaker
        private final long openFor;                         // how long to stay open before letting one probe through
        private State state = State.CLOSED;
        private int consecutiveFailures;
        private long openedAt;
        private boolean probing;

        CircuitBreaker(int threshold, long openFor) { this.threshold = threshold; this.openFor = openFor; }
        synchronized State state() { return state; }

        /** Ask before every call. When half open, exactly one probe is allowed at a time. */
        synchronized boolean allow(long now) {
            if (state == State.OPEN && now - openedAt >= openFor) { state = State.HALF_OPEN; probing = false; }
            switch (state) {
                case CLOSED: return true;
                case OPEN:   return false;
                default:     if (probing) return false;
                             probing = true;
                             return true;
            }
        }
        synchronized void success() { consecutiveFailures = 0; probing = false; state = State.CLOSED; }
        synchronized void failure(long now) {
            if (state == State.HALF_OPEN || ++consecutiveFailures >= threshold) {
                state = State.OPEN; openedAt = now; probing = false; consecutiveFailures = 0;
            }
        }
    }

    /** 100 requests per second for 180 s; the dependency is down from 60 s to 125 s.
     *  Returns {calls that reached the dependency while it was down, requests rejected by the breaker, ms from recovery until the first successful call}. */
    static double[] outage(boolean useBreaker) {
        CircuitBreaker breaker = new CircuitBreaker(5, 10_000);
        long downFrom = 60_000, downTo = 125_000;
        int calls = 0, rejected = 0;
        long firstOk = -1;
        for (long now = 0; now < 180_000; now += 10) {
            if (useBreaker && !breaker.allow(now)) { rejected++; continue; }
            boolean up = now < downFrom || now >= downTo;
            if (!up) calls++;
            if (up) { breaker.success(); if (now >= downTo && firstOk < 0) firstOk = now; }
            else breaker.failure(now);
        }
        return new double[]{calls, rejected, firstOk - downTo};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java CircuitBreakerDemo.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        CircuitBreaker b = new CircuitBreaker(3, 1000);
        check(b.allow(0) && b.state() == CircuitBreaker.State.CLOSED, "starts closed");
        b.failure(0); b.failure(1); b.success();
        b.failure(2); b.failure(3);
        check(b.state() == CircuitBreaker.State.CLOSED, "a success resets the count: two failures, success, two failures is still closed");
        b.failure(4);
        check(b.state() == CircuitBreaker.State.OPEN, "three failures in a row open the breaker");
        check(!b.allow(500) && !b.allow(1003), "calls are refused while open");
        check(b.allow(1004) && b.state() == CircuitBreaker.State.HALF_OPEN, "after the open period one probe is let through");
        check(!b.allow(1005), "while the probe is out, other calls are still refused");
        b.failure(1006);
        check(b.state() == CircuitBreaker.State.OPEN && !b.allow(2005) && b.allow(2006), "a failed probe reopens the breaker for another full period");
        b.success();
        check(b.state() == CircuitBreaker.State.CLOSED && b.allow(2007) && b.allow(2008), "a successful probe closes it again");

        Random rnd = new Random(54);
        for (int t = 0; t < 2000; t++) {                    // random walks: closed lets calls through, open refuses them, half open lets exactly one probe through
            CircuitBreaker c = new CircuitBreaker(1 + rnd.nextInt(5), 1 + rnd.nextInt(50));
            long now = 0;
            boolean probeOut = false;
            for (int step = 0; step < 300; step++) {
                now += rnd.nextInt(10);
                if (probeOut && rnd.nextInt(3) == 0) {      // the probe comes back
                    if (rnd.nextBoolean()) c.success(); else c.failure(now);
                    probeOut = false;
                    continue;
                }
                boolean allowed = c.allow(now);
                CircuitBreaker.State after = c.state();
                if (probeOut) check(!allowed, "a second call is refused while the probe is out");
                else if (after == CircuitBreaker.State.HALF_OPEN) { check(allowed, "the first call after the open period is the probe"); probeOut = true; }
                else if (after == CircuitBreaker.State.OPEN) check(!allowed, "open refuses calls");
                else { check(allowed, "closed lets calls through"); if (rnd.nextInt(4) == 0) c.failure(now); else c.success(); }
            }
        }
        double[] with = outage(true), without = outage(false);
        check(without[0] == 6500 && without[1] == 0 && without[2] == 0, "without a breaker every one of the 6,500 requests during the outage reaches the dependency");
        check(with[0] == 11 && with[2] == 5040 && with[1] > 6000, "with a breaker only the first 5 failures and one probe every 10 s reach it, got " + Arrays.toString(with));
        System.out.printf("dependency down for 65 s at 100 requests/s: without a breaker %.0f calls hit it; with a breaker (5 failures, 10 s open) only %.0f did, %.0f requests were refused locally, and the first success after recovery came %.0f ms late%n",
                without[0], with[0], with[1], with[2]);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("CircuitBreakerDemo: " + passed + " checks passed");
    }
}
