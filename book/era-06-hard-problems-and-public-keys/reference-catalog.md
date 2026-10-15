# Era 6 — Hard Problems and Public Keys: from the fast Fourier transform to logical clocks

*Reference catalog. Thirteen developments, from 1965 to 1978.*

> **Field note from the visiting historian.** In the fifth era the species learned to write programs well. In this one their programs begin to run side by side, share memory, and talk to each other across networks; their data outgrow memory and move to disks; and their machines begin to keep secrets in public. Some old problems turn out to have much faster methods than anyone expected: transforms, matrix products, searches through text and graphs. Others, a whole family of them, resist every attempt, and the species proves that they all stand or fall together without learning which. By the end of the era they have turned that hardness into a resource: the security of their messages rests on problems they believe nobody can solve quickly.

## How to use this catalog

Every link was opened before it was listed. Where a video page could not be opened, no video is listed and the gap is recorded instead. Links are tagged by level, so a high-school reader and a PhD scholar can both find their way in:

| Tag | Meaning |
|---|---|
| **Start** | No background needed. Watch or read this first. |
| **Deeper** | University level: the mechanism, the proof, the analysis. |
| **Scholar** | Primary sources and research papers: the evidence itself, and the arguments about it. |

Each claim also carries a certainty label:

- **Documented**: stated by the primary text, the holding archive, or standard scholarship.
- **Conjecture**: a reasonable reading that the evidence does not settle.
- **Disputed**: scholars, or the opened sources, disagree; the positions are given.

The **Atlas** lines will point to the matching chapters of *The Evolutionary Atlas of Algorithms and Data Structures* once mapped. The **Code** lines point to the tested Java programs.

