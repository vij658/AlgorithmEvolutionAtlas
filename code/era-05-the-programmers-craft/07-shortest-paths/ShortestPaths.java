import java.util.*;

/**
 * Era 5, topic 7: Dijkstra's shortest paths (Amsterdam, 1956; published 1959).
 *
 * HOW IT WORKS
 *   To find the shortest route from P to every other town, Dijkstra splits the towns into three sets. A: towns whose
 *   shortest distance from P is known. B: towns reached by some road from A, with the best distance found so far.
 *   C: the rest. Start with P alone in A. Repeat: move the town of B with the smallest distance into A (no route can
 *   later beat it, because every other route has to leave A through a town that is already at least as far); then
 *   look along the roads out of that town and improve the distances of its neighbours, moving them from C into B
 *   if they were not there yet. When Q enters A, its distance is final. Road lengths must not be negative.
 *   The same paper solves a second problem: the shortest network joining all towns (grow a tree from one town, always
 *   adding the shortest road to a town not yet in it).
 *
 * WHAT THIS PROGRAM DOES
 *   1. A map of 64 invented towns (Dijkstra's ARMAC demonstration used 64 Dutch cities), roads to near neighbours;
 *      the shortest route between two corners, with the sets A, B, C after the first few steps.
 *   2. Dijkstra's method against Ford's method (improve every road again and again until nothing changes) on 2,000
 *      random maps: the same distances, and the work each needed.
 *   3. How large set B gets, against the number of roads (the paper's point about storage).
 *   4. A road of negative length, where the method's argument fails.
 *   5. The shortest network joining all 64 towns, by Dijkstra's first method and by Kruskal's, the same length.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ShortestPaths.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ShortestPaths {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1956L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % n);
    }

    record Road(int to, int len) {}

    static List<List<Road>> empty(int n) {
        List<List<Road>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        return g;
    }

    static void road(List<List<Road>> g, int a, int b, int len) { g.get(a).add(new Road(b, len)); g.get(b).add(new Road(a, len)); }

    static final int INF = Integer.MAX_VALUE / 2;
    static long selections, looks;
    static int maxB;
    static List<String> snapshots;

    /** Dijkstra's method as in 1959: scan set B for its nearest town (no priority queue). */
    static int[] dijkstra(List<List<Road>> g, int p, int[] prev) {
        int n = g.size();
        int[] dist = new int[n];
        Arrays.fill(dist, INF);
        char[] set = new char[n];
        Arrays.fill(set, 'C');
        dist[p] = 0;
        set[p] = 'B';
        if (prev != null) Arrays.fill(prev, -1);
        maxB = 1;
        int step = 0;
        while (true) {
            int u = -1;
            for (int i = 0; i < n; i++) if (set[i] == 'B' && (u < 0 || dist[i] < dist[u])) u = i;
            if (u < 0) break;
            set[u] = 'A';
            selections++;
            for (Road r : g.get(u)) {
                looks++;
                if (set[r.to()] == 'A') continue;
                if (dist[u] + r.len() < dist[r.to()]) {
                    dist[r.to()] = dist[u] + r.len();
                    if (prev != null) prev[r.to()] = u;
                    set[r.to()] = 'B';
                }
            }
            int b = 0;
            for (char c : set) if (c == 'B') b++;
            maxB = Math.max(maxB, b);
            if (snapshots != null && step < 4) {
                StringBuilder a = new StringBuilder(), bb = new StringBuilder();
                for (int i = 0; i < n; i++) {
                    if (set[i] == 'A') a.append(a.length() > 0 ? " " : "").append(i).append('=').append(dist[i]);
                    if (set[i] == 'B') bb.append(bb.length() > 0 ? " " : "").append(i).append('=').append(dist[i]);
                }
                snapshots.add(String.format("after step %d: A {%s} B {%s}", step + 1, a, bb));
            }
            step++;
        }
        return dist;
    }

    /** Ford's method: go over every road, improving distances, until a full pass changes nothing. */
    static int[] ford(List<List<Road>> g, int p) {
        int n = g.size();
        int[] dist = new int[n];
        Arrays.fill(dist, INF);
        dist[p] = 0;
        for (int pass = 0; pass < n; pass++) {
            boolean changed = false;
            for (int u = 0; u < n; u++) {
                if (dist[u] == INF) continue;
                for (Road r : g.get(u)) {
                    looks++;
                    if (dist[u] + r.len() < dist[r.to()]) { dist[r.to()] = dist[u] + r.len(); changed = true; }
                }
            }
            if (!changed) break;
        }
        return dist;
    }

    /** A map of n towns at random points; each town joined to its k nearest neighbours. */
    static int[][] xy;

    static List<List<Road>> map(int n, int k) {
        xy = new int[n][2];
        for (int i = 0; i < n; i++) { xy[i][0] = rnd(1000); xy[i][1] = rnd(1000); }
        List<List<Road>> g = empty(n);
        Set<Long> have = new HashSet<>();
        for (int i = 0; i < n; i++) {
            Integer[] by = new Integer[n];
            for (int j = 0; j < n; j++) by[j] = j;
            final int a = i;
            Arrays.sort(by, Comparator.comparingInt(j -> d2(a, j)));
            for (int t = 1; t <= k; t++) {
                int j = by[t];
                long key = (long) Math.min(i, j) * n + Math.max(i, j);
                if (have.add(key)) road(g, i, j, (int) Math.round(Math.sqrt(d2(i, j))));
            }
        }
        return g;
    }

    static int d2(int i, int j) { int dx = xy[i][0] - xy[j][0], dy = xy[i][1] - xy[j][1]; return dx * dx + dy * dy; }

    static int roads(List<List<Road>> g) { int m = 0; for (List<Road> l : g) m += l.size(); return m / 2; }

    public static void main(String[] args) {
        // ---- 1. the map of 64 towns -----------------------------------------------------------------------------------------
        List<List<Road>> g = map(64, 4);
        int p = 0, q = 0;
        for (int i = 0; i < 64; i++) {
            if (xy[i][0] + xy[i][1] < xy[p][0] + xy[p][1]) p = i;
            if (xy[i][0] + xy[i][1] > xy[q][0] + xy[q][1]) q = i;
        }
        int[] prev = new int[64];
        snapshots = new ArrayList<>();
        selections = looks = 0;
        int[] dist = dijkstra(g, p, prev);
        List<String> snaps = snapshots;
        snapshots = null;
        long sel64 = selections, look64 = looks;
        int[] fd = ford(g, p);
        check(Arrays.equals(dist, fd), "Ford agrees on the map");
        check(dist[q] < INF, "the map is connected from corner to corner");
        Deque<Integer> route = new ArrayDeque<>();
        for (int v = q; v != -1; v = prev[v]) route.push(v);
        int sum = 0;
        List<Integer> rl = new ArrayList<>(route);
        for (int i = 0; i + 1 < rl.size(); i++) {
            int a = rl.get(i), b = rl.get(i + 1), len = -1;
            for (Road r : g.get(a)) if (r.to() == b) len = r.len();
            sum += len;
        }
        check(sum == dist[q], "the route adds up to the distance");
        StringJoiner rj = new StringJoiner(" ");
        for (int v : rl) rj.add(String.valueOf(v));
        System.out.printf("map: 64 invented towns at random points in a 1000 x 1000 square, each joined to its 4 nearest neighbours: %d roads ; from town %d (bottom left) to town %d (top right) the shortest route is %s, length %d, through %d towns ; Dijkstra's method moved %d towns into A and looked along %d road ends%n",
                roads(g), p, q, rj, dist[q], rl.size(), sel64, look64);
        System.out.println("sets: " + String.join(" ; ", snaps));

        // ---- 2. random maps: Dijkstra against Ford --------------------------------------------------------------------------
        int maps = 2000;
        long dSel = 0, dLook = 0, fLook = 0, totalRoads = 0;
        int biggestB = 0;
        for (int t = 0; t < maps; t++) {
            int n = 20 + rnd(80);
            List<List<Road>> h = empty(n);
            int m = n + rnd(3 * n);
            for (int e = 0; e < m; e++) { int a = rnd(n), b = rnd(n); if (a != b) road(h, a, b, 1 + rnd(100)); }
            totalRoads += roads(h);
            selections = looks = 0;
            int[] d1 = dijkstra(h, 0, null);
            dSel += selections;
            dLook += looks;
            biggestB = Math.max(biggestB, maxB);
            check(maxB < n, "set B never holds every town");
            looks = 0;
            int[] d2 = ford(h, 0);
            fLook += looks;
            check(Arrays.equals(d1, d2), "same distances on random map " + t);
        }
        System.out.printf("random: %,d random maps of 20 to 99 towns, road lengths 1 to 100 ; Dijkstra's method and Ford's gave the same distance to every town ; road ends looked at: Dijkstra %,d, Ford %,d (%.1f times as many) ; Dijkstra also scanned set B once per town to find its nearest member%n",
                maps, dLook, fLook, (double) fLook / dLook);

        // ---- 3. storage ---------------------------------------------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        for (int n : new int[]{64, 256, 1024}) {
            List<List<Road>> h = map(n, 4);
            selections = looks = 0;
            dijkstra(h, 0, null);
            sj.add(String.format("%d towns, %d roads: set B at most %d towns", n, roads(h), maxB));
            check(maxB < n, "set B smaller than the number of towns");
        }
        System.out.printf("storage: the method needs to keep only the roads into set B, one per town of B, never all the roads at once ; %s%n", sj);

        // ---- 4. a negative road ---------------------------------------------------------------------------------------------
        List<List<Road>> neg = empty(4);
        // directed roads: 0->1 (2), 0->2 (5), 2->1 (-4), 1->3 (2)
        neg.get(0).add(new Road(1, 2));
        neg.get(0).add(new Road(2, 5));
        neg.get(2).add(new Road(1, -4));
        neg.get(1).add(new Road(3, 2));
        int[] dn = dijkstra(neg, 0, null), fn = ford(neg, 0);
        check(dn[3] == 4 && fn[3] == 3, "the negative road breaks the argument");
        System.out.printf("negative: one-way roads 0->1 length 2, 0->2 length 5, 2->1 length -4, 1->3 length 2 ; Dijkstra's method fixes town 1 at distance 2 before it sees the road from 2, and gives town 3 the distance %d ; Ford's method finds %d (0, 2, 1, 3) ; the proof needs lengths that are never negative%n",
                dn[3], fn[3]);

        // ---- 5. the shortest network ----------------------------------------------------------------------------------------
        List<List<Road>> full = empty(64);
        seed = 1956L;
        map(64, 4);                                        // same towns as the first map
        for (int i = 0; i < 64; i++) for (int j = i + 1; j < 64; j++) road(full, i, j, (int) Math.round(Math.sqrt(d2(i, j))));
        // Dijkstra's problem 1: grow a tree from town 0
        boolean[] in = new boolean[64];
        int[] best = new int[64];
        Arrays.fill(best, INF);
        best[0] = 0;
        long treeLen = 0;
        for (int k = 0; k < 64; k++) {
            int u = -1;
            for (int i = 0; i < 64; i++) if (!in[i] && (u < 0 || best[i] < best[u])) u = i;
            in[u] = true;
            treeLen += best[u];
            for (Road r : full.get(u)) if (!in[r.to()] && r.len() < best[r.to()]) best[r.to()] = r.len();
        }
        // Kruskal: all roads by length, joining groups
        List<int[]> all = new ArrayList<>();
        for (int i = 0; i < 64; i++) for (Road r : full.get(i)) if (i < r.to()) all.add(new int[]{r.len(), i, r.to()});
        all.sort(Comparator.comparingInt((int[] e) -> e[0]).thenComparingInt(e -> e[1]).thenComparingInt(e -> e[2]));
        int[] parent = new int[64];
        for (int i = 0; i < 64; i++) parent[i] = i;
        long kLen = 0;
        int used = 0;
        for (int[] e : all) {
            int a = e[1], b = e[2];
            while (parent[a] != a) a = parent[a];
            while (parent[b] != b) b = parent[b];
            if (a != b) { parent[a] = b; kLen += e[0]; used++; }
        }
        check(used == 63 && kLen == treeLen, "both methods give the same shortest network");
        System.out.printf("tree: the shortest network joining all 64 towns (any town may be joined to any other) ; Dijkstra's first problem, growing one tree from town 0: length %d ; Kruskal's method, shortest roads first unless they close a loop: length %d, 63 roads, the same%n",
                treeLen, kLen);

        System.out.println("ShortestPaths: " + passed + " checks passed");
    }
}
