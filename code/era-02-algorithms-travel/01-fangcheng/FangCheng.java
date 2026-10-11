import java.math.BigInteger;
import java.util.*;

/**
 * Era 2, topic 1: elimination on the counting board, fangcheng ("rectangular arrays"), chapter 8 of the Nine Chapters
 * on the Mathematical Art (compiled c. 200 BCE - 50 CE, dates disputed; Liu Hui's commentary 263 CE).
 *
 * HOW IT WORKS
 *   Each condition of the problem is laid out as one column of rods: the counts of each unknown from top to bottom,
 *   and the total at the foot. The first condition goes on the right. To clear the top place of another column,
 *   multiply that whole column by the top number of the right-hand column, then subtract the right-hand column from it
 *   again and again until the top place is empty. Repeat with the next place down, until the board is a triangle and
 *   the last column holds one unknown alone. Then work back up. Because every column is multiplied before it is
 *   subtracted, nothing is ever divided until the end, and every number on the board stays a whole number.
 *   Subtraction can leave less than nothing, so the board needs negative numbers and rules for them: subtract like
 *   signs, add unlike signs, and a number taken from an empty place changes its sign.
 *   Turned a quarter turn, the board is the matrix of modern "Gaussian" elimination.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Solves Problem 1 of chapter 8 (three grades of grain) step by step on the board, checks each step against the
 *      intermediate columns published for it, and finishes with the Nine Chapters' common divisor.
 *   2. Solves the cattle, sheep and pigs problem of the same chapter, where conditions and working are negative, and
 *      counts how often each part of the sign rule is used.
 *   3. Measures how big the numbers get: plain cross-multiplication (digits double at each step), the same with common
 *      factors cancelled, and Bareiss's 1968 fraction-free method, against exact rational answers.
 *   4. Counts the multiplications of cross-multiplying against modern elimination by division.
 *   5. Shows what machines added: a tiny pivot that wrecks elimination in floating point, partial pivoting that fixes
 *      it, and the textbook worst case, where partial pivoting itself lets the numbers grow as 2^(n-1).
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java FangCheng.java
 *   Expected output: expected-output.txt in this folder.
 */
public class FangCheng {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static BigInteger big(long v) { return BigInteger.valueOf(v); }

    // ------------------------------------------------------------------------------------------------------------------
    // Exact fractions, for answers
    // ------------------------------------------------------------------------------------------------------------------
    record Frac(BigInteger num, BigInteger den) {
        static Frac of(BigInteger n, BigInteger d) {
            if (d.signum() < 0) { n = n.negate(); d = d.negate(); }
            BigInteger g = n.gcd(d);
            if (g.signum() == 0) g = BigInteger.ONE;
            return new Frac(n.divide(g), d.divide(g));
        }
        Frac minus(Frac o) { return of(num.multiply(o.den).subtract(o.num.multiply(den)), den.multiply(o.den)); }
        Frac times(BigInteger k) { return of(num.multiply(k), den); }
        Frac over(BigInteger k) { return of(num, den.multiply(k)); }
        /** "9 1/4", as the Nine Chapters writes a whole number and a part. */
        String mixed() {
            BigInteger[] qr = num.divideAndRemainder(den);
            if (qr[1].signum() == 0) return qr[0].toString();
            if (qr[0].signum() == 0) return num + "/" + den;
            return qr[0] + " " + qr[1].abs() + "/" + den;
        }
    }

    // ------------------------------------------------------------------------------------------------------------------
    // The board. col[j] is the j-th condition, counted from the right; col[j][i] is its count of unknown i (top to
    // bottom) and col[j][n] is its total, at the foot of the column.
    // ------------------------------------------------------------------------------------------------------------------
    static BigInteger[][] board(long[][] cols) {
        BigInteger[][] b = new BigInteger[cols.length][];
        for (int j = 0; j < cols.length; j++) {
            b[j] = new BigInteger[cols[j].length];
            for (int i = 0; i < cols[j].length; i++) b[j][i] = big(cols[j][i]);
        }
        return b;
    }

    static BigInteger[][] copy(BigInteger[][] b) {
        BigInteger[][] c = new BigInteger[b.length][];
        for (int j = 0; j < b.length; j++) c[j] = b[j].clone();
        return c;
    }

    static String col(BigInteger[] c) {
        StringJoiner s = new StringJoiner(" ");
        for (BigInteger v : c) s.add(v.toString());
        return s.toString();
    }

    /** The board as it is seen, left to right: the last condition first. */
    static String seen(BigInteger[][] b) {
        StringJoiner s = new StringJoiner(" | ");
        for (int j = b.length - 1; j >= 0; j--) s.add(col(b[j]));
        return s.toString();
    }

