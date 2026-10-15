# A*: Search Guided by an Estimate: the program

*Era 6 · topic 4 · 1968* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/04-a-star/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/04-a-star/a-star.html) · [All era 6 programs](../README.md)

## How it works

```text
Dijkstra's method (Era 5) finds the shortest path by growing a circle of settled places around the start, nearest
first, in every direction at once. A robot that knows roughly where the goal lies wastes most of that work.
The Graph Traverser went the other way: always step from the place that looks closest to the goal. It is fast,
but a wall in the way can lead it into a dead end and out again, and the path it returns may be long.
A* takes the next place n with the smallest
    f(n) = g(n) + h(n),
where g(n) is the length of the best path found so far from the start to n, and h(n) is an estimate of what
remains. If h never overestimates (it is "admissible"), the first time the goal is taken its path is a shortest
one. If also h(m) <= cost(m, n) + h(n) for every step from m to n (it is "consistent"), no place ever needs to be
taken twice. With h = 0 it is Dijkstra's method; with a perfect h it walks straight along a shortest path.
```

## What the program does

```text
1. A small map with a cup-shaped wall: Dijkstra, the greedy Graph Traverser and A*, drawn.
2. A 400 x 400 map with a quarter of its squares walled: no estimate, two admissible estimates, a perfect one.
3. 2,000 random maps: A* always finds a shortest path, the greedy method often does not.
4. Weighted A* (f = g + w h): fewer places taken, paths never more than w times too long.
5. An estimate that is admissible but not consistent: A* that never reopens a place goes wrong; with reopening
   it is right again.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AStar.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [A* Search](https://cacm.acm.org/opinion/a-search) — Communications of the ACM | How the name came about, as Raphael told it |
| Start | [A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) — Wikipedia | Admissibility, consistency, and the 1972 correction that was wrong |
| Deeper | [Shakey: The World's First Mobile, Intelligent Robot, 1972](https://ieeemilestones.ethw.org/Milestones:Shakey:_The_World%E2%80%99s_First_Mobile,_Intelligent_Robot,_1972) — Engineering and Technology History Wiki | The robot that needed A*, and what else came out of it |
| Scholar | [A Formal Basis for the Heuristic Determination of Minimum Cost Paths](https://people.stfx.ca/jdelamer/courses/csci-564/_downloads/b2220c66675ddde471ca1795147b8e86/A_Formal_Basis_for_the_Heuristic_Determination_of_Minimum_Cost_Paths.pdf) — P. E. Hart, N. J. Nilsson and B. Raphael, *IEEE Trans. Systems Science and Cybernetics* (1968), scan on a course page | The eight-page paper with the theorems |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
