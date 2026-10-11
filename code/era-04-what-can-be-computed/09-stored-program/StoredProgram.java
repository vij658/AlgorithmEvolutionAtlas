import java.util.*;

/**
 * Era 4, topic 9: the stored program, and merge sort (1945-1948).
 *
 * HOW IT WORKS
 *   A stored-program computer keeps its instructions in the same memory as its numbers, as numbers. The Manchester
 *   "Baby" (1948) had 32 words of store and seven instructions; this program uses that instruction set:
 *       JMP s   jump to the address held in word s        JRP s   jump forward by the number held in word s
 *       LDN s   load minus the number in word s           STO s   store the accumulator in word s
 *       SUB s   subtract the number in word s             CMP     skip the next instruction if the accumulator < 0
 *       STP     stop
 *   Each instruction is a word: a function number (0 to 7) times 8192, plus an address. Because instructions are
 *   numbers, a program can do arithmetic on them: adding 1 to "LDN 100" makes it "LDN 101". The first programs
 *   stepped through lists that way, since there were no index registers.
 *   Merging takes two sorted lists and repeatedly moves the smaller front item to the output. Merge sort merges
 *   runs of length 1 into runs of 2, then 4, and so on: about n log2 n comparisons for n items.
 *
 * WHAT THIS PROGRAM DOES
 *   1. A simulator for the seven instructions, with a small assembler.
 *   2. A 16-instruction program, written for the Baby's instructions and 32-word store, that finds the highest proper
 *      factor of 2^18 by repeated subtraction, the task of the Baby's first program (21 June 1948).
 *   3. A merging program that rewrites the addresses inside its own instructions, run on a larger store.
 *   4. Merge sort's worst case for every permutation of up to 8 items, against the formula and the lower bound.
 *   5. Merge sort against insertion sort on up to a million items.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java StoredProgram.java
 *   Expected output: expected-output.txt in this folder.
 */
public class StoredProgram {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final String[] OPS = {"JMP", "JRP", "LDN", "STO", "SUB", "SUB", "CMP", "STP"};

    // ---- 1. the machine -----------------------------------------------------------------------------------------------
    static final class Machine {
        final int[] mem;
        int acc = 0, ci = 0;
        long executed = 0;
        Machine(int[] program) { mem = program.clone(); }
        /** Run until STP; return the number of instructions executed. */
        long run(long limit) {
            while (executed < limit) {
                ci++;                                                  // the address counter moves on before each fetch
                int w = mem[ci], f = (w >>> 13) & 7, s = w & 8191;
                executed++;
                switch (f) {
                    case 0 -> ci = mem[s];                             // JMP: to the address held in s
                    case 1 -> ci += mem[s];                            // JRP: forward by the number held in s
                    case 2 -> acc = -mem[s];                           // LDN
                    case 3 -> mem[s] = acc;                            // STO
                    case 4, 5 -> acc -= mem[s];                        // SUB
                    case 6 -> { if (acc < 0) ci++; }                   // CMP: skip the next instruction if negative
                    default -> { return executed; }                    // STP
                }
            }
            throw new IllegalStateException("no STP within " + limit + " instructions");
        }
    }

    /** A two-pass assembler: lines "label: OP operand" or "label: NUM expression", expressions like loop-1 or -5. */
    static Map<String, Integer> labels;

    static int[] assemble(String[] lines, int size) {
        labels = new HashMap<>();
        for (int a = 0; a < lines.length; a++) {
            String ln = lines[a].trim();
            if (ln.contains(":")) labels.put(ln.substring(0, ln.indexOf(':')).trim(), a);
        }
        int[] mem = new int[size];
        for (int a = 0; a < lines.length; a++) {
            String ln = lines[a].trim();
            if (ln.contains(":")) ln = ln.substring(ln.indexOf(':') + 1).trim();
            String[] p = ln.split("\\s+");
            if (p[0].equals("NUM")) { mem[a] = eval(p[1]); continue; }
            int f = Arrays.asList(OPS).indexOf(p[0]);
            mem[a] = f * 8192 + (p.length > 1 ? eval(p[1]) : 0);
        }
        return mem;
    }

    static int eval(String e) {
        int total = 0, sign = 1, i = 0;
        if (e.startsWith("-")) { sign = -1; i = 1; }
        StringBuilder tok = new StringBuilder();
        for (; i <= e.length(); i++) {
            if (i == e.length() || e.charAt(i) == '+' || e.charAt(i) == '-') {
                String t = tok.toString();
                total += sign * (t.chars().allMatch(Character::isDigit) ? Integer.parseInt(t) : labels.get(t));
                if (i < e.length()) sign = e.charAt(i) == '+' ? 1 : -1;
                tok.setLength(0);
            } else tok.append(e.charAt(i));
        }
        return total;
    }

    static String word(int w) {
        int f = (w >>> 13) & 7;
        return OPS[f] + (f == 6 || f == 7 ? "" : " " + (w & 8191));
    }

