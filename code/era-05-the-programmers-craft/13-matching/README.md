# Edmonds's Matching: the program

*Era 5 · topic 13 · 1965* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/13-matching/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/13-matching/matching.html) · [All era 5 programs](../README.md)

## How it works

```text
A matching pairs up vertices of a graph along its edges, each vertex in at most one pair. Berge (1957): a matching
is as large as possible exactly when there is no augmenting path, a path that starts and ends at unpaired
vertices and alternates between edges outside and inside the matching; swapping the edges along such a path adds
one pair. So: search for an augmenting path, swap, repeat. The search grows a tree from an unpaired vertex,
labelling vertices "outer" (an even number of steps from the root) and "inner" (odd). In a graph with odd cycles
the search can label a vertex inner when another way round the cycle would have made it outer, and then miss the
path. Edmonds's remedy: when two outer vertices are joined, they close an odd cycle, a "blossom"; shrink the
whole blossom to a single outer vertex and carry on. Every vertex of the blossom can then be reached as outer.
The work is bounded by a polynomial in the number of vertices; Edmonds called such algorithms "good", against
the obvious method of trying every matching, whose number grows faster than any power.
```

## What the program does

```text
1. An 8-vertex graph with a 5-cycle where the search without blossoms misses the augmenting path, and Edmonds's
   search finds it.
2. Edmonds's algorithm against trying every matching, on 20,000 random graphs of up to 12 vertices.
3. Counting: the number of matchings of a complete graph against the steps of Edmonds's algorithm.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Matching.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Blossom algorithm](https://en.wikipedia.org/wiki/Blossom_algorithm) — Wikipedia | Augmenting paths, blossoms and the running time |
| Start | [Jack Edmonds](https://en.wikipedia.org/wiki/Jack_Edmonds) — Wikipedia | The matching paper, polynomial time and the P versus NP conjectures |
| Start | [Edmonds's Blossom Algorithm](https://algorithms.discrete.ma.tum.de/graph-algorithms/matchings-blossom-algorithm/index_en.html) — Johannes Feil, Technische Universität München (2016) | An interactive applet that runs the algorithm step by step |
| Deeper | [Paths, Trees, and Flowers](https://nvlpubs.nist.gov/nistpubs/sp958-lide/html/140-144.html) — NIST Special Publication 958, essay by Christoph Witzgall and colleagues | Edmonds at the National Bureau of Standards, and why "good" algorithms mattered |
| Deeper | [Cobham's thesis](https://en.wikipedia.org/wiki/Cobham%27s_thesis) — Wikipedia | Polynomial time as the meaning of "feasible" |
| Deeper | [Jack Edmonds](https://www.informs.org/Explore/History-of-O.R.-Excellence/Biographical-Profiles/Edmonds-Jack) — INFORMS biographical profile | His career, matroids and awards |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
