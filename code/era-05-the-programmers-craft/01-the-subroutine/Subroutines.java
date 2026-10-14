import java.util.*;

/**
 * Era 5, topic 1: the subroutine (Cambridge, 1949-1951).
 *
 * HOW IT WORKS
 *   A closed subroutine is one copy of a routine that any part of a program can jump to. The hard part is getting
 *   back: the early machines had no "return" instruction. David Wheeler's answer, on the EDSAC at Cambridge: the
 *   caller loads its own instruction word into the accumulator and jumps; since that word contains the caller's
 *   address, the subroutine can add a constant to it and get the instruction "jump back to just after the caller",
 *   which it stores in its own last word. When the routine finishes it runs into that word and goes home.
 *   This program uses a small accumulator machine of its own (not EDSAC's order code). Each instruction is one word,
 *   operation x 1000 + address:
 *       0 HLT  stop                       5 JMP a  jump to a
 *       1 LDA a  acc = word a             6 JNG a  jump to a if acc < 0
 *       2 ADD a  acc = acc + word a       7 JZR a  jump to a if acc = 0
 *       3 SUB a  acc = acc - word a       8 OUT a  print word a
 *       4 STA a  word a = acc
 *   The caller at address n writes "LDA n" (load my own word, 1000 + n) and "JMP s"; the subroutine adds 4002 and
 *   gets 5000 + n + 2, which is "JMP n+2". A routine that calls itself overwrites its own way home, so the Wheeler
 *   jump cannot do recursion. Machines later kept return addresses on a stack; four extra instructions model that:
 *       9 CAL a  push the next address, jump to a     11 PSH  push acc
 *      10 RET    pop an address and jump to it        12 POP  pop into acc
 *
 * WHAT THIS PROGRAM DOES
 *   1. A machine and a loader that places a routine written once at any address (relocation).
 *   2. One call traced word by word: how the return jump is built and planted.
 *   3. A square-root subroutine (subtract 1, 3, 5, 7, ... while possible), called from k places, against the same
 *      code written out in full at every place (an "open" subroutine): words of memory and instructions executed.
 *   4. A small library (square root, multiply, power), loaded at two different sets of addresses, printing a table
 *      of squares like the EDSAC's first program and checking every result.
 *   5. A routine that calls itself: with the Wheeler jump it never returns; with a stack it does.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java Subroutines.java
 *   Expected output: expected-output.txt in this folder.
 */
public class Subroutines {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static final String[] OPS = {"HLT", "LDA", "ADD", "SUB", "STA", "JMP", "JNG", "JZR", "OUT", "CAL", "RET", "PSH", "POP"};

    // ---- 1. the machine and the loader ---------------------------------------------------------------------------------
    static final class Machine {
        final int[] mem = new int[1000];
        final Deque<Integer> stack = new ArrayDeque<>();
        final List<Integer> out = new ArrayList<>();
        int acc = 0, pc = 0, maxDepth = 0;
        long executed = 0;
        List<String> trace = null;

        /** Run from address start; return true if HLT was reached within the limit. */
        boolean run(int start, long limit) {
            pc = start;
            while (executed < limit) {
                int w = mem[pc], op = w / 1000, a = w % 1000, at = pc;
                if (w < 0 || op >= OPS.length) throw new IllegalStateException("not an instruction at " + pc + ": " + w);
                pc++;
                executed++;
                switch (op) {
                    case 0 -> { return true; }
                    case 1 -> acc = mem[a];
                    case 2 -> acc += mem[a];
                    case 3 -> acc -= mem[a];
                    case 4 -> mem[a] = acc;
                    case 5 -> pc = a;
                    case 6 -> { if (acc < 0) pc = a; }
                    case 7 -> { if (acc == 0) pc = a; }
                    case 8 -> out.add(mem[a]);
                    case 9 -> { stack.push(pc); pc = a; maxDepth = Math.max(maxDepth, stack.size()); }
                    case 10 -> pc = stack.pop();
                    case 11 -> { stack.push(acc); maxDepth = Math.max(maxDepth, stack.size()); }
                    case 12 -> acc = stack.pop();
                    default -> throw new IllegalStateException();
                }
                if (trace != null) trace.add(String.format("%d: %s %d -> acc %d", at, OPS[op], a, acc));
            }
            return false;
        }
    }

