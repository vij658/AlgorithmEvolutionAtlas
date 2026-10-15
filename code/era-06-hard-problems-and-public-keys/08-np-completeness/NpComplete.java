import java.util.*;

/**
 * Era 6, topic 8: NP-completeness (Cook 1971, Levin 1973, Karp 1972).
 *
 * HOW IT WORKS
 *   Some problems are easy to check but seem hard to solve. Given a formula in true/false variables, such as
 *       (x1 or x2 or not x3) and (not x1 or x3) and ...
 *   checking a proposed assignment takes one pass over the formula; finding one, or showing there is none, seems to
 *   need trying a large share of all 2^n assignments. NP is the class of problems whose answers can be checked
 *   quickly; P, those that can be solved quickly ("quickly" meaning in a number of steps bounded by a polynomial).
 *   Cook showed that every problem in NP can be translated quickly into a question about such a formula: so if
 *   formulas could be decided quickly, everything in NP could. Karp then translated satisfiability into 21 problems
 *   about graphs, sets and numbers, so all of them stand or fall together. Nobody knows whether they can be solved
 *   quickly; that is the question "P = NP?".
 *   A translation (a "reduction") must preserve the answer exactly. For example, a formula with m clauses of three
 *   literals becomes a graph: one triangle per clause, and an edge between every literal and its negation. The graph
 *   has m vertices with no edge between any two of them exactly when the formula can be satisfied.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A small formula turned into a graph, and a satisfying assignment read off an independent set.
 *   2. A chain of reductions, satisfiability -> 3-satisfiability -> independent set -> vertex cover -> clique,
 *      checked on 1,000 random formulas, each problem solved by its own exhaustive method.
 *   3. Checking against finding: a formula of 60 variables, an answer checked in one pass, found by search.
 *   4. Random 3-satisfiability with 50 variables: the share satisfiable and the work of a search, against the
 *      number of clauses per variable.
 *   5. The work of the search near the hardest ratio, for 20 to 80 variables.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java NpComplete.java
 *   Expected output: expected-output.txt in this folder.
 */
public class NpComplete {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1971L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int rnd(int n) { return (int) (uniform() * n); }

    // A literal is +v or -v for variable v = 1..n; a clause is an int[]; a formula is a List<int[]>.

    static boolean satisfies(List<int[]> f, boolean[] val) {
        for (int[] c : f) {
            boolean ok = false;
            for (int l : c) if (val[Math.abs(l)] == (l > 0)) { ok = true; break; }
            if (!ok) return false;
        }
        return true;
    }

    static boolean bruteSat(List<int[]> f, int n) {
        boolean[] val = new boolean[n + 1];
        for (long mask = 0; mask < (1L << n); mask++) {
            for (int v = 1; v <= n; v++) val[v] = ((mask >> (v - 1)) & 1) == 1;
            if (satisfies(f, val)) return true;
        }
        return false;
    }

    // ---- a search with unit propagation (Davis, Putnam, Logemann, Loveland, 1962) -----------------------------------
    static long nodes;

    static boolean[] dpll(List<int[]> f, int n) {
        int[] val = new int[n + 1];                       // 0 unknown, 1 true, -1 false
        return dpll(f, val) ? toBool(val) : null;
    }

    static boolean[] toBool(int[] val) {
        boolean[] b = new boolean[val.length];
        for (int i = 1; i < val.length; i++) b[i] = val[i] == 1;
        return b;
    }

    static boolean dpll(List<int[]> f, int[] val) {
        nodes++;
        int[] saved = val.clone();
        // unit propagation
        while (true) {
            int unit = 0, shortest = Integer.MAX_VALUE, branch = 0;
            boolean allSat = true;
            for (int[] c : f) {
                int free = 0, last = 0;
                boolean sat = false;
                for (int l : c) {
                    int v = val[Math.abs(l)];
                    if (v == 0) { free++; last = l; }
                    else if ((v == 1) == (l > 0)) { sat = true; break; }
                }
                if (sat) continue;
                allSat = false;
                if (free == 0) { System.arraycopy(saved, 0, val, 0, val.length); return false; }
                if (free == 1) { unit = last; break; }
                if (free < shortest) { shortest = free; branch = last; }
            }
            if (allSat) return true;
            if (unit != 0) { val[Math.abs(unit)] = unit > 0 ? 1 : -1; continue; }
            // branch on a literal of a shortest open clause
            int v = Math.abs(branch);
            val[v] = branch > 0 ? 1 : -1;
            if (dpll(f, val)) return true;
            val[v] = branch > 0 ? -1 : 1;
            if (dpll(f, val)) return true;
            System.arraycopy(saved, 0, val, 0, val.length);
            return false;
        }
    }

