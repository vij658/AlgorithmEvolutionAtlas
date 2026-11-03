# Algorithms That Find Algorithms: the program

*Era 9 · topic 13 · 2022–2025* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/13-algorithms-that-find-algorithms/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/13-algorithms-that-find-algorithms/algorithms-that-find-algorithms.html) · [All era 9 programs](../README.md)

## How it works

```text
Multiplying an n x n matrix A by B is described by one fixed three-dimensional table of zeros and ones, the
matrix multiplication tensor T: T[(i,j), (j,k), (k,i)] = 1 for all i, j, k, and 0 elsewhere. An algorithm that
uses R multiplications is the same thing as writing T as a sum of R pieces u (x) v (x) w, each the product of
three vectors: the r-th multiplication is (sum of u_r-weighted entries of A) times (sum of v_r-weighted entries
of B), and w_r says to which entries of the product it is added. The schoolbook method is n^3 pieces; Strassen's
2 x 2 method is 7. Finding algorithms is finding short decompositions.
AlphaTensor searched for them with reinforcement learning, as a game. Kauers and Moosbauer walk instead on a
"flip graph": two pieces that share a factor, a (x) b (x) c + a (x) b' (x) c', can be rewritten as
a (x) (b + b') (x) c + a (x) b' (x) (c' - c) without changing the sum (a flip); when two pieces come to share two
factors they merge into one, and the algorithm has one multiplication fewer (a reduction).
Whatever finds an algorithm, checking it is easy: add up the pieces and compare with T.
```

## What the program does

```text
1. Builds T for 2 x 2, 3 x 3 and 4 x 4 and checks the schoolbook method, Strassen's 7, and Strassen applied
   twice to 4 x 4 (49 multiplications), all with arithmetic modulo 2.
2. Checks AlphaTensor's published 47-multiplication algorithm for 4 x 4 matrices modulo 2 (embedded below, from
   DeepMind's alphatensor repository, file algorithms/factorizations_f2.npz, key "4,4,4", CC BY 4.0) against T,
   and by multiplying random 0/1 matrices.
3. Random walks on the flip graph, starting from the schoolbook method: 2 x 2 down to 7, 3 x 3 down to 23
   (Laderman's 1976 record), and 4 x 4 for a fixed number of flips.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java AlgorithmDiscovery.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [How AI Discovered a Faster Matrix Multiplication Algorithm](https://www.youtube.com/watch?v=fDAPJ7rvcUw) — Quanta Magazine | The story of AlphaTensor and the Linz response |
| Start | [Discovering novel algorithms with AlphaTensor](https://deepmind.google/blog/discovering-novel-algorithms-with-alphatensor/) — Google DeepMind (2022) | The announcement |
| Start | [AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms](https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/) — Google DeepMind (2025) | The 2025 system |
| Deeper | [Matrix multiplication algorithm](https://en.wikipedia.org/wiki/Matrix_multiplication_algorithm) — Wikipedia | Where AlphaTensor's results sit among the records |
| Scholar | [Matej Balog - AlphaTensor: Discover faster matrix multiplication algorithms with RL - IPAM at UCLA](https://www.youtube.com/watch?v=QJT3LszR2pA) — Institute for Pure & Applied Mathematics (IPAM) | A talk by one of AlphaTensor's authors |
| Scholar | [Flip Graphs for Matrix Multiplication](https://arxiv.org/abs/2212.01175) — M. Kauers, J. Moosbauer (2022) | The random-walk method the program uses |
| Scholar | [AlphaTensor repository](https://github.com/google-deepmind/alphatensor) — Google DeepMind | The discovered algorithms, as data |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
