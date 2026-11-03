import java.util.*;

/**
 * Era 9, topic 8: Monte Carlo tree search (Abramson 1987, Brugmann 1992, Coulom 2006, Kocsis and Szepesvari 2006),
 * the search inside AlphaGo (DeepMind, 2016).
 *
 * HOW IT WORKS
 *   To judge a position without any knowledge of the game, play it out to the end with random moves, many times,
 *   and count the wins. Monte Carlo tree search grows a tree of positions from such playouts. Each round has four
 *   steps:
 *     selection       from the root, repeatedly choose the child with the largest UCB1 score
 *                       wins/visits + c * sqrt(ln(parent visits) / visits)
 *                     a high win rate attracts the search, and so does having been tried only a few times;
 *     expansion       add one untried move as a new node;
 *     simulation      play randomly from there to the end of the game;
 *     backpropagation add the result to every node on the path.
 *   The move played is the root's most visited child. With more rounds UCT's choice converges to the best move.
 *   AlphaGo replaced the uniform choice of new moves with a policy network's probabilities and the random playouts
 *   partly with a value network; this program uses no networks, only a hand-written prior to show the idea.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Solves tic-tac-toe exactly (minimax over every position) and asks UCT for a move in 600 random positions,
 *      with 30, 300 and 3,000 rounds: how often is its move one of the best?
 *   2. Plays Connect Four: UCT against random moves, and UCT with 4 times as many rounds against UCT.
 *   3. A prior that prefers central columns (a stand-in for AlphaGo's policy network) against plain UCT with the
 *      same number of rounds.
 *   4. The root's visit counts and win rates in one Connect Four position, for the page.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MonteCarloTreeSearch.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MonteCarloTreeSearch {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    /** A two-player game with alternating moves. Players are 1 and 2; winner() is 0 while undecided, 3 for a draw. */
    interface Game {
        Game copy();
        int toMove();
        int[] moves();
        void play(int m);
        int winner();
    }

    // ---- tic-tac-toe ----------------------------------------------------------------------------------------------------
    static class TTT implements Game {
        int[] b = new int[9]; int turn = 1, n = 0;
        static final int[][] L = {{0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {0, 3, 6}, {1, 4, 7}, {2, 5, 8}, {0, 4, 8}, {2, 4, 6}};

        public TTT copy() { TTT t = new TTT(); t.b = b.clone(); t.turn = turn; t.n = n; return t; }
        public int toMove() { return turn; }
        public int[] moves() { int[] m = new int[9 - n]; int k = 0; for (int i = 0; i < 9; i++) if (b[i] == 0) m[k++] = i; return m; }
        public void play(int m) { b[m] = turn; turn = 3 - turn; n++; }
        public int winner() {
            for (int[] l : L) if (b[l[0]] != 0 && b[l[0]] == b[l[1]] && b[l[1]] == b[l[2]]) return b[l[0]];
            return n == 9 ? 3 : 0;
        }
        int key() { int k = 0; for (int x : b) k = k * 3 + x; return k; }
    }

    static Map<Integer, Integer> memo = new HashMap<>();

    /** Exact value for the player to move: +1 win, 0 draw, -1 loss. */
    static int solve(TTT t) {
        int w = t.winner();
        if (w == 3) return 0;
        if (w != 0) return w == t.turn ? 1 : -1;
        Integer c = memo.get(t.key());
        if (c != null) return c;
        int best = -2;
        for (int m : t.moves()) { TTT u = t.copy(); u.play(m); best = Math.max(best, -solve(u)); }
        memo.put(t.key(), best);
        return best;
    }

    // ---- Connect Four, 7 columns by 6 rows ------------------------------------------------------------------------------
    static class C4 implements Game {
        int[] b = new int[42]; int[] h = new int[7]; int turn = 1, n = 0, last = -1;

        public C4 copy() { C4 c = new C4(); c.b = b.clone(); c.h = h.clone(); c.turn = turn; c.n = n; c.last = last; return c; }
        public int toMove() { return turn; }
        public int[] moves() { int k = 0; for (int c = 0; c < 7; c++) if (h[c] < 6) k++; int[] m = new int[k]; k = 0; for (int c = 0; c < 7; c++) if (h[c] < 6) m[k++] = c; return m; }
        public void play(int c) { last = h[c] * 7 + c; b[last] = turn; h[c]++; turn = 3 - turn; n++; }
        public int winner() {
            if (last < 0) return 0;
            int p = b[last], r = last / 7, c = last % 7;
            int[][] dirs = {{0, 1}, {1, 0}, {1, 1}, {1, -1}};
            for (int[] d : dirs) {
                int cnt = 1;
                for (int s = -1; s <= 1; s += 2) {
                    int rr = r + s * d[0], cc = c + s * d[1];
                    while (rr >= 0 && rr < 6 && cc >= 0 && cc < 7 && b[rr * 7 + cc] == p) { cnt++; rr += s * d[0]; cc += s * d[1]; }
                }
                if (cnt >= 4) return p;
            }
            return n == 42 ? 3 : 0;
        }
    }

    // ---- the search -------------------------------------------------------------------------------------------------------
    static class Node {
        final int move, mover; // the move that led here, and who made it
        final Node parent;
        final List<Node> kids = new ArrayList<>();
        int[] untried;
        int nu; // number of untried moves left
        double wins; int visits;
        double prior = 1;

        Node(Node parent, int move, int mover, Game g) {
            this.parent = parent; this.move = move; this.mover = mover;
            untried = g.winner() == 0 ? g.moves() : new int[0];
            nu = untried.length;
        }
    }

    static final double C = Math.sqrt(2);

    /** Returns the root after the given number of rounds. prior != null switches to AlphaGo-style selection with it. */
    static Node search(Game root, int rounds, Random r, double[] prior) {
        Node top = new Node(null, -1, 3 - root.toMove(), root);
        for (int it = 0; it < rounds; it++) {
            Node n = top; Game g = root.copy();
            // 1. selection
            while (n.nu == 0 && !n.kids.isEmpty()) {
                Node best = null; double bs = -1e18;
                for (Node k : n.kids) {
                    double s = prior == null
                            ? k.wins / k.visits + C * Math.sqrt(Math.log(n.visits) / k.visits)
                            : k.wins / k.visits + 1.5 * k.prior * Math.sqrt(n.visits) / (1 + k.visits);
                    if (s > bs) { bs = s; best = k; }
                }
                n = best; g.play(n.move);
            }
            // 2. expansion: a random untried move, or with a prior, the untried move the prior likes most
            if (n.nu > 0) {
                int i;
                if (prior == null) i = r.nextInt(n.nu);
                else { i = 0; for (int j = 1; j < n.nu; j++) if (prior[n.untried[j]] > prior[n.untried[i]]) i = j; }
                int m = n.untried[i]; n.untried[i] = n.untried[--n.nu];
                int mover = g.toMove();
                g.play(m);
                Node k = new Node(n, m, mover, g);
                if (prior != null) k.prior = prior[m];
                n.kids.add(k); n = k;
            }
            // 3. simulation
            int w;
            while ((w = g.winner()) == 0) { int[] ms = g.moves(); g.play(ms[r.nextInt(ms.length)]); }
            // 4. backpropagation
            for (Node a = n; a != null; a = a.parent) { a.visits++; a.wins += w == 3 ? 0.5 : (w == a.mover ? 1 : 0); }
        }
        return top;
    }

    static int bestMove(Node root) {
        Node b = null;
        for (Node k : root.kids) if (b == null || k.visits > b.visits) b = k;
        return b.move;
    }

    /** Plays one game; returns the winner (1, 2 or 3 for a draw). rounds <= 0 means random moves. */
    static int match(int rounds1, double[] prior1, int rounds2, double[] prior2, Random r) {
        C4 g = new C4();
        while (g.winner() == 0) {
            int rounds = g.turn == 1 ? rounds1 : rounds2;
            double[] pr = g.turn == 1 ? prior1 : prior2;
            int m;
            if (rounds <= 0) { int[] ms = g.moves(); m = ms[r.nextInt(ms.length)]; }
            else m = bestMove(search(g, rounds, r, pr));
            g.play(m);
        }
        return g.winner();
    }

    /** A wins, draws, B wins over games with each side moving first in half of them. */
    static int[] series(int games, int rA, double[] pA, int rB, double[] pB, long seed) {
        Random r = new Random(seed);
        int[] res = new int[3];
        for (int k = 0; k < games; k++) {
            boolean aFirst = k % 2 == 0;
            int w = aFirst ? match(rA, pA, rB, pB, r) : match(rB, pB, rA, pA, r);
            if (w == 3) res[1]++;
            else if ((w == 1) == aFirst) res[0]++;
            else res[2]++;
        }
        return res;
    }

    public static void main(String[] args) {
        // ---- 1. tic-tac-toe against the exact answer -----------------------------------------------------------------
        TTT empty = new TTT();
        check(solve(empty) == 0, "tic-tac-toe is a draw with best play");
        // every position reachable in play that is not over
        List<TTT> all = new ArrayList<>();
        Set<Integer> seen = new HashSet<>();
        Deque<TTT> q = new ArrayDeque<>(List.of(empty));
        while (!q.isEmpty()) {
            TTT t = q.poll();
            if (!seen.add(t.key()) || t.winner() != 0) continue;
            all.add(t);
            for (int m : t.moves()) { TTT u = t.copy(); u.play(m); q.add(u); }
        }
        Random r = new Random(8);
        Collections.shuffle(all, r);
        List<TTT> sample = all.subList(0, 600);
        // positions where some moves are worse than others are the real test
        int hard = 0;
        for (TTT t : sample) {
            Set<Integer> vals = new HashSet<>();
            for (int m : t.moves()) { TTT u = t.copy(); u.play(m); vals.add(-solve(u)); }
            if (vals.size() > 1) hard++;
        }
        StringJoiner tj = new StringJoiner(" ; ");
        int[] budgets = {30, 300, 3000};
        double[] rate = new double[3];
        for (int bi = 0; bi < 3; bi++) {
            int ok = 0, okHard = 0;
            for (TTT t : sample) {
                int v = solve(t);
                int m = bestMove(search(t, budgets[bi], r, null));
                TTT u = t.copy(); u.play(m);
                boolean good = -solve(u) == v;
                if (good) ok++;
                Set<Integer> vals = new HashSet<>();
                for (int mm : t.moves()) { TTT w = t.copy(); w.play(mm); vals.add(-solve(w)); }
                if (good && vals.size() > 1) okHard++;
            }
            rate[bi] = (double) okHard / hard;
            tj.add(String.format("%,d rounds: a best move in %d of %d (%d of %d where a wrong move exists)", budgets[bi], ok, sample.size(), okHard, hard));
        }
        check(rate[2] > rate[0] && rate[2] > 0.97, "with 3,000 rounds UCT nearly always finds a best move");
        System.out.printf("tictactoe: solved exactly, %,d positions in play, the empty board is a draw ; UCT on %d random positions ; %s%n",
                all.size(), sample.size(), tj);

        // ---- 2. Connect Four -------------------------------------------------------------------------------------------
        int[] vr = series(40, 200, null, 0, null, 11);
        check(vr[0] >= 38, "UCT with 200 rounds beats random moves");
        int[] vs = series(60, 2000, null, 500, null, 12);
        check(vs[0] > vs[2], "4 times the rounds wins more");
        System.out.printf("connect4: 7 columns, 6 rows, each side first in half the games ; UCT 200 rounds against random moves: %d wins, %d draws, %d losses ; UCT 2,000 rounds against UCT 500: %d wins, %d draws, %d losses%n",
                vr[0], vr[1], vr[2], vs[0], vs[1], vs[2]);

        // ---- 3. a prior ----------------------------------------------------------------------------------------------------
        double[] prior = {1 / 16.0, 2 / 16.0, 3 / 16.0, 4 / 16.0, 3 / 16.0, 2 / 16.0, 1 / 16.0};
        int[] vp = series(60, 500, prior, 500, null, 13);
        check(vp[0] > vp[2], "the prior helps at an equal number of rounds");
        System.out.printf("prior: a prior of 1, 2, 3, 4, 3, 2, 1 (out of 16) over the columns, centre first, selection by win rate + 1.5 * prior * sqrt(parent visits) / (1 + visits) ; with prior, 500 rounds, against plain UCT, 500 rounds: %d wins, %d draws, %d losses%n",
                vp[0], vp[1], vp[2]);

        // ---- 4. one position, for the page ------------------------------------------------------------------------------------
        C4 g = new C4();
        for (int c : new int[]{3, 3, 2, 4, 2}) g.play(c);
        Node root = search(g, 5000, new Random(14), null);
        StringJoiner rj = new StringJoiner(" ; ");
        int tot = 0;
        for (Node k : root.kids) tot += k.visits;
        root.kids.sort(Comparator.comparingInt(k -> k.move));
        for (Node k : root.kids) rj.add(String.format("column %d: %d visits, wins %.0f%%", k.move + 1, k.visits, 100 * k.wins / k.visits));
        check(tot == 5000, "every round passes through exactly one child of the root");
        int bm = bestMove(root);
        System.out.printf("position: moves 4, 4, 3, 5, 3 (columns, 1 to 7, Red first) ; Yellow to move ; UCT 5,000 rounds ; %s ; chosen: column %d%n", rj, bm + 1);

        System.out.println("MonteCarloTreeSearch: " + passed + " checks passed");
    }
}
