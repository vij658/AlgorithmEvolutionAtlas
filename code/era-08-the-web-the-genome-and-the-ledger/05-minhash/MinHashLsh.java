import java.nio.file.*;
import java.util.*;

/**
 * Era 8, topic 5: MinHash and locality-sensitive hashing (Broder, Digital's Systems Research Center, 1997; Indyk and
 * Motwani, Stanford, 1998).
 *
 * HOW IT WORKS
 *   Cut a document into its overlapping runs of w words, its "shingles". Two documents resemble each other as much as
 *   their sets of shingles overlap: resemblance (the Jaccard index) = shared shingles / all shingles of either.
 *   Computing that for every pair of millions of documents is hopeless, so Broder sketches each document: put all
 *   possible shingles in a random order and keep the one that comes first in each document. The first shingle of
 *   the union of A and B is equally likely to be any of its members, and the two documents keep the same one exactly
 *   when it is shared, so Pr[same minimum] = shared / union = the resemblance. With k independent orders (in practice,
 *   k hash functions), the fraction of agreeing minima estimates the resemblance with an error near sqrt(J(1-J)/k).
 *   To find similar pairs without comparing all of them, cut each sketch into b bands of r numbers and put each band
 *   in a hash table: two documents become candidates if they agree on a whole band, which happens with probability
 *   1 - (1 - J^r)^b, a steep S-shaped curve. This is locality-sensitive hashing: similar items collide on purpose.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The key fact checked exactly: for every pair of subsets of a 7-element universe, the fraction of the 5,040
 *      orders in which the minima agree equals the Jaccard index, as a fraction.
 *   2. Documents: this book's field notes (corpus.txt) cut into 40-word pieces, plus copies with 5%, 10%, 20% and 40%
 *      of their words replaced. Exact resemblance against MinHash estimates with 16, 64 and 256 hash functions.
 *   3. Banding: how often pairs of known resemblance become candidates, against 1 - (1 - J^r)^b.
 *   4. Finding all pairs with resemblance at least 0.5: every pair compared, against LSH candidates only.
 *   5. Two sentences for the book's widget, with 32 hash functions it can repeat.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step; corpus.txt must be in the current folder)
 *   java MinHashLsh.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MinHashLsh {
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

    static long mix64(long z) {
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    static long fnv64(String t) { // 64-bit FNV-1a
        long h = 0xcbf29ce484222325L;
        for (char c : t.toCharArray()) { h ^= c; h *= 0x100000001b3L; }
        return h;
    }

    /** The shingles of a list of words: each run of w words, as a 64-bit FNV-1a hash of its text. */
    static long[] shingles(List<String> words, int w) {
        Set<Long> s = new HashSet<>();
        for (int i = 0; i + w <= words.size(); i++) s.add(fnv64(String.join(" ", words.subList(i, i + w))));
        long[] a = new long[s.size()];
        int q = 0;
        for (long x : s) a[q++] = x;
        Arrays.sort(a);
        return a;
    }

    static double jaccard(long[] a, long[] b) { // both sorted
        int i = 0, j = 0, inter = 0;
        while (i < a.length && j < b.length) {
            if (a[i] == b[j]) { inter++; i++; j++; } else if (a[i] < b[j]) i++; else j++;
        }
        return (double) inter / (a.length + b.length - inter);
    }

    static long[] sketch(long[] set, int k) {
        long[] m = new long[k];
        Arrays.fill(m, Long.MAX_VALUE);
        for (long x : set) for (int i = 0; i < k; i++) {
            long h = mix64(x ^ (0x9e3779b97f4a7c15L * (i + 1))) >>> 1;
            if (h < m[i]) m[i] = h;
        }
        return m;
    }

    static double estimate(long[] a, long[] b, int k) { int e = 0; for (int i = 0; i < k; i++) if (a[i] == b[i]) e++; return (double) e / k; }

    static void permutations(int[] p, int k, List<int[]> out) {
        if (k == p.length) { out.add(p.clone()); return; }
        for (int i = k; i < p.length; i++) {
            int t = p[k]; p[k] = p[i]; p[i] = t;
            permutations(p, k + 1, out);
            t = p[k]; p[k] = p[i]; p[i] = t;
        }
    }

    public static void main(String[] args) throws Exception {
        // ---- 1. the key fact, exactly -----------------------------------------------------------------------------
        List<int[]> perms = new ArrayList<>();
        permutations(new int[]{0, 1, 2, 3, 4, 5, 6}, 0, perms);
        int pairs = 0;
        for (int A = 1; A < 128; A++) for (int B = 1; B < 128; B++) {
            int agree = 0;
            for (int[] p : perms) { // p[x] is the place of element x in the order
                int ma = 99, mb = 99;
                for (int x = 0; x < 7; x++) { if ((A >> x & 1) == 1) ma = Math.min(ma, p[x]); if ((B >> x & 1) == 1) mb = Math.min(mb, p[x]); }
                if (ma == mb) agree++;
            }
            int inter = Integer.bitCount(A & B), union = Integer.bitCount(A | B);
            check((long) agree * union == (long) perms.size() * inter, "Pr[minima agree] = |A and B| / |A or B| exactly");
            pairs++;
        }
        System.out.printf("exact: all %,d pairs of non-empty subsets of a 7-element universe, all %,d orders: in every case the minima agree in exactly the fraction |A and B| / |A or B| of the orders%n", pairs, perms.size());

        // ---- 2. documents and their copies -----------------------------------------------------------------------------
        String text = new String(Files.readAllBytes(Paths.get("corpus.txt")), "UTF-8").toLowerCase().replaceAll("[^a-z0-9' ]+", " ");
        List<String> all = new ArrayList<>(Arrays.asList(text.trim().split("\\s+")));
        List<String> vocab = new ArrayList<>(new TreeSet<>(all));
        List<List<String>> docs = new ArrayList<>();
        List<Integer> origin = new ArrayList<>();
        double[] rates = {0, 0.05, 0.10, 0.20, 0.40};
        int pieces = all.size() / 40;
        for (int p = 0; p < pieces; p++) {
            List<String> base = all.subList(40 * p, 40 * p + 40);
            for (double r : rates) {
                List<String> d = new ArrayList<>(base);
                for (int i = 0; i < d.size(); i++) if (next32() < r) d.set(i, vocab.get((int) (next32() * vocab.size())));
                docs.add(d); origin.add(p);
            }
        }
        int W = 4;
        long[][] sh = new long[docs.size()][];
        for (int i = 0; i < docs.size(); i++) sh[i] = shingles(docs.get(i), W);
        StringJoiner rj = new StringJoiner(" ; ");
        for (int ri = 1; ri < rates.length; ri++) {
            double s = 0; int c = 0;
            for (int p = 0; p < pieces; p++) { s += jaccard(sh[5 * p], sh[5 * p + ri]); c++; }
            rj.add(String.format("%.0f%% of words replaced: resemblance %.2f on average", 100 * rates[ri], s / c));
        }
        System.out.printf("documents: corpus.txt, %,d words, cut into %d pieces of 40 words ; each piece plus 4 copies with words replaced at random: %,d documents ; shingles of %d words ; %s%n", all.size(), pieces, docs.size(), W, rj);

        int K = 256;
        long[][] sk = new long[docs.size()][];
        for (int i = 0; i < docs.size(); i++) sk[i] = sketch(sh[i], K);
        StringJoiner ej = new StringJoiner(" ; ");
        double prevRms = Double.POSITIVE_INFINITY;
        for (int k : new int[]{16, 64, 256}) {
            double se = 0, theory = 0;
            int n = 0;
            for (int p = 0; p < pieces; p++) for (int ri = 1; ri < rates.length; ri++) {
                int a = 5 * p, b = 5 * p + ri;
                double j = jaccard(sh[a], sh[b]), e = estimate(sk[a], sk[b], k);
                se += (e - j) * (e - j); theory += j * (1 - j) / k; n++;
            }
            double rms = Math.sqrt(se / n), th = Math.sqrt(theory / n);
            check(rms < prevRms, "more hash functions, smaller error");
            check(rms > 0.7 * th && rms < 1.3 * th, "the error is about sqrt(J(1-J)/k)");
            prevRms = rms;
            ej.add(String.format("%d hash functions (%,d bytes a document): typical error %.3f (theory %.3f)", k, k * 8, rms, th));
        }
        System.out.printf("estimate: %,d pairs (each piece against its 4 copies) ; %s%n", pieces * 4, ej);

        // ---- 3. banding ---------------------------------------------------------------------------------------------
        int bands = 32, rows = 4; // 128 hash functions
        StringJoiner bj = new StringJoiner(" ; ");
        Random br = new Random(1998);
        for (double target : new double[]{0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9}) {
            int trials = 2000, cand = 0;
            int size = 200, shared = (int) Math.round(2 * size * target / (1 + target)); // |A and B| / |A or B| = target
            double jj = (double) shared / (2 * size - shared);
            for (int t = 0; t < trials; t++) {
                long[] a = new long[size], b = new long[size];
                for (int i = 0; i < size; i++) { a[i] = br.nextLong(); b[i] = i < shared ? a[i] : br.nextLong(); }
                long[] sa = sketch(a, bands * rows), sb = sketch(b, bands * rows);
                boolean hit = false;
                for (int band = 0; band < bands && !hit; band++) {
                    boolean all4 = true;
                    for (int r = 0; r < rows; r++) if (sa[band * rows + r] != sb[band * rows + r]) { all4 = false; break; }
                    hit = all4;
                }
                if (hit) cand++;
            }
            double theory = 1 - Math.pow(1 - Math.pow(jj, rows), bands), got = (double) cand / trials;
            check(Math.abs(got - theory) < 0.04, "candidate rate follows 1 - (1 - J^r)^b");
            bj.add(String.format("%.2f:%.3f:%.3f", jj, got, theory));
        }
        System.out.printf("bands: %d bands of %d rows (128 hash functions) ; 2,000 pairs of 200-element sets at each resemblance ; resemblance:candidate rate:theory 1 - (1 - J^4)^32 ; %s%n", bands, rows, bj);

        // ---- 4. all similar pairs: every pair against LSH ------------------------------------------------------------
        int D = docs.size();
        long compared = 0;
        Set<Long> truePairs = new HashSet<>();
        for (int a = 0; a < D; a++) for (int b = a + 1; b < D; b++) { compared++; if (jaccard(sh[a], sh[b]) >= 0.5) truePairs.add((long) a * D + b); }
        Map<String, List<Integer>> buckets = new HashMap<>();
        for (int d = 0; d < D; d++) for (int band = 0; band < bands; band++) {
            StringBuilder key = new StringBuilder().append(band);
            for (int r = 0; r < rows; r++) key.append(',').append(sk[d][band * rows + r]);
            buckets.computeIfAbsent(key.toString(), x -> new ArrayList<>()).add(d);
        }
        Set<Long> candidates = new HashSet<>();
        for (List<Integer> bucket : buckets.values()) for (int i = 0; i < bucket.size(); i++) for (int j = i + 1; j < bucket.size(); j++) {
            int a = Math.min(bucket.get(i), bucket.get(j)), b = Math.max(bucket.get(i), bucket.get(j));
            candidates.add((long) a * D + b);
        }
        int found = 0, falseCand = 0;
        for (long c : candidates) { if (truePairs.contains(c)) found++; else falseCand++; }
        for (long t : truePairs) check(origin.get((int) (t / D)).equals(origin.get((int) (t % D))), "every similar pair comes from the same piece");
        check(found >= 0.95 * truePairs.size(), "LSH finds at least 95% of the similar pairs");
        System.out.printf("search: %,d documents ; comparing every pair: %,d comparisons, %,d pairs with resemblance at least 0.5 ; LSH with the first 128 of the 256 hash functions: %,d candidate pairs to check, finding %,d of them (%.1f%%), %,d candidates below 0.5%n",
                D, compared, truePairs.size(), candidates.size(), found, 100.0 * found / truePairs.size(), falseCand);

        // ---- 5. the widget ---------------------------------------------------------------------------------------------
        String A = "a search engine that has fetched thirty million pages finds that many of them are copies or near copies of each other";
        String B = "a search engine that has fetched forty million pages finds that most of them are copies or near copies of one another";
        int[] sa = widgetShingles(A), sb = widgetShingles(B);
        Set<Integer> setA = new TreeSet<>(), setB = new TreeSet<>();
        for (int x : sa) setA.add(x);
        for (int x : sb) setB.add(x);
        Set<Integer> inter = new TreeSet<>(setA); inter.retainAll(setB);
        Set<Integer> union = new TreeSet<>(setA); union.addAll(setB);
        int agree = 0;
        StringJoiner aj = new StringJoiner("");
        for (int i = 0; i < 32; i++) {
            long ma = Long.MAX_VALUE, mb = Long.MAX_VALUE;
            for (int x : setA) ma = Math.min(ma, widgetHash(x, i));
            for (int x : setB) mb = Math.min(mb, widgetHash(x, i));
            if (ma == mb) agree++;
            aj.add(ma == mb ? "1" : "0");
        }
        System.out.printf("widget: shingles of 2 words, each hashed with 32-bit FNV-1a over its text ; hash function i (0 to 31) is MurmurHash3's finalizer of (shingle hash XOR (i + 1) * 0x9e3779b9) ; A: \"%s\" ; B: \"%s\" ; %d and %d shingles, %d shared, resemblance %d/%d = %.3f ; minima agree for %d of 32 hash functions (estimate %.3f) ; agreement by function: %s%n",
                A, B, setA.size(), setB.size(), inter.size(), inter.size(), union.size(), (double) inter.size() / union.size(), agree, agree / 32.0, aj);

        System.out.println("MinHashLsh: " + passed + " checks passed");
    }

    static int fnv1a(String s) {
        int h = 0x811c9dc5;
        for (char c : s.toCharArray()) { h ^= c; h *= 16777619; }
        return h;
    }

    static int fmix32(int h) { h ^= h >>> 16; h *= 0x85ebca6b; h ^= h >>> 13; h *= 0xc2b2ae35; h ^= h >>> 16; return h; }

    static long widgetHash(int shingle, int i) { return fmix32(shingle ^ ((i + 1) * 0x9e3779b9)) & 0xffffffffL; }

    static int[] widgetShingles(String s) {
        String[] w = s.split(" ");
        int[] out = new int[w.length - 1];
        for (int i = 0; i + 1 < w.length; i++) out[i] = fnv1a(w[i] + " " + w[i + 1]);
        return out;
    }
}
