# 32. Breadth-first and depth-first search

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#32-breadth-first-and-depth-first-search)

## How it works

Breadth-first search explores in layers with a queue and gives shortest paths in unweighted graphs; depth-first search goes deep with a stack (or recursion) and exposes structure such as cycles and connected components.

## In depth (from the catalog page)

Two ways to walk a graph, both in O(V + E). BFS uses a queue and visits vertices in order of their distance (number of edges) from the start, so the first time it reaches a vertex is along a shortest path in an unweighted graph. DFS uses a stack, or recursion, and goes as deep as it can before backing up. It is the engine behind connected components, cycle detection, topological ordering (entry 36) and backtracking (entry 25).

```java
static int[] bfsDistances(List<List<Integer>> g, int src) {
    int[] dist = new int[g.size()];
    Arrays.fill(dist, -1);                              // -1 means not reached yet
    ArrayDeque<Integer> q = new ArrayDeque<>();
    dist[src] = 0;
    q.add(src);
    while (!q.isEmpty()) {
        int u = q.poll();
        for (int v : g.get(u))
            if (dist[v] < 0) { dist[v] = dist[u] + 1; q.add(v); }    // mark when enqueued
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
```

> **Verified.** On 1,000 random undirected graphs of up to 31 vertices (duplicate edges and self-loops included), `bfsDistances` equalled Floyd–Warshall distances with unit weights from every source, and `components` agreed with union-find on the number of components. On a chain of 200,000 vertices, `components` returned 1, while `dfsRecursive` threw `StackOverflowError` with this JDK's default thread stack.

<!-- -->

> **Pitfall.** Mark a vertex as seen when you *enqueue* it, as `dist[v] = …` does, not when you dequeue it, or the same vertex enters the queue many times. Recursive DFS goes as deep as the longest path, which on real data (a linked chain of 200,000 nodes, a long dependency chain) overflows the default stack. The explicit-stack version above marks vertices when it pushes them, so its visit order differs from recursive DFS. That is fine for reachability and components, but algorithms that need true discovery and finishing times need a stack of iterators instead.

**Use it for** shortest hop counts ("degrees of separation", word ladders, fewest moves in a puzzle), flood fill, crawlers, dependency discovery, maze solving and connected components.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/32-bfs-and-dfs
java BfsAndDfs.java
```

JDK 17 or newer, no build step. It prints 357,918 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
200,000-node chain: iterative DFS fine, recursive DFS threw StackOverflowError
BfsAndDfs: 357918 checks passed
```

## References

- **Read:** [Graph Algorithms in Python: BFS, DFS and beyond (freeCodeCamp)](https://www.freecodecamp.org/news/graph-algorithms-in-python-bfs-dfs-and-beyond/)
