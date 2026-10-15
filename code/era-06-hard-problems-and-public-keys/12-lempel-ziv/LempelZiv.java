import java.nio.file.*;
import java.util.*;

/**
 * Era 6, topic 12: universal compression (Ziv and Lempel, 1977 and 1978).
 *
 * HOW IT WORKS
 *   Huffman's code (Era 5) needs the probabilities of the letters, and it codes each letter on its own. Ziv and Lempel
 *   asked for a method that knows nothing about the source in advance and still, on long enough inputs, does as well
 *   as a code designed for that source.
 *   1977 (LZ77): keep the last W letters already sent. At each step find the longest string starting here that also
 *   starts somewhere in that window; send (how far back, how long, the next letter). The receiver copies from what
 *   it already has.
 *   1978 (LZ78): build a dictionary of phrases as you go. At each step find the longest phrase in the dictionary that
 *   matches what comes next; send (its number, the next letter), and add that phrase plus the letter as a new entry.
 *   Repetition at any distance, any phrase that recurs, is coded by a reference; the longer the input, the longer
 *   the phrases, and the fewer bits per letter.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Both methods on a short string, every token shown, and decoded back.
 *   2. Round trips on 2,000 random inputs and on this book's field notes.
 *   3. Bits per letter on the field notes: Huffman's code for single letters, LZ77, LZ78.
 *   4. A text made of one block repeated 50 times: what letter-by-letter coding cannot see.
 *   5. A source with memory (a two-state chain that stays put 9 times in 10): LZ78's bits per symbol for 1,000 to
 *      10,000,000 symbols, falling towards the source's entropy rate, which it was never told.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step; corpus.txt must be in the current folder)
 *   java LempelZiv.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LempelZiv {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1977L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int rnd(int n) { return (int) (uniform() * n); }

    // ---- LZ77 --------------------------------------------------------------------------------------------------------
    record Triple(int back, int length, char next) {}

    static List<Triple> lz77(String s, int window, int maxLen) {
        List<Triple> out = new ArrayList<>();
        int i = 0, n = s.length();
        while (i < n) {
            int bestLen = 0, bestBack = 0;
            for (int j = Math.max(0, i - window); j < i; j++) {
                int k = 0;
                while (k < maxLen && i + k < n - 1 && s.charAt(j + k) == s.charAt(i + k)) k++;   // may run past i: overlaps allowed
                if (k > bestLen) { bestLen = k; bestBack = i - j; }
            }
            out.add(new Triple(bestBack, bestLen, s.charAt(i + bestLen)));
            i += bestLen + 1;
        }
        return out;
    }

    static String unLz77(List<Triple> code) {
        StringBuilder sb = new StringBuilder();
        for (Triple t : code) {
            int start = sb.length() - t.back();
            for (int k = 0; k < t.length(); k++) sb.append(sb.charAt(start + k));
            sb.append(t.next());
        }
        return sb.toString();
    }

    // ---- LZ78 --------------------------------------------------------------------------------------------------------
    record Pair(int phrase, char next) {}

    static List<Pair> lz78(String s) {
        List<Pair> out = new ArrayList<>();
        HashMap<Long, Integer> dict = new HashMap<>();
        int node = 0, entries = 1;                                   // entry 0 is the empty phrase
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            Integer child = dict.get(((long) node << 16) | c);
            if (child != null && i < s.length() - 1) { node = child; continue; }
            if (child != null) { out.add(new Pair(node, c)); break; }   // input ends inside a known phrase
            out.add(new Pair(node, c));
            dict.put(((long) node << 16) | c, entries++);
            node = 0;
        }
        return out;
    }

    static String unLz78(List<Pair> code) {
        List<String> dict = new ArrayList<>(List.of(""));
        StringBuilder sb = new StringBuilder();
        for (Pair p : code) { String w = dict.get(p.phrase()) + p.next(); sb.append(w); dict.add(w); }
        return sb.toString();
    }

    static int bitsFor(long values) { return 64 - Long.numberOfLeadingZeros(Math.max(1, values - 1)); }

    /** LZ78 size in bits: the k-th pair's phrase number takes ceil(log2 k) bits, its letter `letterBits`. */
    static long lz78Bits(List<Pair> code, int letterBits) {
        long bits = 0;
        for (int k = 1; k <= code.size(); k++) bits += bitsFor(k) + letterBits;
        return bits;
    }

    static double huffmanBits(String s) {
        // Huffman's code for single letters: total length = sum over merges of the merged weights
        Map<Character, Long> f = new HashMap<>();
        for (char c : s.toCharArray()) f.merge(c, 1L, Long::sum);
        PriorityQueue<Long> pq = new PriorityQueue<>(f.values());
        long total = 0;
        while (pq.size() > 1) { long a = pq.poll(), b = pq.poll(); total += a + b; pq.add(a + b); }
        return total;
    }

    static String show77(List<Triple> code) {
        StringJoiner sj = new StringJoiner(" ");
        for (Triple t : code) sj.add("(" + t.back() + "," + t.length() + "," + (t.next() == ' ' ? "_" : String.valueOf(t.next())) + ")");
        return sj.toString();
    }

    public static void main(String[] args) throws Exception {
        // ---- 1. a short string ------------------------------------------------------------------------------------------
        String small = "abracadabra abracadabra";
        List<Triple> c77 = lz77(small, 4096, 255);
        List<Pair> c78 = lz78(small);
        check(unLz77(c77).equals(small) && unLz78(c78).equals(small), "both decode the short string");
        StringJoiner p78 = new StringJoiner(" ");
        List<String> dict = new ArrayList<>(List.of(""));
        for (Pair p : c78) { String w = dict.get(p.phrase()) + p.next(); dict.add(w); p78.add("(" + p.phrase() + "," + (p.next() == ' ' ? "_" : p.next()) + ")=" + w.replace(' ', '_')); }
        System.out.printf("small: \"%s\" (%d letters, _ is a space) ; LZ77 sends %d triples (how far back, how long, next letter): %s ; LZ78 sends %d pairs (phrase number, next letter), each becoming a new phrase: %s%n",
                small, small.length(), c77.size(), show77(c77), c78.size(), p78);

        // ---- 2. round trips ------------------------------------------------------------------------------------------
        String corpus = new String(Files.readAllBytes(Paths.get("corpus.txt")), "ISO-8859-1");   // one char per byte
        int trips = 0;
        for (int t = 0; t < 2000; t++) {
            int alpha = 1 + rnd(26), len = 1 + rnd(400);
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < len; i++) sb.append((char) ('a' + rnd(alpha)));
            String x = sb.toString();
            check(unLz77(lz77(x, 1 + rnd(64), 1 + rnd(20))).equals(x), "LZ77 round trip");
            check(unLz78(lz78(x)).equals(x), "LZ78 round trip");
            trips++;
        }
        List<Triple> k77 = lz77(corpus, 4096, 15);
        List<Pair> k78 = lz78(corpus);
        check(unLz77(k77).equals(corpus) && unLz78(k78).equals(corpus), "the field notes come back exactly");
        System.out.printf("trips: %,d random strings (1 to 400 letters, alphabets of 1 to 26, random window sizes) and this book's field notes (%,d bytes) encoded and decoded by both methods ; every one comes back exactly%n",
                trips, corpus.length());

        // ---- 3. bits per letter on the field notes -------------------------------------------------------------------
        int n = corpus.length();
        double huff = huffmanBits(corpus) / n;
        long b77 = (long) k77.size() * (12 + 4 + 8);
        long b78 = lz78Bits(k78, 8);
        System.out.printf("notes: the field notes as %,d bytes of 8 bits ; Huffman's code for single bytes %.2f bits per byte ; LZ77 with a window of 4,096 and matches up to 15 (12 + 4 + 8 = 24 bits per triple): %,d triples, %.2f bits per byte ; LZ78: %,d pairs (phrase number growing from 1 to %d bits, plus 8), %.2f bits per byte ; on a text this short, Huffman's code still wins%n",
                n, huff, k77.size(), (double) b77 / n, k78.size(), bitsFor(k78.size()), (double) b78 / n);

        // ---- 4. repetition -----------------------------------------------------------------------------------------------
        String block = corpus.substring(0, 1000);
        String rep = block.repeat(50);
        List<Triple> r77 = lz77(rep, 4096, 255);
        List<Pair> r78 = lz78(rep);
        double rh = huffmanBits(rep) / rep.length();
        long rb77 = (long) r77.size() * (12 + 8 + 8);
        long rb78 = lz78Bits(r78, 8);
        check(unLz77(r77).equals(rep) && unLz78(r78).equals(rep), "repetition round trip");
        check((double) rb77 / rep.length() < 0.5 && rh > 3, "LZ77 sees the repetition, Huffman cannot");
        check(Math.abs(rh - huffmanBits(block) / block.length()) < 1e-12, "Huffman gives the same rate for one copy and for fifty");
        System.out.printf("repeat: the first 1,000 bytes of the notes, repeated 50 times (50,000 bytes) ; Huffman's code for single bytes %.2f bits per byte, exactly as for one copy ; LZ77 (window 4,096, matches up to 255, 12 + 8 + 8 bits per triple): %,d triples, %.2f bits per byte ; LZ78: %,d pairs, %.2f bits per byte, its phrases growing longer with every copy%n",
                rh, r77.size(), (double) rb77 / rep.length(), r78.size(), (double) rb78 / rep.length());

        // ---- 5. universality on a source with memory -------------------------------------------------------------------
        double stay = 0.9, h = -(stay * Math.log(stay) + (1 - stay) * Math.log(1 - stay)) / Math.log(2);
        int total = 10_000_000;
        StringBuilder src = new StringBuilder(total);
        char cur = '0';
        for (int i = 0; i < total; i++) { src.append(cur); if (uniform() >= stay) cur = cur == '0' ? '1' : '0'; }
        String s = src.toString();
        StringJoiner uj = new StringJoiner(" ; ");
        double prevRate = 9, lastRate = 0;
        for (int len = 1000; len <= total; len *= 10) {
            String part = s.substring(0, len);
            List<Pair> code = lz78(part);
            double rate = (double) lz78Bits(code, 1) / len;
            if (len <= 100_000) check(unLz78(code).equals(part), "binary round trip");
            check(rate < prevRate, "the rate falls as the input grows");
            prevRate = rate;
            lastRate = rate;
            uj.add(String.format("%,d symbols: %.3f", len, rate));
        }
        long ones = s.chars().filter(c -> c == '1').count();
        double p1 = (double) ones / total, h0 = -(p1 * Math.log(p1) + (1 - p1) * Math.log(1 - p1)) / Math.log(2);
        check(lastRate < h0 && lastRate > h, "between the per-symbol entropy and the entropy rate");
        System.out.printf("universal: a source of 0s and 1s that repeats its last symbol with probability 0.9 ; 0s and 1s are equally common, so coding symbols one at a time cannot beat %.3f bits per symbol ; the source's true rate (its entropy rate, from Era 4's Shannon) is %.3f ; LZ78, told nothing about the source, bits per symbol: %s ; still falling towards %.3f%n",
                h0, h, uj, h);

        System.out.println("LempelZiv: " + passed + " checks passed");
    }
}
