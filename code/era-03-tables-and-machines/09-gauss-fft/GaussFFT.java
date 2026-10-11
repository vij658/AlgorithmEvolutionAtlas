import java.math.BigInteger;
import java.util.*;

/**
 * Era 3, topic 9: Gauss's fast Fourier transform (Göttingen, probably late 1805; printed 1866), rediscovered by
 * Cooley and Tukey (1965).
 *
 * HOW IT WORKS
 *   A periodic quantity measured at N equally spaced points (Gauss: positions of an asteroid around its orbit) can be
 *   written as a sum of sines and cosines. Finding their coefficients directly, each from all N observations, takes
 *   N x N products (the discrete Fourier transform). Gauss noticed that if N = N1 x N2, the observations fall into N2
 *   interleaved groups of N1 (for N = 12: three groups of four, n = 3 n1 + n2). Fit each small group first, adjust
 *   ("twiddle") the results by a turn of angle, then combine the groups with N1 small fits of size N2. The work drops
 *   from N^2 to about N (N1 + N2) products; splitting again and again, for N a power of 2, it drops to about
 *   (N/2) log2 N.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Fits 12 periodic observations directly and by Gauss's 4 x 3 and 3 x 4 splits, and counts the products.
 *   2. Checks that the fitted sum of sines and cosines passes through all 12 observations.
 *   3. Checks the fast transform against the direct one on random data for many sizes, and inverts it.
 *   4. Counts the products, direct against fast, for N from 8 to 1,048,576.
 *   5. Full circle: multiplies two 2,000-digit numbers by a fast transform of their digits.
 *   The 12 observations are the program's own test data: the sources opened for this book do not print Gauss's.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java GaussFFT.java
 *   Expected output: expected-output.txt in this folder.
 */
public class GaussFFT {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long mults;                                         // complex multiplications

    /** Direct transform: X[k] = sum_n x[n] e^(-2 pi i n k / N). */
    static double[][] dft(double[] re, double[] im) {
        int N = re.length;
        double[] R = new double[N], I = new double[N];
        for (int k = 0; k < N; k++)
            for (int n = 0; n < N; n++) {
                double a = -2 * Math.PI * ((long) n * k % N) / N, c = Math.cos(a), s = Math.sin(a);
                R[k] += re[n] * c - im[n] * s; I[k] += re[n] * s + im[n] * c; mults++;
            }
        return new double[][]{R, I};
    }

    /** Gauss's split for N = N1 * N2: N2 interleaved groups n = N2*n1 + n2, transformed, twiddled, combined. */
    static double[][] split(double[] re, double[] im, int N1, int N2) {
        int N = N1 * N2;
        double[][] YR = new double[N2][], YI = new double[N2][];
        for (int n2 = 0; n2 < N2; n2++) {                       // N2 transforms of length N1
            double[] gr = new double[N1], gi = new double[N1];
            for (int n1 = 0; n1 < N1; n1++) { gr[n1] = re[N2 * n1 + n2]; gi[n1] = im[N2 * n1 + n2]; }
            double[][] Y = dft(gr, gi);
            YR[n2] = Y[0]; YI[n2] = Y[1];
        }
        double[] R = new double[N], I = new double[N];
        for (int k1 = 0; k1 < N1; k1++) {
            double[] zr = new double[N2], zi = new double[N2];
            for (int n2 = 0; n2 < N2; n2++) {                   // twiddle by e^(-2 pi i n2 k1 / N)
                double a = -2 * Math.PI * n2 * k1 / N, c = Math.cos(a), s = Math.sin(a);
                zr[n2] = YR[n2][k1] * c - YI[n2][k1] * s; zi[n2] = YR[n2][k1] * s + YI[n2][k1] * c;
                if (n2 * k1 != 0) mults++;
            }
            double[][] Z = dft(zr, zi);                         // N1 transforms of length N2
            for (int k2 = 0; k2 < N2; k2++) { R[k1 + N1 * k2] = Z[0][k2]; I[k1 + N1 * k2] = Z[1][k2]; }
        }
        return new double[][]{R, I};
    }

