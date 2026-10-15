import java.math.BigInteger;
import java.util.*;

/**
 * Era 6, topic 10: public-key cryptography (Diffie and Hellman 1976; Rivest, Shamir and Adleman 1977).
 *
 * HOW IT WORKS
 *   Every cipher before 1976 needed the two parties to share a secret key first, carried by hand or by a trusted
 *   courier. Diffie and Hellman asked for functions that are easy to compute and hard to undo.
 *   Key exchange: everyone knows a large prime p and a number g. Alice picks a secret a and publishes g^a mod p; Bob
 *   picks b and publishes g^b mod p. Each raises the other's public number to their own secret and gets g^(ab) mod p.
 *   An eavesdropper who sees g^a and g^b must find a from g^a (a "discrete logarithm"), for which no fast method is
 *   known.
 *   RSA: pick two large primes p and q, publish n = pq and a number e; keep d with e d = 1 modulo (p-1)(q-1).
 *   Anyone can encrypt M as C = M^e mod n; only the holder of d can decrypt, M = C^d mod n. Run the other way, the
 *   holder of d can sign, and anyone can check the signature with e. Finding d from n and e seems to require
 *   factoring n.
 *   Raising to a power mod n is fast: square and multiply, one bit of the exponent at a time. Large primes are found
 *   by testing random numbers with a quick probabilistic test (the RSA paper recommends Solovay and Strassen's).
 *
 * WHAT THIS PROGRAM DOES
 *   1. A Diffie-Hellman exchange with a 256-bit prime.
 *   2. Easy one way, hard the other: powers by squaring against discrete logarithms by search, for growing primes.
 *   3. The RSA paper's small example (p = 47, q = 59) encrypting a message, and decrypting it.
 *   4. Primality tests: Fermat's test fooled by Carmichael numbers; Solovay and Strassen's test, whose liars are
 *      never more than half the bases, checked exhaustively for every odd composite below 3,000.
 *   5. A 1,024-bit RSA key made with that test; messages encrypted, decrypted, signed and verified.
 *   6. Breaking by factoring: trial division on growing n, against the cost of encrypting.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java PublicKey.java
 *   Expected output: expected-output.txt in this folder.
 */
