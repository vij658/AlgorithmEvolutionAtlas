# Heapsort and the Heap: the program

*Era 5 · topic 12 · 1964* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/12-heapsort/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/12-heapsort/heapsort.html) · [All era 5 programs](../README.md)

## How it works

```text
A heap is a list read as a tree: the item at position i (counting from 0) has its children at 2i+1 and 2i+2,
and every item is at least as large as its children, so the largest is at the front. To add an item, put it at
the end and let it climb past smaller parents (Williams). To remove the largest, move the last item to the front
and let it sink below larger children. Heapsort builds a heap from the list, then repeatedly swaps the front
(largest) item with the last item of the heap and lets the new front sink: the sorted list grows at the back,
inside the same array. Floyd built the heap faster: treat each of the lower half of the positions, from the back,
as the root of a small heap and let it sink; most items sink only a level or two, so building takes fewer than
2n comparisons. Sorting then takes about 2 n log2 n comparisons, whatever the input.
```

## What the program does

```text
1. A heap built from ten numbers, as an array and as a tree.
2. Building a heap by Williams's insertions and by Floyd's sinking: comparisons, and the exact worst case of
   Floyd's method over every ordering of up to 10 items against 2n - 2s(n) - e(n).
3. Heapsort on random and on sorted lists up to a million items: comparisons against 2 n log2 n, with no extra list.
4. Equal keys: heapsort does not keep their original order.
5. The heap as a priority queue: Dijkstra's shortest paths (topic 7) with set B kept in a heap.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Heapsort.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Heapsort](https://en.wikipedia.org/wiki/Heapsort) — Wikipedia | Williams's method, Floyd's improvement and the comparison counts |
| Start | [Heap (data structure)](https://en.wikipedia.org/wiki/Heap_(data_structure) — Wikipedia | The heap as a priority queue, and its uses beyond sorting |
| Deeper | [J. W. J. Williams](https://en.wikipedia.org/wiki/J._W._J._Williams) — Wikipedia | The inventor's career in England and Canada |
| Scholar | [Algorithm 232 - Heapsort](https://hjemmesider.diku.dk/~henglein/bib/publications/williams1964.html) — J. W. J. Williams, *CACM* 7(6): 347–348 (1964), bibliographic record | The citation of the original algorithm |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
