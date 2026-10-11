# Hollerith's Tabulator: the program

*Era 3 · topic 13 · 1890* · Book page: [GitHub edition](../../../book/era-03-tables-and-machines/13-hollerith-tabulator/README.md) · [interactive edition](../../../book/era-03-tables-and-machines/13-hollerith-tabulator/hollerith-tabulator.html) · [All era 3 programs](../README.md)

## How it works

```text
Each person becomes one card, with a hole punched for each answer (sex, born in the country or abroad, age group,
and so on). To count, a clerk places a card in a press; pins come down, and wherever there is a hole a pin passes
through into a cup of mercury, closes a circuit, and advances a dial by one. One pass of the cards fills many dials
at once, and relays can count combinations ("native males aged 20 to 29") by requiring several holes together.
A sorting table then shows which drawer each card should go into, so the deck can be divided and counted again for
new questions without re-punching. Later sorters sorted on one column at a time; sorting a deck column by column,
from the last digit to the first, sorts it completely (radix sort).
```

## What the program does

```text
1. Works out the speed-ups in the 1888 trial from the Census Bureau's published hours.
2. Punches a synthetic population of 1,000,000 people onto cards, and counts it two ways: by hand tallies (one
   mark per person per question) and by the tabulator (one card per person per pass, many dials at once).
3. Counts combinations with relays on 40 dials, as many as the 1890 tabulator had, in a single pass.
4. Sorts the deck into drawers by a column, and sorts card numbers completely by passes column by column.
5. Full circle: the same count as a modern group-by, and the clerk's time at 80 cards a minute.
The population is invented test data, not census returns.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java HollerithTabulator.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Hollerith Machine](https://www.census.gov/about/history/bureau-history/census-innovations/technology/hollerith-machine.html) — US Census Bureau history | The 1888 trial in hours, the mercury cups, the 40 dials and the sorting table |
| Start | [Herman Hollerith](https://columbia.edu/cu/computinghistory/hollerith.html) — Frank da Cruz, Columbia University Computing History (2001, updated 2023) | His life, the patent, the PhD and the 1890 census |
| Scholar | [An Electric Tabulating System](https://columbia.edu/cu/computinghistory/hh/index.html) — Herman Hollerith, *School of Mines Quarterly* X(16):238–255 (April 1889), reproduced by Columbia University | His own description: the problem, the cards, the circuits and the sorting box |
| Scholar | [US 395,782: Art of compiling statistics](https://patents.google.com/patent/US395782) — Herman Hollerith, US patent issued 8 January 1889, Google Patents | The claims: holes for statistical items, counted by electric circuits |

Every link was opened before it was listed. More, with certainty labels: [Era 3 reference catalog](../../../book/era-03-tables-and-machines/reference-catalog.md).
