import java.util.*;

/**
 * Era 5, topic 4: hashing (IBM, 1953-1957).
 *
 * HOW IT WORKS
 *   To find a record without searching the whole file, compute its place from its key. A hash function scrambles the
 *   key into a number between 0 and m - 1, the record goes into that slot, and a search computes the same number and
 *   looks only there. Two keys can land on the same slot (a collision). Luhn's memorandum of January 1953 kept a
 *   bucket of records at each slot (chaining). Amdahl's idea for the IBM 701 assembler, published by Peterson in
 *   1957, keeps one table: if the slot is taken, try the next one, and the next (open addressing with linear
 *   probing). Either way, while the table is not too full, a search takes a few probes however large the file is.
 *   Dumey (1956) took the key as a number and kept the remainder after dividing by a prime.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Luhn's example of a bucket number: add the digits of a phone number in pairs and keep the last digit of each sum.
 *   2. Chaining and linear probing at load factors from 0.5 to 0.95: average probes for a search that finds its key
 *      and for one that does not, measured, against the classical formulas.
 *   3. Peterson's 1957 experiment: a store of 10,000 records in buckets of 20, filled with random keys from 40% to
 *      100%, and buckets of 1 with 500 records; our averages beside the figures in his tables.
 *   4. Remainders: keys that share a pattern, divided by a power of two and by a prime.
 *   5. The payoff: probes per search as the file grows from a thousand to a million keys, against binary search.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Hashing.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Hashing {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1953L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed >>> 1;
    }

    static int rnd(int n) { return (int) ((next() >>> 20) % n); }

    // ---- 1. Luhn's bucket number --------------------------------------------------------------------------------------
    static String luhnBucket(String digits) {
        StringBuilder b = new StringBuilder();
        for (int i = 0; i + 1 < digits.length(); i += 2) b.append(((digits.charAt(i) - '0') + (digits.charAt(i + 1) - '0')) % 10);
        return b.toString();
    }

    // ---- 2. tables ------------------------------------------------------------------------------------------------------
    /** A multiplicative scramble of a 64-bit key into 0 .. m-1. */
    static int h(long key, int m) {
        long x = key * 0x9E3779B97F4A7C15L;
        x ^= x >>> 29;
        return (int) Long.remainderUnsigned(x, m);
    }

    static final class Chained {
        final List<List<Long>> slots = new ArrayList<>();
        final int m;
        Chained(int m) { this.m = m; for (int i = 0; i < m; i++) slots.add(new ArrayList<>()); }
        void put(long k) { slots.get(h(k, m)).add(k); }
        /** Keys compared to find k (0 if its bucket is empty). */
        int probes(long k) {
            List<Long> b = slots.get(h(k, m));
            for (int i = 0; i < b.size(); i++) if (b.get(i) == k) return i + 1;
            return b.size();
        }
    }

    static final class Linear {
        final long[] t;
        final boolean[] used;
        final int m;
        Linear(int m) { this.m = m; t = new long[m]; used = new boolean[m]; }
        void put(long k) { int i = h(k, m); while (used[i]) i = (i + 1) % m; used[i] = true; t[i] = k; }
        /** Slots looked at to find k, or to reach an empty slot. */
        int probes(long k) {
            int i = h(k, m), p = 1;
            while (used[i] && t[i] != k) { i = (i + 1) % m; p++; }
            return p;
        }
    }

    // ---- 3. Peterson's buckets -------------------------------------------------------------------------------------------
    /** Fill nb buckets of capacity c with n random keys; overflow goes to the next bucket with room (circularly).
     *  Return the average number of buckets read to find a record. */
    static double peterson(int nb, int c, int n) {
        int[] fill = new int[nb];
        long buckets = 0;
        for (int r = 0; r < n; r++) {
            int b = rnd(nb), read = 1;
            while (fill[b] == c) { b = (b + 1) % nb; read++; }
            fill[b]++;
            buckets += read;   // a later search follows the same path: the record is found after the same buckets
        }
        return (double) buckets / n;
    }

    public static void main(String[] args) {
        // ---- 1. Luhn ---------------------------------------------------------------------------------------------------
        String phone = "9147213350";
        String bucket = luhnBucket(phone);
        check(bucket.length() == 5, "five pairs, five digits");
        int[] count = new int[100000];
        int phones = 200000;
        for (int i = 0; i < phones; i++) {
            StringBuilder sb = new StringBuilder();
            for (int d = 0; d < 10; d++) sb.append(rnd(10));
            count[Integer.parseInt(luhnBucket(sb.toString()))]++;
        }
        int empty = 0, most = 0;
        for (int c : count) { if (c == 0) empty++; most = Math.max(most, c); }
        double expectEmpty = 100000 * Math.exp(-2.0);
        check(Math.abs(empty - expectEmpty) < 600, "the buckets fill like random throws");
        System.out.printf("luhn: the number %s in pairs 91 47 21 33 50 ; add each pair and keep the last digit: %s, the bucket number ; %,d random 10-digit numbers into the 100,000 buckets: %,d buckets empty (random throws would leave about %,.0f), the fullest holds %d, so a search reads one small bucket instead of the whole list%n",
                phone, bucket, phones, empty, expectEmpty, most);

        // ---- 2. chaining against linear probing -----------------------------------------------------------------------------
        int m = 100003;
        StringJoiner rows = new StringJoiner(" ; ");
        for (double a : new double[]{0.5, 0.7, 0.8, 0.9, 0.95}) {
            int n = (int) Math.round(a * m);
            Chained ch = new Chained(m);
            Linear lp = new Linear(m);
            long[] keys = new long[n];
            for (int i = 0; i < n; i++) { keys[i] = next(); ch.put(keys[i]); lp.put(keys[i]); }
            long chHit = 0, lpHit = 0, chMiss = 0, lpMiss = 0;
            for (long k : keys) { chHit += ch.probes(k); lpHit += lp.probes(k); }
            int misses = 100000;
            for (int i = 0; i < misses; i++) { long k = next(); chMiss += ch.probes(k); lpMiss += lp.probes(k); }
            double cH = (double) chHit / n, lH = (double) lpHit / n, cM = (double) chMiss / misses, lM = (double) lpMiss / misses;
            double fcH = 1 + a / 2, fcM = a, flH = 0.5 * (1 + 1 / (1 - a)), flM = 0.5 * (1 + 1 / ((1 - a) * (1 - a)));
            check(Math.abs(cH - fcH) / fcH < 0.02 && Math.abs(cM - fcM) / fcM < 0.03, "chaining follows 1 + a/2 and a");
            if (a < 0.93) check(Math.abs(lH - flH) / flH < 0.05 && Math.abs(lM - flM) / flM < 0.05, "linear probing follows the formulas");
            else check(lH > flH * 0.9 && lM > flM * 0.9, "near-full table: long runs");
            rows.add(String.format("%.2f full: chaining %.2f / %.2f (formula %.2f / %.2f), linear probing %.2f / %.2f (formula %.2f / %.2f)",
                    a, cH, cM, fcH, fcM, lH, lM, flH, flM));
        }
        System.out.printf("probes: table of %,d slots, random keys ; average probes for a search that finds its key / one that does not: %s ; formulas: chaining 1 + a/2 and a, linear probing (1 + 1/(1-a))/2 and (1 + 1/(1-a)^2)/2 ; at 0.95 a single table strays far from the formula, because a few very long runs of filled slots dominate%n", m, rows);

        // ---- 3. Peterson 1957 -----------------------------------------------------------------------------------------------
        int[] pct = {40, 60, 80, 90, 95, 100};
        double[] his = {1.000, 1.002, 1.033, 1.134, 1.334, 4.041};
        StringJoiner pj = new StringJoiner(" ; ");
        int runs = 200;
        double[] ours = new double[pct.length];
        for (int i = 0; i < pct.length; i++) {
            double sum = 0;
            for (int r = 0; r < runs; r++) sum += peterson(500, 20, 10000 * pct[i] / 100);
            ours[i] = sum / runs;
            pj.add(String.format("%d%%: %.3f (his %.3f)", pct[i], ours[i], his[i]));
        }
        for (int i = 0; i < 5; i++) check(Math.abs(ours[i] - his[i]) < 0.04, "Peterson's bucket figures up to 95%");
        check(ours[5] > 3.3 && ours[5] < 4.7, "the full store lies within Peterson's run-to-run range");
        int[] pct1 = {10, 70, 100};
        double[] his1 = {1.053, 2.260, 16.914};
        StringJoiner pj1 = new StringJoiner(" ; ");
        double[] ours1 = new double[3];
        for (int i = 0; i < 3; i++) {
            double sum = 0;
            for (int r = 0; r < 2000; r++) sum += peterson(500, 1, 500 * pct1[i] / 100);
            ours1[i] = sum / 2000;
            pj1.add(String.format("%d%%: %.3f (his %.3f)", pct1[i], ours1[i], his1[i]));
        }
        check(Math.abs(ours1[0] - his1[0]) < 0.03 && Math.abs(ours1[1] - his1[1]) < 0.15, "Peterson's single-record figures");
        System.out.printf("peterson: 10,000 records in 500 buckets of 20, overflow into the next bucket with room, %d random fillings each ; average buckets read to find a record: %s ; buckets of 1, 500 records, 2,000 fillings each: %s%n",
                runs, pj, pj1);

        // ---- 4. remainders ----------------------------------------------------------------------------------------------------
        int nk = 1000;
        Set<Integer> pow2 = new HashSet<>(), prime = new HashSet<>();
        for (int i = 1; i <= nk; i++) { long key = 64L * i; pow2.add((int) (key % 1024)); prime.add((int) (key % 1021)); }
        check(pow2.size() == 16 && prime.size() == nk, "a prime spreads patterned keys");
        Set<Integer> dec = new HashSet<>(), decp = new HashSet<>();
        for (int i = 0; i < nk; i++) { long key = 5550000L + 100L * i; dec.add((int) (key % 1000)); decp.add((int) (key % 1009)); }
        check(dec.size() == 10 && decp.size() == nk, "keys ending in 00");
        System.out.printf("prime: %,d keys that are multiples of 64, by remainder: dividing by 1024 uses %d slots, dividing by the prime 1021 uses %d ; %,d phone-like keys ending in 00: the last three digits give %d slots, the remainder after the prime 1009 gives %d%n",
                nk, pow2.size(), prime.size(), nk, dec.size(), decp.size());

        // ---- 5. growth ----------------------------------------------------------------------------------------------------------
        StringJoiner gj = new StringJoiner(" ; ");
        for (int n : new int[]{1000, 10000, 100000, 1000000}) {
            Linear lp = new Linear(2 * n + 1);
            long[] keys = new long[n];
            for (int i = 0; i < n; i++) { keys[i] = next(); lp.put(keys[i]); }
            long hp = 0;
            for (long k : keys) hp += lp.probes(k);
            long[] sorted = keys.clone();
            Arrays.sort(sorted);
            long bp = 0;
            for (long k : keys) {
                int lo = 0, hi = n - 1;
                while (true) { int mid = (lo + hi) >>> 1; bp++; if (sorted[mid] == k) break; if (sorted[mid] < k) lo = mid + 1; else hi = mid - 1; }
            }
            double avgH = (double) hp / n, avgB = (double) bp / n;
            check(avgH < 1.6, "half-full table: about 1.5 probes");
            gj.add(String.format("%,d keys: hashing %.2f probes, binary search %.2f", n, avgH, avgB));
        }
        System.out.printf("growth: a table kept half full, against binary search in a sorted list ; average probes to find a key: %s ; hashing stays level while binary search adds a step each time the file doubles%n", gj);

        System.out.println("Hashing: " + passed + " checks passed");
    }
}
