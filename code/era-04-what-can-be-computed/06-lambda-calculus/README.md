# Church's Lambda Calculus: the program

*Era 4 · topic 6 · 1936* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/06-lambda-calculus/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/06-lambda-calculus/lambda-calculus.html) · [All era 4 programs](../README.md)

## How it works

```text
There are only three kinds of term: a variable x; a function \x.M ("given x, return M"); and an application M N
("apply M to N"). There is one rule of computation, beta reduction: (\x.M) N becomes M with N put in place of x.
A term with nothing left to reduce is in normal form, and that is the answer. Numbers are functions: the numeral
n is \f.\x.f (f (... (f x))), "apply f n times". Arithmetic is then a matter of composing:
    PLUS = \m.\n.\f.\x.m f (n f x)      MULT = \m.\n.\f.m (n f)      EXP = \m.\n.n m
Recursion needs no names: Y = \g.(\x.g (x x)) (\x.g (x x)) satisfies Y g = g (Y g). Some terms never reach a
normal form, such as (\x.x x) (\x.x x), which reduces to itself, and Church proved in 1936 that no effective
procedure decides which terms have one.
```

## What the program does

```text
1. Parses lambda terms and reduces them, always rewriting the leftmost, outermost redex first.
2. Church's own numerals of 1936, which start at 1, beside today's, which start at 0.
3. PLUS, MULT, EXP and the predecessor on small numerals, against ordinary arithmetic, counting reduction steps;
   the whole reduction of PLUS 2 3, step by step.
4. Factorial through the Y combinator, with no named recursion anywhere.
5. The term that reduces to itself for ever, and a term whose answer depends on the order of reduction.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LambdaCalculus.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus) — Wikipedia | Terms, β-reduction, Church numerals, Ω and Y, and the history |
| Start | [Alonzo Church](https://mathshistory.st-andrews.ac.uk/Biographies/Church/) — MacTutor | Church's life, his thesis, his theorem, and his students |
| Deeper | [Birth of lambda-calculus and combinatory logic](https://www.macs.hw.ac.uk/~fairouz/forest/events/history/birth-lambda.html) — Roger Hindley, talk abstract, Workshop on History of Logics, Types and Rewriting, Heriot-Watt University (5 December 2000) | Schönfinkel's combinators of 1920, before the λ-calculus |
| Scholar | [An Unsolvable Problem of Elementary Number Theory](https://courses.fit.cvut.cz/NI-VYC/church-an-unsolvable-problem-of-elementary-number-theory.pdf) — Alonzo Church, *American Journal of Mathematics* 58(2):345–363 (1936), scan on a Czech Technical University course page | The numerals, the thesis, and the first unsolvable problem |
| Scholar | [A Note on the Entscheidungsproblem](https://people.csail.mit.edu/brooks/idocs/church_ent.pdf) — Alonzo Church, *The Journal of Symbolic Logic* 1(1):40–41 (1936), reprint on an MIT page | Hilbert's decision problem for first-order logic, answered: no |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
