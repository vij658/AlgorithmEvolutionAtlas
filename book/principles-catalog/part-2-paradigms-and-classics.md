---
Title: Coding Principles Catalog
Part: 2
Part-Title: Algorithm paradigms and classics
Subtitle: The named strategies and textbook algorithms behind most real code, each with Java you can run and a measured result.
Checks: 6,914,381
JDK: 21.0.12
Java: ../../code/principles/part-2-paradigms-and-classics/*/*.java
Description: Twenty-two named principles, from divide and conquer, dynamic programming and Dijkstra's algorithm to Bloom filters, HyperLogLog and Newton's method, each with verified Java code.
---

## How to read Part 2

Same layout as Part 1: the idea, what it costs, Java code, a **Verified** note saying exactly what was run, and when to reach for it (or not). Every algorithm was checked against a slower, obviously correct version on random inputs: brute force, `Arrays.sort`, `String.indexOf`, `BigInteger`, Floyd–Warshall. That comparison is the cheapest way to catch off-by-one errors, and it is a principle in its own right. Randomized checks use fixed seeds, so the numbers reproduce.

All code was compiled and run on OpenJDK 21. Snippets leave out imports and `main`, and where a snippet differs from the program only by a counter used to take a measurement, the Verified note says so. Every entry has its own full program, in the repository's `code/principles` folder and at the bottom of this page; each compiles as it is on JDK 17 or newer and runs with `java <File>.java`.

Part 2 has five groups. **A** covers the design paradigms: divide and conquer, binary search, dynamic programming, greedy algorithms, backtracking and amortized analysis (entries 21–26). **B** covers linear-time techniques that replace nested loops with a single pass (27–31). **C** covers graph algorithms (32–37). **D** covers probabilistic data structures that trade a little accuracy for a lot of memory (38–40). **E** covers numerical iteration (41–42). A quick-reference table closes the part.

## A. Design paradigms

### 21. Divide and conquer, and the master theorem

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

### 22. Binary search, and binary search on the answer

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

### 23. Dynamic programming

When a problem has *overlapping subproblems* (the same smaller question comes up again and again) and *optimal substructure* (the best answer is assembled from best answers to smaller questions), solve each subproblem once and store the result. Bellman named the method in the 1950s. The recipe: define the state, write the recurrence, fill the table in an order that satisfies the dependencies, and keep only the part of the table the recurrence still needs. The cost is the number of states times the work per state.

```java
static int knapsack(int[] w, int[] v, int cap) {
    int[] best = new int[cap + 1];
    for (int i = 0; i < w.length; i++)
        for (int c = cap; c >= w[i]; c--)              // go downward so each item is used at most once
            best[c] = Math.max(best[c], best[c - w[i]] + v[i]);
    return best[cap];
}

static int lcsLength(String a, String b) {             // longest common subsequence
    int[][] dp = new int[a.length() + 1][b.length() + 1];
    for (int i = 1; i <= a.length(); i++)
        for (int j = 1; j <= b.length(); j++)
            dp[i][j] = a.charAt(i - 1) == b.charAt(j - 1)
                    ? dp[i - 1][j - 1] + 1
                    : Math.max(dp[i - 1][j], dp[i][j - 1]);
    return dp[a.length()][b.length()];
}

static int minCoins(int[] coins, int amount) {
    final int INF = Integer.MAX_VALUE / 2;
    int[] dp = new int[amount + 1];
    Arrays.fill(dp, INF);
    dp[0] = 0;
    for (int a = 1; a <= amount; a++)
        for (int c : coins)
            if (c <= a) dp[a] = Math.min(dp[a], dp[a - c] + 1);
    return dp[amount] >= INF ? -1 : dp[amount];
}

static long fibNaive(int n) { return n < 2 ? n : fibNaive(n - 1) + fibNaive(n - 2); }

static long fibMemo(int n, long[] memo) {              // top-down: recursion plus a cache
    if (n < 2) return n;
    if (memo[n] != 0) return memo[n];
    return memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
}
```

> **Verified.** `knapsack` matched an enumeration of every subset on 500 random instances of up to 12 items, and the textbook case (weights 1, 3, 4, 5, values 1, 4, 5, 7, capacity 7) gives 9. `lcsLength` matched an enumeration of every subsequence on 500 random string pairs, and "AGGTAB" against "GXTXAYB" gives 4. `minCoins` matched a breadth-first search on 500 random coin sets. For fib(30), naive recursion made 2,692,537 calls and the memoized version made 59 (counted with instrumented copies of the two functions).

Knapsack runs in O(n·W), where W is the capacity's *value*, not its length in bits. That makes it pseudo-polynomial: one more bit in W doubles the work. The general problem is NP-hard, and this table is why it stays practical when W is modest. Levenshtein distance (entry 6) is the same pattern with a different recurrence.

> **Pitfall.** In 0/1 knapsack the capacity loop must run downward. Run it upward and one item can be counted many times, which solves the unbounded variant instead. The other trap is stack depth: top-down memoization recurses as deep as the longest dependency chain, so a state space with 100,000 steps can overflow the stack where the bottom-up loop would not.

**Use it for** `diff` and version-control merges (longest common subsequence), sequence alignment in bioinformatics, spell-correction suggestions, text justification, the Viterbi algorithm in speech and tagging, shortest paths on DAGs, and parsing (CYK, Earley). If you can phrase the answer as "the best of several choices, each leaving a smaller version of the same problem", try a table.

### 24. Greedy algorithms and the exchange argument

Take the locally best choice at every step and never undo it. Greedy algorithms are fast and short, and they are correct only for problems whose structure makes the local choice safe. The standard proof is an *exchange argument*: take any optimal solution that disagrees with greedy's first choice, swap greedy's choice in, and show the result is no worse. If you can't produce that argument, test the greedy rule against brute force on small inputs, because plausible greedy rules are wrong surprisingly often.

```java
static int maxNonOverlapping(int[][] intervals) {      // each {start, end}; touching ends are allowed
    int[][] s = intervals.clone();
    Arrays.sort(s, Comparator.comparingInt(x -> x[1]));   // earliest finish first
    int count = 0, lastEnd = Integer.MIN_VALUE;
    for (int[] iv : s)
        if (iv[0] >= lastEnd) { count++; lastEnd = iv[1]; }
    return count;
}

record Node(long weight, int order, char symbol, Node left, Node right) {}

static Map<Character, String> huffman(Map<Character, Long> freq) {
    PriorityQueue<Node> pq = new PriorityQueue<>(Comparator.comparingLong(Node::weight).thenComparingInt(Node::order));
    int order = 0;
    for (Map.Entry<Character, Long> e : new TreeMap<>(freq).entrySet())
        pq.add(new Node(e.getValue(), order++, e.getKey(), null, null));
    while (pq.size() > 1) {
        Node a = pq.poll(), b = pq.poll();              // merge the two lightest subtrees
        pq.add(new Node(a.weight() + b.weight(), order++, '\0', a, b));
    }
    Map<Character, String> codes = new TreeMap<>();
    assign(pq.poll(), "", codes);
    return codes;
}

private static void assign(Node n, String prefix, Map<Character, String> out) {
    if (n.left() == null) { out.put(n.symbol(), prefix.isEmpty() ? "0" : prefix); return; }
    assign(n.left(), prefix + "0", out);
    assign(n.right(), prefix + "1", out);
}
```

> **Verified.** Earliest-finish-first matched an enumeration of every subset on 1,000 random sets of up to 12 intervals. The tempting rule "take the earliest start" fails on {[0, 10], [1, 2], [3, 4]}: it finds 1 meeting where the optimum is 2. Huffman on the textbook frequencies 45, 13, 12, 16, 9 and 5 (per 100 symbols) needs 224 bits, which is 2.24 bits per symbol, against 300 bits for fixed 3-bit codes and an entropy of 2.2199 bits (entry 16). The codes were prefix-free, and the average length stayed between the entropy and the entropy plus one bit. On 500 random sets of 2 to 7 weights, Huffman's total cost equalled the best of every possible merge order. Greedy change-making with coins 1, 5, 10, 25 matched the dynamic program of entry 23 for every amount from 1 to 1,000, but with coins 1, 3, 4 and amount 6 greedy takes three coins (4 + 1 + 1) where the optimum is two (3 + 3).

<!-- -->

> **Pitfall.** A greedy rule that works on your examples is not a proof. Coin systems like 1, 5, 10, 25 are special; change the denominations and greedy quietly stops being optimal.

**Use it for** interval scheduling, minimum spanning trees (entry 37), shortest paths with non-negative weights (entry 33) and compression: Huffman codes sit inside DEFLATE (gzip, zip, PNG) and JPEG. Greedy is also the usual first approximation when the exact problem is too hard.

### 25. Backtracking and pruning

Build a solution one decision at a time, and as soon as a partial solution cannot be completed, back up and try the next option. The power is in the pruning: abandoning a branch early discards everything below it. N-Queens with bit masks is the compact example. Three integers record which columns and diagonals are under attack, and `free & -free` picks the lowest available square.

```java
static int queens(int n) { return place(n, 0, 0, 0, 0); }

private static int place(int n, int row, int cols, int d1, int d2) {
    if (row == n) return 1;
    int count = 0;
    int free = ~(cols | d1 | d2) & ((1 << n) - 1);     // columns not attacked in this row
    while (free != 0) {
        int bit = free & -free;                         // lowest free column
        free ^= bit;
        count += place(n, row + 1, cols | bit, (d1 | bit) << 1, (d2 | bit) >>> 1);
    }
    return count;
}
```

> **Verified.** The counts for n = 1 to 12 are 1, 0, 0, 2, 10, 4, 40, 92, 352, 724, 2,680 and 14,200, matching the known sequence, and for n up to 8 they agree with a brute-force enumeration of all permutations. With a node counter in an instrumented copy: 8 queens has 92 solutions and the search visited 2,057 nodes, against 8! = 40,320 permutations and 8⁸ = 16,777,216 raw placements. 12 queens has 14,200 solutions and 856,189 nodes.

Pruning is the whole game: the search looked at about 5% of the permutations (2,057 of 40,320) and about 0.012% of the raw placements. The code uses `int` masks, so n must stay below 31, and the running time still explodes long before that.

> **Pitfall.** Backtracking is exponential in the worst case. A pruning test must be cheap and must never reject a partial solution that could still succeed. Order the choices so that failures show up early (try the most constrained variable first), and put a bound on the work when the input is untrusted. Regular-expression engines that backtrack inherit the same cost, which is why an adversarial pattern or input can keep a server busy for a very long time.

**Use it for** Sudoku and other constraint solvers, SAT solvers (DPLL is backtracking plus unit propagation), parsers, puzzle generation, enumerating permutations and subsets, and branch and bound, which adds a cost bound to prune with.

### 26. Amortized analysis

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


## B. Linear-time techniques

### 27. Prefix sums, difference arrays, sliding windows and the monotonic deque

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

### 28. Kadane's algorithm and the Boyer–Moore majority vote

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

### 29. Fisher–Yates shuffle and reservoir sampling

A fair shuffle walks from the end of the array and swaps each position with a random position at or before it. Reservoir sampling picks k items uniformly from a stream of unknown length in one pass: keep the first k, then let item number i (counting from 0) replace a random slot with probability k/(i + 1).

```java
static void shuffle(int[] a, Random rnd) {
    for (int i = a.length - 1; i > 0; i--) {
        int j = rnd.nextInt(i + 1);                     // 0..i inclusive
        int t = a[i]; a[i] = a[j]; a[j] = t;
    }
}

static int[] reservoirSample(int[] stream, int k, Random rnd) {   // reads the stream once, keeps k items
    int[] res = Arrays.copyOf(stream, k);
    for (int i = k; i < stream.length; i++) {
        int j = rnd.nextInt(i + 1);
        if (j < k) res[j] = stream[i];
    }
    return res;
}
```

> **Verified.** The tempting shuffle that swaps every position with a random position *anywhere* is biased, for a counting reason: it makes nⁿ equally likely choices, and nⁿ is not a multiple of n!. For three items it has 3³ = 27 choice sequences for 6 permutations. Enumerated exactly, the permutations 012, 021, 102, 120, 201 and 210 get 4, 5, 5, 5, 4 and 4 of them, so none gets the fair share of 4.5. With four items there are 256 sequences, and the per-permutation counts run from 8 to 15 where a fair shuffle would give 10.67. Fisher–Yates, enumerated over all of its n! choice sequences for n = 3, 4 and 5, produced 6, 24 and 120 distinct permutations: every permutation exactly once. Keeping 3 of 10 items with `reservoirSample` over 200,000 trials, every item was kept with a frequency within 0.0010 of the ideal 0.3.

<!-- -->

> **Pitfall.** Fisher–Yates breaks if you are off by one. Draw `j` from `0..i-1` instead of `0..i` (that is Sattolo's algorithm, which produces only cyclic permutations) and no element can ever stay where it started. For n = 3, 4 and 5 the program found no fixed points and only 2, 6 and 24 of the 6, 24 and 120 permutations reachable.

<!-- -->

> **Pitfall.** A shuffle can be no more random than its generator's state. `java.util.Random` keeps a 48-bit state, so it can produce at most 2⁴⁸ ≈ 2.8×10¹⁴ different shuffles. 16! = 2.09×10¹³ fits under that, 17! = 3.56×10¹⁴ does not, and a 52-card deck needs log₂(52!) = 225.58, so 226 bits of seed. For anything with money or security attached, use `SecureRandom`. And don't hand-roll the shuffle at all: `Collections.shuffle` implements Fisher–Yates, and its Javadoc describes walking the list backwards and swapping a randomly selected element, taken from the part up to and including the current position, into the current position.

**Use it for** shuffling, sampling without replacement, A/B-test assignment, bootstrap resampling, and keeping a uniform sample of a log or event stream you can only read once.

### 30. Floyd's cycle detection and Pollard's rho

Floyd's "tortoise and hare" runs two pointers over a sequence, one step and two steps at a time. If there is a cycle they must meet inside it, using O(1) memory. To find where the cycle starts, reset one pointer to the head and move both one step at a time: if the tail has μ nodes, then μ steps from the head and μ steps from the meeting point both end on the cycle's first node. Pollard's rho (1975) turns the same idea into a factoring method. The sequence `x → x² + c mod n` must repeat modulo an unknown prime factor p after roughly √p steps (the birthday bound of entry 13), but not yet modulo n, so `gcd(|x − y|, n)` turns into a factor as soon as the tortoise and hare agree modulo p.

```java
static final class ListNode {
    final int val;
    ListNode next;
    ListNode(int v) { val = v; }
}

static ListNode cycleStart(ListNode head) {            // node where the cycle begins, or null
    ListNode slow = head, fast = head;
    while (fast != null && fast.next != null) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow == fast) {                             // met inside the cycle
            slow = head;
            while (slow != fast) { slow = slow.next; fast = fast.next; }
            return slow;
        }
    }
    return null;
}

static long pollardRho(long n) {                       // n composite and < 3e9 so products fit in a long
    if (n % 2 == 0) return 2;
    for (long c = 1; ; c++) {
        long x = 2, y = 2, d = 1;
        while (d == 1) {
            x = (x * x + c) % n;
            y = (y * y + c) % n;
            y = (y * y + c) % n;                        // the hare moves two steps
            d = gcd(Math.abs(x - y), n);                // gcd from entry 1
        }
        if (d != n) return d;                           // d == n: the walk closed too soon, retry with another c
    }
}
```

> **Verified.** `cycleStart` found the right node on 5,580 generated lists, with tails of 0 to 29 nodes and cycles of 2 to 42 nodes, plus a one-node self-loop, and it returns null on acyclic lists and on null. `pollardRho` splits 8051 into 83 × 97 and 10403 into 101 × 103. On 200 products of two random primes between 20,000 and 46,000 it averaged 132 iterations, where trial division by odd numbers would need about 14,320 divisions. An iteration costs a few multiplications and a gcd, so the saving in time is smaller than that ratio, but it is large and it grows with the size of the smaller factor.

<!-- -->

> **Pitfall.** `pollardRho` never returns on a prime `n`, because there is no factor to find, so test primality first with `BigInteger.isProbablePrime`. The `long` version needs n below about 3.03×10⁹ for the same overflow reason as `modPow` in entry 11; beyond that use `BigInteger`.

**Use it for** cycle checks on linked lists and iterators in O(1) memory, finding the period of a pseudo-random generator or any iterated function, detecting an infinite loop in a state machine, and factoring or discrete-logarithm attacks on small numbers and small groups. The square-root cost of rho is the same effect that rates a 256-bit elliptic-curve group at about 128 bits of security.

### 31. Knuth–Morris–Pratt string search

A naive search restarts from the next text position after every mismatch and can re-read the same characters again and again. KMP (1977) precomputes, for each prefix of the pattern, the length of its longest proper prefix that is also a suffix (the *prefix function*). After a mismatch it falls back by that amount instead of restarting, so the text pointer never moves backwards and the total work is O(n + m).

```java
static int[] prefixFunction(String p) {                // pi[i] = longest proper prefix of p[0..i] that is also a suffix
    int[] pi = new int[p.length()];
    for (int i = 1, k = 0; i < p.length(); i++) {
        while (k > 0 && p.charAt(i) != p.charAt(k)) k = pi[k - 1];
        if (p.charAt(i) == p.charAt(k)) k++;
        pi[i] = k;
    }
    return pi;
}

static int kmpSearch(String text, String p) {          // first match or -1, O(n + m)
    if (p.isEmpty()) return 0;
    int[] pi = prefixFunction(p);
    for (int i = 0, k = 0; i < text.length(); i++) {
        while (k > 0 && text.charAt(i) != p.charAt(k)) k = pi[k - 1];
        if (text.charAt(i) == p.charAt(k)) k++;
        if (k == p.length()) return i - k + 1;
    }
    return -1;
}

static int smallestPeriod(String s) {                  // shortest p such that s is s[0, p) repeated
    int m = s.length();
    if (m == 0) return 0;
    int p = m - prefixFunction(s)[m - 1];
    return m % p == 0 ? p : m;
}
```

> **Verified.** `prefixFunction("abacabad")` is 0, 0, 1, 0, 1, 2, 3, 0. `kmpSearch` matched `String.indexOf` on 20,000 random binary strings and patterns. `smallestPeriod` matched a brute-force search on 20,000 random strings of up to 12 characters; it gives 3 for "abcabcabc", 1 for "aaaa", and 7 (no repetition) for "abcabca". On the adversarial text of 100,000 `a` characters with the pattern 999 `a` characters followed by `b`, naive search made 99,001,000 character comparisons and KMP made 299,000, about three per text character (both counted with instrumented copies).

<!-- -->

> **Pitfall.** For everyday substring search call `String.indexOf` or `contains`. KMP earns its place when the input arrives as a stream you can read only once (the text pointer never backs up), when the input may be adversarial, and when you want the prefix function itself, for example to find a string's smallest period. For many patterns at once, look at Aho–Corasick, which generalizes the same fallback idea.

**Use it for** pattern matching in streams and network traffic, detecting repetition and periodicity in strings, and as a building block: the prefix function is the core of several string algorithms, and the Z-algorithm is a close relative.

## C. Graph algorithms

The graph code below uses adjacency lists: `g.get(u)` holds the neighbors of u, or `{neighbor, weight}` pairs for weighted graphs. Small helpers in the full program build them from edge arrays.

### 32. Breadth-first and depth-first search

Two ways to walk a graph, both in O(V + E). BFS uses a queue and visits vertices in order of their distance (number of edges) from the start, so the first time it reaches a vertex is along a shortest path in an unweighted graph. DFS uses a stack, or recursion, and goes as deep as it can before backing up. It is the engine behind connected components, cycle detection, topological ordering (entry 36) and backtracking (entry 25).

```java
static int[] bfsDistances(List<List<Integer>> g, int src) {
    int[] dist = new int[g.size()];
    Arrays.fill(dist, -1);                              // -1 means not reached yet
    ArrayDeque<Integer> q = new ArrayDeque<>();
    dist[src] = 0;
    q.add(src);
    while (!q.isEmpty()) {
        int u = q.poll();
        for (int v : g.get(u))
            if (dist[v] < 0) { dist[v] = dist[u] + 1; q.add(v); }    // mark when enqueued
    }
    return dist;
}

static int components(List<List<Integer>> g) {          // iterative DFS: safe for very deep graphs
    int count = 0;
    boolean[] seen = new boolean[g.size()];
    ArrayDeque<Integer> stack = new ArrayDeque<>();
    for (int s = 0; s < g.size(); s++) {
        if (seen[s]) continue;
        count++;
        seen[s] = true;
        stack.push(s);
        while (!stack.isEmpty()) {
            int u = stack.pop();
            for (int v : g.get(u))
                if (!seen[v]) { seen[v] = true; stack.push(v); }
        }
    }
    return count;
}

static void dfsRecursive(List<List<Integer>> g, int u, boolean[] seen) {
    seen[u] = true;
    for (int v : g.get(u)) if (!seen[v]) dfsRecursive(g, v, seen);
}
```

> **Verified.** On 1,000 random undirected graphs of up to 31 vertices (duplicate edges and self-loops included), `bfsDistances` equalled Floyd–Warshall distances with unit weights from every source, and `components` agreed with union-find on the number of components. On a chain of 200,000 vertices, `components` returned 1, while `dfsRecursive` threw `StackOverflowError` with this JDK's default thread stack.

<!-- -->

> **Pitfall.** Mark a vertex as seen when you *enqueue* it, as `dist[v] = …` does, not when you dequeue it, or the same vertex enters the queue many times. Recursive DFS goes as deep as the longest path, which on real data (a linked chain of 200,000 nodes, a long dependency chain) overflows the default stack. The explicit-stack version above marks vertices when it pushes them, so its visit order differs from recursive DFS. That is fine for reachability and components, but algorithms that need true discovery and finishing times need a stack of iterators instead.

**Use it for** shortest hop counts ("degrees of separation", word ladders, fewest moves in a puzzle), flood fill, crawlers, dependency discovery, maze solving and connected components.

### 33. Dijkstra's algorithm

Shortest paths from one source when every edge weight is non-negative. It is greedy: repeatedly take the unfinished vertex with the smallest tentative distance, declare it final, and relax its outgoing edges. With a binary heap it runs in O((V + E) log V); with a plain array instead of a heap it is O(V²), which is better for dense graphs. Java's `PriorityQueue` has no decrease-key operation, so the usual approach adds a new entry for every improvement and skips outdated ones when they surface ("lazy deletion").

```java
static long[] dijkstra(List<List<int[]>> g, int src) {   // edges as {to, weight}, weights >= 0
    long[] dist = new long[g.size()];
    Arrays.fill(dist, Long.MAX_VALUE);
    dist[src] = 0;
    PriorityQueue<long[]> pq = new PriorityQueue<>(Comparator.comparingLong(x -> x[0]));
    pq.add(new long[]{0, src});
    while (!pq.isEmpty()) {
        long[] top = pq.poll();
        int u = (int) top[1];
        if (top[0] > dist[u]) continue;                  // stale entry: a shorter path was already found
        for (int[] e : g.get(u)) {
            long nd = top[0] + e[1];
            if (nd < dist[e[0]]) { dist[e[0]] = nd; pq.add(new long[]{nd, e[0]}); }
        }
    }
    return dist;                                         // Long.MAX_VALUE marks unreachable vertices
}
```

> **Verified.** The classic six-vertex example gives distances 0, 7, 9, 20, 20, 11. On 400 random directed graphs of up to 31 vertices with weights from 0 to 20 (zero weights allowed, some vertices unreachable), this version and the textbook variant that finalizes each vertex exactly once (`dijkstraSettled` in the full program) both matched Floyd–Warshall from every source. Negative edges are another story: in the graph 0→1 (weight 1), 0→2 (4), 2→1 (−5), the finalize-once version answers dist(0, 1) = 1, while the true distance through vertex 2 is −1, which Bellman–Ford finds. The lazy version above also answers −1 on this graph, because it lets a vertex be improved again.

<!-- -->

> **Pitfall.** With negative edges the greedy argument fails: a vertex declared final can still be improved later. The lazy-deletion version above happens to re-relax vertices and so survives the small example, but then it re-expands vertices and loses the O((V + E) log V) bound. If weights can be negative, use Bellman–Ford (entry 35).

**Use it for** road and network routing (OSPF routers compute their shortest-path trees with a method based on Dijkstra's algorithm), maps and games (usually with A* on top, entry 34), minimum-cost anything with non-negative costs, and as a subroutine, for example in Johnson's algorithm (entry 35).

### 34. A* search and admissible heuristics

A* is Dijkstra with a guess. It orders vertices by `f = g + h`: the cost paid so far plus an estimate `h` of the cost still to go. If `h` never overestimates the true remaining cost (it is *admissible*), the first time the goal comes off the queue its path is optimal. Dijkstra is the special case `h = 0`. On a 4-connected grid with unit steps, the Manhattan distance from entry 4 is a natural heuristic. Multiplying the heuristic by a weight above 1 makes the search greedier and faster, at the price of the optimality guarantee.

```java
/** w = 1: A* with the Manhattan heuristic; w = 0: plain Dijkstra; w > 1: inflated, inadmissible heuristic. */
static int astar(boolean[][] wall, int sr, int sc, int tr, int tc, int w) {
    int R = wall.length, C = wall[0].length;
    int[] g = new int[R * C];
    Arrays.fill(g, Integer.MAX_VALUE);
    boolean[] closed = new boolean[R * C];
    // entries are {f, g, cell}: smallest f first, and among equal f the larger g
    PriorityQueue<int[]> pq = new PriorityQueue<>((x, y) -> x[0] != y[0] ? Integer.compare(x[0], y[0]) : Integer.compare(y[1], x[1]));
    int start = sr * C + sc;
    g[start] = 0;
    pq.add(new int[]{w * (Math.abs(sr - tr) + Math.abs(sc - tc)), 0, start});
    int[] dr = {1, -1, 0, 0}, dc = {0, 0, 1, -1};
    while (!pq.isEmpty()) {
        int cur = pq.poll()[2];
        if (closed[cur]) continue;
        closed[cur] = true;
        int r = cur / C, c = cur % C;
        if (r == tr && c == tc) return g[cur];
        for (int d = 0; d < 4; d++) {
            int nr = r + dr[d], nc = c + dc[d];
            if (nr < 0 || nc < 0 || nr >= R || nc >= C || wall[nr][nc]) continue;
            int ni = nr * C + nc, ng = g[cur] + 1;
            if (ng < g[ni]) {
                g[ni] = ng;
                pq.add(new int[]{ng + w * (Math.abs(nr - tr) + Math.abs(nc - tc)), ng, ni});
            }
        }
    }
    return -1;                                           // unreachable
}
```

> **Verified.** On 2,000 random 30×30 grids with 25% walls, 1,402 of which had a path from corner to corner, A* with the Manhattan heuristic returned exactly the length found by breadth-first search every time, and −1 whenever there was no path. Averaged over the 1,402 solvable grids it expanded 135 cells, where Dijkstra (the same code with weight 0) expanded 665. Inflating the heuristic to 3× cut that to 88 cells but returned a longer-than-optimal path in 1,332 of the 1,402 grids, at worst 1.53 times the optimum, and never shorter. A weighted search with a consistent heuristic is guaranteed to stay within its weight of the optimum, and it did. (The full program also counts the expanded cells; the snippet leaves that counter out.)

<!-- -->

> **Pitfall.** The optimality guarantee needs an admissible heuristic, and this closed-set version, which never reopens a finished cell, also wants it *consistent*: `h(u) ≤ cost(u, v) + h(v)` for every edge. Manhattan distance is both on a 4-connected unit grid. Allow diagonal moves and it overestimates, so switch to Chebyshev or octile distance. An inflated heuristic is a deliberate trade of correctness for speed; here a 3× heuristic bought a 1.5× reduction in work and cost the optimal answer in 94% of the solvable grids.

**Use it for** game and robot pathfinding, route planning (with a straight-line or haversine heuristic, entry 9), puzzle solving such as sliding tiles with Manhattan distance, and any best-first search where domain knowledge can supply the estimate.

### 35. Bellman–Ford, Floyd–Warshall and Johnson

**Bellman–Ford** relaxes every edge V − 1 times; after round i every shortest path of at most i edges is correct. Negative edges are fine, and if a V-th round still improves something, a negative cycle is reachable and shortest paths don't exist. It runs in O(V·E). **Floyd–Warshall** finds all pairs with three nested loops in O(V³): after step k, `d[i][j]` is the shortest path that uses only the first k vertices as stepping stones, and a negative number on the diagonal exposes a negative cycle. **Johnson's algorithm** gets all pairs on sparse graphs by reweighting. It runs Bellman–Ford once from a virtual source to get a potential `h(v)` for every vertex, replaces each weight with `w(u, v) + h(u) − h(v)`, which is never negative, and then runs Dijkstra from every vertex. The reweighting changes every path from s to t by the same amount, `h(s) − h(t)`, so shortest paths stay shortest.

```java
static final long INF = Long.MAX_VALUE / 4;              // large, but INF + INF cannot overflow

