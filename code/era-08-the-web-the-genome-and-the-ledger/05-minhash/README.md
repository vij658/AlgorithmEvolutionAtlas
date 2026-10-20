# MinHash and Locality-Sensitive Hashing: the program

*Era 8 · topic 5 · 1997–1998* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/05-minhash/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/05-minhash/minhash.html) · [All era 8 programs](../README.md)

## How it works

```text
Cut a document into its overlapping runs of w words, its "shingles". Two documents resemble each other as much as
their sets of shingles overlap: resemblance (the Jaccard index) = shared shingles / all shingles of either.
Computing that for every pair of millions of documents is hopeless, so Broder sketches each document: put all
possible shingles in a random order and keep the one that comes first in each document. The first shingle of
the union of A and B is equally likely to be any of its members, and the two documents keep the same one exactly
when it is shared, so Pr[same minimum] = shared / union = the resemblance. With k independent orders (in practice,
k hash functions), the fraction of agreeing minima estimates the resemblance with an error near sqrt(J(1-J)/k).
To find similar pairs without comparing all of them, cut each sketch into b bands of r numbers and put each band
in a hash table: two documents become candidates if they agree on a whole band, which happens with probability
1 - (1 - J^r)^b, a steep S-shaped curve. This is locality-sensitive hashing: similar items collide on purpose.
```

## What the program does

```text
1. The key fact checked exactly: for every pair of subsets of a 7-element universe, the fraction of the 5,040
   orders in which the minima agree equals the Jaccard index, as a fraction.
2. Documents: this book's field notes (corpus.txt) cut into 40-word pieces, plus copies with 5%, 10%, 20% and 40%
   of their words replaced. Exact resemblance against MinHash estimates with 16, 64 and 256 hash functions.
3. Banding: how often pairs of known resemblance become candidates, against 1 - (1 - J^r)^b.
4. Finding all pairs with resemblance at least 0.5: every pair compared, against LSH candidates only.
5. Two sentences for the book's widget, with 32 hash functions it can repeat.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MinHashLsh.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [MinHash](https://en.wikipedia.org/wiki/MinHash) — Wikipedia | The one-line proof and the error of k samples |
| Deeper | [Syntactic Clustering of the Web](https://archives.iw3c2.org/www2010/pubs/77977/src-tn-1997-015.pdf) — A. Broder, S. Glassman, M. Manasse, G. Zweig (1997) | What it took to cluster 30 million pages |
| Scholar | [On the resemblance and containment of documents](https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf) — A. Broder (1997), on a Princeton course page | Shingles, resemblance and min-wise samples |
| Scholar | [Approximate Nearest Neighbor: Towards Removing the Curse of Dimensionality](https://mirror.theoryofcomputing.org/articles/v008a014/) — S. Har-Peled, P. Indyk, R. Motwani, *Theory of Computing* (2012) | Locality-sensitive hashing, from the 1998 and 2001 papers |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
