import java.util.*;
import java.util.regex.Pattern;

/**
 * Era 5, topic 2: regular expressions (Kleene 1951; Rabin and Scott 1959; Thompson 1968).
 *
 * HOW IT WORKS
 *   A regular expression is built from single symbols with three operations: E|F (either), EF (one then the other)
 *   and E* (zero or more of E, one after another). Kleene showed in 1951 that these describe exactly the patterns a
 *   machine with finitely many states can recognise.
 *   Thompson's construction turns an expression into such a machine piece by piece: a symbol is two states joined by
 *   an arrow labelled with the symbol; "either" and "repeat" add two states and some unlabelled arrows (moves that
 *   read nothing); "then" joins the end of one piece to the start of the next. The machine is nondeterministic: it
 *   can be in several states at once. To match a text, keep the set of states the machine could be in, and update the
 *   whole set once per letter: the work is (letters) x (states), never more.
 *   Rabin and Scott (1959) showed that each set of states can itself be made one state of an ordinary machine (the
 *   subset construction). That machine reads each letter with a single table lookup, but it may need 2^n states.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A parser for Kleene's three operations and Thompson's construction; checks the state count 2s - c.
 *   2. An expression for the binary numerals divisible by 3, checked on every string of up to 16 digits.
 *   3. Random expressions matched on random strings by the state-set method, by the subset machine, and by
 *      java.util.regex: all three must agree.
 *   4. The subset construction and minimisation for (a|b)*abb, and the 2^n blow-up for "the n-th letter from the
 *      end is a".
 *   5. A backtracking matcher (try one way, back up, try another) against the state-set method on (a|aa)*b.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java RegularExpressions.java
 *   Expected output: expected-output.txt in this folder.
 */
public class RegularExpressions {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- 1. expressions -----------------------------------------------------------------------------------------------
    static final class Node {
        final char kind;      // 'c' symbol, '.' then, '|' either, '*' repeat
        final char sym;
        final Node l, r;
        Node(char kind, char sym, Node l, Node r) { this.kind = kind; this.sym = sym; this.l = l; this.r = r; }
    }

    static String src;
    static int pos, symbols, concats;

    static Node parse(String s) {
        src = s;
        pos = 0;
        symbols = 0;
        concats = 0;
        Node n = alt();
        if (pos != s.length()) throw new IllegalArgumentException("unexpected " + s.charAt(pos));
        return n;
    }

    static Node alt() {
        Node n = cat();
        while (pos < src.length() && src.charAt(pos) == '|') { pos++; symbols++; n = new Node('|', ' ', n, cat()); }
        return n;
    }

    static Node cat() {
        Node n = rep();
        while (pos < src.length() && src.charAt(pos) != '|' && src.charAt(pos) != ')') { concats++; n = new Node('.', ' ', n, rep()); }
        return n;
    }

    static Node rep() {
        Node n;
        char c = src.charAt(pos);
        if (c == '(') { pos++; n = alt(); if (src.charAt(pos++) != ')') throw new IllegalArgumentException("missing )"); }
        else if (Character.isLetterOrDigit(c)) { pos++; symbols++; n = new Node('c', c, null, null); }
        else throw new IllegalArgumentException("unexpected " + c);
        while (pos < src.length() && src.charAt(pos) == '*') { pos++; symbols++; n = new Node('*', ' ', n, null); }
        return n;
    }

    // ---- Thompson's construction ------------------------------------------------------------------------------------
    static final class State {
        char label;           // 0: the arrows read nothing
        State out1, out2;
        boolean dead;
        int id;
    }

    record Frag(State start, State end) {}

    static int made;

    static State st() { made++; return new State(); }

    static Frag build(Node n) {
        switch (n.kind) {
            case 'c': {
                State s = st(), e = st();
                s.label = n.sym;
                s.out1 = e;
                return new Frag(s, e);
            }
            case '.': {
                Frag a = build(n.l), b = build(n.r);
                // join: the end of a takes over the start of b (no arrow ever enters a piece's start)
                a.end().label = b.start().label;
                a.end().out1 = b.start().out1;
                a.end().out2 = b.start().out2;
                b.start().dead = true;
                made--;
                State end = b.end() == b.start() ? a.end() : b.end();
                return new Frag(a.start(), end);
            }
            case '|': {
                Frag a = build(n.l), b = build(n.r);
                State s = st(), e = st();
                s.out1 = a.start();
                s.out2 = b.start();
                a.end().out1 = e;
                b.end().out1 = e;
                return new Frag(s, e);
            }
            default: {
                Frag a = build(n.l);
                State s = st(), e = st();
                s.out1 = a.start();
                s.out2 = e;
                a.end().out1 = a.start();
                a.end().out2 = e;
                return new Frag(s, e);
            }
        }
    }

    static final class Nfa {
        final List<State> states = new ArrayList<>();
        final State start, accept;
        Nfa(String regex) {
            made = 0;
            Frag f = build(parse(regex));
            start = f.start();
            accept = f.end();
            Deque<State> todo = new ArrayDeque<>(List.of(start));
            Set<State> seen = new HashSet<>(List.of(start));
            while (!todo.isEmpty()) {
                State s = todo.pop();
                s.id = states.size();
                states.add(s);
                for (State t : new State[]{s.out1, s.out2}) if (t != null && seen.add(t)) todo.push(t);
            }
        }

