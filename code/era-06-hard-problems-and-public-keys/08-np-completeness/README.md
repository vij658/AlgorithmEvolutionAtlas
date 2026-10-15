# NP-Completeness: the program

*Era 6 · topic 8 · 1971–1973* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/08-np-completeness/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/08-np-completeness/np-completeness.html) · [All era 6 programs](../README.md)

## How it works

```text
Some problems are easy to check but seem hard to solve. Given a formula in true/false variables, such as
    (x1 or x2 or not x3) and (not x1 or x3) and ...
checking a proposed assignment takes one pass over the formula; finding one, or showing there is none, seems to
need trying a large share of all 2^n assignments. NP is the class of problems whose answers can be checked
quickly; P, those that can be solved quickly ("quickly" meaning in a number of steps bounded by a polynomial).
Cook showed that every problem in NP can be translated quickly into a question about such a formula: so if
formulas could be decided quickly, everything in NP could. Karp then translated satisfiability into 21 problems
about graphs, sets and numbers, so all of them stand or fall together. Nobody knows whether they can be solved
quickly; that is the question "P = NP?".
A translation (a "reduction") must preserve the answer exactly. For example, a formula with m clauses of three
literals becomes a graph: one triangle per clause, and an edge between every literal and its negation. The graph
has m vertices with no edge between any two of them exactly when the formula can be satisfied.
```

## What the program does

```text
1. A small formula turned into a graph, and a satisfying assignment read off an independent set.
2. A chain of reductions, satisfiability -> 3-satisfiability -> independent set -> vertex cover -> clique,
   checked on 1,000 random formulas, each problem solved by its own exhaustive method.
3. Checking against finding: a formula of 60 variables, an answer checked in one pass, found by search.
4. Random 3-satisfiability with 50 variables: the share satisfiable and the work of a search, against the
   number of clauses per variable.
5. The work of the search near the hardest ratio, for 20 to 80 variables.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java NpComplete.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Favorite Theorems: NP-Completeness](https://blog.computationalcomplexity.org/2005/04/favorite-theorems-np-completeness.html) — Lance Fortnow, Computational Complexity blog (2005) | Cook and Levin in a few paragraphs |
| Start | [Favorite Theorems: Combinatorial NP-Complete Problems](https://blog.computationalcomplexity.org/2005/05/favorite-theorems-combinatorial-np.html) — Lance Fortnow (2005) | Why Karp's 21 problems changed the field |
| Start | [Karp's 21 NP-complete problems](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems) — Wikipedia | The tree of reductions |
| Deeper | [Stephen Cook](https://en.wikipedia.org/wiki/Stephen_Cook) — Wikipedia | Berkeley, Toronto, and the 1971 paper |
| Deeper | [Leonid Levin](https://en.wikipedia.org/wiki/Leonid_Levin) — Wikipedia | The same discovery, made independently in the Soviet Union |
| Scholar | [The Complexity of Theorem-Proving Procedures](https://www.cs.umd.edu/~gasarch/COURSES/452/F14/cookpaper.pdf) — S. A. Cook, STOC 1971, on a University of Maryland course page | The paper that defined the question |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
