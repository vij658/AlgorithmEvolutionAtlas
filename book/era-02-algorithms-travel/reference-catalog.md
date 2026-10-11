# Era 2 — Algorithms Travel: from the Nine Chapters to al-Kashi

*Reference catalog. Eleven developments, from about 200 BCE to 1424 CE.*

> **Field note from the visiting historian.** In the first era, procedures were invented in a few places and written on clay, papyrus and parchment. In this one they travel: from China and India to Baghdad, and from Baghdad to Pisa. Along the way they gain a sign for nothing, a name ("algorithm" comes from al-Khwarizmi), and the first infinite series.

## How to use this catalog

Every link was opened before it was listed. Where a video page could not be opened, no video is listed and the gap is recorded instead. Links are tagged by level, so a high-school reader and a PhD scholar can both find their way in:

| Tag | Meaning |
|---|---|
| **Start** | No background needed. Watch or read this first. |
| **Deeper** | University level: the mechanism, the proof, the analysis. |
| **Scholar** | Primary sources and research papers: the evidence itself, and the arguments about it. |

Each claim also carries a certainty label:

- **Documented**: stated by the holding museum, the primary text, or standard scholarship.
- **Conjecture**: a reasonable reading that the evidence does not settle.
- **Disputed**: scholars disagree; the main positions are given.

