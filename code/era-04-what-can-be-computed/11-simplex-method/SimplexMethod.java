import java.math.BigInteger;
import java.util.*;

/**
 * Era 4, topic 11: the simplex method (Dantzig, 1947).
 *
 * HOW IT WORKS
 *   A linear program asks for numbers x1, ..., xn that make a linear quantity c.x as large as possible, subject to
 *   linear limits A x <= b and x >= 0. The limits cut out a many-sided solid, and if there is a best plan, one sits at
 *   a corner. There are far too many corners to try them all, so the simplex method walks: start at a corner (here,
 *   all x = 0), look for a neighbouring corner that is better, move there, and stop when no neighbour is better. In
 *   table form each move is a "pivot": one variable enters the plan, one leaves, and the table is rewritten by
 *   elimination. Dantzig's rule picks the entering variable with the largest gain per unit; Bland's rule
 *   picks the first that gains at all, and can never cycle (go round a loop of corners for ever).
 *   Every linear program has a dual, a second program whose best value is the same (von Neumann's duality, 1947);
 *   the final table hands over the dual's solution for free, and it certifies the answer.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A simplex method in exact fractions, with Dantzig's and Bland's rules.
 *   2. A small production plan solved corner by corner.
 *   3. 2,000 random small programs: the simplex answer against every corner, and the dual's value against it.
 *   4. How many pivots random programs need as they grow, against the number of constraints.
 *   5. The Klee-Minty cubes (1972), on which Dantzig's rule visits every one of the 2^n corners.
 *   6. Assigning 10 people to 10 jobs: the simplex answer against all 10! assignments; and 70!, Dantzig's example.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SimplexMethod.java
 *   Expected output: expected-output.txt in this folder.
 */
public class SimplexMethod {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** An exact fraction. */
    record Q(BigInteger n, BigInteger d) implements Comparable<Q> {
        static final Q ZERO = of(0), ONE = of(1);
        static Q of(long v) { return new Q(BigInteger.valueOf(v), BigInteger.ONE); }
        static Q make(BigInteger n, BigInteger d) {
            if (d.signum() < 0) { n = n.negate(); d = d.negate(); }
            BigInteger g = n.gcd(d);
            return g.signum() == 0 || g.equals(BigInteger.ONE) ? new Q(n, d) : new Q(n.divide(g), d.divide(g));
        }
        Q add(Q o) { return make(n.multiply(o.d).add(o.n.multiply(d)), d.multiply(o.d)); }
        Q sub(Q o) { return make(n.multiply(o.d).subtract(o.n.multiply(d)), d.multiply(o.d)); }
        Q mul(Q o) { return make(n.multiply(o.n), d.multiply(o.d)); }
        Q div(Q o) { return make(n.multiply(o.d), d.multiply(o.n)); }
        int signum() { return n.signum(); }
        public int compareTo(Q o) { return n.multiply(o.d).compareTo(o.n.multiply(d)); }
        public String toString() { return d.equals(BigInteger.ONE) ? n.toString() : n + "/" + d; }
    }

    /** The result of a simplex run: the best value, the plan, the dual prices, the corners visited. */
    record Result(Q value, Q[] x, Q[] y, int pivots, List<Q[]> path) {}

