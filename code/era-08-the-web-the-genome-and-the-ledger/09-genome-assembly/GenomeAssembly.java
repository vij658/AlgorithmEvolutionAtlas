import java.util.*;

/**
 * Era 8, topic 9: Genome assembly with de Bruijn graphs (Idury and Waterman, 1995; Pevzner, Tang and Waterman, 2001).
 *
 * HOW IT WORKS
 *   A sequencer reads only short pieces ("reads") of a long genome, from many copies cut at random places. Cut every
 *   read into all its words of k letters (k-mers). Make a graph whose points are the words of k - 1 letters and draw
 *   one arrow for each k-mer, from its first k - 1 letters to its last k - 1 letters. Walking the genome from end to
 *   end crosses every arrow once, so the genome is a path that uses every arrow exactly once: an Eulerian path.
 *   Euler (Era 3) showed when such a path exists (every point has as many arrows in as out, except the two ends),
 *   and Hierholzer's method finds one in time proportional to the number of arrows. The older approach, one point per
 *   read and a link for each overlap, needs a path that visits every point once, a Hamiltonian path, for which no
 *   fast method is known.
 *   What goes wrong: a stretch the reads missed breaks the path into pieces ("contigs"); a repeat longer than k makes
 *   points where the path can go more than one way, so several genomes fit the reads; a misread letter adds k false
 *   words, but each false word is seen only once or twice while true words are seen many times, so rare words can be
 *   thrown away first.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A random genome of 20,000 letters, 6,000 error-free reads of 100 letters (two of them at the genome's two ends,
 *      the rest at random places): the graph for k = 31, Euler's degree rule, and the genome rebuilt exactly by
 *      Hierholzer's method.
 *   2. Lower coverage: how many contigs when the reads leave gaps.
 *   3. A repeat: the same 300 letters at three places; how many different genomes fit, and which.
 *   4. Reads with 1% misread letters: the k-mer counts, the threshold, and the contigs before and after it.
 *   5. A 32-letter genome for the book's widget, for k = 3 to 8: how many genomes fit its words.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java GenomeAssembly.java
 *   Expected output: expected-output.txt in this folder.
 */
public class GenomeAssembly {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static int s32 = 2001;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    static String randomDna(int n) {
        StringBuilder b = new StringBuilder(n);
        for (int i = 0; i < n; i++) b.append("ACGT".charAt((int) (next32() * 4)));
        return b.toString();
    }

