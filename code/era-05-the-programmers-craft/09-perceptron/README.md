# Rosenblatt's Perceptron: the program

*Era 5 · topic 9 · 1957–1958* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/09-perceptron/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/09-perceptron/perceptron.html) · [All era 5 programs](../README.md)

## How it works

```text
A perceptron looks at many inputs (the 400 photocells of the Mark I, say), multiplies each by a weight, adds them
up with a bias, and answers yes if the total is positive, no if it is not. It learns from examples: when it
answers wrongly, each weight is nudged in the direction that would have made the answer right (add the input
for a missed yes, subtract it for a false yes), and when it answers rightly nothing changes. If some setting of
the weights separates the yes examples from the no examples by a straight cut (a plane, in many dimensions), this
rule finds such a setting after a limited number of mistakes; if none exists, it never settles.
```

## What the program does

```text
1. Cards of 20 x 20 cells with a mark on the left or the right half, in random places, with speckle noise: how many
   cards the perceptron sees before it stops making mistakes, its score on new cards, and the weights it learned.
2. The mistake bound: on random separable examples in 2 to 50 dimensions, the number of mistakes never exceeds
   (R / margin)^2.
3. All 16 functions of two yes/no inputs: which can be learned.
4. XOR: the weights never settle; give the perceptron one more input, x AND y, and it learns at once.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Perceptron.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Professor's perceptron paved the way for AI – 60 years too soon](https://news.cornell.edu/node/313946) — Melanie Lefkowitz, Cornell Chronicle (2019) | The 1958 demonstration, the cards, and the headlines |
| Start | [Perceptron](https://en.wikipedia.org/wiki/Perceptron) — Wikipedia | The learning rule, the Mark I, the convergence theorem and XOR |
| Deeper | [Frank Rosenblatt](https://en.wikipedia.org/wiki/Frank_Rosenblatt) — Wikipedia | His life, the Mark I and *Principles of Neurodynamics* |
| Scholar | [The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain](https://homepages.math.uic.edu/~lreyzin/papers/rosenblatt58.pdf) — F. Rosenblatt, *Psychological Review* 65(6): 386–408 (1958), on a University of Illinois Chicago page | The paper: three questions about perception and a machine to answer them |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
