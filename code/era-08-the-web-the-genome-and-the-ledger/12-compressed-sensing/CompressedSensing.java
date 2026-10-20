import java.util.*;

/**
 * Era 8, topic 12: Compressed sensing (Candès, Romberg and Tao, 2004 preprint, 2006 journal; Donoho, 2006).
 *
 * HOW IT WORKS
 *   A signal x has N numbers, but only k of them are not zero, and we do not know which. Take m measurements, each a
 *   fixed random combination of all N numbers: y = A x, with A an m-by-N matrix of random numbers. With m < N the
 *   equations A x = y have infinitely many solutions. The usual choice, the solution with the smallest sum of
 *   squares, spreads the signal thinly over every position and is almost never right. Candès, Romberg and Tao
 *   proved that the solution with the smallest sum of absolute values (the l1 norm) is, with high probability,
 *   exactly x, as soon as m is a modest multiple of k log(N / k). Why l1: the set of points with a given l1 norm is
 *   a diamond with corners on the axes, and a random flat set of solutions touches the smallest diamond at a corner,
 *   where most numbers are zero.
 *   Minimizing |x_1| + ... + |x_N| subject to A x = y is a linear program (Era 7): write x = u - v with u, v >= 0 and
 *   minimize the sum of u and v. This program solves it with a primal-dual interior-point method (Mehrotra's
 *   predictor-corrector, as in Era 7's program).
 *
 * WHAT THIS PROGRAM DOES
 *   1. One signal: N = 128, k = 5, m = 40 random measurements: the l1 solution against the smallest-squares one.
 *   2. The phase transition: for m from 16 to 64 and k from 2 to 16, how often l1 minimization recovers the signal
 *      exactly (10 random signals and matrices each), and how often the smallest-squares solution does.
 *   3. A small signal (N = 32, k = 3) recovered from 4 to 20 measurements, for the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CompressedSensing.java
 *   Expected output: expected-output.txt in this folder.
 */
public class CompressedSensing {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static Random rnd = new Random(2004);

    static double[] sparseSignal(int N, int k) {
        double[] x = new double[N];
        List<Integer> idx = new ArrayList<>();
        for (int i = 0; i < N; i++) idx.add(i);
        Collections.shuffle(idx, rnd);
        for (int i = 0; i < k; i++) x[idx.get(i)] = (rnd.nextBoolean() ? 1 : -1) * (1 + rnd.nextDouble());
        return x;
    }

    static double[][] gaussianMatrix(int m, int N) {
        double[][] A = new double[m][N];
        for (double[] row : A) for (int j = 0; j < N; j++) row[j] = rnd.nextGaussian() / Math.sqrt(m);
        return A;
    }

    static double[] mul(double[][] A, double[] x) {
        double[] y = new double[A.length];
        for (int i = 0; i < A.length; i++) for (int j = 0; j < x.length; j++) y[i] += A[i][j] * x[j];
        return y;
    }

    static double[][] cholesky(double[][] M) {
        int n = M.length;
        double[][] L = new double[n][n];
        for (int j = 0; j < n; j++) {
            double s = M[j][j];
            for (int p = 0; p < j; p++) s -= L[j][p] * L[j][p];
            if (s <= 1e-30 * M[j][j]) s = 1e-30 * M[j][j]; // guard against a vanishing pivot
            L[j][j] = Math.sqrt(s);
            for (int i = j + 1; i < n; i++) {
                double t = M[i][j];
                for (int p = 0; p < j; p++) t -= L[i][p] * L[j][p];
                L[i][j] = t / L[j][j];
            }
        }
        return L;
    }

    static double[] cholSolve(double[][] L, double[] r) {
        int n = L.length;
        double[] z = r.clone();
        for (int i = 0; i < n; i++) { for (int p = 0; p < i; p++) z[i] -= L[i][p] * z[p]; z[i] /= L[i][i]; }
        for (int i = n - 1; i >= 0; i--) { for (int p = i + 1; p < n; p++) z[i] -= L[p][i] * z[p]; z[i] /= L[i][i]; }
        return z;
    }

