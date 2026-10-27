import java.nio.file.*;
import java.util.*;
import java.util.function.*;

/**
 * Era 8, topic 11: MapReduce (Jeffrey Dean and Sanjay Ghemawat, Google, OSDI 2004).
 *
 * HOW IT WORKS
 *   The programmer writes two functions. map(record) emits (key, value) pairs; reduce(key, all values for that key)
 *   combines them. For counting words: map emits (word, 1) for each word of its piece of text; reduce adds up the 1s.
 *   The library does the rest. It cuts the input into M pieces and runs a map task on each, on whichever machine is
 *   free; each map task sorts its output into R parts by hash(key) mod R and keeps them on its own disk. Then R reduce
 *   tasks each fetch their part from every map task, group by key, and write the results to a shared file system.
 *   Because map and reduce are deterministic and change nothing else, any task can be run again with the same
 *   result. So when a machine dies, the master simply runs its tasks again elsewhere, including finished map tasks,
 *   whose output was on the dead machine's disk. And when the job is nearly done, the master starts backup copies of
 *   the tasks still running; whichever copy finishes first counts, so one slow machine cannot hold up the whole job.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Counts the words of this book's field notes (corpus.txt) with 40 map tasks and 8 reduce tasks on a simulated
 *      cluster of 10 machines, and checks the result against a plain count.
 *   2. The same job when a machine dies halfway through the map phase; when one machine runs 5 times slower; and the
 *      slow machine again with backup tasks. Time is simulated: a task's duration is its amount of data divided by
 *      its machine's speed. The counts are checked to be identical every time.
 *   3. PageRank (topic 7) written as a map and a reduce, run for 10 rounds on topic 7's 8-page web.
 *   4. A smaller job (12 map tasks, 3 reduce tasks, 6 machines) whose schedules are printed for the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step; corpus.txt must be in the current folder)
 *   java MapReduce.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MapReduce {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** A simulated cluster run: which machine ran which task when, and the job's result. */
    static final class Run {
        double finish;
        int mapRuns, reduceRuns, backups, killed;
        List<String> schedule = new ArrayList<>();
        Map<String, Long> result = new TreeMap<>();
    }

    static int partition(String key, int R) { return Math.floorMod(key.hashCode(), R); }

    /**
     * Simulate word count. speeds[w] = work per unit time of machine w; failAt = time machine 0 dies (or infinity);
     * backups = start backup copies of running tasks when nothing else is left to start.
     */
    static Run simulate(List<List<String>> splits, int R, double[] speeds, double failAt, boolean backups) {
        int M = splits.size(), W = speeds.length;
        Run run = new Run();
        // the map function and the reduce function: the only code a MapReduce user writes
        Function<List<String>, List<Map.Entry<String, Long>>> map = words -> {
            List<Map.Entry<String, Long>> out = new ArrayList<>();
            for (String w : words) out.add(Map.entry(w, 1L));
            return out;
        };
        BiFunction<String, List<Long>, Long> reduce = (k, vs) -> { long s = 0; for (long v : vs) s += v; return s; };

        List<List<List<Map.Entry<String, Long>>>> mapOut = new ArrayList<>(); // [map task][partition] -> pairs
        for (int m = 0; m < M; m++) mapOut.add(null);
        int[] mapWhere = new int[M];
        boolean[] mapDone = new boolean[M], reduceDone = new boolean[R];
        boolean dead = false;
        // running copies: {task id (map m, or M + r for reduce r), machine, start, end}
        List<double[]> running = new ArrayList<>();
        double now = 0;
        Deque<Integer> pending = new ArrayDeque<>();
        for (int m = 0; m < M; m++) pending.add(m);
        long totalPairs = 0;
        for (List<String> s : splits) totalPairs += s.size();
        while (true) {
            boolean allMaps = true;
            for (boolean d : mapDone) allMaps &= d;
            boolean allReduces = true;
            for (boolean d : reduceDone) allReduces &= d;
            if (allMaps && allReduces) break;
            if (allMaps && pending.isEmpty() && running.isEmpty()) for (int r = 0; r < R; r++) if (!reduceDone[r]) pending.add(M + r);
            // give work to idle machines
            for (int w = 0; w < W; w++) {
                if (w == 0 && dead) continue;
                final int ww = w;
                boolean busy = running.stream().anyMatch(c -> c[1] == ww);
                if (busy) continue;
                Integer task = pending.poll();
                boolean backup = false;
                if (task == null && backups && !running.isEmpty()) { // a backup copy of the running task that will end last,
                    double[] latest = null;                              // if a fresh copy here would finish sooner
                    for (double[] c : running) {
                        int t = (int) c[0];
                        long copies = running.stream().filter(x -> x[0] == t).count();
                        double w0 = t < M ? splits.get(t).size() / 100.0 : (double) totalPairs / R / 200.0;
                        if (copies == 1 && now + w0 / speeds[w] < c[3] && (latest == null || c[3] > latest[3])) latest = c;
                    }
                    if (latest != null) { task = (int) latest[0]; backup = true; }
                }
                if (task == null) continue;
                if (task >= M && !allMaps) { pending.addFirst(task); continue; }
                double work = task < M ? splits.get(task).size() / 100.0 : (double) totalPairs / R / 200.0;
                running.add(new double[]{task, w, now, now + work / speeds[w]});
                if (backup) run.backups++;
            }
            // the next event: a task copy finishes, or machine 0 dies
            double next = Double.POSITIVE_INFINITY;
            double[] first = null;
            for (double[] c : running) if (c[3] < next) { next = c[3]; first = c; }
            if (!dead && failAt < next) {
                now = failAt; dead = true;
                Iterator<double[]> it = running.iterator();
                while (it.hasNext()) { double[] c = it.next(); if (c[1] == 0) { run.schedule.add(sched(c, now, "lost", M)); it.remove(); if (running.stream().noneMatch(x -> x[0] == c[0])) pending.addFirst((int) c[0]); } }
                for (int m = 0; m < M; m++) if (mapDone[m] && mapWhere[m] == 0) { // finished map output lived on the dead disk
                    mapDone[m] = false; mapOut.set(m, null); pending.add(m);
                    run.schedule.add("machine 0's finished map " + m + " must run again");
                }
                continue;
            }
            if (first == null) throw new IllegalStateException("stuck");
            now = next;
            running.remove(first);
            int t = (int) first[0], w = (int) first[1];
            run.schedule.add(sched(first, now, "done", M));
            // the first copy to finish counts; other copies of the same task are stopped
            Iterator<double[]> it = running.iterator();
            while (it.hasNext()) { double[] c = it.next(); if (c[0] == t) { run.schedule.add(sched(c, now, "stopped", M)); it.remove(); run.killed++; } }
            if (t < M) {
                run.mapRuns++;
                List<List<Map.Entry<String, Long>>> parts = new ArrayList<>();
                for (int r = 0; r < R; r++) parts.add(new ArrayList<>());
                for (Map.Entry<String, Long> e : map.apply(splits.get(t))) parts.get(partition(e.getKey(), R)).add(e);
                mapOut.set(t, parts); mapDone[t] = true; mapWhere[t] = w;
            } else {
                run.reduceRuns++;
                int r = t - M;
                TreeMap<String, List<Long>> grouped = new TreeMap<>();
                for (int m = 0; m < M; m++) for (Map.Entry<String, Long> e : mapOut.get(m).get(r)) grouped.computeIfAbsent(e.getKey(), x -> new ArrayList<>()).add(e.getValue());
                for (Map.Entry<String, List<Long>> g : grouped.entrySet()) run.result.put(g.getKey(), reduce.apply(g.getKey(), g.getValue()));
                reduceDone[r] = true;
            }
        }
        run.finish = now;
        // no machine ever ran two task copies at once
        for (int w = 0; w < W; w++) {
            List<double[]> iv = new ArrayList<>();
            for (String e : run.schedule) {
                if (!e.contains("@")) continue;
                String[] f = e.split("[@:-]");
                if (Integer.parseInt(f[1]) == w) iv.add(new double[]{Double.parseDouble(f[2]), Double.parseDouble(f[3])});
            }
            iv.sort((x, y) -> Double.compare(x[0], y[0]));
            for (int i = 1; i < iv.size(); i++) check(iv.get(i)[0] >= iv.get(i - 1)[1] - 1e-9, "a machine runs one task at a time");
        }
        return run;
    }

    static String sched(double[] c, double end, String how, int M) {
        int t = (int) c[0];
        return String.format("%s%d@%d:%.2f-%.2f:%s", t < M ? "m" : "r", t < M ? t : t - M, (int) c[1], c[2], end, how);
    }

    public static void main(String[] args) throws Exception {
        String text = new String(Files.readAllBytes(Paths.get("corpus.txt")), "UTF-8").toLowerCase().replaceAll("[^a-z0-9']+", " ").trim();
        List<String> words = Arrays.asList(text.split(" "));
        Map<String, Long> plain = new TreeMap<>();
        for (String w : words) plain.merge(w, 1L, Long::sum);
        int M = 40, R = 8, W = 10;
        List<List<String>> splits = new ArrayList<>();
        for (int m = 0; m < M; m++) splits.add(words.subList(m * words.size() / M, (m + 1) * words.size() / M));

        // ---- 1 and 2. word count, four ways ----------------------------------------------------------------------------
        double[] even = new double[W];
        Arrays.fill(even, 1);
        double[] slow = even.clone();
        slow[3] = 0.2;
        Object[][] cases = {
                {"normal", even, Double.POSITIVE_INFINITY, false},
                {"machine 0 dies at time 2.0", even, 2.0, false},
                {"machine 3 runs at 1/5 speed, no backups", slow, Double.POSITIVE_INFINITY, false},
                {"machine 3 runs at 1/5 speed, with backups", slow, Double.POSITIVE_INFINITY, true}};
        StringJoiner cj = new StringJoiner(" ; ");
        double[] times = new double[4];
        for (int i = 0; i < cases.length; i++) {
            Run r = simulate(splits, R, (double[]) cases[i][1], (double) cases[i][2], (boolean) cases[i][3]);
            check(r.result.equals(plain), "the job's counts equal a plain count, whatever happened to the machines");
            times[i] = r.finish;
            cj.add(String.format("%s: finished at %.2f, %d map runs and %d reduce runs for 40 and 8 tasks, %s, %s stopped", cases[i][0], r.finish, r.mapRuns, r.reduceRuns, r.backups == 1 ? "1 backup copy" : r.backups + " backup copies", r.killed == 1 ? "1 copy" : r.killed + " copies"));
        }
        check(times[1] > times[0], "a dead machine costs time");
        check(times[2] > 1.3 * times[3], "backups rescue the job from the slow machine");
        System.out.printf("wordcount: corpus.txt, %,d words, %,d different ; %d map tasks, %d reduce tasks, %d machines ; map: (word, 1) for each word ; reduce: the sum ; partition: hash(word) mod %d ; time unit: 100 words mapped or 200 pairs reduced at speed 1 ; %s ; without backups the slow machine makes the job %.0f%% longer%n",
                words.size(), plain.size(), M, R, W, R, cj, 100 * (times[2] / times[3] - 1));
        StringJoiner top = new StringJoiner(" ");
        plain.entrySet().stream().sorted((a, b) -> Long.compare(b.getValue(), a.getValue())).limit(5).forEach(e -> top.add(e.getKey() + ":" + e.getValue()));
        System.out.printf("counts: the 5 commonest words %s%n", top);

        // ---- 3. PageRank as MapReduce ----------------------------------------------------------------------------------
        int[][] web = {{1, 2}, {2}, {0}, {2, 4}, {5}, {3, 6}, {}, {2, 6}};
        int n = web.length;
        double d = 0.85;
        double[] pr = new double[n], direct = new double[n];
        Arrays.fill(pr, 1.0 / n); Arrays.fill(direct, 1.0 / n);
        for (int round = 0; round < 10; round++) {
            // map: page v emits (u, share) for each link v -> u, and ("*", rank) if it has no links
            List<Object[]> pairs = new ArrayList<>();
            for (int v = 0; v < n; v++) {
                if (web[v].length == 0) pairs.add(new Object[]{-1, pr[v]});
                for (int u : web[v]) pairs.add(new Object[]{u, pr[v] / web[v].length});
            }
            double dangling = 0;
            for (Object[] p : pairs) if ((int) p[0] == -1) dangling += (double) p[1];
            // reduce: for each page, (1 - d)/N + d (sum of shares + dangling / N)
            double[] nx = new double[n];
            double[] sums = new double[n];
            for (Object[] p : pairs) if ((int) p[0] >= 0) sums[(int) p[0]] += (double) p[1];
            for (int u = 0; u < n; u++) nx[u] = (1 - d) / n + d * (sums[u] + dangling / n);
            pr = nx;
            // the same round written directly
            double[] dn = new double[n];
            double dd = 0;
            for (int v = 0; v < n; v++) { if (web[v].length == 0) dd += direct[v]; for (int u : web[v]) dn[u] += direct[v] / web[v].length; }
            for (int u = 0; u < n; u++) dn[u] = (1 - d) / n + d * (dn[u] + dd / n);
            direct = dn;
        }
        double diff = 0;
        for (int i = 0; i < n; i++) diff = Math.max(diff, Math.abs(pr[i] - direct[i]));
        check(diff < 1e-15, "PageRank by map and reduce equals PageRank computed directly");
        StringJoiner pj = new StringJoiner(",");
        for (double x : pr) pj.add(String.format("%.4f", x));
        System.out.printf("pagerank: topic 7's 8-page web, 10 rounds, each round one map (each page sends rank / links along each link) and one reduce (each page adds what it received) ; ranks %s ; largest difference from the direct computation %.0e%n", pj, diff);

        // ---- 4. the widget's small job ---------------------------------------------------------------------------------
        List<List<String>> small = new ArrayList<>();
        for (int m = 0; m < 12; m++) small.add(words.subList(m * 100, m * 100 + 100 + (m % 3) * 50));
        double[] six = {1, 1, 1, 1, 1, 1}, sixSlow = {1, 1, 1, 1, 0.25, 1};
        Object[][] wcases = {{"normal", six, Double.POSITIVE_INFINITY, false}, {"failure", six, 2.2, false}, {"straggler", sixSlow, Double.POSITIVE_INFINITY, false}, {"backups", sixSlow, Double.POSITIVE_INFINITY, true}};
        Map<String, Long> smallPlain = new TreeMap<>();
        for (List<String> s : small) for (String w : s) smallPlain.merge(w, 1L, Long::sum);
        for (Object[] c : wcases) {
            Run r = simulate(small, 3, (double[]) c[1], (double) c[2], (boolean) c[3]);
            check(r.result.equals(smallPlain), "widget job: correct counts");
            System.out.printf("widget: %s ; 12 map tasks (100, 150 or 200 words), 3 reduce tasks, 6 machines%s ; finished at %.2f ; task@machine:start-end:outcome %s%n",
                    c[0], c[0].equals("failure") ? ", machine 0 dies at time 2.2" : c[0].equals("normal") ? "" : ", machine 4 at 1/4 speed", r.finish, String.join(" ", r.schedule));
        }

        System.out.println("MapReduce: " + passed + " checks passed");
    }
}
