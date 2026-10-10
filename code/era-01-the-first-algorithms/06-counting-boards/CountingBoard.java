import java.util.*;

/**
 * Era 1, topic 6: counting boards and the abacus (the Salamis tablet, c. 300 BCE; Roman hand abaci; the English
 * Exchequer table, first mentioned in 1110; the Chinese suanpan and Japanese soroban).
 *
 * HOW IT WORKS
 *   A counting board is place value you can touch. Each column (or line) stands for ones, tens, hundreds, and so on,
 *   and the number of counters in it is that digit. To add, push the second number's counters onto the board, then
 *   settle: wherever a column holds ten, clear it and put one counter in the next column. Many boards and abaci also
 *   have a counter worth five in each column (a "bi-quinary" layout, as on the Roman hand abacus and the soroban), so a
 *   column never needs more than one five and four ones: five ones are exchanged for a five, two fives for one counter
 *   in the next column. No digit is ever written; the procedure lives in the hands.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Models a plain board (up to 9 counters per column) and a board with fives, adds and subtracts on both by
 *      pushing counters and settling, and checks both against ordinary arithmetic on 400,000 random cases.
 *   2. Counts the work: counters on the board, counters moved, and exchanges, for a worked example and on average.
 *   3. Shows an invariant: however the exchanges are ordered (settling after every addition, or piling counters up
 *      and settling once at the end), their number is the same, because each exchange removes exactly nine counters
 *      net. Delaying the carries is the idea behind the carry-save adders of fast hardware multipliers.
 *   Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CountingBoard.java
 *   Expected output: expected-output.txt in this folder.
 */
public class CountingBoard {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int COLUMNS = 9;                                    // ones up to hundred millions

    /**
     * A counting board. ones[i] counters worth 10^i in column i; fives[i] counters worth 5 x 10^i (always 0 on a plain
     * board). The work done is counted as counters placed, counters removed and exchanges made.
     */
    static final class Board {
        final boolean withFives;
        final int[] ones = new int[COLUMNS + 1], fives = new int[COLUMNS + 1];
        long placed, removed, exchanges;

        Board(boolean withFives) { this.withFives = withFives; }

        long value() {
            long v = 0, p = 1;
            for (int i = 0; i <= COLUMNS; i++, p *= 10) v += (ones[i] + 5L * fives[i]) * p;
            return v;
        }

        int counters() { return Arrays.stream(ones).sum() + Arrays.stream(fives).sum(); }

        /** Push the counters of n onto the board, column by column, without settling. */
        void push(long n) {
            for (int i = 0; n > 0; i++, n /= 10) {
                int dgt = (int) (n % 10);
                if (withFives && dgt >= 5) { fives[i]++; placed++; dgt -= 5; }
                ones[i] += dgt;
                placed += dgt;
            }
        }

        /** Settle: exchange until every column is in standard form (plain: at most 9; with fives: at most 1 five, 4 ones). */
        void settle() {
            for (int i = 0; i < COLUMNS; i++) {
                if (withFives) {
                    while (ones[i] >= 5) { ones[i] -= 5; fives[i]++; removed += 5; placed++; exchanges++; }
                    while (fives[i] >= 2) { fives[i] -= 2; ones[i + 1]++; removed += 2; placed++; exchanges++; }
                    // a carried-in counter can make five ones again in the next column: the loop reaches it next
                } else {
                    while (ones[i] >= 10) { ones[i] -= 10; ones[i + 1]++; removed += 10; placed++; exchanges++; }
                }
            }
        }

        /** Take n away: remove its counters, breaking a counter of the next column (or a five) into smaller ones when short. */
        void take(long n) {
            for (int i = 0; n > 0; i++, n /= 10) {
                int dgt = (int) (n % 10);
                while (columnValue(i) < dgt) borrow(i);
                // remove dgt units from column i, using ones first, then a five (giving change in ones)
                while (dgt > 0) {
                    if (ones[i] > 0) { ones[i]--; removed++; dgt--; }
                    else { fives[i]--; removed++; ones[i] += 5; placed += 5; exchanges++; }
                }
            }
        }

        int columnValue(int i) { return ones[i] + 5 * fives[i]; }

        /** Break one counter from the next column up into ten (or into two fives) in column i. */
        void borrow(int i) {
            int j = i + 1;
            while (columnValue(j) == 0) j++;                           // find a column that has something to break
            for (int k = j; k > i; k--) {
                if (ones[k] > 0) { ones[k]--; removed++; }
                else { fives[k]--; removed++; ones[k] += 4; placed += 4; }  // break a five: four ones stay, one goes down
                if (withFives) { fives[k - 1] += 2; placed += 2; } else { ones[k - 1] += 10; placed += 10; }
                exchanges++;
            }
        }

        String show() {
            StringJoiner j = new StringJoiner(" ");
            int top = COLUMNS;
            while (top > 0 && ones[top] == 0 && fives[top] == 0) top--;
            for (int i = top; i >= 0; i--) j.add(withFives ? fives[i] + "|" + ones[i] : Integer.toString(ones[i]));
            return j.toString();
        }
    }

