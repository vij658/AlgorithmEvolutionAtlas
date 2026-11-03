import java.util.*;

/**
 * Era 9, topic 5: Adam (Diederik P. Kingma and Jimmy Lei Ba, arXiv December 2014, ICLR 2015).
 *
 * HOW IT WORKS
 *   Gradient descent moves every parameter against its gradient g by a step of size alpha * g. Adam gives every
 *   parameter its own step. It keeps two running averages of that parameter's gradient:
 *     m = beta1 * m + (1 - beta1) * g          (the mean, like momentum)
 *     v = beta2 * v + (1 - beta2) * g * g      (the mean square, like RMSProp)
 *   Both start at zero, so early on they are too small; dividing by (1 - beta1^t) and (1 - beta2^t) corrects that.
 *   The step is alpha * mhat / (sqrt(vhat) + eps). Its size is about alpha whatever the scale of the gradient: a
 *   parameter whose gradients are tiny moves as far as one whose gradients are huge. The paper's defaults are
 *   alpha = 0.001, beta1 = 0.9, beta2 = 0.999, eps = 1e-8.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Five methods (SGD, momentum, AdaGrad, RMSProp, Adam) on three problems: a small neural network on two
 *      interleaved spirals, logistic regression with rare features, and a long narrow valley with noisy gradients.
 *      Each method gets its best learning rate from the same grid; the program also counts how many rates of the
 *      grid come within a factor 2 of that method's best loss.
 *   2. Adam's bias correction: the factor by which the first steps would be wrong without it, and the effect on the
 *      neural network.
 *   3. Invariance: multiply one parameter's gradients by 1,000 and Adam's path does not change.
 *   4. A convex problem on which Adam's steps keep the point at the wrong end, and AMSGrad, which steps by the
 *      largest mean square so far, reaches the right end.
 *   5. Paths on a two-dimensional valley for the page.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Adam.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Adam {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- the optimizers ---------------------------------------------------------------------------------------------
    static final String[] NAMES = {"SGD", "momentum", "AdaGrad", "RMSProp", "Adam"};

    /** One optimizer's state for a parameter vector of length n. */
    static class Opt {
        final int kind; final double lr; final double[] m, v, vmax; int t = 0;
        boolean biasCorrection = true, amsgrad = false;
        double b1 = 0.9, b2 = 0.999, eps = 1e-8;

        Opt(int kind, double lr, int n) { this.kind = kind; this.lr = lr; m = new double[n]; v = new double[n]; vmax = new double[n]; }

        void step(double[] w, double[] g) {
            t++;
            for (int i = 0; i < w.length; i++) {
                switch (kind) {
                    case 0 -> w[i] -= lr * g[i];
                    case 1 -> { m[i] = 0.9 * m[i] + g[i]; w[i] -= lr * m[i]; }
                    case 2 -> { v[i] += g[i] * g[i]; w[i] -= lr * g[i] / (Math.sqrt(v[i]) + 1e-8); }
                    case 3 -> { v[i] = 0.9 * v[i] + 0.1 * g[i] * g[i]; w[i] -= lr * g[i] / (Math.sqrt(v[i]) + 1e-8); }
                    default -> {
                        m[i] = b1 * m[i] + (1 - b1) * g[i];
                        v[i] = b2 * v[i] + (1 - b2) * g[i] * g[i];
                        double mh = m[i], vh = v[i];
                        if (amsgrad) { vmax[i] = Math.max(vmax[i], v[i]); vh = vmax[i]; }
                        if (biasCorrection) { mh /= 1 - Math.pow(b1, t); vh /= 1 - Math.pow(b2, t); }
                        w[i] -= lr * mh / (Math.sqrt(vh) + eps);
                    }
                }
            }
        }
    }

    interface Problem {
        int size();
        double[] init(Random r);
        double gradient(double[] w, Random r, double[] g); // stochastic gradient into g; returns the minibatch loss
        double loss(double[] w);                             // full loss
    }

    // ---- problem 1: a small network on two spirals ---------------------------------------------------------------------
    static class Spirals implements Problem {
        final int H = 16, n = 400;
        final double[][] X = new double[n][2];
        final int[] Y = new int[n];

        Spirals() {
            Random r = new Random(1);
            for (int i = 0; i < n; i++) {
                int c = i % 2;
                double t = 0.25 + 3.0 * (i / 2) / (n / 2.0), a = t * 2.2 + c * Math.PI;
                X[i][0] = t * Math.cos(a) / 3.3 + 0.03 * r.nextGaussian();
                X[i][1] = t * Math.sin(a) / 3.3 + 0.03 * r.nextGaussian();
                Y[i] = c;
            }
        }

        // layout: W1 (H x 2), b1 (H), W2 (H x H), b2 (H), w3 (H), b3
        public int size() { return H * 2 + H + H * H + H + H + 1; }

        public double[] init(Random r) {
            double[] w = new double[size()];
            int k = 0;
            for (int i = 0; i < H * 2; i++) w[k++] = r.nextGaussian() * Math.sqrt(1.0 / 2);
            k += H;
            for (int i = 0; i < H * H; i++) w[k++] = r.nextGaussian() * Math.sqrt(1.0 / H);
            k += H;
            for (int i = 0; i < H; i++) w[k++] = r.nextGaussian() * Math.sqrt(1.0 / H);
            return w;
        }

        double example(double[] w, int e, double[] g) {
            int o1 = 0, ob1 = 2 * H, o2 = 3 * H, ob2 = 3 * H + H * H, o3 = 4 * H + H * H, ob3 = 5 * H + H * H;
            double[] h1 = new double[H], h2 = new double[H];
            for (int j = 0; j < H; j++) h1[j] = Math.tanh(w[o1 + 2 * j] * X[e][0] + w[o1 + 2 * j + 1] * X[e][1] + w[ob1 + j]);
            for (int j = 0; j < H; j++) {
                double s = w[ob2 + j];
                for (int k = 0; k < H; k++) s += w[o2 + j * H + k] * h1[k];
                h2[j] = Math.tanh(s);
            }
            double z = w[ob3];
            for (int j = 0; j < H; j++) z += w[o3 + j] * h2[j];
            double p = 1 / (1 + Math.exp(-z));
            double loss = -(Y[e] == 1 ? Math.log(p + 1e-12) : Math.log(1 - p + 1e-12));
            if (g == null) return loss;
            double dz = p - Y[e];
            double[] d2 = new double[H], d1 = new double[H];
            g[ob3] += dz;
            for (int j = 0; j < H; j++) { g[o3 + j] += dz * h2[j]; d2[j] = dz * w[o3 + j] * (1 - h2[j] * h2[j]); }
            for (int j = 0; j < H; j++) {
                g[ob2 + j] += d2[j];
                for (int k = 0; k < H; k++) { g[o2 + j * H + k] += d2[j] * h1[k]; d1[k] += d2[j] * w[o2 + j * H + k]; }
            }
            for (int k = 0; k < H; k++) {
                double dk = d1[k] * (1 - h1[k] * h1[k]);
                g[o1 + 2 * k] += dk * X[e][0]; g[o1 + 2 * k + 1] += dk * X[e][1]; g[ob1 + k] += dk;
            }
            return loss;
        }

        public double gradient(double[] w, Random r, double[] g) {
            Arrays.fill(g, 0);
            int B = 16;
            double L = 0;
            for (int b = 0; b < B; b++) L += example(w, r.nextInt(n), g);
            for (int i = 0; i < g.length; i++) g[i] /= B;
            return L / B;
        }

        public double loss(double[] w) {
            double L = 0;
            for (int e = 0; e < n; e++) L += example(w, e, null);
            return L / n;
        }
    }

    // ---- problem 2: logistic regression where most features are rare -------------------------------------------------
    static class Sparse implements Problem {
        final int D = 500, n = 4000, active = 8;
        final int[][] F = new int[n][active];
        final int[] Y = new int[n];

        Sparse() {
            Random r = new Random(2);
            double[] truth = new double[D];
            for (int j = 0; j < D; j++) truth[j] = r.nextGaussian() * 2;
            for (int i = 0; i < n; i++) {
                double s = 0;
                for (int a = 0; a < active; a++) {
                    int j = (int) Math.min(D - 1, Math.floor(Math.exp(r.nextDouble() * Math.log(D)))) ; // feature j drawn with weight about 1/j: a few common, most rare
                    F[i][a] = j; s += truth[j] / Math.sqrt(active);
                }
                Y[i] = r.nextDouble() < 1 / (1 + Math.exp(-s)) ? 1 : 0;
            }
        }

        public int size() { return D; }

        public double[] init(Random r) { return new double[D]; }

        double example(double[] w, int e, double[] g) {
            double z = 0;
            for (int j : F[e]) z += w[j] / Math.sqrt(active);
            double p = 1 / (1 + Math.exp(-z));
            if (g != null) for (int j : F[e]) g[j] += (p - Y[e]) / Math.sqrt(active);
            return -(Y[e] == 1 ? Math.log(p + 1e-12) : Math.log(1 - p + 1e-12));
        }

        public double gradient(double[] w, Random r, double[] g) {
            Arrays.fill(g, 0);
            int B = 16;
            double L = 0;
            for (int b = 0; b < B; b++) L += example(w, r.nextInt(n), g);
            for (int i = 0; i < g.length; i++) g[i] /= B;
            return L / B;
        }

        public double loss(double[] w) {
            double L = 0;
            for (int e = 0; e < n; e++) L += example(w, e, null);
            return L / n;
        }
    }

    // ---- problem 3: a long narrow valley, with noise in the gradient --------------------------------------------------
    static class Valley implements Problem {
        final int D = 20;
        final double[] lam = new double[D];

        Valley() { for (int i = 0; i < D; i++) lam[i] = Math.pow(1000, i / (D - 1.0)); } // curvatures from 1 to 1,000

        public int size() { return D; }

        public double[] init(Random r) { double[] w = new double[D]; Arrays.fill(w, 1.0); return w; }

        public double gradient(double[] w, Random r, double[] g) {
            for (int i = 0; i < D; i++) g[i] = lam[i] * w[i] + 0.5 * Math.sqrt(lam[i]) * r.nextGaussian();
            return loss(w);
        }

        public double loss(double[] w) {
            double L = 0;
            for (int i = 0; i < D; i++) L += 0.5 * lam[i] * w[i] * w[i];
            return L;
        }
    }

    static final double[] GRID = {1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 0.1, 0.3, 1.0, 3.0};

    /** Train and return the full loss at the end (infinity if it blew up). */
    static double train(Problem p, Opt o, int steps, long seed) {
        Random r = new Random(seed);
        double[] w = p.init(new Random(seed + 1)), g = new double[p.size()];
        for (int s = 0; s < steps; s++) {
            p.gradient(w, r, g);
            o.step(w, g);
        }
        double L = p.loss(w);
        return Double.isFinite(L) && L < 1e6 ? L : Double.POSITIVE_INFINITY;
    }

    static double avgTrain(Problem p, int kind, double lr, int steps) {
        double s = 0;
        for (int seed = 0; seed < 3; seed++) s += train(p, new Opt(kind, lr, p.size()), steps, 100 + seed);
        return s / 3;
    }

    static String lrs(double x) { return x >= 0.01 ? String.valueOf(x) : String.format("%.0e", x).replace("e-0", "e-"); }

    // ---- two-dimensional valley for the page ---------------------------------------------------------------------------
    static double fx(double x, double y) { return 0.5 * (x * x / 10 + 10 * y * y); } // curvature 0.1 along x, 10 along y

    public static void main(String[] args) {
        // ---- 1. the race ----------------------------------------------------------------------------------------------------
        Problem[] probs = {new Spirals(), new Sparse(), new Valley()};
        String[] pname = {"spirals", "rare features", "valley"};
        int[] steps = {2000, 2000, 1000};
        double[][] best = new double[3][5], bestLr = new double[3][5];
        for (int q = 0; q < 3; q++) {
            Problem p = probs[q];
            double start = p.loss(p.init(new Random(101)));
            StringJoiner sj = new StringJoiner(" ; ");
            for (int k = 0; k < 5; k++) {
                StringJoiner all = new StringJoiner(" ");
                best[q][k] = Double.POSITIVE_INFINITY;
                for (int i = 0; i < GRID.length; i++) {
                    double L = avgTrain(p, k, GRID[i], steps[q]);
                    all.add(Double.isFinite(L) ? String.format("%.4f", L) : "diverged");
                    if (L < best[q][k]) { best[q][k] = L; bestLr[q][k] = GRID[i]; }
                }
                sj.add(String.format("%s best rate %s loss %.4f, by rate %s", NAMES[k], lrs(bestLr[q][k]), best[q][k], all));
            }
            check(best[q][4] < start, "Adam improves on the starting loss");
            System.out.printf("race: %s ; %,d parameters, %,d steps, %s, loss at the start %.4f, mean of 3 seeds ; %s%n",
                    pname[q], p.size(), steps[q], q == 2 ? "noise added to every gradient" : "minibatches of 16", start, sj);
        }
        StringJoiner gj = new StringJoiner(" ");
        for (double g : GRID) gj.add(lrs(g));
        // the best rate of each method, across the three problems
        StringJoiner tj = new StringJoiner(" ; ");
        double adamSpread = 0, sgdSpread = 0;
        for (int k = 0; k < 5; k++) {
            double spread = 0;
            for (int q = 0; q < 3; q++) for (int r = 0; r < 3; r++) spread = Math.max(spread, bestLr[q][k] / bestLr[r][k]);
            if (k == 0) sgdSpread = spread;
            if (k == 4) adamSpread = spread;
            tj.add(String.format("%s %s, %s, %s (factor %.0f)", NAMES[k], lrs(bestLr[0][k]), lrs(bestLr[1][k]), lrs(bestLr[2][k]), spread));
        }
        check(adamSpread < sgdSpread, "Adam's best rate moves less across problems than SGD's");
        // Adam's own default, untuned
        StringJoiner dj = new StringJoiner(" ; ");
        for (int q = 0; q < 3; q++) {
            double L = avgTrain(probs[q], 4, 0.001, steps[q]);
            double bestAll = Arrays.stream(best[q]).min().getAsDouble();
            dj.add(String.format("%s %.4f (best of all methods %.4f)", pname[q], L, bestAll));
        }
        System.out.printf("tuning: rates tried %s ; best rate on spirals, rare features, valley: %s ; Adam at its default 0.001, untuned: %s%n", gj, tj, dj);

        // ---- 2. bias correction ---------------------------------------------------------------------------------------------
        StringJoiner bj = new StringJoiner(", ");
        double worst = 0; int worstT = 0;
        for (int t = 1; t <= 200; t++) {
            double f = (1 - Math.pow(0.9, t)) / Math.sqrt(1 - Math.pow(0.999, t)); // step without correction / step with it, for a steady gradient
            if (f > worst) { worst = f; worstT = t; }
            if (t == 1 || t == 10 || t == 100 || t == 1000) bj.add(String.format("step %d: %.2f", t, f));
        }
        for (int t : new int[]{1000, 5000}) bj.add(String.format("step %d: %.2f", t, (1 - Math.pow(0.9, t)) / Math.sqrt(1 - Math.pow(0.999, t))));
        check(Math.abs((1 - 0.9) / Math.sqrt(1 - 0.999) - Math.sqrt(10)) < 1e-9, "the first uncorrected step is sqrt(10) times too long");
        // the spirals, with and without the correction, at Adam's best rate and above
        StringJoiner cj = new StringJoiner(" ; ");
        Problem sp = probs[0];
        double[] rates = {0.003, 0.01, 0.03, 0.1};
        for (double lr : rates) {
            double a = 0, b = 0;
            for (int seed = 0; seed < 3; seed++) {
                a += train(sp, new Opt(4, lr, sp.size()), 300, 100 + seed) / 3;
                Opt o = new Opt(4, lr, sp.size()); o.biasCorrection = false;
                b += train(sp, o, 300, 100 + seed) / 3;
            }
            if (lr == 0.1) check(b > 5 * a, "at rate 0.1 the uncorrected early steps throw the network off");
            cj.add(String.format("rate %s: %.4f corrected, %.4f uncorrected", lrs(lr), a, b));
        }
        System.out.printf("bias: a steady gradient, beta1 0.9, beta2 0.999 ; uncorrected step / corrected step: %s ; largest %.2f at step %d ; spirals after 300 steps, mean of 3 seeds: %s%n",
                bj, worst, worstT, cj);

        // ---- 3. invariance --------------------------------------------------------------------------------------------------
        double maxDiff = 0, sgdDiff = 0;
        {
            Problem v = probs[2];
            double[] w1 = v.init(null), w2 = v.init(null), g1 = new double[v.size()], g2 = new double[v.size()];
            double[] s1 = v.init(null), s2 = v.init(null);
            Opt a1 = new Opt(4, 0.01, v.size()), a2 = new Opt(4, 0.01, v.size()), q1 = new Opt(0, 1e-3, v.size()), q2 = new Opt(0, 1e-3, v.size());
            a2.eps = 0; a1.eps = 0;
            Random r1 = new Random(9), r2 = new Random(9);
            for (int s = 0; s < 500; s++) {
                v.gradient(w1, r1, g1); v.gradient(w2, r2, g2);
                g2[0] *= 1000; // the same problem with parameter 0 measured in different units
                a1.step(w1, g1); a2.step(w2, g2);
                double[] h1 = g1.clone(), h2 = g1.clone(); h2[0] *= 1000;
                q1.step(s1, h1); q2.step(s2, h2);
            }
            for (int i = 0; i < w1.length; i++) maxDiff = Math.max(maxDiff, Math.abs(w1[i] - w2[i]));
            sgdDiff = Math.abs(s1[0] - s2[0]);
        }
        check(maxDiff < 1e-12, "Adam's path is unchanged when one gradient is scaled by 1,000");
        System.out.printf("scale: the valley, gradient of parameter 1 multiplied by 1,000 at every step, 500 steps ; Adam (eps = 0): largest difference in any parameter %.1e ; SGD fed the same gradients: parameter 1 differs by %.2f%n", maxDiff, sgdDiff);

        // ---- 4. a convex problem where Adam goes the wrong way --------------------------------------------------------
        // f_t(x) = 3x on every third step and -x otherwise, x kept in [-1, 1]. The average, (3 - 1 - 1)/3 x = x/3, is
        // smallest at x = -1. One large rare gradient against two small common ones.
        double[] ends = new double[3];
        String[] mname = {"SGD", "Adam (beta1 0, beta2 0.1)", "AMSGrad (the same betas)"};
        for (int k = 0; k < 3; k++) {
            double[] x = {0.0};
            Opt o = new Opt(k == 0 ? 0 : 4, 0, 1);
            o.b1 = 0; o.b2 = 0.1; o.amsgrad = k == 2; o.biasCorrection = false;
            for (int t = 1; t <= 30_000; t++) {
                double g = t % 3 == 1 ? 3 : -1;
                double lr = 0.1 / Math.sqrt(t);
                Opt step = new Opt(o.kind, lr, 1); step.b1 = 0; step.b2 = 0.1; step.amsgrad = o.amsgrad; step.biasCorrection = false;
                step.m[0] = o.m[0]; step.v[0] = o.v[0]; step.vmax[0] = o.vmax[0];
                step.step(x, new double[]{g});
                o.m[0] = step.m[0]; o.v[0] = step.v[0]; o.vmax[0] = step.vmax[0];
                x[0] = Math.max(-1, Math.min(1, x[0]));
            }
            ends[k] = x[0];
        }
        check(ends[0] < -0.99 && ends[2] < -0.99 && ends[1] > 0.99, "SGD and AMSGrad reach x = -1, Adam ends at x = +1");
        System.out.printf("convex: f_t(x) = 3x on every third step, -x on the others, x in [-1, 1], best x = -1 ; step size 0.1/sqrt(t), 30,000 steps ; %s ends at %.3f, %s at %.3f, %s at %.3f%n",
                mname[0], ends[0], mname[1], ends[1], mname[2], ends[2]);

        // ---- 5. paths for the page --------------------------------------------------------------------------------------------
        double[] lrs2 = {0.15, 0.015, 0.5, 0.1, 0.1};
        StringJoiner pj = new StringJoiner(" ; ");
        for (int k = 0; k < 5; k++) {
            double[] w = {-9, 2.2};
            Opt o = new Opt(k, lrs2[k], 2);
            StringJoiner path = new StringJoiner(" ");
            path.add(String.format("%.3f,%.3f", w[0], w[1]));
            for (int s = 1; s <= 120; s++) {
                double[] g = {w[0] / 10, 10 * w[1]};
                o.step(w, g);
                if (s % 3 == 0) path.add(String.format("%.3f,%.3f", w[0], w[1]));
            }
            pj.add(String.format("%s rate %s end %.3f %s", NAMES[k], lrs2[k], fx(w[0], w[1]), path));
        }
        System.out.printf("paths: f(x, y) = (x^2/10 + 10 y^2)/2 from (-9, 2.2), 120 steps, every third point ; %s%n", pj);

        System.out.println("Adam: " + passed + " checks passed");
    }
}
