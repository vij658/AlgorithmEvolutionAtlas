import java.math.BigInteger;
import java.util.*;

/**
 * Era 6, topic 1: the fast Fourier transform, for machines (Cooley and Tukey, 1965).
 *
 * HOW IT WORKS
 *   The discrete Fourier transform turns N samples x_0 ... x_(N-1) into N frequencies
 *       X_k = sum over n of x_n * w^(nk),   w = e^(-2 pi i / N),
 *   about N^2 multiplications. If N is even, the sum splits into the even-numbered samples and the odd-numbered ones:
 *       X_k = E_k + w^k O_k,   X_(k + N/2) = E_k - w^k O_k,
 *   where E and O are transforms of half the length. Each pair of outputs costs one multiplication (a "butterfly").
 *   Repeating the split down to single samples gives log2 N stages of N/2 butterflies. Done in place, the samples
 *   must first be put in "bit-reversed" order: sample n goes to the position whose binary digits are n's reversed.
 *   Because multiplying two numbers is a convolution of their digits, and the transform turns a convolution into
 *   pointwise products, the same trick multiplies very long numbers quickly.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The bit-reversed order for 8 and 16 samples.
 *   2. The FFT against the direct sum on random data of 1,024 samples: the largest difference.
 *   3. Complex multiplications counted for N = 2^4 ... 2^20, direct against fast.
 *   4. A "seismogram": two waves hidden in noise four times their size, found as the two tallest peaks.
 *   5. Two 4,000-digit numbers multiplied through the FFT, against Java's BigInteger.
 *   6. The inverse transform gives the samples back.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java FastFourier.java
 *   Expected output: expected-output.txt in this folder.
 */
public class FastFourier {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long mults;

    static int reverse(int i, int bits) {
        int r = 0;
        for (int b = 0; b < bits; b++) { r = (r << 1) | (i & 1); i >>= 1; }
        return r;
    }