    /** Radix-2 fast transform (recursive), counting the twiddle multiplications. */
    static void fft(double[] re, double[] im, boolean inverse) {
        int N = re.length;
        if (N == 1) return;
        double[] er = new double[N / 2], ei = new double[N / 2], or = new double[N / 2], oi = new double[N / 2];
        for (int i = 0; i < N / 2; i++) { er[i] = re[2 * i]; ei[i] = im[2 * i]; or[i] = re[2 * i + 1]; oi[i] = im[2 * i + 1]; }
        fft(er, ei, inverse); fft(or, oi, inverse);
        for (int k = 0; k < N / 2; k++) {
            double a = (inverse ? 2 : -2) * Math.PI * k / N, c = Math.cos(a), s = Math.sin(a);
            double tr = or[k] * c - oi[k] * s, ti = or[k] * s + oi[k] * c;
            mults++;
            re[k] = er[k] + tr; im[k] = ei[k] + ti; re[k + N / 2] = er[k] - tr; im[k + N / 2] = ei[k] - ti;
        }
    }

    static double maxDiff(double[][] a, double[][] b) {
        double m = 0;
        for (int i = 0; i < a[0].length; i++) m = Math.max(m, Math.hypot(a[0][i] - b[0][i], a[1][i] - b[1][i]));
        return m;
    }

