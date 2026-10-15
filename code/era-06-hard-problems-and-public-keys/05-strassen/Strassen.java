import java.math.BigDecimal;
import java.util.*;

/**
 * Era 6, topic 5: multiplying matrices with seven products instead of eight (Strassen, 1969).
 *
 * HOW IT WORKS
 *   Two 2 x 2 matrices are multiplied, by the rule taught in school, with 8 multiplications:
 *       [a b] [e f]   [ae+bg  af+bh]
 *       [c d] [g h] = [ce+dg  cf+dh]
 *   Strassen found seven products that are enough:
 *       m1 = (a+d)(e+h)   m2 = (c+d)e   m3 = a(f-h)   m4 = d(g-e)   m5 = (a+b)h   m6 = (c-a)(e+f)   m7 = (b-d)(g+h)
 *       ae+bg = m1+m4-m5+m7   af+bh = m3+m5   ce+dg = m2+m4   cf+dh = m1-m2+m3+m6
 *   The letters may themselves be blocks of a bigger matrix, because the formulas never use ab = ba. So a matrix of
 *   size 2^k is cut into four blocks, seven products of half size are made, each the same way, down to single numbers:
 *   7^k multiplications instead of 8^k, that is n^2.807 instead of n^3. One saved multiplication, repeated at every
 *   level, changes the exponent.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Checks the seven-product formulas exactly, as bilinear forms, and on random numbers.
 *   2. Counts multiplications and additions for sizes 2 ... 4,096, school against Strassen, and finds where switching
 *      to the school method for small blocks pays.
 *   3. Multiplies two random 256 x 256 integer matrices both ways: identical results, multiplications counted.
 *   4. Rounding: on 128 x 128 matrices of decimals, both methods against the exact product.
 *   5. Inverting a matrix by blocks with the fast product, against Gauss-Jordan elimination.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Strassen.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Strassen {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1969L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static long mults, adds;

    // ---- matrices as double[][] ------------------------------------------------------------------------------------
    static double[][] school(double[][] A, double[][] B) {
        int n = A.length;
        double[][] C = new double[n][n];
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                double s = A[i][0] * B[0][j];
                mults++;
                for (int k = 1; k < n; k++) { s += A[i][k] * B[k][j]; mults++; adds++; }
                C[i][j] = s;
            }
        return C;
    }

    static double[][] add(double[][] A, double[][] B, int sign) {
        int n = A.length;
        double[][] C = new double[n][n];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) C[i][j] = A[i][j] + sign * B[i][j];
        adds += (long) n * n;
        return C;
    }

    static double[][] block(double[][] A, int r, int c, int h) {
        double[][] B = new double[h][h];
        for (int i = 0; i < h; i++) System.arraycopy(A[r + i], c, B[i], 0, h);
        return B;
    }

    static double[][] join(double[][] C11, double[][] C12, double[][] C21, double[][] C22) {
        int h = C11.length;
        double[][] C = new double[2 * h][2 * h];
        for (int i = 0; i < h; i++) {
            System.arraycopy(C11[i], 0, C[i], 0, h);
            System.arraycopy(C12[i], 0, C[i], h, h);
            System.arraycopy(C21[i], 0, C[i + h], 0, h);
            System.arraycopy(C22[i], 0, C[i + h], h, h);
        }
        return C;
    }

    /** Strassen's product; blocks of size <= cutoff are multiplied the school way. */
    static double[][] fast(double[][] A, double[][] B, int cutoff) {
        int n = A.length;
        if (n <= cutoff) return school(A, B);
        int h = n / 2;
        double[][] a = block(A, 0, 0, h), b = block(A, 0, h, h), c = block(A, h, 0, h), d = block(A, h, h, h);
        double[][] e = block(B, 0, 0, h), f = block(B, 0, h, h), g = block(B, h, 0, h), hh = block(B, h, h, h);
        double[][] m1 = fast(add(a, d, 1), add(e, hh, 1), cutoff);
        double[][] m2 = fast(add(c, d, 1), e, cutoff);
        double[][] m3 = fast(a, add(f, hh, -1), cutoff);
        double[][] m4 = fast(d, add(g, e, -1), cutoff);
        double[][] m5 = fast(add(a, b, 1), hh, cutoff);
        double[][] m6 = fast(add(c, a, -1), add(e, f, 1), cutoff);
        double[][] m7 = fast(add(b, d, -1), add(g, hh, 1), cutoff);
        double[][] C11 = add(add(add(m1, m4, 1), m5, -1), m7, 1);
        double[][] C12 = add(m3, m5, 1);
        double[][] C21 = add(m2, m4, 1);
        double[][] C22 = add(add(add(m1, m2, -1), m3, 1), m6, 1);
        return join(C11, C12, C21, C22);
    }

    /** Operation counts without doing the work: {multiplications, additions} for size n, cutoff c. */
    static long[] count(long n, long c) {
        if (n <= c) return new long[]{n * n * n, n * n * (n - 1)};
        long[] sub = count(n / 2, c);
        return new long[]{7 * sub[0], 7 * sub[1] + 18 * (n / 2) * (n / 2)};
    }

    static double[][] random(int n) {
        double[][] M = new double[n][n];
        for (double[] row : M) for (int j = 0; j < n; j++) row[j] = uniform();
        return M;
    }

    // ---- inversion by blocks ---------------------------------------------------------------------------------------
    /** Inverse of A by 2 x 2 blocks: two half-size inverses and six half-size products (fast), down to 1 x 1. */
    static double[][] invert(double[][] A) {
        int n = A.length;
        if (n == 1) { mults++; return new double[][]{{1 / A[0][0]}}; }
        int h = n / 2;
        double[][] A11 = block(A, 0, 0, h), A12 = block(A, 0, h, h), A21 = block(A, h, 0, h), A22 = block(A, h, h, h);
        double[][] I = invert(A11);
        double[][] II = fast(A21, I, 1);
        double[][] III = fast(I, A12, 1);
        double[][] IV = fast(A21, III, 1);
        double[][] V = add(IV, A22, -1);
        double[][] VI = invert(V);
        double[][] C12 = fast(III, VI, 1);
        double[][] C21 = fast(VI, II, 1);
        double[][] VII = fast(III, C21, 1);
        double[][] C11 = add(I, VII, -1);
        double[][] C22 = new double[h][h];
        for (int i = 0; i < h; i++) for (int j = 0; j < h; j++) C22[i][j] = -VI[i][j];
        return join(C11, C12, C21, C22);
    }

    static double[][] gaussJordan(double[][] A0) {
        int n = A0.length;
        double[][] A = new double[n][];
        for (int i = 0; i < n; i++) A[i] = A0[i].clone();
        double[][] X = new double[n][n];
        for (int i = 0; i < n; i++) X[i][i] = 1;
        for (int p = 0; p < n; p++) {
            double inv = 1 / A[p][p];
            mults++;
            for (int j = p + 1; j < n; j++) { A[p][j] *= inv; mults++; }
            for (int j = 0; j <= p; j++) { X[p][j] *= inv; mults++; }       // X's row p is zero beyond column p
            for (int i = 0; i < n; i++) {
                if (i == p) continue;
                double f = A[i][p];
                for (int j = p + 1; j < n; j++) { A[i][j] -= f * A[p][j]; mults++; }
                for (int j = 0; j <= p; j++) { X[i][j] -= f * X[p][j]; mults++; }
            }
        }
        return X;
    }

    public static void main(String[] args) {
        // ---- 1. the seven products ------------------------------------------------------------------------------------
        // A product (sum of x's)(sum of y's) is a 4 x 4 table of coefficients: entry [i][j] multiplies x_i * y_j.
        // x = a, b, c, d (indices 0..3) ; y = e, f, g, h.
        int[][][] m = new int[7][4][4];
        int[][] L = {{1, 0, 0, 1}, {0, 0, 1, 1}, {1, 0, 0, 0}, {0, 0, 0, 1}, {1, 1, 0, 0}, {-1, 0, 1, 0}, {0, 1, 0, -1}};
        int[][] R = {{1, 0, 0, 1}, {1, 0, 0, 0}, {0, 1, 0, -1}, {-1, 0, 1, 0}, {0, 0, 0, 1}, {1, 1, 0, 0}, {0, 0, 1, 1}};
        for (int p = 0; p < 7; p++) for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) m[p][i][j] = L[p][i] * R[p][j];
        int[][] combine = {{1, 0, 0, 1, -1, 0, 1}, {0, 0, 1, 0, 1, 0, 0}, {0, 1, 0, 1, 0, 0, 0}, {1, -1, 1, 0, 0, 1, 0}};
        // the school formulas: C11 = ae+bg, C12 = af+bh, C21 = ce+dg, C22 = cf+dh
        int[][][] want = new int[4][4][4];
        int[][] pairs = {{0, 0, 1, 2}, {0, 1, 1, 3}, {2, 0, 3, 2}, {2, 1, 3, 3}};
        for (int q = 0; q < 4; q++) { want[q][pairs[q][0]][pairs[q][1]] = 1; want[q][pairs[q][2]][pairs[q][3]] = 1; }
        for (int q = 0; q < 4; q++)
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++) {
                    int s = 0;
                    for (int p = 0; p < 7; p++) s += combine[q][p] * m[p][i][j];
                    check(s == want[q][i][j], "coefficient " + q + i + j);
                }
        for (int trial = 0; trial < 1000; trial++) {
            long[] x = new long[8];
            for (int i = 0; i < 8; i++) x[i] = (long) (uniform() * 2_000_001) - 1_000_000;
            long a = x[0], b = x[1], c = x[2], d = x[3], e = x[4], f = x[5], g = x[6], h = x[7];
            long m1 = (a + d) * (e + h), m2 = (c + d) * e, m3 = a * (f - h), m4 = d * (g - e), m5 = (a + b) * h, m6 = (c - a) * (e + f), m7 = (b - d) * (g + h);
            check(m1 + m4 - m5 + m7 == a * e + b * g && m3 + m5 == a * f + b * h && m2 + m4 == c * e + d * g && m1 - m2 + m3 + m6 == c * f + d * h, "random 2 x 2");
        }
        System.out.println("seven: m1 = (a+d)(e+h), m2 = (c+d)e, m3 = a(f-h), m4 = d(g-e), m5 = (a+b)h, m6 = (c-a)(e+f), m7 = (b-d)(g+h) ; ae+bg = m1+m4-m5+m7, af+bh = m3+m5, ce+dg = m2+m4, cf+dh = m1-m2+m3+m6 ; checked exactly as 4 x 4 coefficient tables (64 coefficients) and on 1,000 random 2 x 2 pairs ; 7 multiplications and 18 additions instead of 8 and 4");

        // ---- 2. counts ------------------------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        long firstWin = -1;
        for (int k = 1; k <= 12; k++) {
            long n = 1L << k;
            long[] sc = count(n, n), st = count(n, 1);
            check(st[0] == pow(7, k) && sc[0] == n * n * n, "multiplications for " + n);
            if (firstWin < 0 && st[0] + st[1] < sc[0] + sc[1]) firstWin = n;
            if (k % 2 == 0 || k == 1)
                cj.add(String.format("n=%,d: school %,d multiplications + %,d additions, Strassen to 1 x 1 %,d + %,d", n, sc[0], sc[1], st[0], st[1]));
        }
        long n4 = 4096, bestC = 0, bestOps = Long.MAX_VALUE;
        StringJoiner cutj = new StringJoiner(", ");
        for (long c = 1; c <= n4; c *= 2) {
            long[] r = count(n4, c);
            if (r[0] + r[1] < bestOps) { bestOps = r[0] + r[1]; bestC = c; }
            if (c >= 8 && c <= 256) cutj.add(String.format("%d: %,d", c, r[0] + r[1]));
        }
        long[] sch = count(n4, n4);
        check(bestOps < sch[0] + sch[1], "with a good cutoff Strassen wins at 4,096");
        System.out.printf("counts: %s ; counting multiplications and additions together, Strassen all the way down first beats the school method at n = %,d ; for n = 4,096, switching to the school method below a block size c gives totals %s ; best c = %d, %,d operations against %,d for the school method (%.2f times fewer)%n",
                cj, firstWin, cutj, bestC, bestOps, sch[0] + sch[1], (double) (sch[0] + sch[1]) / bestOps);

        // ---- 3. agreement on integers --------------------------------------------------------------------------------
        int n = 256;
        double[][] A = new double[n][n], B = new double[n][n];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) { A[i][j] = (int) (uniform() * 2001) - 1000; B[i][j] = (int) (uniform() * 2001) - 1000; }
        mults = adds = 0;
        double[][] C1 = school(A, B);
        long sm = mults, sa = adds;
        mults = adds = 0;
        double[][] C2 = fast(A, B, 1);
        long fm = mults, fa = adds;
        long[] exact = new long[]{0};
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n; j++) {
                long s = 0;
                for (int k = 0; k < n; k++) s += (long) A[i][k] * (long) B[k][j];
                check(C1[i][j] == s && C2[i][j] == s, "entry " + i + "," + j);
                exact[0] += Math.abs(s);
            }
        check(fm == pow(7, 8) && sm == (long) n * n * n, "256 x 256 counts");
        mults = adds = 0;
        fast(A, B, 32);
        long cm = mults, ca = adds;
        System.out.printf("agree: two random %d x %d matrices of whole numbers between -1000 and 1000 ; all %,d entries identical, school and Strassen ; school %,d multiplications and %,d additions ; Strassen to 1 x 1 %,d and %,d ; Strassen with school blocks of 32 %,d and %,d%n",
                n, n, n * n, sm, sa, fm, fa, cm, ca);

        // ---- 4. rounding ------------------------------------------------------------------------------------------------
        int r = 128;
        double[][] P = random(r), Q = random(r);
        double[][] D1 = school(P, Q), D2 = fast(P, Q, 1), D3 = fast(P, Q, 16);
        double e1 = 0, e2 = 0, e3 = 0;
        for (int i = 0; i < r; i++)
            for (int j = 0; j < r; j++) {
                BigDecimal s = BigDecimal.ZERO;
                for (int k = 0; k < r; k++) s = s.add(new BigDecimal(P[i][k]).multiply(new BigDecimal(Q[k][j])));
                e1 = Math.max(e1, Math.abs(new BigDecimal(D1[i][j]).subtract(s).doubleValue()));
                e2 = Math.max(e2, Math.abs(new BigDecimal(D2[i][j]).subtract(s).doubleValue()));
                e3 = Math.max(e3, Math.abs(new BigDecimal(D3[i][j]).subtract(s).doubleValue()));
            }
        check(e2 > e1 && e3 < e2, "Strassen rounds worse, less so with school blocks");
        check(e2 < 1e-10, "but still small");
        System.out.printf("rounding: two random %d x %d matrices of decimals between 0 and 1, entries of the product about 32 ; largest error against the exact product: school %.1e, Strassen to 1 x 1 %.1e (%.0f times larger), Strassen with school blocks of 16 %.1e%n",
                r, r, e1, e2, e2 / e1, e3);

        // ---- 5. inversion -----------------------------------------------------------------------------------------------
        int s = 256;
        double[][] M = random(s);
        for (int i = 0; i < s; i++) M[i][i] += s;                 // keeps every block invertible and well behaved
        mults = 0;
        double[][] X1 = gaussJordan(M);
        long gm = mults;
        mults = 0;
        double[][] X2 = invert(M);
        long im = mults;
        double res1 = 0, res2 = 0;
        double[][] R1 = school(M, X1), R2 = school(M, X2);
        for (int i = 0; i < s; i++)
            for (int j = 0; j < s; j++) {
                res1 = Math.max(res1, Math.abs(R1[i][j] - (i == j ? 1 : 0)));
                res2 = Math.max(res2, Math.abs(R2[i][j] - (i == j ? 1 : 0)));
            }
        check(res1 < 1e-12 && res2 < 1e-12, "both inverses are right");
        check(gm == (long) s * s * s + s, "Gauss-Jordan uses n^3 + n multiplications and divisions");
        check(im < gm, "block inversion with Strassen uses fewer");
        long[] inv = new long[13];
        inv[0] = 1;
        for (int k = 1; k <= 12; k++) inv[k] = 2 * inv[k - 1] + 6 * pow(7, k - 1);
        check(inv[8] == im, "count formula matches the run");
        System.out.printf("inverse: a random %d x %d matrix (made safe by adding %d along the diagonal) ; Gauss-Jordan elimination %,d multiplications and divisions ; inversion by 2 x 2 blocks (two half-size inverses and six half-size Strassen products) %,d ; matrix times inverse differs from the identity by at most %.1e and %.1e ; at 4,096 the counts would be %,d against %,d%n",
                s, s, s, gm, im, res1, res2, (long) 4096 * 4096 * 4096 + 4096, inv[12]);

        System.out.println("Strassen: " + passed + " checks passed");
    }

    static long pow(long b, int e) { long r = 1; for (int i = 0; i < e; i++) r *= b; return r; }
}
