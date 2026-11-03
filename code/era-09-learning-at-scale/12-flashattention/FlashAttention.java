import java.util.*;

/**
 * Era 9, topic 12: FlashAttention (Tri Dao, Daniel Y. Fu, Stefano Ermon, Atri Rudra and Christopher Re, 2022), with
 * the online softmax of Maxim Milakov and Natalia Gimelshein (2018).
 *
 * HOW IT WORKS
 *   Attention computes S = Q K^T / sqrt(d) (an N x N table of scores), P = softmax of each row of S, and O = P V.
 *   On a graphics processor the arithmetic is fast; moving numbers between the large, slow main memory (HBM) and the
 *   small, fast on-chip memory (SRAM) is not. Standard attention writes S and P to main memory and reads them back,
 *   about 4 N^2 numbers of traffic. FlashAttention never stores S or P. It cuts K and V into blocks of Bc rows and Q
 *   into blocks of Br rows, small enough to sit in SRAM together, and for each row keeps a running maximum m and a
 *   running sum l of exponentials. When a new block raises the maximum from m to m', everything accumulated so far
 *   is multiplied by exp(m - m'), so the result at the end is exactly softmax(S) V: the same numbers, computed in a
 *   different order.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The online softmax: one pass with a running maximum and sum gives the same weights as the usual two passes,
 *      and the naive softmax without a maximum overflows where the safe one does not.
 *   2. Standard attention and FlashAttention on random Q, K and V (N up to 1,024, d = 64): the outputs agree to the
 *      last few bits, while the program counts every number each method reads from and writes to main memory.
 *   3. The counts for longer sequences and other head sizes, against the paper's Theta(N d + N^2) and
 *      Theta(N^2 d^2 / M), and the extra memory each method needs.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java FlashAttention.java
 *   Expected output: expected-output.txt in this folder.
 */
public class FlashAttention {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** Main-memory traffic, in numbers read and written. */
    static long reads, writes;

