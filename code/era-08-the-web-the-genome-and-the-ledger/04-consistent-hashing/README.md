# Consistent Hashing: the program

*Era 8 · topic 4 · 1997* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/04-consistent-hashing/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/04-consistent-hashing/consistent-hashing.html) · [All era 8 programs](../README.md)

## How it works

```text
Many servers share many keys (web pages, files, records). The obvious rule, server = hash(key) mod N, spreads
them evenly, but when N changes almost every key gets a new server: hash mod 10 and hash mod 11 agree for only
about one key in 11. Consistent hashing puts servers and keys on the same circle of hash values and gives each key
to the first server clockwise from it. A new server takes over only the keys between it and the server before it;
a server that leaves hands its keys to the next one; nothing else moves. One point per server gives uneven arcs,
so each server is placed at many points ("virtual nodes"), which evens out the load.
Chord (2001) finds a key's server without any central list: each node knows the nodes 1, 2, 4, 8, ... positions
ahead on the circle (its "fingers"), and each hop at least halves the remaining distance, so a lookup among N
nodes takes about log2 N hops.
Rendezvous hashing (1996) is a relative: each key goes to the server with the highest hash(key, server).
```

## What the program does

```text
1. 100,000 keys on 10 servers, then 11: how many move under mod-N, the circle and rendezvous hashing, and where.
2. A server leaves: only its keys move, all to its successor.
3. Load balance with 1 to 1,000 points per server.
4. Clients that know different sets of servers: how many servers does one key end up on ("spread")?
5. Chord: 1,024 nodes, 10,000 lookups by fingers.
6. A small circle of named servers and keys for the book's widget, hashed with 32-bit FNV-1a and a mixing step.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ConsistentHashing.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Consistent hashing](https://en.wikipedia.org/wiki/Consistent_hashing) — Wikipedia | The circle, virtual nodes and where it is used |
| Scholar | [Consistent Hashing and Random Trees](https://cs.brown.edu/courses/csci2950-u/f09/papers/chash97stoc.pdf) — D. Karger et al., STOC (1997), on a Brown course page | Hot spots, the four properties and the construction |
| Scholar | [Chord: A Scalable Peer-to-peer Lookup Service for Internet Applications](https://pdos.csail.mit.edu/archive/6.824-2012/papers/stoica-chord.pdf) — I. Stoica et al., SIGCOMM (2001), on an MIT course page | Consistent hashing without a central directory |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
