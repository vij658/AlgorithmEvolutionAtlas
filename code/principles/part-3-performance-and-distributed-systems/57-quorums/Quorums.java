import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.function.*;

/**
 * Entry 57 of the principles catalog (Part 3): Quorums: R + W > N
 *
 * HOW IT WORKS
 *   With N replicas, writes acknowledged by W and reads querying R, any read quorum overlaps any write quorum
 *   when R + W > N, so a read sees the latest acknowledged write. The program measures stale reads and
 *   availability for different (N, R, W).
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Quorums.java
 *   Expected: the output in expected-output.txt, ending "Quorums: 1001919 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Quorums {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long choose(int n, int k) {
        if (k < 0 || k > n) return 0;
        long r = 1;
        for (int i = 1; i <= k; i++) r = r * (n - k + i) / i;
        return r;
    }

    /** Chance that a read of R random replicas misses all W replicas that took the latest write. */
    static double staleProbability(int n, int r, int w) { return choose(n - w, r) / (double) choose(n, r); }

    /** Chance that at least k of n replicas are up when each is up independently with probability p. */
    static double atLeast(int n, int k, double p) {
        double sum = 0;
        for (int j = k; j <= n; j++) sum += choose(n, j) * Math.pow(p, j) * Math.pow(1 - p, n - j);
        return sum;
    }

    static int[] sample(int n, int k, Random rnd) {             // k distinct indices out of n (partial Fisher-Yates)
        int[] idx = new int[n];
        for (int i = 0; i < n; i++) idx[i] = i;
        for (int i = 0; i < k; i++) { int j = i + rnd.nextInt(n - i); int t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
        return Arrays.copyOf(idx, k);
    }

    /** n replicas, each holding a version number. A write reaches a random set of w replicas; a read asks a random set of r and keeps the highest version. */
    static final class Register {
        final int n; final int[] version; int latest;
        Register(int n) { this.n = n; version = new int[n]; }
        void write(int w, Random rnd) { latest++; for (int i : sample(n, w, rnd)) version[i] = latest; }
        int read(int r, Random rnd) { int best = 0; for (int i : sample(n, r, rnd)) best = Math.max(best, version[i]); return best; }
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Quorums.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        for (int n = 1; n <= 9; n++) {
            for (int r = 1; r <= n; r++) for (int w = 1; w <= n; w++) {
                long disjoint = 0, pairs = 0;
                for (int ws = 0; ws < (1 << n); ws++) {
                    if (Integer.bitCount(ws) != w) continue;
                    for (int rs = 0; rs < (1 << n); rs++) {
                        if (Integer.bitCount(rs) != r) continue;
                        pairs++;
                        if ((ws & rs) == 0) disjoint++;
                    }
                }
                check((disjoint == 0) == (r + w > n), "every read set meets every write set exactly when R + W > N, N = " + n + " R = " + r + " W = " + w);
                check(disjoint == choose(n, w) * choose(n - w, r) && pairs == choose(n, w) * choose(n, r), "counting disjoint pairs gives C(N-W, R) per write set");
                check(close(disjoint / (double) pairs, staleProbability(n, r, w), 1e-12), "stale probability is C(N-W, R) / C(N, R)");
            }
        }
        Random rnd = new Random(57);
        int[][] configs = {{3, 1, 1}, {3, 1, 2}, {3, 2, 1}, {3, 2, 2}, {5, 1, 1}, {5, 2, 2}, {5, 2, 3}, {5, 3, 3}, {7, 3, 3}, {7, 2, 2}};
        StringBuilder sb = new StringBuilder();
        for (int[] c : configs) {
            int n = c[0], r = c[1], w = c[2], trials = 400_000, stale = 0;
            for (int t = 0; t < trials; t++) {
                Register reg = new Register(n);
                reg.write(w, rnd);
                if (reg.read(r, rnd) < reg.latest) stale++;
            }
            double formula = staleProbability(n, r, w), measured = stale / (double) trials;
            check(close(measured, formula, 0.004), "stale reads right after one write, N R W = " + Arrays.toString(c) + ": measured " + measured + ", formula " + formula);
            sb.append(String.format("(%d,%d,%d): formula %.4f, measured %.4f; ", n, r, w, formula, measured));
        }
        System.out.println("share of reads that miss the latest write, read straight after one write to a random W replicas: " + sb);
        for (int[] c : new int[][]{{3, 2, 2}, {5, 3, 3}, {5, 2, 4}, {4, 3, 2}, {6, 4, 3}}) {      // R + W > N: a read never misses the latest completed write, however many writes came before
            int n = c[0], r = c[1], w = c[2];
            Register reg = new Register(n);
            for (int op = 0; op < 300_000; op++) {
                if (rnd.nextInt(3) == 0) reg.write(w, rnd);
                else check(reg.read(r, rnd) == reg.latest, "with R + W > N every read returns the latest version, N R W = " + Arrays.toString(c));
            }
        }
        Register loose = new Register(5);
        int staleReads = 0;
        for (int op = 0; op < 100_000; op++) { if (rnd.nextInt(3) == 0) loose.write(2, rnd); else if (loose.read(2, rnd) < loose.latest) staleReads++; }
        check(staleReads > 10_000, "with R + W <= N, stale reads are common over a long run, got " + staleReads);
        sb.setLength(0);
        double p = 0.99;
        for (int[] c : new int[][]{{3, 2, 2}, {3, 1, 3}, {3, 3, 1}, {5, 3, 3}, {5, 1, 5}}) {
            int n = c[0], r = c[1], w = c[2], trials = 2_000_000, readOk = 0, writeOk = 0;
            for (int t = 0; t < trials; t++) {
                int up = 0;
                for (int i = 0; i < n; i++) if (rnd.nextDouble() < p) up++;
                if (up >= r) readOk++;
                if (up >= w) writeOk++;
            }
            check(close(readOk / (double) trials, atLeast(n, r, p), 0.0005) && close(writeOk / (double) trials, atLeast(n, w, p), 0.0005), "availability formula, N R W = " + Arrays.toString(c));
            sb.append(String.format("(%d,%d,%d): reads %.6f, writes %.6f; ", n, r, w, atLeast(n, r, p), atLeast(n, w, p)));
        }
        System.out.println("each replica up with probability 0.99, chance that a read / a write can reach enough replicas: " + sb);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("Quorums: " + passed + " checks passed");
    }
}
