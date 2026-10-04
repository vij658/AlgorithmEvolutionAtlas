# 50. Percentiles, histograms and coordinated omission

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Percentiles cannot be averaged across servers; merge histograms instead. A log-bucketed histogram keeps percentiles within a chosen relative error in little memory. A closed-loop load generator that waits for each response hides stalls (coordinated omission).

## What the program checks

A log histogram with 1% relative error (811 buckets) is within 0.79% of the exact percentiles; averaging two servers' p99s gives 554.9 ms against a true p99 of 12.0 ms; a closed-loop benchmark hides a 1 s stall

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/50-percentiles-and-coordinated-omission
java Percentiles.java
```

JDK 17 or newer, no build step. It prints 9 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
log histogram with 1% relative error (811 buckets covering 0.01 ms to 100 s) on 300,000 lognormal samples, worst percentile error 0.790%: p50.0 exact 10.00 ms, histogram 10.08 ms; p90.0 exact 36.06 ms, histogram 36.02 ms; p99.0 exact 101.89 ms, histogram 101.37 ms; p99.9 exact 212.58 ms, histogram 211.69 ms; 
server A: 995,000 requests between 8 and 12 ms, p99 12.0 ms; server B: 5,000 requests between 900 and 1,100 ms, p99 1097.9 ms; average of the two p99s 554.9 ms; true p99 of all traffic 12.0 ms, true p99.9 1060.0 ms; merged histograms say p99 12.1 ms and p99.9 1061.1 ms
a 1 s stall seen by a closed-loop benchmark: p50 0.5 ms, p99 0.5 ms, p99.9 0.5 ms, max 1000.5 ms, 1 of 20000 requests slower than 100 ms; measured from the intended send time: p50 0.5 ms, p99 900.5 ms, p99.9 990.5 ms, max 1000.5 ms, 1801 slower than 100 ms
Percentiles: 9 checks passed
```

## References

- the wrk2 README on coordinated omission; DDSketch, PVLDB 12(12), 2195–2205 (2019).
