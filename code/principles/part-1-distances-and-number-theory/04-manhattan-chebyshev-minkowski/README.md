# 4. Manhattan (L1), Chebyshev (L∞) and Minkowski (Lp)

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#4-manhattan-l1-chebyshev-l-and-minkowski-lp)

## How it works

Manhattan (L1) adds absolute coordinate differences, Chebyshev (L∞) takes the largest one, and Minkowski (Lp) generalises both: p = 1 is Manhattan, p = 2 is Euclidean, and p → ∞ approaches Chebyshev. The right one is the one that matches how things move.

## In depth (from the catalog page)

Three relatives of L2: sum the absolute differences (L1), take the largest one (L∞), or generalize both with an exponent p.

```java
static double manhattan(double[] p, double[] q) {
    double s = 0;
    for (int i = 0; i < p.length; i++) s += Math.abs(p[i] - q[i]);
    return s;
}

static double chebyshev(double[] p, double[] q) {
    double m = 0;
    for (int i = 0; i < p.length; i++) m = Math.max(m, Math.abs(p[i] - q[i]));
    return m;
}

static double minkowski(double[] p, double[] q, double r) {
    double s = 0;
    for (int i = 0; i < p.length; i++) s += Math.pow(Math.abs(p[i] - q[i]), r);
    return Math.pow(s, 1.0 / r);
}
```

> **Verified.** From (0, 0) to (3, 4): L1 = 7, L∞ = 4, L2 = 5. Over 1,000 random 4-D triples all three obeyed the triangle inequality, and `L∞ ≤ L2 ≤ L1` always held. Minkowski gives 7 at p = 1 and 5 at p = 2, and 4.000000 (to six decimals) at p = 50, showing the slide toward Chebyshev as p grows.

Pick the metric that matches how things move: L1 for four-direction grid movement, L∞ for eight-direction (king) moves, L2 for free movement. These are also the usual admissible heuristics for A* search (Part 2). L1 is less dominated by one huge coordinate than L2, which is why L1 penalties (Lasso) give sparse models and L1 distances are more robust to outliers.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/04-manhattan-chebyshev-minkowski
java MinkowskiDistances.java
```

JDK 17 or newer, no build step. It prints 5,003 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
MinkowskiDistances: 5003 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
