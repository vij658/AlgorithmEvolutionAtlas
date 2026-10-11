import java.math.BigInteger;
import java.util.*;

/**
 * Era 2, topic 8: Fibonacci's Liber abaci (Leonardo of Pisa, 1202; second edition 1228).
 *
 * HOW IT WORKS
 *   "These are the nine figures of the Indians: 9 8 7 6 5 4 3 2 1." With them and a zero, any number is written in a
 *   few figures, and every operation becomes a written procedure whose working stays on the page for anyone to check.
 *   The book teaches the four operations and fractions (chapters 2-7), then merchants' problems: prices, barter,
 *   partnerships and money changing (8-11), many posed problems including the rabbits (12), and double false position,
 *   the method "elchataym" (13): try two guesses, see how far each misses, and combine them to hit the answer.
 *   The rabbits: a newborn pair can breed at one month old, gives birth a month later, and so on; each month's count is
 *   the sum of the two before it, F(n) = F(n-1) + F(n-2).
 *
 * WHAT THIS PROGRAM DOES
 *   1. Compares the length of Roman and Hindu-Arabic numerals from 1 to 3999, and writes out a merchant's
 *      multiplication with its partial products, the working that Roman numerals do not leave.
 *   2. Breeds the rabbits month by month as individual pairs, and checks the count against the recurrence.
 *   3. Computes Fibonacci numbers four ways: plain recursion (counting the calls), a loop, fast doubling, and Binet's
 *      formula in floating point (finding where it first goes wrong).
 *   4. Shows that consecutive Fibonacci numbers are the worst case of Euclid's algorithm (Lame, 1844).
 *   5. Solves linear problems by double false position, and shows it is only approximate for curved ones.
 *   6. Full circle: the Fibonacci lemma behind Fibonacci heaps (Fredman and Tarjan, 1987).
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LiberAbaci.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LiberAbaci {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static String roman(int n) {
        int[] v = {1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1};
        String[] s = {"M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"};
        StringBuilder b = new StringBuilder();
        for (int i = 0; i < v.length; i++) while (n >= v[i]) { b.append(s[i]); n -= v[i]; }
        return b.toString();
    }

    static int fromRoman(String r) {
        Map<Character, Integer> m = Map.of('I', 1, 'V', 5, 'X', 10, 'L', 50, 'C', 100, 'D', 500, 'M', 1000);
        int total = 0;
        for (int i = 0; i < r.length(); i++) {
            int a = m.get(r.charAt(i)), b = i + 1 < r.length() ? m.get(r.charAt(i + 1)) : 0;
            total += a < b ? -a : a;
        }
        return total;
    }

    static long calls;

    static long naive(int n) { calls++; return n < 2 ? n : naive(n - 1) + naive(n - 2); }

    static int doublingSteps;

    /** Fast doubling: F(2k) = F(k)(2F(k+1) - F(k)), F(2k+1) = F(k)^2 + F(k+1)^2. Returns {F(n), F(n+1)}. */
    static BigInteger[] doubling(int n) {
        if (n == 0) return new BigInteger[]{BigInteger.ZERO, BigInteger.ONE};
        BigInteger[] h = doubling(n / 2);
        doublingSteps++;
        BigInteger a = h[0], b = h[1];
        BigInteger c = a.multiply(b.shiftLeft(1).subtract(a)), d = a.multiply(a).add(b.multiply(b));
        return n % 2 == 0 ? new BigInteger[]{c, d} : new BigInteger[]{d, c.add(d)};
    }

    static int euclidSteps(long a, long b) {
        int s = 0;
        while (b != 0) { long r = a % b; a = b; b = r; s++; }
        return s;
    }

    public static void main(String[] args) {
        // ---- Roman against Indian figures ---------------------------------------------------------------------------
        long romanTotal = 0, digitTotal = 0;
        int longest = 0, longestAt = 0;
        for (int n = 1; n <= 3999; n++) {
            String r = roman(n);
            check(fromRoman(r) == n, "Roman numerals read back");
            romanTotal += r.length();
            digitTotal += Integer.toString(n).length();
            if (r.length() > longest) { longest = r.length(); longestAt = n; }
        }
        System.out.printf("numerals: 1 to 3999 ; Roman %.2f symbols on average, longest %d (%d = %s) ; Indian figures %.2f on average, at most 4%n",
                romanTotal / 3999.0, longest, longestAt, roman(longestAt), digitTotal / 3999.0);
        // a merchant's multiplication, with the working left on the page
        long a = 1202, b = 1228;
        StringJoiner partial = new StringJoiner(" ; ");
        long sum = 0;
        int products = 0;
        String bs = Long.toString(b);
        for (int i = bs.length() - 1, shift = 0; i >= 0; i--, shift++) {
            long dgt = bs.charAt(i) - '0';
            long p = a * dgt;
            products += Long.toString(a).length();
            partial.add(a + " x " + dgt + (shift > 0 ? " x " + (long) Math.pow(10, shift) : "") + " = " + p * (long) Math.pow(10, shift));
            sum += p * (long) Math.pow(10, shift);
        }
        check(sum == a * b, "the partial products add up");
        System.out.printf("multiply: %d x %d (%s x %s) ; partial products %s ; total %d (%s) ; %d digit products%n",
                a, b, roman((int) a), roman((int) b), partial, sum, sum < 4000 ? roman((int) sum) : "too big for standard Roman numerals", products);

        // ---- the rabbits, pair by pair ------------------------------------------------------------------------------
        // each pair is an age in months; a pair aged 2 or more gives birth to a newborn pair every month
        List<Integer> pairs = new ArrayList<>(List.of(0));   // one newborn pair
        StringJoiner months = new StringJoiner(" ");
        long[] fib = new long[100];
        fib[1] = 1; fib[2] = 1;
        for (int i = 3; i < 100; i++) fib[i] = fib[i - 1] + fib[i - 2];
        for (int m = 1; m <= 12; m++) {
            List<Integer> next = new ArrayList<>();
            for (int age : pairs) { next.add(age + 1); if (age + 1 >= 2) next.add(0); }
            pairs = next;
            months.add(Integer.toString(pairs.size()));
            check(pairs.size() == fib[m + 1], "month " + m + ": the recurrence");
        }
        check(months.toString().split(" ")[3].equals("5"), "five pairs at the end of the fourth month");
        System.out.printf("rabbits: pairs at the end of months 1 to 12: %s%n", months);

        // ---- four ways to compute Fibonacci numbers --------------------------------------------------------------------
        StringJoiner nc = new StringJoiner(" ; ");
        for (int n : new int[]{10, 20, 30, 35}) {
            calls = 0;
            long f = naive(n);
            check(f == fib[n] && calls == 2 * fib[n + 1] - 1, "plain recursion makes 2F(n+1) - 1 calls");
            nc.add("F(" + n + ") = " + f + " in " + calls + " calls");
        }
        System.out.printf("recursion: %s%n", nc);
        doublingSteps = 0;
        BigInteger f1000 = doubling(1000)[0];
        int steps1000 = doublingSteps;
        BigInteger x = BigInteger.ZERO, y = BigInteger.ONE;
        for (int i = 0; i < 1000; i++) { BigInteger t = x.add(y); x = y; y = t; }
        check(x.equals(f1000), "the loop and fast doubling agree on F(1000)");
        doublingSteps = 0;
        BigInteger fm = doubling(1_000_000)[0];
        System.out.printf("fast: F(1000) has %d digits: loop 1000 additions, fast doubling %d steps ; F(1000000) has %d digits, in %d doubling steps%n",
                f1000.toString().length(), steps1000, fm.toString().length(), doublingSteps);
        double phi = (1 + Math.sqrt(5)) / 2;
        int firstWrong = -1;
        BigInteger p0 = BigInteger.ZERO, p1 = BigInteger.ONE;
        for (int n = 0; n <= 90; n++) {
            long binet = Math.round(Math.pow(phi, n) / Math.sqrt(5));
            if (firstWrong < 0 && BigInteger.valueOf(binet).compareTo(p0) != 0) firstWrong = n;
            BigInteger t = p0.add(p1); p0 = p1; p1 = t;
        }
        check(firstWrong > 60, "Binet's formula holds in doubles for the first sixty or so");
        System.out.printf("binet: rounding phi^n / sqrt 5 in double precision gives F(n) exactly up to n = %d, and first goes wrong at n = %d%n",
                firstWrong - 1, firstWrong);

        // ---- Lame: Fibonacci pairs are the worst case for Euclid -------------------------------------------------------
        int[] firstNeeding = new int[40];
        Arrays.fill(firstNeeding, -1);
        for (int aa = 2; aa <= 2000; aa++) for (int bb = 1; bb < aa; bb++) {      // smallest a first, then smallest b
            int s = euclidSteps(aa, bb);
            if (firstNeeding[s] < 0) firstNeeding[s] = aa * 10000 + bb;
        }
        StringJoiner worst = new StringJoiner(" ; ");
        for (int s = 1; s <= 14; s++) {
            int aa = firstNeeding[s] / 10000, bb = firstNeeding[s] % 10000;
            check(aa == fib[s + 2] && bb == fib[s + 1], "the smallest pair needing " + s + " steps is a Fibonacci pair");
            if (s % 3 == 1 || s == 14) worst.add(s + " steps: " + aa + ", " + bb);
        }
        System.out.printf("lame: for a > b, the smallest pair that needs k division steps is (F(k+2), F(k+1)) ; %s%n", worst);

        // ---- double false position (elchataym) ------------------------------------------------------------------------
        // a problem f(x) = target with f linear: guess g1, g2; errors e1, e2; answer (g1 e2 - g2 e1) / (e2 - e1)
        Random r = new Random(1202);
        int exact = 0;
        for (int t = 0; t < 10_000; t++) {
            double m = 1 + r.nextInt(50), c = r.nextInt(100), target = r.nextInt(10_000);
            double g1 = r.nextInt(100), g2 = g1 + 1 + r.nextInt(100);
            double e1 = m * g1 + c - target, e2 = m * g2 + c - target;
            double xs = (g1 * e2 - g2 * e1) / (e2 - e1);
            check(Math.abs(m * xs + c - target) < 1e-6, "double false position is exact for linear problems");
            exact++;
        }
        // one worked example: a price problem; then a curved one, x^2 = 2, where two guesses only approximate
        double g1 = 1, g2 = 2, e1 = g1 * g1 - 2, e2 = g2 * g2 - 2;
        double once = (g1 * e2 - g2 * e1) / (e2 - e1);
        double lo = 1, hi = 2;
        int iters = 0;
        double xm = once;
        while (Math.abs(xm * xm - 2) > 1e-12) {           // repeat the method: regula falsi
            double el = lo * lo - 2, eh = hi * hi - 2;
            xm = (lo * eh - hi * el) / (eh - el);
            if (xm * xm < 2) lo = xm; else hi = xm;
            iters++;
        }
        System.out.printf("false position: %d random linear problems solved exactly from two guesses ; for x^2 = 2, guesses 1 and 2 give %.6f ; repeated, %d rounds reach %.12f%n",
                exact, once, iters, xm);

        // ---- full circle: the Fibonacci lemma of Fibonacci heaps -------------------------------------------------------
        // the smallest tree of rank k: a root whose children have ranks at least 0, 0, 1, ..., k-2
        long[] s = new long[60];
        s[0] = 1; s[1] = 2;
        for (int k = 2; k < 60; k++) { s[k] = 2; for (int i = 0; i <= k - 2; i++) s[k] += s[i]; }
        for (int k = 0; k < 60 && k + 2 < 92; k++) check(s[k] == fib[k + 2], "smallest rank-k tree has F(k+2) nodes");
        int maxRank = 0;
        while (s[maxRank + 1] <= 1_000_000) maxRank++;
        System.out.printf("heap: the smallest tree of rank k in a Fibonacci heap has F(k+2) nodes (checked for k up to 59) ; so a heap of a million items has rank at most %d ; log_phi(10^6) = %.1f%n",
                maxRank, Math.log(1e6) / Math.log(phi));

        System.out.printf("LiberAbaci: %d checks passed%n", passed);
    }
}
