import java.math.BigInteger;
import java.util.*;

/**
 * Era 1, topic 3: Babylonian place value and reciprocal tables (base 60; place value probably from the Ur III period,
 * c. 2100 BCE; Old Babylonian school tables, c. 1800 BCE).
 *
 * HOW IT WORKS
 *   A number is written as a row of base-60 digits, and each digit with just two signs: a vertical wedge for 1 and a
 *   corner wedge for 10 (so 59 is five corner wedges and nine vertical ones). The same digit means 1, 60 or 3,600
 *   depending only on where it stands. Old Babylonian scribes had no zero for an empty place and no mark for where the
 *   whole part ends, so readers relied on context.
 *   To divide, a scribe looked up the reciprocal of the divisor in a table and multiplied: a / b = a x (1/b). The
 *   standard table lists the "regular" numbers, those whose only prime factors are 2, 3 and 5, because exactly those
 *   have reciprocals that end in base 60.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Converts to and from base 60, counts the wedges each number needs, and measures how many numbers look alike
 *      when there is no zero and no point.
 *   2. Rebuilds the standard reciprocal table and checks it, entry by entry, against the table as transcribed by
 *      Duncan Melville; checks that it lists exactly the regular numbers from 2 to 81; shows the endless reciprocals
 *      of the numbers it skips; and divides by multiplying with reciprocals.
 *   3. Rebuilds the first row of Plimpton 322 from the reciprocal pair 2;24 and 0;25.
 *   4. Full circle: divides by a constant the way compilers do since Granlund and Montgomery (1994), by multiplying
 *      with a precomputed reciprocal, and checks it against ordinary division.
 *   Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BabylonianPlaceValue.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BabylonianPlaceValue {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // 1. Base 60 and the wedges
    // ----------------------------------------------------------------------------------------------------

    /** The base-60 digits of n, largest place first. */
    static int[] sexagesimal(long n) {
        if (n == 0) return new int[]{0};
        Deque<Integer> d = new ArrayDeque<>();
        while (n > 0) { d.push((int) (n % 60)); n /= 60; }
        return d.stream().mapToInt(Integer::intValue).toArray();
    }

    static long fromSexagesimal(int[] digits) {
        long v = 0;
        for (int d : digits) v = v * 60 + d;
        return v;
    }

    /** Write digits the modern way: 1,24,51,10. */
    static String show(int[] digits) {
        StringJoiner j = new StringJoiner(",");
        for (int d : digits) j.add(Integer.toString(d));
        return j.toString();
    }

    /** Wedges for one digit: a corner wedge per ten, a vertical wedge per one. */
    static int wedges(int digit) { return digit / 10 + digit % 10; }

    static int wedges(long n) { return Arrays.stream(sexagesimal(n)).map(BabylonianPlaceValue::wedges).sum(); }

    static int egyptianSigns(long n) {
        int s = 0;
        for (char c : Long.toString(n).toCharArray()) s += c - '0';
        return s;
    }

    /** How a number looks with no point: trailing empty places cannot be seen, so 1 and 60 look the same. */
    static String lookNoPoint(long n) {
        int[] d = sexagesimal(n);
        int end = d.length;
        while (end > 1 && d[end - 1] == 0) end--;
        return show(Arrays.copyOf(d, end));
    }

    /** How a number looks with no point and no zero: empty places vanish everywhere, so 61 and 3,601 look the same. */
    static String lookNoZero(long n) {
        return show(Arrays.stream(sexagesimal(n)).filter(x -> x != 0).toArray());
    }

    // ----------------------------------------------------------------------------------------------------
    // 2. Reciprocals
    // ----------------------------------------------------------------------------------------------------

    static boolean isRegular(long n) {
        if (n <= 0) return false;
        for (int p : new int[]{2, 3, 5}) while (n % p == 0) n /= p;
        return n == 1;
    }

    /**
     * The reciprocal of a regular number as base-60 digits, written the Babylonian way with no point: 1/8 = 0;7,30 is
     * written 7,30. Find the smallest power 60^j that n divides; the digits of 60^j / n are the reciprocal.
     */
    static int[] reciprocal(long n) {
        if (!isRegular(n)) throw new IllegalArgumentException(n + " is not regular");
        BigInteger sixty = BigInteger.valueOf(60), p = BigInteger.ONE, N = BigInteger.valueOf(n);
        while (!p.mod(N).equals(BigInteger.ZERO)) p = p.multiply(sixty);
        BigInteger k = p.divide(N);
        List<Integer> d = new ArrayList<>();
        while (k.signum() > 0) { d.add(0, k.mod(sixty).intValue()); k = k.divide(sixty); }
        int[] out = d.stream().mapToInt(Integer::intValue).toArray();
        int end = out.length;
        while (end > 1 && out[end - 1] == 0) end--;                      // a floating number: trailing zeros unseen
        return Arrays.copyOf(out, end);
    }

    /** The first `count` base-60 digits after the point of 1/n, and the length of the repeating cycle. */
    static int[] expansion(int n, int count) {
        int[] d = new int[count];
        int r = 1;
        for (int i = 0; i < count; i++) { r *= 60; d[i] = r / n; r %= n; }
        return d;
    }

    static int period(int n) {
        Map<Integer, Integer> seen = new HashMap<>();
        int r = 1 % n, i = 0;
        while (r != 0 && !seen.containsKey(r)) { seen.put(r, i++); r = r * 60 % n; }
        return r == 0 ? 0 : i - seen.get(r);
    }

    /** The standard Old Babylonian reciprocal table, as transcribed by Duncan Melville (St. Lawrence University). */
    static final String[] MELVILLE = ("2-30, 3-20, 4-15, 5-12, 6-10, 8-7,30, 9-6,40, 10-6, 12-5, 15-4, 16-3,45, 18-3,20, 20-3, "
            + "24-2,30, 25-2,24, 27-2,13,20, 30-2, 32-1,52,30, 36-1,40, 40-1,30, 45-1,20, 48-1,15, 50-1,12, 54-1,6,40, "
            + "1-1, 1,4-56,15, 1,12-50, 1,15-48, 1,20-45, 1,21-44,26,40").split(", ");

    // ----------------------------------------------------------------------------------------------------
    // 4. Division by a constant, the compiler's way (Granlund and Montgomery, 1994)
    // ----------------------------------------------------------------------------------------------------

    /** The precomputed "reciprocal" for dividing 32-bit numbers by d: m = ceil(2^(32 + l) / d), l = ceil(log2 d). */
    static long[] magic(long d) {
        int l = 64 - Long.numberOfLeadingZeros(d - 1);                     // ceil(log2 d); 0 for d = 1
        BigInteger two = BigInteger.ONE.shiftLeft(32 + l), D = BigInteger.valueOf(d);
        BigInteger[] qr = two.divideAndRemainder(D);
        BigInteger m = qr[1].signum() == 0 ? qr[0] : qr[0].add(BigInteger.ONE);
        return new long[]{m.longValueExact(), 32 + l};
    }

    /** floor(n / d) for 0 <= n < 2^32, by one multiplication and a shift: (n x m) >> shift. No division. */
    static long divideByMagic(long n, long m, int shift) {
        long hi = Math.multiplyHigh(n, m), lo = n * m;                    // the 128-bit product n x m
        return (hi << (64 - shift)) | (lo >>> shift);                      // shift is between 32 and 63
    }

    // ----------------------------------------------------------------------------------------------------

    public static void main(String[] args) {
        // 1. base 60 and wedges
        for (long n : new long[]{1, 59, 60, 61, 3601, 4622, 9999, 216000}) {
            int[] d = sexagesimal(n);
            check(fromSexagesimal(d) == n, "base 60 round trip");
            System.out.printf("sexa %d: digits=%s wedges=%d egyptian-signs=%d%n", n, show(d), wedges(n), egyptianSigns(n));
        }
        long sumW = 0, sumE = 0;
        int worstW = 0;
        long worstAt = 0;
        for (long n = 1; n <= 9999; n++) {
            int w = wedges(n);
            sumW += w;
            sumE += egyptianSigns(n);
            if (w > worstW) { worstW = w; worstAt = n; }
        }
        System.out.printf("average 1-9999: wedges=%.2f egyptian-signs=%.2f most-wedges=%d at %d (%s)%n", sumW / 9999.0, sumE / 9999.0,
                worstW, worstAt, show(sexagesimal(worstAt)));
        check(lookNoPoint(1).equals(lookNoPoint(60)) && lookNoPoint(60).equals(lookNoPoint(3600)), "1, 60 and 3,600 look the same");
        check(lookNoZero(61).equals(lookNoZero(3601)), "61 and 3,601 look the same without zero");

        long limit = 216_000;                                              // 60^3
        Map<String, Integer> byPoint = new HashMap<>(), byZero = new HashMap<>();
        for (long n = 1; n < limit; n++) {
            byPoint.merge(lookNoPoint(n), 1, Integer::sum);
            byZero.merge(lookNoZero(n), 1, Integer::sum);
        }
        long sharedPoint = 0, sharedZero = 0;
        int biggest = 0;
        String biggestLook = "";
        for (long n = 1; n < limit; n++) {
            if (byPoint.get(lookNoPoint(n)) > 1) sharedPoint++;
            if (byZero.get(lookNoZero(n)) > 1) sharedZero++;
        }
        for (Map.Entry<String, Integer> e : byZero.entrySet())
            if (e.getValue() > biggest || (e.getValue() == biggest && e.getKey().compareTo(biggestLook) < 0)) { biggest = e.getValue(); biggestLook = e.getKey(); }
        System.out.printf("look below %d: no point: %d numbers look like another; no point and no zero: %d; largest look-alike group %d numbers all written %s%n",
                limit, sharedPoint, sharedZero, biggest, biggestLook);
        System.out.printf("look examples: 1 and 60 and 3600 are all written %s; 61 and 3601 are both written %s without a zero%n", lookNoPoint(60), lookNoZero(3601));

        // 2. the reciprocal table
        int matched = 0;
        List<Long> heads = new ArrayList<>();
        for (String entry : MELVILLE) {
            String[] parts = entry.split("-");
            int[] headDigits = Arrays.stream(parts[0].split(",")).mapToInt(Integer::parseInt).toArray();
            long head = fromSexagesimal(headDigits);
            // the table is in increasing order and its numbers float: the "1" after 54 is 1,0 = 60
            while (!heads.isEmpty() && head < heads.get(heads.size() - 1)) head *= 60;
            heads.add(head);
            String recip = show(reciprocal(head));
            check(recip.equals(parts[1]), "reciprocal of " + parts[0] + " is " + parts[1]);
            matched++;
            System.out.printf("table %s: reciprocal=%s head=%d%n", parts[0], recip, head);
        }
        System.out.printf("tablecheck: %d of %d entries of the standard table recomputed exactly%n", matched, MELVILLE.length);
        List<Long> regular = new ArrayList<>(), skipped = new ArrayList<>();
        for (long n = 2; n <= 81; n++) (isRegular(n) ? regular : skipped).add(n);
        check(regular.equals(heads), "the table lists exactly the regular numbers from 2 to 81");
        StringJoiner sk = new StringJoiner(" ");
        for (int i = 0; i < 12; i++) sk.add(Long.toString(skipped.get(i)));
        System.out.printf("skipped 2-81: %d regular numbers listed, %d skipped; first skipped %s%n", regular.size(), skipped.size(), sk);
        for (int n : new int[]{7, 11, 13}) {
            int p = period(n);
            int[] e = expansion(n, Math.max(6, p + 1));
            // check: the expansion really is 1/n
            BigInteger num = BigInteger.ZERO;
            for (int x : expansion(n, p)) num = num.multiply(BigInteger.valueOf(60)).add(BigInteger.valueOf(x));
            BigInteger cycle = BigInteger.valueOf(60).pow(p).subtract(BigInteger.ONE);
            check(num.multiply(BigInteger.valueOf(n)).equals(cycle), "1/" + n + " = cycle / (60^p - 1)");
            System.out.printf("repeat 1/%d: 0;%s,... repeats every %d digits%n", n, show(Arrays.copyOf(e, Math.max(6, p + 1))), p);
        }
        long[][] divs = {{100, 16}, {50, 8}, {7, 12}, {1000, 81}};
        for (long[] q : divs) {
            int[] rec = reciprocal(q[1]);
            // a x (1/b): the reciprocal's digits are 60^j / b; the product a x 60^j / b, read as a floating number
            BigInteger sixty = BigInteger.valueOf(60), p = BigInteger.ONE, B = BigInteger.valueOf(q[1]);
            while (!p.mod(B).equals(BigInteger.ZERO)) p = p.multiply(sixty);
            BigInteger product = BigInteger.valueOf(q[0]).multiply(p.divide(B));
            int places = 0;
            for (BigInteger t = p; t.compareTo(BigInteger.ONE) > 0; t = t.divide(sixty)) places++;
            // the exact quotient as a base-60 number with `places` fractional digits
            BigInteger[] whole = product.divideAndRemainder(p);
            check(product.multiply(B).equals(BigInteger.valueOf(q[0]).multiply(p)), "a x (1/b) = a / b exactly");
            List<Integer> frac = new ArrayList<>();
            BigInteger r = whole[1];
            for (int i = 0; i < places; i++) { r = r.multiply(sixty); frac.add(r.divide(p).intValue()); r = r.mod(p); }
            while (!frac.isEmpty() && frac.get(frac.size() - 1) == 0) frac.remove(frac.size() - 1);
            String fracS = frac.isEmpty() ? "" : ";" + show(frac.stream().mapToInt(Integer::intValue).toArray());
            String wholeS = show(sexagesimal(whole[0].longValueExact()));
            String decimal;
            try {
                decimal = new java.math.BigDecimal(q[0]).divide(new java.math.BigDecimal(q[1])).stripTrailingZeros().toPlainString();
            } catch (ArithmeticException endless) {                       // ends in base 60 but not in base 10
                decimal = new java.math.BigDecimal(q[0]).divide(new java.math.BigDecimal(q[1]), new java.math.MathContext(8)).toPlainString() + "... never ends";
            }
            System.out.printf("divide %d / %d: reciprocal of %s is %s, so %s x %s = %s%s (decimal %s)%n", q[0], q[1], show(sexagesimal(q[1])), show(rec),
                    show(sexagesimal(q[0])), show(rec), wholeS, fracS, decimal);
        }
        for (long n : new long[]{60, 3600, 216_000, 12_960_000}) {
            long c = 0;
            for (long k = 1; k <= n; k++) if (isRegular(k)) c++;
            System.out.printf("regular-count up to %d: %d numbers (%.3f%%)%n", n, c, 100.0 * c / n);
        }

        // 3. Plimpton 322, row 1, from the reciprocal pair 2;24 and 0;25 (Bruins, Robson)
        // in units of 1/3600: x = 2;24 = 8640/3600, 1/x = 0;25 = 1500/3600
        long x = 2 * 3600 + 24 * 60, xr = 25 * 60;
        check(x * xr == 3600L * 3600L, "2;24 and 0;25 are a reciprocal pair");
        long half_diff = (x - xr) / 2, half_sum = (x + xr) / 2;           // 0;59,30 and 1;24,30 in units of 1/3600
        long s = half_diff, dgl = half_sum, l = 3600;
        while (s % 2 == 0 && dgl % 2 == 0 && l % 2 == 0) { s /= 2; dgl /= 2; l /= 2; }
        for (int pr : new int[]{3, 5}) while (s % pr == 0 && dgl % pr == 0 && l % pr == 0) { s /= pr; dgl /= pr; l /= pr; }
        check(s == 119 && dgl == 169 && l == 120, "row 1: short side 1,59 and diagonal 2,49");
        check(dgl * dgl - s * s == l * l, "169^2 - 119^2 = 120^2");
        System.out.printf("plimpton row 1: x=2;24 1/x=0;25 half-difference=0;59,30 half-sum=1;24,30 -> short side %s (%d), diagonal %s (%d), long side %d; %d^2 - %d^2 = %d^2%n",
                show(sexagesimal(s)), s, show(sexagesimal(dgl)), dgl, l, dgl, s, l);

        // 4. division by multiplying with a precomputed reciprocal, as compilers do
        Random rnd = new Random(1994);
        long checkedDiv = 0;
        for (long d = 1; d <= 1000; d++) {
            long[] mg = magic(d);
            long[] probes = {0, 1, d - 1, d, d + 1, 0xFFFF_FFFFL, 0xFFFF_FFFFL - 1, 0x8000_0000L};
            for (long n : probes) {
                if (n < 0 || n > 0xFFFF_FFFFL) continue;
                check(divideByMagic(n, mg[0], (int) mg[1]) == n / d, "magic division");
                checkedDiv++;
            }
            for (int i = 0; i < 2000; i++) {
                long n = rnd.nextLong(0, 1L << 32);
                check(divideByMagic(n, mg[0], (int) mg[1]) == n / d, "magic division " + n + "/" + d);
                checkedDiv++;
            }
        }
        for (long d : new long[]{7, 60}) {
            long[] mg = magic(d);
            System.out.printf("magic %d: multiply by %d, then shift right %d bits (no division)%n", d, mg[0], mg[1]);
        }
        System.out.printf("magiccheck: %d divisions by 1 to 1000 agreed with ordinary division%n", checkedDiv);

        System.out.printf("BabylonianPlaceValue: %d checks passed%n", passed);
    }
}
