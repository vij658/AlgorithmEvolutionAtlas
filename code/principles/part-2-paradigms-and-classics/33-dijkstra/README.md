# 33. Dijkstra's algorithm

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#33-dijkstras-algorithm)

## How it works

Shortest paths from one source with non-negative edge weights: repeatedly settle the unvisited vertex with the smallest known distance (a priority queue) and relax its outgoing edges. O((V + E) log V) with a binary heap.

## In depth (from the catalog page)

Shortest paths from one source when every edge weight is non-negative. It is greedy: repeatedly take the unfinished vertex with the smallest tentative distance, declare it final, and relax its outgoing edges. With a binary heap it runs in O((V + E) log V); with a plain array instead of a heap it is O(V²), which is better for dense graphs. Java's `PriorityQueue` has no decrease-key operation, so the usual approach adds a new entry for every improvement and skips outdated ones when they surface ("lazy deletion").

```java
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
    return dist;                                         // Long.MAX_VALUE marks unreachable vertices
}
```

> **Verified.** The classic six-vertex example gives distances 0, 7, 9, 20, 20, 11. On 400 random directed graphs of up to 31 vertices with weights from 0 to 20 (zero weights allowed, some vertices unreachable), this version and the textbook variant that finalizes each vertex exactly once (`dijkstraSettled` in the full program) both matched Floyd–Warshall from every source. Negative edges are another story: in the graph 0→1 (weight 1), 0→2 (4), 2→1 (−5), the finalize-once version answers dist(0, 1) = 1, while the true distance through vertex 2 is −1, which Bellman–Ford finds. The lazy version above also answers −1 on this graph, because it lets a vertex be improved again.

<!-- -->

> **Pitfall.** With negative edges the greedy argument fails: a vertex declared final can still be improved later. The lazy-deletion version above happens to re-relax vertices and so survives the small example, but then it re-expands vertices and loses the O((V + E) log V) bound. If weights can be negative, use Bellman–Ford (entry 35).

**Use it for** road and network routing (OSPF routers compute their shortest-path trees with a method based on Dijkstra's algorithm), maps and games (usually with A* on top, entry 34), minimum-cost anything with non-negative costs, and as a subroutine, for example in Johnson's algorithm (entry 35).

## Run it

```
cd code/principles/part-2-paradigms-and-classics/33-dijkstra
java Dijkstra.java
```

JDK 17 or newer, no build step. It prints 137,839 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
negative edge 2->1 of weight -5: textbook Dijkstra (each vertex finalized once) says dist(0,1) = 1, the lazy-deletion version says -1, Bellman-Ford says -1
Dijkstra: 137839 checks passed
```

## References

- Wikipedia, [Open Shortest Path First](https://en.wikipedia.org/wiki/Open_Shortest_Path_First): OSPF computes the shortest-path tree for each route using a method based on Dijkstra's algorithm. [Routing Information Protocol](https://en.wikipedia.org/wiki/Routing_Information_Protocol): RIP is a distance-vector protocol, a family based on the Bellman–Ford algorithm.
- **Watch:** [Dijkstra's Algorithm — Computerphile](https://www.youtube.com/watch?v=GazC3A4OQTE)
- **Read:** [Dijkstra's Shortest Path Algorithm — A Detailed and Visual Introduction (freeCodeCamp)](https://www.freecodecamp.org/news/dijkstras-shortest-path-algorithm-visual-introduction/)
