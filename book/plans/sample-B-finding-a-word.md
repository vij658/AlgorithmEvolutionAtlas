# Sample B plan: "Finding a word" (Rabin–Karp from the pain of plain search)

**Status: plan only. Nothing here has been verified or coded yet.** In particular, every name, date and citation below is from my recollection and is **marked "to verify"**; none of it has been checked against a source in this project. Sample B is the second voice test: a *hard* chapter, to see whether the need-driven style holds when the algorithm is not obvious. Companion to [the design decisions](../00-about-the-book/design-decisions.md) and [the chapter 1 outline](../era-01-the-first-algorithms/chapter-01-adding-two-numbers/outline.md).

**Goal of the chapter.** A reader who finishes it should not think "here is Rabin–Karp" but "of course: that is what you would have to do next." Each step is the answer to a pain the previous step left.

## The chain of needs

| # | What hurt | The fix | History to verify |
|---|---|---|---|
| 0 | Find a pattern of length *m* in a text of length *n* by sliding it along and comparing character by character. On a text of all `a` and a pattern of `a…ab` it does about *n·m* comparisons. Every shift forgets everything the last one learned | | |
| 1 | Forgetting. When a mismatch happens after *k* matched characters you already know what those *k* text characters are | **Never re-read the text:** Knuth–Morris–Pratt, a failure function that says how far the pattern can shift | KMP's three-way discovery (to verify: Morris from a text-editor problem around 1970; Cook's theorem on two-way pushdown automata; Pratt; Knuth's role); the 1977 SIAM J. Comput. paper |
| 2 | Even KMP reads every text character. Can a mismatch let you skip text without reading it? | **Skip:** compare from the end of the pattern; the text character at a mismatch says how far to jump (Boyer–Moore, Horspool) | Boyer and Moore, CACM 1977; Horspool 1980 (both to verify) |
| 3 | Both methods compare *characters*. What if each window of text could be summarized by one number, compared in one step? | **Fingerprint the window,** and update the fingerprint in constant time as the window slides (a rolling hash: Horner's rule from catalog entry 15) | Karp and Rabin, "Efficient randomized pattern-matching algorithms", IBM J. Res. Dev., 1987 (to verify, including what the abstract says about higher-dimensional patterns) |
| 4 | Different windows can have the same number: collisions (the birthday bound, catalog entry 13) | **Verify on a match:** a hash match only means "check here" | |
| 5 | If the modulus is fixed and known, an adversary can build text that triggers a collision at almost every position and the running time degrades to *n·m* | **Randomize the modulus:** pick a random prime; the chance of a false match is provably small | The fixed-modulus attack on hashes mod 2⁶⁴ with Thue–Morse strings is folklore among contest programmers (to verify before using) |
| 6 | Where does the fingerprint idea shine? | **Many patterns at once** (a set of hashes), **2-D patterns**, plagiarism detection, content-defined chunking | Winnowing, rsync (to verify if mentioned) |

**The logical core to bring out:** it is cheaper to compare small summaries and only check the details when the summaries agree. That filter-then-verify shape returns later (Bloom filters, locality-sensitive hashing), which makes it a thread across the braid.

## Planned Java (differential-tested against `String.indexOf`)

- `naiveSearch`, `kmpSearch` (can reuse catalog entry 31), `horspoolSearch`, `rabinKarpSearch` with a rolling hash modulo a large prime and verification on match.
- Tests with fixed seeds: random texts and patterns over small and large alphabets, empty and equal-length edge cases, overlapping matches; every result compared with `indexOf` and with the others.
- Measured, not asserted by timing: counts of character comparisons (naive vs KMP vs Horspool), hash collisions and verifications for Rabin–Karp at several moduli; the fixed-modulus attack shown by counting false matches against a weak modulus; the randomized-modulus result as a false-match rate over many random primes.
- Program output feeds the page numbers (the same rule as chapter 1).

## History to verify before writing any prose

- KMP: who discovered what, when, and the story behind Morris's discovery; what Knuth's paper says about it.
- Boyer–Moore and Horspool: dates, venues, and what each added.
- Karp–Rabin: venue, year, and the abstract (fingerprints; higher-dimensional patterns).
- The Thue–Morse attack: a citable source (not just forum folklore) or drop it.
- Anything about rsync or plagiarism detection, only if I mention them.

## Devices planned for the chapter

- *Pause and try:* "your pattern is `aaaab`: how many comparisons does the plain method make on a text of 1,000 `a`?"; "after a mismatch at position *k*, what do you already know?"; "can two different strings share a hash? give one".
- *Wrong turn:* "just compare hashes of the whole text and pattern" (that only tests one alignment); "use the sum of the character codes as the hash" (anagrams collide, and sliding is easy but the hash is poor): the reason a *positional* hash (Horner) is needed.
- *Time-travel scene (reconstructed):* a programmer at a terminal in the early 1970s whose editor re-reads the buffer after every mismatch. Only if the history check supports the setting.
- *⊕:* "remember what you matched ⊕ a table of how far to shift = KMP"; "polynomial hash ⊕ sliding window = rolling hash"; "rolling hash ⊕ random modulus = Karp–Rabin with a guarantee".
- *Full circle:* hashing windows of data is how near-duplicate detection and content-addressed storage find repeats; fingerprints of text windows appear again in deduplicating training data for language models (to verify before any claim).

## Why this chapter is the right second test

It has a long chain of needs, one of them (collisions, then attack, then randomization) is a *security* pain rather than a speed pain, and it reuses two verified catalog entries (Horner's method, the birthday bound), which tests the "reuse the catalog as prove-it layers" decision.
