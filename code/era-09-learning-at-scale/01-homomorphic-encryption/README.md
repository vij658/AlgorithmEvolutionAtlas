# Fully Homomorphic Encryption: the program

*Era 9 · topic 1 · 2009–2010* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/01-homomorphic-encryption/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/01-homomorphic-encryption/homomorphic-encryption.html) · [All era 9 programs](../README.md)

## How it works

```text
The secret key is a large odd number p. To encrypt one bit m, pick a large random q and a small random r and send
    c = p*q + 2*r + m.
To decrypt, reduce c modulo p into the range (-p/2, p/2]; that leaves the "noise" 2r + m, whose last bit is m.
Adding two ciphertexts adds the noises: (2r1 + m1) + (2r2 + m2) has last bit m1 XOR m2. Multiplying them
multiplies the noises: its last bit is m1 AND m2. XOR and AND together build any circuit, so any computation can
be done on ciphertexts without the key.
The catch is the noise. Additions add noise bits slowly; each multiplication roughly doubles the number of noise
bits. Once the noise passes p/2, reduction modulo p wraps around and decryption gives garbage. The scheme is
"somewhat homomorphic": good for circuits of limited depth. Gentry's bootstrapping evaluates the decryption
circuit itself on an encrypted copy of the key, which resets the noise; that needs far larger numbers than this
program uses, so the program measures the limit instead.
Security rests on the approximate-gcd problem: given many near-multiples p*q_i + r_i of a hidden p, find p. With
no noise, one gcd would reveal p at once.
```

## What the program does

```text
1. A secret p of 512 bits; every bit pattern of XOR and AND on encrypted bits, checked.
2. Noise growth: the noise's size in bits after 1, 2, 3 ... levels of multiplication, until decryption fails.
3. A 4-bit adder (ripple carry, 7 gates per bit) run on encrypted inputs for all 256 pairs of 4-bit numbers.
4. A public key: 30 encryptions of zero; anyone can encrypt by adding a random subset of them.
5. Why the noise matters: without it, the gcd of two ciphertexts of zero is p (or a multiple); with it, the gcd
   is 1 or tiny.
6. A small example with a 4-digit key for the book's widget.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java FullyHomomorphic.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [How To Compute With Encrypted Data](https://www.youtube.com/watch?v=fLjPGhCDzKY) — TechTechPotato (Ian Cutress) | An introduction for a general audience |
| Deeper | [Introduction to FHE (Fully Homomorphic Encryption) - Pascal Paillier, FHE.org Meetup](https://www.youtube.com/watch?v=aruz58RarVA) — Zama | A talk by the inventor of the Paillier cryptosystem |
| Deeper | [Homomorphic encryption](https://en.wikipedia.org/wiki/Homomorphic_encryption) — Wikipedia | The 1978 question, the noise, bootstrapping and the generations of schemes |
| Scholar | [A Decade (or so) of fully homomorphic encryption, by Craig Gentry](https://www.youtube.com/watch?v=487AjvFW1lk) — IACR | The inventor, on the channel of the International Association for Cryptologic Research |
| Scholar | [A Fully Homomorphic Encryption Scheme](https://crypto.stanford.edu/craig/craig-thesis.pdf) — C. Gentry (2009), dissertation, Stanford | The first construction, and bootstrapping |
| Scholar | [Fully Homomorphic Encryption over the Integers](https://eprint.iacr.org/2009/616) — M. van Dijk, C. Gentry, S. Halevi, V. Vaikuntanathan (2009–2010) | The same idea with integers only; the scheme the program follows |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
