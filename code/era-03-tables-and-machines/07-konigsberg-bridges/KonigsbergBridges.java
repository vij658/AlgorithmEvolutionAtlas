import java.util.*;

/**
 * Era 3, topic 7: the bridges of Königsberg (Euler, presented 1735, dated 1736, printed 1741; Hierholzer 1873).
 *
 * HOW IT WORKS
 *   Forget distances and shapes; keep only which piece of land each bridge joins. A walker who enters a piece of land
 *   by one bridge must leave it by another, so the bridges at every piece of land are used in pairs, except where the
 *   walk starts and where it ends. So a walk crossing every bridge exactly once is possible only if zero or two pieces
 *   of land have an odd number of bridges (Euler). Conversely, if the land is connected and zero or two pieces are odd,
 *   such a walk exists (Hierholzer): walk until you are stuck, which can only happen at the end; then, from any place on
 *   the walk that still has unused bridges, walk a closed loop and splice it in; repeat.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Builds Königsberg: four pieces of land A (the island), B, C, D and seven bridges, and counts bridges per piece.
 *   2. Repeats Euler's own count: how often each letter must appear in a route, against the letters a route can have.
 *   3. Searches every walk that never repeats a bridge, to confirm that none crosses all seven.
 *   4. Adds an eighth bridge, finds the route with Hierholzer's splicing, and checks it.
 *   5. Tests Euler's condition against exhaustive search on 20,000 random multigraphs, and times Hierholzer against
 *      search.
 *   6. Full circle: a de Bruijn sequence (every 4-digit binary code exactly once) as a route through a graph.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java KonigsbergBridges.java
 *   Expected output: expected-output.txt in this folder.
 */
public class KonigsbergBridges {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** A multigraph: edges[i] = {u, v}. */
    record Graph(int n, int[][] edges) {
        int[] degrees() { int[] d = new int[n]; for (int[] e : edges) { d[e[0]]++; d[e[1]]++; } return d; }
        int odd() { int c = 0; for (int x : degrees()) if (x % 2 == 1) c++; return c; }
        boolean connected() {                                   // over vertices that have edges
            int[] par = new int[n]; for (int i = 0; i < n; i++) par[i] = i;
            for (int[] e : edges) union(par, e[0], e[1]);
            int root = -1; int[] d = degrees();
            for (int i = 0; i < n; i++) if (d[i] > 0) { int r = find(par, i); if (root < 0) root = r; else if (r != root) return false; }
            return true;
        }
    }

    static int find(int[] p, int x) { while (p[x] != x) x = p[x] = p[p[x]]; return x; }

    static void union(int[] p, int a, int b) { p[find(p, a)] = find(p, b); }

    static long searched;

    /** Exhaustive search: the longest walk (in bridges) that never repeats a bridge, over all starting points. */
    static int longestTrail(Graph g) {
        int best = 0;
        boolean[] used = new boolean[g.edges.length];
        for (int s = 0; s < g.n; s++) best = Math.max(best, dfs(g, s, used, 0));
        return best;
    }

    static int dfs(Graph g, int at, boolean[] used, int len) {
        searched++;
        int best = len;
        for (int i = 0; i < g.edges.length; i++) {
            if (used[i]) continue;
            int[] e = g.edges[i];
            if (e[0] != at && e[1] != at) continue;
            used[i] = true;
            best = Math.max(best, dfs(g, e[0] == at ? e[1] : e[0], used, len + 1));
            used[i] = false;
            if (best == g.edges.length) return best;            // a full route: stop early
        }
        return best;
    }

    static long hierholzerSteps;

    /** Hierholzer: a route over every edge exactly once, as a list of vertices (null if Euler's condition fails). */
    static List<Integer> hierholzer(Graph g) {
        if (!g.connected()) return null;
        int[] d = g.degrees();
        int odd = 0, start = -1;
        for (int i = 0; i < g.n; i++) if (d[i] % 2 == 1) { odd++; start = i; }
        if (odd != 0 && odd != 2) return null;
        if (start < 0) for (int i = 0; i < g.n; i++) if (d[i] > 0) { start = i; break; }
        List<List<int[]>> adj = new ArrayList<>();
        for (int i = 0; i < g.n; i++) adj.add(new ArrayList<>());
        for (int i = 0; i < g.edges.length; i++) { adj.get(g.edges[i][0]).add(new int[]{g.edges[i][1], i}); adj.get(g.edges[i][1]).add(new int[]{g.edges[i][0], i}); }
        boolean[] used = new boolean[g.edges.length];
        int[] ptr = new int[g.n];
        Deque<Integer> stack = new ArrayDeque<>();
        LinkedList<Integer> route = new LinkedList<>();
        stack.push(start);
        while (!stack.isEmpty()) {                              // walk until stuck, then back up and splice
            int v = stack.peek();
            while (ptr[v] < adj.get(v).size() && used[adj.get(v).get(ptr[v])[1]]) ptr[v]++;
            hierholzerSteps++;
            if (ptr[v] == adj.get(v).size()) { route.addFirst(stack.pop()); }
            else { int[] e = adj.get(v).get(ptr[v]); used[e[1]] = true; stack.push(e[0]); }
        }
        return route;
    }

