# Era 8 — The Web, the Genome and the Ledger (plan)

*1995 to 2008. Topic list in order of time, with the exceptions noted below. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the seventh era the species' computers joined into networks and began to learn. In this one the network becomes a Web of tens of millions of pages, which must be searched, ranked, copied to caches and cleared of duplicates; its laboratories read the species' own genome from millions of shredded fragments; its data streams past faster than it can be kept; and its computers, now thousands in one room, must work as one and agree on one history. The methods of this era are built for scale: they summarize instead of storing, sample instead of measuring everything, settle for a provable approximation, and assume that some part is always failing. Two older questions are closed along the way: whether primality can be decided without chance, and whether a computer can learn what happened a thousand steps ago.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | Support vector machines | Vapnik and Chervonenkis 1964; kernels 1992; soft margin 1995 | Moscow; AT&T Bell Laboratories | A perceptron's line may pass close to the examples; curved boundaries needed explicit features; data are rarely separable | The widest margin, fixed by support vectors; kernels; the soft margin | The perceptron (Era 5, 9) |
| 2 | Approximation by semidefinite programming | STOC 1994; *J. ACM* 1995 | MIT; IBM Yorktown Heights | MAX CUT is NP-hard, and the best guarantee was the 1/2 of a coin flip | Relax to unit vectors, solve the semidefinite program, round with a random hyperplane: 0.878 | NP-completeness (Era 6, 8); linear programming (Era 7, 1) |
| 3 | Streaming sketches | Flajolet–Martin 1983–1985; Alon, Matias and Szegedy 1996; Count-Min 2005; HyperLogLog 2007 | Tel Aviv, Bell Labs, AT&T; INRIA, IBM; Rutgers | Exact counts need memory for every item, and a stream cannot be read twice | Small random summaries updated in one pass, with guaranteed error; lower bounds | Hashing (Era 5, 4) |
| 4 | Consistent hashing | 1997; Akamai 1998; Chord 2001 | MIT | Hash-mod-n placement moves nearly every key when a server joins or leaves | Keys and servers on one circle; each key to the next server; about 1/n of the keys move | Hashing (Era 5, 4) |
| 5 | MinHash and locality-sensitive hashing | Broder 1997; Indyk and Motwani 1998 | DEC Systems Research Center; Stanford | Near-duplicates among millions of pages; every pair costs n² comparisons | Minimum hashes estimate resemblance; hashes that make similar items collide | Karp–Rabin fingerprints (Era 7, 9) |
| 6 | Long short-term memory | Thesis 1991; report 1995; journal 1997; forget gate 1999 | TU München; IDSIA, Lugano | Error signals through time vanish or explode, so recurrent networks forget | A memory cell whose error flows back unchanged, guarded by learned gates | Backpropagation (Era 7, 7) |
| 7 | PageRank | Project 1996; paper April 1998 | Stanford | Keyword search returned junk; directories could not keep up | Rank by links: the stationary distribution of a damped random surfer, by the power method | Markov chains (Era 4, 3) |
| 8 | Paxos | Written and submitted 1989 or 1990; published May 1998 | Lamport, at the Systems Research Center (SRC) | Replicas must agree though messages are delayed or lost and computers stop | Numbered ballots, promise then accept, overlapping majorities | The Byzantine generals (Era 7, 3); logical clocks (Era 6, 13) |
| 9 | Genome assembly with de Bruijn graphs | Idury and Waterman 1995; Pevzner, Tang and Waterman 2001 | USC; UC San Diego | Overlap assembly is a Hamiltonian path problem, broken by repeats | Reads cut into k-letter words; the genome is an Eulerian path | Euler's bridges (Era 3, 7) |
| 10 | PRIMES is in P | 6 August 2002; *Annals* 2004 | IIT Kanpur | Fast primality tests were randomized, special or conditional | (x − a)ⁿ ≡ xⁿ − a modulo (xʳ − 1, n) for a few a | Randomized primality tests (Era 6, 10) |
| 11 | MapReduce | December 2004 | Google | Programs on thousands of failing machines had to handle distribution themselves | Map and reduce: deterministic tasks a library can schedule and re-run | Sorting and merging (Era 4, 9) |
| 12 | Compressed sensing | Preprint 2004; journal 2006 | Caltech, UCLA; Stanford | Sampling at the full rate wastes measurements on sparse signals | Random measurements, then ℓ1 minimization finds the sparse signal exactly | Linear programming (Era 7, 1) |
| 13 | Bitcoin's proof-of-work ledger | 31 October 2008; genesis block 3 January 2009 | Online, by "Satoshi Nakamoto" | Electronic cash can be double-spent without a trusted bank | A hash chain sealed by proof of work; the chain with the most work wins | Merkle's trees and the Byzantine generals (Era 7, 2 and 3) |

## Decisions after the reference catalog

- The era runs from 1995 (the soft-margin support vector machine and Goemans and Williamson's journal paper) to 2008 (Bitcoin), and the topics are ordered by the year each development first appeared in public, except where noted.
- Support vector machines (1) are placed by the 1995 paper that gave them their name and the soft margin; the 1964 and 1992 steps share the page.
- Goemans and Williamson (2) are placed by the 1995 journal paper, as Karp and Rabin were in Era 7; the 1994 conference version shares the page.
- Streaming sketches (3) are placed by Alon, Matias and Szegedy's 1996 paper, which the sources credit with founding the field; Flajolet and Martin's earlier counting and the later Count-Min and HyperLogLog share the page.
- Consistent hashing (4) and MinHash (5) both appeared in 1997; consistent hashing comes first by its May conference. Locality-sensitive hashing (1998) shares MinHash's page.
- Paxos (8) is placed by its 1998 publication, though it was written about eight years earlier; the sources disagree on whether it was first submitted in 1989 or 1990, and the catalog marks that **Disputed**.
- Genome assembly (9) is placed by the 2001 EULER paper, with Idury and Waterman's 1995 method on the same page.
- Compressed sensing (12) is placed by the 2004 preprint; the 2006 journal versions share the page.
- Several pages could not be opened: every video site, a few publishers' pages behind a browser check, and some course pages behind logins. The catalog lists them as gaps instead of citing them.
- Every program prints only plain ASCII and uses fixed seeds, so the outputs are the same on every machine.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
