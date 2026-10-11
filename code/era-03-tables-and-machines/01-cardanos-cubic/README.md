# Cardano's Cubic: the program

*Era 3 · topic 1 · 1545 CE* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/01-cardanos-cubic/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/01-cardanos-cubic/cardanos-cubic.html) · [All era 3 programs](../README.md)

## How it works

```text
Any cubic a x^3 + b x^2 + c x + d = 0 becomes y^3 + p y + q = 0 after the shift x = y - b/(3a), which removes the
square term. Now look for y as a sum u + v. Then y^3 = u^3 + v^3 + 3uv(u + v), so if 3uv = -p, the equation
becomes u^3 + v^3 = -q. With uv fixed, u^3 and v^3 are the two roots of the quadratic t^2 + q t - p^3/27 = 0:
  u^3, v^3 = -q/2 +- sqrt(D),   D = (q/2)^2 + (p/3)^3,   y = cbrt(u^3) + cbrt(v^3).
A cubic has been turned into a quadratic plus two cube roots. The trap: when the cubic has three real roots, D is
negative, so the recipe passes through the square root of a negative number (the "irreducible case"). Bombelli
(1572) calculated straight through it: for x^3 = 15x + 4, D = -121, and the cube roots of 2 + sqrt(-121) and
2 - sqrt(-121) are 2 + i and 2 - i, whose sum is the real root 4.
```

## What the program does

```text
1. Removes the square term from a cubic and solves it by the formula, step by step.
2. Repeats Cardano's first calculation with complex numbers, (5 + sqrt(-15))(5 - sqrt(-15)) = 40, and Bombelli's
   x^3 = 15x + 4 in exact integer complex arithmetic.
3. Surveys random cubics: how often the formula must pass through square roots of negatives.
4. Checks the formula, in complex arithmetic, on 100,000 random cubics with known roots.
5. Shows where the formula fails in floating point (cancellation), and how a few correction steps repair it.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java CardanoCubic.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Whopping Cool Math! (March 2013)](https://people.math.harvard.edu/~engelwar/MathS305/Cardanos%20Formula.pdf) — James Tanton, newsletter column (hosted on a Harvard course page) | The Cardano–Tartaglia story, then the cubic formula as guided exercises, ending with an "imaginary" expression that equals 2 |
| Start | [Quadratic, cubic and quartic equations](https://mathshistory.st-andrews.ac.uk/HistTopics/Quadratic_etc_equations/) — MacTutor (O'Connor and Robertson) | The whole story in one page: del Ferro, Fior, Tartaglia, Cardan, Ferrari, Bombelli |
| Start | [Niccolò Fontana Tartaglia](https://mathshistory.st-andrews.ac.uk/Biographies/Tartaglia/) — MacTutor | The contest, the night of 13 February 1535, the verse, the oath and the 1548 debate |
| Start | [Girolamo Cardano](https://mathshistory.st-andrews.ac.uk/Biographies/Cardan/) — MacTutor | Why Cardan felt free to publish, and the first calculation with complex numbers |
| Deeper | [Rafael Bombelli](https://mathshistory.st-andrews.ac.uk/Biographies/Bombelli/) — MacTutor | "Plus of minus": the first rules for calculating with complex numbers |
| Deeper | [A Short History of Complex Numbers](https://math.mit.edu/~dunkel/Teach/18.04_2019S/historic/Merino_2006.pdf) — Orlando Merino, University of Rhode Island (2006), on an MIT course page | Cardano's formula on x³ = 15x + 4, and how Bombelli found the cube roots 2 ± i |
| Deeper | [Bombelli, Rafael](https://mathshistory.st-andrews.ac.uk/DSB/Bombelli.pdf) — S. A. Jayawardene, *Dictionary of Scientific Biography* (via MacTutor) | How the *Algebra* handles the irreducible case |
| Scholar | [Ars Magna, sive de regulis algebraicis (1545)](https://sourcelibrary.org/book/cardano-ars-magna-1545-first-edition-cardano) — Source Library: 172 scans digitized by Smithsonian Libraries (public domain), with an English translation | The book itself, Nuremberg 1545 |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
