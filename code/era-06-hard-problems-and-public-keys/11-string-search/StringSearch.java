import java.nio.file.*;
import java.util.*;

/**
 * Era 6, topic 11: fast string searching (Knuth, Morris and Pratt; Boyer and Moore; both 1977).
 *
 * HOW IT WORKS
 *   The simple way to find a pattern of length m in a text of length n tries every starting position and compares
 *   letter by letter; on unlucky texts (aaaa...ab) that is about m times n comparisons, and on a mismatch it moves
 *   back in the text to try the next position.
 *   Knuth, Morris and Pratt never move back. When a mismatch comes after j matched letters, those j letters are known:
 *   they are the first j letters of the pattern. A table computed once from the pattern ("next") says how much of the
 *   pattern can still be matched at that point. Each letter of the text is read once, and the whole search takes
 *   time proportional to m + n.
 *   Boyer and Moore compare from the right end of the pattern. If the text letter there does not occur in the pattern
 *   at all, the pattern can jump m places at once. Two tables say how far to shift: one by the mismatched letter
 *   (delta1), one by the matched ending (delta2). On ordinary text most letters are never looked at: the longer the
 *   pattern, the faster the search.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The simple method on an unlucky text: comparisons and backing up.
 *   2. The "next" table of Knuth, Morris and Pratt for a sample pattern, and a search with it.
 *   3. Boyer and Moore's two tables for a sample pattern.
 *   4. All three methods on 20,000 random searches: identical answers.
 *   5. Letters examined per letter of text passed, for patterns of length 1 to 14, in English (this book's own
 *      field notes), in random binary text, and in random text over 100 symbols.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step; corpus.txt must be in the current folder)
 *   java StringSearch.java
 *   Expected output: expected-output.txt in this folder.
 */
public class StringSearch {
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

    static long looks, backups;

    static List<Integer> simple(String t, String p) {
        List<Integer> found = new ArrayList<>();
        int n = t.length(), m = p.length();
        for (int s = 0; s + m <= n; s++) {
            int j = 0;
            while (j < m) { looks++; if (t.charAt(s + j) != p.charAt(j)) break; j++; }
            if (j == m) found.add(s);
            if (j > 0) backups++;                       // the next try starts behind letters already read
        }
        return found;
    }

    /** next[j]: after j letters matched and a mismatch, how many letters of the pattern are still matched. */
    static int[] failure(String p) {
        int m = p.length();
        int[] f = new int[m + 1];
        f[0] = -1;
        int k = -1;
        for (int j = 0; j < m; j++) {
            while (k >= 0 && p.charAt(k) != p.charAt(j)) k = f[k];
            k++;
            f[j + 1] = k;
        }
        return f;
    }

    static List<Integer> kmp(String t, String p) {
        List<Integer> found = new ArrayList<>();
        int[] f = failure(p);
        int m = p.length(), j = 0;
        for (int i = 0; i < t.length(); i++) {             // i only moves forward
            char c = t.charAt(i);
            while (true) {
                looks++;
                if (p.charAt(j) == c) { j++; break; }
                j = f[j];
                if (j < 0) { j = 0; break; }
            }
            if (j == m) { found.add(i - m + 1); j = f[m]; }
        }
        return found;
    }

    static int[] delta1(String p) {
        int m = p.length();
        int[] d = new int[65536];
        Arrays.fill(d, m);
        for (int j = 0; j < m - 1; j++) d[p.charAt(j)] = m - 1 - j;
        return d;
    }

