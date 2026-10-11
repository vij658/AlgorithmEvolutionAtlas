# Binary Arithmetic: the program

*Era 3 · topic 6 · 1703* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/06-binary-arithmetic/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/06-binary-arithmetic/binary-arithmetic.html) · [All era 3 programs](../README.md)

## How it works

```text
Write numbers with two digits, 0 and 1, where each place is worth twice the place to its right: 1101101 means
64 + 32 + 8 + 4 + 1 = 109. To convert, halve again and again and keep the remainders. Addition needs only
"1 + 1 = 10"; multiplication needs no table at all, because each digit of the multiplier is 0 or 1: add a shifted
copy of the number, or don't. That is the Egyptian scribes' doubling (Era 1, topic 5) written as a numeral.
The price is length: a binary numeral is about 3.32 times as long as the decimal one.
```

## What the program does

```text
1. Converts Harriot's 1101101 = 109 both ways, and checks conversion on every number below 2^20.
2. Counts the facts to memorise: addition and multiplication tables in base 10 and base 2.
3. Adds and multiplies 100,000 random pairs bit by bit (shift and add), and counts the work.
4. Shows Egyptian doubling as binary multiplication.
5. Measures the price: digits per number in base 2 and base 10.
6. Full circle: Java prints Harriot's numeral, and stores negative numbers as complements (topic 3).
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java BinaryArithmetic.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Binary number](https://en.wikipedia.org/wiki/Binary_number) — Wikipedia | From Pingala and the *I Ching* to Harriot, Leibniz, Boole and Shannon |
| Start | [Harriot and binary numbers](https://mathshistory.st-andrews.ac.uk/Extras/Harriot_binary_numbers) — MacTutor (after J. W. Shirley, *Am. J. Physics* 19, 1951) | Harriot's conversions and binary arithmetic, a century before Leibniz |
| Deeper | [The binary system was created long before Leibniz](https://cacm.acm.org/blogs/blog-cacm/221749-the-binary-system-was-created-long-before-leibniz/fulltext) — Herbert Bruderer, *Communications of the ACM* blog | Harriot, Napier's chessboard, Caramuel 1670 and Leibniz |
| Scholar | [Why Did Thomas Harriot Invent Binary?](https://fermatslibrary.com/s/why-did-thomas-harriot-invent-binary) — Lloyd Strickland, *The Mathematical Intelligencer* (2023), via Fermat's Library | Dating Harriot's manuscripts (1601–1605) and why he invented binary |
| Scholar | [Explanation of binary arithmetic (1703)](https://kastalia.medienhaus.udk-berlin.de/odl/Leibniz.pdf) — Leibniz, English text © Lloyd Strickland 2007 (hosted at UdK Berlin) | Leibniz's own case for binary: no tables to memorise, and Fuxi's figures |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
