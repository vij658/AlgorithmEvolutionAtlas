import java.util.*;

/**
 * Era 7, topic 11: Shor's factoring algorithm (Peter Shor, Bell Labs, 1994), simulated on an ordinary computer.
 *
 * HOW IT WORKS
 *   Factoring N reduces to finding a period. Pick a number a at random. The powers a, a^2, a^3, ... modulo N repeat
 *   with some period r (the "order" of a). If r is even, then (a^(r/2) - 1)(a^(r/2) + 1) is a multiple of N, and
 *   for at least half of the choices of a, a greatest common divisor (Euclid, Era 1) with N splits N. Finding r is the
 *   hard part: no fast classical method is known. A quantum computer puts a register into a superposition of all x
 *   from 0 to Q - 1 (Q at least N^2) at once, computes a^x mod N into a second register, and measures it: what is left
 *   is a superposition of the x that share one value, spaced r apart. A quantum Fourier transform (the FFT, Era 6,
 *   done by interference) turns that comb into peaks near multiples of Q / r; one measurement gives a number y near
 *   one of them, and continued fractions recover r from y / Q. This program does every step with ordinary arithmetic,
 *   storing all Q amplitudes, which is exactly why simulating it is hopeless for large N, and why a quantum computer
 *   would not be.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The classical reduction: for many N, the share of choices of a whose period splits N.
 *   2. The quantum step for N = 15 and N = 21: where the measurement probabilities pile up.
 *   3. The whole algorithm, simulated, for N up to 1,007: measurements needed until a factor appears.
 *   4. The cost of simulating it: amplitudes needed against the number of digits of N.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ShorFactoring.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ShorFactoring {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1994L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static long gcd(long a, long b) { while (b != 0) { long t = a % b; a = b; b = t; } return Math.abs(a); }

    static long powmod(long a, long e, long n) {
        long r = 1 % n;
        a %= n;
        while (e > 0) { if ((e & 1) == 1) r = r * a % n; a = a * a % n; e >>= 1; }
        return r;
    }

    /** The order of a modulo n, by brute force (the step a quantum computer would do quickly). */
    static long order(long a, long n) {
        long x = a % n, r = 1;
        while (x != 1) { x = x * a % n; r++; }
        return r;
    }

    /** The classical post-processing: a factor of n from the order r of a, or -1 if this a fails. */
    static long splitWith(long a, long r, long n) {
        if (r % 2 == 1) return -1;
        long h = powmod(a, r / 2, n);
        if (h == n - 1) return -1;
        long f = gcd(h - 1, n);
        return f > 1 && f < n ? f : -1;
    }

    // ---- the quantum Fourier transform, simulated by a complex FFT of size Q --------------------------------------
    static void fft(double[] re, double[] im) {
        int n = re.length;
        for (int i = 1, j = 0; i < n; i++) {
            int bit = n >> 1;
            for (; (j & bit) != 0; bit >>= 1) j ^= bit;
            j ^= bit;
            if (i < j) { double t = re[i]; re[i] = re[j]; re[j] = t; t = im[i]; im[i] = im[j]; im[j] = t; }
        }
        for (int len = 2; len <= n; len <<= 1) {
            double ang = 2 * Math.PI / len;
            for (int i = 0; i < n; i += len)
                for (int k = 0; k < len / 2; k++) {
                    double wr = Math.cos(ang * k), wi = Math.sin(ang * k);
                    int u = i + k, v = i + k + len / 2;
                    double xr = re[v] * wr - im[v] * wi, xi = re[v] * wi + im[v] * wr;
                    re[v] = re[u] - xr; im[v] = im[u] - xi;
                    re[u] += xr; im[u] += xi;
                }
        }
    }

    /**
     * The probabilities of measuring y in the first register, after the second register was measured and gave
     * a^x0 mod n: the first register holds an equal superposition of x = x0, x0 + r, x0 + 2r, ... below Q.
     */
    static double[] measureProbabilities(long a, long n, int Q, int x0) {
        double[] re = new double[Q], im = new double[Q];
        long z = powmod(a, x0, n);
        int count = 0;
        long v = 1;
        for (int x = 0; x < Q; x++) {                       // this loop is the "modular exponentiation" step
            if (v == z) { re[x] = 1; count++; }
            v = v * a % n;
        }
        double norm = 1 / Math.sqrt(count);
        for (int x = 0; x < Q; x++) re[x] *= norm;
        fft(re, im);
        double[] p = new double[Q];
        for (int y = 0; y < Q; y++) p[y] = (re[y] * re[y] + im[y] * im[y]) / Q;
        return p;
    }

    /** Continued fractions: the denominators of the convergents of y / Q, smallest first. */
    static List<Long> convergentDenominators(long y, long Q, long limit) {
        List<Long> out = new ArrayList<>();
        long h0 = 0, h1 = 1, k0 = 1, k1 = 0;               // standard recurrence, starting from the empty fraction
        long num = y, den = Q;
        while (den != 0) {
            long q = num / den;
            long h2 = q * h1 + h0, k2 = q * k1 + k0;
            if (k2 >= limit) break;
            out.add(k2);
            h0 = h1; h1 = h2; k0 = k1; k1 = k2;
            long t = num - q * den; num = den; den = t;
        }
        return out;
    }

    static int sample(double[] p) {
        double u = uniform(), c = 0;
        for (int y = 0; y < p.length; y++) { c += p[y]; if (u < c) return y; }
        return p.length - 1;
    }

    public static void main(String[] args) {
        // ---- 1. the reduction ----------------------------------------------------------------------------------------
        long[] Ns = {15, 21, 33, 35, 39, 51, 55, 57, 65, 77, 91, 143, 221, 323, 1007, 3233, 10403, 25217};
        StringJoiner rj = new StringJoiner(" ; ");
        double worst = 1;
        for (long n : Ns) {
            int good = 0, tried = 0;
            for (long a = 2; a < n; a++) {
                if (gcd(a, n) != 1) continue;               // (a lucky a that shares a factor splits N at once)
                tried++;
                long f = splitWith(a, order(a, n), n);
                if (f > 0) { check(n % f == 0, "the gcd is a real factor"); good++; }
            }
            double share = (double) good / tried;
            worst = Math.min(worst, share);
            if (n == 15 || n == 21 || n == 91 || n == 1007 || n == 3233 || n == 25217)
                rj.add(String.format("N=%,d: %,d of %,d choices of a work (%.0f%%)", n, good, tried, 100 * share));
        }
        check(worst >= 0.5, "at least half of the a's work for a product of two distinct odd primes");
        System.out.printf("reduction: for %d products of two distinct odd primes from 15 to 25,217, every a with no factor in common with N, its period r found by brute force, and gcd(a^(r/2) - 1, N) tried ; %s ; the smallest share over all %d was %.0f%%%n",
                Ns.length, rj, Ns.length, 100 * worst);

        // ---- 2. the quantum step for 15 and 21 -----------------------------------------------------------------------
        StringJoiner pj = new StringJoiner(" ; ");
        {
            long n = 15, a = 7;
            int Q = 256;
            long r = order(a, n);
            double[] p = measureProbabilities(a, n, Q, 0);
            double onPeaks = 0;
            for (int k = 0; k < r; k++) onPeaks += p[(int) (k * Q / r)];
            check(r == 4 && Math.abs(onPeaks - 1) < 1e-9, "for N = 15 all the probability sits exactly on multiples of Q/4");
            pj.add(String.format("N=15, a=7, period %d, Q=%d: probability %.3f at each of y = 0, 64, 128, 192, and %.3f everywhere else", r, Q, p[64], 1 - onPeaks));
        }
        {
            long n = 21, a = 2;
            int Q = 512;
            long r = order(a, n);
            double[] p = measureProbabilities(a, n, Q, 0);
            double near = 0;
            StringJoiner peaks = new StringJoiner(", ");
            for (int k = 0; k < r; k++) {
                int y = (int) Math.round((double) k * Q / r);
                near += p[y];
                peaks.add(String.format("%d", y));
            }
            check(r == 6 && near > 0.4, "for N = 21 most probability is on the integers nearest k Q / 6");
            pj.add(String.format("N=21, a=2, period %d, Q=%d: Q/r = %.2f is not a whole number, so the peaks spread ; the integers nearest k Q / r (%s) carry %.3f of the probability together", r, Q, (double) Q / r, peaks, near));
        }
        System.out.printf("peaks: after the second register is measured and the Fourier transform applied, the chance of each measurement y of the first register ; %s%n", pj);

        // ---- 3. the whole algorithm -----------------------------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        long[] targets = {15, 21, 35, 77, 143, 221, 323, 391, 437, 667, 899, 1007};
        long totalMeasurements = 0;
        for (long n : targets) {
            int bits = 64 - Long.numberOfLeadingZeros(n * n - 1);
            int Q = 1 << bits;                                     // Q is the first power of two at least N^2
            int measurements = 0, choices = 0;
            long factor = -1;
            while (factor < 0) {
                long a = 2 + (long) (uniform() * (n - 3));
                choices++;
                if (gcd(a, n) > 1) { choices--; continue; }        // such a lucky a would split N at once; skip it,
                                                                   // to watch the quantum step do the work
                int x0 = (int) (uniform() * Q);
                double[] p = measureProbabilities(a, n, Q, x0);
                for (int attempt = 0; attempt < 4 && factor < 0; attempt++) {
                    int y = sample(p);
                    measurements++;
                    for (long s : convergentDenominators(y, Q, n)) {
                        for (long mult = 1; mult <= 4 && s * mult < n; mult++) {   // r may be a small multiple of s
                            if (s * mult > 0 && powmod(a, s * mult, n) == 1) {
                                long f = splitWith(a, s * mult, n);
                                if (f > 0) factor = f;
                                break;
                            }
                        }
                        if (factor > 0) break;
                    }
                }
            }
            check(n % factor == 0 && factor > 1 && factor < n, "a real factor");
            totalMeasurements += measurements;
            sj.add(String.format("N=%,d = %d x %d: Q=2^%d, %d choice%s of a, %d measurement%s", n, Math.min(factor, n / factor), Math.max(factor, n / factor), bits, choices, choices == 1 ? "" : "s", measurements, measurements == 1 ? "" : "s"));
        }
        System.out.printf("shor: the whole algorithm simulated with all Q amplitudes stored, Q the first power of two at least N^2, a chosen at random with no factor in common with N ; %s ; %d simulated measurements in all%n", sj, totalMeasurements);

        // ---- 4. the cost of simulating -------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        for (int bits : new int[]{10, 20, 64, 512, 2048}) {
            int qbits = 2 * bits;
            cj.add(String.format("a %,d-bit N: %,d qubits in the first register, 2^%,d amplitudes to store", bits, qbits, qbits));
        }
        System.out.printf("cost: a quantum computer's first register needs about 2 log2 N qubits, but simulating it stores one complex number for every value it can hold ; %s%n", cj);

        System.out.println("ShorFactoring: " + passed + " checks passed");
    }
}
