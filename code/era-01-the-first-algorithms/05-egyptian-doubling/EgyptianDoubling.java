import java.math.BigInteger;
import java.util.*;
import java.util.function.BinaryOperator;

/**
 * Era 1, topic 5: Egyptian multiplication by doubling (the Rhind Mathematical Papyrus, copied by the scribe Ahmose
 * about 1550 BCE from an older text).
 *
 * HOW IT WORKS
 *   To multiply a by b with no times table, write two columns: 1 and b, then keep doubling both (2 and 2b, 4 and 4b,
 *   ...) while the left column stays at most a. Tick the rows whose left numbers add up to a, and add their right
 *   numbers. For 41 x 59: rows 1, 8 and 32 make 41, so the answer is 59 + 472 + 1888 = 2419. Only two skills are
 *   needed, doubling and adding, and about log2(a) rows. The ticked rows are the binary digits of a, though the
 *   scribes had no idea of base 2. Replace "add" by "multiply" and "double" by "square", and the same table computes
 *   powers: square-and-multiply, the method behind RSA.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Multiplies by doubling, printing the table for the papyrus-style example 41 x 59, and checks the method against
 *      ordinary multiplication on 500,000 random pairs, counting doublings and additions.
 *   2. Divides by doubling the divisor, as the scribes did.
 *   3. Runs the same algorithm on other operations (Stepanov's generic power): multiplication from addition,
 *      powers from multiplication, Fibonacci numbers from 2 x 2 matrices, and RSA decryption with modular powers.
 *   4. Finds the shortest addition chains for every number up to 128 and counts where doubling-and-adding is not the
 *      shortest way (the first is 15).
 *   Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java EgyptianDoubling.java
 *   Expected output: expected-output.txt in this folder.
 */
public class EgyptianDoubling {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // 1. Multiplication by doubling
    // ----------------------------------------------------------------------------------------------------

    /** One row of the doubling table: the multiplier (a power of two), the doubled value, and whether it is ticked. */
    record Row(long multiplier, long value, boolean ticked) {}

    /** The scribe's table for a x b: double until the multiplier would pass a, then tick rows from the bottom up. */
    static List<Row> table(long a, long b) {
        List<long[]> rows = new ArrayList<>();
        for (long m = 1, v = b; m <= a; m += m, v += v) rows.add(new long[]{m, v});   // doubling = adding to itself
        List<Row> out = new ArrayList<>();
        long left = a;
        boolean[] tick = new boolean[rows.size()];
        for (int i = rows.size() - 1; i >= 0; i--) {                       // the biggest multiplier that still fits
            if (rows.get(i)[0] <= left) { tick[i] = true; left -= rows.get(i)[0]; }
        }
        for (int i = 0; i < rows.size(); i++) out.add(new Row(rows.get(i)[0], rows.get(i)[1], tick[i]));
        return out;
    }

    /** a x b by doubling and adding; returns {product, doublings, additions}. */
    static long[] multiply(long a, long b) {
        List<Row> t = table(a, b);
        long sum = 0;
        int adds = -1;                                                       // the first ticked row needs no addition
        for (Row r : t) if (r.ticked()) { sum += r.value(); adds++; }
        return new long[]{sum, t.size() - 1, Math.max(adds, 0)};
    }

    /** The "Russian peasant" form: halve a and double b, adding b whenever a is odd. Same ticks, read from the top. */
    static long peasant(long a, long b) {
        long sum = 0;
        while (a > 0) {
            if ((a & 1) == 1) sum += b;
            a >>= 1;
            b += b;
        }
        return sum;
    }

    // ----------------------------------------------------------------------------------------------------
    // 2. Division by doubling the divisor
    // ----------------------------------------------------------------------------------------------------

    /** a / b: double b while it fits, then take rows from the biggest down. Returns {quotient, remainder, rows}. */
    static long[] divide(long a, long b) {
        List<long[]> rows = new ArrayList<>();
        for (long m = 1, v = b; v <= a; m += m, v += v) rows.add(new long[]{m, v});
        long q = 0, left = a;
        for (int i = rows.size() - 1; i >= 0; i--)
            if (rows.get(i)[1] <= left) { left -= rows.get(i)[1]; q += rows.get(i)[0]; }
        return new long[]{q, left, rows.size()};
    }

    // ----------------------------------------------------------------------------------------------------
    // 3. The same algorithm for any associative operation (Stepanov's generic power)
    // ----------------------------------------------------------------------------------------------------

