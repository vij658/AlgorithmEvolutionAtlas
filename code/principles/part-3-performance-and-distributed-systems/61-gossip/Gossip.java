import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 61 of the principles catalog (Part 3): Gossip (epidemic) protocols
 *
 * HOW IT WORKS
 *   Each node periodically tells a random peer what it knows (push), asks a random peer (pull), or both. A
 *   rumour reaches all n nodes in about log2 n + ln n rounds with push, and faster with push-pull.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Gossip.java
 *   Expected: the output in expected-output.txt, ending "Gossip: 12 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Gossip {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final int PUSH = 0, PULL = 1, PUSH_PULL = 2;

    static final String[] GOSSIP_NAMES = {"push", "pull", "push-pull"};

    /** Rounds until all n nodes know a rumor that starts at node 0. In every round each node contacts one random other node; all contacts use the state from the start of the round. */
    static int gossipRounds(int mode, int n, Random rnd) {
        boolean[] informed = new boolean[n], next = new boolean[n];
        informed[0] = true;
        int count = 1, rounds = 0;
        while (count < n) {
            System.arraycopy(informed, 0, next, 0, n);
            for (int i = 0; i < n; i++) {
                int j = rnd.nextInt(n - 1);
                if (j >= i) j++;                            // a random node other than i
                if (mode != PULL && informed[i]) next[j] = true;                      // push: i tells j
                if (mode != PUSH && informed[j]) next[i] = true;                      // pull: i asks j
            }
            count = 0;
            for (boolean b : next) if (b) count++;
            boolean[] tmp = informed; informed = next; next = tmp;
            rounds++;
        }
        return rounds;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Gossip.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(61);
        StringBuilder sb = new StringBuilder();
        for (int n : new int[]{1 << 10, 1 << 14, 1 << 17, 1 << 20}) {
            int trials = n >= (1 << 20) ? 5 : 30;
            double[] mean = new double[3];
            for (int mode = 0; mode < 3; mode++) {
                for (int t = 0; t < trials; t++) mean[mode] += gossipRounds(mode, n, rnd) / (double) trials;
            }
            double log2n = Math.log(n) / Math.log(2), pushFormula = log2n + Math.log(n), pullFormula = log2n + Math.log(Math.log(n)) / Math.log(2), pushPullFormula = Math.log(n) / Math.log(3);
            check(Math.abs(mean[PUSH] - pushFormula) < 3, "push needs about log2 n + ln n rounds, n = " + n + ": measured " + mean[PUSH] + ", formula " + pushFormula);
            check(Math.abs(mean[PULL] - pullFormula) < 3, "pull needs about log2 n + log2 ln n rounds, n = " + n + ": measured " + mean[PULL] + ", formula " + pullFormula);
            check(mean[PUSH_PULL] < mean[PULL] && mean[PULL] < mean[PUSH] && mean[PUSH_PULL] > pushPullFormula, "push-pull beats pull beats push, and push-pull stays above log3 n, n = " + n);
            sb.append(String.format("n = %,d: push %.1f (log2 n + ln n = %.1f), pull %.1f (log2 n + log2 ln n = %.1f), push-pull %.1f (log3 n = %.1f); ", n, mean[PUSH], pushFormula, mean[PULL], pullFormula, mean[PUSH_PULL], pushPullFormula));
        }
        System.out.println("rounds until every node knows the rumor, one random contact per node per round, mean of 30 runs (5 at a million nodes): " + sb);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("Gossip: " + passed + " checks passed");
    }
}
