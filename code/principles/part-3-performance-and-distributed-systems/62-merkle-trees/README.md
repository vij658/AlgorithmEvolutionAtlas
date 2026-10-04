# 62. Merkle trees

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

A tree of hashes: each leaf hashes a block, each parent hashes its children. Two replicas compare roots and descend only into subtrees whose hashes differ, finding differences in O(d log n) comparisons. Prefixing leaves and nodes differently (RFC 6962) blocks second-preimage tricks.

## What the program checks

Finding differences between two 65,536-slot replicas: 33 comparisons for one difference; the second-preimage trap without RFC 6962's prefixes

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/62-merkle-trees
java MerkleTrees.java
```

JDK 17 or newer, no build step. It prints 12,520 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
two replicas with 65,536 slots (comparing everything would take 65,536 hashes): 0 differences: 1 comparisons (bound 1); 1 differences: 33 comparisons (bound 33); 4 differences: 105 comparisons (bound 129); 16 differences: 371 comparisons (bound 513); 64 differences: 1,291 comparisons (bound 2,049); 256 differences: 4,161 comparisons (bound 8,193); 1024 differences: 12,689 comparisons (bound 32,769); 
without prefixes the tree over {x, y} and the one-leaf tree over H(x)||H(y) share the root 42dbeeb4eb5d41bb...; with RFC 6962 prefixes the roots are 6bcf0e2e93e0a18e... and 239fa321f1b4c2fe...
MerkleTrees: 12520 checks passed
```

## References

- RFC 6962 (Certificate Transparency); section 3.5 on the Signed Tree Head is **not yet verified**.
