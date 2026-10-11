import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Era 3, topic 2: logarithms (Napier, 1614; Briggs, 1617 and 1624).
 *
 * HOW IT WORKS
 *   Give every number a partner, its logarithm, so that the partner of a product is the sum of the partners:
 *   log(ab) = log a + log b. With a printed table, a long multiplication becomes two look-ups, one addition and one
 *   look-up backwards; division becomes subtraction, and a square root becomes halving. Briggs chose base 10, so that
 *   log 10 = 1 and log 1 = 0. To compute the table he took the square root of 10 again and again (54 times), reaching a
 *   number 1 + d extremely close to 1, whose logarithm is exactly 1/2^54. Very close to 1, the logarithm is
 *   proportional to the excess over 1, so a number x near 1 has logarithm (x - 1)/d times 1/2^54. To find log 2, take
 *   square roots of 2 until it is near 1, use the proportion, and multiply back by the number of halvings. Only the
 *   primes need this work: log 6 = log 2 + log 3.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Multiplies by adding, with tables of 4, 7 and 14 decimals, and measures the error the table's rounding causes.
 *   2. Runs Briggs's 54 square roots of 10 to 40 digits and finds log 2, log 3 and log 7 by his proportion,
 *      measuring how many decimals are right for 10 to 60 roots.
 *   3. Counts the work in a table like Briggs's 1624 table: how many entries need a computation of their own (primes).
 *   4. Counts digit operations: long multiplication against the look-up and addition.
 *   5. Full circle: a product of many small probabilities in 64-bit floating point, directly and by adding logarithms.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Logarithms.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Logarithms {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final MathContext MC = new MathContext(60);

    /** log10 to high precision, for checking (ln by atanh series, then divide by ln 10). */
    static BigDecimal ln(BigDecimal x) {
        // ln x = 2 atanh((x - 1)/(x + 1)), after scaling x into [0.5, 2] by powers of 2
        int k = 0;
        BigDecimal two = BigDecimal.valueOf(2);
        while (x.compareTo(two) > 0) { x = x.divide(two, MC); k++; }
        while (x.compareTo(new BigDecimal("0.5")) < 0) { x = x.multiply(two, MC); k--; }
        BigDecimal y = x.subtract(BigDecimal.ONE).divide(x.add(BigDecimal.ONE), MC), y2 = y.multiply(y, MC), term = y, sum = y;
        for (int n = 3; term.abs().compareTo(new BigDecimal("1e-58")) > 0; n += 2) {
            term = term.multiply(y2, MC);
            sum = sum.add(term.divide(BigDecimal.valueOf(n), MC), MC);
        }
        return sum.multiply(two, MC).add(LN2 == null ? BigDecimal.ZERO : LN2.multiply(BigDecimal.valueOf(k), MC), MC);
    }

    static BigDecimal LN2, LN10;

    static BigDecimal log10(BigDecimal x) { return ln(x).divide(LN10, MC); }

    static int correctDecimals(BigDecimal approx, BigDecimal truth) {
        BigDecimal err = approx.subtract(truth).abs();
        int d = 0;
        while (d < 50 && err.compareTo(new BigDecimal("0.5").movePointLeft(d + 1)) < 0) d++;
        return d;
    }

    /** Briggs's proportion: log10 x from k square roots of x and n square roots of 10, at 40 significant digits. */
    static BigDecimal briggs(BigDecimal x, int n, MathContext mc, int[] rootsOut) {
        BigDecimal r10 = BigDecimal.TEN;
        for (int i = 0; i < n; i++) r10 = r10.sqrt(mc);
        BigDecimal d10 = r10.subtract(BigDecimal.ONE);                 // 10^(1/2^n) = 1 + d10
        BigDecimal rx = x;
        int k = 0;
        while (rx.subtract(BigDecimal.ONE).abs().compareTo(d10) > 0) { rx = rx.sqrt(mc); k++; }   // until x^(1/2^k) is as close to 1
        // log10(rx) ~ (rx - 1)/d10 * 2^-n ; log10 x = 2^k log10(rx)
        BigDecimal frac = rx.subtract(BigDecimal.ONE).divide(d10, mc);
        if (rootsOut != null) { rootsOut[0] = n; rootsOut[1] = k; }
        return frac.multiply(BigDecimal.valueOf(2).pow(k), mc).divide(BigDecimal.valueOf(2).pow(n), mc);
    }

    public static void main(String[] args) {
        LN2 = null;
        LN2 = ln(BigDecimal.valueOf(2).sqrt(MC)).multiply(BigDecimal.valueOf(2), MC);   // sqrt 2 lies in [0.5, 2]: no scaling needed
        LN10 = ln(BigDecimal.TEN);
        check(Math.abs(LN2.doubleValue() - Math.log(2)) < 1e-15 && Math.abs(LN10.doubleValue() - Math.log(10)) < 1e-15, "ln 2 and ln 10 agree with Math.log");

        // ---- 1. multiplying by adding ---------------------------------------------------------------------------------
        long[][] pairs = {{4567, 8912}, {1234, 5678}, {7854, 3906}, {9999, 9999}};
        StringJoiner ex = new StringJoiner(" ; ");
        for (long[] pr : pairs) {
            BigDecimal la = log10(BigDecimal.valueOf(pr[0])).setScale(7, RoundingMode.HALF_EVEN), lb = log10(BigDecimal.valueOf(pr[1])).setScale(7, RoundingMode.HALF_EVEN);
            BigDecimal sum = la.add(lb);
            double back = Math.pow(10, sum.doubleValue());
            long exact = pr[0] * pr[1];
            double rel = Math.abs(back - exact) / exact;
            check(rel < 5e-7, "a 7-place table gives the product to about 7 figures");
            if (ex.length() < 400) ex.add(String.format("%d x %d: %s + %s = %s -> %.0f (exact %d, relative error %.1e)", pr[0], pr[1], la.toPlainString(), lb.toPlainString(), sum.toPlainString(), back, exact, rel));
        }
        System.out.printf("multiply: %s%n", ex);
        Random rnd = new Random(1614);
        StringJoiner prec = new StringJoiner(" ; ");
        for (int places : new int[]{4, 7, 14}) {
            double worst = 0, sumRel = 0; int n = 20000;
            for (int t = 0; t < n; t++) {
                long a = 10000 + rnd.nextInt(90000), b = 10000 + rnd.nextInt(90000);
                BigDecimal la = log10(BigDecimal.valueOf(a)).setScale(places, RoundingMode.HALF_EVEN), lb = log10(BigDecimal.valueOf(b)).setScale(places, RoundingMode.HALF_EVEN);
                // the inverse look-up, done exactly: 10^(la + lb)
                BigDecimal s = la.add(lb);
                BigDecimal back = BigDecimal.TEN.pow(s.intValue()).multiply(BigDecimal.valueOf(Math.pow(10, s.subtract(BigDecimal.valueOf(s.intValue())).doubleValue())), MC);
                double rel = back.subtract(BigDecimal.valueOf(a * b)).abs().divide(BigDecimal.valueOf(a * b), MC).doubleValue();
                worst = Math.max(worst, rel); sumRel += rel;
                check(rel <= (Math.pow(10, Math.pow(10, -places)) - 1) * 1.01 + 1e-15, "the error stays within the table's rounding");
            }
            prec.add(String.format("%d places: worst relative error %.1e, average %.1e", places, worst, sumRel / n));
        }
        System.out.printf("precision: 20,000 random products of five-digit numbers by table look-up ; %s%n", prec);

        // ---- 2. Briggs's square roots of 10 ------------------------------------------------------------------------
        MathContext mc40 = new MathContext(40);
        BigDecimal r = BigDecimal.TEN;
        StringJoiner roots = new StringJoiner(" ; ");
        for (int i = 1; i <= 54; i++) {
            r = r.sqrt(mc40);
            if (i <= 3 || i == 10 || i == 20 || i == 54) roots.add(String.format("root %d: %s", i, r.round(new MathContext(22)).toPlainString()));
        }
        BigDecimal d54 = r.subtract(BigDecimal.ONE);
        BigDecimal predicted = LN10.divide(BigDecimal.valueOf(2).pow(54), MC);   // ln(1 + d) ~ d, so d ~ ln10/2^54
        check(d54.subtract(predicted).abs().divide(predicted, MC).doubleValue() < 1e-15, "after 54 roots, the excess over 1 is ln 10 / 2^54 to 15 figures");
        System.out.printf("roots: %s ; the excess over 1 after 54 roots is %s, and its logarithm is exactly 1/2^54 = %s%n",
                roots, d54.round(new MathContext(16)).toString(), BigDecimal.ONE.divide(BigDecimal.valueOf(2).pow(54), MC).round(new MathContext(16)).toString());

        StringJoiner logs = new StringJoiner(" ; ");
        for (int x : new int[]{2, 3, 7}) {
            int[] used = new int[2];
            BigDecimal lx = briggs(BigDecimal.valueOf(x), 54, mc40, used);
            BigDecimal truth = log10(BigDecimal.valueOf(x));
            int dec = correctDecimals(lx, truth);
            check(dec >= 14, "54 roots give at least Briggs's 14 decimals");
            logs.add(String.format("log %d = %s (true %s ; %d roots of %d ; %d correct decimals)", x, lx.setScale(16, RoundingMode.HALF_EVEN).toPlainString(), truth.setScale(16, RoundingMode.HALF_EVEN).toPlainString(), used[1], x, dec));
        }
        System.out.printf("briggs: %s%n", logs);
        StringJoiner byRoots = new StringJoiner(" ; ");
        int prevDec = -1;
        for (int n = 10; n <= 60; n += 10) {
            BigDecimal l2 = briggs(BigDecimal.valueOf(2), n, mc40, null);
            int dec = correctDecimals(l2, log10(BigDecimal.valueOf(2)));
            check(dec >= prevDec, "more roots never give fewer decimals");
            prevDec = dec;
            byRoots.add(n + " roots: " + dec);
        }
        System.out.printf("truth: log 2 = %s%n", log10(BigDecimal.valueOf(2)).setScale(36, RoundingMode.HALF_EVEN).toPlainString());
        System.out.printf("depth: square roots of 10 taken, and correct decimals of log 2 by the proportion: %s%n", byRoots);

        // ---- 3. how much of a table needs its own computation -----------------------------------------------------------
        int[][] ranges = {{1, 20000}, {90001, 100000}};
        int entries = 0, primes = 0, bySum = 0, outside = 0, small = 0;
        for (int[] rg : ranges)
            for (int v = rg[0]; v <= rg[1]; v++) {
                entries++;
                if (v == 1) { bySum++; continue; }                     // log 1 = 0
                if (isPrime(v)) { primes++; if (v <= 20000) small++; continue; }
                int big = largestPrimeFactor(v);
                if (big <= 20000) {
                    bySum++;
                    // the law itself, on every such entry: log v = log a + log (v/a) for its smallest factor a
                    int a = smallestFactor(v);
                    check(Math.abs(Math.log10(a) + Math.log10(v / a) - Math.log10(v)) < 1e-13, "log(ab) = log a + log b");
                } else outside++;                                     // a prime factor above 20,000 that is not in the table
            }
        check(entries == primes + bySum + outside, "every entry is counted once");
        System.out.printf("table: a table of 1 to 20,000 and 90,001 to 100,000 has %,d entries ; %,d are prime and need a logarithm of their own (%,d below 20,000, %,d above 90,000) ; %,d follow by adding logarithms of smaller entries ; %,d have a prime factor above 20,000 that is not itself in the table%n",
                entries, primes, small, primes - small, bySum, outside);

        // ---- 4. digit operations ----------------------------------------------------------------------------------------
        // long multiplication of two n-digit numbers: n^2 digit products and about n^2 digit additions;
        // by logarithms: 2 look-ups, one addition of two (n+2)-place logs, one inverse look-up
        StringJoiner ops = new StringJoiner(" ; ");
        for (int n : new int[]{5, 7, 14}) ops.add(String.format("%d digits: long multiplication %d digit products, logarithms one addition of %d digits and 3 look-ups", n, n * n, n + 1));
        System.out.printf("work: %s%n", ops);

        // ---- 5. full circle: adding logarithms instead of multiplying probabilities ---------------------------------------
        double prod = 1, logSum = 0;
        int steps = 400;
        for (int i = 0; i < steps; i++) { double pr = 0.01 + 0.0001 * (i % 7); prod *= pr; logSum += Math.log10(pr); }
        check(prod == 0.0, "the direct product underflows to zero");
        BigDecimal exactProd = BigDecimal.ONE;
        for (int i = 0; i < steps; i++) exactProd = exactProd.multiply(new BigDecimal(Double.toString(0.01 + 0.0001 * (i % 7))), MC);
        BigDecimal exactLog = log10(exactProd);
        check(Math.abs(exactLog.doubleValue() - logSum) < 1e-9, "the sum of logarithms is right");
        System.out.printf("underflow: the product of %d probabilities near 0.01 in 64-bit floating point is %s (the smallest positive double is %s) ; the sum of their base-10 logarithms is %.6f, so the product is about 10^%.6f (exact %.6f)%n",
                steps, prod, Double.MIN_VALUE, logSum, logSum, exactLog.doubleValue());

        System.out.printf("Logarithms: %d checks passed%n", passed);
    }

    static boolean isPrime(int v) {
        if (v < 2) return false;
        for (int d = 2; (long) d * d <= v; d++) if (v % d == 0) return false;
        return true;
    }

    static int smallestFactor(int v) { for (int d = 2; (long) d * d <= v; d++) if (v % d == 0) return d; return v; }

    static int largestPrimeFactor(int v) {
        int big = 1;
        for (int d = 2; (long) d * d <= v; d++) while (v % d == 0) { big = d; v /= d; }
        return v > 1 ? Math.max(big, v) : big;
    }
}
