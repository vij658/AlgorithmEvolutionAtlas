import java.math.BigInteger;
import java.util.*;

/**
 * Era 3, topic 1: Cardano's cubic (del Ferro c. 1515, Tartaglia 1535, Cardano's Ars Magna 1545, Bombelli 1572).
 *
 * HOW IT WORKS
 *   Any cubic a x^3 + b x^2 + c x + d = 0 becomes y^3 + p y + q = 0 after the shift x = y - b/(3a), which removes the
 *   square term. Now look for y as a sum u + v. Then y^3 = u^3 + v^3 + 3uv(u + v), so if 3uv = -p, the equation
 *   becomes u^3 + v^3 = -q. With uv fixed, u^3 and v^3 are the two roots of the quadratic t^2 + q t - p^3/27 = 0:
 *     u^3, v^3 = -q/2 +- sqrt(D),   D = (q/2)^2 + (p/3)^3,   y = cbrt(u^3) + cbrt(v^3).
 *   A cubic has been turned into a quadratic plus two cube roots. The trap: when the cubic has three real roots, D is
 *   negative, so the recipe passes through the square root of a negative number (the "irreducible case"). Bombelli
 *   (1572) calculated straight through it: for x^3 = 15x + 4, D = -121, and the cube roots of 2 + sqrt(-121) and
 *   2 - sqrt(-121) are 2 + i and 2 - i, whose sum is the real root 4.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Removes the square term from a cubic and solves it by the formula, step by step.
 *   2. Repeats Cardano's first calculation with complex numbers, (5 + sqrt(-15))(5 - sqrt(-15)) = 40, and Bombelli's
 *      x^3 = 15x + 4 in exact integer complex arithmetic.
 *   3. Surveys random cubics: how often the formula must pass through square roots of negatives.
 *   4. Checks the formula, in complex arithmetic, on 100,000 random cubics with known roots.
 *   5. Shows where the formula fails in floating point (cancellation), and how a few correction steps repair it.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CardanoCubic.java
 *   Expected output: expected-output.txt in this folder.
 */
public class CardanoCubic {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** A complex number a + bi in double precision. */
    record C(double re, double im) {
        C plus(C o) { return new C(re + o.re, im + o.im); }
        C minus(C o) { return new C(re - o.re, im - o.im); }
        C times(C o) { return new C(re * o.re - im * o.im, re * o.im + im * o.re); }
        C times(double k) { return new C(re * k, im * k); }
        C div(C o) { double d = o.re * o.re + o.im * o.im; return new C((re * o.re + im * o.im) / d, (im * o.re - re * o.im) / d); }
        double abs() { return Math.hypot(re, im); }
        static C sqrt(double x) { return x >= 0 ? new C(Math.sqrt(x), 0) : new C(0, Math.sqrt(-x)); }
        /** The principal cube root. */
        C cbrt() {
            if (im == 0) return new C(Math.cbrt(re), 0);
            double r = Math.cbrt(abs()), t = Math.atan2(im, re) / 3;
            return new C(r * Math.cos(t), r * Math.sin(t));
        }
    }

    static final C OMEGA = new C(-0.5, Math.sqrt(3) / 2);   // a cube root of 1: the other two cube roots are u*w, u*w^2

    /** The three roots of y^3 + p y + q = 0 by Cardano's formula, in complex arithmetic. */
    static C[] cardano(double p, double q) {
        double D = (q / 2) * (q / 2) + (p / 3) * (p / 3) * (p / 3);
        C s = C.sqrt(D);
        C u3 = new C(-q / 2, 0).plus(s);
        C u = u3.cbrt();
        if (u.abs() < 1e-300) { u3 = new C(-q / 2, 0).minus(s); u = u3.cbrt(); }
        C[] y = new C[3];
        C uk = u;
        for (int k = 0; k < 3; k++) {
            C v = uk.abs() < 1e-300 ? new C(0, 0) : new C(-p / 3, 0).div(uk);   // 3uv = -p
            y[k] = uk.plus(v);
            uk = uk.times(OMEGA);
        }
        return y;
    }

