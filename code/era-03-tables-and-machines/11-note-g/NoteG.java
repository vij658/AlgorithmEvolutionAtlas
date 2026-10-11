import java.math.BigInteger;
import java.util.*;

/**
 * Era 3, topic 11: Lovelace's Note G (Menabrea's Sketch of the Analytical Engine, translated with notes by A.A.L.,
 * London, 1843).
 *
 * HOW IT WORKS
 *   The Analytical Engine was to have a store of numbered columns (variables V1, V2, ...), a mill that does one
 *   arithmetic operation at a time, and punched cards saying which operation to apply to which columns; a set of cards
 *   could be repeated, making a loop. Note G shows how such an engine would compute a Bernoulli number from the ones
 *   before it, using the identity (in Lovelace's numbering, B1 = 1/6, B3 = -1/30, B5 = 1/42, B7 = -1/30):
 *     0 = A0 + A1 B1 + A3 B3 + ... + B_(2n-1),   A0 = -(1/2)(2n - 1)/(2n + 1),   A1 = 2n/2,
 *     and each later A is the one before times two more falling factors over two more rising ones.
 *   The middle terms all have the same shape, so one group of operations, repeated, computes them all.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Runs a 25-operation program in the style of Note G (store, mill, a repeated group) for Lovelace's B7, in exact
 *      fractions, and counts the operations executed. It is a reconstruction: the table itself could not be read in an
 *      opened copy, so the operation numbers here are this program's own.
 *   2. Checks the program's B1 to B19 (Lovelace's numbering) against the standard recurrence.
 *   3. Runs it with the division of operation 4 the wrong way round, the bug Wikipedia reports in the printed table,
 *      and shows the wrong B7.
 *   4. Counts how the work grows with n.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java NoteG.java
 *   Expected output: expected-output.txt in this folder.
 */
public class NoteG {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** An exact fraction. */
    record Q(BigInteger n, BigInteger d) {
        static Q of(long a) { return new Q(BigInteger.valueOf(a), BigInteger.ONE); }
        static Q of(long a, long b) { return new Q(BigInteger.valueOf(a), BigInteger.valueOf(b)).norm(); }
        Q norm() {
            if (d.signum() < 0) return new Q(n.negate(), d.negate()).norm();
            BigInteger g = n.gcd(d); return g.signum() == 0 ? new Q(BigInteger.ZERO, BigInteger.ONE) : new Q(n.divide(g), d.divide(g));
        }
        Q add(Q o) { return new Q(n.multiply(o.d).add(o.n.multiply(d)), d.multiply(o.d)).norm(); }
        Q sub(Q o) { return new Q(n.multiply(o.d).subtract(o.n.multiply(d)), d.multiply(o.d)).norm(); }
        Q mul(Q o) { return new Q(n.multiply(o.n), d.multiply(o.d)).norm(); }
        Q div(Q o) { return new Q(n.multiply(o.d), d.multiply(o.n)).norm(); }
        Q neg() { return new Q(n.negate(), d); }
        public String toString() { return d.equals(BigInteger.ONE) ? n.toString() : n + "/" + d; }
    }

    /** One operation card: kind, two source columns, a destination column. */
    record Op(int num, char kind, int a, int b, int dest, String note) {}

