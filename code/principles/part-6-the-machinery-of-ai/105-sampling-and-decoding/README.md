# 105. Choosing the next token: greedy, temperature, top-k, top-p and beam search

*Part 6 — The machinery of modern AI (entries 101–108)* · [All programs](../../README.md) · [Part 6 plan](../../../../book/principles-catalog/part-6-status-and-plan.md)

## What hurt?

The model gives probabilities, not text. Always taking the most likely token gives dull, repetitive text and can miss the most likely *sentence*. Sampling freely from the full distribution sometimes picks one of the thousands of individually unlikely tokens in the long tail, and one bad token can derail everything after it. And teams that set temperature to 0 for reproducibility are surprised when outputs still change.

## How it works

**Greedy** takes the top token. **Sampling** draws in proportion to probability (walk the cumulative sum until it passes a uniform random number). **Temperature** reshapes the distribution first (entry 101). **Top-k** keeps the k most likely tokens; **top-p** (nucleus sampling) keeps the smallest set of most likely tokens whose probabilities add up to at least p. Both renormalize and cut off the tail. **Beam search** keeps the k best partial sequences, because the best first token is not always the start of the best sequence: greedy has no exchange argument here (entry 24).

Why "temperature 0" still varies: a logit is a long floating-point sum, float addition is not associative (entry 18), and servers split sums differently depending on how many requests are batched together. Two tokens that are tied in exact arithmetic are ranked by rounding noise.

## What the program shows

- On 1,000 random distributions, top-p always keeps the *smallest* set reaching p, and top-k with k = 1 is greedy.
- A 10-token example: top-p 0.9 keeps 4 tokens at temperature 1 (0.441 + 0.267 + 0.162 = 0.870 is not enough) and 3 at temperature 0.7.
- 200,000 draws from top-p 0.9 at temperature 0.7: every kept token within 0.43 standard errors of its probability; the 7 cut tokens drawn 0 times. Same seed, same text.
- Two logits that are the same 4,096 numbers added in different orders: unequal in 1,964 of 2,000 trials with a 32-bit total, each order winning about half the time; with a 64-bit total, 0 of 2,000.
- Hand example: greedy picks a sequence with probability 0.24; beam width 2 finds one with 0.36.
- 300 random toy models (3,125 sequences each): the most likely sequence was found by greedy 128 times, beam 2 204, beam 4 268, beam 8 293; once, a wider beam did worse than a narrower one.

## Full circle

- [Entry 24, greedy algorithms](../../part-2-paradigms-and-classics/24-greedy-algorithms/README.md): greedy decoding fails for the same reason greedy coin change fails.
- [Entry 18, summing floats](../../part-1-distances-and-number-theory/18-kahan-and-neumaier-summation/README.md): the order of addition changes the answer, and here it changes the chosen word.
- [Entry 29, sampling](../../part-2-paradigms-and-classics/29-fisher-yates-and-reservoir-sampling/README.md) and [entry 42, Monte Carlo](../../part-2-paradigms-and-classics/42-monte-carlo/README.md): checking a sampler against its target distribution.

## Your turn

Do these yourself, without asking an AI to do them for you. Predict the answer on paper before you run anything.

1. Before running: with top-p 0.5 on the 10-token example, how many tokens survive?
2. Implement *min-p* sampling (keep tokens with probability ≥ min_p × the top probability) and test it the same way.
3. Add a repetition penalty to the toy model and show greedy decoding getting stuck in a loop without it.
4. Find, by search over random models, a case where beam 4 beats beam 8. What does it look like?

## Run it

```
cd code/principles/part-6-the-machinery-of-ai/105-sampling-and-decoding
java SamplingAndDecoding.java
```

JDK 17 or newer, no build step. It prints 5515 passing checks; a failed check stops the program with an `AssertionError` and a non-zero exit status. Randomized checks use a fixed seed, so the output below is exactly what you should see.

## Expected output

```
10-token example, probabilities 0.441 0.267 0.162 0.060 0.036 0.022 0.008 0.003 0.001 0.000
temperature 0.7: top token 0.546; temperature 1.5: top token 0.339; top-k 3 keeps 3; top-p 0.9 keeps 4; top-p 0.9 at temperature 0.7 keeps 3
200,000 draws from top-p 0.9 at temperature 0.7: every kept token within 0.43 standard errors of its probability; the 7 cut tokens drawn 0 times
two logits that are the same 4,096 numbers added in different orders: unequal in 1964 of 2000 trials with a 32-bit total (B came out ahead 971 times); with a 64-bit total, 0 of 2000
hand example: greedy picks [0, 2] with probability 0.24; beam width 2 finds [1, 0] with probability 0.36
300 random models, vocabulary 5, length 5: most likely sequence found by greedy 128 times; beam 2 204 times; beam 4 268 times; beam 8 293 times; a wider beam did worse than a narrower one 1 time
SamplingAndDecoding: 5515 checks passed
```

## References

*Citations only; links will be added and checked when the book's reference catalog reaches these topics.*

- A. Fan, M. Lewis and Y. Dauphin, "Hierarchical neural story generation", ACL 2018 (top-k sampling).
- A. Holtzman, J. Buys, L. Du, M. Forbes and Y. Choi, "The curious case of neural text degeneration", ICLR 2020 (nucleus / top-p sampling).
- H. He and Thinking Machines Lab, "Defeating nondeterminism in LLM inference", 2025 (batch size and floating-point order).
