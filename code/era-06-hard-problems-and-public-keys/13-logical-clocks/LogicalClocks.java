import java.util.*;

/**
 * Era 6, topic 13: time, clocks and the ordering of events (Lamport, 1978).
 *
 * HOW IT WORKS
 *   Computers that cooperate over a network have no common clock, and messages take time to arrive. Lamport asked
 *   what "before" can mean there. Event a "happened before" event b (a -> b) if they are in the same process and a
 *   came first, or a is the sending of a message and b its receipt, or there is a chain of such steps from a to b.
 *   If neither happened before the other, the two are "concurrent": no process could ever tell which came first.
 *   A logical clock is a counter in each process:
 *       IR1  add 1 between any two events of the process;
 *       IR2  stamp each message with the sender's counter; on receipt, set the counter above both its own value
 *            and the stamp.
 *   Then a -> b always implies C(a) < C(b) (the Clock Condition). Breaking ties by process number gives one total
 *   order of all events that every process can compute for itself, consistent with "happened before". Lamport used
 *   it to share a resource with no central scheduler: requests are served in timestamp order.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Three processes exchanging messages: every event's clock, which pairs are ordered and which concurrent.
 *   2. 500 random runs: the Clock Condition never fails; how often C(a) < C(b) without a -> b.
 *   3. The total order: always consistent with "happened before".
 *   4. Lamport's mutual exclusion: 5 processes, random message delays, 1,000 entries to the shared resource.
 *   5. The anomaly Lamport pointed out: an order the system cannot see (a telephone call) contradicted by the clocks.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java LogicalClocks.java
 *   Expected output: expected-output.txt in this folder.
 */
public class LogicalClocks {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1978L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int rnd(int n) { return (int) (uniform() * n); }

    /** An event: process, position in its process, clock value; `from` is the send event if this is a receipt. */
    static class Event {
        final int proc, index, id;
        int clock, from = -1;
        String label;
        Event(int proc, int index, int id) { this.proc = proc; this.index = index; this.id = id; }
    }

    /** A run: events per process, built step by step with the two clock rules. */
    static class Run {
        final List<Event> all = new ArrayList<>();
        final List<List<Event>> byProc = new ArrayList<>();
        final int[] clock;

        Run(int procs) { clock = new int[procs]; for (int i = 0; i < procs; i++) byProc.add(new ArrayList<>()); }

        Event local(int p) {
            Event e = new Event(p, byProc.get(p).size(), all.size());
            clock[p]++;                                            // IR1
            e.clock = clock[p];
            byProc.get(p).add(e); all.add(e);
            return e;
        }

        Event receive(int p, Event send) {
            Event e = new Event(p, byProc.get(p).size(), all.size());
            clock[p] = Math.max(clock[p], send.clock) + 1;        // IR2 (and IR1)
            e.clock = clock[p];
            e.from = send.id;
            byProc.get(p).add(e); all.add(e);
            return e;
        }

        /** happened-before for every pair, by following process order and messages (transitive closure). */
        boolean[][] happenedBefore() {
            int n = all.size();
            boolean[][] hb = new boolean[n][n];
            // events were created in an order consistent with ->, so one pass in creation order suffices
            for (Event e : all) {
                List<Event> mine = byProc.get(e.proc);
                if (e.index > 0) { Event prev = mine.get(e.index - 1); hb[prev.id][e.id] = true; for (int x = 0; x < n; x++) if (hb[x][prev.id]) hb[x][e.id] = true; }
                if (e.from >= 0) { hb[e.from][e.id] = true; for (int x = 0; x < n; x++) if (hb[x][e.from]) hb[x][e.id] = true; }
            }
            return hb;
        }
    }

