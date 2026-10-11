import java.math.BigInteger;
import java.util.*;

/**
 * Era 2, topic 3: the Chinese remainder problem (Sunzi Suanjing, Volume 3, Problem 26, 3rd-5th century CE, date
 * disputed), and Qin Jiushao's dayan rule for finding the multipliers (Shushu jiuzhang, 1247).
 *
 * HOW IT WORKS
 *   "Counted in threes, 2 are left; in fives, 3; in sevens, 2. How many?" Sunzi does not search. He keeps one ready-made
 *   number for each divisor: 70, 21 and 15. Each is a multiple of the other two divisors that leaves 1 for its own
 *   (70 = 2 x 35 leaves 1 when divided by 3, and is divisible by 5 and 7). So 2 x 70 + 3 x 21 + 2 x 15 leaves 2, 3 and 2,
 *   and casting out 105 = 3 x 5 x 7 as often as possible gives the smallest answer, 23.
 *   Finding the ready-made numbers for other divisors is the hard part: for each divisor m and the product M of the
 *   others, find k with M k leaving 1 when divided by m. Qin Jiushao's dayan qiuyi ("finding one") rule does it on the
 *   counting board: put M (reduced by m) at the upper right, m at the lower right, 1 at the upper left; divide the lower
 *   number by the upper and the upper by the lower in turn, adding each quotient times the left-hand number to the
 *   other left-hand place, until the upper right is 1. The upper left is then k. It is Euclid's algorithm with a
 *   running record of the quotients: what is now called the extended Euclidean algorithm.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Solves Sunzi's problem by his rule and by search, and checks that all 105 triples of remainders have exactly one
 *      answer below 105.
 *   2. Runs the dayan rule step by step for Sunzi's multipliers and for a calendar congruence in Qin's book
 *      (377873 x leaves 1 when divided by 499067), and checks it against the extended Euclidean algorithm on
 *      100,000 random cases.
 *   3. Solves systems whose divisors share factors, by Qin's idea of replacing them with coprime divisors, against a
 *      brute-force search.
 *   4. Measures search against the rule as the cycles grow.
 *   5. Full circle: RSA decryption by the remainder theorem (as in PKCS #1, RFC 8017) against plain decryption, with
 *      the cost in word multiplications.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ChineseRemainder.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ChineseRemainder {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long divisions;                               // division steps on the board

    /**
     * Qin Jiushao's dayan qiuyi: k with a k = 1 (mod m), for a and m coprime, a reduced below m. The board has four
     * places: upper left (starts at 1), upper right (a), lower left (starts at 0), lower right (m). trace may be null.
     */
    static long dayan(long a, long m, List<String> trace) {
        long ul = 1, ur = a % m, ll = 0, lr = m;
        if (ur == 1) return 1;
        while (true) {
            long q = lr / ur;                              // the lower right divided by the upper right
            lr -= q * ur;
            ll += q * ul;
            divisions++;
            if (trace != null) trace.add(String.format("lower by upper: quotient %d ; board %d %d / %d %d", q, ul, ur, ll, lr));
            if (lr == 0) throw new IllegalArgumentException("not coprime");
            q = lr == 1 ? ur - 1 : ur / lr;                // the upper right divided by the lower right; stop at 1, not 0
            ur -= q * lr;
            ul += q * ll;
            divisions++;
            if (trace != null) trace.add(String.format("upper by lower: quotient %d ; board %d %d / %d %d", q, ul, ur, ll, lr));
            if (ur == 1) return ul % m;
        }
    }

    /** The extended Euclidean algorithm, for comparison. */
    static long inverse(long a, long m) {
        long r0 = m, r1 = a % m, t0 = 0, t1 = 1;
        while (r1 != 0) {
            long q = r0 / r1, r = r0 - q * r1, t = t0 - q * t1;
            r0 = r1; r1 = r; t0 = t1; t1 = t;
        }
        if (r0 != 1) throw new IllegalArgumentException("not coprime");
        return ((t0 % m) + m) % m;
    }

    /** Sunzi's rule for pairwise coprime divisors: the multipliers, then the sum, cast out the product. */
    static long[] multipliers(long[] m) {
        long prod = 1;
        for (long x : m) prod *= x;
        long[] mult = new long[m.length];
        for (int i = 0; i < m.length; i++) {
            long others = prod / m[i];
            mult[i] = others * dayan(others % m[i], m[i], null);
        }
        return mult;
    }

    static long solve(long[] r, long[] m) {
        long prod = 1;
        for (long x : m) prod *= x;
        long[] mult = multipliers(m);
        BigInteger s = BigInteger.ZERO;
        for (int i = 0; i < m.length; i++) s = s.add(BigInteger.valueOf(r[i]).multiply(BigInteger.valueOf(mult[i])));
        return s.mod(BigInteger.valueOf(prod)).longValueExact();
    }

    static long gcd(long a, long b) { return b == 0 ? Math.abs(a) : gcd(b, a % b); }

    /**
     * Divisors that share factors: give each prime power to just one divisor (the one where it is largest), so the new
     * divisors are coprime and their product is the least common multiple; check the remainders agree on shared factors.
     * Returns {answer, lcm}, or null if the conditions contradict each other.
     */
    static long[] solveAny(long[] r, long[] m) {
        int n = m.length;
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if ((r[i] - r[j]) % gcd(m[i], m[j]) != 0) return null;
        long[] keep = new long[n];
        Arrays.fill(keep, 1);
        Map<Long, long[]> best = new TreeMap<>();          // prime -> {highest power, index}
        for (int i = 0; i < n; i++) {
            long x = m[i];
            for (long p = 2; p * p <= x; p++) {
                if (x % p != 0) continue;
                long pw = 1;
                while (x % p == 0) { x /= p; pw *= p; }
                if (!best.containsKey(p) || best.get(p)[0] < pw) best.put(p, new long[]{pw, i});
            }
            if (x > 1 && (!best.containsKey(x) || best.get(x)[0] < x)) best.put(x, new long[]{x, i});
        }
        for (long[] v : best.values()) keep[(int) v[1]] *= v[0];
        List<Long> rs = new ArrayList<>(), ms = new ArrayList<>();
        for (int i = 0; i < n; i++) if (keep[i] > 1) { rs.add(Math.floorMod(r[i], keep[i])); ms.add(keep[i]); }
        long lcm = 1;
        for (long x : ms) lcm *= x;
        if (ms.isEmpty()) return new long[]{0, 1};
        long ans = solve(rs.stream().mapToLong(Long::longValue).toArray(), ms.stream().mapToLong(Long::longValue).toArray());
        return new long[]{ans, lcm};
    }

    static long mulmods;                                  // modular multiplications in square-and-multiply

    static BigInteger power(BigInteger b, BigInteger e, BigInteger m) {
        BigInteger result = BigInteger.ONE, base = b.mod(m);
        for (int i = e.bitLength() - 1; i >= 0; i--) {
            result = result.multiply(result).mod(m);
            mulmods++;
            if (e.testBit(i)) { result = result.multiply(base).mod(m); mulmods++; }
        }
        return result;
    }

    public static void main(String[] args) {
        // ---- Sunzi's problem -------------------------------------------------------------------------------------
        long[] m = {3, 5, 7}, r = {2, 3, 2};
        long[] mult = multipliers(m);
        check(Arrays.equals(mult, new long[]{70, 21, 15}), "Sunzi's multipliers are 70, 21 and 15");
        long sum = 0;
        StringJoiner terms = new StringJoiner(" + ");
        for (int i = 0; i < 3; i++) { sum += r[i] * mult[i]; terms.add(r[i] + " x " + mult[i]); }
        long ans = sum % 105;
        check(sum == 233 && ans == 23, "2 x 70 + 3 x 21 + 2 x 15 = 233, and 233 - 210 = 23");
        long tries = 0, found = -1;
        for (long x = 1; ; x++) { tries++; if (x % 3 == 2 && x % 5 == 3 && x % 7 == 2) { found = x; break; } }
        check(found == 23, "search finds 23");
        System.out.printf("sunzi: multipliers %d %d %d ; %s = %d ; cast out %d -> %d ; search needs %d tries%n",
                mult[0], mult[1], mult[2], terms, sum, sum - ans, ans, tries);
        boolean[] hit = new boolean[105];
        for (int a = 0; a < 3; a++) for (int b = 0; b < 5; b++) for (int c = 0; c < 7; c++) {
            long x = solve(new long[]{a, b, c}, m);
            check(x % 3 == a && x % 5 == b && x % 7 == c && !hit[(int) x], "each triple of remainders has its own answer");
            hit[(int) x] = true;
        }
        System.out.printf("sunzi all: 105 triples of remainders, 105 different answers below 105%n");

        // ---- the dayan rule ---------------------------------------------------------------------------------------
        for (int i = 0; i < 3; i++) {
            long others = 105 / m[i];
            List<String> tr = new ArrayList<>();
            long k = dayan(others % m[i], m[i], tr);
            System.out.printf("dayan %d mod %d: reduce to %d ; k = %d ; multiplier %d x %d = %d ; %d steps%n",
                    others, m[i], others % m[i], k, others, k, others * k, tr.size());
        }
        List<String> tr = new ArrayList<>();
        divisions = 0;
        long kq = dayan(377873, 499067, tr);
        check(kq * 377873 % 499067 == 1, "the calendar congruence is solved");
        check(kq == inverse(377873, 499067), "the dayan rule agrees with the extended Euclidean algorithm");
        for (int s = 0; s < tr.size(); s++) System.out.printf("qin step %d: %s%n", s + 1, tr.get(s));
        System.out.printf("qin answer: 377873 x %d = %d = %d x 499067 + 1 ; %d divisions%n", kq,
                377873L * kq, 377873L * kq / 499067, divisions);
        Random rnd = new Random(1247);
        long totalSteps = 0, worstSteps = 0;
        for (int t = 0; t < 100_000; t++) {
            long mm = 2 + rnd.nextInt(1_000_000_000), a;
            do { a = 1 + (long) (rnd.nextDouble() * (mm - 1)); } while (gcd(a, mm) != 1);
            divisions = 0;
            long k = dayan(a, mm, null);
            check(k == inverse(a, mm), "dayan = extended Euclid");
            totalSteps += divisions;
            worstSteps = Math.max(worstSteps, divisions);
        }
        System.out.printf("dayan random: 100000 random divisors below 10^9, same answer as extended Euclid every time ; %.1f divisions on average, at most %d%n",
                totalSteps / 100_000.0, worstSteps);

        // ---- Qin's example with three cycles, and divisors that share factors --------------------------------------
        long qx = solve(new long[]{1, 14, 1}, new long[]{19, 17, 12});
        check(qx % 19 == 1 && qx % 17 == 14 && qx % 12 == 1, "Qin's three cycles");
        System.out.printf("qin cycles: leaves 1 by 19, 14 by 17, 1 by 12 -> %d (repeats every %d)%n", qx, 19 * 17 * 12);
        long[] shared = solveAny(new long[]{5, 11}, new long[]{12, 18});
        check(shared != null && shared[0] == 29 && shared[1] == 36, "5 by 12 and 11 by 18 -> 29, every 36");
        long[] clash = solveAny(new long[]{1, 2}, new long[]{4, 6});
        check(clash == null, "1 by 4 and 2 by 6 contradict each other: one is odd, the other even");
        System.out.printf("shared: leaves 5 by 12 and 11 by 18 -> divisors 4 and 9 -> %d, every %d ; leaves 1 by 4 and 2 by 6 -> no number%n",
                shared[0], shared[1]);
        int agree = 0;
        for (int a = 2; a <= 24; a++) for (int b = 2; b <= 24; b++) for (int c = 2; c <= 12; c++) {
            long[] mods = {a, b, c};
            long[] rem = {(a * 7 + 3) % a, (b * 5 + 4) % b, (c + 2) % c};
            long[] got = solveAny(rem, mods);
            long l = (long) a / gcd(a, b) * b;
            l = l / gcd(l, c) * c;
            long brute = -1;
            for (long x = 0; x < l; x++) if (x % a == rem[0] && x % b == rem[1] && x % c == rem[2]) { brute = x; break; }
            check(got == null ? brute == -1 : got[0] == brute && got[1] == l, "shared factors: rule = search");
            agree++;
        }
        System.out.printf("shared random: %d systems of three divisors up to 24, the rule agrees with search every time%n", agree);

        // ---- search against the rule as the cycles grow ---------------------------------------------------------------
        long[] primes = {1009, 1013, 1019, 1021, 1031, 1033};
        for (int k = 2; k <= 6; k++) {
            long[] mk = Arrays.copyOf(primes, k), rk = new long[k];
            for (int i = 0; i < k; i++) rk[i] = rnd.nextInt((int) mk[i]);
            divisions = 0;
            long x = solve(rk, mk);
            for (int i = 0; i < k; i++) check(x % mk[i] == rk[i], "the rule's answer leaves the right remainders");
            BigInteger prod = BigInteger.ONE;
            for (long p : mk) prod = prod.multiply(BigInteger.valueOf(p));
            System.out.printf("scale %d cycles: repeat every %s ; answer %d ; search needs %d tries ; the rule needs %d divisions and %d multiplications%n",
                    k, prod, x, x + 1, divisions, k);
        }

        // ---- full circle: RSA decryption by the remainder theorem --------------------------------------------------
        Random kr = new Random(1247);
        BigInteger e = BigInteger.valueOf(65537), p, q, phi;
        do {
            p = BigInteger.probablePrime(1024, kr);
            q = BigInteger.probablePrime(1024, kr);
            phi = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
        } while (!phi.gcd(e).equals(BigInteger.ONE) || p.equals(q));
        if (p.compareTo(q) < 0) { BigInteger t = p; p = q; q = t; }
        BigInteger n = p.multiply(q), d = e.modInverse(phi);
        BigInteger dP = d.mod(p.subtract(BigInteger.ONE)), dQ = d.mod(q.subtract(BigInteger.ONE)), qInv = q.modInverse(p);
        long plainMul = 0, crtMul = 0;
        int msgs = 200;
        for (int t = 0; t < msgs; t++) {
            BigInteger msg = new BigInteger(2040, kr);
            BigInteger c = msg.modPow(e, n);
            mulmods = 0;
            BigInteger m0 = power(c, d, n);
            plainMul += mulmods;
            mulmods = 0;
            BigInteger m1 = power(c, dP, p), m2 = power(c, dQ, q);   // RFC 8017, RSADP step 2.b
            BigInteger h = m1.subtract(m2).multiply(qInv).mod(p);
            BigInteger mc = m2.add(q.multiply(h));
            crtMul += mulmods;
            check(m0.equals(msg) && mc.equals(msg), "both ways decrypt the message");
        }
        int words2048 = 2048 / 64, words1024 = 1024 / 64;
        double plainCost = (double) plainMul / msgs * words2048 * words2048;
        double crtCost = (double) crtMul / msgs * words1024 * words1024;
        check(plainCost / crtCost > 3.5, "the remainder theorem saves about three quarters of the work");
        System.out.printf("rsa: 2048-bit key, %d messages decrypted both ways ; plain: %.0f multiplications of 2048-bit numbers ; by remainders: %.0f of 1024-bit numbers ; word products %.0f against %.0f, %.1f times fewer%n",
                msgs, (double) plainMul / msgs, (double) crtMul / msgs, plainCost, crtCost, plainCost / crtCost);

        System.out.printf("ChineseRemainder: %d checks passed%n", passed);
    }
}
