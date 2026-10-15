import java.util.*;

/**
 * Era 7, topic 1: linear programming in polynomial time (Klee and Minty 1972, Khachiyan 1979, Karmarkar 1984).
 *
 * HOW IT WORKS
 *   A linear program asks for the largest value of c.x over the points x that satisfy linear inequalities A x <= b.
 *   Those points form a polytope, and the best value is reached at a corner. The simplex method (Era 4) walks from
 *   corner to better corner along the edges. Usually it needs few steps; but Klee and Minty built a squashed cube in
 *   n dimensions on which the usual rule (enter the variable with the largest coefficient) visits all 2^n corners.
 *   Khachiyan's ellipsoid method encloses the feasible region in an ellipsoid. If the ellipsoid's centre breaks a
 *   constraint, that constraint cuts the ellipsoid in half, and a smaller ellipsoid is drawn around the good half.
 *   The volume shrinks by a fixed factor each time, so a feasible point is found in a polynomial number of steps.
 *   Interior-point methods (Karmarkar 1984) move through the inside of the polytope instead of along its edges. The
 *   kind used here, primal-dual path-following, solves the program and its dual together: at the optimum every
 *   variable times its matching dual slack is zero, so each step is a Newton step towards points where all those
 *   products are equal and a little smaller, stopping just short of the walls. The number of steps hardly grows
 *   with the size of the problem.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The simplex method with Dantzig's rule on Klee and Minty's cube, n = 1 ... 14: pivots counted, 2^n - 1.
 *   2. A primal-dual interior-point method (Mehrotra's predictor-corrector) on the same cubes: iterations
 *      counted, the same optimum.
 *   3. Random linear programs of 10 to 160 variables: simplex pivots and interior-point iterations.
 *   4. The ellipsoid method in two dimensions: steps to find a point in smaller and smaller triangles, against
 *      the volume bound.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LinearProgramming.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LinearProgramming {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1979L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    // ---- the simplex method on a tableau: maximize c.x, A x <= b, x >= 0, b >= 0 ---------------------------------------
    static long pivots;

    static double simplex(double[][] A, double[] b, double[] c) {
        int m = A.length, n = c.length;
        double[][] T = new double[m + 1][n + m + 1];
        for (int i = 0; i < m; i++) {
            System.arraycopy(A[i], 0, T[i], 0, n);
            T[i][n + i] = 1;
            T[i][n + m] = b[i];
        }
        for (int j = 0; j < n; j++) T[m][j] = -c[j];               // objective row: reduced costs, negated
        pivots = 0;
        while (true) {
            int e = -1;
            double most = -1e-12;
            for (int j = 0; j < n + m; j++) if (T[m][j] < most) { most = T[m][j]; e = j; }   // Dantzig: largest coefficient
            if (e < 0) return T[m][n + m];
            int l = -1;
            double best = Double.MAX_VALUE;
            for (int i = 0; i < m; i++) if (T[i][e] > 1e-12) { double r = T[i][n + m] / T[i][e]; if (r < best - 1e-12) { best = r; l = i; } }
            if (l < 0) throw new IllegalStateException("unbounded");
            double p = T[l][e];
            for (int j = 0; j <= n + m; j++) T[l][j] /= p;
            for (int i = 0; i <= m; i++) {
                if (i == l || T[i][e] == 0) continue;
                double f = T[i][e];
                for (int j = 0; j <= n + m; j++) T[i][j] -= f * T[l][j];
            }
            pivots++;
        }
    }

    // ---- a primal-dual interior-point method: maximize c.x, A x + w = b, x >= 0, w >= 0 ---------------------------------
    // Unknowns: v = (x, w), the dual prices y, and the reduced costs z, which must end with z = (-c, 0) - [A I]^T y >= 0.
    // At the optimum every product v_j z_j is zero. Each iteration takes Newton steps towards the point where all the
    // products equal sigma * mu (mu is their current average): Mehrotra's predictor-corrector first tries sigma = 0 to
    // see how far a pure step would get, then picks sigma from that and corrects. Steps stop just short of the walls.
    static int iterations;
    static double[][] Am;     // the constraint matrix of the program being solved
    static int mRows, nCols;

    static double[] interiorPoint(double[][] A, double[] b, double[] c) {
        int m = A.length, n = c.length, N = n + m;
        Am = A; mRows = m; nCols = n;
        double[] cost = new double[N];
        for (int j = 0; j < n; j++) cost[j] = -c[j];
        // Mehrotra's starting point: the least-squares solutions, shifted to be positive
        double[] ones = new double[N];
        Arrays.fill(ones, 1);
        double[][] L = cholesky(normalMatrix(ones));
        double[] v = timesT(cholSolve(L, b.clone()));
        double[] y = cholSolve(L, times(cost));
        double[] z = new double[N];
        double[] aty0 = timesT(y);
        for (int j = 0; j < N; j++) z[j] = cost[j] - aty0[j];
        double minV = Arrays.stream(v).min().getAsDouble(), minZ = Arrays.stream(z).min().getAsDouble();
        double sv = Math.max(-1.5 * minV, 0), sz = Math.max(-1.5 * minZ, 0);
        for (int j = 0; j < N; j++) { v[j] += sv; z[j] += sz; }
        double vz = dot(v, z), sumV = Arrays.stream(v).sum(), sumZ = Arrays.stream(z).sum();
        double sv2 = 0.5 * vz / sumZ, sz2 = 0.5 * vz / sumV;
        for (int j = 0; j < N; j++) { v[j] += sv2; z[j] += sz2; }

        double bScale = 1 + maxAbs(b), cScale = 1 + maxAbs(c);
        iterations = 0;
        while (true) {
            double[] av = times(v), aty = timesT(y);
            double[] rp = new double[m], rd = new double[N];
            for (int i = 0; i < m; i++) rp[i] = b[i] - av[i];
            for (int j = 0; j < N; j++) rd[j] = cost[j] - aty[j] - z[j];
            double mu = dot(v, z) / N;
            double primal = dot(cost, v), dual = dot(b, y);
            if (maxAbs(rp) / bScale < 1e-9 && maxAbs(rd) / cScale < 1e-9 && Math.abs(primal - dual) / (1 + Math.abs(primal)) < 1e-9)
                return Arrays.copyOf(v, n);
            check(iterations < 200, "the interior-point method converges");
            double[] d = new double[N];
            for (int j = 0; j < N; j++) d[j] = v[j] / z[j];
            double[][] F = cholesky(normalMatrix(d));
            // predictor: aim straight at products of zero
            double[] r3 = new double[N];
            for (int j = 0; j < N; j++) r3[j] = -v[j] * z[j];
            double[][] aff = newton(F, d, v, z, rp, rd, r3);
            double apA = stepTo(v, aff[0], 1.0), adA = stepTo(z, aff[1], 1.0);
            double muAff = 0;
            for (int j = 0; j < N; j++) muAff += (v[j] + apA * aff[0][j]) * (z[j] + adA * aff[1][j]);
            muAff /= N;
            double sigma = Math.pow(muAff / mu, 3);
            // corrector: aim at products of sigma * mu, allowing for the predictor's second-order error
            for (int j = 0; j < N; j++) r3[j] = sigma * mu - v[j] * z[j] - aff[0][j] * aff[1][j];
            double[][] st = newton(F, d, v, z, rp, rd, r3);
            double ap = stepTo(v, st[0], 0.99), ad = stepTo(z, st[1], 0.99);
            for (int j = 0; j < N; j++) { v[j] += ap * st[0][j]; z[j] += ad * st[1][j]; }
            for (int i = 0; i < m; i++) y[i] += ad * st[2][i];
            iterations++;
        }
    }

    /** One Newton step for [A I] dv = rp, [A I]^T dy + dz = rd, Z dv + V dz = r3; returns {dv, dz, dy}. */
    static double[][] newton(double[][] F, double[] d, double[] v, double[] z, double[] rp, double[] rd, double[] r3) {
        int N = v.length;
        double[] t = new double[N];
        for (int j = 0; j < N; j++) t[j] = d[j] * (r3[j] / v[j] - rd[j]);
        double[] at = times(t), rhs = new double[mRows];
        for (int i = 0; i < mRows; i++) rhs[i] = rp[i] - at[i];
        double[] dy = cholSolve(F, rhs);
        double[] atdy = timesT(dy), dv = new double[N], dz = new double[N];
        for (int j = 0; j < N; j++) { dv[j] = d[j] * atdy[j] + t[j]; dz[j] = (r3[j] - z[j] * dv[j]) / v[j]; }
        return new double[][]{dv, dz, dy};
    }

    /** The longest step, at most 1, that keeps every coordinate positive, shortened by the factor eta. */
    static double stepTo(double[] x, double[] dx, double eta) {
        double a = 1 / eta;
        for (int j = 0; j < x.length; j++) if (dx[j] < 0) a = Math.min(a, -x[j] / dx[j]);
        return Math.min(1, eta * a);
    }

    /** [A I] D [A I]^T = A Dx A^T + Dw. */
    static double[][] normalMatrix(double[] d) {
        double[][] M = new double[mRows][mRows];
        for (int i = 0; i < mRows; i++) {
            for (int k = i; k < mRows; k++) {
                double sum = 0;
                for (int j = 0; j < nCols; j++) sum += Am[i][j] * d[j] * Am[k][j];
                M[i][k] = sum;
                M[k][i] = sum;
            }
            M[i][i] += d[nCols + i];
        }
        return M;
    }

    /** [A I] x. */
    static double[] times(double[] x) {
        double[] r = new double[mRows];
        for (int i = 0; i < mRows; i++) { double s = x[nCols + i]; for (int j = 0; j < nCols; j++) s += Am[i][j] * x[j]; r[i] = s; }
        return r;
    }

    /** [A I]^T y. */
    static double[] timesT(double[] y) {
        double[] r = new double[nCols + mRows];
        for (int j = 0; j < nCols; j++) r[j] = colDot(Am, j, y);
        for (int i = 0; i < mRows; i++) r[nCols + i] = y[i];
        return r;
    }

    static double[][] cholesky(double[][] M) {
        int n = M.length;
        double[][] L = new double[n][n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j <= i; j++) {
                double s = M[i][j];
                for (int k = 0; k < j; k++) s -= L[i][k] * L[j][k];
                if (i == j) L[i][i] = Math.sqrt(Math.max(s, 1e-300));
                else L[i][j] = s / L[j][j];
            }
        }
        return L;
    }

    static double[] cholSolve(double[][] L, double[] r) {
        int n = r.length;
        double[] y = new double[n];
        for (int i = 0; i < n; i++) { double s = r[i]; for (int k = 0; k < i; k++) s -= L[i][k] * y[k]; y[i] = s / L[i][i]; }
        double[] x = new double[n];
        for (int i = n - 1; i >= 0; i--) { double s = y[i]; for (int k = i + 1; k < n; k++) s -= L[k][i] * x[k]; x[i] = s / L[i][i]; }
        return x;
    }

    static double colDot(double[][] A, int j, double[] y) { double s = 0; for (int i = 0; i < A.length; i++) s += A[i][j] * y[i]; return s; }

    static double maxAbs(double[] a) { double s = 0; for (double x : a) s = Math.max(s, Math.abs(x)); return s; }

    static double dot(double[] a, double[] b) { double s = 0; for (int i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }

    /** Klee and Minty's cube in Chvatal's form: max sum 2^(n-j) x_j, 2 sum_{j<i} 2^(i-j) x_j + x_i <= 5^i. */
    static Object[] kleeMinty(int n) {
        double[][] A = new double[n][n];
        double[] b = new double[n], c = new double[n];
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < i; j++) A[i][j] = 2 * Math.pow(2, i - j);
            A[i][i] = 1;
            b[i] = Math.pow(5, i + 1);
            c[i] = Math.pow(2, n - 1 - i);
        }
        return new Object[]{A, b, c};
    }

    public static void main(String[] args) {
        // ---- 1 and 2. Klee and Minty's cube ----------------------------------------------------------------------------
        StringJoiner kj = new StringJoiner(" ; ");
        int maxIpm = 0;
        for (int n = 1; n <= 14; n++) {
            Object[] km = kleeMinty(n);
            double[][] A = (double[][]) km[0];
            double[] b = (double[]) km[1], c = (double[]) km[2];
            double opt = simplex(A, b, c);
            long piv = pivots;
            check(piv == (1L << n) - 1, "Klee-Minty n=" + n + " takes 2^n - 1 pivots");
            check(opt == Math.pow(5, n), "optimum 5^n");
            double[] x = interiorPoint(A, b, c);
            double v = dot(c, x);
            check(Math.abs(v - opt) / opt < 1e-6, "interior point reaches the optimum, n=" + n);
            maxIpm = Math.max(maxIpm, iterations);
            if (n == 1 || n == 2 || n == 3 || n % 2 == 0)
                kj.add(String.format("n=%d: simplex %,d pivot%s, interior point %d iterations", n, piv, piv == 1 ? "" : "s", iterations));
        }
        System.out.printf("kleeminty: maximize sum of 2^(n-j) x_j subject to 2 sum_{j<i} 2^(i-j) x_j + x_i <= 5^i ; the simplex method with Dantzig's rule (enter the largest coefficient) against a primal-dual interior-point method (Mehrotra's predictor-corrector), both reaching the optimum 5^n ; %s ; the simplex pivots are exactly 2^n - 1 every time, the interior-point iterations never more than %d%n",
                kj, maxIpm);

        // ---- 3. random programs -----------------------------------------------------------------------------------------
        StringJoiner rj = new StringJoiner(" ; ");
        for (int n = 10; n <= 160; n *= 2) {
            long sumPiv = 0, sumIt = 0;
            int trials = 5;
            for (int t = 0; t < trials; t++) {
                int m = n;
                double[][] A = new double[m][n];
                double[] b = new double[m], c = new double[n];
                for (int i = 0; i < m; i++) { for (int j = 0; j < n; j++) A[i][j] = uniform(); b[i] = 1 + uniform() * n / 4.0; }
                for (int j = 0; j < n; j++) c[j] = uniform();
                double opt = simplex(A, b, c);
                sumPiv += pivots;
                double[] x = interiorPoint(A, b, c);
                check(Math.abs(dot(c, x) - opt) / opt < 1e-6, "random LP: both methods agree");
                sumIt += iterations;
            }
            rj.add(String.format("%d variables and %d constraints: simplex %.1f pivots, interior point %.1f iterations", n, n, (double) sumPiv / trials, (double) sumIt / trials));
        }
        System.out.printf("random: random programs (positive coefficients), 5 of each size, both methods reaching the same optimum ; %s%n", rj);

        // ---- 4. the ellipsoid method in the plane ----------------------------------------------------------------------
        // Find a point inside a small triangle, starting from a circle of radius 100 centred at the origin.
        StringJoiner ej = new StringJoiner(" ; ");
        double ratio = (2.0 / 3.0) * Math.sqrt(4.0 / 3.0);              // area shrink per step in two dimensions
        int prevSteps = 0;
        for (int k = 0; k <= 6; k++) {
            double side = 10 * Math.pow(0.1, k / 2.0);                // triangle sides from 10 down to 10^-2
            double cx = 37.0, cy = -21.0;                              // a corner of the triangle, away from the start
            double[][] cons = {{0, -1, -cy}, {-1, 0, -cx}, {1, 1, cx + cy + side}};   // y >= cy, x >= cx, x + y <= cx + cy + side
            double[] z = {0, 0};
            double[][] P = {{100 * 100, 0}, {0, 100 * 100}};
            double area0 = Math.PI * 100 * 100, area = area0;
            int steps = 0;
            while (true) {
                double[] viol = null;
                for (double[] con : cons) if (con[0] * z[0] + con[1] * z[1] > con[2]) { viol = con; break; }
                if (viol == null) break;
                double[] a = {viol[0], viol[1]};
                double[] Pa = {P[0][0] * a[0] + P[0][1] * a[1], P[1][0] * a[0] + P[1][1] * a[1]};
                double aPa = a[0] * Pa[0] + a[1] * Pa[1];
                double[] g = {Pa[0] / Math.sqrt(aPa), Pa[1] / Math.sqrt(aPa)};
                z[0] -= g[0] / 3; z[1] -= g[1] / 3;                    // n = 2: move 1/(n+1) along -P g
                for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) P[i][j] = (4.0 / 3.0) * (P[i][j] - (2.0 / 3.0) * g[i] * g[j]);
                double newArea = Math.PI * Math.sqrt(P[0][0] * P[1][1] - P[0][1] * P[1][0]);
                check(Math.abs(newArea / area - ratio) < 1e-9, "each cut shrinks the area by the same factor");
                area = newArea;
                steps++;
                check(steps < 10_000, "terminates");
            }
            double tri = side * side / 2;
            double bound = Math.ceil(Math.log(area0 / tri) / Math.log(1 / ratio));
            check(steps <= bound, "never more steps than the area bound");
            check(steps >= prevSteps, "smaller targets take at least as many steps");
            prevSteps = steps;
            ej.add(String.format("side %s: %d steps (bound %.0f)", fmt(side), steps, bound));
        }
        System.out.printf("ellipsoid: find a point inside a right triangle near (37, -21), starting from the disc of radius 100 about the origin ; each cut shrinks the ellipse's area by the factor %.4f ; %s ; the bound is the number of shrinkings that would take the starting area below the triangle's%n",
                ratio, ej);

        System.out.println("LinearProgramming: " + passed + " checks passed");
    }

    static String fmt(double x) {
        if (x >= 1) return String.format("%.2f", x).replaceAll("\\.?0+$", "");
        return String.format("%.4f", x).replaceAll("0+$", "");
    }
}
