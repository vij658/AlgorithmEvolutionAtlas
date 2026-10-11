import java.util.*;

/**
 * Era 3, topic 6: binary arithmetic (Harriot c. 1601-1605, unpublished; Caramuel 1670; Leibniz 1679 and 1703).
 *
 * HOW IT WORKS
 *   Write numbers with two digits, 0 and 1, where each place is worth twice the place to its right: 1101101 means
 *   64 + 32 + 8 + 4 + 1 = 109. To convert, halve again and again and keep the remainders. Addition needs only
 *   "1 + 1 = 10"; multiplication needs no table at all, because each digit of the multiplier is 0 or 1: add a shifted
 *   copy of the number, or don't. That is the Egyptian scribes' doubling (Era 1, topic 5) written as a numeral.
 *   The price is length: a binary numeral is about 3.32 times as long as the decimal one.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Converts Harriot's 1101101 = 109 both ways, and checks conversion on every number below 2^20.
 *   2. Counts the facts to memorise: addition and multiplication tables in base 10 and base 2.
 *   3. Adds and multiplies 100,000 random pairs bit by bit (shift and add), and counts the work.
 *   4. Shows Egyptian doubling as binary multiplication.
 *   5. Measures the price: digits per number in base 2 and base 10.
 *   6. Full circle: Java prints Harriot's numeral, and stores negative numbers as complements (topic 3).
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BinaryArithmetic.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BinaryArithmetic {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** Decimal to binary by repeated halving: the remainders, read from the last to the first. */
    static String toBinary(long n) {
        if (n == 0) return "0";
        StringBuilder s = new StringBuilder();
        while (n > 0) { s.append(n % 2); n /= 2; }
        return s.reverse().toString();
    }

    /** Binary to decimal: double and add, digit by digit from the left. */
    static long fromBinary(String b) {
        long v = 0;
        for (char c : b.toCharArray()) v = 2 * v + (c - '0');
        return v;
    }

    static long bitOps;

    /** Add two binary numerals digit by digit with the one rule 1 + 1 = 10. */
    static String add(String a, String b) {
        StringBuilder s = new StringBuilder();
        int i = a.length() - 1, j = b.length() - 1, carry = 0;
        while (i >= 0 || j >= 0 || carry > 0) {
            int t = carry + (i >= 0 ? a.charAt(i--) - '0' : 0) + (j >= 0 ? b.charAt(j--) - '0' : 0);
            s.append(t % 2);
            carry = t / 2;
            bitOps++;
        }
        return s.reverse().toString();
    }

    /** Multiply by shift and add: for each 1 in b, add a shifted copy of a. No multiplication table is used. */
    static String multiply(String a, String b, int[] adds) {
        String acc = "0";
        for (int k = 0; k < b.length(); k++) {
            if (b.charAt(b.length() - 1 - k) == '1') {
                acc = add(acc, a + "0".repeat(k));
                adds[0]++;
            }
        }
        return acc;
    }

    public static void main(String[] args) {
        // ---- 1. Harriot's example ------------------------------------------------------------------------------------
        String h = "1101101";
        long hv = fromBinary(h);
        check(hv == 109 && toBinary(109).equals(h), "1101101 = 109 both ways");
        StringJoiner halve = new StringJoiner(", ");
        long n = 109;
        while (n > 0) { halve.add(n + " r " + (n % 2)); n /= 2; }
        StringJoiner places = new StringJoiner(" + ");
        for (int i = 0; i < h.length(); i++) if (h.charAt(i) == '1') places.add(String.valueOf(1L << (h.length() - 1 - i)));
        System.out.printf("harriot: 1101101 = %s = %d ; back again by halving 109: %s ; reading the remainders upward gives %s%n", places, hv, halve, toBinary(109));
        for (long v = 0; v < (1L << 20); v++) check(fromBinary(toBinary(v)) == v && toBinary(v).equals(Long.toBinaryString(v)), "conversion both ways");
        System.out.printf("convert: every number below 2^20 = %,d converted to binary and back, matching Java's own conversion%n", 1 << 20);

        // ---- 2. the facts to learn by heart ----------------------------------------------------------------------------
        // ordered pairs of single digits, and the distinct facts once a + b = b + a is used
        int dec = 10 * 10, decSym = 10 * 11 / 2, bin = 2 * 2, binSym = 2 * 3 / 2;
        // facts that are not trivial: multiplication facts with neither factor 0 or 1
        int decHard = 8 * 9 / 2, binHard = 0;
        System.out.printf("tables: base 10 has %d single-digit sums and %d products (%d each, counting a + b and b + a once), of which %d products have no factor 0 or 1 ; base 2 has %d of each (%d counted once), and every product has a factor 0 or 1: 0 x 0 = 0, 0 x 1 = 0, 1 x 1 = 1, and the only sum that carries is 1 + 1 = 10%n",
                dec, dec, decSym, decHard, bin, binSym);
        check(binHard == 0, "nothing to memorise in base 2");

        // ---- 3. random sums and products, bit by bit --------------------------------------------------------------------
        Random rnd = new Random(1703);
        long totalAdds = 0, totalBits = 0;
        int N = 100000;
        for (int t = 0; t < N; t++) {
            long a = 1 + rnd.nextInt(1 << 20), b = 1 + rnd.nextInt(1 << 20);
            String sa = toBinary(a), sb = toBinary(b);
            check(fromBinary(add(sa, sb)) == a + b, "binary addition");
            int[] adds = {0};
            check(fromBinary(multiply(sa, sb, adds)) == a * b, "shift-and-add multiplication");
            totalAdds += adds[0]; totalBits += sb.length();
        }
        System.out.printf("random: %,d pairs of numbers below 2^20 added and multiplied bit by bit, all correct ; a product needs one shifted addition for each 1 in the multiplier: on average %.2f additions for multipliers of %.2f bits%n",
                N, totalAdds / (double) N, totalBits / (double) N);

        // ---- 4. Egyptian doubling is binary multiplication ----------------------------------------------------------------
        long ea = 13, eb = 21;
        StringJoiner rows = new StringJoiner(" ; ");
        long acc = 0, p = 1, dbl = eb;
        StringJoiner ticked = new StringJoiner(" + ");
        while (p <= ea) {
            boolean tick = (ea & p) != 0;
            rows.add(String.format("%d: %d%s", p, dbl, tick ? " (ticked)" : ""));
            if (tick) { acc += dbl; ticked.add(String.valueOf(dbl)); }
            p *= 2; dbl *= 2;
        }
        check(acc == ea * eb && toBinary(ea).equals("1101"), "13 x 21 by doubling, ticking the rows of 1101");
        System.out.printf("egypt: %d x %d by doubling: %s ; ticked rows %s = %d ; the ticks, read from the bottom, are %s, which is %d in binary%n",
                ea, eb, rows, ticked, acc, toBinary(ea), ea);

        // ---- 5. the price: length ------------------------------------------------------------------------------------------
        long bd = 0, dd = 0;
        int M = 1_000_000;
        for (int v = 1; v <= M; v++) { bd += toBinary(v).length(); dd += String.valueOf(v).length(); }
        double ratio = bd / (double) dd;
        check(Math.abs(ratio - 3.32) < 0.2, "binary numerals are about 3.3 times as long");
        System.out.printf("length: the numbers 1 to %,d take %,d decimal digits and %,d binary digits, %.2f times as many ; log2(10) = %.4f%n",
                M, dd, bd, ratio, Math.log(10) / Math.log(2));

        // ---- 6. full circle -----------------------------------------------------------------------------------------------
        String javaBin = Integer.toBinaryString(109);
        byte neg = (byte) -109;
        String negBits = String.format("%8s", Integer.toBinaryString(neg & 0xFF)).replace(' ', '0');
        String onesComp = String.format("%8s", Integer.toBinaryString(~109 & 0xFF)).replace(' ', '0');
        check(javaBin.equals("1101101") && (neg & 0xFF) == 256 - 109 && fromBinary(onesComp) + 1 == (neg & 0xFF), "two's complement is the ones' complement plus one");
        System.out.printf("circle: Integer.toBinaryString(109) = %s ; -109 in an 8-bit byte is %s = 256 - 109 = %d, the ones' complement %s plus 1 ; there are 2^6 = %d six-digit binary numbers, as many as the hexagrams in Bouvet's figure%n",
                javaBin, negBits, neg & 0xFF, onesComp, 1 << 6);

        System.out.printf("BinaryArithmetic: %d checks passed%n", passed);
    }
}
