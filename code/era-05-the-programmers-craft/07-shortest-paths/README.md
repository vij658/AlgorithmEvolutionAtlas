# Dijkstra's Shortest Paths: the program

*Era 5 · topic 7 · 1956–1959* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/07-shortest-paths/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/07-shortest-paths/shortest-paths.html) · [All era 5 programs](../README.md)

## How it works

```text
To find the shortest route from P to every other town, Dijkstra splits the towns into three sets. A: towns whose
shortest distance from P is known. B: towns reached by some road from A, with the best distance found so far.
C: the rest. Start with P alone in A. Repeat: move the town of B with the smallest distance into A (no route can
later beat it, because every other route has to leave A through a town that is already at least as far); then
look along the roads out of that town and improve the distances of its neighbours, moving them from C into B
if they were not there yet. When Q enters A, its distance is final. Road lengths must not be negative.
The same paper solves a second problem: the shortest network joining all towns (grow a tree from one town, always
adding the shortest road to a town not yet in it).
```

## What the program does

```text
1. A map of 64 invented towns (Dijkstra's ARMAC demonstration used 64 Dutch cities), roads to near neighbours;
   the shortest route between two corners, with the sets A, B, C after the first few steps.
2. Dijkstra's method against Ford's method (improve every road again and again until nothing changes) on 2,000
   random maps: the same distances, and the work each needed.
3. How large set B gets, against the number of roads (the paper's point about storage).
4. A road of negative length, where the method's argument fails.
5. The shortest network joining all 64 towns, by Dijkstra's first method and by Kruskal's, the same length.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ShortestPaths.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [An Interview With Edsger W. Dijkstra](https://cacm.acm.org/?p=31927) — Philip L. Frana (2001), *Communications of the ACM* | The café, the twenty minutes, and why it waited three years |
| Start | [The Simple, Elegant Algorithm That Makes Google Maps Possible](https://www.vice.com/en/article/4x3pp9/the-simple-elegant-algorithm-that-makes-google-maps-possible) — Michael Byrne, Vice (2015) | The ARMAC demonstration and the 64 cities |
| Start | [Routes: Edsger Dijkstra](https://chalkdustmagazine.com/biographies/routes-edsger-dijkstra/) — Emma Bell, *Chalkdust* (2018) | A short biography for students |
| Deeper | [Edsger W. Dijkstra](https://amturing.acm.org/award_winners/dijkstra_1053701) — ACM Turing Award | The ARMAC program, the X1 wiring problem and his later work |
| Deeper | [Edsger W. Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra) — Wikipedia | Life and work, from the Mathematical Centre to Austin |
| Scholar | [A note on two problems in connexion with graphs](https://isidore.co/misc/Physics%20papers%20and%20books/Zotero/storage/RQ5SZPTE/Dijkstra%20-%201959%20-%20A%20note%20on%20two%20problems%20in%20connexion%20with%20graphs.pdf) — E. W. Dijkstra, *Numerische Mathematik* 1: 269–271 (1959), scan | The three-page paper: the tree, the path, and the sets A, B, C |
| Scholar | [A note on two problems in connexion with graphs](https://ir.cwi.nl/pub/9256) — CWI repository record, with the full text | The paper at the institute where Dijkstra worked |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
