import java.math.BigInteger;
import java.util.*;

/**
 * Era 4, topic 5: Gödel's numbering (1931).
 *
 * HOW IT WORKS
 *   Gödel gave each basic sign of his formal system a number:
 *       "0" 1   "f" (the next number) 3   "~" (not) 5   "v" (or) 7   "P" (for all) 9   "(" 11   ")" 13
 *   and each variable a prime above 13 (or a power of one, for variables of higher type). A formula, a string of signs
 *   with numbers n1, n2, ..., nk, becomes the single number 2^n1 * 3^n2 * 5^n3 * ... * pk^nk. Because a number
 *   factors into primes in only one way, the formula can be read back from its number. A proof, a list of formulas,
 *   is coded the same way, with the formulas' numbers as the exponents. Then "x is the number of a proof of the
 *   formula numbered y" is a statement about whole numbers that can be checked with loops of known length (Gödel's
 *   "primitive recursive" functions), so arithmetic can talk about its own proofs. With a substitution trick
 *   (the diagonal) he wrote a formula that says, in effect, "the formula with this number is not provable", where
 *   the number is its own.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Gödel's sign table, and the numbers of a few formulas, from "f0" (the number 1, coded as 24) upward.
 *   2. Codes 10,000 random formulas and reads every one back by factoring; all numbers are different.
 *   3. The size of a proof's number, which is too large to write down.
 *   4. Reading an exponent back with loops of fixed length only (no open-ended search), checked against division
 *      for every number up to 200,000 and the first ten primes.
 *   5. The diagonal trick with a modern numbering of English sentences: a sentence G that names, by a number, a
 *      recipe whose result is G itself.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java GodelNumbering.java
 *   Expected output: expected-output.txt in this folder.
 */
public class GodelNumbering {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- 1. Gödel's signs ------------------------------------------------------------------------------------------
    static final String[] SIGNS = {"0", "f", "~", "v", "P", "(", ")"};
    static final int[] SIGN_NUM = {1, 3, 5, 7, 9, 11, 13};
    static final String[] VARS = {"x1", "y1", "z1", "x2", "y2", "z2"};
    static final int[] VAR_NUM = {17, 19, 23, 17 * 17, 19 * 19, 23 * 23};

    static final int[] PRIMES = firstPrimes(40);

    static int[] firstPrimes(int k) {
        int[] p = new int[k];
        int n = 0;
        for (int c = 2; n < k; c++) {
            boolean prime = true;
            for (int i = 0; i < n && p[i] * p[i] <= c; i++) if (c % p[i] == 0) { prime = false; break; }
            if (prime) p[n++] = c;
        }
        return p;
    }

    /** The sign numbers of a formula written with the signs above and the variables x1, y1, z1, x2, y2, z2. */
    static List<Integer> signs(String formula) {
        List<Integer> out = new ArrayList<>();
        for (int i = 0; i < formula.length(); ) {
            boolean hit = false;
            for (int v = 0; v < VARS.length && !hit; v++)
                if (formula.startsWith(VARS[v], i)) { out.add(VAR_NUM[v]); i += 2; hit = true; }
            for (int s = 0; s < SIGNS.length && !hit; s++)
                if (formula.startsWith(SIGNS[s], i)) { out.add(SIGN_NUM[s]); i += 1; hit = true; }
            if (!hit) throw new IllegalArgumentException("unknown sign at " + i + " in " + formula);
        }
        return out;
    }

    /** Gödel's number of a sequence: 2^n1 * 3^n2 * 5^n3 * ... */
    static BigInteger godel(List<Integer> seq) {
        BigInteger g = BigInteger.ONE;
        for (int i = 0; i < seq.size(); i++) g = g.multiply(BigInteger.valueOf(PRIMES[i]).pow(seq.get(i)));
        return g;
    }

