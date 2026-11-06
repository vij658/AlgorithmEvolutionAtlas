import java.util.*;

/**
 * Entry 102 of the principles catalog (Part 6): Backpropagation (reverse-mode automatic differentiation)
 * and gradient descent
 *
 * HOW IT WORKS
 *   Every number computed is a node that remembers which nodes it came from and how to pass a gradient back to
 *   them (the chain rule, one operation at a time). To get the derivative of the output with respect to every
 *   input, sort the nodes so each comes after the nodes it depends on (entry 36, topological sort), set the
 *   output's gradient to 1, and walk the list backwards, each node adding its share into its parents. When a node
 *   is used twice its gradient is the SUM of both uses, so gradients are accumulated with +=, never assigned.
 *   One backward pass costs a small constant times one forward pass, however many inputs there are; finite
 *   differences need two forward passes per input. That gap is why networks with billions of weights can train.
 *   Gradient descent then moves every weight a small step against its gradient: w <- w - lr * dLoss/dw.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Backpropagation.java
 *   Expected: the output in expected-output.txt, ending "Backpropagation: 1515 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class Backpropagation {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    static long nodesCreated = 0, backwardSteps = 0;
    /** Set to false to see the classic bug: assigning gradients instead of adding them. */
    static boolean accumulate = true;

    static final class Value {
        double data, grad;
        final Value[] parents;
        Runnable backward = () -> {};

        Value(double data, Value... parents) {
            this.data = data;
            this.parents = parents;
            if (parents.length > 0) nodesCreated++;
        }
    }

    static void addGrad(Value v, double delta) { v.grad = accumulate ? v.grad + delta : delta; }

    static Value add(Value a, Value b) {
        Value out = new Value(a.data + b.data, a, b);
        out.backward = () -> { addGrad(a, out.grad); addGrad(b, out.grad); };
        return out;
    }

    static Value sub(Value a, Value b) {
        Value out = new Value(a.data - b.data, a, b);
        out.backward = () -> { addGrad(a, out.grad); addGrad(b, -out.grad); };
        return out;
    }

    static Value mul(Value a, Value b) {
        Value out = new Value(a.data * b.data, a, b);
        out.backward = () -> { addGrad(a, b.data * out.grad); addGrad(b, a.data * out.grad); };
        return out;
    }

    static Value tanh(Value a) {
        double t = Math.tanh(a.data);
        Value out = new Value(t, a);
        out.backward = () -> addGrad(a, (1 - t * t) * out.grad);
        return out;
    }

    static Value exp(Value a) {
        double e = Math.exp(a.data);
        Value out = new Value(e, a);
        out.backward = () -> addGrad(a, e * out.grad);
        return out;
    }

    static Value square(Value a) {
        Value out = new Value(a.data * a.data, a);
        out.backward = () -> addGrad(a, 2 * a.data * out.grad);
        return out;
    }

    /** Topological order (entry 36): every node after the nodes it was computed from. Iterative DFS. */
    static List<Value> topologicalOrder(Value root) {
        List<Value> order = new ArrayList<>();
        Set<Value> seen = Collections.newSetFromMap(new IdentityHashMap<>());
        Deque<Value> stack = new ArrayDeque<>();
        Deque<Integer> next = new ArrayDeque<>();
        stack.push(root); next.push(0); seen.add(root);
        while (!stack.isEmpty()) {
            Value v = stack.peek();
            int i = next.pop();
            if (i < v.parents.length) {
                next.push(i + 1);
                Value p = v.parents[i];
                if (seen.add(p)) { stack.push(p); next.push(0); }
            } else {
                stack.pop();
                order.add(v);
            }
        }
        return order;
    }

    /** Reverse mode: seed the output with gradient 1 and apply the chain rule from the output back. */
    static void backpropagate(Value root) {
        List<Value> order = topologicalOrder(root);
        root.grad = 1;
        for (int i = order.size() - 1; i >= 0; i--) { order.get(i).backward.run(); backwardSteps++; }
    }

    // ----------------------------------------------------------------------------------------------------
    // A tiny neural network: 2 inputs, one hidden layer of tanh units, one tanh output
    // ----------------------------------------------------------------------------------------------------
    static final class Mlp {
        final Value[][] w1; final Value[] b1, w2; final Value b2;
        final List<Value> params = new ArrayList<>();

        Mlp(int inputs, int hidden, Random rnd) {
            w1 = new Value[hidden][inputs]; b1 = new Value[hidden]; w2 = new Value[hidden];
            for (int h = 0; h < hidden; h++) {
                for (int i = 0; i < inputs; i++) params.add(w1[h][i] = new Value(rnd.nextDouble() * 2 - 1));
                params.add(b1[h] = new Value(rnd.nextDouble() * 2 - 1));
                params.add(w2[h] = new Value(rnd.nextDouble() * 2 - 1));
            }
            params.add(b2 = new Value(rnd.nextDouble() * 2 - 1));
        }

        Value forward(double[] x) {
            Value out = b2;
            for (int h = 0; h < w1.length; h++) {
                Value s = b1[h];
                for (int i = 0; i < x.length; i++) s = add(s, mul(w1[h][i], new Value(x[i])));
                out = add(out, mul(w2[h], tanh(s)));
            }
            return tanh(out);
        }
    }

    static final double[][] XOR_X = {{0, 0}, {0, 1}, {1, 0}, {1, 1}};
    static final double[] XOR_Y = {-1, 1, 1, -1};

    static Value xorLoss(Mlp net) {
        Value loss = new Value(0);
        for (int k = 0; k < 4; k++) loss = add(loss, square(sub(net.forward(XOR_X[k]), new Value(XOR_Y[k]))));
        return loss;
    }

    /** Full-batch gradient descent. zeroGrad = false reproduces the "forgot to reset gradients" bug. */
    static double[] train(long seed, int steps, double lr, boolean zeroGrad, int[] report) {
        Mlp net = new Mlp(2, 8, new Random(seed));
        double[] losses = new double[report.length];
        int r = 0;
        for (int step = 0; step <= steps; step++) {
            if (zeroGrad) for (Value p : net.params) p.grad = 0;
            Value loss = xorLoss(net);
            if (r < report.length && report[r] == step) losses[r++] = loss.data;
            if (step == steps) break;
            backpropagate(loss);
            for (Value p : net.params) p.data -= lr * p.grad;
        }
        return losses;
    }

    // ----------------------------------------------------------------------------------------------------
    // Random expression programs, for comparing backpropagation with finite differences
    // ----------------------------------------------------------------------------------------------------
    record Instr(int op, int a, int b) {}

    static List<Instr> randomProgram(Random rnd, int inputs, int length) {
        List<Instr> prog = new ArrayList<>();
        for (int k = 0; k < length; k++) {
            int pool = inputs + k;
            prog.add(new Instr(rnd.nextInt(6), rnd.nextInt(pool), rnd.nextInt(pool)));
        }
        return prog;
    }

    static Value runProgram(List<Instr> prog, Value[] inputs) {
        List<Value> pool = new ArrayList<>(Arrays.asList(inputs));
        for (Instr in : prog) {
            Value a = pool.get(in.a()), b = pool.get(in.b());
            pool.add(switch (in.op()) {
                case 0 -> add(a, b);
                case 1 -> sub(a, b);
                case 2 -> mul(tanh(a), b);
                case 3 -> tanh(a);
                case 4 -> exp(tanh(a));
                default -> square(tanh(a));
            });
        }
        return pool.get(pool.size() - 1);
    }

    static double evalProgram(List<Instr> prog, double[] x) {
        Value[] in = new Value[x.length];
        for (int i = 0; i < x.length; i++) in[i] = new Value(x[i]);
        return runProgram(prog, in).data;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java Backpropagation.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // Known answer: f = a*b + c at a = 2, b = -3, c = 10.
        Value a = new Value(2), b = new Value(-3), c = new Value(10);
        Value fv = add(mul(a, b), c);
        backpropagate(fv);
        check(fv.data == 4 && a.grad == -3 && b.grad == 2 && c.grad == 1, "f = a*b + c");
        System.out.println(f("f = a*b + c at (2, -3, 10): f = %.0f, df/da = %.0f, df/db = %.0f, df/dc = %.0f",
                fv.data, a.grad, b.grad, c.grad));

        // A node used twice: d(x*x)/dx = 2x. Assigning instead of adding gives x.
        Value x = new Value(3);
        backpropagate(mul(x, x));
        double right = x.grad;
        accumulate = false;
        Value y = new Value(3);
        backpropagate(mul(y, y));
        double wrong = y.grad;
        accumulate = true;
        check(right == 6 && wrong == 3, "gradients of a reused node must be added");
        System.out.println(f("d(x*x)/dx at x = 3: %.0f with +=, %.0f if gradients are assigned instead of added", right, wrong));

        // 500 random programs: backpropagation against central finite differences.
        double worst = 0;
        for (int t = 0; t < 500; t++) {
            int n = 3;
            List<Instr> prog = randomProgram(rnd, n, 4 + rnd.nextInt(12));
            double[] xs = new double[n];
            Value[] in = new Value[n];
            for (int i = 0; i < n; i++) in[i] = new Value(xs[i] = rnd.nextDouble() * 2 - 1);
            Value out = runProgram(prog, in);
            backpropagate(out);
            for (int i = 0; i < n; i++) {
                double h = 1e-6;
                double[] up = xs.clone(), dn = xs.clone();
                up[i] += h; dn[i] -= h;
                double fd = (evalProgram(prog, up) - evalProgram(prog, dn)) / (2 * h);
                double rel = Math.abs(fd - in[i].grad) / (1 + Math.abs(in[i].grad));
                worst = Math.max(worst, rel);
                check(rel < 1e-6, "backpropagation matches finite differences");
            }
        }
        System.out.println(f("500 random expression graphs: backpropagation matches finite differences to a relative %.1e", worst));

        // Cost: one backward pass for all gradients, against two forward passes per input.
        int inputs = 1000;
        Value[] w = new Value[inputs];
        for (int i = 0; i < inputs; i++) w[i] = new Value(rnd.nextGaussian());
        nodesCreated = 0; backwardSteps = 0;
        Value s = new Value(0);
        for (int i = 0; i < inputs; i++) s = add(s, square(sub(w[i], new Value(i / (double) inputs))));
        long forwardOps = nodesCreated;
        backpropagate(s);
        long backOps = backwardSteps;
        boolean allRight = true;
        for (int i = 0; i < inputs; i++) allRight &= close(w[i].grad, 2 * (w[i].data - i / (double) inputs), 1e-12);
        check(allRight, "gradient of sum (w_i - c_i)^2 is 2 (w_i - c_i)");
        check(forwardOps == 3L * inputs, "forward operation count");
        long fdOps = 2L * inputs * forwardOps;
        System.out.println(f("%,d inputs: one forward pass is %,d operations, one backward pass visits %,d nodes (the operations plus inputs and constants); "
                + "central finite differences would need %,d forward passes (%,d operations)",
                inputs, forwardOps, backOps, 2 * inputs, fdOps));

        // Gradient descent on f(x) = x^2: x <- x - lr * 2x = (1 - 2 lr) x. Converges only for 0 < lr < 1.
        StringBuilder sb = new StringBuilder("gradient descent on x^2 from x = 1, 50 steps: ");
        double[] rates = {0.1, 0.5, 0.9, 1.0, 1.1};
        double[] finals = new double[rates.length];
        for (int k = 0; k < rates.length; k++) {
            Value xv = new Value(1);
            for (int step = 0; step < 50; step++) {
                xv.grad = 0;
                backpropagate(square(xv));
                xv.data -= rates[k] * xv.grad;
            }
            finals[k] = xv.data;
            sb.append(f("lr %.1f -> x = %.3g; ", rates[k], xv.data));
        }
        check(Math.abs(finals[0]) < 1e-4 && finals[1] == 0 && Math.abs(finals[2]) < 1e-4, "lr < 1 converges");
        check(Math.abs(finals[3]) == 1, "lr = 1 oscillates forever");
        check(Math.abs(finals[4]) > 1000, "lr > 1 diverges");
        System.out.println(sb.toString().trim());

        // Train a network to compute XOR, which no single linear unit can.
        int[] report = {0, 50, 100, 200, 500, 1000};
        double[] good = train(7, 1000, 0.05, true, report);
        double[] bug = train(7, 1000, 0.05, false, report);
        StringBuilder tr = new StringBuilder("XOR, 2-8-1 tanh network, learning rate 0.05, loss at step ");
        for (int k = 0; k < report.length; k++) tr.append(f("%d: %.5f; ", report[k], good[k]));
        System.out.println(tr.toString().trim());
        check(good[report.length - 1] < 0.01, "XOR is learned");
        for (int k = 1; k < report.length; k++) check(good[k] < good[k - 1], "loss falls");
        check(new Mlp(2, 8, new Random(7)).params.size() == 33, "2-8-1 network has 33 parameters");

        // Forgetting to reset gradients: each step uses the SUM of every gradient so far (momentum that never
        // decays). On XOR it happens to work; on x^2 with lr 0.1 the iterate keeps swinging and never settles.
        Value xv = new Value(1);
        double maxLate = 0;
        for (int step = 0; step < 200; step++) {
            backpropagate(square(xv));          // no xv.grad = 0 here
            xv.data -= 0.1 * xv.grad;
            if (step >= 150) maxLate = Math.max(maxLate, Math.abs(xv.data));
        }
        check(maxLate > 0.5, "without resetting, gradient descent on x^2 does not converge");
        System.out.println(f("without resetting gradients: XOR loss at step 1000 is %.5f (it acts like momentum and "
                + "happens to work), but on x^2 with lr 0.1 |x| still reaches %.3f in steps 150-199 (it never settles)",
                bug[report.length - 1], maxLate));
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(102));
        System.out.println("Backpropagation: " + passed + " checks passed");
    }
}
