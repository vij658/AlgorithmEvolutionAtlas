import java.util.*;

/**
 * Era 6, topic 7: B-trees, balanced trees for the disk (Bayer and McCreight, 1970-72).
 *
 * HOW IT WORKS
 *   A balanced binary tree (Era 5, topic 11) finds one key among a million in about 20 steps. In memory that is
 *   nothing; but an index too big for memory lives on a disk, each step can mean a separate read of the disk, and a
 *   disk read costs as much as a great many steps in memory. Bayer and McCreight made each node a whole "page" of the
 *   disk, holding between k and 2k keys in order, with a child between each pair. One read brings in a whole page,
 *   and a search descends through only a few pages.
 *   Insertion adds the key to its leaf page. If the page then holds 2k + 1 keys, it splits: the middle key moves up
 *   into the parent, and the two halves of k keys each become pages. A split can climb to the root; when the root
 *   splits, the tree grows a new root, so every leaf always stays at the same depth.
 *   Deletion is the mirror image: a page left with fewer than k keys borrows one from a neighbour through the parent,
 *   or, if the neighbour has only k, merges with it, pulling the separating key down.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A small tree (k = 2: pages of 2 to 4 keys), built key by key, every split shown.
 *   2. A million random keys in trees with pages of 4, 20, 100 and 400 keys: height and pages read per search,
 *      against a balanced binary tree.
 *   3. How full the pages are, keys inserted in random order and in sorted order.
 *   4. Half the keys deleted: the rules still hold everywhere, and every search is still right.
 *   5. The height of every tree built, against the bounds that the rules imply.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BTrees.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BTrees {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1970L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed >>> 1;
    }

    static class Page {
        int n;
        long[] keys;
        Page[] kids;              // null for a leaf

        Page(int k, boolean leaf) {
            keys = new long[2 * k + 1];
            if (!leaf) kids = new Page[2 * k + 2];
        }

        boolean leaf() { return kids == null; }
    }

    static class BTree {
        final int k;
        Page root;
        long reads, splits, merges, borrows, size;
        final List<String> log = new ArrayList<>();
        boolean logging;

        BTree(int k) { this.k = k; root = new Page(k, true); }

        /** Position of the first key >= x in the page. */
        static int find(Page p, long x) {
            int lo = 0, hi = p.n;
            while (lo < hi) { int mid = (lo + hi) >>> 1; if (p.keys[mid] < x) lo = mid + 1; else hi = mid; }
            return lo;
        }

        boolean contains(long x) {
            Page p = root;
            while (true) {
                reads++;
                int i = find(p, x);
                if (i < p.n && p.keys[i] == x) return true;
                if (p.leaf()) return false;
                p = p.kids[i];
            }
        }

        boolean insert(long x) {
            Object[] up = insert(root, x);
            if (up == null) return false;
            if (up.length == 2) {                                  // the root split: a new root on top
                Page r = new Page(k, false);
                r.keys[0] = (long) up[0];
                r.kids[0] = root;
                r.kids[1] = (Page) up[1];
                r.n = 1;
                root = r;
                if (logging) log.add("new root " + up[0]);
            }
            size++;
            return true;
        }

        /** Returns null if x was present, an empty array if nothing moved up, else {middle key, new right page}. */
        Object[] insert(Page p, long x) {
            int i = find(p, x);
            if (i < p.n && p.keys[i] == x) return null;
            if (!p.leaf()) {
                Object[] up = insert(p.kids[i], x);
                if (up == null || up.length == 0) return up;
                System.arraycopy(p.keys, i, p.keys, i + 1, p.n - i);
                System.arraycopy(p.kids, i + 1, p.kids, i + 2, p.n - i);
                p.keys[i] = (long) up[0];
                p.kids[i + 1] = (Page) up[1];
            } else {
                System.arraycopy(p.keys, i, p.keys, i + 1, p.n - i);
                p.keys[i] = x;
            }
            p.n++;
            if (p.n <= 2 * k) return new Object[0];
            // the page holds 2k + 1 keys: split it around the middle key
            Page right = new Page(k, p.leaf());
            System.arraycopy(p.keys, k + 1, right.keys, 0, k);
            if (!p.leaf()) System.arraycopy(p.kids, k + 1, right.kids, 0, k + 1);
            right.n = k;
            p.n = k;
            if (!p.leaf()) for (int j = k + 1; j <= 2 * k + 1; j++) p.kids[j] = null;
            splits++;
            if (logging) log.add("split around " + p.keys[k]);
            return new Object[]{p.keys[k], right};
        }

        boolean delete(long x) {
            boolean found = delete(root, x);
            if (root.n == 0 && !root.leaf()) root = root.kids[0];      // the root emptied: the tree shrinks
            if (found) size--;
            return found;
        }

        boolean delete(Page p, long x) {
            int i = find(p, x);
            boolean here = i < p.n && p.keys[i] == x;
            if (p.leaf()) {
                if (!here) return false;
                System.arraycopy(p.keys, i + 1, p.keys, i, p.n - i - 1);
                p.n--;
                return true;
            }
            boolean found;
            if (here) {
                // replace x by the largest key of its left subtree, then delete that key there
                Page q = p.kids[i];
                while (!q.leaf()) q = q.kids[q.n];
                long pred = q.keys[q.n - 1];
                p.keys[i] = pred;
                found = delete(p.kids[i], pred);
            } else found = delete(p.kids[i], x);
            if (p.kids[i].n < k) repair(p, i);
            return found;
        }

        /** Child i of p has k - 1 keys: borrow from a neighbour with more than k, or merge with one. */
        void repair(Page p, int i) {
            Page c = p.kids[i];
            if (i > 0 && p.kids[i - 1].n > k) {                         // borrow from the left
                Page l = p.kids[i - 1];
                System.arraycopy(c.keys, 0, c.keys, 1, c.n);
                if (!c.leaf()) System.arraycopy(c.kids, 0, c.kids, 1, c.n + 1);
                c.keys[0] = p.keys[i - 1];
                if (!c.leaf()) c.kids[0] = l.kids[l.n];
                p.keys[i - 1] = l.keys[l.n - 1];
                if (!l.leaf()) l.kids[l.n] = null;
                l.n--; c.n++;
                borrows++;
            } else if (i < p.n && p.kids[i + 1].n > k) {                // borrow from the right
                Page r = p.kids[i + 1];
                c.keys[c.n] = p.keys[i];
                if (!c.leaf()) c.kids[c.n + 1] = r.kids[0];
                p.keys[i] = r.keys[0];
                System.arraycopy(r.keys, 1, r.keys, 0, r.n - 1);
                if (!r.leaf()) { System.arraycopy(r.kids, 1, r.kids, 0, r.n); r.kids[r.n] = null; }
                r.n--; c.n++;
                borrows++;
            } else {                                                    // merge with a neighbour of exactly k keys
                int j = i > 0 ? i - 1 : i;                              // merge kids[j] and kids[j + 1]
                Page l = p.kids[j], r = p.kids[j + 1];
                l.keys[l.n] = p.keys[j];
                System.arraycopy(r.keys, 0, l.keys, l.n + 1, r.n);
                if (!l.leaf()) System.arraycopy(r.kids, 0, l.kids, l.n + 1, r.n + 1);
                l.n += r.n + 1;
                System.arraycopy(p.keys, j + 1, p.keys, j, p.n - j - 1);
                System.arraycopy(p.kids, j + 2, p.kids, j + 1, p.n - j - 1);
                p.kids[p.n] = null;
                p.n--;
                merges++;
            }
        }

        int height() { int h = 1; for (Page p = root; !p.leaf(); p = p.kids[0]) h++; return h; }

        /** Checks every rule; returns {pages, keys}. */
        long[] verify() {
            long[] count = new long[2];
            int[] leafDepth = {-1};
            long[] last = {Long.MIN_VALUE};
            verify(root, 1, true, count, leafDepth, last);
            return count;
        }

        void verify(Page p, int depth, boolean isRoot, long[] count, int[] leafDepth, long[] last) {
            count[0]++;
            count[1] += p.n;
            check(isRoot ? (p.n <= 2 * k && (p.n >= 1 || p.leaf())) : (p.n >= k && p.n <= 2 * k), "page size");
            if (p.leaf()) {
                if (leafDepth[0] < 0) leafDepth[0] = depth;
                check(leafDepth[0] == depth, "all leaves at one depth");
                for (int i = 0; i < p.n; i++) { check(p.keys[i] > last[0], "keys in order"); last[0] = p.keys[i]; }
                return;
            }
            for (int i = 0; i <= p.n; i++) {
                verify(p.kids[i], depth + 1, false, count, leafDepth, last);
                if (i < p.n) { check(p.keys[i] > last[0], "keys in order"); last[0] = p.keys[i]; }
            }
        }

        String levels() {
            StringJoiner out = new StringJoiner(" / ");
            List<Page> level = List.of(root);
            while (!level.isEmpty()) {
                StringJoiner lj = new StringJoiner(" ");
                List<Page> nextLevel = new ArrayList<>();
                for (Page p : level) {
                    StringJoiner pj = new StringJoiner(" ", "[", "]");
                    for (int i = 0; i < p.n; i++) pj.add(String.valueOf(p.keys[i]));
                    lj.add(pj.toString());
                    if (!p.leaf()) for (int i = 0; i <= p.n; i++) nextLevel.add(p.kids[i]);
                }
                out.add(lj.toString());
                level = nextLevel;
            }
            return out.toString();
        }
    }

    public static void main(String[] args) {
        // ---- 1. a small tree --------------------------------------------------------------------------------------------
        BTree small = new BTree(2);
        small.logging = true;
        long[] order = {20, 40, 10, 30, 15, 35, 7, 26, 18, 22, 5, 42, 13, 46, 27, 8, 32, 38, 24, 45, 28};
        StringJoiner steps = new StringJoiner(" ; ");
        for (long x : order) {
            small.log.clear();
            small.insert(x);
            if (!small.log.isEmpty()) steps.add("insert " + x + ": " + String.join(", ", small.log));
        }
        small.verify();
        check(small.height() == 3 && small.size == order.length, "the small tree");
        System.out.printf("small: pages of 2 to 4 keys (k = 2) ; keys inserted in the order %s ; %s ; the tree, level by level: %s ; %d splits, height %d%n",
                Arrays.toString(order).replace(",", "").replace("[", "").replace("]", ""), steps, small.levels(), small.splits, small.height());

        // ---- 2. a million keys ------------------------------------------------------------------------------------------
        int n = 1_000_000;
        long[] keys = new long[n];
        HashSet<Long> distinct = new HashSet<>();
        for (int i = 0; i < n; ) { long x = next() % 1_000_000_000_000L; if (distinct.add(x)) keys[i++] = x; }
        long[] probes = new long[100_000];
        for (int i = 0; i < probes.length; i++) probes[i] = (i % 2 == 0) ? keys[(int) (next() % n)] : next() % 1_000_000_000_000L;
        StringJoiner mj = new StringJoiner(" ; ");
        int binaryHeight = 64 - Long.numberOfLeadingZeros(n);       // levels of a perfectly balanced binary tree
        BTree big100 = null;
        int[] ks = {2, 10, 50, 200};
        List<long[]> heights = new ArrayList<>();
        for (int k : ks) {
            BTree t = new BTree(k);
            for (long x : keys) check(t.insert(x), "insert");
            long[] pk = t.verify();
            check(pk[1] == n, "all keys present");
            t.reads = 0;
            int hits = 0;
            for (long x : probes) if (t.contains(x)) hits++;
            check(hits >= probes.length / 2, "the stored half is found");
            double perSearch = (double) t.reads / probes.length;
            mj.add(String.format("pages of %d to %d keys: height %d, %.2f pages read per search, %,d pages, %.0f%% full", k, 2 * k, t.height(), perSearch, pk[0], 100.0 * n / (pk[0] * 2.0 * k)));
            heights.add(new long[]{k, n, t.height()});
            if (k == 50) big100 = t;
        }
        System.out.printf("million: %,d random keys, 100,000 searches (half for keys present) ; a perfectly balanced binary tree has %d levels ; %s%n", n, binaryHeight, mj);

        // ---- 3. how full ----------------------------------------------------------------------------------------------
        BTree sorted = new BTree(50);
        long[] sortedKeys = keys.clone();
        Arrays.sort(sortedKeys);
        for (long x : sortedKeys) sorted.insert(x);
        long[] ps = sorted.verify();
        long[] pr = big100.verify();
        double fillRandom = 100.0 * n / (pr[0] * 100.0), fillSorted = 100.0 * n / (ps[0] * 100.0);
        check(fillSorted < fillRandom && Math.abs(fillSorted - 50) < 1.5, "sorted insertion leaves pages half full");
        heights.add(new long[]{50, n, sorted.height()});
        System.out.printf("fill: pages of 50 to 100 keys ; keys inserted in random order: %,d pages, %.1f%% full on average ; the same keys inserted in sorted order: %,d pages, %.1f%% full, since every split leaves a half-full page behind that never receives another key ; height %d and %d%n",
                pr[0], fillRandom, ps[0], fillSorted, big100.height(), sorted.height());

        // ---- 4. deletion ----------------------------------------------------------------------------------------------
        long[] shuffled = keys.clone();
        for (int i = n - 1; i > 0; i--) { int j = (int) (next() % (i + 1)); long t = shuffled[i]; shuffled[i] = shuffled[j]; shuffled[j] = t; }
        HashSet<Long> gone = new HashSet<>();
        big100.borrows = big100.merges = 0;
        for (int i = 0; i < n / 2; i++) { check(big100.delete(shuffled[i]), "delete " + shuffled[i]); gone.add(shuffled[i]); }
        long[] after = big100.verify();
        check(after[1] == n - n / 2 && big100.size == n - n / 2, "half left");
        int right = 0;
        for (long x : keys) if (big100.contains(x) != gone.contains(x)) right++;
        check(right == n, "every search right after deletions");
        check(!big100.delete(shuffled[0]), "a deleted key cannot be deleted again");
        heights.add(new long[]{50, n - n / 2, big100.height()});
        System.out.printf("delete: %,d of the keys deleted in random order from the tree of pages of 50 to 100 ; %,d borrows from a neighbour, %,d merges ; afterwards every page still holds 50 to 100 keys (the root 1 to 100), every leaf is at depth %d, and all %,d searches (for deleted and kept keys) answer correctly ; %,d pages, %.1f%% full%n",
                n / 2, big100.borrows, big100.merges, big100.height(), n, after[0], 100.0 * after[1] / (after[0] * 100.0));

        // ---- 5. bounds --------------------------------------------------------------------------------------------------
        // With pages of k to 2k keys, n keys need a height h with  log_(2k+1)(n+1) <= h <= 1 + log_(k+1)((n+1)/2).
        heights.add(new long[]{2, order.length, small.height()});
        StringJoiner bj = new StringJoiner(" ; ");
        for (long[] hk : heights) {
            double lo = Math.log(hk[1] + 1) / Math.log(2 * hk[0] + 1), hi = 1 + Math.log((hk[1] + 1) / 2.0) / Math.log(hk[0] + 1);
            check(hk[2] >= lo - 1e-9 && hk[2] <= hi + 1e-9, "height within bounds");
            bj.add(String.format("k=%d, n=%,d: %.2f <= %d <= %.2f", hk[0], hk[1], lo, hk[2], hi));
        }
        System.out.printf("bounds: height h of a tree of n keys in pages of k to 2k keys: log(n+1)/log(2k+1) <= h <= 1 + log((n+1)/2)/log(k+1) ; %s%n", bj);

        System.out.println("BTrees: " + passed + " checks passed");
    }
}
