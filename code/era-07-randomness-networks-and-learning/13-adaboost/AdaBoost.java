import java.util.*;

/**
 * Era 7, topic 13: AdaBoost (Yoav Freund and Robert Schapire, AT&T, 1995; journal version 1997).
 *
 * HOW IT WORKS
 *   A "weak" rule of thumb is one that is right a little more often than a coin: here a decision stump, a single
 *   test such as "x below 0.43 means yes". Kearns and Valiant asked whether rules that weak could always be combined
 *   into an accurate one; Schapire showed in 1990 that they could, and Freund and Schapire's AdaBoost made it
 *   practical. Give every training example a weight, equal at first. Each round, find the stump with the smallest
 *   weighted error e; then shrink the weight of every example it got right by the factor e / (1 - e), so the next
 *   round concentrates on the examples still being missed. The final rule is a vote of all the stumps, each counted
 *   with weight log((1 - e) / e). Freund and Schapire proved that the training error falls at least as fast as the
 *   product of 2 sqrt(e (1 - e)) over the rounds: exponentially, as long as each stump beats a coin by some margin.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Points in a square, labelled by whether they lie inside a circle: no single stump can draw a circle. Training
 *      and test error as rounds are added, against the proven bound.
 *   2. The same with 10% of the training labels flipped: the weights pile up on the flipped examples.
 *   3. A small set of 120 points made with a simple generator that the book's widget repeats, so the widget can show
 *      the same rounds with the same errors.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AdaBoost.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AdaBoost {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- a 32-bit generator simple enough to repeat exactly in JavaScript ------------------------------------------
    static int s32 = 1995;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    /** n points in the unit square; label +1 inside the circle of radius 0.35 about (0.5, 0.5), else -1. */
    static double[][] points(int n) {
        double[][] p = new double[n][3];
        for (double[] q : p) {
            q[0] = next32(); q[1] = next32();
            double dx = q[0] - 0.5, dy = q[1] - 0.5;
            q[2] = dx * dx + dy * dy < 0.35 * 0.35 ? 1 : -1;
        }
        return p;
    }

    /** A stump: feature f (0 = x, 1 = y), threshold t, sign s: predicts s if value < t, else -s. */
    record Stump(int f, double t, int s) {
        int predict(double[] q) { return q[f] < t ? s : -s; }
    }

    /** The stump with the smallest weighted error; ties go to the first found (x before y, low thresholds first). */
    static Stump bestStump(double[][] p, double[] w, double[] errOut) {
        int n = p.length;
        Stump best = null;
        double bestErr = Double.MAX_VALUE;
        for (int f = 0; f < 2; f++) {
            Integer[] idx = new Integer[n];
            for (int i = 0; i < n; i++) idx[i] = i;
            final int ff = f;
            Arrays.sort(idx, (a, b) -> Double.compare(p[a][ff], p[b][ff]));
            // errPlus: weighted error of "predict +1 below t, -1 above" for t below every point = weight of all +1 points
            double errPlus = 0;
            for (int i = 0; i < n; i++) if (p[i][2] > 0) errPlus += w[i];
            for (int k = 0; k <= n; k++) {
                if (k > 0) {
                    int i = idx[k - 1];                        // point i moves to the "below" side
                    errPlus += p[i][2] > 0 ? -w[i] : w[i];
                }
                if (k == 0 || k == n) continue;                // a threshold outside the data is not a test
                if (p[idx[k - 1]][f] == p[idx[k]][f]) continue;
                double t = (p[idx[k - 1]][f] + p[idx[k]][f]) / 2;
                double errMinus = 1 - errPlus;
                if (errPlus < bestErr) { bestErr = errPlus; best = new Stump(f, t, 1); }
                if (errMinus < bestErr) { bestErr = errMinus; best = new Stump(f, t, -1); }
            }
        }
        errOut[0] = bestErr;
        return best;
    }

    static List<Stump> stumps;
    static List<Double> votes;
    static double bound;

    static int predict(double[] q) {
        double sum = 0;
        for (int k = 0; k < stumps.size(); k++) sum += votes.get(k) * stumps.get(k).predict(q);
        return sum >= 0 ? 1 : -1;
    }

    static double error(double[][] p) {
        int wrong = 0;
        for (double[] q : p) if (predict(q) != q[2]) wrong++;
        return (double) wrong / p.length;
    }

    static double[] weights;

    /** One round of AdaBoost: returns the stump's weighted error. */
    static double round(double[][] p) {
        double[] e = new double[1];
        Stump h = bestStump(p, weights, e);
        double eps = e[0];
        double beta = eps / (1 - eps);
        for (int i = 0; i < p.length; i++) if (h.predict(p[i]) == p[i][2]) weights[i] *= beta;
        double sum = 0;
        for (double x : weights) sum += x;
        for (int i = 0; i < p.length; i++) weights[i] /= sum;
        stumps.add(h);
        votes.add(Math.log(1 / beta));
        bound *= 2 * Math.sqrt(eps * (1 - eps));
        return eps;
    }

    static void start(int n) {
        weights = new double[n];
        Arrays.fill(weights, 1.0 / n);
        stumps = new ArrayList<>();
        votes = new ArrayList<>();
        bound = 1;
    }

    public static void main(String[] args) {
        // ---- 1. the circle -----------------------------------------------------------------------------------------
        double[][] train = points(1000), test = points(20000);
        start(train.length);
        StringJoiner cj = new StringJoiner(" ; ");
        double firstErr = 0, minEps = 1, maxEps = 0;
        int zeroAt = -1;
        Set<Integer> report = Set.of(1, 2, 5, 10, 20, 50, 100, 200, 500);
        for (int t = 1; t <= 500; t++) {
            double eps = round(train);
            minEps = Math.min(minEps, eps);
            maxEps = Math.max(maxEps, eps);
            check(eps < 0.5, "each stump beats a coin on the weighted examples");
            double tr = error(train);
            check(tr <= bound + 1e-12, "training error never exceeds the product bound");
            if (t == 1) firstErr = error(test);
            if (tr == 0 && zeroAt < 0) zeroAt = t;
            if (report.contains(t)) cj.add(String.format("%d round%s: training error %.1f%% (bound %.1f%%), test error %.1f%%", t, t == 1 ? "" : "s", 100 * tr, 100 * Math.min(1, bound), 100 * error(test)));
        }
        double finalTest = error(test);
        check(finalTest < firstErr / 3, "500 stumps together are far better than one");
        System.out.printf("circle: 1,000 training points and 20,000 test points in the unit square, labelled by whether they lie inside a circle of radius 0.35 ; one stump (one threshold on x or on y) per round ; %s ; training error first reached 0 after %d rounds ; the stumps' weighted errors ranged from %.3f to %.3f%n",
                cj, zeroAt, minEps, maxEps);

        // ---- 2. noisy labels ------------------------------------------------------------------------------------------
        s32 = 7;
        double[][] noisy = points(1000);
        boolean[] flipped = new boolean[noisy.length];
        int flips = 0;
        for (int i = 0; i < noisy.length; i++) if (next32() < 0.10) { noisy[i][2] = -noisy[i][2]; flipped[i] = true; flips++; }
        start(noisy.length);
        StringJoiner nj = new StringJoiner(" ; ");
        double bestTest = 1;
        for (int t = 1; t <= 500; t++) {
            round(noisy);
            double te = error(test);
            bestTest = Math.min(bestTest, te);
            if (t == 10 || t == 50 || t == 200 || t == 500) {
                double onFlipped = 0;
                for (int i = 0; i < noisy.length; i++) if (flipped[i]) onFlipped += weights[i];
                nj.add(String.format("%d rounds: training error %.1f%%, test error %.1f%%, %.0f%% of the weight on the flipped examples", t, 100 * error(noisy), 100 * te, 100 * onFlipped));
            }
        }
        double onFlippedEnd = 0;
        for (int i = 0; i < noisy.length; i++) if (flipped[i]) onFlippedEnd += weights[i];
        check(onFlippedEnd > 3 * (double) flips / noisy.length, "the weight piles up on the flipped examples");
        check(error(test) > bestTest, "and the test error ends above its best");
        System.out.printf("noise: a new set of 1,000 training points with %d labels (%.0f%%) flipped at random, tested on the same clean 20,000 ; %s ; the best test error along the way was %.1f%%%n",
                flips, 100.0 * flips / noisy.length, nj, 100 * bestTest);

        // ---- 3. the widget's points --------------------------------------------------------------------------------
        s32 = 2003;
        double[][] small = points(120);
        start(small.length);
        StringJoiner wj = new StringJoiner(" ");
        for (int t = 1; t <= 40; t++) {
            double eps = round(small);
            int wrong = 0;
            for (double[] q : small) if (predict(q) != q[2]) wrong++;
            wj.add(String.format("%d:%d:%.4f", t, wrong, eps));
        }
        Stump first = stumps.get(0);
        System.out.printf("widget: 120 points from the 32-bit generator s = 1664525 s + 1013904223 (mod 2^32), seed 2003, x then y for each point ; first stump: %s %s %.4f predicts %s ; round:training mistakes:weighted error of that round's stump ; %s%n",
                first.f() == 0 ? "x" : "y", "<", first.t(), first.s() > 0 ? "inside" : "outside", wj);

        System.out.println("AdaBoost: " + passed + " checks passed");
    }
}
