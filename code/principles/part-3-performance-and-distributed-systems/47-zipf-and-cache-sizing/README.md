# 47. Zipf's law and cache sizing

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

In a Zipf distribution the k-th most popular item is requested in proportion to 1/k^s, so a small cache of the most popular items serves a large share of requests. The program measures the hit ratio for different cache sizes and exponents.

## What the program checks

Caching the top 1% of items serves 68.0% of requests at exponent 1 (1,000,000 items)

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/47-zipf-and-cache-sizing
java ZipfCacheSizing.java
```

JDK 17 or newer, no build step. It prints 5 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Zipf, exponent 1, sampled 3000000 requests: top 100 of 100,000: measured 0.4288, formula 0.4291; top 1,000 of 100,000: measured 0.6190, formula 0.6191; top 10,000 of 100,000: measured 0.8097, formula 0.8096; 
share of requests served by caching the most popular items out of 1,000,000: s = 0.8: top 0.1% -> 20.7%, top 1% -> 36.2%, top 10% -> 60.9%; s = 1.0: top 0.1% -> 52.0%, top 1% -> 68.0%, top 10% -> 84.0%; s = 1.2: top 0.1% -> 82.2%, top 1% -> 91.0%, top 10% -> 96.5%; 
with s = 1 over 1,000,000 items the single most popular item takes 6.95% of all requests and the top 10 take 20.4%
ZipfCacheSizing: 5 checks passed
```

## References

- Breslau et al., "Web caching and Zipf-like distributions", INFOCOM 1999 (the exponent varies by trace).
