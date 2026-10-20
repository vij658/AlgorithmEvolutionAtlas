import java.security.MessageDigest;
import java.util.*;

/**
 * Era 7, topic 6: zero-knowledge proofs (Goldwasser, Micali and Rackoff, 1985; Goldreich, Micali and Wigderson, 1986).
 *
 * HOW IT WORKS
 *   A prover wants to convince a verifier that something is true, say that two graphs are the same graph with the
 *   vertices renamed, without revealing why (the renaming). Each round the prover draws a fresh random renaming of the
 *   first graph and shows the result H. The verifier flips a coin: "show me how H comes from graph 0" or "from graph 1".
 *   Someone who knows the secret renaming can always answer. Someone who does not can prepare for only one of the two
 *   questions, and is caught half the time, so k rounds leave a cheater 1 chance in 2^k. And the verifier learns
 *   nothing: a "simulator" who knows no secret can produce conversations with exactly the same distribution, by
 *   guessing the coin in advance and starting again when wrong. Goldreich, Micali and Wigderson then gave such a proof
 *   for every problem in NP, through graph 3-colouring: the prover locks each vertex's colour in a sealed box (here a
 *   hash commitment), the verifier picks an edge, and only those two boxes are opened.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Graph isomorphism: an honest prover always passes; a cheater with two different graphs is caught half the time
 *      per round, and passes k rounds about once in 2^k.
 *   2. The simulator: real conversations and simulated ones, counted over all possible transcripts, are the same.
 *   3. Graph 3-colouring with SHA-256 commitments: an honest prover always passes, and the colours the verifier sees
 *      are uniformly random pairs; a prover whose colouring has one bad edge is caught about once in E rounds.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java ZeroKnowledge.java
 *   Expected output: expected-output.txt in this folder.
 */
