# Hashing: the program

*Era 5 · topic 4 · 1953–1957* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/04-hashing/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/04-hashing/hashing.html) · [All era 5 programs](../README.md)

## How it works

```text
To find a record without searching the whole file, compute its place from its key. A hash function scrambles the
key into a number between 0 and m - 1, the record goes into that slot, and a search computes the same number and
looks only there. Two keys can land on the same slot (a collision). Luhn's memorandum of January 1953 kept a
bucket of records at each slot (chaining). Amdahl's idea for the IBM 701 assembler, published by Peterson in
1957, keeps one table: if the slot is taken, try the next one, and the next (open addressing with linear
probing). Either way, while the table is not too full, a search takes a few probes however large the file is.
Dumey (1956) took the key as a number and kept the remainder after dividing by a prime.
```

## What the program does

```text
1. Luhn's example of a bucket number: add the digits of a phone number in pairs and keep the last digit of each sum.
2. Chaining and linear probing at load factors from 0.5 to 0.95: average probes for a search that finds its key
   and for one that does not, measured, against the classical formulas.
3. Peterson's 1957 experiment: a store of 10,000 records in buckets of 20, filled with random keys from 40% to
   100%, and buckets of 1 with 500 records; our averages beside the figures in his tables.
4. Remainders: keys that share a pattern, divided by a power of two and by a prime.
5. The payoff: probes per search as the file grows from a thousand to a million keys, against binary search.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Hashing.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Hans Peter Luhn and the Birth of the Hashing Algorithm](https://spectrum.ieee.org/tech-history/silicon-revolution/hans-peter-luhn-and-the-birth-of-the-hashing-algorithm) — Hallam Stevens, IEEE Spectrum (2018) | Luhn's buckets, told with his phone-number example |
| Start | [Linear probing](https://en.wikipedia.org/wiki/Linear_probing) — Wikipedia | Amdahl's next-free-slot method, its history and its cost |
| Start | [Hans Peter Luhn](https://en.wikipedia.org/wiki/Hans_Peter_Luhn) — Wikipedia | The engineer behind hashing, the Luhn checksum and KWIC indexes |
| Deeper | [History of hashing, *The Art of Computer Programming* §6.4](https://www.Gwern.net/doc/cs/algorithm/information/compression/1998-knuth-taocp-v3-sortingandsearching-hashinghistory.pdf) — Donald E. Knuth (excerpt, 1998 edition) | Who did what between 1953 and 1967, from interviews and memoranda |
| Scholar | [Indexing for Rapid Random Access Memory Systems](https://bitsavers.mirrorservice.org/magazines/Computers_And_Automation/195612.pdf) — Arnold I. Dumey, *Computers and Automation* 5(12): 6–9 (December 1956), scan at bitsavers | The first published description: divide by a prime, keep the remainder |
| Scholar | [Addressing for Random-Access Storage](https://www.Gwern.net/doc/cs/algorithm/1957-peterson.pdf) — W. W. Peterson, *IBM Journal* (April 1957), 130–146 | Open addressing measured: the tables this topic's program repeats |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
