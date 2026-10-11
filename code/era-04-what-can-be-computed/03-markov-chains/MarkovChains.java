import java.util.*;

/**
 * Era 4, topic 3: Markov chains (Markov 1906 and 1913).
 *
 * HOW IT WORKS
 *   A Markov chain moves between states (here two: vowel V and consonant C). The chance of the next state depends
 *   only on the present one, through four fixed numbers:
 *       after V: vowel with probability p1, consonant 1 - p1
 *       after C: vowel with probability p2, consonant 1 - p2
 *   The letters are not independent (unless p1 = p2), yet the share of vowels in a long run still settles down, to
 *       p = p2 / (1 - p1 + p2),
 *   and the difference from it shrinks like |p1 - p2|^n after n letters. That was Markov's answer to the claim that
 *   the law of large numbers needs independence. Dependence changes the size of the fluctuations instead: with
 *   d = p1 - p2, the variance of the number of vowels in n letters is close to n p (1 - p) (1 + d) / (1 - d) when n is
 *   large, against n p (1 - p) for independent letters. In 1913 Markov tested this on 20,000 letters of Pushkin's
 *   Eugene Onegin.
 *
 * WHAT THIS PROGRAM DOES
 *   1. Takes the counts reported for Markov's sample (Hayes, American Scientist, 2013) and finds which way of counting
 *      pairs makes them consistent: only 20,000 pairs that run one letter past the sample, which needs the first
 *      letter to be a consonant and letter 20,001 a vowel.
 *   2. Recomputes the probabilities (0.432, 0.128, 0.663), and the 3,731 double vowels that independent letters
 *      would give.
 *   3. The chain's long-run share of vowels, and how fast the transition table's powers approach it.
 *   4. The dispersion factor (1 + d) / (1 - d), and a simulation of 200,000 groups of 100 letters (Markov wrote his
 *      letters in groups of 100) against the exact variance formula, for the chain and for independent letters.
 *   5. The law of large numbers for the dependent chain: the running share of vowels over 10 million letters.
 *   Every printed line starts with a tag that the book's page builder reads.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java MarkovChains.java
 *   Expected output: expected-output.txt in this folder.
 */
public class MarkovChains {
    static long passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static long seed = 1913L;

    /** A fixed 64-bit linear congruential generator, so the output is the same on every machine. */
    static double uniform() {
        seed = seed * 6364136223846793005L + 1442695040888963407L;
        return (seed >>> 11) / 9007199254740992.0;                   // the top 53 bits, in [0, 1)
    }

    /** Exact variance of the number of vowels in n letters of a stationary two-state chain. */
    static double varExact(int n, double p, double d) {
        double q = 1 - p, s = n;                                       // Var = p q (n + 2 sum_{k=1}^{n-1} (n - k) d^k)
        double dk = 1;
        for (int k = 1; k < n; k++) { dk *= d; s += 2 * (n - k) * dk; }
        return p * q * s;
    }

