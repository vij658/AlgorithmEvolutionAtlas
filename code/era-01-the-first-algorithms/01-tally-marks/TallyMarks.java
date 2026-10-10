import java.util.*;

/**
 * Era 1, topic 1: tally marks (notched bones from Border Cave, c. 44,000 years ago, and Ishango, c. 25,000-16,000 BP).
 *
 * HOW IT WORKS
 *   A tally keeps one mark per thing: one notch per animal, per day, per debt. Nobody needs a word for "seventeen" to
 *   keep it; they only need to add one mark each time. Two collections can be compared the same way, without counting
 *   either one: pair them off one by one, and whichever has things left over is larger. This is one-to-one
 *   correspondence, the idea Cantor made precise in 1878 to compare the sizes of infinite sets.
 *   A tally is also the first append-only log: marks are added, never changed, and the count is the length of the log.
 *   Its weakness is reading. Every mark must be looked at, so a long tally is slow to read, which is the pain that the
 *   next topic (grouping) answers.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Matching: compares two collections by pairing alone, checked against counting on 200,000 random pairs.
 *   2. The tally as a log: adding marks, replaying the log, and the cost of reading it mark by mark compared with
 *      reading it in groups of five (a preview of topic 2).
 *   3. The Ishango bone's notch groups as read by Jean de Heinzelin (1962) and listed by the UNESCO portal: column
 *      totals 60, 48, 60, the primes 11, 13, 17, 19, the groups 10 +/- 1 and 20 +/- 1, and the doubling pairs. Then the
 *      same marks grouped differently, as the UNESCO listing's own sub-groups allow: the doubling pattern weakens.
 *   4. How surprising are those patterns? Exact counts (no random sampling) under a stated assumption: each group size
 *      is equally likely to be any number from 3 to 21, the range seen on the bone. Prints how rare the bone's
 *      combination of patterns would be, and how common it is for random marks to show at least one pattern.
 *   5. The split tally (medieval English Exchequer, abolished 1826): notches cut across a stick that is then split in
 *      two; a forged notch on one half no longer matches the other.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java TallyMarks.java
 *   Expected output: expected-output.txt in this folder.
 */
public class TallyMarks {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // 1. Matching: which collection is larger, without counting either
    // ----------------------------------------------------------------------------------------------------

    /** The result of pairing two collections off: how many pairs were made, which side had things left, and how many. */
    record Match(int pairs, int winner, int leftOver) {}       // winner: 1 = first, 2 = second, 0 = same size

    /**
     * Pair the two collections off one thing at a time until one of them runs out. No number is ever needed: each step
     * only asks "is there still something on both sides?". The copies are taken so the caller's lists are untouched.
     */
    static <T> Match match(List<T> first, List<T> second) {
        Deque<T> a = new ArrayDeque<>(first), b = new ArrayDeque<>(second);
        int pairs = 0;
        while (!a.isEmpty() && !b.isEmpty()) {             // one stone from each pile, set aside together
            a.pop();
            b.pop();
            pairs++;
        }
        if (a.isEmpty() && b.isEmpty()) return new Match(pairs, 0, 0);
        return a.isEmpty() ? new Match(pairs, 2, b.size()) : new Match(pairs, 1, a.size());
    }

    static List<String> herd(String name, int n) {
        List<String> h = new ArrayList<>();
        for (int i = 0; i < n; i++) h.add(name + i);
        return h;
    }

    // ----------------------------------------------------------------------------------------------------
    // 2. The tally as an append-only log
    // ----------------------------------------------------------------------------------------------------

    /** A tally: marks are only ever added. The count is the number of marks; the log can be replayed. */
    static final class Tally {
        private final List<String> marks = new ArrayList<>();

        void mark(String what) { marks.add(what); }        // the only way to change a tally

        int count() { return marks.size(); }

        List<String> replay() { return List.copyOf(marks); }
    }

    /** Looks needed to read n marks one at a time. */
    static int looksOneByOne(int n) { return n; }

    /** Looks needed when marks are bundled in fives: one look per bundle, plus one for any leftover marks. */
    static int looksByFives(int n) { return n / 5 + (n % 5 > 0 ? 1 : 0); }