    /** In-place radix-2 FFT of (re, im); inverse if sign = +1. */
    static void fft(double[] re, double[] im, int sign) {
        int n = re.length, bits = Integer.numberOfTrailingZeros(n);
        for (int i = 0; i < n; i++) {
            int j = reverse(i, bits);
            if (j > i) { double t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
        }
        for (int len = 2; len <= n; len <<= 1) {
            double ang = sign * 2 * Math.PI / len;
            for (int start = 0; start < n; start += len)
                for (int k = 0; k < len / 2; k++) {
                    double wr = Math.cos(ang * k), wi = Math.sin(ang * k);
                    int a = start + k, b = a + len / 2;
                    double tr = re[b] * wr - im[b] * wi, ti = re[b] * wi + im[b] * wr;   // one complex multiplication
                    mults++;
                    re[b] = re[a] - tr; im[b] = im[a] - ti;
                    re[a] += tr; im[a] += ti;
                }
        }
        if (sign > 0) for (int i = 0; i < n; i++) { re[i] /= n; im[i] /= n; }
    }

    static double[][] dft(double[] re, double[] im) {
        int n = re.length;
        double[] or = new double[n], oi = new double[n];
        for (int k = 0; k < n; k++)
            for (int j = 0; j < n; j++) {
                double ang = -2 * Math.PI * ((long) j * k % n) / n;
                or[k] += re[j] * Math.cos(ang) - im[j] * Math.sin(ang);
                oi[k] += re[j] * Math.sin(ang) + im[j] * Math.cos(ang);
                mults++;
            }
        return new double[][]{or, oi};
    }

    static long seed = 1965L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static double gauss() { return Math.sqrt(-2 * Math.log(1 - uniform())) * Math.cos(2 * Math.PI * uniform()); }

    public static void main(String[] args) {
        // ---- 1. bit reversal ----------------------------------------------------------------------------------------------
        StringJoiner b8 = new StringJoiner(" "), b16 = new StringJoiner(" ");
        for (int i = 0; i < 8; i++) b8.add(String.valueOf(reverse(i, 3)));
        for (int i = 0; i < 16; i++) b16.add(String.valueOf(reverse(i, 4)));
        check(b8.toString().equals("0 4 2 6 1 5 3 7"), "bit reversal of 8");
        System.out.printf("bitrev: positions 0 to 7 hold samples %s (6 = 110 in binary holds sample 011 = 3) ; for 16: %s%n", b8, b16);

        // ---- 2. agreement ---------------------------------------------------------------------------------------------------
        int n = 1024;
        double[] re = new double[n], im = new double[n];
        for (int i = 0; i < n; i++) { re[i] = uniform() * 2 - 1; im[i] = uniform() * 2 - 1; }
        mults = 0;
        double[][] direct = dft(re, im);
        long dftMults = mults;
        double[] fr = re.clone(), fi = im.clone();
        mults = 0;
        fft(fr, fi, -1);
        long fftMults = mults;
        double worst = 0;
        for (int k = 0; k < n; k++) {
            double diff = Math.hypot(fr[k] - direct[0][k], fi[k] - direct[1][k]);
            check(diff < 1e-9, "frequency " + k + " agrees");
            worst = Math.max(worst, diff);
        }
        check(worst < 1e-9, "FFT equals the direct sum");
        check(dftMults == (long) n * n && fftMults == (long) n / 2 * 10, "operation counts");
        System.out.printf("agree: %,d random complex samples ; direct sum %,d complex multiplications, FFT %,d (%.0f times fewer) ; largest difference between the two answers %.1e%n",
                n, dftMults, fftMults, (double) dftMults / fftMults, worst);

        // ---- 3. counts ---------------------------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        for (int k = 4; k <= 20; k += 4) {
            long N = 1L << k, d = N * N, f = N / 2 * k;
            cj.add(String.format("N=%,d: direct %,d, fast %,d, %,.0f times fewer", N, d, f, (double) d / f));
        }
        double[] big = new double[1 << 20], bigi = new double[1 << 20];
        for (int i = 0; i < big.length; i++) big[i] = uniform();
        mults = 0;
        fft(big, bigi, -1);
        check(mults == (1L << 19) * 20, "a million-point FFT does N/2 log2 N multiplications");
        System.out.printf("counts: complex multiplications, N^2 for the direct sum against (N/2) log2 N for the FFT ; %s ; the program ran the 1,048,576-point FFT and counted %,d%n", cj, mults);

        // ---- 4. a seismogram ---------------------------------------------------------------------------------------------
        int m = 4096;
        double[] sr = new double[m], si = new double[m];
        int f1 = 237, f2 = 1001;
        for (int i = 0; i < m; i++) sr[i] = 1.0 * Math.sin(2 * Math.PI * f1 * i / m) + 0.6 * Math.sin(2 * Math.PI * f2 * i / m) + 4.0 * gauss();
        fft(sr, si, -1);
        double[] power = new double[m / 2];
        for (int k = 1; k < m / 2; k++) power[k] = sr[k] * sr[k] + si[k] * si[k];
        Integer[] idx = new Integer[m / 2 - 1];
        for (int k = 1; k < m / 2; k++) idx[k - 1] = k;
        Arrays.sort(idx, (a, b) -> Double.compare(power[b], power[a]));
        int p1 = Math.min(idx[0], idx[1]), p2 = Math.max(idx[0], idx[1]);
        check(p1 == f1 && p2 == f2, "the two waves are the two tallest peaks");
        double mean = 0;
        for (int k = 1; k < m / 2; k++) mean += power[k];
        mean /= (m / 2 - 1);
        System.out.printf("signal: %,d samples ; waves of %d and %d cycles, heights 1.0 and 0.6, buried in random noise of spread 4.0 ; the two tallest peaks of the transform are at %d and %d cycles, %.0f and %.0f times the average height of the others%n",
                m, f1, f2, p1, p2, power[f1] / mean, power[f2] / mean);

        // ---- 5. multiplying long numbers ------------------------------------------------------------------------------
        int digits = 4000;
        StringBuilder sa = new StringBuilder(), sb = new StringBuilder();
        sa.append(1 + (int) (uniform() * 9));
        sb.append(1 + (int) (uniform() * 9));
        for (int i = 1; i < digits; i++) { sa.append((int) (uniform() * 10)); sb.append((int) (uniform() * 10)); }
        int size = Integer.highestOneBit(2 * digits - 1) << 1;
        double[] ar = new double[size], ai = new double[size], br = new double[size], bi = new double[size];
        for (int i = 0; i < digits; i++) { ar[i] = sa.charAt(digits - 1 - i) - '0'; br[i] = sb.charAt(digits - 1 - i) - '0'; }
        mults = 0;
        fft(ar, ai, -1);
        fft(br, bi, -1);
        for (int i = 0; i < size; i++) { double r = ar[i] * br[i] - ai[i] * bi[i], im2 = ar[i] * bi[i] + ai[i] * br[i]; ar[i] = r; ai[i] = im2; mults++; }
        fft(ar, ai, 1);
        long fftTotal = mults;
        long[] coef = new long[size];
        double maxErr = 0;
        for (int i = 0; i < size; i++) { coef[i] = Math.round(ar[i]); maxErr = Math.max(maxErr, Math.abs(ar[i] - coef[i])); }
        StringBuilder prod = new StringBuilder();
        long carry = 0;
        for (int i = 0; i < size; i++) { long v = coef[i] + carry; prod.append((char) ('0' + v % 10)); carry = v / 10; }
        while (carry > 0) { prod.append((char) ('0' + carry % 10)); carry /= 10; }
        String p = prod.reverse().toString().replaceFirst("^0+", "");
        String want = new BigInteger(sa.toString()).multiply(new BigInteger(sb.toString())).toString();
        check(p.equals(want), "FFT product equals BigInteger");
        check(maxErr < 0.1, "rounding is safe");
        System.out.printf("multiply: two random %,d-digit numbers ; their digits convolved through three FFTs of %,d points: %,d complex multiplications, against %,d digit products by schoolbook ; the %,d-digit product, starting %s and ending %s, equals Java's BigInteger result ; largest rounding error %.3f%n",
                digits, size, fftTotal, (long) digits * digits, p.length(), p.substring(0, 12), p.substring(p.length() - 12), maxErr);

        // ---- 6. inverse --------------------------------------------------------------------------------------------------
        double[] xr = new double[256], xi = new double[256];
        for (int i = 0; i < 256; i++) xr[i] = uniform();
        double[] keep = xr.clone();
        fft(xr, xi, -1);
        fft(xr, xi, 1);
        double back = 0;
        for (int i = 0; i < 256; i++) { double e = Math.abs(xr[i] - keep[i]) + Math.abs(xi[i]); check(e < 1e-12, "sample " + i + " comes back"); back = Math.max(back, e); }
        check(back < 1e-12, "inverse returns the samples");
        System.out.printf("inverse: 256 random samples transformed and transformed back with the opposite sign and a division by 256 ; largest difference from the original %.1e%n", back);

        System.out.println("FastFourier: " + passed + " checks passed");
    }
}