    public static void main(String[] args) {
        // ---- 1. twelve periodic observations -------------------------------------------------------------------------
        int N = 12;
        double[] obs = new double[N], zero = new double[N];
        // test data: a periodic curve of the kind an orbit gives, with a mean, a first and a second harmonic
        for (int n = 0; n < N; n++) { double t = 2 * Math.PI * n / N; obs[n] = 700 + 450 * Math.cos(t) - 520 * Math.sin(t) + 90 * Math.cos(2 * t) + 35 * Math.sin(2 * t) + 12 * Math.cos(3 * t); obs[n] = Math.round(obs[n]); }
        StringJoiner os = new StringJoiner(", ");
        for (double v : obs) os.add(String.valueOf((long) v));
        mults = 0;
        double[][] direct = dft(obs, zero);
        long mDirect = mults;
        mults = 0;
        double[][] s43 = split(obs, zero, 4, 3);
        long m43 = mults;
        mults = 0;
        double[][] s34 = split(obs, zero, 3, 4);
        long m34 = mults;
        check(maxDiff(direct, s43) < 1e-9 && maxDiff(direct, s34) < 1e-9, "both of Gauss's splits give the direct coefficients");
        check(mDirect == 144, "direct: 144 products");
        // the coefficients as cosines and sines: a0 + sum (a_k cos kt + b_k sin kt)
        StringJoiner cf = new StringJoiner(" ; ");
        cf.add(String.format("mean %.2f", direct[0][0] / N));
        for (int k = 1; k <= 3; k++) cf.add(String.format("cos %dt %.2f, sin %dt %.2f", k, 2 * direct[0][k] / N, k, -2 * direct[1][k] / N));
        System.out.printf("twelve: observations at 0, 30, ..., 330 degrees: %s ; coefficients %s ; direct %d products ; Gauss's split 4 x 3: %d (three groups of four, n = 3 n1 + n2) ; 3 x 4: %d ; all three agree to %.0e%n",
                os, cf, mDirect, m43, m34, Math.max(maxDiff(direct, s43), maxDiff(direct, s34)) < 1e-9 ? 1e-9 : 1);

        // ---- 2. the fitted curve passes through every observation ------------------------------------------------------
        double worst = 0;
        for (int n = 0; n < N; n++) {
            double t = 2 * Math.PI * n / N, v = direct[0][0] / N;
            for (int k = 1; k < N / 2; k++) v += 2 * (direct[0][k] * Math.cos(k * t) - direct[1][k] * Math.sin(k * t)) / N;
            v += direct[0][N / 2] * Math.cos(N / 2.0 * t) / N;
            worst = Math.max(worst, Math.abs(v - obs[n]));
            check(Math.abs(v - obs[n]) < 1e-9, "the trigonometric sum passes through the observation");
        }
        double between = direct[0][0] / N;
        double tm = 2 * Math.PI * 0.5 / N;                       // halfway between the first two observations, 15 degrees
        for (int k = 1; k < N / 2; k++) between += 2 * (direct[0][k] * Math.cos(k * tm) - direct[1][k] * Math.sin(k * tm)) / N;
        between += direct[0][N / 2] * Math.cos(N / 2.0 * tm) / N;
        System.out.printf("interpolate: the sum of sines and cosines passes through all 12 observations (largest miss %.1e) ; at 15 degrees, between the first two, it gives %.2f%n", worst, between);

        // ---- 3. fast against direct on random data ------------------------------------------------------------------------
        Random rnd = new Random(1805);
        int sizes = 0;
        for (int p = 1; p <= 11; p++) {
            int M = 1 << p;
            for (int t = 0; t < 20; t++) {
                double[] r = new double[M], i = new double[M];
                for (int k = 0; k < M; k++) { r[k] = rnd.nextGaussian(); i[k] = rnd.nextGaussian(); }
                double[][] d = dft(r, i);
                double[] fr = r.clone(), fi = i.clone();
                fft(fr, fi, false);
                check(maxDiff(d, new double[][]{fr, fi}) < 1e-8 * M, "fast equals direct");
                fft(fr, fi, true);
                double back = 0;
                for (int k = 0; k < M; k++) back = Math.max(back, Math.hypot(fr[k] / M - r[k], fi[k] / M - i[k]));
                check(back < 1e-12 * M, "the inverse transform recovers the data");
            }
            sizes++;
        }
        System.out.printf("random: the fast transform equals the direct one, and its inverse recovers the data, on 20 random complex sequences of each length 2, 4, ..., 2,048 (%d lengths)%n", sizes);

        // ---- 4. counting the products ----------------------------------------------------------------------------------
        StringJoiner cnt = new StringJoiner(" ; ");
        for (int p : new int[]{3, 6, 10, 15, 20}) {
            long M = 1L << p;
            mults = 0;
            if (p <= 15) { double[] r = new double[(int) M], i = new double[(int) M]; fft(r, i, false); }
            else mults = (M / 2) * p;                            // the same count, (N/2) log2 N, without running it
            check(mults == (M / 2) * p, "the fast transform makes (N/2) log2 N twiddle products");
            cnt.add(String.format("N = %,d: direct %,d, fast %,d (%,d times fewer)", M, M * M, mults, M * M / mults));
        }
        System.out.printf("count: complex multiplications ; %s%n", cnt);

        // ---- 5. full circle: multiplying long numbers --------------------------------------------------------------------
        int digits = 2000;
        StringBuilder sa = new StringBuilder(), sb = new StringBuilder();
        sa.append(1 + rnd.nextInt(9)); sb.append(1 + rnd.nextInt(9));
        for (int k = 1; k < digits; k++) { sa.append(rnd.nextInt(10)); sb.append(rnd.nextInt(10)); }
        BigInteger A = new BigInteger(sa.toString()), B = new BigInteger(sb.toString());
        int L = 1; while (L < 2 * digits) L <<= 1;
        double[] ar = new double[L], ai = new double[L], br = new double[L], bi = new double[L];
        for (int k = 0; k < digits; k++) { ar[k] = sa.charAt(digits - 1 - k) - '0'; br[k] = sb.charAt(digits - 1 - k) - '0'; }
        mults = 0;
        fft(ar, ai, false); fft(br, bi, false);
        for (int k = 0; k < L; k++) { double r = ar[k] * br[k] - ai[k] * bi[k], i = ar[k] * bi[k] + ai[k] * br[k]; ar[k] = r; ai[k] = i; mults++; }
        fft(ar, ai, true);
        long fftMults = mults;
        // carry, as on Pascal's wheels (topic 3)
        StringBuilder prod = new StringBuilder();
        long carry = 0;
        for (int k = 0; k < L; k++) { long v = Math.round(ar[k] / L) + carry; prod.append(v % 10); carry = v / 10; }
        while (carry > 0) { prod.append(carry % 10); carry /= 10; }
        String ps = prod.reverse().toString().replaceFirst("^0+", "");
        check(ps.equals(A.multiply(B).toString()), "the product by fast transform equals BigInteger's");
        System.out.printf("circle: two random %,d-digit numbers multiplied by transforming their digits, multiplying point by point, transforming back and carrying ; the %,d-digit product matches Java's BigInteger ; %,d complex multiplications, against %,d digit products by long multiplication%n",
                digits, ps.length(), fftMults, (long) digits * digits);

        System.out.printf("GaussFFT: %d checks passed%n", passed);
    }
}
