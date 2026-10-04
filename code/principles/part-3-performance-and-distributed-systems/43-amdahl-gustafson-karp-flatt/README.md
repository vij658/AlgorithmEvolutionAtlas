# 43. Amdahl, Gustafson, Karp–Flatt and list scheduling

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Amdahl: if a fraction s of the work is serial, speed-up on p workers is at most 1/(s + (1 − s)/p), capped at 1/s. Gustafson: if the problem grows with p, scaled speed-up is s + (1 − s)·p. Karp–Flatt recovers the serial fraction from a measured speed-up, and Graham's bound limits greedy list scheduling to within 2 − 1/p of optimal.

## What the program checks

With 5% serial work the speedup is 5.93 on 8 workers, 15.42 on 64, 19.64 on 1024, limit 20; efficiency falls to 1.9% on 1024. Gustafson's scaled speedup on 64 workers: 60.85. Karp–Flatt recovers a serial fraction of 0.0500 from a measured speedup of 5.9259

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/43-amdahl-gustafson-karp-flatt
java SpeedupLaws.java
```

JDK 17 or newer, no build step. It prints 50,003 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
Amdahl, p = 0.95: speedup 5.93 on 8 workers, 15.42 on 64, 19.64 on 1024, limit 20
efficiency (speedup / workers) at p = 0.95: 74% on 8 workers, 24% on 64, 1.9% on 1024
same 5% serial part, but the problem grows with the machine (Gustafson): 60.85 on 64 workers, against Amdahl's 15.42
limits 1/(1-p): p = 0.5 -> 2, 0.9 -> 10, 0.99 -> 100, 0.999 -> 1000
10 equal tasks on 64 workers finish in 1.0 time units, a speedup of 10, where Amdahl with p = 1 would promise 64
Karp-Flatt: a measured speedup of 5.9259 on 8 workers implies a serial fraction of 0.0500
SpeedupLaws: 50003 checks passed
```

## References

- Amdahl, AFIPS 1967 (DOI 10.1145/1465482.1465560); Gustafson, "Reevaluating Amdahl's law", CACM 31(5), 532–533 (1988); Karp and Flatt, CACM 33(5), 539–543 (1990); Graham, "Bounds for certain multiprocessing anomalies", Bell System Technical Journal 45(9), 1563–1581 (1966).
