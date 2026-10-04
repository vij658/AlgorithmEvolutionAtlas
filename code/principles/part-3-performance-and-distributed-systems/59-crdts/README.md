# 59. CRDTs (conflict-free replicated data types)

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Conflict-free replicated data types merge with an operation that is commutative, associative and idempotent, so replicas that have seen the same updates converge in any order. The program covers counters, sets and registers, and the trap of last-writer-wins with clock skew.

## What the program checks

Counters, sets and registers converge; last-writer-wins with 50 ms clock skew lets the earlier write win 24.0% of the time when the writes are 50 ms apart

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/59-crdts
java Crdts.java
```

JDK 17 or newer, no build step. It prints 16,808 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
last-writer-wins, clocks with independent skew of 50 ms standard deviation: share of causally ordered write pairs where the earlier write wins: gap 0 ms: 50.0% (formula 50.0%); gap 50 ms: 24.0% (formula 24.0%); gap 100 ms: 7.9% (formula 7.9%); gap 200 ms: 0.2% (formula 0.2%); 
Crdts: 16808 checks passed
```

## References

- Shapiro et al., "Conflict-free replicated data types", SSS 2011.
