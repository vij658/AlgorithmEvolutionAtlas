import java.util.*;

/**
 * Era 5, topic 10: Hoare's Quicksort (Moscow, 1959; Communications of the ACM, 1961; The Computer Journal, 1962).
 *
 * HOW IT WORKS
 *   Pick one item, the bound (today: the pivot). Partition: a finger starts at each end of the list and moves inward,
 *   the left finger stopping at an item that is not smaller than the bound, the right finger at one that is not
 *   larger; swap the two items and go on until the fingers meet. Now everything on the left is no larger than
 *   everything on the right. Sort the two parts the same way. On random data each partition splits the list roughly
 *   in half, so the work grows like n log n: about 2 n ln n = 1.39 n log2 n comparisons when every other item is
 *   compared with the bound once and the bound is then set aside. If the bound is always the smallest item (a
 *   sorted list and the first item as the bound), each partition peels off one item and the work is about n^2 / 2.
 *   Choosing the bound at random makes that bad luck vanishingly rare.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The words of one of Hoare's own sentences about Moscow, sorted, with the first partition shown.
 *   2. Every ordering of 1 to 9 items: the average number of comparisons, exactly, against 2(n+1)H_n - 4n.
 *   3. Random lists from 1,000 to a million items: comparisons against 1.39 n log2 n and the lower bound log2 n!.
 *   4. Insertion sort, Hoare's first idea, on the same lists while it is still feasible.
 *   5. Sorted input: the first item as the bound, against a bound chosen at random.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Quicksort.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Quicksort {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1959L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % n);
    }

    static long comparisons;
    static boolean randomBound;

    static <T extends Comparable<T>> boolean less(T a, T b) { comparisons++; return a.compareTo(b) < 0; }

    /** Hoare's partition with two fingers; returns j such that a[lo..j] <= a[j+1..hi]. */
    static <T extends Comparable<T>> int partition(T[] a, int lo, int hi) {
        if (randomBound) swap(a, lo, lo + rnd(hi - lo + 1));
        T bound = a[lo];
        int i = lo - 1, j = hi + 1;
        while (true) {
            do i++; while (less(a[i], bound));
            do j--; while (less(bound, a[j]));
            if (i >= j) return j;
            swap(a, i, j);
        }
    }

    static <T> void swap(T[] a, int i, int j) { T t = a[i]; a[i] = a[j]; a[j] = t; }

    /** Sort the smaller part by recursion and the larger by going round again, so the stack stays short. */
    static <T extends Comparable<T>> void quicksort(T[] a, int lo, int hi) {
        while (lo < hi) {
            int p = partition(a, lo, hi);
            if (p - lo < hi - p) { quicksort(a, lo, p); lo = p + 1; }
            else { quicksort(a, p + 1, hi); hi = p; }
        }
    }

    /** A partition that compares every other item with the bound exactly once (for the exact average). */
    static int partitionOnce(int[] a, int lo, int hi) {
        int bound = a[lo], k = lo;
        for (int i = lo + 1; i <= hi; i++) { comparisons++; if (a[i] < bound) { k++; int t = a[k]; a[k] = a[i]; a[i] = t; } }
        int t = a[lo]; a[lo] = a[k]; a[k] = t;
        return k;
    }

    static void quicksortOnce(int[] a, int lo, int hi) {
        while (lo < hi) {
            int p = partitionOnce(a, lo, hi);
            if (p - lo < hi - p) { quicksortOnce(a, lo, p - 1); lo = p + 1; }
            else { quicksortOnce(a, p + 1, hi); hi = p - 1; }
        }
    }

    static long insertionSort(int[] a) {
        long c = 0;
        for (int i = 1; i < a.length; i++) {
            int x = a[i], j = i - 1;
            while (j >= 0) { c++; if (a[j] > x) { a[j + 1] = a[j]; j--; } else break; }
            a[j + 1] = x;
        }
        return c;
    }

    static boolean permute(int[] p) {
        int i = p.length - 2;
        while (i >= 0 && p[i] > p[i + 1]) i--;
        if (i < 0) return false;
        int j = p.length - 1;
        while (p[j] < p[i]) j--;
        int t = p[i]; p[i] = p[j]; p[j] = t;
        for (int a = i + 1, b = p.length - 1; a < b; a++, b--) { t = p[a]; p[a] = p[b]; p[b] = t; }
        return true;
    }

    static Integer[] randomList(int n) {
        Integer[] a = new Integer[n];
        for (int i = 0; i < n; i++) a[i] = i;
        for (int i = n - 1; i > 0; i--) swap(a, i, rnd(i + 1));
        return a;
    }

    static double log2(double v) { return Math.log(v) / Math.log(2); }

    public static void main(String[] args) {
        // ---- 1. the words of a sentence ------------------------------------------------------------------------------------
        String sentence = "it paid to sort the words of the sentence into the same alphabetical order before consulting the dictionary";
        String[] w = sentence.split(" ");
        String[] first = w.clone();
        comparisons = 0;
        randomBound = false;
        int cut = partition(first, 0, first.length - 1);
        String left = String.join(" ", Arrays.copyOfRange(first, 0, cut + 1)), right = String.join(" ", Arrays.copyOfRange(first, cut + 1, first.length));
        String[] s = w.clone();
        comparisons = 0;
        quicksort(s, 0, s.length - 1);
        String[] t = w.clone();
        Arrays.sort(t);
        check(Arrays.equals(s, t), "the words are sorted");
        System.out.printf("words: \"%s\" (Hoare, recalling Moscow) ; bound \"%s\" ; after the first partition: [%s] [%s] ; sorted with %d comparisons: %s%n",
                sentence, w[0], left, right, comparisons, String.join(" ", s));

        // ---- 2. every ordering of up to 9 items ----------------------------------------------------------------------------
        StringJoiner ej = new StringJoiner(" ; ");
        for (int n = 1; n <= 9; n++) {
            int[] p = new int[n];
            for (int i = 0; i < n; i++) p[i] = i;
            long total = 0, perms = 0;
            do {
                int[] a = p.clone();
                comparisons = 0;
                quicksortOnce(a, 0, n - 1);
                for (int i = 0; i < n; i++) check(a[i] == i, "sorted");
                total += comparisons;
                perms++;
            } while (permute(p));
            // 2(n+1)H_n - 4n as a fraction over n!: compare total/perms with the formula exactly using doubles of integers
            double h = 0;
            for (int k = 1; k <= n; k++) h += 1.0 / k;
            double formula = 2 * (n + 1) * h - 4 * n, avg = (double) total / perms;
            check(Math.abs(avg - formula) < 1e-9, "exact average for n = " + n);
            if (n >= 3) ej.add(String.format("n=%d: %,d orderings, %.4f", n, perms, avg));
        }
        System.out.printf("exact: every ordering of n distinct items sorted, each item compared with the bound once per partition ; average comparisons %s ; each equals 2(n+1)(1 + 1/2 + ... + 1/n) - 4n exactly%n", ej);

        // ---- 3. random lists ----------------------------------------------------------------------------------------------
        randomBound = false;
        StringJoiner rj = new StringJoiner(" ; ");
        for (int n : new int[]{1000, 10000, 100000, 1000000}) {
            Integer[] a = randomList(n);
            comparisons = 0;
            quicksort(a, 0, n - 1);
            for (int i = 0; i < n; i++) check(a[i] == i, "random list sorted");
            double lower = 0;
            for (int k = 2; k <= n; k++) lower += log2(k);
            rj.add(String.format("%,d items: %,d comparisons = %.2f n log2 n (no method can use fewer than log2 n! = %.2f n log2 n on every list)",
                    n, comparisons, comparisons / (n * log2(n)), lower / (n * log2(n))));
            check(comparisons < 2.2 * n * log2(n), "about n log n");
        }
        System.out.printf("random: random orderings, the first item as the bound ; %s ; the two-finger partition keeps the bound inside one of the parts and compares the items where the fingers meet twice, so it needs somewhat more than the 1.39 n log2 n of the count above%n", rj);

        // ---- 4. insertion sort -------------------------------------------------------------------------------------------
        StringJoiner ij = new StringJoiner(" ; ");
        for (int n : new int[]{1000, 10000, 50000}) {
            Integer[] r = randomList(n);
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = r[i];
            long c = insertionSort(a);
            for (int i = 0; i < n; i++) check(a[i] == i, "insertion sorted");
            comparisons = 0;
            quicksort(r, 0, n - 1);
            ij.add(String.format("%,d items: insertion %,d comparisons, Quicksort %,d", n, c, comparisons));
            check(Math.abs(c - (double) n * n / 4) < 0.05 * n * n / 4, "insertion about n^2/4");
        }
        System.out.printf("insertion: Hoare's first idea, insertion sort, needs about n^2/4 comparisons on random orderings ; %s%n", ij);

        // ---- 5. sorted input ---------------------------------------------------------------------------------------------
        int n = 20000;
        Integer[] sorted = new Integer[n];
        for (int i = 0; i < n; i++) sorted[i] = i;
        randomBound = false;
        comparisons = 0;
        quicksort(sorted, 0, n - 1);
        long firstBound = comparisons;
        for (int i = 0; i < n; i++) sorted[i] = i;
        randomBound = true;
        comparisons = 0;
        quicksort(sorted, 0, n - 1);
        long randBound = comparisons;
        check(firstBound > (long) n * n / 2 && randBound < 2.2 * n * log2(n), "the bad case and its cure");
        System.out.printf("worst: an already sorted list of %,d items ; with the first item as the bound each partition peels off one item: %,d comparisons, more than n^2/2 = %,d ; with the bound chosen at random: %,d (%.2f n log2 n)%n",
                n, firstBound, (long) n * n / 2, randBound, randBound / (n * log2(n)));

        System.out.println("Quicksort: " + passed + " checks passed");
    }
}
