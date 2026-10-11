import java.util.*;

/**
 * Era 3, topic 8: least squares (Legendre 1805; Gauss 1809, who said he had used it since 1795; Ceres 1801).
 *
 * HOW IT WORKS
 *   Measurements disagree, and there are more of them than unknowns, so the equations cannot all hold. Legendre's rule:
 *   choose the unknowns that make the sum of the squares of the errors as small as possible. For a model
 *   y = c1 f1(x) + ... + cn fn(x) fitted to m observations, setting the derivative of the sum of squares to zero for each
 *   unknown gives n linear "normal equations", (F^T F) c = F^T y, however many observations there are. They are solved by
 *   elimination (Era 2, topic 1). Squares are chosen because they make the arithmetic linear and, as Legendre put it,
 *   set up a kind of balance among the errors, so that no single extreme error dominates.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Fits a straight line and a quadratic to noisy observations by the normal equations and Gaussian elimination,
 *      and checks that no nearby choice of coefficients has a smaller sum of squares.
 *   2. Compares three rules on 10,000 noisy data sets: least squares, least absolute errors, and least largest error.
 *   3. Shows a single wild observation pulling each rule.
 *   4. Counts the work: the normal equations stay n by n however many observations.
 *   5. Shows the weakness of the normal equations for ill-conditioned fits, against an orthogonal (QR) solution.
 *   6. Full circle: gradient descent on the sum of squares, as a machine-learning library trains a linear model,
 *      reaches the same coefficients.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LeastSquares.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LeastSquares {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long flops;

    /** Gaussian elimination with partial pivoting: solve A c = b (A is n x n). */
    static double[] solve(double[][] A0, double[] b0) {
        int n = b0.length;
        double[][] A = new double[n][];
        for (int i = 0; i < n; i++) A[i] = A0[i].clone();
        double[] b = b0.clone();
        for (int k = 0; k < n; k++) {
            int p = k;
            for (int i = k + 1; i < n; i++) if (Math.abs(A[i][k]) > Math.abs(A[p][k])) p = i;
            double[] t = A[k]; A[k] = A[p]; A[p] = t; double tb = b[k]; b[k] = b[p]; b[p] = tb;
            for (int i = k + 1; i < n; i++) {
                double f = A[i][k] / A[k][k];
                for (int j = k; j < n; j++) { A[i][j] -= f * A[k][j]; flops++; }
                b[i] -= f * b[k];
            }
        }
        double[] c = new double[n];
        for (int i = n - 1; i >= 0; i--) { double s = b[i]; for (int j = i + 1; j < n; j++) s -= A[i][j] * c[j]; c[i] = s / A[i][i]; }
        return c;
    }

    /** Least squares by the normal equations: (F^T F) c = F^T y, with F[i][j] = x_i^j. */
    static double[] normalEquations(double[] x, double[] y, int n) {
        double[][] M = new double[n][n];
        double[] r = new double[n];
        for (int i = 0; i < x.length; i++) {
            double[] f = new double[n];
            for (int j = 0; j < n; j++) f[j] = Math.pow(x[i], j);
            for (int a = 0; a < n; a++) { r[a] += f[a] * y[i]; for (int b = 0; b < n; b++) { M[a][b] += f[a] * f[b]; flops++; } }
        }
        return solve(M, r);
    }

    /** Least squares by Householder reflections (QR), never forming F^T F. */
    static double[] qr(double[] x, double[] y, int n) {
        int m = x.length;
        double[][] F = new double[m][n];
        double[] b = y.clone();
        for (int i = 0; i < m; i++) for (int j = 0; j < n; j++) F[i][j] = Math.pow(x[i], j);
        for (int k = 0; k < n; k++) {
            double norm = 0;
            for (int i = k; i < m; i++) norm += F[i][k] * F[i][k];
            norm = Math.sqrt(norm);
            double alpha = F[k][k] > 0 ? -norm : norm;
            double[] v = new double[m];
            for (int i = k; i < m; i++) v[i] = F[i][k];
            v[k] -= alpha;
            double vv = 0; for (int i = k; i < m; i++) vv += v[i] * v[i];
            if (vv == 0) continue;
            for (int j = k; j < n; j++) { double s = 0; for (int i = k; i < m; i++) s += v[i] * F[i][j]; s = 2 * s / vv; for (int i = k; i < m; i++) F[i][j] -= s * v[i]; }
            double s = 0; for (int i = k; i < m; i++) s += v[i] * b[i]; s = 2 * s / vv; for (int i = k; i < m; i++) b[i] -= s * v[i];
        }
        double[] c = new double[n];
        for (int i = n - 1; i >= 0; i--) { double s = b[i]; for (int j = i + 1; j < n; j++) s -= F[i][j] * c[j]; c[i] = s / F[i][i]; }
        return c;
    }

    static double sse(double[] x, double[] y, double[] c) {
        double s = 0;
        for (int i = 0; i < x.length; i++) { double p = 0; for (int j = c.length - 1; j >= 0; j--) p = p * x[i] + c[j]; s += (y[i] - p) * (y[i] - p); }
        return s;
    }

    /** The line minimising the sum of absolute errors passes through two data points: try every pair. */
    static double[] lad(double[] x, double[] y) {
        double best = Double.MAX_VALUE; double[] bc = null;
        for (int i = 0; i < x.length; i++) for (int j = i + 1; j < x.length; j++) {
            if (x[i] == x[j]) continue;
            double b = (y[j] - y[i]) / (x[j] - x[i]), a = y[i] - b * x[i], s = 0;
            for (int k = 0; k < x.length; k++) s += Math.abs(y[k] - a - b * x[k]);
            if (s < best) { best = s; bc = new double[]{a, b}; }
        }
        return bc;
    }

    /** The line minimising the largest error (Chebyshev): search over the slope, the intercept follows from the extremes. */
    static double[] minimax(double[] x, double[] y) {
        double lo = -50, hi = 50;
        for (int it = 0; it < 200; it++) {                       // the largest error is convex in the slope: ternary search
            double m1 = lo + (hi - lo) / 3, m2 = hi - (hi - lo) / 3;
            if (maxErr(x, y, m1) < maxErr(x, y, m2)) hi = m2; else lo = m1;
        }
        double b = (lo + hi) / 2, mn = Double.MAX_VALUE, mx = -Double.MAX_VALUE;
        for (int k = 0; k < x.length; k++) { double r = y[k] - b * x[k]; mn = Math.min(mn, r); mx = Math.max(mx, r); }
        return new double[]{(mn + mx) / 2, b};
    }

    static double maxErr(double[] x, double[] y, double b) {
        double mn = Double.MAX_VALUE, mx = -Double.MAX_VALUE;
        for (int k = 0; k < x.length; k++) { double r = y[k] - b * x[k]; mn = Math.min(mn, r); mx = Math.max(mx, r); }
        return (mx - mn) / 2;
    }

    public static void main(String[] args) {
        Random rnd = new Random(1805);
        // ---- 1. fitting by the normal equations ---------------------------------------------------------------------
        int m = 22;                                               // as many observations as Piazzi made of Ceres
        double[] x = new double[m], y = new double[m];
        for (int i = 0; i < m; i++) { x[i] = i * 41.0 / (m - 1) / 10; y[i] = 2.0 + 0.7 * x[i] + 0.15 * x[i] * x[i] + 0.05 * rnd.nextGaussian(); }
        double[] line = normalEquations(x, y, 2), quad = normalEquations(x, y, 3);
        // no nearby coefficients do better
        for (double[] c : new double[][]{line, quad}) {
            double best = sse(x, y, c);
            for (int t = 0; t < 2000; t++) {
                double[] c2 = c.clone();
                c2[rnd.nextInt(c.length)] += 1e-3 * rnd.nextGaussian();
                check(sse(x, y, c2) >= best, "the least-squares coefficients minimise the sum of squares");
            }
        }
        System.out.printf("fit: %d observations of y = 2 + 0.7x + 0.15x^2 plus noise (sd 0.05) ; straight line y = %.4f + %.4fx, sum of squares %.4f ; quadratic y = %.4f + %.4fx + %.4fx^2, sum of squares %.5f ; the normal equations are %d by %d and %d by %d, whatever the number of observations%n",
                m, line[0], line[1], sse(x, y, line), quad[0], quad[1], quad[2], sse(x, y, quad), 2, 2, 3, 3);

        // ---- 2. three rules on noisy data ----------------------------------------------------------------------------
        int trials = 10000;
        double[] mse = new double[3];
        int lsBest = 0;
        for (int t = 0; t < trials; t++) {
            int n = 15;
            double[] xx = new double[n], yy = new double[n];
            for (int i = 0; i < n; i++) { xx[i] = i; yy[i] = 1 + 0.5 * i + rnd.nextGaussian(); }
            double[] a = normalEquations(xx, yy, 2), b = lad(xx, yy), c = minimax(xx, yy);
            double ea = (a[1] - 0.5) * (a[1] - 0.5), eb = (b[1] - 0.5) * (b[1] - 0.5), ec = (c[1] - 0.5) * (c[1] - 0.5);
            mse[0] += ea; mse[1] += eb; mse[2] += ec;
        }
        for (int k = 0; k < 3; k++) mse[k] /= trials;
        check(mse[0] < mse[1] && mse[0] < mse[2], "with bell-shaped (normal) errors, least squares estimates the slope best");
        System.out.printf("rules: %,d data sets of 15 points on y = 1 + 0.5x with normal errors (sd 1) ; mean squared error of the fitted slope: least squares %.5f, least absolute errors %.5f, least largest error %.5f%n",
                trials, mse[0], mse[1], mse[2]);

        // ---- 3. one wild observation ---------------------------------------------------------------------------------
        int n = 15;
        double[] xx = new double[n], yy = new double[n];
        for (int i = 0; i < n; i++) { xx[i] = i; yy[i] = 1 + 0.5 * i + 0.3 * rnd.nextGaussian(); }
        double[] cleanLs = normalEquations(xx, yy, 2), cleanLad = lad(xx, yy), cleanMm = minimax(xx, yy);
        yy[n - 1] += 20;                                          // one observation copied wrongly
        double[] wildLs = normalEquations(xx, yy, 2), wildLad = lad(xx, yy), wildMm = minimax(xx, yy);
        check(Math.abs(wildLad[1] - cleanLad[1]) < Math.abs(wildLs[1] - cleanLs[1]) && Math.abs(wildLs[1] - cleanLs[1]) < Math.abs(wildMm[1] - cleanMm[1]),
                "one wild point moves the least-largest-error line most, least squares next, least absolute errors least");
        System.out.printf("wild: 15 points on y = 1 + 0.5x, then one observation off by 20 ; slope before and after: least squares %.3f -> %.3f ; least absolute errors %.3f -> %.3f ; least largest error %.3f -> %.3f%n",
                cleanLs[1], wildLs[1], cleanLad[1], wildLad[1], cleanMm[1], wildMm[1]);

        // ---- 4. the work -----------------------------------------------------------------------------------------------
        StringJoiner work = new StringJoiner(" ; ");
        for (int obs : new int[]{22, 1000, 100000}) {
            double[] ox = new double[obs], oy = new double[obs];
            for (int i = 0; i < obs; i++) { ox[i] = rnd.nextDouble(); oy[i] = 1 + 2 * ox[i] - ox[i] * ox[i] + 0.01 * rnd.nextGaussian(); }
            flops = 0;
            double[] c = normalEquations(ox, oy, 3);
            check(Math.abs(c[1] - 2) < 0.1, "the fit recovers the coefficients");
            work.add(String.format("%,d observations: %,d multiply-adds to form the 3 by 3 normal equations and solve them", obs, flops));
        }
        System.out.printf("work: %s%n", work);

        // ---- 5. the normal equations' weakness -----------------------------------------------------------------------
        StringJoiner cond = new StringJoiner(" ; ");
        for (int deg : new int[]{3, 6, 9, 12}) {
            int obs = 60, k = deg + 1;
            double[] ox = new double[obs], oy = new double[obs];
            for (int i = 0; i < obs; i++) { ox[i] = i / (double) (obs - 1); double v = 0; for (int j = k - 1; j >= 0; j--) v = v * ox[i] + 1; oy[i] = v; }   // exact data: all coefficients 1
            double[] ne = normalEquations(ox, oy, k), q = qr(ox, oy, k);
            double eNe = 0, eQ = 0;
            for (int j = 0; j < k; j++) { eNe = Math.max(eNe, Math.abs(ne[j] - 1)); eQ = Math.max(eQ, Math.abs(q[j] - 1)); }
            if (deg == 12) check(eNe > 1000 * eQ, "at degree 12 the normal equations lose far more digits than QR");
            cond.add(String.format("degree %d: normal equations error %.1e, QR %.1e", deg, eNe, eQ));
        }
        System.out.printf("digits: fitting exact data (every coefficient 1) by polynomials in 64-bit floating point, largest coefficient error ; %s%n", cond);

        // ---- 6. full circle: gradient descent ----------------------------------------------------------------------------
        double a = 0, b = 0, lr = 0.05;
        int steps = 0;
        double[] target = normalEquations(xx, yy, 2);
        while (steps < 200000) {
            double ga = 0, gb = 0;
            for (int i = 0; i < n; i++) { double r = a + b * xx[i] - yy[i]; ga += r; gb += r * xx[i]; }
            a -= lr * ga / n / 10; b -= lr * gb / n / 100;
            steps++;
            if (Math.abs(a - target[0]) < 1e-9 && Math.abs(b - target[1]) < 1e-9) break;
        }
        check(Math.abs(a - target[0]) < 1e-9 && Math.abs(b - target[1]) < 1e-9, "gradient descent reaches the least-squares line");
        System.out.printf("circle: gradient descent on the sum of squares for the 15 points with the wild one, from (0, 0): after %,d small steps y = %.6f + %.6fx, the normal equations' y = %.6f + %.6fx in one elimination%n",
                steps, a, b, target[0], target[1]);

        System.out.printf("LeastSquares: %d checks passed%n", passed);
    }
}
