import java.util.*;

/**
 * Era 6, topic 9: depth-first search and linear-time graph algorithms (Hopcroft and Tarjan, 1971-74).
 *
 * HOW IT WORKS
 *   Depth-first search explores a graph the way one explores a maze with a ball of thread: go along an unexplored
 *   edge whenever there is one, and back up only when everything from here has been seen. Numbering the vertices in
 *   the order they are reached, the edges used to arrive form a tree; every other edge of an undirected graph leads
 *   from a vertex back to one of its ancestors (Tarjan called these "fronds"). Each edge is examined a fixed number of
 *   times, so the whole search takes time proportional to V + E.
 *   Tarjan and Hopcroft saw that one extra number per vertex answers questions that had seemed to need much more work.
 *   The "lowpoint" of v is the smallest number reachable from v by going down the tree and then along at most one
 *   frond. A vertex u (not the root) is a cut vertex, whose removal disconnects the graph, exactly when it has a
 *   child v with lowpoint(v) >= number(u). In a directed graph the same idea (LOWLINK) finds the strongly connected
 *   components: the largest groups in which every vertex can reach every other.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A small undirected graph: the search order, tree edges and fronds, lowpoints, cut vertices, and the
 *      biconnected components.
 *   2. A small directed graph: its strongly connected components by Tarjan's method.
 *   3. 2,000 random graphs: cut vertices and strong components against slow methods that remove each vertex or test
 *      every pair for reachability.
 *   4. Graphs from 1,000 to 1,000,000 vertices: the work counted, against V + E, and against the slow method.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java DepthFirst.java
 *   Expected output: expected-output.txt in this folder.
 */
public class DepthFirst {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1972L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int rnd(int n) { return (int) (uniform() * n); }

    static long steps;

    static int[][] adjacency(int n, List<int[]> edges, boolean directed) {
        int[] deg = new int[n];
        for (int[] e : edges) { deg[e[0]]++; if (!directed) deg[e[1]]++; }
        int[][] adj = new int[n][];
        for (int i = 0; i < n; i++) adj[i] = new int[deg[i]];
        int[] fill = new int[n];
        for (int[] e : edges) { adj[e[0]][fill[e[0]]++] = e[1]; if (!directed) adj[e[1]][fill[e[1]]++] = e[0]; }
        return adj;
    }

    // ---- undirected: numbers, lowpoints, cut vertices, biconnected components (iterative, no deep recursion) ---------
    static class Bicon {
        int[] num, low, parent;
        boolean[] cut;
        List<List<int[]>> components = new ArrayList<>();
        List<int[]> treeEdges = new ArrayList<>(), fronds = new ArrayList<>();
        int[] order;
    }

    static Bicon biconnected(int[][] adj) {
        int n = adj.length;
        Bicon b = new Bicon();
        b.num = new int[n]; b.low = new int[n]; b.parent = new int[n]; b.cut = new boolean[n]; b.order = new int[n];
        Arrays.fill(b.num, -1);
        int counter = 0;
        int[] edgeIdx = new int[n], stackV = new int[n];
        Deque<int[]> edgeStack = new ArrayDeque<>();
        for (int r = 0; r < n; r++) {
            if (b.num[r] >= 0) continue;
            int sp = 0, rootChildren = 0;
            stackV[sp++] = r;
            b.parent[r] = -1;
            b.order[counter] = r;
            b.num[r] = b.low[r] = counter++;
            steps++;
            while (sp > 0) {
                int u = stackV[sp - 1];
                if (edgeIdx[u] < adj[u].length) {
                    int v = adj[u][edgeIdx[u]++];
                    steps++;
                    if (b.num[v] < 0) {                                         // a tree edge: go deeper
                        b.parent[v] = u;
                        b.order[counter] = v;
                        b.num[v] = b.low[v] = counter++;
                        steps++;
                        edgeStack.push(new int[]{u, v});
                        b.treeEdges.add(new int[]{u, v});
                        if (u == r) rootChildren++;
                        stackV[sp++] = v;
                    } else if (v != b.parent[u] && b.num[v] < b.num[u]) {      // a frond, back to an ancestor
                        b.low[u] = Math.min(b.low[u], b.num[v]);
                        edgeStack.push(new int[]{u, v});
                        b.fronds.add(new int[]{u, v});
                    }
                } else {                                                        // u is finished: back up
                    sp--;
                    int p = b.parent[u];
                    if (p >= 0) {
                        b.low[p] = Math.min(b.low[p], b.low[u]);
                        if (b.low[u] >= b.num[p]) {                             // p separates u's subtree
                            if (p != r) b.cut[p] = true;
                            List<int[]> comp = new ArrayList<>();
                            int[] e;
                            do { e = edgeStack.pop(); comp.add(e); } while (!(e[0] == p && e[1] == u));
                            b.components.add(comp);
                        }
                    }
                }
            }
            if (rootChildren > 1) b.cut[r] = true;
        }
        return b;
    }

