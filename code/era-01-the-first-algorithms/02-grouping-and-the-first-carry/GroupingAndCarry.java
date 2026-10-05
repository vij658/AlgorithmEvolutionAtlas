import java.util.*;

/**
 * Era 1, topic 2: grouping, written numerals and the first carry (Egypt and Sumer, c. 3200-3000 BCE).
 *
 * HOW IT WORKS
 *   A tally needs one mark per thing. Grouped numerals give each bundle its own sign: Egyptian hieroglyphs have signs
 *   for 1, 10, 100, ... up to 1,000,000, and the earliest Sumerian accounts bundle 10 small units into one sign, 6 of
 *   those into the next, then 10, then 6 again. A number is written by repeating each sign as often as needed.
 *   Adding is then two moves: pool the signs of both numbers, and wherever there are too many of one sign (ten, or
 *   six, depending on the step), exchange them for one sign of the next size. That exchange is the carry. It is
 *   older than place value: it only needs bundles and an exchange rate.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Writes numbers in four ways: a tally, Egyptian signs (exchange rate 10 at every step), the Sumerian
 *      sexagesimal system for counted objects (rates 10, 6, 10, 6, 10) and the bisexagesimal system for rations
 *      (rates 10, 6, 2, 10, 6), and counts how many signs each needs.
 *   2. Adds by pooling and exchanging, printing every exchange of a worked example, and checks the method against
 *      ordinary addition on 300,000 random pairs in every system.
 *   3. Measures carries: how often a column passes a carry on when two long random numbers are added (Holte showed
 *      the long-run share is one half, in any base), and the longest carry chain when two random 40-bit numbers are
 *      added (Burks, Goldstine and von Neumann, 1946, showed its average is at most log2 40, about 5.3).
 *   Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java GroupingAndCarry.java
 *   Expected output: expected-output.txt in this folder.
 */
public class GroupingAndCarry {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // 1. Number systems as ladders of exchange rates
    // ----------------------------------------------------------------------------------------------------

    /**
     * A grouped number system. rates[i] says how many of sign i make one of sign i + 1. The last sign has no limit:
     * it simply repeats.
     */
    record NumberSystem(String name, int[] rates) {
        /** The value of each sign in units: 1, then the running product of the rates. */
        long[] values() {
            long[] v = new long[rates.length + 1];
            v[0] = 1;
            for (int i = 0; i < rates.length; i++) v[i + 1] = v[i] * rates[i];
            return v;
        }

        /** How many of each sign (smallest sign first) to write n: take as many of the biggest sign as fit, and so on. */
        int[] toSigns(long n) {
            long[] v = values();
            int[] c = new int[v.length];
            for (int i = v.length - 1; i >= 0; i--) {
                c[i] = (int) (n / v[i]);
                n %= v[i];
            }
            return c;
        }

        long value(int[] counts) {
            long[] v = values();
            long total = 0;
            for (int i = 0; i < counts.length; i++) total += counts[i] * v[i];
            return total;
        }

        int signCount(long n) { return Arrays.stream(toSigns(n)).sum(); }
    }

    static final NumberSystem TALLY = new NumberSystem("tally", new int[]{});
    static final NumberSystem EGYPTIAN = new NumberSystem("egyptian", new int[]{10, 10, 10, 10, 10, 10});
    static final NumberSystem SEXAGESIMAL = new NumberSystem("sumerian-S", new int[]{10, 6, 10, 6, 10});
    static final NumberSystem BISEXAGESIMAL = new NumberSystem("sumerian-B", new int[]{10, 6, 2, 10, 6});

    // ----------------------------------------------------------------------------------------------------
    // 2. Adding: pool the signs, then exchange
    // ----------------------------------------------------------------------------------------------------

    /** The result of an addition: the signs, how many exchanges were made, and every state along the way. */
    record Sum(int[] counts, int exchanges, List<int[]> states) {}

