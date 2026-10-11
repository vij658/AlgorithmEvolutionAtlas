# Boole's Algebra of Logic: the program

*Era 3 · topic 12 · 1847–1854* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/12-boolean-algebra/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/12-boolean-algebra/boolean-algebra.html) · [All era 3 programs](../README.md)

## How it works

```text
Let x stand for a class of things (men), and xy for the things in both x and y (mortal men). Then xx = x: selecting
men from men gives men. As an equation of ordinary algebra, x^2 = x has only the roots 0 and 1, so Boole's symbols
behave like numbers that can only be 0 (nothing) or 1 (everything). 1 - x is "not x", and "All x are y" says that
nothing is x without being y: x(1 - y) = 0. Reasoning becomes algebra on 0 and 1: substitute, multiply, solve.
Any expression in x can be expanded as f(1) x + f(0)(1 - x), which is a truth table written as a formula.
Shannon (1937) saw that a relay contact is also either closed (1) or open (0): contacts in series give xy, in
parallel x + y - xy, so circuits can be designed and simplified by Boole's algebra.
```

## What the program does

```text
1. Finds the solutions of x^2 = x among whole numbers and fractions: only 0 and 1.
2. Checks Boole's expansion on every function of two and three variables.
3. Tests all 256 forms of the categorical syllogism by algebra over 0 and 1, and counts the valid ones, with and
   without assuming that every class has members.
4. Builds a full adder and a 16-bit adder from Boolean expressions and checks them on every input.
5. Simplifies a switching circuit by Boole's laws and counts the contacts saved.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java BooleanAlgebra.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [George Boole](https://mathshistory.st-andrews.ac.uk/Biographies/Boole/) — MacTutor | His life from Lincoln to Cork, and the two books |
| Start | [A Symbolic Analysis of Relay and Switching Circuits](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits) — Wikipedia | How Shannon turned Boole's algebra into circuit design |
| Deeper | [The Life and Work of George Boole (review)](https://www.maths.tcd.ie/pub/ims/bull74/Lynch2.pdf) — Peter Lynch, *Irish Mathematical Society Bulletin* 74:97–101 (2014) | A short guide to MacHale's biography and to why Boole matters |
| Scholar | [An Investigation of the Laws of Thought (1854)](https://www.gutenberg.org/etext/15114) — George Boole, Project Gutenberg eBook 15114 (public domain; [PDF](https://www.gutenberg.org/files/15114/15114-pdf.pdf)) | The book: x² = x, and logic as an algebra of 0 and 1 |
| Scholar | [A Symbolic Analysis of Relay and Switching Circuits](https://dspace.mit.edu/bitstream/handle/1721.1/11173/34541425.pdf%20?sequence=1) — Claude E. Shannon, MIT master's thesis (signed 10 August 1937; degree listed 1940), MIT DSpace | "This calculus is shown to be exactly analogous to the Calculus of Propositions used in the symbolic study of logic" |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
