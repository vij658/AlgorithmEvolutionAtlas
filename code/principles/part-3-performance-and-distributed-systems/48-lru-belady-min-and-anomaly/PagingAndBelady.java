import java.util.*;

/**
 * Entry 48 of the principles catalog (Part 3): LRU, Belady's MIN and Belady's anomaly
 *
 * HOW IT WORKS
 *   LRU evicts the least recently used page; Belady's MIN (evict the page used furthest in the future) is the
 *   optimal offline policy. FIFO can fault more with more memory (Belady's anomaly); stack algorithms such as
 *   LRU never do.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java PagingAndBelady.java
 *   Expected: the output in expected-output.txt, ending "PagingAndBelady: 3909 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class PagingAndBelady {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class LruCache<K> {                        // LinkedHashMap in access order evicts the least recently used entry
        private final LinkedHashMap<K, Boolean> map;
        LruCache(int capacity) {
            map = new LinkedHashMap<>(16, 0.75f, true) {
                @Override protected boolean removeEldestEntry(Map.Entry<K, Boolean> eldest) { return size() > capacity; }
            };
        }
        boolean access(K key) {                             // true on a hit
            boolean hit = map.get(key) != null;             // get() also marks the entry as most recently used
            if (!hit) map.put(key, Boolean.TRUE);
            return hit;
        }
    }

    static int lruHits(int[] trace, int capacity) {
        LruCache<Integer> cache = new LruCache<>(capacity);
        int hits = 0;
        for (int x : trace) if (cache.access(x)) hits++;
        return hits;
    }

    static int lruHitsSlow(int[] trace, int capacity) {     // list in recency order, for cross-checking
        ArrayList<Integer> list = new ArrayList<>();
        int hits = 0;
        for (int x : trace) {
            int at = list.indexOf(x);
            if (at >= 0) { hits++; list.remove(at); }
            else if (list.size() == capacity) list.remove(0);
            list.add(x);
        }
        return hits;
    }

    static int fifoHits(int[] trace, int capacity) {
        ArrayDeque<Integer> queue = new ArrayDeque<>();
        HashSet<Integer> resident = new HashSet<>();
        int hits = 0;
        for (int x : trace) {
            if (resident.contains(x)) { hits++; continue; }
            if (queue.size() == capacity) resident.remove(queue.poll());
            queue.add(x);
            resident.add(x);
        }
        return hits;
    }

    static int randomHits(int[] trace, int capacity, Random rnd) {
        ArrayList<Integer> slots = new ArrayList<>();
        HashSet<Integer> resident = new HashSet<>();
        int hits = 0;
        for (int x : trace) {
            if (resident.contains(x)) { hits++; continue; }
            if (slots.size() == capacity) {
                int v = rnd.nextInt(capacity);
                resident.remove(slots.get(v));
                slots.set(v, x);
            } else slots.add(x);
            resident.add(x);
        }
        return hits;
    }

    /** Belady's MIN: on a miss with a full cache, evict the resident item whose next use lies farthest in the future. */
    static int minHits(int[] trace, int capacity) {
        int n = trace.length;
        int[] nextUse = new int[n];
        HashMap<Integer, Integer> last = new HashMap<>();
        for (int i = n - 1; i >= 0; i--) { nextUse[i] = last.getOrDefault(trace[i], Integer.MAX_VALUE); last.put(trace[i], i); }
        TreeSet<Long> byNextUse = new TreeSet<>();          // key = nextUse << 32 | item, so the farthest next use is last()
        HashMap<Integer, Integer> resident = new HashMap<>();   // item -> its current next-use index
        int hits = 0;
        for (int i = 0; i < n; i++) {
            int item = trace[i];
            long low = item & 0xffffffffL;
            Integer old = resident.get(item);
            if (old != null) { hits++; byNextUse.remove(((long) old << 32) | low); }
            else if (resident.size() == capacity) {
                long far = byNextUse.pollLast();
                resident.remove((int) (far & 0xffffffffL));
            }
            resident.put(item, nextUse[i]);
            byNextUse.add(((long) nextUse[i] << 32) | low);
        }
        return hits;
    }

    static int bestHits(int[] trace, int i, int mask, int cap, HashMap<Long, Integer> memo) {   // exhaustive optimum for tiny traces
        if (i == trace.length) return 0;
        long key = ((long) i << 32) | mask;
        Integer cached = memo.get(key);
        if (cached != null) return cached;
        int bit = 1 << trace[i], best;
        if ((mask & bit) != 0) best = 1 + bestHits(trace, i + 1, mask, cap, memo);
        else if (Integer.bitCount(mask) < cap) best = bestHits(trace, i + 1, mask | bit, cap, memo);
        else {
            best = 0;
            for (int v = 0; v < 31; v++) if ((mask >> v & 1) == 1) best = Math.max(best, bestHits(trace, i + 1, (mask & ~(1 << v)) | bit, cap, memo));
        }
        memo.put(key, best);
        return best;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 47 (zipf-and-cache-sizing), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    /** Inverse-CDF sampling: binary search (entry 22) in the cumulative distribution. Returns zero-based ranks. */
    static int[] zipfSample(int items, double s, int count, Random rnd) {
        double[] cdf = new double[items];
        double acc = 0;
        for (int i = 0; i < items; i++) { acc += Math.pow(i + 1, -s); cdf[i] = acc; }
        int[] out = new int[count];
        for (int j = 0; j < count; j++) {
            double u = rnd.nextDouble() * acc;
            int lo = 0, hi = items - 1;
            while (lo < hi) { int mid = (lo + hi) >>> 1; if (cdf[mid] < u) lo = mid + 1; else hi = mid; }
            out[j] = lo;
        }
        return out;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java PagingAndBelady.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(48);
        for (int t = 0; t < 300; t++) {
            int[] trace = new int[500];
            for (int i = 0; i < trace.length; i++) trace[i] = rnd.nextInt(40);
            for (int cap : new int[]{1, 5, 20}) check(lruHits(trace, cap) == lruHitsSlow(trace, cap), "LinkedHashMap LRU matches a list-based LRU");
        }
        for (int t = 0; t < 3000; t++) {
            int[] trace = new int[1 + rnd.nextInt(14)];
            int distinct = 2 + rnd.nextInt(5);
            for (int i = 0; i < trace.length; i++) trace[i] = rnd.nextInt(distinct);
            int cap = 1 + rnd.nextInt(4);
            check(minHits(trace, cap) == bestHits(trace, 0, 0, cap, new HashMap<>()), "Belady's MIN equals the exhaustive optimum on tiny traces");
        }
        int[] classic = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
        int fifo3 = classic.length - fifoHits(classic, 3), fifo4 = classic.length - fifoHits(classic, 4);
        int lru3 = classic.length - lruHits(classic, 3), lru4 = classic.length - lruHits(classic, 4);
        check(fifo3 == 9 && fifo4 == 10, "Belady's anomaly: FIFO has more faults with 4 frames than with 3");
        check(lru4 <= lru3, "LRU never gets worse with more frames");
        System.out.println("Belady's anomaly on 1 2 3 4 1 2 5 1 2 3 4 5: FIFO faults " + fifo3 + " with 3 frames, " + fifo4 + " with 4; LRU faults " + lru3 + " and " + lru4);
        int anomalies = 0, lruViolations = 0, traces = 2000;
        for (int t = 0; t < traces; t++) {
            int[] trace = new int[60];
            for (int i = 0; i < trace.length; i++) trace[i] = rnd.nextInt(10);
            boolean fifoBad = false;
            for (int cap = 1; cap < 10; cap++) {
                if (fifoHits(trace, cap + 1) < fifoHits(trace, cap)) fifoBad = true;
                if (lruHits(trace, cap + 1) < lruHits(trace, cap)) lruViolations++;
            }
            if (fifoBad) anomalies++;
        }
        check(lruViolations == 0, "LRU has the stack property: a bigger cache never has fewer hits");
        check(anomalies > 0, "random traces do trigger FIFO's anomaly");
        System.out.println("on " + traces + " random traces of 60 requests over 10 items, a larger FIFO cache did worse for some size in " + anomalies + " traces; LRU did so in " + lruViolations);
        int[] zipf = zipfSample(10_000, 0.9, 200_000, rnd);
        StringBuilder sb = new StringBuilder();
        for (int cap : new int[]{100, 1000}) {
            int lru = lruHits(zipf, cap), fifo = fifoHits(zipf, cap), rand = randomHits(zipf, cap, rnd), min = minHits(zipf, cap);
            int fixed = 0;
            for (int r : zipf) if (r < cap) fixed++;            // keep the cap most popular items forever: the best online policy when requests are independent
            check(min >= lru && min >= fifo && min >= rand && min >= fixed, "MIN is at least as good as every online policy");
            check(fixed > lru && fixed > fifo && fixed > rand, "for independent requests, keeping the most popular items beats LRU, FIFO and random");
            sb.append(String.format("capacity %d: LRU %.1f%%, FIFO %.1f%%, random %.1f%%, top-%d kept forever %.1f%%, MIN %.1f%%; ", cap, 100.0 * lru / zipf.length, 100.0 * fifo / zipf.length, 100.0 * rand / zipf.length, cap, 100.0 * fixed / zipf.length, 100.0 * min / zipf.length));
        }
        System.out.println("hit rates on a Zipf(0.9) trace of 200,000 requests over 10,000 items: " + sb);
        int k = 100, rounds = 100;
        int[] loop = new int[(k + 1) * rounds];
        for (int i = 0; i < loop.length; i++) loop[i] = i % (k + 1);
        int lruLoop = lruHits(loop, k), fifoLoop = fifoHits(loop, k), randLoop = randomHits(loop, k, rnd), minLoop = minHits(loop, k);
        check(lruLoop == 0 && fifoLoop == 0 && minLoop > 0.9 * loop.length && randLoop > 0, "a loop one item larger than the cache defeats LRU and FIFO completely");
        System.out.printf("cycling through %d items with room for %d, %d requests: LRU %d hits, FIFO %d, random %.1f%%, MIN %.1f%%%n",
                k + 1, k, loop.length, lruLoop, fifoLoop, 100.0 * randLoop / loop.length, 100.0 * minLoop / loop.length);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("PagingAndBelady: " + passed + " checks passed");
    }
}
