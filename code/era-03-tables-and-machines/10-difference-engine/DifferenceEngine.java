import java.math.BigInteger;
import java.util.*;

/**
 * Era 3, topic 10: Babbage's difference engine (London, 1821-1822; Difference Engine No. 2 designed 1847-1849,
 * built by the Science Museum 1991, printer 2002).
 *
 * HOW IT WORKS
 *   Take any polynomial, list its values at x = 0, 1, 2, ..., and subtract neighbours: the first differences. Subtract
 *   neighbours again: the second differences. For a polynomial of degree n the nth differences are constant. So the
 *   table can be run backwards: keep one value and one difference of each order in a column of wheels, and each turn
 *   of the handle adds every difference into the one above it. The value column then steps through the table using
 *   additions only, which is exactly what wheels with a carry (topic 3) can do. Babbage's first model had two orders
 *   of difference and made a table of x^2 + x + 41.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Runs a two-difference engine on x^2 + x + 41, as Babbage's model did, checking every value.
 *   2. Runs engines of higher order on random polynomials of degree up to 7, with exact whole numbers.
 *   3. Counts the work: additions per entry against Horner's multiplications and additions.
 *   4. Makes a 7-place table of common logarithms from 1,000 to 9,999 by a seventh-order engine, restarting from exact
 *      values every 50 entries, and compares every entry with the true rounded value.
 *   5. Shows how differences expose an error in a printed table.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java DifferenceEngine.java
 *   Expected output: expected-output.txt in this folder.
 */
public class DifferenceEngine {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long additions;

    /** An engine: column[0] is the value, column[k] the kth difference. One turn adds each column into the one above. */
    static final class Engine {
        final BigInteger[] col;

        Engine(BigInteger[] initial) { col = initial.clone(); }

        BigInteger turn() {
            for (int k = 0; k < col.length - 1; k++) { col[k] = col[k].add(col[k + 1]); additions++; }   // top first: uses the old differences
            return col[0];
        }
    }

    /** The starting column from the first n + 1 values: f(0), and the differences at 0. */
    static BigInteger[] setUp(BigInteger[] firstValues) {
        int n = firstValues.length;
        BigInteger[] row = firstValues.clone(), col = new BigInteger[n];
        for (int k = 0; k < n; k++) {
            col[k] = row[0];
            BigInteger[] next = new BigInteger[row.length - 1];
            for (int i = 0; i + 1 < row.length; i++) next[i] = row[i + 1].subtract(row[i]);
            row = next;
        }
        return col;
    }

    static final java.math.MathContext MC = new java.math.MathContext(50);
    static java.math.BigDecimal LN10;

    /** ln x for x >= 1, to about 45 digits: halve x by powers of 2, then 2 atanh((x - 1)/(x + 1)). */
    static java.math.BigDecimal ln(java.math.BigDecimal x) {
        java.math.BigDecimal two = java.math.BigDecimal.valueOf(2);
        int k = 0;
        while (x.compareTo(java.math.BigDecimal.valueOf(1.5)) > 0) { x = x.divide(two, MC); k++; }
        java.math.BigDecimal y = x.subtract(java.math.BigDecimal.ONE).divide(x.add(java.math.BigDecimal.ONE), MC), y2 = y.multiply(y, MC), term = y, sum = y;
        for (int n = 3; term.abs().compareTo(new java.math.BigDecimal("1e-49")) > 0; n += 2) { term = term.multiply(y2, MC); sum = sum.add(term.divide(java.math.BigDecimal.valueOf(n), MC), MC); }
        return sum.multiply(two, MC).add(LN2.multiply(java.math.BigDecimal.valueOf(k), MC), MC);
    }

    static java.math.BigDecimal LN2;

    static java.math.BigDecimal log10(long v) { return ln(java.math.BigDecimal.valueOf(v)).divide(LN10, MC); }

    static BigInteger horner(long[] c, long x) {                   // c[0] + c[1] x + ...
        BigInteger v = BigInteger.ZERO, X = BigInteger.valueOf(x);
        for (int i = c.length - 1; i >= 0; i--) v = v.multiply(X).add(BigInteger.valueOf(c[i]));
        return v;
    }

