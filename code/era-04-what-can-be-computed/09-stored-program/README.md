# The Stored Program, and Merge Sort: the program

*Era 4 · topic 9 · 1945–1948* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/09-stored-program/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/09-stored-program/stored-program.html) · [All era 4 programs](../README.md)

## How it works

```text
A stored-program computer keeps its instructions in the same memory as its numbers, as numbers. The Manchester
"Baby" (1948) had 32 words of store and seven instructions; this program uses that instruction set:
    JMP s   jump to the address held in word s        JRP s   jump forward by the number held in word s
    LDN s   load minus the number in word s           STO s   store the accumulator in word s
    SUB s   subtract the number in word s             CMP     skip the next instruction if the accumulator < 0
    STP     stop
Each instruction is a word: a function number (0 to 7) times 8192, plus an address. Because instructions are
numbers, a program can do arithmetic on them: adding 1 to "LDN 100" makes it "LDN 101". The first programs
stepped through lists that way, since there were no index registers.
Merging takes two sorted lists and repeatedly moves the smaller front item to the output. Merge sort merges
runs of length 1 into runs of 2, then 4, and so on: about n log2 n comparisons for n items.
```

## What the program does

```text
1. A simulator for the seven instructions, with a small assembler.
2. A 16-instruction program, written for the Baby's instructions and 32-word store, that finds the highest proper
   factor of 2^18 by repeated subtraction, the task of the Baby's first program (21 June 1948).
3. A merging program that rewrites the addresses inside its own instructions, run on a larger store.
4. Merge sort's worst case for every permutation of up to 8 items, against the formula and the lower bound.
5. Merge sort against insertion sort on up to a million items.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java StoredProgram.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [First Draft of a Report on the EDVAC](https://en.wikipedia.org/wiki/First_Draft_of_a_Report_on_the_EDVAC) — Wikipedia | The stored-program design, its distribution, and the dispute over credit |
| Start | [Manchester Baby](https://en.wikipedia.org/wiki/Manchester_Baby) — Wikipedia | The first stored program to run, and the seven instructions it used |
| Start | [Merge sort](https://en.wikipedia.org/wiki/Merge_sort) — Wikipedia | The algorithm, its analysis and its variants |
| Scholar | [Von Neumann's First Computer Program](https://fermatslibrary.com/s/von-neumanns-first-computer-program) — Donald E. Knuth, *Computing Surveys* 2(4):247–260 (December 1970), annotated on Fermat's Library | The 1945 merging program, read line by line |
| Scholar | [First Draft of a Report on the EDVAC](https://cs.carleton.edu/faculty/jondich/courses/cs207_f03/assignments/edvac.pdf) — John von Neumann (30 June 1945), reprinted from Laplante (ed.), *Great Papers in Computer Science*, on a Carleton College course page | The five organs, and orders stored as numbers |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
