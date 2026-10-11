import java.util.*;

/**
 * Era 3, topic 13: Hollerith's tabulator (patent US 395,782, 1889; the United States census of 1890).
 *
 * HOW IT WORKS
 *   Each person becomes one card, with a hole punched for each answer (sex, born in the country or abroad, age group,
 *   and so on). To count, a clerk places a card in a press; pins come down, and wherever there is a hole a pin passes
 *   through into a cup of mercury, closes a circuit, and advances a dial by one. One pass of the cards fills many dials
 *   at once, and relays can count combinations ("native males aged 20 to 29") by requiring several holes together.
 *   A sorting table then shows which drawer each card should go into, so the deck can be divided and counted again for
 *   new questions without re-punching. Later sorters sorted on one column at a time; sorting a deck column by column,
 *   from the last digit to the first, sorts it completely (radix sort).
 *
 * WHAT THIS PROGRAM DOES
 *   1. Works out the speed-ups in the 1888 trial from the Census Bureau's published hours.
 *   2. Punches a synthetic population of 1,000,000 people onto cards, and counts it two ways: by hand tallies (one
 *      mark per person per question) and by the tabulator (one card per person per pass, many dials at once).
 *   3. Counts combinations with relays on 40 dials, as many as the 1890 tabulator had, in a single pass.
 *   4. Sorts the deck into drawers by a column, and sorts card numbers completely by passes column by column.
 *   5. Full circle: the same count as a modern group-by, and the clerk's time at 80 cards a minute.
 *   The population is invented test data, not census returns.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java HollerithTabulator.java
 *   Expected output: expected-output.txt in this folder.
 */
public class HollerithTabulator {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** A card: the punched positions, one per field. */
    record Card(int sex, int nativity, int age, int region, int occupation, int serial) {}

    static final String[] SEX = {"male", "female"}, NAT = {"native", "foreign-born"};

