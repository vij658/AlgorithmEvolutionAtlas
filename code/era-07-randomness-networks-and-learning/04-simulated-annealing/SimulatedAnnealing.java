import java.util.*;

/**
 * Era 7, topic 4: simulated annealing (Kirkpatrick, Gelatt and Vecchi, IBM, 1983; Cerny, Bratislava, 1985).
 *
 * HOW IT WORKS
 *   To shorten a travelling salesman's tour, try a small change: reverse one stretch of the tour. Iterative
 *   improvement keeps a change only if the tour gets shorter, and soon stops at a tour that no single change can
 *   improve, often far from the best. Annealing borrows the Metropolis rule from the physics of cooling metal: a change
 *   that lengthens the tour by d is still accepted, with probability exp(-d / T). At a high "temperature" T nearly
 *   every change is accepted and the tour wanders; as T is lowered slowly, worse changes are accepted more and more
 *   rarely, and the tour settles into a deep valley rather than the first hollow it finds. Cooling fast is
 *   "quenching" and gives worse tours; cooling slowly takes longer and gives better ones.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Tours of 12 cities, where the best tour can be found exactly (Held and Karp's method, a dynamic programme; Era 5):
 *      how often iterative improvement and annealing find it.
 *   2. Tours of 200 cities: a random tour, iterative improvement, and annealing.
 *   3. The cooling rate: tour length and work for slower and slower cooling.
 *   4. One annealing run, temperature by temperature: the share of changes accepted.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SimulatedAnnealing.java
 *   Expected output: expected-output.txt in this folder.
 */
public class SimulatedAnnealing {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1983L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int below(int k) { return (int) (uniform() * k); }

    static double[][] cities(int n) {
        double[][] c = new double[n][2];
        for (double[] p : c) { p[0] = uniform(); p[1] = uniform(); }
        return c;
    }

    static double dist(double[][] c, int a, int b) { return Math.hypot(c[a][0] - c[b][0], c[a][1] - c[b][1]); }

    static double length(double[][] c, int[] t) {
        double s = 0;
        for (int i = 0; i < t.length; i++) s += dist(c, t[i], t[(i + 1) % t.length]);
        return s;
    }

    static int[] randomTour(int n) {
        int[] t = new int[n];
        for (int i = 0; i < n; i++) t[i] = i;
        for (int i = n - 1; i > 0; i--) { int j = below(i + 1); int x = t[i]; t[i] = t[j]; t[j] = x; }
        return t;
    }

    /** Change in length if the stretch t[i..j] (i < j) is reversed. */
    static double delta(double[][] c, int[] t, int i, int j) {
        int n = t.length;
        int a = t[(i - 1 + n) % n], b = t[i], cc = t[j], d = t[(j + 1) % n];
        if (a == cc || b == d) return 0;                         // reversing the whole tour changes nothing
        return dist(c, a, cc) + dist(c, b, d) - dist(c, a, b) - dist(c, cc, d);
    }

    static void reverse(int[] t, int i, int j) {
        while (i < j) { int x = t[i]; t[i] = t[j]; t[j] = x; i++; j--; }
    }

    static long tries;

    /** Iterative improvement: keep trying random reversals, keep only those that shorten, stop when none helps. */
    static int[] descend(double[][] c, int[] t) {
        int n = t.length;
        boolean improved = true;
        while (improved) {
            improved = false;
            for (int i = 0; i < n - 1; i++)
                for (int j = i + 1; j < n; j++) {
                    tries++;
                    if (delta(c, t, i, j) < -1e-12) { reverse(t, i, j); improved = true; }
                }
        }
        return t;
    }

    static List<String> acceptLog;

    /**
     * Annealing with Kirkpatrick, Gelatt and Vecchi's schedule: start hot enough that nearly every change is accepted,
     * multiply the temperature by `cool` each time, and at each temperature try up to 100 n changes, moving on early
     * after 10 n acceptances; frozen after three successive temperatures that accept fewer than 1 change in 1,000.
     * A final pass of iterative improvement makes sure the result cannot be improved by one reversal.
     */
    static int[] anneal(double[][] c, int[] t, double cool) {
        int n = t.length;
        double T = 2.0;
        int cold = 0;
        while (cold < 3) {
            int accepted = 0, tried = 0;
            while (tried < 100 * n && accepted < 10 * n) {
                int i = below(n), j = below(n);
                if (i == j) continue;
                if (i > j) { int x = i; i = j; j = x; }
                if (j - i >= n - 2) continue;                     // the same cycle, only reversed: not a change
                double d = delta(c, t, i, j);
                tried++;
                tries++;
                if (d <= 0 || uniform() < Math.exp(-d / T)) { reverse(t, i, j); accepted++; }
            }
            if (acceptLog != null) acceptLog.add(String.format("%.4f:%.3f", T, accepted / (double) tried));
            cold = accepted * 1000 < tried ? cold + 1 : 0;
            T *= cool;
        }
        return descend(c, t);
    }

