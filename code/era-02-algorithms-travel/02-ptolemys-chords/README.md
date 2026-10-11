# Ptolemy's Table of Chords: the program

*Era 2 · topic 2 · c. 150 CE* · Book page: [GitHub edition](../../../book/era-02-algorithms-travel/02-ptolemys-chords/README.md) · [interactive edition](../../../book/era-02-algorithms-travel/02-ptolemys-chords/ptolemys-chords.html) · [All era 2 programs](../README.md)

## How it works

```text
Astronomy needs the chord of every angle: the straight line across a circle between the ends of an arc. On a circle
of radius 60 (diameter 120, chosen for base-60 arithmetic), the chord of an arc a is 120 sin(a/2), so a table of
chords is a table of sines in disguise. Nobody can measure every chord, so the table is grown from a seed:
  seed      chords known exactly from regular polygons: 36 (decagon), 60 (hexagon), 72 (pentagon), 90 (square),
            120 degrees (triangle);
  rules     the supplement, crd(180 - a) = sqrt(120^2 - crd(a)^2), from the right angle in a semicircle;
            halving, crd(a/2)^2 = 60 (120 - crd(180 - a));
            sums and differences, from Ptolemy's theorem on a quadrilateral in a circle (the diagonals multiplied
            equal the two pairs of opposite sides multiplied and added);
  squeeze   the chord of 1 degree cannot be reached by halving and differences from the seed, so it is pinned
            between the values that 3/4 and 1 1/2 degrees give;
  fill      every half degree from 1/2 to 180 by the sum rule, each entry rounded to seconds (sixtieths of
            sixtieths), with a column of increments for interpolating between entries.
```

## What the program does

```text
1. Checks Ptolemy's theorem on 20,000 random quadrilaterals in a circle.
2. Builds the seed chords and derives 12, 6, 3, 1 1/2 and 3/4 degrees by Ptolemy's route, rounding to seconds at
   every step as a hand computer would, then squeezes the chord of 1 degree and halves it to 1/2 degree.
3. Fills the whole table of 360 entries by adding half a degree at a time, and compares every entry with the true
   chord, rounded to the second.
4. Measures linear interpolation between half-degree entries at every minute of arc, against the rounding error.
5. Recovers Ptolemy's pi (3;8,30) and square root of 3 from the chords.
6. Full circle: computes sin(x) the way the GNU C library does for most arguments, from a table of sines and
   cosines plus the sum rule, and compares it with Java's StrictMath.sin, and with half-degree linear interpolation.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java PtolemyChords.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Incredible Sine Wave and its Uses](https://www.gresham.ac.uk/watch-now/sine-wave) — Gresham College, Sarah Hart, 23 May 2022 (video and transcript) | Hipparchus's lost chord table and how later sine tables were built from half-angle and sum formulas. Context only: Ptolemy is not mentioned |
| Start | [Claudius Ptolemy](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf) — Heinz Klaus Strick, trans. John O'Connor, MacTutor (2020) | The construction step by step: exact chords, halving, differences, interpolation |
| Start | [History of Mathematics: Ptolemy's Theorem](https://parabola.unsw.edu.au/sites/default/files/2024-03/vol43_no1_5.pdf) — Michael A. B. Deakin, *Parabola* 43(1), UNSW (2007) | The theorem behind the sum and difference rules, written for school students |
| Deeper | [Ancient Astronomy, Lecture 1](https://people.sc.fsu.edu/~dduke/lectures/lecture1.pdf) — Florida State University course notes (author not named on the slides; the URL is Dennis Duke's) | Ptolemy's toolkit (chords, base-60 fractions, interpolation) and why the table's authorship is doubted |
| Deeper | [Teaching and Learning the Trigonometric Functions through Their Origins: Episode 3 – Ptolemy Finds High Noon in Chords of Circles](https://old.maa.org/press/periodicals/convergence/teaching-and-learning-the-trigonometric-functions-through-their-origins-episode-3-ptolemy-finds-high) — Daniel E. Otero (Xavier University), MAA *Convergence*, December 2020 | Classroom project: use the chord table and sexagesimal arithmetic to check Ptolemy's noon shadows |
| Deeper | [Ptolemy biography](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/) — MacTutor (O'Connor and Robertson) | Dates, observations, the Crd function and the addition formulas |
| Deeper | [Trigonometric functions](https://mathshistory.st-andrews.ac.uk/HistTopics/Trigonometric_functions/) — MacTutor (O'Connor and Robertson) | From Hipparchus's chords to Ptolemy's polygons, half-arc rule and interpolation |
| Deeper | [Euclid's Elements, Book XIII, Proposition 10](https://mathcs.clarku.edu/~djoyce/elements/bookXIII/propXIII10.html) — David E. Joyce, Clark University | The pentagon's side squared equals the hexagon's plus the decagon's, which gives the seed chord of 72° |
| Scholar | [The Mathematics of the Heavens and the Earth (review)](https://old.maa.org/node/109370) — Rob Bradley, MAA Reviews (2011), on Glen Van Brummelen, Princeton UP 2009 | Points to the standard modern account, which has sections on Ptolemy's chord table, the chord of 1° and the interpolation table |
| Scholar | [Ptolemy's Almagest](https://press.princeton.edu/isbn/9780691002606) — G. J. Toomer (trans.), Princeton University Press, 1998 | The standard English translation, from Heiberg's Greek text (publisher's page) |
| Scholar | [Syntaxis Mathematica](https://catalog.perseus.org/catalog/urn:cts:greekLit:tlg0363.tlg001) — Perseus Catalog record | Heiberg's Greek edition (Teubner, 1898–1903) and Manitius's German translation (1912–13), with links to scans |
| Scholar | [s_sin.c (IBM Accurate Mathematical Library)](https://codebrowser.dev/glibc/glibc/sysdeps/ieee754/dbl-64/s_sin.c.html) — GNU C library source, on codebrowser.dev | `do_sin` combines a sin/cos table with the sum rule; its comment states a worst case of 0.518 units in the last place |
| Scholar | [Vat. lat. 2054](https://ptolemaeus.badw.de/ms/446) — Ptolemaeus Arabus et Latinus, Bavarian Academy of Sciences | George of Trebizond's Latin Almagest, 15th century, with images |

Every link was opened before it was listed. More, with certainty labels: [Era 2 reference catalog](../../../book/era-02-algorithms-travel/reference-catalog.md).