    /** Read the sequence back: divide out 2, then 3, then 5, ... counting how often each divides. */
    static List<Integer> decode(BigInteger g) {
        List<Integer> seq = new ArrayList<>();
        for (int i = 0; !g.equals(BigInteger.ONE); i++) {
            BigInteger p = BigInteger.valueOf(PRIMES[i]);
            int e = 0;
            while (g.mod(p).signum() == 0) { g = g.divide(p); e++; }
            seq.add(e);
        }
        return seq;
    }

    static String describe(BigInteger g) {
        String s = g.toString();
        return s.length() <= 24 ? s : s.length() + " digits, " + s.substring(0, 6) + "..." + s.substring(s.length() - 6);
    }

    // ---- 4. an exponent read back with loops of fixed length only ----------------------------------------------------
    /** The exponent of p in x (x >= 1), using only for-loops whose length is fixed before they start. */
    static long exponentBounded(long p, long x) {
        long e = 0;
        long power = 1;
        for (int k = 1; k <= 63; k++) {                                 // 63 tries always suffice for a long
            power = power <= Long.MAX_VALUE / p ? power * p : 0;          // p^k, or 0 once it no longer fits
            if (power != 0 && power <= x && x % power == 0) e = k;
        }
        return e;
    }

    static long exponentByDivision(long p, long x) {
        long e = 0;
        while (x % p == 0) { x /= p; e++; }
        return e;
    }

    // ---- 5. the diagonal trick with sentences --------------------------------------------------------------------------
    /** Printable ASCII, space to tilde, as the digits 1 to 95 of a bijective base-95 numbering of sentences. */
    static BigInteger number(String s) {
        BigInteger n = BigInteger.ZERO, B = BigInteger.valueOf(95);
        for (char c : s.toCharArray()) {
            if (c < 32 || c > 126) throw new IllegalArgumentException("not printable ASCII");
            n = n.multiply(B).add(BigInteger.valueOf(c - 31));
        }
        return n;
    }

    static String sentence(BigInteger n) {
        StringBuilder sb = new StringBuilder();
        BigInteger B = BigInteger.valueOf(95);
        while (n.signum() > 0) {
            int d = n.subtract(BigInteger.ONE).mod(B).intValue() + 1;
            sb.append((char) (d + 31));
            n = n.subtract(BigInteger.valueOf(d)).divide(B);
        }
        return sb.reverse().toString();
    }

    /** diag(n): take sentence number n and write the number n in place of every at-sign. */
    static String diag(BigInteger n) {
        return sentence(n).replace("@", n.toString());
    }

    static long seed = 1931L;

