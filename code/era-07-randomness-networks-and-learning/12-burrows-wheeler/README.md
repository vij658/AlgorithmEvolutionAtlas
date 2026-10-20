# The Burrows–Wheeler Transform: the program

*Era 7 · topic 12 · 1983–1994* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/12-burrows-wheeler/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/12-burrows-wheeler/burrows-wheeler.html) · [All era 7 programs](../README.md)

## How it works

```text
Write down every rotation of a block of text (move the first letter to the end, again and again), sort the
rotations alphabetically, and keep only the last letter of each. That column, L, is a rearrangement of the text
in which letters that come before similar contexts sit together: all the rotations that start with "he" are
sorted next to each other, and the letters just before "he" are mostly t, so the t's bunch up in L. L compresses well with simple methods: move-to-front turns repeated letters into
small numbers, mostly zeros, and a Huffman code (Era 5) packs those into few bits. The surprise is that L, plus
the position of the original text among the sorted rotations, is enough to rebuild the text: the k-th "e" in L
and the k-th "e" in the sorted first column are the same letter of the text (the "LF mapping"), so the text can be
walked backwards one letter at a time. The same mapping lets one count a pattern's occurrences in the text by
looking at L alone, one pattern letter at a time (Ferragina and Manzini's FM index, 2000), which is how programs
align DNA reads to a genome.
```

## What the program does

```text
1. The transform of "abracadabra", rotation by rotation, and its inverse.
2. This book's field notes (corpus.txt, the same text as Era 6's Lempel-Ziv program): runs of equal letters
   before and after, move-to-front, and bits per byte against Huffman alone, Era 6's LZ77, and Deflate (gzip).
3. Block size: the transform needs large blocks to work well.
4. Counting patterns with the FM index's backward search, against counting by scanning.
5. Round trips: 2,000 random strings and every block transformed and inverted.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java BurrowsWheeler.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Burrows–Wheeler transform](https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform) — Wikipedia | The transform worked by hand, and its inverse |
| Deeper | [Lecture 5: Library Complexity and Short Read Alignment (Mapping)](https://ocw.mit.edu/courses/7-91j-foundations-of-computational-and-systems-biology-spring-2014/resources/lecture-5-library-complexity-and-short-read-alignment-mapping/) — MIT OpenCourseWare, David Gifford, 7.91J (Spring 2014) | Builds an FM index from the Burrows–Wheeler transform to align DNA reads, with video and transcript |
| Deeper | [Introduction to the Burrows-Wheeler Transform and FM Index](https://www.cl.cam.ac.uk/teaching/2324/Bioinfo/papers/bwt_fm.pdf) — B. Langmead (2013) | The LF mapping and backward search, step by step |
| Scholar | [A Block-sorting Lossless Data Compression Algorithm](https://www.cl.cam.ac.uk/teaching/0304/DSAlgs/SRC-124.pdf) — M. Burrows, D. Wheeler, SRC Research Report 124 (1994) | The transform, its inverse, and the measurements |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
