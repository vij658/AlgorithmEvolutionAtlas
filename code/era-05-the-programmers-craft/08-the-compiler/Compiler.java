import java.util.*;

/**
 * Era 5, topic 8: the compiler (FORTRAN, IBM, 1954-1957) and the grammar that describes a language (Backus 1959,
 * the ALGOL 60 report, 1960).
 *
 * HOW IT WORKS
 *   A compiler reads a formula such as A + B * C ** 2 and writes the machine instructions that compute it. First it
 *   must find the structure the formula's author meant: multiplication before addition, powers before
 *   multiplication, left to right among equals. The ALGOL 60 report wrote that structure down as a grammar:
 *       <expression> ::= <term> | <expression> <adding operator> <term>
 *       <term>       ::= <factor> | <term> <multiplying operator> <factor>
 *       <factor>     ::= <primary> | <factor> ** <primary>
 *       <primary>    ::= <number> | <variable> | ( <expression> )
 *   Each rule becomes one procedure of the parser, which calls the others as the rules mention them. The result is a
 *   tree; the code generator walks the tree and emits instructions for a machine with one accumulator, using
 *   temporary storage words where an intermediate result has to wait. FORTRAN's makers cared above all that the
 *   instructions be nearly as few as a careful programmer's, so the generator tries not to store and reload what it
 *   can use directly.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A parser written straight from the grammar above, showing the structure it finds in a formula.
 *   2. Two code generators for a one-accumulator machine: a plain one that stores every intermediate result, and one
 *      that uses an operand directly whenever it can; the instructions for a sample formula.
 *   3. 20,000 random formulas from the grammar: printed, parsed again, compiled both ways, run on the machine with
 *      random values, and checked against direct evaluation; the instruction counts of the two generators.
 *   4. Left to right: A - B - C, and why the rule <expression> <adding operator> <term> fixes the meaning.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Compiler.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Compiler {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- the tree ----------------------------------------------------------------------------------------------------
    record Node(String op, String leaf, Node l, Node r) {
        boolean isLeaf() { return leaf != null; }
    }

    static Node leaf(String s) { return new Node(null, s, null, null); }

    static Node bin(String op, Node l, Node r) { return new Node(op, null, l, r); }

    // ---- 1. the parser: one procedure per rule -------------------------------------------------------------------------
    static List<String> tokens;
    static int pos;

    static List<String> lex(String s) {
        List<String> t = new ArrayList<>();
        for (int i = 0; i < s.length(); ) {
            char c = s.charAt(i);
            if (c == ' ') { i++; continue; }
            if (c == '*' && i + 1 < s.length() && s.charAt(i + 1) == '*') { t.add("**"); i += 2; continue; }
            if (Character.isLetterOrDigit(c)) {
                int j = i;
                while (j < s.length() && Character.isLetterOrDigit(s.charAt(j))) j++;
                t.add(s.substring(i, j));
                i = j;
                continue;
            }
            t.add(String.valueOf(c));
            i++;
        }
        return t;
    }

    static Node parse(String s) {
        tokens = lex(s);
        pos = 0;
        Node n = expression();
        if (pos != tokens.size()) throw new IllegalArgumentException("unexpected " + tokens.get(pos));
        return n;
    }

    static String peek() { return pos < tokens.size() ? tokens.get(pos) : ""; }

    // <expression> ::= <term> | <expression> <adding operator> <term>   (the left recursion becomes a loop)
    static Node expression() {
        Node n = term();
        while (peek().equals("+") || peek().equals("-")) { String op = tokens.get(pos++); n = bin(op, n, term()); }
        return n;
    }

    // <term> ::= <factor> | <term> <multiplying operator> <factor>
    static Node term() {
        Node n = factor();
        while (peek().equals("*")) { pos++; n = bin("*", n, factor()); }
        return n;
    }

    // <factor> ::= <primary> | <factor> ** <primary>
    static Node factor() {
        Node n = primary();
        while (peek().equals("**")) { pos++; n = bin("**", n, primary()); }
        return n;
    }

    // <primary> ::= <number> | <variable> | ( <expression> )
    static Node primary() {
        String t = peek();
        if (t.equals("(")) {
            pos++;
            Node n = expression();
            if (!peek().equals(")")) throw new IllegalArgumentException("missing )");
            pos++;
            return n;
        }
        if (t.isEmpty() || !Character.isLetterOrDigit(t.charAt(0))) throw new IllegalArgumentException("unexpected " + t);
        pos++;
        return leaf(t);
    }

    static String full(Node n) { return n.isLeaf() ? n.leaf() : "(" + full(n.l()) + " " + n.op() + " " + full(n.r()) + ")"; }

    static int prec(String op) { return op.equals("**") ? 3 : op.equals("*") ? 2 : 1; }

    /** Print with the fewest parentheses the grammar needs. */
    static String plain(Node n) {
        if (n.isLeaf()) return n.leaf();
        String l = plain(n.l()), r = plain(n.r());
        if (!n.l().isLeaf() && prec(n.l().op()) < prec(n.op())) l = "(" + l + ")";
        if (!n.r().isLeaf() && prec(n.r().op()) <= prec(n.op())) r = "(" + r + ")";
        return l + " " + n.op() + " " + r;
    }

    // ---- 2. code generation -----------------------------------------------------------------------------------------------
    static List<String> code;
    static int temps;

    static String opcode(String op) { return switch (op) { case "+" -> "ADD"; case "-" -> "SUB"; default -> "MPY"; }; }

    static String newTemp() { return "T" + (++temps); }

    /** The plain generator: every intermediate result goes to a temporary word. */
    static void plainGen(Node n) {
        if (n.isLeaf()) { code.add("LDA " + n.leaf()); return; }
        if (n.op().equals("**")) {
            plainGen(n.l());
            String t = newTemp();
            code.add("STO " + t);
            for (int k = 1; k < Integer.parseInt(n.r().leaf()); k++) code.add("MPY " + t);
            return;
        }
        plainGen(n.l());
        String t1 = newTemp();
        code.add("STO " + t1);
        plainGen(n.r());
        String t2 = newTemp();
        code.add("STO " + t2);
        code.add("LDA " + t1);
        code.add(opcode(n.op()) + " " + t2);
    }

    /** The careful generator: use a simple operand directly; for + and * the order may be swapped. */
    static void goodGen(Node n) {
        if (n.isLeaf()) { code.add("LDA " + n.leaf()); return; }
        if (n.op().equals("**")) {
            int k = Integer.parseInt(n.r().leaf());
            String base;
            if (n.l().isLeaf()) { base = n.l().leaf(); code.add("LDA " + base); }
            else { goodGen(n.l()); base = newTemp(); if (k > 1) code.add("STO " + base); }
            for (int i = 1; i < k; i++) code.add("MPY " + base);
            return;
        }
        String op = opcode(n.op());
        if (n.r().isLeaf()) { goodGen(n.l()); code.add(op + " " + n.r().leaf()); return; }
        if (!n.op().equals("-") && n.l().isLeaf()) { goodGen(n.r()); code.add(op + " " + n.l().leaf()); return; }
        goodGen(n.r());
        String t = newTemp();
        code.add("STO " + t);
        goodGen(n.l());
        code.add(op + " " + t);
    }

    static List<String> compile(Node n, boolean good) {
        code = new ArrayList<>();
        temps = 0;
        if (good) goodGen(n); else plainGen(n);
        return code;
    }

    /** The one-accumulator machine. Numbers in the program are constants; letters are variables. */
    static long run(List<String> prog, Map<String, Long> vars) {
        Map<String, Long> mem = new HashMap<>(vars);
        long acc = 0;
        for (String ins : prog) {
            String op = ins.substring(0, 3), a = ins.substring(4);
            long v = op.equals("STO") ? 0 : a.matches("\\d+") ? Long.parseLong(a) : mem.get(a);
            switch (op) {
                case "LDA" -> acc = v;
                case "ADD" -> acc += v;
                case "SUB" -> acc -= v;
                case "MPY" -> acc *= v;
                default -> mem.put(a, acc);
            }
        }
        return acc;
    }

    static long eval(Node n, Map<String, Long> vars) {
        if (n.isLeaf()) return n.leaf().matches("\\d+") ? Long.parseLong(n.leaf()) : vars.get(n.leaf());
        long l = eval(n.l(), vars), r = eval(n.r(), vars);
        return switch (n.op()) {
            case "+" -> l + r;
            case "-" -> l - r;
            case "*" -> l * r;
            default -> { long p = 1; for (int i = 0; i < r; i++) p *= l; yield p; }
        };
    }

    // ---- random formulas from the grammar -------------------------------------------------------------------------------
    static long seed = 1957L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % n);
    }

    static final String VARS = "ABCDEFGH";

    static String randExpression(int d) {
        String s = randTerm(d);
        int k = d > 0 ? rnd(3) : 0;
        for (int i = 0; i < k; i++) s += (rnd(2) == 0 ? " + " : " - ") + randTerm(d - 1);
        return s;
    }

    static String randTerm(int d) {
        String s = randFactor(d);
        int k = d > 0 ? rnd(3) : 0;
        for (int i = 0; i < k; i++) s += " * " + randFactor(d - 1);
        return s;
    }

    static String randFactor(int d) {
        String s = randPrimary(d);
        if (d > 0 && rnd(5) == 0) s += " ** " + (2 + rnd(2));
        return s;
    }

    static String randPrimary(int d) {
        int r = rnd(d > 0 ? 6 : 5);
        if (r < 3) return String.valueOf(VARS.charAt(rnd(VARS.length())));
        if (r < 5) return String.valueOf(1 + rnd(9));
        return "(" + randExpression(d - 1) + ")";
    }

    public static void main(String[] args) {
        // ---- 1. the structure of a formula ------------------------------------------------------------------------------------
        String f = "A + B * C ** 2 - D * (E - F)";
        Node t = parse(f);
        check(full(t).equals("((A + (B * (C ** 2))) - (D * (E - F)))"), "structure");
        System.out.printf("parse: %s ; the grammar's structure, every operation in its own brackets: %s ; powers first, then products, then sums and differences, left to right%n",
                f, full(t));

        // ---- 2. code ----------------------------------------------------------------------------------------------------
        List<String> p1 = compile(t, false), p2 = compile(t, true);
        Map<String, Long> vals = Map.of("A", 3L, "B", 4L, "C", 5L, "D", 6L, "E", 9L, "F", 2L);
        long want = 3 + 4 * 25 - 6 * 7;
        check(run(p1, vals) == want && run(p2, vals) == want && eval(t, vals) == want, "both programs compute it");
        System.out.printf("code: plain generator, %d instructions: %s ; careful generator, %d instructions: %s ; with A=3 B=4 C=5 D=6 E=9 F=2 both give %d%n",
                p1.size(), String.join(" ; ", p1), p2.size(), String.join(" ; ", p2), want);

        // ---- 3. random formulas ------------------------------------------------------------------------------------------------
        int n = 20000;
        long plainTotal = 0, goodTotal = 0, runs = 0;
        int longest = 0;
        String longestF = "";
        for (int i = 0; i < n; i++) {
            String s = randExpression(3);
            Node a = parse(s);
            String again = plain(a);
            Node b = parse(again);
            check(full(a).equals(full(b)), "printing and parsing again keeps the structure: " + s);
            List<String> c1 = compile(a, false), c2 = compile(a, true);
            plainTotal += c1.size();
            goodTotal += c2.size();
            check(c2.size() <= c1.size(), "the careful code is never longer");
            for (int k = 0; k < 5; k++) {
                Map<String, Long> v = new HashMap<>();
                for (char ch : VARS.toCharArray()) v.put(String.valueOf(ch), (long) (rnd(19) - 9));
                long e = eval(a, v);
                check(run(c1, v) == e && run(c2, v) == e, "machine agrees with direct evaluation: " + s);
                runs++;
            }
            if (s.length() > longest && s.length() <= 60) { longest = s.length(); longestF = s; }
        }
        System.out.printf("random: %,d random formulas made from the grammar's rules, such as %s ; each printed with the fewest brackets, parsed again to the same structure, compiled both ways and run %,d times in all with random values: every result matched direct evaluation ; instructions in all: plain %,d, careful %,d (%.0f%% fewer)%n",
                n, longestF, runs, plainTotal, goodTotal, 100.0 * (plainTotal - goodTotal) / plainTotal);

        // ---- 4. left to right --------------------------------------------------------------------------------------------------
        Node lr = parse("A - B - C");
        Map<String, Long> v3 = Map.of("A", 10L, "B", 4L, "C", 3L);
        long left = eval(lr, v3), right = 10 - (4 - 3);
        check(full(lr).equals("((A - B) - C)") && left == 3 && right == 9, "left association");
        System.out.printf("assoc: A - B - C with A=10 B=4 C=3 ; the rule <expression> ::= <expression> <adding operator> <term> puts the earlier subtraction deeper in the tree: %s = %d, not A - (B - C) = %d%n",
                full(lr), left, right);

        System.out.println("Compiler: " + passed + " checks passed");
    }
}
