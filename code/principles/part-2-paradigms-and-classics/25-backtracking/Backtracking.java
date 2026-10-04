import java.util.*;

/**
 * Entry 25 of the principles catalog (Part 2): Backtracking and pruning
 *
 * HOW IT WORKS
 *   Build a solution one choice at a time and abandon a partial solution as soon as it cannot lead to a valid
 *   answer. On N-queens, checking each queen as it is placed visits 2,057 nodes for n = 8, where trying every
 *   placement would test 16,777,216 boards.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Backtracking.java
 *   Expected: the output in expected-output.txt, ending "Backtracking: 21 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Backtracking {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int queens(int n) { return place(n, 0, 0, 0, 0); }

    private static int place(int n, int row, int cols, int d1, int d2) {
        if (row == n) return 1;
        int count = 0;
        int free = ~(cols | d1 | d2) & ((1 << n) - 1);     // columns not attacked in this row
        while (free != 0) {
            int bit = free & -free;                         // lowest free column
            free ^= bit;
            count += place(n, row + 1, cols | bit, (d1 | bit) << 1, (d2 | bit) >>> 1);
        }
        return count;
    }

    static long nodes;                                      // instrumented copy

    private static int placeCounted(int n, int row, int cols, int d1, int d2) {
        nodes++;
        if (row == n) return 1;
        int count = 0;
        int free = ~(cols | d1 | d2) & ((1 << n) - 1);
        while (free != 0) {
            int bit = free & -free;
            free ^= bit;
            count += placeCounted(n, row + 1, cols | bit, (d1 | bit) << 1, (d2 | bit) >>> 1);
        }
        return count;
    }

    static int bruteQueens(int n, int row, int[] pos, boolean[] used) {   // enumerate permutations
        if (row == n) {
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (Math.abs(pos[i] - pos[j]) == j - i) return 0;
            return 1;
        }
        int total = 0;
        for (int c = 0; c < n; c++) if (!used[c]) { used[c] = true; pos[row] = c; total += bruteQueens(n, row + 1, pos, used); used[c] = false; }
        return total;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Backtracking.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        int[] known = {1, 0, 0, 2, 10, 4, 40, 92, 352, 724, 2680, 14200};
        for (int n = 1; n <= 12; n++) check(queens(n) == known[n - 1], "queens(" + n + ")");
        for (int n = 1; n <= 8; n++) check(bruteQueens(n, 0, new int[n], new boolean[n]) == queens(n), "bitmask backtracking vs permutation enumeration, n=" + n);
        nodes = 0;
        placeCounted(8, 0, 0, 0, 0);
        check(nodes < 40_320, "pruned search visits fewer nodes than 8! permutations");
        System.out.println("8 queens: " + queens(8) + " solutions; backtracking visited " + nodes + " nodes (8! = 40,320 permutations, 8^8 = 16,777,216 placements)");
        nodes = 0;
        placeCounted(12, 0, 0, 0, 0);
        System.out.println("12 queens: " + queens(12) + " solutions; " + nodes + " nodes visited");
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("Backtracking: " + passed + " checks passed");
    }
}
