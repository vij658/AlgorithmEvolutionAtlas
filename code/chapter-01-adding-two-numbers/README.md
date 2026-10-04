# Chapter 1 program: adding two numbers

*Book:* [chapter 1 outline](../../book/era-01-the-first-algorithms/chapter-01-adding-two-numbers/outline.md) · [history fact sheet](../../book/era-01-the-first-algorithms/chapter-01-adding-two-numbers/history-fact-sheet.md) · [era 1 reference catalog](../../book/era-01-the-first-algorithms/reference-catalog.md)

## How it works

Adding two numbers written in columns: each column's total keeps what fits (total mod radix) and passes the rest up as a carry (total div radix). Because two digits below r plus a carry of 1 never reach 2r, the carry is always 0 or 1, in any base and even in mixed bases such as pounds, shillings and pence. A counting board does the same work in two steps: push all the counters on, then settle full columns. In a machine the carry is the slow part: rippling waits for the longest carry chain (about log2 n columns on random inputs, n in the worst case), while carry-lookahead combines (generate, propagate) pairs in doubling rounds and finishes in ceil(log2 n) rounds, at the cost of more work.

## What is in the file

| Section | Methods | The idea |
|---|---|---|
| The carry is an exchange | `value`, `addColumns` | Column addition in any radix, including mixed radix (£ s d); the carry is always 0 or 1 |
| The counting board | `columnSums`, `settle` | Push every counter on first (all columns at once), then settle full columns |
| The machine: carry-lookahead | `generates`, `propagates`, `lookaheadCarries`, `addLookahead` | Combine (generate, propagate) pairs over doubling spans: ceil(log2 n) rounds |
| How long carry chains are | `longestChain` | On random inputs the longest chain grows like log2 n, not n |
| A real 64-bit word | `addByRippling`, `addByLookahead` | `a ^ b` is the sum without carries, `a & b` the carries; ripple until no carry is left, or look ahead in 6 rounds |
| Checks | `main` | Against `BigInteger` and Java's own `+`, on hundreds of thousands of random cases with fixed seeds |

## Run it

```
cd code/chapter-01-adding-two-numbers
java AddingTwoNumbers.java
```

It prints 14,072,170 passing checks. Every number the chapter quotes comes from this output.

## Expected output

```
3 pounds 17s 9d + 2 pounds 5s 8d = 6 pounds 3s 5d (pence 9 + 8 = 17 -> 5, carry 1; shillings 17 + 5 + 1 = 23 -> 3, carry 1; pounds 3 + 2 + 1 = 6)
the carry out of a column is never more than 1: checked every digit pair and incoming carry for every radix from 2 to 100 (676,698 cases)
addColumns against BigInteger, numbers of up to 40 columns: radix 2: 100,000 sums match; radix 10: 100,000 sums match; radix 60: 100,000 sums match; random mixed radices (2 to 100 per column): 100,000 sums match; 
decimal: 478 + 359 = 837; 99999 + 1 = 100000
exercises: 7 yd 2 ft 11 in + 4 yd 1 ft 5 in = 12 yd 1 ft 4 in; 1 h 45 min 50 s + 2 h 20 min 25 s = 4 h 6 min 15 s
64 binary columns, all ones plus one (the worst case): a ripple adder passes the carry through all 64 columns in turn; lookahead settles every carry in 6 rounds and 321 combine steps
longest carry chain when adding two random n-bit numbers, 1,000,000 pairs for each n: 8 bits: average longest chain 2.16 (log2 n = 3.00), longest seen 8; 16 bits: average longest chain 3.24 (log2 n = 4.00), longest seen 16; 32 bits: average longest chain 4.29 (log2 n = 5.00), longest seen 21; 40 bits: average longest chain 4.62 (log2 n = 5.32), longest seen 23; 64 bits: average longest chain 5.31 (log2 n = 6.00), longest seen 23; (for n = 40 von Neumann's team estimated about log2 40 = 5.3)
a real 64-bit word, 1,000,000 random pairs: rippling and lookahead both agree with Java's +; rippling needs (longest carry chain + 1) rounds exactly, on average 5.62 rounds for random 40-bit numbers and 6.29 for random 64-bit numbers, and more than 6 rounds for 37.6% of the 64-bit pairs; all ones + 1 needs 64 rounds; lookahead always needs 6
AddingTwoNumbers: 14072170 checks passed
```

## References

- History of counting, numerals, place value and the counting board, with checked video, lecture, article and primary-source links: [Era 1 reference catalog](../../book/era-01-the-first-algorithms/reference-catalog.md), topics 1–3 and 6.
- Every historical claim in the chapter, with its source and confidence label: [history fact sheet](../../book/era-01-the-first-algorithms/chapter-01-adding-two-numbers/history-fact-sheet.md).
