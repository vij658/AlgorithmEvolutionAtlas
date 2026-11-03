import java.math.BigInteger;
import java.util.*;

/**
 * Era 9, topic 1: Fully homomorphic encryption (Gentry, 2009), in the integer version of van Dijk, Gentry, Halevi and
 * Vaikuntanathan (2009-2010).
 *
 * HOW IT WORKS
 *   The secret key is a large odd number p. To encrypt one bit m, pick a large random q and a small random r and send
 *       c = p*q + 2*r + m.
 *   To decrypt, reduce c modulo p into the range (-p/2, p/2]; that leaves the "noise" 2r + m, whose last bit is m.
 *   Adding two ciphertexts adds the noises: (2r1 + m1) + (2r2 + m2) has last bit m1 XOR m2. Multiplying them
 *   multiplies the noises: its last bit is m1 AND m2. XOR and AND together build any circuit, so any computation can
 *   be done on ciphertexts without the key.
 *   The catch is the noise. Additions add noise bits slowly; each multiplication roughly doubles the number of noise
 *   bits. Once the noise passes p/2, reduction modulo p wraps around and decryption gives garbage. The scheme is
 *   "somewhat homomorphic": good for circuits of limited depth. Gentry's bootstrapping evaluates the decryption
 *   circuit itself on an encrypted copy of the key, which resets the noise; that needs far larger numbers than this
 *   program uses, so the program measures the limit instead.
 *   Security rests on the approximate-gcd problem: given many near-multiples p*q_i + r_i of a hidden p, find p. With
 *   no noise, one gcd would reveal p at once.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A secret p of 512 bits; every bit pattern of XOR and AND on encrypted bits, checked.
 *   2. Noise growth: the noise's size in bits after 1, 2, 3 ... levels of multiplication, until decryption fails.
 *   3. A 4-bit adder (ripple carry, 7 gates per bit) run on encrypted inputs for all 256 pairs of 4-bit numbers.
 *   4. A public key: 30 encryptions of zero; anyone can encrypt by adding a random subset of them.
 *   5. Why the noise matters: without it, the gcd of two ciphertexts of zero is p (or a multiple); with it, the gcd
 *      is 1 or tiny.
 *   6. A small example with a 4-digit key for the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java FullyHomomorphic.java
 *   Expected output: expected-output.txt in this folder.
 */
public class FullyHomomorphic {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final Random RND = new Random(2009);

    /** A secret key: an odd number with exactly `bits` bits. */
    static BigInteger key(int bits) {
        BigInteger p = new BigInteger(bits - 1, RND).setBit(bits - 1).setBit(0);
        return p;
    }

    /** c = p*q + 2r + m, with q of qBits bits and r of rBits bits (r may be negative). */
    static BigInteger enc(BigInteger p, int m, int qBits, int rBits) {
        BigInteger q = new BigInteger(qBits, RND);
        BigInteger r = new BigInteger(rBits, RND);
        if (RND.nextBoolean()) r = r.negate();
        return p.multiply(q).add(r.shiftLeft(1)).add(BigInteger.valueOf(m));
    }

    /** c reduced into (-p/2, p/2]: the noise. */
    static BigInteger noise(BigInteger p, BigInteger c) {
        BigInteger r = c.mod(p);
        if (r.compareTo(p.shiftRight(1)) > 0) r = r.subtract(p);
        return r;
    }

    static int dec(BigInteger p, BigInteger c) {
        return noise(p, c).testBit(0) ? 1 : 0; // testBit works for negative numbers in two's complement: odd stays odd
    }

    static BigInteger xor(BigInteger a, BigInteger b) { return a.add(b); }

    static BigInteger and(BigInteger a, BigInteger b) { return a.multiply(b); }

    /** NOT x = x XOR 1, where 1 is the trivial (noise-free) encryption of 1. */
    static BigInteger not(BigInteger a) { return a.add(BigInteger.ONE); }

    static int noiseBits(BigInteger p, BigInteger c) { return noise(p, c).abs().bitLength(); }

