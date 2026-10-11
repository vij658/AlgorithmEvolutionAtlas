import java.math.BigInteger;
import java.util.*;

/**
 * Era 4, topic 1: Hilbert's questions (1900 and 1928).
 *
 * HOW IT WORKS
 *   Hilbert's tenth problem (Paris, 1900) asks for "a process according to which it can be determined by a finite
 *   number of operations" whether an equation with whole-number coefficients, such as x^3 + y^3 + z^3 = 30, has a
 *   solution in whole numbers. Half of such a process is easy: try every tuple of integers, shell by shell (first all
 *   tuples whose largest entry is 0, then 1, then 2, ...). If a solution exists, the search reaches it after finitely
 *   many tries and stops. If none exists, the search never stops, and watching it tells you nothing. Sometimes a proof
 *   settles the "no" side instead: x^2 + y^2 is never 3 more than a multiple of 4, so x^2 + y^2 = 1103 has no solution,
 *   because 1103 = 4 x 275 + 3. Hilbert hoped some finite process would always decide. In 1970 Matiyasevich, building
 *   on Davis, Putnam and Robinson, proved that none exists. For one unknown there is one: an integer root of a
 *   polynomial must divide its constant term, so only finitely many candidates need testing.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The shell-by-shell search reaches every tuple exactly once (checked for three unknowns, shells 0 to 25).
 *   2. Search: x^2 + y^2 = 1105 and x^3 + y^3 + z^3 = 29 stop with a solution.
 *   3. Proof by remainders: x^2 + y^2 = 1103 is impossible modulo 4, x^3 + y^3 + z^3 = 4 modulo 9; the search agrees
 *      as far as it goes (millions of tuples, none a solution).
 *   4. x^3 + y^3 + z^3 = 30, 33 and 42: no remainder rules them out, a search through shell 200 finds nothing, and the
 *      solutions found by computer in 1999 and 2019 are checked exactly, with the number of tuples a blind search
 *      would have tried before reaching them.
 *   5. One unknown: the divisor test decides 3,000 random polynomials, and a full search agrees every time.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HilbertsQuestions.java
 *   Expected output: expected-output.txt in this folder.
 */
public class HilbertsQuestions {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** An equation  f(x1, ..., xk) = target  with whole-number coefficients. */
    record Eq(String text, int vars, int power, long target) {
        long lhs(long[] v) {                                      // x1^power + ... + xk^power
            long s = 0;
            for (long x : v) s += power == 2 ? x * x : x * x * x;
            return s;
        }
    }

    // ---- 1. the search, shell by shell --------------------------------------------------------------------------------
    interface Visit { boolean at(long[] v); }                     // return true to stop

    static long tried;

    /**
     * Visit every tuple whose largest entry (in absolute value) is exactly r, each once: the first coordinate that
     * reaches r is coordinate i; coordinates before it stay inside the shell, coordinates after it range freely.
     */
    static boolean shell(int k, long r, Visit visit) {
        long[] v = new long[k];
        if (r == 0) { tried++; return visit.at(v); }
        for (int i = 0; i < k; i++)
            for (long s : new long[]{-r, r}) {
                v[i] = s;
                if (fill(v, 0, i, r, visit)) return true;
            }
        return false;
    }

    static boolean fill(long[] v, int j, int i, long r, Visit visit) {
        if (j == v.length) { tried++; return visit.at(v); }
        if (j == i) return fill(v, j + 1, i, r, visit);
        long lim = j < i ? r - 1 : r;
        for (long x = -lim; x <= lim; x++) {
            v[j] = x;
            if (fill(v, j + 1, i, r, visit)) return true;
        }
        return false;
    }

    /** Search shells 0, 1, 2, ... up to maxShell. Returns the first solution found, or null. */
    static long[] search(Eq e, long maxShell, long[] shellFound) {
        long[][] hit = new long[1][];
        tried = 0;
        for (long r = 0; r <= maxShell; r++) {
            boolean stop = shell(e.vars, r, v -> {
                if (e.lhs(v) == e.target) { hit[0] = v.clone(); return true; }
                return false;
            });
            if (stop) { shellFound[0] = r; return hit[0]; }
        }
        return null;
    }

    // ---- 3. proof by remainders ---------------------------------------------------------------------------------------
    /** The smallest m <= maxM for which the equation has no solution even in remainders mod m, or 0 if there is none. */
    static int obstruction(Eq e, int maxM) {
        for (int m = 2; m <= maxM; m++) {
            boolean[] isPow = new boolean[m];
            for (int a = 0; a < m; a++) isPow[(int) (e.power == 2 ? (long) a * a % m : (long) a * a % m * a % m)] = true;
            int t = (int) Math.floorMod(e.target, (long) m);
            boolean possible = false;
            if (e.vars == 2) {
                for (int a = 0; a < m && !possible; a++) if (isPow[a] && isPow[Math.floorMod(t - a, m)]) possible = true;
            } else {
                for (int a = 0; a < m && !possible; a++)
                    for (int b = 0; b < m && !possible; b++)
                        if (isPow[a] && isPow[b] && isPow[Math.floorMod(t - a - b, m)]) possible = true;
            }
            if (!possible) return m;
        }
        return 0;
    }

