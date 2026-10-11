import java.util.*;

/**
 * Era 2, topic 2: Ptolemy's table of chords (Almagest, Book I, Alexandria, c. 150 CE).
 *
 * HOW IT WORKS
 *   Astronomy needs the chord of every angle: the straight line across a circle between the ends of an arc. On a circle
 *   of radius 60 (diameter 120, chosen for base-60 arithmetic), the chord of an arc a is 120 sin(a/2), so a table of
 *   chords is a table of sines in disguise. Nobody can measure every chord, so the table is grown from a seed:
 *     seed      chords known exactly from regular polygons: 36 (decagon), 60 (hexagon), 72 (pentagon), 90 (square),
 *               120 degrees (triangle);
 *     rules     the supplement, crd(180 - a) = sqrt(120^2 - crd(a)^2), from the right angle in a semicircle;
 *               halving, crd(a/2)^2 = 60 (120 - crd(180 - a));
 *               sums and differences, from Ptolemy's theorem on a quadrilateral in a circle (the diagonals multiplied
 *               equal the two pairs of opposite sides multiplied and added);
 *     squeeze   the chord of 1 degree cannot be reached by halving and differences from the seed, so it is pinned
 *               between the values that 3/4 and 1 1/2 degrees give;
 *     fill      every half degree from 1/2 to 180 by the sum rule, each entry rounded to seconds (sixtieths of
 *               sixtieths), with a column of increments for interpolating between entries.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Checks Ptolemy's theorem on 20,000 random quadrilaterals in a circle.
 *   2. Builds the seed chords and derives 12, 6, 3, 1 1/2 and 3/4 degrees by Ptolemy's route, rounding to seconds at
 *      every step as a hand computer would, then squeezes the chord of 1 degree and halves it to 1/2 degree.
 *   3. Fills the whole table of 360 entries by adding half a degree at a time, and compares every entry with the true
 *      chord, rounded to the second.
 *   4. Measures linear interpolation between half-degree entries at every minute of arc, against the rounding error.
 *   5. Recovers Ptolemy's pi (3;8,30) and square root of 3 from the chords.
 *   6. Full circle: computes sin(x) the way the GNU C library does for most arguments, from a table of sines and
 *      cosines plus the sum rule, and compares it with Java's StrictMath.sin, and with half-degree linear interpolation.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java PtolemyChords.java
 *   Expected output: expected-output.txt in this folder.
 */
public class PtolemyChords {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final double D = 120;                         // the diameter, in parts

    /** The true chord of an arc of a degrees: 120 sin(a/2). */
    static double crd(double a) { return D * Math.sin(Math.toRadians(a) / 2); }

    /** Round to seconds, as the table does: the nearest multiple of 1/3600 of a part. */
    static double sec(double v) { return Math.round(v * 3600) / 3600.0; }

    /** Round to thirds, one place more than the table, for working on the way to it. */
    static double third(double v) { return Math.round(v * 216000) / 216000.0; }

    /** Base-60 with a semicolon after the whole parts: 37;4,55. places = number of sexagesimal places. */
    static String sexa(double v, int places) {
        long scale = 1;
        for (int i = 0; i < places; i++) scale *= 60;
        long n = Math.round(Math.abs(v) * scale);
        long[] digits = new long[places];
        for (int i = places - 1; i >= 0; i--) { digits[i] = n % 60; n /= 60; }
        StringBuilder s = new StringBuilder(v < 0 ? "-" : "").append(n).append(';');
        for (int i = 0; i < places; i++) s.append(i == 0 ? "" : ",").append(digits[i]);
        return s.toString();
    }

    // the rules, applied to rounded table values ----------------------------------------------------------------------
    static double supplement(double c) { return Math.sqrt(D * D - c * c); }

    static double half(double cSupp) { return Math.sqrt(D / 2 * (D - cSupp)); }       // from crd(180 - a) to crd(a/2)

    /** crd(a - b) from crd a, crd b and their supplements: Ptolemy's theorem with one side a diameter. */
    static double difference(double ca, double cb) { return (ca * supplement(cb) - cb * supplement(ca)) / D; }

