import java.util.*;

/**
 * Era 8, topic 7: PageRank (Larry Page and Sergey Brin, Stanford, 1996-1998), with Kleinberg's hubs and authorities.
 *
 * HOW IT WORKS
 *   A page is important if important pages link to it. Write PR(u) for page u's rank; a page v with L(v) outgoing links
 *   passes PR(v) / L(v) along each of them. With N pages and a damping factor d (0.85):
 *       PR(u) = (1 - d) / N + d * sum over pages v linking to u of PR(v) / L(v).
 *   This is one equation per page, all at once. Brin and Page read it as a random surfer: at each step, with
 *   probability d follow a random link of the current page, otherwise jump to a page chosen at random. PR(u) is the
 *   long-run share of time spent on u. Pages without links ("dangling") send the surfer to a random page.
 *   The power method: start with every page at 1/N and apply the right-hand side again and again. Each round shrinks
 *   the remaining error by a factor of at most d, so at most about 150 rounds bring it below 10^-10 for d = 0.85,
 *   however many pages there are (on a well-connected web, far fewer); each round costs one pass over the links.
 *   Brin and Page's paper writes PR(u) = (1 - d) + d * sum ..., which is the same ranking multiplied by N.
 *   Kleinberg's HITS gives each page two scores: a good hub links to good authorities, a good authority is linked
 *   from good hubs; alternate the two updates and normalize.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A made-up web of 10,000 pages that grows by preferential attachment (new pages tend to link to pages that are
 *      already well linked), 10% of them dangling. The power method, its rounds and its rate.
 *   2. A web of 500 pages solved exactly by Gaussian elimination, against the power method and against a random
 *      surfer who takes 4,000,000 steps.
 *   3. Rounds needed for d = 0.5, 0.85, 0.95 and 0.99.
 *   4. A link farm: k new pages that all link to one page, and what they buy it.
 *   5. HITS on the same 500 pages.
 *   6. An 8-page web for the book's widget: the first rounds of the power method.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java PageRank.java
 *   Expected output: expected-output.txt in this folder.
 */
public class PageRank {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static int s32 = 1998;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    /**
     * A web grown by preferential attachment: each new page links to up to 5 earlier pages, chosen with probability
     * proportional to (in-links + 1); a share of pages get no links at all (dangling). Then each page with links adds 2
     * more to pages anywhere, so that links also point forward and the web has cycles.
     */
    static int[][] growWeb(int n, double danglingShare) {
        List<Set<Integer>> out = new ArrayList<>();
        List<Integer> urn = new ArrayList<>(); // page i appears (in-links + 1) times
        for (int i = 0; i < n; i++) {
            Set<Integer> links = new LinkedHashSet<>();
            boolean dangling = i > 5 && next32() < danglingShare;
            if (i > 0 && !dangling) {
                int want = Math.min(5, i);
                while (links.size() < want) links.add(urn.get((int) (next32() * urn.size())));
            }
            out.add(links);
            for (int j : links) urn.add(j);
            urn.add(i);
        }
        for (int i = 0; i < n; i++) { // then every page that has links adds 2 more, to any page, again by popularity
            Set<Integer> links = out.get(i);
            if (links.isEmpty()) continue;
            int want = links.size() + 2;
            while (links.size() < want) { int j = urn.get((int) (next32() * urn.size())); if (j != i) links.add(j); }
        }
        int[][] g = new int[n][];
        for (int i = 0; i < n; i++) g[i] = out.get(i).stream().mapToInt(Integer::intValue).toArray();
        return g;
    }

    /** One round: next(u) = (1 - d)/N + d (sum of PR(v)/L(v) over v -> u + dangling mass / N). */
    static double[] round(int[][] g, double[] pr, double d) {
        int n = g.length;
        double[] nx = new double[n];
        double dangling = 0;
        for (int v = 0; v < n; v++) {
            if (g[v].length == 0) { dangling += pr[v]; continue; }
            double share = pr[v] / g[v].length;
            for (int u : g[v]) nx[u] += share;
        }
        for (int u = 0; u < n; u++) nx[u] = (1 - d) / n + d * (nx[u] + dangling / n);
        return nx;
    }

