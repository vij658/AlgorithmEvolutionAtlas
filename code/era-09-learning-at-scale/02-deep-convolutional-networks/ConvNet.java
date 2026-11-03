import java.util.*;

/**
 * Era 9, topic 2: Deep convolutional networks (Krizhevsky, Sutskever and Hinton, University of Toronto, 2012).
 *
 * HOW IT WORKS
 *   A convolutional layer slides a small filter (here 3 x 3 numbers) over the image and, at every position, multiplies
 *   the filter by the pixels under it and adds them up. Where the image matches the filter's pattern, the sum is
 *   large. The same filter is used at every position (weight sharing), so a pattern learned in one corner is
 *   recognized in any other. An activation function then bends the sums: AlexNet used the rectified linear unit
 *   ReLU(x) = max(0, x), which unlike the S-shaped tanh and sigmoid does not flatten out for large inputs, so its
 *   gradient does not vanish. Pooling summarizes each map; here global max pooling keeps only each filter's
 *   strongest response anywhere in the image. A final layer turns the pooled responses into class probabilities
 *   (softmax). Everything is trained by backpropagation (Era 7, topic 7) and stochastic gradient descent.
 *   Dropout switches off a random half of a layer's units at each training step, so that no unit can rely on others,
 *   and scales the survivors up to keep the average the same; at test time all units are used.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Makes 12 x 12 images of four kinds of stroke (horizontal, vertical and two diagonals) with noise and stray
 *      dots. Training strokes all lie in the left half of the image; test strokes all lie in the right half.
 *   2. Trains a small convolutional network (6 filters of 3 x 3, ReLU, global max pooling, softmax: 88 numbers) and
 *      checks its gradient against finite differences. It recognizes strokes in the half it never saw.
 *   3. Trains a fully connected network with the same data (144 inputs, 16 hidden units: 2,388 numbers). It fits
 *      the left half and fails on the right: it has no idea that a stroke is the same stroke elsewhere.
 *   4. ReLU against tanh: images seen until the training error first falls below 25% (the measure Krizhevsky and
 *      colleagues used, on CIFAR-10), for 8 starting weights.
 *   5. Dropout on a fully connected network with 64 hidden units trained on 240 images.
 *   6. Prints the trained network's 88 numbers for the book's widget, which lets the reader draw a stroke.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ConvNet.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ConvNet {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final int S = 12, F = 6, K = 4, M = S - 2; // image side, filters, classes, map side
    static final String[] NAMES = {"horizontal", "vertical", "diagonal down", "diagonal up"};

    // ---- data ---------------------------------------------------------------------------------------------------------
    /** A stroke of class k, length 4 to 6, entirely inside columns [c0, c1], with noise and three stray dots. */
    static double[] stroke(Random r, int k, int c0, int c1) {
        double[] img = new double[S * S];
        int len = 4 + r.nextInt(3);
        int dx = k == 1 ? 0 : 1, dy = k == 0 ? 0 : (k == 3 ? -1 : 1);
        int x0, y0;
        while (true) {
            x0 = c0 + r.nextInt(c1 - c0 + 1);
            y0 = r.nextInt(S);
            int x1 = x0 + dx * (len - 1), y1 = y0 + dy * (len - 1);
            if (x1 <= c1 && y1 >= 0 && y1 < S) break;
        }
        for (int i = 0; i < len; i++) img[(y0 + dy * i) * S + x0 + dx * i] = 1.0;
        for (int i = 0; i < S * S; i++) img[i] += 0.12 * r.nextGaussian();
        for (int i = 0; i < 3; i++) img[r.nextInt(S * S)] += 0.7;
        return img;
    }

    static double[][] X;
    static int[] Y;

    static void makeSet(Random r, int n, int c0, int c1) {
        X = new double[n][];
        Y = new int[n];
        for (int i = 0; i < n; i++) { Y[i] = i % K; X[i] = stroke(r, Y[i], c0, c1); }
    }

    // ---- the convolutional network ---------------------------------------------------------------------------------
    static boolean RELU = true;

    static double act(double z) { return RELU ? Math.max(0, z) : Math.tanh(z); }

    static double dact(double z) { return RELU ? (z > 0 ? 1 : 0) : 1 - Math.tanh(z) * Math.tanh(z); }

    static double[][] W = new double[F][9];   // filters
    static double[] B = new double[F];        // filter biases
    static double[][] V = new double[K][F];   // output weights
    static double[] C = new double[K];        // output biases

    static void init(long seed) {
        Random r = new Random(seed);
        for (int f = 0; f < F; f++) { for (int j = 0; j < 9; j++) W[f][j] = 0.5 * r.nextGaussian(); B[f] = 0; }
        for (int k = 0; k < K; k++) { for (int f = 0; f < F; f++) V[k][f] = 0.5 * r.nextGaussian(); C[k] = 0; }
    }

    /** Filter f applied at map position (i, j): the pre-activation sum. */
    static double conv(double[] img, int f, int i, int j) {
        double s = B[f];
        for (int a = 0; a < 3; a++) for (int b = 0; b < 3; b++) s += W[f][a * 3 + b] * img[(i + a) * S + j + b];
        return s;
    }

    static int[] argmax = new int[F];
    static double[] pre = new double[F], feat = new double[F];

    /** Forward pass: global max pooling of each filter's activation map, then softmax over the 4 classes. */
    static double[] forward(double[] img) {
        for (int f = 0; f < F; f++) {
            double best = Double.NEGATIVE_INFINITY;
            for (int i = 0; i < M; i++) for (int j = 0; j < M; j++) {
                double z = conv(img, f, i, j), a = act(z);
                if (a > best) { best = a; argmax[f] = i * M + j; pre[f] = z; }
            }
            feat[f] = best;
        }
        double[] lg = new double[K];
        double mx = Double.NEGATIVE_INFINITY;
        for (int k = 0; k < K; k++) { lg[k] = C[k]; for (int f = 0; f < F; f++) lg[k] += V[k][f] * feat[f]; mx = Math.max(mx, lg[k]); }
        double s = 0;
        for (int k = 0; k < K; k++) { lg[k] = Math.exp(lg[k] - mx); s += lg[k]; }
        for (int k = 0; k < K; k++) lg[k] /= s;
        return lg;
    }

    static double loss(double[] img, int y) { return -Math.log(forward(img)[y]); }

    /** Gradients of the loss for one image, by backpropagation. */
    static double[][] gW = new double[F][9], gV = new double[K][F];
    static double[] gB = new double[F], gC = new double[K];

    static void backward(double[] img, int y) {
        double[] p = forward(img);
        for (double[] row : gW) Arrays.fill(row, 0);
        for (double[] row : gV) Arrays.fill(row, 0);
        Arrays.fill(gB, 0); Arrays.fill(gC, 0);
        double[] dfeat = new double[F];
        for (int k = 0; k < K; k++) {
            double dl = p[k] - (k == y ? 1 : 0);
            gC[k] = dl;
            for (int f = 0; f < F; f++) { gV[k][f] = dl * feat[f]; dfeat[f] += dl * V[k][f]; }
        }
        for (int f = 0; f < F; f++) { // max pooling passes the gradient to the winning position only
            int i = argmax[f] / M, j = argmax[f] % M;
            double dz = dfeat[f] * dact(pre[f]);
            gB[f] = dz;
            for (int a = 0; a < 3; a++) for (int b = 0; b < 3; b++) gW[f][a * 3 + b] = dz * img[(i + a) * S + j + b];
        }
    }

    static void sgdStep(double lr) {
        for (int f = 0; f < F; f++) { for (int j = 0; j < 9; j++) W[f][j] -= lr * gW[f][j]; B[f] -= lr * gB[f]; }
        for (int k = 0; k < K; k++) { for (int f = 0; f < F; f++) V[k][f] -= lr * gV[k][f]; C[k] -= lr * gC[k]; }
    }

    static int predict(double[] img) {
        double[] p = forward(img);
        int best = 0;
        for (int k = 1; k < K; k++) if (p[k] > p[best]) best = k;
        return best;
    }

    static double errorRate(double[][] xs, int[] ys) {
        int wrong = 0;
        for (int i = 0; i < xs.length; i++) if (predict(xs[i]) != ys[i]) wrong++;
        return (double) wrong / xs.length;
    }

    /** Train for up to maxEpochs passes; returns the first pass after which the training error is below `target`. */
    static int train(double[][] xs, int[] ys, int maxEpochs, double lr, double target, long seed) {
        Random r = new Random(seed);
        Integer[] order = new Integer[xs.length];
        for (int i = 0; i < order.length; i++) order[i] = i;
        int reached = -1;
        for (int e = 1; e <= maxEpochs; e++) {
            Collections.shuffle(Arrays.asList(order), r);
            for (int i : order) { backward(xs[i], ys[i]); sgdStep(lr); }
            if (reached < 0 && errorRate(xs, ys) < target) { reached = e; if (target > 0) break; }
        }
        return reached;
    }

    // ---- a fully connected network, for comparison -------------------------------------------------------------
    static int H = 16;
    static double[][] A1, A2;
    static double[] b1, b2;

    static void mlpInit(long seed) {
        A1 = new double[H][S * S]; A2 = new double[K][H]; b1 = new double[H]; b2 = new double[K]; hid = new double[H];
        Random r = new Random(seed);
        for (int h = 0; h < H; h++) { for (int j = 0; j < S * S; j++) A1[h][j] = r.nextGaussian() / Math.sqrt(S * S); b1[h] = 0; }
        for (int k = 0; k < K; k++) { for (int h = 0; h < H; h++) A2[k][h] = r.nextGaussian() / Math.sqrt(H); b2[k] = 0; }
    }

    static double[] hid;

    static double[] mlpForward(double[] x, boolean[] keep, double scale) {
        for (int h = 0; h < H; h++) {
            double z = b1[h];
            for (int j = 0; j < S * S; j++) z += A1[h][j] * x[j];
            hid[h] = Math.max(0, z) * (keep == null ? 1 : (keep[h] ? scale : 0));
        }
        double[] lg = new double[K];
        double mx = Double.NEGATIVE_INFINITY;
        for (int k = 0; k < K; k++) { lg[k] = b2[k]; for (int h = 0; h < H; h++) lg[k] += A2[k][h] * hid[h]; mx = Math.max(mx, lg[k]); }
        double s = 0;
        for (int k = 0; k < K; k++) { lg[k] = Math.exp(lg[k] - mx); s += lg[k]; }
        for (int k = 0; k < K; k++) lg[k] /= s;
        return lg;
    }

    static void mlpTrain(double[][] xs, int[] ys, int epochs, double lr, double drop, long seed) {
        Random r = new Random(seed);
        Integer[] order = new Integer[xs.length];
        for (int i = 0; i < order.length; i++) order[i] = i;
        boolean[] keep = new boolean[H];
        for (int e = 0; e < epochs; e++) {
            Collections.shuffle(Arrays.asList(order), r);
            for (int i : order) {
                for (int h = 0; h < H; h++) keep[h] = r.nextDouble() >= drop;
                double[] x = xs[i];
                double[] p = mlpForward(x, drop > 0 ? keep : null, 1 / (1 - drop));
                double[] dh = new double[H];
                for (int k = 0; k < K; k++) {
                    double dl = p[k] - (k == ys[i] ? 1 : 0);
                    for (int h = 0; h < H; h++) { dh[h] += dl * A2[k][h]; A2[k][h] -= lr * dl * hid[h]; }
                    b2[k] -= lr * dl;
                }
                for (int h = 0; h < H; h++) {
                    if (hid[h] <= 0) continue; // ReLU off, or dropped
                    double dz = dh[h] * (drop > 0 ? 1 / (1 - drop) : 1);
                    for (int j = 0; j < S * S; j++) A1[h][j] -= lr * dz * x[j];
                    b1[h] -= lr * dz;
                }
            }
        }
    }

    static double mlpError(double[][] xs, int[] ys) {
        int wrong = 0;
        for (int i = 0; i < xs.length; i++) {
            double[] p = mlpForward(xs[i], null, 1);
            int best = 0;
            for (int k = 1; k < K; k++) if (p[k] > p[best]) best = k;
            if (best != ys[i]) wrong++;
        }
        return (double) wrong / xs.length;
    }

    public static void main(String[] args) {
        Random data = new Random(2012);
        makeSet(data, 800, 0, 5);
        double[][] trX = X; int[] trY = Y;
        makeSet(data, 400, 6, 11);
        double[][] teX = X; int[] teY = Y;
        makeSet(data, 400, 0, 5);
        double[][] leftX = X; int[] leftY = Y;
        System.out.printf("data: 12 x 12 images of 4 strokes (%s), length 4 to 6, noise and 3 stray dots ; training: %d images with every stroke in the left half ; tests: %d in the left half, %d in the right half%n",
                String.join(", ", NAMES), trX.length, leftX.length, teX.length);

        // ---- 2. the convolutional network -------------------------------------------------------------------------
        RELU = true;
        init(7);
        // gradient check on a few images
        double worst = 0;
        Random gc = new Random(1);
        for (int t = 0; t < 5; t++) {
            int n = gc.nextInt(trX.length);
            backward(trX[n], trY[n]);
            double[][] aW = new double[F][9];
            for (int f = 0; f < F; f++) aW[f] = gW[f].clone();
            double[][] aV = new double[K][];
            for (int k = 0; k < K; k++) aV[k] = gV[k].clone();
            double h = 1e-6;
            for (int f = 0; f < F; f++) for (int j = 0; j < 9; j++) {
                double o = W[f][j];
                W[f][j] = o + h; double lp = loss(trX[n], trY[n]);
                W[f][j] = o - h; double lm = loss(trX[n], trY[n]);
                W[f][j] = o;
                worst = Math.max(worst, Math.abs((lp - lm) / (2 * h) - aW[f][j]));
            }
            for (int k = 0; k < K; k++) for (int f = 0; f < F; f++) {
                double o = V[k][f];
                V[k][f] = o + h; double lp = loss(trX[n], trY[n]);
                V[k][f] = o - h; double lm = loss(trX[n], trY[n]);
                V[k][f] = o;
                worst = Math.max(worst, Math.abs((lp - lm) / (2 * h) - aV[k][f]));
            }
        }
        check(worst < 1e-6, "backpropagation agrees with finite differences");
        train(trX, trY, 40, 0.02, 0, 11);
        double cTrain = errorRate(trX, trY), cLeft = errorRate(leftX, leftY), cRight = errorRate(teX, teY);
        check(cTrain < 0.05 && cRight < 0.10, "the convolutional network recognizes strokes in the half it never saw");
        int[][] conf = new int[K][K];
        for (int i = 0; i < teX.length; i++) conf[teY[i]][predict(teX[i])]++;
        StringJoiner cj = new StringJoiner(" ; ");
        for (int k = 0; k < K; k++) cj.add(NAMES[k] + " " + conf[k][k] + "/" + (teX.length / K));
        System.out.printf("cnn: 6 filters of 3 x 3, ReLU, global max pooling, softmax: %d numbers ; gradient check: largest difference %.1e ; 40 passes of SGD ; error: training %.1f%%, new left-half images %.1f%%, right-half images (never seen) %.1f%% ; right half by class: %s%n",
                F * 9 + F + K * F + K, worst, 100 * cTrain, 100 * cLeft, 100 * cRight, cj);
        // remember the trained network for the widget
        double[][] tW = new double[F][]; for (int f = 0; f < F; f++) tW[f] = W[f].clone();
        double[] tB = B.clone(); double[][] tV = new double[K][]; for (int k = 0; k < K; k++) tV[k] = V[k].clone(); double[] tC = C.clone();

        // ---- 3. a fully connected network -------------------------------------------------------------------------
        mlpInit(5);
        mlpTrain(trX, trY, 40, 0.01, 0, 13);
        double mTrain = mlpError(trX, trY), mLeft = mlpError(leftX, leftY), mRight = mlpError(teX, teY);
        check(mTrain < 0.05 && mRight > 0.4, "the fully connected network fits the left half and fails on the right");
        System.out.printf("mlp: fully connected, 144 inputs, %d ReLU units, softmax: %,d numbers ; 40 passes of SGD ; error: training %.1f%%, new left-half images %.1f%%, right-half images %.1f%% (chance is 75%%)%n",
                H, H * 144 + H + K * H + K, 100 * mTrain, 100 * mLeft, 100 * mRight);

        // ---- 4. ReLU against tanh ------------------------------------------------------------------------------------
        StringJoiner rj = new StringJoiner(" ; ");
        int reluTotal = 0, tanhTotal = 0, reluWins = 0;
        double[][] probeX = Arrays.copyOf(trX, 200); int[] probeY = Arrays.copyOf(trY, 200);
        for (long seed = 1; seed <= 8; seed++) {
            int[] res = new int[2];
            for (int t = 0; t < 2; t++) {
                RELU = t == 0;
                init(100 + seed);
                Random r = new Random(200 + seed); // the same starting weights and the same sequence of images
                res[t] = -1;
                for (int steps = 1; steps <= 40_000; steps++) {
                    int n = r.nextInt(trX.length);
                    backward(trX[n], trY[n]);
                    sgdStep(0.02);
                    if (steps % 20 == 0 && errorRate(probeX, probeY) < 0.25) { res[t] = steps; break; }
                }
                check(res[t] > 0, "training error falls below 25%");
            }
            reluTotal += res[0]; tanhTotal += res[1];
            if (res[0] < res[1]) reluWins++;
            rj.add(String.format("start %d: ReLU %d, tanh %d", seed, res[0], res[1]));
        }
        check(reluWins >= 6 && reluTotal < tanhTotal, "ReLU reaches 25% training error sooner");
        System.out.printf("relu: images seen until the training error (first 200 training images, checked every 20) first falls below 25%%, same starting weights and same images ; %s ; total ReLU %,d, tanh %,d: tanh needed %.1f times as many ; ReLU faster in %d of 8%n",
                rj, reluTotal, tanhTotal, (double) tanhTotal / reluTotal, reluWins);
        RELU = true;

        // ---- 5. dropout ---------------------------------------------------------------------------------------------
        H = 64;
        double[][] smallX = Arrays.copyOf(trX, 240); int[] smallY = Arrays.copyOf(trY, 240);
        double[] te = new double[2], trn = new double[2];
        int dropWins = 0;
        for (long seed = 1; seed <= 5; seed++) {
            double[] one = new double[2];
            for (int t = 0; t < 2; t++) {
                mlpInit(300 + seed);
                mlpTrain(smallX, smallY, 100, 0.01, t == 0 ? 0 : 0.5, 400 + seed);
                trn[t] += mlpError(smallX, smallY) / 5;
                one[t] = mlpError(leftX, leftY);
                te[t] += one[t] / 5;
            }
            if (one[1] < one[0]) dropWins++;
        }
        check(te[1] < te[0], "dropout lowers the average test error here");
        System.out.printf("dropout: fully connected network with 64 hidden units, 240 training images, 100 passes, 5 starts ; without dropout: training error %.1f%%, error on new left-half images %.1f%% ; dropout 0.5 on the hidden units: training error %.1f%%, error on new images %.1f%% ; dropout better in %d of 5 starts%n",
                100 * trn[0], 100 * te[0], 100 * trn[1], 100 * te[1], dropWins);
        H = 16;

        // ---- 6. the widget's network ---------------------------------------------------------------------------------
        W = tW; B = tB; V = tV; C = tC;
        StringJoiner wj = new StringJoiner(" ; ");
        for (int f = 0; f < F; f++) {
            StringJoiner one = new StringJoiner(",");
            for (double x : W[f]) one.add(String.format("%.3f", x));
            wj.add(String.format("filter %d: %s bias %.3f", f, one, B[f]));
        }
        for (int k = 0; k < K; k++) {
            StringJoiner one = new StringJoiner(",");
            for (double x : V[k]) one.add(String.format("%.3f", x));
            wj.add(String.format("class %d: %s bias %.3f", k, one, C[k]));
        }
        // the rounded network must still give the same answers
        double[][] rW = new double[F][9]; double[] rB = new double[F]; double[][] rV = new double[K][F]; double[] rC = new double[K];
        for (int f = 0; f < F; f++) { for (int j = 0; j < 9; j++) rW[f][j] = Math.round(W[f][j] * 1000) / 1000.0; rB[f] = Math.round(B[f] * 1000) / 1000.0; }
        for (int k = 0; k < K; k++) { for (int f = 0; f < F; f++) rV[k][f] = Math.round(V[k][f] * 1000) / 1000.0; rC[k] = Math.round(C[k] * 1000) / 1000.0; }
        int[] full = new int[teX.length];
        for (int i = 0; i < teX.length; i++) full[i] = predict(teX[i]);
        W = rW; B = rB; V = rV; C = rC;
        int same = 0;
        for (int i = 0; i < teX.length; i++) if (predict(teX[i]) == full[i]) same++;
        check(same >= teX.length - 2, "the printed (rounded) network gives the same answers");
        // a clean stroke of each class in the middle
        StringJoiner pj = new StringJoiner(" ; ");
        for (int k = 0; k < K; k++) {
            double[] img = new double[S * S];
            int dx = k == 1 ? 0 : 1, dy = k == 0 ? 0 : (k == 3 ? -1 : 1), x0 = 4, y0 = k == 3 ? 8 : (k == 0 ? 6 : 3);
            for (int i = 0; i < 5; i++) img[(y0 + dy * i) * S + x0 + dx * i] = 1;
            double[] p = forward(img);
            check(predict(img) == k, "a clean " + NAMES[k] + " stroke is recognized");
            pj.add(String.format("%s %.3f", NAMES[k], p[k]));
        }
        System.out.printf("widget: trained network, numbers rounded to 3 decimals (same answer on %d of %d right-half images) ; %s ; clean 5-pixel strokes in the middle, probability of the right class: %s%n",
                same, teX.length, wj, pj);

        System.out.println("ConvNet: " + passed + " checks passed");
    }
}