static long[] bellmanFord(int n, int[][] edges, int src) {   // edges {u, v, w}; null if a negative cycle is reachable
    long[] dist = new long[n];
    Arrays.fill(dist, INF);
    dist[src] = 0;
    for (int pass = 1; pass < n; pass++) {
        boolean changed = false;
        for (int[] e : edges)
            if (dist[e[0]] < INF && dist[e[0]] + e[2] < dist[e[1]]) { dist[e[1]] = dist[e[0]] + e[2]; changed = true; }
        if (!changed) break;
    }
    for (int[] e : edges)
        if (dist[e[0]] < INF && dist[e[0]] + e[2] < dist[e[1]]) return null;   // still improving: negative cycle
    return dist;
}

static long[][] floydWarshall(int n, int[][] edges) {
    long[][] d = new long[n][n];
    for (long[] row : d) Arrays.fill(row, INF);
    for (int i = 0; i < n; i++) d[i][i] = 0;
    for (int[] e : edges) d[e[0]][e[1]] = Math.min(d[e[0]][e[1]], e[2]);
    for (int k = 0; k < n; k++)
        for (int i = 0; i < n; i++)
            if (d[i][k] < INF)
                for (int j = 0; j < n; j++)
                    if (d[k][j] < INF && d[i][k] + d[k][j] < d[i][j]) d[i][j] = d[i][k] + d[k][j];
    return d;
}

