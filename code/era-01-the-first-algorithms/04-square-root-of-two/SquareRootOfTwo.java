import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Era 1, topic 4: the square root of 2 on the tablet YBC 7289 (Old Babylonian, c. 1800-1600 BCE).
 *
 * HOW IT WORKS
 *   The tablet shows a square with its diagonals. The side is marked 30, and along the diagonal are two numbers in
 *   base 60: 1;24,51,10 (that is 1 + 24/60 + 51/60^2 + 10/60^3, an approximation of the square root of 2) and
 *   42;25,35 (30 times it, the length of the diagonal). How the scribe got the value is disputed.
 *   One procedure that reaches it is averaging: if g is a guess for the square root of N, then g and N/g lie on
 *   opposite sides of the root, so their average is a better guess. Heron of Alexandria wrote this procedure down in
 *   his Metrica (1st century CE). It is Newton's method for x^2 - N = 0, and each step roughly doubles the number of
 *   correct digits.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Checks the tablet's arithmetic exactly (30 x 1;24,51,10 = 42;25,35) and measures how close 1;24,51,10 is.
 *   2. Runs the averaging procedure from the guess 1 with exact fractions, shows that the third new guess, 577/408,
 *      gives the tablet's digits when cut to three base-60 places (but not when rounded), and checks that every guess
 *      is a continued-fraction convergent of the square root of 2 and solves Pell's equation p^2 - 2q^2 = 1.
 *   3. Counts the steps three methods need for 6, 15, 100 and 1,000 correct digits: halving an interval, the
 *      digit-by-digit method taught in schools, and averaging.
 *   4. Repeats Heron's own example (the square root of 720 from 27), a division-free variant for 1/sqrt(2), and the
 *      inverse square root of the Quake III Arena source code: a bit trick plus one Newton step, checked on every
 *      float from 1 to 4.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SquareRootOfTwo.java
 *   Expected output: expected-output.txt in this folder.
 */
public class SquareRootOfTwo {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final MathContext MC = new MathContext(1200);
    static final BigDecimal TWO = BigDecimal.valueOf(2);
    static final BigDecimal SQRT2 = TWO.sqrt(MC);

    /** An exact fraction p/q. */
    record Frac(BigInteger p, BigInteger q) {
        BigDecimal value() { return new BigDecimal(p).divide(new BigDecimal(q), MC); }

        public String toString() { return p + "/" + q; }
    }

    /** One averaging step for the square root of N: (g + N/g) / 2, with exact fractions. */
    static Frac average(Frac g, long n) {
        BigInteger N = BigInteger.valueOf(n);
        // g = p/q: (p/q + N q/p) / 2 = (p^2 + N q^2) / (2 p q)
        BigInteger num = g.p().pow(2).add(N.multiply(g.q().pow(2)));
        BigInteger den = BigInteger.TWO.multiply(g.p()).multiply(g.q());
        BigInteger k = num.gcd(den);
        return new Frac(num.divide(k), den.divide(k));
    }

    /** The first `places` base-60 digits after the point of a positive number, cut off (not rounded). */
    static int[] sexagesimalDigits(BigDecimal x, int places) {
        int[] d = new int[places + 1];
        BigDecimal sixty = BigDecimal.valueOf(60);
        d[0] = x.intValue();
        BigDecimal f = x.subtract(BigDecimal.valueOf(d[0]));
        for (int i = 1; i <= places; i++) {
            f = f.multiply(sixty);
            d[i] = f.intValue();
            f = f.subtract(BigDecimal.valueOf(d[i]));
        }
        return d;
    }

    /** Rounded to `places` base-60 places. */
    static int[] sexagesimalRounded(BigDecimal x, int places) {
        BigDecimal scale = BigDecimal.valueOf(60).pow(places);
        BigInteger units = x.multiply(scale).setScale(0, RoundingMode.HALF_UP).toBigInteger();
        int[] d = new int[places + 1];
        for (int i = places; i >= 1; i--) {
            d[i] = units.mod(BigInteger.valueOf(60)).intValue();
            units = units.divide(BigInteger.valueOf(60));
        }
        d[0] = units.intValue();
        return d;
    }

    static String sexa(int[] d) {
        StringBuilder s = new StringBuilder().append(d[0]).append(';');
        for (int i = 1; i < d.length; i++) s.append(i > 1 ? "," : "").append(d[i]);
        return s.toString();
    }

    /** -log10 of the error, rounded down: the number of correct decimal places, measured. */
    static int places(BigDecimal x) {
        BigDecimal err = x.subtract(SQRT2).abs();
        int k = 0;
        BigDecimal tenth = BigDecimal.ONE;
        while (err.compareTo(tenth) < 0 && k < 1100) { k++; tenth = tenth.movePointLeft(1); }
        return k - 1;
    }

    // ----------------------------------------------------------------------------------------------------
    // three methods, counted in steps
    // ----------------------------------------------------------------------------------------------------