    static String residues(int power, int m) {
        TreeSet<Integer> s = new TreeSet<>();
        for (int a = 0; a < m; a++) s.add((int) (power == 2 ? (long) a * a % m : (long) a * a % m * a % m));
        StringJoiner j = new StringJoiner(", ");
        for (int x : s) j.add(String.valueOf(x));
        return j.toString();
    }

    // ---- 5. one unknown: the divisor test -----------------------------------------------------------------------------
    /** Integer roots of a[0] + a[1] x + ... + a[n] x^n (a[n] != 0), found by testing divisors of the constant term. */
    static TreeSet<Long> rootsByDivisors(long[] a, long[] ops) {
        TreeSet<Long> roots = new TreeSet<>();
        int low = 0;
        while (low < a.length && a[low] == 0) low++;               // x = 0 is a root; divide out the powers of x
        if (low > 0) roots.add(0L);
        long c = Math.abs(a[low]);
        for (long d = 1; d <= c; d++)
            if (c % d == 0)
                for (long x : new long[]{d, -d}) { ops[0]++; if (eval(a, x) == 0) roots.add(x); }
        return roots;
    }

    static long eval(long[] a, long x) {
        long s = 0;
        for (int i = a.length - 1; i >= 0; i--) s = s * x + a[i];     // Horner's rule
        return s;
    }

    static long seed = 20261011L;

    static int rnd(int n) {                                          // a fixed linear congruential generator
        seed = (seed * 6364136223846793005L + 1442695040888963407L);
        return (int) Long.remainderUnsigned(seed >>> 33, n);
    }

    static String fmt(long[] v) {
        StringJoiner j = new StringJoiner(", ", "(", ")");
        for (long x : v) j.add(String.valueOf(x));
        return j.toString();
    }

