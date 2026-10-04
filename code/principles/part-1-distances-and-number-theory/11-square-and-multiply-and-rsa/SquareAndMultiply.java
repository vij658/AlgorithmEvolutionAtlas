import java.math.BigInteger;
import java.util.*;
import java.util.stream.IntStream;

/**
 * Entry 11 of the principles catalog (Part 1): Square-and-multiply, Fermat's little theorem and RSA
 *
 * HOW IT WORKS
 *   Compute a^e mod m by reading e in binary: square for every bit, multiply in a when the bit is 1, so only
 *   about 2*log2 e multiplications are needed. Fermat's little theorem gives a fast (fallible) primality test,
 *   and together with the extended Euclid inverse it is enough for textbook RSA.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java SquareAndMultiply.java
 *   Expected: the output in expected-output.txt, ending "SquareAndMultiply: 3002 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class SquareAndMultiply {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---------- modular arithmetic ----------
    static long modPow(long base, long exp, long mod) {   // needs mod <= ~3.03e9 so products fit in a long
        long result = 1 % mod;
        base %= mod;
        while (exp > 0) {
            if ((exp & 1) == 1) result = result * base % mod;
            base = base * base % mod;
            exp >>= 1;
        }
        return result;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    // ---------- sieve ----------
    static int[] primesUpTo(int n) {
        boolean[] composite = new boolean[n + 1];
        for (long i = 2; i * i <= n; i++)
            if (!composite[(int) i])
                for (long j = i * i; j <= n; j += i) composite[(int) j] = true;
        return IntStream.rangeClosed(2, n).filter(i -> !composite[i]).toArray();
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java SquareAndMultiply.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // modular exponentiation, Fermat, RSA
        for (int i = 0; i < 2000; i++) {
            long mod = rnd.nextLong(2, 3_000_000_000L);
            long b = rnd.nextLong(0, 3_000_000_000L), e = rnd.nextLong(0, 1_000_000_000_000L);
            check(modPow(b, e, mod) == BigInteger.valueOf(b).modPow(BigInteger.valueOf(e), BigInteger.valueOf(mod)).longValue(), "modPow vs BigInteger");
        }
        final long MOD = 1_000_000_007L;
        for (int i = 0; i < 1000; i++) {
            long a = rnd.nextLong(1, MOD);
            check(a * modPow(a, MOD - 2, MOD) % MOD == 1, "Fermat inverse a^(p-2)");
        }
        long n = 61L * 53L, e = 17;
        long c = modPow(65, e, n);
        check(n == 3233 && c == 2790 && modPow(c, 2753, n) == 65, "toy RSA round trip");
        check(modPow(2, 560, 561) == 1 && !BigInteger.valueOf(561).isProbablePrime(50), "Carmichael 561 fools the Fermat test");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("SquareAndMultiply: " + passed + " checks passed");
    }
}