    /**
     * Place a routine at an origin. Each line is "label: OP operand", "label: DAT value" or "OP" alone. An operand is a
     * number, "*" (this word's own address), a label of this routine, a name from the shared table, or name+k / name-k.
     * Labels are local to the routine, so the same text can be loaded anywhere: that is relocation.
     */
    static Map<String, Integer> load(Machine m, int origin, String src, Map<String, Integer> shared) {
        String[] lines = src.strip().split("\n");
        Map<String, Integer> local = new HashMap<>();
        for (int i = 0; i < lines.length; i++) {
            String ln = lines[i].strip();
            if (ln.contains(":")) local.put(ln.substring(0, ln.indexOf(':')).strip(), origin + i);
        }
        for (int i = 0; i < lines.length; i++) {
            String ln = lines[i].strip();
            if (ln.contains(":")) ln = ln.substring(ln.indexOf(':') + 1).strip();
            String[] t = ln.split("\\s+");
            int here = origin + i, value = t.length > 1 ? resolve(t[1], here, local, shared) : 0;
            if (t[0].equals("DAT")) m.mem[here] = value;
            else m.mem[here] = Arrays.asList(OPS).indexOf(t[0]) * 1000 + value;
            if (!t[0].equals("DAT") && Arrays.asList(OPS).indexOf(t[0]) < 0) throw new IllegalArgumentException(ln);
        }
        return local;
    }

    static int resolve(String s, int here, Map<String, Integer> local, Map<String, Integer> shared) {
        int k = 0;
        int plus = Math.max(s.lastIndexOf('+'), s.lastIndexOf('-'));
        if (plus > 0) {
            k = Integer.parseInt(s.substring(plus + 1)) * (s.charAt(plus) == '-' ? -1 : 1);
            s = s.substring(0, plus);
        }
        int base;
        if (s.equals("*")) base = here;
        else if (s.matches("-?\\d+")) base = Integer.parseInt(s);
        else if (local.containsKey(s)) base = local.get(s);
        else if (shared.containsKey(s)) base = shared.get(s);
        else throw new IllegalArgumentException("unknown name " + s);
        return base + k;
    }

    static int words(String src) { return src.strip().split("\n").length; }

    // The shared words: parameters, result, constants. The same addresses in every program.
    static final int P = 900, Q = 901, R = 902, B = 903, E = 904, ZERO = 910, ONE = 911, TWO = 912, BACK = 913;

    static Map<String, Integer> shared() {
        Map<String, Integer> s = new HashMap<>(Map.of("P", P, "Q", Q, "R", R, "B", B, "E", E));
        s.putAll(Map.of("ZERO", ZERO, "ONE", ONE, "TWO", TWO, "BACK", BACK));
        return s;
    }

    static void constants(Machine m) {
        m.mem[ZERO] = 0;
        m.mem[ONE] = 1;
        m.mem[TWO] = 2;
        m.mem[BACK] = 5000 + 2 - 1000;           // turns "LDA n" into "JMP n+2"
    }

    // Square root by subtracting the odd numbers 1, 3, 5, ...: the count that fits is the whole part of the root.
    static final String SQRT = """
            S:    ADD BACK
                  STA EXIT
                  LDA ZERO
                  STA R
                  LDA ONE
                  STA ODD
                  LDA P
                  STA REM
            LOOP: LDA REM
                  SUB ODD
                  JNG EXIT
                  STA REM
                  LDA R
                  ADD ONE
                  STA R
                  LDA ODD
                  ADD TWO
                  STA ODD
                  JMP LOOP
            EXIT: DAT 0
            ODD:  DAT 0
            REM:  DAT 0
            """;