    public static void main(String[] args) {
        // ---- 1. three processes -------------------------------------------------------------------------------------
        Run r = new Run(3);
        Event p1 = r.local(0); p1.label = "p1";
        Event q1 = r.local(1); q1.label = "q1";
        Event p2 = r.local(0); p2.label = "p2 sends to Q";
        Event q2 = r.receive(1, p2); q2.label = "q2 receives";
        Event q3 = r.local(1); q3.label = "q3 sends to R";
        Event r1 = r.local(2); r1.label = "r1";
        Event r2 = r.receive(2, q3); r2.label = "r2 receives";
        Event p3 = r.local(0); p3.label = "p3";
        Event r3 = r.local(2); r3.label = "r3 sends to P";
        Event p4 = r.receive(0, r3); p4.label = "p4 receives";
        boolean[][] hb = r.happenedBefore();
        int ordered = 0, concurrent = 0, clockOnly = 0, n = r.all.size();
        for (int a = 0; a < n; a++)
            for (int b = a + 1; b < n; b++) {
                Event x = r.all.get(a), y = r.all.get(b);
                if (hb[a][b] || hb[b][a]) ordered++; else concurrent++;
                if (hb[a][b]) check(x.clock < y.clock, "clock condition");
                if (hb[b][a]) check(y.clock < x.clock, "clock condition");
                if (!hb[a][b] && !hb[b][a] && x.clock != y.clock) clockOnly++;
            }
        StringJoiner ej = new StringJoiner(", ");
        for (Event e : r.all) ej.add(e.label + " " + e.clock);
        check(hb[p1.id][r2.id] && !hb[q1.id][p2.id] && !hb[p3.id][r3.id] && !hb[r3.id][p3.id], "the example's relations");
        System.out.printf("three: processes P, Q, R ; events with their clocks: %s ; of the %d pairs of events, %d are ordered by happened-before and %d are concurrent ; p1 -> r2 through p2 -> q2 -> q3 -> r2, so C(p1) = %d < C(r2) = %d ; p3 (clock %d) and r3 (clock %d) are concurrent, though their clocks differ%n",
                ej, n * (n - 1) / 2, ordered, concurrent, p1.clock, r2.clock, p3.clock, r3.clock);

        // ---- 2 and 3. random runs ---------------------------------------------------------------------------------
        long pairs = 0, hbPairs = 0, concPairs = 0, smallerButConcurrent = 0, totalOrderOk = 0;
        for (int t = 0; t < 500; t++) {
            int procs = 2 + rnd(5), steps = 10 + rnd(40);
            Run run = new Run(procs);
            List<Event> inFlight = new ArrayList<>();
            for (int s = 0; s < steps; s++) {
                int p = rnd(procs);
                double u = uniform();
                if (u < 0.35 && !inFlight.isEmpty()) {
                    // deliver some message addressed to... any process other than its sender
                    Event send = inFlight.remove(rnd(inFlight.size()));
                    int to = rnd(procs - 1);
                    if (to >= send.proc) to++;
                    run.receive(to, send);
                } else {
                    Event e = run.local(p);
                    if (u < 0.7) inFlight.add(e);                  // this event sends a message
                }
            }
            boolean[][] h = run.happenedBefore();
            int m = run.all.size();
            // total order: by clock, ties broken by process number
            List<Event> order = new ArrayList<>(run.all);
            order.sort(Comparator.comparingInt((Event e) -> e.clock).thenComparingInt(e -> e.proc));
            int[] pos = new int[m];
            for (int i = 0; i < m; i++) pos[order.get(i).id] = i;
            boolean consistent = true;
            for (int a = 0; a < m; a++)
                for (int b = 0; b < m; b++) {
                    if (a == b) continue;
                    Event x = run.all.get(a), y = run.all.get(b);
                    if (h[a][b]) { check(x.clock < y.clock, "clock condition, run " + t); if (pos[a] > pos[b]) consistent = false; }
                    if (a < b) {
                        pairs++;
                        if (h[a][b] || h[b][a]) hbPairs++;
                        else { concPairs++; if (x.clock != y.clock) smallerButConcurrent++; }
                    }
                }
            check(consistent, "the total order respects happened-before");
            totalOrderOk++;
        }
        System.out.printf("random: 500 random runs of 2 to 6 processes and 10 to 50 steps ; %,d pairs of events ; %,d ordered by happened-before, and for every one of them the clocks agree (C(a) < C(b)) ; %,d concurrent pairs, of which %,d (%.0f%%) still have different clocks: a smaller clock does not mean happened-before ; the order by clock, ties broken by process number, respects happened-before in all %d runs%n",
                pairs, hbPairs, concPairs, smallerButConcurrent, 100.0 * smallerButConcurrent / concPairs, totalOrderOk);

        // ---- 4. mutual exclusion ------------------------------------------------------------------------------------
        int N = 5, entriesWanted = 1000;
        mutex(N, entriesWanted);

        // ---- 5. the anomaly -----------------------------------------------------------------------------------------
        // A user at process A issues request a; then telephones a colleague at B, who issues request b.
        // A has been quiet, B busy: B's clock is far ahead.
        // A has been busy, B quiet: b gets the smaller clock although a came first in the real world.
        Run an2 = new Run(2);
        for (int i = 0; i < 9; i++) an2.local(0);
        for (int i = 0; i < 2; i++) an2.local(1);
        Event a2 = an2.local(0), b2 = an2.local(1);
        boolean[][] h6 = an2.happenedBefore();
        check(!h6[a2.id][b2.id] && !h6[b2.id][a2.id], "a and b are concurrent to the system");
        check(b2.clock < a2.clock, "the system orders b before a");
        System.out.printf("anomaly: A issues request a, then a user telephones a colleague at B, who issues request b ; the call is outside the system, so to it a and b are concurrent ; if A's clock had reached %d and B's only %d, the system orders b (clock %d) before a (clock %d), the reverse of what happened ; Lamport's remedies: carry the timestamp through the call, or physical clocks kept close enough%n",
                a2.clock - 1, b2.clock - 1, b2.clock, a2.clock);

        System.out.println("LogicalClocks: " + passed + " checks passed");
    }

