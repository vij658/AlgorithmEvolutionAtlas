# Fast String Searching: the program

*Era 6 · topic 11 · 1969–1977* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/11-string-search/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/11-string-search/string-search.html) · [All era 6 programs](../README.md)

## How it works

```text
The simple way to find a pattern of length m in a text of length n tries every starting position and compares
letter by letter; on unlucky texts (aaaa...ab) that is about m times n comparisons, and on a mismatch it moves
back in the text to try the next position.
Knuth, Morris and Pratt never move back. When a mismatch comes after j matched letters, those j letters are known:
they are the first j letters of the pattern. A table computed once from the pattern ("next") says how much of the
pattern can still be matched at that point. Each letter of the text is read once, and the whole search takes
time proportional to m + n.
Boyer and Moore compare from the right end of the pattern. If the text letter there does not occur in the pattern
at all, the pattern can jump m places at once. Two tables say how far to shift: one by the mismatched letter
(delta1), one by the matched ending (delta2). On ordinary text most letters are never looked at: the longer the
pattern, the faster the search.
```

## What the program does

```text
1. The simple method on an unlucky text: comparisons and backing up.
2. The "next" table of Knuth, Morris and Pratt for a sample pattern, and a search with it.
3. Boyer and Moore's two tables for a sample pattern.
4. All three methods on 20,000 random searches: identical answers.
5. Letters examined per letter of text passed, for patterns of length 1 to 14, in English (this book's own
   field notes), in random binary text, and in random text over 100 symbols.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java StringSearch.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Boyer–Moore string-search algorithm](https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm) — Wikipedia | The two tables, and the long road to its worst-case bound |
| Scholar | [Fast Pattern Matching in Strings](https://cs.brown.edu/courses/csci1810/fall-2023/resources/ch2_readings/kmp_strings.pdf) — D. E. Knuth, J. H. Morris and V. R. Pratt, *SIAM Journal on Computing* (1977), on a Brown course page | The algorithm, its theory, and a section on how it was found three times |
| Scholar | [A Fast String Searching Algorithm](https://www.cs.utexas.edu/%7Emoore/publications/fstrpos.pdf) — R. S. Boyer and J S. Moore, *Communications of the ACM* (1977), on Moore's page | Searching from the right, with measurements on English and random text |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
