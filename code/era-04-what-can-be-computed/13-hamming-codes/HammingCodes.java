import java.util.*;

/**
 * Era 4, topic 13: Hamming's error-correcting codes (1947-1950).
 *
 * HOW IT WORKS
 *   Number the positions of a code word 1, 2, 3, ... and put check bits at the positions 1, 2, 4, 8, ... (the powers
 *   of two); the other positions carry the message. The check bit at position 2^k makes the parity even over every
 *   position whose number has bit k set. When a word arrives with one bit flipped, exactly the checks that cover that
 *   position fail, and the failed checks, read as a binary number, spell the position: flip it back. With 7 positions,
 *   4 carry the message and 3 are checks (the (7,4) code). Every two code words differ in at least 3 places, so a
 *   single error leaves the word closer to the right code word than to any other. One more bit, the parity of the
 *   whole word, raises the distance to 4: single errors are corrected and double errors detected.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Builds the 16 code words of the (7,4) code and checks the distance between every pair.
 *   2. Checks that every 7-bit word is within one place of exactly one code word (a "perfect" code).
 *   3. Corrects every single error; shows that every double error is mis-corrected; then adds the overall parity bit
 *      and detects every double error.
 *   4. The longer codes (15,11), (31,26), (63,57), on random words with one error.
 *   5. A million 4-bit messages over a channel that flips 1 bit in 100: no code, Hamming's code, and sending each bit
 *      three times.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HammingCodes.java
 *   Expected output: expected-output.txt in this folder.
 */
public class HammingCodes {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** Encode data bits into a code word of n = 2^r - 1 positions; bit i of the result is position i + 1. */
    static long encode(long data, int r) {
        int n = (1 << r) - 1;
        long word = 0;
        int d = 0;
        for (int pos = 1; pos <= n; pos++) {
            if (Integer.bitCount(pos) == 1) continue;                     // a check position, filled below
            if ((data >> d & 1) == 1) word |= 1L << (pos - 1);
            d++;
        }
        for (int k = 0; k < r; k++) {
            int parity = 0;
            for (int pos = 1; pos <= n; pos++) if ((pos >> k & 1) == 1 && (word >> (pos - 1) & 1) == 1) parity ^= 1;
            if (parity == 1) word |= 1L << ((1 << k) - 1);
        }
        return word;
    }

    /** The syndrome: the failed checks read as a binary number, which is the position of a single error (0 = none). */
    static int syndrome(long word, int r) {
        int n = (1 << r) - 1, s = 0;
        for (int pos = 1; pos <= n; pos++) if ((word >> (pos - 1) & 1) == 1) s ^= pos;
        return s;
    }

    static long correct(long word, int r) {
        int s = syndrome(word, r);
        return s == 0 ? word : word ^ (1L << (s - 1));
    }

    static long dataOf(long word, int r) {
        int n = (1 << r) - 1, d = 0;
        long data = 0;
        for (int pos = 1; pos <= n; pos++) {
            if (Integer.bitCount(pos) == 1) continue;
            if ((word >> (pos - 1) & 1) == 1) data |= 1L << d;
            d++;
        }
        return data;
    }

