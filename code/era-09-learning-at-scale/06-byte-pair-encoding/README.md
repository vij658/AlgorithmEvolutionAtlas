# Byte-Pair Encoding for Words: the program

*Era 9 · topic 6 · 2015* · Book page: [GitHub edition](../../../book/era-09-learning-at-scale/06-byte-pair-encoding/README.md) · [interactive edition](../../../book/era-09-learning-at-scale/06-byte-pair-encoding/byte-pair-encoding.html) · [All era 9 programs](../README.md)

## How it works

```text
Gage's compressor finds the most frequent pair of adjacent bytes in a text, replaces every occurrence with a byte
that does not appear in the text, records the replacement in a table, and repeats. Sennrich, Haddow and Birch
ran the same loop on words written as letters, with an end-of-word symbol after each word (the paper writes it as a raised dot, this program as _). Every merge adds
one symbol to the vocabulary; after enough merges frequent words are single symbols and rare words are written
with a few frequent pieces. A new word is cut up by replaying the learned merges in the order they were learned,
so a word never seen in training still gets a spelling in known pieces.
Language-model tokenizers start from the 256 possible bytes of UTF-8 instead of letters, so any text at all can
be written without an "unknown" symbol.
```

## What the program does

```text
1. Gage's compressor on Wikipedia's example, aaabdaaabac, and the table that undoes it.
2. The paper's Figure 1 dictionary {low, lowest, newer, wider}: checks that the figure's four merges are a valid
   run of the algorithm (each was a most frequent pair when it was made) and shows this program's own run.
3. Learns merges from a corpus of 20,000 sentences written from 40 word stems and their endings, with some
   stem-ending combinations held out; measures symbols per word as merges grow, and whether held-out words are
   cut at the boundary between stem and ending.
4. Letters against bytes: a letter vocabulary meets characters it has never seen; a byte vocabulary never does,
   and decoding gives back every string exactly.
Every printed line starts with a tag that the book's page builder reads.
```

## Run it

```
java BytePairEncoding.java        # JDK 17 or newer, no build step
```

The output must match [`expected-output.txt`](expected-output.txt) line for line; [`../../run-all.sh`](../../run-all.sh) checks every program in the repository this way. Each output line starts with a tag (the first word), and the book's pages are built from those tagged lines, so every number in the book comes from this program.

## Watch and read

| Level | Link | Why |
|---|---|---|
| Start | [Byte Pair Encoding Tokenization](https://www.youtube.com/watch?v=HEikzVL-lZU) — Hugging Face | A short lesson from the Hugging Face course |
| Start | [Byte-pair encoding](https://en.wikipedia.org/wiki/Byte-pair_encoding) — Wikipedia | The 1994 compressor and today's tokenizers |
| Deeper | [Let's build the GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE) — Andrej Karpathy | A byte-level tokenizer written from scratch |
| Scholar | [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/pdf/1508.07909) — R. Sennrich, B. Haddow, A. Birch (2015–2016) | Merges learned on words, and Algorithm 1 |

Every link was opened before it was listed. More, with certainty labels: [Era 9 reference catalog](../../../book/era-09-learning-at-scale/reference-catalog.md).
