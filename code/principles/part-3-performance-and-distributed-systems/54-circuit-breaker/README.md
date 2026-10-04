# 54. Circuit breaker

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Wrap calls to a dependency in a state machine: closed (calls pass), open (fail fast after too many failures), half-open (let a probe through after a timeout). During an outage it stops wasting calls and gives the dependency room to recover.

## What the program checks

A 65 s outage: 6,500 calls reach the dependency without a breaker, 11 with one

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/54-circuit-breaker
java CircuitBreakerDemo.java
```

JDK 17 or newer, no build step. It prints 579,040 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
dependency down for 65 s at 100 requests/s: without a breaker 6500 calls hit it; with a breaker (5 failures, 10 s open) only 11 did, 6993 requests were refused locally, and the first success after recovery came 5040 ms late
CircuitBreakerDemo: 579040 checks passed
```

## References

- Martin Fowler, "CircuitBreaker".
