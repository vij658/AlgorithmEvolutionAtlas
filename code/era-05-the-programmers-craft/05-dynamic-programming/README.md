# Dynamic Programming: the program

*Era 5 · topic 5 · 1952–1957* · Book page: [GitHub edition](../../../book/era-05-the-programmers-craft/05-dynamic-programming/README.md) · [interactive edition](../../../book/era-05-the-programmers-craft/05-dynamic-programming/dynamic-programming.html) · [All era 5 programs](../README.md)

## How it works

```text
Many plans are made in stages: which road out of this town, how much to order this month, whether to stop or roll
again. Trying every complete plan multiplies the choices at every stage. Bellman's principle of optimality says
that whatever the first decision, the rest of an optimal plan must be optimal for the situation the first
decision leaves. So work backwards: find the best value of every situation at the last stage, then use those
values to find the best value of every situation one stage earlier, and so on to the start. Each situation is
solved once and its value kept in a table. With chance in the process, "best value" becomes "best expected value".
```

## What the program does

```text
1. A journey through 10 stages with 5 towns at each: every one of the 1,953,125 routes priced, against working
   backwards stage by stage.
2. Counting the routes through a grid: the same sub-questions asked over and over by plain recursion, against a
   table that asks each once.
3. A die you may roll up to n times, keeping the last roll: the exact value of the game for each n, as fractions,
   and the rule it implies; checked by playing a million games.
4. Packing a knapsack: the table method against all 2^18 choices for 300 random sets of items.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java DynamicProgramming.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) — Wikipedia | The method, the Bellman equation and the disputed story of the name |
| Start | [Why Is It Called "Dynamic Programming"?](https://conversableeconomist.com/2022/08/24/why-is-it-called-dynamic-programming/) — Timothy Taylor, Conversable Economist (2022) | Bellman's own account, quoted at length |
| Deeper | [Richard Ernest Bellman](https://mathshistory.st-andrews.ac.uk/Biographies/Bellman/) — MacTutor | His career at RAND and after |
| Deeper | [Richard Bellman on the Birth of Dynamic Programming](https://web.cs.miami.edu/home/odelia/teaching/csc317_fall19/syllabus/dy_birth.pdf) — Stuart Dreyfus, *Operations Research* 50(1) (2002), on a University of Miami course page | Excerpts from *Eye of the Hurricane*, introduced by a colleague |
| Scholar | [On a problem in dynamic programming](https://www.rand.org/pubs/research_memoranda/RM813.html) — R. E. Bellman, RAND RM-813 (1952) | One of the first RAND memoranda with the name (catalogue record) |
| Scholar | [Dynamic programming and a new formalism in the calculus of variations](https://pmc.ncbi.nlm.nih.gov/articles/PMC527981) — R. Bellman, *PNAS* 40(4): 231–235 (1954) | An early journal paper, with a free scan |

Every link was opened before it was listed. More, with certainty labels: [Era 5 reference catalog](../../../book/era-05-the-programmers-craft/reference-catalog.md).
