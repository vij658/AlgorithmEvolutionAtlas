import java.util.*;

/**
 * Era 5, topic 6: linked lists (Newell, Shaw and Simon, 1956) and garbage collection (McCarthy, about 1959).
 *
 * HOW IT WORKS
 *   A linked list keeps each item in a cell together with the address of the next cell. Items need not sit side by
 *   side in memory, so a new item is spliced in by changing two addresses instead of moving everything after it.
 *   Lisp's cells hold two addresses, the "car" (the item) and the "cdr" (the rest of the list); since the car can be
 *   another list, cells make trees, and a formula such as (PLUS X (TIMES 3 X)) is a tree of cells. The unused cells
 *   are themselves chained into a free list, and every new cell is taken from it.
 *   A program that builds and discards structures leaves cells that nothing points to any more. McCarthy's answer,
 *   when the free list runs out: start from the cells the program can still reach (the roots), mark everything
 *   reachable from them, then sweep through memory and put every unmarked cell back on the free list.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A memory of two-address cells with a free list.
 *   2. Adding 10,000 items one at a time to the front of a list and of an array: addresses changed against items moved.
 *   3. Reversing a list in place by turning its arrows round.
 *   4. Symbolic differentiation on formulas stored as cells, simplifying as it goes: four derivatives of
 *      x^4 + 5x, checked by evaluating each one.
 *   5. The same work repeated in a small memory, so that the free list runs out again and again: mark-and-sweep keeps
 *      the program going, and every answer is still right.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ListsAndGarbage.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ListsAndGarbage {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- 1. the memory -------------------------------------------------------------------------------------------------
    // A cell number > 0 is a cell; 0 is NIL (the empty list); a number < 0 is an atom: -1 - (index in the atom table).
    static int[] car, cdr;
    static boolean[] mark;
    static int free, freeCount;
    static final List<String> atoms = new ArrayList<>();
    static final int[] roots = new int[10000];
    static int nroots = 0;
    static long allocated = 0, collections = 0, reclaimed = 0;

    static void memory(int cells) {
        car = new int[cells + 1];
        cdr = new int[cells + 1];
        mark = new boolean[cells + 1];
        free = 0;
        for (int c = cells; c >= 1; c--) { cdr[c] = free; free = c; }       // chain every cell into the free list
        freeCount = cells;
        allocated = collections = reclaimed = 0;
        nroots = 0;
    }

    static int atom(String name) {
        int i = atoms.indexOf(name);
        if (i < 0) { atoms.add(name); i = atoms.size() - 1; }
        return -1 - i;
    }

    static String name(int a) { return atoms.get(-1 - a); }

    static boolean isAtom(int x) { return x < 0; }

    static int push(int x) { roots[nroots++] = x; return x; }

    static void pop(int k) { nroots -= k; }

    static int cons(int a, int d) {
        if (free == 0) {
            push(a);
            push(d);              // the two arguments must survive the collection
            gc();
            pop(2);
            if (free == 0) throw new IllegalStateException("memory full");
        }
        int c = free;
        free = cdr[c];
        freeCount--;
        car[c] = a;
        cdr[c] = d;
        allocated++;
        return c;
    }

    /** Mark everything reachable from the roots, then sweep the unmarked cells onto the free list. */
    static void gc() {
        collections++;
        Arrays.fill(mark, false);
        Deque<Integer> todo = new ArrayDeque<>();
        for (int i = 0; i < nroots; i++) if (roots[i] > 0) todo.push(roots[i]);
        while (!todo.isEmpty()) {
            int c = todo.pop();
            if (mark[c]) continue;
            mark[c] = true;
            if (car[c] > 0) todo.push(car[c]);
            if (cdr[c] > 0) todo.push(cdr[c]);
        }
        for (int c = 1; c < car.length; c++)
            if (!mark[c]) {
                boolean wasFree = isFree(c);
                if (!wasFree) { car[c] = 0; cdr[c] = free; free = c; freeCount++; reclaimed++; }
            }
    }

    static boolean[] onFree;

    static boolean isFree(int c) {
        // cells already on the free list are found by a walk before the sweep
        return onFree != null && onFree[c];
    }

    static void gcFull() {
        onFree = new boolean[car.length];
        for (int c = free; c != 0; c = cdr[c]) onFree[c] = true;
        gc();
        onFree = null;
    }

    // ---- reading and writing formulas ----------------------------------------------------------------------------------
    static String text;
    static int at;

    static int read(String s) { text = s; at = 0; return readExpr(); }

    static int readExpr() {
        while (text.charAt(at) == ' ') at++;
        if (text.charAt(at) == '(') {
            at++;
            List<Integer> items = new ArrayList<>();
            while (true) {
                while (text.charAt(at) == ' ') at++;
                if (text.charAt(at) == ')') { at++; break; }
                items.add(push(readExpr()));
            }
            int list = 0;
            for (int i = items.size() - 1; i >= 0; i--) { list = cons(items.get(i), push(list)); pop(1); }
            pop(items.size());
            return list;
        }
        int start = at;
        while (at < text.length() && text.charAt(at) != ' ' && text.charAt(at) != ')' && text.charAt(at) != '(') at++;
        return atom(text.substring(start, at));
    }

    static String show(int x) {
        if (x == 0) return "NIL";
        if (isAtom(x)) return name(x);
        StringJoiner sj = new StringJoiner(" ", "(", ")");
        for (int c = x; c != 0; c = cdr[c]) sj.add(show(car[c]));
        return sj.toString();
    }

    static int list3(int op, int p, int q) {
        push(p);
        push(q);
        int c1 = push(cons(q, 0));
        int c2 = push(cons(p, c1));
        int r = cons(op, c2);
        pop(4);
        return r;
    }

    static int second(int e) { return car[cdr[e]]; }

    static int third(int e) { return car[cdr[cdr[e]]]; }

    static boolean isNumber(int x) { return isAtom(x) && name(x).matches("-?\\d+"); }

    static long num(int x) { return Long.parseLong(name(x)); }

    static int number(long v) { return atom(Long.toString(v)); }

    // ---- differentiation and simplification ------------------------------------------------------------------------
    static final int PLUS = atom("PLUS"), TIMES = atom("TIMES"), X = atom("X"), ZERO = atom("0"), ONE = atom("1");

    /** d/dX of e; e must be reachable from a root while this runs. */
    static int diff(int e) {
        if (isAtom(e)) return e == X ? ONE : ZERO;
        int op = car[e], a = second(e), b = third(e);
        int da = push(diff(a)), db = push(diff(b));
        int r;
        if (op == PLUS) r = list3(PLUS, da, db);
        else {
            int t1 = push(list3(TIMES, da, b));
            int t2 = push(list3(TIMES, a, db));
            r = list3(PLUS, t1, t2);
            pop(2);
        }
        pop(2);
        return r;
    }

    static int simplify(int e) {
        if (isAtom(e)) return e;
        int op = car[e];
        int a = push(simplify(second(e))), b = push(simplify(third(e)));
        int r;
        if (isNumber(a) && isNumber(b)) r = number(op == PLUS ? num(a) + num(b) : num(a) * num(b));
        else if (op == PLUS && a == ZERO) r = b;
        else if (op == PLUS && b == ZERO) r = a;
        else if (op == PLUS && a == b) r = list3(TIMES, number(2), a);    // the same cell or atom twice
        else if (op == TIMES && (a == ZERO || b == ZERO)) r = ZERO;
        else if (op == TIMES && a == ONE) r = b;
        else if (op == TIMES && b == ONE) r = a;
        else if (op == TIMES && isNumber(b)) r = list3(TIMES, b, a);     // numbers in front
        else r = list3(op, a, b);
        pop(2);
        return r;
    }

    static long eval(int e, long x) {
        if (isAtom(e)) return e == X ? x : num(e);
        long a = eval(second(e), x), b = eval(third(e), x);
        return car[e] == PLUS ? a + b : a * b;
    }

    static final String F = "(PLUS (TIMES X (TIMES X (TIMES X X))) (TIMES 5 X))";

    /** Exact k-th derivative of x^4 + 5x at x. */
    static long exact(int k, long x) {
        long[] c = new long[5];
        c[4] = 1;
        c[1] = 5;
        for (int d = 0; d < k; d++) { for (int i = 1; i < 5; i++) c[i - 1] = i * c[i]; c[4] = 0; }
        long v = 0, p = 1;
        for (int i = 0; i < 5; i++) { v += c[i] * p; p *= x; }
        return v;
    }

    /** Four derivatives; returns the derivatives as text, checking each by evaluation. */
    static List<String> derivatives() {
        List<String> out = new ArrayList<>();
        int base = nroots;
        int cur = push(read(F));
        for (int k = 1; k <= 4; k++) {
            int d = push(diff(cur));
            int s = simplify(d);
            pop(2);
            cur = push(s);
            for (long x = -3; x <= 3; x++) check(eval(cur, x) == exact(k, x), "derivative " + k + " at " + x);
            out.add(show(cur));
        }
        nroots = base;
        return out;
    }

    public static void main(String[] args) {
        // ---- 2. the front of a list ----------------------------------------------------------------------------------------
        memory(20000);
        int n = 10000;
        long pointerWrites = 0, moves = 0;
        int head = 0;
        int[] array = new int[n];
        int size = 0;
        for (int i = 0; i < n; i++) {
            head = cons(number(i % 10), head);         // a new cell whose cdr is the old head
            pointerWrites += 2;                        // the new cell's cdr, and the head
            for (int j = size; j > 0; j--) { array[j] = array[j - 1]; moves++; }
            array[0] = i % 10;
            size++;
        }
        int walked = 0;
        for (int c = head; c != 0; c = cdr[c]) { check(num(car[c]) == array[walked], "list and array agree"); walked++; }
        check(walked == n && moves == (long) n * (n - 1) / 2, "counts");
        System.out.printf("front: %,d items added one at a time to the front ; linked list: %,d cells taken from the free list and %,d addresses written ; array: %,d items moved along to make room%n",
                n, n, pointerWrites, moves);

        // ---- 3. reversal ------------------------------------------------------------------------------------------------------
        memory(100);
        int list = push(read("(A B C D E F G H)"));
        String before = show(list);
        int prev = 0, c = list, turned = 0;
        while (c != 0) { int nx = cdr[c]; cdr[c] = prev; prev = c; c = nx; turned++; }
        check(show(prev).equals("(H G F E D C B A)"), "reversed");
        check(freeCount == 100 - 8, "no new cells");
        System.out.printf("reverse: %s becomes %s by turning %d arrows round, with no new cells%n", before, show(prev), turned);

        // ---- 4. differentiation ------------------------------------------------------------------------------------------
        memory(100000);
        List<String> ds = derivatives();
        long big = allocated;
        check(collections == 0, "the big memory never runs out");
        System.out.printf("diff: f = x^4 + 5x, stored as %s ; derivatives, simplified as they are made: 1: %s ; 2: %s ; 3: %s ; 4: %s ; each checked by evaluating it at x = -3 to 3 ; %,d cells taken in all%n",
                F, ds.get(0), ds.get(1), ds.get(2), ds.get(3), big);

        // ---- 5. a small memory and the collector ----------------------------------------------------------------------------
        int small = 250, rounds = 200;
        memory(small);
        for (int r = 0; r < rounds; r++) check(derivatives().equals(ds), "same derivatives in a small memory, round " + r);
        long cellsTaken = allocated, ran = collections, back = reclaimed;
        check(ran > 100 && cellsTaken > small * 100L, "the collector ran many times");
        gcFull();
        check(freeCount == small, "after the work, every cell is free again");
        int smallest = 0;
        for (int cells = 100; cells <= 474 && smallest == 0; cells++) {
            memory(cells);
            try { if (derivatives().equals(ds)) smallest = cells; } catch (IllegalStateException full) { /* too small */ }
        }
        check(smallest > 0 && smallest <= small, "the work fits in the small memory");
        System.out.printf("gc: the same four derivatives computed %d times in a memory of only %d cells ; %,d cells taken in all, %,.0f times the memory ; the free list ran out %,d times, and each time mark-and-sweep returned the unreachable cells (%,d in all) ; all %d rounds gave the same answers ; at the end nothing is reachable and all %d cells are free ; the smallest memory in which the work can be done at all: %d cells, about the most that are ever in use at once%n",
                rounds, small, cellsTaken, (double) cellsTaken / small, ran, back, rounds, small, smallest);

        System.out.println("ListsAndGarbage: " + passed + " checks passed");
    }
}
