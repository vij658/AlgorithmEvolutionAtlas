import java.util.*;

/**
 * Era 7, topic 5: splay trees and amortized analysis (Sleator and Tarjan, AT&T Bell Laboratories, 1985).
 *
 * HOW IT WORKS
 *   A binary search tree finds a key by walking down from the root, left if smaller, right if larger. Balanced trees
 *   (Era 5) keep every path short by storing extra information and following rules after each change. A splay tree
 *   stores nothing extra. Instead, every time a key is touched, it is "splayed": rotated up to the root, two levels
 *   at a time (the zig-zig and zig-zag steps), which also roughly halves the depth of every node on the way. One
 *   access can still be slow, but Sleator and Tarjan proved that any sequence of m accesses takes O(m log n) in all:
 *   the cost is "amortized", averaged over the worst possible sequence. The proof gives the tree a potential, the sum
 *   of log2(size of each subtree): a slow access always lowers the potential, which pays for it. Frequently used
 *   keys stay near the root, so on skewed workloads a splay tree is as good as the best fixed tree for those
 *   frequencies, without knowing them.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The access lemma, checked on every one of 1,000,000 splays: rotations + change in potential
 *      <= 3 (log2 n - log2 size(x)) + 1.
 *   2. Keys inserted in sorted order and then read in order: a plain search tree, a splay tree, a balanced tree.
 *   3. Skewed (Zipf) accesses: the splay tree against a perfectly balanced tree and the optimal fixed tree for the
 *      true frequencies (Knuth's dynamic programme, 1971).
 *   4. Working sets: repeatedly using a few keys out of 100,000 costs about log2 of the few, not of 100,000.
 *   5. Tarjan's simplest example of amortization: a stack where one operation may pop many items.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SplayTrees.java
 *   Expected output: expected-output.txt in this folder.
 */
public class SplayTrees {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1985L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int below(int k) { return (int) (uniform() * k); }

    // ---- the splay tree: nodes are the keys 0..n-1 themselves; -1 means "none" -----------------------------------------
    static class Splay {
        final int[] left, right, parent, size;
        int root = -1;
        long rotations, visited;
        double potential;              // sum over nodes of log2(size)
        boolean trackPotential;

        Splay(int n) {
            left = new int[n]; right = new int[n]; parent = new int[n]; size = new int[n];
            Arrays.fill(left, -1); Arrays.fill(right, -1); Arrays.fill(parent, -1);
        }

        int sz(int x) { return x < 0 ? 0 : size[x]; }

        static double lg(int s) { return Math.log(s) / Math.log(2); }

        /** Rotates x above its parent, keeping sizes (and the potential) up to date. */
        void rotate(int x) {
            int p = parent[x], g = parent[p];
            if (trackPotential) potential -= lg(size[x]) + lg(size[p]);
            if (left[p] == x) {
                left[p] = right[x]; if (right[x] >= 0) parent[right[x]] = p;
                right[x] = p;
            } else {
                right[p] = left[x]; if (left[x] >= 0) parent[left[x]] = p;
                left[x] = p;
            }
            parent[p] = x;
            parent[x] = g;
            if (g >= 0) { if (left[g] == p) left[g] = x; else right[g] = x; } else root = x;
            size[p] = 1 + sz(left[p]) + sz(right[p]);
            size[x] = 1 + sz(left[x]) + sz(right[x]);
            if (trackPotential) potential += lg(size[x]) + lg(size[p]);
            rotations++;
        }

        void splay(int x) {
            while (parent[x] >= 0) {
                int p = parent[x], g = parent[p];
                if (g < 0) rotate(x);                                                 // zig
                else if ((left[g] == p) == (left[p] == x)) { rotate(p); rotate(x); }  // zig-zig
                else { rotate(x); rotate(x); }                                        // zig-zag
            }
        }

        /** Finds key k (which must be present), counting the nodes visited, then splays it. */
        void access(int k) {
            int x = root;
            while (x != k) { visited++; x = k < x ? left[x] : right[x]; }
            visited++;
            splay(x);
        }

        void insert(int k) {
            size[k] = 1;
            if (root < 0) { root = k; return; }                // log2(1) = 0: a single node adds no potential
            int x = root, p = -1;
            while (x >= 0) { visited++; p = x; x = k < x ? left[x] : right[x]; }
            parent[k] = p;
            if (k < p) left[p] = k; else right[p] = k;
            for (int a = p; a >= 0; a = parent[a]) { if (trackPotential) potential -= lg(size[a]); size[a]++; if (trackPotential) potential += lg(size[a]); }
            splay(k);
        }
    }

    // ---- a plain (unbalanced) binary search tree --------------------------------------------------------------------
    static class Plain {
        final int[] left, right;
        int root = -1;
        long visited;

        Plain(int n) { left = new int[n]; right = new int[n]; Arrays.fill(left, -1); Arrays.fill(right, -1); }

