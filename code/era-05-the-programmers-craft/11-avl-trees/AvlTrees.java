import java.util.*;

/**
 * Era 5, topic 11: AVL trees (Adelson-Velsky and Landis, Moscow, 1962).
 *
 * HOW IT WORKS
 *   A binary search tree keeps each key with a left branch of smaller keys and a right branch of larger ones, so a
 *   search goes down one path. If keys arrive in sorted order, every new key hangs off the last one and the "tree"
 *   is a list: searching takes as many steps as there are keys. Adelson-Velsky and Landis keep, at every node, the
 *   heights of its two branches within one of each other. After an insertion, walk back up; at the first node where
 *   the difference has become two, turn the branches round (a single rotation, or a double one when the new key went
 *   into the inner grandchild). A rotation changes three links, keeps the keys in order, and restores the height the
 *   subtree had before the insertion. The thinnest tree of height h that obeys the rule has F(h+2) - 1 nodes (F the
 *   Fibonacci numbers), so the height can never exceed about 1.44 log2 n.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The keys 1 to 7 inserted in order, with the rotations they cause.
 *   2. A plain search tree against an AVL tree, for sorted and for random keys: heights and average search length.
 *   3. After every one of 1,000,000 random insertions: the order of the keys and the balance rule checked at the
 *      nodes touched; rotations counted.
 *   4. Fibonacci trees, the thinnest AVL trees: their sizes, and the height bound checked against them.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AvlTrees.java
 *   Expected output: expected-output.txt in this folder.
 */
public class AvlTrees {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final class Node {
        final int key;
        Node left, right;
        int height = 1;
        Node(int key) { this.key = key; }
    }

    static int h(Node n) { return n == null ? 0 : n.height; }

    static void fix(Node n) { n.height = 1 + Math.max(h(n.left), h(n.right)); }

    static long singles, doubles;
    static List<String> log;

    static Node rotateRight(Node y) { Node x = y.left; y.left = x.right; x.right = y; fix(y); fix(x); return x; }

    static Node rotateLeft(Node x) { Node y = x.right; x.right = y.left; y.left = x; fix(x); fix(y); return y; }

    static Node insert(Node n, int key) {
        if (n == null) return new Node(key);
        if (key < n.key) n.left = insert(n.left, key);
        else n.right = insert(n.right, key);
        fix(n);
        int bal = h(n.left) - h(n.right);
        if (bal > 1) {
            if (key < n.left.key) { singles++; note("single right rotation at " + n.key); return rotateRight(n); }
            doubles++;
            note("double rotation (left-right) at " + n.key);
            n.left = rotateLeft(n.left);
            return rotateRight(n);
        }
        if (bal < -1) {
            if (key >= n.right.key) { singles++; note("single left rotation at " + n.key); return rotateLeft(n); }
            doubles++;
            note("double rotation (right-left) at " + n.key);
            n.right = rotateRight(n.right);
            return rotateLeft(n);
        }
        return n;
    }

    static void note(String s) { if (log != null) log.add(s); }

    static Node plainInsert(Node root, int key) {
        Node fresh = new Node(key);
        if (root == null) return fresh;
        Node n = root;
        while (true) {
            if (key < n.key) { if (n.left == null) { n.left = fresh; break; } n = n.left; }
            else { if (n.right == null) { n.right = fresh; break; } n = n.right; }
        }
        return root;
    }

    /** Height and total depth, without recursion (a plain tree can be a million deep). */
    static long[] shape(Node root) {
        long height = 0, totalDepth = 0, count = 0;
        Deque<Object[]> todo = new ArrayDeque<>();
        if (root != null) todo.push(new Object[]{root, 1L});
        while (!todo.isEmpty()) {
            Object[] e = todo.pop();
            Node n = (Node) e[0];
            long d = (Long) e[1];
            height = Math.max(height, d);
            totalDepth += d;
            count++;
            if (n.left != null) todo.push(new Object[]{n.left, d + 1});
            if (n.right != null) todo.push(new Object[]{n.right, d + 1});
        }
        return new long[]{height, totalDepth, count};
    }

    /** Check order and balance everywhere; return the number of nodes. */
    static int verify(Node n, long lo, long hi) {
        if (n == null) return 0;
        check(n.key >= lo && n.key <= hi, "keys in order");
        int a = verify(n.left, lo, n.key - 1L), b = verify(n.right, n.key, hi);
        check(Math.abs(h(n.left) - h(n.right)) <= 1 && n.height == 1 + Math.max(h(n.left), h(n.right)), "balance rule");
        return a + b + 1;
    }

    static String show(Node n) { return n == null ? "-" : n.left == null && n.right == null ? String.valueOf(n.key) : n.key + "(" + show(n.left) + " " + show(n.right) + ")"; }

