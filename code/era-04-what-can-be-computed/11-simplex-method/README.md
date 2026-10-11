# The Simplex Method: the program

*Era 4 · topic 11 · 1947* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/11-simplex-method/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/11-simplex-method/simplex-method.html) · [All era 4 programs](../README.md)

## How it works

```text
A linear program asks for numbers x1, ..., xn that make a linear quantity c.x as large as possible, subject to
linear limits A x <= b and x >= 0. The limits cut out a many-sided solid, and if there is a best plan, one sits at
a corner. There are far too many corners to try them all, so the simplex method walks: start at a corner (here,
all x = 0), look for a neighbouring corner that is better, move there, and stop when no neighbour is better. In
table form each move is a "pivot": one variable enters the plan, one leaves, and the table is rewritten by
elimination. Dantzig's rule picks the entering variable with the largest gain per unit; Bland's rule
picks the first that gains at all, and can never cycle (go round a loop of corners for ever).
Every linear program has a dual, a second program whose best value is the same (von Neumann's duality, 1947);
the final table hands over the dual's solution for free, and it certifies the answer.
```

## What the program does

```text
1. A simplex method in exact fractions, with Dantzig's and Bland's rules.
2. A small production plan solved corner by corner.
3. 2,000 random small programs: the simplex answer against every corner, and the dual's value against it.
4. How many pivots random programs need as they grow, against the number of constraints.
5. The Klee-Minty cubes (1972), on which Dantzig's rule visits every one of the 2^n corners.
6. Assigning 10 people to 10 jobs: the simplex answer against all 10! assignments; and 70!, Dantzig's example.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java SimplexMethod.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Simplex algorithm](https://en.wikipedia.org/wiki/Simplex_algorithm) — Wikipedia | Pivoting, the name, cycling and the Klee–Minty worst case |
| Start | [Linear programming](https://en.wikipedia.org/wiki/Linear_programming) — Wikipedia | Kantorovich, Koopmans, Dantzig and von Neumann's duality, and what came after |
| Start | [Stigler diet](https://en.wikipedia.org/wiki/Stigler_diet) — Wikipedia | The diet problem that was the method's first large test |
| Deeper | [George B. Dantzig, a Biographical Memoir](https://www.nasonline.org/wp-content/uploads/2024/06/dantzig-george-b.pdf) — Richard W. Cottle, National Academy of Sciences (2024) | Dantzig's life, from Neyman's unsolved problems to the Air Force |
| Scholar | [Origins of the Simplex Method](https://apps.dtic.mil/sti/pdfs/ADA182708.pdf) — George B. Dantzig, Technical Report SOL 87-5, Systems Optimization Laboratory, Stanford University (May 1987), via DTIC | Dantzig's own account of 1947: the Pentagon, von Neumann, column geometry and the diet problem |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