    /** The smallest-squares solution: x = A^T (A A^T)^-1 y. */
    static double[] leastNorm(double[][] A, double[] y) {
        int m = A.length, N = A[0].length;
        double[][] M = new double[m][m];
        for (int i = 0; i < m; i++) for (int j = 0; j < m; j++) for (int t = 0; t < N; t++) M[i][j] += A[i][t] * A[j][t];
        double[] w = cholSolve(cholesky(M), y);
        double[] x = new double[N];
        for (int i = 0; i < m; i++) for (int t = 0; t < N; t++) x[t] += A[i][t] * w[i];
        return x;
    }

    static int lastIterations;
    static double lastGap;

    /**
     * Basis pursuit: minimize sum |x_j| subject to A x = y, as the linear program min 1.(u + v), A u - A v = y,
     * u, v >= 0, by a primal-dual interior-point method with Mehrotra's predictor-corrector.
     */
    static double[] basisPursuit(double[][] A, double[] y) {
        int m = A.length, N = A[0].length, n = 2 * N;
        // B = [A, -A]; B z for z = (u, v); B^T l
        java.util.function.Function<double[], double[]> Bz = z -> { double[] r = new double[m]; for (int i = 0; i < m; i++) for (int j = 0; j < N; j++) r[i] += A[i][j] * (z[j] - z[N + j]); return r; };
        java.util.function.Function<double[], double[]> BTl = l -> { double[] r = new double[n]; for (int j = 0; j < N; j++) { double s = 0; for (int i = 0; i < m; i++) s += A[i][j] * l[i]; r[j] = s; r[N + j] = -s; } return r; };
        java.util.function.Function<double[], double[][]> normal = d -> { // B diag(d) B^T = A diag(d_u + d_v) A^T
            double[][] M = new double[m][m];
            for (int j = 0; j < N; j++) { double dj = d[j] + d[N + j]; for (int i = 0; i < m; i++) { double a = A[i][j] * dj; for (int k = 0; k <= i; k++) M[i][k] += a * A[k][j]; } }
            for (int i = 0; i < m; i++) for (int k = 0; k < i; k++) M[k][i] = M[i][k];
            double mx = 0;
            for (int i = 0; i < m; i++) mx = Math.max(mx, M[i][i]);
            for (int i = 0; i < m; i++) M[i][i] += 1e-14 * mx; // a tiny regularization keeps the factorization stable near the end
            return M;
        };
        double[] c = new double[n];
        Arrays.fill(c, 1);
        // Mehrotra's starting point
        double[] ones = new double[n];
        Arrays.fill(ones, 1);
        double[][] L0 = cholesky(normal.apply(ones));
        double[] z = BTl.apply(cholSolve(L0, y));
        double[] lam = cholSolve(L0, Bz.apply(c));
        double[] s = new double[n];
        double[] bl = BTl.apply(lam);
        for (int j = 0; j < n; j++) s[j] = c[j] - bl[j];
        double mz = 0, ms = 0;
        for (int j = 0; j < n; j++) { mz = Math.min(mz, z[j]); ms = Math.min(ms, s[j]); }
        for (int j = 0; j < n; j++) { z[j] += Math.max(-1.5 * mz, 0); s[j] += Math.max(-1.5 * ms, 0); }
        double zs = 0, sz = 0, ss = 0;
        for (int j = 0; j < n; j++) { zs += z[j] * s[j]; sz += z[j]; ss += s[j]; }
        for (int j = 0; j < n; j++) { z[j] += 0.5 * zs / ss; s[j] += 0.5 * zs / sz; }
        int it = 0;
        double bestScore = Double.POSITIVE_INFINITY;
        double[] best = z.clone(), bestLam = lam.clone();
        for (; it < 100; it++) {
            double[] bz = Bz.apply(z), btl = BTl.apply(lam);
            double[] rp = new double[m], rd = new double[n];
            for (int i = 0; i < m; i++) rp[i] = y[i] - bz[i];
            double mu = 0, nrp = 0, nrd = 0;
            for (int j = 0; j < n; j++) { rd[j] = c[j] - btl[j] - s[j]; mu += z[j] * s[j]; nrd = Math.max(nrd, Math.abs(rd[j])); }
            for (double v : rp) nrp = Math.max(nrp, Math.abs(v));
            mu /= n;
            double score = Math.max(nrp, Math.max(nrd, mu));
            if (!(score >= bestScore)) { bestScore = score; best = z.clone(); bestLam = lam.clone(); }
            if (nrp < 1e-9 && nrd < 1e-9 && mu < 1e-10) break; // stop before the last steps lose accuracy
            double[] d = new double[n];
            for (int j = 0; j < n; j++) d[j] = z[j] / s[j];
            double[][] L = cholesky(normal.apply(d));
            double[][] aff = direction(L, rp, rd, negProd(z, s), z, s, d, Bz, BTl, m, n);
            double ap = stepTo(z, aff[0], 1), ad = stepTo(s, aff[2], 1);
            double muAff = 0;
            for (int j = 0; j < n; j++) muAff += (z[j] + ap * aff[0][j]) * (s[j] + ad * aff[2][j]);
            muAff /= n;
            double sigma = Math.pow(muAff / mu, 3);
            double[] rc = new double[n];
            for (int j = 0; j < n; j++) rc[j] = -z[j] * s[j] - aff[0][j] * aff[2][j] + sigma * mu;
            double[][] dir = direction(L, rp, rd, rc, z, s, d, Bz, BTl, m, n);
            ap = stepTo(z, dir[0], 0.99); ad = stepTo(s, dir[2], 0.99);
            for (int j = 0; j < n; j++) { z[j] += ap * dir[0][j]; s[j] += ad * dir[2][j]; }
            for (int i = 0; i < m; i++) lam[i] += ad * dir[1][i];
        }
        lastIterations = it;
        z = best; lam = bestLam; // the most accurate iterate seen (normally the last)
        double primal = 0, dual = 0;
        for (int j = 0; j < n; j++) primal += z[j];
        for (int i = 0; i < m; i++) dual += y[i] * lam[i];
        lastGap = primal - dual;
        double[] x = new double[N];
        for (int j = 0; j < N; j++) x[j] = z[j] - z[N + j];
        return x;
    }

