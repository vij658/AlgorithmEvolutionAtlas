# The Barnes–Hut Tree Code: the program

*Era 7 · topic 8 · 1986* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/08-barnes-hut/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/08-barnes-hut/barnes-hut.html) · [All era 7 programs](../README.md)

## How it works

```text
To move N stars under gravity you need the pull of every star on every other: N(N - 1) terms, a billion for
N = 30,000, at every time step. Barnes and Hut put the stars in a tree of cubes: the whole box, split into 8
smaller cubes, each split again, until every cube holds at most one star. Each cube remembers its total mass and
centre of mass. To find the pull on one star, walk down the tree from the top: a cube that looks small from the
star (its width s divided by its distance d is below a chosen angle theta) is treated as one heavy point at its
centre of mass; a cube that looks big is opened and its children are looked at instead. A star then feels about
log N cubes instead of N stars, so a step costs about N log N. Smaller theta opens more cubes: slower, more
accurate; theta = 0 opens everything and gives back the exact sum.
```

## What the program does

```text
1. Builds the tree for a cluster of stars (a Plummer sphere) and checks that theta = 0 gives the exact forces.
2. Counts interactions for N = 1,000 to 100,000 stars: direct sum against the tree.
3. Measures the error of the tree's forces against the exact ones for several values of theta.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java BarnesHut.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Barnes–Hut simulation](https://en.wikipedia.org/wiki/Barnes%E2%80%93Hut_simulation) — Wikipedia | The tree, the opening angle, and the speed–accuracy trade-off |
| Start | [The Barnes-Hut Galaxy Simulator](https://beltoforion.de/en/barnes-hut-galaxy-simulator/) — Ingo Berg | Diagrams, pseudocode, an animation of θ and a video of two colliding galaxies (its remarks on θ are not consistent throughout) |
| Deeper | [Hierarchical Methods for the N-Body problem](https://people.eecs.berkeley.edu/%7Edemmel/cs267_Spr16/Lectures/lecture25_NBody_jwd16_4pp.pdf) — J. Demmel, UC Berkeley CS 267 (2016) | Barnes–Hut beside the fast multipole method, and running both in parallel |
| Scholar | [hackforce manual page](https://bima.astro.umd.edu/nemo/man_html/hackforce.1.html) — NEMO toolkit, J. E. Barnes | A working tree code by one of the inventors, still distributed |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
