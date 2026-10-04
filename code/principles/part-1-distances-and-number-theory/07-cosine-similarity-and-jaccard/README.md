# 7. Cosine similarity and Jaccard index

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#7-cosine-similarity-and-jaccard-index)

## How it works

Cosine similarity is the dot product of two vectors divided by the product of their lengths: it measures angle and ignores size. Jaccard similarity is |A ∩ B| / |A ∪ B| for sets. 1 − cosine is not a true distance (it breaks the triangle inequality); the angle is.

## In depth (from the catalog page)

Cosine measures the angle between two vectors and ignores their length. Jaccard is the overlap of two sets divided by their union.

```java
static double cosine(double[] u, double[] v) {
    double dot = 0, nu = 0, nv = 0;
    for (int i = 0; i < u.length; i++) { dot += u[i] * v[i]; nu += u[i] * u[i]; nv += v[i] * v[i]; }
    return dot / (Math.sqrt(nu) * Math.sqrt(nv));
}

static <T> double jaccard(Set<T> a, Set<T> b) {
    Set<T> inter = new HashSet<>(a); inter.retainAll(b);
    Set<T> union = new HashSet<>(a); union.addAll(b);
    return union.isEmpty() ? 1.0 : (double) inter.size() / union.size();
}
```

> **Verified.** Orthogonal vectors give 0, parallel vectors give 1, opposite vectors give −1. For 100 random unit vectors in 8-D, `‖u − v‖² = 2 − 2·cos θ` held to 1e-12. `jaccard({1,2,3}, {2,3,4})` is 0.5.

For unit vectors that identity means ranking by cosine and ranking by Euclidean distance give the same order, which is why vector databases store normalized embeddings and rank by dot product. Jaccard fits shingles, tags and permission sets, and MinHash (Broder, 1997) estimates it cheaply at scale.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/07-cosine-similarity-and-jaccard
java CosineAndJaccard.java
```

JDK 17 or newer, no build step. It prints 104 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
CosineAndJaccard: 104 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
