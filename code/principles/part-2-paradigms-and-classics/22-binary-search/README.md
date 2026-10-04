# 22. Binary search, and binary search on the answer

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#22-binary-search-and-binary-search-on-the-answer)

## How it works

Keep an interval that must contain the answer and halve it each step: O(log n) comparisons. The same idea finds the smallest value that makes a monotone yes/no test succeed ('binary search on the answer'). Compute the midpoint as lo + (hi − lo)/2 to avoid overflow.

## In depth (from the catalog page)

If a yes/no question is monotone, meaning every "no" comes before every "yes", you can find the boundary with O(log n) questions by always asking about the middle. Two refinements turn this from a lookup into a general tool. Ask for the *first* position where the answer is yes (`lowerBound`) instead of any position that matches. And apply it to answers instead of array positions: "what is the smallest capacity that still ships everything in time?"

```java
static int lowerBound(int[] a, int key) {          // first index i with a[i] >= key, or a.length
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] < key) lo = mid + 1; else hi = mid;
    }
    return lo;
}

static int upperBound(int[] a, int key) {          // first index i with a[i] > key, or a.length
    int lo = 0, hi = a.length;
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (a[mid] <= key) lo = mid + 1; else hi = mid;
    }
    return lo;
}

static int daysNeeded(int[] w, int cap) {          // days to ship packages in order with a daily limit of cap
    int days = 1, load = 0;
    for (int x : w) {
        if (load + x > cap) { days++; load = 0; }
        load += x;
    }
    return days;
}

static int minShipCapacity(int[] weights, int days) {   // smallest capacity that ships in order within `days`
    int lo = Arrays.stream(weights).max().getAsInt();    // must fit the heaviest package
    int hi = Arrays.stream(weights).sum();               // ships everything on day one
    while (lo < hi) {
        int mid = (lo + hi) >>> 1;
        if (daysNeeded(weights, mid) <= days) hi = mid; else lo = mid + 1;
    }
    return lo;
}

static double bisect(DoubleUnaryOperator f, double lo, double hi, int iterations) {   // f increasing, f(lo) <= 0 < f(hi)
    for (int i = 0; i < iterations; i++) {
        double mid = 0.5 * (lo + hi);
        if (f.applyAsDouble(mid) > 0) hi = mid; else lo = mid;
    }
    return 0.5 * (lo + hi);
}
```

> **Verified.** `lowerBound` and `upperBound` matched a linear scan on 5,000 random arrays full of duplicates, for every key from −1 to 21, and they handle the empty array. For every array size from 1 to 1,500 and every distinct search outcome, `lowerBound` made at most ⌊log₂ n⌋ + 1 probes. On 1,000,000 sorted ints the worst case seen was 20 probes, which is the bound (2²⁰ = 1,048,576). `minShipCapacity` matched a linear scan on 3,000 random cases, and the classic weights 1 to 10 in 5 days give 15. Bisection of x² − 2 on [1, 2] lands within 1e-12 of √2 after 40 halvings, since ⌈log₂(10¹²)⌉ = 40.

<!-- -->

> **Pitfall.** `Arrays.binarySearch` and `Collections.binarySearch` promise nothing about which duplicate they return, and they report a missing key as `-(insertion point) - 1`. When you need the first or last occurrence, or the insertion point, write the bound functions above. Other classic mistakes: `(lo + hi) / 2` overflowing (entry 20), a loop condition that never shrinks the range, and a predicate that is not monotone, which returns garbage without any error.

<!-- -->

> **Rule of thumb.** Use a half-open range `[lo, hi)`, loop while `lo < hi`, and always move one end to `mid` or `mid + 1`. That shape terminates on every input and avoids most off-by-one bugs.

**Use it for** `git bisect` (finding the first bad commit), minimizing a maximum or maximizing a minimum (shipping, scheduling, allocation), capacity and rate-limit calculations, root-finding on a monotone function, and any sorted structure. Databases run the same search inside sorted pages and files.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/22-binary-search
java BinarySearch.java
```

JDK 17 or newer, no build step. It prints 2,372,505 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
1,000,000 sorted ints: at most 20 probes observed (bound 20)
BinarySearch: 2372505 checks passed
```

## References

- Bloch, J., [Extra, Extra – Read All About It: Nearly All Binary Searches and Mergesorts are Broken](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/) (2006): the `(low + high) / 2` overflow.
