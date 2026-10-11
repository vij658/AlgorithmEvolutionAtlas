import java.util.*;

/**
 * Era 4, topic 10: Monte Carlo, and the middle-square method (1946-1949).
 *
 * HOW IT WORKS
 *   To find a probability or an average that is too tangled to calculate, simulate many random cases and count. The
 *   share of random points in a square that land inside a quarter circle estimates pi/4; the share of points in a
 *   cube that land in a ball estimates the ball's volume, in any number of dimensions. The answer is only
 *   approximate, but its typical error shrinks like 1/sqrt(N) for N samples, whatever the dimension: four times the
 *   samples, half the error.
 *   The method needs random numbers by the million. Von Neumann's middle-square method makes them by arithmetic:
 *   square a 4-digit number (padding the square to 8 digits) and keep the middle 4 digits, then repeat. The numbers
 *   look random for a while, but each one fixes the next, so the sequence must eventually repeat, often soon, and
 *   some seeds sink to 0000 or stick at a fixed point.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Runs the 4-digit middle-square method from all 10,000 seeds and lists every cycle it falls into.
 *   2. Estimates pi from random points and measures how the error shrinks with the number of points.
 *   3. Estimates the volume of the unit ball in 2, 5 and 10 dimensions, against the exact formula.
 *   4. Estimates pi with middle-square numbers instead of good ones, and shows what goes wrong.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MonteCarlo.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MonteCarlo {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** One step of the 4-digit middle-square method. */
    static int middleSquare(int x) { return (int) ((long) x * x / 100 % 10000); }

    static long seed = 1946L;

    /** A 64-bit linear congruential generator, its top 53 bits as a number in [0, 1). */
    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / 9007199254740992.0;
    }

    static String four(int x) { return String.format("%04d", x); }

    /** Volume of the unit ball in d dimensions: pi^(d/2) / Gamma(d/2 + 1), with Gamma by its recurrence. */
    static double ballVolume(int d) {
        double gamma = d % 2 == 0 ? 1 : Math.sqrt(Math.PI);                // Gamma(1) or Gamma(1/2)
        for (double x = d % 2 == 0 ? 1 : 0.5; x < d / 2.0 + 1 - 1e-9; x++) gamma *= x;
        return Math.pow(Math.PI, d / 2.0) / gamma;
    }

    public static void main(String[] args) {
        // ---- 1. middle-square from every seed ---------------------------------------------------------------------------
        Map<String, Integer> cycleSeeds = new TreeMap<>();
        int longest = 0, longestSeed = 0;
        long totalRun = 0;
        for (int s = 0; s < 10000; s++) {
            Map<Integer, Integer> seen = new HashMap<>();
            int x = s, k = 0;
            while (!seen.containsKey(x)) { seen.put(x, k++); x = middleSquare(x); }
            int start = x;
            List<Integer> cyc = new ArrayList<>();
            do { cyc.add(x); x = middleSquare(x); } while (x != start);
            // name the cycle from its smallest member
            int mi = cyc.indexOf(Collections.min(cyc));
            StringJoiner name = new StringJoiner(" ");
            for (int i = 0; i < cyc.size(); i++) name.add(four(cyc.get((mi + i) % cyc.size())));
            cycleSeeds.merge(name.toString(), 1, Integer::sum);
            if (k > longest) { longest = k; longestSeed = s; }
            totalRun += k;
        }
        for (String fixed : new String[]{"0000", "0100", "2500", "3792", "7600"}) check(cycleSeeds.containsKey(fixed), "fixed point " + fixed);
        check(cycleSeeds.containsKey("0540 2916 5030 3009"), "the cycle 0540 2916 5030 3009");
        StringJoiner cj = new StringJoiner(" ; ");
        cycleSeeds.forEach((c, n) -> cj.add("[" + c + "] from " + n + (n == 1 ? " seed" : " seeds")));
        System.out.printf("middle: 4-digit middle-square from all 10000 seeds ; every sequence ends in one of %d cycles: %s ; the longest run before a number repeats is %d numbers, from seed %s ; on average %.1f%n",
                cycleSeeds.size(), cj, longest, four(longestSeed), totalRun / 10000.0);

        // the sequence from seed 1234, until a number repeats
        StringJoiner sq = new StringJoiner(" ");
        Set<Integer> got = new HashSet<>();
        int z = 1234;
        while (got.add(z)) { sq.add(four(z)); z = middleSquare(z); }
        check(got.size() < 100, "seed 1234 repeats within 100 numbers");
        System.out.printf("seq: from seed 1234: %s, then %s again ; %d different numbers%n", sq, four(z), got.size());

        // ---- 2. pi from random points -------------------------------------------------------------------------------------
        StringJoiner est = new StringJoiner(" ; ");
        long inside = 0, n = 0;
        for (long target = 100; target <= 10_000_000L; target *= 10) {
            while (n < target) { double x = uniform(), y = uniform(); if (x * x + y * y < 1) inside++; n++; }
            est.add(String.format("%,d points: %.6f", n, 4.0 * inside / n));
        }
        double piFinal = 4.0 * inside / n;
        check(Math.abs(piFinal - Math.PI) < 0.002, "ten million points give pi to about 3 decimals");
        // the error: root-mean-square over 200 independent runs at each size
        int[] sizes = {1000, 4000, 16000, 64000};
        double[] rms = new double[sizes.length];
        for (int i = 0; i < sizes.length; i++) {
            double sum2 = 0;
            for (int r = 0; r < 200; r++) {
                long in = 0;
                for (int k = 0; k < sizes[i]; k++) { double x = uniform(), y = uniform(); if (x * x + y * y < 1) in++; }
                double e = 4.0 * in / sizes[i] - Math.PI;
                sum2 += e * e;
            }
            rms[i] = Math.sqrt(sum2 / 200);
        }
        StringJoiner rj = new StringJoiner(", ");
        for (int i = 0; i < sizes.length; i++) rj.add(String.format("%,d: %.5f", sizes[i], rms[i]));
        StringJoiner ratios = new StringJoiner(", ");
        for (int i = 0; i + 1 < sizes.length; i++) {
            double ratio = rms[i] / rms[i + 1];
            check(ratio > 1.6 && ratio < 2.5, "four times the points, about half the error");
            ratios.add(String.format("%.2f", ratio));
        }
        double theory = Math.sqrt(Math.PI * (4 - Math.PI) / 1000);           // the standard deviation for N = 1000
        System.out.printf("pi: share of random points inside the quarter circle, times 4 ; %s ; typical error over 200 runs: %s ; ratios %s ; theory for 1,000 points sqrt(pi(4 - pi)/N) = %.5f%n",
                est, rj, ratios, theory);

        // ---- 3. the volume of a ball, in any dimension --------------------------------------------------------------------
        StringJoiner bj = new StringJoiner(" ; ");
        int samples = 1_000_000;
        for (int d : new int[]{2, 5, 10}) {
            long in = 0;
            for (int k = 0; k < samples; k++) {
                double r2 = 0;
                for (int j = 0; j < d; j++) { double u = 2 * uniform() - 1; r2 += u * u; }
                if (r2 < 1) in++;
            }
            double estimate = Math.pow(2, d) * in / samples, exact = ballVolume(d);
            double share = (double) in / samples;
            double se = Math.pow(2, d) * Math.sqrt(share * (1 - share) / samples);
            check(Math.abs(estimate - exact) < 4 * se, "within four standard errors in dimension " + d);
            bj.add(String.format("d = %d: estimate %.4f, exact %.4f, %.2f%% of points inside", d, estimate, exact, 100 * share));
        }
        check(Math.abs(ballVolume(2) - Math.PI) < 1e-12 && Math.abs(ballVolume(3) - 4 * Math.PI / 3) < 1e-12, "the formula gives pi and 4pi/3");
        System.out.printf("ball: volume of the unit ball from %,d random points in the cube ; %s ; a grid with 10 points per side would need 10^d points%n", samples, bj);

        // ---- 4. pi from middle-square numbers -------------------------------------------------------------------------------
        int x = 1234;
        Set<Integer> seen = new HashSet<>();
        long in = 0, pts = 0;
        int used = 0;
        while (pts < 100_000) {
            int a = x; x = middleSquare(x);
            int b = x; x = middleSquare(x);
            if (seen.contains(a)) { /* the sequence has started repeating */ } else seen.add(a);
            seen.add(b);
            double u = a / 10000.0, v = b / 10000.0;
            if (u * u + v * v < 1) in++;
            pts++;
        }
        used = seen.size();
        double bad = 4.0 * in / pts;
        check(used < 100, "middle-square from 1234 produces fewer than 100 different numbers");
        System.out.printf("bad: pi from 100,000 points made of 4-digit middle-square numbers, seed 1234: %.4f ; only %d different numbers ever appear before the sequence repeats%n", bad, used);

        System.out.println("MonteCarlo: " + passed + " checks passed");
    }
}
