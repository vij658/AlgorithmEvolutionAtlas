# 52. Exponential backoff and jitter

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Retry after a delay that doubles each attempt, with a cap. Adding jitter (randomising the delay) breaks up synchronised retry waves; the program counts the total calls needed by plain, full-jitter and decorrelated-jitter strategies against an overloaded server.

## What the program checks

200 clients against a server taking 5 requests/ms: retrying at once costs 4,100 requests, full jitter 644, decorrelated jitter 496

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/52-exponential-backoff-and-jitter
java BackoffAndJitter.java
```

JDK 17 or newer, no build step. It prints 400,016 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
200 clients, server accepts 5 requests per ms, base 10 ms, cap 1000 ms, mean of 200 runs: retry at once: 4100 requests, done after 39 ms, worst millisecond 195.0 requests; exponential, no jitter: 4100 requests, done after 33270 ms, worst millisecond 195.0 requests; equal jitter: 671 requests, done after 130 ms, worst millisecond 45.3 requests; full jitter: 644 requests, done after 116 ms, worst millisecond 34.0 requests; decorrelated jitter: 496 requests, done after 113 ms, worst millisecond 16.3 requests; 
the same experiment for other base delays, mean of 100 runs, the least possible is 395 requests: base 2 ms: equal jitter 960 requests / 108 ms; full jitter 1005 requests / 99 ms; decorrelated jitter 786 requests / 74 ms; base 10 ms: equal jitter 670 requests / 130 ms; full jitter 643 requests / 122 ms; decorrelated jitter 496 requests / 112 ms; base 50 ms: equal jitter 468 requests / 155 ms; full jitter 417 requests / 140 ms; decorrelated jitter 397 requests / 314 ms; base 200 ms: equal jitter 397 requests / 424 ms; full jitter 395 requests / 204 ms; decorrelated jitter 395 requests / 598 ms; 
BackoffAndJitter: 400016 checks passed
```

## References

- Marc Brooker, "Exponential Backoff And Jitter", AWS Architecture Blog (2015).
