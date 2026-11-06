import java.util.*;

/**
 * Entry 105 of the principles catalog (Part 6): Choosing the next token: greedy, temperature, top-k, top-p and
 * beam search
 *
 * HOW IT WORKS
 *   A language model gives a probability for every possible next token (entry 101); something else must pick one.
 *   Greedy takes the most likely token. Sampling draws one at random in proportion to its probability (inverse
 *   CDF: walk the cumulative sum until it passes a uniform random number). Temperature divides the logits first
 *   (low = safer, high = more varied). Top-k keeps only the k most likely tokens; top-p ("nucleus" sampling) keeps
 *   the smallest set of most-likely tokens whose probabilities add up to at least p; both renormalize and cut off
 *   the long tail of unlikely tokens. Beam search keeps the k best partial sequences instead of one, because the
 *   locally best token is not always the start of the best sequence (entry 24: greedy needs an exchange argument,
 *   and here there is none). Even "temperature 0" can vary between runs: the logits are long floating-point sums,
 *   floating-point addition is not associative (entry 18), and servers add in different orders for different
 *   batch sizes, so near-ties can flip.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SamplingAndDecoding.java
 *   Expected: the output in expected-output.txt, ending "SamplingAndDecoding: 5515 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class SamplingAndDecoding {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    // ----------------------------------------------------------------------------------------------------
    // Helper copied from entry 101 (softmax-and-cross-entropy): stable softmax with temperature
    // ----------------------------------------------------------------------------------------------------
    static double[] softmax(double[] z, double temperature) {
        double m = Double.NEGATIVE_INFINITY;
        for (double v : z) m = Math.max(m, v / temperature);
        double[] e = new double[z.length];
        double s = 0;
        for (int i = 0; i < z.length; i++) { e[i] = Math.exp(z[i] / temperature - m); s += e[i]; }
        for (int i = 0; i < z.length; i++) e[i] /= s;
        return e;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int argmax(double[] p) {
        int best = 0;
        for (int i = 1; i < p.length; i++) if (p[i] > p[best]) best = i;
        return best;
    }

    /** Token indices from most to least likely (ties: lower index first). */
    static Integer[] byProbability(double[] p) {
        Integer[] idx = new Integer[p.length];
        for (int i = 0; i < p.length; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> p[a] != p[b] ? Double.compare(p[b], p[a]) : Integer.compare(a, b));
        return idx;
    }

    static double[] keepAndRenormalize(double[] p, Integer[] order, int keep) {
        double[] out = new double[p.length];
        double s = 0;
        for (int r = 0; r < keep; r++) s += p[order[r]];
        for (int r = 0; r < keep; r++) out[order[r]] = p[order[r]] / s;
        return out;
    }

    /** Keep the k most likely tokens. */
    static double[] topK(double[] p, int k) {
        return keepAndRenormalize(p, byProbability(p), Math.min(k, p.length));
    }

    /** Keep the smallest set of most likely tokens whose total probability is at least topP. */
    static double[] topP(double[] p, double topP) {
        Integer[] order = byProbability(p);
        double cum = 0;
        int keep = 0;
        while (keep < p.length && cum < topP) cum += p[order[keep++]];
        return keepAndRenormalize(p, order, Math.max(1, keep));
    }

    static int countKept(double[] p) { int c = 0; for (double v : p) if (v > 0) c++; return c; }

    /** Inverse-CDF sampling. */
    static int sample(double[] p, Random rnd) {
        double u = rnd.nextDouble(), cum = 0;
        for (int i = 0; i < p.length; i++) { cum += p[i]; if (u < cum) return i; }
        for (int i = p.length - 1; i >= 0; i--) if (p[i] > 0) return i;   // u landed in the rounding gap
        return p.length - 1;
    }

    // ----------------------------------------------------------------------------------------------------
    // Sequence decoding on a toy language model: a fixed random next-token distribution for every prefix
    // ----------------------------------------------------------------------------------------------------
    interface Model { double[] next(List<Integer> prefix); }

    static Model randomModel(long seed, int vocab, double spread) {
        return prefix -> {
            long h = seed;
            for (int t : prefix) h = h * 1_000_003L + t + 1;
            Random r = new Random(h);
            double[] z = new double[vocab];
            for (int i = 0; i < vocab; i++) z[i] = spread * r.nextGaussian();
            return softmax(z, 1);
        };
    }

    record Hyp(List<Integer> tokens, double logProb) {}

    static Hyp greedy(Model m, int length) { return beam(m, length, 1); }

    static Hyp beam(Model m, int length, int width) {
        List<Hyp> beam = List.of(new Hyp(List.of(), 0));
        for (int step = 0; step < length; step++) {
            List<Hyp> next = new ArrayList<>();
            for (Hyp h : beam) {
                double[] p = m.next(h.tokens());
                for (int t = 0; t < p.length; t++) {
                    List<Integer> toks = new ArrayList<>(h.tokens());
                    toks.add(t);
                    next.add(new Hyp(toks, h.logProb() + Math.log(p[t])));
                }
            }
            next.sort((a, b) -> Double.compare(b.logProb(), a.logProb()));
            beam = next.subList(0, Math.min(width, next.size()));
        }
        return beam.get(0);
    }

    static Hyp exhaustive(Model m, int length, List<Integer> prefix, double logProb) {
        if (prefix.size() == length) return new Hyp(prefix, logProb);
        double[] p = m.next(prefix);
        Hyp best = null;
        for (int t = 0; t < p.length; t++) {
            List<Integer> toks = new ArrayList<>(prefix);
            toks.add(t);
            Hyp h = exhaustive(m, length, toks, logProb + Math.log(p[t]));
            if (best == null || h.logProb() > best.logProb()) best = h;
        }
        return best;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java SamplingAndDecoding.java
    // ----------------------------------------------------------------------------------------------------
    static double[] randomDistribution(Random rnd, int n, double spread) {
        double[] z = new double[n];
        for (int i = 0; i < n; i++) z[i] = spread * rnd.nextGaussian();
        return softmax(z, 1);
    }

    static void runChecks(Random rnd) {
        // 1. Top-p keeps the SMALLEST set reaching p; top-k with k = 1 is greedy; both renormalize.
        for (int t = 0; t < 1000; t++) {
            int n = 2 + rnd.nextInt(40);
            double[] p = randomDistribution(rnd, n, 2);
            double pp = rnd.nextDouble();
            double[] q = topP(p, pp);
            int kept = countKept(q);
            Integer[] order = byProbability(p);
            double massKept = 0, massOneLess = 0;
            for (int r = 0; r < kept; r++) massKept += p[order[r]];
            for (int r = 0; r < kept - 1; r++) massOneLess += p[order[r]];
            check(massKept >= pp - 1e-12 || kept == n, "top-p reaches p");
            check(massOneLess < pp, "top-p set is the smallest");
            check(close(Arrays.stream(q).sum(), 1, 1e-12), "renormalized");
            double[] g = topK(p, 1);
            check(g[argmax(p)] == 1.0, "top-k with k = 1 is greedy");
        }

        // 2. A worked example: what each rule keeps.
        double[] logits = {3.0, 2.5, 2.0, 1.0, 0.5, 0.0, -1.0, -2.0, -3.0, -4.0};
        double[] p = softmax(logits, 1);
        StringBuilder sb = new StringBuilder("10-token example, probabilities");
        for (double v : p) sb.append(f(" %.3f", v));
        System.out.println(sb);
        double[] p07 = softmax(logits, 0.7), p15 = softmax(logits, 1.5);
        System.out.println(f("temperature 0.7: top token %.3f; temperature 1.5: top token %.3f; top-k 3 keeps %d; "
                + "top-p 0.9 keeps %d; top-p 0.9 at temperature 0.7 keeps %d",
                p07[0], p15[0], countKept(topK(p, 3)), countKept(topP(p, 0.9)), countKept(topP(p07, 0.9))));
        check(countKept(topP(p, 0.9)) == 4 && countKept(topP(p07, 0.9)) == 3, "worked example counts: 0.441 + 0.267 + 0.162 = 0.870 < 0.9");

        // 3. Sampling matches the target: 200,000 draws from top-p 0.9 at temperature 0.7.
        double[] target = topP(p07, 0.9);
        int draws = 200_000;
        int[] counts = new int[target.length];
        Random sampler = new Random(42);
        for (int i = 0; i < draws; i++) counts[sample(target, sampler)]++;
        double worstZ = 0;
        for (int i = 0; i < target.length; i++) {
            if (target[i] == 0) { check(counts[i] == 0, "cut tokens are never drawn"); continue; }
            double sd = Math.sqrt(draws * target[i] * (1 - target[i]));
            double z = Math.abs(counts[i] - draws * target[i]) / sd;
            worstZ = Math.max(worstZ, z);
            check(z < 4.5, "sample frequency matches probability");
        }
        System.out.println(f("200,000 draws from top-p 0.9 at temperature 0.7: every kept token within %.2f standard errors "
                + "of its probability; the %d cut tokens drawn 0 times", worstZ, target.length - countKept(target)));

        // 4. Same seed, same text. Different seed, different text.
        int[] a = new int[50], b = new int[50], c = new int[50];
        Random r1 = new Random(7), r2 = new Random(7), r3 = new Random(8);
        for (int i = 0; i < 50; i++) { a[i] = sample(p, r1); b[i] = sample(p, r2); c[i] = sample(p, r3); }
        check(Arrays.equals(a, b) && !Arrays.equals(a, c), "seeded sampling is reproducible");

        // 5. Why "temperature 0" can still vary: the same numbers added in a different order.
        //    Token A's logit and token B's logit are sums of the SAME 4,096 terms, so they are equal in exact
        //    arithmetic; in 32-bit floats the order of addition decides which one is bigger.
        int trials = 2000, differ = 0, bWins = 0, differDouble = 0;
        for (int t = 0; t < trials; t++) {
            float[] terms = new float[4096];
            for (int i = 0; i < terms.length; i++) terms[i] = (float) rnd.nextGaussian();
            float[] shuffled = terms.clone();
            for (int i = shuffled.length - 1; i > 0; i--) { int j = rnd.nextInt(i + 1); float tmp = shuffled[i]; shuffled[i] = shuffled[j]; shuffled[j] = tmp; }
            float sa = 0, sb2 = 0;
            double da = 0, db = 0;
            for (float v : terms) { sa += v; da += v; }
            for (float v : shuffled) { sb2 += v; db += v; }
            if (sa != sb2) differ++;
            if (sb2 > sa) bWins++;
            if (da != db) differDouble++;
        }
        check(differ > trials / 2, "float sums depend on order");
        System.out.println(f("two logits that are the same 4,096 numbers added in different orders: unequal in %d of %d trials "
                + "with a 32-bit total (B came out ahead %d times); with a 64-bit total, %d of %d",
                differ, trials, bWins, differDouble, trials));

        // 6. Greedy is not optimal: a hand example.
        Model hand = prefix -> {
            if (prefix.isEmpty()) return new double[]{0.6, 0.4, 0.0};
            if (prefix.size() == 1 && prefix.get(0) == 0) return new double[]{0.3, 0.3, 0.4};
            return new double[]{0.9, 0.1, 0.0};
        };
        Hyp g = greedy(hand, 2), bm = beam(hand, 2, 2);
        check(close(Math.exp(g.logProb()), 0.24, 1e-12) && close(Math.exp(bm.logProb()), 0.36, 1e-12), "hand example");
        System.out.println(f("hand example: greedy picks %s with probability %.2f; beam width 2 finds %s with probability %.2f",
                g.tokens(), Math.exp(g.logProb()), bm.tokens(), Math.exp(bm.logProb())));

        // 7. Random toy models: vocabulary 5, length 5 (3,125 sequences each).
        int models = 300, vocab = 5, len = 5;
        int[] widths = {1, 2, 4, 8};
        int[] optimal = new int[widths.length];
        int widerWorse = 0;
        for (int mIdx = 0; mIdx < models; mIdx++) {
            Model m = randomModel(1000 + mIdx, vocab, 1.0);
            Hyp best = exhaustive(m, len, List.of(), 0);
            double prev = Double.NEGATIVE_INFINITY;
            for (int w = 0; w < widths.length; w++) {
                Hyp h = beam(m, len, widths[w]);
                check(h.logProb() <= best.logProb() + 1e-12, "exhaustive search is an upper bound");
                if (close(h.logProb(), best.logProb(), 1e-12)) optimal[w]++;
                if (h.logProb() < prev - 1e-12) widerWorse++;
                prev = Math.max(prev, h.logProb());
            }
            Hyp full = beam(m, len, (int) Math.pow(vocab, len));
            check(close(full.logProb(), best.logProb(), 1e-12), "a beam as wide as the tree is exhaustive");
        }
        StringBuilder bs = new StringBuilder(f("%d random models, vocabulary %d, length %d: most likely sequence found by ", models, vocab, len));
        for (int w = 0; w < widths.length; w++) bs.append(f("%s %d times; ", widths[w] == 1 ? "greedy" : "beam " + widths[w], optimal[w]));
        bs.append(f("a wider beam did worse than a narrower one %d time%s", widerWorse, widerWorse == 1 ? "" : "s"));
        System.out.println(bs.toString().trim());
        check(optimal[0] < optimal[widths.length - 1], "wider beams find the best sequence more often");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(105));
        System.out.println("SamplingAndDecoding: " + passed + " checks passed");
    }
}
