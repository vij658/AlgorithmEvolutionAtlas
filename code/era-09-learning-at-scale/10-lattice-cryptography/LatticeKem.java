import java.util.*;

/**
 * Era 9, topic 10: Lattice cryptography and ML-KEM (Oded Regev's learning with errors, 2005; CRYSTALS-Kyber,
 * submitted to NIST in 2017; FIPS 203, August 2024).
 *
 * HOW IT WORKS
 *   Learning with errors: given a random matrix A and b = A s + e (mod q), where s is secret and e is a vector of
 *   small random errors, find s. Without e, Gaussian elimination finds s at once; with e, no efficient method is
 *   known, on ordinary or quantum computers. Kyber works with polynomials of degree below n = 256, coefficients
 *   modulo q = 3329, and arithmetic modulo X^256 + 1; a "module" is a short vector (k = 2, 3 or 4) of them.
 *     Key generation: public t = A s + e, with s and e small; A comes from a public seed.
 *     Encryption of a 256-bit message m: pick small r, e1, e2; send u = A^T r + e1 and
 *       v = t^T r + e2 + (q/2 rounded) * m, each rounded to fewer bits (Compress with d_u and d_v bits).
 *     Decryption: v - s^T u = e^T r + e2 + (q/2) m - s^T e1 + rounding: a small noise plus m times q/2,
 *       so each coefficient near q/2 is a 1 and near 0 is a 0.
 *   Polynomials are multiplied with the number-theoretic transform, the Fourier transform modulo q, using
 *   zeta = 17, a primitive 256th root of unity modulo 3329.
 *   This program implements the arithmetic of ML-KEM's inner encryption scheme (K-PKE) as FIPS 203 describes it,
 *   with java.util.Random in place of the standard's SHA-3 and SHAKE hashing; it is a model for study, not a
 *   conforming or secure implementation.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Learning with and without errors: Gaussian elimination recovers s from exact equations and fails with errors.
 *   2. The number-theoretic transform: 17 is a primitive 256th root of unity, and multiplication through the NTT
 *      equals schoolbook multiplication modulo X^256 + 1.
 *   3. The three parameter sets: thousands of encryptions each, every message recovered, the largest noise against
 *      the margin q/4; key and ciphertext sizes from the formulas, against the published sizes.
 *   4. Too much noise: larger errors or harsher rounding, and decryption starts to fail.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LatticeKem.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LatticeKem {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int N = 256, Q = 3329, ZETA = 17;

    static int mod(long x) { long r = x % Q; return (int) (r < 0 ? r + Q : r); }

    static int pow(int b, int e) { long r = 1, x = b; while (e > 0) { if ((e & 1) == 1) r = r * x % Q; x = x * x % Q; e >>= 1; } return (int) r; }

    static int bitrev7(int i) { int r = 0; for (int k = 0; k < 7; k++) if ((i >> k & 1) == 1) r |= 1 << (6 - k); return r; }

    // ---- the number-theoretic transform (FIPS 203, Algorithms 9 to 12) --------------------------------------------------
    static int[] ntt(int[] a) {
        int[] f = a.clone();
        int i = 1;
        for (int len = 128; len >= 2; len /= 2)
            for (int start = 0; start < N; start += 2 * len) {
                int z = pow(ZETA, bitrev7(i++));
                for (int j = start; j < start + len; j++) {
                    int t = mod((long) z * f[j + len]);
                    f[j + len] = mod(f[j] - t);
                    f[j] = mod(f[j] + t);
                }
            }
        return f;
    }

    static int[] invNtt(int[] a) {
        int[] f = a.clone();
        int i = 127;
        for (int len = 2; len <= 128; len *= 2)
            for (int start = 0; start < N; start += 2 * len) {
                int z = pow(ZETA, bitrev7(i--));
                for (int j = start; j < start + len; j++) {
                    int t = f[j];
                    f[j] = mod(t + f[j + len]);
                    f[j + len] = mod((long) z * (f[j + len] - t));
                }
            }
        for (int j = 0; j < N; j++) f[j] = mod((long) f[j] * 3303);
        return f;
    }

    static int[] mulNtt(int[] f, int[] g) {
        int[] h = new int[N];
        for (int i = 0; i < 128; i++) {
            int gamma = pow(ZETA, 2 * bitrev7(i) + 1);
            long a0 = f[2 * i], a1 = f[2 * i + 1], b0 = g[2 * i], b1 = g[2 * i + 1];
            h[2 * i] = mod(a0 * b0 + mod(a1 * b1) * (long) gamma);
            h[2 * i + 1] = mod(a0 * b1 + a1 * b0);
        }
        return h;
    }

    /** Schoolbook multiplication modulo X^256 + 1, for checking. */
    static int[] mulSlow(int[] a, int[] b) {
        long[] c = new long[N];
        for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) {
            long p = (long) a[i] * b[j];
            if (i + j < N) c[i + j] += p; else c[i + j - N] -= p;
        }
        int[] r = new int[N];
        for (int i = 0; i < N; i++) r[i] = mod(c[i]);
        return r;
    }

    static int[] add(int[] a, int[] b) { int[] c = new int[N]; for (int i = 0; i < N; i++) c[i] = mod(a[i] + b[i]); return c; }
    static int[] sub(int[] a, int[] b) { int[] c = new int[N]; for (int i = 0; i < N; i++) c[i] = mod(a[i] - b[i]); return c; }

    /** Centred binomial distribution with parameter eta: sum of eta coin flips minus sum of eta coin flips. */
    static int[] cbd(int eta, Random r) {
        int[] p = new int[N];
        for (int i = 0; i < N; i++) { int x = 0; for (int k = 0; k < eta; k++) x += r.nextInt(2) - r.nextInt(2); p[i] = mod(x); }
        return p;
    }

    static int compress(int x, int d) { return (int) (((((long) x << d) + Q / 2) / Q) & ((1 << d) - 1)); }
    static int decompress(int y, int d) { return (int) (((long) y * Q + (1L << (d - 1))) >> d); }

    static int[] roundTrip(int[] a, int d) { int[] c = new int[N]; for (int i = 0; i < N; i++) c[i] = decompress(compress(a[i], d), d); return c; }

    /** Centred representative of x mod q, in (-q/2, q/2]. */
    static int centre(int x) { return x > Q / 2 ? x - Q : x; }

    // ---- K-PKE ----------------------------------------------------------------------------------------------------------
    static class Params {
        final String name; final int k, eta1, eta2, du, dv;
        Params(String name, int k, int eta1, int eta2, int du, int dv) { this.name = name; this.k = k; this.eta1 = eta1; this.eta2 = eta2; this.du = du; this.dv = dv; }
    }

    static class Keys { int[][][] Ahat; int[][] that, shat; }

    static Keys keygen(Params P, Random r) {
        Keys K = new Keys();
        K.Ahat = new int[P.k][P.k][N];
        for (int i = 0; i < P.k; i++) for (int j = 0; j < P.k; j++) for (int c = 0; c < N; c++) K.Ahat[i][j][c] = r.nextInt(Q);
        K.shat = new int[P.k][]; int[][] ehat = new int[P.k][];
        for (int i = 0; i < P.k; i++) { K.shat[i] = ntt(cbd(P.eta1, r)); ehat[i] = ntt(cbd(P.eta1, r)); }
        K.that = new int[P.k][];
        for (int i = 0; i < P.k; i++) {
            int[] acc = new int[N];
            for (int j = 0; j < P.k; j++) acc = add(acc, mulNtt(K.Ahat[i][j], K.shat[j]));
            K.that[i] = add(acc, ehat[i]);
        }
        return K;
    }

    /** Encrypts and decrypts one message; returns the number of wrong bits and stores the largest noise in noise[0]. */
    static int roundTripMessage(Params P, Keys K, Random r, int[] noise, int du, int dv) {
        int[] m = new int[N];
        for (int i = 0; i < N; i++) m[i] = r.nextInt(2);
        int[][] rhat = new int[P.k][];
        for (int i = 0; i < P.k; i++) rhat[i] = ntt(cbd(P.eta1, r));
        int[][] u = new int[P.k][];
        for (int i = 0; i < P.k; i++) {
            int[] acc = new int[N];
            for (int j = 0; j < P.k; j++) acc = add(acc, mulNtt(K.Ahat[j][i], rhat[j])); // A transposed
            u[i] = roundTrip(add(invNtt(acc), cbd(P.eta2, r)), du);
        }
        int[] acc = new int[N];
        for (int j = 0; j < P.k; j++) acc = add(acc, mulNtt(K.that[j], rhat[j]));
        int[] mu = new int[N];
        for (int i = 0; i < N; i++) mu[i] = m[i] * ((Q + 1) / 2);
        int[] v = roundTrip(add(add(invNtt(acc), cbd(P.eta2, r)), mu), dv);
        // decryption
        int[] su = new int[N];
        for (int j = 0; j < P.k; j++) su = add(su, mulNtt(K.shat[j], ntt(u[j])));
        int[] w = sub(v, invNtt(su));
        int wrong = 0;
        for (int i = 0; i < N; i++) {
            int bit = compress(w[i], 1);
            if (bit != m[i]) wrong++;
            noise[0] = Math.max(noise[0], Math.abs(centre(mod(w[i] - mu[i]))));
        }
        return wrong;
    }

    // ---- learning with errors, small and plain -----------------------------------------------------------------------
    /** Solves A s = b (mod q) for square A by Gaussian elimination; returns null if A is singular. */
    static int[] gauss(int[][] A, int[] b) {
        int n = b.length;
        long[][] M = new long[n][n + 1];
        for (int i = 0; i < n; i++) { for (int j = 0; j < n; j++) M[i][j] = A[i][j]; M[i][n] = b[i]; }
        for (int c = 0; c < n; c++) {
            int p = c; while (p < n && M[p][c] == 0) p++;
            if (p == n) return null;
            long[] t = M[c]; M[c] = M[p]; M[p] = t;
            long inv = pow((int) M[c][c], Q - 2);
            for (int j = c; j <= n; j++) M[c][j] = M[c][j] * inv % Q;
            for (int i = 0; i < n; i++) if (i != c && M[i][c] != 0) {
                long f = M[i][c];
                for (int j = c; j <= n; j++) M[i][j] = mod(M[i][j] - f * M[c][j]);
            }
        }
        int[] s = new int[n];
        for (int i = 0; i < n; i++) s[i] = (int) M[i][n];
        return s;
    }

    public static void main(String[] args) {
        Random r = new Random(10);

        // ---- 1. with and without errors -------------------------------------------------------------------------------
        int n = 16, trials = 200, exact = 0, withErr = 0;
        double meanWrong = 0;
        for (int t = 0; t < trials; t++) {
            int[][] A = new int[n][n]; int[] s = new int[n], b0 = new int[n], b1 = new int[n];
            for (int i = 0; i < n; i++) { s[i] = mod(r.nextInt(5) - 2); for (int j = 0; j < n; j++) A[i][j] = r.nextInt(Q); }
            for (int i = 0; i < n; i++) {
                long x = 0; for (int j = 0; j < n; j++) x += (long) A[i][j] * s[j];
                b0[i] = mod(x); b1[i] = mod(x + r.nextInt(5) - 2);
            }
            int[] g0 = gauss(A, b0), g1 = gauss(A, b1);
            if (g0 != null && Arrays.equals(g0, s)) exact++;
            if (g1 != null && Arrays.equals(g1, s)) withErr++;
            if (g1 != null) { int w = 0; for (int i = 0; i < n; i++) if (g1[i] != s[i]) w++; meanWrong += (double) w / trials; }
        }
        check(exact == trials && withErr == 0, "exact equations give s, equations with errors do not");
        System.out.printf("lwe: %d equations in %d unknowns modulo %d, secret entries from -2 to 2, %d trials ; without errors Gaussian elimination recovers the secret %d times ; with errors from -2 to 2 added: %d times, and on average %.1f of the %d entries come out wrong%n",
                n, n, Q, trials, exact, withErr, meanWrong, n);

        // ---- 2. the NTT ----------------------------------------------------------------------------------------------------
        check(pow(ZETA, 128) == Q - 1 && pow(ZETA, 256) == 1, "17 is a primitive 256th root of unity modulo 3329");
        check((128 * 3303) % Q == 1, "3303 is the inverse of 128");
        int agree = 0, rt = 0;
        for (int t = 0; t < 50; t++) {
            int[] a = new int[N], b = new int[N];
            for (int i = 0; i < N; i++) { a[i] = r.nextInt(Q); b[i] = r.nextInt(Q); }
            if (Arrays.equals(invNtt(ntt(a)), a)) rt++;
            if (Arrays.equals(invNtt(mulNtt(ntt(a), ntt(b))), mulSlow(a, b))) agree++;
        }
        check(rt == 50 && agree == 50, "the NTT inverts and multiplies correctly");
        long slowOps = (long) N * N, fastOps = 3L * 7 * 128 + 128 * 5 + N; // 7 layers of 128 butterflies in two forward and one inverse transform, 5 per pair in the pointwise product, and the final scaling
        System.out.printf("ntt: 17^128 = %d = -1 and 17^256 = 1 modulo %d ; inverse of the transform restores 50 of 50 random polynomials ; product through the NTT equals schoolbook multiplication modulo X^256 + 1 in 50 of 50 ; multiplications: schoolbook %,d, through the NTT about %,d%n",
                pow(ZETA, 128), Q, slowOps, fastOps);

        // ---- 3. the three parameter sets --------------------------------------------------------------------------------
        Params[] sets = {new Params("ML-KEM-512", 2, 3, 2, 10, 4), new Params("ML-KEM-768", 3, 2, 2, 10, 4), new Params("ML-KEM-1024", 4, 2, 2, 11, 5)};
        int[][] published = {{800, 768, 1632}, {1184, 1088, 2400}, {1568, 1568, 3168}};
        StringJoiner pj = new StringJoiner(" ; ");
        for (int si = 0; si < sets.length; si++) {
            Params P = sets[si];
            int pk = 384 * P.k + 32, ct = 32 * (P.du * P.k + P.dv), sk = 768 * P.k + 96;
            check(pk == published[si][0] && ct == published[si][1] && sk == published[si][2], P.name + " sizes");
            int wrongBits = 0, msgs = 0, keys = 20, per = 50;
            int[] noise = {0};
            Random pr = new Random(100 + si);
            for (int kk = 0; kk < keys; kk++) {
                Keys K = keygen(P, pr);
                for (int t = 0; t < per; t++) { wrongBits += roundTripMessage(P, K, pr, noise, P.du, P.dv); msgs++; }
            }
            check(wrongBits == 0, P.name + " decrypts every message");
            pj.add(String.format("%s k %d, eta1 %d, eta2 %d, du %d, dv %d: public key 384k+32 = %,d bytes, ciphertext 32(du k + dv) = %,d bytes, secret key 768k+96 = %,d bytes (published: %,d, %,d, %,d) ; %,d messages under %d keys, %d wrong bits, largest noise %d against the margin %d",
                    P.name, P.k, P.eta1, P.eta2, P.du, P.dv, pk, ct, sk, published[si][0], published[si][1], published[si][2], msgs, keys, wrongBits, noise[0], Q / 4));
        }
        System.out.printf("params: n = 256, q = 3329 ; %s%n", pj);

        // ---- 4. too much noise --------------------------------------------------------------------------------------------
        StringJoiner nj = new StringJoiner(" ; ");
        Object[][] variants = {{"ML-KEM-768 as published", 2, 2, 10, 4}, {"eta1 = eta2 = 6", 6, 6, 10, 4}, {"eta1 = eta2 = 10", 10, 10, 10, 4}, {"du = 6, dv = 2", 2, 2, 6, 2}, {"du = 5, dv = 2", 2, 2, 5, 2}};
        int[] failsBy = new int[variants.length];
        for (int vi = 0; vi < variants.length; vi++) {
            Object[] v = variants[vi];
            Params P = new Params((String) v[0], 3, (int) v[1], (int) v[2], (int) v[3], (int) v[4]);
            Random vr = new Random(300 + vi);
            int wrong = 0, msgs = 0;
            int[] noise = {0};
            for (int kk = 0; kk < 5; kk++) {
                Keys K = keygen(P, vr);
                for (int t = 0; t < 20; t++) { wrong += roundTripMessage(P, K, vr, noise, P.du, P.dv); msgs++; }
            }
            failsBy[vi] = wrong;
            nj.add(String.format("%s: %d wrong bits in %,d, largest noise %d", v[0], wrong, msgs * N, noise[0]));
        }
        check(failsBy[0] == 0 && failsBy[2] > 0 && failsBy[4] > 0, "enough noise or rounding breaks decryption");
        System.out.printf("noise: k = 3, 100 messages of 256 bits each, a bit is read wrong when the noise passes q/4 = %d ; %s%n", Q / 4, nj);

        System.out.println("LatticeKem: " + passed + " checks passed");
    }
}
