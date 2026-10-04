# 19. Comparing floating-point numbers, and money

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#19-comparing-floating-point-numbers-and-money)

## How it works

Never compare doubles with ==: use a tolerance that is relative for large values and absolute near zero. For money use BigDecimal built from strings (new BigDecimal(0.1) keeps the binary error), and remember that equals() is scale-sensitive while compareTo() is not.

## In depth (from the catalog page)

Two doubles that should be equal rarely are, so compare with a tolerance that combines a relative part (for large numbers) and an absolute part (for numbers near zero).

```java
static boolean nearlyEqual(double a, double b, double relTol, double absTol) {
    return Math.abs(a - b) <= Math.max(absTol, relTol * Math.max(Math.abs(a), Math.abs(b)));
}
```

> **Verified.** `0.1 + 0.2 != 0.3` is true. `(0.1 + 0.2) + 0.3` is 0.6000000000000001 but `0.1 + (0.2 + 0.3)` is 0.6, so double addition is not associative, and a parallel reduction that changes the order can change the result. With a relative tolerance of 1e-9, `0.1 + 0.2` equals 0.3 and `1e10 + 1` equals 1e10. Near zero, a purely relative test says 1e-20 and 2e-20 differ, and adding an absolute tolerance of 1e-12 fixes it.

For money, never use `double`. Use `BigDecimal` built from strings, or integer minor units such as cents:

- `new BigDecimal("0.1").add(new BigDecimal("0.2")).equals(new BigDecimal("0.3"))` is true.
- `new BigDecimal(0.1)` is 0.1000000000000000055511151231257827021181583404541015625, because that constructor takes the exact binary value. Use `new BigDecimal("0.1")` or `BigDecimal.valueOf(0.1)`.
- `new BigDecimal("2.0").equals(new BigDecimal("2.00"))` is false because `equals` compares the scale too. Use `compareTo(...) == 0`.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/19-comparing-floats-and-money
java ComparingFloats.java
```

JDK 17 or newer, no build step. It prints 6 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
new BigDecimal(0.1) = 0.1000000000000000055511151231257827021181583404541015625
(0.1+0.2)+0.3 = 0.6000000000000001, 0.1+(0.2+0.3) = 0.6
ComparingFloats: 6 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
