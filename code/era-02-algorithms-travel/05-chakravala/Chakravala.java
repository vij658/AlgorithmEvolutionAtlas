import java.math.BigInteger;
import java.util.*;

/**
 * Era 2, topic 5: the chakravala and "Pell's" equation (Brahmagupta, 628; Jayadeva, quoted 1073; Bhaskara II, 1150).
 *
 * HOW IT WORKS
 *   Find whole numbers with a^2 - N b^2 = 1. (The Indian texts write N x^2 + 1 = y^2.) Guessing fails because the
 *   smallest answer can be enormous: for N = 61, b = 226,153,980.
 *   Composition (Brahmagupta's bhavana): if a^2 - N b^2 = k and c^2 - N d^2 = l, then
 *     (ac + Nbd)^2 - N (ad + bc)^2 = kl,
 *   so two near-misses multiply into a new one. Composing a near-miss with itself and dividing by k makes an exact
 *   answer, in fractions, and when k is 1, 2 or 4 (either sign) a few more compositions make it whole.
 *   The chakravala ("cyclic") method makes this work for every N: from a triple (a, b, k), choose m so that k divides
 *   a + b m and m^2 - N is as small as possible; compose with (m, 1, m^2 - N) and divide by k:
 *     a' = (a m + N b) / |k|,   b' = (a + b m) / |k|,   k' = (m^2 - N) / k.
 *   Repeat until k = 1. The cycle always ends, though the proof came in Europe, with Lagrange's theory (1766-1767).
 *
 * WHAT THIS PROGRAM DOES
 *   1. Checks Brahmagupta's composition identity on random triples.
 *   2. Solves Brahmagupta's N = 92 in two compositions.
 *   3. Runs the chakravala step by step for Bhaskara II's N = 61 and N = 67, and the short route for 61: one step to
 *      k = -4, then Brahmagupta's finish.
 *   4. For every N up to 1000 that is not a square, compares the chakravala with Lagrange's continued fractions (steps
 *      to the smallest answer) and checks that both find the same answer.
 *   5. Measures how big the smallest answers get, and how long a plain search would take.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Chakravala.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Chakravala {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static BigInteger big(long v) { return BigInteger.valueOf(v); }

    // ---- exact fractions, for Brahmagupta's compositions ---------------------------------------------------------------
    record Q(BigInteger n, BigInteger d) {
        static Q of(BigInteger n, BigInteger d) {
            if (d.signum() < 0) { n = n.negate(); d = d.negate(); }
            BigInteger g = n.gcd(d);
            return new Q(n.divide(g), d.divide(g));
        }
        static Q of(long n) { return new Q(big(n), BigInteger.ONE); }
        Q plus(Q o) { return of(n.multiply(o.d).add(o.n.multiply(d)), d.multiply(o.d)); }
        Q times(Q o) { return of(n.multiply(o.n), d.multiply(o.d)); }
        Q times(long k) { return of(n.multiply(big(k)), d); }
        Q over(long k) { return of(n, d.multiply(big(k))); }
        boolean whole() { return d.equals(BigInteger.ONE); }
        public String toString() { return whole() ? n.toString() : n + "/" + d; }
    }

    /** A triple a, b, k with a^2 - N b^2 = k, in fractions. */
    record T(Q a, Q b, Q k) {
        public String toString() { return "(" + a + ", " + b + ", " + k + ")"; }
        boolean whole() { return a.whole() && b.whole() && k.whole(); }
    }

    /** Brahmagupta's composition: (a, b, k) with (c, d, l) gives (ac + Nbd, ad + bc, kl). */
    static T compose(T x, T y, long N) {
        return new T(x.a.times(y.a).plus(x.b.times(y.b).times(N)), x.a.times(y.b).plus(x.b.times(y.a)), x.k.times(y.k));
    }

    static boolean holds(T t, long N) { return t.a.times(t.a).plus(t.b.times(t.b).times(-N)).equals(t.k); }

    static long chakSteps;
    static List<String> trace;

    /** The chakravala, from the nearest square, until k = 1. Returns {a, b}. */
    static BigInteger[] chakravala(long N) { return chakravala(N, false); }

    static BigInteger[] stopTriple;                      // where the early stop happened: {a, b, k}

    /** With early = true, stop as soon as k is 1, 2 or 4 (either sign) and finish with Brahmagupta's compositions. */
    static BigInteger[] chakravala(long N, boolean early) {
        long r = (long) Math.sqrt((double) N);
        while (r * r > N) r--;
        while ((r + 1) * (r + 1) <= N) r++;
        long a0 = (N - r * r < (r + 1) * (r + 1) - N) ? r : r + 1;   // the nearest square
        BigInteger a = big(a0), b = BigInteger.ONE, k = big(a0 * a0 - N), n = big(N);
        chakSteps = 0;
        if (trace != null) trace.add(String.format("start %s %s %s", a, b, k));
        while (!k.equals(BigInteger.ONE)) {
            long kk = k.abs().longValueExact();
            if (early && (kk == 1 || kk == 2 || kk == 4)) { stopTriple = new BigInteger[]{a, b, k}; return finish(a, b, k, N); }
            // m with |k| dividing a + b m, and m^2 - N as small as possible
            long best = -1;
            BigInteger bestGap = null;
            long lo = Math.max(1, r - 2 * kk), hi = r + 2 * kk + 1;
            for (long m = lo; m <= hi; m++) {
                if (a.add(b.multiply(big(m))).mod(big(kk)).signum() != 0) continue;
                BigInteger gap = big(m * m - N).abs();
                if (bestGap == null || gap.compareTo(bestGap) < 0) { best = m; bestGap = gap; }
            }
            BigInteger m = big(best), K = k.abs();
            BigInteger na = a.multiply(m).add(n.multiply(b)).divide(K);
            BigInteger nb = a.add(b.multiply(m)).divide(K);
            BigInteger nk = m.multiply(m).subtract(n).divide(k);
            a = na; b = nb; k = nk;
            chakSteps++;
            check(a.multiply(a).subtract(n.multiply(b).multiply(b)).equals(k), "every chakravala triple is a near-miss");
            if (trace != null) trace.add(String.format("m %d -> %s %s %s", best, a, b, k));
        }
        stopTriple = new BigInteger[]{a, b, k};
        return new BigInteger[]{a, b};
    }

    static long compositions;

    /** Brahmagupta's finish from a^2 - N b^2 = k with k = -1, 2, -2, 4 or -4: compose until whole with k = 1. */
    static BigInteger[] finish(BigInteger a, BigInteger b, BigInteger k, long N) {
        compositions = 0;
        long kk = k.abs().longValueExact();
        long half = kk == 4 ? 2 : 1;                       // for k = 4 or -4, work with halves: k becomes 1 or -1
        T h = new T(Q.of(a, big(half)), Q.of(b, big(half)), Q.of(k, big(half * half)));
        T t = h;
        if (kk == 2) { t = compose(h, h, N); t = new T(t.a.over(2), t.b.over(2), t.k.over(4)); compositions++; }
        while (!t.whole()) { t = compose(t, h, N); compositions++; }      // powers of the half-triple until whole
        if (t.k.equals(Q.of(-1))) { t = compose(t, t, N); compositions++; }
        check(holds(t, N) && t.k.equals(Q.of(1)) && t.whole(), "Brahmagupta's finish gives a whole answer");
        return new BigInteger[]{t.a.n, t.b.n};
    }

    static long cfSteps;

    /** Lagrange's way: continued fraction convergents p/q of sqrt(N) until p^2 - N q^2 = 1. Returns {p, q}. */
    static BigInteger[] continuedFraction(long N) {
        long a0 = (long) Math.sqrt((double) N);
        while (a0 * a0 > N) a0--;
        while ((a0 + 1) * (a0 + 1) <= N) a0++;
        long m = 0, d = 1, a = a0;
        BigInteger p0 = BigInteger.ONE, q0 = BigInteger.ZERO, p1 = big(a0), q1 = BigInteger.ONE, n = big(N);
        cfSteps = 1;
        while (!p1.multiply(p1).subtract(n.multiply(q1).multiply(q1)).equals(BigInteger.ONE)) {
            m = d * a - m;
            d = (N - m * m) / d;
            a = (a0 + m) / d;
            BigInteger p2 = big(a).multiply(p1).add(p0), q2 = big(a).multiply(q1).add(q0);
            p0 = p1; q0 = q1; p1 = p2; q1 = q2;
            cfSteps++;
        }
        return new BigInteger[]{p1, q1};
    }

    public static void main(String[] args) {
        // ---- the composition identity -----------------------------------------------------------------------------
        Random rnd = new Random(628);
        for (int t = 0; t < 20_000; t++) {
            long N = 2 + rnd.nextInt(1000), a = rnd.nextInt(2000) - 1000, b = rnd.nextInt(2000) - 1000, c = rnd.nextInt(2000) - 1000, d = rnd.nextInt(2000) - 1000;
            T x = new T(Q.of(a), Q.of(b), Q.of(a * a - N * b * b)), y = new T(Q.of(c), Q.of(d), Q.of(c * c - N * d * d));
            check(holds(compose(x, y, N), N), "Brahmagupta's composition identity");
        }
        System.out.printf("compose: (ac + Nbd)^2 - N(ad + bc)^2 = (a^2 - Nb^2)(c^2 - Nd^2) on 20000 random cases%n");

        // ---- Brahmagupta's N = 92 ---------------------------------------------------------------------------------
        long N = 92;
        T s = new T(Q.of(10), Q.of(1), Q.of(8));
        check(holds(s, N), "10^2 - 92 = 8");
        T s2 = compose(s, s, N);
        T s3 = new T(s2.a.over(8), s2.b.over(8), s2.k.over(64));
        T s4 = compose(s3, s3, N);
        check(holds(s4, N) && s4.whole() && s4.k.equals(Q.of(1)), "two compositions give a whole answer");
        System.out.printf("n92: start %s ; composed with itself %s ; divided by 8 %s ; composed again %s%n", s, s2, s3, s4);

        // ---- Bhaskara's N = 61 and 67 ----------------------------------------------------------------------------
        for (long n : new long[]{61, 67}) {
            trace = new ArrayList<>();
            BigInteger[] ab = chakravala(n);
            List<String> tr = trace;
            trace = null;
            for (String line : tr) System.out.printf("chakravala %d: %s%n", n, line);
            BigInteger[] cf = continuedFraction(n);
            check(ab[0].equals(cf[0]) && ab[1].equals(cf[1]), "chakravala and continued fractions agree for " + n);
            long fullSteps = chakSteps, convergents = cfSteps;
            BigInteger[] early = chakravala(n, true);
            check(early[0].equals(ab[0]) && early[1].equals(ab[1]), "stopping early gives the same answer for " + n);
            System.out.printf("answer %d: a = %s, b = %s ; chakravala %d steps ; stopping at k = %s after %d step%s and finishing by %d composition%s ; continued fractions %d convergents%n",
                    n, ab[0], ab[1], fullSteps, stopTriple[2], chakSteps, chakSteps == 1 ? "" : "s", compositions, compositions == 1 ? "" : "s", convergents);
        }
        // the short route for 61: one step to k = -4, then Brahmagupta's finish with halves
        T h = new T(Q.of(39).over(2), Q.of(5).over(2), Q.of(-1));        // 39^2 - 61 x 5^2 = -4, halved
        check(holds(h, 61), "(39/2)^2 - 61 (5/2)^2 = -1");
        T h2 = compose(h, h, 61), h3 = compose(h2, h, 61), h6 = compose(h3, h3, 61);
        check(h3.whole() && h3.k.equals(Q.of(-1)), "the cube is whole, with k = -1");
        check(h6.whole() && h6.k.equals(Q.of(1)) && h6.a.n.toString().equals("1766319049"), "the square of the cube is Bhaskara's answer");
        System.out.printf("short 61: (39, 5, -4) halved %s ; squared %s ; cubed %s ; cube squared %s%n", h, h2, h3, h6);

        // ---- every N up to 1000 ------------------------------------------------------------------------------------
        int count = 0, chakFewer = 0, worstN = 0;
        long chakTotal = 0, cfTotal = 0, chakMax = 0, cfMax = 0, earlyTotal = 0;
        int digitsMax = 0;
        String biggest = "";
        for (long n = 2; n <= 1000; n++) {
            long r = (long) Math.sqrt((double) n);
            if (r * r == n) continue;
            count++;
            BigInteger[] ab = chakravala(n);
            long full = chakSteps;
            BigInteger[] early = chakravala(n, true);
            long shortWork = chakSteps + compositions;
            check(early[0].equals(ab[0]) && early[1].equals(ab[1]), "the early stop and Brahmagupta's finish give the same answer");
            earlyTotal += shortWork;
            chakSteps = full;
            BigInteger[] cf = continuedFraction(n);
            check(ab[0].equals(cf[0]) && ab[1].equals(cf[1]), "both methods find the same smallest answer");
            chakTotal += chakSteps; cfTotal += cfSteps;
            chakMax = Math.max(chakMax, chakSteps); cfMax = Math.max(cfMax, cfSteps);
            if (chakSteps <= cfSteps) chakFewer++;
            if (ab[0].toString().length() > digitsMax) { digitsMax = ab[0].toString().length(); worstN = (int) n; biggest = ab[0].toString(); }
        }
        check(chakFewer == count, "the chakravala never needs more steps than the convergents");
        System.out.printf("survey: %d values of N from 2 to 1000 (squares left out) ; same smallest answer every time ; chakravala %.1f steps on average, at most %d ; stopping early and composing %.1f operations on average ; continued fractions %.1f convergents on average, at most %d%n",
                count, chakTotal / (double) count, chakMax, earlyTotal / (double) count, cfTotal / (double) count, cfMax);
        System.out.printf("biggest: N = %d has the largest smallest answer below 1000: a = %s (%d digits)%n", worstN, biggest, digitsMax);

        // ---- search -------------------------------------------------------------------------------------------------
        long tries = 0;
        BigInteger[] s61 = continuedFraction(61);
        for (long b = 1; b <= 120; b++) {                  // Brahmagupta's 92: b = 120
            tries++;
            long v = 92 * b * b + 1, r = (long) Math.sqrt((double) v);
            if (r * r == v) { check(b == 120 && r == 1151, "search finds 1151 and 120 for 92"); break; }
        }
        System.out.printf("search: for 92, trying b = 1, 2, 3, ... finds the answer after %d tries ; for 61 it would need %s tries ; for %d, %s tries%n",
                tries, s61[1], worstN, continuedFraction(worstN)[1]);

        System.out.printf("Chakravala: %d checks passed%n", passed);
    }
}
