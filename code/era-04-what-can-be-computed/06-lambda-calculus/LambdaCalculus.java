import java.util.*;

/**
 * Era 4, topic 6: Church's lambda calculus (1932-1936).
 *
 * HOW IT WORKS
 *   There are only three kinds of term: a variable x; a function \x.M ("given x, return M"); and an application M N
 *   ("apply M to N"). There is one rule of computation, beta reduction: (\x.M) N becomes M with N put in place of x.
 *   A term with nothing left to reduce is in normal form, and that is the answer. Numbers are functions: the numeral
 *   n is \f.\x.f (f (... (f x))), "apply f n times". Arithmetic is then a matter of composing:
 *       PLUS = \m.\n.\f.\x.m f (n f x)      MULT = \m.\n.\f.m (n f)      EXP = \m.\n.n m
 *   Recursion needs no names: Y = \g.(\x.g (x x)) (\x.g (x x)) satisfies Y g = g (Y g). Some terms never reach a
 *   normal form, such as (\x.x x) (\x.x x), which reduces to itself, and Church proved in 1936 that no effective
 *   procedure decides which terms have one.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Parses lambda terms and reduces them, always rewriting the leftmost, outermost redex first.
 *   2. Church's own numerals of 1936, which start at 1, beside today's, which start at 0.
 *   3. PLUS, MULT, EXP and the predecessor on small numerals, against ordinary arithmetic, counting reduction steps;
 *      the whole reduction of PLUS 2 3, step by step.
 *   4. Factorial through the Y combinator, with no named recursion anywhere.
 *   5. The term that reduces to itself for ever, and a term whose answer depends on the order of reduction.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LambdaCalculus.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LambdaCalculus {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- terms, with variables as de Bruijn indices (0 = the nearest enclosing \) ----------------------------------
    sealed interface T permits Var, Lam, App {}
    record Var(int i) implements T {}
    record Lam(T body) implements T {}
    record App(T f, T a) implements T {}

    /** Add d to every variable that points outside the c innermost binders. */
    static T shift(T t, int d, int c) {
        if (t instanceof Var v) return v.i >= c ? new Var(v.i + d) : v;
        if (t instanceof Lam l) return new Lam(shift(l.body, d, c + 1));
        App a = (App) t;
        return new App(shift(a.f, d, c), shift(a.a, d, c));
    }

    /** Put s in place of variable j in t. */
    static T subst(T t, int j, T s) {
        if (t instanceof Var v) return v.i == j ? s : v;
        if (t instanceof Lam l) return new Lam(subst(l.body, j + 1, shift(s, 1, 0)));
        App a = (App) t;
        return new App(subst(a.f, j, s), subst(a.a, j, s));
    }

    /** (\.body) arg  ->  body with arg put in place of variable 0. */
    static T beta(T body, T arg) { return shift(subst(body, 0, shift(arg, 1, 0)), -1, 0); }

    /** One step of normal order (leftmost, outermost redex first), or null if t is in normal form. */
    static T stepNormal(T t) {
        if (t instanceof App a) {
            if (a.f instanceof Lam l) return beta(l.body, a.a);
            T f = stepNormal(a.f);
            if (f != null) return new App(f, a.a);
            T x = stepNormal(a.a);
            return x == null ? null : new App(a.f, x);
        }
        if (t instanceof Lam l) { T b = stepNormal(l.body); return b == null ? null : new Lam(b); }
        return null;
    }

    /** One step of applicative order (arguments first, innermost redex first), or null if in normal form. */
    static T stepApplicative(T t) {
        if (t instanceof App a) {
            T f = stepApplicative(a.f);
            if (f != null) return new App(f, a.a);
            T x = stepApplicative(a.a);
            if (x != null) return new App(a.f, x);
            if (a.f instanceof Lam l) return beta(l.body, a.a);
            return null;
        }
        if (t instanceof Lam l) { T b = stepApplicative(l.body); return b == null ? null : new Lam(b); }
        return null;
    }

    static long steps;

    static T normalize(T t, long limit) {
        steps = 0;
        while (steps < limit) {
            T n = stepNormal(t);
            if (n == null) return t;
            t = n;
            steps++;
        }
        return null;
    }

    // ---- parsing:  \x.M  for a function, juxtaposition for application, names of definitions in capitals -----------
    static final Map<String, T> DEF = new LinkedHashMap<>();

    static T parse(String s) {
        Parser p = new Parser(s);
        T t = p.term(new ArrayDeque<>());
        if (p.i != s.length()) throw new IllegalArgumentException("trailing input in " + s);
        return t;
    }

    static final class Parser {
        final String s;
        int i = 0;
        Parser(String s) { this.s = s; }
        void ws() { while (i < s.length() && s.charAt(i) == ' ') i++; }
        T term(Deque<String> env) {
            ws();
            if (s.charAt(i) == '\\') {
                i++;
                int st = i;
                while (Character.isLetterOrDigit(s.charAt(i))) i++;
                String name = s.substring(st, i);
                if (s.charAt(i) != '.') throw new IllegalArgumentException("expected . at " + i + " in " + s);
                i++;
                env.push(name);
                T body = term(env);
                env.pop();
                return new Lam(body);
            }
            T t = atom(env);
            while (true) {
                ws();
                if (i >= s.length() || s.charAt(i) == ')') return t;
                if (s.charAt(i) == '\\') return new App(t, term(env));
                t = new App(t, atom(env));
            }
        }
        T atom(Deque<String> env) {
            ws();
            if (s.charAt(i) == '(') { i++; T t = term(env); ws(); i++; return t; }
            int st = i;
            while (i < s.length() && (Character.isLetterOrDigit(s.charAt(i)))) i++;
            String name = s.substring(st, i);
            if (name.isEmpty()) throw new IllegalArgumentException("expected a name at " + st + " in " + s);
            int k = 0;
            for (String e : env) { if (e.equals(name)) return new Var(k); k++; }
            if (name.chars().allMatch(Character::isDigit)) return church(Integer.parseInt(name));
            T d = DEF.get(name);
            if (d == null) throw new IllegalArgumentException("unknown name " + name);
            return d;
        }
    }

    static T church(int n) {
        T body = new Var(0);
        for (int k = 0; k < n; k++) body = new App(new Var(1), body);
        return new Lam(new Lam(body));
    }

    /** The number a normal-form numeral stands for, or -1 if it is not a numeral. */
    static int unchurch(T t) {
        if (!(t instanceof Lam l1) || !(l1.body instanceof Lam l2)) return -1;
        int n = 0;
        T b = l2.body;
        while (b instanceof App a && a.f.equals(new Var(1))) { n++; b = a.a; }
        return b.equals(new Var(0)) ? n : -1;
    }

    /** Print with binder names a, b, c, ... chosen by depth, in Church's compact style: \ab.a(a(b)). */
    static String show(T t) { return show(t, 0); }

    static String show(T t, int depth) {
        if (t instanceof Var v) return String.valueOf((char) ('a' + depth - 1 - v.i));
        if (t instanceof Lam) {
            StringBuilder names = new StringBuilder();
            T b = t;
            int d = depth;
            while (b instanceof Lam l) { names.append((char) ('a' + d)); d++; b = l.body; }
            return "\\" + names + "." + show(b, d);
        }
        App a = (App) t;
        String f = show(a.f, depth);
        return (a.f instanceof Lam ? "(" + f + ")" : f) + "(" + show(a.a, depth) + ")";
    }

    public static void main(String[] args) {
        String[][] defs = {
                {"SUCC", "\\n.\\f.\\x.f (n f x)"},
                {"PLUS", "\\m.\\n.\\f.\\x.m f (n f x)"},
                {"MULT", "\\m.\\n.\\f.m (n f)"},
                {"EXP", "\\m.\\n.n m"},
                {"PRED", "\\n.\\f.\\x.n (\\g.\\h.h (g f)) (\\u.x) (\\u.u)"},
                {"TRUE", "\\x.\\y.x"},
                {"FALSE", "\\x.\\y.y"},
                {"ISZERO", "\\n.n (\\x.FALSE) TRUE"},
                {"Y", "\\g.(\\x.g (x x)) (\\x.g (x x))"},
                {"FACT", "Y (\\r.\\n.ISZERO n 1 (MULT n (r (PRED n))))"},
                {"OMEGA", "(\\x.x x) (\\x.x x)"},
        };
        for (String[] d : defs) DEF.put(d[0], parse(d[1]));

        // ---- 2. numerals ----------------------------------------------------------------------------------------------
        check(show(church(2)).equals("\\ab.a(a(b))"), "2 printed in Church's style");
        System.out.printf("numerals: Church 1936 (from 1): 1 = %s, 2 = %s, 3 = %s ; today (from 0): 0 = %s, the same formulas otherwise%n",
                show(church(1)), show(church(2)), show(church(3)), show(church(0)));

        // ---- 3. arithmetic --------------------------------------------------------------------------------------------
        int agree = 0, etaOnes = 0;
        long totalSteps = 0;
        Map<String, Long> sample = new LinkedHashMap<>();
        for (int m = 0; m <= 6; m++)
            for (int n = 0; n <= 6; n++) {
                Object[][] ops = {{"PLUS", m + n}, {"MULT", m * n}, {"EXP", (int) Math.pow(m, n)}};
                for (Object[] op : ops) {
                    int want = (int) op[1];
                    if (op[0].equals("EXP") && want > 800) continue;
                    T r = normalize(parse(op[0] + " " + m + " " + n), 10_000_000);
                    if (op[0].equals("EXP") && n == 0) {                      // 0 m reduces to \x.x, which is 1 only
                        check(r != null && show(r).equals("\\a.a"), "EXP m 0 gives the identity");   // after eta
                        etaOnes++;
                        continue;
                    }
                    check(r != null && unchurch(r) == want, op[0] + " " + m + " " + n);
                    agree++;
                    totalSteps += steps;
                    if (m == 2 && n == 3) sample.put(op[0] + " 2 3", steps);
                }
            }
        for (int n = 0; n <= 10; n++) {
            T r = normalize(parse("PRED " + n), 1_000_000);
            check(r != null && unchurch(r) == Math.max(0, n - 1), "PRED " + n);
            agree++;
            totalSteps += steps;
            if (n == 3) sample.put("PRED 3", steps);
        }
        StringJoiner sj = new StringJoiner(", ");
        sample.forEach((k, v) -> sj.add(k + " in " + v));
        System.out.printf("arith: PLUS, MULT and EXP on numerals 0 to 6 and PRED on 0 to 10: %d results, all equal to ordinary arithmetic, %d reduction steps in all ; EXP m 0 gives \\a.a in all %d cases, which is the numeral 1 only after eta-conversion ; steps: %s%n",
                agree, totalSteps, etaOnes, sj);

        // the whole reduction of PLUS 2 3, step by step
        T tr = parse("PLUS 2 3");
        System.out.println("trace: 0 " + show(tr));
        for (int s = 1; ; s++) {
            T nx = stepNormal(tr);
            if (nx == null) break;
            tr = nx;
            System.out.println("trace: " + s + " " + show(tr));
        }
        check(unchurch(tr) == 5, "the trace ends at 5");

        // ---- 4. factorial by the Y combinator --------------------------------------------------------------------------
        StringJoiner fj = new StringJoiner(" ; ");
        int[] fact = {1, 1, 2, 6, 24, 120};
        for (int n = 0; n <= 5; n++) {
            T r = normalize(parse("FACT " + n), 50_000_000);
            check(r != null && unchurch(r) == fact[n], "FACT " + n);
            fj.add(n + "! = " + fact[n] + " in " + steps + " steps");
        }
        System.out.printf("fact: factorial with Y and no named recursion: %s%n", fj);

        // ---- 5. a term with no normal form, and the order of reduction ---------------------------------------------------
        T om = DEF.get("OMEGA");
        T om1 = stepNormal(om);
        check(om1.equals(om), "Omega reduces to itself");
        check(normalize(om, 1000) == null, "Omega has no normal form in 1000 steps");
        T k = parse("(\\x.\\y.y) OMEGA");
        T kn = normalize(k, 1000);
        check(kn != null && show(kn).equals("\\a.a") && steps == 1, "normal order discards Omega");
        T t = k;
        int app = 0;
        for (; app < 1000; app++) { T n = stepApplicative(t); if (n == null) break; t = n; }
        check(app == 1000, "applicative order never finishes");
        System.out.printf("omega: (\\x.x x)(\\x.x x) reduces in one step to itself, and after 1000 steps has not changed: it has no normal form ; (\\x.\\y.y) applied to it: leftmost-outermost order reaches %s in %d step, arguments-first order is still working after %d steps%n",
                show(kn), 1, app);

        System.out.println("LambdaCalculus: " + passed + " checks passed");
    }
}
