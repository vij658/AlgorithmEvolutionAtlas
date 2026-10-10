import java.math.BigInteger;
import java.util.*;

/**
 * Era 1, topic 7: Euclid's algorithm (Elements, Book VII, Propositions 1-2, c. 300 BCE).
 *
 * HOW IT WORKS
 *   To find the greatest common divisor of a and b, replace the pair (a, b) by (b, a mod b) until the second number
 *   is 0; the first number is then the answer. Euclid did it by repeated subtraction ("the less is continually
 *   subtracted in turn from the greater"); one division does a whole run of those subtractions at once. Drawn as a
 *   picture: cut the biggest possible squares off an a-by-b rectangle, again and again; the side of the last square
 *   is the gcd, and the number of squares cut at each stage (the quotients) is the continued fraction of a/b.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The four ways to find a gcd that the book compares: trying every candidate, repeated subtraction (Euclid's
 *      own form), division (the modern form) and Stein's binary GCD (shifts and subtraction only).
 *   2. The extended algorithm (Aryabhata's "pulverizer"), which also finds x, y with a*x + b*y = gcd(a, b), and the
 *      modular inverse that RSA key generation uses.
 *   3. Checks: every method agrees with BigInteger.gcd on hundreds of thousands of random pairs; Bezout's identity
 *      holds; Lame's bound (steps <= 5 x digits of the smaller number) holds; consecutive Fibonacci numbers are the
 *      worst case. Random inputs use fixed seeds, so every run prints the same numbers.
 *   4. The measurements behind the book's tables and charts (each printed line starts with a tag the figure script
 *      reads): the worked example 1071 and 462, a comparison of the four methods, worst cases by number of digits,
 *      average steps by number of digits, and the distribution of steps for random 18-digit pairs.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java EuclidsAlgorithm.java
 *   Expected output: expected-output.txt in this folder.
 */
public class EuclidsAlgorithm {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The four ways to find a gcd
    // ----------------------------------------------------------------------------------------------------

    /** Before Euclid: try every candidate from the smaller number down. Returns {gcd, candidates tried}. */
    static long[] gcdByTrying(long a, long b) {
        long tries = 0;
        for (long d = Math.min(a, b); d >= 1; d--) {
            tries++;
            if (a % d == 0 && b % d == 0) return new long[]{d, tries};
        }
        return new long[]{Math.max(a, b), tries};          // one of them is 0
    }

    /** Euclid's own form: take the smaller from the larger until one of them is 0. Returns {gcd, subtractions}. */
    static long[] gcdBySubtraction(long a, long b) {
        long subtractions = 0;
        while (a != 0 && b != 0) {
            if (a >= b) a -= b; else b -= a;
            subtractions++;
        }
        return new long[]{a + b, subtractions};
    }

    /** The modern form: one division does a whole run of subtractions. */
    static long gcd(long a, long b) {
        while (b != 0) {
            long r = a % b;                                // what is left after taking b away as often as possible
            a = b;
            b = r;
        }
        return a;
    }

    /** Number of divisions the modern form makes. */
    static int divisionSteps(long a, long b) {
        int steps = 0;
        while (b != 0) {
            long r = a % b;
            a = b;
            b = r;
            steps++;
        }
        return steps;
    }

    /** Stein's binary GCD (published 1967): halving and subtraction only. Returns {gcd, loop iterations}. */
    static long[] binaryGcd(long a, long b) {
        if (a == 0) return new long[]{b, 0};
        if (b == 0) return new long[]{a, 0};
        int shift = Long.numberOfTrailingZeros(a | b);    // the power of 2 both share
        a >>= Long.numberOfTrailingZeros(a);
        long iterations = 0;
        while (b != 0) {
            b >>= Long.numberOfTrailingZeros(b);           // halve away every factor of 2: it cannot be in the gcd now
            if (a > b) { long t = a; a = b; b = t; }
            b -= a;                                        // both odd, so the difference is even
            iterations++;
        }
        return new long[]{a << shift, iterations};
    }