    // ---- 4 and 5. merge sort, counting comparisons -------------------------------------------------------------------
    static long comparisons, inversions;

    static void mergeSort(int[] a, int[] tmp, int lo, int hi) {           // sorts a[lo, hi)
        if (hi - lo < 2) return;
        int mid = (lo + hi) >>> 1;
        mergeSort(a, tmp, lo, mid);
        mergeSort(a, tmp, mid, hi);
        int i = lo, j = mid, k = lo;
        while (i < mid && j < hi) {
            comparisons++;
            if (a[i] <= a[j]) tmp[k++] = a[i++];
            else { tmp[k++] = a[j++]; inversions += mid - i; }              // a[j] jumps over the mid - i items left
        }
        while (i < mid) tmp[k++] = a[i++];
        while (j < hi) tmp[k++] = a[j++];
        System.arraycopy(tmp, lo, a, lo, hi - lo);
    }

    static long insertionShifts(int[] a) {
        long shifts = 0;
        for (int i = 1; i < a.length; i++) {
            int x = a[i], j = i - 1;
            while (j >= 0 && a[j] > x) { a[j + 1] = a[j]; j--; shifts++; }
            a[j + 1] = x;
        }
        return shifts;
    }

    static long seed = 1945L;

    static int rnd(int n) {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (int) Long.remainderUnsigned(seed >>> 33, n);
    }

    static boolean nextPermutation(int[] p) {
        int i = p.length - 2;
        while (i >= 0 && p[i] >= p[i + 1]) i--;
        if (i < 0) return false;
        int j = p.length - 1;
        while (p[j] <= p[i]) j--;
        int t = p[i]; p[i] = p[j]; p[j] = t;
        for (int a = i + 1, b = p.length - 1; a < b; a++, b--) { t = p[a]; p[a] = p[b]; p[b] = t; }
        return true;
    }