static long[][] johnson(int n, int[][] edges) {          // all-pairs shortest paths via reweighting; null on a negative cycle
    int[][] ext = new int[edges.length + n][];
    System.arraycopy(edges, 0, ext, 0, edges.length);
    for (int i = 0; i < n; i++) ext[edges.length + i] = new int[]{n, i, 0};      // virtual source reaches everything for free
    long[] h = bellmanFord(n + 1, ext, n);
    if (h == null) return null;
    List<List<int[]>> g = new ArrayList<>();
    for (int i = 0; i < n; i++) g.add(new ArrayList<>());
    for (int[] e : edges) {
        long w = e[2] + h[e[0]] - h[e[1]];
        if (w < 0) throw new IllegalStateException("reweighting must make every edge non-negative");
        g.get(e[0]).add(new int[]{e[1], (int) w});
    }
    long[][] d = new long[n][n];
    for (int s = 0; s < n; s++) {
        long[] ds = dijkstra(g, s);                      // dijkstra from entry 33
        for (int t = 0; t < n; t++) d[s][t] = ds[t] == Long.MAX_VALUE ? INF : ds[t] - h[s] + h[t];
    }
    return d;
}
```

> **Verified.** On 300 random graphs of up to 15 vertices, 268 of them containing negative edges, Bellman–Ford from every source, Floyd–Warshall and Johnson agreed on every pair. The graphs had no negative cycle by construction: each weight was a non-negative weight plus `p(u) − p(v)` for a random potential p, which shifts every path by the same amount and leaves cycle totals unchanged. On the three-vertex cycle 0→1 (2), 1→2 (2), 2→0 (−5), whose total is −1, Bellman–Ford and Johnson returned null, and Floyd–Warshall left a negative number on the diagonal.

<!-- -->

> **Rule of thumb.** Non-negative weights: Dijkstra. Negative weights and one source: Bellman–Ford. All pairs on a small or dense graph: Floyd–Warshall. All pairs on a large sparse graph: Johnson, or simply Dijkstra from every vertex when weights are non-negative.

**Use it for** currency-arbitrage detection (take −log of every exchange rate; a negative cycle is a profitable loop), distance-vector routing (protocols such as RIP are built on Bellman–Ford), systems of difference constraints (`x_j − x_i ≤ c` is an edge of weight c), and transitive closure, which is Floyd–Warshall with booleans (Warshall's algorithm).

### 36. Topological sort (Kahn's algorithm)

A topological order lists the vertices of a directed acyclic graph so that every edge points forward. Kahn's algorithm (1962) repeatedly removes a vertex with no remaining incoming edges and decrements its neighbors' in-degrees. If it finishes without placing every vertex, the graph has a cycle, so the same code doubles as cycle detection. It runs in O(V + E).

```java
static List<Integer> topoSort(int n, int[][] edges) {    // null if the graph has a cycle
    List<List<Integer>> g = new ArrayList<>();
    int[] indeg = new int[n];
    for (int i = 0; i < n; i++) g.add(new ArrayList<>());
    for (int[] e : edges) { g.get(e[0]).add(e[1]); indeg[e[1]]++; }
    ArrayDeque<Integer> q = new ArrayDeque<>();
    for (int i = 0; i < n; i++) if (indeg[i] == 0) q.add(i);
    List<Integer> order = new ArrayList<>();
    while (!q.isEmpty()) {
        int u = q.poll();
        order.add(u);
        for (int v : g.get(u)) if (--indeg[v] == 0) q.add(v);
    }
    return order.size() == n ? order : null;
}
```

> **Verified.** On 1,000 random DAGs of up to 31 vertices, built from a hidden random order so that every edge points forward in it, `topoSort` returned all n vertices with every edge pointing forward. Adding the reverse of one existing edge, which makes a 2-cycle, made it return null every time, and the chain 0→1→2 gives [0, 1, 2]. Swapping the queue for a `PriorityQueue<Integer>` (`topoSortSmallestFirst` in the full program) produced the lexicographically smallest valid order on 300 random graphs of up to 7 vertices, checked against all n! orders.

<!-- -->

> **Pitfall.** The order is not unique, and the FIFO version's choice can shift when the input order shifts. For reproducible output (build plans, generated files, migrations), break ties explicitly, as the min-heap variant does. When `topoSort` returns null, the vertices that never reached in-degree zero are exactly those on a cycle or downstream of one, which is enough to print a useful "circular dependency" message.

**Use it for** build systems and package managers (what to compile or install first), spreadsheet recalculation, task schedulers, course prerequisites, data-pipeline stages, database migration ordering and class initialization order.

### 37. Union-find and minimum spanning trees

**Union-find** (disjoint sets) keeps a partition of n items and supports `find` (which set is this item in?) and `union` (merge two sets). Two tricks make it fast: union by rank, which hangs the shorter tree under the taller one, and path compression, here in its "halving" form, which points each visited node at its grandparent. Together they give O(α(n)) amortized time per operation, where α is the inverse Ackermann function, below 5 for any input size that could physically exist (Tarjan, 1975). A **spanning tree** connects all vertices with n − 1 edges, and the **minimum spanning tree** (MST) has the smallest total weight. By the *cut property*, the lightest edge crossing any split of the vertices belongs to some MST, and both classic algorithms apply it: **Kruskal** sorts the edges and keeps an edge when its endpoints are in different sets, and **Prim** grows a single tree by always adding the lightest edge that leaves it.

```java
static final class DSU {
    final int[] parent, rank;
    int sets;
    DSU(int n) {
        parent = new int[n]; rank = new int[n]; sets = n;
        for (int i = 0; i < n; i++) parent[i] = i;
    }
    int find(int x) {                                   // path halving
        while (parent[x] != x) { parent[x] = parent[parent[x]]; x = parent[x]; }
        return x;
    }
    boolean union(int a, int b) {
        int ra = find(a), rb = find(b);
        if (ra == rb) return false;                     // already together: this edge would close a cycle
        if (rank[ra] < rank[rb]) { int t = ra; ra = rb; rb = t; }
        parent[rb] = ra;                                // attach the shorter tree under the taller one
        if (rank[ra] == rank[rb]) rank[ra]++;
        sets--;
        return true;
    }
}