A note on videos: no video page could be opened from the environment used to build this catalog, so no videos are listed; each topic's **Gaps** line says so. Where a publisher's page redirected elsewhere, the redirect was not followed and the paper is described through the sources that were opened.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [The fast Fourier transform](#1-the-fast-fourier-transform-for-machines) | 1963 meeting; demonstrated 1964; published 1965 | A transform of N samples took about N² operations |
| 2 | [Mutual exclusion and the semaphore](#2-mutual-exclusion-and-the-semaphore) | Dekker about 1962; semaphore 1962; EWD 123, 1965 | Processes sharing memory corrupt data or wait for ever |
| 3 | [Objects, classes and subclasses](#3-objects-classes-and-subclasses) | Simula begun 1961; Simula 67, 1967 | A model of many interacting things was a heap of arrays and scattered code |
| 4 | [A*](#4-a-search-guided-by-an-estimate) | Shakey project; received 1967; published 1968 | Dijkstra's method explores every direction; greedy search returns long paths |
| 5 | [Fast matrix multiplication](#5-fast-matrix-multiplication) | 1969 | Multiplying and inverting matrices took n³ operations |
| 6 | [The relational model of data](#6-the-relational-model-of-data) | 1970 | Programs depended on how the data was stored |
| 7 | [B-trees](#7-b-trees) | Idea 1969; report 1970; published 1972 | Indexes too big for memory, one disk access per step |
| 8 | [NP-completeness](#8-np-completeness) | Cook 1971; Karp 1972; Levin 1973 | Many problems resisted every fast method, and nobody knew why |
| 9 | [Depth-first search](#9-depth-first-search-and-linear-time-graph-algorithms) | Planarity work from 1970; paper 1972; planarity 1974 | Graph structure took repeated searches |
| 10 | [Public-key cryptography](#10-public-key-cryptography) | Diffie and Hellman 1976; RSA 1977; GCHQ in secret 1970–1974 | Every cipher needed a key shared in advance |
| 11 | [Fast string searching](#11-fast-string-searching) | Morris 1969; KMP and Boyer–Moore 1977 | Searching reread the text, m × n comparisons at worst |
| 12 | [Universal compression](#12-universal-compression-lempel-and-ziv) | 1977 and 1978 | Good codes needed the source's probabilities |
| 13 | [Logical clocks](#13-logical-clocks-and-the-order-of-events) | 1978 | No meaning for "before" between separate computers |

## 1. The fast Fourier transform, for machines

**When / where:** John W. Tukey (Princeton University and Bell Telephone Laboratories) and James W. Cooley (IBM Watson Research Center, Yorktown Heights), brought together by Richard Garwin of IBM after a 1963 meeting of President Kennedy's Science Advisory Committee; a program demonstrated at IBM Research in 1964; "An Algorithm for the Machine Calculation of Complex Fourier Series", received 17 August 1964, *Mathematics of Computation* 19: 297–301 (April 1965).
**Atlas:** to be mapped · **Code:** [`FastFourier.java`](../../code/era-06-hard-problems-and-public-keys/01-fast-fourier-transform/) · **Page:** [topic 1](01-fast-fourier-transform/README.md)

> **Field note.** Gauss had found the trick in 1805 and left it in Latin among his papers (Era 3, topic 9). A hundred and sixty years later it was found again, by people who needed it badly: a committee advising the American president wanted to detect underground nuclear tests from the shaking of the ground, and the arithmetic of turning a seismogram into its frequencies was too slow for the machines of the day. A statistician mentioned that he knew a shortcut; a physicist who heard him asked IBM for a programmer to make it work. The shortcut, halving and halving again, turns a million-point transform from a trillion multiplications into some tens of millions. It went on to wherever a signal had to be taken apart: the compression of sound and video, the scanners that see inside a body, and, by a turn the committee never imagined, the multiplication of very large numbers.

**What hurt:** a discrete Fourier transform of N samples takes about N² operations, too slow on the computers of the 1960s for long records such as seismograms.
**The step forward:** for N a power of two, split the samples into even and odd positions, transform each half, and combine them with N/2 "butterflies"; repeated, about N log₂ N operations, done in place after a reordering of the samples by bit reversal.

**Evidence and certainty**

- The paper's abstract: Good's methods, applied to Fourier series, give "a number of operations proportional to N log N rather than N²"; it acknowledges Yates and Box et al. and cites I. J. Good (1958); "The authors wish to thank Richard Garwin for his essential role in communication and encouragement." Received 17 August 1964; pages 297–301. **Documented** ([Cooley and Tukey 1965, on a UC Davis course page](https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf))
- At a 1963 meeting of President Kennedy's Science Advisory Committee on detecting underground nuclear tests, Garwin recognized that Tukey had "a scheme to do a complete discrete Fourier transform with a vastly reduced number of mathematical calculations" and asked IBM for a mathematical analyst; Cooley was recruited. The 1964 demonstration ran on an IBM 7094, reportedly programmed in FORTRAN; for large problems of the time it was about 100 times faster than existing codes. IEEE Milestone, dedicated in 2025 at Princeton (22 May) and IBM (11 June). **Documented** ([Engineering and Technology History Wiki, IEEE Milestone](https://ethw.org/Milestones:First_Demonstration_of_the_Fast_Fourier_Transform_(FFT),_1964))
- "If the Fourier transform could be made faster, Garwin said, seismometers could be planted in the ground" near the Soviet Union; sensors using the algorithm detected nuclear explosions within a 15-kilometre radius. **Documented** as reported by Kathy Pretz ([IEEE Spectrum, 21 August 2025](https://spectrum.ieee.org/fft-algorithm-ieee-milestone)); the 15-kilometre figure is not in the paper
- Cooley (18 September 1926 – 29 June 2016) joined the Research Staff at IBM Watson Research Center in 1962; the paper is *Math. Comput.* 19, 297–301. **Documented** ([Wikipedia, James Cooley](https://en.wikipedia.org/wiki/James_Cooley))
- Gauss had the method about 1805; Runge (1903), Danielson and Lanczos (1942) and Good (1958) had versions before 1965. **Documented** (Era 3, topic 9, citing Heideman, Johnson and Burrus 1985)

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The 60-Year Old Algorithm Underlying Today's Tech](https://spectrum.ieee.org/fft-algorithm-ieee-milestone) | Kathy Pretz, IEEE Spectrum (2025) | The nuclear-test story and the IEEE Milestone |
| Start | [First Demonstration of the Fast Fourier Transform, 1964](https://ethw.org/Milestones:First_Demonstration_of_the_Fast_Fourier_Transform_(FFT),_1964) | Engineering and Technology History Wiki | The milestone citation and its history |
| Deeper | [James Cooley](https://en.wikipedia.org/wiki/James_Cooley) | Wikipedia | The IBM mathematician who wrote the program |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [An Algorithm for the Machine Calculation of Complex Fourier Series](https://www.ece.ucdavis.edu/~bbaas/281/papers/CooleyTukey.1965.pdf) | J. W. Cooley and J. W. Tukey, *Mathematics of Computation* 19: 297–301 (1965), on a UC Davis course page | The five-page paper |

**Gaps:** no video page could be opened. The issue number of *Mathematics of Computation* is not given in the opened sources. The Spectrum article's 15-kilometre figure and the "100 times faster" figure are reported, not checked; the topic's program measures its own speed-up in operations, not time.

## 2. Mutual exclusion and the semaphore

**When / where:** Edsger W. Dijkstra, Mathematical Centre, Amsterdam, then the Technological University, Eindhoven: Th. J. Dekker's solution for two processes, reported in Dijkstra's manuscript EWD 35 (1962 or 1963); the semaphore, introduced in 1962 (EWD 51, "Multiprogrammering en X8"); "Cooperating sequential processes", manuscript EWD 123, finalized in September 1965 and published in 1968.
**Atlas:** to be mapped · **Code:** [`Semaphores.java`](../../code/era-06-hard-problems-and-public-keys/02-semaphores/) · **Page:** [topic 2](02-semaphores/README.md)

> **Field note.** The machines of the 1960s were fast enough to be shared: while one program waited for a tape, another could compute, and a third could print. Programs that run side by side and use the same memory meet a new kind of error, one that appears only when their steps happen to interleave badly, and disappears when anyone looks. Dijkstra set out the problem plainly: two processes, each with a section that the other must not enter at the same time. Several obvious answers are wrong, in ways that take some finding; a colleague, Dekker, found one that is right. Dijkstra then gave the species a simpler tool, a counter that a process can lower only when it is above zero, and with it a vocabulary (the critical section, the semaphore, and the "deadly embrace" now called deadlock) that operating systems still use.

**What hurt:** processes that share memory and run in interleaved steps can corrupt shared data (a lost update) or wait for each other for ever; correct solutions with ordinary variables were hard to find and harder to check.
**The step forward:** the critical section as a problem stated precisely; Dekker's algorithm for two processes; and the semaphore, a non-negative integer with indivisible operations P (wait until positive, then decrease) and V (increase), which makes mutual exclusion and producer–consumer cooperation short and checkable.

**Evidence and certainty**

- EWD 123, "Cooperating sequential processes" (Department of Mathematics, Technological University, Eindhoven): in each cycle "a so-called 'critical section' occurs", and "at any moment at most one of the two is engaged in its critical section"; "To the Dutch mathematician Th.J.Dekker the credit is due for the first correct solution"; semaphores are "essentially non-negative integers"; the V-operation is "to increase the value of its argument semaphore by 1", the P-operation "to decrease the value of its argument semaphore by 1 as soon as the resulting value would be non-negative"; section 6 is "The Problem of the Deadly Embrace". **Documented** ([EWD 123, transcription at the E. W. Dijkstra Archive, University of Texas](https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html))
- Dekker's algorithm is "the first known correct solution to the mutual exclusion problem"; Dijkstra reported it in EWD 35 ("undated, 1962 or 1963") and in EWD 123, dated September 1965; the algorithm "won't work on SMP machines equipped with these CPUs without the use of memory barriers". **Documented** ([Wikipedia, Dekker's algorithm](https://en.wikipedia.org/wiki/Dekker%27s_algorithm))
- Dijkstra "introduced the concept of a semaphore already in 1962" (EWD 51); "Cooperating Sequential Processes" was "finalized in 1965 and was available as his manuscript EWD 123", published in 1968, and "originated the field of concurrent programming"; he identified "the problem of the deadly embrace" and proposed the "Banker's algorithm" (EWD 108); the dining philosophers came in 1971. **Documented** ([K. R. Apt, "Edsger Wybe Dijkstra (1930–2002): A Portrait of a Genius", arXiv](https://arxiv.org/pdf/cs/0210001))
- What P and V stand for: Apt gives "Prolaag", "a non-existing Dutch word that stands for 'lower'"; a note at New York University, quoting Gert Vegter of Groningen, gives "Probeer ('Try')" and "Verhoog ('Increment')"; EWD 123 does not expand them. **Disputed** ([Apt](https://arxiv.org/pdf/cs/0210001); [NYU, "Origin of P and V"](https://cs.nyu.edu/~yap/classes/os/resources/origin_of_PV.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Dekker's algorithm](https://en.wikipedia.org/wiki/Dekker%27s_algorithm) | Wikipedia | Flags and a turn: the first correct solution, and why modern processors need more |
| Deeper | [Edsger Wybe Dijkstra (1930–2002): A Portrait of a Genius](https://arxiv.org/pdf/cs/0210001) | Krzysztof R. Apt (2002), arXiv | Semaphores, THE, the deadly embrace and the dining philosophers, in context |
| Deeper | [Origin of P and V](https://cs.nyu.edu/~yap/classes/os/resources/origin_of_PV.html) | New York University course page | One account of the Dutch words behind P and V |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Cooperating sequential processes (EWD 123)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD01xx/EWD123.html) | E. W. Dijkstra (1965), transcription at the E. W. Dijkstra Archive | The essay that stated the problem and introduced P and V to a wide audience |

**Gaps:** no video page could be opened. EWD 35 and EWD 51 were not opened; their dates are as given by Wikipedia and Apt. The body of EWD 123's section on the deadly embrace was not read. The topic's program checks every interleaving of small models, not real threads on real processors.

## 3. Objects, classes and subclasses

**When / where:** Ole-Johan Dahl and Kristen Nygaard, Norwegian Computing Center, Oslo: work begun in 1961 on "a description language for computer simulations"; Simula I, a simulation language; "Class and subclass declarations", presented at the IFIP working conference on simulation languages at Lysebu, near Oslo, in 1967 (published in *Simulation Programming Languages*, ed. J. N. Buxton, pp. 158–174); Simula 67, a general programming language built as an extension of Algol 60.
**Atlas:** to be mapped · **Code:** [`Objects.java`](../../code/era-06-hard-problems-and-public-keys/03-objects/) · **Page:** [topic 3](03-objects/README.md)

> **Field note.** Nygaard studied complicated systems by simulating them, and found that the languages of the day made such systems hard even to describe. A harbour or a post office is made of many things, each acting on its own and meeting the others now and then; in a program about it, each thing's data sat in separate arrays and its behaviour in scattered code. He persuaded his colleague Dahl to help him build a language for it. Their answer was to let the program contain the things: a *class* describes one kind of thing, its data and what it can do; any number of *objects* of that class can be made while the program runs; and a *subclass* inherits everything from its class and changes only what differs. A procedure declared *virtual* is looked up in the object's own class when it is called, so a program written for customers in general works unchanged for letters and parcels. Dahl later wrote that this last idea was "a last minute extension". Through Smalltalk, C++ and Java it became, in the words of its IEEE Milestone, "dominant in systems development".

**What hurt:** programs that model many interacting things (a simulation above all) kept each thing's data in separate arrays and its behaviour in scattered code; adding a new kind of thing meant changing the program in many places.
**The step forward:** the class (data and procedures together), objects created dynamically at run time, subclasses by prefixing that inherit all properties of their class, and virtual procedures bound late, so that general code works for every subclass.

**Evidence and certainty**

- IEEE Milestone citation: "Ole-Johan Dahl and Kristen Nygaard created the Simula programming languages in the 1960s at the Norwegian Computer Center. They introduced a new way of modeling and simulating complex tasks." Work began in 1961 to "develop a description language for computer simulations"; SIMULA introduced "the class concept for encapsulation of data structure and code", "subclasses for reuse of code" and "late binding for flexible inheritance"; "Classes could be dynamically instantiated at run-time"; Kay "picked up the ideas of SIMULA in his Smalltalk language", and they were "adopted in wide-spread languages such as C++ and Java". Dedicated 27 September 2017 at the University of Oslo. **Documented** ([Engineering and Technology History Wiki, IEEE Milestone](https://ethw.org/Milestones:Object-Oriented_Programming,_1961-1967))
- ACM A. M. Turing Award (Norway, 2001), to Nygaard "With Ole-Johan Dahl, for ideas fundamental to the emergence of object oriented programming, through their design of the programming languages Simula I and Simula 67"; the page describes the "discrete event simulation language Simula I and general programming language Simula 67", defined "to be an extension of an international standard language, Algol-60". **Documented** ([ACM Awards, Kristen Nygaard](https://awards.acm.org/award_winners/nygaard_5916220))
- "Kristen persuaded Ole-Johan to join him at the Norwegian Computing Center to help developing a simulation language"; "The central concepts in the language were called objects and inheritance." **Documented** ([University of Oslo, rector's blog, 27 September 2017](https://www.uio.no/om/aktuelt/rektorbloggen/2017/50-years-anniversary-of-simula-the-first-object-or.html))
- SIMULA I "was a process description and simulation language"; "the original purpose of the language was to simulate activities from the real world"; Dahl and Nygaard's "Class and subclass declarations" (pp. 158–174) was presented at the Lysebu conference; by "using C as a prefix to another class, the latter would be taken to be a subclass of C inheriting all properties of C"; Dahl called virtual "a last minute extension"; Kay "took from Simula the ideas of classes, objects and object references"; "Smalltalk-72 did not include inheritance", while "Smalltalk-76 included a Simula-like inheritance scheme". **Documented** ([Andrew P. Black, "Object-oriented programming: some history, and challenges for the next fifty years", arXiv](https://arxiv.org/pdf/1303.0427))
- The year of the Turing Award: 2001 on the ACM page and in the IEEE Milestone, 2002 on the University of Oslo page. That the award named for 2001 was presented in 2002 would reconcile them, but no opened source says so. **Disputed**
- That Simula was "the first object-oriented programming language" is the University of Oslo page's title; the IEEE Milestone dates object-oriented programming to 1961–1967 without that phrase. **Documented** as a claim of the University of Oslo

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [50 years anniversary of Simula](https://www.uio.no/om/aktuelt/rektorbloggen/2017/50-years-anniversary-of-simula-the-first-object-or.html) | University of Oslo, rector's blog (2017) | How Nygaard and Dahl came together, in a page |
| Start | [Object-Oriented Programming, 1961-1967](https://ethw.org/Milestones:Object-Oriented_Programming,_1961-1967) | Engineering and Technology History Wiki | The IEEE Milestone citation and what Simula introduced |
| Deeper | [Object-oriented programming: some history, and challenges for the next fifty years](https://arxiv.org/pdf/1303.0427) | Andrew P. Black (2013), arXiv | Classes, prefixing and virtual procedures in Simula's own words, and what Smalltalk took from it |
| Deeper | [Kristen Nygaard](https://awards.acm.org/award_winners/nygaard_5916220) | ACM Awards | The Turing Award citation for Simula I and Simula 67 |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | Class and subclass declarations | O.-J. Dahl and K. Nygaard, in J. N. Buxton (ed.), *Simulation Programming Languages* (1967), pp. 158–174 | The paper that introduced subclasses; no openable copy was found (see **Gaps**) |

**Gaps:** no video page could be opened. No openable copy of "Class and subclass declarations" or of the Simula 67 Common Base was found; they are described here through Black's quotations. The Turing Award year is disputed between the opened sources. The topic's program is written in Java, a descendant of Simula, not in Simula itself.

## 4. A*: search guided by an estimate

**When / where:** Peter E. Hart, Nils J. Nilsson and Bertram Raphael, Artificial Intelligence Group, Stanford Research Institute, Menlo Park, California, for the mobile robot Shakey; "A Formal Basis for the Heuristic Determination of Minimum Cost Paths", manuscript received 24 November 1967, *IEEE Transactions on Systems Science and Cybernetics* SSC-4(2): 100–107 (July 1968).
**Atlas:** to be mapped · **Code:** [`AStar.java`](../../code/era-06-hard-problems-and-public-keys/04-a-star/) · **Page:** [topic 4](04-a-star/README.md)

> **Field note.** The researchers at Stanford Research Institute were building a robot, Shakey, that was to find its own way across a room full of obstacles. Dijkstra's method (Era 5, topic 7) would find the shortest route, but it spreads out evenly in every direction, though the robot knows roughly where its goal lies. Nilsson first proposed a method that always steps towards the place that looks nearest the goal; it is quick, but a wall can lead it astray. Raphael suggested adding the distance already travelled to the estimate of the distance still to go; Hart suspected the result might be the best possible, and the three proved under what conditions it is. Nilsson had called his own method "Algorithm A"; the improved one became A*. Their proof needs one thing of the estimate: that it never overestimate. The method is now, in the words of its IEEE Milestone page, "the path-finding algorithm of choice for a wide variety of applications", among them computing driving directions.

**What hurt:** Dijkstra's method explores in every direction at once, wasting work when the goal's direction is roughly known; heuristic searches that head for the goal were faster but could return long paths, and there was, in the paper's words, "no underlying theory to guide the development of efficient search procedures".
**The step forward:** take next the place with the smallest f(n) = g(n) + h(n), the cost so far plus an estimate of the rest; if the estimate is a lower bound the first path found to the goal is a cheapest one, and under a consistency assumption no admissible method with the same information takes fewer places.

**Evidence and certainty**

- The paper, by Hart, Nilsson and Raphael ("with the Artificial Intelligence Group of the Applied Physics Laboratory"), *IEEE Transactions on Systems Science and Cybernetics*, vol. SSC-4, no. 2, July 1968, pp. 100–107, "Manuscript received November 24, 1967": the minimum-cost path problem "arises naturally in a number of interesting applications", yet "there has been no underlying theory to guide the development of efficient search procedures"; it defines f(n) = g(n) + h(n); Theorem 1, if the estimate is a lower bound on h, "then A* is admissible"; "We shall call this assumption the consistency assumption"; A* "expands the fewest possible nodes necessary to guarantee finding an optimal path", so "we claim that A* is an optimal algorithm" (among admissible algorithms no more informed, with a caveat about ties). **Documented** ([Hart, Nilsson and Raphael 1968, on a St. Francis Xavier University course page](https://people.stfx.ca/jdelamer/courses/csci-564/_downloads/b2220c66675ddde471ca1795147b8e86/A_Formal_Basis_for_the_Heuristic_Determination_of_Minimum_Cost_Paths.pdf))
- A* was created in the Shakey project; Nilsson first proposed the Graph Traverser, whose estimate ignores the distance from the start; Raphael suggested using the sum g(n) + h(n); Hart introduced admissibility and consistency; a later correction claimed consistency was not needed for the optimality theorem, and Dechter and Pearl showed in 1985 that this was false; Dijkstra's algorithm "can be viewed as a special case of A*" (h = 0). **Documented** ([Wikipedia, A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm))
- Raphael's recollection: Nilsson presented a route-planning method for Shakey and called it Algorithm A "For lack of anything better"; Raphael proposed a change, Hart suggested the new version might be optimal, they proved the conditions, and named it A* to tell it from Algorithm A. **Documented** as one participant's recollection ([Communications of the ACM, "A* Search"](https://cacm.acm.org/opinion/a-search))
- The IEEE Milestone page for Shakey (SRI, 1966–1972): A* "provably computes the shortest (or in general minimum cost) path through a network" and is "the path-finding algorithm of choice for a wide variety of applications", including "computing driving directions (whether by a web service or a car navigation system)"; Shakey's methods "proved seminal in robotics and in the design of web servers, automobiles, factories, video games and Mars rovers". **Documented** ([Engineering and Technology History Wiki, IEEE Milestone: Shakey](https://ieeemilestones.ethw.org/Milestones:Shakey:_The_World%E2%80%99s_First_Mobile,_Intelligent_Robot,_1972))
- Who first proposed what: Wikipedia names the Graph Traverser as Nilsson's first proposal; the CACM page says Nilsson's first method was called "Algorithm A". The two accounts may describe the same step; the opened sources do not say. **Conjecture**

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [A* Search](https://cacm.acm.org/opinion/a-search) | Communications of the ACM | How the name came about, as Raphael told it |
| Start | [A* search algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm) | Wikipedia | Admissibility, consistency, and the 1972 correction that was wrong |
| Deeper | [Shakey: The World's First Mobile, Intelligent Robot, 1972](https://ieeemilestones.ethw.org/Milestones:Shakey:_The_World%E2%80%99s_First_Mobile,_Intelligent_Robot,_1972) | Engineering and Technology History Wiki | The robot that needed A*, and what else came out of it |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Formal Basis for the Heuristic Determination of Minimum Cost Paths](https://people.stfx.ca/jdelamer/courses/csci-564/_downloads/b2220c66675ddde471ca1795147b8e86/A_Formal_Basis_for_the_Heuristic_Determination_of_Minimum_Cost_Paths.pdf) | P. E. Hart, N. J. Nilsson and B. Raphael, *IEEE Trans. Systems Science and Cybernetics* (1968), scan on a course page | The eight-page paper with the theorems |

**Gaps:** no video page could be opened. The scan of the paper garbles its inequalities, so the exact wording of Theorem 1's condition was not read. The 1972 correction and Dechter and Pearl's 1985 paper were not opened. The CACM page gives no author or date. The topic's program uses square grids with steps of length one, not Shakey's maps.

## 5. Fast matrix multiplication

**When / where:** Volker Strassen (born 1936 in Düsseldorf-Gerresheim), who had joined the Institute of Applied Mathematics of the University of Zürich in 1968; "Gaussian elimination is not optimal", *Numerische Mathematik* 13: 354–356 (1969).
**Atlas:** to be mapped · **Code:** [`Strassen.java`](../../code/era-06-hard-problems-and-public-keys/05-strassen/) · **Page:** [topic 5](05-strassen/README.md)

> **Field note.** Tables of numbers, matrices, are multiplied by a rule taught in school: every row against every column, n³ multiplications for tables of size n. For two-by-two tables that is eight, and it looked as if it had to be. In 1969 Strassen published a three-page paper with a title that was itself a claim: "Gaussian elimination is not optimal". He had found seven products that are enough for two-by-two tables, and because his formulas never use the fact that ab = ba, the letters may be blocks of a larger table and the trick repeats at every level. One multiplication saved at each level lowers the exponent from 3 to log₂ 7 ≈ 2.807, and with it the cost of inverting matrices and solving systems of equations. The paper turned a settled question into an open one: how small can the exponent be? It has been lowered many times since, most recently in 2026, though none of the later methods is practical; Strassen's own is still used.

**What hurt:** multiplying and inverting n × n matrices, by the rule and by Gaussian elimination, takes about n³ operations, and nobody had shown that fewer were possible.
**The step forward:** seven multiplications for a 2 × 2 product, valid for blocks, applied recursively: about n^2.807 operations for multiplication, and for inversion and other problems of linear algebra that reduce to it.

**Evidence and certainty**

- Volker Strassen, "Gaussian elimination is not optimal", *Numerische Mathematik* 13, pages 354–356, 1969. **Documented** ([bibliographic entry, cr.yp.to](https://cr.yp.to/bib/1969/strassen.bibtex))
- Strassen was born on 29 April 1936 in Düsseldorf-Gerresheim; he joined the Institute of Applied Mathematics at the University of Zürich in 1968; in 1969 he "discovered a novel way to multiply two matrices", with exponent log₂ 7 = 2.808, showing Gaussian elimination "is not an optimal solution"; his later work includes the Schönhage–Strassen multiplication and a randomized primality test (1977); Knuth Prize 2008. **Documented** ([J. J. O'Connor and E. F. Robertson, MacTutor History of Mathematics](https://mathshistory.st-andrews.ac.uk/Biographies/Strassen.html))
- Strassen showed that Gaussian elimination is not an optimal algorithm for many problems of linear algebra; 2 × 2 matrices cannot be multiplied with fewer than 7 multiplications; nine years passed before Pan first improved on the exponent; Coppersmith and Winograd reached ω < 2.38 (1987), of purely theoretical interest; no lower bound above ω ≥ 2 is known. **Documented** ([P. Bürgisser, "Schnelle Matrixmultiplikation und Kombinatorik", Séminaire Lotharingien de Combinatoire, in German](https://www.mat.univie.ac.at/~slc/wpapers/s36buerg.pdf))
- The bound on ω: 2.8074 (Strassen, 1969), 2.796 (Pan, 1978), 2.3755 (Coppersmith and Winograd, 1990), 2.3728639 (Le Gall, 2014), 2.371339 (Alman, Duan, Vassilevska Williams, Xu, Xu and Zhou, 2024), 2.371177 (2026); "Unlike algorithms with faster asymptotic complexity, Strassen's algorithm is used in practice", while the later improvements "are not used in practice, because they are galactic algorithms". **Documented** ([Wikipedia, Computational complexity of matrix multiplication](https://en.wikipedia.org/wiki/Computational_complexity_of_matrix_multiplication))
- The 2026 bound: "Our combined approach yields an upper bound of 𝜔 < 2.371177, improving the previous best bound of 2.371339", by E. Dupont, M. Eisenberger, B. Kozlovskii, A. Mehrabian, F. J. R. Ruiz, A. See, R. Zhou, J. Alman, V. Vassilevska Williams and M. Balog, submitted 18 August 2026, using an AI system, AlphaEvolve. **Documented** ([arXiv 2608.16884](https://arxiv.org/pdf/2608.16884))
- Where Strassen's method begins to pay in practice: "recursively applying Strassen's method can save time for n > 100", as quoted from Wikipedia. **Conjecture**: it depends on the machine; the topic's program counts operations, not time ([John D. Cook, "How fast can you multiply matrices?", 2018](https://www.johndcook.com/blog/2018/08/31/how-fast-can-you-multiply-matrices/))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [How fast can you multiply matrices?](https://www.johndcook.com/blog/2018/08/31/how-fast-can-you-multiply-matrices/) | John D. Cook (2018) | Eight products, then seven, in a short post |
| Start | [Volker Strassen](https://mathshistory.st-andrews.ac.uk/Biographies/Strassen.html) | MacTutor History of Mathematics | The mathematician, and his other fast algorithms |
| Deeper | [Computational complexity of matrix multiplication](https://en.wikipedia.org/wiki/Computational_complexity_of_matrix_multiplication) | Wikipedia | Every lowering of the exponent since 1969, with references |
| Deeper | [Schnelle Matrixmultiplikation und Kombinatorik](https://www.mat.univie.ac.at/~slc/wpapers/s36buerg.pdf) | Peter Bürgisser, Séminaire Lotharingien de Combinatoire (in German) | How the exponent came down, from someone in Strassen's school |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Gaussian elimination is not optimal (bibliographic entry)](https://cr.yp.to/bib/1969/strassen.bibtex) | V. Strassen, *Numerische Mathematik* 13: 354–356 (1969) | The three-page paper; no openable copy of the text was found |
| Scholar | [Improving the matrix multiplication exponent with modern optimization and AlphaEvolve](https://arxiv.org/pdf/2608.16884) | E. Dupont et al. (2026), arXiv | The latest bound, found with the help of an AI system |

**Gaps:** no video page could be opened. The text of Strassen's 1969 paper was not opened (the publisher's page redirected and was not followed); its contents are described through MacTutor and Bürgisser. Why Strassen looked for the method, and whether he expected to find it, is not in any opened source. The topic's program counts operations; its rounding comparison is one experiment, not a theorem.

## 6. The relational model of data

**When / where:** Edgar F. Codd, IBM Research Laboratory, San Jose, California; "A Relational Model of Data for Large Shared Data Banks", *Communications of the ACM* 13(6): 377–387 (June 1970).
**Atlas:** to be mapped · **Code:** [`Relational.java`](../../code/era-06-hard-problems-and-public-keys/06-relational-model/) · **Page:** [topic 6](06-relational-model/README.md)

> **Field note.** Codd was an Oxford-trained mathematician who had flown with the Royal Air Force in the war and joined IBM as a programmer in 1949. By the late 1960s the databases he saw kept their records in trees and chains, and a program reached its data by walking them, one link at a time, in an order fixed when the database was designed. Change the order, and the programs broke. His paper opens with a demand: "Future users of large data banks must be protected from having to know how the data is organized in the machine." He proposed that users see only relations, tables of rows with no order and no pointers, and ask for what they want with a few operations on whole tables, leaving the machine to decide how to find it. A research group at IBM began building it, as System R, in 1973, and two of its members, Chamberlin and Boyce, designed the query language now called SQL. Codd received the Turing Award in 1981.

**What hurt:** programs that used hierarchical and network databases depended on how the data was stored (its ordering, its indexes, its access paths); a question against the grain of the structure meant reading all of it, and changing the structure broke the programs.
**The step forward:** data as relations (sets of n-tuples) in normal form, with operations such as restriction, projection and join; users say what they want, the system chooses how, and the storage can change without changing the questions.

**Evidence and certainty**

- The paper, by E. F. Codd, "IBM Research Laboratory, San Jose, California", *Communications of the ACM* 13(6), June 1970, pp. 377–387: "Future users of large data banks must be protected from having to know how the data is organized in the machine"; a relation is "a set of ntuples" (relations of degree n are "n-ary"); the three principal kinds of data dependence are "ordering dependence, indexing dependence, and access path dependence"; normalization proceeds from the top of a tree of relations, taking "its primary key" and expanding "each of the immediately subordinate relations"; operations include permutation, projection ("any duplication in the rows" removed), join, composition and restriction; the model is a basis for "treating derivability, redundancy, and consistency of relations". **Documented** ([Codd 1970, on a Boston University reading-group page](https://cs-people.bu.edu/mathan/reading-groups/papers-classics/codd.pdf))
- Codd was "an Oxford-educated mathematician working at the IBM San Jose Research Lab"; "The early databases used rigid hierarchical structures and convoluted navigational plans"; "A group of programmers in 1973 undertook an industrial-strength implementation: the System R project"; Chamberlin and Boyce "developed SQL"; "DB2 was first shipped in 1983"; Codd "received the Turing Award from the Association of Computing Machinery in 1981"; relational databases became "a multibillion-dollar industry and the standard for processing financial records". The page also says Relational Software (later Oracle) "produced the first commercially available relational database in 1977". **Documented** as IBM states it ([IBM History, The relational database](https://www.ibm.com/history/relational-database))
- Codd was born in 1923 on the Isle of Portland in Dorset, studied at Exeter College, Oxford, flew in the Royal Air Force in the Second World War, joined IBM in 1949 "as a mathematical programmer", took a master's degree and doctorate at the University of Michigan from 1961, joined the San Jose lab in 1968, and died in 2003. **Documented** ([IBM History, Edgar F. Codd](https://www.ibm.com/es-es/history/edgar-codd))
- Chamberlin and Boyce created SEQUEL as System R's query language; "Later SEQUEL was renamed to SQL because of a trademark issue"; System R began in 1973. **Documented** ([Agnieszka Kozubek-Krycuń, "The History of SQL", LearnSQL, 2020](https://learnsql.com/blog/history-of-sql/))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The relational database](https://www.ibm.com/history/relational-database) | IBM History | The idea, System R, SQL and DB2, from the company where it began |
| Start | [The History of SQL](https://learnsql.com/blog/history-of-sql/) | Agnieszka Kozubek-Krycuń, LearnSQL (2020) | From SEQUEL to SQL |
| Deeper | [Edgar F. Codd](https://www.ibm.com/es-es/history/edgar-codd) | IBM History | The life of the man behind the model |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Relational Model of Data for Large Shared Data Banks](https://cs-people.bu.edu/mathan/reading-groups/papers-classics/codd.pdf) | E. F. Codd, *Communications of the ACM* 13(6): 377–387 (1970), on a Boston University page | The eleven-page paper |

**Gaps:** no video page could be opened. A copy of the paper at the University of Michigan could not be fetched (the site disallows it); the Boston University copy was read. IBM's date for the first commercial relational database (1977) was not checked against another source. The paper's normal form is the first of several; the later ones are not covered. The topic's program uses an invented supplier-and-part database, and its tree is a simplified model of a hierarchical database, not IMS or any real product.

## 7. B-trees

**When / where:** Rudolf Bayer and Edward M. McCreight, Boeing Scientific Research Laboratories: the idea in autumn 1969 (by Bayer's account); a Boeing technical report, circulated in July 1970 and presented at the 1970 ACM SIGFIDET Workshop on Data Description and Access; "Organization and Maintenance of Large Ordered Indexes", *Acta Informatica* 1(3): 173–189 (1972).
**Atlas:** to be mapped · **Code:** [`BTrees.java`](../../code/era-06-hard-problems-and-public-keys/07-b-trees/) · **Page:** [topic 7](07-b-trees/README.md)

> **Field note.** At Boeing in the late 1960s the data of its "Jumbo" programme, its many parts and the history of how each was made, had pushed the data processing of the day to its limits; that is how Bayer remembered it. A balanced tree (Era 5, topic 11) finds a key in about twenty steps among a million, but when the index is too large for memory and lives on a disk, each step may be a separate trip to the disk. Bayer walked into his colleague McCreight's office with an idea: make every node of the tree a whole page of the disk, holding many keys, so that each trip brings back a great deal and a search needs only a few. A page that overflows splits in two and passes its middle key up; the tree grows at the root, never at the leaves, so it stays perfectly balanced. They never said what the B stands for. McCreight later said only that "It has to do with Balance"; Bayer's view, as McCreight reported it, was that "the more you think about what the B in B-Tree means, the better you understand B-Trees!" The structure became, in Wikipedia's words, "the standard index implementation in almost all relational databases".

**What hurt:** indexes too large for main memory had to live on disk, where every node of a binary tree could cost a separate slow access; keeping a large index ordered and balanced under insertions and deletions was hard.
**The step forward:** pages of between k and 2k keys, all leaves at one depth; insertion splits a full page and passes the middle key up, deletion borrows from or merges with a neighbour; a search reads about log base k of n pages.

**Evidence and certainty**

- Rudolf Bayer and Edward M. McCreight invented B-trees "while working at Boeing Research Labs", to "efficiently manage index pages for large random-access files", assuming the index would be too large to fit in main memory; "Organization and maintenance of large ordered indices" was first circulated in July 1970 and later published in *Acta Informatica*; the authors never explained the B, and suggestions include "Boeing, balanced, between, broad, bushy, and Bayer"; McCreight in 2013: "Everybody does!", "It has to do with Balance", and Bayer's "the more you think about what the B in B-Tree means, the better you understand B-Trees!"; the B-tree "remains the standard index implementation in almost all relational databases", and it is used in file systems such as HFS+, APFS, NTFS and ext4. **Documented** ([Wikipedia, B-tree](https://en.wikipedia.org/wiki/B-tree))
- Bayer's memoir (in German): "Am weitaus wichtigsten war die Arbeit über B-Bäume im Herbst 1969" (by far the most important was the work on B-trees in autumn 1969); "Ich erinnere mich noch genau, wie ich in das Büro meines Kollegen Ed McCreight spaziert bin" (I remember exactly how I walked into my colleague Ed McCreight's office); the data processing of the time "an ihre Grenzen stieß bei der Verwaltung der vielen Einzelteile" (reached its limits in managing the many individual parts) of Boeing's "Jumbo" programme; the work appeared first as a Boeing technical report, then at the "1970 ACM SICFIDET [sic] Workshop on DATA DESCRIPTION AND ACCESS", and "die erste offizielle und referierte Publikation erschien erst 1972 in den Acta Informatica". **Documented** ([Rudolf Bayer, Memoiren, Technical University of Munich](https://db.cit.tum.de/~bayer/Memoiren-Bayer.pdf))
- R. Bayer and E. McCreight, "Organization and Maintenance of Large Ordered Indexes", *Acta Informatica* 1(3): 173–189, Springer, 1972. **Documented** ([bibliographic entry, Augsburg University of Applied Sciences](https://glossar.hs-augsburg.de/Bayer,_McCreight_(1972)))
- McCreight received his Ph.D. from Carnegie Mellon University in 1969, co-invented the B-tree "while at Boeing", later co-designed the Xerox Alto and improved Weiner's suffix-tree algorithm (1976). **Documented** ([Wikipedia, Edward M. McCreight](https://en.wikipedia.org/wiki/Edward_M._McCreight))
- When the B-tree was invented: 1970 in Wikipedia; autumn 1969 in Bayer's memoir, with the report circulated in July 1970. The memoir dates the idea, Wikipedia the report. **Documented**, two dates for two events

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [B-tree](https://en.wikipedia.org/wiki/B-tree) | Wikipedia | The structure, its variants, and the mystery of the B |
| Deeper | [Memoiren](https://db.cit.tum.de/~bayer/Memoiren-Bayer.pdf) | Rudolf Bayer, Technical University of Munich (in German) | The inventor's own account of Boeing and the B-tree |
| Deeper | [Edward M. McCreight](https://en.wikipedia.org/wiki/Edward_M._McCreight) | Wikipedia | The co-inventor, who went on to the Xerox Alto |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Organization and Maintenance of Large Ordered Indexes (bibliographic entry)](https://glossar.hs-augsburg.de/Bayer,_McCreight_(1972)) | R. Bayer and E. McCreight, *Acta Informatica* 1(3): 173–189 (1972) | The paper; no openable copy of the text was found |

**Gaps:** no video page could be opened. The text of the 1972 paper and of the 1970 report was not opened, so the paper's own bounds and cost analysis are not quoted; the bounds in the topic's program are derived from the rules, not taken from the paper. McCreight's 2013 remarks are quoted as Wikipedia gives them; the original was not opened. The memoir's "Jumbo" is not identified further in the opened text. The topic's program counts pages read, not disk time.

## 8. NP-completeness

**When / where:** Stephen A. Cook, University of Toronto, "The Complexity of Theorem-Proving Procedures", ACM Symposium on the Theory of Computing (STOC), 1971; Richard M. Karp, University of California, Berkeley, "Reducibility Among Combinatorial Problems", in *Proceedings of a Symposium on the Complexity of Computer Computations*, 1972; independently, Leonid Levin in the Soviet Union, "Universal search problems", *Problemy Peredachi Informatsii* (*Problems of Information Transmission*), 1973.
**Atlas:** to be mapped · **Code:** [`NpComplete.java`](../../code/era-06-hard-problems-and-public-keys/08-np-completeness/) · **Page:** [topic 8](08-np-completeness/README.md)

> **Field note.** By 1970 the species had fast methods for many problems and none at all for others: for the best route through many towns, the best timetable, the largest group of people who all know each other, the methods known came down to trying an enormous number of possibilities. Cook, who had just moved to Toronto after Berkeley's mathematics department declined to keep him, showed in 1971 that one problem, deciding whether a formula of true-and-false variables can be made true, carries all the others of its kind inside it: every problem whose answers can be checked quickly can be translated quickly into a question about such a formula. Levin, in the Soviet Union, found the same thing independently. A year later Karp translated the formula problem into twenty-one problems about graphs, sets and numbers, so that if any one of them had a fast method, they all would. "If Cook made the P versus NP question interesting to logicians," a later complexity theorist wrote, "Karp made the question important to everyone else." Cook thought a proof that no fast method exists "would be a major breakthrough". Nobody has found either a fast method or such a proof; the question is one of the seven Millennium Prize Problems.

**What hurt:** many practical problems of search and optimization resisted every attempt at an efficient algorithm, and there was no way to tell whether the failure lay with the searchers or with the problems.
**The step forward:** polynomial-time reduction between problems; the class NP of problems whose solutions can be checked in polynomial time; Cook's theorem that satisfiability is as hard as anything in NP (NP-complete); Karp's reductions showing 21 natural problems equally hard; the open question whether P = NP.

**Evidence and certainty**

- Cook's paper (Stephen A. Cook, University of Toronto): "any recognition problem solved by a polynomial time-bounded nondeterministic Turing machine" can be reduced to deciding whether a propositional formula is a tautology; Theorem 1, any set accepted "by some nondeterministic Turing machine within polynomial time" is P-reducible to {DNF tautologies}; "it is fruitless to search for a polynomial decision procedure for the subgraph problem" unless tautologies have one; "I feel it is worth spending considerable effort trying to prove this conjecture. Such a proof would be a major breakthrough in complexity theory." **Documented** ([Cook 1971, on a University of Maryland course page](https://www.cs.umd.edu/~gasarch/COURSES/452/F14/cookpaper.pdf))
- Cook was born on 14 December 1939; Berkeley's mathematics department did not reappoint him (Karp: "It is to our everlasting shame that we were unable to persuade the math department to give him tenure"); he joined the University of Toronto in 1970; the paper was presented at the 1971 ACM SIGACT Symposium on the Theory of Computing; "This theorem was proven independently by Leonid Levin in the Soviet Union"; Turing Award 1982; the P versus NP question "remains open and is among the seven famous Millennium Prize Problems". **Documented** ([Wikipedia, Stephen Cook](https://en.wikipedia.org/wiki/Stephen_Cook))
- Levin (born 2 November 1948, Dnipropetrovsk) studied under Kolmogorov; his "Universal search problems" appeared in *Problems of Information Transmission* in 1973; the result is "often called the Cook–Levin theorem"; he emigrated to the United States in 1978. **Documented** ([Wikipedia, Leonid Levin](https://en.wikipedia.org/wiki/Leonid_Levin))
- Karp's 1972 paper used Cook's theorem and gave polynomial-time many-one reductions from satisfiability to 21 problems, among them 0–1 integer programming, clique, vertex cover, set covering, Hamiltonian circuit, 3-satisfiability, chromatic number, exact cover, Steiner tree, 3-dimensional matching and knapsack. **Documented** ([Wikipedia, Karp's 21 NP-complete problems](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems))
- Lance Fortnow: Cook gave "the first formal treatment of the P versus NP problem"; Levin reached similar results independently; "If Cook made the P versus NP question interesting to logicians, Karp made the question important to everyone else"; Karp's paper named the classes P and NP and defined the reductions now called Karp reductions; later work showed hundreds, if not thousands, of natural problems NP-complete. **Documented** ([Fortnow, "Favorite Theorems: NP-Completeness", 2005](https://blog.computationalcomplexity.org/2005/04/favorite-theorems-np-completeness.html); [Fortnow, "Favorite Theorems: Combinatorial NP-Complete Problems", 2005](https://blog.computationalcomplexity.org/2005/05/favorite-theorems-combinatorial-np.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Favorite Theorems: NP-Completeness](https://blog.computationalcomplexity.org/2005/04/favorite-theorems-np-completeness.html) | Lance Fortnow, Computational Complexity blog (2005) | Cook and Levin in a few paragraphs |
| Start | [Favorite Theorems: Combinatorial NP-Complete Problems](https://blog.computationalcomplexity.org/2005/05/favorite-theorems-combinatorial-np.html) | Lance Fortnow (2005) | Why Karp's 21 problems changed the field |
| Start | [Karp's 21 NP-complete problems](https://en.wikipedia.org/wiki/Karp%27s_21_NP-complete_problems) | Wikipedia | The tree of reductions |
| Deeper | [Stephen Cook](https://en.wikipedia.org/wiki/Stephen_Cook) | Wikipedia | Berkeley, Toronto, and the 1971 paper |
| Deeper | [Leonid Levin](https://en.wikipedia.org/wiki/Leonid_Levin) | Wikipedia | The same discovery, made independently in the Soviet Union |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Complexity of Theorem-Proving Procedures](https://www.cs.umd.edu/~gasarch/COURSES/452/F14/cookpaper.pdf) | S. A. Cook, STOC 1971, on a University of Maryland course page | The paper that defined the question |

**Gaps:** no video page could be opened. Karp's and Levin's papers were not opened; their contents are given through Wikipedia and Fortnow. The full list of Karp's 21 problems was not extracted (18 were read). Where the 1971 symposium was held is not in the opened sources. The topic's program shows that its reductions preserve the answer on small random formulas and measures one search method on random formulas; neither says anything about whether P = NP.

## 9. Depth-first search and linear-time graph algorithms

**When / where:** Robert Tarjan, Stanford University and then Cornell University, with John Hopcroft (Cornell, on sabbatical at Stanford from June 1970); "Depth-First Search and Linear Graph Algorithms", *SIAM Journal on Computing* 1(2), June 1972 (received 30 August 1971); Hopcroft and Tarjan, "Efficient planarity testing", *Journal of the ACM* 21(4): 549–568 (October 1974).
**Atlas:** to be mapped · **Code:** [`DepthFirst.java`](../../code/era-06-hard-problems-and-public-keys/09-depth-first-search/) · **Page:** [topic 9](09-depth-first-search/README.md)

> **Field note.** Exploring a maze by always taking an unexplored passage and turning back only at dead ends is old; a nineteenth-century French author, Trémaux, described a form of it for solving mazes. In June 1970 a graduate student at Stanford, Tarjan, was looking for a thesis topic, and Hopcroft had just arrived from Cornell for a sabbatical year. They set out to test whether a network can be drawn on a page without crossing lines, and found that the key was to study depth-first search with care: the order in which it reaches the vertices, and the few edges that lead back up the tree, carry enough information to answer such questions in time proportional to the size of the graph. Tarjan's 1972 paper used one extra number per vertex to find, in a single pass, the points whose failure would cut a network in two, and the groups of a one-way network in which everything can reach everything else. No method that must look at the whole graph can do better than linear time. Hopcroft and Tarjan shared the Turing Award in 1986.

**What hurt:** questions about the structure of graphs (connectivity, cut vertices, strongly connected components, planarity) were answered by methods that, in effect, repeated a search many times, taking time that grows faster than the size of the graph.
**The step forward:** depth-first search as a tool for analysis: number the vertices in the order reached, classify the remaining edges (fronds), and keep a lowpoint per vertex; biconnected and strongly connected components in time proportional to V + E, and with more work planarity.

**Evidence and certainty**

- Tarjan's paper: "Department of Computer Science, Cornell University", *SIAM J. Comput.* Vol. 1, No. 2, June 1972, "Received by the editors August 30, 1971, and in revised form March 9, 1972"; the space and time of both algorithms (strongly connected components and biconnected components) are bounded by k₁V + k₂E + k₃ "where V is the number of vertices and E is the number of edges"; LOWLINK(v) "is the smallest vertex which is in the same component as v and is reachable by traversing zero or more tree arcs followed by at most one frond or cross-link"; the biconnectivity algorithm is credited to Hopcroft and Tarjan. **Documented** ([Tarjan 1972, on a Carnegie Mellon University page](https://www.cs.cmu.edu/~cdm/resources/Tarjan1972-sccs.pdf))
- Tarjan's Turing Award lecture, "Algorithm Design" (*Communications of the ACM* 30(3): 204–212, March 1987): he entered Stanford's graduate program after Caltech in 1969; in June 1970 "John Hopcroft arrived from Cornell to begin a sabbatical year at Stanford"; "The focus of our activities became the problem of testing the planarity of a graph"; "After carefully studying the properties of depth-first search, we developed a way to generate paths in O(n) time using depth-first search." **Documented** ([Tarjan, "Algorithm Design", on a Williams College course page](https://www.cs.williams.edu/~heeringa/classes/cs256/s07/tarjan-turing.pdf))
- Tarjan, born 30 April 1948 in Pomona, California, received his Ph.D. at Stanford in 1972 under Robert Floyd and Donald Knuth with the thesis "An Efficient Planarity Algorithm"; he shared the 1986 Turing Award with Hopcroft "For fundamental achievements in the design and analysis of algorithms and data structures"; "The Hopcroft–Tarjan planarity testing algorithm was the first linear-time algorithm for planarity testing." **Documented** ([Wikipedia, Robert Tarjan](https://en.wikipedia.org/wiki/Robert_Tarjan))
- J. Hopcroft and R. Tarjan, "Efficient planarity testing", *Journal of the ACM* 21(4): 549–568, October 1974. **Documented** ([Journal of the ACM bibliography, MIT](https://projects.csail.mit.edu/jacm/References/hopcroftt1974:549.html))
- "A version of depth-first search was investigated in the 19th century by French mathematician Charles Pierre Trémaux as a strategy for solving mazes"; the search takes O(|V| + |E|) on explicit graphs; its uses include biconnected and strongly connected components, planarity testing and topological sorting. **Documented** ([Wikipedia, Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search); [Wikipedia, Trémaux tree](https://en.wikipedia.org/wiki/Tr%C3%A9maux_tree))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Depth-first search](https://en.wikipedia.org/wiki/Depth-first_search) | Wikipedia | The search, its orders, and its uses |
| Start | [Robert Tarjan](https://en.wikipedia.org/wiki/Robert_Tarjan) | Wikipedia | The many algorithms of one designer |
| Deeper | [Algorithm Design (Turing Award lecture)](https://www.cs.williams.edu/~heeringa/classes/cs256/s07/tarjan-turing.pdf) | R. E. Tarjan, *Communications of the ACM* (1987) | How planarity led him and Hopcroft to depth-first search, in his own words |
| Deeper | [Trémaux tree](https://en.wikipedia.org/wiki/Tr%C3%A9maux_tree) | Wikipedia | The maze-solver's tree, and why every depth-first search builds one |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Depth-First Search and Linear Graph Algorithms](https://www.cs.cmu.edu/~cdm/resources/Tarjan1972-sccs.pdf) | R. Tarjan, *SIAM Journal on Computing* 1(2) (1972), on a Carnegie Mellon page | Strong components and biconnected components in linear time |
| Scholar | [Efficient planarity testing (bibliographic entry)](https://projects.csail.mit.edu/jacm/References/hopcroftt1974:549.html) | J. Hopcroft and R. Tarjan, *Journal of the ACM* 21(4): 549–568 (1974) | The first linear-time planarity test; the text was not opened |

**Gaps:** no video page could be opened. The date and place of Trémaux's maze method are not in the opened sources. The planarity paper's text was not opened. The topic's program does not test planarity; it finds cut vertices, biconnected components and strong components, and counts its steps.

## 10. Public-key cryptography

**When / where:** Whitfield Diffie and Martin E. Hellman, Department of Electrical Engineering, Stanford University, "New Directions in Cryptography", *IEEE Transactions on Information Theory* IT-22(6): 644–654 (November 1976; received 3 June 1976), with Ralph Merkle working independently; Ronald L. Rivest, Adi Shamir and Leonard M. Adleman, Laboratory for Computer Science, MIT, "A Method for Obtaining Digital Signatures and Public-Key Cryptosystems", received 4 April 1977, *Communications of the ACM* 21: 120–126 (1978). In secret, at the British signals agency GCHQ: James Ellis (1970), Clifford Cocks (1973) and Malcolm Williamson (1974), revealed in 1997.
**Atlas:** to be mapped · **Code:** [`PublicKey.java`](../../code/era-06-hard-problems-and-public-keys/10-public-key-cryptography/) · **Page:** [topic 10](10-public-key-cryptography/README.md)

> **Field note.** Every cipher the species had used, from the substitution ciphers that frequency analysis broke (Era 2, topic 7) to the Enigma machine (Era 4, topic 8), needed the two parties to share a secret key before they could speak in secret. In 1976 two researchers at Stanford opened their paper with a sentence that turned out to be accurate: "We stand today on the brink of a revolution in cryptography." Diffie and Hellman showed how two strangers could agree on a secret key in full view of an eavesdropper, using a calculation that is easy one way and, as far as anyone knew, hard the other; and they described signatures that anyone can check and only one person can make. They had the idea of a public key that encrypts while a private key decrypts, but no practical way to build one. A year later three young researchers at MIT found it in the arithmetic of very large primes, recommended a new randomized test for finding such primes, and printed a challenge: "The reader is challenged to find a way to 'break' our method." In 1997 the British government revealed that its own cryptographers had found much the same ideas years earlier and kept them secret.

**What hurt:** symmetric ciphers require a secret key to be shared in advance, which does not scale to many parties who have never met, and there was no digital equivalent of a signature that anyone could verify.
**The step forward:** key agreement over a public channel by exponentiation modulo a prime (Diffie–Hellman); public-key encryption and signatures from a trapdoor one-way function, RSA's exponentiation modulo a product of two large primes; fast probabilistic primality testing to make the keys.

**Evidence and certainty**

- Diffie and Hellman, "New Directions in Cryptography" (Invited Paper), *IEEE Transactions on Information Theory* Vol. IT-22, No. 6, November 1976, pp. 644–654, manuscript received 3 June 1976, both of the Department of Electrical Engineering, Stanford University: "We stand today on the brink of a revolution in cryptography"; in a public key cryptosystem enciphering and deciphering use distinct keys and the enciphering key can be published; key exchange by exponentiation modulo a prime q, whose reversal needs discrete logarithms; "Merkle [1] has independently studied the problem of" distributing keys over an insecure channel; a digital signature must be "a digital phenomenon with the same properties as a written signature". **Documented** ([Diffie and Hellman 1976, on Martin Hellman's Stanford page](https://ee.stanford.edu/~hellman/publications/24.pdf))
- Rivest, Shamir and Adleman, MIT Laboratory for Computer Science, "Received April 4, 1977; revised September 1, 1977": encryption C ≡ M^e (mod n), decryption M ≡ C^d (mod n); they recommend "100-digit (decimal) prime numbers p and q, so that n has 200 digits"; for primality "we recommend the elegant 'probabilistic' algorithm due to Solovay and Strassen"; a worked example with p = 47, q = 59, n = 2773, e = 17, d = 157; "The reader is challenged to find a way to 'break' our method"; public-key cryptography is "an elegant concept invented by Diffie and Hellman". **Documented** ([Rivest, Shamir and Adleman, on an MIT course page](https://people.csail.mit.edu/vinodv/COURSES/MAT302-S13/RSApaper.pdf))
- Published in *Communications of the ACM* 21, pages 120–126, 1978. **Documented** ([bibliographic entry, cr.yp.to](https://cr.yp.to/bib/1978/rivest.bibtex))
- GCHQ "released a document on December 1 1997, claiming to have invented publickey cryptography several years before it was discovered by the research community"; in 1973 Cocks "described what was essentially RSA"; in 1974 Williamson "invented another classified algorithm, remarkably similar to Diffie-Hellman"; Schneier's judgment: "while they may have discovered the mathematics, it is clear that they never understood its significance". **Documented**, with Schneier's judgment as his opinion ([Bruce Schneier, "The Secret Story of Nonsecret Encryption", 1998](https://www.schneier.com/essays/archives/1998/04/the_secret_story_of.html))
- Cocks (born 28 December 1950) joined CESG, part of GCHQ, in September 1973, and "quickly developed what later became known as the RSA encryption algorithm"; his "Note on 'Non-Secret Encryption'" is dated 20 November 1973; the work was declassified in 1997, and Cocks told the story in a public talk on 18 December 1997. **Documented** ([Wikipedia, Clifford Cocks](https://en.wikipedia.org/wiki/Clifford_Cocks))
- Ellis (25 September 1924 – 25 November 1997) "first proposed his scheme for 'non-secret encryption' in 1970", in "The possibility of secure non-secret digital encryption", CESG Report 3006, January 1970; he died a month before the public announcement. **Documented** ([Wikipedia, James H. Ellis](https://en.wikipedia.org/wiki/James_H._Ellis))
- The date of Ellis's idea: 1970 on his Wikipedia page (with the January 1970 report), 1969 on Cocks's Wikipedia page, and 1960 in Schneier's essay as read. **Disputed**

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Secret Story of Nonsecret Encryption](https://www.schneier.com/essays/archives/1998/04/the_secret_story_of.html) | Bruce Schneier (1998) | The public inventions and the secret ones, and how to credit them |
| Start | [Clifford Cocks](https://en.wikipedia.org/wiki/Clifford_Cocks) | Wikipedia | RSA, found first and kept secret |
| Deeper | [James H. Ellis](https://en.wikipedia.org/wiki/James_H._Ellis) | Wikipedia | The idea of non-secret encryption, inside GCHQ |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf) | W. Diffie and M. E. Hellman, *IEEE Trans. Information Theory* (1976) | Key exchange, public keys and signatures, proposed |
| Scholar | [A Method for Obtaining Digital Signatures and Public-Key Cryptosystems](https://people.csail.mit.edu/vinodv/COURSES/MAT302-S13/RSApaper.pdf) | R. L. Rivest, A. Shamir and L. Adleman, *Communications of the ACM* (1978) | The first practical public-key system, with its small worked example |

**Gaps:** no video page could be opened. Merkle's paper, Solovay and Strassen's test paper, and the GCHQ documents were not opened. The topic's program uses keys far too small or too simply made for real use; its 1,024-bit key is an illustration, and it does not implement the padding that real RSA needs.

## 11. Fast string searching

**When / where:** James H. Morris, Jr., a text editor for the CDC 6400 (summer 1969); Donald E. Knuth (Stanford), from a theorem of Stephen Cook's about pushdown automata (early 1970); Vaughan R. Pratt; "Fast Pattern Matching in Strings", *SIAM Journal on Computing* 6(2): 323–350 (June 1977; received 29 August 1974). Robert S. Boyer (Stanford Research Institute) and J Strother Moore (Xerox Palo Alto Research Center), "A Fast String Searching Algorithm", *Communications of the ACM* 20(10): 762–772 (October 1977); R. W. Gosper independently.
**Atlas:** to be mapped · **Code:** [`StringSearch.java`](../../code/era-06-hard-problems-and-public-keys/11-string-search/) · **Page:** [topic 11](11-string-search/README.md)

> **Field note.** Finding a word in a text is the most ordinary of tasks, and the obvious method is nearly always good enough: try each starting place and compare letter by letter. But on an unlucky text it compares almost every letter with almost every letter of the pattern, and each failure sends it back to reread text it has already seen. Morris met the second problem in 1969 while writing a text editor and found a way never to back up; Knuth, early in 1970, arrived at the same method from an abstract theorem of Cook's; Pratt made it independent of the size of the alphabet; when he described it to Morris, Morris recognized it as his own. The three published together, with a running time "proportional to the sum of the lengths of the strings". In the same year Boyer and Moore turned the problem around: compare from the end of the pattern, and a letter that does not occur in it lets the pattern jump its whole length. Their search is "usually sublinear": on English, with a pattern of five letters, it looks at about a quarter of the text. The longer the pattern, the less of the text it reads.

**What hurt:** the simple method's worst case is about m × n comparisons, and it rereads text on every failed attempt, which is awkward when text arrives as a stream or from a file that cannot be backed up.
**The step forward:** precompute from the pattern what is already known after a partial match: Knuth, Morris and Pratt's "next" table, giving linear time and no backing up; Boyer and Moore's right-to-left comparison with two shift tables, skipping most of the text on ordinary inputs.

**Evidence and certainty**

- Knuth, Morris and Pratt, *SIAM J. Comput.* Vol. 6, No. 2, June 1977, pp. 323–350, "Received August 29, 1974, and in revised form April 7, 1976": the algorithm "finds all occurrences of one given string within another, in running time proportional to the sum of the lengths of the strings"; it "was discovered in a rather interesting way": "One of the authors (J. H. Morris) was implementing a text-editor for the CDC 6400 computer during the summer of 1969"; "Another author (D. E. Knuth) learned early in 1970 of S. A. Cook's surprising theorem" about two-way deterministic pushdown automata; "Pratt modified Knuth's data structure so that the running-time was independent of the alphabet size"; when Pratt described it, Morris recognized it as his own; a postscript notes that Boyer, Moore and R. W. Gosper independently found a faster method that skips text. **Documented** ([Knuth, Morris and Pratt 1977, on a Brown University course page](https://cs.brown.edu/courses/csci1810/fall-2023/resources/ch2_readings/kmp_strings.pdf))
- Boyer (Stanford Research Institute) and Moore (Xerox Palo Alto Research Center), *Communications of the ACM* 20(10), October 1977, pp. 762–772: the algorithm is "usually sublinear"; the expected number of characters inspected is c(i + patlen) where "c < 1 and gets smaller as patlen increases"; for English patterns of length 5 it inspects about 0.24 characters per character passed, where Knuth–Morris–Pratt inspects 1 and the simple algorithm about 1.1; the tables delta1 (by character) and delta2 (by matched ending); Gosper independently found the delta1-only version; Knuth proved in January 1976 that the improved delta2 gives linear worst-case behaviour. **Documented** ([Boyer and Moore 1977, on J Strother Moore's University of Texas page](https://www.cs.utexas.edu/%7Emoore/publications/fstrpos.pdf))
- The Boyer–Moore algorithm is "the standard benchmark for practical string-search literature"; worst-case bounds were later proved by Guibas and Odlyzko (5n comparisons) and Cole (3n, 1991); with Galil's rule (1979) it is linear in all cases. **Documented** ([Wikipedia, Boyer–Moore string-search algorithm](https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm))
- The year of Guibas and Odlyzko's bound: 1980 in the article's text, 1977 in its reference list. **Disputed**

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Boyer–Moore string-search algorithm](https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm) | Wikipedia | The two tables, and the long road to its worst-case bound |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Fast Pattern Matching in Strings](https://cs.brown.edu/courses/csci1810/fall-2023/resources/ch2_readings/kmp_strings.pdf) | D. E. Knuth, J. H. Morris and V. R. Pratt, *SIAM Journal on Computing* (1977), on a Brown course page | The algorithm, its theory, and a section on how it was found three times |
| Scholar | [A Fast String Searching Algorithm](https://www.cs.utexas.edu/%7Emoore/publications/fstrpos.pdf) | R. S. Boyer and J S. Moore, *Communications of the ACM* (1977), on Moore's page | Searching from the right, with measurements on English and random text |

**Gaps:** no video page could be opened. Cook's theorem on two-way pushdown automata and Gosper's version were not opened. The topic's program measures its own implementation on this book's field notes (about 18,600 letters) rather than the texts Boyer and Moore used; its delta1 table counts only letters before the last, a common variant of theirs.

## 12. Universal compression: Lempel and Ziv

**When / where:** Jacob Ziv and Abraham Lempel, Technion – Israel Institute of Technology, Haifa (Ziv on sabbatical at Bell Telephone Laboratories, Murray Hill, and Lempel later at Sperry Research Center when the first paper appeared); "A Universal Algorithm for Sequential Data Compression", *IEEE Transactions on Information Theory* IT-23(3), from p. 337 (May 1977; received 23 June 1975); "Compression of Individual Sequences via Variable-Rate Coding", IT-24(5): 530–536 (September 1978).
**Atlas:** to be mapped · **Code:** [`LempelZiv.java`](../../code/era-06-hard-problems-and-public-keys/12-lempel-ziv/) · **Page:** [topic 12](12-lempel-ziv/README.md)

> **Field note.** Huffman's code (Era 5, topic 3) is the best possible for coding letters one at a time, but it must be told how often each letter occurs, and it cannot see that a whole phrase has occurred before. Two colleagues at the Technion in Haifa, an electrical engineer and a computer scientist, set out to compress data without knowing anything about its source in advance. Their first method keeps a window of what has already been sent and replaces each new stretch by a pointer into it: how far back, how long, and the next letter. The second builds a dictionary of phrases as it goes. They proved that on long enough inputs these methods do as well as a code designed for the source: they are universal. In 1984 Welch published a faster form of the dictionary method, and descendants of the two methods went on to compress files, images and data on the Internet; the IEEE Milestone at Haifa says the algorithm "contributed significantly in making the internet a global communications medium". Both men died in 2023.

**What hurt:** good compression codes (Huffman's, Shannon's) had to be designed for a known source, with known probabilities; real data arrive without them, and repeated phrases were invisible to letter-by-letter codes.
**The step forward:** code each new piece of the input by reference to what has already been seen, a sliding window (LZ77) or a growing dictionary of phrases (LZ78), with no model of the source; the compression ratio approaches the best achievable for any stationary source as the input grows.

**Evidence and certainty**

- Ziv and Lempel, *IEEE Transactions on Information Theory* Vol. IT-23, No. 3, May 1977, pp. 337 onward, "Manuscript received June 23, 1975; revised July 6, 1976": "A universal algorithm for sequential data compression is presented"; its compression ratio "uniformly approaches the lower bounds on the compression ratios attainable by block-to-variable codes and variable-to-block codes designed to match a completely specified source"; the encoder finds the "reproducible extension" into the buffer and sends "the pointer of the reproduction", the length, and the last symbol; both authors at the Technion, Haifa, Ziv then at Bell Telephone Laboratories and Lempel at Sperry Research Center. **Documented** ([Ziv and Lempel 1977, on a Peking University page](https://www.icst.pku.edu.cn/mipl/docs/ziv1977.pdf))
- IEEE Milestone, dedicated 6 September 2004 in Haifa: "The data compression algorithm developed at this site in 1977 by Abraham Lempel and Jacob Ziv became a basis for enabling data transmission via the internet in an efficient way. It contributed significantly in making the internet a global communications medium"; the 1978 paper (IT-24(5): 530–536) and Welch's "A Technique for High-Performance Data Compression" (*Computer* 17(6), 1984); its use in ".gif image files"; Lempel taught at the Technion from 1963 to 2004 and died in 2023; Ziv died in 2023. **Documented** ([Engineering and Technology History Wiki, IEEE Milestone](https://ethw.org/Milestones:Lempel-Ziv_Data_Compression_Algorithm,_1977))
- Ziv "died on 26 March at the age of 91"; in 1977, while he was on sabbatical at Bell Labs, he and Lempel published the algorithm known as LZ77, and the next year LZ78; IEEE Medal of Honor 2021 "for fundamental contributions to information theory and data compression technology"; the algorithms led to Unix compression programs of the early 1980s and to WinZip and Gzip in the early 1990s, and "are used today in GIF, TIFF and other image formats". **Documented** ([Amanda Davis, "Remembering Jacob Ziv", IEEE Spectrum, 10 April 2023](https://spectrum.ieee.org/remembering-jacob-ziv))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Remembering Jacob Ziv](https://spectrum.ieee.org/remembering-jacob-ziv) | Amanda Davis, IEEE Spectrum (2023) | The man, the sabbatical, and where the algorithms went |
| Start | [Lempel-Ziv Data Compression Algorithm, 1977](https://ethw.org/Milestones:Lempel-Ziv_Data_Compression_Algorithm,_1977) | Engineering and Technology History Wiki | The IEEE Milestone, with the 1978 and 1984 papers |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Universal Algorithm for Sequential Data Compression](https://www.icst.pku.edu.cn/mipl/docs/ziv1977.pdf) | J. Ziv and A. Lempel, *IEEE Trans. Information Theory* (1977), on a Peking University page | The sliding-window method and its proof of universality |

**Gaps:** no video page could be opened. The 1978 paper and Welch's 1984 paper were not opened. Lempel's birth date is not in the opened sources, nor is the last page of the 1977 paper (the opened copy runs from 337 to 342, with references after). The topic's program uses simple fixed-width codes for its tokens, not the codes of the papers or of any file format, and its universality experiment is one source, not a proof.

## 13. Logical clocks and the order of events

**When / where:** Leslie Lamport, Massachusetts Computer Associates (where he worked from 1970 to 1977; the paper also gives an address at SRI International); "Time, Clocks, and the Ordering of Events in a Distributed System", *Communications of the ACM* 21(7): 558–565 (July 1978).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** As the species' computers came to be joined into networks, a question that had seemed philosophical became practical: when two machines with separate clocks each record an event, which came first? Lamport answered by refusing to trust clocks at all. One event "happened before" another only if information could have flowed from the first to the second, along a process or through a message; otherwise the two are concurrent, and no observer inside the system can tell their order. He noted that the definition resembles the way special relativity treats space and time. A simple counter in each machine, advanced at every event and pushed forward whenever a message arrives with a larger stamp, is enough to give every event a number consistent with this order; breaking ties by machine number turns it into one total order that every machine can compute for itself. With it Lamport showed how machines can share a resource fairly with no one in charge. Thirty-six years later the citation for his Turing Award spoke of "imposing clear, well-defined coherence on the seemingly chaotic behavior of distributed computing systems".

**What hurt:** in a system of separate computers that communicate only by messages, physical clocks disagree and messages are delayed, so there was no reliable meaning for "before", and no way for the computers to agree on the order of requests without a central coordinator.
**The step forward:** the happened-before relation, a partial order defined by process order and messages; logical clocks satisfying the Clock Condition (a → b implies C(a) < C(b)) by two rules; a total order by breaking ties with process numbers; a distributed mutual-exclusion algorithm that grants requests in that order; an analysis of physical clocks for orderings the system cannot see.

**Evidence and certainty**

- Lamport, "Time, Clocks, and the Ordering of Events in a Distributed System", Massachusetts Computer Associates, Inc., *Communications of the ACM* 21(7), July 1978, pp. 558–565: happened-before (→) is "the smallest relation satisfying the following three conditions" (order within a process, sending before receipt, transitivity), and events are concurrent if neither happened before the other; the Clock Condition, if a → b then C(a) < C(b); IR1, "Each process P_i increments C_i between any two successive events"; IR2, messages carry the sender's clock and the receiver sets its clock above both its own value and the stamp; a total order by clock values with ties broken by an arbitrary ordering of the processes; mutual exclusion with requests granted in order, where "a central scheduler" granting requests in arrival order fails; anomalous behaviour when events outside the system, such as a telephone call, impose an order; the definition resembles the space-time formulation of special relativity. **Documented** ([Lamport 1978, on the ACM Turing Award site](https://amturing.acm.org/p558-lamport.pdf))
- ACM, 18 March 2014: Lamport was recognized "for imposing clear, well-defined coherence on the seemingly chaotic behavior of distributed computing systems", work including "causality and logical clocks, replicated state machines, and sequential consistency"; he "developed LaTeX"; with others he "invented the notion of Byzantine failure"; Intel's Wen-Hann Wang: "the brilliant 'logical clock' abstraction he introduced some 40 years ago has had an immense impact on the field". **Documented** ([ACM press release](https://www.acm.org/media-center/2014/march/acm-turing-award-goes-to-pioneer-who-advanced-reliability-and-consistency-of-computing-systems))
- Lamport, born 7 February 1941 in New York, worked at Massachusetts Computer Associates (1970–1977), SRI International (1977–1985), Digital Equipment Corporation and Compaq (1985–2001) and Microsoft Research (2001 to his retirement in January 2025); Turing Award 2013 "for fundamental contributions to the theory and practice of distributed and concurrent systems"; also the bakery algorithm and LaTeX. **Documented** ([Wikipedia, Leslie Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport))
- The wording of the Turing Award citation: "fundamental contributions to the theory and practice of distributed and concurrent systems" on Wikipedia; "imposing clear, well-defined coherence on the seemingly chaotic behavior of distributed computing systems" in the ACM's announcement. **Documented**, two wordings; which is the formal citation is not settled in the opened sources

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [ACM Turing Award Goes to Pioneer Who Advanced Reliability and Consistency of Computing Systems](https://www.acm.org/media-center/2014/march/acm-turing-award-goes-to-pioneer-who-advanced-reliability-and-consistency-of-computing-systems) | ACM (2014) | What logical clocks led to, in the award announcement |
| Start | [Leslie Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport) | Wikipedia | A career in concurrency, from the bakery algorithm to LaTeX |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Time, Clocks, and the Ordering of Events in a Distributed System](https://amturing.acm.org/p558-lamport.pdf) | L. Lamport, *Communications of the ACM* 21(7): 558–565 (1978) | Eight pages that defined "before" for distributed systems |

**Gaps:** no video page could be opened. The paper's received date is not in the opened copy. The paper's physical-clock analysis is not reproduced. The topic's program simulates processes and messages in one program with random delays; it does not run on separate machines.

## What the era leaves behind

- **Faster than obvious.** The FFT (1), Strassen's products (5) and the string searches of Knuth, Morris, Pratt, Boyer and Moore (11) show that a problem's obvious operation count is not its true cost; Strassen's exponent is still being lowered in 2026.
- **Programs that share.** Critical sections and semaphores (2) for processes that share memory; logical clocks and a total order of events (13) for computers that share nothing but messages.
- **Programs built from things.** Simula's classes, objects and subclasses (3): object-oriented programming, in its IEEE Milestone's words now "dominant in systems development".
- **Data that outgrow memory.** Relations that hide how data are stored (6), and B-trees that store them on disk in a few reads per search (7); compression that needs no model of its data (12).
- **Search with knowledge.** A* (4) uses an estimate of the distance to go; depth-first search (9) reads the structure of a graph in one pass.
- **Hardness as a fact and as a tool.** NP-completeness (8) shows that hundreds, if not thousands, of problems stand or fall together; public-key cryptography (10) builds secrecy on problems believed to be hard.

Era 7 picks up in 1978 and runs towards the present: randomness and approximation, the algorithms of the Internet, and machines that learn.
