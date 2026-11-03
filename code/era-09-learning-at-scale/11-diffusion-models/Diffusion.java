import java.util.*;

/**
 * Era 9, topic 11: Diffusion models (Jascha Sohl-Dickstein, Eric A. Weiss, Niru Maheswaranathan and Surya Ganguli,
 * 2015; Jonathan Ho, Ajay Jain and Pieter Abbeel, UC Berkeley, 2020).
 *
 * HOW IT WORKS
 *   The forward process destroys data a little at a time: x_t = sqrt(1 - beta_t) x_(t-1) + sqrt(beta_t) * noise, for
 *   t = 1 to T = 1000, with beta rising from 0.0001 to 0.02. After all the steps, x_T is indistinguishable from
 *   pure Gaussian noise. Any step can be reached at once: x_t = sqrt(abar_t) x_0 + sqrt(1 - abar_t) eps, where
 *   abar_t is the product of (1 - beta_s) for s up to t and eps is standard Gaussian noise.
 *   Training: take a data point x_0, a random t and fresh noise eps, form x_t, and teach a network eps_theta(x_t, t)
 *   to guess eps (squared error). Sampling: start from pure noise x_T and for t = T down to 1 remove the predicted
 *   noise, x_(t-1) = (x_t - beta_t / sqrt(1 - abar_t) * eps_theta(x_t, t)) / sqrt(1 - beta_t) + sqrt(beta_t) z,
 *   with fresh Gaussian z (none at the last step). Points the network never saw appear, shaped like the data.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The forward process on a two-armed spiral of points: running 1,000 small steps agrees with the closed form,
 *      and at the end the points have the mean and spread of pure noise.
 *   2. Trains a small network (time-embedded, two hidden layers, gradients written by hand and checked) to predict
 *      the noise, with Adam (topic 5).
 *   3. Samples new points from pure noise by the reverse process, and measures how close they lie to the spiral,
 *      against fresh spiral points and against plain Gaussian points; also with the network replaced by zero.
 *   4. Prints the trained weights and a few sample paths for the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Diffusion.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Diffusion {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int T = 1000, F = 8, IN = 2 + 2 * F, H = 64;
    static final double[] beta = new double[T + 1], alpha = new double[T + 1], abar = new double[T + 1];

    static {
        abar[0] = 1;
        for (int t = 1; t <= T; t++) {
            beta[t] = 1e-4 + (0.02 - 1e-4) * (t - 1) / (T - 1);
            alpha[t] = 1 - beta[t];
            abar[t] = abar[t - 1] * alpha[t];
        }
    }

    /** A point on a two-armed spiral, scaled to about unit spread. */
    static double[] spiral(Random r) {
        double s = Math.sqrt(r.nextDouble());
        double ang = 4.2 * s + (r.nextBoolean() ? Math.PI : 0);
        return new double[]{1.6 * s * Math.cos(ang) + 0.04 * r.nextGaussian(), 1.6 * s * Math.sin(ang) + 0.04 * r.nextGaussian()};
    }

    // ---- the network: [x, y, sin/cos of t at F frequencies] -> H -> H -> 2 ---------------------------------------------
    static class Net {
        double[][] W1 = new double[H][IN], W2 = new double[H][H], W3 = new double[2][H];
        double[] b1 = new double[H], b2 = new double[H], b3 = new double[2];

        Net(Random r) {
            for (double[] row : W1) for (int j = 0; j < IN; j++) row[j] = r.nextGaussian() * Math.sqrt(2.0 / IN);
            for (double[] row : W2) for (int j = 0; j < H; j++) row[j] = r.nextGaussian() * Math.sqrt(2.0 / H);
            for (double[] row : W3) for (int j = 0; j < H; j++) row[j] = r.nextGaussian() * Math.sqrt(1.0 / H);
        }

        Net() {}
    }

    static double[] embed(double x, double y, int t) {
        double[] e = new double[IN];
        e[0] = x; e[1] = y;
        for (int k = 0; k < F; k++) {
            double w = t / 1000.0 * Math.pow(2, k) * Math.PI / 2;
            e[2 + 2 * k] = Math.sin(w); e[3 + 2 * k] = Math.cos(w);
        }
        return e;
    }

    /** Predicted noise; when g is not null, adds the gradient of 0.5 |pred - eps|^2 to g and returns the loss. */
    static double[] forward(Net n, double[] in, double[] eps, Net g, double[] lossOut) {
        double[] h1 = new double[H], h2 = new double[H], out = new double[2];
        for (int i = 0; i < H; i++) { double s = n.b1[i]; for (int j = 0; j < IN; j++) s += n.W1[i][j] * in[j]; h1[i] = Math.max(0, s); }
        for (int i = 0; i < H; i++) { double s = n.b2[i]; for (int j = 0; j < H; j++) s += n.W2[i][j] * h1[j]; h2[i] = Math.max(0, s); }
        for (int i = 0; i < 2; i++) { double s = n.b3[i]; for (int j = 0; j < H; j++) s += n.W3[i][j] * h2[j]; out[i] = s; }
        if (g == null) return out;
        double[] d3 = {out[0] - eps[0], out[1] - eps[1]};
        lossOut[0] += 0.5 * (d3[0] * d3[0] + d3[1] * d3[1]);
        double[] d2 = new double[H], d1 = new double[H];
        for (int i = 0; i < 2; i++) { g.b3[i] += d3[i]; for (int j = 0; j < H; j++) { g.W3[i][j] += d3[i] * h2[j]; d2[j] += d3[i] * n.W3[i][j]; } }
        for (int i = 0; i < H; i++) {
            if (h2[i] <= 0) continue;
            g.b2[i] += d2[i];
            for (int j = 0; j < H; j++) { g.W2[i][j] += d2[i] * h1[j]; d1[j] += d2[i] * n.W2[i][j]; }
        }
        for (int i = 0; i < H; i++) {
            if (h1[i] <= 0) continue;
            g.b1[i] += d1[i];
            for (int j = 0; j < IN; j++) g.W1[i][j] += d1[i] * in[j];
        }
        return out;
    }

    /** Every parameter, as a list of (array, index) views for the optimizer and the gradient check. */
    static List<double[]> rows(Net n) {
        List<double[]> L = new ArrayList<>();
        L.addAll(Arrays.asList(n.W1)); L.addAll(Arrays.asList(n.W2)); L.addAll(Arrays.asList(n.W3));
        L.add(n.b1); L.add(n.b2); L.add(n.b3);
        return L;
    }

    static double[][] sample(Net n, int count, Random r, boolean zeroNet, List<double[][]> paths) {
        double[][] x = new double[count][2];
        for (double[] p : x) { p[0] = r.nextGaussian(); p[1] = r.nextGaussian(); }
        for (int t = T; t >= 1; t--) {
            for (int i = 0; i < count; i++) {
                double[] e = zeroNet ? new double[2] : forward(n, embed(x[i][0], x[i][1], t), null, null, null);
                for (int c = 0; c < 2; c++) {
                    double mean = (x[i][c] - beta[t] / Math.sqrt(1 - abar[t]) * e[c]) / Math.sqrt(alpha[t]);
                    x[i][c] = mean + (t > 1 ? Math.sqrt(beta[t]) * r.nextGaussian() : 0);
                }
                if (paths != null && i < paths.size() && (t - 1) % 50 == 0) paths.get(i)[(T - t + 1) / 50] = x[i].clone();
            }
        }
        return x;
    }

    /** Mean distance from each point to the nearest of the reference points. */
    static double nnDist(double[][] pts, double[][] ref) {
        double s = 0;
        for (double[] p : pts) {
            double best = 1e9;
            for (double[] q : ref) best = Math.min(best, Math.hypot(p[0] - q[0], p[1] - q[1]));
            s += best;
        }
        return s / pts.length;
    }

    public static void main(String[] args) {
        Random r = new Random(11);

        // ---- 1. the forward process ----------------------------------------------------------------------------------
        int M = 4000;
        double[][] x0 = new double[M][];
        for (int i = 0; i < M; i++) x0[i] = spiral(r);
        double[][] xs = new double[M][2];
        for (int i = 0; i < M; i++) xs[i] = x0[i].clone();
        double maxDiff = 0;
        StringJoiner fj = new StringJoiner(" ; ");
        for (int t = 1; t <= T; t++) {
            for (double[] p : xs) for (int c = 0; c < 2; c++) p[c] = Math.sqrt(alpha[t]) * p[c] + Math.sqrt(beta[t]) * r.nextGaussian();
            if (t == 100 || t == 300 || t == 1000) {
                // the closed form predicts, for each point, mean sqrt(abar) x0 and variance 1 - abar: compare the averages
                double resid = 0, rv = 0;
                for (int i = 0; i < M; i++) for (int c = 0; c < 2; c++) {
                    double d = xs[i][c] - Math.sqrt(abar[t]) * x0[i][c];
                    resid += d / (2 * M); rv += d * d / (2 * M);
                }
                maxDiff = Math.max(maxDiff, Math.abs(rv - (1 - abar[t])));
                double mx = 0, vx = 0;
                for (double[] p : xs) mx += p[0] / M;
                for (double[] p : xs) vx += (p[0] - mx) * (p[0] - mx) / M;
                fj.add(String.format("t = %d: abar %.5f, step by step the leftover noise has variance %.3f, the closed form says %.3f ; spread of x %.3f", t, abar[t], rv, 1 - abar[t], Math.sqrt(vx)));
            }
        }
        check(maxDiff < 0.03, "1,000 small steps agree with the closed form");
        check(abar[T] < 1e-4, "after 1,000 steps almost nothing of the data is left");
        System.out.printf("forward: beta from %.4f to %.2f over T = %d steps, %,d spiral points ; %s ; sqrt(abar_T) = %.4f of the data is left%n",
                beta[1], beta[T], T, M, fj, Math.sqrt(abar[T]));

        // ---- 2a. gradient check -----------------------------------------------------------------------------------------
        Net net = new Net(new Random(12));
        double worst = 0;
        {
            Net g = new Net();
            double[] in = embed(0.3, -0.7, 420), eps = {0.5, -1.2}, L = {0};
            forward(net, in, eps, g, L);
            List<double[]> P = rows(net), G = rows(g);
            Random pr = new Random(13);
            int tested = 0;
            while (tested < 60) {
                int k = pr.nextInt(P.size()), j = pr.nextInt(P.get(k).length);
                if (Math.abs(G.get(k)[j]) < 1e-9) continue;
                double old = P.get(k)[j], h = 1e-6;
                double[] lp = {0}, lm = {0};
                P.get(k)[j] = old + h; forward(net, in, eps, new Net(), lp);
                P.get(k)[j] = old - h; forward(net, in, eps, new Net(), lm);
                P.get(k)[j] = old;
                double num = (lp[0] - lm[0]) / (2 * h);
                worst = Math.max(worst, Math.abs(num - G.get(k)[j]) / (Math.abs(num) + Math.abs(G.get(k)[j])));
                tested++;
            }
        }
        check(worst < 1e-5, "hand-written gradients match finite differences");

        // ---- 2b. training --------------------------------------------------------------------------------------------------
        int steps = 12000, B = 64;
        List<double[]> P = rows(net);
        List<double[]> Mm = new ArrayList<>(), Vv = new ArrayList<>();
        for (double[] p : P) { Mm.add(new double[p.length]); Vv.add(new double[p.length]); }
        StringJoiner lj = new StringJoiner(",");
        double run = 0;
        for (int step = 1; step <= steps; step++) {
            Net g = new Net();
            double[] L = {0};
            for (int b = 0; b < B; b++) {
                double[] p = spiral(r);
                int t = 1 + r.nextInt(T);
                double[] eps = {r.nextGaussian(), r.nextGaussian()};
                double sa = Math.sqrt(abar[t]), sn = Math.sqrt(1 - abar[t]);
                forward(net, embed(sa * p[0] + sn * eps[0], sa * p[1] + sn * eps[1], t), eps, g, L);
            }
            run += L[0] / B;
            List<double[]> G = rows(g);
            double lr = step < 9000 ? 2e-3 : 5e-4;
            for (int k = 0; k < P.size(); k++) {
                double[] p = P.get(k), gg = G.get(k), m = Mm.get(k), v = Vv.get(k);
                for (int j = 0; j < p.length; j++) {
                    double gi = gg[j] / B;
                    m[j] = 0.9 * m[j] + 0.1 * gi; v[j] = 0.999 * v[j] + 0.001 * gi * gi;
                    p[j] -= lr * (m[j] / (1 - Math.pow(0.9, step))) / (Math.sqrt(v[j] / (1 - Math.pow(0.999, step))) + 1e-8);
                }
            }
            if (step % 1000 == 0) { lj.add(String.format("%.3f", 2 * run / 1000)); run = 0; }
        }
        int params = H * IN + H + H * H + H + 2 * H + 2;
        System.out.printf("train: network [x, y, %d sines and cosines of t] -> %d -> %d -> 2, ReLU, %,d parameters ; gradient check: largest relative difference %.1e ; Adam, %,d steps of %d noisy points, t uniform from 1 to %d ; mean squared error of the noise guess (a guess of 0 scores 2.0) every 1,000 steps: %s%n",
                2 * F, H, H, params, worst, steps, B, T, lj);

        // ---- 3. sampling ---------------------------------------------------------------------------------------------------
        int S = 600;
        double[][] ref = new double[3000][];
        for (int i = 0; i < ref.length; i++) ref[i] = spiral(r);
        List<double[][]> paths = new ArrayList<>();
        for (int i = 0; i < 6; i++) paths.add(new double[T / 50 + 1][]);
        double[][] gen = sample(net, S, new Random(21), false, paths);
        double[][] fresh = new double[S][], gauss = new double[S][];
        for (int i = 0; i < S; i++) { fresh[i] = spiral(r); gauss[i] = new double[]{r.nextGaussian(), r.nextGaussian()}; }
        double[][] zero = sample(net, S, new Random(22), true, null);
        double dGen = nnDist(gen, ref), dFresh = nnDist(fresh, ref), dGauss = nnDist(gauss, ref), dZero = nnDist(zero, ref);
        // which arm: an arm-0 point at radius 1.6 s has angle 4.2 s; an arm-1 point is turned by half a circle
        int armA = 0;
        for (double[] p : gen) {
            double s = Math.hypot(p[0], p[1]) / 1.6, da = Math.abs(Math.IEEEremainder(Math.atan2(p[1], p[0]) - 4.2 * s, 2 * Math.PI));
            if (da < Math.PI / 2) armA++;
        }
        System.out.printf("sample: %d new points from pure noise, %,d reverse steps each ; mean distance to the nearest of 3,000 spiral points: generated %.4f, fresh spiral points %.4f, Gaussian noise %.4f, reverse process with the network replaced by 0: %.4f ; generated points on the first arm %d, on the second %d%n",
                S, T, dGen, dFresh, dGauss, dZero, armA, S - armA);

        check(dGen < 0.15 * dGauss, "generated points lie close to the spiral, far closer than noise");
        check(dZero > dGauss, "the reverse process without a trained network does not produce the spiral");
        check(Math.abs(armA - (S - armA)) < S / 5, "both arms are generated, about equally");
        // ---- 4. for the widget ---------------------------------------------------------------------------------------------
        StringJoiner pj = new StringJoiner(" ; ");
        for (double[][] path : paths) {
            StringJoiner one = new StringJoiner(" ");
            for (double[] p : path) if (p != null) one.add(String.format("%.3f,%.3f", p[0], p[1]));
            pj.add(one.toString());
        }
        System.out.printf("paths: 6 points, every 50 steps from t = 1000 to the end ; %s%n", pj);
        StringJoiner gj = new StringJoiner(" ");
        for (int i = 0; i < 200; i++) gj.add(String.format("%.3f,%.3f", gen[i][0], gen[i][1]));
        System.out.printf("points: 200 generated ; %s%n", gj);
        StringBuilder wb = new StringBuilder("weights:");
        String[] names = {"W1", "W2", "W3", "b1", "b2", "b3"};
        double[][][] mats = {net.W1, net.W2, net.W3, {net.b1}, {net.b2}, {net.b3}};
        for (int k = 0; k < names.length; k++) {
            StringJoiner one = new StringJoiner(",");
            for (double[] row : mats[k]) for (double v : row) one.add(String.format("%.4f", v));
            wb.append(" ; ").append(names[k]).append(' ').append(mats[k].length).append('x').append(mats[k][0].length).append(' ').append(one);
        }
        // rounded weights must give the same quality
        Net rn = new Net();
        double[][][] rm = {rn.W1, rn.W2, rn.W3, {rn.b1}, {rn.b2}, {rn.b3}};
        for (int k = 0; k < names.length; k++) for (int i = 0; i < mats[k].length; i++) for (int j = 0; j < mats[k][i].length; j++) rm[k][i][j] = Math.round(mats[k][i][j] * 1e4) / 1e4;
        double dR = nnDist(sample(rn, 300, new Random(23), false, null), ref);
        check(dR < 0.15 * dGauss, "the rounded weights still generate the spiral");
        System.out.println(wb);

        System.out.println("Diffusion: " + passed + " checks passed");
    }
}