        BitSet closure(BitSet set) {
            BitSet c = (BitSet) set.clone();
            Deque<Integer> todo = new ArrayDeque<>();
            set.stream().forEach(todo::push);
            while (!todo.isEmpty()) {
                State s = states.get(todo.pop());
                if (s.label != 0) continue;
                for (State t : new State[]{s.out1, s.out2}) if (t != null && !c.get(t.id)) { c.set(t.id); todo.push(t.id); }
            }
            return c;
        }

        BitSet startSet() { BitSet b = new BitSet(); b.set(start.id); return closure(b); }

        BitSet step(BitSet set, char ch) {
            BitSet next = new BitSet();
            set.stream().forEach(i -> { State s = states.get(i); if (s.label == ch) next.set(s.out1.id); });
            return closure(next);
        }

        long work;

        boolean matches(String text) {
            BitSet cur = startSet();
            for (int i = 0; i < text.length(); i++) {
                work += cur.cardinality();
                cur = step(cur, text.charAt(i));
            }
            return cur.get(accept.id);
        }
    }

    // ---- the subset construction (Rabin and Scott) and minimisation -----------------------------------------------------
    static final class Dfa {
        final List<BitSet> sets = new ArrayList<>();
        final List<int[]> next = new ArrayList<>();
        final List<Boolean> accepting = new ArrayList<>();
        final String alphabet;
        Dfa(Nfa n, String alphabet) {
            this.alphabet = alphabet;
            Map<BitSet, Integer> index = new HashMap<>();
            BitSet s0 = n.startSet();
            index.put(s0, 0);
            sets.add(s0);
            for (int i = 0; i < sets.size(); i++) {
                int[] row = new int[alphabet.length()];
                for (int k = 0; k < alphabet.length(); k++) {
                    BitSet t = n.step(sets.get(i), alphabet.charAt(k));
                    Integer j = index.get(t);
                    if (j == null) { j = sets.size(); index.put(t, j); sets.add(t); }
                    row[k] = j;
                }
                next.add(row);
                accepting.add(sets.get(i).get(n.accept.id));
            }
        }

        boolean matches(String text) {
            int s = 0;
            for (int i = 0; i < text.length(); i++) {
                int k = alphabet.indexOf(text.charAt(i));
                if (k < 0) return false;
                s = next.get(s)[k];
            }
            return accepting.get(s);
        }

        /** Moore's method: split the states into groups until no letter separates two states of a group. */
        int minimalStates() {
            int n = sets.size();
            int[] group = new int[n];
            for (int i = 0; i < n; i++) group[i] = accepting.get(i) ? 1 : 0;
            int count = -1;
            while (true) {
                Map<List<Integer>, Integer> sig = new HashMap<>();
                int[] g2 = new int[n];
                for (int i = 0; i < n; i++) {
                    List<Integer> key = new ArrayList<>();
                    key.add(group[i]);
                    for (int t : next.get(i)) key.add(group[t]);
                    g2[i] = sig.computeIfAbsent(key, x -> sig.size());
                }
                group = g2;
                if (sig.size() == count) return count;
                count = sig.size();
            }
        }
    }

    // ---- a backtracking matcher, counting its steps -------------------------------------------------------------------
    static long steps;

    interface Cont { boolean at(int i); }

    static boolean bt(Node n, String t, int i, Cont k) {
        steps++;
        switch (n.kind) {
            case 'c': return i < t.length() && t.charAt(i) == n.sym && k.at(i + 1);
            case '.': return bt(n.l, t, i, j -> bt(n.r, t, j, k));
            case '|': return bt(n.l, t, i, k) || bt(n.r, t, i, k);
            default: return bt(n.l, t, i, j -> j > i && bt(n, t, j, k)) || k.at(i);
        }
    }

    static boolean btMatches(String regex, String t) { return bt(parse(regex), t, 0, j -> j == t.length()); }

