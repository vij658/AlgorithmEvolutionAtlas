import java.util.*;

/**
 * Entry 34 of the principles catalog (Part 2): A* search and admissible heuristics
 *
 * HOW IT WORKS
 *   Dijkstra's algorithm guided by a heuristic h(v) that estimates the remaining distance: expand the vertex
 *   with the smallest g + h. If h never overestimates (admissible) the path is optimal; a stronger heuristic
 *   expands fewer vertices.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AStarSearch.java
 *   Expected: the output in expected-output.txt, ending "AStarSearch: 5404 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class AStarSearch {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int bfsGrid(boolean[][] wall, int sr, int sc, int tr, int tc) {
        int R = wall.length, C = wall[0].length;
        int[] dist = new int[R * C];
        Arrays.fill(dist, -1);
        ArrayDeque<Integer> q = new ArrayDeque<>();
        dist[sr * C + sc] = 0;
        q.add(sr * C + sc);
        int[] dr = {1, -1, 0, 0}, dc = {0, 0, 1, -1};
        while (!q.isEmpty()) {
            int cur = q.poll(), r = cur / C, c = cur % C;
            if (r == tr && c == tc) return dist[cur];
            for (int d = 0; d < 4; d++) {
                int nr = r + dr[d], nc = c + dc[d];
                if (nr < 0 || nc < 0 || nr >= R || nc >= C || wall[nr][nc] || dist[nr * C + nc] >= 0) continue;
                dist[nr * C + nc] = dist[cur] + 1;
                q.add(nr * C + nc);
            }
        }
        return -1;
    }

    /** w = 1: A* with the Manhattan heuristic; w = 0: plain Dijkstra; w > 1: inflated, inadmissible heuristic. */
    static int astar(boolean[][] wall, int sr, int sc, int tr, int tc, int w, int[] expandedOut) {
        int R = wall.length, C = wall[0].length;
        int[] g = new int[R * C];
        Arrays.fill(g, Integer.MAX_VALUE);
        boolean[] closed = new boolean[R * C];
        PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0]) : Integer.compare(y[1], x[1]));
        int start = sr * C + sc;
        g[start] = 0;
        pq.add(new int[]{w * (Math.abs(sr - tr) + Math.abs(sc - tc)), 0, start});
        int expanded = 0;
        int[] dr = {1, -1, 0, 0}, dc = {0, 0, 1, -1};
        while (!pq.isEmpty()) {
            int[] top = pq.poll();
            int cur = top[2];
            if (closed[cur]) continue;
            closed[cur] = true;
            expanded++;
            int r = cur / C, c = cur % C;
            if (r == tr && c == tc) { expandedOut[0] = expanded; return g[cur]; }
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
        expandedOut[0] = expanded;
        return -1;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java AStarSearch.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        int R = 30, C = 30, grids = 2000, reachable = 0, suboptimal = 0;
        long expAstar = 0, expDijkstra = 0, expInflated = 0;
        double worstRatio = 1;
        for (int t = 0; t < grids; t++) {
            boolean[][] wall = new boolean[R][C];
            for (int r = 0; r < R; r++) for (int c = 0; c < C; c++) wall[r][c] = rnd.nextInt(100) < 25;
            wall[0][0] = false;
            wall[R - 1][C - 1] = false;
            int opt = bfsGrid(wall, 0, 0, R - 1, C - 1);
            int[] e1 = new int[1], e0 = new int[1], e3 = new int[1];
            int a = astar(wall, 0, 0, R - 1, C - 1, 1, e1);
            int dj = astar(wall, 0, 0, R - 1, C - 1, 0, e0);
            int inf = astar(wall, 0, 0, R - 1, C - 1, 3, e3);
            check(a == opt && dj == opt, "A* with an admissible heuristic returns the optimal length");
            if (opt >= 0) {
                reachable++;
                expAstar += e1[0]; expDijkstra += e0[0]; expInflated += e3[0];
                check(inf >= opt, "an inflated heuristic never beats the optimum");
                check(inf <= 3 * opt, "weighted A* with factor 3 stays within 3x of the optimum");
                worstRatio = Math.max(worstRatio, inf / (double) opt);
                if (inf > opt) suboptimal++;
            } else check(inf == -1, "unreachable stays unreachable");
        }
        check(expAstar < expDijkstra, "A* expands fewer nodes than Dijkstra overall");
        check(suboptimal > 0, "the inflated heuristic gave at least one suboptimal path");
        System.out.printf("%d random 30x30 grids with 25%% walls, %d reachable: mean nodes expanded Dijkstra %.0f, A* %.0f, A* with 3x heuristic %.0f; the 3x heuristic returned a longer-than-optimal path in %d grids (worst ratio to the optimum %.2f, guaranteed at most 3)%n",
                grids, reachable, expDijkstra / (double) reachable, expAstar / (double) reachable, expInflated / (double) reachable, suboptimal, worstRatio);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2027));
        System.out.println("AStarSearch: " + passed + " checks passed");
    }
}