static long kruskal(int n, int[][] edges) {              // edges {u, v, w}; total weight of a minimum spanning forest
    int[][] sorted = edges.clone();
    Arrays.sort(sorted, Comparator.comparingInt(e -> e[2]));
    DSU dsu = new DSU(n);
    long total = 0;
    for (int[] e : sorted)
        if (dsu.union(e[0], e[1])) total += e[2];
    return total;
}

static long prim(int n, List<List<int[]>> g) {           // connected graph; g.get(u) holds {neighbor, weight}
    boolean[] in = new boolean[n];
    PriorityQueue<int[]> pq = new PriorityQueue<>(Comparator.comparingInt(x -> x[0]));
    pq.add(new int[]{0, 0});
    long total = 0;
    while (!pq.isEmpty()) {
        int[] top = pq.poll();
        if (in[top[1]]) continue;
        in[top[1]] = true;
        total += top[0];
        for (int[] e : g.get(top[1])) if (!in[e[0]]) pq.add(new int[]{e[1], e[0]});
    }
    return total;
}
```

> **Verified.** On 1,000 random connected weighted graphs of up to 41 vertices, built as a random spanning tree plus extra edges (parallel edges and self-loops included), Kruskal and Prim found the same total weight, and a spanning tree always used exactly n − 1 edges (the full program's `kruskal` also reports how many edges it kept). Union-find also gave the same component counts as the depth-first search of entry 32. With 1,000,000 elements after 1,000,000 random unions (union by rank plus path halving, measured with an instrumented copy of `find`), the next 1,000,000 finds took 0.856 parent hops each on average.

<!-- -->

> **Pitfall.** Without union by rank or size, and without path compression, a sequence of unions can build a chain and make `find` cost O(n). Also, an MST is not a shortest-path tree: it minimizes total weight, not distances from any vertex, so don't use it for routing.

**Use it for** Kruskal's algorithm, connected components of a graph that keeps growing, cycle detection in undirected graphs (`union` returning false means the edge closes a cycle), merging accounts or equivalence classes, percolation and image-segmentation labels, and maze generation. MSTs show up in network and cable design, single-linkage clustering (cut the heaviest MST edges), and as a 2-approximation for the traveling-salesman problem when the distances form a metric (entry 10).

## D. Probabilistic data structures

These trade a small, quantifiable error for a large saving in memory or movement. The error is the point of the design, so each entry measures it.

### 38. Bloom filter

A Bloom filter (Bloom, 1970) answers "have I seen this key?" with a bit array and k hash functions. Adding a key sets k bits. A lookup says "definitely not present" if any of its k bits is 0 and "probably present" if all are 1. There are no false negatives. After n insertions into m bits, the false-positive probability is about `(1 − e^(−kn/m))^k`. That is smallest at `k = (m/n)·ln 2`, and hitting a target rate p takes `m = −n·ln p / (ln 2)²` bits: about 9.585 bits per key for 1%, plus about 4.8 more bits per key for every further factor of ten. The code derives its k bit positions from two hashes as `h1 + i·h2`, a trick Kirsch and Mitzenmacher showed costs nothing in the asymptotic false-positive rate.

```java
static long mix(long z) {                              // splitmix64 finalizer: a strong 64-bit mixer
    z = (z ^ (z >>> 30)) * 0xbf58476d1ce4e5b9L;
    z = (z ^ (z >>> 27)) * 0x94d049bb133111ebL;
    return z ^ (z >>> 31);
}

