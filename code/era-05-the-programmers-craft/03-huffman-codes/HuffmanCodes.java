import java.nio.file.*;
import java.util.*;

/**
 * Era 5, topic 3: Huffman's codes (MIT, 1951; published 1952).
 *
 * HOW IT WORKS
 *   A prefix code gives each symbol a string of bits, no string the beginning of another, so a stream of bits can be
 *   cut back into symbols without separators. Common symbols should get short strings. Fano's method works from the
 *   top: sort the symbols, split them into two groups of nearly equal total probability, give one group 0 and the
 *   other 1, and split each group again. Huffman's method works from the bottom: take the two least probable symbols,
 *   make them the two branches of a new node whose probability is their sum, and repeat until one node is left. The
 *   path from the top to a symbol, 0 for one branch and 1 for the other, is its codeword. Huffman proved that no
 *   prefix code has a smaller average length for the given probabilities.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Huffman's procedure on a short phrase, merge by merge.
 *   2. The letters of corpus.txt (the field notes of Eras 1 to 3, the same text as in Era 4's Shannon program):
 *      five bits for every letter, Shannon's code, Fano's splitting and Huffman's code, against the entropy.
 *   3. The whole text encoded and decoded again with Huffman's code.
 *   4. Huffman against every possible prefix code, by exhaustive search, for 20,000 random small alphabets; and how
 *      often Fano's splitting is worse.
 *   5. The longest codeword: with Fibonacci-number frequencies Huffman's tree becomes a single long branch.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HuffmanCodes.java
 *   Expected output: expected-output.txt in this folder.
 */
public class HuffmanCodes {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static double log2(double v) { return Math.log(v) / Math.log(2); }

    // ---- Huffman's procedure ----------------------------------------------------------------------------------------
    static final class Node {
        final long w;
        final int sym, order;      // sym >= 0 for a leaf; order breaks ties: older nodes first
        final Node zero, one;
        Node(long w, int sym, int order, Node zero, Node one) { this.w = w; this.sym = sym; this.order = order; this.zero = zero; this.one = one; }
    }

    static List<String> merges;

    static Node huffman(long[] w, String[] names) {
        PriorityQueue<Node> q = new PriorityQueue<>((a, b) -> a.w != b.w ? Long.compare(a.w, b.w) : Integer.compare(a.order, b.order));
        int order = 0;
        for (int i = 0; i < w.length; i++) if (w[i] > 0) q.add(new Node(w[i], i, order++, null, null));
        merges = new ArrayList<>();
        Map<Node, String> label = new HashMap<>();
        for (Node n : q) label.put(n, names == null ? "" : names[n.sym]);
        if (q.size() == 1) return new Node(q.peek().w, -1, order, q.poll(), null);
        while (q.size() > 1) {
            Node a = q.poll(), b = q.poll(), c = new Node(a.w + b.w, -1, order++, a, b);
            if (names != null) {
                String la = label.get(a), lb = label.get(b);
                label.put(c, la + lb);
                merges.add(String.format("%s(%d) + %s(%d) = %s(%d)", la, a.w, lb, b.w, la + lb, c.w));
            }
            q.add(c);
        }
        return q.poll();
    }

    static void codes(Node n, String prefix, String[] out) {
        if (n == null) return;
        if (n.sym >= 0) { out[n.sym] = prefix.isEmpty() ? "0" : prefix; return; }
        codes(n.zero, prefix + "0", out);
        codes(n.one, prefix + "1", out);
    }

    static String[] huffmanCode(long[] w, String[] names) {
        String[] c = new String[w.length];
        codes(huffman(w, names), "", c);
        return c;
    }

    // ---- Fano's splitting --------------------------------------------------------------------------------------------
    static void fano(Integer[] order, long[] w, int lo, int hi, String prefix, String[] out) {
        if (hi - lo == 1) { out[order[lo]] = prefix.isEmpty() ? "0" : prefix; return; }
        long total = 0;
        for (int i = lo; i < hi; i++) total += w[order[i]];
        long left = 0, best = Long.MAX_VALUE;
        int cut = lo + 1;
        for (int i = lo; i < hi - 1; i++) {
            left += w[order[i]];
            long diff = Math.abs(total - 2 * left);
            if (diff < best) { best = diff; cut = i + 1; }
        }
        fano(order, w, lo, cut, prefix + "0", out);
        fano(order, w, cut, hi, prefix + "1", out);
    }

    static Integer[] byWeight(long[] w) {
        List<Integer> idx = new ArrayList<>();
        for (int i = 0; i < w.length; i++) if (w[i] > 0) idx.add(i);
        idx.sort((a, b) -> w[b] != w[a] ? Long.compare(w[b], w[a]) : a - b);
        return idx.toArray(new Integer[0]);
    }

