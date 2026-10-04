# 28. Kadane's algorithm and the Boyer–Moore majority vote

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#28-kadanes-algorithm-and-the-boyermoore-majority-vote)

## How it works

Kadane's algorithm finds the maximum-sum subarray in one pass: the best sum ending here is either this element alone or this element plus the best sum ending at the previous one. Boyer–Moore majority vote finds an element occurring more than n/2 times with one counter, then a second pass confirms it.

## In depth (from the catalog page)

Two famous one-pass algorithms whose power is a tiny piece of state that summarizes everything seen so far. Kadane (popularized by Bentley in the 1980s): the best subarray ending at this position is either the element alone or the element added to the best subarray ending at the previous position. Boyer–Moore (1981): keep a candidate and a counter; the same value adds a vote and a different value cancels one. If a value fills more than half the positions, it survives every cancellation.

```java
static long maxSubarray(int[] a) {                      // best sum of a non-empty contiguous subarray
    long best = a[0], cur = a[0];
    for (int i = 1; i < a.length; i++) {
        cur = Math.max(a[i], cur + a[i]);               // extend the best run ending here, or start fresh
        best = Math.max(best, cur);
    }
    return best;
}

static int majority(int[] a) {                          // correct only if a majority element exists
    int cand = 0, count = 0;
    for (int x : a) {
        if (count == 0) cand = x;
        count += (x == cand) ? 1 : -1;
    }
    return cand;
}
```

> **Verified.** `maxSubarray` matched a brute-force check of every subarray on 3,000 random arrays, gives 6 on the classic input −2, 1, −3, 4, −1, 2, 1, −5, 4, and returns −1 on −3, −1, −2. `majority` returned the majority element whenever a value filled more than half of the positions, over 3,000 random arrays of up to 25 elements drawn from {0, 1, 2}. With no majority the answer is arbitrary: {1, 2, 3} returns 3.

<!-- -->

> **Pitfall.** Boyer–Moore finds the majority element only *if one exists*. When that isn't guaranteed, run a second pass that counts the candidate and confirms it. Kadane as written needs a non-empty array and returns the largest single element when every value is negative; start `best` at 0 if an empty subarray is allowed.

**Use it for** maximum-profit and maximum-gain problems (the best buy-then-sell pair is Kadane run on the day-to-day differences), streaming majority and heavy hitters (Misra–Gries generalizes Boyer–Moore to the k most frequent items), and as a model for any computation where a small summary can be updated one element at a time.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/28-kadane-and-boyer-moore-majority
java KadaneAndMajority.java
```

JDK 17 or newer, no build step. It prints 3,925 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
KadaneAndMajority: 3925 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