    /**
     * Add two numbers written in signs. Pool them (add the counts sign by sign), then walk from the smallest sign
     * upwards: while there are at least `rate` of a sign, take that many away and add one of the next sign.
     */
    static Sum add(NumberSystem s, int[] a, int[] b, boolean keepStates) {
        int[] c = new int[a.length];
        for (int i = 0; i < c.length; i++) c[i] = a[i] + b[i];            // pool
        List<int[]> states = new ArrayList<>();
        if (keepStates) states.add(c.clone());
        int exchanges = 0;
        for (int i = 0; i < s.rates().length; i++) {
            while (c[i] >= s.rates()[i]) {                                // too many of this sign
                c[i] -= s.rates()[i];                                     // give up `rate` of them ...
                c[i + 1] += 1;                                            // ... for one of the next size: the carry
                exchanges++;
                if (keepStates) states.add(c.clone());
            }
        }
        return new Sum(c, exchanges, states);
    }

    static String counts(int[] c) {
        StringBuilder s = new StringBuilder();
        for (int x : c) s.append(s.length() == 0 ? "" : " ").append(x);
        return s.toString();
    }

    // ----------------------------------------------------------------------------------------------------
    // 3. Carries in long additions
    // ----------------------------------------------------------------------------------------------------

    /** For two numbers given as digits (smallest first) in base b: which columns pass a carry on. */
    static boolean[] carriesOut(int[] x, int[] y, int base) {
        boolean[] out = new boolean[x.length];
        int carry = 0;
        for (int i = 0; i < x.length; i++) {
            int t = x[i] + y[i] + carry;
            carry = t >= base ? 1 : 0;
            out[i] = carry == 1;
        }
        return out;
    }

    /**
     * The longest carry chain in a binary addition, as Burks, Goldstine and von Neumann counted it: a carry is made in a
     * column where both digits are 1, and it travels one column further for every column where exactly one digit is 1.
     * Its length is the number of columns it travels.
     */
    static int longestChain(int[] x, int[] y) {
        int best = 0;
        for (int i = 0; i < x.length; i++) {
            if (x[i] == 1 && y[i] == 1) {                                // a carry is made here ...
                int j = i + 1;
                while (j < x.length && x[j] != y[j]) j++;                // ... and travels while exactly one digit is 1
                best = Math.max(best, j - i);
            }
        }
        return best;
    }

    /** The same, by brute force on the carries themselves: follow each carry made where both digits are 1. */
    static int longestChainByCarries(int[] x, int[] y) {
        boolean[] c = carriesOut(x, y, 2);
        int best = 0;
        for (int i = 0; i < x.length; i++) {
            if (x[i] + y[i] == 2) {
                int len = 1;
                for (int j = i + 1; j < x.length && c[j] && x[j] + y[j] == 1; j++) len++;
                best = Math.max(best, len);
            }
        }
        return best;
    }

    // ----------------------------------------------------------------------------------------------------