public class PublicKey {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1976L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed;
    }

    static BigInteger randomBits(int bits) {
        BigInteger r = BigInteger.ZERO;
        for (int i = 0; i < bits; i += 32) r = r.shiftLeft(32).add(BigInteger.valueOf((next() >>> 32) & 0xffffffffL));
        return r.shiftRight(r.bitLength() > bits ? r.bitLength() - bits : 0).setBit(bits - 1);
    }

    static BigInteger randomBelow(BigInteger n) {
        BigInteger r;
        do r = randomBits(n.bitLength() + 8).mod(n); while (r.signum() == 0);
        return r;
    }

    static long mults;

    /** x^e mod m by squaring and multiplying, counting multiplications. */
    static BigInteger power(BigInteger x, BigInteger e, BigInteger m) {
        BigInteger r = BigInteger.ONE;
        x = x.mod(m);
        for (int i = e.bitLength() - 1; i >= 0; i--) {
            r = r.multiply(r).mod(m); mults++;
            if (e.testBit(i)) { r = r.multiply(x).mod(m); mults++; }
        }
        return r;
    }

    static long power(long x, long e, long m) {
        long r = 1;
        x %= m;
        while (e > 0) { if ((e & 1) == 1) r = r * x % m; x = x * x % m; e >>= 1; }
        return r;
    }

    /** The Jacobi symbol (a/n) for odd n > 0. */
    static int jacobi(long a, long n) {
        a %= n;
        int s = 1;
        while (a != 0) {
            while (a % 2 == 0) { a /= 2; long r = n % 8; if (r == 3 || r == 5) s = -s; }
            long t = a; a = n; n = t;
            if (a % 4 == 3 && n % 4 == 3) s = -s;
            a %= n;
        }
        return n == 1 ? s : 0;
    }

    static int jacobi(BigInteger a, BigInteger n) {
        a = a.mod(n);
        int s = 1;
        BigInteger three = BigInteger.valueOf(3), four = BigInteger.valueOf(4), eight = BigInteger.valueOf(8), five = BigInteger.valueOf(5);
        while (a.signum() != 0) {
            while (!a.testBit(0)) { a = a.shiftRight(1); BigInteger r = n.mod(eight); if (r.equals(three) || r.equals(five)) s = -s; }
            BigInteger t = a; a = n; n = t;
            if (a.mod(four).equals(three) && n.mod(four).equals(three)) s = -s;
            a = a.mod(n);
        }
        return n.equals(BigInteger.ONE) ? s : 0;
    }

    /** One round of Solovay and Strassen's test with base a: a prime always passes. */
    static boolean solovayStrassen(long n, long a) {
        int j = jacobi(a, n);
        if (j == 0) return false;
        return power(a, (n - 1) / 2, n) == (j == 1 ? 1 : n - 1);
    }

    static boolean probablePrime(BigInteger n, int rounds) {
        if (!n.testBit(0)) return n.equals(BigInteger.TWO);
        for (int i = 0; i < rounds; i++) {
            BigInteger a = randomBelow(n.subtract(BigInteger.ONE));
            int j = jacobi(a, n);
            if (j == 0) return false;
            BigInteger x = a.modPow(n.subtract(BigInteger.ONE).shiftRight(1), n);
            if (!x.equals(j == 1 ? BigInteger.ONE : n.subtract(BigInteger.ONE))) return false;
        }
        return true;
    }

    static BigInteger randomPrime(int bits, int[] tried) {
        while (true) {
            BigInteger c = randomBits(bits).setBit(0).setBit(bits - 2);      // top two bits set: products have 2 x bits
            tried[0]++;
            if (probablePrime(c, 100)) return c;
        }
    }

    static boolean isPrime(long n) {
        if (n < 2) return false;
        for (long d = 2; d * d <= n; d++) if (n % d == 0) return false;
        return true;
    }

    public static void main(String[] args) {
        // ---- 1. Diffie-Hellman -----------------------------------------------------------------------------------------
        int[] tried = {0};
        BigInteger q, p;
        do { q = randomPrime(255, tried); p = q.shiftLeft(1).add(BigInteger.ONE); } while (!probablePrime(p, 100));
        check(p.isProbablePrime(100), "p is prime (Java's own test agrees)");
        BigInteger g = BigInteger.TWO;
        while (g.modPow(q, p).equals(BigInteger.ONE) || g.modPow(BigInteger.TWO, p).equals(BigInteger.ONE)) g = g.add(BigInteger.ONE);
        BigInteger a = randomBelow(p.subtract(BigInteger.ONE)), b = randomBelow(p.subtract(BigInteger.ONE));
        mults = 0;
        BigInteger A = power(g, a, p);
        long oneSide = mults;
        BigInteger B = power(g, b, p);
        BigInteger keyA = power(B, a, p), keyB = power(A, b, p);
        check(keyA.equals(keyB), "both sides compute the same key");
        String hex = keyA.toString(16);
        System.out.printf("dh: public prime p of %d bits (p = 2q + 1 with q prime, found after testing %,d candidates for q) and g = %s ; Alice's secret a and Bob's secret b are random numbers below p ; Alice sends g^a mod p, Bob sends g^b mod p ; each raises what they receive to their own secret ; both get the same %d-bit key, beginning %s ; computing g^a took %d multiplications%n",
                p.bitLength(), tried[0], g, keyA.bitLength(), hex.substring(0, 16), oneSide);

        // ---- 2. one way easy, the other way hard -----------------------------------------------------------------------
        StringJoiner oj = new StringJoiner(" ; ");
        for (int bits = 16; bits <= 32; bits += 4) {
            long pp, gg;
            long cand = (1L << (bits - 1)) + 1 + 2 * (next() >>> 40) % (1L << (bits - 3));
            pp = cand | 1;
            while (!(isPrime(pp) && isPrime((pp - 1) / 2))) pp += 2;
            long qq = (pp - 1) / 2;
            gg = 2;
            while (power(gg, qq, pp) == 1 || power(gg, 2, pp) == 1) gg++;
            long secret = 1 + Long.remainderUnsigned(next(), pp - 2);
            long pub = power(gg, secret, pp);
            // search for the exponent by trying 1, 2, 3, ...
            long x = 1, k = 0;
            while (true) { k++; x = x * gg % pp; if (x == pub) break; }
            check(power(gg, k, pp) == pub, "the logarithm found is right");
            long sq = 0;
            for (long e = secret; e > 0; e >>= 1) sq += (e & 1) == 1 ? 2 : 1;
            oj.add(String.format("%d-bit prime: the power took %d multiplications, the search %,d", bits, sq, k));
        }
        System.out.printf("oneway: g^x mod p for a random secret x below p, by squaring and multiplying (at most 2 multiplications per bit of x) ; then x found again from the result by trying x = 1, 2, 3, ... (on average about p/2 tries) ; %s ; for the 256-bit prime above the power took %d multiplications, and the search would take about 2^255 tries%n", oj, oneSide);

        // ---- 3. the paper's example -----------------------------------------------------------------------------------
        long P = 47, Q = 59, N = P * Q, phi = (P - 1) * (Q - 1), D = 157, E = 17;
        check(N == 2773 && (E * D) % phi == 1, "e d = 1 mod (p-1)(q-1)");
        String msg = "ITS ALL GREEK TO ME";
        StringBuilder digits = new StringBuilder();
        for (char c : msg.toCharArray()) digits.append(String.format("%02d", c == ' ' ? 0 : c - 'A' + 1));
        if (digits.length() % 4 != 0) digits.append("00");
        StringJoiner plain = new StringJoiner(" "), cipher = new StringJoiner(" "), back = new StringJoiner(" ");
        StringBuilder backDigits = new StringBuilder();
        for (int i = 0; i < digits.length(); i += 4) {
            long m = Long.parseLong(digits.substring(i, i + 4));
            long c = power(m, E, N), m2 = power(c, D, N);
            check(m2 == m, "block decrypts");
            plain.add(String.format("%04d", m));
            cipher.add(String.format("%04d", c));
            backDigits.append(String.format("%04d", m2));
        }
        StringBuilder text = new StringBuilder();
        for (int i = 0; i + 1 < backDigits.length(); i += 2) { int v = Integer.parseInt(backDigits.substring(i, i + 2)); text.append(v == 0 ? ' ' : (char) ('A' + v - 1)); }
        check(text.toString().trim().equals(msg), "the message comes back");
        System.out.printf("paper: p = 47, q = 59, n = 2773, (p-1)(q-1) = %d, e = 17, d = 157 (17 x 157 = %d = 1 more than %d) ; \"%s\" as two-digit letters (blank 00, A 01 ... Z 26), blocks of four: %s ; each block M sent as M^17 mod 2773: %s ; each received block C turned back by C^157 mod 2773: \"%s\"%n",
                phi, E * D, phi, msg, plain, cipher, text.toString().trim());

        // ---- 4. primality tests ---------------------------------------------------------------------------------------
        List<Long> carmichael = new ArrayList<>();
        for (long n = 3; n < 100_000; n += 2) {
            if (isPrime(n)) continue;
            boolean allPass = true;
            for (long base = 2; base < n && allPass; base++) {
                if (gcd(base, n) != 1) continue;
                if (power(base, n - 1, n) != 1) allPass = false;
            }
            if (allPass) carmichael.add(n);
        }
        check(carmichael.size() >= 3 && carmichael.get(0) == 561, "561 is the first Carmichael number");
        int composites = 0;
        double worstShare = 0;
        long worstN = 0;
        for (long n = 9; n < 3000; n += 2) {
            if (isPrime(n)) continue;
            composites++;
            long liars = 0;
            for (long base = 1; base < n; base++) if (solovayStrassen(n, base)) liars++;
            double share = (double) liars / (n - 1);
            check(share <= 0.5, n + ": at most half the bases lie");
            if (share > worstShare) { worstShare = share; worstN = n; }
        }
        for (long n = 3; n < 3000; n += 2) if (isPrime(n)) for (long base = 1; base < n; base++) check(solovayStrassen(n, base), "a prime always passes");
        int caught = 0;
        for (long c : carmichael) { boolean found = false; for (long base = 2; base < c && !found; base++) if (!solovayStrassen(c, base)) found = true; if (found) caught++; }
        check(caught == carmichael.size(), "Solovay-Strassen catches every Carmichael number");
        StringJoiner cj = new StringJoiner(", ");
        for (int i = 0; i < Math.min(8, carmichael.size()); i++) cj.add(String.format("%,d", carmichael.get(i)));
        System.out.printf("primes: Fermat's test (a^(n-1) = 1 mod n for primes) is passed by every base sharing no factor with n by the %d Carmichael numbers below 100,000: %s, ... ; Solovay and Strassen's test (a^((n-1)/2) = the Jacobi symbol (a/n) mod n) is passed by every base for every odd prime below 3,000, and checked exhaustively for all %,d odd composites below 3,000: at most half the bases ever pass, the largest share being %.3f for n = %,d ; it catches all %d Carmichael numbers ; so 100 random rounds wrongly pass a composite with chance at most 2^-100%n",
                carmichael.size(), cj, composites, worstShare, worstN, caught);

        // ---- 5. a 1,024-bit RSA key ------------------------------------------------------------------------------------
        int[] t1 = {0}, t2 = {0};
        BigInteger pp = randomPrime(512, t1), qq = randomPrime(512, t2);
        BigInteger n = pp.multiply(qq), ph = pp.subtract(BigInteger.ONE).multiply(qq.subtract(BigInteger.ONE));
        BigInteger e = BigInteger.valueOf(65537);
        check(ph.gcd(e).equals(BigInteger.ONE), "e has an inverse");
        BigInteger d = e.modInverse(ph);
        check(pp.isProbablePrime(100) && qq.isProbablePrime(100), "Java's own test agrees the factors are prime");
        int ok = 0;
        long encMults = 0, decMults = 0;
        for (int i = 0; i < 100; i++) {
            BigInteger m = randomBelow(n);
            mults = 0;
            BigInteger c = power(m, e, n);
            encMults += mults;
            mults = 0;
            BigInteger m2 = power(c, d, n);
            decMults += mults;
            BigInteger sig = m.modPow(d, n);
            boolean verified = sig.modPow(e, n).equals(m);
            BigInteger forged = sig.add(BigInteger.ONE).mod(n);
            boolean forgedFails = !forged.modPow(e, n).equals(m);
            check(m2.equals(m) && verified && forgedFails, "round trip, signature, forgery");
            ok++;
        }
        System.out.printf("rsa: two random 512-bit primes, found after testing %d and %d odd candidates with 100 rounds each ; n = pq has %d bits (%d decimal digits) ; e = 65537, d computed from (p-1)(q-1) ; %d random messages encrypted and decrypted, signed and verified, and a signature changed by 1 always rejected ; average multiplications: encrypting %.0f, decrypting %.0f%n",
                t1[0], t2[0], n.bitLength(), n.toString().length(), ok, encMults / 100.0, decMults / 100.0);

        // ---- 6. breaking by factoring ---------------------------------------------------------------------------------
        StringJoiner fj = new StringJoiner(" ; ");
        long firstDivs = 0, lastDivs = 0;
        int rounds = 0;
        for (int bits = 20; bits <= 52; bits += 8) {
            int half = bits / 2;
            long f1, f2;
            do f1 = (1L << (half - 1)) + (next() >>> 40) % (1L << (half - 1)); while (!isPrime(f1));
            do f2 = (1L << (half - 1)) + (next() >>> 40) % (1L << (half - 1)); while (!isPrime(f2) || f2 == f1);
            long nn = f1 * f2, divs = 0, found = 0;
            for (long dd = 3; ; dd += 2) { divs++; if (nn % dd == 0) { found = dd; break; } }
            check(found == Math.min(f1, f2), "trial division finds the smaller factor");
            if (firstDivs == 0) firstDivs = divs; else rounds++;
            lastDivs = divs;
            fj.add(String.format("%d-bit n = %,d: %,d trial divisions", 64 - Long.numberOfLeadingZeros(nn), nn, divs));
        }
        System.out.printf("factor: n = pq with p and q of equal size, factored by dividing by 3, 5, 7, ... ; %s ; each 8 more bits multiplied the work by %.1f on average (the square root of 2^8 is 16) ; for the 1,024-bit n above, about 2^510 divisions, against about %.0f multiplications to encrypt%n",
                fj, Math.pow((double) lastDivs / firstDivs, 1.0 / rounds), encMults / 100.0);

        System.out.println("PublicKey: " + passed + " checks passed");
    }

    static long gcd(long x, long y) { while (y != 0) { long t = x % y; x = y; y = t; } return x; }
}
