# Deep Convolutional Networks: the program

*Era 9 · topic 2 · 2012* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/02-deep-convolutional-networks/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/02-deep-convolutional-networks/deep-convolutional-networks.html) · [All era 9 programs](../README.md)

## How it works

```text
A convolutional layer slides a small filter (here 3 x 3 numbers) over the image and, at every position, multiplies
the filter by the pixels under it and adds them up. Where the image matches the filter's pattern, the sum is
large. The same filter is used at every position (weight sharing), so a pattern learned in one corner is
recognized in any other. An activation function then bends the sums: AlexNet used the rectified linear unit
ReLU(x) = max(0, x), which unlike the S-shaped tanh and sigmoid does not flatten out for large inputs, so its
gradient does not vanish. Pooling summarizes each map; here global max pooling keeps only each filter's
strongest response anywhere in the image. A final layer turns the pooled responses into class probabilities
(softmax). Everything is trained by backpropagation (Era 7, topic 7) and stochastic gradient descent.
Dropout switches off a random half of a layer's units at each training step, so that no unit can rely on others,
and scales the survivors up to keep the average the same; at test time all units are used.
```

## What the program does

```text
1. Makes 12 x 12 images of four kinds of stroke (horizontal, vertical and two diagonals) with noise and stray
   dots. Training strokes all lie in the left half of the image; test strokes all lie in the right half.
2. Trains a small convolutional network (6 filters of 3 x 3, ReLU, global max pooling, softmax: 88 numbers) and
   checks its gradient against finite differences. It recognizes strokes in the half it never saw.
3. Trains a fully connected network with the same data (144 inputs, 16 hidden units: 2,388 numbers). It fits
   the left half and fails on the right: it has no idea that a stroke is the same stroke elsewhere.
4. ReLU against tanh: images seen until the training error first falls below 25% (the measure Krizhevsky and
   colleagues used, on CIFAR-10), for 8 starting weights.
5. Dropout on a fully connected network with 64 hidden units trained on 240 images.
6. Prints the trained network's 88 numbers for the book's widget, which lets the reader draw a stroke.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ConvNet.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Neural Networks Part 8: Image Classification with Convolutional Neural Networks (CNNs)](https://www.youtube.com/watch?v=HGwBXDKFk9I) — StatQuest with Josh Starmer | Filters, pooling and classification, step by step |
| Start | [AlexNet](https://en.wikipedia.org/wiki/AlexNet) — Wikipedia | The network, the contest and what came before |
| Deeper | [[Classic] ImageNet Classification with Deep Convolutional Neural Networks (Paper Explained)](https://www.youtube.com/watch?v=Nq3auVtvd9Q) — Yannic Kilcher | A walk through the 2012 paper |
| Scholar | [ImageNet Classification with Deep Convolutional Neural Networks](https://courses.cs.duke.edu/fall16/compsci527/papers/Krizhevsky%20et%20al%20DNN%20ImageNet%202012.pdf) — A. Krizhevsky, I. Sutskever, G. Hinton (2012), on a Duke course page | The paper, with its ReLU and dropout experiments |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
