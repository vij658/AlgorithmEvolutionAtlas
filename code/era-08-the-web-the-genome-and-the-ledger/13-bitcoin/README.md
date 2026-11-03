# Bitcoin's Proof-of-Work Ledger: the program

*Era 8 · topic 13 · 2008* · Book page: [GitHub edition](../../../book/era-08-the-web-the-genome-and-the-ledger/13-bitcoin/README.md) · [interactive edition](../../../book/era-08-the-web-the-genome-and-the-ledger/13-bitcoin/bitcoin.html) · [All era 8 programs](../README.md)

## How it works

```text
A ledger of payments is kept by everyone, as a chain of blocks. Each block holds a batch of transactions (as the
root of a Merkle tree of their hashes, Era 7), the hash of the block before it, and a number called the nonce.
A block counts only if the SHA-256 hash of its header, read as a number, is below a target: in other words it
starts with enough zero bits. No one knows how to find such a nonce except by trying: with d zero bits needed,
about 2^d tries. Checking it takes one hash. That is the proof of work.
Changing an old transaction changes its block's Merkle root, so its hash, so the next block's "previous hash" no
longer matches: to rewrite history an attacker must redo the work of that block and of every block after it,
while honest computers keep extending the chain. Everyone follows the chain with the most work.
Nakamoto's Section 11 computes the chance that an attacker with a share q of the computing power, starting z
blocks behind, ever catches up: while the honest side makes z blocks the attacker makes about z q / p (a Poisson
count), and from k blocks behind a gambler with odds q / p catches up with probability (q / p)^k.
```

## What the program does

```text
1. The real genesis block of 3 January 2009: its 80-byte header, hashed twice with SHA-256, against its published
   hash, and against the target encoded in the header.
2. A toy chain: Merkle roots, and blocks mined at 4 to 16 zero bits; tries against 2^d.
3. Tampering: one transaction changed in block 3 of 10, what breaks, and the work to repair it.
4. Nakamoto's Section 11 tables, recomputed from his formula, against the numbers printed in the paper; and the
   race simulated directly.
5. A block mined with plain SHA-256 at 4 to 16 zero bits, for the book's widget to repeat.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java Bitcoin.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [History of bitcoin](https://en.wikipedia.org/wiki/History_of_bitcoin) — Wikipedia | From the domain name to the first transaction |
| Start | [Bitcoin and Cryptocurrency Technologies](https://discovery.princeton.edu/2016/11/15/bitcoin-and-cryptocurrency-technologies-a-comprehensive-introduction) — Princeton University (2016) | A textbook for the whole subject |
| Deeper | [Genesis block](https://www.utwente.nl/en/ces/sal/exams/Blockchain-and-Distributed-Ledger-Technology-test/1-Bitcoin/genesis-block-bitcoin-wiki.pdf) — Bitcoin Wiki, printed for a University of Twente course | The first block, field by field |
| Scholar | [Bitcoin: A Peer-to-Peer Electronic Cash System](https://courses.csail.mit.edu/6.857/2015/files/L07-nakamoto-bitcoin-a-peer-to-peer-electronic-cash-system.pdf) — S. Nakamoto (2008), on an MIT course page | The design and the Section 11 calculations |
| Scholar | [Bitcoin P2P e-cash paper](https://www.metzdowd.com/pipermail/cryptography/2008-October/014810.html) — S. Nakamoto, Cryptography Mailing List (31 October 2008) | The announcement |

Every link was opened before it was listed. More, with certainty labels: [Era 8 reference catalog](../../../book/era-08-the-web-the-genome-and-the-ledger/reference-catalog.md).