    static double[] negProd(double[] a, double[] b) { double[] r = new double[a.length]; for (int i = 0; i < a.length; i++) r[i] = -a[i] * b[i]; return r; }

    /** Solve B dz = rp, B^T dl + ds = rd, S dz + Z ds = rc through the normal equations (B D B^T) dl = rp - B S^-1 rc + B D rd. */
    static double[][] direction(double[][] L, double[] rp, double[] rd, double[] rc, double[] z, double[] s, double[] d,
                                java.util.function.Function<double[], double[]> Bz, java.util.function.Function<double[], double[]> BTl, int m, int n) {
        double[] t = new double[n];
        for (int j = 0; j < n; j++) t[j] = rc[j] / s[j] - d[j] * rd[j];
        double[] bt = Bz.apply(t);
        double[] rhs = new double[m];
        for (int i = 0; i < m; i++) rhs[i] = rp[i] - bt[i];
        double[] dl = cholSolve(L, rhs);
        double[] btdl = BTl.apply(dl);
        double[] ds = new double[n], dz = new double[n];
        for (int j = 0; j < n; j++) { ds[j] = rd[j] - btdl[j]; dz[j] = (rc[j] - z[j] * ds[j]) / s[j]; }
        return new double[][]{dz, dl, ds};
    }

    static double stepTo(double[] v, double[] dv, double eta) {
        double a = 1;
        for (int j = 0; j < v.length; j++) if (dv[j] < 0) a = Math.min(a, -eta * v[j] / dv[j]);
        return a;
    }

    static String f2(double v) { String t = String.format("%.2f", v); return t.equals("-0.00") ? "0.00" : t; }

    static double maxErr(double[] a, double[] b) { double e = 0; for (int i = 0; i < a.length; i++) e = Math.max(e, Math.abs(a[i] - b[i])); return e; }

    static double l1(double[] a) { double s = 0; for (double v : a) s += Math.abs(v); return s; }

    static boolean recovered(double[] xhat, double[] x) { return maxErr(xhat, x) < 1e-5; }

