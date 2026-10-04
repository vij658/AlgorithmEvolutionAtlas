# 58. Lamport clocks and vector clocks

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Lamport clocks give every event a number consistent with causality (if a happened before b, L(a) < L(b)), but equal ordering says nothing about concurrency. Vector clocks keep one counter per process and can tell 'before', 'after' and 'concurrent' apart.

## What the program checks

Lamport clocks give concurrent events different numbers 92.1% of the time; vector clocks identify every concurrent pair

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/58-lamport-and-vector-clocks
java LogicalClocks.java
```

JDK 17 or newer, no build step. It prints 32,834,516 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
3000 random runs, 7,507,802 event pairs: 4,704,495 causally ordered, 2,803,307 concurrent; Lamport clocks gave the concurrent pairs different numbers in 92.1% of cases (they cannot say 'concurrent'), vector clocks identified every one of them
LogicalClocks: 32834516 checks passed
```

## References

- Lamport, "Time, clocks, and the ordering of events in a distributed system", CACM 21(7), 558–565 (1978); Fidge (1988); Mattern (1988).
