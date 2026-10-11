import java.nio.file.*;
import java.util.*;

/**
 * Era 4, topic 12: Shannon's switches, bits and entropy (1937 and 1948).
 *
 * HOW IT WORKS
 *   1937: a relay contact is a Boolean variable. Two contacts in series conduct when both are closed (x AND y); in
 *   parallel, when either is (x OR y). So a network of relays is a formula of Boole's algebra, and the algebra can
 *   simplify the network before it is built.
 *   1948: a message source that emits symbol i with probability p_i produces, on average,
 *       H = - sum p_i log2 p_i   bits per symbol,
 *   its entropy. No code can use fewer bits per symbol on average, and simple codes come within one bit: give
 *   symbol i a codeword of about -log2 p_i bits. If the next symbol depends on the previous ones (a Markov source,
 *   topic 3), the entropy given the past is lower, and that is the source's redundancy. Shannon showed how close
 *   statistics alone come to English by generating text from them: random letters, then letters with English
 *   frequencies, then pairs, triples, and words.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Relay networks as Boolean formulas: a three-branch network and its five-contact simplification, compared on
 *      every input; the two-way light switch; the carry and sum of a binary adder.
 *   2. Letter statistics of a sample of this book's own text (corpus.txt, the field notes of Eras 1 to 3), with the
 *      entropy per letter given 0, 1 and 2 letters of context.
 *   3. Imitation text in the manner of Shannon's approximations, from the same statistics.
 *   4. Shannon's code from the letter frequencies: prefix-free, and its average length between H and H + 1.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java InformationTheory.java
 *   Expected output: expected-output.txt in this folder.
 */
public class InformationTheory {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- 1. relay networks --------------------------------------------------------------------------------------------
    /** A network: series (all must conduct) or parallel (any may conduct) of contacts and sub-networks. */
    interface Net { boolean conducts(boolean[] v); int contacts(); }

    record Contact(int var, boolean closedWhenOn) implements Net {
        public boolean conducts(boolean[] v) { return v[var] == closedWhenOn; }
        public int contacts() { return 1; }
    }

    record Series(Net... parts) implements Net {
        public boolean conducts(boolean[] v) { for (Net p : parts) if (!p.conducts(v)) return false; return true; }
        public int contacts() { int c = 0; for (Net p : parts) c += p.contacts(); return c; }
    }

    record Parallel(Net... parts) implements Net {
        public boolean conducts(boolean[] v) { for (Net p : parts) if (p.conducts(v)) return true; return false; }
        public int contacts() { int c = 0; for (Net p : parts) c += p.contacts(); return c; }
    }

    static Contact x(int i) { return new Contact(i, true); }
    static Contact notx(int i) { return new Contact(i, false); }

    static boolean same(Net a, Net b, int vars) {
        for (int m = 0; m < (1 << vars); m++) {
            boolean[] v = new boolean[vars];
            for (int i = 0; i < vars; i++) v[i] = (m >> i & 1) == 1;
            check(a.conducts(v) == b.conducts(v), "networks agree on input " + m);
            if (a.conducts(v) != b.conducts(v)) return false;
        }
        return true;
    }

    // ---- 2. statistics ------------------------------------------------------------------------------------------------
    static final String ALPHA = " ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    static double log2(double v) { return Math.log(v) / Math.log(2); }

    /** Entropy of the next letter given the previous k letters, from counts of (k+1)-letter strings. */
    static double conditionalEntropy(String s, int k) {
        Map<String, Integer> ctx = new HashMap<>(), full = new HashMap<>();
        for (int i = k; i < s.length(); i++) {
            ctx.merge(s.substring(i - k, i), 1, Integer::sum);
            full.merge(s.substring(i - k, i + 1), 1, Integer::sum);
        }
        double total = s.length() - k, h = 0;
        for (Map.Entry<String, Integer> e : full.entrySet()) {
            double pJoint = e.getValue() / total, pCond = (double) e.getValue() / ctx.get(e.getKey().substring(0, k));
            h -= pJoint * log2(pCond);
        }
        return h;
    }