    // ----------------------------------------------------------------------------------------------------
    // 3. The Ishango bone, as read by de Heinzelin and listed by the UNESCO Portal to the Heritage of Astronomy
    // ----------------------------------------------------------------------------------------------------

    static final int[] COLUMN_G = {11, 13, 17, 19};
    static final int[] COLUMN_M = {3, 6, 4, 8, 10, 5, 5, 7};          // the listing writes 10 as (9+1) and 5 as (1+4)
    static final int[] COLUMN_M_SPLIT = {3, 6, 4, 8, 9, 1, 1, 4, 5, 7}; // the same marks with those two groups split
    static final int[] COLUMN_D = {11, 21, 19, 9};

    static boolean isPrime(int n) {
        if (n < 2) return false;
        for (int d = 2; d * d <= n; d++) if (n % d == 0) return false;
        return true;
    }

    /** One away from 10 or from 20: 9, 11, 19, 21. */
    static boolean nearTen(int n) { return n == 9 || n == 11 || n == 19 || n == 21; }

    /** Neighbouring groups where one is exactly twice the other. */
    static int doublingPairs(int[] col) {
        int k = 0;
        for (int i = 0; i + 1 < col.length; i++)
            if (col[i] == 2 * col[i + 1] || col[i + 1] == 2 * col[i]) k++;
        return k;
    }

    static int sum(int[] col) { return Arrays.stream(col).sum(); }

    static boolean allPrime(int[] col) { return Arrays.stream(col).allMatch(TallyMarks::isPrime); }

    static boolean allNearTen(int[] col) { return Arrays.stream(col).allMatch(TallyMarks::nearTen); }

    static String join(int[] col) {
        StringBuilder s = new StringBuilder();
        for (int v : col) s.append(s.length() == 0 ? "" : " ").append(v);
        return s.toString();
    }

    // ----------------------------------------------------------------------------------------------------
    // 4. How surprising are the patterns? Exact counts under a stated assumption
    // ----------------------------------------------------------------------------------------------------

    static final int LO = 3, HI = 21, SIZES = HI - LO + 1;       // group sizes seen on the bone run from 1 to 21; the
                                                                  // main groups run from 3 to 21, so the model uses that

    /** Counts over all 19^4 four-group columns: [all prime & total % 12 == 0, all near-ten & total % 12 == 0,
     *  both of those at once, any of (all prime, all near-ten, total % 12 == 0), total columns]. */
    static long[] countFourGroupColumns() {
        long primeAnd12 = 0, nearAnd12 = 0, bothAnd12 = 0, anyPattern = 0, total = 0;
        int[] c = new int[4];
        for (c[0] = LO; c[0] <= HI; c[0]++)
            for (c[1] = LO; c[1] <= HI; c[1]++)
                for (c[2] = LO; c[2] <= HI; c[2]++)
                    for (c[3] = LO; c[3] <= HI; c[3]++) {
                        total++;
                        boolean p = allPrime(c), n = allNearTen(c), twelve = sum(c) % 12 == 0;
                        if (p && twelve) primeAnd12++;
                        if (n && twelve) nearAnd12++;
                        if (p && n && twelve) bothAnd12++;
                        if (p || n || twelve) anyPattern++;
                    }
        return new long[]{primeAnd12, nearAnd12, bothAnd12, anyPattern, total};
    }

