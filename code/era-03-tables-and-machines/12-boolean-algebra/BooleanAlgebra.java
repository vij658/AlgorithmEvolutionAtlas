import java.util.*;

/**
 * Era 3, topic 12: Boole's algebra of logic (The Mathematical Analysis of Logic, 1847; The Laws of Thought, 1854);
 * Shannon's relays (1937).
 *
 * HOW IT WORKS
 *   Let x stand for a class of things (men), and xy for the things in both x and y (mortal men). Then xx = x: selecting
 *   men from men gives men. As an equation of ordinary algebra, x^2 = x has only the roots 0 and 1, so Boole's symbols
 *   behave like numbers that can only be 0 (nothing) or 1 (everything). 1 - x is "not x", and "All x are y" says that
 *   nothing is x without being y: x(1 - y) = 0. Reasoning becomes algebra on 0 and 1: substitute, multiply, solve.
 *   Any expression in x can be expanded as f(1) x + f(0)(1 - x), which is a truth table written as a formula.
 *   Shannon (1937) saw that a relay contact is also either closed (1) or open (0): contacts in series give xy, in
 *   parallel x + y - xy, so circuits can be designed and simplified by Boole's algebra.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Finds the solutions of x^2 = x among whole numbers and fractions: only 0 and 1.
 *   2. Checks Boole's expansion on every function of two and three variables.
 *   3. Tests all 256 forms of the categorical syllogism by algebra over 0 and 1, and counts the valid ones, with and
 *      without assuming that every class has members.
 *   4. Builds a full adder and a 16-bit adder from Boolean expressions and checks them on every input.
 *   5. Simplifies a switching circuit by Boole's laws and counts the contacts saved.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BooleanAlgebra.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BooleanAlgebra {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- syllogisms -------------------------------------------------------------------------------------------------
    // three classes S, M, P; a "world" says which of the 8 regions (s, m, p each 0 or 1) have members
    static boolean region(int world, int s, int m, int p) { return ((world >> (s * 4 + m * 2 + p)) & 1) == 1; }

    /** Is "X are Y" of the given type true? type: A all, E no, I some, O some not. x, y are 0 = S, 1 = M, 2 = P. */
    static boolean holds(int world, char type, int x, int y) {
        boolean someXY = false, someXnotY = false;
        for (int r = 0; r < 8; r++) {
            if (((world >> r) & 1) == 0) continue;
            int[] bits = {(r >> 2) & 1, (r >> 1) & 1, r & 1};    // s, m, p
            if (bits[x] == 1 && bits[y] == 1) someXY = true;
            if (bits[x] == 1 && bits[y] == 0) someXnotY = true;
        }
        return switch (type) {
            case 'A' -> !someXnotY;                              // x(1 - y) = 0
            case 'E' -> !someXY;                                 // xy = 0
            case 'I' -> someXY;                                  // xy is not 0
            default -> someXnotY;                                // x(1 - y) is not 0
        };
    }

    static boolean nonEmpty(int world, int cls) {
        for (int r = 0; r < 8; r++) if (((world >> r) & 1) == 1 && ((r >> (2 - cls)) & 1) == 1) return true;
        return false;
    }

    public static void main(String[] args) {
        // ---- 1. x^2 = x ------------------------------------------------------------------------------------------------
        List<String> sols = new ArrayList<>();
        for (int x = -1000; x <= 1000; x++) if ((long) x * x == x) sols.add(String.valueOf(x));
        int fracs = 0;
        for (int q = 2; q <= 200; q++) for (int p = -400; p <= 400; p++) { if (p % q == 0) continue; fracs++; check((long) p * p * 1 != (long) p * q, "no fraction p/q satisfies (p/q)^2 = p/q"); }
        check(sols.equals(List.of("0", "1")), "x^2 = x only for 0 and 1");
        System.out.printf("law: x^2 = x among the whole numbers from -1,000 to 1,000: only %s ; among %,d fractions p/q with q from 2 to 200: none ; so x(1 - x) = 0 for every symbol%n", String.join(" and ", sols), fracs);

        // ---- 2. Boole's expansion ---------------------------------------------------------------------------------------
        int f2 = 0;
        for (int f = 0; f < 16; f++) {                           // every function of two variables, as its truth table
            for (int x = 0; x <= 1; x++) for (int y = 0; y <= 1; y++) {
                int direct = (f >> (x * 2 + y)) & 1;
                int expanded = 0;                                // f(1,1) xy + f(1,0) x(1-y) + f(0,1)(1-x)y + f(0,0)(1-x)(1-y)
                for (int a = 0; a <= 1; a++) for (int b = 0; b <= 1; b++) expanded += ((f >> (a * 2 + b)) & 1) * (a == 1 ? x : 1 - x) * (b == 1 ? y : 1 - y);
                check(expanded == direct, "the expansion reproduces the function");
            }
            f2++;
        }
        int f3 = 0;
        for (int f = 0; f < 256; f++) {
            for (int v = 0; v < 8; v++) {
                int x = (v >> 2) & 1, y = (v >> 1) & 1, z = v & 1, expanded = 0;
                for (int t = 0; t < 8; t++) expanded += ((f >> t) & 1) * (((t >> 2) & 1) == 1 ? x : 1 - x) * (((t >> 1) & 1) == 1 ? y : 1 - y) * ((t & 1) == 1 ? z : 1 - z);
                check(expanded == ((f >> v) & 1), "three-variable expansion");
            }
            f3++;
        }
        System.out.printf("expand: f(x) = f(1) x + f(0)(1 - x) ; checked for all %d functions of two variables (4 terms each) and all %d of three (8 terms each)%n", f2, f3);

        // ---- 3. all 256 syllogisms -------------------------------------------------------------------------------------------
        char[] T = {'A', 'E', 'I', 'O'};
        // figures: positions of the middle term M in the major premise (M-P or P-M) and minor premise (S-M or M-S)
        int[][][] fig = {{{1, 2}, {0, 1}}, {{2, 1}, {0, 1}}, {{1, 2}, {1, 0}}, {{2, 1}, {1, 0}}};
        int valid = 0, validImport = 0, forms = 0;
        List<String> modern = new ArrayList<>();
        for (int f = 0; f < 4; f++)
            for (char a : T) for (char b : T) for (char c : T) {
                forms++;
                boolean ok = true, okImport = true;
                for (int w = 0; w < 256; w++) {
                    boolean prem = holds(w, a, fig[f][0][0], fig[f][0][1]) && holds(w, b, fig[f][1][0], fig[f][1][1]);
                    if (prem && !holds(w, c, 0, 2)) {
                        ok = false;
                        if (nonEmpty(w, 0) && nonEmpty(w, 1) && nonEmpty(w, 2)) okImport = false;
                    }
                }
                if (ok) { valid++; modern.add("" + a + b + c + "-" + (f + 1)); }
                if (okImport) validImport++;
            }
        check(forms == 256 && valid == 15 && validImport == 24, "15 valid forms, 24 if every class has members");
        check(modern.contains("AAA-1"), "Barbara is valid");
        System.out.printf("syllogism: all %d forms (4 figures x 4^3 moods), tested against all 256 ways three classes can share members ; valid: %d ; valid if every class has members: %d ; the first valid form is %s, \"all M are P, all S are M, so all S are P\": m(1 - p) = 0 and s(1 - m) = 0 give s(1 - p) = 0%n",
                forms, valid, validImport, modern.get(0));

        // ---- 4. Shannon: adders from Boolean expressions --------------------------------------------------------------------
        int fa = 0;
        for (int v = 0; v < 8; v++) {
            int x = (v >> 2) & 1, y = (v >> 1) & 1, c = v & 1;
            int sum = xor(xor(x, y), c);
            int carry = or(and(x, y), and(c, xor(x, y)));
            check(sum + 2 * carry == x + y + c, "the full adder adds");
            fa++;
        }
        Random rnd = new Random(1854);
        int added = 0;
        for (int t = 0; t < 200000; t++) {
            int a = rnd.nextInt(1 << 16), b = rnd.nextInt(1 << 16), carry = 0, s = 0;
            for (int i = 0; i < 16; i++) {
                int x = (a >> i) & 1, y = (b >> i) & 1;
                s |= xor(xor(x, y), carry) << i;
                carry = or(and(x, y), and(carry, xor(x, y)));
            }
            s |= carry << 16;
            check(s == a + b, "the 16-bit adder of Boolean expressions adds");
            added++;
        }
        System.out.printf("adder: a full adder as Boolean expressions, sum = x XOR y XOR c and carry = xy OR c(x XOR y), checked on all %d inputs ; chained sixteen times, it added %,d random pairs of 16-bit numbers correctly%n", fa, added);

        // ---- 5. simplifying a circuit ------------------------------------------------------------------------------------------
        // xy + x(1 - y) + (1 - x) y: 6 contacts as written ; Boole's laws reduce it to x + y - xy (x OR y): 2 contacts
        int contactsBefore = 6, contactsAfter = 2;
        for (int v = 0; v < 4; v++) {
            int x = (v >> 1) & 1, y = v & 1;
            int before = or(or(and(x, y), and(x, 1 - y)), and(1 - x, y));
            check(before == or(x, y), "the simplified circuit behaves the same");
        }
        // the majority of three, xy + xz + yz: 6 contacts ; as x(y + z) + yz: 5
        for (int v = 0; v < 8; v++) {
            int x = (v >> 2) & 1, y = (v >> 1) & 1, z = v & 1;
            check(or(or(and(x, y), and(x, z)), and(y, z)) == or(and(x, or(y, z)), and(y, z)), "majority, factored");
        }
        System.out.printf("circuit: xy + x(1 - y) + (1 - x)y as relays: %d contacts ; by Boole's laws it equals x + y - xy, two contacts in parallel: %d ; the majority of three, xy + xz + yz (6 contacts), factored as x(y + z) + yz: 5 ; both checked on every input%n",
                contactsBefore, contactsAfter);

        System.out.printf("BooleanAlgebra: %d checks passed%n", passed);
    }

    static int and(int a, int b) { return a * b; }                // contacts in series

    static int or(int a, int b) { return a + b - a * b; }         // contacts in parallel

    static int xor(int a, int b) { return a + b - 2 * a * b; }
}
