import java.math.BigInteger;
import java.util.*;

/**
 * Chapter 1, "Two numbers, one answer": why adding has a carry, and why the carry became the slow part.
 *
 * HOW IT WORKS
 *   Adding two numbers written in columns: each column's total keeps what fits (total mod radix) and passes the
 *   rest up as a carry (total div radix). Because two digits below r plus a carry of 1 never reach 2r, the
 *   carry is always 0 or 1, in any base and even in mixed bases such as pounds, shillings and pence. A counting
 *   board does the same work in two steps: push all the counters on, then settle full columns. In a machine the
 *   carry is the slow part: rippling waits for the longest carry chain (about log2 n columns on random inputs,
 *   n in the worst case), while carry-lookahead combines (generate, propagate) pairs in doubling rounds and
 *   finishes in ceil(log2 n) rounds, at the cost of more work.
 *
 * HOW THIS FILE IS ORGANISED (the banners below follow the chapter's sections)
 *   the carry is an exchange -> the counting board does it in two steps -> the machine: carry-lookahead
 *   -> how long carry chains really are -> a real 64-bit word, added by rippling and by lookahead -> checks.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AddingTwoNumbers.java
 *   Expected: the output in expected-output.txt. Randomized checks use fixed seeds, so it reproduces exactly.
 *
 * The chapter outline and its history fact sheet are in book/era-01-the-first-algorithms/chapter-01-adding-two-numbers/.
 */
public class AddingTwoNumbers {
    static int passed = 0;
    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ======================= the carry is an exchange =======================
    /** What a number written in columns is worth. Column 0 is the smallest unit; radix[i] says how many units of column i make one unit of column i + 1. */
    static BigInteger value(long[] digits, long[] radix) {
        BigInteger total = BigInteger.ZERO, unit = BigInteger.ONE;
        for (int i = 0; i < digits.length; i++) {
            total = total.add(unit.multiply(BigInteger.valueOf(digits[i])));
            if (i + 1 < digits.length) unit = unit.multiply(BigInteger.valueOf(radix[i]));      // one unit of the next column is worth radix[i] units of this one
        }
        return total;
    }

    /** Adds two numbers written in columns (smallest column first, every digit below its column's radix). The extra last slot holds whatever overflows the top column. */
    static long[] addColumns(long[] a, long[] b, long[] radix) {
        long[] sum = new long[a.length + 1];
        long carry = 0;
        for (int i = 0; i < a.length; i++) {
            long total = a[i] + b[i] + carry;                // this column, plus whatever the column below passed up
            sum[i] = total % radix[i];                       // what stays here
            carry = total / radix[i];                        // what is exchanged for one unit of the next column
        }
        sum[a.length] = carry;
        return sum;
    }

    // ======================= the counting board does it in two steps =======================
    /** Step 1 of the board: push both numbers' counters onto the same lines. Nothing is carried yet, so every column could be done at the same moment. */
    static long[] columnSums(long[] a, long[] b) {
        long[] sums = new long[a.length];
        for (int i = 0; i < a.length; i++) sums[i] = a[i] + b[i];
        return sums;
    }

    /** Step 2: sweep up from the smallest line, trading each overfull line for counters on the next one. This part is sequential: one carry can cause the next. */
    static long[] settle(long[] sums, long[] radix) {
        long[] out = new long[sums.length + 1];
        long carry = 0;
        for (int i = 0; i < sums.length; i++) {
            long total = sums[i] + carry;
            out[i] = total % radix[i];
            carry = total / radix[i];
        }
        out[sums.length] = carry;
        return out;
    }

    // ======================= looking ahead =======================
    /** Does this column make a carry all by itself, whatever arrives from below? */
    static boolean generates(long a, long b, long radix) { return a + b >= radix; }
    /** Does this column pass a carry on if one arrives? That happens when it is exactly one short of overflowing (9 in decimal, 1 in binary). */
    static boolean propagates(long a, long b, long radix) { return a + b == radix - 1; }

