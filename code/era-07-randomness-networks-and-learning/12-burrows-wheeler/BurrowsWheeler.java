import java.nio.file.*;
import java.util.*;
import java.util.zip.Deflater;

/**
 * Era 7, topic 12: the Burrows-Wheeler transform (Michael Burrows and David Wheeler, Digital Equipment Corporation
 * Systems Research Center, Palo Alto, report of 10 May 1994; found by Wheeler in 1983).
 *
 * HOW IT WORKS
 *   Write down every rotation of a block of text (move the first letter to the end, again and again), sort the
 *   rotations alphabetically, and keep only the last letter of each. That column, L, is a rearrangement of the text
 *   in which letters that come before similar contexts sit together: all the rotations that start with "he" are
 *   sorted next to each other, and the letters just before "he" are mostly t, so the t's bunch up in L. L compresses well with simple methods: move-to-front turns repeated letters into
 *   small numbers, mostly zeros, and a Huffman code (Era 5) packs those into few bits. The surprise is that L, plus
 *   the position of the original text among the sorted rotations, is enough to rebuild the text: the k-th "e" in L
 *   and the k-th "e" in the sorted first column are the same letter of the text (the "LF mapping"), so the text can be
 *   walked backwards one letter at a time. The same mapping lets one count a pattern's occurrences in the text by
 *   looking at L alone, one pattern letter at a time (Ferragina and Manzini's FM index, 2000), which is how programs
 *   align DNA reads to a genome.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The transform of "abracadabra", rotation by rotation, and its inverse.
 *   2. This book's field notes (corpus.txt, the same text as Era 6's Lempel-Ziv program): runs of equal letters
 *      before and after, move-to-front, and bits per byte against Huffman alone, Era 6's LZ77, and Deflate (gzip).
 *   3. Block size: the transform needs large blocks to work well.
 *   4. Counting patterns with the FM index's backward search, against counting by scanning.
 *   5. Round trips: 2,000 random strings and every block transformed and inverted.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step; corpus.txt must be in the current folder)
 *   java BurrowsWheeler.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BurrowsWheeler {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1994L;

    static int below(int k) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % k);
    }

    /** The rotations of s in sorted order, as starting positions (prefix doubling on cyclic ranks). */
    static int[] sortedRotations(byte[] s) {
        int n = s.length;
        int[] rank = new int[n];
        for (int i = 0; i < n; i++) rank[i] = s[i] & 0xff;
        int[] order = new int[n];
        long[] key = new long[n];
        for (int k = 1; ; k <<= 1) {
            for (int i = 0; i < n; i++) key[i] = ((long) rank[i] * (n + 256) + rank[(int) ((i + (long) k) % n)]) * n + i;
            Arrays.sort(key);
            int[] newRank = new int[n];
            int r = 0;
            for (int j = 0; j < n; j++) {
                order[j] = (int) (key[j] % n);
                if (j > 0 && key[j] / n != key[j - 1] / n) r++;
                newRank[order[j]] = r;
            }
            rank = newRank;
            if (r == n - 1 || k >= n) break;
        }
        return order;
    }

    static int lastIndex;    // the row of the sorted rotations that holds the original text ("I" in the report)

    static byte[] bwt(byte[] s) {
        int n = s.length;
        int[] order = sortedRotations(s);
        byte[] L = new byte[n];
        for (int j = 0; j < n; j++) {
            L[j] = s[(order[j] + n - 1) % n];
            if (order[j] == 0) lastIndex = j;
        }
        return L;
    }

    /** Inverts the transform with the LF mapping: walk backwards from row I. */
    static byte[] inverse(byte[] L, int I) {
        int n = L.length;
        int[] count = new int[257];
        for (byte b : L) count[(b & 0xff) + 1]++;
        for (int c = 1; c <= 256; c++) count[c] += count[c - 1];           // count[c] = letters smaller than c
        int[] seen = new int[256], lf = new int[n];
        for (int j = 0; j < n; j++) { int c = L[j] & 0xff; lf[j] = count[c] + seen[c]++; }
        byte[] s = new byte[n];
        int row = I;
        for (int k = n - 1; k >= 0; k--) { s[k] = L[row]; row = lf[row]; }
        return s;
    }

    static int[] moveToFront(byte[] L) {
        List<Integer> list = new ArrayList<>();
        for (int c = 0; c < 256; c++) list.add(c);
        int[] out = new int[L.length];
        for (int j = 0; j < L.length; j++) {
            int c = L[j] & 0xff, pos = list.indexOf(c);
            out[j] = pos;
            list.remove(pos);
            list.add(0, c);
        }
        return out;
    }

    /** Bits needed by a Huffman code built for these symbol counts (the code table itself not counted). */
    static long huffmanBits(long[] freq) {
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> a[0] != b[0] ? Long.compare(a[0], b[0]) : Long.compare(a[1], b[1]));
        long id = 0;
        for (long f : freq) if (f > 0) pq.add(new long[]{f, id++});
        if (pq.size() == 1) return pq.peek()[0];
        long bits = 0;
        while (pq.size() > 1) {
            long[] a = pq.poll(), b = pq.poll();
            bits += a[0] + b[0];                          // each merge adds one bit to every symbol beneath it
            pq.add(new long[]{a[0] + b[0], id++});
        }
        return bits;
    }

    static int runs(byte[] s) {
        int r = s.length > 0 ? 1 : 0;
        for (int i = 1; i < s.length; i++) if (s[i] != s[i - 1]) r++;
        return r;
    }

    static long blockBits(byte[] block) {
        int[] m = moveToFront(bwt(block));
        long[] f = new long[256];
        for (int x : m) f[x]++;
        return huffmanBits(f) + 32;                        // plus 32 bits to record I
    }

    // ---- the FM index: counting with L alone ----------------------------------------------------------------------
    static int[] C;           // C[c] = number of letters in the text smaller than c
    static int[][] occ;       // occ[c][j] = number of c among L[0..j-1]
    static long fmSteps;

    static void buildIndex(byte[] L) {
        int n = L.length;
        C = new int[257];
        for (byte b : L) C[(b & 0xff) + 1]++;
        for (int c = 1; c <= 256; c++) C[c] += C[c - 1];
        occ = new int[256][];
        for (int c = 0; c < 256; c++) if (C[c + 1] > C[c]) occ[c] = new int[n + 1];
        for (int j = 0; j < n; j++) for (int c = 0; c < 256; c++) if (occ[c] != null) occ[c][j + 1] = occ[c][j] + ((L[j] & 0xff) == c ? 1 : 0);
    }

    /** Backward search: the number of sorted rotations that begin with p. */
    static int fmCount(byte[] p) {
        int lo = 0, hi = occ[firstPresent()].length - 1;          // rows [lo, hi)
        for (int k = p.length - 1; k >= 0 && lo < hi; k--) {
            int c = p[k] & 0xff;
            fmSteps++;
            if (occ[c] == null) return 0;
            lo = C[c] + occ[c][lo];
            hi = C[c] + occ[c][hi];
        }
        return Math.max(0, hi - lo);
    }

    static int firstPresent() { for (int c = 0; c < 256; c++) if (occ[c] != null) return c; return 0; }

    /** Occurrences of p as a substring of the cyclic text (what rotations count). */
    static int scanCount(byte[] s, byte[] p) {
        int n = s.length, count = 0;
        for (int i = 0; i < n; i++) {
            int j = 0;
            while (j < p.length && s[(i + j) % n] == p[j]) j++;
            if (j == p.length) count++;
        }
        return count;
    }

    public static void main(String[] args) throws Exception {
        // ---- 1. abracadabra -----------------------------------------------------------------------------------------
        byte[] small = "abracadabra".getBytes("ISO-8859-1");
        int[] order = sortedRotations(small);
        StringJoiner rot = new StringJoiner(" ");
        for (int j : order) rot.add(new String(small, j, small.length - j, "ISO-8859-1") + new String(small, 0, j, "ISO-8859-1"));
        byte[] L = bwt(small);
        int I = lastIndex;
        check(Arrays.equals(inverse(L, I), small), "abracadabra comes back");
        System.out.printf("small: the rotations of abracadabra, sorted: %s ; last letters L = %s, the original is row I = %d ; L has %d runs of equal letters, the text %d ; inverting with the LF mapping gives %s%n",
                rot, new String(L, "ISO-8859-1"), I, runs(L), runs(small), new String(inverse(L, I), "ISO-8859-1"));

        // ---- 2. the field notes ------------------------------------------------------------------------------------
        byte[] text = Files.readAllBytes(Paths.get("corpus.txt"));
        int n = text.length;
        byte[] Lt = bwt(text);
        int It = lastIndex;
        check(Arrays.equals(inverse(Lt, It), text), "the field notes come back");
        int[] mtf = moveToFront(Lt);
        long zeros = 0, small4 = 0;
        for (int x : mtf) { if (x == 0) zeros++; if (x < 4) small4++; }
        long[] raw = new long[256];
        for (byte b : text) raw[b & 0xff]++;
        double huffRaw = (double) huffmanBits(raw) / n;
        double bwtBits = (double) blockBits(text) / n;
        Deflater d = new Deflater(9);
        d.setInput(text);
        d.finish();
        byte[] buf = new byte[n * 2];
        int deflated = d.deflate(buf);
        d.end();
        double deflateBits = 8.0 * deflated / n;
        check(bwtBits < huffRaw && bwtBits < deflateBits, "block sorting beats Huffman alone and Deflate on this text");
        // what sits before "he": the rotations beginning "he" are adjacent once sorted, and their last letters are these
        Map<Character, Integer> before = new TreeMap<>();
        int heCount = 0;
        for (int i = 1; i + 1 < n; i++) if (text[i] == 'h' && text[i + 1] == 'e') { before.merge((char) text[i - 1], 1, Integer::sum); heCount++; }
        List<Map.Entry<Character, Integer>> top = new ArrayList<>(before.entrySet());
        top.sort((x, y) -> y.getValue() - x.getValue());
        StringJoiner hj = new StringJoiner(", ");
        for (int k = 0; k < 4; k++) hj.add(String.format("%s %d", top.get(k).getKey() == ' ' ? "space" : String.valueOf(top.get(k).getKey()), top.get(k).getValue()));
        check(top.get(0).getKey() == 't', "t is the commonest letter before he");
        System.out.printf("context: in the field notes, %d places where \"he\" comes after another character ; the character before it: %s ; so in L the rows for rotations starting \"he\" form a block made mostly of t%n", heCount, hj);
        System.out.printf("notes: this book's field notes, %,d bytes ; runs of equal letters: %,d in the text, %,d in L ; after move-to-front, %.1f%% of the numbers are 0 and %.1f%% are below 4 ; bits per byte: Huffman's code on single bytes %.2f ; Era 6's LZ77 4.95 (from that program's output) ; Deflate (gzip's method, level 9, header included) %.2f ; Burrows-Wheeler, move-to-front, then Huffman %.2f%n",
                n, runs(text), runs(Lt), 100.0 * zeros / n, 100.0 * small4 / n, huffRaw, deflateBits, bwtBits);

        // ---- 3. block size -----------------------------------------------------------------------------------------
        StringJoiner bj = new StringJoiner(" ; ");
        double prev = Double.MAX_VALUE;
        for (int size : new int[]{250, 1_000, 4_000, n}) {
            long bits = 0;
            for (int start = 0; start < n; start += size) {
                byte[] block = Arrays.copyOfRange(text, start, Math.min(n, start + size));
                byte[] Lb = bwt(block);
                check(Arrays.equals(inverse(Lb, lastIndex), block), "every block comes back");
                bits += blockBits(block);
            }
            double bpb = (double) bits / n;
            check(bpb < prev, "bigger blocks compress better");
            prev = bpb;
            bj.add(String.format("blocks of %,d bytes: %.2f bits per byte", Math.min(size, n), bpb));
        }
        System.out.printf("blocks: the field notes cut into blocks, each transformed and coded on its own ; %s%n", bj);

        // ---- 4. counting with the FM index --------------------------------------------------------------------------
        buildIndex(Lt);
        StringJoiner fj = new StringJoiner(" ; ");
        for (String pat : new String[]{"the", "algorithm", "Era", " of the ", "Euclid", "quantum"}) {
            byte[] p = pat.getBytes("ISO-8859-1");
            fmSteps = 0;
            int fm = fmCount(p), scan = scanCount(text, p);
            check(fm == scan, "backward search counts what scanning counts: " + pat);
            fj.add(String.format("\"%s\": %d (%d steps)", pat.replace(' ', '_'), fm, fmSteps));
        }
        for (int t = 0; t < 500; t++) {                     // random pieces of the text, and random strings
            int len = 1 + below(12), at = below(n - len);
            byte[] p = t % 2 == 0 ? Arrays.copyOfRange(text, at, at + len) : randomBytes(len, 4);
            check(fmCount(p) == scanCount(text, p), "random pattern counts agree");
        }
        System.out.printf("fmindex: occurrences counted from L alone by backward search, one step per pattern letter, against scanning all %,d positions (_ is a space) ; %s ; 500 more patterns agree with scanning%n", n, fj);

        // ---- 5. round trips --------------------------------------------------------------------------------------
        int trips = 2000;
        for (int t = 0; t < trips; t++) {
            byte[] s = randomBytes(1 + below(300), 1 + below(26));
            byte[] Ls = bwt(s);
            check(Arrays.equals(inverse(Ls, lastIndex), s), "random string comes back");
        }
        System.out.printf("trips: %,d random strings (1 to 300 letters, alphabets of 1 to 26) transformed and inverted ; every one comes back exactly%n", trips);

        System.out.println("BurrowsWheeler: " + passed + " checks passed");
    }

    static byte[] randomBytes(int len, int alphabet) {
        byte[] s = new byte[len];
        for (int i = 0; i < len; i++) s[i] = (byte) ('a' + below(alphabet));
        return s;
    }
}
