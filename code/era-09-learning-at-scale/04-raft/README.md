# Raft: the program

*Era 9 · topic 4 · 2014* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/04-raft/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/04-raft/raft.html) · [All era 9 programs](../README.md)

## How it works

```text
A cluster of servers keeps one replicated log of commands. Time is divided into numbered terms. In each term at
most one server is leader; the others are followers. A follower that hears nothing from a leader for an
election timeout (chosen at random, here 150 to 300 ms) becomes a candidate: it increases its term, votes for
itself and asks the others for votes. A server votes at most once per term, and only for a candidate whose log
is at least as up to date as its own (a later last term, or the same last term and at least as long). A
candidate with votes from a majority becomes leader.
The leader appends client commands to its log and sends them to the followers (AppendEntries), each message
naming the index and term of the entry just before the new ones; a follower accepts only if its log has that
entry, otherwise the leader backs up and tries an earlier point. An entry is committed once a majority stores
it and it is from the leader's current term; committed entries are applied to each server's state machine in
order. Messages may be lost, delayed or reordered, and servers may crash and restart; the rules keep five
properties true: Election Safety, Leader Append-Only, Log Matching, Leader Completeness, State Machine Safety.
```

## What the program does

```text
1. Simulates a 5-server cluster for many runs with lost and delayed messages, crashes, restarts and network
   partitions, sending client commands throughout, and checks all five safety properties continuously.
2. Randomized against fixed election timeouts: how long the cluster is without a leader after a leader crashes,
   and how many elections end in a split vote.
3. Breaks one rule (votes are granted without checking that the candidate's log is up to date) and lets the
   same checker find a committed entry that is lost.
4. A short scripted run for the book's page: who leads in which term, and what each log holds.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Raft.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Raft Consensus Algorithm](https://raft.github.io/) — raft.github.io | An interactive cluster to break |
| Deeper | [Distributed Systems 6.2: Raft](https://www.youtube.com/watch?v=uXEYuDwm7e4) — Martin Kleppmann | A lecture from Kleppmann's Cambridge course |
| Scholar | [Raft lecture (Raft user study)](https://www.youtube.com/watch?v=YbZ3zDzDnrw) — Diego Ongaro | The lecture recorded for the user study, by Raft's designer |
| Scholar | [In Search of an Understandable Consensus Algorithm](https://www.cs.princeton.edu/courses/archive/spring22/cos418/papers/raft.pdf) — D. Ongaro, J. Ousterhout (2014), on a Princeton course page | The algorithm, the safety properties and the user study |
| Scholar | [USENIX ATC '14 paper page](https://usenix.org/node/184041) — USENIX | Venue, pages and award |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