    /** Held and Karp's dynamic programme: the exact shortest tour, for small n. */
    static double heldKarp(double[][] c) {
        int n = c.length, full = 1 << (n - 1);
        double[][] best = new double[full][n - 1];
        for (double[] row : best) Arrays.fill(row, Double.MAX_VALUE);
        for (int j = 0; j < n - 1; j++) best[1 << j][j] = dist(c, n - 1, j);
        for (int s = 1; s < full; s++)
            for (int j = 0; j < n - 1; j++) {
                if ((s & (1 << j)) == 0 || best[s][j] == Double.MAX_VALUE) continue;
                for (int k = 0; k < n - 1; k++) {
                    if ((s & (1 << k)) != 0) continue;
                    double v = best[s][j] + dist(c, j, k);
                    if (v < best[s | (1 << k)][k]) best[s | (1 << k)][k] = v;
                }
            }
        double opt = Double.MAX_VALUE;
        for (int j = 0; j < n - 1; j++) opt = Math.min(opt, best[full - 1][j] + dist(c, j, n - 1));
        return opt;
    }

    static boolean isTour(int[] t) {
        boolean[] seen = new boolean[t.length];
        for (int x : t) { if (seen[x]) return false; seen[x] = true; }
        return true;
    }

    public static void main(String[] args) {
        // ---- 1. small tours, against the exact optimum -----------------------------------------------------------------
        int instances = 50, small = 12, descentHits = 0, annealHits = 0;
        double descentExcess = 0, annealExcess = 0;
        for (int k = 0; k < instances; k++) {
            double[][] c = cities(small);
            double opt = heldKarp(c);
            int[] start = randomTour(small);
            int[] d = descend(c, start.clone());
            int[] a = anneal(c, start.clone(), 0.9);
            check(isTour(d) && isTour(a), "results are tours");
            double ld = length(c, d), la = length(c, a);
            check(ld >= opt - 1e-9 && la >= opt - 1e-9, "nothing beats the exact optimum");
            if (ld - opt < 1e-9) descentHits++;
            if (la - opt < 1e-9) annealHits++;
            descentExcess += (ld / opt - 1) / instances;
            annealExcess += (la / opt - 1) / instances;
        }
        check(annealHits > descentHits, "annealing finds the optimum more often");
        System.out.printf("exact: %d sets of %d random cities, the shortest tour found exactly by Held and Karp's method ; iterative improvement (reversing stretches) from a random tour found it %d times, on average %.1f%% too long ; annealing found it %d times, on average %.2f%% too long%n",
                instances, small, descentHits, 100 * descentExcess, annealHits, 100 * annealExcess);

        // ---- 2. 200 cities -------------------------------------------------------------------------------------------
        int n = 200, sets = 10;
        double sumRandom = 0, sumDescent = 0, sumAnneal = 0;
        long triesDescent = 0, triesAnneal = 0;
        int annealWins = 0;
        for (int k = 0; k < sets; k++) {
            double[][] c = cities(n);
            int[] start = randomTour(n);
            sumRandom += length(c, start) / sets;
            tries = 0;
            int[] d = descend(c, start.clone());
            triesDescent += tries / sets;
            tries = 0;
            int[] a = anneal(c, start.clone(), 0.9);
            triesAnneal += tries / sets;
            check(isTour(a) && isTour(d), "tours");
            double ld = length(c, d), la = length(c, a);
            sumDescent += ld / sets;
            sumAnneal += la / sets;
            if (la < ld) annealWins++;
        }
        check(sumAnneal < sumDescent && sumDescent < sumRandom, "annealing beats iterative improvement beats random");
        System.out.printf("tour: %d sets of %d random cities in a unit square, average tour length ; random tour %.2f ; iterative improvement %.3f (%,d changes tried) ; annealing %.3f (%,d changes tried), shorter in %d of %d sets%n",
                sets, n, sumRandom, sumDescent, triesDescent, sumAnneal, triesAnneal, annealWins, sets);

        // ---- 3. the cooling rate ---------------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        double[] cools = {0.5, 0.8, 0.9, 0.95, 0.99};
        double[] lens = new double[cools.length];
        long[] work = new long[cools.length];
        for (int q = 0; q < cools.length; q++) {
            seed = 777;
            for (int k = 0; k < 5; k++) {
                double[][] c = cities(n);
                int[] start = randomTour(n);
                tries = 0;
                int[] a = anneal(c, start, cools[q]);
                lens[q] += length(c, a) / 5;
                work[q] += tries / 5;
            }
            cj.add(String.format("factor %.2f: length %.3f, %,d changes tried", cools[q], lens[q], work[q]));
        }
        check(lens[cools.length - 1] < lens[0], "slow cooling beats fast cooling");
        check(work[cools.length - 1] > work[0], "and costs more");
        System.out.printf("cooling: the same 5 sets of %d cities annealed with the temperature multiplied by each factor in turn ; %s%n", n, cj);

        // ---- 4. one run, temperature by temperature ------------------------------------------------------------------
        seed = 4598;
        double[][] c = cities(n);
        acceptLog = new ArrayList<>();
        anneal(c, randomTour(n), 0.9);
        List<String> log = acceptLog;
        acceptLog = null;
        double firstRate = Double.parseDouble(log.get(0).split(":")[1]);
        double lastRate = Double.parseDouble(log.get(log.size() - 1).split(":")[1]);
        check(firstRate > 0.8 && lastRate < 0.001, "hot: most accepted ; frozen: almost none");
        StringJoiner lj = new StringJoiner(" ");
        for (String s : log) lj.add(s);
        System.out.printf("accept: one run on %d cities, %d temperatures, temperature:share of changes accepted ; %s%n", n, log.size(), lj);

        System.out.println("SimulatedAnnealing: " + passed + " checks passed");
    }
}