        void insert(int k) {
            if (root < 0) { root = k; return; }
            int x = root;
            while (true) {
                visited++;
                if (k < x) { if (left[x] < 0) { left[x] = k; return; } x = left[x]; }
                else { if (right[x] < 0) { right[x] = k; return; } x = right[x]; }
            }
        }

        void access(int k) { int x = root; while (x != k) { visited++; x = k < x ? left[x] : right[x]; } visited++; }
    }

    /** Depth (root = 1) of key k in a perfectly balanced tree over 0..n-1. */
    static int balancedDepth(int k, int lo, int hi) {
        int d = 1;
        while (true) { int mid = (lo + hi) >>> 1; if (k == mid) return d; if (k < mid) hi = mid - 1; else lo = mid + 1; d++; }
    }

    /** Knuth's O(n^2) dynamic programme: the expected number of nodes visited in the optimal fixed tree. */
    static double optimalStatic(double[] p) {
        int n = p.length;
        double[][] cost = new double[n + 1][n + 1];
        int[][] root = new int[n + 1][n + 1];
        double[] prefix = new double[n + 1];
        for (int i = 0; i < n; i++) prefix[i + 1] = prefix[i] + p[i];
        for (int i = 0; i < n; i++) { cost[i][i + 1] = p[i]; root[i][i + 1] = i; }
        for (int len = 2; len <= n; len++)
            for (int i = 0; i + len <= n; i++) {
                int j = i + len;
                double best = Double.MAX_VALUE;
                int arg = -1;
                for (int r = root[i][j - 1]; r <= root[i + 1][j]; r++) {   // Knuth: the best root moves monotonically
                    double c = cost[i][r] + cost[r + 1][j];
                    if (c < best) { best = c; arg = r; }
                }
                cost[i][j] = best + prefix[j] - prefix[i];
                root[i][j] = arg;
            }
        return cost[0][n];
    }

    public static void main(String[] args) {
        // ---- 1. the access lemma on every splay ---------------------------------------------------------------------
        int n = 10_000;
        Splay s = new Splay(n);
        s.trackPotential = true;
        int[] order = new int[n];
        for (int i = 0; i < n; i++) order[i] = i;
        for (int i = n - 1; i > 0; i--) { int j = below(i + 1); int t = order[i]; order[i] = order[j]; order[j] = t; }
        for (int k : order) s.insert(k);
        long ops = 1_000_000, totalRot = 0;
        double totalBound = 0, slack = Double.MAX_VALUE;
        for (long t = 0; t < ops; t++) {
            int k = below(n);
            int x = s.root;
            while (x != k) x = k < x ? s.left[x] : s.right[x];
            double rBefore = Splay.lg(s.size[s.root]) - Splay.lg(s.size[k]);
            double phi0 = s.potential;
            long r0 = s.rotations;
            s.splay(k);
            long rot = s.rotations - r0;
            double actual = Math.max(rot, 1);
            double amortized = actual + (s.potential - phi0);
            double bound = 3 * rBefore + 1;
            check(amortized <= bound + 1e-9, "the access lemma");
            slack = Math.min(slack, bound - amortized);
            totalRot += rot;
            totalBound += bound;
        }
        // the potential is a sum of logs, so it stays between 0 and n log2 n
        double fresh = 0;
        for (int i = 0; i < n; i++) fresh += Splay.lg(s.size[i]);
        check(Math.abs(fresh - s.potential) < 1e-6 * fresh, "the running potential matches a fresh count");
        System.out.printf("lemma: %,d random accesses on a splay tree of %,d keys ; for every one, rotations + change in potential <= 3 (log2 n - log2 size(x)) + 1 held (closest margin %.3f) ; total rotations %,d, %.1f per access on average, against an average bound of %.1f from the lemma ; final potential %,.0f of at most n log2 n = %,.0f%n",
                ops, n, slack, totalRot, (double) totalRot / ops, totalBound / ops, s.potential, n * Splay.lg(n));

        // ---- 2. sorted insertions, then read in order -------------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        for (int m : new int[]{1_000, 10_000}) {
            Plain pl = new Plain(m);
            Splay sp = new Splay(m);
            for (int k = 0; k < m; k++) { pl.insert(k); sp.insert(k); }
            long plIns = pl.visited, spIns = sp.visited;
            pl.visited = 0; sp.visited = 0;
            long spRot0 = sp.rotations;
            for (int k = 0; k < m; k++) { pl.access(k); sp.access(k); }
            long bal = 0;
            for (int k = 0; k < m; k++) bal += balancedDepth(k, 0, m - 1);
            check(pl.visited == (long) m * (m + 1) / 2, "the plain tree is a path: 1 + 2 + ... + m");
            check(sp.visited < 6L * m, "splaying in order costs linear time (the scanning theorem)");
            sj.add(String.format("%,d keys: plain tree %,d nodes visited inserting and %,d reading ; splay tree %,d and %,d (%,d rotations reading) ; balanced tree %,d reading",
                    m, plIns, pl.visited, spIns, sp.visited, sp.rotations - spRot0, bal));
        }
        System.out.printf("sorted: insert the keys 1, 2, 3, ... in order, then read them all in order ; %s%n", sj);