    static List<int[]> random3Sat(int n, int m) {
        List<int[]> f = new ArrayList<>();
        for (int i = 0; i < m; i++) {
            int a = 1 + rnd(n), b, c;
            do b = 1 + rnd(n); while (b == a);
            do c = 1 + rnd(n); while (c == a || c == b);
            f.add(new int[]{rnd(2) == 0 ? a : -a, rnd(2) == 0 ? b : -b, rnd(2) == 0 ? c : -c});
        }
        return f;
    }

    // ---- reductions ----------------------------------------------------------------------------------------------------
    /** Any CNF formula to one with exactly three literals per clause, adding new variables; returns {formula, n'}. */
    static Object[] toThreeSat(List<int[]> f, int n) {
        List<int[]> g = new ArrayList<>();
        int next = n;
        for (int[] c : f) {
            if (c.length == 1) {
                int a = ++next, b = ++next;
                g.add(new int[]{c[0], a, b}); g.add(new int[]{c[0], a, -b}); g.add(new int[]{c[0], -a, b}); g.add(new int[]{c[0], -a, -b});
            } else if (c.length == 2) {
                int a = ++next;
                g.add(new int[]{c[0], c[1], a}); g.add(new int[]{c[0], c[1], -a});
            } else if (c.length == 3) g.add(c.clone());
            else {
                int y = ++next;
                g.add(new int[]{c[0], c[1], y});
                for (int i = 2; i < c.length - 2; i++) { int z = ++next; g.add(new int[]{-y, c[i], z}); y = z; }
                g.add(new int[]{-y, c[c.length - 2], c[c.length - 1]});
            }
        }
        return new Object[]{g, next};
    }

    /** 3-SAT to a graph on 3m vertices (bitmask adjacency): triangles per clause, edges between opposite literals. */
    static long[] toGraph(List<int[]> g) {
        int V = 3 * g.size();
        long[] adj = new long[V];
        for (int i = 0; i < V; i++)
            for (int j = i + 1; j < V; j++) {
                boolean sameClause = i / 3 == j / 3;
                boolean opposite = g.get(i / 3)[i % 3] == -g.get(j / 3)[j % 3];
                if (sameClause || opposite) { adj[i] |= 1L << j; adj[j] |= 1L << i; }
            }
        return adj;
    }

    /** Largest independent set within the vertex set `alive`, by branching on a vertex of largest degree. */
    static int maxIndependent(long[] adj, long alive) {
        if (alive == 0) return 0;
        int best = -1, bestDeg = -1;
        for (long s = alive; s != 0; s &= s - 1) {
            int v = Long.numberOfTrailingZeros(s), d = Long.bitCount(adj[v] & alive);
            if (d <= 1) return 1 + maxIndependent(adj, alive & ~(1L << v) & ~adj[v]);   // safe to take
            if (d > bestDeg) { bestDeg = d; best = v; }
        }
        int with = 1 + maxIndependent(adj, alive & ~(1L << best) & ~adj[best]);
        int without = maxIndependent(adj, alive & ~(1L << best));
        return Math.max(with, without);
    }

    /** Smallest vertex cover of the edges within `alive`: for a vertex v, either v is in it, or all its neighbours are. */
    static int minCover(long[] adj, long alive) {
        int best = -1, bestDeg = 0;
        for (long s = alive; s != 0; s &= s - 1) {
            int v = Long.numberOfTrailingZeros(s), d = Long.bitCount(adj[v] & alive);
            if (d > bestDeg) { bestDeg = d; best = v; }
        }
        if (best < 0) return 0;                                       // no edges left
        for (long s = alive; s != 0; s &= s - 1) {                    // a vertex with one edge: take its neighbour
            int v = Long.numberOfTrailingZeros(s);
            long nv = adj[v] & alive;
            if (Long.bitCount(nv) == 1) return 1 + minCover(adj, alive & ~nv & ~(1L << v));
        }
        long nb = adj[best] & alive;
        return Math.min(1 + minCover(adj, alive & ~(1L << best)), Long.bitCount(nb) + minCover(adj, alive & ~nb & ~(1L << best)));
    }

