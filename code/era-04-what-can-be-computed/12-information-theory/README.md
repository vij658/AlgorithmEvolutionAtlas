# Shannon's Bits: the program

*Era 4 · topic 12 · 1937–1948* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/12-information-theory/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/12-information-theory/information-theory.html) · [All era 4 programs](../README.md)

## How it works

```text
1937: a relay contact is a Boolean variable. Two contacts in series conduct when both are closed (x AND y); in
parallel, when either is (x OR y). So a network of relays is a formula of Boole's algebra, and the algebra can
simplify the network before it is built.
1948: a message source that emits symbol i with probability p_i produces, on average,
    H = - sum p_i log2 p_i   bits per symbol,
its entropy. No code can use fewer bits per symbol on average, and simple codes come within one bit: give
symbol i a codeword of about -log2 p_i bits. If the next symbol depends on the previous ones (a Markov source,
topic 3), the entropy given the past is lower, and that is the source's redundancy. Shannon showed how close
statistics alone come to English by generating text from them: random letters, then letters with English
frequencies, then pairs, triples, and words.
```

## What the program does

```text
1. Relay networks as Boolean formulas: a three-branch network and its five-contact simplification, compared on
   every input; the two-way light switch; the carry and sum of a binary adder.
2. Letter statistics of a sample of this book's own text (corpus.txt, the field notes of Eras 1 to 3), with the
   entropy per letter given 0, 1 and 2 letters of context.
3. Imitation text in the manner of Shannon's approximations, from the same statistics.
4. Shannon's code from the letter frequencies: prefix-free, and its average length between H and H + 1.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java InformationTheory.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Claude Elwood Shannon](https://mathshistory.st-andrews.ac.uk/Biographies/Shannon/) — MacTutor | Shannon's life, the thesis and the 1948 paper |
| Start | [A Symbolic Analysis of Relay and Switching Circuits](https://en.wikipedia.org/wiki/A_Symbolic_Analysis_of_Relay_and_Switching_Circuits) — Wikipedia | Boole's algebra put to work in telephone exchanges |
| Start | [A Mathematical Theory of Communication](https://en.wikipedia.org/wiki/A_Mathematical_Theory_of_Communication) — Wikipedia | The paper, the book, and its reception |
| Start | [Andrey Markov & Claude Shannon Counted Letters to Build the First Language-Generation Models](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models) — Oscar Schwartz, IEEE Spectrum (11 November 2019) | How Shannon's imitations of English grew out of Markov's counts |
| Scholar | [A Mathematical Theory of Communication](https://people.csail.mit.edu/dmoshkov/courses/codes/shannon1948.pdf) — C. E. Shannon, *Bell System Technical Journal* 27 (1948), reprint on an MIT course page | Bits, entropy, the approximations to English, and channel capacity |
| Scholar | [A symbolic analysis of relay and switching circuits](https://dspace.mit.edu/handle/1721.1/11173) — Claude Elwood Shannon, M.S. thesis, MIT Department of Electrical Engineering (catalogued 1940), DSpace@MIT | The thesis, with a scan of the original |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
