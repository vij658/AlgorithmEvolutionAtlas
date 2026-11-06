# 104. Attention, the causal mask and the KV cache

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

Older sequence models read text one token at a time and squeezed everything read so far into one fixed-size state, so the start of a long text faded away, and the reading could not be done in parallel. The fix lets every token look directly at every earlier token. That creates two new pains: the cost grows with the square of the length, and generating text one token at a time seems to redo all the earlier work at every step.

## How it works

Each token's vector is projected three ways: a **query** (what am I looking for?), a **key** (what do I contain?) and a **value** (what do I pass on?). A token's output is the average of the values of the tokens it may see, weighted by `softmax(q·k / √d)` (entry 101). Several **heads** do this in parallel on slices of the vector.

The `√d` is not decoration: the dot product of two random d-dimensional vectors has variance d, so without the division the softmax saturates and nearly all the weight lands on one token. A language model may only look backwards (the **causal mask**), and without position information attention cannot tell word order at all, which is why positions are added separately.

The causal mask has a happy consequence. When generating token t, the keys and values of tokens 0…t−1 are exactly what they were at the previous step, so they can be stored instead of recomputed: the **KV cache**. Each new token then costs work proportional to t instead of t². The price is memory, which grows with every token of every conversation being served. **Grouped-query attention** lets several query heads share one key/value head and divides that memory.

## What the program shows

- With 4, 2 and 1 KV heads, generating with the cache gives *bit-for-bit* the same outputs as recomputing everything (largest difference 0.0); the cache holds 1,536, 768 and 384 numbers.
- Causal mask: in 50 trials, changing token j left outputs 0…j−1 bit-for-bit identical (and later outputs did change).
- No mask, no positions: shuffling the input shuffles the output the same way (difference 7.8e-16), so attention alone cannot see order.
- Variance of `q·k`: 16.1, 63.5, 252.5, 1022.9 for d = 16, 64, 256, 1024. With d = 256 and 64 keys, the largest attention weight averages 0.897 without `1/√d` and 0.106 with it.
- Generating 24 tokens at width 32: 1,395,200 multiply-adds recomputing everything, 117,504 with the cache (11.9 times fewer); the counts match the formulas exactly. For 4,096 tokens at width 4,096, the same formulas give 1,912 times fewer.
- Memory: 32 layers × 32 heads × 128 dimensions at 16 bits is 512 KiB per token, 4 GiB for 8,192 tokens; with 8 shared KV heads, 1 GiB.

## Full circle

- [Entry 7, cosine similarity](../../part-1-distances-and-number-theory/07-cosine-similarity-and-jaccard/README.md): attention scores are dot products; a query looks for keys pointing its way.
- [Entry 23, dynamic programming](../../part-2-paradigms-and-classics/23-dynamic-programming/README.md): the KV cache is memoization, storing answers that will be asked for again.
- [Entry 47, cache sizing](../../part-3-performance-and-distributed-systems/47-zipf-and-cache-sizing/README.md) and [entry 45, Little's law](../../part-3-performance-and-distributed-systems/45-littles-law/README.md): memory per token × tokens in flight decides how many users one GPU can serve.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: how many bytes of KV cache does one 100,000-token conversation need with the 32-layer, 8-KV-head configuration?
2. Remove the `/ √d` and rerun the KV-cache check. Does it still pass? (It should: why?) What changes instead?
3. Add sinusoidal or rotary position encodings to the queries and keys and show that the permutation check now fails.
4. Count the multiply-adds of the *last* generated token with and without the cache, as a function of t.

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/104-attention-and-the-kv-cache
java AttentionAndKvCache.java
```

JDK 17 or newer, no build step. It prints 402 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
24 tokens, model width 32, 4 query heads: 4 KV heads: cache holds 1,536 numbers, largest difference from full recomputation 0.0e+00; 2 KV heads: cache holds 768 numbers, largest difference from full recomputation 0.0e+00; 1 KV head: cache holds 384 numbers, largest difference from full recomputation 0.0e+00;
causal mask: in 50 trials, changing token j left outputs 0..j-1 bit-for-bit identical
no mask, no positions: 20 shuffles of the input shuffle the output identically (largest difference 7.8e-16), so word order must be added separately
variance of q . k for random vectors with unit-variance entries: d=16: 16.1; d=64: 63.5; d=256: 252.5; d=1024: 1022.9;
d=256, 64 keys: the largest attention weight averages 0.897 without the 1/sqrt(d) and 0.106 with it
generating 24 tokens (width 32): 1,395,200 multiply-adds recomputing everything, 117,504 with the KV cache (11.9 times fewer)
same formulas for 4,096 tokens at width 4,096, one layer: 6.57e+14 against 3.44e+11 multiply-adds (1912 times fewer)
KV cache for 32 layers x 32 heads x 128 dims at 16 bits: 512 KiB per token, 4 GiB for 8,192 tokens; with 8 shared KV heads (grouped-query attention): 1 GiB
AttentionAndKvCache: 402 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- D. Bahdanau, K. Cho and Y. Bengio, "Neural machine translation by jointly learning to align and translate", ICLR 2015.
- A. Vaswani et al., "Attention is all you need", NeurIPS 2017.
- R. Pope et al., "Efficiently scaling Transformer inference", MLSys 2023 (the KV cache and its memory).
- J. Ainslie et al., "GQA: Training generalized multi-query Transformer models from multi-head checkpoints", EMNLP 2023.
- W. Kwon et al., "Efficient memory management for large language model serving with PagedAttention", SOSP 2023.
