# AVL Trees: the program

*Era 5 · topic 11 · 1962* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/11-avl-trees/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/11-avl-trees/avl-trees.html) · [All era 5 programs](../README.md)

## How it works

```text
A binary search tree keeps each key with a left branch of smaller keys and a right branch of larger ones, so a
search goes down one path. If keys arrive in sorted order, every new key hangs off the last one and the "tree"
is a list: searching takes as many steps as there are keys. Adelson-Velsky and Landis keep, at every node, the
heights of its two branches within one of each other. After an insertion, walk back up; at the first node where
the difference has become two, turn the branches round (a single rotation, or a double one when the new key went
into the inner grandchild). A rotation changes three links, keeps the keys in order, and restores the height the
subtree had before the insertion. The thinnest tree of height h that obeys the rule has F(h+2) - 1 nodes (F the
Fibonacci numbers), so the height can never exceed about 1.44 log2 n.
```

## What the program does

```text
1. The keys 1 to 7 inserted in order, with the rotations they cause.
2. A plain search tree against an AVL tree, for sorted and for random keys: heights and average search length.
3. After every one of 1,000,000 random insertions: the order of the keys and the balance rule checked at the
   nodes touched; rotations counted.
4. Fibonacci trees, the thinnest AVL trees: their sizes, and the height bound checked against them.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AvlTrees.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [AVL tree](https://en.wikipedia.org/wiki/AVL_tree) — Wikipedia | The balance rule, rotations and the Fibonacci bound |
| Deeper | [Georgy Adelson-Velsky](https://en.wikipedia.org/wiki/Georgy_Adelson-Velsky) — Wikipedia | The inventor, and his chess programs |
| Scholar | [An algorithm for organization of information](https://mathnet.ru/eng/dan26964) — G. M. Adel'son-Vel'skii and E. M. Landis, *Dokl. Akad. Nauk SSSR* 146(2): 263–266 (1962), Math-Net.Ru record | The four-page paper, in Russian |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