    public static void main(String[] args) {
        // ---- 1. the 1888 trial (hours from the Census Bureau's history page) ------------------------------------------
        double[] capture = {144.5, 100.5, 72.5}, prepare = {44.5, 55.5, 5.5};   // two rivals, then Hollerith
        System.out.printf("trial: 1880 returns from four areas of St Louis ; capturing the data: rivals %.1f and %.1f hours, Hollerith %.1f, %.1f and %.1f times faster ; preparing it for tabulation: rivals %.1f and %.1f hours, Hollerith %.1f, %.1f and %.1f times faster%n",
                capture[0], capture[1], capture[2], capture[0] / capture[2], capture[1] / capture[2],
                prepare[0], prepare[1], prepare[2], prepare[0] / prepare[2], prepare[1] / prepare[2]);
        check(Math.abs(prepare[1] / prepare[2] - 10.09) < 0.01, "the preparation speed-up");

        // ---- 2. a synthetic population -------------------------------------------------------------------------------
        Random rnd = new Random(1890);
        int N = 1_000_000;
        Card[] deck = new Card[N];
        for (int i = 0; i < N; i++) {
            int age = Math.min(9, (int) Math.abs(rnd.nextGaussian() * 2.6 + 2.8));   // ten age groups: 0-9, 10-19, ..., 90+
            deck[i] = new Card(rnd.nextInt(2), rnd.nextDouble() < 0.15 ? 1 : 0, age, rnd.nextInt(6), rnd.nextInt(10), i);
        }
        int questions = 5;                                       // sex, nativity, age group, region, occupation
        long tallyMarks = (long) N * questions;                   // one mark per person per question, then the marks must be counted
        // the tabulator: one pass reads every card once and advances one dial per question (and relay combinations too)
        long[][] dials = new long[questions][10];
        for (Card c : deck) { dials[0][c.sex]++; dials[1][c.nativity]++; dials[2][c.age]++; dials[3][c.region]++; dials[4][c.occupation]++; }
        for (int q = 0; q < questions; q++) { long s = 0; for (long v : dials[q]) s += v; check(s == N, "every card counted once per question"); }
        System.out.printf("count: %,d cards ; by hand, %,d tally marks (one per person per question, %d questions), each later counted again ; by the tabulator, one pass of %,d cards fills all %d questions' dials at once ; males %,d, females %,d ; native %,d, foreign-born %,d%n",
                N, tallyMarks, questions, N, questions, dials[0][0], dials[0][1], dials[1][0], dials[1][1]);

        // ---- 3. combinations on 40 dials ---------------------------------------------------------------------------------
        long[] combo = new long[40];                              // sex x nativity x age group = 2 x 2 x 10 = 40 dials
        for (Card c : deck) combo[(c.sex * 2 + c.nativity) * 10 + c.age]++;   // a relay closes only when all three holes are punched
        long s40 = 0; for (long v : combo) s40 += v;
        check(s40 == N, "the 40 combination dials account for every card");
        // check against counting each combination separately (40 passes)
        for (int sx = 0; sx < 2; sx++) for (int nt = 0; nt < 2; nt++) for (int ag = 0; ag < 10; ag++) {
            long direct = 0;
            for (Card c : deck) if (c.sex == sx && c.nativity == nt && c.age == ag) direct++;
            check(direct == combo[(sx * 2 + nt) * 10 + ag], "the relay count equals a separate count");
        }
        System.out.printf("combine: 2 sexes x 2 nativities x 10 age groups = 40 dials, as many as the 1890 tabulator had, filled in one pass ; e.g. native males aged 20 to 29: %,d ; foreign-born females aged 60 to 69: %,d ; a separate pass for each of the 40 combinations would read %,d cards instead of %,d%n",
                combo[(0 * 2 + 0) * 10 + 2], combo[(1 * 2 + 1) * 10 + 6], 40L * N, (long) N);

        // ---- 4. sorting ------------------------------------------------------------------------------------------------
        // the sorting table: after reading a card, the clerk drops it into the drawer for its region
        List<List<Card>> drawers = new ArrayList<>();
        for (int i = 0; i < 6; i++) drawers.add(new ArrayList<>());
        for (Card c : deck) drawers.get(c.region).add(c);
        StringJoiner dr = new StringJoiner(", ");
        for (List<Card> d : drawers) dr.add(String.format("%,d", d.size()));
        // then count occupations within one drawer only
        long[] occ = new long[10];
        for (Card c : drawers.get(3)) occ[c.occupation]++;
        long occSum = 0; for (long v : occ) occSum += v;
        check(occSum == drawers.get(3).size(), "the drawer's cards counted again");
        // radix sort by card number, one digit column at a time, last digit first, into 10 pockets
        Card[] shuffled = deck.clone();
        for (int i = N - 1; i > 0; i--) { int j = rnd.nextInt(i + 1); Card t = shuffled[i]; shuffled[i] = shuffled[j]; shuffled[j] = t; }
        Card[] cur = shuffled;
        int passes = 0;
        for (int place = 1; place < N; place *= 10) {
            List<List<Card>> pockets = new ArrayList<>();
            for (int i = 0; i < 10; i++) pockets.add(new ArrayList<>());
            for (Card c : cur) pockets.get((c.serial / place) % 10).add(c);   // stable: cards keep their order in each pocket
            int k = 0;
            for (List<Card> p : pockets) for (Card c : p) cur[k++] = c;
            passes++;
        }
        for (int i = 0; i < N; i++) check(cur[i].serial == i, "column-by-column sorting sorts the deck");
        long cardHandlings = (long) passes * N;
        double comparisons = N * (Math.log(N) / Math.log(2));
        System.out.printf("sort: dropping the cards into 6 drawers by region: %s ; one drawer recounted by occupation without re-punching ; sorting %,d shuffled cards by their 6-digit number, one column per pass, last digit first: %d passes, %,d card handlings ; a comparison sort needs about %,.0f comparisons%n",
                dr, N, passes, cardHandlings, comparisons);

        // ---- 5. full circle -------------------------------------------------------------------------------------------
        Map<String, Long> groupBy = new TreeMap<>();
        for (Card c : deck) groupBy.merge(SEX[c.sex] + " " + NAT[c.nativity], 1L, Long::sum);
        for (int sx = 0; sx < 2; sx++) for (int nt = 0; nt < 2; nt++) {
            long sum = 0; for (int ag = 0; ag < 10; ag++) sum += combo[(sx * 2 + nt) * 10 + ag];
            check(groupBy.get(SEX[sx] + " " + NAT[nt]) == sum, "the group-by equals the dials");
        }
        double minutes = N / 80.0;
        System.out.printf("circle: the same counts as a database group-by (sex, nativity): %s ; at 80 cards a minute, one clerk feeds %,d cards in %,.0f minutes (%,.0f hours) per pass%n",
                groupBy, N, minutes, minutes / 60);

        System.out.printf("HollerithTabulator: %d checks passed%n", passed);
    }
}