    static int rnd(int n) {                                           // a fixed linear congruential generator
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) Long.remainderUnsigned(seed >>> 33, n);
    }

    public static void main(String[] args) {
        // ---- 1. signs and formulas ------------------------------------------------------------------------------------
        StringJoiner tab = new StringJoiner(" ");
        for (int s = 0; s < SIGNS.length; s++) tab.add(SIGNS[s] + "=" + SIGN_NUM[s]);
        System.out.printf("signs: %s ; variables x1=%d y1=%d z1=%d (primes above 13) ; x2=%d y2=%d z2=%d (their squares, for the next type)%n",
                tab, VAR_NUM[0], VAR_NUM[1], VAR_NUM[2], VAR_NUM[3], VAR_NUM[4], VAR_NUM[5]);
        String[] formulas = {"0", "f0", "ff0", "x2(x1)", "~(x2(x1))", "x1P(x2(x1))"};
        BigInteger[] fnum = new BigInteger[formulas.length];
        for (int k = 0; k < formulas.length; k++) {
            List<Integer> sg = signs(formulas[k]);
            BigInteger g = godel(sg);
            fnum[k] = g;
            check(decode(g).equals(sg), "read back " + formulas[k]);
            StringJoiner sj = new StringJoiner(" "), pw = new StringJoiner(" * ");
            for (int i = 0; i < sg.size(); i++) { sj.add(String.valueOf(sg.get(i))); pw.add(PRIMES[i] + "^" + sg.get(i)); }
            System.out.printf("formula: %s ; signs %s ; %s = %s%n", formulas[k], sj, pw, describe(g));
        }
        check(fnum[1].equals(BigInteger.valueOf(24)) && fnum[2].equals(BigInteger.valueOf(1080)), "f0 is 24 and ff0 is 1080");

        // ---- 2. ten thousand random formulas ---------------------------------------------------------------------------
        int trials = 10000;
        Set<BigInteger> seen = new HashSet<>();
        int maxDigits = 0;
        int[] all = new int[SIGN_NUM.length + VAR_NUM.length];
        for (int i = 0; i < SIGN_NUM.length; i++) all[i] = SIGN_NUM[i];
        for (int i = 0; i < VAR_NUM.length; i++) all[SIGN_NUM.length + i] = VAR_NUM[i];
        Set<List<Integer>> seqs = new HashSet<>();
        for (int t = 0; t < trials; t++) {
            int len = 1 + rnd(8);
            List<Integer> sq = new ArrayList<>();
            for (int i = 0; i < len; i++) sq.add(all[rnd(all.length)]);
            BigInteger g = godel(sq);
            check(decode(g).equals(sq), "random formula read back");
            if (seqs.add(sq)) check(seen.add(g), "different formulas, different numbers");
            maxDigits = Math.max(maxDigits, g.toString().length());
        }
        System.out.printf("roundtrip: %d random strings of 1 to 8 signs (%d different) coded and factored back: every one recovered, no two different strings share a number ; the largest number has %d digits%n",
                trials, seqs.size(), maxDigits);

        // ---- 3. the number of a proof -------------------------------------------------------------------------------------
        // a list of formulas f0, ff0, x2(x1) is coded as 2^#f0 * 3^#ff0 * 5^#(x2(x1)); count its digits with logarithms
        BigInteger e3 = fnum[3];
        // digits of 5^e3 = e3 * log10(5): e3 has hundreds of digits, so work with its leading digits and length
        String es = e3.toString();
        double lead = Double.parseDouble(es.substring(0, 15)) / 1e14;      // e3 = lead * 10^(len-1)
        double logDigits = Math.log10(lead * Math.log10(5)) + (es.length() - 1);
        check(logDigits > 90, "the proof's number has more than 10^90 digits");
        System.out.printf("proof: the list f0, ff0, x2(x1) is coded as 2^24 * 3^1080 * 5^(the number of x2(x1)) ; its last factor alone has about 10^%.1f digits, far too many to write down%n",
                logDigits);

        // ---- 4. exponents read back with fixed-length loops -------------------------------------------------------------
        long agreed = 0;
        for (int i = 0; i < 10; i++)
            for (long x = 1; x <= 200000; x++) {
                check(exponentBounded(PRIMES[i], x) == exponentByDivision(PRIMES[i], x), "bounded loops agree with division");
                agreed++;
            }
        System.out.printf("bounded: the exponent of p in x found with loops of fixed length (63 tries) agrees with repeated division for x = 1 to 200000 and the first 10 primes: %d cases%n", agreed);

        // ---- 5. the diagonal -----------------------------------------------------------------------------------------------
        String A = "Put the number @ in place of every at-sign in sentence number @: the sentence you get is not provable.";
        BigInteger a = number(A);
        check(sentence(a).equals(A), "sentence numbering reads back");
        String G = A.replace("@", a.toString());
        check(diag(a).equals(G), "diag of A's number is G");
        BigInteger g = number(G);
        check(!g.equals(a) && !G.contains(g.toString()), "G does not contain its own number");
        check(G.contains(a.toString()), "G contains A's number");
        System.out.printf("diag: A = \"%s\" (%d characters) ; its number has %d digits ; G is A with that number written in place of each at-sign (%d characters, number of %d digits) ; following G's recipe gives G itself ; G = \"%s\"%n",
                A, A.length(), a.toString().length(), G.length(), g.toString().length(), G);

        System.out.println("GodelNumbering: " + passed + " checks passed");
    }
}
