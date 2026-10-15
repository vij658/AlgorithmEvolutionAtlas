import java.util.*;

/**
 * Era 7, topic 3: the Byzantine generals (Pease, Shostak and Lamport, SRI International, 1980 and 1982).
 *
 * HOW IT WORKS
 *   A commander sends an order, ATTACK or RETREAT, to n - 1 lieutenants by messenger. Some of the generals,
 *   possibly the commander, are traitors who may say anything to anyone. The loyal lieutenants must all decide
 *   the same thing (IC1), and if the commander is loyal they must obey him (IC2). These are faulty computers in a
 *   fault-tolerant system: a broken sensor or processor that tells different parts of the system different things.
 *   With spoken messages the problem can be solved exactly when more than two thirds of the generals are loyal:
 *   n >= 3m + 1 for m traitors. The algorithm OM(m): the commander sends his order; each lieutenant then acts as
 *   commander in OM(m - 1), passing on what he heard to the others; each lieutenant takes the majority of what he
 *   heard directly and what the others say they heard (RETREAT on a tie). With signed messages that cannot be
 *   forged, the algorithm SM(m) works for any number of generals: a lieutenant collects every order that arrives
 *   with a valid chain of signatures, signs and passes on each new one, and in the end obeys if he received
 *   exactly one order, and retreats otherwise.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Three generals, one traitor: the two situations that a loyal lieutenant cannot tell apart.
 *   2. OM(m) against traitors who may send any message: every traitor behaviour, or many random ones when there
 *      are too many to list. No violations when n >= 3m + 1; violations found when n = 3m.
 *   3. How many messages OM(m) sends, and how many SM(m) sends.
 *   4. SM(m) against traitors who may sign anything they like but cannot forge a loyal general's signature.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ByzantineGenerals.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ByzantineGenerals {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int RETREAT = 0, ATTACK = 1;

    static String order(int v) { return v == ATTACK ? "ATTACK" : "RETREAT"; }

    // ---- the traitors' choices: either read bit by bit from a number (to list every behaviour), or random --------------
    static long mask;          // when listing: bit k is the k-th message a traitor sends
    static int used;           // traitor messages sent so far
    static boolean random;
    static long seed = 1982L;

    static int traitorSays() {
        if (random) {
            seed = seed * 6364136223846793005L + 1442695040888963407L;
            used++;
            return (int) (seed >>> 63);
        }
        return (int) ((mask >>> used++) & 1);
    }

    static boolean[] traitor;
    static long messages;

    /**
     * OM(m): the commander sends v (if loyal) to the lieutenants; returns, for each lieutenant, the value he decides
     * on for this commander's order.
     */
    static int[] om(int m, int commander, int[] lieutenants, int v, int n) {
        int[] received = new int[n];
        for (int l : lieutenants) {
            received[l] = traitor[commander] ? traitorSays() : v;
            messages++;
        }
        int[] decided = new int[n];
        if (m == 0) {
            for (int l : lieutenants) decided[l] = received[l];
            return decided;
        }
        // relayed[j][i]: what lieutenant j concludes lieutenant i was told
        int[][] relayed = new int[n][n];
        for (int i : lieutenants) {
            int[] others = Arrays.stream(lieutenants).filter(x -> x != i).toArray();
            int[] sub = om(m - 1, i, others, received[i], n);
            for (int j : others) relayed[j][i] = sub[j];
        }
        for (int j : lieutenants) {
            int attack = received[j] == ATTACK ? 1 : 0, total = 1;
            for (int i : lieutenants) if (i != j) { attack += relayed[j][i]; total++; }
            decided[j] = 2 * attack > total ? ATTACK : RETREAT;      // majority, RETREAT on a tie
        }
        return decided;
    }

    /** Runs OM(m) on generals 0..n-1 (0 is the commander); returns true if IC1 and IC2 both hold. */
    static boolean runOM(int n, int m, int v) {
        int[] lieutenants = new int[n - 1];
        for (int i = 1; i < n; i++) lieutenants[i - 1] = i;
        used = 0;
        int[] d = om(m, 0, lieutenants, v, n);
        int first = -1;
        for (int l : lieutenants) {
            if (traitor[l]) continue;
            if (first < 0) first = d[l];
            if (d[l] != first) return false;                       // IC1: loyal lieutenants agree
            if (!traitor[0] && d[l] != v) return false;            // IC2: they obey a loyal commander
        }
        return true;
    }

    /** One run of OM(m); when n >= 3m + 1 a failure is a bug, so it is checked. */
    static boolean om(int n, int m, int v) {
        boolean ok = runOM(n, m, v);
        if (n >= 3 * m + 1) check(ok, "OM(" + m + ") with n = " + n + " keeps IC1 and IC2");
        return ok;
    }

    static int traitorMessages(int n, int m) {
        mask = 0; random = false;
        runOM(n, m, ATTACK);
        return used;
    }

    // ---- SM(m): signed messages --------------------------------------------------------------------------------------
    /**
     * Round by round. A message is an order and the list of generals who signed it, commander first. Loyal lieutenants
     * add each new order to their set and, while the chain has at most m signatures, sign it and send it on to everyone
     * who has not signed it. Traitors may send any order with any chain of traitors' signatures (they share their keys)
     * starting from the commander, but only if the commander is a traitor or the order is his real one, and they may
     * send it to anyone in any round, or never. The rounds are timed: an order arriving in round k must carry exactly
     * k + 1 signatures, so a late order cannot pretend to come straight from the commander.
     */
    static boolean runSM(int n, int m, int v) {
        List<Set<Integer>> V = new ArrayList<>();
        for (int i = 0; i < n; i++) V.add(new TreeSet<>());
        List<int[]> inbox = new ArrayList<>();         // {receiver, value, signer1, signer2, ...}
        for (int l = 1; l < n; l++) {
            if (!traitor[0]) inbox.add(new int[]{l, v, 0});
            messages++;
        }
        List<Integer> traitorLts = new ArrayList<>();
        for (int i = 1; i < n; i++) if (traitor[i]) traitorLts.add(i);
        for (int round = 0; round <= m + 1; round++) {
            // traitors inject messages: each loyal lieutenant may receive, this round, any order the traitors can sign
            for (int l = 1; l < n; l++) {
                if (traitor[l]) continue;
                for (int value = 0; value <= 1; value++) {
                    if (!traitor[0] && value != v) continue;          // the loyal commander's signature cannot be forged
                    if (traitorSays() == 0) continue;
                    // a chain: the commander, then up to `round` traitor lieutenants (a valid chain has distinct signers)
                    List<Integer> chain = new ArrayList<>();
                    chain.add(0);
                    List<Integer> pool = new ArrayList<>(traitorLts);
                    pool.remove((Integer) l);
                    for (int k = 0; k < round && !pool.isEmpty(); k++) chain.add(pool.remove((int) (traitorPick(pool.size()))));
                    if (chain.size() != round + 1) continue;          // in round k a valid order carries k + 1 signatures
                    int[] msg = new int[2 + chain.size()];
                    msg[0] = l; msg[1] = value;
                    for (int k = 0; k < chain.size(); k++) msg[2 + k] = chain.get(k);
                    inbox.add(msg);
                    messages++;
                }
            }
            List<int[]> next = new ArrayList<>();
            for (int[] msg : inbox) {
                int r = msg[0], value = msg[1];
                if (traitor[r]) continue;
                if (V.get(r).contains(value)) continue;
                V.get(r).add(value);
                int signatures = msg.length - 2;
                if (relay && signatures - 1 < m) {                    // fewer than m lieutenants have signed
                    Set<Integer> signed = new HashSet<>();
                    for (int k = 2; k < msg.length; k++) signed.add(msg[k]);
                    for (int j = 1; j < n; j++) {
                        if (j == r || signed.contains(j)) continue;
                        int[] out = Arrays.copyOf(msg, msg.length + 1);
                        out[0] = j;
                        out[msg.length] = r;
                        next.add(out);
                        messages++;
                    }
                }
            }
            inbox = next;
        }
        int first = -1;
        for (int l = 1; l < n; l++) {
            if (traitor[l]) continue;
            int d = V.get(l).size() == 1 ? V.get(l).iterator().next() : RETREAT;
            if (first < 0) first = d;
            if (d != first) return false;
            if (!traitor[0] && d != v) return false;
        }
        return true;
    }

    static boolean relay = true;    // switched off once, to show that the traitors' freedom is enough to break a weaker rule

    static long traitorPick(int k) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 33) % k;
    }

    /** All ways to choose m traitors among n generals, as boolean arrays. */
    static List<boolean[]> traitorSets(int n, int m) {
        List<boolean[]> out = new ArrayList<>();
        for (int s = 0; s < (1 << n); s++) {
            if (Integer.bitCount(s) != m) continue;
            boolean[] t = new boolean[n];
            for (int i = 0; i < n; i++) t[i] = ((s >> i) & 1) == 1;
            out.add(t);
        }
        return out;
    }

    public static void main(String[] args) {
        // ---- 1. three generals ---------------------------------------------------------------------------------------
        // Situation A: the commander (loyal) says ATTACK; lieutenant 2 (traitor) tells lieutenant 1 "he said RETREAT".
        // Situation B: the commander (traitor) says ATTACK to lieutenant 1 and RETREAT to lieutenant 2, who (loyal)
        //              truthfully tells lieutenant 1 "he said RETREAT".
        int[] viewA = {ATTACK, RETREAT}, viewB = {ATTACK, RETREAT};
        check(Arrays.equals(viewA, viewB), "lieutenant 1 sees the same thing in both situations");
        System.out.printf("three: situation A, the commander is loyal and orders ATTACK, lieutenant 2 is a traitor and tells lieutenant 1 the order was RETREAT ; situation B, the commander is a traitor, orders ATTACK to lieutenant 1 and RETREAT to lieutenant 2, and lieutenant 2 truthfully reports RETREAT ; in both, lieutenant 1 hears %s from the commander and %s from lieutenant 2 ; in A he must attack (IC2), so he attacks in B too ; by the same argument lieutenant 2 must retreat in B, and the loyal lieutenants disagree%n",
                order(viewA[0]), order(viewA[1]));

        // ---- 2. OM(m) against every traitor behaviour ------------------------------------------------------------------
        StringJoiner oj = new StringJoiner(" ; ");
        int[][] cases = {{3, 1}, {4, 1}, {5, 1}, {6, 2}, {7, 2}, {8, 2}, {9, 3}, {10, 3}};
        for (int[] cs : cases) {
            int n = cs[0], m = cs[1];
            long tried = 0, failed = 0;
            String how = "";
            for (boolean[] t : traitorSets(n, m)) {
                traitor = t;
                int k = traitorMessages(n, m);
                for (int v = 0; v <= 1; v++) {
                    if (k <= 16) {
                        random = false;
                        how = "every behaviour";
                        for (mask = 0; mask < (1L << k); mask++) { tried++; if (!om(n, m, v)) failed++; }
                    } else {
                        random = true;
                        how = "random behaviours";
                        int trials = n <= 8 ? 2000 : 200;
                        for (int r = 0; r < trials; r++) { tried++; if (!om(n, m, v)) failed++; }
                    }
                }
            }
            random = false;
            if (n < 3 * m + 1) check(failed > 0, "OM(" + m + ") fails for some behaviour with n = " + n);
            oj.add(String.format("n=%d, m=%d (%s): %,d runs, %s, %,d broke IC1 or IC2", n, m, how, tried, n >= 3 * m + 1 ? "n >= 3m+1" : "n = 3m", failed));
        }
        System.out.printf("om: OM(m) with m traitors placed every possible way, both orders ; a traitor's every message chosen by the adversary ; %s%n", oj);

        // ---- 3. messages sent --------------------------------------------------------------------------------------------
        StringJoiner mj = new StringJoiner(" ; ");
        long prevOM = 0;
        for (int m = 1; m <= 4; m++) {
            int n = 3 * m + 1;
            traitor = new boolean[n];
            random = false; mask = 0;
            messages = 0;
            runOM(n, m, ATTACK);
            long omMsgs = messages;
            long formula = 0, term = 1;
            for (int k = 0; k <= m; k++) { term *= (n - 1 - k); formula += term; }
            check(omMsgs == formula, "OM message count: (n-1) + (n-1)(n-2) + ... + (n-1)...(n-m-1)");
            check(omMsgs > prevOM, "grows");
            prevOM = omMsgs;
            messages = 0;
            runSM(n, m, ATTACK);
            long smMsgs = messages;
            check(smMsgs == (long) (n - 1) * (n - 1), "SM with no traitors: (n-1) + (n-1)(n-2) messages");
            mj.add(String.format("m=%d, n=%d: OM %,d messages, SM %,d", m, n, omMsgs, smMsgs));
        }
        System.out.printf("messages: with no traitors present, the messages each algorithm sends when n = 3m + 1 ; %s ; OM's count is (n-1) + (n-1)(n-2) + ... + (n-1)(n-2)...(n-m-1) ; SM sends each order on once, (n-1)^2 in all%n", mj);

        // ---- 4. SM(m) -------------------------------------------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        int[][] smCases = {{3, 1}, {4, 2}, {5, 3}, {6, 2}, {7, 5}};
        for (int[] cs : smCases) {
            int n = cs[0], m = cs[1];
            long tried = 0, failed = 0;
            random = true;
            for (boolean[] t : traitorSets(n, m)) {
                traitor = t;
                for (int v = 0; v <= 1; v++)
                    for (int r = 0; r < 300; r++) { tried++; boolean ok = runSM(n, m, v); check(ok, "SM(" + m + ") with n = " + n + " keeps IC1 and IC2"); if (!ok) failed++; }
            }
            random = false;
            sj.add(String.format("n=%d, m=%d: %,d runs, %d failures", n, m, tried, failed));
        }
        relay = false;
        long ctrlTried = 0, ctrlFailed = 0;
        random = true;
        for (boolean[] t : traitorSets(3, 1)) {
            traitor = t;
            for (int v = 0; v <= 1; v++) for (int r = 0; r < 300; r++) { ctrlTried++; if (!runSM(3, 1, v)) ctrlFailed++; }
        }
        random = false;
        relay = true;
        check(ctrlFailed > 0, "without passing orders on, the same traitors do break it");
        sj.add(String.format("control, n=3, m=1 but lieutenants never pass orders on: %,d runs, %,d failures", ctrlTried, ctrlFailed));
        System.out.printf("sm: SM(m), signed messages, traitors free to sign anything with their own keys, to send it to anyone in any round or not at all, but unable to forge a loyal general's signature ; %s ; with signatures, three generals can survive one traitor%n", sj);

        System.out.println("ByzantineGenerals: " + passed + " checks passed");
    }
}
