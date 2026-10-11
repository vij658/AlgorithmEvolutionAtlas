import java.math.BigInteger;
import java.util.*;

/**
 * Era 2, topic 6: algorism and al-jabr (Muhammad ibn Musa al-Khwarizmi, House of Wisdom, Baghdad, c. 820-830 CE).
 *
 * HOW IT WORKS
 *   Al-Khwarizmi's algebra has no symbols, only words, and still it is an algorithm that works for any numbers.
 *   1. Al-jabr ("restoring"): a subtracted term is moved to the other side, where it is added.
 *   2. Al-muqabala ("balancing"): like terms on both sides cancel, leaving each kind on one side only.
 *   3. Divide by the number of squares, so that one square remains.
 *   4. The equation is now one of six types, each with a fixed recipe:
 *        squares equal roots; squares equal numbers; roots equal numbers;
 *        squares and roots equal numbers (x^2 + 10x = 39: halve the roots, 5; square, 25; add, 64; root, 8;
 *        take away half the roots: x = 3);
 *        squares and numbers equal roots (x^2 + 21 = 10x: half the roots plus or minus the root of
 *        25 - 21: x = 7 or 3);
 *        roots and numbers equal squares (3x + 4 = x^2: half the roots plus the root of 2 1/4 + 4: x = 4).
 *   Only positive answers count; a type with no positive answer is "impossible".
 *   His other book taught the Indian numerals and written, step-by-step arithmetic with them, including square roots.
 *   Latin copies began "Dixit Algorizmi", and his name became the word "algorithm".
 *
 * WHAT THIS PROGRAM DOES
 *   1. Solves the three worked examples of the mixed types by the recipes, step by step.
 *   2. Reduces 100,000 random equations, with subtracted terms on both sides, by al-jabr and al-muqabala, sorts them
 *      into the six types, solves them by the recipes, and checks every answer against the quadratic formula.
 *   3. Takes a square root digit by digit, as written arithmetic does, against the Babylonian averaging of Era 1.
 *   4. Shows what the recipe meets in floating point: Forsythe's example, where one root loses every digit, and the
 *      rearranged formula that keeps them.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AlKhwarizmi.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AlKhwarizmi {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- exact fractions ------------------------------------------------------------------------------------------
    record Q(long n, long d) implements Comparable<Q> {
        static Q of(long n, long d) {
            if (d < 0) { n = -n; d = -d; }
            long g = gcd(Math.abs(n), d);
            return new Q(n / g, d / g);
        }
        static Q of(long n) { return new Q(n, 1); }
        Q plus(Q o) { return of(n * o.d + o.n * d, d * o.d); }
        Q minus(Q o) { return of(n * o.d - o.n * d, d * o.d); }
        Q times(Q o) { return of(n * o.n, d * o.d); }
        Q div(Q o) { return of(n * o.d, d * o.n); }
        int sign() { return Long.signum(n); }
        public int compareTo(Q o) { return Long.compare(n * o.d, o.n * d); }
        /** The square root, if it is a fraction. */
        Q sqrt() {
            long rn = (long) Math.round(Math.sqrt((double) n)), rd = (long) Math.round(Math.sqrt((double) d));
            return rn * rn == n && rd * rd == d ? new Q(rn, rd) : null;
        }
        double value() { return (double) n / d; }
        public String toString() {
            if (d == 1) return Long.toString(n);
            long w = n / d, r = Math.abs(n % d);
            return w == 0 ? n + "/" + d : w + " " + r + "/" + d;
        }
    }

    static long gcd(long a, long b) { return b == 0 ? a : gcd(b, a % b); }

    static final String[] TYPES = {"squares equal roots", "squares equal numbers", "roots equal numbers",
            "squares and roots equal numbers", "squares and numbers equal roots", "roots and numbers equal squares"};

    /**
     * An equation as two sides, each with a number of squares, roots and units (any may be negative: subtracted).
     * Returns the type (0-5, or -1 if nothing is left), the reduced coefficients, and the positive roots (as doubles).
     */
    static int lastType;
    static double[] solve(long[] left, long[] right, List<String> say) {
        long[] L = left.clone(), R = right.clone();
        // al-jabr: a subtracted term is restored, moving it to the other side
        for (int i = 0; i < 3; i++) {
            if (L[i] < 0) { R[i] -= L[i]; L[i] = 0; }
            if (R[i] < 0) { L[i] -= R[i]; R[i] = 0; }
        }
        if (say != null) say.add("al-jabr: " + side(L) + " = " + side(R));
        // al-muqabala: like terms on both sides cancel
        for (int i = 0; i < 3; i++) {
            long m = Math.min(L[i], R[i]);
            L[i] -= m; R[i] -= m;
        }
        if (say != null) say.add("al-muqabala: " + side(L) + " = " + side(R));
        // gather: s squares, r roots, n units, each on a known side
        long sq = L[0] - R[0], rt = L[1] - R[1], un = L[2] - R[2];   // sq x^2 + rt x + un = 0
        if (sq < 0 || (sq == 0 && rt < 0)) { sq = -sq; rt = -rt; un = -un; }
        Q s = Q.of(sq), b = Q.of(Math.abs(rt)), c = Q.of(Math.abs(un));
        if (sq != 0) { b = b.div(s); c = c.div(s); }
        List<Double> roots = new ArrayList<>();
        int type;
        if (sq == 0 && rt == 0) { lastType = -1; return new double[0]; }
        if (sq == 0) {                                        // roots equal numbers
            type = 2;
            if (rt * -un > 0) roots.add((double) -un / rt);
        } else if (rt == 0) {                                 // squares equal numbers
            type = 1;
            if (un < 0) roots.add(Math.sqrt(c.value()));
        } else if (un == 0) {                                 // squares equal roots
            type = 0;
            if (rt < 0) roots.add(b.value());
        } else {
            Q half = b.div(Q.of(2)), sqHalf = half.times(half);
            if (rt > 0 && un < 0) {                           // squares and roots equal numbers: x = sqrt((b/2)^2 + c) - b/2
                type = 3;
                roots.add(Math.sqrt(sqHalf.plus(c).value()) - half.value());
                if (say != null) say.add(String.format("recipe: halve the roots, %s ; square it, %s ; add the number, %s ; take the root ; take away half the roots", half, sqHalf, sqHalf.plus(c)));
            } else if (rt < 0 && un > 0) {                    // squares and numbers equal roots: x = b/2 -+ sqrt((b/2)^2 - c)
                type = 4;
                Q disc = sqHalf.minus(c);
                if (disc.sign() >= 0) {
                    double r = Math.sqrt(disc.value());
                    roots.add(half.value() - r);
                    if (disc.sign() > 0) roots.add(half.value() + r);
                }
                if (say != null) say.add(String.format("recipe: halve the roots, %s ; square it, %s ; take away the number, %s ; its root added to or taken from half the roots", half, sqHalf, disc));
            } else if (rt < 0 && un < 0) {                    // roots and numbers equal squares: x = b/2 + sqrt((b/2)^2 + c)
                type = 5;
                roots.add(half.value() + Math.sqrt(sqHalf.plus(c).value()));
                if (say != null) say.add(String.format("recipe: halve the roots, %s ; square it, %s ; add the number, %s ; take the root ; add half the roots", half, sqHalf, sqHalf.plus(c)));
            } else {                                          // all terms on one side: no positive answer
                type = -2;
            }
        }
        lastType = type;
        Collections.sort(roots);
        return roots.stream().mapToDouble(Double::doubleValue).toArray();
    }

    static String side(long[] t) {
        StringJoiner s = new StringJoiner(" + ");
        if (t[0] != 0) s.add(t[0] + (Math.abs(t[0]) == 1 ? " square" : " squares"));
        if (t[1] != 0) s.add(t[1] + (Math.abs(t[1]) == 1 ? " root" : " roots"));
        if (t[2] != 0) s.add(t[2] + "");
        return s.length() == 0 ? "0" : s.toString();
    }

    /** Positive real roots of a x^2 + b x + c = 0 by the modern formula. */
    static double[] formula(double a, double b, double c) {
        List<Double> r = new ArrayList<>();
        if (a == 0) { if (b != 0 && -c / b > 0) r.add(-c / b); }
        else {
            double D = b * b - 4 * a * c;
            if (D >= 0) {
                double s = Math.sqrt(D);
                for (double x : new double[]{(-b - s) / (2 * a), (-b + s) / (2 * a)}) if (x > 1e-12 && !r.contains(x)) r.add(x);
            }
        }
        Collections.sort(r);
        return r.stream().mapToDouble(Double::doubleValue).toArray();
    }

    public static void main(String[] args) {
        // ---- the worked examples -----------------------------------------------------------------------------------
        long[][][] examples = {{{1, 10, 0}, {0, 0, 39}}, {{1, 0, 21}, {0, 10, 0}}, {{0, 3, 4}, {1, 0, 0}}};
        String[] names = {"a square and 10 roots equal 39", "a square and 21 equal 10 roots", "3 roots and 4 equal a square"};
        double[][] expect = {{3}, {3, 7}, {4}};
        for (int e = 0; e < 3; e++) {
            List<String> say = new ArrayList<>();
            double[] r = solve(examples[e][0], examples[e][1], say);
            check(Arrays.equals(r, expect[e]), "the worked example " + names[e]);
            StringJoiner rs = new StringJoiner(" or ");
            for (double x : r) rs.add(String.valueOf((long) x));
            System.out.printf("example %s: type %d, %s ; %s ; x = %s%n", names[e], lastType + 1, TYPES[lastType], say.get(say.size() - 1), rs);
        }

        // ---- reduce and solve random equations -----------------------------------------------------------------
        Random rnd = new Random(820);
        int[] perType = new int[6];
        int none = 0, impossible = 0, agree = 0, total = 100_000;
        for (int t = 0; t < total; t++) {
            long[] L = new long[3], R = new long[3];
            for (int i = 0; i < 3; i++) { L[i] = rnd.nextInt(21) - 10; R[i] = rnd.nextInt(21) - 10; }
            double[] mine = solve(L, R, null);
            double a = L[0] - R[0], b = L[1] - R[1], c = L[2] - R[2];
            double[] modern = formula(a, b, c);
            if (lastType == -1) { none++; continue; }
            if (lastType == -2) { impossible++; check(modern.length == 0, "no positive answer when every term is on one side"); continue; }
            perType[lastType]++;
            boolean same = mine.length == modern.length;
            for (int i = 0; same && i < mine.length; i++) same = Math.abs(mine[i] - modern[i]) < 1e-9 * Math.max(1, modern[i]);
            check(same, "the recipe agrees with the quadratic formula");
            agree++;
        }
        StringJoiner pt = new StringJoiner(" ; ");
        for (int i = 0; i < 6; i++) pt.add(TYPES[i] + " " + perType[i]);
        System.out.printf("random: %d equations with terms subtracted on both sides ; %d reduce to nothing ; %d have every term on one side ; %d sorted into the six types, all agreeing with the quadratic formula: %s%n",
                total, none, impossible, agree, pt);
        List<String> say = new ArrayList<>();
        double[] r = solve(new long[]{-1, 10, 0}, new long[]{0, 4, 9}, say);   // 10 roots minus a square = 4 roots and 9
        check(r.length == 1 && r[0] == 3 && lastType == 4, "10 roots - a square = 4 roots + 9 reduces to a square and 9 equal 6 roots: x = 3");
        System.out.printf("reduce: 10 roots - 1 square = 4 roots + 9 ; %s ; %s ; %s ; x = %s%n", say.get(0), say.get(1), say.get(2),
                r.length == 0 ? "none" : String.valueOf(r[0]).replace(".0", ""));

        // ---- square roots: digit by digit, against averaging -----------------------------------------------------
        int digits = 60;
        BigInteger target = BigInteger.TWO.multiply(BigInteger.TEN.pow(2 * digits));    // sqrt(2) x 10^60
        // digit by digit: bring down two digits at a time, find the largest next digit that fits
        String two = "2" + "0".repeat(2 * digits);
        BigInteger rem = BigInteger.ZERO, root = BigInteger.ZERO;
        int digitSteps = 0, trials = 0;
        for (int i = 0; i < two.length(); i += 2) {
            String pair = (i == 0 && two.length() % 2 == 1) ? two.substring(0, 1) : two.substring(i, Math.min(i + 2, two.length()));
            if (i == 0 && two.length() % 2 == 1) i -= 1;
            rem = rem.multiply(BigInteger.valueOf(100)).add(new BigInteger(pair));
            int dgt = 0;
            for (int d = 9; d >= 0; d--) {
                trials++;
                BigInteger t = root.multiply(BigInteger.valueOf(20)).add(BigInteger.valueOf(d)).multiply(BigInteger.valueOf(d));
                if (t.compareTo(rem) <= 0) { dgt = d; rem = rem.subtract(t); break; }
            }
            root = root.multiply(BigInteger.TEN).add(BigInteger.valueOf(dgt));
            digitSteps++;
        }
        check(root.equals(target.sqrt()), "digit-by-digit square root is exact");
        // Babylonian averaging (Era 1, topic 4), on whole numbers scaled by 10^60
        BigInteger x = BigInteger.TEN.pow(digits);
        int avgSteps = 0;
        while (true) {
            BigInteger nx = x.add(target.divide(x)).shiftRight(1);
            avgSteps++;
            if (nx.subtract(x).abs().compareTo(BigInteger.ONE) <= 0) { x = nx; break; }
            x = nx;
        }
        while (x.multiply(x).compareTo(target) > 0) x = x.subtract(BigInteger.ONE);
        check(x.equals(target.sqrt()), "averaging reaches the same root");
        System.out.printf("sqrt2: %d digits of the root of 2 ; digit by digit %d steps (%d trial digits) ; averaging %d steps ; 1.%s...%n",
                digits + 1, digitSteps, trials, avgSteps, root.toString().substring(1, 21));

        // ---- the recipe in floating point (Forsythe 1970) ----------------------------------------------------------
        for (double big : new double[]{1e5, 1e9}) {
            // squares and numbers equal roots: x^2 + 1 = big x ; the small root by the recipe and by the rearranged form
            double half = big / 2, rt = Math.sqrt(half * half - 1);
            double recipe = half - rt;
            double stable = 1 / (half + rt);                  // the product of the roots is 1, so small = 1 / large
            double truth = stable;
            check(Math.abs(stable * (half + rt) - 1) < 1e-15, "rearranged root");
            System.out.printf("float x^2 + 1 = %.0e x: small root by the recipe %s ; rearranged %s ; recipe error %.1e of the answer%n",
                    big, recipe, stable, Math.abs(recipe - truth) / truth);
        }

        System.out.printf("AlKhwarizmi: %d checks passed%n", passed);
    }
}
