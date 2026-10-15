# Logical Clocks: the program

*Era 6 · topic 13 · 1978* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/13-logical-clocks/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/13-logical-clocks/logical-clocks.html) · [All era 6 programs](../README.md)

## How it works

```text
Computers that cooperate over a network have no common clock, and messages take time to arrive. Lamport asked
what "before" can mean there. Event a "happened before" event b (a -> b) if they are in the same process and a
came first, or a is the sending of a message and b its receipt, or there is a chain of such steps from a to b.
If neither happened before the other, the two are "concurrent": no process could ever tell which came first.
A logical clock is a counter in each process:
    IR1  add 1 between any two events of the process;
    IR2  stamp each message with the sender's counter; on receipt, set the counter above both its own value
         and the stamp.
Then a -> b always implies C(a) < C(b) (the Clock Condition). Breaking ties by process number gives one total
order of all events that every process can compute for itself, consistent with "happened before". Lamport used
it to share a resource with no central scheduler: requests are served in timestamp order.
```

## What the program does

```text
1. Three processes exchanging messages: every event's clock, which pairs are ordered and which concurrent.
2. 500 random runs: the Clock Condition never fails; how often C(a) < C(b) without a -> b.
3. The total order: always consistent with "happened before".
4. Lamport's mutual exclusion: 5 processes, random message delays, 1,000 entries to the shared resource.
5. The anomaly Lamport pointed out: an order the system cannot see (a telephone call) contradicted by the clocks.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LogicalClocks.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [ACM Turing Award Goes to Pioneer Who Advanced Reliability and Consistency of Computing Systems](https://www.acm.org/media-center/2014/march/acm-turing-award-goes-to-pioneer-who-advanced-reliability-and-consistency-of-computing-systems) — ACM (2014) | What logical clocks led to, in the award announcement |
| Start | [Leslie Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport) — Wikipedia | A career in concurrency, from the bakery algorithm to LaTeX |
| Scholar | [Time, Clocks, and the Ordering of Events in a Distributed System](https://amturing.acm.org/p558-lamport.pdf) — L. Lamport, *Communications of the ACM* 21(7): 558–565 (1978) | Eight pages that defined "before" for distributed systems |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
