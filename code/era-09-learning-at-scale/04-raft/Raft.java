import java.util.*;

/**
 * Era 9, topic 4: Raft (Diego Ongaro and John Ousterhout, Stanford University, USENIX ATC 2014).
 *
 * HOW IT WORKS
 *   A cluster of servers keeps one replicated log of commands. Time is divided into numbered terms. In each term at
 *   most one server is leader; the others are followers. A follower that hears nothing from a leader for an
 *   election timeout (chosen at random, here 150 to 300 ms) becomes a candidate: it increases its term, votes for
 *   itself and asks the others for votes. A server votes at most once per term, and only for a candidate whose log
 *   is at least as up to date as its own (a later last term, or the same last term and at least as long). A
 *   candidate with votes from a majority becomes leader.
 *   The leader appends client commands to its log and sends them to the followers (AppendEntries), each message
 *   naming the index and term of the entry just before the new ones; a follower accepts only if its log has that
 *   entry, otherwise the leader backs up and tries an earlier point. An entry is committed once a majority stores
 *   it and it is from the leader's current term; committed entries are applied to each server's state machine in
 *   order. Messages may be lost, delayed or reordered, and servers may crash and restart; the rules keep five
 *   properties true: Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Simulates a 5-server cluster for many runs with lost and delayed messages, crashes, restarts and network
 *      partitions, sending client commands throughout, and checks all five safety properties continuously.
 *   2. Randomized against fixed election timeouts: how long the cluster is without a leader after a leader crashes,
 *      and how many elections end in a split vote.
 *   3. Breaks one rule (votes are granted without checking that the candidate's log is up to date) and lets the
 *      same checker find a committed entry that is lost.
 *   4. A short scripted run for the book's page: who leads in which term, and what each log holds.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Raft.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Raft {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- configuration --------------------------------------------------------------------------------------------
    static int N = 5;
    static boolean RANDOM_TIMEOUTS = true, VOTE_RESTRICTION = true;
    static final int HEARTBEAT = 50, DMIN = 5, DMAX = 25;
    static double LOSS = 0.05;

    record Entry(int term, int cmd) {}

    static final int FOLLOWER = 0, CANDIDATE = 1, LEADER = 2;

    static class Server {
        int id, term = 0, votedFor = -1, role = FOLLOWER, commit = 0, applied = 0;
        List<Entry> log = new ArrayList<>(); // index i+1 is log.get(i)
        long deadline, nextBeat;
        int[] nextIndex = new int[N], matchIndex = new int[N];
        Set<Integer> votes = new HashSet<>();
        boolean up = true;

        int lastTerm() { return log.isEmpty() ? 0 : log.get(log.size() - 1).term; }

        int termAt(int i) { return i == 0 ? 0 : log.get(i - 1).term; }
    }

    // message kinds
    static final int RV = 0, RV_REPLY = 1, AE = 2, AE_REPLY = 3;

    static class Msg {
        int kind, from, to, term, a, b; // RV: a = lastIndex, b = lastTerm ; RV_REPLY: a = granted ; AE: a = prevIndex, b = prevTerm ; AE_REPLY: a = success, b = match
        List<Entry> entries;
        int commit;
        long at, seq;
    }

    static Server[] S;
    static PriorityQueue<Msg> net;
    static Random R;
    static long now, seqNo;
    static boolean[][] cut; // network partition: cut[i][j] = messages from i to j are dropped

    // ---- what the checker watches -----------------------------------------------------------------------------------
    static Map<Integer, Integer> leaderOfTerm;          // Election Safety
    static Map<Integer, Entry> committedAt;             // index -> entry, as committed by some leader
    static Map<Integer, Integer> appliedAt;             // index -> command, as applied by any server
    static List<String> violations;
    static int elections, splitVotes, leadersElected;
    static long commandsCommitted;

    static void violation(String s) { if (violations.size() < 5) violations.add(s); }

    static void send(Msg m) {
        if (R.nextDouble() < LOSS) return;
        m.at = now + DMIN + R.nextInt(DMAX - DMIN + 1);
        m.seq = seqNo++;
        net.add(m);
    }

    static long timeout() { return RANDOM_TIMEOUTS ? 150 + R.nextInt(151) : 150; }

    static void becomeFollower(Server s, int term) {
        if (term > s.term) { s.term = term; s.votedFor = -1; }
        s.role = FOLLOWER;
    }

    static void startElection(Server s) {
        s.role = CANDIDATE;
        s.term++;
        s.votedFor = s.id;
        s.votes = new HashSet<>(Set.of(s.id));
        s.deadline = now + timeout();
        elections++;
        for (int j = 0; j < N; j++) if (j != s.id) {
            Msg m = new Msg(); m.kind = RV; m.from = s.id; m.to = j; m.term = s.term; m.a = s.log.size(); m.b = s.lastTerm();
            send(m);
        }
    }

    static void becomeLeader(Server s) {
        s.role = LEADER;
        leadersElected++;
        Integer prev = leaderOfTerm.putIfAbsent(s.term, s.id);
        if (prev != null && prev != s.id) violation("Election Safety: two leaders in term " + s.term);
        // Leader Completeness: every entry committed in an earlier term must be in the new leader's log
        for (Map.Entry<Integer, Entry> c : committedAt.entrySet()) {
            int i = c.getKey();
            if (c.getValue().term < s.term && (i > s.log.size() || !s.log.get(i - 1).equals(c.getValue())))
                violation("Leader Completeness: leader of term " + s.term + " lacks committed entry " + i);
        }
        for (int j = 0; j < N; j++) { s.nextIndex[j] = s.log.size() + 1; s.matchIndex[j] = 0; }
        s.nextBeat = now;
    }

    static void sendAppend(Server s, int j) {
        Msg m = new Msg(); m.kind = AE; m.from = s.id; m.to = j; m.term = s.term;
        m.a = s.nextIndex[j] - 1; m.b = s.termAt(m.a);
        m.entries = new ArrayList<>(s.log.subList(m.a, s.log.size()));
        m.commit = s.commit;
        send(m);
    }

    static void apply(Server s) {
        while (s.applied < s.commit) {
            s.applied++;
            int cmd = s.log.get(s.applied - 1).cmd;
            Integer before = appliedAt.putIfAbsent(s.applied, cmd);
            if (before != null && before != cmd) violation("State Machine Safety: two commands applied at index " + s.applied);
        }
    }

    static void deliver(Msg m) {
        Server s = S[m.to];
        if (!s.up || cut[m.from][m.to]) return;
        if (m.term > s.term) becomeFollower(s, m.term);
        switch (m.kind) {
            case RV -> {
                boolean upToDate = m.b > s.lastTerm() || (m.b == s.lastTerm() && m.a >= s.log.size());
                boolean grant = m.term == s.term && (s.votedFor == -1 || s.votedFor == m.from) && (upToDate || !VOTE_RESTRICTION);
                if (grant) { s.votedFor = m.from; s.deadline = now + timeout(); }
                Msg r = new Msg(); r.kind = RV_REPLY; r.from = s.id; r.to = m.from; r.term = s.term; r.a = grant ? 1 : 0;
                send(r);
            }
            case RV_REPLY -> {
                if (s.role == CANDIDATE && m.term == s.term && m.a == 1) {
                    s.votes.add(m.from);
                    if (s.votes.size() > N / 2) becomeLeader(s);
                }
            }
            case AE -> {
                Msg r = new Msg(); r.kind = AE_REPLY; r.from = s.id; r.to = m.from; r.term = s.term;
                if (m.term < s.term) { r.a = 0; send(r); return; }
                if (s.role == LEADER) violation("Election Safety: leader " + s.id + " got AppendEntries from another leader of term " + m.term);
                s.role = FOLLOWER;
                s.deadline = now + timeout();
                if (m.a > s.log.size() || s.termAt(m.a) != m.b) { r.a = 0; send(r); return; }
                for (int k = 0; k < m.entries.size(); k++) {
                    int idx = m.a + 1 + k;
                    if (idx <= s.log.size() && s.log.get(idx - 1).term != m.entries.get(k).term) {
                        if (idx <= s.commit) violation("a committed entry was overwritten at index " + idx);
                        while (s.log.size() >= idx) s.log.remove(s.log.size() - 1);
                    }
                    if (idx > s.log.size()) s.log.add(m.entries.get(k));
                }
                int lastNew = m.a + m.entries.size();
                if (m.commit > s.commit) s.commit = Math.min(m.commit, lastNew);
                apply(s);
                r.a = 1; r.b = lastNew;
                send(r);
            }
            case AE_REPLY -> {
                if (s.role != LEADER || m.term != s.term) return;
                if (m.a == 1) {
                    s.matchIndex[m.from] = Math.max(s.matchIndex[m.from], m.b);
                    s.nextIndex[m.from] = s.matchIndex[m.from] + 1;
                    for (int n = s.log.size(); n > s.commit; n--) {
                        if (s.log.get(n - 1).term != s.term) break; // only entries of the current term are committed by counting
                        int count = 1;
                        for (int j = 0; j < N; j++) if (j != s.id && s.matchIndex[j] >= n) count++;
                        if (count > N / 2) {
                            for (int i = s.commit + 1; i <= n; i++) {
                                Entry e = s.log.get(i - 1);
                                Entry before = committedAt.putIfAbsent(i, e);
                                if (before != null && !before.equals(e)) violation("two different entries committed at index " + i);
                                commandsCommitted++;
                            }
                            s.commit = n;
                            apply(s);
                            break;
                        }
                    }
                } else {
                    s.nextIndex[m.from] = Math.max(1, s.nextIndex[m.from] - 1);
                }
            }
        }
    }

    /** Log Matching: if two logs hold an entry with the same index and term, they agree on everything up to it. */
    static void checkLogMatching() {
        for (int i = 0; i < N; i++) for (int j = i + 1; j < N; j++) {
            List<Entry> a = S[i].log, b = S[j].log;
            int n = Math.min(a.size(), b.size());
            int lastSame = -1;
            for (int k = n - 1; k >= 0; k--) if (a.get(k).term == b.get(k).term) { lastSame = k; break; }
            for (int k = 0; k <= lastSame; k++) if (!a.get(k).equals(b.get(k))) { violation("Log Matching between servers " + i + " and " + j); return; }
        }
    }

    /** Leader Append-Only: while a server leads a term, its log only grows; nothing in it is changed or removed. */
    static int[] snapTerm;
    static List<List<Entry>> snap;

    static void checkAppendOnly() {
        for (Server s : S) {
            if (s.up && s.role == LEADER) {
                if (snapTerm[s.id] == s.term) {
                    List<Entry> before = snap.get(s.id);
                    if (s.log.size() < before.size() || !s.log.subList(0, before.size()).equals(before))
                        violation("Leader Append-Only: leader " + s.id + " of term " + s.term + " lost or changed an entry");
                }
                snapTerm[s.id] = s.term;
                snap.set(s.id, new ArrayList<>(s.log));
            } else snapTerm[s.id] = -1;
        }
    }

    static void setup(long seed) {
        R = new Random(seed);
        S = new Server[N];
        for (int i = 0; i < N; i++) { S[i] = new Server(); S[i].id = i; S[i].deadline = timeout(); }
        net = new PriorityQueue<>(Comparator.<Msg>comparingLong(m -> m.at).thenComparingLong(m -> m.seq));
        now = 0; seqNo = 0;
        cut = new boolean[N][N];
        leaderOfTerm = new HashMap<>(); committedAt = new HashMap<>(); appliedAt = new HashMap<>();
        violations = new ArrayList<>();
        snapTerm = new int[N]; Arrays.fill(snapTerm, -1);
        snap = new ArrayList<>(); for (int i = 0; i < N; i++) snap.add(List.of());
        elections = 0; splitVotes = 0; leadersElected = 0; commandsCommitted = 0;
    }

    static int nextCmd = 1;

    /** One millisecond of simulated time. */
    static void tick() {
        while (!net.isEmpty() && net.peek().at <= now) deliver(net.poll());
        for (Server s : S) {
            if (!s.up) continue;
            if (s.role == LEADER) {
                if (now >= s.nextBeat) { for (int j = 0; j < N; j++) if (j != s.id) sendAppend(s, j); s.nextBeat = now + HEARTBEAT; }
            } else if (now >= s.deadline) {
                if (s.role == CANDIDATE) splitVotes++; // its previous election ended without a winner
                startElection(s);
            }
        }
        now++;
    }

    static Server leader() {
        Server best = null;
        for (Server s : S) if (s.up && s.role == LEADER && (best == null || s.term > best.term)) best = s;
        return best;
    }

    static void crash(Server s) { s.up = false; }

    static void restart(Server s) {
        s.up = true; s.role = FOLLOWER; s.commit = 0; s.applied = 0; s.deadline = now + timeout(); // term, vote and log are kept on disk
    }

    /** A chaotic run: commands every 20 ms, crashes, restarts and partitions. */
    static long chaoticRun(long seed, int millis) {
        setup(seed);
        long noLeader = 0;
        int[] downUntil = new int[N];
        int partitionUntil = -1;
        for (int t = 0; t < millis; t++) {
            Server l = leader();
            if (l == null) noLeader++;
            if (t % 20 == 0 && l != null) l.log.add(new Entry(l.term, nextCmd++));
            if (t % 400 == 0 && R.nextDouble() < 0.5) {
                int v = R.nextInt(N);
                int down = 0;
                for (Server s : S) if (!s.up) down++;
                if (S[v].up && down < 2) { crash(S[v]); downUntil[v] = t + 200 + R.nextInt(1200); }
            }
            for (int i = 0; i < N; i++) if (!S[i].up && t >= downUntil[i]) restart(S[i]);
            if (t % 1000 == 500 && R.nextDouble() < 0.3) { // cut the cluster into two groups for a while
                int k = 1 + R.nextInt(2);
                List<Integer> ids = new ArrayList<>(List.of(0, 1, 2, 3, 4));
                Collections.shuffle(ids, R);
                Set<Integer> side = new HashSet<>(ids.subList(0, k));
                for (int i = 0; i < N; i++) for (int j = 0; j < N; j++) cut[i][j] = side.contains(i) != side.contains(j);
                partitionUntil = t + 300 + R.nextInt(700);
            }
            if (t == partitionUntil) cut = new boolean[N][N];
            tick();
            if (t % 50 == 0) checkLogMatching();
            checkAppendOnly();
        }
        return noLeader;
    }

    /** Crash the leader of a calm cluster and measure the time until a new leader is elected. */
    static long[] electionAfterCrash(long seed, boolean random) {
        setup(seed);
        LOSS = 0.0;
        RANDOM_TIMEOUTS = true; // the first leader is elected the usual way; the rule under test applies after the crash
        long t = 0;
        while (leader() == null && t < 100_000) { tick(); t++; }
        RANDOM_TIMEOUTS = random;
        for (int k = 0; k < 500; k++) tick();
        Server old = leader();
        crash(old);
        int splits0 = splitVotes;
        long start = now;
        while ((leader() == null || leader() == old) && now - start < 100_000) tick();
        LOSS = 0.05;
        return new long[]{now - start, splitVotes - splits0};
    }

    public static void main(String[] args) {
        // ---- 1. chaos, with every rule ----------------------------------------------------------------------------------
        int runs = 300, millis = 10_000;
        long totalElections = 0, totalLeaders = 0, totalSplits = 0, totalCommitted = 0, totalNoLeader = 0;
        for (int run = 0; run < runs; run++) {
            long nl = chaoticRun(1000 + run, millis);
            check(violations.isEmpty(), "run " + run + ": " + violations);
            int maxTerm = 0;
            for (Server s : S) maxTerm = Math.max(maxTerm, s.term);
            check(leaderOfTerm.size() <= maxTerm, "at most one leader per term");
            totalElections += elections; totalLeaders += leadersElected; totalSplits += splitVotes; totalCommitted += committedAt.size(); totalNoLeader += nl;
            // state machine safety across servers: every server's applied commands are a prefix of one sequence
            for (Server s : S) for (int i = 1; i <= s.applied; i++) check(appliedAt.get(i) == s.log.get(i - 1).cmd, "applied prefix");
        }
        System.out.printf("chaos: %d runs of %,d simulated ms, 5 servers, %.0f%% of messages lost, delays %d to %d ms, crashes, restarts and partitions, a client command every 20 ms ; %,d elections, %,d leaders elected, %,d ended by a timeout without a winner ; %,d entries committed ; no leader %.1f%% of the time ; safety violations: 0 (Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety checked throughout)%n",
                runs, millis, 100 * LOSS, DMIN, DMAX, totalElections, totalLeaders, totalSplits, totalCommitted, 100.0 * totalNoLeader / ((long) runs * millis));

        // ---- 2. randomized against fixed timeouts --------------------------------------------------------------------
        StringJoiner tj = new StringJoiner(" ; ");
        long[] median = new long[2], stuck = new long[2], splits = new long[2];
        for (int t = 0; t < 2; t++) {
            long[] times = new long[200];
            for (int k = 0; k < 200; k++) {
                long[] r = electionAfterCrash(5000 + k, t == 0);
                times[k] = r[0]; splits[t] += r[1];
                if (r[0] >= 100_000) stuck[t]++;
            }
            Arrays.sort(times);
            median[t] = times[100];
            tj.add(String.format("%s: median %d ms, slowest %s, %d of 200 still without a leader after 100 s, %,d elections ended by a timeout without a winner",
                    t == 0 ? "random 150-300 ms" : "fixed 150 ms", median[t], times[199] >= 100_000 ? "over 100 s" : times[199] + " ms", stuck[t], splits[t]));
        }
        RANDOM_TIMEOUTS = true;
        check(stuck[0] == 0 && stuck[1] > 0 && splits[0] < splits[1], "randomized timeouts always elect a new leader; fixed ones can repeat split votes for ever");
        System.out.printf("timeouts: leader crashed in a calm cluster, time until a new leader, 200 trials each ; %s%n", tj);

        // ---- 3. break one rule ---------------------------------------------------------------------------------------
        VOTE_RESTRICTION = false;
        int bad = 0, first = -1;
        String firstWhat = "";
        for (int run = 0; run < runs; run++) {
            chaoticRun(1000 + run, millis);
            if (!violations.isEmpty()) { bad++; if (first < 0) { first = run; firstWhat = violations.get(0); } }
        }
        VOTE_RESTRICTION = true;
        check(bad > 0, "without the voting rule the checker finds a violation");
        System.out.printf("broken: votes granted without checking that the candidate's log is up to date ; the same %d runs: %d with a safety violation ; first in run %d: %s%n",
                runs, bad, first, firstWhat);

        // ---- 4. a short run for the page ----------------------------------------------------------------------------------
        setup(42);
        LOSS = 0;
        StringJoiner ev = new StringJoiner(" ; ");
        int lastLeader = -1, lastTerm = 0;
        int cmd = 1;
        for (int t = 0; t < 3000; t++) {
            Server l = leader();
            if (l != null && (l.id != lastLeader || l.term != lastTerm)) { ev.add(String.format("%d ms: S%d leads term %d", t, l.id + 1, l.term)); lastLeader = l.id; lastTerm = l.term; }
            if (t % 100 == 50 && l != null && cmd <= 12) l.log.add(new Entry(l.term, cmd++));
            if (t == 1000 && l != null) { crash(l); ev.add(String.format("%d ms: S%d crashes", t, l.id + 1)); }
            if (t == 2000) for (Server s : S) if (!s.up) { restart(s); ev.add(String.format("%d ms: S%d restarts", t, s.id + 1)); }
            tick();
        }
        for (int k = 0; k < 500; k++) tick();
        check(violations.isEmpty(), "the scripted run is safe");
        StringJoiner lj = new StringJoiner(" ; ");
        for (Server s : S) {
            StringJoiner one = new StringJoiner(",");
            for (Entry e : s.log) one.add(e.term + ":" + e.cmd);
            lj.add(String.format("S%d term %d commit %d log %s", s.id + 1, s.term, s.commit, one));
        }
        int c0 = S[0].commit;
        for (Server s : S) check(s.commit == c0 && s.log.size() == c0, "after the run all logs are equal and committed");
        System.out.printf("story: 5 servers, no lost messages ; %s ; after 3,500 ms every log holds the same %d entries (term:command) ; %s%n", ev, c0, lj);

        System.out.println("Raft: " + passed + " checks passed");
    }
}