    /** Largest clique, by Bron and Kerbosch's method with a pivot. */
    static int maxClique(long[] adj, long R, long P, long X) {
        if (P == 0 && X == 0) return Long.bitCount(R);
        int best = Long.bitCount(R);
        long PX = P | X;
        int pivot = Long.numberOfTrailingZeros(PX), most = -1;
        for (long s = PX; s != 0; s &= s - 1) { int u = Long.numberOfTrailingZeros(s), d = Long.bitCount(adj[u] & P); if (d > most) { most = d; pivot = u; } }
        for (long s = P & ~adj[pivot]; s != 0; s &= s - 1) {
            int v = Long.numberOfTrailingZeros(s);
            best = Math.max(best, maxClique(adj, R | (1L << v), P & adj[v], X & adj[v]));
            P &= ~(1L << v);
            X |= 1L << v;
        }
        return best;
    }

    static String show(List<int[]> f) {
        StringJoiner sj = new StringJoiner(" and ");
        for (int[] c : f) {
            StringJoiner cj = new StringJoiner(" or ", "(", ")");
            for (int l : c) cj.add((l < 0 ? "not x" : "x") + Math.abs(l));
            sj.add(cj.toString());
        }
        return sj.toString();
    }

    public static void main(String[] args) {
        // ---- 1. a small formula as a graph ----------------------------------------------------------------------------
        List<int[]> tiny = List.of(new int[]{1, 2, -3}, new int[]{-1, 3, 4}, new int[]{-2, -3, -4}, new int[]{1, -2, 4});
        long[] tg = toGraph(tiny);
        int edges = 0, cross = 0;
        for (int i = 0; i < 12; i++) edges += Long.bitCount(tg[i]);
        edges /= 2;
        cross = edges - 3 * tiny.size();
        // find an independent set of size 4 by choosing one vertex per triangle
        int[] pick = null;
        for (int code = 0; code < 81 && pick == null; code++) {
            int[] p = {code % 3, code / 3 % 3, code / 9 % 3, code / 27};
            boolean ok = true;
            for (int i = 0; i < 4 && ok; i++) for (int j = i + 1; j < 4 && ok; j++) if ((tg[3 * i + p[i]] >> (3 * j + p[j]) & 1) == 1) ok = false;
            if (ok) pick = p;
        }
        boolean[] val = new boolean[5];
        StringJoiner chosen = new StringJoiner(", ");
        for (int i = 0; i < 4; i++) { int l = tiny.get(i)[pick[i]]; val[Math.abs(l)] = l > 0; chosen.add((l < 0 ? "not x" : "x") + Math.abs(l)); }
        check(satisfies(tiny, val), "the independent set gives a satisfying assignment");
        check(maxIndependent(tg, (1L << 12) - 1) == 4, "4 is the largest");
        System.out.printf("tiny: formula %s ; graph: 12 vertices (one per literal), %d edges (12 inside the 4 triangles, %d joining a literal to its negation) ; an independent set of 4, one vertex per triangle: %s ; set those literals true (others false): x1=%s x2=%s x3=%s x4=%s, and every clause is satisfied%n",
                show(tiny), edges, cross, chosen, val[1], val[2], val[3], val[4]);

        // ---- 2. a chain of reductions ---------------------------------------------------------------------------------
        int trials = 1000, sat = 0, maxV = 0, maxClauses = 0;
        for (int t = 0; t < trials; ) {
            int n = 4, m = 4 + rnd(7);
            List<int[]> f = new ArrayList<>();
            for (int i = 0; i < m; i++) {
                int len = 1 + rnd(4);
                List<Integer> vars = new ArrayList<>();
                for (int v = 1; v <= n; v++) vars.add(v);
                int[] c = new int[len];
                for (int j = 0; j < len; j++) { int v = vars.remove(rnd(vars.size())); c[j] = rnd(2) == 0 ? v : -v; }
                f.add(c);
            }
            Object[] r = toThreeSat(f, n);
            @SuppressWarnings("unchecked") List<int[]> g = (List<int[]>) r[0];
            if (3 * g.size() > 63) continue;                         // keep the graph within 63 vertices
            t++;
            int n3 = (int) r[1], k = g.size(), V = 3 * k;
            boolean a = bruteSat(f, n);
            boolean b = dpll(g, n3) != null;
            long[] adj = toGraph(g);
            long all = V == 64 ? -1L : (1L << V) - 1;
            boolean c = maxIndependent(adj, all) >= k;
            boolean d = minCover(adj, all) <= V - k;
            long[] comp = new long[V];
            for (int i = 0; i < V; i++) comp[i] = ~adj[i] & all & ~(1L << i);
            boolean e = maxClique(comp, 0, all, 0) >= k;
            check(a == b && b == c && c == d && d == e, "all five answers agree on formula " + t);
            if (a) sat++;
            maxV = Math.max(maxV, V);
            maxClauses = Math.max(maxClauses, k);
        }
        check(sat > 100 && trials - sat > 100, "both answers occur often");
        System.out.printf("chain: %,d random formulas in 4 variables, 4 to 10 clauses of 1 to 4 literals ; each one turned into 3-satisfiability (clauses of exactly 3, extra variables added), then a graph (independent set of size m?), then vertex cover (at most 3m - m vertices touching every edge?), then clique in the complementary graph (m vertices all joined?) ; each of the five questions answered by its own exhaustive method: try all 16 assignments, a search with unit propagation, branching for independent sets, branching for covers, Bron and Kerbosch's clique search ; all five answers agree on every formula: %d satisfiable, %d not ; graphs of up to %d vertices%n",
                trials, sat, trials - sat, maxV);

        // ---- 3. checking against finding ------------------------------------------------------------------------------
        int nv = 60, mc = 240;
        List<int[]> big;
        boolean[] answer;
        do {
            big = random3Sat(nv, mc);
            nodes = 0;
            answer = dpll(big, nv);
        } while (answer == null);
        long found = nodes;
        long checks = 0;
        for (int[] c : big) { checks++; boolean ok = false; for (int l : c) if (answer[Math.abs(l)] == (l > 0)) ok = true; check(ok, "clause satisfied"); }
        System.out.printf("check: a random formula of %d variables and %d clauses of 3 ; the search with unit propagation found a satisfying assignment after %,d steps of its tree ; checking it takes one look at each of the %d clauses ; trying every assignment could take up to 2^%d = %,d%n",
                nv, mc, found, checks, nv, 1L << nv);

        // ---- 4. the threshold -----------------------------------------------------------------------------------------
        int n = 50, per = 200;
        StringJoiner tj = new StringJoiner(" ; ");
        double peakRatio = 0;
        long peakMedian = 0;
        double[] ratios = {2.0, 3.0, 3.5, 4.0, 4.25, 4.5, 5.0, 6.0, 8.0};
        double[] satShare = new double[ratios.length];
        for (int ri = 0; ri < ratios.length; ri++) {
            int m = (int) Math.round(ratios[ri] * n), s = 0;
            long[] work = new long[per];
            for (int t = 0; t < per; t++) {
                List<int[]> f = random3Sat(n, m);
                nodes = 0;
                boolean[] a = dpll(f, n);
                if (a != null) { s++; check(satisfies(f, a), "a found assignment satisfies"); }
                work[t] = nodes;
            }
            Arrays.sort(work);
            long median = work[per / 2];
            satShare[ri] = (double) s / per;
            if (median > peakMedian) { peakMedian = median; peakRatio = ratios[ri]; }
            tj.add(String.format("%.2f clauses per variable: %d%% satisfiable, median %,d steps", ratios[ri], Math.round(100.0 * s / per), median));
        }
        check(satShare[0] == 1.0 && satShare[ratios.length - 1] == 0.0, "few clauses: always satisfiable; many: never");
        check(peakRatio >= 4.0 && peakRatio <= 4.5, "the work peaks near the crossover");
        System.out.printf("threshold: random formulas of %d variables, %d formulas for each number of clauses ; %s ; the search works hardest at %.2f clauses per variable, where the share that can be satisfied falls from nearly all to nearly none%n",
                n, per, tj, peakRatio);

        // ---- 5. growth -------------------------------------------------------------------------------------------------
        StringJoiner gj = new StringJoiner(" ; ");
        long prev = 0;
        double lastFactor = 0;
        for (int nn = 20; nn <= 80; nn += 10) {
            int m = (int) Math.round(4.26 * nn), cnt = 100;
            long[] work = new long[cnt];
            for (int t = 0; t < cnt; t++) { List<int[]> f = random3Sat(nn, m); nodes = 0; dpll(f, nn); work[t] = nodes; }
            Arrays.sort(work);
            long med = work[cnt / 2];
            gj.add(String.format("n=%d: %,d", nn, med));
            if (prev > 0) lastFactor = (double) med / prev;
            check(med > prev, "the work grows with n");
            prev = med;
        }
        System.out.printf("growth: median steps of the search on 100 random formulas with 4.26 clauses per variable ; %s ; each 10 more variables multiply the work, by %.1f at the last step%n", gj, lastFactor);

        System.out.println("NpComplete: " + passed + " checks passed");
    }
}