    public static void main(String[] args) {
        // 1. a worked example on both boards
        long a = 2763, b = 1489;
        for (boolean fives : new boolean[]{false, true}) {
            Board bd = new Board(fives);
            String kind = fives ? "fives" : "plain";
            bd.push(a);
            System.out.printf("work %s %d %d: put down %d -> %s (%d counters)%n", kind, a, b, a, bd.show(), bd.counters());
            bd.push(b);
            System.out.printf("work %s %d %d: push on %d -> %s (%d counters)%n", kind, a, b, b, bd.show(), bd.counters());
            bd.settle();
            System.out.printf("work %s %d %d: settled -> %s (%d counters) value=%d exchanges=%d moves=%d%n", kind, a, b, bd.show(), bd.counters(),
                    bd.value(), bd.exchanges, bd.placed + bd.removed);
            check(bd.value() == a + b, "worked example on the " + kind + " board");
        }

        // 2. random checks and averages
        Random rnd = new Random(300);
        int trials = 100_000;
        for (boolean fives : new boolean[]{false, true}) {
            long sumCounters = 0, sumMoves = 0, sumEx = 0, maxCol = 0;
            for (int t = 0; t < trials; t++) {
                long x = rnd.nextLong(0, 10_000), y = rnd.nextLong(0, 10_000);
                Board bd = new Board(fives);
                bd.push(x);
                long before = bd.placed;
                bd.push(y);
                bd.settle();
                check(bd.value() == x + y, "addition on the board");
                for (int i = 0; i <= COLUMNS; i++) {
                    check(fives ? bd.ones[i] <= 4 && bd.fives[i] <= 1 : bd.ones[i] <= 9, "settled columns are in standard form");
                    maxCol = Math.max(maxCol, bd.ones[i] + bd.fives[i]);
                }
                sumCounters += bd.counters();
                sumMoves += bd.placed + bd.removed - before;              // the work of adding y, not of setting up x
                sumEx += bd.exchanges;
                // subtraction: take y back off
                Board sb = new Board(fives);
                sb.push(x + y);
                sb.settle();
                sb.take(y);
                check(sb.value() == x, "subtraction on the board");
                sb.settle();
                check(sb.value() == x, "subtraction settles");
            }
            System.out.printf("average %s: %d additions of two numbers below 10,000: %.2f counters left on the board, %.2f counters moved, %.2f exchanges per addition; most counters in one settled column %d%n",
                    fives ? "fives" : "plain", trials, (double) sumCounters / trials, (double) sumMoves / trials, (double) sumEx / trials, maxCol);
        }
        System.out.printf("boardcheck: %d additions and %d subtractions on two kinds of board agreed with ordinary arithmetic%n", 2 * trials, 2 * trials);

        // 3. the invariant: settling once or settling every time makes the same number of exchanges
        Random r2 = new Random(1964);
        long[] numbers = new long[1000];
        for (int i = 0; i < numbers.length; i++) numbers[i] = r2.nextLong(0, 100_000);
        long total = Arrays.stream(numbers).sum();
        Board eager = new Board(false), lazy = new Board(false);
        int eagerSettles = 0;
        for (long n : numbers) { eager.push(n); eager.settle(); eagerSettles++; }
        for (long n : numbers) lazy.push(n);
        int mostInColumn = Arrays.stream(lazy.ones).max().getAsInt();
        lazy.settle();
        check(eager.value() == total && lazy.value() == total, "both boards hold the total");
        check(eager.exchanges == lazy.exchanges, "the same number of exchanges either way");
        long putDown = 0;
        for (long n : numbers) { long m = n; while (m > 0) { putDown += m % 10; m /= 10; } }
        check((putDown - lazy.counters()) % 9 == 0 && (putDown - lazy.counters()) / 9 == lazy.exchanges, "exchanges = (counters put down - counters left) / 9");
        System.out.printf("invariant: adding %d random numbers below 100,000 (total %d): settling after each one, %d exchanges over %d settlings; piling up and settling once, %d exchanges (a column held up to %d counters); counters put down %d, left %d, (put down - left) / 9 = %d%n",
                numbers.length, total, eager.exchanges, eagerSettles, lazy.exchanges, mostInColumn, putDown, lazy.counters(), (putDown - lazy.counters()) / 9);
        // with fives the counting is different (exchanges remove 4 or 1 net), but the order still does not matter
        Board eagerF = new Board(true), lazyF = new Board(true);
        for (long n : numbers) { eagerF.push(n); eagerF.settle(); }
        for (long n : numbers) lazyF.push(n);
        lazyF.settle();
        check(eagerF.value() == total && lazyF.value() == total, "fives boards hold the total");
        check(eagerF.exchanges == lazyF.exchanges, "with fives too, the order of exchanges does not change their number");
        System.out.printf("invariant fives: settling after each one, %d exchanges; settling once, %d exchanges%n", eagerF.exchanges, lazyF.exchanges);

        System.out.printf("CountingBoard: %d checks passed%n", passed);
    }
}
