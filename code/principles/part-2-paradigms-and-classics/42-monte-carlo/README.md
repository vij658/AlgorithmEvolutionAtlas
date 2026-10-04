# 42. Monte Carlo and the 1/√n law

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#42-monte-carlo-and-the-1n-law)

## How it works

Estimate a quantity by random sampling and averaging. The error shrinks like 1/√n whatever the dimension, so each extra decimal digit costs 100 times more samples; the program measures that law on π and on an integral.

## In depth (from the catalog page)

Estimate a quantity by random sampling. The error of the average of n independent samples with standard deviation σ is about σ/√n, whatever the dimension of the problem: ten times the accuracy costs a hundred times the samples. The code estimates π as the fraction of random points in the unit square that land inside the quarter circle, and integrates a function by averaging it at random points. *Stratified sampling* splits the range into n slices and draws one random point per slice, which spreads the points evenly and can beat plain sampling by orders of magnitude on smooth functions.

```java
static double estimatePi(long samples, Random rnd) {
    long inside = 0;
    for (long i = 0; i < samples; i++) {
        double x = rnd.nextDouble(), y = rnd.nextDouble();
        if (x * x + y * y <= 1.0) inside++;
    }
    return 4.0 * inside / samples;
}

static double integrate(DoubleUnaryOperator f, int n, boolean stratified, Random rnd) {   // average of f over [0, 1]
    double sum = 0;
    for (int i = 0; i < n; i++) {
        double u = stratified ? (i + rnd.nextDouble()) / n : rnd.nextDouble();   // one random point per stratum
        sum += f.applyAsDouble(u);
    }
    return sum / n;
}
```

> **Verified.** The root-mean-square error of the π estimate follows `√(π(4 − π)/n)`, the spread of a binomial count. With n = 100, 10,000 and 1,000,000 samples the measured errors were 0.155, 0.0168 and 0.00161 against predictions of 0.164, 0.0164 and 0.00164 (300, 300 and 100 trials), so each hundredfold increase in samples bought about a tenfold gain in accuracy. For the integral of 4/(1 + x²) over [0, 1], which equals π, with n = 10,000 samples, plain Monte Carlo had an RMS error of 6.32e-03 against the predicted σ/√n = 6.43e-03, and stratified sampling had 6.24e-07: about 10,000 times smaller with the same number of samples.

<!-- -->

> **Pitfall.** The 1/√n law is slow, since each extra digit costs 100 times the samples. In one or a few dimensions with a smooth integrand, stratification or deterministic quadrature wins; Monte Carlo wins when the dimension is high, because its error rate doesn't depend on it. Seed the generator when you need reproducible runs, and in multithreaded code give each thread its own generator (`ThreadLocalRandom` or `SplittableRandom`) rather than sharing one `Random`, whose Javadoc warns about contention.

**Use it for** risk and queueing simulations, physics and rendering (path tracing), probabilities with no closed form, power calculations for experiments, and Monte Carlo tree search in game AI. The method was developed at Los Alamos in the 1940s by Ulam, von Neumann and Metropolis.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/42-monte-carlo
java MonteCarlo.java
```

JDK 17 or newer, no build step. It prints 5 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
pi estimate with n = 100 samples: measured RMS error 0.15521, predicted 0.16422 (300 trials)
pi estimate with n = 10,000 samples: measured RMS error 0.01679, predicted 0.01642 (300 trials)
pi estimate with n = 1,000,000 samples: measured RMS error 0.00161, predicted 0.00164 (100 trials)
integral of 4/(1+x^2) on [0,1] with n = 10,000: plain Monte Carlo RMS error 6.32e-03 (sigma/sqrt(n) = 6.43e-03), stratified 6.24e-07
MonteCarlo: 5 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
