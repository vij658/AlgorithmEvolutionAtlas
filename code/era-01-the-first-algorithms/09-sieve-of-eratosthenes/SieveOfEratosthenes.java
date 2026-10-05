import java.util.*;

/**
 * Era 1, topic 9: the sieve of Eratosthenes (Eratosthenes of Cyrene, 276-194 BCE; the method survives in Nicomachus
 * of Gerasa's Introduction to Arithmetic, about 100 CE, Book I, Chapter 13).
 *
 * HOW IT WORKS
 *   To list the primes up to N, do not test each number for divisors. Write all the numbers down, then for each prime
 *   p in turn cross out its multiples. Whatever is never crossed out is prime. Two refinements make it fast: start
 *   crossing at p x p (smaller multiples were already crossed by smaller primes), and stop once p x p passes N. The work
 *   is about N log log N crossings, far less than testing each number by division.
 *   Nicomachus's account crosses out with every odd number, not only with primes; the extra work is wasted but the
 *   answer is the same. The linear sieve crosses each composite exactly once.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Counts the work of six ways to list the primes up to N: trial division by primes up to the square root, the
 *      "unfaithful sieve" of functional programming (each number tested against every earlier prime, O'Neill 2009),
 *      sieving odd numbers with every odd number (as in Nicomachus's account) or with odd primes only, the textbook
 *      sieve (primes from p x p over all numbers), and the linear sieve.
 *   2. Checks that all six agree, and counts the primes: 25 below 100, up to 5,761,455 below 100,000,000 (with a
 *      segmented sieve that holds only a small window in memory).
 *   3. Compares the crossings with N log log N and the prime counts with N / ln N.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SieveOfEratosthenes.java
 *   Expected output: expected-output.txt in this folder.
 */
public class SieveOfEratosthenes {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long work;                                                   // divisions or crossings, depending on the method

    /** The sieve: cross out multiples of each prime p, starting at p x p, while p x p <= n. */
    static boolean[] sieve(int n) {
        boolean[] composite = new boolean[n + 1];
        work = 0;
        for (int p = 2; (long) p * p <= n; p++) {
            if (composite[p]) continue;                                 // only primes do the crossing
            for (int m = p * p; m <= n; m += p) {                       // counting on by p: repeated addition
                composite[m] = true;
                work++;
            }
        }
        return composite;
    }

    /**
     * The sieve on odd numbers only (even numbers above 2 are known to be composite), crossing with the odd primes
     * from p x p in steps of 2p.
     */
    static boolean[] oddSieve(int n, boolean everyOdd) {
        boolean[] composite = new boolean[n + 1];
        for (int m = 4; m <= n; m += 2) composite[m] = true;           // the even numbers, known at once
        work = 0;
        for (int k = 3; (long) k * k <= n; k += 2) {
            if (!everyOdd && composite[k]) continue;                    // primes only; or every odd number, as in Nicomachus
            for (int m = k * k; m <= n; m += 2 * k) {
                composite[m] = true;
                work++;
            }
        }
        return composite;
    }

    /** Trial division: test each number by the primes up to its square root. */
    static List<Integer> trialDivision(int n) {
        List<Integer> primes = new ArrayList<>();
        work = 0;
        for (int x = 2; x <= n; x++) {
            boolean prime = true;
            for (int p : primes) {
                if ((long) p * p > x) break;
                work++;
                if (x % p == 0) { prime = false; break; }
            }
            if (prime) primes.add(x);
        }
        return primes;
    }

    /** The "unfaithful sieve": each number is tested against every earlier prime until one divides it (no square-root stop). */
    static List<Integer> unfaithful(int n) {
        List<Integer> primes = new ArrayList<>();
        work = 0;
        for (int x = 2; x <= n; x++) {
            boolean prime = true;
            for (int p : primes) {
                work++;
                if (x % p == 0) { prime = false; break; }
            }
            if (prime) primes.add(x);
        }
        return primes;
    }

    /** The linear sieve: every composite c is crossed exactly once, as (smallest prime factor of c) x (c / that factor). */
    static int[] linear(int n) {
        int[] spf = new int[n + 1];
        List<Integer> primes = new ArrayList<>();
        work = 0;
        for (int i = 2; i <= n; i++) {
            if (spf[i] == 0) { spf[i] = i; primes.add(i); }
            for (int p : primes) {
                if (p > spf[i] || (long) p * i > n) break;
                spf[p * i] = p;
                work++;
            }
        }
        return spf;
    }

