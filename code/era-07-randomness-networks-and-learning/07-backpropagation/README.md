# Backpropagation: the program

*Era 7 · topic 7 · 1970–1986* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/07-backpropagation/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/07-backpropagation/backpropagation.html) · [All era 7 programs](../README.md)

## How it works

```text
A neural network is a chain of simple steps: each unit adds up its inputs times weights and squashes the sum with
a smooth S-shaped function. Learning means adjusting the weights so the outputs get closer to the targets, by
gradient descent: nudge every weight against the slope of the error. The slope with respect to each weight could
be measured by wiggling that weight and running the whole network again, once per weight. Backpropagation gets all
the slopes at once: run the network forward, then apply the chain rule backwards, from the error at the output to
each hidden unit and each weight. That costs about as much as one more forward run, whatever the number of
weights. With it, hidden units can learn features that no single layer can represent, such as exclusive-or.
```

## What the program does

```text
1. The perceptron rule (Era 5) on AND and on exclusive-or (XOR): it learns AND, and never gets XOR right.
2. A network with two hidden units trained by backpropagation on XOR, from 100 random starts.
3. Backpropagation's gradient against wiggling each weight: the same numbers, at a fraction of the work.
4. One XOR run in detail: the error epoch by epoch, from fixed starting weights the book's widget also uses.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Backpropagation.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Introduction to Neural Nets: videos](https://cs.wellesley.edu/~cs332/videos/Neural_Nets_videos.html) — Wellesley College CS 332, listing Grant Sanderson's 3Blue1Brown videos | "What is backpropagation really doing?" and "Backpropagation calculus", with suggested stopping points |
| Deeper | [30 Years of Adaptive Neural Networks](https://isl.stanford.edu/people/widrow/papers/j199030years.pdf) — B. Widrow, M. Lehr, *Proc. IEEE* (1990) | Perceptron, Madaline and backpropagation, by one of the field's pioneers |
| Deeper | [Deep Learning in Neural Networks: An Overview](https://arxiv.org/pdf/1404.7828) — J. Schmidhuber (2014) | Section 5.5 traces backpropagation from the 1960s to 1986 |
| Scholar | [Learning Representations by Back-Propagating Errors](https://mlanthology.org/misc/1986/rumelhart1986misc-learning) — D. Rumelhart, G. Hinton, R. Williams, *Nature* (1986), ML Anthology record | The abstract and full citation of the paper that made the method famous |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
