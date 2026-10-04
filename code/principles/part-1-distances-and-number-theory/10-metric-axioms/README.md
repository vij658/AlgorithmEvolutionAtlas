# 10. The four metric axioms

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#10-the-four-metric-axioms)

## How it works

A metric must be non-negative, zero only for identical points, symmetric, and obey the triangle inequality. Indexes and pruning tricks (BK-trees, metric trees) rely on the triangle inequality, so the program checks which common 'distances' satisfy it and which (squared L2, 1 − cosine) do not.

## In depth (from the catalog page)

A function is a true distance (a metric) if it is non-negative, zero only for identical inputs, symmetric, and obeys the triangle inequality `d(x, z) ≤ d(x, y) + d(y, z)`. Metric trees (VP-trees, BK-trees), many clustering guarantees and nearest-neighbour pruning depend on all four.

```java
static double angle(double[] u, double[] v) {      // a true metric on directions
    return Math.acos(Math.max(-1.0, Math.min(1.0, cosine(u, v))));
}
```

> **Verified.** L1, L2, L∞ and Levenshtein passed the triangle inequality on random data (entries 3 to 6), and squared L2 failed it. The popular "cosine distance" `1 − cos θ` fails too: for vectors at 0°, 45° and 90°, d(u, w) = 1.0000 but d(u, v) + d(v, w) = 0.5858. The angle itself passed on 1,000 random 8-D triples.

<!-- -->

> **Rule of thumb.** If a library promises metric-space speedups (BK-tree, VP-tree, triangle-inequality pruning in k-means), give it a real metric. For cosine, use the angle, or Euclidean distance on normalized vectors.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/10-metric-axioms
java MetricAxioms.java
```

JDK 17 or newer, no build step. It prints 1,001 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
1 - cos at 0/45/90 degrees: d(u,w) = 1.0000 > d(u,v) + d(v,w) = 0.5858
MetricAxioms: 1001 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
