# Public-Key Cryptography: the program

*Era 6 · topic 10 · 1976–1977* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/10-public-key-cryptography/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/10-public-key-cryptography/public-key-cryptography.html) · [All era 6 programs](../README.md)

## How it works

```text
Every cipher before 1976 needed the two parties to share a secret key first, carried by hand or by a trusted
courier. Diffie and Hellman asked for functions that are easy to compute and hard to undo.
Key exchange: everyone knows a large prime p and a number g. Alice picks a secret a and publishes g^a mod p; Bob
picks b and publishes g^b mod p. Each raises the other's public number to their own secret and gets g^(ab) mod p.
An eavesdropper who sees g^a and g^b must find a from g^a (a "discrete logarithm"), for which no fast method is
known.
RSA: pick two large primes p and q, publish n = pq and a number e; keep d with e d = 1 modulo (p-1)(q-1).
Anyone can encrypt M as C = M^e mod n; only the holder of d can decrypt, M = C^d mod n. Run the other way, the
holder of d can sign, and anyone can check the signature with e. Finding d from n and e seems to require
factoring n.
Raising to a power mod n is fast: square and multiply, one bit of the exponent at a time. Large primes are found
by testing random numbers with a quick probabilistic test (the RSA paper recommends Solovay and Strassen's).
```

## What the program does

```text
1. A Diffie-Hellman exchange with a 256-bit prime.
2. Easy one way, hard the other: powers by squaring against discrete logarithms by search, for growing primes.
3. The RSA paper's small example (p = 47, q = 59) encrypting a message, and decrypting it.
4. Primality tests: Fermat's test fooled by Carmichael numbers; Solovay and Strassen's test, whose liars are
   never more than half the bases, checked exhaustively for every odd composite below 3,000.
5. A 1,024-bit RSA key made with that test; messages encrypted, decrypted, signed and verified.
6. Breaking by factoring: trial division on growing n, against the cost of encrypting.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java PublicKey.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [The Secret Story of Nonsecret Encryption](https://www.schneier.com/essays/archives/1998/04/the_secret_story_of.html) — Bruce Schneier (1998) | The public inventions and the secret ones, and how to credit them |
| Start | [Clifford Cocks](https://en.wikipedia.org/wiki/Clifford_Cocks) — Wikipedia | RSA, found first and kept secret |
| Deeper | [James H. Ellis](https://en.wikipedia.org/wiki/James_H._Ellis) — Wikipedia | The idea of non-secret encryption, inside GCHQ |
| Scholar | [New Directions in Cryptography](https://ee.stanford.edu/~hellman/publications/24.pdf) — W. Diffie and M. E. Hellman, *IEEE Trans. Information Theory* (1976) | Key exchange, public keys and signatures, proposed |
| Scholar | [A Method for Obtaining Digital Signatures and Public-Key Cryptosystems](https://people.csail.mit.edu/vinodv/COURSES/MAT302-S13/RSApaper.pdf) — R. L. Rivest, A. Shamir and L. Adleman, *Communications of the ACM* (1978) | The first practical public-key system, with its small worked example |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
