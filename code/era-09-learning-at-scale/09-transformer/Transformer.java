import java.util.*;

/**
 * Era 9, topic 9: The Transformer (Ashish Vaswani and seven co-authors, Google Brain, Google Research and University
 * of Toronto, 2017), after the attention of Dzmitry Bahdanau, KyungHyun Cho and Yoshua Bengio (2014).
 *
 * HOW IT WORKS
 *   Every position of the input is a vector. Attention lets one position gather information from all the others:
 *   it forms a query q, every position forms a key k_i and a value v_i (each by multiplying its vector by a learned
 *   matrix), and the output is a weighted average of the values,
 *     Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V,
 *   so a position takes most from the positions whose keys best match its query. Dividing by sqrt(d_k) keeps the
 *   scores from growing with the vector length, which would make the softmax nearly one-hot and its gradient
 *   nearly zero. The Transformer stacks such layers (with several "heads" side by side, residual connections and
 *   small feed-forward networks) and needs no recurrence: all positions are computed at once.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A task that needs attention: a sequence of 6 (key, value) pairs and then a query key; the answer is the value
 *      stored under that key. A one-layer, one-head attention model with hand-written gradients (checked against
 *      finite differences) learns it; a model that averages the positions instead of attending cannot.
 *   2. The scaling: with d_k = 512 and no division by sqrt(d_k), the softmax saturates and its gradient vanishes.
 *   3. The sinusoidal positional encoding: the dot product of the encodings of two positions depends only on how
 *      far apart they are.
 *   4. The cost of one layer, counted: self-attention against a recurrent layer.
 *   Every printed line starts with a tag that the book's page builder reads; the last line before the checks holds
 *   the trained weights for the book's widget.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Transformer.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Transformer {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int NK = 16, NV = 16, PAIRS = 6, D = 32, DK = 16;

    /** All parameters: key and value embeddings, query/key/value/output matrices. */
    static class Model {
        final boolean attend; // false: average all positions equally (no attention)
        double[][] Ek = new double[NK][D], Ev = new double[NV][D], Wq = new double[DK][D], Wk = new double[DK][D], Wv = new double[D][D], Wo = new double[NV][D];

        Model(boolean attend, Random r) {
            this.attend = attend;
            for (double[][] M : all()) for (double[] row : M) for (int j = 0; j < row.length; j++) row[j] = r.nextGaussian() / Math.sqrt(D);
        }

        double[][][] all() { return new double[][][]{Ek, Ev, Wq, Wk, Wv, Wo}; }

        Model zeroLike() { Model z = new Model(attend, new Random(0)); for (double[][] M : z.all()) for (double[] row : M) Arrays.fill(row, 0); return z; }
    }

    record Example(int[] keys, int[] vals, int query, int answer) {}

    static Example example(Random r) {
        int[] keys = new int[PAIRS], vals = new int[PAIRS];
        List<Integer> ks = new ArrayList<>();
        for (int i = 0; i < NK; i++) ks.add(i);
        Collections.shuffle(ks, r);
        for (int i = 0; i < PAIRS; i++) { keys[i] = ks.get(i); vals[i] = r.nextInt(NV); }
        int j = r.nextInt(PAIRS);
        return new Example(keys, vals, keys[j], vals[j]);
    }

    static double[] mul(double[][] M, double[] x) {
        double[] y = new double[M.length];
        for (int i = 0; i < M.length; i++) { double s = 0; for (int j = 0; j < x.length; j++) s += M[i][j] * x[j]; y[i] = s; }
        return y;
    }

    /** Forward and, when g is not null, backward. Returns the loss; probs and attention are filled when not null. */
    static double run(Model m, Example e, Model g, double[] probsOut, double[] attnOut) {
        double[][] x = new double[PAIRS][D];
        for (int i = 0; i < PAIRS; i++) for (int t = 0; t < D; t++) x[i][t] = m.Ek[e.keys[i]][t] + m.Ev[e.vals[i]][t];
        double[] xq = m.Ek[e.query].clone();
        double[] q = mul(m.Wq, xq);
        double[][] k = new double[PAIRS][], v = new double[PAIRS][];
        double[] s = new double[PAIRS], a = new double[PAIRS];
        double mx = -1e300;
        for (int i = 0; i < PAIRS; i++) {
            k[i] = mul(m.Wk, x[i]); v[i] = mul(m.Wv, x[i]);
            double dot = 0; for (int t = 0; t < DK; t++) dot += q[t] * k[i][t];
            s[i] = dot / Math.sqrt(DK);
            mx = Math.max(mx, s[i]);
        }
        double z = 0;
        for (int i = 0; i < PAIRS; i++) { a[i] = m.attend ? Math.exp(s[i] - mx) : 1; z += a[i]; }
        for (int i = 0; i < PAIRS; i++) a[i] /= z;
        if (attnOut != null) System.arraycopy(a, 0, attnOut, 0, PAIRS);
        double[] o = new double[D];
        for (int i = 0; i < PAIRS; i++) for (int t = 0; t < D; t++) o[t] += a[i] * v[i][t];
        double[] h = new double[D];
        for (int t = 0; t < D; t++) h[t] = o[t] + xq[t]; // residual connection
        double[] logit = mul(m.Wo, h);
        double lm = Arrays.stream(logit).max().getAsDouble(), lz = 0;
        double[] p = new double[NV];
        for (int c = 0; c < NV; c++) { p[c] = Math.exp(logit[c] - lm); lz += p[c]; }
        for (int c = 0; c < NV; c++) p[c] /= lz;
        if (probsOut != null) System.arraycopy(p, 0, probsOut, 0, NV);
        double loss = -Math.log(p[e.answer]);
        if (g == null) return loss;
        // ---- backward ----
        double[] dl = p.clone(); dl[e.answer] -= 1;
        double[] dh = new double[D];
        for (int c = 0; c < NV; c++) for (int t = 0; t < D; t++) { g.Wo[c][t] += dl[c] * h[t]; dh[t] += m.Wo[c][t] * dl[c]; }
        double[] dxq = dh.clone(), dq = new double[DK];
        double[] da = new double[PAIRS];
        double[][] dx = new double[PAIRS][D];
        for (int i = 0; i < PAIRS; i++) {
            for (int t = 0; t < D; t++) da[i] += dh[t] * v[i][t];
            // through v_i = Wv x_i, with dv_i = a_i dh
            for (int r = 0; r < D; r++) {
                double dvr = a[i] * dh[r];
                for (int t = 0; t < D; t++) { g.Wv[r][t] += dvr * x[i][t]; dx[i][t] += m.Wv[r][t] * dvr; }
            }
        }
        if (m.attend) {
            double sum = 0; for (int i = 0; i < PAIRS; i++) sum += a[i] * da[i];
            for (int i = 0; i < PAIRS; i++) {
                double ds = a[i] * (da[i] - sum) / Math.sqrt(DK);
                for (int t = 0; t < DK; t++) dq[t] += ds * k[i][t];
                for (int r = 0; r < DK; r++) {
                    double dkr = ds * q[r];
                    for (int t = 0; t < D; t++) { g.Wk[r][t] += dkr * x[i][t]; dx[i][t] += m.Wk[r][t] * dkr; }
                }
            }
            for (int r = 0; r < DK; r++) for (int t = 0; t < D; t++) { g.Wq[r][t] += dq[r] * xq[t]; dxq[t] += m.Wq[r][t] * dq[r]; }
        }
        for (int i = 0; i < PAIRS; i++) for (int t = 0; t < D; t++) { g.Ek[e.keys[i]][t] += dx[i][t]; g.Ev[e.vals[i]][t] += dx[i][t]; }
        for (int t = 0; t < D; t++) g.Ek[e.query][t] += dxq[t];
        return loss;
    }

    static double accuracy(Model m, int n, long seed, double[] meanAttn) {
        Random r = new Random(seed);
        int ok = 0;
        double[] p = new double[NV], a = new double[PAIRS];
        double att = 0;
        for (int k = 0; k < n; k++) {
            Example e = example(r);
            run(m, e, null, p, a);
            int best = 0; for (int c = 1; c < NV; c++) if (p[c] > p[best]) best = c;
            if (best == e.answer) ok++;
            for (int i = 0; i < PAIRS; i++) if (e.keys[i] == e.query) att += a[i];
        }
        if (meanAttn != null) meanAttn[0] = att / n;
        return (double) ok / n;
    }

    static double[] train(Model m, int steps, long seed) {
        Random r = new Random(seed);
        Model mm = m.zeroLike(), vv = m.zeroLike();
        double lr = 3e-3, lossSum = 0;
        double[] curve = new double[steps / 250];
        for (int t = 1; t <= steps; t++) {
            Model g = m.zeroLike();
            int B = 32;
            for (int b = 0; b < B; b++) lossSum += run(m, example(r), g, null, null);
            double[][][] P = m.all(), G = g.all(), M1 = mm.all(), V1 = vv.all();
            for (int k = 0; k < P.length; k++) for (int i = 0; i < P[k].length; i++) for (int j = 0; j < P[k][i].length; j++) {
                double gi = G[k][i][j] / B;
                M1[k][i][j] = 0.9 * M1[k][i][j] + 0.1 * gi; V1[k][i][j] = 0.999 * V1[k][i][j] + 0.001 * gi * gi;
                P[k][i][j] -= lr * (M1[k][i][j] / (1 - Math.pow(0.9, t))) / (Math.sqrt(V1[k][i][j] / (1 - Math.pow(0.999, t))) + 1e-8);
            }
            if (t % 250 == 0) { curve[t / 250 - 1] = lossSum / (250 * B); lossSum = 0; }
        }
        return curve;
    }

    public static void main(String[] args) {
        // ---- 1a. gradient check ---------------------------------------------------------------------------------------
        double worst = 0;
        {
            Model m = new Model(true, new Random(1));
            Example e = example(new Random(2));
            Model g = m.zeroLike();
            run(m, e, g, null, null);
            Random pr = new Random(3);
            double[][][] P = m.all(), G = g.all();
            int tested = 0;
            while (tested < 80) {
                int k = pr.nextInt(P.length), i = pr.nextInt(P[k].length), j = pr.nextInt(P[k][i].length);
                if (Math.abs(G[k][i][j]) < 1e-9) continue; // an embedding row this example does not use
                double old = P[k][i][j], h = 1e-5;
                P[k][i][j] = old + h; double lp = run(m, e, null, null, null);
                P[k][i][j] = old - h; double lm = run(m, e, null, null, null);
                P[k][i][j] = old;
                double num = (lp - lm) / (2 * h);
                worst = Math.max(worst, Math.abs(num - G[k][i][j]) / (Math.abs(num) + Math.abs(G[k][i][j])));
                tested++;
            }
        }
        check(worst < 1e-5, "hand-written gradients match finite differences");
        System.out.printf("gradient: 80 parameters, one example ; largest relative difference from finite differences %.1e%n", worst);

        // ---- 1b. training ---------------------------------------------------------------------------------------------------
        int steps = 3000;
        Model att = new Model(true, new Random(10)), avg = new Model(false, new Random(10));
        double[] ca = train(att, steps, 11), cv = train(avg, steps, 11);
        double[] attOn = new double[1];
        double accA = accuracy(att, 5000, 99, attOn), accV = accuracy(avg, 5000, 99, null);
        check(accA > 0.95, "attention learns the lookup");
        check(accV < 0.35, "averaging the positions cannot");
        StringJoiner cj = new StringJoiner(","), cw = new StringJoiner(",");
        for (double x : ca) cj.add(String.format("%.3f", x));
        for (double x : cv) cw.add(String.format("%.3f", x));
        int params = NK * D + NV * D + 2 * DK * D + D * D + NV * D;
        System.out.printf("lookup: %d (key, value) pairs then a query key ; %d keys, %d values ; d_model %d, d_k %d, %,d parameters ; Adam rate 0.003, %,d steps of 32 sequences ; on 5,000 new sequences: attention %.1f%% right, mean attention on the matching pair %.3f ; averaging the positions instead: %.1f%% right (one value in %d by chance is %.1f%%) ; loss every 250 steps: attention %s ; averaging %s%n",
                PAIRS, NK, NV, D, DK, params, steps, 100 * accA, attOn[0], 100 * accV, NV, 100.0 / NV, cj, cw);

        // ---- 2. why divide by sqrt(d_k) ------------------------------------------------------------------------------
        Random sr = new Random(20);
        StringJoiner sj = new StringJoiner(" ; ");
        double[][] res = new double[2][2];
        for (int dk : new int[]{4, 64, 512}) {
            for (int scaled = 0; scaled < 2; scaled++) {
                double maxw = 0, gnorm = 0, var = 0;
                int T = 2000, n = 10;
                for (int t = 0; t < T; t++) {
                    double[] q = new double[dk];
                    for (int i = 0; i < dk; i++) q[i] = sr.nextGaussian();
                    double[] s = new double[n];
                    for (int j = 0; j < n; j++) {
                        double dot = 0; for (int i = 0; i < dk; i++) dot += q[i] * sr.nextGaussian();
                        var += dot * dot / (T * n);
                        s[j] = scaled == 1 ? dot / Math.sqrt(dk) : dot;
                    }
                    double mx = Arrays.stream(s).max().getAsDouble(), z = 0;
                    double[] a = new double[n];
                    for (int j = 0; j < n; j++) { a[j] = Math.exp(s[j] - mx); z += a[j]; }
                    double mw = 0, gn = 0;
                    for (int j = 0; j < n; j++) { a[j] /= z; mw = Math.max(mw, a[j]); }
                    // size of the softmax's Jacobian: sum of a_j (1 - a_j), which is 0 when one weight is 1
                    for (int j = 0; j < n; j++) gn += a[j] * (1 - a[j]);
                    maxw += mw / T; gnorm += gn / T;
                }
                if (dk == 512) { res[scaled][0] = maxw; res[scaled][1] = gnorm; }
                sj.add(String.format("d_k %d %s: variance of q.k %.0f, largest weight %.3f, softmax slope %.3f", dk, scaled == 1 ? "scaled" : "unscaled", var, maxw, gnorm));
            }
        }
        check(res[0][0] > 0.95 && res[1][1] > 10 * res[0][1], "without scaling, d_k = 512 saturates the softmax");
        System.out.printf("scaling: 10 keys, random unit-variance vectors, 2,000 trials ; %s%n", sj);

        // ---- 3. sinusoidal positions -------------------------------------------------------------------------------------
        int dm = 64;
        double[][] pe = new double[100][dm];
        for (int pos = 0; pos < 100; pos++) for (int i = 0; i < dm / 2; i++) {
            double w = Math.pow(10000, -2.0 * i / dm);
            pe[pos][2 * i] = Math.sin(pos * w); pe[pos][2 * i + 1] = Math.cos(pos * w);
        }
        double maxDev = 0;
        StringJoiner pj = new StringJoiner(", ");
        for (int off : new int[]{0, 1, 2, 5, 10, 50}) {
            double first = 0;
            for (int p0 = 0; p0 + off < 100; p0++) {
                double dot = 0; for (int i = 0; i < dm; i++) dot += pe[p0][i] * pe[p0 + off][i];
                if (p0 == 0) first = dot; else maxDev = Math.max(maxDev, Math.abs(dot - first));
            }
            pj.add(String.format("%d apart: %.3f", off, first));
        }
        check(maxDev < 1e-9, "the dot product depends only on the distance");
        System.out.printf("positions: PE(pos, 2i) = sin(pos / 10000^(2i/d)), PE(pos, 2i+1) = cos(...), d = %d, positions 0 to 99 ; PE(p) . PE(p + k) for every p: %s ; largest difference between pairs with the same distance %.1e%n", dm, pj, maxDev);

        // ---- 4. cost ----------------------------------------------------------------------------------------------------------
        StringJoiner kj = new StringJoiner(" ; ");
        for (int[] nd : new int[][]{{50, 512}, {512, 512}, {4096, 512}}) {
            long n = nd[0], d = nd[1];
            long att2 = 2 * n * n * d, rec = n * d * d;
            kj.add(String.format("n %,d, d %d: attention %,d multiply-adds in 1 step, recurrent %,d in %,d steps one after another", n, d, att2, rec, n));
        }
        System.out.printf("cost: one layer, scores and weighted sums (n^2 d each) against a recurrent update (d^2 per position) ; %s%n", kj);

        // ---- the trained model, for the widget ---------------------------------------------------------------------------------
        StringBuilder wb = new StringBuilder("weights:");
        String[] names = {"Ek", "Ev", "Wq", "Wk", "Wv", "Wo"};
        double[][][] P = att.all();
        for (int k = 0; k < P.length; k++) {
            StringJoiner one = new StringJoiner(",");
            for (double[] row : P[k]) for (double x : row) one.add(String.format("%.3f", x));
            wb.append(" ; ").append(names[k]).append(' ').append(P[k].length).append('x').append(P[k][0].length).append(' ').append(one);
        }
        // the rounded weights still solve the task
        Model rounded = new Model(true, new Random(0));
        double[][][] R = rounded.all();
        for (int k = 0; k < P.length; k++) for (int i = 0; i < P[k].length; i++) for (int j = 0; j < P[k][i].length; j++) R[k][i][j] = Math.round(P[k][i][j] * 1000) / 1000.0;
        double accR = accuracy(rounded, 5000, 99, null);
        check(Math.abs(accR - accA) < 0.01, "weights rounded to 3 decimals behave the same");
        System.out.println(wb);

        System.out.println("Transformer: " + passed + " checks passed");
    }
}
