# 46. Utilization and queueing delay

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

As utilization ρ approaches 1, waiting explodes: for an M/M/1 queue the time in system is 1/(1 − ρ) service times. Pollaczek–Khinchine adds the effect of variable service times, and Erlang C gives the waiting probability for a pool of servers, which sets how many servers keep waits rare.

## What the program checks

M/M/1 time in system is 2, 5, 10, 20 service times at 50%, 80%, 90%, 95% load; Pollaczek–Khinchine for M/G/1; Erlang C for pooled servers; the staffing rule (smallest pool with P(wait) ≤ 5%) against the Halfin–Whitt limit 1.74√a

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/46-utilization-and-queueing-delay
java QueueingDelay.java
```

JDK 17 or newer, no build step. It prints 35 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
M/M/1 mean time in system (service time 1): rho 0.50: simulated 2.00 vs formula 2.00; rho 0.80: simulated 4.99 vs formula 5.00; rho 0.90: simulated 10.02 vs formula 10.00; rho 0.95: simulated 20.13 vs formula 20.00; 
M/D/1 (constant service time): rho 0.50: simulated 1.50 vs formula 1.50; rho 0.80: simulated 3.00 vs formula 3.00; rho 0.90: simulated 5.54 vs formula 5.50; rho 0.95: simulated 10.55 vs formula 10.50; 
M/G/1 at rho = 0.8 with lognormal service, squared coefficient of variation 4: simulated 11.09, Pollaczek-Khinchine 11.00; constant service gives 3.00, exponential 5.00
time in system over service time: rho 0.5 -> 2, 0.8 -> 5, 0.9 -> 10, 0.95 -> 20, 0.99 -> 100
M/M/1 at rho = 0.8, mean time in system 5.01: median 3.47, p90 11.53, p99 23.10, p99.9 34.94 (an exponential distribution with mean 5 has 3.47, 11.51, 23.03, 34.54)
rho = 0.8 with the same total load, one shared pool of c servers (service time 1): 1 servers: P(wait) 0.800, mean wait 4.000 (simulated 4.011); 2 servers: P(wait) 0.711, mean wait 1.778 (simulated 1.781); 5 servers: P(wait) 0.554, mean wait 0.554 (simulated 0.560); 10 servers: P(wait) 0.409, mean wait 0.205 (simulated 0.207); 50 servers: P(wait) 0.087, mean wait 0.009 (simulated 0.009); 100 servers: P(wait) 0.020, mean wait 0.001 (simulated 0.001); 
smallest pool with P(wait) <= 5% for offered load a: a = 25: 35 servers (+10, 2.00 sqrt(a)); a = 100: 119 servers (+19, 1.90 sqrt(a)); a = 400: 436 servers (+36, 1.80 sqrt(a)); a = 1600: 1671 servers (+71, 1.78 sqrt(a)); a = 6400: 6540 servers (+140, 1.75 sqrt(a));  Halfin-Whitt limit for 5%: 1.740 sqrt(a)
offered load 100 Erlangs (for example 1000 requests/s at 0.1 s each), P(wait): 101 servers: 0.8833; 105 servers: 0.5157; 110 servers: 0.2370; 120 servers: 0.0332; 130 servers: 0.0025; 
QueueingDelay: 35 checks passed
```

## References

- Pollaczek–Khinchine formula; Erlang C; Halfin and Whitt, Operations Research 29(3) (1981) (DOI 10.1287/opre.29.3.567).
