import java.math.BigInteger;
import java.util.*;

/**
 * Era 5, topic 5: dynamic programming (Richard Bellman, RAND, 1950s).
 *
 * HOW IT WORKS
 *   Many plans are made in stages: which road out of this town, how much to order this month, whether to stop or roll
 *   again. Trying every complete plan multiplies the choices at every stage. Bellman's principle of optimality says
 *   that whatever the first decision, the rest of an optimal plan must be optimal for the situation the first
 *   decision leaves. So work backwards: find the best value of every situation at the last stage, then use those
 *   values to find the best value of every situation one stage earlier, and so on to the start. Each situation is
 *   solved once and its value kept in a table. With chance in the process, "best value" becomes "best expected value".
 *
 * WHAT THIS PROGRAM DOES
 *   1. A journey through 10 stages with 5 towns at each: every one of the 1,953,125 routes priced, against working
 *      backwards stage by stage.
 *   2. Counting the routes through a grid: the same sub-questions asked over and over by plain recursion, against a
 *      table that asks each once.
 *   3. A die you may roll up to n times, keeping the last roll: the exact value of the game for each n, as fractions,
 *      and the rule it implies; checked by playing a million games.
 *   4. Packing a knapsack: the table method against all 2^18 choices for 300 random sets of items.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java DynamicProgramming.java
 *   Expected output: expected-output.txt in this folder.
 */
