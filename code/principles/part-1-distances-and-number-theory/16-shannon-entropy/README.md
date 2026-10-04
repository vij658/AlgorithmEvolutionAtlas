# 16. Shannon entropy

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#16-shannon-entropy)

## How it works

Entropy H = −Σ p·log₂ p is the average number of bits needed per symbol from a source. It bounds lossless compression and measures how many guesses a secret is worth. It describes the process that produced the data, not one particular string.

## In depth (from the catalog page)

`H = −Σ pᵢ log₂ pᵢ` is the average number of bits needed to describe an outcome drawn from a distribution. It lower-bounds lossless compression, measures information gain in decision trees, and sizes secrets.

```java
static double entropyBits(double... p) {
    double h = 0;
    for (double x : p) if (x > 0) h -= x * (Math.log(x) / Math.log(2));
    return h;
}
```

> **Verified.** A fair coin has 1 bit, four equally likely outcomes have 2 bits, and a 90/10 coin has 0.469 bits. A password of 12 characters drawn uniformly at random from 94 printable symbols has 12·log₂(94) = 78.66 bits. Six Diceware words (from a 7,776-word list) have 77.55 bits, and four words have 51.70.

<!-- -->

> **Pitfall.** Entropy describes how a secret was chosen, not how it looks. Those figures hold only for uniformly random choices; a human-picked "random-looking" password has far less.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/16-shannon-entropy
java ShannonEntropy.java
```

JDK 17 or newer, no build step. It prints 3 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
12 random chars from 94 symbols = 78.66 bits; 6 Diceware words = 77.55 bits; 4 words = 51.70 bits
ShannonEntropy: 3 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