    /**
     * Counts over all 19^8 eight-group columns, by dynamic programming over (last group size, doubling pairs so far
     * capped at 3, total mod 12). Returns [at least 3 doubling pairs & total % 12 == 0,
     * at least 3 doubling pairs or total % 12 == 0, total columns].
     */
    static long[] countEightGroupColumns() {
        long[][][] ways = new long[HI + 1][4][12];
        for (int v = LO; v <= HI; v++) ways[v][0][v % 12] = 1;
        for (int pos = 1; pos < 8; pos++) {
            long[][][] next = new long[HI + 1][4][12];
            for (int last = LO; last <= HI; last++)
                for (int d = 0; d < 4; d++)
                    for (int m = 0; m < 12; m++) {
                        long w = ways[last][d][m];
                        if (w == 0) continue;
                        for (int v = LO; v <= HI; v++) {
                            int nd = Math.min(3, d + ((v == 2 * last || last == 2 * v) ? 1 : 0));
                            next[v][nd][(m + v) % 12] += w;
                        }
                    }
            ways = next;
        }
        long both = 0, either = 0, total = 0;
        for (int last = LO; last <= HI; last++)
            for (int d = 0; d < 4; d++)
                for (int m = 0; m < 12; m++) {
                    long w = ways[last][d][m];
                    total += w;
                    if (d == 3 && m == 0) both += w;
                    if (d == 3 || m == 0) either += w;
                }
        return new long[]{both, either, total};
    }

    /** Brute force over a smaller alphabet, to check the dynamic programme on a case small enough to enumerate. */
    static long[] bruteEightGroup(int lo, int hi, int len) {
        long both = 0, either = 0, total = 0;
        int k = hi - lo + 1;
        int[] c = new int[len];
        long all = 1;
        for (int i = 0; i < len; i++) all *= k;
        for (long code = 0; code < all; code++) {
            long x = code;
            for (int i = 0; i < len; i++) { c[i] = lo + (int) (x % k); x /= k; }
            total++;
            boolean d3 = doublingPairs(c) >= 3, m = sum(c) % 12 == 0;
            if (d3 && m) both++;
            if (d3 || m) either++;
        }
        return new long[]{both, either, total};
    }

    static long[] dpEightGroup(int lo, int hi, int len) {
        long[][][] ways = new long[hi + 1][4][12];
        for (int v = lo; v <= hi; v++) ways[v][0][v % 12] = 1;
        for (int pos = 1; pos < len; pos++) {
            long[][][] next = new long[hi + 1][4][12];
            for (int last = lo; last <= hi; last++)
                for (int d = 0; d < 4; d++)
                    for (int m = 0; m < 12; m++) {
                        long w = ways[last][d][m];
                        if (w == 0) continue;
                        for (int v = lo; v <= hi; v++) {
                            int nd = Math.min(3, d + ((v == 2 * last || last == 2 * v) ? 1 : 0));
                            next[v][nd][(m + v) % 12] += w;
                        }
                    }
            ways = next;
        }
        long both = 0, either = 0, total = 0;
        for (int last = lo; last <= hi; last++)
            for (int d = 0; d < 4; d++)
                for (int m = 0; m < 12; m++) {
                    long w = ways[last][d][m];
                    total += w;
                    if (d == 3 && m == 0) both += w;
                    if (d == 3 || m == 0) either += w;
                }
        return new long[]{both, either, total};
    }

    // ----------------------------------------------------------------------------------------------------
    // 5. The split tally: two halves that must match
    // ----------------------------------------------------------------------------------------------------

    /** A notch: where along the stick it is cut, and how wide (wider notches stood for larger sums). */
    record Notch(int at, int width) {}

    /** Cutting the notches across the whole stick, then splitting it lengthwise, gives two halves with the same notches. */
    static List<List<Notch>> cutAndSplit(List<Notch> notches) {
        List<Notch> stock = new ArrayList<>(notches), foil = new ArrayList<>(notches);
        return List.of(stock, foil);
    }

    /** The two halves are laid side by side: they match only if every notch lines up. */
    static boolean halvesMatch(List<Notch> stock, List<Notch> foil) {
        return new HashSet<>(stock).equals(new HashSet<>(foil)) && stock.size() == foil.size();
    }

    // ----------------------------------------------------------------------------------------------------

