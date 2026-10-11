# Turing's Machines: the program

*Era 4 · topic 7 · 1936* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/07-turing-machines/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/07-turing-machines/turing-machines.html) · [All era 4 programs](../README.md)

## How it works

```text
A Turing machine has a tape of squares, a head that scans one square, and a finite table. Each line of the table
says: in this state (Turing's "m-configuration"), reading this symbol, write a symbol, move one square left or
right (or stay), and go to that state. That is all, and Turing argued that it is all a person computing with
pencil and paper needs. Because the table is finite, it can be written out as a string of letters (Turing's
"standard description") and then as a number (its "description number"). A universal machine reads such a
number from its tape and does what the described machine would do: the program is data. The price is that no
machine can take any description and decide whether that machine will run properly for ever or not; today the
question is usually put as whether it halts.
```

## What the program does

```text
1. Runs the first example of Turing's paper, which prints 0 1 0 1 ... on every other square.
2. Writes its standard description and description number by Turing's rules, and checks them against the
   number printed in 1936; decodes the number back into a table and runs that (a universal machine in miniature).
3. Does the same for the two-state example on Wikipedia's "Description number" page.
4. Runs every machine with two states and two symbols from a blank tape: those that halt do so within 6 steps.
5. Runs Marxen and Buntrock's five-state machine (1989), proved the five-state "busy beaver" in 2024: it halts
   after 47,176,870 steps. A test that simply waits 10 million steps would call it a machine that never halts.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java TuringMachines.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Turing 2018/3: "On Computable Numbers" – Turing's 1936 Paper](https://podcasts.ox.ac.uk/turing-20183-computable-numbers-turings-1936-paper) — Peter Millican, University of Oxford, series *Alan Turing on Computability and Intelligence* (video, with transcript) | A walk through the paper: the human computer, the machines and their tables |
| Start | [Turing machine](https://en.wikipedia.org/wiki/Turing_machine) — Wikipedia | Tape, head, table, the universal machine, and the human "computer" Turing modelled |
| Start | [Alan Mathison Turing](https://mathshistory.st-andrews.ac.uk/Biographies/Turing/) — MacTutor | Newman's course, the paper, Princeton, and Bletchley Park |
| Start | [Halting problem](https://en.wikipedia.org/wiki/Halting_problem) — Wikipedia | The diagonal proof, and who named the problem |
| Deeper | [Turing 2018/4: Enumerating the Computable Numbers, and the Universal Turing Machine](https://www.podcasts.ox.ac.uk/turing-20184-enumerating-computable-numbers-and-universal-turing-machine?video=1) — Peter Millican, University of Oxford (video) | Description numbers, the universal machine and the diagonal argument |
| Deeper | [Description number](https://en.wikipedia.org/wiki/Description_number) — Wikipedia | How a machine becomes a number |
| Deeper | [Busy beaver](https://en.wikipedia.org/wiki/Busy_beaver) — Wikipedia | Radó's function, the five-state champion, and its proof in 2024 |
| Scholar | [On Computable Numbers, with an Application to the Entscheidungsproblem](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) — A. M. Turing, *Proceedings of the London Mathematical Society* (2) 42:230–265 (1936–37), scan on a University of Virginia page | The paper |
| Scholar | [On Computable Numbers (transcription)](https://verostko.com/turing/1936-paper.html) — Transcription by abelard.org, reproduced with permission of the London Mathematical Society | A searchable text with the example tables and description numbers |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
