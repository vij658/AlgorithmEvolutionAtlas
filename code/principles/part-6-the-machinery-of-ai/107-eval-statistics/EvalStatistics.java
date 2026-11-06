import java.math.BigInteger;
import java.util.*;

/**
 * Entry 107 of the principles catalog (Part 6): Statistics for evals: Wilson intervals, paired comparisons
 * (McNemar) and the unbiased pass@k estimator
 *
 * HOW IT WORKS
 *   An eval is a sample: a model that gets 81 of 100 questions right has an accuracy somewhere around 81%, and the
 *   question is how wide "around" is. The usual p +/- 1.96 sqrt(p(1-p)/n) (the Wald interval) is too narrow near 0%
 *   and 100% and collapses to zero width at 100 of 100. Wilson's interval (1927) inverts the test instead and
 *   keeps close to its promised 95% coverage. To compare two models, score them on the SAME questions and look only
 *   at the questions where they disagree (McNemar, 1947): the shared easy and hard questions cancel, so a paired
 *   test detects a 2-point gain with far fewer questions than comparing two separate accuracies. For code models,
 *   pass@k (the chance that at least one of k attempts passes) is estimated from n >= k samples with c correct
 *   as 1 - C(n-c, k) / C(n, k) (Chen et al., 2021), which is exactly unbiased; plugging c/n into 1 - (1 - p)^k is not.
 *
 * HOW THIS FILE IS ORGANISED
 *   1. The algorithm: the methods the catalog page explains, exactly as tested.
 *   2. Helpers copied from other entries, where this entry is checked against them (marked by a banner).
 *   3. runChecks(): known answers, edge cases, and randomized comparisons against a slower reference. Randomized
 *      checks use a fixed seed, so every run prints the same numbers. Each passing check adds one to the count;
 *      a failing check throws an AssertionError and the program exits with a non-zero status.
 *
 * RUN (JDK 17 or newer, no build step)
 *   java EvalStatistics.java
 *   Expected: the output in expected-output.txt, ending "EvalStatistics: 10018 checks passed".
 *
 * The README.md next to this file explains the idea in depth and lists references.
 */
public class EvalStatistics {
    static int passed = 0;

    static void check(boolean ok, String what) {
        if (!ok) throw new AssertionError("FAILED: " + what);
        passed++;
    }

    static boolean close(double a, double b, double tol) { return Math.abs(a - b) <= tol; }

    static String f(String fmt, Object... args) { return String.format(Locale.ROOT, fmt, args); }

    static final double Z95 = 1.959963984540054;   // the 97.5th percentile of the standard normal

    // ----------------------------------------------------------------------------------------------------
    // The algorithm
    // ----------------------------------------------------------------------------------------------------
    /** Wald interval: p +/- z sqrt(p(1-p)/n). */
    static double[] wald(int k, int n, double z) {
        double p = k / (double) n, h = z * Math.sqrt(p * (1 - p) / n);
        return new double[]{p - h, p + h};
    }

    /** Wilson score interval. */
    static double[] wilson(int k, int n, double z) {
        double p = k / (double) n, z2 = z * z;
        double denom = 1 + z2 / n;
        double centre = (p + z2 / (2 * n)) / denom;
        double half = z / denom * Math.sqrt(p * (1 - p) / n + z2 / (4.0 * n * n));
        return new double[]{centre - half, centre + half};
    }

    /** Exact McNemar test: two-sided p-value from b and c, the counts of the two kinds of disagreement. */
    static double mcNemarExact(int b, int c) {
        int n = b + c, m = Math.min(b, c);
        if (n == 0) return 1;
        double tail = 0;
        for (int i = 0; i <= m; i++) tail += Math.exp(logChoose(n, i) - n * Math.log(2));
        return Math.min(1, 2 * tail);
    }

    /** Two-proportion z-test (unpaired): two-sided p-value. */
    static double twoProportionZ(int k1, int k2, int n) {
        double p1 = k1 / (double) n, p2 = k2 / (double) n, pool = (k1 + k2) / (2.0 * n);
        double se = Math.sqrt(pool * (1 - pool) * 2.0 / n);
        if (se == 0) return 1;
        return 2 * (1 - normalCdf(Math.abs(p1 - p2) / se));
    }

    /** Unbiased pass@k from n samples with c correct: 1 - C(n-c, k)/C(n, k), as a stable product. */
    static double passAtK(int n, int c, int k) {
        if (n - c < k) return 1.0;
        double prod = 1;
        for (int i = n - c + 1; i <= n; i++) prod *= 1 - k / (double) i;
        return 1 - prod;
    }

    /** The tempting estimator: plug c/n into 1 - (1 - p)^k. Biased. */
    static double passAtKNaive(int n, int c, int k) { return 1 - Math.pow(1 - c / (double) n, k); }