    /** Halve the interval [1, 2] that holds the root, keeping the half where the square changes sides. */
    static int bisectionSteps(int digits) {
        BigDecimal lo = BigDecimal.ONE, hi = TWO, target = BigDecimal.ONE.movePointLeft(digits);
        int steps = 0;
        while (hi.subtract(lo).compareTo(target) >= 0) {
            BigDecimal mid = lo.add(hi).divide(TWO, MC);
            if (mid.multiply(mid).compareTo(TWO) <= 0) lo = mid; else hi = mid;
            steps++;
        }
        check(lo.compareTo(SQRT2) <= 0 && hi.compareTo(SQRT2) >= 0, "the root stays inside the interval");
        return steps;
    }

    /** The schoolbook digit-by-digit method: one decimal digit per step. Returns the digits found. */
    static String digitByDigit(int digits) {
        BigInteger remainder = BigInteger.ZERO, root = BigInteger.ZERO;
        StringBuilder out = new StringBuilder();
        BigInteger pair = BigInteger.TWO;                                   // 2.00 00 00 ...: first pair 2, then 00s
        for (int i = 0; i <= digits; i++) {
            remainder = remainder.multiply(BigInteger.valueOf(100)).add(pair);
            int x = 9;                                                     // largest x with (20 root + x) x <= remainder
            while (BigInteger.valueOf(20).multiply(root).add(BigInteger.valueOf(x)).multiply(BigInteger.valueOf(x)).compareTo(remainder) > 0) x--;
            remainder = remainder.subtract(BigInteger.valueOf(20).multiply(root).add(BigInteger.valueOf(x)).multiply(BigInteger.valueOf(x)));
            root = root.multiply(BigInteger.TEN).add(BigInteger.valueOf(x));
            out.append(x);
            if (i == 0) out.append('.');
            pair = BigInteger.ZERO;
        }
        return out.toString();
    }

    static int averagingSteps(int digits) {
        BigDecimal g = BigDecimal.ONE, target = BigDecimal.ONE.movePointLeft(digits);
        int steps = 0;
        while (g.subtract(SQRT2).abs().compareTo(target) >= 0) {
            g = g.add(TWO.divide(g, MC)).divide(TWO, MC);
            steps++;
        }
        return steps;
    }

    // ----------------------------------------------------------------------------------------------------
    // Quake III Arena's inverse square root (id Software, released under the GPL)
    // ----------------------------------------------------------------------------------------------------

    static float qRsqrtGuess(float number) {
        int i = Float.floatToRawIntBits(number);
        i = 0x5f3759df - (i >> 1);                                         // the bit trick: a first guess for 1/sqrt(x)
        return Float.intBitsToFloat(i);
    }

    static float qRsqrt(float number) {
        float x2 = number * 0.5f, y = qRsqrtGuess(number);
        y = y * (1.5f - (x2 * y * y));                                     // one Newton step for 1/y^2 - x = 0
        return y;
    }

    // ----------------------------------------------------------------------------------------------------