    static double l1(double[] a, double[] b) { double s = 0; for (int i = 0; i < a.length; i++) s += Math.abs(a[i] - b[i]); return s; }

    static int lastRounds;
    static double[] lastDiffs;

    static double[] power(int[][] g, double d, double tol) {
        int n = g.length;
        double[] pr = new double[n];
        Arrays.fill(pr, 1.0 / n);
        List<Double> diffs = new ArrayList<>();
        for (int r = 1; r <= 100_000; r++) {
            double[] nx = round(g, pr, d);
            double diff = l1(nx, pr);
            diffs.add(diff);
            pr = nx;
            if (diff < tol) { lastRounds = r; break; }
        }
        lastDiffs = diffs.stream().mapToDouble(Double::doubleValue).toArray();
        return pr;
    }

    static double[] exact(int[][] g, double d) { // solve (I - d M) x = (1 - d)/N with the dangling columns filled
        int n = g.length;
        double[][] a = new double[n][n + 1];
        for (int u = 0; u < n; u++) { a[u][u] = 1; a[u][n] = (1 - d) / n; }
        for (int v = 0; v < n; v++) {
            if (g[v].length == 0) { for (int u = 0; u < n; u++) a[u][v] -= d / n; }
            else for (int u : g[v]) a[u][v] -= d / g[v].length;
        }
        for (int c = 0; c < n; c++) { // Gaussian elimination with partial pivoting
            int piv = c;
            for (int r = c + 1; r < n; r++) if (Math.abs(a[r][c]) > Math.abs(a[piv][c])) piv = r;
            double[] t = a[c]; a[c] = a[piv]; a[piv] = t;
            for (int r = c + 1; r < n; r++) {
                double f = a[r][c] / a[c][c];
                if (f != 0) for (int k = c; k <= n; k++) a[r][k] -= f * a[c][k];
            }
        }
        double[] x = new double[n];
        for (int r = n - 1; r >= 0; r--) {
            double s = a[r][n];
            for (int k = r + 1; k < n; k++) s -= a[r][k] * x[k];
            x[r] = s / a[r][r];
        }
        return x;
    }

    static Integer[] order(double[] pr) {
        Integer[] idx = new Integer[pr.length];
        for (int i = 0; i < idx.length; i++) idx[i] = i;
        Arrays.sort(idx, (a, b) -> pr[b] != pr[a] ? Double.compare(pr[b], pr[a]) : Integer.compare(a, b));
        return idx;
    }

    static int place(double[] pr, int page) { Integer[] o = order(pr); for (int i = 0; i < o.length; i++) if (o[i] == page) return i + 1; return -1; }

