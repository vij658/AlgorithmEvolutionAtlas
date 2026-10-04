# 3. Euclidean distance (L2)

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#3-euclidean-distance-l2)

## How it works

The straight-line distance: the square root of the sum of squared coordinate differences. Comparing squared distances avoids the square root when only the order matters. Math.hypot avoids the overflow that the naive formula hits with huge coordinates.

## In depth (from the catalog page)

The Pythagorean theorem in n dimensions: `d(p, q) = √Σ(pᵢ − qᵢ)²`.

```java
static double dist2(double[] p, double[] q) {     // squared distance
    double s = 0;
    for (int i = 0; i < p.length; i++) { double d = p[i] - q[i]; s += d * d; }
    return s;
}

static double euclid(double[] p, double[] q) { return Math.sqrt(dist2(p, q)); }
```

Three principles hide in this one formula:

- **Skip the square root when you only compare.** The square root is monotonic, so squared distances rank neighbours the same way.
- **Squared distance is not a metric.** On a line, the points 0, 1 and 2 give d(0, 2) = 4 but d(0, 1) + d(1, 2) = 2, so the triangle inequality fails. Don't feed squared distances to algorithms that prune using that inequality.
- **Mind overflow.** Squaring large coordinates can overflow even when the answer is representable. `Math.hypot` avoids that, at the cost of speed.

> **Verified.** `euclid((0,0), (3,4))` is exactly 5.0. With x = y = 1e200, `Math.sqrt(x*x + y*y)` returns Infinity, while `Math.hypot(x, y)` returns about 1.414e200. Over 200 random queries against 50 five-dimensional points each, squared distance picked the same nearest neighbour as true distance every time. The squared version broke the triangle inequality on the 0-1-2 example and the true distance did not.

**Use it for** nearest-neighbour search, k-means, clustering, and any "how far apart are these numeric vectors" question where the features share one scale. Standardize the features first when they don't.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/03-euclidean-distance
java EuclideanDistance.java
```

JDK 17 or newer, no build step. It prints 206 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
EuclideanDistance: 206 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
