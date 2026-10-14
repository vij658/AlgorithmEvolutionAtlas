# Linked Lists and Garbage Collection: the program

*Era 5 · topic 6 · 1956–1960* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/06-linked-lists/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/06-linked-lists/linked-lists.html) · [All era 5 programs](../README.md)

## How it works

```text
A linked list keeps each item in a cell together with the address of the next cell. Items need not sit side by
side in memory, so a new item is spliced in by changing two addresses instead of moving everything after it.
Lisp's cells hold two addresses, the "car" (the item) and the "cdr" (the rest of the list); since the car can be
another list, cells make trees, and a formula such as (PLUS X (TIMES 3 X)) is a tree of cells. The unused cells
are themselves chained into a free list, and every new cell is taken from it.
A program that builds and discards structures leaves cells that nothing points to any more. McCarthy's answer,
when the free list runs out: start from the cells the program can still reach (the roots), mark everything
reachable from them, then sweep through memory and put every unmarked cell back on the free list.
```

## What the program does

```text
1. A memory of two-address cells with a free list.
2. Adding 10,000 items one at a time to the front of a list and of an array: addresses changed against items moved.
3. Reversing a list in place by turning its arrows round.
4. Symbolic differentiation on formulas stored as cells, simplifying as it goes: four derivatives of
   x^4 + 5x, checked by evaluating each one.
5. The same work repeated in a small memory, so that the free list runs out again and again: mark-and-sweep keeps
   the program going, and every answer is still right.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ListsAndGarbage.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Linked list](https://wikipedia.com/wiki/LinkedList) — Wikipedia | The data structure and its history at RAND and MIT |
| Start | [Garbage collection (computer science)](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science) — Wikipedia | Reclaiming unreachable memory, from McCarthy to today |
| Deeper | [Information Processing Language](https://en.wikipedia.org/wiki/Information_Processing_Language) — Wikipedia | The first list-processing language and its free list |
| Deeper | [John McCarthy](https://en.wikipedia.org/wiki/John_McCarthy_(computer_scientist) — Wikipedia | Lisp, garbage collection and the name "artificial intelligence" |
| Deeper | [LISP](https://www.cl.cam.ac.uk/teaching/0708/ConceptsPL/LISP.pdf) — University of Cambridge, Concepts in Programming Languages (2007–08) | Lecture slides on McCarthy's paper, with his remark about the name |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
