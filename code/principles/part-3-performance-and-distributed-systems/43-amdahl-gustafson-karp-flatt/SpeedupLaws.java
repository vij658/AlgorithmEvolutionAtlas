import java.util.*;

/**
 * Entry 43 of the principles catalog (Part 3): Amdahl, Gustafson, Karp-Flatt and list scheduling
 *
 * HOW IT WORKS
 *   Amdahl: if a fraction s of the work is serial, speed-up on p workers is at most 1/(s + (1 - s)/p), capped
 *   at 1/s. Gustafson: if the problem grows with p, scaled speed-up is s + (1 - s)*p. Karp-Flatt recovers the
 *   serial fraction from a measured speed-up, and Graham's bound limits greedy list scheduling to within 2 -
 *   1/p of optimal.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SpeedupLaws.java
 *   Expected: the output in expected-output.txt, ending "SpeedupLaws: 50003 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class SpeedupLaws {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static boolean rel(double a, double b, double r) { return Math.abs(a - b) <= r * Math.max(Math.abs(a), Math.abs(b)); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static double amdahl(double p, double n) { return 1.0 / ((1 - p) + p / n); }       // p = parallelizable fraction of the one-worker run

    static double amdahlLimit(double p) { return 1.0 / (1 - p); }

    static double gustafson(double s, double n) { return n - s * (n - 1); }            // s = serial fraction of the n-worker run

    static double karpFlatt(double speedup, double n) { return (1 / speedup - 1 / n) / (1 - 1 / n); }   // measured serial fraction

    /** Greedy list scheduling: the serial part runs first, then each task goes to the worker that becomes free first. */
    static double makespan(double serial, double[] tasks, int workers) {
        PriorityQueue<Double> free = new PriorityQueue<>();
        for (int i = 0; i < workers; i++) free.add(serial);
        double end = serial;
        for (double t : tasks) {
            double start = free.poll();
            free.add(start + t);
            end = Math.max(end, start + t);
        }
        return end;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java SpeedupLaws.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        check(close(amdahl(0.95, 8), 5.9259, 1e-4) && close(amdahl(0.95, 64), 15.4217, 1e-4) && close(amdahl(0.95, 1024), 19.6357, 1e-4), "Amdahl values for p = 0.95");
        check(close(amdahlLimit(0.95), 20, 1e-12) && close(amdahlLimit(0.5), 2, 1e-12) && close(amdahlLimit(0.99), 100, 1e-9), "limit 1/(1-p)");
        for (double p : new double[]{0.5, 0.9, 0.95, 0.99}) {
            double prev = 0;
            for (int n = 1; n <= 5000; n++) {
                double s = amdahl(p, n);
                check(s > prev && s < amdahlLimit(p), "Amdahl speedup rises with n but never reaches 1/(1-p)");
                prev = s;
            }
        }
        for (int t = 0; t < 10_000; t++) {
            double p = 0.01 + 0.98 * rnd.nextDouble();
            int n = 2 + rnd.nextInt(1000);
            check(rel(karpFlatt(amdahl(p, n), n), 1 - p, 1e-9), "Karp-Flatt recovers the serial fraction exactly from an Amdahl speedup");
            double s = rnd.nextDouble();
            check(rel(gustafson(s, n), s + (1 - s) * n, 1e-12), "Gustafson equals s + (1 - s) n");
        }
        for (int t = 0; t < 5000; t++) {
            int workers = 1 + rnd.nextInt(16), m = 1 + rnd.nextInt(60);
            double serial = 5 * rnd.nextDouble(), sum = 0, maxTask = 0;
            double[] tasks = new double[m];
            for (int i = 0; i < m; i++) { tasks[i] = 0.1 + 9.9 * rnd.nextDouble(); sum += tasks[i]; maxTask = Math.max(maxTask, tasks[i]); }
            double ms = makespan(serial, tasks, workers);
            double lower = serial + Math.max(maxTask, sum / workers);
            double graham = serial + sum / workers + (1 - 1.0 / workers) * maxTask;
            check(ms >= lower - 1e-9 && ms <= graham + 1e-9, "list scheduling stays between the lower bound and Graham's bound");
            double p = sum / (serial + sum);
            check((serial + sum) / ms <= amdahl(p, workers) + 1e-9, "no schedule beats Amdahl's law");
        }
        double[] ten = new double[10];
        Arrays.fill(ten, 1.0);
        check(makespan(0, ten, 64) == 1.0, "10 unit tasks on 64 workers take 1.0");
        System.out.printf("Amdahl, p = 0.95: speedup %.2f on 8 workers, %.2f on 64, %.2f on 1024, limit %.0f%n", amdahl(0.95, 8), amdahl(0.95, 64), amdahl(0.95, 1024), amdahlLimit(0.95));
        System.out.printf("efficiency (speedup / workers) at p = 0.95: %.0f%% on 8 workers, %.0f%% on 64, %.1f%% on 1024%n", 100 * amdahl(0.95, 8) / 8, 100 * amdahl(0.95, 64) / 64, 100 * amdahl(0.95, 1024) / 1024);
        System.out.printf("same 5%% serial part, but the problem grows with the machine (Gustafson): %.2f on 64 workers, against Amdahl's %.2f%n", gustafson(0.05, 64), amdahl(0.95, 64));
        System.out.printf("limits 1/(1-p): p = 0.5 -> %.0f, 0.9 -> %.0f, 0.99 -> %.0f, 0.999 -> %.0f%n", amdahlLimit(0.5), amdahlLimit(0.9), amdahlLimit(0.99), amdahlLimit(0.999));
        System.out.println("10 equal tasks on 64 workers finish in 1.0 time units, a speedup of 10, where Amdahl with p = 1 would promise 64");
        double measured = 5.9259;
        System.out.printf("Karp-Flatt: a measured speedup of %.4f on 8 workers implies a serial fraction of %.4f%n", measured, karpFlatt(measured, 8));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2028));
        System.out.println("SpeedupLaws: " + passed + " checks passed");
    }
}
