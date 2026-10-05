# Grouping and the First Carry: the program

*Era 1 · topic 2 · c. 3000 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/02-grouping-and-the-first-carry/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/02-grouping-and-the-first-carry/grouping-and-the-first-carry.html) · [All era 1 programs](../README.md)

## How it works

```text
A tally needs one mark per thing. Grouped numerals give each bundle its own sign: Egyptian hieroglyphs have signs
for 1, 10, 100, ... up to 1,000,000, and the earliest Sumerian accounts bundle 10 small units into one sign, 6 of
those into the next, then 10, then 6 again. A number is written by repeating each sign as often as needed.
Adding is then two moves: pool the signs of both numbers, and wherever there are too many of one sign (ten, or
six, depending on the step), exchange them for one sign of the next size. That exchange is the carry. It is
older than place value: it only needs bundles and an exchange rate.
```

## What the program does

```text
1. Writes numbers in four ways: a tally, Egyptian signs (exchange rate 10 at every step), the Sumerian
   sexagesimal system for counted objects (rates 10, 6, 10, 6, 10) and the bisexagesimal system for rations
   (rates 10, 6, 2, 10, 6), and counts how many signs each needs.
2. Adds by pooling and exchanging, printing every exchange of a worked example, and checks the method against
   ordinary addition on 300,000 random pairs in every system.
3. Measures carries: how often a column passes a carry on when two long random numbers are added (Holte showed
   the long-run share is one half, in any base), and the longest carry chain when two random 40-bit numbers are
   added (Burks, Goldstine and von Neumann, 1946, showed its average is at most log2 40, about 5.3).
Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
```

## Run it

```
java GroupingAndCarry.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Cuneiform Numbers](https://www.youtube.com/watch?v=RR3zzQP3bII) — Numberphile (Alex Bellos) | How numbers were written in cuneiform |
| Start | [Egyptian Number System](https://www.youtube.com/watch?v=z8f4MR6m7YY) — Khan Academy India | The hieroglyphic signs for powers of ten |
| Start | [Arithmetic Operations in Egyptian Number System](https://www.youtube.com/watch?v=YdOXWQuNsDE) — Khan Academy India | Adding with Egyptian numerals: the pool-and-exchange carry |
| Start | [The most important lumps of dry mud in history](https://www.youtube.com/watch?v=BLHhcYFeC5A) — Stefan Milo | Clay tokens as counters that became writing (does not mention the critiques) |
| Deeper | [From Laundry Lists to Liturgies: The Origins of Writing in Ancient Mesopotamia](https://www.youtube.com/watch?v=Rgdb-sY0Y4A) — Getty Museum, Irving Finkel (British Museum) | 90-minute talk on how cuneiform began, accounting included |
| Deeper | [Denise Schmandt-Besserat — How Writing Came About](https://www.youtube.com/watch?v=M7bg0PsNXMQ) — Talk by the author of the token theory | The theory in her own words; pair it with Valerio and Ferrara |
| Deeper | [Number Systems Ancient to Modern 1: the Egyptians](https://www.youtube.com/watch?v=NgNNkUewUGQ) — Insights into Mathematics, N. J. Wildberger (UNSW) | Long lecture on the Egyptian system |
| Deeper | [Tokens: their significance for the origin of counting and writing](https://sites.utexas.edu/dsb/tokens/tokens/) — Denise Schmandt-Besserat, UT Austin | The token sequence with dates |
| Scholar | [Bulla with impressions and tokens (SB 1967)](https://collections.louvre.fr/en/ark:/53355/cl010176019) — Musée du Louvre | A real clay envelope from Susa holding 15 tokens |
| Scholar | [Proto-cuneiform tablet: account of barley distribution](https://www.metmuseum.org/art/collection/search/329081) — Metropolitan Museum of Art | Jemdet Nasr tablet, c. 3100–2900 BCE, with circular impressions used as numbers |
| Scholar | [Numeracy at the dawn of writing: Mesopotamia and beyond](https://www.sciencedirect.com/science/article/pii/S0315086020300665) — Valerio and Ferrara, Historia Mathematica 59 (2022) | The critique of the token theory |
| Scholar | [The state of decipherment of proto-Elamite](https://www.mpiwg-berlin.mpg.de/Preprints/P183.PDF) — Robert K. Englund, MPIWG Preprint 183 | Proto-cuneiform number systems and their link to tokens |
| Deeper | [Carries, Combinatorics, and an Amazing Matrix](https://sites.math.washington.edu/~billey/classes/561.fall.2019/past.articles/holte.pdf) — John M. Holte, American Mathematical Monthly 104 (1997) | Carries form a Markov chain; in the long run half the columns carry |
| Scholar | [Preliminary discussion of the logical design of an electronic computing instrument](https://www.cs.unc.edu/~adyilie/comp265/vonNeumann.html) — Burks, Goldstine and von Neumann (1946) | Section 5.6: the longest carry sequence averages about 5 for 40 digits |
| Scholar | [Carries, Shuffling and An Amazing Matrix](https://ar5iv.labs.arxiv.org/html/0806.3583) — Diaconis and Fulman (2008), arXiv | Where Holte's carries chain leads: card shuffling and Eulerian numbers |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
