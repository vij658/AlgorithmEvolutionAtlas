import java.math.BigInteger;
import java.util.*;

/**
 * Entry 30 of the principles catalog (Part 2): Floyd's cycle detection and Pollard's rho
 *
 * HOW IT WORKS
 *   Floyd's tortoise and hare: one pointer moves one step, the other two; if there is a cycle they meet inside
 *   it, and restarting one pointer from the head finds the cycle's start in O(1) memory. Pollard's rho uses the
 *   same idea on x -> x^2 + c mod n to find a factor.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java CycleDetection.java
 *   Expected: the output in expected-output.txt, ending "CycleDetection: 5785 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class CycleDetection {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long gcd(long a, long b) { while (b != 0) { long t = a % b; a = b; b = t; } return Math.abs(a); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static final class ListNode {
        final int val;
        ListNode next;
        ListNode(int v) { val = v; }
    }

    static ListNode cycleStart(ListNode head) {            // node where the cycle begins, or null
        ListNode slow = head, fast = head;
        while (fast != null && fast.next != null) {
            slow = slow.next;
            fast = fast.next.next;
            if (slow == fast) {                             // met inside the cycle
                slow = head;
                while (slow != fast) { slow = slow.next; fast = fast.next; }
                return slow;
            }
        }
        return null;
    }

    static long rhoIterations;

    static long pollardRho(long n) {                       // n composite and < 3e9 so products fit in a long
        if (n % 2 == 0) return 2;
        for (long c = 1; ; c++) {
            long x = 2, y = 2, d = 1;
            while (d == 1) {
                rhoIterations++;
                x = (x * x + c) % n;
                y = (y * y + c) % n;
                y = (y * y + c) % n;                        // the hare moves two steps
                d = gcd(Math.abs(x - y), n);
            }
            if (d != n) return d;                           // d == n: the walk closed too soon, retry with another c
        }
    }

    static BigInteger randomPrime(Random rnd, int lo, int hi) {
        while (true) {
            BigInteger p = BigInteger.valueOf(lo + rnd.nextInt(hi - lo));
            if (p.isProbablePrime(40)) return p;
        }
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java CycleDetection.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int len = 1; len <= 30; len++)
            for (int entry = 0; entry < len; entry++)
                for (int cyc = 1; cyc <= 12; cyc++) {
                    ListNode[] nodes = new ListNode[len + cyc];
                    for (int i = 0; i < nodes.length; i++) nodes[i] = new ListNode(i);
                    for (int i = 0; i + 1 < nodes.length; i++) nodes[i].next = nodes[i + 1];
                    nodes[nodes.length - 1].next = nodes[entry];            // cycle back to node `entry`
                    check(cycleStart(nodes[0]) == nodes[entry], "cycle start found: tail " + len + ", entry " + entry + ", cycle " + cyc);
                }
        ListNode a = new ListNode(1);
        a.next = new ListNode(2);
        check(cycleStart(a) == null && cycleStart(null) == null, "no cycle");
        ListNode self = new ListNode(7);
        self.next = self;
        check(cycleStart(self) == self, "a one-node self-loop");
        long f = pollardRho(8051);
        check(f == 83 || f == 97, "8051 = 83 * 97");
        f = pollardRho(10403);
        check(f == 101 || f == 103, "10403 = 101 * 103");
        long totalRho = 0, totalTrial = 0;
        int cases = 200;
        for (int t = 0; t < cases; t++) {
            long p = randomPrime(rnd, 20_000, 46_000).longValue(), q;
            do { q = randomPrime(rnd, 20_000, 46_000).longValue(); } while (q == p);
            long n = p * q;
            rhoIterations = 0;
            long d = pollardRho(n);
            check(d != 1 && d != n && n % d == 0, "nontrivial factor of " + n);
            totalRho += rhoIterations;
            totalTrial += Math.min(p, q) / 2;                  // odd trial divisions up to the smaller factor
        }
        System.out.printf("semiprimes of two random primes between 20,000 and 46,000: Pollard rho averaged %.0f iterations, trial division would need about %.0f divisions%n",
                totalRho / (double) cases, totalTrial / (double) cases);
        check(totalRho < totalTrial / 10, "rho needs far fewer steps than trial division here");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("CycleDetection: " + passed + " checks passed");
    }
}
