# Era 5 — The Programmer's Craft (plan)

*1949 to 1965. Topic list in order of time, with the exceptions noted below. Dates were checked in the reference catalog; the catalog's certainty labels win where they differ.*

> **Field note from the visiting historian.** In the fourth era the species learned what a procedure is, and built machines that keep procedures in memory as numbers. In this one they discover how hard it is to write procedures well, and invent a craft for it: routines written once and shared, languages translated by the machine itself, memory organised into lists, tables, trees and heaps, and methods that divide a problem, remember partial answers, or settle one place at a time. By the end of the era they are asking not only whether a problem can be solved, but whether it can be solved in a time that grows like a power of its size.

| # | Topic | Working date | Where | What hurt | The step forward | Builds on |
|---|---|---|---|---|---|---|
| 1 | The subroutine | EDSAC 1949; library and book 1951; paper 1952 | Cambridge | Every program wrote the same routines again | One shared copy, entered by a jump that passes the return address (the Wheeler jump) | The stored program (Era 4, 9) |
| 2 | Regular expressions | Kleene 1951; Rabin and Scott 1959; Thompson 1968 | RAND, IBM, Bell Labs | No exact description of what a finite machine can recognise | Three operations (or, then, repeat); patterns become machines | Nerve nets of McCulloch and Pitts; Turing (Era 4, 7) |
| 3 | Huffman's codes | 1951; published 1952 | MIT | Codes near the entropy, none provably shortest | Merge the two rarest symbols, repeat; optimal prefix code | Shannon (Era 4, 12) |
| 4 | Hashing | Luhn 1953; Amdahl 1954; Dumey 1956; Peterson 1957 | IBM | Finding a record took longer as the file grew | Compute the address from the key; chains or the next free slot | Tables (Era 3) |
| 5 | Dynamic programming | 1952–1957 | RAND | Plans made in stages multiply beyond listing | The principle of optimality: work backwards, store each answer | The problem of points (Era 3, 4) |
| 6 | Linked lists and garbage collection | IPL about 1956; Lisp 1958–1960 | RAND, Carnegie Tech, MIT | Fixed memory could not grow, shrink or be spliced | Cells with the address of the next; mark and sweep | The stored program (Era 4, 9) |
| 7 | Dijkstra's shortest paths | 1956; published 1959 | Amsterdam | Route-finding kept data for every road | Settle the nearest unsettled place, one at a time | Jarník (Era 4, 4); dynamic programming (5) |
| 8 | The compiler, and a grammar for languages | FORTRAN 1954–1957; BNF 1959–1960 | IBM; Paris; the ALGOL committee | Programs written instruction by instruction; languages defined in prose | Formulas translated into efficient code; recursive rules that define a language | The subroutine (1) |
| 9 | Rosenblatt's perceptron | 1957–1958 | Cornell Aeronautical Laboratory | A hand-written rule for every pattern | Weights corrected after each wrong answer | McCulloch and Pitts's neuron |
| 10 | Hoare's Quicksort | 1959; published 1961–1962 | Moscow; Elliott Brothers | Simple sorts take n² steps; merging needs a second memory | Partition around one item from both ends; recurse | Merge sort (Era 4, 9) |
| 11 | AVL trees | 1962 | Moscow | Search trees degenerate into lists | Heights within one; repair by rotations | Linked cells (6) |
| 12 | Heapsort and the heap | Williams 1964; Floyd 1964 | Elliott Automation (Williams) | Quicksort's bad cases; the largest of a changing set | A tree in an array, parents above children; n log n always | Quicksort (10) |
| 13 | Edmonds's matching and the "good" algorithm | 1961; published 1965 | National Bureau of Standards | No agreed meaning of "efficient"; odd cycles defeat matching | Shrink blossoms; polynomial time as the test of a good algorithm | Graph search (7) |

## Decisions after the reference catalog

- The era runs from 1949 (the EDSAC's first programs and the first subroutines) to 1965 (Edmonds's paper and Cobham's), where "efficient" acquires its modern meaning.
- Regular expressions (2) are placed by Kleene's memorandum of December 1951. Thompson's construction (1968) belongs to the next era by date; it is described here because it is the step that turned Kleene's algebra into a working program, and the page says so.
- Linked lists and garbage collection share topic 6: IPL's lists (about 1956) needed a free list; Lisp's automatic reclamation (about 1959) answered the problem lists created.
- Dynamic programming (5) is placed at 1952, the year of Bellman's first publication and RAND memoranda, not at the 1957 book; Bellman's own story of the name (dated 1950) is labelled disputed.
- The compiler (8) is placed by FORTRAN's project start (1954) and delivery (1957); BNF (1959–1960) shares the topic because it describes the languages compilers read.
- Heapsort (12) covers both Williams's algorithm and the heap as a priority queue, and its page returns to Dijkstra's method (7) to show the heap at work.
- Several pages could not be opened: YouTube pages (one rate-limited, others in error) and pages whose permission requests were withdrawn. The catalog lists them as gaps instead of citing them.
- Every program prints only plain ASCII and uses fixed seeds, so the outputs are the same on every machine.

The [reference catalog](reference-catalog.md) holds the links (every one opened before it was listed) and the evidence for each topic.
