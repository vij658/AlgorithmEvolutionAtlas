# The Subroutine: the program

*Era 5 · topic 1 · 1949–1952* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/01-the-subroutine/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/01-the-subroutine/the-subroutine.html) · [All era 5 programs](../README.md)

## How it works

```text
A closed subroutine is one copy of a routine that any part of a program can jump to. The hard part is getting
back: the early machines had no "return" instruction. David Wheeler's answer, on the EDSAC at Cambridge: the
caller loads its own instruction word into the accumulator and jumps; since that word contains the caller's
address, the subroutine can add a constant to it and get the instruction "jump back to just after the caller",
which it stores in its own last word. When the routine finishes it runs into that word and goes home.
This program uses a small accumulator machine of its own (not EDSAC's order code). Each instruction is one word,
operation x 1000 + address:
    0 HLT  stop                       5 JMP a  jump to a
    1 LDA a  acc = word a             6 JNG a  jump to a if acc < 0
    2 ADD a  acc = acc + word a       7 JZR a  jump to a if acc = 0
    3 SUB a  acc = acc - word a       8 OUT a  print word a
    4 STA a  word a = acc
The caller at address n writes "LDA n" (load my own word, 1000 + n) and "JMP s"; the subroutine adds 4002 and
gets 5000 + n + 2, which is "JMP n+2". A routine that calls itself overwrites its own way home, so the Wheeler
jump cannot do recursion. Machines later kept return addresses on a stack; four extra instructions model that:
    9 CAL a  push the next address, jump to a     11 PSH  push acc
   10 RET    pop an address and jump to it        12 POP  pop into acc
```

## What the program does

```text
1. A machine and a loader that places a routine written once at any address (relocation).
2. One call traced word by word: how the return jump is built and planted.
3. A square-root subroutine (subtract 1, 3, 5, 7, ... while possible), called from k places, against the same
   code written out in full at every place (an "open" subroutine): words of memory and instructions executed.
4. A small library (square root, multiply, power), loaded at two different sets of addresses, printing a table
   of squares like the EDSAC's first program and checking every result.
5. A routine that calls itself: with the Wheeler jump it never returns; with a stack it does.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Subroutines.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [EDSAC Project Videos](https://www.tnmoc.org/edsac-videos) — The National Museum of Computing, films begun by David Allen (2012–2020) | The reconstruction of the machine on which the subroutine was born, filmed as it was built; "EDSAC Veterans" (2016) records a visit to it |
| Start | [David J. Wheeler](https://history.computer.org/pioneers/wheeler.html) — IEEE Computer Society, Computer Pioneers | The subroutine, the jump and the initial orders, credited to Wheeler |
| Start | [EDSAC](https://en.wikipedia.org/wiki/EDSAC) — Wikipedia | The machine, its first programs of 6 May 1949, and its subroutine library |
| Start | [Wheeler Jump](https://en.wikipedia.org/wiki/Wheeler_Jump) — Wikipedia | How a routine returned without a return instruction, and why it could not recurse |
| Deeper | [The EDSAC Simulator](https://www.dcs.warwick.ac.uk/~edsac/Home.html) — Martin Campbell-Kelly, University of Warwick | "A faithful software evocation of the EDSAC computer as it existed in 1949-51", with original programs and subroutines |
| Deeper | [EDSAC to be recreated](https://www.cam.ac.uk/news/edsac-to-be-recreated) — University of Cambridge (13 January 2011) | The replica project at The National Museum of Computing |
| Deeper | [EDSAC](https://tnmoc.org/edsac) — The National Museum of Computing | The replica at Bletchley Park; "There were only 18 operation codes" |
| Scholar | [Review of *The Preparation of Programs for an Electronic Digital Computer*](https://www.ams.org/journals/bull/1952-58-02/S0002-9904-1952-09610-5) — John Todd, *Bulletin of the AMS* 58 (1952), 276–278 | A contemporary review of the book that published the subroutine library |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