    public static void main(String[] args) {
        // ---- 1. the published counts, and which way of counting pairs fits them ------------------------------------
        int N = 20000, V = 8638, C = 11362, VV = 1104, CC = 3827, MIX = 15069;
        check(V + C == N, "vowels + consonants = 20,000");
        check(VV + CC + MIX == N, "pairs add up to 20,000");
        System.out.printf("counts: %d letters, %d vowels, %d consonants ; pairs %d vowel-vowel, %d consonant-consonant, %d mixed, total %d%n",
                N, V, C, VV, CC, MIX, VV + CC + MIX);

        // (a) 19,999 pairs inside the sample: there would be 19,999 pairs, not 20,000
        boolean linear = VV + CC + MIX == N - 1;
        check(!linear, "19,999 pairs do not fit");
        // (b) a closed loop: every letter starts one pair and ends one, so VV + VC = V and VV + CV = V
        int vcLoop = V - VV, cvLoop = V - VV;
        boolean loop = vcLoop + cvLoop == MIX && CC + cvLoop == C;
        check(!loop, "a closed loop does not fit");
        // (c) each of the 20,000 letters starts a pair; the last pair ends on letter 20,001
        int VC = V - VV, CV = C - CC;                                  // pairs starting with a vowel / with a consonant
        check(VC + CV == MIX, "the mixed pairs split as V->C 7534, C->V 7535");
        // letters that end a pair are letters 2 .. 20,001: vowels among them = V - [letter 1 is V] + [letter 20,001 is V]
        int endV = VV + CV;
        List<String> fits = new ArrayList<>();
        for (int firstV = 0; firstV <= 1; firstV++)
            for (int lastV = 0; lastV <= 1; lastV++)
                if (V - firstV + lastV == endV) fits.add((firstV == 1 ? "vowel" : "consonant") + " first, " + (lastV == 1 ? "vowel" : "consonant") + " at 20,001");
        check(fits.size() == 1 && fits.get(0).equals("consonant first, vowel at 20,001"), "exactly one arrangement fits");
        System.out.printf("pairs: 19,999 pairs inside the sample would total 19,999, not %d ; a closed loop needs %d mixed pairs, not %d ; 20,000 pairs, the last reaching letter 20,001, fit with vowel->consonant %d and consonant->vowel %d, only if %s%n",
                VV + CC + MIX, vcLoop + cvLoop, MIX, VC, CV, fits.get(0));

        // ---- 2. the probabilities -----------------------------------------------------------------------------------
        double p = (double) V / N, p1 = (double) VV / V, p2 = (double) CV / C;
        check(String.format("%.3f", p).equals("0.432") && String.format("%.3f", p1).equals("0.128") && String.format("%.3f", p2).equals("0.663"),
                "the probabilities 0.432, 0.128, 0.663");
        long indep = Math.round(N * p * p);
        check(indep == 3731, "independent letters would give 3,731 double vowels");
        System.out.printf("probabilities: a vowel %.4f ; a vowel after a vowel %d/%d = %.4f ; a vowel after a consonant %d/%d = %.4f ; independent letters would give %d x %.4f^2 = %d double vowels, the poem has %d%n",
                p, VV, V, p1, CV, C, p2, N, p, indep, VV);

        // ---- 3. long-run share and the powers of the transition table ----------------------------------------------
        double d = p1 - p2;
        double pi = p2 / (1 - p1 + p2);
        check(Math.abs(pi - p) < 1e-4, "the chain's long-run share matches the sample's share of vowels");
        double[][] P = {{p1, 1 - p1}, {p2, 1 - p2}};
        double[][] M = {{1, 0}, {0, 1}};
        StringJoiner pw = new StringJoiner(" ; ");
        for (int n = 1; n <= 12; n++) {
            double[][] R = new double[2][2];
            for (int i = 0; i < 2; i++)
                for (int j = 0; j < 2; j++)
                    for (int k = 0; k < 2; k++) R[i][j] += M[i][k] * P[k][j];
            M = R;
            double gap = Math.abs(M[0][0] - M[1][0]);                   // after a vowel versus after a consonant
            check(Math.abs(gap - Math.pow(Math.abs(d), n)) < 1e-12, "the gap shrinks like |d|^n");
            if (n == 1 || n == 2 || n == 3 || n == 5 || n == 8 || n == 12)
                pw.add(String.format("%d letters on: %.6f vs %.6f", n, M[0][0], M[1][0]));
        }
        System.out.printf("longrun: share of vowels p2 / (1 - p1 + p2) = %.4f ; d = p1 - p2 = %.4f ; chance of a vowel n letters after a vowel vs after a consonant: %s%n",
                pi, d, pw);

        // ---- 4. the size of the fluctuations ------------------------------------------------------------------------
        double factor = (1 + d) / (1 - d);
        int groups = 200000, len = 100;
        double sumC = 0, sumC2 = 0, sumI = 0, sumI2 = 0;
        boolean vowel = uniform() < pi;
        for (int g = 0; g < groups; g++) {
            int cntC = 0, cntI = 0;
            for (int k = 0; k < len; k++) {
                vowel = uniform() < (vowel ? p1 : p2);
                if (vowel) cntC++;
                if (uniform() < p) cntI++;
            }
            sumC += cntC; sumC2 += (double) cntC * cntC;
            sumI += cntI; sumI2 += (double) cntI * cntI;
        }
        double meanC = sumC / groups, varC = sumC2 / groups - meanC * meanC;
        double meanI = sumI / groups, varI = sumI2 / groups - meanI * meanI;
        double binom = len * p * (1 - p);
        double exactC = varExact(len, pi, d);
        check(Math.abs(varC / exactC - 1) < 0.02, "simulated chain variance matches the exact formula");
        check(Math.abs(varI / binom - 1) < 0.02, "simulated independent variance matches n p q");
        check(Math.abs(exactC / (len * pi * (1 - pi)) - factor) < 0.01, "for groups of 100 the exact ratio is close to (1 + d)/(1 - d)");
        System.out.printf("spread: dispersion factor (1 + d) / (1 - d) = %.4f ; groups of %d letters: independent letters, variance n p q = %.2f, simulated %.2f ; the chain, exact variance %.2f (ratio %.4f), simulated %.2f, over %d groups%n",
                factor, len, binom, varI, exactC, exactC / (len * pi * (1 - pi)), varC, groups);

        // ---- 5. the law of large numbers, with dependence -------------------------------------------------------------
        seed = 1906L;
        vowel = uniform() < 0.5;
        long count = 0;
        StringJoiner run = new StringJoiner(" ; ");
        long next = 100;
        double lastErr = 1;
        for (long i = 1; i <= 10_000_000L; i++) {
            vowel = uniform() < (vowel ? p1 : p2);
            if (vowel) count++;
            if (i == next) {
                double share = (double) count / i;
                run.add(String.format("%,d letters: %.5f", i, share));
                lastErr = Math.abs(share - pi);
                next *= 10;
            }
        }
        check(lastErr < 3e-4, "after 10 million letters the share is within 0.0003 of the long-run value");
        System.out.printf("lln: a simulated chain with these probabilities, share of vowels after %s ; long-run value %.5f%n", run, pi);

        System.out.println("MarkovChains: " + passed + " checks passed");
    }
}