static final class Bloom {
    final BitSet bits;
    final int m, k;
    Bloom(int expectedItems, double fpRate) {
        m = (int) Math.ceil(-expectedItems * Math.log(fpRate) / (Math.log(2) * Math.log(2)));
        k = Math.max(1, (int) Math.round((double) m / expectedItems * Math.log(2)));
        bits = new BitSet(m);
    }
    private int index(long key, int i) {                         // double hashing: h1 + i * h2
        long h1 = mix(key), h2 = mix(key ^ 0x9e3779b97f4a7c15L) | 1;
        return (int) Long.remainderUnsigned(h1 + i * h2, m);
    }
    void add(long key) { for (int i = 0; i < k; i++) bits.set(index(key, i)); }
    boolean mightContain(long key) {
        for (int i = 0; i < k; i++) if (!bits.get(index(key, i))) return false;
        return true;
    }
}

static double bloomTheory(double m, double n, int k) { return Math.pow(1 - Math.exp(-k * n / m), k); }
```

> **Verified.** For 100,000 keys at a 1% target the constructor chose m = 958,506 bits (9.585 per key, 117 KiB) and k = 7. All 100,000 inserted keys were found, so there were no false negatives. Over 1,000,000 keys that had never been inserted, the measured false-positive rate was 0.0100, the same as the formula's 0.0100, and the formula's best whole number of hash functions is 7. The same filter after 200,000 insertions, twice its design size, measured 0.1587 against 0.1575 from the formula: a 1% filter had turned into a 16% filter.

<!-- -->

> **Pitfall.** A plain Bloom filter cannot delete a key, because clearing a bit may erase other keys; counting Bloom filters and cuckoo filters support deletion at some cost in space. And size the filter for the count you will really insert. Guava's documentation warns that overflowing a `BloomFilter` with significantly more elements than specified saturates it and sharply worsens the false-positive probability, which is the 1%-to-16% jump measured above.

**Use it for** skipping expensive lookups. Once a filter policy is set, RocksDB writes a Bloom filter into every new on-disk file to decide whether that file may contain the key, at about 10 bits per key for a 1% false-positive rate, in line with the 9.585 bits above. Guava ships a ready-made `BloomFilter`. Bloom filters also suit "already seen" sets in crawlers and caches, where a rare false "yes" is cheap and a false "no" is not allowed.

### 39. Consistent hashing

Spreading keys over N servers with `hash(key) % N` has an ugly property: change N and almost every key moves, so adding one server to a cache cluster empties the cache. Consistent hashing (Karger et al., 1997) places servers and keys on the same circle of hash values, and each key belongs to the first server clockwise from it. A new server takes over only the arc just before it, about 1/N of the keys, and keys move only *to* the new server. Giving each server many positions on the circle (virtual nodes) evens out the arcs. Dynamo does exactly this: each node is assigned to multiple points in the ring.

```java
static long hashString(String s) {                     // FNV-1a, then the mixer from entry 38
    long h = 0xcbf29ce484222325L;
    for (byte b : s.getBytes(StandardCharsets.UTF_8)) { h ^= (b & 0xff); h *= 0x100000001b3L; }
    return mix(h);
}