    public static void main(String[] args) {
        // ---- 1. the scheme -------------------------------------------------------------------------------------------
        final int P_BITS = 512, Q_BITS = 1024, R_BITS = 24;
        BigInteger p = key(P_BITS);
        int trials = 0;
        for (int t = 0; t < 200; t++) {
            for (int a = 0; a < 2; a++) for (int b = 0; b < 2; b++) {
                BigInteger ca = enc(p, a, Q_BITS, R_BITS), cb = enc(p, b, Q_BITS, R_BITS);
                check(dec(p, ca) == a && dec(p, cb) == b, "decryption");
                check(dec(p, xor(ca, cb)) == (a ^ b), "XOR on ciphertexts");
                check(dec(p, and(ca, cb)) == (a & b), "AND on ciphertexts");
                check(dec(p, not(ca)) == 1 - a, "NOT on ciphertexts");
                trials++;
            }
        }
        BigInteger c0 = enc(p, 1, Q_BITS, R_BITS);
        System.out.printf("scheme: secret p of %d bits ; c = p*q + 2r + m with q of %d bits and noise r of %d bits ; ciphertext of %d bits ; %d XOR, AND and NOT pairs on encrypted bits all decrypt correctly%n",
                P_BITS, Q_BITS, R_BITS, c0.bitLength(), trials);

        // ---- 2. noise growth -----------------------------------------------------------------------------------------
        // Multiply ciphertexts of 1 together in a balanced tree: level L multiplies two level-(L-1) results.
        StringJoiner nj = new StringJoiner(" ; ");
        BigInteger[] level = new BigInteger[64];
        for (int i = 0; i < level.length; i++) level[i] = enc(p, 1, Q_BITS, R_BITS);
        int maxOk = 0, failAt = -1;
        int addBits = noiseBits(p, xor(level[0], level[1]));
        nj.add(String.format("fresh: %d bits", noiseBits(p, level[0])));
        for (int L = 1; L <= 6 && level.length >= 2; L++) {
            BigInteger[] next = new BigInteger[level.length / 2];
            for (int i = 0; i < next.length; i++) next[i] = and(level[2 * i], level[2 * i + 1]);
            level = next;
            int nb = noiseBits(p, level[0]);
            boolean ok = dec(p, level[0]) == 1;
            boolean allOk = true;
            for (BigInteger c : level) allOk &= dec(p, c) == 1;
            if (allOk) maxOk = L;
            else if (failAt < 0) failAt = L;
            nj.add(String.format("depth %d: %s bits%s", L, ok ? String.valueOf(nb) : "over " + (P_BITS - 1), allOk ? "" : " (decryption fails)"));
            if (!allOk) break;
        }
        check(maxOk >= 3 && failAt > maxOk, "the noise limit is reached after a few levels of multiplication");
        // the measured limit agrees with the estimate: noise bits roughly double per level, failure once they reach p's
        int est = 0;
        for (double b = R_BITS + 1; b < P_BITS - 1; b = 2 * b + 1) est++;
        check(Math.abs(est - maxOk) <= 1, "measured depth matches doubling estimate");
        // a long chain of additions barely grows the noise
        BigInteger sum = enc(p, 0, Q_BITS, R_BITS);
        for (int i = 0; i < 1000; i++) sum = xor(sum, enc(p, i % 2, Q_BITS, R_BITS));
        int sumBits = noiseBits(p, sum);
        check(dec(p, sum) == 0, "1000 additions still decrypt (500 ones: even)");
        check(sumBits <= R_BITS + 12, "additions add a few bits");
        System.out.printf("noise: secret p of %d bits, decryption works while the noise stays under p/2 ; %s ; deepest working multiplication depth %d, doubling estimate %d ; one addition: %d bits ; after 1,000 additions: %d bits%n",
                P_BITS, nj, maxOk, est, addBits, sumBits);

        // ---- 3. an encrypted 4-bit adder -------------------------------------------------------------------------
        int pairs = 0, maxDepthNoise = 0;
        for (int x = 0; x < 16; x++) for (int y = 0; y < 16; y++) {
            BigInteger[] cx = new BigInteger[4], cy = new BigInteger[4];
            for (int i = 0; i < 4; i++) { cx[i] = enc(p, (x >> i) & 1, Q_BITS, R_BITS); cy[i] = enc(p, (y >> i) & 1, Q_BITS, R_BITS); }
            BigInteger carry = BigInteger.ZERO; // trivial encryption of 0
            BigInteger[] s = new BigInteger[5];
            for (int i = 0; i < 4; i++) {
                BigInteger t = xor(cx[i], cy[i]);
                s[i] = xor(t, carry);
                carry = xor(and(cx[i], cy[i]), and(carry, t)); // majority: ab + c(a XOR b), the two terms never both 1
            }
            s[4] = carry;
            int got = 0;
            for (int i = 0; i < 5; i++) got |= dec(p, s[i]) << i;
            check(got == x + y, "encrypted addition " + x + " + " + y);
            maxDepthNoise = Math.max(maxDepthNoise, noiseBits(p, s[4]));
            pairs++;
        }
        System.out.printf("adder: 4-bit ripple-carry adder on encrypted bits ; %d pairs of 4-bit numbers, all sums correct ; noise in the final carry up to %d bits of %d%n",
                pairs, maxDepthNoise, P_BITS);

        // ---- 4. a public key --------------------------------------------------------------------------------------
        final int TAU = 30;
        BigInteger[] pk = new BigInteger[TAU];
        for (int i = 0; i < TAU; i++) pk[i] = enc(p, 0, Q_BITS, R_BITS);
        int pkOk = 0;
        for (int t = 0; t < 400; t++) {
            int m = t & 1;
            BigInteger c = BigInteger.valueOf(m).add(BigInteger.valueOf(2L * RND.nextInt(1 << 10)));
            for (int i = 0; i < TAU; i++) if (RND.nextBoolean()) c = c.add(pk[i]);
            check(dec(p, c) == m, "public-key encryption decrypts");
            pkOk++;
        }
        System.out.printf("public: public key = %d encryptions of 0 ; encrypt m as m + 2*(small) + a random subset sum of them ; %d encryptions by subset sum, all decrypt correctly%n",
                TAU, pkOk);

        // ---- 5. why the noise matters ----------------------------------------------------------------------------------
        BigInteger z1 = p.multiply(new BigInteger(Q_BITS, RND)), z2 = p.multiply(new BigInteger(Q_BITS, RND));
        BigInteger g0 = z1.gcd(z2);
        check(g0.mod(p).signum() == 0, "without noise the gcd is a multiple of p");
        int smallFactorsRemoved = 0;
        BigInteger g = g0;
        for (int d = 2; d < 1000; d++) while (g.mod(BigInteger.valueOf(d)).signum() == 0 && g.divide(BigInteger.valueOf(d)).mod(p).signum() == 0) { g = g.divide(BigInteger.valueOf(d)); smallFactorsRemoved++; }
        check(g.equals(p), "removing small factors from the gcd gives p exactly");
        BigInteger n1 = pk[0], n2 = pk[1];
        BigInteger gn = n1.gcd(n2);
        check(gn.bitLength() < 32, "with noise the gcd is tiny");
        System.out.printf("gcd: two ciphertexts of 0 without noise: their gcd has %d bits and, after removing %d small factor%s, equals p ; with noise: gcd = %s (%d bits), and p stays hidden%n",
                g0.bitLength(), smallFactorsRemoved, smallFactorsRemoved == 1 ? "" : "s", gn, gn.bitLength());

        // ---- 6. the widget's small example ------------------------------------------------------------------------------
        // Key p = 1009 (odd, prime), noise r in [-4, 4], q in [1000, 9999]: two bits, XOR and AND, by hand.
        BigInteger wp = BigInteger.valueOf(1009);
        long[][] ex = {{1, 4321, 3}, {1, 7777, -2}};
        BigInteger wa = wp.multiply(BigInteger.valueOf(ex[0][1])).add(BigInteger.valueOf(2 * ex[0][2] + ex[0][0]));
        BigInteger wb = wp.multiply(BigInteger.valueOf(ex[1][1])).add(BigInteger.valueOf(2 * ex[1][2] + ex[1][0]));
        BigInteger ws = xor(wa, wb), wm = and(wa, wb);
        check(dec(wp, wa) == 1 && dec(wp, wb) == 1 && dec(wp, ws) == 0 && dec(wp, wm) == 1, "widget example decrypts");
        // how many ANDs of fresh ciphertexts fit under 1009/2 with |noise| <= 9
        int wDepth = 0;
        for (long nmax = 9; nmax * 9 <= 504; nmax *= 9) wDepth++;
        System.out.printf("widget: p = %s ; a = %s*%d + 2*(%d) + 1 = %s ; b = %s*%d + 2*(%d) + 1 = %s ; a + b = %s, noise %s, decrypts to %d ; a * b = %s, noise %s, decrypts to %d ; with fresh noise up to 9, products of %d fresh ciphertexts always fit under p/2%n",
                wp, wp, ex[0][1], ex[0][2], wa, wp, ex[1][1], ex[1][2], wb, ws, noise(wp, ws), dec(wp, ws), wm, noise(wp, wm), dec(wp, wm), wDepth + 1);

        System.out.println("FullyHomomorphic: " + passed + " checks passed");
    }
}
