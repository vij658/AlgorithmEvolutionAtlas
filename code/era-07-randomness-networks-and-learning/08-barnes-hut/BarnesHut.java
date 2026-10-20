import java.util.*;

/**
 * Era 7, topic 8: the Barnes-Hut tree code (Josh Barnes and Piet Hut, Nature, December 1986).
 *
 * HOW IT WORKS
 *   To move N stars under gravity you need the pull of every star on every other: N(N - 1) terms, a billion for
 *   N = 30,000, at every time step. Barnes and Hut put the stars in a tree of cubes: the whole box, split into 8
 *   smaller cubes, each split again, until every cube holds at most one star. Each cube remembers its total mass and
 *   centre of mass. To find the pull on one star, walk down the tree from the top: a cube that looks small from the
 *   star (its width s divided by its distance d is below a chosen angle theta) is treated as one heavy point at its
 *   centre of mass; a cube that looks big is opened and its children are looked at instead. A star then feels about
 *   log N cubes instead of N stars, so a step costs about N log N. Smaller theta opens more cubes: slower, more
 *   accurate; theta = 0 opens everything and gives back the exact sum.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Builds the tree for a cluster of stars (a Plummer sphere) and checks that theta = 0 gives the exact forces.
 *   2. Counts interactions for N = 1,000 to 100,000 stars: direct sum against the tree.
 *   3. Measures the error of the tree's forces against the exact ones for several values of theta.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java BarnesHut.java
 *   Expected output: expected-output.txt in this folder.
 */
public class BarnesHut {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1986L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static final double SOFT2 = 1e-6;     // softening, so two stars very close together do not give infinite forces

    /** n stars of equal mass 1/n in a Plummer sphere (a standard model of a star cluster), radius cut at 10. */
    static double[][] plummer(int n) {
        double[][] p = new double[n][3];
        for (double[] q : p) {
            double r;
            do { r = 1 / Math.sqrt(Math.pow(uniform(), -2.0 / 3) - 1); } while (r > 10);
            double z = 2 * uniform() - 1, phi = 2 * Math.PI * uniform(), s = Math.sqrt(1 - z * z);
            q[0] = r * s * Math.cos(phi); q[1] = r * s * Math.sin(phi); q[2] = r * z;
        }
        return p;
    }

    // ---- the tree of cubes -------------------------------------------------------------------------------------------
    static class Cell {
        final double cx, cy, cz, half;      // centre and half-width of the cube
        double mass, mx, my, mz;            // total mass, and mass-weighted position (centre of mass once divided)
        int body = -1;                      // the one star in a leaf
        Cell[] child;
        Cell(double cx, double cy, double cz, double half) { this.cx = cx; this.cy = cy; this.cz = cz; this.half = half; }
    }

    static double[][] pos;
    static double m;
    static int cells, depth;

    static void insert(Cell c, int b, int d) {
        depth = Math.max(depth, d);
        if (c.child == null && c.body < 0 && c.mass == 0) { c.body = b; c.mass = m; c.mx = m * pos[b][0]; c.my = m * pos[b][1]; c.mz = m * pos[b][2]; return; }
        if (c.child == null) {                              // a leaf with one star: split it
            c.child = new Cell[8];
            int old = c.body;
            c.body = -1;
            place(c, old, d);
        }
        place(c, b, d);
        c.mass += m; c.mx += m * pos[b][0]; c.my += m * pos[b][1]; c.mz += m * pos[b][2];
    }

    static void place(Cell c, int b, int d) {
        int k = (pos[b][0] > c.cx ? 1 : 0) | (pos[b][1] > c.cy ? 2 : 0) | (pos[b][2] > c.cz ? 4 : 0);
        if (c.child[k] == null) {
            double h = c.half / 2;
            c.child[k] = new Cell(c.cx + ((k & 1) != 0 ? h : -h), c.cy + ((k & 2) != 0 ? h : -h), c.cz + ((k & 4) != 0 ? h : -h), h);
            cells++;
        }
        insert(c.child[k], b, d + 1);
    }

    static Cell build(double[][] p) {
        pos = p;
        m = 1.0 / p.length;
        double lim = 0;
        for (double[] q : p) for (double x : q) lim = Math.max(lim, Math.abs(x));
        Cell root = new Cell(0, 0, 0, lim * 1.0001);
        cells = 1; depth = 0;
        for (int b = 0; b < p.length; b++) {
            if (root.mass == 0 && root.body < 0) { insert(root, b, 0); continue; }
            insert(root, b, 0);
        }
        return root;
    }

    static long interactions;

