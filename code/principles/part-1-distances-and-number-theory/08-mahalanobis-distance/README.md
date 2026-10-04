# 8. Mahalanobis distance

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#8-mahalanobis-distance)

## How it works

Distance measured in units of the data's own spread: it rescales and decorrelates features with the inverse covariance matrix, so a point far out along a direction where the data barely varies counts as far. With the identity matrix it is Euclidean distance.

## In depth (from the catalog page)

Euclidean distance after accounting for each feature's spread and the correlations between features: `d = √((x − μ)ᵀ Σ⁻¹ (x − μ))`. It answers "how unusual is this point for this distribution", not just "how far".

```java
static double mahalanobis2(double[] x, double[] mu, double[][] cov) {   // 2-D, explicit inverse
    double a = cov[0][0], b = cov[0][1], c = cov[1][0], d = cov[1][1];
    double det = a * d - b * c;
    double dx = x[0] - mu[0], dy = x[1] - mu[1];
    return Math.sqrt((dx * (d * dx - b * dy) + dy * (-c * dx + a * dy)) / det);
}
```

> **Verified.** With the identity covariance it equals Euclid (the 3-4-5 triangle gives 5). With `cov = [[1, 0.9], [0.9, 1]]`, the points (1, 1) and (1, −1) are both √2 ≈ 1.414 from the mean, yet their Mahalanobis distances are 1.026 and 4.472. The first lies along the correlation and is typical, and the second is a strong outlier.

**Use it for** anomaly detection, and for scoring how far a behavioral sample (a typing-rhythm or motion feature vector, say) sits from a user's baseline. It needs a stable covariance estimate, so keep enough samples relative to the number of dimensions. In n dimensions use a linear-algebra library and solve with a Cholesky factorization rather than inverting the matrix.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/08-mahalanobis-distance
java MahalanobisDistance.java
```

JDK 17 or newer, no build step. It prints 2 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
same Euclid distance sqrt(2); Mahalanobis along correlation = 1.0260, against = 4.4721
MahalanobisDistance: 2 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