    public static void main(String[] args) {
        // 1. matching
        int[][] examples = {{12, 9}, {7, 7}, {15, 23}};
        for (int[] e : examples) {
            Match m = match(herd("sheep", e[0]), herd("stone", e[1]));
            check(m.pairs() == Math.min(e[0], e[1]), "pairs");
            check(m.leftOver() == Math.abs(e[0] - e[1]), "left over");
            System.out.printf("match %d %d: pairs=%d winner=%s by=%d counting-needs=%d%n", e[0], e[1], m.pairs(),
                    m.winner() == 0 ? "same" : (m.winner() == 1 ? "first" : "second"), m.leftOver(), e[0] + e[1]);
        }
        Random rnd = new Random(1);
        int agree = 0, trials = 200_000;
        for (int i = 0; i < trials; i++) {
            int a = rnd.nextInt(61), b = rnd.nextInt(61);
            Match m = match(herd("a", a), herd("b", b));
            int byCounting = Integer.compare(a, b);
            int byMatching = m.winner() == 0 ? 0 : (m.winner() == 1 ? 1 : -1);
            check(byCounting == byMatching, "matching agrees with counting");
            agree++;
        }
        System.out.printf("matchcheck: %d random pairs of collections (0 to 60 things each), matching agreed with counting every time%n", agree);

        // 2. the tally as a log
        Tally t = new Tally();
        String[] days = {"new moon", "day", "day", "day", "half moon", "day", "day"};
        for (String d : days) t.mark(d);
        check(t.count() == days.length, "count is the length of the log");
        check(t.replay().equals(List.of(days)), "replay gives back every mark in order");
        System.out.printf("log: %d marks added, count=%d, replay=%s%n", days.length, t.count(), String.join(",", t.replay()));
        for (int n : new int[]{4, 7, 23, 60, 168, 1000}) {
            check(looksByFives(n) <= looksOneByOne(n), "grouping never needs more looks");
            System.out.printf("read %d: one-by-one=%d by-fives=%d%n", n, looksOneByOne(n), looksByFives(n));
        }
        for (int n = 0; n <= 10_000; n++) check(looksByFives(n) == (n + 4) / 5, "looks by fives is n/5 rounded up");

        // 3. the Ishango bone
        check(sum(COLUMN_G) == 60 && sum(COLUMN_M) == 48 && sum(COLUMN_D) == 60, "column totals 60, 48, 60");
        check(sum(COLUMN_G) + sum(COLUMN_M) + sum(COLUMN_D) == 168, "168 notches, as the holding museum counts them");
        check(allPrime(COLUMN_G), "column G is the four primes between 10 and 20");
        int primesBetween10And20 = 0;
        for (int n = 10; n <= 20; n++) if (isPrime(n)) primesBetween10And20++;
        check(primesBetween10And20 == 4, "there are exactly four primes between 10 and 20");
        check(allNearTen(COLUMN_D), "column D is 10+1, 20+1, 20-1, 10-1");
        check(sum(COLUMN_M_SPLIT) == 48, "splitting groups keeps the marks");
        System.out.printf("ishango G: %s total=%d all-prime=%s near-ten=%s doubling-pairs=%d%n", join(COLUMN_G), sum(COLUMN_G),
                allPrime(COLUMN_G), allNearTen(COLUMN_G), doublingPairs(COLUMN_G));
        System.out.printf("ishango M: %s total=%d all-prime=%s near-ten=%s doubling-pairs=%d%n", join(COLUMN_M), sum(COLUMN_M),
                allPrime(COLUMN_M), allNearTen(COLUMN_M), doublingPairs(COLUMN_M));
        System.out.printf("ishango D: %s total=%d all-prime=%s near-ten=%s doubling-pairs=%d%n", join(COLUMN_D), sum(COLUMN_D),
                allPrime(COLUMN_D), allNearTen(COLUMN_D), doublingPairs(COLUMN_D));
        System.out.printf("ishango total: %d notches in 3 columns of 4, 8 and 4 groups%n", sum(COLUMN_G) + sum(COLUMN_M) + sum(COLUMN_D));
        System.out.printf("regroup M: %s total=%d doubling-pairs=%d (was %d)%n", join(COLUMN_M_SPLIT), sum(COLUMN_M_SPLIT),
                doublingPairs(COLUMN_M_SPLIT), doublingPairs(COLUMN_M));
        check(doublingPairs(COLUMN_M) == 3 && doublingPairs(COLUMN_M_SPLIT) == 2, "doubling pairs 3, then 2 after splitting");

        // 4. how surprising?
        long[] small = bruteEightGroup(1, 6, 8), smallDp = dpEightGroup(1, 6, 8);
        check(Arrays.equals(small, smallDp), "the counting programme agrees with brute force on sizes 1..6");
        long[] small2 = bruteEightGroup(3, 9, 7), small2Dp = dpEightGroup(3, 9, 7);
        check(Arrays.equals(small2, small2Dp), "and on sizes 3..9, length 7");
        long[] four = countFourGroupColumns();
        long[] eight = countEightGroupColumns();
        check(four[4] == 130_321L, "19^4 four-group columns");
        check(eight[2] == 16_983_563_041L, "19^8 eight-group columns");
        long primeAnd12 = four[0], nearAnd12 = four[1], bothAnd12 = four[2], anyFour = four[3], allFour = four[4];
        long d3And12 = eight[0], anyEight = eight[1], allEight = eight[2];
        System.out.printf("model: group sizes equally likely from %d to %d; columns of 4, 8 and 4 groups as on the bone%n", LO, HI);
        System.out.printf("pattern all-prime-and-total-multiple-of-12: %d of %d four-group columns%n", primeAnd12, allFour);
        System.out.printf("pattern near-ten-and-total-multiple-of-12: %d of %d four-group columns%n", nearAnd12, allFour);
        System.out.printf("pattern both-of-those: %d of %d four-group columns%n", bothAnd12, allFour);
        System.out.printf("pattern three-doublings-and-total-multiple-of-12: %d of %d eight-group columns%n", d3And12, allEight);
        // the bone's combination: one four-group column all prime, the other all near-ten (either way round), the middle
        // column three doubling pairs, and every total a multiple of 12. Inclusion-exclusion for "either way round".
        double pA = (double) primeAnd12 / allFour, pB = (double) nearAnd12 / allFour, pAB = (double) bothAnd12 / allFour;
        double pM = (double) d3And12 / allEight;
        double pBone = (2 * pA * pB - pAB * pAB) * pM;
        System.out.printf("combination: probability %.3e, about 1 in %,d random bones%n", pBone, Math.round(1 / pBone));
        double pNoneFour = 1 - (double) anyFour / allFour, pNoneEight = 1 - (double) anyEight / allEight;
        double pSome = 1 - pNoneFour * pNoneFour * pNoneEight;
        System.out.printf("any-pattern: a four-group column shows at least one pattern %.1f%% of the time, the eight-group column %.1f%%; a random bone shows at least one somewhere %.1f%% of the time%n",
                100.0 * anyFour / allFour, 100.0 * anyEight / allEight, 100 * pSome);
        check(pBone > 0 && pBone < 1e-6, "the combination is rare under the model");
        check(pSome > 0.2, "some pattern somewhere is common under the model");

        // 5. the split tally
        Random r = new Random(1826);
        int honest = 0, caught = 0, n = 10_000;
        for (int i = 0; i < n; i++) {
            List<Notch> notches = new ArrayList<>();
            int k = 1 + r.nextInt(12), at = 0;
            for (int j = 0; j < k; j++) { at += 1 + r.nextInt(6); notches.add(new Notch(at, 1 + r.nextInt(4))); }
            List<List<Notch>> halves = cutAndSplit(notches);
            if (halvesMatch(halves.get(0), halves.get(1))) honest++;
            List<Notch> forged = new ArrayList<>(halves.get(0));         // the holder of the stock adds a notch
            if (r.nextBoolean()) forged.add(new Notch(at + 1 + r.nextInt(6), 1 + r.nextInt(4)));
            else forged.set(r.nextInt(forged.size()), new Notch(forged.get(0).at(), 9));   // or widens one
            if (!halvesMatch(forged, halves.get(1))) caught++;
        }
        check(honest == n && caught == n, "honest halves match; forged halves do not");
        System.out.printf("split: %d honest stick pairs matched, %d of %d forged halves were caught%n", honest, caught, n);

        System.out.printf("TallyMarks: %d checks passed%n", passed);
    }
}
