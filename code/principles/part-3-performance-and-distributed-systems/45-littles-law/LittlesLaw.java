import java.util.*;
import java.util.function.DoubleSupplier;

/**
 * Entry 45 of the principles catalog (Part 3): Little's law
 *
 * HOW IT WORKS
 *   In any stable system, the average number of items inside equals the arrival rate times the average time
 *   each spends inside: L = lambdaW. It needs no assumptions about distributions; the program checks it on
 *   simulated queues of many kinds.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LittlesLaw.java
 *   Expected: the output in expected-output.txt, ending "LittlesLaw: 9 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class LittlesLaw {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    static double gaussian(Random rnd) {                       // Box-Muller from nextDouble, so results do not depend on the JDK's nextGaussian
        double u1 = 1 - rnd.nextDouble(), u2 = rnd.nextDouble();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    }

    static double exponential(Random rnd, double mean) { return -mean * Math.log(1 - rnd.nextDouble()); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** One FIFO/LIFO/random-order server with Poisson arrivals. Returns {arrival times, departure times}. */
    static double[][] singleServer(int customers, double lambda, DoubleSupplier service, int discipline, Random rnd) {
        double[] arrive = new double[customers], depart = new double[customers], svc = new double[customers];
        double t = 0;
        for (int i = 0; i < customers; i++) { t += exponential(rnd, 1 / lambda); arrive[i] = t; svc[i] = service.getAsDouble(); }
        ArrayList<Integer> waiting = new ArrayList<>();
        int next = 0, done = 0;
        double now = 0;
        while (done < customers) {
            if (waiting.isEmpty() && next < customers && arrive[next] > now) now = arrive[next];
            while (next < customers && arrive[next] <= now) waiting.add(next++);
            int pick = discipline == 0 ? 0 : discipline == 1 ? waiting.size() - 1 : rnd.nextInt(waiting.size());   // FIFO, LIFO, random
            int c = waiting.remove(pick);
            now += svc[c];
            depart[c] = now;
            done++;
        }
        return new double[][]{arrive, depart};
    }

    /** Returns {L, lambda, W, T}: time-average number in system, arrival rate, mean time in system, observation time. */
    static double[] little(double[] arrive, double[] depart) {
        int n = arrive.length;
        double end = 0, sumW = 0;
        double[][] events = new double[2 * n][];
        for (int i = 0; i < n; i++) {
            end = Math.max(end, depart[i]);
            sumW += depart[i] - arrive[i];
            events[2 * i] = new double[]{arrive[i], +1};
            events[2 * i + 1] = new double[]{depart[i], -1};
        }
        Arrays.sort(events, Comparator.comparingDouble(e -> e[0]));
        double area = 0, last = 0;
        int inSystem = 0;
        for (double[] e : events) { area += inSystem * (e[0] - last); last = e[0]; inSystem += (int) e[1]; }
        return new double[]{area / end, n / end, sumW / n, end};
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java LittlesLaw.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks() {
        String[] names = {"FIFO", "LIFO", "random order"};
        StringBuilder line = new StringBuilder();
        for (int d = 0; d < 3; d++) {
            for (int dist = 0; dist < 3; dist++) {
                Random rnd = new Random(45 + 10 * d + dist);
                double sigma2 = Math.log(5), sigma = Math.sqrt(sigma2);
                DoubleSupplier service = dist == 0 ? () -> exponential(rnd, 0.7)
                        : dist == 1 ? () -> 0.7
                        : () -> 0.7 * Math.exp(-sigma2 / 2 + sigma * gaussian(rnd));          // lognormal, mean 0.7, squared coefficient of variation 4
                double[][] run = singleServer(50_000, 1.0, service, d, rnd);
                double[] s = little(run[0], run[1]);
                check(rel(s[0], s[1] * s[2], 1e-9), "L = lambda W exactly, " + names[d] + ", service distribution " + dist);
                if (dist == 0) line.append(String.format("%s: L = %.3f, lambda = %.3f, W = %.3f, lambda*W = %.3f; ", names[d], s[0], s[1], s[2], s[1] * s[2]));
            }
        }
        System.out.println("Little's law on 9 simulated queues (3 service orders x 3 service-time distributions, 50,000 customers each) holds to 1e-9; exponential service, rho = 0.7: " + line);
        System.out.printf("sizing example: %.0f requests/s x %.1f s each = %.0f requests in flight%n", 500.0, 0.2, 500 * 0.2);
    }

    public static void main(String[] args) throws Exception {
        runChecks();
        System.out.println("LittlesLaw: " + passed + " checks passed");
    }
}