    static String bits(long w, int n) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) sb.append((w >> i & 1) == 1 ? '1' : '0');      // position 1 first
        return sb.toString();
    }

    static long seed = 1950L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / 9007199254740992.0;
    }

    public static void main(String[] args) {
        // ---- 1. the sixteen code words ------------------------------------------------------------------------------------
        long[] cw = new long[16];
        StringJoiner list = new StringJoiner(" ");
        for (int m = 0; m < 16; m++) {
            cw[m] = encode(m, 3);
            check(syndrome(cw[m], 3) == 0 && dataOf(cw[m], 3) == m, "a code word passes every check and carries its message");
            list.add(bits(cw[m], 7));
        }
        int minDist = 7, pairs = 0;
        for (int a = 0; a < 16; a++)
            for (int b = a + 1; b < 16; b++) { minDist = Math.min(minDist, Long.bitCount(cw[a] ^ cw[b])); pairs++; }
        check(minDist == 3, "minimum distance 3");
        System.out.printf("code: the 16 code words of the (7,4) code, positions 1 to 7, checks at 1, 2 and 4: %s ; every two of them differ in at least %d places (%d pairs)%n",
                list, minDist, pairs);

        // ---- 2. a perfect code ------------------------------------------------------------------------------------------------
        int[] near = new int[128];
        for (long c : cw) {
            near[(int) c]++;
            for (int i = 0; i < 7; i++) near[(int) (c ^ (1L << i))]++;
        }
        for (int w = 0; w < 128; w++) check(near[w] == 1, "each 7-bit word is within one place of exactly one code word");
        System.out.println("perfect: each code word with its 7 one-bit neighbours makes a ball of 8 words ; 16 balls x 8 = 128 = 2^7: every 7-bit word lies in exactly one ball");

        // ---- 3. single and double errors -------------------------------------------------------------------------------------
        int singles = 0;
        for (int m = 0; m < 16; m++)
            for (int i = 0; i < 7; i++) {
                long received = cw[m] ^ (1L << i);
                check(syndrome(received, 3) == i + 1, "the failed checks spell the position");
                check(correct(received, 3) == cw[m], "corrected");
                singles++;
            }
        int doubles = 0, miscorrected = 0;
        for (int m = 0; m < 16; m++)
            for (int i = 0; i < 7; i++)
                for (int j = i + 1; j < 7; j++) {
                    long received = cw[m] ^ (1L << i) ^ (1L << j);
                    doubles++;
                    if (correct(received, 3) != cw[m]) miscorrected++;
                }
        check(miscorrected == doubles, "the (7,4) code mis-corrects every double error");
        // the eighth bit: parity of the whole word (Hamming's distance-4 code)
        int singles8 = 0, doubles8 = 0, detected8 = 0;
        for (int m = 0; m < 16; m++) {
            long w8 = cw[m] | ((long) (Long.bitCount(cw[m]) & 1) << 7);
            for (int i = 0; i < 8; i++) {
                long r1 = w8 ^ (1L << i);
                boolean overallOdd = (Long.bitCount(r1) & 1) == 1;
                int s = syndrome(r1 & 127, 3);
                long fixed = !overallOdd ? r1 : (s == 0 ? r1 ^ (1L << 7) : r1 ^ (1L << (s - 1)));
                check(fixed == w8, "single error corrected with the eighth bit");
                singles8++;
                for (int j = i + 1; j < 8; j++) {
                    long r2 = w8 ^ (1L << i) ^ (1L << j);
                    boolean odd = (Long.bitCount(r2) & 1) == 1, flagged = !odd && syndrome(r2 & 127, 3) != 0;
                    check(flagged, "double error detected");
                    doubles8++;
                    detected8++;
                }
            }
        }
        System.out.printf("errors: all %d single errors corrected, the failed checks spelling each position ; all %d double errors fool the (7,4) code into a wrong correction ; with an eighth bit for the parity of the whole word, all %d single errors are corrected and all %d double errors detected%n",
                singles, doubles, singles8, detected8);

        // ---- 4. longer codes ---------------------------------------------------------------------------------------------------
        StringJoiner fam = new StringJoiner(" ; ");
        for (int r = 3; r <= 6; r++) {
            int n = (1 << r) - 1, k = n - r, trials = 20000;
            for (int t = 0; t < trials; t++) {
                long data = 0;
                for (int i = 0; i < k; i++) if (uniform() < 0.5) data |= 1L << i;
                long w = encode(data, r);
                int flip = (int) (uniform() * n);
                long got = correct(w ^ (1L << flip), r);
                check(got == w && dataOf(got, r) == data, "single error corrected in a longer code");
            }
            fam.add(String.format("(%d,%d): %d checks for %d message bits, %.0f%% of the bits carry the message", n, k, r, k, 100.0 * k / n));
        }
        System.out.printf("family: %s ; each corrected one random error in each of 20000 random words%n", fam);

        // ---- 5. a noisy channel ----------------------------------------------------------------------------------------------
        double p = 0.01;
        int messages = 1_000_000;
        int wrongPlain = 0, wrongHamming = 0, wrongTriple = 0;
        for (int t = 0; t < messages; t++) {
            int m = (int) (uniform() * 16);
            // no code: 4 bits
            int plain = m;
            for (int i = 0; i < 4; i++) if (uniform() < p) plain ^= 1 << i;
            if (plain != m) wrongPlain++;
            // Hamming (7,4): 7 bits
            long w = cw[m];
            for (int i = 0; i < 7; i++) if (uniform() < p) w ^= 1L << i;
            if (dataOf(correct(w, 3), 3) != m) wrongHamming++;
            // each bit three times, majority vote: 12 bits
            int tri = 0;
            for (int i = 0; i < 4; i++) {
                int ones = 0, bit = m >> i & 1;
                for (int c = 0; c < 3; c++) ones += (uniform() < p ? 1 - bit : bit);
                if (ones >= 2) tri |= 1 << i;
            }
            if (tri != m) wrongTriple++;
        }
        double expectPlain = 1 - Math.pow(1 - p, 4), expectHamming = 1 - Math.pow(1 - p, 7) - 7 * p * Math.pow(1 - p, 6);
        check(Math.abs((double) wrongPlain / messages - expectPlain) < 0.002, "uncoded error rate as expected");
        check(Math.abs((double) wrongHamming / messages - expectHamming) < 0.0005, "Hamming error rate as expected");
        check(wrongHamming * 10 < wrongPlain, "Hamming's code cuts the errors more than tenfold");
        System.out.printf("channel: %,d four-bit messages, each bit flipped with probability %.2f ; no code (4 bits sent): %,d wrong (%.3f%%, expected %.3f%%) ; Hamming (7,4), 7 bits: %,d wrong (%.3f%%, expected %.3f%%) ; each bit three times, 12 bits: %,d wrong (%.3f%%)%n",
                messages, p, wrongPlain, 100.0 * wrongPlain / messages, 100 * expectPlain, wrongHamming, 100.0 * wrongHamming / messages, 100 * expectHamming,
                wrongTriple, 100.0 * wrongTriple / messages);

        System.out.println("HammingCodes: " + passed + " checks passed");
    }
}
