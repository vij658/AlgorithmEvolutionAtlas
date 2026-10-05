# Tally Marks: the program

*Era 1 · topic 1 · c. 44,000–20,000 years ago* · Book page: [GitHub edition](../../../book/era-01-the-first-algorithms/01-tally-marks/README.md) · [interactive edition](../../../book/era-01-the-first-algorithms/01-tally-marks/tally-marks.html) · [All era 1 programs](../README.md)

## How it works

```text
A tally keeps one mark per thing: one notch per animal, per day, per debt. Nobody needs a word for "seventeen" to
keep it; they only need to add one mark each time. Two collections can be compared the same way, without counting
either one: pair them off one by one, and whichever has things left over is larger. This is one-to-one
correspondence, the idea Cantor made precise in 1878 to compare the sizes of infinite sets.
A tally is also the first append-only log: marks are added, never changed, and the count is the length of the log.
Its weakness is reading. Every mark must be looked at, so a long tally is slow to read, which is the pain that the
next topic (grouping) answers.
```

## What the program does

```text
1. Matching: compares two collections by pairing alone, checked against counting on 200,000 random pairs.
2. The tally as a log: adding marks, replaying the log, and the cost of reading it mark by mark compared with
   reading it in groups of five (a preview of topic 2).
3. The Ishango bone's notch groups as read by Jean de Heinzelin (1962) and listed by the UNESCO portal: column
   totals 60, 48, 60, the primes 11, 13, 17, 19, the groups 10 +/- 1 and 20 +/- 1, and the doubling pairs. Then the
   same marks grouped differently, as the UNESCO listing's own sub-groups allow: the doubling pattern weakens.
4. How surprising are those patterns? Exact counts (no random sampling) under a stated assumption: each group size
   is equally likely to be any number from 3 to 21, the range seen on the bone. Prints how rare the bone's
   combination of patterns would be, and how common it is for random marks to show at least one pattern.
5. The split tally (medieval English Exchequer, abolished 1826): notches cut across a stick that is then split in
   two; a forged notch on one half no longer matches the other.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java TallyMarks.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [A brief history of numerical systems](https://www.youtube.com/watch?v=cZH0YnFpjwU) — TED-Ed (Alessandra King) | Short animation from body-part counting and tally marks to Egyptian and Babylonian numerals |
| Start | [Ishango Bone](https://humanorigins.si.edu/evidence/behavior/recording-information/ishango-bone) — Smithsonian Human Origins | Short museum entry: age, discovery, three rows of tally marks |
| Start | [Ishango Bone](https://nrich.maths.org/problems/ishango-bone) — NRICH, University of Cambridge | Student activity listing the notch groups row by row; stresses that "nobody knows for sure" |
| Start | [When was math invented?](https://www.livescience.com/physics-mathematics/mathematics/when-was-math-invented) — Live Science (2025) | Lebombo to Ishango to Sumerian numerals, with expert caution about origins |
| Deeper | [Lecture 2: Arithmetic (handout)](https://people.math.harvard.edu/~knill/teaching/mathe320_2010/handouts/01-arithmetic.pdf) — Harvard Math E-320, Oliver Knill | Written lecture notes: tallying with sticks, bones, knots and pebbles, through to Egyptian and Babylonian numerals |
| Deeper | [Technical Marvels (2): Lebombo and Ishango Bones](https://cacm.acm.org/blogcacm/technical-marvels-part-2-lebombo-and-ishango-bones) — Communications of the ACM blog | A computing historian on both bones as early notation |
| Deeper | [The Ishango Bone, DR Congo](https://web.astronomicalheritage.net/show-entity?identity=85&idsubentity=1) — UNESCO Portal to the Heritage of Astronomy | Column totals 60, 48, 60, with the counting and lunar readings side by side |
| Scholar | [The first Ishango bone](https://ishango.naturalsciences.be/en/en-ishango-20.html) — RBINS, the holding museum | The museum's own description and its caution about interpretation |
| Scholar | [The fables of Ishango, or the irresistible temptation of mathematical fiction](http://www.bibnum.education.fr/sites/default/files/ishango-analysis_v2.pdf) — Olivier Keller (2010; English 2015) | The main sceptical analysis |
| Scholar | [Does the Ishango Bone Indicate Knowledge of the Base 12?](https://arxiv.org/pdf/1204.1019) — Vladimir Pletser, arXiv | The base-12 reading. Read it alongside Keller |
| Scholar | [The oldest mathematical artefact](https://www.cambridge.org/core/journals/mathematical-gazette/article/abs/7136-the-oldest-mathematical-artefact/65E17776F7EC0D23568F9826F5BC8CDF) — Mathematical Gazette 71 (1987) | The note that named the Lebombo bone the oldest mathematical artefact (preview only) |
| Deeper | [Georg Cantor](https://mathshistory.st-andrews.ac.uk/Biographies/Cantor/) — MacTutor History of Mathematics | 1878: sets of equal power are those in one-to-one correspondence |
| Start | [Tally sticks](https://www.parliament.uk/about/living-heritage/building/palace/estatehistory/from-the-parliamentary-collections/fire-of-westminster/tallysticks/) — UK Parliament | Abolished in 1826; burning them caused the fire of 16 October 1834 |
| Start | [Medieval Exchequer tally sticks](https://collection.sciencemuseumgroup.org.uk/objects/co60506/medieval-exchequer-tally-sticks) — Science Museum Group | A real pair, c. 1440: stock for the lender, foil for the debtor |
| Deeper | [The Log: What every software engineer should know about real-time data's unifying abstraction](https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying) — Jay Kreps, LinkedIn Engineering (2013) | The append-only log as the core of modern data systems |
| Scholar | [Subitizing: An Analysis of Its Component Processes](https://escholarship.org/content/qt9fn27772/qt9fn27772_noSplash_758e0f7f6e6c0393e6eb156f48bd67b2.pdf) — Mandler and Shebo, J. Exp. Psychology: General (1982) | Why small groups are seen at a glance and long rows must be counted |

Every link was opened before it was listed. More, with certainty labels: [Era 1 reference catalog](../../../book/era-01-the-first-algorithms/reference-catalog.md).
