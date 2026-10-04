# 41. Newton's method

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#41-newtons-method)

## How it works

To solve f(x) = 0, follow the tangent line: x ← x − f(x)/f'(x). Near a simple root the number of correct digits roughly doubles each step (quadratic convergence); for √a this is the ancient 'average x and a/x' rule.

## In depth (from the catalog page)

To solve f(x) = 0, replace f by its tangent line at the current guess and jump to where the tangent crosses zero: `x ← x − f(x)/f′(x)`. Near a simple root the new error is about the old error squared divided by 2x, so the number of correct digits roughly doubles with every step. For square roots it becomes the Babylonian method, `x ← (x + a/x)/2`.

```java
static double newtonSqrt(double a) {                     // a > 0
    double x = a >= 1 ? a : 1;                           // start at or above sqrt(a) so iterates decrease
    for (int i = 0; i < 200; i++) {
        double next = 0.5 * (x + a / x);
        if (next >= x) break;                            // no further progress: converged to machine precision
        x = next;
    }
    return x;
}

static long isqrt(long n) {                              // floor(sqrt(n)), exact for every non-negative long
    if (n < 2) return n;
    long x = (long) Math.sqrt((double) n);               // good first guess, can be off by one for large n
    while (x > n / x) x--;                               // x * x > n, written without overflow
    while (x + 1 <= n / (x + 1)) x++;                    // (x + 1)^2 <= n
    return x;
}
```

> **Verified.** Starting from 2, Newton's iteration for √2 had absolute errors of 8.579e-02, 2.453e-03, 2.124e-06, 1.595e-12 and 2.220e-16 after steps 1 to 5, each matching the exact identity `x′ − r = (x − r)² / (2x)` to within 0.1% until the error reached the rounding floor. `newtonSqrt` agreed with `Math.sqrt` to a worst relative error of 2.22e-16 over 200,000 values between 1e-10 and 1e10, using 5 iterations for 2 and 21 for 1e10. `isqrt` matched `BigInteger.sqrt` on 1,000,000 random longs and on 600,000 values within 1 of a perfect square, up to 3,037,000,499². The shortcut `(long) Math.sqrt((double) n)` was wrong for 195,694 of those 600,000 values, always one too big: above 2⁵³ converting n to a double rounds off its low bits, so a number just below a perfect square can round up to it. Newton on f(x) = ∛x from x₀ = 1 sends x to −2x every step, so after 8 steps x = 255.99999999999994, which is (−2)⁸ up to rounding: the iteration diverges.

<!-- -->

> **Pitfall.** Newton needs a good starting point and a derivative that stays away from zero; otherwise it can diverge, cycle or jump far away, as with ∛x above. Safeguard it with bisection (entry 22): accept a Newton step only when it stays inside an interval known to contain the root, and bisect otherwise. For exact integer square roots never cast `Math.sqrt`; use `isqrt` or `BigInteger.valueOf(n).sqrt()`.

**Use it for** root-finding and optimization: solving for a yield or interest rate, implied volatility, nonlinear equations in many variables (with a Jacobian), and Newton-type optimizers. The famous fast inverse square root from Quake III is a clever first guess followed by one Newton step.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/41-newtons-method
java NewtonsMethod.java
```

JDK 17 or newer, no build step. It prints 1,600,023 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Newton for sqrt(2) from x0 = 2, absolute error per iteration: 1: 8.579e-02  2: 2.453e-03  3: 2.124e-06  4: 1.595e-12  5: 2.220e-16  
newtonSqrt vs Math.sqrt over 200,000 values in [1e-10, 1e10]: worst relative error 2.22e-16; iterations for a = 2: 5, for a = 1e10: 21
isqrt exact on 1,000,000 random longs and 600000 near-square values; plain (long) Math.sqrt(n) was wrong for 195694 of those near-square values, too big in 195694 of them
Newton on cbrt(x) from x0 = 1 diverges: after 8 steps x = 255.99999999999994
NewtonsMethod: 1600023 checks passed
```

## References

- **Lecture:** [MIT 6.006 Lecture 12: Square Roots, Newton's Method](https://www.youtube.com/watch?v=2YeJ-5UAke8)
- **Read:** [Square Roots via Newton's Method — MIT 18.335 note (S. G. Johnson)](https://math.mit.edu/~stevenj/18.335/newton-sqrt.pdf)
- **History and more links:** [Era 1 reference catalog](../../../../book/era-01-the-first-algorithms/reference-catalog.md#4-the-square-root-of-2-on-ybc-7289)
