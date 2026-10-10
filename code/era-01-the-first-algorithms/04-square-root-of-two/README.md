# The Square Root of Two: the program

*Era 1 · topic 4 · c. 1800–1600 BCE* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/04-square-root-of-two/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/04-square-root-of-two/square-root-of-two.html) · [All era 1 programs](../README.md)

## How it works

```text
The tablet shows a square with its diagonals. The side is marked 30, and along the diagonal are two numbers in
base 60: 1;24,51,10 (that is 1 + 24/60 + 51/60^2 + 10/60^3, an approximation of the square root of 2) and
42;25,35 (30 times it, the length of the diagonal). How the scribe got the value is disputed.
One procedure that reaches it is averaging: if g is a guess for the square root of N, then g and N/g lie on
opposite sides of the root, so their average is a better guess. Heron of Alexandria wrote this procedure down in
his Metrica (1st century CE). It is Newton's method for x^2 - N = 0, and each step roughly doubles the number of
correct digits.
```

## What the program does

```text
1. Checks the tablet's arithmetic exactly (30 x 1;24,51,10 = 42;25,35) and measures how close 1;24,51,10 is.
2. Runs the averaging procedure from the guess 1 with exact fractions, shows that the third new guess, 577/408,
   gives the tablet's digits when cut to three base-60 places (but not when rounded), and checks that every guess
   is a continued-fraction convergent of the square root of 2 and solves Pell's equation p^2 - 2q^2 = 1.
3. Counts the steps three methods need for 6, 15, 100 and 1,000 correct digits: halving an interval, the
   digit-by-digit method taught in schools, and averaging.
4. Repeats Heron's own example (the square root of 720 from 27), a division-free variant for 1/sqrt(2), and the
   inverse square root of the Quake III Arena source code: a bit trick plus one Newton step, checked on every
   float from 1 to 4.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java SquareRootOfTwo.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [A Cuneiform Tablet in the Digital Age](https://www.youtube.com/watch?v=Ecm15-TKOBg) — Yale University | Yale's own film about YBC 7289 and its 3D-printed copies |
| Start | [Cuneiform Numbers](https://www.youtube.com/watch?v=RR3zzQP3bII) — Numberphile | What you need to read 1;24,51,10 |
| Start | [Early Mathematics: A Short Introduction](https://www.youtube.com/watch?v=ojvdPjMhnKI) — Gresham College, Robin Wilson | Includes the Mesopotamian √2 approximation |
| Start | [The Best Known Old Babylonian Tablet?](https://old.maa.org/press/periodicals/convergence/the-best-known-old-babylonian-tablet) — MAA Convergence | A novice scribe's practice exercise; √2 correct to three sexagesimal places |
| Deeper | [Lecture 12: Square Roots, Newton's Method](https://www.youtube.com/watch?v=2YeJ-5UAke8) — MIT 6.006 (Srini Devadas), MIT OpenCourseWare | The same iteration used today for high-precision roots, with error and cost analysis |
| Deeper | [YBC 7289 — Analysis](https://personal.math.ubc.ca/~cass/Euclid/ybc/analysis.html) — Bill Casselman, UBC | Works through the numbers on the tablet |
| Deeper | [Babylonian Pythagoras](https://mathshistory.st-andrews.ac.uk/HistTopics/Babylonian_Pythagoras/) — MacTutor | Two candidate methods, and the admission that there is no evidence of the method being used elsewhere |
| Deeper | [Square Roots via Newton's Method](https://math.mit.edu/~stevenj/18.335/newton-sqrt.pdf) — MIT 18.335 note (S. G. Johnson) | Quadratic convergence: correct digits roughly double each step. It dates the Babylonians to "circa 1000 BCE", which is too late for this tablet |
| Scholar | [YBC 07289 (P255048)](https://cdli.earth/artifacts/255048) — CDLI | Catalogue record and transliteration |
| Scholar | [YBC 7289 exhibition label](https://isaw.nyu.edu/exhibitions/before-pythagoras/items/ybc-7289/) — ISAW, NYU | Museum label from *Before Pythagoras* |
| Scholar | [A 3,800-year journey from classroom to classroom](https://news.yale.edu/2016/04/11/3800-year-journey-classroom-classroom) — Yale News | Curators on the tablet and its digitisation |
| Scholar | [Square root approximations in Old Babylonian mathematics: YBC 7289 in context](https://www.sciencedirect.com/science/article/pii/S0315086098922091) — Fowler and Robson, Historia Mathematica 25 (1998) | The standard scholarly study |
| Deeper | [Heron of Alexandria](https://mathshistory.st-andrews.ac.uk/Biographies/Heron/) — MacTutor History of Mathematics | The Metrica's square root of 720, in Heron's words |
| Deeper | [q_math.c, Quake III Arena source](https://github.com/id-Software/Quake-III-Arena/blob/master/code/game/q_math.c) — id Software, on GitHub | Q_rsqrt: a bit-trick guess and one Newton step |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
