# Mutual Exclusion and the Semaphore: the program

*Era 6 · topic 2 · 1962–1965* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/02-semaphores/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/02-semaphores/semaphores.html) · [All era 6 programs](../README.md)

## How it works

```text
Two programs that run at the same time and share memory can interfere: if both read a counter, add one, and write
it back, one of the additions can be lost. Each must have a "critical section" that the other may not enter at
the same moment. With nothing but shared variables this is surprisingly hard; Dijkstra credited Th. J. Dekker with
the first correct solution for two processes. Dijkstra's own remedy is the semaphore, a shared non-negative
integer with two indivisible operations: P waits until the value is positive and then lowers it by one; V raises
it by one. A semaphore that starts at 1, with P before the critical section and V after it, lets one process in.
Because running programs can interleave in astronomically many ways, the only convincing test is to try every
interleaving. This program does exactly that: it explores every state that the programs can reach.
```

## What the program does

```text
1. Two processes add one to a shared counter: every interleaving of their loads and stores, and how many lose an
   update; the same with a semaphore around the addition.
2. Three plausible attempts at mutual exclusion with shared flags, and Dekker's algorithm: every reachable state
   searched for two processes in their critical sections at once, and for states from which one of them can
   never get in again.
3. A semaphore protecting three processes.
4. The "deadly embrace": two processes taking two semaphores in opposite orders, and in the same order.
5. A producer and a consumer sharing a buffer of two places, governed by two semaphores.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Semaphores.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Dekker's algorithm](https://en.wikipedia.org/wiki/Dekker%27s_algorithm) — Wikipedia | Flags and a turn: the first correct solution, and why modern processors need more |
| Deeper | [Edsger Wybe Dijkstra (1930–2002): A Portrait of a Genius](https://arxiv.org/pdf/cs/0210001) — Krzysztof R. Apt (2002), arXiv | Semaphores, THE, the deadly embrace and the dining philosophers, in context |
| Deeper | [Origin of P and V](https://cs.nyu.edu/~yap/classes/os/resources/origin_of_PV.html) — New York University course page | One account of the Dutch words behind P and V |
| Scholar | [Cooperating sequential processes (EWD 123)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html) — E. W. Dijkstra (1965), transcription at the E. W. Dijkstra Archive | The essay that stated the problem and introduced P and V to a wide audience |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
