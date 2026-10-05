# Euclid's Algorithm: the program

*Era 1 · topic 7 · c. 300 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/07-euclids-algorithm/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/07-euclids-algorithm/euclids-algorithm.html) · [All era 1 programs](../README.md)

## How it works

```text
To find the greatest common divisor of a and b, replace the pair (a, b) by (b, a mod b) until the second number
is 0; the first number is then the answer. Euclid did it by repeated subtraction ("the less is continually
subtracted in turn from the greater"); one division does a whole run of those subtractions at once. Drawn as a
picture: cut the biggest possible squares off an a-by-b rectangle, again and again; the side of the last square
is the gcd, and the number of squares cut at each stage (the quotients) is the continued fraction of a/b.
```

## What the program does

```text
1. The four ways to find a gcd that the book compares: trying every candidate, repeated subtraction (Euclid's
   own form), division (the modern form) and Stein's binary GCD (shifts and subtraction only).
2. The extended algorithm (Aryabhata's "pulverizer"), which also finds x, y with a*x + b*y = gcd(a, b), and the
   modular inverse that RSA key generation uses.
3. Checks: every method agrees with BigInteger.gcd on hundreds of thousands of random pairs; Bezout's identity
   holds; Lame's bound (steps <= 5 x digits of the smaller number) holds; consecutive Fibonacci numbers are the
   worst case. Random inputs use fixed seeds, so every run prints the same numbers.
4. The measurements behind the book's tables and charts (each printed line starts with a tag the figure script
   reads): the worked example 1071 and 462, a comparison of the four methods, worst cases by number of digits,
   average steps by number of digits, and the distribution of steps for random 18-digit pairs.
```

## Run it

```
java EuclidsAlgorithm.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Euclid's Algorithm](https://www.youtube.com/watch?v=6Y3jHHE_hbA) — Numberphile (Sophie Maclean) | The algorithm and its Fibonacci connection |
| Start | [The Euclidean Algorithm (Finding the GCD/GCF)](https://www.youtube.com/watch?v=SR-jmdjzw-Y) — Houston Math Prep | Step-by-step worked examples |
| Start | [Here's looking at Euclid](https://www.youtube.com/watch?v=9O97Xad-iTQ) — Gresham College, Robin Wilson (2004) | Greek mathematics and the *Elements*, with the Euclidean algorithm in context |
| Start | [Euclid's Algorithm](https://www.cut-the-knot.org/blue/Euclid.shtml) — Cut the Knot | gcd(*a*, *b*) = gcd(*b*, *r*) with a worked example, and Bézout's identity |
| Deeper | [Lec 4, MIT 6.042J Mathematics for Computer Science](https://www.youtube.com/watch?v=NuY7szYSXSw) — MIT OpenCourseWare (2010) | GCD, Euclid's algorithm, the Pulverizer (extended Euclid) |
| Deeper | [2.1.2 Euclidean Algorithm](https://www.youtube.com/watch?v=dW0f62lcCLE) — MIT OpenCourseWare (6.042J, 2015) | Short course segment |
| Deeper | [Euclidean Algorithm](https://mathworld.wolfram.com/EuclideanAlgorithm.html) — Wolfram MathWorld | Lamé's bound, Fibonacci worst case, average-case step count |
| Deeper | [Euclid of Alexandria](https://mathshistory.st-andrews.ac.uk/Biographies/Euclid/) — MacTutor | What is (and is not) known about Euclid |
| Scholar | [Introduction to number theory lecture 3: divisibility and Euclid's algorithm](https://www.youtube.com/watch?v=pVKhDtOjji8) — Richard Borcherds (UC Berkeley) | Rigorous treatment; continues in lecture 4 |
| Scholar | [Elements VII.1](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII1.html) — David E. Joyce, Clark University | The propositions with commentary and worked examples |
| Scholar | [Origins of the analysis of the Euclidean algorithm](https://www.sciencedirect.com/science/article/pii/S0315086084710317) — Jeffrey Shallit, Historia Mathematica 21 (1994) | Who first bounded the running time |
| Scholar | [Aryabhata I](https://mathshistory.st-andrews.ac.uk/Biographies/Aryabhata_I/) — MacTutor History of Mathematics | The kuttaka and its link to Euclid's algorithm |
| Scholar | [A Method for Obtaining Digital Signatures and Public-Key Cryptosystems](https://people.csail.mit.edu/rivest/Rsapaper.pdf) — Rivest, Shamir and Adleman (1977) | RSA computes its exponents with "a variation of Euclid's algorithm" |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