    // ---- Lamport's distributed mutual exclusion ---------------------------------------------------------------------
    record Msg(double at, long order, int from, int to, String kind, int ts) {}

    static void mutex(int N, int entriesWanted) {
        PriorityQueue<Msg> net = new PriorityQueue<>(Comparator.comparingDouble(Msg::at).thenComparingLong(Msg::order));
        long[] counter = {0};
        int[] clock = new int[N];
        double[][] lastOnChannel = new double[N][N];
        // each process: its queue of requests (timestamp, process), and the latest timestamp heard from each other
        List<TreeSet<long[]>> queues = new ArrayList<>();
        int[][] heard = new int[N][N];
        for (int i = 0; i < N; i++) queues.add(new TreeSet<>((x, y) -> x[0] != y[0] ? Long.compare(x[0], y[0]) : Long.compare(x[1], y[1])));
        int[] myRequest = new int[N];
        Arrays.fill(myRequest, -1);
        double[] nextRequestAt = new double[N];
        for (int i = 0; i < N; i++) nextRequestAt[i] = uniform() * 5;
        int inside = -1, entries = 0;
        long messages = 0;
        double releaseAt = Double.MAX_VALUE;
        List<long[]> grantOrder = new ArrayList<>();
        double now = 0;
        int requested = 0;
        while (entries < entriesWanted || inside >= 0) {
            // the next thing to happen: a message arrives, a process asks, or the holder releases
            double tMsg = net.isEmpty() ? Double.MAX_VALUE : net.peek().at();
            int asker = -1;
            double tAsk = Double.MAX_VALUE;
            for (int i = 0; i < N; i++) if (myRequest[i] < 0 && nextRequestAt[i] < tAsk && requested < entriesWanted) { tAsk = nextRequestAt[i]; asker = i; }
            double t = Math.min(tMsg, Math.min(tAsk, releaseAt));
            now = t;
            if (t == releaseAt) {
                int p = inside;
                clock[p]++;
                queues.get(p).removeIf(x -> x[1] == p);
                for (int j = 0; j < N; j++) if (j != p) { messages++; post(net, counter, lastOnChannel, now, p, j, "release", clock[p]); }
                myRequest[p] = -1;
                nextRequestAt[p] = now + uniform() * 10;
                inside = -1;
                releaseAt = Double.MAX_VALUE;
            } else if (t == tAsk) {
                int p = asker;
                clock[p]++;
                myRequest[p] = clock[p];
                requested++;
                queues.get(p).add(new long[]{clock[p], p});
                for (int j = 0; j < N; j++) if (j != p) { messages++; post(net, counter, lastOnChannel, now, p, j, "request", clock[p]); }
            } else {
                Msg m = net.poll();
                int p = m.to();
                clock[p] = Math.max(clock[p], m.ts()) + 1;
                heard[p][m.from()] = Math.max(heard[p][m.from()], m.ts());
                if (m.kind().equals("request")) {
                    queues.get(p).add(new long[]{m.ts(), m.from()});
                    clock[p]++;
                    messages++;
                    post(net, counter, lastOnChannel, now, p, m.from(), "ack", clock[p]);
                } else if (m.kind().equals("release")) {
                    int from = m.from();
                    queues.get(p).removeIf(x -> x[1] == from);
                }
            }
            // anyone whose request heads its own queue, and who has heard a later timestamp from everyone, may enter
            if (inside < 0) {
                for (int p = 0; p < N; p++) {
                    if (myRequest[p] < 0 || queues.get(p).isEmpty()) continue;
                    long[] head = queues.get(p).first();
                    if (head[1] != p) continue;
                    boolean all = true;
                    for (int j = 0; j < N; j++) if (j != p && heard[p][j] <= myRequest[p]) all = false;
                    if (!all) continue;
                    inside = p;
                    entries++;
                    grantOrder.add(new long[]{myRequest[p], p});
                    releaseAt = now + 0.5 + uniform();
                    break;
                }
            } else {
                // safety: nobody else may satisfy the entry rule while the resource is held
                for (int p = 0; p < N; p++) {
                    if (p == inside || myRequest[p] < 0 || queues.get(p).isEmpty()) continue;
                    long[] head = queues.get(p).first();
                    boolean all = true;
                    for (int j = 0; j < N; j++) if (j != p && heard[p][j] <= myRequest[p]) all = false;
                    check(!(head[1] == p && all), "never two inside at once");
                }
            }
        }
        boolean inOrder = true;
        for (int i = 1; i < grantOrder.size(); i++) {
            long[] x = grantOrder.get(i - 1), y = grantOrder.get(i);
            if (x[0] > y[0] || (x[0] == y[0] && x[1] > y[1])) inOrder = false;
        }
        check(inOrder, "requests granted in timestamp order");
        check(entries == entriesWanted, "every request granted");
        check(messages == 3L * (N - 1) * entries, "3 (N - 1) messages per entry");
        System.out.printf("mutex: %d processes share one resource with no central scheduler, messages delayed at random (each channel delivers in order) ; %,d entries ; never two inside at once ; requests granted in the order of their timestamps (ties by process number) ; %,d messages, %.1f per entry (a request, an acknowledgement and a release to each of the %d others: 3 x %d = %d)%n",
                N, entries, messages, (double) messages / entries, N - 1, N - 1, 3 * (N - 1));
    }

    static void post(PriorityQueue<Msg> net, long[] counter, double[][] last, double now, int from, int to, String kind, int ts) {
        double at = Math.max(last[from][to], now + 0.1 + uniform() * 2);   // first in, first out on each channel
        last[from][to] = at;
        net.add(new Msg(at, counter[0]++, from, to, kind, ts));
    }
}
