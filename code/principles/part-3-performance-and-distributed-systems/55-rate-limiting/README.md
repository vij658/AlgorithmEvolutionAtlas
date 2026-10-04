# 55. Token bucket, GCRA, fixed and sliding windows

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Limit request rates: a token bucket refills at rate r up to a burst size; GCRA is the same thing expressed with a single timestamp. Fixed windows allow double bursts at a window boundary; sliding logs and sliding windows fix that at different costs.

## What the program checks

A burst at a window boundary: fixed window admits 200 against a limit of 100, sliding log admits 100

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/55-rate-limiting
java RateLimiters.java
```

JDK 17 or newer, no build step. It prints 119,466,754 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
limit 100 per 1000 ms, silence until 900 ms then a request every millisecond until 1100 ms: fixed window admitted 200 (all within 200 ms), sliding log 100, token bucket (100 per second) with burst 100 admitted 119, with burst 10 admitted 29
RateLimiters: 119466754 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
