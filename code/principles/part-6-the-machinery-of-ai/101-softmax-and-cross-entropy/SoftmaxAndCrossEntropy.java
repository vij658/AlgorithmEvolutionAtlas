import java.util.*;

/**
 * Entry 101 of the principles catalog (Part 6): Softmax, log-sum-exp and cross-entropy
 *
 * HOW IT WORKS
 *   A language model ends every step with one number per token in its vocabulary (the logits). Softmax turns
 *   them into probabilities: p_i = exp(z_i) / sum_j exp(z_j). Training minimizes cross-entropy, the average of
 *   -log p(correct token). Computed naively, exp overflows (above 709.78 in double, 88.72 in float) and log(0)
 *   gives -Infinity. The fix is one line: subtract the largest logit first, which changes nothing mathematically
 *   (softmax is shift-invariant) and keeps every exponent <= 0. The same trick gives log-sum-exp, and
 *   cross-entropy = logsumexp(z) - z_target never takes the log of a rounded-to-zero probability.
 *   The gradient of cross-entropy with respect to the logits is simply softmax(z) - onehot(target).
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SoftmaxAndCrossEntropy.java
 *   Expected: the output in expected-output.txt, ending "SoftmaxAndCrossEntropy: 2121 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class SoftmaxAndCrossEntropy {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** The textbook formula. Correct on paper; overflows for logits above about 709.78. */
    static double[] softmaxNaive(double[] z) {
        double[] e = new double[z.length];
        double s = 0;
        for (int i = 0; i < z.length; i++) { e[i] = Math.exp(z[i]); s += e[i]; }
        for (int i = 0; i < z.length; i++) e[i] /= s;
        return e;
    }

    static double max(double[] z) {
        double m = Double.NEGATIVE_INFINITY;
        for (double v : z) m = Math.max(m, v);
        return m;
    }

    /** log(sum exp(z_i)), computed as m + log(sum exp(z_i - m)) so no exponent is positive. */
    static double logSumExp(double[] z) {
        double m = max(z);
        if (m == Double.NEGATIVE_INFINITY) return m;
        double s = 0;
        for (double v : z) s += Math.exp(v - m);
        return m + Math.log(s);
    }

    /** Stable softmax: subtract the largest logit first. */
    static double[] softmax(double[] z) {
        double m = max(z);
        double[] e = new double[z.length];
        double s = 0;
        for (int i = 0; i < z.length; i++) { e[i] = Math.exp(z[i] - m); s += e[i]; }
        for (int i = 0; i < z.length; i++) e[i] /= s;
        return e;
    }

    /** Softmax with temperature T: divide the logits by T. Small T sharpens, large T flattens. */
    static double[] softmax(double[] z, double temperature) {
        double[] s = new double[z.length];
        for (int i = 0; i < z.length; i++) s[i] = z[i] / temperature;
        return softmax(s);
    }

    /** -log softmax(z)[target], without ever forming the probability: logsumexp(z) - z[target]. */
    static double crossEntropy(int target, double[] logits) {
        return logSumExp(logits) - logits[target];
    }

    /** Cross-entropy of a target distribution p against the model's logits (soft labels, distillation). */
    static double crossEntropy(double[] p, double[] logits) {
        double lse = logSumExp(logits), s = 0;
        for (int i = 0; i < p.length; i++) if (p[i] > 0) s += p[i] * (lse - logits[i]);
        return s;
    }

    /** The naive version: form the probability, then take its log. */
    static double crossEntropyNaive(int target, double[] logits) {
        return -Math.log(softmaxNaive(logits)[target]);
    }

    /** d CE / d z = softmax(z) - onehot(target). */
    static double[] gradCrossEntropy(int target, double[] logits) {
        double[] g = softmax(logits);
        g[target] -= 1;
        return g;
    }

    /** Entropy in nats. */
    static double entropy(double[] p) {
        double h = 0;
        for (double v : p) if (v > 0) h -= v * Math.log(v);
        return h;
    }

    /** Kullback-Leibler divergence KL(p || q) in nats. */
    static double kl(double[] p, double[] q) {
        double d = 0;
        for (int i = 0; i < p.length; i++) if (p[i] > 0) d += p[i] * Math.log(p[i] / q[i]);
        return d;
    }

    // ----------------------------------------------------------------------------------------------------
    // Shared helpers
    // ----------------------------------------------------------------------------------------------------
    static double[] randomLogits(Random rnd, int n, double scale) {
        double[] z = new double[n];
        for (int i = 0; i < n; i++) z[i] = scale * rnd.nextGaussian();
        return z;
    }

    static double[] randomDistribution(Random rnd, int n) {
        double[] p = new double[n];
        double s = 0;
        for (int i = 0; i < n; i++) { p[i] = -Math.log(1 - rnd.nextDouble()); s += p[i]; }
        for (int i = 0; i < n; i++) p[i] /= s;
        return p;
    }

    static double sum(double[] v) { double s = 0; for (double x : v) s += x; return s; }

    static String vec(double[] v) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < v.length; i++) sb.append(i == 0 ? "" : ", ").append(f("%.6f", v[i]));
        return sb.append("]").toString();
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java SoftmaxAndCrossEntropy.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // Known answer.
        double[] known = softmax(new double[]{1, 2, 3});
        check(close(known[0], 0.09003057317038046, 1e-15) && close(known[1], 0.24472847105479764, 1e-15)
                && close(known[2], 0.6652409557748219, 1e-15), "softmax([1,2,3])");
        System.out.println("softmax([1, 2, 3]) = " + vec(known));

        // Where the naive formula breaks.
        double doubleLimit = Math.log(Double.MAX_VALUE), floatLimit = Math.log(Float.MAX_VALUE);
        check(Double.isFinite(Math.exp(709.78)) && Math.exp(709.79) == Double.POSITIVE_INFINITY, "double exp limit");
        check(Float.isFinite((float) Math.exp(88.72)) && (float) Math.exp(88.73) == Float.POSITIVE_INFINITY, "float exp limit");
        System.out.println(f("exp(x) overflows above x = %.2f in double and x = %.2f in float (32-bit)", doubleLimit, floatLimit));

        double[] big = {1000, 0};
        double[] naiveBig = softmaxNaive(big), stableBig = softmax(big);
        check(Double.isNaN(naiveBig[0]), "naive softmax of [1000, 0] is NaN");
        check(stableBig[0] == 1.0 && close(stableBig[1], Math.exp(-1000), 0), "stable softmax of [1000, 0]");
        System.out.println(f("logits [1000, 0]: naive softmax [%s, %s], stable softmax [%.1f, %.1f]",
                naiveBig[0], naiveBig[1], stableBig[0], stableBig[1]));

        double ceNaive = crossEntropyNaive(1, big), ceStable = crossEntropy(1, big);
        check(ceNaive == Double.POSITIVE_INFINITY || Double.isNaN(ceNaive), "naive cross-entropy breaks");
        check(ceStable == 1000.0, "stable cross-entropy is exactly 1000");
        System.out.println(f("cross-entropy when the correct token's logit is 1000 below the best: naive %s, stable %.1f",
                ceNaive, ceStable));

        // Stable and naive agree wherever the naive one works; softmax sums to 1; shift invariance.
        double worstRel = 0;
        for (int t = 0; t < 500; t++) {
            double[] z = randomLogits(rnd, 2 + rnd.nextInt(50), 10);
            double[] a = softmax(z), b = softmaxNaive(z);
            for (int i = 0; i < z.length; i++) worstRel = Math.max(worstRel, Math.abs(a[i] - b[i]) / b[i]);
            check(close(sum(a), 1, 1e-12), "softmax sums to 1");
            double c = (t % 2 == 0 ? 1 : -1) * 1e4 * rnd.nextDouble();
            double[] shifted = z.clone();
            for (int i = 0; i < z.length; i++) shifted[i] += c;
            double[] s = softmax(shifted);
            boolean same = true;
            for (int i = 0; i < z.length; i++) same &= close(s[i], a[i], 1e-9 * Math.max(1, a[i]) + 1e-12);
            check(same, "shift invariance");
        }
        check(worstRel < 1e-12, "stable matches naive on moderate logits");
        System.out.println(f("500 random logit vectors with sd 10: stable and naive softmax agree to a relative %.1e", worstRel));

        // Cross-entropy = entropy + KL, KL >= 0 (Gibbs' inequality), cross-entropy is smallest when q = p.
        for (int t = 0; t < 300; t++) {
            int n = 2 + rnd.nextInt(30);
            double[] p = randomDistribution(rnd, n);
            double[] z = randomLogits(rnd, n, 3);
            double[] q = softmax(z);
            check(close(crossEntropy(p, z), entropy(p) + kl(p, q), 1e-10), "H(p, q) = H(p) + KL(p || q)");
            check(kl(p, q) >= -1e-15, "Gibbs' inequality");
            double[] logp = new double[n];
            for (int i = 0; i < n; i++) logp[i] = Math.log(p[i]);
            check(crossEntropy(p, logp) <= crossEntropy(p, z) + 1e-12, "cross-entropy smallest at q = p");
        }

        // The gradient is softmax - onehot: compare with central finite differences.
        double worstGrad = 0;
        for (int t = 0; t < 200; t++) {
            int n = 2 + rnd.nextInt(20), target = rnd.nextInt(n);
            double[] z = randomLogits(rnd, n, 3);
            double[] g = gradCrossEntropy(target, z);
            double h = 1e-5;
            for (int i = 0; i < n; i++) {
                double[] up = z.clone(), dn = z.clone();
                up[i] += h; dn[i] -= h;
                double fd = (crossEntropy(target, up) - crossEntropy(target, dn)) / (2 * h);
                worstGrad = Math.max(worstGrad, Math.abs(fd - g[i]));
            }
            check(close(sum(g), 0, 1e-12), "gradient sums to zero");
        }
        check(worstGrad < 1e-8, "gradient matches finite differences");
        System.out.println(f("200 random cases: gradient softmax - onehot matches finite differences to %.1e", worstGrad));

        // What a single prediction costs: -ln p.
        StringBuilder costs = new StringBuilder("loss for one token when the model gives the right answer probability ");
        String[] ps = {"0.9", "0.5", "0.1", "0.01", "0.0001"};
        for (String p : ps) costs.append(f("%s: %.3f nats; ", p, -Math.log(Double.parseDouble(p))));
        check(close(-Math.log(0.5), Math.log(2), 1e-15), "p = 1/2 costs one bit");
        System.out.println(costs.toString().trim());

        // Uniform over a vocabulary: cross-entropy ln V, perplexity exactly V.
        int vocab = 50_000;
        double[] uniform = new double[vocab];
        double ce = crossEntropy(123, uniform);
        check(close(ce, Math.log(vocab), 1e-12), "uniform cross-entropy = ln V");
        check(close(Math.exp(ce), vocab, 1e-6), "uniform perplexity = V");
        System.out.println(f("uniform guess over %,d tokens: cross-entropy %.4f nats = %.4f bits, perplexity %.1f",
                vocab, ce, ce / Math.log(2), Math.exp(ce)));

        // Temperature: entropy rises with T; T -> 0 is argmax; T -> infinity is uniform.
        double[] z = {2.0, 1.0, 0.5, 0.0};
        StringBuilder temps = new StringBuilder("temperature on logits [2, 1, 0.5, 0]: ");
        double prevH = -1;
        for (double tt : new double[]{0.01, 0.25, 0.5, 1, 2, 10, 1000}) {
            double[] p = softmax(z, tt);
            double h = entropy(p);
            check(h > prevH, "entropy increases with temperature");
            prevH = h;
            temps.append(f("T=%s top %.4f entropy %.4f; ", tt, p[0], h));
        }
        check(softmax(z, 0.01)[0] > 0.999999, "T -> 0 approaches argmax");
        check(close(entropy(softmax(z, 1e6)), Math.log(4), 1e-6), "T -> infinity approaches uniform");
        System.out.println(temps.toString().trim());
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(101));
        System.out.println("SoftmaxAndCrossEntropy: " + passed + " checks passed");
    }
}