    /** crd(a + b): first the supplement of the sum, then back. */
    static double sum(double ca, double cb) { return supplement((supplement(ca) * supplement(cb) - ca * cb) / D); }

    static int secondsOff(double v, double truth) { return (int) Math.round(Math.abs(v - truth) * 3600); }

    public static void main(String[] args) {
        // ---- Ptolemy's theorem -----------------------------------------------------------------------------------
        Random r = new Random(150);
        double worst = 0;
        for (int t = 0; t < 20_000; t++) {
            double[] ang = new double[4];
            for (int i = 0; i < 4; i++) ang[i] = r.nextDouble() * 2 * Math.PI;
            Arrays.sort(ang);                              // A, B, C, D in order round the circle
            double[][] p = new double[4][];
            for (int i = 0; i < 4; i++) p[i] = new double[]{60 * Math.cos(ang[i]), 60 * Math.sin(ang[i])};
            double ab = dist(p[0], p[1]), bc = dist(p[1], p[2]), cd = dist(p[2], p[3]), da = dist(p[3], p[0]);
            double ac = dist(p[0], p[2]), bd = dist(p[1], p[3]);
            double gap = Math.abs(ac * bd - (ab * cd + bc * da)) / (ac * bd);
            worst = Math.max(worst, gap);
            check(gap < 1e-9, "Ptolemy's theorem: AC x BD = AB x CD + BC x DA");
        }
        System.out.printf("theorem: 20000 random quadrilaterals in a circle, largest relative gap %.1e%n", worst);

        // ---- the seed --------------------------------------------------------------------------------------------
        Map<String, Double> table = new LinkedHashMap<>();
        double c36 = sec(30 * (Math.sqrt(5) - 1));         // side of the decagon in a circle of radius 60
        double c60 = 60;                                   // side of the hexagon: the radius
        double c72 = sec(Math.sqrt(60 * 60 + c36 * c36));  // pentagon: its side squared = hexagon's + decagon's (Euclid XIII.10)
        double c90 = sec(Math.sqrt(2 * 60 * 60));          // square
        double c120 = sec(Math.sqrt(3 * 60 * 60));         // equilateral triangle
        double[][] seeds = {{36, c36}, {60, c60}, {72, c72}, {90, c90}, {120, c120}};
        for (double[] s : seeds) {
            check(secondsOff(s[1], crd(s[0])) == 0, "the seed chord of " + s[0] + " degrees is right to the second");
            System.out.printf("seed %s: %s ; true %s%n", fmtArc(s[0]), sexa(s[1], 2), sexa(crd(s[0]), 3));
        }

        // ---- Ptolemy's route to small arcs ------------------------------------------------------------------------
        double c12 = third(difference(c72, c60));          // 72 - 60, worked to thirds
        System.out.printf("derive 12: %s (difference of 72 and 60) ; to the second %s ; true %s%n", sexa(c12, 3), sexa(sec(c12), 2), sexa(crd(12), 3));
        double c = c12, a = 12;
        double c3q = 0, c1h = 0;
        while (a > 0.75) {
            c = third(half(supplement(c)));
            a /= 2;
            System.out.printf("derive %s: %s (half of %s) ; to the second %s ; true %s%n", fmtArc(a), sexa(c, 3), fmtArc(a * 2), sexa(sec(c), 2), sexa(crd(a), 3));
            if (a == 1.5) c1h = c;
            if (a == 0.75) c3q = c;
        }
        for (double[] x : new double[][]{{12, c12}, {1.5, c1h}, {0.75, c3q}})
            check(sec(x[1]) == sec(crd(x[0])), "derived chord right to the second at " + x[0]);
        check(sexa(sec(c1h), 2).equals("1;34,15"), "1 1/2 degrees: 1;34,15, as Strick reports");
        // the squeeze: a chord grows more slowly than its arc, so crd 1 < 4/3 crd 3/4 and crd 1 > 2/3 crd 1 1/2
        double lo = 2.0 / 3 * c1h, hi = 4.0 / 3 * c3q;
        check(lo < crd(1) && crd(1) < hi, "the true chord of 1 degree lies in the squeeze");
        double c1 = sec((lo + hi) / 2);
        check(sec(lo) == c1 && Math.abs(hi - c1) < 1.0 / 3600, "both bounds give the same chord to the second");
        System.out.printf("squeeze 1: between %s and %s, so %s ; true %s%n", sexa(lo, 3), sexa(hi, 3), sexa(c1, 2), sexa(crd(1), 3));
        double cHalf = sec(half(supplement(c1)));
        check(sexa(cHalf, 2).equals("0;31,25"), "half a degree: 0;31,25, as in Ptolemy's table");
        System.out.printf("derive 1/2: %s (half of 1) ; true %s%n", sexa(cHalf, 2), sexa(crd(0.5), 3));

        // ---- fill the table: add half a degree at a time ------------------------------------------------------------
        double[] built = new double[361];                  // built[k] = chord of k/2 degrees
        built[1] = cHalf;
        built[2] = c1;
        for (int k = 3; k <= 360; k++) built[k] = sec(sum(built[k - 1], cHalf));
        int exact = 0, off1 = 0, maxOff = 0, maxAt = 0;
        for (int k = 1; k <= 360; k++) {
            int off = secondsOff(built[k], sec(crd(k / 2.0)));
            if (off == 0) exact++;
            if (off == 1) off1++;
            if (off > maxOff) { maxOff = off; maxAt = k; }
        }
        System.out.printf("chain: 360 entries by adding 1/2 degree each time: %d right to the second, %d one second off, worst %d seconds off at %s%n",
                exact, off1, maxOff, fmtArc(maxAt / 2.0));
        // anchored: restart the sums from every seed and derived chord, the way the rules allow
        double[] anchored = new double[361];
        Map<Integer, Double> anchors = new TreeMap<>(Map.of(1, cHalf, 2, c1, 3, sec(c1h), 24, sec(c12), 72, c36, 120, c60, 144, c72, 180, c90, 240, c120));
        for (int k = 1; k <= 360; k++) {
            if (anchors.containsKey(k)) { anchored[k] = anchors.get(k); continue; }
            anchored[k] = sec(sum(anchored[k - 1], cHalf));
        }
        int aExact = 0, aMax = 0;
        for (int k = 1; k <= 360; k++) {
            int off = secondsOff(anchored[k], sec(crd(k / 2.0)));
            if (off == 0) aExact++;
            aMax = Math.max(aMax, off);
        }
        check(aExact > exact, "restarting from the exact chords keeps more entries right");
        System.out.printf("anchored: restarting the sums at each known chord: %d of 360 right to the second, worst %d seconds off%n", aExact, aMax);
        // a few rows of the table: arc, chord, increment per minute of arc (1/30 of the step to the next entry)
        for (int k : new int[]{1, 2, 3, 60, 120, 240, 359, 360}) {
            double inc = k < 360 ? (sec(crd((k + 1) / 2.0)) - sec(crd(k / 2.0))) / 30 : 0;
            System.out.printf("row %s: chord %s ; increment per minute %s%n", fmtArc(k / 2.0), sexa(sec(crd(k / 2.0)), 2), sexa(inc, 3));
        }

        // ---- interpolating between entries ---------------------------------------------------------------------
        double worstInterp = 0, worstAt = 0;
        for (int m = 0; m < 180 * 60; m++) {               // every minute of arc
            double arc = m / 60.0;
            int k = (int) Math.floor(arc * 2);
            double a0 = k / 2.0;
            double y0 = k == 0 ? 0 : sec(crd(a0)), y1 = sec(crd(a0 + 0.5));
            double y = y0 + (y1 - y0) * (arc - a0) / 0.5;
            double e = Math.abs(y - crd(arc));
            if (e > worstInterp) { worstInterp = e; worstAt = arc; }
        }
        double bound = Math.pow(Math.toRadians(0.5), 2) / 8 * (D / 4);
        check(worstInterp < bound + 1.0 / 7200, "interpolation error within h^2/8 max|f''| plus the rounding");
        System.out.printf("interpolate: every minute of arc from 0 to 180 degrees: worst error %.2f seconds at %s ; curvature alone allows %.2f seconds, rounding half a second%n",
                worstInterp * 3600, fmtArcMin(worstAt), bound * 3600);

        // ---- pi and the root of 3 ------------------------------------------------------------------------------------
        double piP = 360 * c1 / D;                         // a 360-sided polygon, perimeter over diameter
        check(sexa(piP, 2).equals("3;8,30"), "Ptolemy's pi: 3;8,30");
        check(Math.abs(piP - 377.0 / 120) < 1e-12, "3;8,30 is 377/120");
        double r3 = c120 / 60;
        System.out.printf("pi: 360 x %s / 120 = %s = 377/120 = %.6f (true %.6f)%n", sexa(c1, 2), sexa(piP, 2), piP, Math.PI);
        System.out.printf("root3: %s / 60 = %s = %.7f (true %.7f)%n", sexa(c120, 2), sexa(r3, 3), r3, Math.sqrt(3));

        // ---- full circle: a table and the sum rule, as in the GNU C library -----------------------------------------
        int N = 128;                                       // table points every 1/128 of a radian
        double[] ts = new double[N * 2 + 1], tc = new double[N * 2 + 1];
        for (int i = 0; i <= 2 * N; i++) { ts[i] = StrictMath.sin(i / (double) N); tc[i] = StrictMath.cos(i / (double) N); }
        // half-degree table with linear interpolation, in double precision
        double[] hd = new double[182];
        for (int i = 0; i < 182; i++) hd[i] = StrictMath.sin(Math.toRadians(i / 2.0));
        Random r2 = new Random(1424);
        double worstUlp = 0, worstLin = 0;
        int samples = 1_000_000;
        for (int t = 0; t < samples; t++) {
            double x = r2.nextDouble() * Math.PI / 2;
            int i = (int) Math.round(x * N);
            double x0 = i / (double) N, dx = x - x0;       // |dx| <= 1/256
            double d2 = dx * dx;
            double sdx = dx * (1 - d2 / 6 * (1 - d2 / 20 * (1 - d2 / 42)));       // short series for small dx
            double cdx = 1 - d2 / 2 * (1 - d2 / 12 * (1 - d2 / 30 * (1 - d2 / 56)));
            double s = ts[i] * cdx + tc[i] * sdx;          // sin(x0 + dx) = sin x0 cos dx + cos x0 sin dx
            double truth = StrictMath.sin(x);
            worstUlp = Math.max(worstUlp, Math.abs(s - truth) / Math.ulp(truth));
            double deg = Math.toDegrees(x) * 2;
            int k = (int) Math.floor(deg);
            double lin = hd[k] + (hd[k + 1] - hd[k]) * (deg - k);
            worstLin = Math.max(worstLin, Math.abs(lin - truth));
        }
        check(worstUlp <= 4, "table plus sum rule: within a few units in the last place");
        check(worstLin < 1e-5, "half-degree interpolation: about five correct decimals");
        System.out.printf("library: %d random angles: table of %d sines and cosines plus the sum rule, worst %.2f units in the last place ; half-degree table with interpolation, worst error %.1e%n",
                samples, 2 * N + 1, worstUlp, worstLin);

        System.out.printf("PtolemyChords: %d checks passed%n", passed);
    }

    static double dist(double[] p, double[] q) { return Math.hypot(p[0] - q[0], p[1] - q[1]); }

    static String fmtArc(double a) {
        if (a == Math.floor(a)) return String.valueOf((long) a);
        long w = (long) Math.floor(a);
        double f = a - w;
        String frac = Math.abs(f - 0.5) < 1e-9 ? "1/2" : Math.abs(f - 0.75) < 1e-9 ? "3/4" : Math.abs(f - 0.25) < 1e-9 ? "1/4" : String.valueOf(f);
        return (w == 0 ? "" : w + " ") + frac;
    }

    static String fmtArcMin(double a) {
        long m = Math.round(a * 60);
        return (m / 60) + " degrees " + (m % 60) + " minutes";
    }
}
