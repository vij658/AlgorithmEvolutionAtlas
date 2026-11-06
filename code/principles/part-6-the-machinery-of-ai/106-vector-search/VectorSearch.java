import java.util.*;

/**
 * Entry 106 of the principles catalog (Part 6): Vector search: exact k-nearest neighbours, IVF (k-means
 * buckets) and SimHash (random-hyperplane signatures)
 *
 * HOW IT WORKS
 *   Retrieval for a language model (RAG) turns every document chunk into an embedding vector and, for a question,
 *   finds the chunks whose vectors point the most nearly the same way (cosine, entry 7). For unit vectors
 *   |u - v|^2 = 2 - 2 cos, so nearest by distance and most similar by cosine are the same list. Exact search
 *   compares the query with every vector: fine for thousands, too slow for billions. Approximate search trades a
 *   little recall for a lot of speed:
 *     IVF (inverted file): cluster the vectors with k-means (Lloyd's algorithm), keep one list per cluster, and
 *       at query time scan only the nprobe clusters whose centres are closest to the query.
 *     SimHash (Charikar, 2002): each bit records which side of a random hyperplane a vector falls on. Two vectors
 *       at angle theta disagree on a bit with probability theta / pi, so the Hamming distance between signatures
 *       (entry 5, one XOR and a bit count per 64 bits) estimates the angle. Scan the tiny signatures, then
 *       re-rank the best few candidates exactly.
 *   Recall@10, the share of the true 10 nearest neighbours that the method returns, is the number to watch.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java VectorSearch.java
 *   Expected: the output in expected-output.txt, ending "VectorSearch: 234 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class VectorSearch {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 7 (cosine-similarity-and-jaccard) and entry 3 (euclidean-distance)
    // ----------------------------------------------------------------------------------------------------
    static double dot(double[] u, double[] v) {
        double s = 0;
        for (int i = 0; i < u.length; i++) s += u[i] * v[i];
        return s;
    }

    static double dist2(double[] p, double[] q) {
        double s = 0;
        for (int i = 0; i < p.length; i++) { double d = p[i] - q[i]; s += d * d; }
        return s;
    }

    static double[] normalize(double[] v) {
        double n = Math.sqrt(dot(v, v));
        double[] out = new double[v.length];
        for (int i = 0; i < v.length; i++) out[i] = v[i] / n;
        return out;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** Indices of the k largest scores (ties: lower index first). */
    static int[] topK(double[] score, int[] candidates, int k) {
        Integer[] idx = new Integer[candidates.length];
        for (int i = 0; i < idx.length; i++) idx[i] = candidates[i];
        Arrays.sort(idx, (a, b) -> score[a] != score[b] ? Double.compare(score[b], score[a]) : Integer.compare(a, b));
        int[] out = new int[Math.min(k, idx.length)];
        for (int i = 0; i < out.length; i++) out[i] = idx[i];
        return out;
    }

    static int[] all(int n) { int[] a = new int[n]; for (int i = 0; i < n; i++) a[i] = i; return a; }

    /** Exact search: score every vector. */
    static int[] exactTopK(double[][] data, double[] q, int k) {
        double[] s = new double[data.length];
        for (int i = 0; i < data.length; i++) s[i] = dot(data[i], q);
        return topK(s, all(data.length), k);
    }

    /** Lloyd's k-means. Returns the centroids; objective[it] is the sum of squared distances after iteration it. */
    static double[][] kMeans(double[][] data, int k, int iterations, Random rnd, int[] assign, double[] objective) {
        int n = data.length, d = data[0].length;
        double[][] c = new double[k][];
        int[] start = all(n);
        for (int i = 0; i < k; i++) { int j = i + rnd.nextInt(n - i); int t = start[i]; start[i] = start[j]; start[j] = t; c[i] = data[start[i]].clone(); }
        for (int it = 0; it < iterations; it++) {
            double obj = 0;
            for (int i = 0; i < n; i++) {
                int best = 0; double bd = Double.MAX_VALUE;
                for (int j = 0; j < k; j++) { double dd = dist2(data[i], c[j]); if (dd < bd) { bd = dd; best = j; } }
                assign[i] = best; obj += bd;
            }
            objective[2 * it] = obj;                      // after the assignment step
            double[][] sum = new double[k][d];
            int[] count = new int[k];
            for (int i = 0; i < n; i++) { count[assign[i]]++; for (int x = 0; x < d; x++) sum[assign[i]][x] += data[i][x]; }
            obj = 0;
            for (int j = 0; j < k; j++) if (count[j] > 0) for (int x = 0; x < d; x++) c[j][x] = sum[j][x] / count[j];
            for (int i = 0; i < n; i++) obj += dist2(data[i], c[assign[i]]);
            objective[2 * it + 1] = obj;                  // after the update step
        }
        return c;
    }

    static final class Ivf {
        final double[][] data, centroids;
        final int[][] lists;

        Ivf(double[][] data, double[][] centroids, int[] assign) {
            this.data = data; this.centroids = centroids;
            List<List<Integer>> l = new ArrayList<>();
            for (int j = 0; j < centroids.length; j++) l.add(new ArrayList<>());
            for (int i = 0; i < data.length; i++) l.get(assign[i]).add(i);
            lists = new int[centroids.length][];
            for (int j = 0; j < centroids.length; j++) lists[j] = l.get(j).stream().mapToInt(Integer::intValue).toArray();
        }

        /** Scan the nprobe closest clusters exactly. scanned[0] receives the number of vectors compared. */
        int[] search(double[] q, int k, int nprobe, long[] scanned) {
            double[] cs = new double[centroids.length];
            for (int j = 0; j < centroids.length; j++) cs[j] = -dist2(q, centroids[j]);
            int[] probe = topK(cs, all(centroids.length), nprobe);
            int total = 0;
            for (int j : probe) total += lists[j].length;
            int[] cand = new int[total];
            int p = 0;
            for (int j : probe) for (int i : lists[j]) cand[p++] = i;
            double[] s = new double[data.length];
            for (int i : cand) s[i] = dot(data[i], q);
            scanned[0] += centroids.length + total;
            return topK(s, cand, k);
        }
    }

    static final class SimHash {
        final double[][] planes;
        SimHash(int bits, int d, Random rnd) {
            planes = new double[bits][d];
            for (double[] p : planes) for (int i = 0; i < d; i++) p[i] = rnd.nextGaussian();
        }

        long[] sign(double[] v) {
            long[] sig = new long[(planes.length + 63) / 64];
            for (int b = 0; b < planes.length; b++) if (dot(planes[b], v) >= 0) sig[b >> 6] |= 1L << (b & 63);
            return sig;
        }

        static int hamming(long[] a, long[] b) {
            int h = 0;
            for (int i = 0; i < a.length; i++) h += Long.bitCount(a[i] ^ b[i]);
            return h;
        }
    }

    /** SimHash search: rank everything by Hamming distance, then re-rank the best `rerank` exactly. */
    static int[] simHashSearch(double[][] data, long[][] sigs, SimHash sh, double[] q, int k, int rerank) {
        long[] qs = sh.sign(q);
        double[] h = new double[data.length];
        for (int i = 0; i < data.length; i++) h[i] = -SimHash.hamming(sigs[i], qs);
        int[] cand = topK(h, all(data.length), rerank);
        double[] s = new double[data.length];
        for (int i : cand) s[i] = dot(data[i], q);
        return topK(s, cand, k);
    }

    static double recall(int[] got, int[] truth) {
        Set<Integer> t = new HashSet<>();
        for (int i : truth) t.add(i);
        int hit = 0;
        for (int i : got) if (t.contains(i)) hit++;
        return hit / (double) truth.length;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java VectorSearch.java
    // ----------------------------------------------------------------------------------------------------
    static double[] gaussian(Random rnd, int d) { double[] v = new double[d]; for (int i = 0; i < d; i++) v[i] = rnd.nextGaussian(); return v; }

    static double[] clusteredPoint(Random rnd, double[][] centers) {
        double[] c = centers[rnd.nextInt(centers.length)];
        double[] g = gaussian(rnd, c.length);
        double[] v = new double[c.length];
        for (int i = 0; i < v.length; i++) v[i] = c[i] + 1.2 * g[i] / Math.sqrt(c.length);
        return normalize(v);
    }

    static void runChecks(Random rnd) {
        // 1. SimHash: the chance that one random hyperplane separates two vectors is angle / pi.
        int d = 64;
        StringBuilder sb = new StringBuilder("one random hyperplane separates two vectors at angle theta with probability theta/pi: ");
        for (int deg : new int[]{10, 30, 60, 90, 120, 170}) {
            double th = Math.toRadians(deg);
            double[] u = normalize(gaussian(rnd, d)), w = gaussian(rnd, d);
            double proj = dot(w, u);
            for (int i = 0; i < d; i++) w[i] -= proj * u[i];
            w = normalize(w);
            double[] v = new double[d];
            for (int i = 0; i < d; i++) v[i] = Math.cos(th) * u[i] + Math.sin(th) * w[i];
            int planes = 50_000, split = 0;
            for (int t = 0; t < planes; t++) {
                double[] p = gaussian(rnd, d);
                if ((dot(p, u) >= 0) != (dot(p, v) >= 0)) split++;
            }
            double expect = th / Math.PI, got = split / (double) planes;
            check(Math.abs(got - expect) < 4.5 * Math.sqrt(expect * (1 - expect) / planes), "P(split) = theta/pi");
            sb.append(f("%d deg: %.4f (theta/pi = %.4f); ", deg, got, expect));
        }
        System.out.println(sb.toString().trim());

        // 2. A collection: 20,000 unit vectors in 64 dimensions around 200 topics, and 200 queries.
        int n = 20_000, topics = 200, queries = 200, k = 10;
        double[][] centers = new double[topics][];
        for (int i = 0; i < topics; i++) centers[i] = normalize(gaussian(rnd, d));
        double[][] data = new double[n][];
        for (int i = 0; i < n; i++) data[i] = clusteredPoint(rnd, centers);
        double[][] qs = new double[queries][];
        int[][] truth = new int[queries][];
        for (int q = 0; q < queries; q++) { qs[q] = clusteredPoint(rnd, centers); truth[q] = exactTopK(data, qs[q], k); }

        // For unit vectors, nearest by Euclidean distance = most similar by cosine.
        for (int q = 0; q < queries; q++) {
            double[] s = new double[n];
            for (int i = 0; i < n; i++) s[i] = -dist2(data[i], qs[q]);
            check(Arrays.equals(topK(s, all(n), k), truth[q]), "L2 ranking = cosine ranking for unit vectors");
        }
        System.out.println(f("%,d unit vectors in %d dimensions, %d queries: exact top-%d by cosine equals exact top-%d by distance for every query",
                n, d, queries, k, k));

        // 3. IVF: k-means into 128 clusters. The k-means objective never goes up.
        int clusters = 128, iterations = 8;
        int[] assign = new int[n];
        double[] obj = new double[2 * iterations];
        double[][] centroids = kMeans(data, clusters, iterations, rnd, assign, obj);
        for (int i = 1; i < obj.length; i++) check(obj[i] <= obj[i - 1] + 1e-9, "Lloyd's algorithm never increases the objective");
        System.out.println(f("k-means, %d clusters, %d iterations: sum of squared distances %.1f after the first assignment, %.1f at the end",
                clusters, iterations, obj[0], obj[obj.length - 1]));
        Ivf ivf = new Ivf(data, centroids, assign);
        StringBuilder ib = new StringBuilder("IVF recall@10 by clusters scanned (comparisons include the 128 cluster centres): ");
        double prev = -1;
        for (int nprobe : new int[]{1, 2, 4, 8, 16, 128}) {
            long[] scanned = {0};
            double r = 0;
            for (int q = 0; q < queries; q++) r += recall(ivf.search(qs[q], k, nprobe, scanned), truth[q]);
            r /= queries;
            check(r >= prev, "recall never falls as more clusters are scanned");
            prev = r;
            if (nprobe == clusters) check(r == 1.0, "scanning every cluster is exact");
            ib.append(f("nprobe %d: %.3f with %.1f%% of a full scan's comparisons; ", nprobe, r, 100.0 * scanned[0] / queries / n));
        }
        System.out.println(ib.toString().trim());

        // 4. SimHash: 128-bit signatures (16 bytes instead of 512), Hamming scan, exact re-rank.
        SimHash sh = new SimHash(128, d, rnd);
        long[][] sigs = new long[n][];
        for (int i = 0; i < n; i++) sigs[i] = sh.sign(data[i]);
        StringBuilder hb = new StringBuilder("SimHash (128 bits) recall@10 by candidates re-ranked exactly: ");
        prev = -1;
        for (int rerank : new int[]{10, 50, 200, 1000, n}) {
            double r = 0;
            for (int q = 0; q < queries; q++) r += recall(simHashSearch(data, sigs, sh, qs[q], k, rerank), truth[q]);
            r /= queries;
            check(r >= prev, "recall never falls as more candidates are re-ranked");
            prev = r;
            if (rerank == n) check(r == 1.0, "re-ranking everything is exact");
            hb.append(f("%,d: %.3f; ", rerank, r));
        }
        System.out.println(hb.toString().trim());
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(106));
        System.out.println("VectorSearch: " + passed + " checks passed");
    }
}
