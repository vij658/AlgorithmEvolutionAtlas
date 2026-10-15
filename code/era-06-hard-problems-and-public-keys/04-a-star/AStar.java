import java.util.*;

/**
 * Era 6, topic 4: A*, the search guided by an estimate (Hart, Nilsson and Raphael, 1968).
 *
 * HOW IT WORKS
 *   Dijkstra's method (Era 5) finds the shortest path by growing a circle of settled places around the start, nearest
 *   first, in every direction at once. A robot that knows roughly where the goal lies wastes most of that work.
 *   The Graph Traverser went the other way: always step from the place that looks closest to the goal. It is fast,
 *   but a wall in the way can lead it into a dead end and out again, and the path it returns may be long.
 *   A* takes the next place n with the smallest
 *       f(n) = g(n) + h(n),
 *   where g(n) is the length of the best path found so far from the start to n, and h(n) is an estimate of what
 *   remains. If h never overestimates (it is "admissible"), the first time the goal is taken its path is a shortest
 *   one. If also h(m) <= cost(m, n) + h(n) for every step from m to n (it is "consistent"), no place ever needs to be
 *   taken twice. With h = 0 it is Dijkstra's method; with a perfect h it walks straight along a shortest path.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A small map with a cup-shaped wall: Dijkstra, the greedy Graph Traverser and A*, drawn.
 *   2. A 400 x 400 map with a quarter of its squares walled: no estimate, two admissible estimates, a perfect one.
 *   3. 2,000 random maps: A* always finds a shortest path, the greedy method often does not.
 *   4. Weighted A* (f = g + w h): fewer places taken, paths never more than w times too long.
 *   5. An estimate that is admissible but not consistent: A* that never reopens a place goes wrong; with reopening
 *      it is right again.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AStar.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AStar {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1968L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static final int[] DR = {-1, 0, 1, 0}, DC = {0, 1, 0, -1};

    interface Estimate { double h(int r, int c); }

    static class Result {
        int cost = -1, expanded, reopened;
        boolean[] taken;
        int[] parent;
    }

    /**
     * Best-first search on a grid of squares (moves up, down, left, right, each of length 1).
     * The next square is the one with the smallest  gw * g + hw * h ; ties go to the larger g, then to the earlier.
     *   Dijkstra: gw = 1, hw = 0.   Greedy: gw = 0, hw = 1.   A*: gw = 1, hw = 1.   Weighted A*: gw = 1, hw = w.
     */
    static Result search(boolean[][] wall, int sr, int sc, int tr, int tc, Estimate est, double gw, double hw, boolean reopen) {
        int rows = wall.length, cols = wall[0].length, n = rows * cols;
        int[] g = new int[n];
        Arrays.fill(g, Integer.MAX_VALUE);
        boolean[] closed = new boolean[n];
        Result res = new Result();
        res.taken = new boolean[n];
        res.parent = new int[n];
        Arrays.fill(res.parent, -1);
        PriorityQueue<double[]> open = new PriorityQueue<>((a, b) -> a[0] != b[0] ? Double.compare(a[0], b[0])
                : a[1] != b[1] ? Double.compare(b[1], a[1]) : Double.compare(a[3], b[3]));
        long order = 0;
        int s = sr * cols + sc, t = tr * cols + tc;
        g[s] = 0;
        open.add(new double[]{hw * est.h(sr, sc), 0, s, order++});
        while (!open.isEmpty()) {
            double[] top = open.poll();
            int u = (int) top[2];
            if (top[1] != g[u] || closed[u]) continue;            // an out-of-date entry
            closed[u] = true;
            res.taken[u] = true;
            res.expanded++;
            if (u == t) { res.cost = g[u]; return res; }
            int ur = u / cols, uc = u % cols;
            for (int d = 0; d < 4; d++) {
                int vr = ur + DR[d], vc = uc + DC[d];
                if (vr < 0 || vc < 0 || vr >= rows || vc >= cols || wall[vr][vc]) continue;
                int v = vr * cols + vc, ng = g[u] + 1;
                if (ng >= g[v]) continue;
                if (gw == 0 && g[v] != Integer.MAX_VALUE) continue;   // the greedy method keeps the first way it found
                if (closed[v]) {
                    if (!reopen) continue;
                    closed[v] = false;
                    res.reopened++;
                }
                g[v] = ng;
                res.parent[v] = u;
                open.add(new double[]{gw * ng + hw * est.h(vr, vc), ng, v, order++});
            }
        }
        return res;
    }

    /** True distances to the goal by breadth-first search backwards; -1 where the goal cannot be reached. */
    static int[][] distances(boolean[][] wall, int tr, int tc) {
        int rows = wall.length, cols = wall[0].length;
        int[][] dist = new int[rows][cols];
        for (int[] row : dist) Arrays.fill(row, -1);
        ArrayDeque<int[]> q = new ArrayDeque<>();
        dist[tr][tc] = 0;
        q.add(new int[]{tr, tc});
        while (!q.isEmpty()) {
            int[] p = q.poll();
            for (int d = 0; d < 4; d++) {
                int r = p[0] + DR[d], c = p[1] + DC[d];
                if (r < 0 || c < 0 || r >= rows || c >= cols || wall[r][c] || dist[r][c] >= 0) continue;
                dist[r][c] = dist[p[0]][p[1]] + 1;
                q.add(new int[]{r, c});
            }
        }
        return dist;
    }

    static int pathLength(Result r, int cols, int tr, int tc) {
        int len = 0;
        for (int v = tr * cols + tc; r.parent[v] >= 0; v = r.parent[v]) len++;
        return len;
    }

    static String drawn(String[] map, Result r) {
        int cols = map[0].length();
        char[][] g = new char[map.length][];
        for (int i = 0; i < map.length; i++) g[i] = map[i].toCharArray();
        for (int i = 0; i < map.length; i++)
            for (int j = 0; j < cols; j++) if (r.taken[i * cols + j] && g[i][j] == '.') g[i][j] = 'o';
        int t = -1;
        for (int i = 0; i < map.length; i++) for (int j = 0; j < cols; j++) if (g[i][j] == 'G') t = i * cols + j;
        for (int v = r.parent[t]; v >= 0 && r.parent[v] >= 0; v = r.parent[v]) g[v / cols][v % cols] = '*';
        StringJoiner sj = new StringJoiner("/");
        for (char[] row : g) sj.add(new String(row));
        return sj.toString();
    }

    public static void main(String[] args) {
        // ---- 1. a small map -------------------------------------------------------------------------------------------
        String[] map = {
                "......................",
                "......................",
                "......##########......",
                "...............#......",
                "...............#......",
                "..S............#...G..",
                "...............#......",
                "...............#......",
                "......##########......",
                "......................",
                "......................"};
        int rows = map.length, cols = map[0].length(), sr = 0, sc = 0, tr = 0, tc = 0;
        boolean[][] wall = new boolean[rows][cols];
        for (int i = 0; i < rows; i++)
            for (int j = 0; j < cols; j++) {
                char ch = map[i].charAt(j);
                wall[i][j] = ch == '#';
                if (ch == 'S') { sr = i; sc = j; }
                if (ch == 'G') { tr = i; tc = j; }
            }
        final int gr = tr, gc = tc;
        Estimate zero = (r, c) -> 0, manhattan = (r, c) -> Math.abs(r - gr) + Math.abs(c - gc);
        Result dij = search(wall, sr, sc, tr, tc, zero, 1, 0, true);
        Result gre = search(wall, sr, sc, tr, tc, manhattan, 0, 1, false);
        Result ast = search(wall, sr, sc, tr, tc, manhattan, 1, 1, true);
        int greLen = pathLength(gre, cols, tr, tc);
        check(dij.cost == ast.cost && greLen > ast.cost, "on the small map A* is shortest and greedy is not");
        check(ast.expanded < dij.expanded && gre.expanded < ast.expanded, "greedy takes fewest, Dijkstra most");
        System.out.printf("small: a %d x %d map, a cup-shaped wall between S and G, moves up, down, left, right ; estimate h = rows apart + columns apart, ignoring walls ; Dijkstra (h not used) takes %d squares, path %d steps ; greedy (h only) takes %d squares, path %d steps ; A* (g + h) takes %d squares, path %d steps%n",
                cols, rows, dij.expanded, dij.cost, gre.expanded, greLen, ast.expanded, ast.cost);
        System.out.println("map-dijkstra: " + drawn(map, dij));
        System.out.println("map-greedy: " + drawn(map, gre));
        System.out.println("map-astar: " + drawn(map, ast));

        // ---- 2. a large map --------------------------------------------------------------------------------------------
        int big = 400;
        boolean[][] bw;
        int[][] truth;
        do {
            bw = new boolean[big][big];
            for (int i = 0; i < big; i++) for (int j = 0; j < big; j++) bw[i][j] = uniform() < 0.25;
            bw[0][0] = false;
            bw[big - 1][big - 1] = false;
            truth = distances(bw, big - 1, big - 1);
        } while (truth[0][0] < 0);
        final int[][] tru = truth;
        final int B = big - 1;
        Estimate none = (r, c) -> 0;
        Estimate euclid = (r, c) -> Math.hypot(B - r, B - c);
        Estimate manh = (r, c) -> (B - r) + (B - c);
        Estimate perfect = (r, c) -> tru[r][c];
        Result[] rs = {
                search(bw, 0, 0, B, B, none, 1, 1, true),
                search(bw, 0, 0, B, B, euclid, 1, 1, true),
                search(bw, 0, 0, B, B, manh, 1, 1, true),
                search(bw, 0, 0, B, B, perfect, 1, 1, true)};
        String[] names = {"h = 0 (Dijkstra)", "h = straight-line distance", "h = rows apart + columns apart", "h = the true remaining distance"};
        int open = 0;
        for (boolean[] row : bw) for (boolean x : row) if (!x) open++;
        StringJoiner lj = new StringJoiner(" ; ");
        for (int i = 0; i < 4; i++) {
            check(rs[i].cost == truth[0][0], names[i] + " finds a shortest path");
            lj.add(String.format("%s: %,d squares taken", names[i], rs[i].expanded));
        }
        check(rs[0].expanded > rs[1].expanded && rs[1].expanded > rs[2].expanded && rs[2].expanded > rs[3].expanded, "better estimates take fewer squares");
        check(rs[3].expanded == truth[0][0] + 1, "a perfect estimate walks straight along a shortest path");
        System.out.printf("large: a %d x %d map, %.0f%% of squares walled at random, %,d open ; from one corner to the other, shortest path %d steps, found by all four ; %s (only the path itself)%n",
                big, big, 100.0 * (big * big - open) / (big * big), open, truth[0][0], lj);

        // ---- 3. many random maps ----------------------------------------------------------------------------------------
        int maps = 2000, sz = 40, greedyLonger = 0, astarFewer = 0;
        double worstGreedy = 1;
        long sumDij = 0, sumAst = 0, sumGre = 0;
        int[][] ends = new int[maps][4];
        boolean[][][] walls = new boolean[maps][][];
        int[][][] truths = new int[maps][][];
        for (int m = 0; m < maps; m++) {
            boolean[][] w;
            int a, b, c, d;
            int[][] dist;
            do {
                w = new boolean[sz][sz];
                for (int i = 0; i < sz; i++) for (int j = 0; j < sz; j++) w[i][j] = uniform() < 0.3;
                a = (int) (uniform() * sz); b = (int) (uniform() * sz); c = (int) (uniform() * sz); d = (int) (uniform() * sz);
                w[a][b] = false; w[c][d] = false;
                dist = distances(w, c, d);
            } while (dist[a][b] < 1);
            walls[m] = w; truths[m] = dist; ends[m] = new int[]{a, b, c, d};
            final int fc = c, fd = d;
            Estimate h = (r, q) -> Math.abs(r - fc) + Math.abs(q - fd);
            Result rd = search(w, a, b, c, d, none, 1, 0, true);
            Result ra = search(w, a, b, c, d, h, 1, 1, true);
            Result rg = search(w, a, b, c, d, h, 0, 1, false);
            int gl = pathLength(rg, sz, c, d);
            check(ra.cost == dist[a][b] && rd.cost == dist[a][b], "map " + m + ": A* and Dijkstra are shortest");
            if (gl > dist[a][b]) greedyLonger++;
            worstGreedy = Math.max(worstGreedy, (double) gl / dist[a][b]);
            if (ra.expanded <= rd.expanded) astarFewer++;
            sumDij += rd.expanded; sumAst += ra.expanded; sumGre += rg.expanded;
        }
        check(astarFewer == maps, "A* never takes more squares than Dijkstra here");
        System.out.printf("many: %,d random %d x %d maps, 30%% walls, random start and goal ; A* found a shortest path on all %,d ; the greedy method returned a longer path on %,d (%.0f%%), at worst %.1f times too long ; squares taken on average: Dijkstra %.0f, A* %.0f, greedy %.0f%n",
                maps, sz, sz, maps, greedyLonger, 100.0 * greedyLonger / maps, worstGreedy, (double) sumDij / maps, (double) sumAst / maps, (double) sumGre / maps);

        // ---- 4. weighted A* --------------------------------------------------------------------------------------------
        StringJoiner wj = new StringJoiner(" ; ");
        for (double w : new double[]{1, 1.5, 2, 3, 5}) {
            Result r = search(bw, 0, 0, B, B, manh, 1, w, true);
            check(r.cost >= truth[0][0] && r.cost <= w * truth[0][0], "weight " + w + " stays within the bound");
            wj.add(String.format("w = %s: %,d squares, path %d (%.3f times the shortest)", w == Math.floor(w) ? String.valueOf((int) w) : String.valueOf(w), r.expanded, r.cost, (double) r.cost / truth[0][0]));
        }
        System.out.printf("weighted: the large map with f = g + w h ; %s%n", wj);

        // ---- 5. an estimate that is admissible but not consistent ------------------------------------------------------
        int wrongNoReopen = 0, totalReopened = 0, mapsReopened = 0;
        double worstNoReopen = 1;
        seed = 1972L;
        for (int m = 0; m < maps; m++) {
            boolean[][] w = walls[m];
            int[][] dist = truths[m];
            double[][] factor = new double[sz][sz];
            for (int i = 0; i < sz; i++) for (int j = 0; j < sz; j++) factor[i][j] = uniform();
            Estimate h = (r, q) -> dist[r][q] < 0 ? 0 : factor[r][q] * dist[r][q];       // never more than the truth
            int a = ends[m][0], b = ends[m][1], c = ends[m][2], d = ends[m][3];
            Result noRe = search(w, a, b, c, d, h, 1, 1, false);
            Result re = search(w, a, b, c, d, h, 1, 1, true);
            int lenNo = pathLength(noRe, sz, c, d);
            check(re.cost == dist[a][b], "map " + m + ": with reopening the answer is shortest");
            if (lenNo > dist[a][b]) { wrongNoReopen++; worstNoReopen = Math.max(worstNoReopen, (double) lenNo / dist[a][b]); }
            totalReopened += re.reopened;
            if (re.reopened > 0) mapsReopened++;
        }
        check(wrongNoReopen > 0, "the inconsistent estimate misleads A* without reopening");
        System.out.printf("inconsistent: the same %,d maps, estimate = the true distance times a random number between 0 and 1, fixed for each square (never too high, but it can drop by more than one in a single step) ; A* that never takes a square twice returned a longer path on %,d maps, at worst %.2f times too long ; A* that reopens a square when a shorter way to it appears was right on all %,d, reopening %,d squares on %,d maps%n",
                maps, wrongNoReopen, worstNoReopen, maps, totalReopened, mapsReopened);

        System.out.println("AStar: " + passed + " checks passed");
    }
}
