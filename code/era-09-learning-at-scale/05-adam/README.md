# Adam: the program

*Era 9 · topic 5 · 2014* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/05-adam/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/05-adam/adam.html) · [All era 9 programs](../README.md)

## How it works

```text
Gradient descent moves every parameter against its gradient g by a step of size alpha * g. Adam gives every
parameter its own step. It keeps two running averages of that parameter's gradient:
  m = beta1 * m + (1 - beta1) * g          (the mean, like momentum)
  v = beta2 * v + (1 - beta2) * g * g      (the mean square, like RMSProp)
Both start at zero, so early on they are too small; dividing by (1 - beta1^t) and (1 - beta2^t) corrects that.
The step is alpha * mhat / (sqrt(vhat) + eps). Its size is about alpha whatever the scale of the gradient: a
parameter whose gradients are tiny moves as far as one whose gradients are huge. The paper's defaults are
alpha = 0.001, beta1 = 0.9, beta2 = 0.999, eps = 1e-8.
```

## What the program does

```text
1. Five methods (SGD, momentum, AdaGrad, RMSProp, Adam) on three problems: a small neural network on two
   interleaved spirals, logistic regression with rare features, and a long narrow valley with noisy gradients.
   Each method gets its best learning rate from the same grid; the program also counts how many rates of the
   grid come within a factor 2 of that method's best loss.
2. Adam's bias correction: the factor by which the first steps would be wrong without it, and the effect on the
   neural network.
3. Invariance: multiply one parameter's gradients by 1,000 and Adam's path does not change.
4. A convex problem on which Adam's steps keep the point at the wrong end, and AMSGrad, which steps by the
   largest mean square so far, reaches the right end.
5. Paths on a two-dimensional valley for the page.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Adam.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Optimization for Deep Learning (Momentum, RMSprop, AdaGrad, Adam)](https://www.youtube.com/watch?v=NE88eqLngkg) — DeepBean | The four methods side by side |
| Deeper | [Adam Optimization Algorithm (C2W2L08)](https://www.youtube.com/watch?v=JXQT_vxqwIs) — DeepLearningAI | Andrew Ng's lecture in the Deep Learning Specialization |
| Deeper | [Stochastic gradient descent](https://en.wikipedia.org/wiki/Stochastic_gradient_descent) — Wikipedia | From Robbins and Monro to Adam and AMSGrad |
| Scholar | [Adam: A Method for Stochastic Optimization](https://arxiv.org/abs/1412.6980) — D. P. Kingma, J. Ba (2014; ICLR 2015) | The algorithm, the defaults and the bias correction |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
