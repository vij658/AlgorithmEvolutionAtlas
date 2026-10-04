# Part 3 — Performance laws and distributed systems: status and plan

*Companion volume, Part 3 (entries 43–62).* All twenty programs are written and verified; **the page text is not written yet.** Each entry links to its program folder, where the README explains the idea and shows the program's full output.

| Piece | Entries | State | Checks passed |
|---|---|---|---|
| [Part 1](part-1-distances-and-number-theory.md): distances, similarity, number theory | 1–20 | Written | 1,221,141 |
| [Part 2](part-2-paradigms-and-classics.md): algorithm paradigms and classics | 21–42 | Written | 6,914,381 |
| Part 3: performance laws and distributed systems | 43–62 | **Programs verified; page not written** | 154,369,152 |
| Part 4: security and identity | | Not started | |
| Part 5: design laws and engineering principles | | Not started | |

Counts are from runs on OpenJDK 21.0.12 (`java File.java`, exit status 0 for every program). See [all programs and their counts](../../code/principles/README.md).

## What each entry checks (headline results from the program output)

| # | Entry | What the program checks, and a headline number |
|---|---|---|
| [43](../../code/principles/part-3-performance-and-distributed-systems/43-amdahl-gustafson-karp-flatt) | Amdahl, Gustafson, Karp–Flatt, list scheduling | With 5% serial work the speedup is 5.93 on 8 workers, 15.42 on 64, 19.64 on 1024, limit 20; efficiency falls to 1.9% on 1024. Gustafson's scaled speedup on 64 workers: 60.85. Karp–Flatt recovers a serial fraction of 0.0500 from a measured speedup of 5.9259 |
| [44](../../code/principles/part-3-performance-and-distributed-systems/44-universal-scalability-law) | Universal Scalability Law | α = 0.03, β = 0.0005 gives a peak of 13.60 at 44 workers. Fitting from noisy measurements at 1–16 workers predicts peaks anywhere from 25 to 602 (and 4 of 20 fits find no peak); with measurements out to 128 workers the range tightens to 42.2–46.7 |
| [45](../../code/principles/part-3-performance-and-distributed-systems/45-littles-law) | Little's law | Holds to 1e-9 on nine simulated queues; 500 requests/s × 0.2 s = 100 requests in flight |
| [46](../../code/principles/part-3-performance-and-distributed-systems/46-utilization-and-queueing-delay) | Utilization and queueing delay | M/M/1 time in system is 2, 5, 10, 20 service times at 50%, 80%, 90%, 95% load; Pollaczek–Khinchine for M/G/1; Erlang C for pooled servers; the staffing rule (smallest pool with P(wait) ≤ 5%) against the Halfin–Whitt limit 1.74√a |
| [47](../../code/principles/part-3-performance-and-distributed-systems/47-zipf-and-cache-sizing) | Zipf's law and cache sizing | Caching the top 1% of items serves 68.0% of requests at exponent 1 (1,000,000 items) |
| [48](../../code/principles/part-3-performance-and-distributed-systems/48-lru-belady-min-and-anomaly) | LRU, Bélády's MIN, Bélády's anomaly | The anomaly on the classic trace (FIFO 9 faults with 3 frames, 10 with 4); LRU never shows it on 2,000 random traces; hit rates of LRU, FIFO, random and MIN on a Zipf trace |
| [49](../../code/principles/part-3-performance-and-distributed-systems/49-tail-latency-and-fan-out) | Tail latency and fan-out | At fan-out 100, 63.3% of user requests are slower than one server's p99; hedging after the p95 costs 5.0% extra load and cuts p99 from 103 ms to 67 ms |
| [50](../../code/principles/part-3-performance-and-distributed-systems/50-percentiles-and-coordinated-omission) | Percentiles, histograms, coordinated omission | A log histogram with 1% relative error (811 buckets) is within 0.79% of the exact percentiles; averaging two servers' p99s gives 554.9 ms against a true p99 of 12.0 ms; a closed-loop benchmark hides a 1 s stall |
| [51](../../code/principles/part-3-performance-and-distributed-systems/51-power-of-two-choices) | The power of two choices | With 1,000,000 balls in 1,000,000 bins the busiest bin holds 8.6 with one choice and 4.0 with two |
| [52](../../code/principles/part-3-performance-and-distributed-systems/52-exponential-backoff-and-jitter) | Exponential backoff and jitter | 200 clients against a server taking 5 requests/ms: retrying at once costs 4,100 requests, full jitter 644, decorrelated jitter 496 |
| [53](../../code/principles/part-3-performance-and-distributed-systems/53-retry-amplification-and-budgets) | Retry amplification and retry budgets | 3 layers × 4 attempts against a dead service means 64 calls at the bottom per user request; a 10% retry budget keeps the system recoverable where immediate retries leave it stuck |
| [54](../../code/principles/part-3-performance-and-distributed-systems/54-circuit-breaker) | Circuit breaker | A 65 s outage: 6,500 calls reach the dependency without a breaker, 11 with one |
| [55](../../code/principles/part-3-performance-and-distributed-systems/55-rate-limiting) | Token bucket, GCRA, fixed and sliding windows | A burst at a window boundary: fixed window admits 200 against a limit of 100, sliding log admits 100 |
| [56](../../code/principles/part-3-performance-and-distributed-systems/56-cache-stampede) | Cache stampede | One hot key: plain TTL reloads 499.8 times per cycle, XFetch 2.6, single flight 1.0 |
| [57](../../code/principles/part-3-performance-and-distributed-systems/57-quorums) | Quorums, R + W > N | Measured stale-read rates match the formula (for example 0.6667 vs 0.6673 for N = 3, R = 1, W = 1); availability for several (N, R, W) |
| [58](../../code/principles/part-3-performance-and-distributed-systems/58-lamport-and-vector-clocks) | Lamport and vector clocks | Lamport clocks give concurrent events different numbers 92.1% of the time; vector clocks identify every concurrent pair |
| [59](../../code/principles/part-3-performance-and-distributed-systems/59-crdts) | CRDTs | Counters, sets and registers converge; last-writer-wins with 50 ms clock skew lets the earlier write win 24.0% of the time when the writes are 50 ms apart |
| [60](../../code/principles/part-3-performance-and-distributed-systems/60-idempotency) | Idempotency | With retries and crashes: no key 10.02% duplicates; key recorded first 10.10% lost; work first 9.96% duplicates; work and key in one transaction exactly once |
| [61](../../code/principles/part-3-performance-and-distributed-systems/61-gossip) | Gossip | Rounds until every node knows a rumor, for push, pull and push-pull, against the formulas |
| [62](../../code/principles/part-3-performance-and-distributed-systems/62-merkle-trees) | Merkle trees | Finding differences between two 65,536-slot replicas: 33 comparisons for one difference; the second-preimage trap without RFC 6962's prefixes |

