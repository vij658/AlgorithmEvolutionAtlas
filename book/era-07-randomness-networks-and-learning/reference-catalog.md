# Era 7 — Randomness, Networks and Learning: from polynomial-time linear programming to AdaBoost

*Reference catalog. Thirteen developments, from 1979 to 1995.*

> **Field note from the visiting historian.** In the sixth era the species learned that some of its problems may have no fast method, and turned that hardness into secrecy. In this one it learns to live with hardness in other ways. It flips coins on purpose: to search, to check, to prove. Its computers join into networks, and it has to make them agree when some parts fail or lie, and share their links without choking them. It builds machines that learn rules from examples instead of being told them. And near the end of the era it discovers, on paper, that a different kind of computer, one that works by quantum interference, would undo the hardness its secrets rest on.

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

A note on videos: video sites themselves could not be opened from the environment used to build this catalog. Where a video is listed, the page that was opened is a course or conference page that hosts it (MIT OpenCourseWare, RubyEvents, a college course page); where no such page was found, no video is listed and the topic's **Gaps** line says so. Redirects to other sites were not followed.

## The chain at a glance

| # | Development | When | The pain it answered |
|---|---|---|---|
| 1 | [Linear programming in polynomial time](#1-linear-programming-in-polynomial-time) | Klee–Minty 1972; Khachiyan 1979; Karmarkar 1984 | The simplex method had no polynomial guarantee |
| 2 | [Merkle's hash trees](#2-merkles-hash-trees) | Thesis and patent filing 1979; patent 1982 | Checking one block meant a fingerprint for every block |
| 3 | [The Byzantine generals](#3-the-byzantine-generals) | 1980 and 1982 | A faulty part could tell different parts different things |
| 4 | [Simulated annealing](#4-simulated-annealing) | 1983; Černý 1985 | Improving by small steps stops at the first local optimum |
| 5 | [Splay trees and amortized analysis](#5-splay-trees-and-amortized-analysis) | 1985 | Balanced trees needed bookkeeping and judged each operation alone |
| 6 | [Zero-knowledge proofs](#6-zero-knowledge-proofs) | 1985; all of NP 1986 | Proving you know a secret meant revealing it |
| 7 | [Backpropagation](#7-backpropagation) | Linnainmaa 1970; Werbos 1981; Rumelhart, Hinton and Williams 1986 | No well-known way to train hidden layers |
| 8 | [The Barnes–Hut tree code](#8-the-barneshut-tree-code) | 1986 | Gravity took N(N − 1) interactions per step |
| 9 | [Karp–Rabin fingerprints](#9-karprabin-fingerprints) | Presented 1985; published 1987 | Fast search needed intricate preprocessing; m × n at worst |
| 10 | [TCP congestion control](#10-tcp-congestion-control) | Collapse 1986; paper 1988; Chiu and Jain 1989 | Senders overran the network: congestion collapse |
| 11 | [Shor's factoring algorithm](#11-shors-factoring-algorithm) | 1994 | Factoring seemed to need superpolynomial time on any computer |
| 12 | [The Burrows–Wheeler transform](#12-the-burrowswheeler-transform) | Wheeler 1983; report 1994; FM index 2000 | Fast compressors compressed less than slow models |
| 13 | [AdaBoost](#13-adaboost) | Question 1988; abstract 1995; journal 1997 | Weak rules of thumb could not be combined in practice |

## 1. Linear programming in polynomial time

**When / where:** Victor Klee and George Minty, "How good is the simplex algorithm?" (1972), the cube on which the simplex method takes exponentially many steps; Leonid Khachiyan, Computer Center of the Soviet Academy of Sciences, Moscow, "A polynomial algorithm in linear programming", *Doklady Akademii Nauk SSSR*, February 1979 (proofs 1980), applying the ellipsoid method of Shor, Nemirovski and Yudin; Narendra Karmarkar, AT&T Bell Laboratories, "A New Polynomial-Time Algorithm for Linear Programming", *Combinatorica*, December 1984.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The simplex method (Era 4, topic 11) walks from corner to corner of the region the constraints allow, and on the problems people actually brought it, it was fast. But in 1972 Klee and Minty built a squashed cube on which it visits every one of the 2ⁿ corners. Was there any method whose work grows like a power of the problem's size? In February 1979 a 26-year-old at the Computer Center in Moscow, Khachiyan, published four pages without proofs saying yes: shrink an ellipsoid around the answer, cutting it in half at each step. Newspapers around the world reported it, with very spotty understanding, and one called it a "Soviet Answer to the 'Traveling Salesmen'", which it was not. In practice the method was slow. Five years later Karmarkar, at Bell Laboratories, published another polynomial method that moves through the inside of the region rather than along its edges, and interior-point methods became, with the simplex method, one of the two ways linear programs are solved.

**What hurt:** the simplex method had no guarantee: on Klee and Minty's cube it takes exponentially many steps, and nobody knew whether linear programming could be solved in polynomial time at all.
**The step forward:** the ellipsoid method, the first polynomial-time algorithm for linear programming (a theoretical breakthrough, slow in practice); then interior-point methods, polynomial and fast, which move through the interior of the feasible region.

**Evidence and certainty**

- Khachiyan (born 3 May 1952 in Leningrad, died 29 April 2005 in South Brunswick, New Jersey), "A polynomial algorithm in linear programming", *Doklady Akademii Nauk SSSR* (1979), a four-page paper showing that an ellipsoid method can solve linear programs in polynomial time, the first such algorithm; it was reported in the *New York Times* ("A Soviet Discovery Rocks World of Mathematics", 7 November 1979); he worked at the Computer Center of the Soviet Academy of Sciences and later at Rutgers; Fulkerson Prize 1982. **Documented** ([Wikipedia, Leonid Khachiyan](https://en.wikipedia.org/wiki/Leonid_Khachiyan))
- "The result was first published in a four-page note, without proofs, in Soviet Mathematics Doklady in February 1979", presented in the West at the Montreal Mathematical Programming Symposium in August 1979, with proofs in 1980; Lawler called the press reaction "The Great Mathematical Sputnik of 1979", the Guardian headlined "Soviet Answer to the 'Traveling Salesmen'", and papers tried to explain it "with very spotty results"; the method "seems to require in practice a number of iterations close to its worst-case bound", while the simplex method remains "highly competitive with the more recent interior-point methods". **Documented** ([SIAM News, "Leonid Khachiyan, 1952–2005: An Appreciation", 2005](https://sites.oxy.edu/lengyel/M372/papers/SIAM%20Leonid%20Khachiyan,%201952%962005%20An%20Appreciation.htm))
- The ellipsoid method's "preliminary version was introduced by Naum Z. Shor"; Nemirovski and Yudin studied it in 1972; in practice "the algorithm is fairly slow and of little practical interest", but it "provided inspiration for later work"; Karmarkar's interior-point method "is much faster than the ellipsoid method in practice". **Documented** ([Wikipedia, Ellipsoid method](https://en.wikipedia.org/wiki/Ellipsoid_method))
- Karmarkar, AT&T Bell Laboratories, *Combinatorica* (December 1984): "We present a new polynomial-time algorithm for linear programming", with running time O(n^3.5 L²) against O(n⁶L²) for the ellipsoid algorithm, built on projective transformations and a potential function. **Documented** ([Karmarkar 1984, on a University of Utah course page](https://users.cs.utah.edu/~tch/notes/PSSAT/EAGER/Ishaan/A_New_Polynomial-Time_Algorithm_for_Linear_Program.pdf))
- Karmarkar's algorithm (1984) is "the first reasonably efficient algorithm that solves these problems in polynomial time"; it was patented in May 1988, adding "fuel for the ongoing controversy over the issue of software patents"; affine scaling, a 1985 simplification using affine instead of projective transformations, turned out to rediscover "an algorithm published by Soviet mathematician I. I. Dikin in 1967", and is not itself known to be polynomial. **Documented** ([Wikipedia, Karmarkar's algorithm](https://en.wikipedia.org/wiki/Karmarkar%27s_algorithm))
- "An interior point method was discovered by Soviet mathematician I. I. Dikin in 1967" and "reinvented in the U.S. in the mid-1980s"; "The class of primal-dual path-following interior-point methods is considered the most successful", and "Mehrotra's predictor–corrector algorithm provides the basis for most implementations of this class of methods". **Documented** ([Wikipedia, Interior-point method](https://en.wikipedia.org/wiki/Interior-point_method))
- Primal-dual methods are "a variant of Newton's method" applied to the optimality conditions; with the centering parameter σ = 0 the direction is the pure Newton (affine-scaling) direction, and a positive σ orients the step "away from the boundary"; Mehrotra's predictor-corrector algorithm was "outlined in a 1993 paper by Mehrotra"; interior-point codes "have proven to be competitive with, and often superior to, the best simplex packages". **Documented** ([NEOS Guide, Interior-Point Methods](https://neos-guide.org/guide/algorithms/ipm))
- Klee and Minty's cube: the simplex method with the usual pivot rule visits all corners of a perturbed cube in dimension n in the worst case ("How good is the simplex algorithm?", in *Inequalities III*); Wikipedia's text says 1973 while its citation says 1972. **Disputed** (the year) ([Wikipedia, Klee–Minty cube](https://en.wikipedia.org/wiki/Klee%E2%80%93Minty_cube))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Leonid Khachiyan, 1952–2005: An Appreciation](https://sites.oxy.edu/lengyel/M372/papers/SIAM%20Leonid%20Khachiyan,%201952%962005%20An%20Appreciation.htm) | SIAM News (2005) | The four-page note, the headlines, and what the method did and did not change |
| Start | [Klee–Minty cube](https://en.wikipedia.org/wiki/Klee%E2%80%93Minty_cube) | Wikipedia | The cube on which the simplex method visits every corner |
| Deeper | [Ellipsoid method](https://en.wikipedia.org/wiki/Ellipsoid_method) | Wikipedia | How cutting ellipsoids in half finds a feasible point |
| Deeper | [Karmarkar's algorithm](https://en.wikipedia.org/wiki/Karmarkar%27s_algorithm) | Wikipedia | Interior points, the patent, and affine scaling |
| Deeper | [Interior-Point Methods](https://neos-guide.org/guide/algorithms/ipm) | NEOS Guide | Primal-dual path-following and Mehrotra's predictor-corrector, as in this topic's program |
| Deeper | [Interior-point method](https://en.wikipedia.org/wiki/Interior-point_method) | Wikipedia | Dikin, Karmarkar, and why primal-dual methods won |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A New Polynomial-Time Algorithm for Linear Programming](https://users.cs.utah.edu/~tch/notes/PSSAT/EAGER/Ishaan/A_New_Polynomial-Time_Algorithm_for_Linear_Program.pdf) | N. Karmarkar, *Combinatorica* (1984), on a University of Utah page | The projective method and its bound |

**Gaps:** no video page could be opened. Khachiyan's Russian note and Klee and Minty's paper were not opened. The *New York Times* articles are cited through Wikipedia, not opened. The topic's program uses a primal-dual interior-point method with Mehrotra's predictor-corrector (Mehrotra's 1993 paper was not opened), not Karmarkar's projective method, and a two-dimensional ellipsoid method for illustration.

## 2. Merkle's hash trees

**When / where:** Ralph Merkle, Stanford University: the PhD thesis "Secrecy, Authentication, and Public Key Systems" (Stanford Electronics Laboratories technical report, June 1979), and the patent "Method of providing digital signatures", filed 5 September 1979, granted 5 January 1982 (US 4,309,569); published for cryptographers as "A Digital Signature Based on a Conventional Encryption Function", *CRYPTO '87* (1988).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Public-key signatures (Era 6, topic 10) rested on a hard problem in number theory. A one-way function, a hash, was simpler: Lamport and Diffie had shown how to sign one message with one by publishing the hashes of secrets and revealing half of the secrets. But each key could sign only one message, and the public keys were long. In his 1979 thesis Merkle hashed the public keys together in pairs, then the pairs in pairs, up to a single root, and published only the root. To prove that any one key belonged, he needed to send "only log2 n" values. The same tree turned out to check any piece of any large collection of data against one short fingerprint, and it is now found in file systems, version control, peer-to-peer networks and certificate logs.

**What hurt:** checking that one block belongs to a large collection meant hashing or storing a fingerprint for every block, and a hash-based one-time signature key could sign only one message.
**The step forward:** hash the fingerprints together in pairs up to one root; any block can then be checked against the root with about log2 n hashes, and many one-time keys can share a single short public key.

**Evidence and certainty**

- Merkle's thesis, Stanford Electronics Laboratories technical report 1979-1, June 1979, chapter V, section 4, "tree authentication": "This method lets us selectively authenticate any 'leaf'"; "Using this method, only log2 n transmissions are required, each of about 200 bits"; the one-time signatures of Lamport and Diffie can each sign one message, which "is not practical for most applications without further refinements". **Documented** ([Merkle, *Secrecy, Authentication, and Public Key Systems*, 1979](https://www.ralphmerkle.com/papers/Thesis1979.pdf))
- US patent 4,309,569, "Method of providing digital signatures", inventor Ralph C. Merkle, assignee Stanford University, filed 5 September 1979, granted 5 January 1982; it names "the root of the authentication tree". **Documented** ([Google Patents, US4309569](https://patents.google.com/patent/US4309569))
- "The concept of a hash tree is named after Ralph Merkle, who patented it in 1979"; checking that a leaf belongs "requires computing a number of hashes proportional to the logarithm of the number of leaf nodes"; uses listed include IPFS, BitTorrent, ZFS, Git and Mercurial, Bitcoin and Ethereum, Certificate Transparency, and Cassandra, Riak and Dynamo for repairing replicas; without a marker for leaves, "The Merkle hash root does not indicate the tree depth, enabling a second-preimage attack". **Documented** ([Wikipedia, Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree))
- Certificate Transparency (Laurie, Langley and Kasper of Google, June 2013, Experimental) defines the tree hash with `SHA-256(0x00 || d(0))` for a leaf and `SHA-256(0x01 || left || right)` for a node, splitting at "the largest power of two smaller than n", and the audit path as "the shortest list of additional nodes in the Merkle Tree required to compute the Merkle Tree Hash". **Documented** ([RFC 6962](https://www.rfc-editor.org/rfc/rfc6962))
- Merkle's signature scheme was developed "by Ralph Merkle in the late 1970s"; it "is believed to be resistant against attacks by quantum computers" because it depends only on secure hash functions; NIST approved stateful hash-based signature variants in 2020 (SP 800-208). **Documented** ([Wikipedia, Merkle signature scheme](https://en.wikipedia.org/wiki/Merkle_signature_scheme))
- NIST's *Dictionary of Algorithms and Data Structures*: in a Merkle tree "each internal node has a hash of all the information in the leaf nodes under it"; it dates the patent's filing to 5 September 1979. **Documented** ([NIST DADS, Merkle tree](https://xlinux.nist.gov/dads/HTML/MerkleTree.html))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Session 3: Blockchain Basics & Cryptography](https://ocw.mit.edu/courses/15-s12-blockchain-and-money-fall-2018/resources/session-3-blockchain-basics-cryptography/) | MIT OpenCourseWare, Gary Gensler, *Blockchain and Money* (Fall 2018) | A lecture covering hash functions and Merkle trees in block headers, with video and transcript |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree) | Wikipedia | The structure, its uses, and the second-preimage attack |
| Start | [Merkle tree](https://xlinux.nist.gov/dads/HTML/MerkleTree.html) | NIST, *Dictionary of Algorithms and Data Structures* | A one-paragraph definition with the original references |
| Deeper | [Merkle signature scheme](https://en.wikipedia.org/wiki/Merkle_signature_scheme) | Wikipedia | One-time keys under one root, and why it matters after quantum computers |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Secrecy, Authentication, and Public Key Systems](https://www.ralphmerkle.com/papers/Thesis1979.pdf) | R. Merkle, PhD thesis, Stanford (1979) | Chapter V introduces tree authentication |
| Scholar | [Method of providing digital signatures](https://patents.google.com/patent/US4309569) | R. Merkle, US patent 4,309,569 (filed 1979) | The authentication tree as patented |
| Scholar | [RFC 6962: Certificate Transparency](https://www.rfc-editor.org/rfc/rfc6962) | B. Laurie, A. Langley, E. Kasper, IETF (2013) | The exact tree hash and audit paths this topic's program follows |

**Gaps:** the *CRYPTO '87* paper was not opened. Lamport's one-time signature (1979) is cited through Merkle's thesis, not opened. No beginner video page could be opened. The thesis was read as an OCR text; its formulas are garbled, so only legible sentences are quoted. The program's keys come from a fixed-seed generator for reproducibility; real keys need a secure random generator.

## 3. The Byzantine generals

**When / where:** Marshall Pease, Robert Shostak and Leslie Lamport, SRI International: "Reaching Agreement in the Presence of Faults", *Journal of the ACM* (1980); Lamport, Shostak and Pease, "The Byzantine Generals Problem", *ACM Transactions on Programming Languages and Systems* 4(3), July 1982, pp. 382–401.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** A computer that stops is easy to notice. One that keeps running but tells one part of a system one thing and another part something else is not. Engineers at SRI building a fault-tolerant computer had posed the problem; Pease, Shostak and Lamport proved in 1980 that with spoken messages, agreement is possible only if more than two thirds of the parties are sound, so three computers cannot outvote one liar. Two years later Lamport retold it as a story about generals besieging a city. He had first called them the Albanian generals; a colleague pointed out that there were Albanians outside Albania, and "The obviously more appropriate Byzantine generals then occurred to me". The name stuck, and "Byzantine fault" now means a component that fails in any way at all, including lying.

**What hurt:** fault-tolerant systems voted among several copies of a computation, but a faulty component could send different values to different voters, and there was no proof of how many components were needed to survive that.
**The step forward:** an exact answer: with m faulty components, oral-message agreement needs at least 3m + 1 in all, achieved by the recursive algorithm OM(m); with unforgeable signatures, any number suffices (SM(m)).

**Evidence and certainty**

- Lamport, Shostak and Pease, SRI International, *ACM TOPLAS* 4(3), July 1982, pp. 382–401: "Reliable computer systems must handle malfunctioning components that give conflicting information"; "no solution with fewer than 3m + 1 generals can cope with m traitors" (p. 385); OM(m) and SM(m) "involve sending up to (n - 1)(n - 2) ... (n - m - 1) messages" (p. 401). **Documented** ([Lamport, Shostak and Pease, "The Byzantine Generals Problem", 1982, on a UMass course page](https://people.cs.umass.edu/~arun/cs677/reading/LSP.pdf))
- The abstract: the problem "is solvable if and only if more than two-thirds of the generals are loyal" with oral messages; "With unforgeable written messages, the problem is solvable for any number of generals and possible traitors"; dated 1 July 1982. **Documented** ([SRI International, publication page](https://sri.com/?p=12386))
- Lamport's note on the 1982 paper: "the best way to attract attention to a problem is to present it in terms of a story"; the problem had been "sometimes called the Chinese Generals Problem"; "the original title of this paper was The Albanian Generals Problem"; Jack Goldberg "was smart enough to realize that there were Albanians in the world outside Albania"; "The obviously more appropriate Byzantine generals then occurred to me"; "The main reason for writing this paper was to assign the new name to the problem." **Documented** ([Microsoft Research, "The Byzantine Generals Problem"](https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/))
- Lamport's note on the 1980 paper (*JACM*, 1980): it won the 2005 Edsger W. Dijkstra Prize in Distributed Computing; the problem was formulated by people working on SIFT at SRI before Lamport arrived; Shostak found the 4-processor solution and the impossibility result, Pease the 3n+1-processor solution, and Lamport the signed-message solution; 3n+1 processors are needed for n faults, 2n+1 with signatures; a former Boeing engineer told him in 1997 that Boeing's commercial aircraft designers knew of the work by 1986. **Documented** (Lamport's own account) ([Microsoft Research, "Reaching Agreement in the Presence of Faults"](https://www.microsoft.com/en-us/research/?p=338426))
- Kleppmann's Cambridge lecture notes: "in a system with 3f + 1 generals, no more than f may be malicious"; "However, even with signatures, the Byzantine generals problem remains challenging." **Documented** ([M. Kleppmann, *Distributed Systems* lecture notes, University of Cambridge, 2021/22](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/dist-sys-notes.pdf))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [The Byzantine Generals Problem](https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/) | Microsoft Research, with Leslie Lamport's note | How the story and the name were chosen |
| Deeper | [Distributed Systems lecture notes](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/dist-sys-notes.pdf) | M. Kleppmann, University of Cambridge (2021/22) | Section 2.2 puts the generals beside the two generals problem and modern systems |
| Deeper | [Reaching Agreement in the Presence of Faults](https://www.microsoft.com/en-us/research/?p=338426) | Microsoft Research, with Lamport's note | Who proved what, and the Boeing story |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Byzantine Generals Problem](https://people.cs.umass.edu/~arun/cs677/reading/LSP.pdf) | L. Lamport, R. Shostak, M. Pease, *ACM TOPLAS* (1982), on a UMass course page | OM(m), SM(m) and the 3m + 1 bound |
| Scholar | [The Byzantine Generals Problem (abstract)](https://sri.com/?p=12386) | SRI International | The abstract as SRI publishes it |

**Gaps:** the 1980 *JACM* paper itself was not opened; its details come from Lamport's note. Kleppmann's lecture videos are linked from his notes, but the video page was not opened. The SIFT project is cited only through Lamport's note. The program's traitors in SM(m) choose their messages at random among those they could sign; they do not relay chains that contain loyal signatures.

## 4. Simulated annealing

**When / where:** Scott Kirkpatrick, C. Daniel Gelatt Jr. and Mario P. Vecchi, IBM Thomas J. Watson Research Center, Yorktown Heights, "Optimization by Simulated Annealing", *Science* 220 (4598), 13 May 1983; independently Vladimír Černý, Comenius University, Bratislava, "Thermodynamical Approach to the Traveling Salesman Problem: An Efficient Simulation Algorithm", *Journal of Optimization Theory and Applications* 45 (1), January 1985; both built on the Metropolis algorithm of 1953.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Era 6 ended with a list of problems, the travelling salesman among them, for which nobody expected a fast exact method. Engineers still had to place chips and route wires. The usual tactic, keep making small changes that help, got stuck at the first arrangement no small change could improve. Kirkpatrick, Gelatt and Vecchi, at IBM, saw that accepting only improvements was like cooling a material too fast, "rapid quenching", which leaves it stuck in a poor, metastable state, and that the remedy in physics is to cool it slowly: to anneal it. They borrowed the rule physicists had used since 1953 to simulate atoms at a temperature: accept a change that makes things worse with a probability that shrinks as the change gets worse and as the temperature falls. Then they lowered the temperature step by step. In Bratislava, Černý published the same idea for the travelling salesman in 1985. The method gives no useful guarantee, but it is short to write and can be tried on any problem with a cost to lower.

**What hurt:** iterative improvement, accepting only changes that help, stops at the first local optimum; for hard problems like chip placement and the travelling salesman that is often far from the best.
**The step forward:** accept worsening changes with probability exp(−Δ/T), and lower T slowly, so the search can climb out of shallow valleys early and settles into a deep one as it cools.

**Evidence and certainty**

- Kirkpatrick, Gelatt and Vecchi, IBM Thomas J. Watson Research Center, *Science*, 13 May 1983: "There is a deep and useful connection between statistical mechanics ... and multivariate or combinatorial optimization"; "Applications to partitioning, component placement, and wiring of electronic systems are described"; they ran travelling salesman problems "with as many as several thousand cities"; annealing "differs from iterative improvement in that the procedure need not get stuck"; their schedule starts where nearly every change is accepted and multiplies the temperature by 0.9 each time; in their partitioning example rapid quenching gave about 700 pins, slow annealing 353 and 321. **Documented** ([Kirkpatrick, Gelatt and Vecchi, 1983](https://zhanggroup.org/teaching/literature/Kirkpatrick_Annealing_Science_1983.pdf))
- Černý, Institute of Physics and Biophysics, Comenius University, Bratislava, *JOTA* 45(1), January 1985: "We present a Monte Carlo algorithm to find approximate solutions of the traveling salesman problem"; on 100 points on a circle, "After a total of 25,000 Monte Carlo trials a value 6.28 was reached, which means that the true optimum was found"; his sampling cites Metropolis, Rosenbluth, Rosenbluth, Teller and Teller (1953). **Documented** ([Černý, 1985](https://mk.bcgsc.ca/papers/cerny-travelingsalesman.pdf))
- Simulated annealing is "an adaptation of the Metropolis–Hastings algorithm", published "by N. Metropolis et al. in 1953"; similar techniques were introduced independently by Pincus (1970), Khachaturyan et al. (1979, 1981), Kirkpatrick, Gelatt and Vecchi (1983), who "also proposed its current name", and Černý (1985); the probability of ending at the global optimum approaches 1 as the schedule is extended, but the time needed "will usually exceed the time required for a complete search of the solution space"; the cooling rate "should be empirically adjusted for each problem". **Documented** ([Wikipedia, Simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Simulated Annealing: The Most Metal Algorithm Ever](https://rubyevents.org/talks/simulated-annealing-the-most-metal-algorithm-ever) | Chris Bloom, RubyConf 2022 (28 minutes) | The metallurgy analogy, a travelling-salesperson example and a real scheduling use |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Simulated annealing](https://en.wikipedia.org/wiki/Simulated_annealing) | Wikipedia | The acceptance rule, the schedule, and who invented it when |
| Deeper | [Lecture 10: simulated annealing](https://ocw.mit.edu/courses/ids-338j-multidisciplinary-system-design-optimization-spring-2010/resources/mitesd_77s10_lec10/) | MIT OpenCourseWare, O. de Weck and K. Willcox (2010) | Lecture notes on annealing as an engineering design tool |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Optimization by Simulated Annealing](https://zhanggroup.org/teaching/literature/Kirkpatrick_Annealing_Science_1983.pdf) | S. Kirkpatrick, C. D. Gelatt, M. P. Vecchi, *Science* (1983), on a research group's teaching page | The analogy, the schedule and the chip-design results |
| Scholar | [Thermodynamical Approach to the Traveling Salesman Problem](https://mk.bcgsc.ca/papers/cerny-travelingsalesman.pdf) | V. Černý, *JOTA* (1985), on a BC Cancer Genome Sciences Centre page | The independent discovery, with worked examples |

**Gaps:** the Metropolis paper (1953) and Pincus (1970) were not opened. The MIT lecture page was opened but its PDF was not. The program's moves reverse a stretch of the tour; Kirkpatrick, Gelatt and Vecchi's exact move set for the travelling salesman was not checked. The program's freezing rule (three temperatures accepting fewer than 1 change in 1,000) is a simplification of theirs.

## 5. Splay trees and amortized analysis

**When / where:** Daniel Sleator and Robert Tarjan, AT&T Bell Laboratories, Murray Hill, New Jersey: "Self-Adjusting Binary Search Trees", *Journal of the ACM* 32(3), July 1985, pp. 652–686; Robert Tarjan, "Amortized Computational Complexity", *SIAM Journal on Algebraic and Discrete Methods* 6(2), April 1985.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Balanced search trees (Era 5) promised that no single search would be slow, and paid for it with extra bookkeeping in every node and fiddly rules after every change. Sleator and Tarjan asked for less: not that every operation be fast, but that any sequence of them be fast on the whole. Their splay tree keeps no bookkeeping at all. Whenever a key is touched, it is rotated up to the root, two steps at a time, which also shortens the path to everything it passed. One access can take as long as the tree is deep, but they proved that m accesses take O(m log n) in total, and that keys used often drift to the top by themselves. To prove it, Tarjan gave the data structure a "potential", like stored energy in physics: a cheap operation may store some up, and an expensive one is paid for by releasing it. That way of accounting, amortized analysis, became a standard tool for judging data structures.

**What hurt:** balanced trees needed extra fields and intricate rebalancing rules, and judged each operation alone, ignoring that real workloads repeat the same keys again and again.
**The step forward:** a tree that restructures itself on every access with one simple rule (splaying), and a way of proving costs over whole sequences of operations (amortization, with a potential function).

**Evidence and certainty**

- Sleator and Tarjan, AT&T Bell Laboratories, *JACM* 32(3), July 1985, pp. 652–686: "The splay tree, a self-adjusting form of binary search tree, is developed and analyzed"; all standard operations have an amortized bound of O(log n), "where by 'amortized time' is meant the time per operation averaged over a worst-case sequence of operations"; "for sufficiently long access sequences, splay trees are as efficient, to within a constant factor, as static optimum search trees"; the efficiency comes "from applying a simple restructuring heuristic, called splaying, whenever the tree is accessed"; the access lemma: "The amortized time to splay a tree with root t at a node x is at most 3(r(t) - r(x)) + 1" (p. 658); the dynamic optimality conjecture (p. 684). **Documented** ([Sleator and Tarjan, 1985, on a Princeton course page](https://www.cs.princeton.edu/courses/archive/fall07/cos521/handouts/self-adjusting.pdf))
- Tarjan, *SIAM J. Alg. Disc. Meth.* 6(2), April 1985: "A powerful technique in the complexity analysis of data structures is amortization, or averaging over time"; the banker's view, in which "To each operation we allocate a certain number of credits", and the physicist's view with a potential function; the first example is a stack where each operation is "composed of zero or more pops followed by a push", with "at most 2m pushes and pops" in m operations; amortization leads to "self-adjusting" data structures. **Documented** ([Tarjan, "Amortized Computational Complexity", 1985, on a Duke course page](https://courses.cs.duke.edu/fall11/cps234/reading/Tarjan85_AmortizedComplexity.pdf))
- "The splay tree was invented by Daniel Sleator and Robert Tarjan in 1985"; "recently accessed elements are quick to access again"; "Splay trees do not need to store any bookkeeping data"; but "the height of a splay tree can be linear" and the tree changes even on read-only accesses, which complicates concurrent use; the dynamic optimality conjecture is unproven. **Documented** ([Wikipedia, Splay tree](https://en.wikipedia.org/wiki/Splay_tree))
- Karger's MIT lecture notes: the potential is the sum of the ranks, r(x) = log of the subtree size; total cost "is as good as of *any* fixed tree"; Tango trees (Demaine and others, 2004) come within O(log log n) of the best dynamic tree, and dynamic optimality remains open. **Documented** ([MIT 6.854 lecture notes, "Splay Trees"](https://courses.csail.mit.edu/6.854/21/Notes/n03-splay.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Splay tree](https://en.wikipedia.org/wiki/Splay_tree) | Wikipedia | The zig, zig-zig and zig-zag steps with pictures, and the trade-offs |
| Deeper | [Lecture 3: Splay Trees](https://courses.csail.mit.edu/6.854/21/Notes/n03-splay.html) | D. Karger, MIT 6.854 *Advanced Algorithms* | The potential-function proof, step by step |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Self-Adjusting Binary Search Trees](https://www.cs.princeton.edu/courses/archive/fall07/cos521/handouts/self-adjusting.pdf) | D. Sleator, R. Tarjan, *JACM* (1985), on a Princeton course page | Splaying, the access lemma and the conjectures |
| Scholar | [Amortized Computational Complexity](https://courses.cs.duke.edu/fall11/cps234/reading/Tarjan85_AmortizedComplexity.pdf) | R. Tarjan, *SIAM J. Alg. Disc. Meth.* (1985), on a Duke course page | The banker's and physicist's views of amortization |

**Gaps:** no lecture video page could be opened. The theorems' formulas in the 1985 paper are garbled in the text that was read, so only legible statements are quoted. Knuth's optimal-tree algorithm (1971), used by the program for comparison, is not separately sourced here. Earlier uses of amortized arguments are not traced.

## 6. Zero-knowledge proofs

**When / where:** Shafi Goldwasser and Silvio Micali (MIT) and Charles Rackoff (University of Toronto), "The Knowledge Complexity of Interactive Proof-Systems", ACM symposium proceedings, 1985; Oded Goldreich (Technion), Silvio Micali (MIT) and Avi Wigderson (Hebrew University), "Proofs that Yield Nothing But Their Validity", *IEEE Symposium on Foundations of Computer Science*, 1986 (journal version *Journal of the ACM* 38, July 1991).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** For two thousand years a proof was a text: anyone who read it learned not only that the theorem was true but why. In 1985 Goldwasser, Micali and Rackoff proposed a different kind of proof, a conversation in which the verifier asks random questions and the prover answers. Such a proof can convince with any certainty you like, short of absolute, and they asked how much "knowledge" it gives away. Some give away none at all: whatever the verifier sees, it could have produced by itself, without the prover. A year later Goldreich, Micali and Wigderson showed that, if secure encryption exists, every statement whose proof can be checked quickly (every problem in NP) has such a zero-knowledge proof. A storyteller's version, about Ali Baba and a cave with a magic door, followed in 1990. Zero-knowledge proofs later became "the essential language for speaking about security of cryptographic protocols", and in 2016 were used to hide the details of payments in cryptocurrencies.

**What hurt:** to prove you know a secret (a password, a key, a solution), you had to reveal it, or at least something about it, to whoever checks the proof.
**The step forward:** interactive, randomized proofs that convince the verifier with overwhelming probability while revealing nothing beyond the truth of the statement, since a simulator with no secret could produce the same conversation.

**Evidence and certainty**

- Goldwasser and Micali (MIT) and Rackoff (Toronto), © 1985 ACM: "we introduce a new theorem-proving procedure, that is a new efficient method of communicating a proof"; "Our 'proofs' are probabilistic in nature"; "Our proofs are interactive"; knowledge complexity is defined by a probabilistic polynomial-time machine M whose output is indistinguishable from the real conversation; quadratic non-residuosity is shown to have knowledge complexity 0. **Documented** ([Goldwasser, Micali and Rackoff, 1985, on a Max Planck Institute course page](https://resources.mpi-inf.mpg.de/departments/d1/teaching/ss13/gitcs/GMR85.pdf))
- Goldreich, Micali and Wigderson, *JACM* 38, July 1991, pp. 691–729 (preliminary version, 27th IEEE FOCS, 1986): proofs that "efficiently demonstrate membership in the language without conveying any additional knowledge"; the graph isomorphism protocol, in which the prover "generates a graph H, which is a random isomorphic copy" of the first graph and the verifier asks which graph to relate H to, repeated "m times, each time using independent random coin tosses"; graph 3-colouring for all of NP assuming "secure encryption functions", where each round shows the verifier only "a pair of different randomly selected elements" of the three colours. **Documented** ([Goldreich, Micali and Wigderson, on Silvio Micali's MIT page](https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Zero%20Knowledge/Proofs_That_Yield_Nothing_But_Their_Validity_or_All_Languages_in_NP_Have_Zero-Knowledge_Proof_Systems.pdf))
- ACM, announcing the 2012 Turing Award to Goldwasser and Micali (13 March 2013): the 1985 paper with Rackoff "initiated the idea of 'zero-knowledge' proofs", which establish a fact without "providing any additional information as to why it is true", and are "the essential language for speaking about security of cryptographic protocols". **Documented** ([ACM press release, 2013](https://www.acm.org/media-center/2013/march/goldwasser-micali-receive-acm-turing-award-for-advances-in-cryptography))
- "Zero-knowledge proofs were first conceived in 1985"; with Babai and Moran's work, the paper invented interactive proof systems, and all five authors won the first Gödel Prize in 1993; completeness, soundness and zero-knowledge defined; the Ali Baba cave story, first published in 1990 by Quisquater and others; zero-knowledge proofs were applied in the Zcash and Zcoin cryptocurrencies in 2016. **Documented** ([Wikipedia, Zero-knowledge proof](https://en.wikipedia.org/wiki/Zero-knowledge_proof))
- Quisquater and Guillou, with Berson, "How to Explain Zero-Knowledge Protocols to Your Children", *Advances in Cryptology – CRYPTO '89* (1990): "Know, oh my children, that very long ago, in the Eastern city of Baghdad, there lived an old man named Ali Baba"; the aim is to show "that it is possible to convince without revealing". **Documented** ([Fermat's Library, annotated text](https://www.fermatslibrary.com/s/how-to-explain-zero-knowledge-protocols-to-your-children))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [How to Explain Zero-Knowledge Protocols to Your Children](https://www.fermatslibrary.com/s/how-to-explain-zero-knowledge-protocols-to-your-children) | J.-J. Quisquater, L. Guillou, T. Berson (1990), annotated by Fermat's Library | The Ali Baba cave, the story everyone uses |
| Start | [Zero-knowledge proof](https://en.wikipedia.org/wiki/Zero-knowledge_proof) | Wikipedia | Completeness, soundness and zero knowledge, with the cave and a graph example |
| Deeper | [Goldwasser, Micali receive ACM Turing Award](https://www.acm.org/media-center/2013/march/goldwasser-micali-receive-acm-turing-award-for-advances-in-cryptography) | ACM (2013) | Why the idea mattered to cryptography |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [The Knowledge Complexity of Interactive Proof-Systems](https://resources.mpi-inf.mpg.de/departments/d1/teaching/ss13/gitcs/GMR85.pdf) | S. Goldwasser, S. Micali, C. Rackoff (1985), on a Max Planck Institute page | Interactive proofs and knowledge complexity |
| Scholar | [Proofs that Yield Nothing But Their Validity](https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Zero%20Knowledge/Proofs_That_Yield_Nothing_But_Their_Validity_or_All_Languages_in_NP_Have_Zero-Knowledge_Proof_Systems.pdf) | O. Goldreich, S. Micali, A. Wigderson, *JACM* (1991) | Graph isomorphism and 3-colouring, as in this topic's program |

**Gaps:** the 1985 copy read does not name the conference (it is commonly cited as STOC 1985, not confirmed here). The issue number of the 1991 *JACM* paper differs between sources and is left out. No video page could be opened. Babai and Moran's work and the Fiat–Shamir transformation are not covered. The program's commitments use SHA-256 with nonces from a fixed-seed generator for reproducibility; real ones need a secure random generator.

## 7. Backpropagation

**When / where:** Seppo Linnainmaa, University of Helsinki, master's thesis, 1970 (the reverse mode of automatic differentiation, without neural networks); Paul Werbos, 1974 discussion and 1981 application to neural networks; David Rumelhart, Geoffrey Hinton and Ronald Williams, "Learning representations by back-propagating errors", *Nature* 323, pp. 533–536, October 1986.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** The perceptron (Era 5) learned by nudging one layer of weights, and one layer cannot even tell whether exactly one of two inputs is on. Layers of hidden units in between could do it, but nobody had a practical way to tell a hidden unit how to change, since its error is not visible at the output. The answer was the chain rule from calculus, run backwards through the network. It had been found several times: Linnainmaa described the general method for computer programs in 1970, and Werbos applied it to neural networks by 1981. What changed in 1986 was a four-page paper in *Nature* by Rumelhart, Hinton and Williams that showed hidden units learning useful features by themselves, and made the method famous; it set off a boom in neural network research.

**What hurt:** single-layer networks could not learn simple functions such as exclusive-or, and there was no efficient, widely known way to train the hidden layers that could.
**The step forward:** compute the slope of the error with respect to every weight at once by running the chain rule backwards from the output, for about the cost of one more pass through the network, and descend that slope.

**Evidence and certainty**

- Rumelhart, Hinton and Williams, *Nature* 323, pp. 533–536 (1986), DOI 10.1038/323533a0: "We describe a new learning procedure, back-propagation, for networks of neurone-like units"; it adjusts the weights to reduce the difference between actual and desired outputs, so that hidden units come to represent important features of the task, which distinguishes it from the perceptron-convergence procedure. **Documented** ([ML Anthology record](https://mlanthology.org/misc/1986/rumelhart1986misc-learning); [NASA ADS record, October 1986](https://ui.adsabs.harvard.edu/abs/1986Natur.323..533R/abstract))
- Explicit, efficient error backpropagation "was first described in Linnainmaa's 1970 master's thesis", which "introduced the reverse mode of automatic differentiation", but without reference to neural networks. **Documented** ([Wikipedia, Seppo Linnainmaa](https://en.wikipedia.org/wiki/Seppo_Linnainmaa))
- Schmidhuber's survey: gradient methods of this kind were discussed "at least since the early 1960s" (Kelley 1960, Bryson 1961); "A simplified derivation of this backpropagation method uses the chain rule only (Dreyfus, 1962)"; BP "apparently was first described in a 1970 master's thesis (Linnainmaa, 1970, 1976), albeit without reference to NNs"; "the first NN-specific application of efficient BP as above was described in 1981 (Werbos, 1981, 2006)"; "A paper of 1986 significantly contributed to the popularisation of BP for NNs". **Documented** (one historian's account, section 5.5) ([J. Schmidhuber, "Deep Learning in Neural Networks: An Overview", 2014](https://arxiv.org/pdf/1404.7828))
- Widrow and Lehr, *Proceedings of the IEEE*, September 1990: Werbos "first published in his doctoral dissertation" in 1974, but his work "remained almost unknown in the scientific community"; "In 1982, Parker rediscovered the technique and in 1985, published a report on it at M.I.T."; "Rumelhart, Hinton, and Williams also rediscovered the technique", and their clear framework made it widely known. **Disputed** (Widrow and Lehr call Werbos's 1974 work a dissertation that published backpropagation; Schmidhuber calls it a preliminary discussion and dates the first neural-network application to 1981) ([Widrow and Lehr, "30 Years of Adaptive Neural Networks", 1990](https://isl.stanford.edu/people/widrow/papers/j199030years.pdf))
- Williams "co-authored the seminal paper in Nature on the backpropagation algorithm along with David Rumelhart and Geoffrey Hinton", which "triggered a boom in neural network research"; he joined Northeastern University in 1986. **Documented** ([Wikipedia, Ronald J. Williams](https://en.wikipedia.org/wiki/Ronald_J._Williams))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Introduction to Neural Nets: videos](https://cs.wellesley.edu/~cs332/videos/Neural_Nets_videos.html) | Wellesley College CS 332, listing Grant Sanderson's 3Blue1Brown videos | "What is backpropagation really doing?" and "Backpropagation calculus", with suggested stopping points |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [30 Years of Adaptive Neural Networks](https://isl.stanford.edu/people/widrow/papers/j199030years.pdf) | B. Widrow, M. Lehr, *Proc. IEEE* (1990) | Perceptron, Madaline and backpropagation, by one of the field's pioneers |
| Deeper | [Deep Learning in Neural Networks: An Overview](https://arxiv.org/pdf/1404.7828) | J. Schmidhuber (2014) | Section 5.5 traces backpropagation from the 1960s to 1986 |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Learning Representations by Back-Propagating Errors](https://mlanthology.org/misc/1986/rumelhart1986misc-learning) | D. Rumelhart, G. Hinton, R. Williams, *Nature* (1986), ML Anthology record | The abstract and full citation of the paper that made the method famous |

**Gaps:** the text of the 1986 *Nature* paper was not opened (only its abstract), so its examples are not described here. Linnainmaa's thesis, Werbos's 1974 and 1981 work and Parker's report were not opened. The authors' 1986 affiliations are not given, because no opened source confirmed them. Minsky and Papert's *Perceptrons* (1969), the usual reference for the limits of one layer, was not opened. The program uses its own learning rate, momentum and starting weights.

## 8. The Barnes–Hut tree code

**When / where:** Josh Barnes and Piet Hut, "A hierarchical O(N log N) force-calculation algorithm", *Nature* 324 (6096), pp. 446–449, 4 December 1986; followed by Leslie Greengard and Vladimir Rokhlin's fast multipole method, 1987.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Astronomers who wanted to watch galaxies collide in a computer faced arithmetic that grew with the square of the number of stars: every star pulls on every other. A few thousand stars was about the limit, far too few to look like a galaxy. Barnes and Hut used an old physical intuition, that a distant crowd pulls almost like one heavy body at its centre of mass, and made it systematic with a tree of cubes, each split into eight. Each star asks the tree: is this cube small enough, seen from here, to be treated as one body? If not, look inside. The work per star then grows with the logarithm of the number of stars instead of the number itself, and the accuracy is set by one number, the opening angle θ. A year later Greengard and Rokhlin's fast multipole method pushed the same idea further, to work that grows only in proportion to N.

**What hurt:** computing gravity directly takes N(N − 1) interactions per time step, which limited simulations of star clusters and galaxies to small numbers of bodies.
**The step forward:** group distant bodies hierarchically in an octree and replace each sufficiently small, distant group by its total mass at its centre of mass, so a step costs about N log N, with accuracy controlled by θ.

**Evidence and certainty**

- J. Barnes and P. Hut, "A hierarchical O(N log N) force-calculation algorithm", *Nature* 324 (6096), pp. 446–449, published 4 December 1986, a letter, DOI 10.1038/324446a0. **Documented** ([Saved copy of the *Nature* article page](https://isidore.co/misc/Physics%20papers%20and%20books/Zotero/storage/IMT92TIC/324446a0.html))
- The method is "named after Joshua Barnes and Piet Hut"; "It is notable for having order O(n log n) compared to a direct-sum algorithm which would be O(n2)"; "The space is recursively subdivided into octants until each subdivision contains 0 or 1 bodies"; a cell is far enough away when the ratio of its width to its distance is "smaller than a threshold value θ"; "larger values of θ increase the speed of the simulation but decreases its accuracy", and with θ = 0 the method "degenerates to a direct-sum algorithm". **Documented** ([Wikipedia, Barnes–Hut simulation](https://en.wikipedia.org/wiki/Barnes%E2%80%93Hut_simulation))
- Demmel's Berkeley lecture (19 April 2016): Barnes–Hut is "An O(N log N) approximate algorithm for the N-Body problem", using centre of mass and total mass "if D/r < θ", and "Good for low accuracy calculations"; Greengard and Rokhlin's fast multipole method (*J. Comp. Phys.* 73, 1987) is "An O(N) approximate algorithm"; the centre-of-mass approximation is "not new", going back to Newton. **Documented** ([J. Demmel, CS 267 lecture 25, "Hierarchical Methods for the N-Body problem"](https://people.eecs.berkeley.edu/%7Edemmel/cs267_Spr16/Lectures/lecture25_NBody_jwd16_4pp.pdf))
- Greengard is "co-inventor with Vladimir Rokhlin Jr. of the fast multipole method (FMM) in 1987", "recognized as one of the top-ten algorithms of the 20th century". **Documented** ([Wikipedia, Leslie Greengard](https://en.wikipedia.org/wiki/Leslie_Greengard))
- The NEMO toolkit's `hackforce`, by Joshua E. Barnes, computes forces "using an adaptive Eulerian tree" with O(N log N) interactions; its opening-angle tolerance defaults to 1.0. **Documented** ([NEMO manual, hackforce](https://bima.astro.umd.edu/nemo/man_html/hackforce.1.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Barnes–Hut simulation](https://en.wikipedia.org/wiki/Barnes%E2%80%93Hut_simulation) | Wikipedia | The tree, the opening angle, and the speed–accuracy trade-off |
| Start | [The Barnes-Hut Galaxy Simulator](https://beltoforion.de/en/barnes-hut-galaxy-simulator/) | Ingo Berg | Diagrams, pseudocode, an animation of θ and a video of two colliding galaxies (its remarks on θ are not consistent throughout) |
| Deeper | [Hierarchical Methods for the N-Body problem](https://people.eecs.berkeley.edu/%7Edemmel/cs267_Spr16/Lectures/lecture25_NBody_jwd16_4pp.pdf) | J. Demmel, UC Berkeley CS 267 (2016) | Barnes–Hut beside the fast multipole method, and running both in parallel |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [hackforce manual page](https://bima.astro.umd.edu/nemo/man_html/hackforce.1.html) | NEMO toolkit, J. E. Barnes | A working tree code by one of the inventors, still distributed |

**Gaps:** the text of the 1986 *Nature* letter was not opened (only its record), and neither was Barnes and Hut's 1989 error analysis (the request timed out). Appel's earlier tree method (1985) is not covered. No video page could be opened. The program uses a Plummer sphere of stars and monopole (centre-of-mass) approximations only.

## 9. Karp–Rabin fingerprints

**When / where:** Richard M. Karp and Michael O. Rabin, "Efficient randomized pattern-matching algorithms", *IBM Journal of Research and Development* 31(2), pp. 249–260, March 1987 (from a conference at Yorktown Heights, December 1985); building on Rabin's "Fingerprinting by Random Polynomials", Harvard technical report, 1981.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Knuth, Morris and Pratt, and Boyer and Moore (Era 6) had made searching for a word in a text fast by careful bookkeeping about the pattern. Karp and Rabin did something simpler and stranger: they stopped comparing letters. Each window of the text is turned into a short number, a fingerprint, the remainder when the window, read as a big number, is divided by a prime. Sliding the window one place updates the fingerprint in a few steps. Letters are compared only where fingerprints agree. Different windows can share a fingerprint, so the method could be fooled, except that the prime is picked at random after the text is fixed, and then nobody, not even someone who wrote the text to cause trouble, can make false alarms common. The same trick searches for many patterns at once, works in two dimensions, and is a standard way to spot copied passages.

**What hurt:** fast exact string search needed intricate preprocessing of each pattern, did not extend easily to many patterns or two-dimensional pictures, and the simple method could take m comparisons at every position.
**The step forward:** compare short rolling fingerprints modulo a randomly chosen prime instead of letters; false alarms are rare with high probability whatever the input, and the method extends at once to many patterns and to higher dimensions.

**Evidence and certainty**

- Karp and Rabin, *IBM J. Res. Dev.* 31(2), pp. 249–260 (1987), DOI 10.1147/rd.312.0249, from a conference held 1 December 1985 at Yorktown Heights: randomized algorithms for finding a pattern in a text that work on much shorter fingerprints instead of the strings, use a constant amount of storage, run essentially in real time, are simple to implement, and extend to higher-dimensional pattern matching. **Documented** ([Hebrew University research portal record](https://cris.huji.ac.il/en/publications/efficient-randomized-pattern-matching-algorithms/))
- The algorithm was "created by Richard M. Karp and Michael O. Rabin" (March 1987); "It uses a rolling hash to quickly filter out positions of the text that cannot match the pattern"; expected time "linear in the combined length of the pattern and text", worst case "the product of the two lengths"; it is "a useful algorithm for multiple pattern search"; "A practical application of the algorithm is detecting plagiarism"; "the hash function should be selected randomly from a family of hash functions". **Documented** ([Wikipedia, Rabin–Karp algorithm](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm))
- Rabin's fingerprint (Harvard technical report "Fingerprinting by Random Polynomials", 1981) divides the message, read as a polynomial over GF(2), by a randomly chosen irreducible polynomial and keeps the remainder; LBFS uses it to "implement variable size shift-resistant blocks". **Documented** ([Wikipedia, Rabin fingerprint](https://en.wikipedia.org/wiki/Rabin_fingerprint))
- Lecture notes "Fingerprinting & Applications" (CS 174, 3 May 2007): "pick a random prime p ∈ {2, ..., T}" and "compute Fp(Y) = Y mod p"; the error is one-sided (a false "match" only); a false match requires p to divide the difference, and "the number of primes that divide any given n-bit number is at most π(n)", giving "Pr[Error] ≤ π(mn)/π(T)". **Documented** ([CS 174 notes, on Varun Kanade's Oxford page](https://www.cs.ox.ac.uk/people/varun.kanade/teaching/CS174-Fall2012/fingerprint.pdf))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Rabin–Karp algorithm](https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm) | Wikipedia | Rolling hashes, worked examples, many patterns |
| Deeper | [Fingerprinting & Applications](https://www.cs.ox.ac.uk/people/varun.kanade/teaching/CS174-Fall2012/fingerprint.pdf) | CS 174 lecture notes (2007) | Why a random prime makes false matches unlikely, with the counting argument |
| Deeper | [Rabin fingerprint](https://en.wikipedia.org/wiki/Rabin_fingerprint) | Wikipedia | The polynomial version, and its use for finding block boundaries in file systems |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Efficient randomized pattern-matching algorithms](https://cris.huji.ac.il/en/publications/efficient-randomized-pattern-matching-algorithms/) | R. Karp, M. Rabin, *IBM J. Res. Dev.* (1987), Hebrew University record | Citation and abstract of the paper |

**Gaps:** the text of the 1987 paper and Rabin's 1981 report were not opened; the IEEE Xplore page returned no content. No video page could be opened. The program reads letters as base-4 digits and uses a random prime modulus, the textbook form; Karp and Rabin's exact fingerprint families were not checked. Its bound (at most 15 prime factors of a nonzero number below 2^64) is the program's own simple version of the counting argument in the notes.

## 10. TCP congestion control

**When / where:** Van Jacobson (Lawrence Berkeley Laboratory) and Michael J. Karels (University of California at Berkeley), "Congestion Avoidance and Control", *ACM SIGCOMM '88* (*Computer Communication Review* 18(4), August 1988; revised November 1988); Dah-Ming Chiu and Raj Jain (Digital Equipment Corporation), "Analysis of the Increase and Decrease Algorithms for Congestion Avoidance in Computer Networks", *Computer Networks and ISDN Systems* 17, 1989.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** In October 1986 the connection between Lawrence Berkeley Laboratory and the University of California at Berkeley delivered 40 bits per second instead of 32,000. Nothing was broken. Every computer was obeying the protocol: send as much as the receiver allows, and resend whatever is not acknowledged in time. When routers' buffers filled, packets were lost, timers expired, and the resent copies made the queues longer still. Jacobson and Karels made each sender treat a lost packet as a signal that the network is overloaded: start slowly, grow the amount in flight by one packet per round trip, and halve it after a loss. They also made the timers measure how much the round-trip time varies, not just its average. A year later Chiu and Jain showed with simple geometry why adding on the way up and multiplying on the way down is the rule that brings competing senders to full use and equal shares. Their rules became the core of the Internet standard for TCP, so that computers that never talk to each other share links politely.

**What hurt:** senders that ignored congestion overfilled router buffers; losses caused timeouts and retransmissions, duplicates crowded out useful data, and the early Internet suffered "congestion collapses".
**The step forward:** each sender infers congestion from packet loss and controls its own window: slow start, additive increase, multiplicative decrease, and retransmission timers based on the mean and variation of the round-trip time, with exponential backoff.

**Evidence and certainty**

- Jacobson and Karels, LBL and UC Berkeley, November 1988: "In October of '86, the Internet had the first of what became a series of 'congestion collapses'", during which "the data throughput from LBL to UC Berkeley" "dropped from 32 Kbps to 40 bps"; seven new algorithms, including "(i) round-trip-time variance estimation", "(ii) exponential retransmit timer backoff", "(iii) slow-start", "(v) dynamic window sizing on congestion", "(vi) Karn's clamped retransmit backoff" and "(vii) fast retransmit"; the principle "A new packet isn't put into the network until an old packet leaves"; slow start: "When starting or restarting after a loss, set cwnd to one packet", "On each ack for new data, increase cwnd by one packet"; "On any timeout, set cwnd to half the current window size (this is the multiplicative decrease)" and "On each ack for new data, increase cwnd by 1/cwnd (this is the additive increase)". **Documented** ([Jacobson and Karels, "Congestion Avoidance and Control", 1988, on a Princeton course page](https://www.cs.princeton.edu/courses/archive/fall08/cos561/papers/jacobson88.pdf))
- Chiu and Jain, Digital Equipment Corporation, *Computer Networks and ISDN Systems* 17 (1989) 1–14: "a simple additive increase and multiplicative decrease algorithm satisfies the sufficient conditions for convergence to an efficient and fair state regardless of the starting state of the network"; the system is viewed "as a trajectory through an n-dimensional vector space"; "All allocations for which x1 = x2 are fair allocations"; the fairness index is bounded "between 0 and 1". **Documented** ([Chiu and Jain, 1989, on a UC Santa Barbara course page](https://sites.cs.ucsb.edu/~ravenben/classes/papers/cj89.pdf))
- RFC 5681 (Allman, Paxson and Blanton, September 2009, Standards Track, obsoleting RFC 2581) "defines TCP's four intertwined congestion control algorithms": slow start, congestion avoidance, fast retransmit and fast recovery; after a timeout "ssthresh = max (FlightSize / 2, 2*SMSS)" and the window is set to one segment; fast retransmit "uses the arrival of 3 duplicate ACKs"; "The core algorithms we describe were developed by Van Jacobson". **Documented** ([RFC 5681](https://rfc-editor.org/rfc/rfc5681))
- Byers's Boston University seminar notes (14 September 1999) summarize the two papers: Chiu and Jain proved additive increase with multiplicative decrease sufficient for convergence to fairness and efficiency, "but they have not proved the necessity of the condition", and their model assumes synchronous feedback. **Documented** ([CS791 scribe notes, Boston University](https://cs-web.bu.edu/fac/byers/courses/791/F99/scribe_notes/cs791-notes-990914.html))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [CS791 notes: Chiu–Jain and Jacobson](https://cs-web.bu.edu/fac/byers/courses/791/F99/scribe_notes/cs791-notes-990914.html) | J. Byers, Boston University (1999) | A short walk through both papers, with their weak points |
| Deeper | [RFC 5681: TCP Congestion Control](https://rfc-editor.org/rfc/rfc5681) | IETF (2009) | The rules as the Internet standard states them today |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Congestion Avoidance and Control](https://www.cs.princeton.edu/courses/archive/fall08/cos561/papers/jacobson88.pdf) | V. Jacobson, M. Karels (1988) | The collapse, the seven algorithms, and the reasoning behind them |
| Scholar | [Analysis of the Increase and Decrease Algorithms for Congestion Avoidance](https://sites.cs.ucsb.edu/~ravenben/classes/papers/cj89.pdf) | D.-M. Chiu, R. Jain, *Computer Networks and ISDN Systems* (1989) | Why additive increase and multiplicative decrease converge to fairness |

**Gaps:** no video page could be opened. Which Berkeley Unix release first shipped the rules is not confirmed by an opened source. The program's model (one bottleneck, synchronous ticks, a receiver that keeps out-of-order packets) is far simpler than the 1986 Internet and shows the mechanism, not the thousandfold collapse.

## 11. Shor's factoring algorithm

**When / where:** Peter Shor, Bell Labs, Murray Hill, New Jersey, 1994: "Algorithms for Quantum Computation: Discrete Logarithms and Factoring" (1994; DIMACS technical report 94-37); journal version "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer", *SIAM Journal on Computing* 26 (arXiv quant-ph/9508027, 1995).
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Public-key cryptography (Era 6) rested on a bet: multiplying two primes is easy, and undoing it is so hard that no one will manage it for numbers of hundreds of digits. In 1994 Peter Shor, at Bell Labs, showed that the bet depends on the kind of computer. On a quantum computer, whose memory can hold a superposition of many values that interfere like waves, factoring takes time that grows only like a power of the number of digits. The algorithm turns factoring into finding the period of a repeating sequence, and finds the period with a quantum version of the Fourier transform. No quantum computer large enough existed then, and none does yet: in 2001 a group at IBM factored 15. But the result changed what people expected of quantum machines, and became a main reason to build them, and to design public-key systems that do not rely on factoring.

**What hurt:** every known classical method for factoring large numbers and computing discrete logarithms takes more than polynomial time, and it was unclear whether any physically realistic computer could do better.
**The step forward:** a polynomial-time algorithm for factoring and discrete logarithms on a quantum computer: reduce factoring to period finding, and find the period by quantum interference (the quantum Fourier transform) followed by continued fractions.

**Evidence and certainty**

- Shor, arXiv quant-ph/9508027 (submitted 30 August 1995, revised 25 January 1996; DOI 10.1137/S0097539795293172), "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer": factoring and discrete logarithms are thought hard on classical computers and underlie several cryptosystems; "Efficient randomized algorithms are given for these two problems on a hypothetical quantum computer", with running time polynomial in the number of digits. **Documented** ([arXiv, quant-ph/9508027](https://arxiv.org/abs/quant-ph/9508027))
- DIMACS technical report 94-37, Shor, "Algorithms for Quantum Computation: Discrete Log and Factoring": "A computer is generally considered to be a universal computational device"; it shows "these computers can factor integers and find discrete logarithms in polynomial time", while all known classical algorithms take superpolynomial time. **Documented** ([DIMACS TR 94-37](https://archive.dimacs.rutgers.edu/TechnicalReports/abstracts/1994/94-37.html))
- "It was developed in 1994 by the American mathematician Peter Shor"; it consists of "A classical reduction of the factoring problem to the problem of order-finding" and a quantum order-finding step; continued fractions "extract the period from the measurement outcomes"; a 2001 IBM group used "an NMR implementation of a quantum computer with seven qubits"; of later small demonstrations, "none of these demonstrations fulfill the requirements of Shor's algorithm"; "it might be feasible to defeat RSA by constructing a large enough quantum computer", and beating classical computers "may require quantum computers with millions of qubits". **Documented** ([Wikipedia, Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm))
- Shor was "working at Bell Labs in Murray Hill, New Jersey"; "its formulation in 1994 was a powerful motivator for the design and construction of quantum computers"; in 2001 IBM "factored 15 into 3 × 5, using an NMR implementation", though "some doubts have been raised" since "no entanglement was observed" (quoting Wikipedia). **Documented** ([History of Information, "Formulation of Shor's Algorithm"](https://www.historyofinformation.com/detail.php?id=3877))
- Smolin, Smith and Vargo (IBM): earlier small demonstrations "factored numbers no larger than 21"; a "compiled" version factors any product of unequal primes with two qubits, so "the correct measure of difficulty when implementing Shor's algorithm is not the size of number factored". **Documented** ([Smolin, Smith and Vargo, "Pretending to factor large numbers on a quantum computer", 2013](https://ar5iv.labs.arxiv.org/html/1301.7007))
- Gidney (Google, 2025) estimates that "a 2048 bit RSA integer could be factored in less than a week using less than one million noisy qubits", "compared to 20 million in Gidney+Ekerå 2019". **Documented** (an estimate, not a demonstration) ([Google Research, "How to factor 2048 bit RSA integers with less than a million noisy qubits"](https://research.google/pubs/how-to-factor-2048-bit-rsa-integers-with-less-than-a-million-noisy-qubits/))

**Watch**

No video page could be opened (see **Gaps**).

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) | Wikipedia | The reduction, the quantum step, and the experiments so far |
| Deeper | [Pretending to factor large numbers on a quantum computer](https://ar5iv.labs.arxiv.org/html/1301.7007) | J. Smolin, G. Smith, A. Vargo (IBM, 2013) | Why "we factored N on a quantum computer" needs careful reading |
| Deeper | [How to factor 2048 bit RSA integers with less than a million noisy qubits](https://research.google/pubs/how-to-factor-2048-bit-rsa-integers-with-less-than-a-million-noisy-qubits/) | C. Gidney, Google (2025) | What breaking real RSA would take, as currently estimated |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer](https://arxiv.org/abs/quant-ph/9508027) | P. Shor, arXiv (1995), *SIAM J. Computing* | The algorithm and its analysis |
| Scholar | [Algorithms for Quantum Computation: Discrete Log and Factoring](https://archive.dimacs.rutgers.edu/TechnicalReports/abstracts/1994/94-37.html) | P. Shor, DIMACS TR 94-37 (1994) | The 1994 announcement |

**Gaps:** the 1994 conference paper itself was not opened; its venue (the IEEE Symposium on Foundations of Computer Science, 1994) is not confirmed by an opened source. The *SIAM J. Computing* year is given as 1996 by one source and 1997 elsewhere, so it is left out. No video page could be opened. The program simulates the quantum step by storing every amplitude, which is only possible for tiny N; it does not model quantum gates or errors.

## 12. The Burrows–Wheeler transform

**When / where:** Michael Burrows and David Wheeler, Systems Research Center of Digital Equipment Corporation, Palo Alto, "A Block-sorting Lossless Data Compression Algorithm", SRC Research Report 124, 10 May 1994; the transform found by Wheeler in 1983 at AT&T Bell Laboratories; turned into a search index by Paolo Ferragina and Giovanni Manzini in 2000.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** Lempel and Ziv (Era 6) compressed text by pointing back at earlier copies. Burrows and Wheeler found a different route, and a stranger one. Take a block of text, write out every rotation of it, sort the rotations, and keep only the last letter of each. The result is the same letters in a new order, where letters that came before similar contexts now sit side by side, so it compresses well with very simple methods. And the shuffle can be undone exactly, from the last column and one number. Wheeler had found it in 1983 and not published it; the 1994 report compressed text better than the Lempel–Ziv programs of the day at a comparable speed. Six years later Ferragina and Manzini showed that the same column, with a few small tables, can answer "how many times does this pattern occur?" without the original text, and that turned a compression trick into the index used by programs that align DNA reads to a genome.

**What hurt:** fast compressors based on Lempel and Ziv's methods compressed less well than slow statistical modelling; full-text indexes such as suffix trees and arrays took many times the space of the text.
**The step forward:** a reversible block-sorting permutation that groups letters by their following context, so move-to-front and Huffman coding compress it well; and, through the LF mapping, a compressed index that counts and locates patterns.

**Evidence and certainty**

- Burrows and Wheeler, SRC Research Report 124, 10 May 1994: "We describe a block-sorting, lossless data compression algorithm, and our implementation of that algorithm"; "The algorithm works by applying a reversible transformation to a block of input text"; "The transformation does not itself compress the data, but reorders it to make it easy to compress with simple algorithms such as move-to-front coding"; it achieves "speed comparable to algorithms based on the techniques of Lempel and Ziv" but "compression close to the best statistical modelling techniques"; "The size of the input block must be large (a few kilobytes) to achieve good compression"; "The algorithm described here was discovered by one of the authors (Wheeler) in 1983 while he was working at AT&T Bell Laboratories, though it has not previously been published"; on the fourteen Calgary Corpus files, mean bits per character were compress 3.63, gzip 2.71, and theirs 2.43 (pp. 15–16). **Documented** ([Burrows and Wheeler, SRC Research Report 124, on a Cambridge course page](https://www.cl.cam.ac.uk/teaching/0304/DSAlgs/SRC-124.pdf))
- The transform "was invented by David Wheeler in 1983, and later published by him and Michael Burrows in 1994"; it "rearranges a character string into runs of similar characters, in a manner that can be reversed"; it is used "in software such as bzip2"; Bowtie, BWA and SOAP2 are alignment programs "that use the Burrows–Wheeler transform". **Documented** ([Wikipedia, Burrows–Wheeler transform](https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform))
- Langmead's tutorial (24 November 2013): the BWT is "a way of permuting the characters of a string T into another string"; the LF mapping (the i-th occurrence of a character in the last column is the i-th in the first) makes it reversible and searchable; in 2000 Ferragina and Manzini showed that the BWT with small auxiliary structures is a space-efficient index, the FM index; backward search applies "the LF Mapping repeatedly to find the range of rows prefixed by successively longer proper suffixes of P". **Documented** ([B. Langmead, "Introduction to the Burrows-Wheeler Transform and FM Index", on a Cambridge course page](https://www.cl.cam.ac.uk/teaching/2324/Bioinfo/papers/bwt_fm.pdf))
- Bowtie was "originally developed by Ben Langmead et al. at the University of Maryland in 2009", gaining speed partly by "implementing the Burrows–Wheeler transform for aligning", with a footprint of "around 2.2GB for the human genome". **Documented** ([Wikipedia, Bowtie](https://en.wikipedia.org/wiki/Bowtie_(sequence_analysis)))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Deeper | [Lecture 5: Library Complexity and Short Read Alignment (Mapping)](https://ocw.mit.edu/courses/7-91j-foundations-of-computational-and-systems-biology-spring-2014/resources/lecture-5-library-complexity-and-short-read-alignment-mapping/) | MIT OpenCourseWare, David Gifford, 7.91J (Spring 2014) | Builds an FM index from the Burrows–Wheeler transform to align DNA reads, with video and transcript |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Burrows–Wheeler transform](https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform) | Wikipedia | The transform worked by hand, and its inverse |
| Deeper | [Introduction to the Burrows-Wheeler Transform and FM Index](https://www.cl.cam.ac.uk/teaching/2324/Bioinfo/papers/bwt_fm.pdf) | B. Langmead (2013) | The LF mapping and backward search, step by step |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A Block-sorting Lossless Data Compression Algorithm](https://www.cl.cam.ac.uk/teaching/0304/DSAlgs/SRC-124.pdf) | M. Burrows, D. Wheeler, SRC Research Report 124 (1994) | The transform, its inverse, and the measurements |

**Gaps:** Ferragina and Manzini's 2000 paper was not opened; it is cited through Langmead's tutorial. The bzip2 manual could not be fetched. The program codes move-to-front output with a single Huffman code per block, without bzip2's run-length and multiple-table stages, so its sizes are not bzip2's. Its Deflate figure includes zlib's header and is for an 18,616-byte text, far smaller than the Calgary Corpus.

## 13. AdaBoost

**When / where:** Yoav Freund and Robert Schapire, AT&T: extended abstract at the Second European Conference on Computational Learning Theory (EuroCOLT), Barcelona, March 1995; "A decision-theoretic generalization of on-line learning and an application to boosting", *Journal of Computer and System Sciences* 55(1), pp. 119–139, 1997; answering a question posed by Michael Kearns and Leslie Valiant (1988–1989) and first answered, impractically, by Schapire (1990) and Freund.
**Atlas:** to be mapped · **Code:** planned

> **Field note.** By the 1980s the people who studied learning machines had a precise definition of learning: from examples, find a rule that is right almost always. Kearns and Valiant asked a sharp question. Suppose all you can find is a rule that is right slightly more often than a coin toss. Can such weak rules always be combined into a strong one? Schapire proved in 1990 that they can, and Freund found another construction, but both were impractical. In 1995 Freund and Schapire found a simple way: weight the examples, and after each weak rule, make the examples it got right count less, so the next rule must attend to the ones still being missed; at the end, let the rules vote, the better ones with louder voices. They proved the training error falls exponentially fast. AdaBoost became a standard tool, won the 2003 Gödel Prize, and showed that a theoretical question about learning could produce a practical method.

**What hurt:** simple classifiers such as single-threshold tests are easy to find but inaccurate, and earlier constructions that combined them into accurate ones were too complicated to use.
**The step forward:** an adaptive reweighting scheme that focuses each new weak classifier on the examples the previous ones missed, combined by a weighted vote, with a proven exponential bound on training error.

**Evidence and certainty**

- Freund and Schapire, AT&T Labs, *Journal of Computer and System Sciences* 55(1):119–139, 1997, with "An extended abstract of this work appeared in the Proceedings of the Second European Conference on Computational Learning Theory, Barcelona, March, 1995": "We show that the multiplicative weight-update rule of Littlestone and Warmuth can be adapted to this model"; in AdaBoost "The update rule reduces the probability assigned to those examples on which the hypothesis makes a good prediction", with β = ε/(1 − ε) and a final vote weighted by log(1/β) (pp. 12–13); Theorem 6 bounds the training error by a product of 2√(ε(1 − ε)) over the rounds (p. 14); "Schapire showed that any weak learning algorithm can be efficiently transformed" into a strong one (p. 11). **Documented** ([Freund and Schapire, 1997, on a Northeastern course page](https://khoury.northeastern.edu/home/vip/teach/IRcourse/6_ML/other_notes/freund_schapire_adaboost_journal.pdf))
- AdaBoost, "short for Adaptive Boosting", was "formulated by Yoav Freund and Robert Schapire in 1995", who "won the 2003 Gödel Prize for their work"; it "is typically used to combine weak base learners (such as decision stumps)"; its exponential loss can "result in excessive weights being assigned to outliers"; with decision trees it "is often referred to as the best out-of-the-box classifier"; the Viola–Jones object detection framework uses a boosted cascade. **Documented** ([Wikipedia, AdaBoost](https://en.wikipedia.org/wiki/AdaBoost))
- The question "is weakly learnability equivalent to strong learnability?" was posed by Kearns and Valiant (unpublished manuscript 1988, ACM STOC 1989) and "got a positive answer by Robert Schapire (1990, proof by construction, not practical)"; Freund gave another, also impractical, answer in 1993; the question is called "the origin of boosting machine learning algorithms". **Documented** ([Wikipedia, Michael Kearns](https://en.wikipedia.org/wiki/Michael_Kearns_(computer_scientist)))

**Watch**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [Lecture 17: Learning: Boosting](https://www.ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/resources/lecture-17-learning-boosting) | MIT OpenCourseWare, Patrick Winston, 6.034 (Fall 2010) | "Can multiple weak classifiers be used to make a strong one?", worked through with video and transcript |

**Read**

| Level | Link | Source | Why |
|---|---|---|---|
| Start | [AdaBoost](https://en.wikipedia.org/wiki/AdaBoost) | Wikipedia | The algorithm, its loss function, and where it is used |
| Deeper | [Michael Kearns](https://en.wikipedia.org/wiki/Michael_Kearns_(computer_scientist)) | Wikipedia | The weak-versus-strong learning question that started boosting |

**Original sources**

| Level | Link | Source | Why |
|---|---|---|---|
| Scholar | [A decision-theoretic generalization of on-line learning and an application to boosting](https://khoury.northeastern.edu/home/vip/teach/IRcourse/6_ML/other_notes/freund_schapire_adaboost_journal.pdf) | Y. Freund, R. Schapire, *J. Comput. Syst. Sci.* (1997) | AdaBoost, its weight update, and the training error bound |

**Gaps:** the 1995 EuroCOLT extended abstract, Schapire's 1990 paper "The strength of weak learnability" and Kearns and Valiant's manuscript were not opened. The program's data (a circle in a square) and its stumps are its own illustration; the paper's experiments are not repeated.

## What the era leaves behind

- **Chance as a tool.** Annealing (4) searches by accepting bad moves at random; Karp and Rabin (9) choose a prime at random so that no text can fool them; zero-knowledge proofs (6) convince by random questions; AdaBoost (13) and backpropagation (7) learn by repeated small corrections.
- **Guarantees over whole sequences.** Amortized analysis (5) judges a data structure by the total cost of everything done with it; splay trees adapt to what is used.
- **Computers that cooperate.** Byzantine agreement (3) survives parts that lie; TCP's congestion control (10) lets senders that never speak to each other share links fairly; Merkle's trees (2) let anyone check a piece of shared data against one short hash.
- **Short summaries of big things.** A hash for a tree of data (2), a fingerprint for a window of text (9), a centre of mass for a cube of stars (8), a sorted column for a block of text (12).
- **Polynomial versus practical.** The ellipsoid method (1) settled that linear programming is polynomial and was slow; interior-point methods were both. Shor's algorithm (11) is polynomial on a machine far larger than the small demonstrations the sources describe.
- **Machines that learn.** Backpropagation (7) trains hidden layers; boosting (13) combines weak rules into strong ones.

Era 8 picks up in the mid-1990s: the algorithms of the Web, of genomes, and of learning at scale.
