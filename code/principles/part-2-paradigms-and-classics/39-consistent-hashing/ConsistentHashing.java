import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Entry 39 of the principles catalog (Part 2): Consistent hashing
 *
 * HOW IT WORKS
 *   Place servers and keys on the same hash ring; each key belongs to the next server clockwise. Adding or
 *   removing a server moves only the keys in its arc (about 1/n of them), and virtual nodes even out the load.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ConsistentHashing.java
 *   Expected: the output in expected-output.txt, ending "ConsistentHashing: 18523 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ConsistentHashing {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long mix(long z) {                              // splitmix64 finalizer: a strong 64-bit mixer
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    static long hashString(String s) {                     // FNV-1a, then the mixer
        long h = 0xcbf29ce484222325L;
        for (byte b : s.getBytes(StandardCharsets.UTF_8)) { h ^= (b & 0xff); h *= 0x100000001b3L; }
        return mix(h);
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class Ring {
        private final TreeMap<Long, String> ring = new TreeMap<>();
        private final int vnodes;
        Ring(int vnodes) { this.vnodes = vnodes; }
        void addNode(String node) { for (int i = 0; i < vnodes; i++) ring.put(hashString(node + "#" + i), node); }
        String nodeFor(String key) {
            Map.Entry<Long, String> e = ring.ceilingEntry(hashString(key));
            return (e != null ? e : ring.firstEntry()).getValue();   // wrap around the ring
        }
    }

    static double maxOverMean(Map<String, Integer> load, int nodes, int keys) {
        return Collections.max(load.values()) / ((double) keys / nodes);
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ConsistentHashing.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        int keys = 100_000;
        String[] keyNames = new String[keys];
        for (int i = 0; i < keys; i++) keyNames[i] = "key-" + i;
        int movedMod = 0;
        for (String k : keyNames) if (Math.floorMod(hashString(k), 10) != Math.floorMod(hashString(k), 11)) movedMod++;
        double fracMod = movedMod / (double) keys;
        check(fracMod > 0.88 && fracMod < 0.93, "modulo hashing moves about 10/11 of the keys");
        double[] fracRing = new double[2], balance = new double[2];
        int[] vn = {1, 200};
        for (int v = 0; v < 2; v++) {
            Ring ring = new Ring(vn[v]);
            for (int i = 0; i < 10; i++) ring.addNode("node-" + i);
            String[] before = new String[keys];
            Map<String, Integer> load = new HashMap<>();
            for (int i = 0; i < keys; i++) { before[i] = ring.nodeFor(keyNames[i]); load.merge(before[i], 1, Integer::sum); }
            balance[v] = maxOverMean(load, 10, keys);
            ring.addNode("node-10");
            int moved = 0;
            for (int i = 0; i < keys; i++) {
                String after = ring.nodeFor(keyNames[i]);
                if (!after.equals(before[i])) { moved++; check(after.equals("node-10"), "keys only ever move to the new node"); }
            }
            fracRing[v] = moved / (double) keys;
        }
        check(fracRing[1] > 0.07 && fracRing[1] < 0.115, "with 200 virtual nodes about 1/11 of the keys move, got " + fracRing[1]);
        check(balance[1] < balance[0], "virtual nodes improve balance");
        System.out.printf("10 -> 11 nodes, 100,000 keys: modulo hashing moved %.1f%% of keys; consistent hashing moved %.1f%% (200 virtual nodes) and %.1f%% (1 virtual node)%n",
                100 * fracMod, 100 * fracRing[1], 100 * fracRing[0]);
        System.out.printf("busiest node's load over the mean: %.2f with 200 virtual nodes per server, %.2f with 1%n", balance[1], balance[0]);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("ConsistentHashing: " + passed + " checks passed");
    }
}