    public static void main(String[] args) {
        // ---- 2. the highest proper factor of 2^18, in 32 words ------------------------------------------------------------
        int N = 1 << 18;
        String[] factor = {
                "start: NUM 0",
                "outer: LDN b",           // A = -b
                "STO t",
                "LDN t",                  // A = b
                "SUB one",                // A = b - 1
                "STO b",                  // try the next smaller divisor
                "LDN negN",               // A = N
                "inner: SUB b",           // subtract b until the accumulator goes negative
                "CMP",
                "back: JRP rel",          // not yet negative: back to inner
                "STO t",                  // t = remainder - b
                "LDN t",                  // A = b - remainder
                "SUB b",                  // A = -remainder
                "CMP",                    // remainder > 0: skip the next line
                "JMP foundp",             // remainder = 0: b divides N
                "JMP outerp",
                "found: STP",
                "b: NUM " + N,
                "t: NUM 0",
                "one: NUM 1",
                "negN: NUM -" + N,
                "rel: NUM inner-back-1",
                "foundp: NUM found-1",
                "outerp: NUM outer-1",
        };
        int[] prog = assemble(factor, 32);
        check(factor.length <= 32, "fits in the Baby's 32 words");
        Machine baby = new Machine(prog);
        long steps = baby.run(100_000_000L);
        int answer = baby.mem[labels.get("b")];
        check(answer == N / 2, "the highest proper factor of 2^18 is 2^17");
        int instructions = labels.get("found") - labels.get("outer") + 1;
        System.out.printf("baby: highest proper factor of 2^18 = %d by repeated subtraction: %d ; a program of %d instructions and %d words of data in a store of 32 words ; %d instructions executed%n",
                N, answer, instructions, factor.length - instructions - 1, steps);

        // ---- 3. a merging program that rewrites its own addresses ---------------------------------------------------------
        int[] runA = new int[8], runB = new int[8];
        for (int i = 0; i < 8; i++) { runA[i] = rnd(1000); runB[i] = rnd(1000); }
        Arrays.sort(runA);
        Arrays.sort(runB);
        List<String> mp = new ArrayList<>(List.of(
                "start: NUM 0",
                "LB: LDN B0",             // A = -b      (the address in this word is rewritten)
                "STO mb",
                "LA: LDN A0",             // A = -a      (and this one)
                "STO ma",
                "SUB mb",                 // A = b - a
                "CMP",                    // b < a: skip the next line and take b
                "JMP takeAp",             // b >= a: take a (equal keys keep their order)
                "LDN LB",                 // take b: add 1 to the address inside instruction LB
                "SUB one",
                "STO tmp",
                "LDN tmp",
                "STO LB",
                "LDN mb",                 // A = b
                "JMP storep",
                "takeA: LDN LA",          // take a: add 1 to the address inside instruction LA
                "SUB one",
                "STO tmp",
                "LDN tmp",
                "STO LA",
                "LDN ma",                 // A = a
                "SC: STO C0",             // write the item (the address in this word is rewritten too)
                "LDN SC",
                "SUB one",
                "STO tmp",
                "LDN tmp",
                "STO SC",
                "LDN cnt",                // count down the items still to write
                "SUB negone",
                "STO tmp",
                "LDN tmp",
                "STO cnt",
                "SUB one",
                "CMP",                    // none left: skip the jump and stop
                "JMP loopp",
                "STP",
                "mb: NUM 0", "ma: NUM 0", "tmp: NUM 0", "one: NUM 1", "negone: NUM -1", "cnt: NUM 16",
                "takeAp: NUM takeA-1", "storep: NUM SC-1", "loopp: NUM LB-1"));
        int progLen = mp.indexOf("STP");                                   // lines 1 .. STP are instructions
        for (int i = 0; i < 9; i++) mp.add((i == 0 ? "A0: " : "") + "NUM " + (i < 8 ? runA[i] : 1_000_000));
        for (int i = 0; i < 9; i++) mp.add((i == 0 ? "B0: " : "") + "NUM " + (i < 8 ? runB[i] : 1_000_000));
        for (int i = 0; i < 16; i++) mp.add((i == 0 ? "C0: " : "") + "NUM 0");
        int[] mem = assemble(mp.toArray(new String[0]), 256);
        int la0 = mem[labels.get("LA")], lb0 = mem[labels.get("LB")], sc0 = mem[labels.get("SC")];
        Machine merger = new Machine(mem);
        long mergeSteps = merger.run(100_000);
        int c0 = labels.get("C0");
        int[] got = Arrays.copyOfRange(merger.mem, c0, c0 + 16);
        int[] want = new int[16];
        System.arraycopy(runA, 0, want, 0, 8);
        System.arraycopy(runB, 0, want, 8, 8);
        Arrays.sort(want);
        check(Arrays.equals(got, want), "the machine merged the two runs");
        check(merger.mem[labels.get("SC")] == sc0 + 16, "the store instruction now points 16 words further on");
        check(merger.mem[labels.get("LA")] + merger.mem[labels.get("LB")] == la0 + lb0 + 16, "the two load instructions moved 16 words between them");
        System.out.printf("merge: runs %s and %s ; merged by a program of %d instructions into %s ; %d instructions executed ; instruction words rewritten as it ran: LA %s -> %s, LB %s -> %s, SC %s -> %s%n",
                Arrays.toString(runA), Arrays.toString(runB), progLen, Arrays.toString(got), mergeSteps,
                word(la0), word(merger.mem[labels.get("LA")]), word(lb0), word(merger.mem[labels.get("LB")]), word(sc0), word(merger.mem[labels.get("SC")]));

        // ---- 4. the worst case, over every permutation -------------------------------------------------------------------
        StringJoiner worst = new StringJoiner(", "), formula = new StringJoiner(", "), lower = new StringJoiner(", ");
        for (int n = 1; n <= 8; n++) {
            int[] p = new int[n];
            for (int i = 0; i < n; i++) p[i] = i;
            long max = 0;
            do {
                int[] a = p.clone();
                comparisons = 0;
                mergeSort(a, new int[n], 0, n);
                for (int i = 0; i < n; i++) check(a[i] == i, "sorted");
                max = Math.max(max, comparisons);
            } while (nextPermutation(p));
            int lg = 0;
            while ((1 << lg) < n) lg++;
            long f = (long) n * lg - (1L << lg) + 1;
            check(max == f, "worst case equals n ceil(lg n) - 2^ceil(lg n) + 1 for n = " + n);
            double lf = 0;
            for (int i = 2; i <= n; i++) lf += Math.log(i) / Math.log(2);
            long lb = (long) Math.ceil(lf - 1e-9);
            check(max >= lb, "no sort beats the lower bound");
            worst.add(String.valueOf(max));
            formula.add(String.valueOf(f));
            lower.add(String.valueOf(lb));
        }
        System.out.printf("worst: merge sort's most comparisons over all permutations of n = 1 to 8 items: %s ; the formula n*ceil(lg n) - 2^ceil(lg n) + 1 gives %s ; no comparison sort can need fewer than ceil(lg n!) = %s%n",
                worst, formula, lower);

        // ---- 5. merge sort against insertion sort -------------------------------------------------------------------------
        StringJoiner scale = new StringJoiner(" ; ");
        for (int n : new int[]{1_000, 10_000, 100_000, 1_000_000}) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = rnd(1 << 30);
            int[] copy = a.clone();
            comparisons = 0;
            inversions = 0;
            mergeSort(a, new int[n], 0, n);
            for (int i = 1; i < n; i++) check(a[i - 1] <= a[i], "sorted");
            if (n <= 10_000) check(insertionShifts(copy) == inversions, "insertion sort makes exactly one shift per inversion");
            scale.add(String.format("n = %d: merge sort %d comparisons (n log2 n = %.0f), insertion sort %d shifts", n, comparisons, n * Math.log(n) / Math.log(2), inversions));
        }
        System.out.printf("scale: random items ; %s ; insertion sort's shifts counted directly for n up to 10000 and as inversions (counted during the merge) beyond%n", scale);

        System.out.println("StoredProgram: " + passed + " checks passed");
    }
}
