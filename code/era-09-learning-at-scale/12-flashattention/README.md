# FlashAttention: the program

*Era 9 · topic 12 · 2022* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/12-flashattention/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/12-flashattention/flashattention.html) · [All era 9 programs](../README.md)

## How it works

```text
Attention computes S = Q K^T / sqrt(d) (an N x N table of scores), P = softmax of each row of S, and O = P V.
On a graphics processor the arithmetic is fast; moving numbers between the large, slow main memory (HBM) and the
small, fast on-chip memory (SRAM) is not. Standard attention writes S and P to main memory and reads them back,
about 4 N^2 numbers of traffic. FlashAttention never stores S or P. It cuts K and V into blocks of Bc rows and Q
into blocks of Br rows, small enough to sit in SRAM together, and for each row keeps a running maximum m and a
running sum l of exponentials. When a new block raises the maximum from m to m', everything accumulated so far
is multiplied by exp(m - m'), so the result at the end is exactly softmax(S) V: the same numbers, computed in a
different order.
```

## What the program does

```text
1. The online softmax: one pass with a running maximum and sum gives the same weights as the usual two passes,
   and the naive softmax without a maximum overflows where the safe one does not.
2. Standard attention and FlashAttention on random Q, K and V (N up to 1,024, d = 64): the outputs agree to the
   last few bits, while the program counts every number each method reads from and writes to main memory.
3. The counts for longer sequences and other head sizes, against the paper's Theta(N d + N^2) and
   Theta(N^2 d^2 / M), and the extra memory each method needs.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java FlashAttention.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Deeper | [Flash Attention derived and coded from first principles with Triton (Python)](https://www.youtube.com/watch?v=zy8ChVd_oTM) — Umar Jamil | The online softmax derived, then coded |
| Scholar | [FlashAttention - Tri Dao \| Stanford MLSys #67](https://www.youtube.com/watch?v=gMOAud7hZg4) — Stanford MLSys Seminars | The first author, at Stanford's systems seminar |
| Scholar | [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/pdf/2205.14135) — T. Dao, D. Y. Fu, S. Ermon, A. Rudra, C. Ré (2022) | Tiling, the online softmax and the IO analysis |
| Scholar | [NeurIPS 2022 proceedings page](https://proceedings.neurips.cc/paper_files/paper/2022/hash/67d57c32e20fd0a7a302cb81d36e40d5-Abstract-Conference.html) — NeurIPS | Venue |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
