import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 59 of the principles catalog (Part 3): CRDTs (conflict-free replicated data types)
 *
 * HOW IT WORKS
 *   Conflict-free replicated data types merge with an operation that is commutative, associative and
 *   idempotent, so replicas that have seen the same updates converge in any order. The program covers counters,
 *   sets and registers, and the trap of last-writer-wins with clock skew.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Crdts.java
 *   Expected: the output in expected-output.txt, ending "Crdts: 16808 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Crdts {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static double gaussian(Random rnd) {                       // Box-Muller from nextDouble, so results do not depend on the JDK's nextGaussian
        double u1 = 1 - rnd.nextDouble(), u2 = rnd.nextDouble();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class GCounter {
        final long[] slots;
        GCounter(int replicas) { slots = new long[replicas]; }
        void increment(int replica, long by) { slots[replica] += by; }
        long value() { long s = 0; for (long v : slots) s += v; return s; }
        GCounter merge(GCounter o) { GCounter g = new GCounter(slots.length); for (int i = 0; i < slots.length; i++) g.slots[i] = Math.max(slots[i], o.slots[i]); return g; }
        @Override public boolean equals(Object o) { return o instanceof GCounter g && Arrays.equals(slots, g.slots); }
        @Override public int hashCode() { return Arrays.hashCode(slots); }
    }

    static final class PNCounter {
        final GCounter up, down;
        PNCounter(int replicas) { up = new GCounter(replicas); down = new GCounter(replicas); }
        PNCounter(GCounter u, GCounter d) { up = u; down = d; }
        void add(int replica, long delta) { if (delta >= 0) up.increment(replica, delta); else down.increment(replica, -delta); }
        long value() { return up.value() - down.value(); }
        PNCounter merge(PNCounter o) { return new PNCounter(up.merge(o.up), down.merge(o.down)); }
        @Override public boolean equals(Object o) { return o instanceof PNCounter c && up.equals(c.up) && down.equals(c.down); }
        @Override public int hashCode() { return Objects.hash(up, down); }
    }

    /** Observed-remove set: every add gets a unique tag; a remove deletes only the tags this replica has seen. Merge is union of both sets. */
    static final class OrSet {
        final TreeMap<Integer, TreeSet<Long>> adds = new TreeMap<>();
        final TreeSet<Long> removed = new TreeSet<>();
        void add(int element, long tag) { adds.computeIfAbsent(element, k -> new TreeSet<>()).add(tag); }
        void remove(int element) { removed.addAll(adds.getOrDefault(element, new TreeSet<>())); }
        boolean contains(int element) { for (long tag : adds.getOrDefault(element, new TreeSet<>())) if (!removed.contains(tag)) return true; return false; }
        TreeSet<Integer> value() { TreeSet<Integer> v = new TreeSet<>(); for (int e : adds.keySet()) if (contains(e)) v.add(e); return v; }
        OrSet merge(OrSet o) {
            OrSet m = new OrSet();
            for (OrSet s : new OrSet[]{this, o}) { for (var en : s.adds.entrySet()) for (long tag : en.getValue()) m.add(en.getKey(), tag); m.removed.addAll(s.removed); }
            return m;
        }
        @Override public boolean equals(Object o) { return o instanceof OrSet s && adds.equals(s.adds) && removed.equals(s.removed); }
        @Override public int hashCode() { return Objects.hash(adds, removed); }
    }

    /** Last-writer-wins register: the larger (timestamp, replica) pair wins. */
    static final class Lww {
        final long timestamp; final int replica; final String value;
        Lww(long timestamp, int replica, String value) { this.timestamp = timestamp; this.replica = replica; this.value = value; }
        Lww merge(Lww o) { return (o.timestamp > timestamp || (o.timestamp == timestamp && o.replica > replica)) ? o : this; }
        @Override public boolean equals(Object o) { return o instanceof Lww l && timestamp == l.timestamp && replica == l.replica && value.equals(l.value); }
        @Override public int hashCode() { return Objects.hash(timestamp, replica, value); }
    }

    static final class TwoPhaseSet {                        // add set and remove set; a removed element can never come back
        final TreeSet<Integer> added = new TreeSet<>(), tombstones = new TreeSet<>();
        void add(int e) { added.add(e); }
        void remove(int e) { if (added.contains(e)) tombstones.add(e); }
        boolean contains(int e) { return added.contains(e) && !tombstones.contains(e); }
    }

    static double bigPhi(double x) {                         // standard normal distribution function by Simpson's rule
        int steps = 20_000;
        double h = x / steps, sum = Math.exp(0) + Math.exp(-x * x / 2);
        for (int i = 1; i < steps; i++) sum += Math.exp(-(i * h) * (i * h) / 2) * (i % 2 == 1 ? 4 : 2);
        return 0.5 + sum * h / 3 / Math.sqrt(2 * Math.PI);
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Crdts.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(59);
        int replicas = 4;
        for (int t = 0; t < 3000; t++) {                    // merge is commutative, associative and idempotent on arbitrary reachable states
            GCounter[] g = new GCounter[3]; PNCounter[] pn = new PNCounter[3]; OrSet[] os = new OrSet[3]; Lww[] lw = new Lww[3];
            long tag = 0;
            for (int i = 0; i < 3; i++) {
                g[i] = new GCounter(replicas); pn[i] = new PNCounter(replicas); os[i] = new OrSet(); lw[i] = new Lww(0, i, "init");
                long clock = rnd.nextInt(30);
                for (int k = 0; k < 12; k++) {
                    int r = rnd.nextInt(replicas), e = rnd.nextInt(6);
                    g[i].increment(r, rnd.nextInt(5)); pn[i].add(r, rnd.nextInt(9) - 4);
                    if (rnd.nextInt(3) == 0) os[i].remove(e); else os[i].add(e, ++tag * 10 + i);
                    clock += 1 + rnd.nextInt(3);            // replica i never reuses a timestamp, so (timestamp, replica) identifies a write
                    lw[i] = lw[i].merge(new Lww(clock, i, "v" + rnd.nextInt(100)));
                }
            }
            check(g[0].merge(g[1]).equals(g[1].merge(g[0])) && g[0].merge(g[1]).merge(g[2]).equals(g[0].merge(g[1].merge(g[2]))) && g[0].merge(g[0]).equals(g[0]), "G-Counter merge: commutative, associative, idempotent");
            check(pn[0].merge(pn[1]).equals(pn[1].merge(pn[0])) && pn[0].merge(pn[1]).merge(pn[2]).equals(pn[0].merge(pn[1].merge(pn[2]))) && pn[0].merge(pn[0]).equals(pn[0]), "PN-Counter merge: commutative, associative, idempotent");
            check(os[0].merge(os[1]).equals(os[1].merge(os[0])) && os[0].merge(os[1]).merge(os[2]).equals(os[0].merge(os[1].merge(os[2]))) && os[0].merge(os[0]).equals(os[0]), "OR-Set merge: commutative, associative, idempotent");
            check(lw[0].merge(lw[1]).equals(lw[1].merge(lw[0])) && lw[0].merge(lw[1]).merge(lw[2]).equals(lw[0].merge(lw[1].merge(lw[2]))) && lw[0].merge(lw[0]).equals(lw[0]), "LWW register merge: commutative, associative, idempotent");
        }
        for (int t = 0; t < 400; t++) {                     // convergence: replicas update locally and exchange stale, duplicated, reordered states; in the end they agree
            GCounter[] g = new GCounter[replicas]; PNCounter[] pn = new PNCounter[replicas]; OrSet[] os = new OrSet[replicas];
            for (int i = 0; i < replicas; i++) { g[i] = new GCounter(replicas); pn[i] = new PNCounter(replicas); os[i] = new OrSet(); }
            ArrayList<GCounter> oldG = new ArrayList<>(); ArrayList<PNCounter> oldPn = new ArrayList<>(); ArrayList<OrSet> oldOs = new ArrayList<>();
            long increments = 0, net = 0, tag = 0;
            TreeSet<Long> allAdds = new TreeSet<>(), observedRemoves = new TreeSet<>();
            TreeMap<Long, Integer> tagElement = new TreeMap<>();
            for (int step = 0; step < 60; step++) {
                int r = rnd.nextInt(replicas);
                switch (rnd.nextInt(4)) {
                    case 0 -> { int by = rnd.nextInt(4); g[r].increment(r, by); increments += by; }
                    case 1 -> { int d = rnd.nextInt(9) - 4; pn[r].add(r, d); net += d; }
                    case 2 -> { int e = rnd.nextInt(5); long tg = ++tag * 10 + r; os[r].add(e, tg); allAdds.add(tg); tagElement.put(tg, e); }
                    default -> { int e = rnd.nextInt(5); observedRemoves.addAll(os[r].adds.getOrDefault(e, new TreeSet<>())); os[r].remove(e); }
                }
                if (rnd.nextInt(3) == 0) {                  // a state snapshot is sent somewhere (possibly an old one, possibly twice)
                    int to = rnd.nextInt(replicas);
                    oldG.add(g[r]); oldPn.add(pn[r]); oldOs.add(os[r]);
                    int pick = rnd.nextInt(oldG.size());
                    g[to] = g[to].merge(oldG.get(pick)); pn[to] = pn[to].merge(oldPn.get(pick)); os[to] = os[to].merge(oldOs.get(pick));
                }
            }
            for (int round = 0; round < 2; round++) for (int a = 0; a < replicas; a++) for (int b = 0; b < replicas; b++) { g[a] = g[a].merge(g[b]); pn[a] = pn[a].merge(pn[b]); os[a] = os[a].merge(os[b]); }
            TreeSet<Integer> expected = new TreeSet<>();
            for (long tg : allAdds) if (!observedRemoves.contains(tg)) expected.add(tagElement.get(tg));
            for (int i = 0; i < replicas; i++) {
                check(g[i].equals(g[0]) && pn[i].equals(pn[0]) && os[i].equals(os[0]), "all replicas converge to the same state");
                check(g[i].value() == increments && pn[i].value() == net, "counters converge to the sum of all updates");
                check(os[i].value().equals(expected), "the OR-Set holds exactly the elements with an add that no remove had seen");
            }
        }
        OrSet a = new OrSet(), b = new OrSet();
        a.add(7, 1); b.add(7, 1);                           // both replicas know element 7 (the same add)
        a.remove(7);                                        // A removes it...
        b.add(7, 2);                                        // ...while B concurrently adds it again
        check(!a.contains(7) && a.merge(b).contains(7) && b.merge(a).contains(7), "OR-Set: a concurrent add beats a remove (add wins)");
        OrSet c = new OrSet();
        c.add(3, 1); c.remove(3); c.add(3, 2);
        check(c.contains(3), "OR-Set: an element can be re-added after a remove");
        TwoPhaseSet tp = new TwoPhaseSet();
        tp.add(3); tp.remove(3); tp.add(3);
        check(!tp.contains(3), "2P-Set: once removed, an element can never be added again");
        Lww x = new Lww(15_000, 1, "x"), y = new Lww(12_000, 0, "y");     // B's clock runs 5 s fast; A's write really came later
        check(x.merge(y).value.equals("x") && y.merge(x).value.equals("x"), "LWW with a clock 5 s fast: the causally later write is lost");
        StringBuilder sb = new StringBuilder();
        double sigma = 50;
        int trials = 1_000_000;
        for (double gap : new double[]{0, 50, 100, 200}) {
            int lost = 0;
            for (int i = 0; i < trials; i++) {
                Lww first = new Lww(Math.round(gaussian(rnd) * sigma * 1000), 1, "first");                       // timestamps in microseconds: skew of the first writer's clock
                Lww second = new Lww(Math.round((gap + gaussian(rnd) * sigma) * 1000), 0, "second");             // the second write is causally later by `gap` ms
                if (first.merge(second).value.equals("first")) lost++;
            }
            double formula = 1 - bigPhi(gap / (sigma * Math.sqrt(2)));
            check(close(lost / (double) trials, formula, 0.003), "LWW loss probability for a gap of " + gap + " ms: measured " + lost / (double) trials + ", formula " + formula);
            sb.append(String.format("gap %.0f ms: %.1f%% (formula %.1f%%); ", gap, 100.0 * lost / trials, 100 * formula));
        }
        System.out.println("last-writer-wins, clocks with independent skew of 50 ms standard deviation: share of causally ordered write pairs where the earlier write wins: " + sb);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("Crdts: " + passed + " checks passed");
    }
}
