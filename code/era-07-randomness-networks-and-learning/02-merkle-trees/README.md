# Merkle's Hash Trees: the program

*Era 7 · topic 2 · 1979* · Book page: [GitHub edition](../../../book/era-07-randomness-networks-and-learning/02-merkle-trees/README.md) · [interactive edition](../../../book/era-07-randomness-networks-and-learning/02-merkle-trees/merkle-trees.html) · [All era 7 programs](../README.md)

## How it works

```text
A hash function turns any data into a short fingerprint (here SHA-256, 32 bytes) that nobody can fake: finding
other data with the same fingerprint is believed to be infeasible. To fingerprint a million blocks, hash each
block, then hash the fingerprints together in pairs, then the pairs of pairs, up to a single root. Anyone who
trusts the root can check one block with only the fingerprints beside the path from that block to the root:
about log2 n of them, 20 for a million blocks, instead of all n. Two copies of the data can find where they
differ by comparing roots and walking down only into the halves that disagree. Merkle's own use was signatures:
a Lamport one-time key can sign one message; hash 2^h one-time public keys into a tree and the 32-byte root
becomes a public key good for 2^h messages.
```

## What the program does

```text
1. Builds trees the way Certificate Transparency does (RFC 6962): 0x00 before a leaf, 0x01 before a pair.
   Checks every inclusion proof for every tree of 1 to 200 leaves, and that a changed leaf, a wrong position or
   a wrong root is rejected. Counts the hashes a proof needs against the number of leaves.
2. Two copies of 2^20 blocks with a few blocks changed: finds them by walking down the two trees.
3. Shows why the 0x00 and 0x01 bytes matter: without them, a different list of leaves has the same root.
4. Lamport one-time signatures and Merkle's tree of them: 64 messages signed under one 32-byte public key.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MerkleTrees.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Merkle tree](https://en.wikipedia.org/wiki/Merkle_tree) — Wikipedia | The structure, its uses, and the second-preimage attack |
| Start | [Merkle tree](https://xlinux.nist.gov/dads/HTML/MerkleTree.html) — NIST, *Dictionary of Algorithms and Data Structures* | A one-paragraph definition with the original references |
| Deeper | [Session 3: Blockchain Basics & Cryptography](https://ocw.mit.edu/courses/15-s12-blockchain-and-money-fall-2018/resources/session-3-blockchain-basics-cryptography/) — MIT OpenCourseWare, Gary Gensler, *Blockchain and Money* (Fall 2018) | A lecture covering hash functions and Merkle trees in block headers, with video and transcript |
| Deeper | [Merkle signature scheme](https://en.wikipedia.org/wiki/Merkle_signature_scheme) — Wikipedia | One-time keys under one root, and why it matters after quantum computers |
| Scholar | [Secrecy, Authentication, and Public Key Systems](https://www.ralphmerkle.com/papers/Thesis1979.pdf) — R. Merkle, PhD thesis, Stanford (1979) | Chapter V introduces tree authentication |
| Scholar | [Method of providing digital signatures](https://patents.google.com/patent/US4309569) — R. Merkle, US patent 4,309,569 (filed 1979) | The authentication tree as patented |
| Scholar | [RFC 6962: Certificate Transparency](https://www.rfc-editor.org/rfc/rfc6962) — B. Laurie, A. Langley, E. Kasper, IETF (2013) | The exact tree hash and audit paths this topic's program follows |

Every link was opened before it was listed. More, with certainty labels: [Era 7 reference catalog](../../../book/era-07-randomness-networks-and-learning/reference-catalog.md).
