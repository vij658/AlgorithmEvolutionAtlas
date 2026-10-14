import java.util.*;

/**
 * Era 5, topic 9: Rosenblatt's perceptron (Cornell Aeronautical Laboratory, 1957-1958).
 *
 * HOW IT WORKS
 *   A perceptron looks at many inputs (the 400 photocells of the Mark I, say), multiplies each by a weight, adds them
 *   up with a bias, and answers yes if the total is positive, no if it is not. It learns from examples: when it
 *   answers wrongly, each weight is nudged in the direction that would have made the answer right (add the input
 *   for a missed yes, subtract it for a false yes), and when it answers rightly nothing changes. If some setting of
 *   the weights separates the yes examples from the no examples by a straight cut (a plane, in many dimensions), this
 *   rule finds such a setting after a limited number of mistakes; if none exists, it never settles.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Cards of 20 x 20 cells with a mark on the left or the right half, in random places, with speckle noise: how many
 *      cards the perceptron sees before it stops making mistakes, its score on new cards, and the weights it learned.
 *   2. The mistake bound: on random separable examples in 2 to 50 dimensions, the number of mistakes never exceeds
 *      (R / margin)^2.
 *   3. All 16 functions of two yes/no inputs: which can be learned.
 *   4. XOR: the weights never settle; give the perceptron one more input, x AND y, and it learns at once.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Perceptron.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Perceptron {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1958L;

    static long next() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return seed;
    }

    static int rnd(int n) { return (int) ((next() >>> 33) % n); }

    static double uniform() { return (next() >>> 11) / (double) (1L << 53); }

    static double gauss() { return Math.sqrt(-2 * Math.log(1 - uniform())) * Math.cos(2 * Math.PI * uniform()); }

    // ---- the perceptron ---------------------------------------------------------------------------------------------
    static final class Unit {
        final double[] w;
        double b;
        long mistakes;
        Unit(int n) { w = new double[n]; }
        boolean answer(double[] x) { double s = b; for (int i = 0; i < x.length; i++) s += w[i] * x[i]; return s > 0; }
        /** Show one example; learn if wrong; return true if it was right. */
        boolean learn(double[] x, boolean yes) {
            if (answer(x) == yes) return true;
            double d = yes ? 1 : -1;
            for (int i = 0; i < x.length; i++) w[i] += d * x[i];
            b += d;
            mistakes++;
            return false;
        }
    }

    // ---- 1. the cards -------------------------------------------------------------------------------------------------
    static final int N = 20;

    static double[] card(boolean left) {
        double[] x = new double[N * N];
        int r = 2 + rnd(N - 6), c = (left ? 1 : N / 2 + 1) + rnd(N / 2 - 5);
        for (int i = 0; i < 3; i++) for (int j = 0; j < 3; j++) x[(r + i) * N + c + j] = 1;
        for (int k = 0; k < 8; k++) x[rnd(N * N)] = 1;                 // specks of dirt anywhere
        return x;
    }

    public static void main(String[] args) {
        Unit u = new Unit(N * N);
        int seen = 0, run = 0, needRun = 200;
        while (run < needRun) {
            boolean left = rnd(2) == 0;
            if (u.learn(card(left), left)) run++; else run = 0;
            seen++;
            check(seen < 100000, "the cards are learned");
        }
        int lastMistakeAt = seen - needRun;
        int right = 0, test = 10000;
        for (int t = 0; t < test; t++) { boolean left = rnd(2) == 0; if (u.answer(card(left)) == left) right++; }
        check(right > test * 0.98, "new cards mostly right");
        StringBuilder map = new StringBuilder();
        double big = 0;
        for (double v : u.w) big = Math.max(big, Math.abs(v));
        for (int r = 0; r < N; r++) {
            if (r > 0) map.append('/');
            for (int c = 0; c < N; c++) { double v = u.w[r * N + c]; map.append(v > big / 4 ? '+' : v < -big / 4 ? '-' : '.'); }
        }
        int plusLeft = 0, minusRight = 0, plusCount = 0, minusCount = 0;
        for (int r = 0; r < N; r++) for (int c = 0; c < N; c++) {
            double v = u.w[r * N + c];
            if (v > big / 4) { plusCount++; if (c < N / 2) plusLeft++; }
            if (v < -big / 4) { minusCount++; if (c >= N / 2) minusRight++; }
        }
        check(plusLeft > 0.75 * plusCount && minusRight > 0.75 * minusCount, "strong positive weights mostly on the left, negative on the right");
        System.out.printf("cards: 20 x 20 cells, a 3 x 3 mark somewhere on the left or the right half, 8 specks of dirt ; the perceptron's last mistake came at card %d (%d mistakes in all), then %d right in a row ; on %,d new cards it was right %,d times (%.2f%%)%n",
                lastMistakeAt, u.mistakes, needRun, test, right, 100.0 * right / test);
        System.out.printf("weights: %s (row by row; + strongly for 'left', - strongly for 'right', . weak) ; %d of the %d strong + weights are on the left half, %d of the %d strong - weights on the right ; the rest were learned from specks of dirt%n",
                map, plusLeft, plusCount, minusRight, minusCount);

        // ---- 2. the mistake bound ----------------------------------------------------------------------------------------
        StringJoiner bj = new StringJoiner(" ; ");
        int trials = 0;
        for (int dim : new int[]{2, 5, 10, 50}) {
            long worstRatio100 = 0;
            long sumMistakes = 0;
            double sumBound = 0;
            for (int t = 0; t < 200; t++) {
                double[] true_w = new double[dim];
                double norm = 0;
                for (int i = 0; i < dim; i++) { true_w[i] = gauss(); norm += true_w[i] * true_w[i]; }
                norm = Math.sqrt(norm);
                for (int i = 0; i < dim; i++) true_w[i] /= norm;
                List<double[]> xs = new ArrayList<>();
                List<Boolean> ys = new ArrayList<>();
                double margin = 0.05, radius = 0;
                while (xs.size() < 400) {
                    double[] x = new double[dim];
                    for (int i = 0; i < dim; i++) x[i] = 2 * uniform() - 1;
                    double s = 0;
                    for (int i = 0; i < dim; i++) s += true_w[i] * x[i];
                    if (Math.abs(s) < margin) continue;                  // keep a gap of at least the margin
                    double r = 0;
                    for (double v : x) r += v * v;
                    radius = Math.max(radius, Math.sqrt(r));
                    xs.add(x);
                    ys.add(s > 0);
                }
                Unit p = new Unit(dim);
                p.b = 0;
                boolean clean = false;
                for (int epoch = 0; epoch < 100000 && !clean; epoch++) {
                    clean = true;
                    for (int i = 0; i < xs.size(); i++) {
                        // no bias here: the true cut passes through the origin
                        double s = 0;
                        for (int k = 0; k < dim; k++) s += p.w[k] * xs.get(i)[k];
                        boolean ans = s > 0;
                        if (ans != ys.get(i)) {
                            clean = false;
                            double d = ys.get(i) ? 1 : -1;
                            for (int k = 0; k < dim; k++) p.w[k] += d * xs.get(i)[k];
                            p.mistakes++;
                        }
                    }
                }
                check(clean, "separable data is learned");
                double bound = (radius / margin) * (radius / margin);
                check(p.mistakes <= bound, "mistakes within (R/margin)^2");
                sumMistakes += p.mistakes;
                sumBound += bound;
                worstRatio100 = Math.max(worstRatio100, Math.round(100 * p.mistakes / bound));
                trials++;
            }
            bj.add(String.format("%d dimensions: %.0f mistakes on average, bound %.0f", dim, sumMistakes / 200.0, sumBound / 200));
        }
        System.out.printf("bound: %d random problems, 400 points in a cube, a random cut through the centre, no point closer to it than 0.05 ; the perceptron always finished, and its mistakes never exceeded (R / 0.05)^2, R the largest distance of a point from the centre ; %s%n",
                trials, bj);

        // ---- 3. all functions of two inputs -----------------------------------------------------------------------------
        double[][] in = {{0, 0}, {0, 1}, {1, 0}, {1, 1}};
        List<String> learned = new ArrayList<>(), not = new ArrayList<>();
        // bit 3 is the answer for (0,0), bit 2 for (0,1), bit 1 for (1,0), bit 0 for (1,1)
        String[] names = {"FALSE", "AND", "x-AND-NOT-y", "x", "y-AND-NOT-x", "y", "XOR", "OR", "NOR", "XNOR", "NOT-y", "x-OR-NOT-y", "NOT-x", "y-OR-NOT-x", "NAND", "TRUE"};
        for (int f = 0; f < 16; f++) {
            Unit p = new Unit(2);
            boolean clean = false;
            for (int epoch = 0; epoch < 1000 && !clean; epoch++) {
                clean = true;
                for (int i = 0; i < 4; i++) if (!p.learn(in[i], (f >> (3 - i) & 1) == 1)) clean = false;
            }
            (clean ? learned : not).add(names[f]);
        }
        check(learned.size() == 14 && not.equals(List.of("XOR", "XNOR")), "14 of 16");
        System.out.printf("boolean: the 16 functions of two inputs x, y ; learned (a straight line separates the yes corners from the no corners): %d, %s ; never learned in 1,000 passes: %s%n",
                learned.size(), String.join(" ", learned), String.join(" ", not));

        // ---- 4. XOR, and a helping input ---------------------------------------------------------------------------------
        Unit xr = new Unit(2);
        boolean[] want = {false, true, true, false};
        int wrongLast = 0;
        Set<String> states = new LinkedHashSet<>();
        boolean cycled = false;
        int epochs = 0;
        for (int epoch = 0; epoch < 1000; epoch++) {
            wrongLast = 0;
            for (int i = 0; i < 4; i++) if (!xr.learn(in[i], want[i])) wrongLast++;
            String st = Arrays.toString(xr.w) + xr.b;
            epochs++;
            if (!states.add(st)) { cycled = true; break; }
        }
        check(cycled && wrongLast > 0, "XOR: the weights come back to an earlier setting, still wrong");
        Unit x3 = new Unit(3);
        int passes = 0;
        boolean clean = false;
        while (!clean) {
            clean = true;
            for (int i = 0; i < 4; i++) if (!x3.learn(new double[]{in[i][0], in[i][1], in[i][0] * in[i][1]}, want[i])) clean = false;
            passes++;
        }
        check(passes < 20, "with x AND y as a third input XOR is learned");
        System.out.printf("xor: x XOR y is yes for (0,1) and (1,0), no for (0,0) and (1,1) ; no straight line separates them, and after %d passes through the four examples the weights were back at a setting they had held before, still wrong on %d ; with x AND y as a third input, learned in %d passes: weights %.0f, %.0f, %.0f, bias %.0f%n",
                epochs, wrongLast, passes, x3.w[0], x3.w[1], x3.w[2], x3.b);

        System.out.println("Perceptron: " + passed + " checks passed");
    }
}
