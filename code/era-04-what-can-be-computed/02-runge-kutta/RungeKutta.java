import java.util.*;

/**
 * Era 4, topic 2: Runge–Kutta methods (Runge 1895, Heun 1900, Kutta 1901).
 *
 * HOW IT WORKS
 *   A differential equation y' = f(t, y) says how fast y changes at every moment. Euler's method (1768) walks forward
 *   in steps of size h, each step following the slope at its start: y(t + h) ~ y(t) + h f(t, y). Its error is
 *   proportional to h, so ten times the accuracy costs ten times the steps. Runge's idea (1895) was to sample the
 *   slope more than once inside each step and combine the samples, as the midpoint and trapezoidal rules do for
 *   areas. The classical method of Kutta (1901) samples four slopes:
 *       k1 = f(t, y)                  k2 = f(t + h/2, y + h k1/2)
 *       k3 = f(t + h/2, y + h k2/2)   k4 = f(t + h, y + h k3)
 *       y(t + h) ~ y + h (k1 + 2 k2 + 2 k3 + k4) / 6
 *   The weights are chosen so that the step agrees with the Taylor series of the true solution up to h^4. That means
 *   eight equations in the weights ("order conditions"); then halving h divides the error by about 2^4 = 16.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Writes five methods as tables of weights (Euler; Runge's midpoint; Heun's third order; Kutta's classical
 *      method and his 3/8 rule) and tests the eight order conditions in exact fractions.
 *   2. Measures each method's order on y' = y, whose answer at t = 1 is e: the error ratio when h is halved.
 *   3. Runs each on the oscillator x'' = -x for 20 periods: Euler's circle spirals out by exactly (1 + h^2) per step.
 *   4. Counts the slope evaluations each method needs for an error below 10^-6.
 *   5. A pendulum swinging through 90 degrees, which no elementary formula describes: the period found by the
 *      classical method agrees with Gauss's arithmetic-geometric mean to 12 digits.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java RungeKutta.java
 *   Expected output: expected-output.txt in this folder.
 */
public class RungeKutta {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** An exact fraction, for the order conditions. */
    record F(long n, long d) {
        static F of(long n, long d) {
            if (d < 0) { n = -n; d = -d; }
            long g = gcd(Math.abs(n), d);
            return new F(n / g, d / g);
        }
        static long gcd(long a, long b) { return b == 0 ? Math.max(a, 1) : gcd(b, a % b); }
        F plus(F o) { return of(n * o.d + o.n * d, d * o.d); }
        F times(F o) { return of(n * o.n, d * o.d); }
        double v() { return (double) n / d; }
        public String toString() { return d == 1 ? String.valueOf(n) : n + "/" + d; }
    }

    static F f(long n, long d) { return F.of(n, d); }
    static final F Z = f(0, 1);

    /** A Runge–Kutta method: slopes are sampled at t + c[i] h, from y + h * sum_j a[i][j] k[j]; the step uses weights b. */
    record Method(String name, String who, F[][] a, F[] b, F[] c) {
        int stages() { return b.length; }
    }

    static Method[] methods() {
        return new Method[]{
                new Method("Euler", "Euler, 1768", new F[][]{{}}, new F[]{f(1, 1)}, new F[]{Z}),
                new Method("Midpoint", "Runge, 1895", new F[][]{{}, {f(1, 2)}}, new F[]{Z, f(1, 1)}, new F[]{Z, f(1, 2)}),
                new Method("Heun3", "third order, of the kind Heun gave in 1900", new F[][]{{}, {f(1, 3)}, {Z, f(2, 3)}}, new F[]{f(1, 4), Z, f(3, 4)}, new F[]{Z, f(1, 3), f(2, 3)}),
                new Method("Classical", "Kutta, 1901", new F[][]{{}, {f(1, 2)}, {Z, f(1, 2)}, {Z, Z, f(1, 1)}},
                        new F[]{f(1, 6), f(1, 3), f(1, 3), f(1, 6)}, new F[]{Z, f(1, 2), f(1, 2), f(1, 1)}),
                new Method("ThreeEighths", "Kutta, 1901", new F[][]{{}, {f(1, 3)}, {f(-1, 3), f(1, 1)}, {f(1, 1), f(-1, 1), f(1, 1)}},
                        new F[]{f(1, 8), f(3, 8), f(3, 8), f(1, 8)}, new F[]{Z, f(1, 3), f(2, 3), f(1, 1)}),
        };
    }

    // ---- 1. the eight order conditions, in exact fractions -----------------------------------------------------------
    static F sumB(Method m, java.util.function.IntFunction<F> g) {
        F s = Z;
        for (int i = 0; i < m.stages(); i++) s = s.plus(m.b[i].times(g.apply(i)));
        return s;
    }

