# 35. Bellman–Ford, Floyd–Warshall and Johnson

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#35-bellmanford-floydwarshall-and-johnson)

## How it works

Bellman–Ford relaxes every edge V − 1 times and handles negative weights (and detects negative cycles). Floyd–Warshall computes all pairs in O(V³) by allowing intermediate vertices one at a time. Johnson reweights edges with Bellman–Ford potentials so Dijkstra can run from every vertex.

## In depth (from the catalog page)

**Bellman–Ford** relaxes every edge V − 1 times; after round i every shortest path of at most i edges is correct. Negative edges are fine, and if a V-th round still improves something, a negative cycle is reachable and shortest paths don't exist. It runs in O(V·E). **Floyd–Warshall** finds all pairs with three nested loops in O(V³): after step k, `d[i][j]` is the shortest path that uses only the first k vertices as stepping stones, and a negative number on the diagonal exposes a negative cycle. **Johnson's algorithm** gets all pairs on sparse graphs by reweighting. It runs Bellman–Ford once from a virtual source to get a potential `h(v)` for every vertex, replaces each weight with `w(u, v) + h(u) − h(v)`, which is never negative, and then runs Dijkstra from every vertex. The reweighting changes every path from s to t by the same amount, `h(s) − h(t)`, so shortest paths stay shortest.

```java
static final long INF = Long.MAX_VALUE / 4;              // large, but INF + INF cannot overflow

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
        long[] ds = dijkstra(g, s);                      // dijkstra from entry 33
        for (int t = 0; t < n; t++) d[s][t] = ds[t] == Long.MAX_VALUE ? INF : ds[t] - h[s] + h[t];
    }
    return d;
}
```

> **Verified.** On 300 random graphs of up to 15 vertices, 268 of them containing negative edges, Bellman–Ford from every source, Floyd–Warshall and Johnson agreed on every pair. The graphs had no negative cycle by construction: each weight was a non-negative weight plus `p(u) − p(v)` for a random potential p, which shifts every path by the same amount and leaves cycle totals unchanged. On the three-vertex cycle 0→1 (2), 1→2 (2), 2→0 (−5), whose total is −1, Bellman–Ford and Johnson returned null, and Floyd–Warshall left a negative number on the diagonal.

<!-- -->

> **Rule of thumb.** Non-negative weights: Dijkstra. Negative weights and one source: Bellman–Ford. All pairs on a small or dense graph: Floyd–Warshall. All pairs on a large sparse graph: Johnson, or simply Dijkstra from every vertex when weights are non-negative.

**Use it for** currency-arbitrage detection (take −log of every exchange rate; a negative cycle is a profitable loop), distance-vector routing (protocols such as RIP are built on Bellman–Ford), systems of difference constraints (`x_j − x_i ≤ c` is an edge of weight c), and transitive closure, which is Floyd–Warshall with booleans (Warshall's algorithm).

## Run it

```
cd code/principles/part-2-paradigms-and-classics/35-bellman-ford-floyd-warshall-johnson
java ShortestPathsAllPairs.java
```

JDK 17 or newer, no build step. It prints 53,276 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Bellman-Ford, Floyd-Warshall and Johnson agreed on all pairs of 300 random graphs, 268 of which contain negative edges
ShortestPathsAllPairs: 53276 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
