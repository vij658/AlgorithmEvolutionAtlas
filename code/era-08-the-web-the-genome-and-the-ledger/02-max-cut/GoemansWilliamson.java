import java.util.*;

/**
 * Era 8, topic 2: Approximation by semidefinite programming: Goemans and Williamson's MAX CUT (MIT and IBM; STOC 1994,
 * Journal of the ACM 1995).
 *
 * HOW IT WORKS
 *   MAX CUT: split the nodes of a network into two groups so that as many links as possible run between the groups.
 *   It is NP-hard (Era 6), so a fast method can only promise to come close. Flipping a coin for each node cuts each
 *   link with probability 1/2, so on average half of all links: at least half of the best.
 *   Goemans and Williamson give each node i a unit arrow v_i in n dimensions instead of a side (+1 or -1) and maximize
 *   sum over links of (1 - v_i . v_j) / 2. With arrows in one dimension this is exactly MAX CUT; with arrows in many it
 *   is a semidefinite program, which can be solved to any accuracy in polynomial time, and its value is at least the
 *   best cut. Then cut the arrows with a random plane through the origin: two arrows at angle theta fall on opposite
 *   sides with probability theta / pi. Since theta / pi >= 0.87856 (1 - cos theta) / 2 for every angle, the expected
 *   cut is at least 0.87856 times the program's value, and so at least 0.87856 times the best cut.
 *   This program solves the semidefinite program with a simple low-rank method: repeatedly turn each arrow to point
 *   exactly away from the weighted sum of its neighbours' arrows. Each turn can only improve the value. It then
 *   proves the answer optimal with a certificate from the dual program: the matrix Diag(|g_i|) + A must have no
 *   negative eigenvalue, where g_i is the sum of node i's neighbours' arrows and A is the adjacency matrix.
 *
 * WHAT THIS PROGRAM DOES
 *   1. The constant: the minimum of 2 theta / (pi (1 - cos theta)), and where it is reached.
 *   2. The 5-cycle, where the program's value is (5/2)(1 + cos(pi/5)) and the best cut is 4.
 *   3. 200 random networks of 16 nodes: the program's value, the best cut by trying all 32,768 splits, the expected
 *      random-plane cut, the coin flip and a simple local search.
 *   4. A network of 400 nodes, too big to try every split: the program's value as a certificate of quality.
 *   5. The Petersen graph, with the random planes of the book's widget.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java GoemansWilliamson.java
 *   Expected output: expected-output.txt in this folder.
 */
public class GoemansWilliamson {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    // ---- a 32-bit generator simple enough to repeat exactly in JavaScript ------------------------------------------
    static int s32 = 1994;

    static double next32() {
        s32 = s32 * 1664525 + 1013904223;
        return (s32 & 0xffffffffL) / 4294967296.0;
    }

    static double ratio(double th) { return 2 * th / (Math.PI * (1 - Math.cos(th))); }

    /** The relaxation's arrows (rank k), found by the low-rank coordinate method. Returns v[n][k]. */
    static double[][] relax(double[][] w, int k) {
        int n = w.length;
        double[][] v = new double[n][k];
        for (double[] vi : v) { // random start: a point in a cube, scaled to unit length
            double len;
            do { len = 0; for (int d = 0; d < k; d++) { vi[d] = 2 * next32() - 1; len += vi[d] * vi[d]; } } while (len < 1e-6);
            len = Math.sqrt(len);
            for (int d = 0; d < k; d++) vi[d] /= len;
        }
        int[][] nb = new int[n][];
        for (int i = 0; i < n; i++) {
            int c = 0;
            for (int j = 0; j < n; j++) if (w[i][j] != 0) c++;
            nb[i] = new int[c];
            c = 0;
            for (int j = 0; j < n; j++) if (w[i][j] != 0) nb[i][c++] = j;
        }
        double prev = Double.NEGATIVE_INFINITY;
        for (int sweep = 0; sweep < 1_000_000; sweep++) {
            double moved = 0;
            for (int i = 0; i < n; i++) {
                double[] g = new double[k];
                for (int j : nb[i]) for (int d = 0; d < k; d++) g[d] += w[i][j] * v[j][d];
                double len = 0;
                for (int d = 0; d < k; d++) len += g[d] * g[d];
                len = Math.sqrt(len);
                if (len > 1e-15) for (int d = 0; d < k; d++) {
                    double nv = -g[d] / len;
                    moved = Math.max(moved, Math.abs(nv - v[i][d]));
                    v[i][d] = nv;
                }
            }
            double val = sdpValue(w, v, nb);
            check(val >= prev - 1e-9, "each sweep of the coordinate method can only improve the value");
            prev = val;
            if (moved < 1e-11) break;
        }
        return v;
    }