    // the program: operations 1-12 set up, 13-23 repeat once for each middle term, 24-25 finish
    static final Op[] PROGRAM = {
        new Op(1, 'x', 2, 3, 4, "2n into V4 (and V5, V6)"),
        new Op(2, '-', 4, 1, 4, "2n - 1"),
        new Op(3, '+', 5, 1, 5, "2n + 1"),
        new Op(4, '/', 4, 5, 11, "(2n - 1)/(2n + 1)"),
        new Op(5, '/', 11, 2, 11, "half of it"),
        new Op(6, '-', 13, 11, 13, "A0 = -(1/2)(2n - 1)/(2n + 1)"),
        new Op(7, '-', 3, 1, 10, "n - 1: the count"),
        new Op(8, '+', 2, 7, 7, "2"),
        new Op(9, '/', 6, 7, 11, "A1 = 2n/2"),
        new Op(10, 'x', 21, 11, 12, "B1 A1"),
        new Op(11, '+', 12, 13, 13, "A0 + B1 A1"),
        new Op(12, '-', 10, 1, 10, "count down"),
        new Op(13, '-', 6, 1, 6, "next falling factor"),
        new Op(14, '+', 1, 7, 7, "next rising factor"),
        new Op(15, '/', 6, 7, 8, "their quotient"),
        new Op(16, 'x', 8, 11, 11, "into A"),
        new Op(17, '-', 6, 1, 6, "next falling factor"),
        new Op(18, '+', 1, 7, 7, "next rising factor"),
        new Op(19, '/', 6, 7, 9, "their quotient"),
        new Op(20, 'x', 9, 11, 11, "the next A"),
        new Op(21, 'x', 22, 11, 12, "B A (the B column advances each time)"),
        new Op(22, '+', 12, 13, 13, "add to the sum"),
        new Op(23, '-', 10, 1, 10, "count down"),
        new Op(24, '-', 0, 13, 24, "B_(2n-1) = -(the sum)"),
        new Op(25, '+', 1, 3, 3, "n + 1, ready for the next"),
    };

    static long executed;

    /** Run the program for n, given the earlier Bernoulli numbers B1, B3, ... (Lovelace's numbering). */
    static Q run(int n, List<Q> earlier, boolean bug, List<String> trace) {
        Map<Integer, Q> V = new HashMap<>();
        V.put(0, Q.of(0)); V.put(1, Q.of(1)); V.put(2, Q.of(2)); V.put(3, Q.of(n));
        for (int c : new int[]{4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 24}) V.put(c, Q.of(0));
        int bIndex = 1;                                             // the first middle term uses B3
        V.put(21, earlier.get(0));
        int pc = 0;
        while (pc < PROGRAM.length) {
            Op op = PROGRAM[pc];
            int a = op.a(), b = op.b();
            if (op.num() == 4 && bug) { int t = a; a = b; b = t; }     // the printed table divides the wrong way round
            if (op.num() == 21) V.put(22, earlier.get(bIndex));
            Q x = V.get(a), y = V.get(b), r = switch (op.kind()) {
                case '+' -> x.add(y); case '-' -> x.sub(y); case 'x' -> x.mul(y); default -> x.div(y);
            };
            if (op.num() == 1) { V.put(4, r); V.put(5, r); V.put(6, r); } else V.put(op.dest(), r);
            executed++;
            if (trace != null) trace.add(String.format("%d: V%d %c V%d -> V%d = %s", op.num(), a, op.kind(), b, op.dest(), V.get(op.dest() == 4 && op.num() == 1 ? 4 : op.dest())));
            if (op.num() == 12) {                                       // enter the repeated group only if a middle term remains
                if (V.get(10).n().signum() == 0) { pc = 23; continue; }
            }
            if (op.num() == 21) bIndex++;
            if (op.num() == 23) {                                       // repeat operations 13-23 while the count is not 0
                if (V.get(10).n().signum() != 0) { pc = 12; continue; }
            }
            pc++;
        }
        return V.get(24);
    }

    /** Bernoulli numbers B_0..B_m (modern numbering, B1 = -1/2) from the standard recurrence sum C(m+1,k) B_k = 0. */
    static Q[] bernoulli(int m) {
        Q[] B = new Q[m + 1];
        B[0] = Q.of(1);
        for (int k = 1; k <= m; k++) {
            Q s = Q.of(0);
            BigInteger c = BigInteger.ONE;                              // C(k+1, j)
            for (int j = 0; j < k; j++) {
                s = s.add(new Q(c, BigInteger.ONE).mul(B[j]));
                c = c.multiply(BigInteger.valueOf(k + 1 - j)).divide(BigInteger.valueOf(j + 1));
            }
            B[k] = s.neg().div(Q.of(k + 1));
        }
        return B;
    }