public class ZeroKnowledge {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1985L;

    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / (double) (1L << 53);
    }

    static int below(int k) { return (int) (uniform() * k); }

    static int[] randomPerm(int n) {
        int[] p = new int[n];
        for (int i = 0; i < n; i++) p[i] = i;
        for (int i = n - 1; i > 0; i--) { int j = below(i + 1); int t = p[i]; p[i] = p[j]; p[j] = t; }
        return p;
    }

    /** The graph with vertex i renamed p[i]. */
    static boolean[][] rename(boolean[][] g, int[] p) {
        int n = g.length;
        boolean[][] h = new boolean[n][n];
        for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) h[p[i]][p[j]] = g[i][j];
        return h;
    }

    static int[] compose(int[] a, int[] b) {          // first b, then a
        int[] c = new int[b.length];
        for (int i = 0; i < b.length; i++) c[i] = a[b[i]];
        return c;
    }

    static int[] inverse(int[] p) {
        int[] q = new int[p.length];
        for (int i = 0; i < p.length; i++) q[p[i]] = i;
        return q;
    }

    static boolean[][] randomGraph(int n, int edges) {
        boolean[][] g = new boolean[n][n];
        int e = 0;
        while (e < edges) {
            int a = below(n), b = below(n);
            if (a == b || g[a][b]) continue;
            g[a][b] = g[b][a] = true;
            e++;
        }
        return g;
    }

    /** Tries every renaming (n! of them): are the graphs isomorphic? */
    static boolean isomorphic(boolean[][] a, boolean[][] b) {
        int n = a.length;
        int[] p = new int[n];
        for (int i = 0; i < n; i++) p[i] = i;
        while (true) {
            if (Arrays.deepEquals(rename(a, p), b)) return true;
            int i = n - 2;
            while (i >= 0 && p[i] > p[i + 1]) i--;
            if (i < 0) return false;
            int j = n - 1;
            while (p[j] < p[i]) j--;
            int t = p[i]; p[i] = p[j]; p[j] = t;
            for (int l = i + 1, r = n - 1; l < r; l++, r--) { t = p[l]; p[l] = p[r]; p[r] = t; }
        }
    }

    // ---- one round of the isomorphism protocol ------------------------------------------------------------------------
    /** The honest prover knows pi with G1 = pi(G0). Returns true if the verifier accepts. */
    static boolean honestRound(boolean[][] g0, boolean[][] g1, int[] pi) {
        int[] sigma = randomPerm(g0.length);
        boolean[][] h = rename(g0, sigma);                     // the prover shows H
        int alpha = below(2);                                  // the verifier's coin
        int[] rho = alpha == 0 ? sigma : compose(sigma, inverse(pi));   // a renaming that takes G_alpha to H
        return Arrays.deepEquals(rename(alpha == 0 ? g0 : g1, rho), h);
    }

    /** A cheater with non-isomorphic graphs guesses the coin, and builds H from that graph. */
    static boolean cheatingRound(boolean[][] g0, boolean[][] g1) {
        int guess = below(2);
        int[] sigma = randomPerm(g0.length);
        boolean[][] h = rename(guess == 0 ? g0 : g1, sigma);
        int alpha = below(2);
        // if the guess was wrong, no renaming of G_alpha gives H; the cheater sends sigma anyway
        return Arrays.deepEquals(rename(alpha == 0 ? g0 : g1, sigma), h);
    }

    static String key(boolean[][] h, int alpha, int[] rho) {
        StringBuilder s = new StringBuilder();
        for (boolean[] row : h) for (boolean x : row) s.append(x ? '1' : '0');
        s.append('|').append(alpha).append('|');
        for (int x : rho) s.append(x);
        return s.toString();
    }

    // ---- commitments: SHA-256 of a random nonce and the value --------------------------------------------------------
    static byte[] sha(byte[] nonce, int value) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(nonce);
            md.update((byte) value);
            return md.digest();
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    static byte[] nonce() {
        byte[] r = new byte[16];
        for (int i = 0; i < 16; i++) r[i] = (byte) below(256);
        return r;
    }

    static int[][] edges;

    /** One round of the 3-colouring protocol; colouring may be invalid (a cheater). Returns the verifier's verdict. */
    static int lastA, lastB;

    static boolean colourRound(int[] colouring) {
        int n = colouring.length;
        int[] shuffle = randomPerm(3);                         // rename the three colours at random
        int[] c = new int[n];
        byte[][] nonces = new byte[n][], boxes = new byte[n][];
        for (int v = 0; v < n; v++) {
            c[v] = shuffle[colouring[v]];
            nonces[v] = nonce();
            boxes[v] = sha(nonces[v], c[v]);                   // the prover sends all the sealed boxes
        }
        int[] e = edges[below(edges.length)];                  // the verifier picks an edge
        int a = e[0], b = e[1];
        // the prover opens two boxes; the verifier checks they match what was sealed, and that the colours differ
        boolean opened = Arrays.equals(sha(nonces[a], c[a]), boxes[a]) && Arrays.equals(sha(nonces[b], c[b]), boxes[b]);
        lastA = c[a]; lastB = c[b];
        return opened && c[a] != c[b] && c[a] >= 0 && c[a] < 3 && c[b] >= 0 && c[b] < 3;
    }

    public static void main(String[] args) {
        // ---- 1. graph isomorphism ---------------------------------------------------------------------------------------
        int n = 8;
        boolean[][] g0 = randomGraph(n, 14);
        int[] pi = randomPerm(n);
        boolean[][] g1 = rename(g0, pi);
        boolean[][] other = randomGraph(n, 14);
        check(isomorphic(g0, g1), "G0 and G1 are isomorphic");
        check(!isomorphic(g0, other), "G0 and the cheater's graph are not (checked over all 8! renamings)");
        int honestRuns = 1000, rounds = 20;
        for (int r = 0; r < honestRuns; r++) {
            boolean ok = true;
            for (int k = 0; k < rounds; k++) ok &= honestRound(g0, g1, pi);
            check(ok, "the honest prover passes");
        }
        long caught = 0, total = 200_000;
        for (long t = 0; t < total; t++) if (!cheatingRound(g0, other)) caught++;
        double catchRate = (double) caught / total;
        check(Math.abs(catchRate - 0.5) < 0.01, "a cheater is caught half the time per round");
        StringJoiner kj = new StringJoiner(" ; ");
        int trials = 100_000;
        for (int k : new int[]{1, 2, 5, 10}) {
            int survived = 0;
            for (int t = 0; t < trials; t++) {
                boolean ok = true;
                for (int r = 0; r < k && ok; r++) ok = cheatingRound(g0, other);
                if (ok) survived++;
            }
            double expect = trials / Math.pow(2, k);
            check(Math.abs(survived - expect) < 5 * Math.sqrt(expect) + 1, "survival about 1 in 2^k");
            kj.add(String.format("%d round%s: %,d of %,d cheaters passed (2^-k predicts %,.0f)", k, k == 1 ? "" : "s", survived, trials, expect));
        }
        System.out.printf("iso: two graphs of %d vertices and 14 edges ; the honest prover, who knows the renaming, passed all %d rounds in %,d of %,d runs ; a cheater whose graphs are not isomorphic was caught in %,d of %,d single rounds (%.3f) ; %s%n",
                n, rounds, honestRuns, honestRuns, caught, total, catchRate, kj);

        // ---- 2. the simulator --------------------------------------------------------------------------------------------
        int m = 5;
        boolean[][] s0 = randomGraph(m, 5);
        int[] spi = randomPerm(m);
        boolean[][] s1 = rename(s0, spi);
        int samples = 600_000;
        Map<String, Integer> real = new HashMap<>(), sim = new HashMap<>();
        for (int t = 0; t < samples; t++) {
            int[] sigma = randomPerm(m);
            boolean[][] h = rename(s0, sigma);
            int alpha = below(2);
            int[] rho = alpha == 0 ? sigma : compose(sigma, inverse(spi));
            real.merge(key(h, alpha, rho), 1, Integer::sum);
        }
        long attempts = 0;
        for (int t = 0; t < samples; t++) {
            while (true) {
                attempts++;
                int guess = below(2);                                // the simulator knows no secret
                int[] tau = randomPerm(m);
                boolean[][] h = rename(guess == 0 ? s0 : s1, tau);
                int alpha = below(2);                                // an honest verifier's coin
                if (alpha != guess) continue;                        // wrong guess: rewind and try again
                sim.merge(key(h, alpha, tau), 1, Integer::sum);
                break;
            }
        }
        Set<String> all = new HashSet<>(real.keySet());
        all.addAll(sim.keySet());
        double tv = 0;
        for (String k : all) tv += Math.abs(real.getOrDefault(k, 0) - sim.getOrDefault(k, 0)) / (double) samples;
        tv /= 2;
        check(real.keySet().equals(sim.keySet()), "the same transcripts occur");
        check(real.size() == 2 * 120, "each of 2 coins x 5! renamings occurs");
        check(tv < 0.02, "with the same frequencies, up to sampling noise");
        System.out.printf("simulate: graphs of %d vertices ; %,d real conversations (shown graph, coin, renaming) and %,d produced by a simulator that knows no secret ; both contain the same %d different transcripts, and the frequencies differ by a total variation distance of %.4f, sampling noise ; the simulator needed %.2f attempts per transcript, rewinding whenever its guess of the coin was wrong%n",
                m, samples, samples, real.size(), tv, (double) attempts / samples);

        // ---- 3. graph 3-colouring with commitments ---------------------------------------------------------------------
        int v = 12;
        int[] colour = new int[v];
        for (int i = 0; i < v; i++) colour[i] = i % 3;
        List<int[]> el = new ArrayList<>();
        for (int a = 0; a < v; a++) for (int b = a + 1; b < v; b++) if (colour[a] != colour[b] && uniform() < 0.6) el.add(new int[]{a, b});
        edges = el.toArray(new int[0][]);
        int E = edges.length;
        int honest = 0;
        int[][] seen = new int[3][3];
        int honestRounds = 60_000;
        for (int r = 0; r < honestRounds; r++) {
            boolean ok = colourRound(colour);
            check(ok, "an honest colouring always passes");
            honest++;
            seen[lastA][lastB]++;
        }
        StringJoiner pj = new StringJoiner(" ");
        double maxDev = 0;
        for (int a = 0; a < 3; a++) for (int b = 0; b < 3; b++) {
            if (a == b) { check(seen[a][b] == 0, "never the same colour"); continue; }
            double share = seen[a][b] / (double) honestRounds;
            maxDev = Math.max(maxDev, Math.abs(share - 1.0 / 6));
            pj.add(String.format("(%d,%d):%.3f", a + 1, b + 1, share));
        }
        check(maxDev < 0.01, "each of the 6 ordered pairs of colours shows about 1/6 of the time");
        // a cheater: the graph gets one more edge, between two vertices of the same colour, and the prover keeps the
        // old colouring, so exactly one edge has both ends the same colour
        int[] bad = colour;
        int[][] withExtra = Arrays.copyOf(edges, E + 1);
        withExtra[E] = new int[]{0, 3};
        edges = withExtra;
        E = edges.length;
        int badEdges = 0;
        for (int[] e : edges) if (bad[e[0]] == bad[e[1]]) badEdges++;
        int caughtRounds = 0, cheatRounds = 100_000;
        for (int r = 0; r < cheatRounds; r++) if (!colourRound(bad)) caughtRounds++;
        double perRound = caughtRounds / (double) cheatRounds;
        check(badEdges == 1, "exactly one bad edge");
        check(Math.abs(perRound - badEdges / (double) E) < 0.005, "caught when the bad edge is picked");
        StringJoiner cj = new StringJoiner(" ; ");
        for (int mult : new int[]{1, 3, 5}) {
            int k = mult * E, survived = 0, runs = 2000;
            for (int t = 0; t < runs; t++) {
                boolean ok = true;
                for (int r = 0; r < k && ok; r++) ok = colourRound(bad);
                if (ok) survived++;
            }
            double expect = runs * Math.pow(1 - badEdges / (double) E, k);
            check(Math.abs(survived - expect) < 5 * Math.sqrt(expect) + 2, "survival (1 - bad/E)^k");
            cj.add(String.format("%,d rounds: %,d of %,d cheaters passed (predicted %.0f)", k, survived, runs, expect));
        }
        System.out.printf("colour: a graph of %d vertices and %d edges with a 3-colouring ; each round the prover renames the 3 colours at random and seals every vertex's colour as SHA-256(random nonce, colour) ; the verifier picks one edge and only those two boxes are opened ; the honest prover passed all %,d rounds, and the opened pairs were spread evenly over the 6 possibilities: %s ; add one edge between two vertices of the same colour (%d edges) and keep the colouring: that prover was caught in %.4f of rounds, about 1/%d ; %s%n",
                v, E - 1, honestRounds, pj, E, perRound, E, cj);

        System.out.println("ZeroKnowledge: " + passed + " checks passed");
    }
}
