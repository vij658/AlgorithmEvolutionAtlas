# Era 5 — The Programmer's Craft: from the subroutine to the "good" algorithm

*Reference catalog. Thirteen developments, from 1949 to 1965.*

> **Field note from the visiting historian.** In the fourth era the species learned what a procedure is, and built machines that keep procedures in memory as numbers. In this one they discover how hard it is to write procedures well, and invent a craft for it: routines written once and shared, languages translated by the machine itself, memory organised into lists, tables, trees and heaps, and methods that divide a problem, remember partial answers, or settle one place at a time. By the end of the era they are asking not only whether a problem can be solved, but whether it can be solved in a time that grows like a power of its size.

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

A note on videos: YouTube pages could not be opened from the environment used to build this catalog (one was refused for rate limiting, others returned errors), so the only video page listed is the museum's film record of the EDSAC reconstruction (topic 1). Several pages could not be opened because the request to open them was withdrawn; each topic's **Gaps** line lists them.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [The subroutine](#1-the-subroutine) | EDSAC 1949; the library and the book 1951; Wheeler's paper 1952 | Every program wrote the same routines again |
| 2 | [Regular expressions](#2-regular-expressions) | Kleene 1951; Rabin and Scott 1959; Thompson 1968 | No exact description of what a finite machine can recognise |
| 3 | [Huffman's codes](#3-huffmans-codes) | MIT 1951; published 1952 | Codes near the entropy, but none provably shortest |
| 4 | [Hashing](#4-hashing) | Luhn 1953; Amdahl 1954; Dumey 1956; Peterson 1957 | Finding a record took longer as the file grew |
| 5 | [Dynamic programming](#5-dynamic-programming) | Bellman at RAND, 1952–1957 | Plans made in stages multiply beyond listing |
| 6 | [Linked lists and garbage collection](#6-linked-lists-and-garbage-collection) | IPL about 1956; Lisp 1958–1960 | Fixed blocks of memory could not grow, shrink or be spliced |
| 7 | [Dijkstra's shortest paths](#7-dijkstras-shortest-paths) | Amsterdam 1956; published 1959 | Route-finding kept data for every road at once |
| 8 | [The compiler, and a grammar for languages](#8-the-compiler-and-a-grammar-for-languages) | FORTRAN 1954–1957; BNF 1959–1960 | Programs written instruction by instruction |
| 9 | [Rosenblatt's perceptron](#9-rosenblatts-perceptron) | 1957–1958 | Recognising patterns needed a hand-written rule for every case |
| 10 | [Hoare's Quicksort](#10-hoares-quicksort) | Moscow 1959; published 1961–1962 | Simple sorts take n^2 steps; merging needs a second memory |
| 11 | [AVL trees](#11-avl-trees) | Moscow 1962 | Search trees degenerate into lists |
| 12 | [Heapsort and the heap](#12-heapsort-and-the-heap) | Williams 1964; Floyd 1964 | Quicksort's bad cases; finding the largest of a changing set |
| 13 | [Edmonds's matching and the "good" algorithm](#13-edmondss-matching-and-the-good-algorithm) | 1961; published 1965 | No agreed meaning of "efficient"; odd cycles defeat the matching search |

## 1. The subroutine

**When / where:** EDSAC, University of Cambridge Mathematical Laboratory: the machine ran its first programs on 6 May 1949. David Wheeler, with Maurice Wilkes and Stanley Gill, devised the "closed subroutine" and the jump to it later called the Wheeler jump; Wheeler's PhD, "Automatic Computing with the EDSAC", was accepted in 1951; *The Preparation of Programs for an Electronic Digital Computer* (Wilkes, Wheeler and Gill, 1951) described a library of subroutines; Wheeler's "The use of sub-routines in programmes" was read at the ACM national meeting in Pittsburgh in 1952.
**Atlas:** to be mapped · **Code:** [`Subroutines.java`](../../code/era-05-the-programmers-craft/01-the-subroutine/) · **Page:** [topic 1](01-the-subroutine/README.md)

> **Field note.** The first stored-program computers were set to work at once, and their programmers immediately noticed that they were writing the same pieces again and again: a square root here, a sine there. The Cambridge group's answer was to write each piece once, keep it on punched tape in a library, and let any program call it. The trick is getting back: the machine had no instruction for "return to where you came from", so the caller put its own address in the accumulator and the subroutine wrote that address into the jump at its own end. With that, programs could be built from parts that other people had written and tested. This is where the craft of programming, as opposed to computing, begins.

**What hurt:** every program repeated the same pieces of code (square roots, input conversion, printing), each time written and debugged afresh, and memory was scarce.
**The step forward:** the closed subroutine: one copy of a routine, entered by a jump that passes the return address, and a library of such routines shared by every programmer, with a catalogue describing how to call each one.

**Evidence and certainty**

- EDSAC "ran its first programs on 6 May 1949, when it calculated a table of square numbers and a list of prime numbers"; it had 512 words of mercury delay-line memory at first, and "There was no unconditional jump instruction". **Documented** ([Wikipedia, EDSAC](https://en.wikipedia.org/wiki/EDSAC); [University of Cambridge, "EDSAC to be recreated" (2011)](https://www.cam.ac.uk/news/edsac-to-be-recreated))
- Wheeler (9 February 1927 – 13 December 2004) "introduced the concept of the subroutine" and "invented the subroutine (or mark place and return) 'jump,' then called the 'Wheeler jump'"; his dissertation "Automatic Computing with the EDSAC" was accepted in 1951. **Documented** ([IEEE Computer Society, Computer Pioneers: Wheeler](https://history.computer.org/pioneers/wheeler.html))
- Wheeler, Wilkes and Gill are credited with inventing the subroutine "around 1951" and called it the "closed subroutine"; Wheeler's paper "The use of sub-routines in programmes" appeared in the proceedings of the 1952 ACM national meeting in Pittsburgh. **Documented** ([Wikipedia, David Wheeler](https://en.wikipedia.org/wiki/David_Wheeler_(computer_scientist)))
- How the jump works: the caller puts its own address in the accumulator and jumps; the routine computes the return address and writes it into its own final jump; the method "is not capable of expressing recursion". **Documented** ([Wikipedia, Wheeler Jump](https://en.wikipedia.org/wiki/Wheeler_Jump))
- *The Preparation of Programs for an Electronic Digital Computer* (Addison-Wesley, 1951), "the first book on computer programming", centred on the EDSAC library of 88 subroutines kept on punched tape with a "library catalog"; the EDSAC article counts 87 subroutines available by 1951. **Documented**, with the count **disputed** between the two pages (88 or 87) ([Wikipedia, The Preparation of Programs](https://en.wikipedia.org/wiki/The_Preparation_of_Programs_for_an_Electronic_Digital_Computer); [Wikipedia, EDSAC](https://en.wikipedia.org/wiki/EDSAC))
- The book was reviewed by John Todd in the *Bulletin of the American Mathematical Society* 58 (1952), 276–278; its subtitle names "special reference to the EDSAC and the use of a library of subroutines". **Documented** ([AMS record](https://www.ams.org/journals/bull/1952-58-02/S0002-9904-1952-09610-5))
- The "initial orders", hard-wired and loaded at start-up, formed "a 31-word relocating assembler", which the EDSAC article calls "the world's first assembler"; the IEEE page credits Wheeler with them. **Documented**, attribution as given by the IEEE page ([Wikipedia, EDSAC](https://en.wikipedia.org/wiki/EDSAC); [IEEE Computer Society](https://history.computer.org/pioneers/wheeler.html))
- Wheeler is "often quoted" as saying "All problems in computer science can be solved by another level of indirection"; no original source was found. **Conjecture** as to wording and occasion ([Wikipedia, David Wheeler](https://en.wikipedia.org/wiki/David_Wheeler_(computer_scientist)))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [EDSAC Project Videos](https://www.tnmoc.org/edsac-videos) | The National Museum of Computing, films begun by David Allen (2012–2020) | The reconstruction of the machine on which the subroutine was born, filmed as it was built; "EDSAC Veterans" (2016) records a visit to it |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [David J. Wheeler](https://history.computer.org/pioneers/wheeler.html) | IEEE Computer Society, Computer Pioneers | The subroutine, the jump and the initial orders, credited to Wheeler |
| Start | [EDSAC](https://en.wikipedia.org/wiki/EDSAC) | Wikipedia | The machine, its first programs of 6 May 1949, and its subroutine library |
| Start | [Wheeler Jump](https://en.wikipedia.org/wiki/Wheeler_Jump) | Wikipedia | How a routine returned without a return instruction, and why it could not recurse |
| Start | [The Preparation of Programs for an Electronic Digital Computer](https://en.wikipedia.org/wiki/The_Preparation_of_Programs_for_an_Electronic_Digital_Computer) | Wikipedia | The first programming book and its library of subroutines |
| Deeper | [The EDSAC Simulator](https://www.dcs.warwick.ac.uk/~edsac/Home.html) | Martin Campbell-Kelly, University of Warwick | "A faithful software evocation of the EDSAC computer as it existed in 1949-51", with original programs and subroutines |
| Deeper | [EDSAC to be recreated](https://www.cam.ac.uk/news/edsac-to-be-recreated) | University of Cambridge (13 January 2011) | The replica project at The National Museum of Computing |
| Deeper | [EDSAC](https://tnmoc.org/edsac) | The National Museum of Computing | The replica at Bletchley Park; "There were only 18 operation codes" |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Review of *The Preparation of Programs for an Electronic Digital Computer*](https://www.ams.org/journals/bull/1952-58-02/S0002-9904-1952-09610-5) | John Todd, *Bulletin of the AMS* 58 (1952), 276–278 | A contemporary review of the book that published the subroutine library |

**Gaps:** the museum's video page lists titles and dates only; the films themselves were not watched for this catalog, and none is listed as being about subroutines. Wheeler's 1952 paper and the 1951 book were not opened; the mechanism of the jump is cited from Wikipedia. The topic's program uses a simplified accumulator machine of its own, not EDSAC's order code.

## 2. Regular expressions

**When / where:** Stephen Cole Kleene, for the RAND Corporation, Santa Monica: *Representation of Events in Nerve Nets and Finite Automata*, research memorandum RM-704, 15 December 1951, defines the "regular events" with three operations. Michael Rabin and Dana Scott, "Finite Automata and Their Decision Problems", *IBM Journal* (April 1959), 114–125: nondeterministic automata and the subset construction. Ken Thompson, "Regular expression search algorithm", *Communications of the ACM* 11(6): 419–422 (June 1968).
**Atlas:** to be mapped · **Code:** [`RegularExpressions.java`](../../code/era-05-the-programmers-craft/02-regular-expressions/) · **Page:** [topic 2](02-regular-expressions/README.md)

> **Field note.** Kleene took up a question about networks of idealised neurons, the kind McCulloch and Pitts had drawn: which patterns of input can such a network recognise? His answer was a small algebra. Start from single events; join two patterns with "or"; put one after another; repeat one any number of times. Everything a finite network can recognise is built from those three operations, and everything built from them can be recognised by a finite network. Kleene apologised for the name he gave the result, "regular", and asked for a better one; nobody supplied it. Eight years later Rabin and Scott let a machine be in several states at once and showed it was no stronger, only shorter to write down. Seventeen years after Kleene, Thompson turned the algebra into a program that searched text, and the notation has been in every programmer's hands since.

**What hurt:** no precise description of the patterns a machine with finite memory can recognise, and later no way to tell a program "find every line that looks like this" without writing a new program for each pattern.
**The step forward:** regular expressions: patterns built from symbols with three operations (or, then, repeat), exactly as strong as finite automata; a pattern is compiled into a machine that reads the text once, letter by letter.

**Evidence and certainty**

- RM-704, *Representation of Events in Nerve Nets and Finite Automata*, by S. C. Kleene, dated 15 December 1951, 102 pages, is listed by RAND with a free PDF. **Documented** ([RAND, RM-704](https://www.rand.org/pubs/research_memoranda/RM704.html))
- In the memorandum, section 7.1: "Our class of regular events will be defined inductively, starting with the definite events, and using three operations"; the operations are E V F (either), EF (one then the other) and E*F, "zero or more consecutive occurrences of E preceded by one of F" (Kleene's star takes two events; the one-argument star of today is a later simplification). A footnote on the name: "We would welcome any suggestions as to a more descriptive term." **Documented** ([Kleene 1951, PDF via DTIC](https://apps.dtic.mil/sti/pdfs/ADA596138.pdf))
- "Regular expressions originated in 1951, when mathematician Stephen Cole Kleene described regular languages using his mathematical notation called regular events"; Kleene "introduced it as an alternative to McCulloch & Pitts's 'prehensible'". Thompson built the notation into the editor QED, compiling patterns "just-in-time" to IBM 7094 code on the Compatible Time-Sharing System, then into the Unix editor ed, from whose command g/re/p the tool grep takes its name. **Documented** ([Wikipedia, Regular expression](https://en.wikipedia.org/wiki/Regular_expression))
- Rabin and Scott (IBM Journal, April 1959, pp. 114–125): "Finite automata are considered in this paper as instruments for classifying finite tapes"; section 5 introduces "the notion of a nondeterministic automaton", and Definition 11 builds an ordinary automaton whose states are "the set of all subsets of S". **Documented** ([Rabin and Scott 1959, on a University of Miami course page](https://www.cs.miami.edu/~burt/learning/csc427.222/docs/rabin-scott.pdf))
- The powerset (subset) construction: an NFA with n states becomes a DFA with at most 2^n states, and some languages need all of them; the standard example is the strings whose n-th symbol from the end is 1. **Documented** ([Wikipedia, Powerset construction](https://en.wikipedia.org/wiki/Powerset_construction))
- Thompson's construction turns an expression with s symbols (not counting parentheses) and c concatenations into an NFA with 2s − c states, "linear in the size of E"; the paper is "Programming Techniques: Regular expression search algorithm", *CACM* 11(6): 419–422, June 1968. Kleene's algorithm goes the other way, from an automaton to an expression. **Documented** ([Wikipedia, Thompson's construction](https://en.wikipedia.org/wiki/Thompson%27s_construction))
- grep: Lee McMahon wanted to search the Federalist Papers, about a megabyte of text, which "He couldn't edit them all in ed"; Thompson wrote grep overnight. Brian Kernighan's account, early 1970s. **Documented** as Kernighan's recollection ([The New Stack, 22 July 2018](https://thenewstack.io/brian-kernighan-remembers-the-origins-of-grep/))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Regular expression](https://en.wikipedia.org/wiki/Regular_expression) | Wikipedia | From Kleene's regular events to QED, ed and grep |
| Start | [Brian Kernighan Remembers the Origins of 'grep'](https://thenewstack.io/brian-kernighan-remembers-the-origins-of-grep/) | David Cassel, The New Stack (2018) | How grep was written in a night, in Kernighan's words |
| Deeper | [Powerset construction](https://en.wikipedia.org/wiki/Powerset_construction) | Wikipedia | Turning a machine that guesses into one that does not, and the 2^n price |
| Deeper | [Thompson's construction](https://en.wikipedia.org/wiki/Thompson%27s_construction) | Wikipedia | Pattern to machine in linear size, piece by piece |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Representation of Events in Nerve Nets and Finite Automata](https://www.rand.org/pubs/research_memoranda/RM704.html) | S. C. Kleene, RAND RM-704 (15 December 1951) | The memorandum that defines the regular events |
| Scholar | [Representation of Events in Nerve Nets and Finite Automata (PDF)](https://apps.dtic.mil/sti/pdfs/ADA596138.pdf) | Kleene 1951, scan via the Defense Technical Information Center | Section 7: the three operations and the footnote on the name |
| Scholar | [Finite Automata and Their Decision Problems](https://www.cs.miami.edu/~burt/learning/csc427.222/docs/rabin-scott.pdf) | M. O. Rabin and D. Scott, *IBM Journal* (April 1959), 114–125, on a University of Miami course page | Nondeterministic automata and the subset construction |

**Gaps:** no video page could be opened; the Computerphile interview "Where GREP Came From" (2018) is embedded in The New Stack article, but its own page was not opened. Thompson's 1968 paper was not opened; its details are cited from Wikipedia. The 1956 printing of Kleene's paper in *Automata Studies* was not opened. The OCR of the Rabin–Scott scan is imperfect, so Theorem 11 is paraphrased, not quoted.

## 3. Huffman's codes

**When / where:** David A. Huffman, a graduate student at MIT, in Robert Fano's information theory course, 1951: a term paper in place of the final exam. "A Method for the Construction of Minimum-Redundancy Codes", *Proceedings of the IRE* 40(9): 1098–1101 (1952).
**Atlas:** to be mapped · **Code:** [`HuffmanCodes.java`](../../code/era-05-the-programmers-craft/03-huffman-codes/) · **Page:** [topic 3](03-huffman-codes/README.md)

> **Field note.** Shannon had shown (Era 4, topic 12) that a message needs, on average, at least its entropy in bits per symbol, and that codes can come within one bit of it. Which code comes closest? Fano split the alphabet into two halves of nearly equal probability, then split the halves, and so on from the top; it was good but not always best. His student Huffman, offered a paper instead of an exam, nearly gave up on proving any code best, and then turned the problem upside down: take the two rarest symbols, which must have the longest codewords, join them into one, and repeat. The tree grows from the leaves to the root, and no other prefix code is shorter. Every compressed file the species exchanges still passes through some descendant of that term paper.

**What hurt:** Shannon's and Fano's codes came close to the entropy but were not always the shortest possible, and nobody could prove which code was.
**The step forward:** Huffman's procedure: repeatedly merge the two least probable symbols into one node; the tree it builds gives a prefix code with the smallest possible average length.

**Evidence and certainty**

- "In 1951, David A. Huffman and his MIT information theory classmates were given the choice of a term paper or a final exam. The professor, Robert M. Fano, assigned a term paper on the problem of finding the most efficient binary code." Huffman, "unable to prove any codes were the most efficient, was about to give up" when he found the method of a frequency-sorted binary tree. **Documented** ([Wikipedia, Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding))
- "Building the tree from the bottom up guaranteed optimality, unlike the top-down approach of Shannon–Fano coding"; "Huffman's original algorithm is optimal for a symbol-by-symbol coding with a known input probability distribution". The paper: *Proceedings of the IRE* 40(9): 1098–1101. **Documented** ([Wikipedia, Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding))
- "What Professor Fano did not tell his students was the fact that it was an open problem and that he was working on the problem himself." **Documented** as told by a classroom project in the MAA's *Convergence*, which cites Fano's 1949 report, Huffman's 1952 paper and an MIT brochure of 1975 ([MAA Convergence, "Discovery of Huffman Codes"](https://old.maa.org/node/646519))
- Huffman (9 August 1925 – 7 October 1999) published the code "while a ScD student at MIT in 1952"; he was "one of the pioneers in the field of mathematical origami"; IEEE Richard W. Hamming Medal, 1999. **Documented** ([Wikipedia, David A. Huffman](https://en.wikipedia.org/wiki/David_A._Huffman); [Engineering and Technology History Wiki](https://ethw.org/David_A._Huffman))
- UC Santa Cruz, announcing his death on 8 October 1999: the procedure was "the result of a term paper he wrote while a graduate student" at MIT, and Huffman codes "are used in nearly every application that involves the compression and transmission of digital data". **Documented** ([UC Santa Cruz press release, copy at the University of Florida](https://www.cise.ufl.edu/~manuel/huffman/press.release.html))
- Prefix codes of this kind sit at the back end of DEFLATE (the method of PKZIP) and of codecs such as JPEG and MP3. **Documented** ([Wikipedia, Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Huffman coding](https://en.wikipedia.org/wiki/Huffman_coding) | Wikipedia | The term paper, the bottom-up tree and why it is optimal |
| Start | [Discovery of Huffman Codes](https://old.maa.org/node/646519) | MAA *Convergence*, classroom project | Fano's open problem and the student who solved it, with sources for a class |
| Deeper | [David A. Huffman](https://ethw.org/David_A._Huffman) | Engineering and Technology History Wiki | His career and awards |
| Deeper | [David A. Huffman](https://en.wikipedia.org/wiki/David_A._Huffman) | Wikipedia | Life, later work and mathematical origami |
| Deeper | [UCSC press release, 8 October 1999](https://www.cise.ufl.edu/~manuel/huffman/press.release.html) | University of California, Santa Cruz (copy at the University of Florida) | The announcement of his death, and where his codes were used |

**Original sources**

No copy of the 1952 paper could be opened (see **Gaps**).

**Gaps:** the 1952 paper was not opened: one copy's permission request was withdrawn, and the IEEE Xplore page returned no content. Its citation is taken from Wikipedia. The YouTube pages of Tom Scott's "How Computers Compress Text" (rate-limited) and Computerphile's "How Huffman Trees Work" (error) could not be read. Fano's 1949 report and the 1991 *Scientific American* profile were not opened.

## 4. Hashing

**When / where:** IBM, New York: Hans Peter Luhn's internal memorandum of January 1953 (buckets and chaining); Gene Amdahl, Elaine M. Boehme (later McGraw), Nathaniel Rochester and Arthur Samuel, building an assembler for the IBM 701 (open addressing with linear probing, 1954); Arnold Dumey, *Computers and Automation*, December 1956 (the first published description); W. W. Peterson, "Addressing for Random-Access Storage", *IBM Journal*, April 1957.
**Atlas:** to be mapped · **Code:** [`Hashing.java`](../../code/era-05-the-programmers-craft/04-hashing/) · **Page:** [topic 4](04-hashing/README.md)

> **Field note.** The new machines could reach any word of their memory in the same short time, and their owners began to store files too large to search from end to end. Sorting a file and searching it by halves took one more step every time the file doubled. An engineer at IBM proposed something stranger: compute where a record lives from the record itself. Chop the key into pieces, add them, keep the last digits, and go straight to that bucket. Two keys sometimes land together, so each bucket holds a short list, or, in a colleague's version, the record moves on to the next free place. Either way, a search costs a few looks whether the file holds a thousand records or a million. The method was old jargon before anyone printed its name.

**What hurt:** finding a record in a large file meant a search through it, or through a sorted index, taking longer as the file grew.
**The step forward:** hashing: compute an address from the key; handle collisions with a list per bucket (chaining) or by trying the next place (open addressing); while the table is not too full, a search takes a few probes regardless of the file's size.

**Evidence and certainty**

- "H. P. Luhn, who wrote an internal IBM memorandum in January 1953 that suggested the use of chaining"; "He pointed out the desirability of using buckets that contain more than one element, for external searching." At the same time Gene M. Amdahl, Elaine M. Boehme, N. Rochester and Arthur L. Samuel "were building an assembly program for the IBM 701", and "Amdahl originated the idea of open addressing with linear probing." **Documented** ([Knuth, *The Art of Computer Programming* vol. 3, §6.4 history, pp. 547–548](https://www.Gwern.net/doc/cs/algorithm/information/compression/1998-knuth-taocp-v3-sortingandsearching-hashinghistory.pdf))
- Linear probing "was first used by Gene Amdahl, Elaine M. McGraw (née Boehme), and Arthur Samuel in 1954, in an assembler program for the IBM 701 computer"; "The first published description of linear probing is by Peterson (1957)". **Documented** ([Wikipedia, Linear probing](https://en.wikipedia.org/wiki/Linear_probing))
- Luhn's example (as retold): the ten digits of a phone number in pairs, each pair added, the last digit of each sum kept, the digits together giving a bucket number. **Documented** as retold by Hallam Stevens ([IEEE Spectrum, 30 January 2018](https://spectrum.ieee.org/tech-history/silicon-revolution/hans-peter-luhn-and-the-birth-of-the-hashing-algorithm)); the memorandum itself was not opened
- Luhn (1 July 1896 – 19 August 1964) joined IBM in 1941; "In 1953, he suggested putting information into buckets in order to speed up search"; he also created the Luhn checksum algorithm and the KWIC method of indexing. **Documented** ([Wikipedia, Hans Peter Luhn](https://en.wikipedia.org/wiki/Hans_Peter_Luhn))
- "Hash coding was first described in the open literature by Arnold I. Dumey, Computers and Automation 5,12 (December 1956), 6-9"; Dumey was "the first to mention the idea of dividing by a prime number and using the remainder as the hash address". The article, "Indexing for Rapid Random Access Memory Systems", divides "by a number slightly less than the number of addressable locations", preferably a prime. **Documented** ([Knuth, p. 547](https://www.Gwern.net/doc/cs/algorithm/information/compression/1998-knuth-taocp-v3-sortingandsearching-hashinghistory.pdf); [*Computers and Automation*, December 1956, scan at bitsavers](https://bitsavers.mirrorservice.org/magazines/Computers_And_Automation/195612.pdf))
- Peterson (*IBM Journal*, April 1957, 130–146): "If that is already occupied, the second listed position would be used. If that also is full, the third would be tried, etc., until an empty position is found." His Table 5A (buckets of 20, 10,000 records) gives average searches of 1.000, 1.002, 1.033, 1.134, 1.334 and 4.041 buckets at 40, 60, 80, 90, 95 and 100% full. **Documented** ([Peterson 1957](https://www.Gwern.net/doc/cs/algorithm/1957-peterson.pdf))
- A. P. Ershov "independently discovered linear open addressing in 1957". **Documented** ([Knuth, p. 547](https://www.Gwern.net/doc/cs/algorithm/information/compression/1998-knuth-taocp-v3-sortingandsearching-hashinghistory.pdf))
- The word: "The first published appearance of the word seems to have been in H. Hellerman's book" (1967), though "it had already become common jargon"; an earlier use is in "an unpublished memorandum written by W. W. Peterson in 1961". **Documented** ([Knuth, p. 548](https://www.Gwern.net/doc/cs/algorithm/information/compression/1998-knuth-taocp-v3-sortingandsearching-hashinghistory.pdf))
- Knuth's analysis (1963) showed that linear probing takes constant expected time per operation; it "was never formally published". **Documented** ([Wikipedia, Linear probing](https://en.wikipedia.org/wiki/Linear_probing))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Hans Peter Luhn and the Birth of the Hashing Algorithm](https://spectrum.ieee.org/tech-history/silicon-revolution/hans-peter-luhn-and-the-birth-of-the-hashing-algorithm) | Hallam Stevens, IEEE Spectrum (2018) | Luhn's buckets, told with his phone-number example |
| Start | [Linear probing](https://en.wikipedia.org/wiki/Linear_probing) | Wikipedia | Amdahl's next-free-slot method, its history and its cost |
| Start | [Hans Peter Luhn](https://en.wikipedia.org/wiki/Hans_Peter_Luhn) | Wikipedia | The engineer behind hashing, the Luhn checksum and KWIC indexes |
| Deeper | [History of hashing, *The Art of Computer Programming* §6.4](https://www.Gwern.net/doc/cs/algorithm/information/compression/1998-knuth-taocp-v3-sortingandsearching-hashinghistory.pdf) | Donald E. Knuth (excerpt, 1998 edition) | Who did what between 1953 and 1967, from interviews and memoranda |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Indexing for Rapid Random Access Memory Systems](https://bitsavers.mirrorservice.org/magazines/Computers_And_Automation/195612.pdf) | Arnold I. Dumey, *Computers and Automation* 5(12): 6–9 (December 1956), scan at bitsavers | The first published description: divide by a prime, keep the remainder |
| Scholar | [Addressing for Random-Access Storage](https://www.Gwern.net/doc/cs/algorithm/1957-peterson.pdf) | W. W. Peterson, *IBM Journal* (April 1957), 130–146 | Open addressing measured: the tables this topic's program repeats |

**Gaps:** Luhn's 1953 memorandum was not found online; his example is quoted through IEEE Spectrum. The Wikipedia article "Hash table" was not opened (its permission request was withdrawn). No video page could be opened. The OCR of the 1956 scan spells the author "Durney"; Knuth gives "Dumey".

## 5. Dynamic programming

**When / where:** Richard Bellman at the RAND Corporation, Santa Monica: research mathematician there from 1952; first publication on dynamic programming 1952; RAND memoranda from 1952 (RM-813, "On a problem in dynamic programming"); "Dynamic programming and a new formalism in the calculus of variations", *PNAS* 40(4): 231–235 (April 1954); the book *Dynamic Programming* (Princeton, 1957).
**Atlas:** to be mapped · **Code:** [`DynamicProgramming.java`](../../code/era-05-the-programmers-craft/05-dynamic-programming/) · **Page:** [topic 5](05-dynamic-programming/README.md)

> **Field note.** The Air Force paid a think-tank, and the think-tank set a mathematician to study "multistage decision processes": decisions taken one after another, each changing the situation for the next. Every stage multiplied the number of complete plans, and trying them all was out of the question. Bellman's observation sounds almost too simple: the remainder of a best plan must itself be best for wherever the first step leaves you. So he started at the end, valued every situation there, and worked backwards one stage at a time, keeping each value in a table. He chose the name, he said later, so that no official could object to it; the story does not quite fit the calendar. Pascal had already done the same thing with a gambling problem (Era 3, topic 4). Bellman made it a method for everything.

**What hurt:** decisions made in many stages: the number of complete plans grows as a product of the choices at each stage, far beyond what could be listed.
**The step forward:** the principle of optimality: solve the last stage first, store the best value of every situation, and work backwards; each sub-problem is solved once. With chance, the best expected value.

**Evidence and certainty**

- "The method was developed by Richard Bellman in the 1950s"; "By 1953, he refined this to the modern meaning". **Documented** ([Wikipedia, Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming))
- Bellman (26 August 1920 – 19 March 1984) first worked at RAND in the summer of 1949 and "left Stanford in 1952 and took up the position of Research Mathematician at RAND"; "Bellman's first publication on dynamic programming appeared in 1952", and his first book on the topic was published by RAND in 1953. A bibliography lists "621 papers, 41 books and 21 translations of books". **Documented** ([MacTutor, Bellman](https://mathshistory.st-andrews.ac.uk/Biographies/Bellman/))
- RAND lists "On a problem in dynamic programming" by Richard Ernest Bellman, RM-813, 1952, and "On some variational problems occurring in the theory of dynamic programming—IV" (Bellman, Glicksberg and Gross), RM-978, 1952. **Documented** ([RAND RM-813](https://www.rand.org/pubs/research_memoranda/RM813.html); [RAND RM-978](https://www.rand.org/pubs/research_memoranda/RM978.html))
- Bellman, "Dynamic programming and a new formalism in the calculus of variations", *PNAS* 40(4): 231–235, April 1954. **Documented** ([PubMed Central record](https://pmc.ncbi.nlm.nih.gov/articles/PMC527981))
- The name, in Bellman's autobiography *Eye of the Hurricane* (1984), p. 159: "I spent the Fall quarter (of 1950) at RAND. My first task was to find a name for multistage decision processes"; Wilson, the Secretary of Defense, "had a pathological fear and hatred of the word, research"; "it's impossible to use the word, dynamic, in a pejorative sense"; "It was something not even a Congressman could object to." **Documented** as Bellman's recollection ([Stuart Dreyfus, "Richard Bellman on the Birth of Dynamic Programming", *Operations Research* 50(1): 48–51 (2002)](https://web.cs.miami.edu/home/odelia/teaching/csc317_fall19/syllabus/dy_birth.pdf); [Timothy Taylor, Conversable Economist (2022)](https://conversableeconomist.com/2022/08/24/why-is-it-called-dynamic-programming/))
- The story "may be inaccurate": Russell and Norvig note that it "cannot be strictly true", because Bellman's first paper using the term (1952) predates Wilson's appointment as Secretary of Defense in 1953; Harold Kushner recalled Bellman saying he "was trying to upstage Dantzig's linear programming by adding dynamic". **Disputed** ([Wikipedia, Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming))
- "I decided to call this technique 'The principle of optimality.'" Asked whether it was rigorous: "Of course not. It's not even precise. A good principle should guide the intuition." **Documented** as Bellman's recollection ([Dreyfus 2002](https://web.cs.miami.edu/home/odelia/teaching/csc317_fall19/syllabus/dy_birth.pdf))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Dynamic programming](https://en.wikipedia.org/wiki/Dynamic_programming) | Wikipedia | The method, the Bellman equation and the disputed story of the name |
| Start | [Why Is It Called "Dynamic Programming"?](https://conversableeconomist.com/2022/08/24/why-is-it-called-dynamic-programming/) | Timothy Taylor, Conversable Economist (2022) | Bellman's own account, quoted at length |
| Deeper | [Richard Ernest Bellman](https://mathshistory.st-andrews.ac.uk/Biographies/Bellman/) | MacTutor | His career at RAND and after |
| Deeper | [Richard Bellman on the Birth of Dynamic Programming](https://web.cs.miami.edu/home/odelia/teaching/csc317_fall19/syllabus/dy_birth.pdf) | Stuart Dreyfus, *Operations Research* 50(1) (2002), on a University of Miami course page | Excerpts from *Eye of the Hurricane*, introduced by a colleague |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [On a problem in dynamic programming](https://www.rand.org/pubs/research_memoranda/RM813.html) | R. E. Bellman, RAND RM-813 (1952) | One of the first RAND memoranda with the name (catalogue record) |
| Scholar | [Dynamic programming and a new formalism in the calculus of variations](https://pmc.ncbi.nlm.nih.gov/articles/PMC527981) | R. Bellman, *PNAS* 40(4): 231–235 (1954) | An early journal paper, with a free scan |

**Gaps:** no video page could be opened. The 1957 book was not opened. RAND's pages for RM-813 and RM-978 give no abstract, and their texts were not read. The PNAS paper's text was not read (the record page has only metadata). Bellman's first 1952 paper was not identified with certainty.

## 6. Linked lists and garbage collection

**When / where:** Allen Newell, Cliff Shaw and Herbert A. Simon, RAND Corporation and the Carnegie Institute of Technology, about 1956: the Information Processing Language (IPL), built on linked lists, for the Logic Theorist; "Programming the Logic Theory Machine" (Newell and Shaw, Western Joint Computer Conference, February 1957). John McCarthy, MIT: Lisp, from 1958; garbage collection, around 1959; "Recursive Functions of Symbolic Expressions and Their Computation by Machine, Part I", *Communications of the ACM* 3(4): 184–195 (1960).
**Atlas:** to be mapped · **Code:** [`ListsAndGarbage.java`](../../code/era-05-the-programmers-craft/06-linked-lists/) · **Page:** [topic 6](06-linked-lists/README.md)

> **Field note.** Programs that tried to reason (proving theorems, playing chess) needed memory that changed shape as they ran: a list of goals that grew and shrank, a formula rebuilt at every step. Arrays could not stretch. The RAND group gave every item a small cell holding the address of the next, so that a list could be spliced anywhere by rewriting an address or two, and they kept the unused cells on a list of their own. McCarthy built a whole language from cells with two addresses. It brought a new problem: programs left cells behind that nothing pointed to. Rather than make the programmer return each one, McCarthy let the machine do it: when the free cells ran out, it marked everything still reachable and took back the rest. He called it garbage collection, though not in print.

**What hurt:** fixed blocks of memory could not grow, shrink or be spliced; programs that manipulated symbols needed structures whose size and shape were unknown in advance, and returning unused memory by hand was a constant source of errors.
**The step forward:** linked lists: cells that hold an item and the address of the next cell, taken from and returned to a free list; and garbage collection: when the free list is empty, mark every cell reachable from the program's roots and return all the others.

**Evidence and certainty**

- IPL was "created by Allen Newell, Cliff Shaw, and Herbert A. Simon at RAND Corporation and the Carnegie Institute of Technology about 1956"; it implemented "the Logic Theorist (1956), the General Problem Solver (1957)"; it "introduced the concepts of symbol processing and list processing", with "lists, dynamic memory allocation, data types, recursion, functions as arguments, generators"; "H2 is the free-list"; "Many of these features were generalized, rationalized, and incorporated into Lisp." **Documented** ([Wikipedia, Information Processing Language](https://en.wikipedia.org/wiki/Information_Processing_Language))
- Linked lists were developed by Newell, Shaw and Simon as the main data structure of IPL; reports appeared in *IRE Transactions on Information Theory* (1956) and in conference proceedings 1957–1959; Newell and Shaw's "Programming the Logic Theory Machine" (WJCC, February 1957) has the "now-classic diagram" of blocks joined by arrows. Newell and Simon received the 1975 ACM Turing Award, citing list processing among their contributions. **Documented** ([Wikipedia, Linked list](https://wikipedia.com/wiki/LinkedList))
- Luhn's memorandum of January 1953 (topic 4) had already suggested linked lists for chained hash tables. **Documented** ([Wikipedia, Linked list](https://wikipedia.com/wiki/LinkedList))
- McCarthy (4 September 1927 – 24 October 2011): "Around 1959, he invented so-called 'garbage collection' methods"; Lisp "soon became the programming language of choice for AI applications after its publication in 1960"; Turing Award 1971; co-author of the 1955 Dartmouth proposal that coined "artificial intelligence". **Documented** ([Wikipedia, John McCarthy](https://en.wikipedia.org/wiki/John_McCarthy_(computer_scientist)))
- "Garbage collection was invented by American computer scientist John McCarthy around 1959 to simplify manual memory management in Lisp"; a tracing collector finds the objects "reachable by a chain of references from certain root objects" and reclaims the rest. **Documented** ([Wikipedia, Garbage collection](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)))
- The 1960 paper: "When a free register is wanted, and there is none left on the free-storage list, a reclamation cycle starts", with McCarthy's later footnote: "We already called this process 'garbage collection', but I guess that I chickened out of using it in the paper—or else the Research Laboratory of Electronics grammar ladies wouldn't let me." **Documented** as quoted in University of Cambridge lecture slides ([Cambridge, Concepts in Programming Languages, LISP slides](https://www.cl.cam.ac.uk/teaching/0708/ConceptsPL/LISP.pdf)); the paper itself was not opened
- Victor Yngve's COMIT (MIT, 1958) also used linked lists, for machine translation; the claim is marked as needing a citation. **Conjecture** ([Wikipedia, Linked list](https://wikipedia.com/wiki/LinkedList))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Linked list](https://wikipedia.com/wiki/LinkedList) | Wikipedia | The data structure and its history at RAND and MIT |
| Start | [Garbage collection (computer science)](https://en.wikipedia.org/wiki/Garbage_collection_(computer_science)) | Wikipedia | Reclaiming unreachable memory, from McCarthy to today |
| Deeper | [Information Processing Language](https://en.wikipedia.org/wiki/Information_Processing_Language) | Wikipedia | The first list-processing language and its free list |
| Deeper | [John McCarthy](https://en.wikipedia.org/wiki/John_McCarthy_(computer_scientist)) | Wikipedia | Lisp, garbage collection and the name "artificial intelligence" |

**Lecture**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [LISP](https://www.cl.cam.ac.uk/teaching/0708/ConceptsPL/LISP.pdf) | University of Cambridge, Concepts in Programming Languages (2007–08) | Lecture slides on McCarthy's paper, with his remark about the name |

**Gaps:** McCarthy's 1960 paper and Newell and Shaw's 1957 paper were not opened; McCarthy's wording is quoted from lecture slides. No video page could be opened. The program's memory is a simplified two-address store, not the IBM 704's word layout.

## 7. Dijkstra's shortest paths

**When / where:** Edsger W. Dijkstra, programmer at the Mathematical Centre, Amsterdam: the shortest-path method designed in 1956 for the public inauguration of the ARMAC computer, and a shortest-wiring method for the X1 computer; both in "A note on two problems in connexion with graphs", *Numerische Mathematik* 1: 269–271 (1959).
**Atlas:** to be mapped · **Code:** [`ShortestPaths.java`](../../code/era-05-the-programmers-craft/07-shortest-paths/) · **Page:** [topic 7](07-shortest-paths/README.md)

> **Field note.** A machine was to be shown to the public, and its programmer wanted a problem that visitors could understand, with an answer they could check: the shortest road between two Dutch cities. He worked out the method in his head, he said, in about twenty minutes, at a café table, without pencil or paper. Grow the set of cities whose distance is settled one at a time, always taking next the nearest of the cities on its edge; nothing reached later can undercut it. The same short paper joined points with the least wire, a problem from the next machine's wiring panel. He waited three years to publish, because there were hardly any journals for such things; the method now runs, in some form, whenever one of the species asks a telephone for directions.

**What hurt:** route-finding on a network: listing all routes grows explosively, and Ford's method, as Berge described it, kept data for every road at once.
**The step forward:** settle one place at a time, always the nearest unsettled one, and update its neighbours; each place is settled once, and only the roads into the frontier set need to be stored.

**Evidence and certainty**

- The paper states two problems: "Construct the tree of minimum total length between the n nodes" and "Find the path of minimum total length between two given nodes P and Q"; the nodes are divided into sets A ("the nodes for which the path of minimum length from P is known"), B and C, and at each step "the node with minimum distance from P is transferred from set B to set A". **Documented** ([Dijkstra 1959, scan](https://isidore.co/misc/Physics%20papers%20and%20books/Zotero/storage/RQ5SZPTE/Dijkstra%20-%201959%20-%20A%20note%20on%20two%20problems%20in%20connexion%20with%20graphs.pdf); [CWI repository record](https://ir.cwi.nl/pub/9256))
- Against Ford's method as described by Berge, "we need not store the data for all branches simultaneously but only those for the branches in sets I and II, and this number is always less than n"; for the tree problem, Kruskal's and Loberman and Weinberger's methods "demand that data for all branches are stored simultaneously". **Documented** ([Dijkstra 1959](https://isidore.co/misc/Physics%20papers%20and%20books/Zotero/storage/RQ5SZPTE/Dijkstra%20-%201959%20-%20A%20note%20on%20two%20problems%20in%20connexion%20with%20graphs.pdf))
- For the official inauguration of the ARMAC in 1956 he wrote a program for a question a nontechnical audience could follow: "Given a network of roads connecting cities, what is the shortest route between two designated cities?"; the minimum spanning tree method, for the X1, "finds the shortest length of wire needed to connect a given set of points on a wiring panel". Dijkstra (11 May 1930 – 6 August 2002); Turing Award 1972, "For fundamental contributions to programming as a high, intellectual challenge". **Documented** ([ACM Turing Award page](https://amturing.acm.org/award_winners/dijkstra_1053701))
- "He formulated and solved the shortest path problem in 1956"; "Because of the absence of journals dedicated to automatic computing, he did not publish the result until 1959." When he married in 1957, "He stated that he was a programmer, which was unacceptable to the authorities." **Documented** ([Wikipedia, Edsger W. Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra))
- His own account (interview with Philip Frana, August 2001, published in *Communications of the ACM* in 2010): the question "What's the shortest way to travel from Rotterdam to Groningen", worked out sitting on a "café terrace" in Amsterdam with "my young fiancée", in about twenty minutes, "without pencil and paper"; "it was published in 1959, three years later". **Documented** as Dijkstra's recollection ([CACM, "An Interview With Edsger W. Dijkstra"](https://cacm.acm.org/?p=31927))
- The ARMAC demonstration used a simplified map of the Netherlands with 64 cities. **Documented** as reported by Michael Byrne ([Vice, 22 March 2015](https://www.vice.com/en/article/4x3pp9/the-simple-elegant-algorithm-that-makes-google-maps-possible)) and Emma Bell ([*Chalkdust*, 12 March 2018](https://chalkdustmagazine.com/biographies/routes-edsger-dijkstra/)); not found in the interview or the paper
- The tree method Dijkstra published had been given by Jarník in 1930 (Era 4, topic 4); Dijkstra's paper credits Kruskal, and Loberman and Weinberger, for other methods. **Conjecture** as to whether Dijkstra knew of Jarník's paper

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [An Interview With Edsger W. Dijkstra](https://cacm.acm.org/?p=31927) | Philip L. Frana (2001), *Communications of the ACM* | The café, the twenty minutes, and why it waited three years |
| Start | [The Simple, Elegant Algorithm That Makes Google Maps Possible](https://www.vice.com/en/article/4x3pp9/the-simple-elegant-algorithm-that-makes-google-maps-possible) | Michael Byrne, Vice (2015) | The ARMAC demonstration and the 64 cities |
| Start | [Routes: Edsger Dijkstra](https://chalkdustmagazine.com/biographies/routes-edsger-dijkstra/) | Emma Bell, *Chalkdust* (2018) | A short biography for students |
| Deeper | [Edsger W. Dijkstra](https://amturing.acm.org/award_winners/dijkstra_1053701) | ACM Turing Award | The ARMAC program, the X1 wiring problem and his later work |
| Deeper | [Edsger W. Dijkstra](https://en.wikipedia.org/wiki/Edsger_W._Dijkstra) | Wikipedia | Life and work, from the Mathematical Centre to Austin |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A note on two problems in connexion with graphs](https://isidore.co/misc/Physics%20papers%20and%20books/Zotero/storage/RQ5SZPTE/Dijkstra%20-%201959%20-%20A%20note%20on%20two%20problems%20in%20connexion%20with%20graphs.pdf) | E. W. Dijkstra, *Numerische Mathematik* 1: 269–271 (1959), scan | The three-page paper: the tree, the path, and the sets A, B, C |
| Scholar | [A note on two problems in connexion with graphs](https://ir.cwi.nl/pub/9256) | CWI repository record, with the full text | The paper at the institute where Dijkstra worked |

**Gaps:** no video page could be opened. The OCR of the scan garbles the volume number; volume 1 is taken from the CWI record. The 64-city detail comes from two secondary articles, not from Dijkstra's own words. The program's map is invented, not the Dutch map of 1956.

## 8. The compiler, and a grammar for languages

**When / where:** John Backus and a team at IBM, New York: the FORTRAN project from the summer of 1954; the manual for the IBM 704, October 1956; "The FORTRAN Automatic Coding System", Western Joint Computer Conference, Los Angeles, 26–28 February 1957; the first compiler delivered in April 1957. Backus's notation for syntax, UNESCO conference, Paris, 1959; the ALGOL 60 report, edited by Peter Naur (1960).
**Atlas:** to be mapped · **Code:** [`Compiler.java`](../../code/era-05-the-programmers-craft/08-the-compiler/) · **Page:** [topic 8](08-the-compiler/README.md)

> **Field note.** Programming the first machines meant writing their instructions one by one, and most of a programmer's time went on the bookkeeping: which word holds what, which register counts the loop. A team at IBM proposed that the machine translate formulas written almost as a mathematician writes them. The team set itself a hard condition, that the translated program be as good as a careful coder's, and spent two and a half years meeting it. One of its first users wrote 47 statements in four hours; the machine turned them into about a thousand instructions in six minutes. Two years later Backus found a way to define such a language exactly: a handful of rules, each saying what a phrase may be made of. With rules like that, the translator could be written from the definition.

**What hurt:** writing programs instruction by instruction was slow and error-prone, and a translator was worth having only if its programs were as good as hand-written ones; languages were described in prose, which left their meaning open to argument.
**The step forward:** the optimizing compiler: formulas and loops translated into machine code nearly as good as a careful programmer's; and a formal grammar (BNF): recursive rules that define exactly which strings belong to a language and what their structure is.

**Evidence and certainty**

- The 1957 paper: "The FORTRAN project was begun in the summer of 1954"; "Two and one-half years and 18 man years have elapsed since the beginning of the project"; the aim was to "produce as good programs as human coders (but without the errors)"; "It was expected that such a system would reduce the coding and debugging task to less than one-fifth of the job it had been." **Documented** ([Backus et al., "The FORTRAN Automatic Coding System" (1957), p. 189, on a University of Massachusetts course page](https://people.cs.umass.edu/~emery/classes/cmpsci691st/readings/PL/FORTRAN-102663113.05.01.acc.pdf))
- A case history in the paper: a user "programmed the job in four hours, using 47 FORTRAN statements. These were compiled by the 704 in six minutes, producing about 1000 instructions"; he "estimated that it might have taken three days to code this job by hand". The authors warn that a case chosen by a system's own authors "seldom gives a good measure of its usefulness". **Documented** ([Backus et al. 1957, p. 189](https://people.cs.umass.edu/~emery/classes/cmpsci691st/readings/PL/FORTRAN-102663113.05.01.acc.pdf))
- How formulas are translated: "there is implicit in every arithmetic formula an order of computation", fixed by conventions on the symbols; the translator assigns level numbers so that "the operations are carried out in the order of increasing level number"; its six sections hold roughly 5,500, 6,000, 2,500, 3,000, 5,000 and 2,000 instructions. **Documented** ([Backus et al. 1957, pp. 192–197](https://people.cs.umass.edu/~emery/classes/cmpsci691st/readings/PL/FORTRAN-102663113.05.01.acc.pdf))
- The paper appeared in the *Proceedings of the Western Joint Computer Conference*, Los Angeles, pp. 188–198, with thirteen authors from J. W. Backus to R. A. Hughes; "the first formal paper on the completed FORTRAN implementation". **Documented** ([Computer History Museum catalogue](https://www.computerhistory.org/collections/catalog/102663113)); the first manual dates from October 1956 and the first compiler was delivered in April 1957 **Documented** ([Centre for Computing History](https://www.computinghistory.org.uk/det/5492/FORTRAN-1-is-formally-published/))
- Backus (3 December 1924 – 17 March 2007) proposed the language in 1953, building on his Speedcoding work; Turing Award 1977, "For profound, influential, and lasting contributions to the design of practical high-level programming systems". **Documented** ([ACM Turing Award page](https://amturing.acm.org/award_recipient/backus_0703524))
- Backus's paper at the UNESCO conference in Paris (1959), "The syntax and semantics of the proposed international algebraic language of the Zurich ACM-GAMM Conference", proposed a metalanguage for syntax; the ALGOL 60 report used it; Knuth (1964) argued for reading BNF as "Backus–Naur form", since it is "not a normal form in the conventional sense"; Ingerman (1967) proposed "Pāṇini Backus form". **Documented** ([Wikipedia, Backus–Naur form](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form))
- The ALGOL 60 report: "Sequences of characters enclosed in the bracket <> represent metalinguistic variables"; "The marks ::= and | (the latter with the meaning of **or**) are metalinguistic connectives"; its arithmetic expressions are defined by rules such as "<term> ::= <factor> | <term> <multiplying operator> <factor>". **Documented** ([Revised Report on the Algorithmic Language Algol 60, edited by Peter Naur, transcription at masswerk.at](https://masswerk.at/algol60/report.htm))
- Whether FORTRAN was the first compiler: earlier translators existed (Backus's own Speedcoding among them); FORTRAN is the first that the opened sources describe as aiming at hand-coded efficiency. **Conjecture** as to "first"

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [FORTRAN-1 is formally published](https://www.computinghistory.org.uk/det/5492/FORTRAN-1-is-formally-published/) | Centre for Computing History | The dates: manual, paper, first compiler |
| Start | [Backus–Naur form](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form) | Wikipedia | Rules that define a language, from Backus 1959 to today |
| Deeper | [John Backus](https://amturing.acm.org/award_recipient/backus_0703524) | ACM Turing Award | Speedcoding, FORTRAN, BNF and his later work |
| Deeper | [The FORTRAN automatic coding system](https://www.computerhistory.org/collections/catalog/102663113) | Computer History Museum catalogue | The 1957 paper's record and author list |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The FORTRAN Automatic Coding System](https://people.cs.umass.edu/~emery/classes/cmpsci691st/readings/PL/FORTRAN-102663113.05.01.acc.pdf) | J. W. Backus et al., *Proceedings of the Western Joint Computer Conference* (February 1957), on a University of Massachusetts course page | The compiler described by its makers, with the 47-statement case history |
| Scholar | [Revised Report on the Algorithmic Language Algol 60](https://masswerk.at/algol60/report.htm) | Edited by Peter Naur; transcription at masswerk.at | The grammar of a whole language written in BNF |

**Gaps:** no video page could be opened. The copy of the 1957 paper at softwarepreservation.org redirects to another host whose permission request was withdrawn; the University of Massachusetts copy was used instead. Backus's 1959 Paris paper and his "History of FORTRAN I, II, and III" (1978) were not opened. The program's machine has one accumulator and four instructions, not the IBM 704's order code.

## 9. Rosenblatt's perceptron

**When / where:** Frank Rosenblatt, research psychologist and project engineer at the Cornell Aeronautical Laboratory, Buffalo, New York: the perceptron simulated on an IBM 704 in 1957; demonstrated by the U.S. Office of Naval Research in July 1958; "The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain", *Psychological Review* 65(6): 386–408 (1958); the Mark I Perceptron, a machine with 400 photocells, built by 1960.
**Atlas:** to be mapped · **Code:** [`Perceptron.java`](../../code/era-05-the-programmers-craft/09-perceptron/) · **Page:** [topic 9](09-perceptron/README.md)

> **Field note.** Every procedure so far had been written down by someone who understood the problem. Rosenblatt, a psychologist, wanted a machine that would find its own procedure from examples, as he supposed a brain must. His unit adds up weighted inputs and answers yes or no; when it is wrong, it shifts its weights toward the right answer, and when it is right it leaves them alone. Shown cards marked on the left or the right, it learned to tell them apart. The Navy's press conference promised far more, and the newspapers repeated it. Eleven years later two critics proved what a single unit could never learn, and interest collapsed for a decade. The learning rule itself survived, and in layered form it is how the species now trains its largest machines.

**What hurt:** recognising patterns (letters, shapes, positions) by writing explicit rules for every case; nobody knew how to make a machine improve from experience.
**The step forward:** a learning machine: a weighted sum and a threshold whose weights are corrected after each wrong answer; for any task in which a straight cut separates the yes cases from the no cases, the corrections stop after finitely many mistakes.

**Evidence and certainty**

- The artificial neuron was "invented in 1943 by Warren McCulloch and Walter Pitts"; at the Cornell Aeronautical Laboratory Rosenblatt "simulated the perceptron on an IBM 704" (1957); the Office of Naval Research and the Rome Air Development Center funded a custom machine, the Mark I, with "An array of 400 photocells arranged in a 20x20 grid", weights in potentiometers and "weight updates during learning were performed by electric motors". **Documented** ([Wikipedia, Perceptron](https://en.wikipedia.org/wiki/Perceptron))
- "In July 1958, the U.S. Office of Naval Research unveiled a remarkable invention"; "After 50 trials, the computer taught itself to distinguish cards marked on the left from cards marked on the right"; the *New York Times* headline: "NEW NAVY DEVICE LEARNS BY DOING: Psychologist Shows Embryo of Computer Designed to Read and Grow Wiser". **Documented** ([Cornell Chronicle, Melanie Lefkowitz, 25 September 2019](https://news.cornell.edu/node/313946))
- After the Navy's press conference the *Times* described "the embryo of an electronic computer that [the Navy] expects will be able to walk, talk, see" and more, which caused controversy among researchers. **Documented** ([Wikipedia, Perceptron](https://en.wikipedia.org/wiki/Perceptron))
- The paper opens: "If we are eventually to understand the capability of higher organisms for perceptual recognition, generalization, recall, and thinking, we must first have answers to three fundamental questions"; it describes learning as "The application of positive and/or negative reinforcement". **Documented** ([Rosenblatt 1958, on a University of Illinois Chicago page](https://homepages.math.uic.edu/~lreyzin/papers/rosenblatt58.pdf))
- Rosenblatt (11 July 1928 – 11 July 1971) died in a boating accident on Chesapeake Bay; the Mark I is in the Smithsonian Institution; *Principles of Neurodynamics* (Spartan Books, 1962). **Documented** ([Wikipedia, Frank Rosenblatt](https://en.wikipedia.org/wiki/Frank_Rosenblatt))
- For linearly separable data "the perceptron is guaranteed to converge after making finitely many mistakes" (Novikoff, dated 1962 in the text and 1963 in the references). Minsky and Papert's book (1969) "showed that it was impossible for these classes of network to learn an XOR function", and interest and funding fell for about a decade, although multilayer perceptrons could compute XOR. **Documented** ([Wikipedia, Perceptron](https://en.wikipedia.org/wiki/Perceptron)); the date of Novikoff's paper is **disputed** between the article's text and its references
- The rule Rosenblatt published is not literally the error-correction rule in this topic's program; his 1958 paper describes reinforcement of active units in several systems. The modern statement is a simplification. **Conjecture** (this catalog's reading of the 1958 paper)

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Professor's perceptron paved the way for AI – 60 years too soon](https://news.cornell.edu/node/313946) | Melanie Lefkowitz, Cornell Chronicle (2019) | The 1958 demonstration, the cards, and the headlines |
| Start | [Perceptron](https://en.wikipedia.org/wiki/Perceptron) | Wikipedia | The learning rule, the Mark I, the convergence theorem and XOR |
| Deeper | [Frank Rosenblatt](https://en.wikipedia.org/wiki/Frank_Rosenblatt) | Wikipedia | His life, the Mark I and *Principles of Neurodynamics* |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Perceptron: A Probabilistic Model for Information Storage and Organization in the Brain](https://homepages.math.uic.edu/~lreyzin/papers/rosenblatt58.pdf) | F. Rosenblatt, *Psychological Review* 65(6): 386–408 (1958), on a University of Illinois Chicago page | The paper: three questions about perception and a machine to answer them |

**Gaps:** no video page could be opened. The 1957 Cornell report, the *New York Times* article itself, Novikoff's paper and Minsky and Papert's *Perceptrons* were not opened. The program's cards are invented 20 x 20 images, not the 1958 cards.

## 10. Hoare's Quicksort

**When / where:** Tony Hoare, a visiting student at Moscow State University, 1959, working towards machine translation for the National Physical Laboratory; "Algorithm 63: Partition" and "Algorithm 64: Quicksort", *Communications of the ACM* 4(7): 321 (July 1961); "Quicksort", *The Computer Journal* 5(1): 10–15 (1962).
**Atlas:** to be mapped · **Code:** [`Quicksort.java`](../../code/era-05-the-programmers-craft/10-quicksort/) · **Page:** [topic 10](10-quicksort/README.md)

> **Field note.** A young Englishman studying in Moscow wanted a machine to translate Russian. Looking words up in the dictionary went faster if the words of each sentence were sorted first, and his first idea for sorting them was too slow. His second was to pick one word, throw the smaller words to one side and the larger to the other, and do the same to each side. He could write the splitting in the language he had, but not, at first, the bookkeeping of all the pieces still waiting to be sorted; when he met ALGOL, in which a procedure may call itself, the whole method took a few lines. Back in England, asked to program another sorting method, he told his employer he knew a faster one, and the employer bet him sixpence that he did not. He later called it the only really interesting algorithm he ever developed. He died in March 2026, at the age of 92.

**What hurt:** sorting in a computer's own memory: the simple methods (insertion) take time proportional to the square of the number of items, and merging (Era 4, topic 9) needs a second area of memory as large as the first.
**The step forward:** divide and conquer in place: partition the list around one item, swapping from both ends, so that each part can be sorted alone; about n log n comparisons on average, with no extra list.

**Evidence and certainty**

- "The quicksort algorithm was developed in 1959 by Tony Hoare while he was a visiting student at Moscow State University"; on a machine translation project for the National Physical Laboratory he needed to "sort the words in Russian sentences before looking them up"; his first idea, insertion sort, was too slow; he wrote the partition in Mercury Autocode but "had trouble dealing with the list of unsorted segments"; "Later, Hoare learned about ALGOL and its ability to do recursion". **Documented** ([Wikipedia, Quicksort](https://en.wikipedia.org/wiki/Quicksort))
- Published as "Algorithm 63: partition and Algorithm 64: Quicksort", *CACM* 4(7), July 1961, p. 321; then a paper with "a theoretical analysis" in *The Computer Journal* 5(1), 1962. On his return to England, asked to write code for Shellsort, he said he knew a faster algorithm, and "his boss bet a sixpence that he did not". **Documented** ([Wikipedia, Quicksort](https://en.wikipedia.org/wiki/Quicksort)); the *Computer Journal* paper's pages, 10–15 **Documented** ([University of Oxford, Department of Computer Science publication record](https://www.cs.ox.ac.uk/publications/publication8195-abstract.html))
- Hoare, in an interview recorded in September 2006 for the Computer History Museum: "it paid to sort the words of the sentence into the same alphabetical order before consulting the dictionary"; "I thought of Quicksort as the second thing"; "I think Quicksort is the only really interesting algorithm that I ever developed." **Documented** ([*Communications of the ACM*, "An Interview With C.A.R. Hoare"](https://cacm.acm.org/?p=20664); [Computer History Museum catalogue](https://www.computerhistory.org/collections/catalog/102658017))
- Average comparisons "2 n ln n ≈ 1.39 n log2 n"; quadratic in the worst case. **Documented** ([Wikipedia, Quicksort](https://en.wikipedia.org/wiki/Quicksort))
- Hoare: National Service 1956–1958, studying Russian in the Royal Navy; graduate student at Moscow State University in 1959; Elliott Brothers from 1960; Queen's University Belfast 1968; Oxford 1977. **Documented** ([University of Oxford, Department of Computer Science](https://www.cs.ox.ac.uk/people/tony.hoare))
- Hoare died peacefully at home on 5 March 2026, at the age of 92. **Documented** ([Wolfson College, Oxford, 16 March 2026](https://www.wolfson.ox.ac.uk/news/wolfson-emeritus-fellow-professor-sir-tony-hoare-dies/); [Computer History Museum, Dag Spicer, 11 March 2026](https://computerhistory.org/blog/in-memoriam-sir-antony-hoare-1934-2026/)); the museum's note recalls his 1980 Turing Award lecture "The Emperor's Old Clothes" and his description of the null reference as his "billion-dollar mistake"

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Quicksort](https://en.wikipedia.org/wiki/Quicksort) | Wikipedia | Moscow, Mercury Autocode, the sixpence, and the analysis |
| Start | [In Memoriam: Sir Antony Hoare (1934–2026)](https://computerhistory.org/blog/in-memoriam-sir-antony-hoare-1934-2026/) | Dag Spicer, Computer History Museum (2026) | His life and work, from Quicksort to the null reference |
| Deeper | [An Interview With C.A.R. Hoare](https://cacm.acm.org/?p=20664) | Jonathan P. Bowen (2006), edited for *Communications of the ACM* | Quicksort in Hoare's own words |
| Deeper | [Tony Hoare](https://www.cs.ox.ac.uk/people/tony.hoare) | University of Oxford, Department of Computer Science | Career outline |
| Deeper | [Wolfson Emeritus Fellow Professor Sir Tony Hoare dies](https://www.wolfson.ox.ac.uk/news/wolfson-emeritus-fellow-professor-sir-tony-hoare-dies/) | Wolfson College, Oxford (16 March 2026) | The college's notice |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Quicksort](https://www.cs.ox.ac.uk/publications/publication8195-abstract.html) | C. A. R. Hoare, *The Computer Journal* 5(1): 10–15 (1962), Oxford publication record | The paper with the analysis |
| Scholar | [Oral history of Sir Antony Hoare](https://www.computerhistory.org/collections/catalog/102658017) | Interview by Jonathan P. Bowen, 8 September 2006, Computer History Museum | The recorded interview behind the CACM excerpt |

**Gaps:** no video page could be opened. The 1961 CACM algorithms and the text of the 1962 paper were not opened; the Oxford record gives only the citation. The sixpence story is quoted from Wikipedia, not from Hoare. The CHM transcript PDF and the oral-history video were not opened.

## 11. AVL trees

**When / where:** Georgy Adelson-Velsky and Evgenii Landis, Moscow: "An algorithm for the organization of information", *Doklady Akademii Nauk SSSR* 146(2): 263–266 (1962), received 13 April 1962; English translation by Myron J. Ricci in *Soviet Mathematics – Doklady* 3: 1259–1263 (1962).
**Atlas:** to be mapped · **Code:** [`AvlTrees.java`](../../code/era-05-the-programmers-craft/11-avl-trees/) · **Page:** [topic 11](11-avl-trees/README.md)

> **Field note.** A search tree finds a key by asking, at each fork, smaller or larger? With luck the tree is bushy and a million keys are found in twenty questions. Without luck, keys arriving in order, it is a single long branch and the questions number in the millions. Two Moscow mathematicians, one of whom would soon lead a chess program, proposed a rule that luck cannot break: at every fork the two branches may differ in height by at most one. When an insertion breaks the rule, a turn of three links restores it. The worst tree the rule allows is shaped by the Fibonacci numbers, and even it is no more than about one and a half times as tall as the best. It was the first search tree that kept itself in balance.

**What hurt:** search trees (and sorted tables) degenerate when keys arrive in an unlucky order: a tree built from sorted keys is a list, and searching it takes time proportional to the number of keys.
**The step forward:** self-balancing: keep the heights of every node's two subtrees within one of each other, repairing with single or double rotations after each insertion; search, insertion and deletion all take time proportional to log n, guaranteed.

**Evidence and certainty**

- The AVL tree, named after "its two Soviet inventors", was invented in 1962 by Georgy Adelson-Velsky and Evgenii Landis, in "An algorithm for the organization of information"; it is "the first self-balancing binary search tree [data structure] to be invented"; the rule: "the heights of the two child subtrees of any node differ by not more than one", restored after insertions and deletions by single or double rotations. **Documented** ([Wikipedia, AVL tree](https://en.wikipedia.org/wiki/AVL_tree))
- The paper: G. M. Adel'son-Vel'skii and E. M. Landis, *Dokl. Akad. Nauk SSSR* 146(2): 263–266 (1962), presented by I. G. Petrovskii, received 13.04.1962; English translation by Myron J. Ricci, *Soviet Mathematics – Doklady* 3: 1259–1263 (1962). **Documented** ([Math-Net.Ru record](https://mathnet.ru/eng/dan26964); [Wikipedia, AVL tree](https://en.wikipedia.org/wiki/AVL_tree))
- The fewest nodes in an AVL tree of a given height follow the Fibonacci numbers, which bounds the height by a constant times log n involving the golden ratio. **Documented** ([Wikipedia, AVL tree](https://en.wikipedia.org/wiki/AVL_tree)); the constant 1.44 in this topic's program is checked by the program, not quoted from the page, whose formula did not survive extraction
- Adelson-Velsky (1922 – 26 April 2014; the article gives both 8 January and 3 March as his birth date) led a chess program at ITEP from 1963 that defeated the Kotok–McCarthy program in 1966, "the first chess match between computer programs", and evolved into Kaissa, "the first world computer chess champion". **Documented**, with the birth date **disputed** within the article ([Wikipedia, Georgy Adelson-Velsky](https://en.wikipedia.org/wiki/Georgy_Adelson-Velsky))
- That the AVL paper itself was motivated by the chess work is often said, but no opened source states it. **Conjecture**

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [AVL tree](https://en.wikipedia.org/wiki/AVL_tree) | Wikipedia | The balance rule, rotations and the Fibonacci bound |
| Deeper | [Georgy Adelson-Velsky](https://en.wikipedia.org/wiki/Georgy_Adelson-Velsky) | Wikipedia | The inventor, and his chess programs |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [An algorithm for organization of information](https://mathnet.ru/eng/dan26964) | G. M. Adel'son-Vel'skii and E. M. Landis, *Dokl. Akad. Nauk SSSR* 146(2): 263–266 (1962), Math-Net.Ru record | The four-page paper, in Russian |

**Gaps:** no video page could be opened. The paper's text and its English translation were not read; the record page has no abstract. Landis's biography was not opened. The NIST Dictionary of Algorithms and Data Structures entry was not opened.

## 12. Heapsort and the heap

**When / where:** J. W. J. Williams, programmer at Elliott Automation (formerly Elliott Brothers), England: "Algorithm 232 – Heapsort", *Communications of the ACM* 7(6): 347–348 (June 1964). Robert W. Floyd, the same year: "Algorithm 245 – Treesort 3", *Communications of the ACM* 7(12): 701 (December 1964).
**Atlas:** to be mapped · **Code:** [`Heapsort.java`](../../code/era-05-the-programmers-craft/12-heapsort/) · **Page:** [topic 12](12-heapsort/README.md)

> **Field note.** Quicksort was fast on average and dreadful on bad days. A programmer at an English computer firm found a method with no bad days. Arrange the list as a family tree squeezed into an array, every parent at least as large as its two children, so that the largest item always sits at the front. Take it, put it at the back, let the item that replaced it sink to its proper level, and repeat: the list sorts itself from the back forward, in its own space, in time proportional to n log n whatever order it arrived in. Within the year Floyd showed that the first step, arranging the heap, can be done in fewer than two comparisons per item. The heap outlived the sort: any program that must keep taking out the most urgent of many waiting tasks uses one.

**What hurt:** Quicksort's bad cases (n²) and merging's extra memory; and programs that must repeatedly find and remove the largest (or most urgent) of a changing set of items had to search it each time.
**The step forward:** the binary heap: a complete binary tree stored in an array, each item at least as large as its children; insertion and removal of the largest in log n steps; heapsort, which sorts in place in at most about 2 n log2 n comparisons on any input; Floyd's bottom-up construction in linear time.

**Evidence and certainty**

- Williams devised heapsort in 1964 (*CACM* 7(6): 347–348); his paper also "introduced the binary heap as a useful data structure in its own right". In the same year Floyd "published an improved version that could sort an array in-place", with a heap construction that "operates in O(n) time" (*CACM* 7(12): 701). Heapsort is in place but "not a stable sort"; it removes the largest item repeatedly "in a similar manner to Selection sort". **Documented** ([Wikipedia, Heapsort](https://en.wikipedia.org/wiki/Heapsort))
- The worst case of Floyd's heap construction "is known to be equal to 2n − 2s₂(n) − e₂(n)" comparisons, s₂(n) the number of 1 bits of n and e₂(n) its trailing 0 bits; heapsort "requires 2n log₂ n + O(n) comparisons worst-case and on average". **Documented** ([Wikipedia, Heapsort](https://en.wikipedia.org/wiki/Heapsort)); this topic's program reproduces the construction formula for every n from 2 to 10 by trying every ordering
- "The heap data structure, specifically the binary heap, was introduced by J. W. J. Williams in 1964, as a data structure for the heapsort sorting algorithm"; heaps implement priority queues and "are also crucial in several efficient graph algorithms such as Dijkstra's algorithm"; a heap can be built "in linear time using the classic Floyd algorithm". **Documented** ([Wikipedia, Heap (data structure)](https://en.wikipedia.org/wiki/Heap_(data_structure)))
- John William Joseph (Bill) Williams, born September 1930 in the Chippenham district of Wiltshire, died 29 September 2012; programmer for Elliot Automation, later English Electric and GEC; from 1974 at Bell-Northern Research in Ottawa. The article dates the invention to 1963, the year before publication. **Documented**, with the year of invention **disputed** between 1963 (the biography) and 1964 (the publication) ([Wikipedia, J. W. J. Williams](https://en.wikipedia.org/wiki/J._W._J._Williams))
- Bibliographic record: J. W. J. Williams, "Algorithm 232 - Heapsort", *Communications of the ACM* 7(6): 347–348, 1964. **Documented** ([University of Copenhagen bibliography](https://hjemmesider.diku.dk/~henglein/bib/publications/williams1964.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Heapsort](https://en.wikipedia.org/wiki/Heapsort) | Wikipedia | Williams's method, Floyd's improvement and the comparison counts |
| Start | [Heap (data structure)](https://en.wikipedia.org/wiki/Heap_(data_structure)) | Wikipedia | The heap as a priority queue, and its uses beyond sorting |
| Deeper | [J. W. J. Williams](https://en.wikipedia.org/wiki/J._W._J._Williams) | Wikipedia | The inventor's career in England and Canada |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Algorithm 232 - Heapsort](https://hjemmesider.diku.dk/~henglein/bib/publications/williams1964.html) | J. W. J. Williams, *CACM* 7(6): 347–348 (1964), bibliographic record | The citation of the original algorithm |

**Gaps:** no video page could be opened. The texts of Williams's and Floyd's 1964 algorithms were not opened; the ACM pages were not tried. Floyd's earlier "Treesort" algorithms were not opened.

## 13. Edmonds's matching and the "good" algorithm

**When / where:** Jack Edmonds, Operations Research Section of the National Bureau of Standards: the blossom algorithm developed in 1961 and published as "Paths, trees, and flowers", *Canadian Journal of Mathematics* 17: 449–467 (1965). Alan Cobham, "The intrinsic computational difficulty of functions", the same year.
**Atlas:** to be mapped · **Code:** [`Matching.java`](../../code/era-05-the-programmers-craft/13-matching/) · **Page:** [topic 13](13-matching/README.md)

> **Field note.** Pairing people off along the links of a network so that as many as possible have partners looks easy, and for two-sided networks the search was already understood. Add triangles and pentagons, odd cycles, and the obvious search goes round the wrong side and misses the improvement it is looking for. Edmonds saw that each odd cycle, a "blossom", could be shrunk to a single point while the search went on, and expanded again afterwards. His paper did something rarer than solve a problem: it asked what solving should mean. Trying every possibility is a finite procedure, but the possibilities grow faster than any power of the size; he called an algorithm "good" if its work grew only like a power. That distinction, polynomial or not, became a dividing line of the whole subject, and its hardest question, whether the two sides really differ, is still open.

**What hurt:** combinatorial problems whose only general method was to try every arrangement, with no agreed meaning for "efficient"; maximum matching in general graphs, where odd cycles defeated the alternating-path search that works for two-sided graphs.
**The step forward:** the blossom algorithm: shrink odd cycles found during the alternating-path search, giving the first polynomial-time algorithm for maximum matching; and the proposal that an algorithm is "good" when its running time is bounded by a polynomial in the size of the input.

**Evidence and certainty**

- Edmonds (born 5 April 1934) worked at the National Bureau of Standards (now NIST) from 1959 to 1969; "Paths, trees, and flowers", *Canadian Journal of Mathematics* 17: 449–467, introduced the blossom algorithm: "This was the first polynomial-time algorithm for maximum matching in graphs"; Edmonds "characterizes feasible problems as those solvable in polynomial time"; in 1966 he "originated the conjectures NP ≠ P and NP ∩ coNP = P"; John von Neumann Theory Prize, 1985. **Documented** ([Wikipedia, Jack Edmonds](https://en.wikipedia.org/wiki/Jack_Edmonds))
- The algorithm was developed in 1961 and published in 1965; "an odd-length cycle in the graph (blossom) is contracted to a single vertex"; the original runs in O(|E||V|²) time; "it gave the first proof that a maximum-size matching could be found using a polynomial amount of computation time", and led to a polyhedral description of the matching polytope. By Berge's lemma a matching is maximum exactly when "there is no M-augmenting path in G". **Documented** ([Wikipedia, Blossom algorithm](https://en.wikipedia.org/wiki/Blossom_algorithm))
- At NBS: "In 1959 he joined NBS, became a founding member of Alan Goldman's newly created Operations Research Section in 1961"; "Edmonds' matching algorithm was the very first instance of a good algorithm for a problem outside that mold"; Edmonds spoke of "the curse of exponentiality", since "many of the known graph-theoretical algorithms required exponential effort"; Berge's theorem (1957): "a larger matching exists not merely if, but also only if, the current matching admits an augmenting path". **Documented** ([NIST Special Publication 958, "Paths, Trees, and Flowers", essay by Christoph Witzgall and colleagues](https://nvlpubs.nist.gov/nistpubs/sp958-lide/html/140-144.html))
- Cobham (1965), "The intrinsic computational difficulty of functions", proposed P as "the set of feasibly computable problems"; Edmonds's paper is credited with "identifying P with tractable problems". **Documented** ([Wikipedia, Cobham's thesis](https://en.wikipedia.org/wiki/Cobham%27s_thesis))
- The 1965 paper was "one of the first to suggest the possibility of establishing a mathematical theory of efficient combinatorial algorithms"; Edmonds moved to the University of Waterloo in 1969. **Documented** ([INFORMS, biographical profile](https://www.informs.org/Explore/History-of-O.R.-Excellence/Biographical-Profiles/Edmonds-Jack))
- Whether Edmonds or Cobham should be credited first with polynomial time as the measure of efficiency: both published in 1965, independently as far as the opened sources say. **Conjecture** as to priority

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Blossom algorithm](https://en.wikipedia.org/wiki/Blossom_algorithm) | Wikipedia | Augmenting paths, blossoms and the running time |
| Start | [Jack Edmonds](https://en.wikipedia.org/wiki/Jack_Edmonds) | Wikipedia | The matching paper, polynomial time and the P versus NP conjectures |
| Start | [Edmonds's Blossom Algorithm](https://algorithms.discrete.ma.tum.de/graph-algorithms/matchings-blossom-algorithm/index_en.html) | Johannes Feil, Technische Universität München (2016) | An interactive applet that runs the algorithm step by step |
| Deeper | [Paths, Trees, and Flowers](https://nvlpubs.nist.gov/nistpubs/sp958-lide/html/140-144.html) | NIST Special Publication 958, essay by Christoph Witzgall and colleagues | Edmonds at the National Bureau of Standards, and why "good" algorithms mattered |
| Deeper | [Cobham's thesis](https://en.wikipedia.org/wiki/Cobham%27s_thesis) | Wikipedia | Polynomial time as the meaning of "feasible" |
| Deeper | [Jack Edmonds](https://www.informs.org/Explore/History-of-O.R.-Excellence/Biographical-Profiles/Edmonds-Jack) | INFORMS biographical profile | His career, matroids and awards |

**Original sources**

No copy of the 1965 paper could be opened (see **Gaps**).

**Gaps:** no video page could be opened. "Paths, trees, and flowers" itself and Cobham's 1965 paper were not opened; Edmonds's own wording of "good" is known here only through the NIST essay, whose text is partly garbled around that definition. Berge's 1957 paper was not opened.

## What the era leaves behind

- **Tools for writing programs.** Routines written once and called from anywhere (1), languages the machine translates for itself, defined by exact grammars (8), and memory that is handed out and taken back automatically (6). Programming becomes a craft with its own instruments.
- **Ways to organise memory.** Hash tables (4), linked lists (6), balanced search trees (11) and heaps (12): each makes a particular question (is this key here? what comes next? what is the largest?) cost a few steps, or a number of steps that grows like log n.
- **Ways to split a problem.** Work backwards and remember every partial answer (5); settle one place at a time (7); merge the two smallest (3); split around one item and sort each side (10).
- **Machines from patterns.** A pattern written in Kleene's algebra becomes a finite machine (2); a perceptron finds its own weights from examples (9).
- **What "efficient" means.** Trying every possibility is finite but hopeless; Edmonds (13) asks for algorithms whose work grows like a power of the input's size. The next era asks which problems have such algorithms at all.

Era 6 picks up in 1965: the fast Fourier transform, objects and concurrent programs, NP-completeness, and the cryptography of the 1970s.
