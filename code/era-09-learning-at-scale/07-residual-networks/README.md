# Residual Networks: the program

*Era 9 · topic 7 · 2015* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/07-residual-networks/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/07-residual-networks/residual-networks.html) · [All era 9 programs](../README.md)

## How it works

```text
A plain deep network passes its signal through layer after layer: each block of two layers computes
h -> relu(W2 relu(W1 h + b1) + b2). Stacking more blocks should never hurt, since the extra blocks could learn
to pass their input through unchanged, yet in practice deeper plain networks train worse: their error on the
training data itself goes up. A residual block adds its input back: h -> relu(h + W2 relu(W1 h + b1) + b2).
The block now only has to learn a correction F(h) to its input, and "no correction" (W2 = 0) passes the
signal through exactly. The shortcut adds no parameters and almost no computation.
```

## What the program does

```text
1. Checks the hand-written gradient against finite differences, for both kinds of network.
The paper's networks normalize every layer (batch normalization); this program does not, and instead starts the
second layer of every residual block at zero, so that each block starts as the identity. It also reports what
happens to a residual network started with the same random weights as the plain one.
2. Trains plain and residual networks of 1 to 32 blocks (4 to 66 layers with weights) to fit a wavy function
   of two variables, with the same data, the same optimizer (Adam, topic 5) and the same number of steps,
   and reports the error on the training data itself.
3. Measures how large the gradient reaching the first block is at the start of training, for each depth.
4. Takes a trained residual network, appends blocks whose second weights are zero, and checks that it computes
   exactly the same function: a deeper residual network can always copy a shallower one.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ResidualNetworks.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Residual neural network](https://en.wikipedia.org/wiki/Residual_neural_network) — Wikipedia | The degradation problem, highway networks and where residuals went next |
| Deeper | [[Classic] Deep Residual Learning for Image Recognition (Paper Explained)](https://www.youtube.com/watch?v=GWt6Fu05voI) — Yannic Kilcher | A walk through the paper |
| Scholar | [Deep Residual Learning for Image Recognition](https://www.youtube.com/watch?v=C6tLw-rPQ2o) — ComputerVisionFoundation Videos | The conference talk, on the channel of the Computer Vision Foundation |
| Scholar | [Deep Residual Learning for Image Recognition](https://arxiv.org/pdf/1512.03385) — K. He, X. Zhang, S. Ren, J. Sun (2015) | The degradation experiment and the residual block |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
