# 61. Gossip (epidemic) protocols

*Part 3 — Performance laws and distributed systems (entries 43–62)* · [All programs](../../README.md) · [Part 3 status](../../../../book/principles-catalog/part-3-status-and-plan.md)

## How it works

Each node periodically tells a random peer what it knows (push), asks a random peer (pull), or both. A rumour reaches all n nodes in about log₂ n + ln n rounds with push, and faster with push-pull.

## What the program checks

Rounds until every node knows a rumor, for push, pull and push-pull, against the formulas

*The catalog page for Part 3 is not written yet; this summary comes from the program's output.*

## Run it

```
cd code/principles/part-3-performance-and-distributed-systems/61-gossip
java Gossip.java
```

JDK 17 or newer, no build step. It prints 12 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
rounds until every node knows the rumor, one random contact per node per round, mean of 30 runs (5 at a million nodes): n = 1,024: push 18.2 (log2 n + ln n = 16.9), pull 14.3 (log2 n + log2 ln n = 12.8), push-pull 9.2 (log3 n = 6.3); n = 16,384: push 25.0 (log2 n + ln n = 23.7), pull 18.2 (log2 n + log2 ln n = 17.3), push-pull 12.0 (log3 n = 8.8); n = 131,072: push 30.0 (log2 n + ln n = 28.8), pull 21.7 (log2 n + log2 ln n = 20.6), push-pull 14.1 (log3 n = 10.7); n = 1,048,576: push 34.2 (log2 n + ln n = 33.9), pull 24.6 (log2 n + log2 ln n = 23.8), push-pull 16.2 (log3 n = 12.6); 
Gossip: 12 checks passed
```

## References

- Demers et al., PODC 1987; Karp et al., FOCS 2000; Pittel (1987); Doerr and Kostrygin, ICALP 2017.
