# Huffman's Codes: the program

*Era 5 · topic 3 · 1951–1952* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/03-huffman-codes/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/03-huffman-codes/huffman-codes.html) · [All era 5 programs](../README.md)

## How it works

```text
A prefix code gives each symbol a string of bits, no string the beginning of another, so a stream of bits can be
cut back into symbols without separators. Common symbols should get short strings. Fano's method works from the
top: sort the symbols, split them into two groups of nearly equal total probability, give one group 0 and the
other 1, and split each group again. Huffman's method works from the bottom: take the two least probable symbols,
make them the two branches of a new node whose probability is their sum, and repeat until one node is left. The
path from the top to a symbol, 0 for one branch and 1 for the other, is its codeword. Huffman proved that no
prefix code has a smaller average length for the given probabilities.
```

## What the program does

```text
1. Huffman's procedure on a short phrase, merge by merge.
2. The letters of corpus.txt (the field notes of Eras 1 to 3, the same text as in Era 4's Shannon program):
   five bits for every letter, Shannon's code, Fano's splitting and Huffman's code, against the entropy.
3. The whole text encoded and decoded again with Huffman's code.
4. Huffman against every possible prefix code, by exhaustive search, for 20,000 random small alphabets; and how
   often Fano's splitting is worse.
5. The longest codeword: with Fibonacci-number frequencies Huffman's tree becomes a single long branch.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java HuffmanCodes.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding) — Wikipedia | The term paper, the bottom-up tree and why it is optimal |
| Start | [Discovery of Huffman Codes](https://old.maa.org/node/646519) — MAA *Convergence*, classroom project | Fano's open problem and the student who solved it, with sources for a class |
| Deeper | [David A. Huffman](https://ethw.org/David_A._Huffman) — Engineering and Technology History Wiki | His career and awards |
| Deeper | [David A. Huffman](https://en.wikipedia.org/wiki/David_A._Huffman) — Wikipedia | Life, later work and mathematical origami |
| Deeper | [UCSC press release, 8 October 1999](https://www.cise.ufl.edu/~manuel/huffman/press.release.html) — University of California, Santa Cruz (copy at the University of Florida) | The announcement of his death, and where his codes were used |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
