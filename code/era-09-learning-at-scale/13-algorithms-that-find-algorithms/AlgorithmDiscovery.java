import java.util.*;

/**
 * Era 9, topic 13: Algorithms that find algorithms (AlphaTensor, DeepMind, 2022; flip graphs, Manuel Kauers and
 * Jakob Moosbauer, Linz, 2022; AlphaEvolve, Google DeepMind, 2025).
 *
 * HOW IT WORKS
 *   Multiplying an n x n matrix A by B is described by one fixed three-dimensional table of zeros and ones, the
 *   matrix multiplication tensor T: T[(i,j), (j,k), (k,i)] = 1 for all i, j, k, and 0 elsewhere. An algorithm that
 *   uses R multiplications is the same thing as writing T as a sum of R pieces u (x) v (x) w, each the product of
 *   three vectors: the r-th multiplication is (sum of u_r-weighted entries of A) times (sum of v_r-weighted entries
 *   of B), and w_r says to which entries of the product it is added. The schoolbook method is n^3 pieces; Strassen's
 *   2 x 2 method is 7. Finding algorithms is finding short decompositions.
 *   AlphaTensor searched for them with reinforcement learning, as a game. Kauers and Moosbauer walk instead on a
 *   "flip graph": two pieces that share a factor, a (x) b (x) c + a (x) b' (x) c', can be rewritten as
 *   a (x) (b + b') (x) c + a (x) b' (x) (c' - c) without changing the sum (a flip); when two pieces come to share two
 *   factors they merge into one, and the algorithm has one multiplication fewer (a reduction).
 *   Whatever finds an algorithm, checking it is easy: add up the pieces and compare with T.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Builds T for 2 x 2, 3 x 3 and 4 x 4 and checks the schoolbook method, Strassen's 7, and Strassen applied
 *      twice to 4 x 4 (49 multiplications), all with arithmetic modulo 2.
 *   2. Checks AlphaTensor's published 47-multiplication algorithm for 4 x 4 matrices modulo 2 (embedded below, from
 *      DeepMind's alphatensor repository, file algorithms/factorizations_f2.npz, key "4,4,4", CC BY 4.0) against T,
 *      and by multiplying random 0/1 matrices.
 *   3. Random walks on the flip graph, starting from the schoolbook method: 2 x 2 down to 7, 3 x 3 down to 23
 *      (Laderman's 1976 record), and 4 x 4 for a fixed number of flips.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AlgorithmDiscovery.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AlgorithmDiscovery {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // AlphaTensor's 47-term factorization of the 4 x 4 multiplication tensor modulo 2: for each of the 47 terms, the
    // 16 entries of u, v and w (entry index i*4 + j), as published by Google DeepMind under CC BY 4.0.
    static final String AT_U =
            "0010000000000000 0010011000000000 0010101000000000 0010001000000000 1000000000000000 1000000010000000 " +
            "1000000010100000 1110011011000000 0100000000001100 0100000000000110 0100000000000100 1110101000001100 " +
            "1110000010100110 0000000000001000 0001000000001001 0001000000000001 1000000011000000 0001000001011001 " +
            "0001000001010000 0001000000010000 0000010000000000 0001010100000000 0001000000000011 0001101000000011 " +
            "0001010000010010 0000000000100000 0001000100000000 0001100100000000 0001000001010110 0001010100000011 " +
            "0001000000000000 0001000000110000 0000100010001000 0001010100001100 0000000100010001 0001011000110000 " +
            "0000001000100010 0000010001000100 0100000000000000 0001100100110000 0000000000000010 0000100000000000 " +
            "0001100111000000 0001000101001000 0000000001000000 0001100000100001 0001000010101001";
    static final String AT_V =
            "0000000010000000 0000100100010000 1010000000100000 1010100110110000 1000000000000000 1101100111000000 " +
            "0100000011000000 0000100100000000 1010001000000000 0000010011000000 1010111011000000 1010000000000000 " +
            "0000000011000000 0110001000001100 0100000000001100 0100000000101110 0001100100000000 0000000000001100 " +
            "0000010000001100 0000010000011101 0000001100011010 0000001000001010 0000000000101010 0000000000100000 " +
            "0000010000011010 0100000001011001 0001001000001011 0001000000001001 0000010000000000 0000000000001010 " +
            "0000000000001000 0000000000011001 0111000000000000 0000001000000000 0000000000000111 0000000000010000 " +
            "0000000001110000 0000011100000000 0000100000000000 0000000000001001 0000010001101010 0011000000101001 " +
            "0001000000000000 0001001000001100 0001010100001100 0100000000101001 0100000000000000";
    static final String AT_W =
            "1100100000000000 0100000000001000 0100000010000000 0100000000000000 1010000010000000 0010000000000000 " +
            "0010100000000000 0000000000001000 0001000010000000 0001100000000000 0001000000000000 0000000010000000 " +
            "0000100000000000 0001000000110000 0001101100110000 0001010100110000 0010000000001000 0000101100100001 " +
            "0010101100000011 0010011000000011 0100000000000101 0100000011010101 0001010111010000 0000010011000000 " +
            "0000010000000001 0010011000000000 0100000001100101 0100000001101110 0000100100000001 0000010011010001 " +
            "1111101111011110 0010011000001110 0000000000100000 0000000010010001 0000010000100001 0000010000001100 " +
            "0000010000000000 0000000000000001 1001000000001000 0000010000101110 0001010100000000 0100000001100000 " +
            "0000000000101010 0000000000100001 0010000000000011 0000010000100000 0000101000100000";

    /** A term is three bit masks: which entries of A, of B and of C (entry index k*n + i for C[i][k]) it uses. */
    static List<int[]> parseAT() {
        String[] u = AT_U.trim().split(" "), v = AT_V.trim().split(" "), w = AT_W.trim().split(" ");
        List<int[]> L = new ArrayList<>();
        for (int r = 0; r < u.length; r++) L.add(new int[]{mask(u[r]), mask(v[r]), mask(w[r])});
        return L;
    }

    static int mask(String bits) { int m = 0; for (int i = 0; i < bits.length(); i++) if (bits.charAt(i) == '1') m |= 1 << i; return m; }

    static List<int[]> schoolbook(int n) {
        List<int[]> L = new ArrayList<>();
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) for (int k = 0; k < n; k++) L.add(new int[]{1 << (i * n + j), 1 << (j * n + k), 1 << (k * n + i)});
        return L;
    }

    /** Strassen's 7 products, signs dropped (arithmetic modulo 2). A, B entries i*2 + j; C entry (i, k) at k*2 + i. */
    static List<int[]> strassen() {
        int[][] t = {
                {0b1001, 0b1001, 0b1001},  // M1 = (A11 + A22)(B11 + B22) -> C11, C22
                {0b1100, 0b0001, 0b1010},  // M2 = (A21 + A22) B11        -> C21, C22
                {0b0001, 0b1010, 0b1100},  // M3 = A11 (B12 - B22)        -> C12, C22
                {0b1000, 0b0101, 0b0011},  // M4 = A22 (B21 - B11)        -> C11, C21
                {0b0011, 0b1000, 0b0101},  // M5 = (A11 + A12) B22        -> C11, C12
                {0b0101, 0b0011, 0b1000},  // M6 = (A21 - A11)(B11 + B12) -> C22
                {0b1010, 0b1100, 0b0001}}; // M7 = (A12 - A22)(B21 + B22) -> C11
        List<int[]> L = new ArrayList<>();
        for (int[] x : t) L.add(x.clone());
        return L;
    }

    /** Applies an n1 scheme to blocks and an n2 scheme inside them: a scheme for n1*n2 with R1*R2 terms. */
    static List<int[]> compose(List<int[]> S1, int n1, List<int[]> S2, int n2) {
        int n = n1 * n2;
        List<int[]> L = new ArrayList<>();
        for (int[] x : S1) for (int[] y : S2) {
            int[] z = new int[3];
            for (int f = 0; f < 3; f++) {
                for (int p = 0; p < n1 * n1; p++) if ((x[f] >> p & 1) == 1)
                    for (int q = 0; q < n2 * n2; q++) if ((y[f] >> q & 1) == 1) {
                        // decode both to (row, col), compose, encode; C masks store (row, col) as col*n + row
                        int r1 = f == 2 ? p % n1 : p / n1, c1 = f == 2 ? p / n1 : p % n1;
                        int r2 = f == 2 ? q % n2 : q / n2, c2 = f == 2 ? q / n2 : q % n2;
                        int row = r1 * n2 + r2, col = c1 * n2 + c2;
                        z[f] |= 1 << (f == 2 ? col * n + row : row * n + col);
                    }
            }
            L.add(z);
        }
        return L;
    }

    /** Adds up the pieces modulo 2 and compares with the multiplication tensor. */
    static boolean isMultiplication(List<int[]> S, int n) {
        int m = n * n;
        boolean[][][] t = new boolean[m][m][m];
        for (int[] x : S) for (int a = 0; a < m; a++) if ((x[0] >> a & 1) == 1) for (int b = 0; b < m; b++) if ((x[1] >> b & 1) == 1)
            for (int c = 0; c < m; c++) if ((x[2] >> c & 1) == 1) t[a][b][c] ^= true;
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) for (int k = 0; k < n; k++) t[i * n + j][j * n + k][k * n + i] ^= true;
        for (boolean[][] p : t) for (boolean[] q : p) for (boolean z : q) if (z) return false;
        return true;
    }

    /** Runs the scheme as an algorithm on 0/1 matrices modulo 2, and compares with the schoolbook product. */
    static boolean multipliesCorrectly(List<int[]> S, int n, int trials, Random r) {
        for (int t = 0; t < trials; t++) {
            int A = r.nextInt(1 << (n * n)), B = r.nextInt(1 << (n * n)), C = 0, want = 0;
            for (int[] x : S) {
                int m = Integer.bitCount(A & x[0]) & Integer.bitCount(B & x[1]) & 1; // one multiplication, modulo 2
                if (m == 1) C ^= x[2];
            }
            for (int i = 0; i < n; i++) for (int k = 0; k < n; k++) {
                int s = 0;
                for (int j = 0; j < n; j++) s ^= (A >> (i * n + j) & 1) & (B >> (j * n + k) & 1);
                if (s == 1) want |= 1 << (k * n + i);
            }
            if (C != want) return false;
        }
        return true;
    }

    // ---- the flip graph -------------------------------------------------------------------------------------------------
    /**
     * Removes pieces with a zero factor and merges pieces that share two factors, looking only at pieces that have
     * changed (a merge changes the surviving piece, which is then looked at in turn); returns how many merges.
     */
    static int reduce(List<int[]> S, Deque<int[]> touched) {
        int merges = 0;
        while (!touched.isEmpty()) {
            int[] x = touched.pop();
            int ix = indexOf(S, x);
            if (ix < 0) continue;
            if (x[0] == 0 || x[1] == 0 || x[2] == 0) { S.remove(ix); continue; }
            for (int j = 0; j < S.size(); j++) {
                int[] y = S.get(j);
                if (y == x) continue;
                boolean done = false;
                for (int p = 0; p < 3; p++) {
                    int q = (p + 1) % 3, s = (p + 2) % 3;
                    if (x[q] == y[q] && x[s] == y[s]) { y[p] ^= x[p]; S.remove(indexOf(S, x)); merges++; touched.push(y); done = true; break; }
                }
                if (done) break;
            }
        }
        return merges;
    }

    static int indexOf(List<int[]> S, int[] x) { for (int i = 0; i < S.size(); i++) if (S.get(i) == x) return i; return -1; }

    static List<int[]> copy(List<int[]> S) { List<int[]> c = new ArrayList<>(); for (int[] x : S) c.add(x.clone()); return c; }

    static long[] trace; // rank after each reduction, as (flips, rank) pairs

    /** Walks from start until the rank reaches target or the flips run out; restarts after `patience` flips without a reduction. */
    static List<int[]> walk(List<int[]> start, int target, long maxFlips, long patience, Random r, long[] flipsUsed, List<long[]> log) {
        List<int[]> S = copy(start), best = copy(start);
        long flips = 0, since = 0;
        int[] js = new int[start.size()];
        long tries = 0;
        while (best.size() > target && flips < maxFlips && tries++ < 1000 * maxFlips) { // the cap on tries stops a scheme with no possible flip
            int i = r.nextInt(S.size()), p = r.nextInt(3);
            int[] x = S.get(i);
            int cnt = 0;
            for (int j = 0; j < S.size(); j++) if (j != i && S.get(j)[p] == x[p]) js[cnt++] = j;
            if (cnt == 0) continue;
            int[] y = S.get(js[r.nextInt(cnt)]);
            int q = (p + 1) % 3, s = (p + 2) % 3;
            if (r.nextBoolean()) { int t = q; q = s; s = t; }
            // the flip: x = a(x)b(x)c, y = a(x)b'(x)c'  ->  a(x)(b+b')(x)c + a(x)b'(x)(c'+c), modulo 2
            x[q] ^= y[q]; y[s] ^= x[s];
            flips++; since++;
            Deque<int[]> touched = new ArrayDeque<>();
            touched.push(x); touched.push(y);
            if (reduce(S, touched) > 0) {
                since = 0;
                if (S.size() < best.size()) { best = copy(S); if (log != null) log.add(new long[]{flips, S.size()}); }
            }
            if (since > patience) { S = copy(start); since = 0; }
        }
        flipsUsed[0] = flips;
        return best;
    }

    static String describe(int mask, String M, int n, boolean transposed) {
        StringJoiner j = new StringJoiner(" + ");
        for (int b = 0; b < n * n; b++) if ((mask >> b & 1) == 1) {
            int row = transposed ? b % n : b / n, col = transposed ? b / n : b % n;
            j.add(M + (row + 1) + (col + 1));
        }
        return j.toString();
    }

    public static void main(String[] args) {
        Random r = new Random(13);

        // ---- 1. the classical schemes ------------------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        for (int n = 2; n <= 4; n++) {
            List<int[]> sb = schoolbook(n);
            check(isMultiplication(sb, n) && multipliesCorrectly(sb, n, 500, r), "schoolbook " + n);
            cj.add(String.format("schoolbook %dx%d: %d multiplications, correct", n, n, sb.size()));
        }
        List<int[]> st = strassen();
        check(isMultiplication(st, 2) && multipliesCorrectly(st, 2, 500, r), "Strassen");
        List<int[]> st2 = compose(st, 2, st, 2);
        check(st2.size() == 49 && isMultiplication(st2, 4) && multipliesCorrectly(st2, 4, 2000, r), "Strassen twice");
        cj.add("Strassen 2x2: 7, correct ; Strassen applied twice, 4x4: 49, correct");
        System.out.printf("classical: modulo 2, each checked against the tensor and on random 0/1 matrices ; %s%n", cj);

        // ---- 2. AlphaTensor's 47 --------------------------------------------------------------------------------------------
        List<int[]> at = parseAT();
        check(at.size() == 47, "47 terms");
        check(isMultiplication(at, 4), "AlphaTensor's factors add up to the 4x4 multiplication tensor modulo 2");
        check(multipliesCorrectly(at, 4, 10_000, r), "and multiply 10,000 random 0/1 matrices correctly");
        check(!isMultiplication(at.subList(0, 46), 4), "dropping a term breaks it");
        int ones = 0;
        for (int[] x : at) ones += Integer.bitCount(x[0]) + Integer.bitCount(x[1]) + Integer.bitCount(x[2]);
        int onesSt = 0;
        for (int[] x : st2) onesSt += Integer.bitCount(x[0]) + Integer.bitCount(x[1]) + Integer.bitCount(x[2]);
        int[] firstTerm = at.get(0);
        System.out.printf("alphatensor: 47 terms read from factorizations_f2.npz (key 4,4,4) ; their sum modulo 2 equals the 4x4 multiplication tensor ; 10,000 random 0/1 matrix pairs multiplied correctly ; with its last term left out it is no longer correct ; nonzero coefficients: AlphaTensor %d, Strassen twice %d ; first multiplication: (%s) x (%s)%n",
                ones, onesSt, describe(firstTerm[0], "A", 4, false), describe(firstTerm[1], "B", 4, false));

        // ---- 3. flip graphs ------------------------------------------------------------------------------------------------
        long[] used = new long[1];
        StringJoiner f2 = new StringJoiner(", ");
        List<int[]> two = null;
        long sum2 = 0;
        for (int s = 0; s < 10; s++) {
            List<int[]> res = walk(schoolbook(2), 7, 1_000_000, 100_000, new Random(100 + s), used, null);
            check(res.size() == 7 && isMultiplication(res, 2), "2x2 reaches 7");
            f2.add(String.valueOf(used[0]));
            sum2 += used[0];
            if (two == null) two = res;
        }
        StringJoiner tj = new StringJoiner(" ; ");
        for (int[] x : two) tj.add(String.format("(%s)(%s) -> %s", describe(x[0], "A", 2, false), describe(x[1], "B", 2, false), describe(x[2], "C", 2, true)));
        System.out.printf("flip2: 2x2 from the schoolbook 8, 10 walks, each reached 7 ; flips needed: %s ; the first walk's algorithm: %s%n", f2, tj);

        StringJoiner f3 = new StringJoiner(", ");
        int reached = 0;
        List<long[]> log3 = new ArrayList<>();
        for (int s = 0; s < 10; s++) {
            List<int[]> res = walk(schoolbook(3), 23, 3_000_000, 2_000_000, new Random(200 + s), used, s == 0 ? log3 : null);
            check(isMultiplication(res, 3), "every 3x3 scheme found is correct");
            if (res.size() == 23) reached++;
            f3.add(res.size() == 23 ? String.valueOf(used[0]) : "not within 3,000,000 (rank " + res.size() + ")");
        }
        check(reached >= 8, "most 3x3 walks reach Laderman's 23");
        StringJoiner lj = new StringJoiner(" ");
        for (long[] e : log3) lj.add(e[0] + ":" + e[1]);
        System.out.printf("flip3: 3x3 from the schoolbook 27, 10 walks of up to 3,000,000 flips ; reached 23 (Laderman's 1976 record): %d of 10 ; flips needed: %s ; the first walk, flips:rank at each new low: 0:27 %s%n", reached, f3, lj);

        List<long[]> log4 = new ArrayList<>();
        List<int[]> res4 = walk(schoolbook(4), 47, 6_000_000, 3_000_000, new Random(300), used, log4);
        check(isMultiplication(res4, 4) && multipliesCorrectly(res4, 4, 2000, r), "the 4x4 scheme found is correct");
        StringJoiner l4 = new StringJoiner(" ");
        for (long[] e : log4) l4.add(e[0] + ":" + e[1]);
        System.out.printf("flip4: 4x4 from the schoolbook 64, one walk of %,d flips ; lowest rank reached %d (Strassen twice: 49, AlphaTensor and Kauers and Moosbauer: 47) ; flips:rank at each new low: 0:64 %s%n", used[0], res4.size(), l4);

        System.out.println("AlgorithmDiscovery: " + passed + " checks passed");
    }
}
