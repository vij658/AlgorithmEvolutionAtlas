import java.math.BigInteger;
import java.util.*;

/**
 * Era 5, topic 13: Edmonds's matching algorithm and the idea of a "good" algorithm (1965).
 *
 * HOW IT WORKS
 *   A matching pairs up vertices of a graph along its edges, each vertex in at most one pair. Berge (1957): a matching
 *   is as large as possible exactly when there is no augmenting path, a path that starts and ends at unpaired
 *   vertices and alternates between edges outside and inside the matching; swapping the edges along such a path adds
 *   one pair. So: search for an augmenting path, swap, repeat. The search grows a tree from an unpaired vertex,
 *   labelling vertices "outer" (an even number of steps from the root) and "inner" (odd). In a graph with odd cycles
 *   the search can label a vertex inner when another way round the cycle would have made it outer, and then miss the
 *   path. Edmonds's remedy: when two outer vertices are joined, they close an odd cycle, a "blossom"; shrink the
 *   whole blossom to a single outer vertex and carry on. Every vertex of the blossom can then be reached as outer.
 *   The work is bounded by a polynomial in the number of vertices; Edmonds called such algorithms "good", against
 *   the obvious method of trying every matching, whose number grows faster than any power.
 *
 * WHAT THIS PROGRAM DOES
 *   1. An 8-vertex graph with a 5-cycle where the search without blossoms misses the augmenting path, and Edmonds's
 *      search finds it.
 *   2. Edmonds's algorithm against trying every matching, on 20,000 random graphs of up to 12 vertices.
 *   3. Counting: the number of matchings of a complete graph against the steps of Edmonds's algorithm.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Matching.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Matching {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static int n;
    static List<List<Integer>> g;
    static int[] match, p, base, queue;
    static boolean[] used, blossom;
    static boolean shrinkBlossoms = true;
    static long steps, blossomsShrunk;

    static void graph(int vertices) {
        n = vertices;
        g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        match = new int[n];
        Arrays.fill(match, -1);
        p = new int[n];
        base = new int[n];
        queue = new int[n];
        used = new boolean[n];
        blossom = new boolean[n];
    }

    static void edge(int a, int b) { g.get(a).add(b); g.get(b).add(a); }

    /** The first common base on the tree paths from a and b to the root. */
    static int lca(int a, int b) {
        boolean[] seen = new boolean[n];
        while (true) { a = base[a]; seen[a] = true; if (match[a] == -1) break; a = p[match[a]]; }
        while (true) { b = base[b]; if (seen[b]) return b; b = p[match[b]]; }
    }

    static void markPath(int v, int b, int child) {
        while (base[v] != b) {
            blossom[base[v]] = blossom[base[match[v]]] = true;
            p[v] = child;
            child = match[v];
            v = p[match[v]];
        }
    }

    /** Grow the alternating tree from root; return an unpaired vertex reached as outer's neighbour, or -1. */
    static int findPath(int root) {
        Arrays.fill(used, false);
        Arrays.fill(p, -1);
        for (int i = 0; i < n; i++) base[i] = i;
        used[root] = true;
        int head = 0, tail = 0;
        queue[tail++] = root;
        while (head < tail) {
            int v = queue[head++];
            for (int to : g.get(v)) {
                steps++;
                if (base[v] == base[to] || match[v] == to) continue;
                if (to == root || (match[to] != -1 && p[match[to]] != -1)) {
                    // v and to are both outer: an odd cycle
                    if (!shrinkBlossoms) continue;
                    int cur = lca(v, to);
                    Arrays.fill(blossom, false);
                    markPath(v, cur, to);
                    markPath(to, cur, v);
                    blossomsShrunk++;
                    for (int i = 0; i < n; i++)
                        if (blossom[base[i]]) {
                            base[i] = cur;
                            if (!used[i]) { used[i] = true; queue[tail++] = i; }
                        }
                } else if (p[to] == -1) {
                    p[to] = v;
                    if (match[to] == -1) return to;
                    used[match[to]] = true;
                    queue[tail++] = match[to];
                }
            }
        }
        return -1;
    }

    static int augmentFrom(int root) {
        int u = findPath(root);
        if (u == -1) return 0;
        while (u != -1) { int pv = p[u], ppv = match[pv]; match[u] = pv; match[pv] = u; u = ppv; }
        return 1;
    }

    static int maximum() {
        int size = 0;
        for (int v = 0; v < n; v++) if (match[v] == -1) size += augmentFrom(v);
        for (int v = 0; v < n; v++) if (match[v] != -1) check(match[match[v]] == v && g.get(v).contains(match[v]), "a valid matching");
        return size;
    }

    // ---- trying every matching -----------------------------------------------------------------------------------------
    static long tried;

    static int brute(boolean[][] adj, boolean[] taken, int v) {
        while (v < n && taken[v]) v++;
        if (v == n) { tried++; return 0; }
        taken[v] = true;
        int best = brute(adj, taken, v + 1);                       // v stays unpaired
        for (int u = v + 1; u < n; u++)
            if (adj[v][u] && !taken[u]) { taken[u] = true; best = Math.max(best, 1 + brute(adj, taken, v + 1)); taken[u] = false; }
        taken[v] = false;
        return best;
    }

    static long seed = 1965L;

    static int rnd(int k) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % k);
    }

    public static void main(String[] args) {
        // ---- 1. the flower ---------------------------------------------------------------------------------------------
        int[][] edges = {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 5}, {5, 6}, {6, 2}, {3, 7}};
        int[][] pairs = {{1, 2}, {3, 4}, {5, 6}};
        int[] results = new int[2];
        String path = "";
        for (int version = 0; version < 2; version++) {
            graph(8);
            for (int[] e : edges) edge(e[0], e[1]);
            for (int[] m : pairs) { match[m[0]] = m[1]; match[m[1]] = m[0]; }
            shrinkBlossoms = version == 1;
            blossomsShrunk = 0;
            int found = findPath(0);
            if (found != -1) {
                StringJoiner pj = new StringJoiner(" ");
                List<Integer> rev = new ArrayList<>();
                for (int u = found; u != -1; ) { rev.add(u); int pv = p[u]; rev.add(pv); u = match[pv]; if (pv == 0) break; }
                Collections.reverse(rev);
                for (int v : rev) pj.add(String.valueOf(v));
                path = pj.toString();
                int u = found;
                while (u != -1) { int pv = p[u], ppv = match[pv]; match[u] = pv; match[pv] = u; u = ppv; }
            }
            int size = 0;
            for (int v = 0; v < 8; v++) if (match[v] > v) size++;
            results[version] = size;
        }
        shrinkBlossoms = true;
        check(results[0] == 3 && results[1] == 4, "the blossom makes the difference");
        System.out.printf("flower: 8 vertices, edges 0-1 1-2 2-3 3-4 4-5 5-6 6-2 3-7 (2 3 4 5 6 is a 5-cycle), pairs 1-2 3-4 5-6 to start, 0 and 7 unpaired ; searching from 0 without blossoms: vertex 3 is reached as inner (0 1 2 3), the path is missed and the matching stays at %d pairs ; with Edmonds's shrinking the cycle 2 3 4 5 6 becomes one outer vertex, the path %s is found, and the matching grows to %d pairs%n",
                results[0], path, results[1]);

        // ---- 2. random graphs against brute force --------------------------------------------------------------------------
        int graphs = 20000;
        long bruteTried = 0, edmondsSteps = 0, shrunk = 0;
        for (int t = 0; t < graphs; t++) {
            int vn = 2 + rnd(11);
            graph(vn);
            boolean[][] adj = new boolean[vn][vn];
            int density = 1 + rnd(4);
            for (int a = 0; a < vn; a++)
                for (int b = a + 1; b < vn; b++)
                    if (rnd(6) < density) { edge(a, b); adj[a][b] = adj[b][a] = true; }
            steps = 0;
            blossomsShrunk = 0;
            int e = maximum();
            edmondsSteps += steps;
            shrunk += blossomsShrunk;
            tried = 0;
            int b = brute(adj, new boolean[vn], 0);
            bruteTried += tried;
            check(e == b, "Edmonds equals brute force on graph " + t);
        }
        System.out.printf("random: %,d random graphs of 2 to 12 vertices ; Edmonds's algorithm found a matching as large as the best of all matchings every time ; %,d blossoms shrunk along the way ; trying every matching looked at %,d matchings in all, Edmonds's searches %,d edge-steps%n",
                graphs, shrunk, bruteTried, edmondsSteps);

        // ---- 3. counting -------------------------------------------------------------------------------------------------
        // matchings of the complete graph K_n (the telephone numbers): T(n) = T(n-1) + (n-1) T(n-2)
        BigInteger[] tel = new BigInteger[401];
        tel[0] = BigInteger.ONE;
        tel[1] = BigInteger.ONE;
        for (int k = 2; k <= 400; k++) tel[k] = tel[k - 1].add(BigInteger.valueOf(k - 1).multiply(tel[k - 2]));
        // check the recurrence against brute force for small complete graphs
        for (int k = 1; k <= 10; k++) {
            graph(k);
            boolean[][] adj = new boolean[k][k];
            for (int a = 0; a < k; a++) for (int b = a + 1; b < k; b++) adj[a][b] = adj[b][a] = true;
            tried = 0;
            brute(adj, new boolean[k], 0);
            check(BigInteger.valueOf(tried).equals(tel[k]), "telephone number " + k);
        }
        StringJoiner cj = new StringJoiner(" ; ");
        for (int k : new int[]{10, 20, 50, 100, 200, 400}) {
            graph(k);
            // a random graph with about a third of all possible edges
            for (int a = 0; a < k; a++) for (int b = a + 1; b < k; b++) if (rnd(3) == 0) edge(a, b);
            steps = 0;
            int m = maximum();
            String count = tel[k].toString();
            String shown = count.length() <= 12 ? String.format("%,d", tel[k]) : String.format("about %s.%s x 10^%d", count.charAt(0), count.substring(1, 3), count.length() - 1);
            cj.add(String.format("%d vertices: matchings of the complete graph %s ; Edmonds on a random graph with a third of the edges: %,d steps, %d pairs", k, shown, steps, m));
        }
        System.out.printf("growth: %s ; the count of matchings grows faster than any power of n, the steps of the search like a small power%n", cj);

        System.out.println("Matching: " + passed + " checks passed");
    }
}
