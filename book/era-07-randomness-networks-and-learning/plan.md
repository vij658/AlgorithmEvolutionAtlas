# Era 7 — Randomness, Networks and Learning (plan)

*1979 to 1995. Topic list in order of time, with the exceptions noted below. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the sixth era the species learned that some of its problems may have no fast method, and turned that hardness into secrecy. In this one it learns to live with hardness in other ways. It flips coins on purpose: to search, to check, to prove. Its computers join into networks, and it has to make them agree when some parts fail or lie, and share their links without choking them. It builds machines that learn rules from examples instead of being told them. And near the end of the era it discovers, on paper, that a different kind of computer, one that works by quantum interference, would undo the hardness its secrets rest on.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | Linear programming in polynomial time | Klee–Minty 1972; Khachiyan 1979; Karmarkar 1984 | Moscow; AT&T Bell Laboratories | The simplex method can take exponentially many steps | The ellipsoid method (polynomial, slow); interior-point methods (polynomial, fast) | The simplex method (Era 4, 11) |
| 2 | Merkle's hash trees | 1979 (patent 1982) | Stanford | Checking one block of a collection needed a fingerprint for every block | Hash fingerprints in pairs up to one root; log₂ n hashes per check; many one-time keys under one public key | Public keys (Era 6, 10); hashing (Era 5, 4) |
| 3 | The Byzantine generals | 1980; 1982 | SRI International | A faulty part can tell different parts different things | 3m + 1 parts survive m liars (OM(m)); with signatures, any number (SM(m)) | Logical clocks (Era 6, 13) |
| 4 | Simulated annealing | 1983; Černý 1985 | IBM Yorktown Heights; Bratislava | Improvement by small steps stops at the first local optimum | Accept worse moves with probability e^(−Δ/T); cool slowly | Monte Carlo (Era 4, 10); NP-completeness (Era 6, 8) |
| 5 | Splay trees and amortized analysis | 1985 | AT&T Bell Laboratories | Balanced trees need bookkeeping and judge each operation alone | Rotate each accessed key to the root; prove costs over whole sequences with a potential | AVL trees (Era 5, 11) |
| 6 | Zero-knowledge proofs | 1985; 1986 for all of NP | MIT, Toronto; Technion, Hebrew University | Proving you know a secret meant revealing something about it | Interactive, randomized proofs that a simulator could fake; commitments for 3-colouring | NP-completeness and public keys (Era 6, 8 and 10) |
| 7 | Backpropagation | Linnainmaa 1970; Werbos 1981; Rumelhart, Hinton and Williams 1986 | Helsinki (1970); the 1986 affiliations are not confirmed | No well-known way to train the hidden layers of a network | The chain rule run backwards: every weight's slope for the cost of one more pass | Rosenblatt's perceptron (Era 5, 9) |
| 8 | The Barnes–Hut tree code | 1986 | Not confirmed by an opened source | Gravity takes N(N − 1) interactions per step | An octree of cubes; distant cubes act as one mass; about N log N, accuracy set by θ | Divide and conquer (Era 6, 5) |
| 9 | Karp–Rabin fingerprints | Presented 1985; published 1987 | Conference at IBM, Yorktown Heights | Fast exact search needed intricate preprocessing; the simple method m × n | Rolling fingerprints modulo a random prime; many patterns; two dimensions | Fast string searching (Era 6, 11); hashing (Era 5, 4) |
| 10 | TCP congestion control | Collapse 1986; paper 1988; Chiu and Jain 1989 | LBL and UC Berkeley; DEC | Senders overran router buffers: congestion collapse | Slow start, additive increase, multiplicative decrease, variance-based timers with backoff | Sharing a resource safely: the semaphore (Era 6, 2) |
| 11 | Shor's factoring algorithm | 1994 | Bell Labs, Murray Hill | Factoring seemed to need superpolynomial time | Reduce to period finding; find the period by a quantum Fourier transform | The FFT and RSA (Era 6, 1 and 10); Euclid (Era 1, 7) |
| 12 | The Burrows–Wheeler transform | Wheeler 1983; report 1994; FM index 2000 | DEC Systems Research Center, Palo Alto | Fast compressors compressed less than slow statistical models | Sort the rotations, keep the last column; move-to-front; the LF mapping inverts and searches | Huffman (Era 5, 3); Lempel–Ziv (Era 6, 12) |
| 13 | AdaBoost | Question 1988; abstract 1995; journal 1997 | AT&T | Weak rules of thumb could not be combined into accurate ones in practice | Reweight the examples after each weak rule; weighted vote; exponential bound on training error | The perceptron (Era 5, 9) |

## Decisions after the reference catalog

- The era runs from 1979 (Khachiyan's note and Merkle's thesis) to 1995 (AdaBoost's first publication), and the topics are ordered by the year each development first appeared in public.
- Linear programming (1) is placed by Khachiyan's 1979 note; Klee and Minty's 1972 cube and Karmarkar's 1984 method share the page. The program uses a primal-dual interior-point method (Mehrotra's predictor-corrector), the kind modern solvers use, rather than Karmarkar's projective method; the page says so.
- Backpropagation (7) is placed at 1986, the paper that made it widely known, with Linnainmaa (1970) and Werbos (1974 and 1981) on the same page; the sources disagree on how to credit Werbos's 1974 work, and the catalog marks that **Disputed**.
- Karp–Rabin (9) is placed by its 1987 journal publication, though it was presented in December 1985.
- The Burrows–Wheeler transform (12) is placed by the 1994 report, with Wheeler's unpublished 1983 discovery and the 2000 FM index on the same page.
- AdaBoost (13) is placed by its 1995 extended abstract; the 1997 journal version is the one that was opened.
- Several pages could not be opened: most video sites, some publishers' pages, and a few redirects. The catalog lists them as gaps instead of citing them.
- Every program prints only plain ASCII and uses fixed seeds, so the outputs are the same on every machine.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
