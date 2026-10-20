import java.util.*;

/**
 * Era 7, topic 9: Karp-Rabin fingerprints (Richard Karp and Michael Rabin, IBM Journal of Research and Development,
 * March 1987; presented December 1985).
 *
 * HOW IT WORKS
 *   To find a pattern of m letters in a text of n letters, the obvious method compares the pattern with every
 *   window of the text, letter by letter. Karp and Rabin compare short fingerprints instead. Read the pattern as one
 *   big number (here, 2 bits per letter of the alphabet A, C, G, T) and keep only its remainder modulo a prime p.
 *   The fingerprint of the next window comes from the last one in a few arithmetic steps: drop the first letter, shift,
 *   add the new letter ("rolling"). Only where fingerprints agree are letters compared. Two different windows can
 *   share a fingerprint only if p divides their difference, and a number below 2^64 has at most 15 prime factors, so
 *   if p is chosen at random among many primes, after the text is fixed, false alarms are rare whatever the text.
 *   A fixed, publicly known p is not safe: someone who knows it can write a text full of false alarms.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Searches a 1,000,000-letter text for patterns: letter comparisons of the obvious method and of fingerprints.
 *   2. False alarms for random primes of different sizes, against the bound from counting prime factors.
 *   3. An adversary who knows a fixed prime, against a prime chosen at random afterwards.
 *   4. One pass for 1,000 patterns at once, against 1,000 separate searches.
 *   5. A 16 x 16 block in a 1,000 x 1,000 grid of letters: the same idea in two dimensions.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java KarpRabin.java
 *   Expected output: expected-output.txt in this folder.
 */
