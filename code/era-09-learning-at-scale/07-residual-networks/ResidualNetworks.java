import java.util.*;

/**
 * Era 9, topic 7: Residual networks (Kaiming He, Xiangyu Zhang, Shaoqing Ren and Jian Sun, Microsoft Research, 2015).
 *
 * HOW IT WORKS
 *   A plain deep network passes its signal through layer after layer: each block of two layers computes
 *   h -> relu(W2 relu(W1 h + b1) + b2). Stacking more blocks should never hurt, since the extra blocks could learn
 *   to pass their input through unchanged, yet in practice deeper plain networks train worse: their error on the
 *   training data itself goes up. A residual block adds its input back: h -> relu(h + W2 relu(W1 h + b1) + b2).
 *   The block now only has to learn a correction F(h) to its input, and "no correction" (W2 = 0) passes the
 *   signal through exactly. The shortcut adds no parameters and almost no computation.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Checks the hand-written gradient against finite differences, for both kinds of network.
 *   The paper's networks normalize every layer (batch normalization); this program does not, and instead starts the
 *   second layer of every residual block at zero, so that each block starts as the identity. It also reports what
 *   happens to a residual network started with the same random weights as the plain one.
 *   2. Trains plain and residual networks of 1 to 32 blocks (4 to 66 layers with weights) to fit a wavy function
 *      of two variables, with the same data, the same optimizer (Adam, topic 5) and the same number of steps,
 *      and reports the error on the training data itself.
 *   3. Measures how large the gradient reaching the first block is at the start of training, for each depth.
 *   4. Takes a trained residual network, appends blocks whose second weights are zero, and checks that it computes
 *      exactly the same function: a deeper residual network can always copy a shallower one.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ResidualNetworks.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ResidualNetworks {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int W = 12;           // width of every hidden layer
    static final int N = 512;          // training points
    static double[][] X = new double[N][2];
    static double[] Y = new double[N];

    /** The network: an input layer 2 -> W, B blocks of two W x W layers, an output layer W -> 1. */
    static class Net {
        final int B; final boolean residual;
        double[] p; // all parameters in one array
        final int inW, inB, outW, outB, blk;

        Net(int B, boolean residual, Random r) { this(B, residual, r, residual); }

        /** zeroBranch: the second layer of every block starts at zero, so every residual block starts as the identity. */
        Net(int B, boolean residual, Random r, boolean zeroBranch) {
            this.B = B; this.residual = residual;
            inW = 0; inB = 2 * W; blk = inB + W;
            outW = blk + B * (2 * W * W + 2 * W); outB = outW + W;
            p = new double[outB + 1];
            for (int i = 0; i < 2 * W; i++) p[inW + i] = r.nextGaussian() * Math.sqrt(2.0 / 2);
            for (int b = 0; b < B; b++) {
                int o = blk + b * (2 * W * W + 2 * W);
                for (int i = 0; i < W * W; i++) p[o + i] = r.nextGaussian() * Math.sqrt(2.0 / W);                 // W1 (He)
                for (int i = 0; i < W * W; i++) { double z = r.nextGaussian() * Math.sqrt(2.0 / W); p[o + W * W + W + i] = zeroBranch ? 0 : z; } // W2 (He, or zero)
            }
            for (int i = 0; i < W; i++) p[outW + i] = r.nextGaussian() * Math.sqrt(1.0 / W);
        }

        int w1(int b) { return blk + b * (2 * W * W + 2 * W); }
        int b1(int b) { return w1(b) + W * W; }
        int w2(int b) { return b1(b) + W; }
        int b2(int b) { return w2(b) + W * W; }

        /** Forward pass; keeps the activations in acts when it is not null (for backpropagation). */
        double forward(double[] x, double[][] h, double[][] u) {
            double[] cur = new double[W];
            for (int j = 0; j < W; j++) cur[j] = Math.max(0, p[inW + 2 * j] * x[0] + p[inW + 2 * j + 1] * x[1] + p[inB + j]);
            if (h != null) h[0] = cur.clone();
            for (int b = 0; b < B; b++) {
                double[] mid = new double[W], nxt = new double[W];
                for (int j = 0; j < W; j++) {
                    double s = p[b1(b) + j];
                    for (int k = 0; k < W; k++) s += p[w1(b) + j * W + k] * cur[k];
                    mid[j] = Math.max(0, s);
                }
                for (int j = 0; j < W; j++) {
                    double s = p[b2(b) + j] + (residual ? cur[j] : 0);
                    for (int k = 0; k < W; k++) s += p[w2(b) + j * W + k] * mid[k];
                    nxt[j] = Math.max(0, s);
                }
                if (u != null) u[b] = mid;
                cur = nxt;
                if (h != null) h[b + 1] = cur.clone();
            }
            double y = p[outB];
            for (int j = 0; j < W; j++) y += p[outW + j] * cur[j];
            return y;
        }

        /** Adds the gradient of 0.5 (f(x) - y)^2 to g; returns the squared error. */
        double backward(double[] x, double y, double[] g) {
            double[][] h = new double[B + 1][], u = new double[B][];
            double f = forward(x, h, u), e = f - y;
            g[outB] += e;
            double[] d = new double[W]; // gradient with respect to the current block output (after its relu)
            for (int j = 0; j < W; j++) { g[outW + j] += e * h[B][j]; d[j] = e * p[outW + j]; }
            for (int b = B - 1; b >= 0; b--) {
                double[] cur = h[b], mid = u[b], out = h[b + 1];
                double[] ds = new double[W]; // through the relu after the addition
                for (int j = 0; j < W; j++) ds[j] = out[j] > 0 ? d[j] : 0;
                double[] dmid = new double[W], dcur = new double[W];
                for (int j = 0; j < W; j++) {
                    g[b2(b) + j] += ds[j];
                    for (int k = 0; k < W; k++) { g[w2(b) + j * W + k] += ds[j] * mid[k]; dmid[k] += ds[j] * p[w2(b) + j * W + k]; }
                    if (residual) dcur[j] += ds[j];
                }
                for (int j = 0; j < W; j++) {
                    double dm = mid[j] > 0 ? dmid[j] : 0;
                    g[b1(b) + j] += dm;
                    for (int k = 0; k < W; k++) { g[w1(b) + j * W + k] += dm * cur[k]; dcur[k] += dm * p[w1(b) + j * W + k]; }
                }
                d = dcur;
            }
            for (int j = 0; j < W; j++) {
                double dj = h[0][j] > 0 ? d[j] : 0;
                g[inW + 2 * j] += dj * x[0]; g[inW + 2 * j + 1] += dj * x[1]; g[inB + j] += dj;
            }
            return e * e;
        }

        double mse() {
            double s = 0;
            for (int i = 0; i < N; i++) { double e = forward(X[i], null, null) - Y[i]; s += e * e; }
            return s / N;
        }

        /** Size of the gradient reaching the first block's weights, over the whole data set. */
        double firstBlockGradient() {
            double[] g = new double[p.length];
            for (int i = 0; i < N; i++) backward(X[i], Y[i], g);
            double s = 0;
            int from = B > 0 ? w1(0) : inW, to = B > 0 ? b2(0) + W : inB + W;
            for (int i = from; i < to; i++) s += (g[i] / N) * (g[i] / N);
            return Math.sqrt(s);
        }
    }

    static double[] train(Net net, int steps, long seed, int every) {
        Random r = new Random(seed);
        int P = net.p.length, batch = 32;
        double[] m = new double[P], v = new double[P], g = new double[P];
        double[] curve = new double[steps / every + 1];
        curve[0] = net.mse();
        double lr = 1e-3;
        for (int t = 1; t <= steps; t++) {
            Arrays.fill(g, 0);
            for (int b = 0; b < batch; b++) { int i = r.nextInt(N); net.backward(X[i], Y[i], g); }
            for (int i = 0; i < P; i++) {
                double gi = g[i] / batch;
                m[i] = 0.9 * m[i] + 0.1 * gi; v[i] = 0.999 * v[i] + 0.001 * gi * gi;
                net.p[i] -= lr * (m[i] / (1 - Math.pow(0.9, t))) / (Math.sqrt(v[i] / (1 - Math.pow(0.999, t))) + 1e-8);
            }
            if (t % every == 0) curve[t / every] = net.mse();
        }
        return curve;
    }

    public static void main(String[] args) {
        Random dr = new Random(7);
        for (int i = 0; i < N; i++) {
            X[i][0] = dr.nextDouble() * 2 - 1; X[i][1] = dr.nextDouble() * 2 - 1;
            Y[i] = Math.sin(3 * X[i][0]) * Math.cos(3 * X[i][1]) + 0.5 * Math.sin(5 * X[i][0] * X[i][1]);
        }
        double var = 0, mean = 0;
        for (double y : Y) mean += y / N;
        for (double y : Y) var += (y - mean) * (y - mean) / N;

        // ---- 1. gradient check ---------------------------------------------------------------------------------------------
        double worst = 0;
        for (boolean res : new boolean[]{false, true}) {
            Net net = new Net(3, res, new Random(1), false);
            double[] g = new double[net.p.length];
            net.backward(X[0], Y[0], g);
            Random pr = new Random(2);
            for (int k = 0; k < 60; k++) {
                int i = pr.nextInt(net.p.length);
                double old = net.p[i], h = 1e-6;
                net.p[i] = old + h; double fp = net.forward(X[0], null, null) - Y[0];
                net.p[i] = old - h; double fm = net.forward(X[0], null, null) - Y[0];
                net.p[i] = old;
                double num = (0.5 * fp * fp - 0.5 * fm * fm) / (2 * h);
                worst = Math.max(worst, Math.abs(num - g[i]) / Math.max(1e-6, Math.abs(num) + Math.abs(g[i])));
            }
        }
        check(worst < 1e-4, "backpropagation matches finite differences");
        System.out.printf("gradient: 60 random parameters of a 3-block plain and a 3-block residual network ; largest relative difference from finite differences %.1e%n", worst);

        // ---- 2. depth ------------------------------------------------------------------------------------------------------
        int[] depths = {1, 2, 4, 8, 16, 32};
        int steps = 1500, every = 100, seeds = 2;
        double[][] fin = new double[2][depths.length], grad = new double[2][depths.length];
        double[] gradHe = new double[depths.length], outHe = new double[depths.length];
        StringJoiner cj = new StringJoiner(" ; ");
        StringJoiner dj = new StringJoiner(" ; ");
        for (int di = 0; di < depths.length; di++) {
            for (int kind = 0; kind < 2; kind++) {
                double[] avg = new double[steps / every + 1];
                for (int s = 0; s < seeds; s++) {
                    Net net = new Net(depths[di], kind == 1, new Random(100 + s));
                    grad[kind][di] += net.firstBlockGradient() / seeds;
                    double[] c = train(net, steps, 200 + s, every);
                    for (int k = 0; k < c.length; k++) avg[k] += c[k] / seeds;
                }
                fin[kind][di] = avg[avg.length - 1];
                StringJoiner one = new StringJoiner(",");
                for (double a : avg) one.add(String.format("%.4f", a));
                cj.add(String.format("%s %d %s", kind == 0 ? "plain" : "residual", depths[di], one));
            }
            for (int s = 0; s < seeds; s++) {
                Net he = new Net(depths[di], true, new Random(100 + s), false);
                gradHe[di] += he.firstBlockGradient() / seeds;
                outHe[di] += he.mse() / seeds;
            }
            dj.add(String.format("%d blocks (%d weight layers, %,d parameters): plain %.4f, residual %.4f ; first-block gradient at the start: plain %.1e, residual %.1e ; a residual network started like the plain one: error at the start %.3g, first-block gradient %.1e",
                    depths[di], 2 * depths[di] + 2, new Net(depths[di], false, new Random(0)).p.length, fin[0][di], fin[1][di], grad[0][di], grad[1][di], outHe[di], gradHe[di]));
        }
        int bestPlain = 0;
        for (int di = 1; di < depths.length; di++) if (fin[0][di] < fin[0][bestPlain]) bestPlain = di;
        int last = depths.length - 1;
        System.out.printf("depth: fit f(x, y) = sin 3x cos 3y + 0.5 sin 5xy on %d points (variance %.4f), width %d, Adam rate 0.001, %,d steps of 32, mean of %d seeds ; plain blocks start with random (He) weights, residual blocks with their second layer at zero ; training error (mean squared) after training: %s%n",
                N, var, W, steps, seeds, dj);
        System.out.printf("degradation: the best plain network had %d blocks (%.4f) ; the 32-block plain network %.4f, %.1f times worse on its own training data ; the 32-block residual network %.4f%n",
                depths[bestPlain], fin[0][bestPlain], fin[0][last], fin[0][last] / fin[0][bestPlain], fin[1][last]);
        check(fin[0][last] > 2 * fin[0][bestPlain], "the deepest plain network trains worse than a shallower plain one");
        check(fin[1][last] < fin[1][0], "the residual networks keep improving with depth");
        check(fin[1][last] < fin[0][last], "at the greatest depth the residual network trains better than the plain one");
        check(grad[0][last] < 0.01 * grad[0][0], "in the deepest plain network little gradient reaches the first block");
        check(gradHe[last] > 1e4 * gradHe[0], "a residual network started like a plain one explodes with depth");
        System.out.printf("curves: training error every %d steps ; %s%n", every, cj);

        // ---- 3. a deeper copy of a shallower network ----------------------------------------------------------------------
        Net small = new Net(4, true, new Random(300));
        train(small, 800, 301, 800);
        Net big = new Net(20, true, new Random(302));
        // copy the input layer, the 4 trained blocks and the output layer; zero the second weights of the extra 16 blocks
        System.arraycopy(small.p, 0, big.p, 0, small.blk);
        for (int b = 0; b < 4; b++) System.arraycopy(small.p, small.w1(b), big.p, big.w1(b), 2 * W * W + 2 * W);
        for (int b = 4; b < 20; b++) { Arrays.fill(big.p, big.w2(b), big.w2(b) + W * W + W, 0.0); }
        for (int j = 0; j <= W; j++) big.p[big.outW + j] = small.p[small.outW + j];
        double maxd = 0;
        for (int i = 0; i < N; i++) maxd = Math.max(maxd, Math.abs(big.forward(X[i], null, null) - small.forward(X[i], null, null)));
        check(maxd == 0.0, "the deeper residual network computes exactly the same function");
        // the same trick in a plain network: zero second weights cut the signal instead of passing it
        Net plainBig = new Net(20, false, new Random(302));
        System.arraycopy(big.p, 0, plainBig.p, 0, big.p.length);
        double plainOut = plainBig.mse();
        double o0 = plainBig.forward(X[0], null, null);
        boolean constant = true;
        for (int i = 1; i < N; i++) if (plainBig.forward(X[i], null, null) != o0) constant = false;
        check(constant, "with zero second weights a plain network gives every input the same output");
        System.out.printf("identity: a 4-block residual network after 800 steps (error %.4f), extended to 20 blocks whose second weights are zero ; largest difference in output over all %d points: %.1f ; the same weights in a plain network: error %.4f, every input gives the same output%n",
                small.mse(), N, maxd, plainOut);

        System.out.println("ResidualNetworks: " + passed + " checks passed");
    }
}
