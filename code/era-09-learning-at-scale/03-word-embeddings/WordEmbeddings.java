import java.util.*;

/**
 * Era 9, topic 3: Word embeddings (word2vec: Mikolov, Chen, Corrado and Dean, Google, January 2013; negative sampling:
 * Mikolov, Sutskever, Chen, Corrado and Dean, October 2013).
 *
 * HOW IT WORKS
 *   Give every word two vectors of d numbers: one for when it is the centre word (v) and one for when it is a
 *   neighbour (u). The skip-gram model asks the centre word to predict the words around it. The full model would
 *   compute a softmax over the whole vocabulary for every pair, which is slow; negative sampling replaces it by a
 *   simpler question: for a real pair (centre w, neighbour c), push sigma(v_w . u_c) towards 1, and for k random
 *   "noise" words n, push sigma(v_w . u_n) towards 0. The noise words are drawn in proportion to (count)^(3/4).
 *   Very frequent words ("the", "is") are thrown away at random, in proportion to how frequent they are.
 *   Nothing tells the model what a word means; words that appear in similar company end up with similar vectors,
 *   and consistent differences in company become consistent directions: v(paris) - v(france) is nearly the same
 *   vector as v(rome) - v(italy), so v(paris) - v(france) + v(italy) lands near v(rome).
 *
 * WHAT THIS PROGRAM DOES
 *   1. Writes a small corpus from sentence patterns about 8 countries, their capitals and languages, and 6 pairs of
 *      words that differ by gender (king and queen, ...). The patterns are known, so the program can check what the
 *      vectors learn; real word2vec learns from billions of words of ordinary text.
 *   2. Checks the gradient of the negative-sampling loss against finite differences.
 *   3. Trains skip-gram with negative sampling (d = 32, window 3, k = 5) and reports nearest neighbours.
 *   4. Analogy tests "a is to b as c is to ?", answered by the word nearest to v(b) - v(a) + v(c): every
 *      country-capital, country-language and male-female combination, against random vectors.
 *   5. The cost of a full softmax against negative sampling, per training pair.
 *   6. Prints the vectors of the 42 content words and a two-dimensional view (principal components) for the widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java WordEmbeddings.java
 *   Expected output: expected-output.txt in this folder.
 */
public class WordEmbeddings {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final String[] COUNTRY = {"france", "italy", "spain", "germany", "japan", "egypt", "peru", "kenya"};
    static final String[] CAPITAL = {"paris", "rome", "madrid", "berlin", "tokyo", "cairo", "lima", "nairobi"};
    static final String[] LANG = {"french", "italian", "spanish", "german", "japanese", "arabic", "quechua", "swahili"};
    static final String[] MALE = {"king", "man", "boy", "brother", "father", "prince"};
    static final String[] FEMALE = {"queen", "woman", "girl", "sister", "mother", "princess"};
    static final String[] ROLE = {"crown", "adult", "school", "sibling", "parent", "palace"};

    static List<String> vocab = new ArrayList<>();
    static Map<String, Integer> id = new HashMap<>();
    static int[] count;

    static int word(String w) {
        Integer i = id.get(w);
        if (i == null) { i = vocab.size(); vocab.add(w); id.put(w, i); }
        return i;
    }

    /** The corpus: sentence patterns filled in at random. */
    static int[] corpus(Random r, int sentences) {
        List<Integer> out = new ArrayList<>();
        for (int s = 0; s < sentences; s++) {
            String sent;
            int c = r.nextInt(8), g = r.nextInt(6);
            boolean female = r.nextBoolean();
            String w = female ? FEMALE[g] : MALE[g], he = female ? "she" : "he", his = female ? "her" : "his";
            switch (r.nextInt(8)) {
                case 0 -> sent = CAPITAL[c] + " is the capital of " + COUNTRY[c];
                case 1 -> sent = "in " + CAPITAL[c] + " they speak " + LANG[c];
                case 2 -> sent = "people of " + COUNTRY[c] + " speak " + LANG[c];
                case 3 -> sent = CAPITAL[c] + " is a city";
                case 4 -> sent = COUNTRY[c] + " is a nation";
                case 5 -> sent = "the " + w + " said " + he + " likes " + his + " " + ROLE[g];
                case 6 -> sent = he + " is the " + w + " of the " + ROLE[g];
                default -> sent = "a " + ROLE[g] + " and " + his + " " + w;
            }
            for (String t : sent.split(" ")) out.add(word(t));
        }
        return out.stream().mapToInt(Integer::intValue).toArray();
    }

    static int D = 32;
    static double[][] vIn, uOut;

    static double sigma(double x) { return 1 / (1 + Math.exp(-x)); }

