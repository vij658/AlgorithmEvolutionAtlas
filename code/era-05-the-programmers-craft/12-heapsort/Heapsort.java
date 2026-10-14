import java.util.*;

/**
 * Era 5, topic 12: heapsort and the heap (Williams 1964; Floyd 1964).
 *
 * HOW IT WORKS
 *   A heap is a list read as a tree: the item at position i (counting from 0) has its children at 2i+1 and 2i+2,
 *   and every item is at least as large as its children, so the largest is at the front. To add an item, put it at
 *   the end and let it climb past smaller parents (Williams). To remove the largest, move the last item to the front
 *   and let it sink below larger children. Heapsort builds a heap from the list, then repeatedly swaps the front
 *   (largest) item with the last item of the heap and lets the new front sink: the sorted list grows at the back,
 *   inside the same array. Floyd built the heap faster: treat each of the lower half of the positions, from the back,
 *   as the root of a small heap and let it sink; most items sink only a level or two, so building takes fewer than
 *   2n comparisons. Sorting then takes about 2 n log2 n comparisons, whatever the input.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A heap built from ten numbers, as an array and as a tree.
 *   2. Building a heap by Williams's insertions and by Floyd's sinking: comparisons, and the exact worst case of
 *      Floyd's method over every ordering of up to 10 items against 2n - 2s(n) - e(n).
 *   3. Heapsort on random and on sorted lists up to a million items: comparisons against 2 n log2 n, with no extra list.
 *   4. Equal keys: heapsort does not keep their original order.
 *   5. The heap as a priority queue: Dijkstra's shortest paths (topic 7) with set B kept in a heap.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Heapsort.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Heapsort {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long comparisons;

    static boolean less(long[] a, int i, int j) { comparisons++; return a[i] < a[j]; }

    static void swap(long[] a, int i, int j) { long t = a[i]; a[i] = a[j]; a[j] = t; }

    /** Let a[i] climb past smaller parents. */
    static void climb(long[] a, int i) {
        while (i > 0) {
            int p = (i - 1) / 2;
            if (less(a, p, i)) { swap(a, p, i); i = p; } else break;
        }
    }

    /** Let a[i] sink below larger children, within a[0..n-1]. */
    static void sink(long[] a, int i, int n) {
        while (2 * i + 1 < n) {
            int c = 2 * i + 1;
            if (c + 1 < n && less(a, c, c + 1)) c++;
            if (less(a, i, c)) { swap(a, i, c); i = c; } else break;
        }
    }

    static void buildWilliams(long[] a) { for (int i = 1; i < a.length; i++) climb(a, i); }

    static void buildFloyd(long[] a) { for (int i = a.length / 2 - 1; i >= 0; i--) sink(a, i, a.length); }

    static void heapsort(long[] a) {
        buildFloyd(a);
        for (int end = a.length - 1; end > 0; end--) { swap(a, 0, end); sink(a, 0, end); }
    }

    static boolean isHeap(long[] a) {
        for (int i = 1; i < a.length; i++) if (a[(i - 1) / 2] < a[i]) return false;
        return true;
    }

    static boolean permute(long[] p) {
        int i = p.length - 2;
        while (i >= 0 && p[i] > p[i + 1]) i--;
        if (i < 0) return false;
        int j = p.length - 1;
        while (p[j] < p[i]) j--;
        swap(p, i, j);
        for (int a = i + 1, b = p.length - 1; a < b; a++, b--) swap(p, a, b);
        return true;
    }

    static long seed = 1964L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed >>> 1;
    }

    static int rnd(int n) { return (int) ((next() >>> 20) % n); }

    static double log2(double v) { return Math.log(v) / Math.log(2); }

    public static void main(String[] args) {
        // ---- 1. a small heap ------------------------------------------------------------------------------------------------
        long[] ten = {31, 41, 59, 26, 53, 58, 97, 93, 23, 84};
        long[] h = ten.clone();
        buildFloyd(h);
        check(isHeap(h), "heap property");
        StringJoiner arr = new StringJoiner(" "), tree = new StringJoiner(" | ");
        for (long v : h) arr.add(String.valueOf(v));
        for (int level = 0, start = 0; start < h.length; level++, start = 2 * start + 1) {
            StringJoiner row = new StringJoiner(" ");
            for (int i = start; i < Math.min(h.length, 2 * start + 1); i++) row.add(String.valueOf(h[i]));
            tree.add("level " + level + ": " + row);
        }
        System.out.printf("heap: the numbers %s built into a heap by Floyd's method: %s ; read as a tree (children of position i at 2i+1 and 2i+2): %s ; every number is at least as large as the numbers below it%n",
                Arrays.toString(ten).replaceAll("[\\[\\],]", ""), arr, tree);

        // ---- 2. building: Williams against Floyd -----------------------------------------------------------------------------
        StringJoiner bj = new StringJoiner(" ; ");
        for (int n : new int[]{1000, 100000, 1000000}) {
            long[] a = new long[n];
            for (int i = 0; i < n; i++) a[i] = next();
            long[] b = a.clone();
            comparisons = 0;
            buildWilliams(a);
            long cw = comparisons;
            comparisons = 0;
            buildFloyd(b);
            long cf = comparisons;
            check(isHeap(a) && isHeap(b), "both are heaps");
            check(cf < 2L * n, "Floyd under 2n");
            long[] s = new long[n];
            for (int i = 0; i < n; i++) s[i] = i;                       // ascending: every insertion climbs to the top
            comparisons = 0;
            buildWilliams(s);
            long cwWorst = comparisons;
            bj.add(String.format("%,d random items: Williams %,d comparisons, Floyd %,d (%.2f per item) ; Williams on ascending items %,d", n, cw, cf, (double) cf / n, cwWorst));
        }
        StringJoiner fj = new StringJoiner(" ; ");
        for (int n = 2; n <= 10; n++) {
            long[] p = new long[n];
            for (int i = 0; i < n; i++) p[i] = i;
            long worst = 0;
            do {
                long[] a = p.clone();
                comparisons = 0;
                buildFloyd(a);
                worst = Math.max(worst, comparisons);
            } while (permute(p));
            int s2 = Integer.bitCount(n), e2 = Integer.numberOfTrailingZeros(n);
            long formula = 2L * n - 2L * s2 - e2;
            check(worst == formula, "Floyd's worst case for n = " + n);
            fj.add(String.format("n=%d: %d", n, worst));
        }
        System.out.printf("build: %s%n", bj);
        System.out.printf("floyd: the most comparisons Floyd's method needs, over every ordering of n items: %s ; each equals 2n - 2s(n) - e(n), s(n) the number of 1s in n written in binary and e(n) its trailing 0s%n", fj);

        // ---- 3. heapsort ---------------------------------------------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        for (int n : new int[]{1000, 100000, 1000000}) {
            for (String kind : new String[]{"random", "sorted"}) {
                long[] a = new long[n];
                for (int i = 0; i < n; i++) a[i] = kind.equals("sorted") ? i : next();
                long[] ref = a.clone();
                Arrays.sort(ref);
                comparisons = 0;
                heapsort(a);
                check(Arrays.equals(a, ref), "sorted correctly");
                check(comparisons < 2 * n * log2(n), "under 2 n log2 n");
                if (n != 1000 || kind.equals("random")) sj.add(String.format("%,d %s: %,d comparisons = %.2f n log2 n", n, kind, comparisons, comparisons / (n * log2(n))));
            }
        }
        System.out.printf("sort: heapsort, the sorted part growing at the back of the same array ; %s ; sorted input costs about the same as random input (Quicksort with the first item as its bound needed over n^2/2 on sorted input, topic 10)%n", sj);

        // ---- 4. equal keys ------------------------------------------------------------------------------------------------------
        String[] cards = {"5a", "3a", "5b", "3b", "5c"};
        long[] packed = {5, 3, 5, 3, 5};                              // the numbers; the letters ride along in where[]
        int[] where = {0, 1, 2, 3, 4};
        int n5 = 5;
        for (int i = n5 / 2 - 1; i >= 0; i--) sinkLabels(packed, where, i, n5);
        for (int end = n5 - 1; end > 0; end--) { swapBoth(packed, where, 0, end); sinkLabels(packed, where, 0, end); }
        StringJoiner out = new StringJoiner(" ");
        for (int i = 0; i < 5; i++) out.add(cards[where[i]]);
        check(!out.toString().equals("3a 3b 5a 5b 5c"), "heapsort is not stable");
        System.out.printf("stable: cards 5a 3a 5b 3b 5c sorted by number only ; heapsort gives %s ; the letters show that cards with equal numbers changed their order (a stable sort would give 3a 3b 5a 5b 5c)%n", out);

        // ---- 5. a priority queue for Dijkstra ---------------------------------------------------------------------------------
        int n = 20000;
        int[][] xy = new int[n][2];
        for (int i = 0; i < n; i++) { xy[i][0] = rnd(100000); xy[i][1] = rnd(100000); }
        // roads: each town to 4 random towns among its 40 neighbours in a sorted strip (cheap way to make local roads)
        Integer[] byX = new Integer[n];
        for (int i = 0; i < n; i++) byX[i] = i;
        Arrays.sort(byX, Comparator.comparingInt(i -> xy[i][0]));
        List<List<int[]>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int r = 0; r < n; r++)
            for (int t = 0; t < 4; t++) {
                int s2 = r + 1 + rnd(20);
                if (s2 >= n) continue;
                int a = byX[r], b = byX[s2];
                int len = (int) Math.round(Math.hypot(xy[a][0] - xy[b][0], xy[a][1] - xy[b][1]));
                g.get(a).add(new int[]{b, len});
                g.get(b).add(new int[]{a, len});
            }
        // scan version (1959)
        long[] d1 = new long[n];
        Arrays.fill(d1, Long.MAX_VALUE);
        boolean[] done = new boolean[n];
        d1[byX[0]] = 0;
        long scanSteps = 0;
        for (int k = 0; k < n; k++) {
            int u = -1;
            for (int i = 0; i < n; i++) { scanSteps++; if (!done[i] && d1[i] != Long.MAX_VALUE && (u < 0 || d1[i] < d1[u])) u = i; }
            if (u < 0) break;
            done[u] = true;
            for (int[] e : g.get(u)) if (!done[e[0]] && d1[u] + e[1] < d1[e[0]]) d1[e[0]] = d1[u] + e[1];
        }
        // heap version: entries (distance, town) packed into a long, with stale entries skipped
        long[] d2 = new long[n];
        Arrays.fill(d2, Long.MAX_VALUE);
        d2[byX[0]] = 0;
        long[] heap = new long[8 * n + 16];
        int size = 0;
        comparisons = 0;
        heap[size++] = -((0L << 20) | byX[0]);                  // a max-heap of negated keys is a min-heap
        boolean[] fin = new boolean[n];
        long heapSteps = 0;
        while (size > 0) {
            long top = -heap[0];
            heap[0] = heap[--size];
            sink(heap, 0, size);
            int u = (int) (top & ((1 << 20) - 1));
            long du = top >>> 20;
            heapSteps++;
            if (fin[u] || du != d2[u]) continue;
            fin[u] = true;
            for (int[] e : g.get(u)) {
                long nd = du + e[1];
                if (nd < d2[e[0]]) {
                    d2[e[0]] = nd;
                    heap[size] = -((nd << 20) | e[0]);
                    climb(heap, size);
                    size++;
                }
            }
        }
        check(Arrays.equals(d1, d2), "heap version agrees");
        System.out.printf("queue: Dijkstra's method on %,d towns with %,d roads ; finding the nearest town of set B by scanning every town: %,d steps ; keeping set B in a heap: %,d removals from the heap and %,d comparisons ; the same distances to every town%n",
                n, g.stream().mapToInt(List::size).sum() / 2, scanSteps, heapSteps, comparisons);

        System.out.println("Heapsort: " + passed + " checks passed");
    }

    static void swapBoth(long[] a, int[] w, int i, int j) { swap(a, i, j); int t = w[i]; w[i] = w[j]; w[j] = t; }

    static void sinkLabels(long[] a, int[] w, int i, int n) {
        while (2 * i + 1 < n) {
            int c = 2 * i + 1;
            if (c + 1 < n && a[c] < a[c + 1]) c++;
            if (a[i] < a[c]) { swapBoth(a, w, i, c); i = c; } else break;
        }
    }
}
