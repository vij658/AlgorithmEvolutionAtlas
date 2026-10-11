# The Cheapest Network: the program

*Era 4 · topic 4 · 1926–1930* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/04-cheapest-network/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/04-cheapest-network/cheapest-network.html) · [All era 4 programs](../README.md)

## How it works

```text
Given towns and the distance between every pair, connect them all with lines of least total length (today: a
minimum spanning tree). One fact does all the work: for any group of towns, the shortest line leaving the group
belongs to the cheapest network (when no two distances are equal). So:
  Borůvka: every town joins its nearest neighbour. That leaves separate pieces; every piece joins the piece
           nearest to it; repeat until one piece remains. Each round at least halves the number of pieces.
  Jarník:  start from one town; repeatedly add the shortest line from the network built so far to a town not
           yet in it.
  Kruskal (1956): take the lines from shortest to longest, keeping each one that joins two separate pieces.
With equal distances, all three need the same tie-breaking rule, or Borůvka's rounds can close a loop.
```

## What the program does

```text
1. Forty towns at random points (like Borůvka's example with 40 cities): Borůvka's rounds, Jarník's growth and
   Kruskal's sort choose exactly the same 39 lines.
2. A thousand more sets of 40 towns: how many rounds Borůvka needs, and a check that every round at least halves
   the number of pieces.
3. Brute force on 200 sets of 7 towns: all 16,807 possible networks each (Cayley's count 7^5); the one the
   algorithms choose is the unique cheapest every time.
4. The rule behind all three, tested on 10,000 random splits of the 40 towns.
5. Three towns at equal distances: without a shared tie-breaking rule, Borůvka's round picks a closed loop.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java CheapestNetwork.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Borůvka's algorithm](https://en.wikipedia.org/wiki/Bor%C5%AFvka%27s_algorithm) — Wikipedia | The rounds, the rediscoveries, and why ties must be broken consistently |
| Start | [Otakar Borůvka](https://mathshistory.st-andrews.ac.uk/Biographies/Boruvka/) — MacTutor | Borůvka's life in Brno and the friend at the power company |
| Start | [Vojtěch Jarník](https://mathshistory.st-andrews.ac.uk/Biographies/Jarnik/) — MacTutor | A number theorist's single, lasting excursion into networks |
| Deeper | [Algorithms for Minimum Spanning Trees](https://courses.grainger.illinois.edu/cs374/fa2020/lec_prerec/20/20_1_0_0.pdf) — CS/ECE 374, University of Illinois (Fall 2020), lecture 20 slides | Borůvka's electricity network and the history before Kruskal and Prim |
| Scholar | [On the History of the Minimum Spanning Tree Problem](https://math.ucdavis.edu/~saito/data/acha.read.w12/graham-hell-mst.pdf) — R. L. Graham and Pavol Hell, *Annals of the History of Computing* 7(1) (1985), on a UC Davis reading list | The standard history: Borůvka, Jarník, Choquet, Florek et al., Kruskal, Prim, Sollin |
| Scholar | [Otakar Borůvka on minimum spanning tree problem: translation of both the 1926 papers, comments, history](https://www.dml.cz/bitstream/handle/10338.dmlcz/500413/Boruvka_03-0000-60_1.pdf) — J. Nešetřil, E. Milková and H. Nešetřilová, *Discrete Mathematics* 233:3–36 (2001), Czech Digital Mathematics Library | Both of Borůvka's papers in English, including the 40-city example |
| Scholar | [Vojtěch Jarník's work in combinatorial optimization](https://www.dml.cz/bitstream/handle/10338.dmlcz/500662/Jarnik_04-0000-19_1.pdf) — B. Korte and J. Nešetřil, *Discrete Mathematics* 235:1–17 (2001), Czech Digital Mathematics Library | Jarník's letter of 1930, in Czech and in English translation |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