    // ----------------------------------------------------------------------------------------------------
    // Shared helpers: log-factorials, binomial probabilities, the normal CDF
    // ----------------------------------------------------------------------------------------------------
    static final double[] LOG_FACT = new double[5001];
    static { for (int i = 1; i < LOG_FACT.length; i++) LOG_FACT[i] = LOG_FACT[i - 1] + Math.log(i); }

    static double logChoose(int n, int k) { return LOG_FACT[n] - LOG_FACT[k] - LOG_FACT[n - k]; }

    static double binomPmf(int n, int k, double p) {
        if (p == 0) return k == 0 ? 1 : 0;
        if (p == 1) return k == n ? 1 : 0;
        return Math.exp(logChoose(n, k) + k * Math.log(p) + (n - k) * Math.log(1 - p));
    }

    /** Standard normal CDF via the complementary error function (Numerical Recipes erfc, |error| < 1.2e-7). */
    static double normalCdf(double x) { return 1 - 0.5 * erfc(x / Math.sqrt(2)); }

    static double erfc(double x) {
        double z = Math.abs(x), t = 1 / (1 + 0.5 * z);
        double r = t * Math.exp(-z * z - 1.26551223 + t * (1.00002368 + t * (0.37409196 + t * (0.09678418
                + t * (-0.18628806 + t * (0.27886807 + t * (-1.13520398 + t * (1.48851587
                + t * (-0.82215223 + t * 0.17087277)))))))));
        return x >= 0 ? r : 2 - r;
    }

    /** Exact coverage of an interval method: the probability, over Binomial(n, p), that it contains p. */
    static double coverage(boolean useWilson, int n, double p) {
        double cov = 0;
        for (int k = 0; k <= n; k++) {
            double[] ci = useWilson ? wilson(k, n, Z95) : wald(k, n, Z95);
            if (ci[0] <= p && p <= ci[1]) cov += binomPmf(n, k, p);
        }
        return cov;
    }

    static BigInteger choose(int n, int k) {
        if (k < 0 || k > n) return BigInteger.ZERO;
        BigInteger r = BigInteger.ONE;
        for (int i = 0; i < k; i++) r = r.multiply(BigInteger.valueOf(n - i)).divide(BigInteger.valueOf(i + 1));
        return r;
    }

