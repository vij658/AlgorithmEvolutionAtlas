# 26. Amortized analysis

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#26-amortized-analysis)

## How it works

Some operations are occasionally expensive but cheap on average over any sequence. Doubling a dynamic array costs O(n) on a resize but O(1) amortized per append, because each resize is paid for by the appends before it. The program counts element copies to show it.

## In depth (from the catalog page)

A single operation may be expensive as long as the *average* over any sequence of operations is cheap. A dynamic array that doubles its capacity when full copies 1 + 2 + 4 + … < 2n elements over n appends, so each append is O(1) amortized even though one of them copies half the array. The growth has to be geometric: growing by a constant makes the total quadratic.

```java
static final class IntList {
    int[] data = new int[1];
    int size;
    void add(int x) {
        if (size == data.length) data = Arrays.copyOf(data, size * 2);   // copies `size` elements
        data[size++] = x;
    }
}

static long copiesGeometric(int n, double factor) {     // count-only simulation of n appends
    long copies = 0;
    int capacity = 1;
    for (int size = 0; size < n; size++)
        if (size == capacity) { copies += size; capacity = Math.max(capacity + 1, (int) (capacity * factor)); }
    return copies;
}

static long copiesLinear(int n, int step) {             // the same, growing by a constant step
    long copies = 0;
    int capacity = 1;
    for (int size = 0; size < n; size++)
        if (size == capacity) { copies += size; capacity += step; }
    return copies;
}

static final class TwoStackQueue {                      // O(1) amortized push and pop
    private final ArrayDeque<Integer> in = new ArrayDeque<>(), out = new ArrayDeque<>();
    void push(int x) { in.push(x); }
    int pop() {
        if (out.isEmpty()) while (!in.isEmpty()) out.push(in.pop());   // reverse once, only when needed
        return out.pop();
    }
    boolean isEmpty() { return in.isEmpty() && out.isEmpty(); }
}
```

> **Verified.** `IntList` kept its contents over 100,000 random appends (with a copy counter in the full program), and at every size up to 2,000,000 the doubling policy had copied fewer than 2n elements in total. For 1,000,000 appends, doubling copies 1,048,575 elements (1.049 per append), growth by 1.5× copies 2.100 per append, and growth by a constant 10, taken to n = 100,000, copies 499,960,000 elements, which is 5,000 per append. The two-stack queue returned the same order as `ArrayDeque` over 100,000 random operations, and no element moved between its stacks more than once (a move counter in the full program checks this). On this JDK, appending to a `StringBuilder` took its capacity through 16, 34, 70, 142, 286, 574, … (twice the old capacity plus 2, the rule its `ensureCapacity` Javadoc gives), and a reflection probe of `ArrayList` showed 10, 15, 22, 33, 49, 73, 109, … where each capacity is the previous one plus half of it.

<!-- -->

> **Pitfall.** Amortized O(1) is not worst-case O(1): the append that triggers growth still copies everything, which matters in latency-sensitive code. If you know the size, say so with `new ArrayList<>(n)` or `ensureCapacity`, and no copying happens at all. The `ArrayList` Javadoc promises constant amortized time but not a growth factor, so the 1.5× above is this JDK's behavior, not a contract.

**Use it for** reasoning about `ArrayList`, `StringBuilder`, hash-table resizing and any structure that occasionally rebuilds itself. The three standard proof methods are aggregate (total cost divided by n), accounting (cheap operations pre-pay for the expensive one later) and potential functions. The two-stack queue is the textbook accounting example: each element is moved from the input stack to the output stack at most once, so total moves never exceed total pushes.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/26-amortized-analysis
java AmortizedAnalysis.java
```

JDK 17 or newer, no build step. It prints 2,133,399 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
1,000,000 appends: doubling copies 1048575 elements (1.049 per append), 1.5x growth 2.100 per append; +10 growth at n = 100,000 copies 499,960,000 elements (5000 per append)
StringBuilder capacities while appending 5,000 chars: [16, 34, 70, 142, 286, 574, 1150, 2302, 4606, 9214]
(ArrayList growth probe skipped; run with --add-opens java.base/java.util=ALL-UNNAMED to enable it)
AmortizedAnalysis: 2133399 checks passed
```

## References

- Oracle, [`StringBuilder`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html): `ensureCapacity` grows to twice the old capacity plus 2. [`ArrayList`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html): the growth policy is unspecified beyond constant amortized time.
