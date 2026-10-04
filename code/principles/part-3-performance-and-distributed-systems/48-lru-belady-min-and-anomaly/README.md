# 48. LRU, Bélády's MIN and Bélády's anomaly

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

LRU evicts the least recently used page; Bélády's MIN (evict the page used furthest in the future) is the optimal offline policy. FIFO can fault more with more memory (Bélády's anomaly); stack algorithms such as LRU never do.

## What the program checks

The anomaly on the classic trace (FIFO 9 faults with 3 frames, 10 with 4); LRU never shows it on 2,000 random traces; hit rates of LRU, FIFO, random and MIN on a Zipf trace

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/48-lru-belady-min-and-anomaly
java PagingAndBelady.java
```

JDK 17 or newer, no build step. It prints 3,909 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Belady's anomaly on 1 2 3 4 1 2 5 1 2 3 4 5: FIFO faults 9 with 3 frames, 10 with 4; LRU faults 10 and 8
on 2000 random traces of 60 requests over 10 items, a larger FIFO cache did worse for some size in 28 traces; LRU did so in 0
hit rates on a Zipf(0.9) trace of 200,000 requests over 10,000 items: capacity 100: LRU 26.2%, FIFO 22.5%, random 22.5%, top-100 kept forever 41.1%, MIN 47.2%; capacity 1000: LRU 55.6%, FIFO 50.9%, random 51.1%, top-1000 kept forever 67.2%, MIN 74.1%; 
cycling through 101 items with room for 100, 10100 requests: LRU 0 hits, FIFO 0, random 97.0%, MIN 98.0%
PagingAndBelady: 3909 checks passed
```

## References

- Bélády, Nelson and Shedler, CACM 12(6), 349–353 (1969); Mattson et al., IBM Systems Journal 9(2), 78–117 (1970); Sleator and Tarjan, "Amortized efficiency of list update and paging rules", CACM 1985.