    /** Maximize c.x subject to A x <= b, x >= 0, with b >= 0, starting from x = 0. */
    static Result simplex(long[][] A, long[] b, long[] c, boolean bland, boolean recordPath) {
        int m = A.length, n = c.length, w = n + m + 1;
        Q[][] T = new Q[m + 1][w];
        int[] basis = new int[m];
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) T[i][j] = Q.of(A[i][j]);
            for (int j = 0; j < m; j++) T[i][n + j] = i == j ? Q.ONE : Q.ZERO;
            T[i][w - 1] = Q.of(b[i]);
            basis[i] = n + i;
        }
        for (int j = 0; j < w; j++) T[m][j] = j < n ? Q.of(-c[j]) : Q.ZERO;
        int pivots = 0;
        List<Q[]> path = new ArrayList<>();
        if (recordPath) path.add(plan(T, basis, n));
        while (true) {
            int enter = -1;
            for (int j = 0; j < w - 1; j++) {
                if (T[m][j].signum() >= 0) continue;
                if (bland) { enter = j; break; }
                if (enter < 0 || T[m][j].compareTo(T[m][enter]) < 0) enter = j;     // Dantzig: the most negative
            }
            if (enter < 0) break;                                                    // no better neighbour: optimal
            int leave = -1;
            Q best = null;
            for (int i = 0; i < m; i++) {
                if (T[i][enter].signum() <= 0) continue;
                Q ratio = T[i][w - 1].div(T[i][enter]);
                int cmp = best == null ? -1 : ratio.compareTo(best);
                if (cmp < 0 || (cmp == 0 && basis[i] < basis[leave])) { best = ratio; leave = i; }
            }
            if (leave < 0) throw new IllegalStateException("unbounded");
            Q p = T[leave][enter];
            for (int j = 0; j < w; j++) T[leave][j] = T[leave][j].div(p);
            for (int i = 0; i <= m; i++) {
                if (i == leave || T[i][enter].signum() == 0) continue;
                Q f = T[i][enter];
                for (int j = 0; j < w; j++) T[i][j] = T[i][j].sub(f.mul(T[leave][j]));
            }
            basis[leave] = enter;
            pivots++;
            if (recordPath) path.add(plan(T, basis, n));
        }
        Q[] y = new Q[m];
        for (int i = 0; i < m; i++) y[i] = T[m][n + i];
        return new Result(T[m][w - 1], plan(T, basis, n), y, pivots, path);
    }

    static Q[] plan(Q[][] T, int[] basis, int n) {
        Q[] x = new Q[n];
        Arrays.fill(x, Q.ZERO);
        for (int i = 0; i < basis.length; i++) if (basis[i] < n) x[basis[i]] = T[i][T[i].length - 1];
        return x;
    }

    /** The best corner by brute force: every choice of n tight constraints among the m + n, solved exactly. */
    static Q bruteForce(long[][] A, long[] b, long[] c) {
        int m = A.length, n = c.length;
        long[][] rows = new long[m + n][];
        long[] rhs = new long[m + n];
        for (int i = 0; i < m; i++) { rows[i] = A[i]; rhs[i] = b[i]; }
        for (int j = 0; j < n; j++) { rows[m + j] = new long[n]; rows[m + j][j] = -1; rhs[m + j] = 0; }   // -x_j <= 0
        Q best = null;
        int[] pick = new int[n];
        for (int mask = 0; mask < (1 << (m + n)); mask++) {
            if (Integer.bitCount(mask) != n) continue;
            int k = 0;
            for (int i = 0; i < m + n; i++) if ((mask >> i & 1) == 1) pick[k++] = i;
            Q[] x = solve(rows, rhs, pick, n);
            if (x == null) continue;
            boolean feasible = true;
            for (int i = 0; i < m + n && feasible; i++) {
                Q s = Q.ZERO;
                for (int j = 0; j < n; j++) s = s.add(Q.of(rows[i][j]).mul(x[j]));
                if (s.compareTo(Q.of(rhs[i])) > 0) feasible = false;
            }
            if (!feasible) continue;
            Q v = Q.ZERO;
            for (int j = 0; j < n; j++) v = v.add(Q.of(c[j]).mul(x[j]));
            if (best == null || v.compareTo(best) > 0) best = v;
        }
        return best;
    }

    /** Solve the n equations rows[pick] . x = rhs[pick] exactly; null if singular. */
    static Q[] solve(long[][] rows, long[] rhs, int[] pick, int n) {
        Q[][] M = new Q[n][n + 1];
        for (int r = 0; r < n; r++) {
            for (int j = 0; j < n; j++) M[r][j] = Q.of(rows[pick[r]][j]);
            M[r][n] = Q.of(rhs[pick[r]]);
        }
        for (int col = 0; col < n; col++) {
            int p = -1;
            for (int r = col; r < n; r++) if (M[r][col].signum() != 0) { p = r; break; }
            if (p < 0) return null;
            Q[] t = M[p]; M[p] = M[col]; M[col] = t;
            for (int r = 0; r < n; r++) {
                if (r == col || M[r][col].signum() == 0) continue;
                Q f = M[r][col].div(M[col][col]);
                for (int j = col; j <= n; j++) M[r][j] = M[r][j].sub(f.mul(M[col][j]));
            }
        }
        Q[] x = new Q[n];
        for (int j = 0; j < n; j++) x[j] = M[j][n].div(M[j][j]);
        return x;
    }

    static long seed = 1947L;

    static int rnd(int k) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) Long.remainderUnsigned(seed >>> 33, k);
    }

    // ---- 4. a fast floating-point simplex for larger random programs (Dantzig's rule) ---------------------------------
    static int pivotsDouble(double[][] A, double[] b, double[] c) {
        int m = A.length, n = c.length, w = n + m + 1;
        double[][] T = new double[m + 1][w];
        for (int i = 0; i < m; i++) { System.arraycopy(A[i], 0, T[i], 0, n); T[i][n + i] = 1; T[i][w - 1] = b[i]; }
        for (int j = 0; j < n; j++) T[m][j] = -c[j];
        int pivots = 0;
        while (true) {
            int enter = -1;
            for (int j = 0; j < w - 1; j++) if (T[m][j] < -1e-9 && (enter < 0 || T[m][j] < T[m][enter])) enter = j;
            if (enter < 0) return pivots;
            int leave = -1;
            for (int i = 0; i < m; i++)
                if (T[i][enter] > 1e-9 && (leave < 0 || T[i][w - 1] / T[i][enter] < T[leave][w - 1] / T[leave][enter])) leave = i;
            double p = T[leave][enter];
            for (int j = 0; j < w; j++) T[leave][j] /= p;
            for (int i = 0; i <= m; i++) {
                if (i == leave) continue;
                double f = T[i][enter];
                if (f != 0) for (int j = 0; j < w; j++) T[i][j] -= f * T[leave][j];
            }
            pivots++;
        }
    }

    static String fmt(Q[] x) {
        StringJoiner j = new StringJoiner(", ", "(", ")");
        for (Q q : x) j.add(q.toString());
        return j.toString();
    }

    public static void main(String[] args) {
        // ---- 2. a small plan, corner by corner ---------------------------------------------------------------------------
        long[][] A = {{1, 0}, {0, 2}, {3, 2}};
        long[] b = {4, 12, 18}, c = {3, 5};
        Result r = simplex(A, b, c, false, true);
        check(r.value.equals(Q.of(36)) && r.x[0].equals(Q.of(2)) && r.x[1].equals(Q.of(6)), "the plan (2, 6) earns 36");
        check(r.value.equals(bruteForce(A, b, c)), "brute force agrees");
        StringJoiner path = new StringJoiner(" -> ");
        for (Q[] p : r.path) {
            Q v = Q.ZERO;
            for (int j = 0; j < c.length; j++) v = v.add(Q.of(c[j]).mul(p[j]));
            path.add(fmt(p) + " earning " + v);
        }
        Q dualValue = Q.ZERO;
        for (int i = 0; i < b.length; i++) dualValue = dualValue.add(Q.of(b[i]).mul(r.y[i]));
        check(dualValue.equals(r.value), "the dual's value equals the plan's");
        System.out.printf("plan: maximize 3x + 5y with x <= 4, 2y <= 12, 3x + 2y <= 18, x, y >= 0 ; Dantzig's rule walks %s ; %d pivots ; dual prices of the three limits %s, and 4, 12, 18 priced at them come to %s, the same as the best plan%n",
                path, r.pivots, fmt(r.y), dualValue);

        // ---- 3. random small programs against brute force, and the dual ------------------------------------------------
        int trials = 2000;
        long totalPivots = 0;
        int maxPivots = 0;
        for (int t = 0; t < trials; t++) {
            int n = 2 + rnd(3), m = 2 + rnd(4);
            long[][] a = new long[m][n];
            long[] bb = new long[m], cc = new long[n];
            for (int i = 0; i < m; i++) { for (int j = 0; j < n; j++) a[i][j] = rnd(10); bb[i] = 1 + rnd(30); }
            for (int j = 0; j < n; j++) cc[j] = 1 + rnd(9);
            for (int j = 0; j < n; j++) {                                   // keep the program bounded: every x_j limited
                boolean limited = false;
                for (int i = 0; i < m; i++) if (a[i][j] > 0) limited = true;
                if (!limited) a[rnd(m)][j] = 1 + rnd(5);
            }
            Result d = simplex(a, bb, cc, false, false);
            Result bl = simplex(a, bb, cc, true, false);
            check(d.value.equals(bruteForce(a, bb, cc)), "simplex equals the best corner");
            check(bl.value.equals(d.value), "Bland's rule agrees with Dantzig's");
            Q dv = Q.ZERO;
            for (int i = 0; i < m; i++) { check(d.y[i].signum() >= 0, "dual prices are not negative"); dv = dv.add(Q.of(bb[i]).mul(d.y[i])); }
            for (int j = 0; j < n; j++) {
                Q s = Q.ZERO;
                for (int i = 0; i < m; i++) s = s.add(Q.of(a[i][j]).mul(d.y[i]));
                check(s.compareTo(Q.of(cc[j])) >= 0, "dual feasible");
            }
            check(dv.equals(d.value), "strong duality");
            totalPivots += d.pivots;
            maxPivots = Math.max(maxPivots, d.pivots);
        }
        System.out.printf("random: %d random programs with 2 to 4 variables and 2 to 5 limits ; the simplex answer equalled the best of all corners every time, Bland's rule agreed, and the dual's value equalled it (strong duality) ; %.2f pivots on average, at most %d%n",
                trials, (double) totalPivots / trials, maxPivots);

        // ---- 4. pivots as programs grow ------------------------------------------------------------------------------------
        StringJoiner grow = new StringJoiner(" ; ");
        for (int size : new int[]{10, 20, 40, 80, 160}) {
            long sum = 0;
            int runs = 10;
            for (int t = 0; t < runs; t++) {
                double[][] a = new double[size][size];
                double[] bb = new double[size], cc = new double[size];
                for (int i = 0; i < size; i++) { for (int j = 0; j < size; j++) a[i][j] = 1 + rnd(100); bb[i] = 1000 + rnd(9000); }
                for (int j = 0; j < size; j++) cc[j] = 1 + rnd(100);
                sum += pivotsDouble(a, bb, cc);
            }
            grow.add(String.format("%d x %d: %.1f pivots", size, size, (double) sum / runs));
        }
        System.out.printf("grow: random dense programs (10 of each size), Dantzig's rule ; %s%n", grow);

        // ---- 5. Klee-Minty cubes ----------------------------------------------------------------------------------------------
        StringJoiner km = new StringJoiner(", ");
        for (int n = 1; n <= 10; n++) {
            long[][] a = new long[n][n];
            long[] bb = new long[n], cc = new long[n];
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < i; j++) a[i][j] = 1L << (i - j + 1);            // 2^(i-j+1) for j < i
                a[i][i] = 1;
                bb[i] = (long) Math.pow(5, i + 1);
                cc[i] = 1L << (n - 1 - i);                                          // 2^(n-j)
            }
            Result k = simplex(a, bb, cc, false, false);
            check(k.pivots == (1 << n) - 1, "Dantzig's rule takes 2^n - 1 pivots on the Klee-Minty cube of dimension " + n);
            check(k.value.equals(Q.of((long) Math.pow(5, n))), "the optimum is 5^n");
            km.add(n + ": " + k.pivots);
        }
        System.out.printf("kleeminty: maximize sum 2^(n-j) x_j with sum_{j<i} 2^(i-j+1) x_j + x_i <= 5^i ; Dantzig's rule pivots for n = %s ; always 2^n - 1, every corner of the squashed cube%n", km);

        // ---- 6. assignment --------------------------------------------------------------------------------------------------
        int N = 10;
        int[][] cost = new int[N][N];
        for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) cost[i][j] = 1 + rnd(99);
        long[][] a = new long[2 * N][N * N];
        long[] bb = new long[2 * N], cc = new long[N * N];
        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++) {
                a[i][i * N + j] = 1;                                                // person i takes at most one job
                a[N + j][i * N + j] = 1;                                            // job j gets at most one person
                cc[i * N + j] = 1000 - cost[i][j];                                  // so a full assignment always pays
            }
        Arrays.fill(bb, 1);
        Result as = simplex(a, bb, cc, true, false);
        int lpCost = 0, ones = 0;
        for (int v = 0; v < N * N; v++) {
            check(as.x[v].equals(Q.ZERO) || as.x[v].equals(Q.ONE), "the simplex answer is whole: 0 or 1");
            if (as.x[v].equals(Q.ONE)) { lpCost += cost[v / N][v % N]; ones++; }
        }
        check(ones == N, "everyone has a job");
        int[] perm = new int[N];
        for (int i = 0; i < N; i++) perm[i] = i;
        int best = Integer.MAX_VALUE;
        long count = 0;
        do {
            int s = 0;
            for (int i = 0; i < N; i++) s += cost[i][perm[i]];
            best = Math.min(best, s);
            count++;
        } while (nextPermutation(perm));
        check(best == lpCost, "the simplex assignment is the cheapest of all");
        BigInteger f70 = BigInteger.ONE;
        for (int i = 2; i <= 70; i++) f70 = f70.multiply(BigInteger.valueOf(i));
        System.out.printf("assign: %d people, %d jobs, random costs 1 to 99 ; the simplex method (Bland's rule, %d pivots) assigns everyone at total cost %d ; checking all %d assignments finds the same minimum ; for 70 people there are 70! = %s assignments, a number of %d digits%n",
                N, N, as.pivots, lpCost, count, f70, f70.toString().length());

        System.out.println("SimplexMethod: " + passed + " checks passed");
    }

    static boolean nextPermutation(int[] p) {
        int i = p.length - 2;
        while (i >= 0 && p[i] >= p[i + 1]) i--;
        if (i < 0) return false;
        int j = p.length - 1;
        while (p[j] <= p[i]) j--;
        int t = p[i]; p[i] = p[j]; p[j] = t;
        for (int x = i + 1, y = p.length - 1; x < y; x++, y--) { t = p[x]; p[x] = p[y]; p[y] = t; }
        return true;
    }
}
