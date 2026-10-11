import java.util.*;

/**
 * Era 4, topic 7: Turing's machines (1936).
 *
 * HOW IT WORKS
 *   A Turing machine has a tape of squares, a head that scans one square, and a finite table. Each line of the table
 *   says: in this state (Turing's "m-configuration"), reading this symbol, write a symbol, move one square left or
 *   right (or stay), and go to that state. That is all, and Turing argued that it is all a person computing with
 *   pencil and paper needs. Because the table is finite, it can be written out as a string of letters (Turing's
 *   "standard description") and then as a number (its "description number"). A universal machine reads such a
 *   number from its tape and does what the described machine would do: the program is data. The price is that no
 *   machine can take any description and decide whether that machine will run properly for ever or not; today the
 *   question is usually put as whether it halts.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Runs the first example of Turing's paper, which prints 0 1 0 1 ... on every other square.
 *   2. Writes its standard description and description number by Turing's rules, and checks them against the
 *      number printed in 1936; decodes the number back into a table and runs that (a universal machine in miniature).
 *   3. Does the same for the two-state example on Wikipedia's "Description number" page.
 *   4. Runs every machine with two states and two symbols from a blank tape: those that halt do so within 6 steps.
 *   5. Runs Marxen and Buntrock's five-state machine (1989), proved the five-state "busy beaver" in 2024: it halts
 *      after 47,176,870 steps. A test that simply waits 10 million steps would call it a machine that never halts.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java TuringMachines.java
 *   Expected output: expected-output.txt in this folder.
 */
public class TuringMachines {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** One line of a table: in state q reading symbol s, write w, move m (-1 left, 0 none, +1 right), go to state n. */
    record Rule(int q, int s, int w, int m, int n) {}

    static final int HALT = -1;

    /** A machine run on a tape of int symbols (0 = blank). Returns the number of moves made, or -1 if it did not halt. */
    static final class Run {
        int[] tape = new int[1 << 16];
        int head = 1 << 15, state = 0, lo = head, hi = head;
        long moves = 0;
        final Map<Long, Rule> table = new HashMap<>();
        Run(List<Rule> rules) { for (Rule r : rules) table.put(key(r.q, r.s), r); }
        static long key(int q, int s) { return (long) q * 1000 + s; }
        /** Returns false when the machine halts, or meets a state and symbol with no rule. */
        boolean step() {
            Rule r = table.get(key(state, tape[head]));
            if (r == null) return false;
            tape[head] = r.w;
            head += r.m;
            lo = Math.min(lo, head);
            hi = Math.max(hi, head);
            state = r.n;
            moves++;
            return state != HALT;
        }
        long ones() { long c = 0; for (int i = lo; i <= hi; i++) if (tape[i] == 1) c++; return c; }
    }

    // ---- Turing's standard description: letters A C D L R N ; and the digits 1 to 7 ------------------------------------
    /** States are numbered from 1 (q1 = DA), symbols from 0 (S0 = blank = D, S1 = DC, S2 = DCC). */
    static String standardDescription(List<Rule> rules) {
        StringBuilder sb = new StringBuilder();
        for (Rule r : rules)
            sb.append("D").append("A".repeat(r.q + 1))
              .append("D").append("C".repeat(r.s))
              .append("D").append("C".repeat(r.w))
              .append(r.m < 0 ? "L" : r.m > 0 ? "R" : "N")
              .append("D").append("A".repeat(r.n + 1))
              .append(";");
        return sb.toString();
    }

    static String descriptionNumber(String sd) {
        StringBuilder sb = new StringBuilder();
        for (char c : sd.toCharArray()) sb.append("ACDLRN;".indexOf(c) + 1);
        return sb.toString();
    }

    /** Read a description number back into a table: the universal machine's first job. */
    static List<Rule> decode(String dn) {
        StringBuilder sd = new StringBuilder();
        for (char c : dn.toCharArray()) sd.append("ACDLRN;".charAt(c - '1'));
        List<Rule> rules = new ArrayList<>();
        for (String line : sd.toString().split(";")) {
            // D A^i D C^j D C^k M D A^m
            int p = 1, i = 0, j = 0, k = 0, m = 0;
            while (line.charAt(p) == 'A') { i++; p++; }
            p++;                                                            // D
            while (line.charAt(p) == 'C') { j++; p++; }
            p++;                                                            // D
            while (line.charAt(p) == 'C') { k++; p++; }
            char mv = line.charAt(p++);
            p++;                                                            // D
            while (p < line.length() && line.charAt(p) == 'A') { m++; p++; }
            rules.add(new Rule(i - 1, j, k, mv == 'L' ? -1 : mv == 'R' ? 1 : 0, m - 1));
        }
        return rules;
    }

