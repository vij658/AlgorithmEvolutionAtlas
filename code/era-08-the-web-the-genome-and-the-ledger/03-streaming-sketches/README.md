# Streaming Sketches: the program

*Era 8 · topic 3 · 1996* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/03-streaming-sketches/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/03-streaming-sketches/streaming-sketches.html) · [All era 8 programs](../README.md)

## How it works

```text
A stream of items goes past once, too many to keep. Three questions, three sketches:
- How "repetitive" is the stream? The second frequency moment F2 = sum of (count of item i)^2. Alon, Matias and
  Szegedy give every item a random sign s(i) = +1 or -1 and keep one number, Z = sum of s(item) over the stream.
  Then Z^2 averages to F2, because the cross terms s(i) s(j) cancel on average. Average many independent copies
  to shrink the spread, and take the median of several averages to make a bad answer unlikely.
- How often did item x appear? Count-Min keeps d rows of w counters; each row hashes x to one counter and adds 1.
  Other items that land in the same counters only add to it, so every row overestimates; the smallest of the d
  counters is the estimate, never too low, and with w = e / epsilon and d = ln(1 / delta) it is too high by more
  than epsilon times the stream's length with probability below delta.
- How many different items? Hash each item to a random-looking bit string. Among n different items, about one
  in 2^k has a hash starting with k zeros, so the longest run of leading zeros seen says roughly log2 n.
  HyperLogLog splits the items into m groups by the first bits of the hash, keeps the longest run in each group
  (a number below 64, so 6 bits), and combines the m answers with a harmonic mean. The error is about
  1.04 / sqrt(m), whatever n is. Flajolet and Martin's earlier method keeps a bitmap per group instead.
```

## What the program does

```text
1. A stream of 1,000,000 items drawn from 100,000 keys with a Zipf law (a few keys very common), counted
   exactly for comparison.
2. The F2 sketch: one pass for a few copies, checked against the same sums computed key by key; then the error
   for 64 and 256 copies, and how often it falls within the promised bound.
3. Count-Min with epsilon = 0.001 and delta = 0.01: every key's estimate checked against its true count.
4. HyperLogLog and Flajolet-Martin counting: the spread of the error over 200 different hash functions for
   several numbers of registers, against 1.04 / sqrt(m) and 0.78 / sqrt(m); and 10 million distinct items in
   2,048 registers.
5. A small Count-Min sketch (3 rows of 16 counters) over the words of a paragraph, for the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java StreamingSketches.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Philippe Flajolet's contribution to streaming algorithms](https://lumbroso.princeton.edu/talk/2013-06-20-aggregate-knowledge/talk-2013-06-20-ak-summit-flajolet-lumbroso-slides.pdf) — J. Lumbroso (2013), slides | From probabilistic counting to HyperLogLog |
| Deeper | [Streaming algorithm](https://en.wikipedia.org/wiki/Streaming_algorithm) — Wikipedia | Frequency moments, heavy hitters, distinct elements and lower bounds |
| Scholar | [Probabilistic Counting Algorithms for Data Base Applications](https://www.Gwern.net/doc/cs/algorithm/1985-flajolet.pdf) — P. Flajolet, G. N. Martin, *JCSS* (1985) | Counting distinct items with hashed bit positions |
| Scholar | [The space complexity of approximating the frequency moments](https://web.math.princeton.edu/~nalon/PDFS/amsz4.pdf) — N. Alon, Y. Matias, M. Szegedy (STOC 1996; author's copy) | Sketches, and the lower bounds |
| Scholar | [An Improved Data Stream Summary: The Count-Min Sketch and its Applications](https://www.cs.tufts.edu/~nr/cs257/archive/graham-cormode/count-min.pdf) — G. Cormode, S. Muthukrishnan (preprint of the 2005 paper) | Point queries that are never too low |
| Scholar | [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](https://dmtcs.episciences.org/3545/pdf) — P. Flajolet, É. Fusy, O. Gandouet, F. Meunier (2007) | Distinct counts in 1.5 kilobytes |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
