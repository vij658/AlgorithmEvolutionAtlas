# 25. Backtracking and pruning

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#25-backtracking-and-pruning)

## How it works

Build a solution one choice at a time and abandon a partial solution as soon as it cannot lead to a valid answer. On N-queens, checking each queen as it is placed visits 2,057 nodes for n = 8, where trying every placement would test 16,777,216 boards.

## In depth (from the catalog page)

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

## Run it

```
cd code/principles/part-2-paradigms-and-classics/25-backtracking
java Backtracking.java
```

JDK 17 or newer, no build step. It prints 21 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
8 queens: 92 solutions; backtracking visited 2057 nodes (8! = 40,320 permutations, 8^8 = 16,777,216 placements)
12 queens: 14200 solutions; 856189 nodes visited
Backtracking: 21 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
