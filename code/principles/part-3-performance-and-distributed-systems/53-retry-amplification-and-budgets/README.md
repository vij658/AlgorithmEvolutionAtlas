# 53. Retry amplification and retry budgets

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Retries multiply: three layers that each try four times turn one failed user request into 64 calls at the bottom. A retry budget (retries limited to a fraction of normal traffic) keeps a struggling system able to recover.

## What the program checks

3 layers × 4 attempts against a dead service means 64 calls at the bottom per user request; a 10% retry budget keeps the system recoverable where immediate retries leave it stuck

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/53-retry-amplification-and-budgets
java RetryBudgets.java
```

JDK 17 or newer, no build step. It prints 13 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
calls reaching the bottom service per user request: 3 layers x 4 attempts, bottom fails 100%: 64.00 calls at the bottom (simulated 64.00); 4 layers x 3 attempts, bottom fails 100%: 81.00 calls at the bottom (simulated 81.00); 3 layers x 3 attempts, bottom fails 50%: 2.00 calls at the bottom (simulated 2.00); 3 layers x 4 attempts, bottom fails 70%: 3.33 calls at the bottom (simulated 3.34); 2 layers x 3 attempts, bottom fails 90%: 6.13 calls at the bottom (simulated 6.13); 5 layers x 2 attempts, bottom fails 80%: 5.00 calls at the bottom (simulated 4.99); 
80 requests/s into a server that does 100/s, with a 5 s stall at 20% speed, mean of 5 runs: no retries: before 81/s, during 5/s, in the 20 s after 47/s, last 20 s 80/s, queue at the end 0; 3 immediate retries: before 79/s, during 6/s, in the 20 s after 0/s, last 20 s 0/s, queue at the end 21807; 3 retries with a 10% budget: before 79/s, during 5/s, in the 20 s after 3/s, last 20 s 79/s, queue at the end 1; 3 retries with full-jitter backoff: before 82/s, during 5/s, in the 20 s after 0/s, last 20 s 0/s, queue at the end 21485; 3 immediate retries, server skips expired requests: before 81/s, during 20/s, in the 20 s after 88/s, last 20 s 79/s, queue at the end 1; 
RetryBudgets: 13 checks passed
```

## References

- Google SRE book, "Addressing Cascading Failures" (64 = 4³ attempts; retry budgets); Finagle retry budgets (20% plus 10 per second); gRPC proposal A6 (retry throttling); Bronson et al., "Metastable Failures in Distributed Systems", HotOS 2021.