    static int opCount;

    /** x op x op ... op x (n times, n >= 1), with about log2(n) steps: the Egyptian table with a general "add". */
    static <T> T power(T x, long n, BinaryOperator<T> op) {
        T result = null;
        while (true) {
            if ((n & 1) == 1) { result = result == null ? x : op.apply(result, x); if (result != x) opCount++; }
            n >>= 1;
            if (n == 0) return result;
            x = op.apply(x, x);                                                  // "double": combine x with itself
            opCount++;
        }
    }

    static long[][] matMul(long[][] a, long[][] b) {
        return new long[][]{
                {a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]},
                {a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]}};
    }

    // ----------------------------------------------------------------------------------------------------
    // 4. Shortest addition chains
    // ----------------------------------------------------------------------------------------------------

    /** Steps the doubling method needs to reach n from 1: (bits - 1) doublings plus (ones - 1) additions. */
    static int binarySteps(long n) {
        return 63 - Long.numberOfLeadingZeros(n) + Long.bitCount(n) - 1;
    }

    /** The chain the doubling method builds, read from the top bit: double, and add 1 where the bit is 1. */
    static List<Long> binaryChain(long n) {
        List<Long> c = new ArrayList<>(List.of(1L));
        long v = 1;
        for (int bit = 62 - Long.numberOfLeadingZeros(n); bit >= 0; bit--) {
            v += v;
            c.add(v);
            if ((n >> bit & 1) == 1) { v += 1; c.add(v); }
        }
        return c;
    }

    /** The shortest addition chain for n (each number the sum of two earlier ones), by iterative deepening. */
    static int[] shortestChain(int n) {
        if (n == 1) return new int[]{1};
        for (int len = 1; ; len++) {
            int[] chain = new int[len + 1];
            chain[0] = 1;
            if (search(chain, 1, len, n)) return chain;
        }
    }

    static boolean search(int[] chain, int k, int len, int n) {
        int last = chain[k - 1];
        if (last == n) return k == len + 1;
        if (k > len) return false;
        if ((long) last << (len - k + 1) < n) return false;                   // even doubling every time falls short
        for (int i = k - 1; i >= 0; i--) {
            for (int j = i; j >= 0; j--) {
                int next = chain[i] + chain[j];
                if (next <= last) break;                                       // keep the chain increasing
                if (next > n) continue;
                chain[k] = next;
                if (search(chain, k + 1, len, n)) return true;
            }
        }
        return false;
    }

    // ----------------------------------------------------------------------------------------------------

    public static void main(String[] args) {
        // 1. the papyrus-style example
        long a = 41, b = 59;
        for (Row r : table(a, b)) System.out.printf("row %d x %d: %d %d%s%n", a, b, r.multiplier(), r.value(), r.ticked() ? " ticked" : "");
        long[] m = multiply(a, b);
        check(m[0] == a * b, "41 x 59 = 2419");
        System.out.printf("multiply %d x %d = %d: doublings=%d additions=%d; repeated addition would take %d additions%n", a, b, m[0], m[1], m[2], a - 1);
        Random rnd = new Random(1550);
        long sumOps = 0, sumRepeat = 0;
        int trials = 500_000;
        for (int i = 0; i < trials; i++) {
            long x = rnd.nextLong(1, 1_000_001), y = rnd.nextLong(1, 1_000_001);
            long[] r = multiply(x, y);
            check(r[0] == x * y, "doubling = multiplication");
            check(peasant(x, y) == x * y, "halving and doubling = multiplication");
            check(r[1] + r[2] == binarySteps(x), "steps = binary length + ones - 2");
            sumOps += r[1] + r[2];
            sumRepeat += x - 1;
        }
        System.out.printf("multiplycheck: %d random pairs below 1,000,000 multiplied by doubling and by halving-and-doubling; average %.2f doublings and additions, against an average of %,.0f additions by repeating%n",
                trials, (double) sumOps / trials, (double) sumRepeat / trials);
        for (long n : new long[]{10, 41, 100, 1_000, 1_000_000}) {
            System.out.printf("steps %d: doubling-and-adding=%d repeated-adding=%d%n", n, binarySteps(n), n - 1);
        }

        // 2. division by doubling the divisor
        for (long[] q : new long[][]{{1000, 7}, {2419, 59}, {696, 8}}) {
            long[] r = divide(q[0], q[1]);
            check(r[0] == q[0] / q[1] && r[1] == q[0] % q[1], "division by doubling");
            System.out.printf("divide %d / %d: quotient=%d remainder=%d rows=%d%n", q[0], q[1], r[0], r[1], r[2]);
        }
        for (int i = 0; i < 200_000; i++) {
            long x = rnd.nextLong(0, 10_000_000), y = rnd.nextLong(1, 5_000);
            long[] r = divide(x, y);
            check(r[0] == x / y && r[1] == x % y, "division by doubling, random");
        }

        // 3. the generic power
        opCount = 0;
        long prod = power(59L, 41, Long::sum);
        check(prod == 2419, "power with + is multiplication");
        System.out.printf("generic + : 59 added to itself 41 times = %d in %d additions%n", prod, opCount);
        opCount = 0;
        BigInteger p3 = power(BigInteger.valueOf(3), 41, BigInteger::multiply);
        check(p3.equals(BigInteger.valueOf(3).pow(41)), "power with x is exponentiation");
        System.out.printf("generic x : 3^41 = %s in %d multiplications (repeating would take 40)%n", p3, opCount);
        opCount = 0;
        long[][] fibM = power(new long[][]{{1, 1}, {1, 0}}, 90, EgyptianDoubling::matMul);
        long f0 = 0, f1 = 1;
        for (int i = 0; i < 90; i++) { long t = f0 + f1; f0 = f1; f1 = t; }
        check(fibM[0][1] == f0, "Fibonacci by matrix powers");
        System.out.printf("generic matrix : Fibonacci number 90 = %d in %d matrix multiplications (adding one by one takes 89 additions)%n", fibM[0][1], opCount);
        // RSA with the textbook key n = 61 x 53 = 3233, e = 17, d = 2753
        BigInteger N = BigInteger.valueOf(3233), message = BigInteger.valueOf(65);
        BigInteger c = message.modPow(BigInteger.valueOf(17), N);
        opCount = 0;
        BigInteger back = power(c, 2753, (u, v) -> u.multiply(v).mod(N));
        check(back.equals(message), "RSA decryption by square-and-multiply");
        check(c.equals(BigInteger.valueOf(2790)), "65^17 mod 3233 = 2790");
        System.out.printf("rsa: n=3233 e=17 d=2753: 65 encrypts to %s; decrypting %s^2753 mod 3233 takes %d multiplications instead of 2752, and gives back %s%n", c, c, opCount, back);
        BigInteger big = new BigInteger(2048, new Random(1977)).setBit(2047);
        int bigOps = big.bitLength() - 1 + big.bitCount() - 1;
        System.out.printf("rsa-2048: a random 2048-bit exponent needs %d squarings and %d multiplications, %d in all%n", big.bitLength() - 1, big.bitCount() - 1, bigOps);

        // 4. shortest addition chains
        int notOptimal = 0, first = 0;
        StringJoiner list = new StringJoiner(" ");
        for (int n = 1; n <= 128; n++) {
            int[] ch = shortestChain(n);
            int best = ch.length - 1;
            for (int i = 1; i < ch.length; i++) {                              // the chain really is a chain
                boolean ok = false;
                for (int x = 0; x < i && !ok; x++) for (int y = x; y < i && !ok; y++) ok = ch[x] + ch[y] == ch[i];
                check(ok, "each step adds two earlier numbers");
            }
            check(best <= binarySteps(n), "never longer than doubling");
            if (best < binarySteps(n)) {
                notOptimal++;
                if (first == 0) first = n;
                if (list.length() < 60) list.add(Integer.toString(n));
            }
        }
        int[] c15 = shortestChain(15);
        StringJoiner c15s = new StringJoiner(", ");
        for (int x : c15) c15s.add(Integer.toString(x));
        List<Long> b15 = binaryChain(15);
        check(b15.size() - 1 == binarySteps(15) && b15.get(b15.size() - 1) == 15, "the doubling chain for 15");
        StringJoiner b15s = new StringJoiner(", ");
        for (long x : b15) b15s.add(Long.toString(x));
        System.out.printf("chain 15: shortest %s (%d steps); doubling and adding needs %d (%s)%n", c15s, c15.length - 1, binarySteps(15), b15s);
        System.out.printf("chains 1-128: doubling and adding is not the shortest for %d numbers; the first are %s%n", notOptimal, list);
        check(first == 15, "15 is the first number where doubling is beaten");

        System.out.printf("EgyptianDoubling: %d checks passed%n", passed);
    }
}