    static double dot(double[] a, double[] b) { double s = 0; for (int d = 0; d < a.length; d++) s += a[d] * b[d]; return s; }

    static double sdpValue(double[][] w, double[][] v, int[][] nb) {
        double s = 0;
        for (int i = 0; i < w.length; i++) for (int j : nb[i]) if (j > i) s += w[i][j] * (1 - dot(v[i], v[j])) / 2;
        return s;
    }

    static double sdpValue(double[][] w, double[][] v) {
        double s = 0;
        for (int i = 0; i < w.length; i++) for (int j = i + 1; j < w.length; j++) if (w[i][j] != 0) s += w[i][j] * (1 - dot(v[i], v[j])) / 2;
        return s;
    }

    /** The dual certificate: Diag(|g_i|) + W must be positive semidefinite (Cholesky with a tiny shift). */
    static boolean certified(double[][] w, double[][] v) {
        int n = w.length, k = v[0].length;
        double[][] m = new double[n][n];
        for (int i = 0; i < n; i++) {
            double[] g = new double[k];
            for (int j = 0; j < n; j++) for (int d = 0; d < k; d++) g[d] += w[i][j] * v[j][d];
            for (int j = 0; j < n; j++) m[i][j] = w[i][j];
            m[i][i] += Math.sqrt(dot(g, g)) + 1e-7;
        }
        for (int j = 0; j < n; j++) { // Cholesky; fails on a negative pivot
            for (int p = 0; p < j; p++) m[j][j] -= m[j][p] * m[j][p];
            if (m[j][j] <= 0) return false;
            m[j][j] = Math.sqrt(m[j][j]);
            for (int i = j + 1; i < n; i++) {
                for (int p = 0; p < j; p++) m[i][j] -= m[i][p] * m[j][p];
                m[i][j] /= m[j][j];
            }
        }
        return true;
    }

    /** The dual's bound (1/4) sum (deg_i + |g_i| + 1e-7): valid when certified() holds; no cut exceeds it. */
    static double dualBound(double[][] w, double[][] v) {
        double b = 0;
        for (int i = 0; i < w.length; i++) {
            double[] g = new double[v[0].length];
            double deg = 0;
            for (int j = 0; j < w.length; j++) { deg += w[i][j]; for (int d = 0; d < g.length; d++) g[d] += w[i][j] * v[j][d]; }
            b += (deg + Math.sqrt(dot(g, g)) + 1e-7) / 4;
        }
        return b;
    }

    /** The exact expected cut of a random plane: sum of w arccos(v_i . v_j) / pi. */
    static double expectedCut(double[][] w, double[][] v) {
        double s = 0;
        for (int i = 0; i < w.length; i++) for (int j = i + 1; j < w.length; j++)
            if (w[i][j] != 0) s += w[i][j] * Math.acos(Math.max(-1, Math.min(1, dot(v[i], v[j])))) / Math.PI;
        return s;
    }

