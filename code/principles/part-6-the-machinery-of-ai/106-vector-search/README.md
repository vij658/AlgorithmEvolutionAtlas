# 106. Vector search: exact k-NN, IVF and SimHash

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

Retrieval-augmented generation (RAG) gives a model the right pages to read before it answers: every document chunk becomes an embedding vector, and a question's vector is compared with all of them. Comparing with every vector is exact and easy, and it is too slow once there are hundreds of millions of chunks and thousands of questions a second.

## How it works

For unit vectors `‖u − v‖² = 2 − 2·cos θ` (entry 7), so the nearest by distance and the most similar by cosine are the same list. Approximate methods trade a little **recall** (the share of the true nearest neighbours returned) for a lot of speed.

**IVF (inverted file):** cluster the vectors with k-means (Lloyd's algorithm: assign each point to its nearest centre, move each centre to the mean of its points, repeat; the total squared distance never goes up). Keep one list per cluster. At query time compare the query with the centres and scan only the `nprobe` closest lists.

**SimHash:** each bit says which side of a random hyperplane a vector lies on. Two vectors at angle θ disagree on a bit with probability θ/π, so the Hamming distance between two signatures (entry 5: one XOR and a bit count per 64 bits) estimates the angle. 128 bits replace 64 doubles (16 bytes instead of 512). Scan the signatures, then re-rank the best few candidates exactly.

Production vector databases mostly use graph indexes such as HNSW, with IVF and quantization close behind. The trade-off they expose is the one measured here: recall against work.

## What the program shows

- A random hyperplane separates two vectors with probability θ/π: 0.0551 at 10° (0.0556 expected), 0.4990 at 90° (0.5), 0.9451 at 170° (0.9444), each from 50,000 hyperplanes.
- 20,000 unit vectors in 64 dimensions around 200 topics, 200 queries: the exact top 10 by cosine equals the exact top 10 by distance for every query.
- k-means with 128 clusters: the objective never increased over 8 iterations (24,827 after the first assignment, 13,940 at the end).
- IVF recall@10: 0.902 scanning 1 cluster (1.5% of a full scan's work), 0.977 with 8 (8.8%), 0.991 with 16 (17%), 1.000 with all of them.
- SimHash (128 bits) recall@10 by candidates re-ranked: 10 → 0.276, 200 → 0.834, 1,000 → 0.966, all → 1.000.

## Full circle

- [Entry 7, cosine similarity](../../part-1-distances-and-number-theory/07-cosine-similarity-and-jaccard/README.md) and [entry 3, Euclidean distance](../../part-1-distances-and-number-theory/03-euclidean-distance/README.md): the identity that makes either ranking work.
- [Entry 5, Hamming distance](../../part-1-distances-and-number-theory/05-hamming-distance/README.md) and [entry 14, bit tricks](../../part-1-distances-and-number-theory/14-bit-tricks-and-gray-code/README.md): SimHash search is XOR and `Long.bitCount`.
- [Entry 38, Bloom filters](../../part-2-paradigms-and-classics/38-bloom-filter/README.md) and [entry 40, HyperLogLog](../../part-2-paradigms-and-classics/40-hyperloglog/README.md): the same bargain: a small, approximate summary instead of the full data.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: what recall do you expect from IVF with 32 clusters probed? Add it and check.
2. Implement the triangle-inequality argument for why probing the closest centres usually finds the true neighbours, and find a query where it fails.
3. Add product quantization: split each vector into 8 sub-vectors and replace each by the nearest of 256 learned centres (one byte). Measure recall and memory.
4. Read the HNSW paper and implement a single-layer navigable small-world graph; compare its recall-for-work curve with IVF's.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/106-vector-search
java VectorSearch.java
```

JDK 17 or newer, no build step. It prints 234 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
one random hyperplane separates two vectors at angle theta with probability theta/pi: 10 deg: 0.0551 (theta/pi = 0.0556); 30 deg: 0.1685 (theta/pi = 0.1667); 60 deg: 0.3362 (theta/pi = 0.3333); 90 deg: 0.4990 (theta/pi = 0.5000); 120 deg: 0.6701 (theta/pi = 0.6667); 170 deg: 0.9451 (theta/pi = 0.9444);
20,000 unit vectors in 64 dimensions, 200 queries: exact top-10 by cosine equals exact top-10 by distance for every query
k-means, 128 clusters, 8 iterations: sum of squared distances 24827.0 after the first assignment, 13940.0 at the end
IVF recall@10 by clusters scanned (comparisons include the 128 cluster centres): nprobe 1: 0.902 with 1.5% of a full scan's comparisons; nprobe 2: 0.928 with 2.6% of a full scan's comparisons; nprobe 4: 0.956 with 4.7% of a full scan's comparisons; nprobe 8: 0.977 with 8.8% of a full scan's comparisons; nprobe 16: 0.991 with 17.0% of a full scan's comparisons; nprobe 128: 1.000 with 100.6% of a full scan's comparisons;
SimHash (128 bits) recall@10 by candidates re-ranked exactly: 10: 0.276; 50: 0.601; 200: 0.834; 1,000: 0.966; 20,000: 1.000;
VectorSearch: 234 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- M. S. Charikar, "Similarity estimation techniques from rounding algorithms", STOC 2002 (SimHash).
- M. X. Goemans and D. P. Williamson, "Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming", *Journal of the ACM* 42(6), 1995 (the θ/π lemma).
- S. P. Lloyd, "Least squares quantization in PCM", *IEEE Transactions on Information Theory* 28(2), 1982 (written at Bell Labs in 1957).
- H. Jégou, M. Douze and C. Schmid, "Product quantization for nearest neighbor search", *IEEE TPAMI* 33(1), 2011 (IVF with quantization).
- Y. A. Malkov and D. A. Yashunin, "Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs", *IEEE TPAMI* 42(4), 2020.