    // ----------------------------------------------------------------------------------------------------
    // Checks: what this program verifies. Run with: java EvalStatistics.java
    // ----------------------------------------------------------------------------------------------------
    static void runChecks(Random rnd) {
        // 1. Wilson's endpoints are the two roots of (phat - p)^2 = z^2 p (1 - p) / n: solve the quadratic directly.
        for (int n : new int[]{1, 5, 20, 100, 1000}) for (int k = 0; k <= n; k += Math.max(1, n / 10)) {
            double ph = k / (double) n, z2 = Z95 * Z95;
            double a = 1 + z2 / n, b = -(2 * ph + z2 / n), c = ph * ph;
            double disc = Math.sqrt(b * b - 4 * a * c);
            double[] w = wilson(k, n, Z95);
            check(close(w[0], (-b - disc) / (2 * a), 1e-12) && close(w[1], (-b + disc) / (2 * a), 1e-12), "Wilson = roots of the quadratic");
            check(w[0] >= -1e-15 && w[1] <= 1 + 1e-15, "Wilson stays inside [0, 1]");
        }
        double[] w81 = wilson(81, 100, Z95), wa81 = wald(81, 100, Z95), w100 = wilson(100, 100, Z95), wa100 = wald(100, 100, Z95);
        System.out.println(f("81 of 100 correct: Wald [%.3f, %.3f], Wilson [%.3f, %.3f]; 100 of 100: Wald [%.3f, %.3f], Wilson [%.3f, %.3f]",
                wa81[0], wa81[1], w81[0], w81[1], wa100[0], wa100[1], w100[0], w100[1]));
        check(wa100[0] == 1 && wa100[1] == 1 && w100[0] < 0.97, "Wald collapses at 100%, Wilson does not");

        // 2. Exact coverage of a "95%" interval.
        StringBuilder sb = new StringBuilder("true coverage of a nominal 95% interval (exact binomial sums): ");
        for (int n : new int[]{20, 100}) for (double p : new double[]{0.5, 0.8, 0.95}) {
            double cw = coverage(false, n, p), cs = coverage(true, n, p);
            sb.append(f("n=%d p=%.2f Wald %.3f Wilson %.3f; ", n, p, cw, cs));
        }
        System.out.println(sb.toString().trim());
        double meanWald = 0, meanWilson = 0;
        int grid = 0;
        for (double p = 0.01; p < 0.995; p += 0.01) { meanWald += coverage(false, 50, p); meanWilson += coverage(true, 50, p); grid++; }
        meanWald /= grid; meanWilson /= grid;
        System.out.println(f("n=50, averaged over p = 0.01 ... 0.99: Wald covers %.3f, Wilson %.3f", meanWald, meanWilson));
        check(meanWilson > 0.93 && meanWilson < 0.96 && meanWald < meanWilson - 0.03, "average coverage over p");
        check(coverage(false, 20, 0.95) < 0.70, "Wald undercovers badly near 100%");

        // 3. How many questions? Half-width of the 95% interval at 80% accuracy, and the unpaired sample size for 80% vs 82%.
        StringBuilder hw = new StringBuilder("at 80% accuracy the 95% interval is +/- ");
        for (int n : new int[]{100, 400, 1000, 5000}) hw.append(f("%.1f points with %,d questions; ", 100 * Z95 * Math.sqrt(0.16 / n), n));
        System.out.println(hw.toString().trim());
        double zBeta = 0.8416212335729143;   // 80% power
        double nUnpaired = Math.pow(Z95 + zBeta, 2) * (0.8 * 0.2 + 0.82 * 0.18) / (0.02 * 0.02);
        check(close(normalCdf(zBeta), 0.80, 1e-6) && close(normalCdf(Z95), 0.975, 1e-6), "normal quantiles");
        System.out.println(f("to tell 80%% from 82%% with two independent samples (5%% test, 80%% power): %,.0f questions per model", Math.ceil(nUnpaired)));

        // 4. Known McNemar value: b = 10, c = 2 gives 2 * (1 + 12 + 66) / 4096.
        check(close(mcNemarExact(10, 2), 2 * 79 / 4096.0, 1e-12), "McNemar known value");
        check(mcNemarExact(5, 5) == 1.0, "McNemar symmetric case");

        // 5. Paired beats unpaired: 1,000 shared questions, model A 80%, model B 82%, errors on the same hard questions.
        int n = 1000, runs = 2000, pairedHits = 0, unpairedHits = 0;
        long discordant = 0;
        for (int r = 0; r < runs; r++) {
            int kA = 0, kB = 0, b = 0, c = 0;
            for (int i = 0; i < n; i++) {
                double u = rnd.nextDouble();
                double v = rnd.nextDouble() < 0.9 ? u : rnd.nextDouble();   // B mostly finds the same questions hard
                boolean aOk = u < 0.80, bOk = v < 0.82;
                if (aOk) kA++;
                if (bOk) kB++;
                if (aOk && !bOk) b++;
                if (!aOk && bOk) c++;
            }
            discordant += b + c;
            if (mcNemarExact(b, c) < 0.05) pairedHits++;
            if (twoProportionZ(kA, kB, n) < 0.05) unpairedHits++;
        }
        check(pairedHits > 3 * unpairedHits, "paired test is far more powerful");
        double seIndependent = Math.sqrt((0.8 * 0.2 + 0.82 * 0.18) / n);
        double powerIndependent = normalCdf(0.02 / seIndependent - Z95);
        check(powerIndependent > 0.15 && powerIndependent < 0.30, "independent-samples power at n = 1000");
        System.out.println(f("%d simulated evals of %,d shared questions (A 80%%, B 82%%): the models disagree on %.1f questions "
                + "on average; McNemar finds the difference in %.1f%% of evals; the same data run through an unpaired "
                + "two-proportion test, %.1f%%; two separate question sets of %,d each would give about %.0f%%",
                runs, n, discordant / (double) runs, 100.0 * pairedHits / runs, 100.0 * unpairedHits / runs, n, 100 * powerIndependent));

        // 6. pass@k: the product form equals the exact binomial-coefficient formula.
        for (int nn = 1; nn <= 30; nn++) for (int cc = 0; cc <= nn; cc++) for (int k = 1; k <= nn; k++) {
            double exact = 1 - new java.math.BigDecimal(choose(nn - cc, k)).divide(new java.math.BigDecimal(choose(nn, k)),
                    java.math.MathContext.DECIMAL64).doubleValue();
            check(close(passAtK(nn, cc, k), exact, 1e-12), "pass@k product = 1 - C(n-c,k)/C(n,k)");
        }

        // 7. Unbiased: averaged over c ~ Binomial(n, p), the estimator equals 1 - (1 - p)^k exactly. The plug-in does not.
        StringBuilder pk = new StringBuilder("pass@k from n = 10 samples, k = 5, expected value of the estimate against the truth: ");
        for (double p : new double[]{0.05, 0.1, 0.3, 0.6}) {
            int nn = 10, k = 5;
            double eUnbiased = 0, eNaive = 0;
            for (int cc = 0; cc <= nn; cc++) {
                double w = binomPmf(nn, cc, p);
                eUnbiased += w * passAtK(nn, cc, k);
                eNaive += w * passAtKNaive(nn, cc, k);
            }
            double truth = 1 - Math.pow(1 - p, k);
            check(close(eUnbiased, truth, 1e-12), "pass@k estimator is unbiased");
            check(eNaive < truth, "plug-in estimator underestimates");
            pk.append(f("p=%.2f truth %.4f, unbiased %.4f, plug-in %.4f; ", p, truth, eUnbiased, eNaive));
        }
        System.out.println(pk.toString().trim());
    }

    public static void main(String[] args) throws Exception {
        runChecks(new Random(107));
        System.out.println("EvalStatistics: " + passed + " checks passed");
    }
}