    /**
     * A random direction, all directions equally likely. In up to 5 dimensions: a point in the cube [-1,1]^k, kept only
     * if inside the unit ball (simple to repeat in the widget); in more, where the ball fills too little of the cube,
     * k independent Gaussian numbers (Box-Muller).
     */
    static double[] randomDirection(int k) {
        double[] r = new double[k];
        if (k > 5) {
            for (int d = 0; d < k; d++) r[d] = Math.sqrt(-2 * Math.log(1 - next32())) * Math.cos(2 * Math.PI * next32());
            return r;
        }
        while (true) {
            double len = 0;
            for (int d = 0; d < k; d++) { r[d] = 2 * next32() - 1; len += r[d] * r[d]; }
            if (len <= 1 && len > 1e-12) return r;
        }
    }

    static double cutOf(double[][] w, boolean[] side) {
        double s = 0;
        for (int i = 0; i < w.length; i++) for (int j = i + 1; j < w.length; j++) if (side[i] != side[j]) s += w[i][j];
        return s;
    }

    static boolean[] roundPlane(double[][] v, double[] r) {
        boolean[] side = new boolean[v.length];
        for (int i = 0; i < v.length; i++) side[i] = dot(v[i], r) >= 0;
        return side;
    }

    /** The best cut, by trying all 2^(n-1) splits in Gray-code order (one node changes side per step). */
    static double bestCut(double[][] w) {
        int n = w.length;
        boolean[] side = new boolean[n];
        double cur = 0, best = 0;
        for (long g = 1; g < (1L << (n - 1)); g++) {
            int i = Long.numberOfTrailingZeros(g);
            for (int j = 0; j < n; j++) if (j != i && w[i][j] != 0) cur += side[i] == side[j] ? w[i][j] : -w[i][j];
            side[i] = !side[i];
            best = Math.max(best, cur);
        }
        return best;
    }

    static double localSearch(double[][] w, boolean[] side) {
        boolean improved = true;
        while (improved) {
            improved = false;
            for (int i = 0; i < w.length; i++) {
                double gain = 0;
                for (int j = 0; j < w.length; j++) if (j != i) gain += side[i] == side[j] ? w[i][j] : -w[i][j];
                if (gain > 1e-12) { side[i] = !side[i]; improved = true; }
            }
        }
        return cutOf(w, side);
    }

    static double[][] randomGraph(int n, double p) {
        double[][] w = new double[n][n];
        for (int i = 0; i < n; i++) for (int j = i + 1; j < n; j++) if (next32() < p) w[i][j] = w[j][i] = 1;
        return w;
    }

    static double total(double[][] w) { double s = 0; for (int i = 0; i < w.length; i++) for (int j = i + 1; j < w.length; j++) s += w[i][j]; return s; }

    static int rankFor(int n) { return (int) Math.ceil(Math.sqrt(2 * n)) + 1; }

