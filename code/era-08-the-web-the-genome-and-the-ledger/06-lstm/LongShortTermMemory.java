import java.util.*;

/**
 * Era 8, topic 6: Long short-term memory (Hochreiter, 1991 thesis; Hochreiter and Schmidhuber, 1997; the forget gate,
 * Gers, Schmidhuber and Cummins, 1999).
 *
 * HOW IT WORKS
 *   A recurrent network reads a sequence one step at a time and carries a hidden state h from step to step:
 *   h_t = tanh(W [x_t, h_{t-1}] + b). Backpropagation through time sends the error back along the same chain, and at
 *   every step it is multiplied by W and by the slope of tanh. After many steps that product has either shrunk to
 *   nothing or blown up, so the network cannot learn that something it saw long ago matters now.
 *   An LSTM cell keeps a separate memory c, changed only by adding: c_t = f * c_{t-1} + i * g, where g is a proposed
 *   new value and i, f, o are gates between 0 and 1 computed from the input and the previous output: i lets new
 *   content in, f keeps (1) or forgets (0) the old, o decides how much of tanh(c) to show as the output h. While f
 *   stays near 1 and i near 0 the memory, and the error flowing back through it, pass unchanged: Hochreiter and
 *   Schmidhuber's "constant error carousel". (Their 1997 cell had no forget gate, f = 1 always; the gate was added in
 *   1999, and is used here.)
 *
 * WHAT THIS PROGRAM DOES
 *   1. Checks both networks' backpropagation through time against finite differences for every weight.
 *   2. The task: a sequence of T steps; at step 0 one input carries a sign (+1 or -1), afterwards it is 0 while a second
 *      input carries random noise; at the last step the network must say which sign it saw. Both networks, with 4
 *      hidden units, are trained by Adam for T = 5, 10, 20, 40 and 80, then tested on 1,000 new sequences.
 *   3. How much the first input still moves the final answer: the difference in the output when only the first sign
 *      is flipped.
 *   4. How the error signal decays on its way back through time in the untrained networks.
 *   5. The trained LSTM's weights for T = 30, printed for the book's widget, with one sequence's memory values.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LongShortTermMemory.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LongShortTermMemory {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static int s32 = 1997;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    static final int I = 2, H = 4, Z = I + H;

    static double sig(double a) { return 1 / (1 + Math.exp(-a)); }

    /** A network: flat parameter array, forward pass with a cache, backward pass into a gradient array. */
    static abstract class Net {
        double[] p;
        abstract double logit(double[][] x, boolean keep);
        abstract void backward(double dLogit, double[] grad);
    }

    // RNN layout: W[H][Z], b[H], v[H], c
    static final class Rnn extends Net {
        static final int NP = H * Z + H + H + 1;
        double[][] hs, zs;

        Rnn(double scale) { p = new double[NP]; for (int k = 0; k < NP; k++) p[k] = (2 * next32() - 1) * scale; }

        double logit(double[][] x, boolean keep) {
            int T = x.length;
            double[] h = new double[H];
            if (keep) { hs = new double[T + 1][]; zs = new double[T][]; hs[0] = h.clone(); }
            for (int t = 0; t < T; t++) {
                double[] z = new double[Z];
                z[0] = x[t][0]; z[1] = x[t][1];
                System.arraycopy(h, 0, z, I, H);
                double[] nh = new double[H];
                for (int u = 0; u < H; u++) {
                    double a = p[H * Z + u];
                    for (int k = 0; k < Z; k++) a += p[u * Z + k] * z[k];
                    nh[u] = Math.tanh(a);
                }
                h = nh;
                if (keep) { zs[t] = z; hs[t + 1] = h.clone(); }
            }
            double s = p[NP - 1];
            for (int u = 0; u < H; u++) s += p[H * Z + H + u] * h[u];
            return s;
        }

        double[] dhNorms; // the size of the error signal at each step, for part 4

        void backward(double dl, double[] g) {
            int T = zs.length;
            double[] dh = new double[H];
            for (int u = 0; u < H; u++) { g[H * Z + H + u] += dl * hs[T][u]; dh[u] = dl * p[H * Z + H + u]; }
            g[NP - 1] += dl;
            dhNorms = new double[T + 1];
            for (int t = T - 1; t >= 0; t--) {
                dhNorms[t + 1] = norm(dh);
                double[] da = new double[H];
                for (int u = 0; u < H; u++) da[u] = dh[u] * (1 - hs[t + 1][u] * hs[t + 1][u]);
                double[] dz = new double[Z];
                for (int u = 0; u < H; u++) {
                    g[H * Z + u] += da[u];
                    for (int k = 0; k < Z; k++) { g[u * Z + k] += da[u] * zs[t][k]; dz[k] += p[u * Z + k] * da[u]; }
                }
                dh = Arrays.copyOfRange(dz, I, Z);
            }
            dhNorms[0] = norm(dh);
        }
    }

    // LSTM layout: for gate q in (input, forget, output, candidate): W_q[H][Z] then b_q[H]; then v[H], c
    static final class Lstm extends Net {
        static final int G = H * Z + H, NP = 4 * G + H + 1;
        double[][] zs, cs, hs, ig, fg, og, gg;

        Lstm(double scale, double forgetBias) {
            p = new double[NP];
            for (int k = 0; k < NP; k++) p[k] = (2 * next32() - 1) * scale;
            for (int u = 0; u < H; u++) p[G + H * Z + u] = forgetBias;
        }

        double logit(double[][] x, boolean keep) {
            int T = x.length;
            double[] h = new double[H], c = new double[H];
            if (keep) { zs = new double[T][]; cs = new double[T + 1][]; hs = new double[T + 1][]; ig = new double[T][]; fg = new double[T][]; og = new double[T][]; gg = new double[T][]; cs[0] = c.clone(); hs[0] = h.clone(); }
            for (int t = 0; t < T; t++) {
                double[] z = new double[Z];
                z[0] = x[t][0]; z[1] = x[t][1];
                System.arraycopy(h, 0, z, I, H);
                double[][] gate = new double[4][H];
                for (int q = 0; q < 4; q++) for (int u = 0; u < H; u++) {
                    double a = p[q * G + H * Z + u];
                    for (int k = 0; k < Z; k++) a += p[q * G + u * Z + k] * z[k];
                    gate[q][u] = q == 3 ? Math.tanh(a) : sig(a);
                }
                double[] nc = new double[H], nh = new double[H];
                for (int u = 0; u < H; u++) { nc[u] = gate[1][u] * c[u] + gate[0][u] * gate[3][u]; nh[u] = gate[2][u] * Math.tanh(nc[u]); }
                c = nc; h = nh;
                if (keep) { zs[t] = z; ig[t] = gate[0]; fg[t] = gate[1]; og[t] = gate[2]; gg[t] = gate[3]; cs[t + 1] = c.clone(); hs[t + 1] = h.clone(); }
            }
            double s = p[NP - 1];
            for (int u = 0; u < H; u++) s += p[4 * G + u] * h[u];
            return s;
        }

        double[] dcNorms;

        void backward(double dl, double[] g) {
            int T = zs.length;
            double[] dh = new double[H], dc = new double[H];
            for (int u = 0; u < H; u++) { g[4 * G + u] += dl * hs[T][u]; dh[u] = dl * p[4 * G + u]; }
            g[NP - 1] += dl;
            dcNorms = new double[T + 1];
            for (int t = T - 1; t >= 0; t--) {
                double[][] da = new double[4][H];
                for (int u = 0; u < H; u++) {
                    double tc = Math.tanh(cs[t + 1][u]);
                    double dout = dh[u] * tc;
                    dc[u] += dh[u] * og[t][u] * (1 - tc * tc);
                    da[0][u] = dc[u] * gg[t][u] * ig[t][u] * (1 - ig[t][u]);
                    da[1][u] = dc[u] * cs[t][u] * fg[t][u] * (1 - fg[t][u]);
                    da[2][u] = dout * og[t][u] * (1 - og[t][u]);
                    da[3][u] = dc[u] * ig[t][u] * (1 - gg[t][u] * gg[t][u]);
                }
                dcNorms[t + 1] = norm(dc);
                double[] dz = new double[Z];
                for (int q = 0; q < 4; q++) for (int u = 0; u < H; u++) {
                    g[q * G + H * Z + u] += da[q][u];
                    for (int k = 0; k < Z; k++) { g[q * G + u * Z + k] += da[q][u] * zs[t][k]; dz[k] += p[q * G + u * Z + k] * da[q][u]; }
                }
                for (int u = 0; u < H; u++) dc[u] *= fg[t][u];
                dh = Arrays.copyOfRange(dz, I, Z);
            }
            dcNorms[0] = norm(dc);
        }
    }

    static double norm(double[] v) { double s = 0; for (double x : v) s += x * x; return Math.sqrt(s); }

    /** One example: sign at step 0 on input 0, noise in [-1, 1] on input 1 at every step. */
    static double[][] sequence(int T, int sign) {
        double[][] x = new double[T][2];
        x[0][0] = sign;
        for (int t = 0; t < T; t++) x[t][1] = 2 * next32() - 1;
        return x;
    }

    static double loss(Net n, double[][] x, int sign) {
        double y = sign > 0 ? 1 : 0, pr = sig(n.logit(x, false));
        return -(y * Math.log(pr) + (1 - y) * Math.log(1 - pr));
    }

    static void train(Net n, int T, int steps) {
        int np = n.p.length;
        double[] m = new double[np], v = new double[np];
        double lr = 0.01, b1 = 0.9, b2 = 0.999;
        for (int step = 1; step <= steps; step++) {
            double[] g = new double[np];
            for (int b = 0; b < 16; b++) {
                int sign = next32() < 0.5 ? 1 : -1;
                double[][] x = sequence(T, sign);
                double pr = sig(n.logit(x, true));
                n.backward(pr - (sign > 0 ? 1 : 0), g);
            }
            double gn = norm(g);
            if (gn > 5) for (int k = 0; k < np; k++) g[k] *= 5 / gn; // clip exploding gradients
            for (int k = 0; k < np; k++) {
                m[k] = b1 * m[k] + (1 - b1) * g[k];
                v[k] = b2 * v[k] + (1 - b2) * g[k] * g[k];
                n.p[k] -= lr * (m[k] / (1 - Math.pow(b1, step))) / (Math.sqrt(v[k] / (1 - Math.pow(b2, step))) + 1e-8);
            }
        }
    }

    static double accuracy(Net n, int T, int tests) {
        int ok = 0;
        for (int t = 0; t < tests; t++) {
            int sign = next32() < 0.5 ? 1 : -1;
            if ((n.logit(sequence(T, sign), false) > 0) == (sign > 0)) ok++;
        }
        return (double) ok / tests;
    }

    /** Average change of the output logit when only the first sign is flipped (same noise). */
    static double sensitivity(Net n, int T, int tests) {
        double s = 0;
        for (int t = 0; t < tests; t++) {
            double[][] x = sequence(T, 1);
            double a = n.logit(x, false);
            x[0][0] = -1;
            s += Math.abs(a - n.logit(x, false)) / 2;
        }
        return s / tests;
    }

    static double gradCheck(Net n, int T) {
        double[][] x = sequence(T, 1);
        double[] g = new double[n.p.length];
        double pr = sig(n.logit(x, true));
        n.backward(pr - 1, g);
        double diff = 0, size = 0;
        for (int k = 0; k < n.p.length; k++) {
            double keep = n.p[k], e = 1e-5;
            n.p[k] = keep + e; double lp = loss(n, x, 1);
            n.p[k] = keep - e; double lm = loss(n, x, 1);
            n.p[k] = keep;
            double num = (lp - lm) / (2 * e);
            check(Math.abs(num - g[k]) < 1e-8, "each slope agrees with its finite difference to 1e-8");
            diff += (num - g[k]) * (num - g[k]); size += (num + g[k]) * (num + g[k]);
        }
        return Math.sqrt(diff / size); // |numeric - backprop| / |numeric + backprop|
    }

    public static void main(String[] args) {
        // ---- 1. gradient checks ---------------------------------------------------------------------------------------
        s32 = 1991;
        Rnn r0 = new Rnn(0.8);
        Lstm l0 = new Lstm(0.8, 1);
        double gr = gradCheck(r0, 12), gl = gradCheck(l0, 12);
        check(gr < 1e-6 && gl < 1e-6, "backpropagation through time agrees with finite differences");
        System.out.printf("gradcheck: 12-step sequence, 4 hidden units ; every one of the RNN's %d weights and the LSTM's %d weights against central differences ; relative difference of the whole gradient: RNN %.1e, LSTM %.1e%n", Rnn.NP, Lstm.NP, gr, gl);

        // ---- 2 and 3. the long-lag task --------------------------------------------------------------------------------
        StringJoiner tj = new StringJoiner(" ; ");
        double rnnAt80 = 0, lstmAt80 = 0, rnnAt5 = 0, sensR80 = 0, sensL80 = 0;
        Rnn rnn80 = null;
        Lstm lstm80 = null;
        for (int T : new int[]{5, 10, 20, 40, 80}) {
            s32 = 1000 + T;
            Rnn rnn = new Rnn(0.8);
            train(rnn, T, 1500);
            Lstm lstm = new Lstm(0.8, 3);
            train(lstm, T, 1500);
            double ar = accuracy(rnn, T, 1000), al = accuracy(lstm, T, 1000);
            double sr = sensitivity(rnn, T, 200), sl = sensitivity(lstm, T, 200);
            if (T == 5) rnnAt5 = ar;
            if (T == 80) { rnnAt80 = ar; lstmAt80 = al; sensR80 = sr; sensL80 = sl; rnn80 = rnn; lstm80 = lstm; }
            tj.add(String.format("T = %d: RNN %.1f%% correct (first input moves the output by %.3f), LSTM %.1f%% (by %.3f)", T, 100 * ar, sr, 100 * al, sl));
        }
        check(rnnAt5 > 0.95, "the plain RNN learns a 5-step lag");
        check(rnnAt80 < 0.65, "the plain RNN is near a coin at 80 steps");
        check(lstmAt80 > 0.95, "the LSTM remembers across 80 steps");
        check(sensL80 > 10 * sensR80, "the first input still moves the LSTM's answer");
        System.out.printf("lag: input 0 carries a sign at step 0 only; input 1 carries noise in [-1, 1] at every step ; 4 hidden units, 1,500 steps of Adam on batches of 16, tested on 1,000 new sequences ; %s%n", tj);

        // ---- 4. the error signal on its way back ---------------------------------------------------------------------
        s32 = 7;
        Net[][] pairsOfNets = {{new Rnn(0.8), new Lstm(0.8, 3)}, {rnn80, lstm80}};
        String[] names = {"untrained", "trained for T = 80"};
        StringJoiner dj = new StringJoiner(" ; ");
        double[][] at79 = new double[2][2];
        for (int pi = 0; pi < 2; pi++) {
            Rnn ru = (Rnn) pairsOfNets[pi][0];
            Lstm lu = (Lstm) pairsOfNets[pi][1];
            double[][] x = sequence(80, 1);
            ru.logit(x, true); ru.backward(1, new double[Rnn.NP]);
            lu.logit(x, true); lu.backward(1, new double[Lstm.NP]);
            StringJoiner one = new StringJoiner(" ");
            for (int back : new int[]{1, 5, 10, 20, 40, 79}) one.add(String.format("%d:%.1e:%.1e", back, ru.dhNorms[80 - back] / ru.dhNorms[79], lu.dcNorms[80 - back] / lu.dcNorms[79]));
            at79[pi][0] = ru.dhNorms[1] / ru.dhNorms[79];
            at79[pi][1] = lu.dcNorms[1] / lu.dcNorms[79];
            dj.add(names[pi] + ": " + one);
        }
        check(at79[0][0] < 1e-15 && at79[1][0] < 1e-15, "the RNN's error signal has vanished 78 steps further back, trained or not");
        check(at79[0][1] > 1e20 * at79[0][0], "the untrained LSTM's memory keeps far more of it");
        check(at79[1][1] > 0.01 && at79[1][1] > 1e14 * at79[1][0], "after training, the LSTM's memory still carries a few percent of it");
        System.out.printf("decay: one 80-step sequence ; size of the error signal k steps back, relative to 1 step back (RNN hidden state : LSTM memory) ; k:RNN:LSTM ; %s%n", dj);

        // ---- 5. the widget's network --------------------------------------------------------------------------------
        s32 = 1999;
        Lstm w = new Lstm(0.8, 3);
        train(w, 30, 1500);
        double aw = accuracy(w, 30, 1000);
        check(aw > 0.95, "the widget's network has learned the task");
        StringJoiner pj = new StringJoiner(",");
        for (double v : w.p) pj.add(String.format("%.4f", v));
        // the widget runs the network with the weights rounded as printed; so does this check
        Lstm wr = new Lstm(0, 0);
        for (int k = 0; k < Lstm.NP; k++) wr.p[k] = Math.round(w.p[k] * 10000) / 10000.0;
        s32 = 2024;
        double[][] ex = sequence(30, -1);
        double lg = wr.logit(ex, true);
        StringJoiner cj = new StringJoiner(" ");
        for (int t = 1; t <= 30; t++) { StringJoiner one = new StringJoiner(","); for (int u = 0; u < H; u++) one.add(String.format("%.3f", wr.cs[t][u])); cj.add(one.toString()); }
        System.out.printf("widget: T = 30, trained from seed 1999, %.1f%% correct on 1,000 new sequences ; %d weights in the order input gate W[4][6] b[4], forget gate, output gate, candidate, then v[4], c ; the 6 inputs to each gate are (sign input, noise input, h1, h2, h3, h4) ; weights rounded to 4 decimals: %s ; example: sign -1, noise from the generator with seed 2024 ; final output logit %.4f ; memory c after each step: %s%n",
                100 * aw, Lstm.NP, pj, lg, cj);

        System.out.println("LongShortTermMemory: " + passed + " checks passed");
    }
}
