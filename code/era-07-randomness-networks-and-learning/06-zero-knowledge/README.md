# Zero-Knowledge Proofs: the program

*Era 7 · topic 6 · 1985–1986* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/06-zero-knowledge/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/06-zero-knowledge/zero-knowledge.html) · [All era 7 programs](../README.md)

## How it works

```text
A prover wants to convince a verifier that something is true, say that two graphs are the same graph with the
vertices renamed, without revealing why (the renaming). Each round the prover draws a fresh random renaming of the
first graph and shows the result H. The verifier flips a coin: "show me how H comes from graph 0" or "from graph 1".
Someone who knows the secret renaming can always answer. Someone who does not can prepare for only one of the two
questions, and is caught half the time, so k rounds leave a cheater 1 chance in 2^k. And the verifier learns
nothing: a "simulator" who knows no secret can produce conversations with exactly the same distribution, by
guessing the coin in advance and starting again when wrong. Goldreich, Micali and Wigderson then gave such a proof
for every problem in NP, through graph 3-colouring: the prover locks each vertex's colour in a sealed box (here a
hash commitment), the verifier picks an edge, and only those two boxes are opened.
```

## What the program does

```text
1. Graph isomorphism: an honest prover always passes; a cheater with two different graphs is caught half the time
   per round, and passes k rounds about once in 2^k.
2. The simulator: real conversations and simulated ones, counted over all possible transcripts, are the same.
3. Graph 3-colouring with SHA-256 commitments: an honest prover always passes, and the colours the verifier sees
   are uniformly random pairs; a prover whose colouring has one bad edge is caught about once in E rounds.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ZeroKnowledge.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [How to Explain Zero-Knowledge Protocols to Your Children](https://www.fermatslibrary.com/s/how-to-explain-zero-knowledge-protocols-to-your-children) — J.-J. Quisquater, L. Guillou, T. Berson (1990), annotated by Fermat's Library | The Ali Baba cave, the story everyone uses |
| Start | [Zero-knowledge proof](https://en.wikipedia.org/wiki/Zero-knowledge_proof) — Wikipedia | Completeness, soundness and zero knowledge, with the cave and a graph example |
| Deeper | [Goldwasser, Micali receive ACM Turing Award](https://www.acm.org/media-center/2013/march/goldwasser-micali-receive-acm-turing-award-for-advances-in-cryptography) — ACM (2013) | Why the idea mattered to cryptography |
| Scholar | [The Knowledge Complexity of Interactive Proof-Systems](https://resources.mpi-inf.mpg.de/departments/d1/teaching/ss13/gitcs/GMR85.pdf) — S. Goldwasser, S. Micali, C. Rackoff (1985), on a Max Planck Institute page | Interactive proofs and knowledge complexity |
| Scholar | [Proofs that Yield Nothing But Their Validity](https://people.csail.mit.edu/silvio/Selected%20Scientific%20Papers/Zero%20Knowledge/Proofs_That_Yield_Nothing_But_Their_Validity_or_All_Languages_in_NP_Have_Zero-Knowledge_Proof_Systems.pdf) — O. Goldreich, S. Micali, A. Wigderson, *JACM* (1991) | Graph isomorphism and 3-colouring, as in this topic's program |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
