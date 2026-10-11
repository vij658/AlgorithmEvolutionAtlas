# Markov Chains: the program

*Era 4 · topic 3 · 1906–1913* · Book page: [GitHub edition](../../../book/era-04-what-can-be-computed/03-markov-chains/README.md) · [interactive edition](../../../book/era-04-what-can-be-computed/03-markov-chains/markov-chains.html) · [All era 4 programs](../README.md)

## How it works

```text
A Markov chain moves between states (here two: vowel V and consonant C). The chance of the next state depends
only on the present one, through four fixed numbers:
    after V: vowel with probability p1, consonant 1 - p1
    after C: vowel with probability p2, consonant 1 - p2
The letters are not independent (unless p1 = p2), yet the share of vowels in a long run still settles down, to
    p = p2 / (1 - p1 + p2),
and the difference from it shrinks like |p1 - p2|^n after n letters. That was Markov's answer to the claim that
the law of large numbers needs independence. Dependence changes the size of the fluctuations instead: with
d = p1 - p2, the variance of the number of vowels in n letters is close to n p (1 - p) (1 + d) / (1 - d) when n is
large, against n p (1 - p) for independent letters. In 1913 Markov tested this on 20,000 letters of Pushkin's
Eugene Onegin.
```

## What the program does

```text
1. Takes the counts reported for Markov's sample (Hayes, American Scientist, 2013) and finds which way of counting
   pairs makes them consistent: only 20,000 pairs that run one letter past the sample, which needs the first
   letter to be a consonant and letter 20,001 a vowel.
2. Recomputes the probabilities (0.432, 0.128, 0.663), and the 3,731 double vowels that independent letters
   would give.
3. The chain's long-run share of vowels, and how fast the transition table's powers approach it.
4. The dispersion factor (1 + d) / (1 - d), and a simulation of 200,000 groups of 100 letters (Markov wrote his
   letters in groups of 100) against the exact variance formula, for the chain and for independent letters.
5. The law of large numbers for the dependent chain: the running share of vowels over 10 million letters.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java MarkovChains.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [First Links in the Markov Chain](https://www.americanscientist.org/sites/americanscientist.org/files/201321152149545-2013-03Hayes.pdf) — Brian Hayes, *American Scientist* 101(2):92–97 (March–April 2013) | The quarrel with Nekrasov, the letter counts, and where chains are used now |
| Start | [Andrey Markov & Claude Shannon Counted Letters to Build the First Language-Generation Models](https://spectrum.ieee.org/andrey-markov-and-claude-shannon-built-the-first-language-generation-models) — Oscar Schwartz, IEEE Spectrum (11 November 2019) | How Markov laid out the letters, and how Shannon took the idea further |
| Start | [An idea that changed the world](https://news.harvard.edu/gazette/story/2013/01/an-idea-that-changed-the-world) — Corydon Ireland, Harvard Gazette (23 January 2013) | The centenary of the 1913 lecture |
| Start | [Andrei Andreyevich Markov](https://mathshistory.st-andrews.ac.uk/Biographies/Markov/) — MacTutor | Markov's life and his work on the law of large numbers |
| Deeper | [Markov chain](https://en.wikipedia.org/wiki/Markov_chain) — Wikipedia | Definitions, the history after Markov, and applications |
| Deeper | [A Historical Note](https://www.math.cuhk.edu.hk/course_builder/2425/math4240/HistoricalNote.pdf) — MATH4240 Stochastic Processes, Chinese University of Hong Kong | The 1906 theorem and the fixed vector (.432, .568) of the Onegin chain |
| Scholar | [The Life and Work of A. A. Markov](https://www.maths.tcd.ie/~nhb/talks/Markov.pdf) — G. P. Basharin, A. N. Langville and V. A. Naumov (PDF on a Trinity College Dublin page) | Markov's papers, his letters to Chuprov, and the Onegin probabilities |
| Scholar | [Markov reads Puškin, again](https://arxiv.org/pdf/2604.20221) — Angelo Maria Sabatini, arXiv 2604.20221 | A recount of Markov's encoding of *Onegin*, with his dispersion coefficients |
| Scholar | [Sur un cas d'épreuves liées en chaîne multiple](https://mathnet.ru/eng/im6871) — A. A. Markov, *Bulletin de l'Académie Impériale des Sciences de St.-Pétersbourg*, VI série, 5(3):171–186 (1911), in Russian; Math-Net.Ru record | One of Markov's papers on trials linked in a chain |
| Scholar | [Sur les valeurs liées qui ne forment pas une chaîne véritable](https://mathnet.ru/eng/im6867) — A. A. Markov, same *Bulletin*, 5(2):113–126 (1911), in Russian; Math-Net.Ru record | Markov on linked quantities that are not a true chain |

Every link was opened before it was listed. More, with certainty labels: [Era 4 reference catalog](../../../book/era-04-what-can-be-computed/reference-catalog.md).
