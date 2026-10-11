import java.math.BigDecimal;
import java.math.MathContext;
import java.math.RoundingMode;
import java.util.*;

/**
 * Era 3, topic 5: Newton's method (Newton 1669, printed 1685 and 1711; Raphson 1690; Simpson 1740).
 *
 * HOW IT WORKS
 *   Guess a root x of f(x) = 0. Near the guess the curve is almost a straight line, the tangent, whose slope is f'(x);
 *   the tangent crosses zero at x - f(x)/f'(x), which is the next guess. Near a simple root the error is roughly
 *   squared at every step, so the number of correct digits roughly doubles. Newton himself did it differently: for
 *   x^3 - 2x - 5 = 0 he put x = 2 + p, wrote out the new polynomial in p, kept only its two lowest terms (10p - 1 = 0, so
 *   p = 0.1), put p = 0.1 + q, and so on, keeping more digits each time. Raphson (1690) applied the correction to the
 *   original equation over and over instead; Simpson (1740) wrote it with fluxions for any equation, and for two
 *   equations in two unknowns.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Repeats Newton's own steps on x^3 - 2x - 5 = 0 with exact polynomial shifts, reaching his 2.09455147.
 *   2. Runs Raphson's form to 60 digits and shows the correct digits doubling.
 *   3. Compares the work with digit-by-digit extraction (Era 2, topic 9) and with bisection.
 *   4. Solves a non-polynomial equation (cos x = x) and a system of two equations by Simpson's method (Cramer's rule
 *      for each step).
 *   5. Shows the method's failures: a 2-cycle, a slow double root, and the basins of z^3 = 1 in the complex plane.
 *   6. Full circle: the Babylonian square root (Era 1, topic 4) is Newton's method, and so is a reciprocal computed
 *      without division.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java NewtonsMethod.java
 *   Expected output: expected-output.txt in this folder.
 */
public class NewtonsMethod {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final MathContext MC = new MathContext(80);

    /** Coefficients highest power first: shift x -> x + d (repeated synthetic division, as in Era 2 topic 9). */
    static BigDecimal[] shift(BigDecimal[] c, BigDecimal d) {
        BigDecimal[] a = c.clone();
        int n = a.length - 1;
        for (int k = 0; k < n; k++) for (int i = 1; i <= n - k; i++) a[i] = a[i].add(a[i - 1].multiply(d));
        return a;
    }

    static String poly(BigDecimal[] c) {
        StringJoiner s = new StringJoiner(" ");
        int n = c.length - 1;
        for (int i = 0; i <= n; i++) {
            BigDecimal v = c[i].stripTrailingZeros();
            String t = v.abs().toPlainString(), term = (n - i == 0 ? t : (v.abs().compareTo(BigDecimal.ONE) == 0 ? "" : t) + "p" + (n - i > 1 ? "^" + (n - i) : ""));
            s.add((v.signum() < 0 ? "- " : (i == 0 ? "" : "+ ")) + term);
        }
        return s.toString();
    }

    static BigDecimal f(BigDecimal x) { return x.pow(3).subtract(x.multiply(BigDecimal.valueOf(2))).subtract(BigDecimal.valueOf(5)); }

    static BigDecimal fp(BigDecimal x) { return x.pow(2).multiply(BigDecimal.valueOf(3)).subtract(BigDecimal.valueOf(2)); }

    static int correct(BigDecimal approx, BigDecimal truth) {
        BigDecimal err = approx.subtract(truth).abs();
        int d = 0;
        while (d < 70 && err.compareTo(new BigDecimal("0.5").movePointLeft(d + 1)) < 0) d++;
        return d;
    }

