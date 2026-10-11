import java.util.*;

/**
 * Era 4, topic 8: breaking Enigma (Rejewski 1932, the Bombe 1940).
 *
 * HOW IT WORKS
 *   An Enigma sends each key press through a plugboard (which swaps some pairs of letters), three wired rotors, a
 *   reflector, and back through the rotors and plugboard. The rightmost rotor turns before every letter, and turns the
 *   next one at its notch, so the scrambling changes with every letter. Because of the reflector, the machine's
 *   letter swaps are their own inverse (typing the cipher text gives back the plain text) and no letter is ever
 *   enciphered as itself.
 *   Rejewski's attack (1932-1938): operators sent each message's three-letter key twice. If A, B, ..., F are the
 *   machine's swaps at positions 1 to 6, the first and fourth cipher letters are linked by the product of A and D,
 *   which every day's traffic reveals. The lengths of its cycles come in pairs and do not depend on the plugboard
 *   (the "characteristic"), so a catalogue of characteristics for every rotor order and position points to the
 *   day's setting.
 *   Turing's Bombe (1940): guess a stretch of plain text (a "crib"). For each rotor position, assume a plug partner
 *   for one letter and follow what the crib then forces; a contradiction (one letter plugged to two others) rules the
 *   position out. Positions with no contradiction are "stops", checked by hand.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Builds the Enigma I with the rotor wirings of 1930 and checks the published test (AAAAA gives BDZGO).
 *   2. Checks that enciphering twice gives back the message, and that no letter goes to itself at any position.
 *   3. Rejewski's characteristic: cycles in pairs for all 105,456 settings, the same with any plugboard; the
 *      catalogue; and a simulated day's traffic in which the catalogue finds the setting.
 *   4. A Bombe run on a 23-letter crib over all 6 rotor orders and 17,576 positions: the stops, and the plugs deduced.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Enigma.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Enigma {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final String[] ROTOR = {"EKMFLGDQVZNTOWYHXUSPAIBRCJ", "AJDKSIRUXBLHWTMCQGZNPYFVOE", "BDFHJLCPRTXVZNYEIWGAKMUSQO"};
    static final char[] NOTCH = {'Q', 'E', 'V'};
    static final String REFLECTOR_A = "EJMZALYXVBWFCRQUONTSPIKHGD", REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT";
    static final int[][] FWD = new int[3][26], BWD = new int[3][26];

    static {
        for (int r = 0; r < 3; r++)
            for (int i = 0; i < 26; i++) {
                FWD[r][i] = ROTOR[r].charAt(i) - 'A';
                BWD[r][ROTOR[r].charAt(i) - 'A'] = i;
            }
    }

    /** Rotor order (left, middle, right) as rotor numbers 0..2, positions 0..25, ring settings all A. */
    static final class Machine {
        final int[] order, pos = new int[3], plug = new int[26], refl = new int[26];
        Machine(int[] order, int[] start, String reflector, int[] plugboard) {
            this.order = order.clone();
            System.arraycopy(start, 0, pos, 0, 3);
            for (int i = 0; i < 26; i++) { refl[i] = reflector.charAt(i) - 'A'; plug[i] = plugboard == null ? i : plugboard[i]; }
        }
        void step() {
            boolean midAtNotch = pos[1] == NOTCH[order[1]] - 'A';
            boolean rightAtNotch = pos[2] == NOTCH[order[2]] - 'A';
            if (midAtNotch) { pos[0] = (pos[0] + 1) % 26; pos[1] = (pos[1] + 1) % 26; }   // the double step
            else if (rightAtNotch) pos[1] = (pos[1] + 1) % 26;
            pos[2] = (pos[2] + 1) % 26;
        }
        /** The scrambler alone (rotors and reflector) at the current position. */
        int scramble(int c) {
            for (int k = 2; k >= 0; k--) c = (FWD[order[k]][(c + pos[k]) % 26] - pos[k] + 26) % 26;
            c = refl[c];
            for (int k = 0; k <= 2; k++) c = (BWD[order[k]][(c + pos[k]) % 26] - pos[k] + 26) % 26;
            return c;
        }
        int press(int c) { step(); return plug[scramble(plug[c])]; }
        String type(String s) {
            StringBuilder sb = new StringBuilder();
            for (char ch : s.toCharArray()) sb.append((char) ('A' + press(ch - 'A')));
            return sb.toString();
        }
        /** The full swap (with plugboard) at the next k key presses, without moving the machine. */
        int[][] next(int k) {
            int[] saved = pos.clone();
            int[][] out = new int[k][26];
            for (int i = 0; i < k; i++) {
                step();
                for (int c = 0; c < 26; c++) out[i][c] = plug[scramble(plug[c])];
            }
            System.arraycopy(saved, 0, pos, 0, 3);
            return out;
        }
    }

    static final int[][] ORDERS = {{0, 1, 2}, {0, 2, 1}, {1, 0, 2}, {1, 2, 0}, {2, 0, 1}, {2, 1, 0}};

    static long seed = 1932L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) Long.remainderUnsigned(seed >>> 33, n);
    }

    static int[] randomPlugboard(int pairs) {
        int[] p = new int[26];
        for (int i = 0; i < 26; i++) p[i] = i;
        List<Integer> free = new ArrayList<>();
        for (int i = 0; i < 26; i++) free.add(i);
        for (int k = 0; k < pairs; k++) {
            int a = free.remove(rnd(free.size())), b = free.remove(rnd(free.size()));
            p[a] = b; p[b] = a;
        }
        return p;
    }

    /** Sorted cycle lengths of the permutation x -> second(first(x)). */
    static List<Integer> cycles(int[] first, int[] second) {
        boolean[] seen = new boolean[26];
        List<Integer> out = new ArrayList<>();
        for (int s = 0; s < 26; s++) {
            if (seen[s]) continue;
            int len = 0;
            for (int x = s; !seen[x]; x = second[first[x]]) { seen[x] = true; len++; }
            out.add(len);
        }
        Collections.sort(out, Collections.reverseOrder());
        return out;
    }

    static boolean pairsUp(List<Integer> c) {
        Map<Integer, Integer> count = new HashMap<>();
        for (int x : c) count.merge(x, 1, Integer::sum);
        for (int v : count.values()) if (v % 2 != 0) return false;
        return true;
    }

    static String characteristic(int[][] six) {
        return cycles(six[0], six[3]) + "" + cycles(six[1], six[4]) + cycles(six[2], six[5]);
    }

    static String letters(int[] p) {
        StringBuilder sb = new StringBuilder();
        for (int x : p) sb.append((char) ('A' + x));
        return sb.toString();
    }

    public static void main(String[] args) {
        // ---- 1. the published test -----------------------------------------------------------------------------------
        Machine m = new Machine(new int[]{0, 1, 2}, new int[]{0, 0, 0}, REFLECTOR_B, null);
        String out = m.type("AAAAA");
        check(out.equals("BDZGO"), "AAAAA gives BDZGO");
        System.out.printf("test: rotors I, II, III, reflector B, rings A, start AAA: AAAAA becomes %s%n", out);

        // ---- 2. enciphering twice gives back the message; no letter goes to itself ------------------------------------
        int trials = 1000;
        for (int t = 0; t < trials; t++) {
            int[] order = ORDERS[rnd(6)], start = {rnd(26), rnd(26), rnd(26)}, plug = randomPlugboard(10);
            StringBuilder msg = new StringBuilder();
            for (int i = 0; i < 60; i++) msg.append((char) ('A' + rnd(26)));
            String c = new Machine(order, start, REFLECTOR_B, plug).type(msg.toString());
            String back = new Machine(order, start, REFLECTOR_B, plug).type(c);
            check(back.equals(msg.toString()), "typing the cipher text gives the message back");
            for (int i = 0; i < 60; i++) check(c.charAt(i) != msg.charAt(i), "no letter becomes itself");
        }
        long fixedChecks = 0;
        for (int p = 0; p < 26 * 26 * 26; p++) {
            Machine mm = new Machine(ORDERS[0], new int[]{p / 676, p / 26 % 26, p % 26}, REFLECTOR_B, null);
            for (int c = 0; c < 26; c++) { check(mm.scramble(c) != c, "no fixed point"); fixedChecks++; }
        }
        System.out.printf("self: %d random 60-letter messages, enciphered and enciphered again, came back unchanged, and no letter was ever enciphered as itself ; at all 17576 positions of rotors I-II-III, none of the 26 letters goes to itself (%d cases)%n",
                trials, fixedChecks);

        // ---- 3. Rejewski's characteristic and catalogue (reflector A, as before November 1937) ----------------------
        Map<String, List<int[]>> catalogue = new HashMap<>();
        long pairedProducts = 0;
        for (int o = 0; o < 6; o++)
            for (int p = 0; p < 17576; p++) {
                int[] start = {p / 676, p / 26 % 26, p % 26};
                int[][] six = new Machine(ORDERS[o], start, REFLECTOR_A, null).next(6);
                for (int k = 0; k < 3; k++) { check(pairsUp(cycles(six[k], six[k + 3])), "cycles come in pairs"); pairedProducts++; }
                catalogue.computeIfAbsent(characteristic(six), z -> new ArrayList<>()).add(new int[]{o, p});
            }
        int settings = 6 * 17576, distinct = catalogue.size(), unique = 0, largest = 0;
        for (List<int[]> v : catalogue.values()) { if (v.size() == 1) unique++; largest = Math.max(largest, v.size()); }
        // the plugboard changes the letters in the cycles, never their lengths
        for (int t = 0; t < 1000; t++) {
            int o = rnd(6);
            int[] start = {rnd(26), rnd(26), rnd(26)};
            int[][] bare = new Machine(ORDERS[o], start, REFLECTOR_A, null).next(6);
            int[][] plugged = new Machine(ORDERS[o], start, REFLECTOR_A, randomPlugboard(6)).next(6);
            check(characteristic(bare).equals(characteristic(plugged)), "the plugboard does not change the characteristic");
        }
        System.out.printf("catalogue: %d settings (6 rotor orders x 17576 positions), reflector A ; the products AD, BE, CF have cycles in pairs every time (%d products) ; %d different characteristics, %d of them belonging to a single setting, at most %d settings sharing one ; with 1000 random plugboards of 6 cables the characteristic never changed%n",
                settings, pairedProducts, distinct, unique, largest);

        // a simulated day: a secret setting and plugboard, and the doubled keys of the day's messages
        int dayOrder = rnd(6);
        int[] dayStart = {rnd(26), rnd(26), rnd(26)};
        int[] dayPlug = randomPlugboard(6);
        int[][] perm = new int[3][26];
        for (int[] row : perm) Arrays.fill(row, -1);
        int messages = 0, filled = 0;
        while (filled < 78) {
            String key = "" + (char) ('A' + rnd(26)) + (char) ('A' + rnd(26)) + (char) ('A' + rnd(26));
            String ind = new Machine(ORDERS[dayOrder], dayStart, REFLECTOR_A, dayPlug).type(key + key);
            messages++;
            for (int k = 0; k < 3; k++) {
                int a = ind.charAt(k) - 'A', b = ind.charAt(k + 3) - 'A';
                if (perm[k][a] < 0) { perm[k][a] = b; filled++; }
                check(perm[k][a] == b, "the indicators are consistent");
            }
        }
        // the products read off the indicators, as Rejewski did: first letter -> fourth letter
        int[] id = new int[26];
        for (int i = 0; i < 26; i++) id[i] = i;
        String observed = cycles(id, perm[0]) + "" + cycles(id, perm[1]) + cycles(id, perm[2]);
        List<int[]> candidates = catalogue.getOrDefault(observed, List.of());
        int dayP = dayStart[0] * 676 + dayStart[1] * 26 + dayStart[2];
        boolean found = candidates.stream().anyMatch(c -> c[0] == dayOrder && c[1] == dayP);
        check(found, "the catalogue contains the day's setting");
        System.out.printf("day: %d intercepted indicators fixed all three products ; their cycle lengths %s ; the catalogue lists %d setting%s with this characteristic, among them the true one%n",
                messages, cycles(id, perm[0]), candidates.size(), candidates.size() == 1 ? "" : "s");

        // ---- 4. a Bombe run on a crib (reflector B, 10 plug cables, as in 1940) --------------------------------------
        int bOrder = rnd(6);
        int[] bStart = {rnd(26), rnd(26), rnd(26)};
        int[] bPlug = randomPlugboard(10);
        String crib = "WETTERVORHERSAGEBISKAYA";
        String cipher = new Machine(ORDERS[bOrder], bStart, REFLECTOR_B, bPlug).type(crib);
        int L = crib.length();
        // the test letter: the letter that appears most often in the crib and its cipher text together
        int[] freq = new int[26];
        for (int i = 0; i < L; i++) { freq[crib.charAt(i) - 'A']++; freq[cipher.charAt(i) - 'A']++; }
        int test = 0;
        for (int c = 1; c < 26; c++) if (freq[c] > freq[test]) test = c;
        long stops = 0, positionsTested = 0;
        boolean trueStop = false;
        int[] deduced = null;
        for (int o = 0; o < 6; o++)
            for (int p = 0; p < 17576; p++) {
                positionsTested++;
                int[] start = {p / 676, p / 26 % 26, p % 26};
                Machine mm = new Machine(ORDERS[o], start, REFLECTOR_B, null);
                int[][] sc = new int[L][26];
                for (int i = 0; i < L; i++) { mm.step(); for (int c = 0; c < 26; c++) sc[i][c] = mm.scramble(c); }
                for (int h = 0; h < 26; h++) {
                    int[] partner = new int[26];
                    Arrays.fill(partner, -1);
                    boolean ok = assign(partner, test, h);
                    // follow the crib: plain letter x at i with partner a means cipher letter y has partner sc[i][a]
                    boolean changed = true;
                    while (ok && changed) {
                        changed = false;
                        for (int i = 0; i < L && ok; i++) {
                            int x = crib.charAt(i) - 'A', y = cipher.charAt(i) - 'A';
                            if (partner[x] >= 0 && partner[y] < 0) { ok = assign(partner, y, sc[i][partner[x]]); changed = true; }
                            else if (partner[y] >= 0 && partner[x] < 0) { ok = assign(partner, x, sc[i][partner[y]]); changed = true; }
                            else if (partner[x] >= 0 && partner[y] >= 0 && sc[i][partner[x]] != partner[y]) ok = false;
                        }
                    }
                    if (ok) {
                        stops++;
                        if (o == bOrder && p == bStart[0] * 676 + bStart[1] * 26 + bStart[2] && h == bPlug[test]) { trueStop = true; deduced = partner; }
                    }
                }
            }
        check(trueStop, "the true setting is a stop");
        int known = 0, right = 0;
        for (int c = 0; c < 26; c++) if (deduced[c] >= 0) { known++; if (deduced[c] == bPlug[c]) right++; }
        check(known == right, "every deduced plug is right");
        System.out.printf("bombe: crib %s under cipher %s ; test letter %c ; %d rotor positions x 26 guesses tested ; %d stop%s, the true setting among them ; at the true stop the crib forces the plug partners of %d letters, all correct%n",
                crib, cipher, (char) ('A' + test), positionsTested, stops, stops == 1 ? " survives" : "s survive", known);

        System.out.println("Enigma: " + passed + " checks passed");
    }

    /** Record that a and b are plugged together; false if either already has a different partner. */
    static boolean assign(int[] partner, int a, int b) {
        if (partner[a] >= 0 && partner[a] != b) return false;
        if (partner[b] >= 0 && partner[b] != a) return false;
        partner[a] = b;
        partner[b] = a;
        return true;
    }
}
