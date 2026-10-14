# Regular Expressions: the program

*Era 5 · topic 2 · 1951* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/02-regular-expressions/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/02-regular-expressions/regular-expressions.html) · [All era 5 programs](../README.md)

## How it works

```text
A regular expression is built from single symbols with three operations: E|F (either), EF (one then the other)
and E* (zero or more of E, one after another). Kleene showed in 1951 that these describe exactly the patterns a
machine with finitely many states can recognise.
Thompson's construction turns an expression into such a machine piece by piece: a symbol is two states joined by
an arrow labelled with the symbol; "either" and "repeat" add two states and some unlabelled arrows (moves that
read nothing); "then" joins the end of one piece to the start of the next. The machine is nondeterministic: it
can be in several states at once. To match a text, keep the set of states the machine could be in, and update the
whole set once per letter: the work is (letters) x (states), never more.
Rabin and Scott (1959) showed that each set of states can itself be made one state of an ordinary machine (the
subset construction). That machine reads each letter with a single table lookup, but it may need 2^n states.
```

## What the program does

```text
1. A parser for Kleene's three operations and Thompson's construction; checks the state count 2s - c.
2. An expression for the binary numerals divisible by 3, checked on every string of up to 16 digits.
3. Random expressions matched on random strings by the state-set method, by the subset machine, and by
   java.util.regex: all three must agree.
4. The subset construction and minimisation for (a|b)*abb, and the 2^n blow-up for "the n-th letter from the
   end is a".
5. A backtracking matcher (try one way, back up, try another) against the state-set method on (a|aa)*b.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java RegularExpressions.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Regular expression](https://en.wikipedia.org/wiki/Regular_expression) — Wikipedia | From Kleene's regular events to QED, ed and grep |
| Start | [Brian Kernighan Remembers the Origins of 'grep'](https://thenewstack.io/brian-kernighan-remembers-the-origins-of-grep/) — David Cassel, The New Stack (2018) | How grep was written in a night, in Kernighan's words |
| Deeper | [Powerset construction](https://en.wikipedia.org/wiki/Powerset_construction) — Wikipedia | Turning a machine that guesses into one that does not, and the 2^n price |
| Deeper | [Thompson's construction](https://en.wikipedia.org/wiki/Thompson%27s_construction) — Wikipedia | Pattern to machine in linear size, piece by piece |
| Scholar | [Representation of Events in Nerve Nets and Finite Automata](https://www.rand.org/pubs/research_memoranda/RM704.html) — S. C. Kleene, RAND RM-704 (15 December 1951) | The memorandum that defines the regular events |
| Scholar | [Representation of Events in Nerve Nets and Finite Automata (PDF)](https://apps.dtic.mil/sti/pdfs/ADA596138.pdf) — Kleene 1951, scan via the Defense Technical Information Center | Section 7: the three operations and the footnote on the name |
| Scholar | [Finite Automata and Their Decision Problems](https://www.cs.miami.edu/~burt/learning/csc427.222/docs/rabin-scott.pdf) — M. O. Rabin and D. Scott, *IBM Journal* (April 1959), 114–125, on a University of Miami course page | Nondeterministic automata and the subset construction |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
