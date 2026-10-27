import java.util.*;

/**
 * Era 8, topic 4: Consistent hashing (Karger, Lehman, Leighton, Levine, Lewin and Panigrahy, MIT, 1997; Chord, 2001).
 *
 * HOW IT WORKS
 *   Many servers share many keys (web pages, files, records). The obvious rule, server = hash(key) mod N, spreads
 *   them evenly, but when N changes almost every key gets a new server: hash mod 10 and hash mod 11 agree for only
 *   about one key in 11. Consistent hashing puts servers and keys on the same circle of hash values and gives each key
 *   to the first server clockwise from it. A new server takes over only the keys between it and the server before it;
 *   a server that leaves hands its keys to the next one; nothing else moves. One point per server gives uneven arcs,
 *   so each server is placed at many points ("virtual nodes"), which evens out the load.
 *   Chord (2001) finds a key's server without any central list: each node knows the nodes 1, 2, 4, 8, ... positions
 *   ahead on the circle (its "fingers"), and each hop at least halves the remaining distance, so a lookup among N
 *   nodes takes about log2 N hops.
 *   Rendezvous hashing (1996) is a relative: each key goes to the server with the highest hash(key, server).
 *
 * WHAT THIS PROGRAM DOES
 *   1. 100,000 keys on 10 servers, then 11: how many move under mod-N, the circle and rendezvous hashing, and where.
 *   2. A server leaves: only its keys move, all to its successor.
 *   3. Load balance with 1 to 1,000 points per server.
 *   4. Clients that know different sets of servers: how many servers does one key end up on ("spread")?
 *   5. Chord: 1,024 nodes, 10,000 lookups by fingers.
 *   6. A small circle of named servers and keys for the book's widget, hashed with 32-bit FNV-1a and a mixing step.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ConsistentHashing.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ConsistentHashing {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long mix64(long z) {
        z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
        z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
        return z ^ (z >>> 31);
    }

    static long keyHash(int k) { return mix64(k * 0x9e3779b97f4a7c15L + 1); }

    static long pointHash(int server, int replica) { return mix64(((long) server << 32 | replica) * 0x9e3779b97f4a7c15L + 2); }

    /** The circle: sorted (position -> server). Positions are unsigned 64-bit hashes; TreeMap compares them unsigned. */
    static TreeMap<Long, Integer> ring(int[] servers, int replicas) {
        TreeMap<Long, Integer> r = new TreeMap<>(Long::compareUnsigned);
        for (int s : servers) for (int v = 0; v < replicas; v++) r.put(pointHash(s, v), s);
        return r;
    }

    static int owner(TreeMap<Long, Integer> r, long h) {
        Map.Entry<Long, Integer> e = r.ceilingEntry(h);
        return (e != null ? e : r.firstEntry()).getValue();
    }

    static int rendezvous(int[] servers, int key) {
        int best = -1; long bh = 0;
        for (int s : servers) {
            long h = mix64(((long) key << 20 ^ s) * 0x9e3779b97f4a7c15L + 3);
            if (best < 0 || Long.compareUnsigned(h, bh) > 0) { best = s; bh = h; }
        }
        return best;
    }

    static int[] range(int a, int b) { int[] r = new int[b - a]; for (int i = a; i < b; i++) r[i - a] = i; return r; }

    /** 32-bit FNV-1a, followed by MurmurHash3's finalizer so that names differing in one letter land far apart. */
    static int fnv1a(String s) {
        int h = 0x811c9dc5;
        for (char c : s.toCharArray()) { h ^= c; h *= 16777619; }
        h ^= h >>> 16; h *= 0x85ebca6b; h ^= h >>> 13; h *= 0xc2b2ae35; h ^= h >>> 16;
        return h;
    }

    public static void main(String[] args) {
        int K = 100_000;
        // ---- 1. ten servers become eleven ----------------------------------------------------------------------------
        int[] ten = range(0, 10), eleven = range(0, 11);
        int modMoved = 0, ringMoved = 0, rvMoved = 0;
        TreeMap<Long, Integer> r10 = ring(ten, 100), r11 = ring(eleven, 100);
        for (int k = 0; k < K; k++) {
            long h = keyHash(k);
            if (Long.remainderUnsigned(h, 10) != Long.remainderUnsigned(h, 11)) modMoved++;
            int a = owner(r10, h), b = owner(r11, h);
            if (a != b) { ringMoved++; check(b == 10, "on the circle, every key that moves goes to the new server"); }
            int ra = rendezvous(ten, k), rb = rendezvous(eleven, k);
            if (ra != rb) { rvMoved++; check(rb == 10, "under rendezvous hashing too"); }
        }
        check(modMoved > 0.85 * K, "mod-N moves most keys");
        check(ringMoved < 0.15 * K && rvMoved < 0.15 * K, "the circle and rendezvous hashing move about 1/11");
        System.out.printf("grow: %,d keys, 10 servers become 11 ; hash mod N: %,d keys move (%.1f%%) ; circle, 100 points per server: %,d move (%.1f%%), all to the new server ; rendezvous: %,d move (%.1f%%), all to the new server ; a fair share for the newcomer is 1/11 = %.1f%%%n",
                K, modMoved, 100.0 * modMoved / K, ringMoved, 100.0 * ringMoved / K, rvMoved, 100.0 * rvMoved / K, 100.0 / 11);

        // ---- 2. a server leaves ---------------------------------------------------------------------------------------
        int[] withoutThree = {0, 1, 2, 4, 5, 6, 7, 8, 9};
        TreeMap<Long, Integer> r1a = ring(ten, 1), r1b = ring(withoutThree, 1);
        int lost = 0;
        Integer succ = null;
        for (int k = 0; k < K; k++) {
            long h = keyHash(k);
            int a = owner(r1a, h), b = owner(r1b, h);
            if (a != b) {
                check(a == 3, "only the leaving server's keys move");
                if (succ == null) succ = b;
                check(b == succ, "and all of them go to one server, its successor on the circle");
                lost++;
            }
        }
        long p3 = pointHash(3, 0);
        Map.Entry<Long, Integer> nx = r1b.ceilingEntry(p3);
        int expectSucc = (nx != null ? nx : r1b.firstEntry()).getValue();
        check(succ == expectSucc, "the successor is the next point clockwise");
        System.out.printf("leave: one point per server ; server 3 leaves: its %,d keys (%.1f%% of all) move, every one to server %d, the next clockwise ; no other key moves%n", lost, 100.0 * lost / K, succ);

        // ---- 3. load balance ----------------------------------------------------------------------------------------
        StringJoiner lj = new StringJoiner(" ; ");
        double prevWorst = Double.POSITIVE_INFINITY;
        for (int reps : new int[]{1, 10, 100, 1000}) {
            double sumWorst = 0, worstWorst = 0;
            int trials = 50;
            for (int t = 0; t < trials; t++) {
                int[] servers = range(100 * t, 100 * t + 10);
                TreeMap<Long, Integer> r = ring(servers, reps);
                Map<Integer, Integer> load = new HashMap<>();
                for (int k = 0; k < K; k++) load.merge(owner(r, keyHash(k)), 1, Integer::sum);
                int mx = 0;
                for (int s : servers) mx = Math.max(mx, load.getOrDefault(s, 0));
                double ratio = mx / (K / 10.0);
                sumWorst += ratio; worstWorst = Math.max(worstWorst, ratio);
            }
            double avg = sumWorst / trials;
            check(avg <= prevWorst + 1e-9, "more points per server, more even load");
            prevWorst = avg;
            lj.add(String.format("%,d point%s per server: busiest server carries %.2f times its fair share on average (worst of 50: %.2f)", reps, reps == 1 ? "" : "s", avg, worstWorst));
        }
        System.out.printf("balance: 10 servers, 100,000 keys, 50 different sets of servers ; %s%n", lj);

        // ---- 4. spread: clients that know different servers ------------------------------------------------------------
        int S = 20, C = 10;
        Random viewRnd = new Random(1997);
        int[][] views = new int[C][];
        for (int c = 0; c < C; c++) {
            List<Integer> all = new ArrayList<>();
            for (int s = 0; s < S; s++) all.add(s);
            Collections.shuffle(all, viewRnd);
            List<Integer> v = all.subList(0, 12 + viewRnd.nextInt(9)); // each client knows 12 to 20 of the servers
            Collections.sort(v);
            views[c] = v.stream().mapToInt(Integer::intValue).toArray();
        }
        double ringSpread = 0, modSpread = 0;
        int maxRing = 0, maxMod = 0;
        List<TreeMap<Long, Integer>> rings = new ArrayList<>();
        for (int[] v : views) rings.add(ring(v, 100));
        for (int k = 0; k < K; k++) {
            long h = keyHash(k);
            Set<Integer> a = new HashSet<>(), b = new HashSet<>();
            for (int c = 0; c < C; c++) {
                a.add(owner(rings.get(c), h));
                b.add(views[c][(int) Long.remainderUnsigned(h, views[c].length)]);
            }
            ringSpread += a.size(); modSpread += b.size();
            maxRing = Math.max(maxRing, a.size()); maxMod = Math.max(maxMod, b.size());
        }
        check(ringSpread < 0.6 * modSpread, "the circle keeps the spread small");
        System.out.printf("spread: %d servers ; %d clients, each knowing a random 12 to 20 of them ; servers one key is sent to, over all clients: circle %.2f on average (at most %d), hash mod (servers known) %.2f (at most %d)%n",
                S, C, ringSpread / K, maxRing, modSpread / K, maxMod);

        // ---- 5. Chord ----------------------------------------------------------------------------------------------
        int nodes = 1024, lookups = 10_000;
        long[] id = new long[nodes];
        Random cr = new Random(2001);
        TreeSet<Long> ids = new TreeSet<>();
        while (ids.size() < nodes) ids.add(cr.nextLong() & 0xffffffffL); // a 32-bit identifier circle
        int q = 0;
        for (long x : ids) id[q++] = x;
        long[][] finger = new long[nodes][32];
        for (int i = 0; i < nodes; i++) for (int f = 0; f < 32; f++) finger[i][f] = successor(ids, (id[i] + (1L << f)) & 0xffffffffL);
        long totalHops = 0;
        int maxHops = 0;
        int[] hist = new int[33];
        for (int t = 0; t < lookups; t++) {
            long key = cr.nextLong() & 0xffffffffL;
            int start = cr.nextInt(nodes);
            long cur = id[start];
            long target = successor(ids, key);
            int hops = 0;
            while (cur != target) {
                long next = successor(ids, (cur + 1) & 0xffffffffL);
                if (between(key, cur, next)) { cur = next; hops++; break; } // the key lies just past cur: its successor owns it
                // the farthest finger that does not pass the key
                int ci = Arrays.binarySearch(id, cur);
                long best = next;
                for (int f = 31; f >= 0; f--) {
                    long fg = finger[ci][f];
                    if (between(fg, cur, key) && fg != key) { best = fg; break; }
                }
                cur = best; hops++;
            }
            check(cur == target, "every lookup ends at the key's owner");
            totalHops += hops; maxHops = Math.max(maxHops, hops); hist[hops]++;
        }
        double avgHops = (double) totalHops / lookups;
        check(maxHops <= 2 * 10, "no lookup takes more than 2 log2 N hops");
        StringJoiner hj = new StringJoiner(" ");
        for (int h = 0; h <= maxHops; h++) hj.add(h + ":" + hist[h]);
        System.out.printf("chord: %,d nodes at random places on a circle of 2^32 identifiers, 32 fingers each ; %,d lookups from random nodes: %.2f hops on average, at most %d (log2 %,d = 10) ; hops:lookups %s%n", nodes, lookups, avgHops, maxHops, nodes, hj);

        // ---- 6. the widget's circle ----------------------------------------------------------------------------------
        String[] names = {"amber", "basil", "cedar", "delta", "ember", "fjord"};
        int reps = 3, keys = 40;
        StringJoiner pj = new StringJoiner(" ");
        TreeMap<Long, String> wr = new TreeMap<>();
        for (String nm : names) for (int v = 0; v < reps; v++) {
            long pos = fnv1a(nm + "#" + v) & 0xffffffffL;
            wr.put(pos, nm);
            pj.add(nm + "#" + v + ":" + pos);
        }
        String[] before = new String[keys];
        for (int k = 0; k < keys; k++) before[k] = ownerOf(wr, fnv1a("key" + k) & 0xffffffffL);
        TreeMap<Long, String> grown = new TreeMap<>(wr);
        for (int v = 0; v < reps; v++) grown.put(fnv1a("gamma#" + v) & 0xffffffffL, "gamma");
        int movedIn = 0;
        StringJoiner mj = new StringJoiner(",");
        for (int k = 0; k < keys; k++) {
            String after = ownerOf(grown, fnv1a("key" + k) & 0xffffffffL);
            if (!after.equals(before[k])) { check(after.equals("gamma"), "widget: moved keys go to the newcomer"); movedIn++; mj.add(Integer.toString(k)); }
        }
        TreeMap<Long, String> shrunk = new TreeMap<>(wr);
        shrunk.values().removeIf(x -> x.equals("cedar"));
        int movedOut = 0;
        for (int k = 0; k < keys; k++) {
            String after = ownerOf(shrunk, fnv1a("key" + k) & 0xffffffffL);
            if (!after.equals(before[k])) { check(before[k].equals("cedar"), "widget: only cedar's keys move"); movedOut++; }
        }
        Map<String, Integer> loads = new TreeMap<>();
        for (String b : before) loads.merge(b, 1, Integer::sum);
        int modMovedW = 0;
        for (int k = 0; k < keys; k++) if (Integer.remainderUnsigned(fnv1a("key" + k), 6) != Integer.remainderUnsigned(fnv1a("key" + k), 7)) modMovedW++;
        System.out.printf("widget: positions are 32-bit FNV-1a hashes, mixed by MurmurHash3's finalizer, of the names (server#copy) and of key0 ... key39 ; points %s ; keys per server: %s ; gamma joins: %d keys move, all to gamma (keys %s) ; cedar leaves instead: %d keys move ; with hash mod 6 becoming mod 7, %d of 40 keys would move%n",
                pj, loads, movedIn, mj, movedOut, modMovedW);

        System.out.println("ConsistentHashing: " + passed + " checks passed");
    }

    static String ownerOf(TreeMap<Long, String> r, long h) {
        Map.Entry<Long, String> e = r.ceilingEntry(h);
        return (e != null ? e : r.firstEntry()).getValue();
    }

    static long successor(TreeSet<Long> ids, long x) { Long s = ids.ceiling(x); return s != null ? s : ids.first(); }

    /** Is x in the circular interval (a, b]? */
    static boolean between(long x, long a, long b) {
        if (a < b) return x > a && x <= b;
        return x > a || x <= b;
    }
}