    static boolean isRoute(Graph g, List<Integer> r) {
        if (r == null || r.size() != g.edges.length + 1) return false;
        Map<Long, Integer> left = new HashMap<>();
        for (int[] e : g.edges) left.merge(key(e[0], e[1]), 1, Integer::sum);
        for (int i = 0; i + 1 < r.size(); i++) {
            long k = key(r.get(i), r.get(i + 1));
            Integer c = left.get(k);
            if (c == null || c == 0) return false;
            left.put(k, c - 1);
        }
        return true;
    }

    static long key(int a, int b) { return a < b ? ((long) a << 32) | b : ((long) b << 32) | a; }

    public static void main(String[] args) {
        // ---- 1. Königsberg: A the island (Kneiphof), B and C the banks, D the land between the rivers ------------------
        String[] name = {"A", "B", "C", "D"};
        int A = 0, B = 1, C = 2, D = 3;
        Graph k = new Graph(4, new int[][]{{A, B}, {A, B}, {A, C}, {A, C}, {A, D}, {B, D}, {C, D}});
        int[] deg = k.degrees();
        int sum = 0; for (int x : deg) sum += x;
        check(sum == 2 * k.edges.length, "the bridge counts add up to twice the number of bridges");
        check(deg[A] == 5 && deg[B] == 3 && deg[C] == 3 && deg[D] == 3, "A has 5 bridges, B, C and D have 3");
        System.out.printf("city: 4 pieces of land, 7 bridges ; bridges at A %d, B %d, C %d, D %d ; total %d = twice the number of bridges ; pieces with an odd number of bridges: %d%n",
                deg[A], deg[B], deg[C], deg[D], sum, k.odd());

        // ---- 2. Euler's count -----------------------------------------------------------------------------------------
        // a route over 7 bridges names 8 pieces of land in order; a piece with k bridges (k odd) appears (k + 1)/2 times
        int need = 0;
        StringJoiner apps = new StringJoiner(", ");
        for (int i = 0; i < 4; i++) { int a = (deg[i] + 1) / 2; need += a; apps.add(name[i] + " " + a); }
        int letters = k.edges.length + 1;
        check(need == 9 && letters == 8, "Euler: 9 letters needed, only 8 in a route");
        System.out.printf("euler: a route over %d bridges is a string of %d letters ; with an odd number k of bridges, a piece of land must appear (k + 1)/2 times: %s ; that is %d letters, more than %d, so no route exists%n",
                k.edges.length, letters, apps, need, letters);

        // ---- 3. exhaustive search -------------------------------------------------------------------------------------
        searched = 0;
        int longest = longestTrail(k);
        long kSearched = searched;
        check(longest == 6, "the longest walk without repeating a bridge uses 6 of the 7");
        System.out.printf("search: every walk that never repeats a bridge, from every piece of land: %,d walks examined ; the longest crosses %d of the %d bridges%n",
                kSearched, longest, k.edges.length);

        // ---- 4. an eighth bridge, and Hierholzer -------------------------------------------------------------------------
        Graph k8 = new Graph(4, Arrays.copyOf(k.edges, 8));
        k8.edges[7] = new int[]{B, C};
        List<Integer> route = hierholzer(k8);
        check(k8.odd() == 2 && isRoute(k8, route), "with a bridge from B to C there is a route, from A to D or back");
        StringBuilder rs = new StringBuilder();
        for (int v : route) rs.append(name[v]);
        List<Integer> none = hierholzer(k);
        check(none == null, "Hierholzer refuses the original city");
        System.out.printf("eighth: add a bridge from B to C: bridges at A %d, B %d, C %d, D %d ; two odd pieces, so a route must start at one and end at the other ; Hierholzer's splicing finds %s, crossing all %d bridges%n",
                k8.degrees()[A], k8.degrees()[B], k8.degrees()[C], k8.degrees()[D], rs, k8.edges.length);

        // ---- 5. Euler's condition against search on random multigraphs ---------------------------------------------------
        Random rnd = new Random(1736);
        int trials = 20000, yes = 0, no = 0;
        long searchWork = 0, hierWork = 0;
        for (int t = 0; t < trials; t++) {
            int n = 3 + rnd.nextInt(4), m = 4 + rnd.nextInt(7);
            int[][] e = new int[m][];
            for (int i = 0; i < m; i++) { int u = rnd.nextInt(n), v; do { v = rnd.nextInt(n); } while (v == u); e[i] = new int[]{u, v}; }
            Graph g = new Graph(n, e);
            searched = 0;
            boolean full = longestTrail(g) == m;
            searchWork += searched;
            hierholzerSteps = 0;
            List<Integer> r = hierholzer(g);
            hierWork += hierholzerSteps;
            boolean euler = g.connected() && (g.odd() == 0 || g.odd() == 2);
            check(full == euler, "a route exists exactly when the land is connected and 0 or 2 pieces are odd");
            if (euler) { check(isRoute(g, r), "Hierholzer's route is valid"); yes++; } else no++;
        }
        System.out.printf("random: %,d random multigraphs with 3 to 6 pieces of land and 4 to 10 bridges ; exhaustive search finds a full route in %,d, exactly those where the land is connected and 0 or 2 pieces are odd ; none of the other %,d has one ; work: search examined %,d walks in all, Hierholzer took %,d steps%n",
                trials, yes, no, searchWork, hierWork);

        // larger: a connected graph with 2,000 bridges, all degrees even
        int n = 200, m = 0;
        List<int[]> big = new ArrayList<>();
        for (int i = 0; i < n; i++) { big.add(new int[]{i, (i + 1) % n}); m++; }       // a ring makes it connected with even degrees
        while (m < 2000) {                                                              // add random closed triangles: degrees stay even
            int a = rnd.nextInt(n), b = rnd.nextInt(n), c = rnd.nextInt(n);
            if (a == b || b == c || a == c) continue;
            big.add(new int[]{a, b}); big.add(new int[]{b, c}); big.add(new int[]{c, a}); m += 3;
        }
        Graph gb = new Graph(n, big.toArray(new int[0][]));
        hierholzerSteps = 0;
        List<Integer> rb = hierholzer(gb);
        check(gb.odd() == 0 && isRoute(gb, rb) && rb.get(0).equals(rb.get(rb.size() - 1)), "a closed route over every edge of a big graph");
        System.out.printf("large: a connected graph with %d pieces of land and %,d bridges, every piece even ; Hierholzer finds a closed route over all %,d bridges in %,d steps%n",
                n, gb.edges.length, gb.edges.length, hierholzerSteps);

        // ---- 6. full circle: a de Bruijn sequence ---------------------------------------------------------------------
        // pieces of land = the 8 three-digit binary strings; a bridge from xyz to yzw for each 4-digit string xyzw
        int order = 4, V = 1 << (order - 1);
        List<int[]> db = new ArrayList<>();
        for (int w = 0; w < (1 << order); w++) db.add(new int[]{w >> 1, w & (V - 1)});
        Graph gd = new Graph(V, db.toArray(new int[0][]));
        // in this directed graph every node has 2 in and 2 out; walk it as directed (follow out-edges only)
        List<Integer> cyc = directedEuler(V, db);
        StringBuilder seq = new StringBuilder(String.format("%3s", Integer.toBinaryString(cyc.get(0))).replace(' ', '0'));
        for (int i = 1; i < cyc.size(); i++) seq.append(cyc.get(i) & 1);
        Set<String> seen = new HashSet<>();
        for (int i = 0; i + order <= seq.length(); i++) seen.add(seq.substring(i, i + order));
        check(seen.size() == (1 << order) && seq.length() == (1 << order) + order - 1, "every 4-digit binary string appears exactly once");
        System.out.printf("circle: the %d four-digit binary codes as bridges between %d three-digit codes ; an Euler route through them spells %s (%d digits), which contains every code exactly once ; trying the codes one by one would take %d digits%n",
                1 << order, V, seq, seq.length(), (1 << order) * order);
        check(gd.edges.length == 16, "16 bridges");

        System.out.printf("KonigsbergBridges: %d checks passed%n", passed);
    }

    /** Hierholzer on a directed graph where every node has as many edges in as out. */
    static List<Integer> directedEuler(int V, List<int[]> edges) {
        List<Deque<Integer>> out = new ArrayList<>();
        for (int i = 0; i < V; i++) out.add(new ArrayDeque<>());
        for (int[] e : edges) out.get(e[0]).addLast(e[1]);
        Deque<Integer> stack = new ArrayDeque<>();
        LinkedList<Integer> cyc = new LinkedList<>();
        stack.push(0);
        while (!stack.isEmpty()) {
            int v = stack.peek();
            if (out.get(v).isEmpty()) cyc.addFirst(stack.pop());
            else stack.push(out.get(v).pollFirst());
        }
        return cyc;
    }
}