public class KarpRabin {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1987L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed >>> 1;
    }

    static int below(int k) { return (int) ((next() >>> 20) % k); }

    static byte[] randomText(int n) {
        byte[] t = new byte[n];
        for (int i = 0; i < n; i++) t[i] = (byte) below(4);
        return t;
    }

    static boolean isPrime(long x) {
        if (x < 2) return false;
        for (long d = 2; d * d <= x; d++) if (x % d == 0) return false;
        return true;
    }

    /** A prime chosen uniformly at random from the primes up to T. */
    static long randomPrime(long T) {
        while (true) { long x = 2 + (next() >>> 20) % (T - 1); if (isPrime(x)) return x; }
    }

    static long comparisons;

    /** The obvious method: compare letter by letter at every position; returns the number of matches. */
    static int naive(byte[] t, byte[] pat) {
        int count = 0, m = pat.length;
        for (int i = 0; i + m <= t.length; i++) {
            int j = 0;
            while (j < m) { comparisons++; if (t[i + j] != pat[j]) break; j++; }
            if (j == m) count++;
        }
        return count;
    }

    static long falseAlarms, hashSteps;

    /** Karp-Rabin with modulus p, base 4: returns the number of true matches; counts false alarms and comparisons. */
    static int karpRabin(byte[] t, byte[] pat, long p) {
        int m = pat.length, count = 0;
        long hp = 0, ht = 0, top = 1;                                   // top = 4^(m-1) mod p
        for (int j = 0; j < m; j++) { hp = (hp * 4 + pat[j]) % p; ht = (ht * 4 + t[j]) % p; if (j > 0) top = top * 4 % p; }
        for (int i = 0; i + m <= t.length; i++) {
            if (i > 0) {                                                 // roll: drop t[i-1], bring in t[i+m-1]
                ht = (ht + p - t[i - 1] * top % p) % p;
                ht = (ht * 4 + t[i + m - 1]) % p;
            }
            hashSteps++;
            if (ht == hp) {
                int j = 0;
                while (j < m) { comparisons++; if (t[i + j] != pat[j]) break; j++; }
                if (j == m) count++; else falseAlarms++;
            }
        }
        return count;
    }

    public static void main(String[] args) {
        int n = 1_000_000, m = 32;
        byte[] text = randomText(n);

        // ---- 1. one pattern -------------------------------------------------------------------------------------------
        byte[] present = Arrays.copyOfRange(text, 400_000, 400_000 + m);
        long p = randomPrime(1L << 31);
        comparisons = 0;
        int a = naive(text, present);
        long naiveComp = comparisons;
        comparisons = 0; falseAlarms = 0; hashSteps = 0;
        int b = karpRabin(text, present, p);
        check(a == b && a >= 1, "both find the same matches");
        long krComp1 = comparisons, krFalse1 = falseAlarms, krSteps1 = hashSteps;
        // the obvious method's worst case: a text of all A's, and a pattern of A's ending in C
        byte[] allA = new byte[n], aaac = new byte[m];
        aaac[m - 1] = 1;
        comparisons = 0;
        naive(allA, aaac);
        long worstNaive = comparisons;
        comparisons = 0; falseAlarms = 0; hashSteps = 0;
        karpRabin(allA, aaac, p);
        check(worstNaive == (long) (n - m + 1) * m, "the obvious method compares all m letters at every position");
        check(comparisons == 0, "the fingerprints never agree, so no letters are compared");
        System.out.printf("search: a text of %,d random letters A, C, G, T, a pattern of %d letters copied from position 400,000 ; the obvious method: %,d letter comparisons ; fingerprints modulo a random prime p = %,d: %,d rolling steps, %,d letter comparisons, %,d false alarm%s ; %d match%s ; on a text of %,d A's and the pattern AAA...AC, the obvious method makes %,d comparisons (m at every position), the fingerprints %,d rolling steps and %,d comparisons%n",
                n, m, naiveComp, p, krSteps1, krComp1, krFalse1, krFalse1 == 1 ? "" : "s", a, a == 1 ? "" : "es", n, worstNaive, hashSteps, comparisons);

        // ---- 2. false alarms against the size of the prime ------------------------------------------------------------
        int sieveMax = 1 << 22;
        boolean[] comp = new boolean[sieveMax + 1];
        int[] pi = new int[sieveMax + 1];
        for (int i = 2; i <= sieveMax; i++) {
            if (!comp[i] && (long) i * i <= sieveMax) for (int j = i * i; j <= sieveMax; j += i) comp[j] = true;
            pi[i] = pi[i - 1] + (comp[i] ? 0 : 1);
        }
        byte[] absent = randomText(m);
        StringJoiner fj = new StringJoiner(" ; ");
        for (int bits : new int[]{10, 14, 18, 22}) {
            long T = 1L << bits;
            int primes = 20;
            long totalFalse = 0;
            for (int r = 0; r < primes; r++) {
                falseAlarms = 0;
                int found = karpRabin(text, absent, randomPrime(T));
                check(found == naiveCount(text, absent), "false alarms never become false matches");
                totalFalse += falseAlarms;
            }
            double avg = (double) totalFalse / primes;
            // a window that differs from the pattern gives a nonzero difference below 2^64, with at most 15 prime factors
            double bound = (double) (n - m + 1) * 15 / pi[(int) T];
            check(avg <= bound, "the measured false alarms stay under the prime-counting bound");
            fj.add(String.format("primes up to 2^%d (%,d of them): %,.1f false alarms on average, bound %,.0f", bits, pi[(int) T], avg, bound));
        }
        System.out.printf("falsealarms: the same text and a %d-letter pattern that does not occur, 20 random primes of each size ; %s ; the bound: positions x 15 / (number of primes), since a nonzero number below 2^64 has at most 15 prime factors%n", m, fj);

        // ---- 3. an adversary who knows the prime ---------------------------------------------------------------------
        long fixed = 101;
        long target = fingerprint(present, fixed);
        int blocks = 20_000;
        byte[] evil = new byte[blocks * m];
        // each block copies the pattern except its last 4 letters, which are changed so the number they spell moves
        // by a multiple of 101: the fingerprint modulo 101 is unchanged, and checking costs 29 or more comparisons
        int tail = 0;
        for (int j = m - 4; j < m; j++) tail = tail * 4 + present[j];
        List<Integer> tails = new ArrayList<>();
        for (int v = 0; v < 256; v++) if (v != tail && (v - tail) % 101 == 0) tails.add(v);
        check(!tails.isEmpty(), "there is another 4-letter ending with the same remainder");
        for (int k = 0; k < blocks; k++) {
            byte[] w = present.clone();
            int v = tails.get(k % tails.size());
            for (int j = m - 1; j >= m - 4; j--) { w[j] = (byte) (v & 3); v >>= 2; }
            check(fingerprint(w, fixed) == target && !Arrays.equals(w, present), "a planted block");
            System.arraycopy(w, 0, evil, k * m, m);
        }
        comparisons = 0; falseAlarms = 0;
        karpRabin(evil, present, fixed);
        long fixedFalse = falseAlarms, fixedComp = comparisons;
        comparisons = 0; falseAlarms = 0;
        long chosen = randomPrime(1L << 31);
        karpRabin(evil, present, chosen);
        check(fixedFalse >= blocks, "every planted block is a false alarm for the known prime");
        check(falseAlarms * 100 < fixedFalse, "a prime chosen afterwards is not fooled");
        System.out.printf("adversary: a text of %,d letters built from %,d blocks, each the pattern with its last 4 letters changed so that the fingerprint modulo 101 stays the same ; searching with p = 101: %,d false alarms, %,d letter comparisons ; with a prime chosen at random afterwards (p = %,d): %,d false alarms, %,d letter comparisons%n",
                evil.length, blocks, fixedFalse, fixedComp, chosen, falseAlarms, comparisons);

        // ---- 4. many patterns at once ---------------------------------------------------------------------------------
        int k = 1000;
        byte[][] pats = new byte[k][];
        for (int i = 0; i < k; i++) pats[i] = i % 2 == 0 ? Arrays.copyOfRange(text, 1000 * i + 7, 1000 * i + 7 + m) : randomText(m);
        long P = randomPrime(1L << 31);
        Map<Long, List<Integer>> byPrint = new HashMap<>();
        for (int i = 0; i < k; i++) byPrint.computeIfAbsent(fingerprint(pats[i], P), z -> new ArrayList<>()).add(i);
        int[] hits = new int[k];
        comparisons = 0; hashSteps = 0;
        long top = 1, h = 0;
        for (int j = 0; j < m; j++) { h = (h * 4 + text[j]) % P; if (j > 0) top = top * 4 % P; }
        for (int i = 0; i + m <= n; i++) {
            if (i > 0) { h = (h + P - text[i - 1] * top % P) % P; h = (h * 4 + text[i + m - 1]) % P; }
            hashSteps++;
            List<Integer> cand = byPrint.get(h);
            if (cand == null) continue;
            for (int c : cand) {
                int j = 0;
                while (j < m) { comparisons++; if (text[i + j] != pats[c][j]) break; j++; }
                if (j == m) hits[c]++;
            }
        }
        long krComp = comparisons;
        comparisons = 0;
        int agree = 0;
        for (int i = 0; i < k; i++) if (naive(text, pats[i]) == hits[i]) agree++;
        check(agree == k, "the one-pass search agrees with 1,000 separate searches");
        int foundPats = 0;
        for (int x : hits) if (x > 0) foundPats++;
        System.out.printf("many: %,d patterns of %d letters, half copied from the text ; one pass with all their fingerprints in a hash table: %,d rolling steps and %,d letter comparisons, %d patterns found ; %,d separate searches by the obvious method: %,d letter comparisons%n",
                k, m, hashSteps, krComp, foundPats, k, comparisons);

        // ---- 5. two dimensions ---------------------------------------------------------------------------------------
        int N = 1000, M = 16;
        byte[][] grid = new byte[N][];
        for (int r = 0; r < N; r++) grid[r] = randomText(N);
        int pr = 613, pc = 271;
        byte[][] block = new byte[M][];
        for (int r = 0; r < M; r++) block[r] = Arrays.copyOfRange(grid[pr + r], pc, pc + M);
        long Q = randomPrime(1L << 31);
        // fingerprint each column strip of height M, rolling down; then roll the strips' prints across each row
        long powCol = 1, powRow = 1;                    // 4^(M-1) for columns, B^(M-1) across, B = 4^M mod Q
        long B = 1;
        for (int i = 0; i < M; i++) B = B * 4 % Q;
        for (int i = 1; i < M; i++) { powCol = powCol * 4 % Q; powRow = powRow * B % Q; }
        long target2 = 0;
        for (int c = 0; c < M; c++) { long col = 0; for (int r = 0; r < M; r++) col = (col * 4 + block[r][c]) % Q; target2 = (target2 * B + col) % Q; }
        long[] col = new long[N];
        for (int c = 0; c < N; c++) for (int r = 0; r < M; r++) col[c] = (col[c] * 4 + grid[r][c]) % Q;
        long steps2 = 0, verify2 = 0;
        List<int[]> found2 = new ArrayList<>();
        for (int r = 0; r + M <= N; r++) {
            if (r > 0) for (int c = 0; c < N; c++) { col[c] = (col[c] + Q - grid[r - 1][c] * powCol % Q) % Q; col[c] = (col[c] * 4 + grid[r + M - 1][c]) % Q; steps2++; }
            long row = 0;
            for (int c = 0; c < M; c++) row = (row * B + col[c]) % Q;
            for (int c = 0; c + M <= N; c++) {
                if (c > 0) { row = (row + Q - col[c - 1] * powRow % Q) % Q; row = (row * B + col[c + M - 1]) % Q; }
                steps2++;
                if (row == target2) {
                    verify2++;
                    boolean same = true;
                    for (int i = 0; i < M && same; i++) for (int j = 0; j < M && same; j++) same = grid[r + i][c + j] == block[i][j];
                    if (same) found2.add(new int[]{r, c});
                }
            }
        }
        long naive2 = 0;
        int naiveFound = 0;
        for (int r = 0; r + M <= N; r++) for (int c = 0; c + M <= N; c++) {
            boolean same = true;
            for (int i = 0; i < M && same; i++) for (int j = 0; j < M && same; j++) { naive2++; same = grid[r + i][c + j] == block[i][j]; }
            if (same) naiveFound++;
        }
        check(found2.size() == naiveFound && found2.get(0)[0] == pr && found2.get(0)[1] == pc, "the block is found where it was copied from");
        System.out.printf("grid: a %,d x %,d grid of random letters, a %d x %d block copied from row %d, column %d ; two-dimensional fingerprints: %,d rolling steps, %d window%s checked letter by letter, found at row %d, column %d ; the obvious method: %,d letter comparisons%n",
                N, N, M, M, pr, pc, steps2, verify2, verify2 == 1 ? "" : "s", found2.get(0)[0], found2.get(0)[1], naive2);

        System.out.println("KarpRabin: " + passed + " checks passed");
    }

    static long fingerprint(byte[] w, long p) {
        long h = 0;
        for (byte x : w) h = (h * 4 + x) % p;
        return h;
    }

    static int naiveCount(byte[] t, byte[] pat) {
        long keep = comparisons;
        int c = naive(t, pat);
        comparisons = keep;
        return c;
    }
}
