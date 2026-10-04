# 21. Divide and conquer, and the master theorem

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#21-divide-and-conquer-and-the-master-theorem)

## How it works

Split the problem, solve the parts recursively, combine the answers. The master theorem gives the cost of T(n) = a·T(n/b) + f(n) by comparing f(n) with n^(log_b a); merge sort, Karatsuba multiplication and quickselect are the worked examples.

## In depth (from the catalog page)

Split a problem into smaller copies of itself, solve those, and combine the answers. The running time follows a recurrence `T(n) = a·T(n/b) + O(n^d)`: a subproblems of size n/b, plus nᵈ work to split and combine. The master theorem reads the answer off by comparing a with bᵈ:

- **a < bᵈ:** the top-level work dominates, so `T = O(n^d)`.
- **a = bᵈ:** every level costs about the same, so `T = O(n^d · log n)`.
- **a > bᵈ:** the many small leaves dominate, so `T = O(n^(log_b a))`.

| Algorithm | a | b | d | Time |
|---|---|---|---|---|
| Binary search | 1 | 2 | 0 | `O(log n)` |
| Merge sort | 2 | 2 | 1 | `O(n log n)` |
| Quickselect (average, pivot splits the range about in half) | 1 | 2 | 1 | `O(n)` |
| Karatsuba multiplication | 3 | 2 | 1 | `O(n^1.585)` |
| Strassen matrix multiplication | 7 | 2 | 2 | `O(n^2.807)` |

The exponents 1.585 and 2.807 are log₂3 and log₂7. Doing three half-size multiplications instead of four, or seven half-size matrix products instead of eight, is what beats the schoolbook methods.

```java
static void mergeSort(int[] a, int[] tmp, int lo, int hi) {   // sorts a[lo, hi)
    if (hi - lo < 2) return;
    int mid = (lo + hi) >>> 1;
    mergeSort(a, tmp, lo, mid);
    mergeSort(a, tmp, mid, hi);
    int i = lo, j = mid, k = lo;
    while (i < mid && j < hi) tmp[k++] = (a[j] < a[i]) ? a[j++] : a[i++];   // left element first on ties
    while (i < mid) tmp[k++] = a[i++];
    while (j < hi) tmp[k++] = a[j++];
    System.arraycopy(tmp, lo, a, lo, hi - lo);
}

static int quickselect(int[] a, int k, Random rnd) {   // k-th smallest, 0-based; reorders a
    int lo = 0, hi = a.length - 1;
    while (true) {
        if (lo == hi) return a[lo];
        int p = a[lo + rnd.nextInt(hi - lo + 1)];      // random pivot defeats adversarial input
        int i = lo, j = hi;
        while (i <= j) {                               // Hoare-style partition
            while (a[i] < p) i++;
            while (a[j] > p) j--;
            if (i <= j) { int t = a[i]; a[i] = a[j]; a[j] = t; i++; j--; }
        }
        if (k <= j) hi = j;
        else if (k >= i) lo = i;
        else return a[k];
    }
}

static BigInteger karatsuba(BigInteger x, BigInteger y) {
    int n = Math.max(x.bitLength(), y.bitLength());
    if (n <= 512) return x.multiply(y);                // base case: small operands
    int half = n / 2;
    BigInteger xh = x.shiftRight(half), xl = x.subtract(xh.shiftLeft(half));
    BigInteger yh = y.shiftRight(half), yl = y.subtract(yh.shiftLeft(half));
    BigInteger a = karatsuba(xh, yh);
    BigInteger b = karatsuba(xl, yl);
    BigInteger c = karatsuba(xh.add(xl), yh.add(yl)).subtract(a).subtract(b);   // = xh*yl + xl*yh
    return a.shiftLeft(2 * half).add(c.shiftLeft(half)).add(b);
}
```

> **Verified.** Merge sort matched `Arrays.sort` on 2,000 random arrays, and quickselect matched `sorted[k]` on 5,000. The worst-case comparison count `W(n) = W(⌊n/2⌋) + W(⌈n/2⌉) + n − 1` equals the closed form `n·⌈lg n⌉ − 2^⌈lg n⌉ + 1` for every n from 1 to 4,096. On 200 random arrays of 1,000 ints (counted with an instrumented copy), merge sort averaged 8,706 comparisons: under its worst case of 8,977 and above the information-theoretic floor of log₂(1000!) = 8,529 that no comparison sort can beat on average. For 10 items that floor is ⌈log₂ 10!⌉ = 22 comparisons. Karatsuba matched `BigInteger.multiply` on 300 random pairs of up to 20,000 bits, with either sign.

**Use it for** sorting, selection (medians, top-k), the FFT, closest-pair problems, and anywhere work can be split and run in parallel; Java's fork/join framework and parallel streams split their input the same way. The JDK itself sorts primitives with a dual-pivot quicksort and sorts objects with TimSort, a stable merge-sort hybrid that needs far fewer than n·lg n comparisons on partially sorted input.

> **Pitfall.** The `karatsuba` above is for understanding. `BigInteger.multiply` already switches from schoolbook multiplication to Karatsuba above 80 ints (2,560 bits) and to three-way Toom–Cook above 240 ints (7,680 bits), so don't hand-roll it. And watch the recursion depth of unbalanced splits: a quicksort with bad pivots recurses n levels deep. Pick pivots at random as `quickselect` does, or recurse into the smaller side and loop on the larger.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/21-divide-and-conquer
java DivideAndConquer.java
```

JDK 17 or newer, no build step. It prints 12,100 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
n = 1000: mean merge-sort comparisons = 8706, worst-case bound = 8977, log2(1000!) = 8529
DivideAndConquer: 12100 checks passed
```

## References

- Oracle, [`Arrays` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html): `sort(int[])` is a dual-pivot quicksort.
- OpenJDK 21, [`TimSort.java`](https://github.com/openjdk/jdk/blob/jdk-21%2B35/src/java.base/share/classes/java/util/TimSort.java): "a stable, adaptive, iterative mergesort", O(n log n) in the worst case. [`BigInteger.java`](https://github.com/openjdk/jdk/blob/jdk-21%2B35/src/java.base/share/classes/java/math/BigInteger.java): Karatsuba above 80 ints and Toom–Cook above 240 ints, with no FFT-based multiplication.