    public static void main(String[] args) {
        Q[] B = bernoulli(40);
        check(B[2].toString().equals("1/6") && B[4].toString().equals("-1/30") && B[6].toString().equals("1/42") && B[8].toString().equals("-1/30"), "the standard values");

        // ---- 1. Lovelace's B7, from B1, B3, B5 ------------------------------------------------------------------------
        List<Q> earlier = List.of(Q.of(1, 6), Q.of(-1, 30), Q.of(1, 42));
        List<String> trace = new ArrayList<>();
        executed = 0;
        Q b7 = run(4, earlier, false, trace);
        long ops4 = executed;
        check(b7.equals(B[8]), "the program's B7 is -1/30 (the modern B8)");
        System.out.printf("noteg: Lovelace's B7 (the modern B8) from B1 = 1/6, B3 = -1/30, B5 = 1/42 ; %d operations executed (25 cards, operations 13 to 23 repeated %d times) ; B7 = %s%n",
                ops4, (ops4 - 14) / 11, b7);
        StringJoiner tj = new StringJoiner(" ; ");
        for (int i = 0; i < 6; i++) tj.add(trace.get(i));
        System.out.printf("trace: %s ; ... ; %s%n", tj, trace.get(trace.size() - 2));

        // ---- 2. the program's numbers against the standard recurrence --------------------------------------------------
        List<Q> got = new ArrayList<>(List.of(Q.of(1, 6)));
        StringJoiner seq = new StringJoiner(", ");
        seq.add("B1 = 1/6");
        for (int n = 2; n <= 10; n++) {
            Q v = run(n, got, false, null);
            check(v.equals(B[2 * n]), "the program agrees with the recurrence");
            got.add(v);
            seq.add("B" + (2 * n - 1) + " = " + v);
        }
        System.out.printf("series: each result fed into the next run: %s ; every one equals the standard value%n", seq);

        // ---- 3. the bug ------------------------------------------------------------------------------------------------
        Q wrong = run(4, earlier, true, null);
        check(!wrong.equals(B[8]), "with operation 4 reversed, B7 is wrong");
        List<Q> chain = new ArrayList<>(List.of(Q.of(1, 6)));
        StringJoiner bad = new StringJoiner(", ");
        for (int n = 2; n <= 5; n++) { Q v = run(n, chain, true, null); chain.add(v); bad.add("B" + (2 * n - 1) + " = " + v); }
        System.out.printf("bug: with operation 4 dividing (2n + 1) by (2n - 1) instead, A0 = -(1/2)(9/7) for n = 4 and B7 comes out %s instead of %s ; fed forward from B1, the run gives %s%n",
                wrong, b7, bad);

        // ---- 4. growth ------------------------------------------------------------------------------------------------
        StringJoiner grow = new StringJoiner(" ; ");
        List<Q> g2 = new ArrayList<>(List.of(Q.of(1, 6)));
        long total = 0;
        for (int n = 2; n <= 20; n++) {
            executed = 0;
            Q v = run(n, g2, false, null);
            g2.add(v);
            total += executed;
            check(v.equals(B[2 * n]), "B up to B39");
            check(executed == 14 + 11L * (n - 2), "operations: 14 plus 11 for each middle term");
            if (n == 4 || n == 10 || n == 20) grow.add(String.format("B%d: %d operations", 2 * n - 1, executed));
        }
        System.out.printf("growth: %s ; operations for B_(2n-1) = 14 + 11(n - 2) ; all of B3 to B39 in %,d operations ; B39 = %s%n", grow, total, g2.get(g2.size() - 1));

        System.out.printf("NoteG: %d checks passed%n", passed);
    }
}
