import java.util.*;

/**
 * Entry 24 of the principles catalog (Part 2): Greedy algorithms and the exchange argument
 *
 * HOW IT WORKS
 *   Take the locally best choice and never look back. It is only correct when an exchange argument shows any
 *   optimal solution can be turned into the greedy one without getting worse; interval scheduling and Huffman
 *   coding pass, and coin change with odd denominations is the counterexample.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java GreedyAlgorithms.java
 *   Expected: the output in expected-output.txt, ending "GreedyAlgorithms: 2534 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class GreedyAlgorithms {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static double log2(double x) { return Math.log(x) / Math.log(2); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static int maxNonOverlapping(int[][] intervals) {      // each {start, end}; touching ends are allowed
        int[][] s = intervals.clone();
        Arrays.sort(s, Comparator.comparingInt(x -> x[1]));   // earliest finish first
        int count = 0, lastEnd = Integer.MIN_VALUE;
        for (int[] iv : s)
            if (iv[0] >= lastEnd) { count++; lastEnd = iv[1]; }
        return count;
    }

    static int earliestStartGreedy(int[][] intervals) {    // the tempting but wrong rule
        int[][] s = intervals.clone();
        Arrays.sort(s, Comparator.comparingInt(x -> x[0]));
        int count = 0, lastEnd = Integer.MIN_VALUE;
        for (int[] iv : s)
            if (iv[0] >= lastEnd) { count++; lastEnd = iv[1]; }
        return count;
    }

    record Node(long weight, int order, char symbol, Node left, Node right) {}

    static Map<Character, String> huffman(Map<Character, Long> freq) {
        PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingLong(Node::weight).thenComparingInt(Node::order));
        int order = 0;
        for (Map.Entry<Character, Long> e : new TreeMap<>(freq).entrySet())
            pq.add(new Node(e.getValue(), order++, e.getKey(), null, null));
        while (pq.size() > 1) {
            Node a = pq.poll(), b = pq.poll();              // merge the two lightest subtrees
            pq.add(new Node(a.weight() + b.weight(), order++, '\0', a, b));
        }
        Map<Character, String> codes = new TreeMap<>();
        assign(pq.poll(), "", codes);
        return codes;
    }

    private static void assign(Node n, String prefix, Map<Character, String> out) {
        if (n.left() == null) { out.put(n.symbol(), prefix.isEmpty() ? "0" : prefix); return; }
        assign(n.left(), prefix + "0", out);
        assign(n.right(), prefix + "1", out);
    }

    static long bruteMergeCost(List<Long> ws) {            // try every pair at every step
        if (ws.size() == 1) return 0;
        long best = Long.MAX_VALUE;
        for (int i = 0; i < ws.size(); i++)
            for (int j = i + 1; j < ws.size(); j++) {
                List<Long> next = new ArrayList<>(ws);
                long merged = next.get(i) + next.get(j);
                next.remove(j);
                next.remove(i);
                next.add(merged);
                best = Math.min(best, merged + bruteMergeCost(next));
            }
        return best;
    }

    // ----------------------------------------------------------------------------------------------------
    // Helpers copied from entry 23 (dynamic-programming), used here for comparison or cross-checking
    // ----------------------------------------------------------------------------------------------------
    static int minCoins(int[] coins, int amount) {
        final int INF = Integer.MAX_VALUE / 2;
        int[] dp = new int[amount + 1];
        Arrays.fill(dp, INF);
        dp[0] = 0;
        for (int a = 1; a <= amount; a++)
            for (int c : coins)
                if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
        return dp[amount] >= INF ? -1 : dp[amount];
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java GreedyAlgorithms.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        for (int t = 0; t < 1000; t++) {
            int n = 1 + rnd.nextInt(12);
            int[][] iv = new int[n][2];
            for (int i = 0; i < n; i++) { int s = rnd.nextInt(20); iv[i][0] = s; iv[i][1] = s + 1 + rnd.nextInt(8); }
            int brute = 0;
            for (int mask = 0; mask < (1 << n); mask++) {
                boolean ok = true;
                int size = Integer.bitCount(mask);
                for (int i = 0; i < n && ok; i++)
                    for (int j = i + 1; j < n && ok; j++)
                        if ((mask >> i & 1) == 1 && (mask >> j & 1) == 1 && !(iv[i][1] <= iv[j][0] || iv[j][1] <= iv[i][0])) ok = false;
                if (ok) brute = Math.max(brute, size);
            }
            check(maxNonOverlapping(iv) == brute, "earliest-finish greedy vs subset enumeration");
        }
        int[][] trap = {{0, 10}, {1, 2}, {3, 4}};
        check(earliestStartGreedy(trap) == 1 && maxNonOverlapping(trap) == 2, "earliest-start greedy is wrong on {[0,10],[1,2],[3,4]}");

        Map<Character, Long> freq = new TreeMap<>();
        freq.put('a', 45L); freq.put('b', 13L); freq.put('c', 12L); freq.put('d', 16L); freq.put('e', 9L); freq.put('f', 5L);
        Map<Character, String> codes = huffman(freq);
        long bits = 0, total = 0;
        for (Map.Entry<Character, Long> e : freq.entrySet()) { bits += e.getValue() * codes.get(e.getKey()).length(); total += e.getValue(); }
        check(bits == 224 && total == 100, "Huffman total cost 224 bits per 100 symbols");
        for (String x : codes.values()) for (String y : codes.values()) if (x != y) check(!y.startsWith(x), "prefix-free");
        double h = 0;
        for (long fq : freq.values()) { double p = fq / 100.0; h -= p * log2(p); }
        double avg = bits / 100.0;
        check(h <= avg && avg < h + 1, "entropy <= Huffman average length < entropy + 1");
        System.out.printf("Huffman: %d bits per %d symbols (%.2f bits/symbol), entropy %.4f; fixed 3-bit codes need 300%n", bits, total, avg, h);
        for (int t = 0; t < 500; t++) {
            int n = 2 + rnd.nextInt(6);
            Map<Character, Long> fm = new TreeMap<>();
            List<Long> ws = new ArrayList<>();
            for (int i = 0; i < n; i++) { long w = 1 + rnd.nextInt(50); fm.put((char) ('a' + i), w); ws.add(w); }
            Map<Character, String> cs = huffman(fm);
            long cost = 0;
            for (Map.Entry<Character, Long> e : fm.entrySet()) cost += e.getValue() * cs.get(e.getKey()).length();
            check(cost == bruteMergeCost(ws), "Huffman cost equals the best of all merge orders");
        }
        int[] us = {1, 5, 10, 25};
        for (int amount = 1; amount <= 1000; amount++) {
            int rest = amount, count = 0;
            for (int i = us.length - 1; i >= 0; i--) { count += rest / us[i]; rest %= us[i]; }
            check(count == minCoins(us, amount), "greedy change is optimal for 1,5,10,25 at " + amount);
        }
        int[] odd = {1, 3, 4};
        int greedy6 = 0, rest = 6;
        for (int i = odd.length - 1; i >= 0; i--) { greedy6 += rest / odd[i]; rest %= odd[i]; }
        check(greedy6 == 3 && minCoins(odd, 6) == 2, "greedy fails for coins 1,3,4 and amount 6");
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("GreedyAlgorithms: " + passed + " checks passed");
    }
}