    public static void main(String[] args) {
        // ---- 1. 10,000 pages --------------------------------------------------------------------------------------------
        int[][] web = growWeb(10_000, 0.10);
        long links = 0; int dang = 0;
        for (int[] o : web) { links += o.length; if (o.length == 0) dang++; }
        double[] pr = power(web, 0.85, 1e-10);
        int rounds = lastRounds;
        double sum = 0;
        for (double x : pr) sum += x;
        check(Math.abs(sum - 1) < 1e-9, "the ranks add up to 1");
        for (double x : pr) check(x >= 0.15 / pr.length - 1e-15, "every page gets at least its share of random jumps, (1 - d)/N");
        check(l1(round(web, pr, 0.85), pr) < 1e-10, "the ranks satisfy the equations");
        double worstRate = 0;
        for (int r = 5; r < lastDiffs.length; r++) worstRate = Math.max(worstRate, lastDiffs[r] / lastDiffs[r - 1]);
        check(worstRate <= 0.85 + 1e-9, "each round shrinks the change by at most d");
        Integer[] top = order(pr);
        int[] in = new int[web.length];
        for (int[] o : web) for (int u : o) in[u]++;
        StringJoiner tj = new StringJoiner(" ");
        for (int i = 0; i < 5; i++) tj.add(String.format("%d:%.5f:%d", top[i], pr[top[i]], in[top[i]]));
        System.out.printf("web: %,d pages, %,d links, %,d dangling pages ; d = 0.85 ; power method from 1/N: %d rounds to a change below 10^-10 ; ranks sum to 1 and satisfy the equations ; each round shrank the change by a factor of at most %.4f (d = 0.85) ; top pages page:rank:links in %s%n", web.length, links, dang, rounds, worstRate, tj);

        // ---- 2. 500 pages: exact, power, surfer -------------------------------------------------------------------------
        s32 = 500;
        int[][] small = growWeb(500, 0.10);
        double[] ex = exact(small, 0.85), pw = power(small, 0.85, 1e-13);
        double maxDiff = 0;
        for (int i = 0; i < ex.length; i++) maxDiff = Math.max(maxDiff, Math.abs(ex[i] - pw[i]));
        check(maxDiff < 1e-12, "the power method agrees with Gaussian elimination");
        long steps = 4_000_000;
        long[] visits = new long[small.length];
        int at = 0;
        for (long t = 0; t < steps; t++) {
            visits[at]++;
            if (small[at].length == 0 || next32() >= 0.85) at = (int) (next32() * small.length);
            else at = small[at][(int) (next32() * small[at].length)];
        }
        double maxSurf = 0;
        for (int i = 0; i < ex.length; i++) maxSurf = Math.max(maxSurf, Math.abs((double) visits[i] / steps - ex[i]));
        Integer[] oe = order(ex);
        double[] freq = new double[ex.length];
        for (int i = 0; i < ex.length; i++) freq[i] = (double) visits[i] / steps;
        Integer[] of = order(freq);
        int same10 = 0;
        Set<Integer> topE = new HashSet<>(Arrays.asList(oe).subList(0, 10));
        for (int i = 0; i < 10; i++) if (topE.contains(of[i])) same10++;
        check(maxSurf < 0.002, "the surfer's shares approach the ranks");
        for (int i = 0; i < ex.length; i++) check(Math.abs(freq[i] - ex[i]) <= 6 * Math.sqrt(ex[i] / steps * 20) + 1e-4, "each page's share of visits is within sampling error of its rank");
        // Brin and Page's form: the same ranking, times N
        double[] bp = new double[ex.length];
        for (int i = 0; i < ex.length; i++) bp[i] = ex[i] * ex.length;
        double bpRes = 0;
        for (int u = 0; u < ex.length; u++) {
            double s = 0;
            for (int v = 0; v < ex.length; v++) {
                if (small[v].length == 0) s += bp[v] / ex.length;
                else for (int w : small[v]) if (w == u) s += bp[v] / small[v].length;
            }
            bpRes = Math.max(bpRes, Math.abs(bp[u] - ((1 - 0.85) + 0.85 * s)));
        }
        check(bpRes < 1e-9, "N times the ranks satisfies the paper's form PR = (1 - d) + d sum");
        System.out.printf("exact: %d pages ; Gaussian elimination against the power method: largest difference %.1e ; a random surfer, %,d steps: largest difference between share of visits and rank %.5f, %d of the top 10 the same ; N times the ranks satisfies Brin and Page's form (1 - d) + d sum to %.0e%n", small.length, maxDiff, steps, maxSurf, same10, bpRes);

        // ---- 3. the damping factor --------------------------------------------------------------------------------------
        StringJoiner dj = new StringJoiner(" ; ");
        for (double d : new double[]{0.5, 0.85, 0.95, 0.99}) {
            power(web, d, 1e-10);
            int r = lastRounds;
            check(r <= Math.ceil(Math.log(1e-10 / 2) / Math.log(d)) + 1, "rounds within the bound log(tol/2) / log d");
            dj.add(String.format("d = %.2f: %d rounds (bound %d)", d, r, (int) Math.ceil(Math.log(1e-10 / 2) / Math.log(d)) + 1));
        }
        System.out.printf("damping: 10,000-page web, change below 10^-10 ; %s%n", dj);

        // ---- 4. a link farm ------------------------------------------------------------------------------------------
        int target = order(pw)[250]; // a page in the middle of the 500
        StringJoiner fj = new StringJoiner(" ; ");
        double before = pw[target];
        fj.add(String.format("no farm: rank %.5f, place %d of %d", before, place(pw, target), small.length));
        double prevRank = before;
        for (int k : new int[]{1, 10, 100}) {
            int n2 = small.length + k;
            int[][] g2 = new int[n2][];
            for (int i = 0; i < small.length; i++) g2[i] = small[i];
            for (int i = small.length; i < n2; i++) g2[i] = new int[]{target};
            double[] p2 = power(g2, 0.85, 1e-13);
            check(p2[target] > prevRank, "a bigger farm buys a higher rank");
            prevRank = p2[target];
            fj.add(String.format("%d farm page%s: rank %.5f, place %d of %d", k, k == 1 ? "" : "s", p2[target], place(p2, target), n2));
        }
        System.out.printf("farm: page %d of the 500-page web ; new pages that link only to it ; %s%n", target, fj);

        // ---- 5. HITS ---------------------------------------------------------------------------------------------------
        int n = small.length;
        double[] hub = new double[n], auth = new double[n];
        Arrays.fill(hub, 1); Arrays.fill(auth, 1);
        int hr = 0;
        for (; hr < 10_000; hr++) {
            double[] na = new double[n], nh = new double[n];
            for (int v = 0; v < n; v++) for (int u : small[v]) na[u] += hub[v];
            normalize(na);
            for (int v = 0; v < n; v++) for (int u : small[v]) nh[v] += na[u];
            normalize(nh);
            double ch = l1(na, auth) + l1(nh, hub);
            auth = na; hub = nh;
            if (ch < 1e-12) break;
        }
        Integer[] oa = order(auth), oh = order(hub);
        int overlap = 0;
        Set<Integer> topPR = new HashSet<>(Arrays.asList(oe).subList(0, 10));
        for (int i = 0; i < 10; i++) if (topPR.contains(oa[i])) overlap++;
        System.out.printf("hits: %d pages ; %d rounds of alternating updates ; top authorities %d %d %d, top hubs %d %d %d ; %d of the 10 best authorities are among PageRank's top 10%n", n, hr + 1, oa[0], oa[1], oa[2], oh[0], oh[1], oh[2], overlap);

        // ---- 6. the widget's 8 pages -------------------------------------------------------------------------------------
        int[][] w8 = {{1, 2}, {2}, {0}, {2, 4}, {5}, {3, 6}, {}, {2, 6}};
        double[] p8 = new double[8];
        Arrays.fill(p8, 1.0 / 8);
        StringJoiner rj = new StringJoiner(" ; ");
        for (int r = 1; r <= 10; r++) {
            p8 = round(w8, p8, 0.85);
            StringJoiner one = new StringJoiner(",");
            for (double x : p8) one.add(String.format("%.4f", x));
            rj.add(r + ": " + one);
        }
        double[] e8 = exact(w8, 0.85);
        StringJoiner xj = new StringJoiner(",");
        for (double x : e8) xj.add(String.format("%.4f", x));
        System.out.printf("widget: 8 pages A to H ; links A->B,C B->C C->A D->C,E E->F F->D,G G (none: dangling) H->C,G ; d = 0.85 ; rounds of the power method from 1/8: %s ; exact: %s%n", rj, xj);

        System.out.println("PageRank: " + passed + " checks passed");
    }

    static void normalize(double[] v) { double s = 0; for (double x : v) s += x * x; s = Math.sqrt(s); for (int i = 0; i < v.length; i++) v[i] /= s; }
}
