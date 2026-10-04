# 34. A* search and admissible heuristics

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#34-a-search-and-admissible-heuristics)

## How it works

Dijkstra's algorithm guided by a heuristic h(v) that estimates the remaining distance: expand the vertex with the smallest g + h. If h never overestimates (admissible) the path is optimal; a stronger heuristic expands fewer vertices.

## In depth (from the catalog page)

A* is Dijkstra with a guess. It orders vertices by `f = g + h`: the cost paid so far plus an estimate `h` of the cost still to go. If `h` never overestimates the true remaining cost (it is *admissible*), the first time the goal comes off the queue its path is optimal. Dijkstra is the special case `h = 0`. On a 4-connected grid with unit steps, the Manhattan distance from entry 4 is a natural heuristic. Multiplying the heuristic by a weight above 1 makes the search greedier and faster, at the price of the optimality guarantee.

```java
/** w = 1: A* with the Manhattan heuristic; w = 0: plain Dijkstra; w > 1: inflated, inadmissible heuristic. */
static int astar(boolean[][] wall, int sr, int sc, int tr, int tc, int w) {
    int R = wall.length, C = wall[0].length;
    int[] g = new int[R * C];
    Arrays.fill(g, Integer.MAX_VALUE);
    boolean[] closed = new boolean[R * C];
    // entries are {f, g, cell}: smallest f first, and among equal f the larger g
    PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0]) : Integer.compare(y[1], x[1]));
    int start = sr * C + sc;
    g[start] = 0;
    pq.add(new int[]{w * (Math.abs(sr - tr) + Math.abs(sc - tc)), 0, start});
    int[] dr = {1, -1, 0, 0}, dc = {0, 0, 1, -1};
    while (!pq.isEmpty()) {
        int cur = pq.poll()[2];
        if (closed[cur]) continue;
        closed[cur] = true;
        int r = cur / C, c = cur % C;
        if (r == tr && c == tc) return g[cur];
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nc < 0 || nr >= R || nc >= C || wall[nr][nc]) continue;
            int ni = nr * C + nc, ng = g[cur] + 1;
            if (ng < g[ni]) {
                g[ni] = ng;
                pq.add(new int[]{ng + w * (Math.abs(nr - tr) + Math.abs(nc - tc)), ng, ni});
            }
        }
    }
    return -1;                                           // unreachable
}
```

> **Verified.** On 2,000 random 30×30 grids with 25% walls, 1,402 of which had a path from corner to corner, A* with the Manhattan heuristic returned exactly the length found by breadth-first search every time, and −1 whenever there was no path. Averaged over the 1,402 solvable grids it expanded 135 cells, where Dijkstra (the same code with weight 0) expanded 665. Inflating the heuristic to 3× cut that to 88 cells but returned a longer-than-optimal path in 1,332 of the 1,402 grids, at worst 1.53 times the optimum, and never shorter. A weighted search with a consistent heuristic is guaranteed to stay within its weight of the optimum, and it did. (The full program also counts the expanded cells; the snippet leaves that counter out.)

<!-- -->

> **Pitfall.** The optimality guarantee needs an admissible heuristic, and this closed-set version, which never reopens a finished cell, also wants it *consistent*: `h(u) ≤ cost(u, v) + h(v)` for every edge. Manhattan distance is both on a 4-connected unit grid. Allow diagonal moves and it overestimates, so switch to Chebyshev or octile distance. An inflated heuristic is a deliberate trade of correctness for speed; here a 3× heuristic bought a 1.5× reduction in work and cost the optimal answer in 94% of the solvable grids.

**Use it for** game and robot pathfinding, route planning (with a straight-line or haversine heuristic, entry 9), puzzle solving such as sliding tiles with Manhattan distance, and any best-first search where domain knowledge can supply the estimate.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/34-a-star-search
java AStarSearch.java
```

JDK 17 or newer, no build step. It prints 5,404 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
2000 random 30x30 grids with 25% walls, 1402 reachable: mean nodes expanded Dijkstra 665, A* 135, A* with 3x heuristic 88; the 3x heuristic returned a longer-than-optimal path in 1332 grids (worst ratio to the optimum 1.53, guaranteed at most 3)
AStarSearch: 5404 checks passed
```

## References

- **Watch:** [A* (A Star) Search Algorithm — Computerphile](https://www.youtube.com/watch?v=ySN5Wnu88nE)