        // ---- 3. skewed accesses ---------------------------------------------------------------------------------------
        n = 1000;
        double[] p = new double[n];
        int[] rank = new int[n];
        for (int i = 0; i < n; i++) rank[i] = i;
        for (int i = n - 1; i > 0; i--) { int j = below(i + 1); int t = rank[i]; rank[i] = rank[j]; rank[j] = t; }
        double h = 0;
        for (int i = 0; i < n; i++) h += 1.0 / (i + 1);
        for (int k = 0; k < n; k++) p[k] = 1.0 / (rank[k] + 1) / h;          // key k is the (rank+1)-th most popular
        double[] cum = new double[n];
        for (int k = 0; k < n; k++) cum[k] = (k > 0 ? cum[k - 1] : 0) + p[k];
        double opt = optimalStatic(p);
        double balanced = 0, entropy = 0;
        for (int k = 0; k < n; k++) balanced += p[k] * balancedDepth(k, 0, n - 1);
        for (int k = 0; k < n; k++) entropy -= p[k] * Math.log(p[k]) / Math.log(2);
        Splay z = new Splay(n);
        for (int k : order) if (k < n) z.insert(k);
        int accesses = 1_000_000;
        z.visited = 0;
        for (int t = 0; t < accesses; t++) {
            double u = uniform();
            int lo = 0, hi = n - 1;
            while (lo < hi) { int mid = (lo + hi) >>> 1; if (cum[mid] < u) lo = mid + 1; else hi = mid; }
            z.access(lo);
        }
        double splayAvg = (double) z.visited / accesses;
        check(opt <= balanced, "the optimal fixed tree beats the balanced one");
        check(splayAvg < balanced, "on this skewed workload the splay tree beats the balanced tree");
        check(splayAvg < 2 * opt + 1, "and stays within a small factor of the optimal fixed tree");
        System.out.printf("zipf: %,d keys, the k-th most popular used with probability proportional to 1/k, %,d accesses ; average nodes visited per access: balanced tree %.2f ; optimal fixed tree for the true frequencies %.2f ; splay tree, knowing nothing, %.2f ; entropy of the frequencies %.2f bits%n",
                n, accesses, balanced, opt, splayAvg, entropy);

        // ---- 4. working sets ------------------------------------------------------------------------------------------
        n = 100_000;
        StringJoiner wj = new StringJoiner(" ; ");
        double prev = 0;
        for (int w : new int[]{1, 10, 100, 1_000, 10_000}) {
            Splay ws = new Splay(n);
            int[] ord = new int[n];
            for (int i = 0; i < n; i++) ord[i] = i;
            for (int i = n - 1; i > 0; i--) { int j = below(i + 1); int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
            for (int k : ord) ws.insert(k);
            int[] set = Arrays.copyOf(ord, w);
            for (int t = 0; t < 20 * w; t++) ws.access(set[below(w)]);          // warm up
            ws.visited = 0;
            int acc = 200_000;
            for (int t = 0; t < acc; t++) ws.access(set[below(w)]);
            double avg = (double) ws.visited / acc;
            check(avg >= prev, "bigger working sets cost more");
            prev = avg;
            wj.add(String.format("%,d key%s in use: %.2f nodes per access (log2 = %.1f)", w, w == 1 ? "" : "s", avg, Splay.lg(w)));
        }
        System.out.printf("workingset: a splay tree of %,d keys, but the accesses go only to a few of them, at random ; %s ; a balanced tree would visit about %.0f every time%n",
                n, wj, Splay.lg(n));

        // ---- 5. the multipop stack -----------------------------------------------------------------------------------
        int m = 1_000_000;
        int height = 0, worst = 0;
        long total = 0;
        for (int t = 0; t < m; t++) {
            int pops = uniform() < 0.01 ? below(height + 1) : (uniform() < 0.3 ? Math.min(height, 1) : 0);
            height -= pops;
            height++;                                  // then one push
            total += pops + 1;
            worst = Math.max(worst, pops + 1);
        }
        check(total <= 2L * m, "at most 2m pushes and pops in m operations");
        System.out.printf("stack: %,d operations, each some pops followed by one push ; the slowest single operation did %,d pushes and pops, but all of them together did %,d, under the 2m = %,d that the amortized argument promises: every item is popped at most once after it is pushed%n",
                m, worst, total, 2L * m);

        System.out.println("SplayTrees: " + passed + " checks passed");
    }
}
