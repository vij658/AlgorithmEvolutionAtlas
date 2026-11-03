# The Transformer: the program

*Era 9 · topic 9 · 2017* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/09-transformer/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/09-transformer/transformer.html) · [All era 9 programs](../README.md)

## How it works

```text
Every position of the input is a vector. Attention lets one position gather information from all the others:
it forms a query q, every position forms a key k_i and a value v_i (each by multiplying its vector by a learned
matrix), and the output is a weighted average of the values,
  Attention(Q, K, V) = softmax(Q K^T / sqrt(d_k)) V,
so a position takes most from the positions whose keys best match its query. Dividing by sqrt(d_k) keeps the
scores from growing with the vector length, which would make the softmax nearly one-hot and its gradient
nearly zero. The Transformer stacks such layers (with several "heads" side by side, residual connections and
small feed-forward networks) and needs no recurrence: all positions are computed at once.
```

## What the program does

```text
1. A task that needs attention: a sequence of 6 (key, value) pairs and then a query key; the answer is the value
   stored under that key. A one-layer, one-head attention model with hand-written gradients (checked against
   finite differences) learns it; a model that averages the positions instead of attending cannot.
2. The scaling: with d_k = 512 and no division by sqrt(d_k), the softmax saturates and its gradient vanishes.
3. The sinusoidal positional encoding: the dot product of the encodings of two positions depends only on how
   far apart they are.
4. The cost of one layer, counted: self-attention against a recurrent layer.
Every printed line starts with a tag that the book's page builder reads; the last line before the checks holds
the trained weights for the book's widget.
```

## Run it

```
java Transformer.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Attention in transformers, step-by-step \| Deep Learning Chapter 6](https://www.youtube.com/watch?v=eMlx5fFNoYc) — 3Blue1Brown | Queries, keys and values, drawn |
| Deeper | [Let's build GPT: from scratch, in code, spelled out.](https://www.youtube.com/watch?v=kCc8FmEb1nY) — Andrej Karpathy | A small transformer written and trained live |
| Scholar | [Attention Is All You Need](https://arxiv.org/pdf/1706.03762) — A. Vaswani and seven co-authors (2017) | The Transformer |
| Scholar | [Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/pdf/1409.0473) — D. Bahdanau, K. Cho, Y. Bengio (2014; ICLR 2015) | Attention, before the Transformer |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
