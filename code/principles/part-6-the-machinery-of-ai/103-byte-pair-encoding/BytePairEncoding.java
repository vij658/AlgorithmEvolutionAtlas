import java.nio.charset.StandardCharsets;
import java.util.*;

/**
 * Entry 103 of the principles catalog (Part 6): Byte-pair encoding (BPE), how language models cut text into tokens
 *
 * HOW IT WORKS
 *   Start with the 256 possible bytes of UTF-8 text, so any string at all can be written down. Count every pair of
 *   neighbouring tokens in a training text, give the most frequent pair a new token number, replace it everywhere,
 *   and repeat. Each merge is recorded in order; the merge list IS the tokenizer. To encode new text, start from
 *   its bytes and keep applying the earliest-learned merge that is present until none applies; to decode, glue
 *   the bytes of each token back together. Text is first split into chunks that start at a space, so merges
 *   never cross a word boundary. The method began as a compression scheme (Gage, 1994); Sennrich, Haddow and
 *   Birch (2016) used it for subword units in translation, and GPT-2 (2019) used it on bytes.
 *   Consequences worth knowing: the model never sees letters, only token numbers ("strawberry" may be two or
 *   three tokens, which is why counting its letters is hard), and text unlike the training text (another script,
 *   unusual code) costs more tokens, which means more money, more latency and less room in the context window.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BytePairEncoding.java
 *   Expected: the output in expected-output.txt, ending "BytePairEncoding: 2380 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BytePairEncoding {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long pairKey(int a, int b) { return ((long) a << 32) | (b & 0xffffffffL); }

    static final class Tokenizer {
        final List<long[]> merges = new ArrayList<>();          // merges.get(r) = {left, right}; new id = 256 + r
        final Map<Long, Integer> rank = new HashMap<>();
        final List<byte[]> vocab = new ArrayList<>();           // id -> bytes
        List<int[]> trainedWords;                               // the training chunks after the last merge
        List<String> trainedChunks;

        Tokenizer() { for (int i = 0; i < 256; i++) vocab.add(new byte[]{(byte) i}); }

        int vocabSize() { return vocab.size(); }

        /** Learn up to numMerges merges; stop early when no pair occurs at least twice. */
        static Tokenizer train(String text, int numMerges, List<Integer> tokensAfterEachMerge) {
            Tokenizer t = new Tokenizer();
            Map<String, Integer> counts = new LinkedHashMap<>();
            for (String c : chunks(text)) counts.merge(c, 1, Integer::sum);
            List<String> keys = new ArrayList<>(counts.keySet());
            List<int[]> words = new ArrayList<>();
            int[] freq = new int[keys.size()];
            for (int i = 0; i < keys.size(); i++) { words.add(bytesOf(keys.get(i))); freq[i] = counts.get(keys.get(i)); }
            for (int m = 0; m < numMerges; m++) {
                Map<Long, Integer> pairs = new HashMap<>();
                for (int w = 0; w < words.size(); w++) {
                    int[] ids = words.get(w);
                    for (int i = 0; i + 1 < ids.length; i++) pairs.merge(pairKey(ids[i], ids[i + 1]), freq[w], Integer::sum);
                }
                long best = 0; int bestCount = 1;
                for (Map.Entry<Long, Integer> e : pairs.entrySet()) {
                    int cnt = e.getValue();
                    if (cnt > bestCount || (cnt == bestCount && cnt > 1 && e.getKey() < best)) { best = e.getKey(); bestCount = cnt; }
                }
                if (bestCount < 2) break;
                int left = (int) (best >>> 32), right = (int) best, id = t.vocab.size();
                t.rank.put(best, t.merges.size());
                t.merges.add(new long[]{left, right});
                byte[] lb = t.vocab.get(left), rb = t.vocab.get(right), nb = Arrays.copyOf(lb, lb.length + rb.length);
                System.arraycopy(rb, 0, nb, lb.length, rb.length);
                t.vocab.add(nb);
                for (int w = 0; w < words.size(); w++) words.set(w, replace(words.get(w), left, right, id));
                if (tokensAfterEachMerge != null) {
                    int total = 0;
                    for (int w = 0; w < words.size(); w++) total += words.get(w).length * freq[w];
                    tokensAfterEachMerge.add(total);
                }
            }
            t.trainedWords = words;
            t.trainedChunks = keys;
            return t;
        }

        /** Encode one chunk: apply the earliest-learned merge present, everywhere, until none applies. */
        int[] encodeChunk(String chunk) {
            int[] ids = bytesOf(chunk);
            while (ids.length > 1) {
                int bestRank = Integer.MAX_VALUE;
                for (int i = 0; i + 1 < ids.length; i++) {
                    Integer r = rank.get(pairKey(ids[i], ids[i + 1]));
                    if (r != null && r < bestRank) bestRank = r;
                }
                if (bestRank == Integer.MAX_VALUE) break;
                long[] m = merges.get(bestRank);
                ids = replace(ids, (int) m[0], (int) m[1], 256 + bestRank);
            }
            return ids;
        }

        int[] encode(String text) {
            List<Integer> out = new ArrayList<>();
            for (String c : chunks(text)) for (int id : encodeChunk(c)) out.add(id);
            return out.stream().mapToInt(Integer::intValue).toArray();
        }

        String decode(int[] ids) {
            java.io.ByteArrayOutputStream bos = new java.io.ByteArrayOutputStream();
            for (int id : ids) bos.writeBytes(vocab.get(id));
            return bos.toString(StandardCharsets.UTF_8);
        }

        /** Show the cut points: tokens separated by '|', a leading space shown as '_'. */
        String show(String text) {
            StringBuilder sb = new StringBuilder();
            for (int id : encode(text)) {
                if (sb.length() > 0) sb.append('|');
                sb.append(new String(vocab.get(id), StandardCharsets.UTF_8).replace(' ', '_'));
            }
            return sb.toString();
        }
    }

    /** Split text into chunks that each start at a space, so merges never join two words. */
    static List<String> chunks(String text) {
        List<String> out = new ArrayList<>();
        int start = 0;
        for (int i = 1; i <= text.length(); i++) {
            if (i == text.length() || text.charAt(i) == ' ') { out.add(text.substring(start, i)); start = i; }
        }
        if (text.isEmpty()) out.clear();
        return out;
    }

    static int[] bytesOf(String s) {
        byte[] b = s.getBytes(StandardCharsets.UTF_8);
        int[] ids = new int[b.length];
        for (int i = 0; i < b.length; i++) ids[i] = b[i] & 0xff;
        return ids;
    }

    /** Replace every non-overlapping occurrence of (left, right), scanning left to right. */
    static int[] replace(int[] ids, int left, int right, int id) {
        int[] out = new int[ids.length];
        int n = 0;
        for (int i = 0; i < ids.length; i++) {
            if (i + 1 < ids.length && ids[i] == left && ids[i + 1] == right) { out[n++] = id; i++; }
            else out[n++] = ids[i];
        }
        return Arrays.copyOf(out, n);
    }

    // ----------------------------------------------------------------------------------------------------
    // Training text (written for this program)
    // ----------------------------------------------------------------------------------------------------
    static final String CORPUS = String.join(" ",
            "An algorithm is a finite list of steps that solves a problem. Every algorithm in this book enters",
            "as the fix for something that hurt. Adding two numbers hurt when the numbers grew long, so people",
            "invented the carry. Searching hurt when the list grew long, so people invented binary search. Sorting",
            "hurt when the cards would not fit on the table, so people invented merge sort. A language model is",
            "also an algorithm. It reads a list of tokens and predicts the next token. The tokens are not letters",
            "and they are not words. They are pieces of words, learned from text by counting which pairs of pieces",
            "appear together most often. The most frequent pair becomes a new piece, and the counting starts again.",
            "This is byte pair encoding. The algorithm is greedy, it is simple, and it is everywhere. Because the",
            "model sees pieces and not letters, a question such as how many letters r are in the word strawberry",
            "is harder than it looks: the model sees the pieces of strawberry, not the ten letters of strawberry.",
            "Because the pieces were learned from the training text, text that looks like the training text needs",
            "few pieces, and text that does not look like it needs many pieces. Many pieces cost more money, take",
            "more time, and fill the context window sooner. The tokenizer is an algorithm too, and it has a history:",
            "it began as a way to compress files, and it became the way that every large language model reads.",
            "The steps are counting pairs, merging the most frequent pair, and repeating until the vocabulary is",
            "large enough. The steps to encode new text are applying the learned merges in the order they were",
            "learned. The steps to decode are gluing the bytes of the pieces back together, which always works.");

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BytePairEncoding.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // Known answer: the classic example "aaabdaaabac". Merge aa (Z), then ab (Y), then Z Y (X): XdXac.
        // (After the first merge, (aa, a) and (a, b) both occur twice; ties go to the smaller pair of ids.)
        Tokenizer g = Tokenizer.train("aaabdaaabac", 10, null);
        String[] expect = {"aa", "ab", "aaab"};
        check(g.merges.size() == 3, "three merges");
        for (int i = 0; i < 3; i++) check(new String(g.vocab.get(256 + i), StandardCharsets.UTF_8).equals(expect[i]), "merge " + i);
        check(g.encode("aaabdaaabac").length == 5, "aaabdaaabac becomes 5 tokens");
        System.out.println("\"aaabdaaabac\": merges learned in order aa, ab, aaab; tokens " + g.show("aaabdaaabac"));

        // Train on the corpus, recording the training text's token count after every merge.
        List<Integer> after = new ArrayList<>();
        Tokenizer t = Tokenizer.train(CORPUS, 400, after);
        int bytes = CORPUS.getBytes(StandardCharsets.UTF_8).length;
        for (int i = 0; i < after.size(); i++) check(after.get(i) < (i == 0 ? bytes : after.get(i - 1)), "each merge shortens the text");
        StringBuilder sb = new StringBuilder(f("training text: %,d bytes; tokens after ", bytes));
        for (int m : new int[]{0, 25, 50, 100, 200, after.size()}) {
            int tokens = m == 0 ? bytes : after.get(m - 1);
            sb.append(f("%d merges: %,d (%.2f bytes per token); ", m, tokens, bytes / (double) tokens));
        }
        System.out.println(sb.toString().trim());
        System.out.println(f("merges learned before no pair occurred twice: %d (vocabulary %d)", t.merges.size(), t.vocabSize()));

        // Encoding with the merge list reproduces exactly the segmentation found during training.
        for (int i = 0; i < t.trainedChunks.size(); i++)
            check(Arrays.equals(t.encodeChunk(t.trainedChunks.get(i)), t.trainedWords.get(i)), "encode = training segmentation");

        // Round trip on the corpus and on 2,000 random strings from several scripts, emoji included.
        check(t.decode(t.encode(CORPUS)).equals(CORPUS), "corpus round trip");
        int[] alphabet = {'a', 'e', 'r', 's', 't', ' ', ' ', '.', 'A', 'é', 'ñ', 0x0915, 0x093F, 0x0928, 0x4E2D, 0x1F600, 0x1F44D};
        for (int k = 0; k < 2000; k++) {
            StringBuilder s = new StringBuilder();
            int len = rnd.nextInt(30);
            for (int i = 0; i < len; i++) s.appendCodePoint(alphabet[rnd.nextInt(alphabet.length)]);
            String str = s.toString();
            check(t.decode(t.encode(str)).equals(str), "round trip");
        }
        check(t.encode("").length == 0, "empty string");

        // What the model actually sees.
        for (String s : new String[]{"The algorithm", " strawberry", " Strawberry", " STRAWBERRY", " tokenizer", " tokenization"})
            { int n = t.encode(s).length; System.out.println(f("%-15s -> %d token%s: %s", "\"" + s + "\"", n, n == 1 ? "" : "s", t.show(s))); }
        check(t.encode(" strawberry").length < t.encode(" STRAWBERRY").length, "capitals cost more tokens");

        // The same sentence in English and in Hindi, with a tokenizer trained on English.
        String en = "An algorithm is a list of steps.";
        String hi = "एल्गोरिदम चरणों की एक सूची है।";
        int enTok = t.encode(en).length, hiTok = t.encode(hi).length;
        int enBytes = en.getBytes(StandardCharsets.UTF_8).length, hiBytes = hi.getBytes(StandardCharsets.UTF_8).length;
        check(hiTok > 3 * enTok, "text unlike the training text costs more tokens");
        check(hiBytes > 2 * hi.length(), "Devanagari takes 3 bytes per character in UTF-8");
        System.out.println(f("English sentence: %d characters, %d bytes, %d tokens; the same sentence in Hindi: "
                + "%d characters, %d bytes, %d tokens (%.1f times as many)",
                en.length(), enBytes, enTok, hi.length(), hiBytes, hiTok, hiTok / (double) enTok));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(103));
        System.out.println("BytePairEncoding: " + passed + " checks passed");
    }
}
