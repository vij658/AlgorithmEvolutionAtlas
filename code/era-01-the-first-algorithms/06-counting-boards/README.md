# Counting Boards: the program

*Era 1 · topic 6 · c. 300 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/06-counting-boards/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/06-counting-boards/counting-boards.html) · [All era 1 programs](../README.md)

## How it works

```text
A counting board is place value you can touch. Each column (or line) stands for ones, tens, hundreds, and so on,
and the number of counters in it is that digit. To add, push the second number's counters onto the board, then
settle: wherever a column holds ten, clear it and put one counter in the next column. Many boards and abaci also
have a counter worth five in each column (a "bi-quinary" layout, as on the Roman hand abacus and the soroban), so a
column never needs more than one five and four ones: five ones are exchanged for a five, two fives for one counter
in the next column. No digit is ever written; the procedure lives in the hands.
```

## What the program does

```text
1. Models a plain board (up to 9 counters per column) and a board with fives, adds and subtracts on both by
   pushing counters and settling, and checks both against ordinary arithmetic on 400,000 random cases.
2. Counts the work: counters on the board, counters moved, and exchanges, for a worked example and on average.
3. Shows an invariant: however the exchanges are ordered (settling after every addition, or piling counters up
   and settling once at the end), their number is the same, because each exchange removes exactly nine counters
   net. Delaying the carries is the idea behind the carry-save adders of fast hardware multipliers.
Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
```

## Run it

```
java CountingBoard.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Introduction to the Roman abacus and counting board](https://www.youtube.com/watch?v=c-2I09cmth0) — Reading Ancient Schoolroom (University of Reading) | Reconstructed Roman reckoning. Follow-up: Multiplication on the Roman abacus |
| Start | [The Salamis Tablet — Calculating on a Counting board](https://www.youtube.com/watch?v=mYR4qa3pswU) — Jens Puhle | A Salamis-style board demonstrated, cited by Wikipedia (independent creator) |
| Start | [Seeing Numbers with Soroban — The Japanese Abacus](https://www.youtube.com/watch?v=Q7OYQqPLH0o) — The Japan Society | How the soroban is used (ages 7–11 and up) |
| Start | [Revolution: Calculators — Abacus](https://www.computerhistory.org/revolution/calculators/1/1) — Computer History Museum | Abaci from China to Greece to the Inca, with the Salamis tablet |
| Deeper | [In Search of A Rare Roman Pocket Calculator](https://cacm.acm.org/blogcacm/in-search-of-a-rare-roman-pocket-calculator/) — Communications of the ACM blog | Tracking down the surviving Roman hand abaci |
| Deeper | [The Abacus, the Numeral Frame, and Counters](https://www.si.edu/spotlight/the-abacus-the-numeral-frame-and-counters) — Smithsonian | European counting boards, suanpan and soroban (it wrongly calls *calculi* Greek; the word is Latin) |
| Scholar | [Exploring Ancient Greek and Roman Numeracy](https://www.youtube.com/watch?v=-45Hxj6Txoo) — Gresham College, Serafina Cuomo (2011) | The Salamis abacus, the Aosta abacus, finger counting, and what remains unknown |
| Scholar | [Permanent exhibition: the Salamis tablet](https://epigraphicmuseum.gr/en/permanent-exhibition/) — Epigraphical Museum, Athens | The holding museum's description |
| Scholar | [Salamis Counting Table (replica)](https://www.si.edu/object/nmah_690540) — Smithsonian NMAH | Replica record; calculation by moving pebbles along lines |
| Scholar | [The Dialogue concerning the Exchequer](https://avalon.law.yale.edu/medieval/excheq.asp) — Avalon Project, Yale Law School (Henderson's translation) | Primary text, c. 1179 |
| Scholar | [A Suggestion for a Fast Multiplier](https://scispace.com/papers/a-suggestion-for-a-fast-multiplier-12zf7tphek) — C. S. Wallace, IEEE Transactions on Electronic Computers 13 (1964) | Adding many rows at once and settling the carries at the end |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
