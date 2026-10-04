# 6. Levenshtein edit distance

*Part 1 — Distances, similarity and number theory (entries 1–20)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-1-distances-and-number-theory.md#6-levenshtein-edit-distance)

## How it works

Dynamic programming over prefixes: cell (i, j) holds the fewest insertions, deletions and substitutions turning the first i characters of one string into the first j of the other. Each cell looks at three neighbours, so the cost is O(n·m), and two rows of memory are enough.

## In depth (from the catalog page)

The fewest single-character insertions, deletions and substitutions needed to turn one string into another. It is dynamic programming: O(n·m) time, and O(m) memory if you keep only two rows.

```java
static int levenshtein(String a, String b) {
    int[] prev = new int[b.length() + 1], cur = new int[b.length() + 1];
    for (int j = 0; j <= b.length(); j++) prev[j] = j;
    for (int i = 1; i <= a.length(); i++) {
        cur[0] = i;
        for (int j = 1; j <= b.length(); j++) {
            int sub = prev[j - 1] + (a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1);
            cur[j] = Math.min(sub, Math.min(prev[j] + 1, cur[j - 1] + 1));
        }
        int[] t = prev; prev = cur; cur = t;
    }
    return prev[b.length()];
}
```

> **Verified.** kitten → sitting is 3, flaw → lawn is 2, and the empty-string and identical-string cases hold. On 2,000 random string triples (alphabet a, b, c; lengths 0 to 6), the distance was symmetric and obeyed the triangle inequality.

**Use it for** spell correction, fuzzy search, record matching and diffing short strings. Variants: Damerau (counts an adjacent swap as one edit), Jaro–Winkler (tuned for names), and a bounded version that gives up once the distance passes a limit, which is much faster for "within k edits" queries.

## Run it

```
cd code/principles/part-1-distances-and-number-theory/06-levenshtein-edit-distance
java LevenshteinDistance.java
```

JDK 17 or newer, no build step. It prints 4,003 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
LevenshteinDistance: 4003 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
