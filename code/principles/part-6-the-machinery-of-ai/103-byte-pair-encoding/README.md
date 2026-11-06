# 103. Byte-pair encoding: how text becomes tokens

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

A model needs a fixed list of symbols. Whole words make the list enormous and still miss new words, names and typos. Single characters make every text very long, and attention's cost grows with the square of the length (entry 104). Something in between was needed: a vocabulary that can write down any text at all, but writes common text in few symbols.

## How it works

Start from the 256 byte values of UTF-8, so every possible string can be written. Count every adjacent pair of symbols in a training text; the most frequent pair becomes a new symbol; replace it everywhere; repeat until the vocabulary is big enough. The ordered list of merges *is* the tokenizer. To encode new text, start from its bytes and keep applying the earliest-learned merge that appears. To decode, concatenate each token's bytes; that always gives back the original text. Text is first cut into chunks that start at a space, so merges never cross word boundaries.

Three consequences matter in practice. **The model never sees letters**: `" strawberry"` is one token here, which is why counting its letters is hard for a model. **Capitals and rare spellings cost more**: `" STRAWBERRY"` is 10 tokens. **Text unlike the training text costs more**: the same sentence in Hindi is 8.9 times as many tokens with a tokenizer trained on English, and tokens are what you pay for, wait for, and fit into the context window.

## What the program shows

- The classic example `aaabdaaabac` learns `aa`, `ab`, `aaab` in that order and becomes 5 tokens: `aaab|d|aaab|a|c`.
- On a 1,705-byte training text, every one of 210 merges shortens it: 1.41 bytes per token after 25 merges, 2.20 after 100, 3.27 after 210.
- Encoding with the merge list reproduces exactly the segmentation found during training, for every training chunk.
- Round trip `decode(encode(s)) = s` on the training text and on 2,000 random strings mixing Latin, accented, Devanagari and Chinese characters and emoji.
- `"The algorithm"` → `T|he|_algorithm`; `" strawberry"` → 1 token; `" Strawberry"` → 4; `" STRAWBERRY"` → 10; `" tokenization"` → `_token|i|z|at|i|on`.
- The same sentence: English 32 characters → 9 tokens; Hindi 30 characters → 80 bytes → 80 tokens.

## Full circle

- [Entry 16, Shannon entropy](../../part-1-distances-and-number-theory/16-shannon-entropy/README.md): BPE began as a compression scheme; frequent pairs get short codes.
- [Entry 24, greedy algorithms](../../part-2-paradigms-and-classics/24-greedy-algorithms/README.md): each merge is a greedy choice, with no exchange argument proving the final vocabulary optimal.
- [Entry 15, rolling hashes](../../part-1-distances-and-number-theory/15-horner-and-rolling-hash/README.md): another way of turning text into numbers, for a different purpose (search instead of modelling).

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: how many tokens is `" algorithms"`? Is it `_algorithm|s`? Check.
2. Train on a page of Java code instead of English. Which merges come first? How many tokens does `public static void main` cost before and after?
3. Add a Hindi paragraph to the training text and measure how the Hindi sentence's token count changes.
4. Why must encoding apply merges in the order they were learned? Find a string where applying them in another order gives a different, longer encoding.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/103-byte-pair-encoding
java BytePairEncoding.java
```

JDK 17 or newer, no build step. It prints 2380 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
"aaabdaaabac": merges learned in order aa, ab, aaab; tokens aaab|d|aaab|a|c
training text: 1,705 bytes; tokens after 0 merges: 1,705 (1.00 bytes per token); 25 merges: 1,211 (1.41 bytes per token); 50 merges: 1,008 (1.69 bytes per token); 100 merges: 775 (2.20 bytes per token); 200 merges: 541 (3.15 bytes per token); 210 merges: 521 (3.27 bytes per token);
merges learned before no pair occurred twice: 210 (vocabulary 466)
"The algorithm" -> 3 tokens: T|he|_algorithm
" strawberry"   -> 1 token: _strawberry
" Strawberry"   -> 4 tokens: _S|t|ra|wberry
" STRAWBERRY"   -> 10 tokens: _S|T|R|A|W|B|E|R|R|Y
" tokenizer"    -> 4 tokens: _token|i|z|er
" tokenization" -> 6 tokens: _token|i|z|at|i|on
English sentence: 32 characters, 32 bytes, 9 tokens; the same sentence in Hindi: 30 characters, 80 bytes, 80 tokens (8.9 times as many)
BytePairEncoding: 2380 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- P. Gage, "A new algorithm for data compression", *The C Users Journal* 12(2), 1994.
- R. Sennrich, B. Haddow and A. Birch, "Neural machine translation of rare words with subword units", ACL 2016.
- A. Radford et al., "Language models are unsupervised multitask learners" (GPT-2), OpenAI, 2019 (byte-level BPE).