    public static void main(String[] args) {
        // ---- 1. the constant -----------------------------------------------------------------------------------------
        double lo = 0.5, hi = Math.PI, phi = (Math.sqrt(5) - 1) / 2;
        for (int k = 0; k < 300; k++) {
            double m1 = hi - phi * (hi - lo), m2 = lo + phi * (hi - lo);
            if (ratio(m1) < ratio(m2)) hi = m2; else lo = m1;
        }
        double thStar = (lo + hi) / 2, alpha = ratio(thStar);
        for (int k = 1; k <= 100_000; k++) check(ratio(Math.PI * k / 100_000) >= alpha - 1e-12, "the minimum is the minimum");
        check(alpha > 0.87856 && alpha < 0.87857, "the constant is 0.87856...");
        check(Math.abs(thStar - 2.331122) < 1e-6, "reached at theta = 2.331122, as the paper says");
        System.out.printf("constant: the minimum of 2 theta / (pi (1 - cos theta)) over 0 < theta <= pi is %.6f, reached at theta = %.6f radians (%.2f degrees)%n", alpha, thStar, Math.toDegrees(thStar));

        // ---- 2. the 5-cycle ------------------------------------------------------------------------------------------
        double[][] c5 = new double[5][5];
        for (int i = 0; i < 5; i++) c5[i][(i + 1) % 5] = c5[(i + 1) % 5][i] = 1;
        double[][] v5 = relax(c5, rankFor(5));
        double sdp5 = sdpValue(c5, v5), formula = 2.5 * (1 + Math.cos(Math.PI / 5)), best5 = bestCut(c5), exp5 = expectedCut(c5, v5);
        check(certified(c5, v5), "the 5-cycle's relaxation is certified optimal");
        check(Math.abs(sdp5 - formula) < 1e-8, "the 5-cycle's value is (5/2)(1 + cos(pi/5))");
        check(best5 == 4, "the best cut of the 5-cycle has 4 links");
        System.out.printf("cycle: the 5-cycle: relaxation %.6f (formula (5/2)(1 + cos(pi/5)) = %.6f), certified ; best cut %.0f ; best / relaxation = %.4f ; neighbouring arrows at %.1f degrees ; expected random-plane cut %.6f%n",
                sdp5, formula, best5, best5 / sdp5, Math.toDegrees(Math.acos(dot(v5[0], v5[1]))), exp5);

        // ---- 3. 200 random networks of 16 nodes ---------------------------------------------------------------------
        s32 = 1995;
        int graphs = 200, n = 16;
        double minRatio = 9, sumRatio = 0, minGap = 9, sumCoin = 0, sumLocal = 0, minLocal = 9, sumBestPlane = 0;
        int planeHitsBest = 0, localHitsBest = 0;
        for (int g = 0; g < graphs; g++) {
            double[][] w = randomGraph(n, 0.5);
            double[][] v = relax(w, rankFor(n));
            check(certified(w, v), "each relaxation is certified optimal by the dual");
            double sdp = sdpValue(w, v), opt = bestCut(w), exp = expectedCut(w, v);
            check(sdp >= opt - 1e-9, "the relaxation's value is at least the best cut");
            check(exp >= alpha * sdp - 1e-9, "expected random-plane cut >= 0.87856 x relaxation");
            check(exp <= opt + 1e-9, "no average of cuts beats the best cut");
            double bestPlane = 0;
            for (int t = 0; t < 100; t++) bestPlane = Math.max(bestPlane, cutOf(w, roundPlane(v, randomDirection(v[0].length))));
            check(bestPlane <= opt, "no plane's cut beats the best cut");
            boolean[] coin = new boolean[n];
            for (int i = 0; i < n; i++) coin[i] = next32() < 0.5;
            double loc = localSearch(w, coin);
            minRatio = Math.min(minRatio, exp / opt); sumRatio += exp / opt;
            minGap = Math.min(minGap, opt / sdp);
            sumCoin += total(w) / 2 / opt; sumLocal += loc / opt; minLocal = Math.min(minLocal, loc / opt);
            sumBestPlane += bestPlane / opt;
            if (bestPlane == opt) planeHitsBest++;
            if (loc == opt) localHitsBest++;
        }
        check(minRatio >= alpha, "on every network the expected random-plane cut is at least 0.87856 of the best");
        System.out.printf("random: %d networks of %d nodes, each link present with probability 1/2 ; relaxation certified optimal on all ; expected random-plane cut / best cut: average %.4f, lowest %.4f ; best of 100 planes / best cut: average %.4f, equal to the best on %d ; best cut / relaxation: lowest %.4f ; coin flip (expected) / best: average %.4f ; local search from a coin flip / best: average %.4f, lowest %.4f, equal to the best on %d%n",
                graphs, n, sumRatio / graphs, minRatio, sumBestPlane / graphs, planeHitsBest, minGap, sumCoin / graphs, sumLocal / graphs, minLocal, localHitsBest);

        // ---- 4. a network of 400 nodes ------------------------------------------------------------------------------
        s32 = 2026;
        int big = 400;
        double[][] wb = randomGraph(big, 0.05);
        double[][] vb = relax(wb, rankFor(big));
        boolean cert = certified(wb, vb);
        check(cert, "the 400-node relaxation is certified optimal");
        double sdpB = sdpValue(wb, vb), boundB = dualBound(wb, vb), expB = expectedCut(wb, vb), bestB = 0;
        check(boundB - sdpB < 1e-4, "the dual bound matches the arrows' value");
        for (int t = 0; t < 100; t++) {
            boolean[] side = roundPlane(vb, randomDirection(vb[0].length));
            bestB = Math.max(bestB, localSearch(wb, side));
        }
        boolean[] coinB = new boolean[big];
        double bestCoinLocal = 0;
        for (int t = 0; t < 100; t++) {
            for (int i = 0; i < big; i++) coinB[i] = next32() < 0.5;
            bestCoinLocal = Math.max(bestCoinLocal, localSearch(wb, coinB));
        }
        check(bestB <= boundB && bestCoinLocal <= boundB, "no cut exceeds the dual's bound");
        System.out.printf("large: %d nodes, %.0f links (each pair linked with probability 0.05), arrows in %d dimensions ; relaxation %.2f ; the dual certificate proves no cut exceeds %.2f ; expected random-plane cut %.1f ; best of 100 planes, each improved by local search: %.0f, so at least %.1f%% of the best possible cut ; best of 100 coin flips with local search: %.0f%n",
                big, total(wb), vb[0].length, sdpB, boundB, expB, bestB, 100 * bestB / boundB, bestCoinLocal);

        // ---- 5. the Petersen graph, with the widget's planes ----------------------------------------------------------
        int[][] pe = {{0, 1}, {1, 2}, {2, 3}, {3, 4}, {4, 0}, {0, 5}, {1, 6}, {2, 7}, {3, 8}, {4, 9}, {5, 7}, {7, 9}, {9, 6}, {6, 8}, {8, 5}};
        double[][] wp = new double[10][10];
        for (int[] e : pe) wp[e[0]][e[1]] = wp[e[1]][e[0]] = 1;
        s32 = 1736;
        double[][] vp = relax(wp, 5);
        check(certified(wp, vp), "the Petersen relaxation is certified optimal");
        double sdpP = sdpValue(wp, vp), bestP = bestCut(wp);
        // the widget uses the arrows rounded to 4 decimals; so does everything below
        double[][] vr = new double[10][5];
        StringJoiner vj = new StringJoiner(" ");
        for (int i = 0; i < 10; i++) {
            StringJoiner one = new StringJoiner(",");
            for (int d = 0; d < 5; d++) { vr[i][d] = Math.round(vp[i][d] * 10000) / 10000.0; one.add(String.format("%.4f", vr[i][d])); }
            vj.add(one.toString());
        }
        double expP = expectedCut(wp, vr);
        s32 = 1995;
        StringJoiner tj = new StringJoiner(" ");
        double sum = 0, bestSoFar = 0;
        for (int t = 1; t <= 20; t++) {
            double c = cutOf(wp, roundPlane(vr, randomDirection(5)));
            sum += c; bestSoFar = Math.max(bestSoFar, c);
            tj.add(String.format("%.0f", c));
        }
        check(bestSoFar <= bestP, "no plane beats the best cut");
        System.out.printf("petersen: the Petersen graph (10 nodes, 15 links), arrows in 5 dimensions, start seed 1736 ; relaxation %.4f, certified ; best cut %.0f ; expected random-plane cut %.4f ; arrows rounded to 4 decimals: %s ; 20 random planes from seed 1995 (each a point in the cube [-1,1]^5 kept if inside the unit ball): %s ; average %.2f, best %.0f%n",
                sdpP, bestP, expP, vj, tj, sum / 20, bestSoFar);

        System.out.println("GoemansWilliamson: " + passed + " checks passed");
    }
}
