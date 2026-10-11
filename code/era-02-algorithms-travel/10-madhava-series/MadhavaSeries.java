import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Era 2, topic 10: Madhava's series for pi (Madhava of Sangamagrama, Kerala, c. 1350-1425; known through Nilakantha's
 * Tantrasangraha, c. 1500, and Jyesthadeva's Yuktibhasa, c. 1530).
 *
 * HOW IT WORKS
 *   pi/4 = 1 - 1/3 + 1/5 - 1/7 + ...  An infinite sum, with no square roots at all. By itself it is hopeless: the
 *   error after n terms is about 1/(4n), so each new digit costs ten times as many terms. Madhava's improvement: stop
 *   after n terms and add one correction that estimates everything left out. The Kerala texts give three, each better:
 *     R = 1/(4n),   R = n/(4n^2 + 1),   R = (n^2 + 1)/(4n^3 + 5n),
 *   added with the sign of the first term left out. A second series converges fast on its own:
 *     pi = sqrt(12) (1 - 1/(3 x 3) + 1/(5 x 3^2) - 1/(7 x 3^3) + ...).
 *
 * WHAT THIS PROGRAM DOES
 *   1. Counts how many terms of the plain series give 1 to 7 correct decimals.
 *   2. Applies the three end corrections after 5, 10, 20 and 50 terms, in exact decimal arithmetic.
 *   3. Sums 21 terms of the sqrt(12) series, against MacTutor's 3.14159265359.
 *   4. Doubles Archimedes' polygons (Era 1, topic 8) until they agree to 11 decimals, counting the square roots.
 *   5. Full circle: the Chudnovsky series (1988), the series behind modern record computations, to 1,000 digits,
 *      checked against an arctangent formula.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MadhavaSeries.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MadhavaSeries {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final MathContext MC = new MathContext(60);
    static BigDecimal PI;                                 // computed below by an arctangent formula, to 1,050 digits

    static BigDecimal arctanInv(int x, MathContext mc) {  // arctan(1/x) by its series
        BigDecimal xx = BigDecimal.valueOf((long) x * x), term = BigDecimal.ONE.divide(BigDecimal.valueOf(x), mc), sum = term;
        BigDecimal eps = BigDecimal.ONE.movePointLeft(mc.getPrecision() + 2);
        for (int k = 1; term.abs().compareTo(eps) > 0; k++) {
            term = term.divide(xx, mc).negate();
            sum = sum.add(term.divide(BigDecimal.valueOf(2L * k + 1), mc), mc);
        }
        return sum;
    }

    /** Correct decimals of an approximation: how many places agree with pi before the error shows. */
    static int decimals(BigDecimal approx) {
        BigDecimal err = approx.subtract(PI).abs();
        if (err.signum() == 0) return 50;
        int d = 0;
        while (d < 60 && err.compareTo(new BigDecimal("0.5").movePointLeft(d + 1)) < 0) d++;
        return d;
    }

    public static void main(String[] args) {
        MathContext big = new MathContext(1050);
        PI = arctanInv(5, big).multiply(BigDecimal.valueOf(16)).subtract(arctanInv(239, big).multiply(BigDecimal.valueOf(4))).round(big);
        check(PI.toPlainString().startsWith("3.14159265358979323846"), "pi to start");

        // ---- the plain series ---------------------------------------------------------------------------------------
        double piD = Math.PI, s = 0, comp = 0;
        int need = 1;
        StringJoiner terms = new StringJoiner(" ; ");
        for (long n = 1; need <= 7; n++) {
            double term = (n % 2 == 1 ? 1.0 : -1.0) / (2 * n - 1);
            double y = term - comp, t = s + y;               // compensated summation
            comp = (t - s) - y;
            s = t;
            if (Math.abs(4 * s - piD) < 0.5 * Math.pow(10, -need)) {
                // the plain sum oscillates: insist that it stays within the bound from here on for 10% more terms
                boolean stays = true;
                double s2 = s, c2 = comp;
                for (long m = n + 1; m <= n + n / 10 + 2; m++) {
                    double tm = (m % 2 == 1 ? 1.0 : -1.0) / (2 * m - 1), y2 = tm - c2, t2 = s2 + y2;
                    c2 = (t2 - s2) - y2; s2 = t2;
                    if (Math.abs(4 * s2 - piD) >= 0.5 * Math.pow(10, -need)) { stays = false; break; }
                }
                if (stays) { terms.add(need + " decimals: " + n + " terms"); need++; }
            }
        }
        System.out.printf("plain: 4(1 - 1/3 + 1/5 - ...) ; %s%n", terms);

        // ---- the end corrections -------------------------------------------------------------------------------------
        for (int n : new int[]{5, 10, 20, 50}) {
            BigDecimal sum = BigDecimal.ZERO;
            for (int k = 1; k <= n; k++) {
                BigDecimal tk = BigDecimal.ONE.divide(BigDecimal.valueOf(2L * k - 1), MC);
                sum = k % 2 == 1 ? sum.add(tk) : sum.subtract(tk);
            }
            BigDecimal N = BigDecimal.valueOf(n);
            BigDecimal r1 = BigDecimal.ONE.divide(N.multiply(BigDecimal.valueOf(4)), MC);
            BigDecimal r2 = N.divide(N.pow(2).multiply(BigDecimal.valueOf(4)).add(BigDecimal.ONE), MC);
            BigDecimal r3 = N.pow(2).add(BigDecimal.ONE).divide(N.pow(3).multiply(BigDecimal.valueOf(4)).add(N.multiply(BigDecimal.valueOf(5))), MC);
            int sign = n % 2 == 0 ? 1 : -1;                    // the sign of the first term left out
            BigDecimal four = BigDecimal.valueOf(4);
            BigDecimal p0 = sum.multiply(four), p1 = sum.add(r1.multiply(BigDecimal.valueOf(sign))).multiply(four);
            BigDecimal p2 = sum.add(r2.multiply(BigDecimal.valueOf(sign))).multiply(four), p3 = sum.add(r3.multiply(BigDecimal.valueOf(sign))).multiply(four);
            int d0 = decimals(p0), d1 = decimals(p1), d2 = decimals(p2), d3 = decimals(p3);
            check(d0 <= d1 && d1 <= d2 && d2 <= d3, "each correction is at least as good as the one before");
            System.out.printf("corrected %d terms: no correction %d decimals (%s) ; 1/(4n) %d ; n/(4n^2+1) %d ; (n^2+1)/(4n^3+5n) %d (%s)%n",
                    n, d0, p0.round(new MathContext(14)).toPlainString(), d1, d2, d3, p3.round(new MathContext(16)).toPlainString());
        }

        // every n from 2 to 300: each correction strictly better than the one before, and the third error shrinks like 1/n^7
        BigDecimal running = BigDecimal.ONE;
        BigDecimal prevE3 = null;
        for (int n = 1; n <= 300; n++) {
            BigDecimal tk = BigDecimal.ONE.divide(BigDecimal.valueOf(2L * n - 1), MC);
            running = n == 1 ? BigDecimal.ONE : (n % 2 == 1 ? running.add(tk) : running.subtract(tk));
            if (n < 2) continue;
            BigDecimal N = BigDecimal.valueOf(n), sg = BigDecimal.valueOf(n % 2 == 0 ? 1 : -1), quarter = PI.divide(BigDecimal.valueOf(4), MC);
            BigDecimal e0 = running.subtract(quarter).abs();
            BigDecimal e1 = running.add(sg.multiply(BigDecimal.ONE.divide(N.multiply(BigDecimal.valueOf(4)), MC))).subtract(quarter).abs();
            BigDecimal e2 = running.add(sg.multiply(N.divide(N.pow(2).multiply(BigDecimal.valueOf(4)).add(BigDecimal.ONE), MC))).subtract(quarter).abs();
            BigDecimal e3 = running.add(sg.multiply(N.pow(2).add(BigDecimal.ONE).divide(N.pow(3).multiply(BigDecimal.valueOf(4)).add(N.multiply(BigDecimal.valueOf(5))), MC))).subtract(quarter).abs();
            check(e1.compareTo(e0) < 0 && e2.compareTo(e1) < 0 && e3.compareTo(e2) < 0, "each correction improves on the last, n = " + n);
            if (prevE3 != null) check(e3.compareTo(prevE3) < 0, "the third correction's error keeps shrinking");
            prevE3 = e3;
        }

        // ---- the sqrt(12) series ------------------------------------------------------------------------------------
        BigDecimal sum = BigDecimal.ZERO, pow3 = BigDecimal.ONE;
        int dPrev = -1;
        StringJoiner prog = new StringJoiner(" ");
        for (int k = 0; k < 21; k++) {
            BigDecimal term = BigDecimal.ONE.divide(BigDecimal.valueOf(2L * k + 1).multiply(pow3), MC);
            sum = k % 2 == 0 ? sum.add(term) : sum.subtract(term);
            pow3 = pow3.multiply(BigDecimal.valueOf(3));
            BigDecimal approx = sum.multiply(BigDecimal.valueOf(12).sqrt(MC));
            if (k == 4 || k == 9 || k == 14 || k == 20) prog.add((k + 1) + " terms " + decimals(approx));
            dPrev = decimals(approx);
        }
        BigDecimal s12 = sum.multiply(BigDecimal.valueOf(12).sqrt(MC));
        String truncated = s12.setScale(11, RoundingMode.DOWN).toPlainString();
        BigDecimal err12 = s12.subtract(PI);
        check(truncated.equals("3.14159265359"), "21 terms of the sqrt(12) series begin 3.14159265359, MacTutor's value");
        check(err12.abs().compareTo(new BigDecimal("1e-11")) < 0, "and are within 10^-11 of pi");
        System.out.printf("sqrt12: 21 terms give %s, whose first 11 decimals are %s ; error %s ; correct decimals (half-unit test): %s%n",
                s12.round(new MathContext(16)).toPlainString(), truncated, err12.round(new MathContext(2)).toString(), prog);

        // ---- Archimedes' polygons ----------------------------------------------------------------------------------
        // inscribed and circumscribed perimeters over the diameter, from the hexagon, doubling the sides each time
        BigDecimal in6 = BigDecimal.valueOf(3), out6 = BigDecimal.valueOf(2).multiply(BigDecimal.valueOf(3).sqrt(MC));   // 6 x side / 2
        BigDecimal a = out6, b = in6;                            // a = circumscribed, b = inscribed
        int roots = 1, doublings = 0;
        long sides = 6;
        while (true) {
            a = BigDecimal.valueOf(2).multiply(a).multiply(b).divide(a.add(b), MC);   // harmonic mean
            b = a.multiply(b).sqrt(MC);                                               // geometric mean: one square root
            roots++; doublings++; sides *= 2;
            BigDecimal mid = a.add(b).divide(BigDecimal.valueOf(2), MC);
            if (a.subtract(b).compareTo(new BigDecimal("1e-11")) < 0) break;
        }
        check(b.compareTo(PI) < 0 && a.compareTo(PI) > 0, "the polygons trap pi");
        System.out.printf("polygons: %d doublings (a %d-sided polygon) and %d square roots before the two bounds agree to 11 decimals: %s < pi < %s%n",
                doublings, sides, roots, b.round(new MathContext(14)).toPlainString(), a.round(new MathContext(14)).toPlainString());

        // ---- full circle: the Chudnovsky series ---------------------------------------------------------------------
        // 1/pi = 12 sum (-1)^k (6k)! (13591409 + 545140134 k) / ((3k)! (k!)^3 640320^(3k + 3/2))
        MathContext mc = new MathContext(1020);
        BigInteger C3 = BigInteger.valueOf(640320).pow(3);
        BigDecimal total = BigDecimal.ZERO;
        BigInteger num = BigInteger.ONE, den = BigInteger.ONE;                   // (6k)! / ((3k)! (k!)^3 640320^(3k))
        int chTerms = 0;
        for (int k = 0; ; k++) {
            if (k > 0) {
                BigInteger kk = BigInteger.valueOf(k);
                for (int j = 6 * k - 5; j <= 6 * k; j++) num = num.multiply(BigInteger.valueOf(j));
                for (int j = 3 * k - 2; j <= 3 * k; j++) den = den.multiply(BigInteger.valueOf(j));
                den = den.multiply(kk.pow(3)).multiply(C3);
            }
            BigDecimal t = new BigDecimal(num.multiply(BigInteger.valueOf(13591409).add(BigInteger.valueOf(545140134).multiply(BigInteger.valueOf(k)))))
                    .divide(new BigDecimal(den), mc);
            total = k % 2 == 0 ? total.add(t) : total.subtract(t);
            chTerms++;
            if (t.compareTo(BigDecimal.ONE.movePointLeft(1015)) < 0) break;
        }
        BigDecimal sqrtC = BigDecimal.valueOf(640320).sqrt(mc).multiply(BigDecimal.valueOf(640320));   // 640320^(3/2)
        BigDecimal piCh = sqrtC.divide(total.multiply(BigDecimal.valueOf(12)), mc);
        int agree = 0;
        String x1 = piCh.toPlainString(), x2 = PI.toPlainString();
        while (agree < Math.min(x1.length(), x2.length()) && x1.charAt(agree) == x2.charAt(agree)) agree++;
        check(agree - 2 >= 1000, "Chudnovsky and the arctangent formula agree to 1,000 decimals");
        System.out.printf("chudnovsky: %d terms give pi to %d decimals (agreeing with an arctangent formula) ; about %.1f digits per term ; Madhava's sqrt(12) series gains %.2f digits per term%n",
                chTerms, agree - 2, (agree - 2) / (double) chTerms, Math.log10(3));

        System.out.printf("MadhavaSeries: %d checks passed%n", passed);
    }
}
