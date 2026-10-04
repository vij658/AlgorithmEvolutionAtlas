# 45. Little's law

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

In any stable system, the average number of items inside equals the arrival rate times the average time each spends inside: L = λW. It needs no assumptions about distributions; the program checks it on simulated queues of many kinds.

## What the program checks

Holds to 1e-9 on nine simulated queues; 500 requests/s × 0.2 s = 100 requests in flight

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/45-littles-law
java LittlesLaw.java
```

JDK 17 or newer, no build step. It prints 9 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Little's law on 9 simulated queues (3 service orders x 3 service-time distributions, 50,000 customers each) holds to 1e-9; exponential service, rho = 0.7: FIFO: L = 2.412, lambda = 0.997, W = 2.419, lambda*W = 2.412; LIFO: L = 2.396, lambda = 1.001, W = 2.393, lambda*W = 2.396; random order: L = 2.281, lambda = 0.999, W = 2.284, lambda*W = 2.281; 
sizing example: 500 requests/s x 0.2 s each = 100 requests in flight
LittlesLaw: 9 checks passed
```

## References

- Little, "A proof for the queuing formula L = λW", Operations Research 9(3) (1961) (DOI 10.1287/opre.9.3.383).
