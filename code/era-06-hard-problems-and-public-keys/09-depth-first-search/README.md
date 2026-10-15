# Depth-First Search: the program

*Era 6 · topic 9 · 1970–1974* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/09-depth-first-search/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/09-depth-first-search/depth-first-search.html) · [All era 6 programs](../README.md)

## How it works

```text
Depth-first search explores a graph the way one explores a maze with a ball of thread: go along an unexplored
edge whenever there is one, and back up only when everything from here has been seen. Numbering the vertices in
the order they are reached, the edges used to arrive form a tree; every other edge of an undirected graph leads
from a vertex back to one of its ancestors (Tarjan called these "fronds"). Each edge is examined a fixed number of
times, so the whole search takes time proportional to V + E.
Tarjan and Hopcroft saw that one extra number per vertex answers questions that had seemed to need much more work.
The "lowpoint" of v is the smallest number reachable from v by going down the tree and then along at most one
frond. A vertex u (not the root) is a cut vertex, whose removal disconnects the graph, exactly when it has a
child v with lowpoint(v) >= number(u). In a directed graph the same idea (LOWLINK) finds the strongly connected
components: the largest groups in which every vertex can reach every other.
```

## What the program does

```text
1. A small undirected graph: the search order, tree edges and fronds, lowpoints, cut vertices, and the
   biconnected components.
2. A small directed graph: its strongly connected components by Tarjan's method.
3. 2,000 random graphs: cut vertices and strong components against slow methods that remove each vertex or test
   every pair for reachability.
4. Graphs from 1,000 to 1,000,000 vertices: the work counted, against V + E, and against the slow method.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java DepthFirst.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search) — Wikipedia | The search, its orders, and its uses |
| Start | [Robert Tarjan](https://en.wikipedia.org/wiki/Robert_Tarjan) — Wikipedia | The many algorithms of one designer |
| Deeper | [Algorithm Design (Turing Award lecture)](https://www.cs.williams.edu/~heeringa/classes/cs256/s07/tarjan-turing.pdf) — R. E. Tarjan, *Communications of the ACM* (1987) | How planarity led him and Hopcroft to depth-first search, in his own words |
| Deeper | [Trémaux tree](https://en.wikipedia.org/wiki/Tr%C3%A9maux_tree) — Wikipedia | The maze-solver's tree, and why every depth-first search builds one |
| Scholar | [Depth-First Search and Linear Graph Algorithms](https://www.cs.cmu.edu/~cdm/resources/Tarjan1972-sccs.pdf) — R. Tarjan, *SIAM Journal on Computing* 1(2) (1972), on a Carnegie Mellon page | Strong components and biconnected components in linear time |
| Scholar | [Efficient planarity testing (bibliographic entry)](https://projects.csail.mit.edu/jacm/References/hopcroftt1974:549.html) — J. Hopcroft and R. Tarjan, *Journal of the ACM* 21(4): 549–568 (1974) | The first linear-time planarity test; the text was not opened |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
