import java.util.*;

/**
 * Era 3, topic 3: the carry, mechanized (Schickard 1623, Pascal 1642-1645, Leibniz 1673-1694).
 *
 * HOW IT WORKS
 *   A wheel with ten positions holds one digit. Turning it past 9 back to 0 must turn the next wheel by one: the carry.
 *   In Schickard's design a single tooth on each wheel pushes the next one, so a long chain of carries (999,999 + 1)
 *   makes every wheel turn at once, driven by the hand on the first. Pascal's sautoir is a weighted lever lifted as a
 *   wheel turns and dropped when it passes 9, so each carry is delivered by gravity, one wheel after another. Pascal's
 *   wheels turn only one way, so the machine adds; to subtract, enter the nines' complement of the first number,
 *   add the second, and read the complement of the result: C(C(a) + b) = a - b, where C(x) = 999...9 - x.
 *   Leibniz's stepped drum has nine teeth of increasing length; setting a digit d engages d teeth, so one turn of the
 *   crank adds d. A carriage shifts the setting one place for each digit of the multiplier, so multiplying by 8,912
 *   takes 8 + 9 + 1 + 2 = 20 turns and 3 shifts, not 8,912 additions.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Simulates a six-wheel adding machine: counts carries and the longest chain of carries for counting up and for
 *      adding columns of figures.
 *   2. Checks subtraction by nines' complements on 100,000 random pairs.
 *   3. Simulates Leibniz's stepped drum: crank turns and shifts for multiplication and division, against repeated
 *      addition.
 *   4. Full circle: the longest carry chain in random 64-bit binary additions, as in a processor's adder.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MechanicalCarry.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MechanicalCarry {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** A row of wheels, least significant first, with a counter of carries and of the longest chain. */
    static final class Wheels {
        final int[] w;
        final int base;
        long carries;
        int longest;
        long overflow;

        Wheels(int n, int base) { w = new int[n]; this.base = base; }

        /** Add d (0..base-1) on wheel i; the carries ripple left one wheel at a time. Returns the chain length. */
        int addAt(int i, int d) {
            int chain = 0;
            w[i] += d;
            while (i < w.length && w[i] >= base) {
                w[i] -= base;
                carries++;
                chain++;
                i++;
                if (i < w.length) w[i] += 1; else overflow++;
            }
            longest = Math.max(longest, chain);
            return chain;
        }

        /** Add a whole number, wheel by wheel from the right (as an operator sets each wheel in turn). */
        int add(long x) {
            int chainMax = 0;
            for (int i = 0; i < w.length && x > 0; i++, x /= base) chainMax = Math.max(chainMax, addAt(i, (int) (x % base)));
            return chainMax;
        }

        long value() { long v = 0; for (int i = w.length - 1; i >= 0; i--) v = v * base + w[i]; return v; }
    }

    static long nines(long x, int n) { long all = 1; for (int i = 0; i < n; i++) all *= 10; return all - 1 - x; }

    public static void main(String[] args) {
        // ---- 1. counting up and adding columns ------------------------------------------------------------------------
        Wheels m = new Wheels(6, 10);
        long[] chainCount = new long[7];
        for (int t = 1; t <= 999999; t++) {
            int c = m.addAt(0, 1);
            chainCount[c]++;
            check(m.value() == t, "the wheels show the count");
        }
        StringJoiner chains = new StringJoiner(" ; ");
        for (int k = 0; k <= 5; k++) chains.add(String.format("%d carr%s: %,d times", k, k == 1 ? "y" : "ies", chainCount[k]));
        check(chainCount[5] == 9 && chainCount[0] == 900000, "counting to 999,999: 900,000 steps with no carry, 9 with a chain of 5");
        long before = m.value();
        int last = m.addAt(0, 1);
        check(before == 999999 && last == 6 && m.overflow == 1 && m.value() == 0, "999,999 + 1 carries through all six wheels and out");
        System.out.printf("count: counting from 1 to 999,999 on six wheels: %,d carries in all ; %s ; then 999,999 + 1 sets off a chain through all %d wheels%n",
                m.carries - 6, chains, last);

        Random rnd = new Random(1642);
        Wheels acc = new Wheels(8, 10);
        long sum = 0;
        int rows = 1000;
        for (int r = 0; r < rows; r++) { long x = rnd.nextInt(100000); acc.add(x); sum += x; check(acc.value() == sum, "the column total is right"); }
        System.out.printf("column: adding a column of %,d five-digit figures on eight wheels: total %,d ; %,d carries (%.2f per figure) ; longest chain %d%n",
                rows, sum, acc.carries, acc.carries / (double) rows, acc.longest);

        // ---- 2. subtraction by nines' complement ------------------------------------------------------------------------
        int ok = 0;
        for (int t = 0; t < 100000; t++) {
            long a = rnd.nextInt(1000000), b = rnd.nextInt(1000000);
            if (b > a) { long s = a; a = b; b = s; }
            Wheels w = new Wheels(6, 10);
            w.add(nines(a, 6));                        // enter the complement of a
            w.add(b);                                  // add b: the wheels never turn backwards
            long shown = nines(w.value(), 6);          // read the complement
            check(shown == a - b, "C(C(a) + b) = a - b");
            ok++;
        }
        long a0 = 4567, b0 = 1234;
        Wheels w0 = new Wheels(6, 10);
        w0.add(nines(a0, 6));
        long mid = w0.value();
        w0.add(b0);
        System.out.printf("subtract: %d - %d on six wheels: enter the nines' complement %06d, add %d to get %06d, read its complement %06d = %d ; checked on %,d random pairs%n",
                a0, b0, mid, b0, w0.value(), nines(w0.value(), 6), nines(w0.value(), 6), ok);

        // ---- 3. Leibniz's stepped drum -------------------------------------------------------------------------------------
        long x = 4567, y = 8912;
        long[] tm = leibnizMultiply(x, y, 12);
        check(tm[0] == x * y && tm[1] == 20 && tm[2] == 3, "4567 x 8912 in 20 turns and 3 shifts");
        long[] dv = leibnizDivide(40701104, 4567, 12);
        check(dv[0] == 8912 && dv[1] == 0, "dividing back gives 8912, remainder 0");
        System.out.printf("leibniz: %d x %d = %d in %d turns of the crank and %d shifts of the carriage (repeated addition would take %,d turns) ; %d / %d = %d remainder %d in %d turns and %d shifts%n",
                x, y, tm[0], tm[1], tm[2], y, 40701104L, x, dv[0], dv[1], dv[2], dv[3]);
        long turns = 0, naive = 0;
        int n = 100000;
        for (int t = 0; t < n; t++) {
            long p = 1 + rnd.nextInt(99999), q = 1 + rnd.nextInt(99999);
            long[] r = leibnizMultiply(p, q, 12);
            check(r[0] == p * q, "the stepped drum multiplies correctly");
            turns += r[1]; naive += q;
        }
        System.out.printf("leibniz survey: %,d random products of numbers below 100,000: on average %.1f crank turns per product, against %,.0f additions by repeated addition%n",
                n, turns / (double) n, naive / (double) n);

        // ---- 4. full circle: carries in binary adders ---------------------------------------------------------------------
        int trials = 200000;
        long longestSum = 0;
        int worstSeen = 0;
        int[] hist = new int[65];
        for (int t = 0; t < trials; t++) {
            long p = rnd.nextLong(), q = rnd.nextLong();
            int c = longestCarryChain(p, q);
            longestSum += c; worstSeen = Math.max(worstSeen, c); hist[c]++;
            check(rippleAdd(p, q) == p + q, "ripple-carry addition matches the processor's");
        }
        int median = 0, acc2 = 0;
        for (int k = 0; k <= 64; k++) { acc2 += hist[k]; if (acc2 >= trials / 2) { median = k; break; } }
        System.out.printf("binary: %,d random 64-bit additions done bit by bit with rippling carries: the longest carry chain averages %.2f bits (median %d, the largest seen %d), though the worst case is 64%n",
                trials, longestSum / (double) trials, median, worstSeen);

        System.out.printf("MechanicalCarry: %d checks passed%n", passed);
    }

    /** Multiply on a stepped-drum machine: set x on the drums; for each digit d of y, turn the crank d times, then shift. Returns {product, turns, shifts}. */
    static long[] leibnizMultiply(long x, long y, int places) {
        Wheels acc = new Wheels(places, 10);
        long turns = 0, shifts = 0, pos = 0;
        String ys = Long.toString(y);
        for (int k = ys.length() - 1; k >= 0; k--) {
            int d = ys.charAt(k) - '0';
            for (int t = 0; t < d; t++) {                              // one turn adds the setting x, shifted pos places
                long s = x;
                for (int i = (int) pos; s > 0; i++, s /= 10) acc.addAt(i, (int) (s % 10));
                turns++;
            }
            if (k > 0) { pos++; shifts++; }
        }
        return new long[]{acc.value(), turns, shifts};
    }

    /** Divide by repeated subtraction with shifts (by complements on an adding mechanism). Returns {quotient, remainder, turns, shifts}. */
    static long[] leibnizDivide(long a, long b, int places) {
        long q = 0, r = a, turns = 0, shifts = 0;
        int top = Long.toString(a).length() - Long.toString(b).length();
        for (int pos = top; pos >= 0; pos--) {
            long bs = b;
            for (int i = 0; i < pos; i++) bs *= 10;
            int d = 0;
            while (r >= bs) { r -= bs; d++; turns++; }
            q = q * 10 + d;
            if (pos > 0) shifts++;
        }
        return new long[]{q, r, turns, shifts};
    }

    static long rippleAdd(long p, long q) {
        long s = 0; int c = 0;
        for (int i = 0; i < 64; i++) {
            int a = (int) (p >>> i) & 1, b = (int) (q >>> i) & 1;
            int t = a + b + c;
            s |= (long) (t & 1) << i;
            c = t >> 1;
        }
        return s;
    }

    /** The longest run of bit positions through which a single carry travels (generated, then propagated). */
    static int longestCarryChain(long p, long q) {
        int longest = 0, run = 0, c = 0;
        for (int i = 0; i < 64; i++) {
            int a = (int) (p >>> i) & 1, b = (int) (q >>> i) & 1;
            if (a == 1 && b == 1) { run = 1; c = 1; }                  // a carry is generated here
            else if (a != b && c == 1) { run++; }                      // the carry propagates through
            else { c = 0; run = 0; }                                   // the carry is absorbed (or there was none)
            if (c == 1) longest = Math.max(longest, run);
            if (a == 0 && b == 0) { c = 0; run = 0; }
        }
        return longest;
    }
}
