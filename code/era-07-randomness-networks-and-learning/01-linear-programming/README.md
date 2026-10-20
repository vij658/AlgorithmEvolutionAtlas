# Linear Programming in Polynomial Time: the program

*Era 7 · topic 1 · 1979–1984* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/01-linear-programming/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/01-linear-programming/linear-programming.html) · [All era 7 programs](../README.md)

## How it works

```text
A linear program asks for the largest value of c.x over the points x that satisfy linear inequalities A x <= b.
Those points form a polytope, and the best value is reached at a corner. The simplex method (Era 4) walks from
corner to better corner along the edges. Usually it needs few steps; but Klee and Minty built a squashed cube in
n dimensions on which the usual rule (enter the variable with the largest coefficient) visits all 2^n corners.
Khachiyan's ellipsoid method encloses the feasible region in an ellipsoid. If the ellipsoid's centre breaks a
constraint, that constraint cuts the ellipsoid in half, and a smaller ellipsoid is drawn around the good half.
The volume shrinks by a fixed factor each time, so a feasible point is found in a polynomial number of steps.
Interior-point methods (Karmarkar 1984) move through the inside of the polytope instead of along its edges. The
kind used here, primal-dual path-following, solves the program and its dual together: at the optimum every
variable times its matching dual slack is zero, so each step is a Newton step towards points where all those
products are equal and a little smaller, stopping just short of the walls. The number of steps hardly grows
with the size of the problem.
```

## What the program does

```text
1. The simplex method with Dantzig's rule on Klee and Minty's cube, n = 1 ... 14: pivots counted, 2^n - 1.
2. A primal-dual interior-point method (Mehrotra's predictor-corrector) on the same cubes: iterations
   counted, the same optimum.
3. Random linear programs of 10 to 160 variables: simplex pivots and interior-point iterations.
4. The ellipsoid method in two dimensions: steps to find a point in smaller and smaller triangles, against
   the volume bound.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LinearProgramming.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Leonid Khachiyan, 1952–2005: An Appreciation](https://sites.oxy.edu/lengyel/M372/papers/SIAM%20Leonid%20Khachiyan,%201952%962005%20An%20Appreciation.htm) — SIAM News (2005) | The four-page note, the headlines, and what the method did and did not change |
| Start | [Klee–Minty cube](https://en.wikipedia.org/wiki/Klee%E2%80%93Minty_cube) — Wikipedia | The cube on which the simplex method visits every corner |
| Deeper | [Ellipsoid method](https://en.wikipedia.org/wiki/Ellipsoid_method) — Wikipedia | How cutting ellipsoids in half finds a feasible point |
| Deeper | [Karmarkar's algorithm](https://en.wikipedia.org/wiki/Karmarkar%27s_algorithm) — Wikipedia | Interior points, the patent, and affine scaling |
| Deeper | [Interior-Point Methods](https://neos-guide.org/guide/algorithms/ipm) — NEOS Guide | Primal-dual path-following and Mehrotra's predictor-corrector, as in this topic's program |
| Deeper | [Interior-point method](https://en.wikipedia.org/wiki/Interior-point_method) — Wikipedia | Dikin, Karmarkar, and why primal-dual methods won |
| Scholar | [A New Polynomial-Time Algorithm for Linear Programming](https://users.cs.utah.edu/~tch/notes/PSSAT/EAGER/Ishaan/A_New_Polynomial-Time_Algorithm_for_Linear_Program.pdf) — N. Karmarkar, *Combinatorica* (1984), on a University of Utah page | The projective method and its bound |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
