import java.util.*;

/**
 * Era 6, topic 6: the relational model of data (Codd, 1970).
 *
 * HOW IT WORKS
 *   The databases of the 1960s stored records in trees and chains, and a program found its data by walking them:
 *   to the supplier, then down to the parts that supplier sends. A question that ran against the grain of the tree
 *   ("who sends part 42?") meant walking all of it, and reorganizing the tree broke the programs that walked it.
 *   Codd proposed that a program should see only relations: tables of rows, each row a tuple of values, with no order
 *   and no pointers. Questions are asked with a few operations on whole tables:
 *       restriction  keep the rows that satisfy a condition
 *       projection   keep some columns, drop duplicate rows
 *       join         combine rows of two tables that agree on a column
 *   How the rows are stored, sorted or indexed is the system's business, and may change without changing a question.
 *   Nested records are put in "normal form" by copying each parent's key into its children, giving flat tables.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A supplier-and-part database stored as a tree, and two questions: one with the grain, one against it.
 *   2. The same data as relations: the same two questions, written once, with and without an index.
 *   3. A join of three tables by three methods (nested loops, hashing, sorting): the same answer, different work.
 *   4. Normal form: nested employee records flattened into four tables, and rebuilt from them exactly.
 *   5. One fact in one place: a supplier's city stored in every shipment row against stored once.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Relational.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Relational {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1970L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int rnd(int n) { return (int) (uniform() * n); }

    static long reads;

    // ---- a relation: a set of rows of ints, with optional indexes ----------------------------------------------------
    static class Relation {
        final String[] cols;
        final List<int[]> rows = new ArrayList<>();
        final Map<Integer, Map<Integer, List<int[]>>> index = new HashMap<>();

        Relation(String... cols) { this.cols = cols; }

        int col(String name) { return Arrays.asList(cols).indexOf(name); }

        void add(int... row) { rows.add(row); }

        void makeIndex(String c) {
            int k = col(c);
            Map<Integer, List<int[]>> m = new HashMap<>();
            for (int[] r : rows) m.computeIfAbsent(r[k], x -> new ArrayList<>()).add(r);
            index.put(k, m);
        }

        /** Restriction: the rows whose column c equals v. Uses an index if one exists; the caller cannot tell. */
        Relation where(String c, int v) {
            int k = col(c);
            Relation out = new Relation(cols);
            if (index.containsKey(k)) {
                for (int[] r : index.get(k).getOrDefault(v, List.of())) { reads++; out.rows.add(r); }
            } else {
                for (int[] r : rows) { reads++; if (r[k] == v) out.rows.add(r); }
            }
            return out;
        }

        /** Projection onto some columns, duplicates removed; the result is a set, so it is returned sorted. */
        TreeSet<List<Integer>> project(String... cs) {
            int[] ks = Arrays.stream(cs).mapToInt(this::col).toArray();
            TreeSet<List<Integer>> out = new TreeSet<>(Relational::compareLists);
            for (int[] r : rows) {
                List<Integer> t = new ArrayList<>();
                for (int k : ks) t.add(r[k]);
                out.add(t);
            }
            return out;
        }
    }

    static int compareLists(List<Integer> a, List<Integer> b) {
        for (int i = 0; i < Math.min(a.size(), b.size()); i++) { int c = Integer.compare(a.get(i), b.get(i)); if (c != 0) return c; }
        return Integer.compare(a.size(), b.size());
    }

    static long work;

    /** Join of R and S on R.a = S.b, by one of three methods; returns rows of R's columns followed by S's. */
    static List<int[]> join(List<int[]> R, int a, List<int[]> S, int b, String method) {
        List<int[]> out = new ArrayList<>();
        switch (method) {
            case "nested" -> {
                for (int[] r : R) for (int[] s : S) { work++; if (r[a] == s[b]) out.add(concat(r, s)); }
            }
            case "hash" -> {
                Map<Integer, List<int[]>> h = new HashMap<>();
                for (int[] r : R) { work++; h.computeIfAbsent(r[a], x -> new ArrayList<>()).add(r); }
                for (int[] s : S) { work++; for (int[] r : h.getOrDefault(s[b], List.of())) out.add(concat(r, s)); }
            }
            case "merge" -> {
                List<int[]> r2 = new ArrayList<>(R), s2 = new ArrayList<>(S);
                r2.sort((x, y) -> { work++; return Integer.compare(x[a], y[a]); });
                s2.sort((x, y) -> { work++; return Integer.compare(x[b], y[b]); });
                int i = 0, j = 0;
                while (i < r2.size() && j < s2.size()) {
                    work++;
                    int c = Integer.compare(r2.get(i)[a], s2.get(j)[b]);
                    if (c < 0) i++;
                    else if (c > 0) j++;
                    else {
                        int v = r2.get(i)[a], j0 = j;
                        while (i < r2.size() && r2.get(i)[a] == v) {
                            for (j = j0; j < s2.size() && s2.get(j)[b] == v; j++) { work++; out.add(concat(r2.get(i), s2.get(j))); }
                            i++;
                        }
                    }
                }
            }
        }
        return out;
    }

    static int[] concat(int[] x, int[] y) {
        int[] z = Arrays.copyOf(x, x.length + y.length);
        System.arraycopy(y, 0, z, x.length, y.length);
        return z;
    }

    public static void main(String[] args) {
        int nSup = 200, nPart = 1000, nShip = 20000;
        String[] cityNames = {"Aberdeen", "Bergen", "Cork", "Dundee", "Esbjerg", "Faro", "Genoa", "Hull", "Izmir", "Jaffa"};
        String[] colors = {"red", "green", "blue", "black", "gold"};                // gold is rare: 1 part in 100
        Relation supplier = new Relation("s", "city"), part = new Relation("p", "color"), supply = new Relation("s", "p", "qty");
        for (int s = 0; s < nSup; s++) supplier.add(s, rnd(cityNames.length));
        for (int p = 0; p < nPart; p++) part.add(p, rnd(100) == 0 ? 4 : rnd(4));
        Set<Long> seen = new HashSet<>();
        while (supply.rows.size() < nShip) {
            int s = rnd(nSup), p = rnd(nPart);
            if (seen.add((long) s * nPart + p)) supply.add(s, p, 1 + rnd(500));
        }

        // ---- 1. a tree ----------------------------------------------------------------------------------------------------
        // Root records are suppliers (found directly by number); under each, its shipments in the order they were added.
        Map<Integer, List<int[]>> bySupplier = new TreeMap<>(), byPart = new TreeMap<>();
        for (int[] r : supply.rows) {
            bySupplier.computeIfAbsent(r[0], x -> new ArrayList<>()).add(r);
            byPart.computeIfAbsent(r[1], x -> new ArrayList<>()).add(r);
        }
        int S7 = 7, P42 = 42;
        // with the grain: the parts that supplier 7 sends
        reads = 1;
        TreeSet<Integer> q1tree = new TreeSet<>();
        for (int[] c : bySupplier.getOrDefault(S7, List.of())) { reads++; q1tree.add(c[1]); }
        long q1reads = reads;
        // against the grain: the suppliers who send part 42 -- every root and every child must be read
        reads = 0;
        TreeSet<Integer> q2tree = new TreeSet<>();
        for (Map.Entry<Integer, List<int[]>> root : bySupplier.entrySet()) {
            reads++;
            for (int[] c : root.getValue()) { reads++; if (c[1] == P42) q2tree.add(root.getKey()); }
        }
        long q2reads = reads;
        // the tree turned the other way: parts at the top -- now the second question is cheap and the first is not
        reads = 1;
        TreeSet<Integer> q2flip = new TreeSet<>();
        for (int[] c : byPart.getOrDefault(P42, List.of())) { reads++; q2flip.add(c[0]); }
        long q2flipReads = reads;
        reads = 0;
        TreeSet<Integer> q1flip = new TreeSet<>();
        for (Map.Entry<Integer, List<int[]>> root : byPart.entrySet()) {
            reads++;
            for (int[] c : root.getValue()) { reads++; if (c[0] == S7) q1flip.add(root.getKey()); }
        }
        long q1flipReads = reads;
        check(q1tree.equals(q1flip) && q2tree.equals(q2flip), "both trees give the same answers");
        check(q2reads == bySupplier.size() + nShip && q1flipReads == byPart.size() + nShip, "against the grain, the whole tree is read");
        System.out.printf("tree: %d suppliers, %,d parts, %,d shipments (supplier, part, quantity) ; stored as a tree with suppliers on top: \"which parts does supplier 7 send?\" reads %d records, \"who sends part 42?\" reads %,d ; turn the tree over, parts on top: the first question now reads %,d, the second %d ; each question is a different program for each tree, 4 programs in all ; answers: supplier 7 sends %d parts, part 42 comes from %d suppliers%n",
                nSup, nPart, nShip, q1reads, q2reads, q1flipReads, q2flipReads, q1tree.size(), q2tree.size());

        // ---- 2. relations -------------------------------------------------------------------------------------------------
        reads = 0;
        TreeSet<List<Integer>> q1rel = supply.where("s", S7).project("p");
        long q1scan = reads;
        reads = 0;
        TreeSet<List<Integer>> q2rel = supply.where("p", P42).project("s");
        long q2scan = reads;
        supply.makeIndex("s");
        supply.makeIndex("p");
        reads = 0;
        TreeSet<List<Integer>> q1idx = supply.where("s", S7).project("p");
        long q1i = reads;
        reads = 0;
        TreeSet<List<Integer>> q2idx = supply.where("p", P42).project("s");
        long q2i = reads;
        List<Integer> a1 = new ArrayList<>(), a2 = new ArrayList<>();
        for (List<Integer> t : q1rel) a1.add(t.get(0));
        for (List<Integer> t : q2rel) a2.add(t.get(0));
        check(a1.equals(new ArrayList<>(q1tree)) && a2.equals(new ArrayList<>(q2tree)), "relations give the tree's answers");
        check(q1rel.equals(q1idx) && q2rel.equals(q2idx), "an index changes the work, not the answer");
        check(q1i == q1tree.size() && q2i == q2tree.size(), "with an index only the matching rows are read");
        System.out.printf("relations: the same data as three tables, supplier(s, city), part(p, color), supply(s, p, qty) ; each question is one line, project(restrict(supply, s = 7), p) and project(restrict(supply, p = 42), s) ; with no index both read all %,d rows ; after the system adds an index on s and on p, the same two lines read %d and %d rows ; same answers as the trees%n",
                q1scan == q2scan ? q1scan : -1, q1i, q2i);

        // ---- 3. a join ----------------------------------------------------------------------------------------------------
        // Which suppliers in Genoa (city 6) send a gold part (color 4)?
        int GENOA = 6, GOLD = 4;
        Relation genoa = supplier.where("city", GENOA), gold = part.where("color", GOLD);
        StringJoiner jj = new StringJoiner(" ; ");
        TreeSet<Integer> first = null;
        long[] costs = new long[3];
        String[] methods = {"nested", "hash", "merge"};
        String[] labels = {"nested loops (every pair compared)", "hashing (one table put in buckets by key)", "sorting both and merging"};
        for (int m = 0; m < 3; m++) {
            work = 0;
            List<int[]> sp = join(genoa.rows, 0, supply.rows, 0, methods[m]);        // supplier columns s, city ; then s, p, qty
            List<int[]> spr = join(sp, 3, gold.rows, 0, methods[m]);                 // then p, color
            TreeSet<Integer> ans = new TreeSet<>();
            for (int[] r : spr) ans.add(r[0]);
            costs[m] = work;
            if (first == null) first = ans;
            check(ans.equals(first), methods[m] + " gives the same answer");
            jj.add(String.format("%s: %,d steps", labels[m], work));
        }
        // the answer checked a fourth way, by brute force over all shipments
        TreeSet<Integer> brute = new TreeSet<>();
        int[] cityOf = new int[nSup], colorOf = new int[nPart];
        for (int[] r : supplier.rows) cityOf[r[0]] = r[1];
        for (int[] r : part.rows) colorOf[r[0]] = r[1];
        for (int[] r : supply.rows) if (cityOf[r[0]] == GENOA && colorOf[r[1]] == GOLD) brute.add(r[0]);
        check(brute.equals(first), "the join is right");
        check(costs[1] < costs[2] && costs[2] < costs[0], "hashing < sorting < nested loops here");
        System.out.printf("join: \"which suppliers in Genoa send a gold part?\" ; restrict supplier to Genoa (%d rows) and part to gold (%d rows), join both with supply (%,d rows) ; %s ; all three find the same %d suppliers, as does a check of every shipment ; the question did not say how, so the system may choose%n",
                genoa.rows.size(), gold.rows.size(), nShip, jj, first.size());

        // ---- 4. normal form -------------------------------------------------------------------------------------------
        // An employee record holds a job history (each job holding a salary history) and a list of children.
        int nEmp = 60;
        List<Object[]> employees = new ArrayList<>();
        for (int e = 0; e < nEmp; e++) {
            List<Object[]> jobs = new ArrayList<>();
            int jobsN = 1 + rnd(4), year = 1950 + rnd(10);
            for (int j = 0; j < jobsN; j++) {
                List<int[]> sal = new ArrayList<>();
                int salN = 1 + rnd(3);
                for (int k = 0; k < salN; k++) sal.add(new int[]{year + k, 3000 + 100 * rnd(50)});
                jobs.add(new Object[]{year, rnd(20), sal});
                year += salN + rnd(3);
            }
            List<int[]> kids = new ArrayList<>();
            int kidsN = rnd(4);
            for (int k = 0; k < kidsN; k++) kids.add(new int[]{rnd(1000), 1955 + rnd(15)});
            employees.add(new Object[]{1000 + e, 1920 + rnd(20), jobs, kids});
        }
        Relation emp = new Relation("man", "born"), job = new Relation("man", "jobdate", "title"),
                sal = new Relation("man", "jobdate", "saldate", "salary"), child = new Relation("man", "childname", "childborn");
        for (Object[] e : employees) {
            int man = (int) e[0];
            emp.add(man, (int) e[1]);
            for (Object o : (List<?>) e[2]) {
                Object[] jb = (Object[]) o;
                job.add(man, (int) jb[0], (int) jb[1]);                                  // the parent's key is copied down
                for (Object so : (List<?>) jb[2]) { int[] s = (int[]) so; sal.add(man, (int) jb[0], s[0], s[1]); }
            }
            for (Object ko : (List<?>) e[3]) { int[] k = (int[]) ko; child.add(man, k[0], k[1]); }
        }
        // rebuild every employee from the four flat tables and compare
        job.makeIndex("man"); child.makeIndex("man"); sal.makeIndex("man");
        int rebuilt = 0;
        for (Object[] e : employees) {
            int man = (int) e[0];
            List<int[]> js = job.where("man", man).rows, ks = child.where("man", man).rows, ss = sal.where("man", man).rows;
            List<?> jobs = (List<?>) e[2], kids = (List<?>) e[3];
            boolean ok = js.size() == jobs.size() && ks.size() == kids.size();
            for (int j = 0; ok && j < jobs.size(); j++) {
                Object[] jb = (Object[]) jobs.get(j);
                ok = js.get(j)[1] == (int) jb[0] && js.get(j)[2] == (int) jb[1];
                List<?> sl = (List<?>) jb[2];
                List<int[]> mine = new ArrayList<>();
                for (int[] s : ss) if (s[1] == (int) jb[0]) mine.add(s);
                ok &= mine.size() == sl.size();
                for (int k = 0; ok && k < sl.size(); k++) ok = mine.get(k)[2] == ((int[]) sl.get(k))[0] && mine.get(k)[3] == ((int[]) sl.get(k))[1];
            }
            for (int k = 0; ok && k < kids.size(); k++) ok = ks.get(k)[1] == ((int[]) kids.get(k))[0];
            check(ok, "employee " + man + " rebuilt");
            rebuilt++;
        }
        System.out.printf("normal: %d nested employee records (man number, birth year, job history with a salary history inside each job, children) ; flattened by copying each parent's key into its children: employee(man, born) %d rows, jobhistory(man, jobdate, title) %d, salaryhistory(man, jobdate, saldate, salary) %d, children(man, childname, childborn) %d ; all %d employees rebuilt exactly from the flat tables%n",
                nEmp, emp.rows.size(), job.rows.size(), sal.rows.size(), child.rows.size(), rebuilt);

        // ---- 5. one fact, one place -----------------------------------------------------------------------------------
        // A single wide table repeats each supplier's city in every shipment row.
        List<int[]> wide = new ArrayList<>();
        for (int[] r : supply.rows) wide.add(new int[]{r[0], cityOf[r[0]], r[1], r[2]});
        int target = 7, copies = 0;
        for (int[] r : wide) if (r[0] == target) copies++;
        // supplier 7 moves to Bergen (city 1); a careless update changes only the first row it finds
        for (int[] r : wide) if (r[0] == target) { r[1] = 1; break; }
        TreeSet<Integer> citiesSeen = new TreeSet<>();
        for (int[] r : wide) if (r[0] == target) citiesSeen.add(r[1]);
        check(copies > 1 && citiesSeen.size() == 2, "the wide table now contradicts itself");
        System.out.printf("once: a single wide table (s, city, p, qty) repeats supplier 7's city in %d rows ; moving supplier 7 to Bergen means changing all %d, and an update that changes one leaves the table saying both %s and %s ; with supplier(s, city) the city is stored once, one row to change%n",
                copies, copies, cityNames[citiesSeen.first()], cityNames[citiesSeen.last()]);

        System.out.println("Relational: " + passed + " checks passed");
    }
}
