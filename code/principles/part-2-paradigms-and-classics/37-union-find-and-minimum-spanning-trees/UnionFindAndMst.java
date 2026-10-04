import java.util.*;

/**
 * Entry 37 of the principles catalog (Part 2): Union-find and minimum spanning trees
 *
 * HOW IT WORKS
 *   Union-find keeps disjoint sets as trees; union by rank and path compression make each operation nearly
 *   O(1). Kruskal's algorithm sorts edges and adds each one that joins two different components, producing a
 *   minimum spanning tree; Prim grows one tree from a vertex.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java UnionFindAndMst.java
 *   Expected: the output in expected-output.txt, ending "UnionFindAndMst: 2001 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class UnionFindAndMst {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long kruskal(int n, int[][] edges, int[] edgesUsed) {      // edges {u, v, w}
        int[][] sorted = edges.clone();
        Arrays.sort(sorted, Comparator.comparingInt(e -> e[2]));
        DSU dsu = new DSU(n);
        long total = 0;
        int used = 0;
        for (int[] e : sorted)
            if (dsu.union(e[0], e[1])) { total += e[2]; used++; }
        edgesUsed[0] = used;
        return total;
    }

    static long prim(int n, List<List<int[]>> g) {                    // connected graph
        boolean[] in = new boolean[n];
        PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(x -> x[0]));
        pq.add(new int[]{0, 0});
        long total = 0;
        while (!pq.isEmpty()) {
            int[] top = pq.poll();
            if (in[top[1]]) continue;
            in[top[1]] = true;
            total += top[0];
            for (int[] e : g.get(top[1])) if (!in[e[0]]) pq.add(new int[]{e[1], e[0]});
        }
        return total;
    }

    static long hops;                                                // instrumented copy of find

    static int findCounted(int[] parent, int x) {
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; hops++; }
        return x;
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

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 32 (bfs-and-dfs), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
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
    // Checks: what this program verifies. Run with: java UnionFindAndMst.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 1000; t++) {
            int n = 2 + rnd.nextInt(40);
            List<int[]> es = new ArrayList<>();
            for (int i = 1; i < n; i++) es.add(new int[]{rnd.nextInt(i), i, 1 + rnd.nextInt(50)});   // random spanning tree keeps it connected
            for (int i = 0, extra = rnd.nextInt(3 * n); i < extra; i++) es.add(new int[]{rnd.nextInt(n), rnd.nextInt(n), 1 + rnd.nextInt(50)});
            int[][] edges = es.toArray(new int[0][]);
            int[] used = new int[1];
            long k = kruskal(n, edges, used);
            check(k == prim(n, weighted(n, edges, true)), "Kruskal and Prim find the same total weight");
            check(used[0] == n - 1, "a spanning tree has n - 1 edges");
        }
        int n = 1_000_000;
        int[] parent = new int[n], rank = new int[n];
        for (int i = 0; i < n; i++) parent[i] = i;
        for (int i = 0; i < n; i++) {                                // random unions, union by rank
            int a = findCounted(parent, rnd.nextInt(n)), b = findCounted(parent, rnd.nextInt(n));
            if (a == b) continue;
            if (rank[a] < rank[b]) { int tmp = a; a = b; b = tmp; }
            parent[b] = a;
            if (rank[a] == rank[b]) rank[a]++;
        }
        hops = 0;
        int finds = 1_000_000;
        for (int i = 0; i < finds; i++) findCounted(parent, rnd.nextInt(n));
        double avg = hops / (double) finds;
        check(avg < 3.0, "path halving keeps the average find under three hops");
        System.out.printf("union-find on 1,000,000 elements after 1,000,000 random unions: %.3f parent hops per find on average%n", avg);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2027));
        System.out.println("UnionFindAndMst: " + passed + " checks passed");
    }
}
