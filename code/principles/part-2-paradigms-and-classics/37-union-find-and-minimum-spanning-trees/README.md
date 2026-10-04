# 37. Union-find and minimum spanning trees

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#37-union-find-and-minimum-spanning-trees)

## How it works

Union-find keeps disjoint sets as trees; union by rank and path compression make each operation nearly O(1). Kruskal's algorithm sorts edges and adds each one that joins two different components, producing a minimum spanning tree; Prim grows one tree from a vertex.

## In depth (from the catalog page)

**Union-find** (disjoint sets) keeps a partition of n items and supports `find` (which set is this item in?) and `union` (merge two sets). Two tricks make it fast: union by rank, which hangs the shorter tree under the taller one, and path compression, here in its "halving" form, which points each visited node at its grandparent. Together they give O(α(n)) amortized time per operation, where α is the inverse Ackermann function, below 5 for any input size that could physically exist (Tarjan, 1975). A **spanning tree** connects all vertices with n − 1 edges, and the **minimum spanning tree** (MST) has the smallest total weight. By the *cut property*, the lightest edge crossing any split of the vertices belongs to some MST, and both classic algorithms apply it: **Kruskal** sorts the edges and keeps an edge when its endpoints are in different sets, and **Prim** grows a single tree by always adding the lightest edge that leaves it.

```java
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
        if (ra == rb) return false;                     // already together: this edge would close a cycle
        if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;                                // attach the shorter tree under the taller one
        if (rank[ra] == rank[rb]) rank[ra]++;
        sets--;
        return true;
    }
}

static long kruskal(int n, int[][] edges) {              // edges {u, v, w}; total weight of a minimum spanning forest
    int[][] sorted = edges.clone();
    Arrays.sort(sorted, Comparator.comparingInt(e -> e[2]));
    DSU dsu = new DSU(n);
    long total = 0;
    for (int[] e : sorted)
        if (dsu.union(e[0], e[1])) total += e[2];
    return total;
}

static long prim(int n, List<List<int[]>> g) {           // connected graph; g.get(u) holds {neighbor, weight}
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
```

> **Verified.** On 1,000 random connected weighted graphs of up to 41 vertices, built as a random spanning tree plus extra edges (parallel edges and self-loops included), Kruskal and Prim found the same total weight, and a spanning tree always used exactly n − 1 edges (the full program's `kruskal` also reports how many edges it kept). Union-find also gave the same component counts as the depth-first search of entry 32. With 1,000,000 elements after 1,000,000 random unions (union by rank plus path halving, measured with an instrumented copy of `find`), the next 1,000,000 finds took 0.856 parent hops each on average.

<!-- -->

> **Pitfall.** Without union by rank or size, and without path compression, a sequence of unions can build a chain and make `find` cost O(n). Also, an MST is not a shortest-path tree: it minimizes total weight, not distances from any vertex, so don't use it for routing.

**Use it for** Kruskal's algorithm, connected components of a graph that keeps growing, cycle detection in undirected graphs (`union` returning false means the edge closes a cycle), merging accounts or equivalence classes, percolation and image-segmentation labels, and maze generation. MSTs show up in network and cable design, single-linkage clustering (cut the heaviest MST edges), and as a 2-approximation for the traveling-salesman problem when the distances form a metric (entry 10).

## Run it

```
cd code/principles/part-2-paradigms-and-classics/37-union-find-and-minimum-spanning-trees
java UnionFindAndMst.java
```

JDK 17 or newer, no build step. It prints 2,001 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
union-find on 1,000,000 elements after 1,000,000 random unions: 0.856 parent hops per find on average
UnionFindAndMst: 2001 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
