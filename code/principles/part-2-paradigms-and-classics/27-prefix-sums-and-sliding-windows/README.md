# 27. Prefix sums, difference arrays, sliding windows and the monotonic deque

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#27-prefix-sums-difference-arrays-sliding-windows-and-the-monotonic-deque)

## How it works

Precompute running totals so any range sum is one subtraction; a difference array does the reverse for range updates. A sliding window moves two pointers through the array once, and a monotonic deque keeps the window's maximum available in O(1).

## In depth (from the catalog page)

Spend O(n) once so that every later query costs O(1). Let `p[i]` be the sum of the first i elements; then the sum of any range is `p[r] − p[l]`. Run the idea backwards and you get the *difference array*: to add v to every element of a range, change two entries, then rebuild the whole array in one pass. Combine prefix sums with a hash map and you can count subarrays with a given sum, even with negative numbers. For "the maximum of every window of size k", a *monotonic deque* keeps only the indices that could still become a maximum, so each index is added once and removed at most once.

```java
static long[] prefix(int[] a) {                         // p[i] = sum of a[0..i)
    long[] p = new long[a.length + 1];
    for (int i = 0; i < a.length; i++) p[i + 1] = p[i] + a[i];
    return p;
}                                                       // sum of a[l..r) is p[r] - p[l]

// difference array: add v to every position in [l, r) with two writes, then rebuild in one pass
long[] diff = new long[n + 1];
diff[l] += v; diff[r] -= v;                             // repeat for each update
long run = 0;
for (int i = 0; i < n; i++) { run += diff[i]; /* run is the total added at position i */ }

static int countSubarraysWithSum(int[] a, int target) { // works with negative numbers too
    Map<Long, Integer> seen = new HashMap<>();
    seen.put(0L, 1);
    long sum = 0;
    int count = 0;
    for (int x : a) {
        sum += x;
        count += seen.getOrDefault(sum - target, 0);    // earlier prefixes that leave exactly `target`
        seen.merge(sum, 1, Integer::sum);
    }
    return count;
}

static int[] slidingMax(int[] a, int k) {               // maximum of every window of size k, O(n)
    int[] out = new int[a.length - k + 1];
    Deque<Integer> dq = new ArrayDeque<>();             // indices whose values are decreasing
    for (int i = 0; i < a.length; i++) {
        while (!dq.isEmpty() && a[dq.peekLast()] <= a[i]) dq.pollLast();
        dq.addLast(i);
        if (dq.peekFirst() <= i - k) dq.pollFirst();
        if (i >= k - 1) out[i - k + 1] = a[dq.peekFirst()];
    }
    return out;
}
```

> **Verified.** On 2,000 random arrays of up to 40 values between −10 and 10, range sums from `prefix` matched a direct sum, `slidingMax` matched a scan of every window, and `countSubarraysWithSum` matched the O(n²) count, negative numbers and zero-sum cases included. The difference array matched a naive update loop on 500 random sets of 20 range updates.

<!-- -->

> **Pitfall.** The shrinking-window (two-pointer) technique needs monotonic behavior: "shortest window with sum at least k" works only when every number is non-negative. With negative numbers, use prefix sums and a hash map as above. Accumulate in `long`, because the prefix sum of a long run of `int` values can overflow an `int`.

**Use it for** range-sum queries, summed-area tables (integral images) in image processing, event sweeps (+1 at a start, −1 at an end, then one pass: that is a difference array), histograms and cumulative metrics, "maximum over the last k readings" in stream processing, and rate-limit windows.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/27-prefix-sums-and-sliding-windows
java PrefixSumsAndWindows.java
```

JDK 17 or newer, no build step. It prints 33,846 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
PrefixSumsAndWindows: 33846 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
