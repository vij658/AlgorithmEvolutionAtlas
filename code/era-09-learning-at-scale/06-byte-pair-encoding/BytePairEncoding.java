import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Era 9, topic 6: Byte-pair encoding for words (Philip Gage 1994; Rico Sennrich, Barry Haddow and Alexandra Birch,
 * University of Edinburgh, 2015).
 *
 * HOW IT WORKS
 *   Gage's compressor finds the most frequent pair of adjacent bytes in a text, replaces every occurrence with a byte
 *   that does not appear in the text, records the replacement in a table, and repeats. Sennrich, Haddow and Birch
 *   ran the same loop on words written as letters, with an end-of-word symbol after each word (the paper writes it as a raised dot, this program as _). Every merge adds
 *   one symbol to the vocabulary; after enough merges frequent words are single symbols and rare words are written
 *   with a few frequent pieces. A new word is cut up by replaying the learned merges in the order they were learned,
 *   so a word never seen in training still gets a spelling in known pieces.
 *   Language-model tokenizers start from the 256 possible bytes of UTF-8 instead of letters, so any text at all can
 *   be written without an "unknown" symbol.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Gage's compressor on Wikipedia's example, aaabdaaabac, and the table that undoes it.
 *   2. The paper's Figure 1 dictionary {low, lowest, newer, wider}: checks that the figure's four merges are a valid
 *      run of the algorithm (each was a most frequent pair when it was made) and shows this program's own run.
 *   3. Learns merges from a corpus of 20,000 sentences written from 40 word stems and their endings, with some
 *      stem-ending combinations held out; measures symbols per word as merges grow, and whether held-out words are
 *      cut at the boundary between stem and ending.
 *   4. Letters against bytes: a letter vocabulary meets characters it has never seen; a byte vocabulary never does,
 *      and decoding gives back every string exactly.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BytePairEncoding.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BytePairEncoding {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final String END = "_"; // the paper writes the end-of-word symbol as a raised dot; this program prints plain ASCII

    record Pair(String a, String b) {
        String joined() { return a + b; }

        public String toString() { return a + " " + b; }
    }

    // ---- learning merges -------------------------------------------------------------------------------------------------
    /** Pair counts over a dictionary of words (as symbol lists) with frequencies, in first-seen order. */
    static LinkedHashMap<Pair, Long> pairCounts(Map<List<String>, Long> vocab) {
        LinkedHashMap<Pair, Long> c = new LinkedHashMap<>();
        for (Map.Entry<List<String>, Long> e : vocab.entrySet()) {
            List<String> w = e.getKey();
            for (int i = 0; i + 1 < w.size(); i++) c.merge(new Pair(w.get(i), w.get(i + 1)), e.getValue(), Long::sum);
        }
        return c;
    }

    static List<String> applyMerge(List<String> w, Pair p) {
        List<String> out = new ArrayList<>(w.size());
        for (int i = 0; i < w.size(); i++) {
            if (i + 1 < w.size() && w.get(i).equals(p.a) && w.get(i + 1).equals(p.b)) { out.add(p.joined()); i++; }
            else out.add(w.get(i));
        }
        return out;
    }

    static Map<List<String>, Long> mergeVocab(Map<List<String>, Long> vocab, Pair p) {
        Map<List<String>, Long> nv = new LinkedHashMap<>();
        for (Map.Entry<List<String>, Long> e : vocab.entrySet()) nv.merge(applyMerge(e.getKey(), p), e.getValue(), Long::sum);
        return nv;
    }

    /** The most frequent pair; ties go to the pair seen first. */
    static Pair best(LinkedHashMap<Pair, Long> c) {
        Pair b = null; long bc = 0;
        for (Map.Entry<Pair, Long> e : c.entrySet()) if (e.getValue() > bc) { b = e.getKey(); bc = e.getValue(); }
        return b;
    }

    static List<String> letters(String word) {
        List<String> s = new ArrayList<>();
        word.codePoints().forEach(cp -> s.add(new String(Character.toChars(cp))));
        s.add(END);
        return s;
    }

    static List<Pair> learn(Map<String, Long> words, int merges, Map<List<String>, Long>[] finalVocab) {
        Map<List<String>, Long> vocab = new LinkedHashMap<>();
        for (Map.Entry<String, Long> e : words.entrySet()) vocab.put(letters(e.getKey()), e.getValue());
        List<Pair> out = new ArrayList<>();
        for (int k = 0; k < merges; k++) {
            Pair p = best(pairCounts(vocab));
            if (p == null) break;
            out.add(p);
            vocab = mergeVocab(vocab, p);
        }
        if (finalVocab != null) finalVocab[0] = vocab;
        return out;
    }

    /** Cut a word by replaying the merges: always apply the earliest-learned merge that occurs, until none does. */
    static List<String> segment(List<String> w, Map<Pair, Integer> rank) {
        while (true) {
            int bestR = Integer.MAX_VALUE; Pair bp = null;
            for (int i = 0; i + 1 < w.size(); i++) {
                Integer r = rank.get(new Pair(w.get(i), w.get(i + 1)));
                if (r != null && r < bestR) { bestR = r; bp = new Pair(w.get(i), w.get(i + 1)); }
            }
            if (bp == null) return w;
            w = applyMerge(w, bp);
        }
    }

    static Map<Pair, Integer> ranks(List<Pair> merges, int upTo) {
        Map<Pair, Integer> r = new HashMap<>();
        for (int i = 0; i < Math.min(upTo, merges.size()); i++) r.put(merges.get(i), i);
        return r;
    }

    // ---- the corpus --------------------------------------------------------------------------------------------------------
    static final String[] ADJ = {"low", "new", "wide", "old", "fast", "slow", "high", "small", "great", "kind",
            "light", "dark", "warm", "cold", "strong", "quick", "deep", "soft", "hard", "bright"};
    static final String[] ADJ_END = {"", "er", "est", "ly", "ness"};
    static final String[] VERB = {"walk", "talk", "play", "jump", "look", "open", "help", "work", "call", "need",
            "learn", "climb", "paint", "train", "clean", "start", "turn", "rain", "build", "read"};
    static final String[] VERB_END = {"", "s", "ed", "ing", "er", "ers"};
    static final String[] FUNC = {"the", "a", "of", "and", "to", "in", "is", "it", "was", "he", "she", "they", "we", "very", "more", "most", "not", "but"};

    /** Plain ASCII output: other characters are written as \\u{hex}. */
    static String esc(String t) {
        StringBuilder b = new StringBuilder();
        t.codePoints().forEach(cp -> { if (cp < 128) b.appendCodePoint(cp); else b.append(String.format("\\u{%x}", cp)); });
        return b.toString();
    }

    static String join(String stem, String end) {
        if (end.isEmpty()) return stem;
        if (stem.endsWith("e") && (end.startsWith("e"))) return stem + end.substring(1);
        return stem + end;
    }

    public static void main(String[] args) {
        // ---- 1. Gage's compressor -----------------------------------------------------------------------------------------
        String text = "aaabdaaabac";
        List<String> s = new ArrayList<>();
        for (char c : text.toCharArray()) s.add(String.valueOf(c));
        List<String> steps = new ArrayList<>(List.of(text));
        String[][] wiki = {{"Z", "a", "a"}, {"Y", "a", "b"}, {"X", "Z", "Y"}}; // Wikipedia's replacements, in order
        List<String[]> table = new ArrayList<>();
        StringJoiner tiej = new StringJoiner(", ");
        for (String[] rep : wiki) {
            // Gage counts a pair only where it can be replaced: "aaa" holds "aa" once, not twice
            Map<Pair, Long> c = new LinkedHashMap<>();
            for (int i = 0; i + 1 < s.size(); i++) c.putIfAbsent(new Pair(s.get(i), s.get(i + 1)), 0L);
            for (Pair q : c.keySet()) {
                long n = 0;
                for (int i = 0; i + 1 < s.size(); i++) if (s.get(i).equals(q.a) && s.get(i + 1).equals(q.b)) { n++; i++; }
                c.put(q, n);
            }
            Pair p = new Pair(rep[1], rep[2]);
            long top = Collections.max(c.values());
            check(c.getOrDefault(p, 0L) == top, "Wikipedia's pair " + p + " is a most frequent pair");
            long ties = c.values().stream().filter(x -> x == top).count() - 1;
            tiej.add(String.format("%s%s %d times%s", p.a, p.b, top, ties > 0 ? " (tied with " + ties + " other)" : ""));
            List<String> t = new ArrayList<>();
            for (int i = 0; i < s.size(); i++) {
                if (i + 1 < s.size() && s.get(i).equals(p.a) && s.get(i + 1).equals(p.b)) { t.add(rep[0]); i++; } else t.add(s.get(i));
            }
            table.add(new String[]{rep[0], p.a + p.b});
            s = t;
            steps.add(String.join("", s));
        }
        // undo with the table, last replacement first
        String back = String.join("", s);
        for (int i = table.size() - 1; i >= 0; i--) back = back.replace(table.get(i)[0], table.get(i)[1]);
        check(back.equals(text), "Gage's table restores the text");
        check(steps.get(1).equals("ZabdZabac") && steps.get(2).equals("ZYdZYac"), "the first two replacements are Wikipedia's");
        StringJoiner tj = new StringJoiner(", ");
        for (String[] r : table) tj.add(r[0] + " = " + r[1]);
        System.out.printf("gage: %s ; table %s ; each a most frequent pair when replaced: %s ; %d symbols down to %d, plus a table of %d entries ; undone with the table: %s%n",
                String.join(" -> ", steps), tj, tiej, text.length(), s.size(), table.size(), back);

        // ---- 2. the paper's Figure 1 ---------------------------------------------------------------------------------------
        Map<String, Long> fig = new LinkedHashMap<>();
        for (String w : new String[]{"low", "lowest", "newer", "wider"}) fig.put(w, 1L);
        Pair[] paper = {new Pair("r", END), new Pair("l", "o"), new Pair("lo", "w"), new Pair("e", "r" + END)};
        Map<List<String>, Long> v = new LinkedHashMap<>();
        for (String w : fig.keySet()) v.put(letters(w), 1L);
        StringJoiner fj = new StringJoiner(" ; ");
        for (Pair p : paper) {
            LinkedHashMap<Pair, Long> c = pairCounts(v);
            long top = Collections.max(c.values());
            long have = c.getOrDefault(p, 0L);
            List<String> tied = new ArrayList<>();
            for (Map.Entry<Pair, Long> e : c.entrySet()) if (e.getValue() == top) tied.add(e.getKey().toString());
            check(have == top, "the figure's merge " + p + " is a most frequent pair");
            fj.add(String.format("%s (count %d, tied with %d other pairs)", p, have, tied.size() - 1));
            v = mergeVocab(v, p);
        }
        StringJoiner after = new StringJoiner(", ");
        for (List<String> w : v.keySet()) after.add(String.join(" ", w));
        List<Pair> mine = learn(fig, 4, null);
        StringJoiner mj = new StringJoiner(", ");
        for (Pair p : mine) mj.add(p.toString());
        System.out.printf("figure: {low, lowest, newer, wider}, one of each ; the paper's merges, each a most frequent pair when made: %s ; the words afterwards: %s ; this program, ties to the pair seen first: %s%n",
                fj, after, mj);

        // ---- 3. learning from a corpus --------------------------------------------------------------------------------------
        Random r = new Random(6);
        List<String> forms = new ArrayList<>(), held = new ArrayList<>();
        List<String[]> heldParts = new ArrayList<>();
        for (int i = 0; i < ADJ.length; i++) {
            int out = 1 + r.nextInt(ADJ_END.length - 1); // hold out one ending of each stem, never the bare stem
            for (int k = 0; k < ADJ_END.length; k++) {
                String w = join(ADJ[i], ADJ_END[k]);
                if (k == out) { held.add(w); heldParts.add(new String[]{ADJ[i], ADJ_END[k]}); } else forms.add(w);
            }
        }
        for (int i = 0; i < VERB.length; i++) {
            int out = 1 + r.nextInt(VERB_END.length - 1);
            for (int k = 0; k < VERB_END.length; k++) {
                String w = VERB[i] + VERB_END[k];
                if (k == out) { held.add(w); heldParts.add(new String[]{VERB[i], VERB_END[k]}); } else forms.add(w);
            }
        }
        // Zipf-like weights: the n-th form is drawn with weight 1/(n+1)
        Collections.shuffle(forms, r);
        double[] cum = new double[forms.size()];
        double tot = 0;
        for (int i = 0; i < forms.size(); i++) { tot += 1.0 / (i + 1); cum[i] = tot; }
        Map<String, Long> words = new LinkedHashMap<>();
        long tokens = 0, chars = 0;
        for (int sn = 0; sn < 20_000; sn++) {
            int len = 4 + r.nextInt(6);
            for (int k = 0; k < len; k++) {
                String w;
                if (r.nextDouble() < 0.4) w = FUNC[r.nextInt(FUNC.length)];
                else {
                    double x = r.nextDouble() * tot;
                    int lo = 0, hi = forms.size() - 1;
                    while (lo < hi) { int mid = (lo + hi) / 2; if (cum[mid] < x) lo = mid + 1; else hi = mid; }
                    w = forms.get(lo);
                }
                words.merge(w, 1L, Long::sum);
                tokens++; chars += w.length();
            }
        }
        for (String h : held) check(!words.containsKey(h), "held-out word " + h + " is not in the corpus");
        @SuppressWarnings("unchecked") Map<List<String>, Long>[] fv = new Map[1];
        List<Pair> merges = learn(words, 300, fv);
        Set<String> alphabet = new TreeSet<>();
        for (String w : words.keySet()) for (String c : letters(w)) alphabet.add(c);
        System.out.printf("corpus: 20,000 sentences, %,d words, %,d distinct, %d letters plus the end symbol ; %d stems, each with endings, and one ending of each stem held out: %d words never seen, such as %s%n",
                tokens, words.size(), alphabet.size() - 1, ADJ.length + VERB.length, held.size(), String.join(", ", held.subList(0, 6)));

        StringJoiner first = new StringJoiner(", ");
        for (int i = 0; i < 20; i++) first.add(merges.get(i).toString().replace(" ", "+"));
        System.out.printf("merges: the first 20: %s%n", first);

        // symbols per word as merges grow
        StringJoiner gj = new StringJoiner(" ; ");
        double prev = Double.MAX_VALUE;
        int[] Ks = {0, 10, 25, 50, 100, 200, 300};
        for (int K : Ks) {
            Map<Pair, Integer> rk = ranks(merges, K);
            long sym = 0;
            for (Map.Entry<String, Long> e : words.entrySet()) sym += segment(letters(e.getKey()), rk).size() * e.getValue();
            double per = (double) sym / tokens;
            check(per <= prev, "more merges never mean more symbols per word");
            prev = per;
            gj.add(String.format("%d merges: %.2f symbols per word, vocabulary %d", K, per, alphabet.size() + K));
        }
        System.out.printf("growth: %s ; every word of the corpus a single symbol needs a vocabulary of %d%n", gj, words.size());

        // held-out words: cut at the boundary between stem and ending?
        int K = 150;
        Map<Pair, Integer> rk = ranks(merges, K);
        int atBoundary = 0, whole = 0;
        double symHeld = 0;
        StringJoiner ex = new StringJoiner(" ; ");
        for (int i = 0; i < held.size(); i++) {
            List<String> seg = segment(letters(held.get(i)), rk);
            symHeld += seg.size();
            check(String.join("", seg).equals(held.get(i) + END), "the pieces spell the word");
            for (String p : seg) check(alphabet.contains(p) || merges.subList(0, K).stream().anyMatch(m -> m.joined().equals(p)), "every piece is in the vocabulary");
            // is there a cut exactly where the stem ends?
            String stem = heldParts.get(i)[0], end = heldParts.get(i)[1];
            int cutAt = join(stem, end).length() - end.length() + (stem.endsWith("e") && end.startsWith("e") ? 1 : 0);
            int pos = 0; boolean cut = false;
            for (String p : seg) { pos += p.length(); if (pos == cutAt) cut = true; }
            if (cut) atBoundary++;
            if (seg.size() == 1) whole++;
            if (i % 7 == 0) ex.add(held.get(i) + " = " + String.join(" + ", seg));
        }
        check(whole == 0, "an unseen word is never a single learned symbol");
        check(atBoundary > held.size() / 2, "most unseen words are cut where stem meets ending");
        System.out.printf("unseen: after %d merges, the %d held-out words in %.2f pieces each ; cut exactly where stem meets ending: %d of %d ; %s%n",
                K, held.size(), symHeld / held.size(), atBoundary, held.size(), ex);

        // ---- 4. letters against bytes ---------------------------------------------------------------------------------------
        String[] tests = {"slowest", "naïve", "café", "Zürich", "日本語", "😀 ok", "Ωmega"};
        Set<String> letterVocab = new HashSet<>(alphabet);
        for (Pair p : merges) letterVocab.add(p.joined());
        // byte-level: learn merges on the UTF-8 bytes of the same corpus words
        Map<List<String>, Long> bv = new LinkedHashMap<>();
        for (Map.Entry<String, Long> e : words.entrySet()) {
            List<String> b = new ArrayList<>();
            for (byte x : e.getKey().getBytes(StandardCharsets.UTF_8)) b.add(String.format("%02x", x & 0xff));
            bv.put(b, e.getValue());
        }
        List<Pair> bm = new ArrayList<>();
        for (int k = 0; k < 150; k++) { Pair p = best(pairCounts(bv)); bm.add(p); bv = mergeVocab(bv, p); }
        Map<Pair, Integer> brk = ranks(bm, 150);
        StringJoiner lj = new StringJoiner(" ; ");
        int unkLetters = 0, exact = 0;
        for (String t : tests) {
            int unk = 0;
            for (String w : t.split(" ")) for (String c : letters(w)) if (!letterVocab.contains(c)) unk++;
            unkLetters += unk;
            // bytes: always 256 base symbols, so nothing is unknown
            List<String> b = new ArrayList<>();
            for (byte x : t.getBytes(StandardCharsets.UTF_8)) b.add(String.format("%02x", x & 0xff));
            List<String> seg = segment(b, brk);
            StringBuilder hex = new StringBuilder();
            for (String p : seg) hex.append(p);
            byte[] dec = new byte[hex.length() / 2];
            for (int i = 0; i < dec.length; i++) dec[i] = (byte) Integer.parseInt(hex.substring(2 * i, 2 * i + 2), 16);
            if (new String(dec, StandardCharsets.UTF_8).equals(t)) exact++;
            lj.add(String.format("\"%s\": %d unknown letters, %d UTF-8 bytes in %d byte tokens", esc(t), unk, b.size(), seg.size()));
        }
        check(unkLetters > 0 && exact == tests.length, "bytes encode everything and decode exactly");
        System.out.printf("bytes: letter vocabulary of %d letters, the end symbol and 300 merges, byte vocabulary of 256 bytes + 150 merges ; %s ; decoded exactly from bytes: %d of %d%n",
                alphabet.size() - 1, lj, exact, tests.length);

        System.out.println("BytePairEncoding: " + passed + " checks passed");
    }
}