    // ---- standard attention: S and P go out to main memory and come back ---------------------------------------------
    static double[][] standard(double[][] Q, double[][] K, double[][] V, boolean compute) {
        int N = Q.length, d = Q[0].length;
        double sc = 1 / Math.sqrt(d);
        double[][] S = compute ? new double[N][N] : null;
        // S = Q K^T: read Q and K, write S
        reads += 2L * N * d; writes += (long) N * N;
        if (compute) for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) { double s = 0; for (int k = 0; k < d; k++) s += Q[i][k] * K[j][k]; S[i][j] = s * sc; }
        // P = softmax(S): read S, write P
        reads += (long) N * N; writes += (long) N * N;
        if (compute) for (int i = 0; i < N; i++) {
            double m = Double.NEGATIVE_INFINITY, z = 0;
            for (int j = 0; j < N; j++) m = Math.max(m, S[i][j]);
            for (int j = 0; j < N; j++) { S[i][j] = Math.exp(S[i][j] - m); z += S[i][j]; }
            for (int j = 0; j < N; j++) S[i][j] /= z;
        }
        // O = P V: read P and V, write O
        reads += (long) N * N + (long) N * d; writes += (long) N * d;
        if (!compute) return null;
        double[][] O = new double[N][d];
        for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) { double p = S[i][j]; for (int k = 0; k < d; k++) O[i][k] += p * V[j][k]; }
        return O;
    }

    // ---- FlashAttention: tiles in fast memory, a running maximum and sum per row ------------------------------------------
    static int lastBc, lastBr;

    static double[][] flash(double[][] Q, double[][] K, double[][] V, int N, int d, long M, boolean compute) {
        int Bc = (int) Math.ceil(M / (4.0 * d)), Br = Math.min(Bc, d);
        Bc = Math.min(Bc, N); Br = Math.min(Br, N);
        lastBc = Bc; lastBr = Br;
        double sc = 1 / Math.sqrt(d);
        double[][] O = compute ? new double[N][d] : null;
        double[] l = compute ? new double[N] : null, m = compute ? new double[N] : null;
        if (compute) Arrays.fill(m, Double.NEGATIVE_INFINITY);
        writes += (long) N * d + 2L * N; // O, l and m initialised in main memory
        for (int j0 = 0; j0 < N; j0 += Bc) {
            int bc = Math.min(Bc, N - j0);
            reads += 2L * bc * d; // K_j and V_j into fast memory
            for (int i0 = 0; i0 < N; i0 += Br) {
                int br = Math.min(Br, N - i0);
                reads += 2L * br * d + 2L * br; // Q_i, O_i, l_i, m_i
                if (compute) for (int i = i0; i < i0 + br; i++) {
                    double[] s = new double[bc];
                    double mt = Double.NEGATIVE_INFINITY;
                    for (int j = 0; j < bc; j++) { double x = 0; for (int k = 0; k < d; k++) x += Q[i][k] * K[j0 + j][k]; s[j] = x * sc; mt = Math.max(mt, s[j]); }
                    double lt = 0;
                    for (int j = 0; j < bc; j++) { s[j] = Math.exp(s[j] - mt); lt += s[j]; }
                    double mNew = Math.max(m[i], mt);
                    double a = Math.exp(m[i] - mNew), b = Math.exp(mt - mNew); // a = 0 on the first block, where m[i] = -infinity
                    double lNew = a * l[i] + b * lt;
                    for (int k = 0; k < d; k++) {
                        double pv = 0; for (int j = 0; j < bc; j++) pv += s[j] * V[j0 + j][k];
                        O[i][k] = (l[i] * a * O[i][k] + b * pv) / lNew;
                    }
                    l[i] = lNew; m[i] = mNew;
                }
                writes += (long) br * d + 2L * br; // O_i, l_i, m_i back to main memory
            }
        }
        return O;
    }

    static double[][] rand(int n, int d, Random r) { double[][] a = new double[n][d]; for (double[] row : a) for (int k = 0; k < d; k++) row[k] = r.nextGaussian(); return a; }

    public static void main(String[] args) {
        Random r = new Random(12);

        // ---- 1. online softmax ---------------------------------------------------------------------------------------
        double[] x = new double[1000];
        for (int i = 0; i < x.length; i++) x[i] = 30 * r.nextGaussian();
        double m = Double.NEGATIVE_INFINITY, l = 0;
        for (double v : x) { double mn = Math.max(m, v); l = l * Math.exp(m - mn) + Math.exp(v - mn); m = mn; }
        double m2 = Arrays.stream(x).max().getAsDouble(), z2 = 0;
        for (double v : x) z2 += Math.exp(v - m2);
        double maxd = 0;
        for (double v : x) maxd = Math.max(maxd, Math.abs(Math.exp(v - m) / l - Math.exp(v - m2) / z2));
        double naive = 0;
        for (double v : x) naive += Math.exp(v);
        check(maxd < 1e-15 && m == m2, "one pass with a running maximum equals two passes");
        double[] big = {1000, 999, 998};
        double nz = 0; for (double v : big) nz += Math.exp(v);
        double safe = Math.exp(big[0] - 1000) / (Math.exp(0) + Math.exp(-1) + Math.exp(-2));
        check(Double.isInfinite(nz) && Math.abs(safe - 0.6652409557748219) < 1e-12, "the naive softmax overflows, the safe one does not");
        System.out.printf("online: 1,000 scores of spread 30 ; one pass with a running maximum and sum against two passes: largest difference %.1e ; scores 1000, 999, 998: sum of exp without the maximum = %s, with it the weights are %.4f, %.4f, %.4f%n",
                maxd, Double.isInfinite(nz) ? "infinity" : String.valueOf(nz), safe, safe * Math.exp(-1), safe * Math.exp(-2));

        // ---- 2. both methods, computed and counted ------------------------------------------------------------------------
        int d = 64;
        long M = 49_152; // one streaming multiprocessor's 192 KB of SRAM, in 4-byte numbers
        StringJoiner cj = new StringJoiner(" ; ");
        for (int N : new int[]{256, 1024}) {
            double[][] Q = rand(N, d, r), K = rand(N, d, r), V = rand(N, d, r);
            reads = writes = 0;
            double[][] Os = standard(Q, K, V, true);
            long ts = reads + writes;
            reads = writes = 0;
            double[][] Of = flash(Q, K, V, N, d, M, true);
            long tf = reads + writes;
            double diff = 0, mag = 0;
            for (int i = 0; i < N; i++) for (int k = 0; k < d; k++) { diff = Math.max(diff, Math.abs(Os[i][k] - Of[i][k])); mag = Math.max(mag, Math.abs(Os[i][k])); }
            check(diff < 1e-12 * Math.max(1, mag), "FlashAttention gives the same output");
            check(tf < ts, "FlashAttention moves fewer numbers");
            cj.add(String.format("N %,d: blocks Bc %d, Br %d ; largest difference in O %.1e ; main-memory traffic standard %,d, FlashAttention %,d (%.1f times less)", N, lastBc, lastBr, diff, ts, tf, (double) ts / tf));
        }
        System.out.printf("exact: d %d, fast memory M = %,d numbers (192 KB of 4-byte numbers), random Q, K, V ; %s%n", d, M, cj);

        // ---- 3. counts for longer sequences and other head sizes ------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        for (int N : new int[]{1024, 4096, 16384, 65536}) {
            long ts = 4L * N * N + 4L * N * d; // the same terms standard() adds up: 2Nd + N^2, N^2 + N^2, N^2 + Nd + Nd
            reads = writes = 0; flash(null, null, null, N, d, M, false);
            long tf = reads + writes;
            double formula = 12.0 * N * N * d * d / M; // leading term of the count above, (3 N d) per block of K and V, N / Bc = 4 N d / M blocks
            if (N >= 4096) check(Math.abs(tf / formula - 1) < 0.15, "for long sequences the count follows 12 N^2 d^2 / M");
            sj.add(String.format("N %,d: standard %,d, FlashAttention %,d (12 N^2 d^2 / M = %,.0f), ratio %.1f ; extra memory: standard %,d numbers for S and P, FlashAttention %,d for m and l", N, ts, tf, formula, (double) ts / tf, 2L * N * N, 2L * N));
        }
        StringJoiner dj = new StringJoiner(" ; ");
        for (int dd : new int[]{32, 64, 128}) {
            int N = 16384;
            reads = writes = 0; flash(null, null, null, N, dd, M, false);
            long tf = reads + writes, ts = 4L * N * N + 4L * N * dd;
            dj.add(String.format("d %d: ratio %.1f", dd, (double) ts / tf));
        }
        System.out.printf("traffic: d %d, M %,d, counted by running FlashAttention's loops without arithmetic ; %s ; at N = 16,384 by head size: %s%n", d, M, sj, dj);

        System.out.println("FlashAttention: " + passed + " checks passed");
    }
}
