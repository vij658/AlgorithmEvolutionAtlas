# B-Trees: the program

*Era 6 · topic 7 · 1969–1972* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/07-b-trees/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/07-b-trees/b-trees.html) · [All era 6 programs](../README.md)

## How it works

```text
A balanced binary tree (Era 5, topic 11) finds one key among a million in about 20 steps. In memory that is
nothing; but an index too big for memory lives on a disk, each step can mean a separate read of the disk, and a
disk read costs as much as a great many steps in memory. Bayer and McCreight made each node a whole "page" of the
disk, holding between k and 2k keys in order, with a child between each pair. One read brings in a whole page,
and a search descends through only a few pages.
Insertion adds the key to its leaf page. If the page then holds 2k + 1 keys, it splits: the middle key moves up
into the parent, and the two halves of k keys each become pages. A split can climb to the root; when the root
splits, the tree grows a new root, so every leaf always stays at the same depth.
Deletion is the mirror image: a page left with fewer than k keys borrows one from a neighbour through the parent,
or, if the neighbour has only k, merges with it, pulling the separating key down.
```

## What the program does

```text
1. A small tree (k = 2: pages of 2 to 4 keys), built key by key, every split shown.
2. A million random keys in trees with pages of 4, 20, 100 and 400 keys: height and pages read per search,
   against a balanced binary tree.
3. How full the pages are, keys inserted in random order and in sorted order.
4. Half the keys deleted: the rules still hold everywhere, and every search is still right.
5. The height of every tree built, against the bounds that the rules imply.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java BTrees.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [B-tree](https://en.wikipedia.org/wiki/B-tree) — Wikipedia | The structure, its variants, and the mystery of the B |
| Deeper | [Memoiren](https://db.cit.tum.de/~bayer/Memoiren-Bayer.pdf) — Rudolf Bayer, Technical University of Munich (in German) | The inventor's own account of Boeing and the B-tree |
| Deeper | [Edward M. McCreight](https://en.wikipedia.org/wiki/Edward_M._McCreight) — Wikipedia | The co-inventor, who went on to the Xerox Alto |
| Scholar | [Organization and Maintenance of Large Ordered Indexes (bibliographic entry)](https://glossar.hs-augsburg.de/Bayer,_McCreight_(1972) — R. Bayer and E. McCreight, *Acta Informatica* 1(3): 173–189 (1972) | The paper; no openable copy of the text was found |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
