# Karp–Rabin Fingerprints: the program

*Era 7 · topic 9 · 1985–1987* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/09-karp-rabin/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/09-karp-rabin/karp-rabin.html) · [All era 7 programs](../README.md)

## How it works

```text
To find a pattern of m letters in a text of n letters, the obvious method compares the pattern with every
window of the text, letter by letter. Karp and Rabin compare short fingerprints instead. Read the pattern as one
big number (here, 2 bits per letter of the alphabet A, C, G, T) and keep only its remainder modulo a prime p.
The fingerprint of the next window comes from the last one in a few arithmetic steps: drop the first letter, shift,
add the new letter ("rolling"). Only where fingerprints agree are letters compared. Two different windows can
share a fingerprint only if p divides their difference, and a number below 2^64 has at most 15 prime factors, so
if p is chosen at random among many primes, after the text is fixed, false alarms are rare whatever the text.
A fixed, publicly known p is not safe: someone who knows it can write a text full of false alarms.
```

## What the program does

```text
1. Searches a 1,000,000-letter text for patterns: letter comparisons of the obvious method and of fingerprints.
2. False alarms for random primes of different sizes, against the bound from counting prime factors.
3. An adversary who knows a fixed prime, against a prime chosen at random afterwards.
4. One pass for 1,000 patterns at once, against 1,000 separate searches.
5. A 16 x 16 block in a 1,000 x 1,000 grid of letters: the same idea in two dimensions.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java KarpRabin.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Rabin–Karp algorithm](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm) — Wikipedia | Rolling hashes, worked examples, many patterns |
| Deeper | [Fingerprinting & Applications](https://www.cs.ox.ac.uk/people/varun.kanade/teaching/CS174-Fall2012/fingerprint.pdf) — CS 174 lecture notes (2007) | Why a random prime makes false matches unlikely, with the counting argument |
| Deeper | [Rabin fingerprint](https://en.wikipedia.org/wiki/Rabin_fingerprint) — Wikipedia | The polynomial version, and its use for finding block boundaries in file systems |
| Scholar | [Efficient randomized pattern-matching algorithms](https://cris.huji.ac.il/en/publications/efficient-randomized-pattern-matching-algorithms/) — R. Karp, M. Rabin, *IBM J. Res. Dev.* (1987), Hebrew University record | Citation and abstract of the paper |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