    // ----------------------------------------------------------------------------------------------------
    // The extended algorithm: the pulverizer
    // ----------------------------------------------------------------------------------------------------

    /** Rows of the extended algorithm: {quotient, remainder, s, t} with remainder = s*a + t*b on every row. */
    static List<long[]> extendedRows(long a, long b) {
        List<long[]> rows = new ArrayList<>();
        long r0 = a, r1 = b, s0 = 1, s1 = 0, t0 = 0, t1 = 1;
        rows.add(new long[]{0, r0, s0, t0});
        rows.add(new long[]{0, r1, s1, t1});
        while (r1 != 0) {
            long q = r0 / r1;
            long r2 = r0 - q * r1, s2 = s0 - q * s1, t2 = t0 - q * t1;
            rows.add(new long[]{q, r2, s2, t2});
            r0 = r1; r1 = r2; s0 = s1; s1 = s2; t0 = t1; t1 = t2;
        }
        return rows;
    }

    /** {g, x, y} with a*x + b*y = g. */
    static long[] extendedGcd(long a, long b) {
        List<long[]> rows = extendedRows(a, b);
        long[] last = rows.get(rows.size() - 2);           // the last non-zero remainder
        return new long[]{last[1], last[2], last[3]};
    }

    /** The inverse of a modulo m, when gcd(a, m) = 1: how RSA turns e into the private exponent d. */
    static long modInverse(long a, long m) {
        long[] g = extendedGcd(m, a % m);
        if (g[0] != 1) throw new ArithmeticException("no inverse: gcd is " + g[0]);
        return Math.floorMod(g[2], m);
    }

    /** The quotients of the division form: the continued fraction of a/b, and the number of squares cut at each stage. */
    static List<Long> quotients(long a, long b) {
        List<Long> q = new ArrayList<>();
        while (b != 0) {
            q.add(a / b);
            long r = a % b;
            a = b;
            b = r;
        }
        return q;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers for the checks and measurements
    // ----------------------------------------------------------------------------------------------------

    static int digits(long x) { return Long.toString(x).length(); }

    static long[] fibonacci(int n) {
        long[] f = new long[n + 1];
        f[1] = 1;
        for (int i = 2; i <= n; i++) f[i] = f[i - 1] + f[i - 2];
        return f;
    }

    static long randomBelow(Random rnd, long bound) { return rnd.nextLong(1, bound); }      // uniform in [1, bound)

    static String join(List<Long> xs) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < xs.size(); i++) sb.append(i == 0 ? "" : i == 1 ? "; " : ", ").append(xs.get(i));
        return "[" + sb + "]";
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks and measurements
    // ----------------------------------------------------------------------------------------------------