    // ---- exact Gaussian integers, for Bombelli ------------------------------------------------------------------
    record G(BigInteger re, BigInteger im) {
        static G of(long a, long b) { return new G(BigInteger.valueOf(a), BigInteger.valueOf(b)); }
        G times(G o) { return new G(re.multiply(o.re).subtract(im.multiply(o.im)), re.multiply(o.im).add(im.multiply(o.re))); }
        G plus(G o) { return new G(re.add(o.re), im.add(o.im)); }
        G cube() { return times(this).times(this); }
        public String toString() {
            int s = im.signum();
            return re + (s >= 0 ? " + " : " - ") + (im.abs().equals(BigInteger.ONE) ? "" : im.abs().toString()) + "i";
        }
    }

    public static void main(String[] args) {
        // ---- 1. removing the square term ------------------------------------------------------------------------
        // 2x^3 - 6x^2 + 18x - 34 = 0: the shift and the depressed cubic are computed, not assumed
        double a = 2, b = -6, c = 18, d = -34;
        double s = -b / (3 * a);
        double p = (3 * a * c - b * b) / (3 * a * a), q = (2 * b * b * b - 9 * a * b * c + 27 * a * a * d) / (27 * a * a * a);
        double Dd = (q / 2) * (q / 2) + (p / 3) * (p / 3) * (p / 3);
        C[] ys = cardano(p, q);
        double x0 = ys[0].re + s;
        check(Math.abs(((a * x0 + b) * x0 + c) * x0 + d) < 1e-9, "the shifted root solves the original cubic");
        System.out.printf("depress: 2x^3 - 6x^2 + 18x - 34 = 0 ; shift x = y + %s ; y^3 + %sy %s = 0 ; D = (q/2)^2 + (p/3)^3 = %s ; u^3 = %s, v^3 = %s ; y = %s ; x = %s%n",
                fmt(s), fmt(p), (q < 0 ? "- " + fmt(-q) : "+ " + fmt(q)), fmt(Dd), fmt(-q / 2 + Math.sqrt(Dd)), fmt(-q / 2 - Math.sqrt(Dd)), fmt(ys[0].re), fmt(x0));

        // the formula on y^3 + 6y = 20, step by step
        double p1 = 6, q1 = -20, D1 = (q1 / 2) * (q1 / 2) + (p1 / 3) * (p1 / 3) * (p1 / 3);
        double u1 = Math.cbrt(-q1 / 2 + Math.sqrt(D1)), v1 = Math.cbrt(-q1 / 2 - Math.sqrt(D1));
        check(D1 == 108 && Math.abs(u1 + v1 - 2) < 1e-12, "x^3 + 6x = 20 has the root 2 = cbrt(sqrt108 + 10) - cbrt(sqrt108 - 10)");
        System.out.printf("formula: x^3 + 6x = 20 ; D = %s ; u = cbrt(sqrt(108) + 10) = %.12f ; v = -cbrt(sqrt(108) - 10) = %.12f ; x = u + v = %.12f%n", fmt(D1), u1, v1, u1 + v1);

        // ---- 2. complex numbers: Cardano's product and Bombelli's cubic ---------------------------------------------
        // (5 + sqrt(-15)) (5 - sqrt(-15)) : with sqrt(-15) = r i, r^2 = 15
        BigInteger re = BigInteger.valueOf(25), imSq = BigInteger.valueOf(15);   // 5*5 - (r i)(-r i) = 25 + 15 ... = 25 - (-15)
        BigInteger prod = re.add(imSq);
        check(prod.intValue() == 40, "(5 + sqrt(-15))(5 - sqrt(-15)) = 40");
        System.out.printf("product: (5 + sqrt(-15)) + (5 - sqrt(-15)) = 10 ; (5 + sqrt(-15)) x (5 - sqrt(-15)) = 25 - (-15) = %d%n", prod);

        // Bombelli: x^3 = 15x + 4, i.e. y^3 - 15y - 4 = 0: p = -15, q = -4
        long pB = -15, qB = -4;
        long Dnum = qB * qB / 4 + pB * pB * pB / 27;               // (q/2)^2 + (p/3)^3 = 4 - 125
        check(Dnum == -121, "D = -121");
        G w1 = G.of(2, 11), w2 = G.of(2, -11);                       // -q/2 +- sqrt(D) = 2 +- 11i
        // search the Gaussian integers a + bi with |a|, |b| <= 5 for a cube root, as Bombelli did by trying a + bi
        G r1 = null;
        int tried = 0;
        for (int x = -5; x <= 5 && r1 == null; x++)
            for (int y = -5; y <= 5; y++) { tried++; if (G.of(x, y).cube().equals(w1)) { r1 = G.of(x, y); break; } }
        G r2 = new G(r1.re(), r1.im().negate());
        check(r2.cube().equals(w2), "the conjugate is a cube root of 2 - 11i");
        G sum = r1.plus(r2);
        check(sum.im().signum() == 0 && sum.re().intValue() == 4, "the root is 4");
        check(4 * 4 * 4 == 15 * 4 + 4, "4^3 = 15 x 4 + 4");
        // the other two roots, from x^2 + 4x + 1 = 0 after dividing by (x - 4)
        double o1 = -2 + Math.sqrt(3), o2 = -2 - Math.sqrt(3);
        check(Math.abs(o1 * o1 * o1 - 15 * o1 - 4) < 1e-12 && Math.abs(o2 * o2 * o2 - 15 * o2 - 4) < 1e-12, "the other roots are -2 +- sqrt 3");
        C[] bomb = cardano(-15, -4);
        int realRoots = 0;
        for (C z : bomb) if (Math.abs(z.im()) < 1e-9) realRoots++;
        check(realRoots == 3, "all three roots are real, though D < 0");
        System.out.printf("bombelli: x^3 = 15x + 4 ; D = (q/2)^2 + (p/3)^3 = %d ; u^3 = %s, v^3 = %s ; trying a + bi with |a|,|b| <= 5 (%d tries): (%s)^3 = %s, (%s)^3 = %s ; x = %s ; the other roots -2 + sqrt3 = %.6f and -2 - sqrt3 = %.6f, all real%n",
                Dnum, w1, w2, tried, r1, r1.cube(), r2, r2.cube(), sum.re(), o1, o2);

        // ---- 3. survey: how often does the formula need square roots of negatives? ------------------------------------
        Random rnd = new Random(1545);
        int threeReal = 0, oneReal = 0, n = 100000, negD = 0, zeroD = 0;
        for (int t = 0; t < n; t++) {
            int A = rnd.nextInt(41) - 20, B = rnd.nextInt(41) - 20, Cc = rnd.nextInt(41) - 20;   // x^3 + A x^2 + B x + C
            double pp = B - A * A / 3.0, qq = 2.0 * A * A * A / 27 - A * B / 3.0 + Cc;
            double DD = (qq / 2) * (qq / 2) + (pp / 3) * (pp / 3) * (pp / 3);
            // count real roots by sign changes of the cubic itself, independent of D
            int real = realRootCount(A, B, Cc);
            if (real == 3) threeReal++; else oneReal++;
            if (DD < -1e-9) { negD++; check(real == 3, "D < 0 exactly when there are three real roots"); }
            else if (DD > 1e-9) check(real == 1, "D > 0 exactly when there is one real root");
            else zeroD++;
        }
        int intRoots = 0, intNeg = 0;
        for (int t = 0; t < n; t++) {                           // cubics with three distinct whole-number roots
            int r1i = rnd.nextInt(41) - 20, r2i, r3i;
            do { r2i = rnd.nextInt(41) - 20; } while (r2i == r1i);
            do { r3i = rnd.nextInt(41) - 20; } while (r3i == r1i || r3i == r2i);
            double A = -(r1i + r2i + r3i), B = r1i * r2i + r1i * r3i + r2i * r3i, Cc = -(double) r1i * r2i * r3i;
            double pp = B - A * A / 3, qq = 2 * A * A * A / 27 - A * B / 3 + Cc;
            double DD = (qq / 2) * (qq / 2) + (pp / 3) * (pp / 3) * (pp / 3);
            intRoots++;
            if (DD < 0) intNeg++;
        }
        check(intNeg == intRoots, "every cubic with three distinct real roots has D < 0");
        System.out.printf("survey: %,d random cubics x^3 + Ax^2 + Bx + C (A, B, C from -20 to 20): %,d with three real roots (%.1f%%), %,d with one ; D < 0 for every cubic with three distinct real roots and D > 0 for every cubic with one (%,d with D = 0, a repeated root) ; %,d cubics with three distinct whole-number roots: D < 0 in %.0f%%%n",
                n, threeReal, 100.0 * threeReal / n, oneReal, zeroD, intRoots, 100.0 * intNeg / intRoots);

        // ---- 4. the formula on 100,000 cubics with known roots ---------------------------------------------------------
        double worst = 0;
        int solved = 0;
        for (int t = 0; t < n; t++) {
            double r1d = rnd.nextInt(201) - 100, r2d = rnd.nextInt(201) - 100, r3d = rnd.nextInt(201) - 100;
            if (r1d == r2d || r2d == r3d || r1d == r3d) { t--; continue; }
            double A = -(r1d + r2d + r3d), B = r1d * r2d + r1d * r3d + r2d * r3d, Cc = -r1d * r2d * r3d;
            double sh = -A / 3, pp = B - A * A / 3, qq = 2 * A * A * A / 27 - A * B / 3 + Cc;
            C[] y = cardano(pp, qq);
            double[] want = {r1d, r2d, r3d};
            boolean[] used = new boolean[3];
            for (C z : y) {
                double best = Double.MAX_VALUE; int bi = -1;
                for (int k = 0; k < 3; k++) if (!used[k]) { double e = new C(z.re() + sh - want[k], z.im()).abs(); if (e < best) { best = e; bi = k; } }
                used[bi] = true;
                worst = Math.max(worst, best);
            }
            check(worst < 1e-6, "the formula recovers the roots");
            solved++;
        }
        System.out.printf("random: %,d cubics with three distinct whole-number roots from -100 to 100 ; Cardano's formula in complex arithmetic recovers all three roots of every one ; worst error %.1e%n", solved, worst);

        // ---- 5. where the formula breaks: cancellation ------------------------------------------------------------------
        // y^3 + 3,000,000,000 y - 1 = 0 has one small real root near 1/3,000,000,000
        double pc = 3e9, qc = -1;
        double Dc = (qc / 2) * (qc / 2) + (pc / 3) * (pc / 3) * (pc / 3);
        double u = Math.cbrt(-qc / 2 + Math.sqrt(Dc)), v = Math.cbrt(-qc / 2 - Math.sqrt(Dc));
        double naive = u + v;
        // the true root, by Newton from 1/3000 in exact-enough arithmetic (long double is not available: iterate to a fixed point)
        double r = 1.0 / pc;
        for (int k = 0; k < 6; k++) r = r - (r * r * r + pc * r + qc) / (3 * r * r + pc);
        double vv = -pc / (3 * u);                                 // uv = -p/3
        double stable = -qc / (u * u - u * vv + vv * vv);        // u + v = (u^3 + v^3)/(u^2 - uv + v^2): all terms positive, nothing cancels
        double relNaive = Math.abs(naive - r) / r, relStable = Math.abs(stable - r) / r;
        // one Newton step repairs the naive value
        double fixed = naive - (naive * naive * naive + pc * naive + qc) / (3 * naive * naive + pc);
        double relFixed = Math.abs(fixed - r) / r;
        check(relNaive > 1e-3 && relStable < 1e-14 && relFixed < 1e-14, "cancellation spoils the plain formula; rearranging or one Newton step repairs it");
        System.out.printf("cancel: y^3 + 3000000000y - 1 = 0 in 64-bit floating point ; u = %.1f, v = %.1f ; root %.17g ; plain formula u + v = %.17g (relative error %.1e) ; as (u^3 + v^3)/(u^2 - uv + v^2) %.17g (%.1e) ; plain formula then one Newton step %.17g (%.1e)%n",
                u, v, r, naive, relNaive, stable, relStable, fixed, relFixed);

        System.out.printf("CardanoCubic: %d checks passed%n", passed);
    }

    /** Real roots of x^3 + A x^2 + B x + C, counted (with multiplicity merged) from the derivative's turning points. */
    static int realRootCount(int A, int B, int C) {
        // f'(x) = 3x^2 + 2A x + B ; if it has no real zeros, f is monotone: one real root
        double disc = 4.0 * A * A - 12.0 * B;
        if (disc <= 0) return 1;
        double x1 = (-2.0 * A - Math.sqrt(disc)) / 6, x2 = (-2.0 * A + Math.sqrt(disc)) / 6;
        double f1 = ((x1 + A) * x1 + B) * x1 + C, f2 = ((x2 + A) * x2 + B) * x2 + C;
        if (f1 * f2 < 0) return 3;
        return 1;                                               // touching (a double root) counts as the boundary case
    }

    static String fmt(double v) {
        if (v == Math.rint(v) && Math.abs(v) < 1e15) return String.valueOf((long) v);
        return String.format("%.6f", v);
    }
}