    static long mults;                              // multiplications of board numbers
    static long likeSigns, unlikeSigns, noOpponent;  // how a subtraction on the board was done (the sign rule)
    static BigInteger biggest;                      // the largest number that appeared on the board
    static List<Integer> steps;                     // if not null: digits of the largest number so far, after each place

    static void see(BigInteger v) { if (v.abs().compareTo(biggest) > 0) biggest = v.abs(); }

    /** x - y, done the way the sign rule describes, and counted. */
    static BigInteger boardSubtract(BigInteger x, BigInteger y) {
        if (y.signum() == 0) return x;
        if (x.signum() == 0) noOpponent++;                 // nothing to take from: the number changes sign
        else if (x.signum() == y.signum()) likeSigns++;    // like signs: take the difference
        else unlikeSigns++;                                // unlike signs: add
        return x.subtract(y);
    }

    /**
     * Fangcheng elimination. For each place k, the column k is the "pivot"; every column j to its left is multiplied by
     * the pivot's number in place k, and the pivot column is subtracted from it as many times as column j had in place
     * k, which empties that place. With reduce, each new column is divided by the common factor of its numbers.
     * trace (may be null) receives one line per step.
     */
    static BigInteger[][] fangcheng(BigInteger[][] start, boolean reduce, List<String> trace) {
        BigInteger[][] b = copy(start);
        int n = b.length;
        for (BigInteger[] c : b) for (BigInteger v : c) see(v);
        for (int k = 0; k < n; k++) {
            if (b[k][k].signum() == 0) {                   // an empty pivot place: use a later column instead
                for (int j = k + 1; j < n; j++) if (b[j][k].signum() != 0) { BigInteger[] t = b[k]; b[k] = b[j]; b[j] = t; break; }
            }
            BigInteger p = b[k][k];
            for (int j = k + 1; j < n; j++) {
                BigInteger a = b[j][k];
                if (a.signum() == 0) continue;             // the place is already empty
                BigInteger[] times = new BigInteger[n + 1];
                for (int i = 0; i <= n; i++) times[i] = i < k ? BigInteger.ZERO : b[j][i].multiply(p);
                mults += n - k;                            // places below k and the total; place k is known to empty
                for (int i = k; i <= n; i++) {
                    BigInteger sub = b[k][i].multiply(a);
                    b[j][i] = i == k ? BigInteger.ZERO : boardSubtract(times[i], sub);
                    see(b[j][i]);
                }
                mults += n - k;
                if (reduce) {
                    BigInteger g = BigInteger.ZERO;
                    for (BigInteger v : b[j]) g = g.gcd(v);
                    if (g.compareTo(BigInteger.ONE) > 0) for (int i = 0; i <= n; i++) b[j][i] = b[j][i].divide(g);
                }
                if (trace != null)
                    trace.add(String.format("column %d x %s = %s ; %s column %d %s time%s -> %s",
                            j + 1, p, col(times), a.signum() > 0 ? "subtract" : "add", k + 1, a.abs(),
                            a.abs().equals(BigInteger.ONE) ? "" : "s", col(b[j])));
            }
            if (steps != null) steps.add(biggest.toString().length());
        }
        return b;
    }

    /** Bareiss (1968): the same cross-multiplication, then an exact division by the previous pivot. Null if singular. */
    static BigInteger[][] bareiss(BigInteger[][] start) {
        BigInteger[][] b = copy(start);
        int n = b.length;
        BigInteger prev = BigInteger.ONE;
        for (int k = 0; k < n; k++) {
            if (b[k][k].signum() == 0) {
                for (int j = k + 1; j < n; j++) if (b[j][k].signum() != 0) { BigInteger[] t = b[k]; b[k] = b[j]; b[j] = t; break; }
            }
            BigInteger p = b[k][k];
            if (p.signum() == 0) return null;
            for (int j = k + 1; j < n; j++) {
                BigInteger a = b[j][k];
                for (int i = k + 1; i <= n; i++) {
                    BigInteger[] qr = b[j][i].multiply(p).subtract(b[k][i].multiply(a)).divideAndRemainder(prev);
                    check(qr[1].signum() == 0, "Bareiss's division is exact");
                    b[j][i] = qr[0];
                    see(b[j][i]);
                }
                b[j][k] = BigInteger.ZERO;
            }
            prev = p;
            if (steps != null) steps.add(biggest.toString().length());
        }
        return b;
    }

