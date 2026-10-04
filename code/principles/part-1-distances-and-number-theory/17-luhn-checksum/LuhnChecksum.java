import java.util.*;

/**
 * Entry 17 of the principles catalog (Part 1): Luhn checksum
 *
 * HOW IT WORKS
 *   From the right, double every second digit (subtracting 9 if the result exceeds 9) and add everything; a
 *   valid number sums to a multiple of 10. It catches every single-digit error and almost every swap of
 *   adjacent digits (all except 09 <-> 90). It is not protection against tampering.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LuhnChecksum.java
 *   Expected: the output in expected-output.txt, ending "LuhnChecksum: 31709 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class LuhnChecksum {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static boolean luhn(String digits) {
        int sum = 0;
        boolean dbl = false;
        for (int i = digits.length() - 1; i >= 0; i--) {
            char ch = digits.charAt(i);
            if (ch == ' ') continue;
            int d = ch - '0';
            if (dbl) { d *= 2; if (d > 9) d -= 9; }
            sum += d;
            dbl = !dbl;
        }
        return sum % 10 == 0;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 18 (kahan-and-neumaier-summation), entry 19 (comparing-floats-and-money), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    // ---------- Luhn helpers ----------
    static String withCheckDigit(Random rnd, int bodyLen) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < bodyLen; i++) sb.append((char) ('0' + rnd.nextInt(10)));
        String body = sb.toString();
        for (char c = '0'; c <= '9'; c++) if (luhn(body + c)) return body + c;
        throw new IllegalStateException("unreachable: exactly one check digit works");
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java LuhnChecksum.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // Luhn
        check(luhn("79927398713") && !luhn("79927398710"), "Luhn sample");
        check(luhn("4111 1111 1111 1111") && !luhn("4111 1111 1111 1112"), "Luhn test card");
        for (int t = 0; t < 200; t++) {
            String num = withCheckDigit(rnd, 15);
            check(luhn(num), "generated number is valid");
            for (int i = 0; i < num.length(); i++)
                for (char d = '0'; d <= '9'; d++)
                    if (d != num.charAt(i)) check(!luhn(num.substring(0, i) + d + num.substring(i + 1)), "every single-digit error caught");
            for (int i = 0; i + 1 < num.length(); i++) {
                char x = num.charAt(i), y = num.charAt(i + 1);
                if (x == y) continue;
                String swapped = num.substring(0, i) + y + x + num.substring(i + 2);
                boolean zeroNine = (x == '0' && y == '9') || (x == '9' && y == '0');
                check(luhn(swapped) == zeroNine, "adjacent swap caught except 09/90");
            }
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(7));
        System.out.println("LuhnChecksum: " + passed + " checks passed");
    }
}