    static String[] fanoCode(long[] w) {
        Integer[] order = byWeight(w);
        String[] c = new String[w.length];
        fano(order, w, 0, order.length, "", c);
        return c;
    }

    // ---- Shannon's code (as in Era 4) ----------------------------------------------------------------------------------
    static String[] shannonCode(long[] w) {
        long total = Arrays.stream(w).sum();
        Integer[] order = byWeight(w);
        String[] c = new String[w.length];
        double cum = 0;
        for (int i : order) {
            double p = (double) w[i] / total;
            int len = (int) Math.ceil(-log2(p) - 1e-12);
            StringBuilder bits = new StringBuilder();
            double f = cum;
            for (int k = 0; k < len; k++) { f *= 2; bits.append(f >= 1 ? '1' : '0'); if (f >= 1) f -= 1; }
            c[i] = bits.toString();
            cum += p;
        }
        return c;
    }

    static long cost(long[] w, String[] c) {
        long t = 0;
        for (int i = 0; i < w.length; i++) if (w[i] > 0) t += w[i] * c[i].length();
        return t;
    }

    static boolean prefixFree(String[] c) {
        for (int a = 0; a < c.length; a++)
            for (int b = 0; b < c.length; b++)
                if (a != b && c[a] != null && c[b] != null && c[b].startsWith(c[a])) return false;
        return true;
    }

    // ---- exhaustive search over all prefix codes ------------------------------------------------------------------------
    /** Best cost over all codeword-length lists l1 <= l2 <= ... that satisfy Kraft's inequality, longest to the rarest. */
    static long bestCost(long[] sortedDesc, int i, int minLen, double kraft, long sofar, long best) {
        if (i == sortedDesc.length) return Math.min(best, sofar);
        if (sofar >= best) return best;
        for (int len = minLen; len < sortedDesc.length; len++) {
            double k = kraft + Math.pow(2, -len);
            if (k > 1 + 1e-12) continue;
            // the rest can still fit only if each can take the longest length, n - 1
            if (k + (sortedDesc.length - i - 1) * Math.pow(2, -(sortedDesc.length - 1)) > 1 + 1e-12) continue;
            best = bestCost(sortedDesc, i + 1, len, k, sofar + sortedDesc[i] * len, best);
        }
        return best;
    }

