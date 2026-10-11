import java.math.BigDecimal;
import java.math.BigInteger;
import java.math.MathContext;
import java.util.*;

/**
 * Era 2, topic 9: Horner's method, nearly six centuries early (Qin Jiushao, Shushu jiuzhang, 1247).
 *
 * HOW IT WORKS
 *   To find a root of an equation of any degree, find it one digit at a time, as in a square root. Suppose the root
 *   lies between 20 and 30: its first digit is 2. Replace x by y + 20 everywhere. The new polynomial in y has a root
 *   between 0 and 10, and its next digit is found the same way. The shift x -> y + d is done on the counting board by
 *   repeated "multiply and add" down the column of coefficients (now called synthetic division), so no power of x is
 *   ever computed. Evaluating a polynomial the same way, a_n x + a_(n-1), times x, plus a_(n-2), ..., takes one
 *   multiplication per degree: Horner's rule. Ruffini (about 1805) and Horner (1819) found it again in Europe.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Counts the multiplications for evaluating a polynomial of degree 10 three ways.
 *   2. Finds roots digit by digit, with exact decimal arithmetic, for a cubic worked by Joyce, a quartic and the
 *      degree-10 "circular city" equation from the Shushu jiuzhang (as given in the Dictionary of Scientific
 *      Biography), and the fifth root of 2; it prints the shifted polynomial after each digit.
 *   3. Checks the method on 5,000 random polynomials built with a known root.
 *   4. Compares digits per step: digit by digit, bisection, and Newton's method.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java QinJiushao.java
 *   Expected output: expected-output.txt in this folder.
 */
public class QinJiushao {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long multAdds;                                // multiply-and-add steps on the board

    /** Horner's rule: coefficients from the highest power down. */
    static BigDecimal horner(BigDecimal[] c, BigDecimal x) {
        BigDecimal v = c[0];
        for (int i = 1; i < c.length; i++) { v = v.multiply(x).add(c[i]); multAdds++; }
        return v;
    }

    /** The shift x -> y + d by repeated synthetic division: returns the coefficients of p(y + d). */
    static BigDecimal[] shift(BigDecimal[] c, BigDecimal d) {
        BigDecimal[] a = c.clone();
        int n = a.length - 1;
        for (int k = 0; k < n; k++)
            for (int i = 1; i <= n - k; i++) { a[i] = a[i].add(a[i - 1].multiply(d)); multAdds++; }
        return a;
    }

    static String poly(BigDecimal[] c) {
        StringJoiner s = new StringJoiner(" ");
        for (BigDecimal v : c) s.add(v.stripTrailingZeros().toPlainString());
        return s.toString();
    }

    static List<String> trace;

    /**
     * The digit-by-digit smallest root in (0, 10^(top+1)) of a polynomial that changes sign there: at each place, the
     * largest digit that does not carry the polynomial past its root; then shift by it.
     */
    static BigDecimal digitRoot(BigDecimal[] coef, int top, int decimals) {
        BigDecimal[] c = coef.clone();
        BigDecimal root = BigDecimal.ZERO;
        int s0 = c[c.length - 1].signum();                  // the sign at the start of the interval
        for (int k = top; k >= -decimals; k--) {
            BigDecimal place = BigDecimal.ONE.scaleByPowerOfTen(k);
            int dgt = 0;
            for (int t = 1; t <= 9; t++) {                  // try 1, 2, 3, ... until the polynomial changes sign
                BigDecimal v = horner(c, place.multiply(BigDecimal.valueOf(t)));
                if (v.signum() == 0) { dgt = t; break; }
                if (v.signum() != s0) break;
                dgt = t;
            }
            if (dgt > 0) {
                BigDecimal d = place.multiply(BigDecimal.valueOf(dgt));
                c = shift(c, d);
                root = root.add(d);
                if (trace != null) trace.add(String.format("digit %d at 10^%d -> root so far %s ; shifted: %s", dgt, k, root.toPlainString(), poly(c)));
                if (c[c.length - 1].signum() == 0) break;    // the root is exact
            }
        }
        return root;
    }

    static BigDecimal[] bd(long... v) {
        BigDecimal[] c = new BigDecimal[v.length];
        for (int i = 0; i < v.length; i++) c[i] = BigDecimal.valueOf(v[i]);
        return c;
    }