    public static void main(String[] args) {
        LN2 = java.math.BigDecimal.ZERO;
        LN2 = ln(java.math.BigDecimal.valueOf(2).sqrt(MC)).multiply(java.math.BigDecimal.valueOf(2), MC);
        LN10 = ln(java.math.BigDecimal.TEN);
        check(Math.abs(LN10.doubleValue() - Math.log(10)) < 1e-15, "ln 10");
        // ---- 1. Babbage's model: x^2 + x + 41 ------------------------------------------------------------------------
        long[] p = {41, 1, 1};
        BigInteger[] first = {horner(p, 0), horner(p, 1), horner(p, 2)};
        BigInteger[] start = setUp(first);
        Engine e = new Engine(start);
        StringJoiner table = new StringJoiner(", ");
        table.add(start[0].toString());
        int primesRun = 0;
        boolean stillPrime = true;
        int firstComposite = -1;
        for (int x = 1; x <= 50; x++) {
            BigInteger v = e.turn();
            check(v.equals(horner(p, x)), "the engine's value equals x^2 + x + 41");
            if (x <= 9) table.add(v.toString());
            if (stillPrime && v.isProbablePrime(50)) primesRun = x; else if (stillPrime) { stillPrime = false; firstComposite = x; }
        }
        check(start[0].isProbablePrime(50) && firstComposite == 40, "x^2 + x + 41 is prime for x = 0 to 39, and 1681 = 41^2 at x = 40");
        System.out.printf("babbage: x^2 + x + 41 ; the engine starts with value %s, first difference %s, second difference %s (constant) ; each turn: value += first difference, first difference += second ; the table: %s, ... ; every value up to x = 50 checked ; prime for x = 0 to %d, then %s = 41 x 41 at x = %d%n",
                start[0], start[1], start[2], table, primesRun, horner(p, 40), firstComposite);

        // ---- 2. higher orders --------------------------------------------------------------------------------------------
        Random rnd = new Random(1822);
        int tested = 0;
        for (int t = 0; t < 2000; t++) {
            int deg = 1 + rnd.nextInt(7);
            long[] c = new long[deg + 1];
            for (int i = 0; i <= deg; i++) c[i] = rnd.nextInt(2001) - 1000;
            BigInteger[] fv = new BigInteger[deg + 1];
            for (int i = 0; i <= deg; i++) fv[i] = horner(c, i);
            BigInteger[] s0 = setUp(fv);
            check(s0[deg].signum() != 0 || c[deg] == 0, "the top difference is constant and non-zero");
            Engine g = new Engine(s0);
            for (int x = 1; x <= 200; x++) check(g.turn().equals(horner(c, x)), "the engine reproduces the polynomial");
            tested++;
        }
        System.out.printf("orders: %,d random polynomials of degree 1 to 7 with whole coefficients from -1,000 to 1,000 ; an engine with one column more than the degree reproduces 200 values of each exactly, using additions only%n", tested);

        // ---- 3. the work ----------------------------------------------------------------------------------------------
        StringJoiner work = new StringJoiner(" ; ");
        for (int deg : new int[]{2, 4, 7}) work.add(String.format("degree %d: the engine %d additions per entry ; Horner's rule %d multiplications and %d additions", deg, deg, deg, deg));
        System.out.printf("work: %s%n", work);

        // ---- 4. a table of logarithms by differences ------------------------------------------------------------------
        // between restarts, log10 is replaced by the polynomial of degree 7 through 8 exact values at s, s + 1, ..., s + 7,
        // stepped by additions; the columns carry whole numbers of 10^-35, far more places than are printed
        BigInteger scale = BigInteger.TEN.pow(35);
        java.math.BigDecimal sc = new java.math.BigDecimal(scale);
        int from = 1000, to = 10000, span = 50, deg = 7;
        int printed = 0, wrong = 0;
        additions = 0;
        java.math.BigDecimal worstErr = java.math.BigDecimal.ZERO;
        for (int s0 = from; s0 < to; s0 += span) {
            BigInteger[] fv = new BigInteger[deg + 1];
            for (int i = 0; i <= deg; i++) fv[i] = log10(s0 + i).multiply(sc).setScale(0, java.math.RoundingMode.HALF_EVEN).toBigIntegerExact();
            Engine g = new Engine(setUp(fv));
            for (int x = 0; x < span; x++) {
                BigInteger v = x == 0 ? g.col[0] : g.turn();
                java.math.BigDecimal exact = log10(s0 + x), got = new java.math.BigDecimal(v).divide(sc, MC);
                java.math.BigDecimal err = got.subtract(exact).abs();
                if (err.compareTo(worstErr) > 0) worstErr = err;
                java.math.BigDecimal rGot = got.setScale(7, java.math.RoundingMode.HALF_EVEN), rTrue = exact.setScale(7, java.math.RoundingMode.HALF_EVEN);
                if (rGot.compareTo(rTrue) != 0) wrong++;
                check(rGot.compareTo(rTrue) == 0, "the printed 7-place logarithm agrees with the true rounded value");
                printed++;
            }
        }
        System.out.printf("logs: a 7-place table of log10 x for x = %,d to %,d, by a seventh-order engine restarted from exact values every %d entries ; %,d entries printed, %d differ from the true rounded value ; largest error before rounding %.1e ; %,d additions in all, %.1f per entry%n",
                from, to - 1, span, printed, wrong, worstErr.doubleValue(), additions, additions / (double) printed);

        // ---- 5. differences expose a misprint --------------------------------------------------------------------------
        long[] tab = new long[12];
        for (int x = 0; x < 12; x++) tab[x] = horner(p, x).longValue();
        long[] bad = tab.clone();
        bad[6] += 10;                                            // one entry printed wrongly: 83 + 10
        long[] d3 = diffs(bad, 3);
        StringJoiner ds = new StringJoiner(", ");
        for (long v : d3) ds.add(String.valueOf(v));
        long[] d3good = diffs(tab, 3);
        for (long v : d3good) check(v == 0, "the true table's third differences are zero");
        check(d3[3] == 10 && d3[4] == -30 && d3[5] == 30 && d3[6] == -10, "the misprint shows as 10, -30, 30, -10");
        System.out.printf("misprint: the table of x^2 + x + 41 for x = 0 to 11 with the entry at x = 6 printed as %d instead of %d ; its third differences, which should all be 0: %s ; the pattern 1, -3, 3, -1 times the error points to the bad entry%n",
                bad[6], tab[6], ds);

        System.out.printf("DifferenceEngine: %d checks passed%n", passed);
    }

    static long[] diffs(long[] a, int order) {
        long[] r = a.clone();
        for (int k = 0; k < order; k++) { long[] n = new long[r.length - 1]; for (int i = 0; i + 1 < r.length; i++) n[i] = r[i + 1] - r[i]; r = n; }
        return r;
    }
}
