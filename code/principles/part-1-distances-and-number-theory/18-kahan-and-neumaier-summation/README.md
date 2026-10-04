# 18. Summing floating-point numbers: Kahan and Neumaier

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#18-summing-floating-point-numbers-kahan-and-neumaier)

## How it works

Floating-point addition rounds, and the rounding errors pile up over long sums. Kahan summation carries the lost low-order part in a compensation variable and adds it back; Neumaier's variant also handles a new term larger than the running sum.

## In depth (from the catalog page)

Adding doubles one at a time loses low-order bits. Compensated summation carries the lost part along in a second variable.

```java
static double kahan(double[] xs) {
    double sum = 0, c = 0;
    for (double x : xs) {
        double y = x - c;
        double t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    return sum;
}

static double neumaier(double[] xs) {           // also handles a new term larger than the running sum
    double sum = 0, c = 0;
    for (double x : xs) {
        double t = sum + x;
        if (Math.abs(sum) >= Math.abs(x)) c += (sum - t) + x;
        else c += (x - t) + sum;
        sum = t;
    }
    return sum + c;
}
```

| Case | Naive loop | Kahan | Neumaier | `DoubleStream.sum()` |
|---|---|---|---|---|
| 10 × 0.1 (want 1.0) | 0.9999999999999999 | 1.0 | 1.0 | 1.0 |
| {1, 1e100, 1, −1e100} (want 2) | 0.0 | 0.0 | **2.0** | 0.0 |
| 100,000 mixed-magnitude values (absolute error against the exact sum) | 7.573e-08 | 2.880e-10 | 1.776e-10 | 2.880e-10 |

> **Verified.** The table is the program's output on JDK 21. Compensation cut the error by a factor of about 260 (Kahan) and 430 (Neumaier) on the random data. Kahan fails when a new term is far larger than the running sum, as with the 1e100 case; Neumaier's variant handles both orderings.

The `DoubleStream.sum()` Javadoc says it may use compensated summation and that results can vary with the order of operations. On this JDK it behaved like Kahan in all three cases. Python 3.12 changed the built-in `sum()` to use Neumaier summation for floats. If you need an exactly rounded result, add with `BigDecimal`, as the test harness does for its reference value.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/18-kahan-and-neumaier-summation
java CompensatedSummation.java
```

JDK 17 or newer, no build step. It prints 5 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
10 x 0.1: naive = 0.9999999999999999, Kahan = 1.0, DoubleStream.sum = 1.0
{1, 1e100, 1, -1e100} true answer 2: naive = 0.0, Kahan = 0.0, Neumaier = 2.0, DoubleStream.sum = 0.0
100k mixed-magnitude values, abs error vs exact: naive 7.573e-08, Kahan 2.880e-10, Neumaier 1.776e-10, DoubleStream.sum 2.880e-10
CompensatedSummation: 5 checks passed
```

## References

- Oracle, [`DoubleStream` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/stream/DoubleStream.html): `sum()` may use compensated summation.
- Python documentation, [What's New In Python 3.12](https://docs.python.org/3/whatsnew/3.12.html): built-in `sum()` now uses Neumaier summation.
