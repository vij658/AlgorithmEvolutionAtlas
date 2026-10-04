import java.util.*;

/**
 * Entry 51 of the principles catalog (Part 3): The power of two choices
 *
 * HOW IT WORKS
 *   Put each ball in the less loaded of two randomly chosen bins instead of one random bin. The maximum load
 *   drops from about log n / log log n to log log n / log 2: an exponential improvement from one extra choice.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java PowerOfTwoChoices.java
 *   Expected: the output in expected-output.txt, ending "PowerOfTwoChoices: 5 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class PowerOfTwoChoices {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int maxLoad(int bins, int balls, int choices, Random rnd) {
        int[] load = new int[bins];
        int max = 0;
        for (int b = 0; b < balls; b++) {
            int best = rnd.nextInt(bins);
            for (int c = 1; c < choices; c++) {
                int cand = rnd.nextInt(bins);
                if (load[cand] < load[best]) best = cand;
            }
            max = Math.max(max, ++load[best]);
        }
        return max;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java PowerOfTwoChoices.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        Random rnd = new Random(51);
        StringBuilder sb = new StringBuilder();
        for (int n : new int[]{1_000, 10_000, 100_000, 1_000_000}) {
            int trials = n >= 1_000_000 ? 5 : 20;
            double[] mean = new double[3];
            for (int d = 1; d <= 3; d++) {
                double sum = 0;
                for (int t = 0; t < trials; t++) sum += maxLoad(n, n, d, rnd);
                mean[d - 1] = sum / trials;
            }
            check(mean[1] < mean[0] && mean[2] <= mean[1] + 0.5, "two choices beat one for n = " + n);
            sb.append(String.format("n = %,d: one choice %.1f, two %.1f, three %.1f; ", n, mean[0], mean[1], mean[2]));
        }
        System.out.println("busiest bin when n balls go into n bins (mean of 20 runs, 5 runs at one million): " + sb);
        int bins = 1_000, balls = 1_000_000, runs = 10;
        double gap1 = 0, gap2 = 0, worst2 = 0;
        for (int t = 0; t < runs; t++) {
            double g2 = maxLoad(bins, balls, 2, rnd) - balls / (double) bins;
            gap1 += (maxLoad(bins, balls, 1, rnd) - balls / (double) bins) / runs;
            gap2 += g2 / runs;
            worst2 = Math.max(worst2, g2);
        }
        check(worst2 < 10 && gap1 > 50, "with many balls the single-choice gap grows but the two-choice gap stays small");
        System.out.printf("heavily loaded: %,d balls in %,d bins (mean load %.0f), mean of %d runs: the busiest bin is %.1f above the mean with one choice and %.1f above with two (worst run %.0f)%n", balls, bins, balls / (double) bins, runs, gap1, gap2, worst2);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("PowerOfTwoChoices: " + passed + " checks passed");
    }
}
