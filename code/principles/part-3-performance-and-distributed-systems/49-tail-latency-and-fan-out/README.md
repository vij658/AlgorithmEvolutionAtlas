# 49. Tail latency and fan-out

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

When one request fans out to many servers, it waits for the slowest. At fan-out 100, most user requests hit at least one server's p99. Hedged requests (send a backup after a delay) cut the tail for a few percent of extra load.

## What the program checks

At fan-out 100, 63.3% of user requests are slower than one server's p99; hedging after the p95 costs 5.0% extra load and cuts p99 from 103 ms to 67 ms

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/49-tail-latency-and-fan-out
java TailLatency.java
```

JDK 17 or newer, no build step. It prints 12 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
share of user requests slower than one server's p99 (102 ms) when they wait for all of n servers: fan-out 1: 1.0% (formula 1.0%); fan-out 10: 9.6% (formula 9.6%); fan-out 100: 63.3% (formula 63.4%); 
so with fan-out 100, a user-level p99 needs each server's 99.9900% quantile; the median of the slowest of 100 sits at the single-server 99.31% quantile
hedged requests (second request after the p95 = 52 ms, first answer wins) on 1,000,000 requests: extra load 5.0%, p99 103 ms -> 67 ms, p99.9 222 ms -> 93 ms
hedging delay against extra load: hedge after p50 (10 ms): +49.9% load, p99 41 ms, p99.9 69 ms; hedge after p90 (36 ms): +10.0% load, p99 56 ms, p99.9 84 ms; hedge after p95 (52 ms): +5.0% load, p99 67 ms, p99.9 93 ms; hedge after p99 (102 ms): +1.0% load, p99 102 ms, p99.9 127 ms; 
TailLatency: 12 checks passed
```

## References

- Dean and Barroso, "The Tail at Scale", CACM 2013.
