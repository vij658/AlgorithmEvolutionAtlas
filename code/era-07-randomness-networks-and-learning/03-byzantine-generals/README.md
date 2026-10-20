# The Byzantine Generals: the program

*Era 7 · topic 3 · 1980–1982* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/03-byzantine-generals/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/03-byzantine-generals/byzantine-generals.html) · [All era 7 programs](../README.md)

## How it works

```text
A commander sends an order, ATTACK or RETREAT, to n - 1 lieutenants by messenger. Some of the generals,
possibly the commander, are traitors who may say anything to anyone. The loyal lieutenants must all decide
the same thing (IC1), and if the commander is loyal they must obey him (IC2). These are faulty computers in a
fault-tolerant system: a broken sensor or processor that tells different parts of the system different things.
With spoken messages the problem can be solved exactly when more than two thirds of the generals are loyal:
n >= 3m + 1 for m traitors. The algorithm OM(m): the commander sends his order; each lieutenant then acts as
commander in OM(m - 1), passing on what he heard to the others; each lieutenant takes the majority of what he
heard directly and what the others say they heard (RETREAT on a tie). With signed messages that cannot be
forged, the algorithm SM(m) works for any number of generals: a lieutenant collects every order that arrives
with a valid chain of signatures, signs and passes on each new one, and in the end obeys if he received
exactly one order, and retreats otherwise.
```

## What the program does

```text
1. Three generals, one traitor: the two situations that a loyal lieutenant cannot tell apart.
2. OM(m) against traitors who may send any message: every traitor behaviour, or many random ones when there
   are too many to list. No violations when n >= 3m + 1; violations found when n = 3m.
3. How many messages OM(m) sends, and how many SM(m) sends.
4. SM(m) against traitors who may sign anything they like but cannot forge a loyal general's signature.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java ByzantineGenerals.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Byzantine Generals Problem](https://www.microsoft.com/en-us/research/publication/byzantine-generals-problem/) — Microsoft Research, with Leslie Lamport's note | How the story and the name were chosen |
| Deeper | [Distributed Systems lecture notes](https://www.cl.cam.ac.uk/teaching/2122/ConcDisSys/dist-sys-notes.pdf) — M. Kleppmann, University of Cambridge (2021/22) | Section 2.2 puts the generals beside the two generals problem and modern systems |
| Deeper | [Reaching Agreement in the Presence of Faults](https://www.microsoft.com/en-us/research/?p=338426) — Microsoft Research, with Lamport's note | Who proved what, and the Boeing story |
| Scholar | [The Byzantine Generals Problem](https://people.cs.umass.edu/~arun/cs677/reading/LSP.pdf) — L. Lamport, R. Shostak, M. Pease, *ACM TOPLAS* (1982), on a UMass course page | OM(m), SM(m) and the 3m + 1 bound |
| Scholar | [The Byzantine Generals Problem (abstract)](https://sri.com/?p=12386) — SRI International | The abstract as SRI publishes it |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
