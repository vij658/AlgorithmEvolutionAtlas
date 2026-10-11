# Monte Carlo: the program

*Era 4 · topic 10 · 1946–1949* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/10-monte-carlo/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/10-monte-carlo/monte-carlo.html) · [All era 4 programs](../README.md)

## How it works

```text
To find a probability or an average that is too tangled to calculate, simulate many random cases and count. The
share of random points in a square that land inside a quarter circle estimates pi/4; the share of points in a
cube that land in a ball estimates the ball's volume, in any number of dimensions. The answer is only
approximate, but its typical error shrinks like 1/sqrt(N) for N samples, whatever the dimension: four times the
samples, half the error.
The method needs random numbers by the million. Von Neumann's middle-square method makes them by arithmetic:
square a 4-digit number (padding the square to 8 digits) and keep the middle 4 digits, then repeat. The numbers
look random for a while, but each one fixes the next, so the sequence must eventually repeat, often soon, and
some seeds sink to 0000 or stick at a fixed point.
```

## What the program does

```text
1. Runs the 4-digit middle-square method from all 10,000 seeds and lists every cycle it falls into.
2. Estimates pi from random points and measures how the error shrinks with the number of points.
3. Estimates the volume of the unit ball in 2, 5 and 10 dimensions, against the exact formula.
4. Estimates pi with middle-square numbers instead of good ones, and shows what goes wrong.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MonteCarlo.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method) — Wikipedia | The idea, its history at Los Alamos, and its accuracy |
| Start | [Middle-square method](https://en.wikipedia.org/wiki/Middle-square_method) — Wikipedia | Von Neumann's generator, its short cycles, and the "state of sin" |
| Deeper | [The Beginning of the Monte Carlo Method](https://mcnpx.lanl.gov/pdf_files/Article_1987_LAS_Metropolis_125--130.pdf) — N. Metropolis, *Los Alamos Science*, Special Issue 1987, 125–130 | A participant's account: ENIAC, the name, the first calculations |
| Deeper | [Ulam, von Neumann and the Monte Carlo method](https://mcnp-green.lanl.gov/pdf_files/Article_1987_LAS_Eckhardt_131--141.pdf) — Roger Eckhardt, *Los Alamos Science*, Special Issue 1987, 131–141 (the extracted title reads "Monte Carlo and the Monte Carlo Method") | Ulam's solitaire question and von Neumann's letter of 1947, quoted |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
