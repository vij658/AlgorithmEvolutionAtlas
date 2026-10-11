# Era 4 — What Can Be Computed: from Hilbert's questions to Hamming's codes

*Reference catalog. Thirteen developments, from 1895 to 1950.*

> **Field note from the visiting historian.** In the third era, procedures were put into tables and machines. In this one, mathematicians ask what a procedure is. Hilbert wants a process that settles every question; within forty years Gödel, Church and Turing have defined computation precisely and proved that some questions have no such process. In the same years the first electronic computers are built, programs are stored in their memories as numbers, and the new machines are set to work on chance, planning, secrecy and their own errors.

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

A note on videos: video pages on YouTube could not be opened from the environment used to build this catalog, so videos appear only where a university lecture page could be opened (Oxford's podcast pages, for topic 7). Each topic's **Gaps** line says so. A few pages could not be opened because the request to open them was withdrawn; those are listed as gaps too.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Hilbert's questions](#1-hilberts-questions) | Paris 1900; Hilbert and Ackermann 1928; Matiyasevich 1970 | "A process ... by a finite number of operations" had no definition |
| 2 | [Runge–Kutta](#2-rungekutta) | Runge 1895; Heun 1900; Kutta 1901 | Euler's steps need to be tiny to be accurate |
| 3 | [Markov chains](#3-markov-chains) | Markov 1906; *Eugene Onegin* 1913 | Probability theory assumed independent trials |
| 4 | [The cheapest network](#4-the-cheapest-network-borůvka-and-jarník) | Borůvka 1926; Jarník 1930 | Connecting towns with the least wire |
| 5 | [Gödel's numbering](#5-gödels-numbering) | Königsberg 1930; printed 1931 | Hilbert wanted every statement settled by a proof |
| 6 | [Church's lambda calculus](#6-churchs-lambda-calculus) | 1932–1936 | No definition of "effectively calculable" |
| 7 | [Turing's machines](#7-turings-machines) | 1936 (printed 1937) | The decision problem needed a model of a person computing |
| 8 | [Breaking Enigma](#8-breaking-enigma) | Rejewski 1932; bomba 1938; Bombe 1940 | A cipher with too many settings to try |
| 9 | [The stored program, and merge sort](#9-the-stored-program-and-merge-sort) | EDVAC report and merging program 1945; Baby 1948 | Machines rewired for every problem; sorting on card machines |
| 10 | [Monte Carlo](#10-monte-carlo-and-numbers-that-only-look-random) | Ulam 1946; ENIAC 1948; Metropolis and Ulam 1949 | Too many interacting chances to calculate |
| 11 | [The simplex method](#11-the-simplex-method) | Dantzig 1947 | Plans with astronomically many options |
| 12 | [Shannon: switches, bits and entropy](#12-shannon-switches-bits-and-entropy) | Thesis 1937; *Mathematical Theory of Communication* 1948 | Circuits by trial and error; no measure of information |
| 13 | [Hamming's codes](#13-hammings-codes) | 1947; published 1950 | A detected error meant starting again |

## 1. Hilbert's questions

**When / where:** David Hilbert's address to the International Congress of Mathematicians in Paris, 1900, listed his problems for the coming century; the tenth asks for a process to decide whether any Diophantine equation has a whole-number solution. In 1928 Hilbert and Wilhelm Ackermann posed the *Entscheidungsproblem*: an algorithm that decides whether any statement of logic is universally valid. Both were answered in the negative: the Entscheidungsproblem by Church and Turing in 1936, the tenth problem by Matiyasevich in 1970, building on Davis, Putnam and Robinson.
**Atlas:** to be mapped · **Code:** [`HilbertsQuestions.java`](../../code/era-04-what-can-be-computed/01-hilberts-questions/) · **Page:** [topic 1](01-hilberts-questions/README.md)

> **Field note.** For three eras I have watched people invent procedures, each for one kind of question. At the start of this century a Göttingen mathematician asked for more: a procedure that would settle every question of a given kind, by a finite number of operations. He was sure it existed: "in mathematics there is no ignorabimus". Within forty years his own question had been turned into mathematics, and the answer was no. Some questions have no procedure at all.

**What hurt:** each kind of equation needed its own method (Era 2, topics 5 and 9), and no one knew whether a single method could settle them all.
**The step forward:** the question itself: what exactly is "a process ... by a finite number of operations"? Asking it forced the definition of an algorithm (topics 6 and 7), and with it the proof that some problems have none.

**Evidence and certainty**

- Problem 10: "To devise a process according to which it can be determined by a finite number of operations" whether a Diophantine equation is solvable in rational integers; Hilbert: "in mathematics there is no ignorabimus". **Documented** ([Hilbert, *Mathematical Problems*, trans. Newson, Project Gutenberg](https://gutenberg.org/files/71655/71655-h/71655-h.htm); [reprint, Bull. AMS 37 (2000)](https://www.ams.org/bull/2000-37-04/S0273-0979-00-00881-8/), originally Bull. AMS 8 (1902))
- The Paris address and its count: MacTutor speaks of "Hilbert's famous 23 Paris problems", while its own links say 24. **Disputed** (the count) ([MacTutor, Hilbert](https://mathshistory.st-andrews.ac.uk/Biographies/Hilbert/))
- 1930, Königsberg: "Wir müssen wissen, wir werden wissen" ("We must know, we shall know"); Hilbert's proof-theory aim was shown impossible by Gödel's paper of 1931. **Documented** ([MacTutor, Hilbert](https://mathshistory.st-andrews.ac.uk/Biographies/Hilbert/))
- The Entscheidungsproblem: "a challenge posed by David Hilbert and Wilhelm Ackermann in 1928", asking for "an algorithm that considers an input statement and answers "yes" or "no""; "Such an algorithm was proven to be impossible by Alonzo Church and Alan Turing in 1936". **Documented** ([Wikipedia, Entscheidungsproblem](https://en.wikipedia.org/wiki/Entscheidungsproblem); [Dawar, Computation Theory, Cambridge](https://www.cl.cam.ac.uk/teaching/2324/CompTheory/slides.pdf))
- Where it was posed: the 1928 International Congress (Cambridge course notes) or the 1928 book by Hilbert and Ackermann (Wikipedia names both the conference and the pair). **Documented**, the emphasis differs
- The tenth problem: "such a general algorithm cannot exist"; Diophantine sets are "recursively enumerable (also known as semi-decidable)": a search finds a solution if there is one, but may run for ever if there is none. **Documented** ([Wikipedia, Hilbert's tenth problem](https://en.wikipedia.org/wiki/Hilbert%27s_tenth_problem))
- A search can run for decades: no integer equal to 4 or 5 modulo 9 is a sum of three cubes, but "it is unknown whether this necessary condition is sufficient"; 33 was settled by Andrew Booker and 42 by Booker and Sutherland, both in 2019, with solutions of 16 and 17 digits; the open cases below 1,000 are 114, 390, 627, 633, 732, 921 and 975; "it is unknown whether representing numbers as sums of cubes is decidable". **Documented** ([Wikipedia, Sums of three cubes](https://en.wikipedia.org/wiki/Sums_of_three_cubes)); the topic's program checks the solutions for 30, 33 and 42
- Matiyasevich: "On the morning of 3 January 1970, I believed I had a solution of Hilbert's tenth problem, but by the end of that day I had discovered a flaw", repaired the next morning; "I saw at once that Julia Robinson had a fresh and wonderful idea." **Documented** ([MacTutor, Matiyasevich](https://mathshistory.st-andrews.ac.uk/Biographies/Matiyasevich/))

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Computation Theory (lecture slides)](https://www.cl.cam.ac.uk/teaching/2324/CompTheory/slides.pdf) | Anuj Dawar (after Andrew Pitts), University of Cambridge, 2024 | The Entscheidungsproblem as the starting point of computation theory: register machines, Turing machines, the lambda calculus and the halting problem |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [David Hilbert](https://mathshistory.st-andrews.ac.uk/Biographies/Hilbert/) | MacTutor | The Paris problems, the Königsberg speech, and what Gödel did to the programme |
| Start | [Entscheidungsproblem](https://en.wikipedia.org/wiki/Entscheidungsproblem) | Wikipedia | The decision problem of 1928 and its negative answer in 1936 |
| Start | [Hilbert's tenth problem](https://en.wikipedia.org/wiki/Hilbert%27s_tenth_problem) | Wikipedia | Why searching for solutions works only one way |
| Start | [Sums of three cubes](https://en.wikipedia.org/wiki/Sums_of_three_cubes) | Wikipedia | A search that halts only if an answer exists, run for decades |
| Deeper | [Yuri Matiyasevich](https://mathshistory.st-andrews.ac.uk/Biographies/Matiyasevich/) | MacTutor | The final step of 1970, in Matiyasevich's own words |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Mathematical Problems (1900)](https://gutenberg.org/files/71655/71655-h/71655-h.htm) | David Hilbert, trans. Mary Winston Newson (1902), Project Gutenberg | The address itself, with problem 10 and "no ignorabimus" |
| Scholar | [Mathematical problems (reprint)](https://www.ams.org/bull/2000-37-04/S0273-0979-00-00881-8/) | *Bulletin of the AMS* 37:407–436 (2000), reprinting Bull. AMS 8 (1902) | The same translation in the journal of record |

**Gaps:** no video page could be opened. Hilbert and Ackermann's *Grundzüge der theoretischen Logik* (1928) was found only in booksellers' listings. Matiyasevich's 1970 paper was not opened.

## 2. Runge–Kutta

**When / where:** Carl Runge, "Ueber die numerische Auflösung von Differentialgleichungen" (1895), extended Euler's step-by-step method (1768–1770) using the midpoint and trapezoidal rules. Karl Heun (1900) carried the conditions to order 4; Wilhelm Kutta's thesis (1901) classified the methods of order 4 and gave the classical one; E. J. Nyström (1925) completed order 5.
**Atlas:** to be mapped · **Code:** [`RungeKutta.java`](../../code/era-04-what-can-be-computed/02-runge-kutta/) · **Page:** [topic 2](02-runge-kutta/README.md)

> **Field note.** Since Newton, the laws of motion have been written as differential equations: how fast a quantity changes, given where it is now. Most of them cannot be solved by formula. Euler had shown how to creep forward in small steps, each step following the slope at its start, but the errors pile up. Two Germans improved the step itself: sample the slope a few times inside the step, at the start, the middle and the end, and take a weighted average. With four samples, halving the step divides the error by sixteen.

**What hurt:** most differential equations have no formula for their solution, and Euler's step-by-step method needs very small steps for accuracy: its error is proportional to the step.
**The step forward:** within each step, evaluate the slope at several points and combine them with weights chosen so that the error is proportional to a high power of the step (the fourth for the classical method).

**Evidence and certainty**

- Euler "first proposed it in his book Institutionum calculi integralis" (1768–1770); the method is first order: "the global error ... is proportional to the step size". **Documented** ([Wikipedia, Euler method](https://en.wikipedia.org/wiki/Euler_method))
- Runge's idea was to base the step "not on this unsymmetrical and relatively inaccurate Riemann rule, but on such improved formulas as the midpoint and trapezoidal rules"; Heun "took the order conditions as far as 4"; Kutta "made a complete classification of order 4 methods" and took the analysis "as far as order 5", though "his work was incomplete in two different respects", corrected by Nyström (1925). **Documented** ([Butcher, *Applied Numerical Mathematics* 20 (1996)](https://tlakoba.w3.uvm.edu/math337/paper_1996_Butcher_RKhistory.pdf))
- The methods "were developed around 1900 by the German mathematicians Carl Runge and Wilhelm Kutta"; "The RK4 method is a fourth-order method"; the 3/8 rule is "also due to Kutta in 1901". **Documented** ([Wikipedia, Runge–Kutta methods](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods))
- Kutta's doctoral thesis, published in 1901, "contains the now famous Runge-Kutta method"; Kutta also gave the theorem on the lift of an aerofoil, found independently by Zhukovsky. **Documented** ([MacTutor, Kutta](https://mathshistory.st-andrews.ac.uk/Biographies/Kutta/))
- Runge held a chair of applied mathematics at Göttingen from 1904 and "worked out many numerical and graphical methods, gave numerical solutions of differential equations". **Documented** ([MacTutor, Runge](https://mathshistory.st-andrews.ac.uk/Biographies/Runge/))
- The journal of Runge's 1895 paper: the Zenodo record gives the title, date (1 June 1895) and a Springer DOI but not the journal; it is usually cited as *Mathematische Annalen* 46. **Conjecture** here (not confirmed in an opened source)

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Runge–Kutta methods](https://en.wikipedia.org/wiki/Runge%E2%80%93Kutta_methods) | Wikipedia | The family of methods, RK4, and adaptive steps |
| Start | [Euler method](https://en.wikipedia.org/wiki/Euler_method) | Wikipedia | The first-order method that Runge improved |
| Start | [Martin Wilhelm Kutta](https://mathshistory.st-andrews.ac.uk/Biographies/Kutta/) | MacTutor | Kutta's thesis of 1901 and his aerofoil theorem |
| Start | [Carl Runge](https://mathshistory.st-andrews.ac.uk/Biographies/Runge/) | MacTutor | Runge's applied mathematics at Göttingen |
| Deeper | [A history of Runge–Kutta methods](https://tlakoba.w3.uvm.edu/math337/paper_1996_Butcher_RKhistory.pdf) | J. C. Butcher, *Applied Numerical Mathematics* 20:247–260 (1996), on a University of Vermont course page | From Euler and Runge to Heun, Kutta and Nyström |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Ueber die numerische Auflösung von Differentialgleichungen (1895)](https://zenodo.org/record/2178704) | Carl Runge, open-access scan on Zenodo (CC0) | Runge's paper that started the family |
| Scholar | [Ueber die numerische Auflösung totaler Differentialgleichungen (1905)](https://eudml.org/doc/58614) | Carl Runge, *Nachrichten ... Göttingen* (1905), 252–257, EuDML record | Runge's later paper on systems of equations |

**Gaps:** no video page could be opened. Kutta's thesis (1901) and Heun's paper (1900) were not opened. The classical fourth-order weights are not printed in the extracted text of the opened sources; the topic's program checks the method's order by measurement instead.

## 3. Markov chains

**When / where:** Andrei Markov, St Petersburg. His first paper on dependent trials was written in 1906 (Kazan journal, printed 1907); papers on chains followed in the Academy's *Bulletin* (1911); on 23 January 1913 he presented to the Imperial Academy of Sciences his count of vowels and consonants in the first 20,000 letters of Pushkin's *Eugene Onegin*.
**Atlas:** to be mapped · **Code:** [`MarkovChains.java`](../../code/era-04-what-can-be-computed/03-markov-chains/) · **Page:** [topic 3](03-markov-chains/README.md)

> **Field note.** For two centuries the law of large numbers, that averages settle down over many trials, had been proved only for trials that do not influence each other: coins, dice, independent draws. Another mathematician, Nekrasov, claimed that independence was needed, and drew conclusions about free will from it. Markov, who called this an abuse of mathematics, built the counter-example: a sequence where each step depends on the one before, and whose averages still settle. Then, to show such sequences exist outside mathematics, he counted the letters of a poem. After a vowel, a vowel came only about one time in eight; after a consonant, about two times in three. The letters were not independent, and their averages settled anyway.

**What hurt:** probability theory could only handle trials that do not influence one another, but most things worth predicting (weather, language, queues, molecules) depend on what came just before.
**The step forward:** let the probability of the next state depend on the present state only, through a fixed table of transition probabilities. Markov proved that the long-run frequencies of the states still converge, so the law of large numbers holds without independence.

**Evidence and certainty**

- Markov (14 June 1856 – 20 July 1922) "is particularly remembered for his study of Markov chains, sequences of random variables in which the future variable is determined by the present variable". **Documented** ([MacTutor, Markov](https://mathshistory.st-andrews.ac.uk/Biographies/Markov/))
- The quarrel: Nekrasov (1902) argued that the law of large numbers requires independence and drew conclusions about free will; Markov called this "an abuse of mathematics" and showed that "The law of large numbers applies perfectly well to systems of dependent variables if they meet certain criteria." **Documented** ([Hayes, *American Scientist* 101 (2013)](https://www.americanscientist.org/sites/americanscientist.org/files/201321152149545-2013-03Hayes.pdf); [Wikipedia, Markov chain](https://en.wikipedia.org/wiki/Markov_chain))
- The 1906 paper began with a two-state system whose transition probabilities are all strictly between 0 and 1, and showed that the frequency of each state converges to a fixed value. **Documented** ([Hayes](https://www.americanscientist.org/sites/americanscientist.org/files/201321152149545-2013-03Hayes.pdf); [CUHK MATH4240, "A Historical Note"](https://www.math.cuhk.edu.hk/course_builder/2425/math4240/HistoricalNote.pdf))
- Its title, transliterated: "Rasprostranenie zakona bol'shih chisel na velichiny, zavisyaschie drug ot druga" (Extension of the law of large numbers to quantities depending on each other), in the *Izvestiya* of the Physico-Mathematical Society at Kazan University; the journal version appeared in 1907. **Documented** ([Basharin, Langville and Naumov, "The Life and Work of A. A. Markov"](https://www.maths.tcd.ie/~nhb/talks/Markov.pdf))
- The lecture of 23 January 1913 to the Imperial Academy of Sciences in St Petersburg analysed the first 20,000 letters of *Eugene Onegin*. **Documented** ([Harvard Gazette, 2013](https://news.harvard.edu/gazette/story/2013/01/an-idea-that-changed-the-world); [Angelino, Princeton LIPS blog](https://lips.cs.princeton.edu/markov-chain-centenary/))
- The counts: 8,638 vowels and 11,362 consonants; 1,104 vowel–vowel pairs, 3,827 consonant–consonant pairs and 15,069 mixed pairs; if letters were independent, about 3,731 double vowels would be expected. **Documented** ([Hayes](https://www.americanscientist.org/sites/americanscientist.org/files/201321152149545-2013-03Hayes.pdf); the pair counts also in [Schwartz, IEEE Spectrum](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models))
- The probabilities: a vowel overall 0.432; a vowel after a vowel 0.128; a vowel after a consonant 0.663. **Documented** ([Basharin, Langville and Naumov](https://www.maths.tcd.ie/~nhb/talks/Markov.pdf)); the topic's program recomputes all three from Hayes's counts
- How the letters were laid out: punctuation and spaces removed, then written in 200 grids of 10 by 10. **Documented** ([Schwartz, IEEE Spectrum](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models))
- How much of the poem: "the poem's first 70 stanzas (20,000 characters)" ([Angelino](https://lips.cs.princeton.edu/markov-chain-centenary/)) against "the first 76 stanzas" ([Sabatini, arXiv 2604.20221](https://arxiv.org/pdf/2604.20221)). **Disputed** (the opened sources differ; Markov's own text was not opened)
- A recount of the modern-spelling text matched Markov's simple dispersion coefficient (0.303) and came close to his complex one (0.199 against 0.195). **Documented** ([Sabatini](https://arxiv.org/pdf/2604.20221))
- After Markov: the Ehrenfest diffusion model (1907) and Poincaré's card-shuffling chains (1912) are now read as Markov chains; Kolmogorov's 1931 paper built "a large part of the early theory of continuous-time Markov processes". **Documented** ([Wikipedia, Markov chain](https://en.wikipedia.org/wiki/Markov_chain))
- Shannon (1948, topic 12) generated imitation English from letter- and word-pair statistics, extending Markov's counting. **Documented** ([Schwartz, IEEE Spectrum](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [First Links in the Markov Chain](https://www.americanscientist.org/sites/americanscientist.org/files/201321152149545-2013-03Hayes.pdf) | Brian Hayes, *American Scientist* 101(2):92–97 (March–April 2013) | The quarrel with Nekrasov, the letter counts, and where chains are used now |
| Start | [Andrey Markov & Claude Shannon Counted Letters to Build the First Language-Generation Models](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models) | Oscar Schwartz, IEEE Spectrum (11 November 2019) | How Markov laid out the letters, and how Shannon took the idea further |
| Start | [An idea that changed the world](https://news.harvard.edu/gazette/story/2013/01/an-idea-that-changed-the-world) | Corydon Ireland, Harvard Gazette (23 January 2013) | The centenary of the 1913 lecture |
| Start | [Andrei Andreyevich Markov](https://mathshistory.st-andrews.ac.uk/Biographies/Markov/) | MacTutor | Markov's life and his work on the law of large numbers |
| Deeper | [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) | Wikipedia | Definitions, the history after Markov, and applications |
| Deeper | [A Historical Note](https://www.math.cuhk.edu.hk/course_builder/2425/math4240/HistoricalNote.pdf) | MATH4240 Stochastic Processes, Chinese University of Hong Kong | The 1906 theorem and the fixed vector (.432, .568) of the Onegin chain |
| Scholar | [The Life and Work of A. A. Markov](https://www.maths.tcd.ie/~nhb/talks/Markov.pdf) | G. P. Basharin, A. N. Langville and V. A. Naumov (PDF on a Trinity College Dublin page) | Markov's papers, his letters to Chuprov, and the Onegin probabilities |
| Scholar | [Markov reads Puškin, again](https://arxiv.org/pdf/2604.20221) | Angelo Maria Sabatini, arXiv 2604.20221 | A recount of Markov's encoding of *Onegin*, with his dispersion coefficients |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Sur un cas d'épreuves liées en chaîne multiple](https://mathnet.ru/eng/im6871) | A. A. Markov, *Bulletin de l'Académie Impériale des Sciences de St.-Pétersbourg*, VI série, 5(3):171–186 (1911), in Russian; Math-Net.Ru record | One of Markov's papers on trials linked in a chain |
| Scholar | [Sur les valeurs liées qui ne forment pas une chaîne véritable](https://mathnet.ru/eng/im6867) | A. A. Markov, same *Bulletin*, 5(2):113–126 (1911), in Russian; Math-Net.Ru record | Markov on linked quantities that are not a true chain |
| Scholar | [Chaînes de Markov discrètes dans le domaine linguistique : l'article de 1913 de A.A. Markov](https://www.numdam.org/item/PSMIR_1981___2_A3_0/) | Micheline Petruszewycz, Séminaire d'histoire des mathématiques, Rennes (1981), in French; Numdam | A reading of the 1913 paper, with its original citation |

**Gaps:** no video page could be opened. Markov's 1913 paper itself, in Russian or in the English translation (*Science in Context* 19(4):591–600, 2006), was not opened: the Onegin counts here come from Hayes, Schwartz and Basharin et al. The 1906 Kazan paper was not opened. The published counts add up only if the 20,000 pairs reach one letter past the sample; the program shows they then need the first letter to be a consonant (chapter one begins «Мой дядя») and the 20,001st to be a vowel. Markov's own text, which would settle how he counted, was not opened.

## 4. The cheapest network: Borůvka and Jarník

**When / where:** Otakar Borůvka, Brno, 1926: "O jistém problému minimálním" (*Práce moravské přírodovědecké společnosti* 3, 37–58) and a short note for engineers in *Elektrotechnický obzor* 15. Vojtěch Jarník, Prague, 1930: a reply written as a letter to Borůvka, under the same title (*Práce moravské přírodovědecké společnosti* 6, 57–63).
**Atlas:** to be mapped · **Code:** [`CheapestNetwork.java`](../../code/era-04-what-can-be-computed/04-cheapest-network/) · **Page:** [topic 4](04-cheapest-network/README.md)

> **Field note.** Southern Moravia was being wired for electricity, and a friend at the power company put a question to a young mathematician: how do you connect every town using the least total length of line? Borůvka's answer is the gentlest algorithm I have met. Every town reaches for its nearest neighbour. That leaves small clusters; every cluster reaches for its nearest cluster, and so on, until one network remains. Four years later Jarník wrote to him with a different way: start at one town and keep adding the cheapest line from the growing network to a town not yet in it. Both are still taught. In the 1950s, Americans found the same methods again, and for a long time they were called by the Americans' names.

**What hurt:** to connect n points as cheaply as possible, the number of possible networks grows explosively with n, so trying them is out of the question.
**The step forward:** a greedy rule that is provably optimal: the cheapest line leaving any connected group of towns always belongs to some cheapest network. Borůvka adds such a line for every group at once, round after round; Jarník grows one group from a single start.

**Evidence and certainty**

- The problem "was communicated to him by a friend Jindrich Saxel - an employee of Zapadomoravske elektrarny" (West-Moravian Powerplants), in the setting of "the electrification of South-Moravia district". **Documented** ([Nešetřil, Milková and Nešetřilová, preprint 2000](https://kam.mff.cuni.cz/kamserie/clanky/2000/s466.pdf); [MacTutor, Borůvka](https://mathshistory.st-andrews.ac.uk/Biographies/Boruvka/))
- The two 1926 papers: "O jistém problému minimálním", *Práce moravské přírodovědecké společnosti* III, 3 (1926), 37–58; and a note in *Elektrotechnický obzor* 15 (1926), 153–4, with "a lucid description of his algorithms by means of a geometric example with 40 cities". **Documented** ([Nešetřil, Milková and Nešetřilová](https://kam.mff.cuni.cz/kamserie/clanky/2000/s466.pdf))
- Borůvka's step, in his engineering note: "I will join each of the given points with the point nearest to it." Graham and Hell's summary: "an edge ab is in the resulting forest G if and only if it is the shortest edge at a or at b." **Documented** ([Graham and Hell, *Annals of the History of Computing* 7(1) (1985)](https://math.ucdavis.edu/~saito/data/acha.read.w12/graham-hell-mst.pdf))
- In the 40-city example, joining each point to its nearest neighbour leaves 13 separate "strokes"; joining each stroke to its nearest stroke leaves 4; one more round gives "a single polygonal stroke ... which solves the given problem". Borůvka assumed all the distances are different. **Documented** ([Nešetřil, Milková and Nešetřilová, *Discrete Mathematics* 233 (2001)](https://www.dml.cz/bitstream/handle/10338.dmlcz/500413/Boruvka_03-0000-60_1.pdf))
- Jarník's paper of 1930 is a letter: "In your article 'On a certain minimal problem'... you solved an interesting problem"; it grows the network by adding the lightest edge from the connected set to a new vertex, which is "essentially Prim's algorithm"; the commentators propose the name Jarník–Prim. **Documented** ([Korte and Nešetřil, *Discrete Mathematics* 235 (2001)](https://www.dml.cz/bitstream/handle/10338.dmlcz/500662/Jarnik_04-0000-19_1.pdf))
- Jarník's method "was formulated quite clearly over a quarter century before" Prim, Kruskal and Dijkstra; Jarník "viewed his work as a simplification of" Borůvka's. **Documented** ([Graham and Hell](https://math.ucdavis.edu/~saito/data/acha.read.w12/graham-hell-mst.pdf); [MacTutor, Jarník](https://mathshistory.st-andrews.ac.uk/Biographies/Jarnik/))
- Rediscoveries of Borůvka's method: Choquet (1938), Florek, Łukasiewicz, Perkal, Steinhaus and Zubrzycki (1951), and Sollin. **Documented** ([Wikipedia, Borůvka's algorithm](https://en.wikipedia.org/wiki/Bor%C5%AFvka%27s_algorithm); [Graham and Hell](https://math.ucdavis.edu/~saito/data/acha.read.w12/graham-hell-mst.pdf))
- Sollin's date: 1961, as an unpublished manuscript presented at Berge's seminar in Paris (Graham and Hell), or 1965 (Wikipedia). **Disputed** (the opened sources differ)
- Kruskal (1956): "Sort the edges by weight; examine each edge in the order of increasing weight"; Prim (1957) chose Jarník's growth rule because it "never requires access to more than two rows of distance data at a time". **Documented** ([Graham and Hell](https://math.ucdavis.edu/~saito/data/acha.read.w12/graham-hell-mst.pdf))
- Borůvka's method needs O(log V) rounds and runs in time O(E log V); with equal weights "a consistent tie-breaking rule must be used", or the chosen edges can form a cycle. **Documented** ([Wikipedia, Borůvka's algorithm](https://en.wikipedia.org/wiki/Bor%C5%AFvka%27s_algorithm))
- A Polish anthropologist, Czekanowski (1909), is cited as a precursor through work on clustering. **Documented** as a claim in [CS/ECE 374 lecture slides, Illinois (2020)](https://courses.grainger.illinois.edu/cs374/fa2020/lec_prerec/20/20_1_0_0.pdf); whether his method is a spanning-tree algorithm was not checked here, so its priority is **conjecture**

**Watch**

No video could be verified (see **Gaps**).

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Algorithms for Minimum Spanning Trees](https://courses.grainger.illinois.edu/cs374/fa2020/lec_prerec/20/20_1_0_0.pdf) | CS/ECE 374, University of Illinois (Fall 2020), lecture 20 slides | Borůvka's electricity network and the history before Kruskal and Prim |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Borůvka's algorithm](https://en.wikipedia.org/wiki/Bor%C5%AFvka%27s_algorithm) | Wikipedia | The rounds, the rediscoveries, and why ties must be broken consistently |
| Start | [Otakar Borůvka](https://mathshistory.st-andrews.ac.uk/Biographies/Boruvka/) | MacTutor | Borůvka's life in Brno and the friend at the power company |
| Start | [Vojtěch Jarník](https://mathshistory.st-andrews.ac.uk/Biographies/Jarnik/) | MacTutor | A number theorist's single, lasting excursion into networks |
| Scholar | [On the History of the Minimum Spanning Tree Problem](https://math.ucdavis.edu/~saito/data/acha.read.w12/graham-hell-mst.pdf) | R. L. Graham and Pavol Hell, *Annals of the History of Computing* 7(1) (1985), on a UC Davis reading list | The standard history: Borůvka, Jarník, Choquet, Florek et al., Kruskal, Prim, Sollin |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Otakar Borůvka on minimum spanning tree problem: translation of both the 1926 papers, comments, history](https://www.dml.cz/bitstream/handle/10338.dmlcz/500413/Boruvka_03-0000-60_1.pdf) | J. Nešetřil, E. Milková and H. Nešetřilová, *Discrete Mathematics* 233:3–36 (2001), Czech Digital Mathematics Library | Both of Borůvka's papers in English, including the 40-city example |
| Scholar | [Vojtěch Jarník's work in combinatorial optimization](https://www.dml.cz/bitstream/handle/10338.dmlcz/500662/Jarnik_04-0000-19_1.pdf) | B. Korte and J. Nešetřil, *Discrete Mathematics* 235:1–17 (2001), Czech Digital Mathematics Library | Jarník's letter of 1930, in Czech and in English translation |

**Gaps:** no video page could be opened. The Czech originals of 1926 and 1930 were read only through the translations above. Kruskal's (1956) and Prim's (1957) papers were not opened; their methods are quoted through Graham and Hell. Borůvka's 40 city coordinates are not reproduced; the topic's program uses its own points.

## 5. Gödel's numbering

**When / where:** Kurt Gödel, aged 24, announced his first incompleteness theorem at a conference in Königsberg in September 1930; the paper, "Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I", was submitted on 17 November 1930 and published in *Monatshefte für Mathematik und Physik* 38 (1931), 173–198.
**Atlas:** to be mapped · **Code:** [`GodelNumbering.java`](../../code/era-04-what-can-be-computed/05-godel-numbering/) · **Page:** [topic 5](05-godel-numbering/README.md)

> **Field note.** Hilbert wanted mathematics written as a game of symbols, with rules so exact that a machine could check every proof, and then a proof that the game could never produce a contradiction. A young logician took the first half at its word. He gave every symbol a number, every formula a number built from those (a product of prime powers), every proof a number built from those, and showed that "this number is a proof of that formula" is a question of ordinary arithmetic. Then arithmetic could talk about its own proofs, and he wrote down a formula that says, in effect, "I am not provable". If the system is consistent, that formula is true and cannot be proved. Programs are numbers: I date the idea from this paper.

**What hurt:** Hilbert's program needed a precise description of what a proof is, and a guarantee that every arithmetical statement could be settled by one.
**The step forward:** arithmetization: code formulas and proofs as numbers so that checking a proof becomes a computation on numbers, defined by "primitive recursive" recipes. The coding lets a formula refer to itself, which yields a true but unprovable statement in any consistent system strong enough for basic arithmetic.

**Evidence and certainty**

- Gödel (28 April 1906 – 14 January 1978), born in Brünn (now Brno); Hilbert's formalism "was dealt a severe blow by Gödel's results". **Documented** ([MacTutor, Gödel](https://mathshistory.st-andrews.ac.uk/Biographies/Godel/))
- The paper: submitted 17 November 1930; *Monatshefte für Mathematik und Physik* 38 (1931), 173–198; it contains 45 explicit definitions of primitive recursive functions and relations; the promised part II was never published. **Documented** ([Wikipedia, On Formally Undecidable Propositions](https://en.wikipedia.org/wiki/On_Formally_Undecidable_Propositions_of_Principia_Mathematica_and_Related_Systems))
- The announcement at Königsberg (September 1930) "drew little attention apart from that of von Neumann", who later proved the second theorem independently and wrote to Gödel on 20 November 1930; Gödel had already found it. **Documented** ([Wikipedia, Gödel's incompleteness theorems](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems); [Zach, "Hilbert's Program Then and Now"](https://arxiv.org/pdf/math/0508572))
- The two theorems: any consistent formal system that can do basic arithmetic has statements it can neither prove nor disprove; and such a system cannot prove its own consistency. **Documented** ([Wikipedia, Gödel's incompleteness theorems](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems))
- Gödel's sign numbers: "0" … 1, "f" (successor) … 3, "~" … 5, "∨" … 7, "Π" … 9, "(" … 11, ")" … 13; variables get primes above 13 and their powers; a sequence of signs n1, n2, …, nk becomes 2^n1 · 3^n2 · … · pk^nk. **Documented** ([Meltzer's translation, p. [179]](https://gtts.ehu.es/German/Docencia/2021/MTBYC/pdf/Godel.pdf); [Hirzel's translation](https://www.hirzels.com/martin/papers/canon00-goedel.pdf); [Wikipedia, Gödel numbering](https://en.wikipedia.org/wiki/G%C3%B6del_numbering))
- The coding is reversible because every number "can be uniquely factored into prime factors"; Gödel used it twice: formulas as sequences of signs, proofs as sequences of formulas. **Documented** ([Wikipedia, Gödel numbering](https://en.wikipedia.org/wiki/G%C3%B6del_numbering))
- The effect on Hilbert's program: the theorems "showed that Hilbert's optimism was unfounded", and finitary consistency proofs for the theories Hilbert had in mind are ruled out; work continued, for example in Gentzen's consistency proof. Some mathematicians dispute how much of the program was refuted. **Documented**, with the extent **disputed** ([Zach](https://arxiv.org/pdf/math/0508572); [Wikipedia, Gödel's incompleteness theorems](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems))
- Kleene later derived the first theorem from computability: a complete, consistent, effective system of arithmetic would make the halting problem (topic 7) decidable. **Documented** ([Wikipedia, Gödel's incompleteness theorems](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems))
- Reading the coding of formulas as numbers as the ancestor of programs stored as data (topics 7 and 9) is this catalog's interpretation. **Conjecture**

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Gödel's incompleteness theorems](https://en.wikipedia.org/wiki/G%C3%B6del%27s_incompleteness_theorems) | Wikipedia | The two theorems, the Königsberg announcement, and the link to the halting problem |
| Start | [Gödel numbering](https://en.wikipedia.org/wiki/G%C3%B6del_numbering) | Wikipedia | The sign table and the prime-power code, with modern variants |
| Start | [Kurt Gödel](https://mathshistory.st-andrews.ac.uk/Biographies/Godel/) | MacTutor | Gödel's life and the reception of his results |
| Deeper | [On Formally Undecidable Propositions of Principia Mathematica and Related Systems](https://en.wikipedia.org/wiki/On_Formally_Undecidable_Propositions_of_Principia_Mathematica_and_Related_Systems) | Wikipedia | The paper itself: dates, structure, the 45 primitive recursive definitions, translations |
| Scholar | [Hilbert's Program Then and Now](https://arxiv.org/pdf/math/0508572) | Richard Zach, arXiv math/0508572 | What Hilbert wanted, what Gödel showed, and what survived |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [On Formally Undecidable Propositions of Principia Mathematica and Related Systems](https://gtts.ehu.es/German/Docencia/2021/MTBYC/pdf/Godel.pdf) | Gödel (1931), translated by B. Meltzer with an introduction by R. B. Braithwaite (1962), on a University of the Basque Country course page | The whole paper in English, with the original page numbers |
| Scholar | [On formally undecidable propositions … (sections 1 and 2)](https://www.hirzels.com/martin/papers/canon00-goedel.pdf) | Gödel (1931), translated by Martin Hirzel (27 November 2000) | A free modern translation of the sign table, the primitive recursive functions and the main argument |

**Gaps:** no video page could be opened. The German original and the Stanford Encyclopedia of Philosophy entry could not be opened (the permission request was withdrawn). Gödel's list of 45 definitions is described, not reproduced; the topic's program decodes his numbers by factoring instead.

## 6. Church's lambda calculus

**When / where:** Alonzo Church and his students Stephen Kleene and J. Barkley Rosser, Princeton, early 1930s. Church presented "An Unsolvable Problem of Elementary Number Theory" to the American Mathematical Society on 19 April 1935 (*American Journal of Mathematics* 58, 345–363, April 1936); "A Note on the Entscheidungsproblem" followed in the first volume of *The Journal of Symbolic Logic* (1936).
**Atlas:** to be mapped · **Code:** [`LambdaCalculus.java`](../../code/era-04-what-can-be-computed/06-lambda-calculus/) · **Page:** [topic 6](06-lambda-calculus/README.md)

> **Field note.** Church set out to rebuild logic on a single operation: apply a function to an argument. A function is written λx. followed by what it does with x, and the only rule of computation is substitution: (λx.M) applied to N becomes M with N put in place of x. His logic turned out to be inconsistent, but the part about functions survived, and it was startlingly strong. Numbers can be written as functions (the number 3 is "apply f three times"), and so can addition, multiplication and every calculation his students tried. Church proposed that "effectively calculable" should simply mean "definable in this way", and then proved that one question about it, whether a formula ever finishes simplifying, has no effective answer. Every functional programming language I have read descends from this.

**What hurt:** "a process ... in a finite number of operations" (Hilbert) had no mathematical definition, so nobody could prove that no process exists for a given problem.
**The step forward:** a precise candidate for "effectively calculable": λ-definable (equivalently, as Kleene showed, recursive). With a definition in hand, Church proved specific problems unsolvable, including Hilbert's Entscheidungsproblem for first-order logic.

**Evidence and certainty**

- Church (14 June 1903 – 11 August 1995) created the λ-calculus in the 1930s, published as *The Calculi of Lambda-Conversion* (1941); Turing came to Princeton in 1936 and completed his PhD under Church; Rosser and Kleene were Church's students. **Documented** ([MacTutor, Church](https://mathshistory.st-andrews.ac.uk/Biographies/Church/))
- The original system was "logically inconsistent in 1935" (the Kleene–Rosser paradox); Church published the part relevant to computation, the untyped λ-calculus, in 1936, and the simply typed λ-calculus in 1940. **Documented** ([Wikipedia, Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus))
- Church's numerals: "each positive integer in Arabic notation standing for a formula of the form λab.a(a(...a(b)...))"; today's version starts from 0 := λf.λx.x, with SUCC, PLUS and MULT as λ-terms. **Documented** ([Church 1936](https://courses.fit.cvut.cz/NI-VYC/church-an-unsolvable-problem-of-elementary-number-theory.pdf); [Wikipedia, Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus))
- The proposal: "a function of positive integers shall be called effectively calculable if it is recursive"; the definition of recursiveness "is due jointly to Jacques Herbrand and Kurt Gödel", and "the proof of equivalence of the two notions [recursive and λ-definable] is due chiefly to Kleene". **Documented** ([Church 1936](https://courses.fit.cvut.cz/NI-VYC/church-an-unsolvable-problem-of-elementary-number-theory.pdf))
- Theorem XVIII: "There is no recursive function of a formula C, whose value is 2 or 1 according as C has a normal form or not." **Documented** ([Church 1936](https://courses.fit.cvut.cz/NI-VYC/church-an-unsolvable-problem-of-elementary-number-theory.pdf))
- "The general case of the Entscheidungsproblem of the engere Funktionenkalkül [first-order logic] is unsolvable"; received 15 April 1936. **Documented** ([Church, *J. Symbolic Logic* 1 (1936), 40–41](https://people.csail.mit.edu/brooks/idocs/church_ent.pdf)); propositional logic, by contrast, has a truth-table decision procedure ([MacTutor, Church](https://mathshistory.st-andrews.ac.uk/Biographies/Church/))
- Ω = (λx.x x)(λx.x x) is "the smallest term that has no normal form"; the fixed-point combinator Y lets recursive functions be written without naming themselves. **Documented** ([Wikipedia, Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus))
- Combinatory logic, the same idea without variables, came first: Moses Schönfinkel's talk at Göttingen in December 1920. **Documented** ([Hindley, workshop abstract, Heriot-Watt 2000](https://www.macs.hw.ac.uk/~fairouz/forest/events/history/birth-lambda.html))
- Whether "effectively calculable" means exactly "λ-definable" cannot be proved, only supported; the thesis "is probably true but cannot be rigorously proved" (Folina, quoted by MacTutor). **Disputed** in the sense that it is a definition offered as a thesis, not a theorem ([MacTutor, Church](https://mathshistory.st-andrews.ac.uk/Biographies/Church/))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus) | Wikipedia | Terms, β-reduction, Church numerals, Ω and Y, and the history |
| Start | [Alonzo Church](https://mathshistory.st-andrews.ac.uk/Biographies/Church/) | MacTutor | Church's life, his thesis, his theorem, and his students |
| Deeper | [Birth of lambda-calculus and combinatory logic](https://www.macs.hw.ac.uk/~fairouz/forest/events/history/birth-lambda.html) | Roger Hindley, talk abstract, Workshop on History of Logics, Types and Rewriting, Heriot-Watt University (5 December 2000) | Schönfinkel's combinators of 1920, before the λ-calculus |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [An Unsolvable Problem of Elementary Number Theory](https://courses.fit.cvut.cz/NI-VYC/church-an-unsolvable-problem-of-elementary-number-theory.pdf) | Alonzo Church, *American Journal of Mathematics* 58(2):345–363 (1936), scan on a Czech Technical University course page | The numerals, the thesis, and the first unsolvable problem |
| Scholar | [A Note on the Entscheidungsproblem](https://people.csail.mit.edu/brooks/idocs/church_ent.pdf) | Alonzo Church, *The Journal of Symbolic Logic* 1(1):40–41 (1936), reprint on an MIT page | Hilbert's decision problem for first-order logic, answered: no |

**Gaps:** no video page could be opened. Cardone and Hindley's history of the λ-calculus and the Stanford Encyclopedia entry on the Church–Turing thesis were not opened. Church's 1932–1933 papers on the original system were not opened; the inconsistency of 1935 is cited from Wikipedia only. The story of how Kleene found the predecessor function was not checked in any source and is not told.

## 7. Turing's machines

**When / where:** Alan Turing, Cambridge, after Max Newman's lectures of spring 1935. "On Computable Numbers, with an Application to the Entscheidungsproblem" was received by the London Mathematical Society on 28 May 1936, read on 12 November 1936, and printed in its *Proceedings* (series 2, vol. 42, 230–265) in 1937, with an appendix on Church's work added on 28 August 1936.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Church had defined computation by a calculus; Turing defined it by watching a person compute. A clerk with a pencil works on squared paper, looks at a few squares at a time, has a finite number of states of mind, and follows fixed rules. Strip that down and you get a machine: a tape of squares, a head that reads one square, writes and moves one step, and a finite table of instructions. Then two surprises. A single machine can do the work of every other, if it is handed the other's table written on its tape: the table is just data. And no machine can look at any table and decide whether that machine will run properly forever or get stuck. Hilbert's decision problem fell with it.

**What hurt:** "effective process" still had no definition that was convincing as a picture of what a human calculator can do, and Hilbert's Entscheidungsproblem needed one to be answered "no".
**The step forward:** the Turing machine, a definition of computation by a finite table acting on an unbounded tape; the universal machine, which runs any table given as data; and the proof that no general process decides whether a machine is "circle-free", from which the Entscheidungsproblem is unsolvable.

**Evidence and certainty**

- Turing (23 June 1912 – 7 June 1954) attended Newman's course on the foundations of mathematics in spring 1935, which covered Gödel's results and Hilbert's question of decidability; he finished the paper in April 1936 and revised it in August; Newman had to argue for its publication after Church's paper appeared. **Documented** ([MacTutor, Turing](https://mathshistory.st-andrews.ac.uk/Biographies/Turing/))
- Received 28 May 1936, read 12 November 1936; appendix "Added 28 August, 1936"; pages 230–265 of series 2, vol. 42. **Documented** ([Turing 1936, scan on a University of Virginia page](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf))
- Computable numbers are "the real numbers whose expressions as a decimal are calculable by finite means"; the first example machine computes "the sequence 010101..." with four m-configurations b, c, e, f. **Documented** ([Turing 1936](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf); table as transcribed at [abelard.org via verostko.com](https://verostko.com/turing/1936-paper.html))
- "It is possible to invent a single machine which can be used to compute any computable sequence." **Documented** ([Turing 1936](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf))
- Machines are written as "standard descriptions" with the letters A, C, D, L, R, N and ";", replaced by the digits 1 to 7 to give a "description number"; the first example's is 31332531173113353111731113322531111731111335317. **Documented** ([transcription at verostko.com](https://verostko.com/turing/1936-paper.html); [Wikipedia, Description number](https://en.wikipedia.org/wiki/Description_number)); the topic's program recomputes it from the table
- "There can be no general process for determining whether a given number is satisfactory or not", i.e. whether the machine it describes is circle-free. **Documented** ([Turing 1936](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf))
- Turing "did not use the terms 'halt' or 'halting'"; Kleene (1952) put it as machines that "eventually stop", and the name "halting problem" is attributed to Martin Davis (lectures 1952, book 1958). **Documented** ([Wikipedia, Halting problem](https://en.wikipedia.org/wiki/Halting_problem))
- Church's "effective calculability" is "equivalent to my 'computability'" (Turing's introduction; the appendix proves it). **Documented** ([Turing 1936](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf))
- Turing went to Princeton in 1936 to work under Church and returned to England in 1938. **Documented** ([MacTutor, Turing](https://mathshistory.st-andrews.ac.uk/Biographies/Turing/))
- How hard halting is, in numbers: Radó's busy beaver (1962); the five-state machine found by Marxen and Buntrock (1989) halts after 47,176,870 steps leaving 4,098 ones, and was proved the five-state champion only in 2024 by the online bbchallenge collective; the function is not computable. **Documented** ([Wikipedia, Busy beaver](https://en.wikipedia.org/wiki/Busy_beaver)); the topic's program runs the machine

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Turing 2018/3: "On Computable Numbers" – Turing's 1936 Paper](https://podcasts.ox.ac.uk/turing-20183-computable-numbers-turings-1936-paper) | Peter Millican, University of Oxford, series *Alan Turing on Computability and Intelligence* (video, with transcript) | A walk through the paper: the human computer, the machines and their tables |
| Deeper | [Turing 2018/4: Enumerating the Computable Numbers, and the Universal Turing Machine](https://www.podcasts.ox.ac.uk/turing-20184-enumerating-computable-numbers-and-universal-turing-machine?video=1) | Peter Millican, University of Oxford (video) | Description numbers, the universal machine and the diagonal argument |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Turing machine](https://en.wikipedia.org/wiki/Turing_machine) | Wikipedia | Tape, head, table, the universal machine, and the human "computer" Turing modelled |
| Start | [Alan Mathison Turing](https://mathshistory.st-andrews.ac.uk/Biographies/Turing/) | MacTutor | Newman's course, the paper, Princeton, and Bletchley Park |
| Start | [Halting problem](https://en.wikipedia.org/wiki/Halting_problem) | Wikipedia | The diagonal proof, and who named the problem |
| Deeper | [Description number](https://en.wikipedia.org/wiki/Description_number) | Wikipedia | How a machine becomes a number |
| Deeper | [Busy beaver](https://en.wikipedia.org/wiki/Busy_beaver) | Wikipedia | Radó's function, the five-state champion, and its proof in 2024 |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [On Computable Numbers, with an Application to the Entscheidungsproblem](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) | A. M. Turing, *Proceedings of the London Mathematical Society* (2) 42:230–265 (1936–37), scan on a University of Virginia page | The paper |
| Scholar | [On Computable Numbers (transcription)](https://verostko.com/turing/1936-paper.html) | Transcription by abelard.org, reproduced with permission of the London Mathematical Society | A searchable text with the example tables and description numbers |

**Gaps:** the scan's example tables are not legible as extracted text; the table and the description number are taken from the transcription and checked by the program. Turing's correction (1937) was not opened. The bbchallenge proof itself was not opened; the 2024 result is cited from Wikipedia.

## 8. Breaking Enigma

**When / where:** Marian Rejewski, with Jerzy Różycki and Henryk Zygalski, Polish Cipher Bureau, Warsaw, from 1932: rotor wiring reconstructed by permutation theory in December 1932, a cyclometer and card catalogue (about 1934–1937), the *bomba* (November 1938). The Polish methods were handed to the British and French near Warsaw in July 1939; Alan Turing's design for the British Bombe (1939), with Gordon Welchman's diagonal board (1940), went into service at Bletchley Park from 18 March 1940.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The German army's cipher machine scrambled every letter through three wired wheels, a reflector and a board of plug cables, and the wheels turned after every key-press: billions upon billions of settings. Three young Polish mathematicians attacked it with the theory of permutations. Operators typed each message's three-letter key twice; Rejewski noticed that the first and fourth letters, the second and fifth, the third and sixth, are linked by permutations whose cycles always come in pairs, and whose cycle lengths the plug cables cannot change. A catalogue of those lengths for every wheel setting turned a day's indicators into a short list of settings. When the procedure changed, the British, starting from the Polish gift, built machines that tested a guessed word of plain text against every wheel position and stopped only where no contradiction arose. Here, for the first time in this book, searching is done by a machine built for the purpose.

**What hurt:** a cipher machine with so many settings that no one could try them, used by an army that changed the settings every day.
**The step forward:** mathematics that ignores most of the settings: cycle lengths that do not depend on the plugboard (Rejewski's "characteristic"), catalogued by machine; then logical deduction from a guessed plaintext ("crib"), automated by the bomba and the Bombe, which reject each wheel position that leads to a contradiction.

**Evidence and certainty**

- Rejewski (16 August 1905 – 13 February 1980) joined the Cipher Bureau in Warsaw full-time on 1 September 1932, with Różycki and Zygalski; the methods were passed to the British and French in July 1939. **Documented** ([MacTutor, Rejewski](https://mathshistory.st-andrews.ac.uk/Biographies/Rejewski/))
- In December 1932 Rejewski worked out the rotor wiring using "the theory of permutations and groups", helped by German manuals and monthly keys that French intelligence (Gustave Bertrand) had obtained from Hans-Thilo Schmidt of the German Cipher Office. **Documented** ([Wikipedia, Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma))
- The doubled message key gave six-letter indicators; "The permutation cycles of the composite permutations always occur in pairs of equal length"; the plugboard changes the letters in the cycles but not their number or lengths (the "characteristic"). **Documented** ([F.L.C., "The Polish recovery of the Enigma rotor wiring", Crypto Cellar (2005)](https://www.cryptocellar.org/enigma/files/rejewski-paper.pdf); [Wikipedia, Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma); [Wikipedia, Cyclometer](https://en.wikipedia.org/wiki/Cyclometer))
- The cyclometer, designed "probably in 1934 or 1935", catalogued 6 × 17,576 = 105,456 settings; the work "was laborious and took over a year"; the reflector change of 1 November 1937 forced a new catalogue, and the procedure change of 15 September 1938 made the method "completely useless". **Documented** ([Wikipedia, Cyclometer](https://en.wikipedia.org/wiki/Cyclometer))
- The Poles, "working with engineers from the AVA Radio Manufacturing Company", built "the 'bomba' – the first cryptanalytic machine to break Enigma codes"; delivered in November 1938. **Documented** ([IEEE Milestone citation, 2014](https://ethw.org/Milestones:First_Breaking_of_Enigma_Code_by_the_Team_of_Polish_Cipher_Bureau%2C_1932-1939); [Wikipedia, Bombe](https://en.wikipedia.org/wiki/Bombe))
- The conference near Warsaw: 26 and 27 July 1939 (Wikipedia); MacTutor gives only July 1939. **Documented** (month); the exact days come from one opened source ([Wikipedia, Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma))
- "A letter could never be encrypted to itself, a consequence of the reflector"; the British Bombe used this, and Welchman's diagonal board exploited the plugboard's symmetry to cut false stops. **Documented** ([Wikipedia, Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma))
- The first British Bombe, "Victory", "was installed in 'Hut 1' at Bletchley Park on 18 March 1940"; each run tested every rotor position against a crib, and "the test would lead to a logical contradiction, ruling out that setting". **Documented** ([Wikipedia, Bombe](https://en.wikipedia.org/wiki/Bombe)); the number of Bombes built by 1945 is given inconsistently on that page (around 200), so no figure is given here
- Turing and Welchman developed the Bombe, and from late 1940 it decoded Luftwaffe messages. **Documented** ([MacTutor, Turing](https://mathshistory.st-andrews.ac.uk/Biographies/Turing/))
- The rotor wirings of the Enigma I (rotors I, II, III; reflectors A and B), with turnover letters Q, E and V. **Documented** ([Wikipedia, Enigma rotor details](https://en.wikipedia.org/wiki/Enigma_rotor_details)); the page's test vector (AAAAA to BDZGO) is marked "citation needed", and the topic's program reproduces it

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Cryptanalysis of the Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma) | Wikipedia | The machine, the doubled indicators, Rejewski's characteristic, Zygalski's sheets and the Bombe |
| Start | [Marian Adam Rejewski](https://mathshistory.st-andrews.ac.uk/Biographies/Rejewski/) | MacTutor | Rejewski's life, from Poznań to the Cipher Bureau and after |
| Start | [Milestone: First Breaking of Enigma Code by the Team of Polish Cipher Bureau, 1932–1939](https://ethw.org/Milestones:First_Breaking_of_Enigma_Code_by_the_Team_of_Polish_Cipher_Bureau%2C_1932-1939) | IEEE History Center, Engineering and Technology History Wiki (dedicated 5 August 2014) | The citation for the bomba |
| Deeper | [Cyclometer](https://en.wikipedia.org/wiki/Cyclometer) | Wikipedia | The catalogue of 105,456 characteristics and why it failed in 1937–38 |
| Deeper | [Bombe](https://en.wikipedia.org/wiki/Bombe) | Wikipedia | Cribs, menus, logical contradictions and the diagonal board |
| Deeper | [The Polish recovery of the Enigma rotor wiring](https://www.cryptocellar.org/enigma/files/rejewski-paper.pdf) | F.L.C., Crypto Cellar (March 2005) | The permutation equations step by step |
| Deeper | [Enigma rotor details](https://en.wikipedia.org/wiki/Enigma_rotor_details) | Wikipedia | The wirings used by the program |

**Gaps:** no video page could be opened. Rejewski's own accounts (for example his 1980–81 papers) were not opened; his December 1932 work is cited from Wikipedia. The Christensen article in *Mathematics Magazine* (2007) could not be read beyond its first page. Turing's own Bombe report was not opened. The topic's program uses reflector A for the Polish catalogue and reflector B elsewhere, and its catalogue is computed, not Rejewski's.

## 9. The stored program, and merge sort

**When / where:** John von Neumann's "First Draft of a Report on the EDVAC" (dated 30 June 1945, written March–April 1945) put instructions and numbers in one memory; in 1945 he also wrote, by hand, a program for merging ("meshing") two sorted sequences, analysed by Knuth in 1970. Goldstine and von Neumann treated sorting and merging "in considerable detail" in 1948. The first stored program actually to run was Tom Kilburn's, on the Manchester "Baby", on 21 June 1948.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The first electronic computers were set up for each problem by plugging cables and setting switches. The design report of 1945 proposed something else: keep the orders for the machine in the same memory as the numbers, written in the same binary digits. Then a program can be loaded like data, and, as it turned out, a program can change its own instructions, which is how the first programs stepped through a list: by adding one to the address inside an instruction. To show that such a machine was more than a calculator, the author wrote out a program for a clerical task, merging sorted files, and estimated that it would beat the punched-card sorting machines of the day. Merge sort, the result, is still how large files are sorted.

**What hurt:** machines that had to be rewired for every new problem, and sorting, the commonest commercial task, done by punched-card machines one digit at a time.
**The step forward:** the stored program: instructions held in memory as numbers, so they can be loaded, changed and computed on like any data. Its first showcase was merging: two sorted lists combined by repeatedly moving the smaller front item to the output. Applied to runs of length 1, 2, 4, …, it sorts n items in about n log₂ n comparisons.

**Evidence and certainty**

- The report is dated 30 June 1945 and was distributed by Herman Goldstine; it describes "a uniform memory containing both numbers (data) and orders (instructions)"; naming the design after von Neumann is "controversial due to von Neumann's failure to name the designers of the architecture, John Mauchly and J. Presper Eckert", and the report counted as a public disclosure that made the EDVAC patent unenforceable. **Documented** ([Wikipedia, First Draft of a Report on the EDVAC](https://en.wikipedia.org/wiki/First_Draft_of_a_Report_on_the_EDVAC)); who deserves the credit is **disputed**
- The report divides the machine into five parts, CA (central arithmetic), CC (central control), M (memory), I (input) and O (output). **Documented** ([the report, reprinted in Laplante, *Great Papers in Computer Science*, on a Carleton College page](https://cs.carleton.edu/faculty/jondich/courses/cs207_f03/assignments/edvac.pdf))
- Knuth calls von Neumann's handwritten merging program "probably the earliest extant program for a stored program digital computer"; its aim: "We wish to formulate code instructions for sorting and for meshing"; the planned EDVAC "is definitely faster than" the IBM sorters of about 400 cards a minute. **Documented** ([Knuth, *Computing Surveys* 2(4):247–260 (1970), on Fermat's Library](https://fermatslibrary.com/s/von-neumanns-first-computer-program))
- Von Neumann's letter of 8 May 1945 to Goldstine: "I have also worked on sorting questions"; the program had to insert record sizes into instruction words because "the machine could only store into the address field of instruction words". **Documented** ([Knuth 1970](https://fermatslibrary.com/s/von-neumanns-first-computer-program))
- Merge sort "was invented by John von Neumann in 1945"; a bottom-up description and analysis "appeared in a report by Goldstine and von Neumann as early as 1948"; its worst case is about n⌈lg n⌉ − 2^⌈lg n⌉ + 1 comparisons. **Documented** ([Wikipedia, Merge sort](https://en.wikipedia.org/wiki/Merge_sort)); the topic's program checks the worst case exhaustively for small n
- The Baby "ran its first program on 21 June 1948": Kilburn's 17 instructions searched for the highest proper factor of 2^18 by repeated subtraction, in 52 minutes and about 3.5 million operations, on 32 words of 32 bits held on a Williams tube; its instruction set has seven functions (JMP, JRP, LDN, STO, SUB, CMP, STP). **Documented** ([Wikipedia, Manchester Baby](https://en.wikipedia.org/wiki/Manchester_Baby))
- Turing's universal machine (topic 7) already treated a machine's table as data on its tape; whether the EDVAC report drew on Turing's paper is not settled in the opened sources. **Conjecture**

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [First Draft of a Report on the EDVAC](https://en.wikipedia.org/wiki/First_Draft_of_a_Report_on_the_EDVAC) | Wikipedia | The stored-program design, its distribution, and the dispute over credit |
| Start | [Manchester Baby](https://en.wikipedia.org/wiki/Manchester_Baby) | Wikipedia | The first stored program to run, and the seven instructions it used |
| Start | [Merge sort](https://en.wikipedia.org/wiki/Merge_sort) | Wikipedia | The algorithm, its analysis and its variants |
| Scholar | [Von Neumann's First Computer Program](https://fermatslibrary.com/s/von-neumanns-first-computer-program) | Donald E. Knuth, *Computing Surveys* 2(4):247–260 (December 1970), annotated on Fermat's Library | The 1945 merging program, read line by line |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [First Draft of a Report on the EDVAC](https://cs.carleton.edu/faculty/jondich/courses/cs207_f03/assignments/edvac.pdf) | John von Neumann (30 June 1945), reprinted from Laplante (ed.), *Great Papers in Computer Science*, on a Carleton College course page | The five organs, and orders stored as numbers |

**Gaps:** no video page could be opened. Von Neumann's manuscript and the 1948 *Planning and Coding of Problems* reports were not opened; they are described through Knuth. Kilburn's own program listing was not opened: the topic's program runs a program of its own, written for the Baby's seven instructions, so its instruction count is not the historical one.

## 10. Monte Carlo, and numbers that only look random

**When / where:** Stanisław Ulam, John von Neumann and Nicholas Metropolis, Los Alamos, 1946–1949. Ulam's idea came in 1946; von Neumann outlined a statistical calculation of neutron diffusion in a letter to Robert Richtmyer of 11 March 1947; the first fully automated Monte Carlo calculations ran on the ENIAC in spring 1948; Metropolis and Ulam published "The Monte Carlo Method" in the *Journal of the American Statistical Association* in 1949. Von Neumann's middle-square method for producing random-looking digits was described in 1949 and printed in 1951.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** A mathematician recovering from an illness played patience and asked what fraction of games can be won. The combinatorics were hopeless; he realised it would be easier to deal a few hundred games and count. That is a strange idea for a mathematician, since the answer is only approximate, but the new electronic computers could deal millions of games, and the questions at Los Alamos (how many neutrons in a chain go on to cause fission?) were as hopeless as patience. The method needs random numbers by the million, and reading them from cards was too slow, so von Neumann had the machine make its own: square a number and keep its middle digits. He knew perfectly well that such numbers are not random. He called using them a sin, and used them.

**What hurt:** problems with too many interacting chances to calculate exactly, from patience to neutron chains, and sampling by hand that had been abandoned as too tedious.
**The step forward:** simulate many random cases on a computer and count: the error falls like 1/√N whatever the number of dimensions. And a deterministic recipe for numbers that pass for random, so the machine need not read them from cards.

**Evidence and certainty**

- Ulam (1983): the method was "suggested by a question which occurred to me in 1946 as I was convalescing from an illness and playing solitaires"; von Neumann wrote to Richtmyer in March 1947 that "the statistical approach is very well suited to a digital treatment". **Documented** ([Eckhardt, *Los Alamos Science*, Special Issue 1987](https://mcnp-green.lanl.gov/pdf_files/Article_1987_LAS_Eckhardt_131--141.pdf))
- Metropolis places "the spark that led to the Monte Carlo method" at the spring 1946 Los Alamos review of the ENIAC's results, when Ulam saw that statistical sampling, abandoned for its tedium, could be revived; the letter to Richtmyer is dated 11 March 1947. **Documented** ([Metropolis, *Los Alamos Science*, Special Issue 1987, 125–130](https://mcnpx.lanl.gov/pdf_files/Article_1987_LAS_Metropolis_125--130.pdf)); the two accounts stress different moments, and neither excludes the other
- The name: Metropolis "suggested an obvious name", after Ulam's uncle, who borrowed money from relatives because he "just had to go to Monte Carlo"; the work was secret and needed a code name. **Documented** ([Metropolis 1987](https://mcnpx.lanl.gov/pdf_files/Article_1987_LAS_Metropolis_125--130.pdf); [Wikipedia, Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method))
- Fermi had experimented with the method in the 1930s while studying neutron diffusion, without publishing; von Neumann, Metropolis and others "programmed the ENIAC computer to perform the first fully automated Monte Carlo calculations", of a fission weapon core, in spring 1948. **Documented** ([Wikipedia, Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method))
- Metropolis and Ulam, "The Monte Carlo Method", *Journal of the American Statistical Association* 44: 335–341 (1949). **Documented** ([Metropolis 1987](https://mcnpx.lanl.gov/pdf_files/Article_1987_LAS_Metropolis_125--130.pdf))
- "Quadrupling the number of sampled points halves the error, regardless of the number of dimensions." **Documented** ([Wikipedia, Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method))
- Middle-square: square an n-digit number and take the middle n digits; "Anyone who considers arithmetical methods of producing random digits is, of course, in a state of sin" (von Neumann, "Various techniques used in connection with random digits", 1951); he found such methods "hundreds of times faster than reading 'truly' random numbers off punch cards". **Documented** ([Wikipedia, Middle-square method](https://en.wikipedia.org/wiki/Middle-square_method))
- Its flaws: periods "usually very short"; for four digits it sticks at 0100, 2500, 3792 and 7600, and 0540 → 2916 → 5030 → 3009 repeats. **Documented** ([Wikipedia, Middle-square method](https://en.wikipedia.org/wiki/Middle-square_method)); the topic's program finds every cycle for four digits
- An earlier inventor, "a Franciscan friar known only as Brother Edvin sometime between 1240 and 1250", is reported from Ivar Ekeland's *The Broken Dice*; the manuscript is said to be lost. **Disputed** (a single secondary report of a lost source)
- Buffon's needle, an earlier way to estimate π by random throws, is "an early variant". **Documented** ([Wikipedia, Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Monte Carlo method](https://en.wikipedia.org/wiki/Monte_Carlo_method) | Wikipedia | The idea, its history at Los Alamos, and its accuracy |
| Start | [Middle-square method](https://en.wikipedia.org/wiki/Middle-square_method) | Wikipedia | Von Neumann's generator, its short cycles, and the "state of sin" |
| Deeper | [The Beginning of the Monte Carlo Method](https://mcnpx.lanl.gov/pdf_files/Article_1987_LAS_Metropolis_125--130.pdf) | N. Metropolis, *Los Alamos Science*, Special Issue 1987, 125–130 | A participant's account: ENIAC, the name, the first calculations |
| Deeper | [Ulam, von Neumann and the Monte Carlo method](https://mcnp-green.lanl.gov/pdf_files/Article_1987_LAS_Eckhardt_131--141.pdf) | Roger Eckhardt, *Los Alamos Science*, Special Issue 1987, 131–141 (the extracted title reads "Monte Carlo and the Monte Carlo Method") | Ulam's solitaire question and von Neumann's letter of 1947, quoted |

**Gaps:** no video page could be opened. The 1949 paper of Metropolis and Ulam and von Neumann's 1951 note were not opened; they are cited through the articles above. The Brother Edvin story rests on one book, which was not opened.

## 11. The simplex method

**When / where:** George Dantzig, mathematical adviser to the comptroller of the U.S. Air Force, the Pentagon, 1947. In the fall of 1947 he visited von Neumann in Princeton and had the National Bureau of Standards test the method on Stigler's diet problem; the method was presented at symposia in 1948 and 1951. Leonid Kantorovich (late 1930s) and Tjalling Koopmans had formulated similar problems independently.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** After the war the American Air Force wanted its plans (how many people, aircraft and supplies, where and when) worked out by machine. Dantzig wrote the rules of such plans as linear inequalities, and the goal as a linear quantity to maximize. The possible plans form a many-sided solid, and the best plan sits at one of its corners; but the corners are uncountably many in human terms (Dantzig liked to point out that assigning 70 people to 70 jobs has more arrangements than the universe has particles). His method walks from corner to neighbouring corner, always uphill, and stops when no neighbour is better. Nobody could explain why it needed so few steps; for twenty-five years it simply did. Then someone built a solid on which it visits every corner.

**What hurt:** planning problems with hundreds of interacting limits (budgets, capacities, requirements) and astronomically many feasible plans, solved by rules of thumb.
**The step forward:** linear programming: write the plan as a linear objective with linear constraints, and the simplex method, which pivots from one corner (a basic feasible solution) of the feasible region to a better neighbour until none is better.

**Evidence and certainty**

- Dantzig (8 November 1914 – 13 May 2005) completed his PhD at Berkeley in 1946 and became mathematical adviser to the comptroller of the newly created U.S. Air Force; "in 1947, in this role, the linear programming problem and the simplex method took shape". **Documented** ([Cottle, NAS Biographical Memoir (2024)](https://www.nasonline.org/wp-content/uploads/2024/06/dantzig-george-b.pdf))
- In 1946 a colleague challenged Dantzig "to mechanize the planning process"; he added an objective function in mid-1947. **Documented** ([Wikipedia, Simplex algorithm](https://en.wikipedia.org/wiki/Simplex_algorithm))
- Dantzig's own account: efficiency became apparent from "viewing the problem in the geometry of the columns rather than the rows"; in the fall of 1947 he went to Princeton to "visit the great mathematician Johnny von Neumann"; he arranged for the Bureau of Standards to test the method on "George Stiegler's nutrition problem" [sic]. **Documented** ([Dantzig, "Origins of the Simplex Method", Stanford SOL 87-5 (May 1987)](https://apps.dtic.mil/sti/pdfs/ADA182708.pdf))
- Von Neumann "immediately conjectured the theory of duality", seeing that a problem from his game theory was equivalent to Dantzig's. **Documented** ([Wikipedia, Linear programming](https://en.wikipedia.org/wiki/Linear_programming))
- Precursors: Fourier (1827) on systems of linear inequalities; Kantorovich in the late 1930s on manufacturing schedules; Koopmans "formulated classical economic problems as linear programs"; Kantorovich and Koopmans shared the 1975 Nobel Memorial Prize in Economic Sciences. **Documented** ([Wikipedia, Linear programming](https://en.wikipedia.org/wiki/Linear_programming))
- The 70-by-70 assignment: more configurations "than the number of particles in the observable universe". **Documented** as Dantzig's example ([Wikipedia, Linear programming](https://en.wikipedia.org/wiki/Linear_programming)); the topic's program computes 70!
- Stigler's diet problem: 77 foods, nine nutrients; Stigler's own diet cost $39.93 a year in 1939 prices; the exact minimum is $39.69. **Documented** ([Wikipedia, Stigler diet](https://en.wikipedia.org/wiki/Stigler_diet)); who carried out the 1947 calculation, and with what labour, was not found in an opened source
- The name "simplex" was suggested by T. S. Motzkin; the method is "remarkably efficient in practice", but the Klee–Minty cube (1972) shows its worst case is exponential; Bland's rule prevents cycling. **Documented** ([Wikipedia, Simplex algorithm](https://en.wikipedia.org/wiki/Simplex_algorithm)); the topic's program runs the Klee–Minty cubes
- Polynomial-time methods came later: Khachiyan (1979) and Karmarkar's interior-point method (1984). **Documented** ([Wikipedia, Linear programming](https://en.wikipedia.org/wiki/Linear_programming))

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Simplex algorithm](https://en.wikipedia.org/wiki/Simplex_algorithm) | Wikipedia | Pivoting, the name, cycling and the Klee–Minty worst case |
| Start | [Linear programming](https://en.wikipedia.org/wiki/Linear_programming) | Wikipedia | Kantorovich, Koopmans, Dantzig and von Neumann's duality, and what came after |
| Start | [Stigler diet](https://en.wikipedia.org/wiki/Stigler_diet) | Wikipedia | The diet problem that was the method's first large test |
| Deeper | [George B. Dantzig, a Biographical Memoir](https://www.nasonline.org/wp-content/uploads/2024/06/dantzig-george-b.pdf) | Richard W. Cottle, National Academy of Sciences (2024) | Dantzig's life, from Neyman's unsolved problems to the Air Force |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Origins of the Simplex Method](https://apps.dtic.mil/sti/pdfs/ADA182708.pdf) | George B. Dantzig, Technical Report SOL 87-5, Systems Optimization Laboratory, Stanford University (May 1987), via DTIC | Dantzig's own account of 1947: the Pentagon, von Neumann, column geometry and the diet problem |

**Gaps:** no video page could be opened. Dantzig's 1951 paper in the Cowles Commission volume and Kantorovich's 1939 monograph were not opened. Stigler's 1945 data are not reproduced; the topic's program checks the method on its own problems.

## 12. Shannon: switches, bits and entropy

**When / where:** Claude Shannon. At MIT in 1937 he wrote the master's thesis "A Symbolic Analysis of Relay and Switching Circuits" (published in the *Transactions of the American Institute of Electrical Engineers*, 1938; degree 1940). At Bell Telephone Laboratories he published "A Mathematical Theory of Communication" in the *Bell System Technical Journal* 27 (July and October 1948), reissued in 1949 as a book with Warren Weaver.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Boole's algebra of logic (Era 3) waited more than eighty years for a use. A student noticed that a telephone exchange's relays are Boole's variables: two switches in series conduct when both are closed (and), in parallel when either is (or). Circuit design became algebra, and algebra can simplify a circuit before anyone builds it. Eleven years later the same man asked what a message is. Not its meaning: its surprise. He measured it in binary digits, "bits", proved that a source's average surprise (its entropy) is the least number of bits per symbol any code can achieve, and showed that a noisy line can carry messages almost without error at any rate below its capacity. To make English concrete he generated imitations of it from Markov's letter statistics (topic 3). Every message I have intercepted on this planet since is coded by his rules.

**What hurt:** relay circuits designed by trial and error; and no measure of information, so no way to know how far a code could be shortened or how fast a noisy line could be used.
**The step forward:** switching algebra (Boolean algebra applied to circuits), and information theory: entropy H = −Σ p log₂ p bits per symbol as the limit of compression, and channel capacity as the limit of reliable transmission.

**Evidence and certainty**

- Shannon (30 April 1916 – 24 February 2001): Michigan degree 1936; MIT master's in electrical engineering and PhD in mathematics, 1940; Bell Laboratories 1941–1972; the master's thesis used Boole's algebra to analyse and optimise relay switching circuits. **Documented** ([MacTutor, Shannon](https://mathshistory.st-andrews.ac.uk/Biographies/Shannon/))
- The thesis was written at MIT in 1937 and published in 1938 in the *Transactions of the AIEE*; Howard Gardner called it "possibly the most important, and also the most famous, master's thesis of the century". **Documented** ([Wikipedia, A Symbolic Analysis of Relay and Switching Circuits](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits)); MIT's catalogue dates the thesis 1940, the year of the degree ([DSpace@MIT](https://dspace.mit.edu/handle/1721.1/11173))
- "A Mathematical Theory of Communication", *Bell System Technical Journal* 27: 379–423 and 623–656 (July and October 1948); renamed *The Mathematical Theory of Communication* in the 1949 book, with an article by Warren Weaver; "the founding work of the field of information theory". **Documented** ([Wikipedia, A Mathematical Theory of Communication](https://en.wikipedia.org/wiki/A_Mathematical_Theory_of_Communication))
- Base-2 units "may be called binary digits, or more briefly bits, a word suggested by J. W. Tukey"; Theorem 2: the only measure meeting his three conditions is H = −K Σ pᵢ log pᵢ, "the entropy of the set of probabilities". **Documented** ([Shannon 1948, reprint on an MIT page](https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf)); MacTutor says the paper introduced the word "bit" in print ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Shannon/))
- The approximations to English, from random letters through letter-pair and word-pair statistics; such sources "are known mathematically as discrete Markoff processes"; the redundancy of ordinary English is roughly 50 per cent, judged over about eight letters. **Documented** ([Shannon 1948](https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf))
- The noisy-channel coding theorem (Theorems 11 and 12): below the channel capacity C, messages can be sent with arbitrarily small frequency of errors. **Documented** ([Shannon 1948](https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf)); MacTutor: the paper showed that adding extra bits allows transmission errors to be corrected, the theme of topic 13
- Scientific American called the paper the "Magna Carta of the Information Age". **Documented** as quoted in [Wikipedia, A Mathematical Theory of Communication](https://en.wikipedia.org/wiki/A_Mathematical_Theory_of_Communication)

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Claude Elwood Shannon](https://mathshistory.st-andrews.ac.uk/Biographies/Shannon/) | MacTutor | Shannon's life, the thesis and the 1948 paper |
| Start | [A Symbolic Analysis of Relay and Switching Circuits](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits) | Wikipedia | Boole's algebra put to work in telephone exchanges |
| Start | [A Mathematical Theory of Communication](https://en.wikipedia.org/wiki/A_Mathematical_Theory_of_Communication) | Wikipedia | The paper, the book, and its reception |
| Start | [Andrey Markov & Claude Shannon Counted Letters to Build the First Language-Generation Models](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models) | Oscar Schwartz, IEEE Spectrum (11 November 2019) | How Shannon's imitations of English grew out of Markov's counts |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Mathematical Theory of Communication](https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf) | C. E. Shannon, *Bell System Technical Journal* 27 (1948), reprint on an MIT course page | Bits, entropy, the approximations to English, and channel capacity |
| Scholar | [A symbolic analysis of relay and switching circuits](https://dspace.mit.edu/handle/1721.1/11173) | Claude Elwood Shannon, M.S. thesis, MIT Department of Electrical Engineering (catalogued 1940), DSpace@MIT | The thesis, with a scan of the original |

**Gaps:** no video page could be opened. The 1948 reprint's text breaks off before the continuous-channel results, so the capacity formula for a band-limited channel is not quoted. The thesis scan was not opened beyond its catalogue record. Shannon's "Prediction and Entropy of Printed English" (1951) was not opened. The topic's program measures its own letter statistics on a sample of this book's text, not on the English corpus Shannon used.

## 13. Hamming's codes

**When / where:** Richard Hamming, Bell Telephone Laboratories, from 1947: frustrated by a relay computer that abandoned his weekend jobs whenever it detected an error, he devised codes that locate and correct errors. "Error Detecting and Error Correcting Codes", *Bell System Technical Journal* 29(2): 147–160 (April 1950).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The relay computers at Bell Labs checked their own work: if a parity check failed, they stopped. During the week an operator restarted the job; at weekends the machine simply dropped it and went on to the next. A mathematician who came back on Mondays to find his work abandoned asked the obvious question: if the machine can tell that something is wrong, why can't it tell where, and put it right? His answer adds a few check digits, each the parity of a chosen set of positions, arranged so that the pattern of failed checks spells out, in binary, the position of the error. Seven digits carry four of information and survive any single error. This era began with a question about what can be computed at all; it ends with computing that can be trusted.

**What hurt:** long calculations on machines that make occasional errors: detecting an error (a parity check) meant starting again.
**The step forward:** error-correcting codes: check digits at positions 1, 2, 4, 8, … whose failed checks name the position of a single error; and the geometry behind them: if every two code words differ in at least three places, any single error can be corrected (at least four: corrected, and a double error detected).

**Evidence and certainty**

- Hamming (11 February 1915 – 7 January 1998) ran the IBM computing machines at Los Alamos from 1945 and joined the mathematics department of Bell Labs in 1946; in 1947 a weekend job ruined by an early error led him to ask why a machine that can detect an error cannot locate it and, being binary, correct it. **Documented** ([MacTutor, Hamming](https://mathshistory.st-andrews.ac.uk/Biographies/Hamming/))
- The machine was the Bell Model V, "an electromechanical, relay-based computer" fed by punched paper tape; on weekends it moved on to the next job when it detected an error. Hamming, in a taped interview: "Damn it, if the machine can detect an error, why can't it locate the position of the error and correct it?" **Documented** ([Wikipedia, Hamming code](https://en.wikipedia.org/wiki/Hamming_code))
- The paper: *Bell System Technical Journal* 29(2): 147–160, April 1950; "a large number of operations must be performed without a single error in the end result"; "The choice of the positions 1, 2, 4, 8, ... for check positions"; "a seven-position single error correcting code admits of 16 code symbols". **Documented** ([Hamming 1950, on a Yale course page](https://zoo.cs.yale.edu/classes/cs323/doc/Hamming.pdf); [Internet Archive record](https://archive.org/details/bstj29-2-147))
- Distance: "If the minimum distance between code points is at least three units", single errors can be corrected; distance 4 gives "single error correction plus double error detection". The paper calls its distance a "metric"; the name "Hamming distance" came later. **Documented** ([Hamming 1950](https://zoo.cs.yale.edu/classes/cs323/doc/Hamming.pdf)); MacTutor credits the paper with the concepts of Hamming distance and metric ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Hamming/))
- The syndrome: the positions of the failing parity checks, summed, give the position of the erroneous bit. **Documented** ([Wikipedia, Hamming code](https://en.wikipedia.org/wiki/Hamming_code))
- Turing Award 1968, "For his work on numerical methods, automatic coding systems, and error-detecting and error-correcting codes." **Documented** ([MacTutor](https://mathshistory.st-andrews.ac.uk/Biographies/Hamming/))
- Shannon's 1948 paper had already shown that added redundancy lets errors be corrected (topic 12); whether Shannon's paper described Hamming's (7,4) code before Hamming published it is not settled in the opened sources. **Conjecture**

**Watch**

No video could be verified (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Hamming code](https://en.wikipedia.org/wiki/Hamming_code) | Wikipedia | The weekend story, the (7,4) code and how the checks locate an error |
| Start | [Richard Wesley Hamming](https://mathshistory.st-andrews.ac.uk/Biographies/Hamming/) | MacTutor | Los Alamos, Bell Labs and the Turing Award |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Error Detecting and Error Correcting Codes](https://zoo.cs.yale.edu/classes/cs323/doc/Hamming.pdf) | R. W. Hamming, *Bell System Technical Journal* 29(2):147–160 (April 1950), on a Yale course page | The paper: check positions, distance, and the bounds on redundancy |
| Scholar | [BSTJ 29: 2. April 1950: Error Detecting and Error Correcting Codes](https://archive.org/details/bstj29-2-147) | Internet Archive, Bell System Technical Journal collection | A scan of the journal pages |

**Gaps:** no video page could be opened. Hamming's taped interview is quoted through Wikipedia, not from the recording. His talk "You and Your Research" (1986) was not opened.

## What the era leaves behind

- **Limits.** Hilbert asked for a process that decides (1); Gödel (5), Church (6) and Turing (7) defined computation exactly and proved that some questions have no such process. Every later "this cannot be computed" or "this cannot be done fast" argues in their style.
- **Programs are numbers.** Gödel coded formulas as numbers (5), Turing coded machines as numbers and ran them on a universal machine (7), and the stored-program computer put instructions in memory beside the data (9).
- **Chance as a tool.** Markov's dependent trials (3) become Monte Carlo simulation (10) and Shannon's entropy (12); the first random numbers made by a machine were known not to be random.
- **Search, made affordable.** A greedy rule that is provably optimal (4), a machine that rejects settings by contradiction (8), a walk from corner to corner of a solid (11), and merging instead of comparing everything with everything (9).
- **Error, measured and managed.** Runge–Kutta methods make the error of a step shrink like a high power of its size (2); Hamming's codes find and repair an error instead of starting over (13).

Era 5 picks up in the 1950s: the loop and the subroutine, compilers, sorting and searching, graphs and dynamic programming.
