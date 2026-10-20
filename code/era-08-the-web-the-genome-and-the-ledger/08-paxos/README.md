# Paxos: the program

*Era 8 · topic 8 · 1989–1998* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/08-paxos/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/08-paxos/paxos.html) · [All era 8 programs](../README.md)

## How it works

```text
Proposers suggest values; acceptors vote. A value is chosen once a majority of acceptors have accepted it in the
same numbered ballot. Messages may be delayed, repeated or lost, and computers may stop; nothing is assumed about
timing. Each ballot has two phases:
  1. The proposer of ballot n sends prepare(n). An acceptor that has not yet promised anything higher promises to
     ignore every ballot below n, and reports the last vote it cast, if any.
  2. With promises from a majority, the proposer sends accept(n, v), where v must be the value of the highest-
     numbered vote reported to it; only if no one reported a vote may it use its own value. An acceptor votes for
     (n, v) unless it has promised a higher ballot.
Why it is safe: if v was chosen in ballot m, a majority voted for it; any later ballot's majority of promises
overlaps that majority in at least one acceptor, which reports a vote of ballot m or later, so the later ballot
proposes v again. Why it may not finish: two proposers can keep pre-empting each other with higher ballots.
```

## What the program does

```text
1. Exhaustive check: 2 proposers (P1 with ballots 1 and 3 and value A, P2 with ballot 2 and value B), 3 acceptors; every message
   stays in the network forever and can be delivered at any moment, any number of times (so delay, repetition and
   loss are all covered). Every reachable state is visited; in none of them are two different values chosen.
2. The same search with the rule broken (the proposer always uses its own value): the shortest run that chooses
   both A and B, printed step by step. And with quorums of 1 acceptor instead of a majority.
3. Random runs with 5 acceptors and 3 proposers, messages lost and acceptors crashing: agreement every time.
4. Duelling proposers: a schedule in which nothing is ever chosen, and the same proposers with one leader.
5. The scripted run of the book's widget, with the rule kept and broken.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Paxos.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Part-Time Parliament, with Lamport's commentary](https://www.microsoft.com/en-us/research/publication/part-time-parliament/) — Microsoft Research | Why the paper took eight years, in the author's words |
| Deeper | [Paxos Made Simple](https://pdos.csail.mit.edu/archive/6.824-2012/papers/paxos-simple.pdf) — L. Lamport (2001), on an MIT course page | The algorithm in plain English, in eleven pages |
| Deeper | [Paxos (computer science)](https://en.wikipedia.org/wiki/Paxos_(computer_science) — Wikipedia | Variants, guarantees and where it runs |
| Scholar | [The Part-Time Parliament](https://www.cs.princeton.edu/courses/archive/spring13/cos598C/lamport-paxos.pdf) — L. Lamport, *ACM TOCS* (1998), on a Princeton course page | The parliament of Paxos and its proofs |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