    static F ac(Method m, int i, java.util.function.IntFunction<F> g) {    // sum_j a[i][j] g(j)
        F s = Z;
        for (int j = 0; j < m.a[i].length; j++) s = s.plus(m.a[i][j].times(g.apply(j)));
        return s;
    }

    /** The conditions for orders 1, 2, 3, 3, 4, 4, 4, 4, as {order, left side, right side}. */
    static Object[][] conditions(Method m) {
        F[] c = m.c;
        return new Object[][]{
                {1, sumB(m, i -> f(1, 1)), f(1, 1)},
                {2, sumB(m, i -> c[i]), f(1, 2)},
                {3, sumB(m, i -> c[i].times(c[i])), f(1, 3)},
                {3, sumB(m, i -> ac(m, i, j -> c[j])), f(1, 6)},
                {4, sumB(m, i -> c[i].times(c[i]).times(c[i])), f(1, 4)},
                {4, sumB(m, i -> c[i].times(ac(m, i, j -> c[j]))), f(1, 8)},
                {4, sumB(m, i -> ac(m, i, j -> c[j].times(c[j]))), f(1, 12)},
                {4, sumB(m, i -> ac(m, i, j -> ac(m, j, k -> c[k]))), f(1, 24)},
        };
    }

    // ---- integration ----------------------------------------------------------------------------------------------------
    interface Sys { double[] f(double t, double[] y); }

    static long evals;

    static double[] step(Method m, Sys sys, double t, double[] y, double h) {
        int s = m.stages(), n = y.length;
        double[][] k = new double[s][];
        for (int i = 0; i < s; i++) {
            double[] yi = y.clone();
            for (int j = 0; j < m.a[i].length; j++)
                for (int q = 0; q < n; q++) yi[q] += h * m.a[i][j].v() * k[j][q];
            k[i] = sys.f(t + m.c[i].v() * h, yi);
            evals++;
        }
        double[] out = y.clone();
        for (int i = 0; i < s; i++)
            for (int q = 0; q < n; q++) out[q] += h * m.b[i].v() * k[i][q];
        return out;
    }

    static double[] solve(Method m, Sys sys, double[] y0, double T, long n) {
        double h = T / n, t = 0;
        double[] y = y0.clone();
        for (long i = 0; i < n; i++) { y = step(m, sys, t, y, h); t = (i + 1) * h; }
        return y;
    }

    static double agm(double a, double b) {
        for (int i = 0; i < 60; i++) { double a2 = (a + b) / 2, b2 = Math.sqrt(a * b); a = a2; b = b2; }
        return a;
    }

