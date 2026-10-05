# The Sieve of Eratosthenes: the program

*Era 1 · topic 9 · c. 240 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/09-sieve-of-eratosthenes/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/09-sieve-of-eratosthenes/sieve-of-eratosthenes.html) · [All era 1 programs](../README.md)

## How it works

```text
To list the primes up to N, do not test each number for divisors. Write all the numbers down, then for each prime
p in turn cross out its multiples. Whatever is never crossed out is prime. Two refinements make it fast: start
crossing at p x p (smaller multiples were already crossed by smaller primes), and stop once p x p passes N. The work
is about N log log N crossings, far less than testing each number by division.
Nicomachus's account crosses out with every odd number, not only with primes; the extra work is wasted but the
answer is the same. The linear sieve crosses each composite exactly once.
```

## What the program does

```text
1. Counts the work of six ways to list the primes up to N: trial division by primes up to the square root, the
   "unfaithful sieve" of functional programming (each number tested against every earlier prime, O'Neill 2009),
   sieving odd numbers with every odd number (as in Nicomachus's account) or with odd primes only, the textbook
   sieve (primes from p x p over all numbers), and the linear sieve.
2. Checks that all six agree, and counts the primes: 25 below 100, up to 5,761,455 below 100,000,000 (with a
   segmented sieve that holds only a small window in memory).
3. Compares the crossings with N log log N and the prime counts with N / ln N.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java SieveOfEratosthenes.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Sieve of Eratosthenes](https://www.youtube.com/watch?v=klcIklsWzrY) — Khan Academy (Journey into cryptography) | Animated introduction, framed by cryptography |
| Start | [Prime-time mathematics](https://www.youtube.com/watch?v=heY6nsELLVk) — Gresham College, Robin Wilson (2005) | Walks through sifting the numbers up to 100 |
| Start | [Sieve of Eratosthenes](https://mathworld.wolfram.com/SieveofEratosthenes.html) — Wolfram MathWorld | The procedure, and how Nicomachus preserved it |
| Deeper | [Infinite Data Structures: To Infinity & Beyond!](https://www.youtube.com/watch?v=bnRNiE_OVWA) — Computerphile (Graham Hutton) | An infinite list of primes in Haskell: the classic "sieve" that O'Neill's paper critiques |
| Deeper | [Sieve of Eratosthenes](https://cp-algorithms.com/algebra/sieve-of-eratosthenes.html) — CP-Algorithms | Proof of *n* log log *n*, the segmented sieve, block-size advice |
| Deeper | [Eratosthenes of Cyrene](https://mathshistory.st-andrews.ac.uk/Biographies/Eratosthenes/) — MacTutor | Life and work. Note: it credits the account to "Nicomedes", a slip for Nicomachus |
| Scholar | [Turner, Bird, Eratosthenes: an eternal burning thread](https://www.cambridge.org/core/journals/journal-of-functional-programming/article/turner-bird-eratosthenes-an-eternal-burning-thread/32E2EDF5D5EAEC95F13D313BC97B86F0) — Jeremy Gibbons, J. Functional Programming 35 (2025) | A follow-up to O'Neill on lazy sieves |
| Scholar | [Introduction to Arithmetic](https://archive.org/details/nicomachus-introduction-to-arithmetic) — Nicomachus, trans. D'Ooge (1926), Internet Archive | The earliest surviving account (Book I, Ch. 13). Also on Zenodo |
| Scholar | [The Genuine Sieve of Eratosthenes](https://www.cs.hmc.edu/~oneill/papers/Sieve-JFP.pdf) — Melissa O'Neill, J. Functional Programming 19 (2009) | Author's PDF; cite JFP 19(1):95–106 |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
