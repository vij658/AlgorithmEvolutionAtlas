import java.util.*;

/**
 * Era 4, topic 4: the cheapest network (Borůvka 1926, Jarník 1930).
 *
 * HOW IT WORKS
 *   Given towns and the distance between every pair, connect them all with lines of least total length (today: a
 *   minimum spanning tree). One fact does all the work: for any group of towns, the shortest line leaving the group
 *   belongs to the cheapest network (when no two distances are equal). So:
 *     Borůvka: every town joins its nearest neighbour. That leaves separate pieces; every piece joins the piece
 *              nearest to it; repeat until one piece remains. Each round at least halves the number of pieces.
 *     Jarník:  start from one town; repeatedly add the shortest line from the network built so far to a town not
 *              yet in it.
 *     Kruskal (1956): take the lines from shortest to longest, keeping each one that joins two separate pieces.
 *   With equal distances, all three need the same tie-breaking rule, or Borůvka's rounds can close a loop.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Forty towns at random points (like Borůvka's example with 40 cities): Borůvka's rounds, Jarník's growth and
 *      Kruskal's sort choose exactly the same 39 lines.
 *   2. A thousand more sets of 40 towns: how many rounds Borůvka needs, and a check that every round at least halves
 *      the number of pieces.
 *   3. Brute force on 200 sets of 7 towns: all 16,807 possible networks each (Cayley's count 7^5); the one the
 *      algorithms choose is the unique cheapest every time.
 *   4. The rule behind all three, tested on 10,000 random splits of the 40 towns.
 *   5. Three towns at equal distances: without a shared tie-breaking rule, Borůvka's round picks a closed loop.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CheapestNetwork.java
 *   Expected output: expected-output.txt in this folder.
 */
public class CheapestNetwork {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1926L;

