import java.util.*;

/**
 * Entry 35 of the principles catalog (Part 2): Bellman-Ford, Floyd-Warshall and Johnson
 *
 * HOW IT WORKS
 *   Bellman-Ford relaxes every edge V - 1 times and handles negative weights (and detects negative cycles).
 *   Floyd-Warshall computes all pairs in O(V^3) by allowing intermediate vertices one at a time. Johnson
 *   reweights edges with Bellman-Ford potentials so Dijkstra can run from every vertex.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ShortestPathsAllPairs.java
 *   Expected: the output in expected-output.txt, ending "ShortestPathsAllPairs: 53276 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ShortestPathsAllPairs {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final long INF = Long.MAX_VALUE / 4;

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
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

    static long[][] johnson(int n, int[][] edges) {          // all-pairs shortest paths via reweighting; null on a negative cycle
        int[][] ext = new int[edges.length + n][];
        System.arraycopy(edges, 0, ext, 0, edges.length);
        for (int i = 0; i < n; i++) ext[edges.length + i] = new int[]{n, i, 0};      // virtual source reaches everything for free
        long[] h = bellmanFord(n + 1, ext, n);
        if (h == null) return null;
        List<List<int[]>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) {
            long w = e[2] + h[e[0]] - h[e[1]];
            if (w < 0) throw new IllegalStateException("reweighting must make every edge non-negative");
            g.get(e[0]).add(new int[]{e[1], (int) w});
        }
        long[][] d = new long[n][n];
        for (int s = 0; s < n; s++) {
            long[] ds = dijkstra(g, s);
            for (int t = 0; t < n; t++) d[s][t] = ds[t] == Long.MAX_VALUE ? INF : ds[t] - h[s] + h[t];
        }
        return d;
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

    static int[][] randomEdges(Random rnd, int n, int m, int lo, int hi) {   // directed, weights in [lo, hi]
        int[][] edges = new int[m][];
        for (int i = 0; i < m; i++) edges[i] = new int[]{rnd.nextInt(n), rnd.nextInt(n), lo + rnd.nextInt(hi - lo + 1)};
        return edges;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 33 (dijkstra), used here for comparison or cross-checking
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

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ShortestPathsAllPairs.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        int withNegative = 0;
        for (int t = 0; t < 300; t++) {
            int n = 2 + rnd.nextInt(14);
            long[] p = new long[n];
            for (int i = 0; i < n; i++) p[i] = rnd.nextInt(31);
            int[][] base = randomEdges(rnd, n, rnd.nextInt(60), 0, 20);
            int[][] edges = new int[base.length][];
            boolean sawNegative = false;
            for (int i = 0; i < base.length; i++) {          // w' = w + p(u) - p(v): cycle sums are unchanged, single edges can go negative
                int w = (int) (base[i][2] + p[base[i][0]] - p[base[i][1]]);
                edges[i] = new int[]{base[i][0], base[i][1], w};
                if (w < 0) sawNegative = true;
            }
            long[][] fw = floydWarshall(n, edges);
            long[][] jo = johnson(n, edges);
            check(jo != null, "no negative cycle by construction");
            for (int s = 0; s < n; s++) {
                long[] bf = bellmanFord(n, edges, s);
                check(bf != null, "Bellman-Ford finds no negative cycle");
                for (int v = 0; v < n; v++) {
                    check(bf[v] == fw[s][v], "Bellman-Ford equals Floyd-Warshall with negative edges");
                    check(jo[s][v] == fw[s][v], "Johnson equals Floyd-Warshall");
                }
            }
            if (sawNegative) withNegative++;
        }
        check(withNegative > 100, "the random test graphs really do contain negative edges (" + withNegative + " of 300)");
        System.out.println("Bellman-Ford, Floyd-Warshall and Johnson agreed on all pairs of 300 random graphs, " + withNegative + " of which contain negative edges");
        int[][] cyc = {{0, 1, 2}, {1, 2, 2}, {2, 0, -5}};
        check(bellmanFord(3, cyc, 0) == null, "Bellman-Ford reports the negative cycle");
        long[][] d = floydWarshall(3, cyc);
        check(d[0][0] < 0, "Floyd-Warshall leaves a negative diagonal entry");
        check(johnson(3, cyc) == null, "Johnson reports the negative cycle");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2027));
        System.out.println("ShortestPathsAllPairs: " + passed + " checks passed");
    }
}
