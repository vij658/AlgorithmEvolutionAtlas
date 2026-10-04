import java.math.BigInteger;
import java.util.*;

/**
 * Entry 21 of the principles catalog (Part 2): Divide and conquer, and the master theorem
 *
 * HOW IT WORKS
 *   Split the problem, solve the parts recursively, combine the answers. The master theorem gives the cost of
 *   T(n) = a*T(n/b) + f(n) by comparing f(n) with n^(log_b a); merge sort, Karatsuba multiplication and
 *   quickselect are the worked examples.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java DivideAndConquer.java
 *   Expected: the output in expected-output.txt, ending "DivideAndConquer: 12100 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class DivideAndConquer {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static double log2(double x) { return Math.log(x) / Math.log(2); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static void mergeSort(int[] a, int[] tmp, int lo, int hi) {   // sorts a[lo, hi)
        if (hi - lo < 2) return;
        int mid = (lo + hi) >>> 1;
        mergeSort(a, tmp, lo, mid);
        mergeSort(a, tmp, mid, hi);
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi) tmp[k++] = (a[j] < a[i]) ? a[j++] : a[i++];   // left element first on ties
        while (i < mid) tmp[k++] = a[i++];
        while (j < hi) tmp[k++] = a[j++];
        System.arraycopy(tmp, lo, a, lo, hi - lo);
    }

    static long cmp;                                   // instrumented copy, used only to count comparisons

    static void mergeSortCounted(int[] a, int[] tmp, int lo, int hi) {
        if (hi - lo < 2) return;
        int mid = (lo + hi) >>> 1;
        mergeSortCounted(a, tmp, lo, mid);
        mergeSortCounted(a, tmp, mid, hi);
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi) { cmp++; tmp[k++] = (a[j] < a[i]) ? a[j++] : a[i++]; }
        while (i < mid) tmp[k++] = a[i++];
        while (j < hi) tmp[k++] = a[j++];
        System.arraycopy(tmp, lo, a, lo, hi - lo);
    }

    static long worstMerge(int n) {                    // W(n) = W(floor(n/2)) + W(ceil(n/2)) + n - 1
        return n <= 1 ? 0 : worstMerge(n / 2) + worstMerge(n - n / 2) + n - 1;
    }

    static int quickselect(int[] a, int k, Random rnd) {   // k-th smallest, 0-based; reorders a
        int lo = 0, hi = a.length - 1;
        while (true) {
            if (lo == hi) return a[lo];
            int p = a[lo + rnd.nextInt(hi - lo + 1)];      // random pivot defeats adversarial input
            int i = lo, j = hi;
            while (i <= j) {                               // Hoare-style partition
                while (a[i] < p) i++;
                while (a[j] > p) j--;
                if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
            }
            if (k <= j) hi = j;
            else if (k >= i) lo = i;
            else return a[k];
        }
    }

    static BigInteger karatsuba(BigInteger x, BigInteger y) {
        int n = Math.max(x.bitLength(), y.bitLength());
        if (n <= 512) return x.multiply(y);                // base case: small operands
        int half = n / 2;
        BigInteger xh = x.shiftRight(half), xl = x.subtract(xh.shiftLeft(half));
        BigInteger yh = y.shiftRight(half), yl = y.subtract(yh.shiftLeft(half));
        BigInteger a = karatsuba(xh, yh);
        BigInteger b = karatsuba(xl, yl);
        BigInteger c = karatsuba(xh.add(xl), yh.add(yl)).subtract(a).subtract(b);   // = xh*yl + xl*yh
        return a.shiftLeft(2 * half).add(c.shiftLeft(half)).add(b);
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java DivideAndConquer.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 2000; t++) {
            int[] a = new int[rnd.nextInt(200)];
            for (int i = 0; i < a.length; i++) a[i] = rnd.nextInt(50) - 25;
            int[] expect = a.clone();
            Arrays.sort(expect);
            int[] got = a.clone();
            mergeSort(got, new int[got.length], 0, got.length);
            check(Arrays.equals(got, expect), "merge sort matches Arrays.sort");
        }
        for (int n = 1; n <= 4096; n++) {
            int c = 32 - Integer.numberOfLeadingZeros(n - 1);          // ceil(log2 n); 0 when n = 1
            check(worstMerge(n) == (long) n * c - (1L << c) + 1, "closed form n*ceil(lg n) - 2^ceil(lg n) + 1 at n=" + n);
        }
        double sumCmp = 0;
        int reps = 200, n = 1000;
        for (int t = 0; t < reps; t++) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = rnd.nextInt();
            cmp = 0;
            mergeSortCounted(a, new int[n], 0, n);
            check(cmp <= worstMerge(n), "comparisons within the worst-case bound");
            sumCmp += cmp;
        }
        for (int t = 0; t < 500; t++) {
            int m = 1 + rnd.nextInt(2000);
            int[] a = new int[m];
            for (int i = 0; i < m; i++) a[i] = rnd.nextInt();
            cmp = 0;
            mergeSortCounted(a, new int[m], 0, m);
            check(cmp <= worstMerge(m), "bound at random sizes");
        }
        double lg = 0;
        for (int i = 2; i <= n; i++) lg += log2(i);                    // log2(n!)
        check(sumCmp / reps >= lg, "average comparisons are at least log2(n!)");
        System.out.printf("n = 1000: mean merge-sort comparisons = %.0f, worst-case bound = %d, log2(1000!) = %.0f%n", sumCmp / reps, worstMerge(n), lg);
        double lg10 = 0;
        for (int i = 2; i <= 10; i++) lg10 += log2(i);
        check((int) Math.ceil(lg10) == 22, "ceil(log2(10!)) = 22");

        for (int t = 0; t < 5000; t++) {
            int m = 1 + rnd.nextInt(100);
            int[] a = new int[m];
            for (int i = 0; i < m; i++) a[i] = rnd.nextInt(30);
            int[] expect = a.clone();
            Arrays.sort(expect);
            int k = rnd.nextInt(m);
            check(quickselect(a.clone(), k, rnd) == expect[k], "quickselect matches sorted[k]");
        }
        check(close(log2(3), 1.585, 0.0005) && close(log2(7), 2.807, 0.0005), "master theorem exponents for Karatsuba and Strassen");
        for (int t = 0; t < 300; t++) {
            BigInteger x = new BigInteger(1 + rnd.nextInt(20000), rnd), y = new BigInteger(1 + rnd.nextInt(20000), rnd);
            if (rnd.nextBoolean()) x = x.negate();
            check(karatsuba(x, y).equals(x.multiply(y)), "Karatsuba matches multiply");
        }
        check(karatsuba(BigInteger.ZERO, BigInteger.TEN.pow(300)).equals(BigInteger.ZERO), "Karatsuba with zero");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("DivideAndConquer: " + passed + " checks passed");
    }
}
