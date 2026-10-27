import java.util.*;

/**
 * Era 8, topic 3: Streaming sketches (Flajolet and Martin 1983-1985; Alon, Matias and Szegedy 1996; Cormode and
 * Muthukrishnan's Count-Min sketch 2005; Flajolet, Fusy, Gandouet and Meunier's HyperLogLog 2007).
 *
 * HOW IT WORKS
 *   A stream of items goes past once, too many to keep. Three questions, three sketches:
 *   - How "repetitive" is the stream? The second frequency moment F2 = sum of (count of item i)^2. Alon, Matias and
 *     Szegedy give every item a random sign s(i) = +1 or -1 and keep one number, Z = sum of s(item) over the stream.
 *     Then Z^2 averages to F2, because the cross terms s(i) s(j) cancel on average. Average many independent copies
 *     to shrink the spread, and take the median of several averages to make a bad answer unlikely.
 *   - How often did item x appear? Count-Min keeps d rows of w counters; each row hashes x to one counter and adds 1.
 *     Other items that land in the same counters only add to it, so every row overestimates; the smallest of the d
 *     counters is the estimate, never too low, and with w = e / epsilon and d = ln(1 / delta) it is too high by more
 *     than epsilon times the stream's length with probability below delta.
 *   - How many different items? Hash each item to a random-looking bit string. Among n different items, about one
 *     in 2^k has a hash starting with k zeros, so the longest run of leading zeros seen says roughly log2 n.
 *     HyperLogLog splits the items into m groups by the first bits of the hash, keeps the longest run in each group
 *     (a number below 64, so 6 bits), and combines the m answers with a harmonic mean. The error is about
 *     1.04 / sqrt(m), whatever n is. Flajolet and Martin's earlier method keeps a bitmap per group instead.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A stream of 1,000,000 items drawn from 100,000 keys with a Zipf law (a few keys very common), counted
 *      exactly for comparison.
 *   2. The F2 sketch: one pass for a few copies, checked against the same sums computed key by key; then the error
 *      for 64 and 256 copies, and how often it falls within the promised bound.
 *   3. Count-Min with epsilon = 0.001 and delta = 0.01: every key's estimate checked against its true count.
 *   4. HyperLogLog and Flajolet-Martin counting: the spread of the error over 200 different hash functions for
 *      several numbers of registers, against 1.04 / sqrt(m) and 0.78 / sqrt(m); and 10 million distinct items in
 *      2,048 registers.
 *   5. A small Count-Min sketch (3 rows of 16 counters) over the words of a paragraph, for the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java StreamingSketches.java
 *   Expected output: expected-output.txt in this folder.
 */
public class StreamingSketches {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static int s32 = 1996;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    static long nextLong() { return ((long) (next32() * 4294967296.0) << 32) ^ (long) (next32() * 4294967296.0); }

    static final long P = 2147483647L; // the prime 2^31 - 1

    /** A random polynomial of degree 3 modulo P: its values at different points are four-wise independent. */
    static long[] poly4() { long[] a = new long[4]; for (int k = 0; k < 4; k++) a[k] = Math.floorMod(nextLong(), P); return a; }

    static long modP(long v) { v = (v & P) + (v >>> 31); return v >= P ? v - P : v; } // v mod (2^31 - 1), for 0 <= v < 2^62

    static int sign(long[] a, long x) {
        long v = a[3];
        for (int k = 2; k >= 0; k--) v = modP(modP(v * x) + a[k]);
        return (v & 1) == 0 ? 1 : -1;
    }

