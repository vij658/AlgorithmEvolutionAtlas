# Lovelace's Note G: the program

*Era 3 · topic 11 · 1843* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/11-note-g/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/11-note-g/note-g.html) · [All era 3 programs](../README.md)

## How it works

```text
The Analytical Engine was to have a store of numbered columns (variables V1, V2, ...), a mill that does one
arithmetic operation at a time, and punched cards saying which operation to apply to which columns; a set of cards
could be repeated, making a loop. Note G shows how such an engine would compute a Bernoulli number from the ones
before it, using the identity (in Lovelace's numbering, B1 = 1/6, B3 = -1/30, B5 = 1/42, B7 = -1/30):
  0 = A0 + A1 B1 + A3 B3 + ... + B_(2n-1),   A0 = -(1/2)(2n - 1)/(2n + 1),   A1 = 2n/2,
  and each later A is the one before times two more falling factors over two more rising ones.
The middle terms all have the same shape, so one group of operations, repeated, computes them all.
```

## What the program does

```text
1. Runs a 25-operation program in the style of Note G (store, mill, a repeated group) for Lovelace's B7, in exact
   fractions, and counts the operations executed. It is a reconstruction: the table itself could not be read in an
   opened copy, so the operation numbers here are this program's own.
2. Checks the program's B1 to B19 (Lovelace's numbering) against the standard recurrence.
3. Runs it with the division of operation 4 the wrong way round, the bug Wikipedia reports in the printed table,
   and shows the wrong B7.
4. Counts how the work grows with n.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java NoteG.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Note G](https://en.wikipedia.org/wiki/Note_G) — Wikipedia | What the table computes, the bug in operation 4, and the "first program" debate |
| Start | [Ada Lovelace](https://mathshistory.st-andrews.ac.uk/SH/lovelace_sh.pdf) — MacTutor (illustrated poster) | Her life and the 1843 translation in one page |
| Deeper | [Ada Lovelace and the Analytical Engine](https://blogs.bodleian.ox.ac.uk/adalovelace/2018/07/26/ada-lovelace-and-the-analytical-engine/) — Christopher Hollings, Ursula Martin and Adrian Rice, Bodleian Libraries (2018) | The historians who studied her papers: the notes, the loops, the execution trace, and music |
| Scholar | [Sketch of the Analytical Engine, with notes by the translator](https://gutenberg.org/files/75107/75107-src/75107-src.htm) — L. F. Menabrea, trans. with notes by A.A.L. (London, 1843), Project Gutenberg | The paper and the notes, including the Jacquard sentence (the copy opened was cut off before Note G's table) |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
