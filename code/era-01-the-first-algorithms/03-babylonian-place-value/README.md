# Babylonian Place Value: the program

*Era 1 · topic 3 · c. 1800 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/03-babylonian-place-value/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/03-babylonian-place-value/babylonian-place-value.html) · [All era 1 programs](../README.md)

## How it works

```text
A number is written as a row of base-60 digits, and each digit with just two signs: a vertical wedge for 1 and a
corner wedge for 10 (so 59 is five corner wedges and nine vertical ones). The same digit means 1, 60 or 3,600
depending only on where it stands. Old Babylonian scribes had no zero for an empty place and no mark for where the
whole part ends, so readers relied on context.
To divide, a scribe looked up the reciprocal of the divisor in a table and multiplied: a / b = a x (1/b). The
standard table lists the "regular" numbers, those whose only prime factors are 2, 3 and 5, because exactly those
have reciprocals that end in base 60.
```

## What the program does

```text
1. Converts to and from base 60, counts the wedges each number needs, and measures how many numbers look alike
   when there is no zero and no point.
2. Rebuilds the standard reciprocal table and checks it, entry by entry, against the table as transcribed by
   Duncan Melville; checks that it lists exactly the regular numbers from 2 to 81; shows the endless reciprocals
   of the numbers it skips; and divides by multiplying with reciprocals.
3. Rebuilds the first row of Plimpton 322 from the reciprocal pair 2;24 and 0;25.
4. Full circle: divides by a constant the way compilers do since Granlund and Montgomery (1994), by multiplying
   with a precomputed reciprocal, and checks it against ordinary division.
Every printed line starts with a tag that the book's page builder reads. Random inputs use fixed seeds.
```

## Run it

```
java BabylonianPlaceValue.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Base 60 (sexagesimal)](https://www.youtube.com/watch?v=R9m2jck1f90) — Numberphile (Thomas Woolley) | The base-60 system shown on Yale Babylonian Collection tablets |
| Start | [The Mesopotamian Number System](https://www.youtube.com/watch?v=jsux7RzcIjw) — Khan Academy India | School-level introduction to base 60 and place value |
| Start | [Babylonian numerals](https://mathshistory.st-andrews.ac.uk/HistTopics/Babylonian_numerals/) — MacTutor | The two-sign base-60 system, the missing zero, theories for "why 60" |
| Deeper | [Ancient Babylonian tablet — world's first trig table](https://www.youtube.com/watch?v=i9-ZPGp1AJE) — UNSW | One side of the Plimpton 322 debate (the 2017 claim). Watch it with the Scientific American critique |
| Deeper | [Lecture 1, History of Math, Princeton University](https://www.youtube.com/watch?v=ZSk63kC9o6U) — Prof. Alex Kontorovich (2024) | University course lecture: early number, sexagesimal, YBC 7289, Plimpton 322 |
| Deeper | [Number Systems Ancient to Modern 2: the Babylonians](https://www.youtube.com/watch?v=58Z91hD5RXE) — N. J. Wildberger | Babylonian place value |
| Deeper | [Old Babylonian Multiplication and Reciprocal Tables](https://www.ams.org/publicoutreach/feature-column/fc-2012-05) — AMS Feature Column (Tony Phillips) | Walks through real tables; explains regular numbers and division by reciprocals |
| Scholar | [Old Babylonian mathematics and Plimpton 322: the remarkable OB sexagesimal system](https://www.youtube.com/watch?v=J5Ug3Cr8RUE) — N. J. Wildberger | Long-form lecture by a co-author of the 2017 claim, so his framing is one-sided |
| Scholar | [Plimpton 322 (P254790)](https://cdli.earth/artifacts/254790) — Cuneiform Digital Library Initiative | Catalogue record with photographs and line art |
| Scholar | ["Our Tools of Learning": Plimpton 322](https://exhibitions.library.columbia.edu/exhibits/show/plimpton/mathematics/page-2) — Columbia University Libraries | The owning library's presentation |
| Scholar | [Multiplication table (Penn Museum B6063)](https://isaw.nyu.edu/exhibitions/before-pythagoras/items/b-6063/) — ISAW, NYU, *Before Pythagoras* | A real Old Babylonian school multiplication tablet from Nippur |
| Deeper | [The numbers behind Plimpton 322](https://arxiv.org/html/1109.3814) — Anthony Phillips, arXiv | Row 1 from the reciprocal pair 2;24 and 0;25, worked through |
| Deeper | [Division by Invariant Integers using Multiplication](https://gmplib.org/~tege/divcnst-pldi94.pdf) — Granlund and Montgomery (1994) | Dividing by a constant with one multiplication; implemented in GCC |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
