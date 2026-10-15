import java.util.*;

/**
 * Era 7, topic 7: backpropagation (Linnainmaa 1970, Werbos 1974 and 1981, Rumelhart, Hinton and Williams 1986).
 *
 * HOW IT WORKS
 *   A neural network is a chain of simple steps: each unit adds up its inputs times weights and squashes the sum with
 *   a smooth S-shaped function. Learning means adjusting the weights so the outputs get closer to the targets, by
 *   gradient descent: nudge every weight against the slope of the error. The slope with respect to each weight could
 *   be measured by wiggling that weight and running the whole network again, once per weight. Backpropagation gets all
 *   the slopes at once: run the network forward, then apply the chain rule backwards, from the error at the output to
 *   each hidden unit and each weight. That costs about as much as one more forward run, whatever the number of
 *   weights. With it, hidden units can learn features that no single layer can represent, such as exclusive-or.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The perceptron rule (Era 4) on AND and on exclusive-or (XOR): it learns AND, and never gets XOR right.
 *   2. A network with two hidden units trained by backpropagation on XOR, from 100 random starts.
 *   3. Backpropagation's gradient against wiggling each weight: the same numbers, at a fraction of the work.
 *   4. One XOR run in detail: the error epoch by epoch, from fixed starting weights the book's widget also uses.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Backpropagation.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Backpropagation {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1986L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static double sigmoid(double x) { return 1 / (1 + Math.exp(-x)); }

    static final double[][] INPUTS = {{0, 0}, {0, 1}, {1, 0}, {1, 1}};
    static final double[] XOR = {0, 1, 1, 0}, AND = {0, 0, 0, 1};

    // ---- 1. the perceptron rule ---------------------------------------------------------------------------------------
    /** Returns the epoch at which all four are right, or -1; best[0] gets the most ever right at once. */
    static int perceptron(double[] target, int epochs, int[] best) {
        double w0 = 0, w1 = 0, b = 0;
        best[0] = 0;
        for (int e = 1; e <= epochs; e++) {
            for (int i = 0; i < 4; i++) {
                double y = w0 * INPUTS[i][0] + w1 * INPUTS[i][1] + b > 0 ? 1 : 0;
                double err = target[i] - y;
                w0 += err * INPUTS[i][0]; w1 += err * INPUTS[i][1]; b += err;
            }
            int right = 0;
            for (int i = 0; i < 4; i++) if ((w0 * INPUTS[i][0] + w1 * INPUTS[i][1] + b > 0 ? 1 : 0) == target[i]) right++;
            best[0] = Math.max(best[0], right);
            if (right == 4) return e;
        }
        return -1;
    }

    // ---- 2. a 2-2-1 network ----------------------------------------------------------------------------------------
    /** Weights: w[0..5] hidden (h0: w0*x0 + w1*x1 + w2, h1: w3*x0 + w4*x1 + w5), w[6..8] output (v0*h0 + v1*h1 + c). */
    static double[] forward(double[] w, double[] x, double[] h) {
        h[0] = sigmoid(w[0] * x[0] + w[1] * x[1] + w[2]);
        h[1] = sigmoid(w[3] * x[0] + w[4] * x[1] + w[5]);
        return new double[]{sigmoid(w[6] * h[0] + w[7] * h[1] + w[8])};
    }

    /** The error 1/2 sum (y - t)^2 over the four patterns, and its gradient by backpropagation. */
    static double errorAndGradient(double[] w, double[] t, double[] grad) {
        Arrays.fill(grad, 0);
        double E = 0;
        double[] h = new double[2];
        for (int i = 0; i < 4; i++) {
            double[] x = INPUTS[i];
            double y = forward(w, x, h)[0];
            E += 0.5 * (y - t[i]) * (y - t[i]);
            double dy = (y - t[i]) * y * (1 - y);          // slope of E at the output unit's input sum
            grad[6] += dy * h[0]; grad[7] += dy * h[1]; grad[8] += dy;
            double dh0 = dy * w[6] * h[0] * (1 - h[0]);    // chain rule: back through the output weight
            double dh1 = dy * w[7] * h[1] * (1 - h[1]);
            grad[0] += dh0 * x[0]; grad[1] += dh0 * x[1]; grad[2] += dh0;
            grad[3] += dh1 * x[0]; grad[4] += dh1 * x[1]; grad[5] += dh1;
        }
        return E;
    }

    static boolean solved(double[] w) {
        double[] h = new double[2];
        for (int i = 0; i < 4; i++) if (Math.abs(forward(w, INPUTS[i], h)[0] - XOR[i]) >= 0.1) return false;
        return true;
    }

    static double rate = 0.5, momentum = 0.9;

    /** Batch gradient descent with momentum; returns the epoch at which XOR is solved, or -1. */
    static int train(double[] w, int maxEpochs, List<Double> curve) {
        double[] grad = new double[9], step = new double[9];
        for (int e = 0; e <= maxEpochs; e++) {
            double E = errorAndGradient(w, XOR, grad);
            if (curve != null) curve.add(E);
            if (solved(w)) return e;
            for (int k = 0; k < 9; k++) { step[k] = -rate * grad[k] + momentum * step[k]; w[k] += step[k]; }
        }
        return -1;
    }

    // ---- 3. a larger network: backpropagation against wiggling every weight ------------------------------------------
    static long mults;

    static double[][] layer(int out, int in) {
        double[][] W = new double[out][in + 1];
        for (double[] row : W) for (int j = 0; j < row.length; j++) row[j] = uniform() * 2 - 1;
        return W;
    }

    static double[] apply(double[][] W, double[] x) {
        double[] y = new double[W.length];
        for (int i = 0; i < W.length; i++) {
            double s = W[i][x.length];
            for (int j = 0; j < x.length; j++) { s += W[i][j] * x[j]; mults++; }
            y[i] = sigmoid(s);
        }
        return y;
    }

    static double loss(double[][] W1, double[][] W2, double[] x, double[] t) {
        double[] y = apply(W2, apply(W1, x));
        double E = 0;
        for (int i = 0; i < y.length; i++) E += 0.5 * (y[i] - t[i]) * (y[i] - t[i]);
        return E;
    }

    public static void main(String[] args) {
        // ---- 1 ----------------------------------------------------------------------------------------------------------
        int[] best = new int[1];
        int andEpoch = perceptron(AND, 1000, best);
        check(andEpoch > 0, "the perceptron learns AND");
        int xorEpoch = perceptron(XOR, 1000, best);
        check(xorEpoch < 0 && best[0] < 4, "the perceptron never gets all of XOR right");
        // no straight line separates XOR: try a fine grid of lines and count the best
        int bestLine = 0;
        for (double a = -2; a <= 2; a += 0.05) for (double b = -2; b <= 2; b += 0.05) for (double c = -2; c <= 2; c += 0.05) {
            int right = 0;
            for (int i = 0; i < 4; i++) if ((a * INPUTS[i][0] + b * INPUTS[i][1] + c > 0 ? 1 : 0) == XOR[i]) right++;
            bestLine = Math.max(bestLine, right);
        }
        check(bestLine == 3, "no line gets all four XOR cases");
        System.out.printf("perceptron: one layer of weights, the perceptron rule ; AND learned in %d epochs ; XOR never learned in 1,000 epochs, at best %d of 4 right at once ; of %,d straight lines tried on a grid, none put all four XOR cases on the right side, the best managed %d%n",
                andEpoch, best[0], 81 * 81 * 81, bestLine);

        // ---- 2 ----------------------------------------------------------------------------------------------------------
        int starts = 100, ok = 0;
        List<Integer> epochs = new ArrayList<>();
        for (int s = 0; s < starts; s++) {
            double[] w = new double[9];
            for (int k = 0; k < 9; k++) w[k] = uniform() * 2 - 1;
            int e = train(w, 5000, null);
            if (e >= 0) { ok++; epochs.add(e); check(solved(w), "solved means every output within 0.1 of its target"); }
        }
        Collections.sort(epochs);
        check(ok > 50, "most starts learn XOR");
        System.out.printf("xor: two inputs, two hidden units, one output, all sigmoid ; batch gradient descent by backpropagation, rate %.1f, momentum %.1f, weights started uniformly in [-1, 1] ; %d of %d starts learned XOR (every output within 0.1 of its target) within 5,000 epochs, the median after %d epochs, the fastest %d, the slowest %d ; the other %d got stuck%n",
                rate, momentum, ok, starts, epochs.get(epochs.size() / 2), epochs.get(0), epochs.get(epochs.size() - 1), starts - ok);

        // ---- 3 ----------------------------------------------------------------------------------------------------------
        int nin = 10, nh = 20, nout = 5;
        double[][] W1 = layer(nh, nin), W2 = layer(nout, nh);
        double[] x = new double[nin], t = new double[nout];
        for (int i = 0; i < nin; i++) x[i] = uniform();
        for (int i = 0; i < nout; i++) t[i] = uniform();
        int weights = nh * (nin + 1) + nout * (nh + 1);
        // backpropagation
        mults = 0;
        double[] h = apply(W1, x), y = apply(W2, h);
        long forwardMults = mults;
        double[] dy = new double[nout], dh = new double[nh];
        double[][] g1 = new double[nh][nin + 1], g2 = new double[nout][nh + 1];
        long backMults = 0;
        for (int i = 0; i < nout; i++) {
            dy[i] = (y[i] - t[i]) * y[i] * (1 - y[i]);
            for (int j = 0; j < nh; j++) { g2[i][j] = dy[i] * h[j]; dh[j] += dy[i] * W2[i][j]; backMults += 2; }
            g2[i][nh] = dy[i];
        }
        for (int j = 0; j < nh; j++) {
            dh[j] *= h[j] * (1 - h[j]);
            for (int k = 0; k < nin; k++) { g1[j][k] = dh[j] * x[k]; backMults++; }
            g1[j][nin] = dh[j];
        }
        // wiggling each weight up and down: two extra forward runs per weight
        double eps = 1e-5, worst = 0;
        mults = 0;
        for (double[][][] pair : new double[][][][]{{W1, g1}, {W2, g2}}) {
            double[][] W = pair[0], G = pair[1];
            for (int i = 0; i < W.length; i++)
                for (int j = 0; j < W[i].length; j++) {
                    double keep = W[i][j];
                    W[i][j] = keep + eps; double up = loss(W1, W2, x, t);
                    W[i][j] = keep - eps; double down = loss(W1, W2, x, t);
                    W[i][j] = keep;
                    double numeric = (up - down) / (2 * eps);
                    double rel = Math.abs(numeric - G[i][j]) / Math.max(1e-8, Math.abs(numeric) + Math.abs(G[i][j]));
                    worst = Math.max(worst, rel);
                    check(rel < 1e-6, "backpropagation agrees with wiggling the weight");
                }
        }
        long wiggleMults = mults;
        check(wiggleMults == 2L * weights * forwardMults, "two forward runs per weight");
        System.out.printf("gradcheck: a network of %d inputs, %d hidden units and %d outputs, %d weights ; backpropagation: one forward run (%,d multiplications) and one backward run (%,d) ; wiggling each weight up and down: %,d forward runs, %,d multiplications ; the %d slopes agree to a relative difference of at most %.1e%n",
                nin, nh, nout, weights, forwardMults, backMults, 2 * weights, wiggleMults, weights, worst);

        // ---- 4 ----------------------------------------------------------------------------------------------------------
        double[] w = {0.5, -0.4, 0.1, -0.3, 0.6, -0.2, 0.4, -0.5, 0.2};
        StringJoiner init = new StringJoiner(" ");
        for (double v : w) init.add(String.format("%.1f", v));
        List<Double> curve = new ArrayList<>();
        int e = train(w, 5000, curve);
        check(e > 0, "the fixed start learns XOR");
        StringJoiner cj = new StringJoiner(" ");
        for (int k = 0; k < curve.size(); k += 10) cj.add(String.format("%d:%.4f", k, curve.get(k)));
        double[] hh = new double[2];
        StringJoiner oj = new StringJoiner(" ");
        for (int i = 0; i < 4; i++) oj.add(String.format("%.0f%.0f->%.3f", INPUTS[i][0], INPUTS[i][1], forward(w, INPUTS[i], hh)[0]));
        StringJoiner fw = new StringJoiner(" ");
        for (double v : w) fw.add(String.format("%.3f", v));
        System.out.printf("xorinit: %s%n", init);
        System.out.printf("xorrun: from the starting weights above, XOR learned after %d epochs ; error (half the sum of squared misses over the 4 cases) every 10 epochs, epoch:error ; %s%n", e, cj);
        System.out.printf("xorfinal: outputs %s ; final weights %s%n", oj, fw);

        System.out.println("Backpropagation: " + passed + " checks passed");
    }
}