    static long seed = 1951L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % n);
    }

    static String randomRegex(int depth) {
        int r = rnd(depth <= 0 ? 2 : 7);
        return switch (r) {
            case 0, 1 -> String.valueOf("ab".charAt(rnd(2)));
            case 2, 3 -> randomRegex(depth - 1) + randomRegex(depth - 1);
            case 4, 5 -> "(" + randomRegex(depth - 1) + "|" + randomRegex(depth - 1) + ")";
            default -> "(" + randomRegex(depth - 1) + ")*";
        };
    }

    static String randomText() {
        int len = rnd(13);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < len; i++) sb.append("ab".charAt(rnd(2)));
        return sb.toString();
    }

    public static void main(String[] args) {
        // ---- 1. Thompson's construction, state count -------------------------------------------------------------------
        String ex = "(a|b)*abb";
        Nfa nx = new Nfa(ex);
        check(nx.states.size() == 2 * symbols - concats && made == nx.states.size(), "2s - c states");
        int sx = symbols, cx = concats;
        for (int t = 0; t < 5000; t++) {
            String r = randomRegex(5);
            Nfa n = new Nfa(r);
            check(n.states.size() == 2 * symbols - concats, "2s - c for " + r);
        }
        System.out.printf("thompson: %s has s = %d symbols (letters, | and *) and c = %d joins ; the machine has 2s - c = %d states ; the same count held for 5000 random expressions%n",
                ex, sx, cx, nx.states.size());

        // ---- 2. multiples of three in binary ----------------------------------------------------------------------------
        String three = "(0|1(01*0)*1)*";
        Nfa n3 = new Nfa(three);
        Dfa d3 = new Dfa(n3, "01");
        int tested = 0, accepted = 0;
        for (int len = 1; len <= 16; len++)
            for (int v = 0; v < (1 << len); v++) {
                StringBuilder sb = new StringBuilder(Integer.toBinaryString(v));
                while (sb.length() < len) sb.insert(0, '0');
                String s = sb.toString();
                boolean want = v % 3 == 0, got = n3.matches(s);
                check(got == want && d3.matches(s) == want, "multiple of 3: " + s);
                tested++;
                if (got) accepted++;
            }
        StringJoiner first = new StringJoiner(" ");
        for (int v = 0, shown = 0; shown < 8; v++) if (n3.matches(Integer.toBinaryString(v))) { first.add(Integer.toBinaryString(v)); shown++; }
        System.out.printf("three: %s matches exactly the binary numerals divisible by 3 ; checked on all %,d strings of 1 to 16 digits (%,d accepted) ; the first numerals it accepts: %s ; Thompson machine %d states, subset machine %d, smallest machine %d%n",
                three, tested, accepted, first, n3.states.size(), d3.sets.size(), d3.minimalStates());

        // ---- 3. random expressions, three matchers ---------------------------------------------------------------------
        int exprs = 2000, texts = 100, agree = 0, yes = 0;
        for (int e = 0; e < exprs; e++) {
            String r = randomRegex(4);
            Nfa n = new Nfa(r);
            Dfa d = new Dfa(n, "ab");
            Pattern p = Pattern.compile(r);
            for (int t = 0; t < texts; t++) {
                String s = randomText();
                boolean a = n.matches(s), b = d.matches(s), c = p.matcher(s).matches();
                check(a == b && b == c, "matchers agree on " + r + " / " + s);
                agree++;
                if (a) yes++;
            }
        }
        System.out.printf("random: %,d random expressions, %d random strings each ; the state-set method, the subset machine and java.util.regex agreed on all %,d cases (%,d matches)%n",
                exprs, texts, agree, yes);

        // ---- 4. subset construction and the blow-up -------------------------------------------------------------------
        Dfa dx = new Dfa(nx, "ab");
        StringJoiner rows = new StringJoiner(" ; ");
        for (int i = 0; i < dx.sets.size(); i++)
            rows.add(String.format("D%d = %s a->D%d b->D%d%s", i, dx.sets.get(i), dx.next.get(i)[0], dx.next.get(i)[1], dx.accepting.get(i) ? " accept" : ""));
        System.out.printf("subset: %s: %d Thompson states become %d sets of states ; %s ; smallest equivalent machine: %d states%n",
                ex, nx.states.size(), dx.sets.size(), rows, dx.minimalStates());

        StringJoiner blow = new StringJoiner(" ; ");
        for (int k = 1; k <= 14; k++) {
            String r = "(a|b)*a" + "(a|b)".repeat(k - 1);
            Nfa n = new Nfa(r);
            Dfa d = new Dfa(n, "ab");
            int min = d.minimalStates();
            check(min == 1 << k, "the n-th from the end needs 2^n states");
            if (k <= 4 || k % 2 == 0) blow.add(String.format("n=%d: %d / %d / %d", k, n.states.size(), d.sets.size(), min));
        }
        System.out.printf("blowup: the n-th letter from the end is a, (a|b)*a(a|b)...(a|b) ; Thompson states / subset states / smallest machine: %s ; the smallest machine always has exactly 2^n states%n", blow);

        // ---- 5. backtracking --------------------------------------------------------------------------------------------
        String bad = "(a|aa)*b";
        Nfa nb = new Nfa(bad);
        StringJoiner bk = new StringJoiner(" ; ");
        long prev = 0;
        for (int k = 5; k <= 30; k += 5) {
            String t = "a".repeat(k);
            steps = 0;
            boolean b1 = btMatches(bad, t);
            nb.work = 0;
            boolean b2 = nb.matches(t);
            check(!b1 && !b2 && !Pattern.matches(bad, t), "no b, no match");
            check(steps > prev, "backtracking grows");
            prev = steps;
            bk.add(String.format("%d letters: backtracking %,d steps, state sets %,d", k, steps, nb.work));
        }
        check(prev > 1_000_000, "backtracking passes a million steps by 30 letters");
        System.out.printf("backtrack: %s on a string of a's with no b ; %s ; trying each way of splitting the a's into a and aa grows like the Fibonacci numbers, the state-set method grows in proportion to the length%n",
                bad, bk);

        System.out.println("RegularExpressions: " + passed + " checks passed");
    }
}
