# 60. Idempotency keys

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

A client sends the same idempotency key with every retry of an operation; the server records the key and its result so a retry returns the stored result instead of acting twice. The key and the effect must be committed together, or crashes cause duplicates or losses.

## What the program checks

With retries and crashes: no key 10.02% duplicates; key recorded first 10.10% lost; work first 9.96% duplicates; work and key in one transaction exactly once

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/60-idempotency
java Idempotency.java
```

JDK 17 or newer, no build step. It prints 516 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
200000 requests, clients retry until they see an answer, 10% crash before the work, 10% crash between work and record, 10% of answers lost: no idempotency key: 89.98% exactly once, 10.02% more than once, 0.00% never; record the key, then do the work: 89.91% exactly once, 0.00% more than once, 10.10% never; do the work, then record the key: 90.04% exactly once, 9.96% more than once, 0.00% never; work and key in one transaction: 100.00% exactly once, 0.00% more than once, 0.00% never; 
Idempotency: 516 checks passed
```

## References

- Stripe's documentation on idempotent requests.