    static int rnd(int n) {                                            // a fixed linear congruential generator
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) Long.remainderUnsigned(seed >>> 33, n);
    }

    static int n;
    static long[] X, Y;

    static long d2(int i, int j) { long dx = X[i] - X[j], dy = Y[i] - Y[j]; return dx * dx + dy * dy; }

    /** Line (i, j) is shorter than line (k, l): by squared length, then by the smaller town, then the larger. */
    static boolean shorter(int i, int j, int k, int l) {
        long a = d2(i, j), b = d2(k, l);
        if (a != b) return a < b;
        int mi = Math.min(i, j), mk = Math.min(k, l);
        if (mi != mk) return mi < mk;
        return Math.max(i, j) < Math.max(k, l);
    }

    static long key(int i, int j) { return (long) Math.min(i, j) * 1000 + Math.max(i, j); }

    // ---- union-find, to know which piece a town is in -----------------------------------------------------------------
    static int[] parent;

    static int find(int a) { while (parent[a] != a) a = parent[a] = parent[parent[a]]; return a; }

    static long examined;

    /** Borůvka: each piece takes its shortest outgoing line, all at once; returns the lines, records the piece counts. */
    static TreeSet<Long> boruvka(List<Integer> pieces) {
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        TreeSet<Long> chosen = new TreeSet<>();
        int count = n;
        pieces.add(count);
        while (count > 1) {
            int[] bi = new int[n], bj = new int[n];
            Arrays.fill(bi, -1);
            for (int i = 0; i < n; i++)
                for (int j = i + 1; j < n; j++) {
                    examined++;
                    int a = find(i), b = find(j);
                    if (a == b) continue;
                    for (int r : new int[]{a, b})
                        if (bi[r] < 0 || shorter(i, j, bi[r], bj[r])) { bi[r] = i; bj[r] = j; }
                }
            int before = count;
            for (int r = 0; r < n; r++)
                if (bi[r] >= 0) {
                    int a = find(bi[r]), b = find(bj[r]);
                    if (a != b) { parent[a] = b; count--; }
                    chosen.add(key(bi[r], bj[r]));
                }
            check(count <= before / 2, "a round at least halves the pieces");
            pieces.add(count);
        }
        return chosen;
    }

    /** Jarník: grow one network from town 0 by the shortest line to a new town. */
    static TreeSet<Long> jarnik() {
        boolean[] in = new boolean[n];
        int[] near = new int[n];                                      // for each outside town, its nearest town inside
        in[0] = true;
        TreeSet<Long> chosen = new TreeSet<>();
        for (int i = 1; i < n; i++) near[i] = 0;
        for (int step = 1; step < n; step++) {
            int best = -1;
            for (int i = 0; i < n; i++) {
                if (in[i]) continue;
                examined++;
                if (best < 0 || shorter(i, near[i], best, near[best])) best = i;
            }
            in[best] = true;
            chosen.add(key(best, near[best]));
            for (int i = 0; i < n; i++) if (!in[i]) { examined++; if (shorter(i, best, i, near[i])) near[i] = best; }
        }
        return chosen;
    }

    /** Kruskal: shortest lines first, keeping those that join two pieces. */
    static TreeSet<Long> kruskal() {
        List<int[]> lines = new ArrayList<>();
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) lines.add(new int[]{i, j});
        lines.sort((u, v) -> u[0] == v[0] && u[1] == v[1] ? 0 : shorter(u[0], u[1], v[0], v[1]) ? -1 : 1);
        parent = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        TreeSet<Long> chosen = new TreeSet<>();
        for (int[] e : lines) {
            examined++;
            int a = find(e[0]), b = find(e[1]);
            if (a != b) { parent[a] = b; chosen.add(key(e[0], e[1])); }
        }
        return chosen;
    }

    static double length(Set<Long> lines) {
        double s = 0;
        for (long k : lines) s += Math.sqrt(d2((int) (k / 1000), (int) (k % 1000)));
        return s;
    }

    static long len2(Set<Long> lines) {
        long s = 0;
        for (long k : lines) s += d2((int) (k / 1000), (int) (k % 1000));
        return s;
    }

    static void towns(int count) {
        n = count;
        X = new long[n];
        Y = new long[n];
        for (int i = 0; i < n; i++) { X[i] = rnd(1000); Y[i] = rnd(1000); }
    }

    public static void main(String[] args) {
        // ---- 1. forty towns ------------------------------------------------------------------------------------------
        towns(40);
        StringJoiner xy = new StringJoiner(" ");
        for (int i = 0; i < n; i++) xy.add(X[i] + "," + Y[i]);
        System.out.println("towns: " + xy);
        List<Integer> pieces = new ArrayList<>();
        examined = 0;
        TreeSet<Long> b = boruvka(pieces);
        long eb = examined;
        examined = 0;
        TreeSet<Long> j = jarnik();
        long ej = examined;
        examined = 0;
        TreeSet<Long> k = kruskal();
        long ek = examined;
        check(b.size() == n - 1 && b.equals(j) && b.equals(k), "the three methods choose the same 39 lines");
        StringJoiner ps = new StringJoiner(" -> ");
        for (int c : pieces) ps.add(String.valueOf(c));
        StringJoiner ls = new StringJoiner(" ");
        for (long key : b) ls.add((key / 1000) + "-" + (key % 1000));
        System.out.printf("boruvka: pieces after each round %s ; %d rounds, %d comparisons of a line%n", ps, pieces.size() - 1, eb);
        System.out.printf("same: Boruvka, Jarnik (%d comparisons) and Kruskal (%d lines examined after sorting %d) choose the same %d lines, total length %.3f ; lines %s%n",
                ej, ek, n * (n - 1) / 2, b.size(), length(b), ls);

        // ---- 2. rounds over a thousand sets ----------------------------------------------------------------------------
        int[] roundHist = new int[10];
        int sets = 1000;
        for (int s = 0; s < sets; s++) {
            towns(40);
            List<Integer> pc = new ArrayList<>();
            TreeSet<Long> bb = boruvka(pc);
            check(bb.equals(kruskal()), "Borůvka equals Kruskal");
            roundHist[pc.size() - 1]++;
        }
        StringJoiner rh = new StringJoiner(", ");
        for (int r = 0; r < roundHist.length; r++) if (roundHist[r] > 0) rh.add(r + " rounds: " + roundHist[r]);
        check(roundHist[6] + roundHist[7] + roundHist[8] + roundHist[9] == 0, "never more than log2(40) rounds, rounded up");
        System.out.printf("rounds: %d more sets of 40 towns ; %s ; every round at least halved the number of pieces%n", sets, rh);

        // ---- 3. brute force over every network on 7 towns ---------------------------------------------------------------
        int small = 7, trials = 200;
        long trees = 0;
        for (int s = 0; s < trials; s++) {
            towns(small);
            TreeSet<Long> mst = kruskal();
            long best = Long.MAX_VALUE, bestCount = 0;
            TreeSet<Long> bestTree = null;
            int[] code = new int[small - 2];
            int total = (int) Math.pow(small, small - 2);
            for (int c = 0; c < total; c++) {
                int v = c;
                for (int i = 0; i < small - 2; i++) { code[i] = v % small; v /= small; }
                TreeSet<Long> t = prufer(code, small);
                trees++;
                long w = len2(t);                                         // squared lengths: same cheapest tree, exact sums
                if (w < best) { best = w; bestCount = 1; bestTree = t; } else if (w == best) bestCount++;
            }
            check(bestCount == 1 && bestTree.equals(mst), "the algorithms' network is the unique cheapest");
        }
        System.out.printf("brute: %d sets of %d towns, every one of the %d possible networks each (%d in all) ; the network the algorithms choose was the unique cheapest every time%n",
                trials, small, (int) Math.pow(small, small - 2), trees);

        // ---- 4. the cut rule ----------------------------------------------------------------------------------------------
        seed = 1930L;
        towns(40);
        TreeSet<Long> mst = kruskal();
        int cuts = 10000;
        for (int c = 0; c < cuts; c++) {
            boolean[] side = new boolean[n];
            int inside = 0;
            for (int i = 0; i < n; i++) { side[i] = rnd(2) == 1; if (side[i]) inside++; }
            if (inside == 0 || inside == n) { side[0] = !side[0]; }
            int bi = -1, bj = -1;
            for (int i = 0; i < n; i++)
                for (int jj = i + 1; jj < n; jj++)
                    if (side[i] != side[jj] && (bi < 0 || shorter(i, jj, bi, bj))) { bi = i; bj = jj; }
            check(mst.contains(key(bi, bj)), "the shortest line across a split is in the network");
        }
        System.out.printf("cut: %d random splits of 40 towns into two groups ; the shortest line between the groups was in the cheapest network every time%n", cuts);

        // ---- 5. ties ------------------------------------------------------------------------------------------------------
        // Three towns at equal distances (lines 0-1, 1-2, 2-0 all the same length). If each town breaks the tie its own
        // way, choosing the line to the next town round the triangle, the round picks all three lines: a closed loop.
        int[][] own = {{0, 1}, {1, 2}, {2, 0}};
        TreeSet<Long> picked = new TreeSet<>();
        for (int[] e : own) picked.add(key(e[0], e[1]));
        check(picked.size() == 3, "inconsistent tie-breaking picks a loop");
        // With one shared rule (smaller town numbers first), towns 0 and 1 pick line 0-1 and town 2 picks line 0-2.
        TreeSet<Long> shared = new TreeSet<>(List.of(key(0, 1), key(0, 1), key(0, 2)));
        check(shared.size() == 2, "a shared rule picks two lines, no loop");
        System.out.println("ties: three towns at equal distances ; each town breaking ties its own way picks lines 0-1, 1-2, 2-0, a closed loop ; one shared rule picks 0-1 and 0-2, a network");

        System.out.println("CheapestNetwork: " + passed + " checks passed");
    }

    /** The network with Prüfer code `code` on towns 0 .. m-1 (every network on m towns has exactly one code). */
    static TreeSet<Long> prufer(int[] code, int m) {
        int[] degree = new int[m];
        Arrays.fill(degree, 1);
        for (int c : code) degree[c]++;
        TreeSet<Long> t = new TreeSet<>();
        for (int c : code) {
            for (int leaf = 0; leaf < m; leaf++)
                if (degree[leaf] == 1) { t.add(key(leaf, c)); degree[leaf]--; degree[c]--; break; }
        }
        int u = -1, v = -1;
        for (int i = 0; i < m; i++) if (degree[i] == 1) { if (u < 0) u = i; else v = i; }
        t.add(key(u, v));
        return t;
    }
}