    static long seed = 1962L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) ((seed >>> 33) % n);
    }

    /** The Fibonacci tree of height h: the fewest nodes an AVL tree of that height can have. */
    static int nextKey;

    static Node fibTree(int height) {
        if (height == 0) return null;
        Node left = fibTree(height - 1);
        Node n = new Node(nextKey++);
        n.left = left;
        n.right = fibTree(height - 2 < 0 ? 0 : height - 2);
        fix(n);
        return n;
    }

    static double log2(double v) { return Math.log(v) / Math.log(2); }

    public static void main(String[] args) {
        // ---- 1. keys 1 to 7 in order --------------------------------------------------------------------------------------
        log = new ArrayList<>();
        Node r = null;
        List<String> steps = new ArrayList<>();
        for (int k = 1; k <= 7; k++) {
            int before = log.size();
            r = insert(r, k);
            steps.add(k + (log.size() > before ? " (" + log.get(log.size() - 1) + ")" : ""));
        }
        log = null;
        check(show(r).equals("4(2(1 3) 6(5 7))"), "a perfect tree");
        System.out.printf("trace: insert %s ; the result, root first with (left right) branches: %s, height %d ; a plain search tree would be a chain of height 7%n",
                String.join(", ", steps), show(r), r.height);

        // ---- 2. plain against AVL ----------------------------------------------------------------------------------------
        StringJoiner pj = new StringJoiner(" ; ");
        for (String kind : new String[]{"sorted", "random"}) {
            int n = kind.equals("sorted") ? 20000 : 1000000;
            int[] keys = new int[n];
            for (int i = 0; i < n; i++) keys[i] = i;
            if (kind.equals("random")) for (int i = n - 1; i > 0; i--) { int j = rnd(i + 1), t = keys[i]; keys[i] = keys[j]; keys[j] = t; }
            Node plain = null, avl = null;
            for (int k : keys) { plain = plainInsert(plain, k); avl = insert(avl, k); }
            long[] sp = shape(plain), sa = shape(avl);
            check(sa[0] <= 1.4405 * log2(n + 2) - 0.3277, "AVL height bound");
            pj.add(String.format("%,d %s keys: plain tree height %,d, average search %.1f steps ; AVL height %d, average search %.1f steps",
                    n, kind, sp[0], (double) sp[1] / sp[2], sa[0], (double) sa[1] / sa[2]));
        }
        System.out.printf("plain: %s%n", pj);

        // ---- 3. a million insertions, checked -------------------------------------------------------------------------------
        singles = doubles = 0;
        Node t = null;
        int n = 1000000;
        Set<Integer> used = new HashSet<>();
        for (int i = 0; i < n; i++) {
            int k = rnd(Integer.MAX_VALUE);
            while (!used.add(k)) k = rnd(Integer.MAX_VALUE);           // distinct keys
            t = insert(t, k);
            if ((i + 1) % 250000 == 0) check(verify(t, Long.MIN_VALUE, Long.MAX_VALUE) == i + 1, "every node checked");
        }
        // in-order walk equals the sorted reference
        List<Integer> walk = new ArrayList<>();
        Deque<Node> st = new ArrayDeque<>();
        Node c = t;
        while (c != null || !st.isEmpty()) { while (c != null) { st.push(c); c = c.left; } c = st.pop(); walk.add(c.key); c = c.right; }
        check(walk.size() == n, "every key is in the tree");
        for (int i = 1; i < walk.size(); i++) check(walk.get(i - 1) < walk.get(i), "in-order walk is sorted");
        System.out.printf("avl: %,d random keys inserted ; the order of the keys and the balance rule checked at every node after each 250,000 insertions ; %,d single and %,d double rotations, %.3f per insertion ; final height %d, against the bound 1.44 log2(n+2) - 0.33 = %.1f and the least possible %d%n",
                n, singles, doubles, (double) (singles + doubles) / n, t.height, 1.4405 * log2(n + 2) - 0.3277, (int) Math.ceil(log2(n + 1)));

        // ---- 4. Fibonacci trees --------------------------------------------------------------------------------------------
        StringJoiner fj = new StringJoiner(" ; ");
        for (int height = 1; height <= 25; height++) {
            nextKey = 0;
            Node ft = fibTree(height);
            int size = verify(ft, Long.MIN_VALUE, Long.MAX_VALUE);
            // F(h+2) - 1
            long a = 1, b = 1;
            for (int i = 3; i <= height + 2; i++) { long s = a + b; a = b; b = s; }
            check(size == b - 1, "Fibonacci tree size F(h+2) - 1");
            check(height <= 1.4405 * log2(size + 2) - 0.3277 + 1e-9, "bound holds for the thinnest trees");
            if (height <= 6 || height % 5 == 0) fj.add(String.format("height %d: %,d node%s", height, size, size == 1 ? "" : "s"));
        }
        System.out.printf("fibonacci: the thinnest AVL tree of each height has one branch of height h-1 and one of h-2, so its size is F(h+2) - 1 ; %s ; even these meet the bound 1.44 log2(n+2) - 0.33%n", fj);

        System.out.println("AvlTrees: " + passed + " checks passed");
    }
}