    // ---- directed: Tarjan's strongly connected components (iterative) -------------------------------------------------
    static int[] strongComponents(int[][] adj) {
        int n = adj.length, counter = 0, compCount = 0;
        int[] num = new int[n], low = new int[n], comp = new int[n], edgeIdx = new int[n], callStack = new int[n];
        boolean[] onStack = new boolean[n];
        int[] stack = new int[n];
        int top = 0;
        Arrays.fill(num, -1);
        for (int r = 0; r < n; r++) {
            if (num[r] >= 0) continue;
            int sp = 0;
            callStack[sp++] = r;
            num[r] = low[r] = counter++;
            stack[top++] = r; onStack[r] = true;
            steps++;
            while (sp > 0) {
                int u = callStack[sp - 1];
                if (edgeIdx[u] < adj[u].length) {
                    int v = adj[u][edgeIdx[u]++];
                    steps++;
                    if (num[v] < 0) {
                        num[v] = low[v] = counter++;
                        stack[top++] = v; onStack[v] = true;
                        callStack[sp++] = v;
                        steps++;
                    } else if (onStack[v]) low[u] = Math.min(low[u], num[v]);
                } else {
                    sp--;
                    if (low[u] == num[u]) {                                    // u is the root of a component
                        int w;
                        do { w = stack[--top]; onStack[w] = false; comp[w] = compCount; } while (w != u);
                        compCount++;
                    }
                    if (sp > 0) { int p = callStack[sp - 1]; low[p] = Math.min(low[p], low[u]); }
                }
            }
        }
        return comp;
    }

    // ---- slow methods ------------------------------------------------------------------------------------------------
    static int countPieces(int[][] adj, int removed) {
        int n = adj.length, pieces = 0;
        boolean[] seen = new boolean[n];
        for (int s = 0; s < n; s++) {
            if (s == removed || seen[s]) continue;
            pieces++;
            ArrayDeque<Integer> q = new ArrayDeque<>(List.of(s));
            seen[s] = true;
            while (!q.isEmpty()) { int u = q.poll(); for (int v : adj[u]) { steps++; if (v != removed && !seen[v]) { seen[v] = true; q.add(v); } } }
        }
        return pieces;
    }

    static boolean[][] reach(int[][] adj) {
        int n = adj.length;
        boolean[][] r = new boolean[n][n];
        for (int s = 0; s < n; s++) {
            ArrayDeque<Integer> q = new ArrayDeque<>(List.of(s));
            r[s][s] = true;
            while (!q.isEmpty()) { int u = q.poll(); for (int v : adj[u]) { steps++; if (!r[s][v]) { r[s][v] = true; q.add(v); } } }
        }
        return r;
    }

    static List<int[]> randomEdges(int n, int m, boolean directed) {
        Set<Long> seen = new HashSet<>();
        List<int[]> edges = new ArrayList<>();
        while (edges.size() < m) {
            int a = rnd(n), b = rnd(n);
            if (a == b) continue;
            long key = directed ? (long) a * n + b : (long) Math.min(a, b) * n + Math.max(a, b);
            if (seen.add(key)) edges.add(new int[]{a, b});
        }
        return edges;
    }

    static String name(int v) { return String.valueOf((char) ('A' + v)); }

