# 57. Quorums: R + W > N

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

With N replicas, writes acknowledged by W and reads querying R, any read quorum overlaps any write quorum when R + W > N, so a read sees the latest acknowledged write. The program measures stale reads and availability for different (N, R, W).

## What the program checks

Measured stale-read rates match the formula (for example 0.6667 vs 0.6673 for N = 3, R = 1, W = 1); availability for several (N, R, W)

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/57-quorums
java Quorums.java
```

JDK 17 or newer, no build step. It prints 1,001,919 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
share of reads that miss the latest write, read straight after one write to a random W replicas: (3,1,1): formula 0.6667, measured 0.6673; (3,1,2): formula 0.3333, measured 0.3329; (3,2,1): formula 0.3333, measured 0.3346; (3,2,2): formula 0.0000, measured 0.0000; (5,1,1): formula 0.8000, measured 0.7995; (5,2,2): formula 0.3000, measured 0.2991; (5,2,3): formula 0.1000, measured 0.0996; (5,3,3): formula 0.0000, measured 0.0000; (7,3,3): formula 0.1143, measured 0.1150; (7,2,2): formula 0.4762, measured 0.4763; 
each replica up with probability 0.99, chance that a read / a write can reach enough replicas: (3,2,2): reads 0.999702, writes 0.999702; (3,1,3): reads 0.999999, writes 0.970299; (3,3,1): reads 0.970299, writes 0.999999; (5,3,3): reads 0.999990, writes 0.999990; (5,1,5): reads 1.000000, writes 0.950990; 
Quorums: 1001919 checks passed
```

## References

- DeCandia et al., "Dynamo" (SOSP 2007); Gifford, "Weighted Voting for Replicated Data" (1979, Xerox PARC report CSL-79-14).
