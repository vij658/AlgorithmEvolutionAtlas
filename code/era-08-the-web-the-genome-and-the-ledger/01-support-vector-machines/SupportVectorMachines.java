import java.util.*;

/**
 * Era 8, topic 1: Support vector machines (Vapnik and Chervonenkis, Moscow, 1960s; Boser, Guyon and Vapnik, AT&T
 * Bell Laboratories, 1992; Cortes and Vapnik, 1995).
 *
 * HOW IT WORKS
 *   Two kinds of examples, labelled +1 and -1, are points in a plane (or in many dimensions). Rosenblatt's perceptron
 *   finds some line that separates them; a support vector machine finds the line with the widest empty street on
 *   either side. Write the line as w . x + b = 0 and ask that every example satisfy y (w . x + b) >= 1; the street
 *   is then 2 / |w| wide, so the widest street has the smallest |w|. That is a quadratic program. Its dual form has
 *   one number alpha_i >= 0 per example, and the answer is w = sum alpha_i y_i x_i: only the examples with alpha_i > 0,
 *   the support vectors, count, and they are the ones standing on the edges of the street.
 *   The dual touches the examples only through dot products x_i . x_j. Replace the dot product by another function
 *   K(x_i, x_j), a kernel, and the same algorithm draws a straight street in a space of new features that it never
 *   writes down: (x . z + 1)^2 is the dot product of the 6 features 1, sqrt2 x1, sqrt2 x2, x1^2, x2^2, sqrt2 x1 x2,
 *   so a straight street there is a curved one here.
 *   Real data rarely separate. The soft margin lets example i stand inside the street, or on the wrong side, by a
 *   slack xi_i, at a price C xi_i; in the dual this only caps every alpha_i at C.
 *   This program solves the dual by sequential minimal optimization: change two alphas at a time (the pair that
 *   most violates the optimality conditions), which can be done exactly with a formula.
 *
 * WHAT THIS PROGRAM DOES
 *   1. 60 separable points: the widest street, checked against a direct search over every direction of the line,
 *      and the street left by a perceptron trained on the same points.
 *   2. The kernel trick checked: (x . z + 1)^2 equals the dot product of the six explicit features.
 *   3. A disc inside a ring: no line separates them; the degree-2 kernel and a Gaussian kernel do.
 *   4. Two overlapping clouds: the soft margin for C from 0.01 to 100.
 *   5. 40 points from a simple generator that the book's widget repeats, for four values of C.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SupportVectorMachines.java
 *   Expected output: expected-output.txt in this folder.
 */
public class SupportVectorMachines {
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

    static double gauss() { // Box-Muller
        double u = next32(), v = next32();
        return Math.sqrt(-2 * Math.log(1 - u)) * Math.cos(2 * Math.PI * v);
    }

    interface Kernel { double k(double[] a, double[] b); }

    static final Kernel LINEAR = (a, b) -> a[0] * b[0] + a[1] * b[1];
    static final Kernel POLY2 = (a, b) -> { double d = a[0] * b[0] + a[1] * b[1] + 1; return d * d; };

    static Kernel gaussian(double gamma) {
        return (a, b) -> { double dx = a[0] - b[0], dy = a[1] - b[1]; return Math.exp(-gamma * (dx * dx + dy * dy)); };
    }

    /** A trained machine: the alphas, the offset b, and what it took. */
    static final class Svm {
        double[][] x; int[] y; double[] alpha; double b; Kernel kern; double C; int iterations;

        double f(double[] p) {
            double s = b;
            for (int i = 0; i < x.length; i++) if (alpha[i] > 0) s += alpha[i] * y[i] * kern.k(x[i], p);
            return s;
        }

        int supportVectors() { int n = 0; for (double a : alpha) if (a > 1e-9) n++; return n; }

        double[] w() { // linear kernel only
            double[] w = new double[2];
            for (int i = 0; i < x.length; i++) { w[0] += alpha[i] * y[i] * x[i][0]; w[1] += alpha[i] * y[i] * x[i][1]; }
            return w;
        }
    }