    /** Reads at random places (java.util.SplittableRandom: the 32-bit generator above is too regular for this). */
    static List<String> reads(String g, int len, int count, double errorRate, long seed) {
        SplittableRandom rnd = new SplittableRandom(seed);
        List<String> r = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            int start = i == 0 ? 0 : i == 1 ? g.length() - len : rnd.nextInt(g.length() - len + 1); // the first two reads cover the two ends
            char[] c = g.substring(start, start + len).toCharArray();
            for (int j = 0; j < len; j++) if (rnd.nextDouble() < errorRate) { char old = c[j]; do c[j] = "ACGT".charAt(rnd.nextInt(4)); while (c[j] == old); }
            r.add(new String(c));
        }
        return r;
    }

    /** k-mer counts over all reads. */
    static Map<String, Integer> kmers(List<String> reads, int k) {
        Map<String, Integer> m = new HashMap<>();
        for (String r : reads) for (int i = 0; i + k <= r.length(); i++) m.merge(r.substring(i, i + k), 1, Integer::sum);
        return m;
    }

    /** The de Bruijn graph: (k-1)-mer -> list of next (k-1)-mers, one arrow per k-mer (times its multiplicity). */
    static Map<String, List<String>> graph(Map<String, Integer> kmerMult) {
        Map<String, List<String>> g = new TreeMap<>();
        for (Map.Entry<String, Integer> e : new TreeMap<>(kmerMult).entrySet()) {
            String km = e.getKey();
            String a = km.substring(0, km.length() - 1), b = km.substring(1);
            for (int t = 0; t < e.getValue(); t++) g.computeIfAbsent(a, x -> new ArrayList<>()).add(b);
            g.computeIfAbsent(b, x -> new ArrayList<>());
        }
        return g;
    }

    static Map<String, Integer> inDegrees(Map<String, List<String>> g) {
        Map<String, Integer> in = new HashMap<>();
        for (String v : g.keySet()) in.putIfAbsent(v, 0);
        for (List<String> outs : g.values()) for (String w : outs) in.merge(w, 1, Integer::sum);
        return in;
    }

    /** Hierholzer's method for an Eulerian path, spelled as a string. */
    static String euler(Map<String, List<String>> g) {
        Map<String, Integer> in = inDegrees(g);
        String start = null;
        for (String v : g.keySet()) if (g.get(v).size() == in.get(v) + 1) start = v;
        if (start == null) start = g.keySet().iterator().next();
        Map<String, Deque<String>> rest = new HashMap<>();
        for (Map.Entry<String, List<String>> e : g.entrySet()) rest.put(e.getKey(), new ArrayDeque<>(e.getValue()));
        Deque<String> stack = new ArrayDeque<>();
        List<String> path = new ArrayList<>();
        stack.push(start);
        while (!stack.isEmpty()) {
            String v = stack.peek();
            Deque<String> outs = rest.get(v);
            if (outs != null && !outs.isEmpty()) stack.push(outs.poll()); else path.add(stack.pop());
        }
        Collections.reverse(path);
        StringBuilder b = new StringBuilder(path.get(0));
        for (int i = 1; i < path.size(); i++) b.append(path.get(i).charAt(path.get(i).length() - 1));
        return b.toString();
    }

    /** Contigs: maximal paths whose inner points have exactly one arrow in and one out. */
    static List<String> contigs(Map<String, List<String>> g) {
        Map<String, Integer> in = inDegrees(g);
        List<String> out = new ArrayList<>();
        Set<String> usedEdges = new HashSet<>();
        for (String v : g.keySet()) {
            boolean oneInOneOut = in.get(v) == 1 && g.get(v).size() == 1;
            if (oneInOneOut) continue;
            for (String w : g.get(v)) {
                StringBuilder b = new StringBuilder(v).append(w.charAt(w.length() - 1));
                usedEdges.add(v + ">" + w);
                String cur = w;
                while (in.get(cur) == 1 && g.get(cur).size() == 1) {
                    String nx = g.get(cur).get(0);
                    usedEdges.add(cur + ">" + nx);
                    b.append(nx.charAt(nx.length() - 1));
                    cur = nx;
                }
                out.add(b.toString());
            }
        }
        return out;
    }

    /** Every distinct string spelled by an Eulerian path (exhaustive; for small graphs). */
    static Set<String> allEulerian(Map<String, List<String>> g, String start, int limit) {
        Map<String, Map<String, Integer>> mult = new TreeMap<>();
        int edges = 0;
        for (Map.Entry<String, List<String>> e : g.entrySet()) for (String w : e.getValue()) { mult.computeIfAbsent(e.getKey(), x -> new TreeMap<>()).merge(w, 1, Integer::sum); edges++; }
        Set<String> found = new TreeSet<>();
        final int e0 = edges;
        Thread t = new Thread(null, () -> walk(start, new StringBuilder(start), mult, e0, found, limit), "walk", 1L << 28); // deep paths need a deep stack
        t.start();
        try { t.join(); } catch (InterruptedException ex) { throw new RuntimeException(ex); }
        return found;
    }

    static void walk(String v, StringBuilder spelled, Map<String, Map<String, Integer>> mult, int left, Set<String> found, int limit) {
        if (found.size() >= limit) return;
        if (left == 0) { found.add(spelled.toString()); return; }
        Map<String, Integer> outs = mult.get(v);
        if (outs == null) return;
        for (Map.Entry<String, Integer> e : outs.entrySet()) if (e.getValue() > 0) {
            e.setValue(e.getValue() - 1);
            spelled.append(e.getKey().charAt(e.getKey().length() - 1));
            walk(e.getKey(), spelled, mult, left - 1, found, limit);
            spelled.setLength(spelled.length() - 1);
            e.setValue(e.getValue() + 1);
        }
    }

    static String startNode(Map<String, List<String>> g) {
        Map<String, Integer> in = inDegrees(g);
        for (String v : g.keySet()) if (g.get(v).size() == in.get(v) + 1) return v;
        return g.keySet().iterator().next();
    }

    /** k-mer multiplicities as they occur in the genome itself (what perfect coverage would reveal). */
    static Map<String, Integer> genomeKmers(String g, int k) {
        Map<String, Integer> m = new HashMap<>();
        for (int i = 0; i + k <= g.length(); i++) m.merge(g.substring(i, i + k), 1, Integer::sum);
        return m;
    }

    public static void main(String[] args) {
        int k = 31;
        // ---- 1. error-free reads, full coverage --------------------------------------------------------------------------
        String genome = randomDna(20_000);
        List<String> rd = reads(genome, 100, 6000, 0, 2001);
        Map<String, Integer> km = kmers(rd, k);
        Map<String, Integer> distinct = new HashMap<>();
        for (String s : km.keySet()) distinct.put(s, 1);
        Map<String, List<String>> g = graph(distinct);
        Map<String, Integer> in = inDegrees(g);
        int starts = 0, ends = 0, balanced = 0;
        for (String v : g.keySet()) {
            int d = g.get(v).size() - in.get(v);
            if (d == 1) starts++; else if (d == -1) ends++; else { check(d == 0, "Euler's rule: arrows in = arrows out"); balanced++; }
        }
        check(starts == 1 && ends == 1, "exactly one start and one end");
        check(distinct.size() == genome.length() - k + 1, "every one of the genome's 31-mers was read");
        String rebuilt = euler(g);
        check(rebuilt.equals(genome), "the Eulerian path spells the genome");
        long overlapPairs = (long) rd.size() * (rd.size() - 1) / 2;
        System.out.printf("exact: random genome of %,d letters ; %,d reads of 100 letters (coverage %.0f) ; k = %d: %,d distinct %d-mers = arrows, %,d points ; Euler's rule: %,d balanced points, 1 start, 1 end ; Hierholzer's path spells the genome exactly ; an overlap graph would compare %,d pairs of reads%n",
                genome.length(), rd.size(), 6000 * 100.0 / genome.length(), k, distinct.size(), k, g.size(), balanced, overlapPairs);

        // ---- 2. coverage ------------------------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        int prevContigs = Integer.MAX_VALUE;
        for (int cov : new int[]{1, 2, 3, 5, 8, 12}) {
            List<String> r = reads(genome, 100, cov * genome.length() / 100, 0, 100 + cov);
            Map<String, Integer> d = new HashMap<>();
            for (String s : kmers(r, k).keySet()) d.put(s, 1);
            List<String> cs = contigs(graph(d));
            int longest = 0;
            for (String c : cs) { longest = Math.max(longest, c.length()); check(genome.contains(c), "every contig is a true piece of the genome"); }
            cj.add(String.format("coverage %d: %d contig%s, longest %,d letters, %.1f%% of the 31-mers read", cov, cs.size(), cs.size() == 1 ? "" : "s", longest, 100.0 * d.size() / (genome.length() - k + 1)));
            prevContigs = cs.size();
        }
        check(prevContigs == 1, "at coverage 12 the genome is one contig");
        System.out.printf("coverage: the same genome, fewer reads ; %s%n", cj);

        // ---- 3. a repeat ------------------------------------------------------------------------------------------------
        s32 = 300;
        String rep = randomDna(300);
        String x = randomDna(2000), y = randomDna(2000), z = randomDna(2000), w = randomDna(2000);
        String withRepeat = x + rep + y + rep + z + rep + w;
        Map<String, List<String>> gr = graph(genomeKmers(withRepeat, k));
        Map<String, Integer> once = new HashMap<>();
        for (String s0 : genomeKmers(withRepeat, k).keySet()) once.put(s0, 1);
        List<String> rc = contigs(graph(once));
        check(rc.contains(rep), "one contig is the repeat itself, stored once");
        for (String c0 : rc) check(withRepeat.contains(c0), "every contig is a true piece");
        Set<String> fits = allEulerian(gr, startNode(gr), 100);
        String swapped = x + rep + z + rep + y + rep + w;
        check(fits.size() == 2 && fits.contains(withRepeat) && fits.contains(swapped), "exactly two genomes fit: the true one and the one with Y and Z swapped");
        System.out.printf("repeat: genome X R Y R Z R W, each piece 2,000 letters, R the same 300 letters three times (%,d letters) ; k = 31, every k-mer with its true count ; %d contigs, one of them R itself, stored once ; genomes that fit the words exactly: %d, the true one and X R Z R Y R W ; with reads of 100 letters no method can tell which%n", withRepeat.length(), rc.size(), fits.size());

        // ---- 4. misread letters -----------------------------------------------------------------------------------------
        List<String> noisy = reads(genome, 100, 6000, 0.01, 404);
        Map<String, Integer> nk = kmers(noisy, k);
        Set<String> truth = genomeKmers(genome, k).keySet();
        int trueSeen = 0, falseSeen = 0, trueKept = 0, falseKept = 0, threshold = 5;
        int[] trueHist = new int[6], falseHist = new int[6];
        for (Map.Entry<String, Integer> e : nk.entrySet()) {
            boolean t = truth.contains(e.getKey());
            int c = Math.min(e.getValue(), 5);
            if (t) { trueSeen++; trueHist[c]++; if (e.getValue() >= threshold) trueKept++; }
            else { falseSeen++; falseHist[c]++; if (e.getValue() >= threshold) falseKept++; }
        }
        Map<String, Integer> solid = new HashMap<>();
        for (Map.Entry<String, Integer> e : nk.entrySet()) if (e.getValue() >= threshold) solid.put(e.getKey(), 1);
        List<String> sc = contigs(graph(solid));
        int longest = 0;
        int trueContigs = 0;
        for (String c : sc) { if (genome.contains(c)) trueContigs++; longest = Math.max(longest, c.length()); }
        check(trueContigs == sc.size(), "every contig from the solid words is a true piece of the genome");
        check(falseKept == 0, "no false word survives the threshold");
        Map<String, Integer> rawOnce = new HashMap<>();
        for (String s0 : nk.keySet()) rawOnce.put(s0, 1);
        int rawContigs = contigs(graph(rawOnce)).size();
        System.out.printf("errors: the same 6,000 reads with 1%% of letters misread ; %,d different 31-mers seen: %,d true, %,d false ; seen once, twice, 3, 4, 5+ times: true %d %d %d %d %d, false %,d %,d %d %d %d ; using every word: %,d contigs ; keeping words seen at least %d times keeps %,d of %,d true words and %d false ones: %d contig%s, the longest %,d letters, every one a true piece of the genome%n",
                nk.size(), trueSeen, falseSeen, trueHist[1], trueHist[2], trueHist[3], trueHist[4], trueHist[5], falseHist[1], falseHist[2], falseHist[3], falseHist[4], falseHist[5], rawContigs, threshold, trueKept, truth.size(), falseKept, sc.size(), sc.size() == 1 ? "" : "s", longest);

        // ---- 5. the widget's genome ---------------------------------------------------------------------------------------
        s32 = 1736;
        String small = randomDna(32);
        StringJoiner wj = new StringJoiner(" ; ");
        for (int kk = 3; kk <= 8; kk++) {
            Map<String, List<String>> gw = graph(genomeKmers(small, kk));
            Set<String> f = allEulerian(gw, startNode(gw), 100000);
            check(f.size() < 100000 && f.contains(small), "the enumeration is complete and the true genome always fits");
            wj.add(String.format("k = %d: %d points, %d arrows, %s", kk, gw.size(), small.length() - kk + 1, f.size() == 1 ? "1 genome fits" : String.format("%,d genomes fit", f.size())));
        }
        System.out.printf("widget: genome %s (32 letters from the generator, seed 1736) ; every k-mer of the genome with its count ; %s%n", small, wj);

        System.out.println("GenomeAssembly: " + passed + " checks passed");
    }
}
