# 23. Dynamic programming

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#23-dynamic-programming)

## How it works

When a problem's answer is built from answers to overlapping subproblems, compute each subproblem once and store it, either top-down with memoisation or bottom-up in a table. Fibonacci, knapsack, longest common subsequence and coin change are the worked examples.

## In depth (from the catalog page)

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

## Run it

```
cd code/principles/part-2-paradigms-and-classics/23-dynamic-programming
java DynamicProgramming.java
```

JDK 17 or newer, no build step. It prints 1,504 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
fib(30): naive recursion made 2692537 calls, memoized made 59
DynamicProgramming: 1504 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