    // Multiply P by Q (Q >= 0) by repeated addition.
    static final String MUL = """
            S:    ADD BACK
                  STA EXIT
                  LDA ZERO
                  STA R
                  LDA Q
                  STA CNT
            LOOP: LDA CNT
                  JZR EXIT
                  SUB ONE
                  STA CNT
                  LDA R
                  ADD P
                  STA R
                  JMP LOOP
            EXIT: DAT 0
            CNT:  DAT 0
            """;

    // B to the power E, by calling MUL: a subroutine may call another one.
    static final String POW = """
            S:    ADD BACK
                  STA EXIT
                  LDA ONE
                  STA ACC
                  LDA E
                  STA CNT
            LOOP: LDA CNT
                  JZR DONE
                  SUB ONE
                  STA CNT
                  LDA ACC
                  STA P
                  LDA B
                  STA Q
                  LDA *
                  JMP MUL
                  LDA R
                  STA ACC
                  JMP LOOP
            DONE: LDA ACC
                  STA R
            EXIT: DAT 0
            ACC:  DAT 0
            CNT:  DAT 0
            """;

    static int isqrt(int n) { int r = 0; while ((r + 1) * (r + 1) <= n) r++; return r; }

    public static void main(String[] args) {
        // ---- 2. one call, traced ------------------------------------------------------------------------------------------
        Machine m = new Machine();
        constants(m);
        Map<String, Integer> sh = shared();
        int subAt = 200;
        Map<String, Integer> sq = load(m, subAt, SQRT, sh);
        sh.put("SQRT", subAt);
        String caller = """
                      LDA X
                      STA P
                CALL: LDA *
                      JMP SQRT
                      OUT R
                      HLT
                X:    DAT 30
                """;
        Map<String, Integer> cl = load(m, 40, caller, sh);
        int n = cl.get("CALL");
        m.trace = new ArrayList<>();
        check(m.run(40, 10_000), "the traced call halts");
        int exit = sq.get("EXIT");
        check(m.mem[exit] == 5000 + n + 2, "the planted word is JMP n+2");
        check(m.out.equals(List.of(5)), "isqrt(30) = 5");
        System.out.printf("call: the caller's word at %d is LDA %d = %d (it loads itself) ; JMP %d enters the routine ; the routine adds %d and gets %d ; it stores that in its last word, %d, where it reads as JMP %d, the word after the call ; the routine returned the square root of 30: %d ; %d instructions executed%n",
                n, n, 1000 + n, subAt, m.mem[BACK], 5000 + n + 2, exit, n + 2, m.out.get(0), m.executed);
        StringJoiner tr = new StringJoiner(" | ");
        for (int i = 0; i < 6; i++) tr.add(m.trace.get(i));
        tr.add("... " + m.trace.get(m.trace.size() - 3));
        tr.add(m.trace.get(m.trace.size() - 2));
        tr.add(m.trace.get(m.trace.size() - 1));
        System.out.println("trace: " + tr);

        // ---- 3. closed against open, k call sites -----------------------------------------------------------------------
        String body = SQRT.substring(SQRT.indexOf("LDA ZERO"), SQRT.indexOf("EXIT:"));   // the routine without the return
        int subWords = words(SQRT), bodyWords = words(body);
        int[] values = {2, 99, 144, 1000, 17, 400, 5, 625, 81, 990};
        StringJoiner mem = new StringJoiner(" ; ");
        int crossover = -1;
        long extraPerCall = -1;
        for (int k = 1; k <= 8; k++) {
            // closed: one copy at 500, k call sequences
            StringBuilder closed = new StringBuilder();
            for (int i = 0; i < k; i++) closed.append("LDA X").append(i).append("\nSTA P\nLDA *\nJMP SQRT\nLDA R\nSTA Y").append(i).append('\n');
            closed.append("HLT\n");
            StringBuilder open = new StringBuilder();
            for (int i = 0; i < k; i++)
                open.append("LDA X").append(i).append("\nSTA P\n")
                        .append(body.replace("LOOP", "LOOP" + i).replace("JNG EXIT", "JNG OUT" + i).replace("ODD", "ODD" + i).replace("REM", "REM" + i))
                        .append("OUT").append(i).append(": LDA R\nSTA Y").append(i).append('\n');
            open.append("HLT\n");
            StringBuilder data = new StringBuilder();
            for (int i = 0; i < k; i++) data.append("X").append(i).append(": DAT ").append(values[i]).append("\nY").append(i).append(": DAT 0\n");
            for (int i = 0; i < k; i++) open.append("ODD").append(i).append(": DAT 0\nREM").append(i).append(": DAT 0\n");
            // place the data after the code in both versions, with the work words of the open version included
            String closedSrc = closed + data.toString(), openSrc = open + data.toString();
            int closedWords = words(closedSrc) + subWords, openWords = words(openSrc);

            Machine mc = new Machine(), mo = new Machine();
            constants(mc);
            constants(mo);
            Map<String, Integer> s1 = shared(), s2 = shared();
            load(mc, 500, SQRT, s1);
            s1.put("SQRT", 500);
            Map<String, Integer> lc = load(mc, 0, closedSrc, s1), lo = load(mo, 0, openSrc, s2);
            check(mc.run(0, 1_000_000) && mo.run(0, 1_000_000), "both versions halt");
            for (int i = 0; i < k; i++) {
                check(mc.mem[lc.get("Y" + i)] == isqrt(values[i]), "closed version correct");
                check(mo.mem[lo.get("Y" + i)] == isqrt(values[i]), "open version correct");
            }
            long extra = (mc.executed - mo.executed) / k;
            check(mc.executed - mo.executed == extra * k, "the cost of a call is the same at every site");
            if (extraPerCall < 0) extraPerCall = extra;
            check(extra == extraPerCall, "constant cost per call");
            if (crossover < 0 && closedWords < openWords) crossover = k;
            mem.add(String.format("%d place%s: closed %d words, open %d", k, k == 1 ? "" : "s", closedWords, openWords));
        }
        check(crossover == 2, "two call sites already favour the closed subroutine");
        System.out.printf("memory: square-root routine %d words (%d without the return machinery), call sequence 6 words ; %s ; the closed subroutine saves memory from %d call sites on ; each call costs %d extra instructions (load own word, jump, build and store the return, jump back)%n",
                subWords, bodyWords, mem, crossover, extraPerCall);

        // ---- 4. a library, loaded at two different places -------------------------------------------------------------------
        String main = """
                      LDA ONE
                      STA I
                LOOP: LDA I
                      STA P
                      STA Q
                      LDA *
                      JMP MUL
                      OUT R
                      LDA R
                      STA P
                      LDA *
                      JMP SQRT
                      OUT R
                      LDA I
                      ADD ONE
                      STA I
                      SUB LIM
                      JNG LOOP
                      JZR LOOP
                      LDA TWO
                      STA B
                      LDA TEN
                      STA E
                      LDA *
                      JMP POW
                      OUT R
                      HLT
                I:    DAT 0
                LIM:  DAT 12
                TEN:  DAT 10
                """;
        int[][] layouts = {{200, 300, 400}, {610, 120, 777}};
        List<List<Integer>> outs = new ArrayList<>();
        StringJoiner lay = new StringJoiner(" ; ");
        for (int[] at : layouts) {
            Machine ml = new Machine();
            constants(ml);
            Map<String, Integer> s = shared();
            s.put("SQRT", at[0]);
            s.put("MUL", at[1]);
            s.put("POW", at[2]);
            load(ml, at[0], SQRT, s);
            load(ml, at[1], MUL, s);
            load(ml, at[2], POW, s);
            load(ml, 0, main, s);
            check(ml.run(0, 1_000_000), "library program halts");
            outs.add(ml.out);
            lay.add(String.format("square root at %d, multiply at %d, power at %d: first word of the loop in multiply is %d", at[0], at[1], at[2], ml.mem[at[1] + 6]));
        }
        List<Integer> expected = new ArrayList<>();
        for (int i = 1; i <= 12; i++) { expected.add(i * i); expected.add(i); }
        expected.add(1024);
        check(outs.get(0).equals(expected) && outs.get(1).equals(expected), "same results wherever the library is loaded");
        StringJoiner sq2 = new StringJoiner(" ");
        for (int i = 1; i <= 12; i++) sq2.add(String.valueOf(outs.get(0).get(2 * (i - 1))));
        System.out.printf("library: three routines (square root %d words, multiply %d, power %d, which calls multiply) ; %s ; both layouts print the squares %s, the square root of each, and 2^10 = %d%n",
                words(SQRT), words(MUL), words(POW), lay, sq2, outs.get(0).get(outs.get(0).size() - 1));
        for (int i = 1; i <= 2000; i++) {
            Machine mt = new Machine();
            constants(mt);
            Map<String, Integer> s = shared();
            load(mt, 200, SQRT, s);
            s.put("SQRT", 200);
            mt.mem[700] = i;
            load(mt, 0, "LDA 700\nSTA P\nLDA *\nJMP SQRT\nHLT", s);
            check(mt.run(0, 1_000_000) && mt.mem[R] == isqrt(i), "square root of every number up to 2000");
        }
        System.out.println("roots: the square-root routine checked against Java for every number from 1 to 2000");

        // ---- 5. recursion -----------------------------------------------------------------------------------------------------
        // SUM(n) = n + SUM(n-1), SUM(0) = 0, written with the Wheeler jump: the inner call overwrites EXIT.
        String sumWheeler = """
                S:    ADD BACK
                      STA EXIT
                      LDA P
                      JZR BASE
                      STA N
                      SUB ONE
                      STA P
                CALL: LDA *
                      JMP S
                      LDA R
                      ADD N
                      STA R
                      JMP EXIT
                BASE: LDA ZERO
                      STA R
                EXIT: DAT 0
                N:    DAT 0
                """;
        Machine mw = new Machine();
        constants(mw);
        Map<String, Integer> sw = shared();
        Map<String, Integer> lw = load(mw, 300, sumWheeler, sw);
        sw.put("SUM", 300);
        load(mw, 0, "LDA FIVE\nSTA P\nLDA *\nJMP SUM\nOUT R\nHLT\nFIVE: DAT 5", sw);
        long limit = 1_000_000;
        boolean halted = mw.run(0, limit);
        check(!halted, "the Wheeler-jump recursion never returns");
        int planted = mw.mem[lw.get("EXIT")];
        check(planted == 5000 + lw.get("CALL") + 2, "the exit word points back inside the routine");
        System.out.printf("wheeler: SUM(5) = 5 + SUM(4) written with the Wheeler jump ; each inner call stores its own return in the same exit word, %d, so after the innermost return the word holds JMP %d, a place inside the routine itself ; the program was stopped after %,d instructions without finishing (R had reached %,d)%n",
                lw.get("EXIT"), planted - 5000, limit, mw.mem[R]);

        String sumStack = """
                S:    LDA P
                      JZR BASE
                      PSH
                      SUB ONE
                      STA P
                      CAL S
                      POP
                      ADD R
                      STA R
                      RET
                BASE: LDA ZERO
                      STA R
                      RET
                """;
        long instr100 = 0;
        int depth100 = 0;
        for (int k = 0; k <= 100; k++) {
            Machine ms = new Machine();
            constants(ms);
            Map<String, Integer> ss = shared();
            load(ms, 300, sumStack, ss);
            ss.put("SUM", 300);
            ms.mem[700] = k;
            load(ms, 0, "LDA 700\nSTA P\nCAL SUM\nHLT", ss);
            check(ms.run(0, 1_000_000), "the stack version halts");
            check(ms.mem[R] == k * (k + 1) / 2, "SUM(k) = k(k+1)/2");
            check(ms.stack.isEmpty(), "the stack is empty at the end");
            if (k == 100) { instr100 = ms.executed; depth100 = ms.maxDepth; }
        }
        System.out.printf("stack: the same routine with return addresses and saved values on a stack (CAL, RET, PSH, POP) ; SUM(k) = k(k+1)/2 correct for every k from 0 to 100 ; SUM(100) = 5050 took %,d instructions and a stack %d deep%n",
                instr100, depth100);

        System.out.println("Subroutines: " + passed + " checks passed");
    }
}