    static double dot(double[] a, double[] b) { double s = 0; for (int i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }

    /** The negative-sampling loss for one pair (w, c) with noise words neg[]: -log s(v.u_c) - sum log s(-v.u_n). */
    static double pairLoss(int w, int c, int[] neg) {
        double L = -Math.log(sigma(dot(vIn[w], uOut[c])));
        for (int n : neg) L -= Math.log(sigma(-dot(vIn[w], uOut[n])));
        return L;
    }

    /** One SGD step on the pair (w, c); returns the gradient with respect to vIn[w] (for the gradient check). */
    static double[] pairStep(int w, int c, int[] neg, double lr) {
        double[] gv = new double[D];
        int[] all = new int[neg.length + 1];
        all[0] = c;
        System.arraycopy(neg, 0, all, 1, neg.length);
        for (int t = 0; t < all.length; t++) {
            int o = all[t];
            double label = t == 0 ? 1 : 0;
            double g = sigma(dot(vIn[w], uOut[o])) - label; // d loss / d (v . u_o)
            for (int i = 0; i < D; i++) { gv[i] += g * uOut[o][i]; uOut[o][i] -= lr * g * vIn[w][i]; }
        }
        for (int i = 0; i < D; i++) vIn[w][i] -= lr * gv[i];
        return gv;
    }

    static double cos(double[] a, double[] b) { return dot(a, b) / Math.sqrt(dot(a, a) * dot(b, b)); }

    static String nearest(double[][] vec, double[] q, Set<Integer> skip, Set<Integer> allowed) {
        int best = -1; double bs = -2;
        for (int i : allowed) if (!skip.contains(i)) { double s = cos(vec[i], q); if (s > bs) { bs = s; best = i; } }
        return vocab.get(best);
    }

    static int[] ana(double[][] vec, String[] A, String[] B, Set<Integer> allowed) {
        int right = 0, total = 0;
        for (int i = 0; i < A.length; i++) for (int j = 0; j < A.length; j++) {
            if (i == j) continue;
            double[] q = new double[D];
            int a = id.get(A[i]), b = id.get(B[i]), c = id.get(A[j]);
            for (int k = 0; k < D; k++) q[k] = vec[b][k] - vec[a][k] + vec[c][k];
            String got = nearest(vec, q, Set.of(a, b, c), allowed);
            if (got.equals(B[j])) right++;
            total++;
        }
        return new int[]{right, total};
    }

    public static void main(String[] args) {
        Random r = new Random(2013);
        int[] text = corpus(r, 30_000);
        int V = vocab.size();
        count = new int[V];
        for (int t : text) count[t]++;
        System.out.printf("corpus: %,d sentences, %,d words, vocabulary of %d ; 8 countries with capitals and languages, 6 male-female pairs with a shared context word each ; most frequent: %s%n",
                30_000, text.length, V, topWords(5));

        // the noise distribution: count^(3/4)
        double[] noise = new double[V];
        double z = 0;
        for (int i = 0; i < V; i++) { noise[i] = Math.pow(count[i], 0.75); z += noise[i]; }
        double[] cum = new double[V];
        double acc = 0;
        for (int i = 0; i < V; i++) { acc += noise[i] / z; cum[i] = acc; }
        int theId = id.get("the");
        double plain = (double) count[theId] / text.length, damped = noise[theId] / z;
        check(damped < plain, "raising counts to the 3/4 power lowers the share of the most frequent word");

        // subsampling of frequent words: keep with probability sqrt(t / f) (t = 0.01 for a corpus this small)
        double tSub = 0.01;
        double[] keep = new double[V];
        for (int i = 0; i < V; i++) keep[i] = Math.min(1, Math.sqrt(tSub / ((double) count[i] / text.length)));

        // ---- 2. gradient check ------------------------------------------------------------------------------------------
        Random init = new Random(7);
        vIn = new double[V][D]; uOut = new double[V][D];
        for (int i = 0; i < V; i++) for (int k = 0; k < D; k++) { vIn[i][k] = (init.nextDouble() - 0.5) / D; uOut[i][k] = 0.3 * init.nextGaussian(); }
        int gw = id.get("paris"), gc = id.get("capital");
        int[] gneg = {id.get("king"), id.get("the"), id.get("swahili")};
        double[][] saveV = deep(vIn), saveU = deep(uOut);
        double[] g = pairStep(gw, gc, gneg, 0); // lr 0: only compute the gradient
        double worst = 0, h = 1e-6;
        for (int k = 0; k < D; k++) {
            double o = vIn[gw][k];
            vIn[gw][k] = o + h; double lp = pairLoss(gw, gc, gneg);
            vIn[gw][k] = o - h; double lm = pairLoss(gw, gc, gneg);
            vIn[gw][k] = o;
            worst = Math.max(worst, Math.abs((lp - lm) / (2 * h) - g[k]));
        }
        check(worst < 1e-8, "the negative-sampling gradient agrees with finite differences");
        vIn = saveV; uOut = saveU;
        // start the output vectors at zero, as word2vec does
        for (double[] row : uOut) Arrays.fill(row, 0);

        // ---- 3. training ------------------------------------------------------------------------------------------------------
        final int WINDOW = 3, KNEG = 5, EPOCHS = 5;
        double lr0 = 0.025;
        long pairs = 0, dropped = 0;
        Random tr = new Random(11);
        int totalSteps = EPOCHS * text.length, step = 0;
        for (int e = 0; e < EPOCHS; e++) {
            for (int pos = 0; pos < text.length; pos++, step++) {
                int w = text[pos];
                if (tr.nextDouble() > keep[w]) { dropped++; continue; }
                double lr = Math.max(lr0 * 1e-3, lr0 * (1 - (double) step / totalSteps));
                int b = 1 + tr.nextInt(WINDOW); // word2vec's random window shrink
                for (int o = pos - b; o <= pos + b; o++) {
                    if (o < 0 || o >= text.length || o == pos) continue;
                    int[] neg = new int[KNEG];
                    for (int k = 0; k < KNEG; k++) {
                        int n;
                        do { double u = tr.nextDouble(); int lo = 0, hi = V - 1; while (lo < hi) { int mid = (lo + hi) / 2; if (cum[mid] < u) lo = mid + 1; else hi = mid; } n = lo; } while (n == text[o]);
                        neg[k] = n;
                    }
                    pairStep(w, text[o], neg, lr);
                    pairs++;
                }
            }
        }
        System.out.printf("train: skip-gram with negative sampling, d = %d, window %d, k = %d noise words from count^(3/4), %d passes ; gradient check: largest difference %.1e ; frequent words subsampled: %,d of %,d occurrences skipped ; %,d (centre, neighbour) pairs ; share of noise draws for \"the\": %.3f instead of %.3f%n",
                D, WINDOW, KNEG, EPOCHS, worst, dropped, (long) EPOCHS * text.length, pairs, damped, plain);

        // ---- nearest neighbours ------------------------------------------------------------------------------------------
        Set<Integer> content = new LinkedHashSet<>();
        for (String[] arr : new String[][]{COUNTRY, CAPITAL, LANG, MALE, FEMALE, ROLE}) for (String s : arr) content.add(id.get(s));
        StringJoiner nj = new StringJoiner(" ; ");
        for (String q : new String[]{"paris", "france", "king", "sister", "swahili"}) {
            int qi = id.get(q);
            List<Integer> others = new ArrayList<>(content);
            others.remove(Integer.valueOf(qi));
            others.sort((a, b) -> Double.compare(cos(vIn[b], vIn[qi]), cos(vIn[a], vIn[qi])));
            nj.add(String.format("%s: %s %.2f, %s %.2f, %s %.2f", q, vocab.get(others.get(0)), cos(vIn[others.get(0)], vIn[qi]),
                    vocab.get(others.get(1)), cos(vIn[others.get(1)], vIn[qi]), vocab.get(others.get(2)), cos(vIn[others.get(2)], vIn[qi])));
        }
        System.out.printf("near: nearest of the %d content words by cosine ; %s%n", content.size(), nj);

        // ---- 4. analogies ----------------------------------------------------------------------------------------------------
        int[] a1 = ana(vIn, COUNTRY, CAPITAL, content), a2 = ana(vIn, COUNTRY, LANG, content), a3 = ana(vIn, MALE, FEMALE, content);
        double[][] rnd = new double[V][D];
        Random rr = new Random(3);
        for (double[] row : rnd) for (int k = 0; k < D; k++) row[k] = rr.nextGaussian();
        int[] b1 = ana(rnd, COUNTRY, CAPITAL, content), b2 = ana(rnd, COUNTRY, LANG, content), b3 = ana(rnd, MALE, FEMALE, content);
        int right = a1[0] + a2[0] + a3[0], total = a1[1] + a2[1] + a3[1], rRight = b1[0] + b2[0] + b3[0];
        check(a1[0] >= 50 && a3[0] >= 27, "country-capital and male-female analogies are mostly answered correctly");
        check(right >= 4 * rRight, "far better than random vectors");
        check(rRight <= 0.1 * total, "random vectors answer almost none");
        int pi = id.get("paris"), fr = id.get("france"), it = id.get("italy");
        double[] q = new double[D];
        for (int k = 0; k < D; k++) q[k] = vIn[pi][k] - vIn[fr][k] + vIn[it][k];
        String rome = nearest(vIn, q, Set.of(pi, fr, it), content);
        check(rome.equals("rome"), "paris - france + italy = rome");
        int ki = id.get("king"), ma = id.get("man"), wo = id.get("woman");
        double[] q2 = new double[D];
        for (int k = 0; k < D; k++) q2[k] = vIn[ki][k] - vIn[ma][k] + vIn[wo][k];
        String queen = nearest(vIn, q2, Set.of(ki, ma, wo), content);
        check(queen.equals("queen"), "king - man + woman = queen");
        System.out.printf("analogy: a is to b as c is to the nearest word to v(b) - v(a) + v(c), among the %d content words ; country:capital %d of %d ; country:language %d of %d ; male:female %d of %d ; all %d of %d (%.0f%%) ; random vectors: %d of %d ; paris - france + italy = %s ; king - man + woman = %s%n", content.size(),
                a1[0], a1[1], a2[0], a2[1], a3[0], a3[1], right, total, 100.0 * right / total, rRight, total, rome, queen);

        // ---- 5. cost ---------------------------------------------------------------------------------------------------------
        long fullOps = (long) V * D, nsOps = (long) (KNEG + 1) * D;
        System.out.printf("cost: multiply-adds per training pair: full softmax over %d words %,d ; negative sampling with k = %d: %,d ; for a vocabulary of 1,000,000 words and d = 300: %,d against %,d%n",
                V, fullOps, KNEG, nsOps, 1_000_000L * 300, (long) (KNEG + 1) * 300);

        // ---- 6. the widget ---------------------------------------------------------------------------------------------------
        List<Integer> cw = new ArrayList<>(content);
        double[][] Xc = new double[cw.size()][D];
        double[] mean = new double[D];
        for (int i = 0; i < cw.size(); i++) for (int k = 0; k < D; k++) mean[k] += vIn[cw.get(i)][k] / cw.size();
        for (int i = 0; i < cw.size(); i++) for (int k = 0; k < D; k++) Xc[i][k] = vIn[cw.get(i)][k] - mean[k];
        double[][] pcs = new double[2][];
        double[] varShare = new double[2];
        double totalVar = 0;
        for (double[] row : Xc) totalVar += dot(row, row);
        for (int c = 0; c < 2; c++) {
            double[] v = new double[D];
            Arrays.fill(v, 1);
            if (c == 1) v[0] = -1;
            for (int it2 = 0; it2 < 500; it2++) {
                double[] nv = new double[D];
                for (double[] row : Xc) { double s = dot(row, v); for (int k = 0; k < D; k++) nv[k] += s * row[k]; }
                if (c == 1) { double s = dot(nv, pcs[0]); for (int k = 0; k < D; k++) nv[k] -= s * pcs[0][k]; }
                double nn = Math.sqrt(dot(nv, nv));
                for (int k = 0; k < D; k++) v[k] = nv[k] / nn;
            }
            pcs[c] = v;
            double var = 0;
            for (double[] row : Xc) { double s = dot(row, v); var += s * s; }
            varShare[c] = var / totalVar;
        }
        StringJoiner wj = new StringJoiner(" ; ");
        for (int i = 0; i < cw.size(); i++) {
            StringJoiner one = new StringJoiner(",");
            for (int k = 0; k < D; k++) one.add(String.format("%.3f", vIn[cw.get(i)][k]));
            wj.add(String.format("%s %.3f %.3f %s", vocab.get(cw.get(i)), dot(Xc[i], pcs[0]), dot(Xc[i], pcs[1]), one));
        }
        System.out.printf("widget: %d content words, each: word x y (two principal components, %.0f%% and %.0f%% of the spread) then its 32 numbers ; %s%n", cw.size(),
                100 * varShare[0], 100 * varShare[1], wj);

        System.out.println("WordEmbeddings: " + passed + " checks passed");
    }

    static double[][] deep(double[][] a) { double[][] b = new double[a.length][]; for (int i = 0; i < a.length; i++) b[i] = a[i].clone(); return b; }

    static String topWords(int n) {
        Integer[] o = new Integer[vocab.size()];
        for (int i = 0; i < o.length; i++) o[i] = i;
        Arrays.sort(o, (a, b) -> count[b] - count[a]);
        StringJoiner j = new StringJoiner(", ");
        for (int i = 0; i < n; i++) j.add(vocab.get(o[i]) + " " + String.format("%,d", count[o[i]]));
        return j.toString();
    }
}
