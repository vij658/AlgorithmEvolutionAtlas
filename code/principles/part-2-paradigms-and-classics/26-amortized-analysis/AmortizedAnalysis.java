import java.util.*;

/**
 * Entry 26 of the principles catalog (Part 2): Amortized analysis
 *
 * HOW IT WORKS
 *   Some operations are occasionally expensive but cheap on average over any sequence. Doubling a dynamic array
 *   costs O(n) on a resize but O(1) amortized per append, because each resize is paid for by the appends before
 *   it. The program counts element copies to show it.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java AmortizedAnalysis.java
 *   Expected: the output in expected-output.txt, ending "AmortizedAnalysis: 2133399 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class AmortizedAnalysis {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class IntList {
        int[] data = new int[1];
        int size;
        long copies;                                        // elements copied by resizes
        void add(int x) {
            if (size == data.length) { data = Arrays.copyOf(data, size * 2); copies += size; }
            data[size++] = x;
        }
    }

    static long copiesGeometric(int n, double factor) {     // count-only simulation
        long copies = 0;
        int capacity = 1;
        for (int size = 0; size < n; size++)
            if (size == capacity) { copies += size; capacity = Math.max(capacity + 1, (int) (capacity * factor)); }
        return copies;
    }

    static long copiesLinear(int n, int step) {
        long copies = 0;
        int capacity = 1;
        for (int size = 0; size < n; size++)
            if (size == capacity) { copies += size; capacity += step; }
        return copies;
    }

    static final class TwoStackQueue {
        private final ArrayDeque<Integer> in = new ArrayDeque<>(), out = new ArrayDeque<>();
        long moves;
        void push(int x) { in.push(x); }
        int pop() {
            if (out.isEmpty()) while (!in.isEmpty()) { out.push(in.pop()); moves++; }
            return out.pop();
        }
        boolean isEmpty() { return in.isEmpty() && out.isEmpty(); }
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java AmortizedAnalysis.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        IntList list = new IntList();
        List<Integer> ref = new ArrayList<>();
        for (int i = 0; i < 100_000; i++) { int x = rnd.nextInt(); list.add(x); ref.add(x); }
        for (int i = 0; i < ref.size(); i++) check(list.data[i] == ref.get(i), "IntList keeps its contents");
        check(list.copies < 2L * list.size, "doubling: copies < 2n");
        long copies = 0;
        int capacity = 1;
        for (int size = 1; size <= 2_000_000; size++) {
            if (size - 1 == capacity) { copies += size - 1; capacity *= 2; }
            check(copies < 2L * size, "copies < 2n at every n up to 2,000,000");
        }
        check(copiesGeometric(1_000_000, 2.0) == (1L << 20) - 1, "doubling to a million copies 2^20 - 1 elements");
        double r15 = (double) copiesGeometric(1_000_000, 1.5) / 1_000_000;
        check(r15 < 3.0, "1.5x growth copies fewer than 3 elements per append");
        long lin = copiesLinear(100_000, 10);
        check(lin > 100_000_000L, "growing by a constant 10 copies a huge amount");
        System.out.printf("1,000,000 appends: doubling copies %d elements (%.3f per append), 1.5x growth %.3f per append; +10 growth at n = 100,000 copies %,d elements (%.0f per append)%n",
                copiesGeometric(1_000_000, 2.0), copiesGeometric(1_000_000, 2.0) / 1e6, r15, lin, lin / 100_000.0);
        TwoStackQueue q = new TwoStackQueue();
        ArrayDeque<Integer> ref2 = new ArrayDeque<>();
        long pushes = 0;
        for (int i = 0; i < 100_000; i++) {
            if (ref2.isEmpty() || rnd.nextInt(3) != 0) { int x = rnd.nextInt(); q.push(x); ref2.addLast(x); pushes++; }
            else check(q.pop() == ref2.pollFirst(), "two-stack queue is FIFO");
        }
        check(q.moves <= pushes, "each element moves between stacks at most once");

        StringBuilder grow = new StringBuilder();              // the StringBuilder Javadoc says: twice the old capacity, plus 2
        int capNow = grow.capacity();
        List<Integer> sbCaps = new ArrayList<>(List.of(capNow));
        for (int i = 0; i < 5000; i++) {
            grow.append('x');
            if (grow.capacity() != capNow) {
                check(grow.capacity() == 2 * capNow + 2, "StringBuilder grows to twice the old capacity plus 2");
                capNow = grow.capacity();
                sbCaps.add(capNow);
            }
        }
        System.out.println("StringBuilder capacities while appending 5,000 chars: " + sbCaps);
        try {                                                   // optional probe, needs: java --add-opens java.base/java.util=ALL-UNNAMED AmortizedAnalysis.java
            java.lang.reflect.Field f = ArrayList.class.getDeclaredField("elementData");
            f.setAccessible(true);
            ArrayList<Integer> al = new ArrayList<>();
            List<Integer> caps = new ArrayList<>();
            for (int i = 0; i < 5000; i++) {
                al.add(i);
                int cap = ((Object[]) f.get(al)).length;
                if (caps.isEmpty() || caps.get(caps.size() - 1) != cap) caps.add(cap);
            }
            for (int i = 1; i < caps.size(); i++)
                if (caps.get(i) != caps.get(i - 1) + (caps.get(i - 1) >> 1)) throw new AssertionError("ArrayList growth is not old + old/2");
            System.out.println("ArrayList capacities while adding 5,000 elements (each is the previous plus half of it): " + caps);
        } catch (ReflectiveOperationException | RuntimeException e) {
            System.out.println("(ArrayList growth probe skipped; run with --add-opens java.base/java.util=ALL-UNNAMED to enable it)");
        }
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("AmortizedAnalysis: " + passed + " checks passed");
    }
}