static final class Ring {
    private final TreeMap<Long, String> ring = new TreeMap<>();
    private final int vnodes;
    Ring(int vnodes) { this.vnodes = vnodes; }
    void addNode(String node) { for (int i = 0; i < vnodes; i++) ring.put(hashString(node + "#" + i), node); }
    String nodeFor(String key) {
        Map.Entry<Long, String> e = ring.ceilingEntry(hashString(key));
        return (e != null ? e : ring.firstEntry()).getValue();   // wrap around the ring
    }
}
```

> **Verified.** With 100,000 keys, going from 10 to 11 servers moved 90.9% of the keys under `hash % N`, which is the expected 10/11. On the ring it moved 8.9% with 200 virtual nodes per server, close to the ideal 1/11 = 9.1%, and 9.6% with a single point per server. Every key that moved on the ring moved to the new server, never between old ones. The busiest server held 1.12 times the mean load with 200 virtual nodes per server and 1.58 times with one.

<!-- -->

> **Pitfall.** The ring is only as even as the hash is uniform, so use a hash with good mixing (not a bare `String.hashCode`). Consistent hashing also balances *keys*, not *load*: one hot key still lands on one server. Dynamo-style systems typically replicate each key on the next few distinct servers clockwise, so a failure doesn't lose data.

**Use it for** distributed caches, sharded databases, request routing to a stateful backend (so the same user hits the same instance), and any cluster where members come and go and moving data is expensive.

### 40. HyperLogLog

Counting distinct items exactly needs memory proportional to the number of distinct items. HyperLogLog (Flajolet, Fusy, Gandouet and Meunier, 2007) estimates the count within a couple of percent from a few kilobytes. Hash every item to a uniform 64-bit value. Use its first p bits to pick one of m = 2ᵖ registers, and in that register remember the largest "number of leading zeros in the remaining bits, plus one". A register that has seen ρ suggests that about 2^ρ distinct items went into it, and a harmonic mean across registers calms the noise: the standard error is about 1.04/√m. A linear-counting correction handles small counts.

```java
static final class HyperLogLog {
    final int p, m;
    final byte[] reg;
    HyperLogLog(int p) { this.p = p; m = 1 << p; reg = new byte[m]; }
    void add(long x) {
        long h = mix(x);                                          // mix from entry 38
        int idx = (int) (h >>> (64 - p));                         // first p bits choose a register
        long rest = (h << p) | (1L << (p - 1));                   // guard bit bounds the leading-zero count
        byte rank = (byte) (Long.numberOfLeadingZeros(rest) + 1);
        if (rank > reg[idx]) reg[idx] = rank;
    }
    void merge(HyperLogLog o) { for (int i = 0; i < m; i++) if (o.reg[i] > reg[i]) reg[i] = o.reg[i]; }
    double estimate() {
        double alpha = 0.7213 / (1 + 1.079 / m);
        double sum = 0;
        int zeros = 0;
        for (byte r : reg) { sum += Math.pow(2, -r); if (r == 0) zeros++; }
        double e = alpha * m * (double) m / sum;
        if (e <= 2.5 * m && zeros > 0) e = m * Math.log((double) m / zeros);   // small-range correction (linear counting)
        return e;
    }
}
```

> **Verified.** With p = 14, which is 16,384 one-byte registers, the theoretical standard error is 1.04/√16,384 = 0.81%. After adding 1,000, 10,000, 100,000 and 1,000,000 distinct keys, the estimates were 1,009 (+0.95%), 10,052 (+0.52%), 99,781 (−0.22%) and 997,636 (−0.24%), all within three standard errors. Adding each of 50,000 keys three times left the registers identical to adding each once. Merging the sketches of two overlapping ranges, 0 to 179,999 and 120,000 to 299,999, gave registers identical to the sketch of the union.

<!-- -->

> **Pitfall.** The error is a *standard* error relative to n, so roughly one estimate in three lands further out than 0.81%. A weak hash ruins the estimate, which is why `add` mixes its input first. The sketch cannot list or delete items, and it is the wrong tool when you need exact counts, such as billing.

**Use it for** unique visitors, distinct queries or users per day, and cardinality estimates inside databases. Redis exposes it as `PFADD`, `PFCOUNT` and `PFMERGE` and documents up to 12 KB per counter and a 0.81% standard error, the same figure as above. Because sketches merge by taking the maximum of each register, they combine across servers and time windows without moving the raw data.

## E. Numerical iteration

### 41. Newton's method

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

### 42. Monte Carlo and the 1/√n law

Estimate a quantity by random sampling. The error of the average of n independent samples with standard deviation σ is about σ/√n, whatever the dimension of the problem: ten times the accuracy costs a hundred times the samples. The code estimates π as the fraction of random points in the unit square that land inside the quarter circle, and integrates a function by averaging it at random points. *Stratified sampling* splits the range into n slices and draws one random point per slice, which spreads the points evenly and can beat plain sampling by orders of magnitude on smooth functions.

```java
static double estimatePi(long samples, Random rnd) {
    long inside = 0;
    for (long i = 0; i < samples; i++) {
        double x = rnd.nextDouble(), y = rnd.nextDouble();
        if (x * x + y * y <= 1.0) inside++;
    }
    return 4.0 * inside / samples;
}