    /** Count the primes up to n with a segmented sieve: only the primes up to sqrt(n) and one window are in memory. */
    static long segmentedCount(long n, int window) {
        int root = (int) Math.sqrt((double) n);
        while ((long) (root + 1) * (root + 1) <= n) root++;
        boolean[] small = sieve(root);
        List<Integer> base = new ArrayList<>();
        for (int p = 2; p <= root; p++) if (!small[p]) base.add(p);
        long count = 0;
        boolean[] seg = new boolean[window];
        for (long lo = 2; lo <= n; lo += window) {
            long hi = Math.min(n, lo + window - 1);
            Arrays.fill(seg, false);
            for (int p : base) {
                long pp = (long) p * p;
                if (pp > hi) break;
                long start = Math.max(pp, (lo + p - 1) / p * p);
                for (long m = start; m <= hi; m += p) seg[(int) (m - lo)] = true;
            }
            for (long x = lo; x <= hi; x++) if (!seg[(int) (x - lo)]) count++;
        }
        return count;
    }

    static int count(boolean[] composite) {
        int c = 0;
        for (int i = 2; i < composite.length; i++) if (!composite[i]) c++;
        return c;
    }

    public static void main(String[] args) {
        // the classic picture: 1 to 100
        boolean[] c100 = sieve(100);
        StringJoiner pr = new StringJoiner(" ");
        for (int i = 2; i <= 100; i++) if (!c100[i]) pr.add(Integer.toString(i));
        System.out.printf("primes to 100: %s%n", pr);
        // which prime crosses each number first (its smallest prime factor), for the picture
        int[] spf100 = linear(100);
        StringJoiner sp = new StringJoiner(" ");
        for (int i = 2; i <= 100; i++) sp.add(Integer.toString(spf100[i]));
        System.out.printf("smallest factor 2-100: %s%n", sp);
        sieve(100);
        long w100 = work;
        int crossingPrimes = 0;
        for (int p = 2; p * p <= 100; p++) if (!c100[p]) crossingPrimes++;
        System.out.printf("sieve 100: %d crossings by %d primes (2, 3, 5, 7); 11 x 11 = 121 passes 100, so every number left is prime%n", w100, crossingPrimes);

        // five methods, same answers, different work
        Map<Integer, Integer> known = Map.of(100, 25, 10_000, 1229, 100_000, 9592, 1_000_000, 78498, 10_000_000, 664579);
        for (int n : new int[]{100, 10_000, 100_000, 1_000_000, 10_000_000}) {
            boolean[] s = sieve(n);
            long wSieve = work;
            int cnt = count(s);
            check(cnt == known.get(n), "prime count up to " + n);
            boolean[] nico = oddSieve(n, true);
            long wNico = work;
            check(Arrays.equals(s, nico), "sieving with every odd number gives the same primes");
            boolean[] odd = oddSieve(n, false);
            long wOdd = work;
            check(Arrays.equals(s, odd), "sieving odd numbers with odd primes gives the same primes");
            check(wOdd < wNico, "composites as sieving numbers only add work");
            List<Integer> td = trialDivision(n);
            long wTrial = work;
            check(td.size() == cnt, "trial division agrees");
            int[] lin = linear(n);
            long wLin = work;
            int linCount = 0;
            for (int i = 2; i <= n; i++) if (lin[i] == i) linCount++;
            check(linCount == cnt, "linear sieve agrees");
            check(wLin == n - 1 - cnt, "the linear sieve crosses each composite exactly once");
            String unf = "-";
            if (n <= 100_000) {
                List<Integer> u = unfaithful(n);
                check(u.equals(td), "the unfaithful sieve gives the same primes");
                unf = Long.toString(work);
            }
            double nloglog = n * Math.log(Math.log(n));
            System.out.printf("work %d: primes=%d trial-division=%d unfaithful-sieve=%s every-odd=%d odd-primes=%d sieve=%d linear=%d ; n ln ln n = %.0f ; n / ln n = %.0f%n",
                    n, cnt, wTrial, unf, wNico, wOdd, wSieve, wLin, nloglog, n / Math.log(n));
        }

        // segmented: a window of 2^16 numbers at a time
        long seg7 = segmentedCount(10_000_000, 1 << 16);
        check(seg7 == 664579, "segmented count agrees at 10^7");
        long seg8 = segmentedCount(100_000_000, 1 << 16);
        check(seg8 == 5_761_455, "5,761,455 primes below 10^8");
        System.out.printf("segmented: %d primes up to 100,000,000 with a window of %d numbers and %d sieving primes in memory (a whole table would need 100,000,001 cells)%n",
                seg8, 1 << 16, count(sieve(10_000)));

        // the gaps: where the sieve leaves big holes
        boolean[] s = sieve(10_000_000);
        int last = 2, bestGap = 0, gapAt = 0, twins = 0;
        for (int i = 3; i <= 10_000_000; i++) {
            if (!s[i]) {
                if (i - last > bestGap) { bestGap = i - last; gapAt = last; }
                if (i - last == 2) twins++;
                last = i;
            }
        }
        System.out.printf("gaps up to 10,000,000: largest gap %d after the prime %d; %d twin-prime pairs%n", bestGap, gapAt, twins);

        System.out.printf("SieveOfEratosthenes: %d checks passed%n", passed);
    }
}