    /**
     * Sequential minimal optimization on the dual: minimize 1/2 a'Qa - sum a with Q_ij = y_i y_j K_ij,
     * 0 <= a_i <= C, sum y_i a_i = 0. Each step picks the maximal violating pair and solves for those two exactly.
     */
    static Svm train(double[][] x, int[] y, Kernel kern, double C) {
        int n = x.length;
        double[][] Q = new double[n][n];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) Q[i][j] = y[i] * y[j] * kern.k(x[i], x[j]);
        double[] a = new double[n], G = new double[n];
        Arrays.fill(G, -1);
        int it = 0;
        while (true) {
            int i = -1, j = -1;
            double gmax = Double.NEGATIVE_INFINITY, gmin = Double.POSITIVE_INFINITY;
            for (int t = 0; t < n; t++) {
                boolean up = y[t] == 1 ? a[t] < C : a[t] > 0;
                boolean low = y[t] == 1 ? a[t] > 0 : a[t] < C;
                double v = -y[t] * G[t];
                if (up && v > gmax) { gmax = v; i = t; }
                if (low && v < gmin) { gmin = v; j = t; }
            }
            if (gmax - gmin < 1e-10 || it >= 2_000_000) break;
            it++;
            double ai = a[i], aj = a[j];
            if (y[i] != y[j]) {
                double quad = Q[i][i] + Q[j][j] + 2 * Q[i][j];
                if (quad <= 0) quad = 1e-12;
                double delta = (-G[i] - G[j]) / quad, diff = a[i] - a[j];
                a[i] += delta; a[j] += delta;
                if (diff > 0) { if (a[j] < 0) { a[j] = 0; a[i] = diff; } }
                else { if (a[i] < 0) { a[i] = 0; a[j] = -diff; } }
                if (diff > 0) { if (a[i] > C) { a[i] = C; a[j] = C - diff; } }
                else { if (a[j] > C) { a[j] = C; a[i] = C + diff; } }
            } else {
                double quad = Q[i][i] + Q[j][j] - 2 * Q[i][j];
                if (quad <= 0) quad = 1e-12;
                double delta = (G[i] - G[j]) / quad, sum = a[i] + a[j];
                a[i] -= delta; a[j] += delta;
                if (sum > C) { if (a[i] > C) { a[i] = C; a[j] = sum - C; } }
                else { if (a[j] < 0) { a[j] = 0; a[i] = sum; } }
                if (sum > C) { if (a[j] > C) { a[j] = C; a[i] = sum - C; } }
                else { if (a[i] < 0) { a[i] = 0; a[j] = sum; } }
            }
            double di = a[i] - ai, dj = a[j] - aj;
            for (int k = 0; k < n; k++) G[k] += Q[i][k] * di + Q[j][k] * dj;
        }
        // the offset: from the examples strictly inside (0, C), which sit exactly on the edge of the street
        double sum = 0; int free = 0, ub = 0;
        double hi = Double.POSITIVE_INFINITY, lo = Double.NEGATIVE_INFINITY;
        for (int t = 0; t < n; t++) {
            double yg = y[t] * G[t];
            if (a[t] > 1e-12 && a[t] < C - 1e-12) { sum += yg; free++; }
            else if ((a[t] <= 1e-12) == (y[t] == 1)) hi = Math.min(hi, yg); else lo = Math.max(lo, yg);
        }
        double rho = free > 0 ? sum / free : (hi + lo) / 2;
        Svm m = new Svm();
        m.x = x; m.y = y; m.alpha = a; m.b = -rho; m.kern = kern; m.C = C; m.iterations = it;
        for (int t = 0; t < n; t++) if (a[t] < 1e-12) a[t] = 0;
        // the optimality (KKT) conditions, checked for every example
        for (int t = 0; t < n; t++) {
            double yf = y[t] * m.f(x[t]);
            if (a[t] == 0) check(yf >= 1 - 1e-6, "an example with alpha 0 is outside the street");
            else if (a[t] >= C - 1e-9) check(yf <= 1 + 1e-6, "an example with alpha C is inside the street or beyond");
            else check(Math.abs(yf - 1) < 1e-6, "a free support vector is exactly on the edge of the street");
        }
        double ya = 0;
        for (int t = 0; t < n; t++) ya += y[t] * a[t];
        check(Math.abs(ya) < 1e-9, "sum of y_i alpha_i is zero");
        return m;
    }

    static int errors(Svm m, double[][] x, int[] y) {
        int e = 0;
        for (int i = 0; i < x.length; i++) if (m.f(x[i]) * y[i] <= 0) e++;
        return e;
    }

    /** The widest street over all directions: margin(theta) = (min over +1 of u.x - max over -1 of u.x) / 2. */
    static double gapAt(double th, double[][] x, int[] y) {
        double c = Math.cos(th), s = Math.sin(th), minP = Double.POSITIVE_INFINITY, maxN = Double.NEGATIVE_INFINITY;
        for (int i = 0; i < x.length; i++) {
            double v = c * x[i][0] + s * x[i][1];
            if (y[i] == 1) minP = Math.min(minP, v); else maxN = Math.max(maxN, v);
        }
        return (minP - maxN) / 2;
    }

    static double bestStreetBySearch(double[][] x, int[] y) {
        int steps = 200_000;
        double best = Double.NEGATIVE_INFINITY, bestTh = 0;
        for (int k = 0; k < steps; k++) {
            double th = 2 * Math.PI * k / steps, g = gapAt(th, x, y);
            if (g > best) { best = g; bestTh = th; }
        }
        double lo = bestTh - 2 * Math.PI / steps, hi = bestTh + 2 * Math.PI / steps; // golden-section refinement
        double phi = (Math.sqrt(5) - 1) / 2;
        for (int k = 0; k < 200; k++) {
            double m1 = hi - phi * (hi - lo), m2 = lo + phi * (hi - lo);
            if (gapAt(m1, x, y) < gapAt(m2, x, y)) lo = m1; else hi = m2;
        }
        return gapAt((lo + hi) / 2, x, y);
    }

    public static void main(String[] args) {
        // ---- 1. separable points: the widest street ----------------------------------------------------------------
        s32 = 1992;
        int n1 = 60;
        double[][] x1 = new double[n1][];
        int[] y1 = new int[n1];
        for (int i = 0; i < n1; ) { // keep points at least 0.06 from the line x + y = 1
            double px = next32(), py = next32(), d = (px + py - 1) / Math.sqrt(2);
            if (Math.abs(d) < 0.06) continue;
            x1[i] = new double[]{px, py}; y1[i] = d > 0 ? 1 : -1; i++;
        }
        Svm hard = train(x1, y1, LINEAR, 1e9);
        double[] w = hard.w();
        double street = 1 / Math.hypot(w[0], w[1]);
        double searched = bestStreetBySearch(x1, y1);
        check(Math.abs(street - searched) < 1e-7, "the machine's street equals the widest found by searching every direction");
        check(errors(hard, x1, y1) == 0, "no training errors on separable points");
        // the perceptron (Era 5) on the same points, in the same order
        double pw0 = 0, pw1 = 0, pb = 0;
        int sweeps = 0, mistakesTotal = 0;
        boolean clean = false;
        while (!clean) {
            clean = true; sweeps++;
            for (int i = 0; i < n1; i++) {
                if (y1[i] * (pw0 * x1[i][0] + pw1 * x1[i][1] + pb) <= 0) {
                    pw0 += y1[i] * x1[i][0]; pw1 += y1[i] * x1[i][1]; pb += y1[i]; clean = false; mistakesTotal++;
                }
            }
        }
        double pm = Double.POSITIVE_INFINITY;
        for (int i = 0; i < n1; i++) pm = Math.min(pm, y1[i] * (pw0 * x1[i][0] + pw1 * x1[i][1] + pb) / Math.hypot(pw0, pw1));
        check(pm > 0 && pm < street, "the perceptron's line separates, with a narrower street");
        System.out.printf("separable: %d points in the unit square, labelled by the side of the line x + y = 1, none closer than 0.06 to it ; widest street: half-width %.5f, found by %d two-alpha steps, %d support vectors ; a search over 200,000 directions with refinement gives %.5f ; line: w = (%.3f, %.3f), b = %.3f ; perceptron, same points in the same order: %d sweeps, %d corrections, half-width %.5f (%.0f%% of the widest)%n",
                n1, street, hard.iterations, hard.supportVectors(), searched, w[0], w[1], hard.b, sweeps, mistakesTotal, pm, 100 * pm / street);

        // ---- 2. the kernel trick ------------------------------------------------------------------------------------
        double worst = 0;
        int trials = 100_000;
        s32 = 7;
        for (int t = 0; t < trials; t++) {
            double[] p = {4 * next32() - 2, 4 * next32() - 2}, q = {4 * next32() - 2, 4 * next32() - 2};
            double r2 = Math.sqrt(2);
            double[] fp = {1, r2 * p[0], r2 * p[1], p[0] * p[0], p[1] * p[1], r2 * p[0] * p[1]};
            double[] fq = {1, r2 * q[0], r2 * q[1], q[0] * q[0], q[1] * q[1], r2 * q[0] * q[1]};
            double dot = 0;
            for (int k = 0; k < 6; k++) dot += fp[k] * fq[k];
            double kv = POLY2.k(p, q);
            worst = Math.max(worst, Math.abs(dot - kv) / Math.max(1, Math.abs(kv)));
            check(Math.abs(dot - kv) <= 1e-12 * Math.max(1, Math.abs(kv)), "(x.z + 1)^2 equals the dot product of the six features");
        }
        System.out.printf("trick: (x . z + 1)^2 against the dot product of (1, sqrt2 x1, sqrt2 x2, x1^2, x2^2, sqrt2 x1 x2) for %,d random pairs: largest relative difference %.1e%n", trials, worst);

        // ---- 3. a disc inside a ring --------------------------------------------------------------------------------
        s32 = 1964;
        double[][] x3 = new double[200][];
        int[] y3 = new int[200];
        double[][] t3 = new double[4000][];
        int[] ty3 = new int[4000];
        fillRing(x3, y3); fillRing(t3, ty3);
        StringJoiner rj = new StringJoiner(" ; ");
        Object[][] kernels = {{"linear", LINEAR}, {"degree-2 polynomial", POLY2}, {"Gaussian, gamma 10", gaussian(10)}};
        int linTrain = 0, polyTrain = -1, gaussTest = -1, polyTest = -1;
        for (Object[] kk : kernels) {
            Svm m = train(x3, y3, (Kernel) kk[1], 10);
            int tr = errors(m, x3, y3), te = errors(m, t3, ty3);
            rj.add(String.format("%s kernel: %d of 200 training points wrong, %d of 4,000 test points wrong (%.1f%%), %d support vectors", kk[0], tr, te, 100.0 * te / 4000, m.supportVectors()));
            if (kk[0].equals("linear")) linTrain = tr;
            if (kk[0].equals("degree-2 polynomial")) { polyTrain = tr; polyTest = te; }
            if (((String) kk[0]).startsWith("Gaussian")) gaussTest = te;
        }
        check(linTrain >= 50, "no line separates a disc from the ring around it");
        check(polyTrain == 0 && polyTest < 40 && gaussTest < 80, "the curved kernels separate them");
        System.out.printf("kernel: 200 training points, 100 labelled +1 inside the disc of radius 0.3 and 100 labelled -1 in the ring from 0.5 to 0.8, C = 10 ; %s%n", rj);

        // ---- 4. two overlapping clouds: the soft margin ------------------------------------------------------------
        s32 = 1995;
        double[][] x4 = new double[200][];
        int[] y4 = new int[200];
        double[][] t4 = new double[5000][];
        int[] ty4 = new int[5000];
        fillClouds(x4, y4); fillClouds(t4, ty4);
        StringJoiner sj = new StringJoiner(" ; ");
        double prevStreet = Double.POSITIVE_INFINITY;
        int bestTe = Integer.MAX_VALUE; double bestC = 0;
        for (double C : new double[]{0.01, 0.1, 1, 10, 100}) {
            Svm m = train(x4, y4, LINEAR, C);
            double[] ww = m.w();
            double half = 1 / Math.hypot(ww[0], ww[1]);
            check(half <= prevStreet + 1e-9, "a larger C never widens the street");
            prevStreet = half;
            int inside = 0;
            for (int i = 0; i < x4.length; i++) if (y4[i] * m.f(x4[i]) < 1 - 1e-9) inside++;
            int tr = errors(m, x4, y4), te = errors(m, t4, ty4);
            if (te < bestTe) { bestTe = te; bestC = C; }
            sj.add(String.format("C = %s: half-width %.3f, %d support vectors, %d points inside the street or beyond, %d training errors, test error %.2f%%", fmtC(C), half, m.supportVectors(), inside, tr, 100.0 * te / 5000));
        }
        System.out.printf("soft: two Gaussian clouds of 100 points each, centres (-1, 0) and (1, 0), spread 0.8, linear kernel ; tested on 5,000 more ; %s ; best test error at C = %s%n", sj, fmtC(bestC));

        // ---- 5. the widget's points --------------------------------------------------------------------------------
        s32 = 2008;
        double[][] x5 = new double[40][];
        int[] y5 = new int[40];
        for (int i = 0; i < 40; i++) {
            double px = next32(), py = next32(), u = next32();
            x5[i] = new double[]{px, py};
            y5[i] = px + py + 0.4 * (u - 0.5) > 1 ? 1 : -1;
        }
        StringJoiner wj = new StringJoiner(" ; ");
        for (double C : new double[]{0.1, 1, 10, 100}) {
            Svm m = train(x5, y5, LINEAR, C);
            double[] ww = m.w();
            StringJoiner sv = new StringJoiner(",");
            for (int i = 0; i < 40; i++) if (m.alpha[i] > 0) sv.add(Integer.toString(i));
            wj.add(String.format("C=%s: w=(%.4f, %.4f) b=%.4f half-width=%.4f steps=%d errors=%d support=%s", fmtC(C), ww[0], ww[1], m.b, 1 / Math.hypot(ww[0], ww[1]), m.iterations, errors(m, x5, y5), sv));
        }
        System.out.printf("widget: 40 points from the 32-bit generator s = 1664525 s + 1013904223 (mod 2^32), seed 2008, three numbers per point (x, y, u), label +1 if x + y + 0.4 (u - 0.5) > 1 ; %s%n", wj);

        System.out.println("SupportVectorMachines: " + passed + " checks passed");
    }

    static String fmtC(double C) { return C == Math.rint(C) ? Long.toString((long) C) : Double.toString(C); }

    /** Half the points in the disc of radius 0.3, half in the ring from 0.5 to 0.8, alternating. */
    static void fillRing(double[][] x, int[] y) {
        for (int i = 0; i < x.length; ) {
            double px = 2 * next32() - 1, py = 2 * next32() - 1, r = Math.hypot(px, py);
            boolean wantDisc = i % 2 == 0;
            if (wantDisc && r < 0.3) { x[i] = new double[]{px, py}; y[i++] = 1; }
            else if (!wantDisc && r > 0.5 && r < 0.8) { x[i] = new double[]{px, py}; y[i++] = -1; }
        }
    }

    static void fillClouds(double[][] x, int[] y) {
        for (int i = 0; i < x.length; i++) {
            int lab = i % 2 == 0 ? 1 : -1;
            x[i] = new double[]{lab + 0.8 * gauss(), 0.8 * gauss()};
            y[i] = lab;
        }
    }
}
