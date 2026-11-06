# 107. Statistics for evals: Wilson intervals, McNemar and pass@k

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

Every change to a prompt, a model or a retrieval step is judged by an eval: a list of questions with known answers. Teams ship a change because the score went from 80% to 82% on 200 questions, which is well inside the noise. Or they report 100% on a small set as if it were certain. An eval is a sample, and a number without an error bar is a guess.

## How it works

**Interval for one accuracy.** The familiar `p ± 1.96·√(p(1−p)/n)` (Wald) is too narrow near 0% and 100%, and at 100 of 100 it has zero width. Wilson's interval inverts the test instead (its endpoints are the two solutions of `(p̂ − p)² = z²·p(1−p)/n`) and stays close to the promised 95%.

**Comparing two models.** Score both on the same questions and look only at the questions where they disagree: b where only A is right, c where only B is right. Under "no difference", each disagreement is a fair coin, so the exact McNemar test is a binomial test on b and c. The questions both get right or both get wrong cancel out, which is why a paired comparison needs far fewer questions.

**pass@k.** For code models: the chance that at least one of k attempts passes. With n ≥ k samples of which c pass, `1 − C(n−c, k)/C(n, k)` is exactly unbiased (Chen et al., 2021). The tempting `1 − (1 − c/n)^k` is biased low, because `1 − (1 − p)^k` is concave (Jensen).

## What the program shows

- Wilson's formula equals the roots of the quadratic, and stays inside [0, 1], for all tested n and k.
- 81 of 100: Wald [0.733, 0.887], Wilson [0.722, 0.875]. 100 of 100: Wald [1.000, 1.000], Wilson [0.963, 1.000].
- Exact coverage of a "95%" interval at n = 20, p = 0.95: Wald 0.639, Wilson 0.925. Averaged over p at n = 50: Wald 0.908, Wilson 0.950.
- At 80% accuracy the 95% interval is ±7.8 points with 100 questions, ±2.5 with 1,000, ±1.1 with 5,000. Telling 80% from 82% with two independent samples needs 6,036 questions per model.
- 2,000 simulated evals of 1,000 *shared* questions (A 80%, B 82%): the models disagree on 49.2 questions on average; McNemar detects the difference in 80.6% of evals; the same data through an unpaired test, 2.1%; two separate question sets of 1,000 each, about 21%.
- pass@k with n = 10, k = 5: the unbiased estimator's expected value equals the truth exactly (e.g. 0.4095 at p = 0.1); the plug-in gives 0.3485.

## Full circle

- [Entry 42, Monte Carlo and the 1/√n law](../../part-2-paradigms-and-classics/42-monte-carlo/README.md): the error bar shrinks like 1/√n; four times the questions halves it.
- [Entry 13, the birthday bound](../../part-1-distances-and-number-theory/13-birthday-bound/README.md): another place where intuition about probability is reliably wrong.
- [Entry 50, percentiles](../../part-3-performance-and-distributed-systems/50-percentiles-and-coordinated-omission/README.md): the same discipline for latency. Measure the distribution, not one number.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: your eval has 300 questions and the new prompt scores 84% against 81%. Is it better? Compute the Wilson intervals by hand, then think about why that is the wrong test.
2. Questions often come in clusters (ten questions about one document). Simulate clustered questions and show the naive interval is too narrow; read Miller (2024) on clustered standard errors.
3. Add a paired bootstrap over questions and compare its p-values with McNemar's.
4. Build an eval of 100 questions over your own book and measure a real model on it, with intervals.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/107-eval-statistics
java EvalStatistics.java
```

JDK 17 or newer, no build step. It prints 10018 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
81 of 100 correct: Wald [0.733, 0.887], Wilson [0.722, 0.875]; 100 of 100: Wald [1.000, 1.000], Wilson [0.963, 1.000]
true coverage of a nominal 95% interval (exact binomial sums): n=20 p=0.50 Wald 0.959 Wilson 0.959; n=20 p=0.80 Wald 0.921 Wilson 0.956; n=20 p=0.95 Wald 0.639 Wilson 0.925; n=100 p=0.50 Wald 0.943 Wilson 0.943; n=100 p=0.80 Wald 0.933 Wilson 0.941; n=100 p=0.95 Wald 0.877 Wilson 0.966;
n=50, averaged over p = 0.01 ... 0.99: Wald covers 0.908, Wilson 0.950
at 80% accuracy the 95% interval is +/- 7.8 points with 100 questions; 3.9 points with 400 questions; 2.5 points with 1,000 questions; 1.1 points with 5,000 questions;
to tell 80% from 82% with two independent samples (5% test, 80% power): 6,036 questions per model
2000 simulated evals of 1,000 shared questions (A 80%, B 82%): the models disagree on 49.2 questions on average; McNemar finds the difference in 80.6% of evals; the same data run through an unpaired two-proportion test, 2.1%; two separate question sets of 1,000 each would give about 21%
pass@k from n = 10 samples, k = 5, expected value of the estimate against the truth: p=0.05 truth 0.2262, unbiased 0.2262, plug-in 0.1889; p=0.10 truth 0.4095, unbiased 0.4095, plug-in 0.3485; p=0.30 truth 0.8319, unbiased 0.8319, plug-in 0.7597; p=0.60 truth 0.9898, unbiased 0.9898, plug-in 0.9703;
EvalStatistics: 10018 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- E. B. Wilson, "Probable inference, the law of succession, and statistical inference", *Journal of the American Statistical Association* 22(158), 1927.
- L. D. Brown, T. T. Cai and A. DasGupta, "Interval estimation for a binomial proportion", *Statistical Science* 16(2), 2001.
- Q. McNemar, "Note on the sampling error of the difference between correlated proportions or percentages", *Psychometrika* 12(2), 1947.
- M. Chen et al., "Evaluating large language models trained on code", 2021 (HumanEval and the unbiased pass@k estimator).
- E. Miller, "Adding error bars to evals: a statistical approach to language model evaluations", 2024.
