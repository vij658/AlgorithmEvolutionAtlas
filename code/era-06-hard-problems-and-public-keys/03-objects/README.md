# Objects, Classes and Subclasses: the program

*Era 6 · topic 3 · 1961–1967* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/03-objects/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/03-objects/objects.html) · [All era 6 programs](../README.md)

## How it works

```text
Simula was built for simulation: a post office, a harbour, a factory, each made of many things that act on their
own and meet now and then. Dahl and Nygaard let the programmer write a class (data together with the procedures
that act on it), make as many objects of it as needed, each living as long as anything refers to it, and declare
subclasses that inherit everything and change only what differs. A "virtual" procedure is looked up in the
object's own class when it is called, so a program written for the general class works unchanged for every
subclass. Java, the language of this book's programs, is one of Simula's descendants.
A discrete-event simulation keeps a list of future events ordered by time, takes the earliest, lets the object
concerned act (which may schedule more events), and repeats.
```

## What the program does

```text
1. A small class hierarchy, Customer with subclasses Letter and Parcel, and which code each call reaches.
2. A post office with one clerk, simulated for a million customers, against queueing theory's formula.
3. The same with two clerks.
4. Letters and parcels mixed: the simulator is not changed, only the subclasses; against the
   Pollaczek-Khinchine formula.
5. The same simulation written without objects (arrays and a switch), with the same random numbers: identical
   results, and what each version must change to add a new kind of customer.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Objects.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [50 years anniversary of Simula](https://www.uio.no/om/aktuelt/rektorbloggen/2017/50-years-anniversary-of-simula-the-first-object-or.html) — University of Oslo, rector's blog (2017) | How Nygaard and Dahl came together, in a page |
| Start | [Object-Oriented Programming, 1961-1967](https://ethw.org/Milestones:Object-Oriented_Programming,_1961-1967) — Engineering and Technology History Wiki | The IEEE Milestone citation and what Simula introduced |
| Deeper | [Object-oriented programming: some history, and challenges for the next fifty years](https://arxiv.org/pdf/1303.0427) — Andrew P. Black (2013), arXiv | Classes, prefixing and virtual procedures in Simula's own words, and what Smalltalk took from it |
| Deeper | [Kristen Nygaard](https://awards.acm.org/award_winners/nygaard_5916220) — ACM Awards | The Turing Award citation for Simula I and Simula 67 |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
