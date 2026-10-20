import java.util.*;

/**
 * Era 8, topic 8: Paxos (Leslie Lamport, "The Part-Time Parliament", written around 1989-1990, published 1998;
 * "Paxos Made Simple", 2001). Single-decree Paxos: several computers must agree on one value.
 *
 * HOW IT WORKS
 *   Proposers suggest values; acceptors vote. A value is chosen once a majority of acceptors have accepted it in the
 *   same numbered ballot. Messages may be delayed, repeated or lost, and computers may stop; nothing is assumed about
 *   timing. Each ballot has two phases:
 *     1. The proposer of ballot n sends prepare(n). An acceptor that has not yet promised anything higher promises to
 *        ignore every ballot below n, and reports the last vote it cast, if any.
 *     2. With promises from a majority, the proposer sends accept(n, v), where v must be the value of the highest-
 *        numbered vote reported to it; only if no one reported a vote may it use its own value. An acceptor votes for
 *        (n, v) unless it has promised a higher ballot.
 *   Why it is safe: if v was chosen in ballot m, a majority voted for it; any later ballot's majority of promises
 *   overlaps that majority in at least one acceptor, which reports a vote of ballot m or later, so the later ballot
 *   proposes v again. Why it may not finish: two proposers can keep pre-empting each other with higher ballots.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Exhaustive check: 2 proposers (P1 with ballots 1 and 3 and value A, P2 with ballot 2 and value B), 3 acceptors; every message
 *      stays in the network forever and can be delivered at any moment, any number of times (so delay, repetition and
 *      loss are all covered). Every reachable state is visited; in none of them are two different values chosen.
 *   2. The same search with the rule broken (the proposer always uses its own value): the shortest run that chooses
 *      both A and B, printed step by step. And with quorums of 1 acceptor instead of a majority.
 *   3. Random runs with 5 acceptors and 3 proposers, messages lost and acceptors crashing: agreement every time.
 *   4. Duelling proposers: a schedule in which nothing is ever chosen, and the same proposers with one leader.
 *   5. The scripted run of the book's widget, with the rule kept and broken.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Paxos.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Paxos {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int ACC = 3, BALLOTS = 3; // ballots 1..3; proposer 0 owns 1 and 3, proposer 1 owns 2
    static final int[] MAX_TRIES = {2, 1};
    static final String VAL = "AB";

    /** A whole system state: acceptors, proposers and the set of messages ever sent. */
    static final class S {
        int[] promised = new int[ACC], voteB = new int[ACC], voteV = new int[ACC];
        int[] votes = new int[ACC];            // bit b: this acceptor voted in ballot b
        int[] pIdx = new int[2], pMask = new int[2], pHighB = new int[2], pHighV = new int[2];
        boolean[] pSent = new boolean[2];
        int prepares;                          // bit b: prepare(b) sent
        int promises;                          // bit (b * ACC + a): promise(b) from a sent
        int[][] promB = new int[BALLOTS + 1][ACC], promV = new int[BALLOTS + 1][ACC];
        int accepts;                           // bit b: accept(b, v) sent
        int[] acceptV = new int[BALLOTS + 1];

        S copy() {
            S c = new S();
            c.promised = promised.clone(); c.voteB = voteB.clone(); c.voteV = voteV.clone(); c.votes = votes.clone();
            c.pIdx = pIdx.clone(); c.pMask = pMask.clone(); c.pHighB = pHighB.clone(); c.pHighV = pHighV.clone(); c.pSent = pSent.clone();
            c.prepares = prepares; c.promises = promises; c.accepts = accepts; c.acceptV = acceptV.clone();
            for (int b = 0; b <= BALLOTS; b++) { c.promB[b] = promB[b].clone(); c.promV[b] = promV[b].clone(); }
            return c;
        }

        String key() {
            StringBuilder s = new StringBuilder();
            for (int a = 0; a < ACC; a++) s.append(promised[a]).append(voteB[a]).append(voteV[a]).append((char) ('a' + votes[a]));
            for (int p = 0; p < 2; p++) s.append(pIdx[p]).append(pMask[p]).append(pHighB[p]).append(pHighV[p]).append(pSent[p] ? 1 : 0);
            s.append('|').append(prepares).append('|').append(promises).append('|').append(accepts).append('|');
            for (int b = 1; b <= BALLOTS; b++) { s.append(acceptV[b]); for (int a = 0; a < ACC; a++) s.append(promB[b][a]).append(promV[b][a]); }
            return s.toString();
        }

        /** The values chosen: v is chosen if some ballot b has votes from a quorum, all for accept(b)'s value. */
        Set<Character> chosen(int quorum) {
            Set<Character> c = new TreeSet<>();
            for (int b = 1; b <= BALLOTS; b++) {
                int n = 0;
                for (int a = 0; a < ACC; a++) if ((votes[a] >> b & 1) == 1) n++;
                if (n >= quorum) c.add(VAL.charAt(acceptV[b]));
            }
            return c;
        }
    }

    static int ballotOf(int p, int idx) { return p + 1 + 2 * (idx - 1); }

    /** All states reachable in one step, with a description of the step. */
    static List<Object[]> successors(S s, boolean keepRule, int quorum) {
        List<Object[]> out = new ArrayList<>();
        for (int p = 0; p < 2; p++) if (s.pIdx[p] < MAX_TRIES[p]) { // start the next ballot
            S t = s.copy();
            t.pIdx[p]++; t.pMask[p] = 0; t.pHighB[p] = 0; t.pHighV[p] = 0; t.pSent[p] = false;
            int b = ballotOf(p, t.pIdx[p]);
            t.prepares |= 1 << b;
            out.add(new Object[]{t, "P" + (p + 1) + " sends prepare(" + b + ")"});
        }
        for (int b = 1; b <= BALLOTS; b++) if ((s.prepares >> b & 1) == 1) for (int a = 0; a < ACC; a++) if (b > s.promised[a]) {
            S t = s.copy();
            t.promised[a] = b;
            t.promises |= 1 << (b * ACC + a);
            t.promB[b][a] = s.voteB[a]; t.promV[b][a] = s.voteV[a];
            out.add(new Object[]{t, "acceptor " + (a + 1) + " promises ballot " + b + (s.voteB[a] > 0 ? ", reporting its vote (" + s.voteB[a] + ", " + VAL.charAt(s.voteV[a]) + ")" : ", no vote yet")});
        }
        for (int b = 1; b <= BALLOTS; b++) for (int a = 0; a < ACC; a++) if ((s.promises >> (b * ACC + a) & 1) == 1) {
            int p = (b - 1) % 2;
            if (s.pIdx[p] == 0 || ballotOf(p, s.pIdx[p]) != b || (s.pMask[p] >> a & 1) == 1 || s.pSent[p]) continue;
            S t = s.copy();
            t.pMask[p] |= 1 << a;
            if (s.promB[b][a] > t.pHighB[p]) { t.pHighB[p] = s.promB[b][a]; t.pHighV[p] = s.promV[b][a]; }
            String d = "P" + (p + 1) + " receives acceptor " + (a + 1) + "'s promise for ballot " + b;
            if (Integer.bitCount(t.pMask[p]) >= quorum) {
                int v = keepRule && t.pHighB[p] > 0 ? t.pHighV[p] : p; // proposer p's own value is VAL[p]
                t.pSent[p] = true; t.accepts |= 1 << b; t.acceptV[b] = v;
                d += " and sends accept(" + b + ", " + VAL.charAt(v) + ")";
            }
            out.add(new Object[]{t, d});
        }
        for (int b = 1; b <= BALLOTS; b++) if ((s.accepts >> b & 1) == 1) for (int a = 0; a < ACC; a++)
            if (b >= s.promised[a] && (s.votes[a] >> b & 1) == 0) {
                S t = s.copy();
                t.promised[a] = b; t.voteB[a] = b; t.voteV[a] = s.acceptV[b]; t.votes[a] |= 1 << b;
                out.add(new Object[]{t, "acceptor " + (a + 1) + " votes (" + b + ", " + VAL.charAt(s.acceptV[b]) + ")"});
            }
        return out;
    }

    /** Breadth-first search over every reachable state. Returns {states, edges, shortest violating trace or null}. */
    static Object[] explore(boolean keepRule, int quorum) {
        S init = new S();
        Map<String, String[]> parent = new HashMap<>(); // key -> {parent key, step}
        ArrayDeque<S> queue = new ArrayDeque<>();
        parent.put(init.key(), null);
        queue.add(init);
        long edges = 0;
        int chosenStates = 0;
        while (!queue.isEmpty()) {
            S s = queue.poll();
            String k = s.key();
            Set<Character> ch = s.chosen(quorum);
            if (!ch.isEmpty()) chosenStates++;
            if (ch.size() > 1) { // rebuild the shortest path to this state
                List<String> trace = new ArrayList<>();
                for (String cur = k; parent.get(cur) != null; cur = parent.get(cur)[0]) trace.add(parent.get(cur)[1]);
                Collections.reverse(trace);
                return new Object[]{parent.size(), edges, trace, chosenStates};
            }
            for (Object[] nx : successors(s, keepRule, quorum)) {
                edges++;
                S t = (S) nx[0];
                String tk = t.key();
                if (!parent.containsKey(tk)) { parent.put(tk, new String[]{k, (String) nx[1]}); queue.add(t); }
            }
        }
        return new Object[]{parent.size(), edges, null, chosenStates};
    }

    // ---- random runs with lost messages and crashes ----------------------------------------------------------------
    static int s32 = 1998;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    /** One random run: n acceptors, m proposers each trying up to 4 ballots; returns the set of chosen values. */
    static Set<Integer> randomRun(int n, int m, double loss, int crashes, int[] decidedSteps) {
        int[] promised = new int[n], vb = new int[n], vv = new int[n];
        boolean[] crashed = new boolean[n];
        int[] votesFor = new int[1000];
        Map<Integer, Integer> ballotValue = new HashMap<>();
        Map<Integer, Set<Integer>> votedIn = new HashMap<>();
        List<int[]> net = new ArrayList<>(); // {kind, ballot, from, to, voteB, voteV}: 0 prepare, 1 promise, 2 accept
        int[] tries = new int[m], ballot = new int[m], mask = new int[m], hb = new int[m], hv = new int[m];
        boolean[] sent = new boolean[m];
        Set<Integer> chosen = new TreeSet<>();
        for (int step = 0; step < 4000; step++) {
            double r = next32();
            if (r < 0.03) { // a proposer starts a new ballot
                int p = (int) (next32() * m);
                if (tries[p] < 4) {
                    tries[p]++; ballot[p] = p + 1 + m * (tries[p] - 1); mask[p] = 0; hb[p] = 0; hv[p] = 0; sent[p] = false;
                    for (int a = 0; a < n; a++) net.add(new int[]{0, ballot[p], p, a, 0, 0});
                }
            } else if (r < 0.035 && crashes > 0) {
                int a = (int) (next32() * n);
                if (!crashed[a]) { crashed[a] = true; crashes--; }
            } else if (!net.isEmpty()) {
                int i = (int) (next32() * net.size());
                int[] msg = net.get(i);
                boolean keep = next32() < 0.2; // the network may deliver it again later
                if (!keep) net.remove(i);
                if (next32() < loss) continue; // lost
                if (msg[0] == 0) {
                    int a = msg[3];
                    if (!crashed[a] && msg[1] > promised[a]) { promised[a] = msg[1]; net.add(new int[]{1, msg[1], a, msg[2], vb[a], vv[a]}); }
                } else if (msg[0] == 1) {
                    int p = msg[3];
                    if (ballot[p] == msg[1] && !sent[p] && (mask[p] >> msg[2] & 1) == 0) {
                        mask[p] |= 1 << msg[2];
                        if (msg[4] > hb[p]) { hb[p] = msg[4]; hv[p] = msg[5]; }
                        if (Integer.bitCount(mask[p]) > n / 2) {
                            sent[p] = true;
                            int v = hb[p] > 0 ? hv[p] : p + 1;
                            ballotValue.put(ballot[p], v);
                            for (int a = 0; a < n; a++) net.add(new int[]{2, ballot[p], p, a, 0, v});
                        }
                    }
                } else {
                    int a = msg[3];
                    if (!crashed[a] && msg[1] >= promised[a]) {
                        promised[a] = msg[1]; vb[a] = msg[1]; vv[a] = msg[5];
                        Set<Integer> who = votedIn.computeIfAbsent(msg[1], x -> new HashSet<>());
                        who.add(a);
                        if (who.size() > n / 2 && chosen.add(msg[5]) && chosen.size() == 1) decidedSteps[0] = step;
                    }
                }
            }
        }
        return chosen;
    }

    public static void main(String[] args) {
        // ---- 1. exhaustive check -----------------------------------------------------------------------------------
        Object[] ok = explore(true, 2);
        check(ok[2] == null, "no reachable state has two values chosen");
        System.out.printf("exhaustive: 2 proposers (P1: ballots 1 and 3, value A; P2: ballot 2, value B), 3 acceptors, majority = 2 ; every message stays in the network and may be delivered at any time, again and again ; %,d reachable states, %,d steps between them ; a value is chosen in %,d of the states ; two different values chosen: in none%n", (Integer) ok[0], (Long) ok[1], (Integer) ok[3]);

        // ---- 2. broken rules -----------------------------------------------------------------------------------------
        Object[] bad = explore(false, 2);
        check(bad[2] != null, "breaking the rule allows two values to be chosen");
        @SuppressWarnings("unchecked") List<String> trace = (List<String>) bad[2];
        Object[] small = explore(true, 1);
        check(small[2] != null, "quorums that need not overlap allow two values to be chosen");
        @SuppressWarnings("unchecked") List<String> trace1 = (List<String>) small[2];
        System.out.printf("broken: the proposer always uses its own value: two values chosen after %d steps (found among %,d states) ; %s%n", trace.size(), (Integer) bad[0], String.join(" ; ", trace));
        System.out.printf("quorum: the rule kept, but a quorum of 1 acceptor instead of a majority: two values chosen after %d steps ; %s%n", trace1.size(), String.join(" ; ", trace1));

        // ---- 3. random runs ---------------------------------------------------------------------------------------
        int runs = 20_000, decided = 0, crashRuns = 0;
        long stepsSum = 0;
        for (int r = 0; r < runs; r++) {
            int[] ds = new int[1];
            int crashes = r % 2 == 0 ? 2 : 0;
            Set<Integer> ch = randomRun(5, 3, 0.1, crashes, ds);
            check(ch.size() <= 1, "agreement in every random run");
            if (ch.size() == 1) { decided++; stepsSum += ds[0]; }
            if (crashes > 0) crashRuns++;
        }
        System.out.printf("random: %,d runs, 5 acceptors, 3 proposers with up to 4 ballots each, 10%% of messages lost, messages delivered in random order and sometimes twice, 2 acceptors crashing in %,d of the runs ; two values chosen: never ; a value chosen in %,d runs (%.1f%%), after %.0f steps on average%n", runs, crashRuns, decided, 100.0 * decided / runs, (double) stepsSum / Math.max(1, decided));

        // ---- 4. duelling proposers --------------------------------------------------------------------------------
        int[] promised = new int[3];
        int[][] vote = new int[3][2];
        int rounds = 0, chosenAt = -1;
        int b1 = 0, b2 = 0;
        for (int k = 0; k < 20; k++) { // P1 prepares, P2 prepares higher, P1's accept is refused, and so on
            b1 = 2 * k + 1;
            for (int a = 0; a < 3; a++) if (b1 > promised[a]) promised[a] = b1;
            b2 = 2 * k + 2;
            for (int a = 0; a < 3; a++) if (b2 > promised[a]) promised[a] = b2;
            int acceptedP1 = 0;
            for (int a = 0; a < 3; a++) if (b1 >= promised[a]) acceptedP1++;
            check(acceptedP1 == 0, "P1's accept arrives after P2's prepare and is refused");
            rounds++;
        }
        // with a leader: only P1 proposes
        int[] promL = new int[3];
        int votesL = 0;
        int bl = 41;
        for (int a = 0; a < 3; a++) if (bl > promL[a]) promL[a] = bl;
        for (int a = 0; a < 3; a++) if (bl >= promL[a]) votesL++;
        check(votesL >= 2, "with one leader the first ballot succeeds");
        System.out.printf("duel: P1 and P2 alternate: each prepare arrives before the other's accept ; after %d ballots each, nothing is chosen, and the schedule can go on forever ; with P1 alone as leader: chosen in its first ballot, %d of 3 acceptors voting%n", rounds, votesL);

        // ---- 5. the widget's run ------------------------------------------------------------------------------------
        for (boolean keepRule : new boolean[]{true, false}) {
            S s = new S();
            String[] script = {
                    "P1 sends prepare(1)", "acceptor 1 promises ballot 1", "acceptor 2 promises ballot 1",
                    "P1 receives acceptor 1's promise for ballot 1", "P1 receives acceptor 2's promise for ballot 1",
                    "acceptor 1 votes (1, A)",
                    "P2 sends prepare(2)", "acceptor 1 promises ballot 2", "acceptor 3 promises ballot 2",
                    "P2 receives acceptor 1's promise for ballot 2", "P2 receives acceptor 3's promise for ballot 2",
                    "acceptor 3 votes (2,", "acceptor 2 votes (1, A)", "acceptor 1 votes (2,"};
            List<String> done = new ArrayList<>();
            for (String want : script) {
                Object[] pick = null;
                for (Object[] nx : successors(s, keepRule, 2)) if (((String) nx[1]).startsWith(want)) { pick = nx; break; }
                check(pick != null, "the widget's script is a valid run");
                s = (S) pick[0];
                done.add((String) pick[1]);
            }
            Set<Character> ch = s.chosen(2);
            if (keepRule) check(ch.size() == 1, "kept rule: one value");
            else check(ch.size() == 2, "broken rule: two values");
            System.out.printf("widget: %s ; %s ; chosen: %s%n", keepRule ? "rule kept" : "rule broken", String.join(" ; ", done), ch);
        }

        System.out.println("Paxos: " + passed + " checks passed");
    }
}
