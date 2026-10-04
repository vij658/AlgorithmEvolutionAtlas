import java.math.BigInteger;
import java.util.*;

/**
 * Entry 29 of the principles catalog (Part 2): Fisher-Yates shuffle and reservoir sampling
 *
 * HOW IT WORKS
 *   Fisher-Yates shuffles by walking backwards and swapping each position with a random earlier (or same)
 *   position, giving every permutation exactly once. Reservoir sampling keeps k items from a stream of unknown
 *   length, replacing an item with probability k/i at step i, so every item ends up kept with probability k/n.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ShuffleAndReservoir.java
 *   Expected: the output in expected-output.txt, ending "ShuffleAndReservoir: 160 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class ShuffleAndReservoir {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static double log2(double x) { return Math.log(x) / Math.log(2); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static void shuffle(int[] a, Random rnd) {
        for (int i = a.length - 1; i > 0; i--) {
            int j = rnd.nextInt(i + 1);                     // 0..i inclusive
            int t = a[i]; a[i] = a[j]; a[j] = t;
        }
    }

    static int[] reservoirSample(int[] stream, int k, Random rnd) {   // reads the stream once, keeps k items
        int[] res = Arrays.copyOf(stream, k);
        for (int i = k; i < stream.length; i++) {
            int j = rnd.nextInt(i + 1);
            if (j < k) res[j] = stream[i];
        }
        return res;
    }

    static Map<List<Integer>, Integer> naiveOutcomes(int n) {   // every sequence of random indices, exactly
        Map<List<Integer>, Integer> counts = new TreeMap<>((x, y) -> x.toString().compareTo(y.toString()));
        int total = 1;
        for (int i = 0; i < n; i++) total *= n;
        for (int code = 0; code < total; code++) {
            Integer[] a = new Integer[n];
            for (int i = 0; i < n; i++) a[i] = i;
            int c = code;
            for (int i = 0; i < n; i++) { int j = c % n; c /= n; Integer t = a[i]; a[i] = a[j]; a[j] = t; }
            counts.merge(Arrays.asList(a), 1, Integer::sum);
        }
        return counts;
    }

    static Set<List<Integer>> fisherYatesOutcomes(int n) {
        Set<List<Integer>> seen = new HashSet<>();
        int total = 1;
        for (int i = 2; i <= n; i++) total *= i;
        for (int code = 0; code < total; code++) {
            Integer[] a = new Integer[n];
            for (int i = 0; i < n; i++) a[i] = i;
            int c = code;
            for (int i = n - 1; i > 0; i--) { int j = c % (i + 1); c /= (i + 1); Integer t = a[i]; a[i] = a[j]; a[j] = t; }
            seen.add(Arrays.asList(a));
        }
        return seen;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java ShuffleAndReservoir.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        Map<List<Integer>, Integer> naive3 = naiveOutcomes(3);
        int total3 = naive3.values().stream().mapToInt(Integer::intValue).sum();
        check(total3 == 27 && naive3.size() == 6 && new HashSet<>(naive3.values()).size() > 1, "naive shuffle of 3 is not uniform");
        check(fisherYatesOutcomes(3).size() == 6 && fisherYatesOutcomes(4).size() == 24 && fisherYatesOutcomes(5).size() == 120, "Fisher-Yates reaches every permutation exactly once");
        Map<List<Integer>, Integer> naive4 = naiveOutcomes(4);
        int max4 = Collections.max(naive4.values()), min4 = Collections.min(naive4.values());
        check(max4 > min4, "naive shuffle of 4 is not uniform");
        System.out.println("naive shuffle of [0,1,2]: outcome counts out of 27 = " + naive3);
        System.out.println("naive shuffle of 4 items: 256 equally likely index sequences, per-permutation counts range from " + min4 + " to " + max4 + " (a uniform shuffle would give 256/24 = 10.67 each)");
        int[] stream = new int[10];
        for (int i = 0; i < 10; i++) stream[i] = i;
        int trials = 200_000;
        int[] hits = new int[10];
        for (int t = 0; t < trials; t++) for (int x : reservoirSample(stream, 3, rnd)) hits[x]++;
        double worst = 0;
        for (int i = 0; i < 10; i++) worst = Math.max(worst, Math.abs(hits[i] / (double) trials - 0.3));
        check(worst < 0.005, "each item is kept with probability k/n = 0.3");
        System.out.printf("reservoir sample of 3 from 10: every item kept with frequency within %.4f of 0.3%n", worst);
        int[] a = {0, 1, 2, 3, 4, 5, 6, 7};
        shuffle(a, rnd);
        Arrays.sort(a);
        check(Arrays.equals(a, new int[]{0, 1, 2, 3, 4, 5, 6, 7}), "shuffle keeps the same elements");

        for (int n = 3; n <= 5; n++) {                          // Sattolo's off-by-one: j drawn from 0..i-1 instead of 0..i
            Set<List<Integer>> seen = new HashSet<>();
            int total = 1;
            for (int i = 2; i <= n - 1; i++) total *= i;         // (n - 1)! random-choice sequences
            for (int code = 0; code < total; code++) {
                Integer[] arr = new Integer[n];
                for (int i = 0; i < n; i++) arr[i] = i;
                int c = code;
                for (int i = n - 1; i > 0; i--) { int j = c % i; c /= i; Integer t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
                for (int i = 0; i < n; i++) check(arr[i] != i, "with nextInt(i) no element can stay where it started");
                seen.add(Arrays.asList(arr));
            }
            check(seen.size() == total, "nextInt(i) reaches only the (n-1)! cyclic permutations");
        }
        System.out.println("shuffle with nextInt(i) instead of nextInt(i + 1): for n = 3, 4, 5 no element ever stays in place, and only 2, 6, 24 of the 6, 24, 120 permutations are reachable");

        BigInteger twoTo48 = BigInteger.ONE.shiftLeft(48), f16 = BigInteger.ONE, f52 = BigInteger.ONE;
        for (int i = 2; i <= 16; i++) f16 = f16.multiply(BigInteger.valueOf(i));
        BigInteger f17 = f16.multiply(BigInteger.valueOf(17));
        for (int i = 2; i <= 52; i++) f52 = f52.multiply(BigInteger.valueOf(i));
        double lg52 = 0;
        for (int i = 2; i <= 52; i++) lg52 += log2(i);
        check(f16.compareTo(twoTo48) < 0 && f17.compareTo(twoTo48) > 0, "16! < 2^48 < 17!");
        check((int) Math.ceil(lg52) == 226 && f52.bitLength() == 226, "52! needs 226 bits");
        System.out.printf("java.util.Random keeps a 48-bit state: at most 2^48 = %s shuffles. 16! = %s fits under that, 17! = %s does not; a 52-card deck needs log2(52!) = %.2f, so 226 bits of seed%n",
                twoTo48, f16, f17, lg52);
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(2026));
        System.out.println("ShuffleAndReservoir: " + passed + " checks passed");
    }
}
