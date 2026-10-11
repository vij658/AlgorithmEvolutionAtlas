# Hamming's Codes: the program

*Era 4 · topic 13 · 1950* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/13-hamming-codes/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/13-hamming-codes/hamming-codes.html) · [All era 4 programs](../README.md)

## How it works

```text
Number the positions of a code word 1, 2, 3, ... and put check bits at the positions 1, 2, 4, 8, ... (the powers
of two); the other positions carry the message. The check bit at position 2^k makes the parity even over every
position whose number has bit k set. When a word arrives with one bit flipped, exactly the checks that cover that
position fail, and the failed checks, read as a binary number, spell the position: flip it back. With 7 positions,
4 carry the message and 3 are checks (the (7,4) code). Every two code words differ in at least 3 places, so a
single error leaves the word closer to the right code word than to any other. One more bit, the parity of the
whole word, raises the distance to 4: single errors are corrected and double errors detected.
```

## What the program does

```text
1. Builds the 16 code words of the (7,4) code and checks the distance between every pair.
2. Checks that every 7-bit word is within one place of exactly one code word (a "perfect" code).
3. Corrects every single error; shows that every double error is mis-corrected; then adds the overall parity bit
   and detects every double error.
4. The longer codes (15,11), (31,26), (63,57), on random words with one error.
5. A million 4-bit messages over a channel that flips 1 bit in 100: no code, Hamming's code, and sending each bit
   three times.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java HammingCodes.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Hamming code](https://en.wikipedia.org/wiki/Hamming_code) — Wikipedia | The weekend story, the (7,4) code and how the checks locate an error |
| Start | [Richard Wesley Hamming](https://mathshistory.st-andrews.ac.uk/Biographies/Hamming/) — MacTutor | Los Alamos, Bell Labs and the Turing Award |
| Scholar | [Error Detecting and Error Correcting Codes](https://zoo.cs.yale.edu/classes/cs323/doc/Hamming.pdf) — R. W. Hamming, *Bell System Technical Journal* 29(2):147–160 (April 1950), on a Yale course page | The paper: check positions, distance, and the bounds on redundancy |
| Scholar | [BSTJ 29: 2. April 1950: Error Detecting and Error Correcting Codes](https://archive.org/details/bstj29-2-147) — Internet Archive, Bell System Technical Journal collection | A scan of the journal pages |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