    public static void main(String[] args) {
        Method[] ms = methods();
        int[] expectOrder = {1, 2, 3, 4, 4};

        // ---- 1. order conditions ------------------------------------------------------------------------------------
        for (int k = 0; k < ms.length; k++) {
            Method m = ms[k];
            Object[][] cond = conditions(m);
            int met = 0, order = 0;
            boolean stillOk = true;
            StringJoiner fails = new StringJoiner(" ; ");
            for (int o = 1; o <= 4; o++) {
                boolean all = true;
                for (Object[] cd : cond)
                    if ((int) cd[0] == o) {
                        boolean ok = cd[1].equals(cd[2]);
                        if (ok) met++;
                        else { all = false; if (fails.length() < 60) fails.add(cd[1] + " instead of " + cd[2]); }
                    }
                if (all && stillOk) order = o; else stillOk = false;
            }
            check(order == expectOrder[k], m.name + " has order " + expectOrder[k]);
            StringJoiner bs = new StringJoiner(", ");
            for (F b : m.b) bs.add(b.toString());
            System.out.printf("tableau: %s (%s) ; %d slope%s ; weights %s ; order conditions met %d of 8 ; order %d%s%n",
                    m.name, m.who, m.stages(), m.stages() == 1 ? "" : "s", bs, met, order,
                    order < 4 ? " ; first failure " + fails.toString().split(" ; ")[0] : "");
        }

        // ---- 2. measured order on y' = y -----------------------------------------------------------------------------
        Sys grow = (t, y) -> new double[]{y[0]};
        long[] ns = {10, 20, 40, 80, 160};
        for (int k = 0; k < ms.length; k++) {
            Method m = ms[k];
            double[] err = new double[ns.length];
            for (int i = 0; i < ns.length; i++) err[i] = Math.abs(solve(m, grow, new double[]{1}, 1, ns[i])[0] - Math.E);
            StringJoiner es = new StringJoiner(", "), rs = new StringJoiner(", ");
            for (double e : err) es.add(String.format("%.2e", e));
            for (int i = 0; i + 1 < ns.length; i++) {
                double r = err[i] / err[i + 1];
                rs.add(String.format("%.2f", r));
                check(Math.abs(Math.log(r) / Math.log(2) - expectOrder[k]) < 0.1, m.name + " error ratio near 2^" + expectOrder[k]);
            }
            double p = Math.log(err[ns.length - 2] / err[ns.length - 1]) / Math.log(2);
            System.out.printf("order: %s ; y' = y from y(0) = 1 to t = 1 ; steps 10, 20, 40, 80, 160 ; errors %s ; ratios %s ; measured order %.3f%n",
                    m.name, es, rs, p);
        }

        // ---- 3. the oscillator x'' = -x for 20 periods ---------------------------------------------------------------
        Sys osc = (t, y) -> new double[]{y[1], -y[0]};
        int perPeriod = 32, periods = 20;
        double T = 2 * Math.PI * periods;
        long n = (long) perPeriod * periods;
        double h = T / n;
        StringJoiner oscOut = new StringJoiner(" ; ");
        for (Method m : ms) {
            double[] y = solve(m, osc, new double[]{1, 0}, T, n);
            double r2 = y[0] * y[0] + y[1] * y[1];
            if (m.name.equals("Euler")) {
                double predicted = Math.pow(1 + h * h, n);
                check(Math.abs(r2 / predicted - 1) < 1e-12, "Euler's circle grows by exactly 1 + h^2 per step");
                oscOut.add(String.format("Euler x^2 + v^2 = %.4f, predicted (1 + h^2)^%d = %.4f", r2, n, predicted));
            } else {
                oscOut.add(String.format("%s %.8f", m.name, r2));
            }
        }
        double[] rk = solve(ms[3], osc, new double[]{1, 0}, T, n);
        check(Math.abs(rk[0] - 1) < 1e-3 && Math.abs(rk[1]) < 1e-2, "the classical method returns near the start");
        System.out.printf("oscillator: x'' = -x, start (1, 0), %d steps per period, %d periods ; x^2 + v^2 should stay 1 ; %s%n", perPeriod, periods, oscOut);

        // ---- 4. cost of an error below 10^-6 on y' = y ---------------------------------------------------------------
        StringJoiner costs = new StringJoiner(" ; ");
        long[] cost = new long[ms.length];
        for (int k = 0; k < ms.length; k++) {
            Method m = ms[k];
            long lo = 1, hi = 1;
            while (Math.abs(solve(m, grow, new double[]{1}, 1, hi)[0] - Math.E) > 1e-6) { lo = hi; hi *= 2; }
            while (lo < hi) {                                         // the smallest n with error <= 1e-6
                long mid = (lo + hi) / 2;
                if (Math.abs(solve(m, grow, new double[]{1}, 1, mid)[0] - Math.E) <= 1e-6) hi = mid; else lo = mid + 1;
            }
            cost[k] = hi * m.stages();
            check(Math.abs(solve(m, grow, new double[]{1}, 1, hi)[0] - Math.E) <= 1e-6, "minimal steps reach 1e-6");
            check(hi == 1 || Math.abs(solve(m, grow, new double[]{1}, 1, hi - 1)[0] - Math.E) > 1e-6, "one step fewer misses 1e-6");
            costs.add(String.format("%s %d steps, %d slope evaluations", m.name, hi, cost[k]));
        }
        for (int k = 1; k < ms.length; k++) check(cost[k] < cost[k - 1] || k == 4, "higher order is cheaper");
        System.out.printf("cost: y' = y to t = 1 with error below 10^-6 ; %s%n", costs);

        // ---- 5. a pendulum through 90 degrees --------------------------------------------------------------------------
        Sys pend = (t, y) -> new double[]{y[1], -Math.sin(y[0])};
        double theta0 = Math.PI / 2;
        double hp = 1.0 / 1024;
        double[] y = {theta0, 0};
        double t = 0;
        evals = 0;
        // swing until the angular velocity turns positive again (half a period), then refine the crossing
        double[] prev;
        while (true) {
            prev = y;
            y = step(ms[3], pend, t, y, hp);
            t += hp;
            if (t > 1 && prev[1] < 0 && y[1] >= 0) break;
        }
        // the moment v = 0 between t - hp and t, by bisection on a shortened last step
        double lo = 0, hi = hp;
        for (int i = 0; i < 60; i++) {
            double mid = (lo + hi) / 2;
            if (step(ms[3], pend, t - hp, prev, mid)[1] < 0) lo = mid; else hi = mid;
        }
        double period = 2 * (t - hp + lo);
        double exact = 2 * Math.PI / agm(1, Math.cos(theta0 / 2));
        check(Math.abs(period - exact) < 1e-11, "pendulum period agrees with the AGM formula");
        System.out.printf("pendulum: theta'' = -sin theta from 90 degrees ; classical method, h = 1/1024, %d slope evaluations: period %.12f ; Gauss's AGM formula 2 pi / M(1, cos 45 deg) = %.12f ; difference %.1e ; small-swing value 2 pi = %.12f%n",
                evals, period, exact, Math.abs(period - exact), 2 * Math.PI);

        System.out.println("RungeKutta: " + passed + " checks passed");
    }
}
