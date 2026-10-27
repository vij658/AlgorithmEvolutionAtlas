# Support Vector Machines: the program

*Era 8 · topic 1 · 1992–1995* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/01-support-vector-machines/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/01-support-vector-machines/support-vector-machines.html) · [All era 8 programs](../README.md)

## How it works

```text
Two kinds of examples, labelled +1 and -1, are points in a plane (or in many dimensions). Rosenblatt's perceptron
finds some line that separates them; a support vector machine finds the line with the widest empty street on
either side. Write the line as w . x + b = 0 and ask that every example satisfy y (w . x + b) >= 1; the street
is then 2 / |w| wide, so the widest street has the smallest |w|. That is a quadratic program. Its dual form has
one number alpha_i >= 0 per example, and the answer is w = sum alpha_i y_i x_i: only the examples with alpha_i > 0,
the support vectors, count, and they are the ones standing on the edges of the street.
The dual touches the examples only through dot products x_i . x_j. Replace the dot product by another function
K(x_i, x_j), a kernel, and the same algorithm draws a straight street in a space of new features that it never
writes down: (x . z + 1)^2 is the dot product of the 6 features 1, sqrt2 x1, sqrt2 x2, x1^2, x2^2, sqrt2 x1 x2,
so a straight street there is a curved one here.
Real data rarely separate. The soft margin lets example i stand inside the street, or on the wrong side, by a
slack xi_i, at a price C xi_i; in the dual this only caps every alpha_i at C.
This program solves the dual by sequential minimal optimization: change two alphas at a time (the pair that
most violates the optimality conditions), which can be done exactly with a formula.
```

## What the program does

```text
1. 60 separable points: the widest street, checked against a direct search over every direction of the line,
   and the street left by a perceptron trained on the same points.
2. The kernel trick checked: (x . z + 1)^2 equals the dot product of the six explicit features.
3. A disc inside a ring: no line separates them; the degree-2 kernel and a Gaussian kernel do.
4. Two overlapping clouds: the soft margin for C from 0.01 to 100.
5. 40 points from a simple generator that the book's widget repeats, for four values of C.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java SupportVectorMachines.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Lecture 16: Learning: Support Vector Machines](https://www.ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/resources/lecture-16-learning-support-vector-machines) — Patrick Winston, MIT OpenCourseWare 6.034 (2010); the page hosts the video and a transcript | The widest street, derived on a blackboard |
| Start | [Support Vector Machines](https://cml.rhul.ac.uk/svm.html) — Royal Holloway, University of London | The Moscow origins, 1962 to 1964 |
| Deeper | [Support vector machine](https://en.wikipedia.org/wiki/Support_vector_machine) — Wikipedia | Margins, the hinge loss, kernels and training by SMO |
| Scholar | [A Training Algorithm for Optimal Margin Classifiers](https://classes.engr.oregonstate.edu/eecs/fall2023/ai534-400/extra/boser-1992.pdf) — B. Boser, I. Guyon, V. Vapnik (1992), on an Oregon State course page | Maximum margins with kernels |
| Scholar | [Support-Vector Networks](https://homepages.math.uic.edu/~lreyzin/papers/cortes95.pdf) — C. Cortes, V. Vapnik, *Machine Learning* (1995), on a UIC page | The soft margin and the digit experiments |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
