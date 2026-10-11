import java.util.*;

/**
 * Era 2, topic 4: zero becomes a number (Brahmagupta, Brahmasphutasiddhanta, Bhillamala, 628 CE; the Gwalior
 * inscription of 876 CE).
 *
 * HOW IT WORKS
 *   Place value writes a number as digits whose worth depends on their position. Without a mark for an empty place,
 *   2, 7 could mean 27, 207, 270 or 2700: the reader has to guess. A placeholder fixes the reading; making zero a number
 *   lets it take part in arithmetic. Brahmagupta's rules treat zero alongside "fortunes" and "debts" (positive and
 *   negative numbers): a fortune minus zero is a fortune, zero minus a debt is a fortune, zero times anything is zero,
 *   and so on. One rule, zero divided by zero is zero, was later rejected.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Measures how ambiguous place value is without zero: in base 10 up to a million, and in base 60 (the
 *      Babylonian system) up to 60^3, with no mark at all and with a placeholder that is never written at the end.
 *   2. Writes the Gwalior numbers (933, 187, 270, 50) and shows what each would collide with without a zero.
 *   3. Implements Brahmagupta's rules for fortunes, debts and zero, and compares them with modern integer arithmetic
 *      on every pair from -60 to 60.
 *   4. Shows what Java does with division by zero today: an exception for whole numbers; infinity, minus infinity
 *      and "not a number" for floating point, with a zero that has a sign.
 *   5. Defines x / 0 = 0, the convention of the Lean and Isabelle proof assistants (and Brahmagupta's answer for 0 / 0),
 *      and checks which laws of fractions survive it, on every pair of fractions in a grid.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ZeroAsANumber.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ZeroAsANumber {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** The digits of n in a base, most significant first. */
    static int[] digits(long n, int base) {
        List<Integer> d = new ArrayList<>();
        while (n > 0) { d.add(0, (int) (n % base)); n /= base; }
        return d.stream().mapToInt(Integer::intValue).toArray();
    }

    /** How n is written with no mark for an empty place: the non-zero digits only. */
    static String noZero(long n, int base) {
        StringJoiner s = new StringJoiner(" ");
        for (int x : digits(n, base)) if (x != 0) s.add(Integer.toString(x));
        return s.toString();
    }

    /** With a placeholder inside the number but none at the end (the Babylonian practice after about 400 BCE). */
    static String medialOnly(long n, int base) {
        int[] d = digits(n, base);
        int end = d.length;
        while (end > 0 && d[end - 1] == 0) end--;
        StringJoiner s = new StringJoiner(" ");
        for (int i = 0; i < end; i++) s.add(d[i] == 0 ? "." : Integer.toString(d[i]));
        return s.toString();
    }

    /** {numbers whose written form is shared, largest group, the form of the largest group}. */
    static Object[] ambiguity(long max, int base, boolean medial) {
        Map<String, Integer> count = new HashMap<>();
        for (long n = 1; n <= max; n++) count.merge(medial ? medialOnly(n, base) : noZero(n, base), 1, Integer::sum);
        long shared = 0;
        int biggest = 0;
        String form = "";
        for (Map.Entry<String, Integer> e : count.entrySet()) {
            if (e.getValue() > 1) shared += e.getValue();
            if (e.getValue() > biggest || (e.getValue() == biggest && e.getKey().compareTo(form) < 0)) { biggest = e.getValue(); form = e.getKey(); }
        }
        return new Object[]{shared, biggest, form};
    }

    // ---- Brahmagupta's rules ---------------------------------------------------------------------------------------
    /** A number as Brahmagupta classes it: a fortune (positive), a debt (negative) or zero; and its size. */
    record B(int kind, long size) {                     // kind: +1 fortune, -1 debt, 0 zero
        static B of(long v) { return new B(Long.signum(v), Math.abs(v)); }
        long value() { return kind * size; }
    }

    /** Addition by the rules: like kinds add; unlike kinds give the difference, of the kind of the larger; zero changes nothing. */
    static B add(B a, B b) {
        if (a.kind == 0) return b;                          // zero added to a number leaves it unchanged
        if (b.kind == 0) return a;
        if (a.kind == b.kind) return new B(a.kind, a.size + b.size);
        if (a.size == b.size) return new B(0, 0);           // a fortune and an equal debt: zero
        return a.size > b.size ? new B(a.kind, a.size - b.size) : new B(b.kind, b.size - a.size);
    }

    /** Subtraction: "a debt minus zero is a debt", "a debt subtracted from zero is a fortune", and so on. */
    static B subtract(B a, B b) {
        if (b.kind == 0) return a;                          // a debt (fortune, zero) minus zero is a debt (fortune, zero)
        if (a.kind == 0) return new B(-b.kind, b.size);     // subtracted from zero, a debt becomes a fortune and a fortune a debt
        return add(a, new B(-b.kind, b.size));
    }

    /** Multiplication: zero times anything is zero; like kinds give a fortune, unlike a debt. */
    static B multiply(B a, B b) {
        if (a.kind == 0 || b.kind == 0) return new B(0, 0);
        return new B(a.kind * b.kind, a.size * b.size);
    }

    /** Division, as a fraction: {kind, numerator, denominator}; zero over zero is zero; n over zero stays n/0. */
    static long[] divide(B a, B b) {
        if (a.kind == 0 && b.kind == 0) return new long[]{0, 0, 1};       // "zero divided by zero is zero"
        if (b.kind == 0) return new long[]{a.kind, a.size, 0};            // "a fraction with zero as denominator"
        if (a.kind == 0) return new long[]{0, 0, 1};
        long g = gcd(a.size, b.size);
        return new long[]{a.kind * b.kind, a.size / g, b.size / g};
    }

    static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }

    // ---- fractions with x / 0 = 0 ----------------------------------------------------------------------------------
    record Q(long n, long d) {
        static Q of(long n, long d) {
            if (d == 0) return new Q(0, 1);                 // the convention: anything divided by zero is zero
            if (d < 0) { n = -n; d = -d; }
            long g = gcd(Math.abs(n), d);
            return new Q(n / g, d / g);
        }
        Q plus(Q o) { return of(n * o.d + o.n * d, d * o.d); }
        Q times(Q o) { return of(n * o.n, d * o.d); }
        Q div(Q o) { return of(n * o.d, d * o.n); }         // o = 0 gives a zero denominator, hence 0
        boolean zero() { return n == 0; }
    }

    public static void main(String[] args) {
        // ---- ambiguity without zero -----------------------------------------------------------------------------
        Object[] dec = ambiguity(999_999, 10, false);
        long decShared = (long) dec[0];
        int ones = 0;
        for (long n = 1; n <= 999_999; n++) if (noZero(n, 10).equals("1")) ones++;
        check(ones == 6, "1, 10, 100, 1000, 10000 and 100000 all look like 1");
        System.out.printf("base10 no mark: of 999999 numbers, %d share their written form with another ; largest group %d (written \"%s\")%n",
                decShared, (int) dec[1], dec[2]);
        long max60 = 60L * 60 * 60 - 1;
        Object[] bab = ambiguity(max60, 60, false);
        Object[] babMed = ambiguity(max60, 60, true);
        System.out.printf("base60 no mark: of %d numbers (three sexagesimal places), %d share their written form ; largest group %d%n",
                max60, (long) bab[0], (int) bab[1]);
        System.out.printf("base60 medial mark: with a placeholder never written at the end, %d still share ; largest group %d%n",
                (long) babMed[0], (int) babMed[1]);
        check((long) babMed[0] < (long) bab[0], "a placeholder removes most of the ambiguity");
        long trailing = 0;                                  // with a medial mark, n and 60n always collide
        for (long n = 1; n <= max60; n++) if (n % 60 == 0 || n * 60 <= max60) trailing++;
        check(trailing == (long) babMed[0], "what remains is exactly the numbers that differ by factors of 60");

        // ---- Gwalior --------------------------------------------------------------------------------------------
        for (long g : new long[]{933, 187, 270, 50}) {
            List<Long> same = new ArrayList<>();
            for (long n = 1; n <= 99_999; n++) if (n != g && noZero(n, 10).equals(noZero(g, 10))) same.add(n);
            StringJoiner s = new StringJoiner(", ");
            for (int i = 0; i < Math.min(5, same.size()); i++) s.add(same.get(i).toString());
            System.out.printf("gwalior %d: without a zero it is written \"%s\" ; below 100000 that also means %d other numbers%s%n",
                    g, noZero(g, 10).replace(" ", ""), same.size(), same.isEmpty() ? "" : ", starting " + s);
        }

        // ---- Brahmagupta's rules against modern integers ---------------------------------------------------------
        int pairs = 0, agreeAdd = 0, agreeSub = 0, agreeMul = 0, agreeDiv = 0, divByZero = 0;
        for (long a = -60; a <= 60; a++) for (long b = -60; b <= 60; b++) {
            pairs++;
            B x = B.of(a), y = B.of(b);
            if (add(x, y).value() == a + b) agreeAdd++;
            if (subtract(x, y).value() == a - b) agreeSub++;
            if (multiply(x, y).value() == a * b) agreeMul++;
            check(add(x, y).value() == a + b && subtract(x, y).value() == a - b && multiply(x, y).value() == a * b,
                    "Brahmagupta's addition, subtraction and multiplication agree with modern integers");
            long[] q = divide(x, y);
            if (b == 0) { divByZero++; continue; }
            long g = gcd(Math.abs(a), Math.abs(b));
            long kind = Long.signum(a) * Long.signum(b);
            boolean same = a == 0 ? q[0] == 0 && q[1] == 0 : q[0] == kind && q[1] == Math.abs(a) / g && q[2] == Math.abs(b) / g;
            check(same, "Brahmagupta's division agrees when the divisor is not zero");
            if (same) agreeDiv++;
        }
        check(agreeAdd == pairs && agreeSub == pairs && agreeMul == pairs, "addition, subtraction and multiplication agree everywhere");
        check(agreeDiv == pairs - divByZero, "division agrees whenever the divisor is not zero");
        long[] zz = divide(B.of(0), B.of(0)), nz = divide(B.of(7), B.of(0));
        check(zz[1] == 0 && zz[2] == 1 && nz[2] == 0, "0/0 = 0 and 7/0 = 7/0 by the rules");
        System.out.printf("brahmagupta: %d pairs from -60 to 60 ; addition, subtraction and multiplication agree with modern integers on all %d ; division on all %d with a non-zero divisor ; 0/0 gives %d ; 7/0 gives the fraction %d/%d%n",
                pairs, pairs, pairs - divByZero, zz[1], nz[1], nz[2]);
        String[][] rules = {
                {"a debt minus zero", fmt(subtract(B.of(-5), B.of(0)))}, {"a fortune minus zero", fmt(subtract(B.of(5), B.of(0)))},
                {"zero minus zero", fmt(subtract(B.of(0), B.of(0)))}, {"zero minus a debt", fmt(subtract(B.of(0), B.of(-5)))},
                {"zero minus a fortune", fmt(subtract(B.of(0), B.of(5)))}, {"zero times a debt", fmt(multiply(B.of(0), B.of(-5)))},
                {"a debt times a debt", fmt(multiply(B.of(-5), B.of(-3)))}, {"a debt times a fortune", fmt(multiply(B.of(-5), B.of(3)))}};
        for (String[] r : rules) System.out.printf("rule %s: %s%n", r[0], r[1]);

        // ---- what Java does today -------------------------------------------------------------------------------------
        String intDiv;
        try { int zero = 0; intDiv = Integer.toString(7 / zero); } catch (ArithmeticException e) { intDiv = "ArithmeticException: " + e.getMessage(); }
        double pz = 0.0, nzd = -0.0;
        check(Double.isNaN(pz / pz) && 7 / pz == Double.POSITIVE_INFINITY && -7 / pz == Double.NEGATIVE_INFINITY, "floating point: NaN and infinities");
        check(pz == nzd && 1 / pz != 1 / nzd, "zero and minus zero are equal, but 1/0 and 1/-0 are not");
        check(pz / pz != pz / pz, "NaN is not equal even to itself");
        System.out.printf("java: 7 / 0 (int) -> %s ; 7.0 / 0.0 -> %s ; -7.0 / 0.0 -> %s ; 0.0 / 0.0 -> %s ; 0.0 == -0.0 is %b ; 1 / -0.0 -> %s ; NaN == NaN is %b%n",
                intDiv, 7 / pz, -7 / pz, pz / pz, pz == nzd, 1 / nzd, pz / pz == pz / pz);

        // ---- the proof assistants' convention: x / 0 = 0 ---------------------------------------------------------------
        List<Q> grid = new ArrayList<>();
        for (int n = -6; n <= 6; n++) for (int d = 1; d <= 6; d++) { Q q = Q.of(n, d); if (!grid.contains(q)) grid.add(q); }
        int triples = 0, assoc = 0, cancel = 0, cancelNz = 0, cancelNzCases = 0, addFrac = 0, distrib = 0;
        for (Q a : grid) for (Q b : grid) {
            // (a / b) x b = a: true for b != 0, and for b = 0 only when a = 0
            if (a.div(b).times(b).equals(a)) cancel++;
            if (!b.zero()) { cancelNzCases++; if (a.div(b).times(b).equals(a)) cancelNz++; }
            else check(a.div(b).times(b).equals(a) == a.zero(), "with b = 0, (a/b) x b = a only for a = 0");
            for (Q c : grid) {
                triples++;
                if (a.div(b).div(c).equals(a.div(b.times(c)))) assoc++;                // (a/b)/c = a/(bc)
                if (a.plus(b).div(c).equals(a.div(c).plus(b.div(c)))) distrib++;        // (a+b)/c = a/c + b/c
                if (a.div(b).plus(c.div(b)).equals(a.plus(c).div(b))) addFrac++;        // a/b + c/b = (a+c)/b
                check(a.div(b).div(c).equals(a.div(b.times(c))) && a.plus(b).div(c).equals(a.div(c).plus(b.div(c)))
                        && a.div(b).plus(c.div(b)).equals(a.plus(c).div(b)), "three laws of fractions survive x/0 = 0");
            }
        }
        int pairs2 = grid.size() * grid.size();
        check(cancelNz == cancelNzCases, "(a/b) x b = a whenever b is not zero");
        check(assoc == triples && distrib == triples && addFrac == triples, "these laws survive x/0 = 0 everywhere");
        check(cancel < pairs2, "but (a/b) x b = a fails when b = 0 and a is not");
        System.out.printf("convention: %d fractions, x/0 = 0 ; (a/b)/c = a/(bc), (a+b)/c = a/c + b/c and a/b + c/b = (a+c)/b hold in all %d cases ; (a/b) x b = a holds in %d of %d pairs, failing only when b = 0 and a is not 0%n",
                grid.size(), triples, cancel, pairs2);

        System.out.printf("ZeroAsANumber: %d checks passed%n", passed);
    }

    static String fmt(B b) { return b.kind == 0 ? "zero" : (b.kind > 0 ? "a fortune of " : "a debt of ") + b.size; }
}