## Sources

These were checked against the source pages when the programs were written. Links will be added as the book's reference catalog reaches each topic.

- **43:** Amdahl, AFIPS 1967 (DOI 10.1145/1465482.1465560); Gustafson, "Reevaluating Amdahl's law", CACM 31(5), 532–533 (1988); Karp and Flatt, CACM 33(5), 539–543 (1990); Graham, "Bounds for certain multiprocessing anomalies", Bell System Technical Journal 45(9), 1563–1581 (1966).
- **44:** Gunther's Universal Scalability Law (perfdynamics.com/Manifesto/USLscalability.html).
- **45:** Little, "A proof for the queuing formula L = λW", Operations Research 9(3) (1961) (DOI 10.1287/opre.9.3.383).
- **46:** Pollaczek–Khinchine formula; Erlang C; Halfin and Whitt, Operations Research 29(3) (1981) (DOI 10.1287/opre.29.3.567).
- **47:** Breslau et al., "Web caching and Zipf-like distributions", INFOCOM 1999 (the exponent varies by trace).
- **48:** Bélády, Nelson and Shedler, CACM 12(6), 349–353 (1969); Mattson et al., IBM Systems Journal 9(2), 78–117 (1970); Sleator and Tarjan, "Amortized efficiency of list update and paging rules", CACM 1985.
- **49:** Dean and Barroso, "The Tail at Scale", CACM 2013.
- **50:** the wrk2 README on coordinated omission; DDSketch, PVLDB 12(12), 2195–2205 (2019).
- **51:** Azar, Broder, Karlin and Upfal, SIAM Journal on Computing 29(1), 180–200 (1999); Envoy's least-request balancer (N = 2 random hosts, "nearly as good as an O(N) full scan").
- **52:** Marc Brooker, "Exponential Backoff And Jitter", AWS Architecture Blog (2015).
- **53:** Google SRE book, "Addressing Cascading Failures" (64 = 4³ attempts; retry budgets); Finagle retry budgets (20% plus 10 per second); gRPC proposal A6 (retry throttling); Bronson et al., "Metastable Failures in Distributed Systems", HotOS 2021.
- **54:** Martin Fowler, "CircuitBreaker".
- **56:** Vattani et al., PVLDB 8(8), 886–897 (2015) (XFetch, probabilistic early recomputation).
- **57:** DeCandia et al., "Dynamo" (SOSP 2007); Gifford, "Weighted Voting for Replicated Data" (1979, Xerox PARC report CSL-79-14).
- **58:** Lamport, "Time, clocks, and the ordering of events in a distributed system", CACM 21(7), 558–565 (1978); Fidge (1988); Mattern (1988).
- **59:** Shapiro et al., "Conflict-free replicated data types", SSS 2011.
- **60:** Stripe's documentation on idempotent requests.
- **61:** Demers et al., PODC 1987; Karp et al., FOCS 2000; Pittel (1987); Doerr and Kostrygin, ICALP 2017.
- **62:** RFC 6962 (Certificate Transparency); section 3.5 on the Signed Tree Head is **not yet verified**.

**Do not state without fetching first:** the Berenbrink et al. citation for the heavily-loaded case of the power of two choices; an optimality claim attributed to Aho, Denning and Ullman; the exact wording of Envoy's herding warning; Resilience4j defaults; Guava and Caffeine loading-cache semantics; the citation details of Bélády's 1966 MIN paper; gRPC's hedging fields.

## What is left for Part 3

1. Write the page text in the same style as Parts 1 and 2: how to read, the two groups (A: performance laws; B: distributed systems), entries 43–62 each with idea, formula, Java snippet, a **Verified** note, a **Pitfall** note, quick reference table and sources.
2. Planned extra experiments (not yet in the programs):
   - an in-flight-count check for Little's law (the number in flight in an M/G/∞ system is Poisson: 500 requests/s × 0.2 s);
   - herding with stale load information for the power of two choices (`gapWithStaleInfo`);
   - a `retry(...)` helper with a fake sleeper, tested in entry 52;
   - a test in entry 56 that waiters on a failed single-flight load receive the loader's exception.
3. Build it with the [page builder](../../code/tools/README.md) into `html/part-3-performance-and-distributed-systems.html`.

## Parts 4 and 5, and the index

Part 4 (*Security and identity*) and Part 5 (*Design laws and engineering principles*) have no entry lists yet, and the lookup table across all parts was not started.

## Open question

Whether to write Part 3 as a page in the catalog's style, or to fold these programs into the book's timeline as *Prove it* layers when the timeline reaches each topic (the plan for Parts 4 and 5).