    /** delta2[j]: how far to shift (measured at the pattern's right end) after a mismatch at position j. */
    static int[] delta2(String p) {
        int m = p.length();
        int[] d = new int[m], suff = new int[m];
        suff[m - 1] = m;
        for (int i = m - 2; i >= 0; i--) {
            int k = 0;
            while (k <= i && p.charAt(i - k) == p.charAt(m - 1 - k)) k++;
            suff[i] = k;                                  // longest common suffix of p[0..i] and p
        }
        Arrays.fill(d, m);
        int j = 0;
        for (int i = m - 1; i >= 0; i--)
            if (suff[i] == i + 1) for (; j < m - 1 - i; j++) if (d[j] == m) d[j] = m - 1 - i;
        for (int i = 0; i <= m - 2; i++) d[m - 1 - suff[i]] = m - 1 - i;
        int[] shift = new int[m];
        for (int i = 0; i < m; i++) shift[i] = d[i] + (m - 1 - i);   // as an advance of the text position
        return shift;
    }

    static List<Integer> boyerMoore(String t, String p) {
        List<Integer> found = new ArrayList<>();
        int n = t.length(), m = p.length();
        int[] d1 = delta1(p), d2 = delta2(p);
        int i = m - 1;                                     // text position under the pattern's last letter
        while (i < n) {
            int j = m - 1, k = i;
            while (true) {
                looks++;
                if (t.charAt(k) != p.charAt(j)) break;
                if (j == 0) break;
                j--; k--;
            }
            if (j == 0 && t.charAt(k) == p.charAt(0)) {
                found.add(k);
                i += m - failure(p)[m];                    // shift by the pattern's period
                continue;
            }
            i = Math.max(k + d1[t.charAt(k)], i + d2[j] - (m - 1 - j));
            if (i <= k) i = k + 1;
        }
        return found;
    }

    static String randomText(int n, int alphabet, char base) {
        StringBuilder sb = new StringBuilder(n);
        for (int i = 0; i < n; i++) sb.append((char) (base + rnd(alphabet)));
        return sb.toString();
    }