    /** The acceleration on star b from the tree, opening cubes with s / d >= theta. */
    static void force(Cell c, int b, double theta, double[] acc) {
        if (c.mass == 0 || c.body == b) return;
        double gx = c.mx / c.mass, gy = c.my / c.mass, gz = c.mz / c.mass;
        double dx = gx - pos[b][0], dy = gy - pos[b][1], dz = gz - pos[b][2];
        double d2 = dx * dx + dy * dy + dz * dz;
        if (c.child == null || 4 * c.half * c.half < theta * theta * d2) {     // width^2 = 4 half^2; (s/d)^2 < theta^2
            if (c.child != null || c.body != b) {
                double inv = 1 / Math.sqrt(d2 + SOFT2);
                double f = c.mass * inv * inv * inv;
                acc[0] += f * dx; acc[1] += f * dy; acc[2] += f * dz;
                interactions++;
            }
            return;
        }
        for (Cell ch : c.child) if (ch != null) force(ch, b, theta, acc);
    }

    static double[] direct(int b) {
        double[] a = new double[3];
        for (int j = 0; j < pos.length; j++) {
            if (j == b) continue;
            double dx = pos[j][0] - pos[b][0], dy = pos[j][1] - pos[b][1], dz = pos[j][2] - pos[b][2];
            double inv = 1 / Math.sqrt(dx * dx + dy * dy + dz * dz + SOFT2);
            double f = m * inv * inv * inv;
            a[0] += f * dx; a[1] += f * dy; a[2] += f * dz;
        }
        return a;
    }

    static double norm(double[] a) { return Math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2]); }

    public static void main(String[] args) {
        // ---- 1. the tree, and theta = 0 ------------------------------------------------------------------------------
        int n = 2000;
        double[][] p = plummer(n);
        Cell root = build(p);
        check(Math.abs(root.mass - 1) < 1e-12, "the root holds all the mass");
        double worst = 0;
        interactions = 0;
        for (int b = 0; b < n; b++) {
            double[] a = new double[3];
            force(root, b, 0.0, a);
            double[] e = direct(b);
            double rel = Math.hypot(Math.hypot(a[0] - e[0], a[1] - e[1]), a[2] - e[2]) / norm(e);
            worst = Math.max(worst, rel);
            check(rel < 1e-10, "theta = 0 gives the exact force");
        }
        check(interactions == (long) n * (n - 1), "theta = 0 means every star meets every other");
        System.out.printf("tree: %,d stars in a Plummer sphere ; the tree has %,d cubes and is %d levels deep ; with theta = 0 every cube is opened, the walk meets every other star (%,d interactions = N(N-1)) and the forces equal the direct sum to a relative difference of %.1e%n",
                n, cells, depth, interactions, worst);

        // ---- 2. interactions as N grows ------------------------------------------------------------------------------
        StringJoiner sj = new StringJoiner(" ; ");
        double prevPer = 0;
        for (int N : new int[]{1_000, 3_000, 10_000, 30_000, 100_000}) {
            seed = 2024 + N;
            double[][] q = plummer(N);
            Cell r = build(q);
            interactions = 0;
            for (int b = 0; b < N; b++) force(r, b, 0.5, new double[3]);
            double per = (double) interactions / N;
            check(per > prevPer, "a bigger cluster needs more interactions per star");
            check(per < 0.6 * (N - 1) || N <= 1_000, "but far fewer than N - 1");
            prevPer = per;
            sj.add(String.format("N=%,d: direct %,d (%,d per star), tree %,d (%,.0f per star), %.0f times fewer",
                    N, (long) N * (N - 1), N - 1, interactions, per, (double) N * (N - 1) / interactions));
        }
        System.out.printf("scaling: interactions needed to find the force on every star, theta = 0.5 ; %s%n", sj);

        // ---- 3. accuracy against theta ------------------------------------------------------------------------------
        n = 10_000;
        seed = 324_446;
        p = plummer(n);
        root = build(p);
        double[][] exact = new double[n][];
        for (int b = 0; b < n; b++) exact[b] = direct(b);
        StringJoiner aj = new StringJoiner(" ; ");
        double prevMedian = -1;
        long prevInter = Long.MAX_VALUE;
        for (double theta : new double[]{0.2, 0.3, 0.5, 0.7, 1.0}) {
            double[] err = new double[n];
            interactions = 0;
            for (int b = 0; b < n; b++) {
                double[] a = new double[3];
                force(root, b, theta, a);
                double[] e = exact[b];
                err[b] = Math.hypot(Math.hypot(a[0] - e[0], a[1] - e[1]), a[2] - e[2]) / norm(e);
            }
            Arrays.sort(err);
            double median = err[n / 2], p99 = err[(int) (0.99 * n)];
            check(median > prevMedian, "a larger theta is less accurate");
            check(interactions < prevInter, "and needs fewer interactions");
            prevMedian = median;
            prevInter = interactions;
            aj.add(String.format("theta %.1f: %,.0f interactions per star, median error %.4f%%, 99th percentile %.3f%%", theta, (double) interactions / n, 100 * median, 100 * p99));
        }
        System.out.printf("accuracy: %,d stars, the tree's force on every star against the exact sum (%,d per star) ; %s%n", n, n - 1, aj);

        System.out.println("BarnesHut: " + passed + " checks passed");
    }
}
