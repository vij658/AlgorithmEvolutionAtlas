# Hoare's Quicksort: the program

*Era 5 · topic 10 · 1959–1962* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/10-quicksort/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/10-quicksort/quicksort.html) · [All era 5 programs](../README.md)

## How it works

```text
Pick one item, the bound (today: the pivot). Partition: a finger starts at each end of the list and moves inward,
the left finger stopping at an item that is not smaller than the bound, the right finger at one that is not
larger; swap the two items and go on until the fingers meet. Now everything on the left is no larger than
everything on the right. Sort the two parts the same way. On random data each partition splits the list roughly
in half, so the work grows like n log n: about 2 n ln n = 1.39 n log2 n comparisons when every other item is
compared with the bound once and the bound is then set aside. If the bound is always the smallest item (a
sorted list and the first item as the bound), each partition peels off one item and the work is about n^2 / 2.
Choosing the bound at random makes that bad luck vanishingly rare.
```

## What the program does

```text
1. The words of one of Hoare's own sentences about Moscow, sorted, with the first partition shown.
2. Every ordering of 1 to 9 items: the average number of comparisons, exactly, against 2(n+1)H_n - 4n.
3. Random lists from 1,000 to a million items: comparisons against 1.39 n log2 n and the lower bound log2 n!.
4. Insertion sort, Hoare's first idea, on the same lists while it is still feasible.
5. Sorted input: the first item as the bound, against a bound chosen at random.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Quicksort.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Quicksort](https://en.wikipedia.org/wiki/Quicksort) — Wikipedia | Moscow, Mercury Autocode, the sixpence, and the analysis |
| Start | [In Memoriam: Sir Antony Hoare (1934–2026)](https://computerhistory.org/blog/in-memoriam-sir-antony-hoare-1934-2026/) — Dag Spicer, Computer History Museum (2026) | His life and work, from Quicksort to the null reference |
| Deeper | [An Interview With C.A.R. Hoare](https://cacm.acm.org/?p=20664) — Jonathan P. Bowen (2006), edited for *Communications of the ACM* | Quicksort in Hoare's own words |
| Deeper | [Tony Hoare](https://www.cs.ox.ac.uk/people/tony.hoare) — University of Oxford, Department of Computer Science | Career outline |
| Deeper | [Wolfson Emeritus Fellow Professor Sir Tony Hoare dies](https://www.wolfson.ox.ac.uk/news/wolfson-emeritus-fellow-professor-sir-tony-hoare-dies/) — Wolfson College, Oxford (16 March 2026) | The college's notice |
| Scholar | [Quicksort](https://www.cs.ox.ac.uk/publications/publication8195-abstract.html) — C. A. R. Hoare, *The Computer Journal* 5(1): 10–15 (1962), Oxford publication record | The paper with the analysis |
| Scholar | [Oral history of Sir Antony Hoare](https://www.computerhistory.org/collections/catalog/102658017) — Interview by Jonathan P. Bowen, 8 September 2006, Computer History Museum | The recorded interview behind the CACM excerpt |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