    public static void main(String[] args) {
        // the ladders
        for (NumberSystem s : List.of(EGYPTIAN, SEXAGESIMAL, BISEXAGESIMAL)) {
            System.out.printf("ladder %s: rates=%s values=%s%n", s.name(), Arrays.toString(s.rates()).replaceAll("[\\[\\],]", ""),
                    Arrays.toString(s.values()).replaceAll("[\\[\\],]", ""));
        }
        check(SEXAGESIMAL.values()[5] == 36_000, "the largest S sign is 36,000 units (Melville)");
        check(BISEXAGESIMAL.values()[5] == 7_200, "the largest B sign is 7,200 units (Melville)");
        check(EGYPTIAN.values()[6] == 1_000_000, "the Egyptian signs reach a million");

        // signs needed
        for (long n : new long[]{7, 60, 168, 1999, 4622, 9999}) {
            for (NumberSystem s : List.of(EGYPTIAN, SEXAGESIMAL, BISEXAGESIMAL))
                check(s.value(s.toSigns(n)) == n, "signs give back the number");
            System.out.printf("signs %d: tally=%d egyptian=%d sumerian-S=%d egyptian-signs=%s sumerian-S-signs=%s%n", n,
                    TALLY.signCount(n), EGYPTIAN.signCount(n), SEXAGESIMAL.signCount(n),
                    counts(EGYPTIAN.toSigns(n)), counts(SEXAGESIMAL.toSigns(n)));
        }
        long sumT = 0, sumE = 0, sumS = 0;
        int worstE = 0, worstS = 0;
        long worstEAt = 0, worstSAt = 0;
        for (long n = 1; n <= 9999; n++) {
            int e = EGYPTIAN.signCount(n), s = SEXAGESIMAL.signCount(n);
            sumT += n;
            sumE += e;
            sumS += s;
            if (e > worstE) { worstE = e; worstEAt = n; }
            if (s > worstS) { worstS = s; worstSAt = n; }
        }
        System.out.printf("average 1-9999: tally=%.1f egyptian=%.2f sumerian-S=%.2f%n", sumT / 9999.0, sumE / 9999.0, sumS / 9999.0);
        System.out.printf("most 1-9999: egyptian=%d at %d sumerian-S=%d at %d%n", worstE, worstEAt, worstS, worstSAt);

        // a worked addition, every exchange shown
        long a = 2763, b = 1489;
        Sum w = add(EGYPTIAN, EGYPTIAN.toSigns(a), EGYPTIAN.toSigns(b), true);
        System.out.printf("work egyptian %d %d: pool=%s%n", a, b, counts(w.states().get(0)));
        for (int i = 1; i < w.states().size(); i++) System.out.printf("work egyptian %d %d: exchange %d=%s%n", a, b, i, counts(w.states().get(i)));
        System.out.printf("work egyptian %d %d: result=%d exchanges=%d%n", a, b, EGYPTIAN.value(w.counts()), w.exchanges());
        check(EGYPTIAN.value(w.counts()) == a + b, "worked example");
        long sa = 47, sb = 38;
        Sum ws = add(SEXAGESIMAL, SEXAGESIMAL.toSigns(sa), SEXAGESIMAL.toSigns(sb), true);
        System.out.printf("work sumerian-S %d %d: pool=%s%n", sa, sb, counts(ws.states().get(0)));
        for (int i = 1; i < ws.states().size(); i++) System.out.printf("work sumerian-S %d %d: exchange %d=%s%n", sa, sb, i, counts(ws.states().get(i)));
        System.out.printf("work sumerian-S %d %d: result=%d exchanges=%d%n", sa, sb, SEXAGESIMAL.value(ws.counts()), ws.exchanges());
        check(SEXAGESIMAL.value(ws.counts()) == sa + sb, "worked example S");
        Sum cascade = add(EGYPTIAN, EGYPTIAN.toSigns(9999), EGYPTIAN.toSigns(1), true);
        System.out.printf("cascade egyptian 9999 1: exchanges=%d result=%d%n", cascade.exchanges(), EGYPTIAN.value(cascade.counts()));
        check(cascade.exchanges() == 4, "9,999 + 1 ripples through four exchanges");

        // pooling and exchanging is addition: check it in every system
        Random rnd = new Random(3000);
        int pairs = 0;
        long totalExchanges = 0;
        for (NumberSystem s : List.of(EGYPTIAN, SEXAGESIMAL, BISEXAGESIMAL)) {
            for (int i = 0; i < 100_000; i++) {
                long x = rnd.nextLong(0, 5_000_000), y = rnd.nextLong(0, 4_000_000);
                Sum r = add(s, s.toSigns(x), s.toSigns(y), false);
                check(s.value(r.counts()) == x + y, "pool and exchange = addition in " + s.name());
                int[] canon = s.toSigns(x + y);
                for (int k = 0; k < s.rates().length; k++) check(r.counts()[k] == canon[k], "the result is fully exchanged");
                if (s == EGYPTIAN) totalExchanges += r.exchanges();
                pairs++;
            }
        }
        System.out.printf("addcheck: %d random pairs in 3 systems, pool-and-exchange agreed with ordinary addition every time%n", pairs);
        System.out.printf("exchanges egyptian: %.3f per addition of two random numbers below 5,000,000%n", totalExchanges / 100_000.0);

        // carries in long additions, base 10 and base 2
        Random r2 = new Random(1946);
        int digits = 12, trials = 200_000;
        long carryCols = 0, firstCol = 0;
        for (int t = 0; t < trials; t++) {
            int[] x = new int[digits], y = new int[digits];
            for (int i = 0; i < digits; i++) { x[i] = r2.nextInt(10); y[i] = r2.nextInt(10); }
            boolean[] c = carriesOut(x, y, 10);
            for (boolean v : c) if (v) carryCols++;
            if (c[0]) firstCol++;
        }
        System.out.printf("carry-share base 10: %.4f of columns over %d additions of two %d-digit numbers; first column %.4f (exactly 45 of 100 digit pairs carry)%n",
                (double) carryCols / ((long) trials * digits), trials, digits, (double) firstCol / trials);
        int lateCarry = 0;
        long lateCols = 0;
        for (int t = 0; t < trials; t++) {          // far from the first column the share settles at one half
            int[] x = new int[40], y = new int[40];
            for (int i = 0; i < 40; i++) { x[i] = r2.nextInt(10); y[i] = r2.nextInt(10); }
            boolean[] c = carriesOut(x, y, 10);
            for (int i = 20; i < 40; i++) { lateCols++; if (c[i]) lateCarry++; }
        }
        double late = (double) lateCarry / lateCols;
        System.out.printf("carry-share base 10 columns 21-40: %.4f (Holte: one half in the long run)%n", late);
        check(Math.abs(late - 0.5) < 0.005, "the long-run carry share is about one half");
        int pairs01 = 0;
        for (int dx = 0; dx < 10; dx++) for (int dy = 0; dy < 10; dy++) if (dx + dy >= 10) pairs01++;
        check(pairs01 == 45, "45 of the 100 digit pairs carry");
        int pairs11 = 0;
        for (int dx = 0; dx < 10; dx++) for (int dy = 0; dy < 10; dy++) if (dx + dy + 1 >= 10) pairs11++;
        check(pairs11 == 55, "with a carry coming in, 55 of the 100 digit pairs carry");
        System.out.printf("transitions base 10: with no carry coming in, %d of 100 digit pairs pass one on; with a carry coming in, %d of 100%n", pairs01, pairs11);

        int bits = 40;
        long sumLongest = 0;
        int[] hist = new int[bits + 1];
        for (int t = 0; t < trials; t++) {
            int[] x = new int[bits], y = new int[bits];
            for (int i = 0; i < bits; i++) { x[i] = r2.nextInt(2); y[i] = r2.nextInt(2); }
            int L = longestChain(x, y);
            check(L == longestChainByCarries(x, y), "two ways of measuring the chain agree");
            sumLongest += L;
            hist[L]++;
        }
        System.out.printf("longest-carry base 2: %d bits, average longest carry chain %.3f over %d random pairs; log2(%d) = %.3f%n",
                bits, (double) sumLongest / trials, trials, bits, Math.log(bits) / Math.log(2));
        int mode = 0;
        for (int i = 0; i <= bits; i++) if (hist[i] > hist[mode]) mode = i;
        int max = 0;
        for (int i = 0; i <= bits; i++) if (hist[i] > 0) max = i;
        System.out.printf("longest-carry spread: most common %d, longest seen %d, worst possible %d%n", mode, max, bits);
        // the carries agree with machine addition: carry into bit i+1 is bit i+1 of (x + y) XOR x XOR y
        for (int t = 0; t < 100_000; t++) {
            long x = r2.nextLong() >>> 25, y = r2.nextLong() >>> 25;            // 39-bit numbers
            int[] xd = new int[40], yd = new int[40];
            for (int i = 0; i < 40; i++) { xd[i] = (int) (x >>> i & 1); yd[i] = (int) (y >>> i & 1); }
            boolean[] c = carriesOut(xd, yd, 2);
            long carryIn = (x + y) ^ x ^ y;
            for (int i = 0; i < 39; i++) check(c[i] == ((carryIn >>> (i + 1) & 1) == 1), "carries match machine addition");
        }

        System.out.printf("GroupingAndCarry: %d checks passed%n", passed);
    }
}
