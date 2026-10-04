import java.util.*;

/**
 * Entry 33 of the principles catalog (Part 2): Dijkstra's algorithm
 *
 * HOW IT WORKS
 *   Shortest paths from one source with non-negative edge weights: repeatedly settle the unvisited vertex with
 *   the smallest known distance (a priority queue) and relax its outgoing edges. O((V + E) log V) with a binary
 *   heap.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Dijkstra.java
 *   Expected: the output in expected-output.txt, ending "Dijkstra: 137839 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Dijkstra {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final long INF = Long.MAX_VALUE / 4;

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long[] dijkstra(List<List<int[]>> g, int src) {   // edges as {to, weight}, weights >= 0
        long[] dist = new long[g.size()];
        Arrays.fill(dist, Long.MAX_VALUE);
        dist[src] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(x -> x[0]));
        pq.add(new long[]{0, src});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            if (top[0] > dist[u]) continue;                  // stale entry: a shorter path was already found
            for (int[] e : g.get(u)) {
                long nd = top[0] + e[1];
                if (nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{nd, e[0]}); }
            }
        }
        return dist;
    }

    static long[] dijkstraSettled(List<List<int[]>> g, int src) {   // textbook variant: each vertex is finalized once
        long[] dist = new long[g.size()];
        Arrays.fill(dist, Long.MAX_VALUE);
        boolean[] settled = new boolean[g.size()];
        dist[src] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(x -> x[0]));
        pq.add(new long[]{0, src});
        while (!pq.isEmpty()) {
            long[] top = pq.poll();
            int u = (int) top[1];
            if (settled[u]) continue;
            settled[u] = true;
            for (int[] e : g.get(u)) {
                long nd = top[0] + e[1];
                if (!settled[e[0]] && nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{nd, e[0]}); }
            }
        }
        return dist;
    }

    // ----------------------------------------------------------------------------------------------------
    // Shared helpers
    // ----------------------------------------------------------------------------------------------------
    static List<List<int[]>> weighted(int n, int[][] edges, boolean both) {   // adjacency lists of {to, weight}
        List<List<int[]>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) {
            g.get(e[0]).add(new int[]{e[1], e[2]});
            if (both) g.get(e[1]).add(new int[]{e[0], e[2]});
        }
        return g;
    }

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

    static int[][] randomEdges(Random rnd, int n, int m, int lo, int hi) {   // directed, weights in [lo, hi]
        int[][] edges = new int[m][];
        for (int i = 0; i < m; i++) edges[i] = new int[]{rnd.nextInt(n), rnd.nextInt(n), lo + rnd.nextInt(hi - lo + 1)};
        return edges;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 35 (bellman-ford-floyd-warshall-johnson), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    static long[] bellmanFord(int n, int[][] edges, int src) {   // edges {u, v, w}; null if a negative cycle is reachable
        long[] dist = new long[n];
        Arrays.fill(dist, INF);
        dist[src] = 0;
        for (int pass = 1; pass < n; pass++) {
            boolean changed = false;
            for (int[] e : edges)
                if (dist[e[0]] < INF && dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
            if (!changed) break;
        }
        for (int[] e : edges)
            if (dist[e[0]] < INF && dist[e[0]] + e[2] < dist[e[1]]) return null;   // still improving: negative cycle
        return dist;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Dijkstra.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        int[][] classic = {{0, 1, 7}, {0, 2, 9}, {0, 5, 14}, {1, 2, 10}, {1, 3, 15}, {2, 3, 11}, {2, 5, 2}, {3, 4, 6}, {4, 5, 9}};
        long[] d = dijkstra(weighted(6, classic, true), 0);
        check(Arrays.equals(d, new long[]{0, 7, 9, 20, 20, 11}), "classic six-node example");
        for (int t = 0; t < 400; t++) {
            int n = 2 + rnd.nextInt(30);
            int[][] edges = randomEdges(rnd, n, rnd.nextInt(120), 0, 20);
            long[][] fw = floydWarshall(n, edges);
            List<List<int[]>> g = weighted(n, edges, false);
            for (int s = 0; s < n; s++) {
                long[] ds = dijkstra(g, s), dt = dijkstraSettled(g, s);
                for (int v = 0; v < n; v++) {
                    long expect = fw[s][v] >= INF ? Long.MAX_VALUE : fw[s][v];
                    check(ds[v] == expect && dt[v] == expect, "Dijkstra equals Floyd-Warshall, zero weights allowed");
                }
            }
        }
        int[][] neg = {{0, 1, 1}, {0, 2, 4}, {2, 1, -5}};
        long settled = dijkstraSettled(weighted(3, neg, false), 0)[1];
        long[] bf = bellmanFord(3, neg, 0);
        check(settled == 1 && bf[1] == -1, "settled-once Dijkstra answers 1 where the true distance is -1");
        long lazy = dijkstra(weighted(3, neg, false), 0)[1];
        check(lazy == -1, "the lazy-deletion version re-relaxes vertex 1 and answers -1 on this example");
        System.out.println("negative edge 2->1 of weight -5: textbook Dijkstra (each vertex finalized once) says dist(0,1) = " + settled
                + ", the lazy-deletion version says " + lazy + ", Bellman-Ford says " + bf[1]);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2027));
        System.out.println("Dijkstra: " + passed + " checks passed");
    }
}
