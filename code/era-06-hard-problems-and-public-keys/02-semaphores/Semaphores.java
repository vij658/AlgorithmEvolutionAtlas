import java.util.*;

/**
 * Era 6, topic 2: mutual exclusion and semaphores (Dekker; Dijkstra, "Cooperating sequential processes", 1965).
 *
 * HOW IT WORKS
 *   Two programs that run at the same time and share memory can interfere: if both read a counter, add one, and write
 *   it back, one of the additions can be lost. Each must have a "critical section" that the other may not enter at
 *   the same moment. With nothing but shared variables this is surprisingly hard; Dijkstra credited Th. J. Dekker with
 *   the first correct solution for two processes. Dijkstra's own remedy is the semaphore, a shared non-negative
 *   integer with two indivisible operations: P waits until the value is positive and then lowers it by one; V raises
 *   it by one. A semaphore that starts at 1, with P before the critical section and V after it, lets one process in.
 *   Because running programs can interleave in astronomically many ways, the only convincing test is to try every
 *   interleaving. This program does exactly that: it explores every state that the programs can reach.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Two processes add one to a shared counter: every interleaving of their loads and stores, and how many lose an
 *      update; the same with a semaphore around the addition.
 *   2. Three plausible attempts at mutual exclusion with shared flags, and Dekker's algorithm: every reachable state
 *      searched for two processes in their critical sections at once, and for states from which one of them can
 *      never get in again.
 *   3. A semaphore protecting three processes.
 *   4. The "deadly embrace": two processes taking two semaphores in opposite orders, and in the same order.
 *   5. A producer and a consumer sharing a buffer of two places, governed by two semaphores.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Semaphores.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Semaphores {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int BLOCKED = -2, DONE = -1;

    /** One instruction of a process: change the shared and local values, return the next pc, or BLOCKED. */
    interface Instr { int step(int[] sh, int[] loc, int me); }

    record Proc(List<Instr> code, Set<Integer> critical) {}

    record State(int[] sh, int[] pc, int[] loc) {
        String key() { return Arrays.toString(sh) + Arrays.toString(pc) + Arrays.toString(loc); }
    }

    /** Explore every state reachable when any process may take the next step. */
    static final class Search {
        final List<Proc> procs;
        final Map<String, State> seen = new LinkedHashMap<>();
        final Map<String, List<String>> next = new HashMap<>();
        Search(List<Proc> procs, int[] sh) {
            this.procs = procs;
            int n = procs.size();
            State s0 = new State(sh.clone(), new int[n], new int[n]);
            Deque<State> todo = new ArrayDeque<>(List.of(s0));
            seen.put(s0.key(), s0);
            while (!todo.isEmpty()) {
                State s = todo.pop();
                List<String> out = new ArrayList<>();
                for (int p = 0; p < n; p++) {
                    State t = move(s, p);
                    if (t == null) continue;
                    out.add(t.key());
                    if (!seen.containsKey(t.key())) { seen.put(t.key(), t); todo.push(t); }
                }
                next.put(s.key(), out);
            }
        }

        State move(State s, int p) {
            if (s.pc()[p] == DONE) return null;
            int[] sh = s.sh().clone(), pc = s.pc().clone(), loc = s.loc().clone();
            int[] mine = {loc[p]};
            int to = procs.get(p).code().get(pc[p]).step(sh, mine, p);
            if (to == BLOCKED) return null;
            loc[p] = mine[0];
            pc[p] = to;
            return new State(sh, pc, loc);
        }

        boolean inCS(State s, int p) { return s.pc()[p] >= 0 && procs.get(p).critical().contains(s.pc()[p]); }

        long bothInCS() {
            long c = 0;
            for (State s : seen.values()) { int k = 0; for (int p = 0; p < procs.size(); p++) if (inCS(s, p)) k++; if (k > 1) c++; }
            return c;
        }

        /** States where no process can move and not all are finished. */
        long stuck() {
            long c = 0;
            for (State s : seen.values()) {
                boolean allDone = Arrays.stream(s.pc()).allMatch(x -> x == DONE);
                if (!allDone && next.get(s.key()).isEmpty()) c++;
            }
            return c;
        }

        /** States from which process p can never again reach its critical section. */
        long shutOut(int p) {
            Set<String> good = new HashSet<>();
            for (State s : seen.values()) if (inCS(s, p)) good.add(s.key());
            boolean grew = true;
            while (grew) {
                grew = false;
                for (State s : seen.values()) {
                    if (good.contains(s.key())) continue;
                    for (String t : next.get(s.key())) if (good.contains(t)) { good.add(s.key()); grew = true; break; }
                }
            }
            return seen.size() - good.size();
        }
    }

    // shared variable slots
    static final int FLAG0 = 0, FLAG1 = 1, TURN = 2, S = 3, S2 = 4, COUNTER = 5, FULL = 6, EMPTY = 7, BUF = 8;

    static Instr set(int slotBase, boolean perProcess, int value) {
        return (sh, loc, me) -> { sh[perProcess ? slotBase + me : slotBase] = value; return -99; };
    }

    /** Build an instruction list where each instruction falls through to the next unless it returns a pc. */
    static List<Instr> program(Instr... ins) {
        List<Instr> out = new ArrayList<>();
        for (int i = 0; i < ins.length; i++) {
            final int k = i, after = i + 1 == ins.length ? 0 : i + 1;
            out.add((sh, loc, me) -> { int r = ins[k].step(sh, loc, me); return r == -99 ? after : r; });
        }
        return out;
    }

    static final Instr NCS = (sh, loc, me) -> -99, CS = (sh, loc, me) -> -99;

    static Instr P(int s) { return (sh, loc, me) -> { if (sh[s] == 0) return BLOCKED; sh[s]--; return -99; }; }

    static Instr V(int s) { return (sh, loc, me) -> { sh[s]++; return -99; }; }

    static Instr await(java.util.function.BiPredicate<int[], Integer> cond) { return (sh, loc, me) -> cond.test(sh, me) ? -99 : BLOCKED; }

    static Instr jumpIf(java.util.function.BiPredicate<int[], Integer> cond, int to) { return (sh, loc, me) -> cond.test(sh, me) ? to : -99; }

    static int other(int me) { return 1 - me; }

    public static void main(String[] args) {
        // ---- 1. the lost update ------------------------------------------------------------------------------------------
        // each process: load counter into a register, add one, store it back
        long[] ends = new long[3];
        int[] interleavings = {0};
        countRace(new int[]{0, 0}, new int[2], 0, ends, interleavings);
        check(interleavings[0] == 20 && ends[2] + ends[1] == 20 && ends[1] > 0, "some interleavings lose an update");
        // with a semaphore: P, load, add, store, V
        long[] ends2 = new long[3];
        int[] inter2 = {0};
        countRaceSem(new int[]{0, 0}, new int[2], 1, 0, ends2, inter2);
        check(ends2[1] == 0 && ends2[2] > 0, "with a semaphore no update is lost");
        System.out.printf("race: two processes each load the counter, add one, store it back (3 steps each) ; all %d interleavings tried: the counter ends at 2 in %d of them and at 1 in %d, an update lost ; with P(s) before and V(s) after, the %d possible orders all end at 2%n",
                interleavings[0], ends[2], ends[1], inter2[0]);

        // ---- 2. attempts at mutual exclusion ----------------------------------------------------------------------------
        StringJoiner attempts = new StringJoiner(" ; ");
        // attempt A: take turns
        List<Instr> alt = program(NCS, await((sh, me) -> sh[TURN] == me), CS, (sh, loc, me) -> { sh[TURN] = other(me); return -99; });
        Search a = new Search(List.of(new Proc(alt, Set.of(2)), new Proc(alt, Set.of(2))), new int[10]);
        check(a.bothInCS() == 0, "taking turns: exclusion holds");
        attempts.add(String.format("taking turns (turn variable): %d states, both inside in %d, but a process can enter only after the other has had its turn", a.seen.size(), a.bothInCS()));
        // attempt B: look at the other's flag, then raise your own
        List<Instr> lookFirst = program(NCS, await((sh, me) -> sh[FLAG0 + other(me)] == 0), set(FLAG0, true, 1), CS, set(FLAG0, true, 0));
        Search b = new Search(List.of(new Proc(lookFirst, Set.of(3)), new Proc(lookFirst, Set.of(3))), new int[10]);
        check(b.bothInCS() > 0, "look then raise: both can enter");
        attempts.add(String.format("look at the other's flag, then raise yours: %d states, both inside at once in %d of them", b.seen.size(), b.bothInCS()));
        // attempt C: raise your flag, then wait for the other's to fall
        List<Instr> raiseFirst = program(NCS, set(FLAG0, true, 1), await((sh, me) -> sh[FLAG0 + other(me)] == 0), CS, set(FLAG0, true, 0));
        Search c = new Search(List.of(new Proc(raiseFirst, Set.of(3)), new Proc(raiseFirst, Set.of(3))), new int[10]);
        check(c.bothInCS() == 0 && c.stuck() > 0, "raise then wait: safe but can deadlock");
        attempts.add(String.format("raise your flag, then wait for the other's to fall: %d states, never both inside, but %d state%s where both wait for ever", c.seen.size(), c.stuck(), c.stuck() == 1 ? "" : "s"));
        // Dekker
        List<Instr> dekker = program(
                NCS,                                                                          // 0
                set(FLAG0, true, 1),                                                          // 1
                jumpIf((sh, me) -> sh[FLAG0 + other(me)] == 0, 7),                            // 2: other not interested: go in
                jumpIf((sh, me) -> sh[TURN] == me, 2),                                        // 3: my turn: insist, look again
                set(FLAG0, true, 0),                                                          // 4: not my turn: back off
                await((sh, me) -> sh[TURN] == me),                                            // 5: wait for my turn
                (sh, loc, me) -> { sh[FLAG0 + me] = 1; return 2; },                           // 6: raise again, look again
                CS,                                                                           // 7
                (sh, loc, me) -> { sh[TURN] = other(me); return -99; },                       // 8: give the turn away
                set(FLAG0, true, 0));                                                         // 9
        Search dk = new Search(List.of(new Proc(dekker, Set.of(7)), new Proc(dekker, Set.of(7))), new int[10]);
        check(dk.bothInCS() == 0 && dk.stuck() == 0 && dk.shutOut(0) == 0 && dk.shutOut(1) == 0, "Dekker is correct");
        check(c.shutOut(0) > 0, "attempt C shuts processes out");
        attempts.add(String.format("Dekker's algorithm (flags and a turn): %d states, never both inside, no state where both wait, and from every state each process can still reach its critical section", dk.seen.size()));
        System.out.println("attempts: every reachable state of two processes searched ; " + attempts);

        // ---- 3. a semaphore for three --------------------------------------------------------------------------------
        List<Instr> mutex = program(NCS, P(S), CS, V(S));
        int[] sh3 = new int[10];
        sh3[S] = 1;
        Search m = new Search(List.of(new Proc(mutex, Set.of(2)), new Proc(mutex, Set.of(2)), new Proc(mutex, Set.of(2))), sh3);
        check(m.bothInCS() == 0 && m.stuck() == 0, "semaphore: exclusion, no deadlock");
        for (int p = 0; p < 3; p++) check(m.shutOut(p) == 0, "nobody shut out");
        System.out.printf("mutex: three processes, each doing P(s), critical section, V(s), with s = 1 at the start ; %d reachable states: never two inside at once, never stuck, and every process can always still get in ; four instructions instead of Dekker's ten, and for any number of processes%n",
                m.seen.size());

        // ---- 4. the deadly embrace ------------------------------------------------------------------------------------
        List<Instr> ab = program(P(S), P(S2), CS, V(S2), V(S), (sh, loc, me) -> DONE);
        List<Instr> ba = program(P(S2), P(S), CS, V(S), V(S2), (sh, loc, me) -> DONE);
        int[] sh4 = new int[10];
        sh4[S] = 1;
        sh4[S2] = 1;
        Search e1 = new Search(List.of(new Proc(ab, Set.of(2)), new Proc(ba, Set.of(2))), sh4);
        Search e2 = new Search(List.of(new Proc(ab, Set.of(2)), new Proc(ab, Set.of(2))), sh4);
        check(e1.stuck() > 0 && e2.stuck() == 0, "opposite order deadlocks, same order does not");
        System.out.printf("embrace: process 1 takes semaphore A then B, process 2 takes B then A ; %d reachable states, %d of them stuck for ever (each holds one and waits for the other) ; both taking A first: %d states, none stuck%n",
                e1.seen.size(), e1.stuck(), e2.seen.size());

        // ---- 5. producer and consumer ------------------------------------------------------------------------------------
        int items = 5;
        // shared: FULL, EMPTY semaphores; BUF..BUF+1 the two places; slot 10 next to write, 11 next to read, 12 produced, 13 consumed ok flag
        List<Instr> producer = program(
                (sh, loc, me) -> sh[12] == items ? DONE : -99,
                P(EMPTY),
                (sh, loc, me) -> { sh[BUF + sh[10]] = sh[12] + 1; sh[10] = (sh[10] + 1) % 2; sh[12]++; return -99; },
                V(FULL));
        List<Instr> consumer = program(
                (sh, loc, me) -> sh[13] == items ? DONE : -99,
                P(FULL),
                (sh, loc, me) -> { int v = sh[BUF + sh[11]]; if (v != sh[13] + 1) sh[14] = 1; sh[BUF + sh[11]] = 0; sh[11] = (sh[11] + 1) % 2; sh[13]++; return -99; },
                V(EMPTY));
        int[] sh5 = new int[16];
        sh5[EMPTY] = 2;
        Search pc = new Search(List.of(new Proc(producer, Set.of()), new Proc(consumer, Set.of())), sh5);
        long finished = 0, outOfOrder = 0, overfull = 0;
        for (State s : pc.seen.values()) {
            if (s.pc()[0] == DONE && s.pc()[1] == DONE) finished++;
            if (s.sh()[14] != 0) outOfOrder++;
            if (s.sh()[12] - s.sh()[13] > 2 || s.sh()[12] - s.sh()[13] < 0) overfull++;
        }
        check(finished == 1 && outOfOrder == 0 && overfull == 0 && pc.stuck() == 0, "producer-consumer correct");
        System.out.printf("buffer: a producer makes items 1 to %d, a consumer takes them, through 2 places, with semaphores empty = 2 and full = 0 ; %d reachable states: the producer never gets more than 2 ahead, the consumer never takes from an empty place, every item arrives in order, and every run ends with all %d delivered%n",
                items, pc.seen.size(), items);

        System.out.println("Semaphores: " + passed + " checks passed");
    }

    /** Count every interleaving of two load-add-store processes; ends[v] counts final values v. */
    static void countRace(int[] pcs, int[] reg, int counter, long[] ends, int[] total) {
        if (pcs[0] == 3 && pcs[1] == 3) { ends[counter]++; total[0]++; return; }
        for (int p = 0; p < 2; p++) {
            if (pcs[p] == 3) continue;
            int[] pc2 = pcs.clone(), r2 = reg.clone();
            int c2 = counter;
            switch (pc2[p]) { case 0 -> r2[p] = c2; case 1 -> r2[p]++; default -> c2 = r2[p]; }
            pc2[p]++;
            countRace(pc2, r2, c2, ends, total);
        }
    }

    /** The same with P(s) and V(s) around the three steps; P blocks when s is 0. */
    static void countRaceSem(int[] pcs, int[] reg, int s, int counter, long[] ends, int[] total) {
        if (pcs[0] == 5 && pcs[1] == 5) { ends[counter]++; total[0]++; return; }
        for (int p = 0; p < 2; p++) {
            if (pcs[p] == 5) continue;
            if (pcs[p] == 0 && s == 0) continue;
            int[] pc2 = pcs.clone(), r2 = reg.clone();
            int c2 = counter, s2 = s;
            switch (pc2[p]) { case 0 -> s2--; case 1 -> r2[p] = c2; case 2 -> r2[p]++; case 3 -> c2 = r2[p]; default -> s2++; }
            pc2[p]++;
            countRaceSem(pc2, r2, s2, c2, ends, total);
        }
    }
}