    static long seed = 1952L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % n);
    }

    static final String ALPHA = " ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    static String show(int i) { return i == 0 ? "space" : String.valueOf(ALPHA.charAt(i)); }

    public static void main(String[] args) throws Exception {
        // ---- 1. a phrase -------------------------------------------------------------------------------------------------
        String phrase = "MISSISSIPPI RIVER";
        String letters = "";
        for (char ch : phrase.toCharArray()) if (letters.indexOf(ch) < 0) letters += ch;
        long[] pw = new long[letters.length()];
        String[] pn = new String[letters.length()];
        for (char ch : phrase.toCharArray()) pw[letters.indexOf(ch)]++;
        for (int i = 0; i < pn.length; i++) pn[i] = letters.charAt(i) == ' ' ? "_" : String.valueOf(letters.charAt(i));
        String[] pc = huffmanCode(pw, pn);
        List<String> steps = new ArrayList<>(merges);
        check(prefixFree(pc), "phrase code is prefix-free");
        StringJoiner cj = new StringJoiner(" ");
        for (int i : byWeight(pw)) cj.add(pn[i] + "=" + pc[i]);
        StringBuilder enc = new StringBuilder();
        for (char ch : phrase.toCharArray()) enc.append(pc[letters.indexOf(ch)]);
        System.out.printf("phrase: %s (%d characters, _ is the space) ; merges: %s ; code: %s ; %d bits, against %d with 3 bits each%n",
                phrase, phrase.length(), String.join(" ; ", steps), cj, enc.length(), 3 * phrase.length());
        System.out.println("bits: " + enc);

        // ---- 2. the corpus -----------------------------------------------------------------------------------------------
        String s = Files.readString(Path.of("corpus.txt")).toUpperCase().replaceAll("[^A-Z]+", " ").trim();
        long[] w = new long[27];
        for (char ch : s.toCharArray()) w[ALPHA.indexOf(ch)]++;
        double h = 0;
        for (long f : w) if (f > 0) { double p = (double) f / s.length(); h -= p * log2(p); }
        String[] hc = huffmanCode(w, null), fc = fanoCode(w), sc = shannonCode(w);
        check(prefixFree(hc) && prefixFree(fc) && prefixFree(sc), "all three codes prefix-free");
        long n = s.length(), bh = cost(w, hc), bf = cost(w, fc), bs = cost(w, sc);
        check(bh <= bf && bh <= bs, "Huffman is never worse");
        check(bh >= h * n - 1e-6 && bh < (h + 1) * n, "H <= Huffman < H + 1");
        StringJoiner hj = new StringJoiner(" ");
        Integer[] ord = byWeight(w);
        for (int r = 0; r < ord.length; r++) if (r < 6 || r >= ord.length - 2) hj.add(show(ord[r]) + " " + hc[ord[r]]);
        System.out.printf("corpus: %,d letters and spaces from the field notes of Eras 1 to 3 ; entropy H = %.3f bits per letter ; five bits each: %,d bits ; Shannon's code: %,d (%.3f per letter) ; Fano's splitting: %,d (%.3f) ; Huffman: %,d (%.3f) ; Huffman's codewords: %s%n",
                n, h, 5 * n, bs, (double) bs / n, bf, (double) bf / n, bh, (double) bh / n, hj);

        // ---- 3. encode and decode ----------------------------------------------------------------------------------------
        Node root = huffman(w, null);
        StringBuilder bits = new StringBuilder();
        for (char ch : s.toCharArray()) bits.append(hc[ALPHA.indexOf(ch)]);
        StringBuilder back = new StringBuilder();
        Node cur = root;
        for (int i = 0; i < bits.length(); i++) {
            cur = bits.charAt(i) == '0' ? cur.zero : cur.one;
            if (cur.sym >= 0) { back.append(ALPHA.charAt(cur.sym)); cur = root; }
        }
        check(back.toString().equals(s) && cur == root, "decoded text is the original");
        check(bits.length() == bh, "bit count matches");
        System.out.printf("roundtrip: the text encoded into %,d bits and decoded again, letter for letter, by walking the tree from the top: 0 left, 1 right, back to the top at each leaf%n", bits.length());

        // ---- 4. optimality ---------------------------------------------------------------------------------------------------
        int trials = 20000, fanoWorse = 0;
        long[] example = null;
        for (int t = 0; t < trials; t++) {
            int k = 2 + rnd(7);
            long[] x = new long[k];
            for (int i = 0; i < k; i++) x[i] = 1 + rnd(40);
            long[] sorted = Arrays.stream(x).boxed().sorted(Comparator.reverseOrder()).mapToLong(Long::longValue).toArray();
            long best = bestCost(sorted, 0, 1, 0, 0, Long.MAX_VALUE);
            long hcost = cost(x, huffmanCode(x, null)), fcost = cost(x, fanoCode(x));
            check(hcost == best, "Huffman equals the best of all prefix codes");
            check(fcost >= best, "nothing beats the best");
            if (fcost > best) {
                fanoWorse++;
                if (example == null || k < example.length) example = x.clone();
            }
        }
        String[] eh = huffmanCode(example, null), ef = fanoCode(example);
        StringJoiner ex = new StringJoiner(" ");
        for (long v : example) ex.add(String.valueOf(v));
        StringJoiner exh = new StringJoiner(" "), exf = new StringJoiner(" ");
        for (int i = 0; i < example.length; i++) { exh.add(eh[i]); exf.add(ef[i]); }
        System.out.printf("optimal: %,d random alphabets of 2 to 8 symbols ; Huffman's total length equalled the best over all prefix codes (exhaustive search) every time ; Fano's splitting was worse in %,d of them (%.1f%%) ; smallest such case, counts %s: Fano %s = %d bits, Huffman %s = %d bits%n",
                trials, fanoWorse, 100.0 * fanoWorse / trials, ex, exf, cost(example, ef), exh, cost(example, eh));

        // ---- 5. the longest codeword ------------------------------------------------------------------------------------------
        long[] fib = new long[20];
        fib[0] = 1;
        fib[1] = 1;
        for (int i = 2; i < fib.length; i++) fib[i] = fib[i - 1] + fib[i - 2];
        String[] fcode = huffmanCode(fib, null);
        int longest = 0;
        for (String c : fcode) longest = Math.max(longest, c.length());
        check(longest == fib.length - 1, "Fibonacci counts give the longest possible codeword");
        System.out.printf("fibonacci: counts 1, 1, 2, 3, 5, ... %d for 20 symbols: each merge joins the newest node with the next count, the tree is one long branch, and the rarest symbols get %d-bit codewords, the most any 20-symbol code can need%n",
                fib[19], longest);

        System.out.println("HuffmanCodes: " + passed + " checks passed");
    }
}
