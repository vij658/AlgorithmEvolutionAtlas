# Splay Trees and Amortized Analysis: the program

*Era 7 · topic 5 · 1985* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/05-splay-trees/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/05-splay-trees/splay-trees.html) · [All era 7 programs](../README.md)

## How it works

```text
A binary search tree finds a key by walking down from the root, left if smaller, right if larger. Balanced trees
(Era 5) keep every path short by storing extra information and following rules after each change. A splay tree
stores nothing extra. Instead, every time a key is touched, it is "splayed": rotated up to the root, two levels
at a time (the zig-zig and zig-zag steps), which also roughly halves the depth of every node on the way. One
access can still be slow, but Sleator and Tarjan proved that any sequence of m accesses takes O(m log n) in all:
the cost is "amortized", averaged over the worst possible sequence. The proof gives the tree a potential, the sum
of log2(size of each subtree): a slow access always lowers the potential, which pays for it. Frequently used
keys stay near the root, so on skewed workloads a splay tree is as good as the best fixed tree for those
frequencies, without knowing them.
```

## What the program does

```text
1. The access lemma, checked on every one of 1,000,000 splays: rotations + change in potential
   <= 3 (log2 n - log2 size(x)) + 1.
2. Keys inserted in sorted order and then read in order: a plain search tree, a splay tree, a balanced tree.
3. Skewed (Zipf) accesses: the splay tree against a perfectly balanced tree and the optimal fixed tree for the
   true frequencies (Knuth's dynamic programme, 1971).
4. Working sets: repeatedly using a few keys out of 100,000 costs about log2 of the few, not of 100,000.
5. Tarjan's simplest example of amortization: a stack where one operation may pop many items.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java SplayTrees.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Splay tree](https://en.wikipedia.org/wiki/Splay_tree) — Wikipedia | The zig, zig-zig and zig-zag steps with pictures, and the trade-offs |
| Deeper | [Lecture 3: Splay Trees](https://courses.csail.mit.edu/6.854/21/Notes/n03-splay.html) — D. Karger, MIT 6.854 *Advanced Algorithms* | The potential-function proof, step by step |
| Scholar | [Self-Adjusting Binary Search Trees](https://www.cs.princeton.edu/courses/archive/fall07/cos521/handouts/self-adjusting.pdf) — D. Sleator, R. Tarjan, *JACM* (1985), on a Princeton course page | Splaying, the access lemma and the conjectures |
| Scholar | [Amortized Computational Complexity](https://courses.cs.duke.edu/fall11/cps234/reading/Tarjan85_AmortizedComplexity.pdf) — R. Tarjan, *SIAM J. Alg. Disc. Meth.* (1985), on a Duke course page | The banker's and physicist's views of amortization |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
