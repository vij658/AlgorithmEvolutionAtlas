# Archimedes Squeezes Pi: the program

*Era 1 · topic 8 · c. 250 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/08-archimedes-pi/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/08-archimedes-pi/archimedes-pi.html) · [All era 1 programs](../README.md)

## How it works

```text
Pi cannot be written down exactly, so Archimedes trapped it. A regular polygon drawn inside a circle has a perimeter
shorter than the circle; one drawn outside has a longer perimeter. Starting from hexagons and doubling the number
of sides four times (6, 12, 24, 48, 96), the two perimeters close in on the circumference from both sides. With
diameter 1, if a is the outside perimeter and b the inside one, doubling the sides gives
    a' = 2ab / (a + b)        (the harmonic mean)
    b' = sqrt(a' b)           (the geometric mean)
Every square root has to be approximated, so Archimedes rounded each bound the safe way: lower bounds down, upper
bounds up. His result, Proposition 3: 3 10/71 < pi < 3 1/7, that is 223/71 < pi < 22/7.
```

## What the program does

```text
1. Runs the doubling from hexagons to 96 sides at high precision and prints both bounds and the gap at each step.
2. Checks Archimedes' result against the 96-gon (his fractions lie safely outside the exact polygon values) and his
   bounds for the square root of 3, 265/153 < sqrt(3) < 1351/780, which are continued-fraction convergents.
3. Redoes the whole computation rounding every intermediate value outward to 4 significant digits, as a hand
   computer must: the bounds stay valid. This is interval arithmetic.
4. Measures how the gap shrinks (about 4 times per doubling), how many doublings 35 digits need (van Ceulen's
   record, c. 1600), and what Huygens-style extrapolation gets from the 48- and 96-gons.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ArchimedesPi.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Discovery That Transformed Pi](https://www.youtube.com/watch?v=gMlf1ELvRzc) — Veritasium | Opens with Archimedes doubling polygons to 96 sides, then moves to Newton's series |
| Start | [The Story of Pi](https://www.youtube.com/watch?v=f4Sk6gEG570) — Gresham College, Robin Wilson (2007) | Archimedes repeatedly doubling a hexagon's sides, in the long history of π |
| Start | [Approximating Pi](https://www.pbs.org/wgbh/nova/archimedes/pi.html) — PBS NOVA | Illustrated: hexagon to 96-gon |
| Start | [A history of Pi](https://mathshistory.st-andrews.ac.uk/HistTopics/Pi_through_the_ages/) — MacTutor | Archimedes' recursion in the long history of π |
| Deeper | [How Archimedes showed that π is approximately equal to 22/7](https://arxiv.org/pdf/2008.07995) — Damini and Dhar, arXiv | Step-by-step modern reconstruction of the doubling recurrences |
| Deeper | [Ancient estimate of π and modern numerical analysis](https://www.johndcook.com/blog/2023/07/30/archimedes-richardson/) — John D. Cook | From the 96-gon to Huygens and Richardson extrapolation |
| Deeper | [Archimedes on the Circumference and Area of a Circle](https://www.ams.org/publicoutreach/feature-column/fc-2012-02) — AMS Feature Column (Bill Casselman) | The method of exhaustion in Proposition 1 (not the 96-gon) |
| Scholar | [The Works of Archimedes](https://archive.org/details/worksofarchimede00arch) — T. L. Heath (1897), Internet Archive | The standard English translation, including *Measurement of a Circle* |
| Scholar | [Archimedes' Measurement of a Circle](https://triumphsannals.journals.publicknowledgeproject.org/index.php/triumphsannals/article/download/13291/11763/71303) — TRIUMPHS primary-source project | Students work through the iterations from Heath's text |
| Deeper | [Interval Analysis (review)](https://www.science.org/doi/10.1126/science.158.3799.365) — Science 158 (1967), review of R. E. Moore, Prentice-Hall 1966 | The 1966 book that made guaranteed bounds a branch of computing |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
