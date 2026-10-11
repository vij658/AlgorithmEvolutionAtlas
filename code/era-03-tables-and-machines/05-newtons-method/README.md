# Newton's Method: the program

*Era 3 · topic 5 · 1669–1740* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/05-newtons-method/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/05-newtons-method/newtons-method.html) · [All era 3 programs](../README.md)

## How it works

```text
Guess a root x of f(x) = 0. Near the guess the curve is almost a straight line, the tangent, whose slope is f'(x);
the tangent crosses zero at x - f(x)/f'(x), which is the next guess. Near a simple root the error is roughly
squared at every step, so the number of correct digits roughly doubles. Newton himself did it differently: for
x^3 - 2x - 5 = 0 he put x = 2 + p, wrote out the new polynomial in p, kept only its two lowest terms (10p - 1 = 0, so
p = 0.1), put p = 0.1 + q, and so on, keeping more digits each time. Raphson (1690) applied the correction to the
original equation over and over instead; Simpson (1740) wrote it with fluxions for any equation, and for two
equations in two unknowns.
```

## What the program does

```text
1. Repeats Newton's own steps on x^3 - 2x - 5 = 0 with exact polynomial shifts, reaching his 2.09455147.
2. Runs Raphson's form to 60 digits and shows the correct digits doubling.
3. Compares the work with digit-by-digit extraction (Era 2, topic 9) and with bisection.
4. Solves a non-polynomial equation (cos x = x) and a system of two equations by Simpson's method (Cramer's rule
   for each step).
5. Shows the method's failures: a 2-cycle, a slow double root, and the basins of z^3 = 1 in the complex plane.
6. Full circle: the Babylonian square root (Era 1, topic 4) is Newton's method, and so is a reciprocal computed
   without division.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java NewtonsMethod.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Newton's method](https://en.wikipedia.org/wiki/Newton%27s_method) — Wikipedia | The method, its history from 1669 to 1740, and why the digits double |
| Deeper | [Historical Development of the Newton–Raphson Method](https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/NewtonRaphson_SIAMRev.pdf) — Tjalling J. Ypma, *SIAM Review* 37(4):531–551 (1995), on a Peking University course page | The standard account: Newton's x³ − 2x − 5 worked step by step, Raphson, Simpson, and the earlier forms |
| Deeper | [Raphson, Joseph](https://mathshistory.st-andrews.ac.uk/DNB/Raphson.html) — *Dictionary of National Biography* (via MacTutor) | Raphson's life, his 1690 book and his independence from the calculus |
| Scholar | [Thomas Simpson and 'Newton's method of approximation': an enduring myth](https://cambridge.org/core/journals/british-journal-for-the-history-of-science/article/thomas-simpson-and-newtons-method-of-approximation-an-enduring-myth/265FA038F1A1873E8850CAFB4468DD8F) — Nick Kollerstrom, *British Journal for the History of Science* 25(3):347–354 (1992); abstract open | The case that the standard method is Simpson's of 1740 |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