    public static void main(String[] args) {
        // ---- 1. every tuple exactly once ------------------------------------------------------------------------------
        int R = 25;
        int side = 2 * R + 1;
        int[] seen = new int[side * side * side];
        long total = 0;
        for (long r = 0; r <= R; r++) {
            tried = 0;
            final long rr = r;
            shell(3, r, v -> {
                long mx = Math.max(Math.abs(v[0]), Math.max(Math.abs(v[1]), Math.abs(v[2])));
                check(mx == rr, "tuple lies on shell " + rr);
                seen[(int) ((v[0] + R) * side * side + (v[1] + R) * side + (v[2] + R))]++;
                return false;
            });
            check(tried == (2 * r + 1) * (2 * r + 1) * (2 * r + 1) - (r == 0 ? 0 : (2 * r - 1) * (2 * r - 1) * (2 * r - 1)), "shell size");
            total += tried;
        }
        for (int s : seen) check(s == 1, "each tuple visited once");
        System.out.printf("shells: three unknowns, shells 0 to %d: %d tuples, each visited exactly once ; shell r holds (2r+1)^3 - (2r-1)^3 tuples%n", R, total);

        // ---- 2. searches that stop ------------------------------------------------------------------------------------
        Eq e1105 = new Eq("x^2 + y^2 = 1105", 2, 2, 1105);
        Eq e29 = new Eq("x^3 + y^3 + z^3 = 29", 3, 3, 29);
        for (Eq e : new Eq[]{e1105, e29}) {
            long[] sh = new long[1];
            long[] sol = search(e, 1000, sh);
            check(sol != null && e.lhs(sol) == e.target, e.text + " solved");
            check(obstruction(e, 60) == 0, e.text + " has no obstruction");
            System.out.printf("found: %s ; the search stops at shell %d after %d tuples with %s%n", e.text, sh[0], tried, fmt(sol));
        }

        // ---- 3. impossible by remainders, and the search agrees as far as it goes ------------------------------------
        Eq e1103 = new Eq("x^2 + y^2 = 1103", 2, 2, 1103);
        Eq e4 = new Eq("x^3 + y^3 + z^3 = 4", 3, 3, 4);
        long[][] caps = {{1000}, {100}};
        Eq[] imp = {e1103, e4};
        for (int k = 0; k < 2; k++) {
            Eq e = imp[k];
            int m = obstruction(e, 60);
            check(m == (k == 0 ? 4 : 9), e.text + " obstruction modulus");
            tried = 0;
            long cap = caps[k][0];
            long none = 0;
            for (long r = 0; r <= cap; r++)
                shell(e.vars, r, v -> { check(e.lhs(v) != e.target, e.text + " has no small solution"); return false; });
            none = tried;
            System.out.printf("impossible: %s ; %s leave remainders {%s} mod %d, and no %d of them add up to %d mod %d ; the search through shell %d tried %d tuples, none a solution%n",
                    e.text, e.power == 2 ? "squares" : "cubes", residues(e.power, m), m, e.vars, Math.floorMod(e.target, (long) m), m, cap, none);
        }

        // ---- 4. sums of three cubes: no obstruction, no small solution, giant solutions -----------------------------
        String[][] giants = {
                {"30", "-283059965", "-2218888517", "2220422932"},
                {"33", "8866128975287528", "-8778405442862239", "-2736111468807040"},
                {"42", "-80538738812075974", "80435758145817515", "12602123297335631"},
        };
        long cap3 = 200;
        for (String[] g : giants) {
            long n = Long.parseLong(g[0]);
            Eq e = new Eq("x^3 + y^3 + z^3 = " + n, 3, 3, n);
            check(obstruction(e, 60) == 0, "no obstruction for " + n);
            long[] sh = new long[1];
            check(search(e, cap3, sh) == null, "no solution through shell " + cap3 + " for " + n);
            long small = tried;
            BigInteger x = new BigInteger(g[1]), y = new BigInteger(g[2]), z = new BigInteger(g[3]);
            BigInteger sum = x.pow(3).add(y.pow(3)).add(z.pow(3));
            check(sum.equals(BigInteger.valueOf(n)), "the known solution for " + n);
            BigInteger r = x.abs().max(y.abs()).max(z.abs());
            BigInteger before = r.shiftLeft(1).subtract(BigInteger.ONE).pow(3);   // tuples in all shells inside r
            System.out.printf("cubes: %d ; no remainder rule up to 60 forbids it ; shells 0 to %d: %d tuples, none ; known solution (%s, %s, %s) checked, cubes sum to %s ; it lies on shell %s ; the shells inside it hold %s tuples (about 10^%d)%n",
                    n, cap3, small, g[1], g[2], g[3], sum, r, before, before.toString().length() - 1);
        }

        // ---- 5. one unknown: a finite process exists ----------------------------------------------------------------
        int polys = 3000, withRoots = 0;
        long divisorTests = 0, searchTests = 0;
        for (int p = 0; p < polys; p++) {
            int deg = 1 + rnd(4);
            long[] a = new long[deg + 1];
            for (int i = 0; i <= deg; i++) a[i] = rnd(61) - 30;
            if (a[deg] == 0) a[deg] = 1 + rnd(30);
            if (p % 3 == 0) {                                        // every third polynomial is built from chosen integer roots
                long[] b = {1};
                for (int i = 0; i < deg; i++) {
                    long root = rnd(21) - 10;
                    long[] nb = new long[b.length + 1];
                    for (int j = 0; j < b.length; j++) { nb[j + 1] += b[j]; nb[j] -= root * b[j]; }
                    b = nb;
                }
                a = b;
            }
            long[] ops = new long[1];
            TreeSet<Long> byDiv = rootsByDivisors(a, ops);
            divisorTests += ops[0];
            // the full search: every integer root satisfies |x| <= 1 + max |a_i / a_n| (Cauchy's bound)
            long bound = 1;
            for (int i = 0; i < a.length - 1; i++) bound = Math.max(bound, 1 + Math.abs(a[i]) / Math.abs(a[a.length - 1]) + 1);
            TreeSet<Long> bySearch = new TreeSet<>();
            for (long x = -bound; x <= bound; x++) { searchTests++; if (eval(a, x) == 0) bySearch.add(x); }
            check(byDiv.equals(bySearch), "divisor test agrees with search");
            if (!byDiv.isEmpty()) withRoots++;
        }
        long[] ex = {-6, 11, -6, 1};                                   // x^3 - 6x^2 + 11x - 6
        long[] ops = new long[1];
        TreeSet<Long> exRoots = rootsByDivisors(ex, ops);
        check(exRoots.equals(new TreeSet<>(List.of(1L, 2L, 3L))), "roots of x^3 - 6x^2 + 11x - 6");
        long[] ex2 = {-1, -1, 0, 0, 0, 1};                             // x^5 - x - 1
        long[] ops2 = new long[1];
        check(rootsByDivisors(ex2, ops2).isEmpty(), "x^5 - x - 1 has no integer root");
        System.out.printf("onevar: x^3 - 6x^2 + 11x - 6: divisors of 6 give %d tests, roots %s ; x^5 - x - 1: %d tests, no integer root ; %d random polynomials of degree 1 to 4: the divisor test (%d evaluations) and a full search (%d evaluations) agree on all, %d have integer roots%n",
                ops[0], exRoots, ops2[0], polys, divisorTests, searchTests, withRoots);

        System.out.println("HilbertsQuestions: " + passed + " checks passed");
    }
}
