# AdaBoost: the program

*Era 7 · topic 13 · 1995–1997* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/13-adaboost/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/13-adaboost/adaboost.html) · [All era 7 programs](../README.md)

## How it works

```text
A "weak" rule of thumb is one that is right a little more often than a coin: here a decision stump, a single
test such as "x below 0.43 means yes". Kearns and Valiant asked whether rules that weak could always be combined
into an accurate one; Schapire showed in 1990 that they could, and Freund and Schapire's AdaBoost made it
practical. Give every training example a weight, equal at first. Each round, find the stump with the smallest
weighted error e; then shrink the weight of every example it got right by the factor e / (1 - e), so the next
round concentrates on the examples still being missed. The final rule is a vote of all the stumps, each counted
with weight log((1 - e) / e). Freund and Schapire proved that the training error falls at least as fast as the
product of 2 sqrt(e (1 - e)) over the rounds: exponentially, as long as each stump beats a coin by some margin.
```

## What the program does

```text
1. Points in a square, labelled by whether they lie inside a circle: no single stump can draw a circle. Training
   and test error as rounds are added, against the proven bound.
2. The same with 10% of the training labels flipped: the weights pile up on the flipped examples.
3. A small set of 120 points made with a simple generator that the book's widget repeats, so the widget can show
   the same rounds with the same errors.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AdaBoost.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Lecture 17: Learning: Boosting](https://www.ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/resources/lecture-17-learning-boosting) — MIT OpenCourseWare, Patrick Winston, 6.034 (Fall 2010) | "Can multiple weak classifiers be used to make a strong one?", worked through with video and transcript |
| Start | [AdaBoost](https://en.wikipedia.org/wiki/AdaBoost) — Wikipedia | The algorithm, its loss function, and where it is used |
| Deeper | [Michael Kearns](https://en.wikipedia.org/wiki/Michael_Kearns_(computer_scientist) — Wikipedia | The weak-versus-strong learning question that started boosting |
| Scholar | [A decision-theoretic generalization of on-line learning and an application to boosting](https://khoury.northeastern.edu/home/vip/teach/IRcourse/6_ML/other_notes/freund_schapire_adaboost_journal.pdf) — Y. Freund, R. Schapire, *J. Comput. Syst. Sci.* (1997) | AdaBoost, its weight update, and the training error bound |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