    static String tapeString(Run r, int from, int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            int s = r.tape[from + i];
            sb.append(s == 0 ? "_" : s == 1 ? "0" : "1");
            if (i + 1 < count) sb.append(' ');
        }
        return sb.toString();
    }

    public static void main(String[] args) {
        // ---- 1. Turing's first example: b, c, e, f (states 0 to 3); symbols blank 0, "0" 1, "1" 2 ---------------------
        List<Rule> t1 = List.of(
                new Rule(0, 0, 1, +1, 1),     // b, None: P0, R -> c
                new Rule(1, 0, 0, +1, 2),     // c, None: R -> e
                new Rule(2, 0, 2, +1, 3),     // e, None: P1, R -> f
                new Rule(3, 0, 0, +1, 0));    // f, None: R -> b
        Run r1 = new Run(t1);
        int start = r1.head;
        for (int s = 0; s < 40; s++) check(r1.step(), "machine I never stops");
        for (int i = 0; i < 40; i++) {
            int want = i % 2 == 1 ? 0 : (i % 4 == 0 ? 1 : 2);
            check(r1.tape[start + i] == want, "0 and 1 on alternate squares");
        }
        System.out.printf("machine1: Turing's first example, m-configurations b, c, e, f, after 40 moves: %s ; figures on every other square, alternately 0 and 1, and it never stops%n",
                tapeString(r1, start, 20));

        String sd = standardDescription(t1);
        String dn = descriptionNumber(sd);
        String printed = "31332531173113353111731113322531111731111335317";
        check(sd.equals("DADDCRDAA;DAADDRDAAA;DAAADDCCRDAAAA;DAAAADDRDA;"), "standard description");
        check(dn.equals(printed), "description number as printed in 1936");
        System.out.printf("sd: standard description %s ; replacing A, C, D, L, R, N, ; by 1 to 7 gives the description number %s, the number printed in the paper%n", sd, dn);

        List<Rule> back = decode(dn);
        check(back.equals(t1), "the number decodes to the same table");
        Run a = new Run(t1), b = new Run(back);
        for (int s = 0; s < 10000; s++) { a.step(); b.step(); }
        check(Arrays.equals(a.tape, b.tape), "the decoded machine writes the same tape");
        System.out.printf("universal: the description number read back as %d instructions ; run from the number alone, the machine wrote the same tape for 10000 moves%n", back.size());

        // ---- 3. Wikipedia's two-state example ----------------------------------------------------------------------------
        List<Rule> w = List.of(new Rule(0, 0, 2, +1, 1), new Rule(1, 0, 1, +1, 0));
        String wdn = descriptionNumber(standardDescription(w));
        check(wdn.equals("313322531173113325317"), "Wikipedia's example");
        System.out.printf("example: q1 blank -> print 1, right, q2 ; q2 blank -> print 0, right, q1 ; standard description %s ; description number %s, as published%n",
                standardDescription(w), wdn);

        // ---- 4. every machine with two states and two symbols ------------------------------------------------------------
        // each of the 4 lines: write 0 or 1, move left or right, go to A, B or halt: 12 choices, 12^4 machines
        int total = 0, halted = 0, maxSteps = 0, maxOnes = 0, stillRunning = 0;
        int[] byTime = new int[8];
        for (int code = 0; code < 12 * 12 * 12 * 12; code++) {
            List<Rule> rules = new ArrayList<>();
            int c = code;
            for (int q = 0; q < 2; q++)
                for (int s = 0; s < 2; s++) {
                    int x = c % 12; c /= 12;
                    int wr = x % 2, mv = (x / 2) % 2 == 0 ? -1 : 1, nx = x / 4;   // nx: 0 A, 1 B, 2 halt
                    rules.add(new Rule(q, s, wr, mv, nx == 2 ? HALT : nx));
                }
            total++;
            Run r = new Run(rules);
            boolean running = true;
            while (running && r.moves < 1000) running = r.step();
            if (!running) {
                halted++;
                check(r.moves <= 6, "a two-state machine that halts does so within 6 moves");
                maxSteps = Math.max(maxSteps, (int) r.moves);
                maxOnes = Math.max(maxOnes, (int) r.ones());
                byTime[(int) r.moves]++;
            } else stillRunning++;
        }
        check(maxSteps == 6 && maxOnes == 4, "S(2) = 6 and the most ones is 4");
        StringJoiner bt = new StringJoiner(", ");
        for (int s = 1; s <= 6; s++) bt.add(s + " moves: " + byTime[s]);
        System.out.printf("two: all %d machines with 2 states and 2 symbols, from a blank tape ; %d halt (%s) ; the slowest takes %d moves and the most ones left is %d ; the other %d are still running after 1000 moves, and none of them halts between move 7 and move 1000%n",
                total, halted, bt, maxSteps, maxOnes, stillRunning);

        // ---- 5. the five-state busy beaver ---------------------------------------------------------------------------------
        // A0 1RB  A1 1LC  B0 1RC  B1 1RB  C0 1RD  C1 0LE  D0 1LA  D1 1LD  E0 1RH  E1 0LA  (states A..E = 0..4)
        List<Rule> bb = List.of(
                new Rule(0, 0, 1, +1, 1), new Rule(0, 1, 1, -1, 2),
                new Rule(1, 0, 1, +1, 2), new Rule(1, 1, 1, +1, 1),
                new Rule(2, 0, 1, +1, 3), new Rule(2, 1, 0, -1, 4),
                new Rule(3, 0, 1, -1, 0), new Rule(3, 1, 1, -1, 3),
                new Rule(4, 0, 1, +1, HALT), new Rule(4, 1, 0, -1, 0));
        Run r5 = new Run(bb);
        long budget = 10_000_000L;
        boolean haltedEarly = false;
        while (r5.moves < budget) if (!r5.step()) { haltedEarly = true; break; }
        check(!haltedEarly, "still running after 10 million moves");
        while (r5.step()) { }
        check(r5.moves == 47_176_870L && r5.ones() == 4098, "S(5) = 47,176,870 and 4,098 ones");
        System.out.printf("bb5: Marxen and Buntrock's five-state machine halts after %d moves, leaving %d ones on a stretch of %d squares ; after %d moves it was still running, so a test that waits that long would wrongly call it a machine that never halts%n",
                r5.moves, r5.ones(), r5.hi - r5.lo + 1, budget);

        System.out.println("TuringMachines: " + passed + " checks passed");
    }
}
