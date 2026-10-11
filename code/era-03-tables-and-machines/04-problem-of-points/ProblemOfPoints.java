import java.math.BigInteger;
import java.util.*;

/**
 * Era 3, topic 4: the problem of points (Pascal and Fermat, 1654).
 *
 * HOW IT WORKS
 *   Two players stake equal sums on a game of rounds, each round a fair toss; the first to win a set number of rounds
 *   takes everything. The game is stopped early. How should the stakes be split? Fermat's way: count. If A still needs a
 *   rounds and B needs b, the game would certainly be decided within a + b - 1 more rounds; list all 2^(a+b-1) equally
 *   likely ways those rounds could fall, and split the stakes in proportion to the number each player would win.
 *   Pascal's way: work backward. If A needs 0 rounds, A gets everything; if B needs 0, A gets nothing. Otherwise one more
 *   round leaves A needing a - 1 or B needing b - 1, each with chance 1/2, so A's fair share is the average of the two
 *   shares one step later. Filling in a table from the finished games backward gives every answer, without listing
 *   the 2^(a+b-1) outcomes.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Pascal's example from his letter of 29 July 1654: 64 pistoles split 48 to 16 and 56 to 8.
 *   2. Fermat's enumeration and Pascal's table agree, in exact fractions, for every position up to 12 rounds each.
 *   3. Fermat's three-player count from his letter of 25 September 1654: 17 combinations against 5 and 5.
 *   4. The proportional rule (Pacioli, 1494) against the fair shares.
 *   5. Pascal's triangle gives each share in closed form.
 *   6. Work: table cells against enumerated outcomes, and a Monte Carlo estimate against the exact table.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ProblemOfPoints.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ProblemOfPoints {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** An exact fraction num/den, den a power of 2 here. */
    record Q(BigInteger num, BigInteger den) {
        static Q of(long n, long d) { return new Q(BigInteger.valueOf(n), BigInteger.valueOf(d)).norm(); }
        Q norm() { BigInteger g = num.gcd(den); return g.signum() == 0 ? new Q(BigInteger.ZERO, BigInteger.ONE) : new Q(num.divide(g), den.divide(g)); }
        Q plus(Q o) { return new Q(num.multiply(o.den).add(o.num.multiply(den)), den.multiply(o.den)).norm(); }
        Q half() { return new Q(num, den.shiftLeft(1)).norm(); }
        Q times(long k) { return new Q(num.multiply(BigInteger.valueOf(k)), den).norm(); }
        double value() { return num.doubleValue() / den.doubleValue(); }
        public String toString() { return den.equals(BigInteger.ONE) ? num.toString() : num + "/" + den; }
    }

    static long cells;

    /** Pascal: A's share (as a fraction of the stakes) when A needs a rounds and B needs b, filled backward in a table. */
    static Q[][] pascalTable(int A, int B) {
        Q[][] t = new Q[A + 1][B + 1];
        for (int a = 0; a <= A; a++)
            for (int b = 0; b <= B; b++) {
                if (a == 0 && b == 0) continue;
                if (a == 0) t[a][b] = Q.of(1, 1);
                else if (b == 0) t[a][b] = Q.of(0, 1);
                else { t[a][b] = t[a - 1][b].plus(t[a][b - 1]).half(); cells++; }
            }
        return t;
    }

    /** Fermat: list every way the next a + b - 1 rounds could fall, and count those in which A wins. */
    static Q fermat(int a, int b) {
        int n = a + b - 1;
        long wins = 0;
        for (long mask = 0; mask < (1L << n); mask++) if (Long.bitCount(mask) >= a) wins++;   // A wins the rounds whose bit is 1
        return Q.of(wins, 1L << n);
    }

    static BigInteger binom(int n, int k) {
        BigInteger r = BigInteger.ONE;
        for (int i = 0; i < k; i++) r = r.multiply(BigInteger.valueOf(n - i)).divide(BigInteger.valueOf(i + 1));
        return r;
    }

    public static void main(String[] args) {
        // ---- 1. Pascal's letter: a game of three, 32 pistoles each ------------------------------------------------------
        Q[][] t3 = pascalTable(3, 3);
        Q s21 = t3[1][2], s20 = t3[1][3], s10 = t3[2][3];         // A has 2 of 3 (needs 1), B has 1 (needs 2), etc.
        check(s21.times(64).toString().equals("48") && s20.times(64).toString().equals("56"), "64 pistoles: 48 to 16 at two games to one, 56 to 8 at two to none");
        System.out.printf("pascal: a game to 3 rounds, 32 pistoles each (64 in all) ; at 2 rounds to 1 the leader's share is %s of 64 = %s pistoles (the other %s) ; at 2 to 0, %s (the other %s) ; at 1 to 0, %s (the other %s)%n",
                s21, s21.times(64), Q.of(64, 1).plus(new Q(s21.times(64).num.negate(), BigInteger.ONE)), s20.times(64), Q.of(64, 1).plus(new Q(s20.times(64).num.negate(), BigInteger.ONE)),
                s10.times(64), Q.of(64, 1).plus(new Q(s10.times(64).num.negate(), BigInteger.ONE)));

        // ---- 2. Fermat and Pascal agree ----------------------------------------------------------------------------------
        int N = 12, agree = 0;
        cells = 0;
        Q[][] t = pascalTable(N, N);
        long tableCells = cells;
        for (int a = 1; a <= N; a++) for (int b = 1; b <= N; b++) { check(t[a][b].equals(fermat(a, b)), "Fermat's count equals Pascal's table"); agree++; }
        System.out.printf("agree: Fermat's enumeration and Pascal's backward table give the same exact fraction in all %d positions with up to %d rounds needed by each player%n", agree, N);

        // ---- 3. Fermat's three players: one needs 1 round, the other two need 2 each ---------------------------------------
        int[] need = {1, 2, 2};
        int rounds = need[0] + need[1] + need[2] - 2;                // the game is surely over within 3 rounds
        int[] winsBy = new int[3];
        int total = 0;
        int[] seq = new int[rounds];
        for (int code = 0; code < (int) Math.pow(3, rounds); code++) {
            int c = code;
            for (int i = 0; i < rounds; i++) { seq[i] = c % 3; c /= 3; }
            int[] got = new int[3];
            int winner = -1;
            for (int i = 0; i < rounds && winner < 0; i++) { got[seq[i]]++; if (got[seq[i]] == need[seq[i]]) winner = seq[i]; }
            winsBy[winner]++;
            total++;
        }
        check(total == 27 && winsBy[0] == 17 && winsBy[1] == 5 && winsBy[2] == 5, "Fermat: 17 combinations for the first and 5 for each of the others");
        // the same by backward recursion, for three players
        double[] three = threeShares(1, 2, 2);
        check(Math.abs(three[0] - 17 / 27.0) < 1e-15 && Math.abs(three[1] - 5 / 27.0) < 1e-15, "the backward recursion agrees for three players");
        System.out.printf("three: three players needing 1, 2 and 2 rounds ; the game is over within %d rounds, %d equally likely sequences ; the first wins %d, the second %d, the third %d ; shares %d/27, %d/27, %d/27%n",
                rounds, total, winsBy[0], winsBy[1], winsBy[2], winsBy[0], winsBy[1], winsBy[2]);

        // ---- 4. the proportional rule against the fair share ----------------------------------------------------------------
        int target = 5;
        Q[][] t5 = pascalTable(target, target);
        StringJoiner prop = new StringJoiner(" ; ");
        int[][] scores = {{1, 0}, {2, 1}, {3, 1}, {4, 3}, {4, 0}};
        for (int[] sc : scores) {
            double fair = t5[target - sc[0]][target - sc[1]].value();
            double pac = sc[0] / (double) (sc[0] + sc[1]);
            prop.add(String.format("%d to %d: proportional %.1f%%, fair %.1f%%", sc[0], sc[1], 100 * pac, 100 * fair));
        }
        check(Math.abs(t5[4][5].value() - 0.63671875) < 1e-12, "at 1 to 0 in a game to 5, the leader's fair share is 163/256");
        System.out.printf("pacioli: a game to %d rounds, the leader's share of the stakes ; %s%n", target, prop);

        // ---- 5. Pascal's triangle --------------------------------------------------------------------------------------------
        int okTri = 0;
        for (int a = 1; a <= N; a++)
            for (int b = 1; b <= N; b++) {
                int n = a + b - 1;
                BigInteger sum = BigInteger.ZERO;
                for (int k = a; k <= n; k++) sum = sum.add(binom(n, k));
                check(new Q(sum, BigInteger.ONE.shiftLeft(n)).norm().equals(t[a][b]), "the triangle's row sum gives the share");
                okTri++;
            }
        StringJoiner rows = new StringJoiner(" / ");
        for (int n = 0; n <= 6; n++) { StringJoiner r = new StringJoiner(" "); for (int k = 0; k <= n; k++) r.add(binom(n, k).toString()); rows.add(r.toString()); }
        // example: A needs 2, B needs 3: n = 4, A wins with at least 2 of 4: 6 + 4 + 1 = 11 of 16
        check(t[2][3].toString().equals("11/16"), "A needing 2 against B needing 3 has 11/16");
        System.out.printf("triangle: rows 0 to 6: %s ; when A needs 2 and B needs 3, row 4 gives A 6 + 4 + 1 = 11 of 16 ; the row sums match the table in all %d positions%n", rows, okTri);

        // ---- 6. the work ---------------------------------------------------------------------------------------------------
        StringJoiner work = new StringJoiner(" ; ");
        for (int k : new int[]{5, 10, 20, 30}) {
            long tableWork = (long) k * k;                          // one average per cell
            BigInteger outcomes = BigInteger.ONE.shiftLeft(2 * k - 1);
            work.add(String.format("%d rounds each: table %,d cells, enumeration %s outcomes", k, tableWork, String.format("%,d", outcomes)));
        }
        check(tableCells == (long) N * N, "the table has one cell per position");
        Random rnd = new Random(1654);
        int trials = 1_000_000, aWins = 0;
        for (int i = 0; i < trials; i++) {
            int a = 3, b = 5;
            while (a > 0 && b > 0) { if (rnd.nextBoolean()) a--; else b--; }
            if (a == 0) aWins++;
        }
        double mc = aWins / (double) trials, exact = t[3][5].value();
        check(Math.abs(mc - exact) < 0.005, "the simulation is near the exact share");
        System.out.printf("work: %s ; a simulation of %,d finished games for A needing 3 and B needing 5 estimates %.4f, the table's exact %s = %.4f (error %.1e)%n",
                work, trials, mc, t[3][5], exact, Math.abs(mc - exact));

        System.out.printf("ProblemOfPoints: %d checks passed%n", passed);
    }

    /** Three players' fair shares by backward recursion: each round is won by any of the three with chance 1/3. */
    static double[] threeShares(int a, int b, int c) {
        if (a == 0) return new double[]{1, 0, 0};
        if (b == 0) return new double[]{0, 1, 0};
        if (c == 0) return new double[]{0, 0, 1};
        double[] x = threeShares(a - 1, b, c), y = threeShares(a, b - 1, c), z = threeShares(a, b, c - 1);
        return new double[]{(x[0] + y[0] + z[0]) / 3, (x[1] + y[1] + z[1]) / 3, (x[2] + y[2] + z[2]) / 3};
    }
}
