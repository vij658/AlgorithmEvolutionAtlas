# 31. Knuth–Morris–Pratt string search

*Part 2 — Algorithm paradigms and classics (entries 21–42)* · [All programs](../../README.md) · [Catalog page](../../../../book/principles-catalog/part-2-paradigms-and-classics.md#31-knuthmorrispratt-string-search)

## How it works

Knuth–Morris–Pratt never re-reads text. A failure table, computed from the pattern alone, says how far the pattern can shift after a mismatch while keeping the characters already matched, so the search runs in O(n + m).

## In depth (from the catalog page)

A naive search restarts from the next text position after every mismatch and can re-read the same characters again and again. KMP (1977) precomputes, for each prefix of the pattern, the length of its longest proper prefix that is also a suffix (the *prefix function*). After a mismatch it falls back by that amount instead of restarting, so the text pointer never moves backwards and the total work is O(n + m).

```java
static int[] prefixFunction(String p) {                // pi[i] = longest proper prefix of p[0..i] that is also a suffix
    int[] pi = new int[p.length()];
    for (int i = 1, k = 0; i < p.length(); i++) {
        while (k > 0 && p.charAt(i) != p.charAt(k)) k = pi[k - 1];
        if (p.charAt(i) == p.charAt(k)) k++;
        pi[i] = k;
    }
    return pi;
}

static int kmpSearch(String text, String p) {          // first match or -1, O(n + m)
    if (p.isEmpty()) return 0;
    int[] pi = prefixFunction(p);
    for (int i = 0, k = 0; i < text.length(); i++) {
        while (k > 0 && text.charAt(i) != p.charAt(k)) k = pi[k - 1];
        if (text.charAt(i) == p.charAt(k)) k++;
        if (k == p.length()) return i - k + 1;
    }
    return -1;
}

static int smallestPeriod(String s) {                  // shortest p such that s is s[0, p) repeated
    int m = s.length();
    if (m == 0) return 0;
    int p = m - prefixFunction(s)[m - 1];
    return m % p == 0 ? p : m;
}
```

> **Verified.** `prefixFunction("abacabad")` is 0, 0, 1, 0, 1, 2, 3, 0. `kmpSearch` matched `String.indexOf` on 20,000 random binary strings and patterns. `smallestPeriod` matched a brute-force search on 20,000 random strings of up to 12 characters; it gives 3 for "abcabcabc", 1 for "aaaa", and 7 (no repetition) for "abcabca". On the adversarial text of 100,000 `a` characters with the pattern 999 `a` characters followed by `b`, naive search made 99,001,000 character comparisons and KMP made 299,000, about three per text character (both counted with instrumented copies).

<!-- -->

> **Pitfall.** For everyday substring search call `String.indexOf` or `contains`. KMP earns its place when the input arrives as a stream you can read only once (the text pointer never backs up), when the input may be adversarial, and when you want the prefix function itself, for example to find a string's smallest period. For many patterns at once, look at Aho–Corasick, which generalizes the same fallback idea.

**Use it for** pattern matching in streams and network traffic, detecting repetition and periodicity in strings, and as a building block: the prefix function is the core of several string algorithms, and the Z-algorithm is a close relative.

## Run it

```
cd code/principles/part-2-paradigms-and-classics/31-knuth-morris-pratt
java KnuthMorrisPratt.java
```

JDK 17 or newer, no build step. It prints 40,005 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
text a^100000, pattern a^999 b: naive search made 99001000 comparisons, KMP made 299000
KnuthMorrisPratt: 40005 checks passed
```

## References

- *Video, lecture and article references for this topic will be added when the book's reference catalog reaches it.*
