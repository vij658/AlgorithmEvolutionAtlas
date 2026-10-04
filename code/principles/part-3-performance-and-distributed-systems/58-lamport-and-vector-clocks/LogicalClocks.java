import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 58 of the principles catalog (Part 3): Lamport clocks and vector clocks
 *
 * HOW IT WORKS
 *   Lamport clocks give every event a number consistent with causality (if a happened before b, L(a) < L(b)),
 *   but equal ordering says nothing about concurrency. Vector clocks keep one counter per process and can tell
 *   'before', 'after' and 'concurrent' apart.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LogicalClocks.java
 *   Expected: the output in expected-output.txt, ending "LogicalClocks: 32834516 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class LogicalClocks {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class LamportClock {
        private int time;
        int tick() { return ++time; }                                // local event or send: the timestamp to attach to the message
        int receive(int remote) { time = Math.max(time, remote) + 1; return time; }
    }

    static final class VectorClock {
        private final int[] v;
        private final int self;
        VectorClock(int processes, int self) { v = new int[processes]; this.self = self; }
        int[] tick() { v[self]++; return v.clone(); }                // local event or send: the vector to attach
        int[] receive(int[] remote) {
            for (int i = 0; i < v.length; i++) v[i] = Math.max(v[i], remote[i]);
            v[self]++;
            return v.clone();
        }
    }

    static final class Execution {
        int[] lamport; int[][] vector; boolean[][] before; int events;
    }

    /** A random run of `processes` processes: internal events, sends and receives, with messages delivered in random order. Events are numbered in a causal order. */
    static Execution randomExecution(int processes, int events, Random rnd) {
        Execution ex = new Execution();
        ex.events = events;
        ex.lamport = new int[events];
        ex.vector = new int[events][];
        ex.before = new boolean[events][events];
        int[] last = new int[processes];
        Arrays.fill(last, -1);
        LamportClock[] lamportClocks = new LamportClock[processes];
        VectorClock[] vectorClocks = new VectorClock[processes];
        for (int i = 0; i < processes; i++) { lamportClocks[i] = new LamportClock(); vectorClocks[i] = new VectorClock(processes, i); }
        ArrayList<int[]> inFlight = new ArrayList<>();      // {send event, destination process}
        for (int e = 0; e < events; e++) {
            int[] msg = null;
            int p;
            if (!inFlight.isEmpty() && rnd.nextInt(3) == 0) { msg = inFlight.remove(rnd.nextInt(inFlight.size())); p = msg[1]; }
            else p = rnd.nextInt(processes);
            ex.lamport[e] = msg == null ? lamportClocks[p].tick() : lamportClocks[p].receive(ex.lamport[msg[0]]);
            ex.vector[e] = msg == null ? vectorClocks[p].tick() : vectorClocks[p].receive(ex.vector[msg[0]]);
            for (int x = 0; x < e; x++)
                ex.before[x][e] = (last[p] >= 0 && (x == last[p] || ex.before[x][last[p]])) || (msg != null && (x == msg[0] || ex.before[x][msg[0]]));
            last[p] = e;
            if (msg == null && processes > 1 && rnd.nextBoolean()) { int to = rnd.nextInt(processes - 1); if (to >= p) to++; inFlight.add(new int[]{e, to}); }   // this event is a send
        }
        return ex;
    }

    static boolean vectorLess(int[] a, int[] b) {
        boolean strictly = false;
        for (int i = 0; i < a.length; i++) { if (a[i] > b[i]) return false; if (a[i] < b[i]) strictly = true; }
        return strictly;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java LogicalClocks.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(58);
        long causal = 0, concurrent = 0, lamportOrders = 0, lamportTies = 0, runs = 3000;
        for (int t = 0; t < runs; t++) {
            int processes = 2 + rnd.nextInt(6), events = 10 + rnd.nextInt(110);
            Execution ex = randomExecution(processes, events, rnd);
            for (int x = 0; x < events; x++) for (int y = x + 1; y < events; y++) {
                boolean hb = ex.before[x][y];
                check(!ex.before[y][x], "event numbers follow causality");
                check(!hb || ex.lamport[x] < ex.lamport[y], "if a happened before b, the Lamport clock of a is smaller");
                check(vectorLess(ex.vector[x], ex.vector[y]) == hb, "vector clocks: V(a) < V(b) exactly when a happened before b");
                check(!vectorLess(ex.vector[y], ex.vector[x]), "a later-numbered event is never vector-smaller");
                if (hb) causal++;
                else {
                    concurrent++;
                    check(!vectorLess(ex.vector[x], ex.vector[y]) && !vectorLess(ex.vector[y], ex.vector[x]), "concurrent events have incomparable vector clocks");
                    if (ex.lamport[x] != ex.lamport[y]) lamportOrders++; else lamportTies++;
                }
            }
        }
        check(concurrent > 0 && lamportOrders > 0.7 * concurrent, "Lamport clocks rank most concurrent pairs as if one came first");
        System.out.printf("%d random runs, %,d event pairs: %,d causally ordered, %,d concurrent; Lamport clocks gave the concurrent pairs different numbers in %.1f%% of cases (they cannot say 'concurrent'), vector clocks identified every one of them%n",
                runs, causal + concurrent, causal, concurrent, 100.0 * lamportOrders / concurrent);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("LogicalClocks: " + passed + " checks passed");
    }
}
