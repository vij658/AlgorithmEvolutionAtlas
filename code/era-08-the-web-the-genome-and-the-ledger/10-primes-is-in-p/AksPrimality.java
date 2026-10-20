import java.util.*;

/**
 * Era 8, topic 10: PRIMES is in P (Manindra Agrawal, Neeraj Kayal and Nitin Saxena, IIT Kanpur, 6 August 2002).
 *
 * HOW IT WORKS
 *   For n > 1 and any a with gcd(a, n) = 1:  n is prime exactly when (X + a)^n = X^n + a as polynomials with every
 *   coefficient taken modulo n. (The middle coefficients of (X + a)^n are the binomial numbers C(n, k) times powers of
 *   a; all of them are divisible by n exactly when n is prime.) But (X + a)^n has n + 1 coefficients: checking them is
 *   no faster than trying divisors. Agrawal, Kayal and Saxena check the identity only modulo X^r - 1 as well, so every
 *   polynomial has fewer than r coefficients, for a small r and a few values of a, and prove that this is enough:
 *     1. If n = a^b with b > 1, n is composite.
 *     2. Find the smallest r for which the powers of n modulo r take more than (log2 n)^2 steps to return to 1.
 *     3. If some a <= r has 1 < gcd(a, n) < n, n is composite.
 *     4. If n <= r, n is prime.
 *     5. For a = 1 to floor(sqrt(phi(r)) log2 n): if (X + a)^n is not X^(n mod r) + a modulo (X^r - 1, n), composite.
 *     6. Otherwise n is prime.
 *   r is at most about (log2 n)^5, so every step takes time polynomial in the number of digits of n. No coin is
 *   tossed, and nothing unproved is assumed. (This is the version on Wikipedia; the August 2002 preprint chose r
 *   differently.)
 *
 * WHAT THIS PROGRAM DOES
 *   1. The identity checked in full for every n up to 300.
 *   2. AKS run on every n from 2 to 3,000 and compared with a sieve; which step decides each one.
 *   3. Carmichael numbers and a strong pseudoprime, which fool Fermat's and Miller's quick tests, against AKS; and
 *      products of two primes larger than r, which only the polynomial check can catch.
 *   4. The cost for primes near 1,000, 10,000 and 100,000, counted in coefficient multiplications, against Miller-Rabin.
 *   5. Pascal's triangle modulo n and the AKS steps for a few numbers, for the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AksPrimality.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AksPrimality {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long gcd(long a, long b) { while (b != 0) { long t = a % b; a = b; b = t; } return Math.abs(a); }

    static long powMod(long b, long e, long m) {
        long r = 1 % m; b %= m;
        while (e > 0) { if ((e & 1) == 1) { r = r * b % m; mults++; } b = b * b % m; mults++; e >>= 1; }
        return r;
    }

    static double log2(long n) { return Math.log(n) / Math.log(2); }

    static boolean perfectPower(long n) {
        for (int b = 2; (1L << b) <= n; b++) {
            long a = Math.round(Math.pow(n, 1.0 / b));
            for (long c = Math.max(2, a - 1); c <= a + 1; c++) {
                long p = 1;
                for (int i = 0; i < b && p <= n; i++) p *= c;
                if (p == n) return true;
            }
        }
        return false;
    }

    static int order(long n, int r) { // multiplicative order of n modulo r (gcd(n, r) = 1)
        long x = n % r;
        int k = 1;
        long v = x;
        while (v != 1) { v = v * x % r; k++; if (k > r) return -1; }
        return k;
    }

    static int phi(int r) { int res = r, x = r; for (int p = 2; p * p <= x; p++) if (x % p == 0) { while (x % p == 0) x /= p; res -= res / p; } if (x > 1) res -= res / x; return res; }

    static long mults; // coefficient multiplications, for counting cost

    /** a * b modulo (X^r - 1, n); n < 2^20 so the products can be summed in a long before reducing. */
    static long[] mulMod(long[] a, long[] b, int r, long n) {
        long[] c = new long[r];
        for (int i = 0; i < r; i++) if (a[i] != 0) {
            for (int j = 0; j < r; j++) {
                int k = i + j; if (k >= r) k -= r;
                c[k] += a[i] * b[j];
            }
            mults += r;
        }
        for (int k = 0; k < r; k++) c[k] %= n;
        return c;
    }

    /** (X + a)^n modulo (X^r - 1, n). */
    static long[] powXa(long a, long n, int r) {
        long[] result = new long[r]; result[0] = 1;
        long[] base = new long[r]; base[0] = a % n; base[1 % r] = (base[1 % r] + 1) % n;
        long e = n;
        while (e > 0) {
            if ((e & 1) == 1) result = mulMod(result, base, r, n);
            e >>= 1;
            if (e > 0) base = mulMod(base, base, r, n);
        }
        return result;
    }

    record Verdict(boolean prime, int step, int r, long aMax, String why) {}

    static Verdict aks(long n) {
        if (n < 2) return new Verdict(false, 0, 0, 0, "below 2");
        if (perfectPower(n)) return new Verdict(false, 1, 0, 0, "a perfect power");
        double l = log2(n);
        int r = 2;
        while (true) {
            if (gcd(n, r) == 1) { int o = order(n, r); if (o > l * l) break; }
            r++;
        }
        for (long a = 2; a <= Math.min(r, n - 1); a++) { long g = gcd(a, n); if (g > 1 && g < n) return new Verdict(false, 3, r, 0, "gcd(" + a + ", n) = " + g); }
        if (n <= r) return new Verdict(true, 4, r, 0, "n <= r");
        long aMax = (long) Math.floor(Math.sqrt(phi(r)) * l);
        for (long a = 1; a <= aMax; a++) {
            long[] p = powXa(a, n, r);
            long[] want = new long[r];
            want[(int) (n % r)] = 1;
            want[0] = (want[0] + a) % n;
            if (!Arrays.equals(p, want)) return new Verdict(false, 5, r, aMax, "fails for a = " + a);
        }
        return new Verdict(true, 6, r, aMax, "passes every a");
    }

    static boolean millerRabin(long n, long[] bases) {
        if (n < 2) return false;
        long d = n - 1; int s = 0;
        while (d % 2 == 0) { d /= 2; s++; }
        for (long b : bases) {
            if (b % n == 0) continue;
            long x = powMod(b, d, n);
            if (x == 1 || x == n - 1) continue;
            boolean ok = false;
            for (int i = 1; i < s; i++) { x = x * x % n; mults++; if (x == n - 1) { ok = true; break; } }
            if (!ok) return false;
        }
        return true;
    }

    public static void main(String[] args) {
        int N = 3000;
        boolean[] composite = new boolean[N + 1];
        composite[0] = composite[1] = true;
        for (int i = 2; (long) i * i <= N; i++) if (!composite[i]) for (int j = i * i; j <= N; j += i) composite[j] = true;

        // ---- 1. the identity in full ---------------------------------------------------------------------------------
        for (int n = 2; n <= 300; n++) {
            long[] row = new long[n + 1]; // the binomial numbers C(n, k) mod n, by Pascal's rule
            row[0] = 1;
            for (int m = 1; m <= n; m++) for (int k = m; k >= 1; k--) row[k] = (row[k] + row[k - 1]) % n;
            boolean allZero = true;
            for (int k = 1; k < n; k++) if (row[k] != 0) allZero = false;
            check(allZero == !composite[n], "n is prime exactly when every C(n, k), 0 < k < n, is divisible by n");
        }
        System.out.println("identity: for every n from 2 to 300, every middle number of row n of Pascal's triangle is divisible by n exactly when n is prime (so (X + a)^n = X^n + a^n modulo n exactly then; with gcd(a, n) = 1, a^n can be replaced by a only for primes)");

        // ---- 2. AKS against the sieve --------------------------------------------------------------------------------
        int[] byStep = new int[7];
        int maxR = 0;
        long maxA = 0;
        for (int n = 2; n <= N; n++) {
            Verdict v = aks(n);
            check(v.prime() == !composite[n], "AKS agrees with the sieve");
            byStep[v.step()]++;
            maxR = Math.max(maxR, v.r());
            maxA = Math.max(maxA, v.aMax());
        }
        System.out.printf("sieve: n = 2 to %,d: AKS agrees with the sieve on all %,d ; decided at step 1 (perfect power): %d, step 3 (a small common factor): %,d, step 4 (n <= r, prime): %d, step 5 (a polynomial check fails): %d, step 6 (all polynomial checks pass, prime): %d ; largest r %d, largest number of values of a %d%n",
                N, N - 1, byStep[1], byStep[3], byStep[4], byStep[5], byStep[6], maxR, maxA);

        // ---- 3. numbers that fool quick tests ------------------------------------------------------------------------
        StringJoiner cj = new StringJoiner(" ; ");
        long[] tricky = {561, 1105, 1729, 2465, 2821, 6601, 8911, 2047};
        for (long n : tricky) {
            boolean fermatFooled = true;
            for (long a = 2; a < n; a++) if (gcd(a, n) == 1 && powMod(a, n - 1, n) != 1) fermatFooled = false;
            boolean mr2 = millerRabin(n, new long[]{2});
            Verdict v = aks(n);
            check(!v.prime(), "AKS is never fooled");
            if (n != 2047) check(fermatFooled, n + " is a Carmichael number: a^(n-1) = 1 mod n for every a coprime to n");
            else check(mr2, "2047 passes Miller's test to base 2");
            cj.add(String.format("%d: Fermat's test fooled by every coprime base: %s, Miller-Rabin base 2 fooled: %s, AKS: composite at step %d (%s)", n, fermatFooled ? "yes" : "no", mr2 ? "yes" : "no", v.step(), v.why()));
        }
        System.out.printf("tricky: %s%n", cj);
        StringJoiner sj = new StringJoiner(" ; ");
        for (long[] pq : new long[][]{{1009, 1013}, {1031, 1033}, {1201, 1709}}) {
            long n = pq[0] * pq[1];
            Verdict v = aks(n);
            check(!v.prime() && v.step() == 5 && pq[0] > v.r(), "a product of two primes above r is caught only by the polynomial check");
            sj.add(String.format("%,d = %,d x %,d: r = %d, so no factor is found by step 3 ; composite at step 5 (%s)", n, pq[0], pq[1], v.r(), v.why()));
        }
        System.out.printf("polynomial: numbers whose factors are all larger than r, so that only the polynomial check can catch them ; %s%n", sj);

        // ---- 4. cost -------------------------------------------------------------------------------------------------
        StringJoiner kj = new StringJoiner(" ; ");
        long prevCost = 0;
        for (long n : new long[]{1009, 10007, 100003}) {
            mults = 0;
            Verdict v = aks(n);
            check(v.prime(), n + " is prime");
            long cost = mults;
            mults = 0;
            check(millerRabin(n, new long[]{2, 3, 5, 7}), "and Miller-Rabin agrees");
            long mr = mults;
            check(cost > 4 * prevCost, "the cost grows quickly with the digits");
            prevCost = cost;
            kj.add(String.format("%,d: r = %d, a up to %d, %,d coefficient multiplications (Miller-Rabin with bases 2, 3, 5, 7: %d multiplications)", n, v.r(), v.aMax(), cost, mr));
        }
        System.out.printf("cost: %s%n", kj);

        // ---- 5. the widget ---------------------------------------------------------------------------------------------
        StringJoiner wj = new StringJoiner(" ; ");
        for (long n : new long[]{7, 9, 31, 97, 341, 561, 1009}) {
            Verdict v = aks(n);
            check(v.prime() == (n < N ? !composite[(int) n] : true), "widget numbers agree with the sieve");
            wj.add(String.format("%d: %s at step %d, r = %d, a up to %d (%s)", n, v.prime() ? "prime" : "composite", v.step(), v.r(), v.aMax(), v.why()));
        }
        System.out.printf("widget: %s%n", wj);

        System.out.println("AksPrimality: " + passed + " checks passed");
    }
}
