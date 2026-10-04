import java.util.*;

/**
 * Entry 36 of the principles catalog (Part 2): Topological sort (Kahn's algorithm)
 *
 * HOW IT WORKS
 *   Kahn's algorithm orders a directed acyclic graph so every edge points forward: repeatedly output a vertex
 *   with no remaining incoming edges. If vertices remain at the end, the graph has a cycle.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java TopologicalSort.java
 *   Expected: the output in expected-output.txt, ending "TopologicalSort: 33598 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class TopologicalSort {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
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

    static List<Integer> topoSortSmallestFirst(int n, int[][] edges) {   // same algorithm with a min-heap: deterministic, lexicographically smallest
        List<List<Integer>> g = new ArrayList<>();
        int[] indeg = new int[n];
        for (int i = 0; i < n; i++) g.add(new ArrayList<>());
        for (int[] e : edges) { g.get(e[0]).add(e[1]); indeg[e[1]]++; }
        PriorityQueue<Integer> ready = new PriorityQueue<>();
        for (int i = 0; i < n; i++) if (indeg[i] == 0) ready.add(i);
        List<Integer> order = new ArrayList<>();
        while (!ready.isEmpty()) {
            int u = ready.poll();
            order.add(u);
            for (int v : g.get(u)) if (--indeg[v] == 0) ready.add(v);
        }
        return order.size() == n ? order : null;
    }

    static boolean nextPermutation(int[] a) {                // advances a to the next permutation in lexicographic order
        int i = a.length - 2;
        while (i >= 0 && a[i] >= a[i + 1]) i--;
        if (i < 0) return false;
        int j = a.length - 1;
        while (a[j] <= a[i]) j--;
        int t = a[i]; a[i] = a[j]; a[j] = t;
        for (int l = i + 1, r = a.length - 1; l < r; l++, r--) { t = a[l]; a[l] = a[r]; a[r] = t; }
        return true;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java TopologicalSort.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 1000; t++) {
            int n = 2 + rnd.nextInt(30);
            List<Integer> perm = new ArrayList<>();
            for (int i = 0; i < n; i++) perm.add(i);
            Collections.shuffle(perm, rnd);
            List<int[]> es = new ArrayList<>();
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (rnd.nextInt(5) == 0) es.add(new int[]{perm.get(i), perm.get(j)});
            int[][] edges = es.toArray(new int[0][]);
            List<Integer> order = topoSort(n, edges);
            check(order != null && order.size() == n, "a DAG always has a topological order");
            int[] pos = new int[n];
            for (int i = 0; i < n; i++) pos[order.get(i)] = i;
            for (int[] e : edges) check(pos[e[0]] < pos[e[1]], "every edge points forward in the order");
            if (edges.length > 0) {
                int[] pick = edges[rnd.nextInt(edges.length)];
                int[][] cyclic = Arrays.copyOf(edges, edges.length + 1);
                cyclic[edges.length] = new int[]{pick[1], pick[0]};              // 2-cycle
                check(topoSort(n, cyclic) == null, "a cycle makes topological sorting impossible");
            }
        }
        check(topoSort(3, new int[][]{{0, 1}, {1, 2}}).equals(List.of(0, 1, 2)), "chain");
        for (int t = 0; t < 300; t++) {                          // the min-heap variant gives the lexicographically smallest order
            int n = 2 + rnd.nextInt(6);                          // 2..7 vertices: all n! orders can be tried
            List<Integer> perm = new ArrayList<>();
            for (int i = 0; i < n; i++) perm.add(i);
            Collections.shuffle(perm, rnd);
            List<int[]> es = new ArrayList<>();
            for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (rnd.nextInt(3) == 0) es.add(new int[]{perm.get(i), perm.get(j)});
            int[][] edges = es.toArray(new int[0][]);
            int[] p = new int[n];
            for (int i = 0; i < n; i++) p[i] = i;
            List<Integer> smallest = null;
            do {                                                 // permutations in lexicographic order: the first valid one is the smallest
                int[] pos = new int[n];
                for (int i = 0; i < n; i++) pos[p[i]] = i;
                boolean ok = true;
                for (int[] e : edges) if (pos[e[0]] >= pos[e[1]]) { ok = false; break; }
                if (ok) { smallest = new ArrayList<>(); for (int x : p) smallest.add(x); break; }
            } while (nextPermutation(p));
            check(smallest != null && smallest.equals(topoSortSmallestFirst(n, edges)), "min-heap Kahn gives the lexicographically smallest topological order");
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2027));
        System.out.println("TopologicalSort: " + passed + " checks passed");
    }
}