    public static void main(String[] args) {
        // the true root, to 70 digits, by many Raphson steps
        BigDecimal root = BigDecimal.valueOf(2);
        for (int i = 0; i < 20; i++) root = root.subtract(f(root).divide(fp(root), MC), MC);
        check(f(root).abs().compareTo(new BigDecimal("1e-75")) < 0, "the reference root");

        // ---- 1. Newton's own steps -----------------------------------------------------------------------------------
        BigDecimal[] c0 = {BigDecimal.ONE, BigDecimal.ZERO, BigDecimal.valueOf(-2), BigDecimal.valueOf(-5)};
        String[] runs = new String[2];
        BigDecimal[] finals = new BigDecimal[2];
        for (int variant = 0; variant < 2; variant++) {           // 0: keep every term ; 1: drop the cubic term after the second step, as negligible
            BigDecimal x = BigDecimal.valueOf(2);
            BigDecimal[] c = shift(c0, x);                          // the polynomial in p, where x = 2 + p
            StringJoiner steps = new StringJoiner(" ; ");
            steps.add("x = 2 + p: " + poly(c) + " = 0");
            int keep = 1;
            for (int k = 0; k < 3; k++) {
                int n = c.length - 1;
                BigDecimal lin = c[n - 1], con = c[n];             // keep only the two lowest terms: lin * p + con = 0
                BigDecimal corr = con.negate().divide(lin, new MathContext(keep, RoundingMode.HALF_EVEN));
                x = x.add(corr);
                if (variant == 1 && k == 1) c = Arrays.copyOfRange(c, 1, c.length);   // drop the cubic term
                c = shift(c, corr);
                steps.add(String.format("%s p %s %s = 0 gives %s (%d figure%s) ; x = %s", lin.stripTrailingZeros().toPlainString(),
                        con.signum() < 0 ? "-" : "+", con.abs().stripTrailingZeros().toPlainString(), corr.toPlainString(), keep, keep == 1 ? "" : "s", x.toPlainString()));
                keep *= 2;
            }
            runs[variant] = steps.toString();
            finals[variant] = x;
        }
        check(finals[0].toPlainString().equals("2.09455148"), "keeping every term gives 2.09455148");
        check(finals[1].toPlainString().equals("2.09455147"), "dropping the cubic term before the third step gives Newton's 2.09455147");
        System.out.printf("newton: x^3 - 2x - 5 = 0 from x = 2 ; dropping the cubic term before the third step: %s ; keeping every term instead ends at %s ; true root %s ; %d correct decimals%n",
                runs[1], finals[0].toPlainString(), root.round(new MathContext(20)).toPlainString(), correct(finals[1], root));

        // ---- 2. Raphson's form: the digits double ----------------------------------------------------------------------------
        BigDecimal r = BigDecimal.valueOf(2);
        StringJoiner dbl = new StringJoiner(" ; ");
        int prev = 0;
        for (int i = 1; i <= 5; i++) {
            r = r.subtract(f(r).divide(fp(r), MC), MC);
            int cd = correct(r, root);
            if (i >= 3) check(cd >= 2 * prev - 2, "the correct decimals roughly double");
            prev = cd;
            dbl.add(String.format("step %d: %d", i, cd));
        }
        System.out.printf("raphson: x <- x - f(x)/f'(x) from 2, correct decimals after each step: %s%n", dbl);

        // ---- 3. the work: Newton against digit-by-digit and bisection, for 60 decimals ------------------------------------------
        int target = 60;
        int nNewton = 0;
        BigDecimal y = BigDecimal.valueOf(2);
        while (correct(y, root) < target) { y = y.subtract(f(y).divide(fp(y), MC), MC); nNewton++; }
        int nBis = 0;
        BigDecimal lo = BigDecimal.valueOf(2), hi = BigDecimal.valueOf(3), two = BigDecimal.valueOf(2);
        while (correct(lo.add(hi).divide(two, MC), root) < target) {
            BigDecimal mid = lo.add(hi).divide(two, MC);
            if (f(mid).signum() < 0) lo = mid; else hi = mid;
            nBis++;
        }
        int nDigit = target + 1;                                // digit by digit: one digit per step, up to 9 trials each
        check(nNewton < 10 && nBis > 190, "Newton needs a handful of steps, bisection about 200");
        System.out.printf("work: %d correct decimals of the root ; Newton %d steps ; digit by digit %d steps (one digit each) ; bisection %d halvings%n",
                target, nNewton, nDigit, nBis);

        // a survey: polynomials of degree 3 to 6 with a known simple root r, started 1% away from it
        Random rnd = new Random(1669);
        int[] hist = new int[20];
        int surveyN = 10000;
        long totalSteps = 0;
        for (int tr = 0; tr < surveyN; tr++) {
            int deg = 3 + rnd.nextInt(4);
            double rt = 1 + rnd.nextInt(9) + rnd.nextDouble();
            double[] q = new double[deg];                          // (x - rt) times a polynomial with no real root near rt: x^(deg-1) + ... with positive coefficients
            for (int i = 0; i < deg; i++) q[i] = 1 + rnd.nextInt(5);
            java.util.function.DoubleUnaryOperator P = xx -> { double v = 0; for (double cq : q) v = v * xx + cq; return (xx - rt) * v; };
            java.util.function.DoubleUnaryOperator D = xx -> { double v = 0, dv = 0; for (double cq : q) { dv = dv * xx + v; v = v * xx + cq; } return v + (xx - rt) * dv; };
            double xx = rt * 1.01;
            int k = 0;
            while (Math.abs(xx - rt) > 1e-12 * rt && k < 19) { xx -= P.applyAsDouble(xx) / D.applyAsDouble(xx); k++; }
            check(Math.abs(xx - rt) <= 1e-12 * rt, "Newton converges from 1% away");
            hist[k]++; totalSteps += k;
        }
        StringJoiner hs = new StringJoiner(" ; ");
        for (int k = 0; k < 20; k++) if (hist[k] > 0) hs.add(String.format("%d steps: %,d", k, hist[k]));
        System.out.printf("survey: %,d polynomials of degree 3 to 6 with a known root, started 1%% away from it, to 12 significant figures: %s ; average %.2f steps%n",
                surveyN, hs, totalSteps / (double) surveyN);

        // ---- 4. Simpson: any equation, and systems ------------------------------------------------------------------------------
        double t = 1;
        int it = 0;
        while (Math.abs(Math.cos(t) - t) > 1e-15 && it < 50) { t = t - (Math.cos(t) - t) / (-Math.sin(t) - 1); it++; }
        check(Math.abs(Math.cos(t) - t) < 1e-15, "cos x = x");
        // x^2 + y^2 = 4, x y = 1, from (2, 0.5): Cramer's rule for the 2x2 linear step
        double u = 2, v = 0.5;
        int its = 0;
        StringJoiner sys = new StringJoiner(" ; ");
        for (; its < 8; its++) {
            double F = u * u + v * v - 4, G = u * v - 1;
            double a = 2 * u, b = 2 * v, cc = v, dd = u, det = a * dd - b * cc;
            double du = (-F * dd + b * G) / det, dv = (-a * G + cc * F) / det;   // Cramer's rule
            u += du; v += dv;
            if (its < 4) sys.add(String.format("(%.12f, %.12f)", u, v));
            if (Math.abs(du) + Math.abs(dv) < 1e-15) { its++; break; }
        }
        check(Math.abs(u * u + v * v - 4) < 1e-14 && Math.abs(u * v - 1) < 1e-14, "the system is solved");
        System.out.printf("simpson: cos x = x from 1: x = %.15f in %d steps ; x^2 + y^2 = 4 and xy = 1 from (2, 0.5), Cramer's rule at each step: %s ; solution (%.15f, %.15f)%n",
                t, it, sys, u, v);

        // ---- 5. failures --------------------------------------------------------------------------------------------------------
        double z = 0;                                            // x^3 - 2x + 2 from 0: 0, 1, 0, 1, ...
        StringJoiner cyc = new StringJoiner(", ");
        for (int i = 0; i < 6; i++) { cyc.add(String.format("%.0f", z)); z = z - (z * z * z - 2 * z + 2) / (3 * z * z - 2); }
        check(cyc.toString().equals("0, 1, 0, 1, 0, 1"), "a 2-cycle");
        double w = 2;                                            // (x - 1)^2 (x + 2): a double root at 1 loses the doubling
        int wSteps = 0;
        while (Math.abs(w - 1) > 1e-6 && wSteps < 200) { w = w - ((w - 1) * (w - 1) * (w + 2)) / (2 * (w - 1) * (w + 2) + (w - 1) * (w - 1)); wSteps++; }
        double s3 = 2;
        int s3Steps = 0;
        while (Math.abs(s3 - 1) > 1e-6 && s3Steps < 200) { s3 = s3 - (s3 * s3 * s3 - 1) / (3 * s3 * s3); s3Steps++; }
        // basins of z^3 = 1 on a grid of starting points in the complex plane
        int G = 600, conv = 0, slow = 0;
        int[] toRoot = new int[3];
        double[][] roots3 = {{1, 0}, {-0.5, Math.sqrt(3) / 2}, {-0.5, -Math.sqrt(3) / 2}};
        long totalIt = 0;
        for (int i = 0; i < G; i++)
            for (int j = 0; j < G; j++) {
                double re = -2 + 4.0 * (i + 0.5) / G, im = -2 + 4.0 * (j + 0.5) / G;
                int k = 0, which = -1;
                for (; k < 100 && which < 0; k++) {
                    double r2 = re * re - im * im, i2 = 2 * re * im;                 // z^2
                    double r3 = r2 * re - i2 * im, i3 = r2 * im + i2 * re;           // z^3
                    double nr = r3 - 1, ni = i3, dr = 3 * r2, di = 3 * i2, dd2 = dr * dr + di * di;
                    if (dd2 == 0) break;
                    re -= (nr * dr + ni * di) / dd2; im -= (ni * dr - nr * di) / dd2;
                    for (int q = 0; q < 3; q++) if (Math.hypot(re - roots3[q][0], im - roots3[q][1]) < 1e-9) which = q;
                }
                if (which >= 0) { toRoot[which]++; conv++; totalIt += k; if (k > 20) slow++; }
            }
        check(conv > 0.99 * G * G, "almost every starting point converges");
        System.out.printf("fail: x^3 - 2x + 2 from 0 cycles %s, ... ; a double root, (x - 1)^2 (x + 2) from 2, needs %d steps to come within 1e-6 (a simple root, x^3 - 1 from 2, needs %d) ; z^3 = 1 from %,d starting points in the square |Re|, |Im| < 2: %,d converge (to 1: %,d ; to the other two: %,d and %,d), %,d take more than 20 steps, on average %.1f steps%n",
                cyc, wSteps, s3Steps, G * G, conv, toRoot[0], toRoot[1], toRoot[2], slow, totalIt / (double) conv);

        // ---- 6. full circle ------------------------------------------------------------------------------------------------------
        // exact fractions p/q: the Babylonian rule averages x and 2/x; Newton subtracts (x^2 - 2)/(2x)
        java.math.BigInteger bp = java.math.BigInteger.ONE, bq = java.math.BigInteger.ONE, np = bp, nq = bq, TWO = java.math.BigInteger.TWO;
        StringJoiner same = new StringJoiner(", ");
        for (int i = 0; i < 4; i++) {
            // Babylonian: (p/q + 2q/p) / 2 = (p^2 + 2q^2) / (2pq)
            java.math.BigInteger p1 = bp.multiply(bp).add(TWO.multiply(bq).multiply(bq)), q1 = TWO.multiply(bp).multiply(bq);
            // Newton: p/q - (p^2/q^2 - 2) / (2p/q) = p/q - (p^2 - 2q^2) / (2pq) = (2p^2 - p^2 + 2q^2) / (2pq), computed as the subtraction
            java.math.BigInteger num = np.multiply(TWO.multiply(np)).subtract(np.multiply(np).subtract(TWO.multiply(nq).multiply(nq))), den = TWO.multiply(np).multiply(nq);
            java.math.BigInteger g1 = p1.gcd(q1), g2 = num.gcd(den);
            bp = p1.divide(g1); bq = q1.divide(g1); np = num.divide(g2); nq = den.divide(g2);
            check(bp.equals(np) && bq.equals(nq), "the Babylonian step is Newton's step, exactly");
            same.add(bp + "/" + bq);
        }
        // 1/a without dividing: x <- x (2 - a x)
        BigDecimal A = new BigDecimal("7"), rec = new BigDecimal("0.1"), truth = BigDecimal.ONE.divide(A, MC);
        StringJoiner recd = new StringJoiner(", ");
        for (int i = 1; i <= 7; i++) { rec = rec.multiply(BigDecimal.valueOf(2).subtract(A.multiply(rec, MC)), MC); recd.add(String.valueOf(correct(rec, truth))); }
        check(correct(rec, truth) >= 60, "the reciprocal converges");
        System.out.printf("circle: square root of 2 from 1 by the Babylonian rule and by Newton's method, the same fractions at every step: %s ; 1/7 without division, x <- x(2 - 7x) from 0.1, correct decimals: %s%n", same, recd);

        System.out.printf("NewtonsMethod: %d checks passed%n", passed);
    }
}