    /** Work back up the triangle: the last column gives the last unknown, and so on. */
    static Frac[] backSubstitute(BigInteger[][] b) {
        int n = b.length;
        Frac[] x = new Frac[n];
        for (int k = n - 1; k >= 0; k--) {
            Frac rest = Frac.of(b[k][n], BigInteger.ONE);
            for (int i = k + 1; i < n; i++) rest = rest.minus(x[i].times(b[k][i]));
            x[k] = rest.over(b[k][k]);
        }
        return x;
    }

    // ------------------------------------------------------------------------------------------------------------------
    // Modern elimination by division, in floating point
    // ------------------------------------------------------------------------------------------------------------------
    static double growth;

    /** Gaussian elimination on rows of [A | b], with or without partial pivoting (largest number in the column). */
    static double[] gauss(double[][] A0, double[] b0, boolean pivot) {
        int n = b0.length;
        double[][] A = new double[n][];
        for (int i = 0; i < n; i++) { A[i] = Arrays.copyOf(A0[i], n + 1); A[i][n] = b0[i]; }
        double start = 0, most = 0;
        for (double[] r : A0) for (double v : r) start = Math.max(start, Math.abs(v));
        most = start;
        for (int k = 0; k < n; k++) {
            if (pivot) {
                int best = k;
                for (int i = k + 1; i < n; i++) if (Math.abs(A[i][k]) > Math.abs(A[best][k])) best = i;
                double[] t = A[k]; A[k] = A[best]; A[best] = t;
            }
            for (int i = k + 1; i < n; i++) {
                double f = A[i][k] / A[k][k];
                for (int j = k; j <= n; j++) {
                    A[i][j] -= f * A[k][j];
                    if (j < n) most = Math.max(most, Math.abs(A[i][j]));
                }
            }
        }
        growth = most / start;
        double[] x = new double[n];
        for (int k = n - 1; k >= 0; k--) {
            double s = A[k][n];
            for (int j = k + 1; j < n; j++) s -= A[k][j] * x[j];
            x[k] = s / A[k][k];
        }
        return x;
    }

    /** Multiplications done by elimination by division (multipliers times pivot rows) and by cross-multiplying. */
    static long[] countMults(int n) {
        long division = 0, cross = 0;
        for (int k = 0; k < n; k++)
            for (int j = k + 1; j < n; j++) {
                division += n - k;                         // places below k and the total
                cross += 2L * (n - k);                     // both columns are multiplied
            }
        return new long[]{division, cross};
    }

    static long[][] randomSystem(Random r, int n, int lo, int hi) {
        long[][] c = new long[n][n + 1];
        for (int j = 0; j < n; j++) for (int i = 0; i <= n; i++) c[j][i] = lo + r.nextInt(hi - lo + 1);
        return c;
    }

