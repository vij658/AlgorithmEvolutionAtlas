import java.util.*;

/**
 * Entry 104 of the principles catalog (Part 6): Scaled dot-product attention, the causal mask and the KV cache
 *
 * HOW IT WORKS
 *   Each token's vector is projected three ways: a query q (what am I looking for?), a key k (what do I offer?)
 *   and a value v (what do I pass on?). A token's output is a weighted average of the values of the tokens it may
 *   see, with weights softmax(q . k / sqrt(d)) (entry 101). Dividing by sqrt(d) matters: the dot product of two
 *   random d-dimensional vectors has variance d, so without it the softmax saturates and almost all weight lands
 *   on one token. Several heads do this in parallel on slices of the vector. A language model may only look
 *   backwards (the causal mask), so when it generates token t, the keys and values of tokens 0..t-1 are exactly
 *   what they were at the previous step. The KV cache stores them instead of recomputing them: each new token
 *   then costs work proportional to t instead of t^2, at the price of memory that grows with every token.
 *   Grouped-query attention lets several query heads share one key/value head, shrinking that memory.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AttentionAndKvCache.java
 *   Expected: the output in expected-output.txt, ending "AttentionAndKvCache: 402 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class AttentionAndKvCache {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    static long macs = 0;   // multiply-adds performed, counted inside the two helpers below

    static double dot(double[] a, int aOff, double[] b, int bOff, int n) {
        double s = 0;
        for (int i = 0; i < n; i++) s += a[aOff + i] * b[bOff + i];
        macs += n;
        return s;
    }

    /** x (1 x rows) times w (rows x cols). */
    static double[] project(double[] x, double[][] w) {
        int cols = w[0].length;
        double[] out = new double[cols];
        for (int i = 0; i < x.length; i++) for (int j = 0; j < cols; j++) out[j] += x[i] * w[i][j];
        macs += (long) x.length * cols;
        return out;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helper copied from entry 101 (softmax-and-cross-entropy): stable softmax
    // ----------------------------------------------------------------------------------------------------
    static double[] softmax(double[] z, int n) {
        double m = Double.NEGATIVE_INFINITY;
        for (int i = 0; i < n; i++) m = Math.max(m, z[i]);
        double[] e = new double[n];
        double s = 0;
        for (int i = 0; i < n; i++) { e[i] = Math.exp(z[i] - m); s += e[i]; }
        for (int i = 0; i < n; i++) e[i] /= s;
        return e;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class Attention {
        final int dModel, heads, kvHeads, dHead;
        final double[][] wq, wk, wv, wo;
        double[][] lastWeights;   // attention weights of the most recent output row, per head (for checks)

        Attention(int dModel, int heads, int kvHeads, Random rnd) {
            this.dModel = dModel; this.heads = heads; this.kvHeads = kvHeads; this.dHead = dModel / heads;
            wq = random(dModel, heads * dHead, rnd);
            wk = random(dModel, kvHeads * dHead, rnd);
            wv = random(dModel, kvHeads * dHead, rnd);
            wo = random(heads * dHead, dModel, rnd);
        }

        static double[][] random(int r, int c, Random rnd) {
            double[][] w = new double[r][c];
            for (double[] row : w) for (int j = 0; j < c; j++) row[j] = rnd.nextGaussian() / Math.sqrt(r);
            return w;
        }

        /** Query head h reads key/value head h / (heads / kvHeads): grouped-query attention. */
        int kvHeadOf(int h) { return h / (heads / kvHeads); }

        /** One output row: query q attends to keys[0..n) and values[0..n). */
        double[] attend(double[] q, List<double[]> keys, List<double[]> values, int n) {
            double[] o = new double[heads * dHead];
            lastWeights = new double[heads][];
            double scale = 1 / Math.sqrt(dHead);
            for (int h = 0; h < heads; h++) {
                int g = kvHeadOf(h);
                double[] scores = new double[n];
                for (int j = 0; j < n; j++) scores[j] = dot(q, h * dHead, keys.get(j), g * dHead, dHead) * scale;
                double[] a = softmax(scores, n);
                lastWeights[h] = a;
                for (int j = 0; j < n; j++) {
                    double[] v = values.get(j);
                    for (int i = 0; i < dHead; i++) o[h * dHead + i] += a[j] * v[g * dHead + i];
                }
                macs += (long) n * dHead;
            }
            return project(o, wo);
        }

        /** The whole sequence at once. causal = true: row i sees rows 0..i only. */
        double[][] full(double[][] x, boolean causal) {
            int n = x.length;
            List<double[]> q = new ArrayList<>(), k = new ArrayList<>(), v = new ArrayList<>();
            for (double[] row : x) { q.add(project(row, wq)); k.add(project(row, wk)); v.add(project(row, wv)); }
            double[][] y = new double[n][];
            for (int i = 0; i < n; i++) y[i] = attend(q.get(i), k, v, causal ? i + 1 : n);
            return y;
        }
    }

    /** Generation with a KV cache: each step projects only the new token and appends its key and value. */
    static final class KvCache {
        final Attention att;
        final List<double[]> keys = new ArrayList<>(), values = new ArrayList<>();

        KvCache(Attention att) { this.att = att; }

        double[] step(double[] x) {
            keys.add(project(x, att.wk));
            values.add(project(x, att.wv));
            return att.attend(project(x, att.wq), keys, values, keys.size());
        }

        long storedNumbers() { return (long) keys.size() * (keys.get(0).length + values.get(0).length); }
    }

    /** Bytes of KV cache: keys and values, for every layer, KV head, dimension and token. */
    static long kvCacheBytes(long layers, long kvHeads, long dHead, long tokens, long bytesPerNumber) {
        return 2 * layers * kvHeads * dHead * tokens * bytesPerNumber;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java AttentionAndKvCache.java
    // ----------------------------------------------------------------------------------------------------
    static double[][] randomInput(Random rnd, int n, int d) {
        double[][] x = new double[n][d];
        for (double[] row : x) for (int j = 0; j < d; j++) row[j] = rnd.nextGaussian();
        return x;
    }

    static double maxDiff(double[] a, double[] b) {
        double m = 0;
        for (int i = 0; i < a.length; i++) m = Math.max(m, Math.abs(a[i] - b[i]));
        return m;
    }

    static void runChecks(Random rnd) {
        int dModel = 32, heads = 4, n = 24;

        // 1. The KV cache gives the same outputs as recomputing everything, for full, grouped and single KV heads.
        StringBuilder sb = new StringBuilder(f("%d tokens, model width %d, %d query heads: ", n, dModel, heads));
        for (int kvHeads : new int[]{4, 2, 1}) {
            Attention att = new Attention(dModel, heads, kvHeads, rnd);
            double[][] x = randomInput(rnd, n, dModel);
            double[][] y = att.full(x, true);
            KvCache cache = new KvCache(att);
            double worst = 0;
            for (int t = 0; t < n; t++) {
                double[] yt = cache.step(x[t]);
                worst = Math.max(worst, maxDiff(yt, y[t]));
                for (double[] w : att.lastWeights) {
                    double s = 0;
                    for (double v : w) s += v;
                    check(Math.abs(s - 1) < 1e-12, "attention weights sum to 1");
                }
            }
            check(worst < 1e-12, "KV cache equals full recomputation");
            check(cache.storedNumbers() == (long) n * 2 * kvHeads * (dModel / heads), "cache size");
            sb.append(f("%d KV head%s: cache holds %,d numbers, largest difference from full recomputation %.1e; ",
                    kvHeads, kvHeads == 1 ? "" : "s", cache.storedNumbers(), worst));
        }
        System.out.println(sb.toString().trim());

        // 2. The causal mask: changing a later token never changes an earlier output (exactly).
        Attention att = new Attention(dModel, heads, heads, rnd);
        double[][] x = randomInput(rnd, n, dModel);
        double[][] y = att.full(x, true);
        for (int trial = 0; trial < 50; trial++) {
            int j = 1 + rnd.nextInt(n - 1);
            double[][] x2 = new double[n][];
            for (int i = 0; i < n; i++) x2[i] = x[i].clone();
            for (int c = 0; c < dModel; c++) x2[j][c] += rnd.nextGaussian();
            double[][] y2 = att.full(x2, true);
            boolean same = true, laterChanged = false;
            for (int i = 0; i < j; i++) same &= Arrays.equals(y[i], y2[i]);
            for (int i = j; i < n; i++) laterChanged |= !Arrays.equals(y[i], y2[i]);
            check(same, "earlier outputs unchanged");
            check(laterChanged, "later outputs do change");
        }
        System.out.println("causal mask: in 50 trials, changing token j left outputs 0..j-1 bit-for-bit identical");

        // 3. Without a mask and without position information, attention cannot see order:
        //    shuffling the input rows shuffles the output rows the same way.
        double[][] yAll = att.full(x, false);
        double worstPerm = 0;
        for (int trial = 0; trial < 20; trial++) {
            int[] perm = new int[n];
            for (int i = 0; i < n; i++) perm[i] = i;
            for (int i = n - 1; i > 0; i--) { int r = rnd.nextInt(i + 1); int tmp = perm[i]; perm[i] = perm[r]; perm[r] = tmp; }
            double[][] xp = new double[n][];
            for (int i = 0; i < n; i++) xp[i] = x[perm[i]];
            double[][] yp = att.full(xp, false);
            for (int i = 0; i < n; i++) worstPerm = Math.max(worstPerm, maxDiff(yp[i], yAll[perm[i]]));
        }
        check(worstPerm < 1e-12, "permutation equivariance");
        System.out.println(f("no mask, no positions: 20 shuffles of the input shuffle the output identically "
                + "(largest difference %.1e), so word order must be added separately", worstPerm));

        // 4. Why divide by sqrt(d): the variance of q . k grows like d, and an unscaled softmax saturates.
        StringBuilder var = new StringBuilder("variance of q . k for random vectors with unit-variance entries: ");
        for (int d : new int[]{16, 64, 256, 1024}) {
            int samples = 20_000;
            double s = 0, s2 = 0;
            double[] q = new double[d], k = new double[d];
            for (int t = 0; t < samples; t++) {
                for (int i = 0; i < d; i++) { q[i] = rnd.nextGaussian(); k[i] = rnd.nextGaussian(); }
                double v = dot(q, 0, k, 0, d);
                s += v; s2 += v * v;
            }
            double variance = s2 / samples - (s / samples) * (s / samples);
            check(Math.abs(variance / d - 1) < 0.05, "variance of a dot product is about d");
            var.append(f("d=%d: %.1f; ", d, variance));
        }
        System.out.println(var.toString().trim());

        int d = 256, keysN = 64, trials = 2000;
        double maxUnscaled = 0, maxScaled = 0;
        for (int t = 0; t < trials; t++) {
            double[] q = new double[d];
            for (int i = 0; i < d; i++) q[i] = rnd.nextGaussian();
            double[] raw = new double[keysN], scaled = new double[keysN];
            for (int j = 0; j < keysN; j++) {
                double s = 0;
                for (int i = 0; i < d; i++) s += q[i] * rnd.nextGaussian();
                raw[j] = s; scaled[j] = s / Math.sqrt(d);
            }
            maxUnscaled += Arrays.stream(softmax(raw, keysN)).max().getAsDouble();
            maxScaled += Arrays.stream(softmax(scaled, keysN)).max().getAsDouble();
        }
        maxUnscaled /= trials; maxScaled /= trials;
        check(maxUnscaled > 0.8 && maxScaled < 0.3, "scaling keeps the softmax from saturating");
        System.out.println(f("d=256, 64 keys: the largest attention weight averages %.3f without the 1/sqrt(d) and %.3f with it",
                maxUnscaled, maxScaled));

        // 5. Work to generate n tokens, counted: recompute everything each step, or use the cache.
        Attention a1 = new Attention(dModel, heads, heads, rnd);
        double[][] xs = randomInput(rnd, n, dModel);
        macs = 0;
        for (int t = 1; t <= n; t++) a1.full(Arrays.copyOf(xs, t), true);
        long noCache = macs;
        macs = 0;
        KvCache kc = new KvCache(a1);
        for (int t = 0; t < n; t++) kc.step(xs[t]);
        long withCache = macs;
        long dm = dModel;
        long formulaCache = 0, formulaNoCache = 0;
        for (long t = 1; t <= n; t++) {
            formulaCache += 4 * dm * dm + 2 * dm * t;
            formulaNoCache += 4 * dm * dm * t + dm * t * (t + 1);
        }
        check(withCache == formulaCache && noCache == formulaNoCache, "counted multiply-adds match the formulas");
        System.out.println(f("generating %d tokens (width %d): %,d multiply-adds recomputing everything, %,d with the KV cache (%.1f times fewer)",
                n, dModel, noCache, withCache, noCache / (double) withCache));
        long bigN = 4096, bigD = 4096, c2 = 0, n2 = 0;
        for (long t = 1; t <= bigN; t++) { c2 += 4 * bigD * bigD + 2 * bigD * t; n2 += 4 * bigD * bigD * t + bigD * t * (t + 1); }
        System.out.println(f("same formulas for %,d tokens at width %,d, one layer: %.3g against %.3g multiply-adds (%.0f times fewer)",
                bigN, bigD, (double) n2, (double) c2, n2 / (double) c2));

        // 6. The price: memory. 32 layers, 32 heads of 128 dimensions, 16-bit numbers, 8,192 tokens.
        long mha = kvCacheBytes(32, 32, 128, 8192, 2), gqa = kvCacheBytes(32, 8, 128, 8192, 2);
        long perToken = kvCacheBytes(32, 32, 128, 1, 2);
        check(mha == 4L << 30 && gqa == 1L << 30 && perToken == 512 << 10, "KV cache sizes");
        System.out.println(f("KV cache for 32 layers x 32 heads x 128 dims at 16 bits: %d KiB per token, %d GiB for 8,192 tokens; "
                + "with 8 shared KV heads (grouped-query attention): %d GiB", perToken >> 10, mha >> 30, gqa >> 30));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(104));
        System.out.println("AttentionAndKvCache: " + passed + " checks passed");
    }
}
