# The Compiler, and a Grammar for Languages: the program

*Era 5 · topic 8 · 1954–1960* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/08-the-compiler/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/08-the-compiler/the-compiler.html) · [All era 5 programs](../README.md)

## How it works

```text
A compiler reads a formula such as A + B * C ** 2 and writes the machine instructions that compute it. First it
must find the structure the formula's author meant: multiplication before addition, powers before
multiplication, left to right among equals. The ALGOL 60 report wrote that structure down as a grammar:
    <expression> ::= <term> | <expression> <adding operator> <term>
    <term>       ::= <factor> | <term> <multiplying operator> <factor>
    <factor>     ::= <primary> | <factor> ** <primary>
    <primary>    ::= <number> | <variable> | ( <expression> )
Each rule becomes one procedure of the parser, which calls the others as the rules mention them. The result is a
tree; the code generator walks the tree and emits instructions for a machine with one accumulator, using
temporary storage words where an intermediate result has to wait. FORTRAN's makers cared above all that the
instructions be nearly as few as a careful programmer's, so the generator tries not to store and reload what it
can use directly.
```

## What the program does

```text
1. A parser written straight from the grammar above, showing the structure it finds in a formula.
2. Two code generators for a one-accumulator machine: a plain one that stores every intermediate result, and one
   that uses an operand directly whenever it can; the instructions for a sample formula.
3. 20,000 random formulas from the grammar: printed, parsed again, compiled both ways, run on the machine with
   random values, and checked against direct evaluation; the instruction counts of the two generators.
4. Left to right: A - B - C, and why the rule <expression> <adding operator> <term> fixes the meaning.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Compiler.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [FORTRAN-1 is formally published](https://www.computinghistory.org.uk/det/5492/FORTRAN-1-is-formally-published/) — Centre for Computing History | The dates: manual, paper, first compiler |
| Start | [Backus–Naur form](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) — Wikipedia | Rules that define a language, from Backus 1959 to today |
| Deeper | [John Backus](https://amturing.acm.org/award_recipient/backus_0703524) — ACM Turing Award | Speedcoding, FORTRAN, BNF and his later work |
| Deeper | [The FORTRAN automatic coding system](https://www.computerhistory.org/collections/catalog/102663113) — Computer History Museum catalogue | The 1957 paper's record and author list |
| Scholar | [The FORTRAN Automatic Coding System](https://people.cs.umass.edu/~emery/classes/cmpsci691st/readings/PL/FORTRAN-102663113.05.01.acc.pdf) — J. W. Backus et al., *Proceedings of the Western Joint Computer Conference* (February 1957), on a University of Massachusetts course page | The compiler described by its makers, with the 47-statement case history |
| Scholar | [Revised Report on the Algorithmic Language Algol 60](https://masswerk.at/algol60/report.htm) — Edited by Peter Naur; transcription at masswerk.at | The grammar of a whole language written in BNF |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