public class DynamicProgramming {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1957L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed >>> 1;
    }

    static int rnd(int n) { return (int) ((next() >>> 20) % n); }

    static double uniform() { return (next() >>> 10) / (double) (1L << 53); }

    // ---- 2. counting paths -------------------------------------------------------------------------------------------
    static long calls;

    static long pathsNaive(int r, int c) {
        calls++;
        if (r == 0 || c == 0) return 1;
        return pathsNaive(r - 1, c) + pathsNaive(r, c - 1);
    }

    // ---- 3. exact fractions ------------------------------------------------------------------------------------------
    record Frac(BigInteger n, BigInteger d) implements Comparable<Frac> {
        static Frac of(long a, long b) { return new Frac(BigInteger.valueOf(a), BigInteger.valueOf(b)).norm(); }
        Frac norm() { BigInteger g = n.gcd(d); return new Frac(n.divide(g), d.divide(g)); }
        Frac add(Frac o) { return new Frac(n.multiply(o.d).add(o.n.multiply(d)), d.multiply(o.d)).norm(); }
        Frac div(long k) { return new Frac(n, d.multiply(BigInteger.valueOf(k))).norm(); }
        public int compareTo(Frac o) { return n.multiply(o.d).compareTo(o.n.multiply(d)); }
        double value() { return n.doubleValue() / d.doubleValue(); }
        public String toString() { return d.equals(BigInteger.ONE) ? n.toString() : n + "/" + d; }
    }

    public static void main(String[] args) {
        // ---- 1. stages --------------------------------------------------------------------------------------------------
        int stages = 10, towns = 5;
        // cost[s][i][j]: from town i at stage s to town j at stage s+1; stage 0 and stage 10 have one town each
        int[][][] cost = new int[stages][][];
        for (int s = 0; s < stages; s++) {
            int from = s == 0 ? 1 : towns, to = s == stages - 1 ? 1 : towns;
            cost[s] = new int[from][to];
            for (int i = 0; i < from; i++) for (int j = 0; j < to; j++) cost[s][i][j] = 1 + rnd(99);
        }
        // every route: choose a town at each of stages 1..9
        long routes = 0, additionsAll = 0;
        int best = Integer.MAX_VALUE;
        int[] choice = new int[stages + 1];
        int middle = stages - 1;
        long total = (long) Math.pow(towns, middle);
        for (long r = 0; r < total; r++) {
            long x = r;
            for (int s = 1; s <= middle; s++) { choice[s] = (int) (x % towns); x /= towns; }
            int c = 0;
            for (int s = 0; s < stages; s++) { c += cost[s][choice[s]][choice[s + 1]]; additionsAll++; }
            best = Math.min(best, c);
            routes++;
        }
        // backwards: value[i] = cheapest cost from town i at stage s to the end
        int[] value = {0};
        long additionsDp = 0;
        int[][] go = new int[stages][];
        for (int s = stages - 1; s >= 0; s--) {
            int from = cost[s].length;
            int[] v = new int[from];
            go[s] = new int[from];
            for (int i = 0; i < from; i++) {
                v[i] = Integer.MAX_VALUE;
                for (int j = 0; j < value.length; j++) {
                    int c = cost[s][i][j] + value[j];
                    additionsDp++;
                    if (c < v[i]) { v[i] = c; go[s][i] = j; }
                }
            }
            value = v;
        }
        check(value[0] == best, "working backwards finds the cheapest route");
        StringJoiner path = new StringJoiner(" ");
        int at = 0, sum = 0;
        for (int s = 0; s < stages; s++) { int j = go[s][at]; sum += cost[s][at][j]; at = j; path.add(String.valueOf(at)); }
        check(sum == best, "the route read off the table costs the minimum");
        System.out.printf("stages: a start, 9 stages of %d towns, a finish, random costs from 1 to 99 ; all %,d routes priced: %,d additions, cheapest %d ; backwards, each town keeping only its best way on: %,d additions, cheapest %d, the same ; the route, as town numbers stage by stage: %s%n",
                towns, routes, additionsAll, best, additionsDp, value[0], path);

        // ---- 2. overlapping sub-questions --------------------------------------------------------------------------------
        StringJoiner pj = new StringJoiner(" ; ");
        for (int n : new int[]{4, 8, 12}) {
            calls = 0;
            long naive = pathsNaive(n, n);
            long[][] t = new long[n + 1][n + 1];
            int entries = 0;
            for (int r = 0; r <= n; r++) for (int c = 0; c <= n; c++) { t[r][c] = (r == 0 || c == 0) ? 1 : t[r - 1][c] + t[r][c - 1]; entries++; }
            check(naive == t[n][n], "same count both ways");
            BigInteger binom = BigInteger.ONE;
            for (int k = 1; k <= n; k++) binom = binom.multiply(BigInteger.valueOf(n + k)).divide(BigInteger.valueOf(k));
            check(binom.longValue() == naive, "C(2n, n)");
            pj.add(String.format("%dx%d grid: %,d routes ; plain recursion made %,d calls, the table filled %d entries", n, n, naive, calls, entries));
        }
        System.out.printf("grid: routes from one corner to the opposite one, moving right or down ; %s ; the recursion asks about the same corners again and again, the table answers each once%n", pj);

        // ---- 3. the die ------------------------------------------------------------------------------------------------------
        List<Frac> v = new ArrayList<>();
        Frac prev = null;
        StringJoiner dj = new StringJoiner(" ; ");
        for (int n = 1; n <= 6; n++) {
            Frac sumF = Frac.of(0, 1);
            int keepFrom = 1;
            for (int face = 1; face <= 6; face++) {
                Frac f = Frac.of(face, 1);
                if (prev == null || f.compareTo(prev) >= 0) sumF = sumF.add(f);
                else { sumF = sumF.add(prev); keepFrom = face + 1; }
            }
            if (prev != null) { keepFrom = 1; while (Frac.of(keepFrom, 1).compareTo(prev) < 0) keepFrom++; }
            Frac val = sumF.div(6);
            v.add(val);
            dj.add(String.format("%d roll%s: %s = %.4f%s", n, n == 1 ? "" : "s", val, val.value(), n == 1 ? "" : String.format(", keep the first roll if it shows %d or more", keepFrom)));
            prev = val;
        }
        check(v.get(0).equals(Frac.of(7, 2)) && v.get(1).equals(Frac.of(17, 4)) && v.get(2).equals(Frac.of(14, 3)), "3.5, 4.25, 14/3");
        // play a million three-roll games with the rule
        int games = 1_000_000;
        long score = 0;
        for (int g = 0; g < games; g++) {
            int r1 = 1 + rnd(6);
            if (r1 >= 5) { score += r1; continue; }
            int r2 = 1 + rnd(6);
            if (r2 >= 4) { score += r2; continue; }
            score += 1 + rnd(6);
        }
        double avg = (double) score / games;
        check(Math.abs(avg - 14.0 / 3) < 0.01, "simulation agrees");
        System.out.printf("dice: roll a die up to n times and keep the last roll ; the value of the game, worked backwards from the last roll: %s ; a million 3-roll games played by that rule averaged %.4f%n", dj, avg);

        // ---- 4. the knapsack -----------------------------------------------------------------------------------------------
        int sets = 300, items = 18;
        long tableOps = 0, subsetOps = 0;
        int exampleBest = -1, exampleCap = 0;
        for (int t = 0; t < sets; t++) {
            int[] w = new int[items], val = new int[items];
            int wsum = 0;
            for (int i = 0; i < items; i++) { w[i] = 1 + rnd(30); val[i] = 1 + rnd(50); wsum += w[i]; }
            int cap = wsum / 3;
            // table: best[c] = best value with capacity c using the items so far
            int[] bestV = new int[cap + 1];
            for (int i = 0; i < items; i++)
                for (int c = cap; c >= w[i]; c--) { bestV[c] = Math.max(bestV[c], bestV[c - w[i]] + val[i]); tableOps++; }
            // every subset, by Gray code
            int bw = 0, bv = 0, brute = 0;
            for (int g = 1; g < (1 << items); g++) {
                int bit = Integer.numberOfTrailingZeros(g);
                boolean in = ((g ^ (g >> 1)) >> bit & 1) == 1;
                bw += in ? w[bit] : -w[bit];
                bv += in ? val[bit] : -val[bit];
                if (bw <= cap && bv > brute) brute = bv;
                subsetOps++;
            }
            check(bestV[cap] == brute, "table equals every subset");
            if (t == 0) { exampleBest = brute; exampleCap = cap; }
        }
        System.out.printf("knapsack: %d random sets of %d items (weights 1 to 30, values 1 to 50), the sack holding a third of the total weight ; the table method and the search through all %,d choices agreed every time ; work: %,d table steps against %,d subsets looked at ; first set: capacity %d, best value %d%n",
                sets, items, 1 << items, tableOps, subsetOps, exampleCap, exampleBest);

        System.out.println("DynamicProgramming: " + passed + " checks passed");
    }
}