    static long mix64(long z) { // splitmix64's finalizer: a strong 64-bit mixing function
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    static double hyperLogLog(int[] keys, int b, long salt) {
        int m = 1 << b;
        byte[] reg = new byte[m];
        for (int x : keys) {
            long h = mix64(x * 0x9e3779b97f4a7c15L + salt);
            int j = (int) (h >>> (64 - b));
            long rest = h << b;
            int rho = rest == 0 ? 64 - b + 1 : Long.numberOfLeadingZeros(rest) + 1;
            if (rho > reg[j]) reg[j] = (byte) rho;
        }
        double sum = 0;
        int zeros = 0;
        for (byte r : reg) { sum += Math.pow(2, -r); if (r == 0) zeros++; }
        double alpha = m == 16 ? 0.673 : m == 32 ? 0.697 : m == 64 ? 0.709 : 0.7213 / (1 + 1.079 / m);
        double e = alpha * m * (double) m / sum;
        if (e <= 2.5 * m && zeros > 0) e = m * Math.log((double) m / zeros); // small range: count empty registers
        return e;
    }

    static double flajoletMartin(int[] keys, int m, long salt) {
        long[] bitmap = new long[m];
        for (int x : keys) {
            long h = mix64(x * 0x9e3779b97f4a7c15L + salt);
            int j = (int) Long.remainderUnsigned(h, m);
            long rest = Long.divideUnsigned(h, m);
            int rho = rest == 0 ? 63 : Long.numberOfTrailingZeros(rest);
            bitmap[j] |= 1L << rho;
        }
        double sumR = 0;
        for (long bm : bitmap) sumR += Long.numberOfTrailingZeros(~bm); // position of the lowest 0 bit
        return m / 0.77351 * Math.pow(2, sumR / m);
    }

    static long keyByKey(long[] a, int[] keys, long[] counts) {
        long z = 0;
        for (int i = 0; i < keys.length; i++) z += counts[i] * sign(a, keys[i]);
        return z;
    }

    static double median(double[] v) { double[] c = v.clone(); Arrays.sort(c); return c.length % 2 == 1 ? c[c.length / 2] : (c[c.length / 2 - 1] + c[c.length / 2]) / 2; }

    static final String PARAGRAPH = "the web becomes a web of tens of millions of pages which must be searched ranked copied to caches "
            + "and cleared of duplicates the data streams past faster than it can be kept and the computers now thousands "
            + "in one room must work as one and agree on one history the methods of this era are built for scale they "
            + "summarize instead of storing sample instead of measuring everything settle for a provable approximation "
            + "and assume that some part is always failing";

    public static void main(String[] args) {
        // ---- 1. the stream -------------------------------------------------------------------------------------------
        int n = 100_000, m = 1_000_000;
        double[] cdf = new double[n];
        double z = 0;
        for (int k = 0; k < n; k++) { z += 1 / Math.pow(k + 1, 1.1); cdf[k] = z; }
        int[] stream = new int[m];
        long[] count = new long[n];
        for (int t = 0; t < m; t++) {
            double u = next32() * z;
            int lo = 0, hi = n - 1;
            while (lo < hi) { int mid = (lo + hi) >>> 1; if (cdf[mid] < u) lo = mid + 1; else hi = mid; }
            stream[t] = lo; count[lo]++;
        }
        long f0 = 0, f2 = 0, maxCount = 0;
        for (long c : count) { if (c > 0) f0++; f2 += c * c; maxCount = Math.max(maxCount, c); }
        int[] seen = new int[(int) f0];
        long[] seenCount = new long[(int) f0];
        for (int k = 0, q0 = 0; k < n; k++) if (count[k] > 0) { seen[q0] = k; seenCount[q0++] = count[k]; }
        System.out.printf("stream: %,d items drawn from %,d keys with a Zipf law (key k with weight 1/k^1.1) ; exactly: %,d distinct keys seen (F0), F1 = %,d, F2 = %,d, the commonest key %,d times%n", m, n, f0, (long) m, f2, maxCount);

        // ---- 2. the F2 sketch ------------------------------------------------------------------------------------------
        s32 = 28;
        for (int c = 0; c < 5; c++) { // one pass over the stream, as a streaming algorithm must
            long[] a = poly4();
            long zs = 0;
            for (int x : stream) zs += sign(a, x);
            long zk = keyByKey(a, seen, seenCount);
            check(zs == zk, "the one-pass sum equals the same sum taken key by key");
        }
        StringJoiner fj = new StringJoiner(" ; ");
        for (int s1 : new int[]{64, 256}) {
            double lambda = 4 / Math.sqrt(s1); // s1 = 16 / lambda^2
            int trials = 40, within = 0;
            double sumErr = 0;
            for (int t = 0; t < trials; t++) {
                double mean = 0;
                for (int c = 0; c < s1; c++) {
                    long[] a = poly4();
                    long zk = keyByKey(a, seen, seenCount);
                    mean += (double) zk * zk;
                }
                mean /= s1;
                double err = Math.abs(mean - f2) / f2;
                sumErr += err;
                if (err <= lambda) within++;
            }
            check(within >= 0.875 * trials * 0.9, "Chebyshev: an average of 16/lambda^2 copies is within lambda at least 7/8 of the time (allowing sampling noise)");
            fj.add(String.format("%,d copies (%,d bytes): average error %.1f%%, within the promised %.1f%% in %d of %d trials", s1, s1 * 8, 100 * sumErr / trials, 100 * lambda, within, trials));
        }
        // median of averages
        double[] avgs = new double[9];
        for (int r = 0; r < 9; r++) {
            double mean = 0;
            for (int c = 0; c < 256; c++) {
                long[] a = poly4();
                long zk = keyByKey(a, seen, seenCount);
                mean += (double) zk * zk;
            }
            avgs[r] = mean / 256;
        }
        double med = median(avgs);
        System.out.printf("ams: sign from a random cubic modulo 2^31 - 1 (four-wise independent) ; one pass checked against the key-by-key sum for 5 copies ; 40 trials each: %s ; median of 9 averages of 256 copies: %,.0f against %,d (error %.1f%%)%n", fj, med, f2, 100 * Math.abs(med - f2) / f2);

        // ---- 3. Count-Min -----------------------------------------------------------------------------------------------
        double eps = 0.001, delta = 0.01;
        int w = (int) Math.ceil(Math.E / eps), d = (int) Math.ceil(Math.log(1 / delta));
        long[][] cm = new long[d][w];
        long[] ha = new long[d], hb = new long[d];
        s32 = 2005;
        for (int r = 0; r < d; r++) { ha[r] = 1 + Math.floorMod(nextLong(), P - 1); hb[r] = Math.floorMod(nextLong(), P); }
        for (int x : stream) for (int r = 0; r < d; r++) cm[r][(int) ((ha[r] * x + hb[r]) % P % w)]++;
        int tooHigh = 0, exact = 0;
        long worstOver = 0;
        for (int k = 0; k < n; k++) {
            long est = Long.MAX_VALUE;
            for (int r = 0; r < d; r++) est = Math.min(est, cm[r][(int) ((ha[r] * k + hb[r]) % P % w)]);
            check(est >= count[k], "Count-Min never underestimates");
            if (est - count[k] > eps * m) tooHigh++;
            if (est == count[k]) exact++;
            worstOver = Math.max(worstOver, est - count[k]);
        }
        check(tooHigh <= delta * n, "at most a fraction delta of keys is overestimated by more than epsilon m");
        // heavy hitters: keys whose estimate is at least 1% of the stream
        int reported = 0, truly = 0, missed = 0;
        for (int k = 0; k < n; k++) {
            long est = Long.MAX_VALUE;
            for (int r = 0; r < d; r++) est = Math.min(est, cm[r][(int) ((ha[r] * k + hb[r]) % P % w)]);
            if (est >= 0.01 * m) reported++;
            if (count[k] >= 0.01 * m) { truly++; if (est < 0.01 * m) missed++; }
        }
        check(missed == 0, "no key with 1% of the stream is missed");
        System.out.printf("countmin: epsilon = %.3f, delta = %.2f, so %d rows of %,d counters (%,d counters in all, against %,d for exact counts) ; all %,d keys queried: none too low, %,d exact, %d too high by more than epsilon m = %,.0f (allowed: %,.0f), largest overestimate %,d ; keys with at least 1%% of the stream: %d really, %d reported, none missed%n",
                eps, delta, d, w, d * w, n, n, exact, tooHigh, eps * m, delta * n, worstOver, truly, reported);

        // ---- 4. counting distinct items -------------------------------------------------------------------------------
        int[] distinctKeys = new int[(int) f0];
        int q = 0;
        for (int k = 0; k < n; k++) if (count[k] > 0) distinctKeys[q++] = k;
        check(hyperLogLog(stream, 10, 5) == hyperLogLog(distinctKeys, 10, 5), "repeats do not change HyperLogLog's registers");
        check(flajoletMartin(stream, 256, 5) == flajoletMartin(distinctKeys, 256, 5), "nor Flajolet-Martin's bitmaps");
        StringJoiner hj = new StringJoiner(" ; ");
        for (int b : new int[]{6, 8, 10, 12}) {
            int regs = 1 << b, trials = 200;
            double ss = 0, sf = 0;
            for (int t = 0; t < trials; t++) {
                double e = hyperLogLog(distinctKeys, b, 1000L * t + b);
                ss += Math.pow((e - f0) / f0, 2);
                double ef = flajoletMartin(distinctKeys, regs, 7000L * t + b);
                sf += Math.pow((ef - f0) / f0, 2);
            }
            double sd = Math.sqrt(ss / trials), sdf = Math.sqrt(sf / trials), th = 1.04 / Math.sqrt(regs), thf = 0.78 / Math.sqrt(regs);
            check(sd > 0.7 * th && sd < 1.3 * th, "HyperLogLog's spread is about 1.04/sqrt(m)");
            check(sdf > 0.7 * thf && sdf < 1.4 * thf, "Flajolet-Martin's spread is about 0.78/sqrt(m)");
            hj.add(String.format("m = %,d: HyperLogLog %.2f%% (theory %.2f%%, %,d bytes at 6 bits a register), Flajolet-Martin %.2f%% (theory %.2f%%, %,d bytes of bitmaps)", regs, 100 * sd, 100 * th, regs * 6 / 8, 100 * sdf, 100 * thf, regs * 8));
        }
        int big = 10_000_000;
        int[] bigKeys = new int[big];
        for (int i = 0; i < big; i++) bigKeys[i] = i;
        double eb = hyperLogLog(bigKeys, 11, 42);
        check(Math.abs(eb - big) / big < 0.05, "10 million distinct items within 5% from 2,048 registers");
        System.out.printf("distinct: true count %,d ; spread (root mean square relative error) over 200 hash functions: %s ; 10,000,000 distinct items in 2,048 registers (1,536 bytes): estimate %,.0f (error %.2f%%)%n", f0, hj, eb, 100 * Math.abs(eb - big) / big);

        // ---- 5. the widget's small Count-Min ----------------------------------------------------------------------------
        String[] words = PARAGRAPH.split(" ");
        Map<String, Integer> truth = new TreeMap<>();
        for (String wd : words) truth.merge(wd, 1, Integer::sum);
        int W = 32, D = 3, PP = 65521;
        int[] A = {3, 7, 11}, B = {1, 5, 9};
        int[][] small = new int[D][W];
        for (String wd : words) for (int r = 0; r < D; r++) small[r][bucket(wd, A[r], B[r], PP, W)]++;
        StringJoiner rows = new StringJoiner(" | ");
        for (int r = 0; r < D; r++) { StringJoiner one = new StringJoiner(","); for (int c : small[r]) one.add(Integer.toString(c)); rows.add(one.toString()); }
        StringJoiner est = new StringJoiner(" ");
        int over = 0;
        for (Map.Entry<String, Integer> e : truth.entrySet()) {
            int ev = Integer.MAX_VALUE;
            for (int r = 0; r < D; r++) ev = Math.min(ev, small[r][bucket(e.getKey(), A[r], B[r], PP, W)]);
            check(ev >= e.getValue(), "the small sketch never underestimates either");
            if (ev > e.getValue()) over++;
            if (e.getValue() >= 3) est.add(e.getKey() + ":" + e.getValue() + ":" + ev);
        }
        System.out.printf("widget: %d words, %d different ; word hash h = (31 h + letter code) mod 65521 ; row r puts a word in counter ((a_r h + b_r) mod 65521) mod 32 with (a, b) = (3, 1), (7, 5), (11, 9) ; counters: %s ; %d of %d words overestimated ; word:true:estimate for words seen 3 or more times: %s%n",
                words.length, truth.size(), rows, over, truth.size(), est);

        System.out.println("StreamingSketches: " + passed + " checks passed");
    }

    static int bucket(String word, int a, int b, int p, int w) {
        int h = 0;
        for (char ch : word.toCharArray()) h = (31 * h + ch) % p;
        return ((a * h + b) % p) % w;
    }
}