    public static void main(String[] args) {
        // ---- 1. a small undirected graph ------------------------------------------------------------------------------
        String[] smallEdges = {"AB", "BC", "CA", "CD", "DE", "EF", "FD", "DG", "GH", "HI", "IG", "BJ"};
        List<int[]> se = new ArrayList<>();
        for (String s : smallEdges) se.add(new int[]{s.charAt(0) - 'A', s.charAt(1) - 'A'});
        int sn = 10;
        int[][] sadj = adjacency(sn, se, false);
        Bicon sb = biconnected(sadj);
        StringJoiner ord = new StringJoiner(" "), lows = new StringJoiner(" "), tree = new StringJoiner(" "), fr = new StringJoiner(" "), cuts = new StringJoiner(" "), comps = new StringJoiner(" ; ");
        for (int i = 0; i < sn; i++) ord.add(name(sb.order[i]));
        for (int i = 0; i < sn; i++) lows.add(name(i) + "=" + sb.num[i] + "/" + sb.low[i]);
        for (int[] e : sb.treeEdges) tree.add(name(e[0]) + name(e[1]));
        for (int[] e : sb.fronds) fr.add(name(e[0]) + name(e[1]));
        for (int i = 0; i < sn; i++) if (sb.cut[i]) cuts.add(name(i));
        for (List<int[]> c : sb.components) {
            TreeSet<String> vs = new TreeSet<>();
            for (int[] e : c) { vs.add(name(e[0])); vs.add(name(e[1])); }
            comps.add(String.join("", vs));
        }
        check(cuts.toString().equals("B C D G"), "the cut vertices of the small graph");
        check(sb.components.size() == 6, "six biconnected components: three triangles and three single edges");
        System.out.printf("small: edges %s ; search from A, vertices in the order reached: %s ; tree edges %s ; fronds %s ; number/lowpoint: %s ; cut vertices (a child's lowpoint does not reach above them): %s ; biconnected components: %s%n",
                String.join(" ", smallEdges), ord, tree, fr, lows, cuts, comps);

        // ---- 2. a small directed graph ---------------------------------------------------------------------------------
        String[] dEdges = {"AB", "BC", "CA", "BD", "DE", "EF", "FD", "GF", "GH", "HG", "HI", "IJ", "JI"};
        List<int[]> de = new ArrayList<>();
        for (String s : dEdges) de.add(new int[]{s.charAt(0) - 'A', s.charAt(1) - 'A'});
        int[][] dadj = adjacency(10, de, true);
        int[] dc = strongComponents(dadj);
        TreeMap<Integer, StringBuilder> groups = new TreeMap<>();
        for (int v = 0; v < 10; v++) groups.computeIfAbsent(dc[v], x -> new StringBuilder()).append(name(v));
        StringJoiner gj = new StringJoiner(" ");
        for (StringBuilder g : groups.values()) gj.add("{" + g + "}");
        check(groups.size() == 4, "four strong components");
        System.out.printf("directed: edges %s ; strong components, in the order Tarjan's method completes them: %s ; each is finished when the search backs out of the first vertex it reached in it%n",
                String.join(" ", dEdges), gj);

        // ---- 3. random graphs against slow methods --------------------------------------------------------------------
        int trials = 2000, cutsFound = 0, compsFound = 0;
        for (int t = 0; t < trials; t++) {
            int n = 4 + rnd(27), m = rnd(2 * n);
            int[][] adj = adjacency(n, randomEdges(n, Math.min(m, n * (n - 1) / 2), false), false);
            Bicon b = biconnected(adj);
            int base = countPieces(adj, -1);
            for (int v = 0; v < n; v++) {
                boolean slowCut = countPieces(adj, v) > base - (adj[v].length == 0 ? 1 : 0);
                check(slowCut == b.cut[v], "cut vertex " + v + " of graph " + t);
                if (slowCut) cutsFound++;
            }
            int[][] dadj2 = adjacency(n, randomEdges(n, Math.min(rnd(2 * n), n * (n - 1)), true), true);
            int[] comp = strongComponents(dadj2);
            boolean[][] r = reach(dadj2);
            Set<Integer> distinctComps = new HashSet<>();
            for (int a = 0; a < n; a++) {
                distinctComps.add(comp[a]);
                for (int c = 0; c < n; c++) check((comp[a] == comp[c]) == (r[a][c] && r[c][a]), "strong component pair");
            }
            compsFound += distinctComps.size();
        }
        System.out.printf("check: %,d random undirected graphs and %,d random directed graphs of 4 to 30 vertices ; every cut vertex found by lowpoints is one whose removal splits the graph, and no other (%,d cut vertices in all) ; every pair of vertices is in the same strong component exactly when each can reach the other (%,d components in all)%n",
                trials, trials, cutsFound, compsFound);

        // ---- 4. linear time ------------------------------------------------------------------------------------------
        StringJoiner lj = new StringJoiner(" ; ");
        for (int n = 1000; n <= 1_000_000; n *= 10) {
            int m = 3 * n;
            int[][] adj = adjacency(n, randomEdges(n, m, true), true);
            steps = 0;
            strongComponents(adj);
            check(steps == n + m, "every vertex is numbered once and every edge examined once");
            lj.add(String.format("V=%,d, E=%,d: %,d steps", n, m, steps));
        }
        int n2 = 2000;
        int[][] adj2 = adjacency(n2, randomEdges(n2, 3 * n2, true), true);
        steps = 0;
        strongComponents(adj2);
        long fastSteps = steps;
        steps = 0;
        reach(adj2);
        long slowSteps = steps;
        check(slowSteps > 100 * fastSteps, "the pairwise method is far slower");
        System.out.printf("linear: strong components of random directed graphs with 3 edges per vertex ; a step is numbering a vertex or examining an edge ; %s ; exactly V + E every time ; on the graph of %,d vertices, finding everything each vertex can reach takes %,d steps against %,d (%,.0f times more)%n",
                lj, n2, slowSteps, fastSteps, (double) slowSteps / fastSteps);

        System.out.println("DepthFirst: " + passed + " checks passed");
    }
}
