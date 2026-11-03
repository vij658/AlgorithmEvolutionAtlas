# Era 8 — The Web, the Genome and the Ledger: from support vector machines to Bitcoin

*Reference catalog. Thirteen developments, from 1995 to 2008.*

> **Field note from the visiting historian.** In the seventh era the species' computers joined into networks and began to learn. In this one the network becomes a Web of tens of millions of pages, which must be searched, ranked, copied to caches and cleared of duplicates; its laboratories read the species' own genome from millions of shredded fragments; its data streams past faster than it can be kept; and its computers, now thousands in one room, must work as one and agree on one history. The methods of this era are built for scale: they summarize instead of storing, sample instead of measuring everything, settle for a provable approximation, and assume that some part is always failing. Two older questions are closed along the way: whether primality can be decided without chance, and whether a computer can learn what happened a thousand steps ago.

## How to use this catalog

Every link was opened before it was listed. Links are tagged by level, so a high-school reader and a PhD scholar can both find their way in:

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

A note on videos: video sites themselves could not be opened from the environment used to build this catalog. The one video listed (topic 1) is on an MIT OpenCourseWare page that hosts it; elsewhere no such page was found, no video is listed and the topic's **Gaps** line says so. Redirects to other sites were not followed.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Support vector machines](#1-support-vector-machines) | 1964; kernels 1992; soft margin 1995 | A perceptron's line could pass close to the examples |
| 2 | [Goemans and Williamson's MAX CUT](#2-approximation-by-semidefinite-programming-goemans-and-williamsons-max-cut) | STOC 1994; journal 1995 | MAX CUT is NP-hard; the best guarantee was 1/2 |
| 3 | [Streaming sketches](#3-streaming-sketches) | 1983–1985; 1996; 2005; 2007 | Exact counts need memory for every item |
| 4 | [Consistent hashing](#4-consistent-hashing) | 1997; Chord 2001 | Hash-mod-n moves nearly every key when servers change |
| 5 | [MinHash and locality-sensitive hashing](#5-minhash-and-locality-sensitive-hashing) | 1997; 1998 | Near-duplicates among millions of pages |
| 6 | [Long short-term memory](#6-long-short-term-memory) | 1991; 1995; 1997; forget gate 1999 | Recurrent networks forgot after a few steps |
| 7 | [PageRank](#7-pagerank) | 1996; April 1998 | Keyword search returned junk |
| 8 | [Paxos](#8-paxos) | Submitted 1989 or 1990; published 1998 | Replicas must agree despite lost messages and stopped computers |
| 9 | [Genome assembly with de Bruijn graphs](#9-genome-assembly-with-de-bruijn-graphs) | 1995; 2001 | Overlap assembly is a Hamiltonian path problem |
| 10 | [PRIMES is in P](#10-primes-is-in-p) | 6 August 2002; journal 2004 | Fast primality tests used chance or unproved hypotheses |
| 11 | [MapReduce](#11-mapreduce) | December 2004 | Every big-data program handled failures its own way |
| 12 | [Compressed sensing](#12-compressed-sensing) | Preprint 2004; journal 2006 | Full-rate sampling wastes measurements on sparse signals |
| 13 | [Bitcoin's proof-of-work ledger](#13-bitcoins-proof-of-work-ledger) | 31 October 2008; 3 January 2009 | Electronic cash could be spent twice without a bank |

## 1. Support vector machines

**When / where:** Vladimir Vapnik and Alexey Chervonenkis, Institute of Control Sciences, Moscow, the "generalised portrait" method (work begun 1962, first published 1964); Bernhard Boser, Isabelle Guyon and Vladimir Vapnik, AT&T Bell Laboratories, "A training algorithm for optimal margin classifiers" (1992), the kernel trick; Corinna Cortes and Vladimir Vapnik, AT&T Bell Laboratories, Holmdel, New Jersey, "Support-vector networks", *Machine Learning* 20 (1995), the soft margin.
**Atlas:** to be mapped · **Code:** [`SupportVectorMachines.java`](../../code/era-08-the-web-the-genome-and-the-ledger/01-support-vector-machines/) · **Page:** [topic 1](01-support-vector-machines/README.md)

> **Field note.** Rosenblatt's perceptron (Era 5, topic 9) stops at the first line that separates its two kinds of examples, however close that line runs to them. In Moscow in the 1960s Vapnik and Chervonenkis asked for the best such line: the one with the widest empty street on either side. Only the examples standing on the edges of the street decide where it goes; they are the support vectors. Thirty years later, at Bell Laboratories, Boser, Guyon and Vapnik noticed that the method only ever compares two examples by a dot product, so the dot product could be swapped for another comparison, a kernel, and the straight street bent into a curved one without ever writing down the curved coordinates. Cortes and Vapnik then let a few examples stand inside the street or on the wrong side, at a price, so that the method works on data no line can separate. On handwritten digits from the US Postal Service their machines made fewer errors than the neural networks they compared against.

**What hurt:** a perceptron's line depends on the order of the examples and may pass close to them; curved boundaries needed explicit new features, whose number explodes; and real data is rarely separable without errors.
**The step forward:** the maximum-margin line, fixed by a few support vectors; kernels that replace dot products, giving curved boundaries for the computing cost of a straight one; and the soft margin, which trades margin against training errors through one constant C.

**Evidence and certainty**

- The ideas were "first proposed by V. N. Vapnik and A. Ya. Chervonenkis" as the "Generalised Portrait Method" at the Institute of Control Sciences of the Russian Academy of Sciences in Moscow; "the development of these ideas started in 1962" and they were first published in 1964; Vapnik's maximum-margin algorithm of 1963 was linear; in 1992 Boser, Guyon and Vapnik "suggested a way to create nonlinear classifiers". **Documented** ([Royal Holloway, Centre for Reliable Machine Learning, Support Vector Machines](https://cml.rhul.ac.uk/svm.html))
- "The original SVM algorithm was invented by Vladimir N. Vapnik and Alexey Ya. Chervonenkis in 1964" (marked *citation needed* on the page); in 1992 Boser, Guyon and Vapnik applied "the kernel trick to maximum-margin hyperplanes"; the soft-margin version "was proposed by Corinna Cortes and Vapnik in 1993 and published in 1995"; Platt's sequential minimal optimization (1998) "breaks the problem down into 2-dimensional sub-problems that are solved analytically". **Documented** ([Wikipedia, Support vector machine](https://en.wikipedia.org/wiki/Support_vector_machine))
- Boser, Guyon and Vapnik, AT&T Bell Laboratories (Boser later at UC Berkeley): "A training algorithm that maximizes the margin between the training patterns and the decision boundary is presented"; the solution is a combination of "the subset of training patterns that are closest to the decision boundary"; it applies to perceptrons, polynomials and radial basis functions. **Documented** ([Boser, Guyon and Vapnik 1992, on an Oregon State course page](https://classes.engr.oregonstate.edu/eecs/fall2023/ai534-400/extra/boser-1992.pdf))
- Cortes and Vapnik, AT&T Bell Labs, Holmdel, *Machine Learning* 20, 273–297 (1995; received 15 May 1993): "The support-vector network is a new learning machine for two-group classification problems", with inputs "non-linearly mapped to a very high-dimension feature space"; "We here extend this result to non-separable training data" with slack variables and a penalty constant; on the US Postal Service digits (7,300 training, 2,000 test) polynomials of degree 1 to 7 gave 12.0, 4.7, 4.4, 4.3, 4.3, 4.2 and 4.3% raw error, against 2.5% for humans and 5.1% for LeNet1; on the NIST digits a degree-4 polynomial gave 1.1%. The paper's text also says a single classifier's test error "does not exceed 1.5%", which does not match its own table. **Documented** (the table); **Disputed** (the paper's own two figures) ([Cortes and Vapnik 1995, on a University of Illinois Chicago page](https://homepages.math.uic.edu/~lreyzin/papers/cortes95.pdf))
- Winston's MIT lecture derives the method as maximizing "the width of the street" with Lagrange multipliers, with an optional kernel. **Documented** ([MIT OpenCourseWare 6.034, Lecture 16](https://www.ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/resources/lecture-16-learning-support-vector-machines))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Lecture 16: Learning: Support Vector Machines](https://www.ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/resources/lecture-16-learning-support-vector-machines) | Patrick Winston, MIT OpenCourseWare 6.034 (2010); the page hosts the video and a transcript | The widest street, derived on a blackboard |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Support Vector Machines](https://cml.rhul.ac.uk/svm.html) | Royal Holloway, University of London | The Moscow origins, 1962 to 1964 |
| Deeper | [Support vector machine](https://en.wikipedia.org/wiki/Support_vector_machine) | Wikipedia | Margins, the hinge loss, kernels and training by SMO |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Training Algorithm for Optimal Margin Classifiers](https://classes.engr.oregonstate.edu/eecs/fall2023/ai534-400/extra/boser-1992.pdf) | B. Boser, I. Guyon, V. Vapnik (1992), on an Oregon State course page | Maximum margins with kernels |
| Scholar | [Support-Vector Networks](https://homepages.math.uic.edu/~lreyzin/papers/cortes95.pdf) | C. Cortes, V. Vapnik, *Machine Learning* (1995), on a UIC page | The soft margin and the digit experiments |

**Gaps:** Vapnik and Chervonenkis's 1964 paper and Platt's 1998 SMO paper were not opened; the program trains with a simplified form of SMO. The numeric error rates in the opened copy of the 1992 paper are garbled, so none are quoted.

## 2. Approximation by semidefinite programming: Goemans and Williamson's MAX CUT

**When / where:** Michel Goemans (MIT) and David Williamson (IBM T. J. Watson Research Center, Yorktown Heights), preliminary version at the 26th ACM Symposium on Theory of Computing, Montreal, 1994; "Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming", *Journal of the ACM* 42(6), November 1995.
**Atlas:** to be mapped · **Code:** [`GoemansWilliamson.java`](../../code/era-08-the-web-the-genome-and-the-ledger/02-max-cut/) · **Page:** [topic 2](02-max-cut/README.md)

> **Field note.** Since the sixth era the species has known that some problems, MAX CUT among them, probably have no fast exact method (Era 6, topic 8). So it began to ask a weaker question: how close to the best can a fast method promise to come? For MAX CUT, splitting a network's nodes into two groups so that as many links as possible run between them, the answer had been one half, from flipping a coin for each node, and for years nobody improved the constant. In 1994 Goemans and Williamson replaced each node's choice of side by an arrow in many dimensions, found the best arrows by semidefinite programming (a relative of the linear programs of Era 7, topic 1), and then cut the arrows with a random plane through the middle. Two arrows land on opposite sides with probability equal to the angle between them over π, and that one fact gives a guarantee of 0.87856 of the best cut.

**What hurt:** for NP-hard problems an exact answer is out of reach, and the best guarantee for MAX CUT had been the 1/2 that a coin flip gives.
**The step forward:** relax the problem to unit vectors, solve the relaxation exactly in polynomial time with semidefinite programming, and round with a random hyperplane; the expected cut is at least 0.87856 of the optimum.

**Evidence and certainty**

- Goemans (MIT) and Williamson (IBM T. J. Watson), *Journal of the ACM* 42(6), November 1995, pp. 1115–1145 (received June 1994): "We present randomized approximation algorithms for the maximum cut (MAX CUT)" that "always deliver solutions of expected value at least .87856 times the optimal value"; the relaxation "can be interpreted both as a semidefinite program and as an eigenvalue minimization problem"; the rounding chooses "a random hyperplane through the origin (with r as its normal)", which separates two vectors with probability θ/π; the constant is the minimum of 2θ/(π(1 − cos θ)), which "achieves its value for θ = 2.331122..."; the earlier best was the 1/2 of Sahni and Gonzales, after which "no progress was made in improving the constant"; a preliminary version appeared at STOC (Montreal, 1994), whose derandomization "had a subtle error". **Documented** ([Goemans and Williamson 1995, MIT](https://math.mit.edu/~goemans/PAPERS/maxcut-jacm.pdf))
- The 2022 AMS Steele Prize for Seminal Contribution to Research went to Goemans and Williamson for this paper, published "in 1995 in the *Journal of the ACM*"; it "yields an approximation ratio of 0.878" and led many problems to be "studied via relaxation to semidefinite programs". **Documented** ([Cornell Bowers College, Steele Prize 2022](https://bowers.cornell.edu/news-stories/david-williamson-and-michel-goemans-receive-2022-steele-prize-seminal-contribution-research))
- Teaching notes derive the coin-flip 1/2, the vector relaxation and the random hyperplane, in which an edge is cut with probability arccos(uᵢ · uⱼ)/π. **Documented** ([Hollbach and Li, "Goemans and Williamson (1995)", University of Toronto course notes](https://www.cs.toronto.edu/~deepkush/teaching/373s22/hwk/tutorial6-max-cut.pdf))
- Khot, Kindler, Mossel and O'Donnell showed hardness results that "match the above two guarantees of Goemans and Williamson, assuming Khot's 'Unique Games Conjecture' (UGC)": if the conjecture holds, no polynomial-time algorithm beats 0.878. **Documented** (that the result is conditional on an unproven conjecture) ([Khot and O'Donnell, *Theory of Computing* 5 (2009)](https://zesty2.cs.uchicago.edu/articles/v005a004/v005a004.pdf))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Williamson and Goemans receive 2022 Steele Prize](https://bowers.cornell.edu/news-stories/david-williamson-and-michel-goemans-receive-2022-steele-prize-seminal-contribution-research) | Cornell University (2022) | What the paper did and why it mattered |
| Deeper | [Goemans and Williamson (1995): Algorithm for MAXCUT](https://www.cs.toronto.edu/~deepkush/teaching/373s22/hwk/tutorial6-max-cut.pdf) | University of Toronto course notes | The relaxation and the rounding, step by step |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Improved approximation algorithms for maximum cut and satisfiability problems using semidefinite programming](https://math.mit.edu/~goemans/PAPERS/maxcut-jacm.pdf) | M. Goemans, D. Williamson, *J. ACM* (1995) | The algorithm, the constant and the proofs |
| Scholar | [SDP gaps and UGC-hardness for Max-Cut-Gain](https://zesty2.cs.uchicago.edu/articles/v005a004/v005a004.pdf) | S. Khot, R. O'Donnell, *Theory of Computing* (2009) | Why 0.878 may be the best possible |

**Gaps:** no video page could be opened. The STOC 1994 version, Sahni and Gonzales's paper and the paper of Khot, Kindler, Mossel and O'Donnell were not opened. The program solves the relaxation with a simple low-rank coordinate method rather than a general semidefinite-programming solver, and checks its answers against exhaustive search on small graphs.

## 3. Streaming sketches

**When / where:** Philippe Flajolet (INRIA) and G. Nigel Martin (IBM, Hursley), probabilistic counting (FOCS 1983; *Journal of Computer and System Sciences* 1985); Noga Alon (Tel Aviv University), Yossi Matias (Bell Laboratories) and Mario Szegedy (AT&T Research), "The space complexity of approximating the frequency moments", STOC, May 1996 (journal version 1999); Graham Cormode and S. Muthukrishnan (Rutgers), the Count-Min sketch (*Journal of Algorithms*, April 2005); Flajolet, Fusy, Gandouet and Meunier, HyperLogLog (Analysis of Algorithms conference, 2007).
**Atlas:** to be mapped · **Code:** [`StreamingSketches.java`](../../code/era-08-the-web-the-genome-and-the-ledger/03-streaming-sketches/) · **Page:** [topic 3](03-streaming-sketches/README.md)

> **Field note.** By the 1990s the species' machines were watching more data pass than they could keep. How many different items went by? Which ones came most often? In 1996 Alon, Matias and Szegedy showed that some such questions can be answered approximately, with a few kilobytes of memory, in one pass, using random summaries they called sketches; and that others cannot. A sketch for the "repeat rate" adds up each item's count multiplied by a random plus or minus one and squares the total. Later sketches answered other questions: Count-Min (2005) estimates how often any one item appeared, never too low; HyperLogLog (2007), the descendant of Flajolet and Martin's counting of the 1980s, estimates the number of distinct items beyond a billion with about 2% error in 1.5 kilobytes.

**What hurt:** exact counts need memory proportional to the number of different items, and a stream that cannot be stored cannot be read twice.
**The step forward:** small randomized summaries, updated in one pass, that answer one question approximately with a guaranteed error, plus proofs of which questions need large memory whatever one does.

**Evidence and certainty**

- Alon (Tel Aviv University), Matias (Bell Laboratories and Tel Aviv) and Szegedy (AT&T Research); "A preliminary version of this paper appeared in Proceedings of the 28th Annual ACM Symposium on Theory of Computing (STOC), May, 1996"; "Surprisingly, it turns out that the numbers F0, F1 and F2 can be approximated in logarithmic space", while F_k for k ≥ 6 needs n^Ω(1) space; F₂ is estimated by Z², where Z sums the counts times four-wise independent random ±1 values, with E(X) = F₂ and variance at most 2F₂²; averages of 16/λ² copies are combined by a median of 2 log(1/δ) averages; any randomized approximation of the largest count "requires Ω(n) space". **Documented** ([Alon, Matias and Szegedy, author's copy](https://web.math.princeton.edu/~nalon/PDFS/amsz4.pdf))
- "The field of streaming algorithms was first formalized and popularized in a 1996 paper" by Alon, Matias and Szegedy, who won the Gödel Prize in 2005 "for their foundational contribution to streaming algorithms"; Flajolet and Martin gave the first algorithm for counting distinct elements. **Documented** ([Wikipedia, Streaming algorithm](https://en.wikipedia.org/wiki/Streaming_algorithm))
- Flajolet (INRIA) and Martin (IBM Development Laboratory, Hursley), *JCSS* 31 (1985): the algorithms "estimate the number of distinct elements in a large collection of data" in one pass with "a small additional storage", about 10% error with 64 words and 5% with 256, using the position of the lowest 1-bit of hashed values and a correction factor φ ≈ 0.77351. **Documented** ([Flajolet and Martin 1985](https://www.Gwern.net/doc/cs/algorithm/1985-flajolet.pdf))
- Lumbroso's history: Martin invented the first version of probabilistic counting at IBM UK; Flajolet and Martin presented it at FOCS 1983; LogLog (Durand and Flajolet, 2003) and HyperLogLog (2007) followed. **Documented** ([J. Lumbroso, "Philippe Flajolet's contribution to streaming algorithms", 2013](https://lumbroso.princeton.edu/talk/2013-06-20-aggregate-knowledge/talk-2013-06-20-ak-summit-flajolet-lumbroso-slides.pdf))
- Cormode (DIMACS, Rutgers) and Muthukrishnan (Rutgers and AT&T Research), *Journal of Algorithms* 55(1):58–75, April 2005: "We introduce a new sublinear space data structure-the Count-Min Sketch- for summarizing data streams"; d = ⌈ln(1/δ)⌉ rows of w = ⌈e/ε⌉ counters with pairwise-independent hashes; the estimate is the minimum over the rows, with aᵢ ≤ âᵢ and, with probability at least 1 − δ, âᵢ ≤ aᵢ + ε‖a‖₁. **Documented** ([Cormode's publication page](https://www.cs.ox.ac.uk/people/graham.cormode/pubs/html/CormodeMuthukrishnan04CMJalg.html); [the paper, on a Tufts course page](https://www.cs.tufts.edu/~nr/cs257/archive/graham-cormode/count-min.pdf))
- Flajolet, Fusy, Gandouet and Meunier (AofA 2007): standard error "typically about 1.04/√m"; cardinalities "well beyond 10⁹" with "a typical accuracy of 2% while using a memory of only 1.5 kilobytes"; registers keep the maximum position of the leftmost 1-bit; a harmonic mean with a bias constant α_m; for small cardinalities, a count of empty registers. **Documented** ([Flajolet, Fusy, Gandouet and Meunier 2007, DMTCS](https://dmtcs.episciences.org/3545/pdf))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Philippe Flajolet's contribution to streaming algorithms](https://lumbroso.princeton.edu/talk/2013-06-20-aggregate-knowledge/talk-2013-06-20-ak-summit-flajolet-lumbroso-slides.pdf) | J. Lumbroso (2013), slides | From probabilistic counting to HyperLogLog |
| Deeper | [Streaming algorithm](https://en.wikipedia.org/wiki/Streaming_algorithm) | Wikipedia | Frequency moments, heavy hitters, distinct elements and lower bounds |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Probabilistic Counting Algorithms for Data Base Applications](https://www.Gwern.net/doc/cs/algorithm/1985-flajolet.pdf) | P. Flajolet, G. N. Martin, *JCSS* (1985) | Counting distinct items with hashed bit positions |
| Scholar | [The space complexity of approximating the frequency moments](https://web.math.princeton.edu/~nalon/PDFS/amsz4.pdf) | N. Alon, Y. Matias, M. Szegedy (STOC 1996; author's copy) | Sketches, and the lower bounds |
| Scholar | [An Improved Data Stream Summary: The Count-Min Sketch and its Applications](https://www.cs.tufts.edu/~nr/cs257/archive/graham-cormode/count-min.pdf) | G. Cormode, S. Muthukrishnan (preprint of the 2005 paper) | Point queries that are never too low |
| Scholar | [HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm](https://dmtcs.episciences.org/3545/pdf) | P. Flajolet, É. Fusy, O. Gandouet, F. Meunier (2007) | Distinct counts in 1.5 kilobytes |

**Gaps:** no video page could be opened. The Gödel Prize citation was found only on an archived page that names the wrong paper's authors, so it is cited through Wikipedia. Durand and Flajolet's LogLog paper and Munro and Paterson's early streaming work were not opened.

## 4. Consistent hashing

**When / where:** David Karger, Eric Lehman, Tom Leighton, Matthew Levine, Daniel Lewin and Rina Panigrahy, MIT Laboratory for Computer Science, "Consistent hashing and random trees: distributed caching protocols for relieving hot spots on the World Wide Web", ACM Symposium on Theory of Computing, 1997; Akamai, founded 1998 by Lewin and Leighton; Chord (Stoica, Morris, Karger, Kaashoek and Balakrishnan, MIT), SIGCOMM, August 2001.
**Atlas:** to be mapped · **Code:** [`ConsistentHashing.java`](../../code/era-08-the-web-the-genome-and-the-ledger/04-consistent-hashing/) · **Page:** [topic 4](04-consistent-hashing/README.md)

> **Field note.** The Web's popular pages were swamped: when a comet struck Jupiter or an election was counted, everyone asked one server at once. Spreading copies over many caches needs a rule for which cache holds which page, and the obvious rule, hash the address and divide by the number of caches (hashing, Era 5, topic 4), has a flaw: add or remove one cache and almost every page moves. In 1997 Karger and his colleagues at MIT gave a rule that "changes minimally as the range of the function changes": put both the caches and the pages at random points on a line or circle and give each page to the nearest cache. A new cache takes over only the pages it now stands nearest to. Two of the authors founded Akamai the next year, and the same idea later placed keys on the computers of peer-to-peer networks and of large databases.

**What hurt:** with hash-mod-n placement, changing the number of servers moves nearly every key; and clients who know different sets of servers disagree about where things are.
**The step forward:** hash keys and servers onto the same circle and give each key to the next server around it; a change of servers moves only about 1/n of the keys, and several points per server even out the load.

**Evidence and certainty**

- Karger and colleagues at MIT "coined the term in a 1997 paper at the Symposium on Theory of Computing", describing it as "a way of distributing requests among a changing population of web servers"; Akamai was founded in 1998 by Daniel Lewin and F. Thomson Leighton, co-authors of the paper; on average only K/N keys are remapped when a slot is added or removed, against nearly all of them for a modular hash table; servers and items are hashed onto a circle and each item goes to the next server clockwise; "virtual nodes" even out the load; Teradata used the underlying technique in a database released in 1986 without the name; rendezvous hashing (1996) is "simpler and more general"; users include Amazon Dynamo, Apache Cassandra and others. **Documented** ([Wikipedia, Consistent hashing](https://en.wikipedia.org/wiki/Consistent_hashing))
- Karger, Lehman, Leighton, Levine, Lewin and Panigrahy, MIT Laboratory for Computer Science: "Hot spots occur any time a large number of clients wish to simultaneously access data from a single server", as at JPL during the Shoemaker–Levy 9 comet impact and at political sites on election night; "a consistent hash function is one which changes minimally as the range of the function changes", with the properties of balance, monotonicity, spread and load; buckets and items are mapped by random functions to the unit interval, each bucket at about a constant times log C points; random cache trees spread each page's requests. **Documented** ([the STOC 1997 paper, on a Brown University course page](https://cs.brown.edu/courses/csci2950-u/f09/papers/chash97stoc.pdf))
- Chord (MIT Laboratory for Computer Science, SIGCOMM, 27–31 August 2001): "given a key, it maps the key onto a node", using "a variant of consistent hashing"; keys go to the first node clockwise on an identifier circle; a finger table of at most m entries points to nodes 2^(i−1) ahead, giving O(log N) hops; "adding virtual nodes as an indirection layer can significantly improve load balance". **Documented** ([Stoica et al. 2001, on an MIT course page](https://pdos.csail.mit.edu/archive/6.824-2012/papers/stoica-chord.pdf))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Consistent hashing](https://en.wikipedia.org/wiki/Consistent_hashing) | Wikipedia | The circle, virtual nodes and where it is used |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Consistent Hashing and Random Trees](https://cs.brown.edu/courses/csci2950-u/f09/papers/chash97stoc.pdf) | D. Karger et al., STOC (1997), on a Brown course page | Hot spots, the four properties and the construction |
| Scholar | [Chord: A Scalable Peer-to-peer Lookup Service for Internet Applications](https://pdos.csail.mit.edu/archive/6.824-2012/papers/stoica-chord.pdf) | I. Stoica et al., SIGCOMM (2001), on an MIT course page | Consistent hashing without a central directory |

**Gaps:** no video page could be opened. The opened copy of the 1997 paper does not print its venue or year; they come from Wikipedia. The paper places points on the unit interval; the program and the page use the circle, as Chord and Wikipedia do. Akamai's own history was not opened.

## 5. MinHash and locality-sensitive hashing

**When / where:** Andrei Broder, Digital Equipment Corporation's Systems Research Center, Palo Alto, "On the resemblance and containment of documents", Compression and Complexity of Sequences, 1997; Broder, Steven Glassman, Mark Manasse and Geoffrey Zweig, "Syntactic clustering of the Web" (SRC Technical Note 1997-015, July 1997), on 30 million pages from an AltaVista crawl; Piotr Indyk and Rajeev Motwani (Stanford), locality-sensitive hashing, STOC 1998.
**Atlas:** to be mapped · **Code:** [`MinHashLsh.java`](../../code/era-08-the-web-the-genome-and-the-ledger/05-minhash/) · **Page:** [topic 5](05-minhash/README.md)

> **Field note.** A search engine that has fetched 30 million pages finds that many of them are copies or near-copies: in AltaVista's crawl of 1996, 12.3 million of the 30 million fell into clusters of pages that resembled each other. Comparing every page with every other is hopeless, and exact fingerprints (Era 7, topic 9) miss pages that differ in one word. At Digital's research centre in Palo Alto, Broder cut each page into overlapping runs of words, "shingles", and measured resemblance as the shared runs over all the runs. Then he made it cheap: shuffle all possible shingles at random and keep, for each page, the one that comes first. The chance that two pages keep the same shingle is exactly their resemblance. A hundred such samples, a few hundred bytes per page, were enough to cluster AltaVista's crawl. Indyk and Motwani turned such hashes, built so that similar things tend to collide, into a general method for finding near neighbours among millions of points.

**What hurt:** finding near-duplicates among millions of documents needs a similarity that tolerates small edits, and comparing every pair costs n² comparisons of long texts.
**The step forward:** a sketch of a few hundred minimum hash values per document, whose agreement estimates resemblance, and hashing designed so that similar items collide, which turns similarity search into lookups.

**Evidence and certainty**

- Broder, Digital Systems Research Center, Palo Alto: resemblance is |S(A,w) ∩ S(B,w)| / |S(A,w) ∪ S(B,w)| over sets of w-shingles; under a random permutation, the chance that the smallest element of the union lies in both sets equals the resemblance; for AltaVista "a collection of over 30,000,000 documents" was clustered at 50% resemblance into 3.6 million clusters of 12.3 million documents; "100 samples seems reasonable and 200 seems more than enough", sketches of 300 to 800 bytes. **Documented** ([Broder 1997, on a Princeton course page](https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf))
- Broder, Glassman, Manasse and Zweig, Digital Equipment Corporation's Systems Research Center (Zweig also UC Berkeley), SRC Technical Note 1997-015, 25 July 1997: 30,000,000 HTML and text documents from an AltaVista Web walk of April 1996, about 150 GB; 2.1 million clusters held only identical documents; about 10.5 CPU-days in all. **Documented** ([Syntactic Clustering of the Web, SRC Technical Note](https://archives.iw3c2.org/www2010/pubs/77977/src-tn-1997-015.pdf))
- "The scheme was published by Andrei Broder in a 1997 conference" and "initially used in the AltaVista search engine to detect duplicate web pages"; "The probability that hmin(A) = hmin(B) is true is equal to the similarity J(A,B)"; the estimate from k hash functions has "expected error is O(1/√k)"; MinHash "may be seen as an instance of locality-sensitive hashing". The page's reference gives the year as 1998 for the 1997 proceedings. **Documented** ([Wikipedia, MinHash](https://en.wikipedia.org/wiki/MinHash))
- Har-Peled, Indyk and Motwani, *Theory of Computing* 8 (2012), "based on the material from the authors' STOC'98 and FOCS'01 papers": algorithms for approximate nearest neighbours in high dimensions with space "only polynomial" and query times "sub-linear" in the size of the data. **Documented** ([Approximate Nearest Neighbor: Towards Removing the Curse of Dimensionality](https://mirror.theoryofcomputing.org/articles/v008a014/))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [MinHash](https://en.wikipedia.org/wiki/MinHash) | Wikipedia | The one-line proof and the error of k samples |
| Deeper | [Syntactic Clustering of the Web](https://archives.iw3c2.org/www2010/pubs/77977/src-tn-1997-015.pdf) | A. Broder, S. Glassman, M. Manasse, G. Zweig (1997) | What it took to cluster 30 million pages |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [On the resemblance and containment of documents](https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf) | A. Broder (1997), on a Princeton course page | Shingles, resemblance and min-wise samples |
| Scholar | [Approximate Nearest Neighbor: Towards Removing the Curse of Dimensionality](https://mirror.theoryofcomputing.org/articles/v008a014/) | S. Har-Peled, P. Indyk, R. Motwani, *Theory of Computing* (2012) | Locality-sensitive hashing, from the 1998 and 2001 papers |

**Gaps:** no video page could be opened. The opened copy of Broder's paper does not print its venue; the venue comes from Wikipedia, which dates the same reference both 1997 and 1998. Indyk and Motwani's 1998 STOC paper was not opened; it is cited through the 2012 journal version. The banding scheme for MinHash used on the topic page and in the program is the standard construction; no opened source describes it in detail.

## 6. Long short-term memory

**When / where:** Sepp Hochreiter, diploma thesis, Technische Universität München, 1991 (the vanishing gradient); Hochreiter (TU München) and Jürgen Schmidhuber (IDSIA, Lugano), technical report 1995, NIPS 1996, and "Long short-term memory", *Neural Computation* 9(8), 1735–1780, 1997; the forget gate, Gers, Schmidhuber and Cummins, 1999.
**Atlas:** to be mapped · **Code:** [`LongShortTermMemory.java`](../../code/era-08-the-web-the-genome-and-the-ledger/06-lstm/) · **Page:** [topic 6](06-lstm/README.md)

> **Field note.** Backpropagation (Era 7, topic 7) can train a network that reads a sequence one step at a time and carries a memory from step to step. But the slope it sends back through time is multiplied at every step, and in his 1991 thesis Hochreiter showed what that does: the error signal either blows up or dies away exponentially with the distance. A network could not learn that something it saw a hundred steps ago mattered now. Hochreiter and Schmidhuber's answer was a memory cell whose content is carried forward unchanged, a "constant error carousel", with gates that learn when to let new input in and when to let the content out. Their 1997 network bridged time lags of more than 1,000 steps on tasks where the older methods failed at 10. A gate for forgetting was added in 1999, and in that form the cell later ran Google's speech recognition and machine translation.

**What hurt:** recurrent networks trained by backpropagation through time could not learn dependencies more than a few steps long, because the error signal vanishes or explodes exponentially with the time lag.
**The step forward:** a memory cell with a self-connection of weight one, so the error flows back unchanged, and multiplicative gates that learn to open and close access to it; the cost per step and weight stays O(1).

**Evidence and certainty**

- Hochreiter (Technische Universität München) and Schmidhuber (IDSIA, Lugano), *Neural Computation* 9(8), 1735–1780 (1997): LSTM can learn to "bridge minimal time lags in excess of 1000 discrete time steps" by enforcing constant error flow through "constant error carrousels"; "Multiplicative gate units learn to open and close access to the constant error flow"; "LSTM is local in space and time; its computational complexity per time step and weight is O(1)"; with backpropagation through time, error signals tend "to either (1) blow up or (2) vanish", as Hochreiter's 1991 analysis showed; on the hardest noise-free task "LSTM solves it, while BPTT and RTRL already fail in case of 10-step minimal time lags". **Documented** ([Hochreiter and Schmidhuber 1997](https://papers.baulab.info/papers/Hochreiter-1997.pdf))
- "Sepp Hochreiter's 1991 German diploma thesis analyzed the vanishing gradient problem"; an early version of LSTM appeared in a 1995 technical report and at NIPS 1996; the 1997 *Neural Computation* paper is "the most commonly used reference point"; Gers, Schmidhuber and Cummins introduced the forget gate in 1999, "the most commonly used version today", and peephole connections in 2000; in 2015 Google used an LSTM for speech recognition on Google Voice, and in 2016 in Google Neural Machine Translation. **Documented** ([Wikipedia, Long short-term memory](https://en.wikipedia.org/wiki/Long_short-term_memory))
- The gates as now written: input, forget and output gates are sigmoids of the input and the previous hidden state; Cₜ = Fₜ ⊙ Cₜ₋₁ + Iₜ ⊙ C̃ₜ and Hₜ = Oₜ ⊙ tanh(Cₜ); the memory cell is "a node with a self-connected recurrent edge of fixed weight 1"; Hochreiter "had articulated this problem as early as 1991". **Documented** ([Dive into Deep Learning, section 10.1, Long Short-Term Memory](https://d2l.ai/chapter_recurrent-modern/lstm.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Long Short-Term Memory (LSTM)](https://d2l.ai/chapter_recurrent-modern/lstm.html) | *Dive into Deep Learning*, section 10.1 | The gates, with equations and code |
| Deeper | [Long short-term memory](https://en.wikipedia.org/wiki/Long_short-term_memory) | Wikipedia | From the 1991 thesis to the forget gate and wide use |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Long Short-Term Memory](https://papers.baulab.info/papers/Hochreiter-1997.pdf) | S. Hochreiter, J. Schmidhuber, *Neural Computation* (1997) | The constant error carousel and the long-lag experiments |

**Gaps:** no video page could be opened, and Olah's well-known 2015 blog post could not be reached. Hochreiter's 1991 thesis, the 1995 report and the 1999 forget-gate paper were not opened. The program uses the cell with a forget gate (the 1999 form), not the 1997 cell, and its tasks are small versions of the paper's long-lag tasks, not the paper's own.

## 7. PageRank

**When / where:** Larry Page and Sergey Brin, Stanford University, a research project from 1996; Brin and Page, "The anatomy of a large-scale hypertextual Web search engine", Seventh International World Wide Web Conference, Brisbane, April 1998 (*Computer Networks and ISDN Systems* 30); Jon Kleinberg's hubs and authorities (HITS), *Journal of the ACM*, 1999.
**Atlas:** to be mapped · **Code:** [`PageRank.java`](../../code/era-08-the-web-the-genome-and-the-ledger/07-pagerank/) · **Page:** [topic 7](07-pagerank/README.md)

> **Field note.** By 1998 the Web held tens of millions of pages, and search engines that matched keywords returned, in Brin and Page's words, "junk results" that "often wash out any results that a user is interested in". Two students at Stanford counted something else: the links. A page is important if important pages link to it, which sounds circular, and is: the ranks are the solution of one enormous system of equations. Brin and Page pictured a random surfer who clicks links forever and, now and then, gets bored and jumps to a random page; a page's PageRank is the share of time the surfer spends there. Multiplying the ranks by the link matrix again and again (the power method) converges, with the damping set at 0.85, the ranks of 26 million pages took a few hours on one workstation. The search engine built on it was called Google.

**What hurt:** keyword matching could not tell an authoritative page from a page stuffed with the right words, and the Web was too large and changed too fast for human-made directories.
**The step forward:** rank by the link structure: the stationary distribution of a random surfer with damping, computed by repeated multiplication with a sparse matrix.

**Evidence and certainty**

- Brin and Page, Computer Science Department, Stanford University, *Computer Networks and ISDN Systems* 30 (1998) 107–117: PR(A) = (1 − d) + d (PR(T₁)/C(T₁) + … + PR(Tₙ)/C(Tₙ)), "We usually set d to 0.85"; a random surfer follows links, never going back, until bored, and then jumps to a random page; at least 24 million pages, link maps with "as many as 518 million of these hyperlinks"; PageRank "can be calculated using a simple iterative algorithm", for 26 million pages "in a few hours on a medium size workstation"; keyword engines return "junk results". **Documented** ([Brin and Page 1998, on a UC Irvine course page](https://www.ics.uci.edu/~djp3/classes/2008_01_01_INF141/Materials/brin1998.pdf))
- PageRank was developed by Page and Brin at Stanford "as a research project" from 1996; Robin Li's RankDex (1996) used a related page-ranking; the patent, assigned to Stanford and granted in 2001, earned Stanford 1.8 million Google shares, sold in 2005 for $336 million; the normalized form PR(u) = (1 − d)/N + d Σ PR(v)/L(v) sums to one, which the original paper confused with a variant that sums to N; dangling pages are treated as linking to every page; on a 322-million-link network the computation converged in 52 iterations. **Documented** ([Wikipedia, PageRank](https://en.wikipedia.org/wiki/PageRank))
- The Google matrix, the power method and its speed: "Brin and Page report that 50 - 100 iterations are required" for a good approximation; a damping value near 0.85 is a compromise between respecting the link structure and fast convergence; "we pretend that a dangling node has a link to every other page". **Documented** ([D. Austin, "How Google Finds Your Needle in the Web's Haystack", AMS Feature Column, December 2006](https://www.ams.org/featurecolumn/archive/pagerank.html)). The iteration counts differ between the two secondary sources (52 against 50 to 100). **Disputed**
- Kleinberg's HITS (*Journal of the ACM*, 1999): a good hub "pointed to many other pages", a good authority "is linked by many different hubs"; the two scores reinforce each other and are normalized after every iteration; unlike PageRank, HITS works on a set of pages chosen for each query. **Documented** ([Wikipedia, HITS algorithm](https://en.wikipedia.org/wiki/HITS_algorithm))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [How Google Finds Your Needle in the Web's Haystack](https://www.ams.org/featurecolumn/archive/pagerank.html) | D. Austin, AMS Feature Column (2006) | The random surfer and the power method, from first principles |
| Deeper | [PageRank](https://en.wikipedia.org/wiki/PageRank) | Wikipedia | History, the normalized formula, dangling pages and convergence |
| Deeper | [HITS algorithm](https://en.wikipedia.org/wiki/HITS_algorithm) | Wikipedia | Hubs and authorities, the query-time alternative |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Anatomy of a Large-Scale Hypertextual Web Search Engine](https://www.ics.uci.edu/~djp3/classes/2008_01_01_INF141/Materials/brin1998.pdf) | S. Brin, L. Page (1998), on a UC Irvine course page | The formula, d = 0.85, and the prototype of Google |

**Gaps:** no video page could be opened. The 1999 Stanford technical report by Page, Brin, Motwani and Winograd and Kleinberg's paper were not opened. Wikipedia's PageRank article names four authors for the *Anatomy* paper, which lists two; the paper is followed here.

## 8. Paxos

**When / where:** Leslie Lamport, "The Part-Time Parliament", written and submitted around 1989–1990, published in *ACM Transactions on Computer Systems* 16(2), May 1998; "Paxos Made Simple", 2001.
**Atlas:** to be mapped · **Code:** [`Paxos.java`](../../code/era-08-the-web-the-genome-and-the-ledger/08-paxos/) · **Page:** [topic 8](08-paxos/README.md)

> **Field note.** The Byzantine generals (Era 7, topic 3) agreed despite traitors, but they marched in lockstep rounds. Real networks have no rounds: messages are late, lost or repeated, and a computer that has stopped answering may only be slow. Lamport described a solution as the lost records of a parliament on the Greek island of Paxos, whose part-time legislators kept wandering out of the chamber, yet still passed one consistent set of decrees. A proposer first asks a majority of acceptors to promise to ignore older ballots, and must then propose the value of the highest ballot any of them had already accepted; because any two majorities share a member, once a value is chosen no later ballot can choose another. The referees found the paper "mildly interesting, though not very important"; it waited eight years for publication, and then became one of the ways the species' largest computer systems keep their copies in agreement.

**What hurt:** keeping several copies of a service consistent when messages can be delayed, lost or duplicated and computers can stop, with no way to tell a crashed computer from a slow one.
**The step forward:** ballots with numbers, two phases (promise, then accept), and majorities that must overlap: safety holds whatever the timing, and progress needs only one distinguished proposer at a time.

**Evidence and certainty**

- Lamport's commentary: the paper was "first submitted in 1990, setting a personal record for publication delay"; "All three referees said that the paper was mildly interesting, though not very important"; it appeared in May 1998 in *ACM TOCS* 16(2) with notes by Keith Marzullo; colleagues at SRC found the algorithm useful before it was published; the name Paxos was suggested by Leo Guibas; the paper won an ACM SIGOPS Hall of Fame Award in 2012. **Documented** ([Microsoft Research, The Part-Time Parliament](https://www.microsoft.com/en-us/research/publication/part-time-parliament/))
- The published paper: "Recent archaeological discoveries on the island of Paxos"; Marzullo's note that the paper "was recently discovered behind a filing cabinet in the TOCS editorial office"; legislators "continually wandered in and out"; the conditions B1–B3 on ballots, including that "The quorums of any two ballots in B have at least one priest in common". **Documented** ([Lamport 1998, on a Princeton course page](https://www.cs.princeton.edu/courses/archive/spring13/cos598C/lamport-paxos.pdf))
- "The Paxos algorithm, when presented in plain English, is very simple" (1 November 2001): proposers, acceptors and learners; "Because any two majorities have at least one acceptor in common, this works if an acceptor can accept at most one value"; phase 1, a prepare request with number n and "a promise not to accept any more proposals numbered less than n"; phase 2, a value that is "the value of the highest-numbered proposal among the responses"; two proposers can keep issuing higher numbers so that none is chosen, so "a distinguished proposer must be selected", and by Fischer, Lynch and Paterson's result that choice "must use either randomness or real time". **Documented** ([Lamport, Paxos Made Simple, on an MIT course page](https://pdos.csail.mit.edu/archive/6.824-2012/papers/paxos-simple.pdf))
- Paxos was "first submitted in 1989" and published in 1998; Oki and Liskov's Viewstamped Replication (1988) is a similar protocol; "Paxos guarantees safety (consistency)" but "is not guaranteed to terminate"; 2f + 1 acceptors tolerate f failures; it is used in Google's Chubby lock service, Spanner and Megastore, and elsewhere. **Documented** ([Wikipedia, Paxos (computer science)](https://en.wikipedia.org/wiki/Paxos_(computer_science))). The submission year: 1990 in Lamport's own commentary, 1989 in Wikipedia. **Disputed**

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Part-Time Parliament, with Lamport's commentary](https://www.microsoft.com/en-us/research/publication/part-time-parliament/) | Microsoft Research | Why the paper took eight years, in the author's words |
| Deeper | [Paxos Made Simple](https://pdos.csail.mit.edu/archive/6.824-2012/papers/paxos-simple.pdf) | L. Lamport (2001), on an MIT course page | The algorithm in plain English, in eleven pages |
| Deeper | [Paxos (computer science)](https://en.wikipedia.org/wiki/Paxos_(computer_science)) | Wikipedia | Variants, guarantees and where it runs |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Part-Time Parliament](https://www.cs.princeton.edu/courses/archive/spring13/cos598C/lamport-paxos.pdf) | L. Lamport, *ACM TOCS* (1998), on a Princeton course page | The parliament of Paxos and its proofs |

**Gaps:** no video page could be opened. Oki and Liskov's paper and Fischer, Lynch and Paterson's paper were not opened. The Raft paper, which compares itself with Paxos, could not be fetched. The program checks single-decree Paxos only, by exhaustive search on a small configuration and by random runs, not the multi-decree protocol.

## 9. Genome assembly with de Bruijn graphs

**When / where:** Ramana Idury and Michael Waterman, University of Southern California, "A new algorithm for DNA sequence assembly", *Journal of Computational Biology* 2(2), 1995; Pavel Pevzner and Haixu Tang (University of California, San Diego) and Waterman, "An Eulerian path approach to DNA fragment assembly", *PNAS* 98(17), 14 August 2001; Velvet (Daniel Zerbino and Ewan Birney, European Bioinformatics Institute), *Genome Research*, 2008.
**Atlas:** to be mapped · **Code:** [`GenomeAssembly.java`](../../code/era-08-the-web-the-genome-and-the-ledger/09-genome-assembly/) · **Page:** [topic 9](09-genome-assembly/README.md)

> **Field note.** To read a genome the species could only read short pieces of it, from many copies broken at random places, like many copies of a book passed through shredders with different cutters. Putting the pieces back means finding a path through them. Treated the obvious way, each piece a point and each overlap a link, the path must visit every point once: a Hamiltonian path, an NP-complete problem (Era 6, topic 8), and the repeats in a genome make it worse. Idury and Waterman, then Pevzner, Tang and Waterman, cut every piece into all its words of length k and made each word a link between its first k − 1 letters and its last k − 1 letters. Now the genome is a path that uses every link once, an Eulerian path, the problem Euler settled for the bridges of Königsberg in 1736 (Era 3, topic 7), which takes linear time. Repeats still make several paths possible, and no method can assemble through a perfect repeat longer than the pieces.

**What hurt:** assembling millions of overlapping reads by their overlaps leads to a Hamiltonian path problem, and repeats in the genome cause wrong joins.
**The step forward:** the de Bruijn graph of the reads' k-letter words, in which the genome is an Eulerian path, found in linear time; errors are cleaned first by discarding rare words.

**Evidence and certainty**

- Idury and Waterman, Departments of Mathematics and Molecular Biology, University of Southern California, *Journal of Computational Biology* 2(2), 291–306 (1995): reads and their reverse complements are cut into k-tuples; vertices are the distinct (k − 1)-tuples and each k-tuple is an edge from its prefix to its suffix; a walk through the edges, "not an exact Eulerian tour, but a variation of it", reconstructs the sequence; ambiguous repeats are left as an "irreducible sequence graph"; with k = 15 on simulated data with 0.5% to 3% errors, more than 99.8% of bases were called correctly. **Documented** ([Idury and Waterman 1995, on a Brown University course page](https://cs.brown.edu/courses/csci1820/spring-2022/resources/Idury_Waterman_1995.pdf))
- Pevzner, Tang (UC San Diego) and Waterman (USC), *PNAS* 98(17):9748–9753, 14 August 2001: assembly traditionally followed the "overlap–layout–consensus" paradigm, a Hamiltonian path problem, and "there is still no polynomial algorithm for the solution of the notorious 'repeat problem'"; in the de Bruijn graph assembly becomes an Eulerian path problem, with read-path constraints added back as the Eulerian Superpath Problem; correcting reads with the spectrum of solid l-tuples reduces errors "by a factor of 35–50"; on the *Neisseria meningitidis* project their EULER gave 149 contigs with none misassembled, against 160 (17 misassembled) for Phrap. **Documented** ([Pevzner, Tang and Waterman 2001, PubMed Central](https://pmc.ncbi.nlm.nih.gov/articles/PMC55524))
- Assembly is "aligning and merging fragments from a longer DNA sequence", like shredding copies of a book; Celera Assembler and Arachne assembled the fruit fly in 2000 and the human genome a year later; overlap–layout–consensus was "typical of the Sanger-data assemblers", the de Bruijn approach is "most widely applied to the short reads"; "It is impossible to assemble through a perfect repeat that is longer than the maximum read length". **Documented** ([Wikipedia, Sequence assembly](https://en.wikipedia.org/wiki/Sequence_assembly))
- Velvet: "Algorithms for de novo short read assembly using de Bruijn graphs", Zerbino and Birney, EMBL-EBI, *Genome Research* 18(5):821–829 (2008). **Documented** ([Genome Research](https://genome.cshlp.org/content/18/5/821))
- Exercise: build the de Bruijn graph of a set of reads and their reverse complements, with an edge from r[1:k] to r[2:k+1] for each (k+1)-mer. **Documented** ([Rosalind, Constructing a De Bruijn Graph](https://rosalind.info/problems/dbru))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Sequence assembly](https://en.wikipedia.org/wiki/Sequence_assembly) | Wikipedia | Shotgun reads, the two approaches, and the repeat limit |
| Start | [Constructing a De Bruijn Graph](https://rosalind.info/problems/dbru) | Rosalind | Build one yourself |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A New Algorithm for DNA Sequence Assembly](https://cs.brown.edu/courses/csci1820/spring-2022/resources/Idury_Waterman_1995.pdf) | R. Idury, M. Waterman, *J. Comput. Biol.* (1995), on a Brown course page | The k-tuple graph and its walk |
| Scholar | [An Eulerian path approach to DNA fragment assembly](https://pmc.ncbi.nlm.nih.gov/articles/PMC55524) | P. Pevzner, H. Tang, M. Waterman, *PNAS* (2001) | Hamiltonian against Eulerian, and EULER's results |
| Scholar | [Velvet: Algorithms for de novo short read assembly using de Bruijn graphs](https://genome.cshlp.org/content/18/5/821) | D. Zerbino, E. Birney, *Genome Research* (2008) | The de Bruijn method for short reads |

**Gaps:** no video page could be opened. Compeau, Pevzner and Tesler's 2011 explainer and a University of Washington lecture could not be opened (a verification page and a login page). The Velvet page opened only its title and keywords. N. G. de Bruijn's own paper was not opened. The program's genomes are random, not real.

## 10. PRIMES is in P

**When / where:** Manindra Agrawal, Neeraj Kayal and Nitin Saxena, Department of Computer Science and Engineering, Indian Institute of Technology Kanpur, "PRIMES is in P", preprint dated 6 August 2002; *Annals of Mathematics* 160(2), 781–793, 2004; Gödel Prize and Fulkerson Prize, 2006.
**Atlas:** to be mapped · **Code:** [`AksPrimality.java`](../../code/era-08-the-web-the-genome-and-the-ledger/10-primes-is-in-p/) · **Page:** [topic 10](10-primes-is-in-p/README.md)

> **Field note.** Since the sixth era the species had checked primes by flipping coins: Solovay and Strassen's test (Era 6, topic 10) and its relatives can call a composite number prime only with a probability that can be made tiny, but not zero. The deterministic methods were either limited to special numbers, or had no proved polynomial bound, or depended on an unproved hypothesis. In August 2002 three computer scientists at Kanpur posted a short paper with a test that has all four virtues at once: it works for every number, always gives the right answer, runs in time polynomial in the number of digits, and rests on nothing unproved. Its heart is an old fact: n is prime exactly when (x − a)ⁿ equals xⁿ − a with every coefficient taken modulo n. Checking that directly takes n steps; their idea was to check it only modulo a small polynomial xʳ − 1, for a few values of a, and to prove that this is enough. The test is not used in practice; what it changed is what is known.

**What hurt:** every fast primality test was probabilistic, limited to special forms, or relied on the unproved generalized Riemann hypothesis; whether primality could be decided in deterministic polynomial time was open.
**The step forward:** test the polynomial identity (x − a)ⁿ ≡ xⁿ − a modulo (xʳ − 1, n) for a small r and a few a; a counting argument proves that only primes (and perfect powers, removed first) pass, in time polynomial in log n.

**Evidence and certainty**

- Agrawal, Kayal and Saxena, IIT Kanpur, 6 August 2002: "We present a deterministic polynomial-time algorithm that determines whether an input number n is prime or composite"; for a coprime to p, p is prime if and only if (x − a)^p ≡ (x^p − a) (mod p); the algorithm rejects perfect powers, finds a suitable prime r, checks gcds, and tests the congruence modulo (x^r − 1, n) for a = 1 to 2√r log n; its time is Õ(log¹² n), with a conjectured Õ(log⁶ n) and possibly Õ(log³ n). **Documented** ([the August 2002 preprint, IIT Kanpur](https://www.cse.iitk.ac.in/users/nitin/papers/aug02.pdf))
- *Annals of Mathematics* 160(2), 781–793 (2004): "an unconditional deterministic algorithm" that runs in polynomial time. **Documented** ([Annals of Mathematics](https://annals.math.princeton.edu/2004/160-2/p12))
- The 2006 Gödel Prize to Agrawal, Kayal and Saxena: earlier polynomial-time tests "were based on probabilistic methods or they relied on an unproven assumption"; "the arguments come in a brilliantly simple manner; they remain completely elementary". **Documented** ([2006 Gödel Prize, SIGACT (archived page)](https://www.2016.sigact.hosting.acm.org/Prizes/Godel/2006.html))
- AKS is the first primality-proving algorithm "simultaneously general, polynomial-time, deterministic, and unconditionally correct"; earlier methods "achieved three of these properties at most"; the version now usually presented takes the smallest r whose multiplicative order modulo r exceeds (log₂ n)²; the authors won the Gödel and Fulkerson Prizes in 2006; the test is "of immense theoretical importance" but "not used in practice, rendering it a galactic algorithm"; for 64-bit inputs Baillie–PSW is deterministic and far faster. **Documented** ([Wikipedia, AKS primality test](https://en.wikipedia.org/wiki/AKS_primality_test))
- Granville's survey of the result opens with Gauss, *Disquisitiones Arithmeticae* (1801), article 329, on the problem of distinguishing primes from composites. **Documented** ([A. Granville, "It is easy to determine whether a given integer is prime", *Bull. AMS* 42 (2005)](https://www.ams.org/bull/2005-42-01/S0273-0979-04-01037-7/))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [AKS primality test](https://en.wikipedia.org/wiki/AKS_primality_test) | Wikipedia | The four properties, the algorithm and a worked example |
| Deeper | [It is easy to determine whether a given integer is prime](https://www.ams.org/bull/2005-42-01/S0273-0979-04-01037-7/) | A. Granville, *Bulletin of the AMS* (2005) | A mathematician's account of the proof and its background |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [PRIMES is in P (preprint, 6 August 2002)](https://www.cse.iitk.ac.in/users/nitin/papers/aug02.pdf) | M. Agrawal, N. Kayal, N. Saxena, IIT Kanpur | The version that was announced |
| Scholar | [PRIMES is in P](https://annals.math.princeton.edu/2004/160-2/p12) | *Annals of Mathematics* 160 (2004) | The published version |

**Gaps:** no video page could be opened. The preprint's algorithm (a prime r with a large prime factor of r − 1) differs in detail from the published one; the program follows the version given on Wikipedia (the smallest r with large order). Lenstra and Pomerance's faster variant was not opened. The *Annals* page's "received" date (24 January 2002) is earlier than the August 2002 preprint and is not used.

## 11. MapReduce

**When / where:** Jeffrey Dean and Sanjay Ghemawat, Google, "MapReduce: Simplified Data Processing on Large Clusters", Sixth Symposium on Operating System Design and Implementation (OSDI), San Francisco, December 2004; Apache Hadoop, an open-source implementation.
**Atlas:** to be mapped · **Code:** [`MapReduce.java`](../../code/era-08-the-web-the-genome-and-the-ledger/11-mapreduce/) · **Page:** [topic 11](11-mapreduce/README.md)

> **Field note.** A search company must run computations over data far too large for one computer, on clusters of cheap computers, any of which may fail. Writing such a program by hand means handling the splitting of the data, the scheduling, the network, and the failures, over and over. Dean and Ghemawat at Google noticed that many of their jobs had one shape, borrowed from the map and reduce of Lisp and other functional languages: apply a function to every record to make key–value pairs, group the pairs by key, and combine each group. A programmer writes those two functions; the library spreads them over the machines, and when a machine dies it simply runs that machine's pieces again, which is safe because the functions have no side effects. Slow machines are handled the same way, by running a backup copy of the last few pieces: without backups, their sort took 44% longer. By 2004 more than a thousand such jobs ran on Google's clusters every day.

**What hurt:** programs that process huge data on thousands of failure-prone computers had to manage distribution, scheduling and fault tolerance themselves, and each one did it differently.
**The step forward:** a restricted programming model, map and reduce, whose deterministic, side-effect-free tasks can be scheduled, moved and re-executed by a library, which hides the distribution.

**Evidence and certainty**

- Dean and Ghemawat, Google, OSDI 2004: MapReduce is "a programming model and an associated implementation for processing and generating large data sets"; programs are "automatically parallelized and executed on a large cluster of commodity machines"; the map function emits intermediate key/value pairs and reduce merges all values for one key, as in word count; the input is split into M pieces and the keys into R pieces "(e.g., hash(key) mod R)"; "Completed map tasks are re-executed on a failure"; the master schedules backup executions of in-progress tasks near the end, and "the sort program described in Section 5.3 takes 44% longer to complete when the backup task mechanism is disabled"; "upwards of one thousand MapReduce jobs are executed on Google's clusters every day"; the sort benchmark ran on "approximately 1800 machines". **Documented** ([Dean and Ghemawat 2004, on a Cornell course page](https://courses.cs.cornell.edu/cs5410/2008fa/Readings/mapreduce-osdi04.pdf))
- "Our abstraction is inspired by the map and reduce primitives present in Lisp and many other functional languages"; Apache Hadoop is a popular open-source implementation; Google's patent was granted in 2010; by 2014 Google had stopped using MapReduce as its primary model ("We don't really use MapReduce anymore", Urs Hölzle); DeWitt and Stonebraker called it "a major step backwards". **Documented** ([Wikipedia, MapReduce](https://en.wikipedia.org/wiki/MapReduce))
- MIT's distributed-systems course (6.5840, 2026, lecture 1): MapReduce aims to be "easy for non-specialist programmers", "MR manages, and hides, all aspects of distribution!", "Coordinator re-runs just the failed Map()s and Reduce()s", and "Map and Reduce should be pure deterministic functions"; in 2004 the shuffle was limited by the network. **Documented** ([MIT 6.5840 lecture notes, Introduction](https://pdos.csail.mit.edu/6.824/notes/l01.txt))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [MIT 6.5840, Lecture 1: Introduction](https://pdos.csail.mit.edu/6.824/notes/l01.txt) | F. Kaashoek, R. Morris (2026), lecture notes | MapReduce as the first example of a distributed system |
| Deeper | [MapReduce](https://en.wikipedia.org/wiki/MapReduce) | Wikipedia | Origins, Hadoop, criticism and decline |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [MapReduce: Simplified Data Processing on Large Clusters](https://courses.cs.cornell.edu/cs5410/2008fa/Readings/mapreduce-osdi04.pdf) | J. Dean, S. Ghemawat, OSDI (2004), on a Cornell course page | The model, the implementation and the measurements |

**Gaps:** no video page could be opened (the MIT course's notes page opened, not its videos). The Google File System paper, on which MapReduce relies, was not opened. The program simulates a cluster on one computer, with simulated time; its timings are not measurements of real machines.

## 12. Compressed sensing

**When / where:** Emmanuel Candès (Caltech), Justin Romberg (Caltech) and Terence Tao (UCLA), "Robust uncertainty principles: exact signal reconstruction from highly incomplete frequency information", preprint dated 10 June 2004, *IEEE Transactions on Information Theory* 52(2), February 2006; David Donoho (Stanford), "Compressed sensing", 2006.
**Atlas:** to be mapped · **Code:** [`CompressedSensing.java`](../../code/era-08-the-web-the-genome-and-the-ledger/12-compressed-sensing/) · **Page:** [topic 12](12-compressed-sensing/README.md)

> **Field note.** The sampling theorem of Nyquist and Shannon tells the species how often to measure a signal to capture it. Yet most of what is measured is thrown away again by compression, because most signals are sparse: a few strong components and a great deal of near-nothing. In 2004 Candès, experimenting with a known trick, minimizing the sum of absolute values (the ℓ1 norm), found it sharpened a blurry image remarkably well. In the paper that followed, with Romberg and Tao, a test image known only along 22 lines through its Fourier transform came back exactly, and they proved why: if a signal has only k nonzero entries, then about k log N random measurements determine it, and a convex program, essentially a linear program (Era 7, topic 1), finds it. The obvious alternative, the smallest solution in the ordinary least-squares sense, smears the answer over every entry. The idea has since been put to work on shorter MRI scans and on a camera with a single pixel.

**What hurt:** the sampling theorem's rate wastes measurements on sparse signals, and with fewer measurements than unknowns the equations have infinitely many solutions.
**The step forward:** random (incoherent) measurements and ℓ1 minimization: among all signals that agree with the measurements, the one with the smallest sum of absolute values is, with high probability, exactly the sparse one.

**Evidence and certainty**

- Candès, Romberg (Caltech) and Tao (UCLA), dated 10 June 2004: "exact recovery may be obtained by solving a convex optimization problem", minimizing the ℓ1 norm subject to the observed Fourier coefficients; recovery holds, with probability at least 1 − O(N^−M), when the number of nonzero entries is below about |Ω|/(29.6(M + 1) log N); the Logan–Shepp phantom, with "512 samples along each of 22 radial lines", is recovered exactly by total-variation minimization. **Documented** ([Candès, Romberg and Tao, arXiv math/0409186](https://arxiv.org/pdf/math/0409186))
- The journal version: *IEEE Transactions on Information Theory* 52(2), 489–509, February 2006. **Documented** ([Caltech Authors record](https://authors.library.caltech.edu/records/4xtrg-6sy14))
- Compressed sensing recovers signals from "far fewer samples than required by the Nyquist–Shannon sampling theorem" by exploiting sparsity and incoherence; "Around 2004" Candès, Romberg, Tao and Donoho showed this; earlier ℓ1 work includes seismology in the 1970s, matching pursuit (1993), the LASSO (1996) and basis pursuit (1998); it speeds up MRI and makes single-pixel cameras possible (Rice University; a lensless camera at Bell Labs). **Documented** ([Wikipedia, Compressed sensing](https://en.wikipedia.org/wiki/Compressed_sensing))
- Candès found the effect by chance in 2004 while using ℓ1 minimization on a blurry image, with a result "remarkably clear" (MAA's summary of Jordan Ellenberg's article in *Wired*, 22 February 2010). **Documented** (as a magazine account) ([MAA Math News, 26 March 2010](https://maa.org/news/math-news/fill-in-the-blanks-using-math-to-turn-lo-res-datasets-into-hi-res-samples))
- Candès's talk "Compressive Sensing", Stanford EE Computer Systems Colloquium, 20 October 2010: the theory could change analog-to-digital conversion, digital optics, MRI and seismics. **Documented** ([Stanford EE380 abstract](https://web.stanford.edu/class/ee380/Abstracts/101020.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Fill in the Blanks: Using Math to Turn Lo-Res Datasets Into Hi-Res Samples](https://maa.org/news/math-news/fill-in-the-blanks-using-math-to-turn-lo-res-datasets-into-hi-res-samples) | MAA Math News (2010), on J. Ellenberg's *Wired* article | How the discovery happened |
| Deeper | [Compressed sensing](https://en.wikipedia.org/wiki/Compressed_sensing) | Wikipedia | Sparsity, incoherence, ℓ1 and applications |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Robust Uncertainty Principles](https://arxiv.org/pdf/math/0409186) | E. Candès, J. Romberg, T. Tao (2004; journal 2006) | The theorem and the 22-line phantom |

**Gaps:** no video page could be opened; the 2010 Stanford talk's page has no video. Donoho's "Compressed sensing" paper was found only in an older abridged form and is not cited. Ellenberg's *Wired* article itself was not opened; MAA's summary of it was. The 22 radial lines and the 2004 date are the paper's; the claim that the discovery came "by chance" is the magazine's. The program uses random Gaussian measurements, not Fourier samples, and solves the ℓ1 problem as a linear program.

## 13. Bitcoin's proof-of-work ledger

**When / where:** Satoshi Nakamoto, "Bitcoin: A Peer-to-Peer Electronic Cash System", announced on the Cryptography Mailing List on 31 October 2008; the domain bitcoin.org registered 18 August 2008; the network started with the genesis block of 3 January 2009; the first transaction, to Hal Finney, 12 January 2009. Adam Back's hashcash, the proof of work it reuses, dates from 1997.
**Atlas:** to be mapped · **Code:** [`Bitcoin.java`](../../code/era-08-the-web-the-genome-and-the-ledger/13-bitcoin/) · **Page:** [topic 13](13-bitcoin/README.md)

> **Field note.** Digital money has an obvious flaw: a file can be copied, so a coin can be spent twice, and the usual cure is a trusted bank that keeps the one true ledger. In October 2008, someone signing as Satoshi Nakamoto posted a design for a ledger with no bank. Everyone keeps a copy. Blocks of transactions are chained by hashes, each holding the Merkle root of its transactions (Era 7, topic 2), and a block counts only if its hash begins with many zero bits, which can be found only by trying nonce after nonce, with work that doubles for every extra zero bit: a proof of work, borrowed from hashcash. Honest computers always extend the longest chain. To rewrite history an attacker must redo the work of every later block and then overtake the honest majority, and Nakamoto calculated how fast that chance falls: with a tenth of the computing power, an attacker who is 5 blocks behind succeeds with probability below 0.1%. In this book's terms it is a kind of Byzantine agreement (Era 7, topic 3) among strangers, with votes paid for in computation.

**What hurt:** electronic cash without a trusted third party could be double-spent, and agreement protocols needed a known list of participants.
**The step forward:** a public chain of blocks, each sealed by a proof of work over the previous block's hash and a Merkle root of its transactions; nodes follow the chain with the most work, and an attacker's chance of catching up from z blocks behind falls exponentially in z.

**Evidence and certainty**

- Nakamoto's paper: "A purely peer-to-peer version of electronic cash would allow online payments to be sent directly"; secure "As long as a majority of CPU power is controlled by nodes that are not cooperating to attack the network"; "The problem of course is the payee can't verify that one of the owners did not double-spend the coin"; a block's SHA-256 hash must begin with a number of zero bits, "similar to Adam Back's Hashcash"; transactions are "hashed in a Merkle Tree"; "Nodes always consider the longest chain to be the correct one"; the first transaction of each block "starts a new coin owned by the creator of the block"; Section 11 gives the attacker's chance of catching up from z blocks behind, with tables for q = 0.1 (z = 1: 0.2045873; z = 5: 0.0009137; z = 10: 0.0000012) and q = 0.3, and the smallest z with chance below 0.1% (q = 0.10: 5; 0.15: 8; 0.20: 11; 0.25: 15; 0.30: 24; 0.35: 41; 0.40: 89; 0.45: 340). **Documented** ([Nakamoto 2008, on an MIT course page](https://courses.csail.mit.edu/6.857/2015/files/L07-nakamoto-bitcoin-a-peer-to-peer-electronic-cash-system.pdf))
- The announcement, Friday 31 October 2008, to the Cryptography Mailing List: double-spending prevented by a peer-to-peer network, "No mint or other trusted parties", new coins from Hashcash-style proof of work. **Documented** ([The Cryptography Mailing List archive](https://www.metzdowd.com/pipermail/cryptography/2008-October/014810.html))
- bitcoin.org registered on 18 August 2008; the white paper posted on 31 October 2008; the genesis block on 3 January 2009, with the text "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks"; the first client released on 9 January 2009; Hal Finney received 10 bitcoins in the first transaction on 12 January 2009 (block 170); hashcash, "a proof-of-work scheme for spam control in 1997". **Documented** ([Wikipedia, History of bitcoin](https://en.wikipedia.org/wiki/History_of_bitcoin))
- The genesis block's header fields (version 1, a zero previous hash, Merkle root, timestamp 1231006505, bits 0x1d00ffff, nonce 2083236893) and its hash 000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f; its 50-bitcoin reward cannot be spent. **Documented** ([Bitcoin Wiki, Genesis block, as printed for a University of Twente course](https://www.utwente.nl/en/ces/sal/exams/Blockchain-and-Distributed-Ledger-Technology-test/1-Bitcoin/genesis-block-bitcoin-wiki.pdf))
- *Bitcoin and Cryptocurrency Technologies* (Narayanan, Bonneau, Felten, Miller and Goldfeder, Princeton University Press, 2016), a textbook introduction to "decentralization, mining, the politics of bitcoin". **Documented** ([Princeton University, Discovery](https://discovery.princeton.edu/2016/11/15/bitcoin-and-cryptocurrency-technologies-a-comprehensive-introduction))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [History of bitcoin](https://en.wikipedia.org/wiki/History_of_bitcoin) | Wikipedia | From the domain name to the first transaction |
| Start | [Bitcoin and Cryptocurrency Technologies](https://discovery.princeton.edu/2016/11/15/bitcoin-and-cryptocurrency-technologies-a-comprehensive-introduction) | Princeton University (2016) | A textbook for the whole subject |
| Deeper | [Genesis block](https://www.utwente.nl/en/ces/sal/exams/Blockchain-and-Distributed-Ledger-Technology-test/1-Bitcoin/genesis-block-bitcoin-wiki.pdf) | Bitcoin Wiki, printed for a University of Twente course | The first block, field by field |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Bitcoin: A Peer-to-Peer Electronic Cash System](https://courses.csail.mit.edu/6.857/2015/files/L07-nakamoto-bitcoin-a-peer-to-peer-electronic-cash-system.pdf) | S. Nakamoto (2008), on an MIT course page | The design and the Section 11 calculations |
| Scholar | [Bitcoin P2P e-cash paper](https://www.metzdowd.com/pipermail/cryptography/2008-October/014810.html) | S. Nakamoto, Cryptography Mailing List (31 October 2008) | The announcement |

**Gaps:** no video page could be opened. Back's hashcash paper, Chaum's ecash and Dai's b-money were not opened. The page treats Bitcoin as an algorithm (a ledger agreed by proof of work), not as an investment; prices and energy use are not discussed. The program's chain is a toy with low difficulty; only the genesis block's header is real.

## What the era leaves behind

- **Summaries instead of data.** Sketches (3) answer questions about streams in kilobytes; MinHash (5) compares documents by a few hundred numbers; compressed sensing (12) rebuilds a signal from fewer measurements than unknowns.
- **Hashing as placement.** Consistent hashing (4) decides which machine holds what; MapReduce (11) sends each key to one reducer by its hash; Bitcoin (13) seals each block with a hash that is expensive to find.
- **Agreement at scale.** Paxos (8) keeps replicas consistent through lost messages and stopped computers; Bitcoin (13) keeps one ledger among strangers, by proof of work.
- **Provable approximation.** Goemans and Williamson (2) promise 0.878 of the best cut; sketches promise errors with stated probabilities.
- **Old mathematics, new scale.** Euler's paths assemble genomes (9); Markov's chains rank the Web (7); Fermat's little theorem, sharpened, decides primality without chance (10).
- **Learning that generalizes and remembers.** Support vector machines (1) maximize a margin; LSTM (6) carries a memory across a thousand steps.

Era 9 picks up in 2009: deep learning at scale, transformers, and the algorithms of 2026.
