import java.util.*;

/**
 * Entry 32 of the principles catalog (Part 2): Breadth-first and depth-first search
 *
 * HOW IT WORKS
 *   Breadth-first search explores in layers with a queue and gives shortest paths in unweighted graphs; depth-
 *   first search goes deep with a stack (or recursion) and exposes structure such as cycles and connected
 *   components.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BfsAndDfs.java
 *   Expected: the output in expected-output.txt, ending "BfsAndDfs: 357918 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class BfsAndDfs {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final long INF = Long.MAX_VALUE / 4;

    // ---------- shared graph helpers ----------
    static List<List<Integer>> undirected(int n, int[][] edges) {
        List<List<Integer>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) { g.get(e[0]).add(e[1]); g.get(e[1]).add(e[0]); }
        return g;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int[] bfsDistances(List<List<Integer>> g, int src) {
        int[] dist = new int[g.size()];
        Arrays.fill(dist, -1);
        ArrayDeque<Integer> q = new ArrayDeque<>();
        dist[src] = 0;
        q.add(src);
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : g.get(u))
                if (dist[v] < 0) { dist[v] = dist[u] + 1; q.add(v); }
        }
        return dist;
    }

    static int components(List<List<Integer>> g) {          // iterative DFS: safe for very deep graphs
        int count = 0;
        boolean[] seen = new boolean[g.size()];
        ArrayDeque<Integer> stack = new ArrayDeque<>();
        for (int s = 0; s < g.size(); s++) {
            if (seen[s]) continue;
            count++;
            seen[s] = true;
            stack.push(s);
            while (!stack.isEmpty()) {
                int u = stack.pop();
                for (int v : g.get(u))
                    if (!seen[v]) { seen[v] = true; stack.push(v); }
            }
        }
        return count;
    }

    static void dfsRecursive(List<List<Integer>> g, int u, boolean[] seen) {
        seen[u] = true;
        for (int v : g.get(u)) if (!seen[v]) dfsRecursive(g, v, seen);
    }

    static final class DSU {
        final int[] parent, rank;
        int sets;
        DSU(int n) {
            parent = new int[n]; rank = new int[n]; sets = n;
            for (int i = 0; i < n; i++) parent[i] = i;
        }
        int find(int x) {                                   // path halving
            while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
            return x;
        }
        boolean union(int a, int b) {
            int ra = find(a), rb = find(b);
            if (ra == rb) return false;
            if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }
            parent[rb] = ra;                                // attach the shorter tree under the taller one
            if (rank[ra] == rank[rb]) rank[ra]++;
            sets--;
            return true;
        }
    }

    // ----------------------------------------------------------------------------------------------------
    // Shared helpers
    // ----------------------------------------------------------------------------------------------------
    static long[][] floydWarshall(int n, int[][] edges) {
        long[][] d = new long[n][n];
        for (long[] row : d) Arrays.fill(row, INF);
        for (int i = 0; i < n; i++) d[i][i] = 0;
        for (int[] e : edges) d[e[0]][e[1]] = Math.min(d[e[0]][e[1]], e[2]);
        for (int k = 0; k < n; k++)
            for (int i = 0; i < n; i++)
                if (d[i][k] < INF)
                    for (int j = 0; j < n; j++)
                        if (d[k][j] < INF && d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
        return d;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java BfsAndDfs.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 1000; t++) {
            int n = 2 + rnd.nextInt(30);
            int[][] edges = new int[rnd.nextInt(60)][];
            for (int i = 0; i < edges.length; i++) edges[i] = new int[]{rnd.nextInt(n), rnd.nextInt(n), 1};
            List<List<Integer>> g = undirected(n, edges);
            int[][] both = new int[edges.length * 2][];
            for (int i = 0; i < edges.length; i++) { both[2 * i] = edges[i]; both[2 * i + 1] = new int[]{edges[i][1], edges[i][0], 1}; }
            long[][] d = floydWarshall(n, both);
            for (int s = 0; s < n; s++) {
                int[] dist = bfsDistances(g, s);
                for (int v = 0; v < n; v++) check(dist[v] == (d[s][v] >= INF ? -1 : (int) d[s][v]), "BFS equals Floyd-Warshall with unit weights");
            }
            DSU dsu = new DSU(n);
            for (int[] e : edges) dsu.union(e[0], e[1]);
            check(components(g) == dsu.sets, "DFS components equal union-find components");
        }
        int n = 200_000;
        List<List<Integer>> chain = new ArrayList<>();
        for (int i = 0; i < n; i++) chain.add(new ArrayList<>());
        for (int i = 0; i + 1 < n; i++) { chain.get(i).add(i + 1); chain.get(i + 1).add(i); }
        check(components(chain) == 1, "iterative DFS handles a 200,000-node chain");
        boolean overflowed = false;
        try { dfsRecursive(chain, 0, new boolean[n]); } catch (StackOverflowError e) { overflowed = true; }
        check(overflowed, "recursive DFS overflows the stack on the same chain");
        System.out.println("200,000-node chain: iterative DFS fine, recursive DFS threw StackOverflowError");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2027));
        System.out.println("BfsAndDfs: " + passed + " checks passed");
    }
}
