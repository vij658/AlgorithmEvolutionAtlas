# Least Squares, and the Lost Planet: the program

*Era 3 · topic 8 · 1801–1809* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/08-least-squares/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/08-least-squares/least-squares.html) · [All era 3 programs](../README.md)

## How it works

```text
Measurements disagree, and there are more of them than unknowns, so the equations cannot all hold. Legendre's rule:
choose the unknowns that make the sum of the squares of the errors as small as possible. For a model
y = c1 f1(x) + ... + cn fn(x) fitted to m observations, setting the derivative of the sum of squares to zero for each
unknown gives n linear "normal equations", (F^T F) c = F^T y, however many observations there are. They are solved by
elimination (Era 2, topic 1). Squares are chosen because they make the arithmetic linear and, as Legendre put it,
set up a kind of balance among the errors, so that no single extreme error dominates.
```

## What the program does

```text
1. Fits a straight line and a quadratic to noisy observations by the normal equations and Gaussian elimination,
   and checks that no nearby choice of coefficients has a smaller sum of squares.
2. Compares three rules on 10,000 noisy data sets: least squares, least absolute errors, and least largest error.
3. Shows a single wild observation pulling each rule.
4. Counts the work: the normal equations stay n by n however many observations.
5. Shows the weakness of the normal equations for ill-conditioned fits, against an orthogonal (QR) solution.
6. Full circle: gradient descent on the sum of squares, as a machine-learning library trains a linear model,
   reaches the same coefficients.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LeastSquares.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Gauss Predicts the Orbit of Ceres](https://thatsmaths.com/2021/06/24/gauss-predicts-the-orbit-of-ceres/) — *thatsmaths* blog (24 June 2021) | The lost planet and the prediction, with the caution about least squares |
| Start | [Gauss and Ceres](https://ow3.math.rutgers.edu/~cherlin/History/Papers1999/weiss.html) — Leorah Weiss, history of mathematics term paper, Rutgers (1999) | Piazzi's 22 observations over 41 days, the three Gauss used, and the recovery |
| Start | [Carl Friedrich Gauss](https://mathshistory.st-andrews.ac.uk/Biographies/Gauss/) — MacTutor | Ceres, the *Theoria motus*, and Gauss's life |
| Deeper | [Regression Analysis – A Powerful Tool and Riveting Drama](https://old.maa.org/sites/default/files/pdf/upload_library/46/HOMSIGMAA/Chalberg-RegressionHistoryPaper.pdf) — Tim Chalberg, Pacific Lutheran University, MAA HOMSIGMAA | Legendre, Gauss, Adrain and the priority dispute |
| Scholar | [Gauss and the method of least squares](https://gtfp.cs.rhul.ac.uk/pulskamp/Gauss/Gauss.html) — Richard Pulskamp, sources in the history of probability and statistics | Where to find Gauss's least-squares writings in translation |
| Scholar | [Sur la méthode des moindres quarrés](https://www.york.ac.uk/depts/maths/histstat/legendre2.pdf) — Legendre, appendix to *Nouvelles méthodes pour la détermination des orbites des comètes* (Paris, 1805), scan on the University of York history of statistics pages | The first publication of least squares, in French |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
