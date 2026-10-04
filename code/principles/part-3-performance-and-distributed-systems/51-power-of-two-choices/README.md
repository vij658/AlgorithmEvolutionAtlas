# 51. The power of two choices

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Put each ball in the less loaded of two randomly chosen bins instead of one random bin. The maximum load drops from about log n / log log n to log log n / log 2: an exponential improvement from one extra choice.

## What the program checks

With 1,000,000 balls in 1,000,000 bins the busiest bin holds 8.6 with one choice and 4.0 with two

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/51-power-of-two-choices
java PowerOfTwoChoices.java
```

JDK 17 or newer, no build step. It prints 5 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
busiest bin when n balls go into n bins (mean of 20 runs, 5 runs at one million): n = 1,000: one choice 5.6, two 3.0, three 2.6; n = 10,000: one choice 6.6, two 3.2, three 3.0; n = 100,000: one choice 7.7, two 3.5, three 3.0; n = 1,000,000: one choice 8.6, two 4.0, three 3.0; 
heavily loaded: 1,000,000 balls in 1,000 bins (mean load 1000), mean of 10 runs: the busiest bin is 98.2 above the mean with one choice and 2.0 above with two (worst run 2)
PowerOfTwoChoices: 5 checks passed
```

## References

- Azar, Broder, Karlin and Upfal, SIAM Journal on Computing 29(1), 180–200 (1999); Envoy's least-request balancer (N = 2 random hosts, "nearly as good as an O(N) full scan").
