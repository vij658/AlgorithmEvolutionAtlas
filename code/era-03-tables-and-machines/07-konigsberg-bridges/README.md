# The Bridges of Königsberg: the program

*Era 3 · topic 7 · 1736* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/07-konigsberg-bridges/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/07-konigsberg-bridges/konigsberg-bridges.html) · [All era 3 programs](../README.md)

## How it works

```text
Forget distances and shapes; keep only which piece of land each bridge joins. A walker who enters a piece of land
by one bridge must leave it by another, so the bridges at every piece of land are used in pairs, except where the
walk starts and where it ends. So a walk crossing every bridge exactly once is possible only if zero or two pieces
of land have an odd number of bridges (Euler). Conversely, if the land is connected and zero or two pieces are odd,
such a walk exists (Hierholzer): walk until you are stuck, which can only happen at the end; then, from any place on
the walk that still has unused bridges, walk a closed loop and splice it in; repeat.
```

## What the program does

```text
1. Builds Königsberg: four pieces of land A (the island), B, C, D and seven bridges, and counts bridges per piece.
2. Repeats Euler's own count: how often each letter must appear in a route, against the letters a route can have.
3. Searches every walk that never repeats a bridge, to confirm that none crosses all seven.
4. Adds an eighth bridge, finds the route with Hierholzer's splicing, and checks it.
5. Tests Euler's condition against exhaustive search on 20,000 random multigraphs, and times Hierholzer against
   search.
6. Full circle: a de Bruijn sequence (every 4-digit binary code exactly once) as a route through a graph.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java KonigsbergBridges.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Seven Bridges of Königsberg](https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg) — Wikipedia | The puzzle, Euler's answer, and what became of the bridges |
| Start | [Leonard Euler's Solution to the Konigsberg Bridge Problem](https://www.maa.org/book/export/html/116599) — Teo Paoletti, MAA *Convergence* | Euler's letters, and why he thought the problem trivial |
| Deeper | [Euler tours](https://www.ics.uci.edu/~eppstein/163/lecture4b.pdf) — David Eppstein, CS 163/265 Graph Algorithms, UC Irvine (Winter 2026) | Euler's condition, Hierholzer's splicing algorithm and its linear running time |
| Deeper | [Das Problem der Königsberger Brücken](https://bez.unibas.ch/fileadmin/user_upload/bez/Koenigsberg.pdf) — Hanspeter Kraft, University of Basel (in German), with Hopkins and Wilson's "The Truth about Königsberg" (2004) reprinted | What Euler actually did, in his own counting, without a graph |
| Scholar | [An Historical Note: Euler's Königsberg Letters](https://www.ime.usp.br/~yw/2016/grafinhos/aulas/Paper-Euler-Letters.pdf) — Horst Sachs, Michael Stiebitz and Robin J. Wilson, *Journal of Graph Theory* 12(1):133–139 (1988) | The letters of 1736 and the publication dates |
| Scholar | [Solutio problematis ad geometriam situs pertinentis (E53)](https://phantom.cs.qc.cuny.edu/gavva/teaching/s24/euler-bridges-paper.pdf) — Euler, 1736 (printed 1741); Euler Archive copy on a Queens College course page | The paper itself, in Latin |
| Scholar | [Ueber die Möglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren](https://eudml.org/doc/156599) — Carl Hierholzer, *Mathematische Annalen* 6:30–32 (1873), EuDML record with a link to the Göttingen scan | The proof of sufficiency, and the construction |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