The **Atlas** lines will point to the matching chapters of *The Evolutionary Atlas of Algorithms and Data Structures* once mapped. The **Code** lines will point to the tested Java programs as they are written.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Elimination on the counting board (*fangcheng*)](#1-elimination-on-the-counting-board-fangcheng) | *Nine Chapters*, c. 200 BCE – 50 CE (disputed); Liu Hui's commentary 263 CE | Several unknowns tied together by several conditions |
| 2 | [Ptolemy's table of chords](#2-ptolemys-table-of-chords) | *Almagest*, c. 150 CE | Astronomy needs the chord of every angle |
| 3 | [The Chinese remainder problem](#3-the-chinese-remainder-problem) | *Sunzi Suanjing*, 3rd–5th century CE (disputed) | Find a number from its remainders |
| 4 | [Zero becomes a number](#4-zero-becomes-a-number) | Brahmagupta, 628 CE; Gwalior inscription, 876 CE | An empty place needs a sign, and arithmetic needs rules for it |
| 5 | [The chakravala and Pell's equation](#5-the-chakravala-and-pells-equation) | Brahmagupta, 628; Jayadeva (quoted 1073); Bhaskara II, 1150 | Whole-number solutions of x² − Ny² = 1 |
| 6 | [Algorism and al-jabr](#6-algorism-and-al-jabr) | al-Khwarizmi, c. 820–830 CE | Hindu numerals and quadratic problems needed written procedures |
| 7 | [Frequency analysis](#7-frequency-analysis) | al-Kindi, c. 850 CE (estimate) | Reading a cipher without the key |
| 8 | [Fibonacci's *Liber Abaci*](#8-fibonaccis-liber-abaci) | 1202 CE | Merchants reckoned with Roman numerals and counting boards |
| 9 | [Horner's method, nearly six centuries early, and the Da Yan rule](#9-horners-method-nearly-six-centuries-early-and-the-da-yan-rule) | Qin Jiushao, 1247 CE | Roots of higher-degree equations |
| 10 | [Madhava's series for π](#10-madhavas-series-for-π) | c. 1350–1425 CE (Kerala school) | Polygons need more square roots for every digit of π |
| 11 | [al-Kashi's π](#11-al-kashis-π) | 1424 CE | Astronomical tables needed π to more places than ever |

## 1. Elimination on the counting board (*fangcheng*)

**When / where:** Han China. The *Nine Chapters on the Mathematical Art* (*Jiuzhang suanshu*) was compiled from older material somewhere between about 200 BCE and 50 CE (the range is disputed, see below). The method is chapter 8, "Rectangular Arrays" (*fangcheng*). Liu Hui wrote his commentary in 263 CE.
**Atlas:** to be mapped · **Code:** [`FangCheng.java`](../../code/era-02-algorithms-travel/01-fangcheng/) · **Page:** [topic 1](01-fangcheng/README.md)

> **Field note.** The clerks here faced a knot: several unknown quantities tied together by several conditions, so no single condition gives any one unknown. They did not untie it with words. They laid it out. Each condition became a column of rods on the counting board. Then they multiplied one column by the head of another and subtracted, column against column, until the board was triangular and the last unknown fell out. Subtraction sometimes left less than nothing, so they gave such quantities rods of a different colour and rules of their own. My hosts later named this procedure after Gauss, who was born nearly two thousand years after it was written down.

**What hurt:** several unknowns tied together by several conditions. Guessing, or the double false position of chapter 7, does not scale to three, four or six unknowns.
**The step forward:** write the coefficients as columns of rods in a rectangular array and eliminate column against column, keeping whole numbers by cross-multiplying. Negative numbers appear along the way, with their own rules for adding and subtracting.

**Evidence and certainty**

- Chapter 8 has 18 problems that reduce to systems of linear equations, with up to six equations in six unknowns. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/)). All but Problem 13 are determinate systems ([Shen, Crossley and Lun, OUP](https://academic.oup.com/book/52966/chapter/421961670)); Haack identifies one indeterminate system of five equations in six unknowns ([MAA](https://www.maa.org/book/export/html/863323)).
- The coefficients are placed in columns, not rows, and the array is reduced to triangular form by column operations. MacTutor: "Negative numbers are used in the matrix and the chapter includes rules to compute with them." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/))
- Unlike textbook row reduction, each column is multiplied by the leading number of the other before subtracting, so the entries stay whole numbers. To get the modern tableau, rotate the board a quarter turn. **Documented** ([Grcar, arXiv](https://arxiv.org/pdf/0907.2397); [Zhang, Oxford](https://courses.maths.ox.ac.uk/mod/resource/view.php?id=2763))
- Positive and negative numbers were told apart by rod colour, red for positive and black for negative. **Documented** ([Retrospect Journal](https://retrospectjournal.com/?p=2906))
- The date of the text is a range, and sources differ. Most historians put its origin around 200 BCE, others between 100 BCE and 50 AD ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/)). Britannica gives the 1st century BCE to the 1st century CE ([Britannica](https://britannica.com/topic/The-Nine-Chapters-on-the-Mathematical-Procedures)). Following Liu Hui's preface, the version compiled by Zhang Cang and Geng Shouchang dates most likely to around 100 BCE ([Haack, MAA](https://www.maa.org/book/export/html/863323)). The first explicit mention is on bronze standard measures of 179 CE ([Zhang, Oxford](https://courses.maths.ox.ac.uk/mod/resource/view.php?id=2763)). **Disputed**
- Liu Hui's commentary dates from 263 CE ([Retrospect Journal](https://retrospectjournal.com/?p=2906); [Gouvêa, MAA](https://old.maa.org/node/859793) gives about 263 CE). The OUP edition dates his appended *Sea Island* manual to 263 AD ([OUP](https://academic.oup.com/book/52966/chapter/421961680)). **Documented**
- The text survives only through late copies. Chapters 1–5 are known from a 13th-century copy, and chapters 6–9 were reconstructed from 18th-century quotations of a lost 15th-century encyclopedia ([Grcar](https://arxiv.org/pdf/0907.2397)). The earliest surviving edition is the Bao edition of 1213 CE ([Retrospect](https://retrospectjournal.com/?p=2906)). **Documented**
- The name "Gaussian elimination" is modern. Legendre called the method "ordinary" and Gauss called it "common" elimination. Grcar argues that Gauss's name stuck because professional computers adopted his bracket notation for least squares. **Documented** for the older names, **Conjecture** for the explanation ([Grcar](https://arxiv.org/pdf/0907.2397))
- Hart argues that *fangcheng* was a practice of rod manipulation, performed by "illiterate adepts" and recorded by "aspiring literati", and that some Western "discoveries" were known in China 1,000 years earlier. **Conjecture**: this is one author's interpretation ([Grcar's review](https://arxiv.org/pdf/1104.2282); [JHU Press](https://press.jhu.edu/books/title/10232/chinese-roots-linear-algebra))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Histories of Numbers](https://www.gresham.ac.uk/watch-now/numbers-cultures) | Gresham College, Karine Chemla (CNRS), 20 October 2021 | Video and transcript. How Chinese rod numerals existed only as rods laid out on a calculating surface. Background on the board, not on chapter 8 itself |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Illustrating The Nine Chapters on the Mathematical Art: Their Use in a College Mathematics History Classroom](https://www.maa.org/book/export/html/863323) | Joel K. Haack (University of Northern Iowa), MAA; from a 2008 Joint Mathematics Meetings talk | How a college course teaches the book; chapter 8 as "Gaussian elimination" |
| Deeper | [The method of fang cheng, an ancient Chinese algorithm to solve simultaneous equations](https://courses.maths.ox.ac.uk/mod/resource/view.php?id=2763) | Zhuo Zhang (Exeter College), Oxford Mathematical Institute course resource, 2020 | Sets the rod array beside first-year linear-algebra row reduction and pins down the one difference: cross-multiplying instead of dividing |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Nine Chapters on the Mathematical Procedures](https://britannica.com/topic/The-Nine-Chapters-on-the-Mathematical-Procedures) | Encyclopaedia Britannica | Short overview: dates, rods, the chapter on simultaneous equations, negative numbers |
| Start | [Fangcheng Procedure in the Nine Chapters on the Mathematical Arts Revisited](https://retrospectjournal.com/?p=2906) | Kat Jivkova, *Retrospect Journal* (Edinburgh University student history magazine), 2021 | Walks through Problem 1 on the board, red and black rods, back substitution |
| Deeper | [Nine Chapters on the Mathematical Art](https://mathshistory.st-andrews.ac.uk/HistTopics/Nine_chapters/) | MacTutor (O'Connor and Robertson) | All nine chapters, dating, and the column-reduction method of chapter 8 |
| Deeper | [The Chinese Roots of Linear Algebra](https://press.jhu.edu/books/title/10232/chinese-roots-linear-algebra) | Roger Hart, Johns Hopkins University Press, 2011 (publisher's page) | The book-length case that *fangcheng* was a rod-board practice that also yields determinant-style solutions |
| Deeper | [Nine Chapters on the Art of Mathematics (review)](https://old.maa.org/node/859793) | Fernando Q. Gouvêa, MAA Reviews, 2017 | Review of the Guo, Dauben and Xu critical edition and translation (2017) |
| Scholar | [How Ordinary Elimination Became Gaussian Elimination](https://arxiv.org/pdf/0907.2397) | Joseph F. Grcar, arXiv preprint | How the method was done in chapter 8, and how it came to carry Gauss's name |
| Scholar | [The Chinese Roots of Linear Algebra (review)](https://arxiv.org/pdf/1104.2282) | Joseph F. Grcar, arXiv | A review of Hart's thesis by the author of the paper above; the counting board as an ancient "spreadsheet" |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Rectangular Arrays](https://academic.oup.com/book/52966/chapter/421961670) | Shen Kangshen, J. N. Crossley and A. W.-C. Lun, *The Nine Chapters on the Mathematical Art: Companion and Commentary*, OUP 1999 (chapter page) | The standard English translation of chapter 8 with Liu Hui's commentary (paywalled; abstract free) |
| Scholar | [Nine Chapters on the Mathematical Art, Vols 7–9](https://sourcelibrary.org/book/nine-chapters-on-the-mathematical-art-vols-7-9) | Source Library: *Siku Quanshu* edition (1773), scanned by Zhejiang University Library | Chinese text of chapter 8, "Rectangular Arrays", from p. 43. The English shown alongside is a machine translation, so do not cite it |

**Added with the topic page** (each opened before it was listed)

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Linpack Benchmark](https://top500.org/project/linpack/) | TOP500 | The benchmark behind the TOP500 list: a dense linear system by LU factorization with partial pivoting, 2/3 n³ + O(n²) operations |
| Start | [Fangcheng (mathematics)](https://en.wikipedia.org/wiki/Fangcheng_(mathematics)) | Wikipedia | Problem 1's answer, the procedure for positive and negative numbers, and references |
| Start | [Counting rods](https://en.wikipedia.org/wiki/Counting_rods) | Wikipedia | Units upright, tens lying flat; red rods positive, black negative; in use from c. 475 BCE to the 16th century |
| Deeper | [Use of the History of Negative Numbers in Education](https://bibnum.publimath.fr/ACF/ACF11039.pdf) | Lenka Molitorisová, Comenius University, Bratislava | Quotes the cattle, sheep and pigs problem (answer 1200, 500, 300) and Liu Hui on red and black rods, from Shen, Crossley and Lun (1999), p. 405 |
| Deeper | [Bareiss algorithm](https://en.wikipedia.org/wiki/Bareiss_algorithm) | Wikipedia | Fraction-free elimination with exact divisions (Bareiss, *Mathematics of Computation* 22, 1968) |
| Deeper | [The Suan shu shu and the Nine Chapters on the Mathematical Art: A Comparison](https://old.maa.org/sites/default/files/images/upload_library/46/HOMSIGMAA/2021-Megan%20Ferguson.pdf) | Megan Ferguson, Adelphi University, 2021 (MAA HOMSIGMAA) | Quotes Martzloff: "negative numbers are never found in the statements of problems" |
| Scholar | [Alan Turing and the origins of modern Gaussian elimination](https://arbor.revistas.csic.es/index.php/arbor/article/download/1886/2073?inline=1) | Froilán M. Dopico, *Arbor* 189 (764), 2013 | Turing (1948) named the LU factorization and introduced the condition number; Wilkinson named partial pivoting; growth is "almost invariably found to be small" |
| Scholar | [John von Neumann's Analysis of Gaussian Elimination and the Origins of Modern Numerical Analysis](https://epubs.siam.org/doi/10.1137/080734716) | Joseph F. Grcar, *SIAM Review* 53(4), 2011, 607–682 | Von Neumann and Goldstine's work as "the first modern paper in numerical analysis" (abstract free) |
| Scholar | [The Chinese Rod Numeral Legacy and its Impact on Mathematics](https://sms.math.nus.edu.sg/smsmedley/Vol-15-2/The%20Chinese%20rod%20numeral%20legacy%20and%20its%20impact%20on%20mathematics(Lam%20Lay%20Yong).pdf) | Lam Lay Yong, presidential address, Singapore Mathematical Society, 1987 | Two sets of rod notations alternating by place; a horizontal rod for five |

**Gaps:** YouTube watch pages could not be opened in this environment (three attempts, all fetch errors), so no YouTube video is listed. The Gresham page above embeds its video. The Chinese Text Project (ctext.org) returned only a security-check page, and Project MUSE returned a verification page, so neither is listed. MacTutor's Liu Hui biography returned content that did not match the page, so it was left out. The arXiv copy of Grcar's paper does not name the journal it appeared in, so it is cited as a preprint. No scholarly translation of the rules for signed numbers (*zheng fu shu*) could be opened in full: the topic page uses Wikipedia's wording and Liu Hui's commentary as quoted by Molitorisová (from Shen, Crossley and Lun, p. 405).

---

---

## 2. Ptolemy's table of chords

**When / where:** Claudius Ptolemy, Alexandria. The table is in Book I of the *Almagest* (*Syntaxis mathematica*), written after his dated observations of 127–141 CE and usually placed about 150 CE.
**Atlas:** to be mapped · **Code:** [`PtolemyChords.java`](../../code/era-02-algorithms-travel/02-ptolemys-chords/) · **Page:** [topic 2](02-ptolemys-chords/README.md)

> **Field note.** The sky-watchers of Alexandria had a geometry problem they met a thousand times a night: given an angle at the centre of a circle, how long is the chord across it? Measuring every chord is impossible, so Ptolemy computed them, in a way I now recognise as an algorithm with a seed and a set of growth rules. The seed is a few chords known exactly from the triangle, square, pentagon, hexagon and decagon. The rules are halving an arc and taking sums and differences of two arcs. Between the entries, a third column tells the reader how much to add for each part of a step. With that, a 360-row table could be built by hand and used for centuries.

**What hurt:** astronomy needs the chord (in effect, the sine) of every angle, and there is no way to measure them all.
**The step forward:** start from a few exact chords, generate the rest with half-arc and sum/difference rules, tabulate at half-degree steps in base 60 on a circle of radius 60, and interpolate linearly between entries.

**Evidence and certainty**

- Ptolemy observed at Alexandria from 26 March 127 to 2 February 141 CE, and the *Almagest* is the earliest of his works ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/)). Course notes date the *Almagest* to 150 ([FSU lecture](https://people.sc.fsu.edu/~dduke/lectures/lecture1.pdf)), and *Convergence* says "second century CE" ([Otero, MAA](https://old.maa.org/press/periodicals/convergence/teaching-and-learning-the-trigonometric-functions-through-their-origins-episode-3-ptolemy-finds-high)). **Documented**, with "c. 150" as an approximation
- Ptolemy's life dates differ even within MacTutor: about 85–165 CE in the biography ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/)), about 100–170 CE in Strick's article ([MacTutor/Strick](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf)). **Disputed**
- The table gives chords for arcs from ½° to 180° in steps of ½° ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf); [Otero](https://old.maa.org/press/periodicals/convergence/teaching-and-learning-the-trigonometric-functions-through-their-origins-episode-3-ptolemy-finds-high)). The diameter is divided into 120 parts ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Trigonometric_functions/)), so the radius is 60, chosen for sexagesimal arithmetic ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf)). The chord relates to the sine by sin a = Crd 2a / 120 ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/)). **Documented**
- The seed chords come from the inscribed triangle, square, pentagon, hexagon and decagon ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Trigonometric_functions/)). Halving gives 30°, 15°, 7½° and 3¾°, and a difference formula gives Crd 6° from 36° − 30° ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf)). The sum and difference rules, analogous to sin(a ± b), come from Ptolemy's theorem on cyclic quadrilaterals ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/); [Deakin, Parabola](https://parabola.unsw.edu.au/sites/default/files/2024-03/vol43_no1_5.pdf)). **Documented**
- After deriving Crd 1½° and Crd ¾°, Ptolemy obtains the chord of 1° by interpolating between them ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf); a separate section, "The Chord of 1°", in [Van Brummelen's book](https://old.maa.org/node/109370)). MacTutor gives Ptolemy's value for half a degree as 0;31,25, correct to six decimal places when converted ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Trigonometric_functions/)). **Documented**
- A third column gives the increments used to interpolate between the half-degree entries ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf)). **Documented**
- With the chords he obtained π ≈ 3 17/120 ≈ 3.14166 and √3 ≈ 1.73205 ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/)). **Documented**
- Hipparchus made the first known chord table, around 140 BCE. It is lost; MacTutor reports the claim that he wrote twelve books of chord tables ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Trigonometric_functions/); [Hart, Gresham](https://www.gresham.ac.uk/watch-now/sine-wave)). **Documented** that it existed and is lost; **Conjecture** for its contents
- Whether Hipparchus and Menelaus already used Ptolemy's theorem: Deakin reports that Toomer doubts it and suggests they used simpler methods ([Parabola](https://parabola.unsw.edu.au/sites/default/files/2024-03/vol43_no1_5.pdf)). **Disputed**
- Whether Ptolemy computed the table himself, by the methods he describes: the FSU notes say there is good reason to think it was not computed that way or by him, and that there is no evidence of who did compute it ([FSU lecture](https://people.sc.fsu.edu/~dduke/lectures/lecture1.pdf)). **Disputed**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Incredible Sine Wave and its Uses](https://www.gresham.ac.uk/watch-now/sine-wave) | Gresham College, Sarah Hart, 23 May 2022 (video and transcript) | Hipparchus's lost chord table and how later sine tables were built from half-angle and sum formulas. Context only: Ptolemy is not mentioned |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Ancient Astronomy, Lecture 1](https://people.sc.fsu.edu/~dduke/lectures/lecture1.pdf) | Florida State University course notes (author not named on the slides; the URL is Dennis Duke's) | Ptolemy's toolkit (chords, base-60 fractions, interpolation) and why the table's authorship is doubted |
| Deeper | [Teaching and Learning the Trigonometric Functions through Their Origins: Episode 3 – Ptolemy Finds High Noon in Chords of Circles](https://old.maa.org/press/periodicals/convergence/teaching-and-learning-the-trigonometric-functions-through-their-origins-episode-3-ptolemy-finds-high) | Daniel E. Otero (Xavier University), MAA *Convergence*, December 2020 | Classroom project: use the chord table and sexagesimal arithmetic to check Ptolemy's noon shadows |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Claudius Ptolemy](https://mathshistory.st-andrews.ac.uk/Strick/ptolemy.pdf) | Heinz Klaus Strick, trans. John O'Connor, MacTutor (2020) | The construction step by step: exact chords, halving, differences, interpolation |
| Start | [History of Mathematics: Ptolemy's Theorem](https://parabola.unsw.edu.au/sites/default/files/2024-03/vol43_no1_5.pdf) | Michael A. B. Deakin, *Parabola* 43(1), UNSW (2007) | The theorem behind the sum and difference rules, written for school students |
| Deeper | [Ptolemy biography](https://mathshistory.st-andrews.ac.uk/Biographies/Ptolemy/) | MacTutor (O'Connor and Robertson) | Dates, observations, the Crd function and the addition formulas |
| Deeper | [Trigonometric functions](https://mathshistory.st-andrews.ac.uk/HistTopics/Trigonometric_functions/) | MacTutor (O'Connor and Robertson) | From Hipparchus's chords to Ptolemy's polygons, half-arc rule and interpolation |
| Scholar | [The Mathematics of the Heavens and the Earth (review)](https://old.maa.org/node/109370) | Rob Bradley, MAA Reviews (2011), on Glen Van Brummelen, Princeton UP 2009 | Points to the standard modern account, which has sections on Ptolemy's chord table, the chord of 1° and the interpolation table |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Ptolemy's Almagest](https://press.princeton.edu/isbn/9780691002606) | G. J. Toomer (trans.), Princeton University Press, 1998 | The standard English translation, from Heiberg's Greek text (publisher's page) |
| Scholar | [Syntaxis Mathematica](https://catalog.perseus.org/catalog/urn:cts:greekLit:tlg0363.tlg001) | Perseus Catalog record | Heiberg's Greek edition (Teubner, 1898–1903) and Manitius's German translation (1912–13), with links to scans |

**Added with the topic page** (each opened before it was listed)

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Euclid's Elements, Book XIII, Proposition 10](https://mathcs.clarku.edu/~djoyce/elements/bookXIII/propXIII10.html) | David E. Joyce, Clark University | The pentagon's side squared equals the hexagon's plus the decagon's: the seed chord of 72° |
| Scholar | [s_sin.c (IBM Accurate Mathematical Library)](https://codebrowser.dev/glibc/glibc/sysdeps/ieee754/dbl-64/s_sin.c.html) | GNU C library source, on codebrowser.dev | `do_sin` combines a sin/cos table with the sum rule; its comment states a worst case of 0.518 units in the last place |
| Scholar | [Vat. lat. 2054](https://ptolemaeus.badw.de/ms/446) | Ptolemaeus Arabus et Latinus, Bavarian Academy of Sciences and Humanities | George of Trebizond's 15th-century Latin *Almagest*, a paper codex of 235 folios, with images |
| Scholar | [Ptolemy, Almagest (Syntaxis Mathematica), Vat. gr. 1594](https://sourcelibrary.org/book/vat-gr-1594-ptolemy) | Source Library, from the Vatican Library's digitization | A Greek manuscript dated about 900 in its record. The English shown is an AI translation, and the page's licence fields conflict |

**Gaps:** YouTube watch pages could not be opened in this environment (fetch errors on every attempt), so no YouTube video is listed, including "Ptolemy and Trigonometry, Part One", which turned up in search. Van Brummelen's book itself was not opened, only the MAA review and its table of contents. An Internet Archive scan of Heiberg's *Opera* (1898) was opened, but the page did not say which volume it holds, so it is not listed. A 19th-century tract on the history of trigonometric tables (Düsseldorf University Library PDF) describes the three-column table, but its author and date could not be confirmed, so it is not listed. The exact Ptolemaic inequality used to bound Crd 1° is not quoted, because no opened page states it.

---

---

## 3. The Chinese remainder problem

**When / where:** China. The *Sunzi Suanjing* (*Master Sun's Mathematical Classic*), Volume 3, Problem 26. The book's date is uncertain: modern sources place it anywhere from the 3rd to the 5th century CE. The general method came later, in Qin Jiushao's *Shushu jiuzhang* (1247).
**Atlas:** to be mapped · **Code:** [`ChineseRemainder.java`](../../code/era-02-algorithms-travel/03-chinese-remainder-problem/) · **Page:** [topic 3](03-chinese-remainder-problem/README.md)

> **Field note.** A short puzzle in a Chinese primer turned out to hold a whole method. Count some things by threes and two are left; by fives, three; by sevens, two. How many things? Master Sun did not search. He kept three ready-made numbers, 70, 21 and 15. Each is a multiple of the other two divisors that leaves remainder 1 for its own. Multiply each remainder by its number, add, and cast out 105. Eight centuries later Qin Jiushao, who said he learned the rule from the calendar-makers, made it work for any divisors. He found the magic multipliers by a chain of divisions that my hosts would recognise as Euclid's algorithm run backwards.

**What hurt:** finding a number from its remainders. Calendar-makers needed a moment when several cycles (days, months, years) line up, and trying every candidate is hopeless when the cycles are long.
**The step forward:** combine the remainders with precomputed multipliers, each a multiple of the other moduli that leaves remainder 1 for its own modulus, then reduce by the product of the moduli. Qin Jiushao's *dayan* rule computes those multipliers for any moduli.

**Evidence and certainty**

- The problem, in MacTutor's translation: "Suppose we have an unknown number of objects. When counted in threes, 2 are left over, when counted in fives, 3 are left over, and when counted in sevens, 2 are left over. How many objects are there?" The answer is 23. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Sun_Zi/)). The Chinese text begins 「今有物不知其數」 ([PolyU lecture notes](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf); [Wang Yixun, 數學傳播](https://web.math.sinica.edu.tw/media/pdf/d353/35308.pdf))
- The worked answer multiplies the remainders out to 140, 63 and 30, which add to 233, and subtracts 210 to reach 23 ([Occidental worksheet](https://sites.oxy.edu/ron/math/400/19/ws/ws11.pdf); [PolyU](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf)). The general rule follows, with multipliers 70, 21 and 15: "If the answer is 106 or more then subtract multiples of 105." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Sun_Zi/))
- Why the multipliers work: 70 is a multiple of 5 × 7 that leaves 1 when divided by 3, 21 is a multiple of 3 × 7 that leaves 1 when divided by 5, and 15 is a multiple of 3 × 5 that leaves 1 when divided by 7. **Documented** ([PolyU](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf))
- The date of the *Sunzi Suanjing* is contested. MacTutor lists estimates from about 250 BC (Ruan Yuan) and the 1st century AD (Dickson) to after 280 AD (Wang Ling), and notes that, taken as a whole, the text "cannot be older than 473 AD" ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Sun_Zi/)). Other sources give the 3rd century AD ([Britannica](https://www.britannica.com/print/article/112749); [Sury, Resonance](https://link.springer.com/doi/10.1007/s12045-015-0171-x)), about 300 CE ([Occidental](https://sites.oxy.edu/ron/math/400/19/ws/ws11.pdf); [Knill](https://legacy-www.math.harvard.edu/~knill/seminars/chinese/chinese.pdf)), the 4th century ([Libbrecht](https://legacy-www.math.harvard.edu/~knill/crt/lib/Libbrecht14.pdf), with a question mark; [Wang](https://web.math.sinica.edu.tw/media/pdf/d353/35308.pdf)), the 4th–5th century ([PolyU](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf)) and about the 5th century ([Project Gutenberg](https://m.gutenberg.org/ebooks/24038)). MacTutor suggests the book was compiled from older sources of different dates. **Disputed**
- Qin Jiushao (1202–1261) wrote the *Shushu jiuzhang* in 1247 ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/)). Its *dayan qiuyi* rule is an algorithm for solving ax ≡ 1 (mod b), which yields the multipliers ([Shen 1988](https://link.springer.com/doi/10.1007/BF00357063), [PDF](https://www.ms.uky.edu/~sohum/ma330/files/CRT_history_Kangsheng.pdf); [PolyU](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf)). Britannica: "the complete theorem was first given in 1247 by Qin Jiushao." **Documented**
- Qin also handled moduli that are not pairwise coprime, by replacing them with coprime ones that give the same solution ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/); [Libbrecht](https://legacy-www.math.harvard.edu/~knill/crt/lib/Libbrecht14.pdf)). **Documented**
- Calendars: first-degree congruences were needed for Chinese calendar computation, for example to find the *shangyuan* epoch of the Jingchu calendar (237 AD) ([Shen 1988](https://www.ms.uky.edu/~sohum/ma330/files/CRT_history_Kangsheng.pdf)). Qin says he learned the method from calendar experts at the Board of Astronomy ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/)). **Documented**. That Sunzi's own puzzle grew out of calendar work is **Conjecture**: no source opened here says so directly
- In India, Aryabhata published his work about a century after the *Sunzi Suanjing* ([Shen 1988](https://www.ms.uky.edu/~sohum/ma330/files/CRT_history_Kangsheng.pdf)), and his 5th-century mathematics contains instances of the theorem ([Sury](https://link.springer.com/doi/10.1007/s12045-015-0171-x)). **Documented**
- The Western name: in 1874 L. Mathiesen pointed out that Sunzi's method matches Gauss's result, which is why Western histories call it the Chinese remainder theorem ([PolyU](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf)). The multipliers were later set to verse in Cheng Dawei's *Suanfa tongzong* (1592) ([PolyU](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf); [Wang](https://web.math.sinica.edu.tw/media/pdf/d353/35308.pdf)). **Documented**, each from a single opened source

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Histories of Numbers](https://www.gresham.ac.uk/watch-now/numbers-cultures) | Gresham College, Karine Chemla (CNRS), 20 October 2021 (video and transcript) | The *Sunzi Suanjing* as the text that explains rod numerals on a calculating surface; Qin Jiushao's *Shu shu jiu zhang*. The remainder problem itself is not discussed |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Chinese Remainder Theorem](https://legacy-www.math.harvard.edu/~knill/seminars/chinese/chinese.pdf) | Oliver Knill, Math Circle slides, Harvard, 15 April 2014 | Sunzi's problem worked visually, with a timeline to Qin Jiushao's "full algorithm" |
| Start | [Non-Western Perspectives, Part 2: Mathematics from China and Africa (Worksheet 11)](https://sites.oxy.edu/ron/math/400/19/ws/ws11.pdf) | Senior Colloquium: History of Mathematics, worksheet (Fall 2019), Occidental College site; instructor not named | Students rework Sunzi's 140 + 63 + 30 − 210 solution |
| Deeper | [Chinese Remainder Theorem (中國剩餘定理), Lecture Notes Set #04, AMA1D01C](https://polyu.edu.hk/ama/profile/hwlee/AMA1D01C/lec04.pdf) | Hong Kong Polytechnic University, Dept. of Applied Mathematics (in Chinese) | The original Chinese text, why 70/21/15 work, and Qin's *dayan qiuyi* procedure with worked examples |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Chinese remainder theorem](https://www.britannica.com/print/article/112749) | Encyclopaedia Britannica | Short statement of the theorem, Sun Zi and Qin Jiushao |
| Deeper | [Sun Zi](https://mathshistory.st-andrews.ac.uk/Biographies/Sun_Zi/) | MacTutor | The problem and the rule in translation, and the full argument over dating |
| Deeper | [Qin Jiushao](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/) | MacTutor | The 1247 generalisation, non-coprime moduli, and the calendar experts |
| Scholar | [Historical development of the Chinese remainder theorem](https://link.springer.com/doi/10.1007/BF00357063) | Shen Kangsheng, *Archive for History of Exact Sciences* 38(4) (1988) 285–305 | The standard history, from calendars to Qin's *dayan* rule. A full-text [PDF](https://www.ms.uky.edu/~sohum/ma330/files/CRT_history_Kangsheng.pdf) is on a University of Kentucky course page |
| Scholar | [Indeterminate Analysis of the First Degree outside China (Ch. 14)](https://legacy-www.math.harvard.edu/~knill/crt/lib/Libbrecht14.pdf) | Ulrich Libbrecht, *Chinese Mathematics in the Thirteenth Century* (PDF on Knill's Harvard CRT site) | Sunzi to Qin compared with India and Fibonacci, who solved congruences case by case |
| Scholar | [Multivariable Chinese remainder theorem](https://link.springer.com/doi/10.1007/s12045-015-0171-x) | B. Sury, *Resonance* 20(3) (2015) 206–216 | History in the abstract (Sunzi, calendars, Aryabhata, Qin), then generalisations |
| Scholar | [孫子剩餘定理與高斯剩餘定理](https://web.math.sinica.edu.tw/media/pdf/d353/35308.pdf) | Wang Yixun, *數學傳播* 35(3) (2011) 64–79, Academia Sinica (in Chinese) | Quotes the original problem and rule in full and compares them with Gauss's method |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [孫子算經 (Sunzi Suan Jing)](https://m.gutenberg.org/ebooks/24038) | Project Gutenberg eBook #24038 (Chinese text; the catalogue lists Li Chunfeng, 602–670) | The whole book in Chinese. The remainder problem is Volume 3 (下), Problem 26 |

**Added with the topic page** (each opened before it was listed)

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [RFC 8017: PKCS #1: RSA Cryptography Specifications Version 2.2](https://rfc-editor.org/rfc/rfc8017) | K. Moriarty (ed.), B. Kaliski, J. Jonsson, A. Rusch, November 2016 | Section 3.2 stores the private key as p, q, dP, dQ, qInv; section 5.1.2 decrypts by the remainder theorem |

Shen (1988) also gives a calendar congruence from Qin's book, 377873 x ≡ 1 (mod 499067), with the answer 457999; the topic's program reproduces it with the dayan rule.

**Gaps:** YouTube watch pages could not be opened in this environment, so no YouTube video is listed. The Chinese Text Project (ctext.org) returned only a security-check page. The Gutenberg catalogue page was opened, but the e-text itself could not be fetched, so the presence of Problem 26 in that copy was not checked directly. No English translation of the whole *Sunzi Suanjing* was found online. Lam Lay Yong and Ang Tian Se's *Fleeting Footsteps* is the usual one, and it was not searched. The PDF copy of Shen (1988) does not show the journal, so the citation comes from Springer's page. The Mathiesen 1874 attribution rests on one source.

---

---

## 4. Zero becomes a number

**When / where:** India. Brahmagupta (598–670) wrote the *Brahmasphutasiddhanta* at Bhillamala (modern Bhinmal) in 628 CE. A stone inscription at a temple in Gwalior is dated 933 in an era beginning in 57 BCE, that is 876 CE. It is the earliest dated Indian zero that everyone accepts.
**Atlas:** to be mapped · **Code:** [`ZeroAsANumber.java`](../../code/era-02-algorithms-travel/04-zero-becomes-a-number/) · **Page:** [topic 4](04-zero-becomes-a-number/README.md)

> **Field note.** For more than a thousand years the Babylonians wrote place-value numbers without any mark for an empty place, and readers guessed from context. When a placeholder finally came, it was a separator, not a number: nobody added it or multiplied by it. In India the mark became a number. In 628 Brahmagupta wrote down rules for zero next to rules for "fortunes" and "debts", which my hosts now call positive and negative numbers. Two centuries later a temple grant at Gwalior wrote 270 and 50 with a small round 0, in a form any modern child could read. His rule that zero divided by zero is zero was later rejected, and my hosts still give that case no value at all.

**What hurt:** place value needs a mark for an empty place, and arithmetic needs rules for what that mark does under addition, subtraction, multiplication and division.
**The step forward:** zero as a digit in a place-value numeral, and as a number with its own arithmetic. Brahmagupta's rules treat it alongside positive and negative numbers.

**Evidence and certainty**

- Brahmagupta lived 598–670 and wrote the *Brahmasphutasiddhanta* in 628 at Bhillamala. He defined zero as a number subtracted from itself and gave rules such as "A debt minus zero is a debt.", "Zero minus zero is a zero." and "The product of zero multiplied by a debt or fortune is zero." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/))
- Brahmagupta's division rules: a positive or negative number divided by zero is a fraction with zero as denominator, and "Zero divided by zero is zero." MacTutor calls the latter incorrect. **Documented** ([MacTutor, Brahmagupta](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/); [MacTutor, Zero](https://mathshistory.st-andrews.ac.uk/HistTopics/Zero/))
- Before India, the Babylonians used no mark for an empty place for over 1,000 years. Around 400 BC they began using two wedges as a placeholder, but never at the end of a number. **Documented** ([MacTutor, Zero](https://mathshistory.st-andrews.ac.uk/HistTopics/Zero/))
- Gwalior: the inscription records a garden of 187 by 270 *hastas* and a daily gift of 50 garlands to the temple. MacTutor calls it the earliest dated Indian record of zero that all agree is genuine. Its date is 933 in an era starting in 57 BC, and the temple is dated to 876 AD ([Casselman, AMS](https://www.ams.org/publicoutreach/feature-column/fcarc-india-zero); [MacTutor, Zero](https://mathshistory.st-andrews.ac.uk/HistTopics/Zero/)). The date follows Hultzsch's 1883 translation ([MAA](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-indian-zeros); [Scientific American](https://www.scientificamerican.com/article/the-elusive-origin-of-zero1/)). **Documented**
- "Oldest zero": Southeast Asian stone inscriptions are two centuries older than Gwalior. The Cambodian stele K-127, found in 1891 (near Sambor, according to *Scientific American*), is dated Khmer year 604, which Swetz gives as 682–683 CE ([MAA Convergence](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-the-cambodian-zero), updated 2024). A *Scientific American* opinion piece by Swetz and Zain reads the year as 605, i.e. 685 CE, and dates three Sumatran stones to 683, 684 and 686 ([Scientific American](https://www.scientificamerican.com/article/the-elusive-origin-of-zero1/)). The Smithsonian still called Gwalior "the oldest known representation of the circular symbol for nothing" in 2013 ([Smithsonian](https://www.smithsonianmag.com/smart-news/you-can-visit-the-worlds-oldest-zero-at-a-temple-in-india-2120286/)). **Disputed** (exact year of K-127; which is "oldest")
- Bakhshali manuscript: in 2017 Oxford announced radiocarbon dates showing it is "as early as the 3rd or 4th century", against Hayashi's earlier estimate of the 8th to 12th century ([Oxford GLAM](https://www.glam.ox.ac.uk/node/218481)). The three tested folios gave CE 224–383, 680–779 and 885–993, and specialists hold that the manuscript was written at one time, most likely in the 9th–10th century ([MAA](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-indian-zeros)). Plofker, Keller, Hayashi, Montelle and Wujastyk argue that the latest dateable folio, not the earliest, dates the copying ([HSSA 2017](https://journals.library.ualberta.ca/hssa/index.php/hssa/article/view/22)). **Disputed**. Recommendation for the plan's open question: keep Bakhshali in this topic's notes, not in its date line
- The Bakhshali dot was a placeholder; Oxford says it later "evolved to have a hollow centre" and became our 0 ([Oxford GLAM](https://www.glam.ox.ac.uk/node/218481)). Plofker et al. argue that its zeros already work as arithmetical operators, not only as placeholders ([HSSA](https://journals.library.ualberta.ca/hssa/index.php/hssa/article/view/22)). **Disputed**
- Earlier Indian placeholder zeros (as early as 200 AD) are claimed by some historians and dismissed by others as later forgeries ([MacTutor, Zero](https://mathshistory.st-andrews.ac.uk/HistTopics/Zero/)). **Disputed**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Much ado about zero](https://www.gresham.ac.uk/watch-now/much-ado-about-zero) | Gresham College, Robin Wilson, 17 November 2004 (embedded video) | Mathematics of China, India and Central America over a thousand years, ending with "the elusive origins of zero" |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Where do mathematical symbols come from?](https://www.gresham.ac.uk/sites/default/files/2021-04-27-1300_HART_Symbols-T.pdf) | Gresham College, Sarah Hart, 27 April 2021 (transcript) | Babylonian placeholder versus zero as a number in Brahmagupta (dated "around 630AD" in the talk) |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [You Can Visit the World's Oldest Zero at a Temple in India](https://www.smithsonianmag.com/smart-news/you-can-visit-the-worlds-oldest-zero-at-a-temple-in-india-2120286/) | Colin Schultz, *Smithsonian Magazine*, 16 October 2013 | Photo of the Gwalior "270" and the popular "oldest zero" story |
| Start | [The Elusive Origin of Zero](https://www.scientificamerican.com/article/the-elusive-origin-of-zero1/) | Swetz and Zain, *Scientific American* (opinion; undated on the page) | The Southeast Asian challenge to Gwalior: Sambor and the Sumatran stones |
| Start | [Mathematical Treasure: Indian Zeros](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-indian-zeros) | MAA *Convergence* | Gwalior's 270, and the three Bakhshali radiocarbon ranges with the specialists' reading of them |
| Deeper | [A history of Zero](https://mathshistory.st-andrews.ac.uk/HistTopics/Zero/) | MacTutor (O'Connor and Robertson) | From Babylonian wedges to Brahmagupta's rules and Gwalior |
| Deeper | [Brahmagupta](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/) | MacTutor (O'Connor and Robertson) | The rules for fortunes, debts and zero, quoted in translation |
| Deeper | [All for Nought](https://www.ams.org/publicoutreach/feature-column/fcarc-india-zero) | Bill Casselman (UBC), AMS Feature Column, February 2007 | A translation of the Gwalior inscription with its numbers 933, 187, 270 and 50, and why it fixes a date for the zero |
| Deeper | [Mathematical Treasure: The Cambodian Zero](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-the-cambodian-zero) | Frank J. Swetz (Penn State), MAA *Convergence*, 2015 (updated 2024) | Stele K-127, the zero two centuries older than Gwalior |
| Scholar | [The Bakhshālī Manuscript: A Response to the Bodleian Library's Radiocarbon Dating](https://journals.library.ualberta.ca/hssa/index.php/hssa/article/view/22) | Plofker, Keller, Hayashi, Montelle and Wujastyk, *History of Science in South Asia* 5(1) (2017) 134–150 | The specialists' case against reading the earliest folio date as the date of the text |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Algebra, with Arithmetic and Mensuration, from the Sanscrit of Brahmegupta and Bháscara](https://archive.org/details/algebrawitharith00brahuoft/page/n5/mode/2up) | H. T. Colebrooke (trans.), London: J. Murray, 1817, Internet Archive | The classic English translation of Brahmagupta's arithmetic and algebra, the source of his rules for zero |
| Scholar | [Carbon dating finds Bakhshali manuscript contains oldest recorded origins of the symbol 'zero'](https://www.glam.ox.ac.uk/node/218481) | University of Oxford, Gardens, Libraries and Museums, 14 September 2017 | The original announcement that started the dispute |

**Added with the topic page** (each opened before it was listed)

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [1/0 = 0](https://hillelwayne.com/post/divide-by-zero/) | Hillel Wayne (10 August 2018; disclaimer added 2024) | Lean and Isabelle define 1/0 = 0, and Coq too; why this is consistent with the field axioms |

**Gaps:** YouTube watch pages could not be opened in this environment, so no YouTube video is listed. The Gresham page embeds its video, but the video itself was not checked. Oxford's research news page on the same announcement was blocked to the fetcher (robots.txt). The Internet Archive page for Colebrooke's 1817 translation does not list its contents, so the chapter numbers of Brahmagupta's zero rules are not given here. No Sanskrit edition of the *Brahmasphutasiddhanta* was found. The *Scientific American* piece shows no date or full author names, and its 685 CE for Sambor conflicts with Swetz's later 682–683 CE. The Oxford page also mentions a paper due "in 2024", which does not fit a 2017 release; this was not resolved. The Mathematical Treasure: Indian Zeros page names no author.

---

---

## 5. The chakravala and Pell's equation

**When / where:** India. Brahmagupta's *Brahmasphutasiddhanta* (628 CE, written at Bhillamala, modern Bhinmal) gives the composition rule (*bhavana*). The full cyclic method (*chakravala*) is first known from Jayadeva, whose verses are quoted in Udayadivakara's commentary *Sundari* of 1073. Bhaskara II (1114–1185), head of the observatory at Ujjain, sets it out in his *Bijaganita* (1150 CE).
**Atlas:** to be mapped · **Code:** [`Chakravala.java`](../../code/era-02-algorithms-travel/05-chakravala/) · **Page:** [topic 5](05-chakravala/README.md)

> **Field note.** The task is to find whole numbers with x² − Ny² = 1. My sources write it Nx² + 1 = y², with the letters swapped. Guessing is hopeless: for N = 61 the smallest answer is x = 1,766,319,049. Brahmagupta noticed that two near-misses can be multiplied into a new near-miss, so a near-miss that is off by 1, 2 or 4 can be turned into an exact answer. Later Indian mathematicians closed the loop. Choose a multiplier that keeps the error small, compose, divide out, and repeat. The cycle always ends, though Bhaskara II probably could not prove it: the proof came six centuries later, in Europe. Europeans met the same equation five hundred years after Bhaskara and named it after John Pell, by what their own historians call a mix-up.

**What hurt:** whole-number solutions of x² − Ny² = 1 can be enormous, so trial and error fails. Brahmagupta's composition finishes the job only once someone has a near-solution with error ±1, ±2 or ±4.
**The step forward:** first, composition (*bhavana*), which builds new solutions out of old ones. Then the *chakravala* adds a cyclic step: from a triple (a, b, k) with a² − Nb² = k, choose m so that k divides a + bm and |m² − N| is small, compose, and divide by k. Repeat until k is ±1, ±2 or ±4, then finish by composition. Selenius (1975) argued that it is a shortest-possible algorithm of the continued-fraction type.

**Evidence and certainty**

- Brahmagupta (598–670) wrote the *Brahmasphutasiddhanta* in 628 at Bhillamala and later headed the Ujjain observatory. **Documented** ([MacTutor, Brahmagupta](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/))
- The composition rule is Brahmagupta's. MacTutor: "Brahmagupta's lemma was discovered by Brahmagupta in 628 AD". Dutta: "Brahmagupta is the first known mathematician to state (in 628) a non-trivial principle of composition." **Documented** ([MacTutor, Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell); [Dutta, *Bhāvanā* 2017](https://bhavana.org.in/the-bhavana-in-mathematics/))
- Brahmagupta's method works only once a solution with k = ±1, ±2 or ±4 is known. Selenius therefore treats it as separate from the general chakravala. **Documented** ([Selenius 1975](https://www.ms.uky.edu/~sohum/ma330/files/Rationale-of-the-chakrav-la-process-of-Jayadeva-and-Bh-skara-II_1975_Historia-Mathematica.pdf))
- Brahmagupta's example N = 92 is solved (x = 120, y = 1151) in two compositions. Dutta quotes Brahmagupta's boast: "One who can solve it within a year [is truly a] mathematician." **Documented** ([Dutta](https://bhavana.org.in/the-bhavana-in-mathematics/))
- Jayadeva is the earliest known expositor of the chakravala. His verses survive only as quotations in the *Sundari* (1073). **Documented** ([Dutta](https://bhavana.org.in/the-bhavana-in-mathematics/); [Selenius](https://www.ms.uky.edu/~sohum/ma330/files/Rationale-of-the-chakrav-la-process-of-Jayadeva-and-Bh-skara-II_1975_Historia-Mathematica.pdf)). His own dates are estimates: Selenius puts him about 1000 or earlier, at least a century before Bhaskara II, and Wikipedia gives c. 950–1000. **Conjecture** ([Wikipedia, Chakravala method](https://en.wikipedia.org/wiki/Chakravala_method))
- The plan credits the cyclic step to Bhaskara II, but the sources above credit Jayadeva with it first, and Dutta calls Bhaskara II's version a variant of Jayadeva's. **Documented** (Dutta). Bhaskara II's *Bijaganita* (1150) works the examples N = 61 and N = 67. MacTutor: "The next step forward was taken by Bhaskara II in 1150". **Documented** ([MacTutor, Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell); [MacTutor, Bhaskara II](https://mathshistory.st-andrews.ac.uk/Biographies/Bhaskara_II/))
- MacTutor's Pell page says Bhaskara II probably had no proof that the method always works. **Conjecture** ([MacTutor, Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell))
- Who first solved N = 61? MacTutor's Brahmagupta biography says "He also solves" 61x² + 1 = y², with smallest solution x = 226153980, y = 1766319049. MacTutor's own Pell page, Dutta and Waldschmidt all assign the case to Bhaskara II (1150). **Disputed** ([MacTutor, Brahmagupta](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/); [MacTutor, Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell); [Waldschmidt 2020](https://webusers.imj-prg.fr/%7Emichel.waldschmidt/articles/pdf/BrahmaguptaFermatPellEnVI.pdf))
- In 1657 Fermat posed the N = 61 case to European mathematicians, about 500 years after Bhaskara II. Brouncker answered with a method that is essentially continued fractions. Euler named the equation after Pell, probably because he confused Brouncker with Pell. **Documented** ([MacTutor, Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell); [Rike, Berkeley Math Circle](https://mathcircle.berkeley.edu/sites/default/files/archivedocs/2008_2009/lectures/0809lecturespdf/PellBMC.pdf): "The name Pell's equation is a misnomer.")
- The date of Lagrange's complete theory differs. MacTutor's Pell page says the theory "was put into a polished form by Lagrange in 1766", and Wikipedia also gives 1766. MacTutor's Pearce chapter says "The complete theory underlying the solution was expounded by Lagrange in 1767." MacTutor also dates Lagrange's *Additions* to Euler's *Algebra* to 1771. **Disputed** ([MacTutor, Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell); [MacTutor, Pearce ch. 14](https://mathshistory.st-andrews.ac.uk/Projects/Pearce/chapter-14); [Wikipedia](https://en.wikipedia.org/wiki/Chakravala_method))
- Selenius: "The chakravala process corresponds to a half-regular best approximating algorithm of minimal length." It is not Lagrange's regular continued fraction. For N = 61 the European method needs 22 convergents, against five or six steps for the Indian one. Wikipedia quotes Hankel calling the method "the finest thing achieved in the theory of numbers before Lagrange." **Documented** ([Selenius](https://www.ms.uky.edu/~sohum/ma330/files/Rationale-of-the-chakrav-la-process-of-Jayadeva-and-Bh-skara-II_1975_Historia-Mathematica.pdf); [Wikipedia](https://en.wikipedia.org/wiki/Chakravala_method))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Pell's Equation and Continued Fractions](https://mathcircle.berkeley.edu/sites/default/files/archivedocs/2008_2009/lectures/0809lecturespdf/PellBMC.pdf) | Tom Rike, Berkeley Math Circle, 28 April 2009 | High-school handout with exercises, covering Brahmagupta, Bhaskara and Fermat's N = 61 challenge |
| Deeper | [Mathematics in India – From Vedic Period to Modern Times](https://nptel.ac.in/courses/111101080) | NPTEL, IIT Bombay (K. Ramasubramanian, M. D. Srinivas, M. S. Sriram) | Video course. The [syllabus PDF](https://arctest.dev.nptel.ac.in/content/syllabus_pdf/111101080.pdf) lists lectures 11–13 on the *Brahmasphutasiddhanta* and 23–24 on the *Bijaganita* of Bhaskara II |
| Deeper | [Indian Mathematics](https://www.ms.uky.edu/~sohum/ma330/files/varadarajan.pdf) | V. S. Varadarajan, notes of two lectures at UCLA, March 2008 (copy on a University of Kentucky course site) | From Brahmagupta to Bhaskara's chakravala, and how Lagrange's theory of continued fractions shows it works |
| Scholar | [On the Brahmagupta–Fermat–Pell equation x² − dy² = ±1](https://webusers.imj-prg.fr/%7Emichel.waldschmidt/articles/pdf/BrahmaguptaFermatPellEnVI.pdf) | Michel Waldschmidt (Sorbonne Université), slides, ICMMSIS'20 web conference, 23 July 2020 | A number theorist's tour from Brahmagupta's N = 92 and Bhaskara's N = 61 through Fermat to Lagrange |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Pell's equation](https://mathshistory.st-andrews.ac.uk/HistTopics/Pell) | MacTutor | The whole story: Brahmagupta (628), Bhaskara II (1150), Fermat, Brouncker, Euler's misnaming, Lagrange |
| Start | [Indian Mathematics – Redressing the balance, ch. 14](https://mathshistory.st-andrews.ac.uk/Projects/Pearce/chapter-14) | MacTutor (Pearce project) | A worked chakravala example, and the comparison with Lagrange |
| Start | [Chakravala method](https://en.wikipedia.org/wiki/Chakravala_method) | Wikipedia | The step rule, written as an algorithm, with the N = 61 example |
| Deeper | [The bhāvanā in Mathematics](https://bhavana.org.in/the-bhavana-in-mathematics/) | Amartya Kumar Dutta (ISI Kolkata), *Bhāvanā* 1(1), January 2017 | Composition, Jayadeva and the chakravala, with worked boxes for N = 92 and N = 61 |
| Deeper | [Bhaskara II](https://mathshistory.st-andrews.ac.uk/Biographies/Bhaskara_II/) | MacTutor | Life (1114–1185) at Ujjain. Lists his examples (N = 8, 11, 32, 61, 67), but does not describe the cyclic method |
| Deeper | [Brahmagupta](https://mathshistory.st-andrews.ac.uk/Biographies/Brahmagupta/) | MacTutor | Life and the 628 treatise. Note that it credits the N = 61 solution to Brahmagupta (see **Disputed**) |
| Scholar | [Rationale of the chakravala process of Jayadeva and Bhaskara II](https://www.ms.uky.edu/~sohum/ma330/files/Rationale-of-the-chakrav-la-process-of-Jayadeva-and-Bh-skara-II_1975_Historia-Mathematica.pdf) | Clas-Olof Selenius, *Historia Mathematica* 2 (1975), 167–184 | The method is a minimal-length semiregular continued-fraction algorithm, distinct from Lagrange's |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Algebra, with Arithmetic and Mensuration, from the Sanscrit of Brahmegupta and Bháscara](https://archive.org/details/algebrawitharith00brahuoft/page/n5/mode/2up) | H. T. Colebrooke (trans.), London: J. Murray, 1817. Internet Archive (University of Toronto copy) | Colebrooke's English translation of Brahmagupta's and Bhaskara's algebra |

**Added with the topic page** (each opened before it was listed)

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Polynomial-time quantum algorithms for Pell's equation and the principal ideal problem](https://pure.psu.edu/en/publications/polynomial-time-quantum-algorithms-for-pells-equation-and-the-pri-2/) | Sean Hallgren, *Journal of the ACM* 54(1), 2007 (Penn State record) | "Factoring integers reduces to finding integer solutions of Pell's equation"; a quantum algorithm solves it in polynomial time and breaks the Buchmann–Williams key exchange |

Dutta's worked N = 61 reaches (5, 39; −4) in one chakravala step and finishes with Brahmagupta's rule for −4. The topic's program reproduces this route, and also the 22 convergents Selenius counts for the continued-fraction method.

**Gaps:** YouTube pages could not be opened in this environment, so no video is listed. Search found a YouTube result titled "Week 12-Lecture 62 : Brahmagupta-Pell equations", probably from an NPTEL course. Its page could not be opened, so its title and channel are unverified. The NPTEL course page did not load its lecture list, and its syllabus PDF is hosted on a test server (arctest.dev.nptel.ac.in). The syllabus does not name the chakravala or *varga-prakriti*. No Gresham College lecture on Pell's equation or the chakravala was found. MacTutor's Bhaskara II biography does not explain the method. No openly readable edition of Jayadeva's verses or of the *Sundari* was found. Kim Plofker's *Mathematics in India* (Princeton) was not opened. The Colebrooke scan page does not itself name the *Bijaganita*, and the relevant chapter was not checked in the scan. Open question for the plan: the sources credit the cyclic step to Jayadeva, before Bhaskara II, and Dutta builds it on the *kuttaka* (the pulverizer). That supports folding the pulverizer into this topic.

---

## 6. Algorism and al-jabr

**When / where:** Baghdad. Muhammad ibn Musa al-Khwarizmi (about 780 – about 850) worked at the House of Wisdom under the caliph al-Ma'mun, who ruled from 813. His algebra, *Hisab al-jabr w'al-muqabala*, is dedicated to al-Ma'mun and is dated anywhere from 813 to 833, and often to about 820. His treatise on Hindu numerals refers back to the algebra, so it came later. Its Arabic original is lost. It survives in Latin, in a 13th-century copy at Cambridge whose opening words are "Dixit Algorizmi", and in a second copy in New York.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** In Baghdad I found the man whose name became the word for what I study. Two of his books matter. One teaches the Indian way of writing numbers: nine figures and a sign for an empty place, then rules for each operation, fractions and square roots, carried out step by step in writing. Latin copyists turned his name into "algorism", and later writers into "algorithm". The other book sorts every linear and quadratic problem into six standard forms and gives a fixed recipe for each. For the hardest forms the recipe is a picture of a square being completed. It has no symbols, only words, and still it is a procedure that works for any numbers. His own species disagrees about whether he was original. Nobody disputes that he was copied.

**What hurt:** the Indian place-value numerals had reached Baghdad, but the methods of computing with them still had to be written out for readers. Practical problems, from measurement to the division of inheritances, led to linear and quadratic equations, which were solved case by case.
**The step forward:** two things. The first is a written, step-by-step arithmetic for place-value numerals: the "algorism". The second is an algebra in which *al-jabr* (restoring: removing subtracted terms) and *al-muqabala* (balancing) reduce a problem to one of six standard types. Each type then has a fixed rule. The mixed types are solved by completing the square: x² + 10x = 39 gives x = 3.

**Evidence and certainty**

- Al-Khwarizmi was born about 780 and died about 850. He worked at the House of Wisdom under al-Ma'mun, and he dedicated his algebra and astronomy to that caliph. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/); [Toomer, DSB](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf))
- No source gives a firm year for the algebra. Wikipedia says it was "compiled between 813 and 833" and elsewhere that it was "written approximately 820 CE". Hughes (MAA) puts al-Khwarizmi's activity at "fl. 815-850". MacTutor gives no year. The plan's c. 820–830 is a reasonable estimate inside al-Ma'mun's reign, not a recorded date. **Conjecture** ([Wikipedia](https://en.wikipedia.org/wiki/Al-Khwarizmi); [Hughes, MAA Convergence](https://old.maa.org/node/116292))
- Toomer says the Hindu-numerals treatise came after the algebra, which it cites. Wikipedia dates it "about 825". The order is **Documented**. The year is a **Conjecture**. ([Toomer](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf); [Wikipedia](https://en.wikipedia.org/wiki/Al-Khwarizmi))
- The arithmetic's Arabic original is lost. Cambridge University Library: "The text of the *Arithmetic* is known only from this copy and one other: New York, Hispanic Society of America, HC 397/726." The Cambridge copy is a 13th-century Latin copy and contains only the first half. Hogendijk describes the Latin version as a 12th-century translation. Burnett, Zhao and Lampe count at least four Latin versions descended from it. **Documented** ([Cambridge Digital Library](https://cudl.lib.cam.ac.uk/view/MS-II-00006-00005/1); [Hogendijk](https://www.jphogendijk.nl/khwarizmi.html); [Burnett et al. 2007](https://sciamvs.org/files/SCIAMVS_08_141-231_Burnett_Zhao_Lampey.pdf))
- Wikipedia says the Cambridge "Dixit Algorizmi" manuscript "is attributed to the Adelard of Bath". None of the other pages opened here names the translator. **Conjecture** ([Wikipedia](https://en.wikipedia.org/wiki/Al-Khwarizmi))
- The treatise teaches place value with the figures 1–9 and 0, the basic operations, fractions and square roots (Toomer). The word "algorism", later "algorithm", comes from his name. "Algebra" comes from *al-jabr* in the title of the algebra. **Documented** ([Toomer](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf); [MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/))
- The algebra has six standard types, such as squares and roots equal to numbers. The worked case x² + 10x = 39 is solved by halving the roots, adding 25 to make 64, and taking the root 8, which gives x = 3. A geometric figure shows the completed square. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/); [Hughes](https://old.maa.org/node/116292))
- Where did his algebra come from? Toomer and Rashed see familiarity with Book II of Euclid's *Elements*. Gandz holds that the *Elements* were "entirely unknown" to him. Toomer also sets out the case for Hindu influence, from the rhetorical style and the rule of three. The Hebrew *Mishnat ha-Middot* may be a source or a later borrowing, depending on its date. **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/); [Toomer](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf))
- How original was he? Rashed calls the originality of the algebra "impossible to overstress". Toomer writes that "al-Khwārizmī's scientific achievements were at best mediocre, but they were uncommonly influential". Wilson says of the arithmetic and the algebra: "Neither was a work of great originality". **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/); [Toomer](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf); [Gresham College](https://www.gresham.ac.uk/node/11558))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Who invented algebra?](https://www.gresham.ac.uk/node/11558) | Gresham College, Robin Wilson, 5 October 2005 (video and transcript) | Islamic mathematics from 750 to 1400. Covers al-Khwarizmi at the House of Wisdom, the origin of "algebra", and x² + 10x = 39 solved by a geometric "completing the square" |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Al-Khwarizmi's Completing the Square Activity](https://bulldog2.redlands.edu/fac/Beery/math115/m115_activ_complsq.htm) | Math 115 course page on the University of Redlands site. Activity by J. Beery, C. Dolezal, A. Sauk and L. Shuey, from *Historical Modules* (MAA, 2003) | Classroom worksheet: translate one of his problems into an equation, then complete the square by drawing it |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Completing the Square](https://old.maa.org/node/116292) | Barnabas Hughes, MAA *Convergence* | The geometric method for x² + 10x = 39, with practice equations |
| Deeper | [Al-Khwarizmi](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Khwarizmi/) | MacTutor | Life, the six equation types, completing the square, and the debate over his sources |
| Scholar | [Al-Khwārizmī](https://mathshistory.st-andrews.ac.uk/DSB/Al-Khwarizmi.pdf) | G. J. Toomer, *Dictionary of Scientific Biography* (reprint hosted by MacTutor) | Dating of each work, the arithmetic's content, and the Greek–Hindu–Hebrew sources question. The OCR is garbled in places |
| Scholar | [Al-Khwarizmi resource page](https://www.jphogendijk.nl/khwarizmi.html) | Jan Hogendijk (Utrecht University address), 2022 | Editions, translations and manuscripts of every work, with links to digitized copies |
| Scholar | [The Toledan *Regule* (*Liber Alchorismi*, part II): A Twelfth-century Arithmetical Miscellany](https://sciamvs.org/files/SCIAMVS_08_141-231_Burnett_Zhao_Lampey.pdf) | Charles Burnett, Ji-Wei Zhao, Kurt Lampe, *SCIAMVS* 8 (2007), 141–231 | How the Latin algorisms grew out of his lost arithmetic. Treats *Dixit Algorizmi* as one Latin version among several |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Algebra of Mohammed ben Musa](https://archive.org/details/algebraofmohamme00khuwuoft/algebraofmohamme00khuwuoft) | Frederic Rosen (ed. and trans.), London: Oriental Translation Fund, 1831. Internet Archive (University of Toronto copy) | Rosen's edition and English translation of the algebra |
| Scholar | [Cambridge University Library MS Ii.6.5](https://cudl.lib.cam.ac.uk/view/MS-II-00006-00005/1) | Cambridge Digital Library | Full digitization, including the 13th-century Latin copy of the *Arithmetic* (first half only), one of the two known copies |

**Gaps:** YouTube pages could not be opened, so no video beyond the Gresham page is listed. The MAA page "Completing the square in a manuscript copy of Al-Khwarizmi's 9th century algebra text" (maa.org/node/29787) loaded with navigation only, so its manuscript details could not be checked. A Cambridge University Press article, "Arabic origins and development of Latin algorisms in the twelfth century" (*Arabic Sciences and Philosophy*), redirected and could not be opened. Rashed's 2009 English edition of the algebra and the Crossley–Henry (1990) and Folkerts (1997) editions of the arithmetic are known only from Hogendijk's list. The New York manuscript (Hispanic Society HC 397/726) was not viewed. The CUDL page uses the identifier MS-II-00006-00005 rather than printing "Ii.6.5", and its text calls the work the *Arithmetic* or "Ars algorismi", not "Dixit Algorizmi". The column-by-column written methods themselves were not described step by step on any page opened, beyond Toomer's list of contents.

---

## 7. Frequency analysis

**When / where:** Baghdad, 9th century CE. Abu Yusuf Ya'qub ibn Ishaq al-Kindi was born in Kufa about 801 (MacTutor's page title says 805), died in Baghdad in 873, and was appointed to the House of Wisdom by al-Ma'mun. His *Risalah fi Istikhraj al-Mu'amma* ("A Manuscript on Deciphering Cryptographic Messages") is usually dated about 850 CE.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** A substitution cipher hides each letter behind another sign, but it cannot hide how often each sign appears. A philosopher in Baghdad wrote the trick down. Take a long plain text in the same language, count its letters and rank them. Count the signs in the secret text and rank them too. Then pair the two lists. When a message is too short for the counts to settle, he says, look instead at which letters like to stand next to each other. This is the first procedure in my catalog that needs facts about a whole language, gathered in advance, as well as the message itself. The treatise came back to light in an Istanbul archive only in the late twentieth century, and its rediscovery has two different dates.

**What hurt:** a monoalphabetic substitution cipher has far too many possible keys to try one by one. Without the key, the message is unreadable.
**The step forward:** count instead of guess. Rank the symbols of the ciphertext by frequency and match them to the ranking from a long sample of plaintext in the same language. When the text is short, use which letters occur together (al-Kindi's "qualitative" method).

**Evidence and certainty**

- Al-Kindi's dates differ within MacTutor itself. Its Quick Info gives born "about 801" in Kufa and died 873 in Baghdad, but its page title gives "805 - 873". **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kindi/))
- "Al-Kindi was appointed by al-Ma'mun to the House of Wisdom". MacTutor's biography says nothing about cryptography. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kindi/))
- The first known recorded explanation of frequency analysis is al-Kindi's, from the 9th century. Singh calls it "the earliest known description of the technique" and says nobody knows who first realized it. **Documented** ([Wikipedia](https://en.wikipedia.org/wiki/Frequency_analysis); [Simon Singh](https://simonsingh.net/The_Black_Chamber/crackingsubstitution.html); [Purdue CS 355](https://www.cs.purdue.edu/homes/ninghui/courses/Fall05/lectures/355_Fall05_lect02.pdf))
- Muslim Heritage dates the treatise to about 850 CE and calls it the oldest existing cryptologic text. That year is an estimate, not a recorded date. **Conjecture** ([Muslim Heritage](https://muslimheritage.com/arab-origins-of-cryptology/))
- When was it rediscovered? Singh says it was "only rediscovered in 1987 in the Sulaimaniyyah Ottoman Archive in Istanbul". Muslim Heritage says it was found in a 1979 search by Mrayati, Alam and al-Tayyan, mostly in the Suleymaniye archive, and that "The manuscripts were edited and analyzed by Dr. Mrayati and his team, and were published in Arabic in 1987." **Disputed** ([Simon Singh](https://simonsingh.net/The_Black_Chamber/crackingsubstitution.html); [Muslim Heritage](https://muslimheritage.com/arab-origins-of-cryptology/))
- The method, in al-Kindi's own words (English excerpt): "Among the expedients we use in cryptanalyzing a cryptogram if the language is already known, is to acquire a fairly long" sample of plain text, count and rank its letters, and match the ranking to the cryptogram. He adds a "qualitative" method for short cryptograms, where letter order by frequency cannot be applied. **Documented** ([Rocca, *Cryptology Through History and Inquiry*](https://sites.wcsu.edu/mbxml/html/section-24.html))
- The Qur'an may be where the idea started. Wikipedia: "It has been suggested that a close textual study of the Qur'an first brought to light" that Arabic has a characteristic letter frequency. **Conjecture** ([Wikipedia](https://en.wikipedia.org/wiki/Frequency_analysis))
- The Arabic–English edition is by M. Mrayati, Y. Meer Alam and M. H. at-Tayyan, translated by Said M. al-Asaid, published by KFCRIS and KACST as Vol. 1 of *Series on Arabic Origins of Cryptology*. It contains the treatise and a study of it. Ycart's references date it to 2002. **Documented** ([IACR Newsletter](https://iacr.org/newsletter/v20n3/newbooks.html); [Ycart 2013](https://benjamins.com/catalog/hl.40.3.01yca))
- Later Arab cryptologists: Ibn Adlan (d. 1268); Ibn ad-Durayhim (d. 1359), whose cryptanalysis treatise of about 1350 was thought lost until the 1979 search; and al-Qalqashandi's encyclopedia (1412). David Kahn's 1967 account rested on al-Qalqashandi. **Documented** ([Muslim Heritage](https://muslimheritage.com/arab-origins-of-cryptology/))
- How did the method reach Europe? The Purdue slides say it was "rediscovered or introduced from the Arabs in the Europe during the Renaissance". Wikipedia notes Cicco Simonetta's deciphering manual of 1474. Whether Europe learned it from Arabic sources is not settled. **Conjecture** ([Purdue CS 355](https://www.cs.purdue.edu/homes/ninghui/courses/Fall05/lectures/355_Fall05_lect02.pdf); [Wikipedia](https://en.wikipedia.org/wiki/Frequency_analysis))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Classical Cryptography: Shift Cipher and Substitution Cipher](https://www.cs.purdue.edu/homes/ninghui/courses/Fall05/lectures/355_Fall05_lect02.pdf) | CS 355 Introduction to Cryptography, lecture 2, Fall 2005 (Purdue computer science site) | University slides that place al-Kindi's frequency analysis against the substitution cipher |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Black Chamber: cracking the substitution cipher](https://simonsingh.net/The_Black_Chamber/crackingsubstitution.html) | Simon Singh | Plain explanation of frequency analysis and al-Kindi's role, with the 1987 rediscovery claim |
| Start | [Arab origins of cryptology](https://muslimheritage.com/arab-origins-of-cryptology/) | Muslim Heritage, summary of a talk by Mohammed I. Al-Suwaiyel (2018) | The treatise's title and date, the 1979 manuscript search, and the later Arab cryptologists |
| Start | [Frequency analysis](https://en.wikipedia.org/wiki/Frequency_analysis) | Wikipedia | The method, al-Kindi, the Qur'an hypothesis, and the European sequel |
| Deeper | [Chapter 2 quotes](https://sites.wcsu.edu/mbxml/html/section-24.html) | Charles F. Rocca Jr., *Cryptology Through History and Inquiry*, Appendix D (WCSU site) | An English excerpt of al-Kindi's own instructions, cited to vol. 1, pp. 121–123 of the book's reference [12] |
| Deeper | [Al-Kindi](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kindi/) | MacTutor | Life, the House of Wisdom, and his works on Indian numbers. Silent on cryptography |
| Scholar | [Letter counting: A stem cell for cryptology, quantitative linguistics, and statistics](https://benjamins.com/catalog/hl.40.3.01yca) | Bernard Ycart, *Historiographia Linguistica* 40(3) (2013), 303–330 | The long history of letter counting, from cryptology to Markov. Cites the al-Kindi edition and Al-Kadi (1992) |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [New books: *Al-Kindi's Treatise on Cryptanalysis*](https://iacr.org/newsletter/v20n3/newbooks.html) | IACR Newsletter 20(3) | Describes the Arabic–English edition (Mrayati, Meer Alam, at-Tayyan; KFCRIS and KACST), whose Chapter 3 is the translation, with the Arabic alongside |

**Gaps:** YouTube pages could not be opened, so no video is listed. Khan Academy's frequency-analysis video was not found at a URL that could be opened. Ibrahim Al-Kadi's paper "Origins of cryptology: The Arab contributions" (*Cryptologia*, 1992) was found as a PDF on a Grenoble faculty site, but the link redirected and could not be opened. The 2002 English edition of the treatise is not openly available. The only full copy found was on a file-sharing site, which is not listed. No Gresham College or other university lecture devoted to al-Kindi was found. The Purdue slides do not name their instructor on the page. Rocca's book does not identify the translator of its excerpt on that page. Neither the Simon Singh page nor Muslim Heritage gives a manuscript shelfmark, so which Süleymaniye manuscript holds the treatise is unverified.

---

## 8. Fibonacci's *Liber Abaci*

**When / where:** Pisa, 1202 CE. Leonardo of Pisa, called Fibonacci (c. 1170 – c. 1250), learned Hindu–Arabic reckoning at Bugia (now Bejaia, Algeria). His father was a public notary at the customs there, acting for Pisan merchants. *Liber abaci* was published in 1202 after his return to Italy. The 1202 text is lost, and every surviving copy descends from the second edition of 1228.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** In Pisa the merchants still wrote amounts in Roman numerals, which are fine for recording a sum and miserable for working one out. The son of a customs official, who had learned the Indian figures in North Africa, wrote them a manual in fifteen chapters. It begins with nine figures and a zero. Then come written rules for multiplying, adding, subtracting and dividing, then fractions, then problem after problem on prices, barter, partnerships and money changing. In chapter 12, almost in passing, there is a puzzle about rabbits whose answer, 1, 2, 3, 5, 8, …, my hosts now name after him. Sanskrit writers had met that sequence centuries earlier. His real export was the written algorithm itself, put into the hands of people who did sums for a living.

**What hurt:** Roman numerals make multiplication and division cumbersome, and they leave no worked record that a reviewer can check, the "audit trail" Devlin stresses. Merchants in a growing maritime trade needed both.
**The step forward:** Hindu–Arabic place value with zero, plus written step-by-step algorithms for the four operations and for fractions. These are applied to commercial problems such as pricing, barter, profit-sharing and currency exchange, and then to double false position, roots and algebra. Along the way comes the rabbit recurrence F(n) = F(n−1) + F(n−2).

**Evidence and certainty**

- Fibonacci's dates: MacTutor gives c. 1170 – c. 1250, and Strick's title gives 1170–1250. MAA's Mathematical Treasures page gives "ca.1180-1241". **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/); [Strick, MacTutor](https://mathshistory.st-andrews.ac.uk/Strick/Fibonacci.pdf); [MAA Mathematical Treasures](https://old.maa.org/node/1734149))
- His father was "appointed by his country as public notary in the customs at Bugia". **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/))
- "Liber abaci (Book of the abacus), published in 1202 after Fibonacci's return to Italy, was dedicated to Scotus." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/))
- Only the second edition survives. Strick: "However, an exemplar of the edition of 1228 survives." Cuomo: "There are twelve manuscript copies of the Liber abaci, three of which are complete". She argues that the printed text must be the 1228 edition, because it refers to the later *Practica geometriae* and *Liber quadratorum*. **Documented** ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/Fibonacci.pdf); [Cuomo, *Aestimatio* 2004](https://ircps.org/wp-content/uploads/2021/04/2004-02-01_Cuomo.pdf))
- The year of the second edition: MacTutor, Strick, Swetz and Cuomo give 1228. MAA's Mathematical Treasures page says "He wrote a later edition in 1212." **Disputed**. The 1212 date is probably a slip, but it is printed. ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/); [Swetz, MAA](https://old.maa.org/node/116274); [MAA Mathematical Treasures](https://old.maa.org/node/1734149))
- Chapter 1 opens with the numerals: "These are the nine figures of the Indians: 9 8 7 6 5 4 3 2 1." Chapters 2–7 cover the operations and fractions, and chapters 8–11 cover commercial problems. **Documented** ([ETSU MATH 3040 notes](https://faculty.etsu.edu/gardnerr/3040/Notes-Eves6/Leonardo-Fibonacci-Liber-abbaci.pdf))
- The rabbit problem sits in chapter 12, in the third section of the book. Its sequence had been recorded in Sanskrit around 200 BC. **Documented** ([Strick](https://mathshistory.st-andrews.ac.uk/Strick/Fibonacci.pdf); [MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/); [Nature blog](https://blogs.nature.com/aviewfromthebridge/2017/04/20/fibonaccis-mathematical-legacy/))
- When did Pisa start paying him? MacTutor quotes "a decree made by the Republic of Pisa in 1240 in which a salary is awarded" to him. Strick: "From 1228 on, FIBONACCI was granted an annual stipend by the city of Pisa for his services as arithmetician and tax assessor." **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/); [Strick](https://mathshistory.st-andrews.ac.uk/Strick/Fibonacci.pdf))
- Is the vernacular *Livero de l'abbecho* a copy of Fibonacci's lost simpler book? Keith Devlin argues that it is. Raffaella Franci, quoted in *Nature*: "I do not believe and I have never claimed that Livero de l'abbecho should be attributed to Leonardo Pisano." **Disputed** ([Nature blog](https://blogs.nature.com/aviewfromthebridge/2017/04/20/fibonaccis-mathematical-legacy/))
- How much did the book shape later teaching? The abacus books "became standard in schools; at least 600 were written over the next few centuries", but *Nature* questions how far *Liber abaci* directly inspired them. **Conjecture** ([Nature blog](https://blogs.nature.com/aviewfromthebridge/2017/04/20/fibonaccis-mathematical-legacy/))
- Sigler's English translation is the first in any modern language. Springer and Cuomo date it 2002, while Swetz's MAA review and the Mathematical Treasures page give 2003. **Disputed** (bibliographic only) ([Springer](https://link.springer.com/book/9780387407371); [Cuomo](https://ircps.org/wp-content/uploads/2021/04/2004-02-01_Cuomo.pdf); [Swetz](https://old.maa.org/node/116274))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Who invented algebra?](https://www.gresham.ac.uk/node/11558) | Gresham College, Robin Wilson, 5 October 2005 (video and transcript) | Islamic mathematics and its route into Europe, including through Fibonacci. Context more than detail |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Fibonacci's Rabbits](https://mathcenter.oxford.emory.edu/site/math125/fibonacciRabbits) | Math 125 notes, Oxford College of Emory University math center site | Turns the rabbit puzzle from *Liber Abaci* (1202) into the recurrence |
| Deeper | [Supplement: Leonardo of Pisa (Fibonacci) and the Liber abbaci](https://faculty.etsu.edu/gardnerr/3040/Notes-Eves6/Leonardo-Fibonacci-Liber-abbaci.pdf) | MATH 3040 course notes, East Tennessee State University faculty site, based on Devlin's *The Man of Numbers* (2011) | Chapter-by-chapter contents of the book, editions, and the *Livero de l'abbecho* |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Leonardo of Pisa, also known as Fibonacci (1170–1250)](https://mathshistory.st-andrews.ac.uk/Strick/Fibonacci.pdf) | Heinz Klaus Strick, trans. David Kramer, MacTutor | Short illustrated life and a tour of the book, rabbits included |
| Start | [Fibonacci's real mathematical legacy](https://blogs.nature.com/aviewfromthebridge/2017/04/20/fibonaccis-mathematical-legacy/) | Davide Castelvecchi, *Nature* blog | Argues that the numerals, not the sequence, were the legacy, and reports the Devlin–Franci dispute |
| Start | [Why do the Fibonacci numbers appear as the number of rabbits in the field each month?](https://fibonacci-numbers.surrey.ac.uk/fibonacci/rabserieswhy.html) | Ron Knott, University of Surrey site | A proof of the recurrence from the rabbit rules |
| Deeper | [Fibonacci](https://mathshistory.st-andrews.ac.uk/Biographies/Fibonacci/) | MacTutor | Life, the 1202 and 1228 editions, the 1240 decree, and the other works (1220, 1225) |
| Deeper | [Fibonacci's Liber Abaci](https://old.maa.org/node/116274) | Frank J. Swetz, MAA *Convergence* (July 2007) | Review of Sigler's translation, with the book's Arabic sources (al-Khwarizmi, Abu Kamil, al-Karaji) |
| Scholar | [Review of Sigler, *Fibonacci's Liber Abaci*](https://ircps.org/wp-content/uploads/2021/04/2004-02-01_Cuomo.pdf) | Serafina Cuomo, *Aestimatio* 1 (2004), 19–27 | The manuscript tradition (12 copies, 3 complete), and why the surviving text is the 1228 edition |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Il Liber abbaci di Leonardo Pisano](https://archive.org/details/bub_gb_w86fLKi88pYC/page/n7/mode/2up) | Baldassarre Boncompagni (ed.), *Scritti di Leonardo Pisano*, 1857. Internet Archive (Google Books scan of the Florence National Central Library copy) | The Latin text, edited from a single manuscript |
| Scholar | [Fibonacci's Liber Abaci: A Translation into Modern English of Leonardo Pisano's Book of Calculation](https://link.springer.com/book/9780387407371) | Laurence Sigler, Springer, 2002 (Sources and Studies in the History of Mathematics and Physical Sciences) | The only complete translation into a modern language |
| Scholar | [Mathematical Treasures: Fibonacci's Liber abaci](https://old.maa.org/node/1734149) | MAA *Convergence* | Images from a 14th-century copy in the Biblioteca Nazionale Centrale di Firenze, including the page of nine Indian figures, and a translation of the autobiographical preface |

**Gaps:** YouTube pages could not be opened, so no video is listed. Search found, for example, "Fibonacci's Liber Abaci: Leonardo Pisano's Book of Calculation" and Italian documentaries, but none could be checked. Keith Devlin's lecture "Leonardo Fibonacci and the birth of the modern western world" (University of Huddersfield, 23 October 2019) has an event page, but the page mentions no recording, so it is not listed. Devlin's *The Man of Numbers* was not opened. The ETSU and Emory pages name neither an author nor a course instructor; their institutions are inferred from their sites. No digitized manuscript of *Liber abaci* (for example in Florence) was found directly, and Boncompagni's volume page does not state its volume number or place of publication. The claim that merchants used counting boards comes from the plan, not from a page opened here: the pages opened speak only of Roman numerals.

---

## 9. Horner's method, nearly six centuries early, and the Da Yan rule

**When / where:** Qin Jiushao (1202–1261), *Shushu jiuzhang* (*Mathematical Treatise in Nine Sections*), 1247, Southern Song China. He wrote it during the mourning period after his mother's death. According to Strick, it was not printed in his lifetime, and the version read today was published in 1842 from a Korean copy.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** This official wrote his mathematics while in mourning, and he put two procedures on the counting board that the West would find again centuries later. The first finds a root of an equation of any degree one digit at a time. Each new digit shifts the whole polynomial, so the next digit is found the same way as the last, and no power is ever computed directly. The second, the Da Yan rule, "searches for unity": it finds the multiplier that leaves remainder 1, and with it a number that fits any set of remainders. Calendar makers had used the rule for centuries. Qin is the first I can find who wrote it out in full.

**What hurt:** equations of degree three, four and even ten arose in area and surveying problems, and calendar reckoning required one number that fit several cycles at once.
**The step forward:** root-finding by repeated shifting of the polynomial, one digit at a time, using only multiplications and additions on the board (the Ruffini–Horner scheme). And a general rule for congruences: make the moduli pairwise coprime, find each inverse by repeated division ("finding unity"), then combine the results.

**Evidence and certainty**

- Qin's dates (1202–1261), the treatise's year (1247), and its nine sections of nine problems. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/); [Britannica](https://www.britannica.com/print/article/111675))
- MacTutor says he solved his cubics and quartics by the standard Chinese method, "namely that which today is called the Ruffini-Horner method". One problem leads to an equation of degree 10, with root x = 3. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/))
- The European rediscovery is dated differently. Britannica: "This method was rediscovered in Europe about 1802 and was known as the Ruffini-Horner method." Ho Peng-yoke (DSB): "The method is identical to that rediscovered by Paolo Ruffini about 1805 and by William George Horner in 1819." Strick puts Ruffini about ten years before Horner's 1819 paper. **Disputed** (Ruffini's date) ([Britannica](https://www.britannica.com/print/article/111675); [DSB](https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf); [Strick](https://mathshistory.st-andrews.ac.uk/Strick/qin_jiushao.pdf))
- Qin did not invent the root-finding method. Britannica calls his book the earliest surviving description and says scholars think the method was widely known in China earlier. The DSB notes that his contemporary Li Zhi could also solve such equations, and that Wang Ling and Needham trace the essentials back to the *Nine Chapters*. **Conjecture** (who first devised it) ([Britannica](https://www.britannica.com/print/article/111675); [DSB](https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf); [Wang & Needham 1955, catalogue record](https://ilse.kobv.de/KobvIndexRecord/nat_lic_papers_NLM110339983))
- Sources number the degree-10 "circular city" problem differently: MacTutor places it in Chapter 4, Siu in Problem 2 of Chapter 8. **Disputed** (numbering only) ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/); [Siu](https://hkumath.hku.hk/~mks/ESU8_MKSiu_Equations_RevisedDraft_Mar12_2019.pdf))
- The Da Yan rule opens Chapter 1. It handles moduli that are not pairwise coprime by first making them coprime. Qin credits the rule to calendar experts at the Board of Astronomy: "He states, however, that these calendar experts used the rule without understanding it." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/))
- The motivation was calendrical. Astronomers fixed a *shangyuan* (superior epoch) at which the 60-day cycle, the winter solstice and a new moon coincided, and placing a year relative to it produced congruences with large moduli. Shen Kangsheng: "QIN had obtained the same results without the concept of prime numbers 550 years before him" (that is, before Gauss). **Documented** ([Shen Kangsheng 1988](https://link.springer.com/doi/10.1007/BF00357063); [full text](https://www.ms.uky.edu/~sohum/ma330/files/CRT_history_Kangsheng.pdf))
- The name *ta yen* ("Great Extension") comes from the *Book of Changes*, not from calendar work. The calendar link comes through the *Shang yuan* problem. **Documented** ([DSB, Ho Peng-yoke](https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf))
- In modern terms, the "finding unity" step computes a modular inverse. Xu and Li show it equivalent in result to the extended Euclidean algorithm, with comparable cost and fewer temporary variables. **Documented** (as their analysis) ([Xu & Li, arXiv](https://arxiv.org/pdf/1610.01175))
- The *Shushu jiuzhang* is the oldest extant Chinese mathematical text with a zero symbol. It uses red and black rods for positive and negative numbers. **Documented** ([DSB](https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf))
- No source opened here claims that either method was transmitted to Europe. Wylie introduced the Dayan rule and Chinese equation-solving to Western readers in 1852. Matthiessen then showed that the Dayan rule is equivalent to Gauss's rule. **Documented** ([Wang Xiaoqin 2003](https://thjcs.site.nthu.edu.tw/p/16-1452-41351.php?Lang=en))
- Small conflicts in the biography: Britannica dates his dismissal for corruption to 1258, Strick to 1259. **Disputed** ([Britannica](https://www.britannica.com/print/article/111675); [Strick](https://mathshistory.st-andrews.ac.uk/Strick/qin_jiushao.pdf))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [The Chinese algorithm for solving equations](https://mathcs.clarku.edu/~djoyce/ma105/chinalg.html) | David E. Joyce, Clark University (course MA105) | Worked digit-by-digit solution of a cubic and a fifth root, with a note on how it ran on a counting board, compared with bisection and Newton's method |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Qin Jiushao](https://mathshistory.st-andrews.ac.uk/Biographies/Qin_Jiushao/) | MacTutor | Life, the 1247 treatise, the degree-10 equation, and the remainder theorem with non-coprime moduli |
| Start | [Qin Jiushao](https://www.britannica.com/print/article/111675) | Encyclopaedia Britannica | Short biography; the earliest surviving description of the root-finding method |
| Start | [Qin Jiushao (1202–1261)](https://mathshistory.st-andrews.ac.uk/Strick/qin_jiushao.pdf) | H. K. Strick, trans. J. O'Connor, MacTutor | Illustrated article with a worked shift-the-root example (x = y + 2) and Sun Zi's 3-5-7 problem |
| Deeper | [Equations in China: Two Millennia of Innovation, Transmission and Retransmission](https://hkumath.hku.hk/~mks/ESU8_MKSiu_Equations_RevisedDraft_Mar12_2019.pdf) | Man-Keung Siu, University of Hong Kong | Places Qin's *zengcheng kaifangfa* in the long Chinese history of equations |
| Deeper | [On the Algorithmic Significance and Analysis of the Method of DaYan Deriving One](https://arxiv.org/pdf/1610.01175) | Guangwu Xu and Bao Li, arXiv | Qin's inverse procedure restated as a 2×2 state-matrix algorithm and compared with extended Euclid |
| Scholar | [Historical development of the Chinese remainder theorem](https://link.springer.com/doi/10.1007/BF00357063) | Shen Kangsheng, *Archive for History of Exact Sciences* 38(4):285–305 (1988) | The calendar origin (*shangyuan*) and a step-by-step reading of the Dayan rule. Full text on a [University of Kentucky course site](https://www.ms.uky.edu/~sohum/ma330/files/CRT_history_Kangsheng.pdf) |
| Scholar | [Traditional Chinese Mathematics in the 19th Century Western World](https://thjcs.site.nthu.edu.tw/p/16-1452-41351.php?Lang=en) | Wang Xiaoqin (2003), National Tsing Hua University journal site | How Wylie, Biernatzki, Cantor and Matthiessen received the Dayan rule in Europe |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Ch'in Chiu-shao](https://mathshistory.st-andrews.ac.uk/DSB/Qin_Jiushao.pdf) | Ho Peng-yoke, *Dictionary of Scientific Biography* (via MacTutor) | Standard reference entry: the root-finding method, the *ta-yen ch'iu-i shu*, the zero symbol, the degree-10 equation |
| Scholar | [Chinese Mathematics in the Thirteenth Century, ch. 14](https://legacy-www.math.harvard.edu/~knill/crt/lib/Libbrecht14.pdf) | Ulrich Libbrecht (MIT Press, 1973), excerpt in [Oliver Knill's CRT library](https://legacy-www.math.harvard.edu/~knill/crt/lib.html), Harvard | The standard English study of the *Shushu jiuzhang*. This chapter surveys first-degree indeterminate analysis outside China and says the problem "finds its culminating point in the work of Ch'in Chiu-shao (1247)" |
| Scholar | [Horner's method in Chinese mathematics; its origins in the root-extraction procedures of the Han dynasty](https://ilse.kobv.de/KobvIndexRecord/nat_lic_papers_NLM110339983) | Wang Ling and Joseph Needham (1955), library catalogue record | The classic paper arguing that the method grows out of Han root extraction. This is a record only, not the text |

**Gaps:** no video was found. Web searches returned no YouTube pages for Qin Jiushao, Horner's method or the Chinese remainder theorem, so none is listed. No online text or translation of the *Shushu jiuzhang* itself could be opened (ctext.org returned only an anti-scraping notice). Wylie's 1852 paper was not found online. The British Journal for the History of Science review of Libbrecht's book could not be fetched (the URL is too long). The Wang–Needham record does not name its journal (it gives only ISSN 0082-5433). Only chapter 14 of Libbrecht was opened, not his translation of the Da Yan problems.

---

## 10. Madhava's series for π

**When / where:** Madhava of Sangamagrama (c. 1350–1425), founder of the Kerala school, southwestern India. None of his mathematical writings survive. His series are known from later Kerala texts: Nilakantha's *Tantrasangraha* (c. 1500) and Jyesthadeva's Malayalam *Ganita-Yukti-Bhasa* (c. 1530), which gives the derivations.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Archimedes' polygons cost a new square root for every doubling. In Kerala I found something new: a sum that never ends. One minus a third, plus a fifth, minus a seventh, and so on, gives a quarter of the circumference over the diameter. By itself this sum is hopeless, because a million terms buy only a few digits. So the Kerala astronomers stopped after a few terms and added one correction that estimates everything they left out. That correction is the clever part. It is the first time I have seen anyone compute with an infinite process and then deal honestly with the part they did not compute.

**What hurt:** each extra digit from polygons needed another round of square roots. The plain series converges far too slowly to use.
**The step forward:** an infinite series for π/4 (and faster forms, such as a series multiplied by √12), with an end-correction term that estimates the remainder after the last term computed.

**Evidence and certainty**

- "All the mathematical writings of Madhava have been lost, although some of his texts on astronomy have survived." His results are known through later Kerala writers. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/))
- Madhava's dates are approximate: c. 1350–1425 (MacTutor; Mumford, "who lived from approximately 1350 to 1425"), c. 1340–1420 (Ramasubramanian, ICM 2022), 1350–1420 with ±5 years flagged as tentative (Singh). **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/); [Mumford](https://www.dam.brown.edu/people/mumford/beyond/papers/2010a--PlofkerReview-AMS.pdf); [ICM slides](https://mathunion.org/fileadmin/IMU/ICM2022/Presentation-slides/218-Krishnamurthi%20Ramasubramanian.pdf); [Singh](https://arxiv.org/pdf/2304.03684))
- The plain series needs almost a million terms for 4–5 decimal places. Madhava's method is to stop and "Make an estimate of the remaining terms in the series", which gives 8–9 places from about 20 terms. Using the √12 form with 21 terms, MacTutor credits him with π correct to 11 decimal places. **Documented** ([ICM slides](https://mathunion.org/fileadmin/IMU/ICM2022/Presentation-slides/218-Krishnamurthi%20Ramasubramanian.pdf); [MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/))
- How Madhava found his correction terms is not recorded. Krishnachandran reviews the reconstructions and concludes that "the rationale presented by Kerala authors is not strong enough to convince modern mathematical scholarship". **Conjecture** ([Krishnachandran, arXiv](https://arxiv.org/abs/2405.11134))
- The date of the *Yuktibhasa* varies: c. 1530 (Springer edition; Ramasubramanian), around 1540 (Mumford), c. 1550 (MacTutor), c. 1500 (Singh). **Disputed** ([Springer](https://link.springer.com/book/9781848820722); [Mumford](https://www.dam.brown.edu/people/mumford/beyond/papers/2010a--PlofkerReview-AMS.pdf); [MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/); [Singh](https://arxiv.org/pdf/2304.03684))
- Europe first heard of the Kerala series from Charles M. Whish, *Transactions of the Royal Asiatic Society* 3 (1834), p. 509. **Documented** ([Singh](https://arxiv.org/pdf/2304.03684))
- Did the series reach Europe before Gregory and Leibniz? In 2007 the University of Manchester announced that "there is strong circumstantial evidence that the Indians passed on their discoveries" to Jesuit missionaries. Plofker, reviewing G. G. Joseph's later book, wrote that "it is hard to help feeling disappointed that this hypothesis ultimately came to nothing." Mumford calls the question of exchange contested and notes that Plofker presents the competing views without settling them. MacTutor calls the European results rediscoveries, and the MAA review says the series was "derived in Europe by Leibniz and Gregory more than two centuries after Madhava's work." **Disputed** ([Manchester](https://www.manchester.ac.uk/about/news/indians-predated-newton-discovery-by-250-years/); [Manuel, quoting Plofker](https://3quarksdaily.com/?p=143638); [Mumford](https://www.dam.brown.edu/people/mumford/beyond/papers/2010a--PlofkerReview-AMS.pdf); [MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/); [MAA review](https://old.maa.org/node/109461))
- Whether this counts as "calculus" is a question of framing. The ICM slides quote the description of the *Yuktibhasa* as "the first textbook on Calculus" and note that some articles express reservations about it. **Disputed** ([ICM slides](https://mathunion.org/fileadmin/IMU/ICM2022/Presentation-slides/218-Krishnamurthi%20Ramasubramanian.pdf))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Mathematics in India: From Vedic Period to Modern Times](https://nptel.ac.in/courses/111101080) | NPTEL video course, IIT Bombay (K. Ramasubramanian, M. D. Srinivas, M. S. Sriram) | Lectures 30–31, "Kerala School of Astronomy and Development of Calculus", and proofs from the *Yuktibhasa* ([syllabus](https://arctest.dev.nptel.ac.in/content/syllabus_pdf/111101080.pdf)) |
| Deeper | [The History and Historiography of the Discovery of Calculus in India](https://mathunion.org/fileadmin/IMU/ICM2022/Presentation-slides/218-Krishnamurthi%20Ramasubramanian.pdf) | K. Ramasubramanian, invited talk, ICM 2022 (slides) | The series, the end-correction, and the Kerala lineage, Madhava to Jyesthadeva |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Madhava of Sangamagrama](https://mathshistory.st-andrews.ac.uk/Biographies/Madhava/) | MacTutor | The series, the √12 form, the correction terms, and how his lost work is known |
| Start | [Indians predated Newton 'discovery' by 250 years](https://www.manchester.ac.uk/about/news/indians-predated-newton-discovery-by-250-years/) | University of Manchester press release (13 Aug 2007) | The transmission claim in its strongest public form, including the "circumstantial evidence" wording |
| Start | [Madhava and the Uninfluential Discovery](https://3quarksdaily.com/?p=143638) | Thomas Manuel, 3 Quarks Daily (2018) | The skeptical side, quoting Plofker's review |
| Deeper | [Mathematics in India (review)](https://www.dam.brown.edu/people/mumford/beyond/papers/2010a--PlofkerReview-AMS.pdf) | David Mumford, *Notices of the AMS* 57(3) (2010) | A mathematician's account of the Kerala power series and the *Yuktibhasa* proofs |
| Deeper | [Ideas of Calculus in Islam and India](https://maa.org/node/95254) | Victor J. Katz, *Mathematics Magazine* 68(3):163–174 (1995), MAA | The classic survey of the Indian power series for sine, cosine and arctangent |
| Deeper | [Review of *Ganita-Yukti-Bhasa*](https://old.maa.org/node/109461) | Homer S. White, MAA Reviews (2009) | What the translation contains, including Madhava's correction terms |
| Deeper | [India and the Calculus of Trigonometric Functions](https://arxiv.org/pdf/2304.03684) | Vijay A. Singh, arXiv | Timeline of the Madhava school and Whish's 1834 report |
| Scholar | [On Mādhava and his correction terms for the Mādhava–Leibniz series for π](https://arxiv.org/abs/2405.11134) | V. N. Krishnachandran, arXiv (2024) | The three correction terms examined critically, and reconstructions of how they were found |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Ganita-Yukti-Bhāṣā (Rationales in Mathematical Astronomy) of Jyeṣṭhadeva](https://link.springer.com/book/9781848820722) | K. V. Sarma (trans.), K. Ramasubramanian, M. D. Srinivas, M. S. Sriram; Springer / Hindustan Book Agency (2008), 2 vols. | The Malayalam text (c. 1530) that gives the derivations, in English translation with notes |

**Gaps:** a Mathologer video, "Powell's Pi Paradox: the genius 14th century Indian solution" (6 May 2023), was found only through a TheTVDB listing. No YouTube page appeared in any search, so the video is not listed. Whish's 1834 paper exists as a PDF on cheenta.com, but the URL was too long to fetch. The full text of Katz (1995) could not be read (only the JSTOR header loaded), so its row relies on the MAA summary page. *The Wire*'s 2018 article returned no body text. The Springer translation of the *Tantrasangraha* was not opened. No text by Madhava himself survives.

---

## 11. al-Kashi's π

**When / where:** Ghiyath al-Din Jamshid Mas'ud al-Kashi (c. 1380–1429), working for Ulugh Beg in Samarkand. He completed *al-Risala al-muhitiyya* (*Treatise on the Circumference*) in July 1424 (Sha'ban 827 AH).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** This calculator did something I had not seen before: he set the error he would accept *before* he began. Take a circle 600,000 times as wide as the Earth. Its computed circumference must be off by no more than the width of a horse's hair. From that target he worked out how far to go: start from a hexagon and keep doubling the sides until the polygon has 3·2^28 = 805,306,368 of them (27 doublings). He did every step in base 60, on a circle of radius 60, and gave the answer in both sexagesimal and decimal fractions. Archimedes' method was already some 1,700 years old. What was new was the accounting: a precision fixed before he started, and a computation planned to meet it.

**What hurt:** astronomical tables needed π to more places than any earlier value gave. Al-Kashi also found errors in the values computed by Abu'l-Wafa and al-Biruni.
**The step forward:** Archimedes' doubling of polygon sides, pushed from a hexagon to 3·2^28 sides. The size of the polygon was chosen to meet an explicit error target, and every root was computed in sexagesimal fractions.

**Evidence and certainty**

- MacTutor: "He produced his *Treatise on the Circumference* in July 1424", in which he "calculated 2π to nine sexagesimal places and translated this into sixteen decimal places". Azarian: "This risala, which was written long-hand in Arabic by Kashani himself, was completed in July 1424 (Shaban 827 A. H. L.)." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kashi/); [Azarian, AMS meeting abstract](https://www.jointmathematicsmeetings.org/amsmtgs/2109_abstracts/1035-01-248.pdf))
- The polygon has 3·2^28 = 805,306,368 sides. **Documented** ([DSB, Youschkevitch & Rosenfeld](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf); [Strick](https://mathshistory.st-andrews.ac.uk/Strick/al-kashi.pdf))
- The accuracy target: for a circle whose diameter is 600,000 Earth diameters, the circumference may be off by no more than the breadth of a horse's hair. The DSB puts this at an error in π of at most 0.5·10^-17. **Documented** ([Azarian's translation of the introduction](https://webcf.waybackmachine.org/web/20220512123120/https://ijpam.eu/contents/2009-57-6/5/5.pdf); [DSB](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf); [Andrade](https://revistas.uece.br/index.php/BOCEHM/article/download/4964/4374/21743))
- The calculations are in sexagesimal notation on a circle of radius 60, with the results given in both sexagesimal and decimal fractions. **Documented** ([ISMI, Max Planck Institute for the History of Science](https://ismi.mpiwg-berlin.mpg.de/text/499858))
- The DSB gives 2π = 6.2831853071795865 and says: "This superb result far surpassed all previous determinations of π." **Documented** ([DSB](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf))
- How many places are correct? Sixteen decimals according to MacTutor, the DSB, Strick and the *Biographical Encyclopedia of Astronomers*. Gourdon and Sebah: "he computed, in 1424, 2π to nine sexagesimal places and his estimation (about 14 correct decimals)". MacTutor counts nine sexagesimal places, while Strick speaks of 10-digit sexagesimal accuracy, probably counting the integer digit 6 as well (this catalog's reading). **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kashi/); [BEA](https://mathshistory.st-andrews.ac.uk/BEA/al_kashi_bea.pdf); [Strick](https://mathshistory.st-andrews.ac.uk/Strick/al-kashi.pdf); [Gourdon & Sebah](https://gauss.dartmouth.edu/~m56s13/Gourdan2010notes_computing_pi_through_ages.pdf))
- When was the record broken? No source opened here dates it directly. The DSB lists van Roomen's fifteen places (1597), which falls short of al-Kashi. MacTutor's van Ceulen page says: "In this book he gave π correct to 20 decimal places using a regular polygon of 15×2^31 sides." That book appeared in 1596, which makes it the earliest larger count found here. **Conjecture** ([DSB](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf); [MacTutor, Van Ceulen](https://mathshistory.st-andrews.ac.uk/Biographies/Van_Ceulen/))
- Van Ceulen's later counts differ: the DSB gives thirty-two places (published 1615), MacTutor 33 places (1615) and 35 places (published 1621). **Disputed** ([DSB](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf); [MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Van_Ceulen/))
- Al-Kashi's death: 22 June 1429 according to MacTutor and Britannica ("possibly" in the BEA). Muslim Heritage gives c. 1380–1436. **Disputed** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kashi/); [Britannica](https://www.britannica.com/biography/al-Kashi); [BEA](https://mathshistory.st-andrews.ac.uk/BEA/al_kashi_bea.pdf); [Muslim Heritage](https://muslimheritage.com/the-scholars-of-samarkand/))
- Ulugh Beg's observatory: the BEA says it was founded in 1420. Strick and Muslim Heritage say construction began in 1424. **Disputed** ([BEA](https://mathshistory.st-andrews.ac.uk/BEA/al_kashi_bea.pdf); [Strick](https://mathshistory.st-andrews.ac.uk/Strick/al-kashi.pdf); [Muslim Heritage](https://muslimheritage.com/the-scholars-of-samarkand/))
- Manuscripts: ISMI lists 9 witnesses, and Hogendijk counts at least eight Arabic manuscripts, with facsimiles of the Istanbul and Mashhad copies. Azarian's abstract says the risala was written "by Kashani himself". Hogendijk's page says he once believed the Mashhad manuscript was not in al-Kashi's hand. Whether an autograph survives is therefore not settled here. **Disputed** ([ISMI](https://ismi.mpiwg-berlin.mpg.de/text/499858); [Hogendijk](https://www.jphogendijk.nl/samarkand.html); [Azarian abstract](https://www.jointmathematicsmeetings.org/amsmtgs/2109_abstracts/1035-01-248.pdf))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [π and its computation through the ages](https://gauss.dartmouth.edu/~m56s13/Gourdan2010notes_computing_pi_through_ages.pdf) | Xavier Gourdon and Pascal Sebah (2010), reading on a Dartmouth course server (Math 56, per the URL) | Places al-Kashi (6·2^27 sides, 1424) in a table of polygon computations of π. Gives the more cautious "about 14 correct decimals" |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Ghiyath al-Din Jamshid Mas'ud al-Kashi](https://mathshistory.st-andrews.ac.uk/Biographies/Al-Kashi/) | MacTutor | Life, Samarkand, the July 1424 treatise, and the *Key to Arithmetic* (completed 2 March 1427) |
| Start | [Al-Kashi](https://mathshistory.st-andrews.ac.uk/Strick/al-kashi.pdf) | H. K. Strick, trans. J. O'Connor, MacTutor | Short illustrated article: the 805,306,368-sided polygon, sin 1°, and Ulugh Beg |
| Start | [The Scholars of Samarkand](https://muslimheritage.com/the-scholars-of-samarkand/) | Muslim Heritage (2005) | Ulugh Beg's madrasa and observatory, and al-Kashi's place among the Samarkand astronomers |
| Deeper | [Al-Kāshī](https://mathshistory.st-andrews.ac.uk/DSB/Al-Kashi.pdf) | A. P. Youschkevitch and B. A. Rosenfeld, *Dictionary of Scientific Biography* (via MacTutor) | The fullest account opened here: the error target, the polygon, the sexagesimal result, comparisons with earlier and later values |
| Deeper | [al-Kāshī (BEA entry)](https://mathshistory.st-andrews.ac.uk/BEA/al_kashi_bea.pdf) | *Biographical Encyclopedia of Astronomers* (via MacTutor) | Al-Kashi as astronomer: the observatory, the *Zij*, sin 1° to 18 places and π to 16 |
| Deeper | [Um estudo da primeira e segunda parte do tratado da circunferência de Al-Kāshī](https://revistas.uece.br/index.php/BOCEHM/article/download/4964/4374/21743) | K. F. C. Andrade, *Boletim Cearense de Educação e História da Matemática* 8(23):665–676 (2021) | In Portuguese. Works through the recursion from the hexagon (R = 60) and the 28 tables |
| Deeper | [Al-Kāshī's Miftāḥ al-Ḥisab, Volume I: Arithmetic (review)](https://www.maa.org/press/maa-reviews/al-k-sh-s-mift-al-isab-volume-i-arithmetic) | Fernando Q. Gouvêa, MAA Reviews | The modern translation of al-Kashi's arithmetic, and his role in building the Samarkand observatory |
| Deeper | [Ludolph van Ceulen](https://mathshistory.st-andrews.ac.uk/Biographies/Van_Ceulen/) | MacTutor | The European polygon computations that finally went past sixteen places (20 in 1596, 35 published 1621) |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Introduction of Al-Risāla Al-Muhītīyya: An English Translation](https://webcf.waybackmachine.org/web/20220512123120/https://ijpam.eu/contents/2009-57-6/5/5.pdf) | M. K. Azarian, *Int. J. Pure and Applied Mathematics* 57(6):903–914 (2009), archived copy | Al-Kashi's own statement of purpose, his critique of earlier values and the horse-hair target, in English |
| Scholar | [The Samarkand school in astronomy and mathematics (ca. 1420 CE)](https://www.jphogendijk.nl/samarkand.html) | Jan P. Hogendijk (Utrecht) | Facsimiles of the Istanbul and Mashhad manuscripts of the treatise, plus a bibliography (Luckey 1953; Hogendijk 2009; Azarian) |
| Scholar | [al-Risālah al-Muḥīṭiyyah](https://ismi.mpiwg-berlin.mpg.de/text/499858) | Islamic Scientific Manuscripts Initiative (ISMI), Max Planck Institute for the History of Science | Catalogue of the 9 known manuscript witnesses, with a description of the method |
| Scholar | [Al-Risala al-Muhitiyya (The Treatise on the Circumference). Preliminary report](https://www.jointmathematicsmeetings.org/amsmtgs/2109_abstracts/1035-01-248.pdf) | M. K. Azarian, AMS meeting abstract (received August 2007) | Dating of the autograph to Sha'ban 827 AH (July 1424) |

**Gaps:** no video was found. Web searches returned no YouTube pages for al-Kashi or his π, so none is listed. Azarian's "Al-Risala al-muhitiyya: a summary" (*Missouri J. Math. Sci.* 22, 2010) on Project Euclid returned only a bot-protection page. Hogendijk's 2009 article ("Al-Kashi's determination of π to 16 decimals in an old manuscript", *ZGAIW* 19) and Luckey's 1953 German edition are cited on Hogendijk's page but were not opened. Britannica's al-Kashi page gave no detail of the computation. The 2019 overview in *Mathematics Interdisciplinary Research* (DOAJ) gave no detail of the method. No full translation of the treatise's computational part was found online.

## What the era leaves behind

- **A sign for nothing.** With zero, place value no longer depends on the reader's guess (Era 1, topic 3), and written column arithmetic becomes possible.
- **The word itself.** "Algorithm" comes from the Latin form of al-Khwarizmi's name, first attached to the written methods of Hindu–Arabic reckoning.
- **Methods that move.** Elimination, remainders and polynomial roots were worked on counting boards in China; the same procedures reappear in Europe centuries later under European names.
- **The first infinite series.** Madhava's series replace ever-finer polygons, and al-Kashi pushes the polygon method to its practical limit in the same century.

Era 3 picks up with logarithms, mechanical calculators and the calculus.