    public static void main(String[] args) {
        // ---- 1. one signal -----------------------------------------------------------------------------------------------
        int N = 128, k = 5, m = 40;
        double[] x = sparseSignal(N, k);
        double[][] A = gaussianMatrix(m, N);
        double[] y = mul(A, x);
        double[] xl1 = basisPursuit(A, y), xl2 = leastNorm(A, y);
        check(maxErr(mul(A, xl1), y) < 1e-8, "the l1 solution fits the measurements");
        check(maxErr(mul(A, xl2), y) < 1e-9, "so does the smallest-squares solution");
        check(recovered(xl1, x), "l1 minimization recovers the signal exactly");
        check(!recovered(xl2, x), "the smallest-squares solution does not");
        check(l1(xl1) <= l1(x) + 1e-8, "the l1 solution's norm is no bigger than the true signal's");
        int spread = 0;
        for (double v : xl2) if (Math.abs(v) > 0.01) spread++;
        StringJoiner nz = new StringJoiner(" ");
        for (int i = 0; i < N; i++) if (x[i] != 0) nz.add(String.format("%d:%.4f:%.4f:%.4f", i, x[i], xl1[i], xl2[i]));
        System.out.printf("one: N = %d, k = %d nonzero entries, m = %d random Gaussian measurements ; l1 minimization: %d interior-point iterations, duality gap %.1e, largest error %.1e ; smallest sum of squares: largest error %.3f, %d of the %d entries above 0.01 in size ; position:true:l1:squares %s%n",
                N, k, m, lastIterations, lastGap, maxErr(xl1, x), maxErr(xl2, x), spread, N, nz);

        // ---- 2. the phase transition -------------------------------------------------------------------------------------
        int[] ms = {16, 24, 32, 40, 48, 56, 64};
        int[] ks = {2, 4, 6, 8, 10, 12, 14, 16};
        int trials = 10, l2Successes = 0, total = 0;
        StringJoiner pj = new StringJoiner(" ; ");
        int[][] success = new int[ms.length][ks.length];
        for (int a = 0; a < ms.length; a++) {
            StringJoiner row = new StringJoiner(",");
            for (int b = 0; b < ks.length; b++) {
                for (int t = 0; t < trials; t++) {
                    double[] xs = sparseSignal(N, ks[b]);
                    double[][] As = gaussianMatrix(ms[a], N);
                    double[] ys = mul(As, xs);
                    double[] r = basisPursuit(As, ys);
                    check(maxErr(mul(As, r), ys) < 1e-7, "every l1 solution fits its measurements");
                    if (recovered(r, xs)) success[a][b]++;
                    if (recovered(leastNorm(As, ys), xs)) l2Successes++;
                    total++;
                }
                row.add(Integer.toString(success[a][b]));
            }
            pj.add("m = " + ms[a] + ": " + row);
        }
        check(success[ms.length - 1][0] == trials, "plenty of measurements, very sparse: always recovered");
        check(success[0][ks.length - 1] == 0, "few measurements, many entries: never");
        check(l2Successes == 0, "the smallest-squares solution never recovers the signal");
        System.out.printf("transition: N = %d ; signals recovered exactly by l1 minimization out of %d, for k = %s ; %s ; the smallest-squares solution: %d of %d%n",
                N, trials, Arrays.toString(ks).replace(" ", ""), pj, l2Successes, total);

        // ---- 3. the widget's small signal --------------------------------------------------------------------------------
        rnd = new Random(32);
        int n2 = 32;
        double[] xw = sparseSignal(n2, 3);
        double[][] Aw = gaussianMatrix(20, n2);
        StringJoiner xj = new StringJoiner(",");
        for (double v : xw) xj.add(f2(v));
        StringJoiner wj = new StringJoiner(" ; ");
        for (int mm : new int[]{4, 6, 8, 10, 12, 16, 20}) {
            double[][] Am = Arrays.copyOf(Aw, mm); // the first mm measurements
            double[] yw = mul(Am, xw);
            double[] r1 = basisPursuit(Am, yw), r2 = leastNorm(Am, yw);
            StringJoiner a1 = new StringJoiner(","), a2 = new StringJoiner(",");
            for (int i = 0; i < n2; i++) { a1.add(f2(r1[i])); a2.add(f2(r2[i])); }
            wj.add(String.format("m=%d %s l1=%s squares=%s", mm, recovered(r1, xw) ? "exact" : "wrong", a1, a2));
        }
        System.out.printf("widget: N = 32, k = 3 ; signal %s ; the first m rows of one 20-by-32 Gaussian matrix ; %s%n", xj, wj);

        System.out.println("CompressedSensing: " + passed + " checks passed");
    }
}
