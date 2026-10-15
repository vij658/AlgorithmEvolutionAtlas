# Universal Compression: the program

*Era 6 · topic 12 · 1977–1978* · Book page: [GitHub edition](../../../book/era-06-hard-problems-and-public-keys/12-lempel-ziv/README.md) · [interactive edition](../../../book/era-06-hard-problems-and-public-keys/12-lempel-ziv/lempel-ziv.html) · [All era 6 programs](../README.md)

## How it works

```text
Huffman's code (Era 5) needs the probabilities of the letters, and it codes each letter on its own. Ziv and Lempel
asked for a method that knows nothing about the source in advance and still, on long enough inputs, does as well
as a code designed for that source.
1977 (LZ77): keep the last W letters already sent. At each step find the longest string starting here that also
starts somewhere in that window; send (how far back, how long, the next letter). The receiver copies from what
it already has.
1978 (LZ78): build a dictionary of phrases as you go. At each step find the longest phrase in the dictionary that
matches what comes next; send (its number, the next letter), and add that phrase plus the letter as a new entry.
Repetition at any distance, any phrase that recurs, is coded by a reference; the longer the input, the longer
the phrases, and the fewer bits per letter.
```

## What the program does

```text
1. Both methods on a short string, every token shown, and decoded back.
2. Round trips on 2,000 random inputs and on this book's field notes.
3. Bits per letter on the field notes: Huffman's code for single letters, LZ77, LZ78.
4. A text made of one block repeated 50 times: what letter-by-letter coding cannot see.
5. A source with memory (a two-state chain that stays put 9 times in 10): LZ78's bits per symbol for 1,000 to
   10,000,000 symbols, falling towards the source's entropy rate, which it was never told.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java LempelZiv.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Remembering Jacob Ziv](https://spectrum.ieee.org/remembering-jacob-ziv) — Amanda Davis, IEEE Spectrum (2023) | The man, the sabbatical, and where the algorithms went |
| Start | [Lempel-Ziv Data Compression Algorithm, 1977](https://ethw.org/Milestones:Lempel-Ziv_Data_Compression_Algorithm,_1977) — Engineering and Technology History Wiki | The IEEE Milestone, with the 1978 and 1984 papers |
| Scholar | [A Universal Algorithm for Sequential Data Compression](https://www.icst.pku.edu.cn/mipl/docs/ziv1977.pdf) — J. Ziv and A. Lempel, *IEEE Trans. Information Theory* (1977), on a Peking University page | The sliding-window method and its proof of universality |

Every link was opened before it was listed. More, with certainty labels: [Era 6 reference catalog](../../../book/era-06-hard-problems-and-public-keys/reference-catalog.md).