    /** Carry-lookahead: every carry at once. In each round a column combines what it knows with what the column `span` places below it knows, so the reach doubles.
     *  Returns carryOut[i] = does column i send a carry up. stats[0] counts the rounds, stats[1] the combine steps. */
    static boolean[] lookaheadCarries(long[] a, long[] b, long[] radix, int[] stats) {
        int n = a.length;
        boolean[] g = new boolean[n], p = new boolean[n];
        for (int i = 0; i < n; i++) { g[i] = generates(a[i], b[i], radix[i]); p[i] = propagates(a[i], b[i], radix[i]); }
        for (int span = 1; span < n; span *= 2) {
            boolean[] g2 = g.clone(), p2 = p.clone();
            for (int i = span; i < n; i++) {
                g2[i] = g[i] || (p[i] && g[i - span]);       // my block makes a carry, or it passes on one that the block below makes
                p2[i] = p[i] && p[i - span];                 // my block passes a carry on only if both of its halves do
                stats[1]++;
            }
            g = g2; p = p2;
            stats[0]++;
        }
        return g;                                            // now g[i] describes columns 0..i, so it is the carry out of column i
    }

    static long[] addLookahead(long[] a, long[] b, long[] radix, int[] stats) {
        boolean[] carryOut = lookaheadCarries(a, b, radix, stats);
        long[] sum = new long[a.length + 1];
        for (int i = 0; i < a.length; i++) {
            long carryIn = (i > 0 && carryOut[i - 1]) ? 1 : 0;
            sum[i] = (a[i] + b[i] + carryIn) % radix[i];
        }
        sum[a.length] = carryOut[a.length - 1] ? 1 : 0;
        return sum;
    }

    // ======================= how long can a carry travel =======================
    /** Longest carry chain when adding two binary numbers of `bits` bits: a column that makes a carry by itself, plus the columns directly above it that only pass the carry on. */
    static int longestChain(long a, long b, int bits) {
        int longest = 0, current = 0;
        for (int i = 0; i < bits; i++) {
            long x = (a >>> i) & 1, y = (b >>> i) & 1;
            if (x + y == 2) current = 1;                     // 1 + 1: this column makes a carry itself, and a new chain starts
            else if (x + y == 1 && current > 0) current++;   // 1 + 0 or 0 + 1: a carry that arrives here is passed on
            else current = 0;                                // 0 + 0 (or nothing arriving): the chain has stopped
            longest = Math.max(longest, current);
        }
        return longest;
    }

    // ======================= the same two ideas on a real machine word =======================
    /** Adds without the + operator. Every round adds all columns at once without carrying, then hands each carry one column up; it ends when no carry is left. */
    static long addByRippling(long a, long b, int[] rounds) {
        while (b != 0) {
            long carries = a & b;                   // the columns where 1 + 1 makes a carry
            a = a ^ b;                              // every column added, nothing carried yet
            b = carries << 1;                       // each carry moves up one column
            rounds[0]++;
        }
        return a;
    }

    /** The same sum with carry-lookahead on all 64 columns at once. p marks columns that pass a carry on, g marks columns that make one by themselves. Six doubling rounds, whatever the numbers. */
    static long addByLookahead(long a, long b) {
        long p = a ^ b, g = a & b;
        long gg = g, pp = p;                        // gg, pp describe blocks of columns; at the start every block is one column
        for (int span = 1; span < 64; span <<= 1) {
            gg |= pp & (gg << span);                // my block makes a carry, or passes on the one that the block below makes
            pp &= pp << span;                       // my block passes a carry on only if both of its halves do
        }
        return p ^ (gg << 1);                       // each sum bit is (a xor b), flipped when a carry comes in from the column below
    }

    // ----------------------------- the checks -----------------------------
    static long[] randomDigits(int n, long[] radix, Random rnd) {
        long[] d = new long[n];
        for (int i = 0; i < n; i++) d[i] = (long) (rnd.nextDouble() * radix[i]);
        return d;
    }