    public static void main(String[] args) {
        // 1. the tablet
        BigInteger units = BigInteger.valueOf(1L * 216000 + 24L * 3600 + 51L * 60 + 10);   // 1;24,51,10 in 60^-3 units
        Frac tablet = new Frac(units, BigInteger.valueOf(216000));
        BigInteger diag = units.multiply(BigInteger.valueOf(30));
        check(diag.equals(BigInteger.valueOf(42L * 216000 + 25L * 3600 + 35L * 60)), "30 x 1;24,51,10 = 42;25,35 exactly");
        BigDecimal tv = tablet.value();
        BigDecimal err = tv.subtract(SQRT2);
        System.out.printf("tablet: 1;24,51,10 = %s... ; sqrt(2) = %s... ; error %s ; 30 x 1;24,51,10 = 42;25,35 exactly%n",
                tv.round(new MathContext(12)).toPlainString(), SQRT2.round(new MathContext(12)).toPlainString(), err.round(new MathContext(3)).toString());
        System.out.printf("tablet-places: %d correct decimal places; square of the tablet value = %s%n", places(tv), tv.multiply(tv).round(new MathContext(12)).toPlainString());
        int[] s2 = sexagesimalDigits(SQRT2, 6);
        System.out.printf("sqrt2 in base 60: %s,...%n", sexa(s2));
        check(sexa(Arrays.copyOf(s2, 4)).equals("1;24,51,10"), "the tablet's digits are the first three places of sqrt 2");

        // 2. averaging from 1, exact
        List<Frac> convergents = new ArrayList<>();
        BigInteger p0 = BigInteger.ONE, q0 = BigInteger.ONE, p1 = BigInteger.valueOf(3), q1 = BigInteger.TWO;
        convergents.add(new Frac(p0, q0));
        convergents.add(new Frac(p1, q1));
        for (int i = 2; i < 64; i++) {                                     // sqrt 2 = [1; 2, 2, 2, ...]
            BigInteger p2 = p1.multiply(BigInteger.TWO).add(p0), q2 = q1.multiply(BigInteger.TWO).add(q0);
            convergents.add(new Frac(p2, q2));
            p0 = p1; q0 = q1; p1 = p2; q1 = q2;
        }
        Frac g = new Frac(BigInteger.ONE, BigInteger.ONE);
        System.out.printf("iterate 0: 1/1 = 1 ; correct places 0%n");
        for (int k = 1; k <= 5; k++) {
            g = average(g, 2);
            BigDecimal v = g.value();
            int idx = (1 << k) - 1;
            check(g.equals(convergents.get(idx)), "averaging step " + k + " lands on convergent " + idx);
            check(g.p().pow(2).subtract(BigInteger.TWO.multiply(g.q().pow(2))).equals(BigInteger.ONE), "Pell: p^2 - 2 q^2 = 1");
            String cut = sexa(sexagesimalDigits(v, 3)), rounded = sexa(sexagesimalRounded(v, 3));
            String frac = g.p().bitLength() < 64 ? g.toString() : g.p().toString().length() + "-digit/" + g.q().toString().length() + "-digit fraction";
            System.out.printf("iterate %d: %s = %s ; correct places %d ; three base-60 places cut %s rounded %s ; convergent %d ; p^2 - 2q^2 = 1%n",
                    k, frac, v.round(new MathContext(12)).toPlainString(), places(v), cut, rounded, idx);
            if (k == 3) check(cut.equals("1;24,51,10") && !rounded.equals("1;24,51,10"), "577/408 cut to 3 places is the tablet value; rounded it is not");
            if (k == 2) check(!cut.equals("1;24,51,10"), "17/12 is not yet the tablet value");
        }

        // 3. three methods
        for (int digits : new int[]{6, 15, 100, 1000}) {
            int b = bisectionSteps(digits), a = averagingSteps(digits);
            String dd = digitByDigit(digits);
            check(dd.equals(SQRT2.setScale(digits, RoundingMode.DOWN).toPlainString()), "digit by digit gives the digits of sqrt 2");
            System.out.printf("method %d digits: halving=%d digit-by-digit=%d averaging=%d%n", digits, b, digits, a);
        }

        // 4a. Heron's example: the square root of 720 from 27
        Frac h = average(new Frac(BigInteger.valueOf(27), BigInteger.ONE), 720);
        check(h.equals(new Frac(BigInteger.valueOf(161), BigInteger.valueOf(6))), "Heron: 26 5/6");
        BigInteger hs = h.p().pow(2), hq = h.q().pow(2);                    // (161/6)^2 = 25921/36 = 720 + 1/36
        check(hs.subtract(BigInteger.valueOf(720).multiply(hq)).equals(BigInteger.ONE) && hq.equals(BigInteger.valueOf(36)), "(26 5/6)^2 = 720 1/36");
        System.out.printf("heron: sqrt(720) from 27: 720/27 = 26 2/3, average = 26 5/6 = %s ; its square is 720 1/36%n", h);

        // 4b. division-free: y <- y (3 - 2 y^2) / 2 converges to 1/sqrt 2, and sqrt 2 = 2y
        BigDecimal y = BigDecimal.ONE, three = BigDecimal.valueOf(3);
        int steps = 0;
        while (y.multiply(TWO).subtract(SQRT2).abs().compareTo(BigDecimal.ONE.movePointLeft(15)) >= 0) {
            y = y.multiply(three.subtract(TWO.multiply(y).multiply(y))).divide(TWO, MC);    // halving is a shift
            steps++;
        }
        System.out.printf("invsqrt: y <- y(3 - 2y^2)/2 from y = 1 reaches 15 correct digits of sqrt 2 = 2y in %d steps, using no division%n", steps);

        // 4c. Quake III Arena: every float in [1, 4)
        int lo = Float.floatToRawIntBits(1.0f), hi = Float.floatToRawIntBits(4.0f);
        double worstGuess = 0, worstStep = 0;
        long count = 0;
        for (int bits = lo; bits < hi; bits++) {
            float x = Float.intBitsToFloat(bits);
            double exact = 1.0 / Math.sqrt(x);
            worstGuess = Math.max(worstGuess, Math.abs(qRsqrtGuess(x) - exact) / exact);
            double stepErr = Math.abs(qRsqrt(x) - exact) / exact;
            check(stepErr < 0.002, "after one Newton step every float is within 0.2%");
            worstStep = Math.max(worstStep, stepErr);
            count++;
        }
        check(count == 1 << 24, "every float in [1, 4)");
        check(worstStep < worstGuess / 10, "one Newton step cuts the error more than tenfold");
        // the error pattern repeats every factor of 4: spot-check far away
        for (float x : new float[]{1e-6f, 0.37f, 123456.7f, 3.0e20f}) {
            double exact = 1.0 / Math.sqrt(x);
            check(Math.abs(qRsqrt(x) - exact) / exact <= worstStep * 1.0001, "same worst error elsewhere");
        }
        System.out.printf("quake: %d floats from 1 to 4; bit-trick guess worst relative error %.4f%%, after one Newton step %.4f%%%n",
                count, 100 * worstGuess, 100 * worstStep);

        System.out.printf("SquareRootOfTwo: %d checks passed%n", passed);
    }
}