    public static void main(String[] args) throws Exception {
        // ---- 1. the simple method on an unlucky text --------------------------------------------------------------------
        String bad = "a".repeat(9999) + "b", pat = "a".repeat(49) + "b";
        looks = backups = 0;
        List<Integer> s1 = simple(bad, pat);
        long simpleLooks = looks, simpleBack = backups;
        looks = 0;
        List<Integer> k1 = kmp(bad, pat);
        long kmpLooks = looks;
        looks = 0;
        List<Integer> b1 = boyerMoore(bad, pat);
        long bmLooks = looks;
        check(s1.equals(k1) && k1.equals(b1) && s1.size() == 1, "one match at the end");
        check(kmpLooks <= 2L * bad.length(), "KMP makes at most 2n comparisons");
        System.out.printf("unlucky: text of 9,999 a's then b, pattern of 49 a's then b ; the simple method makes %,d comparisons and backs up in the text %,d times ; Knuth-Morris-Pratt %,d comparisons, never backing up ; Boyer-Moore %,d%n",
                simpleLooks, simpleBack, kmpLooks, bmLooks);

        // ---- 2. the next table ----------------------------------------------------------------------------------------
        String p2 = "abcabcacab", t2 = "babcbabcabcaabcabcabcacabc";
        int[] f2 = failure(p2);
        StringJoiner fj = new StringJoiner(" ");
        for (int j = 1; j <= p2.length(); j++) fj.add(String.valueOf(f2[j]));
        looks = 0;
        List<Integer> k2 = kmp(t2, p2);
        long kmpSample = looks;
        check(k2.equals(simple(t2, p2)), "KMP agrees on the sample");
        System.out.printf("next: pattern %s ; after j = 1 ... %d letters matched, the longest proper ending of those j letters that is also a beginning of the pattern has length: %s ; text %s ; found at position %s with %d comparisons for %d letters of text%n",
                p2, p2.length(), fj, t2, k2, kmpSample, t2.length());

        // ---- 3. Boyer and Moore's tables --------------------------------------------------------------------------------
        String p3 = "AT-THAT";
        int[] d1 = delta1(p3), d2 = delta2(p3);
        StringJoiner d1j = new StringJoiner(", "), d2j = new StringJoiner(" ");
        for (char c : "ATH-".toCharArray()) d1j.add(c + " " + d1[c]);
        d1j.add("any other letter " + p3.length());
        for (int j = 0; j < p3.length(); j++) d2j.add(String.valueOf(d2[j]));
        String t3 = "WHICH-FINALLY-HALTS.--AT-THAT-POINT";
        looks = 0;
        List<Integer> b3 = boyerMoore(t3, p3);
        long bmSample = looks;
        check(b3.equals(simple(t3, p3)), "BM agrees on the sample");
        check(bmSample < t3.length(), "Boyer-Moore looks at fewer letters than the text has");
        System.out.printf("tables: pattern %s ; delta1 (jump by the text letter at a mismatch): %s ; delta2 (advance after a mismatch at pattern position 1 ... %d, by the matched ending): %s ; text %s ; found at position %s after looking at %d of its %d letters%n",
                p3, d1j, p3.length(), d2j, t3, b3, bmSample, t3.length());

        // ---- 4. agreement ---------------------------------------------------------------------------------------------
        int agree = 0, matches = 0;
        for (int t = 0; t < 20000; t++) {
            int alpha = 1 + rnd(4);
            String text = randomText(1 + rnd(300), alpha, 'a'), p = randomText(1 + rnd(8), alpha, 'a');
            List<Integer> a = simple(text, p), b = kmp(text, p), c = boyerMoore(text, p);
            check(a.equals(b) && b.equals(c), "agreement on random search " + t);
            agree++;
            matches += a.size();
        }
        System.out.printf("agree: %,d random searches (texts of up to 300 letters over alphabets of 1 to 4 letters, patterns of 1 to 8) ; the simple method, Knuth-Morris-Pratt and Boyer-Moore report the same %,d matches%n", agree, matches);

        // ---- 5. letters examined per letter passed ------------------------------------------------------------------
        String english = new String(Files.readAllBytes(Paths.get("corpus.txt")), "UTF-8").replaceAll("\\s+", " ");
        String binary = randomText(english.length(), 2, '0'), hundred = randomText(english.length(), 100, (char) 200);
        String[] names = {"English", "binary", "100 symbols"};
        String[] texts = {english, binary, hundred};
        StringJoiner rj = new StringJoiner(" ; ");
        double eng5 = 0, eng14 = 0;
        for (int which = 0; which < 3; which++) {
            String text = texts[which];
            StringJoiner row = new StringJoiner(" ");
            for (int m = 1; m <= 14; m++) {
                long sumLooks = 0, sumPassed = 0, kmpL = 0;
                for (int trial = 0; trial < 300; trial++) {
                    int at = rnd(text.length() - m);
                    String p = text.substring(at, at + m);
                    looks = 0;
                    List<Integer> found = boyerMoore(text, p);
                    int first = found.get(0);
                    // count only the work up to the first match, as Boyer and Moore did
                    looks = 0;
                    boyerMoore(text.substring(0, first + m), p);
                    sumLooks += looks;
                    sumPassed += first + m;
                    looks = 0;
                    kmp(text.substring(0, first + m), p);
                    kmpL += looks;
                }
                double r = (double) sumLooks / sumPassed;
                if (which == 0 && m == 5) eng5 = r;
                if (which == 0 && m == 14) eng14 = r;
                if (m == 1 || m == 2 || m == 5 || m == 10 || m == 14) row.add(String.format("m=%d: %.2f", m, r));
                if (m == 5) check((double) kmpL / sumPassed >= 1.0, "KMP looks at every letter at least once");
            }
            rj.add(names[which] + " " + row);
        }
        check(eng5 < 0.4 && eng14 < eng5, "on English, Boyer-Moore skips most letters, more as patterns grow");
        System.out.printf("speed: Boyer-Moore, letters examined per letter of text passed before the first match, 300 random patterns taken from each text for each length m (Knuth-Morris-Pratt always examines at least 1) ; %s ; in English, %.2f at m = 5 and %.2f at m = 14 ; texts of %,d letters%n",
                rj, eng5, eng14, english.length());

        System.out.println("StringSearch: " + passed + " checks passed");
    }
}