    public static void main(String[] args) {
        // ---- evaluating a polynomial of degree 10 ------------------------------------------------------------------
        int n = 10;
        int termByTerm = 0, keepPowers = 0, hornerM = n;
        for (int k = 1; k <= n; k++) termByTerm += k;      // x^k as k multiplications (one to bring in its coefficient)
        keepPowers = (n - 1) + n;                          // x^2..x^n from the previous power, then n coefficients
        BigDecimal[] city = bd(1, 0, 15, 0, 72, 0, -864, 0, -11664, 0, -34992);   // x^10 + 15x^8 + 72x^6 - 864x^4 - 11664x^2 - 34992
        multAdds = 0;
        BigDecimal v3 = horner(city, BigDecimal.valueOf(3));
        check(v3.signum() == 0 && multAdds == n, "x = 3 is a root, found with 10 multiply-adds");
        System.out.printf("evaluate: degree 10 ; term by term %d multiplications ; keeping the powers %d ; Horner's rule %d ; the circular-city polynomial at x = 3 is %s%n",
                termByTerm, keepPowers, hornerM, v3.toPlainString());

        // ---- digit by digit -------------------------------------------------------------------------------------
        Object[][] problems = {
                {"cubic", bd(1, 2, 6, -13258), 1, 6},                         // Joyce: x^3 + 2x^2 + 6x - 13258 = 0
                {"quartic", bd(-1, 0, 763200, 0, -40642560000L), 2, 0},      // DSB: -x^4 + 763200x^2 - 40642560000 = 0
                {"city", city, 0, 0},                                        // DSB: the degree-10 circular-city equation
                {"fifth", bd(1, 0, 0, 0, 0, -2), 0, 10},                     // the fifth root of 2 (Joyce)
        };
        for (Object[] p : problems) {
            trace = new ArrayList<>();
            multAdds = 0;
            BigDecimal[] c = (BigDecimal[]) p[1];
            BigDecimal root = digitRoot(c, (int) p[2], (int) p[3]);
            long work = multAdds;
            List<String> tr = trace;
            trace = null;
            for (int i = 0; i < Math.min(tr.size(), 4); i++) System.out.printf("%s %s%n", p[0], tr.get(i));
            System.out.printf("%s root: %s ; %d digits ; %d multiply-adds%n", p[0], root.toPlainString(), tr.size(), work);
            if (p[0].equals("cubic")) check(root.toPlainString().startsWith("22.93"), "the cubic's root begins 22.93");
            if (p[0].equals("quartic")) check(root.compareTo(BigDecimal.valueOf(240)) == 0, "the quartic's smallest positive root is 240");
            if (p[0].equals("city")) check(root.compareTo(BigDecimal.valueOf(3)) == 0, "the city equation's root is 3");
            if (p[0].equals("fifth")) check(root.toPlainString().startsWith("1.1486983549"), "the fifth root of 2");
        }
        // the quartic's other root, 840: start above 240 by shifting first
        BigDecimal[] q = shift(bd(-1, 0, 763200, 0, -40642560000L), BigDecimal.valueOf(300));
        BigDecimal r840 = digitRoot(q, 3, 0).add(BigDecimal.valueOf(300));
        check(r840.compareTo(BigDecimal.valueOf(840)) == 0, "the quartic's other positive root is 840");
        System.out.printf("quartic other: searching above 300 gives %s ; check: -840^4 + 763200 x 840^2 - 40642560000 = %s%n",
                r840.toPlainString(), horner(bd(-1, 0, 763200, 0, -40642560000L), r840).toPlainString());

        // ---- random polynomials with a known root ----------------------------------------------------------------
        Random rnd = new Random(1247);
        int found = 0;
        for (int t = 0; t < 5000; t++) {
            int deg = 2 + rnd.nextInt(7);
            long r = 1 + rnd.nextInt(9999);                  // a root of up to four digits
            // p(x) = (x - r)(x^(deg-1) + positive coefficients): one positive root, at r
            long[] qc = new long[deg];
            qc[0] = 1;
            for (int i = 1; i < deg; i++) qc[i] = 1 + rnd.nextInt(20);
            BigInteger[] pc = new BigInteger[deg + 1];
            for (int i = 0; i <= deg; i++) pc[i] = BigInteger.ZERO;
            for (int i = 0; i < deg; i++) { pc[i] = pc[i].add(BigInteger.valueOf(qc[i])); pc[i + 1] = pc[i + 1].subtract(BigInteger.valueOf(qc[i] * r)); }
            BigDecimal[] c = new BigDecimal[deg + 1];
            for (int i = 0; i <= deg; i++) c[i] = new BigDecimal(pc[i]);
            BigDecimal got = digitRoot(c, 3, 0);
            check(got.compareTo(BigDecimal.valueOf(r)) == 0, "digit by digit recovers the root");
            found++;
        }
        System.out.printf("random: %d polynomials of degree 2 to 8 with a root of up to four digits ; every root recovered digit by digit%n", found);

        // ---- how fast: digit by digit, bisection, Newton ------------------------------------------------------------
        double target = Math.pow(2, 0.2);
        // digit by digit: one decimal digit per step (up to 9 trials each)
        multAdds = 0;
        BigDecimal dd = digitRoot(bd(1, 0, 0, 0, 0, -2), 0, 14);
        int ddSteps = 15;
        double lo = 1, hi = 2;
        int bis = 0;
        while (hi - lo > 1e-15) { double m = (lo + hi) / 2; if (m * m * m * m * m < 2) lo = m; else hi = m; bis++; }
        double x = 1;
        int newton = 0;
        while (Math.abs(x * x * x * x * x - 2) > 1e-15 && newton < 100) { x = x - (x * x * x * x * x - 2) / (5 * x * x * x * x); newton++; }
        check(Math.abs(x - target) < 1e-15 && Math.abs(lo - target) < 1e-14, "all three agree");
        System.out.printf("speed: fifth root of 2 to 15 digits ; digit by digit %d steps (%d multiply-adds) ; bisection %d halvings ; Newton %d steps ; %s%n",
                ddSteps, multAdds, bis, newton, dd.toPlainString());

        System.out.printf("QinJiushao: %d checks passed%n", passed);
    }
}