    static long longestChainSlow(long a, long b, int bits) {      // for every column that makes a carry by itself, walk up while the columns above pass it on
        long best = 0;
        for (int i = 0; i < bits; i++) {
            if (((a >>> i) & 1) + ((b >>> i) & 1) != 2) continue;
            long length = 1;
            for (int j = i + 1; j < bits && ((a >>> j) & 1) + ((b >>> j) & 1) == 1; j++) length++;
            best = Math.max(best, length);
        }
        return best;
    }

    public static void main(String[] args) {
        Random rnd = new Random(2029);

        // ---- the money example from the text, and the same sum done the other way
        long[] money = {12, 20, 1_000_000};                  // pence in a shilling, shillings in a pound, and "no limit" for pounds
        long[] first = {9, 17, 3}, second = {8, 5, 2};       // 3 pounds 17 shillings 9 pence and 2 pounds 5 shillings 8 pence, smallest column first
        long[] total = addColumns(first, second, money);
        check(total[0] == 5 && total[1] == 3 && total[2] == 6 && total[3] == 0, "3 pounds 17s 9d + 2 pounds 5s 8d = 6 pounds 3s 5d");
        System.out.printf("3 pounds 17s 9d + 2 pounds 5s 8d = %d pounds %ds %dd (pence 9 + 8 = 17 -> 5, carry 1; shillings 17 + 5 + 1 = 23 -> 3, carry 1; pounds 3 + 2 + 1 = 6)%n", total[2], total[1], total[0]);
        for (int t = 0; t < 200_000; t++) {
            long[] x = {rnd.nextInt(12), rnd.nextInt(20), rnd.nextInt(10_000)}, y = {rnd.nextInt(12), rnd.nextInt(20), rnd.nextInt(10_000)};
            long[] z = addColumns(x, y, money);
            long pence = (x[0] + 12 * x[1] + 240 * x[2]) + (y[0] + 12 * y[1] + 240 * y[2]);       // convert both to pence, add, and compare
            check(value(z, money).longValue() == pence && z[0] < 12 && z[1] < 20, "adding on the money ladder matches adding in pence");
        }
        check(value(new long[]{0, 0, 1}, money).longValue() == 240, "one pound is worth 240 pence");

        // ---- why a single carry is always enough: (r - 1) + (r - 1) + 1 = 2r - 1 < 2r
        long columns = 0;
        for (long r = 2; r <= 100; r++)
            for (long a = 0; a < r; a++) for (long b = 0; b < r; b++) for (long c = 0; c <= 1; c++) { check((a + b + c) / r <= 1, "the carry out of a column is 0 or 1"); columns++; }
        System.out.printf("the carry out of a column is never more than 1: checked every digit pair and incoming carry for every radix from 2 to 100 (%,d cases)%n", columns);

        // ---- the same loop on every ladder: radix 2, 10, 60, and random mixed ladders, against BigInteger
        StringBuilder sb = new StringBuilder();
        for (long fixed : new long[]{2, 10, 60, 0}) {
            int trials = 100_000;
            for (int t = 0; t < trials; t++) {
                int n = 1 + rnd.nextInt(40);
                long[] radix = new long[n + 1];
                for (int i = 0; i <= n; i++) radix[i] = fixed != 0 ? fixed : 2 + rnd.nextInt(99);
                long[] x = randomDigits(n, radix, rnd), y = randomDigits(n, radix, rnd), z = addColumns(x, y, radix);
                check(value(z, radix).equals(value(x, radix).add(value(y, radix))), "addColumns on radix " + fixed);
                for (int i = 0; i < n; i++) check(z[i] < radix[i], "every digit of the answer is below its radix");
            }
            sb.append(fixed != 0 ? "radix " + fixed : "random mixed radices (2 to 100 per column)").append(": ").append(String.format("%,d", trials)).append(" sums match; ");
        }
        System.out.println("addColumns against BigInteger, numbers of up to 40 columns: " + sb);
        long[] decA = {8, 7, 4}, decB = {9, 5, 3}, ten = {10, 10, 10};
        long[] dec = addColumns(decA, decB, ten);
        check(value(dec, ten).intValue() == 837, "478 + 359 = 837");
        long[] nines = {9, 9, 9, 9, 9}, one = {1, 0, 0, 0, 0}, ten5 = {10, 10, 10, 10, 10};
        check(Arrays.equals(addColumns(nines, one, ten5), new long[]{0, 0, 0, 0, 0, 1}), "99999 + 1 = 100000");
        System.out.printf("decimal: 478 + 359 = %d; 99999 + 1 = %d%n", value(dec, ten).intValue(), value(addColumns(nines, one, ten5), new long[]{10, 10, 10, 10, 10, 10}).intValue());

        // ---- the exercises in the text, every answer checked
        long[] imperial = {12, 3, 1_000_000};                // inches in a foot, feet in a yard, no limit on yards
        long[] length = addColumns(new long[]{11, 2, 7}, new long[]{5, 1, 4}, imperial);
        check(Arrays.equals(length, new long[]{4, 1, 12, 0}), "7 yd 2 ft 11 in + 4 yd 1 ft 5 in = 12 yd 1 ft 4 in");
        long[] clock = {60, 60, 1_000};                      // seconds in a minute, minutes in an hour, no limit on hours
        long[] elapsed = addColumns(new long[]{50, 45, 1}, new long[]{25, 20, 2}, clock);
        check(Arrays.equals(elapsed, new long[]{15, 6, 4, 0}), "1 h 45 min 50 s + 2 h 20 min 25 s = 4 h 6 min 15 s");
        System.out.printf("exercises: 7 yd 2 ft 11 in + 4 yd 1 ft 5 in = %d yd %d ft %d in; 1 h 45 min 50 s + 2 h 20 min 25 s = %d h %d min %d s%n", length[2], length[1], length[0], elapsed[2], elapsed[1], elapsed[0]);

        // ---- the board in two steps gives the same answer as the one-pass loop
        for (int t = 0; t < 100_000; t++) {
            int n = 1 + rnd.nextInt(30);
            long[] radix = new long[n];
            for (int i = 0; i < n; i++) radix[i] = 2 + rnd.nextInt(60);
            long[] x = randomDigits(n, radix, rnd), y = randomDigits(n, radix, rnd);
            check(Arrays.equals(settle(columnSums(x, y), radix), addColumns(x, y, radix)), "settle(columnSums) equals addColumns");
        }

        // ---- carry-lookahead gives the same sums, in about log2 n rounds instead of n steps
        for (long fixed : new long[]{2, 10, 60, 0}) {
            for (int t = 0; t < 50_000; t++) {
                int n = 1 + rnd.nextInt(70);
                long[] radix = new long[n];
                for (int i = 0; i < n; i++) radix[i] = fixed != 0 ? fixed : 2 + rnd.nextInt(99);
                long[] x = randomDigits(n, radix, rnd), y = randomDigits(n, radix, rnd);
                if (t % 5 == 0) for (int i = 0; i < n; i++) { x[i] = radix[i] - 1; y[i] = i == 0 ? 1 : 0; }     // the worst case: one carry that must run through every column
                int[] stats = new int[2];
                check(Arrays.equals(addLookahead(x, y, radix, stats), addColumns(x, y, radix)), "lookahead equals the ripple sum, radix " + fixed);
                int expectedRounds = n == 1 ? 0 : 32 - Integer.numberOfLeadingZeros(n - 1);     // ceil(log2 n)
                check(stats[0] == expectedRounds, "lookahead needs ceil(log2 n) rounds, n = " + n);
            }
        }
        int[] stats64 = new int[2];
        long[] radix64 = new long[64], zeros = new long[64], ones = new long[64];
        Arrays.fill(radix64, 2);
        ones[0] = 1;
        long[] allOnes = new long[64];
        Arrays.fill(allOnes, 1);
        long[] worst = addLookahead(allOnes, ones, radix64, stats64);
        check(worst[64] == 1 && Arrays.stream(worst, 0, 64).allMatch(v -> v == 0), "1111...1 + 1 = 1000...0 with lookahead");
        System.out.printf("64 binary columns, all ones plus one (the worst case): a ripple adder passes the carry through all 64 columns in turn; lookahead settles every carry in %d rounds and %d combine steps%n", stats64[0], stats64[1]);

        // ---- how far do carries really travel? random operands, measured
        sb.setLength(0);
        double mean40 = 0;
        for (int bits : new int[]{8, 16, 32, 40, 64}) {
            int trials = 1_000_000;
            long mask = bits == 64 ? -1L : (1L << bits) - 1;
            double sum = 0;
            int max = 0;
            for (int t = 0; t < trials; t++) {
                long a = rnd.nextLong() & mask, b = rnd.nextLong() & mask;
                int chain = longestChain(a, b, bits);
                if (t < 20_000) check(chain == longestChainSlow(a, b, bits), "longestChain matches the slow version");
                sum += chain;
                max = Math.max(max, chain);
            }
            double log2 = Math.log(bits) / Math.log(2);
            check(sum / trials <= log2 + 0.5 && sum / trials >= log2 - 3, "the average longest chain stays close to log2 n, bits = " + bits + ", got " + sum / trials);
            if (bits == 40) mean40 = sum / trials;
            sb.append(String.format("%d bits: average longest chain %.2f (log2 n = %.2f), longest seen %d; ", bits, sum / trials, log2, max));
        }
        check(longestChain(-1L, 1L, 64) == 64 && longestChain(0, 0, 64) == 0 && longestChain(0b0111, 0b0001, 4) == 3, "worst case and trivial cases");
        System.out.println("longest carry chain when adding two random n-bit numbers, 1,000,000 pairs for each n: " + sb + String.format("(for n = 40 von Neumann's team estimated about log2 40 = %.1f)", Math.log(40) / Math.log(2)));
        // ---- the real thing: a 64-bit word added by rippling and by lookahead, against Java's own +
        long[] edge = {0, 1, -1, Long.MAX_VALUE, Long.MIN_VALUE, 0x5555555555555555L, 0xAAAAAAAAAAAAAAAAL, 0x00000000FFFFFFFFL, 1L << 62};
        for (long x : edge)
            for (long y : edge) check(addByRippling(x, y, new int[1]) == x + y && addByLookahead(x, y) == x + y, "rippling and lookahead agree with + on the edge cases");
        int[] worstRounds = new int[1];
        check(addByRippling(-1L, 1L, worstRounds) == 0 && addByLookahead(-1L, 1L) == 0, "all ones plus one wraps around to zero");
        int pairs = 1_000_000, over6 = 0;
        double rounds40 = 0, rounds64 = 0;
        long mask40 = (1L << 40) - 1, mask62 = (1L << 62) - 1;
        for (int t = 0; t < pairs; t++) {
            long a = rnd.nextLong(), b = rnd.nextLong();
            int[] r64 = new int[1];
            check(addByRippling(a, b, r64) == a + b, "rippling equals +");
            check(addByLookahead(a, b) == a + b, "lookahead equals +");
            rounds64 += r64[0];
            if (r64[0] > 6) over6++;
            int[] r62 = new int[1], r40 = new int[1];
            addByRippling(a & mask62, b & mask62, r62);
            check(r62[0] == longestChain(a & mask62, b & mask62, 62) + 1, "rippling needs exactly one round more than the longest carry chain");
            addByRippling(a & mask40, b & mask40, r40);
            check(r40[0] == longestChain(a & mask40, b & mask40, 40) + 1, "the same for 40 bits");
            rounds40 += r40[0];
        }
        System.out.printf("a real 64-bit word, %,d random pairs: rippling and lookahead both agree with Java's +; rippling needs (longest carry chain + 1) rounds exactly, on average %.2f rounds for random 40-bit numbers and %.2f for random 64-bit numbers, and more than 6 rounds for %.1f%% of the 64-bit pairs; all ones + 1 needs %d rounds; lookahead always needs 6%n",
                pairs, rounds40 / pairs, rounds64 / pairs, 100.0 * over6 / pairs, worstRounds[0]);
        System.out.println("AddingTwoNumbers: " + passed + " checks passed");
    }
}
