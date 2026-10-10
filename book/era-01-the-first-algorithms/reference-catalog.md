# Era 1 — The First Algorithms: from tally marks to the sieve

*Reference catalog, sample installment. Nine developments, from about 44,000 years ago to about 240 BCE.*

> **Field note from the visiting historian.** I came to catalog how this species learned to compute. Before they had writing, they cut notches in bone. By the time they built libraries, they had written down procedures that work for *any* number. Those procedures were their first algorithms. Each entry below records one new development. For each I set down the date as best it can be known, the problem that forced it, what changed, and where to watch, read and check the evidence yourself.

## How to use this catalog

Every link was opened before it was listed. YouTube links were also checked against YouTube's own title record. Links are tagged by level, so a high-school reader and a PhD scholar can both find their way in:

| Tag | Meaning |
|---|---|
| **Start** | No background needed. Watch or read this first. |
| **Deeper** | University level: the mechanism, the proof, the analysis. |
| **Scholar** | Primary sources and research papers: the evidence itself, and the arguments about it. |

Each claim also carries a certainty label:

- **Documented**: stated by the holding museum, the primary text, or standard scholarship.
- **Conjecture**: a reasonable reading that the evidence does not settle.
- **Disputed**: scholars disagree; the main positions are given.

The **Atlas** line points to the matching chapters of *The Evolutionary Atlas of Algorithms and Data Structures*. The **Code** line points to a tested Java program in this repository, when one exists.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Tally marks](#1-tally-marks--one-mark-per-thing) | c. 44,000–20,000 years ago | Remembering *how many* without words for big numbers |
| 2 | [Grouping, written numerals and the first carry](#2-grouping-written-numerals-and-the-first-carry) | Tokens from c. 7500 BCE; numerals c. 3200–3000 BCE | Long rows of marks are slow to write and impossible to read at a glance |
| 3 | [Babylonian place value and reciprocal tables](#3-babylonian-place-value-and-reciprocal-tables) | Place value c. 2100 BCE; school tables c. 1800 BCE | Additive numerals make multiplication and division painful |
| 4 | [The square root of 2 on YBC 7289](#4-the-square-root-of-2-on-ybc-7289) | c. 1800–1600 BCE | Some lengths cannot be measured exactly, so they must be computed |
| 5 | [Egyptian multiplication by doubling](#5-egyptian-multiplication-by-doubling) | Rhind papyrus c. 1550 BCE, copied from an older text | Multiplying without a times table |
| 6 | [The counting board and the abacus](#6-the-counting-board-and-the-abacus) | Salamis tablet c. 300 BCE; Exchequer table by 1110 CE | Fast, error-resistant reckoning with movable counters |
| 7 | [Euclid's algorithm](#7-euclids-algorithm) | Elements Book VII, c. 300 BCE | Finding the greatest common measure without trying every candidate |
| 8 | [Archimedes squeezes π](#8-archimedes-squeezes-π) | c. 250 BCE | A quantity that can never be written exactly, but can be trapped |
| 9 | [The sieve of Eratosthenes](#9-the-sieve-of-eratosthenes) | c. 240 BCE, recorded c. 100 CE | Listing primes without testing each number by division |

---

## 1. Tally marks — one mark per thing

**When / where:** the Lebombo bone, Border Cave, South Africa, about 44,000 years ago. The Ishango bone, eastern DR Congo, about 20,000–25,000 years ago (sources differ).
**Atlas:** Ch. 7 (Early Number Systems), Ch. 89 (Numeral Systems) · **Code:** none yet

> **Field note.** Before numbers, there is matching: one notch for each animal, each day, each debt. You need no idea of "seventeen" to keep this record; you only need to be able to make one mark per thing. It is the first data structure: an append-only log.

**What hurt:** memory. A hunter, a herder or a moon-watcher needed to know *how many* without a word for the number.
**The step forward:** one-to-one correspondence. Each thing gets one mark, so comparing two collections means comparing two rows of marks.

**Evidence and certainty**

- The Ishango bone was found in 1950 and is held by the Royal Belgian Institute of Natural Sciences (RBINS). It is a fossilised bone handle with a quartz tip and 168 notches in three columns. **Documented** ([RBINS](https://ishango.naturalsciences.be/en/en-ishango-20.html))
- Its age is given as about 20,000 years (Live Science), 22,000 (MathWorld) or 25,000 (Smithsonian); NRICH gives the discovery year as 1960 instead of 1950. **Disputed**: quote a range.
- What the marks *mean* is open. Readings include arithmetic with primes and doubling (de Heinzelin), a lunar calendar (Marshack), and base 12 (Pletser and Huylebrouck). Keller (2010) argues the marks only show one-to-one matching, and RBINS itself says "the marks however do not imply the invention of counting". **Disputed**
- Border Cave notched bones: d'Errico et al. (PNAS 2012) conclude that people there "used notched bones for notational purposes", about 44,000 years ago. The popular "29-day lunar tally" story for the Lebombo bone is **Conjecture**.

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [A brief history of numerical systems](https://www.youtube.com/watch?v=cZH0YnFpjwU) | TED-Ed (Alessandra King) | Short animation from body-part counting and tally marks to Egyptian and Babylonian numerals |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Lecture 2: Arithmetic (handout)](https://people.math.harvard.edu/~knill/teaching/mathe320_2010/handouts/01-arithmetic.pdf) | Harvard Math E-320, Oliver Knill | Written lecture notes: tallying with sticks, bones, knots and pebbles, through to Egyptian and Babylonian numerals |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Ishango Bone](https://humanorigins.si.edu/evidence/behavior/recording-information/ishango-bone) | Smithsonian Human Origins | Short museum entry: age, discovery, three rows of tally marks |
| Start | [Ishango Bone](https://nrich.maths.org/problems/ishango-bone) | NRICH, University of Cambridge | Student activity listing the notch groups row by row; stresses that "nobody knows for sure" |
| Start | [When was math invented?](https://www.livescience.com/physics-mathematics/mathematics/when-was-math-invented) | Live Science (2025) | Lebombo to Ishango to Sumerian numerals, with expert caution about origins |
| Deeper | [Technical Marvels (2): Lebombo and Ishango Bones](https://cacm.acm.org/blogcacm/technical-marvels-part-2-lebombo-and-ishango-bones) | Communications of the ACM blog | A computing historian on both bones as early notation |
| Deeper | [The Ishango Bone, DR Congo](https://web.astronomicalheritage.net/show-entity?identity=85&idsubentity=1) | UNESCO Portal to the Heritage of Astronomy | Column totals 60, 48, 60, with the counting and lunar readings side by side |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The first Ishango bone](https://ishango.naturalsciences.be/en/en-ishango-20.html) and [Bones with notches](https://ishango.naturalsciences.be/en/en-ishango-19.html) | RBINS, the holding museum | The museum's own description and its caution about interpretation |
| Scholar | [The fables of Ishango, or the irresistible temptation of mathematical fiction](http://www.bibnum.education.fr/sites/default/files/ishango-analysis_v2.pdf) | Olivier Keller (2010; English 2015) | The main sceptical analysis |
| Scholar | [Does the Ishango Bone Indicate Knowledge of the Base 12?](https://arxiv.org/pdf/1204.1019) | Vladimir Pletser, arXiv | The base-12 reading. Read it alongside Keller |
| Scholar | [The oldest mathematical artefact](https://www.cambridge.org/core/journals/mathematical-gazette/article/abs/7136-the-oldest-mathematical-artefact/65E17776F7EC0D23568F9826F5BC8CDF) | Mathematical Gazette 71 (1987) | The note that named the Lebombo bone the oldest mathematical artefact (preview only) |
| Scholar | [Early evidence of San material culture … Border Cave](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1073/pnas.1204213109&format=json&resultType=core) | d'Errico et al., PNAS 2012 (Europe PMC record) | The redating, and "notched bones for notational purposes" |

**Gaps:** I found no explainer video or lecture from a museum, university or major channel about either bone. The YouTube videos that exist come from small channels, often with overclaiming titles, so they are left out.

---

## 2. Grouping, written numerals and the first carry

**When / where:** clay tokens in the Near East from about 7500 BCE. Proto-cuneiform number signs at Uruk, about 3200–3000 BCE. Egyptian hieroglyphic numerals from about 3000 BCE.
**Atlas:** Ch. 7.1 (computational limits of additive numerals), Ch. 89 · **Code:** [chapter 1 program](../../code/chapter-01-adding-two-numbers/), whose `settle` method is exactly "replace ten of one sign by one of the next"

> **Field note.** Fourteen strokes in a row cannot be read at a glance; ten strokes swapped for one new sign can. Once the signs exist, adding is pooling them, and whenever ten of one sign pile up you exchange them for one of the next. The exchange is the carry, and it is older than place value.

**What hurt:** long rows of marks are slow to write, easy to miscount, and impossible to compare at a glance.
**The step forward:** a new sign for each group (ten, a hundred …). Addition becomes *pool the signs, then exchange each full group for one sign of the next size*.

**Evidence and certainty**

- Schmandt-Besserat's theory: plain clay tokens (7500–3500 BCE), then tokens sealed in clay envelopes, then tablets with impressed signs, then abstract numerals. **Disputed**: Valerio and Ferrara (Historia Mathematica, 2022) argue that numerals and proto-cuneiform signs were "two distinct but converging developments".
- Late Uruk accounts (c. 3200–3000 BCE) used several commodity-specific number systems, including a sexagesimal one with steps 1, 10, 60, 600, 3,600. **Documented** ([Englund, MPIWG preprint](https://www.mpiwg-berlin.mpg.de/Preprints/P183.PDF))
- Egyptian addition, in MacTutor's words: "One just adds the individual symbols, but replacing ten copies of a symbol by a single symbol of the next higher value." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Egyptian_numerals/))
- What the sign for 10 depicts (a hobble for cattle, or a heel bone) is described differently in different sources. **Disputed**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Cuneiform Numbers](https://www.youtube.com/watch?v=RR3zzQP3bII) | Numberphile (Alex Bellos) | How numbers were written in cuneiform |
| Start | [Egyptian Number System](https://www.youtube.com/watch?v=z8f4MR6m7YY) | Khan Academy India | The hieroglyphic signs for powers of ten |
| Start | [Arithmetic Operations in Egyptian Number System](https://www.youtube.com/watch?v=YdOXWQuNsDE) | Khan Academy India | Adding with Egyptian numerals: the pool-and-exchange carry |
| Start | [The most important lumps of dry mud in history](https://www.youtube.com/watch?v=BLHhcYFeC5A) | Stefan Milo | Clay tokens as counters that became writing (does not mention the critiques) |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Early Mathematics: A Short Introduction](https://www.youtube.com/watch?v=ojvdPjMhnKI) | Gresham College, Robin Wilson (2011) | Egyptian signs and adding by "replacing each group of ten by the next symbol"; Mesopotamian sexagesimal |
| Deeper | [From Laundry Lists to Liturgies: The Origins of Writing in Ancient Mesopotamia](https://www.youtube.com/watch?v=Rgdb-sY0Y4A) | Getty Museum, Irving Finkel (British Museum) | 90-minute talk on how cuneiform began, accounting included |
| Deeper | [Denise Schmandt-Besserat — How Writing Came About](https://www.youtube.com/watch?v=M7bg0PsNXMQ) | Talk by the author of the token theory | The theory in her own words; pair it with Valerio and Ferrara |
| Deeper | [Number Systems Ancient to Modern 1: the Egyptians](https://www.youtube.com/watch?v=NgNNkUewUGQ) | Insights into Mathematics, N. J. Wildberger (UNSW) | Long lecture on the Egyptian system |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Egyptian numerals](https://mathshistory.st-andrews.ac.uk/HistTopics/Egyptian_numerals/) | MacTutor, St Andrews | The standard reference for hieroglyphic and hieratic numerals |
| Start | [Ancient Egyptian Math (teacher resource)](https://www.penn.museum/img/k12/teacherresources/pdfs/AncientEgyptianMath.pdf) | Penn Museum | Classroom sheet: what each sign depicts, with worked examples |
| Start | [From Counting to Writing](https://www.sciencenews.org/article/counting-writing) | Science News (2006) | Accessible account of "writing emerged from counting" |
| Deeper | [Tokens: their significance for the origin of counting and writing](https://sites.utexas.edu/dsb/tokens/tokens/) | Denise Schmandt-Besserat, UT Austin | The token sequence with dates |
| Deeper | [Sumerian metrological numeration](https://myslu.stlawu.edu/~dmel/mesomath/sumerian.html) | Duncan Melville, St. Lawrence University | Why early numbers were tied to commodities, and how one wedge came to mean 1, 60 or 3,600 |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Bulla with impressions and tokens (SB 1967)](https://collections.louvre.fr/en/ark:/53355/cl010176019) | Musée du Louvre | A real clay envelope from Susa holding 15 tokens |
| Scholar | [Proto-cuneiform tablet: account of barley distribution](https://www.metmuseum.org/art/collection/search/329081) | Metropolitan Museum of Art | Jemdet Nasr tablet, c. 3100–2900 BCE, with circular impressions used as numbers |
| Scholar | [Numeracy at the dawn of writing: Mesopotamia and beyond](https://www.sciencedirect.com/science/article/pii/S0315086020300665) | Valerio and Ferrara, Historia Mathematica 59 (2022) | The critique of the token theory |
| Scholar | [The state of decipherment of proto-Elamite](https://www.mpiwg-berlin.mpg.de/Preprints/P183.PDF) | Robert K. Englund, MPIWG Preprint 183 | Proto-cuneiform number systems and their link to tokens |

**Gaps:** the Narmer macehead (the classic example of very large hieroglyphic numbers) could not be verified on a museum page, so it is left out.

---

## 3. Babylonian place value and reciprocal tables

**When / where:** sexagesimal place value probably arose in the Ur III period, about 2100 BCE. Old Babylonian scribal schools, about 1800 BCE, taught multiplication and reciprocal tables. Plimpton 322 comes probably from Larsa, about 1820–1762 BCE.
**Atlas:** Ch. 1 (Babylonian Mathematics: 1.2 clay-tablet procedures, 1.3 lookup tables, 1.5 Plimpton 322) · **Code:** [chapter 1 program](../../code/chapter-01-adding-two-numbers/), which adds in any radix including 60

> **Field note.** Here the same wedge means one, sixty or three thousand six hundred, depending only on *where* it stands. Position does the work that new signs did before. With position comes a new trick: to divide, look up the reciprocal in a table and multiply. Division turns into a lookup, the first precomputed table I have found.

**What hurt:** in an additive system, multiplying and dividing means juggling piles of signs.
**The step forward:** place value in base 60, with two signs (1 and 10). Memorised tables of products and reciprocals then let scribes divide by multiplying.

**Evidence and certainty**

- Two signs make the 59 digits. There was no zero to fill an empty place and no point to mark where the whole part ends, so context decided whether a numeral meant 1 or 60. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/HistTopics/Babylonian_numerals/))
- "For Old Babylonians, division by n amounted to multiplication by 1/n." Tables list reciprocals of *regular* numbers (only prime factors 2, 3, 5). **Documented** ([AMS Feature Column](https://www.ams.org/publicoutreach/feature-column/fc-2012-05))
- Plimpton 322 has been read as a table of Pythagorean triples (Neugebauer and Sachs, 1945), as a teacher's aid built from reciprocal pairs (Robson, 2002), and as an exact trigonometric table (Mansfield and Wildberger, 2017). **Disputed**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Base 60 (sexagesimal)](https://www.youtube.com/watch?v=R9m2jck1f90) | Numberphile (Thomas Woolley) | The base-60 system shown on Yale Babylonian Collection tablets |
| Start | [The Mesopotamian Number System](https://www.youtube.com/watch?v=jsux7RzcIjw) | Khan Academy India | School-level introduction to base 60 and place value |
| Deeper | [Ancient Babylonian tablet — world's first trig table](https://www.youtube.com/watch?v=i9-ZPGp1AJE) | UNSW | One side of the Plimpton 322 debate (the 2017 claim). Watch it with the Scientific American critique |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Lecture 1, History of Math, Princeton University](https://www.youtube.com/watch?v=ZSk63kC9o6U) | Prof. Alex Kontorovich (2024) | University course lecture: early number, sexagesimal, YBC 7289, Plimpton 322 |
| Deeper | [Number Systems Ancient to Modern 2: the Babylonians](https://www.youtube.com/watch?v=58Z91hD5RXE) | N. J. Wildberger | Babylonian place value |
| Scholar | [Old Babylonian mathematics and Plimpton 322: the remarkable OB sexagesimal system](https://www.youtube.com/watch?v=J5Ug3Cr8RUE) | N. J. Wildberger | Long-form lecture by a co-author of the 2017 claim, so his framing is one-sided |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Babylonian numerals](https://mathshistory.st-andrews.ac.uk/HistTopics/Babylonian_numerals/) | MacTutor | The two-sign base-60 system, the missing zero, theories for "why 60" |
| Deeper | [Old Babylonian Multiplication and Reciprocal Tables](https://www.ams.org/publicoutreach/feature-column/fc-2012-05) | AMS Feature Column (Tony Phillips) | Walks through real tables; explains regular numbers and division by reciprocals |
| Deeper | [Mock Reciprocal Table](https://myslu.stlawu.edu/~dmel/mesomath/reciprocal.html) | Duncan Melville | The standard table's line format; about 50 known copies |
| Deeper | [Babylonian Pythagoras](https://mathshistory.st-andrews.ac.uk/HistTopics/Babylonian_Pythagoras/) | MacTutor | Plimpton 322's columns, its errors and the debate |
| Deeper | [Babylon Revisited](https://magazine.columbia.edu/article/babylon-revisited) | Columbia Magazine | How the tablet reached Columbia, and the 1945 and 2017 readings |
| Deeper | [Don't Fall for Babylonian Trigonometry Hype](https://www.scientificamerican.com/blog/roots-of-unity/dont-fall-for-babylonian-trigonometry-hype/) | Scientific American | Critique of the 2017 claim |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Plimpton 322 (P254790)](https://cdli.earth/artifacts/254790) | Cuneiform Digital Library Initiative | Catalogue record with photographs and line art |
| Scholar | ["Our Tools of Learning": Plimpton 322](https://exhibitions.library.columbia.edu/exhibits/show/plimpton/mathematics/page-2) | Columbia University Libraries | The owning library's presentation |
| Scholar | [Multiplication table (Penn Museum B6063)](https://isaw.nyu.edu/exhibitions/before-pythagoras/items/b-6063/) | ISAW, NYU, *Before Pythagoras* | A real Old Babylonian school multiplication tablet from Nippur |
| Scholar | [Words and Pictures: New Light on Plimpton 322](https://maa.org/programs/maa-awards/writing-awards/words-and-pictures-new-light-on-plimpton-322) | Eleanor Robson, Amer. Math. Monthly 109 (2002) | The reciprocal-pair reading; trigonometry is "conceptually anachronistic" |
| Scholar | [Plimpton 322 is Babylonian exact sexagesimal trigonometry](https://www.sciencedirect.com/science/article/pii/S0315086017300691) | Mansfield and Wildberger, Historia Mathematica 44 (2017) | The trigonometric reading |

**Gaps:** no major-channel video is devoted to reciprocal tables.

---

## 4. The square root of 2 on YBC 7289

**When / where:** an Old Babylonian school tablet, about 1800–1600 BCE (sources range from 1900 to 1600), Yale Babylonian Collection.
**Atlas:** Ch. 1.4 (Babylonian square root, the Heron-method ancestor), Ch. 102 (Newton–Raphson) · **Code:** [Newton's method, entry 41](../../code/principles/part-2-paradigms-and-classics/41-newtons-method/)

> **Field note.** A student drew a square and its diagonals, wrote 30 on a side and two numbers along the diagonal. The first is √2 in base 60, 1;24,51,10, which is 1.41421296…, correct to about six decimal places. No one measures that finely; it had to be computed. *How* it was computed is still argued over, 3,800 years later.

**What hurt:** some lengths, like the diagonal of a square, can never be written exactly as a fraction. Yet builders and surveyors still need them.
**The step forward:** a value accurate enough for any practical purpose, and later a procedure that improves any guess: average the guess *g* and *N/g*. That procedure is the ancestor of Newton's method.

**Evidence and certainty**

- The tablet shows a square with diagonals, side 30, and along the diagonal 1;24,51,10 and 42;25,35 (= 30√2). **Documented** ([CDLI](https://cdli.earth/artifacts/255048))
- Heron of Alexandria (1st century CE) states the averaging procedure in his *Metrica*: for √720, start from 27 and average 27 with 720/27. **Documented** ([MacTutor: Heron](https://mathshistory.st-andrews.ac.uk/Biographies/Heron/))
- Whether Old Babylonian scribes used that iteration is **disputed**. Fowler and Robson (1998) argue the scribe copied a value from a coefficient list and reconstruct a geometric "cut and paste" step equivalent to one averaging step. Buckle (2023) proposes another route. Repeated averaging reproduces the tablet's value at the fourth step, which shows the method is possible, not that it was used.

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [A Cuneiform Tablet in the Digital Age](https://www.youtube.com/watch?v=Ecm15-TKOBg) | Yale University | Yale's own film about YBC 7289 and its 3D-printed copies |
| Start | [Cuneiform Numbers](https://www.youtube.com/watch?v=RR3zzQP3bII) | Numberphile | What you need to read 1;24,51,10 |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Early Mathematics: A Short Introduction](https://www.youtube.com/watch?v=ojvdPjMhnKI) | Gresham College, Robin Wilson | Includes the Mesopotamian √2 approximation |
| Deeper | [Lecture 12: Square Roots, Newton's Method](https://www.youtube.com/watch?v=2YeJ-5UAke8) | MIT 6.006 (Srini Devadas), MIT OpenCourseWare | The same iteration used today for high-precision roots, with error and cost analysis |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Best Known Old Babylonian Tablet?](https://old.maa.org/press/periodicals/convergence/the-best-known-old-babylonian-tablet) | MAA Convergence | A novice scribe's practice exercise; √2 correct to three sexagesimal places |
| Start | [Babylon and the Square Root of 2](https://johncarlosbaez.wordpress.com/2011/12/02/babylon-and-the-square-root-of-2/) | John Baez, *Azimuth* | Shows averaging reaches the tablet's value at step four. Read it with Fowler and Robson for the sceptical view |
| Deeper | [YBC 7289 — Analysis](https://personal.math.ubc.ca/~cass/Euclid/ybc/analysis.html) | Bill Casselman, UBC | Works through the numbers on the tablet |
| Deeper | [Babylonian Pythagoras](https://mathshistory.st-andrews.ac.uk/HistTopics/Babylonian_Pythagoras/) | MacTutor | Two candidate methods, and the admission that there is no evidence of the method being used elsewhere |
| Deeper | [Square Roots via Newton's Method](https://math.mit.edu/~stevenj/18.335/newton-sqrt.pdf) | MIT 18.335 note (S. G. Johnson) | Quadratic convergence: correct digits roughly double each step. It dates the Babylonians to "circa 1000 BCE", which is too late for this tablet |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [YBC 07289 (P255048)](https://cdli.earth/artifacts/255048) | CDLI | Catalogue record and transliteration |
| Scholar | [YBC 7289 exhibition label](https://isaw.nyu.edu/exhibitions/before-pythagoras/items/ybc-7289/) | ISAW, NYU | Museum label from *Before Pythagoras* |
| Scholar | [A 3,800-year journey from classroom to classroom](https://news.yale.edu/2016/04/11/3800-year-journey-classroom-classroom) | Yale News | Curators on the tablet and its digitisation |
| Scholar | [Square root approximations in Old Babylonian mathematics: YBC 7289 in context](https://www.sciencedirect.com/science/article/pii/S0315086098922091) | Fowler and Robson, Historia Mathematica 25 (1998) | The standard scholarly study |
| Scholar | [How the estimate of √2 on YBC 7289 may have been calculated](https://www.sciencedirect.com/science/article/pii/S0315086022000477) | Buckle, Historia Mathematica 62 (2023) | A recent alternative reconstruction |

**Gaps:** no major popular channel has a video devoted to YBC 7289. Sources disagree on how and when Yale acquired the tablet (1909 or "by 1944").

---

## 5. Egyptian multiplication by doubling

**When / where:** the Rhind Mathematical Papyrus, copied by the scribe Ahmose about 1550 BCE from a text he says was older; British Museum EA10057 and EA10058.
**Atlas:** Ch. 2 (Egyptian Algorithms), Ch. 94 (Exponentiation) · **Code:** [square-and-multiply, entry 11](../../code/principles/part-1-distances-and-number-theory/11-square-and-multiply-and-rsa/), the same idea with × in place of +

> **Field note.** These scribes had no times table. To multiply 41 by 59 they doubled 59 again and again (59, 118, 236, 472, 944, 1888) and added the rows whose multipliers make 41 = 32 + 8 + 1. They never named base 2, yet they wrote every number as a sum of powers of two. Swap the addition for multiplication and you have the fast exponentiation that today's encryption runs on.

**What hurt:** multiplying with additive numerals and no memorised table.
**The step forward:** only two skills are needed, doubling and adding. Any multiplier is a sum of powers of two, so about log₂ *n* doublings suffice.

**Evidence and certainty**

- The Rhind papyrus holds 84 problems, including multiplication and division tables. Ahmose dates his copy to year 33 of the Hyksos king Apophis. **Documented** ([British Museum EA10057](https://www.britishmuseum.org/collection/object/Y_EA10057))
- Absolute dates differ: c. 1650 BCE (MacTutor), c. 1550 BCE (BM catalogue), around 1500 BCE (BM blog, 2025). **Disputed**
- MacTutor calls doubling "a very early use of binary arithmetic". This is a modern reading: the Egyptians had no concept of base 2. **Documented** as an interpretation.
- That "Russian peasant multiplication" descends from the Egyptian method is **Conjecture**.

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Russian Multiplication](https://www.youtube.com/watch?v=HJ_PP5rqLg0) | Numberphile (Johnny Ball) | Halving and doubling, and why it is binary |
| Start | [How Ancient Egyptians Multiplied Numbers Quickly](https://www.youtube.com/watch?v=qHXsKyVSPOU) | MindYourDecisions (Presh Talwalkar) | The Egyptian method, its "Russian peasant" form, and why it works |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Early Mathematics: A Short Introduction](https://www.youtube.com/watch?v=ojvdPjMhnKI) | Gresham College, Robin Wilson | The Rhind papyrus, doubling and halving, unit fractions |
| Deeper | [Four Algorithmic Journeys Part 1: Spoils of the Egyptians](https://www.youtube.com/playlist?list=PLHxtyCq_WDLV5N5zUCBCDC2WqF1VBDGg1) | Alexander Stepanov (A9), lecture playlist | From Ahmes's 41 × 59 to the generic power algorithm. [Lecture notes (PDF)](https://www.stepanovpapers.com/Journeys/Journey1.pdf) |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Mathematics in Egyptian Papyri](https://mathshistory.st-andrews.ac.uk/HistTopics/Egyptian_papyri/) | MacTutor | 41 × 59 worked by doubling, plus the Rhind and Moscow problems |
| Start | [Egyptian Multiplication, binary system](https://www.cut-the-knot.org/Curriculum/Algebra/EgyptianMultiplication.shtml) | Cut the Knot | Interactive: how the doubling table picks out the binary digits |
| Start | [Mathematical Treasure: the Rhind and Moscow papyri](https://old.maa.org/press/periodicals/convergence/mathematical-treasure-the-rhind-and-moscow-mathematical-papyri) | MAA Convergence | Illustrated overview of both papyri |
| Deeper | [From Mathematics to Generic Programming: The First Algorithm](https://www.informit.com/articles/article.aspx?p=2264460) | Stepanov and Rose (book excerpt) | Ahmes's algorithm and why it relies on associativity |
| Deeper | [Fast multiplication / exponentiation](https://www.cs.uaf.edu/2013/spring/cs463/lecture/02_13_multiplication.html) | University of Alaska Fairbanks, CS 463 notes | "Replacing + with * gives the fast exponentiation by squaring trick", and why RSA needs it |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Rhind Mathematical Papyrus, EA10057](https://www.britishmuseum.org/collection/object/Y_EA10057) and [EA10058](https://www.britishmuseum.org/collection/object/Y_EA10058) | British Museum | Catalogue records of both sections |
| Scholar | [Learn maths like an Egyptian](https://www.britishmuseum.org/blog/learn-maths-egyptian-secrets-rhind-mathematical-papyrus) | British Museum blog (curator, 2025) | The papyrus as Ahmose's copy of an older original |
| Scholar | [Egyptian multiplication and some of its ramifications](https://arxiv.org/html/1901.10961) | M. H. van Emden, arXiv | From the binary expansion to exponentiation, division and logarithms |
| Scholar | [On the history of the square-and-multiply algorithm](https://arxiv.org/html/2606.00958) | Aydin et al., arXiv (2026 preprint) | From Pingala (c. 200 BCE) to al-Kashi (1427). It does not cover Egypt |

**Gaps:** no museum video covers the multiplication method itself; no online museum record was found for the Moscow papyrus.

---

## 6. The counting board and the abacus

**When / where:** the Salamis tablet, a marble counting board, about 300 BCE (Epigraphical Museum, Athens). Roman bronze hand abaci. The English Exchequer table, first mentioned in 1110 and described about 1179. The Chinese suanpan (clearly illustrated by 1573) and the Japanese soroban.
**Atlas:** Ch. 7.2 (The Abacus — an early physical algorithm machine) · **Code:** [chapter 1 program](../../code/chapter-01-adding-two-numbers/): `columnSums` is "push the counters on", `settle` is "exchange full columns"

> **Field note.** On these boards nobody writes a digit. Counters go in columns; adding is pushing more counters on, then settling: any column holding a full group is cleared and one counter goes to the next column. The procedure lives in the hands. Their word *calculus* is Latin for a small pebble, and the English *Exchequer* is named after the chequered cloth its officials counted on.

**What hurt:** written numerals (Greek, Roman) were poor for calculating. Merchants and treasuries needed speed and fewer mistakes.
**The step forward:** a physical place-value machine. Columns hold the place value, so the user only has to push and exchange.

**Evidence and certainty**

- The Salamis tablet (EM 11515) dates to about 300 BCE (the Computer History Museum says 4th century BCE). Sources disagree on the year it was found, so none is given here. **Documented** ([Computer History Museum](https://www.computerhistory.org/revolution/calculators/1/1/128))
- What it was used for is **disputed**. The holding museum says it is "believed to be a table of mathematical calculations or a toy", and it was once thought to be a gaming board.
- Three bronze Roman hand abaci survive (Aosta, Paris, Rome). **Documented** ([CACM blog](https://cacm.acm.org/blogcacm/in-search-of-a-rare-roman-pocket-calculator/))
- *Calculus*: Latin "a pebble used as a reckoning counter". **Documented** ([Etymonline](https://www.etymonline.com/word/calculus))
- The *Dialogue concerning the Exchequer* (c. 1179) describes the table, its striped black cloth and counters, and the chessboard origin of the name. **Documented**
- Early dates for the suanpan and the soroban vary widely between sources. **Disputed**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Introduction to the Roman abacus and counting board](https://www.youtube.com/watch?v=c-2I09cmth0) | Reading Ancient Schoolroom (University of Reading) | Reconstructed Roman reckoning. Follow-up: [Multiplication on the Roman abacus](https://www.youtube.com/watch?v=j-3vLKm6mUM) |
| Start | [The Salamis Tablet — Calculating on a Counting board](https://www.youtube.com/watch?v=mYR4qa3pswU) | Jens Puhle | A Salamis-style board demonstrated, cited by Wikipedia (independent creator) |
| Start | [Seeing Numbers with Soroban — The Japanese Abacus](https://www.youtube.com/watch?v=Q7OYQqPLH0o) | The Japan Society | How the soroban is used (ages 7–11 and up) |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Exploring Ancient Greek and Roman Numeracy](https://www.youtube.com/watch?v=-45Hxj6Txoo) | Gresham College, Serafina Cuomo (2011) | The Salamis abacus, the Aosta abacus, finger counting, and what remains unknown |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Revolution: Calculators — Abacus](https://www.computerhistory.org/revolution/calculators/1/1) | Computer History Museum | Abaci from China to Greece to the Inca, with the Salamis tablet |
| Start | [I'm counting on it](https://chalkdustmagazine.com/features/im-counting-on-it/) | Chalkdust magazine (2023) | Counting boards and abaci around the world, and words like *calculus* and *counter* |
| Start | [The Exchequer: a chequered history](https://history.blog.gov.uk/2013/08/14/the-exchequer-a-chequered-history/) | GOV.UK History of Government blog | How the chequered cloth was used at the audit |
| Deeper | [In Search of A Rare Roman Pocket Calculator](https://cacm.acm.org/blogcacm/in-search-of-a-rare-roman-pocket-calculator/) | Communications of the ACM blog | Tracking down the surviving Roman hand abaci |
| Deeper | [The Abacus, the Numeral Frame, and Counters](https://www.si.edu/spotlight/the-abacus-the-numeral-frame-and-counters) | Smithsonian | European counting boards, suanpan and soroban (it wrongly calls *calculi* Greek; the word is Latin) |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Permanent exhibition: the Salamis tablet](https://epigraphicmuseum.gr/en/permanent-exhibition/) | Epigraphical Museum, Athens | The holding museum's description |
| Scholar | [Salamis Counting Table (replica)](https://www.si.edu/object/nmah_690540) | Smithsonian NMAH | Replica record; calculation by moving pebbles along lines |
| Scholar | [The Dialogue concerning the Exchequer](https://avalon.law.yale.edu/medieval/excheq.asp) | Avalon Project, Yale Law School (Henderson's translation) | Primary text, c. 1179 |
| Scholar | [Early accounting: the tally and checkerboard](https://egrove.olemiss.edu/aah_journal/vol16/iss2/2/) | W. T. Baxter, Accounting Historians Journal (1989) | Medieval counter-reckoning and tally sticks |
| Scholar | [Zhusuan: Chinese abacus calculation](https://ich.unesco.org/en/RL/chinese-zhusuan-knowledge-and-practices-of-mathematical-calculation-through-the-abacus-00853) | UNESCO Intangible Cultural Heritage (2013) | The inscription for bead-and-rod calculation |

**Gaps:** Mabel Lang's "Herodotos and the Abacus" (Hesperia, 1957) and Herodotus 2.36 could not be opened. No video was found on the Exchequer table.

---

## 7. Euclid's algorithm

**When / where:** Euclid's *Elements*, Book VII, Propositions 1–2, Alexandria, about 300 BCE. The method probably predates Euclid.
**Visual page:** [Euclid's algorithm, with diagrams, charts and an interactive edition](07-euclids-algorithm/README.md) · **Atlas:** Ch. 4 (The Euclidean Algorithm — the oldest living algorithm), Ch. 92 (Number theory) · **Code:** [Euclidean algorithm, entry 1](../../code/principles/part-1-distances-and-number-theory/01-euclidean-algorithm/) and [extended Euclid, entry 2](../../code/principles/part-1-distances-and-number-theory/02-extended-euclidean-algorithm/)

> **Field note.** Earlier procedures computed a *value*. This one proves something about *any* two numbers and stops on its own. Take the smaller from the larger, again and again; when the two are equal, that is the greatest common measure. Later readers noticed that one division does many subtractions at once. It still runs, unchanged in spirit, inside every encryption library they use.

**What hurt:** to find the largest measure that divides two lengths or numbers, you would otherwise try every candidate.
**The step forward:** reduce the pair. gcd(*a*, *b*) = gcd(*b*, *a* mod *b*), so the numbers shrink until the remainder is zero.

**Evidence and certainty**

- Book VII, Prop. 1 uses repeated subtraction ("the less is continually subtracted in turn from the greater") to test whether two numbers are coprime. Prop. 2 finds "the greatest common measure of two given numbers not relatively prime". **Documented** ([Joyce's edition](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII1.html))
- Earlier origins (Eudoxus, Theaetetus, the Pythagoreans) have been proposed but not proven. **Conjecture**
- Lamé (1844) showed the number of division steps is at most five times the number of decimal digits of the smaller number, with consecutive Fibonacci numbers as the worst case. Shallit (1994) shows Reynaud (1811), Léger (1837) and Finck (1841) got there first, in part or in full. **Documented**, with priority **disputed**.
- Knuth: "the granddaddy of all algorithms, because it is the oldest nontrivial algorithm that has survived to the present day" (*TAOCP* Vol. 2). The page number differs by edition and was not checked against the book itself.

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Euclid's Algorithm](https://www.youtube.com/watch?v=6Y3jHHE_hbA) | Numberphile (Sophie Maclean) | The algorithm and its Fibonacci connection |
| Start | [The Euclidean Algorithm (Finding the GCD/GCF)](https://www.youtube.com/watch?v=SR-jmdjzw-Y) | Houston Math Prep | Step-by-step worked examples |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Here's looking at Euclid](https://www.youtube.com/watch?v=9O97Xad-iTQ) | Gresham College, Robin Wilson (2004) | Greek mathematics and the *Elements*, with the Euclidean algorithm in context |
| Deeper | [Lec 4, MIT 6.042J Mathematics for Computer Science](https://www.youtube.com/watch?v=NuY7szYSXSw) | MIT OpenCourseWare (2010) | GCD, Euclid's algorithm, the Pulverizer (extended Euclid) |
| Deeper | [2.1.2 Euclidean Algorithm](https://www.youtube.com/watch?v=dW0f62lcCLE) | MIT OpenCourseWare (6.042J, 2015) | Short course segment |
| Scholar | [Introduction to number theory lecture 3: divisibility and Euclid's algorithm](https://www.youtube.com/watch?v=pVKhDtOjji8) | Richard Borcherds (UC Berkeley) | Rigorous treatment; continues in [lecture 4](https://www.youtube.com/watch?v=R-O8j7FHEXI) |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Euclid's Algorithm](https://www.cut-the-knot.org/blue/Euclid.shtml) | Cut the Knot | gcd(*a*, *b*) = gcd(*b*, *r*) with a worked example, and Bézout's identity |
| Deeper | [Euclidean Algorithm](https://mathworld.wolfram.com/EuclideanAlgorithm.html) | Wolfram MathWorld | Lamé's bound, Fibonacci worst case, average-case step count |
| Deeper | [Euclid of Alexandria](https://mathshistory.st-andrews.ac.uk/Biographies/Euclid/) | MacTutor | What is (and is not) known about Euclid |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Elements VII.1](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII1.html) and [VII.2](https://mathcs.clarku.edu/~djoyce/elements/bookVII/propVII2.html) | David E. Joyce, Clark University | The propositions with commentary and worked examples |
| Scholar | [Origins of the analysis of the Euclidean algorithm](https://www.sciencedirect.com/science/article/pii/S0315086084710317) | Jeffrey Shallit, Historia Mathematica 21 (1994) | Who first bounded the running time |

---

## 8. Archimedes squeezes π

**When / where:** *Measurement of a Circle*, Syracuse, probably about 250 BCE.
**Atlas:** Ch. 6.4–6.5 (Archimedes and numerical approximation; the method of exhaustion) · **Code:** planned

> **Field note.** π cannot be written down exactly. Archimedes traps it instead. A polygon inside the circle is too short, a polygon outside is too long, and every doubling of the sides narrows the gap. After 6, 12, 24, 48 and 96 sides: 223/71 < π < 22/7. He does not give *an* answer; he gives an answer with a guaranteed error bound.

**What hurt:** a needed quantity that no exact number can express.
**The step forward:** bracketing. Two bounds that close in step by step, each step a fixed recurrence from the last.

**Evidence and certainty**

- Proposition 3: "The ratio of the circumference of any circle to its diameter is less than 3 1/7 but greater than 3 10/71." **Documented** ([Heath's translation](https://archive.org/details/worksofarchimede00arch))
- The surviving treatise is probably a fragment of a longer work, and its proposition order is not original. **Disputed**
- Archimedes does not say how he got his square-root bounds (e.g. 265/153 < √3 < 1351/780). Reconstructions differ. **Disputed** ([Davies, arXiv](https://arxiv.org/abs/1101.0492))
- "The first algorithm with a guaranteed error bound" is this catalog's own framing; MacTutor says "the first theoretical calculation". **Conjecture**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Discovery That Transformed Pi](https://www.youtube.com/watch?v=gMlf1ELvRzc) | Veritasium | Opens with Archimedes doubling polygons to 96 sides, then moves to Newton's series |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Story of Pi](https://www.youtube.com/watch?v=f4Sk6gEG570) | Gresham College, Robin Wilson (2007) | Archimedes repeatedly doubling a hexagon's sides, in the long history of π |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Approximating Pi](https://www.pbs.org/wgbh/nova/archimedes/pi.html) | PBS NOVA | Illustrated: hexagon to 96-gon |
| Start | [A history of Pi](https://mathshistory.st-andrews.ac.uk/HistTopics/Pi_through_the_ages/) | MacTutor | Archimedes' recursion in the long history of π |
| Deeper | [How Archimedes showed that π is approximately equal to 22/7](https://arxiv.org/pdf/2008.07995) | Damini and Dhar, arXiv | Step-by-step modern reconstruction of the doubling recurrences |
| Deeper | [Ancient estimate of π and modern numerical analysis](https://www.johndcook.com/blog/2023/07/30/archimedes-richardson/) | John D. Cook | From the 96-gon to Huygens and Richardson extrapolation |
| Deeper | [Archimedes on the Circumference and Area of a Circle](https://www.ams.org/publicoutreach/feature-column/fc-2012-02) | AMS Feature Column (Bill Casselman) | The method of exhaustion in Proposition 1 (not the 96-gon) |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Works of Archimedes](https://archive.org/details/worksofarchimede00arch) | T. L. Heath (1897), Internet Archive | The standard English translation, including *Measurement of a Circle* |
| Scholar | [Archimedes' Measurement of a Circle](https://triumphsannals.journals.publicknowledgeproject.org/index.php/triumphsannals/article/download/13291/11763/71303) | TRIUMPHS primary-source project | Students work through the iterations from Heath's text |

**Gaps:** no Archimedes-π video from Numberphile, Mathologer, 3Blue1Brown or TED-Ed was found.

---

## 9. The sieve of Eratosthenes

**When / where:** Eratosthenes of Cyrene (276–194 BCE), librarian at Alexandria from about 240 BCE. The method survives in Nicomachus of Gerasa's *Introduction to Arithmetic* (about 100 CE), Book I, Chapter 13.
**Atlas:** Ch. 3 (The Sieve of Eratosthenes — mapping the primes) · **Code:** [sieve, entry 12](../../code/principles/part-1-distances-and-number-theory/12-sieve-of-eratosthenes/)

> **Field note.** Testing each number for divisors repeats the same work again and again. The sieve turns the problem inside out: never ask "is *n* prime?" Instead, for each prime, cross out its multiples, and whatever survives is prime. It is the oldest algorithm I have found that trades memory (a whole table of numbers) for speed.

**What hurt:** trial division repeats work; each number is tested from scratch.
**The step forward:** cross out multiples instead of testing divisors. The cost is about *n* log log *n* steps, and sieving only needs primes up to √*n*.

**Evidence and certainty**

- Eratosthenes' life, Alexandria, and the librarianship. **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Eratosthenes/))
- The earliest account is Nicomachus, about three centuries later, and his version sieves by odd numbers rather than only by primes. "c. 240 BCE" is a floruit, not a date for the sieve. **Documented**
- The linear sieve is credited to Gries and Misra (1978) by Wikipedia and to Pritchard (1987) by CP-Algorithms. **Disputed**
- O'Neill (2009) showed that the famous one-line functional "sieve" is really trial division, and far slower than the real thing. **Documented**

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Sieve of Eratosthenes](https://www.youtube.com/watch?v=klcIklsWzrY) | Khan Academy (Journey into cryptography) | Animated introduction, framed by cryptography |
| Deeper | [Infinite Data Structures: To Infinity & Beyond!](https://www.youtube.com/watch?v=bnRNiE_OVWA) | Computerphile (Graham Hutton) | An infinite list of primes in Haskell: the classic "sieve" that O'Neill's paper critiques |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Prime-time mathematics](https://www.youtube.com/watch?v=heY6nsELLVk) | Gresham College, Robin Wilson (2005) | Walks through sifting the numbers up to 100 |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Sieve of Eratosthenes](https://mathworld.wolfram.com/SieveofEratosthenes.html) | Wolfram MathWorld | The procedure, and how Nicomachus preserved it |
| Deeper | [Sieve of Eratosthenes](https://cp-algorithms.com/algebra/sieve-of-eratosthenes.html) | CP-Algorithms | Proof of *n* log log *n*, the segmented sieve, block-size advice |
| Deeper | [Eratosthenes of Cyrene](https://mathshistory.st-andrews.ac.uk/Biographies/Eratosthenes/) | MacTutor | Life and work. Note: it credits the account to "Nicomedes", a slip for Nicomachus |
| Scholar | [Turner, Bird, Eratosthenes: an eternal burning thread](https://www.cambridge.org/core/journals/journal-of-functional-programming/article/turner-bird-eratosthenes-an-eternal-burning-thread/32E2EDF5D5EAEC95F13D313BC97B86F0) | Jeremy Gibbons, J. Functional Programming 35 (2025) | A follow-up to O'Neill on lazy sieves |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Introduction to Arithmetic](https://archive.org/details/nicomachus-introduction-to-arithmetic) | Nicomachus, trans. D'Ooge (1926), Internet Archive | The earliest surviving account (Book I, Ch. 13). Also on [Zenodo](https://zenodo.org/records/6060110) |
| Scholar | [The Genuine Sieve of Eratosthenes](https://www.cs.hmc.edu/~oneill/papers/Sieve-JFP.pdf) | Melissa O'Neill, J. Functional Programming 19 (2009) | Author's PDF; cite JFP 19(1):95–106 |

**Gaps:** no sieve video from Numberphile or 3Blue1Brown was found. The Nicomachus chapter reference comes from MathWorld; the scan's own text was not readable online.

---

## What the era leaves behind

| ⊕ Combination | Result |
|---|---|
| One mark per thing ⊕ a sign per group | Written numerals, and the carry as an exchange |
| Grouping ⊕ position | Place value: the same sign means 1, 60 or 3,600 |
| Place value ⊕ precomputed tables | Division by looking up a reciprocal |
| Doubling ⊕ adding | Multiplication in about log₂ *n* steps, later fast exponentiation |
| Repeated subtraction ⊕ division | Euclid's algorithm in its fast form |
| Two bounds ⊕ a doubling recurrence | Archimedes' π with a guaranteed error |
| A table in memory ⊕ crossing out | The sieve: memory traded for speed |

**Next installment:** Era 2. Al-Khwarizmi and the word "algorithm", Indian zero and positional arithmetic, Fibonacci's *Liber Abaci*, and frequency analysis (al-Kindi).
