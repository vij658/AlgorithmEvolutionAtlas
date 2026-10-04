# 36. Topological sort (Kahn's algorithm)

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#36-topological-sort-kahns-algorithm)

## How it works

Kahn's algorithm orders a directed acyclic graph so every edge points forward: repeatedly output a vertex with no remaining incoming edges. If vertices remain at the end, the graph has a cycle.

## In depth (from the catalog page)

A topological order lists the vertices of a directed acyclic graph so that every edge points forward. Kahn's algorithm (1962) repeatedly removes a vertex with no remaining incoming edges and decrements its neighbors' in-degrees. If it finishes without placing every vertex, the graph has a cycle, so the same code doubles as cycle detection. It runs in O(V + E).

```java
static List<Integer> topoSort(int n, int[][] edges) {    // null if the graph has a cycle
    List<List<Integer>> g = new ArrayList<>();
    int[] indeg = new int[n];
    for (int i = 0; i < n; i++) g.add(new ArrayList<>());
    for (int[] e : edges) { g.get(e[0]).add(e[1]); indeg[e[1]]++; }
    ArrayDeque<Integer> q = new ArrayDeque<>();
    for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
    List<Integer> order = new ArrayList<>();
    while (!q.isEmpty()) {
        int u = q.poll();
        order.add(u);
        for (int v : g.get(u)) if (--indeg[v] == 0) q.add(v);
    }
    return order.size() == n ? order : null;
}
```

> **Verified.** On 1,000 random DAGs of up to 31 vertices, built from a hidden random order so that every edge points forward in it, `topoSort` returned all n vertices with every edge pointing forward. Adding the reverse of one existing edge, which makes a 2-cycle, made it return null every time, and the chain 0→1→2 gives [0, 1, 2]. Swapping the queue for a `PriorityQueue<Integer>` (`topoSortSmallestFirst` in the full program) produced the lexicographically smallest valid order on 300 random graphs of up to 7 vertices, checked against all n! orders.

<!-- -->

> **Pitfall.** The order is not unique, and the FIFO version's choice can shift when the input order shifts. For reproducible output (build plans, generated files, migrations), break ties explicitly, as the min-heap variant does. When `topoSort` returns null, the vertices that never reached in-degree zero are exactly those on a cycle or downstream of one, which is enough to print a useful "circular dependency" message.

**Use it for** build systems and package managers (what to compile or install first), spreadsheet recalculation, task schedulers, course prerequisites, data-pipeline stages, database migration ordering and class initialization order.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/36-topological-sort
java TopologicalSort.java
```

JDK 17 or newer, no build step. It prints 33,598 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
TopologicalSort: 33598 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
