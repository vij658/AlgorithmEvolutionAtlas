import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 60 of the principles catalog (Part 3): Idempotency keys
 *
 * HOW IT WORKS
 *   A client sends the same idempotency key with every retry of an operation; the server records the key and
 *   its result so a retry returns the stored result instead of acting twice. The key and the effect must be
 *   committed together, or crashes cause duplicates or losses.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Idempotency.java
 *   Expected: the output in expected-output.txt, ending "Idempotency: 516 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Idempotency {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class IdempotentStore {
        record Entry(String fingerprint, CompletableFuture<String> response) {}
        private final ConcurrentHashMap<String, Entry> entries = new ConcurrentHashMap<>();
        final AtomicInteger executions = new AtomicInteger();
        /** Runs `effect` once per key. Repeats with the same key and request replay the stored answer; a repeat with a different request is refused. */
        String execute(String key, String fingerprint, Supplier<String> effect) {
            Entry mine = new Entry(fingerprint, new CompletableFuture<>());
            Entry first = entries.putIfAbsent(key, mine);
            if (first != null) {
                if (!first.fingerprint().equals(fingerprint)) throw new IllegalArgumentException("idempotency key reused with a different request");
                return first.response().join();             // replay the stored answer (this waits if the first call is still running)
            }
            executions.incrementAndGet();
            try { String response = effect.get(); mine.response().complete(response); return response; }
            catch (RuntimeException e) { mine.response().completeExceptionally(e); throw e; }
        }
    }

    static final int NO_KEY = 0, RECORD_THEN_EFFECT = 1, EFFECT_THEN_RECORD = 2, ONE_TRANSACTION = 3;

    static final String[] IDEMPOTENCY_NAMES = {"no idempotency key", "record the key, then do the work", "do the work, then record the key", "work and key in one transaction"};

    /** A client retries (same key) until it sees an answer. Every attempt crashes before its first step with probability 0.1, between the two steps with probability 0.1,
     *  and loses its answer with probability 0.1. Returns {requests done exactly once, done more than once, never done}. */
    static int[] payments(int design, int requests, Random rnd) {
        int[] effects = new int[requests];
        boolean[] recorded = new boolean[requests];
        for (int id = 0; id < requests; id++) {
            for (int attempt = 0; attempt < 100; attempt++) {
                boolean answered = false;
                if (rnd.nextDouble() < 0.1) { /* crashed before doing anything */ }
                else if (design == NO_KEY) { effects[id]++; answered = true; }
                else if (recorded[id]) { answered = true; }                                   // replay: the key says it is done
                else if (design == ONE_TRANSACTION) { effects[id]++; recorded[id] = true; answered = true; }
                else if (design == RECORD_THEN_EFFECT) { recorded[id] = true; if (rnd.nextDouble() >= 0.1) { effects[id]++; answered = true; } }
                else { effects[id]++; if (rnd.nextDouble() >= 0.1) { recorded[id] = true; answered = true; } }
                if (answered && rnd.nextDouble() >= 0.1) break;                                // answer arrives
            }
        }
        int once = 0, twice = 0, never = 0;
        for (int e : effects) { if (e == 1) once++; else if (e > 1) twice++; else never++; }
        return new int[]{once, twice, never};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Idempotency.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() throws Exception {
        IdempotentStore store = new IdempotentStore();
        check(store.execute("k1", "pay 10 to bob", () -> "charged").equals("charged") && store.execute("k1", "pay 10 to bob", () -> "charged again").equals("charged") && store.executions.get() == 1, "a repeat with the same key replays the first answer without running the work again");
        try { store.execute("k1", "pay 99 to eve", () -> "charged"); check(false, "a key reused for a different request must be refused"); }
        catch (IllegalArgumentException expected) { passed++; }
        for (int round = 0; round < 30; round++) {          // 32 threads race with one key: 16 send the same request, 16 send a different one
            IdempotentStore s = new IdempotentStore();
            ExecutorService pool = Executors.newFixedThreadPool(32);
            CountDownLatch go = new CountDownLatch(1);
            List<Future<String>> results = new ArrayList<>();
            for (int i = 0; i < 32; i++) {
                String fingerprint = i % 2 == 0 ? "pay 10" : "pay 20";
                results.add(pool.submit(() -> { go.await(); return s.execute("race", fingerprint, () -> "charged " + fingerprint); }));
            }
            go.countDown();
            int refused = 0;
            Set<String> answers = new HashSet<>();
            for (Future<String> f : results) {
                try { answers.add(f.get(30, TimeUnit.SECONDS)); }
                catch (ExecutionException e) { check(e.getCause() instanceof IllegalArgumentException, "the only failure is the refusal"); refused++; }
            }
            pool.shutdown();
            check(s.executions.get() == 1 && refused == 16 && answers.size() == 1, "one execution, one stored answer, 16 refusals, got " + s.executions.get() + " " + refused + " " + answers);
        }
        Random rnd = new Random(60);
        int requests = 200_000;
        StringBuilder sb = new StringBuilder();
        int[][] out = new int[4][];
        for (int d = 0; d < 4; d++) {
            out[d] = payments(d, requests, rnd);
            sb.append(String.format("%s: %.2f%% exactly once, %.2f%% more than once, %.2f%% never; ", IDEMPOTENCY_NAMES[d], 100.0 * out[d][0] / requests, 100.0 * out[d][1] / requests, 100.0 * out[d][2] / requests));
        }
        check(out[NO_KEY][1] > 0.05 * requests && out[NO_KEY][2] == 0, "retries without a key duplicate work");
        check(out[RECORD_THEN_EFFECT][2] > 0.01 * requests && out[RECORD_THEN_EFFECT][1] == 0, "recording first loses work");
        check(out[EFFECT_THEN_RECORD][1] > 0.01 * requests && out[EFFECT_THEN_RECORD][2] == 0, "recording last duplicates work");
        check(out[ONE_TRANSACTION][0] == requests, "one transaction: every request done exactly once");
        System.out.println(requests + " requests, clients retry until they see an answer, 10% crash before the work, 10% crash between work and record, 10% of answers lost: " + sb);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("Idempotency: " + passed + " checks passed");
    }
}