    public static void main(String[] args) {
        // ---- Problem 1: three grades of grain --------------------------------------------------------------------
        // Right column: 3 bundles of top grade, 2 of medium, 1 of low give 39 dou; middle 2, 3, 1 give 34; left 1, 2, 3 give 26.
        BigInteger[][] p1 = board(new long[][]{{3, 2, 1, 39}, {2, 3, 1, 34}, {1, 2, 3, 26}});
        System.out.printf("p1 board: %s%n", seen(p1));
        List<String> trace = new ArrayList<>();
        biggest = BigInteger.ZERO;
        mults = 0;
        BigInteger[][] t1 = fangcheng(p1, false, trace);
        for (int s = 0; s < trace.size(); s++) System.out.printf("p1 step %d: %s%n", s + 1, trace.get(s));
        System.out.printf("p1 triangle: %s%n", seen(t1));
        // the intermediate columns given for this problem (Lam and Ang's translation, set out by Zhang, Oxford 2020)
        check(col(t1[1]).equals("0 5 1 24"), "middle column after the first step is 0 5 1 24");
        check(trace.get(1).endsWith("-> 0 4 8 39"), "left column after the second step is 0 4 8 39");
        check(col(t1[2]).equals("0 0 36 99"), "left column at the end is 0 0 36 99");
        // the Nine Chapters' way back up: keep every answer over the last column's number (the common divisor, fa)
        BigInteger fa = t1[2][2];
        BigInteger[] shi = new BigInteger[3];
        shi[2] = t1[2][3];
        for (int k = 1; k >= 0; k--) {
            BigInteger s = t1[k][3].multiply(fa);
            for (int i = k + 1; i < 3; i++) s = s.subtract(t1[k][i].multiply(shi[i]));
            BigInteger[] qr = s.divideAndRemainder(t1[k][k]);
            check(qr[1].signum() == 0, "each total divides exactly by its column's number");
            shi[k] = qr[0];
        }
        Frac[] x1 = backSubstitute(t1);
        for (int k = 0; k < 3; k++) check(x1[k].equals(Frac.of(shi[k], fa)), "the common divisor gives the same answers");
        check(x1[0].mixed().equals("9 1/4") && x1[1].mixed().equals("4 1/4") && x1[2].mixed().equals("2 3/4"),
                "the book's answer: 9 1/4, 4 1/4 and 2 3/4 dou");
        System.out.printf("p1 back: divisor %s ; dividends %s %s %s%n", fa, shi[0], shi[1], shi[2]);
        System.out.printf("p1 answer: top %s ; medium %s ; low %s dou ; %d multiplications ; largest number %s%n",
                x1[0].mixed(), x1[1].mixed(), x1[2].mixed(), mults, biggest);

        // ---- Cattle, sheep and pigs: negative numbers ----------------------------------------------------------
        // Sell 2 cattle and 5 sheep, buy 13 pigs: 1000 cash left. Sell 3 cattle and 3 pigs, buy 9 sheep: exactly
        // enough. Sell 6 sheep and 8 pigs, buy 5 cattle: 600 short. Selling is positive, buying and shortfall negative.
        BigInteger[][] p8 = board(new long[][]{{2, 5, -13, 1000}, {3, -9, 3, 0}, {-5, 6, 8, -600}});
        System.out.printf("animals board: %s%n", seen(p8));
        likeSigns = unlikeSigns = noOpponent = 0;
        trace.clear();
        BigInteger[][] t8 = fangcheng(p8, false, trace);
        for (int s = 0; s < trace.size(); s++) System.out.printf("animals step %d: %s%n", s + 1, trace.get(s));
        Frac[] x8 = backSubstitute(t8);
        check(x8[0].mixed().equals("1200") && x8[1].mixed().equals("500") && x8[2].mixed().equals("300"),
                "the book's answer: cattle 1200, sheep 500, pig 300");
        long negatives = 0;
        for (BigInteger[] c : t8) for (BigInteger v : c) if (v.signum() < 0) negatives++;
        System.out.printf("animals answer: cattle %s ; sheep %s ; pig %s ; sign rule: %d like-sign subtractions, %d unlike-sign (added), %d from an empty place ; %d negative numbers left on the board%n",
                x8[0].mixed(), x8[1].mixed(), x8[2].mixed(), likeSigns, unlikeSigns, noOpponent, negatives);
        check(likeSigns + unlikeSigns + noOpponent > 0 && unlikeSigns > 0, "the working needs the rule for unlike signs");

        // ---- How big do the numbers get? -------------------------------------------------------------------------
        Random rnd = new Random(263);                      // Liu Hui's year, as a seed
        int lastPlain = 0;
        for (int n : new int[]{3, 5, 7, 9, 11, 13, 15}) {
            long[][] sys;
            do { sys = randomSystem(rnd, n, -9, 9); } while (bareissDet(board(sys)).signum() == 0);
            BigInteger[][] b = board(sys);
            List<Integer> plainSteps = new ArrayList<>(), bareissSteps = new ArrayList<>();
            biggest = BigInteger.ZERO;
            steps = plainSteps;
            BigInteger[][] plain = fangcheng(b, false, null);
            steps = null;
            int dPlain = biggest.toString().length();
            biggest = BigInteger.ZERO;
            BigInteger[][] reduced = fangcheng(b, true, null);
            int dReduced = biggest.toString().length();
            biggest = BigInteger.ZERO;
            steps = bareissSteps;
            BigInteger[][] br = bareiss(b);
            steps = null;
            int dBareiss = biggest.toString().length();
            if (n == 15) {
                StringJoiner ps = new StringJoiner(" "), bs = new StringJoiner(" ");
                for (int v : plainSteps) ps.add(Integer.toString(v));
                for (int v : bareissSteps) bs.add(Integer.toString(v));
                System.out.printf("steps 15 unknowns plain: %s%n", ps);
                System.out.printf("steps 15 unknowns bareiss: %s%n", bs);
                for (int k = 1; k < bareissSteps.size(); k++) check(bareissSteps.get(k) - bareissSteps.get(k - 1) <= 3, "Bareiss adds only a digit or two per place");
            }
            Frac[] xs = backSubstitute(plain);
            check(Arrays.equals(xs, backSubstitute(reduced)), "cancelling common factors gives the same answer");
            check(Arrays.equals(xs, backSubstitute(br)), "Bareiss gives the same answer");
            int dAnswer = 0;
            for (Frac f : xs) dAnswer = Math.max(dAnswer, Math.max(f.num().abs().toString().length(), f.den().toString().length()));
            check(dReduced <= dPlain && dBareiss <= dPlain, "cross-multiplying without cancelling makes the biggest numbers");
            if (n > 3) check(dPlain > lastPlain, "plain cross-multiplication grows with every unknown");
            lastPlain = dPlain;
            System.out.printf("growth %d unknowns: plain %d digits ; common factors cancelled %d digits ; Bareiss %d digits ; answer %d digits%n",
                    n, dPlain, dReduced, dBareiss, dAnswer);
        }

        // ---- Counting the work ------------------------------------------------------------------------------------
        check(countMults(3)[1] == 16, "the counter agrees with the board: 16 multiplications for Problem 1");
        for (int n : new int[]{3, 6, 18, 100, 1000}) {
            long[] m = countMults(n);
            check(m[0] == ((long) n * n * n - n) / 3, "elimination by division: (n^3 - n) / 3 multiplications");
            check(m[1] == 2 * m[0], "cross-multiplying doubles them");
            System.out.printf("work %d unknowns: by division %d multiplications ; cross-multiplying %d ; n^3/3 = %.0f%n",
                    n, m[0], m[1], n * (double) n * n / 3);
        }

        // ---- What machines added: rounding --------------------------------------------------------------------------
        double eps = 1e-20;
        double[][] tiny = {{eps, 1}, {1, 1}};
        double[] tb = {1, 2};
        double[] noPiv = gauss(tiny, tb, false);
        double[] piv = gauss(tiny, tb, true);
        // exactly, x = 1 / (1 - 10^-20) = 10^20 / (10^20 - 1)
        BigInteger e20 = BigInteger.TEN.pow(20);
        Frac xExact = Frac.of(e20, e20.subtract(BigInteger.ONE));
        check(noPiv[0] == 0.0 && noPiv[1] == 1.0, "without pivoting, a pivot of 10^-20 loses x completely");
        check(piv[0] == 1.0 && piv[1] == 1.0, "partial pivoting gets both right to double precision");
        System.out.printf("tiny pivot: without pivoting x = %s, y = %s ; with partial pivoting x = %s, y = %s ; exactly x = %s/%s%n",
                noPiv[0], noPiv[1], piv[0], piv[1], xExact.num(), xExact.den());

        Random r2 = new Random(1948);                      // the year of Turing's paper, as a seed
        // the worst case for partial pivoting: 1 on the diagonal, -1 below it, 1 in the last column
        for (int n : new int[]{20, 40, 60}) {
            double[][] W = new double[n][n];
            double[][] R = new double[n][n];
            double[] xt = new double[n];
            for (int i = 0; i < n; i++) {
                xt[i] = r2.nextDouble();
                for (int j = 0; j < n; j++) {
                    W[i][j] = i == j || j == n - 1 ? 1 : (j < i ? -1 : 0);
                    R[i][j] = 2 * r2.nextDouble() - 1;
                }
            }
            double[] wb = mul(W, xt), rb = mul(R, xt);
            double[] wx = gauss(W, wb, true);
            double gW = growth;
            double[] rx = gauss(R, rb, true);
            double gR = growth;
            check(gW == Math.pow(2, n - 1), "the worst case: growth exactly 2^(n-1)");
            check(gR < 50, "a random matrix: small growth");
            System.out.printf("worst case %d: growth 2^%d, error %.1e ; random matrix growth %.1f, error %.1e%n",
                    n, Math.getExponent(gW), err(wx, xt), gR, err(rx, xt));
        }
        System.out.printf("FangCheng: %d checks passed%n", passed);
    }

    static BigInteger bareissDet(BigInteger[][] b) {
        BigInteger keep = biggest == null ? BigInteger.ZERO : biggest;
        biggest = BigInteger.ZERO;
        BigInteger[][] t = bareiss(b);
        biggest = keep;
        return t == null ? BigInteger.ZERO : t[b.length - 1][b.length - 1];
    }

    static double[] mul(double[][] A, double[] x) {
        double[] y = new double[x.length];
        for (int i = 0; i < x.length; i++) for (int j = 0; j < x.length; j++) y[i] += A[i][j] * x[j];
        return y;
    }

    /** The largest error in any unknown, relative to the largest unknown. */
    static double err(double[] x, double[] truth) {
        double e = 0, m = 0;
        for (int i = 0; i < x.length; i++) { e = Math.max(e, Math.abs(x[i] - truth[i])); m = Math.max(m, Math.abs(truth[i])); }
        return e / m;
    }
}
