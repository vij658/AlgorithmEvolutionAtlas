# 56. Cache stampede: single flight and early recomputation

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

When a hot cache entry expires, many requests rebuild it at once. Single flight lets one caller rebuild while the others wait; probabilistic early recomputation (XFetch) refreshes slightly before expiry, with a chance that rises as expiry nears.

## What the program checks

One hot key: plain TTL reloads 499.8 times per cycle, XFetch 2.6, single flight 1.0

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/56-cache-stampede
java CacheStampede.java
```

JDK 17 or newer, no build step. It prints 687 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
one hot key, 1000 requests/s, TTL 30 s, a load takes 0.5 s, 9000 s of traffic: plain TTL: 499.8 loads per cycle (290 cycles), 499.8 requests waited, at most 562 loads at once, 499.8 requests found no value; XFetch (beta = 1): 2.6 loads per cycle (329 cycles), 2.6 requests waited, at most 17 loads at once, 0.0 requests found no value; single flight: 1.0 loads per cycle (295 cycles), 502.5 requests waited, at most 1 loads at once, 502.5 requests found no value; XFetch + single flight: 1.0 loads per cycle (332 cycles), 1.0 requests waited, at most 1 loads at once, 0.0 requests found no value; XFetch with beta = 2: 1.6 loads per cycle
CacheStampede: 687 checks passed
```

## References

- Vattani et al., PVLDB 8(8), 886–897 (2015) (XFetch, probabilistic early recomputation).