    public static void main(String[] args) {
        Random rnd = new Random(300);                      // c. 300 BCE

        // --- the worked example, 1071 and 462; the small one the reader tries first, 48 and 18;
        //     and the slowest pair below 100, 89 and 55 (consecutive Fibonacci numbers)
        long A = 1071, B = 462;
        for (long[] p : new long[][]{{A, B}, {48, 18}, {89, 55}}) {
            long a = p[0], b = p[1];
            while (b != 0) {
                long q = a / b, r = a % b;
                System.out.println("trace " + p[0] + " " + p[1] + ": " + a + " = " + q + " x " + b + " + " + r);
                a = b;
                b = r;
            }
        }
        check(gcd(48, 18) == 6 && divisionSteps(48, 18) == 3, "gcd(48, 18) = 6 in 3 divisions");
        check(gcd(A, B) == 21, "gcd(1071, 462) = 21");
        check(quotients(A, B).equals(List.of(2L, 3L, 7L)), "1071/462 = [2; 3, 7]");
        System.out.println("quotients " + A + "/" + B + " = " + join(quotients(A, B)) + " (squares cut at each stage)");
        for (long[] row : extendedRows(A, B))
            System.out.println("extended " + A + " " + B + ": q=" + row[0] + " r=" + row[1] + " s=" + row[2] + " t=" + row[3]);
        long[] ext = extendedGcd(A, B);
        check(ext[0] == 21 && A * ext[1] + B * ext[2] == 21, "Bezout for 1071, 462");
        System.out.println("bezout " + A + " " + B + ": " + ext[0] + " = " + ext[1] + " x " + A + " + " + ext[2] + " x " + B);

        // --- the four methods side by side
        long[] fib = fibonacci(92);
        long[][] pairs = {{1071, 462}, {89, 55}, {1_000_000, 1}, {fib[47], fib[46]},
                          {randomBelow(rnd, 1_000_000_000_000_000_000L), randomBelow(rnd, 1_000_000_000_000_000_000L)}};
        for (long[] p : pairs) {
            long x = Math.max(p[0], p[1]), y = Math.min(p[0], p[1]);
            long g = gcd(x, y);
            long tries = Math.min(x, y) <= 10_000_000 ? gcdByTrying(x, y)[1] : y - g + 1;   // counted exactly either way
            long subtractions = 0;
            for (long q : quotients(x, y)) subtractions += q;                                // each quotient is a run of subtractions
            if (Math.min(x, y) <= 10_000_000) check(gcdBySubtraction(x, y)[1] == subtractions, "subtraction count");
            long[] bin = binaryGcd(x, y);
            check(bin[0] == g, "binary gcd agrees");
            System.out.println("compare " + x + " " + y + ": gcd=" + g + " trying=" + tries + " subtracting=" + subtractions
                    + " dividing=" + divisionSteps(x, y) + " binary=" + bin[1]);
        }

        // --- every method agrees with BigInteger
        for (int i = 0; i < 200_000; i++) {
            long x = randomBelow(rnd, 1L << (1 + rnd.nextInt(62))), y = randomBelow(rnd, 1L << (1 + rnd.nextInt(62)));
            long g = BigInteger.valueOf(x).gcd(BigInteger.valueOf(y)).longValue();
            check(gcd(x, y) == g, "division form vs BigInteger");
            check(binaryGcd(x, y)[0] == g, "binary form vs BigInteger");
            long[] e = extendedGcd(x, y);
            check(e[0] == g && BigInteger.valueOf(x).multiply(BigInteger.valueOf(e[1]))
                    .add(BigInteger.valueOf(y).multiply(BigInteger.valueOf(e[2]))).equals(BigInteger.valueOf(g)), "Bezout identity");
            check(divisionSteps(x, y) <= 5 * digits(Math.min(x, y)) + 1, "Lame bound (plus the first step when x < y)");
        }
        for (int i = 0; i < 20_000; i++) {
            long x = randomBelow(rnd, 5_000), y = randomBelow(rnd, 5_000);
            long g = gcd(x, y);
            check(gcdByTrying(x, y)[0] == g && gcdBySubtraction(x, y)[0] == g, "trying and subtracting agree");
        }
        check(gcd(0, 5) == 5 && gcd(5, 0) == 5 && gcd(0, 0) == 0, "zero inputs");

        // --- the continued fraction rebuilds the fraction exactly
        for (int i = 0; i < 20_000; i++) {
            long x = randomBelow(rnd, 1_000_000_000L), y = randomBelow(rnd, 1_000_000_000L);
            List<Long> q = quotients(x, y);
            BigInteger num = BigInteger.ONE, den = BigInteger.ZERO;   // evaluate [q0; q1, ...] from the back
            for (int k = q.size() - 1; k >= 0; k--) {
                BigInteger t = num;
                num = BigInteger.valueOf(q.get(k)).multiply(num).add(den);
                den = t;
            }
            long g = gcd(x, y);
            check(num.equals(BigInteger.valueOf(x / g)) && den.equals(BigInteger.valueOf(y / g)), "continued fraction is exact");
        }

        // --- worst cases: consecutive Fibonacci numbers, against Lame's bound
        for (int n = 1; n <= 89; n++) check(divisionSteps(fib[n + 2], fib[n + 1]) == n, "Fibonacci pair F(n+2), F(n+1) takes n steps");
        int[] limits = {100, 1000};
        for (int limit : limits) {
            int best = -1; long bx = 0, by = 0;
            for (long x = 1; x < limit; x++)
                for (long y = 1; y <= x; y++) {
                    int s = divisionSteps(x, y);
                    check(s <= 5 * digits(y), "Lame bound, exhaustive");
                    if (s > best) { best = s; bx = x; by = y; }
                }
            System.out.println("exhaustive below " + limit + ": most steps " + best + " at (" + bx + ", " + by + ")");
        }
        check(divisionSteps(89, 55) == 9 && divisionSteps(987, 610) == 14, "Fibonacci pairs below 100 and 1000");
        for (int d = 1; d <= 18; d++) {
            int k = 2;
            while (digits(fib[k + 1]) <= d) k++;            // fib[k] is the largest Fibonacci number with at most d digits
            long y = fib[k], x = fib[k + 1];
            int s = divisionSteps(x, y);
            check(s <= 5 * d, "Lame bound at the worst case");
            System.out.println("worst digits=" + d + ": (" + x + ", " + y + ") steps=" + s + " lame=" + (5 * d));
        }

        // --- the average case, by number of digits
        double[] mean = new double[19];
        int samples = 100_000;
        for (int d = 1; d <= 18; d++) {
            long bound = 1;
            for (int i = 0; i < d; i++) bound *= 10;
            long total = 0;
            for (int i = 0; i < samples; i++) total += divisionSteps(randomBelow(rnd, bound), randomBelow(rnd, bound));
            mean[d] = (double) total / samples;
            System.out.printf("average digits=%d: %.3f steps over %d random pairs%n", d, mean[d], samples);
        }
        double sx = 0, sy = 0, sxx = 0, sxy = 0;
        int m = 0;
        for (int d = 6; d <= 18; d++) { sx += d; sy += mean[d]; sxx += d * d; sxy += d * mean[d]; m++; }
        double slope = (m * sxy - sx * sy) / (m * sxx - sx * sx);
        double predicted = 12 * Math.log(2) / (Math.PI * Math.PI) * Math.log(10);
        check(Math.abs(slope - predicted) < 0.05, "average grows like Heilbronn's 0.843 ln n");
        System.out.printf("slope: %.3f more steps per extra digit (measured, 6 to 18 digits); Heilbronn's 12 ln2 / pi^2 x ln 10 = %.3f%n", slope, predicted);

        // --- how the steps are spread for random 18-digit pairs
        int[] hist = new int[100];
        int lo = 99, hi = 0;
        for (int i = 0; i < samples; i++) {
            long x = rnd.nextLong(100_000_000_000_000_000L, 1_000_000_000_000_000_000L);
            long y = rnd.nextLong(100_000_000_000_000_000L, 1_000_000_000_000_000_000L);
            int s = divisionSteps(Math.max(x, y), Math.min(x, y));
            check(s <= 5 * 18, "Lame bound for 18 digits");
            hist[s]++;
            lo = Math.min(lo, s);
            hi = Math.max(hi, s);
        }
        StringBuilder h = new StringBuilder("histogram 18 digits (" + samples + " random pairs):");
        for (int s = lo; s <= hi; s++) h.append(" ").append(s).append(":").append(hist[s]);
        System.out.println(h);

        // --- RSA: the private exponent is a modular inverse, found by the extended algorithm
        check(modInverse(17, 3120) == 2753 && (17L * 2753) % 3120 == 1, "RSA toy example: 17 x 2753 = 1 mod 3120");
        boolean threw = false;
        try { modInverse(6, 9); } catch (ArithmeticException e) { threw = true; }
        check(threw, "no inverse when the gcd is not 1");
        System.out.println("rsa: e=17, phi=3120, d=" + modInverse(17, 3120) + " (17 x 2753 = " + (17L * 2753) + " = 15 x 3120 + 1)");

        System.out.println("EuclidsAlgorithm: " + passed + " checks passed");
    }
}