static double integrate(DoubleUnaryOperator f, int n, boolean stratified, Random rnd) {   // average of f over [0, 1]
    double sum = 0;
    for (int i = 0; i < n; i++) {
        double u = stratified ? (i + rnd.nextDouble()) / n : rnd.nextDouble();   // one random point per stratum
        sum += f.applyAsDouble(u);
    }
    return sum / n;
}
```

> **Verified.** The root-mean-square error of the π estimate follows `√(π(4 − π)/n)`, the spread of a binomial count. With n = 100, 10,000 and 1,000,000 samples the measured errors were 0.155, 0.0168 and 0.00161 against predictions of 0.164, 0.0164 and 0.00164 (300, 300 and 100 trials), so each hundredfold increase in samples bought about a tenfold gain in accuracy. For the integral of 4/(1 + x²) over [0, 1], which equals π, with n = 10,000 samples, plain Monte Carlo had an RMS error of 6.32e-03 against the predicted σ/√n = 6.43e-03, and stratified sampling had 6.24e-07: about 10,000 times smaller with the same number of samples.

<!-- -->

> **Pitfall.** The 1/√n law is slow, since each extra digit costs 100 times the samples. In one or a few dimensions with a smooth integrand, stratification or deterministic quadrature wins; Monte Carlo wins when the dimension is high, because its error rate doesn't depend on it. Seed the generator when you need reproducible runs, and in multithreaded code give each thread its own generator (`ThreadLocalRandom` or `SplittableRandom`) rather than sharing one `Random`, whose Javadoc warns about contention.

**Use it for** risk and queueing simulations, physics and rendering (path tracing), probabilities with no closed form, power calculations for experiments, and Monte Carlo tree search in game AI. The method was developed at Los Alamos in the 1940s by Ulam, von Neumann and Metropolis.

## Quick reference for Part 2

| # | Principle | Reach for it when | Watch out for |
|---|---|---|---|
| 21 | Divide and conquer, master theorem | work splits into independent subproblems: sorting, selection, big multiplication | unbalanced splits recurse deeply; use the JDK's versions |
| 22 | Binary search, on the answer | sorted data, or any monotone yes/no question | midpoint overflow; duplicates; non-monotone predicates |
| 23 | Dynamic programming | overlapping subproblems with optimal substructure | pseudo-polynomial tables; loop direction; recursion depth |
| 24 | Greedy, exchange argument | scheduling, compression, spanning trees | needs a proof; compare against brute force |
| 25 | Backtracking, pruning | constraint satisfaction, enumeration | exponential worst case; pruning must be sound |
| 26 | Amortized analysis | dynamic arrays, structures that rebuild themselves | not a worst-case bound; growth must be geometric |
| 27 | Prefix sums, difference arrays, windows | repeated range queries and updates, sliding maxima | two pointers need non-negative data; overflow |
| 28 | Kadane, Boyer–Moore | best run or majority element in one pass | the majority vote needs a verification pass |
| 29 | Fisher–Yates, reservoir sampling | fair shuffles, samples from streams | off-by-one bias; generator state limits reachable shuffles |
| 30 | Floyd cycle detection, Pollard's rho | cycles in O(1) memory, factoring | rho never returns on a prime |
| 31 | Knuth–Morris–Pratt | streaming or worst-case-safe substring search | `String.indexOf` is the default |
| 32 | BFS and DFS | hop counts, components, traversal | mark on enqueue; recursion depth |
| 33 | Dijkstra | shortest paths with non-negative weights | negative edges |
| 34 | A* | pathfinding with a good estimate | the heuristic must be admissible and, here, consistent |
| 35 | Bellman–Ford, Floyd–Warshall, Johnson | negative weights, all pairs, negative cycles | pick by graph density; overflow of the infinity value |
| 36 | Topological sort | dependency ordering, cycle detection | the order is not unique; break ties on purpose |
| 37 | Union-find, minimum spanning tree | merging sets, cheapest way to connect everything | needs rank and compression; an MST is not a shortest-path tree |
| 38 | Bloom filter | a cheap "definitely not here" test | no deletes; size it for the real key count |
| 39 | Consistent hashing | sharding with few moved keys when members change | needs virtual nodes and a good hash |
| 40 | HyperLogLog | distinct counts in kilobytes | approximate, with a relative error |
| 41 | Newton's method | fast root-finding | can diverge; `(long) Math.sqrt` is wrong for large n |
| 42 | Monte Carlo | high-dimensional integrals and simulations | error shrinks only as 1/√n |

## Sources

- Oracle, [`Collections` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Collections.html): `shuffle` walks the list backwards swapping a randomly selected earlier element into the current position; `binarySearch` gives no guarantee which duplicate is found and returns `-(insertion point) - 1` for a missing key.
- Oracle, [`Arrays` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Arrays.html): `sort(int[])` is a dual-pivot quicksort.
- OpenJDK 21, [`TimSort.java`](https://github.com/openjdk/jdk/blob/jdk-21%2B35/src/java.base/share/classes/java/util/TimSort.java): "a stable, adaptive, iterative mergesort", O(n log n) in the worst case. [`BigInteger.java`](https://github.com/openjdk/jdk/blob/jdk-21%2B35/src/java.base/share/classes/java/math/BigInteger.java): Karatsuba above 80 ints and Toom–Cook above 240 ints, with no FFT-based multiplication.
- Oracle, [`Random` in the Java SE 21 API](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/Random.html): a 48-bit seed, and not cryptographically secure.
- Oracle, [`StringBuilder`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/StringBuilder.html): `ensureCapacity` grows to twice the old capacity plus 2. [`ArrayList`](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/ArrayList.html): the growth policy is unspecified beyond constant amortized time.
- Wikipedia, [Open Shortest Path First](https://en.wikipedia.org/wiki/Open_Shortest_Path_First): OSPF computes the shortest-path tree for each route using a method based on Dijkstra's algorithm. [Routing Information Protocol](https://en.wikipedia.org/wiki/Routing_Information_Protocol): RIP is a distance-vector protocol, a family based on the Bellman–Ford algorithm.
- Flajolet, Fusy, Gandouet and Meunier, [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) (2007): standard error about 1.04/√m, the constant `0.7213/(1 + 1.079/m)` and the small-range correction. Redis, [HyperLogLog documentation](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/): up to 12 KB and a 0.81% standard error.
- Kirsch and Mitzenmacher, [Less Hashing, Same Performance: Building a Better Bloom Filter](https://www.eecs.harvard.edu/~michaelm/postscripts/rsa2008.pdf): two hash functions suffice, with no loss in the asymptotic false-positive probability. RocksDB, [Bloom filter wiki](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter): a filter in every new SST file, about 10 bits per key for a 1% rate. Guava, [`BloomFilter`](https://guava.dev/releases/snapshot-jre/api/docs/com/google/common/hash/BloomFilter.html): overflowing a filter sharply worsens its false-positive probability.
- Karger, Lehman, Leighton, Panigrahy, Levine and Lewin, [Consistent hashing and random trees](https://doi.org/10.1145/258533.258660) (STOC 1997). DeCandia et al., [Dynamo: Amazon's Highly Available Key-value Store](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) (SOSP 2007): consistent hashing with each node assigned to multiple points in the ring, and replication of each key at the N−1 clockwise successors, using a preference list that skips positions so it holds only distinct physical nodes.
