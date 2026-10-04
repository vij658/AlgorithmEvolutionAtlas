import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 55 of the principles catalog (Part 3): Token bucket, GCRA, fixed and sliding windows
 *
 * HOW IT WORKS
 *   Limit request rates: a token bucket refills at rate r up to a burst size; GCRA is the same thing expressed
 *   with a single timestamp. Fixed windows allow double bursts at a window boundary; sliding logs and sliding
 *   windows fix that at different costs.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java RateLimiters.java
 *   Expected: the output in expected-output.txt, ending "RateLimiters: 119466754 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class RateLimiters {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** Token bucket written as time credit: the bucket holds up to burst * ticksPerRequest ticks of credit, refills one tick per tick and each request spends ticksPerRequest. */
    static final class TokenBucket {
        private final long cost, capacity;
        private long level, last;
        TokenBucket(long ticksPerRequest, long burst, long start) { cost = ticksPerRequest; capacity = burst * cost; level = capacity; last = start; }
        boolean tryAcquire(long now) {
            level = Math.min(capacity, level + (now - last));
            last = now;
            if (level < cost) return false;
            level -= cost;
            return true;
        }
    }

    /** Generic cell rate algorithm: remembers only the "theoretical arrival time" of the next conforming request. */
    static final class Gcra {
        private final long interval, tolerance;
        private long tat;
        Gcra(long ticksPerRequest, long burst, long start) { interval = ticksPerRequest; tolerance = (burst - 1) * ticksPerRequest; tat = start; }
        boolean tryAcquire(long now) {
            if (now < tat - tolerance) return false;
            tat = Math.max(now, tat) + interval;
            return true;
        }
    }

    static final class FixedWindow {
        private final long window; private final int limit; private long windowStart = Long.MIN_VALUE; private int count;
        FixedWindow(long window, int limit) { this.window = window; this.limit = limit; }
        boolean tryAcquire(long now) {
            long start = Math.floorDiv(now, window) * window;
            if (start != windowStart) { windowStart = start; count = 0; }
            if (count >= limit) return false;
            count++;
            return true;
        }
    }

    static final class SlidingLog {
        private final long window; private final int limit; private final ArrayDeque<Long> admitted = new ArrayDeque<>();
        SlidingLog(long window, int limit) { this.window = window; this.limit = limit; }
        boolean tryAcquire(long now) {
            while (!admitted.isEmpty() && admitted.peekFirst() <= now - window) admitted.pollFirst();
            if (admitted.size() >= limit) return false;
            admitted.addLast(now);
            return true;
        }
    }

    /** Largest number of admitted requests in any closed interval of the given length (in ticks). `times` is sorted. */
    static int maxInInterval(long[] times, int n, long length) {
        int best = 0, lo = 0;
        for (int hi = 0; hi < n; hi++) {
            while (times[hi] - times[lo] > length) lo++;
            best = Math.max(best, hi - lo + 1);
        }
        return best;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java RateLimiters.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(55);
        for (int t = 0; t < 3000; t++) {                    // the bucket and GCRA are the same rule
            long T = 1 + rnd.nextInt(50), burst = 1 + rnd.nextInt(20);
            TokenBucket tb = new TokenBucket(T, burst, 0);
            Gcra g = new Gcra(T, burst, 0);
            long now = 0;
            for (int i = 0; i < 400; i++) {
                now += rnd.nextInt(4) == 0 ? rnd.nextInt((int) (3 * T) + 1) : rnd.nextInt(3);
                check(tb.tryAcquire(now) == g.tryAcquire(now), "token bucket and GCRA make the same decision, T = " + T + ", burst = " + burst);
            }
        }
        for (int t = 0; t < 1500; t++) {                    // token bucket: in any interval of length d it admits at most burst + floor(d / T)
            long T = 1 + rnd.nextInt(20), burst = 1 + rnd.nextInt(12);
            TokenBucket tb = new TokenBucket(T, burst, 0);
            long[] adm = new long[600];
            int n = 0;
            long now = 0;
            for (int i = 0; i < 1500 && n < adm.length; i++) {
                now += rnd.nextInt(5) == 0 ? rnd.nextInt((int) (2 * T) + 1) : rnd.nextInt(2);
                if (tb.tryAcquire(now)) adm[n++] = now;
            }
            for (int i = 0; i < n; i++) for (int j = i; j < n; j++) check(j - i + 1 <= burst + (adm[j] - adm[i]) / T, "token bucket never admits more than burst + d / T in an interval of length d");
        }
        int limit = 5;
        long window = 100;
        for (int t = 0; t < 1500; t++) {                    // random traffic: fixed window never exceeds twice its limit in a window-length interval, sliding log never exceeds the limit
            FixedWindow fw = new FixedWindow(window, limit);
            SlidingLog sl = new SlidingLog(window, limit);
            long[] a = new long[2000], b = new long[2000];
            int na = 0, nb = 0;
            long now = rnd.nextInt(1000);
            for (int i = 0; i < 4000; i++) {
                now += rnd.nextInt(10) == 0 ? rnd.nextInt(40) : rnd.nextInt(2);
                if (fw.tryAcquire(now) && na < a.length) a[na++] = now;
                if (sl.tryAcquire(now) && nb < b.length) b[nb++] = now;
            }
            check(maxInInterval(a, na, window - 1) <= 2 * limit, "fixed window: at most 2 x limit in any window-length interval");
            check(maxInInterval(b, nb, window - 1) <= limit, "sliding log: at most the limit in any window-length interval");
        }
        // the burst across a window boundary: quiet, then dense traffic around the boundary
        FixedWindow fw = new FixedWindow(1000, 100);
        SlidingLog sl = new SlidingLog(1000, 100);
        TokenBucket tb100 = new TokenBucket(10, 100, 0), tb10 = new TokenBucket(10, 10, 0);
        long[] f = new long[400], s = new long[400], k100 = new long[400], k10 = new long[400];
        int nf = 0, ns = 0, n100 = 0, n10 = 0;
        for (long now = 0; now < 2000; now++) {
            if (now < 900 || now >= 1100) continue;
            if (fw.tryAcquire(now)) f[nf++] = now;
            if (sl.tryAcquire(now)) s[ns++] = now;
            if (tb100.tryAcquire(now)) k100[n100++] = now;
            if (tb10.tryAcquire(now)) k10[n10++] = now;
        }
        check(nf == 200 && f[0] == 900 && f[nf - 1] == 1099, "fixed window admits 200 requests within 200 ms around the boundary, limit 100 per 1000 ms");
        check(ns == 100 && n100 == 100 + (k100[n100 - 1] - k100[0]) / 10 && n10 == 10 + (k10[n10 - 1] - k10[0]) / 10, "sliding log admits 100; a token bucket admits exactly burst + span / 10");
        check(n100 == 119 && n10 == 29, "token bucket with burst 100 admits 119, with burst 10 admits 29");
        System.out.printf("limit 100 per 1000 ms, silence until 900 ms then a request every millisecond until 1100 ms: fixed window admitted %d (all within %d ms), sliding log %d, token bucket (100 per second) with burst 100 admitted %d, with burst 10 admitted %d%n",
                nf, f[nf - 1] - f[0] + 1, ns, n100, n10);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("RateLimiters: " + passed + " checks passed");
    }
}