    static long seed = 1948L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / 9007199254740992.0;
    }

    /** Draw from counts. */
    static <T> T draw(Map<T, Integer> counts, List<T> order) {
        int total = 0;
        for (T t : order) total += counts.getOrDefault(t, 0);
        double r = uniform() * total;
        for (T t : order) { r -= counts.getOrDefault(t, 0); if (r < 0) return t; }
        return order.get(order.size() - 1);
    }

    /** Text from letter statistics of order k (k = -1: uniform letters). */
    static String imitate(String s, int k, int length) {
        StringBuilder out = new StringBuilder();
        List<Character> letters = new ArrayList<>();
        for (char c : ALPHA.toCharArray()) letters.add(c);
        if (k < 0) {
            for (int i = 0; i < length; i++) out.append(ALPHA.charAt((int) (uniform() * 27)));
            return out.toString();
        }
        Map<String, Map<Character, Integer>> next = new HashMap<>();
        for (int i = k; i < s.length(); i++) next.computeIfAbsent(s.substring(i - k, i), z -> new HashMap<>()).merge(s.charAt(i), 1, Integer::sum);
        String context = s.substring(0, k);
        out.append(context);
        while (out.length() < length) {
            Map<Character, Integer> m = next.get(context);
            if (m == null) { context = s.substring(0, k); continue; }
            char c = draw(m, letters);
            out.append(c);
            context = k == 0 ? "" : out.substring(out.length() - k);
        }
        return out.toString();
    }

    static String imitateWords(List<String> words, int k, int count) {
        List<String> vocab = new ArrayList<>(new TreeSet<>(words));
        StringJoiner out = new StringJoiner(" ");
        if (k == 0) {
            Map<String, Integer> c = new HashMap<>();
            for (String w : words) c.merge(w, 1, Integer::sum);
            for (int i = 0; i < count; i++) out.add(draw(c, vocab));
            return out.toString();
        }
        Map<String, Map<String, Integer>> next = new HashMap<>();
        for (int i = 1; i < words.size(); i++) next.computeIfAbsent(words.get(i - 1), z -> new HashMap<>()).merge(words.get(i), 1, Integer::sum);
        String w = words.get(0);
        out.add(w);
        for (int i = 1; i < count; i++) {
            Map<String, Integer> m = next.get(w);
            w = m == null ? words.get(0) : draw(m, vocab);
            out.add(w);
        }
        return out.toString();
    }

    public static void main(String[] args) throws Exception {
        // ---- 1. switching circuits ---------------------------------------------------------------------------------
        // x y + x y' z + x' y z   (three branches in parallel, 2 + 3 + 3 contacts)
        Net three = new Parallel(new Series(x(0), x(1)), new Series(x(0), notx(1), x(2)), new Series(notx(0), x(1), x(2)));
        // x y + z (x + y)          (Boole's algebra: the same function, the majority of three, with 5 contacts)
        Net five = new Parallel(new Series(x(0), x(1)), new Series(x(2), new Parallel(x(0), x(1))));
        check(same(three, five, 3), "the simplified network is the same function");
        // the two-way light switch: x y' + x' y
        Net stairs = new Parallel(new Series(x(0), notx(1)), new Series(notx(0), x(1)));
        int flips = 0;
        boolean[] v = new boolean[2];
        boolean lamp = stairs.conducts(v);
        for (int k = 0; k < 8; k++) { v[k % 2] = !v[k % 2]; boolean now = stairs.conducts(v); if (now != lamp) flips++; lamp = now; }
        check(flips == 8, "either switch always changes the lamp");
        // a binary adder's carry is the majority network above; its sum is the three-way switch
        int ok = 0;
        for (int m = 0; m < 8; m++) {
            boolean[] w = {(m & 1) == 1, (m & 2) == 2, (m & 4) == 4};
            int a = w[0] ? 1 : 0, b = w[1] ? 1 : 0, c = w[2] ? 1 : 0, total = a + b + c;
            boolean sum = w[0] ^ w[1] ^ w[2];
            check(five.conducts(w) == (total >= 2) && sum == (total % 2 == 1), "adder carry and sum");
            ok++;
        }
        System.out.printf("relays: x y + x y' z + x' y z needs %d contacts ; Boole's algebra rewrites it as x y + z (x + y), %d contacts, the same on all 8 inputs ; the two-way light switch x y' + x' y changes the lamp at every flip of either switch ; the 5-contact network is the carry of a binary adder, on all %d inputs%n",
                three.contacts(), five.contacts(), ok);

        // ---- 2. statistics of a sample text ----------------------------------------------------------------------------
        String raw = Files.readString(Path.of("corpus.txt"));
        String s = raw.toUpperCase().replaceAll("[^A-Z]+", " ").trim();
        List<String> words = Arrays.asList(s.split(" "));
        int[] freq = new int[27];
        for (char c : s.toCharArray()) freq[ALPHA.indexOf(c)]++;
        double h0 = log2(27), h1 = 0;
        for (int f : freq) if (f > 0) { double p = (double) f / s.length(); h1 -= p * log2(p); }
        double h1b = conditionalEntropy(s, 0), h2 = conditionalEntropy(s, 1), h3 = conditionalEntropy(s, 2);
        check(Math.abs(h1 - h1b) < 1e-9, "two ways to the letter entropy agree");
        check(h0 > h1 && h1 > h2 && h2 > h3, "more context, less uncertainty");
        Integer[] idx = new Integer[27];
        for (int i = 0; i < 27; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> freq[b] - freq[a] != 0 ? freq[b] - freq[a] : a - b);
        StringJoiner top = new StringJoiner(" ");
        for (int i = 0; i < 8; i++) top.add((idx[i] == 0 ? "space" : String.valueOf(ALPHA.charAt(idx[i]))) + String.format(" %.3f", (double) freq[idx[i]] / s.length()));
        System.out.printf("text: %d characters of this book's field notes (letters and spaces), %d words, %d different words ; commonest: %s ; entropy per letter with no statistics log2 27 = %.3f bits, with letter frequencies %.3f, given one letter before %.3f, given two %.3f ; redundancy by the last estimate %.0f%%%n",
                s.length(), words.size(), new TreeSet<>(words).size(), top, h0, h1, h2, h3, 100 * (1 - h3 / h0));

        // ---- 3. imitations ---------------------------------------------------------------------------------------------
        System.out.println("imitation: 0 (random letters): " + imitate(s, -1, 72));
        System.out.println("imitation: 1 (letter frequencies): " + imitate(s, 0, 72));
        System.out.println("imitation: 2 (letter pairs): " + imitate(s, 1, 72));
        System.out.println("imitation: 3 (letter triples): " + imitate(s, 2, 72));
        System.out.println("imitation: w1 (word frequencies): " + imitateWords(words, 0, 14));
        System.out.println("imitation: w2 (word pairs): " + imitateWords(words, 1, 14));

        // ---- 4. Shannon's code ------------------------------------------------------------------------------------------
        // sort by probability, give symbol i the first ceil(-log2 p_i) bits of the running total of the probabilities before it
        double cum = 0, avg = 0;
        String[] code = new String[27];
        for (int r = 0; r < 27; r++) {
            int i = idx[r];
            if (freq[i] == 0) continue;
            double p = (double) freq[i] / s.length();
            int len = (int) Math.ceil(-log2(p) - 1e-12);
            StringBuilder bits = new StringBuilder();
            double f = cum;
            for (int k = 0; k < len; k++) { f *= 2; bits.append(f >= 1 ? '1' : '0'); if (f >= 1) f -= 1; }
            code[i] = bits.toString();
            avg += p * len;
            cum += p;
        }
        for (int a = 0; a < 27; a++)
            for (int b = 0; b < 27; b++)
                if (a != b && code[a] != null && code[b] != null) check(!code[b].startsWith(code[a]), "no codeword begins another");
        check(avg >= h1 - 1e-12 && avg < h1 + 1, "H <= average length < H + 1");
        long bits = 0;
        for (char c : s.toCharArray()) bits += code[ALPHA.indexOf(c)].length();
        System.out.printf("code: Shannon's code from the letter frequencies: space %s, E %s, T %s, ... Z %s ; no codeword begins another ; average %.3f bits per letter, between H = %.3f and H + 1 ; the whole text in %d bits, against %d with 5 bits for every letter%n",
                code[0], code[ALPHA.indexOf('E')], code[ALPHA.indexOf('T')], code[ALPHA.indexOf('Z')] == null ? "(unused)" : code[ALPHA.indexOf('Z')],
                avg, h1, bits, 5L * s.length());

        System.out.println("InformationTheory: " + passed + " checks passed");
    }
}
