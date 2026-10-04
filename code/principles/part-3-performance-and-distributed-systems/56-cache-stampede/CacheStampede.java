import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 56 of the principles catalog (Part 3): Cache stampede: single flight and early recomputation
 *
 * HOW IT WORKS
 *   When a hot cache entry expires, many requests rebuild it at once. Single flight lets one caller rebuild
 *   while the others wait; probabilistic early recomputation (XFetch) refreshes slightly before expiry, with a
 *   chance that rises as expiry nears.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CacheStampede.java
 *   Expected: the output in expected-output.txt, ending "CacheStampede: 687 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class CacheStampede {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    static double exponential(Random rnd, double mean) { return -mean * Math.log(1 - rnd.nextDouble()); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class SingleFlight<K, V> {
        private final ConcurrentHashMap<K, CompletableFuture<V>> inFlight = new ConcurrentHashMap<>();
        final AtomicInteger loads = new AtomicInteger(), coalesced = new AtomicInteger();
        V get(K key, Supplier<V> loader) {
            CompletableFuture<V> mine = new CompletableFuture<>();
            CompletableFuture<V> theirs = inFlight.putIfAbsent(key, mine);
            if (theirs != null) { coalesced.incrementAndGet(); return theirs.join(); }      // someone is already loading this key: wait for their answer
            loads.incrementAndGet();
            try {
                V value = loader.get();
                mine.complete(value);
                return value;
            } catch (RuntimeException e) {
                mine.completeExceptionally(e);
                throw e;
            } finally {
                inFlight.remove(key, mine);
            }
        }
    }

    static final int NAIVE = 0, XFETCH = 1, SINGLE_FLIGHT = 2, BOTH = 3;           // bit 0: refresh early, bit 1: join a load that is already running

    static final String[] STAMPEDE_NAMES = {"plain TTL", "XFetch (beta = 1)", "single flight", "XFetch + single flight"};

    /** XFetch: should this request refresh a value that expires at `expiry`? `delta` is how long a refresh takes. The closer to expiry, the likelier. */
    static boolean refreshEarly(double now, double expiry, double delta, double beta, Random rnd) {
        return now - delta * beta * Math.log(1 - rnd.nextDouble()) >= expiry;
    }

    /** One hot key in virtual time. Requests arrive at `rate` per second; a value lives `ttl` seconds after its load finishes; a load takes `load` seconds.
     *  A refresh cycle starts when a load begins while none is running. Returns {loads per cycle, requests that had to wait per cycle,
     *  most loads running at once, requests that found no value at all per cycle, number of cycles}. */
    static double[] stampede(int strategy, double rate, double ttl, double load, double beta, double seconds, Random rnd) {
        PriorityQueue<Double> finishing = new PriorityQueue<>();
        double validUntil = ttl, t = 0;                     // start with a value that was loaded at time 0, so the first cycle is typical too
        long loads = 0, waited = 0, empty = 0, cycles = 0;
        int peak = 0;
        while (t < seconds) {
            t += exponential(rnd, 1 / rate);
            while (!finishing.isEmpty() && finishing.peek() <= t) validUntil = finishing.poll() + ttl;
            boolean start = false, early = (strategy & 1) != 0, coalesce = (strategy & 2) != 0;
            if (t < validUntil) {
                if (early && (!coalesce || finishing.isEmpty()) && refreshEarly(t, validUntil, load, beta, rnd)) {    // this request volunteers to refresh early
                    start = true; waited++;
                }
            } else {
                empty++;
                if (coalesce && !finishing.isEmpty()) waited++;      // join the load that is already running
                else { start = true; waited++; }
            }
            if (start) {
                if (finishing.isEmpty()) cycles++;
                loads++;
                finishing.add(t + load);
            }
            peak = Math.max(peak, finishing.size());
        }
        return new double[]{loads / (double) cycles, waited / (double) cycles, peak, empty / (double) cycles, cycles};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java CacheStampede.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() throws Exception {
        // real threads: 32 callers ask for the same missing key while the loader is running; the loader finishes only after all 31 others have joined it
        for (int round = 0; round < 20; round++) {
            SingleFlight<String, String> sf = new SingleFlight<>();
            int callers = 32;
            ExecutorService pool = Executors.newFixedThreadPool(callers);
            CountDownLatch go = new CountDownLatch(1);
            List<Future<String>> results = new ArrayList<>();
            for (int i = 0; i < callers; i++) results.add(pool.submit(() -> {
                go.await();
                return sf.get("hot", () -> {
                    long deadline = System.nanoTime() + 10_000_000_000L;
                    while (sf.coalesced.get() < callers - 1) {
                        if (System.nanoTime() > deadline) throw new IllegalStateException("callers never joined");
                        Thread.yield();
                    }
                    return "value";
                });
            }));
            go.countDown();
            for (Future<String> r : results) check(r.get(30, TimeUnit.SECONDS).equals("value"), "every caller gets the loaded value");
            pool.shutdown();
            check(sf.loads.get() == 1 && sf.coalesced.get() == callers - 1, "32 concurrent callers cause exactly one load, got " + sf.loads.get());
            check(sf.get("hot", () -> "again").equals("again") && sf.loads.get() == 2, "once the load is over, the next call loads again");
        }
        SingleFlight<String, String> failing = new SingleFlight<>();
        try { failing.get("k", () -> { throw new IllegalStateException("backend down"); }); check(false, "the loader's exception must propagate"); }
        catch (IllegalStateException expected) { passed++; }
        check(failing.get("k", () -> "recovered").equals("recovered"), "a failed load is not cached: the next call tries again");

        double rate = 1000, ttl = 30, load = 0.5, seconds = 9000;
        double[][] r = new double[4][];
        for (int s = 0; s < 4; s++) r[s] = stampede(s, rate, ttl, load, 1.0, seconds, new Random(5600 + s));
        check(rel(r[NAIVE][0], rate * load + 1, 0.1) && r[NAIVE][2] > 0.8 * rate * load, "plain TTL: about rate x load = 500 duplicate loads per expiry, got " + Arrays.toString(r[NAIVE]));
        check(r[SINGLE_FLIGHT][0] == 1.0 && r[SINGLE_FLIGHT][2] == 1 && rel(r[SINGLE_FLIGHT][1], rate * load + 1, 0.1), "single flight: one load per cycle, but everyone who arrives meanwhile waits");
        check(r[XFETCH][0] < 5 && r[XFETCH][1] == r[XFETCH][0] && r[XFETCH][3] == 0 && r[XFETCH][2] < 0.1 * r[NAIVE][2], "XFetch: a handful of loads, nobody finds an empty cache, got " + Arrays.toString(r[XFETCH]));
        check(r[BOTH][0] == 1.0 && r[BOTH][1] == 1.0 && r[BOTH][2] == 1 && r[BOTH][3] == 0, "XFetch with single flight: one load per cycle, one request pays for it, nobody finds an empty cache, got " + Arrays.toString(r[BOTH]));
        double[] bigBeta = stampede(XFETCH, rate, ttl, load, 2.0, seconds, new Random(5699));
        check(bigBeta[3] == 0 && bigBeta[0] < r[NAIVE][0] / 50, "a larger beta also works");
        StringBuilder sb = new StringBuilder();
        for (int s = 0; s < 4; s++) sb.append(String.format("%s: %.1f loads per cycle (%.0f cycles), %.1f requests waited, at most %.0f loads at once, %.1f requests found no value; ", STAMPEDE_NAMES[s], r[s][0], r[s][4], r[s][1], r[s][2], r[s][3]));
        System.out.println("one hot key, 1000 requests/s, TTL 30 s, a load takes 0.5 s, 9000 s of traffic: " + sb + String.format("XFetch with beta = 2: %.1f loads per cycle", bigBeta[0]));
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("CacheStampede: " + passed + " checks passed");
    }
}
