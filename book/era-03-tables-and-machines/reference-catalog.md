# Era 3 — Tables and Machines: from Cardano's cubic to Hollerith's tabulator

*Reference catalog. Thirteen developments, from 1545 to 1890 CE.*

> **Field note from the visiting historian.** In the second era, procedures travelled. In this one they are made to run without a thinking person: printed as tables so that nobody has to compute, built into wheels so that nobody has to carry, turned into rules that correct themselves, and at last written as instructions for a machine. Along the way, logic becomes arithmetic and arithmetic becomes binary.

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

A note on videos: video pages on YouTube could not be opened from the environment used to build this catalog, so videos appear only where a lecture page (Gresham College) could be opened. Each topic's **Gaps** line says so.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Cardano's cubic](#1-cardanos-cubic) | Tartaglia 1535; *Ars Magna* 1545; Bombelli 1572 | Cubic equations had no general method |
| 2 | [Logarithms](#2-logarithms) | Napier 1614; Briggs 1617, 1624 | Long multiplications for astronomy and navigation |
| 3 | [The carry, mechanized](#3-the-carry-mechanized) | Schickard 1623; Pascal 1642–1645; Leibniz 1673–1694 | Columns of addition, and every carry by hand |
| 4 | [The problem of points](#4-the-problem-of-points) | Pascal and Fermat, 1654 | No fair rule for a game stopped early |
| 5 | [Newton's method](#5-newtons-method) | Newton 1669; Raphson 1690; Simpson 1740 | Formulas stop at degree four, and digit-by-digit roots are slow |
| 6 | [Binary arithmetic](#6-binary-arithmetic) | Harriot c. 1601–1605 (unpublished); Leibniz 1703 | Base-ten arithmetic needs memorised tables |
| 7 | [The bridges of Königsberg](#7-the-bridges-of-königsberg) | Euler 1736 (printed 1741); Hierholzer 1873 | A route question with too many cases to try |
| 8 | [Least squares, and the lost planet](#8-least-squares-and-the-lost-planet) | Ceres 1801; Legendre 1805; Gauss 1809 | More observations than unknowns, and they disagree |
| 9 | [Gauss's fast Fourier transform, 160 years early](#9-gausss-fast-fourier-transform-160-years-early) | Gauss 1805 (printed 1866); Cooley and Tukey 1965 | A periodic fit from N observations costs N² products |
| 10 | [Babbage's difference engine](#10-babbages-difference-engine) | 1822; No. 2 built 1991 | Printed tables full of errors |
| 11 | [Lovelace's Note G](#11-lovelaces-note-g) | 1843 | A general machine has to be told what to do |
| 12 | [Boole's algebra of logic](#12-booles-algebra-of-logic) | 1847, 1854; Shannon 1937 | Logic as a catalogue of syllogisms |
| 13 | [Hollerith's tabulator](#13-holleriths-tabulator) | Patent 1889; census of 1890 | Census tallies took years |

## 1. Cardano's cubic

**When / where:** Scipione del Ferro solved one kind of cubic around 1515 in Bologna and kept it secret; Niccolò Tartaglia found the method again on 13 February 1535 for a public contest with Antonio Fior; Girolamo Cardano published it, with Lodovico Ferrari's solution of the quartic, in *Ars Magna* (Nuremberg, 1545). Rafael Bombelli's *Algebra* (1572) made the formula work when it passes through square roots of negative numbers.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** For three thousand years the people I have followed solved equations of the second degree by a recipe. In Italy the third degree fell, in secret, in a contest, and in a quarrel over a broken oath. The recipe that came out of it worked, but it had a trap: for some cubics with three perfectly ordinary answers, the recipe insisted on taking the square root of a negative number. Rather than throw the recipe away, Bombelli wrote rules for these impossible quantities and calculated straight through them to the real answer.

**What hurt:** cubic equations had no general method; problems were solved case by case, or digit by digit (Era 2, topic 9).
**The step forward:** a substitution that turns a cubic into a quadratic in a new unknown, so the answer is a formula in square and cube roots. When the formula needs the square root of a negative number (the *casus irreducibilis*), rules for calculating with such numbers carry it through.

**Evidence and certainty**

- Del Ferro "solved this cubic equation around 1515 but kept his work a complete secret until just before his death, in 1526"; Fior challenged Tartaglia to a public contest, and "Tartaglia solved all Fior's problems in the space of 2 hours"; "In 1545 he [Cardan] published Ars Magna the first Latin treatise on algebra." **Documented** ([MacTutor, Quadratic, cubic and quartic equations](https://mathshistory.st-andrews.ac.uk/HistTopics/Quadratic_etc_equations/))
- The contest was in 1535; "in the early hours of 13 February 1535, inspiration came to Tartaglia"; MacTutor's Tartaglia page says he solved "all thirty of Fior's problems in less than two hours". In March 1539 Tartaglia gave Cardan the method, in verse, after Cardan swore to keep it secret. **Documented**, though the two MacTutor pages word the contest differently ([MacTutor, Tartaglia](https://mathshistory.st-andrews.ac.uk/Biographies/Tartaglia/))
- In 1543 Cardan and Ferrari saw del Ferro's notes in Bologna, and Cardan then felt free to publish: Ferrari recalled "a little book in the hand of Scipione del Ferro". **Documented** as Cardan's and Ferrari's account ([MacTutor, Cardan](https://mathshistory.st-andrews.ac.uk/Biographies/Cardan/))
- The first calculation with complex numbers: Cardan multiplied 5 + √−15 by 5 − √−15, "dismissing mental tortures", to get 40, and called the subtlety "so subtle that it is useless". **Documented** ([MacTutor, Cardan](https://mathshistory.st-andrews.ac.uk/Biographies/Cardan/))
- Bombelli's *Algebra*: "The first three were published in 1572"; he named √−n "plus of minus" and gave rules such as "Plus of minus times plus of minus makes minus". The DSB says his treatment of complex numbers was "almost that followed today". **Documented** ([MacTutor, Bombelli](https://mathshistory.st-andrews.ac.uk/Biographies/Bombelli/); [DSB, Jayawardene](https://mathshistory.st-andrews.ac.uk/DSB/Bombelli.pdf))
- The standard example: "Bombelli considered the equation x³ = 15x + 4". Cardano's formula gives x as the sum of the cube roots of 2 + √−121 and 2 − √−121; Bombelli set the first equal to a + bi, the second to a − bi, and found a = 2, b = 1, so x = (2 + i) + (2 − i) = 4. His reaction: "At first, the thing seemed to me to be based more on sophism than on truth". **Documented** in secondary sources; neither MacTutor page nor the DSB gives the equation, and the *Algebra* itself was not opened ([Merino, A Short History of Complex Numbers](https://math.mit.edu/~dunkel/Teach/18.04_2019S/historic/Merino_2006.pdf))
- The Fior contest is often given as 30 problems each; the two MacTutor pages agree on the speed but not on the wording. **Documented** (the contest), the details **disputed**
- Tartaglia's reaction: after *Ars Magna* "his intense dislike of Cardan turned into a pathological hatred"; on 10 August 1548 he lost a public debate with Ferrari in Milan. **Documented** ([MacTutor, Tartaglia](https://mathshistory.st-andrews.ac.uk/Biographies/Tartaglia/))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Whopping Cool Math! (March 2013)](https://people.math.harvard.edu/~engelwar/MathS305/Cardanos%20Formula.pdf) | James Tanton, newsletter column (hosted on a Harvard course page) | The Cardano–Tartaglia story, then the cubic formula as guided exercises, ending with an "imaginary" expression that equals 2 |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Quadratic, cubic and quartic equations](https://mathshistory.st-andrews.ac.uk/HistTopics/Quadratic_etc_equations/) | MacTutor (O'Connor and Robertson) | The whole story in one page: del Ferro, Fior, Tartaglia, Cardan, Ferrari, Bombelli |
| Start | [Niccolò Fontana Tartaglia](https://mathshistory.st-andrews.ac.uk/Biographies/Tartaglia/) | MacTutor | The contest, the night of 13 February 1535, the verse, the oath and the 1548 debate |
| Start | [Girolamo Cardano](https://mathshistory.st-andrews.ac.uk/Biographies/Cardan/) | MacTutor | Why Cardan felt free to publish, and the first calculation with complex numbers |
| Deeper | [Rafael Bombelli](https://mathshistory.st-andrews.ac.uk/Biographies/Bombelli/) | MacTutor | "Plus of minus": the first rules for calculating with complex numbers |
| Deeper | [A Short History of Complex Numbers](https://math.mit.edu/~dunkel/Teach/18.04_2019S/historic/Merino_2006.pdf) | Orlando Merino, University of Rhode Island (2006), on an MIT course page | Cardano's formula on x³ = 15x + 4, and how Bombelli found the cube roots 2 ± i |
| Deeper | [Bombelli, Rafael](https://mathshistory.st-andrews.ac.uk/DSB/Bombelli.pdf) | S. A. Jayawardene, *Dictionary of Scientific Biography* (via MacTutor) | How the *Algebra* handles the irreducible case |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Ars Magna, sive de regulis algebraicis (1545)](https://sourcelibrary.org/book/cardano-ars-magna-1545-first-edition-cardano) | Source Library: 172 scans digitized by Smithsonian Libraries (public domain), with an English translation | The book itself, Nuremberg 1545 |

**Gaps:** no video could be opened: a widely shared YouTube video on how imaginary numbers were invented could not be fetched, so none is listed. The *Algebra* of 1572 was not opened, so the x³ = 15x + 4 example rests on secondary sources. Witmer's English translation of *Ars Magna* (1968) was not opened.

## 2. Logarithms

**When / where:** John Napier, *Mirifici logarithmorum canonis descriptio* (Edinburgh, 1614), and his numbering rods (*Rabdologiae*, 1617). Henry Briggs, Gresham College's first professor of geometry, visited Napier in 1615 and 1616; they agreed on logarithms with log 1 = 0 and base 10. Briggs published *Logarithmorum chilias prima* (London, 1617) and *Arithmetica logarithmica* (London, 1624).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Astronomers and navigators of this time spend their nights multiplying long numbers. A Scottish laird spent twenty years on a cure: a table in which every number has a partner, chosen so that adding the partners does the work of multiplying the numbers. A London professor rode for days to meet him, and between them they settled the form that every pocket calculator used until the 1970s. The partners themselves were found by a brutal routine: take the square root of ten, fifty-four times in a row, each time to thirty decimals.

**What hurt:** multiplication, division and roots of long numbers, for astronomy and navigation, were slow and error-prone.
**The step forward:** a table of logarithms turns multiplication into addition, division into subtraction and a root into a division. Briggs built base-10 tables from repeated square roots and finite differences.

**Evidence and certainty**

- "Napier published his system in 1614, but he wrote that it took him some twenty years to invent it." **Documented** ([Stewart, Gresham lecture](https://www.gresham.ac.uk/sites/default/files/27jan97ianstewart_fourcenturiesoflogorithms.pdf); [MacTutor, Napier](https://mathshistory.st-andrews.ac.uk/Biographies/Napier/))
- Napier's numbering rods, published in *Rabdologiae* (1617), were made of ivory, hence "Napier's bones"; Napier died on 4 April 1617. **Documented** ([MacTutor, Napier](https://mathshistory.st-andrews.ac.uk/Biographies/Napier/))
- Briggs visited Napier in the summer of 1615 and again in 1616; Napier proposed tables with log 1 = 0 and base 10, which Briggs then built. MacTutor's Briggs page relays Lilly's story that the two men looked at each other in silence for almost a quarter of an hour. **Documented** (the visits and the agreement); the silence is an anecdote at third hand ([MacTutor, Briggs](https://mathshistory.st-andrews.ac.uk/Biographies/Briggs/))
- *Arithmetica logarithmica* (1624) gives "the logarithms of the natural numbers from 1 to 20,000 and 90,000 to 100,000 computed to 14 decimal places" (MacTutor); Roegel's reconstruction says "from 1 to 20000 and from 90001 to 100000 with 14 decimals". **Documented**; the second range differs by one in its first entry ([MacTutor, Briggs](https://mathshistory.st-andrews.ac.uk/Biographies/Briggs/); [Roegel](https://locomat.loria.fr/briggs1624/briggs1624doc.pdf))
- Briggs's method: successive square roots of 10, "computed these values until n = 54", then a proportion for numbers close to 1, with finite differences to speed up the roots. **Documented** ([Roegel](https://locomat.loria.fr/briggs1624/briggs1624doc.pdf))
- Vlacq's table of 1628 (1 to 100,000, 10 places) was called a second edition of Briggs's table, "although it actually wasn't"; Briggs complained that Vlacq had cut four of his figures. **Documented** ([Roegel](https://locomat.loria.fr/briggs1624/briggs1624doc.pdf))
- Napier "introduced the decimal notation for fractions" (MacTutor). Decimal fractions were already in use (Era 2, topic 11; Stevin, 1585, not opened here). **Disputed** as a first

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Four Centuries of Logarithms](https://www.gresham.ac.uk/sites/default/files/27jan97ianstewart_fourcenturiesoflogorithms.pdf) | Ian Stewart, Gresham Professor of Geometry, 27 January 1997 (transcript) | From Napier's twenty years of work and Briggs's base 10 to the slide rule |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [John Napier](https://mathshistory.st-andrews.ac.uk/Biographies/Napier/) | MacTutor | The 1614 book, the bones, and the agreement with Briggs |
| Start | [Henry Briggs](https://mathshistory.st-andrews.ac.uk/Biographies/Briggs/) | MacTutor | Gresham College, the 1615 visit and the 1624 tables |
| Deeper | [Arithmetica logarithmica (1624): a reconstruction](https://locomat.loria.fr/briggs1624/briggs1624doc.pdf) | Denis Roegel, LOCOMAT project (2011, revised 2014) | How Briggs computed: 54 square roots of 10, proportions near 1, finite differences, and what Vlacq did with the table |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Napier's Descriptio and Constructio, translated](https://www.17centurymaths.com/contents/napiercontents.html) | Ian Bruce, 17centurymaths.com | Napier's own description (1614) and construction (1619) of his logarithms, in English with the Latin |

**Gaps:** no video page could be opened. The Gresham lecture is listed as a transcript only. Stevin's *De Thiende* (1585) was not opened. Napier's definition by two moving points is described in the translations but was not quoted here.

## 3. The carry, mechanized

**When / where:** Wilhelm Schickard described a "calculating clock" to Johannes Kepler in a letter of 20 September 1623 (Tübingen); the machine burned before it was finished. Blaise Pascal began his adding machine in 1642 in Rouen, for his father's tax accounts, published an 18-page *Lettre dédicatoire* about it in 1645 and received a royal privilege in 1649. Gottfried Wilhelm Leibniz showed a wooden model of a machine that could multiply to the Royal Society in London on 1 February 1673; the surviving stepped reckoner dates from about 1694.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** On the counting boards of the first era (topic 6), the carry was a decision: ten counters become one in the next column, and a person had to notice. In this century three men put the carry into brass. Schickard's machine burned. Pascal's dropped a small weighted lever from one wheel to the next, so a carry could ripple through every column without straining the gears. Leibniz built a drum with nine teeth of different lengths, so that one turn of a crank added a whole number, and a sliding carriage made multiplication into repeated addition.

**What hurt:** long columns of addition (taxes, accounts) and long multiplications were done by hand, with every carry a chance for error.
**The step forward:** wheels of ten teeth with an automatic carry (Schickard, Pascal); subtraction by adding the nines' complement; and Leibniz's stepped drum with a shifting carriage, so multiplication is repeated addition and division repeated subtraction.

**Evidence and certainty**

- Schickard to Kepler, 20 September 1623: "What you have done by calculation I have just tried to do by way of mechanics." The first machine "was destroyed in a fire while still incomplete"; the drawings were found among Kepler's papers in the 1950s, and von Freytag Löringhoff of Tübingen reconstructed the machine. **Documented** ([MacTutor, Schickard poster](https://mathshistory.st-andrews.ac.uk/SH/schickard_sh.pdf))
- Wikipedia's Pascaline article says Schickard's drawings had been published at least once a century from 1718, so "rediscovered" overstates it. **Disputed**
- Pascal began in 1642, at 18, because of "the laborious arithmetical calculations required by his father's" work; he built 50 prototypes; nine machines survive; the royal privilege dates from 1649. **Documented** ([Wikipedia, Pascal's calculator](https://en.wikipedia.org/wiki/Pascaline); [Norman, History of Information](https://historyofinformation.com/detail.php?id=382))
- The carry: "The sautoir falls of its own weight", with no contact between wheels; the gears turn one way only, so the machine adds, and subtracts by the nines' complement. **Documented** ([Wikipedia, Pascal's calculator](https://en.wikipedia.org/wiki/Pascaline)); Pascal used weights because a carry across several digits could damage gears like Schickard's ([Tam, CPSC 409 notes](https://cspages.ucalgary.ca/~tam/2025/409F/notes/early_mechanical/early_mechanical_part1_6_per_page.pdf))
- The 1645 pamphlet: "Lettre dédicatoire à Monseigneur le Chancelier sur le sujet de la machine nouvellement inventée par le Sieur B. P."; a machine signed by Pascal in 1652 is in the Musée des Arts et Métiers, Paris. **Documented** ([Norman](https://historyofinformation.com/detail.php?id=382))
- Leibniz had the idea in 1672 in Paris, showed a wooden model to the Royal Society on 1 February 1673, and completed the machine in 1694; the drum (*Staffelwalze*) multiplies by repeated addition, shifting one place for each digit of the multiplier; "a design flaw in the carry mechanism" kept it from working reliably. The surviving machine is in the Gottfried Wilhelm Leibniz Library, Hanover. **Documented** ([Wikipedia, Stepped reckoner](https://en.wikipedia.org/wiki/Stepped_reckoner))
- How many machines Leibniz built: the Pascaline article gives two (1694 and 1706), of which only the 1694 one survives; the Stepped reckoner article calls the survivor the "younger machine". **Disputed**

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Early Mechanical Computers](https://cspages.ucalgary.ca/~tam/2025/409F/notes/early_mechanical/early_mechanical_part1_6_per_page.pdf) | James Tam, CPSC 409 (history of computing), University of Calgary | Schickard's single-tooth carry, Pascal's falling weights, Leibniz's stepped drum and its manual carries |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Pascal's calculator](https://en.wikipedia.org/wiki/Pascaline) | Wikipedia | The sautoir, nines' complement subtraction, the 50 prototypes and the nine survivors |
| Start | [Blaise Pascal Invents a Calculator: The Pascaline](https://historyofinformation.com/detail.php?id=382) | Jeremy Norman, History of Information | The 1645 pamphlet and the 1652 machine in Paris |
| Start | [Wilhelm Schickard](https://mathshistory.st-andrews.ac.uk/SH/schickard_sh.pdf) | MacTutor (illustrated poster, unsigned) | The letter to Kepler, the fire and the reconstruction |
| Deeper | [Stepped reckoner](https://en.wikipedia.org/wiki/Stepped_reckoner) | Wikipedia | The Leibniz wheel, the shifting carriage and the carry flaw |

**Original sources**

No original source could be opened (see **Gaps**).

**Gaps:** no video page could be opened. Pascal's *Lettre dédicatoire* (1645) in translation (Project Euclid, *Modern Logic* 7) returned only a bot-protection page. Schickard's second letter to Kepler (1624) and Leibniz's own description of his machine were not opened. The date of the carry flaw's discovery was not found in an opened source.

## 4. The problem of points

**When / where:** letters between Blaise Pascal (Paris) and Pierre de Fermat (Toulouse), summer 1654, on how to divide the stakes of a game stopped before the end; the question came to Pascal from the Chevalier de Méré. Pascal's *Traité du triangle arithmétique* followed (published 1665), and Christiaan Huygens' *De ratiociniis in ludo aleae* (1657).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Two gamblers stop a game halfway. How should the money be split? Merchants' arithmetic books had offered answers for a century and a half, and they disagreed. In one summer of letters, two Frenchmen settled it, by two different routes. Fermat listed every way the game could have finished and counted. Pascal reasoned one round at a time from the end, filling in a table of fair shares from the finished games back to the stopped one. It is the first time I have seen a hard question answered by building a table of easier answers.

**What hurt:** a stopped game had no fair rule; proportional answers (Pacioli, 1494) gave strange results, and Tartaglia doubted that any division could avoid a lawsuit.
**The step forward:** value the game by what could still happen. Fermat enumerated every continuation; Pascal worked backward one round at a time, each share the average of the two shares one step later, and connected the answer to the arithmetic triangle.

**Evidence and certainty**

- Pacioli's *Summa* (1494) divided the stakes "in proportion to the number of rounds won by each player"; Tartaglia found "counterintuitive results" and wrote that "in whatever way the division is made there will be cause for litigation". **Documented** ([Wikipedia, Problem of points](https://en.wikipedia.org/wiki/Problem_of_points))
- Pascal, 29 July 1654: two gamblers "play, for example, in three throws, and when each has put 32 pistoles at stake"; with two throws against one, "He will then have 48 pistoles and the other will have 16"; with two against none, "he will have 48 and 8, which is 56 pistoles". **Documented** ([Fermat and Pascal on Probability, trans. Sanford](https://www.uu.nl/sites/default/files/correspondentie_fermat_en_pascal.pdf))
- Fermat's method by combinations: Pascal, 24 August 1654, "your theory which proceeds by combinations is very just"; Fermat replies on 29 August and 25 September 1654. **Documented** (same source)
- The letters "laid the foundation for the theory of probability"; they solved the problem of points only for two players; "Pascal was not the first to study the Pascal triangle". **Documented** ([MacTutor, Pascal](https://mathshistory.st-andrews.ac.uk/Biographies/Pascal/))
- The problem came to Pascal from the Chevalier de Méré (Antoine Gombaud) around 1654. **Documented** in secondary sources ([Wikipedia](https://en.wikipedia.org/wiki/Problem_of_points); [Hart, Gresham](https://www.gresham.ac.uk/node/15381))
- The *Traité du triangle arithmétique* was published in 1665, after Pascal's death, and uses the triangle for the division of stakes. **Documented** in Wikipedia; MacTutor gives no date ([Wikipedia](https://en.wikipedia.org/wiki/Problem_of_points))
- Huygens' *De ratiociniis in ludo aleae* (1657), "the first systematic treatise on probability", built on Pascal's expected-value reasoning. **Documented** ([Wikipedia](https://en.wikipedia.org/wiki/Problem_of_points))
- Is Pascal's backward induction the first dynamic programming? The method (a table of answers to smaller games, each from the next) is the same; the name and the general theory are Bellman's (1950s, Era 5). **Conjecture** (this catalog's reading)

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Lottery-Winning Maths](https://www.gresham.ac.uk/node/15381) | Gresham College, Sarah Hart, 31 January 2023 (video and transcript) | How a nobleman's dispute led Pascal and Fermat to the problem of points, and the triangle "known as Pascal's triangle now" |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Problem of points](https://en.wikipedia.org/wiki/Problem_of_points) | Wikipedia | Pacioli, Tartaglia, de Méré, the two methods, the triangle and Huygens |
| Start | [Blaise Pascal](https://mathshistory.st-andrews.ac.uk/Biographies/Pascal/) | MacTutor | The 1654 letters, the arithmetical triangle, and the calculating machine |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Fermat and Pascal on Probability](https://www.uu.nl/sites/default/files/correspondentie_fermat_en_pascal.pdf) | The 1654 letters, trans. Vera Sanford (Smith, *A Source Book in Mathematics*) and Maxine Merrington (David, *Games, Gods and Gambling*), on a Utrecht University page | Pascal's 64 pistoles divided 48 to 16 and 56 to 8; Fermat's "combinations" |

**Gaps:** Pacioli's *Summa* and Pascal's *Traité* were not opened. The York history-of-statistics page and Pulskamp's translations were found but not opened.

## 5. Newton's method

**When / where:** Isaac Newton's *De analysi per aequationes numero terminorum infinitas*, written in Cambridge probably in mid-1669, solves x³ − 2x − 5 = 0 by successive corrections; it was first printed (in Wallis's *Treatise of Algebra*) in 1685 and in full in 1711. Joseph Raphson published his own iteration, *Analysis aequationum universalis*, in London in 1690. Thomas Simpson gave the general form for any equation, and for two equations in two unknowns, in 1740.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Qin Jiushao (Era 2, topic 9) dug out a root one digit at a time. Newton did something bolder: guess, then ask what small correction would make the guess right if the curve were a straight line. The correction is never exactly right, so do it again. With each round the number of correct digits roughly doubles. Newton wrote out a new polynomial at every step; Raphson saw that one could keep correcting the same equation; Simpson saw that the equation need not be a polynomial at all. The method carries Newton's name, though three people made it what it is.

**What hurt:** formulas for roots stop at degree four (topic 1), and digit-by-digit extraction gains only one digit per step.
**The step forward:** replace the curve by its tangent line, solve the line, and repeat; the error is roughly squared at every step, so the correct digits roughly double.

**Evidence and certainty**

- Newton's example is x³ − 2x − 5 = 0, from x₀ = 2: substitute 2 + p, keep the lowest-order terms, 10p − 1 ≈ 0, so p ≈ 0.1; repeating on successively transformed polynomials gives 2.09455147. *De analysi* was written "probably mid-1669" and printed in 1711; the earliest printed account is chapter 94 of Wallis's *A Treatise of Algebra* (1685). **Documented** ([Ypma, SIAM Review 37 (1995)](https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/NewtonRaphson_SIAMRev.pdf))
- Raphson (1690) applied a correction formula repeatedly to the original equation, without Newton's intermediate polynomials, and wrote that his method was "not only, I believe, not of the same origin, but also, certainly, not with the same development". **Documented** ([Ypma](https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/NewtonRaphson_SIAMRev.pdf)); he replaced the divisor in Viète's method by the derivative "without reference to the calculus of either Newton or Leibniz" ([MacTutor, Raphson (DNB)](https://mathshistory.st-andrews.ac.uk/DNB/Raphson.html))
- Simpson (1740) gave the first general formulation by fluxions, with a non-polynomial example, and extended it to two equations in two unknowns; the f′(x) notation of the modern form was published by Lagrange (1798). Ypma: "the Newton-Raphson-Simpson method is a designation more nearly representing the facts of history". **Documented** ([Ypma](https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/NewtonRaphson_SIAMRev.pdf)); Kollerstrom argues that "this invention has migrated back in time" from Simpson to Newton ([Kollerstrom, BJHS 25 (1992)](https://cambridge.org/core/journals/british-journal-for-the-history-of-science/article/thomas-simpson-and-newtons-method-of-approximation-an-enduring-myth/265FA038F1A1873E8850CAFB4468DD8F)). Who deserves the name: **Disputed**
- The modern form's date: Lagrange 1798 (Ypma) or 1797 (DNB via MacTutor). **Disputed**
- Earlier forms: a method algebraically equivalent to Newton's was known to al-Ṭūsī, and al-Kashi used a form of it for xᴾ − N = 0 (Ypma); the Babylonian square-root method is conjectured to be a special case (Wikipedia). **Documented** (Ypma's account), the Babylonian link **conjecture** ([Wikipedia, Newton's method](https://en.wikipedia.org/wiki/Newton%27s_method))
- Quadratic convergence: "the number of correct digits roughly doubles with each step". **Documented** ([Wikipedia](https://en.wikipedia.org/wiki/Newton%27s_method))
- Raphson was elected a Fellow of the Royal Society on 30 November 1689, three days after Halley proposed him. **Documented** ([MacTutor, Raphson (DNB)](https://mathshistory.st-andrews.ac.uk/DNB/Raphson.html))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Newton's method](https://en.wikipedia.org/wiki/Newton%27s_method) | Wikipedia | The method, its history from 1669 to 1740, and why the digits double |
| Deeper | [Historical Development of the Newton–Raphson Method](https://www.math.pku.edu.cn/teachers/litj/notes/numer_anal/NewtonRaphson_SIAMRev.pdf) | Tjalling J. Ypma, *SIAM Review* 37(4):531–551 (1995), on a Peking University course page | The standard account: Newton's x³ − 2x − 5 worked step by step, Raphson, Simpson, and the earlier forms |
| Deeper | [Raphson, Joseph](https://mathshistory.st-andrews.ac.uk/DNB/Raphson.html) | *Dictionary of National Biography* (via MacTutor) | Raphson's life, his 1690 book and his independence from the calculus |
| Scholar | [Thomas Simpson and 'Newton's method of approximation': an enduring myth](https://cambridge.org/core/journals/british-journal-for-the-history-of-science/article/thomas-simpson-and-newtons-method-of-approximation-an-enduring-myth/265FA038F1A1873E8850CAFB4468DD8F) | Nick Kollerstrom, *British Journal for the History of Science* 25(3):347–354 (1992); abstract open | The case that the standard method is Simpson's of 1740 |

**Original sources**

No original source could be opened (see **Gaps**).

**Gaps:** no video page could be opened. *De analysi*, Raphson's *Analysis* and Simpson's *Essays* were not opened as scans; the account rests on Ypma and Kollerstrom.

## 6. Binary arithmetic

**When / where:** Thomas Harriot worked out binary notation and arithmetic in unpublished papers, probably between 1601 and 1605 (England). Juan Caramuel printed a binary system in *Mathesis biceps* (1670). Gottfried Wilhelm Leibniz wrote on the "binary progression" in 1679 and published *Explication de l'Arithmétique Binaire* in the Paris Academy's volume for 1703, after Joachim Bouvet sent him the hexagrams attributed to Fuxi from China (1701).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The Egyptian scribes of the first era (topic 5) multiplied by doubling, and so, without saying it, wrote every number as a sum of powers of two. An Englishman wrote such numbers down with only two signs around 1604 and left them in a drawer. Leibniz, eighty years later, made the system public and said plainly that he was not recommending it for ordinary use. What he saw instead was that its arithmetic needs no memorised tables at all: every rule is "one and one make ten". That is exactly what a machine can do.

**What hurt:** arithmetic in base ten needs memorised tables (the multiplication table), and the reasons behind its rules are hidden.
**The step forward:** two digits only; adding, subtracting and multiplying reduce to a few rules with no tables; and a number's binary digits are its doubling pattern.

**Evidence and certainty**

- Harriot used binary to convert numbers (1101101 = 109) and to add, subtract and multiply, in "the papers which he left unpublished at his death"; "He saw no practical applications for his theory in his day, and he dropped it." **Documented** ([MacTutor, Harriot and binary numbers](https://mathshistory.st-andrews.ac.uk/Extras/Harriot_binary_numbers), after Shirley, 1951)
- Dating Harriot: "It is not possible to determine the exact date of his invention"; it may be "as early as September 1601", and "The latest date ... is probably November 1605"; the often-quoted 1604 is Knuth's conjecture. Strickland argues that Harriot's weighing experiments (1601–1605) and his own positional notation led him to binary, which he treated as "little more than a curiosity". **Documented** (the range), the motive **conjecture** ([Strickland, *Mathematical Intelligencer*, 2023](https://fermatslibrary.com/s/why-did-thomas-harriot-invent-binary))
- Caramuel's *Mathesis biceps vetus et nova* (1670) "probably contains ... the first known publication in Europe on the binary system" (Ineichen, quoted by Bruderer); Wikipedia gives Caramuel's publication as 1700. **Disputed** ([Bruderer, CACM blog](https://cacm.acm.org/blogs/blog-cacm/221749-the-binary-system-was-created-long-before-leibniz/fulltext); [Wikipedia, Binary number](https://en.wikipedia.org/wiki/Binary_number))
- Napier described arithmetic with "double powers" on a chessboard in *Rabdologiae* (1617). **Documented** ([Bruderer](https://cacm.acm.org/blogs/blog-cacm/221749-the-binary-system-was-created-long-before-leibniz/fulltext))
- Leibniz's first known binary paper is from 1679, with conversion and arithmetic algorithms; the *Explication* appeared in 1703 (in the Academy's volume printed in 1705). **Documented** ([Wikipedia](https://en.wikipedia.org/wiki/Binary_number); [Bruderer](https://cacm.acm.org/blogs/blog-cacm/221749-the-binary-system-was-created-long-before-leibniz/fulltext))
- Leibniz, 1703: "The ordinary reckoning of arithmetic is done according to the progression of tens"; in binary "there would no longer be any need to learn anything by heart"; "I am not in any way recommending this way of counting"; Bouvet wrote in 1701 of "this philosophical prince's grand figure, which goes up to 64", and "this Father has deciphered the enigma of Fuxi". **Documented** ([Leibniz, *Explanation of binary arithmetic*, trans. Strickland](https://kastalia.medienhaus.udk-berlin.de/odl/Leibniz.pdf))
- The hexagrams as "an independent, parallel invention of binary notation" (Wikipedia) is a reading of Bouvet's and Leibniz's, not of the *I Ching*'s authors. **Conjecture**

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Binary number](https://en.wikipedia.org/wiki/Binary_number) | Wikipedia | From Pingala and the *I Ching* to Harriot, Leibniz, Boole and Shannon |
| Start | [Harriot and binary numbers](https://mathshistory.st-andrews.ac.uk/Extras/Harriot_binary_numbers) | MacTutor (after J. W. Shirley, *Am. J. Physics* 19, 1951) | Harriot's conversions and binary arithmetic, a century before Leibniz |
| Deeper | [The binary system was created long before Leibniz](https://cacm.acm.org/blogs/blog-cacm/221749-the-binary-system-was-created-long-before-leibniz/fulltext) | Herbert Bruderer, *Communications of the ACM* blog | Harriot, Napier's chessboard, Caramuel 1670 and Leibniz |
| Scholar | [Why Did Thomas Harriot Invent Binary?](https://fermatslibrary.com/s/why-did-thomas-harriot-invent-binary) | Lloyd Strickland, *The Mathematical Intelligencer* (2023), via Fermat's Library | Dating Harriot's manuscripts (1601–1605) and why he invented binary |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Explanation of binary arithmetic (1703)](https://kastalia.medienhaus.udk-berlin.de/odl/Leibniz.pdf) | Leibniz, English text © Lloyd Strickland 2007 (hosted at UdK Berlin) | Leibniz's own case for binary: no tables to memorise, and Fuxi's figures |

**Gaps:** no video page could be opened. Harriot's manuscripts and Leibniz's 1679 paper were not opened. Strickland and Lewis, *Leibniz on Binary* (MIT Press, 2022), was found only as a publisher's listing.

## 7. The bridges of Königsberg

**When / where:** Leonhard Euler presented his solution to the St Petersburg Academy on 26 August 1735; the paper, *Solutio problematis ad geometriam situs pertinentis*, is dated 1736 (*Commentarii* 8, pp. 128–140) but was printed in 1741. Carl Hierholzer's proof that Euler's condition is also sufficient, with a way to construct the route, appeared in *Mathematische Annalen* 6 (1873).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Seven bridges joined the islands and banks of a Prussian city, and its citizens asked whether a walk could cross each exactly once. Listing every route is hopeless. Euler threw away everything but which land touches which bridge, and counted: every time a walker enters a piece of land he must leave it, so the bridges at each piece pair up, except at the start and the end. Four pieces of land had an odd number of bridges, so no walk exists. He called the question "so banal". It is the first time I have seen a problem solved by deciding what to ignore.

**What hurt:** a question about routes had too many cases to try one by one, and no part of existing mathematics seemed to apply.
**The step forward:** keep only the connections (land and bridges, later vertices and edges) and count: a walk over every bridge exactly once exists only if zero or two pieces of land have an odd number of bridges. Hierholzer (1873) proved the converse by building the walk from closed loops spliced together.

**Evidence and certainty**

- Presented on 26 August 1735; published in the *Commentarii* for 1736, pp. 128–140; "Although dated 1736, Euler's paper was not actually published until 1741". **Documented** ([Sachs, Stiebitz and Wilson, *J. Graph Theory* 12 (1988)](https://www.ime.usp.br/~yw/2016/grafinhos/aulas/Paper-Euler-Letters.pdf); [Kraft, Basel, reprinting Hopkins and Wilson](https://bez.unibas.ch/fileadmin/user_upload/bez/Koenigsberg.pdf); [Wikipedia, Seven Bridges of Königsberg](https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg))
- Euler's letters: to Marinoni, 13 March 1736, the problem was "so banal" but "worthy of attention", and he had found "a simple, yet completely established" rule; to Ehler, 3 April 1736, "the solution is based on reason alone". **Documented** ([Sachs, Stiebitz and Wilson](https://www.ime.usp.br/~yw/2016/grafinhos/aulas/Paper-Euler-Letters.pdf); [Paoletti, MAA Convergence](https://www.maa.org/book/export/html/116599))
- The counting: "the number of bridges written next to the letters A, B, C, etc. together add up to twice the total number of bridges", because "each bridge is counted twice, once for each of the two areas which it joins". **Documented** (Euler, quoted by Hopkins and Wilson, in [Kraft](https://bez.unibas.ch/fileadmin/user_upload/bez/Koenigsberg.pdf))
- Euler stated, but did not prove, that the condition is sufficient; "A valid proof was not published until 1873, by Carl Hierholzer." **Documented** ([Sachs, Stiebitz and Wilson](https://www.ime.usp.br/~yw/2016/grafinhos/aulas/Paper-Euler-Letters.pdf); [Eppstein, CS 163 notes](https://www.ics.uci.edu/~eppstein/163/lecture4b.pdf))
- Hierholzer's paper: "Ueber die Möglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren", *Mathematische Annalen* 6 (1873), 30–32. That it appeared after his death is widely stated but was not found in an opened source. **Documented** (the paper), the posthumous detail **conjecture** ([EuDML](https://eudml.org/doc/156599))
- Euler's rule (paragraph 20): "If there are more than two areas to which an odd number of bridges lead, then such a journey is impossible." **Documented** (Hopkins and Wilson's translation, in [Kraft](https://bez.unibas.ch/fileadmin/user_upload/bez/Koenigsberg.pdf))
- Euler drew no graph: "graphs of this kind didn't make their first appearance until the second half of the nineteenth century"; the dots-and-lines "Konigsberg graph" first appeared in W. W. Rouse Ball's book of 1892. **Documented** ([Hopkins and Wilson, in Kraft](https://bez.unibas.ch/fileadmin/user_upload/bez/Koenigsberg.pdf)); the paper is still generally called the first in graph theory ([Eppstein](https://www.ics.uci.edu/~eppstein/163/lecture4b.pdf))
- Today: two bridges were lost to bombing in the Second World War, two others replaced by a highway; three remain, two from Euler's time. **Documented** ([Wikipedia](https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Euler tours](https://www.ics.uci.edu/~eppstein/163/lecture4b.pdf) | David Eppstein, CS 163/265 Graph Algorithms, UC Irvine (Winter 2026) | Euler's condition, Hierholzer's splicing algorithm and its linear running time |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Seven Bridges of Königsberg](https://en.wikipedia.org/wiki/Seven_Bridges_of_K%C3%B6nigsberg) | Wikipedia | The puzzle, Euler's answer, and what became of the bridges |
| Start | [Leonard Euler's Solution to the Konigsberg Bridge Problem](https://www.maa.org/book/export/html/116599) | Teo Paoletti, MAA *Convergence* | Euler's letters, and why he thought the problem trivial |
| Deeper | [Das Problem der Königsberger Brücken](https://bez.unibas.ch/fileadmin/user_upload/bez/Koenigsberg.pdf) | Hanspeter Kraft, University of Basel (in German), with Hopkins and Wilson's "The Truth about Königsberg" (2004) reprinted | What Euler actually did, in his own counting, without a graph |
| Scholar | [An Historical Note: Euler's Königsberg Letters](https://www.ime.usp.br/~yw/2016/grafinhos/aulas/Paper-Euler-Letters.pdf) | Horst Sachs, Michael Stiebitz and Robin J. Wilson, *Journal of Graph Theory* 12(1):133–139 (1988) | The letters of 1736 and the publication dates |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Solutio problematis ad geometriam situs pertinentis (E53)](https://phantom.cs.qc.cuny.edu/gavva/teaching/s24/euler-bridges-paper.pdf) | Euler, 1736 (printed 1741); Euler Archive copy on a Queens College course page | The paper itself, in Latin |
| Scholar | [Ueber die Möglichkeit, einen Linienzug ohne Wiederholung und ohne Unterbrechung zu umfahren](https://eudml.org/doc/156599) | Carl Hierholzer, *Mathematische Annalen* 6:30–32 (1873), EuDML record with a link to the Göttingen scan | The proof of sufficiency, and the construction |

**Gaps:** no video page could be opened. The English translation in Biggs, Lloyd and Wilson, *Graph Theory 1736–1936*, was not opened, so Euler's paragraphs are quoted only through Hopkins and Wilson. The Göttingen scan of Hierholzer's paper was not opened.

## 8. Least squares, and the lost planet

**When / where:** Giuseppe Piazzi found Ceres in Palermo on 1 January 1801 and lost it in the Sun's glare in February. Carl Friedrich Gauss, aged 24, computed an orbit from Piazzi's observations; Franz Xaver von Zach and Heinrich Olbers found Ceres again in December 1801 close to Gauss's prediction. Adrien-Marie Legendre published the method of least squares in Paris in 1805, in an appendix to his book on comet orbits; Gauss published his version in *Theoria motus corporum coelestium* (1809), saying he had used it since 1795.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Astronomers have more measurements than unknowns, and the measurements disagree. Which answer is right? None of them, exactly. A French geometer said: choose the answer that makes the sum of the squared errors as small as possible, because then the errors balance one another and no single bad measurement takes over. The arithmetic is old (the elimination of Era 2, topic 1); the new thing is a rule for what counts as best. A young German had already used it, he said, to find a planet that everyone else had lost.

**What hurt:** more observations than unknowns give equations that cannot all hold; astronomers and surveyors combined them by ad hoc rules.
**The step forward:** choose the values that make the sum of squared residuals smallest; setting its derivatives to zero gives as many linear "normal equations" as unknowns, solved by elimination.

**Evidence and certainty**

- Piazzi discovered Ceres on 1 January 1801; Gauss's prediction "differed greatly from the others", and Zach found it on 7 December 1801 "almost exactly where Gauss had predicted" (MacTutor). Weiss gives 22 observations over 41 days and has Zach on 7 December and Olbers on 31 December; other accounts say New Year's Eve. **Documented** (the discovery and recovery), the recovery dates **disputed** ([MacTutor, Gauss](https://mathshistory.st-andrews.ac.uk/Biographies/Gauss/); [Weiss, Rutgers, 1999](https://ow3.math.rutgers.edu/~cherlin/History/Papers1999/weiss.html); [thatsmaths, 2021](https://thatsmaths.com/2021/06/24/gauss-predicts-the-orbit-of-ceres/))
- Piazzi "had only been able to observe 9 degrees of its orbit" (MacTutor; Weiss agrees). **Documented**
- Did Gauss use least squares for Ceres? MacTutor and Weiss say yes; thatsmaths notes it is unclear. **Disputed**
- Legendre, 1805: the method "consiste à rendre minimum la somme des quarrés des erreurs", which establishes "entre les erreurs une sorte d'équilibre" that keeps the extreme errors from prevailing. **Documented** ([Legendre, *Appendice. Sur la méthode des moindres quarrés*, scan](https://www.york.ac.uk/depts/maths/histstat/legendre2.pdf))
- Gauss, 1809: "principium nostrum quo jam inde ab anno 1795 usi sumus" ("our principle, which we have used since 1795"). Legendre published first; the evidence suggests independent discovery, Gauss earlier, but Stigler could not reproduce Gauss's 1799 results with least squares. **Disputed** (priority) ([Chalberg, MAA HOMSIGMAA](https://old.maa.org/sites/default/files/pdf/upload_library/46/HOMSIGMAA/Chalberg-RegressionHistoryPaper.pdf))
- Translations of Gauss's least-squares writings: Davis (1857) of the *Theoria motus*; G. W. Stewart (SIAM, 1995) of the *Theoria combinationis* (1821, 1823). **Documented** ([Pulskamp's Gauss page](https://gtfp.cs.rhul.ac.uk/pulskamp/Gauss/Gauss.html))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Gauss Predicts the Orbit of Ceres](https://thatsmaths.com/2021/06/24/gauss-predicts-the-orbit-of-ceres/) | *thatsmaths* blog (24 June 2021) | The lost planet and the prediction, with the caution about least squares |
| Start | [Gauss and Ceres](https://ow3.math.rutgers.edu/~cherlin/History/Papers1999/weiss.html) | Leorah Weiss, history of mathematics term paper, Rutgers (1999) | Piazzi's 22 observations over 41 days, the three Gauss used, and the recovery |
| Start | [Carl Friedrich Gauss](https://mathshistory.st-andrews.ac.uk/Biographies/Gauss/) | MacTutor | Ceres, the *Theoria motus*, and Gauss's life |
| Deeper | [Regression Analysis – A Powerful Tool and Riveting Drama](https://old.maa.org/sites/default/files/pdf/upload_library/46/HOMSIGMAA/Chalberg-RegressionHistoryPaper.pdf) | Tim Chalberg, Pacific Lutheran University, MAA HOMSIGMAA | Legendre, Gauss, Adrain and the priority dispute |
| Scholar | [Gauss and the method of least squares](https://gtfp.cs.rhul.ac.uk/pulskamp/Gauss/Gauss.html) | Richard Pulskamp, sources in the history of probability and statistics | Where to find Gauss's least-squares writings in translation |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Sur la méthode des moindres quarrés](https://www.york.ac.uk/depts/maths/histstat/legendre2.pdf) | Legendre, appendix to *Nouvelles méthodes pour la détermination des orbites des comètes* (Paris, 1805), scan on the University of York history of statistics pages | The first publication of least squares, in French |

**Gaps:** no video page could be opened. Stigler's "Gauss and the Invention of Least Squares" (*Annals of Statistics* 9, 1981) on Project Euclid returned a bot-protection page. Gauss's *Theoria motus* was not opened.

## 9. Gauss's fast Fourier transform, 160 years early

**When / where:** Carl Friedrich Gauss, Göttingen, most likely October–November 1805: the unpublished treatise *Theoria interpolationis methodo nova tractata*, on fitting periodic curves to the observed positions of the asteroids Pallas and Juno. It was printed only in volume 3 of his collected works (1866). James W. Cooley and John W. Tukey published the method for computers in *Mathematics of Computation* 19 (1965), 297–301, without knowing of Gauss's version; Heideman, Johnson and Burrus traced it back to Gauss in 1984–1985.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** An asteroid goes round and round, so its position is a periodic curve, and Gauss wanted the sines and cosines that fit twelve observations of Pallas. Done directly, every coefficient needs every observation: twelve times twelve products. Gauss noticed that twelve is three times four. Fit the four observations in each of three groups first, then combine the three small fits. The work shrinks, and for long series it shrinks enormously. He left it in Latin among his papers, where it waited for the electronic computer to make it indispensable.

**What hurt:** computing the coefficients of a periodic fit (a discrete Fourier transform) from N observations takes about N² multiplications.
**The step forward:** if N = N₁ × N₂, split the observations into N₂ interleaved groups, transform each group, then combine the results with a second, smaller set of transforms; repeated over all factors, about N log N operations.

**Evidence and certainty**

- The authors "infer that GAUSS wrote this treatise in October-November, 1805"; it "appeared only in his collected works" (Werke, vol. 3, 1866). **Documented** for the publication, **conjecture** (a well-argued inference) for the month ([Heideman, Johnson and Burrus, *Archive for History of Exact Sciences*, 1985](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-3.pdf))
- "The example of N = 12 for the orbit of the asteroid Pallas was worked out in Article 28"; Gauss did it both as 4 × 3 and as 3 × 4, with the index change n = N₂·n₁ + n₂; the eccentricity of Juno quoted in the treatise (0.254236) helps date it. **Documented** ([Heideman, Johnson and Burrus](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-3.pdf))
- The treatise predates Fourier's presentation to the Paris Academy in December 1807 (published 1822). **Documented** (same source)
- Rediscoveries before 1965: Runge (1903), Danielson and Lanczos (1942), Good's prime-factor algorithm (1958). **Documented** (same source)
- Cooley and Tukey: "a number of operations proportional to N log N rather than N²", and "less than 2N log₂ N operations" for N a power of 2. **Documented** ([Cooley and Tukey, 1965](https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf))
- Cooley and Tukey later wrote that the paper "was at first credited with a great discovery", and that the algorithm "should be put in the public domain to prevent anyone from patenting it". **Documented** ([Cooley and Tukey, *Citation Classic*, 1993](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-1.pdf))
- The Pallas observations themselves are not printed in the sources opened here, so the topic's program uses its own test data. **Gap**

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Historical Notes on the Fast Fourier Transform](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-2.pdf) | James W. Cooley, Peter A. W. Lewis and Peter D. Welch (1967), on a University of Washington course page | What was known before 1965, written two years after it |
| Scholar | [Gauss and the History of the Fast Fourier Transform](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-3.pdf) | Michael T. Heideman, Don H. Johnson and C. Sidney Burrus, *Archive for History of Exact Sciences* (1985) | The discovery that Gauss had the FFT in 1805, with his Pallas and Juno examples |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [An Algorithm for the Machine Calculation of Complex Fourier Series](https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf) | James W. Cooley and John W. Tukey, *Mathematics of Computation* 19:297–301 (1965), on a UC Davis course page | The paper that made the FFT standard |
| Scholar | [On the Origin and Publication of the FFT Paper](https://faculty.washington.edu/seattle/physics541/%202010-Fourier-transforms/history-1.pdf) | Cooley and Tukey, *Current Contents* "Citation Classic" (1993) | The authors' own account of how the 1965 paper came about |

**Gaps:** no video page could be opened. Gauss's *Theoria interpolationis* (Werke 3) was not opened, so his Pallas data are not reproduced. The IEEE ASSP Magazine version (1984) of Heideman, Johnson and Burrus was not opened.

## 10. Babbage's difference engine

**When / where:** Charles Babbage, London. In 1821, checking astronomical tables with John Herschel, he exclaimed that he wished they had been "executed by steam". On 14 June 1822 he announced a small working model to the Astronomical Society, and in a letter to Sir Humphry Davy described it computing x² + x + 41. Difference Engine No. 1, built with the engineer Joseph Clement, stopped in 1833 with about a seventh assembled. His Difference Engine No. 2 (designed 1847–1849) was built by the Science Museum, London: the calculating section in 1991, the printer in 2002.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Since Briggs (topic 2), the world has run on printed tables, and the tables are full of mistakes: wrong digits computed, right digits set wrongly in type. An English mathematician noticed that a polynomial's values can be produced with no multiplication at all. Keep its differences in a column, and every new value is a chain of additions. Additions are what wheels do well. So he designed a machine of columns that adds and, at the end, sets the answer straight into type, so that no human hand ever copies a number.

**What hurt:** printed tables for navigation and astronomy contained errors, both of computation and of typesetting.
**The step forward:** the method of finite differences: for a polynomial of degree n the nth differences are constant, so each new table entry needs only n additions; built as wheels, with the result printed directly by the machine.

**Evidence and certainty**

- Babbage: "I wish to God these calculations had been executed by steam"; Herschel: "It is quite possible." **Documented** as Babbage's own anecdote ([Mike James, I Programmer, 14 June 2022](https://i-programmer.info/news/82-heritage/15481-difference-engine-reported-14-june-1822.html))
- 14 June 1822: a note to the (Royal) Astronomical Society; "in the engine which is just finished I have limited myself to two orders of differences"; tables "of square and triangular numbers, as well as a table from the singular x² + x + 41". **Documented** ([James](https://i-programmer.info/news/82-heritage/15481-difference-engine-reported-14-june-1822.html))
- The letter to Davy (1822): the model "proceeded to make a table from the formula x² + x + 41"; thirty numbers in "two minutes and thirty seconds", and in another trial figures "at the rate of forty-four in a minute". **Documented** (excerpt from *The Works of Charles Babbage*, vol. 2, ed. Campbell-Kelly, at [ed-thelen.org](https://ed-thelen.org/bab/bab-letter.html))
- Difference Engine No. 1 stopped in 1833 after a dispute with Clement over compensation; about one-seventh was assembled. **Documented** ([James](https://i-programmer.info/news/82-heritage/15481-difference-engine-reported-14-june-1822.html)); the cost to the government (often quoted as £17,000) was not found in an opened source
- Difference Engine No. 2: designs "1847-9"; "The calculating section was finished in 1991 in time for the bicentenary of Babbage's birth"; "the printing and stereotyping apparatus was completed in 2002"; 8,000 parts, five tons; "The completed machine works as Babbage intended." **Documented** ([Computer History Museum, A Modern Sequel](https://www.computerhistory.org/babbage/modernsequel/); [Science Museum Group collection](https://collection.sciencemuseumgroup.org.uk/objects/co62748))
- The method in print, 1834: the *Edinburgh Review* explained that Babbage had "literally thrown" the method of differences "into wheel-work", and that errors in logarithm tables came from type moved after it was set: "the types, as first composed, were correct". **Documented** ([*The Calculating Engine*, Edinburgh Review, July 1834, Project Gutenberg](https://gutenberg.org/files/71292/71292-h/71292-h.htm)); the reviewer is unnamed there (usually identified as Dionysius Lardner, **conjecture** here)

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [200 Years Ago Charles Babbage Proposed His Difference Engine](https://i-programmer.info/news/82-heritage/15481-difference-engine-reported-14-june-1822.html) | Mike James, I Programmer (14 June 2022) | The note of 1822, the model, x² + x + 41, Clement, and why Engine No. 1 stopped |
| Start | [A Modern Sequel](https://www.computerhistory.org/babbage/modernsequel/) | Computer History Museum | How the Science Museum built Difference Engine No. 2 and found that it works |
| Start | [Difference Engine No. 2](https://collection.sciencemuseumgroup.org.uk/objects/co62748) | Science Museum Group collection | The machine itself, with Doron Swade's role |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Letter to Sir Humphry Davy (excerpt)](https://ed-thelen.org/bab/bab-letter.html) | Babbage, 1822, from *The Works of Charles Babbage* vol. 2 (ed. Campbell-Kelly), on Ed Thelen's site | Babbage on his working model: x² + x + 41 at forty-four figures a minute |
| Scholar | [The Calculating Engine (Edinburgh Review, 1834)](https://gutenberg.org/files/71292/71292-h/71292-h.htm) | Project Gutenberg eBook 71292 | A contemporary explanation of the method of differences and of errors in printed tables |

**Gaps:** no video page could be opened. Babbage's 1822 note itself and the full letter to Davy were not opened. The cost of Engine No. 1 and the orders of difference of Engine No. 2 were not found in opened sources.

## 11. Lovelace's Note G

**When / where:** Luigi Menabrea published a French account of Babbage's Analytical Engine in 1842 (Geneva). Ada Lovelace translated it and added seven notes, A to G, signed only "A.A.L."; they appeared in *Taylor's Scientific Memoirs* (London) in August 1843. Note G ends with a table that computes a Bernoulli number on the Engine, step by step.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Babbage's second machine (designed in the 1830s, never built) was different in kind: a store of numbered columns, a mill that does arithmetic, and a train of punched cards, borrowed from the Jacquard loom, that says which operation to do on which columns. A translator's notes, longer than the paper they annotate, worked out what such a machine could do: repeat a group of cards (a loop), act on symbols as well as numbers, perhaps compose music. To show it, she laid out every step of a calculation of a Bernoulli number. One step has its division the wrong way round. It is still the first such plan I have found in print.

**What hurt:** a machine that only follows a fixed pattern (topic 10) can make only one kind of table; and no one had described how a general machine would be told what to do.
**The step forward:** a calculation written as a numbered sequence of operations on named storage places, with repetition, for a machine that reads its instructions from cards.

**Evidence and certainty**

- Lovelace's paper appeared in *Taylor's Scientific Memoirs* in August 1843, 66 pages of which "forty-one make up her appendices", signed only "A.A.L.". **Documented** ([Hollings, Martin and Rice, Bodleian blog, 26 July 2018](https://blogs.bodleian.ox.ac.uk/adalovelace/2018/07/26/ada-lovelace-and-the-analytical-engine/))
- Note A: the Analytical Engine "weaves algebraical patterns just as the Jacquard-loom weaves flowers and leaves". **Documented** ([Menabrea and Lovelace, *Sketch of the Analytical Engine*, Project Gutenberg](https://gutenberg.org/files/75107/75107-src/75107-src.htm))
- Note G: "The Analytical Engine has no pretensions whatever to originate any thing." **Documented** (quoted in [Di Donato, University of Pisa, 2004](https://btfp.sp.unipi.it/dida/telema/scheda_ada.html))
- The table computes the eighth Bernoulli number (B₈ today; Lovelace's B₇). Lovelace chose a method whose "object is not simplicity or facility of computation, but the illustration of the powers of the engine". **Documented** ([Wikipedia, Note G](https://en.wikipedia.org/wiki/Note_G); [Hollings, Martin and Rice](https://blogs.bodleian.ox.ac.uk/adalovelace/2018/07/26/ada-lovelace-and-the-analytical-engine/))
- The bug: in operation 4 "the division is the wrong way round"; run as printed, the program "would fail to generate Bernoulli numbers correctly". It was never run in Babbage's or Lovelace's lifetime. **Documented** ([Wikipedia, Note G](https://en.wikipedia.org/wiki/Note_G))
- "The first computer program"? The table is "often described" so, but Hollings, Martin and Rice call it an execution trace, the program proper being the card decks; Bromley found "several dozen sample programs prepared by Babbage between 1837 and 1840", unpublished and simpler. **Disputed** ([Hollings, Martin and Rice](https://blogs.bodleian.ox.ac.uk/adalovelace/2018/07/26/ada-lovelace-and-the-analytical-engine/); [Wikipedia, Note G](https://en.wikipedia.org/wiki/Note_G))
- Loops and music: "A complex mechanism allowed the machine to repeat a deck of cards, so as to execute a loop"; the engine "might compose elaborate and scientific pieces of music of any degree of complexity or extent". **Documented** ([Hollings, Martin and Rice](https://blogs.bodleian.ox.ac.uk/adalovelace/2018/07/26/ada-lovelace-and-the-analytical-engine/))
- Lovelace lived 10 December 1815 – 27 November 1852. **Documented** ([MacTutor, Lovelace poster](https://mathshistory.st-andrews.ac.uk/SH/lovelace_sh.pdf))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Note G](https://en.wikipedia.org/wiki/Note_G) | Wikipedia | What the table computes, the bug in operation 4, and the "first program" debate |
| Start | [Ada Lovelace](https://mathshistory.st-andrews.ac.uk/SH/lovelace_sh.pdf) | MacTutor (illustrated poster) | Her life and the 1843 translation in one page |
| Deeper | [Ada Lovelace and the Analytical Engine](https://blogs.bodleian.ox.ac.uk/adalovelace/2018/07/26/ada-lovelace-and-the-analytical-engine/) | Christopher Hollings, Ursula Martin and Adrian Rice, Bodleian Libraries (2018) | The historians who studied her papers: the notes, the loops, the execution trace, and music |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Sketch of the Analytical Engine, with notes by the translator](https://gutenberg.org/files/75107/75107-src/75107-src.htm) | L. F. Menabrea, trans. with notes by A.A.L. (London, 1843), Project Gutenberg | The paper and the notes, including the Jacquard sentence (the copy opened was cut off before Note G's table) |

**Gaps:** no video page could be opened. The Note G table itself could not be read in an opened copy (the Gutenberg text was truncated in the fetch; the Fourmilab edition needed permission that could not be given), so the topic's program rebuilds Lovelace's recurrence rather than her exact table, and quotes the bug only as Wikipedia describes it. Bromley's paper on Babbage's earlier programs was not opened.

## 12. Boole's algebra of logic

**When / where:** George Boole, a schoolmaster in Lincoln, published *The Mathematical Analysis of Logic* in 1847; appointed the first professor of mathematics at Queen's College, Cork, in 1849, he published *An Investigation of the Laws of Thought* in 1854. In 1937 Claude Shannon showed in his MIT master's thesis (published 1938) that Boole's algebra describes circuits of switches.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Since Aristotle, logic had been a list of valid argument forms, learned by heart. A self-taught teacher wrote logic as algebra: letters for classes of things, multiplication for "and", and one law that ordinary numbers do not obey, x times x equals x. Only two numbers satisfy it, nothing and everything, 0 and 1. Reasoning became calculation, done by rules a clerk could follow. Eighty years later a student noticed that a switch, too, is either open or closed, and the algebra of thought became the algebra of circuits.

**What hurt:** logic was a catalogue of syllogisms, checked by memory and rhetoric; there was no way to calculate a conclusion from many premises.
**The step forward:** symbols for classes and propositions, with "and" as multiplication and the law x² = x; any question becomes an equation to be solved or expanded, and every symbol takes only the values 0 and 1.

**Evidence and certainty**

- Boole was born on 2 November 1815 in Lincoln and died on 8 December 1864 near Cork; in August 1849 he was announced as "the first Professor of Mathematics at Queen's College, Cork". *The Laws of Thought* (1854) "approached logic in a new way reducing it to a simple algebra" and "began the algebra of logic called Boolean algebra which now finds application in computer construction, switching circuits etc." **Documented** ([MacTutor, Boole](https://mathshistory.st-andrews.ac.uk/Biographies/Boole/))
- *The Mathematical Analysis of Logic* (1847), subtitled "a calculus of deductive reasoning"; *The Laws of Thought* his "greatest work". **Documented** ([Lynch, review of MacHale, *Irish Math. Soc. Bulletin* 74, 2014](https://www.maths.tcd.ie/pub/ims/bull74/Lynch2.pdf))
- The law: "x² = x", "the expression of a second general law of those symbols"; "the equation x² = x, considered as algebraic, has no other roots than 0 and 1", so the symbols "admit indifferently of the values 0 and 1, and of these values alone". **Documented** ([Boole, *The Laws of Thought*, ch. II, Project Gutenberg](https://www.gutenberg.org/files/15114/15114-pdf.pdf))
- Shannon's thesis (MIT, 1937; published 1938) showed that Boolean algebra "could be used to simplify the arrangement of the relays"; Goldstine called it "surely ... one of the most important master's theses ever written", and Gardner "possibly the most important, and also the most famous, master's thesis of the century". **Documented** ([Wikipedia, A Symbolic Analysis of Relay and Switching Circuits](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits))
- What set Boole writing in 1847 (often said to be the quarrel between De Morgan and Hamilton) is not stated in the opened sources. **Conjecture**

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [George Boole](https://mathshistory.st-andrews.ac.uk/Biographies/Boole/) | MacTutor | His life from Lincoln to Cork, and the two books |
| Start | [A Symbolic Analysis of Relay and Switching Circuits](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits) | Wikipedia | How Shannon turned Boole's algebra into circuit design |
| Deeper | [The Life and Work of George Boole (review)](https://www.maths.tcd.ie/pub/ims/bull74/Lynch2.pdf) | Peter Lynch, *Irish Mathematical Society Bulletin* 74:97–101 (2014) | A short guide to MacHale's biography and to why Boole matters |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [An Investigation of the Laws of Thought (1854)](https://www.gutenberg.org/etext/15114) | George Boole, Project Gutenberg eBook 15114 (public domain; [PDF](https://www.gutenberg.org/files/15114/15114-pdf.pdf)) | The book: x² = x, and logic as an algebra of 0 and 1 |
| Scholar | [A Symbolic Analysis of Relay and Switching Circuits](https://dspace.mit.edu/bitstream/handle/1721.1/11173/34541425.pdf%20?sequence=1) | Claude E. Shannon, MIT master's thesis (signed 10 August 1937; degree listed 1940), MIT DSpace | "This calculus is shown to be exactly analogous to the Calculus of Propositions used in the symbolic study of logic" |

**Gaps:** no video page could be opened. *The Mathematical Analysis of Logic* (1847) was not opened.

## 13. Hollerith's tabulator

**When / where:** Herman Hollerith, a Columbia School of Mines graduate (Engineer of Mines, 1879), patented "the art of compiling statistics" with punched cards (US 395,782, issued 8 January 1889; first application 1884) and described "An Electric Tabulating System" in Columbia's *School of Mines Quarterly* (April 1889). His machines won the Census Office's trial in 1888 and counted the 1890 census.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The young republic counts its people every ten years, and the counting now takes nearly as long as the interval. Clerks made a tally mark in a small square for every person with every property, then counted the marks. An engineer put each person on a card, as holes. A press brings pins down on the card; where there is a hole, a pin dips into a cup of mercury, closes a circuit, and a dial moves on by one. The same cards can be counted again and again for new questions, and sorted into drawers by what is punched on them. Tally marks, the very first algorithm I recorded (Era 1, topic 1), have become electrical.

**What hurt:** tabulating a census by hand, with tally marks, took years and could not answer new questions without starting again.
**The step forward:** one punched card per person; electrical counting through the holes; and sorting the cards by their punches so that combinations can be counted (later, sorting by one column at a time).

**Evidence and certainty**

- Hollerith on hand tabulation: "making tally-marks in small squares and then adding and counting such tally-marks"; without new methods the next census would be "impossible" "on account of the time and expense involved"; records become machine-readable by "punching holes in cards or strips of paper, which perforations can then be used to control circuits"; relays count combinations such as "the number of native white males, of native white females". **Documented** ([Hollerith, *An Electric Tabulating System*, 1889, Columbia University Computing History](https://columbia.edu/cu/computinghistory/hh/index.html))
- The patent: US 395,782, "Art of compiling statistics", issued 8 January 1889, a division of an application of 23 September 1884; claim 2: "recording separate statistical items pertaining to the individual by holes or combinations of holes punched in sheets", counted by electro-magnetic counters. **Documented** ([Google Patents](https://patents.google.com/patent/US395782))
- The 1888 trial on 1880 data from four areas of St Louis: data capture 144.5 and 100.5 hours for the two rivals, 72.5 for Hollerith; preparation for tabulation 44.5 and 55.5 hours against Hollerith's 5.5. **Documented** ([US Census Bureau, The Hollerith Machine](https://www.census.gov/about/history/bureau-history/census-innovations/technology/hollerith-machine.html))
- The machine: "Pins that passed through the punch card completed an electrical circuit when contacting the mercury below", advancing one of 40 dials; a bell signalled each card; a sorting table told the operator which drawer to use; "An experienced clerk could process 80 cards per minute". **Documented** (same source)
- The saving: the machines "reduced a ten-year job to three months" and saved "five million dollars", though Columbia's page notes that other sources give different timeframes. **Disputed** (the figures) ([da Cruz, Columbia University Computing History](https://columbia.edu/cu/computinghistory/hollerith.html))
- The work earned Hollerith a Columbia PhD in 1890 "upon the work which he has performed". **Documented** ([da Cruz](https://columbia.edu/cu/computinghistory/hollerith.html))
- Punched-card machines descended from Hollerith's were used at the Census Bureau "until computers replaced it in the 1950s"; his company is an ancestor of IBM. **Documented** (the Census Bureau's use); the company history was not checked in an opened source (**conjecture** here)

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Hollerith Machine](https://www.census.gov/about/history/bureau-history/census-innovations/technology/hollerith-machine.html) | US Census Bureau history | The 1888 trial in hours, the mercury cups, the 40 dials and the sorting table |
| Start | [Herman Hollerith](https://columbia.edu/cu/computinghistory/hollerith.html) | Frank da Cruz, Columbia University Computing History (2001, updated 2023) | His life, the patent, the PhD and the 1890 census |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [An Electric Tabulating System](https://columbia.edu/cu/computinghistory/hh/index.html) | Herman Hollerith, *School of Mines Quarterly* X(16):238–255 (April 1889), reproduced by Columbia University | His own description: the problem, the cards, the circuits and the sorting box |
| Scholar | [US 395,782: Art of compiling statistics](https://patents.google.com/patent/US395782) | Herman Hollerith, US patent issued 8 January 1889, Google Patents | The claims: holes for statistical items, counted by electric circuits |

**Gaps:** no video page could be opened. The founding dates of the Tabulating Machine Company and of IBM, and the time the 1890 count took, were not confirmed in an opened source. Later card sorters that sort one column at a time (the basis of radix sort) are not covered by an opened source here; the topic's page marks that link as a conjecture.

## What the era leaves behind

- **Tables instead of thinking.** Logarithms (2) and the difference engine (10) put computation into print, so that users only look things up; the engine's aim was to remove the human copyist entirely.
- **Machines that carry, then machines that follow orders.** From Pascal's falling lever (3) to Babbage's columns (10) and Lovelace's sequence of operations with repetition (11): the step from a calculator to a program.
- **Iteration and error.** Newton's method (5) corrects a guess until it is good enough; least squares (8) defines what "best" means when data disagree; Gauss's FFT (9) shows that the order of the work can matter more than the work.
- **Two values.** Binary (6) and Boole's algebra (12) meet in Shannon's switching circuits, and Hollerith's holes (13) are already data that a machine reads.
- **Counting what to ignore.** Euler's bridges (7) and Pascal's table of fair shares (4) solve questions by throwing away detail and counting structure: graphs and dynamic programming, under other names.

Era 4 picks up with the foundations: what can be computed at all (Hilbert, Gödel, Church and Turing) and the first electronic computers.
